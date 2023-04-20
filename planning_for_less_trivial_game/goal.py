import pygame
import numpy as np

class Goal:
    def __init__(self, memory, goal_radius):
        self.memory = memory
        self.goal_radius = goal_radius
        self.color = (255, 255, 0) # Yellow

    def position(self):
        return self.memory.get_goal_position()

    def render(self, screen):
        x, y = self.position()
        pygame.draw.circle(
            screen,
            self.color,
            (x, y),
            self.goal_radius
        )
