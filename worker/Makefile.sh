##
## You provide this to build your docker image
##
version=$1
export PROJECT_ID=jamiess-1470077384373
docker build -t worker:${version} .
docker build -t gcr.io/${PROJECT_ID}/worker:${version} .
docker push gcr.io/${PROJECT_ID}/worker:${version} 
kubectl create deployment worker --image=gcr.io/${PROJECT_ID}/worker:${version}
