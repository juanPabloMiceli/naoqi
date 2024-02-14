from redis import Redis
import sounddevice as sd
from time import sleep
from workspace.external_modules.hearing.speech_detection import audio_callback
from workspace.external_modules.hearing.python_recording import Recorder
from workspace.external_modules.hearing.gpt import transcribe
from workspace.redis.redis_manager import RedisManager


AUDIO_PATH = "/app/workspace/external_modules/hearing/audio_files"


class AudioInputManager:
    def __init__(self):
        self.recorder = Recorder()
        self.redis = Redis(host="nao-redis", port=6379, db=0)
        self.redis_manager = RedisManager()
        self.redis_manager.clear_redis_keys()
        # self.redis.delete("speech_detected")

    @property
    def speech_detected(self):
        return self.redis.get("speech_detected") == b"1"

    def start(self, interval: int):
        """This method will start a constantly recording, interrupting it every interval amount of time.
        If the correct redis key indicates it, then this method will not interrupt the audio recording.
        """

        def stream_callback(indata, frames, time, status):
            hearing_status = self.redis_manager.hearing_status()
            talk_status = self.redis_manager.talk_status()
            avoid_hearing = hearing_status is False or talk_status is False
            speech_detected_value = None
            if not avoid_hearing:
                speech_detected_value = audio_callback(indata, frames, time, status)
            self.recorder.callback(indata, frames, time, status)

            if speech_detected_value is not None:
                self.redis.set("speech_detected", int(speech_detected_value))

        with sd.InputStream(
            device=self.recorder.device,  # self.recorder.device,
            callback=stream_callback,
            channels=self.recorder.channels,
            samplerate=self.recorder.samplerate,
        ):
            self.recorder.start_recording()  # Start audio recording

            while True:

                self.redis_manager.turn_on_hearing()
                self.redis_manager.turn_on_talk()

                try:
                    sleep(interval)  # Wait for the specified interval

                    # Check if the redis key indicates not to interrupt recording
                    if not self.speech_detected:
                        self.recorder.stop_recording(
                            "noise.wav"
                        )  # Stop audio recording
                        self.recorder.start_recording()
                    else:
                        print("Speech detected")
                        while self.speech_detected:
                            sleep(0.5)
                        print("Speech undetected")
                        # speech_tag = self.redis.get("speech_tag").decode("utf-8")
                        speech_audio_filepath = "nao_audio.wav"

                        self.recorder.stop_recording(
                            speech_audio_filepath
                        )  # Stop audio recording
                        print("Recording Stopped")

                        # transcribe audio file
                        transcription = transcribe(speech_audio_filepath)

                        # translate
                        # translated_transcription = translate(transcription)

                        print("Passing user transcription to chatbot")
                        # put the message on the conversation pipe
                        self.redis_manager.store_user_message(transcription)
                        # wait for the system response to be available
                        print("Waiting for chatbot response")
                        while not self.redis_manager.chat_response_available():
                            sleep(1)

                        print("Got chatbot response")
                        response = self.redis_manager.consume_chat_response()

                        if response is not None:
                            # execute the talking mechanism

                            # prevent further hearing
                            self.redis_manager.turn_off_hearing()

                            # pass the response onto the NAO via redis
                            # self.redis.set(f"gpt_response", response)

                            # execute the t2s of the NAO
                            self.redis_manager.store_nao_message(response)

                            # wait for nao message consumption
                            while self.redis_manager.nao_message_available():
                                sleep(0.5)

                            # re-allow hearing
                            self.redis_manager.turn_on_hearing()

                    self.recorder.start_recording()
                except Exception as e:
                    print(e)
                    self.recorder.stop_recording("noise.wav")


if __name__ == "__main__":
    aim = AudioInputManager()
    aim.start(2)
