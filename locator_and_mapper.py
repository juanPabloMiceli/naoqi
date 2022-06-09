from logging import Logger
import numpy as np
import math
from geometry import angle, angle_between_vectors, pol2cart, distance, direction, transformed_point
from logger_factory import LoggerFactory

class QrLocation:

    def __init__(self, point, id):
        self.point = point
        self.id = id

    def __str__(self):
        return "({}): [{},{}]".format(self.id, self.point[0], self.point[1])

    def __repr__(self):
        return self.__str__()

class LocatorAndMapper:

    qrs_data = np.array([])
    LOGGER = LoggerFactory.get_logger("LOGGER")
    nao_location = None

    def add_information(self, new_qrs_data):
        if len(new_qrs_data) < 2:
            return

        if len(self.qrs_data) == 0:
            # Procedimiento inicial
            qr1 = new_qrs_data[0]
            qr2 = new_qrs_data[1]
 
            self.LOGGER.info("Starting first step of location, chose qrs {} and {}".format(qr1.id, qr2.id))
            
            point_qr1 = pol2cart(qr1.distance, math.radians(-qr1.angle))
            point_qr2 = pol2cart(qr2.distance, math.radians(-qr2.angle))

            qr2_qr1_distance = distance(point_qr1, point_qr2)
            self.__add_qr_to_map(np.array([0,0]), qr1.id)
            self.__add_qr_to_map(np.array([round(qr2_qr1_distance, 3),0]), qr2.id)
            
        # Procedimiento general
        known_qrs_indices = self.__get_known_qrs_indices(new_qrs_data)
        if len(known_qrs_indices) == 2:
            self.nao_location = self.__get_nao_location(known_qrs_indices, new_qrs_data)
            self.__add_new_qrs(new_qrs_data, known_qrs_indices)
    
        return self.get_nao_location()

    def get_nao_location(self):
        return self.nao_location

    def origin_position(self):
        return transformed_point(np.zeros(2), self.map_axis_zero, self.angle_between_coordinates)

    def __get_nao_location(self, known_qrs_indices, new_qrs_data):
        qr1 = new_qrs_data[known_qrs_indices[0]]
        qr2 = new_qrs_data[known_qrs_indices[1]]

        self.LOGGER.info("Getting Nao location, chose qrs {} and {}".format(qr1.id, qr2.id))

        for qr_data in self.qrs_data:
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
        nao_location[0] = round(nao_location[0], )
        self.LOGGER.info("Nao location: {}".format(nao_location))

        return nao_location

    def __add_qr_to_map(self, point, id):
        self.qrs_data = np.append(self.qrs_data, QrLocation(point, id))

    def __get_known_qrs_indices(self, new_qrs_data):
        known_qrs = []

        for index, new_qr_data in enumerate(new_qrs_data):
            for qr_data in self.qrs_data:
                if new_qr_data.id == qr_data.id:
                    known_qrs.append(index)
        
        return np.array(known_qrs)[:2] # I am only interested in the first two for localization and mapping
    
    def __get_new_qrs_indices(self, new_qrs_data):
        new_qrs = []

        for index, new_qr_data in enumerate(new_qrs_data):
            is_new = True
            for qr_data in self.qrs_data:
                if new_qr_data.id == qr_data.id:
                    is_new = False
                    break
            if is_new:
                new_qrs.append(index)
        
        return np.array(new_qrs)

    def __add_new_qrs(self, new_qrs_data, known_qrs_indices):
        new_qrs_indices = self.__get_new_qrs_indices(new_qrs_data)

        qr1 = new_qrs_data[known_qrs_indices[0]]
        qr2 = new_qrs_data[known_qrs_indices[1]]

        for qr_data in self.qrs_data:
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
            new_qr = np.add(self.nao_location, new_qr_nao)
            new_qr = np.vectorize(lambda n: round(n, 3))(new_qr)
            self.__add_qr_to_map(new_qr, new_qr_data.id)

