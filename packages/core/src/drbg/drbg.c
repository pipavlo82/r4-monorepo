#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#include "re4/drbg.h"
#include "re4/entropy.h"
#include "../sp800_90b/estimator.h"

/* ------------------------- Політика reseed/health ------------------------- */

#define RESEED_BYTES_THRESHOLD (64ull * 1024ull * 1024ull) /* 64 MiB */
#define RESEED_TIME_THRESHOLD_S 180                        /* 3 хв */

struct re4_ctx {
  /* Статус для публічного API */
  re4_status_t st;

  /* Внутрішні лічильники для політики reseed */
  time_t last_reseed;
  uint64_t bytes_since_reseed;
};

/* ------------------------- Внутрішні утиліти ------------------------- */

static int need_reseed(const re4_ctx *ctx) {
  if (!ctx) return 0;
  if (ctx->bytes_since_reseed >= RESEED_BYTES_THRESHOLD) return 1;
  if ((time(NULL) - ctx->last_reseed) >= RESEED_TIME_THRESHOLD_S) return 1;
  return 0;
}

static double estimate_min_entropy_90b(const unsigned char *samp, size_t samp_len) {
  /* MCV оцінка (мін-ентропія у бітах на байт) */
  return re4_90b_mcv_min_entropy(samp, samp_len);
}

/* ------------------------- Публічний API ------------------------- */

re4_ctx *re4_create(void) {
  re4_ctx *ctx = (re4_ctx *)calloc(1, sizeof(*ctx));
  return ctx;
}

void re4_free(re4_ctx *ctx) {
  if (ctx) {
    /* тут могли б затирати чутливий стан, якщо був би ключ/nonce */
    free(ctx);
  }
}

int re4_init(re4_ctx *ctx, const char *domain_tag) {
  (void)domain_tag; /* доменні теги додамо пізніше у мікс сіда */

  if (!ctx) return -1;

  /* 1) первинний seed (64 байти з системи) */
  unsigned char seed[64];
  if (re4_sys_entropy(seed, sizeof(seed)) != (int)sizeof(seed)) {
    memset(seed, 0, sizeof(seed));
    return -2;
  }

  /* 2) одноразова вибірка для SP800-90B (MCV), ~4 KiB достатньо для CI */
  const size_t samp_len = 4096;
  unsigned char *samp = (unsigned char *)malloc(samp_len);
  if (!samp) {
    memset(seed, 0, sizeof(seed));
    return -3;
  }
  int got = re4_sys_entropy(samp, samp_len);
  if (got != (int)samp_len) {
    memset(samp, 0, samp_len);
    free(samp);
    memset(seed, 0, sizeof(seed));
    return -4;
  }

  ctx->st.est_min_entropy_bits_per_byte = estimate_min_entropy_90b(samp, samp_len);

  /* наразі використовуємо системну ентропію як бекенд, тож seed не міксуємо;
     коли інтегруємо core-стрім — тут викличемо мікс/ініт ядра */
  memset(seed, 0, sizeof(seed));
  memset(samp, 0, samp_len);
  free(samp);

  ctx->st.healthy = 1;
  ctx->st.generated_total = 0;
  ctx->st.reseed_count = 1;

  ctx->last_reseed = time(NULL);
  ctx->bytes_since_reseed = 0;

  return 0;
}

int re4_reseed(re4_ctx *ctx) {
  if (!ctx) return -1;

  unsigned char seed[64];
  if (re4_sys_entropy(seed, sizeof(seed)) != (int)sizeof(seed)) {
    memset(seed, 0, sizeof(seed));
    ctx->st.healthy = 0;
    return -2;
  }

  /* Оновлюємо 90B оцінку на новій вибірці */
  const size_t samp_len = 4096;
  unsigned char *samp = (unsigned char *)malloc(samp_len);
  if (!samp) {
    memset(seed, 0, sizeof(seed));
    return -3;
  }
  int got = re4_sys_entropy(samp, samp_len);
  if (got != (int)samp_len) {
    memset(samp, 0, samp_len);
    free(samp);
    memset(seed, 0, sizeof(seed));
    ctx->st.healthy = 0;
    return -4;
  }
  ctx->st.est_min_entropy_bits_per_byte = estimate_min_entropy_90b(samp, samp_len);

  /* Місце для міксу ключа/nonce ядра — додамо при інтеграції core */
  memset(seed, 0, sizeof(seed));
  memset(samp, 0, samp_len);
  free(samp);

  ctx->st.reseed_count++;
  ctx->last_reseed = time(NULL);
  ctx->bytes_since_reseed = 0;
  ctx->st.healthy = 1;

  return 0;
}

int re4_random(re4_ctx *ctx, void *out, size_t n) {
  if (!ctx || !out) return -1;
  if (!ctx->st.healthy) return -2;

  if (need_reseed(ctx)) {
    if (re4_reseed(ctx) != 0) return -3;
  }

  /* Поки що — системна ентропія; замінимо на ядро (stream) згодом */
  uint8_t *p = (uint8_t *)out;
  size_t left = n;
  while (left > 0) {
    size_t chunk = left > 4096 ? 4096 : left;
    int got = re4_sys_entropy(p, chunk);
    if (got != (int)chunk) {
      ctx->st.healthy = 0;
      return -4;
    }
    p += chunk;
    left -= chunk;
    ctx->st.generated_total += chunk;
    ctx->bytes_since_reseed += chunk;
  }
  return 0;
}

re4_status_t re4_status(const re4_ctx *ctx) {
  if (!ctx) {
    re4_status_t z;
    memset(&z, 0, sizeof(z));
    return z;
  }
  return ctx->st;
}
