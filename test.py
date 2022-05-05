from time import sleep
import cv2
from sys import platform
from datetime import datetime
from CameraSetup import cameraSetup as cs
from MotionDetector  import MotionDetector as md


cameraList = []
caps = []

bannedCam = cs.checkOS()
camera_indices = cs.getCams(bannedCam)

caps = [None] * len(camera_indices)
for i in range(len(caps)):
    caps[i] = cv2.VideoCapture(camera_indices[i])
    caps[i].set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    caps[i].set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    width = caps[i].get(cv2.CAP_PROP_FRAME_WIDTH)
    height = caps[i].get(cv2.CAP_PROP_FRAME_HEIGHT)
    if not caps[i].isOpened() or width != 1280 or height != 720:
        raise IOError("Couldn't open camera " + str(camera_indices[i]))


print(caps)
print(camera_indices)
while True:
    # Capture frame-by-frame
    for cameras in range(len(camera_indices)):
        ret, frame = caps[cameras].read()
        # Display the resulting frame
        cv2.imshow('Camera'+str(cameras), frame)
    k = cv2.waitKey(1)
    if k == ord('q') or k == 27:
        break

# When everything done, release the capture
for cap in caps:
    cap.release()

cv2.destroyAllWindows()

