from .pipeline import probe,command
def check(path):
 data=probe(path);v=next(x for x in data["streams"] if x["codec_type"]=="video");a=next(x for x in data["streams"] if x["codec_type"]=="audio")
 if (v["width"],v["height"])!=(1080,1920) or v["codec_name"]!="h264" or a["codec_name"]!="aac":raise ValueError("Wrong video/audio format")
 command(["ffmpeg","-v","error","-i",path,"-f","null","-"])
 return {"passed":True,"seconds":float(data["format"]["duration"]),"human_motion_and_voice_review_required":True}
