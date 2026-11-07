#!/usr/bin/env python3
"""E184's checks, v2 (kit note 1, KIT.md.dated-note-1.md sections 1 and 5), off-card (they read files, never the card). check_e184.py
(v1, which stays as committed) with three changes, and its helpers imported unchanged:

    python3 -B tools/claims-v3/e184/check_e184_v2.py harness [--binaries]
        v1's check against harness-e184-v2.json (kit v2's box files) in place of harness-e184.json. "HARNESS OK: <n> files" or the faults.
    python3 -B tools/claims-v3/e184/check_e184_v2.py block <pass dir>
        the post-block check, with v2's status: "fail" when any busy sample is off 600 MHz (v1 called that "partial"), "partial" when the
        clock held and at least half the pass's items are readable but not all (arm S: quads e184_common.read_process reads; arm B:
        loaded items with launches), "ok" when all are, else "fail". Writes <pass dir>/check.json (status, note, faults, mhz_ok,
        busy_samples, readable, items); prints "<status> <note>". block_e184{s,b}_v2.sh exit 7 on "partial", and queue_e184_v2.sh goes on.
    python3 -B tools/claims-v3/e184/check_e184_v2.py smoke <smoke pass dir>
        the smoke's gate, v1's, but the 16-shire n = 19 quad is a gross check only: -0.15 to +0.30 W (v1: 0.05-0.30 W, a band that read
        E184-P's registered alternative, small steps at E178's 0.29 of their size at that operating point, as a NO-GO with chance 0.57:
        the verifier's fault 1; power-e184-a2.json > K). The 32-shire bands, the readable-quads test, the instruction-rate test, the
        600 MHz test and arm B's gate are v1's.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402
import check_e184 as v1  # noqa: E402

HARNESS = "harness-e184-v2.json"
SMOKE_BANDS_S = {(32, 0): (-0.15, 0.15), (32, 121): (0.70, 1.30), (32, 1024): (7.6, 9.3), (16, 19): (-0.15, 0.30)}


def harness(binaries):
    h = json.load(open(os.path.join(HERE, HARNESS)))
    bad = []
    for rel, want in sorted(h["files"].items()):
        p = os.path.join(TOP, rel)
        if not os.path.exists(p):
            bad.append("missing " + rel)
        elif v1.sha(p) != want:
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
                if not os.path.exists(p) or v1.sha(p) != want:
                    bad.append("binary %s differs from BUILD-E184.json" % rel)
                n += 1
            if b.get("patched_main_sha256") != h["patched_main_sha256"]:
                bad.append("the build's host/main.cpp is not the pinned patched file")
    if bad:
        print("HARNESS FAULTS: " + "; ".join(bad[:12]) + (" (+%d)" % (len(bad) - 12) if len(bad) > 12 else ""))
        return 1
    print("HARNESS OK: %d files (%s)" % (n, HARNESS))
    return 0


def status_of(readable, total, m_ok):
    if not m_ok:
        return "fail"
    if readable == total and total > 0:
        return "ok"
    if total > 0 and 2 * readable >= total:
        return "partial"
    return "fail"


def block(pdir):
    cfg = json.load(open(os.path.join(pdir, "configs.json")))
    items = cfg["items"]
    if cfg["arm"] == "arm_S":
        qs, tel, runs = v1.quads(pdir)
        good = [q for q in qs if q["reason"] is None]
        m_ok, nb = v1.mhz_ok(tel)
        readable, total = len(good), len(items)
        bad = [{"seq": q["seq"], "reason": q["reason"]} for q in qs if q["reason"]]
        what = "quads readable"
    else:
        runs = v1.jl(os.path.join(pdir, "runs.jsonl"))
        tel = v1.jl(os.path.join(pdir, "telemetry.jsonl"))
        need = [it for it in items if it["cfg"] != "idle"]
        have = set(r["seq"] for r in runs if r.get("ok"))
        m_ok, nb = v1.mhz_ok(tel)
        miss = [it["seq"] for it in need if it["seq"] not in have]
        readable, total = len(need) - len(miss), len(need)
        bad = miss
        what = "loaded items have launches"
    st = status_of(readable, total, m_ok)
    note = "%d/%d %s; busy samples %d, all 600 MHz: %s" % (readable, total, what, nb, m_ok)
    if not m_ok:
        note = "a busy sample off 600 MHz (v2: fail); " + note
    json.dump({"status": st, "note": note, "faults": bad, "mhz_ok": m_ok, "busy_samples": nb, "readable": readable, "items": total,
               "check": "check_e184_v2.py"}, open(os.path.join(pdir, "check.json"), "w"), indent=1)
    print("%s %s" % (st, note))
    return 0


def smoke(pdir):
    cfg = json.load(open(os.path.join(pdir, "configs.json")))
    why = []
    if cfg["arm"] == "arm_S":
        qs, tel, _ = v1.quads(pdir)
        if len(qs) != 4 or any(q["reason"] for q in qs):
            why.append("not four readable quads: %s" % [q["reason"] for q in qs])
        else:
            for q in qs:
                lo, hi = SMOKE_BANDS_S[(q["mask_m"], q["n"])]
                if not lo <= q["y"] <= hi:
                    why.append("m%d n%d read %.3f W, outside %.2f-%.2f" % (q["mask_m"], q["n"], q["y"], lo, hi))
            rates = [r for q in qs for r in q["rate"]]
            med = c.median(rates)
            if any(abs(r / med - 1) > 0.03 for r in rates):
                why.append("an instruction rate is more than 3% off the median %.4f" % med)
        m_ok, nb = v1.mhz_ok(tel)
        if not m_ok:
            why.append("a busy sample off 600 MHz")
    else:
        return v1.smoke(pdir)
    if why:
        print("SMOKE NO-GO: " + "; ".join(why))
        return 1
    print("SMOKE GO (check_e184_v2.py: the 16-shire n = 19 quad a gross check, -0.15 to +0.30 W)")
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
