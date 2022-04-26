
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
        raise NotImplementedError
        # return score