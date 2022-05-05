
from cv2 import imshow
from CoordinateProjector import CoordinateProjector
from DartLocalization import DartLocalization
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
    def __init__(self, image_B):
        self.reference = cv.imread('images/pic_nice.jpg', cv.IMREAD_GRAYSCALE)
        self.projectors = self.create_projectors(image_B)
        


    def evaluate(self, image_B, image_I):
        '''
        Uses the RegionSegmenter and dart localizer thingy to score
        ''' 
        self.create_projector()
        coordinate_list =       self.get_dart_coordinates(image_B, image_I)
        coordinate_list =       self.check_if_no_dart(coordinate_list)
        proj_coordinate_list =  self.project_coordinates(coordinate_list)
        proj_coordinate_list =  self.quality_control_projected_coordinates(self, proj_coordinate_list)
        for proj in enumerate(proj_coordinate_list):
            test = cv.circle(self.projector.img_ref, proj, 10, (250, 0, 0), 4)
            cv.imshow("yes", test)
        return 0

    def get_dart_coordinates(self, image_B, image_I):
        '''
        Returns all dart coordinate estimates found by DartLocalization using all cameras before and after images
        '''
        coordinate_list = []
        for i, _ in enumerate(self.frames_before):
            x, y = DartLocalization.find_dart_point(image_B[i], image_I[i])
            coordinate_list.append((x,y,i))
        return coordinate_list

    def create_projectors(self, image_B):
        '''
        Creates projectors and their projection matrix for all cameras 
        '''
        projectors = [] * len(self.frames_before)
        for i, _ in enumerate(self.frames_before):
            projectors[i] = CoordinateProjector(self.reference)
            image_B_gray = cv.cvtColor(image_B, cv.COLOR_BGR2GRAY)
            projectors[i].generate_matrix(image_B_gray)

    def check_if_no_dart(self, coordinate_list):
        '''
        Removes darts from coordinate list that were not found
        '''
        for i, c in enumerate(coordinate_list):
            if c[0] < 0 and c[1] < 0:
                print(f'No dart ({c[0]},{c[1]})')
                del coordinate_list[i]
            print(f'x: {c[0]}, y: {c[1]}')
        return coordinate_list

    def project_coordinates(self, coordinate_list):
        '''
        Projects all dart coordinates from DartLocalization.find_dart_point using the project_dart_coordinate method
        '''
        proj_coordinate_list = []
        for i, c in enumerate(coordinate_list):
            proj_coordinate_list.append(self.projectors[c[2]].project_dart_coordinate((c[0], c[1]))) 
        return proj_coordinate_list

    def quality_control_projected_coordinates(self, proj_coordinate_list):
        proj = proj_coordinate_list
        average = [sum(x)/len(x) for x in zip(*proj_coordinate_list)]
        #if(len(proj_coordinate_list) == 3):
        #    if(average > self.distance(proj[0], proj[1])):

    def distance(self, c1, c2):
        x1, y1 = c1
        x2, y2 = c2
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

