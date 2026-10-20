import unittest
from src.upload_test import validate_test
from src.publish import authorize
R="123";D="a"*64
M={"run_id":R,"mode":"smoke","demo":True}
Q={"passed":True,"seconds":5.1}
C="TEST_PRIVATE:"+R+":"+D
class TechnicalUploadTests(unittest.TestCase):
    def test_explicit_private_sample(self):
        validate_test(M,Q,R,D,C,None)
    def test_generic_approval_rejected(self):
        with self.assertRaises(PermissionError):validate_test(M,Q,R,D,"yes",None)
    def test_duplicate_or_ambiguous_upload_rejected(self):
        for state in ("upload_in_progress","uploaded_needs_verification","uploaded_private"):
            with self.assertRaises(PermissionError):validate_test(M,Q,R,D,C,{"status":state})
    def test_wrong_sample_rejected(self):
        with self.assertRaises(ValueError):validate_test({**M,"run_id":"456"},Q,R,D,C,None)
    def test_episode_cannot_use_test_path(self):
        with self.assertRaises(ValueError):validate_test({**M,"demo":False,"mode":"episode"},Q,R,D,C,None)
    def test_bad_qa_rejected(self):
        with self.assertRaises(ValueError):validate_test(M,{"passed":False,"seconds":5},R,D,C,None)
    def test_sample_still_cannot_go_public(self):
        record={**M,"manifest_sha256":D,"status":"uploaded_private","youtube_id":"test"}
        with self.assertRaises(PermissionError):authorize(record,"make_public",R,D,"PUBLIC:test")
