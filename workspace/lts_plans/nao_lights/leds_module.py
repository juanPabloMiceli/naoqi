class LedsModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["luces_cabeza_on", "luces_cabeza_off"]

    def luces_cabeza_on(self):
        print("Prendiendo luces")
        self.nao.head_leds_on()

    def luces_cabeza_off(self):
        self.nao.head_leds_off()
