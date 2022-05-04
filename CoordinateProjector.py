import numpy as np
import cv2 as cv

class CoordinateProjector:
    '''
    Class for projecting dart coordinates from camera image
    onto a statis point mask image in order to get the points.
    Code taken from: 
    https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html
    
    First generate Matrix and then project the coordinates.

    
    '''
    
    def __init__(self, image_reference):
        self.img_ref = image_reference
        self.matrix = None
        self.MIN_MATCH_COUNT = 10

    def set_img_ref(self, image_reference):
        self.img_ref = image_reference

    
    def generate_matrix(self, img_cam):
        '''
        Generates a transformation matrix using a camera image and
        a static reference image
        
        '''
        # Initiate SIFT detector
        sift = cv.SIFT_create(400)
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img_cam,None)
        kp2, des2 = sift.detectAndCompute(self.img_ref,None)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)
        flann = cv.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1,des2,k=2)
        # store all the good matches as per Lowe's ratio test.
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)
        matrix = None
        print("good matches: " + str(len(good)))
        if len(good)>self.MIN_MATCH_COUNT:
            # good = good[:10]
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            matrix, _ = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
        else:
            print( "Not enough matches are found - {}/{}".format(len(good), self.MIN_MATCH_COUNT) )
        self.matrix = matrix


    def project_dart_coordinate(self, dart_coordinate):
        '''
        projects a coordinate from dart localization to a coordinate
        on the static mask image. Make sure to run generate_matrix
        in order to have a projection matrix for the projection.
        '''
        c = dart_coordinate
        if(self.matrix == None):
            print("ERROR in project_dart_coordinate, projection matrix is None")
            return (0,0)
        c = np.array([[c[0], c[1]]], dtype='float32')
        c = np.array([c])
        c = cv.perspectiveTransform(c, self.matrix)
        return (int(c[0][0][0]), int(c[0][0][1]))