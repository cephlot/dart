import cv2 as cv
from sys import platform

class cameraSetup:
    """
    Class providing methods for camera init.
    """
    
    @staticmethod
    def testDevice(source):
        """Test if capture device can be opened

        :param source: capture device index
        :type source: int
        :return: 0 if can open, 1 otherwise
        :rtype: int
        """
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
        """Get list of capture devices, with exception

        :param exception: exception index
        :type exception: int
        :return: list of capture devices
        :rtype: list
        """        
        valid_cams = []
        for i in range(8):
            if i is not exception:
                if cameraSetup.testDevice(i) == 0:
                    valid_cams.append(i)
                    print(" --- Able to open camera ", i, " --- ")
        return valid_cams

    @staticmethod
    def checkOS():
        """Checks which OS is currently running

        :raises RuntimeError: If running on unknown OS
        :return: 0 if linux or win32, 1 if darwin
        :rtype: int
        """  
        return 5000      
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
        """Waits until cameras are stable

        :param camera_indices: camera indices to wait for
        :type camera_indices: list
        :param caps: capture devices to wait for
        :type caps: list
        """        
        for cameras in range(len(camera_indices)):
            for i in range(50):
                ret, frame = caps[cameras].read()
