from time import sleep
import cv2
from sys import platform
from datetime import datetime
from CameraSetup import cameraSetup

class MotionDetector:
    """
    Class for handling motion detection.
    """

    def __init__(self):
        bannedCam = cameraSetup.checkOS()
        #bannedCam = 2
        self.camera_indices = cameraSetup.getCams(bannedCam)
        #self.open_cameras()
    
    def __del__(self):
        for i in range(len(self.caps)):
            self.caps[i].release()

    def open_cameras(self):
        """Opens the camera devices and populates list.
        """
        self.caps = [None] * len(self.camera_indices)
        for i in range(len(self.caps)):
            self.caps[i] = cv2.VideoCapture(self.camera_indices[i])

        cameraSetup.stabilize(self.camera_indices, self.caps, 50)

        """
        # self.caps = [None] * len(self.camera_indices)
        # for i in range(len(self.caps)):
        #     self.caps[i] = cv2.VideoCapture(self.camera_indices[i])
        #     self.caps[i].set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        #     self.caps[i].set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        #     width = self.caps[i].get(cv2.CAP_PROP_FRAME_WIDTH)
        #     height = self.caps[i].get(cv2.CAP_PROP_FRAME_HEIGHT)
        #     if not self.caps[i].isOpened() or width != 1280 or height != 720:
        #         raise IOError("Couldn't open camera " + str(self.camera_indices[i]))
        """
    
    def read_frames(self):
        """Reads frames from open capture devices

        :raises IOError: if camera cannot be read from
        :return: list of one frame per camera
        :rtype: list
        """
        frames = [None] * len(self.caps)
        for i in range(len(self.caps)):
            ret, frame = self.caps[i].read()
            if not ret:
                raise IOError("Cannot read frame from camera " + str(self.camera_indices[i]))
            frames[i] = frame
        return frames

    def wait_for_motion(self):
        """Takes photos of background images (image_B) and detected images (image_I) containing a dart for all
        cameras.
        Waits for motion that exceeds a threshold. If motion is detected it takes the photos after waiting for motion 
        to stop.

        :return: tuple of lists containing images before and after
        :rtype: tuple
        """
        
        print("Waiting for motion...")
        previous_frame = [None] * len(self.caps)
        waiting_for_motion_end = False

        previous_frames = [[]] * len(self.caps)

        while True:
            # Get frames from all cameras
            frames = self.read_frames()
                
            for i in range(len(self.caps)):
                frame = frames[i]
                # Preprocess frame
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                processed_frame = cv2.GaussianBlur(src=frame_gray, ksize=(9,9), sigmaX=0)

                if previous_frame[i] is None:
                    previous_frame[i] = processed_frame
                    continue

                diff_frame = cv2.absdiff(src1=previous_frame[i], src2=processed_frame)
                previous_frame[i] = processed_frame
                previous_frames[i].append(frame)
                previous_frames[i] = previous_frames[i][-5:]
                thresh_frame = cv2.threshold(src=diff_frame, thresh=90, maxval=255, type=cv2.THRESH_BINARY)[1]

                if cv2.countNonZero(thresh_frame) > 10:
                    # Threshold frame contains white pixels
                    if not waiting_for_motion_end:
                        print("Motion detected!")
                        frames_before_motion = [None] * len(self.caps)
                        for i in range(len(self.caps)):
                            frames_before_motion[i] = previous_frames[i][0]
                        waiting_for_motion_end = True
                    waiting_start = datetime.now()
                elif waiting_for_motion_end and (datetime.now() - waiting_start).total_seconds() >= 0.5:
                    # No motion for at least 0.5s
                    print("Motion stopped!")
                    frames_after_motion = frames
                    waiting_for_motion_end = False
                    return frames_before_motion, frames_after_motion
                sleep(0.01)
