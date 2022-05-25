import cv2


for i in range(100):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if not cap.isOpened():
        break
    for j in range(10):
        ret, frame = cap.read()
        if not ret:
            raise IOError(f'Couldn\'t read camera {i}')
    ret, frame = cap.read()
    cv2.imshow(f'Cam {i}', frame)

cv2.waitKey(0)