import numpy as np
import cv2
from pyzbar.pyzbar import decode
images = ['qrArmario25cm.jpg', 'qrArmario120cm.jpg', 'qrArmario240cm.jpg', 'qrArmario280cm.jpg', 'qrArmarioCote.jpg', 'qrArmarioOffset.jpg', '3qrs.jpg', '2qrs.jpg', '122cm-6degrees3qrs.jpg', '174cm24degrees2qrs.jpg', '153cm-15degrees2qrs.jpg']
# images = ['qrArmarioOffet.jpg', '3qrs.jpg', '2qrs.jpg']
WIDTH = 1280
HEIGHT = 960
CONSTANT = 0.8495
QR_HEIGHT = 18
SHARED_FILE = "sharedFile.csv"

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

def get_processed_image(rgb_image):
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    blur_image = cv2.GaussianBlur(gray_image,(5,5),0)
    _,th_image = cv2.threshold(blur_image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return th_image

def add_points_to_image(image, polygon):
    # Top left corner
    image = cv2.circle(image, (get_top_left(polygon)[0], get_top_left(polygon)[1]), radius=0, color=(0, 0, 255), thickness=5)
    # Top right corner
    image = cv2.circle(image, (get_top_right(polygon)[0], get_top_right(polygon)[1]), radius=0, color=(0, 255, 0), thickness=5)
    # Bottom left corner
    image = cv2.circle(image, (get_bottom_left(polygon)[0], get_bottom_left(polygon)[1]), radius=0, color=(255, 0, 0), thickness=5)
    # Bottom right corner
    image = cv2.circle(image, (get_bottom_right(polygon)[0], get_bottom_right(polygon)[1]), radius=0, color=(255, 0, 255), thickness=5)
    # Middle of the bottom line
    image = cv2.circle(image, (get_middle_bottom(polygon)[0], get_middle_bottom(polygon)[1]), radius=0, color=(231, 0, 123), thickness=5)
    # Middle of the top line
    image = cv2.circle(image, (get_middle_top(polygon)[0], get_middle_top(polygon)[1]), radius=0, color=(123, 0, 231), thickness=5)
    # QR center
    qr_center = get_qr_center(polygon)
    image = cv2.circle(image, (qr_center[0], qr_center[1]), radius=0, color=(0, 255, 255), thickness=5) # Center

    return image

def save_image_with_marked_qrs(rgb_image, name):
    processed_image = get_processed_image(rgb_image)
    decoded_qrs = decode(processed_image)
    polygons = [decoded_qr.polygon for decoded_qr in decoded_qrs]
    for polygon in polygons:
        rgb_image = add_points_to_image(rgb_image, polygon)
    cv2.imwrite(name, rgb_image)
    print("Image " + name + " correctly saved.")


def write_data(file, data):
    f = open(file, "w")
    f.write("id,distance,angle\n")
    for elem in data:
        id = elem['id']
        distance = elem['distance']
        angle = elem['angle']
        f.write("\"{}\",{},{}\n".format(id, distance, angle))
    f.close()

def process_image(image):
    '''
    Receives a grayscale image returns the info of found qrs. It also updates sharedFile.csv if you are running sonar.py.

    Input: np.array
    Output: [qr_data]
    qr_data:
    {
        'id': int,
        'distance': int,
        'angle': int
    } 
    '''
    blur = cv2.GaussianBlur(image,(5,5),0)
    _,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    decoded_qrs = decode(th3)
    qrs_data = []

    for decoded_qr in decoded_qrs:
        polygon = decoded_qr.polygon
        qr_center_relative_to_image_center = get_qr_center_relative_to_image_center(polygon)
        alpha_degrees = get_alpha_degrees(qr_center_relative_to_image_center)
        distance = get_distance(polygon)
        qrs_data.append({
                'id': int(decoded_qr.data.decode("utf-8").replace("buenas buenas", "10")),
                'distance': round(distance),
                'angle': round(alpha_degrees)
            })
    write_data(SHARED_FILE, qrs_data)
    return qrs_data


if __name__ == "__main__":
    for image in images:
        img = cv2.imread("images/"+image,cv2.IMREAD_GRAYSCALE)
        blur = cv2.GaussianBlur(img,(5,5),0)
        _,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        decoded = decode(th3)
        img2 = cv2.imread("images/"+image)
        data = []

        for decodedElem in decoded:
            
            polygon = decodedElem.polygon
            # print(f"{image=}")
            # print(f"{polygon=}")
            
            # res = cv2.rectangle(th3, (decoded[0].rect), (0, 0, 0), 2)
            qr_center_relative_to_image_center = get_qr_center_relative_to_image_center(polygon)
            qr_center = get_qr_center(polygon)
            alpha = get_alpha(qr_center_relative_to_image_center)
            alpha_degrees = get_alpha_degrees(qr_center_relative_to_image_center)
            beta = get_beta(qr_center_relative_to_image_center)
            beta_degrees = get_beta_degrees(qr_center_relative_to_image_center)
            distance = get_distance(polygon)
            

            print("top left: {}".format(get_top_left(polygon)))
            print(str(decodedElem.data))
            # print(f"{qr_center_relative_to_image_center=}, {alpha=}, {alpha_degrees=}, {beta=}, {beta_degrees=}, {distance=}")
            data.append({
                'id': decodedElem.data,
                'distance': round(distance),
                'angle': round(alpha_degrees)
            })
            image = cv2.polylines(img2, np.array([polygon]), True, (255,0,0))
            image = cv2.circle(image, (get_top_left(polygon)[0], get_top_left(polygon)[1]), radius=0, color=(0, 0, 255), thickness=5)
            image = cv2.circle(image, (get_top_right(polygon)[0], get_top_right(polygon)[1]), radius=0, color=(0, 255, 0), thickness=5)
            image = cv2.circle(image, (get_bottom_left(polygon)[0], get_bottom_left(polygon)[1]), radius=0, color=(255, 0, 0), thickness=5)
            image = cv2.circle(image, (get_bottom_right(polygon)[0], get_bottom_right(polygon)[1]), radius=0, color=(255, 0, 255), thickness=5)
            image = cv2.circle(image, (get_middle_bottom(polygon)[0], get_middle_bottom(polygon)[1]), radius=0, color=(231, 0, 123), thickness=5)
            image = cv2.circle(image, (get_middle_top(polygon)[0], get_middle_top(polygon)[1]), radius=0, color=(123, 0, 231), thickness=5)
            image = cv2.circle(image, (qr_center[0], qr_center[1]), radius=0, color=(0, 255, 255), thickness=5) # Center
            # Center of image
            image = cv2.circle(image, (WIDTH//2, HEIGHT//2), radius=0, color=(255, 255, 0), thickness=5)
        write_data(SHARED_FILE, data)
        cv2.imshow('image', image)
        cv2.waitKey(0)
        # and finally destroy/close all open windows
        cv2.destroyAllWindows()
        # cv2.imwrite("images/out/"+image, res)
