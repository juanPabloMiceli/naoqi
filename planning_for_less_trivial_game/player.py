import math
import pygame
import time

class Player:
    def __init__(self, memory):
        self.triangle_size = 20.0
        self.triangle_center = [250.0, 250.0]
        self.angle = 0.0
        self.color = (0, 255, 0) # Green
        self.memory = memory

    def render(self, screen):
        pygame.draw.polygon(
            screen,
            self.color,
            self.triangle_points()
        )

    # update the triangle position based on user input
    def triangle_points(self):
        PI = math.pi
        angle = self.memory.get_player_angle()
        player_x, player_y = self.memory.get_player_position()
        point1 = (
                player_x + self.triangle_size * math.cos(angle),
                player_y + self.triangle_size * math.sin(angle)
                )
        point2 = (
                player_x + self.triangle_size * math.cos(angle + PI - (PI / 5)),
                player_y + self.triangle_size * math.sin(angle + PI - (PI / 5))
                )
        point3 = (
                player_x + self.triangle_size * math.cos(angle + PI + (PI / 5)),
                player_y + self.triangle_size * math.sin(angle + PI + (PI / 5))
                )
        return [point1, point2, point3]

