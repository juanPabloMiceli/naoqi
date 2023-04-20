import argparse
import math
import sys
import time

import qi

from workspace.naoqi_custom.nao_properties import NaoProperties


class HeadController:

    max_left = -119.5
    max_right = 119.5

    max_down = -29.5
    max_up = 38.5

    def __init__(self, session):
        self.service = session.service("ALMotion")

    def __min_max(self, val, min_thresh, max_thresh):
        return max(min(val, max_thresh), min_thresh)

    def __correct_x_angle(self, angle):
        return self.__min_max(angle, self.max_left, self.max_right)

    def __correct_y_angle(self, angle):
        return self.__min_max(angle, self.max_down, self.max_up)


    def look_at(self, angle_x, angle_y):
        '''
            Receives angle_x and angle_y in degrees and rotates nao's head.

            Range:

            -119.5 (full left) <= angle_x <= 119.5 (full right)

            -29.5 (full down) <= angle_y <= 38.5 (full up)

            This is a blocking function!
        '''
        self.service.setStiffnesses("Head", 1.0)
        joint_names = ["HeadYaw", "HeadPitch"]
        joint_angles = [math.radians(-self.__correct_x_angle(angle_x)), math.radians(-self.__correct_y_angle(angle_y))]
        speed = 0.25
        self.service.angleInterpolationWithSpeed(joint_names,joint_angles, speed)
        self.service.angleInterpolationWithSpeed(joint_names,joint_angles, speed)
        return True

    def look_front(self):
        self.look_at(0, 0)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=float, default=0.0,
                        help="Angle in degrees for moving the nao's head left to right. Range: [-119.5, 119.5]")
    parser.add_argument('--y', type=float, default=0.0,
                        help="Angle in degrees for moving the nao's head bottom to top. Range: [-29.5, 38.5]")
    args = parser.parse_args()
    X,Y = args.x, args.y
    IP, PORT = NaoProperties().get_connection_properties()

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    head_controller = HeadController(session)
    head_controller.look_at(X,Y)
