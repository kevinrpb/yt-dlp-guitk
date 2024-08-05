#!/usr/bin/env bash

if [[ -z $RUNNER_TEMP ]]; then
	echo This script must be run on GitHub Actions.
	exit -1
fi

KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db

# Get certificates
echo $DEVELOPER_ID_INSTALLER | base64 --decode >certificate_installer.p12
echo $DEVELOPER_ID_APPLICATION | base64 --decode >certificate_application.p12

# Configure Keychain
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

# Import certificates
security import "certificate_installer.p12" \
	-P "$P12_PASSWORD" \
	-k "$KEYCHAIN_PATH" \
	-A -t cert -f pkcs12
security import "certificate_application.p12" \
	-P "$P12_PASSWORD" \
	-k "$KEYCHAIN_PATH" \
	-A -t cert -f pkcs12

security list-keychain -d user -s "$KEYCHAIN_PATH"
