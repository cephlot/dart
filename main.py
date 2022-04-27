import cv2
from numpy import disp
from MotionDetector import MotionDetector
from DartLocalization import DartLocalization

motion_detector = MotionDetector()

frames_before_motion, frames_after_motion = motion_detector.wait_for_motion()

for i in range(len(frames_before_motion)):
    # cv2.imshow("Before motion " + str(i), frames_before_motion[i])
    # cv2.imshow("After motion " + str(i), frames_after_motion[i])
    dart_x, dart_y = DartLocalization.find_dart_point(frames_before_motion[i], frames_after_motion[i])
    image_with_dart = frames_after_motion[i].copy()
    cv2.circle(image_with_dart, (int(dart_x), int(dart_y)), radius=10, color=(0,255,0), thickness=2)
    cv2.imshow("Point " + str(i), image_with_dart)

cv2.waitKey()

cv2.destroyAllWindows()