#!/usr/bin/env python3
"""DV2 validation: may a frozen NAT replication session start now? (dv2v/block.sh VN passes; PREREG-VAL section 5)

    vn_check.py <val.json> <dv2v data dir> <now ms>   ->   "<ok 0|1> <next pass 6051-6099> <why>"

It reads files only: the newest VZ cycle (p9101-p9499 z1.json) must be <= 15 min old and read <= val.json
nat.nat_cool_max; fewer than vn_sessions_max sessions (p6050-p6099 session.json, launched) and fewer than
vn_blocks_needed complete G4 blocks (an INT16 and a PER16 T-run of one block at S = nat.g4_S) may exist.
"""
import glob
import json
import os
import sys


def lj(f):
    try:
        return json.load(open(f))
    except Exception:
        return None


def check(vj, val, now):
    V = json.load(open(vj))
    nat = V.get("nat") or {}
    zs = [z for z in (lj(f) for f in glob.glob(os.path.join(val, "p9[1-4][0-9][0-9]", "z1.json"))) if z and z.get("t_ms")]
    zs.sort(key=lambda z: z["t_ms"])
    sess = [x for x in (lj(f) for f in glob.glob(os.path.join(val, "p60[5-9][0-9]", "session.json"))) if x]
    launched = [x for x in sess if x.get("launched")]
    used = sorted(int(os.path.basename(d)[1:]) for d in glob.glob(os.path.join(val, "p60[5-9][0-9]")))
    nxt = (used[-1] + 1) if used else 6051
    blocks = 0
    for d in glob.glob(os.path.join(val, "p60[5-9][0-9]")):
        runs = []
        try:
            runs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl")) if l.startswith("{")]
        except Exception:
            pass
        by = {}
        for r in runs:
            if r.get("kind") == "T" and r.get("S") == nat.get("g4_S") and (r.get("name") or "")[:5] in ("INT16", "PER16"):
                by.setdefault(r.get("block"), set()).add(r["name"][:5])
        blocks += sum(1 for b in by.values() if len(b) == 2)
    if not zs:
        return 0, nxt, "no VZ reading yet"
    z = zs[-1]
    if now - z["t_ms"] > 900e3:
        return 0, nxt, "the newest VZ reading is %.0f min old" % ((now - z["t_ms"]) / 60e3)
    cmax = int(nat.get("nat_cool_max", 60))
    if z.get("reading_c") is None or z["reading_c"] > cmax:
        return 0, nxt, "the newest VZ reading is %s (> %s)" % (z.get("reading_c"), cmax)
    if len(launched) >= int(V.get("vn_sessions_max", 3)):
        return 0, nxt, "%d validation NAT sessions launched (max %s)" % (len(launched), V.get("vn_sessions_max", 3))
    if blocks >= int(V.get("vn_blocks_needed", 16)):
        return 0, nxt, "%d complete G4 blocks (needed %s)" % (blocks, V.get("vn_blocks_needed"))
    if nxt > 6099:
        return 0, nxt, "no validation NAT pass number left"
    return 1, nxt, "VZ p%s read %s C; %d sessions launched, %d complete G4 blocks" % (z.get("pass"), z.get("reading_c"), len(launched), blocks)


if __name__ == "__main__":
    ok, nxt, why = check(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    print(ok, nxt, why)
