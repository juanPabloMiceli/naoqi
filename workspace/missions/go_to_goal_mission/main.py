import time

import numpy as np
from workspace.automata.planner_automata import Automata
from workspace.missions.go_to_goal_mission.close_to_goal_sensor import CloseToGoalSensor
from workspace.missions.go_to_goal_mission.go_command_sensor import GoCommandSensor
from workspace.missions.go_to_goal_mission.leds_module import LedsModule
from workspace.missions.go_to_goal_mission.move_module import MoveModule
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.logger_factory import LoggerFactory
from workspace.utils.nao_factory import NaoFactory

LOGGER = LoggerFactory.get_logger("main")

shared_memory = NaoSharedMemory()
nao, simulation = NaoFactory.create(shared_memory)

goals_positions = [np.array([100, 200]), np.array([100, 100]), np.array([220, 200])]
goals_directions = [180, 180, 0]  
nao.new_goal(goals_positions[0], goals_directions[0])

# Stop basic awareness so that nao doesn't move his head when not commanded 
nao.set_awareness(False)
# Look front for finding qrs
nao.look_at(0, -2)

sensing_list = [CloseToGoalSensor(nao, goals_positions, goals_directions), GoCommandSensor(nao, simulation)]
module_list = [LedsModule(nao), MoveModule(nao)]

# Load and start automata
automata = Automata(module_list, shared_memory, verbose=True)
automata.load_automata_from_file("workspace/missions/go_to_goal_mission/automata.txt")
automata.start()

dt_seconds = 0.1
t1 = time.time()
interval = 0

while 1:
    # Sensing
    for sensor in sensing_list:
        sensor.sense()

    # Calculate time until next interval and sleep
    interval += 1
    t2 = time.time()

    sleep_time = t1 + interval*dt_seconds - t2
    if sleep_time > 0:
        time.sleep(sleep_time)
    else:
        LOGGER.warn("Took to long sensing!")

    if t2 - t1 > 180:
        shared_memory.add_message("exit")