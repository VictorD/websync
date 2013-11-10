FROM lightweight/websync

ADD . /docker-registry

CMD cd /docker-registry startDocker.sh