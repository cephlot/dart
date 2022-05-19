import math
import cv2
from cv2 import imshow
from cv2 import goodFeaturesToTrack
from matplotlib import pyplot as plt
import numpy as np
from scipy.ndimage.interpolation import rotate
from math import atan2, cos, sin, sqrt, pi

from sklearn.metrics import roc_auc_score
from ImageNormalizer import ImageNormalizer

class DartLocalization:

    def drawAxis(img, p_, q_, colour, scale):
        """draw out axis on the image

        :param img: input image
        :type img: image
        :param p_: p values
        :type p_: int
        :param q_: q values
        :type q_: int
        :param colour: color of the arrow
        :type colour: int
        :param scale: scale of the image
        :type scale: image
        """        
        p = list(p_)
        q = list(q_)
        
        angle = atan2(p[1] - q[1], p[0] - q[0]) # angle in radians
        hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
        # Here we lengthen the arrow by a factor of scale
        q[0] = p[0] - scale * hypotenuse * cos(angle)
        q[1] = p[1] - scale * hypotenuse * sin(angle)
        cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)
        # create the arrow hooks
        p[0] = q[0] + 9 * cos(angle + pi / 4)
        p[1] = q[1] + 9 * sin(angle + pi / 4)
        cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)
        p[0] = q[0] + 9 * cos(angle - pi / 4)
        p[1] = q[1] + 9 * sin(angle - pi / 4)
        cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)

    def getOrientation(pts, img):
        """get the orientation of a blob of pixels using PCA to calculate direction of the dart

        :param pts: points of interest (coordinates)
        :type pts: int
        :param img: input image
        :type img: image
        :return: the angle in radiants
        :rtype: float
        """        
        sz = len(pts)
        data_pts = np.empty((sz, 2), dtype=np.float64)
        for i in range(data_pts.shape[0]):
            data_pts[i,0] = pts[i,0,0]
            data_pts[i,1] = pts[i,0,1]
        # Perform PCA analysis
        mean = np.empty((0))
        mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean)
        # Store the center of the object
        cntr = (int(mean[0,0]), int(mean[0,1]))
        
        
        cv2.circle(img, cntr, 3, (255, 0, 255), 2)
        p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
        p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
        DartLocalization.drawAxis(img, cntr, p1, (0, 255, 0), 1)
        DartLocalization.drawAxis(img, cntr, p2, (255, 255, 0), 5)
        angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
        
        return angle
    


    def dist(x1,y1, x2,y2, x3,y3):
        """get the distance between points

        :param x1: x coordinate 1
        :type x1: int
        :param y1: y coordinate 1
        :type y1: int
        :param x2: x coordinate 2
        :type x2: int
        :param y2: y coordinate 2
        :type y2: int
        :param x3: x coordinate 3
        :type x3: int
        :param y3: y coordinate 3
        :type y3: int
        :return: distance between points
        :rtype: int
        """        
        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        dist = math.sqrt(dx*dx + dy*dy)

        return dist


    def img2gray(img):
        """Takes in an image as an input and converts it into a
        grayscaled image

        :param img: input RGB image
        :type img: image
        :return: grayscaled image
        :rtype: image
        """        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img_gray
    
    def getDiff(clean_plate, new_img):
        """Creates an image that is the difference between a image with and
        without the dart

        :param clean_plate: image without the dart in RGB
        :type clean_plate: image
        :param new_img:  image with the dart in RGB
        :type new_img: image
        :return: difference image
        :rtype: image
        """        
        diff = cv2.absdiff(clean_plate, new_img)
        return diff

    def thresholding(clean_plate, new_img):
        """Doing thresholding on the image to isolate only the dart
        from the image

        :param clean_plate: image without the dart in RGB
        :type clean_plate: image
        :param new_img: image with the dart in RGB
        :type new_img: image
        :return: thresholded image
        :rtype: binary image
        """        
        diff_img = DartLocalization.getDiff(new_img, clean_plate)
        diff_img = DartLocalization.img2gray(diff_img)

        img_thresh = DartLocalization.thresholding_from_diff(diff=diff_img)
        
        return diff_img, img_thresh
    
    def thresholding_from_diff(diff):
        """Gets the threshold from the diff image

        :param diff: image of the difference between the image with and without the dart
        :type diff: image
        :return: threshold image
        :rtype: binary image
        """        
    
        img_blur = cv2.GaussianBlur(diff, (3,3), 0)

        _, img_threshold = cv2.threshold(img_blur, 15, 255, cv2.THRESH_BINARY)
        return img_threshold

    def erode_dilate(image_thresh):
        """performs erode, dilate, open and close to get a more clean segmentation/threshold

        :param image_thresh: thresholded image
        :type image_thresh: binary image
        :return: improved thresholded image
        :rtype: binary image
        """ 
        big_kernel = np.ones((5,5), np.int8)
        small_kernel = np.ones((3,3), np.int8)
        #image_thresh = cv2.erode(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.dilate(image_thresh, big_kernel, iterations=1)
        image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_CLOSE, kernel=(3,3), iterations=2)
        return image_thresh
        """       
        small_kernel = np.ones((5,5), np.int8)
        smaller_kernel = np.ones((3,3), np.int8)
        big_kernel = np.ones((9,9), np.int8)

        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.dilate(image_thresh, big_kernel, iterations=1)
        image_thresh = cv2.erode(image_thresh, small_kernel, iterations=3)
        image_thresh = cv2.dilate(image_thresh, small_kernel, iterations=1)
        image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_CLOSE, kernel=(3,3), iterations=2)
        image_thresh = cv2.morphologyEx(image_thresh, cv2.MORPH_OPEN, kernel=(3,3), iterations=2)
        return image_thresh
        """

    def getFeatures(img_in):
        """Using cv2 goodFeaturesToTrack to find points of interest (poi) to track in the image. Returns a array of all coordinates

        :param img_in: input image to be scanned for points of interest
        :type img_in: image
        :return: array of points of interest
        :rtype: int
        """        
        edges = cv2.goodFeaturesToTrack(img_in, 250, 0.008, 1, mask=None, blockSize=3, useHarrisDetector=1, k=0.08)  # k=0.08
        corners = np.int0(edges)

        return corners

    def filterCorners(corners):
        """Filter the array of points of interest to only get the cluster with the highest intensity, in theory we should only get points of the dart

        :param corners: array of points of interest 
        :type corners: int
        :return: filtered array of points of interest
        :rtype: int
        """        
        cornerdata = []
        tt = 0
        mean_corners = np.mean(corners, axis=0)
        for i in corners:
            xl, yl = i.ravel()
            # filter noise to only get dart arrow
            ## threshold important -> make accessible
            if abs(mean_corners[0][0] - xl) > 180:
                cornerdata.append(tt)
            if abs(mean_corners[0][1] - yl) > 120:
                cornerdata.append(tt)
            tt += 1

        corners_new = np.delete(corners, [cornerdata], axis=0)  # delete corners to form new array

        return corners_new

    def filterCornersLine(corners, rows, cols):
        """another filtering method. Fits a line between points and appends if the distance between those points are within a certain limit

        :param corners: array of point of interests
        :type corners: int
        :param rows: amount of rows in the image
        :type rows: int
        :param cols: amount of columns in the image
        :type cols: int
        :return: final filtered array of points of interest
        :rtype: int
        """        
        [vx, vy, x, y] = cv2.fitLine(corners, cv2.DIST_HUBER, 0, 0.1, 0.1)
        lefty = int((-x * vy / vx) + y)
        righty = int(((cols - x) * vy / vx) + y)

        cornerdata = []
        tt = 0
        for i in corners:
            xl, yl = i.ravel()
            # check distance to fitted line, only draw corners within certain range
            distance = DartLocalization.dist(0, lefty, cols - 1, righty, xl, yl)
            if distance > 30:  ## threshold important -> make accessible
                cornerdata.append(tt)

            tt += 1

        corners_final = np.delete(corners, [cornerdata], axis=0)  # delete corners to form new array

        return corners_final

    def rotateImage(img, angle):
        """Rotates the image after a set angle

        :param img: input image
        :type img: image
        :param angle: angle to rotate
        :type angle: angle (in radiants)
        :return: rotated image
        :rtype: image
        """        
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY), math.degrees(angle), 1.0)
        return cv2.warpAffine(img, M, (w, h))

    def linearErode(img):
        """Eroding method using linear structural element

        :param img: input image
        :type img: image
        :return: output image
        :rtype: image
        """        
        xb,yb,wb,hb = cv2.boundingRect(img)
        
        rotated_horizontal = int(hb // 3)

        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rotated_horizontal))
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        img_new = cv2.dilate(img, kernel, iterations=1)
        return cv2.erode(img_new, horizontalStructure, iterations=1)
    
    def calculateCenterOfPixelMass(dart_mask):
        """Calculates the center of mass on the binary image

        :param dart_mask: mask of the dart
        :type dart_mask: binary image
        :return: the coordinates of the center of mass in pixel grid
        :rtype: int, int
        """        
        # calculate center of mass of dart pixels in binary image
        m = cv2.moments(dart_mask)
        center_of_mass_x = m["m10"] / m["m00"]
        center_of_mass_y = m["m01"] / m["m00"]

        return center_of_mass_x, center_of_mass_y

    def getPointPosition(dart_mask ,center_of_mass_x, center_of_mass_y):
        """get the coordinates of the point of the dart by calculating which point is furthest from the center of mass

        :param dart_mask: mask of the dart
        :type dart_mask: binary image
        :param center_of_mass_x: the center of mass in x coordinates
        :type center_of_mass_x: int
        :param center_of_mass_y: the center of mass in y coordinates
        :type center_of_mass_y: int
        :return: returns the predicted point of the dart as well as the opposite point of the dart.
        :rtype: int, int, int, int
        """        
        # Find pixel furthest away from center of mass (this should be the point of the dart)
        nonzero = cv2.findNonZero(dart_mask)
        distances = np.sqrt((nonzero[:,:,0] - center_of_mass_x) ** 2 + (nonzero[:,:,1] - center_of_mass_y) ** 2)
        max_index = np.argmax(distances)
        
        max_x = nonzero[max_index,0,0]
        max_y = nonzero[max_index,0,1]

        distance_far_away = np.sqrt((nonzero[:,:,0] - max_x) ** 2 + (nonzero[:,:,1] - max_y) ** 2)
        max_index_far_away = np.argmax(distance_far_away)

        op_x = nonzero[max_index_far_away,0,0]
        op_y = nonzero[max_index_far_away,0,1]

        return max_x, max_y, op_x, op_y

    def dartPointCorrection(dart_mask, max_x, max_y, op_x, op_y, boarder_limit):
        """Corrects the dart tips position in case the tip is predicted to be on the boarder of the frame

        :param dart_mask: a mask of the dart
        :type dart_mask: binary image
        :param max_x: predicted x coordinates of the dart point
        :type max_x: int
        :param max_y: predicted y coordinates of the dart point
        :type max_y: int
        :param op_x: opposite x coordinates of the dart point
        :type op_x: int
        :param op_y: opposite y coordinates of the dart point
        :type op_y: int
        :param boarder_limit: number of pixels from the boarder
        :type boarder_limit: int
        :return: the coordinates of the dart point corrected
        :rtype: int, int
        """        

        if max_y > dart_mask.shape[0] - boarder_limit or max_y < boarder_limit or max_x > dart_mask.shape[1] - boarder_limit or max_x < boarder_limit:
            max_y = op_y
            max_x = op_x
        
        return max_x, max_y

    def getContour(img, diff_img, boarder_limit, clean):
        """Gets a list of the contours (blobs of pixels) and stores them from largest to smallest.
        The dart should be the largest and therefore be the shape that we subtract to only get the dart in the threshold
        Performs a contour check again on the new subtracted diff image for a cleaner result

        :param img: input image
        :type img: image
        :param diff_img: image of the difference between the image with and without the dart
        :type diff_img: image
        :param boarder_limit: number of pixels from the boarder
        :type boarder_limit: int
        :raises RuntimeError: Error if no contours are found
        :return: coordinates for the dart point on the picture in pixel grid
        :rtype: int, int
        """        
        
        threshold = img

        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            print("ERROR getContour no contours")
            return -1,-1
        cnts = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

        threshold = np.zeros(threshold.shape, np.uint8)
        cv2.fillPoly(threshold, pts =[cnts[0]], color=255)

        diff_img = cv2.subtract(threshold, diff_img)

        contours, hierarchy = cv2.findContours(diff_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            print("ERROR getContour no contours")
            return -1,-1

        c = max(contours, key = cv2.contourArea)

        # Subtract everything outside contour
        contour_mask = np.zeros((diff_img.shape[0],diff_img.shape[1],1), np.uint8)
        contour_mask = cv2.fillPoly(contour_mask, pts=[c], color=255)

        dart_mask = cv2.subtract(threshold, cv2.bitwise_not(contour_mask))
            
        angle = None
        pca_img = dart_mask.copy()
        for i, cont in enumerate(contours):
            # Calculate the area of each contour
            area = cv2.contourArea(cont)
            # Ignore contours that are too small or too large
            if area < 1e2 or 1e5 < area:
                continue
            # Find the orientation of each shape
            angle = DartLocalization.getOrientation(cont, pca_img)
            
        rotated = DartLocalization.rotateImage(img=threshold, angle=angle)
        extractedDartImg = DartLocalization.linearErode(rotated)
        enhanced = DartLocalization.rotateImage(img=extractedDartImg, angle=(-angle))

        center_of_mass_x, center_of_mass_y = DartLocalization.calculateCenterOfPixelMass(dart_mask=enhanced)
        max_x, max_y, op_x, op_y = DartLocalization.getPointPosition(dart_mask=enhanced, center_of_mass_x=center_of_mass_x, center_of_mass_y=center_of_mass_y)

        #DartLocalization.printDebug(dart_mask, max_x, max_y, op_x, op_y, boarder_limit, clean)

        return DartLocalization.dartPointCorrection(dart_mask=dart_mask, max_x=max_x, max_y=max_y, op_x=op_x, op_y=op_y, boarder_limit=boarder_limit)

    def printDebug(dart_mask, max_x, max_y, op_x, op_y, board_limiter, image):
        """Debug print method

        :param dart_mask: mask of the dart
        :type dart_mask: binary image
        :param max_x: predicted x coordinates of the dart point
        :type max_x: int
        :param max_y: predicted y coordinates of the dart point
        :type max_y: int
        :param op_x: opposite x coordinates of the dart point
        :type op_x: int
        :param op_y: opposite y coordinates of the dart point
        :type op_y: int
        :param board_limiter: number of pixels from the boarder
        :type board_limiter: int
        """        
        print("dartMask size:", dart_mask.shape[0], dart_mask.shape[1])
        print("image size:", image.shape[0], image.shape[1])
        print("estimated point:",max_x, max_y)
        print("opposite point:",op_x, op_y)
        print("boarder limit", board_limiter)

        image = cv2.circle(image, (int(max_x), int(max_y)), radius=2, color=(0,255,0), thickness=2)
        image = cv2.circle(image, (int(op_x), int(op_y)), radius=2, color=(0,0,255), thickness=2)
        
        cv2.imshow("mask", dart_mask)
        cv2.imshow("img", image)
        cv2.waitKey(0)

    @staticmethod
    def find_dart_point(image_without_dart, image_with_dart):
        """Finds the darts position on the board

        :param image_without_dart: clean image without the dart
        :type image_without_dart: image
        :param image_with_dart: image with the dart
        :type image_with_dart: image
        :return: coordinates for the darts position
        :rtype: int, int
        """        

        image_with_dart = ImageNormalizer.normalize_image(ImageNormalizer.clahe_EQ(image_with_dart))
        image_without_dart = ImageNormalizer.normalize_image(ImageNormalizer.clahe_EQ(image_without_dart))

        # image_with_dart = cv2.resize(image_with_dart, (640, 480), interpolation=cv2.INTER_AREA)
        # image_without_dart = cv2.resize(image_without_dart, (640, 480), interpolation=cv2.INTER_AREA)
        diff_img, threshold = DartLocalization.thresholding(image_without_dart, image_with_dart)

        goodFeaturesToTrack_img = diff_img.copy()
        rows, cols = diff_img.shape[:2]
        poi = DartLocalization.getFeatures(goodFeaturesToTrack_img)
        poi = DartLocalization.filterCorners(poi)
        poi = DartLocalization.filterCornersLine(poi, rows, cols)

        for i in range(1, len(poi)):
            end = poi[i][0]
            start = poi[i-1][0]
            cv2.line(goodFeaturesToTrack_img, start, end, (255,255,255))
            
        goodFeaturesToTrack_img = cv2.fillPoly(goodFeaturesToTrack_img, pts=[poi], color=255)
        
        _, goodFeaturesToTrack_img = cv2.threshold(goodFeaturesToTrack_img, 240, 255, cv2.THRESH_BINARY)
        goodFeaturesToTrack_img = cv2.dilate(goodFeaturesToTrack_img, np.ones((5,5)))
        goodFeaturesToTrack_img = cv2.morphologyEx(goodFeaturesToTrack_img, cv2.MORPH_CLOSE, kernel=np.ones((1,1)), iterations=2)

        return DartLocalization.getContour(goodFeaturesToTrack_img, diff_img, 5, image_with_dart)