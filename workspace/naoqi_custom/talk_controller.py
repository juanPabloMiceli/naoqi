import time
import random
import string

from redis import Redis

from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties

from workspace.naoqi_custom.proxy_factory import ProxyFactory


def remove_non_ascii_letters(input_string, leave_dots_and_commas=False):
    # Create a string of all ASCII letters
    ascii_letters = string.ascii_letters

    if leave_dots_and_commas:
        for char in [".", "'", ",", ":", "\n", " ", "?"]:
            ascii_letters = ascii_letters + char

    # Filter out characters that are not ASCII letters
    filtered_string = "".join(char for char in input_string if char in ascii_letters)

    return filtered_string


class TalkController:
    def __init__(self, ip, port):
        self.LOGGER = LoggerFactory.get_logger("TalkController")
        self.proxy = ProxyFactory.get_proxy("ALTextToSpeech", ip, port)

        self.animated_speech_cfg = ProxyFactory.get_proxy("ALAnimatedSpeech", ip, port)
        self.animated_speech_cfg.setBodyLanguageModeFromStr("disabled")

        self.awareness = ProxyFactory.get_proxy("ALBasicAwareness", ip, port)

        self.redis_conn = Redis()

    def start_talk(self):
        # enable initiative tracking
        self.awareness.startAwareness()
        self.awareness.setStimulusDetectionEnabled("People", True)
        self.awareness.setEngagementMode("FullyEngaged")
        self.awareness.setTrackingMode("BodyRotation")

        # enable talk on redis
        self.redis_conn.set("avoid_hearing", 0)

        # another way could be to start an AudioInputManager on another docker container
        # this could be done via a script that reads the enable or disable key on redis
        # this script would start and end a process that handles the audio processing

    def end_talk(self):
        # disable talk on redis
        self.redis_conn.set("avoid_hearing", 1)

    def talk(self, sentence):
        self.LOGGER.info("Going to speak out loud")

        # read the desired sentence from redis
        sentence = remove_non_ascii_letters(sentence, leave_dots_and_commas=True)

        self.LOGGER.info('Going to say: "{}"'.format(sentence))

        self.proxy.say(sentence.encode("utf-8", errors="ignore"))


if __name__ == "__main__":
    IP, PORT = NaoProperties().get_connection_properties()
    talk_controller = TalkController(IP, PORT)

    redis = Redis()

    possible_talks = ["hi", "hello", "how are you?"]

    while True:
        # put a sentence in the redis
        # redis.set("gpt_response", random.choice(possible_talks))
        time.sleep(1)

        # read it out loud
        talk_controller.talk(random.choice(possible_talks))
        time.sleep(1)
