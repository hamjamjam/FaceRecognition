#!/bin/bash
img_file="${1:-https://upload.wikimedia.org/wikipedia/commons/a/a0/Pierre-Person.jpg}"
IP=$(kubectl get services | grep ^rest | awk '{print $4}')
python3 rest-client.py ${IP}:5000 url "${img_file}" 1
# https://static.toiimg.com/photo/msid-68523832/68523832.jpg 1
