import time

import numpy as np
from workspace.automata.planner_automata import Automata
from workspace.missions.go_to_goal_mission.close_to_goal_sensor import CloseToGoalSensor
from workspace.missions.go_to_goal_mission.leds_module import LedsModule
from workspace.missions.go_to_goal_mission.move_module import MoveModule
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.logger_factory import LoggerFactory
from workspace.utils.nao_factory import NaoFactory

LOGGER = LoggerFactory.get_logger("main")

shared_memory = NaoSharedMemory()
nao = NaoFactory.create(shared_memory)

goal_position = np.array([80, 100])
goal_direction_degrees = 180
nao.new_goal(goal_position, goal_direction_degrees)

# Stop basic awareness so that nao doesn't move his head when not commanded 
nao.set_awareness(False)
# Look front for finding qrs
nao.look_at(0, -2)

sensing_list = [CloseToGoalSensor(nao, goal_position, goal_direction_degrees)]
module_list = [LedsModule(nao), MoveModule(nao, goal_position, goal_direction_degrees)]

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

    if t2 - t1 > 60:
        shared_memory.add_message("exit")