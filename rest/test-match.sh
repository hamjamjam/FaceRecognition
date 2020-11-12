#!/bin/bash
img_hash="${1:-'9a64dc44fd860d5541c9ec0d4e359efe'}"
IP=$(kubectl get services | grep ^rest | awk '{print $4}')
python3 rest-client.py ${IP}:5000 match "${img_hash}" 1
