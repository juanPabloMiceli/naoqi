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

from workspace.naoqi_custom.nao_properties import NaoProperties


class AwarenessController:
    """
    The AwarnessController controls whether the NAO is on the aware or still state.

    On the aware state: The NAO is constantly moving and performing acts of detection.
    On the still state: The NAO stays in a motionless state, fixed state and only moves on command.
    """

    def __init__(self, session):
        # type: (qi.Session) -> AwarenessController

        # subscribe to the awareness service for the NAO
        self.basic_awareness_service = session.service("ALBasicAwareness")

        # subscribe to the motion control service for the NAO
        self.background_movement_service = session.service("ALMotion")

    def set(self, new_state):
        # type: (bool) -> None
        """
        Sets the awareness to the received boolean value

        Parameters
        ----------
        new_state: bool
            The new state to set up on the NAO
        """
        # if new_state is True, then send the start awareness signal to the NAO
        # else send the stop awareness signal to the NAO
        self.basic_awareness_service.startAwareness() if new_state else self.basic_awareness_service.stopAwareness()

        # set the backgroung motion of breathing (naturally moving like it lives) to the new state
        # note that "All" is used, this means a complete body motion will be executed
        self.background_movement_service.setBreathEnabled("All", new_state)

    def get(self):
        # type: () -> bool
        """
        Get the current awareness state of the NAO

        Returns
        -------
        bool
            The current awareness state of the NAO
        """
        return self.basic_awareness_service.is_enabled()


if __name__ == "__main__":
    # if executed as a script, the following code will allow to send the option
    # --disable or --enable to set the awareness state fo the NAO
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--state", type=bool, default=False
    )  # Do not pass this argument directly, pass either --enable or --disable
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--enable", dest="state", action="store_true")
    group.add_argument("--disable", dest="state", action="store_false")
    args = parser.parse_args()

    # save the pass parameter as a variable
    STATE = args.state

    # get the NAO connections settings
    IP, PORT = NaoProperties().get_connection_properties()

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print(
            "Can't connect to Naoqi at ip \"" + IP + '" on port ' + str(PORT) + ".\n"
            "Please check your script arguments. Run with -h option for help."
        )
        sys.exit(1)

    # finally, set the state on the controller
    AwarenessController(session).set(STATE)
