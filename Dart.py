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

    def wait(self):
        frames_before, frames_after = self.detector.wait_for_motion()
        
        for i, frame in enumerate(frames_before):
            self.segmenter[i] = RegionSegmenter(frame)

    def get_score(self):
        frames_before, frames_after = self.detector.wait_for_motion()
        scores = Counter()
        regions = [6, 11]

        for i, frame in enumerate(frames_before):
            evaluator = ScoreEvaluator(frame, frames_after[i], regions[i], segmenter[i])
            scores[i] = evaluator.evaluate()

        value, _ = scores.most_common()

        return value
