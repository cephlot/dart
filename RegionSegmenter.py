import cv2 as cv
import numpy as np

class RegionSegmenter:
    '''
    Class that segments an image of the dart board (no dart!)

    Attributes:
    ------------
    image
        the image of a dart board
    color_mask
        The extracted color mask from the image
    foreground
        The cropped dart board
    mask_scoring_area
        the mask of the entire scoring area
    mask_3x
        mask of 3x multiplier regions
    mask_2x
        mask of 2x multiplier regions
    mask_1x
        mask of the 1x multiplier region
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
        self.color_mask = None
        self.foreground = None
        self.mask_scoring_area = None
        self.mask_3x = None
        self.mask_2x = None
        self.mask_1x = None
        self.mask_points = None
        self.mask_inner_bullseye = None
        self.mask_outer_bullseye = None

        self.bbox = None

    def segment(self):   
        self.crop_board()
        self.multiplier_mask()
        self.scoring_region()
        self.get_mask_1x()
        self.get_mask_2x()
        self.get_mask_3x()
        self.get_bullseye_masks()
        
    def crop_board(self):

        # Create a greyscale of the board and use otsu to extract the foreground
        grayscale = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        ret, thresholded = cv.threshold(grayscale, 0, 255, cv.THRESH_OTSU)
        thresholded = cv.bitwise_not(thresholded)

        # Create a bounding rectangle containing only the foreground
        self.bbox = cv.boundingRect(thresholded)
        x, y, w, h = self.bbox

        # Extract the foreground using the bounding box
        foreground = self.image[y:y+h, x:x+w]
        self.foreground = foreground

    def multiplier_mask(self):
        # Make a 3-channel greyscale version of the image
        grayscale = cv.cvtColor(self.foreground, cv.COLOR_BGR2GRAY)
        grayscale = cv.cvtColor(grayscale, cv.COLOR_GRAY2RGB)

        # Extract only the colors by subtracting the greyscale
        colors = cv.subtract(self.foreground, grayscale)
        grayscale2 = cv.cvtColor(colors, cv.COLOR_BGR2GRAY)

        # Use otsu to get a black and white mask for the color region
        ret, thresholded = cv.threshold(grayscale2, 0, 255, cv.THRESH_OTSU)

        self.color_mask = thresholded

    def scoring_region(self):

        # Dilate and erode the color mask to get rid of unwanted garbage
        kernel = np.ones((6, 6), np.uint8)
        image = cv.dilate(self.color_mask, kernel)
        image = cv.erode(image, kernel) 

        # Find the largest contour and fill it to create a mask of the scoring area
        contours, hierarchy = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        area = np.zeros(image.shape, np.uint8)
        cv.fillPoly(area, pts=[cnts[0]], color=255)

        self.mask_scoring_area = area

    def get_mask_1x(self):
        image = cv.subtract(self.mask_scoring_area, self.color_mask)

        # Erode and dilate to clean the image
        kernel = np.ones((6, 6), np.uint8)
        image = cv.erode(image, kernel)
        image = cv.dilate(image, kernel)

        self.mask_1x = image

    def get_mask_2x(self):

        # Find the largest contour in the 1x score mask
        contours, hierarchy = cv.findContours(self.mask_1x, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        # Fill the contour
        image = np.zeros(self.mask_1x.shape, np.uint8)
        cv.fillPoly(image, pts =[cnts[0]], color=255)

        # subtract the filled contour from the scoring area to get the 2x ring mask
        result = cv.subtract(self.mask_scoring_area, image)

        self.mask_2x = result

    def get_mask_3x(self):

        color_mask = self.color_mask
        image = cv.subtract(color_mask, self.mask_2x)

        # Erode and dilate to get rid of unwanted garbage
        kernel = np.ones((4, 4), np.uint8)
        image = cv.erode(image, kernel)
        image = cv.dilate(image, kernel)

        kernel = np.ones((10, 10), np.uint8)
        image = cv.dilate(image, kernel)
        image = cv.erode(image, kernel)

        # Fill the largest contour 
        contours, hierarchy = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        blank = np.zeros(image.shape, np.uint8)
        cv.fillPoly(blank, pts =[cnts[0]], color=255)

        # Gets the 3x multiplier and bullseye zone
        blank = cv.subtract(blank, self.mask_1x)

        blank2 = np.zeros(image.shape, np.uint8)
        cv.fillPoly(blank2, pts =[cnts[1]], color=255)

        # Get rid of the bullseye zone
        mask_3x = cv.subtract(blank, blank2)

        self.mask_3x = mask_3x

    def get_bullseye_masks(self):
        
        # Subtract the different multipliers from the scoring region
        bullseye = cv.subtract(self.mask_scoring_area, self.mask_1x)
        bullseye = cv.subtract(bullseye, self.mask_2x)
        bullseye = cv.subtract(bullseye, self.mask_3x)

        # extracts the 2 circles from the color mask (instead of one big circle)
        bullseye = cv.bitwise_and(bullseye, self.color_mask, mask = None)

        contours, hierarchy = cv.findContours(bullseye, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        inner_bullseye = np.zeros(bullseye.shape, np.uint8)
        cv.fillPoly(inner_bullseye, pts =[cnts[1]], color=255)

        outer_bullseye = np.zeros(bullseye.shape, np.uint8)
        cv.fillPoly(outer_bullseye, pts =[cnts[0]], color=255)

        outer_bullseye = cv.subtract(outer_bullseye, inner_bullseye)

        self.mask_inner_bullseye = inner_bullseye
        self.mask_outer_bullseye = outer_bullseye

    def create_point_mask(self):
        raise NotImplementedError