import math
from ctypes import c_bool
from multiprocessing import Value, RawArray, Queue
from ctypes import *
import numpy as np

class SharedMem():
    def __init__(self):
        #Player Position
        self._posx = Value('d',0.0) #X axis
        self._posy = Value('d',0.0) #Y axis

        #Goal Position
        self._goal_index = Value('i', 0)
        self._goal_x_array = RawArray('d', [0.0, 0.0, 0.0, 0.0, 0.0])
        self._goal_y_array = RawArray('d', [0.0, 0.0, 0.0, 0.0, 0.0])
        self._goal_x = Value('d', 0.0)
        self._goal_y = Value('d', 0.0)

        #Angle
        self._angle = Value('d', 0.0)

        #Grid
        self._grid_size = Value('I', 0)

        #Event queue
        self.event_queue = Queue()

    def set_player_position(self,pos):
        self._posx.value = pos[0]
        self._posy.value = pos[1]

    def get_player_position(self):
        return np.array([self._posx.value,self._posy.value])

    def advance_goal(self):
        self._goal_index.value = (self._goal_index.value + 1) % len(self._goal_x_array.value)

    def set_goal_position(self, goal_positions):
        x_positions = []
        y_positions = []
        for goal_position in goal_positions:
            x_positions.append(goal_position[0])
            y_positions.append(goal_position[1])
        self._goal_x_array.value = x_positions
        self._goal_y_array.value = y_positions

    def get_goal_position(self):
        return np.array([
            self._goal_x_array.value[self._goal_index.value],
            self._goal_y_array.value[self._goal_index.value]
            ])

    def set_grid_size(self, size):
        self._grid_size.value = size

    def get_grid_size(self):
        return self._grid_size.value

    def get_angle_to_goal(self):
        goal_x, goal_y = self.get_goal_position()
        player_x, player_y = self.get_player_position()
        dx = goal_x - player_x
        dy = goal_y - player_y
        angle_to_goal = math.atan2(dy, dx) - self.get_player_angle()
        if angle_to_goal  < 0:
            angle_to_goal  += 2 * math.pi
        if angle_to_goal  > 2 * math.pi:
            angle_to_goal  -= 2 * math.pi
        return angle_to_goal

    def set_player_angle(self, angle):
        self._angle.value = angle

    def get_player_angle(self):
        return self._angle.value

    def decrease_angle(self):
        new_angle = self._angle.value - 0.05
        if new_angle < 0:
            new_angle += 2 * math.pi
        self._angle.value = new_angle

    def increase_angle(self):
        new_angle = self._angle.value + 0.05
        if new_angle > 2 * math.pi:
            new_angle -= 2 * math.pi
        self._angle.value = new_angle
