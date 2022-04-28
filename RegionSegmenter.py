import cv2 as cv
import numpy as np
from PointMaskHelper import generate_point_mask

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

    def segment(self, closest_score):   
        '''
        OBS: set closest_score to score region nearest camera
        '''
        self.crop_board()
        self.multiplier_mask()
        self.scoring_region()
        self.get_mask_1x()
        self.get_mask_2x()
        self.get_mask_3x()
        self.get_bullseye_masks()
        self.create_point_mask(closest_score)
        
    def crop_board(self):

        # Create a greyscale of the board and use otsu to extract the foreground
        grayscale = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        ret, thresholded = cv.threshold(grayscale, 0, 255, cv.THRESH_OTSU)

        if (thresholded is None):
            print("crop_board: The thresholded image was empty")
            self.foreground = np.zeros(self.image, np.uint8)
            return

        thresholded = cv.bitwise_not(thresholded)

        # Create a bounding rectangle containing only the foreground
        self.bbox = cv.boundingRect(thresholded)
        x, y, w, h = self.bbox

        # Extract the foreground using the bounding box
        foreground = self.image[y:y+h, x:x+w]
        self.foreground = foreground

    def multiplier_mask(self):

        if (self.foreground is None):
            print("multiplier_mask: The foreground was empty")
            self.color_mask = np.zeros(self.image, np.uint8)
            return

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

        if (self.color_mask is None):
            print("scoring_region: The color mask was empty")
            self.mask_scoring_area = np.zeros(self.image, np.uint8)
            return

        # Dilate and erode the color mask to get rid of unwanted garbage
        kernel = np.ones((15, 15), np.uint8)
        image = cv.dilate(self.color_mask, kernel)
        image = cv.erode(image, kernel) 

        # Find the largest contour and fill it to create a mask of the scoring area
        contours, hierarchy = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        if (not cnts):
            print("scoring_region: no contours were found")
            self.mask_scoring_area = np.zeros(self.image, np.uint8)
            return


        area = np.zeros(image.shape, np.uint8)
        cv.fillPoly(area, pts=[cnts[0]], color=255)

        self.mask_scoring_area = area

    def get_mask_1x(self):

        if (self.mask_scoring_area is None):
            print("get_mask_1x: The scoring area mask was empty")
            self.mask_1x = np.zeros(self.image, np.uint8)
            return

        image = cv.subtract(self.mask_scoring_area, self.color_mask)

        # Erode and dilate to clean the image
        kernel = np.ones((10, 10), np.uint8)
        image = cv.erode(image, kernel)
        image = cv.dilate(image, kernel)

        self.mask_1x = image

    def get_mask_2x(self):

        if (self.mask_1x is None):
            print("get_mask_2x: The 1x multiplier mask was empty")
            self.mask_2x = np.zeros(self.image, np.uint8)
            return

        # Find the largest contour in the 1x score mask
        contours, hierarchy = cv.findContours(self.mask_1x, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        if (not cnts):
            print("get_mask_2x: no contours were found")
            self.mask_2x = np.zeros(self.image, np.uint8)
            return

        # Fill the contour
        image = np.zeros(self.mask_1x.shape, np.uint8)
        cv.fillPoly(image, pts =[cnts[0]], color=255)

        # subtract the filled contour from the scoring area to get the 2x ring mask
        result = cv.subtract(self.mask_scoring_area, image)

        self.mask_2x = result

    def get_mask_3x(self):

        if (self.color_mask is None):
            print("get_mask_3x: The color mask was empty")
            self.mask_3x = np.zeros(self.image, np.uint8)
            return

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

        if (not cnts):
            print("get_mask_3x: no contours were found")
            self.mask_3x = np.zeros(self.image, np.uint8)
            return

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
        
        if (self.mask_scoring_area is None):
            print("get_bullseye_masks: The scoring area mask was empty")
            self.mask_inner_bullseye = np.zeros(self.image, np.uint8)
            self.mask_outer_bullseye = np.zeros(self.image, np.uint8)
            return

        if (self.color_mask is None):
            print("get_bullseye_masks: The color mask was empty")
            self.mask_inner_bullseye = np.zeros(self.image, np.uint8)
            self.mask_outer_bullseye = np.zeros(self.image, np.uint8)
            return

        if (self.mask_1x is None):
            print("get_bullseye_masks: The 1x mask was empty")
            self.mask_inner_bullseye = np.zeros(self.image, np.uint8)
            self.mask_outer_bullseye = np.zeros(self.image, np.uint8)
            return

        if (self.mask_2x is None):
            print("get_bullseye_masks: The 2x mask was empty")
            self.mask_inner_bullseye = np.zeros(self.image, np.uint8)
            self.mask_outer_bullseye = np.zeros(self.image, np.uint8)
            return

        if (self.mask_3x is None):
            print("get_bullseye_masks: The 3x mask was empty")
            self.mask_inner_bullseye = np.zeros(self.image, np.uint8)
            self.mask_outer_bullseye = np.zeros(self.image, np.uint8)
            return

        # Subtract the different multipliers from the scoring region
        bullseye = cv.subtract(self.mask_scoring_area, self.mask_1x)
        bullseye = cv.subtract(bullseye, self.mask_2x)
        bullseye = cv.subtract(bullseye, self.mask_3x)

        # extracts the 2 circles from the color mask (instead of one big circle)
        bullseye = cv.bitwise_and(bullseye, self.color_mask, mask = None)

        contours, hierarchy = cv.findContours(bullseye, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        if (not cnts):
            print("get_bullseye_masks: no contours were found")
            self.mask_inner_bullseye = np.zeros(self.image, np.uint8)
            self.mask_outer_bullseye = np.zeros(self.image, np.uint8)
            return

        inner_bullseye = np.zeros(bullseye.shape, np.uint8)
        cv.fillPoly(inner_bullseye, pts =[cnts[1]], color=255)

        outer_bullseye = np.zeros(bullseye.shape, np.uint8)
        cv.fillPoly(outer_bullseye, pts =[cnts[0]], color=255)

        outer_bullseye = cv.subtract(outer_bullseye, inner_bullseye)

        self.mask_inner_bullseye = inner_bullseye
        self.mask_outer_bullseye = outer_bullseye

    
    def create_point_mask(self, closest_score):
        '''
        Generates the point mask for the board. Give the point of the
        region to the bottom middle of the image in order for
        point regions to be assigned correctly!
        '''
        self.mask_points = generate_point_mask(self.foreground, self.mask_scoring_area, closest_score)