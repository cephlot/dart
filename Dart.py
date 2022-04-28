from ImageNormalizer import ImageNormalizer
import RegionSegmenter
import MotionDetector
from collections import Counter

from ScoreEvaluator import ScoreEvaluator

class Dart:
    '''
    Class that represents a game of Dart
    '''

    def __init__(self):
        self.detector = MotionDetector.MotionDetector()
        self.segmenter = None

<<<<<<< HEAD
    def start_round(self):
        '''
        Simulates one dart throw. Waits for motion and recieves score for each camera.
        Returns the predicted score with most votes from each camera.
        '''
=======
    def wait(self):
        frames_before, frames_after = self.detector.wait_for_motion()

        if self.segmenter == None:
            self.segmenter = []

            for i, frame in enumerate(frames_before):
                self.segmenter.append(RegionSegmenter(ImageNormalizer.normalize_image(frame)))

    def get_score(self):
>>>>>>> 18568e1a07540966a09c228fcf661b9cce6a15e2
        frames_before, frames_after = self.detector.wait_for_motion()
        scores = Counter()
        regions = [11]

        for i, frame in enumerate(frames_before):
            evaluator = ScoreEvaluator(frame, frames_after[i], regions[i], self.segmenter[i])
            scores[i] = evaluator.evaluate()

        #value, _ = scores.most_common()
        value = scores[0]

        return value
