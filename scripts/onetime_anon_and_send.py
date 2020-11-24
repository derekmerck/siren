"""
Step 2:  Assign id to stable studies and send to archive

Given a stable study, retag _all_ instances with content-based
DICOM UIDs, anonymize, and optionally send to peer node for
review.

It is impossible to tag with a reproducible, content-based hash
until a study is stable.
"""

"""
Timing:
  dev:  0.62 dx/s
"""

from pprint import pprint
import time
import hashlib
import typing as typ
from diana.dicom import DLv
from diana.dixel import Dixel, orthanc_sham_map
from diana.services import Orthanc, HashRegistry
from diana.services.orthanc import oid_from

CLEAR_SOURCE = False
ANNOUNCMENT_INTERVAL = 10

# Test study oid
STUDY_OID = ""

# siren-prod
# ORTHANC_QUEUE_URL = "http://orthanc-queue:8042"
# ORTHANC_PEER_URL  = "http://localhost/hobit/"
# CACHE_FILE = "/data/tmp/hashes.pkl"

# dev-staging
ORTHANC_QUEUE_URL = "http://localhost:8043"
ORTHANC_PEER_URL  = "http://localhost/hobit-staging/"
CACHE_FILE        = "/tmp/hashes.pkl"
# todo: Peer must have "diana-hash" metadata name assigned and stash info


def anonymize_and_send_w_registry(
        study_oid: str,
        O: Orthanc,
        H: HashRegistry,
        P: Orthanc = None,
        clear_source: bool = False
    ):

    tic = time.time()
    n = 0

    if P is None:
        P = O  # Stash result in-place

    study_dx = O.get(study_oid)
    study_dx.dhash = H.get(study_dx.mhash)["dhash"]
    study_info = O.get(study_oid, view="raw")
    new_inst_info = None
    for ser_oid in study_info["Series"]:
        ser_dx = O.get(ser_oid, dlvl=DLv.SERIES)
        ser_dx.dhash = H.get(ser_dx.mhash)["dhash"]
        ser_info = O.get(ser_oid, dlvl=DLv.SERIES, view="raw")
        for inst_oid in ser_info["Instances"]:
            n += 1
            if n % ANNOUNCMENT_INTERVAL == 0:
                print(f"Processed {n} instances")
                H.shelve()

            inst_dx = O.get(inst_oid, dlvl=DLv.INSTANCE)
            inst_dx.dhash = H.get(inst_dx.mhash)["dhash"]

            def best_pt_id(dx: Dixel):
                candidate = dx.tags.get("PatientID", "")
                if candidate != "":
                    return candidate
                candidate = dx.tags.get("PatientName", "")
                if candidate != "":
                    return candidate
                return "UNKNOWN"

            m = orthanc_sham_map(
                stu_mhash=study_dx.mhash,
                stu_dhash=study_dx.dhash,
                patient_id=best_pt_id(study_dx),
                stu_dt=study_dx.timestamp,

                ser_mhash = ser_dx.mhash,
                ser_dhash = ser_dx.dhash,
                ser_dt = ser_dx.timestamp,

                inst_mhash = inst_dx.mhash,
                inst_dhash = inst_dx.dhash,
                inst_dt = inst_dx.timestamp
            )

            s = [ m["Replace"]["PatientID"],
                  m["Replace"]["StudyInstanceUID"],
                  m["Replace"]["SeriesInstanceUID"],
                  m["Replace"]["SOPInstanceUID"] ]
            expected_oid = oid_from(s)

            # TODO: Prefer to check this in put??
            # if H.exists(expected_oid):
            #     # print("Skipping existing")
            #     continue

            bin = O.anonymize(inst_oid, dlvl=DLv.INSTANCE, replacement_map=m)  # Anon inst no longer returns image?
            new_bhash = hashlib.sha224( bin ).hexdigest()
            new_inst_info = P.put(raw=bin)
            new_inst = P.get(new_inst_info["ID"], dlvl=DLv.INSTANCE)
            new_inst.bhash = new_bhash
            new_inst.dhash = inst_dx.dhash
            # P.put_metadata(new_inst.oid(), DLv.INSTANCE, "diana-hash", new_inst.dhash)
            # if new_inst is not None:
            #     H.get(inst_dx.mhash)["ShamAccNum"] = m["Replace"]["AccessionNumber"]
                # H.put(new_inst, link_duplicates=True)
                # H.set(new_inst.oid(), new_inst.mhash)
            if clear_source:
                O.delete(inst_oid, dlvl=DLv.INSTANCE)
        # if new_inst_info is not None:
            # new_ser = P.get(new_inst_info["ParentSeries"])
            # H.set(new_ser.oid(), new_ser.mhash)
            # H.get(ser_dx.mhash)["ShamAccNum"] = m["Replace"]["AccessionNumber"]
            # P.put_metadata(new_ser.oid(), DLv.SERIES, "diana-hash", ser_dx.dhash)
            # H.link(new_ser.mhash, ser_dx.mhash)
    # if new_inst_info is not None:
    #     H.get(study_dx.mhash)["ShamAccNum"] = m["Replace"]["AccessionNumber"]

        # new_stu = P.get(new_inst_info["ParentStudy"])
        # H.set(new_stu.oid(), new_stu.mhash)
        # # P.put_metadata(new_stu.oid(), DLv.STUDY, "diana-hash", study_dx.dhash)
        # H.link(new_stu.mhash, study_dx.mhash)

    toc = time.time()
    print(f"----------------------------")
    print(f"Uploaded {n} files")
    print(f"Elapsed time: {toc-tic:.2f} ({max([n,1])/(toc-tic):.2f}dx/s)")
    print(f"----------------------------")

    H.shelve()


def anon_and_push_all(queue: Orthanc,
                      reg: HashRegistry,
                      archive: Orthanc = None,
                      clear_source: bool = False):

    for oid in queue.inventory():
        anonymize_and_send_w_registry(oid, queue, reg, archive, clear_source)


if __name__ == "__main__":

    O = Orthanc(url=ORTHANC_QUEUE_URL)
    P = Orthanc(url=ORTHANC_PEER_URL)
    H = HashRegistry(cache_file=CACHE_FILE)
    # anonymize_and_send_w_registry(STUDY_OID, O, H, P, clear_source=CLEAR_SOURCE)

    anon_and_push_all(O, H, P, clear_source=CLEAR_SOURCE)
