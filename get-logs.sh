deployment=$1
pod=${kubectl get pods | grep ^${deployment} | awk '{print $1}'}
kubectl logs ${pod}
