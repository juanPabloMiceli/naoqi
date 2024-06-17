import pygame
from workspace.mock.simulation.colors import *
from threading import Thread
import numpy as np
import math

from workspace.properties.nao_properties import NaoProperties
from workspace.utils import geometry

class NaoSimulation(Thread):
    def __init__(self, nao, _map):
        super(NaoSimulation, self).__init__()
        pygame.init()
        self.nao = nao
        self._map = _map
        self.screen_width = 700
        self.screen_height = 500
        self.map_offset = np.array([100, 100])
        self.buttons_callbacks = {}

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.setDaemon(True)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos() 
                    for _, button_info in self.buttons_callbacks.items():
                        top, left, width, height = button_info["top"], button_info["left"], button_info["width"], button_info["height"]
                        if left <= x <= left + width and top <= y <= top + height:
                            button_info["callback"]()
                            break

            # Fill the background with white
            self.screen.fill(DARK_GRAY)

            self.__draw_map()
            self.__draw_real_nao()
            self.__draw_goal()
            self.__draw_measured_nao()
            self.__draw_buttons()
            # Update the display
            pygame.display.flip()

        # Quit Pygame
        pygame.quit()

    def __draw_buttons(self):
        for _, button_info in self.buttons_callbacks.items():
            top, left, width, height = button_info["top"], button_info["left"], button_info["width"], button_info["height"]
            inside_color = button_info['inside_color']
            outside_color = button_info['outside_color']
            pygame.draw.rect(self.screen, outside_color, (left - 5, top - 5, width + 10, height + 10))
            pygame.draw.rect(self.screen, inside_color, (left, top, width, height))


    def __draw_map(self):
        pygame.draw.rect(self.screen, WHITE, (self.map_offset[0] - 5, self.map_offset[1] - 5, self._map.width + 10, self._map.height + 10))
        pygame.draw.rect(self.screen, LIGHT_GRAY, (self.map_offset[0], self.map_offset[1], self._map.width, self._map.height))
        
        for qr in self._map.qrs:
            qr_position = qr.position + self.map_offset
            pygame.draw.circle(self.screen, PURPLE, qr_position, 3)

        for ball in self._map.balls:
            ball_position = ball.position + self.map_offset
            pygame.draw.circle(self.screen, RED, ball_position, 5)
    
    def __draw_real_nao(self):
        nao_color = self.__get_nao_color()
        nao_position = self.nao.get_position_simulation() + self.map_offset
        nao_direction = self.nao.get_direction_simulation() 
        pygame.draw.circle(self.screen, nao_color, nao_position, 20)
        self.__draw_real_fov(nao_position, nao_direction)

    def __draw_real_fov(self, nao_position, nao_direction):
        # Draw arcs
        direction = 360 - nao_direction # Mirrors X axis
        pygame.draw.arc(self.screen, FOV_COLOR, (nao_position[0] - NaoProperties.qr_max_distance(), nao_position[1] - NaoProperties.qr_max_distance(), 2 * NaoProperties.qr_max_distance(), 2 * NaoProperties.qr_max_distance()), math.radians(direction - (NaoProperties.qr_detection_angle() / 2)), math.radians(direction + (NaoProperties.qr_detection_angle() / 2)), 2)
        pygame.draw.arc(self.screen, FOV_COLOR, (nao_position[0] - NaoProperties.qr_min_distance(), nao_position[1] - NaoProperties.qr_min_distance(), 2 * NaoProperties.qr_min_distance(), 2 * NaoProperties.qr_min_distance()), math.radians(direction - (NaoProperties.qr_detection_angle() / 2)), math.radians(direction + (NaoProperties.qr_detection_angle() / 2)), 2)
        
        # Draw center line
        direction = math.radians(nao_direction)
        line_start = nao_position + geometry.pol2cart(NaoProperties.qr_min_distance(), direction)
        self.__draw_line_from_position(line_start, direction, NaoProperties.qr_max_distance() - NaoProperties.qr_min_distance(), FOV_COLOR)

        # Draw clockwise line
        direction = math.radians(nao_direction + (NaoProperties.qr_detection_angle() / 2))
        line_start = nao_position + geometry.pol2cart(NaoProperties.qr_min_distance(), direction)
        self.__draw_line_from_position(line_start, direction, NaoProperties.qr_max_distance() - NaoProperties.qr_min_distance(), FOV_COLOR)

        # Draw counter clockwise line
        direction = math.radians(nao_direction - (NaoProperties.qr_detection_angle() / 2))
        line_start = nao_position + geometry.pol2cart(NaoProperties.qr_min_distance(), direction)
        self.__draw_line_from_position(line_start, direction, NaoProperties.qr_max_distance() - NaoProperties.qr_min_distance(), FOV_COLOR)


    def __draw_line_from_position(self, position, angle, length, color):
        line_end = position + geometry.pol2cart(length, angle)
        pygame.draw.line(self.screen, color, position, line_end)
        
    def __get_nao_color(self):
        if self.nao.is_lost():
            return BLUE
        if self.nao.get_head_leds():
            return YELLOW
        return DARK_GRAY

    def __draw_measured_nao(self):
        nao_radius = 5
        nao_position = self.nao.get_position() + self.map_offset
        nao_direction = self.nao.get_direction() 

        # Nao Position
        pygame.draw.line(self.screen, RED, (nao_position[0] - nao_radius, nao_position[1] - nao_radius), (nao_position[0] + nao_radius, nao_position[1] + nao_radius), 5)
        pygame.draw.line(self.screen, RED, (nao_position[0] + nao_radius, nao_position[1] - nao_radius), (nao_position[0] - nao_radius, nao_position[1] + nao_radius), 5)

        # Nao Direction
        direction = math.radians(nao_direction)
        line_start = nao_position + geometry.pol2cart(NaoProperties.qr_min_distance(), direction)
        self.__draw_line_from_position(line_start, direction, NaoProperties.qr_max_distance() - NaoProperties.qr_min_distance(), RED)

    
    def __draw_goal(self):
        goal_position, _ = self.nao.get_goal()
        if goal_position is not None:
            pygame.draw.circle(self.screen, GOLD, goal_position + self.map_offset, 20, 2)

    def add_button(self, inside_color,  outside_color, rect, callback):
        self.buttons_callbacks['button_{}'.format(len(self.buttons_callbacks))] = {
            'left': rect[0],
            'top': rect[1],
            'width': rect[2],
            'height': rect[3],
            'inside_color': inside_color,
            'outside_color': outside_color,
            'callback': callback
        }
