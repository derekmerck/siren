"""
This script automatically registers and queues files as they arrive in
the incoming folder.
"""

import logging
from libsvc.daemon import Watcher, Trigger, Event
from diana.daemons import ObservableOrthanc, DicomEventType
from diana.services import HashRegistry
from diana.dicom import DLv
from onetime_anon_and_send import anonymize_and_send_w_registry

# CONFIG

UPLOAD_DICOM   = True
ANNOUNCEMENT_INTERVAL = 10

RUN_PROD = False

if RUN_PROD:
    # siren-prod
    ORTHANC_QUEUE_URL  = "http://queue:8042"
    ORTHANC_PEER_URL  = "http://localhost/hobit/"
    CACHE_FILE   = "/data/tmp/hashes.pkl"
else:
    # siren-staging
    ORTHANC_QUEUE_URL  = "http://queue-s:8042"
    ORTHANC_PEER_URL  = "http://localhost/hobit-staging/"
    CACHE_FILE   = "/data/tmp/hashes-s.pkl"


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    O = ObservableOrthanc(url=ORTHANC_QUEUE_URL)
    P = ObservableOrthanc(url=ORTHANC_PEER_URL)
    H = HashRegistry(cache_file=CACHE_FILE)

    def handle_study(event: Event, source: ObservableOrthanc):
        logging.debug(event)
        study_oid = event.data.get("oid")
        anonymize_and_send_w_registry(study_oid, source, H, P)

    t_file = Trigger(
        source=O,
        event_type=DicomEventType.STUDY_STABLE,
        # handler=print
        handler=handle_study
    )

    W = Watcher(triggers=[t_file])
    W.run()
