#include <stdio.h>
#include <string.h>

#include "re4/drbg.h" // дає прототипи re4_create/re4_init/re4_random/...
#include "re4/entropy.h"

int main(void) {
  re4_ctx *ctx = re4_create();
  if (!ctx) {
    fprintf(stderr, "create failed\n");
    return 1;
  }

  if (re4_init(ctx, "test/basic") != 0) {
    fprintf(stderr, "init failed\n");
    re4_free(ctx);
    return 2;
  }

  unsigned char buf[32];
  int rc = re4_random(ctx, buf, sizeof(buf)); // не буде implicit після інклуда
  if (rc != 0) {
    fprintf(stderr, "random failed: %d\n", rc);
    re4_free(ctx);
    return 3;
  }

  re4_status_t st = re4_status(ctx);
  printf("ok; bytes=%llu reseeds=%llu healthy=%d H_min/byte=%.3f\n",
         (unsigned long long)st.generated_total, (unsigned long long)st.reseed_count, st.healthy,
         st.est_min_entropy_bits_per_byte);

  re4_free(ctx);
  return 0;
}
