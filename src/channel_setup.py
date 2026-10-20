"""Check YouTube authorization and apply supported channel metadata, never upload."""
import copy
import json
import os
import re
from pathlib import Path

MUTABLE = {"country", "description", "defaultLanguage", "keywords",
           "trackingAnalyticsAccountId", "unsubscribedTrailer"}

def select_channel(api, channel_id):
    if not re.fullmatch(r"UC[A-Za-z0-9_-]{22}", channel_id or ""):
        raise ValueError("Set the exact YOUTUBE_CHANNEL_ID repository variable")
    items = api.channels().list(part="id,snippet,brandingSettings", mine=True).execute().get("items", [])
    matches = [c for c in items if c.get("id") == channel_id]
    if len(matches) != 1:
        raise PermissionError("Authorized channel does not match configured channel")
    return matches[0]

def branding_body(channel, profile):
    # channels.update replaces mutable properties: retain existing unrelated values.
    old = channel.get("brandingSettings", {}).get("channel", {})
    unknown = set(old) - MUTABLE - {"title", "moderateComments", "showRelatedChannels", "showBrowseView", "featuredChannelsTitle", "featuredChannelsUrls", "profileColor"}
    if unknown:
        raise ValueError("Unrecognized branding fields; inspect before updating")
    settings = {k: copy.deepcopy(v) for k, v in old.items() if k in MUTABLE}
    desc = profile["description_ar"]
    keywords = " ".join('"' + k + '"' if " " in k else k for k in profile["keywords"])
    if not desc or len(desc) > 1000 or len(keywords) > 500:
        raise ValueError("Channel metadata exceeds supported limits")
    if any('"' in k or "\n" in k for k in profile["keywords"]):
        raise ValueError("Invalid keyword")
    settings.update(description=desc, keywords=keywords,
                    defaultLanguage=profile["language"], country=profile["country"])
    return {"id": channel["id"], "brandingSettings": {"channel": settings}}

def run(api, channel_id, profile, action="check"):
    if action not in ("check", "apply_profile"):
        raise ValueError("Unknown setup action")
    channel = select_channel(api, channel_id)
    if action == "check":
        return {"status": "connected", "channel_id": channel_id,
                "title": channel.get("snippet", {}).get("title", ""),
                "videos_uploaded": 0}
    # Protect the pre-existing personal channel from accidental rebranding.
    if channel.get("snippet", {}).get("title") != profile["name"]:
        raise PermissionError("Create/name the dedicated project channel in Studio first")
    body = branding_body(channel, profile)
    api.channels().update(part="brandingSettings", body=body).execute()
    verified = select_channel(api, channel_id).get("brandingSettings", {}).get("channel", {})
    if any(verified.get(k) != v for k, v in body["brandingSettings"]["channel"].items()):
        raise RuntimeError("Metadata update could not be verified")
    return {"status": "profile_applied_verified", "channel_id": channel_id,
            "fields": ["description", "keywords", "defaultLanguage", "country"],
            "videos_uploaded": 0}

def main():
    from .common import owner_only
    owner_only()
    report = {"status": "blocked", "videos_uploaded": 0}
    missing = [n for n in ("YOUTUBE_OAUTH_JSON", "YOUTUBE_CHANNEL_ID") if not os.environ.get(n)]
    if missing:
        report["missing_configuration"] = missing
    else:
        from .publish import youtube
        profile = json.loads(Path("data/channel-profile.json").read_text(encoding="utf-8"))
        report = run(youtube(), os.environ["YOUTUBE_CHANNEL_ID"], profile,
                     os.environ.get("SETUP_ACTION", "check"))
    Path("build").mkdir(exist_ok=True)
    Path("build/channel-setup.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = "## YouTube setup\n\nStatus: " + report["status"] + "\n\nNo video is uploaded or published.\n"
    if missing:
        summary += "\nMissing configuration: " + ", ".join(missing) + "\n"
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(summary)
    if missing:
        raise SystemExit(1)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        # Avoid logging OAuth objects, API error payloads or credential material.
        print("Channel setup stopped:", type(exc).__name__)
        raise SystemExit(1)
