import time
class AskModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["pedir", "no_operation"]

    def pedir(self):
        self.nao.stop_moving()
        time.sleep(2)
        self.nao.head_leds_on()
        self.nao.say("Give me the ball!")

    def no_operation(self):
        pass
