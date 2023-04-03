import pygame
import time

class Player:
    def __init__(self, start_x, start_y, memory):
        self.x = start_x
        self.y = start_y
        self.color = (0, 255, 0) # Green
        self.memory = memory

    def render(self, screen, cell_size):
        x, y = self.memory.get_player_position()
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect(
                x * cell_size,
                y * cell_size,
                cell_size,
                cell_size
            )
        )
