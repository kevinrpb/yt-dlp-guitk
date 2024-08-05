#!/usr/bin/env bash

name="yt-dlp-guitk"

# macOS stuff
bundle_id="me.kevinrpb.$name"
sign_id="2FB1729D9A60F092BD8760694FBF5B5EEBCE5721"
entitlements_file="resources/entitlements.plist"

poetry run pyinstaller \
  yt_dlp_guitk/__main__.py \
  --name "$name" \
  --osx-bundle-identifier "$bundle_id" \
  --osx-entitlements-file "$entitlements_file" \
  --contents-directory "_$name_internal" \
  --codesign-identity "$sign_id" \
  --target-architecture "arm64" \
  --onedir \
  --windowed \
  --noconfirm \
  --clean \
  --log-level=WARN

# Create zip
rm dist/yt_dlp_guitk.zip
ditto -c -k --sequesterRsrc --keepParent dist/yt-dlp-guitk.(app|exe) dist/yt-dlp-guitk.zip
