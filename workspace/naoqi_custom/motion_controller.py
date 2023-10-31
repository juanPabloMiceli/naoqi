from workspace.naoqi_custom.proxy_factory import ProxyFactory
from naoqi import qi
import numpy as np

class MotionController:

    def __init__(self, ip, port):
        self.motion_proxy = ProxyFactory.get_proxy("ALMotion", ip, port)
        self.motion_proxy.wakeUp()
        while not self.motion_proxy.robotIsWakeUp():
            continue

    def walk_forward(self):
        self.motion_proxy.move(1, 0, 0)

    def walk_backward(self):
        self.motion_proxy.move(-0.2, 0, 0)

    def stop_moving(self):
        self.motion_proxy.move(0, 0, 0)

    def rest(self):
        self.motion_proxy.rest()

    def rotate_counter_clockwise(self):
        self.motion_proxy.move(0,0,np.radians(90))

    def rotate_clockwise(self):
        self.motion_proxy.move(0,0,-np.radians(90))

    def is_awake(self):
        return self.motion_proxy.robotIsWakeUp()

    def awake(self):
        self.motion_proxy.wakeUp()
        while not self.motion_proxy.robotIsWakeUp():
            continue