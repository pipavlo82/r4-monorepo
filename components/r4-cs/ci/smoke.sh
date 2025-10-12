#!/usr/bin/env bash
set -euo pipefail

echo "[i] Environment:"
uname -a || true
gcc --version | head -n1 || true

# 1) Спроба зібрати, якщо є Makefile
if [ -f Makefile ] || [ -f makefile ]; then
  echo "[i] Detected Makefile, building…"
  make -j"$(nproc)"
fi

# 2) Якщо є готовий r4cs_cat — використовуємо його
if [ -x ./r4cs_cat ]; then
  BYTES=$((16<<20))   # 16 MiB
  echo "[i] Running r4cs_cat smoke (16 MiB)…"
  n=$(./r4cs_cat -n "$BYTES" | wc -c)
  echo "[i] Produced bytes: $n"
  if [ "$n" -ne "$BYTES" ]; then
    echo "[!] Unexpected byte count from r4cs_cat" >&2
    exit 1
  fi
  exit 0
fi

# 3) Інакше — пробуємо зібрати demo.c через pkg-config (локальний pc файл у репо або system-wide)
if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists r4cs; then
  echo "[i] Building demo via pkg-config…"
  gcc -O2 -std=c11 demo.c $(pkg-config --cflags --libs r4cs) -o demo
  echo "[i] Running demo (32 bytes hex):"
  ./demo
  exit 0
fi

# 4) Фолбек: спробувати зібрати r4cs_cat із вихідних (найпростіший випадок)
if compgen -G "r4cs_cat.c" > /dev/null; then
  echo "[i] Fallback: building r4cs_cat.c directly…"
  gcc -O2 -std=c11 r4cs_cat.c -lcrypto -lpthread -o r4cs_cat
  BYTES=$((16<<20))
  n=$(./r4cs_cat -n "$BYTES" | wc -c)
  echo "[i] Produced bytes: $n"
  [ "$n" -eq "$BYTES" ] || { echo "[!] Unexpected byte count"; exit 1; }
  exit 0
fi

echo "[!] Could not find a build path (no Makefile, no r4cs_cat, no pkg-config r4cs, no r4cs_cat.c)."
exit 1
