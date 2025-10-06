## Дисклеймер безпеки
Це MVP. Попри проходження тестів випадковості, **це не гарантія криптостійкості**. Перед продакшеном потрібен незалежний аудит.

## Тести
- PractRand: до 2–8 GiB (core set) — без аномалій
- NIST STS: 80 послідовностей × 1e6 біт — ок
- Dieharder: full (-a), поодинокі WEAK перетестовано — ок

## Збірка з C
pkg-config --cflags --libs r4cs
gcc -O2 -std=c11 demo.c $(pkg-config --cflags --libs r4cs) -o demo
./demo

## Зовнішня ентропія (опційно)
export R4_PATH="/home/pavlo/bin/re4_stream"
export R4_SEED="1"
./r4cs_cat -n 64 -hex
