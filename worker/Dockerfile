FROM dirkcgrunwald/facerec:latest
RUN mkdir /worker
WORKDIR /worker
copy worker-server.py /worker
CMD  python3 worker-server.py
