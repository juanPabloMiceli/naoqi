import math
import time

class ModulePosition():
    def __init__(self, memory):
        self.memory = memory
        self.speed = 1.0
        self.controllables = ["forward"]

    def forward(self):
        x, y = self.memory.get_player_position()
        angle = self.memory.get_player_angle()
        self.memory.set_player_position([
            self.speed * math.sin(math.radians(angle)) + x,
            self.speed * math.cos(math.radians(angle)) + y
            ])
