#define _POSIX_C_SOURCE 200809L
#include "r4cs.h"
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>

#ifndef R4_RESEED_INTERVAL
#define R4_RESEED_INTERVAL (1u<<20) /* кожні ~1 МіБ виводу */
#endif

// -------- util: secure memset --------
static void secure_bzero(void *p, size_t n) {
#if defined(__STDC_LIB_EXT1__)
    memset_s(p, n, 0, n);
#else
    volatile unsigned char *vp = (volatile unsigned char*)p;
    while (n--) *vp++ = 0;
#endif
}

// -------- ChaCha20 core (мінімум) --------
typedef struct {
    uint8_t key[32];
    uint8_t nonce[12];
    uint32_t counter;
} chacha20_ctx;

static inline uint32_t rotl32(uint32_t x, int r){ return (x<<r)|(x>>(32-r)); }
#define QR(a,b,c,d) do{ \
    a+=b; d^=a; d=rotl32(d,16); \
    c+=d; b^=c; b=rotl32(b,12); \
    a+=b; d^=a; d=rotl32(d, 8); \
    c+=d; b^=c; b=rotl32(b, 7); \
}while(0)

static void chacha20_block(const chacha20_ctx *ctx, uint32_t out[16]) {
    static const uint32_t C[4] = {0x61707865,0x3320646e,0x79622d32,0x6b206574};
    uint32_t s[16];
    s[0]=C[0]; s[1]=C[1]; s[2]=C[2]; s[3]=C[3];
    // key
    for (int i=0;i<8;i++){
        s[4+i] = ((uint32_t)ctx->key[4*i]) |
                 ((uint32_t)ctx->key[4*i+1] << 8) |
                 ((uint32_t)ctx->key[4*i+2] << 16) |
                 ((uint32_t)ctx->key[4*i+3] << 24);
    }
    // counter + nonce
    s[12] = ctx->counter;
    s[13] = ((uint32_t)ctx->nonce[0]) | ((uint32_t)ctx->nonce[1]<<8) |
            ((uint32_t)ctx->nonce[2]<<16) | ((uint32_t)ctx->nonce[3]<<24);
    s[14] = ((uint32_t)ctx->nonce[4]) | ((uint32_t)ctx->nonce[5]<<8) |
            ((uint32_t)ctx->nonce[6]<<16) | ((uint32_t)ctx->nonce[7]<<24);
    s[15] = ((uint32_t)ctx->nonce[8]) | ((uint32_t)ctx->nonce[9]<<8) |
            ((uint32_t)ctx->nonce[10]<<16)| ((uint32_t)ctx->nonce[11]<<24);

    for (int i=0;i<16;i++) out[i]=s[i];

    for (int i=0;i<10;i++){
        QR(out[0],out[4],out[8],out[12]);
        QR(out[1],out[5],out[9],out[13]);
        QR(out[2],out[6],out[10],out[14]);
        QR(out[3],out[7],out[11],out[15]);
        QR(out[0],out[5],out[10],out[15]);
        QR(out[1],out[6],out[11],out[12]);
        QR(out[2],out[7],out[8],out[13]);
        QR(out[3],out[4],out[9],out[14]);
    }
    for (int i=0;i<16;i++) out[i]+=s[i];
}

static void chacha20_generate(chacha20_ctx *ctx, uint8_t *out, size_t n) {
    while (n) {
        uint32_t blk[16];
        chacha20_block(ctx, blk);
        ctx->counter++;
        size_t take = n < 64 ? n : 64;
        memcpy(out, blk, take);
        secure_bzero(blk, sizeof(blk));
        out += take; n -= take;
    }
}

// -------- HKDF-SHA256 (через OpenSSL HMAC) --------
static int hkdf_extract(const uint8_t *salt,size_t salt_len,
                        const uint8_t *ikm,size_t ikm_len,
                        uint8_t out_prk[32]) {
    unsigned int len=0;
    unsigned char *p = HMAC(EVP_sha256(), salt, (int)salt_len, ikm, ikm_len, out_prk, &len);
    return (p && len==32) ? 0 : -1;
}

static int hkdf_expand(const uint8_t prk[32],
                       const uint8_t *info,size_t info_len,
                       uint8_t *okm,size_t okm_len) {
    uint8_t T[32]; size_t Tlen=0; uint8_t c=1;
    size_t done=0;
    while (done<okm_len) {
        HMAC_CTX *ctx = HMAC_CTX_new();
        if(!ctx) return -1;
        if (HMAC_Init_ex(ctx, prk, 32, EVP_sha256(), NULL) != 1) { HMAC_CTX_free(ctx); return -1; }
        if (Tlen) HMAC_Update(ctx, T, Tlen);
        if (info && info_len) HMAC_Update(ctx, info, info_len);
        HMAC_Update(ctx, &c, 1);
        unsigned int outl=0;
        HMAC_Final(ctx, T, &outl);
        HMAC_CTX_free(ctx);
        size_t copy = (okm_len - done < 32) ? (okm_len - done) : 32;
        memcpy(okm+done, T, copy);
        done += copy; Tlen = outl; c++;
    }
    secure_bzero(T, sizeof(T));
    return 0;
}

static int hkdf_sha256(const uint8_t *salt,size_t salt_len,
                       const uint8_t *ikm,size_t ikm_len,
                       const uint8_t *info,size_t info_len,
                       uint8_t *okm,size_t okm_len) {
    uint8_t prk[32];
    if (hkdf_extract(salt, salt_len, ikm, ikm_len, prk) != 0) return -1;
    int rc = hkdf_expand(prk, info, info_len, okm, okm_len);
    secure_bzero(prk, sizeof(prk));
    return rc;
}

// -------- глобальний DRBG --------
static chacha20_ctx G;
static size_t g_bytes_since_reseed = SIZE_MAX; // форс перший reseed
static FILE *g_r4 = NULL;
static pthread_mutex_t g_mx = PTHREAD_MUTEX_INITIALIZER;

// читання з /dev/urandom
static int read_urandom(void *buf, size_t n) {
    FILE *f = fopen("/dev/urandom","rb"); if(!f) return -1;
    size_t got = fread(buf,1,n,f); fclose(f);
    return (got==n)?0:-1;
}

// запуск re4_stream
static int r4_open(const char *path) {
    if (g_r4) return 0;
    const char *p = path;
    if (!p || !*p) { p = getenv("R4_PATH"); if(!p||!*p) p = "re4_stream"; }
    const char *seed = getenv("R4_SEED");
    char cmd[512];
    if (seed && *seed) snprintf(cmd,sizeof(cmd),"%s %s", p, seed);
    else {
        unsigned long long s=0; read_urandom(&s, sizeof(s)); if(!s) s=1ULL;
        snprintf(cmd,sizeof(cmd),"%s %llu", p, (unsigned long long)s);
    }
    g_r4 = popen(cmd, "r");
    return g_r4 ? 0 : -1;
}

static int r4_read(void *buf, size_t n) {
    if (!g_r4) return -1;
    uint8_t *p=(uint8_t*)buf; size_t total=0;
    while (total<n) {
        size_t got = fread(p+total,1,n-total,g_r4);
        if (got==0) return -1;
        total += got;
    }
    return 0;
}

static int reseed_locked(void) {
    // збираємо мікс: 64B OS + 64B R4 + контекст
    uint8_t salt[64], r4buf[64], ikm[64];
    if (read_urandom(salt, sizeof(salt)) != 0) return -1;
    if (r4_read(r4buf, sizeof(r4buf)) != 0) return -1;

    // info: PID|time|“R4-CS v1”
    uint8_t info[64]; memset(info,0,sizeof(info));
    uint32_t pid = (uint32_t)getpid();
    uint64_t t = (uint64_t)time(NULL);
    memcpy(info, &pid, sizeof(pid));
    memcpy(info+8, &t, sizeof(t));
    memcpy(info+16, "R4-CS v1", 8);

    // ikm = XOR(OS, R4) для простоти
    for (size_t i=0;i<sizeof(ikm);i++) ikm[i] = salt[i] ^ r4buf[i];

    // HKDF -> 32 key + 12 nonce + 4 counter (всього 48)
    uint8_t okm[48];
    if (hkdf_sha256(salt, sizeof(salt), ikm, sizeof(ikm), info, sizeof(info), okm, sizeof(okm)) != 0)
        return -1;

    memcpy(G.key,   okm, 32);
    memcpy(G.nonce, okm+32, 12);
    memcpy(&G.counter, okm+44, 4);

    secure_bzero(okm, sizeof(okm));
    secure_bzero(salt, sizeof(salt));
    secure_bzero(r4buf, sizeof(r4buf));
    secure_bzero(ikm, sizeof(ikm));

    g_bytes_since_reseed = 0;
    return 0;
}

// -------- публічні API --------
int r4cs_init(const char *r4_path) {
    pthread_mutex_lock(&g_mx);
    int rc = 0;
    if (r4_open(r4_path) != 0) rc = -1;
    else if (reseed_locked() != 0) rc = -2;
    pthread_mutex_unlock(&g_mx);
    return rc;
}

int r4cs_reseed(void) {
    pthread_mutex_lock(&g_mx);
    int rc = reseed_locked();
    pthread_mutex_unlock(&g_mx);
    return rc;
}

int r4cs_random(void *out, size_t n) {
    uint8_t *p = (uint8_t*)out;
    pthread_mutex_lock(&g_mx);
    if (g_bytes_since_reseed > R4_RESEED_INTERVAL) {
        if (reseed_locked() != 0) { pthread_mutex_unlock(&g_mx); return -1; }
    }
    while (n) {
        size_t chunk = n;
        if (g_bytes_since_reseed + chunk > R4_RESEED_INTERVAL)
            chunk = R4_RESEED_INTERVAL - g_bytes_since_reseed;
        if (chunk == 0) {
            if (reseed_locked()!=0) { pthread_mutex_unlock(&g_mx); return -1; }
            continue;
        }
        chacha20_generate(&G, p, chunk);
        p += chunk; n -= chunk; g_bytes_since_reseed += chunk;
    }
    pthread_mutex_unlock(&g_mx);
    return 0;
}

void r4cs_close(void) {
    pthread_mutex_lock(&g_mx);
    if (g_r4) { pclose(g_r4); g_r4=NULL; }
    secure_bzero(&G, sizeof(G));
    pthread_mutex_unlock(&g_mx);
}
