from ImageAnalyzer import ImageAnalyzer

import MotionDetector

import cv2 as cv

from ScoreEvaluator import ScoreEvaluator

class Dart:
    '''
    Class that represents a game of Dart
    '''

    def __init__(self):
        self.detector = MotionDetector.MotionDetector()
        # self.reference = cv.imread('images/pic_nice.jpg', cv.IMREAD_GRAYSCALE)
        #cv.imshow("pic nice", self.reference)
        #cv.waitKey(0)

    def wait(self):
        '''
        Wrapper for MotionDetector.wait_for_motion. Stores frames before and 
        frames after.

        :param self: self object.
        '''
        frames_before, frames_after = self.detector.wait_for_motion()
        self.frames_before = frames_before
        self.frames_after = frames_after

    def get_score(self):
        '''
        Gets the score from a dart by using evaluator.

        :param self: self object.
        '''
        print("BEFORE")
        print(len(self.frames_before))
        evaluator = ScoreEvaluator(self.frames_before)
        return evaluator.evaluate(self.frames_before, self.frames_after)

    def wait_detect(self):
        '''
        Waits for motion to be detected and then determines if there's a change 
        of players.

        :param self: self object.
        '''

        condition = False

        while condition is False:
            frames_before, frames_after = self.detector.wait_for_motion()
            condition = ImageAnalyzer.analyze(self.frames_before, frames_after)

        self.frames_before = frames_after
