from MotionDetector import MotionDetector
import cv2
motion_detector = MotionDetector()

frame_before_motion, frame_after_motion = motion_detector.wait_for_motion()

cv2.imshow("Before motion", frame_before_motion)
cv2.imshow("After motion", frame_after_motion)
cv2.waitKey()

cv2.destroyAllWindows()