#!/usr/bin/env python3
"""E218 (Q230): the card, its stops and every point's predicted peak, the card time and its caps, the order, and the refusal rule. Written
before any E218 datum. Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e218/plan_e218.py            writes plan-e218.json and plan-e218.txt
    /usr/bin/python3 -I -B tools/claims-v3/e218/plan_e218.py --check    rebuilds both and compares with the files (exit 0 = PASS)

THE PEAK of a point (DECLARED-v32.md section 9.1, the planning line): PP = the largest W over idle at its own seconds at 600 MHz over MM1-v3.2
(x (1 + 2 eps_G) at a G point, eps_G = MM1-v3.2's LOEO no-twin W-over-idle-given-t rms over the gemmLnc points, 8.429%), MM1-v3.1, MM1-v3,
MM1-v2, 'v3.1 + gemmLnc term' and 'v3.1 + contention' (each where it prices), plus aifoundry3 card 0's rest law at its T0 forecast (MM1-v3.2's
params, 54.4 C), plus 2 W - computed by the land (points-e218.csv > PP) and re-checked here from the landed forecasts (the largest of the six
models' W plus the rest law plus 2 W; G points with MM1-v3.2 x (1 + 2 eps_G)); the script REFUSES (exit 3) if any point's PP is at or above the
67.0 W line or the re-check differs by more than 1e-6 W. BESIDE IT, REPORTED: E215's gemmLnc bound (MM1-v3.1's W over idle x 1.85 + the rest
+ 2 W) at every G point, against the 70 W board stop; E215 arm A's and E213 arm A's measured peaks on this card.
THE CARD TIME (DECLARED-v32.md 9.5): the runs at the pace of the last committed session in this run form on this card, E215 arm A (119 runs in
52.76 card-minutes, docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3, its smoke, gates, die-gate waits and rests included), plus the
smoke and stop-path minutes as E215 counted them (0.89 min for four processes and the stop-path test, scaled to two and the test); no run starts
after 60 card-minutes from the first card command; the session ends at 70 (the cap) after the run in progress; if the plan exceeds 55
card-minutes, F's drawn points are dropped first in reverse draw order, then F's scored ones, never G or Y (this plan does not exceed it).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
LANDED_FC = ("tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json", "1236dd9953b853a59293fc00377ff451b85756319cc80934c60208a7334d6209")
PARAMS = ("tools/matmul/mm1/v3.2/out/mm1_v32_params.json", "c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab")
DEC = ("tools/matmul/mm1/v3.2/out/decisions_v32.json", "ff1a4c014e435ac4df6e999af341fac74dbb6d4745a404b853698e7b38a3a571")
E215A = ("docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/data-e215.json", "651e954328c700205df64c497698621315870ad47d9223a25424e3df842ce763")
A3 = "aifoundry3 card 0"
LINE_W = 67.0
STOP_W = 70.0
MARGIN_W = 2.0
GEMMLNC_FACTOR = 1.85
RULE_MIN, CAP_MIN, DROP_F_ABOVE = 60.0, 70.0, 55.0
SMOKE_MIN_E215 = 0.89  # four smoke processes and the stop-path test, as E215 counted them
PP_MODELS = ("MM1-v3.2", "MM1-v3.1", "MM1-v3", "MM1-v2", "v3.1 + gemmLnc term", "v3.1 + contention")
CARD = {
    "card": A3, "box": "aifoundry3", "devices": "the box's one card, its device nodes at index 0", "lock": "/run/lock/etsoc-shire0.lock",
    "clock": "600 MHz pinned (a boot-time TDP of 0 latches the governor), read, never set",
    "config_gate": "TDP 0 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E207, E211, E213 arm A and E215 arm A read the same)",
    "stops": ("the board strictly above 70 W on 3 samples in a row (counting the samples that carry a board reading; a sample with none neither "
              "counts nor breaks the row); the shires' mean die (minshire[0]) at or above 70 C; the hottest-sensor latch (minshire[2]) at or above "
              "70 C once it has risen during the session above the lowest value it read since the session's first sample (E213's and E215 arm A's "
              "lines); a stop touches the host's stop file, never a kill"),
    "die_gate": "min(60, the session's rest die + 4) C, waited at most 300 s, else that run is NO DATA (E207's, E213 arm A's and E215 arm A's)",
    "run": ("its die gate, 10 s at rest, one host process '--seconds 6 --budget 7.5' under a plain 'timeout 10' (never -k; no SIGKILL to a "
            "device process, sent or arranged), a 4 s tail (E206's form)"),
    "measured_peaks": ("E215 arm A 59.34 W (the gemmLnc smoke s03), its gemmLnc block 50.52 W, shires 55 C, the latch 61 C (session 12:05:55-12:58:41 "
                       "PST Thu 19 Nov 2026, 52.76 card-minutes, no stop); E213 arm A 64.22 W (a075, gemmLnc3x1x3 fp32), 58 C, latch 51 -> 61 C "
                       "(06:37:09-07:19:59 PST Wed 18 Nov 2026); E211 61.9 W, 59 C; E210 58.66 W, 59 C; E207 51.26 W, 56 C: all under the 70 W / 70 C stops"),
    "rest": ("the first card command at least 40 minutes after the last session on aifoundry3 card 0 ended (E215 arm A's ended 12:58:41 PST Thu 19 Nov "
             "2026; any later session counts; simulator runs on aifoundry3 are not card sessions)"),
    "window": ("G = the card lane's booking on its day; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the "
               "Pacific day; G at 20:29:00 PST or earlier (Thu 19 Nov 2026), else from 00:00:30 PST Fri 20 Nov 2026 (the queue bound 08:00 PST Fri)")}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def pinned(rel, want):
    got = sha_rel(rel)
    if got != want:
        print(f"plan_e218: REFUSED, {rel} is {got}, pinned {want}")
        sys.exit(4)
    return os.path.join(REPO, rel)


def build():
    P = json.load(open(os.path.join(HERE, "points-e218.json")))
    L = json.load(open(pinned(*LANDED_FC)))["forecasts"]
    params = json.load(open(pinned(*PARAMS)))
    dec = json.load(open(pinned(*DEC)))
    eps_g = dec["steps"]["step4"]["acceptance"]["5"]["LOEO W given t over gemmLnc points (no twin, >= 3 W)"]["v32"] / 100.0
    rl = params["rest_law"][A3]
    T0 = rl["T0_forecast_c"]
    rest_W = rl["a"] * T0 ** 2 + rl["b"] * T0 + rl["c"]
    d215 = json.load(open(pinned(*E215A)))["arms"]["A"]
    n215 = sum(len(p["runs"]) for p in d215["points"].values()) + len(d215["ties"]["runs"])
    cm215 = d215["queue"]["card_min"]
    pace = cm215 * 60.0 / n215
    peaks, refusals = [], []
    for p in P["points"]:
        f = L[p["id"]]
        ws = []
        for m in PP_MODELS:
            x = f.get(m) or {}
            if x.get("W_over_idle") is None:
                continue
            w = x["W_over_idle"] * ((1.0 + 2.0 * eps_g) if (m == "MM1-v3.2" and p["family"] == "G") else 1.0)
            ws.append((w, m + (" x (1 + 2 eps_G)" if (m == "MM1-v3.2" and p["family"] == "G") else "")))
        if p["family"] == "Y":
            b31 = f["MM1-v3.1"]
            g = f["v3.1 + contention"].get("layout_factor") or 1.0
            ws.append((b31["A_W"] + b31["B_W_us"] / (b31["T_op_us"] * g), "v3.1 + contention (its exact factor)"))
        w, by = max(ws)
        pp = w + rest_W + MARGIN_W
        row = {"point": p["id"], "family": p["family"], "arm": p["arm"], "format": p["format"], "mask": p["shire_mask"], "PP_W": round(pp, 3),
               "PP_by": by, "landed_PP_W": p["PP_W"], "landed_PP_by": p["PP_by"], "recheck_diff_W": pp - p["PP_W"]}
        if p["family"] == "G":
            row["E215_bound_W_REPORTED"] = round(f["MM1-v3.1"]["W_over_idle"] * GEMMLNC_FACTOR + rest_W + MARGIN_W, 3)
            row["E215_bound_under_stop"] = row["E215_bound_W_REPORTED"] < STOP_W
        if abs(pp - p["PP_W"]) > 1e-6 and p["family"] != "Y":
            refusals.append(f"{p['id']}: PP {pp:.6f} W re-checked, the land's {p['PP_W']:.6f} W")
        if p["PP_W"] >= LINE_W:
            refusals.append(f"{p['id']}: PP {p['PP_W']:.2f} W at or above the {LINE_W} W line")
        peaks.append(row)
    if refusals:
        print("plan_e218: REFUSED: " + "; ".join(refusals))
        sys.exit(3)
    o = P["order"]
    runs = o["runs"]
    smoke_min = SMOKE_MIN_E215 * (o["smoke_processes"] + 1) / 5.0
    planned = runs * pace / 60.0 + smoke_min
    top = sorted(peaks, key=lambda r: -r["landed_PP_W"])[:5]
    p1 = len(o["pass1"])
    cut = {"what": "the opening smoke, tie 1, pass 1 and tie 2: every Gt, Y and F point once (the G block not reached)",
           "runs": 1 + p1 + 1, "card_minutes": round((2 + p1) * pace / 60.0 + smoke_min, 1)}
    out = {"experiment": "E218", "request": "Q230", "card": CARD, "line_W": LINE_W, "stop_W": STOP_W, "margin_W": MARGIN_W, "eps_G": eps_g,
           "rest_law_W_at_T0": rest_W, "rest_law_T0_c": T0, "peaks": peaks, "top5": [{"point": r["point"], "PP_W": r["landed_PP_W"], "by": r["landed_PP_by"]}
                                                                                      for r in top],
           "highest_PP_W": top[0]["landed_PP_W"], "highest_G_PP_W": max(r["landed_PP_W"] for r in peaks if r["family"] == "G"),
           "pace": {"source": f"E215 arm A ({E215A[0]}): {n215} runs in {cm215} card-minutes, smoke, gates, die-gate waits and rests included",
                    "s_per_run": pace, "E213_arm_A_REPORTED": "105 runs in 42.83 card-minutes (24.47 s a run)"},
           "order": o, "runs": runs, "smoke_processes": o["smoke_processes"], "smoke_and_stop_path_min": round(smoke_min, 2),
           "card_minutes_planned": round(planned, 1), "rule_min": RULE_MIN, "cap_min": CAP_MIN, "drop_F_above_min": DROP_F_ABOVE,
           "F_dropped_by_the_plan": [], "registered_subset_if_cut": cut, "refusals": []}
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    L2 = [f"E218 on {A3} at 600 MHz ({CARD['devices']}; lock {CARD['lock']})",
          f"  clock: {CARD['clock']}", f"  start config gate (read): {CARD['config_gate']}",
          f"  the planning line: {LINE_W} W (no point runs whose planning peak reaches it); live stops: {CARD['stops']}",
          f"  die gate: {CARD['die_gate']}", f"  a run: {CARD['run']}",
          f"  planning peak (DECLARED-v32.md 9.1; rest law {rest_W:.2f} W at {T0} C, eps_G {eps_g:.5f}): highest {top[0]['landed_PP_W']:.2f} W at "
          f"{top[0]['point']}; top five {[(r['point'], round(r['landed_PP_W'], 2)) for r in top]}",
          "  every point's planning peak (W): " + ", ".join(f"{r['point']} {r['landed_PP_W']:.2f}" for r in peaks),
          "  G points, E215's gemmLnc bound (REPORTED; MM1-v3.1's W x 1.85 + rest + 2 W against the 70 W stop): " +
          ", ".join(f"{r['point']} {r['E215_bound_W_REPORTED']:.2f}" for r in peaks if r["family"] == "G"),
          f"  measured peaks on this card: {CARD['measured_peaks']}",
          f"  card time planned: {planned:.1f} card-minutes ({runs} runs at {pace:.2f} s a run, {out['pace']['source']}; 2 smoke processes and the "
          f"stop-path test {smoke_min:.2f} min); no run starts after {RULE_MIN:.0f} card-minutes; the session ends at {CAP_MIN:.0f} after the run in "
          f"progress; F dropped by the plan: none (the plan is under {DROP_F_ABOVE:.0f} card-minutes)",
          f"  registered subset if cut: {cut}", f"  rest: {CARD['rest']}", f"  window: {CARD['window']}",
          "  order: " + " ".join(f"{b}:{i}" for b, i in o["sequence_blocks"]), "refusals: none"]
    return js, "\n".join(L2) + "\n", out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    js, tx, out = build()
    pj, pt = os.path.join(HERE, "plan-e218.json"), os.path.join(HERE, "plan-e218.txt")
    if a.check:
        ok = open(pj).read() == js and open(pt).read() == tx
        print(f"plan_e218 --check: {'PASS' if ok else 'FAIL'}")
        sys.exit(0 if ok else 1)
    open(pj, "w").write(js)
    open(pt, "w").write(tx)
    print(f"plan_e218: {out['runs']} runs, {out['card_minutes_planned']} card-minutes planned (rule {RULE_MIN:.0f}, cap {CAP_MIN:.0f}); highest PP "
          f"{out['highest_PP_W']:.2f} W (G {out['highest_G_PP_W']:.2f} W); plan-e218.json {hashlib.sha256(js.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
