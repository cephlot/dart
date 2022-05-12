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
        if (image_reference is None):
            print("Reference image is None on init for CoordinateProjector.")
        self.img_ref = image_reference
        self.matrix = None
        self.MIN_MATCH_COUNT = 35

    def set_img_ref(self, image_reference):
        """Sets image reference
        :param image_reference: image to change to
        :type image_reference: image
        """
        self.img_ref = image_reference

    
    def generate_matrix(self, img_cam):
        """Generates a transformation metrix using a camera image and a static
        reference image
        :param img_cam: Camera image
        :type img_cam: image
        :return: None if not enough matches are found
        :rtype: None
        """
        img_ref = self.img_ref
        if(img_cam is None):
            print("No image in generate_matrix, img_cam is None")
            return np.zeros((3,3))
        kp1, kp2, matches = self.get_matches_and_keypoints(img_cam)
        good = self.get_good_matches(matches)
        matrix = None
        print("SIFT good matches: " + str(len(good)))
        if len(good)>self.MIN_MATCH_COUNT:
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            matrix, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()
            h,w = img_cam.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv.perspectiveTransform(pts,matrix)
            img_ref = cv.polylines(img_ref,[np.int32(dst)],True,255,3, cv.LINE_AA)
        else:
            print( "Not enough matches are found - {}/{}".format(len(good), self.MIN_MATCH_COUNT) )
            return None
        '''img_warped = cv.warpPerspective(img_cam,matrix,self.img_ref.shape)
        cv.imshow("original", img_cam)   
        cv.waitKey(0)
        cv.imshow("warped", img_warped)   
        cv.waitKey(0)'''
        '''draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)
        image_pog = cv.warpPerspective(img_cam, matrix, (img_cam.shape[0], img_ref.shape[1]))
        img3 = cv.drawMatches(img_cam,kp1,image_pog,kp2,good,None,**draw_params)
        cv.imshow(f"good matches are {len(good)}", img3)'''


        self.matrix = matrix


    def get_matches_and_keypoints(self, img_cam):
        '''
        Uses SIFT and FLANN-based matcher on img_cam and img_ref to get the keypoints and matches between images.
        -------------
        @param img_cam cameras picture
        @return kp1 keypoints from camera
        @return kp2 keypoints from reference picture
        @return matches match list between keypoints
        '''
        sift = cv.SIFT_create(400)
        kp1, des1 = sift.detectAndCompute(img_cam,None)
        kp2, des2 = sift.detectAndCompute(self.img_ref,None)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 10)
        flann = cv.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1,des2,k=2)
        return kp1, kp2, matches

    def get_good_matches(self, matches):
        '''
        Store all the good matches as per Lowe's ratio test.
        '''
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)
        return good

    def project_dart_coordinate(self, dart_coordinate):
        """Projects a coordinate from dart localization to a coordinate on a 
        static mask image. Make sure to run generate_matrix in order to have a 
        projection matrix for the projection
        :param dart_coordinate: Coordinate to project
        :type dart_coordinate: (int,int)
        :return: Real dart board coordinates
        :rtype: (int,int)
        """
        c = dart_coordinate
        if(self.matrix is None):
            print("ERROR in project_dart_coordinate, projection matrix is None")
            return (0,0)
        c = np.array([[c[0], c[1]]], dtype='float32')
        c = np.array([c])
        c = cv.perspectiveTransform(c, self.matrix)
        return (int(c[0][0][0]), int(c[0][0][1]))

    def hasMatrix(self):        
        if(self.matrix is None):
            return False
        return True