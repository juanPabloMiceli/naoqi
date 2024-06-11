
import time

from workspace.utils.logger_factory import LoggerFactory
from workspace.properties.nao_properties import NaoProperties

from workspace.naoqi_custom.proxy_factory import ProxyFactory


class LedsController:
    
    class SUPPORTED_COLORS:
        WHITE = 'white'
        RED = 'red'
        GREEN = 'green'
        BLUE = 'blue'
        YELLOW = 'yellow'
        MAGENTA = 'magenta'
        CYAN  = 'cyan'
    
    class SUPPORTED_GROUPS:
        ALL = 'AllLeds'
        BRAIN = 'BrainLeds'
        EYES = 'FaceLeds'
        EARS = 'EarLeds'
        FEET = 'FeetLeds'
        
    def __init__(self, ip, port):
        self.LOGGER = LoggerFactory.get_logger("LedsController")
        self.proxy = ProxyFactory.get_proxy("ALLeds", ip, port)

    def on(self, group = 'BrainLeds'):
        self.LOGGER.info('Turning on {} leds'.format(group))
        self.proxy.on(group)
    
    def off(self, group = 'BrainLeds'):
        self.LOGGER.info('Turning off {} leds'.format(group))
        self.proxy.off(group)

    def fade(self, group = 'FaceLeds', color = 'white'):
        self.LOGGER.info("Setting {} {}".format(group, color))
        self.proxy.fadeRGB(group, color, 0.0)
