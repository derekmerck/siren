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

# siren-prod
# ROOT_PATH    = "/data/incoming"
# ORTHANC_URL  = "http://orthanc-queue:8042"
# CACHE_FILE   = "/data/tmp/hashes.pkl"

# dev-staging
ORTHANC_QUEUE_URL   = "http://localhost:8043"
ORTHANC_ARCHIVE_URL = "http://localhost/hobit/"
CACHE_FILE          = "/tmp/hashes.pkl"

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    O = ObservableOrthanc(url=ORTHANC_QUEUE_URL)
    P = ObservableOrthanc(url=ORTHANC_ARCHIVE_URL)
    H = HashRegistry(cache_file=CACHE_FILE)

    def handle_study(event: Event, source: ObservableOrthanc):
        logging.debug(event)
        study_oid = event.data.get("oid")
        anonymize_and_send_w_registry(study_oid, source, H, P)

    t_file = Trigger(
        source=O,
        event_type=DicomEventType.STUDY_STABLE,
        handler=print
        # handler=handle_file
    )

    W = Watcher(triggers=[t_file])
    W.run()
