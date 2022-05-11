import cv2
import numpy as np
class DartLocalization:
    @staticmethod
    def find_dart_point(image_without_dart, image_with_dart):
        """Predicts the coordinate of a dart point

        :param image_without_dart: image without dart
        :type image_without_dart: image
        :param image_with_dart: image with dart
        :type image_with_dart: image
        :return: coordinate of dart point
        :rtype: (int,int)
        """
        denoised_image_without_dart = cv2.GaussianBlur(image_without_dart, ksize=(5,5), sigmaX=0.0)
        denoised_image_with_dart = cv2.GaussianBlur(image_with_dart, ksize=(5,5), sigmaX=0.0)

        image_color_diff = cv2.absdiff(src1=denoised_image_without_dart, src2=denoised_image_with_dart)
        image_gray_diff = cv2.cvtColor(image_color_diff, cv2.COLOR_BGR2GRAY)

        image_thresh = cv2.threshold(src=image_gray_diff, thresh=15, maxval=255, type=cv2.THRESH_BINARY)[1]

        small_kernel = np.ones((5,5), np.uint8)
        big_kernel = np.ones((9,9), np.uint8)
        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.dilate(image_thresh, big_kernel, iterations=1)
        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.dilate(image_thresh, big_kernel, iterations=1)

        image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_OPEN, kernel=(5,5), iterations=1)

        dart_mask = image_thresh

        contours, hierarchy = cv2.findContours(dart_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            return -1,-1

        c = max(contours, key = cv2.contourArea)

        # Subtract everything outside contour
        contour_mask = np.zeros((dart_mask.shape[0],dart_mask.shape[1],1), np.uint8)
        contour_mask = cv2.fillPoly(contour_mask, pts=[c], color=255)
        dart_mask = cv2.subtract(dart_mask, cv2.bitwise_not(contour_mask))

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