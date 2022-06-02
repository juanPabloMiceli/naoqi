import numpy as np
import cv2
from pyzbar.pyzbar import decode

images = ['qrArmario25cm.jpg', 'qrArmario120cm.jpg', 'qrArmario240cm.jpg', 'qrArmario280cm.jpg', 'qrArmarioCote.jpg', 'qrArmarioOffset.jpg', '3qrs.jpg', '2qrs.jpg', '122cm-6degrees3qrs.jpg', '174cm24degrees2qrs.jpg', '153cm-15degrees2qrs.jpg']

class QrPoints:

    def __init__(self, polygon):
        self.center = self.__get_center(polygon)
        self.top_left = self.__get_top_left(polygon)
        self.top_right = self.__get_top_right(polygon)
        self.bottom_left = self.__get_bottom_left(polygon)
        self.bottom_right = self.__get_bottom_right(polygon)
        self.middle_top = self.__get_middle_top(polygon)
        self.middle_bottom = self.__get_middle_bottom(polygon)

    def __get_center(self, polygon):
        center_x = (polygon[0].x + polygon[1].x + polygon[2].x + polygon[3].x) // 4   
        center_y = (polygon[0].y + polygon[1].y + polygon[2].y + polygon[3].y) // 4   
        return [center_x, center_y]

    def __get_middle_top(self, polygon):
        top_left = self.__get_top_left(polygon)
        top_right = self.__get_top_right(polygon)
        middle_x = (top_left[0] + top_right[0]) // 2
        middle_y = (top_left[1] + top_right[1]) // 2
        return [middle_x, middle_y]

    def __get_middle_bottom(self, polygon):
        bottom_left = self.__get_bottom_left(polygon)
        bottom_right = self.__get_bottom_right(polygon)
        middle_x = (bottom_left[0] + bottom_right[0]) // 2
        middle_y = (bottom_left[1] + bottom_right[1]) // 2
        return [middle_x, middle_y]

    def __get_top_left(self, polygon):
        return min(self.__get_tops(polygon))

    def __get_top_right(self, polygon):
        return max(self.__get_tops(polygon))

    def __get_bottom_left(self, polygon):
        return min(self.__get_bottoms(polygon))

    def __get_bottom_right(self, polygon):
        return max(self.__get_bottoms(polygon))

    def __get_tops(self, polygon):
        return sorted(polygon, key=lambda p: p[1])[:2]

    def __get_bottoms(self, polygon):
        return sorted(polygon, key=lambda p: p[1])[2:]
        
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

    @staticmethod
    def get_qrs_information(gray_image):
        '''
            Receives a grayscale image of size 1280x960 and returns the info of found qrs.

            Input: np.array
            Output: [qr_data]
            qr_data:
            {
                'id': int,
                'distance': int,
                'angle': int
            } 
        '''
        desired_shape = (QrDetector.HEIGHT, QrDetector.WIDTH)
        if gray_image.shape != desired_shape:
            print("Incorrect image shape when detecting qrs {}. Please provide an image with shape {}.".format(gray_image.shape, desired_shape))
            exit(1)
            
        binary_image = QrDetector.__binarize_image(gray_image)
        decoded_qrs = decode(binary_image)
        qrs_data = []

        for decoded_qr in decoded_qrs:
            qr_points = QrPoints(decoded_qr.polygon)
            qr_center_relative_to_image_center = QrDetector.__relative_to_image_center(qr_points.center)
            alpha_degrees = QrDetector.__get_alpha_degrees(qr_center_relative_to_image_center)
            distance = QrDetector.__get_distance(qr_points)
            qrs_data.append(QrData(int(decoded_qr.data.decode("utf-8").replace("buenas buenas", "10")), round(distance), round(alpha_degrees)))
        return qrs_data


    @staticmethod
    def find_qrs_and_show(rgb_image, save_path=""):
        binary_image = QrDetector.__binarize_image(rgb_image)
        decoded_qrs = decode(binary_image)

        for decoded_qr in decoded_qrs:
            polygon = decoded_qr.polygon
            qr_points = QrPoints(polygon)
            
            # Polygon
            rgb_image = cv2.polylines(rgb_image, np.array([polygon]), True, (255,0,0))
            # Top left corner
            rgb_image = cv2.circle(rgb_image, (qr_points.top_left[0], qr_points.top_left[1]), radius=0, color=(0, 0, 255), thickness=5)
            # Top right corner
            rgb_image = cv2.circle(rgb_image, (qr_points.top_right[0], qr_points.top_right[1]), radius=0, color=(0, 255, 0), thickness=5)
            # Bottom left corner
            rgb_image = cv2.circle(rgb_image, (qr_points.bottom_left[0], qr_points.bottom_left[1]), radius=0, color=(255, 0, 0), thickness=5)
            # Bottom right corner
            rgb_image = cv2.circle(rgb_image, (qr_points.bottom_right[0], qr_points.bottom_right[1]), radius=0, color=(255, 0, 255), thickness=5)
            # Middle of the bottom line
            rgb_image = cv2.circle(rgb_image, (qr_points.middle_bottom[0], qr_points.middle_bottom[1]), radius=0, color=(231, 0, 123), thickness=5)
            # Middle of the top line
            rgb_image = cv2.circle(rgb_image, (qr_points.middle_top[0], qr_points.middle_top[1]), radius=0, color=(123, 0, 231), thickness=5)
            # QR center
            rgb_image = cv2.circle(rgb_image, (qr_points.center[0], qr_points.center[1]), radius=0, color=(0, 255, 255), thickness=5)
            # Image center
            rgb_image = cv2.circle(rgb_image, (QrDetector.WIDTH//2, QrDetector.HEIGHT//2), radius=0, color=(255, 255, 0), thickness=5)
            
        cv2.imshow('image', rgb_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if save_path != "":
            cv2.imwrite(save_path, rgb_image)
            print("Image " + save_path + " correctly saved.")
        
    @staticmethod
    def __binarize_image(image):
        if image.ndim == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray_image = image
        blur = cv2.GaussianBlur(gray_image,(5,5),0)
        _,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        return th3

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
        rgb_image = cv2.imread("images/"+image)
        QrDetector.find_qrs_and_show(rgb_image)