class LedsModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["on", "off"]

    def on(self):
        self.nao.head_leds_on()

    def off(self):
        self.nao.head_leds_off()
