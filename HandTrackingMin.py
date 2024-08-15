# This file just contains the minimum code required for hand tracking using mediapipe and opencv
import cv2
import mediapipe as mp
import time

# Setting up the camera
# 1 is an external webcam, use 0 for built in or default cams
# CAP_DSHOW is essential for this to run on my external webcam
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Instantiate the Hands solution:
    # def __init__(self,
    #             static_image_mode=False,
    #             max_num_hands=2,
    #             model_complexity=1,
    #             min_detection_confidence=0.5,
    #             min_tracking_confidence=0.5):
mpHands = mp.solutions.hands
# I like the default params
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Frame ratetracking
pTime = 0
cTime = 0

# Main camera read loop
while True:
    success, img = cap.read()
    # Convert img to RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks: # If there are any hands detected on the screen
        for handLms in results.multi_hand_landmarks: # The default params for instantiating Hands() obj allows for 2 hands
            for id, lm in enumerate(handLms.landmark):
                # The landmarks are returned as a ratio of the h, w values with decimal places. That must be converted to RGB 'coordinates'
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(f"{id}: ({cx}, {cy})")
                if id == 0 or id == 4 or id == 8 or id == 12 or id == 16 or id == 20:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
            # Draws the points for each landmark on the hand as well as the connections between them
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # Calculate / display fps
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (7, 45), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

    cv2.imshow("Video Captute", img)
    if cv2.waitKey(1) & 0xFF == 27: # Can exit with the "ESC" key\
        break

cap.release()
cv2.destroyAllWindows()