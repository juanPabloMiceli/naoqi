import math
import threading
import numpy as np
from workspace.cli.parsers.move_parser import rotate_clockwise
from workspace.utils import geometry


class AdvancedMovementController:
    '''
    This class handles things like 'move to this place'.
    These methods are non blocking.
    Only one method is allowed to run at any point of time, so if a second method is called before the first
    one released the lock, it will immediately return without performing any actions.
    '''
    def __init__(self, nao, shared_memory):
        self.lock = threading.RLock()        
        self.nao = nao
        self.shared_memory = shared_memory
        
    def move_to(self, target_position, target_angle):
        thread = threading.Thread(target=self.__move_to, args=[target_position, target_angle])
        thread.setDaemon(True)
        thread.start()

    def __move_to(self, target_position, target_angle):
        if not self.lock.acquire(False):
            print('Move operation denied, lock is already in use')
            return
        try:
            current_position = self.shared_memory.get_position()
            distance_to_target = geometry.distance(current_position, target_position)
            
            while distance_to_target > 20:
                current_position = self.shared_memory.get_position()
                distance_to_target = geometry.distance(current_position, target_position)
                nao_to_target_direction = geometry.direction(current_position, target_position)
                nao_to_target_angle = math.degrees(geometry.angle(nao_to_target_direction)) 
                self.__rotate_to(nao_to_target_angle)
                if self.nao.is_lost():
                    self.nao.stop_moving()
                else:
                    self.nao.walk_forward()

            self.__rotate_to(target_angle)
            self.nao.stop_moving()
        finally:
            self.lock.release()

    def __rotate_to(self, target_angle):
        if not self.lock.acquire(False):
            print('Rotate operation denied, lock is already in use')
            return
        try:
            nao_direction = self.shared_memory.get_direction()
            clockwise_distance = (target_angle - nao_direction + 360) % 360
            counterclockwise_distance = (nao_direction - target_angle + 360) % 360
            angle_to_target = min(clockwise_distance, counterclockwise_distance)

            while angle_to_target > 30:
                if clockwise_distance < counterclockwise_distance:
                    self.nao.rotate_clockwise()
                else:
                    self.nao.rotate_counter_clockwise()
                nao_direction = self.shared_memory.get_direction()
                clockwise_distance = (target_angle - nao_direction + 360) % 360
                counterclockwise_distance = (nao_direction - target_angle + 360) % 360
                angle_to_target = min(clockwise_distance, counterclockwise_distance)
        finally:
            self.lock.release()
