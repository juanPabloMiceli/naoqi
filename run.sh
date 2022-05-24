#!/bin/bash

sudo docker run --mount type=bind,source=$PWD,target=/app --rm -it naoqi
