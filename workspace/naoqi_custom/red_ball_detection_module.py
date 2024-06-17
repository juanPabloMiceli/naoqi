import math
from naoqi import ALModule

from workspace.properties.nao_properties import NaoProperties

class RedBallDetectionModule(ALModule):
    """ Red Ball Detection Module
    """
    def __init__(self, module_name, nao):
        self.name = module_name
        ALModule.__init__(self, self.name)
        self.nao = nao

    def red_ball_detected(self, event_name, value, identifier):
        """ Callback function
            This function will be called when a red ball is detected, if more than one
            red ball is detected in the same frame, the only ball to call the function
            is the biggest one.
        """
        ball_horizontal_angle = math.degrees(value[1][0])
        ball_vertical_angle = -math.degrees(value[1][1])
        ball_distance = NaoProperties.balls_diameter() / value[1][2]
        self.nao.ball_detected(ball_distance, ball_horizontal_angle, ball_vertical_angle)
