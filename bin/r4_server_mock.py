#!/usr/bin/env python3
import os, socket, struct, sys, grp

SOCK_DIR = "/run/r4sock"
SOCK_PATH = f"{SOCK_DIR}/r4.sock"
R4F1 = 0x52344631
R4F2 = 0x52344632
MAX_REQ = 1<<20

def main():
    os.makedirs(SOCK_DIR, exist_ok=True)
    try: os.remove(SOCK_PATH)
    except FileNotFoundError: pass

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(SOCK_PATH)
    os.chmod(SOCK_PATH, 0o660)
    try:
        gid = grp.getgrnam("r4users").gr_gid
        os.chown(SOCK_PATH, 0, gid)
    except KeyError:
        pass
    s.listen(16)
    print(f"[mock] listening on {SOCK_PATH}", file=sys.stderr)

    while True:
        c, _ = s.accept()
        try:
            while True:
                hdr = recvn(c, 8)
                if not hdr: break
                magic, nbytes = struct.unpack("<II", hdr)
                if magic != R4F1 or nbytes>MAX_REQ or nbytes==0:
                    c.sendall(struct.pack("<II", R4F2, 0))
                    break
                data = read_urandom(nbytes)
                c.sendall(struct.pack("<II", R4F2, len(data)) + data)
        except Exception:
            pass
        finally:
            c.close()

def recvn(sock, n):
    buf = bytearray()
    while len(buf)<n:
        part = sock.recv(n-len(buf))
        if not part: return None
        buf += part
    return bytes(buf)

def read_urandom(n):
    with open("/dev/urandom","rb") as f:
        return f.read(n)

if __name__ == "__main__":
    main()
