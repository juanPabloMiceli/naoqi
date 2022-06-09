import math
import sys
import time
import cv2
import numpy as np
from locator_and_mapper import LocatorAndMapper
from nao_properties import NaoProperties
import qi

from awareness_controller import AwarenessController
from head_controller import HeadController
from qr_detector import QrDetector
from sonar_adapter import SonarAdapter
from video_controller import VideoController

images = ['images/174cm24degrees2qrs.jpg', 'images/153cm-15degrees2qrs.jpg']

def main(session, ip, port):

    # Stop basic awareness so that nao doesn't move his head when not commanded 
    # AwarenessController(session).set(False)

    # # Look front for finding qrs
    # HeadController(session).look_front()

    # video_controller = VideoController(ip, port)
    sonar_adapter = SonarAdapter()
    locator_and_mapper = LocatorAndMapper()
    index = input("Insert index: ")

    while index != -1:
        cv2_image = cv2.imread(images[index])
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2GRAY)
        # cv2_image = video_controller.get_current_image()
        qrs_data = QrDetector.get_qrs_information(cv2_image)
        sonar_adapter.write_data(qrs_data)
        locator_and_mapper.add_information(qrs_data)
        time.sleep(1)
        index = input("Insert index: ")


        # if len(qrs_data) > 1:
        #     qr1 = qrs_data[0]
        #     qr2 = qrs_data[1] #Cambiar los signos de angle (math.atan2(y,x))
        #     print("qr1: {}, qr2: {}".format(qr1, qr2))
        #     point_qr1 = np.array([qr1['distance'] * math.cos(math.radians(-qr1['angle'])), qr1['distance'] * math.sin(math.radians(-qr1['angle']))])
        #     point_qr2 = np.array([qr2['distance'] * math.cos(math.radians(-qr2['angle'])), qr2['distance'] * math.sin(math.radians(-qr2['angle']))])
        #     qr2_qr1_distance = np.linalg.norm(np.subtract(point_qr2, point_qr1))
        #     print("Dist ({})_({}) = {}".format(qr1['id'], qr2['id'], qr2_qr1_distance))


if __name__ == "__main__":
    
    IP, PORT = NaoProperties().get_connection_properties()

    #Borrar
    main(None, None, None)
    exit(0)

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, IP, PORT)
