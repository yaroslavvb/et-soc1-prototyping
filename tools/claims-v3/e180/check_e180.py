#!/usr/bin/env python3
"""E180's checks, off-card (they read files, never the card).

    python3 tools/claims-v3/e180/check_e180.py harness [--binaries]
        every file the box runs equals harness-e180.json's sha256 (the box's E180 build too with --binaries, against
        build/enercat-e180/BUILD-E180.json, which build_e180.sh writes); every image equals kinds-e180.json's sha256;
        cfgs-e180.json and plan-e180.json are the registration's. Prints "HARNESS OK: <n> files" or the faults; exit 1 on any.
    python3 tools/claims-v3/e180/check_e180.py block <pass dir> --card <id> --root <tree>
        the post-block check (V3-CATFULL's cflib.py check form): workloads/enercat/analyze_catalogue.py's bursts_of on the
        pass; writes <pass dir>/check.json and prints "<status> <note>" (ok | partial | fail).
    python3 tools/claims-v3/e180/check_e180.py smoke <smoke pass dir> --root <tree>
        the smoke's gate: every smoke configuration has its launches and a kept burst, the busy clock read 600 MHz, and
        every burst's instruction rate is within 3% of the others' (the loop's timing must not depend on the number);
        prints "SMOKE GO" or "SMOKE NO-GO: <why>"; exit 1 on NO-GO.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import importlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXPECTED_BURST_LAUNCHES = (6, 7, 8)     # a 3 s burst of 0.4 s launches (the catalogue's: 8 at --gap 4.5, 7 when slow)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        return [json.loads(l) for l in open(path) if l.startswith("{")]
    return []


def harness(binaries):
    h = json.load(open(os.path.join(HERE, "harness-e180.json")))
    bad = []
    for rel, want in sorted(h["files"].items()):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            bad.append(f"missing {rel}")
        elif sha(p) != want:
            bad.append(f"changed {rel}")
    kinds = json.load(open(os.path.join(HERE, "kinds-e180.json")))
    for rel, want in kinds["images"].items():
        p = os.path.join(HERE, rel)
        if not os.path.exists(p) or sha(p) != want:
            bad.append(f"image {rel} differs from kinds-e180.json")
    n = len(h["files"]) + len(kinds["images"])
    if binaries:
        bj = os.path.join(ROOT, "build", "enercat-e180", "BUILD-E180.json")
        if not os.path.exists(bj):
            bad.append("build/enercat-e180/BUILD-E180.json missing (run build_e180.sh)")
        else:
            b = json.load(open(bj))
            for rel, want in b["binaries"].items():
                p = os.path.join(ROOT, rel)
                if not os.path.exists(p) or sha(p) != want:
                    bad.append(f"binary {rel} differs from BUILD-E180.json")
                n += 1
            if b.get("acc_modes_inc_sha256") != h["acc_modes_inc_sha256"]:
                bad.append("the build's appended modes differ from acc-modes-e180.inc")
    if bad:
        print("HARNESS FAULTS: " + "; ".join(bad[:12]) + (f" (+{len(bad) - 12})" if len(bad) > 12 else ""))
        return 1
    print(f"HARNESS OK: {n} files")
    return 0


def analyzer(root):
    sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
    try:
        return importlib.import_module("analyze_catalogue")
    finally:
        sys.path.pop(0)


def bursts(d, root):
    tel, runs = jl(os.path.join(d, "telemetry.jsonl")), jl(os.path.join(d, "runs.jsonl"))
    cfgs = (json.load(open(os.path.join(d, "configs.json"))) if os.path.exists(os.path.join(d, "configs.json")) else {}).get("cfgs", [])
    if len(tel) < 50 or not runs:
        return [], runs, tel, cfgs
    res = analyzer(root).bursts_of(tel, runs)
    return (res[0] if isinstance(res, tuple) else res), runs, tel, cfgs


def block(d, card, root):
    bl, runs, tel, cfgs = bursts(d, root)
    expected = [c["cfg"] for c in cfgs]
    have = {r["cfg"] for r in runs}
    missing = [c for c in expected if c not in have]
    cut = {b["cfg"] for b in bl}
    uncut = [c for c in expected if c in have and c not in cut]
    off = [b["cfg"] for b in bl if not b["mhz_busy_all_600"]]
    launches = {c: sum(1 for r in runs if r["cfg"] == c) for c in expected}
    short = [c for c, n in launches.items() if c in have and n not in EXPECTED_BURST_LAUNCHES]
    res = {"card": card, "expected": len(expected), "with_launches": len(have), "missing": missing, "uncut": uncut,
           "off_600": off, "launch_counts": launches, "short_bursts": short, "n_tel": len(tel), "n_runs": len(runs),
           "die_c_busy_max": max((b["die_c_busy"] for b in bl), default=None),
           "board_w_max": max((s["board_w"] for s in tel), default=None)}
    if len(tel) < 50 or not runs or len(missing) > len(expected) // 2:
        st, note = "fail", f"no data (telemetry lines {len(tel)}, launches {len(runs)}, {len(missing)} of {len(expected)} without one)"
    elif missing or uncut or off:
        st, note = "partial", (f"{len(missing)} without a launch, {len(uncut)} not cut by bursts_of, {len(off)} off 600 MHz: "
                               f"{','.join((missing + uncut + off)[:6])}")
    else:
        st, note = "ok", f"{len(bl)}/{len(expected)} bursts, die {res['die_c_busy_max']:.1f} C at most, board {res['board_w_max']:.2f} W at most"
    res.update({"status": st, "note": note})
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    print(f"{st} {note}")
    return 0


def smoke(d, root):
    bl, runs, tel, cfgs = bursts(d, root)
    expected = [c["cfg"] for c in cfgs]
    why = []
    have = {r["cfg"] for r in runs}
    cut = {b["cfg"]: b for b in bl}
    for c in expected:
        if c not in have:
            why.append(f"{c}: no launch")
        elif c not in cut:
            why.append(f"{c}: not cut by bursts_of")
        elif not cut[c]["mhz_busy_all_600"]:
            why.append(f"{c}: off 600 MHz")
    rates = [cut[c]["ops_per_s"] for c in expected if c in cut]
    if rates and (max(rates) - min(rates)) / max(rates) > 0.03:
        why.append(f"instruction rates differ by {(max(rates) - min(rates)) / max(rates):.1%} (the loop's timing must not depend on the number)")
    if why:
        print("SMOKE NO-GO: " + "; ".join(why))
        return 1
    print(f"SMOKE GO: {len(expected)} configurations, rates {min(rates):.4e}-{max(rates):.4e} a second")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["harness", "block", "smoke"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--card")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--binaries", action="store_true")
    a = ap.parse_args()
    if a.cmd == "harness":
        sys.exit(harness(a.binaries))
    if a.cmd == "block":
        sys.exit(block(a.dir, a.card, a.root))
    sys.exit(smoke(a.dir, a.root))


if __name__ == "__main__":
    main()
