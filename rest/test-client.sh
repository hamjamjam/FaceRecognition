IP=$(kubectl get services | grep ^rest | awk '{print $4}')
python3 rest-client.py 34.122.233.94:5000 url https://storage.googleapis.com/cu-csci-5253/lfw/AJ_Cook.jpg 1
