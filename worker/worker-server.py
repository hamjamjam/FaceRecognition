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
import inspect
import urllib.request
import requests
from io import BytesIO

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
redisFaceToHashSet = redis.Redis(host=redisHost, db=5) # Key -> Set
redisHashToObama = redis.Redis(host=redisHost, db=6)
redisNameToHash.set('foo','bar')
print(redisNameToHash.get('foo'))

def isMatch(face_encodings, face_encodings_serialized):
    is_match = False
    for face_enc_ser in face_encodings_serialized:
        match_results = face_recognition.compare_faces(face_encodings, pickle.loads(face_enc_ser))
        if match_results.count(True) > 0:
            return True
    return False

def isObama(face_encoding):
    # Pre-calculated face encoding of Obama generated with face_recognition.face_encodings(img)
    known_face_encoding = [-0.09634063,  0.12095481, -0.00436332, -0.07643753,  0.0080383,
                            0.01902981, -0.07184699, -0.09383309,  0.18518871, -0.09588896,
                            0.23951106,  0.0986533 , -0.22114635, -0.1363683 ,  0.04405268,
                            0.11574756, -0.19899382, -0.09597053, -0.11969153, -0.12277931,
                            0.03416885, -0.00267565,  0.09203379,  0.04713435, -0.12731361,
                           -0.35371891, -0.0503444 , -0.17841317, -0.00310897, -0.09844551,
                           -0.06910533, -0.00503746, -0.18466514, -0.09851682,  0.02903969,
                           -0.02174894,  0.02261871,  0.0032102 ,  0.20312519,  0.02999607,
                           -0.11646006,  0.09432904,  0.02774341,  0.22102901,  0.26725179,
                            0.06896867, -0.00490024, -0.09441824,  0.11115381, -0.22592428,
                            0.06230862,  0.16559327,  0.06232892,  0.03458837,  0.09459756,
                           -0.18777156,  0.00654241,  0.08582542, -0.13578284,  0.0150229 ,
                            0.00670836, -0.08195844, -0.04346499,  0.03347827,  0.20310158,
                            0.09987706, -0.12370517, -0.06683611,  0.12704916, -0.02160804,
                            0.00984683,  0.00766284, -0.18980607, -0.19641446, -0.22800779,
                            0.09010898,  0.39178532,  0.18818057, -0.20875394,  0.03097027,
                           -0.21300618,  0.02532415,  0.07938635,  0.01000703, -0.07719778,
                           -0.12651891, -0.04318593,  0.06219772,  0.09163868,  0.05039065,
                           -0.04922386,  0.21839413, -0.02394437,  0.06173781,  0.0292527 ,
                            0.06160797, -0.15553983, -0.02440624, -0.17509389, -0.0630486 ,
                            0.01428208, -0.03637431,  0.03971229,  0.13983178, -0.23006812,
                            0.04999552,  0.0108454 , -0.03970895,  0.02501768,  0.08157793,
                           -0.03224047, -0.04502571,  0.0556995 , -0.24374914,  0.25514284,
                            0.24795187,  0.04060191,  0.17597422,  0.07966681,  0.01920104,
                           -0.01194376, -0.02300822, -0.17204897, -0.0596558 ,  0.05307484,
                            0.07417042,  0.07126575,  0.00209804]
        
    is_obama = False
    match_results = face_recognition.compare_faces([known_face_encoding], face_encoding)
    if match_results[0]:
        is_obama = True
        return is_obama
    return is_obama

        
def callback2(ch, method, properties, inputbody):
    try:
        body = inputbody.decode("utf-8")
        print(body)
        print('callback made')
        responsekey = "hashes_of_corr_images"
        if redisNameToHash.exists(body):
            print('name exists')
            return
    except Exception as e:
        img_hash = '0'
        print(e)
    
    try:
        response = requests.get(body)
        img = Image.open(BytesIO(response.content))
        m = hashlib.md5()
        with io.BytesIO() as memf:
            img.save(memf, 'PNG')
            data = memf.getvalue()
            m.update(data)
        img_hash = m.hexdigest()
    except Exception as e:
        print("img hash failed: ", e)
        img_hash = '0'
    
    print(img_hash)
    
    try:
        if redisHashToFaceRec.exists(img_hash):
            redisNameToHash.set(body, img_hash)
            redisHashToName.sadd(img_hash, body)
            return
    
        response = requests.get(body)
        fileObject = BytesIO(response.content)
        image = face_recognition.load_image_file(fileObject)
        print('loaded image')
        face_encodings = list(face_recognition.face_encodings(image))
        face_encodings_serialized = [pickle.dumps(encoding) for encoding in face_encodings]
        
    except Exception as e:
        print("face_ecodings failed: ", e)  
        
    try:    
        if len(face_encodings) > 0:
            print('adding faces')
            print(type(face_encodings))
            print(type(img_hash))
            for key in redisHashToFaceRec.keys():
                face_enc_saved = redisHashToFaceRec.smembers(key)
                face_enc_saved = list(face_enc_saved)
                if isMatch(face_encodings, face_enc_saved):
                    redisHashToHashSet.sadd(img_hash, key)
                    redisHashToHashSet.sadd(key, img_hash)
            
            redisHashToFaceRec.sadd(img_hash, *face_encodings_serialized)
            print('if there were faces, added to redis')

        has_obama = 'no'
        for face_enc in face_encodings:
            if isObama(face_enc):
                has_obama = 'yes'
                break
        redisHashToObama.set(img_hash, has_obama)
    
        
        #hasheSet = list(redisHashToHashSet.smembers(img_hash))
        #hashes = [hash.decode("utf-8") for hash in hasheSet]
        #print('got hashes')
        
        redisHashToName.sadd(img_hash, body)
        print('set hash to name')
        
        redisNameToHash.set(body, img_hash)
        print('set name to hash')
    
    except Exception as e:
        print("something failed: ", e)  


def wrapped_callback(ch, method, properties, inputBody):
    print("wrapper: got callback")
    try: 
        callback2(ch, method, properties, inputBody)
    except Exception as e:
        print("ya dun fucked up mate: ", e)

def main():
    print('running main')
    
    credentials=pika.PlainCredentials('guest','guest')
    parameters = pika.ConnectionParameters(rabbitMQHost, 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    #connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
    channel = connection.channel()
    channel.queue_declare(queue='work')
    print('connection made')
    print(inspect.getargspec(channel.basic_consume))
    
    def callback(ch, method, properties, inputbody):
        print('callback made')
        body = inputbody.decode("utf-8")
        
        responsekey = "hashes_of_corr_images"
        if redisNameToHash.exists(body):
            img_hash = redisNameToHash.get(body)
            hashes = redisHashToHashSet.get(img_hash)
            result = {responsekey: hashes    }
            return jsonify(result)
    
        img_hash = hashlib.md5(Image.open(body).tobytes())

        if redishHashToFaceRec.exists(img_hash):
            redisNameToHash.set(body, img_hash)
            redisHashToName.sadd(img_hash, body)
            hashes = redisHashToHashSet.get(img_hash)
            result = {responsekey: hashes    }
            return jsonify(result)

        img = face_recognition.load_image_file(body)

        face_encodings = face_recognition.face_encodings(img)

        redisNameToHash.set(body, img_hash)
        redisHashToName.set(img_hash, body)
        redisHashToFaceRec.set(img_hash, *set(face_encodings))

        otherHash = {}



    channel.basic_consume(queue='work', on_message_callback=wrapped_callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
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
