import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import requests
import json
from time import sleep

devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"Device #{i}: {device['name']}")
    
device_id = input("Select a device:")
device_name = devices[int(device_id)]['name']

def post_to_api(audio_filename):
    # Create a dictionary with the data to be sent in the request body
    data = {"path": audio_filename}

    # Convert the data to JSON format
    json_data = json.dumps(data)

    # Set the URL of your FastAPI endpoint
    url = "http://nao-gpt-api:8000/transcribe_and_generate/"

    try:
        # Send a POST request with the JSON data
        response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})

        # Check the response status code
        response.raise_for_status()

        # Parse the JSON response
        parsed_response = response.json()

        # Access the generated text from the response
        generated_text = parsed_response["generated_text"]

        # Return the generated text
        return generated_text

    except requests.HTTPError as e:
        # Handle HTTP errors
        print("HTTP Error:", e.response.status_code, e.response.reason)

    except requests.RequestException as e:
        # Handle other request exceptions
        print("Request Exception:", str(e))

    except Exception as e:
        # Handle other exceptions
        print("Error:", str(e))

class Recorder:
    def __init__(self, samplerate=44100, channels=2):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = []
        self.is_recording = False

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
        write(f"/app/audio_files/{filename}", self.samplerate, np.concatenate(self.recording, axis=0))
        self.recording = []

recorder = Recorder()

# for i, device in enumerate(devices):
#         try:
#             sd.check_input_settings(device=i, samplerate=44100)
#             print("The device supports a sample rate of 44100 Hz.")
#         except Exception as e:
#             print(f"The device does not support a sample rate of 44100 Hz: {e}")
#             continue
#         print(f"Recording from device #{i}: {device['name']}")
#         recorder.recording = []
#         with sd.InputStream(device=i, channels=recorder.channels, callback=recorder.callback, samplerate=recorder.samplerate):
#             sleep(5)
#         final_buffer = np.concatenate(recorder.recording, axis=0)
#         write(f'output_device_{i}.wav', recorder.samplerate, final_buffer)



while True:
    input("Press Enter to start recording")
    print('Recording Started')
    recorder.start_recording()
        
        
    with sd.InputStream(device=device_name, callback=recorder.callback, channels=recorder.channels, samplerate=recorder.samplerate):
        input("Press Enter to stop recording")
        print('Recording Stopped')
        recorder.stop_recording('output.wav')  # Save as WAV file
    
    # send the message to the gpt api
    print('Posting the audio to the GPT API')
    response = post_to_api('output.wav')
    print(response)
    
    