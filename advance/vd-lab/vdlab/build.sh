#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export JAVA_HOME=~/workspace/jdk-17
export PATH="$JAVA_HOME/bin:$PATH"
SDK=~/workspace/android-sdk
BT="$SDK/build-tools/34.0.0"
AJAR="$SDK/platforms/android-34/android.jar"
rm -rf out && mkdir -p out/classes out/dex
javac -encoding UTF-8 -cp "$AJAR" -d out/classes $(find src -name '*.java')
"$BT/d8" --lib "$AJAR" --output out/dex $(find out/classes -name '*.class')
"$BT/aapt2" link -o out/app-unsigned.apk -I "$AJAR" --manifest AndroidManifest.xml \
  --min-sdk-version 26 --target-sdk-version 34 --version-code 1 --version-name 0.1
(cd out/dex && python3 -c "import zipfile; zipfile.ZipFile('../app-unsigned.apk', 'a').write('classes.dex')")
"$BT/zipalign" -f 4 out/app-unsigned.apk out/vdlab.apk
"$BT/apksigner" sign --ks ~/workspace/musedroid-app/debug.keystore --ks-pass pass:android \
  --key-pass pass:android out/vdlab.apk
"$BT/apksigner" verify out/vdlab.apk && ls -la out/vdlab.apk
