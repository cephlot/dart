import cv2

def open_camera(n):
    cap = cv2.VideoCapture(n, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    if not cap.isOpened():
        raise IOError("Couldn't open camera " + str(n))
    return cap

def print_camera_properties(cap, n):
    print("Properties of camera " + str(n))
    print("Resolution: " + str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) + "x" + str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

def show_next_frame(cap, n):
    ret, frame = cap.read()
    if not ret:
        raise IOError("Couldn't read frame from camera " + str(n))
    cv2.imshow(str(n), frame)

camera_indexes = [1,2]
caps = [None] * len(camera_indexes)
for i in range(len(camera_indexes)):
    caps[i] = open_camera(camera_indexes[i])

for i in range(len(camera_indexes)):
    print_camera_properties(caps[i], camera_indexes[i])

while True:
    for i in range(len(camera_indexes)):
        show_next_frame(caps[i], camera_indexes[i])
    cv2.waitKey(1)