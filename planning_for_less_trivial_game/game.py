import math
import time
import sys
import pygame
from player import Player
from goal import Goal
from sensing_angle import SensingAngle
from module_angle import ModuleAngle
from sensing_position import SensingPosition
from module_position import ModulePosition

from planner_util_sharedmem import SharedMem
from planner_automata import Automata


def main():
    # Constants
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    screen_size = 500
    grid_size = 10
    cell_size = screen_size // grid_size
    goal_radius = cell_size // 2

    memory = SharedMem()
    sensing_angle = SensingAngle(memory)
    sensing_position = SensingPosition(memory, goal_radius)
    module_angle = ModuleAngle(memory)
    module_position = ModulePosition(memory)
    sensing_list = [sensing_angle, sensing_position]
    module_list = [module_angle]

    memory.set_player_position([250.0, 250.0])
    memory.set_goal_position([[250.0, 450.0], [100.0, 100.0], [400.0, 100.0],
        [100.0, 400.0], [250.0, 250.0]])
    memory.set_grid_size(grid_size)
    memory.set_player_angle(0.0)

    automata = Automata(module_list, memory, verbose=True)
    automata.load_automata_from_file("angle_automata_v3.txt")
    automata.start()


    screen = pygame.display.set_mode((screen_size, screen_size))
    player = Player(memory)
    goal = Goal(memory, goal_radius)
    font = pygame.font.SysFont('Arial', 20)
    while True:
        frame_start = time.time()
        for sensor in sensing_list:
            sensor.sense()
        player_x, player_y = memory.get_player_position()
        goal_x, goal_y = memory.get_goal_position()
        if (player_x, player_y) == (goal_x, goal_y):
            print("Victory")
            memory.event_queue.put('exit')
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                memory.event_queue.put('exit')
                sys.exit()
        screen.fill(BLACK)
        draw_grid(screen, screen_size, cell_size, WHITE)
        goal.render(screen)
        player.render(screen)
        # render the angle text as a surface
        player_angle = math.degrees(memory.get_player_angle())
        angle_to_goal = math.degrees(memory.get_angle_to_goal())
        distance_to_goal = sensing_position.distance_to_goal()
        angle_surface = font.render(
                f"Angle: {player_angle:.1f}", True, (255,255, 255))
        angle_to_goal_surface = font.render(
                f"Angle to goal:{angle_to_goal:.1f}", True, (255, 255, 255))
        distance_to_goal_surface = font.render(
                f"Distance to goal:{distance_to_goal:.1f}", True, (255, 255, 255))

        # blit the angle surface onto the screen
        screen.blit(
                angle_surface,
                (
                    screen_size - angle_surface.get_width() - 10,
                    10))
        screen.blit(
                angle_to_goal_surface,
                (
                    screen_size - angle_to_goal_surface.get_width() - 10,
                    angle_to_goal_surface.get_height() + 10
                ))
        screen.blit(
                distance_to_goal_surface,
                (
                    screen_size - distance_to_goal_surface.get_width() - 10,
                    2*distance_to_goal_surface.get_height() + 10
                ))
        pygame.display.flip()
        frame_end = time.time()
        time.sleep(0.05 - (frame_end - frame_start))

def draw_grid(screen, grid_size, cell_size, grid_color):
    for line_position in range(0, grid_size, cell_size):
        pygame.draw.line(
            screen,
            grid_color,
            (line_position, 0),
            (line_position, grid_size)
        )
        pygame.draw.line(
            screen,
            grid_color,
            (0,line_position),
            (grid_size, line_position)
        )

if __name__ == "__main__":
    pygame.init()
    main()
