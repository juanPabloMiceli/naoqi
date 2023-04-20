import math
import pandas as pd
import pygame
import time
import os

from sonar_adapter import SonarAdapter


pygame.init()

# Set up the drawing window
WIDTH = 800
CENTER = (WIDTH/2, WIDTH/2)
ALPHA = 0
CIRCLE_DISTANCE = 50
BACKGROUND_COLOR = (0,0,0)
TOTAL_CIRCLES = 6
NEON_GREEN = (57, 255, 20)
ROBOT_COLOR = (255, 0, 0)

screen = pygame.display.set_mode([WIDTH, WIDTH])

def get_line_end(start, length_cm, angle_degrees):
    angle_radians = math.radians(angle_degrees+90)
    y = - (math.sin(angle_radians) * length_cm) + start[1]
    x = - (math.cos(angle_radians) * length_cm) + start[0]
    return (x,y)

def draw_target(screen, alpha, center, distance, angle, id, color):
    point = get_line_end(center, distance, angle+alpha)
    pygame.draw.line(screen, color, center, point, 1)
    pygame.draw.circle(screen, color, point, 5, 0)
    font = pygame.font.SysFont('timesnewroman',  16)
 
    text = font.render(id, True, color)
    
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
    
    # set the center of the rectangular object.
    textRect.center = (point[0], point[1]-15)
    screen.blit(text, textRect)

def draw_targets(screen, alpha, center, data_df, color):
    for _, data_elem in data_df.iterrows():
        draw_target(screen, alpha, center, data_elem['distance'], data_elem['angle'], data_elem['id'].astype(int).astype(str), color)


def draw_target_info(screen, alpha, center, counter, color, distance, angle, id):
    font = pygame.font.SysFont('timesnewroman',  16)
 
    text = font.render(f"id: {id.astype(int)}, distance: {distance}, angle: {angle}", True, color)
    
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
    
    # set the center of the rectangular object.
    textRect.left = 10
    textRect.top = center[1] + (counter*20)+ 290
    screen.blit(text, textRect)

def draw_targets_info(screen, alpha, center, data_df, color):
    counter = 0
    for _, data_elem in data_df.iterrows():
        draw_target_info(screen, alpha, center, counter, color, round(data_elem['distance'], 3).astype(str), round(data_elem['angle'], 3).astype(str), data_elem['id'].astype(int).astype(str))
        counter += 1

def draw_qrs(screen, alpha, center, data_df, color):
    draw_targets(screen, alpha, center, data_df, color)
    draw_targets_info(screen, alpha, center, data_df, color)

def update_display_angle(angle):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        angle += 0.25
    if keys[pygame.K_LEFT]:
        angle -= 0.25
    if keys[pygame.K_r]:
        angle = 0

    return angle

def draw_sonar_circles(screen, circle_distance, total_circles, center, color):
    for i in range(1, total_circles + 1):
        pygame.draw.circle(screen, color, center, i * circle_distance, 1)

def draw_robot(screen, color, center, alpha):
    pygame.draw.line(screen, color, center, get_line_end(center, 25, alpha), 2)

def retrieve_data(file):
    return pd.read_csv(file)


# clean_file(SHARED_FILE)
sonar_adapter = SonarAdapter()

running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    ALPHA = update_display_angle(ALPHA)

    # Fill the background with white
    screen.fill(BACKGROUND_COLOR)

    draw_sonar_circles(screen, CIRCLE_DISTANCE, TOTAL_CIRCLES, CENTER, NEON_GREEN)
    draw_robot(screen, ROBOT_COLOR, CENTER, ALPHA)
    if sonar_adapter.has_new_data:
        data_df = sonar_adapter.get_data()

    draw_qrs(screen, ALPHA, CENTER, data_df, NEON_GREEN)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()

    