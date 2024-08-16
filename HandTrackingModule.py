import cv2
import mediapipe as mp
import time

class HandDetector():
    def __init__(self, mode=False, max_hands=2, detect_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detect_con
        self.track_con = track_con

        self.mpHands = mp.solutions.hands
        # For some reason i had to explicitely set the names of the params, or i would get a type error
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        # Must convert image from (returned) BGR to RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img
    
    def find_position(self, img, hand_num=0, draw=True):
        # List containing all the landmarks
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[hand_num]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList
                
def main():
    # Setting up the camera
    # 1 is an external webcam, use 0 for built in or default cams
    # CAP_DSHOW is essential for this to run on my external webcam
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    # Framerate tracking
    pTime = 0
    cTime = 0

    # Instantiate the HandDetector class
    detector = HandDetector()
    # Main camera read loop
    while True:
        success, img = cap.read()

        img = detector.find_hands(img)

        lmList = detector.find_position(img)
        if len(lmList) != 0:
            print(lmList[4])

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

if __name__ == "__main__":
    main()