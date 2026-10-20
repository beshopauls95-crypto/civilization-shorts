# Architecture and actual limits

Production consumes real AI-generated MP4 clips. It never substitutes still-image zoom/pan. Each clip is downloaded from an allowlisted OpenArt CDN URL with a 50 MiB limit. Voice is offline Arabic eSpeak; FFmpeg creates H.264/AAC 1080×1920 output. Caption timing is per scene. Input native dimensions are recorded, so upscaling is not presented as native 1080p generation.

The current default packet is one five-second smoke-test clip. Episode mode requires distinct clips, 30–60 seconds overall, a curated unused historical topic, six matching narration scenes for the initial topic, and safe voice speed. It records topic usage on channel-state. The initial topic queue is finite (one Rosetta Stone packet). Research and script generation use sourced editorial inputs; live discovery, independent automated claim verification and a generative writer are not configured.

A successful production uploads a three-day review artifact with video, preview, script, sources, media provenance, QA and a SHA256 manifest. These are public-repository drafts, not confidential storage. Review validates the successful main production run, source commit, exact artifact name, ZIP member allowlist, size and all file hashes. Only the configured owner on main can decide approve/reject. Rejection is final for that run/version. Smoke samples cannot be approved for upload.

Manual state transitions:
pending -> approved OR rejected
approved -> upload_in_progress -> uploaded_private -> public

Private upload requires UPLOAD:RUN_ID:MANIFEST_SHA256 after an approved episode. Public publication requires a separate PUBLIC:YOUTUBE_ID confirmation. The OAuth channel is checked against a configured channel ID. Uploads disclose realistic generated media. Pending, rejected, changed, demo and already-uploaded versions cannot upload. An ambiguous interrupted upload remains upload_in_progress; reconcile with Studio before recovery to prevent duplicates.

State is durable JSON under ledger/ on channel-state with optimistic SHA checks. Review/publication/analytics share a concurrency group. Administrators remain trusted and can edit source or ledger. Workflow inputs are passed through environment variables. YouTube credentials appear only as GitHub Secrets references; production receives no YouTube credentials.

Analytics can read views, likes and comments after OAuth. Retention is null because YouTube Analytics API integration is outstanding. Errors are visible in Actions logs; no statistics are fabricated.

The daily readiness workflow runs at 07:17 UTC and reports that generation is disabled. It does not generate daily videos. A sustainable authorized provider adapter and new reviewed source packets are required before daily autonomous generation can be implemented.
