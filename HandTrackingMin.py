
"""""
Virtual mouse controller
"""""
import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm

#################################################################
cam_w, cam_h = 720, 480
#################################################################

# Setting up the camera
# 1 is an external webcam, use 0 for built in or default cams
# CAP_DSHOW is essential for this to run on my external webcam
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(3, cam_w)
cap.set(4, cam_h)

detector = htm.HandDetector(detect_con=0.5)

# Frame ratetracking
pTime = 0
cTime = 0


# Main camera read loop
while True:
    success, img = cap.read()

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