FROM lightweight/websync

ADD . /docker-registry

RUN cd /docker-registry 
CMD chmod +x startDocker.sh && ./startDocker.sh