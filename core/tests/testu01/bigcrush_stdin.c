#include "../../src/core/re4ctor_core.h"
#include <stdint.h>
#include <stdio.h>
int main() {
  re4_state s;
  re4_seed(&s, 0x1ULL, 0x2ULL);
  uint8_t buf[1 << 16];
  for (;;) {
    re4_bytes(&s, buf, sizeof(buf));
    if (fwrite(buf, 1, sizeof(buf), stdout) != (sizeof(buf))) break;
  }
  return 0;
}
