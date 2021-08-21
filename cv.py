"""
Created on Sun Aug  1 20:06:47 2021

@author: Sharjeel Masood
"""

import cv2
from utils import *
import numpy as np
import math
import matplotlib.pyplot as plt
import time
import keyboard

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

data_x = []
data_y = []
data_p = []

z = np.array([-3.43962799e-07,  2.43667009e-02,  4.40222928e+01])
p = np.poly1d(z)

def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def volume_control(positions, image, smooth_arr, next_ind):
    x1, y1 = positions[4][1], positions[4][2]
    x2, y2 = positions[8][1], positions[8][2]
    
    ax1, ay1 = positions[0][1], positions[0][2]
    ax2, ay2 = positions[5][1], positions[5][2]
    ax3, ay3 = positions[9][1], positions[9][2]
    ax4, ay4 = positions[13][1], positions[13][2]
    ax5, ay5 = positions[17][1], positions[17][2]
    
    cv2.circle(image, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
    cv2.circle(image, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
    cv2.line(image, (x1, y1), (x2, y2), (255, 0, 255), 3)
    
    length = math.hypot(x2 - x1, y2 - y1)
    area = PolyArea([ax1, ax2, ax3, ax4, ax5], [ay1, ay2, ay3, ay4, ay5])
    
    if area >= 3500:
        # Range -65 to 0
        max_length = p(area)
        vol = np.interp(length, [30, max_length], [-65, 0])
        smooth_arr[next_ind] = vol
        next_ind = next_ind + 1
        if next_ind == 6:
            next_ind = 0
        vol_level = np.mean(smooth_arr)
        
        if vol_level > 0:
            vol_level = -1*vol_level
        volume.SetMasterVolumeLevel(vol_level, None)
    
    if area >= 1300 and area < 3500:
        # Range -65 to 0
        max_length = p(area)
        vol = np.interp(length, [20, max_length], [-65, 0])
        smooth_arr[next_ind] = vol
        next_ind = next_ind + 1
        if next_ind == 6:
            next_ind = 0
        vol_level = np.mean(smooth_arr)
        
        if vol_level > 0:
            vol_level = -1*vol_level
        volume.SetMasterVolumeLevel(vol_level, None)
    
    return image, smooth_arr, next_ind

def increase_vol():
    cp = volume.GetMasterVolumeLevel()
    vol = np.interp(cp, [-65, 0], [0, 100])
    vol = vol + 2
    cp = np.interp(vol, [0, 100], [-65, 0])
    volume.SetMasterVolumeLevel(cp, None)

def decrease_vol():
    cp = volume.GetMasterVolumeLevel()
    vol = np.interp(cp, [-65, 0], [0, 100])
    vol = vol - 2
    cp = np.interp(vol, [0, 100], [-65, 0])
    volume.SetMasterVolumeLevel(cp, None)

def command_numbers(fingers, positions, image, frame, position_frame, volume_frame, space_frame, full_frame):
    
    num = np.count_nonzero(fingers)
    ones = np.squeeze(np.array(np.where(fingers == 1)))
    print(num)
    print(ones)
    try:
        if num == 1:
            #if ones[0] == 1:
            if frame < volume_frame or frame > int(volume_frame + 5):
                volume_frame = frame
                # Backward
                keyboard.send('left')
        
        if num == 2:
            if ones[0] == 0 and ones[1] == 1:
                if frame < volume_frame or frame > int(volume_frame + 5):
                    volume_frame = frame
                    decrease_vol()
            
            if ones[0] == 1 and ones[1] == 2:
                if frame < position_frame or frame > int(position_frame + 5):
                    position_frame = frame
                    # Forward
                    keyboard.send('right')
        
        if num == 3:
            if ones[0] == 0 and ones[1] == 1 and ones[2] == 2:
                if frame < volume_frame or frame > int(volume_frame + 5):
                    volume_frame = frame
                    increase_vol()
    
            # if ones[0] == 0 and ones[1] == 1 and ones[2] == 4:
            #     # print('Volume Control')
            #     image, smooth_arr, next_ind = volume_control(positions, image, smooth_arr, next_ind)
            
            if ones[0] == 1 and ones[1] == 2 and ones[2] ==3:
                if frame < full_frame or frame > int(full_frame + 15):
                    # print('Full screen')
                    full_frame = frame
                    keyboard.send("F11")
            
            if  ones[0] == 2 and ones[1] == 3 and ones[2] == 4:
                if frame < full_frame or frame > int(full_frame + 15):
                    # print('Full screen)
                    full_frame = frame
                    keyboard.send('F11')
            
    
        if num == 4:
            if ones[0] == 1 and ones[1] == 2 and ones[2] == 3 and ones[3] == 4:
                if frame < space_frame or frame > int(space_frame + 15):
                    # print('play/pause')
                    space_frame = frame
                    keyboard.send("space")
    except:
        print('None')
    
    return image, space_frame, full_frame, volume_frame, position_frame



cap = cv2.VideoCapture(0)

detector = handDetector(detectionCon = 0.8, trackCon = 0.2)
ptime = 0
frame_num = 0
space_frame_no = 0
full_frame_no = 0
volume_frame_no = 0
position_frame_no = 0

# smooth_arr = np.zeros(6)
# smooth_arr = smooth_arr + 15
# next_index = 0

while(cap.isOpened()):
    stat, image = cap.read()
    
    if stat == True:
        image = detector.findhands(image)
        
        position_list = detector.findPosition(image, draw=False)
        number_list = detector.find_numbers(position_list)
        number_list = np.array(number_list)

        image, space_frame_no, full_frame_no, volume_frame_no, position_frame_no = command_numbers(number_list, position_list, image, frame_num, 
                                                                                                    position_frame_no, volume_frame_no, space_frame_no, full_frame_no)    
        
        frame_num = frame_num + 1
        
        if frame_num >= 2000:
            frame_num = 0
        
        cv2.imshow("Image", image)
        
        ctime = time.time()
        fps = 1/(ctime-ptime)
        ptime = ctime
        # print("FPS: ", fps)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("Could not read the image")


cap.release()
cv2.destroyAllWindows()
# print('Volume: ', volume.GetMasterVolumeLevel())

# plt.xlabel("Area")
# plt.ylabel("Length")
# plt.plot(data_x, data_y, color ="red")
# plt.plot(data_x, data_p, color ="blue")
# plt.show()

# z = np.polyfit(data_x, data_y, 2)
# print("values:", z)