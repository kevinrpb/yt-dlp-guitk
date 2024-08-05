#!/usr/bin/env bash

poetry run pyinstaller \
  "yt_dlp_guitk/__main__.py" \
  --name "yt-dlp-guitk" \
  --osx-bundle-identifier "me.kevinrpb.yt-dlp-guitk" \
  --osx-entitlements-file "resources/entitlements.plist" \
  --contents-directory "_yt-dlp-guitk_internal" \
  --codesign-identity "$CODESIGN_IDENTITY" \
  --target-architecture "arm64" \
  --onedir \
  --windowed \
  --noconfirm \
  --clean \
  --log-level=WARN
