#!/bin/bash

sudo docker run --mount type=bind,source=$PWD,target=/app --rm -it -u $(id -u):$(id -g) naoqi
