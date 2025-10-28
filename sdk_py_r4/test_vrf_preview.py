from r4sdk import R4Client

# приклад: PQ-нода на 8081 або 8082
client = R4Client(api_key="demo", host="http://localhost:8082")

try:
    vrf = client.get_vrf(
        length=32,
        sig_type="dilithium",
        endpoint="/random_pq",  # якщо бекенд називається інакше, міняєш тут
    )
    print("✅ VRF response:")
    print(vrf)

    print("Local verify (stub):", client.verify_vrf_locally(vrf))
except Exception as e:
    print("❌ VRF request failed:", e)

# а от класичний random:
rnd = client.get_random(16)
print("classic /random bytes:", rnd.hex())
