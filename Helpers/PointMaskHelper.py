import cv2
import numpy as np
'''
    Method to generate a point mask from one image.
    The method will generate 10 lines all with distinct angles. 
    This means that each line will segment the board according to the 
    point reagions of the board as these are the most distinguished lines.
    The image must not have lines that are more distinct than the point region lines.
    Parametres
    Every segment will be filled with a value from 1 to 20, these are NOT scores, only
    used to differentiate from each region.
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
    # Black out entire image
    h,w = image.shape[:2]
    lineImage = np.zeros((h,w,1), dtype = "uint8")
    angle_list = []
    i = 0
    range = 10
    # index of lines in order to seperate them
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
            cv2.line(lineImage,(x1,y1),(x2,y2),(255),1)
        i += 1
    
    filledImage = fillSegments(lineImage)
    filledImage = filledImage - lineImage
    return filledImage

'''
    Helper method that fills each segment
    with a unique colour. Colours range from
    1 to 20 in grayscale (1 dimension)
    -----------
    image
        Image to fill
    return
        Segmented Image
'''
def fillSegments(image):
    image2 = image.copy()
    h,w = image2.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    region = 1
    for x in range(w):
        # Top Border
        if(image2[0,x] == 0):
            cv2.floodFill(image2, mask, (x,0), (region))
            region +=1
        # Bottom Border
        if(image2[h-1,x] == 0):
            cv2.floodFill(image2, mask, (x,h-1), (region))
            region +=1
    for y in range(h):
        # Left Border
        if(image2[y,0] == 0):
            cv2.floodFill(image2, mask, (0,y), (region))
            region +=1
        # Right Border
        if(image2[y,w-1] == 0):
            cv2.floodFill(image2, mask, (w-1,y), (region))
            region +=1
    return image2



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