FROM lightweight/websync

ADD . /docker-registry

CMD cd /docker-registry 
CMD chmod +x startDocker.sh
CMD ./startDocker.sh