FROM dirkcgrunwald/facerec:latest

RUN pip3 install pika
RUN pip3 install redis
RUN pip3 install flask
RUN pip3 install requests

ENV PYTHONUNBUFFERED=1

RUN mkdir /worker
WORKDIR /worker
copy worker-server.py /worker
CMD  python3 worker-server.py
