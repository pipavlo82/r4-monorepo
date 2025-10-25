#include <bbattery.h>
#include <stdint.h>
#include <stdio.h>
#include <unif01.h>

static FILE *in;

static unsigned int getbits(void) {
  // Повертаємо 32 біти (little-endian) з stdin буферизовано
  static unsigned char buf[1 << 20];
  static size_t len = 0, pos = 0;
  uint32_t x = 0;
  for (int i = 0; i < 32; i += 8) {
    if (pos >= len) {
      len = fread(buf, 1, sizeof(buf), in);
      if (!len) {
        fprintf(stderr, "\n[bigcrush_stdin] EOF\n");
        return 0;
      }
      pos = 0;
    }
    x |= ((uint32_t)buf[pos++]) << i;
  }
  return (unsigned int)x;
}

int main(void) {
  in = stdin;
  setvbuf(in, NULL, _IONBF, 0);
  unif01_Gen *gen = unif01_CreateExternGenBits("stdin_stream_u01", getbits);
  bbattery_BigCrush(gen);
  unif01_DeleteExternGenBits(gen);
  return 0;
}
