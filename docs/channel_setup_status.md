# Channel setup status

The owner approved channel creation and the displayed YouTube terms. The creation form was prepared but submission has not been verified; browser control is currently unavailable. Never label the channel created based only on consent or this file.

Prepared profile: data/channel-profile.json.

The manual **Check or configure YouTube channel** workflow defaults to a read-only connection check. It reports missing YOUTUBE_OAUTH_JSON / YOUTUBE_CHANNEL_ID, verifies the authorized channel ID, and never uploads videos. apply_profile updates description, keywords, language and country only, after checking the existing channel title matches the dedicated project. It reads existing settings first and verifies the result after updating.

Channel creation, name/handle, avatar, banner, Studio upload defaults, audience/comment controls, and homepage still need live YouTube Studio setup. This workflow does not claim to apply those settings. Existing upload code enforces private status independently of Studio defaults.

Google Cloud project/API/OAuth consent and secure GitHub Secret entry remain pending. Do not place credentials in repository files, inputs, artifacts or chat. No paid browser task or AI generation is authorized by this implementation.

Reference: https://developers.google.com/youtube/data/reference/rest/v3/channels/update
