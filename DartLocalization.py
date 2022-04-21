import cv2
import numpy as np
class DartLocalization:
    def find_dart_point(image_without_dart, image_with_dart):
        # Convert to grayscale and pply gaussian blur
        image_without_dart = cv2.cvtColor(image_without_dart, cv2.COLOR_BGR2GRAY)
        image_without_dart = cv2.GaussianBlur(image_without_dart, ksize=(5,5), sigmaX=0.0)

        image_with_dart = cv2.cvtColor(image_with_dart, cv2.COLOR_BGR2GRAY)
        image_with_dart = cv2.GaussianBlur(image_with_dart, ksize=(5,5), sigmaX=0.0)

        # Find the pixels belonging to the new dart
        image_diff = cv2.absdiff(src1=image_without_dart, src2=image_with_dart)

        image_thresh = cv2.threshold(src=image_diff, thresh=10, maxval=255, type=cv2.THRESH_BINARY)[1]

        kernel = np.ones((9,9), np.uint8)

        image_dilated = cv2.dilate(image_thresh, kernel, iterations=1)

        image_eroded = cv2.erode(image_dilated, kernel, iterations=1)

        # calculate center of mass of dart pixels in binary image
        M = cv2.moments(image_eroded)
        # Get x,y coordinates of center of mass
        x_average = M["m10"] / M["m00"]
        y_average = M["m01"] / M["m00"]

        # Find pixel furthest away from center of mass (this should be the point of the dart)
        nonzero = cv2.findNonZero(image_eroded)

        # Can this be replaced with np.linalg.norm() ?
        distances = np.sqrt((nonzero[:,:,0] - x_average) ** 2 + (nonzero[:,:,1] - y_average) ** 2)
        max_index = np.argmax(distances)
        max_x = nonzero[max_index,0,0]
        max_y = nonzero[max_index,0,1]

        return max_x, max_y