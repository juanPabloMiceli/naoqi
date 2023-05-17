import time
import sys

from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.proxy_factory import ProxyFactory

from naoqi import ALModule, ALBroker

import qi

LOOK_TIMEOUT = 20 # seconds

postures_vocabularies = {
    "Stand": ["parar", "parado", "pararse", "parate", "levantate", "de-pie", "stand"],
    "Sit": ["sentar", "sentado", "sentarse", "sentate", "sit"],
    "LyingBelly": ["acostar", "acostado", "acostarse", "acostate", "lay"],
}

class CommandController(ALModule):
    def __init__(self, ip, port, session):
        self.name = "commandController"
        ALModule.__init__(self, self.name)
        self.LOGGER = LoggerFactory.get_logger("CommandController")
        self.awareness = session.service("ALBasicAwareness")
        self.people_perception = session.service("ALPeoplePerception")
        self.face_detection = session.service("ALFaceDetection")
        # self.animation_player = session.service("ALAnimationPlayer")
        # self.wave_detection = session.service("ALWavingDetection")
        self.text_to_speech = session.service("ALTextToSpeech")
        self.speech_recognition = session.service("ALSpeechRecognition")
        self.sound_detection = session.service("ALSoundDetection")
        self.memory = session.service("ALMemory")
        self.posture_manager = session.service("ALRobotPosture")
        self.LOGGER.info(self.posture_manager.getPostureList())
        self.animated_speech = session.service("ALAnimatedSpeech")
        self.motion = session.service("ALMotion")

        self.waved_person_id = None

    def start_awareness(self):
        # wake up
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
        self.LOGGER.info("Using full body rotation for engagement")
        self.awareness.setTrackingMode("BodyRotation")

        # set the speech recognition variables
        self.speech_recognition.removeAllContext()
        self.speech_recognition.unsubscribe(self.getName())
        self.speech_recognition.setLanguage("English")
        self.speech_recognition.setAudioExpression(True)
        self.speech_recognition.setVisualExpression(True)
        known_vocbulary = []
        for _, posture_vocabulary in postures_vocabularies.items():
            for word in posture_vocabulary:
                known_vocbulary.append(word)
        self.speech_recognition.setVocabulary(known_vocbulary, False)
        self.animated_speech.setBodyLanguageMode(0)

        # subscribing to speech recognition
        self.memory.subscribeToEvent(
            "GazeAnalysis/PersonStartsLookingAtRobot",
            self.getName(),
            "looked_at"
        )


        # subscribe to wave detection
        self.LOGGER.info("Subscribing to wave detection events")
        self.memory.subscribeToEvent(
            "GazeAnalysis/PersonStartsLookingAtRobot",
            self.getName(),
            "looked_at"
        )
        while 1:
            continue

    def stop_awareness(self):
        # start the awareness of the NAO
        self.LOGGER.info("Stopping awareness")
        self.motion.rest()

    def looked_at(
            self,
            event_name,
            person_id,
            subscriber_identifier
        ):
        self.LOGGER.info("Has been looked by {}.".format(person_id))
        # save into memory the id of the person waving at the NAO
        self.waved_person_id = person_id

        self.wave()

        self.speech_recognition.subscribe(self.getName())
        # subscribe to the sound detection module for 3 seconds
        self.memory.subscribeToEvent(
            "WordRecognized",
            self.getName(),
            "talked_at"
        )

        time.sleep(10)

        # unsuscribe
        self.memory.unsubscribeToEvent(
            "WordRecognized",
            self.getName()
        )
        self.speech_recognition.unsubscribe(self.getName())


    def talked_at(
            self,
            event_name,
            word,
            subscriber_identifier
    ):
        # capture whats being said

        self.LOGGER.info(word)
        self.LOGGER.info(self.memory.getData("WordRecognized"))

        # detect specific commands
        # match to known commands
        for posture, posture_vocabulary in postures_vocabularies:
            if word in posture_vocabulary:
                print("{} recognized".format(word))
                print("Going to execute {}".format(posture))
                self.posture_manager.goToPosture(posture, 1)

        # stop capturing what was being said

        pass

    def wave(self):
        
        self.text_to_speech.say("bip bop")

    def sound_detected(self):
        
        self.LOGGER.info("sound detected")
        

    def on(self):
        self.LOGGER.info("Turning on leds [{}]".format(self.group))
        self.proxy.on(self.group)

if __name__ == "__main__":
    IP, PORT = NaoProperties().get_connection_properties()

    broker = ALBroker("broker", "0.0.0.0", 0, IP, PORT)

    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print("error :(")
        sys.exit(1)

    commandController = CommandController(IP, PORT, session)

    #commandController.start_awareness()
    commandController.stop_awareness()