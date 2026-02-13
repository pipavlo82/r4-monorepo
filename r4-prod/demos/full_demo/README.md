# RE4CTOR Full Demo (local)

This script runs an end-to-end local demo:

core RNG (:8080)
-> signed randomness node (:8081)
-> Solidity verifier (Hardhat)
-> LotteryR4 sample

## Run
```bash
bash demos/full_demo/run_full_demo.sh
```

## Notes
- The script is designed to be noise-tolerant for optional probes.
- It does not embed any secrets.
