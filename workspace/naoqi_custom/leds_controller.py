import time

from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties

from workspace.naoqi_custom.proxy_factory import ProxyFactory


class LedsController:
    def __init__(self, ip, port):
        self.LOGGER = LoggerFactory.get_logger("LedsController")
        self.proxy = ProxyFactory.get_proxy("ALLeds", ip, port)
        self.group = "BrainLeds"

    def off(self):
        self.LOGGER.info("Turning off leds [{}]".format(self.group))
        self.proxy.off(self.group)

    def on(self):
        self.LOGGER.info("Turning on leds [{}]".format(self.group))
        self.proxy.on(self.group)

if __name__ == "__main__":
    IP, PORT = NaoProperties().get_connection_properties()
    leds_controller = LedsController(IP, PORT)

    while True:
        leds_controller.on()
        time.sleep(1)
        leds_controller.off()
        time.sleep(1)
