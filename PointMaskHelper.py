import cv2
import numpy as np

def generate_point_mask(image, score_region, closest_score ):
    """Method to generate a point mask from one image.
    The method will generate 10 lines all with distinct angles. 
    This means that each line will segment the board according to the 
    point reagions of the board as these are the most distinguished lines.
    The image must not have lines that are more distinct than the point region lines.
    Parametres
    Every segment will be filled with a value from 1 to 20, these are NOT scores, only
    used to differentiate from each region.

    :param image: image to generate lines from 
    :type image: image
    :param score_region: scoring region
    :type score_region: matrix
    :param closest_score: the point region neares the mounted camera
    :type closest_score: int
    :return: source image with added lines
    :rtype: image
    """
    
    image_cropped = preprocess(image, score_region)
    lineImage, lines = getLines(image_cropped)
    lineImage = draw_lines(lineImage, lines)
    filledImage = fillSegments(lineImage, closest_score)
    filledImage = filledImage - lineImage
    return filledImage

def preprocess(image, score_region):
    """Preprocess the image to give better accuracy when using hughLines

    :param image: image to preprocess
    :type image: image
    :param score_region: scoring region
    :type score_region: matrix
    :return: cropped image
    :rtype: image
    """
    
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cann_img = cv2.Canny(image_gray,100,200)
    image_cropped = cv2.bitwise_and(cann_img, score_region, mask = None) 
    kernel = np.ones((10, 10), np.uint8)
    image_cropped = cv2.dilate(image_cropped, kernel)
    image_cropped = cv2.erode(image_cropped, kernel) 
    return image_cropped


def getLines(image_cropped):
    """Gets all the lines return by HughLines on the cropped image

    :param image_cropped: image to get lines from
    :type image_cropped: image
    :return: tuple of an empty image and lines
    :rtype: image, list
    """
    
    lines = cv2.HoughLines(image_cropped, 1, np.pi/180, 120, np.array([]))
    h,w = image_cropped.shape[:2]
    lineImage = np.zeros((h,w,1), dtype = "uint8")
    return lineImage, lines


def draw_lines(lineImage, lines):
    """Draws the lines on lineImage using the coordinates in lines

    :param lineImage: image to draw on
    :type lineImage: image
    :param lines: lines
    :type lines: list
    :return: image with lines
    :rtype: image
    """
    
    angle_list = []
    i = 0
    range = 10
    # index of lines in order to seperate them
    while i < range:
        line = (0,0)
        try:         
            line = lines[i]
        except Exception as exception:
            print("Not enough distinct lines for Point Mask")
            print("Exception: {}".format(type(exception).__name__))
            print("Exception message: {}".format(exception))    
            return lineImage
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
    """Helper methid that fills each segment with a unique color. Colors range 
    from 1 to 20 in greyscale (1 dimension)

    :param image: image to fill
    :type image: image
    :param closest_score: score region closest to camera
    :type closest_score: int
    :return: segmented image
    :rtype: image
    """
    
    order = [20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]
    index = order.index(closest_score)
    image2 = image.copy()
    h,w = image2.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    # Bottom Mid to Bottom Left
    for x in range(int(w/2), 0, -1):
        if(image2[h-1,x] == 0):
            cv2.floodFill(image2, mask, (x,h-1), order[index])
            index = (index + 1) % 20
    # Bottom Left to Top Left
    for y in range(h-1, 0, -1):
        if(image2[y, 0] == 0):
            cv2.floodFill(image2, mask, (0,y), order[index])
            index = (index + 1) % 20
    # Top Left to Top Right
    for x in range(0, w-1):
        if(image2[0,x] == 0):
            cv2.floodFill(image2, mask, (x,0), order[index])
            index = (index + 1) % 20
    # Top Right to Bottom Right
    for y in range(0, h-1):
        if(image2[y, w-1] == 0):
            cv2.floodFill(image2, mask, (w-1,y), order[index])
            index = (index + 1) % 20
    # Bottom Right to Bottom Mid
    for x in range(w-1, int(w/2), -1):
        if(image2[h-1,x] == 0):
            cv2.floodFill(image2, mask, (x,h-1), order[index])
            index = (index + 1) % 20
    return image2

def exists_line(theta, list):
    """Helper method that checks if the angle theta is too close to another 
    already saved angle on list

    :param theta: angle to compare
    :type theta: float
    :param list: list of angles to compare
    :type list: list
    :return: True if a line in the list is the same as theta, False otherwise
    :rtype: bool
    """
    
    angle = np.round(theta/np.pi*180)
    for a in list:
        d = a - angle
        d = (d + 180) % 360 - 180
        if(abs(d) < 10):
            return True
    return False