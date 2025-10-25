#include "estimator.h"
#include <math.h>
double re4_90b_mcv_min_entropy(const unsigned char *buf, size_t n) {
  if (n == 0) return 0.0;
  unsigned int freq[256] = {0};
  for (size_t i = 0; i < n; ++i)
    freq[buf[i]]++;
  unsigned int maxf = 0;
  for (int i = 0; i < 256; ++i)
    if (freq[i] > maxf) maxf = freq[i];
  double pmax = (double)maxf / (double)n;
  if (pmax <= 0.0) return 0.0;
  double h = -log2(pmax);
  if (h < 0.0) h = 0.0;
  if (h > 8.0) h = 8.0;
  return h;
}
