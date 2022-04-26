import cv2
import numpy as np
class DartLocalization:
    @staticmethod
    def find_dart_point(image_without_dart, image_with_dart):
        # denoised_image_without_dart = cv2.bilateralFilter(image_without_dart, d=5, sigmaColor=30, sigmaSpace=20)
        # denoised_image_with_dart = cv2.bilateralFilter(image_with_dart, d=5, sigmaColor=30, sigmaSpace=20)
        denoised_image_without_dart = cv2.GaussianBlur(image_without_dart, ksize=(5,5), sigmaX=0.0)
        denoised_image_with_dart = cv2.GaussianBlur(image_with_dart, ksize=(5,5), sigmaX=0.0)

        image_color_diff = cv2.absdiff(src1=denoised_image_without_dart, src2=denoised_image_with_dart)
        cv2.imshow("Frame difference", image_color_diff)
        image_gray_diff = cv2.cvtColor(image_color_diff, cv2.COLOR_BGR2GRAY)

        image_thresh = cv2.threshold(src=image_gray_diff, thresh=15, maxval=255, type=cv2.THRESH_BINARY)[1]
        cv2.imshow("Threshold", image_thresh)

        # image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_OPEN, kernel=(3,3), iterations=1)
        # cv2.imshow("Open", image_thresh)
        # image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_CLOSE, kernel=(3,3), iterations=1)
        # cv2.imshow("Close", image_thresh)

        small_kernel = np.ones((5,5), np.uint8)
        big_kernel = np.ones((9,9), np.uint8)
        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.dilate(image_thresh, big_kernel, iterations=1)
        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.dilate(image_thresh, big_kernel, iterations=1)
        cv2.imshow("Dilate erode", image_thresh)

        image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_OPEN, kernel=(5,5), iterations=1)

        dart_mask = image_thresh
        cv2.imshow("dart mask", dart_mask)

        contours, hierarchy = cv2.findContours(dart_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(contours, key = cv2.contourArea)
        x,y,w,h = cv2.boundingRect(c)

        dart_mask_contour = cv2.cvtColor(dart_mask.copy(), cv2.COLOR_GRAY2BGR)
        # draw the biggest contour (c) in green
        cv2.rectangle(dart_mask_contour,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow("Contour", dart_mask_contour)

        # Subtract everything outside contour
        contour_mask = np.zeros((dart_mask.shape[0],dart_mask.shape[1],1), np.uint8)
        contour_mask = cv2.fillPoly(contour_mask, pts =[c], color=255)
        dart_mask = cv2.subtract(dart_mask, cv2.bitwise_not(contour_mask))
        cv2.imshow("Dart mask subtract", dart_mask)

        # calculate center of mass of dart pixels in binary image
        m = cv2.moments(dart_mask)
        center_of_mass_x = m["m10"] / m["m00"]
        center_of_mass_y = m["m01"] / m["m00"]

        dart_mask_copy = dart_mask.copy()

        cv2.circle(dart_mask_copy, (int(center_of_mass_x), int(center_of_mass_y)), 10, 128, 2)
        cv2.imshow("Center of mass", dart_mask_copy)

        # Find pixel furthest away from center of mass (this should be the point of the dart)
        nonzero = cv2.findNonZero(dart_mask)
        distances = np.sqrt((nonzero[:,:,0] - center_of_mass_x) ** 2 + (nonzero[:,:,1] - center_of_mass_y) ** 2)
        max_index = np.argmax(distances)
        max_x = nonzero[max_index,0,0]
        max_y = nonzero[max_index,0,1]

        return max_x, max_y