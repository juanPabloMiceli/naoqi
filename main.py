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
from nao_properties import NaoProperties
import qi

from awareness_controller import AwarenessController
from head_controller import HeadController
from qr_detector import QrDetector
from sonar_adapter import SonarAdapter
from video_controller import VideoController

def main(session, ip, port):

    # Stop basic awareness so that nao doesn't move his head when not commanded 
    AwarenessController(session).set(False)

    # Look front for finding qrs
    HeadController(session).look_front()

    video_controller = VideoController(ip, port)
    sonar_adapter = SonarAdapter()

    while True:
        time.sleep(1)
        cv2_image = video_controller.get_current_image()
        qrs_data = QrDetector.get_qrs_information(cv2_image)
        sonar_adapter.write_data(qrs_data)

        if len(qrs_data) > 1:
            qr1 = qrs_data[0]
            qr2 = qrs_data[1] #Cambiar los signos de angle (math.atan2(y,x))
            print("qr1: {}, qr2: {}".format(qr1, qr2))
            point_qr1 = np.array([qr1['distance'] * math.cos(math.radians(-qr1['angle'])), qr1['distance'] * math.sin(math.radians(-qr1['angle']))])
            point_qr2 = np.array([qr2['distance'] * math.cos(math.radians(-qr2['angle'])), qr2['distance'] * math.sin(math.radians(-qr2['angle']))])
            qr2_qr1_distance = np.linalg.norm(np.subtract(point_qr2, point_qr1))
            print("Dist ({})_({}) = {}".format(qr1['id'], qr2['id'], qr2_qr1_distance))


if __name__ == "__main__":
    
    IP, PORT = NaoProperties.get_connection_properties()

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, IP, PORT)
