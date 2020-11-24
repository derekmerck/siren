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
$ cd /opt/siren
$ git pull
```

Test connection

```
$ root@9ed454f28617:/opt/siren/scripts# ping queue-s
  PING queue-s (172.22.0.5) 56(84) bytes of data.
  64 bytes from orthanc-queue-staging.docker-compose_default (172.22.0.5): icmp_seq=1 ttl=64 time=0.151 ms
```
