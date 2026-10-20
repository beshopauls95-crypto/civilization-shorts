# YouTube OAuth setup on Android

## Actual state
Use the EXISTING channel **حكاوى التاريخ**, ID `UCC5PfvQjAimGTBr0UJVo06A`. Do not create a replacement channel.
Google Cloud project: `hekawy-history-shorts` (Hekawy History Shorts). Creation was reported without billing or a Free Trial.
Country Egypt was not verified; recheck the account's country rather than marking it complete.
YouTube API Enable was clicked in a separate automation, but its final verification is pending. OAuth application/client and GitHub credential configuration have NOT been completed.

No video has been uploaded or published. The owner explicitly authorized publishing the five-second AI-motion sample publicly; that intent does not prove execution.

## Secure first-time account setup
These steps require access to the owner's Google and GitHub accounts. Never send a password, OTP, client secret, authorization code or refresh token in chat. Never commit a downloaded credentials JSON.

1. In Google Cloud, select project hekawy-history-shorts and verify YouTube Data API v3 shows enabled. Do not start a Free Trial, link billing or enter a card.
2. In Google Auth Platform, configure Branding with app name حكاوى التاريخ and the owner support/developer email. Use External audience for the personal Google account. In Testing, allow only the owner as a test user. The owner must review and accept any required policy declaration themselves.
3. Create an OAuth client of type Web application. Authorized redirect URI: `https://developers.google.com/oauthplayground`. This creates persistent security credentials; require explicit owner consent before creation. Do not expose its secret in screenshots or logs.
4. Open Google's OAuth 2.0 Playground. Its settings must use **your own OAuth credentials**. Enter the project's client ID/secret directly into Google's UI. Use offline access. Do not use the Playground's shared client credentials for the stored project token.
5. Authorize scope `https://www.googleapis.com/auth/youtube.force-ssl` and choose the channel حكاوى التاريخ. Review Google's actual permission screen: this scope is broader than just uploading and can manage videos and related channel content. Grant only if understood and approved.
6. Exchange the returned authorization code inside Playground and retain the refresh token securely. Do not paste it in chat or a workflow input.
7. In GitHub repository Settings → Secrets and variables → Actions, create secret `YOUTUBE_OAUTH_JSON` with a JSON object containing `client_id`, `client_secret`, `refresh_token`. Enter the real values only in the protected secret form.
8. In Actions repository Variables, set `YOUTUBE_CHANNEL_ID` to `UCC5PfvQjAimGTBr0UJVo06A`.
9. Run **Check or configure YouTube channel**, action check. This is read-only and verifies the authorized channel before any upload. Workflow success alone is never owner video approval.

Testing consent applications may issue short-lived refresh tokens; verify current Google requirements before relying on unattended daily operation. A dedicated secure OAuth callback is preferable for a sustained deployment.

## Upload and publish the explicitly approved technical sample
Use **Upload or publish approved technical sample** only after the connection check passes.
- First action: upload_private; exact production run ID + reviewed manifest SHA256 + `TEST_PRIVATE:RUN_ID:SHA256`.
- Then action: make_public; same run and digest + actual returned YouTube ID + `TEST_PUBLIC:RUN_ID:SHA256:YOUTUBE_ID`.
- Publication verifies ledger, selected channel and returned public status; it cannot target another video by changing only the confirmation.
- Upload starts private and records its state before the network request. Never repeat an ambiguous upload; inspect Studio first.
- Samples remain technical demonstrations, not completed 30–60 second episodes. Synthetic-media disclosure is enabled. Normal episode review/publication guards remain separate.

## Remaining work
Live OAuth, secret storage, upload, public publication and analytics have not been tested. Successful unit tests do not prove these external operations.
Current public eligibility/quotas and platform requirements must be checked against current official documentation and the actual account.

Official references:
- https://developers.google.com/identity/protocols/oauth2
- https://developers.google.com/oauthplayground
- https://developers.google.com/youtube/v3/getting-started
- https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
