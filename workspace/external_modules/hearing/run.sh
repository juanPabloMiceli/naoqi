#!/bin/bash

# get this file location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# locate on workspace dir (absolute path as docker requires it)
cd $SCRIPT_DIR
cd ../..
CURRENT_DIR=$(pwd)

sudo docker network create nao-net
sudo docker run --rm --network=nao-net --name nao-redis -p 6379:6379 -d redis
sudo docker run --network=nao-net --device /dev/snd:/dev/snd --mount type=bind,source=$CURRENT_DIR,target=/app/workspace --rm -it nao_hearing-image bash -c "poetry run python workspace/external_modules/hearing/audio_input_manager.py"
