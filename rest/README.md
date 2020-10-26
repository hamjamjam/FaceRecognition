# REST API and interface

You must create a deployment that creates an external endpoint using a load balancer or ingress node. This deployment external endpoint in your cluster.

You must provide a `rest-server.py` that implements a Flask server that responds to the routes below. We have provided a `rest-client.py` that can send images to the `rest-server.py`.

The REST service takes in named images or URL's for images and sends those to the worker nodes for processing. Because it may take some time to process an image, the REST service returns a hash that can be used for further queries to see if the image contains faces and the names or URL's of matching images. You do not need to store the actual images. You can assume that URL's are unique that that once one has been processed, you don't need to process it again. You can't make the same assumption for filenames. However, you can assume that the hash of an image can be used to uniquely identify the image.

The REST routes are:

+ /scan/image/[filename] [POST] - scan the picture passed as the content of the request and with the specified filename. Compute [a hash of the contents](https://docs.python.org/3/library/hashlib.html) and send the hash and image to a worker using the `toWorker` rabbitmq exchange. The work will add the filename to the Redis database as described in the worker documentation. The response of this API should be a JSON document containing a single field `hash` that is the hash used to identify the provided image for subsequent `match` queries. For example:
```
  { 'hash' : "abcedef...128" }
```
+ /scan/url [POST] - the request body should contain a json message with a URL specifying an image. The format of the json object should be `{ "url" : "http://whatever.jpg"}`. The REST server [should retrieve the image](https://www.tutorialspoint.com/downloading-files-from-web-using-python) and proceed as for `/scan/image` but use the URL as the file name. We assume that URL's are unique, so if you've already processed it once, you don't need to do it again.
+ /match/[hash] [GET] -- using the hash, return a list of the image name or URL's that contain matching faces. If the hash doesn't match or there are no faces in the image, an empty list is returned.

Your server should be robust to failure of RabbitMQ connections. This can be difficult to do if you just open the connections at the start of the code as provided in the starter code. You can take advantage of Kubernetes by simply exiting the container which will cause the pod to restart. Normally, [Flask catches all exceptions which prevents your program from exiting](https://flask.palletsprojects.com/en/1.1.x/errorhandling/). You can override that using the following code.
```
@app.errorhandler(Exception)
def handle_exception(e):
    os._exit(1)
```

### Development Steps
You will need two RabbitMQ exchanges.
+ A `topic` exchange called `logs` used for debugging and logging output
+ A `direct` exchange called `toWorker` used by the REST API to send images to the worker

You should use the topic exchange for debug messages with the topics `[hostname].rest.debug` and `[hostname].rest.info`, substituting the proper hostname. You can include whatever debugging information you want, but you must include a message for each attempted API call and the outcome of that call (successful, etc).

You may find it useful to create a `logs` container and deployment that listen to the logs and dumps them out to `stderr` so you can examine them using `kubectl logs..`.

When installing the `pika` library used to communicate with `rabbitmq`, you should use the `pip` or `pip3` command to install the packages in your container. The solution code uses the following packages:
```
sudo pip3 install --upgrade pika redis jsonpickle requests flask
```
