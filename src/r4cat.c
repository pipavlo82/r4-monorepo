#include "r4.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void usage(const char *p) {
    fprintf(stderr,"Usage: %s [-n BYTES] [-hex] [-sock PATH] [-t TIMEOUT_MS]\n",p);
}

int main(int argc, char **argv) {
    long long nbytes = -1;
    int hex = 0;
    const char *sock = NULL;
    int tmo = 30000;

    for (int i=1;i<argc;i++) {
        if (!strcmp(argv[i],"-n") && i+1<argc) { nbytes = atoll(argv[++i]); }
        else if (!strcmp(argv[i],"-hex")) { hex = 1; }
        else if (!strcmp(argv[i],"-sock") && i+1<argc) { sock = argv[++i]; }
        else if (!strcmp(argv[i],"-t") && i+1<argc) { tmo = atoi(argv[++i]); }
        else { usage(argv[0]); return 1; }
    }

    struct r4_opts o = { .sock_path = sock ? sock : R4_DEFAULT_SOCK, .timeout_ms = tmo };
    if (r4_open_ex(&o) != 0) { fprintf(stderr,"r4_open failed\n"); return 1; }

    unsigned char buf[1<<16];

    if (nbytes < 0) {
        for (;;) {
            long long got = r4_read(buf, sizeof(buf));
            if (got <= 0) { fprintf(stderr,"r4_read error (HMAC/protocol)\n"); r4_close(); return 2; }
            if (!hex) {
                if (fwrite(buf,1,(size_t)got,stdout)!=(size_t)got) break;
            } else {
                for (long long i=0;i<got;i++) printf("%02x", buf[i]);
            }
        }
    } else {
        long long left = nbytes;
        while (left > 0) {
            size_t chunk = (left > (long long)sizeof(buf)) ? sizeof(buf) : (size_t)left;
            long long got = r4_read(buf, chunk);
            if (got <= 0) { fprintf(stderr,"r4_read error (HMAC/protocol)\n"); r4_close(); return 2; }
            if (!hex) {
                if (fwrite(buf,1,(size_t)got,stdout)!=(size_t)got) break;
            } else {
                for (long long i=0;i<got;i++) printf("%02x", buf[i]);
            }
            left -= got;
        }
    }
    if (hex) printf("\n");
    r4_close();
    return 0;
}
