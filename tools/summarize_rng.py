#!/usr/bin/env python3
import sys, re, json
text = sys.stdin.read()
out = {}
pvals = re.findall(r"\bp\s*=\s*([0-9\.eE+-]+)", text)
if pvals: out["p_values_tail"] = pvals[-10:]
flags = re.findall(r"\b(FAIL|weak)\b", text, re.I)
out["flags"] = len(flags)
print(json.dumps(out, indent=2))
