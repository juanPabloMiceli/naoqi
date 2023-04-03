import sys
import pygame
from player import Player
from goal import Goal
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

    memory = SharedMem()
    sensing_position = SensingPosition(memory)
    module_position = ModulePosition(memory)
    sensing_list = [sensing_position]
    module_list = [module_position]

    memory.set_player_position([0,0])
    memory.set_grid_size(grid_size)

    automata = Automata(module_list, memory, verbose=True)
    automata.load_automata_from_file("automata.txt")
    automata.start()


    screen = pygame.display.set_mode((screen_size, screen_size))
    player = Player(0, 0, memory)
    goal = Goal(9,0)
    while True:
        for sensor in sensing_list:
            sensor.sense()
        player_x, player_y = memory.get_player_position()
        goal_x, goal_y = goal.position()
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
        player.render(screen, cell_size)
        goal.render(screen, cell_size)
        pygame.display.flip()

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
