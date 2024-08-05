#!/usr/bin/env bash

KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db

# Store credentials
xcrun notarytool store-credentials "$KEYCHAIN_PROFILE" \
  --apple-id "$APPLE_ID" \
  --team-id "$TEAM_ID" \
  --password "$NOTARYTOOL_PASSWORD" \
  --keychain "$KEYCHAIN_PATH"

# Create zip for notarization
rm -f "dist/yt-dlp-guitk.zip"
ditto -c -k --sequesterRsrc --keepParent "dist/yt-dlp-guitk.app" "dist/yt-dlp-guitk.zip"

# Notarize
xcrun notarytool submit "dist/yt-dlp-guitk.zip" \
  --wait \
  --keychain "$KEYCHAIN_PATH" \
  --keychain-profile "$KEYCHAIN_PROFILE"

# Staple
xcrun stapler staple "dist/yt-dlp-guitk.app"

# Rezip stapled file
rm -f "dist/yt-dlp-guitk.zip"
ditto -c -k --sequesterRsrc --keepParent "dist/yt-dlp-guitk.app" "dist/yt-dlp-guitk.zip"
