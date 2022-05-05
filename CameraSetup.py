from time import sleep
import cv2 as cv
from sys import platform
from datetime import datetime

class cameraSetup:
    @staticmethod
    def testDevice(source):
        cap = cv.VideoCapture(source)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
        if cap is None or not cap.isOpened() or width != 1280 or height != 720:
            print('Warning: unable to open video source: ', source)
            return 1
        return 0

    @staticmethod
    def getCams(excption):
        valid_cams = []
        for i in range(8):
            if i is not excption:
                if cameraSetup.testDevice(i) is 0:
                    valid_cams.append(i)
        
        return valid_cams
        
    @staticmethod
    def checkOS():
        if platform == "linux" or platform == "linux2":
            return 0
        elif platform == "darwin":
            return 1
        elif platform == "win32":
            return 0
        else:
            raise RuntimeError("Unknown operating system")
