#include "r4cs.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

static void usage(const char *prog){
    fprintf(stderr,
      "Usage: %s -n BYTES [-hex]\n"
      "Env: R4_PATH=/full/path/to/re4_stream  R4_SEED=...\n", prog);
}

int main(int argc, char **argv){
    size_t n = 0;
    int hex = 0;
    for(int i=1;i<argc;i++){
        if (!strcmp(argv[i],"-n") && i+1<argc) { n = (size_t)strtoull(argv[++i],NULL,0); }
        else if (!strcmp(argv[i],"-hex")) hex=1;
        else { usage(argv[0]); return 1; }
    }
    if (!n){ usage(argv[0]); return 1; }

    if (r4cs_init(NULL)!=0){
        fprintf(stderr,"r4cs_init failed\n");
        return 2;
    }

    uint8_t *buf = (uint8_t*)malloc(n);
    if (!buf){ perror("malloc"); return 3; }

    if (r4cs_random(buf,n)!=0){
        fprintf(stderr,"r4cs_random failed\n");
        free(buf); r4cs_close(); return 4;
    }

    if (hex){
        static const char *H="0123456789abcdef";
        for (size_t i=0;i<n;i++){
            putchar(H[buf[i]>>4]);
            putchar(H[buf[i]&15]);
        }
        putchar('\n');
    } else {
        fwrite(buf,1,n,stdout);
    }

    free(buf);
    r4cs_close();
    return 0;
}
