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

    def start_round(self):
        '''
        Simulates one dart throw. Waits for motion and recieves score for each camera.
        Returns the predicted score with most votes from each camera.
        '''
        frames_before, frames_after = self.detector.wait_for_motion()
        scores = Counter()
        regions = [6, 11]

        for i, frame in enumerate(frames_before):
            evaluator = ScoreEvaluator(frame, frames_after[i], regions[i])
            scores[i] = evaluator.evaluate()

        value, _ = scores.most_common()

        return value
