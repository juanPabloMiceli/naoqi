import time

from logger_factory import LoggerFactory
from nao_properties import NaoProperties
from proxy_factory import ProxyFactory

from naoqi import ALModule

LOOK_TIMEOUT = 20 # seconds

class GreetController(ALModule):
    def __init__(self, ip, port):
        self.name = "greetModule"
        ALModule.__init__(self, self.name)
        self.LOGGER = LoggerFactory.get_logger("GreetController")
        self.awareness = ProxyFactory.get_proxy("ALBasicAwareness", ip, port)
        self.people_perception = ProxyFactory.get_proxy("ALPeoplePerception", ip, port)
        self.face_detection = ProxyFactory.get_proxy("ALPeoplePerception", ip, port)
        self.animation_player = ProxyFactory.get_proxy("ALPeoplePerception", ip, port)
        self.wave_detection = ProxyFactory.get_proxy("ALPeoplePerception", ip, port)
        self.text_to_speech = ProxyFactory.get_proxy("ALPeoplePerception", ip, port)
        self.memory = ProxyFactory.get_proxy("ALPeoplePerception", ip, port)

        self.waved_person_id = None

    def start_awareness(self):
        # start the awareness of the NAO
        self.LOGGER.info("Starting greeting awareness")
        self.awareness.setEnabled(True)
        
        # enable people detection only
        self.LOGGER.info("Allowing people detection")
        self.awareness.setStimulusDetectionEnabled("People", True)

        # set the engament mode to fully engaged to avoid dsitractions
        self.LOGGER.info("Using full engagement mode")
        self.awareness.setEngagementMode("FullyEngaged")

        # set the tracking mode to whole body to be able to follow the people it interacts with
        self.LOGGER.info("Using full body rotation for engagement")
        self.awareness.setTrackingMode("BodyRotation")

        # subscribe to wave detection
        self.LOGGER.info("Subscribing to wave detection events")
        self.memory.subscribeToEvent(
            "PersonWaving",
            self.getName(),
            "greet_detected"
        )


    def greet_detected(
            self,
            event_name,
            person_id,
            subscriber_identifier
        ):
        self.LOGGER.info("Has been waved by {}.".format(person_id))
        # save into memory the id of the person waving at the NAO
        self.waved_person_id = person_id

        # only for testing
        self.wave()


    def wave(self):
        
        # engage with the person that will be waved
        self.awareness.engagePerson(self.waved_person_id)

        # pause awareness
        self.awareness.pauseAwareness()

        # greet, gets an animation future to be able to 
        animation_future = self.animation_player.runTag("hello")
        self.text_to_speech.say("Hi")

        # wait for the future to end
        animation_future.wait(10000)

        #resume awareness
        self.awareness.resumeAwareness()
        

    def on(self):
        self.LOGGER.info("Turning on leds [{}]".format(self.group))
        self.proxy.on(self.group)

if __name__ == "__main__":
    IP, PORT = NaoProperties().get_connection_properties()
    leds_controller = GreetController(IP, PORT)

    GreetController.start_awareness()
