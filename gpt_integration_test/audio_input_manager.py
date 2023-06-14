
from python_recording import Recorder
from redis import Redis
import sounddevice as sd

class AudioInputManager():
    def __init__(self):
        self.recorder = Recorder()
        self.redis = Redis(host="nao-redis", port=3679, db=0) #TODO
        
    def start(self, interval:int):
        """This method will start a constantly recording, interrupting it every interval amount of time.
        If the correct redis key indicates it, then this method will not interrupt the audio recording.
        """
        self.recorder.start_recording()  # Start audio recording
        with sd.InputStream(device=self.recorder.device_name, callback=self.recorder.callback, channels=self.recorder.channels, samplerate=self.recorder.samplerate):
        
            while True:
                    sleep(interval)  # Wait for the specified interval
                    
                    # Check if the redis key indicates not to interrupt recording
                    if self.redis.get("speech_detected") != b"1":
                        self.recorder.stop_recording("noise.wav")  # Stop audio recording
                        self.recorder.start_recording()
                    else:
                        while self.redis.get("speech_end") != b"1":
                            sleep(0.5)
                        speech_tag = self.redis.get("speech_tag").decode("utf-8")
                        self.recorder.stop_recording(f"{speech_tag}.wav")  # Stop audio recording
                        self.redis.set("speech_available", 1)
                        self.recorder.start_recording()
        
    