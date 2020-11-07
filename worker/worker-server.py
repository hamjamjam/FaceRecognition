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

redisHost = os.getenv("REDIS_HOST") or "redis"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "rabbitmq"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

import face_recognition
from flask import Flask, jsonify, request, redirect

# You can change this to any folder on your system

redisNameToHash = redis.Redis(host=redisHost, db=1)    # Key -> Value
redisHashToName = redis.Redis(host=redisHost, db=2)    # Key -> Set
redisHashToFaceRec = redis.Redis(host=redisHost, db=3) # Key -> Set
redisHashToHashSet = redis.Redis(host=redisHost, db=4) # Key -> Set
redisFaceToHashSet = redis.Redis(host=redisHost, db=4) # Key -> Set
redisNameToHash.set('foo','bar')

def main():
    print('running main')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
    channel = connection.channel()
    channel.queue_declare(queue='work')
    print('connection made')
    
    def callback(ch, method, properties, body):
    ##body is image url
        print('callback made')
        responsekey = "hashes_of_corr_images"
        if redisNameToHash.exists(body):
            img_hash = redisNameToHash.get(body)
            hashes = redisHashtoHashSet.get(img_hash)
            result = {responsekey: hashes    }
            return jsonify(result)
    
        img_hash = hashlib.md5(Image.open(body).tobytes())

        if redishHashToFaceRec.exists(img_hash):
            redisNameToHash.set(body, img_hash)
            redisHashToName.sadd(img_hash, body)
            hashes = redisHashtoHashSet.get(img_hash)
            result = {responsekey: hashes    }
            return jsonify(result)

        img = face_recognition.load_image_file(body)

        face_encodings = face_recognition.face_encodings(img)

        redisNameToHash.set(body, img_hash)
        redisHashToName.set(img_hash, body)
        redisHashToFaceRec.set(img_hash, *set(face_encodings))

        otherHash = {}

        for face_enc in face_encodings:
            try:
                otherHash.add(redisFaceToHashSet.get(face_enc))
            except:
                pass
            redisFaceToHashSet.sadd(face_enc, img_hash)

        redisHashtoHashSet.sadd(img_hash, *otherHash)

        hashes = redisHashtoHashSet.get(img_hash)
        result = {responsekey: hashes    }
        return jsonify(result)


    channel.basic_consume(
        queue='work', on_message_callback=callback, auto_ack=True)
    #  print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
