import sys
import time
import qi
from workspace.location.qr_detector import QrDetector
from workspace.properties.nao_properties import NaoProperties
from workspace.naoqi_custom.proxy_factory import ProxyFactory
from workspace.naoqi_custom.leds_controller import LedsController
from workspace.naoqi_custom.awareness_controller import AwarenessController
from workspace.naoqi_custom.video_controller import VideoController
from workspace.naoqi_custom.head_controller import HeadController
from workspace.naoqi_custom.motion_controller import MotionController
from workspace.naoqi_custom.talk_controller import TalkController
from workspace.naoqi_custom.postures_controller import PosturesController
from workspace.location.locator_and_mapper import LocatorAndMapper
from workspace.utils.qr_decoder import QrDecoder


class Nao:
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory
        self.ip, self.port = NaoProperties().get_connection_properties()
        self.session = self.__start_session()
        self.leds_controller = LedsController(self.ip, self.port)
        self.awareness_controller = AwarenessController(self.session)
        self.awareness_controller.set(False)
        self.broker = ALBroker('broker', '0.0.0.0', 0, self.ip, self.port)
        self.nao_memory = self.session.service('ALMemory')
        self.video_controller = VideoController(self.ip, self.port)
        self.head_controller = HeadController(self.session)
        self.movement_controller = MotionController(self.ip, self.port, None)
        self.position_updater = LocatorAndMapper(shared_memory, self)
        self.talk_controller = TalkController(self.ip, self.port)
        self.posture_controller = PosturesController(self.session)

        self.last_ball_detected = time.time() - NaoProperties.seen_ball_time_of_grace()


    def __start_session(self):
        session = qi.Session()
        try:
            session.connect("tcp://" + self.ip + ":" + str(self.port))
        except RuntimeError:
            print(
                "Can't connect to Naoqi at ip \""
                + self.ip
                + '" on port '
                + str(self.port)
                + ".\n"
                "Please check your script arguments. Run with -h option for help."
            )
            sys.exit(1)
        return session

    def sit(self):
        self.posture_controller.sit()

    def lay(self):
        self.posture_controller.lying_belly()

    def stand(self):
        self.posture_controller.stand()

    def say(self, sentence):
        self.talk_controller.say(sentence)

    def end_talk(self):
        self.talk_controller.end_talk()

    def start_talk(self):
        self.talk_controller.start_talk()

    def head_leds_on(self):
        self.leds_controller.on()

    def head_leds_off(self):
        self.leds_controller.off()

    def set_awareness(self, new_awareness):
        self.awareness_controller.set(new_awareness)

    def get_frame(self):
        return self.video_controller.get_current_gray_image()

    def look_at(self, x_angle_degrees, y_angle_degrees):
        self.head_controller.look_at(x_angle_degrees, y_angle_degrees)

    def walk_forward(self):
        self.movement_controller.walk_forward()

    def stop_moving(self):
        self.movement_controller.stop_moving()

    def walk_backward(self):
        self.movement_controller.walk_backward()

    def rest(self):
        self.movement_controller.rest()

    def rotate_counter_clockwise(self):
        self.movement_controller.rotate_counter_clockwise()

    def rotate_clockwise(self):
        self.movement_controller.rotate_clockwise()

    def debug_qrs(self):
        while True:
            gray_image = self.get_frame()
            qrs_data = QrDecoder.decode(gray_image)
            print("QRs decoded, I found {} of them.\n".format(len(qrs_data)))
            for qr_data in qrs_data:
                print(qr_data)

    def get_qrs_in_vision(self):
        return QrDetector.get_qrs_information(self.get_frame())

    def ball_detected(self, distance, horizontal_angle_degrees, vertical_angle_degrees):
        self.last_ball_detected = time.time()
        self.shared_memory.set_new_ball(distance, horizontal_angle_degrees, vertical_angle_degrees)

    def get_ball_info(self):
        now = time.time()
        if self.__ball_is_in_vision():
            return self.shared_memory.get_latest_ball_info()
        return None

    def __ball_is_in_vision(self):
        return (time.time() - self.last_ball_detected) < NaoProperties.seen_ball_time_of_grace()

    def debug_red_ball_detection(self):
        while True:
            detected_ball_info = self.get_ball_info()
            if detected_ball_info is not None:
                distance, horizontal_angle, vertical_angle = detected_ball_info
                horizontal_side = "right" if horizontal_angle > 0 else "left"
                vertical_side = "up" if vertical_angle > 0 else "down"
                print("Ball detected: {}cm away, {}º {} and {}º {}".format(distance, horizontal_angle, horizontal_side, vertical_angle, vertical_side))
