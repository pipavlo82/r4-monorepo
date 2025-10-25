#include <stdint.h>
#include <stddef.h>
#include <limits.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#if defined(__x86_64__) || defined(_M_X64)
#include <immintrin.h>
#endif

// --- HW intrinsics (best-effort) ---
int re4_hw_rdrand(uint64_t *out) {
#if defined(__x86_64__) || defined(_M_X64)
  unsigned long long tmp = 0ULL;
  int ok = _rdrand64_step(&tmp);
  if (ok) {
    *out = (uint64_t)tmp;
    return 1;
  }
  return 0;
#else
  (void)out;
  return 0;
#endif
}

int re4_hw_rdseed(uint64_t *out) {
#if defined(__x86_64__) || defined(_M_X64)
  unsigned long long tmp = 0ULL;
  int ok = _rdseed64_step(&tmp);
  if (ok) {
    *out = (uint64_t)tmp;
    return 1;
  }
  return 0;
#else
  (void)out;
  return 0;
#endif
}

// --- Portable system entropy (/dev/urandom) ---
// returns number of bytes written, or -1 on error
static size_t re4_sys_entropy_impl(void *buf, size_t n) {
  if (!buf || n == 0) return 0;

  int flags = O_RDONLY;
#ifdef O_CLOEXEC
  flags |= O_CLOEXEC;
#endif
  int fd = open("/dev/urandom", flags);
  if (fd < 0) return 0;

  uint8_t *p = (uint8_t *)buf;
  size_t left = n;

  while (left > 0) {
    ssize_t r = read(fd, p, left);
    if (r > 0) {
      p += (size_t)r;
      left -= (size_t)r;
    } else if (r == 0) {
      break; // EOF (майже неможливо для urandom)
    } else {
      if (errno == EINTR) continue;
      close(fd);
      return 0;
    }
  }

  close(fd);
  return n - left;
}

int re4_sys_entropy(uint8_t *dst, size_t n) {
  if (!dst || n == 0) return -1;
  size_t got = re4_sys_entropy_impl(dst, n);
  if (got == 0) return -1;
  if (got > (size_t)INT_MAX) got = (size_t)INT_MAX;
  return (int)got;
}
