from Helpers.PointMaskHelper import generate_mask


class RegionSegmenter:
    '''
    Class that segments an image of the dart board (no dart!)

    Attributes:
    ------------
    image
        the image of a dart board
    mask3x
        mask of 3x multiplier regions
    mask2x
        mask of 2x multiplier regions
    mask_points
        mask of point regions
    mask_outer_bullseye
        mask of point regions
    mask_inner_bullseye
        mask of point regions
    NOTE: masks can be changed, not sure if all of these are needed or correct
    '''
    def __init__(self, image):
        self.image = image
        self.mask_3x = None
        self.mask_2x = None
        self.mask_1x = None
        self.mask_points = None
        self.mask_inner_bullseye = None
        self.mask_outer_bullseye = None

    def segment(self):   
        raise NotImplementedError
    def crop_board(self):
        raise NotImplementedError
    def multiplier_mask(self):
        raise NotImplementedError
    def divide_multiplier_mask(self):
        raise NotImplementedError
    def create_singular_multiplier_mask(self):
        raise NotImplementedError
    def create_point_mask(self):
        self.mask_points = generate_mask(self.image)