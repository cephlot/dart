from time import sleep
from sys import platform
from datetime import datetime
from CameraSetup import cameraSetup as cs
from MotionDetector  import MotionDetector as md
import cv2

cameraList = []
caps = []

bannedCam = cs.checkOS()
camera_indices = cs.getCams(bannedCam)
caps = [None] * len(camera_indices)

for i in range(len(caps)):
    caps[i] = cv2.VideoCapture(camera_indices[i])


cs.stabilize(camera_indices, caps)

while True:
    # Capture frame-by-frame
    for cameras in range(len(camera_indices)):
        ret, frame = caps[cameras].read()
        # Display the resulting frame
        cv2.imshow('Camera'+str(cameras), frame)
    k = cv2.waitKey(1)
    if k == ord('q') or k == 27:
        break

# for cameras in range(len(camera_indices)):
#     ret, frame = caps[cameras].read()
#         # Display the resulting frame
#     cv2.imwrite('Camera'+str(cameras)+'.png', frame)

# When everything done, release the capture
for cap in caps:
    cap.release()

cv2.destroyAllWindows()

