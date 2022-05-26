import math
import pandas as pd
import pygame
import time
import os


pygame.init()

# Set up the drawing window
WIDTH = 800
CENTER = (WIDTH/2, WIDTH/2)
ALPHA = 0
CIRCLE_DISTANCE = 50
BACKGROUND_COLOR = (0,0,0)
TOTAL_CIRCLES = 8
SHARED_FILE = "sharedFile.csv"
LAST_DATA_TIME = time.time()
NEON_GREEN = (57, 255, 20)


screen = pygame.display.set_mode([WIDTH, WIDTH])


distance = 110
angle = 45

def get_line_end(start, length_cm, angle_degrees):
    angle_radians = math.radians(angle_degrees+90)
    y = - (math.sin(angle_radians) * length_cm) + start[1]
    x = - (math.cos(angle_radians) * length_cm) + start[0]
    return (x,y)

def draw_target(screen, alpha, center, distance, angle, id, color):
    point = get_line_end(center, distance, angle+alpha)
    pygame.draw.line(screen, color, center, point, 1)
    pygame.draw.circle(screen, color, point, 5, 0)
    # (120, 120, 120)
    font = pygame.font.SysFont('timesnewroman',  16)
 
    text = font.render(id, True, color)
    
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
    
    # set the center of the rectangular object.
    textRect.center = (point[0]+15, point[1])
    screen.blit(text, textRect)

def draw_targets(screen, alpha, center, data_df, color):
    for index, data_elem in data_df.iterrows():
        draw_target(screen, alpha, center, data_elem['distance'], data_elem['angle'], data_elem['id'].astype(str), color)

def data_changed(file, last_time_data):
    return last_time_data < os.path.getmtime(file)


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
    # Draw a solid blue circle in the center
    for i in range(1, total_circles + 1):
        pygame.draw.circle(screen, color, center, i * circle_distance, 1)

def draw_robot(screen, center, alpha):
    pygame.draw.line(screen, (255, 0, 0), center, get_line_end(center, 25, alpha), 2)

def retrieve_data(file):
    return pd.read_csv(file)

# Run until the user asks to quit
def clean_file(file):
    f = open(file, "w")
    f.write("id,distance,angle\n")
    f.close()
# Path(SHARED_FILE).touch()
clean_file(SHARED_FILE)
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
    draw_robot(screen, CENTER, ALPHA)
    # data_df = pd.DataFrame([])
    if data_changed(SHARED_FILE, LAST_DATA_TIME):
        data_df = retrieve_data(SHARED_FILE)
        LAST_DATA_TIME = time.time()  

    draw_targets(screen, ALPHA, CENTER, data_df, NEON_GREEN)
    # draw_target(distance, ALPHA, angle)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()

    