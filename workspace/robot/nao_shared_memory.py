import numpy as np
from multiprocessing import Value

class NaoSharedMemory:
    def __init__(self):
        self.__brain_leds = Value('b', False)
        self.__x_position = Value('f', 0.0)
        self.__y_position = Value('f', 0.0)
        self.__direction = Value('f', 0.0)
        self.__x_position_simulation = Value('f', 150.0)
        self.__y_position_simulation = Value('f', 150.0)
        self.__direction_simulation = Value('f', 45.0)
    
    def set_brain_leds(self, new_value):
        with self.__brain_leds.get_lock():
            self.__brain_leds.value = new_value

    def get_brain_leds(self):
        return self.__brain_leds.value

    def set_position(self, new_position):
        with self.__x_position.get_lock():
            self.__x_position.value = new_position[0]
        with self.__y_position.get_lock():
            self.__y_position.value = new_position[1]

    def get_position(self):
        return np.array([self.__x_position.value, self.__y_position.value])

    def get_direction(self):
        return self.__direction.value

    def set_direction(self, new_direction):
        new_direction %= 360
        with self.__direction.get_lock():
            self.__direction.value = new_direction

    def set_position_simulation(self, new_position_simulation):
        with self.__x_position_simulation.get_lock():
            self.__x_position_simulation.value = new_position_simulation[0]
        with self.__y_position_simulation.get_lock():
            self.__y_position_simulation.value = new_position_simulation[1]

    def get_position_simulation(self):
        return np.array([self.__x_position_simulation.value, self.__y_position_simulation.value])

    def get_direction_simulation(self):
        return self.__direction_simulation.value

    def set_direction_simulation(self, new_direction_simulation):
        new_direction_simulation %= 360
        with self.__direction_simulation.get_lock():
            self.__direction_simulation.value = new_direction_simulation 
