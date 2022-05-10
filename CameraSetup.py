from time import sleep
import cv2 as cv
from sys import platform
from datetime import datetime


class cameraSetup:
    '''
    Class providing methods for camera init.
    '''
    
    @staticmethod
    def testDevice(source):
        '''
        Static method testing if a source can be opened

        :param source: Camera source to be tested
        :return: 0 if source can be opened, otherwise 1
        '''
        cap = cv.VideoCapture(source)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
        if cap is None or not cap.isOpened():
            print('Warning: unable to open video source: ', source)
            return 1
        return 0

    @staticmethod
    def getCams(exception):
        '''
        Static method to get valid cameras.

        :param exception: Excluded camera
        :returns: A list of valid cameras.
        '''
        valid_cams = []
        for i in range(8):
            if i is not exception:
                if cameraSetup.testDevice(i) == 0:
                    valid_cams.append(i)
        return valid_cams

    @staticmethod
    def checkOS():
        '''
        Static method to check which OS is running. Raises exception if running 
        on anything other than linux, darwin or win32.

        :return: 1 if platform is darwin, 0 if linux or win32.
        '''
        if platform == "linux" or platform == "linux2":
            return 0
        elif platform == "darwin":
            return 1
        elif platform == "win32":
            return 0
        else:
            raise RuntimeError("Unknown operating system")

    @staticmethod
    def stabilize(camera_indices, caps):
        '''
        Static method that waits until cameras are stable.

        :param camera_indices: Cameras indices to read from.
        :param caps: Capture devices to read from.
        '''
        for cameras in range(len(camera_indices)):
            for i in range(50):
                ret, frame = caps[cameras].read()
