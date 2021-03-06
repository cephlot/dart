import cv2 as cv
import numpy as np
from PointMaskHelper import generate_point_mask

class RegionSegmenter:
    """
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
    """
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
        """Segments the board with current configuration

        :param closest_score: closest scoring region
        :type closest_score: int
        """

        self.crop_board()
        self.multiplier_mask()
        self.scoring_region()
        self.get_mask_1x()
        self.get_mask_2x()
        self.get_mask_3x()
        self.get_bullseye_masks()
        self.create_point_mask(closest_score)
        
    def crop_board(self):
        """Crops the board with current configuration
        """

        # Create a greyscale of the board and use otsu to extract the foreground
        grayscale = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        ret, thresholded = cv.threshold(grayscale, 0, 255, cv.THRESH_OTSU)

        if (thresholded is None):
            print("crop_board: The thresholded image was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.foreground = np.zeros(shape, np.uint8)
            return

        thresholded = cv.bitwise_not(thresholded)

        # Create a bounding rectangle containing only the foreground
        self.bbox = cv.boundingRect(thresholded)
        x, y, w, h = self.bbox

        # Extract the foreground using the bounding box
        foreground = self.image[y:y+h, x:x+w]
        self.foreground = foreground

    def multiplier_mask(self):
        """Creates multiplier mask with curernt configuration
        """

        if (self.foreground is None):
            print("multiplier_mask: The foreground was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.color_mask = np.zeros(shape, np.uint8)
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
        """Creates the scoring region with current configuration
        """

        if (self.color_mask is None):
            print("scoring_region: The color mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_scoring_area = np.zeros(shape, np.uint8)
            return

        # Dilate and erode the color mask to get rid of unwanted garbage
        kernel = np.ones((55, 55), np.uint8)
        image = cv.dilate(self.color_mask, kernel)
        image = cv.erode(image, kernel) 

        # Find the largest contour and fill it to create a mask of the scoring area
        contours, hierarchy = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        if (not cnts):
            print("scoring_region: no contours were found")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_scoring_area = np.zeros(shape, np.uint8)
            return


        area = np.zeros(image.shape, np.uint8)
        cv.fillPoly(area, pts=[cnts[0]], color=255)

        self.mask_scoring_area = area

    def get_mask_1x(self):
        """Create the 1x scoring mask with current configuration
        """

        if (self.mask_scoring_area is None):
            print("get_mask_1x: The scoring area mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_1x = np.zeros(shape, np.uint8)
            return

        image = cv.subtract(self.mask_scoring_area, self.color_mask)

        # Erode and dilate to clean the image
        kernel = np.ones((10, 10), np.uint8)
        image = cv.erode(image, kernel)
        image = cv.dilate(image, kernel)

        self.mask_1x = image

    def get_mask_2x(self):
        """Create the 2x scoring mask with current configuration
        """

        if (self.mask_1x is None):
            print("get_mask_2x: The 1x multiplier mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_2x = np.zeros(shape, np.uint8)
            return

        # Find the largest contour in the 1x score mask
        contours, hierarchy = cv.findContours(self.mask_1x, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv.contourArea, reverse=True)[:2]

        if (not cnts):
            print("get_mask_2x: no contours were found")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_2x = np.zeros(shape, np.uint8)
            return

        # Fill the contour
        image = np.zeros(self.mask_1x.shape, np.uint8)
        cv.fillPoly(image, pts =[cnts[0]], color=255)

        # subtract the filled contour from the scoring area to get the 2x ring mask
        result = cv.subtract(self.mask_scoring_area, image)

        self.mask_2x = result

    def get_mask_3x(self):
        """Create the 3x scoring mask with current configuration
        """

        if (self.color_mask is None):
            print("get_mask_3x: The color mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_3x = np.zeros(shape, np.uint8)
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
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_3x = np.zeros(shape, np.uint8)
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
        """Create bullseye masks with current configuration
        """
        
        if (self.mask_scoring_area is None):
            print("get_bullseye_masks: The scoring area mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_inner_bullseye = np.zeros(shape, np.uint8)
            self.mask_outer_bullseye = np.zeros(shape, np.uint8)
            return

        if (self.color_mask is None):
            print("get_bullseye_masks: The color mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_inner_bullseye = np.zeros(shape, np.uint8)
            self.mask_outer_bullseye = np.zeros(shape, np.uint8)
            return

        if (self.mask_1x is None):
            print("get_bullseye_masks: The 1x mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_inner_bullseye = np.zeros(shape, np.uint8)
            self.mask_outer_bullseye = np.zeros(shape, np.uint8)
            return

        if (self.mask_2x is None):
            print("get_bullseye_masks: The 2x mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_inner_bullseye = np.zeros(shape, np.uint8)
            self.mask_outer_bullseye = np.zeros(shape, np.uint8)
            return

        if (self.mask_3x is None):
            print("get_bullseye_masks: The 3x mask was empty")
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_inner_bullseye = np.zeros(shape, np.uint8)
            self.mask_outer_bullseye = np.zeros(shape, np.uint8)
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
            shape = (self.image.shape[0], self.image.shape[1])
            self.mask_inner_bullseye = np.zeros(shape, np.uint8)
            self.mask_outer_bullseye = np.zeros(shape, np.uint8)
            return

        inner_bullseye = np.zeros(bullseye.shape, np.uint8)
        cv.fillPoly(inner_bullseye, pts =[cnts[1]], color=255)

        outer_bullseye = np.zeros(bullseye.shape, np.uint8)
        cv.fillPoly(outer_bullseye, pts =[cnts[0]], color=255)

        outer_bullseye = cv.subtract(outer_bullseye, inner_bullseye)

        self.mask_inner_bullseye = inner_bullseye
        self.mask_outer_bullseye = outer_bullseye

    
    def create_point_mask(self, closest_score):
        """Generates the point mask for the board. Give the point of the
        region to the bottom middle of the image in order for
        point regions to be assigned correctly!

        :param closest_score: closests scoring region
        :type closest_score: int
        """

        self.mask_points = generate_point_mask(self.foreground, self.mask_scoring_area, closest_score)

    def image_stats(image):
        """Computes the mean and standard deviation of each color channel


        :param image: image to compute stats for
        :type image: image
        :return: tuple of l-, a-, b-means and  l-, a-, b-standard deviations
        :rtype: (int, int, int, int, int, int)
        """

        (l, a, b) = cv.split(image)
        (lMean, lStd) = (l.mean(), l.std())
        (aMean, aStd) = (a.mean(), a.std())
        (bMean, bStd) = (b.mean(), b.std())
        # return the color statistics
        return (lMean, lStd, aMean, aStd, bMean, bStd)

    def color_transfer(source, target):
        """Convert the image from a RGB to a LAB color space to make transfer simplier,
        Takes the source image as a "color reference" for the target, generating a modified
        image with matching colors

        This code is backup in case auto white balancing does not work.

        :param source: source image
        :type source: image
        :param target: target imge
        :type target: image
        :return: modified image
        :rtype: image
        """

        source = cv.cvtColor(source, cv.COLOR_BGR2LAB).astype("float32")
        target = cv.cvtColor(target, cv.COLOR_BGR2LAB).astype("float32")
        # compute color statistics for the source and target images
        (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = RegionSegmenter.image_stats(source)
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = RegionSegmenter.image_stats(target)
        # subtract the means from the target image
        (l, a, b) = cv.split(target)
        l -= lMeanTar
        a -= aMeanTar
        b -= bMeanTar
        # scale by the standard deviations
        l = (lStdTar / lStdSrc) * l
        a = (aStdTar / aStdSrc) * a
        b = (bStdTar / bStdSrc) * b
        # add in the source mean
        l += lMeanSrc
        a += aMeanSrc
        b += bMeanSrc
        # clip the pixel intensities to [0, 255] if they fall outside
        # this range
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)
        # merge the channels together and convert back to the RGB color
        # space, being sure to utilize the 8-bit unsigned integer data
        # type
        transfer = cv.merge([l, a, b])
        transfer = cv.cvtColor(transfer.astype("uint8"), cv.COLOR_LAB2BGR)
        
        # return the color transferred image
        return transfer