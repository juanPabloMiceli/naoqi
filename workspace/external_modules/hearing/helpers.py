import logging
import selectors
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
import openai
from redis import Redis
import json

import workspace.external_modules.secret_cfg as scfg
from workspace.redis.redis_manager import RedisManager

openai.api_key = scfg.API_KEY

redis_manager = RedisManager()


def transcribe(audio_path: str) -> str:
    full_path = "/app/workspace/external_modules/hearing/audio_files/" + audio_path
    try:
        audio_file = open(full_path, "rb")
        transcript = openai.Audio.translate(
            "whisper-1",
            audio_file,
            # prompt="These audio are directed to Chookie, and Aldebaran NAO Robot",
        )["text"]
        print(f"Transcript: {transcript}")
        return transcript
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error transcribing audio")


def translate(text: str): 
    response = openai.Completion.create( 
    engine="gpt-3.5-turbo-instruct", 
    prompt=f"Translate the following text from spanish into english (if its in english return the text as is): {text}\n", 
    max_tokens=60, 
    n=1, 
    stop=None, 
    temperature=0.7, ) 
    response_text =  response.choices[0].text.strip()
    translated = text not in response_text
    return_text = response_text if translated else text
    print(f"translated transcription: {return_text}")
    return return_text

def input_with_timeout(prompt, timeout, default):
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ)

    print(prompt, end='', flush=True)

    events = sel.select(timeout)
    if events:
        # Input is available before timeout
        return sys.stdin.readline().strip()
    else:
        # Timeout occurred, return default value
        print(default)
        return default
