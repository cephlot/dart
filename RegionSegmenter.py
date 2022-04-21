import cv2 as cv

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

        foreground = img[y:y+h, x:x+w]
        return foreground
        
    def multiplier_mask(self):
        raise NotImplementedError
    def divide_multiplier_mask(self):
        raise NotImplementedError
    def create_singular_multiplier_mask(self):
        raise NotImplementedError
    def create_point_mask(self):
        raise NotImplementedError