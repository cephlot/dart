import cv2
import numpy as np
from ImageNormalizer import ImageNormalizer

class DartLocalization:

    def img2gray(img):
        """_summary_

        :param img: _description_
        :type img: _type_
        :return: _description_
        :rtype: _type_
        """        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img_gray
    
    def getDiff(clean_plate, new_img):
        """_summary_

        :param clean_plate: _description_
        :type clean_plate: _type_
        :param new_img: _description_
        :type new_img: _type_
        :return: _description_
        :rtype: _type_
        """        
        diff = cv2.absdiff(clean_plate, new_img)
        return diff

    def thresholding(clean_plate, new_img):
        """_summary_

        :param clean_plate: _description_
        :type clean_plate: _type_
        :param new_img: _description_
        :type new_img: _type_
        :return: _description_
        :rtype: _type_
        """        
        diff_img = DartLocalization.getDiff(new_img, clean_plate)
        diff_img = DartLocalization.img2gray(diff_img)

        img_thresh = DartLocalization.thresholding_from_diff(diff=diff_img)
        
        return diff_img, img_thresh
    
    def thresholding_from_diff(diff):
        """_summary_

        :param diff: _description_
        :type diff: _type_
        :return: _description_
        :rtype: _type_
        """        
        img_blur = cv2.GaussianBlur(diff, (3,3), 0)
        img_blur = cv2.bilateralFilter(img_blur, 5, 20, 20)

        _, img_threshold = cv2.threshold(img_blur, 15, 255, cv2.THRESH_BINARY)
        return img_threshold

    def erode_dilate(image_thresh):
        """_summary_

        :param image_thresh: _description_
        :type image_thresh: _type_
        :return: _description_
        :rtype: _type_
        """        
        small_kernel = np.ones((5,5), np.int8)
        smaller_kernel = np.ones((3,3), np.int8)
        big_kernel = np.ones((9,9), np.int8)

        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.dilate(image_thresh, big_kernel, iterations=1)
        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=3)
        image_thresh = cv2.dilate(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_CLOSE, kernel=(3,3), iterations=2)
        image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_OPEN, kernel=(3,3), iterations=2)
        return image_thresh

    def getContour(img, diff_img, boarder_limit):
        """_summary_

        :param img: _description_
        :type img: _type_
        :param diff_img: _description_
        :type diff_img: _type_
        :param boarder_limit: _description_
        :type boarder_limit: _type_
        :raises RuntimeError: _description_
        :return: _description_
        :rtype: _type_
        """        
        threshold = img
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

        threshold = np.zeros(threshold.shape, np.uint8)
        cv2.fillPoly(threshold, pts =[cnts[0]], color=255)

        diff_img = cv2.subtract(threshold, diff_img)

        cv2.imshow("threshold", threshold)
        cv2.imshow("diff", diff_img)

        contours, hierarchy = cv2.findContours(diff_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            raise RuntimeError("No contours")
        c = max(contours, key = cv2.contourArea)

        # Subtract everything outside contour
        contour_mask = np.zeros((diff_img.shape[0],diff_img.shape[1],1), np.uint8)
        contour_mask = cv2.fillPoly(contour_mask, pts=[c], color=255)
        dart_mask = cv2.subtract(threshold, cv2.bitwise_not(contour_mask))
        cv2.imshow("Dart mask subtract", dart_mask)

        center_of_mass_x, center_of_mass_y = DartLocalization.calculateCenterOfPixelMass(dart_mask=dart_mask)
        max_x, max_y, op_x, op_y = DartLocalization.getPointPosition(dart_mask=dart_mask, center_of_mass_x=center_of_mass_x, center_of_mass_y=center_of_mass_y)
        return DartLocalization.dartPointCorrection(dart_mask=dart_mask, max_x=max_x, max_y=max_y, op_x=op_x, op_y=op_y, boarder_limit=boarder_limit)
    
    def calculateCenterOfPixelMass(dart_mask):
        """_summary_

        :param dart_mask: _description_
        :type dart_mask: _type_
        :return: _description_
        :rtype: _type_
        """        
        # calculate center of mass of dart pixels in binary image
        m = cv2.moments(dart_mask)
        center_of_mass_x = m["m10"] / m["m00"]
        center_of_mass_y = m["m01"] / m["m00"]

        return center_of_mass_x, center_of_mass_y

    def getPointPosition(dart_mask ,center_of_mass_x, center_of_mass_y):
        """_summary_

        :param dart_mask: _description_
        :type dart_mask: _type_
        :param center_of_mass_x: _description_
        :type center_of_mass_x: _type_
        :param center_of_mass_y: _description_
        :type center_of_mass_y: _type_
        :return: _description_
        :rtype: _type_
        """        
        # Find pixel furthest away from center of mass (this should be the point of the dart)
        nonzero = cv2.findNonZero(dart_mask)
        distances = np.sqrt((nonzero[:,:,0] - center_of_mass_x) ** 2 + (nonzero[:,:,1] - center_of_mass_y) ** 2)
        max_index = np.argmax(distances)
        
        max_x = nonzero[max_index,0,0]
        max_y = nonzero[max_index,0,1]

        distance_far_away = np.sqrt((nonzero[:,:,0] - max_x) ** 2 + (nonzero[:,:,1] - max_y) ** 2)
        max_index_far_away = np.argmax(distance_far_away)

        op_x = nonzero[max_index_far_away,0,0]
        op_y = nonzero[max_index_far_away,0,1]

        return max_x, max_y, op_x, op_y

    def dartPointCorrection(dart_mask, max_x, max_y, op_x, op_y, boarder_limit):
        """_summary_

        :param dart_mask: _description_
        :type dart_mask: _type_
        :param max_x: _description_
        :type max_x: _type_
        :param max_y: _description_
        :type max_y: _type_
        :param op_x: _description_
        :type op_x: _type_
        :param op_y: _description_
        :type op_y: _type_
        :param boarder_limit: _description_
        :type boarder_limit: _type_
        :return: _description_
        :rtype: _type_
        """        

        if max_y > dart_mask.shape[0] - boarder_limit or max_y < boarder_limit or max_x > dart_mask.shape[1] - boarder_limit or max_x < boarder_limit:
            max_y = op_y
            max_x = op_x
        
        return max_x, max_y

    def printDebug(dart_mask, max_x, max_y, op_x, op_y, board_limiter):
        print("image size:", dart_mask.shape[0], dart_mask.shape[1])
        print("estimated point:",max_x, max_y)
        print("opposite point:",op_x, op_y)
        print("boarder limit", board_limiter)

    @staticmethod
    def find_dart_point(image_without_dart, image_with_dart):
        """_summary_

        :param image_without_dart: _description_
        :type image_without_dart: _type_
        :param image_with_dart: _description_
        :type image_with_dart: _type_
        :return: _description_
        :rtype: _type_
        """        

        image_with_dart = ImageNormalizer.normalize_image(ImageNormalizer.clahe_EQ(image_with_dart))
        image_without_dart = ImageNormalizer.normalize_image(ImageNormalizer.clahe_EQ(image_without_dart))

        diff_img, threshold = DartLocalization.thresholding(image_without_dart, image_with_dart)
        threshold = DartLocalization.erode_dilate(threshold)

        return DartLocalization.getContour(threshold, diff_img, 5)