#!/bin/bash
docker network create nao-net
docker run --rm --network=nao-net --name nao-redis -p 6379:6379 -d redis
sudo docker run --network=nao-net --device /dev/snd:/dev/snd --mount type=bind,source=$PWD,target=/app --rm -it gpt-api poetry run python python_recording.py