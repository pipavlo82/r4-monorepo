#ifndef RE4CTOR_CORE_H
#define RE4CTOR_CORE_H
#include <stddef.h>
#include <stdint.h>

typedef struct {
  uint64_t s[4];
} re4_state;

void re4_seed(re4_state *st, uint64_t seed_lo, uint64_t seed_hi);
uint32_t re4_u32(re4_state *st);
uint64_t re4_u64(re4_state *st);
void re4_bytes(re4_state *st, void *out, size_t n);

#endif
