import base64,json,os
from .common import requests
class State:
 def __init__(self):
  self.repo=os.environ["GITHUB_REPOSITORY"];self.base="https://api.github.com/repos/"+self.repo
  self.s=requests.Session();self.s.headers.update({"Authorization":"Bearer "+os.environ["GH_TOKEN"],"Accept":"application/vnd.github+json","User-Agent":"CivilizationSecrets/1.0"})
  r=self.s.get(self.base+"/git/ref/heads/channel-state",timeout=30)
  if r.status_code==404:
   h=self.s.get(self.base+"/git/ref/heads/main",timeout=30);h.raise_for_status()
   r=self.s.post(self.base+"/git/refs",json={"ref":"refs/heads/channel-state","sha":h.json()["object"]["sha"]},timeout=30)
  r.raise_for_status()
 def get(self,key):
  r=self.s.get(self.base+"/contents/ledger/"+key+".json",params={"ref":"channel-state"},timeout=30)
  if r.status_code==404:return None,None
  r.raise_for_status();v=r.json()
  return json.loads(base64.b64decode(v["content"])),v["sha"]
 def put(self,key,data,previous=None):
  body={"branch":"channel-state","message":"ledger: "+key+" [skip ci]","content":base64.b64encode(json.dumps(data,ensure_ascii=False).encode()).decode()}
  if previous:body["sha"]=previous
  r=self.s.put(self.base+"/contents/ledger/"+key+".json",json=body,timeout=30);r.raise_for_status()
 def update(self,key,fn):
  old,previous=self.get(key);new=fn(old);self.put(key,new,previous);return new
