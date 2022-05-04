from ImageNormalizer import ImageNormalizer
from RegionSegmenter import RegionSegmenter
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
        self.frames_before = frames_before
        self.frames_after = frames_after

        if self.segmenter == None:
            self.segmenter = [None] * len(frames_before)

            for i, frame in enumerate(frames_before):
                self.segmenter[i] = RegionSegmenter(ImageNormalizer.normalize_image(frame))

    def get_score(self):
        scores = []
        regions = [11]

        for i, frame in enumerate(self.frames_before):
            evaluator = ScoreEvaluator(frame, self.frames_after[i], regions[i], self.segmenter[i])
            scores.append(evaluator.evaluate())

        return Dart.vote(scores)

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
