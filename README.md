# أسرار الحضارات | Civilization Secrets

## Actual deployment status
This repository now contains a cloud smoke-test workflow for a genuine AI-generated moving video with Arabic synthetic narration, Arabic overlay and explicit imaginative-reconstruction disclosure.

The first test is about five seconds, 360x640 source scaled to 1080x1920. It is not a completed 30–60-second episode. Voice is offline eSpeak Arabic and requires human listening review.

Run **AI Motion Production Test** in Actions, then download review-RUN_ID. Watch video.mp4 and review script, sources, media provenance, QA and manifest files. No YouTube upload or public publication occurs. Workflow success never means user approval.

Source lives in src/pipeline.py, with dependencies in requirements.txt and scene provenance in data/ai-scenes.json. This currently assembles supplied generated clips; a daily AI generation provider is not configured. Episode mode refuses the demo packet and requires at least four distinct AI motion clips and a 30–60-second total.

## Outstanding work
- Recover/merge the previously prepared full research/review/publish code from the original workspace.
- Configure a verified AI generation provider with an approved budget. No permanent free daily video-generation service is assumed.
- Add independently researched topics and multiple generated scenes.
- Implement and test durable owner approval/rejection and private-upload/publication workflows.
- Create/authorize the YouTube channel and configure secrets securely.
- Implement analytics and test real YouTube integration.

## Cost controls
Uses standard public GitHub-hosted Ubuntu compute; no paid AI generation API is called by this workflow. Three-day artifact retention; upload size capped at 50 MiB and repository artifacts checked against a conservative 180 MiB threshold before rendering. These controls do not inspect account-wide storage. No billing settings, secrets, repository visibility or authentication protections are changed.

No YouTube integration has been tested. Do not treat this smoke test as a finished autonomous daily channel.
