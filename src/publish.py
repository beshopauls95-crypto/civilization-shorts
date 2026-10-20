import os,json,re
from .common import owner_only,now,read
from .state import State
from .artifacts import download
def authorize(record,action,rid,digest,confirmation):
 if not record or record.get("run_id")!=rid or record.get("manifest_sha256")!=digest:raise ValueError("Wrong approved version")
 if record.get("demo",True) or record.get("mode")!="episode":raise PermissionError("Demo cannot be published")
 if action=="upload_private":
  if record["status"]!="approved" or confirmation!="UPLOAD:"+rid+":"+digest:raise PermissionError("Exact private upload approval required")
 elif action=="make_public":
  if record["status"]!="uploaded_private" or not record.get("youtube_id") or confirmation!="PUBLIC:"+record["youtube_id"]:raise PermissionError("Separate public approval required")
 else:raise ValueError("Unknown action")
def youtube():
 from google.oauth2.credentials import Credentials
 from googleapiclient.discovery import build
 d=json.loads(os.environ["YOUTUBE_OAUTH_JSON"])
 c=Credentials(token=None,refresh_token=d["refresh_token"],client_id=d["client_id"],client_secret=d["client_secret"],token_uri="https://oauth2.googleapis.com/token",scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
 return build("youtube","v3",credentials=c,cache_discovery=False)
def check_channel(api):
 cid=os.environ.get("YOUTUBE_CHANNEL_ID")
 if not cid:raise ValueError("Missing channel ID")
 channels=api.channels().list(part="id",mine=True).execute()
 if cid not in {x["id"] for x in channels.get("items",[])}:raise PermissionError("Wrong OAuth channel")
 return cid
def main():
 owner_only();s=State();rid=os.environ["TARGET_RUN"];digest=os.environ["MANIFEST_SHA"];action=os.environ["PUBLISH_ACTION"]
 record,previous=s.get("runs/"+rid);authorize(record,action,rid,digest,os.environ["CONFIRMATION"])
 if action=="upload_private":
  folder,m=download(s,rid,digest)
  if m.get("demo") or m["mode"]!="episode" or not 30<=read(folder/"quality.json")["seconds"]<=60:raise ValueError("Not a complete episode")
  script=read(folder/"script.json")
  if not script.get("description") or not script.get("tags"):raise ValueError("Missing title/description/tags for actual episode")
  if len(script["title"])>100 or len(script["description"])>5000:raise ValueError("Metadata exceeds YouTube limit")
 api=youtube();cid=check_channel(api)
 if action=="upload_private":
  from googleapiclient.http import MediaFileUpload
  s.put("runs/"+rid,{**record,"status":"upload_in_progress","started_at":now()},previous)
  request=api.videos().insert(part="snippet,status",body={"snippet":{"title":script["title"],"description":script["description"],"tags":script["tags"],"categoryId":"27","defaultLanguage":"ar","defaultAudioLanguage":"ar"},"status":{"privacyStatus":"private","selfDeclaredMadeForKids":False,"containsSyntheticMedia":True}},media_body=MediaFileUpload(str(folder/"video.mp4"),mimetype="video/mp4",resumable=True,chunksize=8*1024*1024))
  response=None
  while response is None:_,response=request.next_chunk(num_retries=3)
  s.update("runs/"+rid,lambda r:{**r,"status":"uploaded_private","youtube_id":response["id"],"uploaded_at":now()})
  print("Uploaded PRIVATE:",response["id"])
 else:
  vid=record["youtube_id"];res=api.videos().list(part="snippet,status",id=vid).execute()
  if len(res.get("items",[]))!=1 or res["items"][0]["snippet"]["channelId"]!=cid:raise PermissionError("Video ownership mismatch")
  api.videos().update(part="status",body={"id":vid,"status":{"privacyStatus":"public","selfDeclaredMadeForKids":res["items"][0]["status"].get("selfDeclaredMadeForKids",False),"containsSyntheticMedia":True}}).execute(num_retries=3)
  s.put("runs/"+rid,{**record,"status":"public","published_at":now()},previous)
  print("Public:",vid)
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("Publishing stopped safely:",type(e).__name__,". Reconcile upload_in_progress in YouTube Studio before retry; never repeat an ambiguous upload.")
  raise SystemExit(1)
