#!/bin/bash
sudo docker run --network=nao-net --add-host=host.docker.internal:host-gateway --mount type=bind,source=$PWD,target=/home/user/nao/ --rm -it -u $(id -u):$(id -g) naoqi
