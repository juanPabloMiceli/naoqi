#!/bin/bash

# get this file location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# locate on workspace dir (absolute path as docker requires it)
cd $SCRIPT_DIR
cd ../..
CURRENT_DIR=$(pwd)

docker network create nao-net
docker run --network nao-net --rm --name nao-redis -p 6379:6379 -d redis
docker run --network nao-net --env-file $SCRIPT_DIR/.env --rm -it --mount type=bind,source=$CURRENT_DIR,target=/app/workspace -v $SCRIPT_DIR/.ignore/logs/:/nao_chat/logs -v $SCRIPT_DIR/.ignore/csv/:/nao_chat/csv --name nao_chat -p 7860:7860 nao_chat-image bash -c "poetry run python workspace/external_modules/chat/nao_chat/main.py"
