import os
from .common import now,write
from .state import State
from .publish import youtube,check_channel
def main():
 s=State()
 r=s.s.get(s.base+"/contents/ledger/runs",params={"ref":"channel-state"},timeout=30)
 if r.status_code==404:rows=[]
 else:
  r.raise_for_status();rows=[s.get("runs/"+x["name"].removesuffix(".json"))[0] for x in r.json() if x["name"].endswith(".json")]
 report={"as_of":now(),"videos":rows,"statistics":[],"retention":None,"retention_status":"YouTube Analytics API authorization/implementation outstanding"}
 if os.environ.get("YOUTUBE_OAUTH_JSON"):
  api=youtube();check_channel(api);ids=[x["youtube_id"] for x in rows if x.get("youtube_id")]
  for i in range(0,len(ids),50):report["statistics"]+=api.videos().list(part="statistics",id=",".join(ids[i:i+50])).execute().get("items",[])
 else:report["youtube_status"]="not_authorized"
 write("build/analytics.json",report);s.update("analytics/latest",lambda _:report)
 print("Real available data saved; missing metrics remain null.")
if __name__=="__main__":main()
