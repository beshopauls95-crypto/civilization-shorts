# YouTube channel and OAuth — not yet authorized or tested

Create a new channel named أسرار الحضارات in the intended Google account. The account holder must sign in, complete account verification and accept any terms. No password, OTP, refresh token or client secret belongs in chat.

Create/select a Google Cloud project and enable YouTube Data API v3 without enabling paid products. Configure the consent screen accurately. This implementation requires offline OAuth authorization for https://www.googleapis.com/auth/youtube.force-ssl to upload/read owned videos and change privacy. This is sensitive channel access and requires explicit consent.

Use a real secure redirect endpoint. Android-only setup can use Google's OAuth 2.0 Playground with your own OAuth client and the authorized redirect https://developers.google.com/oauthplayground. Enter client credentials directly in Google's trusted UI and grant consent there. Do not use obsolete out-of-band OAuth or paste credentials into workflow inputs, issues or chat. A dedicated callback service is preferable for a sustained deployment.

Store a JSON object with client_id, client_secret and refresh_token in GitHub Actions secret YOUTUBE_OAUTH_JSON. Store the expected channel UC... identifier in repository variable YOUTUBE_CHANNEL_ID. The code checks the authenticated channel before modifying any video. No secrets have been supplied or stored by the assistant.

External consent apps in Testing may have short-lived refresh tokens; verify current Google publishing/verification requirements. Project-specific upload quotas and public-upload eligibility need checking in the actual console. No API audit or monetization approval is implied.

First real upload must be an exact owner-approved episode, uploaded PRIVATE with explicit upload confirmation. Public publication requires a second explicit confirmation naming the returned YouTube ID. Generated realistic historical scenes use containsSyntheticMedia=true.

Original narration and AI animation do not guarantee monetization eligibility; mass-produced repetitive content may be ineligible. Do not fabricate sources or present generated scenes as historical evidence.

References:
https://developers.google.com/identity/protocols/oauth2
https://developers.google.com/youtube/v3/getting-started
https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
https://support.google.com/youtube/answer/14328491
