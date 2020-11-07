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

#
# $ curl -XPOST -F "file=@obama2.jpg" http://127.0.0.1:5001
#
# Returns:
#
# {
#  "face_found_in_image": true,
#  "is_picture_of_obama": true
# }
#
redisHost = os.getenv("REDIS_HOST") or "redis"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "rabbitmq"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

import face_recognition
from flask import Flask, jsonify, request, redirect

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='work')

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

redisNameToHash = redis.Redis(host=redisHost, db=1)    # Key -> Value
redisHashToName = redis.Redis(host=redisHost, db=2)    # Key -> Set
redisHashToFaceRec = redis.Redis(host=redisHost, db=3) # Key -> Set
redisHashToHashSet = redis.Redis(host=redisHost, db=4) # Key -> Set
redisFaceToHashSet = redis.Redis(host=redisHost, db=4) # Key -> Set
r.set(‘foo’,’bar’)
r.get(‘foo’)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Is this a picture of Obama?</title>
    <h1>Upload a picture and see if it's a picture of Obama!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''
  
  
def callback(ch, method, properties, body):
  ##body is image url
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
