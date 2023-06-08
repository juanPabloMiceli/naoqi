#!/bin/bash
docker network create nao-net
docker run --mount type=bind,source=$PWD,target=/app --rm -it --network=nao-net -p 8000:8000 --name nao-gpt-api gpt-api uvicorn main:app --host 0.0.0.0 --port 8000