import sys
import time
import qi


from workspace.location.locator_and_mapper import LocatorAndMapper
from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.awareness_controller import AwarenessController
from workspace.naoqi_custom.head_controller import HeadController
from workspace.naoqi_custom.leds_controller import LedsController
from workspace.naoqi_custom.video_controller import VideoController

from workspace.trivial_location_mission.sharedmem import SharedMem
from workspace.trivial_location_mission.module_leds import ModuleLeds
from workspace.trivial_location_mission.sensing_position import SensingPosition
from workspace.trivial_location_mission.planner_automata import Automata

LOGGER = LoggerFactory.get_logger("main")
def main(session, ip, port):
    # Stop basic awareness so that nao doesn't move his head when not commanded 
    AwarenessController(session).set(False)

    # Look front for finding qrs
    head_controller = HeadController(session)
    head_controller.look_at(0, -2)

    memory = SharedMem()
    memory.set_goal_position([0, 0])

    # Start position module in a new thread.
    locator_and_mapper = LocatorAndMapper(memory, VideoController(ip, port), 'workspace/trivial_location_mission/qrs_positions.json')
    locator_and_mapper.start()

    # Declare automata modules and sensors
    sensing_position = SensingPosition(memory, 100)
    module_leds = ModuleLeds(LedsController(ip, port))

    sensing_list = [sensing_position]
    module_list = [module_leds]

    # Load and start automata
    automata = Automata(module_list, memory, verbose=True)
    automata.load_automata_from_file("workspace/trivial_location_mission/automata.txt")
    automata.start()

    dt_seconds = 0.2
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

        # if t2 - t1 > 10:
        #     memory.add_message("exit")


if __name__ == "__main__":
    
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



