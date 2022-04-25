import cv2 as cv
import numpy as np

class RegionSegmenter:
    '''
    Class that segments an image of the dart board (no dart!)

    Attributes:
    ------------
    image
        the image of a dart board
    mask3x
        mask of 3x multiplier regions
    mask2x
        mask of 2x multiplier regions
    mask_points
        mask of point regions
    mask_outer_bullseye
        mask of point regions
    mask_inner_bullseye
        mask of point regions
    NOTE: masks can be changed, not sure if all of these are needed or correct
    '''
    def __init__(self, image):
        self.image = image
        self.foreground = None
        self.score = None
        self.mask_3x = None
        self.mask_2x = None
        self.mask_1x = None
        self.mask_points = None
        self.mask_inner_bullseye = None
        self.mask_outer_bullseye = None

        self.bbox = None

    def segment(self):   
        raise NotImplementedError
    def crop_board(self):
        grayscale = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)

        ret, thresholded = cv.threshold(grayscale, 0, 255, cv.THRESH_OTSU)
        thresholded = cv.bitwise_not(thresholded)

        self.bbox = cv.boundingRect(thresholded)
        x, y, w, h = self.bbox

        foreground = self.image[y:y+h, x:x+w]
        self.foreground = foreground

    def multiplier_mask(self):
        grayscale = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        grayscale = cv.cvtColor(grayscale, cv.COLOR_GRAY2RGB)

        colors = cv.subtract(self.image, grayscale)
        grayscale2 = cv.cvtColor(colors, cv.COLOR_BGR2GRAY)
        ret, thresholded = cv.threshold(grayscale2, 0, 255, cv.THRESH_OTSU)

        return thresholded

    def scoring_region(self):
        kernel = np.ones((6, 6), np.uint8)

        color_mask = self.multiplier_mask()

        image = cv.dilate(color_mask, kernel)
        image = cv.erode(image, kernel) 

        contours, hierarchy = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        largets_area = 0
        largest_contour = None

        for cnt in contours:
            area = cv.contourArea(cnt)
            if (area > largets_area):
                largets_area = area
                largest_contour = cnt

        cv.fillPoly(image, pts =[largest_contour], color=255)

        kernel = np.ones((50, 50), np.uint8)
        image = cv.erode(image, kernel)
        image = cv.dilate(image, kernel)

        self.score = image

    def get_mask_1x(self):
        kernel = np.ones((6, 6), np.uint8)
        image = cv.subtract(self.score, self.multiplier_mask())
        image = cv.erode(image, kernel)
        image = cv.dilate(image, kernel)

        self.mask_1x = image
        return image

    def get_mask_2x(self):
        contours, hierarchy = cv.findContours(self.mask_1x, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        largets_area = 0
        largest_contour = None

        for cnt in contours:
            area = cv.contourArea(cnt)
            if (area > largets_area):
                largets_area = area
                largest_contour = cnt

        image = np.zeros(self.mask_1x.shape, np.uint8)

        cv.fillPoly(image, pts =[largest_contour], color=255)

        result = cv.subtract(self.score, image)

        self.mask_2x = result
        return result

    def get_mask_3x(self):

        color_mask = self.multiplier_mask()
        image = cv.subtract(color_mask, self.mask_2x)

        kernel = np.ones((4, 4), np.uint8)
        image = cv.erode(image, kernel)
        image = cv.dilate(image, kernel)

        kernel = np.ones((10, 10), np.uint8)
        image = cv.dilate(image, kernel)
        image = cv.erode(image, kernel)

        contours, hierarchy = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        largets_area = 0
        largest_contour = None

        for cnt in contours:
            area = cv.contourArea(cnt)
            if (area > largets_area):
                largets_area = area
                largest_contour = cnt

        blank = np.zeros(image.shape, np.uint8)
        cv.fillPoly(blank, pts =[largest_contour], color=255)

        cv.drawContours(blank, [largest_contour], -1, 255, 1)
        blank = cv.subtract(blank, self.mask_1x)

        new_image = blank.copy()

        contours, hierarchy = cv.findContours(blank, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        blank2 = np.zeros(image.shape, np.uint8)
        cv.fillPoly(blank2, pts =[cnts[1]], color=255)

        blank = cv.subtract(blank, blank2)

        return blank

    def create_point_mask(self):
        raise NotImplementedError