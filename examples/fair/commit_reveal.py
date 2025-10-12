import os, time, hashlib, json, base64, getpass
from bindings.python.r4 import R4

user = getpass.getuser()
ts = int(time.time())
salt = os.urandom(16)

commit_msg = json.dumps({"who":user,"ts":ts,"salt":base64.b64encode(salt).decode()}, sort_keys=True)
commit = hashlib.sha256(commit_msg.encode()).hexdigest()
print("COMMIT:", commit)

r = R4()
rand = r.read(32)
r.close()

reveal = {"commit_msg": commit_msg, "rand_hex": rand.hex()}
print("REVEAL:", json.dumps(reveal))

check = hashlib.sha256(commit_msg.encode()).hexdigest()
assert check == commit, "commit mismatch"

ticket = hashlib.sha256(rand + commit_msg.encode()).hexdigest()
print("TICKET:", ticket)
