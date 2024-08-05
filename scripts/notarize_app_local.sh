#!/usr/bin/env bash

# Needs this to work
# xcrun notarytool store-credentials "$KEYCHAIN_PROFILE" \
#   --apple-id "$APPLE_ID" \
#   --team-id "$TEAM_ID" \
#   --password "$NOTARYTOOL_PASSWORD" \

# Create zip
rm "dist/yt_dlp_guitk.zip"
ditto -c -k --sequesterRsrc --keepParent "dist/yt-dlp-guitk.app" "dist/yt-dlp-guitk.zip"

# Notarize
xcrun notarytool submit "dist/yt-dlp-guitk.zip" \
	--wait \
	--keychain-profile "dev-notarytool-profile"

# Staple
xcrun stapler staple "dist/yt-dlp-guitk.app"
