#include "re4ctor_core.h"

static uint64_t splitmix64(uint64_t *x) {
  uint64_t z = (*x += 0x9e3779b97f4a7c15ULL);
  z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
  z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
  return z ^ (z >> 31);
}
static inline uint64_t rotl(const uint64_t x, int k) {
  return (x << k) | (x >> (64 - k));
}

static uint64_t next64(re4_state *st) {
  const uint64_t result = rotl(st->s[1] * 5, 7) * 9;
  const uint64_t t = st->s[1] << 17;
  st->s[2] ^= st->s[0];
  st->s[3] ^= st->s[1];
  st->s[1] ^= st->s[2];
  st->s[0] ^= st->s[3];
  st->s[2] ^= t;
  st->s[3] = rotl(st->s[3], 45);
  return result;
}

void re4_seed(re4_state *st, uint64_t lo, uint64_t hi) {
  uint64_t x = lo ^ 0x7f4a7c159e3779b9ULL ^ (hi << 1);
  st->s[0] = splitmix64(&x);
  st->s[1] = splitmix64(&x);
  st->s[2] = splitmix64(&x);
  st->s[3] = splitmix64(&x);
}

uint64_t re4_u64(re4_state *st) {
  return next64(st);
}

uint32_t re4_u32(re4_state *st) {
  static uint64_t buf;
  static int have = 0;
  if (!have) {
    buf = next64(st);
    have = 1;
    return (uint32_t)(buf & 0xffffffffu);
  }
  have = 0;
  return (uint32_t)(buf >> 32);
}

void re4_bytes(re4_state *st, void *out, size_t n) {
  uint8_t *p = (uint8_t *)out;
  while (n) {
    uint64_t x = next64(st);
    size_t k = n < 8 ? n : 8;
    for (size_t i = 0; i < k; i++)
      p[i] = (uint8_t)(x >> (i * 8));
    p += k;
    n -= k;
  }
}
