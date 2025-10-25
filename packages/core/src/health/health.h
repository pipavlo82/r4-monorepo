#pragma once
#include <stddef.h>
#include <stdint.h>

typedef struct {
  /* RCT: repetition count test on bytes */
  uint8_t last_byte;
  uint32_t run_len;
  uint32_t max_run; /* threshold: fail if run_len > max_run */

  /* AP: adaptive proportion on LSB in a sliding window */
  uint32_t ap_win;   /* window size (e.g., 1024) */
  uint32_t ap_low;   /* lower bound of ones */
  uint32_t ap_high;  /* upper bound of ones */
  uint32_t ap_count; /* ones in current window */
  uint32_t ap_seen;  /* bytes seen in current window */
} re4_health_t;

void re4_health_init(re4_health_t *h, uint32_t rct_maxrun, uint32_t ap_win, uint32_t ap_low,
                     uint32_t ap_high);

/* Feed bytes; return 1=ok, 0=health fail (caller should pause/gate output). */
int re4_health_feed(re4_health_t *h, const uint8_t *buf, size_t n);
