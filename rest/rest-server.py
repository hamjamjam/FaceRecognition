##
from flask import Flask, request, Response
import json, jsonpickle, pickle
import platform
import io, os, sys
import pika, redis
import hashlib, requests
from PIL import Image
import base64

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

# Initialize the Flask application
app = Flask(__name__)

# route http posts to this method
@app.route('/api/image/<X>', methods=['POST'])
def test(X):
    print(X)
    r = request
    # convert the data to a PIL image type so we can extract dimensions
    try:
        m = hashlib.md5()
        m.update(r.data)
        q = m.hexdigest()
        response = {
            "hash" : q
        }
        # encode response using jsonpickle
        response_pickled = jsonpickle.encode(response)
        message = pickle.dumps([X,q,r.data])
        credentials=pika.PlainCredentials('guest','guest')
        parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='work')
        channel.basic_publish(exchange ='',routing_key='work', body = message)
        print(" [x] Sent Data ")
        connection.close()
    except:
        response = {
           "hash" : 0
        }

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/api/hash/<X>', methods=['GET'])
def getvalue(X):
    r = redis.Redis(host = "redis",db=1)
    v = pickle.loads(r.get(X))
    response = {
        "value": v
    }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/api/license/<X>', methods=['GET'])
def getChecksum(X):
    r = redis.Redis(host = "redis",db=3)
    v = base64.b64decode(r.get(X))
    response = {
        "value": v
    }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")
app.run(host="0.0.0.0", port=5000)
app.debug = True
