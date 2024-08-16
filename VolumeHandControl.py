"""""
Virtual volume controller
"""""
import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#################################################################
cam_w, cam_h = 720, 480
#################################################################

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(3, cam_w)
cap.set(4, cam_h)

# Framerate tracking
pTime = 0
cTime = 0

# Instantiate hand tracking object
detector = htm.HandDetector(detect_con=0.7)

# Initialize volume manipulation
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

length = 0

while True:
    success, img = cap.read()

    img = detector.find_hands(img)
    lmList = detector.find_position(img, draw=False)
    if len(lmList) != 0:
        # Get thumb coords
        x1, y1 = lmList[4][1], lmList[4][2]
        # Get index finger coords
        x2, y2 = lmList[8][1], lmList[8][2]
        # Get center value for the line
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        # Draw circles for relevant fingers
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        # Draw line between fingers
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        # Add a circle to the center of the line
        cv2.circle(img, (int(cx), int(cy)), 5, (255, 0, 255), cv2.FILLED)

        # Calculate the length of the line
        length = math.hypot(x2 - x1, y2 - y1)

        # Apply exponential scaling to get a more even volume adjustment
        scaled_length = np.interp(length, [25, 200], [0, 1])  # Scale length to a 0-1 range
        vol = min_vol + (max_vol - min_vol) * (scaled_length ** 0.325)  # Cube the scaled length for exponential effect

        # Set the volume
        volume.SetMasterVolumeLevel(vol, None)

        # Minimum volume val (0%)
        if length < 25:
            cv2.circle(img, (int(cx), int(cy)), 5, (0, 0, 255), cv2.FILLED)
        # Maximum volume val (100%)
        elif length > 200:
            cv2.circle(img, (int(cx), int(cy)), 5, (0, 255, 0), cv2.FILLED)

    # Draw volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    # Calculate and display the current volume
    vol_bar = np.interp(length, [25, 200], [400, 150])
    vol_perc = np.interp(length ** 3, [25 ** 3, 200 ** 3], [0, 100])  # Adjust the percentage display to match the scaling
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f"Volume: {int(vol_perc)}%", (7, 425), cv2.FONT_HERSHEY_PLAIN, 1.25, (0, 255, 0), 2)

    # Calculate / display fps
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (7, 45), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

    cv2.imshow("Video Capture", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Can exit with the "ESC" key
        break

cap.release()
cv2.destroyAllWindows()
