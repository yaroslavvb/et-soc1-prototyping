#!/usr/bin/env python3
"""scout-q146: the noise of a paired difference between two kinds measured in the same session and card, from committed
600 MHz kinds sessions (post hoc reading of committed reductions; no fit, no card).

For every session file (Q139(u)'s footing reductions E78-E142, and the pool sessions' own reductions E153, E157, E163, E164,
E171, E172), every pair of items of one type that share >= 3 passes: per pass d = D1 - D2, then sd over passes.
Null pairs: two items whose operand bytes are identical (by sha256 of the 2,048 bytes; the host's built-in pi has the bytes of
tiles/fp32/pi.bin, checked here). Writes JSON to stdout.
"""
import glob
import hashlib
import json
import math
import os
import statistics
import sys

ROOT = sys.argv[1]
DD = os.path.join(ROOT, "docs", "reports", "data")
KD = os.path.join(ROOT, "tools", "claims-v3", "kinds")
load = lambda p: json.load(open(p))  # noqa: E731
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731

SESS = {}
for p in sorted(glob.glob(os.path.join(DD, "2026-11-03-q139u-footing", "reduced", "e*-footing.json"))):
    SESS[os.path.basename(p).split("-")[0].upper()] = p
OWN = {"E153": "2026-11-03-e153-blind6-aifoundry3/e153.json", "E157": "2026-11-03-e157-blind6-card1/e157.json",
       "E163": "2026-11-04-e163-blind7-aifoundry3/e163.json", "E164": "2026-11-04-e164-blind7-card1/e164.json",
       "E171": "2026-11-05-e171-blind8-aifoundry3/e171.json", "E172": "2026-11-05-e172-blind8-card1/e172.json"}
for k, v in OWN.items():
    SESS[k] = os.path.join(DD, v)

# sha per (exp, key)
shamap = {}
for r in load(os.path.join(DD, "2026-11-04-q140m-m9", "rows-m9.json")):
    shamap[(r["exp"], r["key"])] = r["tile_sha256"]
for pool, exps in (("blind6", ("E153", "E157")), ("blind7", ("E163", "E164")), ("blind8", ("E171", "E172"))):
    man = load(os.path.join(KD, pool, pool + ".json"))
    for meta in man["tiles"]:
        p = os.path.join(KD, pool, meta["file"])
        if os.path.exists(p):
            for e in exps:
                shamap[(e, meta["name"])] = sha(p)
kt = {}
for t in ("fp32", "fp16", "int8"):
    for p in glob.glob(os.path.join(KD, "tiles", t, "*.bin")):
        kt[f"{t}.{os.path.basename(p)[:-4]}"] = sha(p)
pi_tile = os.path.join(KD, "tiles", "fp32", "pi.bin")
raw = open(pi_tile, "rb").read()
pi_ok = raw == bytes.fromhex("db0f4940") * 512
PI_SHA = sha(pi_tile)

out = {"pi_builtin_equals_tiles_fp32_pi": pi_ok, "sessions": {}, "null_pairs": [], "named_pairs": [], "summary": {}}
NAMED = [("anchor_pi", "fp32.pi"), ("anchor_pi", "fp32.ones"), ("fp32.ones", "fp32.pi"), ("fp32.ones", "fp32.neg_ones"),
         ("fp16.ones", "fp16.neg_ones"), ("int8.ones", "int8.neg_ones"), ("fp32.nz_both", "fp32.dn1_both"),
         ("fp16.nz_both", "fp16.ones")]
all_sd = {"fp32": [], "fp16": [], "int8": []}
for exp, path in SESS.items():
    if not os.path.exists(path):
        continue
    d = load(path)
    items, pp = d["items"], d.get("per_pass") or {}
    passes = sorted(pp)
    out["sessions"][exp] = {"card": d.get("card"), "passes": len(passes), "clock_mhz": d.get("clock_mhz")}

    def sh(key):
        if key == "anchor_pi":
            return PI_SHA if pi_ok else None
        return shamap.get((exp, key)) or kt.get(key)

    keys = [k for k in items if isinstance(items[k].get("D"), dict) and items[k]["D"].get("mean") is not None]
    by_type = {}
    for k in keys:
        by_type.setdefault(items[k]["type"], []).append(k)

    def pair(k1, k2):
        ds = [pp[p][k1]["D"] - pp[p][k2]["D"] for p in passes if k1 in pp[p] and k2 in pp[p]
              and pp[p][k1].get("D") is not None and pp[p][k2].get("D") is not None]
        if len(ds) < 3:
            return None
        m, s = statistics.mean(ds), statistics.stdev(ds)
        se1, se2 = items[k1]["D"].get("se") or 0.0, items[k2]["D"].get("se") or 0.0
        return {"n": len(ds), "mean": m, "sd_pass": s, "se_paired": s / math.sqrt(len(ds)),
                "se_unpaired": math.sqrt(se1 ** 2 + se2 ** 2), "D1": items[k1]["D"]["mean"], "D2": items[k2]["D"]["mean"]}

    for t, ks in by_type.items():
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                r = pair(ks[i], ks[j])
                if r is None:
                    continue
                all_sd[t].append(r["sd_pass"])
                s1, s2 = sh(ks[i]), sh(ks[j])
                if s1 and s1 == s2:
                    out["null_pairs"].append({"exp": exp, "card": d.get("card"), "k1": ks[i], "k2": ks[j], **r})
    for k1, k2 in NAMED:
        if k1 in items and k2 in items:
            r = pair(k1, k2)
            if r:
                out["named_pairs"].append({"exp": exp, "card": d.get("card"), "k1": k1, "k2": k2, **r})
for t, v in all_sd.items():
    if v:
        v = sorted(v)
        out["summary"][t] = {"pairs": len(v), "sd_pass_median": statistics.median(v), "sd_pass_p10": v[len(v) // 10],
                             "sd_pass_p90": v[(9 * len(v)) // 10]}
json.dump(out, sys.stdout, indent=1)
