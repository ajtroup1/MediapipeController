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
skip_frames = 3  # Number of frames to skip before updating cursor
frame_count = 0  # Counter to keep track of frames

# Sensitivity factors
base_sensitivity = 3.0
adjusted_sensitivity = 1.0

# Click state
thumb_was_up = False
index_was_up = False
current_sensitivity = adjusted_sensitivity  # Default to adjusted sensitivity

pyautogui.FAILSAFE = False

# Initialize cursor position
cursor_x, cursor_y = screen_w // 2, screen_h // 2

# Main camera read loop
while True:
    success, img = cap.read()
    img = detector.find_hands(img, draw=False)
    lmList = detector.find_position(img, draw=False)
    
    if len(lmList) != 0:
        fingers = detector.fingers_up(lmList)
        thumb_up = fingers[0]  # Assume index 0 is the thumb
        index_up = fingers[1]  # Assume index 1 is the index finger

        # Check if all fingers are up and change sensitivity accordingly
        if all(fingers):
            current_sensitivity = base_sensitivity
            cv2.putText(img, "5 Fingers Up", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        else:
            current_sensitivity = adjusted_sensitivity
            cv2.putText(img, "Less than 5 Fingers", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

        # Update cursor only if the frame is not skipped
        if frame_count % (skip_frames + 1) == 0:
            # Calculate cursor position
            cursor_x = np.interp(lmList[8][1], [0, cam_w], [0, screen_w])
            cursor_y = np.interp(lmList[8][2], [0, cam_h], [0, screen_h])

            # Flip horizontal direction
            cursor_x = screen_w - cursor_x
            
            # Apply sensitivity factor
            cursor_x *= current_sensitivity
            cursor_y *= current_sensitivity
            
            # Bound cursor position within screen dimensions
            cursor_x = np.clip(cursor_x, 0, screen_w - 1)
            cursor_y = np.clip(cursor_y, 0, screen_h - 1)
            
            pyautogui.moveTo(cursor_x, cursor_y)

        # Handle clicks
        if not index_up and index_was_up:
            pyautogui.click()
            cv2.putText(img, "Left Click!", (10, 120), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            index_was_up = False  # Reset the state after left-clicking

        if not thumb_up and thumb_was_up:
            pyautogui.rightClick()
            cv2.putText(img, "Right Click!", (10, 120), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 3)
            thumb_was_up = False  # Reset the state after right-clicking

        # Update thumb and index states
        if index_up:
            index_was_up = True
        if thumb_up:
            thumb_was_up = True

    # Update frame counter and calculate FPS
    frame_count += 1
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (7, 45), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

    flipped_img = cv2.flip(img, 1)
    cv2.imshow("Video Capture", flipped_img)
    if cv2.waitKey(1) & 0xFF == 27: # Can exit with the "ESC" key
        break

cap.release()
cv2.destroyAllWindows()
