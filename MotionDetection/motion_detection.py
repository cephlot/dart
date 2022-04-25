from time import sleep
import cv2
from sys import platform
from datetime import datetime

class MotionDetector:
    def __init__(self):
        if platform == "linux" or platform == "linux2":
            self.cap = cv2.VideoCapture(0)
        elif platform == "darwin":
            self.cap = cv2.VideoCapture(1)
        elif platform == "win32":
            self.cap = cv2.VideoCapture(0)
        else:
            raise RuntimeError("Unknown operating system")

        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def __del__(self):
        self.cap.release()

    def wait_for_motion(self):
        frame_before_motion = None
        frame_after_motion = None
        previous_frame = None
        waiting_for_motion_end = False

        while True:
            ret, frame = self.cap.read()
            if not ret:
                raise IOError("Cannot read frame")
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            processed_frame = cv2.GaussianBlur(src=frame_gray, ksize=(5,5), sigmaX=0)

            if previous_frame is None:
                previous_frame = processed_frame
                continue

            diff_frame = cv2.absdiff(src1=previous_frame, src2=processed_frame)
            previous_frame = processed_frame
            thresh_frame = cv2.threshold(src=diff_frame, thresh=50, maxval=255, type=cv2.THRESH_BINARY)[1]

            if thresh_frame.any():
                if not waiting_for_motion_end:
                    print("Motion detected!")
                    frame_before_motion = previous_frame
                    waiting_for_motion_end = True
                waiting_start = datetime.now()
            elif waiting_for_motion_end and (datetime.now() - waiting_start).total_seconds() >= 0.5:
                # No motion for at least 1s
                frame_after_motion = processed_frame
                waiting_for_motion_end = False
                return frame_before_motion, frame_after_motion
            sleep(0.1)

motion_detector = MotionDetector()

frame_before_motion, frame_after_motion = motion_detector.wait_for_motion()

cv2.imshow("Before motion", frame_before_motion)
cv2.imshow("After motion", frame_after_motion)
cv2.waitKey()

cv2.destroyAllWindows()