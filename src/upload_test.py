"""Owner-requested technical samples may be uploaded privately, never made public."""
import os
import re
from .common import owner_only, now, read
from .state import State
from .artifacts import download
from .publish import youtube, check_channel

def validate_test(manifest, quality, rid, digest, confirmation, previous):
    if not re.fullmatch(r"[0-9]+", rid) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("Invalid exact sample reference")
    if confirmation != "TEST_PRIVATE:" + rid + ":" + digest:
        raise PermissionError("Explicit exact technical-sample approval required")
    if previous is not None:
        raise PermissionError("Existing or ambiguous test upload: inspect Studio before retrying")
    if str(manifest.get("run_id")) != rid or manifest.get("mode") != "smoke" or manifest.get("demo") is not True:
        raise ValueError("This workflow accepts technical samples only")
    if not quality.get("passed") or not 1 <= quality.get("seconds", 0) <= 15:
        raise ValueError("Invalid sample QA or duration")

def main():
    owner_only()
    if not os.environ.get("YOUTUBE_OAUTH_JSON") or not os.environ.get("YOUTUBE_CHANNEL_ID"):
        raise ValueError("YouTube OAuth secret and channel variable are not configured")
    rid = os.environ["TARGET_RUN"]
    digest = os.environ["MANIFEST_SHA"]
    confirmation = os.environ["CONFIRMATION"]
    # Validate identifiers before state/API requests.
    if not re.fullmatch(r"[0-9]+", rid) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("Invalid sample reference")
    if confirmation != "TEST_PRIVATE:" + rid + ":" + digest:
        raise PermissionError("Exact sample approval missing")
    s = State()
    key = "test-uploads/" + rid
    previous, _ = s.get(key)
    folder, manifest = download(s, rid, digest)
    validate_test(manifest, read(folder / "quality.json"), rid, digest, confirmation, previous)
    api = youtube()
    cid = check_channel(api)
    if cid != read("config.json").get("channel_id"):
        raise PermissionError("Channel variable does not match owner-selected project channel")
    sources = read(folder / "sources.json")
    description = "اختبار تقني خاص للمراجعة، وليس حلقة تاريخية مكتملة.\nمشهد تخيلي متحرك مولد بالذكاء الاصطناعي، وتعليق صوتي عربي آلي.\nالمشهد ليس دليلًا أثريًا أو تصويرًا تاريخيًا حقيقيًا.\n\nالمصادر:\n" + "\n".join(x["url"] for x in sources)
    body = {"snippet": {"title": "حكاوى التاريخ | عينة AI متحركة — اختبار خاص",
                        "description": description, "tags": ["حكاوى التاريخ", "اختبار تقني"],
                        "categoryId": "27", "defaultLanguage": "ar", "defaultAudioLanguage": "ar"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
    record = {"run_id": rid, "manifest_sha256": digest, "demo": True, "mode": "smoke",
              "status": "upload_in_progress", "started_at": now(), "public_eligible": False}
    s.put(key, record)
    from googleapiclient.http import MediaFileUpload
    request = api.videos().insert(part="snippet,status", body=body,
        media_body=MediaFileUpload(str(folder / "video.mp4"), mimetype="video/mp4", resumable=True))
    response = None
    while response is None:
        _, response = request.next_chunk(num_retries=3)
    vid = response["id"]
    # Record the ID before readback, to prevent duplicate upload after an uncertain check.
    s.update(key, lambda r: {**r, "youtube_id": vid, "status": "uploaded_needs_verification"})
    items = api.videos().list(part="snippet,status", id=vid).execute().get("items", [])
    if len(items) != 1 or items[0]["snippet"]["channelId"] != cid or items[0]["status"]["privacyStatus"] != "private":
        raise RuntimeError("Private upload could not be verified; inspect Studio")
    s.update(key, lambda r: {**r, "status": "uploaded_private", "verified_at": now()})
    print("Verified PRIVATE technical sample:", vid)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Technical upload stopped safely:", type(exc).__name__,
              "Do not repeat an ambiguous upload; inspect Studio and the test ledger.")
        raise SystemExit(1)
