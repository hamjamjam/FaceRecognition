FROM python:3.7
ENV PYTHONUNBUFFERED=1
RUN pip3 install Flask
RUN pip3 install pillow jsonpickle
RUN pip3 install requests
RUN pip3 install numpy
RUN pip3 install --upgrade pika
RUN pip3 install redis
RUN mkdir /rest
WORKDIR /rest
copy rest-server.py /rest
CMD     python3 rest-server.py
