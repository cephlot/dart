import cv2
import numpy as np

class ImageNormalizer:
    @staticmethod
    def normalize_image(img):
        white_balance_corrected = ImageNormalizer.white_balance(img)
        return ImageNormalizer.normalize_brightness(white_balance_corrected)

    @staticmethod
    def white_balance(img):
        # https://stackoverflow.com/questions/46390779/automatic-white-balancing-with-grayworld-assumption
        result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
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

        hsv = cv2.merge((h,s,result))
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
