#ifndef R4_H
#define R4_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#ifndef R4_DEFAULT_SOCK
#define R4_DEFAULT_SOCK "/run/r4sock/r4.sock"
#endif

struct r4_opts {
    const char *sock_path;   // default R4_DEFAULT_SOCK
    int timeout_ms;          // default 30000
};

int       r4_open_ex(const struct r4_opts *opts);
long long r4_read(void *out, size_t n);
uint32_t  r4_u32(void);
void      r4_close(void);

#ifdef __cplusplus
}
#endif
#endif
