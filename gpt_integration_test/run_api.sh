#!/bin/bash
sudo docker network create nao-net
sudo docker run --mount type=bind,source=$PWD,target=/app --rm -it --network=nao-net -p 8000:8000 --name nao-gpt-api gpt-api bash
