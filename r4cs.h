// r4cs.h
#pragma once
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct r4ctx {
    unsigned char key[32];
    unsigned char nonce[12];
    uint32_t      counter;
} r4ctx;

int  r4_init_from_system(r4ctx *ctx);
int  r4_init_from_path(r4ctx *ctx, const char *path);
void r4_free(r4ctx *ctx);
int  r4_generate(r4ctx *ctx, unsigned char *out, size_t out_len);

#ifdef __cplusplus
}
#endif
