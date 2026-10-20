import io,re,zipfile
from pathlib import Path
from .common import sha,read
REQUIRED={"video.mp4","preview.jpg","script.json","sources.json","media.json","quality.json","review.txt"}
def validate(folder,run_id,expected):
 folder=Path(folder)
 if not re.fullmatch("[0-9]+",run_id) or not re.fullmatch("[0-9a-f]{64}",expected):raise ValueError("Invalid review reference")
 if sha(folder/"manifest.json")!=expected:raise ValueError("Manifest changed")
 m=read(folder/"manifest.json")
 if str(m["run_id"])!=run_id or set(m["files"])!=REQUIRED:raise ValueError("Wrong run or bundle")
 for name,digest in m["files"].items():
  if sha(folder/name)!=digest:raise ValueError("Changed review file")
 if not read(folder/"quality.json").get("passed"):raise ValueError("QA failed")
 return m
def download(state,run_id,expected):
 if not re.fullmatch("[0-9]+",run_id):raise ValueError("Invalid run")
 r=state.s.get(state.base+"/actions/runs/"+run_id,timeout=30);r.raise_for_status();run=r.json()
 if run["head_branch"]!="main" or run["path"]!=".github/workflows/produce.yml" or run["conclusion"]!="success" or run["repository"]["full_name"]!=state.repo:raise ValueError("Untrusted production run")
 r=state.s.get(state.base+"/actions/runs/"+run_id+"/artifacts",timeout=30);r.raise_for_status()
 match=[a for a in r.json()["artifacts"] if a["name"]=="review-"+run_id and not a["expired"]]
 if len(match)!=1 or match[0]["size_in_bytes"]>50*1024*1024:raise ValueError("Missing or oversized artifact")
 r=state.s.get(state.base+"/actions/artifacts/"+str(match[0]["id"])+"/zip",timeout=90);r.raise_for_status()
 folder=Path("build/approved");folder.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(io.BytesIO(r.content)) as z:
  if len(z.infolist())!=len(REQUIRED)+1 or set(z.namelist())!=REQUIRED|{"manifest.json"} or sum(i.file_size for i in z.infolist())>50*1024*1024:raise ValueError("Unsafe archive")
  z.extractall(folder)
 m=validate(folder,run_id,expected)
 if m["commit"]!=run["head_sha"]:raise ValueError("Wrong source commit")
 return folder,m
