import cv2
import numpy as np
class DartLocalization:
    @staticmethod
    def find_dart_point(image_without_dart, image_with_dart):
        denoised_image_without_dart = cv2.bilateralFilter(image_without_dart, d=5, sigmaColor=30, sigmaSpace=20)
        denoised_image_with_dart = cv2.bilateralFilter(image_with_dart, d=5, sigmaColor=30, sigmaSpace=20)

        image_color_diff = cv2.absdiff(src1=denoised_image_without_dart, src2=denoised_image_with_dart)
        image_gray_diff = cv2.cvtColor(image_color_diff, cv2.COLOR_BGR2GRAY)

        image_thresh = cv2.threshold(src=image_gray_diff, thresh=5, maxval=255, type=cv2.THRESH_BINARY)[1]

        kernel = np.ones((5,5), np.uint8)
        image_dilated = cv2.dilate(image_thresh, kernel, iterations=1)
        image_eroded = cv2.erode(image_dilated, kernel, iterations=1)

        dart_mask = image_eroded

        # calculate center of mass of dart pixels in binary image
        m = cv2.moments(dart_mask)
        center_of_mass_x = m["m10"] / m["m00"]
        center_of_mass_y = m["m01"] / m["m00"]

        # Find pixel furthest away from center of mass (this should be the point of the dart)
        nonzero = cv2.findNonZero(dart_mask)
        distances = np.sqrt((nonzero[:,:,0] - center_of_mass_x) ** 2 + (nonzero[:,:,1] - center_of_mass_y) ** 2)
        max_index = np.argmax(distances)
        max_x = nonzero[max_index,0,0]
        max_y = nonzero[max_index,0,1]

        return max_x, max_y