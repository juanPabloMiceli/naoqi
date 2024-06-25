import time

from workspace.automata.planner_automata import Automata
from workspace.lts_plans.nao_lights.leds_module import LedsModule
from workspace.lts_plans.nao_lights.wait_module import WaitModule
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.logger_factory import LoggerFactory
from workspace.utils.nao_factory import NaoFactory

LOGGER = LoggerFactory.get_logger("main")

shared_memory = NaoSharedMemory()
nao, simulation = NaoFactory.create(shared_memory)

sensing_list = []
module_list = [WaitModule(nao), LedsModule(nao)]

# Load and start automata
automata = Automata(module_list, shared_memory, verbose=True)
automata.load_automata_from_file("workspace/lts_plans/nao_lights/automata.fsp")
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
