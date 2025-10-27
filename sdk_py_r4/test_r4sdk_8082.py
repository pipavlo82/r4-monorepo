from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8082")
random_bytes = client.get_random(16)
print("🔐 Random from 8082:", random_bytes.hex())
