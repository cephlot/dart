from datetime import datetime
import cv2
import numpy as np
class DartLocalization:
    def find_dart_point(image_without_dart, image_with_dart):
        image_without_dart = cv2.cvtColor(image_without_dart, cv2.COLOR_BGR2GRAY)
        image_without_dart = cv2.GaussianBlur(image_without_dart, ksize=(5,5), sigmaX=0.0)

        image_with_dart = cv2.cvtColor(image_with_dart, cv2.COLOR_BGR2GRAY)
        image_with_dart = cv2.GaussianBlur(image_with_dart, ksize=(5,5), sigmaX=0.0)

        image_diff = cv2.absdiff(src1=image_without_dart, src2=image_with_dart)

        image_thresh = cv2.threshold(src=image_diff, thresh=10, maxval=255, type=cv2.THRESH_BINARY)[1]

        kernel = np.ones((9,9), np.uint8)

        image_dilated = cv2.dilate(image_thresh, kernel, iterations=1)

        image_eroded = cv2.erode(image_dilated, kernel, iterations=1)

        # Process manually
        start_time = datetime.now()

        rows,cols = image_eroded.shape
        x_sum = 0
        y_sum = 0
        n_white = 0
        for y in range(rows):
            for x in range(cols):
                if image_eroded[y,x] != 0:
                    n_white += 1
                    x_sum += x
                    y_sum += y

        x_average = x_sum / n_white
        y_average = y_sum / n_white

        max_distance = 0
        max_x = None
        max_y = None
        for y in range(rows):
            for x in range(cols):
                if image_eroded[y,x] != 0:
                    x_diff = np.abs(x_average-x)
                    y_diff = np.abs(y_average-y)
                    distance = np.linalg.norm([x_diff, y_diff])
                    if distance > max_distance:
                        max_x = x
                        max_y = y
                        max_distance = distance

        end_time = datetime.now()
        print("Processing manually took " + str((end_time-start_time).total_seconds()*1000) + "ms")

        # Process with OpenCV
        start_time = datetime.now()

        # calculate center of mass of white pixels in binary image
        # calculate x,y coordinate of center
        M = cv2.moments(image_eroded)
        x_average = M["m10"] / M["m00"]
        y_average = M["m01"] / M["m00"]

        # Find pixel furthest away from center of mass
        nonzero = cv2.findNonZero(image_eroded)
        distances = np.sqrt((nonzero[:,:,0] - x_average) ** 2 + (nonzero[:,:,1] - y_average) ** 2) # TODO: np.linalg.norm() ???
        max_index = np.argmax(distances)
        max_x = nonzero[max_index,0,0]
        max_y = nonzero[max_index,0,1]

        end_time = datetime.now()
        print("Processing with OpenCV took " + str((end_time-start_time).total_seconds()*1000) + "ms")

        return max_x, max_y