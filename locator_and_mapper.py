import numpy as np
import math
from geometry import pol2cart, distance, direction, transformed_point
from logger_factory import LoggerFactory

class QrLocation:

    def __init__(self, point, id):
        self.point = point
        self.id = id

class LocatorAndMapper:

    qrs_data = np.array()
    map_axis = None
    map_axis_zero = None
    LOGGER = LoggerFactory.get_logger("LOGGER")

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
            x_dir = direction(point_qr1, point_qr2)
            y_dir = np.array([-self.x_dir[1], self.x_dir[0]])
            self.map_axis = np.array([x_dir, y_dir])
            self.map_axis_zero = point_qr1
            angle_between_coordinates = np.arctan2(self.map_axis[1], self.map_axis[0])
            self.LOGGER.info("Dist: {}".format(qr2_qr1_distance))
            
            self.__add_qr_to_map(point_qr1, qr1.id, angle_between_coordinates)
            self.__add_qr_to_map(point_qr2, qr2.id, angle_between_coordinates)
            
        # Procedimiento general
        known_qrs_indices = self.__get_known_qrs_indices(new_qrs_data)
        if len(known_qrs_indices) >= 2:
            nao_location = self.get_nao_location(known_qrs_indices)
            self.__add_new_qrs(new_qrs_data, nao_location)

        return nao_location
    
    def origin_position(self):
        return transformed_point(np.zeros(2), self.map_axis_zero, self.angle_between_coordinates)

    def __add_qr_to_map(self, point, id, angle_between_coordinates):
        self.qrs_data = np.append(QrLocation(transformed_point(point, self.map_axis_zero, angle_between_coordinates), id))

    def __get_known_qrs_indices(self, new_qrs_data):
        known_qrs = []

        for index, new_qr_data in enumerate(new_qrs_data):
            for qr_data in self.qrs_data:
                if new_qr_data.id == qr_data.id:
                    known_qrs.append(index)
        
        return np.array(known_qrs)[:2] # I am only interested in the first two for localization and mapping
    
    def __get_new_qrs_indices(self, new_qrs_data):
        new_qrs = []

        for index, new_qr_data in new_qrs_data:
            is_new = True
            for qr_data in self.qrs_data:
                if new_qr_data.id == qr_data.id:
                    is_new = False
                    break
            if is_new:
                new_qrs.append(index)
        
        return np.array(new_qrs)

    def __add_new_qrs(self, new_qrs_data, nao_location, known_qrs_indices):
        new_qrs_indices = self.__get_new_qrs_indices(new_qrs_data)

        qr1 = new_qrs_data[known_qrs_indices[0]]
        qr2 = new_qrs_data[known_qrs_indices[1]]

        # New QR angle in map coords is the sum of the new QR angle in NAO coords and NAO angle in map coords.
        # Nao angle in map coords is the sum of the angle of the known QRs in the map coords and the angle of the known QRs in NAO coords


        gamma = np.arctan2()

        for new_qr_index in new_qrs_indices:
            new_qr_data = new_qrs_data[new_qr_index]

