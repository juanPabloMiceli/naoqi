
class ModuleLeds():
    def __init__(self, leds_controller):
        self.leds_controller = leds_controller
        self.controllables = ["on", "off"]

    def on(self):
        self.leds_controller.on()

    def off(self):
        self.leds_controller.off()
