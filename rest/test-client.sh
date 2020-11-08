IP=$(kubectl get services | grep ^rest | awk '{print $4}')
python3 rest-client.py ${IP}:5000 url https://static.toiimg.com/photo/msid-68523832/68523832.jpg 1
