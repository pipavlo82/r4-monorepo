# R4-CS (MVP)

DRBG: HKDF-SHA256 → ChaCha20 з опційним зовнішнім ентропійним стрімером `re4_stream`.

## Швидкий старт (Linux)

```bash
# 0) (опційно) якщо є зовнішній стрімер
export R4_PATH="/home/pavlo/bin/re4_stream"
export R4_SEED="1"

# 1) Приклад: вивести 64 байти у hex
./r4cs_cat -n 64 -hex

# 2) Згенерувати 64 МіБ і швидко прогнати PractRand (stdin32)
RNGT="$HOME/.local/bin/RNG_test_new"
./r4cs_cat -n $((64<<20)) | "$RNGT" stdin32 -tlmin 26 -tlmax 26

