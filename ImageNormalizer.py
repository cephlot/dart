import cv2
import numpy as np

class ImageNormalizer:
    @staticmethod
    def green_color_mask(img):
        #convert the BGR image to HSV colour space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #set the lower and upper bounds for the green hue
        lower_green = np.array([50,80,50])
        upper_green = np.array([80,255,255])

        #create a mask for green colour using inRange function
        mask = cv2.inRange(hsv, lower_green, upper_green)

        #perform bitwise and on the original image arrays using the mask
        res = cv2.bitwise_and(img, img, mask=mask)

        kernelBIG = np.ones((6,6)) 
        res = cv2.dilate(res, kernelBIG)
        res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, (20, 20))
        kernelSMALL = np.ones((3,3))
        res = cv2.erode(res, kernelSMALL)

        return res

    @staticmethod
    def image_colorfulness(image, sigma):
        hsvImg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

        #multiple by a factor to change the saturation
        hsvImg[...,1] = hsvImg[...,1]*sigma

        return cv2.cvtColor(hsvImg,cv2.COLOR_HSV2BGR)

    @staticmethod
    def normalize_image(img):
        white_balance_corrected = ImageNormalizer.white_balance(img)
        return ImageNormalizer.normalize_brightness(white_balance_corrected)

    @staticmethod
    def normalize_image_spec_green(img):
        white_balance_corrected = ImageNormalizer.white_balance(img)
        normal_brightness = ImageNormalizer.normalize_brightness(white_balance_corrected)
        img_green = ImageNormalizer.green_color_mask(white_balance_corrected)
        img_green = ImageNormalizer.image_colorfulness(img_green, 1.5)
        
        ret = cv2.add(img_green, normal_brightness)
        return ret


    @staticmethod
    def white_balance(img):
        # https://stackoverflow.com/questions/46390779/automatic-white-balancing-with-grayworld-assumption
        result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.3)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.3)
        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result

    @staticmethod
    def normalize_brightness(img):
        # https://linuxtut.com/en/9c9fc6c0e9e8a9d05800/
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)

        v = v-np.mean(v) + 128
        v = np.clip(v,0,255)
        result = np.array(v, dtype=np.uint8)
        
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # result = clahe.apply(result)

        hsv = cv2.merge((h,s,result))
        res = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return res
