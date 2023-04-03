import pygame
import numpy as np

class Goal:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.color = (255, 255, 0) # Yellow

    def position(self):
        return np.array([self.x, self.y])

    def render(self, screen, cell_size):
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect(
                self.x * cell_size,
                self.y * cell_size,
                cell_size,
                cell_size
            )
        )
