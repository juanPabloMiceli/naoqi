import time
from workspace.lts_plans.search_and_ask_ball.sensor import Sensor

class SearchBallSensor(Sensor):

    OK = "ok"
    NOT_OK = "not_ok"
    WAITING = "waiting"

    def __init__(self, nao):
        super(SearchBallSensor, self).__init__(nao)
        self.search_start_time = time.time()

    def on_enable(self):
        self.search_start_time = time.time()

    def _sense_impl(self):
        ball_info = self.nao.get_ball_info()
        ball_status = self.get_new_ball_status(ball_info)
        if ball_status == self.WAITING:
            return False # stay enabled

        self.nao.shared_memory.add_message(ball_status)
        return True # disable when done

    def get_new_ball_status(self, ball_info):
        if ball_info is None:
            if time.time() - self.search_start_time > 10:
                return self.NOT_OK
            return self.WAITING
        return self.OK

