import sys
import time
# from workspace.location.qr_detector import QrDetector
from workspace.utils.geometry import distance, direction
from workspace.naoqi_custom.proxy_factory import ProxyFactory
from workspace.naoqi_custom.nao_properties import NaoProperties
from naoqi import qi
import numpy as np
from threading import Thread

'''
Estrategia de movimiento:
    Supongamos que estamos en (Xs, Ys) y queremos ir a (Xe, Ye).

    1. Si estamos "cerca" de (Xe, Ye), terminamos, si no, ir al paso 2. 
    2. Conseguir el vector resultante de ir desde (Xs, Ys) hasta (Xe, Ye), llamemoslo 'v'.
    3. 
        * Si el angulo entre el pecho del Nao y 'v' es "chico", caminar "un poco" e ir al paso 1.
        * Si no, ir al paso 4.
    4. Girar el pecho del Nao hasta que el angulo formado entre su cuerpo y el vector 'v' sea lo suficientemente chico.
    5. Ir al paso 1.
'''
class MovementController(Thread):

    def __init__(self, ip, port, memory):
        self.motion_proxy = ProxyFactory.get_proxy("ALMotion", ip, port)
        self.motion_proxy.wakeUp()
        while not self.motion_proxy.robotIsWakeUp():
            continue
        self.memory = memory
        self.target_position = None
        self.acceptable_error_radius = 50
        self.acceptable_error_angle = np.radians(10)

    '''
    Goes to the position stored in self.target_position asynchronously. Fails if target_position is None. 
    When NAO reaches target it clears target_position in order to avoid people forget setting the position before
    starting the thread.
    '''
    def run(self):
        nao_position = self.memory.get_nao_position()
        nao_direction = self.memory.get_nao_direction()
        while not _close_enough(nao_position):
            torso_to_target_angle = self._get_angle(nao_position, nao_direction)
            if abs(torso_to_target_angle) < self.acceptable_error_angle:
                self.motion_proxy.move(0.5, 0, 0)
            else:
                # Rotate based on torso_to_target_angle
                pass

            nao_position = self.memory.get_nao_position()
            nao_direction = self.memory.get_nao_direction()

    def set_target(self, target_position):
        self.target_position = target_position

    def go_to(self, target_location):
        nao_location = self.locator_and_mapper.get_nao_location()
        if self._close_enough(nao_location, target_location):
            return True
        target_direction = direction(nao_location, target_location)

    def _close_enough(self, nao_position, target_position):
        return distance(nao_position, target_position) < self.acceptable_error_radius

    def walk_forward(self):
        self.motion_proxy.move(1, 0, 0)

    def walk_backward(self):
        self.motion_proxy.move(-0.2, 0, 0)

    def non_walk(self):
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



if __name__ == "__main__":
    
    IP, PORT = NaoProperties().get_connection_properties()

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    movement_controller = MovementController(IP, PORT, None)

    start = time.time()

    while True:
        stop = time.time()
        if stop - start < 10:
            movement_controller.walk_forward()
        elif stop - start < 15:
            movement_controller.rotate_clockwise()
        elif stop - start < 20:
            movement_controller.rotate_counter_clockwise()
        else:   
            movement_controller.rest()
            break


