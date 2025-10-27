from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8082")

try:
    rand = client.get_random(16)
    print("🔐 Random bytes:", rand.hex())
except Exception as e:
    print("❌ Error:", e)
