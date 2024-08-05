#!/usr/bin/env bash

if [[ -z $RUNNER_TEMP ]]; then
	echo This script must only be run on GitHub Actions.
	exit -1
fi

KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db

# ----- Create certificate files from secrets base64 -----
echo $DEVELOPER_ID_INSTALLER_CER | base64 --decode >certificate_installer.cer
echo $DEVELOPER_ID_INSTALLER_KEY | base64 --decode >certificate_installer.key
echo $DEVELOPER_ID_APPLICATION_CER | base64 --decode >certificate_application.cer
echo $DEVELOPER_ID_APPLICATION_KEY | base64 --decode >certificate_application.key

# ----- Create p12 file -----
openssl pkcs12 -export -name zup \
	-in certificate_installer.cer \
	-inkey certificate_installer.key \
	-passin pass:$KEY_PASSWORD \
	-out certificate_installer.p12 \
	-passout pass:$P12_PASSWORD
openssl pkcs12 -export -name zup \
	-in certificate_application.cer \
	-inkey certificate_application.key \
	-passin pass:$KEY_PASSWORD \
	-out certificate_application.p12 \
	-passout pass:$P12_PASSWORD

# ----- Configure Keychain -----
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

# ----- Import certificates on Keychain -----
security import certificate_installer.p12 \
	-P "$P12_PASSWORD" \
	-A -t cert -f pkcs12 -k $KEYCHAIN_PATH
security import certificate_application.p12 \
	-P "$P12_PASSWORD" \
	-A -t cert -f pkcs12 -k $KEYCHAIN_PATH
security list-keychain -d user -s $KEYCHAIN_PATH
