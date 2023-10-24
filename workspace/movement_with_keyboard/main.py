import sys
import os
import time
from workspace.naoqi_custom.movement_controller import MovementController
from workspace.properties.nao_properties import NaoProperties
from naoqi import qi
from threading import Thread


class KeyboardController(Thread):
    def __init__(self, movement_controller):
        self.movement_controller = movement_controller
        self.shared_file = "workspace/movement_with_keyboard/shared.txt"
        self.last_accesed = time.time()

    def run(self):
        while True:
            if self.last_accesed < self._last_modified(self.shared_file):
                self.last_accesed = time.time()
            with open(self.shared_file, 'r') as f:
                f.seek(-2, 2)
                character = f.read(1)
                character = character.lower()
                if character == 'w':
                    self.movement_controller.walk_forward()
                    print("Arriba")
                elif character == 's':
                    self.movement_controller.walk_backward()
                    print("Abajo")
                elif character == 'a':
                    self.movement_controller.rotate_counter_clockwise()
                    print("Izquierda")
                elif character == 'd':
                    self.movement_controller.rotate_clockwise()
                    print("Derecha")
                elif character == 'z':
                    self.movement_controller.stop_moving()
                    print("STOP")
                elif character == 'q':
                    self.movement_controller.rest()
                    print("EXIT")
                    break
                else:
                    print("unknown character '{}'".format(character))


    def _last_modified(self, ff):
        modified_time = 0
        try:
            modified_time = os.path.getmtime(ff)
        except:
            modified_time = 0
        return modified_time

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

    keyboard_controller = KeyboardController(movement_controller)
    keyboard_controller.run()
