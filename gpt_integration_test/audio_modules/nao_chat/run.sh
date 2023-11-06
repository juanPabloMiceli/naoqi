#!/bin/bash

# get this file location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

docker network create nao-net
docker run --network nao-net --rm --name nao-redis -p 6379:6379 -d redis
docker run --network nao-net --env-file .env --rm -it -v $SCRIPT_DIR:/nao_chat -v $SCRIPT_DIR/.ignore/logs/:/nao_chat/logs -v $SCRIPT_DIR/.ignore/csv/:/nao_chat/csv --name nao_chat -p 7860:7860 nao_chat-image /bin/bash
