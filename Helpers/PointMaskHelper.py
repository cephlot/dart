import cv2
import numpy as np


def generate_mask(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cann_img = cv2.Canny(image_gray,200,300)
    lines = cv2.HoughLines(cann_img, 1, np.pi/180, 120, np.array([]))
    angle_list = []
    i = 0
    range = 10
    while i < range:
        line = lines[i]
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        if(exists_line(theta, angle_list)):
            range += 1
        else:
            angle_list.append(np.round(theta/np.pi*180))
            cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)
        i += 1
 
    cv2.imwrite('/mnt/c/dart/pics/image.png', image)
    cv2.imwrite('/mnt/c/dart/pics/cann_img.png', cann_img)

def exists_line(theta, list):
    angle = np.round(theta/np.pi*180)
    for a in list:
        d = a - angle
        d = (d + 180) % 360 - 180
        if(abs(d) < 10):
            return True
    return False


image = cv2.imread('/mnt/c/dart/pics/pic.png') 
generate_mask(image)