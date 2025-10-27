#!/bin/bash
set -euo pipefail

TAG=$1
echo "🏷  Releasing tag: $TAG"

mkdir -p release
zip -r "release/r4sdk-${TAG}.zip" sdk_py_r4/
