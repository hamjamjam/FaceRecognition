# Face Recognition as a Service

This is an implementation of a service that takes in an image URL, hashes the image, and returns a list of hashes (or an empty list) of images in which there is a face match.

It uses the following open source face recognition software:

`https://github.com/ageitgey/face_recognition`

## About the service

The service has been written to run on a Kubernetes cluster. It uses RabbitMQ for queuing, a Redis database and a REST API.

This was done as part of a class, CSCI 5253: Datacenter Scale Computing, taken at the University of Colorado Boulder.
