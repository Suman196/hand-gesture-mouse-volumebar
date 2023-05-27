

import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER

import pyautogui
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
index_y = 0
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume.GetVolumeRange()[:2]
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    frame_height, frame_width, _ = img.shape
    lmList = []
    if results.multi_hand_landmarks:
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)
                if id == 8:
                    cv2.circle(img, center=(cx, cy), radius=15, color=(0, 255, 255))
             # take all screen of window
                # index fing pos
                    index_x = screen_width / frame_width * cx
                    index_y = screen_height / frame_height * cy
                    pyautogui.moveTo(index_x, index_y)
                if id == 4:
                    cv2.circle(img, center=(cx, cy), radius=15, color=(0, 255, 255))
            # take all screen of window
            # thumb find pos
                    thumb_x = screen_width / frame_width * cx
                    thumb_y = screen_height / frame_height * cy
                # print('outside', abs(index_y - thumb_y))
                    if abs(index_y - thumb_y) < 40:
                # print('Click')
                        pyautogui.click()
                        pyautogui.sleep(1)
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[12][1], lmList[12][2]

        # Marking Thumb and Index finger
        cv2.circle(img, (x1, y1), 15, (255, 255, 255))
        cv2.circle(img, (x2, y2), 15, (255, 255, 255))
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
        length = hypot(x2 - x1, y2 - y1)
        if length < 50:
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

        vol = np.interp(length, [15, 220], [volMin, volMax])
        volume.SetMasterVolumeLevel(vol, None)
        volBar = np.interp(length, [15, 220], [400, 150])
        volPer = np.interp(length, [15, 220], [0, 100])

        # Volume Bar
        cv2.rectangle(img, (15, 150), (85, 400), (0, 0, 0), 3)
        cv2.rectangle(img, (15, int(volBar)), (85, 400), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (10, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (0, 0, 0), 3)

    cv2.imshow('handDetector', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()