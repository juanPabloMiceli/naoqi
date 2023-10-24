import pygame
from workspace.mock.simulation.colors import *
from threading import Thread
import numpy as np
import math

from workspace.properties.nao_properties import NaoProperties

class NaoSimulation(Thread):
    def __init__(self, nao, _map):
        super(NaoSimulation, self).__init__()
        pygame.init()
        self.nao = nao
        self._map = _map
        self.screen_width = 800
        self.screen_height = 800
        self.map_offset = np.array([100, 100])

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.setDaemon(True)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Fill the background with white
            self.screen.fill(DARK_GRAY)

            self.__draw_map()
            self.__draw_real_nao()
            self.__draw_measured_nao()
            # Update the display
            pygame.display.flip()

        # Quit Pygame
        pygame.quit()

    def __draw_map(self):
        pygame.draw.rect(self.screen, WHITE, (self.map_offset[0] - 5, self.map_offset[1] - 5, self._map.width + 10, self._map.height + 10))
        pygame.draw.rect(self.screen, LIGHT_GRAY, (self.map_offset[0], self.map_offset[1], self._map.width, self._map.height))
        
        for qr in self._map.qrs:
            qr_position = qr.position + self.map_offset
            pygame.draw.circle(self.screen, PURPLE, qr_position, 3)
    
    def __draw_real_nao(self):
        nao_color = YELLOW if self.nao.get_head_leds() else DARK_GRAY
        nao_position = self.nao.get_position_simulation() + self.map_offset
        nao_direction = 360 - self.nao.get_direction_simulation() # Mirrors X axis
        pygame.draw.circle(self.screen, nao_color, nao_position, 20)
        pygame.draw.arc(self.screen, FOV_COLOR, (nao_position[0] - NaoProperties.qr_max_distance(), nao_position[1] - NaoProperties.qr_max_distance(), NaoProperties.qr_max_distance() * 2, NaoProperties.qr_max_distance() * 2), math.radians(nao_direction - (NaoProperties.qr_detection_angle() / 2)), math.radians(nao_direction + (NaoProperties.qr_detection_angle() / 2)), NaoProperties.qr_max_distance() - NaoProperties.qr_min_distance())
        # pygame.draw.arc(self.screen, CYAN, (nao_position[0] - 200, nao_position[1] - 200, 400, 400), math.radians(nao_direction - 15), math.radians(nao_direction + 15), 2)
        # pygame.draw.arc(self.screen, CYAN, (nao_position[0] - 30, nao_position[1] - 30, 60, 60), math.radians(nao_direction - 15), math.radians(nao_direction + 15), 2)

    def __draw_measured_nao(self):
        nao_radius = 5
        nao_position = self.nao.get_position() + self.map_offset
        pygame.draw.line(self.screen, RED, (nao_position[0] - nao_radius, nao_position[1] - nao_radius), (nao_position[0] + nao_radius, nao_position[1] + nao_radius), 5)
        pygame.draw.line(self.screen, RED, (nao_position[0] + nao_radius, nao_position[1] - nao_radius), (nao_position[0] - nao_radius, nao_position[1] + nao_radius), 5)