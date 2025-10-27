from r4sdk import R4Client

client = R4Client(api_key="demo", base_url="http://localhost:8080")
print(client.random_hex(32))
