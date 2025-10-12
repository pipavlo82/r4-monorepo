#define _POSIX_C_SOURCE 200809L
#include "r4.h"
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/types.h>
#include <sys/time.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>

#include <openssl/hmac.h>
#include <openssl/sha.h>

#ifndef R4_DEFAULT_SOCK
#define R4_DEFAULT_SOCK "/run/r4sock/r4.sock"
#endif
#ifndef R4_KEY_PATH
#define R4_KEY_PATH "/etc/r4/secret.key"
#endif
#ifndef R4_MAX_REQ
#define R4_MAX_REQ (1u<<20)
#endif

static int g_fd = -1;
static unsigned char g_key[64];
static size_t g_keylen = 0;

static const uint32_t R4F1 = 0x52344631u; // 'R4F1'
static const uint32_t R4F2 = 0x52344632u; // 'R4F2'

static int set_timeouts(int fd, int ms) {
    if (ms <= 0) ms = 30000;
    struct timeval tv = { .tv_sec = ms/1000, .tv_usec = (ms%1000)*1000 };
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv))<0) return -1;
    if (setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv))<0) return -1;
    return 0;
}

static int load_key_once(void){
    if (g_keylen) return 0;
    const char *p = R4_KEY_PATH;
    FILE *f = fopen(p,"rb");
    if (!f) return -1;
    g_keylen = fread(g_key,1,sizeof(g_key),f);
    fclose(f);
    if (g_keylen == 0) return -1;
    return 0;
}

int r4_open_ex(const r4_opts *opts) {
    if (g_fd != -1) return 0;
    if (load_key_once()!=0) return -1;

    const char *path = (opts && opts->socket_path && *opts->socket_path) ? opts->socket_path : R4_DEFAULT_SOCK;
    int fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return -1;
    if (set_timeouts(fd, opts ? opts->timeout_ms : 30000) < 0) { close(fd); return -1; }

    struct sockaddr_un sa; memset(&sa,0,sizeof(sa));
    sa.sun_family = AF_UNIX;
    if (strlen(path) >= sizeof(sa.sun_path)) { close(fd); return -1; }
    strncpy(sa.sun_path, path, sizeof(sa.sun_path)-1);

    if (connect(fd,(struct sockaddr*)&sa,sizeof(sa)) < 0) { close(fd); return -1; }
    g_fd = fd;
    return 0;
}

static int hmac_check(const void *hdr, size_t hdrlen,
                      const unsigned char *nonce8,
                      const unsigned char *data, size_t n,
                      const unsigned char *tag32)
{
    unsigned char mac[EVP_MAX_MD_SIZE];
    unsigned int maclen=0;
    HMAC(EVP_sha256(), g_key, (int)g_keylen, (const unsigned char*)hdr, (int)hdrlen, mac, &maclen);
    HMAC(EVP_sha256(), g_key, (int)g_keylen, nonce8, 8, mac, &maclen); // chaining is not correct; do single-shot:
    // Recompute correctly as one-shot:
    unsigned char allhdr[8];
    memcpy(allhdr, hdr, 8);
    HMAC_CTX *ctx = HMAC_CTX_new();
    if (!ctx) return -1;
    int ok = 0;
    if (HMAC_Init_ex(ctx, g_key, (int)g_keylen, EVP_sha256(), NULL) == 1
     && HMAC_Update(ctx, allhdr, 8) == 1
     && HMAC_Update(ctx, nonce8, 8) == 1
     && HMAC_Update(ctx, data, n) == 1
     && HMAC_Final(ctx, mac, &maclen) == 1) {
        ok = 1;
    }
    HMAC_CTX_free(ctx);
    if (!ok || maclen != 32) return -1;
    return CRYPTO_memcmp(mac, tag32, 32) == 0 ? 0 : -1;
}

static long long r4_pull(void *out, size_t want) {
    if (g_fd < 0) return -1;
    unsigned char *o = (unsigned char*)out;
    size_t left = want;

    while (left) {
        uint32_t chunk = (left > R4_MAX_REQ) ? (uint32_t)R4_MAX_REQ : (uint32_t)left;

        struct __attribute__((packed)) { uint32_t magic, nbytes; } req = { R4F1, chunk };
        ssize_t w = send(g_fd, &req, sizeof(req), MSG_NOSIGNAL);
        if (w != (ssize_t)sizeof(req)) return -1;

        struct __attribute__((packed)) { uint32_t magic, nbytes; } hdr;
        ssize_t r = recv(g_fd, &hdr, sizeof(hdr), MSG_WAITALL);
        if (r != (ssize_t)sizeof(hdr)) return -1;
        if (hdr.magic != R4F2 || hdr.nbytes > chunk) return -1;

        size_t n = hdr.nbytes;
        if (!n) break; // EOF

        unsigned char nonce[8];
        if (recv(g_fd, nonce, 8, MSG_WAITALL) != 8) return -1;

        size_t got = 0;
        while (got < n) {
            ssize_t rr = recv(g_fd, o + got, n - got, 0);
            if (rr <= 0) return -1;
            got += (size_t)rr;
        }

        unsigned char tag[32];
        if (recv(g_fd, tag, 32, MSG_WAITALL) != 32) return -1;

        if (hmac_check(&hdr, sizeof(hdr), nonce, o, n, tag) != 0) return -1;

        o += n;
        left -= n;
    }
    return (long long)(want - left);
}

long long r4_read(void *out, size_t n) {
    if (!n) return 0;
    return r4_pull(out, n);
}

uint32_t r4_u32(void) {
    uint32_t v=0;
    if (r4_read(&v, sizeof(v)) != sizeof(v)) { r4_close(); return 0; }
    return v;
}

void r4_close(void) {
    if (g_fd >= 0) { close(g_fd); g_fd = -1; }
}
