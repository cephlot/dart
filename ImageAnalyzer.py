import cv2 as cv
from cv2 import imshow
import numpy as np

class ImageAnalyzer:
    '''
    Class containing methods for detecting differences in images.
    '''

    @staticmethod
    def analyze(befores, afters):
        '''
        Analyzes two lists of images to see if there are differences.
        '''

        for i, before in enumerate(befores):
            before = cv.cvtColor(before, cv.COLOR_BGR2GRAY)
            after = cv.cvtColor(afters[i], cv.COLOR_BGR2GRAY)

            before = cv.GaussianBlur(src=before, ksize=(9,9), sigmaX=0)
            after = cv.GaussianBlur(src=after, ksize=(9,9), sigmaX=0)

            diff_frame = cv.absdiff(src1=before, src2=after)
            thresh_frame = cv.threshold(src=diff_frame, thresh=0, maxval=255, type=cv.THRESH_BINARY)[1]
            thresh_frame = cv.erode(src=thresh_frame, kernel=np.ones((6,6)))

            contours, hierarchy = cv.findContours(thresh_frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            
            if len(contours) == 1:
                return True
            print(len(contours))
        return False