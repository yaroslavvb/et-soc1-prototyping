#!/usr/bin/env python3
"""E222's kit (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum): THE TIMEOUT SIZING (E222.md 6: "the kit sizes the plain timeout so
that no frozen GEMM's check of C is cut off (E218's R0 lesson: f04's run 77, a 1.31 s GEMM, hit the plain timeout 10)"), from committed bytes
and the frozen forecasts only. E220's desk/timeout_e220.py (kit 2f0ab9cd) for E222's one arm, aifoundry3 card 0 at its pinned 600 MHz.

E218's R0 FAIL (verify-e218d's medium finding): f04 (gemmL15x16x32, MM1-v3.2's frozen 1.3086 s a GEMM) ran past its plain `timeout 10` twice
(10.088 and 10.136 s, rc 124 from the TERM), and run 77's check of C was cut off. Where a process's time goes (rgm136's host, E136's
`repeatFor` and `Session::overBudget`; rgm211's host the same loop): PRE (the host's own setup and the device's opening, to the first launch),
then the launches - one calibration launch, then launches of about 0.5 s (at least one whole GEMM) while the counted launches' time is under
--seconds (6) AND the device has been open for at most --budget (7.5 s): the last launch starts at most 7.5 s after the device opened, so the
device phase ends at most --budget + one launch after it - then POST (the check of C and the device's closing). So, for every process:

    L  <=  PRE + RUN_BUDGET + W + POST       (W: one launch's wall, the larger of ~0.5 s and one GEMM)

THE RULE (E220's classes, one class per process, by MM1-v3.2's frozen seconds a GEMM t at 600 MHz, forecast-e222.csv), its class-S bound read
PER PROCESS (the kit's reading, before any E222 datum):
  - class S (t <= T_S = 0.5 s): every bound term measured on committed bytes from THIS card, aifoundry3 card 0 (E218's session b445b0f5, E215 arm
    A's 8355db15, E213 arm A's c69a12aa): PREPOST_S = the largest measured pre + post OF ONE PROCESS among the processes that exited 0 and whose
    launches are all at most 0.9 s, rounded up to 0.1 s and given 0.1 s more; W_S = the largest measured launch wall of those processes, the
    same rounding; the bound PREPOST_S + RUN_BUDGET + W_S must be at most HOST_TIMEOUT (10 s), else the tool refuses (exit 3): such a process
    keeps the registered plain `timeout 10`. Why per process: a process's length is its own pre, its own device phase (at most RUN_BUDGET and
    one launch) and its own post; E220's form adds the largest pre, the largest launch wall and the largest post of DIFFERENT processes (here
    E218's g11t pre 0.882 s and E215 arm A's a046 post 0.713 s), which reads 10.2 s on this card and is REPORTED beside, never the rule. E222's
    shapes sit inside the committed ranges that drive pre and post (the deepest K, KB 48, and the C sizes: REPORTED below);
  - class L (t > 0.5 s): no E222 point is one (the longest frozen GEMM is wn04t's 0.063 s): the tool refuses (exit 3) if one were, since the kit
    would then need a longer plain timeout for it (E220's xf04 form) by a dated note first.
The smoke processes (s01, s03: `--seconds 2 --budget 3.5`, 0.00076 and 0.00074 s a GEMM) are class S too. REPORTED beside: the deepest K any
E222 point runs (KB 48: wn01, gemmLnc1x6x48) and the committed processes at that depth on this card (E218's g11, g11t: gemmL(nc)6x2x48), and the
longest committed process that exited 0. The sampler's, the config read's and every other device call keeps its `timeout 10`. Nothing here
changes a point, a forecast, the run's form (--seconds 6 --budget 7.5), a stop, the card-time rule or the cap.

    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/timeout_e222.py           writes desk/timeouts-e222.json (exit 0; 3 refused)
    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/timeout_e222.py --check   re-makes it in memory and compares (TIMEOUT-E222 CHECK PASS / FAIL)
Standard library only; single-threaded; reads committed files only.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import glob
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E222 = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E222, "..", "..", ".."))
OUT = os.path.join(HERE, "timeouts-e222.json")
FC = ("tools/claims-v3/e222/forecast-e222.csv", "223f943e32c01544063de6b1dc925712e0701ba43f4c99f97ff622e8c5b835cb")
PLAN = ("tools/claims-v3/e222/plan-e222.json", "4feb710a9f99a4652ea3b977097fed231ba5fe0f23e4d51712b73c56eeae28a7")
SESSIONS = ["docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3", "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3",
            "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3"]
CARD = "aifoundry3 card 0"
COL = "600.0"
HOST_TIMEOUT_S = 10
RUN_BUDGET = 7.5
T_S = 0.5
MARGIN_S = 0.1


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(rel, pin):
    p = os.path.join(REPO, rel)
    if sha(p) != pin:
        sys.exit(f"timeout_e222: REFUSED, {rel} is not its pinned {pin[:12]}")
    return p


def up(x):
    return math.ceil(x * 10 - 1e-9) / 10.0


def kb_of(tok):
    m = re.match(r"gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$", tok or "")
    return int(m.group(3)) if m else None


def processes(d):
    """(token, pre, post, launch walls, rc, length) of every committed process of a session folder (E215's/E218's run.json form), from each
    process's own launch records (SPARSITY t_start_ms, t_end_ms, wall_s) and its run.json t0_ms/t1_ms"""
    out = []
    for rj in sorted(glob.glob(os.path.join(REPO, d, "session", "runs", "*", "run.json"))):
        try:
            R = json.load(open(rj))
        except (OSError, ValueError):
            continue
        for p in R.get("procs") or []:
            op = os.path.join(os.path.dirname(rj), p.get("name", "") + ".out")
            if not os.path.exists(op) or p.get("t0_ms") is None or p.get("t1_ms") is None:
                continue
            L = []
            for ln in open(op, errors="replace"):
                if ln.startswith("SPARSITY "):
                    try:
                        j = json.loads(ln[9:])
                    except ValueError:
                        continue
                    if isinstance(j, dict) and j.get("test") == "fma" and j.get("t_start_ms") and j.get("t_end_ms"):
                        L.append(j)
            if not L:
                continue
            out.append({"token": L[0].get("arm"), "pre": (L[0]["t_start_ms"] - p["t0_ms"]) / 1e3, "post": (p["t1_ms"] - L[-1]["t_end_ms"]) / 1e3,
                        "walls": [float(x.get("wall_s") or 0) for x in L], "rc": p.get("rc"), "len": (p["t1_ms"] - p["t0_ms"]) / 1e3,
                        "run": os.path.basename(os.path.dirname(rj)), "session": os.path.basename(d)})
    return out


def make():
    fc = {}
    with open(pinned(*FC)) as f:
        for r in csv.DictReader(f):
            if r["model"] == "MM1-v3.2" and r["f_mhz"] == COL:
                fc[r["id"]] = r
    plan = json.load(open(pinned(*PLAN)))
    meas = []
    for d in SESSIONS:
        meas += processes(d)
    small = [x for x in meas if max(x["walls"]) <= 0.9]
    rc0 = [x for x in meas if x["rc"] == 0]
    s0 = [x for x in small if x["rc"] == 0]
    top = max(s0, key=lambda x: x["pre"] + x["post"])
    PREPOST_S = round(up(top["pre"] + top["post"]) + MARGIN_S, 3)
    W_S = round(up(max(max(x["walls"]) for x in small)) + MARGIN_S, 3)
    bound_s = round(PREPOST_S + RUN_BUDGET + W_S, 3)
    PRE_S = round(up(max(x["pre"] for x in small)) + MARGIN_S, 3)              # E220's form, REPORTED
    POST = round(up(max(x["post"] for x in rc0)) + MARGIN_S, 3)
    e220_form = round(PRE_S + RUN_BUDGET + W_S + POST, 3)
    per, refused = {}, []
    for r in plan["order"]["runs"]:
        pid = r["id"]
        row = fc.get(pid)
        if row is None:
            refused.append(f"{pid}: no MM1-v3.2 row in forecast-e222.csv")
            continue
        t = float(row["seconds_per_gemm"])
        cls = "S" if t <= T_S else "L"
        if cls == "L":
            refused.append(f"{pid}: {row['token']} {t:.3f} s a GEMM is class L (a longer plain timeout would be needed: a dated note first)")
        per[pid] = {"token": row["token"], "t_s": round(t, 6), "class": cls, "timeout_s": HOST_TIMEOUT_S,
                    "form": "--seconds 2 --budget 3.5" if r["block"] == "smoke" else "--seconds 6 --budget 7.5"}
    deep_kb = max(kb_of(v["token"]) or 0 for v in per.values())
    rec = {"what": "E222's per-process plain timeout, sized so that no frozen GEMM's check of C is cut off (E222.md 6; E218's R0 lesson) - the "
                   "kit's sizing tool desk/timeout_e222.py (E220's rule); every device call keeps `timeout 10`",
           "card": CARD, "column_mhz": COL,
           "rule": {"class_S": f"MM1-v3.2's frozen seconds a GEMM at 600 MHz at most {T_S} s: the registered plain timeout {HOST_TIMEOUT_S} s, the "
                               f"bound PREPOST_S + RUN_BUDGET + W_S (one process's own pre and post) at most {HOST_TIMEOUT_S} s",
                    "class_L": "none in E222 (refused if one were)", "PREPOST_S": PREPOST_S, "W_S": W_S, "RUN_BUDGET": RUN_BUDGET,
                    "class_S_bound_s": bound_s,
                    "PREPOST_S_from": {"run": top["run"], "session": top["session"], "token": top["token"], "pre_s": round(top["pre"], 3),
                                       "post_s": round(top["post"], 3)},
                    "E220_form_REPORTED": {"what": "E220's sum of the largest pre, launch wall and post of different processes (never the rule here)",
                                           "PRE_S": PRE_S, "W_S": W_S, "POST": POST, "bound_s": e220_form}},
           "measured": {"sessions": SESSIONS, "processes": len(meas), "pre_max_s": round(max(x["pre"] for x in meas), 3),
                        "post_max_rc0_s": round(max(x["post"] for x in rc0), 3), "len_max_rc0_s": round(max(x["len"] for x in rc0), 3),
                        "longest": sorted(({"run": x["run"], "session": x["session"], "token": x["token"], "len_s": round(x["len"], 3),
                                            "pre_s": round(x["pre"], 3), "post_s": round(x["post"], 3), "rc": x["rc"],
                                            "wall_max_s": round(max(x["walls"]), 3)} for x in meas), key=lambda r: -r["len_s"])[:4],
                        "at_the_deepest_K_REPORTED": {"E222_deepest_KB": deep_kb, "E222_points_at_it": sorted(k for k, v in per.items() if kb_of(v["token"]) == deep_kb),
                                                      "committed_processes_at_it": sorted(({"run": x["run"], "session": x["session"], "token": x["token"],
                                                                                            "len_s": round(x["len"], 3), "post_s": round(x["post"], 3),
                                                                                            "rc": x["rc"]} for x in meas if kb_of(x["token"]) == deep_kb),
                                                                                          key=lambda r: (r["session"], r["run"]))}},
           "runs": per, "longest_E222_GEMM_s": max(v["t_s"] for v in per.values()), "longer_timeouts": {}, "refused": refused,
           "fc_sha256": FC[1], "plan_sha256": PLAN[1]}
    if bound_s > HOST_TIMEOUT_S:
        refused.append(f"the class-S bound {bound_s} s is over the registered {HOST_TIMEOUT_S} s")
    return rec, refused


def main():
    rec, refused = make()
    txt = json.dumps(rec, indent=1, sort_keys=True) + "\n"
    if refused:
        print("timeout_e222: REFUSED: " + "; ".join(refused[:6]))
        sys.exit(3)
    if "--check" in sys.argv[1:]:
        ok = os.path.exists(OUT) and open(OUT).read() == txt
        print("TIMEOUT-E222 CHECK " + ("PASS" if ok else "FAIL (rebuilt != committed)") +
              f" (every E222 process class S under the plain timeout {HOST_TIMEOUT_S} s; the class-S bound {rec['rule']['class_S_bound_s']} s per process, "
              f"E220's form {rec['rule']['E220_form_REPORTED']['bound_s']} s REPORTED; "
              f"the longest frozen GEMM {rec['longest_E222_GEMM_s']} s)")
        sys.exit(0 if ok else 1)
    open(OUT, "w").write(txt)
    print(f"every E222 process class S: plain timeout {HOST_TIMEOUT_S} s; class-S bound {rec['rule']['class_S_bound_s']} s (PREPOST_S "
          f"{rec['rule']['PREPOST_S']} from {rec['rule']['PREPOST_S_from']['run']}, W_S {rec['rule']['W_S']}; E220's form "
          f"{rec['rule']['E220_form_REPORTED']['bound_s']} s REPORTED); longest frozen GEMM {rec['longest_E222_GEMM_s']} s; deepest KB "
          f"{rec['measured']['at_the_deepest_K_REPORTED']['E222_deepest_KB']} with {len(rec['measured']['at_the_deepest_K_REPORTED']['committed_processes_at_it'])} "
          f"committed processes at it on {CARD}")
    print(f"wrote {os.path.relpath(OUT, REPO)} {sha(OUT)}")


if __name__ == "__main__":
    main()
