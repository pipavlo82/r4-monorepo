from r4sdk import R4Client

# IMPORTANT: тут ставимо порт 8081 бо це PQ/Dilithium вузол
client = R4Client(api_key="demo", host="http://localhost:8081")

# 1. просто глянемо /version, щоб зрозуміти, що там за нода
import requests
try:
    v = requests.get("http://localhost:8081/version", timeout=3)
    print("8081 /version status:", v.status_code)
    print("8081 /version body:", v.text)
except Exception as e:
    print("⚠ cannot reach 8081 /version:", e)

# 2. спробуємо PQ-відповідь (дві опції, залежно як воно у тебе називається зараз)
for url in [
    "http://localhost:8081/random_pq?sig=dilithium&n=32",
    "http://localhost:8081/vrf?n=32&sig=dilithium",
]:
    try:
        r = requests.get(url, headers={"X-API-Key": "demo"}, timeout=3)
        print(f"try {url} -> {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"⚠ cannot reach {url}:", e)
