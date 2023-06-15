import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
import openai

import secret_cfg as scfg


class AudioRequest(BaseModel):
    path: str
    expected_response: str


class SentText(BaseModel):
    text: str


# Initialize the FastAPI app
app = FastAPI()

openai.api_key = scfg.API_KEY

POSTURE_PROMPT = """
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

TALK_PROMPT = """
You are an Aldebaran NAO robot working for the LAFHIS lab at the university of Buenos Aires.
Your main objective is to engage in general talk, small talk if necessary (such as "how are you", etc).
You should be able to explain what can you do as a NAO robot and also what the LAFHIS lab investigates.
Try to be concise on the themes you talk about and don't branch out. Prompt the user if he wants to be explained more about said topic.
"""

prompt_dict = {"talk": TALK_PROMPT, "posture": POSTURE_PROMPT}


def execute_message(text: str, base_prompt=POSTURE_PROMPT) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": text},
        ],
    )
    generated_text = response.choices[0].message.content
    print(generated_text)
    return generated_text


@app.post("/transcribe_and_generate/")
async def transcribe_and_generate(audio: AudioRequest):
    # gather the audio path
    audio_path = "/app/audio_files/" + audio.path
    expected_response = audio.expected_response
    response_prompt = prompt_dict[expected_response]
    try:
        audio_file = open(audio_path, "rb")
        transcript = openai.Audio.translate("whisper-1", audio_file)["text"]
        print(f"Transcript: {transcript}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error transcribing audio")

    try:
        # execute the transcript on gpt
        return {"generated_text": execute_message(transcript, response_prompt)}
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


@app.get("/test_api")
async def test_api():
    return {"generated_text": "Hi, my name is Chookie"}
