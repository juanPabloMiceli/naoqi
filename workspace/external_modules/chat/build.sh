#!/bin/bash

# get this file location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

CURRENT_DIR="$(pwd)"

cd $SCRIPT_DIR

docker build -t nao_chat-image $SCRIPT_DIR

cd $CURRENT_DIR
