#pragma once
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  int healthy;                          // 1 = ok, 0 = fail/paused
  uint64_t generated_total;             // bytes produced since init
  uint64_t reseed_count;                // how many reseeds
  double est_min_entropy_bits_per_byte; // SP800-90B (MCV) on last seed
} re4_status_t;

typedef struct re4_ctx re4_ctx;

/* Lifecycle */
re4_ctx *re4_create(void);
void re4_free(re4_ctx *ctx);

/* Init / reseed */
int re4_init(re4_ctx *ctx, const char *domain_tag);
int re4_reseed(re4_ctx *ctx);

/* Generate random bytes */
int re4_random(re4_ctx *ctx, void *out, size_t n);

/* Status (const-correct) */
re4_status_t re4_status(const re4_ctx *ctx);

#ifdef __cplusplus
}
#endif
