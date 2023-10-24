import numpy as np
import threading
import math
import time
from workspace.mock.movement_daemon import MovementDaemon
from workspace.utils.logger_factory import LoggerFactory
import workspace.utils.geometry as geometry

class NaoMock:

    def __init__(self, shared_memory, map):
        self.LOGGER = LoggerFactory.get_logger("NaoMock", dummy=True)
        self.shared_memory = shared_memory
        self.map = map
        self.movement_daemon = MovementDaemon(self.shared_memory)
        self.movement_daemon.start()
        self.qrs_in_vision = np.array([])

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

    def get_frame(self):
        # QR range: [30cm 1.5mts] [-30deg, 30deg]
        self.qrs_in_vision = np.array([])
        for qr in self.map.qrs:
            distance = geometry.distance(qr.position, self.get_position())
            if distance < 30 or distance > 200:
                continue
            nao_to_qr_direction = geometry.direction(self.get_position(), qr.position) 
            nao_direction_vector = geometry.rotate(np.array([1, 0]), math.radians(self.get_direction())) 

            angle_to_qr = geometry.angle_between_vectors(nao_direction_vector, nao_to_qr_direction)
            if math.degrees(angle_to_qr) > 30 or math.degrees(angle_to_qr) < -30:
                continue
            self.qrs_in_vision = np.append(self.qrs_in_vision, qr)
        time.sleep(1)

    def look_at(self, x_angle_degrees, y_angle_degrees):
        self.LOGGER.info('New head position ({}, {})'.format(x_angle_degrees, y_angle_degrees))

    def walk_forward(self):
        # 80cm in 7 seconds
        self.movement_daemon.move(1, 0, 0)
        self.LOGGER.info('Walking forward')

    def stop_moving(self):
        self.movement_daemon.move(0, 0, 0)
        self.LOGGER.info('Stop moving')

    def walk_backward(self):
        # 80cm in 8.6 seconds
        self.movement_daemon.move(-1, 0, 0)
        self.LOGGER.info('Walking backward')

    def rest(self):
        self.LOGGER.info('Resting')

    def rotate_counter_clockwise(self):
        # 180 degrees in 7 seconds
        self.movement_daemon.move(0, 0, -1)
        self.LOGGER.info('Rotating clockwise')

    def rotate_clockwise(self):
        # 180 degrees in 7 seconds
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
            self.get_frame()

