class LedsModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["luces_on"]

    def luces_on(self):
        self.nao.head_leds_on()
