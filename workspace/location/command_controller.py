import time
import sys

from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.proxy_factory import ProxyFactory

from naoqi import ALModule, ALBroker

import qi

LOOK_TIMEOUT = 20 # seconds

postures_vocabularies = {
    "Standing": ["stand", "up", "standing", "raise", "wake", "de-pie"],
    "Sitting": ["sentar", "sentado", "sentarse", "sentate", "sit"],
    "LyingBelly": ["acostar", "acostado", "acostarse", "acostate", "down", "lay"],
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
        self.speech_recognition = ProxyFactory.get_proxy("ALSpeechRecognition", ip, port)
        self.memory = session.service("ALMemory")

        self.waved_person_id = None

    def start_awareness(self):
        print("Awake")
        # start the awareness of the NAO
        print(self.awareness.__dict__)
        self.LOGGER.info("Starting greeting awareness")
        self.awareness.startAwareness()
        
        # enable people detection only
        self.LOGGER.info("Allowing people detection")
        self.awareness.setStimulusDetectionEnabled("People", True)

        # set the engament mode to fully engaged to avoid dsitractions
        self.LOGGER.info("Using full engagement mode")
        self.awareness.setEngagementMode("FullyEngaged")

        # set the trackipanishe to whole body to be able to follow the people it interacts with
        self.LOGGER.info("Using full body rotation for engagement")
        self.awareness.setTrackingMode("BodyRotation")

        # set the speech recognition variables
        print(self.speech_recognition.getAvailableLanguages())
        self.speech_recognition.setLanguage("English")
        self.speech_recognition.setAudioExpression(True)
        self.speech_recognition.setVisualExpression(True)
        known_vocbulary = []
        for _, posture_vocabulary in postures_vocabularies.items():
            for word in posture_vocabulary:
                known_vocbulary.append(word)
        self.speech_recognition.setVocabulary(known_vocbulary, False)


        # subscribe to wave detection
        self.LOGGER.info("Subscribing to wave detection events")
        self.memory.subscribeToEvent(
            "GazeAnalysis/PersonStartsLookingAtRobot",
            self.getName(),
            "looked_at"
        )
        while 1:
            continue

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

        # subscribe to the sound detection module for 3 seconds
        print("TIPO {}".format(type(self.getName())))
        self.speech_recognition.subscribe(
            "WordRecognized",
            self.getName(),
            "talked_at"
        )

        time.sleep(5)

        # unsuscribe
        self.speech_recognition.unsubscribe(
            "WordRecognized",
            self.getName()
        )


    def talked_at(
            self,
            event_name,
            word,
            subscriber_identifier
    ):
        # capture whats being said
        print("Palabra: {}".format(word))

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
    motion_proxy = ProxyFactory.get_proxy("ALMotion", IP, PORT)
    motion_proxy.wakeUp()

    commandController.start_awareness()
