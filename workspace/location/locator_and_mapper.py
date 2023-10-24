from threading import Thread

import time
import json
import numpy as np
import math
from workspace.utils.geometry import angle, pol2cart, distance, direction, transformed_point
from workspace.utils.logger_factory import LoggerFactory
from workspace.location.qr_detector import QrDetector

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: {}, y: {}".format(self.x, self.y)

    def __repr__(self):
        return self.__str__()

class QrPosition:
    def __init__(self, id, position):
        self.id = id
        self.position = position

    def __str__(self):
        return "({}): {}".format(self.id, self.position)

    def __repr__(self):
        return self.__str__()


'''
LocatorAndMapper is in charge of updating the NAO location in real time.
It will run in a separate thread so as not to disturb other threads.
'''
class LocatorAndMapper(Thread):
    def __init__(self, memory, nao, positions_json=None):
        super(LocatorAndMapper, self).__init__()
        self.LOGGER = LoggerFactory.get_logger("LOCATOR_MAPPER")
        self.memory = memory
        self.nao = nao
        self.positions = np.array([])
        if positions_json != None:
            self.positions = self._load_json(positions_json)

    def run(self):
        while True:
            start = time.time()
            gray_nao_pov = self.video_controller.get_current_gray_pov()
            stop = time.time()
            self.LOGGER.info("get current gray pov took {} seconds".format(stop - start))
            start = time.time()
            qrs_data = QrDetector.get_qrs_information(gray_nao_pov)
            stop = time.time()
            self.LOGGER.info("get qrs information took {} seconds".format(stop - start))
            start = time.time()
            self._add_information(qrs_data)
            stop = time.time()
            self.LOGGER.info("Add information took {} seconds".format(stop - start))

    '''
    Input: qrs_data of the current frame
    Adds the new qrs (if any) to the already saved qrs and writes to memory the
    new NAO location based on the current qrs data.
    '''
    def _add_information(self, new_qrs_data):
        if len(new_qrs_data) < 2:
            self.LOGGER.info("I could not found 2 QRs, found {} :(".format(len(new_qrs_data)))
            return

        if len(self.positions) == 0:
            # Procedimiento inicial
            qr1 = new_qrs_data[0]
            qr2 = new_qrs_data[1]

            self.LOGGER.info("Starting first step of location, chose qrs {} and {}".format(qr1.id, qr2.id))

            point_qr1 = pol2cart(qr1.distance, math.radians(-qr1.angle))
            point_qr2 = pol2cart(qr2.distance, math.radians(-qr2.angle))

            qr2_qr1_distance = distance(point_qr1, point_qr2)
            self._add_qr_to_map(qr1.id, Position(0,0))
            self._add_qr_to_map(qr2.id, Position(round(qr2_qr1_distance, 3), 0))

        # Procedimiento general
        known_qrs_indices = self._get_known_qrs_indices(new_qrs_data)
        if len(known_qrs_indices) == 2:
            nao_position, nao_direction = self._compute_nao_position(known_qrs_indices, new_qrs_data)
            self.LOGGER.info("New position: {}\nNew direction: {}".format(nao_position, nao_direction))
            self._set_nao_position(nao_position)
            self._set_nao_direction(nao_direction)
            self._add_new_qrs(new_qrs_data, known_qrs_indices, nao_position)


    def origin_position(self):
        return transformed_point(np.zeros(2), self.map_axis_zero, self.angle_between_coordinates)

    def _set_nao_direction(self, new_direction):
        self.memory.set_nao_direction(new_direction)

    def _set_nao_position(self, new_position):
        self.memory.set_nao_position(new_position)

    def _compute_nao_position(self, known_qrs_indices, new_qrs_data):
        qr1 = new_qrs_data[known_qrs_indices[0]]
        qr2 = new_qrs_data[known_qrs_indices[1]]

        self.LOGGER.info("Getting Nao location, chose qrs {} and {}".format(qr1.id, qr2.id))

        for qr_data in self.positions:
            if qr_data.id == qr1.id:
                qr1_position_in_map = np.array([qr_data.position.x, qr_data.position.y])
            if qr_data.id == qr2.id:
                qr2_position_in_map = np.array([qr_data.position.x, qr_data.position.y])

        qr1_position_from_torso = pol2cart(qr1.distance, math.radians(-qr1.angle))
        qr2_position_from_torso = pol2cart(qr2.distance, math.radians(-qr2.angle))

        qr2_qr1_torso = direction(qr1_position_from_torso, qr2_position_from_torso)
        qr2_qr1_map = direction(qr1_position_in_map, qr2_position_in_map)

        qr2_qr1_angle_torso = angle(qr2_qr1_torso) # alpha12
        qr2_qr1_angle_map = angle(qr2_qr1_map) # gamma12
        
        nao_direction = qr2_qr1_angle_map - qr2_qr1_angle_torso
        qr1_nao_map_angle = nao_direction + np.radians(-qr1.angle)

        qr1_nao_map_length = qr1.distance
        qr1_nao_map = pol2cart(qr1_nao_map_length, qr1_nao_map_angle)

        nao_position = np.subtract(qr1_position_in_map, qr1_nao_map) 
        nao_position = np.vectorize(lambda n: round(n, 3))(nao_position)
        self.LOGGER.info("Nao location: {}".format(nao_position))

        return nao_position, nao_direction

    def _add_qr_to_map(self, id, position):
        self.positions = np.append(self.positions, QrPosition(position, id))

    def _get_known_qrs_indices(self, new_qrs_data):
        known_qrs_indices = []

        for index, new_qr_data in enumerate(new_qrs_data):
            for qr_position in self.positions:
                if new_qr_data.id == qr_position.id:
                    known_qrs_indices.append(index)

        return np.array(known_qrs_indices)[:2] # I am only interested in the first two for localization and mapping

    def _get_new_qrs_indices(self, new_qrs_data):
        new_qrs_indices = []

        for index, new_qr_data in enumerate(new_qrs_data):
            is_new = True
            for qr_position in self.positions:
                if new_qr_data.id == qr_position.id:
                    is_new = False
                    break
            if is_new:
                new_qrs_indices.append(index)

        return np.array(new_qrs_indices)

    def _add_new_qrs(self, new_qrs_data, known_qrs_indices, nao_position):
        new_qrs_indices = self._get_new_qrs_indices(new_qrs_data)

        qr1 = new_qrs_data[known_qrs_indices[0]]
        qr2 = new_qrs_data[known_qrs_indices[1]]

        for qr_position in self.positions:
            if qr_position.id == qr1.id:
                point_qr1_map = qr_position.position
            if qr_position.id == qr2.id:
                point_qr2_map = qr_position.position

        for new_qr_index in new_qrs_indices:
            new_qr_data = new_qrs_data[new_qr_index]

            qr1_position_from_torso = pol2cart(qr1.distance, math.radians(-qr1.angle))
            qr2_position_from_torso = pol2cart(qr2.distance, math.radians(-qr2.angle))

            qr2_qr1_torso = direction(qr1_position_from_torso, qr2_position_from_torso)
            qr2_qr1_map = direction(point_qr1_map, point_qr2_map)

            qr2_qr1_angle_torso = angle(qr2_qr1_torso)
            qr2_qr1_angle_map = angle(qr2_qr1_map)

            new_qr_nao_map_length = new_qr_data.distance
            new_qr_nao_map_angle = np.radians(-new_qr_data.angle) - qr2_qr1_angle_torso + qr2_qr1_angle_map
            new_qr_nao = pol2cart(new_qr_nao_map_length, new_qr_nao_map_angle)
            new_qr_position = np.add(nao_position, new_qr_nao)
            new_qr_position = np.vectorize(lambda n: round(n, 3))(new_qr_position)
            self._add_qr_to_map(new_qr_data.id, Position(new_qr_position[0], new_qr_position[1]))

    # def _get_nao_direction(self, known_qrs_indices, new_qrs_data):

    def _load_json(self, positions_json):
        positions = np.array([])
        with open(positions_json, 'r') as json_file:
            positions_dict = json.load(json_file)
        for position_dict in positions_dict:
            id = position_dict['id']
            position = position_dict['position']
            positions = np.append(positions, QrPosition(id, Position(position['x'], position['y'])))
        
        return positions
