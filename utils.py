"""
Created on Sun Mar 21 15:49:44 2021

@author: Sharjeel Masood
"""

import cv2
import mediapipe as mp

class handDetector():
    def __init__(self, mode = False, maxHands = 2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
    
    def findhands(self, image, draw = True):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)
                    
        if self.results.multi_hand_landmarks:
            for handlms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(image, handlms, self.mpHands.HAND_CONNECTIONS)
        
        return image

    def findPosition(self, image, handNo=0, draw=True):
        
        lm_list = []
        
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            
            for idd, lm in enumerate(myHand.landmark):
                
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                
                lm_list.append([idd, cx, cy])
                if draw:
                    cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    
        return lm_list
    
    def find_numbers(self, handlist):
        
        tip_ids = [4, 8, 12, 16, 20]
        fingers = []
        
        if len(handlist) != 0:
            
            # Thunb
            if handlist[tip_ids[4]][1] > handlist[tip_ids[1]][1]:
            
                if handlist[tip_ids[0]][1] < handlist[tip_ids[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            else:
                if handlist[tip_ids[0]][1] > handlist[tip_ids[0] - 3][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # Other 4 fingers
            for idd in range(1,5):
                
                if handlist[tip_ids[idd]][2] < handlist[tip_ids[idd] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

        return fingers

    
