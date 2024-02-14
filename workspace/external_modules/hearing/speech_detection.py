import sounddevice as sd
import speech_recognition as sr
import numpy as np
import scipy.io.wavfile as wavfile
import redis
import wave

AUDIO_PATH = "/app/workspace/external_modules/hearing/audio_files"

# Redis configuration
redis_host = "nao-redis"  # Replace with your Redis server host
redis_port = 6379  # Replace with your Redis server port

# Initialize Redis client
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)

# Audio configuration
chunk_size = 1024
sample_rate = 44100
silence_threshold = 0.06  # Adjust this threshold according to your needs


# SoundDevice callback function
def audio_callback(indata, frames, time, status) -> bool:
    is_speech_currently_detected = redis_client.get("speech_detected") == b"1"

    # Convert the audio data to integers
    audio_data = list(map(int, (indata * 32767).flatten()))

    # Check if the audio exceeds the silence threshold
    max_amplitude = max(audio_data) / 32767  # Normalize to the range [-1, 1]

    speech_detected = None
    if max_amplitude > silence_threshold and not is_speech_currently_detected:
        speech_detected = True
        redis_client.incrby("audio_callback_missing_tries", 100)
    elif max_amplitude <= silence_threshold and is_speech_currently_detected:
        tries_left = redis_client.decr("audio_callback_missing_tries")
        if tries_left <= 0:
            speech_detected = False
            redis_client.set("audio_callback_missing_tries", 0)

    return speech_detected


def has_speech(audio_file_path: str) -> bool:
    sample_rate, audio_data = wavfile.read(audio_file_path)

    # Convert audio data to byte stream
    audio_data = audio_data.astype(np.int16)
    audio_stream = audio_data.tobytes()

    # Create a new wave file
    with wave.open(f"{AUDIO_PATH}/converted_file.wav", "wb") as wav:
        wav.setnchannels(2)  # Set number of channels
        wav.setsampwidth(2)  # Set sample width (2 bytes for int16 data)
        wav.setframerate(sample_rate)  # Set sample rate
        wav.writeframes(audio_stream)

    print("Converted audio file")

    r = sr.Recognizer()

    with sr.AudioFile(f"{AUDIO_PATH}/converted_file.wav") as source:
        audio = r.record(source)  # Read the entire audio file

    print("loaded audio file into wave")

    try:
        text = r.recognize_google(
            audio, language="es-ES"
        )  # Use Google Speech Recognition
        print("recognition succedeed")
        return True  # Speech was recognized
    except sr.UnknownValueError:
        print("cant recognize")
        return False  # No speech was recognized
    except sr.RequestError:
        print("Recognition request failed.")
        return False


if __name__ == "__main__":
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"Device #{i}: {device['name']}")

    print("Recorder usage requires a mic selection")
    device_id = input("Select a device:")
    device_name = devices[int(device_id)]["name"]
    print(device_name)

    # Start the audio stream
    stream = sd.InputStream(
        device=device_name,
        callback=audio_callback,
        channels=1,
        samplerate=sample_rate,
        blocksize=chunk_size,
    )

    stream.start()

    # Keep the script running until interrupted
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

    # Stop and close the stream
    stream.stop()
    stream.close()
