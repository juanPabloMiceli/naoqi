import math
import sys
import time
import cv2
import numpy as np
from locator_and_mapper import LocatorAndMapper
from map_display_adapter import MapDisplayAdapter
from nao_properties import NaoProperties
import qi

from awareness_controller import AwarenessController
from head_controller import HeadController
from qr_detector import QrDetector
from sonar_adapter import SonarAdapter
from video_controller import VideoController
from photo_saver import PhotoSaver

images = ['images/174cm24degrees2qrs.jpg', 'images/153cm-15degrees2qrs.jpg']

def main(session, ip, port):

    # Stop basic awareness so that nao doesn't move his head when not commanded 
    AwarenessController(session).set(False)

    # # Look front for finding qrs
    head_controller = HeadController(session)
    head_controller.look_at(0, 0)
    

    video_controller = VideoController(ip, port)
    sonar_adapter = SonarAdapter()
    map_display_adapter = MapDisplayAdapter()
    locator_and_mapper = LocatorAndMapper()
    photo_saver = PhotoSaver("images/head_angle_test/QRCenterVsImageCenter.jpg")

    index = raw_input("Insert index: ")

    while index != -1:
        # cv2_image = cv2.imread(images[index])
        # cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2GRAY)
        rgb_image = video_controller.get_current_rgb_image()
        gray_image = video_controller.get_current_gray_image()
        qrs_data = QrDetector.get_qrs_information(gray_image)
        QrDetector.find_qrs_and_show(rgb_image, photo_saver.get_save_path(), False)
        locator_and_mapper.add_information(qrs_data)
        sonar_adapter.write_data(qrs_data)
        map_display_adapter.write_data(locator_and_mapper.get_nao_location(), locator_and_mapper.qrs_data)
        time.sleep(1)
        index = raw_input("Insert index: ")


if __name__ == "__main__":
    
    IP, PORT = NaoProperties().get_connection_properties()

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, IP, PORT)
