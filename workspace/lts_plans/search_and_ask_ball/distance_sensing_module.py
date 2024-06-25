class DistanceSensingModule():
    def __init__(self, nao, sensing_dict):
        self.nao = nao
        self.controllables = ["sensar_distancia"]
        self.sensing_dict = sensing_dict

    def sensar_distancia(self):
        self.sensing_dict["ball_proximity_sensor"][1] = True
