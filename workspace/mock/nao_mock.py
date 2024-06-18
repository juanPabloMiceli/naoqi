import numpy as np
import math
import time
from workspace.location.advanced_movement_controller import AdvancedMovementController
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
        self.advanced_movement_controller = AdvancedMovementController(self, shared_memory)
        self.LOGGER.info('Starting robot...')
        time.sleep(2)
        self.LOGGER.info('Robot started...')


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
            distance, angle = self.__get_distance_and_angle(self.get_position_simulation(), self.get_direction_simulation(), qr.position)

            if self.__is_in_vision(distance, angle, NaoProperties.qr_min_distance(), NaoProperties.qr_max_distance(), NaoProperties.qr_detection_angle()):
                qrs_in_vision.append(QrPositionData(qr.id, distance, angle))

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
    
    def move_to(self, x, y, final_angle_degrees):
        self.advanced_movement_controller.move_to(np.array([x, y]), final_angle_degrees)

    def move_to_goal(self):
        goal_position, goal_direction = self.get_goal()
        if goal_position is None:
            print('No goal defined!')
            return
        self.move_to(goal_position[0], goal_position[1], goal_direction)

    def rotate_to(self, target_angle_degrees):
        self.advanced_movement_controller.rotate_to(target_angle_degrees)

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
    
    def is_lost(self):
        return self.shared_memory.get_nao_is_lost()
    
    def set_is_lost(self, new_value):
        return self.shared_memory.set_nao_is_lost(new_value)
    
    def new_goal(self, goal_position, target_direction_degrees):
        self.shared_memory.set_current_goal_position(goal_position)
        self.shared_memory.set_current_goal_direction(target_direction_degrees)
    
    def get_goal(self):
        return (self.shared_memory.get_current_goal_position(), self.shared_memory.get_current_goal_direction())

    def debug_qrs(self):
        while True:
            qrs = self.get_qrs_in_vision()
            for qr in qrs:
                side = "right" if qr.angle < 0 else "left"
                self.LOGGER.info("QR {} found {:.2f}cm away and {:.2f}deg {}".format(qr.id, qr.distance, abs(qr.angle), side))

    def say(self, text):
        self.LOGGER.info("Nao says: \"{}\"".format(text))


    def get_ball_info(self):
        start = time.time()

        ball_info = None
        for ball in self._map.balls:
            distance, angle = self.__get_distance_and_angle(self.get_position_simulation(), self.get_direction_simulation(), ball.position)

            if self.__is_in_vision(distance, angle, NaoProperties.qr_min_distance(), NaoProperties.qr_max_distance(), NaoProperties.qr_detection_angle()):
                ball_info = (distance, angle)

        end = time.time()
        sleep_time = max(0, (1 / 20) - (end - start))
        time.sleep(sleep_time)

        return ball_info

    def debug_red_ball_detection(self):
        while True:
            detected_ball_info = self.get_ball_info()
            if detected_ball_info is not None:
                distance, horizontal_angle = detected_ball_info
                horizontal_side = "right" if horizontal_angle < 0 else "left"
                self.LOGGER.info("Ball detected: {:.2f}cm away, {:.2f}deg {}".format(distance, abs(horizontal_angle), horizontal_side))

    def __is_in_vision(self, distance, angle, min_distance, max_distance, detection_angle):
        if distance < min_distance or distance > NaoProperties.qr_max_distance():
            return False
        return abs(angle) < (detection_angle / 2)


    def __get_distance_and_angle(self, nao_position, nao_direction, other_position):
        x_versor = np.array([1, 0]) 
        distance = geometry.distance(other_position, nao_position)
        nao_to_other_direction = geometry.direction(nao_position, other_position) 
        nao_direction_vector = geometry.rotate(x_versor, math.radians(nao_direction)) 

        angle_to_other = math.degrees(geometry.angle_between_vectors(nao_to_other_direction, nao_direction_vector))
        return distance, angle_to_other
