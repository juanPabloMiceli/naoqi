import time
from redis import Redis

import numpy as np
from workspace.automata.planner_automata import Automata
from workspace.missions.talk_postures_mission.user_request_sensor import (
    UserRequestSensing,
)
from workspace.missions.talk_postures_mission.talk_module import TalkModule
from workspace.missions.talk_postures_mission.postures_module import PosturesModule
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.logger_factory import LoggerFactory
from workspace.utils.nao_factory import NaoFactory

LOGGER = LoggerFactory.get_logger("main")

shared_memory = NaoSharedMemory()
nao = NaoFactory.create(shared_memory)

redis = Redis("127.0.0.1", 6379, 0)
redis.set("command_type", "chat")

# fail if no talking services are working
# TODO

sensing_list = [UserRequestSensing(nao, redis)]
module_list = [TalkModule(nao), PosturesModule(nao)]

# Load and start automata
automata = Automata(module_list, shared_memory, verbose=True)
automata.load_automata_from_file(
    "workspace/missions/talk_postures_mission/automata.txt"
)
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

    sleep_time = t1 + interval * dt_seconds - t2
    if sleep_time > 0:
        time.sleep(sleep_time)
    else:
        LOGGER.warn("Took to long sensing!")

    if t2 - t1 > 60:
        shared_memory.add_message("exit")
