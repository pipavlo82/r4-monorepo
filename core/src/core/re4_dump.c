#include "re4ctor_core.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
  uint64_t lo = 0x123456789abcdef0ULL, hi = 0xfedcba9876543210ULL;
  if (argc >= 3) {
    lo = strtoull(argv[1], NULL, 0);
    hi = strtoull(argv[2], NULL, 0);
  }
  re4_state s;
  re4_seed(&s, lo, hi);
  uint8_t buf[1 << 16];
  for (;;) {
    re4_bytes(&s, buf, sizeof(buf));
    if (fwrite(buf, 1, sizeof(buf), stdout) != (sizeof(buf))) break;
  }
  return 0;
}
