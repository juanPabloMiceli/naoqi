import math
import time

class ModuleAngle():
    def __init__(self, memory):
        self.memory = memory
        self.speed = 1.0
        self.controllables = ["turn_left", "turn_right", "forward"]


    def turn_left(self):
        print("Turning left...")
        self.memory.increase_angle()

    def turn_right(self):
        print("Turning right...")
        self.memory.decrease_angle()

    def forward(self):
        x, y = self.memory.get_player_position()
        angle = self.memory.get_player_angle()
        print(f"Moving angle: {angle=}")
        self.memory.set_player_position([
            self.speed * math.cos(angle) + x,
            self.speed * math.sin(angle) + y
            ])
