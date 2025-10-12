#!/usr/bin/env python3
import sys, re, json
text = sys.stdin.read()
out = {}
out["p_values_tail"] = re.findall(r"\bp\s*=\s*([0-9\.eE+-]+)", text)[-10:]
out["flags"] = len(re.findall(r"\b(FAIL|weak)\b", text, re.I))
print(json.dumps(out, indent=2))
