# Siren Services

## Startup Services

Creates the following services on host:
- Traefik router
- Orthanc HOBIT archive
- Orthanc HOBIT queue
- Orthanc HOBIT archive (staging)
- Orthanc HOBIT queue (staging)
- DIANA worker w volume binding to `/data/incoming`

```
$ cd dev/siren/docker-compose
$ docker-compose up
```

Services all set to restart, so the services are robust against system resets.

## Launching the file watcher

Instruct the worker to run a file watcher from `/data/incoming` to the queue.

Start a screen session

```
$ screen
$ docker exec -it diana /bin/bash
```

Make sure we are on latest

```
$ cd /opt/diana && git pull
$ cd libsvc && git pull origin master
$ cd /opt/siren && git pull
```

Test connection

```
$ ping queue-s
  PING queue-s (172.22.0.5) 56(84) bytes of data.
  64 bytes from orthanc-queue-staging.docker-compose_default (172.22.0.5): icmp_seq=1 ttl=64 time=0.151 ms
```

Run the file watcher.

```
$ cd scripts
$ python auto_reg_and_enqueue
```

Test the watcher by copying some DICOM files around in `/data/incoming` on the host. DICOM files should show up on http://<host>:8042 (or 8043 for staging).  Non-DICOM creation events should be rejected.

This process is a pain to debug b/c the watcher can crash quietly, without bringing down the poller.  So it is useful to keep it on a screen for debugging.

