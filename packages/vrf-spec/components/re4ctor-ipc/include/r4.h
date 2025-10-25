#ifndef R4_H
#define R4_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    const char *socket_path; // default: /run/r4sock/r4.sock
    int timeout_ms;          // default: 30000
} r4_opts;

int  r4_open_ex(const r4_opts *opts);
static inline int r4_open(void){ return r4_open_ex(NULL); }
long long r4_read(void *out, size_t n);
uint32_t r4_u32(void);
void r4_close(void);

#ifdef __cplusplus
}
#endif
#endif
