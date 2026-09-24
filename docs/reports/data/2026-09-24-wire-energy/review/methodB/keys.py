import json,sys,numpy as np
H=("aifoundry2","aifoundry3")
def keys(fn):
    R=json.load(open(fn)); k={}
    for st in ("v1","v2"):
        for m in ("noc","board","board_tc"):
            M=R[f"model|{st}|{m}"]
            for q in ("a","b","rms","rand","s0"):
                k[f"{st} {m} {q}"]=np.mean([M[h][q] for h in H])
            if st=="v2":
                for q in ("comp_34_14","comp_1_0"): k[f"{st} {m} {q}"]=np.mean([M[h][q] for h in H])
    for m in ("noc","board","board_tc"):
        for lab in ("wsep d1-5","wu d1-4"):
            r=R[f"sep|{m}|{lab}"]
            for q in ("data_paired","zeros"):
                k[f"{m} {lab} {q}"]=np.mean([r[h][q] for h in H])
    return k
fs=sys.argv[1:]
K=[keys(f) for f in fs]
print(f"{'quantity':32s}"+"".join(f"{f[10:-5]:>14s}" for f in fs))
for q in K[0]:
    print(f"{q:32s}"+"".join(f"{k[q]:14.3f}" for k in K))
