
import copy
from cv2 import imshow
from CoordinateProjector import CoordinateProjector
from DartLocalization import DartLocalization
import cv2 as cv

from PredictedCoordinate import PredictedCoordinate


class ScoreEvaluator:
    """
    Class that evaluates a score based on background image of board and image 
    of board with dart.
    Will use CoordinateProjector and DartLocalization to achive this.
    """

    def __init__(self):
        self.reference = cv.imread('images/pic_nice.jpg', cv.IMREAD_GRAYSCALE)
        self.board_mask = cv.imread('images/board_mask.png', cv.IMREAD_GRAYSCALE)
        self.DISTANCE_FACTOR = 1.1
        self.PIXEL_FACTOR = 10
        self.projectors = []

    def evaluate(self, image_B_frames, image_I_frames):
        """Uses the RegionSegmenter and dart localizer to score, call create_projection_matrix before calling this
        :param image_B_frames: images from all cameras before dart is thrown
        :type image_B_frames: list
        :param image_I_frames: images from all cameras after dart is thrown
        :type image_I_frames: list
        :param b_create_matrix: boolean create matrix
        :type b_create_matrix: bool

        :return: 0 if all transformations are bad
        :rtype: int
        """
        if(self.error_check_input(image_B_frames, image_I_frames)):  return 0
        coordinate_list         =  self.get_dart_coordinates(image_B_frames, image_I_frames)
        coordinate_list         =  self.check_if_no_dart(coordinate_list)
        proj_coordinate_list    =  self.project_coordinates(coordinate_list)
        if(len(proj_coordinate_list) == 0):
            print("ERROR: No good projeciton where possible, returning score 0")
            return 0, (0,0)
        proj_coordinate_list    =  self.quality_control_projected_coordinates(proj_coordinate_list)
        average_coordinate      =  self.average_coordinates(proj_coordinate_list)
        if(average_coordinate is None):
            print("evaluate -- ERROR -- could not create average coordinate, returning 0")
            return 0, (0,0)
        
        '''image_ref = cv.imread('images\pic_nice.jpg')
        test = image_ref
        for _,proj in enumerate(proj_coordinate_list):
            test = cv.circle(test, proj, 10, (250, 0, 0), 4)
        test = cv.circle(test, average_coordinate, 8, (0, 250, 0), 3)
        #cv.imshow("yes", test)
        cv.waitKey(0) '''
        score = self.score_coordinate(average_coordinate)
        print("score: ", score)
        return score, average_coordinate


    def error_check_input(self, image_B_frames,image_I_frames):
        """Checks the length of image lists
        :param image_B_frames: list of images before
        :type image_B_frames: list
        :param image_I_frames: list of images after
        :type image_I_frames: list
        :return: 1 if the lengths aren't the same, 0 otherwise
        :rtype: int
        """
        if(len(self.projectors) != len(image_B_frames)):
            print("ERROR - ScoreEvaluator.error_check_input - :  Did not get expected amount of frames as input")
        if(len(image_B_frames) != len(image_I_frames)):
            print("ERROR: Different length of image_B_frames and image_I_frames in evaluator")
            return 1
        if(len(image_B_frames) == 0):
            print("ERROR: No images to evaluate")
            return 1
        return 0

    def create_projection_matrix(self, image_B_frames):
        """Creates new projection matrix for projectors
        :param image_B_frames: before frames for projection matrix
        :type image_B_frames: list of images
        :param b_create_matrix: true if the program should create new matrix
        :type b_create_matrix: bool
        """
        print("create_projection_matrix - creating new Projection Matrix")

        if(len(self.projectors) == 0):
            self.create_projection_matrix_helper(image_B_frames, True)
        elif(len(image_B_frames) != len(self.projectors)):
            print("ERROR: Recieved less frames than expected to create Porjection Matrices")
            return 
        else:
            self.create_projection_matrix_helper(image_B_frames, False)


    def create_projection_matrix_helper(self, image_B_frames, no_existing_projectors):
        """Creates projectors and their projection matrix for all cameras if no exists
        otherwise only creates new projection matrix 
        :param image_B_frames: images before dart is thrown
        :type image_B_frames: list
        :return: projectors
        :rtype: list
        """
        for i, image_b in enumerate(image_B_frames):
            if(no_existing_projectors):
                self.projectors.append(CoordinateProjector(self.reference))
            image_B_gray = cv.cvtColor(image_b, cv.COLOR_BGR2GRAY)
            self.projectors[i].generate_matrix(image_B_gray)


    def get_dart_coordinates(self, image_B_frames, image_I_frames):
        """ Returns all dart coordinate estimates found by DartLocalization using all cameras before and after images
        Coordinates returned are PredictedCoordinate objects. this is done to keep track of
        what coordinates are from what camera even after deleting some bad coordinates
        :param image_B_frames: list of images before dart is thrown
        :type image_B_frames: list
        :param image_I_frames: list of images after dart is thrown
        :type image_I_frames: list
        :return: list of coordinates
        :rtype: list
        """

        coordinate_list = []
        for i, _ in enumerate(image_B_frames):
            x, y = DartLocalization.find_dart_point(image_B_frames[i], image_I_frames[i])
            if(not (x < 0 and y < 0)):
                pc = PredictedCoordinate(x,y,i)
                coordinate_list.append(pc)
        return coordinate_list





    def check_if_no_dart(self, coordinate_list):
        """Removes darts from coordinate list that were not found
        :param coordinate_list: list of coordinates
        :type coordinate_list: list
        :return: coordinate list
        :rtype: list
        """
        for c in coordinate_list:
            if c.get_x() < 1 and c.get_y() < 1:
                print(f'No dart ({c.get_x()},{c.get_y()})')
                coordinate_list.remove(c)
        return coordinate_list

    def project_coordinates(self, coordinate_list):
        """Projects all dart coordinates from DartLocalization.find_dart_point using the project_dart_coordinate method
        :param coordinate_list: coordinate list
        :type coordinate_list: list
        :return: projected coordinate list
        :rtype: list
        """

        proj_coordinate_list = []
        for c in coordinate_list:
            if(self.projectors[c.get_camera_index()].hasMatrix()):
                proj_coordinate_list.append(self.projectors[c.get_camera_index()].project_dart_coordinate((c.get_x(), c.get_y()))) 
        return proj_coordinate_list


    def quality_control_projected_coordinates(self, proj_coordinate_list):
        """Will remove a dart coordinate if:
            Three coordinates exists
            Distance from average coordinate is 1.3X further away than average distance from average coordinate
            Distance from average coordinate is at least 5 pixels
            Coordinate is furthest away
        :param proj_coordinate_list: projected coordinates list
        :type proj_coordinate_list: list
        :return: filtered list
        :rtype: list
        """

        proj = self.check_negative_projection(proj_coordinate_list)
        if(len(proj) != 3):
            return proj
        average = self.average_coordinates(proj)
        avarage_distance = 0
        for c in proj:
            avarage_distance += self.distance(average, c)
        avarage_distance = avarage_distance / len(proj)
        worst_c = None
        for c in proj:
            distanceFromAvarage = self.distance(average, c)
            if(distanceFromAvarage > avarage_distance*1.1 and distanceFromAvarage > self.PIXEL_FACTOR):
                if(worst_c is None):
                    worst_c = (c, distanceFromAvarage)
                elif(distanceFromAvarage > worst_c[1]):
                    worst_c = (c, distanceFromAvarage)
        if(not (worst_c is None)):
            print(f'quality_control_projected_coordinates: one bad dart cordinate, removing ({worst_c[0][1]},{worst_c[0][0]})')
            proj.remove(worst_c[0])
        return proj
    
    def check_negative_projection(self,coordinates):
        """Checks for negative projections and filters them out
        :param coordinates: coordinate list
        :type coordinates: list
        :return: filtered list
        :rtype: list
        """

        coordinatesCopy = copy.deepcopy(coordinates)
        
        for c in coordinates:
            if(c[0] < 1 or c[1] < 1):
                coordinatesCopy.remove(c)
                print(f"check_negative_projection -- ERROR -- Projected coordinate for dart out of bounce {c}")
            elif(c[0] > self.reference.shape[0] or c[1] > self.reference.shape[1]):
                print(f"check_negative_projection -- ERROR -- Projected coordinate for dart out of bounce {c}")
                coordinatesCopy.remove(c)
        return coordinatesCopy

    def score_coordinate(self, coordinate):
        """Scors the average dart coordinate using scoring mask
        :param coordinate: coordinate to compute from
        :type coordinate: list
        :return: score 
        :rtype: int
        """

        score = 0
        try:
            score = self.board_mask[round(coordinate[1])][round(coordinate[0])]
        except Exception as e:
            print("Can't score dart, coordinate is outside of range")
            print(e)
        return score

    def average_coordinates(self, coordinates):
        """Calculates the average coordinates
        :param coordinates: coordinate list
        :type coordinates: list
        :return: average coordinates
        :rtype: (int,int)
        """
        if(len(coordinates) == 0):
            print("average_coordinates -- ERROR -- No projected coordinate found to average -- returning (0,0)")
            return None
        c = [sum(x)/len(x) for x in zip(*coordinates)]
        return ((round(c[0])),round(c[1]))

    def distance(self, c1, c2):
        """Finds distance between two coordinates
        :param c1: first coordinate
        :type c1: (int,int)
        :param c2: second coordinate
        :type c2: (int,int)
        :return: distance between the coordinates
        :rtype: float
        """
        x1, y1 = c1
        x2, y2 = c2
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5