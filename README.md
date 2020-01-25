# LIFX Day and Dusk in a Docker Container

This container reproduces the LIFX Day and Dusk scheduling functionality 
locally but removes the dependency on the LIFX Cloud and adds 
fine-grained control over timing, kelvin value and power status. 

# WORK-IN-PROGRESS

Currently this image does nothing. Hopefully it'll do something useful soon.

## Running the container

LIFX discovery is done using UDP broadcast packets, so the container either
needs to be directly connected to the host network (`--net=host`) or have
its own IP address via a Docker MACVLAN based network.

The example below uses the simpler option of just binding to the host network.
Note that this method _does not work_ if you're using Docker for Mac.

```
docker run --name=daydusk --detach --net=host avmiller/docker-lifx-daydusk
```

## Building the container

If you want to build your own image, just checkout the repo and run:

```
docker build -t myimage:tag .
```
