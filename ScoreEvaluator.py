
from DartLocalization import DartLocalization
from RegionSegmenter import RegionSegmenter


class ScoreEvaluator:
    '''
    Class that evaluates a score based on background image of board and image 
    of board with dart

    Attributes:
    ------------
    image_B
        the image of an empty dart board
    image_I
        the image of an dart board with dart
    NOTE: work in progress these attributes are temporary
    ''' 
    def __init__(self, image_B, image_I):
        self.image_B = image_B
        self.image_I = image_I

    # Uses the RegionSegmenter and dart localizer thingy to score
    def evaluate(self):
        segmenter = RegionSegmenter(self.image_B)
        x, y = DartLocalization.find_dart_point(self.image_B, self.Image_I)
        multiplier = 0

        if segmenter.mask_inner_bullseye[y][x]:
            return 50
        elif segmenter.mask_inner_bullseye[y][x]:
            return 25
        elif segmenter.mask_3x[y][x]:
            multiplier = 3
        elif segmenter.mask_2x[y][x]:
            multiplier = 2
        elif segmenter.mask_1x[y][x]:
            multiplier = 1
        else:
            return 0

        return segmenter.mask_points[y][x]*multiplier