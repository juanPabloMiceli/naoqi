import os
import sys
import time
from naoqi import ALProxy

IP = "192.168.0.171"
PORT = 9559

try:
    photoCaptureProxy = ALProxy("ALPhotoCapture", IP, PORT)
except Exception as e:
    print("Error when creating ALPhotoCapture proxy")
    print(str(e))
    exit(1)

''' Resolution table
|   8   |  40x30px  |
---------------------
|   7   |  80x60px  |
---------------------
|   0   | 160x120px |
---------------------
|   1   | 320x240px |
---------------------
|   2   | 640x480px |
---------------------
|   3   |1280x960px |
'''

photoCaptureProxy.setResolution(3)
photoCaptureProxy.setPictureFormat("jpg")
photoCaptureProxy.takePictures(1, "/home/nao/pictures/", "naomark")
