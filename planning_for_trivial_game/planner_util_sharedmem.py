from ctypes import c_bool
from multiprocessing import Value,Queue
from ctypes import *
import numpy as np

class SharedMem():
    def __init__(self):
        #Position
        self._posx = Value('I',0) #X axis
        self._posy = Value('I',0) #Y axis

        #Grid
        self._grid_size = Value('I', 0)

        #Event queue
        self.event_queue = Queue()

    def set_player_position(self,pos):
        self._posx.value = pos[0]
        self._posy.value = pos[1]

    def get_player_position(self):
        return np.array([self._posx.value,self._posy.value])

    def set_grid_size(self, size):
        self._grid_size.value = size

    def get_grid_size(self):
        return self._grid_size.value
