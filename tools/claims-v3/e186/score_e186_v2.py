#!/usr/bin/env python3
"""E186 kit note 1 (Q158, fix-e186): the scorer v2. It is score_e186.py, imported and run UNCHANGED (its frozen checks, its C-session
gate, E186-C, the scale with its fail-closed rule, every line and every rule of E186.md section 5), with one gate added before any word
is read from a train (verify-e186's fault 1; E186.md.dated-amendment-A1.md section A1-2):

  THE PAIRING CHECK (pairing_e186.py, over every train block of the raw copy): a train with any launch record whose train_kind is off
  the registered schedule, whose type is not the train's, whose train_values is not the scheduled kind's registered tile, or whose C
  record is missing or carries another fnv than the scheduled kind's registered tile bytes reads NOT SCORED, exactly as a train with a
  launch not PASS reads under E186-C: its SIGN, SIZE and WHICH words NOT SCORED, its z in no joint word, the rules read from it as E186.md
  says for a train NOT SCORED (SPLIT3/SPLIT63 NOT SCORED, GB/GA over the other ladder train, S23R NOT SCORED), and its quads in no
  E186-TR-N pool. E186-C itself is not changed: it still reads the check of C alone. The gate's own reading is written as
  rules > E186-PAIR (PASS, or FAIL with the trains), and the full report as "pairing".

How. train_iv (score_e186's per-train interval) is wrapped for the one call, so every rule downstream reads the NOT SCORED interval; then
E186-TR-N is re-read with score_e186's own lines, the failed trains left out (the same value when no train fails: checked). Nothing else
is recomputed. score_e186.py, pairing_e186.py and this file each have their sha256 in the output.

  score   /usr/bin/python3 -B score_e186_v2.py score <score_e186.py's arguments, unchanged>
Exit codes: score_e186's (0 written, 4 no finished check of C, 9 a frozen input differs), and 9 when a registered tile is off its sha256.
/usr/bin/python3 (3.9). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e186 as B  # noqa: E402  (run unchanged; train_iv is wrapped for the one call)
import pairing_e186 as PR  # noqa: E402

VERSION = "score_e186_v2 (KIT.md.dated-note-1.md)"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def trn(tr, ctr, leave_out):
    """E186-TR-N exactly as score_e186.score reads it (its loop, its TRN_SIG, its thresholds), with the trains in leave_out left out"""
    by_f = {}
    for tid, t in tr.get("trains", {}).items():
        if not ctr.get(tid, {}).get("all_pass") or tid in leave_out:
            continue
        rp = t["reported"]
        if rp.get("quad_residual_df"):
            fam = "int8" if t["type"] == "int8" else "float"
            ss, dfn = by_f.get(fam, (0.0, 0))
            by_f[fam] = (ss + rp["quad_residual_sd"] ** 2 * rp["quad_residual_df"], dfn + rp["quad_residual_df"])
    ratios = {f: {"pooled_sd_w": math.sqrt(ss / dfn), "df": dfn, "forecast_sd_w": B.TRN_SIG[f], "ratio": math.sqrt(ss / dfn) / B.TRN_SIG[f]}
              for f, (ss, dfn) in by_f.items()}
    if ratios:
        rr = max(v["ratio"] for v in ratios.values())
        return {"verdict": "AS FORECAST" if rr <= 1.25 else ("WORSE" if rr <= 2.0 else "FAILS"), "largest_ratio": rr, "by_family": ratios}
    return {"verdict": "NOT SCORED", "why": "no train scored"}


def score(a):
    pr = PR.check_raw(a.raw, os.path.dirname(os.path.abspath(a.ccheck)))
    failed = {tid: v for tid, v in pr["trains"].items() if not v["ok"]}
    base_iv = B.train_iv

    def train_iv(tr, tid, ctr):
        v = base_iv(tr, tid, ctr)
        if tid in failed and v.get("lo") is not None:
            f = failed[tid]
            return {"n": 0, "lo": None, "hi": None, "mean": None, "se": None, "df": None, "hw": None,
                    "why": f"the pairing check (KIT.md.dated-note-1.md; A1-2): {f['why']}; {f['failures_by_check']}; "
                           + "; ".join(f["first_failures"][:2])}
        return v
    B.train_iv = train_iv
    try:
        out = B.score(a)
    finally:
        B.train_iv = base_iv
    tr = json.load(open(a.trains)) if a.trains and os.path.exists(a.trains) else {"trains": {}}
    ctr = out["c_status"]["trains"]
    if not failed:
        same = trn(tr, ctr, set())
        if json.dumps(same, sort_keys=True) != json.dumps(out["rules"]["E186-TR-N"], sort_keys=True):
            raise B.Refuse(B.EXIT_FROZEN, "E186-TR-N re-read with no train left out differs from score_e186's own: refusing")
    else:
        out["rules"]["E186-TR-N"] = dict(trn(tr, ctr, set(failed)), trains_left_out_by_the_pairing_check=sorted(failed))
        out["verdicts"]["E186-TR-N"] = out["rules"]["E186-TR-N"]["verdict"]
    out["rules"]["E186-PAIR"] = {"verdict": "PASS" if pr["ok"] else "FAIL", "trains_read": pr["trains_checked"],
                                 "trains_not_paired": pr["trains_failed"],
                                 "rule": "every launch record of every train block on the registered schedule, its type, its tile and a C "
                                         "record of that tile's bytes (E186.md.dated-amendment-A1.md section A1-2); a train not paired "
                                         "reads NOT SCORED"}
    out["verdicts"]["E186-PAIR"] = out["rules"]["E186-PAIR"]["verdict"]
    out["pairing"] = pr
    out["scorer_v2"] = {"version": VERSION, "score_e186_v2_sha256": sha(os.path.abspath(__file__)),
                        "score_e186_sha256": sha(os.path.abspath(B.__file__)), "pairing_e186_sha256": sha(os.path.abspath(PR.__file__))}
    return out


def md(out):
    s = B.md(out)
    p = out["pairing"]
    L = ["", "## The pairing check (score_e186_v2.py, KIT.md.dated-note-1.md)", "",
         f"E186-PAIR: {out['verdicts']['E186-PAIR']}; {len(p['trains_checked'])} train block(s) read; not paired: {p['trains_failed'] or 'none'}",
         "", "| train | block | launch records | paired | not paired, by check | C log |", "|---|---|---|---|---|---|"]
    for tid, v in p["trains"].items():
        L.append(f"| {tid} | p{v['block']} | {v['launch_records']} | {v['launches_paired']} | {v['failures_by_check'] or 0} | "
                 f"{', '.join(v['c_log']) or 'none'} |")
    return s + "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("score",))
    ap.add_argument("--reduction")
    ap.add_argument("--runs-csv")
    ap.add_argument("--trains")
    ap.add_argument("--anchors")
    ap.add_argument("--raw", required=True)
    ap.add_argument("--ccheck", required=True)
    ap.add_argument("--since", type=float)
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--skip-c-gate", action="store_true")
    a = ap.parse_args()
    try:
        out = score(a)
    except B.Refuse as e:
        print(f"REFUSED ({e.code}): {e}", file=sys.stderr)
        sys.exit(e.code)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(f"REFUSED (9): {e.code}", file=sys.stderr)
            sys.exit(9)
        raise
    js = json.dumps(out, indent=1, sort_keys=True, default=lambda o: sorted(o) if isinstance(o, set) else None) + "\n"
    if a.json:
        open(a.json, "w").write(js)
    if a.md:
        open(a.md, "w").write(md(out))
    print(json.dumps(out["verdicts"], indent=1))


if __name__ == "__main__":
    main()
