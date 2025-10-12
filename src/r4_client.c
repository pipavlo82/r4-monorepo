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
#include <openssl/evp.h>

#ifndef R4_MAX_REQ
#define R4_MAX_REQ (1u<<20)  // 1 MiB per request
#endif

static int g_fd = -1;
static unsigned char g_key[32];
static size_t g_keylen = 0;

static uint32_t MAGIC_REQ = 0x52344631u; // 'R4F1'
static uint32_t MAGIC_RES = 0x52344632u; // 'R4F2'

static int set_timeouts(int fd, int ms) {
    if (ms <= 0) ms = 30000;
    struct timeval tv = { .tv_sec = ms/1000, .tv_usec = (ms%1000)*1000 };
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv))<0) return -1;
    if (setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv))<0) return -1;
    return 0;
}

static int load_key(unsigned char *out, size_t *outlen) {
    const char *path = "/etc/r4/secret.key";
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    ssize_t r = read(fd, out, 32);
    close(fd);
    if (r != 32) return -1;
    *outlen = 32;
    return 0;
}

static int hmac_check(const unsigned char *allhdr8, const unsigned char *nonce8,
                      const unsigned char *data, size_t n,
                      const unsigned char *tag32) {
    unsigned char mac[EVP_MAX_MD_SIZE];
    unsigned int maclen = 0;

    HMAC_CTX *ctx = HMAC_CTX_new();
    if (!ctx) return -1;
    int ok =
       HMAC_Init_ex(ctx, g_key, (int)g_keylen, EVP_sha256(), NULL) == 1 &&
       HMAC_Update(ctx, allhdr8, 8) == 1 &&
       HMAC_Update(ctx, nonce8, 8) == 1 &&
       HMAC_Update(ctx, data, n) == 1 &&
       HMAC_Final(ctx, mac, &maclen) == 1 &&
       maclen == 32 &&
       CRYPTO_memcmp(mac, tag32, 32) == 0;
    HMAC_CTX_free(ctx);
    return ok ? 0 : -1;
}

static int recv_exact(int fd, void *buf, size_t n) {
    unsigned char *p = (unsigned char *)buf;
    size_t left = n;
    while (left) {
        ssize_t r = recv(fd, p, left, MSG_WAITALL);
        if (r <= 0) return -1;
        p += (size_t)r; left -= (size_t)r;
    }
    return 0;
}

int r4_open_ex(const struct r4_opts *opts) {
    if (g_fd >= 0) return 0;

    if (load_key(g_key, &g_keylen) != 0) return -1;

    const char *sock = (opts && opts->sock_path && *opts->sock_path) ? opts->sock_path : R4_DEFAULT_SOCK;
    int tmo = (opts && opts->timeout_ms > 0) ? opts->timeout_ms : 30000;

    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    if (set_timeouts(fd, tmo) != 0) { close(fd); return -1; }

    struct sockaddr_un su;
    memset(&su, 0, sizeof(su));
    su.sun_family = AF_UNIX;
    if (strlen(sock) >= sizeof(su.sun_path)) { close(fd); return -1; }
    strcpy(su.sun_path, sock);

    if (connect(fd, (struct sockaddr*)&su, sizeof(su)) != 0) {
        close(fd);
        return -1;
    }
    g_fd = fd;
    return 0;
}

long long r4_read(void *out, size_t n) {
    if (g_fd < 0) return -1;
    if (!out || n == 0) return 0;
    if (n > R4_MAX_REQ) n = R4_MAX_REQ;

    uint32_t hdr[2] = {MAGIC_REQ, (uint32_t)n};
    if (send(g_fd, hdr, sizeof(hdr), MSG_NOSIGNAL) != (ssize_t)sizeof(hdr))
        return -1;

    uint32_t rhdr[2];
    if (recv_exact(g_fd, rhdr, sizeof(rhdr)) != 0) return -1;
    if (rhdr[0] != MAGIC_RES) return -1;

    uint32_t rlen = rhdr[1];
    if (rlen == 0 || rlen > n) return -1;

    unsigned char nonce[8];
    if (recv_exact(g_fd, nonce, 8) != 0) return -1;

    if (recv_exact(g_fd, out, rlen) != 0) return -1;

    unsigned char tag[32];
    if (recv_exact(g_fd, tag, 32) != 0) return -1;

    if (hmac_check((unsigned char*)rhdr, nonce, (unsigned char*)out, rlen, tag) != 0) {
        return -1;
    }
    return (long long)rlen;
}

uint32_t r4_u32(void) {
    uint32_t v = 0;
    long long got = r4_read(&v, sizeof(v));
    if (got != (long long)sizeof(v)) {
        r4_close();
        return 0;
    }
    return v;
}

void r4_close(void) {
    if (g_fd >= 0) { close(g_fd); g_fd = -1; }
    OPENSSL_cleanse(g_key, sizeof(g_key));
    g_keylen = 0;
}
