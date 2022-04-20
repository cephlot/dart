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

previous_frame = None

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gauss = cv2.GaussianBlur(src=frame_gray, ksize=(5,5), sigmaX=0)

    if previous_frame is None:
        previous_frame = frame_gauss
        continue

    diff_frame = cv2.absdiff(src1=previous_frame, src2=frame_gauss)
    previous_frame = frame_gauss
    thresh_frame = cv2.threshold(src=diff_frame, thresh=40, maxval=255, type=cv2.THRESH_BINARY)[1]
    contours, _ = cv2.findContours(image=thresh_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:  
        if cv2.contourArea(contour) < 50:
            # too small: skip!
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        present_frame = cv2.rectangle(img=frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=2)
    cv2.imshow('Input', present_frame)

    c = cv2.waitKey(1)
    if c == 27:
        break

cap.release()
cv2.destroyAllWindows()