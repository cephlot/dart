import numpy as np
import cv2 as cv
import time


MIN_MATCH_COUNT = 20

img1 = cv.imread('C:\dart\images\pic_angle.png',cv.IMREAD_GRAYSCALE)        # queryImage
img2 = cv.imread('C:\dart\images\pic_nice.jpg',cv.IMREAD_GRAYSCALE)         # trainImage
start_time = time.time()

# Initiate SIFT detector
sift = cv.SIFT_create()
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
    if m.distance < 0.7*n.distance:
        good.append(m)
epic_matrix = None
print("good matches: " + str(len(good)))
if len(good)>MIN_MATCH_COUNT:
    # good = good[:10]
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
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
img1_c = cv.imread('C:\dart\images\pic_angle.png')        # queryImage
img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
img_warped = cv.warpPerspective(img1_c,epic_matrix,img2.shape)
cv.imwrite('C:\dart\images\warped.png',img_warped)   
cv.imwrite('C:\dart\images\_features.png',img3)

# Dart hit test
def hit(img1_c, img_warped, coordinate, epic_matrix, color):
    img_hit = cv.circle(img1_c, (coordinate[0], coordinate[1]), 6, color, 2)
    coordinate = np.array([[coordinate[0], coordinate[1]]], dtype='float32')
    coordinate = np.array([coordinate])
    coordinate = cv.perspectiveTransform(coordinate, epic_matrix)
    img_hit_warped = cv.circle(img_warped, (int(coordinate[0][0][0]), int(coordinate[0][0][1])), 6, color, 2)
    return img_hit, img_hit_warped
    
pic_nice = cv.imread('C:\dart\images\pic_nice.jpg')        # queryImage

img_hit, pic_nice = hit(img1_c, pic_nice, (783,429,1), epic_matrix, (0,255,0))
img_hit, pic_nice = hit(img_hit, pic_nice, (430,180,1), epic_matrix, (255, 0 ,0))
img_hit, pic_nice = hit(img_hit, pic_nice, (600,300,1), epic_matrix, (0, 0 ,255))


cv.imwrite('C:\dart\images\dart_hit_angle.png',img_hit)
cv.imwrite('C:\dart\images\pic_nice_hit.png',pic_nice)
