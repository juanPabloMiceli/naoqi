# This test degrees(alpha) how to use the ALLandMarkDetection module.
# - We first instantiate a proxy to the ALLandMarkDetection module
#     Note that this module should be loaded on the robot's NAOqi.
#     The module output its results in ALMemory in a variable
#     called "LandmarkDetected"
# - We then read this AlMemory value and check whether we get
#   interesting things.

import qi
import sys
import argparse

from nao_properties import NaoProperties

class AwarenessController:
    
    def __init__(self, session):
        self.service = session.service("ALBasicAwareness")
    
    def set(self, new_state):
        self.service.startAwareness() if new_state else self.service.stopAwareness() 
    
    def get(self):
        return self.service.is_enabled()
            

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--state', type=bool, default=False) # Do not pass this argument directly, pass either --enable or --disable
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--enable', dest='state', action='store_true')
    group.add_argument('--disable', dest='state', action='store_false')
    args = parser.parse_args()

    STATE = args.state
    IP, PORT = NaoProperties().get_connection_properties()
    

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    AwarenessController(session).set(STATE)