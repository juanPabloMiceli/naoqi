import time

from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties

from workspace.naoqi_custom.proxy_factory import ProxyFactory


class LedsController:
    """
    Provides a simple API to control the LEDs on the robot's head.

    Attributes
    ----------
    LOGGER : logging.Logger
        The logger instance for this class.
    proxy : ALLeds
        The proxy instance to control the LEDs on the robot's head.
    group : str
        The name of the LED group to control.

    Methods
    -------
    off()
        Sets the leds off
    on()
        Sets the leds on
    """

    def __init__(self, ip, port):
        # type: (str, int) -> None
        """
        Initializes a new instance of `LedsController`.

        Parameters
        ----------
        ip : str
            The IP address of the robot.
        port : int
            The port number to connect to the robot.

        """
        self.LOGGER = LoggerFactory.get_logger("LedsController")
        self.proxy = ProxyFactory.get_proxy("ALLeds", ip, port)
        self.group = "BrainLeds"

    def off(self):
        # type: () -> None
        """
        Turns off the LEDs on the robot's head.

        """
        self.LOGGER.info("Turning off leds [{}]".format(self.group))
        self.proxy.off(self.group)

    def on(self):
        # type: () -> None
        """
        Turns on the LEDs on the robot's head.

        """
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
