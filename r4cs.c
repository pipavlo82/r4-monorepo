// r4cs.c (фрагменти)

#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <errno.h>
#include <openssl/evp.h>
#include <openssl/core_names.h>
#include <openssl/kdf.h>

/* --- secure zero --- */
static void r4_secure_zero(void *p, size_t n) {
#if defined(__STDC_LIB_EXT1__)
    memset_s(p, n, 0, n);
#elif defined(HAVE_EXPLICIT_BZERO)
    explicit_bzero(p, n);
#elif defined(_WIN32)
    SecureZeroMemory(p, n);
#else
    volatile unsigned char *vp = (volatile unsigned char *)p;
    while (n--) *vp++ = 0;
#endif
}

/* --- HKDF-SHA256 (OpenSSL 3 EVP_KDF) --- */
static int hkdf_sha256(const unsigned char *ikm, size_t ikm_len,
                       const unsigned char *salt, size_t salt_len,
                       const unsigned char *info, size_t info_len,
                       unsigned char *out, size_t out_len) {
    int ok = 0;
    EVP_KDF *kdf = NULL;
    EVP_KDF_CTX *kctx = NULL;
    OSSL_PARAM params[5], *p = params;

    kdf = EVP_KDF_fetch(NULL, "HKDF", NULL);
    if (!kdf) goto end;
    kctx = EVP_KDF_CTX_new(kdf);
    if (!kctx) goto end;

    *p++ = OSSL_PARAM_construct_utf8_string(OSSL_KDF_PARAM_DIGEST, "SHA256", 0);
    *p++ = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_KEY, (void*)ikm, ikm_len);
    if (salt && salt_len) *p++ = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_SALT, (void*)salt, salt_len);
    if (info && info_len) *p++ = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_INFO, (void*)info, info_len);
    *p   = OSSL_PARAM_construct_end();

    if (EVP_KDF_derive(kctx, out, out_len, params) == 1) ok = 1;

end:
    EVP_KDF_CTX_free(kctx);
    EVP_KDF_free(kdf);
    return ok ? 0 : -1;
}

/* --- стан DRBG (ChaCha20 key/nonce/ctr), прикладова структура --- */
typedef struct {
    unsigned char key[32];
    unsigned char nonce[12];
    uint64_t      counter;
    int           initialized;
    int           deterministic; // 1 коли ініт з R4_SEED
} r4_ctx;

/* --- ініціалізація з SEED (без системної ентропії) --- */
int r4_init_from_seed(r4_ctx *ctx, const unsigned char *seed, size_t seed_len,
                      const unsigned char *info, size_t info_len)
{
    unsigned char okm[32 + 12]; // key||nonce
    if (hkdf_sha256(seed, seed_len, NULL, 0, info, info_len, okm, sizeof(okm)) != 0)
        return -1;

    memcpy(ctx->key,   okm, 32);
    memcpy(ctx->nonce, okm + 32, 12);
    r4_secure_zero(okm, sizeof(okm));
    ctx->counter = 0;
    ctx->initialized = 1;
    ctx->deterministic = 1;
    return 0;
}

/* --- ініціалізація з системної ентропії (коли SEED не задано) --- */
/* ВАЖЛИВО: цей шлях НЕ ВИКЛИКАЄТЬСЯ, якщо є R4_SEED */
static int r4_init_from_system(r4_ctx *ctx) {
    // тут можна читати getrandom()/URANDOM один раз,
    // але він не викликається в детермінованому режимі
    // (залиш як є, або реалізуй за потреби)
    return -1; // поки вимкнемо, щоб не було випадкових звернень
}

/* --- публічний init --- */
int r4_init_auto(r4_ctx *ctx) {
    const char *seed_env = getenv("R4_SEED");
    if (seed_env && seed_env[0]) {
        const unsigned char *seed = (const unsigned char*)seed_env;
        size_t seed_len = strlen(seed_env);
        const char *info_env = getenv("R4_INFO"); // optional
        const unsigned char *info = (const unsigned char*)info_env;
        size_t info_len = info_env ? strlen(info_env) : 0;
        return r4_init_from_seed(ctx, seed, seed_len, info, info_len);
    }
    // без SEED — або ініт із системи, або фейл (щоб не було “тихого” доступу)
    return r4_init_from_system(ctx);
}

/* --- генерація байтів через EVP_chacha20 --- */
static int r4_generate(r4_ctx *ctx, unsigned char *out, size_t out_len) {
    if (!ctx || !ctx->initialized) return -1;

    EVP_CIPHER_CTX *cctx = EVP_CIPHER_CTX_new();
    if (!cctx) return -1;
    int ok = 0, outl;

    if (EVP_EncryptInit_ex(cctx, EVP_chacha20(), NULL, NULL, NULL) != 1) goto end;

    // ChaCha20 параметри: ключ, nonce (12B), лічильник (32-біт у TLS; тут підженемо через ctrl)
    if (EVP_CIPHER_CTX_ctrl(cctx, EVP_CTRL_AEAD_SET_IVLEN, 12, NULL) != 1) goto end;
   unsigned char iv[16];
memcpy(iv, ctx->nonce, 12);
uint32_t ctr = (uint32_t)ctx->counter; // adjust as needed
memcpy(iv + 12, &ctr, 4); // little-endian
if (EVP_EncryptInit_ex(cctx, NULL, NULL, ctx->key, iv) != 1) goto end;
    if (EVP_EncryptUpdate(cctx, out, &outl, out, (int)out_len) != 1) goto end;
    // у потокових шифрах буфер in==out дає XOR; простіше згенерувати нулі такого ж розміру.
    // Краще так:
    unsigned char *zeros = calloc(1, out_len);
    if (!zeros) goto end;
    if (EVP_EncryptUpdate(cctx, out, &outl, zeros, (int)out_len) != 1) { free(zeros); goto end; }
    free(zeros);

    // оновити counter: крок у 64-байтних блоках
    ctx->counter += (out_len + 63) / 64;
    ok = 1;

end:
    EVP_CIPHER_CTX_free(cctx);
    return ok ? 0 : -1;
}

/* --- очищення стану --- */
void r4_free(r4_ctx *ctx) {
    if (!ctx) return;
    r4_secure_zero(ctx->key, sizeof(ctx->key));
    r4_secure_zero(ctx->nonce, sizeof(ctx->nonce));
    r4_secure_zero(ctx, sizeof(*ctx));
}
