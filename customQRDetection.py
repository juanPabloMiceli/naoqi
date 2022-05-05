import numpy as np
import cv2
from pyzbar.pyzbar import decode
images = ['qrArmario25cm.jpg', 'qrArmario120cm.jpg', 'qrArmario240cm.jpg', 'qrArmario280cm.jpg', 'qrArmarioCote.jpg']

for image in images:
    img = cv2.imread("images/"+image,cv2.IMREAD_GRAYSCALE)
    blur = cv2.GaussianBlur(img,(5,5),0)
    ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    decoded = decode(th3)
    print(decoded)
    res = cv2.rectangle(th3, decoded[0].rect, (0, 0, 0), 2)
    # cv2.imwrite("images/out/"+image, res)