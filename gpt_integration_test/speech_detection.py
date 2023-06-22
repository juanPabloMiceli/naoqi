import sounddevice as sd
import redis

# Redis configuration
redis_host = "nao-redis"  # Replace with your Redis server host
redis_port = 6379  # Replace with your Redis server port

# Initialize Redis client
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)

# Audio configuration
chunk_size = 1024
sample_rate = 44100
silence_threshold = 0.05  # Adjust this threshold according to your needs


# SoundDevice callback function
def audio_callback(indata, frames, time, status):
    is_speech_detected = redis_client.get("speech_detected") == b"1"

    # Convert the audio data to integers
    audio_data = list(map(int, (indata * 32767).flatten()))

    # Check if the audio exceeds the silence threshold
    max_amplitude = max(audio_data) / 32767  # Normalize to the range [-1, 1]

    if max_amplitude > silence_threshold and not is_speech_detected:
        redis_client.set("speech_detected", 1)
        redis_client.incrby("audio_callback_missing_tries", 100)
    elif max_amplitude <= silence_threshold and is_speech_detected:
        tries_left = redis_client.decr("audio_callback_missing_tries")
        if tries_left <= 0:
            redis_client.set("speech_detected", 0)
            redis_client.set("audio_callback_missing_tries", 0)


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
