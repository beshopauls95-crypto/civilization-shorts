"""Render supplied AI motion clips; does not silently substitute still images."""
import ctypes as C
import hashlib
import json
import os
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests
import espeakng_loader

OUT = Path("build")
OUT.mkdir(exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def dump(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def command(args):
    subprocess.run([str(a) for a in args], check=True)

def probe(path):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]))

def voice(text, path):
    lib=C.CDLL(espeakng_loader.get_library_path())
    lib.espeak_Initialize.argtypes=[C.c_int,C.c_int,C.c_char_p,C.c_int]
    rate=lib.espeak_Initialize(2,0,str(Path(espeakng_loader.get_data_path()).parent).encode(),0)
    if rate<=0: raise RuntimeError("Cannot initialize Arabic voice")
    chunks=[]
    CB=C.CFUNCTYPE(C.c_int,C.POINTER(C.c_short),C.c_int,C.c_void_p)
    @CB
    def callback(samples, count, events):
        if samples and count>0: chunks.append(C.string_at(samples,count*2))
        return 0
    lib.espeak_SetSynthCallback.argtypes=[CB]
    lib.espeak_SetSynthCallback(callback)
    lib.espeak_SetVoiceByName.argtypes=[C.c_char_p]
    if lib.espeak_SetVoiceByName(b"ar") != 0: raise RuntimeError("Arabic voice unavailable")
    lib.espeak_SetParameter(1,155,0)
    lib.espeak_Synth.argtypes=[C.c_void_p,C.c_size_t,C.c_uint,C.c_int,C.c_uint,C.c_uint,C.POINTER(C.c_uint),C.c_void_p]
    data=text.encode()+b"\0"
    buf=C.create_string_buffer(data)
    if lib.espeak_Synth(buf,len(data),0,1,0,1,None,None)!=0: raise RuntimeError("Voice synthesis failed")
    lib.espeak_Synchronize()
    lib.espeak_Terminate()
    if not chunks: raise RuntimeError("Empty audio")
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(b"".join(chunks))

def overlay(text, path):
    im=Image.new("RGBA",(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype(FONT,46)
    small=ImageFont.truetype(FONT,34)
    draw.rounded_rectangle((40,80,1040,215),20,fill=(10,15,23,225))
    draw.text((540,120),"حكاوى التاريخ",font=small,anchor="mm",direction="rtl",fill="#edca83")
    draw.text((540,175),"مشهد تخيلي مولد بالذكاء الاصطناعي",font=small,anchor="mm",direction="rtl",fill="white")
    lines=[]; line=""
    for word in text.split():
        candidate=(line+" "+word).strip()
        if draw.textlength(candidate,font=font,direction="rtl")>850 and line:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    if len(lines)>5:raise ValueError("Caption too long")
    y=1470-len(lines)*28
    draw.rounded_rectangle((45,y-35,1035,y+len(lines)*70+25),22,fill=(10,15,23,225))
    for line in lines:
        draw.text((540,y),line,font=font,anchor="mt",direction="rtl",fill="white")
        y+=70
    im.save(path)

def fetch_clip(url,path):
    if not url.startswith("https://cdn.openart.ai/"):raise ValueError("Only explicit OpenArt result URLs currently allowed")
    with requests.get(url,stream=True,timeout=(15,90)) as r:
        r.raise_for_status()
        size=0
        with path.open("wb") as f:
            for chunk in r.iter_content(65536):
                size+=len(chunk)
                if size>50*1024*1024:raise ValueError("Clip exceeds limit")
                f.write(chunk)

def render(scenes,mode):
    total=0
    for i,s in enumerate(scenes):
        clip=OUT/f"input-{i}.mp4"; wav=OUT/f"voice-{i}.wav"; png=OUT/f"caption-{i}.png"
        fetch_clip(s["url"],clip)
        info=probe(clip)
        seconds=float(info["format"]["duration"])
        native=next(x for x in info["streams"] if x["codec_type"]=="video")
        s["native_width"]=native["width"];s["native_height"]=native["height"];s["duration_seconds"]=seconds
        if not 1<=seconds<=20:raise ValueError("Unexpected clip duration")
        voice(s["narration"],wav)
        spoken=float(probe(wav)["format"]["duration"])
        speed=max(1,spoken/seconds)
        if speed>1.3:raise ValueError("Narration is too long for the moving scene")
        overlay(s["narration"],png)
        filt="[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];[bg][1:v]overlay=0:0,format=yuv420p[v];[2:a]atempo="+str(speed)+",apad[a]"
        command(["ffmpeg","-y","-v","error","-i",clip,"-i",png,"-i",wav,"-filter_complex_threads","1","-filter_complex",filt,"-map","[v]","-map","[a]","-t",str(seconds),"-r","24","-c:v","libx264","-preset","veryfast","-crf","25","-maxrate","3M","-bufsize","6M","-c:a","aac","-b:a","96k","-movflags","+faststart",OUT/f"scene-{i}.mp4"])
        total+=seconds
    if mode=="episode" and not 30<=total<=60:raise ValueError("Full episodes must be 30 to 60 seconds")
    (OUT/"concat.txt").write_text("\n".join("file 'scene-"+str(i)+".mp4'" for i in range(len(scenes))))
    command(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",OUT/"concat.txt","-c","copy","-movflags","+faststart",OUT/"video.mp4"])
    info=probe(OUT/"video.mp4")
    v=next(x for x in info["streams"] if x["codec_type"]=="video")
    a=next(x for x in info["streams"] if x["codec_type"]=="audio")
    assert (v["width"],v["height"])==(1080,1920) and v["codec_name"]=="h264" and a["codec_name"]=="aac"
    command(["ffmpeg","-v","error","-i",OUT/"video.mp4","-f","null","-"])
    vol=subprocess.run(["ffmpeg","-hide_banner","-i",str(OUT/"video.mp4"),"-af","volumedetect","-vn","-f","null","-"],capture_output=True,text=True,check=True)
    import re
    mean=float(re.search(r"mean_volume: ([\-\w.]+) dB",vol.stderr).group(1))
    assert mean>-45,"Silent narration"
    command(["ffmpeg","-y","-v","error","-ss","1","-i",OUT/"video.mp4","-frames:v","1",OUT/"preview.jpg"])
    dump("quality.json",{"passed":True,"seconds":float(info["format"]["duration"]),"audio_mean_db":mean,"human_motion_and_voice_review_required":True})
    return total

def main():
    mode=os.environ.get("PRODUCTION_MODE","smoke") or "smoke"
    packet=json.loads(Path("data/ai-scenes.json").read_text())
    scenes=packet["scenes"]
    episode_script=None
    state=None
    if mode=="episode":
        if packet.get("demo",True):raise RuntimeError("Only one demo scene exists. A full episode needs new sourced AI clips; generation provider not configured.")
        if len(scenes)<4 or len({s["url"] for s in scenes})!=len(scenes):raise RuntimeError("Need at least four distinct AI motion scenes")
        from .state import State
        from .research import select
        from .generate_script import generate
        state=State()
        index,_=state.get("production/index")
        topic=select((index or {}).get("used",{}),packet.get("topic_id",""))
        episode_script=generate(topic)
        if len(scenes)!=len(episode_script["scenes"]):raise ValueError("Each narration scene needs its own generated clip")
        scenes=[{**s,"narration":n} for s,n in zip(scenes,episode_script["scenes"])]
        packet["title"]=episode_script["title"]
        packet["sources"]=topic["sources"]
    else: scenes=scenes[:1]
    total=render(scenes,mode)
    dump("script.json",{**(episode_script or {}),"title":packet["title"],"narration":[s["narration"] for s in scenes],"mode":mode})
    dump("sources.json",packet["sources"])
    dump("media.json",{"kind":"ai_generated_motion","scenes":scenes,"disclosure":"Imaginative reconstruction; not historical footage","resolution_note":"Inspect each scene native_width/native_height; 1080x1920 export can be upscaled"})
    (OUT/"review.txt").write_text(("اختبار تقني قصير فقط.\n" if mode=="smoke" else "حلقة كاملة تنتظر المراجعة.\n")+"شاهد الحركة واستمع للنطق العربي وراجع المصادر. لا توجد موافقة رفع أو نشر.\nلا يوجد اتصال بيوتيوب في هذا التشغيل.\n",encoding="utf-8")
    names=["video.mp4","preview.jpg","script.json","sources.json","media.json","quality.json","review.txt"]
    manifest={"run_id":os.environ.get("GITHUB_RUN_ID"),"commit":os.environ.get("GITHUB_SHA"),"mode":mode,"demo":mode=="smoke","production_quality_eligible":mode=="episode","approval":"pending","synthetic_media":True,"files":{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
    if state:
        def remember(old):
            old=old or {"used":{}}
            if topic["id"] in old["used"]:raise ValueError("Topic already produced")
            old["used"][topic["id"]]=os.environ["GITHUB_RUN_ID"]
            return old
        state.update("production/index",remember)
    dump("manifest.json",manifest)
    sha=hashlib.sha256((OUT/"manifest.json").read_bytes()).hexdigest()
    print("Review manifest SHA256:",sha)
    print("Review run ID:",os.environ.get("GITHUB_RUN_ID"))
    bundle=OUT/"bundle";bundle.mkdir(exist_ok=True)
    import shutil
    for n in names+["manifest.json"]:shutil.copy2(OUT/n,bundle/n)
    summary="## AI motion test ready for human review\n\nMode: "+mode+"\n\nDuration: "+str(total)+" seconds\n\nManifest SHA256: "+sha+"\n\nHuman review is required. Smoke mode is only a short technical sample. Download the review artifact and watch video.mp4. No YouTube API is called.\n"
    with open(os.environ["GITHUB_STEP_SUMMARY"],"a") as f:f.write(summary)

if __name__=="__main__":main()
