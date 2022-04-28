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

    def wait(self):
        frames_before, frames_after = self.detector.wait_for_motion()

        if self.segmenter == None:
            self.segmenter = []

            for i, frame in enumerate(frames_before):
                self.segmenter.append(RegionSegmenter(ImageNormalizer.normalize_image(frame)))

    def get_score(self):
        frames_before, frames_after = self.detector.wait_for_motion()
        scores = Counter()
        regions = [11]

        for i, frame in enumerate(frames_before):
            evaluator = ScoreEvaluator(frame, frames_after[i], regions[i], self.segmenter[i])
            scores[i] = evaluator.evaluate()

        #value, _ = scores.most_common()
        value = scores[0]

        return value
