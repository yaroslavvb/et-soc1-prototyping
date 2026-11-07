#!/usr/bin/env python3
"""E184's checks, off-card (they read files, never the card).

    python3 -B tools/claims-v3/e184/check_e184.py harness [--binaries]
        every file the box runs, sources, builds from or reads equals harness-e184.json's sha256 (with --binaries also the box's E184
        build against build/enercat-e184/BUILD-E184.json, which build_e184.sh writes). "HARNESS OK: <n> files" or the faults; exit 1.
    python3 -B tools/claims-v3/e184/check_e184.py block <pass dir>
        the post-block check: every item's launches ok and at 600 MHz; arm S: every quad readable (e184_common.read_process); arm B:
        every burst and hold has its launches. Writes <pass dir>/check.json; prints "<status> <note>" (ok | partial | fail).
    python3 -B tools/claims-v3/e184/check_e184.py smoke <smoke pass dir>
        the smoke's gate. Arm S (p18401): all four quads readable; the null's contrast within +-0.15 W; n = 121 on 32 shires within
        0.70-1.30 W (the forecast 0.999 W); every minion switched within 7.6-9.3 W (E180's 8.455 W +- 10%); 16 shires n = 19 within
        0.05-0.30 W; every launch's instruction rate a hart within 3% of the smoke's median. Arm B (p18431): each of the three bursts
        has its launches, and the SRAM rail's PMIC average rose at least 0.5 W over the idle before it. "SMOKE GO" or "SMOKE NO-GO".
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def jl(path):
    for p, op in ((path + ".gz", gzip.open), (path, open)):
        if os.path.exists(p):
            out = []
            with op(p, "rt") as f:
                for line in f:
                    if line.startswith("{"):
                        try:
                            out.append(json.loads(line))
                        except ValueError:
                            pass
            return out
    return []


def harness(binaries):
    h = json.load(open(os.path.join(HERE, "harness-e184.json")))
    bad = []
    for rel, want in sorted(h["files"].items()):
        p = os.path.join(TOP, rel)
        if not os.path.exists(p):
            bad.append("missing " + rel)
        elif sha(p) != want:
            bad.append("changed " + rel)
    n = len(h["files"])
    if binaries:
        bj = os.path.join(TOP, "build", "enercat-e184", "BUILD-E184.json")
        if not os.path.exists(bj):
            bad.append("build/enercat-e184/BUILD-E184.json missing (run build_e184.sh)")
        else:
            b = json.load(open(bj))
            for rel, want in b["binaries"].items():
                p = os.path.join(TOP, rel)
                if not os.path.exists(p) or sha(p) != want:
                    bad.append("binary %s differs from BUILD-E184.json" % rel)
                n += 1
            if b.get("patched_main_sha256") != h["patched_main_sha256"]:
                bad.append("the build's host/main.cpp is not the pinned patched file")
    if bad:
        print("HARNESS FAULTS: " + "; ".join(bad[:12]) + (" (+%d)" % (len(bad) - 12) if len(bad) > 12 else ""))
        return 1
    print("HARNESS OK: %d files" % n)
    return 0


def quads(pdir):
    tel, runs = jl(os.path.join(pdir, "telemetry.jsonl")), jl(os.path.join(pdir, "runs.jsonl"))
    by = {}
    for r in runs:
        by.setdefault(r["seq"], []).append(r)
    out = []
    for seq, lns in sorted(by.items()):
        rd = c.read_process(tel, lns)
        y = base = None
        if rd["reason"] is None:
            y, base = c.quad_contrast(rd["blocks"])
        out.append({"seq": seq, "n": lns[0]["n"], "ref": lns[0]["ref"], "mask_m": lns[0]["mask_m"], "y": y, "base": base,
                    "reason": rd["reason"], "rate": [x["ops_per_cycle_per_hart"] for x in lns if x.get("ok")]})
    return out, tel, runs


def mhz_ok(tel):
    busy = [d["mhz"]["minion"] for d in tel if d.get("board_w", 0) > 28 and "mhz" in d]
    return (all(m == 600 for m in busy), len(busy))


def block(pdir):
    cfg = json.load(open(os.path.join(pdir, "configs.json")))
    items = cfg["items"]
    if cfg["arm"] == "arm_S":
        qs, tel, runs = quads(pdir)
        good = [q for q in qs if q["reason"] is None]
        m_ok, nb = mhz_ok(tel)
        st = "ok" if len(good) == len(items) and m_ok else ("partial" if good else "fail")
        note = "%d/%d quads readable; busy samples %d, all 600 MHz: %s" % (len(good), len(items), nb, m_ok)
        bad = [{"seq": q["seq"], "reason": q["reason"]} for q in qs if q["reason"]]
    else:
        runs = jl(os.path.join(pdir, "runs.jsonl"))
        tel = jl(os.path.join(pdir, "telemetry.jsonl"))
        need = [it for it in items if it["cfg"] != "idle"]
        have = set(r["seq"] for r in runs if r.get("ok"))
        m_ok, nb = mhz_ok(tel)
        miss = [it["seq"] for it in need if it["seq"] not in have]
        st = "ok" if not miss and m_ok else ("partial" if len(miss) < len(need) else "fail")
        note = "%d/%d loaded items have launches; busy samples %d, all 600 MHz: %s" % (len(need) - len(miss), len(need), nb, m_ok)
        bad = miss
    json.dump({"status": st, "note": note, "faults": bad}, open(os.path.join(pdir, "check.json"), "w"), indent=1)
    print("%s %s" % (st, note))
    return 0


def smoke(pdir):
    cfg = json.load(open(os.path.join(pdir, "configs.json")))
    why = []
    if cfg["arm"] == "arm_S":
        qs, tel, _ = quads(pdir)
        if len(qs) != 4 or any(q["reason"] for q in qs):
            why.append("not four readable quads: %s" % [q["reason"] for q in qs])
        else:
            bands = {(32, 0): (-0.15, 0.15), (32, 121): (0.70, 1.30), (32, 1024): (7.6, 9.3), (16, 19): (0.05, 0.30)}
            for q in qs:
                lo, hi = bands[(q["mask_m"], q["n"])]
                if not lo <= q["y"] <= hi:
                    why.append("m%d n%d read %.3f W, outside %.2f-%.2f" % (q["mask_m"], q["n"], q["y"], lo, hi))
            rates = [r for q in qs for r in q["rate"]]
            med = c.median(rates)
            if any(abs(r / med - 1) > 0.03 for r in rates):
                why.append("an instruction rate is more than 3% off the median %.4f" % med)
        m_ok, nb = mhz_ok(tel)
        if not m_ok:
            why.append("a busy sample off 600 MHz")
    else:
        runs, tel = jl(os.path.join(pdir, "runs.jsonl")), jl(os.path.join(pdir, "telemetry.jsonl"))
        for it in cfg["items"]:
            lns = [r for r in runs if r["seq"] == it["seq"] and r.get("ok")]
            if not lns:
                why.append("item %d has no launch" % it["seq"])
                continue
            t0, t1 = min(r["t_start_ms"] for r in lns), max(r["t_end_ms"] for r in lns)
            pre = [d["sp"]["sram_w"][0] for d in tel if t0 - 2500 <= d["t_ms"] <= t0 - 200]
            busy = [d["sp"]["sram_w"][0] for d in tel if t1 - 700 <= d["t_ms"] <= t1]
            if not pre or not busy or c.fmean(busy) - c.fmean(pre) < 0.5:
                why.append("item %d (%s): the SRAM rail did not rise 0.5 W" % (it["seq"], it["cfg"]))
    if why:
        print("SMOKE NO-GO: " + "; ".join(why))
        return 1
    print("SMOKE GO")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["harness", "block", "smoke"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--binaries", action="store_true")
    a = ap.parse_args()
    if a.cmd == "harness":
        sys.exit(harness(a.binaries))
    if a.cmd == "block":
        sys.exit(block(a.dir))
    sys.exit(smoke(a.dir))


if __name__ == "__main__":
    main()
