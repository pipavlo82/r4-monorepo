# R4 Secure IPC (Unix socket) + HMAC

Socket: /run/r4sock/r4.sock
Key: /etc/r4/secret.key (32B, root:root, 600)

Request (client -> server):
  struct { uint32_t magic=0x52344631; uint32_t nbytes; } LE, packed

Response (server -> client):
  struct { uint32_t magic=0x52344632; uint32_t nbytes; } LE, packed
  uint8_t nonce[8]
  uint8_t data[nbytes]
  uint8_t tag[32]   // HMAC-SHA256( key, header||nonce||data )

Будь-яка невідповідність => розрив.
