// r4cs.c — R4-CS (HKDF-SHA256 → ChaCha20 DRBG) із опційною зовн. ентропією
// Портативно для OpenSSL 1.1.1/3.x: БЕЗ EVP_CTRL_CHACHA20_SET_COUNTER.
// IV = [counter(4B LE)] + [nonce(12B)]

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>

#include <openssl/evp.h>
#include <openssl/kdf.h>        // EVP_PKEY_HKDF
#include <openssl/err.h>

#include "r4cs.h"               // див. примітку у відповіді

#ifndef R4_READ_CHUNK
#define R4_READ_CHUNK  (1<<20)  // 1 MiB при генерації
#endif

#ifndef R4_ENTROPY_MAX
#define R4_ENTROPY_MAX (1<<20)  // максимум, який читаємо з зовн. джерела (1 MiB)
#endif

// ------------------------------------------------------------
// Внутрішні допоміжні

static void r4_memzero(void *p, size_t n) {
    volatile unsigned char *vp = (volatile unsigned char *)p;
    while (n--) *vp++ = 0;
}

// Читання з /dev/urandom або getrandom(2) (де є).
static int r4_get_system_entropy(void *buf, size_t n) {
#if defined(__linux__)
    // спробуємо getrandom без блокування; якщо нема — fallback
    // Не включаємо <sys/random.h>, щоб уникнути залежностей на старих glibc;
    // просто читаємо з /dev/urandom:
#endif
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) return -1;
    size_t off = 0;
    while (off < n) {
        ssize_t r = read(fd, (unsigned char*)buf + off, n - off);
        if (r < 0) { if (errno == EINTR) continue; close(fd); return -1; }
        if (r == 0) { close(fd); return -1; }
        off += (size_t)r;
    }
    close(fd);
    return 0;
}

// HKDF-SHA256: out = HKDF(salt, ikm, info, out_len)
static int r4_hkdf_sha256(const unsigned char *salt, size_t salt_len,
                          const unsigned char *ikm,  size_t ikm_len,
                          const unsigned char *info, size_t info_len,
                          unsigned char *out, size_t out_len) {
    int ok = 0;
    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_HKDF, NULL);
    if (!pctx) return 0;

    if (EVP_PKEY_derive_init(pctx) <= 0) goto done;
    if (EVP_PKEY_CTX_set_hkdf_md(pctx, EVP_sha256()) <= 0) goto done;
    if (salt && salt_len) {
        if (EVP_PKEY_CTX_set1_hkdf_salt(pctx, salt, (int)salt_len) <= 0) goto done;
    } else {
        // OpenSSL дозволяє salt бути NULL — це норм OK
    }
    if (EVP_PKEY_CTX_set1_hkdf_key(pctx, ikm, (int)ikm_len) <= 0) goto done;
    if (info && info_len) {
        if (EVP_PKEY_CTX_add1_hkdf_info(pctx, info, (int)info_len) <= 0) goto done;
    }
    size_t olen = out_len;
    if (EVP_PKEY_derive(pctx, out, &olen) <= 0) goto done;
    ok = (olen == out_len);

done:
    EVP_PKEY_CTX_free(pctx);
    return ok;
}

// Побудувати IV: [ctr(LE 32b)] + [nonce(12B)]
static void r4_build_iv(uint32_t ctr, const unsigned char nonce[12],
                        unsigned char iv16[16]) {
    iv16[0] = (unsigned char)(ctr & 0xff);
    iv16[1] = (unsigned char)((ctr >> 8) & 0xff);
    iv16[2] = (unsigned char)((ctr >> 16) & 0xff);
    iv16[3] = (unsigned char)((ctr >> 24) & 0xff);
    memcpy(iv16 + 4, nonce, 12);
}

// Єдине місце ініціалізації ключа/nonce за HKDF.
// ikm = системна ентропія || (опційно) зовнішня ентропія || seed (якщо R4_SEED).
static int r4_derive_key_nonce(struct r4ctx *ctx,
                               const unsigned char *ikm, size_t ikm_len,
                               const unsigned char *salt, size_t salt_len) {
    unsigned char okm[32 + 12]; // key || nonce
    const unsigned char info[] = "r4cs/hkdf/v1";
    if (!r4_hkdf_sha256(salt, salt_len, ikm, ikm_len, info, sizeof(info)-1,
                        okm, sizeof(okm))) {
        r4_memzero(okm, sizeof(okm));
        return -1;
    }
    memcpy(ctx->key,   okm, 32);
    memcpy(ctx->nonce, okm + 32, 12);
    ctx->counter = 0;
    r4_memzero(okm, sizeof(okm));
    return 0;
}

// ------------------------------------------------------------
// API

int r4_init_from_system(struct r4ctx *ctx) {
    if (!ctx) return -1;

    unsigned char sys[64];     // початкове IKM
    unsigned char salt[32];

    if (r4_get_system_entropy(sys, sizeof(sys)) != 0) return -1;
    if (r4_get_system_entropy(salt, sizeof(salt)) != 0) {
        r4_memzero(sys, sizeof(sys));
        return -1;
    }

    // Якщо задано детерм. seed — доміксуємо його у IKM
    const char *seed_env = getenv("R4_SEED");
    if (seed_env && *seed_env) {
        // просте домішування: HKDF(sys, seed_env) як новий ikm
        unsigned char mix[64];
        size_t seed_len = strlen(seed_env);
        if (!r4_hkdf_sha256(sys, sizeof(sys),
                            (const unsigned char*)seed_env, seed_len,
                            (const unsigned char*)"mix", 3, mix, sizeof(mix))) {
            r4_memzero(sys, sizeof(sys));
            r4_memzero(salt, sizeof(salt));
            return -1;
        }
        memcpy(sys, mix, sizeof(sys));
        r4_memzero(mix, sizeof(mix));
    }

    int rc = r4_derive_key_nonce(ctx, sys, sizeof(sys), salt, sizeof(salt));
    r4_memzero(sys, sizeof(sys));
    r4_memzero(salt, sizeof(salt));
    return rc;
}

// Ініціалізація з додатковою зовнішньою ентропією: читаємо перші N байтів з файлу/pipe.
int r4_init_from_path(struct r4ctx *ctx, const char *path) {
    if (!ctx || !path) return -1;

    // 1) базова системна ентропія
    unsigned char sys[64];
    if (r4_get_system_entropy(sys, sizeof(sys)) != 0) return -1;

    // 2) зовнішня ентропія
    unsigned char *ext = NULL;
    size_t ext_len = 0;

    int fd = open(path, O_RDONLY);
    if (fd >= 0) {
        ext = (unsigned char*)malloc(R4_ENTROPY_MAX);
        if (!ext) { close(fd); r4_memzero(sys, sizeof(sys)); return -1; }
        ssize_t r = read(fd, ext, R4_ENTROPY_MAX);
        if (r > 0) ext_len = (size_t)r;
        close(fd);
        // якщо нічого не прочитали — просто 0 байтів
    }

    // сіль
    unsigned char salt[32];
    if (r4_get_system_entropy(salt, sizeof(salt)) != 0) {
        r4_memzero(sys, sizeof(sys));
        free(ext);
        return -1;
    }

    // побудуємо IKM: HKDF( salt=sys, ikm=ext || sys )
    // Якщо ext_len==0 — все одно працює.
    unsigned char ikm[64];
    size_t off = 0;
    if (ext_len) {
        size_t take = ext_len > sizeof(ikm) ? sizeof(ikm) : ext_len;
        memcpy(ikm + off, ext, take);
        off += take;
    }
    // доміксуємо sys (щоб було мін. 64 байтів IKM)
    size_t tail = sizeof(ikm) - off;
    if (tail > sizeof(sys)) tail = sizeof(sys);
    memcpy(ikm + off, sys, tail);
    off += tail;

    int rc = r4_derive_key_nonce(ctx, ikm, off, salt, sizeof(salt));

    r4_memzero(sys, sizeof(sys));
    r4_memzero(ikm, sizeof(ikm));
    r4_memzero(salt, sizeof(salt));
    if (ext) { r4_memzero(ext, ext_len); free(ext); }

    // Додатковий детермінізм, якщо задано R4_SEED:
    const char *seed_env = getenv("R4_SEED");
    if (rc == 0 && seed_env && *seed_env) {
        unsigned char mix[44]; // 32+12
        if (!r4_hkdf_sha256(NULL, 0,
                (const unsigned char*)seed_env, strlen(seed_env),
                (const unsigned char*)"seed-mix", 8, mix, sizeof(mix))) {
            return -1;
        }
        memcpy(ctx->key,   mix, 32);
        memcpy(ctx->nonce, mix+32, 12);
        ctx->counter = 0;
        r4_memzero(mix, sizeof(mix));
    }
    return rc;
}

void r4_free(struct r4ctx *ctx) {
    if (!ctx) return;
    r4_memzero(ctx, sizeof(*ctx));
}

// Генерація out_len байтів потоку.
// Реалізація: шифруємо нулі ChaCha20; лічильник інкрементується самим шифром.
// Для відновлення позиції — заново будуємо IV з потрібним counter.
int r4_generate(struct r4ctx *ctx, unsigned char *out, size_t out_len) {
    if (!ctx || (!out && out_len)) return -1;
    if (out_len == 0) return 0;

    int ok = -1;
    EVP_CIPHER_CTX *cctx = EVP_CIPHER_CTX_new();
    if (!cctx) return -1;

    unsigned char iv16[16];
    r4_build_iv(ctx->counter, ctx->nonce, iv16);

    if (EVP_EncryptInit_ex(cctx, EVP_chacha20(), NULL, ctx->key, iv16) != 1) {
        goto done;
    }

    unsigned char *zeros = NULL;
    size_t chunk = R4_READ_CHUNK;
    if (chunk > out_len) chunk = out_len;
    zeros = (unsigned char*)calloc(1, chunk);
    if (!zeros) goto done;

    size_t remaining = out_len;
    int outl = 0;

    while (remaining) {
        size_t this = remaining < chunk ? remaining : chunk;
        if (EVP_EncryptUpdate(cctx, out, &outl, zeros, (int)this) != 1) {
            goto done;
        }
        out      += (size_t)outl;
        remaining -= (size_t)outl;
    }

    // Порахувати, на скільки блоків просунулись: у ChaCha20 блок = 64 байти (16 слів).
    // Але оскільки ми стартували з exact counter у IV та просто "крутили" stream,
    // збільшимо логічний лічильник на кількість 64B-блоків.
    ctx->counter += (uint32_t)((out_len + 63u) / 64u);
    ok = 0;

done:
    if (zeros) { r4_memzero(zeros, chunk); free(zeros); }
    EVP_CIPHER_CTX_free(cctx);
    return ok;
}
