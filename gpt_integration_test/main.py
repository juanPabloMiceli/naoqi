import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
import openai

import secret_cfg as scfg


class AudioPath(BaseModel):
    path: str

class SentText(BaseModel):
    text: str


# Initialize the FastAPI app
app = FastAPI()

openai.api_key = scfg.API_KEY

BASIC_PROMPT = """
You are an intent detector for a NAO robot named Chooki.
Your task is to receive Spanish audio transcriptions of requests given to the robot and map the request to a known posture.
You can only respond to posture requests. Your objective is to detect the requested posture, compare it to the known postures, and return the name of the posture.
If the requested posture is unknown or if no posture was requested, you should respond with "Unknown".
Your response should follow the following schema:

"recognized_posture"

The known postures are:

Stand
Sit         -- Sit down on the floor (By default when asked to sit down)
Crouch
LyingBelly  -- Which would be lying on its belly on the floor (By default when asked to lay down)
LyingBack   -- Which would be lying on its back on the floor
SitRelax    -- (Only when prompt to be chill while sitting)


The transcript is:
    """

def execute_message(text: str) -> str:

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": BASIC_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    generated_text = response.choices[0].message.content
    print(generated_text)
    return generated_text


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

    try:
        return {"generated_text": execute_message(text)}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Error generating response from GPT-3"
        )
    
@app.post("/generate")
async def generate(sent_text: SentText):
    try:
        return {"generated_text": execute_message(sent_text.text)}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Error generating response from GPT-3"
        )
    

@app.get("/test_api/")
async def test_api():
    return {"generated_text": "Hi, my name is Chookie"}
