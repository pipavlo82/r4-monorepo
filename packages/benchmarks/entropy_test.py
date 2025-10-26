#!/usr/bin/env python3
# 🧠 quick entropy estimate
import math,collections
data=open("sample.bin","rb").read()
freq=collections.Counter(data)
H=-sum((c/len(data))*math.log2(c/len(data)) for c in freq.values())
print(f"Entropy ≈ {H:.4f} bits/byte (ideal=8.0)")
