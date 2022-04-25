from datetime import datetime
import cv2
from DartLocalization import DartLocalization

image_without_dart = cv2.imread("images/board_empty.png")

image_with_dart = cv2.imread("images/board_20.png")

start_time = datetime.now()
dart_x, dart_y = DartLocalization.find_dart_point(image_without_dart, image_with_dart)
end_time = datetime.now()

print("Calculation took " + str((end_time-start_time).total_seconds()*1000) + "ms")

cv2.circle(image_with_dart, (int(dart_x), int(dart_y)), radius=10, color=(0,255,0), thickness=2)
cv2.imshow("Point", image_with_dart)

cv2.waitKey()

cv2.destroyAllWindows()