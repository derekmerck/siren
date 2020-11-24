"""
This script automatically registers and queues files as they arrive in
the incoming folder.
"""

import logging
from libsvc.daemon import Watcher, Trigger, Event, FileEventType
from diana.daemons import ObservableDicomDir
from diana.services import Orthanc, HashRegistry

# CONFIG
UPLOAD_DICOM   = True
ANNOUNCEMENT_INTERVAL = 10
RUN_PROD = False

if RUN_PROD:
    # siren-prod
    ROOT_PATH    = "/data/incoming"
    ORTHANC_URL  = "http://queue:8042"
    CACHE_FILE   = "/data/tmp/hashes.pkl"
else:
    # siren-staging
    ROOT_PATH    = "/data/incoming"
    ORTHANC_URL  = "http://queue-s:8042"
    CACHE_FILE   = "/data/tmp/hashes-s.pkl"


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    D = ObservableDicomDir(root=ROOT_PATH)
    H = HashRegistry(cache_file=CACHE_FILE)
    Q = Orthanc(url=ORTHANC_URL)

    def handle_file(event: Event, source: ObservableDicomDir):
        logging.debug(event)
        fp = event.data.get("fp")
        dx = source.get(fp,
                   # bhash_validator=lambda x: not H.exists,
                   binary=True,
                   ignore_errors=True)
        if dx is not None:
            logging.debug(f"putting {dx}")
            H.put(dx)
            if UPLOAD_DICOM and Q is not None:
                Q.put(dx)

    t_file = Trigger(
        source=D,
        event_type=FileEventType.FILE_ADDED,
        # handler=print
        handler=handle_file
    )

    W = Watcher(triggers=[t_file])

    D.poll_events()
    W.run()
