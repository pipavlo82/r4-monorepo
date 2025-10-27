from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8082")
rnd = client.get_random(16)
print(f"🔐 Test OK, got {len(rnd)} bytes: {rnd.hex()}")

