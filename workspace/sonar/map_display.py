import math
import pandas as pd
import pygame
import time
import os

from map_display_adapter import MapDisplayAdapter


pygame.init()

# Set up the drawing window
WIDTH = 801
CENTER = (WIDTH//2, WIDTH//2)
GRID_WIDTH = 50
BACKGROUND_COLOR = (0,0,0)
TOTAL_CIRCLES = 6
NEON_GREEN = (57, 255, 20)
ROBOT_COLOR = (255, 0, 0)
QRS_COLOR = (255, 255, 255)
robot_path = []

screen = pygame.display.set_mode([WIDTH, WIDTH])

def draw_target(screen, center, qr_information, color):
    point = (qr_information.x + center[0], qr_information.y + center[1])
    pygame.draw.circle(screen, color, point, 5, 0)
    font = pygame.font.SysFont('timesnewroman',  16)
 
    text = font.render(qr_information.id, True, color)
    
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
    
    # set the center of the rectangular object.
    textRect.center = (point[0], point[1]-15)
    screen.blit(text, textRect)

def draw_targets(screen, center, qrs_information, color):
    for qr_information in qrs_information:
        draw_target(screen, center, qr_information, color)


def draw_qrs(screen, center, qrs_information, color):
    draw_targets(screen, center, qrs_information, color)


def draw_grid(screen, screen_size, grid_width, color):
    for i in range(0, (screen_size // grid_width) + 1):
        # Horizontal lines
        pygame.draw.line(screen, color, (0, i * grid_width), (screen_size, i * grid_width), 1)
        # Vertical lines
        pygame.draw.line(screen, color, (i * grid_width, 0), (i * grid_width, screen_size), 1)


def draw_robot(screen, center, color, robot_position):
    pygame.draw.circle(screen, color, (robot_position[0] + center[0], robot_position[1] + center[1]), 5, 0)

def draw_path(screen, center, path, color):
    for i in range(len(path)-1):
        pygame.draw.line(screen, color, (center[0] + path[i][0], center[1] + path[i][1]), (center[0] + path[i+1][0], center[1] + path[i+1][1]), 1)
        pygame.draw.circle(screen, (77,77, 255), (center[0] + path[i][0], center[1] + path[i][1]), 3, 0)



map_display_adapter = MapDisplayAdapter()
robot_position = (0,0)
qrs_information = []
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    

    # Fill the background with white
    screen.fill(BACKGROUND_COLOR)

    draw_grid(screen, WIDTH, GRID_WIDTH, NEON_GREEN)
    
    if map_display_adapter.has_new_data():
        time.sleep(0.2)
        robot_position = map_display_adapter.get_robot_location()
        qrs_information = map_display_adapter.get_qrs_information()
        robot_path.append(robot_position)

    draw_path(screen, CENTER, robot_path, ROBOT_COLOR)
    draw_robot(screen, CENTER, ROBOT_COLOR, robot_position)
    draw_qrs(screen, CENTER, qrs_information, QRS_COLOR)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()

    