#!/usr/bin/env python3
"""E175 (Q143(g) fix pass; dated note A2 beside E175.md): the self-test of m1_reading_e175.py, before any E175 session. Desk only: it reads
committed files and writes only temporary ones. Every session here is made up, in selftest_score_e175.py's form (synth_cells: the zeros anchors
at made-up reads, every other tile's measured values = the scorer's own recomputed prediction + a designed error), and is scored by the
registered scorer itself (score_e175.score, unchanged); the reader then reads that score.

  R1  measured = M10 carried exactly: M1 BETTER (as the scorer's S3g) and M1c BETTER: read as evidence on D (BETTER).
  R2  measured = M9's part exactly: M1 WORSE and M1c WORSE: read as evidence on D (WORSE).
  R3  a board level 0.5 W below M10 carried on both groups, with tile-to-tile noise (0.3 W) that has no part along the two models' within-group
      difference: M1 BETTER, M1c not BETTER: read as the session's board level, its side "below both models' predictions".
  R4  the same 0.5 W above: M1 WORSE, M1c not WORSE: read as the session's board level, "above".
  R5  the noise alone (zero mean in each group): M1 NOT RESOLVED and M1c NOT RESOLVED: no reading on D.
  R6  9 scored tiles (M1's minimum is 10): M1 NOT SCORED: nothing read, no crash.
  R7  in R1-R5 the reader's re-derived M1 and clock beside equal the scorer's field for field, and the identity holds: M1's point is below 0
      exactly when abar_delta < theta, and mean(a^2) - mean(b^2) = 2 mean(delta) (abar_delta - theta).
  R8  refusals: a results file whose M1 verdict was altered (exit 2); whose clock beside was altered (exit 2); a file that is not the scorer's
      (exit 3); and a score with fewer than 2 passes (only its note): NOT SCORED, exit 0.

    /usr/bin/python3 -B tools/claims-v3/e175/selftest_m1_reading_e175.py > tools/claims-v3/e175/selftest-m1-reading.txt
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e165"))
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
import e175_common as C  # noqa: E402
import p8gov as G  # noqa: E402
import score_e175 as SC  # noqa: E402
import m1_reading_e175 as R  # noqa: E402

RES = []


def ok(cond, what):
    RES.append((bool(cond), what))
    print(("PASS " if cond else "FAIL ") + what)


def cells_for(P, A, pred_a2, mode):
    """selftest_score_e175.synth_cells' form: 3 passes per tile, the zeros anchors at made-up reads, the others' measured values = the scorer's
    own recomputed prediction (M10 carried, or M9's part for mode m9) + a designed board error; the clock and rise errors are small patterns"""
    cells = {}
    zw = {"fp32": 34.1, "fp16": 34.0, "int8": 35.3}
    for nm in C.ZEROS_ANCHORS:
        t = P["tiles"][nm]
        cells[t["label"]] = {"label": t["label"], "passes": [1, 2, 3], "n": 3, "burst_mhz_runs": [800.0] * 3, "burst_w_runs": [zw[t["type"]]] * 3,
                             "die_start_runs": [53, 54, 55], "rise_runs": [2.0] * 3, "burst_mhz": 800.0, "burst_w": zw[t["type"]], "rise_c": 2.0,
                             "name": nm, "type": t["type"], "peak_w_runs": [zw[t["type"]] + 1] * 3, "peak_w": zw[t["type"]] + 1}
    for nm in P["run"]:
        if nm in C.ZEROS_ANCHORS:
            continue
        t = P["tiles"][nm]
        cells[t["label"]] = {"label": t["label"], "passes": [1, 2, 3], "n": 3, "burst_mhz_runs": [0.0] * 3, "burst_w_runs": [0.0] * 3,
                             "die_start_runs": [52, 54, 56], "rise_runs": [0.0] * 3, "name": nm, "type": t["type"], "peak_w_runs": [60.0] * 3, "peak_w": 60.0}
    pm10, pm9, _ = SC.predictions(A, pred_a2, cells, P)
    scored = sorted(P["sets"]["scored"])
    grp = {n: P["tiles"][n]["group"] for n in scored}
    # the noise: +-0.3 W alternating in name order within each group, less its part along the two models' within-group difference, centred
    noise = {}
    for g in ("governed", "pinned"):
        ns = [n for n in scored if grp[n] == g]
        d = [pm9[n]["burst_board_w"] - pm10[n]["burst_board_w"] for n in ns]
        dm = sum(d) / len(d)
        dc = [x - dm for x in d]
        u = [0.3 if i % 2 == 0 else -0.3 for i in range(len(ns))]
        um = sum(u) / len(u)
        u = [x - um for x in u]
        dd = sum(x * x for x in dc)
        k = sum(x * y for x, y in zip(u, dc)) / dd if dd else 0.0
        v = [x - k * y for x, y in zip(u, dc)]
        vm = sum(v) / len(v)
        for n, x in zip(ns, v):
            noise[n] = x - vm
    for i, nm in enumerate(P["run"]):
        if nm in C.ZEROS_ANCHORS:
            continue
        c = cells[P["tiles"][nm]["label"]]
        base = pm9 if mode == "m9" else pm10
        e = noise.get(nm, 0.0)
        ew = {"m10": 0.0, "m9": 0.0, "low": -0.5 + e, "high": 0.5 + e, "noise": e}[mode]
        em = 0.0 if mode in ("m10", "m9") else (0.7 if i % 2 else -0.7)
        c["burst_w"] = base[nm]["burst_board_w"] + ew
        c["burst_mhz"] = base[nm]["burst_mhz"] + em
        c["rise_c"] = base[nm]["burst_die_rise_c"]
        c["burst_w_runs"], c["burst_mhz_runs"], c["rise_runs"] = [c["burst_w"]] * 3, [c["burst_mhz"]] * 3, [c["rise_c"]] * 3
    return cells


def main():
    A = C.a2p()
    P = SC.load_pred()
    with open(os.path.join(C.TOP, C.PRED_REL)) as f:
        pred_a2 = json.load(f)
    print(f"E175 dated note A2's M1 reader, self-test: m1_reading_e175.py {C.sha256_file(R.__file__)[:16]}, score_e175.py {C.sha256_file(SC.__file__)[:16]}, "
          f"p8gov.py {C.sha256_file(G.__file__)[:16]}, predictions-e175.json {C.sha256_file(SC.PRED_PATH)[:16]}; seeds M1 {A.P().seed_of(R.RULE_M1)}, "
          f"M1c {A.P().seed_of(R.RULE_M1C)}")
    want = {"m10": ("BETTER", "BETTER", "BETTER: evidence on D"), "m9": ("WORSE", "WORSE", "WORSE: evidence on D"),
            "low": ("BETTER", None, "BETTER: the session's board level, not evidence on D"),
            "high": ("WORSE", None, "WORSE: the session's board level, not evidence on D"),
            "noise": ("NOT RESOLVED", "NOT RESOLVED", "NOT RESOLVED: no reading on D")}
    keep = {}
    for k, (v1, vc, rd) in want.items():
        sc = SC.score(cells_for(P, A, pred_a2, k), P, A, pred_a2)
        r = R.read({"score": sc}, P, A)
        keep[k] = (sc, r)
        m1, m1c = r["M1"]["verdict"], r["M1c"]["verdict"]
        cond = m1 == v1 and r["reading"] == rd and (m1c == vc if vc else m1c != v1)
        tag = {"m10": "R1", "m9": "R2", "low": "R3", "high": "R4", "noise": "R5"}[k]
        extra = ""
        if k in ("low", "high"):
            side = "below" if k == "low" else "above"
            cond = cond and r["side"] == side and f"{side} both models' predictions" in r["sentence"] and "not evidence on D" in r["sentence"]
            extra = f", side {r['side']} (Bg's mean {r['Bg_mean_w']:+.3f} W, Bp's {r['Bp_mean_w']:+.3f} W)"
        ok(cond, f"{tag} {k}: M1 {m1} {r['M1'].get('ci95')}, M1c {m1c} {r['M1c'].get('ci95')}: reading '{r['reading']}'{extra}")
    # R6: fewer than 10 scored tiles
    cells = cells_for(P, A, pred_a2, "low")
    sc_all = sorted(P["sets"]["scored"])
    drop = set(sc_all[9:])
    few = {lab: c for lab, c in cells.items() if C.name_of(lab) not in drop}
    sc6 = SC.score(few, P, A, pred_a2)
    r6 = R.read({"score": sc6}, P, A)
    ok(sc6["tiles_scored"] == 9 and r6["verdict"].startswith("NOT SCORED") and r6["reading"] == "NOT SCORED",
       f"R6 9 scored tiles: M1 {r6['verdict']}, reading {r6['reading']}, no crash")
    # R7: re-derived equal and the identity
    ident = all(r["M1_rederived_equal"] and r["M1_clock_beside_rederived_equal"] for _, r in keep.values())
    ok(ident, "R7a in R1-R5 the reader re-derived M1 and the clock beside from the scorer's own tiles, equal field for field (it refuses otherwise)")
    idn = []
    for k, (_, r) in keep.items():
        I = r["identity"]
        both = I["point_below_0"] == I["abar_below_theta"]
        close = abs(I["mean_a2_minus_mean_b2"] - I["two_mean_delta_times_abar_minus_theta"]) < 1e-6
        idn.append((k, both, close, r["abar_delta_w"], r["theta_w"], r["M1"].get("point")))
    ok(all(b and c for _, b, c, *_ in idn), "R7b the identity in R1-R5 (M1's point below 0 exactly when abar_delta < theta; mean(a^2) - mean(b^2) = "
       "2 mean(delta)(abar_delta - theta)): " + "; ".join(f"{k} abar {a} theta {t} point {p}" for k, _, _, a, t, p in idn))
    # R8: refusals, through main() on files
    tmp = tempfile.mkdtemp(prefix="e175-m1read-")
    try:
        sc3 = keep["low"][0]
        p_ok = os.path.join(tmp, "results.json")
        json.dump({"score": sc3}, open(p_ok, "w"))
        o_ok = os.path.join(tmp, "m1-reading.json")
        rc0 = R.main([p_ok, "--out", o_ok])
        got = json.load(open(o_ok))
        ok(rc0 == 0 and got["reading"] == want["low"][2] and got["inputs_sha256"]["results"] == C.sha256_file(p_ok),
           f"R8a main() on a written results file: rc {rc0}, reading '{got['reading']}', the results' sha256 recorded")
        t1 = copy.deepcopy(sc3)
        t1["rules"]["E175-A2-M1"]["verdict"] = "NOT RESOLVED"
        p1 = os.path.join(tmp, "tampered-m1.json")
        json.dump({"score": t1}, open(p1, "w"))
        rc1 = R.main([p1])
        ok(rc1 == 2, f"R8b a results file whose M1 verdict was altered: refused, rc {rc1}")
        t2 = copy.deepcopy(sc3)
        t2["reported"]["E175-A2-M1_clock_beside"]["ci95"] = [0.0, 0.0]
        p2 = os.path.join(tmp, "tampered-clock.json")
        json.dump({"score": t2}, open(p2, "w"))
        rc2 = R.main([p2])
        ok(rc2 == 2, f"R8c a results file whose clock beside was altered: refused, rc {rc2}")
        p3 = os.path.join(tmp, "not-results.json")
        json.dump([1, 2, 3], open(p3, "w"))
        rc3 = R.main([p3])
        ok(rc3 == 3, f"R8d a file that is not the scorer's results: refused, rc {rc3}")
        p4 = os.path.join(tmp, "one-pass.json")
        json.dump({"score": {"note": "fewer than 2 counted passes: every rule NOT SCORED"}}, open(p4, "w"))
        o4 = os.path.join(tmp, "one-pass-reading.json")
        rc4 = R.main([p4, "--out", o4])
        ok(rc4 == 0 and json.load(open(o4))["reading"] == "NOT SCORED", f"R8e a score with fewer than 2 passes: NOT SCORED, rc {rc4}")
    finally:
        shutil.rmtree(tmp)
    n_ok = sum(1 for x, _ in RES if x)
    print(f"{'ALL PASS' if n_ok == len(RES) else 'FAILED'}: {n_ok} of {len(RES)}")
    return 0 if n_ok == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
