# Solution

## Redis and RabbitMQ
I did not make changes to these

## Rest server
I set up the rest server to listen to the existing rest client and work with the url command.

The rest server sends along an image url to Rabbit (which passes it to the worker).

The rest server then checks redis to see if the k, v store containing url and hash exists. If a hash exists (which means the image was properly processed), it then starts checking redis for the hash to the hashes of other images in the database with a face match until it either times out (5s) or it gets something back.

If the rest server cannot find a list of other hashes but it CAN find the hash of the image (from url), then it assumes that the image was processed by did not have any matches and so it returns to the client 'no matches found'.

If the rest server can find a list of other hashes, it will decode them and hand them back to the client as a list.


## Worker
I set up the worker to consume the rabbitMQ queue

the worker first hashes the image from url.

It then gets the face encodings of the image.

It then checks the entire database of stored images for a match (if the images contain multiple faces, just one face needs to match). If there is a match, the two images get added to each other's hash set.


## Build, Test and Debug
OH BOY.
There are several build, test and debug scripts sitting around in the repo.
`/rest/build-rest.sh` builds the rest server (got kind of annoying)
`/worker/Makefile.sh` builds the worker from the image provided

`/get-logs.sh` takes input (e.g. worker) and spits out the logs files
`/rest/test-rest.sh` takes input (e.g. image url) and runs the client script

By using my `\get-logs.sh` command and ensuring that each pod would write python print output to the log files, I was able to effectively debug syntax with regards to having each service/container/pod talk to the right thing.

Rabbit and Redis were pretty well behaved and neither required an extrenal IP to be run within the same Kube cluster; I was able to just set the hostnames to 'rabbitmq' and 'redis' respectively.

Connecting to Rabbit, sending and consuming was a matter of using the example that their docs give.

I troubleshot the worker script by getting a shell to the worker container and running various test python scripts from there.
