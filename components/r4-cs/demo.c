#include "r4cs.h"
#include <stdio.h>
#include <stddef.h>

int main(void) {
    if (r4cs_init(NULL) != 0) {
        fprintf(stderr, "r4cs_init failed\n");
        return 1;
    }
    unsigned char b[32];
    if (r4cs_random(b, sizeof b) != 0) {
        fprintf(stderr, "r4cs_random failed\n");
        r4cs_close();
        return 2;
    }
    for (size_t i = 0; i < sizeof b; i++) printf("%02x", b[i]);
    putchar('\n');
    r4cs_close();
    return 0;
}
