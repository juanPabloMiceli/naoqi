import time
import sys
import urllib2
import json
import urllib
from redis import Redis
from time import sleep
import inspect
import string

from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.proxy_factory import ProxyFactory

from naoqi import ALModule, ALBroker

import qi


def remove_non_ascii_letters(input_string, leave_dots_and_commas=False):
    # Create a string of all ASCII letters
    ascii_letters = string.ascii_letters

    if leave_dots_and_commas:
        ascii_letters += [".", "'", ",", ":", "\n"]

    # Filter out characters that are not ASCII letters
    filtered_string = "".join(char for char in input_string if char in ascii_letters)

    return filtered_string


LOOK_TIMEOUT = 20  # seconds

postures_vocabularies = {
    "Stand": ["stand"],
    "Sit": ["sit"],
    "LyingBelly": ["lay"],
    "Crouch": ["crouch"],
    "LyingBack": ["lay back"],
    "SitRelax": ["sit relax"],
}


class CommandController(ALModule):
    def __init__(self, ip, port, session, command_type):
        self.name = "commandController"
        ALModule.__init__(self, self.name)
        self.LOGGER = LoggerFactory.get_logger("CommandController")
        self.modules = []

        self.awareness = session.service("ALBasicAwareness")
        self.modules.append((self.awareness, "stopAwareness"))

        self.people_perception = session.service("ALPeoplePerception")
        # self.modules.append((self.people_perception, ""))

        # self.face_detection = session.service("ALFaceDetection")
        # self.modules.append((self.face_detection, ""))

        # self.animation_player = session.service("ALAnimationPlayer")
        # self.wave_detection = session.service("ALWavingDetection")
        self.text_to_speech = session.service("ALTextToSpeech")
        # self.modules.append((self.text_to_speech, ""))

        self.speech_recognition = session.service("ALSpeechRecognition")
        self.modules.append((self.speech_recognition, ""))

        # self.sound_detection = session.service("ALSoundDetection")
        # self.modules.append((self.sound_detected, ""))

        self.posture_manager = session.service("ALRobotPosture")
        self.modules.append((self.posture_manager, "stopMove"))

        # self.LOGGER.info(self.posture_manager.getPostureList())
        self.animated_speech = session.service("ALAnimatedSpeech")
        # self.modules.append((self.animated_speech, ""))

        self.memory = session.service("ALMemory")
        self.modules.append((self.memory, "unregisterModuleReference"))

        self.motion = session.service("ALMotion")
        self.modules.append((self.animated_speech, "rest"))

        self.redis = Redis(host="nao-redis", port=6379, db=0)
        self.command_type = command_type
        self.redis.set("command_type", command_type)

    def start_awareness(self):
        self.motion.wakeUp()

        # start the awareness of the NAO
        self.LOGGER.info("Starting greeting awareness")
        self.awareness.startAwareness()

        # enable people detection only
        self.LOGGER.info("Allowing people detection")
        self.awareness.setStimulusDetectionEnabled("People", True)

        # set the engament mode to fully engaged to avoid dsitractions
        self.LOGGER.info("Using full engagement mode")
        self.awareness.setEngagementMode("FullyEngaged")

        # set the tracking mode to whole body to be able to follow the people it interacts with
        self.LOGGER.info("Using head movement for engagement")
        self.awareness.setTrackingMode("BodyRotation")

        # set the speech recognition variables
        self.speech_recognition.setLanguage("English")
        self.speech_recognition.setAudioExpression(False)
        self.speech_recognition.setVisualExpression(False)
        self.animated_speech.setBodyLanguageModeFromStr("disabled")

        # set a name for the audo files
        self.redis.set("speech_tag", "nao_audio")
        # self.allow_gaze_recgonition(True)
        # self.allow_speech_recgonition(True)

        while True:
            if self.command_type == "postures":
                self.text_to_speech.say(
                    "Please tell me what posture you would like me to do."
                )
            self.redis.set("avoid_hearing", 0)

            while self.redis.get("gpt_response") is None:
                sleep(0.2)

            self.LOGGER.info("Has GPT response")

            self.redis.set("avoid_hearing", 1)

            response = self.redis.get("gpt_response").decode("utf-8")
            if self.command_type == "postures":
                self.manage_posture_command(response)
            elif self.command_type == "talk":
                self.manage_talk_response(response)
            else:
                self.LOGGER.info("Unknown method to manage")

            self.redis.delete("gpt_response")

    def manage_posture_command(self, response):
        response = remove_non_ascii_letters(response)

        self.LOGGER.info("Received command: {}".format(response))

        # execute pose
        if response in postures_vocabularies.keys():
            self.text_to_speech.say("Yes, I'm going to {}.".format(response))
            self.posture_manager.goToPosture(response, 1)
        else:
            self.text_to_speech.say(
                "Sorry, I didn't recognize the posture you requested."
            )

    def manage_talk_response(self, response):
        response = remove_non_ascii_letters(response, leave_dots_and_commas=True)

        self.LOGGER.info("Received response: {}".format(response))

        self.text_to_speech.say(response.encode("utf-8", errors="ignore"))

    def stop_awareness(self):
        # start the awareness of the NAO
        self.LOGGER.info("Stopping awareness")
        self.allow_gaze_recgonition(False)
        self.allow_speech_recgonition(False)
        name = self.getName()
        try:
            self.speech_recognition.unsubscribe(name)
        except RuntimeError:
            pass
        self.awareness.stopAwareness()
        self.posture_manager.stopMove()
        try:
            self.memory.unregisterModuleReference(name)
        except RuntimeError:
            pass
        self.motion.rest()

    def speech_change_detected(self, event_name, status, sub_identifier):
        self.LOGGER.info("Speech status changed")
        self.logger.info("new status is {}".format(status))
        if status == "SpeechDetected":
            self.redis.set("speech_detected", 1)
        else:  # if status == "Idle":
            self.redis.set("speech_detected", 0)

    def looked_at(self, event_name, id_list, sub_identifier):
        self.LOGGER.info("People looking at the NAO changed")
        people_looking_at_the_nao = len(id_list)
        self.logger.info(
            "The people lokking at the NAO are {}".format(people_looking_at_the_nao)
        )
        if people_looking_at_the_nao > 0:
            self.allow_speech_recgonition(True)
        elif people_looking_at_the_nao == 0:
            self.allow_speech_recgonition(False)
            self.redis.set("speech_detected", 0)

    def allow_speech_recgonition(self, allow):
        try:
            if allow:
                self.memory.subscribeToEvent(
                    "ALSpeechRecognition/Status",
                    self.getName(),
                    "speech_change_detected",
                )
            else:
                self.memory.unsubscribeToEvent(
                    "ALSpeechRecognition/Status", self.getName()
                )
        except RuntimeError:
            pass
        self.LOGGER.info("Speech recognition set to {}".format(str(allow)))

    def allow_gaze_recgonition(self, allow):
        try:
            if allow:
                self.memory.subscribeToEvent(
                    "GazeAnalysis/PeopleLookingAtRobot",
                    self.getName(),
                    "looked_at",
                )
            else:
                self.memory.unsubscribeToEvent(
                    "GazeAnalysis/PeopleLookingAtRobot",
                    self.getName(),
                )
        except RuntimeError:
            pass
        self.LOGGER.info("Gaze recognition set to {}".format(str(allow)))


if __name__ == "__main__":
    IP, PORT = NaoProperties().get_connection_properties()

    broker = ALBroker("broker", "0.0.0.0", 0, IP, PORT)

    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print("error :(")
        sys.exit(1)

    command_type = "talk"  # "postures"

    commandController = CommandController(IP, PORT, session, command_type)

    try:
        commandController.start_awareness()
    except Exception as e:
        commandController.LOGGER.info(e)
    finally:
        commandController.stop_awareness()
