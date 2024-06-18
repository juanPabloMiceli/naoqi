class AskModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["pedir", "no_operation"]
        self.first_time = True

    def pedir(self):
        self.nao.say("Give me the ball!")

    def no_operation(self):
        if self.first_time:
            self.nao.stop_moving()
            self.nao.head_leds_on()
            self.first_time = False
