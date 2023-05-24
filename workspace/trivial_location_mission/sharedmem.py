from ctypes import c_bool
from multiprocessing import Value,Queue
from ctypes import *
import numpy as np

'''
Shared memory module that will be available for every module controlling the
NAO.
Attributes:
    * _naox, _naoy: Two values of type double that will tell us the current
    location of the NAO.

    * _goalx, _goaly: Two values of type double that will tell us the current
    location of the goal.

    * event_queue: Message Queue that will be used for communicating the plan
    events and controllable modules.
'''
class SharedMem():
    def __init__(self):
        #NAO Position
        self._naox = Value('d',0.0) #X axis
        self._naoy = Value('d',0.0) #Y axis

        self._nao_direction = Value('d', 0.0)

        #goal Position
        self._goalx = Value('d',0.0) #X axis
        self._goaly = Value('d',0.0) #Y axis

        #Event queue
        self._event_queue = Queue()

    def set_nao_position(self, new_position):
        self._naox.value = new_position[0]
        self._naoy.value = new_position[1]

    def get_nao_position(self):
        return np.array([self._naox.value, self._naoy.value])

    def set_nao_direction(self, new_direction):
        self._nao_direction.value = new_direction

    def get_nao_position(self):
        return self._nao_direction.value

    def set_goal_position(self, new_position):
        self._goalx.value = new_position[0]
        self._goaly.value = new_position[1]

    def get_goal_position(self):
        return np.array([self._goalx.value, self._goaly.value])

    def add_message(self, msg):
        self._event_queue.put(msg)

    def get_message(self):
        return self._event_queue.get()

    def messages_left(self):
        return self._event_queue.qsize()
