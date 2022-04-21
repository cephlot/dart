import cv2

def generate_mask(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(image_gray,50,200,3)
    lines = None
    edges = cv2.HoughLines(100, lines, 1, 50, 150, 0, 0 ); 
    cv2.imwrite('/mnt/c/dart/pics/Test_edges.jpg', edges) 



image = cv2.imread('/mnt/c/dart/pics/pic.png') 
generate_mask(image)