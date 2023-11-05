from __future__ import absolute_import
import sys
import time
from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties
import qi

from workspace.naoqi_custom.leds_controller import LedsController

from workspace.blinking_leds_mission.sharedmem import SharedMem
from workspace.blinking_leds_mission.module_leds import ModuleLeds
from workspace.blinking_leds_mission.sensing_trivial import SensingTrivial
from workspace.blinking_leds_mission.planner_automata import Automata

LOGGER = LoggerFactory.get_logger("main")
def main(session, ip, port):
    # Instance Shared Memory
    memory = SharedMem()

    # Declare automata modules and sensors
    sensing_trivial = SensingTrivial(memory)
    module_leds = ModuleLeds(LedsController(ip, port))

    sensing_list = [sensing_trivial]
    module_list = [module_leds]

    # Load and start automata
    automata = Automata(module_list, memory, verbose=True)
    automata.load_automata_from_file("workspace/blinking_leds_mission/blinking_leds_automata.txt")
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

        if t2 - t1 > 10:
            memory.add_message("exit")


if __name__ == "__main__":
    __package__ = "trivial_mission.trivial_mission"
    IP, PORT = NaoProperties().get_connection_properties()

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, IP, PORT)
