from bindings.python.r4 import R4
r = R4()
data = r.read(100000)
print("bytes:", len(data))
r.close()
