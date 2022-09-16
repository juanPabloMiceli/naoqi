from re import L
from locator_and_mapper import LocatorAndMapper
from video_controller import VideoController
from sonar_adapter import SonarAdapter
from map_display_adapter import MapDisplayAdapter
from qr_detector import QrDetector
import numpy as np
from geometry import distance, direction
'''
Estrategia de movimiento:
    Supongamos que estamos en (Xs, Ys) y queremos ir a (Xe, Ye).

    1. Si estamos "cerca" de (Xe, Ye), terminamos, si no, ir al paso 2. 
    2. Conseguir el vector resultante de ir desde (Xs, Ys) hasta (Xe, Ye), llamemoslo 'v'.
    3. 
        * Si el angulo entre el pecho del Nao y 'v' es "chico", caminar "un poco" e ir al paso 1.
        * Si no, ir al paso 4.
    4. Girar el pecho del Nao hasta que el ángulo formado entre su cuerpo y el vector 'v' sea lo suficientemente chico.
    5. Ir al paso 1.
'''
class MovementController:

    def __init__(self, session, ip, port, sonar_enable=False, map_display_enable=False):
        self.service  = session.service("ALMotion")
        self.locator_and_mapper = LocatorAndMapper()
        self.video_controller = VideoController(ip, port)
        self.sonar_enable = sonar_enable
        self.sonar_adapter = SonarAdapter()
        self.map_display_enable = map_display_enable
        self.map_display_adapter = MapDisplayAdapter()
        self.__add_information()

    def __add_information(self):
        gray_image = self.video_controller.get_current_gray_image()
        qrs_data = QrDetector.get_qrs_information(gray_image)
        self.locator_and_mapper.add_information(qrs_data)
        self.__update_sonar_and_map_dislay(qrs_data)

    def __update_sonar_and_map_dislay(self, qrs_data):
        if self.sonar_enable:
            self.sonar_adapter.write_data(qrs_data)
        if self.map_display_enable:
            self.map_display_adapter.write_data(self.locator_and_mapper.get_nao_location(), self.locator_and_mapper.qrs_data)



    def go_to(self, target_location):
        nao_location = self.locator_and_mapper.get_nao_location()
        if self.__close_enough(nao_location, target_location):
            return True
        target_direction = direction(nao_location, target_location)

    def __close_enough(nao_location, target_location):
        return distance(nao_location, target_location) < 10

