import time

from workspace.automata.planner_automata import Automata
from workspace.lts_plans.simple_ball.leds_module import LedsModule
from workspace.lts_plans.simple_ball.sensor_module import SensorModule
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.logger_factory import LoggerFactory
from workspace.utils.nao_factory import NaoFactory
from workspace.naoqi_custom.red_ball_detection_module import RedBallDetectionModule

LOGGER = LoggerFactory.get_logger("main")
AUTOMATA_PATH = "workspace/lts_plans/activate_on_ball/automata.fsp"

shared_memory = NaoSharedMemory()
nao, simulation = NaoFactory.create(shared_memory)

from workspace.naoqi_custom.red_ball_detection_module import RedBallDetectionModule
redBallModule = RedBallDetectionModule("redBallModule", nao)
nao.nao_memory.subscribeToEvent('redBallDetected', 'redBallModule', 'red_ball_detected')

sensing_list = []
module_list = [SensorModule(nao), LedsModule(nao)]

# Load and start automata
automata = Automata(module_list, shared_memory, verbose=True)
automata.load_automata_from_file(AUTOMATA_PATH)
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
