#!/usr/bin/env bash
set -euo pipefail
set -o pipefail

BAD="/run/r4sock/bad.sock"
PY="/tmp/bad_server.py"
LOG="/tmp/bad_server.log"
PYTHON="${PYTHON:-/usr/bin/python3}"
CLIENT="./bin/r4cat"
TIMEOUT="${TIMEOUT:-3s}"

# pre-checks
if [ ! -x "$CLIENT" ]; then
  echo "tamper.sh: $CLIENT not found or not executable" >&2
  exit 111
fi

id | grep -q r4users || { echo "tamper.sh: current shell has no r4users group"; exit 112; }
[[ -w /run/r4sock ]] || { echo "tamper.sh: no write perms to /run/r4sock"; exit 113; }

cleanup () {
  pkill -f "$PY" 2>/dev/null || true
  rm -f "$BAD" "$PY" "$LOG"
}
trap cleanup EXIT

cat > "$PY" <<'PY'
import os, socket, struct, sys
sock="/run/r4sock/bad.sock"
try: os.remove(sock)
except: pass
s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(sock); s.listen(1)
print("[bad] READY", flush=True)
c,_=s.accept()
hdr=c.recv(8)
if hdr:
    magic,n=struct.unpack("<II",hdr)
    # FAKE: no nonce/tag; client must reject
    c.sendall(struct.pack("<II",0x52344632,n)+b'\x00'*n)
c.close(); s.close()
PY

nohup "$PYTHON" "$PY" > "$LOG" 2>&1 &
# wait until socket ready
for i in {1..200}; do
  [[ -S "$BAD" ]] && ss -lx | grep -q "$BAD" && grep -q '\[bad\] READY' "$LOG" && break
  sleep 0.02
done

# run client; capture stderr+rc; stdout must be empty (0 bytes)
set +e
OUT="$({ timeout "$TIMEOUT" "$CLIENT" -n 32 -hex -sock "$BAD"; } 2>&1)"
RC=$?
set -e
BYTES="$(timeout "$TIMEOUT" "$CLIENT" -n 32 -hex -sock "$BAD" | wc -c || true)"

# Accept either explicit protocol message or generic failure; require non-zero rc and 0 stdout
if [ "$RC" -ne 0 ] && [ "$BYTES" -eq 0 ]; then
  echo "OK: tamper rejected (rc=$RC), stdout empty"
  exit 0
else
  echo "tamper FAILED: rc=$RC, stdout=$BYTES bytes"
  echo "stderr/stdout:"
  echo "$OUT"
  exit 2
fi
