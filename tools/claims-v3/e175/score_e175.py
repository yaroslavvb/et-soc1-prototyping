#!/usr/bin/env python3
"""E175 (Q143(g)): the registered reduction and scoring, as E175.md registers them (lab c50ff493), written before any E175 data. E173's
score_e173.py (lab 5a2a9ba0) with E175's sets, rule ids and reported arms.

    python3 tools/claims-v3/ccheck/ccheck.py check <RUNDIR>/c-log.jsonl --out <data dir>/ccheck-<session>.json --jobs 2   # at the desk, per session
    python3 -B tools/claims-v3/e175/score_e175.py <RUNDIR> [<RUNDIR> ...] --ccheck <ccheck-<session>.json> [...] [--out results.json] > score.txt

THE REDUCTION is E165's, imported and called unchanged (score_e165.collect and cells_of: E80's metrics, Q139(k)'s C join, the complete and counted
runs, the per-tile means over counted passes, the burst D against the same pass's zeros anchor). A run's pass is its protocol's order entry at its
index: each session's protocol (named with its sha256 in its e175.json) must be one of this kit's committed protocols, whose entries are the
registered order's runs (p8gov.protocol_map, E173's, imported unchanged).

THE PRIMARY: predict_pool8_a2.py burst on E175's frozen predictions (tools/claims-v3/e175/frozen/predictions-pool8-aifoundry2.json, the frozen
predictor's own output for E175's pool) with the session's zeros-anchor reads (the three zeros anchors' counted bursts only) and each tile's own
counted die starts: M10 carried (rule E) and M9's part on M9's D beside, as the frozen code returns them.

THE RULES (E175.md "Decision rules"): E175-A2-G, Bg, Bp, R2, F1, F2, W1, W2, M1, H1, read at the scored n with the frozen engine and the rule ids
as written (p8gov's fixed lines, R2's form, boot_rule and paired, unchanged); E175-C; E175-R0 (a diagnostic). The sets: the design's 16 governed
and 8 pinned, groups fixed by the frozen file; a tile with fewer than 2 counted passes is left out and named; A TILE WITH ANY LAUNCH WHOSE C CHECK
IS NOT PASS LEAVES EVERY SCORED SET, and every rule is also given over the complete runs with C not required, beside. Reported, never a verdict:
E175-GS (the governed clock error's slope on M10 carried's predicted clock, with its tile-resampled range), each stratum, M9's part on every rule.

REFUSALS (E175.md): exit 5 if a session the registration requires to carry a C log (smoke, stoptest-board, every BURST session the queue started
that ran a work launch) has no check of C given; exit 2 for a run of a tile left out by name, a run not its protocol's at its index, a protocol not
the kit's, a frozen input that differs, or a tile other than the zeros anchors reaching the primary's anchors input. A rule under its minimum, or
an empty set, reads NOT SCORED.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e165"))
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
import e175_common as C  # noqa: E402
import p8gov as G  # noqa: E402  (E173's, imported unchanged: the fixed lines, R2's form, the bootstrap and paired engines)
import score_e165 as S  # noqa: E402  (E165's reduction, unchanged)

PRED_PATH = os.path.join(HERE, "predictions-e175.json")
GS_DRAWS = 20000
PROTOCOLS = ("protocol.json", "protocol-subset.json", "protocol-dry.json")
MEAS = {"mhz": "burst_mhz", "w": "burst_w", "rise": "rise_c"}
PRD = {"mhz": "burst_mhz", "w": "burst_board_w", "rise": "burst_die_rise_c"}
E165_RESULTS_REL = "docs/reports/data/2026-11-04-e165-blind7-aifoundry2/results.json"


class Refused(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def load_pred(path=PRED_PATH):
    with open(path) as f:
        return json.load(f)


def meta_of(P):
    meta = {n: {"label": t["label"], "type": t["type"], "group": t["group"], "priority": t["priority"], "anchor": bool(t["anchor_role"])}
            for n, t in P["tiles"].items()}
    zeros = {P["tiles"][n]["type"]: P["tiles"][n]["label"] for n in C.ZEROS_ANCHORS}
    return meta, zeros


def stray_left_out(runs, P):
    lo = set(P["left_out"])
    stray = sorted({m["label"] for m in runs if C.name_of(m["label"]) in lo})
    return f"runs of tiles left out by name: {stray}" if stray else None


def c_excluded(runs):
    """E175.md (POOL8-REGISTRATION section 7's rule): a tile with any BURST launch whose C check is not PASS leaves every scored set (dry runs: none)"""
    out = {}
    for m in runs:
        if m.get("dry"):
            continue
        n = C.name_of(m["label"])
        if n is None:
            continue
        if not m.get("c_pass"):
            out.setdefault(n, []).append({"run": m["run"], "verdicts": m.get("c_verdicts")})
    return out


def errs(names, q, cells_by_name, pm):
    return [cells_by_name[n][MEAS[q]] - pm[n][PRD[q]] for n in names if cells_by_name[n].get(MEAS[q]) is not None and pm.get(n)]


def predictions(A, pred_a2, cells, P):
    """the primary's recompute for every tile (the frozen code computes all 27): the session's zeros-anchor reads and each tile's die starts"""
    _, zl = meta_of(P)
    anchors, used = G.anchors_from(cells, zl)
    G.refuse_foreign_anchor(used, zl)
    die = {}
    for n, t in P["tiles"].items():
        c = cells.get(t["label"])
        if c:
            ds = [x for x in c["die_start_runs"] if x is not None]
            if ds:
                die[n] = ds
    b = A.burst(pred_a2, anchors, die)["tiles"]
    return {n: v["M10"] for n, v in b.items()}, {n: v["M9"] for n, v in b.items()}, anchors


def relabel(d, rule):
    d = dict(d)
    d["rule"] = rule
    return d


def r2(Gr, Bg, Bp):
    """E175-A2-R2 as registered: p8gov.r2's form (PASS if all three PASS; FAIL if any FAILs; else NOT SCORED), with E175's rule ids"""
    v = G.r2(Gr, Bg, Bp)
    return {"rule": "E175-A2-R2", "components": {"E175-A2-G": Gr["verdict"], "E175-A2-Bg": Bg["verdict"], "E175-A2-Bp": Bp["verdict"]},
            "verdict": v["verdict"], "form": v["form"]}


def slope_gs(x, y, draws=GS_DRAWS):
    """E175-GS (reported): the least-squares slope of the governed clock error y on the predicted clock x, MHz per MHz, with the 2.5-97.5% range of
    `draws` tile-resampled slopes (random.Random("E175-GS"); a resample whose x has no spread is skipped and counted)"""
    import random
    n = len(x)
    out = {"rule": "E175-GS", "n": n, "note": "reported, never a verdict (E175.md)"}
    if n < 3 or len(y) != n:
        out["slope"] = None
        return out

    def fit(ix):
        xs, ys = [x[i] for i in ix], [y[i] for i in ix]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        sxx = sum((a - mx) ** 2 for a in xs)
        if sxx <= 1e-12:
            return None, None
        b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sxx
        return b, my - b * mx
    b, a0 = fit(list(range(n)))
    if b is None:
        out["slope"] = None
        return out
    rng = random.Random("E175-GS")
    vals, skipped = [], 0
    for _ in range(draws):
        bb, _ = fit([rng.randrange(n) for _ in range(n)])
        if bb is None:
            skipped += 1
        else:
            vals.append(bb)
    vals.sort()
    m = len(vals)
    out.update(slope_mhz_per_mhz=G.r4(b, 5), intercept_mhz=G.r4(a0, 3), x_span_mhz=[G.r4(min(x), 2), G.r4(max(x), 2)],
               range_95=[G.r4(vals[int(0.025 * m)], 5), G.r4(vals[int(0.975 * m) - 1], 5)] if m else None, resamples_skipped=skipped,
               resolved=("rising" if m and vals[int(0.025 * m)] > 0 else "falling" if m and vals[int(0.975 * m) - 1] < 0 else "neither"))
    return out


def score(cells, P, A, pred_a2, excl=None, light=False):
    """every registered rule on one set of cells; excl = the tiles C excludes (none for the C-not-required form beside)"""
    mp, mn, refs = P["rules"]["min_passes"], P["rules"]["minimum_tiles"], A.e165_refs()
    excl = excl or {}
    byname = {n: cells[t["label"]] for n, t in P["tiles"].items() if t["label"] in cells}
    tiles = sorted(n for n in P["sets"]["scored"] if n in byname and byname[n]["n"] >= mp and n not in excl)
    left = sorted(n for n in P["sets"]["scored"] if n not in tiles)
    gov = [n for n in tiles if P["tiles"][n]["group"] == "governed"]
    pin = [n for n in tiles if P["tiles"][n]["group"] == "pinned"]
    pm10, pm9, anchors = predictions(A, pred_a2, cells, P)
    out = {"tiles_scored": len(tiles), "governed": gov, "pinned": pin, "left_out": left, "left_out_c": sorted(n for n in excl if n in P["sets"]["scored"]),
           "left_out_by_name": P["left_out"], "anchors": anchors,
           "anchor_delta": ({"delta_w": pm10[tiles[0]]["delta_w"], "delta_source": pm10[tiles[0]]["delta_source"]} if tiles else None)}
    R = {}
    R["E175-A2-G"] = relabel(G.fixed_G(errs(gov, "mhz", byname, pm10), mn["A2_group"]), "E175-A2-G")
    R["E175-A2-Bg"] = G.fixed_mean("E175-A2-Bg", errs(gov, "w", byname, pm10), mn["A2_group"])
    R["E175-A2-Bp"] = G.fixed_mean_rms("E175-A2-Bp", errs(pin, "w", byname, pm10), mn["A2_group"])
    R["E175-A2-R2"] = r2(R["E175-A2-G"], R["E175-A2-Bg"], R["E175-A2-Bp"])
    R["E175-A2-F1"] = G.boot_rule("E175-A2-F1", errs(gov, "mhz", byname, pm10), refs["gov_mhz"], mn["A2_group"], A)
    R["E175-A2-F2"] = G.boot_rule("E175-A2-F2", errs(pin, "mhz", byname, pm10), refs["pin_mhz"], mn["A2_group"], A)
    R["E175-A2-W1"] = G.boot_rule("E175-A2-W1", errs(gov, "w", byname, pm10), refs["gov_w"], mn["A2_group"], A)
    R["E175-A2-W2"] = G.boot_rule("E175-A2-W2", errs(pin, "w", byname, pm10), refs["pin_w"], mn["A2_group"], A)
    R["E175-A2-M1"] = G.paired("E175-A2-M1", errs(tiles, "w", byname, pm10), errs(tiles, "w", byname, pm9), mn["A2_all"], A)
    R["E175-A2-H1"] = G.boot_rule("E175-A2-H1", errs(tiles, "rise", byname, pm10), refs["heat_c"], mn["A2_all"], A)
    out["rules"] = R
    if light:
        return out
    rep = {}
    rep["E175-A2-M1_clock_beside"] = G.paired("E175-A2-M1", errs(tiles, "mhz", byname, pm10), errs(tiles, "mhz", byname, pm9), mn["A2_all"], A)
    rep["E175-GS"] = slope_gs([pm10[n]["burst_mhz"] for n in gov if byname[n].get("burst_mhz") is not None],
                              errs(gov, "mhz", byname, pm10))
    rep["E175-GS_M9"] = slope_gs([pm9[n]["burst_mhz"] for n in gov if byname[n].get("burst_mhz") is not None], errs(gov, "mhz", byname, pm9))
    rep["M9_on_every_rule"] = {
        "E175-A2-G": relabel(G.fixed_G(errs(gov, "mhz", byname, pm9), mn["A2_group"]), "E175-A2-G (M9's part)"),
        "E175-A2-Bg": G.fixed_mean("E175-A2-Bg (M9's part)", errs(gov, "w", byname, pm9), mn["A2_group"]),
        "E175-A2-Bp": G.fixed_mean_rms("E175-A2-Bp (M9's part)", errs(pin, "w", byname, pm9), mn["A2_group"]),
        "E175-A2-F1": G.boot_rule("E175-A2-F1", errs(gov, "mhz", byname, pm9), refs["gov_mhz"], mn["A2_group"], A),
        "E175-A2-W1": G.boot_rule("E175-A2-W1", errs(gov, "w", byname, pm9), refs["gov_w"], mn["A2_group"], A),
        "E175-A2-F2": G.boot_rule("E175-A2-F2", errs(pin, "mhz", byname, pm9), refs["pin_mhz"], mn["A2_group"], A),
        "E175-A2-W2": G.boot_rule("E175-A2-W2", errs(pin, "w", byname, pm9), refs["pin_w"], mn["A2_group"], A),
        "note": "reported, never a verdict (E175.md): the same rules on M9's part on M9's D"}
    rep["M9_on_every_rule"]["E175-A2-R2"] = r2(rep["M9_on_every_rule"]["E175-A2-G"], rep["M9_on_every_rule"]["E175-A2-Bg"],
                                               rep["M9_on_every_rule"]["E175-A2-Bp"])
    sets = {"governed": gov, "pinned": pin, "all": tiles}
    for k, names in P["sets"]["strata"].items():
        sets[f"stratum_{k}"] = [n for n in names if n in tiles]
    for ty in ("fp32", "fp16", "int8"):
        sets[ty] = [n for n in tiles if P["tiles"][n]["type"] == ty]
    for fam in sorted({(P["tiles"][n].get("e175") or {}).get("family") for n in tiles} - {None}):
        sets[f"family_{fam}"] = [n for n in tiles if (P["tiles"][n].get("e175") or {}).get("family") == fam]
    rep["by_set"] = {}
    for s_, names in sets.items():
        row = {"n": len(names)}
        for q in ("mhz", "w", "rise"):
            for lab, pm in (("M10", pm10), ("M9", pm9)):
                e = errs(names, q, byname, pm)
                row[f"{lab}_{q}_rms"], row[f"{lab}_{q}_mean"] = G.r4(G.rms(e), 3), G.r4(G.mean(e), 3)
        rep["by_set"][s_] = row
    pk = {}
    ran = sorted(n for n in byname if not P["tiles"][n]["left_out"])
    for lab, pm in (("M10", pm10), ("M9", pm9)):
        over = [{"tile": n, "peak_w": byname[n]["peak_w"], "hi95_w": pm[n]["peak_board_hi95_w"]} for n in ran
                if byname[n].get("peak_w") is not None and byname[n]["peak_w"] > pm[n]["peak_board_hi95_w"] + 1e-9]
        pk[lab] = {"n": sum(1 for n in ran if byname[n].get("peak_w") is not None), "over": over}
    rep["peaks_vs_hi95"] = pk
    za = {}
    for n in C.ZEROS_ANCHORS:
        c = byname.get(n)
        if c and c["n"] >= 1:
            fb = P["tiles"][n]["models"]["M10"]["a2_fallback"]
            za[n] = {"n": c["n"], "burst_mhz": c["burst_mhz"], "burst_w": c["burst_w"], "die_start_runs": c["die_start_runs"],
                     "as_frozen_fallback_err_w": G.r4(c["burst_w"] - fb["burst_board_w"], 3)}
    rep["zeros_anchors"] = za
    rep["tiles"] = {n: {"group": P["tiles"][n]["group"], "set": P["tiles"][n]["set"], "stratum": P["tiles"][n]["stratum"],
                        "case": P["tiles"][n]["case"], "passes": byname[n]["passes"], "burst_mhz": byname[n]["burst_mhz"],
                        "burst_w": byname[n]["burst_w"], "rise_c": byname[n]["rise_c"], "die_start_runs": byname[n]["die_start_runs"],
                        "D_w": byname[n].get("D_w"), "peak_w": byname[n].get("peak_w"),
                        "M10": {k: pm10[n][k] for k in ("burst_mhz", "burst_board_w", "burst_die_rise_c", "burst_D_w", "group")},
                        "M9": {k: pm9[n][k] for k in ("burst_mhz", "burst_board_w", "burst_die_rise_c", "burst_D_w", "group")}} for n in tiles}
    out["reported"] = rep
    return out


def scoring(runs, P, A, pred_a2, key):
    meta, zeros = meta_of(P)
    cells = S.cells_of(runs, meta, zeros, key=key)
    passes = sorted({m["pass"] for m in runs if m[key]})
    res = {"key": key, "passes": passes, "cells": cells}
    if len(passes) < P["rules"]["min_passes"]:
        res["score"] = {"note": f"fewer than {P['rules']['min_passes']} {key} passes: every rule NOT SCORED"}
        return res
    excl = c_excluded(runs) if key == "counted" else {}
    res["c_excluded"] = excl
    res["score"] = score(cells, P, A, pred_a2, excl)
    return res


def run(rundirs, ccheck, pred_path=PRED_PATH, out=None):
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise Refused(2, "refused: " + "; ".join(bad))
    P = load_pred(pred_path)
    A = C.a2p()
    with open(os.path.join(C.TOP, C.PRED_REL)) as f:
        pred_a2 = json.load(f)
    qdir = os.path.dirname(os.path.normpath(os.path.abspath(rundirs[0])))
    ok, missing, req, rep = G.check_c_coverage(qdir, ccheck, C.C_LOG_SESSIONS)
    if not ok:
        raise Refused(5, f"refused: the registration requires a C log and its check for {req}; no check of C given for {missing} (E175.md)")
    cc = S.load_ccheck(ccheck)
    runs, protos = [], {}
    for rd in rundirs:
        try:
            m, name = G.protocol_map(HERE, rd, "e175.json", {"order": P["order"], "dry_order": P["dry_order"]}, PROTOCOLS)
            protos[os.path.basename(os.path.normpath(rd))] = name
            runs += S.collect([rd], cc, pass_of=G.pass_of_map(m))
        except SystemExit as e:
            raise Refused(2, str(e.code))
    why = stray_left_out(runs, P)
    if why:
        raise Refused(2, f"refused: {why}")
    try:
        prim = scoring(runs, P, A, pred_a2, "counted")
        comp = scoring(runs, P, A, pred_a2, "complete")
    except SystemExit as e:
        raise Refused(2, str(e.code))
    rp = R0 = None
    try:
        with open(os.path.join(C.TOP, E165_RESULTS_REL)) as f:
            rp = json.load(f)["cells"]
    except (OSError, ValueError, KeyError):
        rp = {}
    R0 = S.replicate(prim["cells"], P["replicate"], {"replicate_mhz": P["rules"]["R0"]["mhz"], "replicate_w": P["rules"]["R0"]["w"]})
    for lab, row in R0["tiles"].items():
        c165 = rp.get(lab) or {}
        if c165 and row.get("n"):
            row["e165_mhz"], row["e165_w"] = c165.get("burst_mhz"), c165.get("burst_w")
            row["d_mhz_vs_e165"] = G.r4(row["burst_mhz"] - c165["burst_mhz"], 2) if c165.get("burst_mhz") is not None else None
            row["d_w_vs_e165"] = G.r4(row["burst_w"] - c165["burst_w"], 3) if c165.get("burst_w") is not None else None
    res = {"experiment": C.EXPERIMENT, "predictions_sha256": C.sha256_file(pred_path), "scorer_sha256": C.sha256_file(__file__),
           "p8gov_sha256": C.sha256_file(G.__file__), "common_sha256": C.sha256_file(C.__file__), "score_e165_sha256": C.sha256_file(S.__file__),
           "predict_pool8_a2_sha256": C.sha256_file(os.path.join(C.TOP, C.A2PY_REL)), "sessions": [os.path.basename(os.path.normpath(r)) for r in rundirs],
           "protocols": protos, "ccheck_files": {os.path.basename(p): C.sha256_file(p) for p in ccheck},
           "c_log_coverage": {"required": req, "read": rep, "missing": missing},
           "dry": any(m["dry"] for m in runs), "runs": len(runs), "runs_complete": sum(1 for m in runs if m["complete"]),
           "runs_counted": sum(1 for m in runs if m["counted"]), "runs_not_complete": [m["run"] for m in runs if not m["complete"]],
           "runs_complete_not_counted": [m["run"] for m in runs if m["complete"] and not m["counted"]],
           "budget_stops": [m["run"] for m in runs if m["budget_stop"]], "passes": prim["passes"],
           "c_check": S.c_rule(runs, bool(ccheck)) if not any(m["dry"] for m in runs) else {"verdict": "NOT SCORED (dry: the toy card writes no C log)"},
           "c_excluded_tiles": prim.get("c_excluded", {}), "score": prim["score"],
           "as_complete_runs_C_not_required": comp["score"].get("rules", comp["score"]), "replicate_R0": R0, "peaks": S.peaks(rundirs),
           "cells": prim["cells"],
           "run_rows": [{k: m.get(k) for k in ("session", "run", "idx", "label", "pass", "complete", "counted", "c_pass", "c_lines", "c_verdicts", "budget_stop",
                                                "burst_mhz", "burst_w", "die_start", "die_max", "peak_w", "c_w", "burst_ghz_kernel")} for m in runs]}
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=1)
    return res


def report(res):
    L = [f"E175 scoring: {res['runs']} burst runs, {res['runs_complete']} complete, {res['runs_counted']} counted, passes {res['passes']}; dry {res['dry']}; "
         f"protocols {res['protocols']}",
         f"  C-log coverage: required {res['c_log_coverage']['required']}, missing {res['c_log_coverage']['missing']}",
         "  E175-C: " + json.dumps({k: v for k, v in res["c_check"].items() if k not in ("by_tile", "runs_not_all_pass")})[:400],
         f"  tiles C excludes: {sorted(res['c_excluded_tiles'])}"]
    sc = res["score"]
    if "rules" in sc:
        L.append(f"  tiles scored {sc['tiles_scored']} (governed {len(sc['governed'])}, pinned {len(sc['pinned'])}); left out {sc['left_out']}")
        L.append("  anchors: " + json.dumps(sc["anchors"])[:300])
        for k, v in sc["rules"].items():
            L.append(f"  {k:10s} {json.dumps(v)[:400]}")
        L.append("  E175-GS (reported): " + json.dumps(sc["reported"]["E175-GS"])[:300])
        L.append("  M9's part, R2 (reported): " + json.dumps(sc["reported"]["M9_on_every_rule"]["E175-A2-R2"])[:300])
        L.append("  by set: " + json.dumps(sc["reported"]["by_set"])[:900])
    else:
        L.append("  " + sc["note"])
    L.append("  E175-R0: " + json.dumps(res["replicate_R0"])[:600])
    L.append("  peaks: " + json.dumps(res["peaks"]))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=PRED_PATH)
    ap.add_argument("--ccheck", nargs="*", default=[])
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        res = run(a.rundirs, a.ccheck, a.pred, a.out)
    except Refused as e:
        print(str(e))
        return e.code
    print(report(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
