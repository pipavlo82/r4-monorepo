# Public API (C / CLI / Python)

C (static lib)
  int       r4_open(const char *path, const char *seed_str);
  long long r4_read(void *out, size_t n);
  uint32_t  r4_u32(void);
  void      r4_close(void);

Environment variables
  R4_SOCK=/run/r4sock/r4.sock   (if using IPC server)
  R4_KEY_PATH=/etc/r4/secret.key  (32B HMAC key)

CLI examples
  ./bin/r4cat -n 64 -hex
  ./bin/r4cat -n 8388608 > chunk.bin

Python (thin wrapper via subprocess)
  from subprocess import check_output
  rnd = check_output(["./bin/r4cat","-n","32"])
  print(rnd.hex())
