#!/usr/bin/env python3
"""E175 (Q143(g)): the scorer's self-test, before any E175 data. Desk only; it reads committed files and writes only temporary ones. E173's
selftest_score_e173.py (lab 5a2a9ba0) with E175's rules, sets and reported arms; never any E173 datum.

    python3 -B tools/claims-v3/e175/selftest_score_e175.py > tools/claims-v3/e175/selftest-score.txt

  S1  E165's committed session (pool 7 on this card, its registered reduction's cells in results.json), where the rules overlap: the session's
      zeros-anchor reads, taken from the zeros anchors' counted bursts only (p8gov.anchors_from), equal E165's committed score.anchors; M9's part
      recomputed per tile through the frozen burst() with them and each tile's die starts equals E165's committed primary on all 52 scored tiles,
      field for field; and E175's rule engine (the fixed lines and R2's form with E175's ids, boot_rule, paired) on those errors reproduces
      E165's committed figures (G's and Bg's governed lines, Bp's pinned lines, R2 PASS as E165-R2 read; F1/F2/W1/W2's and H1's rms; 12
      governed, 40 pinned, 52 in all). E165's own engines reproduce its committed lines, so the errors are E165's own; E175's lines and GS on
      them are printed for information.
  S2  E175's lines at the planned n (p8gov.boot_rule through predict_pool8.boot_range, E175's rule ids) equal predictions-e175.json's and the
      registration's design-power-e175.json (F1, F2, W1, W2, H1).
  S3  a made-up E175 session with known answers (cells; the predictions recomputed by the scorer's own call; measured = prediction + designed
      errors): G, Bg, Bp, R2 PASS, F1/W1/F2/W2/H1 PASS; a +3 MHz governed clock level: G FAIL, R2 FAIL; a +0.7 W pinned level: Bp FAIL, R2 FAIL;
      measured = M10's prediction: M1 BETTER; = M9's: M1 WORSE; a designed slope of +0.2 MHz per MHz of predicted clock: GS reads it, rising; a
      C-excluded tile leaves the sets; fewer than 8 governed: G, Bg, F1, W1 NOT SCORED and R2 NOT SCORED; no scored tile: every rule NOT
      SCORED, no crash.
  S4  the registered refusals: a session that ran a work launch with no check of C given (exit 5's test), a dry session needing none, a tile
      other than the zeros anchors reaching the anchors input, a protocol not the kit's, a tampered order entry, a run not its protocol's at its
      index, a run of a tile left out by name (on a copy whose left_out names one: E175 leaves none).
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
import e165_common as C165  # noqa: E402
import score_e165 as S165  # noqa: E402

TOP = C.TOP
E165D = os.path.join(TOP, "docs/reports/data/2026-11-04-e165-blind7-aifoundry2")
RES = []


def ok(cond, what):
    RES.append((bool(cond), what))
    print(("PASS " if cond else "FAIL ") + what)


def s1(A):
    with open(os.path.join(E165D, "results.json")) as f:
        r = json.load(f)
    with open(os.path.join(TOP, "tools/claims-v3/e165/predictions-e165.json")) as f:
        P = json.load(f)
    cells, sc = r["cells"], r["score"]
    zl = {P["tiles"][n]["type"]: P["tiles"][n]["label"] for n in C165.ZEROS_ANCHORS}
    anchors, used = G.anchors_from(cells, zl)
    ok(anchors == sc["anchors"], f"S1a the zeros anchors' counted bursts give E165's committed score.anchors ({sum(len(v) for v in anchors.values())} reads)")
    ok(sorted(used) == sorted(zl.values()), "S1b only the three zeros anchors reached the anchors input")
    tiles = {c["name"]: c for c in cells.values() if c.get("name") and P["tiles"][c["name"]]["scored"] and c["n"] >= 2}
    diff, n = [], 0
    pm = {}
    for nm, c in tiles.items():
        m9 = P["tiles"][nm]["models"]["M9"]
        b = C165.primary(m9["D600_a3_footing_w"], P["tiles"][nm]["type"], anchors, [x for x in c["die_start_runs"] if x is not None] or None, m9["D_band_hw"])
        pm[nm] = b
        want = sc["reported"]["tiles"][nm]["primary"]
        for k, v in want.items():
            if b.get(k) != v:
                diff.append(f"{nm}.{k}")
        n += 1
    ok(n == 52 and not diff, f"S1c M9's part recomputed per tile equals E165's committed primary: {n} tiles, {len(diff)} fields differ")
    gov = sorted(x for x in tiles if P["tiles"][x]["group"] == "governed")
    pin = sorted(x for x in tiles if P["tiles"][x]["group"] == "pinned")
    alln = sorted(tiles)

    def e(names, mk, pk):
        return [tiles[x][mk] - pm[x][pk] for x in names]
    eg_m, eg_w, ep_w, ep_m = e(gov, "burst_mhz", "burst_mhz"), e(gov, "burst_w", "burst_board_w"), e(pin, "burst_w", "burst_board_w"), e(pin, "burst_mhz", "burst_mhz")
    er = e(alln, "rise_c", "burst_die_rise_c")
    R2 = sc["rules"]["E165-R2"]
    g = SC.relabel(G.fixed_G(eg_m, 8), "E175-A2-G")
    bg = G.fixed_mean("E175-A2-Bg", eg_w, 8)
    bp = G.fixed_mean_rms("E175-A2-Bp", ep_w, 8)
    r2 = SC.r2(g, bg, bp)
    ok((len(gov), len(pin), len(alln)) == (12, 40, 52), "S1d the sets: 12 governed, 40 pinned, 52 scored (E165's)")
    ok(round(g["rms"], 3) == R2["G"]["rms"] and round(g["mean"], 3) == R2["G"]["mean"] and g["verdict"] == "PASS",
       f"S1e A2-G's lines on E165's governed clock: rms {g['rms']}, mean {g['mean']} (committed {R2['G']['rms']}, {R2['G']['mean']}): both lines hold, as E165's")
    ok(round(bg["mean"], 3) == R2["Bg"]["mean"] and bg["verdict"] == "PASS",
       f"S1f A2-Bg's line on E165's governed board: mean {bg['mean']} (committed {R2['Bg']['mean']}): PASS (E165's FAIL was its resolution test against M7, not a P8 line)")
    ok(round(bp["mean"], 3) == R2["Bp"]["mean"] and round(bp["rms"], 3) == R2["Bp"]["rms"] and bp["verdict"] == "PASS",
       f"S1g A2-Bp's lines on E165's pinned board: mean {bp['mean']}, rms {bp['rms']} (committed {R2['Bp']['mean']}, {R2['Bp']['rms']}): PASS")
    ok(r2["verdict"] == "PASS" and r2["rule"] == "E175-A2-R2" and g["verdict"] == bg["verdict"] == bp["verdict"] == "PASS",
       f"S1g2 E175-A2-R2's form on E165's three P8 lines reads {r2['verdict']} (E165-R2's own committed verdict, which adds its resolution test "
       f"against M7, reads {R2.get('verdict')})")
    rr = sc["rules"]
    ok(all(round(G.rms(x), 3) == rr[k]["rms"] for k, x in (("E165-F1", eg_m), ("E165-F2", ep_m), ("E165-W1", eg_w), ("E165-W2", ep_w), ("E165-H1", er))),
       f"S1h F1/F2/W1/W2/H1's rms reproduce E165's committed {[rr[k]['rms'] for k in ('E165-F1', 'E165-F2', 'E165-W1', 'E165-W2', 'E165-H1')]}")
    ref = P["reference"]
    lines = {k: [round(x, 3) for x in C165.boot_rms_range(refe, len(x_), seed=165)] for k, x_, refe in
             (("E165-F1", eg_m, ref["e2e"]["governed"]["mhz_err"]), ("E165-F2", ep_m, ref["e2e"]["pinned"]["mhz_err"]),
              ("E165-W1", eg_w, ref["e2e"]["governed"]["w_err"]), ("E165-W2", ep_w, ref["e2e"]["pinned"]["w_err"]), ("E165-H1", er, ref["heat"]["rise_err_c"]))}
    ok(all(lines[k] == rr[k]["range_2.5_97.5"] for k in lines), f"S1i E165's own engine (seed 165) reproduces its committed lines: {lines}")
    m7 = {x: P["tiles"][x]["models"]["M7"] for x in alln}
    pr7 = C165.paired_rms_diff(eg_m, [tiles[x]["burst_mhz"] - m7[x]["burst_mhz"] for x in gov])
    ok(pr7["ci95"] == R2["G"]["vs_M7"]["ci95"], f"S1j E165's paired engine (seed 1651) reproduces its committed G vs M7 interval {[round(v, 3) for v in pr7['ci95']]}")
    refs = A.e165_refs()
    info = {"E175-A2-F1 on E165's 12 governed clock errors": G.boot_rule("E175-A2-F1", eg_m, refs["gov_mhz"], 8, A),
            "E175-A2-W1 on E165's governed board": G.boot_rule("E175-A2-W1", eg_w, refs["gov_w"], 8, A),
            "E175-A2-F2 on E165's 40 pinned clock errors": G.boot_rule("E175-A2-F2", ep_m, refs["pin_mhz"], 8, A),
            "E175-A2-W2 on E165's pinned board": G.boot_rule("E175-A2-W2", ep_w, refs["pin_w"], 8, A),
            "E175-A2-H1 on E165's die rise": G.boot_rule("E175-A2-H1", er, refs["heat_c"], 10, A),
            "E175 paired engine, M9 against M7 on E165's board": G.paired("E175-A2-M1", e(alln, "burst_w", "burst_board_w"),
                                                                          [tiles[x]["burst_w"] - m7[x]["burst_board_w"] for x in alln], 10, A),
            "E175-GS on E165's governed clock errors": SC.slope_gs([pm[x]["burst_mhz"] for x in gov], eg_m)}
    for k, v in info.items():
        print(f"     information: {k}: {json.dumps({kk: v.get(kk) for kk in ('n', 'rms', 'range_95', 'point', 'ci95', 'verdict', 'slope_mhz_per_mhz', 'resolved')})}")
    ok(info["E175-A2-F2 on E165's 40 pinned clock errors"]["verdict"] == "FAIL" and info["E175-A2-W2 on E165's pinned board"]["verdict"] == "PASS"
       and info["E175-A2-F1 on E165's 12 governed clock errors"]["verdict"] == "PASS" and info["E175-A2-W1 on E165's governed board"]["verdict"] == "PASS",
       "S1k on E175's engines E165's governed clock and board PASS (as E165-F1, E165-W1), its pinned clock still FAILs and its pinned board PASSes (as E165-F2, E165-W2)")


def s2(A, P):
    refs = A.e165_refs()
    L = P["lines"]
    ng, npn, na = len(P["sets"]["governed"]), len(P["sets"]["pinned"]), len(P["sets"]["scored"])
    got = {"E175-A2-F1": A.P().boot_range(refs["gov_mhz"], ng, "E175-A2-F1", "rms"), "E175-A2-F2": A.P().boot_range(refs["pin_mhz"], npn, "E175-A2-F2", "rms"),
           "E175-A2-W1": A.P().boot_range(refs["gov_w"], ng, "E175-A2-W1", "rms"), "E175-A2-W2": A.P().boot_range(refs["pin_w"], npn, "E175-A2-W2", "rms"),
           "E175-A2-H1": A.P().boot_range(refs["heat_c"], na, "E175-A2-H1", "rms")}
    ok(all(got[k] == L[k]["range_95"] for k in got), "S2 E175's lines at the planned n equal predictions-e175.json's "
       + json.dumps({k: [round(x, 3) for x in v] for k, v in got.items()}))
    with open(os.path.join(TOP, "tools/claims-v3/e175/design-power-e175.json")) as f:
        dp = json.load(f)["lines"]
    same = {k: (dp[k][str(n)]["range_95"] == got[k]) for k, n in (("E175-A2-F1", ng), ("E175-A2-W1", ng), ("E175-A2-F2", npn), ("E175-A2-W2", npn),
                                                                     ("E175-A2-H1", na)) if str(n) in dp.get(k, {})}
    ok(same and all(same.values()), f"S2a and the registration's design-power-e175.json at the same n: {same}")
    b = G.boot_rule("E175-A2-W2", [0.6] * npn, refs["pin_w"], 8, A)
    ok(b["range_95"] == L["E175-A2-W2"]["range_95"] and b["seed"] == L["E175-A2-W2"]["seed"], f"S2b p8gov.boot_rule reads the same line and seed at n {npn}")


def synth_cells(P, A, pred_a2, mode, excl=None):
    """cells for every run tile of E175 with 3 passes; the zeros anchors at made-up reads; every other tile's measured values = the scorer's own
    recomputed prediction + a designed error (mode)"""
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
    pin = P["sets"]["pinned"]
    for i, nm in enumerate(P["run"]):
        if nm in C.ZEROS_ANCHORS:
            continue
        c = cells[P["tiles"][nm]["label"]]
        base = pm9 if mode == "m9" else pm10
        ew = {"good": (0.3 if i % 2 else -0.1), "level": 0.7, "m10": 0.0, "m9": 0.0, "glevel": 0.0, "slope": 0.0}[mode]
        em = {"good": (1.0 if i % 2 else -1.0), "level": 1.0, "m10": 0.0, "m9": 0.0, "glevel": (3.0 if nm not in pin else 0.0),
              "slope": (0.2 * (base[nm]["burst_mhz"] - 760.0) if nm not in pin else 0.0)}[mode]
        eh = {"good": (0.3 if i % 2 else -0.3), "level": 0.3, "m10": 0.0, "m9": 0.0, "glevel": 0.0, "slope": 0.0}[mode]
        if mode == "good" and nm not in pin:
            ew = 0.0
        if mode == "level" and nm not in pin:
            ew = 0.0
        c["burst_w"] = base[nm]["burst_board_w"] + ew
        c["burst_mhz"] = base[nm]["burst_mhz"] + em
        c["rise_c"] = base[nm]["burst_die_rise_c"] + eh
        c["burst_w_runs"], c["burst_mhz_runs"], c["rise_runs"] = [c["burst_w"]] * 3, [c["burst_mhz"]] * 3, [c["rise_c"]] * 3
    return cells, pm10, pm9


def s3(A, P, pred_a2):
    cells, pm10, _ = synth_cells(P, A, pred_a2, "good")
    sc = SC.score(cells, P, A, pred_a2)
    R = sc["rules"]
    pin = P["sets"]["pinned"]
    ng, npn = len(P["sets"]["governed"]), len(pin)
    ew = [cells[P["tiles"][n]["label"]]["burst_w"] - pm10[n]["burst_board_w"] for n in pin]
    ok(sc["tiles_scored"] == ng + npn and len(sc["governed"]) == ng and len(sc["pinned"]) == npn,
       f"S3a the made-up session scores {ng + npn} tiles: {ng} governed, {npn} pinned")
    ok(abs(R["E175-A2-Bp"]["mean"] - G.mean(ew)) < 1e-4 and R["E175-A2-Bp"]["verdict"] == "PASS",
       f"S3b Bp reads the designed pinned errors (mean {R['E175-A2-Bp']['mean']}, rms {R['E175-A2-Bp']['rms']}): PASS")
    ok(all(R[k]["verdict"] == "PASS" for k in ("E175-A2-G", "E175-A2-Bg", "E175-A2-F1", "E175-A2-W1", "E175-A2-F2", "E175-A2-W2", "E175-A2-H1")),
       "S3c G (" + str(R["E175-A2-G"]["rms"]) + " MHz rms), Bg, F1, W1, F2, W2 and H1 PASS on the designed errors")
    ok(R["E175-A2-R2"]["verdict"] == "PASS" and set(R["E175-A2-R2"]["components"]) == {"E175-A2-G", "E175-A2-Bg", "E175-A2-Bp"},
       "S3d E175-A2-R2 reads PASS when G, Bg and Bp PASS (rank 2 can read PASS on E175)")
    cg, _, _ = synth_cells(P, A, pred_a2, "glevel")
    R = SC.score(cg, P, A, pred_a2)["rules"]
    ok(R["E175-A2-G"]["verdict"] == "FAIL" and not R["E175-A2-G"]["mean_within_line"] and R["E175-A2-R2"]["verdict"] == "FAIL",
       f"S3e a +3 MHz governed clock level: G {R['E175-A2-G']['verdict']} (mean {R['E175-A2-G']['mean']}), R2 {R['E175-A2-R2']['verdict']}")
    cl, _, _ = synth_cells(P, A, pred_a2, "level")
    R = SC.score(cl, P, A, pred_a2)["rules"]
    ok(R["E175-A2-Bp"]["verdict"].startswith("FAIL") and R["E175-A2-R2"]["verdict"] == "FAIL",
       f"S3f a +0.7 W pinned level: Bp {R['E175-A2-Bp']['verdict']}, R2 {R['E175-A2-R2']['verdict']}")
    c10, _, _ = synth_cells(P, A, pred_a2, "m10")
    R10 = SC.score(c10, P, A, pred_a2)["rules"]["E175-A2-M1"]
    c9, _, _ = synth_cells(P, A, pred_a2, "m9")
    R9 = SC.score(c9, P, A, pred_a2)["rules"]["E175-A2-M1"]
    ok(R10["verdict"] == "BETTER" and R9["verdict"] == "WORSE", f"S3g measured = M10 carried: M1 {R10['verdict']} {R10['ci95']}; = M9's part: {R9['verdict']} {R9['ci95']}")
    cs, _, _ = synth_cells(P, A, pred_a2, "slope")
    gs = SC.score(cs, P, A, pred_a2)["reported"]["E175-GS"]
    ok(gs["slope_mhz_per_mhz"] is not None and abs(gs["slope_mhz_per_mhz"] - 0.2) < 1e-3 and gs["resolved"] == "rising",
       f"S3h a designed slope of +0.2 MHz per MHz: GS reads {gs['slope_mhz_per_mhz']} {gs['range_95']}, {gs['resolved']}")
    ex = SC.score(cells, P, A, pred_a2, excl={pin[0]: [{"run": "x"}]})
    ok(ex["tiles_scored"] == ng + npn - 1 and pin[0] in ex["left_out_c"], f"S3i a tile with a launch not PASS leaves every scored set ({ng + npn - 1} scored)")
    few = {k: v for k, v in cells.items() if C.name_of(k) not in P["sets"]["governed"][7:]}
    rf = SC.score(few, P, A, pred_a2)["rules"]
    ok(all(rf[k]["verdict"].startswith("NOT SCORED") for k in ("E175-A2-G", "E175-A2-Bg", "E175-A2-F1", "E175-A2-W1"))
       and rf["E175-A2-R2"]["verdict"] == "NOT SCORED" and rf["E175-A2-Bp"]["verdict"] == "PASS",
       "S3j with 7 governed tiles (minimum 8): G, Bg, F1 and W1 NOT SCORED, R2 NOT SCORED, Bp still PASS")
    zc = {k: v for k, v in cells.items() if C.name_of(k) in C.ZEROS_ANCHORS}
    e0 = SC.score(zc, P, A, pred_a2)
    ok(e0["tiles_scored"] == 0 and all(v["verdict"].startswith("NOT SCORED") for k, v in e0["rules"].items()),
       "S3k no scored tile: every rule NOT SCORED, no crash")


def s4(A, P):
    tmp = tempfile.mkdtemp(prefix="e175-selftest-")
    try:
        q = os.path.join(tmp, "runs")
        for s, wl, dry in (("smoke", 3, False), ("stoptest-board", 1, False), ("stoptest-die", 0, False), ("s1", 145, False)):
            os.makedirs(os.path.join(q, s))
            with open(os.path.join(q, s, "launches.jsonl"), "w") as f:
                for i in range(wl):
                    f.write(json.dumps({"role": "work", "run": f"r{i}"}) + "\n")
            with open(os.path.join(q, s, "session.json"), "w") as f:
                json.dump({"dry": dry}, f)
            if wl:
                open(os.path.join(q, s, "c-log.jsonl"), "w").close()
        with open(os.path.join(q, "queue.jsonl"), "w") as f:
            for s in ("smoke", "stoptest-board", "stoptest-die", "s1"):
                f.write(json.dumps({"kind": "session_start", "name": s}) + "\n")
        okc, miss, req, _ = G.check_c_coverage(q, ["x/ccheck-s1.json"], C.C_LOG_SESSIONS)
        ok(not okc and miss == ["smoke", "stoptest-board"] and req == ["smoke", "stoptest-board", "s1"],
           f"S4a the C-log list: required {req}; with only s1's check given, missing {miss}: refused (the scorer's exit 5)")
        okc, miss, _, _ = G.check_c_coverage(q, ["a/ccheck-smoke.json", "a/ccheck-stoptest-board.json", "a/ccheck-s1.json.gz"], C.C_LOG_SESSIONS)
        ok(okc and not miss, "S4b with the three checks given (one gzipped) nothing is missing")
        os.makedirs(os.path.join(q, "s2"))
        with open(os.path.join(q, "s2", "launches.jsonl"), "w") as f:
            f.write(json.dumps({"role": "work"}) + "\n")
        with open(os.path.join(q, "queue.jsonl"), "a") as f:
            f.write(json.dumps({"kind": "session_start", "name": "s2"}) + "\n")
        okc, miss, req, _ = G.check_c_coverage(q, ["a/ccheck-smoke.json", "a/ccheck-stoptest-board.json", "a/ccheck-s1.json"], C.C_LOG_SESSIONS)
        ok(not okc and miss == ["s2"], f"S4c a resume s2 that ran a work launch must carry a C log too: missing {miss}")
        d = os.path.join(tmp, "dry")
        os.makedirs(os.path.join(d, "s1"))
        with open(os.path.join(d, "s1", "launches.jsonl"), "w") as f:
            f.write(json.dumps({"role": "work"}) + "\n")
        with open(os.path.join(d, "s1", "session.json"), "w") as f:
            json.dump({"dry": True}, f)
        okc, miss, req, _ = G.check_c_coverage(d, [], C.C_LOG_SESSIONS)
        ok(okc and req == [], "S4d a dry session (the toy card writes no C log) needs none")
        zl = {P["tiles"][n]["type"]: P["tiles"][n]["label"] for n in C.ZEROS_ANCHORS}
        try:
            G.refuse_foreign_anchor(list(zl.values()) + [P["tiles"][P["sets"]["pinned"][0]]["label"]], zl)
            r = False
        except SystemExit:
            r = True
        ok(r, "S4e a tile other than the zeros anchors reaching the anchors input is refused")
        kit = os.path.join(tmp, "kit")
        os.makedirs(kit)
        proto = {"order_source": "order", "order_entries": [{"idx": i, "registered_idx": o["idx"], "pass": o["pass"], "label": o["label"]}
                                                            for i, o in enumerate(P["order"])]}
        with open(os.path.join(kit, "protocol.json"), "w") as f:
            json.dump(proto, f)
        sha = C.sha256_file(os.path.join(kit, "protocol.json"))
        rd = os.path.join(tmp, "sess")
        os.makedirs(rd)
        with open(os.path.join(rd, "e175.json"), "w") as f:
            json.dump({"protocol": "protocol.json", "protocol_sha256": sha}, f)
        orders = {"order": P["order"], "dry_order": P["dry_order"]}
        m, _ = G.protocol_map(kit, rd, "e175.json", orders, SC.PROTOCOLS)
        f_ = G.pass_of_map(m)
        ok(len(m) == len(P["order"]) == 145 and f_({"idx": 60, "label": P["order"][60]["label"]}) == P["order"][60]["pass"],
           "S4f the kit's protocol maps 145 runs to the registered order")
        for what, run in (("a run not its protocol's at its index", {"idx": 60, "label": P["order"][61]["label"], "run": "x"}),):
            try:
                f_(run)
                r = False
            except SystemExit:
                r = True
            ok(r, f"S4g {what} is refused")
        with open(os.path.join(rd, "e175.json"), "w") as f:
            json.dump({"protocol": "protocol-other.json", "protocol_sha256": sha}, f)
        try:
            G.protocol_map(kit, rd, "e175.json", orders, SC.PROTOCOLS)
            r = False
        except SystemExit:
            r = True
        ok(r, "S4h a protocol not one of the kit's is refused")
        bad = copy.deepcopy(proto)
        bad["order_entries"][5]["label"] = bad["order_entries"][6]["label"]
        with open(os.path.join(kit, "protocol.json"), "w") as f:
            json.dump(bad, f)
        with open(os.path.join(rd, "e175.json"), "w") as f:
            json.dump({"protocol": "protocol.json", "protocol_sha256": C.sha256_file(os.path.join(kit, "protocol.json"))}, f)
        try:
            G.protocol_map(kit, rd, "e175.json", orders, SC.PROTOCOLS)
            r = False
        except SystemExit:
            r = True
        ok(r, "S4i a protocol whose entry is not the registered order's run is refused")
        with open(os.path.join(rd, "e175.json"), "w") as f:
            json.dump({"protocol": "protocol.json", "protocol_sha256": "0" * 64}, f)
        try:
            G.protocol_map(kit, rd, "e175.json", orders, SC.PROTOCOLS)
            r = False
        except SystemExit:
            r = True
        ok(r, "S4j a protocol whose bytes are not the recorded ones is refused")
        P2 = copy.deepcopy(P)
        P2["left_out"] = [P["sets"]["pinned"][0]]
        why = SC.stray_left_out([{"label": C.label_of(P2["left_out"][0])}], P2)
        ok(why is not None and SC.stray_left_out([{"label": C.label_of(P["sets"]["pinned"][0])}], P) is None and P["left_out"] == [],
           f"S4k a run of a tile left out by name is refused, on a copy that names one ({why}); E175 itself leaves none")
    finally:
        shutil.rmtree(tmp)


def main():
    A = C.a2p()
    P = SC.load_pred()
    with open(os.path.join(TOP, C.PRED_REL)) as f:
        pred_a2 = json.load(f)
    print(f"E175 scorer self-test: score_e175.py {C.sha256_file(SC.__file__)[:16]}, p8gov.py {C.sha256_file(G.__file__)[:16]}, "
          f"predictions-e175.json {C.sha256_file(SC.PRED_PATH)[:16]}, predict_pool8_a2.py {C.sha256_file(os.path.join(TOP, C.A2PY_REL))[:16]}")
    s1(A)
    s2(A, P)
    s3(A, P, pred_a2)
    s4(A, P)
    n_ok = sum(1 for x, _ in RES if x)
    print(f"{'ALL PASS' if n_ok == len(RES) else 'FAILED'}: {n_ok} of {len(RES)}")
    return 0 if n_ok == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
