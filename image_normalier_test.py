import cv2
import numpy as np
from ImageNormalizer import ImageNormalizer

camera_indices = [0,2]

caps = [None] * len(camera_indices)
for i in range(len(caps)):
    caps[i] = cv2.VideoCapture(camera_indices[i])
    width = 640
    height = 360
    caps[i].set(cv2.CAP_PROP_FRAME_WIDTH, width)
    caps[i].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if not caps[i].isOpened():
        raise IOError("Couldn't open camera " + str(camera_indices[i]))
    if caps[i].get(cv2.CAP_PROP_FRAME_WIDTH) != width or caps[i].get(cv2.CAP_PROP_FRAME_HEIGHT) != height:
        raise IOError("Couldn't set resolution for camera " + str(camera_indices[i]))

while True:
    frames = []
    for i in range(len(caps)):
        ret, frame = caps[i].read()
        if not ret:
            raise IOError("Couln't read frame")
        frames.append(frame)

    images = []
    for i in range(len(frames)):
        corrected_frame = ImageNormalizer.normalize_image(frames[i])
        image = np.hstack((frames[i], corrected_frame))
        images.append(image)

    image = images[0]
    for i in range(1,len(images)):
        image = np.vstack((image, images[i]))
    cv2.imshow("Image", image)
    if cv2.waitKey(1) == 27:
        break
