import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import requests
OWNER="beshopauls95-crypto"
def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding="utf-8"))
def write(path,data):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
def owner_only():
 if os.environ.get("GITHUB_ACTOR")!=OWNER or os.environ.get("GITHUB_REF")!="refs/heads/main":raise PermissionError("Only owner on main may review/publish")
