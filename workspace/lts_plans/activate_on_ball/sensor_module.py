class SensorModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["sensar"]

    def sensar(self):
        if self.nao.ball_is_in_vision():
            self.nao.shared_memory.add_message("vi_pelota")
        else:
            self.nao.shared_memory.add_message("no_vi_pelota")
