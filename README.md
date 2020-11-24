# Siren Services

## Startup Services

Creates the following services on host:
- Traefik router
- Orthanc HOBIT archive
- Orthanc HOBIT queue
- Orthanc HOBIT archive - staging
- Orthanc HOBIT queue - staging
- DIANA worker w volume binding to /data/incoming

```
$ cd dev/siren/docker-compose
$ docker-compose up
```

Services all set to restart, so the services are robust against system resets.

## Launching the file watcher

Instruct the worker to run a file watcher from `/data/incoming` to the queue.

Make sure we are on latest

```
$ docker exec -it diana /bin/bash
$ cd /opt/diana3
$ git pull
```