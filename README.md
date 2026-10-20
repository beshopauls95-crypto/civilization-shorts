# Civilization Secrets | أسرار الحضارات

A cloud pipeline for Arabic Shorts built from real AI-generated moving scenes, with exact-version owner review and separate private-upload/publication approvals.

## Verified result
The cloud renderer produced a playable MP4 with actual AI motion, offline Arabic narration, shaped Arabic captions and an imaginative-reconstruction disclosure.
Latest production: https://github.com/beshopauls95-crypto/civilization-shorts/actions/runs/39487995741
Safety CI: https://github.com/beshopauls95-crypto/civilization-shorts/actions/runs/39487995687 — 14 tests passed.

The current sample is approximately five seconds. Its generated source is 360x640, scaled to a 1080x1920 H.264/AAC export. This does not mean native 1080p generation. The sample is ineligible for YouTube upload. Listen to the synthetic Arabic voice and check visual quality before accepting a future episode.

## Android operation
Open Actions, select the successful production run and download review-RUN_ID under Artifacts. Extract the ZIP in Files, watch video.mp4 and inspect script.json, sources.json, media.json and quality.json. Artifacts are retained for three days.

Review video accepts an exact production run ID and manifest SHA256, then records the owner's approve/reject decision. Rejected versions cannot be reapproved. Smoke demos cannot be approved for upload.

Publish approved video requires an approved full episode, channel OAuth, and UPLOAD:RUN_ID:MANIFEST_SHA256 to upload PRIVATE. Making public requires a second explicit confirmation PUBLIC:YOUTUBE_ID. Production never calls YouTube. An ambiguous upload remains upload_in_progress until reconciled in Studio.

## Current limits and remaining work
- One AI motion demo clip and one curated Rosetta Stone historical topic are available.
- Episode mode needs distinct generated clips, matching sourced narration and 30–60 seconds total.
- AI clip generation is not automated. The connected Free generation account has no credits remaining. No sustainable free daily provider is assumed.
- Research/script generation use a finite grounded editorial queue. Live discovery and a generative script model are not configured.
- Daily production readiness reports the blocker; it does not generate daily videos.
- YouTube channel setup, OAuth and actual upload/privacy tests are outstanding.
- Analytics supports available views/likes/comments after authorization. Retention remains null.

Source modules, workflows and Android/OAuth guides are included. See docs/acceptance.md for actual execution evidence and docs/architecture.md for trust boundaries.

## Cost and privacy
The repository remains public. Treat draft artifacts and ledger records as public repository material. Standard public Ubuntu runners are used. Artifacts have a repository storage guard and three-day retention, but account-wide storage is not inspected. No paid AI generation, trial, subscription, billing change or new browser run was initiated by these workflows. Keep provider spending disabled until explicitly authorized. Secrets belong only in GitHub Actions Secrets; do not paste credentials into chat.
