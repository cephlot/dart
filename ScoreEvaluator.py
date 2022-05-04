
from cv2 import imshow
from DartLocalization import DartLocalization
from RegionSegmenter import RegionSegmenter

import cv2 as cv


class ScoreEvaluator:
    '''
    Class that evaluates a score based on background image of board and image 
    of board with dart
    ------------
    image_B
        the image of an empty dart board
    image_I
        the image of an dart board with dart
    NOTE: work in progress these attributes are temporary
    ''' 
    def __init__(self, image_B, image_I, projector):
        self.image_B = image_B
        self.image_I = image_I
        self.projector = projector

        image_B_gray = cv.cvtColor(image_B, cv.COLOR_BGR2GRAY)
        self.projector.generate_matrix(image_B_gray)

    def evaluate(self):
        '''
        Uses the RegionSegmenter and dart localizer thingy to score
        '''
        x, y = DartLocalization.find_dart_point(self.image_B, self.image_I)
        if x < 0 and y < 0:
            print(f'No dart ({x},{y})')
            return 0
        multiplier = 0

        print(f'x: {x}, y: {y}')

        hit_loc = self.projector.project_dart_coordinate((x, y))

        test = cv.circle(self.projector.img_ref, hit_loc, 10, (250, 0, 0), 4)
        cv.imshow("yes", test)

        return 0

        '''
        if self.segmenter.mask_inner_bullseye[y][x]:
            print('bulleye!')
            return 50
        elif self.segmenter.mask_outer_bullseye[y][x]:
            print('lesser bullseye')
            return 25
        elif self.segmenter.mask_3x[y][x]:
            print('3x')
            multiplier = 3
        elif self.segmenter.mask_2x[y][x]:
            print('2x')
            multiplier = 2
        elif self.segmenter.mask_1x[y][x]:
            print('1x')
            multiplier = 1
        else:
            print('outside')
            return 0
        '''
        #print(f'Region: {self.segmenter.mask_points[y][x]}')

        #return self.segmenter.mask_points[y][x]*multiplier
