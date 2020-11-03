FROM ubuntu:19.10
RUN apt-get update
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y openalpr
RUN cp /usr/share/openalpr/runtime_data/ocr/tessdata/lus.traineddata /usr/share/openalpr/runtime_data/ocr
RUN apt-get install -y python3 python3-pip python3-pillow python3-openalpr python3-redis
RUN pip3 install pika
RUN pip3 install jsonpickle
RUN pip3 install pillow
RUN pip3 install request
RUN pip3 install redis
RUN pip3 install numpy
RUN mkdir /worker
WORKDIR /worker
copy worker-server.py /worker
CMD  python3 worker-server.py
