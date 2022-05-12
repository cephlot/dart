from ImageAnalyzer import ImageAnalyzer

import MotionDetector

import cv2 as cv

from ScoreEvaluator import ScoreEvaluator

class Dart:
    """
    Class that represents a game of Dart
    """

    def __init__(self):
        self.detector = MotionDetector.MotionDetector()

    def wait(self, first_dart):
        """Wrapper for MotionDetector.wait_for_motion. Stores frames before and 
        frames after.
        """

        frames_before, frames_after = self.detector.wait_for_motion()
        self.frames_before = frames_before
        self.frames_after = frames_after

        if(first_dart):
            self.frames_before_before = frames_before

    def get_score(self):
        """Gets the score from a dart by using evaluator.


        :return: a score evaluation
        :rtype: int
        """        
        print("BEFORE")
        print(len(self.frames_before))
        evaluator = ScoreEvaluator(self.frames_before)
        return evaluator.evaluate(self.frames_before, self.frames_after)

    def wait_detect(self):
        """Waits for motion to be detected and then determines if there's a change 
        of players.
        """        

        condition = False

        while condition is False:
            frames_before, frames_after = self.detector.wait_for_motion()
            
            condition = ImageAnalyzer.analyze(self.frames_before_before, frames_after)

        self.frames_before = frames_after
