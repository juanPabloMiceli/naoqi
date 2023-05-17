#!/bin/bash

sudo docker run --mount type=bind,source=$PWD,target=/home/user/nao/ --rm -it -u $(id -u):$(id -g) naoqi
