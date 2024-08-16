import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm
import pyautogui
import numpy as np

#################################################################
cam_w, cam_h = 720, 480
#################################################################

# Setting up the camera
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(3, cam_w)
cap.set(4, cam_h)

detector = htm.HandDetector(detect_con=0.7)

# Frame rate tracking
pTime = 0
cTime = 0

screen_w, screen_h = pyautogui.size()

# Frame skipping parameters
# Performance was an issue. Specifically because of the pyautogui calls to moveTo
# TODO: figure out other performance enhancers
skip_frames = 3  # Number of frames to skip before updating cursor
frame_count = 0  # Counter to keep track of frames

# Main camera read loop
while True:
    success, img = cap.read()
    img = detector.find_hands(img, draw=False)
    lmList = detector.find_position(img, draw=False)
    
    if len(lmList) != 0:
        fingers = detector.fingers_up(lmList)
        if all(fingers):
            # Update cursor only if the frame is not skipped
            if frame_count % (skip_frames + 1) == 0:
                cv2.putText(img, "5 Fingers Up", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                
                # Flip the x-axis movement. Was mirrored by default (ew)
                cursor_x = np.interp(lmList[8][1], [0, cam_w], [screen_w, 0])
                cursor_y = np.interp(lmList[8][2], [0, cam_h], [0, screen_h])
                pyautogui.moveTo(cursor_x, cursor_y)
        else:
            cv2.putText(img, "Less than 5 Fingers", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    # Update frame counter and calculate FPS
    frame_count += 1
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (7, 45), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

    cv2.imshow("Video Capture", img)
    if cv2.waitKey(1) & 0xFF == 27: # Can exit with the "ESC" key
        break

cap.release()
cv2.destroyAllWindows()
