import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from src.review import decide
from src.publish import authorize
from src.artifacts import validate,REQUIRED
from src.common import sha,write,owner_only
DIGEST="a"*64
RID="123"
MANIFEST={"run_id":RID,"mode":"episode","demo":False}
def record(status="approved"):
 return {"run_id":RID,"manifest_sha256":DIGEST,"mode":"episode","demo":False,"status":status}
class Safety(unittest.TestCase):
 def test_pending_cannot_upload(self):
  with self.assertRaises(PermissionError):authorize(record("pending"),"upload_private",RID,DIGEST,"UPLOAD:"+RID+":"+DIGEST)
 def test_rejected_cannot_upload(self):
  with self.assertRaises(PermissionError):authorize(record("rejected"),"upload_private",RID,DIGEST,"UPLOAD:"+RID+":"+DIGEST)
 def test_exact_approved_version_can_upload(self):
  authorize(record(),"upload_private",RID,DIGEST,"UPLOAD:"+RID+":"+DIGEST)
 def test_wrong_digest(self):
  with self.assertRaises(ValueError):authorize(record(),"upload_private",RID,"b"*64,"UPLOAD:"+RID+":"+DIGEST)
 def test_wrong_run(self):
  with self.assertRaises(ValueError):authorize(record(),"upload_private","456",DIGEST,"UPLOAD:"+RID+":"+DIGEST)
 def test_plain_yes_is_not_approval(self):
  with self.assertRaises(PermissionError):authorize(record(),"upload_private",RID,DIGEST,"yes")
 def test_public_needs_separate_confirmation(self):
  r={**record("uploaded_private"),"youtube_id":"video123"}
  with self.assertRaises(PermissionError):authorize(r,"make_public",RID,DIGEST,"UPLOAD:"+RID+":"+DIGEST)
  authorize(r,"make_public",RID,DIGEST,"PUBLIC:video123")
 def test_demo_cannot_be_approved(self):
  with self.assertRaises(ValueError):decide(None,"approve",RID,DIGEST,{**MANIFEST,"mode":"smoke","demo":True},"owner")
 def test_demo_cannot_upload(self):
  with self.assertRaises(PermissionError):authorize({**record(),"demo":True},"upload_private",RID,DIGEST,"UPLOAD:"+RID+":"+DIGEST)
 def test_rejection_is_final(self):
  r=decide(None,"reject",RID,DIGEST,MANIFEST,"owner")
  with self.assertRaises(ValueError):decide(r,"approve",RID,DIGEST,MANIFEST,"owner")
 def test_ambiguous_upload_cannot_repeat(self):
  with self.assertRaises(PermissionError):authorize(record("upload_in_progress"),"upload_private",RID,DIGEST,"UPLOAD:"+RID+":"+DIGEST)
 def test_only_owner_on_main(self):
  with patch.dict("os.environ",{"GITHUB_ACTOR":"other","GITHUB_REF":"refs/heads/main"}):
   with self.assertRaises(PermissionError):owner_only()
 def test_reviewer_cannot_use_other_branch(self):
  with patch.dict("os.environ",{"GITHUB_ACTOR":"beshopauls95-crypto","GITHUB_REF":"refs/heads/other"}):
   with self.assertRaises(PermissionError):owner_only()
 def test_modified_video_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   for f in REQUIRED:(p/f).write_text("{}")
   write(p/"quality.json",{"passed":True})
   m={**MANIFEST,"files":{f:sha(p/f) for f in REQUIRED}}
   write(p/"manifest.json",m);expected=sha(p/"manifest.json")
   validate(p,RID,expected)
   (p/"video.mp4").write_text("changed")
   with self.assertRaises(ValueError):validate(p,RID,expected)
if __name__=="__main__":unittest.main()
