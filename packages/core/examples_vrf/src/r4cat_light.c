// r4cat_light.c
// Minimal demo client for CI / smoke tests.
// Reads N bytes from the core RNG binary (re4_dump) and prints as hex.
//
// This does NOT use the old Unix-socket IPC struct r4_opts.
// This is intentionally dumb but portable.

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>

static void to_hex(const uint8_t *buf, size_t n) {
    static const char *hex = "0123456789abcdef";
    for (size_t i = 0; i < n; i++) {
        putchar(hex[buf[i] >> 4]);
        putchar(hex[buf[i] & 0x0f]);
    }
    putchar('\n');
}

int main(int argc, char **argv) {
    // default 32 bytes
    size_t want = 32;
    if (argc > 1) {
        want = (size_t) strtoul(argv[1], NULL, 10);
        if (want == 0 || want > 1024*1024) {
            fprintf(stderr, "bad length\n");
            return 1;
        }
    }

    // Open the core RNG binary `re4_dump` from the release bundle layout:
    // In prod we'd have /opt/re4ctor/bin/re4_dump (or similar).
    // For CI we assume `packages/core/re4_release.tar.gz` exists,
    // but we don't actually unpack here. For smoke, let's just try local build path.
    //
    // Fallback strategy for CI:
    //  1. try ./packages/core/build/re4_dump
    //  2. if not, try ./bin/re4_dump
    //  3. if still not, bail.

    const char *candidates[] = {
        "packages/core/build/re4_dump",
        "bin/re4_dump",
        NULL
    };

    FILE *fp = NULL;
    for (int i = 0; candidates[i]; i++) {
        fp = fopen(candidates[i], "rb");
        if (fp) break;
    }

    if (!fp) {
        fprintf(stderr, "cannot open re4_dump (not built yet)\n");
        return 2;
    }

    uint8_t *buf = malloc(want);
    if (!buf) {
        fprintf(stderr, "oom\n");
        fclose(fp);
        return 3;
    }

    size_t got = fread(buf, 1, want, fp);
    fclose(fp);

    if (got != want) {
        fprintf(stderr, "short read (%zu/%zu)\n", got, want);
        free(buf);
        return 4;
    }

    // print as hex (just like /random?fmt=hex)
    to_hex(buf, got);
    free(buf);
    return 0;
}
