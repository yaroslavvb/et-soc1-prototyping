#!/usr/bin/env python3
"""E220's kit (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): THE TIMEOUT SIZING (E220.md 6: "the kit sizes the timeout so that
no frozen GEMM's check of C is cut off (E218's R0 lesson: f04 run 77)"), for both arms, from committed bytes and the frozen forecasts only.

E218's R0 FAIL (verify-e218d's medium finding): f04 (gemmL15x16x32, MM1-v3.2's frozen 1.3086 s a GEMM) ran past its plain `timeout 10` twice
(10.088 and 10.136 s, rc 124 from the TERM), and run 77's check of C was cut off. Where a process's time goes (rgm136's host, E136's
`repeatFor` and `Session::overBudget`, both hosts the same loop): PRE (the host's own setup and the device's opening, to the first launch), then
the launches - one calibration launch, then launches of about 0.5 s (at least one whole GEMM) while the counted launches' time is under
--seconds (6) AND the device has been open for at most --budget (7.5 s): the last launch starts at most 7.5 s after the device opened, so the
device phase ends at most --budget + one launch after it - then POST (the check of C and the device's closing). So, for every process:

    L  <=  PRE + RUN_BUDGET + W + POST       (W: one launch's wall, the larger of ~0.5 s and one GEMM)

THE RULE (one class per process, by MM1-v3.2's frozen seconds a GEMM t at the arm's SLOWEST clock: arm A 600 MHz; arm B the 600 MHz column, the
governor's floor, so that a route-m run is covered too):
  - class S (t <= T_S = 0.5 s): every bound term measured on committed bytes, on the arm's card and on aifoundry3 (the slowest host the lab has
    measured these shapes on, E218): PRE_S = the largest measured pre of any process whose GEMM is at most 0.5 s, rounded up to 0.1 s and given
    0.1 s more; W_S = the largest measured launch wall of those processes, the same rounding; POST = the largest measured post of any process
    that exited 0, the same rounding; the bound must be at most HOST_TIMEOUT (10 s), else the tool refuses (exit 3): such a process keeps the
    registered plain `timeout 10`;
  - class L (t > 0.5 s): its timeout is ceil(PRE_L + RUN_BUDGET + 1.25 t + POST_L + 1.0) s, where PRE_L is the largest measured pre (f04's on
    aifoundry3, the only committed GEMM of that size) given 0.33 s more and POST_L 0.6 s (f04's check takes about 0.36 s, verify-e218d): still a
    plain `timeout` (never -k), only longer. E220 has one such point on each arm: xf04 (gemmL15x16x32 fp32), E218's f04.
The sampler's, the config read's and every other device call keeps its `timeout 10`. Nothing here changes a point, a forecast, the run's form
(--seconds 6 --budget 7.5), a stop, the card-time rule or the cap.

    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/timeout_e220.py           writes desk/timeouts-e220.json (exit 0; 3 a class-S bound over 10 s)
    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/timeout_e220.py --check   re-makes it in memory and compares (CHECK PASS / CHECK FAIL)
Standard library only; single-threaded; reads committed files only.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import glob
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E220 = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E220, "..", "..", ".."))
OUT = os.path.join(HERE, "timeouts-e220.json")
FC = ("tools/claims-v3/e220/forecast-e220.csv", "082e3d9c8c1c32353438fe8e2930ad3d900049f5f1b3181c48d1897d373227fa")
PLAN = ("tools/claims-v3/e220/plan-e220.json", "6d63318734f61bc6b9c9fa7550b52434b2d309e9f1182a6964413fb3a6ef79d9")
# the committed sessions read, by card (each a data folder at GitHub main, read only)
SESSIONS = {
    "aifoundry1 card 1": ["docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1", "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1"],
    "aifoundry2 card 0": ["docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2", "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2"],
    "aifoundry3 card 0": ["docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3"],
}
ARM_CARD = {"A": "aifoundry1 card 1", "B": "aifoundry2 card 0"}
SLOW_COL = {"A": "600.0", "B": "600.0"}
HOST_TIMEOUT_S = 10
RUN_BUDGET = 7.5
T_S = 0.5
MARGIN_S = 0.1
PRE_L_MARGIN = 0.33
POST_L = 0.6
L_SAFETY = 1.0
T_GROW = 1.25
SMOKE_TOKEN = {("A", "s03"): "gemmLnc2x1x37", ("B", "s03"): "gemmLnc6x5x10"}     # D1's smoke rows (plan-e220.json > departure_D1_smoke)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(rel, pin):
    p = os.path.join(REPO, rel)
    if sha(p) != pin:
        sys.exit(f"timeout_e220: REFUSED, {rel} is not its pinned {pin[:12]}")
    return p


def up(x):
    return math.ceil(x * 10 - 1e-9) / 10.0


def processes(d):
    """(token, pre, post, launch walls, rc) of every committed process of a session folder (E215's/E218's run.json form and E208's), from
    each process's own launch records (SPARSITY t_start_ms, t_end_ms, wall_s) and its run.json t0_ms/t1_ms."""
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
                        "run": os.path.basename(os.path.dirname(rj))})
    return out


def make():
    fc = {}
    with open(pinned(*FC)) as f:
        for r in csv.DictReader(f):
            if r["model"] == "MM1-v3.2":
                fc[(r["arm"], r["id"], r["f_mhz"])] = r
    plan = json.load(open(pinned(*PLAN)))
    meas = {card: [] for card in SESSIONS}
    for card, ds in SESSIONS.items():
        for d in ds:
            meas[card] += [dict(x, session=os.path.basename(d)) for x in processes(d)]
    # the measured GEMM seconds by token: a process's longest launch with one GEMM a launch is the GEMM's time; a launch of ~0.5 s holds several
    allp = [x for c in meas for x in meas[c]]
    small = [x for x in allp if max(x["walls"]) <= 0.9]          # launches of about 0.5 s: GEMMs at most 0.5 s (rgm136's ~0.5 s launches)
    big = [x for x in allp if max(x["walls"]) > 0.9]             # one GEMM a launch, longer than 0.9 s (E218's f04)
    PRE_S = round(up(max(x["pre"] for x in small)) + MARGIN_S, 3)
    W_S = round(up(max(max(x["walls"]) for x in small)) + MARGIN_S, 3)
    POST = round(up(max(x["post"] for x in allp if x["rc"] == 0)) + MARGIN_S, 3)
    PRE_L = round(up(max(x["pre"] for x in big) + PRE_L_MARGIN), 3) if big else None
    bound_s = round(PRE_S + RUN_BUDGET + W_S + POST, 3)
    rec = {"what": "E220's per-process plain timeout, sized so that no frozen GEMM's check of C is cut off (E220.md 6; E218's R0 lesson) - the "
                   "kit's sizing tool desk/timeout_e220.py; every other device call keeps `timeout 10`",
           "rule": {"class_S": f"MM1-v3.2's frozen seconds a GEMM at the arm's slowest clock at most {T_S} s: the registered plain timeout "
                               f"{HOST_TIMEOUT_S} s, the bound PRE_S + RUN_BUDGET + W_S + POST at most {HOST_TIMEOUT_S} s",
                    "class_L": f"over {T_S} s: ceil(PRE_L + RUN_BUDGET + {T_GROW} t + POST_L + {L_SAFETY}) s, still a plain timeout (never -k)",
                    "PRE_S": PRE_S, "W_S": W_S, "POST": POST, "PRE_L": PRE_L, "POST_L": POST_L, "RUN_BUDGET": RUN_BUDGET,
                    "class_S_bound_s": bound_s},
           "measured": {card: {"sessions": SESSIONS[card], "processes": len(meas[card]),
                               "pre_max_s": round(max((x["pre"] for x in meas[card]), default=0), 3),
                               "post_max_rc0_s": round(max((x["post"] for x in meas[card] if x["rc"] == 0), default=0), 3),
                               "len_max_s": round(max((x["len"] for x in meas[card]), default=0), 3),
                               "longest": sorted(({"run": x["run"], "session": x["session"], "token": x["token"], "len_s": round(x["len"], 3),
                                                   "pre_s": round(x["pre"], 3), "post_s": round(x["post"], 3), "rc": x["rc"],
                                                   "wall_max_s": round(max(x["walls"]), 3)} for x in meas[card]),
                                                 key=lambda r: -r["len_s"])[:4]} for card in meas},
           "arms": {}, "fc_sha256": FC[1], "plan_sha256": PLAN[1]}
    if bound_s > HOST_TIMEOUT_S:
        print(f"timeout_e220: the class-S bound {bound_s} s is over the registered {HOST_TIMEOUT_S} s: REFUSED (a kit note first)")
        sys.exit(3)
    for arm in ("A", "B"):
        runs = plan["arms"][arm]["runs"]
        per = {}
        for r in runs:
            pid = r["id"]
            tok = SMOKE_TOKEN.get((arm, pid), r.get("token"))
            row = fc.get((arm, pid, SLOW_COL[arm]))
            t = float(row["seconds_per_gemm"]) if row and row.get("token") == tok else None
            if t is None:               # the smoke rows D1 replaced (and s01 on arm B: E208's three 1x1x4 smoke arms): 2 s processes, class S
                per[pid] = {"token": tok, "t_s": None, "class": "S (a smoke row, --seconds 2 --budget 3.5: no frozen forecast of its token)",
                            "timeout_s": HOST_TIMEOUT_S}
                continue
            if t <= T_S:
                per[pid] = {"token": tok, "t_s": round(t, 6), "class": "S", "timeout_s": HOST_TIMEOUT_S}
            else:
                L = PRE_L + RUN_BUDGET + T_GROW * t + POST_L
                per[pid] = {"token": tok, "t_s": round(t, 6), "class": "L", "bound_s": round(L, 3), "timeout_s": int(math.ceil(L + L_SAFETY))}
        rec["arms"][arm] = {"card": ARM_CARD[arm], "slowest_column_mhz": SLOW_COL[arm], "timeouts": per,
                            "longer": {k: v["timeout_s"] for k, v in per.items() if v["timeout_s"] != HOST_TIMEOUT_S}}
    return rec


def main():
    rec = make()
    txt = json.dumps(rec, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv[1:]:
        ok = os.path.exists(OUT) and open(OUT).read() == txt
        print("TIMEOUT-E220 CHECK " + ("PASS" if ok else "FAIL (rebuilt != committed)"))
        sys.exit(0 if ok else 1)
    open(OUT, "w").write(txt)
    for arm in ("A", "B"):
        print(f"arm {arm}: longer timeouts {rec['arms'][arm]['longer']}; class S bound {rec['rule']['class_S_bound_s']} s")
    print(f"wrote {os.path.relpath(OUT, REPO)} {sha(OUT)}")


if __name__ == "__main__":
    main()
