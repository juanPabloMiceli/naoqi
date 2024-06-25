import time
from workspace.properties.nao_properties import NaoProperties

class SearchBallSensor():

    OK = "ok"
    NOT_OK = "not_ok"
    WAITING = "waiting"

    def __init__(self, nao):
        self.nao = nao
        self.search_start_time = time.time()

    def sense(self):
        ball_info = self.nao.get_ball_info()
        ball_status = self.get_new_ball_status(ball_info)
        if ball_status == self.WAITING:
            return False

        self.nao.shared_memory.add_message(ball_status)
        return True

    def get_new_ball_status(self, ball_info):
        if ball_info is None:
            if time.time() - self.search_start_time > 10:
                return self.NOT_OK
            return self.WAITING
        return self.OK
        # if abs(ball_info[1]) < 10:
        #     return self.OK
        # return self.WAITING

    def start_search(self):
        self.search_start_time = time.time()
