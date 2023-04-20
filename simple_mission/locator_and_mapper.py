from threading import Thread

from logging import Logger
import numpy as np
import math
from geometry import angle, pol2cart, distance, direction, transformed_point
from ..logger_factory import LoggerFactory
from ..qr_detector import QrDetector

class QrLocation:

    def __init__(self, point, id):
        self.point = point
        self.id = id

    def __str__(self):
        return "({}): [{},{}]".format(self.id, self.point[0], self.point[1])

    def __repr__(self):
        return self.__str__()

'''
LocatorAndMapper is in charge of updating the NAO location in real time.
It will run in a separate thread so as not to disturb other threads.
'''
class LocatorAndMapper(Thread):
    def __init__(self, memory, video_controller):
        super(LocatorAndMapper, self).__init__()
        self.LOGGER = LoggerFactory.get_logger("LOCATOR_MAPPER")
        self.video_controller = video_controller
        self.memory = memory
        self.already_saved_qrs_data = np.array([
            QrLocation((0, 0), 10),
            QrLocation((29, 0), 20),
            QrLocation((56, 0), 7),
            QrLocation((97.2, 10.5), 6),
            QrLocation((97.2, 56.5), 8),
            # QrLocation((97.2 - 17, 56.5 + 13.5 + 18.5), 9),
            QrLocation((93.85, 98.65), 9),
            # QrLocation((97.2 - 17, 56.5 + 13.5 + 18.5 + 22.5), 11),
            QrLocation((93.85, 121.15), 11),
            QrLocation((69.86, 156.61), 2),
            QrLocation((56.59, 171.37), 13),
            QrLocation((31.4, 188.19), 1),
            QrLocation((7.77, 192.28), 14),
            QrLocation((-26.39, 185.59), 12),
            QrLocation((-44.05, 176.16), 15),
            QrLocation((-59.67, 149.63), 16),
            QrLocation((-74.88, 128.53), 3),
            QrLocation((-79.51, 102.79), 5),
            QrLocation((-79.51, 74.79), 4),
            QrLocation((-79.51, 47.79), 17),
            QrLocation((-55.97, 21.46), 18),
            QrLocation((-36.04, 9.71), 19),
            ])

    def run(self):
        gray_nao_pov = video_controller.get_current_gray_pov()
        qrs_data = QrDetector.get_qrs_information(gray_nao_pov)
        self._add_information(qrs_data)

    '''
    Input: qrs_data of the current frame
    Adds the new qrs (if any) to the already saved qrs and writes to memory the
    new NAO location based on the current qrs data.
    '''
    def _add_information(self, new_qrs_data):
            self.LOGGER.info("NAO saw {} QRs".format(len(new_qrs_data)))
        if len(new_qrs_data) < 2:
            return

        if len(self.already_saved_qrs_data) == 0:
            # Procedimiento inicial
            qr1 = new_qrs_data[0]
            qr2 = new_qrs_data[1]

            self.LOGGER.info("Starting first step of location, chose qrs {} and {}".format(qr1.id, qr2.id))

            point_qr1 = pol2cart(qr1.distance, math.radians(-qr1.angle))
            point_qr2 = pol2cart(qr2.distance, math.radians(-qr2.angle))

            qr2_qr1_distance = distance(point_qr1, point_qr2)
            self._add_qr_to_map(np.array([0,0]), qr1.id)
            self._add_qr_to_map(np.array([round(qr2_qr1_distance, 3),0]), qr2.id)

        # Procedimiento general
        known_qrs_indices = self._get_known_qrs_indices(new_qrs_data)
        self.LOGGER.info(len(known_qrs_indices))
        if len(known_qrs_indices) == 2:
            new_nao_location = self._compute_nao_location(known_qrs_indices, new_qrs_data)
            self._set_nao_location(new_nao_location)
            # TODO: Compute and save NAO direction
            self._add_new_qrs(new_qrs_data, known_qrs_indices)

    def origin_position(self):
        return transformed_point(np.zeros(2), self.map_axis_zero, self.angle_between_coordinates)

    def _get_nao_location(self):
        return self.memory.get_nao_location()

    def _set_nao_location(self, new_location):
        self.memory.set_nao_location(new_location)

    def _compute_nao_location(self, known_qrs_indices, new_qrs_data):
        qr1 = new_qrs_data[known_qrs_indices[0]]
        qr2 = new_qrs_data[known_qrs_indices[1]]

        self.LOGGER.info("Getting Nao location, chose qrs {} and {}".format(qr1.id, qr2.id))

        for qr_data in self.already_saved_qrs_data:
            if qr_data.id == qr1.id:
                point_qr1_map = qr_data.point
            if qr_data.id == qr2.id:
                point_qr2_map = qr_data.point

        point_qr1_torso = pol2cart(qr1.distance, math.radians(-qr1.angle))
        point_qr2_torso = pol2cart(qr2.distance, math.radians(-qr2.angle))

        qr2_qr1_torso = direction(point_qr1_torso, point_qr2_torso) 
        qr2_qr1_map = direction(point_qr1_map, point_qr2_map)

        qr2_qr1_angle_torso = angle(qr2_qr1_torso)
        qr2_qr1_angle_map = angle(qr2_qr1_map)

        qr1_nao_map_length = qr1.distance
        qr1_nao_map_angle = qr2_qr1_angle_map - qr2_qr1_angle_torso + np.radians(-qr1.angle)

        qr1_nao_map = pol2cart(qr1_nao_map_length, qr1_nao_map_angle)

        nao_location = np.subtract(point_qr1_map, qr1_nao_map) 
        nao_location = np.vectorize(lambda n: round(n, 3))(nao_location)
        self.LOGGER.info("Nao location: {}".format(nao_location))

        return nao_location

    def _add_qr_to_map(self, point, id):
        self.already_saved_qrs_data = np.append(self.already_saved_qrs_data, QrLocation(point, id))

    def _get_known_qrs_indices(self, new_qrs_data):
        known_qrs = []

        for index, new_qr_data in enumerate(new_qrs_data):
            for qr_data in self.already_saved_qrs_data:
                if new_qr_data.id == qr_data.id:
                    known_qrs.append(index)

        return np.array(known_qrs)[:2] # I am only interested in the first two for localization and mapping

    def _get_new_qrs_indices(self, new_qrs_data):
        new_qrs = []

        for index, new_qr_data in enumerate(new_qrs_data):
            is_new = True
            for qr_data in self.already_saved_qrs_data:
                if new_qr_data.id == qr_data.id:
                    is_new = False
                    break
            if is_new:
                new_qrs.append(index)

        return np.array(new_qrs)

    def _add_new_qrs(self, new_qrs_data, known_qrs_indices):
        new_qrs_indices = self._get_new_qrs_indices(new_qrs_data)

        qr1 = new_qrs_data[known_qrs_indices[0]]
        qr2 = new_qrs_data[known_qrs_indices[1]]

        for qr_data in self.already_saved_qrs_data:
            if qr_data.id == qr1.id:
                point_qr1_map = qr_data.point
            if qr_data.id == qr2.id:
                point_qr2_map = qr_data.point

        for new_qr_index in new_qrs_indices:
            new_qr_data = new_qrs_data[new_qr_index]

            point_qr1_torso = pol2cart(qr1.distance, math.radians(-qr1.angle))
            point_qr2_torso = pol2cart(qr2.distance, math.radians(-qr2.angle))

            qr2_qr1_torso = direction(point_qr1_torso, point_qr2_torso)
            qr2_qr1_map = direction(point_qr1_map, point_qr2_map)

            qr2_qr1_angle_torso = angle(qr2_qr1_torso)
            qr2_qr1_angle_map = angle(qr2_qr1_map)

            new_qr_nao_map_length = new_qr_data.distance
            new_qr_nao_map_angle = np.radians(-new_qr_data.angle) - qr2_qr1_angle_torso + qr2_qr1_angle_map
            new_qr_nao = pol2cart(new_qr_nao_map_length, new_qr_nao_map_angle)
            new_qr = np.add(self._get_nao_location(), new_qr_nao)
            new_qr = np.vectorize(lambda n: round(n, 3))(new_qr)
            self._add_qr_to_map(new_qr, new_qr_data.id)



