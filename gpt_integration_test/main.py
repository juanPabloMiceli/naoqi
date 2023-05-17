import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
import openai


class AudioPath(BaseModel):
    path: str


# Initialize the FastAPI app
app = FastAPI()

openai.api_key = "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"


@app.post("/transcribe_and_generate/")
async def transcribe_and_generate(audio: AudioPath):
    r = sr.Recognizer()
    audio_path = "/audio_files/" + audio.path
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            text = "Chookie parate"
            print("Transcribed Text: ", text)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error transcribing audio")

    prompt = """
You are an intent detector for a NAO robot named Chooki. Your task is to receive Spanish audio transcriptions of requests given to the robot and map the request to a known posture. You can only respond to posture requests. Your objective is to detect the requested posture, compare it to the known postures, and return the name of the posture along with its availability. If the requested posture is unknown or if no posture was requested, you should respond with "Unknown" and indicate that the posture isn't available. Your response should follow the following schema:

'{
"RequestedPosture": "[recognized_posture]",
"Available": true/false
}'

The known postures are:

Stand
Sit
Crouch
Lay Down

The transcript is:
    """

    prompt

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
        )
        generated_text = response.choices[0].message.content
        print(generated_text)
        return {"generated_text": generated_text}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Error generating response from GPT-3"
        )
