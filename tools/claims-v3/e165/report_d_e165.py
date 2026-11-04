#!/usr/bin/env python3
"""E165 (Q141(g)), amendment A2-4: the burst D in both forms, reported beside score_e165.py's, never a verdict. Standard library only; no device,
no ssh. It is run at the desk after the registered scoring (collect_e165_bounded.sh runs it):

    python3 -B tools/claims-v3/e165/report_d_e165.py <RUNDIR> [<RUNDIR> ...] --ccheck <ccheck-<session>.json> [...] [--out d-both.json] > d-both.txt

The registered form (score_e165.cells_of, E160's reduce_e160.cells_of, unchanged): a tile's burst D in pass p is its burst_w less the burst_w of the
same type's zeros anchor in pass p, whatever clock that anchor burst ran at; the tile's D is the mean over its passes. E160's fp16 zeros anchor ran
its pass 1 at 752 MHz under the service processor's mid-burst idle status and read 2.185 W short of its two 800 MHz passes, so every fp16 tile's
three-pass D read 0.728 W high (E160's corrections, C1). E165's order puts the three zeros anchors first in every pass, so the same can recur.

The second form, D_795, is C1's correction made a rule before any E165 data: in a pass where the anchor burst of the tile's type ran below 795 MHz
(predict_m9_a2.MIN_ANCHOR_MHZ, the filter burst() applies to the same anchors), that burst is replaced by the mean of the anchor's counted bursts
at 795 MHz or more; every other pass keeps its own anchor burst; a pass with no counted anchor burst is left out, as in the registered form; with no
counted anchor burst at 795 MHz or more for a type, that type's D_795 is not given (None) and says so. The zeros anchors' own D is not computed in
this form (they are the primary's inputs, never scored).

It reports, from the counted runs: each tile's D in both forms (its passes, and the reference each pass used), the anchors' passes below 795 MHz,
and the scorer's by_set D rows (rms and mean of D less each model's burst_D_w: M9 primary, M9 as frozen, M8, M7, M6) in both forms, computed by
score_e165.score() on the registered cells and on the same cells with D_795 in place of D, so that nothing but the D rows can differ (checked).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e165_common as C  # noqa: E402
import score_e165 as S  # noqa: E402

MIN_MHZ = 795.0   # predict_m9_a2.MIN_ANCHOR_MHZ (checked in main)


def d_795(cells, meta, zeros, min_mhz=MIN_MHZ):
    """{label: {...}} for every pool tile with a name: the registered D (as cells_of computed it) and D_795 (C1's form), with each pass's reference"""
    out = {}
    anchor_labels = set(zeros.values())
    for lab, c in sorted(cells.items()):
        name = c.get("name")
        if name is None:
            continue
        t = meta[name]
        zl = zeros.get(t["type"])
        a = cells.get(zl)
        row = {"name": name, "type": t["type"], "group": t["group"], "passes": c["passes"], "D_w": c.get("D_w"), "D_runs": c.get("D_runs")}
        if lab in anchor_labels:
            row.update({"D_w_795": None, "D_runs_795": None, "why": "a zeros anchor (an input of the primary; never scored)"})
            out[lab] = row
            continue
        if a is None:
            row.update({"D_w_795": None, "D_runs_795": None, "why": f"no counted burst of {zl}"})
            out[lab] = row
            continue
        apass = dict(zip(a["passes"], a["burst_w_runs"]))
        amhz = dict(zip(a["passes"], a["burst_mhz_runs"]))
        good = [p for p in a["passes"] if amhz[p] is not None and amhz[p] >= min_mhz]
        ref = S.mean([apass[p] for p in good]) if good else None
        W = dict(zip(c["passes"], c["burst_w_runs"]))
        runs, refs = [], {}
        for p in c["passes"]:
            if p not in apass:
                continue                                          # no anchor burst in this pass: left out, as registered
            if amhz[p] is not None and amhz[p] >= min_mhz:
                refs[str(p)] = {"from": f"pass {p}", "w": apass[p]}
                runs.append(W[p] - apass[p])
            elif ref is not None:
                refs[str(p)] = {"from": f"mean of passes {good} at {min_mhz:.0f} MHz or more (pass {p} ran at {amhz[p]} MHz)", "w": S.rnd(ref, 4)}
                runs.append(W[p] - ref)
            else:
                runs = None
                break
        if runs is None or not runs:
            row.update({"D_w_795": None, "D_runs_795": None, "why": f"no counted burst of {zl} at {min_mhz:.0f} MHz or more"})
        else:
            row.update({"D_w_795": S.rnd(S.mean(runs), 3), "D_runs_795": [round(x, 3) for x in runs], "ref_by_pass": refs})
        out[lab] = row
    return out


def anchors_below(cells, zeros, min_mhz=MIN_MHZ):
    out = {}
    for ty, zl in sorted(zeros.items()):
        a = cells.get(zl)
        if a:
            out[ty] = {"label": zl, "passes": a["passes"], "burst_mhz_runs": a["burst_mhz_runs"], "burst_w_runs": a["burst_w_runs"],
                       "passes_below": [p for p, f in zip(a["passes"], a["burst_mhz_runs"]) if f is not None and f < min_mhz]}
    return out


def with_d795(cells, rows):
    """a copy of the cells with D_795 in place of the registered D (pool tiles with a D_795; every other field unchanged)"""
    c2 = copy.deepcopy(cells)
    for lab, r in rows.items():
        if r.get("D_w_795") is not None:
            c2[lab]["D_w"] = r["D_w_795"]
            c2[lab]["D_runs"] = r["D_runs_795"]
    return c2


def strip_d(x):
    """the score with the D rows and the tiles' D removed (what must be identical between the two forms)"""
    x = copy.deepcopy(x)
    for row in x.get("reported", {}).get("by_set", {}).values():
        for k in [k for k in row if "_D_" in k]:
            del row[k]
    for t in x.get("reported", {}).get("tiles", {}).values():
        t.pop("D_w", None)
    return x


def d_rows(score):
    return {s: {k: v for k, v in row.items() if "_D_" in k or k == "n"} for s, row in score["reported"]["by_set"].items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e165.json"))
    ap.add_argument("--ccheck", nargs="*", default=[])
    ap.add_argument("--out")
    a = ap.parse_args()
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    if C.m9a2().MIN_ANCHOR_MHZ != MIN_MHZ:
        raise SystemExit(f"refused: predict_m9_a2.MIN_ANCHOR_MHZ is {C.m9a2().MIN_ANCHOR_MHZ}, not {MIN_MHZ}")
    P = json.load(open(a.pred))
    runs = S.collect(a.rundirs, S.load_ccheck(a.ccheck), pass_of=S.pass_by_order(P))
    why = S.stray_left_out(runs, P)
    if why:
        raise SystemExit(f"refused: {why}")
    meta, zeros = S.meta_of(P)
    cells = S.cells_of(runs, meta, zeros, key="counted")
    mp = P["rules"]["min_passes"]
    passes = sorted({m["pass"] for m in runs if m["counted"]})
    rows = d_795(cells, meta, zeros)
    res = {"experiment": "E165", "what": "the burst D in both forms (amendment A2-4; reported, never a verdict)", "min_anchor_mhz": MIN_MHZ,
           "report_sha256": C.sha256_file(os.path.abspath(__file__)), "scorer_sha256": C.sha256_file(S.__file__),
           "predictions_sha256": C.sha256_file(a.pred), "sessions": [os.path.basename(os.path.normpath(r)) for r in a.rundirs],
           "passes_counted": passes, "anchors": anchors_below(cells, zeros), "tiles": rows}
    if len(passes) < mp:
        res["by_set"] = f"fewer than {mp} counted passes: not computed (every rule NOT SCORED)"
    else:
        s0 = S.score(cells, P, mp, light=True)
        s1 = S.score(with_d795(cells, rows), P, mp, light=True)
        same = json.dumps(strip_d(s0), sort_keys=True) == json.dumps(strip_d(s1), sort_keys=True)
        res["by_set"] = {"registered": d_rows(s0), "D_795": d_rows(s1)}
        res["everything_but_D_identical"] = same
        if not same:
            raise SystemExit("refused: the two forms' scores differ outside the D rows")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    print(f"E165 burst D in both forms (amendment A2-4, reported only): counted passes {passes}; anchors at {MIN_MHZ:.0f} MHz or more kept")
    for ty, an in res["anchors"].items():
        print(f"  {ty} anchor {an['label']}: clock {an['burst_mhz_runs']} MHz, board {an['burst_w_runs']} W; passes below {MIN_MHZ:.0f} MHz: {an['passes_below'] or 'none'}")
    if isinstance(res["by_set"], dict):
        print("  everything but the D rows identical between the two forms:", res["everything_but_D_identical"])
        print("  set          n   M9 primary D rms / mean (registered -> D_795)     M8 D rms / mean (registered -> D_795)")
        for s in res["by_set"]["registered"]:
            r0, r1 = res["by_set"]["registered"][s], res["by_set"]["D_795"][s]
            print(f"  {s:12s} {r0['n']:3d}   {r0['M9_primary_D_rms']} / {r0['M9_primary_D_mean']} -> {r1['M9_primary_D_rms']} / {r1['M9_primary_D_mean']}"
                  f"      {r0['M8_D_rms']} / {r0['M8_D_mean']} -> {r1['M8_D_rms']} / {r1['M8_D_mean']}")
    else:
        print(" ", res["by_set"])
    print("  tile                                      group     D registered (passes)  ->  D_795 (passes)")
    for lab, r in sorted(rows.items(), key=lambda kv: (kv[1]["type"], kv[0])):
        if r.get("D_w_795") is None and "why" in r:
            print(f"  {r['name']:41s} {r['group']:8s}  {r['D_w']} {r['D_runs']}  ->  not given: {r['why']}")
        else:
            print(f"  {r['name']:41s} {r['group']:8s}  {r['D_w']} {r['D_runs']}  ->  {r['D_w_795']} {r['D_runs_795']}")


if __name__ == "__main__":
    main()
