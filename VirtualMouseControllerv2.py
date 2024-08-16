import cv2
import HandTrackingModule as htm
import numpy as np
import time
from pynput.mouse import Button, Controller

# TODO
# Make clicking more precise and easy
# Right click
# Program breaks when 2 hands are on the screen

#################################################################
cam_w, cam_h = 720, 480
#################################################################

# Setting up the camera
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(3, cam_w)
cap.set(4, cam_h)

mode = 'Cursor'
detector = htm.HandDetector(detect_con=0.7)

pTime = 0
cTime = 0

# Initialize pynput mouse controller
mouse = Controller()

# Variable to track the state of the mouse click
is_clicked = False

def putText(img, mode, loc=(250, 450), color=(0, 255, 255)):
    cv2.putText(img, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, color, 3)

while True:
    success, img = cap.read()
    if not success:
        print("Issue reading video capture")
        break

    img = detector.find_hands(img, draw=False)
    lmList = detector.find_position(img, draw=False)

    if len(lmList) != 0:
        if mode == 'Cursor':
            active = 1
            putText(img, mode)
            cv2.rectangle(img, (110, 20), (620, 350), (255, 255, 255), 3)

            fingers = detector.fingers_up(lmList)

            if fingers[1:] == [0, 0, 0, 0]:  # thumb excluded
                active = 0
                mode = 'N'
            else:
                if len(lmList) != 0:
                    x1, y1 = lmList[8][1], lmList[8][2]
                    w, h = 1920, 1080  # Update with your screen resolution
                    X = int(np.interp(x1, [110, 620], [w - 1, 0]))
                    Y = int(np.interp(y1, [20, 350], [0, h - 1]))
                    cv2.circle(img, (lmList[8][1], lmList[8][2]), 7, (255, 255, 255), cv2.FILLED)
                    cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 255, 0), cv2.FILLED)  # thumb

                    if X % 2 != 0:
                        X = X - X % 2
                    if Y % 2 != 0:
                        Y = Y - Y % 2
                    
                    # Move mouse using pynput
                    mouse.position = (X, Y)

                    # If thumb is down, initiate or maintain click
                    if fingers[0] == 0:
                        cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 0, 255), cv2.FILLED)  # thumb
                        if not is_clicked:
                            mouse.press(Button.left)
                            is_clicked = True
                    # If thumb is up, release click
                    else:
                        if is_clicked:
                            mouse.release(Button.left)
                            is_clicked = False

    cTime = time.time()
    fps = 1 / ((cTime + 0.01) - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
    flippedImg = cv2.flip(img, 1)
    cv2.imshow('Video Capture', flippedImg)

    if cv2.waitKey(1) & 0xFF == 27: # Exit on ESC key
        break

cap.release()
cv2.destroyAllWindows()
