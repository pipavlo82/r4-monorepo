import os, socket, struct

DEFAULT_SOCK = "/run/r4sock/r4.sock"
R4F1 = 0x52344631
R4F2 = 0x52344632
MAX_REQ = 1<<20

class R4:
    def __init__(self, socket_path=None, timeout=30.0):
        self.sock_path = socket_path or os.environ.get("R4_SOCK", DEFAULT_SOCK)
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.settimeout(timeout)
        self.s.connect(self.sock_path)

    def read(self, n:int) -> bytes:
        out = bytearray()
        left = n
        while left>0:
            chunk = min(left, MAX_REQ)
            self.s.sendall(struct.pack("<II", R4F1, chunk))
            hdr = self._recvn(8)
            magic, nbytes = struct.unpack("<II", hdr)
            if magic != R4F2 or nbytes>chunk:
                raise RuntimeError("protocol error")
            if nbytes==0: break
            out += self._recvn(nbytes)
            left -= nbytes
        return bytes(out)

    def _recvn(self, n):
        buf = bytearray()
        while len(buf) < n:
            part = self.s.recv(n - len(buf))
            if not part:
                raise RuntimeError("eof")
            buf += part
        return bytes(buf)

    def close(self):
        try: self.s.close()
        except: pass

if __name__ == "__main__":
    r = R4()
    print(r.read(64).hex())
    r.close()
