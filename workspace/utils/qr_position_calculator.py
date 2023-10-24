import numpy as np
from workspace.utils.qr_position import QrPosition

class QrPositionCalculator:

    IMAGE_WIDTH = 1280
    IMAGE_HEIGHT = 960
    CONSTANT = 0.8495
    QR_HEIGHT = 18

    @classmethod
    def get_qrs_positions(cls, qrs_data):
        '''
            Receives an array of qr_code_data and returns an array containing the QRs 
            position and id.

            Input: np.array
            Output: [qr_position]
            qr_position:
            {
                'id': int,
                'distance': float,
                'angle': float
            } 
        '''

        for qr_data in qrs_data:
            qr_center_relative_to_image_center = cls.__relative_to_image_center(qr_data.center)
            alpha_degrees = cls.__get_alpha_degrees(qr_center_relative_to_image_center)
            distance = cls.__get_distance(qr_data)
            qrs_data.append(QrData(qr_data.data, round(distance, 3), round(alpha_degrees, 3)))
        return qrs_data

    @classmethod
    def __relative_to_image_center(cls, point):
        return [point[0] - (cls.IMAGE_WIDTH/2), -point[1] + (cls.IMAGE_HEIGHT/2)]

    @classmethod
    def __get_alpha_degrees(cls, point):
        return np.degrees(cls.__get_alpha(point))

    @classmethod
    def __get_alpha(cls, point):
        x = point[0]
        return np.arctan(x / (cls.IMAGE_WIDTH * cls.CONSTANT))


    @classmethod
    def __get_distance(cls, qr_points):
        middle_top_relative_to_image_center = cls.__relative_to_image_center(qr_points.middle_top)
        middle_bottom_relative_to_image_center = cls.__relative_to_image_center(qr_points.middle_bottom)

        return cls.QR_HEIGHT / (np.tan(cls.__get_beta(middle_top_relative_to_image_center)) - np.tan(cls.__get_beta(middle_bottom_relative_to_image_center)))

    @classmethod
    def __get_beta(cls, point):
        x = point[0]
        y = point[1]
        return np.arctan(y / np.sqrt(np.power(cls.IMAGE_WIDTH * cls.CONSTANT, 2) + np.power(x, 2)))
