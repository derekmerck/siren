from pprint import pprint
import hashlib
from diana.services import HashRegistry
from diana.dicom import DLv
from diana.dicom import DcmUIDMint

RUN_PROD = False

if RUN_PROD:
    CACHE_FILE = "/tmp/hashes.pkl"
else:
    CACHE_FILE = "/tmp/hashes-s.pkl"

if __name__ == "__main__":

    H = HashRegistry(cache_file=CACHE_FILE)
    d = H.find(q={"dlvl": DLv.STUDY})
    D = DcmUIDMint()
    for v in d.values():
        stu_mhash = v["mhash"]
        stu_dhash = v["dhash"]
        sham_study_uid = D.content_hash_uid(stu_mhash, stu_dhash, DLv.STUDY)
        sham_accession_number = hashlib.sha3_224(sham_study_uid.encode("utf8")).hexdigest()
        v["sham_acc_num"] = sham_accession_number
    pprint(list(d.values()))

