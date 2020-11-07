#!/bin/sh
#
# You can use this script to launch Redis and RabbitMQ on Kubernetes
# and forward their connections to your local computer. That means
# you can then work on your worker-server.py and rest-server.py
# on your local computer rather than pushing to Kubernetes with each change.
#
# To kill the port-forward processes us e.g. "ps augxww | grep port-forward"
# to identify the processes ids
#
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml
kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml

kubectl port-forward --address 0.0.0.0 service/rabbitmq 5672:5672 &
kubectl port-forward --address 0.0.0.0 service/redis-master 6379:6379 &

export PROJECT_ID=jamiess-1470077384373
docker build -t rest:v1 .
docker build -t gcr.io/${PROJECT_ID}/rest:v1 .
docker push gcr.io/${PROJECT_ID}/rest:v1
kubectl create deployment rest --image=gcr.io/${PROJECT_ID}/rest:v1
kubectl expose deployment rest --type=LoadBalancer --port 5000 --target-port 5000

docker build -t worker:v1 .
docker build -t gcr.io/${PROJECT_ID}/worker:v1 .
docker push gcr.io/${PROJECT_ID}/worker:v1 
kubectl create deployment worker --image=gcr.io/${PROJECT_ID}/worker:v1
