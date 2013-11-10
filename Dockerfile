FROM lightweight/websync

ADD . /websync

CMD ["5000"]

ENTRYPOINT ["python", "/websync/run.py"]
