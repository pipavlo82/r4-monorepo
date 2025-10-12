#ifndef R4_PUBLIC_REF_H
#define R4_PUBLIC_REF_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Reference wrapper: reads bytes from secure IPC server (HMAC-framed). */
int      r4ref_open(const char *sock_path);
long long r4ref_read(void *out, size_t n);
uint32_t r4ref_u32(void);
void     r4ref_close(void);
#ifdef __cplusplus
}
#endif
#endif
