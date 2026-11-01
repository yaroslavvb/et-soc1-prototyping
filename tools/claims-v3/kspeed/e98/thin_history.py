#!/usr/bin/env python3
"""E98: one box's 5 s history over [from, to) epoch s, keeping the numbers and nothing else: t, cpu, mem, load, temps, cards[n, ok, held (a bool), die, max, w].

    python3 thin_history.py <file> <from s> <to s>
"""
import json
import sys

a, b = int(sys.argv[2]) * 1000, int(sys.argv[3]) * 1000
for ln in open(sys.argv[1]):
    try:
        r = json.loads(ln)
    except ValueError:
        continue
    t = r.get("t", 0)
    if not a <= t < b:
        continue
    out = {k: r.get(k) for k in ("t", "cpu", "mem", "load")}
    out["temps"] = {k: v for k, v in (r.get("temps") or {}).items() if isinstance(v, (int, float))}
    out["cards"] = [{"n": c.get("n"), "ok": c.get("ok"), "held": bool(c.get("held")), "die": c.get("die"), "max": c.get("max"), "w": c.get("w")} for c in (r.get("cards") or [])]
    print(json.dumps(out, separators=(",", ":")))
