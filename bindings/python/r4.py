import os, socket, struct

DEFAULT_SOCK = os.environ.get("R4_SOCK", "/run/r4sock/r4.sock")

class R4:
    def __init__(self, sock_path: str = DEFAULT_SOCK):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.connect(sock_path)

    def read(self, n: int) -> bytes:
        # Request: MAGIC('R4F1') + LEN
        self.s.sendall(struct.pack("<II", 0x52344631, n))
        # Response header: MAGIC('R4F2') + LEN
        hdr = self._recv_exact(8)
        magic, ln = struct.unpack("<II", hdr)
        if magic != 0x52344632 or ln == 0:
            raise RuntimeError("protocol/HMAC error")
        return self._recv_exact(ln)

    def _recv_exact(self, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            chunk = self.s.recv(n - len(out))
            if not chunk:
                raise RuntimeError("short read")
            out.extend(chunk)
        return bytes(out)

    def close(self):
        try: self.s.close()
        except: pass

if __name__ == "__main__":
    r = R4()
    print(r.read(32).hex())
    r.close()
