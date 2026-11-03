"""Integration test of analyze_e162's freezeA / freezeL / score paths on E149's committed logs dressed as E162 runs.
E149's features lack the row-lag keys, so rlag<r> := row and gtrR<r> := 0 here (synthetic; the numbers mean nothing).
Usage: python dryrun_e149_logs.py <scratch dir>, then analyze_e162.py reduce / freezeA / freezeL / score on its
fakeA1, fakeA2, fakeL1, fakeL2 folders (E162.md, "Selftest and desk runs"; the numbers it gives are not results)."""
import gzip
import json
import os
import shutil
import sys

E149 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "docs", "reports", "data",
                    "2026-11-02-e149-gpu-model-check", "logs")
out = sys.argv[1]


def ext(fe):
    fe = json.loads(json.dumps(fe))
    for k, v in fe.items():
        if "A" not in v:
            continue
        for side in ("A", "B"):
            for r in (1, 2, 4, 8, 16, 32):
                v[side][f"rlag{r}"] = list(v[side]["row"])
        for r in (1, 2, 4, 8, 16, 32):
            v["cross"][f"gtrR{r}"] = 0.0
    return fe


def jl(p):
    with gzip.open(p, "rt") as f:
        return json.load(f)


def jw(p, o):
    with gzip.open(p, "wt") as f:
        json.dump(o, f)


for run, new in (("e149-20261102-r1", "fakeA1"), ("e149-20261102-r2", "fakeA2"), ("e149-20261102-r1", "fakeL1"),
                 ("e149-20261102-r2", "fakeL2")):
    dst = os.path.join(out, new)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(E149, run), dst)
    for u in ("A", "B"):
        d = os.path.join(dst, u)
        p1 = os.path.join(d, "features-1.json.gz")
        f1 = ext(jl(p1)) if os.path.exists(p1) else {}
        f2 = ext(jl(os.path.join(d, "features-2.json.gz")))
        if new == "fakeA1":
            jw(os.path.join(d, "features-A1.json.gz"), f1)
            jw(os.path.join(d, "features-HA.json.gz"), f2)
            jw(os.path.join(d, "features-E149.json.gz"), dict(f1, **f2))
        elif new == "fakeL1":
            jw(os.path.join(d, "features-L1.json.gz"), {k: v for k, v in f1.items() if k.startswith("bf16.")})
            jw(os.path.join(d, "features-HL.json.gz"), {k: v for k, v in f2.items() if k.startswith("bf16.")})
        elif new == "fakeA2":
            jw(os.path.join(d, "features-A2.json.gz"), f2)
        else:
            jw(os.path.join(d, "features-L2.json.gz"), {k: v for k, v in f2.items() if k.startswith("bf16.")})
print("fake runs written")
