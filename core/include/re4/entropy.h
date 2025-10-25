#pragma once
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Portable system entropy: returns bytes written (may be < n), 0 on error
size_t re4_sys_entropy(void *buf, size_t n);

// HW intrinsics (may be stubbed out if not available): return 1 on success, 0 otherwise
int re4_hw_rdrand(uint64_t *out);
int re4_hw_rdseed(uint64_t *out);

#ifdef __cplusplus
}
#endif
