import numpy as np
import cv2 as cv
import time

from ImageNormalizer import ImageNormalizer

def imShowScale(img, scale):
    width = int(img.shape[1] * scale / 100)
    height = int(img.shape[0] * scale / 100)
    dim = (width, height)
    
    # resize image
    return cv.resize(img, dim, interpolation = cv.INTER_AREA)

MIN_MATCH_COUNT = 1

img1 = cv.imread('images\pic_angle2.jpg')        # queryImage
img1 = ImageNormalizer.normalize_image(img1)
img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
cv.imshow("input balanced angled", imShowScale(img1,60))
cv.waitKey(0)
img2 = cv.imread('images\pic_nice.jpg')         # trainImage
img2 = ImageNormalizer.normalize_image(img2)
img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
cv.imshow("input balanced reference", imShowScale(img2,60))
cv.waitKey(0)


start_time = time.time()

# Initiate SIFT detector
sift = cv.SIFT_create(100)
# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
flann = cv.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1,des2,k=2)
# store all the good matches as per Lowe's ratio test.
good = []
for m,n in matches:
    if m.distance < 0.55*n.distance:
        good.append(m)
epic_matrix = None
print("good matches: " + str(len(good)))
if len(good)>MIN_MATCH_COUNT:
    # good = good[:10]
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    #M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
    M, mask = cv.findHomography(src_pts, dst_pts, 0)

    epic_matrix = M
    print(M)
    seconds = (time.time() - start_time) * 1000
    print("--- %s miliseconds ---" % seconds)
    matchesMask = mask.ravel().tolist()
    h,w = img1.shape
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv.perspectiveTransform(pts,M)
    img2 = cv.polylines(img2,[np.int32(dst)],True,255,3, cv.LINE_AA)
else:
    print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
    matchesMask = None
draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)



# Warp test
img1_c = cv.imread('images\pic_angle2.jpg')        # queryImage
img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
img_warped = cv.warpPerspective(img1_c,epic_matrix,img2.shape)
cv.imshow("warpedPerspective image",imShowScale(img_warped,70))   
cv.waitKey(0)
cv.imshow("DrawMatches, SIFT features",imShowScale(img3,40))
cv.waitKey(0)

# Dart hit test
def hit(img1_c, img_warped, coordinate, epic_matrix, color):
    img_hit = cv.circle(img1_c, (coordinate[0], coordinate[1]), 6, color, 2)
    coordinate = np.array([[coordinate[0], coordinate[1]]], dtype='float32')
    coordinate = np.array([coordinate])
    coordinate = cv.perspectiveTransform(coordinate, epic_matrix)
    img_hit_warped = cv.circle(img_warped, (int(coordinate[0][0][0]), int(coordinate[0][0][1])), 6, color, 2)
    return img_hit, img_hit_warped
    
pic_nice = cv.imread('images\pic_nice.jpg')        # queryImage

img_hit, pic_nice = hit(img1_c, pic_nice, (783,429,1), epic_matrix, (0,255,0))
img_hit, pic_nice = hit(img_hit, pic_nice, (430,180,1), epic_matrix, (255, 0 ,0))
img_hit, pic_nice = hit(img_hit, pic_nice, (600,300,1), epic_matrix, (0, 0 ,255))


cv.imshow("Hit on cam image",imShowScale(img_hit,50))
cv.waitKey(0)
cv.imshow("Hit on reference image",imShowScale(pic_nice,50))
cv.waitKey(0)