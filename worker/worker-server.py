#
# Worker server
#
import pickle
import platform
from PIL import Image
import io
import os
import sys
import pika
import redis
import hashlib


hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

##
## You provide this
##
