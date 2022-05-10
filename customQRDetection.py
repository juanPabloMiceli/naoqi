import numpy as np
import cv2
from pyzbar.pyzbar import decode
images = ['qrArmario25cm.jpg', 'qrArmario120cm.jpg', 'qrArmario240cm.jpg', 'qrArmario280cm.jpg', 'qrArmarioCote.jpg']
WIDTH = 1280
HEIGHT = 960
CONSTANT = 0.8495
QR_HEIGHT = 18

def get_distance(polygon):
    middle_top = get_middle_top(polygon)
    middle_top_relative_to_image_center = relative_to_image_center(middle_top)
    middle_bottom = get_middle_bottom(polygon)
    middle_bottom_relative_to_image_center = relative_to_image_center(middle_bottom)

    return QR_HEIGHT / (np.tan(get_beta(middle_top_relative_to_image_center)) - np.tan(get_beta(middle_bottom_relative_to_image_center)))

def relative_to_image_center(point):
    return [point[0] - (WIDTH/2), -point[1] + (HEIGHT/2)]

def get_middle_top(polygon):
    top_left = get_top_left(polygon)
    top_right = get_top_right(polygon)
    middle_x = (top_left[0] + top_right[0]) // 2
    middle_y = (top_left[1] + top_right[1]) // 2
    return [middle_x, middle_y]

def get_middle_bottom(polygon):
    bottom_left = get_bottom_left(polygon)
    bottom_right = get_bottom_right(polygon)
    middle_x = (bottom_left[0] + bottom_right[0]) // 2
    middle_y = (bottom_left[1] + bottom_right[1]) // 2
    return [middle_x, middle_y]

def get_tops(polygon):
    return sorted(polygon, key=lambda p: p[1])[:2]


def get_top_left(polygon):
    return min(get_tops(polygon))

def get_top_right(polygon):
    return max(get_tops(polygon))

def get_bottoms(polygon):
    return sorted(polygon, key=lambda p: p[1])[2:]


def get_bottom_left(polygon):
    return min(get_bottoms(polygon))

def get_bottom_right(polygon):
    return max(get_bottoms(polygon))

def get_qr_center(polygon):
    center_x = (polygon[0].x + polygon[1].x + polygon[2].x + polygon[3].x) // 4   
    center_y = (polygon[0].y + polygon[1].y + polygon[2].y + polygon[3].y) // 4   
    return [center_x, center_y]

def get_qr_center_relative_to_image_center(polygon):
    center = get_qr_center(polygon) 
    return [center[0] - (WIDTH/2), -center[1] + (HEIGHT/2)]

def get_alpha(point):
    x = point[0]
    return np.arctan(x / (WIDTH * CONSTANT))

def get_alpha_degrees(point):
    return np.degrees(get_alpha(point))

def get_beta(point):
    x = point[0]
    y = point[1]
    return np.arctan(y / np.sqrt(np.power(WIDTH * CONSTANT, 2) + np.power(x, 2)))

def get_beta_degrees(point):
    return np.degrees(get_beta(point))

for image in images:
    img = cv2.imread("images/"+image,cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread("images/"+image)
    blur = cv2.GaussianBlur(img,(5,5),0)
    ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    decoded = decode(th3)
    polygon = decoded[0].polygon
    print(f"{image=}")
    print(f"{polygon=}")
    res = cv2.rectangle(th3, decoded[0].rect, (0, 0, 0), 2)
    qr_center_relative_to_image_center = get_qr_center_relative_to_image_center(polygon)
    qr_center = get_qr_center(polygon)
    alpha = get_alpha(qr_center_relative_to_image_center)
    alpha_degrees = get_alpha_degrees(qr_center_relative_to_image_center)
    beta = get_beta(qr_center_relative_to_image_center)
    beta_degrees = get_beta_degrees(qr_center_relative_to_image_center)
    distance = get_distance(polygon)
    

    print(f"{get_top_left(polygon)=}")
    print(f"{qr_center_relative_to_image_center=}, {alpha=}, {alpha_degrees=}, {beta=}, {beta_degrees=}, {distance=}")
    image = cv2.circle(img2, (get_top_left(polygon)[0], get_top_left(polygon)[1]), radius=0, color=(0, 0, 255), thickness=5)
    image = cv2.circle(image, (get_top_right(polygon)[0], get_top_right(polygon)[1]), radius=0, color=(0, 255, 0), thickness=5)
    image = cv2.circle(image, (get_bottom_left(polygon)[0], get_bottom_left(polygon)[1]), radius=0, color=(255, 0, 0), thickness=5)
    image = cv2.circle(image, (get_bottom_right(polygon)[0], get_bottom_right(polygon)[1]), radius=0, color=(255, 0, 255), thickness=5)
    image = cv2.circle(image, (get_middle_bottom(polygon)[0], get_middle_bottom(polygon)[1]), radius=0, color=(231, 0, 123), thickness=5)
    image = cv2.circle(image, (get_middle_top(polygon)[0], get_middle_top(polygon)[1]), radius=0, color=(123, 0, 231), thickness=5)
    image = cv2.circle(image, (qr_center[0], qr_center[1]), radius=0, color=(0, 255, 255), thickness=5) # Center
    # Center of image
    image = cv2.circle(image, (WIDTH//2, HEIGHT//2), radius=0, color=(255, 255, 0), thickness=5)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    # and finally destroy/close all open windows
    cv2.destroyAllWindows()
    # cv2.imwrite("images/out/"+image, res)
