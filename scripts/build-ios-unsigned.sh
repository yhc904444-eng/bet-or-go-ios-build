#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Run this script on a cloud Mac with Xcode 26 or newer." >&2
  exit 1
fi
command -v xcodebuild >/dev/null
command -v python3 >/dev/null
xcodebuild -version
xcode_major="$(xcodebuild -version | awk '/^Xcode / { split($2, v, "."); print v[1] }')"
if [[ "$xcode_major" -lt 26 ]]; then
  echo "Capacitor 8 requires Xcode 26 or newer." >&2
  exit 1
fi
test -f ios/App/App/public/index.html
test -f ios/App/App/capacitor.config.json

mkdir -p release .build/ios-unsigned
xcodebuild \
  -project ios/App/App.xcodeproj \
  -scheme App \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -sdk iphoneos \
  -derivedDataPath .build/ios-unsigned/DerivedData \
  -archivePath .build/ios-unsigned/RiverPoker.xcarchive \
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY= \
  ARCHS=arm64 ONLY_ACTIVE_ARCH=NO \
  archive 2>&1 | tee release/ios-build.log

app="$PWD/.build/ios-unsigned/RiverPoker.xcarchive/Products/Applications/App.app"
test -d "$app"
version="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$app/Info.plist")"
ipa="$PWD/release/RiverPoker-$version-iOS-Unsigned.ipa"
payload_dir="$(mktemp -d "${TMPDIR:-/tmp}/river-ios-unsigned.XXXXXX")"
trap 'rm -rf -- "$payload_dir"' EXIT
mkdir -p "$payload_dir/Payload"
ditto "$app" "$payload_dir/Payload/App.app"
(cd "$payload_dir" && zip -qry "$ipa" Payload)

python3 scripts/verify-ios-ipa.py "$ipa" --output release/ios-verification.json
(cd release && shasum -a 256 "$(basename "$ipa")" > "$(basename "$ipa").sha256")
echo "Unsigned device IPA: $ipa"
echo "Install by re-signing with Sideloadly or AltStore and the device owner's Apple ID."
