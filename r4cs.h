#pragma once
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Ініціалізація DRBG.
// r4_path: шлях до re4_stream (або NULL => береться з $R4_PATH або "re4_stream").
// Повертає 0 при успіху, <0 при помилці.
int r4cs_init(const char *r4_path);

// Згенерувати n байт у out.
// Повертає 0 при успіху, <0 при помилці.
int r4cs_random(void *out, size_t n);

// Форсований reseed (опціонально).
int r4cs_reseed(void);

// Закрити пайп та занулити ключі.
void r4cs_close(void);

#ifdef __cplusplus
}
#endif
