import cv2

def open_camera(i):
    cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
    if not cap.isOpened():
        print(f'Couldn\'t open camera {i}')
        return False, None
    print(f'Resolution of camera {i} is {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')
    width = 1280
    height = 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if cap.get(cv2.CAP_PROP_FRAME_WIDTH) != width or cap.get(cv2.CAP_PROP_FRAME_HEIGHT) != height:
        print(f'Couldn\'t set resolution of camera {i} to {width}x{height}: resolution is {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')
        return False, None
    return True, cap

cap_indices = [0,1]
caps = []
for i in range(len(cap_indices)):
    success, cap = open_camera(cap_indices[i])
    if success:
        caps.append(cap)

if len(caps) == 0:
    print('No cameras could be opened')
else:
    while(True):
        for i in range(len(caps)):
            ret, frame = caps[i].read()
            if ret == False:
                break
            cv2.imshow(f'Cam {cap_indices[i]}', frame)
        key = cv2.waitKey(10)
        if key != -1:
            break

cv2.destroyAllWindows()
