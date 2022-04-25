import cv2
import numpy as np
'''
    Method to generate a point mask from one image.
    The method will generate 10 lines all with distinct angles. 
    This means that each line will segment the board according to the 
    point reagions of the board as these are the most distinguished lines.
    The image must not have lines that are more distinct than the point region lines.
    Parametres
    -----------
    image
        the image to generate lines from
    return
        the same image as the parametre but with added lines.
'''
def generate_point_mask(image):
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
    return image
'''
    Helper method that checks if the angle theta
    is too close to antother already saved angle in list. 
    Parametres
    -----------
    theta
        One angle to compare
    list
        List of angles to compare
    return
        True if a line in the list is the same as theta
        False if no line matches theta
'''
def exists_line(theta, list):
    angle = np.round(theta/np.pi*180)
    for a in list:
        d = a - angle
        d = (d + 180) % 360 - 180
        if(abs(d) < 10):
            return True
    return False