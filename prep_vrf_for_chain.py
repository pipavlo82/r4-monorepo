#!/usr/bin/env python3
import base64
import json
import hashlib
import requests

from eth_utils import keccak, to_checksum_address

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# This script:
# 1. Calls the local R4PQ node (/random_pq?sig=ecdsa)
# 2. Extracts random, timestamp, sig_b64, pubkey_b64
# 3. Parses the PEM public key, derives Ethereum-style address
# 4. Splits signature into r,s and brute-forces v (27/28) that matches signer
#
# Output: ready-to-use (randomNumber, timestampIso, v, r, s, signerAddr)
# for the Solidity verifier.

PQ_URL = "http://localhost:8081/random_pq?sig=ecdsa"

def load_sample():
    r = requests.get(PQ_URL, timeout=5)
    r.raise_for_status()
    data = r.json()
    return data

def sha256_bytes(b: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(b)
    return h.digest()

def pem_to_eth_address(pem_bytes: bytes) -> str:
    """
    pubkey_b64 in the API is actually a base64 of the full PEM text:
    -----BEGIN PUBLIC KEY-----
    ...
    -----END PUBLIC KEY-----

    We decode base64 -> PEM text (bytes with BEGIN/END).
    Then we parse the PEM, get the EC point (X,Y), and convert to an Ethereum-style address.
    """
    pub = load_pem_public_key(pem_bytes)

    # Expect EC public key on secp256k1
    public_numbers = pub.public_numbers()
    x = public_numbers.x
    y = public_numbers.y

    # Build uncompressed SEC1 form: 0x04 || X || Y
    x_bytes = x.to_bytes(32, "big")
    y_bytes = y.to_bytes(32, "big")
    uncompressed = b"\x04" + x_bytes + y_bytes  # 65 bytes

    # Ethereum address = last 20 bytes of keccak(pubkey[1:])
    eth_addr_bytes = keccak(uncompressed[1:])[-20:]
    return to_checksum_address("0x" + eth_addr_bytes.hex())

def recover_v(random_int, timestamp_iso, r_bytes32, s_bytes32, want_addr):
    """
    Brute-force recid in {0,1} using secp256k1 public key recovery (coincurve).
    Return solidity-compatible v = recid + 27, plus the msg_hash.
    """
    from coincurve import PublicKey

    # Solidity msg preimage:
    # sha256( abi.encodePacked(uint256, string) )
    random_be = random_int.to_bytes(32, "big")
    msg_preimage = random_be + timestamp_iso.encode("utf-8")
    msg_hash = sha256_bytes(msg_preimage)

    sig_no_v = r_bytes32 + s_bytes32  # 64 bytes

    for recid in (0, 1):
        # coincurve wants signature = 64-byte rs + 1-byte recid
        sig_65 = sig_no_v + bytes([recid])

        try:
            pubkey_obj = PublicKey.from_signature_and_message(
                sig_65,
                msg_hash,
                hasher=None  # we already gave raw sha256(message)
            )
        except Exception:
            continue

        # uncompressed SEC1 point (65 bytes, 0x04 || X || Y)
        uncompressed = pubkey_obj.format(compressed=False)

        # derive eth-style address
        addr = to_checksum_address("0x" + keccak(uncompressed[1:])[-20:].hex())

        if addr == want_addr:
            solidity_v = recid + 27  # what Solidity ecrecover expects
            return solidity_v, msg_hash.hex()

    raise RuntimeError("could not match v using recid=0/1 vs signer address")

def main():
    data = load_sample()
    print("Raw response from node:")
    print(json.dumps(data, indent=2))

    random_int = int(data["random"])
    timestamp_iso = data["timestamp"]
    sig_b64 = data["sig_b64"]
    pubkey_b64 = data["pubkey_b64"]

    # 1. Decode signature
    sig_raw = base64.b64decode(sig_b64)

    if len(sig_raw) < 64:
        raise ValueError(f"sig too short: {len(sig_raw)} bytes")
    r_bytes32 = sig_raw[0:32]
    s_bytes32 = sig_raw[32:64]

    # 2. Decode pubkey (PEM stored as base64 string)
    pem_bytes = base64.b64decode(pubkey_b64)

    # 3. Derive Ethereum-style address for this signer
    signer_addr = pem_to_eth_address(pem_bytes)
    print(f"\n[*] Derived signer Ethereum-style address: {signer_addr}")

    # 4. Figure out 'v' that recovers signer_addr
    v, msg_hash_hex = recover_v(random_int, timestamp_iso, r_bytes32, s_bytes32, signer_addr)
    print(f"[*] Chosen v = {v}")
    print(f"[*] sha256(message) = 0x{msg_hash_hex}")

    # 5. Print Solidity input payload
    print("\n=== Solidity inputs ===")
    print(f"R4_SIGNER_ADDRESS (constructor arg): {signer_addr}")
    print(f"randomNumber (uint256): {random_int}")
    print(f'timestampIso (string): "{timestamp_iso}"')
    print(f"v (uint8): {v}")
    print(f"r (bytes32): 0x{r_bytes32.hex()}")
    print(f"s (bytes32): 0x{s_bytes32.hex()}")

    print("\nUse these with:")
    print("  R4VRFVerifier vrf = new R4VRFVerifier(R4_SIGNER_ADDRESS);")
    print("  bool ok = vrf.verify(randomNumber, timestampIso, v, r, s);")
    print("  // ok should be true")

if __name__ == "__main__":
    main()
