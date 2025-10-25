#include "health.h"

void re4_health_init(re4_health_t *h, uint32_t rct_maxrun, uint32_t ap_win, uint32_t ap_low,
                     uint32_t ap_high) {
  h->last_byte = 0;
  h->run_len = 0;
  h->max_run = rct_maxrun;
  h->ap_win = ap_win;
  h->ap_low = ap_low;
  h->ap_high = ap_high;
  h->ap_count = 0;
  h->ap_seen = 0;
}

int re4_health_feed(re4_health_t *h, const uint8_t *buf, size_t n) {
  for (size_t i = 0; i < n; ++i) {
    uint8_t b = buf[i];

    /* RCT on bytes */
    if (i == 0 && h->ap_seen == 0 && h->run_len == 0) {
      h->last_byte = b;
      h->run_len = 1;
    } else {
      if (b == h->last_byte) {
        if (++h->run_len > h->max_run) return 0;
      } else {
        h->last_byte = b;
        h->run_len = 1;
      }
    }

    /* AP on LSB */
    h->ap_count += (b & 1u);
    h->ap_seen++;
    if (h->ap_seen == h->ap_win) {
      if (h->ap_count < h->ap_low || h->ap_count > h->ap_high) return 0;
      h->ap_seen = 0;
      h->ap_count = 0; /* slide by window (non-overlap) */
    }
  }
  return 1;
}
