# This test degrees(alpha) how to use the ALLandMarkDetection module.
# - We first instantiate a proxy to the ALLandMarkDetection module
#     Note that this module should be loaded on the robot's NAOqi.
#     The module output its results in ALMemory in a variable
#     called "LandmarkDetected"
# - We then read this AlMemory value and check whether we get
#   interesting things.
import argparse
import math
import sys
import time
from os.path import exists

import numpy as np
import qi

from customQRDetection import process_image
from naoqi import ALProxy


def disable_basic_awareness(session):
    ba_service = session.service("ALBasicAwareness")
    ba_service.stopAwareness()

def look_front():
    motion_service  = session.service("ALMotion")
    motion_service.setStiffnesses("Head", 1.0) 

    names            = "HeadYaw"
    angles           = 0
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
    names            = "HeadPitch"
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
# A un metro el nao puede detectar landmarks de 19.8cm de diametro en un cono de +-25 grados. (Ojo que 25 le cuesta)
def look_semi_right():
    motion_service  = session.service("ALMotion")
    motion_service.setStiffnesses("Head", 1.0) 

    names            = "HeadYaw"
    angles           = -math.radians(45)
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
    names            = "HeadPitch"
    angles           = 0
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)

def get_side_mult(side_str):
    if side_str == "left":
        mult = 1
    elif side_str == "right":
        mult = -1
    else:
        print("side_str must be either \"left\" or \"right\"")
        exit(1)
    return mult

def look_at(angle, side_str):
    side_mult = get_side_mult(side_str)
    motion_service  = session.service("ALMotion")
    motion_service.setStiffnesses("Head", 1.0) 

    names            = "HeadYaw"
    angles           = side_mult * math.radians(angle)
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
    names            = "HeadPitch"
    angles           = 0
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)

def get_proxy(proxyName, ip, port):
    try:
        proxy = ALProxy(proxyName, ip, port)
    except Exception as e:
        print("Error when creating "+proxyName+" proxy:")
        print(str(e))
        exit(1)
    return proxy


def main(session, args):

    # Stop basic awareness so that nao doesn't move his head when not commanded 
    disable_basic_awareness(session)

    # Look at some angle for finding the landmark
    look_at(0, "right")

    videoDeviceProxy = get_proxy("ALVideoDevice", args.ip, args.port)
    videoId = videoDeviceProxy.subscribeCamera("My_Test_Video", 0, 3, 8, 1)

    while True:
        try: 
            time.sleep(1)
            container = videoDeviceProxy.getImageRemote(videoId)

            image = map(ord, container[6])
            image_array = np.array(image, dtype=np.uint8)
            image_array = image_array.reshape(960,1280)

            print("id: " + str(container[7]))
            qrs_data = process_image(image_array)
            if len(qrs_data) > 1:
                qr1 = qrs_data[0]
                qr2 = qrs_data[1] #Cambiar los signos de angle (math.atan2(y,x))
                print("qr1: {}, qr2: {}".format(qr1, qr2))
                point_qr1 = np.array([qr1['distance'] * math.cos(math.radians(-qr1['angle'])), qr1['distance'] * math.sin(math.radians(-qr1['angle']))])
                point_qr2 = np.array([qr2['distance'] * math.cos(math.radians(-qr2['angle'])), qr2['distance'] * math.sin(math.radians(-qr2['angle']))])
                qr2_qr1_distance = np.linalg.norm(np.subtract(point_qr2, point_qr1))
                print("Dist ({})_({}) = {}".format(qr1['id'], qr2['id'], qr2_qr1_distance))
        except KeyboardInterrupt:
            videoDeviceProxy.unsubscribe("My_Test_Video")

            print("Correctly unsuscribed!")
            print("Exiting the program!")
            sys.exit(0)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.0.171",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()

    # Check there is nothing invalid in the arguments received

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, args)

# Sample cmd
# python landmark.py --ip=192.168.0.171 --port=9559 --out=data.csv --landmark_diameter=19.8 --actual_distance=30 --torso_orientation=F
