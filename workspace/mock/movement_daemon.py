import numpy as np
import math
import time
from threading import Thread
from workspace.utils.geometry import rotate
from workspace.properties.nao_properties import NaoProperties

class MovementDaemon(Thread):
    def __init__(self, shared_memory):
        super(MovementDaemon, self).__init__()
        self.setDaemon(True)
        self.shared_memory = shared_memory
        self.x_speed = 0
        self.y_speed = 0
        self.direction_speed = 0

    def run(self):
        while True:
            start = time.time()
            current_direction = self.shared_memory.get_direction_simulation()
            current_position = self.shared_memory.get_position_simulation()
            self.shared_memory.set_direction_simulation(current_direction + self.direction_speed)
            
            walk_vector = rotate([self.x_speed, self.y_speed], math.radians(current_direction))
            self.shared_memory.set_position_simulation(walk_vector + current_position)
            end = time.time()
            sleep_time = max(0, (1 / NaoProperties.simulation_fps()) - (end - start))
            time.sleep(sleep_time)

    def move(self, x, y, direction):
        if x >= 0:
            self.x_speed = x * NaoProperties.forward_speed() # NAO real forward speed 11.5cm/sec
        else:
            self.x_speed = x * NaoProperties.backward_speed() # Nao real backward speed 9.5cm/sec
        self.y_speed = y
        self.direction_speed = direction * NaoProperties.rotation_speed() # NAO real rotation speed (26deg/sec)