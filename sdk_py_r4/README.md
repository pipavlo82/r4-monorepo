# r4sdk

**r4sdk** is a lightweight Python client for the [Re4ctoR](https://github.com/pipavlo82/r4-monorepo) high-entropy randomness API.

Supports secure random byte fetching via HTTP with API Key authentication.  
Ideal for cryptographic, simulation, and research use.

---

## 🚀 Features

- 🔒 API key authentication
- ⚡ Fast local access (`localhost` by default)
- 📦 Clean Python interface

---

## 📦 Installation

Install from PyPI:

```bash
pip install r4sdk
Or install locally:

pip install .
🧪 Usage
from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8082")
print(client.get_random(16).hex())
🔧 CLI Quick Test
echo 'from r4sdk import R4Client; c=R4Client(api_key="demo", host="http://localhost:8082"); print(c.get_random(16).hex())' | python3

📁 Files
r4sdk/__init__.py — core SDK client

test_sdk.py — standalone test

setup.py — packaging

🛡 License
MIT © Pavlo Tvardovskyi

