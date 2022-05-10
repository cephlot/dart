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
        frames_before, frames_after = self.detector.wait_for_motion()
        self.frames_before = frames_before
        self.frames_after = frames_after

    def get_score(self):
        '''
        Gets the score from a dart by using evaluator
        '''
        evaluator = ScoreEvaluator(self.frames_before)
        return evaluator.evaluate(self.frames_before, self.frames_after)

    def vote(scores):
        '''
        returns most common value or the max value if all values occur the same amount of times.
        '''
        most_freq = Dart.most_frequent(scores)
        if (scores.count(most_freq) > 1):
            return most_freq
        return max(scores)

    def most_frequent(List):
        '''
        Returns the most frequent element
        '''
        return max(set(List), key = List.count)

    def wait_detect(self):
        '''
        Waits for motion to be detected and then determines if there's a change 
        of players.
        '''

        condition = False

        while condition is False:
            frames_before, frames_after = self.detector.wait_for_motion()

            # analyse image
            condition = ImageAnalyzer.analyze(self.frames_before, frames_after)

        # Set new background
        self.frames_before = frames_after
