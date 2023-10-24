import numpy as np
import threading
import math
import time
from workspace.location.locator_and_mapper import LocatorAndMapper
from workspace.mock.movement_daemon import MovementDaemon
from workspace.properties.nao_properties import NaoProperties
from workspace.utils.logger_factory import LoggerFactory
import workspace.utils.geometry as geometry
from workspace.utils.qr_position_data import QrPositionData

class NaoMock:

    def __init__(self, shared_memory, _map):
        self.LOGGER = LoggerFactory.get_logger("NaoMock", dummy=True)
        self.shared_memory = shared_memory
        self._map = _map
        self.movement_daemon = MovementDaemon(self.shared_memory)
        self.movement_daemon.start()
        self.qrs_in_vision = np.array([])
        self.locator_and_mapper = LocatorAndMapper(self.shared_memory, self, _map)
        self.locator_and_mapper.start()

    def head_leds_on(self):
        self.shared_memory.set_brain_leds(True)
        self.LOGGER.info('Leds on')

    def head_leds_off(self):
        self.shared_memory.set_brain_leds(False)
        self.LOGGER.info('Leds off')

    def get_head_leds(self):
        return self.shared_memory.get_brain_leds()

    def set_awareness(self, new_awareness):
        if new_awareness:
            awareness_status = 'enabled'
        else:
            awareness_status = 'disabled'
        self.LOGGER.info('Awareness {}'.format(awareness_status))

    def get_qrs_in_vision(self):
        start = time.time()

        qrs_in_vision = []
        for qr in self._map.qrs:
            distance = geometry.distance(qr.position, self.get_position_simulation())
            if distance < NaoProperties.qr_min_distance() or distance > NaoProperties.qr_max_distance():
                continue
            nao_to_qr_direction = geometry.direction(self.get_position_simulation(), qr.position) 
            nao_direction_vector = geometry.rotate(np.array([1, 0]), math.radians(self.get_direction_simulation())) 

            angle_to_qr = math.degrees(geometry.angle_between_vectors(nao_to_qr_direction, nao_direction_vector))
            if angle_to_qr > NaoProperties.qr_detection_angle() / 2 or angle_to_qr < -(NaoProperties.qr_detection_angle() / 2):
                continue
            qrs_in_vision.append(QrPositionData(qr.id, distance, angle_to_qr))

        end = time.time()
        sleep_time = max(0, (1 / NaoProperties.nao_fps()) - (end - start))
        time.sleep(sleep_time)

        return qrs_in_vision

    def look_at(self, x_angle_degrees, y_angle_degrees):
        self.LOGGER.info('New head position ({}, {})'.format(x_angle_degrees, y_angle_degrees))

    def walk_forward(self):
        self.movement_daemon.move(1, 0, 0)
        self.LOGGER.info('Walking forward')

    def stop_moving(self):
        self.movement_daemon.move(0, 0, 0)
        self.LOGGER.info('Stop moving')

    def walk_backward(self):
        self.movement_daemon.move(-1, 0, 0)
        self.LOGGER.info('Walking backward')

    def rest(self):
        self.LOGGER.info('Resting')

    def rotate_counter_clockwise(self):
        self.movement_daemon.move(0, 0, -1)
        self.LOGGER.info('Rotating clockwise')

    def rotate_clockwise(self):
        self.movement_daemon.move(0, 0, 1)
        self.LOGGER.info('Rotating counter clockwise')

    def get_position(self):
        return self.shared_memory.get_position()
    
    def get_position_simulation(self):
        return self.shared_memory.get_position_simulation()

    def get_direction(self):
        return self.shared_memory.get_direction()
    
    def get_direction_simulation(self):
        return self.shared_memory.get_direction_simulation()

    def debug_qrs(self):
        while True:
            self.get_qrs_in_vision()

