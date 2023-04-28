import argparse
import math
import sys
import time

import qi

from workspace.naoqi_custom.nao_properties import NaoProperties


class HeadController:
    """
    Controls the head of the Nao robot by rotating it in x and y axes.

    Attributes:
    -----------
    max_left : float
        The maximum angle the head can rotate to the left in degrees
    max_right : float
        The maximum angle the head can rotate to the right in degrees
    max_down : float
        The maximum angle the head can rotate downwards in degrees
    max_up : float
        The maximum angle the head can rotate upwards in degrees

    Methods
    -------
    look_at(angle_x: float, angle_y: float) -> None
        Sets the head of the NAO to the indicated angles
    """

    max_left = -119.5
    max_right = 119.5

    max_down = -29.5
    max_up = 38.5

    def __init__(self, session):
        # type (qi.Session) -> None
        """
        Initializes the HeadController object.

        Parameters:
        ----------
        session : qi.Session
            The session object used to connect to the robot's Naoqi API.
        """
        # subscribes to the motion service
        self.service = session.service("ALMotion")

    def __min_max(self, val, min_thresh, max_thresh):
        # type (float, float, float) -> float
        """
        Ensures that the given value is within the given min and max thresholds.
        Returns either the minimium of maximun value if the threshold is exeeded

        Parameters:
        ----------
        val : float
            The value to be checked.
        min_thresh : float
            The minimum threshold that the value can have.
        max_thresh : float
            The maximum threshold that the value can have.

        Returns:
        -------
        float:
            The value, if it is within the given min and max thresholds. If it is less than the
            minimum threshold, the minimum threshold is returned. If it is greater than the maximum
            threshold, the maximum threshold is returned.
        """
        return max(min(val, max_thresh), min_thresh)

    def __correct_x_angle(self, angle):
        # type (float) -> float
        """
        Ensures that the given x-axis angle is within the robot's maximum left and right
        rotation limits.

        Parameters:
        ----------
        angle : float
            The x-axis angle in degrees.

        Returns:
        -------
        float:
            The angle, if it is within the robot's maximum left and right rotation limits. If it
            is less than the maximum left limit, the maximum left limit is returned. If it is
            greater than the maximum right limit, the maximum right limit is returned.
        """
        return self.__min_max(angle, self.max_left, self.max_right)

    def __correct_y_angle(self, angle):
        # type (float) -> float
        """
        Ensures that the given y-axis angle is within the robot's maximum down and up rotation
        limits.

        Parameters:
        ----------
        angle : float
            The y-axis angle in degrees.

        Returns:
        -------
        float:
            The angle, if it is within the robot's maximum down and up rotation limits. If it is
            less than the maximum down limit, the maximum down limit is returned. If it is greater
            than the maximum up limit, the maximum up limit is returned.
        """
        return self.__min_max(angle, self.max_down, self.max_up)

    def look_at(self, angle_x, angle_y):
        # type: (float, float) -> None
        """
        Sets the head of the NAO to the indicated angles.

        Parameters
        ----------
        angle_x : float
            The angle to rotate the head horizontally (in degrees)
        angle_y : float
            The angle to rotate the head vertically (in degrees)
        """
        # set the resistance that the head will make upon movement
        self.service.setStiffnesses("Head", 1.0)

        # the following refer to joints (AKA movement points) on the robot as detailed on the NAO's documentation
        joint_names = ["HeadYaw", "HeadPitch"]

        # cast the angles of the joints to radians
        joint_angles = [
            math.radians(-self.__correct_x_angle(angle_x)),
            math.radians(-self.__correct_y_angle(angle_y)),
        ]

        # set the speed that the robot will use to move the head
        speed = 0.25

        # Interpolate the joint angles at a given speed.
        # Repeat the command twice to ensure the robot actually moves.
        self.service.angleInterpolationWithSpeed(joint_names, joint_angles, speed)
        self.service.angleInterpolationWithSpeed(joint_names, joint_angles, speed)

    def look_front(self):
        # type: () -> None
        """
        Sets the head of the NAO to look straight ahead.
        Looks directly in front of its chest, with his eyesight in parallel with the floor.
        """
        self.look_at(0, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--x",
        type=float,
        default=0.0,
        help="Angle in degrees for moving the nao's head left to right. Range: [-119.5, 119.5]",
    )
    parser.add_argument(
        "--y",
        type=float,
        default=0.0,
        help="Angle in degrees for moving the nao's head bottom to top. Range: [-29.5, 38.5]",
    )
    args = parser.parse_args()
    X, Y = args.x, args.y
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

    head_controller = HeadController(session)
    head_controller.look_at(X, Y)
