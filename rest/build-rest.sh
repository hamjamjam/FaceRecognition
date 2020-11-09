#!/bin/bash
version=$1
export PROJECT_ID=jamiess-1470077384373
docker build -t rest:${version} .
docker build -t gcr.io/${PROJECT_ID}/rest:${version} .
docker push gcr.io/${PROJECT_ID}/rest:${version}
kubectl create deployment rest --image=gcr.io/${PROJECT_ID}/rest:${version}
kubectl expose deployment rest --type=LoadBalancer --port 5000 --target-port 5000
