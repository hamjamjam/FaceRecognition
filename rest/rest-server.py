##
from flask import Flask, request, Response, jsonify
import time
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
redisHost = os.getenv("REDIS_HOST") or "redis"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "rabbitmq"

redisNameToHash = redis.Redis(host=redisHost, db=1)    # Key -> Value
redisHashToName = redis.Redis(host=redisHost, db=2)    # Key -> Set
redisHashToFaceRec = redis.Redis(host=redisHost, db=3) # Key -> Set
redisHashToHashSet = redis.Redis(host=redisHost, db=4) # Key -> Set
redisFaceToHashSet = redis.Redis(host=redisHost, db=5) # Key -> Set
redisHashToObama = redis.Redis(host=redisHost, db=6)


print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

# Initialize the Flask application
app = Flask(__name__)

# route http posts to this method
@app.route('/api/image/<X>', methods=['POST'])
def test(X):
    print(X)
    app.logger.info(X)
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
        app.logger.info('sent data')
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




@app.route('/scan/url', methods=['POST'])
def scanUrl():
    data = request.json
    url = data["url"]
    print(url)
    
    message = url
    credentials=pika.PlainCredentials('guest','guest')
    parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='work')
    channel.basic_publish(exchange ='',routing_key='work', body = message)
    print(" [x] Sent Data " + url)
    connection.close()
    
    for i in range(0,10):
        time.sleep(0.5)
        if redisNameToHash.exists(url):
            myhash = redisNameToHash.get(url)
#            if redisHashToObama.exists(myhash):
#                isObama = redisHashToObama.get(myhash).decode("utf-8") 
#                print("is obama: ", isObama)
#                return jsonify(is_obama=isObama)
            if redisHashToHashSet.exists(myhash):
                hasheSet = list(redisHashToHashSet.smembers(myhash))
                hashes = [hash.decode("utf-8") for hash in hasheSet]
                print('got hashes')
                return jsonify(hash_list = hashes)

    if redisNameToHash.exists(url):
        return jsonfiy(hash_list = "no matching images")
    else:
        return Response(status=500)

print('pooooo')

app.debug = True
app.run(host="0.0.0.0", port=5000)


