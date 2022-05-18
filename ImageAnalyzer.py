import cv2 as cv
import numpy as np

class ImageAnalyzer:
    """
    Class containing methods for detecting differences in images.
    """

    @staticmethod
    def analyze(befores, afters):
        """Analyzes two lists of images to see if there are differences

        :param befores: list of images before
        :type befores: list
        :param afters: list of images after
        :type afters: list
        :return: True if there is one contour, otherwise False
        :rtype: bool
        """

        for i, before in enumerate(befores):
            before = cv.cvtColor(before, cv.COLOR_BGR2GRAY)
            after = cv.cvtColor(afters[i], cv.COLOR_BGR2GRAY)

            before = cv.GaussianBlur(src=before, ksize=(5,5), sigmaX=0)
            after = cv.GaussianBlur(src=after, ksize=(5,5), sigmaX=0)

            diff_frame = cv.absdiff(src1=before, src2=after)
            thresh_frame = cv.threshold(src=diff_frame, thresh=18, maxval=255, type=cv.THRESH_BINARY)[1]
            thresh_frame = cv.erode(src=thresh_frame, kernel=np.ones((6,6)))

            contours, _  = cv.findContours(thresh_frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

            if len(contours) == 0:
                return True
        return False