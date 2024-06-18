class SearchBallModule():
    def __init__(self, nao, sensors_dict):
        self.nao = nao
        self.controllables = ["perfilar"]
        self.sensors_dict = sensors_dict

    def perfilar(self):
        self.nao.rotate_counter_clockwise()
        self.sensors_dict["search_ball_sensor"][1] = True
        self.sensors_dict["search_ball_sensor"][0].start_search()
