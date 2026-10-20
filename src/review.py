import os
from .common import owner_only,now
from .state import State
from .artifacts import download
def decide(old,decision,run_id,digest,manifest,actor):
 if old and (old["status"]!="pending" or old["manifest_sha256"]!=digest):raise ValueError("Version already decided or mismatched")
 if decision not in ("approve","reject"):raise ValueError("Unknown decision")
 if str(manifest["run_id"])!=run_id:raise ValueError("Wrong run")
 if decision=="approve" and (manifest.get("demo") or manifest.get("mode")!="episode"):raise ValueError("Demo cannot be approved for upload")
 return {"run_id":run_id,"manifest_sha256":digest,"status":"approved" if decision=="approve" else "rejected","reviewed_by":actor,"reviewed_at":now(),"mode":manifest["mode"],"demo":manifest.get("demo",True)}
def main():
 owner_only();s=State();rid=os.environ["TARGET_RUN"];digest=os.environ["MANIFEST_SHA"]
 folder,m=download(s,rid,digest)
 s.update("runs/"+rid,lambda old:decide(old,os.environ["DECISION"],rid,digest,m,os.environ["GITHUB_ACTOR"]))
 print("Decision recorded. No YouTube request made.")
if __name__=="__main__":main()
