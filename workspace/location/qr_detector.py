import numpy as np
import cv2

from workspace.utils.qr_decoder import QrDecoder
from workspace.utils.logger_factory import LoggerFactory

images = ['baldoza360/intento3/original/out21.jpg']#, 'qrArmario120cm.jpg', 'qrArmario240cm.jpg', 'qrArmario280cm.jpg', 'qrArmarioCote.jpg', 'qrArmarioOffset.jpg', '3qrs.jpg', '2qrs.jpg', '122cm-6degrees3qrs.jpg', '174cm24degrees2qrs.jpg', '153cm-15degrees2qrs.jpg']

class QrData:
    
    def __init__(self, id, distance, angle):
        self.id = id
        self.distance = distance
        self.angle = angle

class QrDetector:
    CONSTANT = 0.8495
    QR_HEIGHT = 18
    WIDTH = 1280
    HEIGHT = 960

    LOGGER = LoggerFactory.get_logger("qr_detector")

    @classmethod
    def get_qrs_information(cls, gray_image):
        '''
            Receives a grayscale image of size 1280x960 and returns the info of found qrs.

            Input: np.array
            Output: [qr_data]
            qr_data:
            {
                'id': int,
                'distance': float,
                'angle': float
            } 
        '''
            
        decoded_qrs = QrDecoder.decode(gray_image)
        qrs_data = []

        for decoded_qr in decoded_qrs:
            qr_center_relative_to_image_center = QrDetector.__relative_to_image_center(decoded_qr.center)
            alpha_degrees = QrDetector.__get_alpha_degrees(qr_center_relative_to_image_center)
            distance = QrDetector.__get_distance(decoded_qr)
            qrs_data.append(QrData(decoded_qr.data, round(distance, 3), round(alpha_degrees, 3)))
        return qrs_data


    #@staticmethod
    #def find_qrs_and_show(rgb_image, save_path="", show=True):
    #    aux_image = rgb_image.copy()
        
    #    decoded_qrs = QrDecoder.decode(rgb_image)
    #    #binary_image = QrDetector.__binarize_image(rgb_image)
    #    #decoded_qrs = py_quirc.py_decode(binary_image.flatten().tolist(), 1280, 960)
    #    #decoded_qrs = decode(binary_image)

    #    for decoded_qr in decoded_qrs:
    #        # polygon = decoded_qr.polygon
    #        # qr_points = QrPoints(polygon)
            
    #        # Polygon
    #        #cv2.polylines(rgb_image, np.array([polygon]), True, (255,0,0))
    #        # Top left corner
    #        cv2.circle(rgb_image, (decoded_qr.top_left[0], decoded_qr.top_left[1]), radius=0, color=(0, 0, 255), thickness=5)
    #        # Top right corner
    #        cv2.circle(rgb_image, (decoded_qr.top_right[0], decoded_qr.top_right[1]), radius=0, color=(0, 255, 0), thickness=5)
    #        # Bottom left corner
    #        cv2.circle(rgb_image, (decoded_qr.bottom_left[0], decoded_qr.bottom_left[1]), radius=0, color=(255, 0, 0), thickness=5)
    #        # Bottom right corner
    #        cv2.circle(rgb_image, (decoded_qr.bottom_right[0], decoded_qr.bottom_right[1]), radius=0, color=(255, 0, 255), thickness=5)
    #        # Middle of the bottom line
    #        cv2.circle(rgb_image, (decoded_qr.middle_bottom[0], decoded_qr.middle_bottom[1]), radius=0, color=(231, 0, 123), thickness=5)
    #        # Middle of the top line
    #        cv2.circle(rgb_image, (decoded_qr.middle_top[0], decoded_qr.middle_top[1]), radius=0, color=(123, 0, 231), thickness=5)
    #        # QR center
    #        cv2.circle(rgb_image, (decoded_qr.center[0], decoded_qr.center[1]), radius=0, color=(0, 255, 255), thickness=5)
    #        # Image center
    #        cv2.circle(rgb_image, (QrDetector.WIDTH//2, QrDetector.HEIGHT//2), radius=0, color=(255, 255, 0), thickness=5)
        
    #    if show:
    #        cv2.imshow('image', rgb_image)
    #        cv2.waitKey(0)
    #        cv2.destroyAllWindows()

    #    if save_path != "":
    #        cv2.imwrite("out_photo.jpg", rgb_image)
    #        # cv2.imwrite(save_path, aux_image)
    #        # cv2.imwrite(save_path.replace("original", "processed"), rgb_image)
    #        QrDetector.LOGGER.info("Image " + save_path + " correctly saved.")
            
        
    @staticmethod
    def __relative_to_image_center(point):
        return [point[0] - (QrDetector.WIDTH/2), -point[1] + (QrDetector.HEIGHT/2)]

    @staticmethod
    def __get_alpha_degrees(point):
        return np.degrees(QrDetector.__get_alpha(point))

    @staticmethod
    def __get_alpha(point):
        x = point[0]
        return np.arctan(x / (QrDetector.WIDTH * QrDetector.CONSTANT))

    @staticmethod
    def __get_distance(qr_points):
        middle_top_relative_to_image_center = QrDetector.__relative_to_image_center(qr_points.middle_top)
        middle_bottom_relative_to_image_center = QrDetector.__relative_to_image_center(qr_points.middle_bottom)

        return QrDetector.QR_HEIGHT / (np.tan(QrDetector.__get_beta(middle_top_relative_to_image_center)) - np.tan(QrDetector.__get_beta(middle_bottom_relative_to_image_center)))

    @staticmethod
    def __get_beta(point):
        x = point[0]
        y = point[1]
        return np.arctan(y / np.sqrt(np.power(QrDetector.WIDTH * QrDetector.CONSTANT, 2) + np.power(x, 2)))


if __name__ == "__main__":
    for image in images:
        rgb_image = cv2.imread("my_photo.jpg")
        QrDetector.find_qrs_and_show(rgb_image, "aux", False)
