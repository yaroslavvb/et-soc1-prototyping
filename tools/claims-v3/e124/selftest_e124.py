#!/usr/bin/env python3
"""E124 (Q134) self-test, on the Intel before the freeze: E124's pipeline on E109's own committed data (aifoundry3), where the answers are known.

    python3 tools/claims-v3/e124/selftest_e124.py [--full]          # writes tools/claims-v3/e124/selftest.txt

  A. check_e124.py: every reused file matches predictions-e124.json.
  B. score_e109.py (unchanged) with predictions-e124.json on E109's committed e109-3pass.json reproduces E109's committed scored-3pass.json in every rule
     but R10 (whose references are card 1's here) - so the frozen file E124 hands the scorer changes nothing but the tie.
  C. extras_e124.py on E109's e109.json (2 kept passes) and e109-3pass.json picks the 3-pass one under the set-aside rule, reads N = 1.735 +- 0.164 W
     (posthoc.json's S_m0_gap) and Y1 PASS, Y2 PASS, Z REPLICATES (E109's labelled reading).
  D. --full: pipeline_e124.sh on E109's raw passes 10910-10912 end to end (reduce_e124.py's card-1 frame on aifoundry3's data: its TDP 0 reads pass E78's
     gate untouched). Found at the first run (19:2x PST, before the freeze): with the meter dips removed the primary keeps all three passes; the dips-kept
     arm sets 10912 aside (its random fp32 anchor spans 1.050 W), so E109's set-aside was a board-meter dip. D asserts exactly that: primary 3, relaxed
     3, dips kept 2, and the verdicts carried by the primary.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D109 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e109-int8-zeros")
L, FAIL = [], []


def ok(cond, msg):
    L.append(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def strip(d):
    d = json.loads(json.dumps(d))
    d["rules"].pop("R10_tie", None)
    return d


def main():
    tmp = tempfile.mkdtemp(prefix="e124st-", dir=os.environ.get("TMPDIR"))
    rc, o = run([sys.executable, os.path.join(HERE, "check_e124.py")])
    ok(rc == 0, f"A check_e124.py: {o.strip()}")
    for name, src in (("3pass", "e109-3pass.json"), ("2kept", "e109.json")):
        out = os.path.join(tmp, f"scored-{name}.json")
        rc, o = run([sys.executable, "tools/claims-v3/e109/score_e109.py", os.path.join(D109, src), "--pred", os.path.join(HERE, "predictions-e124.json"),
                     "--out", out])
        ref = json.load(open(os.path.join(D109, "scored-3pass.json" if name == "3pass" else "scored.json")))
        mine = json.load(open(out))
        ok(rc == 0 and strip(mine) == strip(ref), f"B score_e109.py with predictions-e124.json on E109's {src}: every rule but R10 identical to the committed "
                                                  f"{'scored-3pass.json' if name == '3pass' else 'scored.json'}")
        L.append(f"     R10 against card 1's references: " + ", ".join(f"{k} {v['verdict']}" for k, v in mine["rules"]["R10_tie"].items()))
    rc, o = run([sys.executable, os.path.join(HERE, "extras_e124.py"), "--primary", os.path.join(D109, "e109.json"), "--relaxed",
                 os.path.join(D109, "e109-3pass.json"), "--scored", os.path.join(tmp, "scored-2kept.json"), "--scored-relaxed",
                 os.path.join(tmp, "scored-3pass.json"), "--out", os.path.join(tmp, "extras.json")])
    x = json.load(open(os.path.join(tmp, "extras.json"))) if rc == 0 else {}
    ok(rc == 0 and x.get("which_reduction_scores", "").startswith("relaxed"), f"C the set-aside rule picks the relaxed reduction (2 kept passes in the "
                                                                              f"primary): {x.get('which_reduction_scores')}")
    ph = json.load(open(os.path.join(D109, "posthoc.json")))["three_passes_gate_lifted"]["S_m0_gap"]
    n = x.get("added_rules", {}).get("Y1", {}).get("N", {})
    ok(abs((n.get("mean") or 0) - ph["mean"]) < 1e-9 and abs((n.get("half") or 0) - ph["half"]) < 1e-9,
       f"C N = {n.get('mean')} +- {n.get('half')} equals posthoc.json's S_m0_gap {ph['mean']} +- {ph['half']}")
    v = {k: x.get("added_rules", {}).get(k, {}).get("verdict") for k in ("Y1", "Y2", "Z")}
    ok(v == {"Y1": "PASS", "Y2": "PASS", "Z": "REPLICATES"}, f"C on E109's labelled reading: {v} (expected Y1 PASS, Y2 PASS, Z REPLICATES)")
    if "--full" in sys.argv:
        out = os.path.join(tmp, "pipe")
        passes = [os.path.join(D109, "aifoundry3/e109", f"p{p}") for p in (10910, 10911, 10912)]
        rc, o = run(["bash", os.path.join(HERE, "pipeline_e124.sh"), out] + passes)
        L.append("     pipeline: " + " | ".join(l for l in o.strip().splitlines() if l)[:900])
        try:
            prim, rel = json.load(open(os.path.join(out, "e124.json"))), json.load(open(os.path.join(out, "e124-relaxed.json")))
            dk = json.load(open(os.path.join(out, "e124-dipskept.json")))
            ex = json.load(open(os.path.join(out, "extras.json")))
            ok(len(prim["passes"]) == 3 and len(rel["passes"]) == 3 and len(dk["passes"]) == 2 and ex["which_reduction_scores"] == "primary",
               f"D pipeline on E109's raw passes: primary keeps {prim['passes']}, relaxed {rel['passes']}, dips kept {dk['passes']} (set aside "
               f"{dk.get('passes_set_aside')}); verdicts carried by: {ex['which_reduction_scores']}")
            L.append(f"     D's verdicts (card-1 frame on aifoundry3's data, leak 0.2414, dips removed): " +
                     json.dumps({k: ex['added_rules'][k]['verdict'] for k in ('Y1', 'Y2', 'Z')}) + "; dip samples removed " +
                     json.dumps({p: v['samples_removed'] for p, v in prim['reducer']['dip_samples_removed'].items()}))
        except Exception as e:  # noqa: BLE001
            ok(False, f"D pipeline outputs unreadable: {e}")
    L.append("SELFTEST " + ("PASS" if not FAIL else f"FAIL ({len(FAIL)})"))
    open(os.path.join(HERE, "selftest.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    sys.exit(0 if not FAIL else 1)


if __name__ == "__main__":
    main()
