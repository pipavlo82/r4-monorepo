from r4sdk import R4Client

def main():
    # 8081 = PQ / Dilithium / Kyber node
    pq = R4Client(api_key="demo", host="http://localhost:8081")

    print("== /version on 8081 ==")
    try:
        print(pq.get_version())
    except Exception as e:
        print("⚠ get_version() failed:", e)

    print("\n== /random_pq sig=dilithium ==")
    vrf_dil = pq.get_vrf(length=32, sig_type="dilithium")
    print(vrf_dil)

    print("\n== /random_pq sig=ecdsa ==")
    vrf_ecdsa = pq.get_vrf(length=32, sig_type="ecdsa")
    print(vrf_ecdsa)

    # classic entropy from 8080 just to show contrast
    core = R4Client(api_key="demo", host="http://localhost:8080")
    rb = core.get_random(16, fmt="hex")
    print("\n== classic /random on 8080 ==")
    print("classic_random(hex->bytes):", rb.hex())

if __name__ == "__main__":
    main()
