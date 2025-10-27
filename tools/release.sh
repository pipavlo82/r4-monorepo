#!/bin/bash
set -euo pipefail

TAG="$1"
echo "📦 Building release bundle for tag: $TAG"

mkdir -p release

zip -r "release/r4sdk-${TAG}.zip" \
    sdk_py_r4/r4sdk \
    sdk_py_r4/dist \
    sdk_py_r4/README.md \
    sdk_py_r4/CHANGELOG.md \
    sdk_py_r4/LICENSE \
    sdk_py_r4/setup.py \
    sdk_py_r4/setup.cfg \
    sdk_py_r4/test_r4sdk.py

echo "✅ Bundle created at release/r4sdk-${TAG}.zip"
