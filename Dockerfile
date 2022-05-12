FROM ubuntu:14.04

RUN apt update
RUN apt upgrade -y
RUN apt install python -y
RUN apt install python-opencv -y
WORKDIR /app

CMD ["/bin/bash"]