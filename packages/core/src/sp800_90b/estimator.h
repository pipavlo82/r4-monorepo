#pragma once
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif

// Мін-ентропія за SP800-90B (Most Common Value, byte-wise)
double re4_90b_mcv_min_entropy(const unsigned char *buf, size_t n);

#ifdef __cplusplus
}
#endif
