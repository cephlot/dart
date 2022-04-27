import cv2
import numpy as np

def generate_point_mask(image, score_region, closest_score ):
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
    seed   
        The point region nearest the mounted camera (center bottom of image)
    return
        the same image as the parametre but with added lines.
    '''
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cann_img = cv2.Canny(image_gray,100,200)
    image_cropped = cv2.bitwise_and(cann_img, score_region, mask = None) 
    lines = cv2.HoughLines(image_cropped, 1, np.pi/180, 120, np.array([]))
    cv2.imwrite('/mnt/c/dart/pics/cann_img.png', image_cropped)
    # Black out entire image
    h,w = image.shape[:2]
    lineImage = np.zeros((h,w,1), dtype = "uint8")
    lineImage = draw_lines(lineImage, lines)
    filledImage = fillSegments(lineImage, closest_score)
    filledImage = filledImage - lineImage
    return filledImage

def draw_lines(lineImage, lines):
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
        x1 = int(x0 + 20000*(-b))
        y1 = int(y0 + 20000*(a))
        x2 = int(x0 - 20000*(-b))
        y2 = int(y0 - 20000*(a))
        if(exists_line(theta, angle_list)):
            range += 1
        else:
            angle_list.append(np.round(theta/np.pi*180))
            cv2.line(lineImage,(x1,y1),(x2,y2),(255),1)
        i += 1
    return lineImage






def fillSegments(image, closest_score):
    '''
    Helper method that fills each segment
    with a unique colour. Colours range from
    1 to 20 in grayscale (1 dimension)
    -----------
    image
        Image to fill
    closest_score
        The Score region closest to the camera
    return
        Segmented Image
    '''
    order = [20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]
    index = order.index(closest_score)
    image2 = image.copy()
    h,w = image2.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    # Bottom Mid to Bottom Left
    for x in range(int(w/2), 0, -1):
        if(image2[h-1,x] == 0):
            cv2.floodFill(image2, mask, (x,h-1), order[index]*12)
            index = (index + 1) % 20
    # Bottom Left to Top Left
    for y in range(h-1, 0, -1):
        if(image2[y, 0] == 0):
            cv2.floodFill(image2, mask, (0,y), order[index]*12)
            index = (index + 1) % 20
    # Top Left to Top Right
    for x in range(0, w-1):
        if(image2[0,x] == 0):
            cv2.floodFill(image2, mask, (x,0), order[index]*12)
            index = (index + 1) % 20
    # Top Right to Bottom Right
    for y in range(0, h-1):
        if(image2[y, w-1] == 0):
            cv2.floodFill(image2, mask, (w-1,y), order[index]*12)
            index = (index + 1) % 20
    # Bottom Right to Bottom Mid
    for x in range(w-1, int(w/2), -1):
        if(image2[h-1,x] == 0):
            cv2.floodFill(image2, mask, (x,h-1), order[index]*12)
            index = (index + 1) % 20
    return image2

    


def exists_line(theta, list):
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
    angle = np.round(theta/np.pi*180)
    for a in list:
        d = a - angle
        d = (d + 180) % 360 - 180
        if(abs(d) < 10):
            return True
    return False