import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write


devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"Device #{i}: {device['name']}")

print("Recorder usage requires a mic selection")
device_id = input("Select a device:")
device_name = devices[int(device_id)]["name"]

AUDIO_PATH = "/app/workspace/external_modules/hearing/audio_files"


class Recorder:
    def __init__(self, samplerate=44100, channels=2, file_path=AUDIO_PATH):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = []
        self.is_recording = False
        self.file_path = file_path
        self.device = device_name

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        if self.is_recording:
            self.recording.append(indata.copy())

    def start_recording(self):
        self.is_recording = True
        if self.recording is None:
            self.recording = np.empty((0, self.channels))

    def stop_recording(self, filename):
        self.is_recording = False
        if len(self.recording) > 0:
            write(
                f"{self.file_path}/{filename}",
                self.samplerate,
                np.concatenate(self.recording, axis=0),
            )
        self.recording = []
