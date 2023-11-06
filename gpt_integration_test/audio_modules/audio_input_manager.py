from python_recording import Recorder, post_to_api
from redis import Redis
import sounddevice as sd
from time import sleep
from speech_detection import audio_callback, has_speech
from nao_chat.nao_chat.conversation_pipe import ConversationPipe


AUDIO_PATH = "/app/audio_files"


class AudioInputManager:
    def __init__(self):
        self.recorder = Recorder()
        self.redis = Redis(host="nao-redis", port=6379, db=0)
        self.convo_pipe = ConversationPipe()
        self.redis.delete("speech_detected")

    @property
    def speech_detected(self):
        return self.redis.get("speech_detected") == b"1"

    def start(self, interval: int):
        """This method will start a constantly recording, interrupting it every interval amount of time.
        If the correct redis key indicates it, then this method will not interrupt the audio recording.
        """

        def stream_callback(indata, frames, time, status):
            avoid_hearing = (
                self.redis.get("avoid_hearing") == b"1"
                or self.redis.get("talk_enabled") != b"1"
            )
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
                        speech_tag = self.redis.get("speech_tag").decode("utf-8")
                        speech_audio_filepath = f"{speech_tag}.wav"

                        self.recorder.stop_recording(
                            speech_audio_filepath
                        )  # Stop audio recording
                        print("Recording Stopped")

                        # if has_speech(f"{AUDIO_PATH}/{speech_audio_filepath}"):
                        #    print("Audio file has actual speech")
                        # send audio recording a retrieve response
                        command_type = self.redis.get("command_type").decode("utf-8")

                        response = post_to_api(
                            speech_audio_filepath,
                            command_type,
                        )

                        if command_type == "chat":
                            print("Passing user transcription to chatbot")
                            # put the message on the conversation pipe
                            self.convo_pipe.add_user_message(response)
                            # wait for the system response to be available
                            print("Waiting for chatbot response")
                            print(self.convo_pipe.get_bot_message_availability())
                            while not self.convo_pipe.get_bot_message_availability():
                                print(self.convo_pipe.get_bot_message_availability())
                                sleep(1)

                            print("Got chatbot response")
                            response = self.convo_pipe.get_bot_message()

                        if response is not None:
                            # execute the talking mechanism

                            # prevent further hearing
                            self.redis.set("avoid_hearing", 1)

                            # pass the response onto the NAO via redis
                            # self.redis.set(f"gpt_response", response)

                            # execute the t2s of the NAO
                            self.redis.set("NAO_response", response)

                            # wait for nao clearing
                            while self.redis.get("NAO_response") is not None:
                                sleep(0.5)

                            # re-allow hearing
                            self.redis.set("avoid_hearing", 0)

                    self.recorder.start_recording()
                except Exception as e:
                    print(e)
                    self.recorder.stop_recording("noise.wav")


if __name__ == "__main__":
    aim = AudioInputManager()
    aim.start(2)
