import time
import sys
import urllib2
import json
import urllib

from workspace.utils.logger_factory import LoggerFactory
from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.proxy_factory import ProxyFactory

from naoqi import ALModule, ALBroker

import qi

LOOK_TIMEOUT = 20 # seconds

postures_vocabularies = {
    "Stand": ["stand"],
    "Sit": ["sit"],
    "LyingBelly": ["lay"],
    "Crouch": ["crouch"],
    "LyingBack": ["lay back"],
    "SitRelax": ["sit relax"],
}

def post_to_api(text):
    # Create a dictionary with the data to be sent in the request body
    data = {"text": text}

    # Convert the data to JSON format
    json_data = json.dumps(data)

    # Set the URL of your FastAPI endpoint
    url = "http://gpt_api:8000/generate"

    while True:
        try:
            # Create a POST request with the JSON data
            request = urllib2.Request(url, json_data, headers={'Content-Type': 'application/json'})

            # Send the request and get the response
            response = urllib2.urlopen(request)

            # Check if the response is a redirect
            if response.getcode() == 307:
                # Get the new URL from the Location header
                url = response.headers['Location']
                continue

            # Read the response data
            response_data = response.read()

            # Parse the JSON response
            parsed_response = json.loads(response_data)

            # Access the generated text from the response
            generated_text = parsed_response["generated_text"]

            # Return the generated text
            return generated_text

        except urllib2.HTTPError as e:
            # Handle HTTP errors
            print("HTTP Error:", e.code, e.reason)

        except urllib2.URLError as e:
            # Handle URL errors
            print("URL Error:", e.reason)

        except Exception as e:
            # Handle other exceptions
            print("Error:", str(e))

class CommandController(ALModule):
    def __init__(self, ip, port, session):
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

        # self.speech_recognition = session.service("ALSpeechRecognition")
        # self.modules.append((self.speech_recognition, ""))

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


        self.waved_person_id = None
        self.handling_word = False
    
    def start_awareness(self, type):
        if type == "hearing":
            self.start_hearing_awareness()
        elif type == "text":
            self.start_text_awareness()

    def start_hearing_awareness(self):
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
        self.LOGGER.info("Using head movement for engagement")
        self.awareness.setTrackingMode("Head")

        # set the speech recognition variables
        self.speech_recognition.setLanguage("English")
        self.speech_recognition.setAudioExpression(True)
        self.speech_recognition.setVisualExpression(False)
        known_vocbulary = []
        for _, posture_vocabulary in postures_vocabularies.items():
            for word in posture_vocabulary:
                known_vocbulary.append(word)
        self.speech_recognition.setVocabulary(known_vocbulary, False)
        self.animated_speech.setBodyLanguageModeFromStr("disabled")

        # subscribe to wave detection
        self.allow_gaze_recgonition(True)
        while 1:
            continue


    def start_text_awareness(self):
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

        # wait for an incoming text
        

        # test text
        request = urllib2.Request("http://gpt_api:8000/test_api")
        response = urllib2.urlopen(request)
        data = json.loads(response.read())
        sentence = data["generated_text"]
        self.LOGGER.info(sentence)
        self.text_to_speech.say(sentence)
        while 1:
            # wait for input
            self.text_to_speech.say("Please write down what posture you would like me to do.")
            text = raw_input("Write message for nao: ")

            self.LOGGER.info("Given text:\n{}".format(text))

            # send input through api
            self.LOGGER.info("Sending request...")
            sentence = post_to_api(text)
            sentence = sentence.replace('"','')
            self.LOGGER.info("Received command: {}".format(sentence))

            # execute pose
            if sentence in postures_vocabularies.keys():
                self.text_to_speech.say("Yes, I'm going to {}.".format(sentence))
                self.posture_manager.goToPosture(sentence, 1)
            else:
                self.text_to_speech.say("Sorry, I didn't recognize the posture you requested.")

    def stop_awareness(self):
        # start the awareness of the NAO
        self.LOGGER.info("Stopping awareness")
        name = self.getName()
        # try:
        #     self.speech_recognition.unsubscribe(name)
        # except RuntimeError:
        #     pass
        # self.awareness.stopAwareness()
        # self.posture_manager.stopMove()
        # try:
        #     self.memory.unregisterModuleReference(name)
        # except RuntimeError:
        #     pass
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

        # open a 10 second window for hearing a word

        self.allow_gaze_recgonition(False)
        self.speech_recognition.subscribe(self.getName())
        self.allow_word_recgonition(True)
        
        time.sleep(10)

        if self.handling_word:
            self.LOGGER.info("waiting for word handling to finish")
            while self.handling_word:
                time.sleep(1)
        self.LOGGER.info("word handling finished")

        self.allow_word_recgonition(False)
        self.speech_recognition.unsubscribe(self.getName())
        self.allow_gaze_recgonition(True)


    def talked_at(
            self,
            event_name,
            word,
            subscriber_identifier
    ):
        if self.handling_word:
            self.LOGGER.info("Already handling word")
            return
        else:
            self.LOGGER.info("Starting word recognizing")
            # disable word hearing
            self.allow_word_recgonition(False)
            self.handling_word = True

            # capture whats being said

            heard_word = word[0]
            certainty = word[1]

            self.LOGGER.info("Heard {} with {} certainty".format(heard_word, certainty))

            if certainty > 0.38:
                self.LOGGER.info("Certainty exceeded")
                # detect specific commands
                # match to known commands
                for posture, posture_vocabulary in postures_vocabularies.items():
                    if heard_word in posture_vocabulary:
                        self.LOGGER.info("Going to execute {}".format(posture))
                        self.posture_manager.goToPosture(posture, 1)

            # stop capturing what was being said

            # allow word hearing again
            self.handling_word = False


    def wave(self):
        
        self.text_to_speech.say("bip bop")

    def sound_detected(self):
        
        self.LOGGER.info("sound detected")

    def allow_word_recgonition(self, allow):
        try:
            if allow:
                self.memory.subscribeToEvent(
                    "WordRecognized",
                    self.getName(),
                    "talked_at"
                )
            else:
                self.memory.unsubscribeToEvent(
                "WordRecognized",
                self.getName()
            )
        except RuntimeError:
            pass
        self.LOGGER.info("Word recognition set to {}".format(str(allow)))
        

    def allow_gaze_recgonition(self, allow):
        try:
            if allow:
                self.memory.subscribeToEvent(
                "GazeAnalysis/PersonStartsLookingAtRobot",
                self.getName(),
                "looked_at"
            )
            else:
                self.memory.unsubscribeToEvent(
                "GazeAnalysis/PersonStartsLookingAtRobot",
                self.getName(),
            )
        except RuntimeError:
            pass
        self.LOGGER.info("Gaze recognition set to {}".format(str(allow)))

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

    try:
        commandController.start_awareness("hearing")
    except Exception as e:
        commandController.LOGGER.info(e)
    finally:
        commandController.stop_awareness()

    # commandController.motion.rest()
