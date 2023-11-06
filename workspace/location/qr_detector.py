import numpy as np

from workspace.utils.qr_decoder import QrDecoder
from workspace.utils.logger_factory import LoggerFactory
from workspace.utils.qr_position_data import QrPositionData

class QrDetector:
    '''
    QrDetector transforms a grayscale image into an array of qrs position in space (distance and angle from the camera and what data do they hold)
    '''
    CAMERA_CONSTANT = 0.8495
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
            qrs_data.append(QrPositionData(decoded_qr.data, round(distance, 3), round(alpha_degrees, 3)))
        return qrs_data

        
    @staticmethod
    def __relative_to_image_center(point):
        return [point[0] - (QrDetector.WIDTH/2), -point[1] + (QrDetector.HEIGHT/2)]

    @staticmethod
    def __get_alpha_degrees(point):
        return np.degrees(QrDetector.__get_alpha(point))

    @staticmethod
    def __get_alpha(point):
        x = point[0]
        return np.arctan(x / (QrDetector.WIDTH * QrDetector.CAMERA_CONSTANT))

    @staticmethod
    def __get_distance(qr_points):
        middle_top_relative_to_image_center = QrDetector.__relative_to_image_center(qr_points.middle_top)
        middle_bottom_relative_to_image_center = QrDetector.__relative_to_image_center(qr_points.middle_bottom)

        return QrDetector.QR_HEIGHT / (np.tan(QrDetector.__get_beta(middle_top_relative_to_image_center)) - np.tan(QrDetector.__get_beta(middle_bottom_relative_to_image_center)))

    @staticmethod
    def __get_beta(point):
        x = point[0]
        y = point[1]
        return np.arctan(y / np.sqrt(np.power(QrDetector.WIDTH * QrDetector.CAMERA_CONSTANT, 2) + np.power(x, 2)))