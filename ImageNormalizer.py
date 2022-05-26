import cv2
import numpy as np

class ImageNormalizer:
    @staticmethod
    def green_color_mask(img):
        """Creates a green color mask

        :param img: image to create mask of
        :type img: image
        :return: green color mask
        :rtype: image
        """        

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
        res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, kernelBIG)
        kernelSMALL = np.ones((3,3))
        res = cv2.erode(res, kernelSMALL)
        res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernelSMALL)

        return res

    @staticmethod
    def red_color_mask(img):
        """Creates a red color mask

        :param img: image to create mask of
        :type img: image
        :return: red color mask
        :rtype: image
        """        

        #convert the BGR image to HSV colour space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #set the lower and upper bounds for the green hue
        lower_red = np.array([1, 100, 100])
        upper_red = np.array([5, 255, 255])

        #create a mask for green colour using inRange function
        mask = cv2.inRange(hsv, lower_red, upper_red)

        #perform bitwise and on the original image arrays using the mask
        res = cv2.bitwise_and(img, img, mask=mask)

        kernelBIG = np.ones((8,8)) 
        res = cv2.dilate(res, kernelBIG)
        res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, kernelBIG)
        kernelSMALL = np.ones((3,3))
        res = cv2.erode(res, kernelSMALL)
        res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernelSMALL)

        cv2.imshow('RED', res)

        return res


    @staticmethod
    def image_colorfulness(image, sigma):
        """Change the saturation of the image

        :param image: image to manipulate
        :type image: image
        :param sigma: saturation factor
        :type sigma: float
        :return: saturated image
        :rtype: image
        """

        hsvImg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

        #multiple by a factor to change the saturation
        hsvImg[...,1] = hsvImg[...,1]*sigma

        return cv2.cvtColor(hsvImg,cv2.COLOR_HSV2BGR)

    @staticmethod
    def normalize_image(img):
        """Normalizes the image

        :param img: image to normalize
        :type img: image
        :return: normalized image
        :rtype: image
        """

        white_balance_corrected = ImageNormalizer.white_balance(img)
        return ImageNormalizer.normalize_brightness(white_balance_corrected)

    @staticmethod
    def normalize_image_spec_green(img, sigma):
        """Normalizes image w.r.t. gren

        :param img: image to normalize
        :type img: image
        :param sigma: saturation factor
        :type sigma: float
        :return: green-normalized image
        :rtype: image
        """

        white_balance_corrected = ImageNormalizer.white_balance(img)
        normal_brightness = ImageNormalizer.normalize_brightness(white_balance_corrected)
        img_green = ImageNormalizer.green_color_mask(white_balance_corrected)
        img_green = ImageNormalizer.image_colorfulness(img_green, sigma)
        
        ret = cv2.add(img_green, normal_brightness)
        return ret
    
    @staticmethod
    def normalize_image_spec_red(img, sigma):
        """Normalizes image w.r.t. red

        :param img: image to normalize
        :type img: image
        :param sigma: saturation factor
        :type sigma: float
        :return: red-normalized image
        :rtype: image
        """

        white_balance_corrected = ImageNormalizer.white_balance(img)
        normal_brightness = ImageNormalizer.normalize_brightness(white_balance_corrected)
        img_red = ImageNormalizer.red_color_mask(white_balance_corrected)
        img_red = ImageNormalizer.image_colorfulness(img_red, sigma)
        
        ret = cv2.add(img_red, normal_brightness)
        return ret

    @staticmethod
    def white_balance(img):
        """Automatically normalizes the white balance of the image

        :param img: image to normalize
        :type img: image
        :return: white-balanced image
        :rtype: image
        """

        # https://stackoverflow.com/questions/46390779/automatic-white-balancing-with-grayworld-assumption
        result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.3)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.3)
        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result

    @staticmethod
    def clahe_EQ(img):

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        result = clahe.apply(v)

        hsv = cv2.merge((h,s,result))
        res = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return res


    @staticmethod
    def normalize_brightness(img):
        """Normalizes the brightness of the image

        :param img: image to normalize
        :type img: image
        :return: brightness-normalized image
        :rtype: image
        """

        # https://linuxtut.com/en/9c9fc6c0e9e8a9d05800/
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)

        v = v-np.mean(v) + 128
        v = np.clip(v,0,255)
        result = np.array(v, dtype=np.uint8)

        hsv = cv2.merge((h,s,result))
        res = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return res
