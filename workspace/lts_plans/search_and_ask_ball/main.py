import time

from workspace.lts_plans.search_and_ask_ball.ball_proximity_sensor import BallProximitySensor
from workspace.lts_plans.search_and_ask_ball.ask_module import AskModule
from workspace.lts_plans.search_and_ask_ball.distance_sensing_module import DistanceSensingModule
from workspace.lts_plans.search_and_ask_ball.moving_module import MovingModule
from workspace.lts_plans.search_and_ask_ball.search_ball_sensor import SearchBallSensor
from workspace.lts_plans.search_and_ask_ball.search_ball_module import SearchBallModule

from workspace.automata.planner_automata import Automata
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.logger_factory import LoggerFactory
from workspace.utils.nao_factory import NaoFactory

AUTOMATA_PATH = "workspace/lts_plans/search_and_ask_ball/automata.fsp"
LOGGER = LoggerFactory.get_logger("main")

shared_memory = NaoSharedMemory()
nao, simulation = NaoFactory.create(shared_memory)

nao.head_leds_off()
nao.look_at(0, 10)

from workspace.naoqi_custom.red_ball_detection_module import RedBallDetectionModule
redBallModule = RedBallDetectionModule("redBallModule", nao)
nao.nao_memory.subscribeToEvent('redBallDetected', 'redBallModule', 'red_ball_detected')

sensing_dict = {
        "ball_proximity_sensor": BallProximitySensor(nao),
        "search_ball_sensor": SearchBallSensor(nao),
        }
module_list = [AskModule(nao), DistanceSensingModule(nao, sensing_dict), MovingModule(nao), SearchBallModule(nao, sensing_dict)]

# Load and start automata
automata = Automata(module_list, shared_memory, verbose=True)
automata.load_automata_from_file(AUTOMATA_PATH)
automata.start()

dt_seconds = 0.5
t1 = time.time()
interval = 0

while 1:
    # Sensing
    for sensor in sensing_dict.values():
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
