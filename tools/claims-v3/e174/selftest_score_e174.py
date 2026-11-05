#!/usr/bin/env python3
"""E174 (Q142(kg)): the scorer's self-test, before any E174 data. Desk only; it reads committed files and writes only temporary ones.

    python3 -B tools/claims-v3/e174/selftest_score_e174.py > tools/claims-v3/e174/selftest-score.txt

  S1  E170's committed session (pool 7 on this card, its registered reduction's cells in results.json): the zeros anchors' counted bursts give
      E170's committed score.anchors; e170_common.pred_card0 (the call predict_pool8_a2 makes on card 0) recomputed per tile with them equals
      E170's committed primary on all 39 scored tiles; the P8 card-0 engine's quantities reproduce E170's committed figures where the rules
      overlap (C0-W and C0-B's board rms and mean, C0-F's clock, the die rise under M9's law, M1's D errors); E170's own engines (seeds 170, 171,
      172, 1701) reproduce its committed lines and its M9-M6 interval. Then, in sample by construction (term c2 was fitted on this session):
      M10's k on the measured board against M9's, the C0-HK pair, and the 39 leave-one-tile-out residuals against heldout-m10.json's rms.
  S2  the P8 lines at E174's planned n (21) equal predictions-e174.json's, and at n 31 intervals-pool8.json's (C0-W, C0-F, C0-H1).
  S3  a made-up E174 session with known answers: C0-W, C0-B, C0-F and C0-H1 on designed errors; the rise at exactly M10's k: C0-HK BETTER, at M9's:
      WORSE; measured D = M10 carried's: C0-M1 BETTER; fewer than 2 counted passes of half A: every rule NOT SCORED; no zeros-anchor burst: every
      rule NOT SCORED; a C-excluded tile leaves the sets.
  S4  the registered refusals (E173's shared ones on E174's names): the C-log list, a dry session, a foreign anchor input, a run of a tile left
      out by name or not admitted.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
sys.path.insert(0, os.path.join(HERE, "..", "e165"))
import e174_common as C  # noqa: E402
import p8gov as G  # noqa: E402
import score_e174 as SC  # noqa: E402
import e165_common as C165  # noqa: E402

TOP = C.TOP
E170D = os.path.join(TOP, "docs/reports/data/2026-11-04-e170-blind7-card0")
RES = []


def ok(cond, what):
    RES.append((bool(cond), what))
    print(("PASS " if cond else "FAIL ") + what)


def s1(A):
    with open(os.path.join(E170D, "results.json")) as f:
        r = json.load(f)
    with open(os.path.join(TOP, "tools/claims-v3/e170/predictions-e170.json")) as f:
        P = json.load(f)
    cells, sc = r["cells"], r["score"]
    zl = {P["tiles"][n]["type"]: P["tiles"][n]["label"] for n in C165.ZEROS_ANCHORS}
    anchors, used = G.anchors_from(cells, zl)
    ok(anchors == sc["anchors"] and sorted(used) == sorted(zl.values()),
       f"S1a the zeros anchors' counted bursts give E170's committed score.anchors ({sum(len(v) for v in anchors.values())} reads), from the zeros anchors only")
    names = [n for n in P["scored"] if P["tiles"][n]["label"] in cells and cells[P["tiles"][n]["label"]]["n"] >= 2]
    cl = {n: cells[P["tiles"][n]["label"]] for n in names}
    pm, diff = {}, []
    for n in names:
        m9 = P["tiles"][n]["models"]["M9"]
        ds = [x for x in cl[n]["die_start_runs"] if x is not None] or None
        b = C.C170.pred_card0(m9["D600_a3_footing_w"], P["tiles"][n]["type"], anchors, ds, m9.get("D_band_hw", 0.0))
        pm[n] = b
        for k, v in sc["reported"]["tiles"][n]["primary"].items():
            if b.get(k) != v:
                diff.append(f"{n}.{k}")
    ok(len(names) == 39 and not diff, f"S1b e170_common.pred_card0 recomputed per tile equals E170's committed primary: {len(names)} tiles, {len(diff)} fields differ")
    ew = [cl[n]["burst_w"] - pm[n]["burst_board_w"] for n in names]
    em = [cl[n]["burst_mhz"] - pm[n]["burst_mhz"] for n in names]
    er = [cl[n]["rise_c"] - pm[n]["burst_die_rise_c"] for n in names]
    R = sc["rules"]
    b = G.fixed_mean_rms("P8-C0-B", ew, 8)
    ok(round(G.rms(ew), 4) == R["E170-W"]["rms"] and round(G.mean(ew), 4) == R["E170-W"]["mean"] and b["verdict"] == R["E170-B"]["verdict"] == "PASS",
       f"S1c the board errors reproduce E170-W and E170-B: rms {round(G.rms(ew), 4)}, mean {round(G.mean(ew), 4)}; C0-B's lines read PASS, as E170-B")
    ok(round(G.rms(em), 4) == R["E170-F"]["rms"] and round(G.mean(em), 4) == R["E170-F"]["mean"],
       f"S1d the clock errors reproduce E170-F: rms {round(G.rms(em), 4)}, mean {round(G.mean(em), 4)}")
    ok(round(G.rms(er), 4) == R["E170-H1"]["rms"] and round(G.mean(er), 4) == R["E170-H1"]["mean"],
       f"S1e the die-rise errors under M9's law reproduce E170-H1: rms {round(G.rms(er), 4)}, mean {round(G.mean(er), 4)}")
    ref = P["reference"]
    lw = [round(x, 4) for x in C.C170.boot_rms_range(ref["pinned_board_w_err"], len(ew), draws=20000, seed=170)]
    lf = [round(x, 4) for x in C.C170.boot_rms_range(ref["pinned_mhz_err"], len(em), draws=20000, seed=171)]
    lh = [round(x, 4) for x in C.C170.boot_rms_range(ref["heat_rise_err_c"], len(er), draws=20000, seed=172)]
    ok(lw == R["E170-W"]["range"] and lf == R["E170-F"]["range"] and lh == R["E170-H1"]["range"],
       f"S1f E170's own engine (seeds 170-172) reproduces its committed lines W {lw}, F {lf}, H1 {lh}")
    p1 = [n for n in names if n in set(P["priority1_new"]) and cl[n].get("D_w") is not None]
    m6 = {n: C.C170.pred_card0(P["tiles"][n]["models"]["M6"]["D600_a3_footing_w"], P["tiles"][n]["type"], anchors,
                               [x for x in cl[n]["die_start_runs"] if x is not None] or None, 0.0) for n in p1}
    a = [cl[n]["D_w"] - pm[n]["burst_D_w"] for n in p1]
    bb = [cl[n]["D_w"] - m6[n]["burst_D_w"] for n in p1]
    d = C.C170.paired_rms_diff(a, bb, draws=20000, seed=1701)
    ok(len(p1) == R["E170-M1"]["n"] and round(d["point"], 4) == R["E170-M1"]["d"] and [round(x, 4) for x in d["ci95"]] == R["E170-M1"]["ci95"],
       f"S1g E170's paired engine (seed 1701) reproduces E170-M1 on the D errors: n {len(p1)}, d {round(d['point'], 4)}, {[round(x, 4) for x in d['ci95']]}")
    pinfo = G.paired("P8-C0-M1", a, bb, 10, A)
    print(f"     information: P8's paired engine on E170's M9-M6 D errors: {json.dumps({k: pinfo.get(k) for k in ('n', 'point', 'ci95', 'verdict')})}")
    kM10, kM9, P0 = SC.heat_ks(A)
    hk = G.paired("P8-C0-HK", [cl[n]["rise_c"] - kM10 * (cl[n]["burst_w"] - P0) for n in names], [cl[n]["rise_c"] - kM9 * (cl[n]["burst_w"] - P0) for n in names], 8, A)
    ok(hk["verdict"] == "BETTER", f"S1h in sample (c2 was fitted on E170): C0-HK's pair on E170's 39 tiles reads {hk['verdict']} {hk['ci95']} (k {kM10} against {kM9})")
    band = A.c0_band()
    with open(os.path.join(TOP, "docs/reports/data/2026-11-04-q142m-m10/heldout-m10.json")) as f:
        hc = json.load(f)["heat_c2_card0_burst"]
    ok(round(band["loto_rms_c"], 4) == hc["loto"]["rms_c"] and band["n"] == 39, f"S1i C0-H1's reference: 39 residuals, rms {round(band['loto_rms_c'], 4)} (heldout-m10.json's {hc['loto']['rms_c']})")


def s2(A, P):
    refs = A.e165_refs()
    band = A.c0_band()
    L = P["lines"]
    got = {"P8-C0-W": A.P().boot_range(refs["pin_w"], 21, "P8-C0-W", "rms"), "P8-C0-F": A.P().boot_range(refs["pin_mhz"], 21, "P8-C0-F", "rms"),
           "P8-C0-H1": A.P().boot_range(band["residuals_c"], 21, "P8-C0-H1", "rms")}
    ok(all(got[k] == L[k]["range_95"] for k in got), "S2a the P8 lines at n 21 equal predictions-e174.json's " + json.dumps({k: [round(x, 3) for x in v] for k, v in got.items()}))
    with open(os.path.join(TOP, C.INTERVALS_REL)) as f:
        iv = json.load(f)["cards"]["aifoundry1c0"]["rules"]
    g31 = {"P8-C0-W": A.P().boot_range(refs["pin_w"], 31, "P8-C0-W", "rms"), "P8-C0-F": A.P().boot_range(refs["pin_mhz"], 31, "P8-C0-F", "rms"),
           "P8-C0-H1": A.P().boot_range(band["residuals_c"], 31, "P8-C0-H1", "rms")}
    ok(all(g31[k] == iv[k]["range_95"] for k in g31), "S2b the same engine at n 31 gives intervals-pool8.json's committed card-0 lines")


def synth(P, A, pred_c0, mode, passes=(1, 2, 3)):
    cells = {}
    zw = {"fp32": 29.3, "fp16": 28.8, "int8": 30.2}
    np_ = len(passes)
    for nm in C.ZEROS_ANCHORS:
        t = P["tiles"][nm]
        cells[t["label"]] = {"label": t["label"], "passes": list(passes), "n": np_, "burst_mhz_runs": [800.0] * np_, "burst_w_runs": [zw[t["type"]]] * np_,
                             "die_start_runs": [54] * np_, "rise_runs": [2.3] * np_, "burst_mhz": 800.0, "burst_w": zw[t["type"]], "rise_c": 2.3, "name": nm,
                             "type": t["type"], "peak_w_runs": [31.0] * np_, "peak_w": 31.0, "D_w": 0.0}
    for nm in P["tiles"]:
        if nm in C.ZEROS_ANCHORS:
            continue
        t = P["tiles"][nm]
        ps = list(passes) if t["tier"] == "A" else [4, 5, 6]
        cells[t["label"]] = {"label": t["label"], "passes": ps, "n": len(ps), "burst_mhz_runs": [0.0] * len(ps), "burst_w_runs": [0.0] * len(ps),
                             "die_start_runs": [53, 54, 55][:len(ps)], "rise_runs": [0.0] * len(ps), "name": nm, "type": t["type"],
                             "peak_w_runs": [50.0] * len(ps), "peak_w": 50.0}
    pm10, pm9, _ = SC.predictions(A, pred_c0, cells, P)
    kM10, kM9, P0 = SC.heat_ks(A)
    for i, nm in enumerate(P["tiles"]):
        if nm in C.ZEROS_ANCHORS:
            continue
        c = cells[P["tiles"][nm]["label"]]
        base = pm9 if mode == "m9" else pm10
        ew = {"good": (0.4 if i % 2 else -0.2), "m10": 0.0, "m9": 0.0, "k10": 0.0, "k9": 0.0}[mode]
        c["burst_w"] = base[nm]["burst_board_w"] + ew
        c["burst_mhz"] = base[nm]["burst_mhz"] + (1.5 if i % 2 else -1.5)
        c["D_w"] = base[nm]["burst_D_w"] + ew
        if mode == "k10":
            c["rise_c"] = kM10 * (c["burst_w"] - P0)
        elif mode == "k9":
            c["rise_c"] = kM9 * (c["burst_w"] - P0)
        else:
            c["rise_c"] = base[nm]["burst_die_rise_c"] + (0.2 if i % 2 else -0.2)
    return cells, pm10


def s3(A, P, pred_c0):
    cells, pm10 = synth(P, A, pred_c0, "good")
    sc = SC.score(cells, P, A, pred_c0)
    R = sc["rules"]
    ok(sc["tiles_scored"] == 21, f"S3a the made-up session scores 21 tiles: {sc['tiles_scored']}")
    ok(R["P8-C0-W"]["verdict"] == "PASS" and R["P8-C0-B"]["verdict"] == "PASS" and R["P8-C0-F"]["verdict"] == "PASS" and R["P8-C0-H1"]["verdict"] == "PASS",
       f"S3b designed errors: C0-W {R['P8-C0-W']['rms']} W {R['P8-C0-W']['verdict']}, C0-B mean {R['P8-C0-B']['mean']} {R['P8-C0-B']['verdict']}, "
       f"C0-F {R['P8-C0-F']['rms']} MHz {R['P8-C0-F']['verdict']}, C0-H1 {R['P8-C0-H1']['rms']} C {R['P8-C0-H1']['verdict']}")
    ok(R["P8-HM"]["verdict"].startswith("NOT SCORED"), "S3c HM NOT SCORED (no hold)")
    c10, _ = synth(P, A, pred_c0, "m10")
    c9, _ = synth(P, A, pred_c0, "m9")
    m10 = SC.score(c10, P, A, pred_c0)["rules"]["P8-C0-M1"]
    m9 = SC.score(c9, P, A, pred_c0)["rules"]["P8-C0-M1"]
    ok(m10["verdict"] == "BETTER" and m9["verdict"] == "WORSE", f"S3d measured D = M10 carried's: C0-M1 {m10['verdict']}; = M9 carried's: {m9['verdict']}")
    k10, _ = synth(P, A, pred_c0, "k10")
    k9, _ = synth(P, A, pred_c0, "k9")
    h10 = SC.score(k10, P, A, pred_c0)["rules"]["P8-C0-HK"]
    h9 = SC.score(k9, P, A, pred_c0)["rules"]["P8-C0-HK"]
    ok(h10["verdict"] == "BETTER" and h9["verdict"] == "WORSE", f"S3e the rise at exactly M10's k: C0-HK {h10['verdict']}; at M9's: {h9['verdict']}")
    rows = [{"pass": 1, "counted": True}, {"pass": 4, "counted": True}]
    res = SC.scoring([dict(m, label="b8-x", run="r", dry=True, c_pass=True, complete=True, burst_mhz=800, burst_w=40, die_start=54, die_max=56, rise_c=2,
                           c_w=None, peak_w=40, idx=0, session="s1", c_verdicts={}, c_lines=0, budget_stop=False) for m in rows], P, A, pred_c0, "counted")
    ok("note" in res["score"] and "half A" in res["score"]["note"], f"S3f fewer than 2 counted passes of half A: {res['score'].get('note')}")
    nz = {k: v for k, v in cells.items() if C.name_of(k) not in C.ZEROS_ANCHORS}
    s0 = SC.score(nz, P, A, pred_c0)
    ok("note" in s0["rules"], f"S3g no zeros-anchor burst: {s0['rules'].get('note')}")
    ex = SC.score(cells, P, A, pred_c0, excl={P["scored"][0]: [{"run": "x"}]})
    ok(ex["tiles_scored"] == 20 and P["scored"][0] in ex["left_out_c"], "S3h a tile with a launch not PASS leaves every scored set (20 scored)")


def s4(A, P):
    tmp = tempfile.mkdtemp(prefix="e174-selftest-")
    try:
        q = os.path.join(tmp, "runs")
        for s, wl in (("stoptest-die", 0), ("stoptest-board", 1), ("smoke", 2), ("s1", 126)):
            os.makedirs(os.path.join(q, s))
            with open(os.path.join(q, s, "launches.jsonl"), "w") as f:
                for i in range(wl):
                    f.write(json.dumps({"role": "work"}) + "\n")
            with open(os.path.join(q, s, "session.json"), "w") as f:
                json.dump({"dry": False}, f)
        with open(os.path.join(q, "queue.jsonl"), "w") as f:
            for s in ("stoptest-die", "stoptest-board", "smoke", "s1"):
                f.write(json.dumps({"kind": "session_start", "name": s}) + "\n")
        okc, miss, req, _ = G.check_c_coverage(q, ["d/ccheck-s1.json"], C.C_LOG_SESSIONS)
        ok(not okc and sorted(miss) == ["smoke", "stoptest-board"] and sorted(req) == ["s1", "smoke", "stoptest-board"],
           f"S4a E170's queue order (die test, board test, smoke, s1): required {req}; with only s1's check, missing {miss}")
        zl = {P["tiles"][n]["type"]: P["tiles"][n]["label"] for n in C.ZEROS_ANCHORS}
        try:
            G.refuse_foreign_anchor(list(zl.values()) + ["b8-" + P["scored"][0]], zl)
            r = False
        except SystemExit:
            r = True
        ok(r, "S4b a tile other than the zeros anchors reaching the anchors input is refused")
        lo = sorted(P["left_out"])[0]
        ok(SC.stray_left_out([{"label": C.label_of(lo)}], P) is not None and SC.stray_left_out([{"label": "b8-not.a.tile"}], P) is not None
           and SC.stray_left_out([{"label": C.label_of(P["scored"][0])}], P) is None, "S4c a run of a tile left out by name, or not admitted, is refused; an admitted one is not")
    finally:
        shutil.rmtree(tmp)


def main():
    A = C.a2p()
    P = SC.load_pred()
    with open(os.path.join(TOP, C.PRED_REL)) as f:
        pred_c0 = json.load(f)
    print(f"E174 scorer self-test: score_e174.py {C.sha256_file(SC.__file__)[:16]}, p8gov.py {C.sha256_file(G.__file__)[:16]}, "
          f"predictions-e174.json {C.sha256_file(SC.PRED_PATH)[:16]}")
    s1(A)
    s2(A, P)
    s3(A, P, pred_c0)
    s4(A, P)
    n_ok = sum(1 for x, _ in RES if x)
    print(f"{'ALL PASS' if n_ok == len(RES) else 'FAILED'}: {n_ok} of {len(RES)}")
    return 0 if n_ok == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
