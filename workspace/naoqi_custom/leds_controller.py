
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

    def on(self, group):
        self.LOGGER.info(f'Turning on {group} leds')
        self.proxy.on(group)
    
    def off(self, group):
        self.LOGGER.info(f'Turning off {group} leds')
        self.proxy.off(group)

    def fade(self, group = 'FaceLeds', color = 'white'):
        self.LOGGER.info(f"Setting {group} {color}")
        self.proxy.fadeRGB(group, color, 0.0)