# R4 Secure IPC (Unix socket)

Socket path (default): /run/r4sock/r4.sock
Permissions: 660, group: r4users

Request (client -> server):
  struct {
    uint32_t magic;    // 0x52344631 ('R4F1')
    uint32_t nbytes;   // 1..(1<<20)
  } __attribute__((packed));

Response (server -> client):
  struct {
    uint32_t magic;    // 0x52344632 ('R4F2')
    uint32_t nbytes;   // фактично віддано
    uint8_t  data[n];  // n байтів
  }

nbytes ≤ 1 MiB/запит. Невідповідність magic/довжин => розрив.
