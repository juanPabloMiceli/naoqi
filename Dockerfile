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

# Creo un usuario para que los archivos creados en el container de forma interactiva no sean root.
RUN useradd -u 1000 -m -s /bin/bash user && echo 'user:password' | chpasswd

# Instalo el naoqi sdk 
COPY naoSDKPython /usr/local/lib/naoSDKPython
RUN echo "export LD_LIBRARY_PATH=/home/user/nao/naoSDKPython/lib/" >> /home/user/.bashrc
RUN echo "export PYTHONPATH=/home/user/nao/naoSDKPython/lib/python2.7/site-packages/" >> /home/user/.bashrc

# Instalo binario zbar
RUN apt-get install libzbar0

#Instalo pip y el python wrapper de zbar
RUN apt-get install python-pip -y
RUN pip install pyzbar

# Instalo pandas para usar el sonar adapter
RUN pip install pandas==0.23.1

# Install Vim
RUN apt-get install vim -y


#Install FZF
WORKDIR /bin
RUN apt-get install wget
RUN wget https://github.com/junegunn/fzf/releases/download/0.39.0/fzf-0.39.0-linux_amd64.tar.gz fzf.tar.gz | true # For some reason this failes with error code 4, but in reality it downloads the binary
RUN tar -xf fzf-0.39.0-linux_amd64.tar.gz
RUN echo "source /home/user/nao/fzf-key-bindings.bash" >> /home/user/.bashrc
RUN apt-get install openssh-client -y

WORKDIR /home/user/nao

CMD ["/bin/bash"]
