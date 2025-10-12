#!/usr/bin/env bash
set -euo pipefail
set -o pipefail

CLIENT=./bin/r4cat
[ -x "$CLIENT" ] || { echo "tamper: no client ($CLIENT)"; exit 0; }

ROOT="$(mktemp -d)"
KEY="$ROOT/secret.key"
SOCK="$ROOT/bad.sock"
PY="$ROOT/bad_server.py"
LOG="$ROOT/bad_server.log"
PYTHON=${PYTHON:-/usr/bin/python3}
TIMEOUT=${TIMEOUT:-3s}

cleanup() {
  pkill -f "$PY" 2>/dev/null || true
  rm -rf "$ROOT"
}
trap cleanup EXIT

head -c 32 /dev/urandom > "$KEY"
export R4_KEY_PATH="$KEY"

cat > "$PY" <<'PY'
import os, socket, struct, sys
sock = os.environ['SOCK']
try:
    os.unlink(sock)
except FileNotFoundError:
    pass
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(sock); s.listen(1)
print("[bad] READY", flush=True)
c,_ = s.accept()
hdr = c.recv(8)
if hdr:
    magic,n = struct.unpack("<II", hdr)
    # ПІДРОБКА: без nonce/tag
    c.sendall(struct.pack("<II",0x52344632,n) + b'\x00'*n)
c.close(); s.close()
PY

export SOCK
nohup "$PYTHON" "$PY" > "$LOG" 2>&1 &

for i in {1..200}; do
  [[ -S "$SOCK" ]] && break
  sleep 0.02
done

set +e
OUT="$({ timeout "$TIMEOUT" "$CLIENT" -n 32 -hex -sock "$SOCK"; } 2>&1)"
RC=$?
set -e

BYTES=$( { timeout "$TIMEOUT" "$CLIENT" -n 32 -hex -sock "$SOCK" | wc -c; } 2>/dev/null || true )

if [[ $RC -ne 2 ]]; then
  echo "tamper: unexpected rc=$RC"
  echo "$OUT"
  exit 112
fi
grep -q 'r4_read error (HMAC/protocol)' <<<"$OUT" || { echo "tamper: expected protocol error"; echo "$OUT"; exit 112; }
[[ "$BYTES" -eq 0 ]] || { echo "tamper: wrote bytes ($BYTES), expected 0"; exit 112; }

echo "OK: tamper rejected (rc=2), stdout empty"
