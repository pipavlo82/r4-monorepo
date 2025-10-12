import os, socket, struct

DEFAULT_SOCK = os.environ.get("R4_SOCK", "/run/r4sock/r4.sock")

class R4:
    def __init__(self, sock_path: str = DEFAULT_SOCK):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.connect(sock_path)
    def read(self, n: int) -> bytes:
        # Minimal request: MAGIC + LEN; server returns framed/HMACed data (handled server-side).
        self.s.sendall(struct.pack("<II", 0x52344631, n))  # 'R4F1'
        hdr = self._recv_exact(8)                          # 'R4F2' + len
        magic, ln = struct.unpack("<II", hdr)
        if magic != 0x52344632 or ln == 0:                 # 'R4F2'
            raise RuntimeError("protocol/HMAC error")
        return self._recv_exact(ln)
    def _recv_exact(self, n):
        b = bytearray()
        while len(b) < n:
            chunk = self.s.recv(n - len(b))
            if not chunk: raise RuntimeError("short read")
            b.extend(chunk)
        return bytes(b)
    def close(self):
        try: self.s.close()
        except: pass

if __name__ == "__main__":
    r = R4()
    print(r.read(32).hex())
    r.close()
