# 🐍 R4 Python SDK

Official Python client for the R4 entropy appliance and randomness API.

## 🚀 Quickstart

Install dependencies:

```bash
pip install -r requirements.txt
Run the test script:

bash
Copy code
python3 test_r4sdk.py
Example output:

bash
Copy code
🔐 Random bytes: 9fa48bd3a213e7f14922ff...
🧩 File Structure
r4sdk/client.py — HTTP client (R4Client)

test_r4sdk.py — test/demo script

setup.py — installable Python package config

📦 Local Install
Install the SDK in editable mode:

bash
Copy code
pip install -e ./sdk_py_r4
Then use in your code:

python
Copy code
from r4sdk import R4Client

client = R4Client(api_key="demo")
rnd = client.get_random(length=32)
print(rnd.hex())
🛠️ Configuration
You can change the default host:

python
Copy code
R4Client(api_key="demo", host="http://localhost:8082")
MIT License • (c) 2025 Re4ctoR RNG Labs
