"""
Step 1:  Queue existing

Script to conduct a single-sweep a DicomDirectory object, register
content hashes with a HashRegistry, and optionally upload instances
to an Orthanc node.
"""

"""
Timing Data
------------
dev:
  registration:   113 dx/s
  register+upload: 30 dx/s
"""

import time
from pprint import pprint
from diana.services import HashRegistry, DicomDirectory, Orthanc
from diana.dicom import DLv

CLEAR_HASHES = False  # Reset hash registry
CLEAR_DICOM  = False  # Reset orthanc data
UPLOAD_DICOM = False  # Upload Dicom files
ANNOUNCEMENT_INTERVAL = 50

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


def register_path(D: DicomDirectory,
                  H: HashRegistry,
                  O: Orthanc=None,
                  upload: bool=False):

    print(f"Registering path {D.root}")
    tic = time.time()
    m, n, o = 0, 0, 0

    for fn in D.inventory():
        m += 1
        if m % ANNOUNCEMENT_INTERVAL == 0:
            print(f"Checked {m} files")
            H.shelve()
        dx = D.get(fn,
                   binary=True,
                   bhash_validator=lambda h: not H.exists(h),
                   ignore_errors=True)
        if dx is not None:
            if not H.exists(dx.mhash):
                n += 1
                if n % ANNOUNCEMENT_INTERVAL == 0:
                    print(f"Registered {n} files")
                H.put(dx)
                if upload and O is not None:
                    o += 1
                    if o % ANNOUNCEMENT_INTERVAL == 0:
                        print(f"Uploaded {o} files")
                    O.put(dx)

    toc = time.time()
    print(f"----------------------------")
    print(f"Checked {m} files")
    print(f"Registered new {n} instances")
    print(f"Uploaded {o} instances")
    print(f"Elapsed time: {toc-tic:.2f} ({max([n,1])/(toc-tic):.2f}dx/s)")
    print(f"----------------------------")

    H.shelve()

    pprint(H.find(q={"dlvl": DLv.STUDY}))


if __name__ == "__main__":

    D = DicomDirectory(root=ROOT_PATH)
    H = HashRegistry(clear_cache=CLEAR_HASHES, cache_file=CACHE_FILE)
    O = Orthanc(url=ORTHANC_URL)
    if CLEAR_DICOM:
        input("Are you sure that you want to clear the queue?")
        O.clear()
    register_path(D, H, O, upload=UPLOAD_DICOM)
