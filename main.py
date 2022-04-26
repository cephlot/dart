import cv2
from MotionDetector import MotionDetector
from DartLocalization import DartLocalization

motion_detector = MotionDetector()

frame_before_motion, frame_after_motion = motion_detector.wait_for_motion()

cv2.imshow("Before motion", frame_before_motion)
cv2.imshow("After motion", frame_after_motion)

image_without_dart = frame_before_motion
image_with_dart = frame_after_motion

dart_x, dart_y = DartLocalization.find_dart_point(image_without_dart, image_with_dart)

cv2.circle(image_with_dart, (int(dart_x), int(dart_y)), radius=10, color=(0,255,0), thickness=2)
cv2.imshow("Point", image_with_dart)

cv2.waitKey()

cv2.destroyAllWindows()