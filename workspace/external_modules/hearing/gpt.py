import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
import openai
from redis import Redis
import json

import workspace.external_modules.hearing.secret_cfg as scfg
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


def translate(message: str) -> str:
    pass
