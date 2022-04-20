import cv2
import numpy as np
from sys import platform


if platform == "darwin":
    cap = cv2.VideoCapture(1)
    # OS X
elif platform == "win32":
    cap = cv2.VideoCapture(0)
    # Windows...

##cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise IOError("Cannot open webcam")


frame_count = 0
previous_frame = None

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(src=frame, ksize=(5,5), sigmaX=0)

    if previous_frame is None:
        previous_frame = frame
        continue

    diff_frame = cv2.absdiff(src1=previous_frame, src2=frame)
    previous_frame = frame

    cv2.imshow('Input', diff_frame)

    c = cv2.waitKey(1)
    if c == 27:
        break

cap.release()
cv2.destroyAllWindows()