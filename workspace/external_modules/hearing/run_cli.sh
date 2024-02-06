#!/bin/bash

# get this file location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

sudo docker network create nao-net
sudo docker run --rm --network=nao-net --name nao-redis -p 6379:6379 -d redis
sudo docker run --network=nao-net --device /dev/snd:/dev/snd --mount type=bind,source=$SCRIPT_DIR,target=/app --rm -it nao_hearing-image poetry run python audio_input_manager.py
