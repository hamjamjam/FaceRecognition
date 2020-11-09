# Solution

## Redis and RabbitMQ
I did not make changes to these

## Rest server
I set up the rest server to listen to the existing rest client and work with the url command.

The rest server sends along an image url to Rabbit (which passes it to the worker).

The rest server then checks redis to see if the k, v store containing url and hash exists. If a hash exists, it then starts checking redis for the hash to isObama database until it either times out (5s) or it finds the image hash in the isObama database.

The server then hands back to the client whether or not the image contained Obama.

There is also a database that stores python pickled versions of all the face encodings of each image submitted, but I got tired and did not implement the full "check every item in the database for a face match" part as the main point of the homework was getting Rabbit, Redis, an API and a worker to all talk to each other and running on a Kubernetes cluster which has been achieved.

## Worker
I set up the worker to consume the rabbitMQ queue

The worker does a lot of things; right now it will just tell you if your image contains Obama.

The worker will also save the image url, the image hash (so the server can pull up the image hash and then use the hash as a key for another Redis database).

The worker does some of the full face rec (i.e. stores pickled versions of face encodings)
