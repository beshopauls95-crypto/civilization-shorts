# Android review and operation

1. Open the repository in Chrome, then Actions. Desktop site may help with workflow inputs.
2. Open AI Motion Production Test. Run workflow on main with smoke for a short sample. Episode mode currently fails safely because no full scene packet exists.
3. After success, download review-RUN_ID under Artifacts. Extract the ZIP in Files. Watch video.mp4, listen to the Arabic narration and review script.json, sources.json, media.json and quality.json.
4. Copy Run ID and Manifest SHA256 from the production summary.
5. Review video lets the owner choose reject/approve for that exact version. A smoke sample can be rejected but cannot be approved for upload. Approval is for complete reviewed episodes only.
6. After YouTube OAuth exists and an actual episode is explicitly approved, Publish approved video -> upload_private with confirmation UPLOAD:RUN_ID:MANIFEST_SHA256.
7. Watch the private upload in Studio. Public publication is a separate run with make_public and confirmation PUBLIC:YOUTUBE_ID.

To revise, commit a new topic/scene packet, produce a new run and review its new hash. Never overwrite a reviewed artifact. Rejection cannot be reversed on the same run. Artifacts expire after three days; save videos you need on your phone.

A produced full topic is consumed in channel-state. New versions need a new reviewed topic ID. If a produced artifact upload fails, investigate the ledger and logs before regeneration. Ambiguous upload_in_progress states require Studio reconciliation rather than blindly repeating an upload.

No permanent daily free video-generation service is configured. The only initial AI clip was generated using the connected service's existing credits.
