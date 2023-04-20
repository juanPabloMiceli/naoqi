FROM ubuntu:16.04

# Update & upgrade de apt
RUN apt-get update
RUN apt-get upgrade -y
# Instalo python y opencv (viene numpy de yapa)
RUN apt-get install python -y
RUN apt-get install python-opencv -y

# Necesario para poder usar el naoqi sdk
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt-get update
RUN apt-get dist-upgrade -y


# Instalo el naoqi sdk 
COPY naoSDKPython /usr/local/lib/naoSDKPython
RUN echo "export LD_LIBRARY_PATH=app/naoSDKPython/lib/" >> /root/.bashrc
RUN echo "export PYTHONPATH=/app/naoSDKPython/lib/python2.7/site-packages/" >> /root/.bashrc



# Instalo binario zbar
RUN apt-get install libzbar0

#Instalo pip y el python wrapper de zbar
RUN apt-get install python-pip -y
RUN pip install pyzbar

# Instalo pandas para usar el sonar adapter
RUN pip install pandas==0.23.1

# Misc installs
RUN apt-get install vim -y

WORKDIR /app

CMD ["/bin/bash"]
