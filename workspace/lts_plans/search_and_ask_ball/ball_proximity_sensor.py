from workspace.properties.nao_properties import NaoProperties
from workspace.lts_plans.search_and_ask_ball.sensor import Sensor

class BallProximitySensor(Sensor):

    LEJOS = "lejos"
    CERCA = "cerca"

    def _sense_impl(self):
        ball_info = self.nao.get_ball_info()
        ball_status = self.get_new_ball_status(ball_info)
        self.nao.shared_memory.add_message(ball_status)
        return True  # disable after one sensing

    def get_new_ball_status(self, ball_info):
        if ball_info is None:
            return self.LEJOS
        distance = ball_info[0]
        if distance > NaoProperties.ball_reachable_distance():
            return self.LEJOS
        return self.CERCA

