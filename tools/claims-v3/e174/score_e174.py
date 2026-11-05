#!/usr/bin/env python3
"""E174 (Q142(kg)): the registered reduction and scoring, as E174.md registers them (lab c8064454), written before any E174 data.

    python3 tools/claims-v3/ccheck/ccheck.py check <RUNDIR>/c-log.jsonl --out <data dir>/ccheck-<session>.json --jobs 2   # at the desk, per session
    python3 -B tools/claims-v3/e174/score_e174.py <RUNDIR> [<RUNDIR> ...] --ccheck <ccheck-<session>.json> [...] [--out results.json] > score.txt

THE REDUCTION is E165's (score_e165.collect and cells_of), imported unchanged, as E170's was; each session's runs are read against its own
protocol's order entries (p8gov.protocol_map: the protocol named with its sha256 in the session's e174.json, one of this kit's committed files).

THE PRIMARY: predict_pool8_a2.py burst on the frozen predictions-pool8-aifoundry1c0.json with the session's zeros-anchor reads (the three zeros
anchors' counted bursts only) and each tile's own counted die starts: M10 carried through E170's card term (e170_common.pred_card0: kappa0
0.9463, the session's zeros level in full) with M10's term c2 rise on the predicted board; M9 carried the same way, with M9's law's rise, beside.

THE RULES (E174.md "Decision rules"): P8-C0-W, B, M1, F, H1, HK at the scored n (A2-3 (g)); P8-HM NOT SCORED (no hold); E174-C; E174-S (a
diagnostic, E170-S's form). Fewer than 2 counted passes of half A (passes 1-3): every rule but E174-C and E174-S NOT SCORED. A tile with fewer than
2 counted passes is left out and named; a tile with any launch whose C check is not PASS leaves every scored set (POOL8-REGISTRATION section 7),
and every rule is also given over the complete runs, C not required, beside.

REFUSALS: as score_e173.py's (exit 5 a missing C-log check; exit 2 the rest).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
sys.path.insert(0, os.path.join(HERE, "..", "e165"))
import e174_common as C  # noqa: E402
import p8gov as G  # noqa: E402
import score_e165 as S  # noqa: E402  (E165's reduction, unchanged)

R = S.R
PRED_PATH = os.path.join(HERE, "predictions-e174.json")
PROTOCOLS = ("protocol.json", "protocol-subset.json", "protocol-dry.json")


def heat_ks(A):
    """C0-HK's two coefficients, read from the frozen files: M10's term c2 (m10.json card0_burst_heat_k_c_per_w, 0.2415) and M9's burst heat law
    (m9_a2.json burst_heat.k_used_c_per_w, 0.1400), both over m9_a2.json's P_idle (21.5 W)"""
    p = A.P()
    H = p.a2_part().HEAT
    return float(p.frozen()["m10"]["card0_burst_heat_k_c_per_w"]), float(H["k_used_c_per_w"]), float(H["P_idle_w"])


class Refused(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def load_pred(path=PRED_PATH):
    with open(path) as f:
        return json.load(f)


def meta_of(P):
    meta = {n: {"label": t["label"], "type": t["type"], "group": "pinned", "priority": t["priority"], "anchor": bool(t["anchor_role"])}
            for n, t in P["tiles"].items()}
    zeros = {P["tiles"][n]["type"]: P["tiles"][n]["label"] for n in C.ZEROS_ANCHORS}
    return meta, zeros


def stray_left_out(runs, P):
    lo = set(P["left_out"])
    stray = sorted({m["label"] for m in runs if C.name_of(m["label"]) in lo or (C.name_of(m["label"]) is not None and C.name_of(m["label"]) not in P["tiles"])})
    return f"runs of tiles left out by name (or not admitted): {stray}" if stray else None


def c_excluded(runs):
    out = {}
    for m in runs:
        n = C.name_of(m["label"])
        if m.get("dry") or n is None:
            continue
        if not m.get("c_pass"):
            out.setdefault(n, []).append({"run": m["run"], "verdicts": m.get("c_verdicts")})
    return out


def predictions(A, pred_c0, cells, P):
    _, zl = meta_of(P)
    anchors, used = G.anchors_from(cells, zl)
    G.refuse_foreign_anchor(used, zl)
    if anchors is None:
        return None, None, None
    die = {}
    for n, t in P["tiles"].items():
        c = cells.get(t["label"])
        if c:
            ds = [x for x in c["die_start_runs"] if x is not None]
            if ds:
                die[n] = ds
    b = A.burst(pred_c0, anchors, die)["tiles"]
    return {n: v["M10"] for n, v in b.items()}, {n: v["M9"] for n, v in b.items()}, anchors


def score(cells, P, A, pred_c0, excl=None, light=False):
    mp, mn, refs = P["rules"]["min_passes"], P["rules"]["minimum_tiles"], A.e165_refs()
    excl = excl or {}
    byname = {n: cells[t["label"]] for n, t in P["tiles"].items() if t["label"] in cells}
    tiles = sorted(n for n in P["scored"] if n in byname and byname[n]["n"] >= mp and n not in excl)
    left = sorted(n for n in P["scored"] if n not in tiles)
    pm10, pm9, anchors = predictions(A, pred_c0, cells, P)
    out = {"tiles_scored": len(tiles), "left_out": left, "left_out_c": sorted(n for n in excl if n in P["scored"]), "anchors": anchors}
    if pm10 is None:
        out["rules"] = {"note": "no zeros-anchor burst counted: the card term's level cannot be read; every rule NOT SCORED"}
        return out
    band = A.c0_band()

    def e(names, mk, pm, pk):
        return [byname[n][mk] - pm[n][pk] for n in names if byname[n].get(mk) is not None and pm.get(n)]
    ew = e(tiles, "burst_w", pm10, "burst_board_w")
    em = e(tiles, "burst_mhz", pm10, "burst_mhz")
    er = e(tiles, "rise_c", pm10, "burst_die_rise_c")
    dn = [n for n in tiles if byname[n].get("D_w") is not None]
    Rr = {}
    Rr["P8-C0-W"] = G.boot_rule("P8-C0-W", ew, refs["pin_w"], mn["C0"], A)
    Rr["P8-C0-B"] = G.fixed_mean_rms("P8-C0-B", ew, mn["C0"])
    Rr["P8-C0-M1"] = G.paired("P8-C0-M1", [byname[n]["D_w"] - pm10[n]["burst_D_w"] for n in dn], [byname[n]["D_w"] - pm9[n]["burst_D_w"] for n in dn],
                              mn["C0_M1"], A)
    Rr["P8-C0-F"] = G.boot_rule("P8-C0-F", em, refs["pin_mhz"], mn["C0"], A)
    Rr["P8-C0-H1"] = G.boot_rule("P8-C0-H1", er, band["residuals_c"], mn["C0"], A)
    hk = [n for n in tiles if byname[n].get("rise_c") is not None and byname[n].get("burst_w") is not None]
    K_M10, K_M9, P_IDLE = heat_ks(A)
    Rr["P8-C0-HK"] = G.paired("P8-C0-HK", [byname[n]["rise_c"] - K_M10 * (byname[n]["burst_w"] - P_IDLE) for n in hk],
                              [byname[n]["rise_c"] - K_M9 * (byname[n]["burst_w"] - P_IDLE) for n in hk], mn["C0"], A)
    Rr["P8-C0-HK"]["k_a"], Rr["P8-C0-HK"]["k_b"] = K_M10, K_M9
    Rr["P8-HM"] = {"rule": "P8-HM", "verdict": "NOT SCORED (no hold runs in E174)"}
    out["rules"] = Rr
    if light:
        return out
    rep = {}
    rep["M9_carried"] = {"board": {"rms": G.r4(G.rms(e(tiles, "burst_w", pm9, "burst_board_w"))), "mean": G.r4(G.mean(e(tiles, "burst_w", pm9, "burst_board_w")))},
                         "clock": {"rms": G.r4(G.rms(e(tiles, "burst_mhz", pm9, "burst_mhz")))},
                         "rise_M9_law": {"rms": G.r4(G.rms(e(tiles, "rise_c", pm9, "burst_die_rise_c"))), "mean": G.r4(G.mean(e(tiles, "rise_c", pm9, "burst_die_rise_c")))}}
    xn = [n for n in dn if pm10[n]["a2_burst_D_w"] >= 5.0]
    rep["X0_ratio_reported"] = C.C170.boot_ratio_ci([byname[n]["D_w"] for n in xn], [pm10[n]["a2_burst_D_w"] for n in xn]) if len(xn) >= 2 else None
    if rep["X0_ratio_reported"]:
        rep["X0_ratio_reported"]["kappa0"] = C.KAPPA0
    rise_meas_k = None
    xs = [(byname[n]["burst_w"] - P_IDLE, byname[n]["rise_c"]) for n in hk]
    if xs and sum(x * x for x, _ in xs) > 0:
        rise_meas_k = sum(x * y for x, y in xs) / sum(x * x for x, _ in xs)
    rep["rise_per_board_w_over_21p5_least_squares"] = G.r4(rise_meas_k)

    def grp(key):
        g = {}
        for n in tiles:
            if byname[n].get("burst_w") is None:
                continue
            g.setdefault(key(n), []).append(byname[n]["burst_w"] - pm10[n]["burst_board_w"])
        return {k: {"n": len(v), "rms": G.r4(G.rms(v)), "mean": G.r4(G.mean(v))} for k, v in sorted(g.items())}
    rep["by_format"] = grp(lambda n: P["tiles"][n]["type"])
    rep["by_tier"] = grp(lambda n: P["tiles"][n]["tier"])
    rep["by_case"] = grp(lambda n: P["tiles"][n]["case"])
    rep["zeros_levels"] = {t: {"bursts": len(rr), "mean_burst_w": G.r4(G.mean([r["burst_w"] for r in rr]))} for t, rr in anchors.items()}
    rep["peaks_vs_estimates"] = sorted(([n, byname[n].get("peak_w"), P["tiles"][n]["est_card0_peak_w"]] for n in byname if n in P["tiles"]),
                                       key=lambda x: -(x[1] or 0))[:12]
    rep["tiles"] = {n: {"type": P["tiles"][n]["type"], "tier": P["tiles"][n]["tier"], "case": P["tiles"][n]["case"], "passes": byname[n]["passes"],
                        "burst_w": byname[n]["burst_w"], "burst_mhz": byname[n]["burst_mhz"], "D_w": byname[n].get("D_w"), "rise_c": byname[n]["rise_c"],
                        "peak_w": byname[n].get("peak_w"), "die_starts": byname[n]["die_start_runs"],
                        "M10": {k: pm10[n].get(k) for k in ("burst_board_w", "burst_mhz", "burst_D_w", "burst_die_rise_c", "zeros_level_w")},
                        "M9": {k: pm9[n].get(k) for k in ("burst_board_w", "burst_mhz", "burst_D_w", "burst_die_rise_c")}} for n in tiles}
    out["reported"] = rep
    return out


def safety(runs, rundirs):
    """E174-S (E170-S's form): no safety stop (the session's marks), no sampler line under 590 MHz in a BURST run, no run's peak at or above 62 W"""
    trips, low = [], []
    for rd in rundirs:
        mp = os.path.join(rd, "marks.jsonl")
        if os.path.exists(mp):
            with open(mp) as f:
                for ln in f:
                    try:
                        d = json.loads(ln)
                    except ValueError:
                        continue
                    if d.get("kind") in ("safety_trip", "e174_alarm", "e170_alarm") or d.get("event") in ("safety_trip", "e174_alarm", "e170_alarm"):
                        trips.append(d)
    tels = {}
    for rd in rundirs:
        for r in R.load_session(rd)[1]:
            if r.get("block") == "BURST":
                tels[(os.path.basename(os.path.normpath(rd)), r["run"])] = os.path.join(rd, r["tel"])
    for m in runs:
        p = tels.get((m["session"], m["run"]))
        s = R.tel(p) if p else []
        mh = [x[4] for x in s if x[4] is not None]
        if mh and min(mh) < C.MIN_MHZ_ALARM:
            low.append([m["run"], min(mh)])
    hot = [[m["run"], m["peak_w"]] for m in runs if m.get("peak_w") is not None and m["peak_w"] >= C.PEAK_LOCK_W]
    v = "PASS" if not trips and not low and not hot else "FAIL"
    return {"safety_marks": trips[:10], "runs_under_590_mhz": low, "runs_at_or_over_62w": hot,
            "board_max_w": max((m["peak_w"] for m in runs if m.get("peak_w") is not None), default=None), "verdict": v}


def scoring(runs, P, A, pred_c0, key):
    meta, zeros = meta_of(P)
    cells = S.cells_of(runs, meta, zeros, key=key)
    a_passes = sorted({m["pass"] for m in runs if m[key] and m["pass"] in (1, 2, 3)})
    res = {"key": key, "passes": sorted({m["pass"] for m in runs if m[key]}), "half_A_passes": a_passes, "cells": cells}
    if len(a_passes) < P["rules"]["min_passes"]:
        res["score"] = {"note": f"fewer than {P['rules']['min_passes']} {key} passes of half A: every rule but E174-C and E174-S NOT SCORED"}
        return res
    excl = c_excluded(runs) if key == "counted" else {}
    res["c_excluded"] = excl
    res["score"] = score(cells, P, A, pred_c0, excl)
    return res


def run(rundirs, ccheck, pred_path=PRED_PATH, out=None):
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise Refused(2, "refused: " + "; ".join(bad))
    P = load_pred(pred_path)
    A = C.a2p()
    with open(os.path.join(C.TOP, C.PRED_REL)) as f:
        pred_c0 = json.load(f)
    qdir = os.path.dirname(os.path.normpath(os.path.abspath(rundirs[0])))
    ok, missing, req, rep = G.check_c_coverage(qdir, ccheck, C.C_LOG_SESSIONS)
    if not ok:
        raise Refused(5, f"refused: the registration requires a C log and its check for {req}; no check of C given for {missing} (E174.md)")
    cc = S.load_ccheck(ccheck)
    runs, protos = [], {}
    for rd in rundirs:
        try:
            m, name = G.protocol_map(HERE, rd, "e174.json", {"order": P["order"], "dry_order": P["dry_order"]}, PROTOCOLS)
            protos[os.path.basename(os.path.normpath(rd))] = name
            runs += S.collect([rd], cc, pass_of=G.pass_of_map(m))
        except SystemExit as e:
            raise Refused(2, str(e.code))
    why = stray_left_out(runs, P)
    if why:
        raise Refused(2, f"refused: {why}")
    try:
        prim = scoring(runs, P, A, pred_c0, "counted")
        comp = scoring(runs, P, A, pred_c0, "complete")
    except SystemExit as e:
        raise Refused(2, str(e.code))
    dry = any(m["dry"] for m in runs)
    res = {"experiment": C.EXPERIMENT, "predictions_sha256": C.sha256_file(pred_path), "scorer_sha256": C.sha256_file(__file__),
           "p8gov_sha256": C.sha256_file(G.__file__), "common_sha256": C.sha256_file(C.__file__), "score_e165_sha256": C.sha256_file(S.__file__),
           "predict_pool8_a2_sha256": C.sha256_file(os.path.join(C.TOP, C.C173.A2PY_REL)), "kappa0": C.KAPPA0,
           "sessions": [os.path.basename(os.path.normpath(r)) for r in rundirs], "protocols": protos,
           "ccheck_files": {os.path.basename(p): C.sha256_file(p) for p in ccheck}, "c_log_coverage": {"required": req, "read": rep, "missing": missing},
           "dry": dry, "runs": len(runs), "runs_complete": sum(1 for m in runs if m["complete"]), "runs_counted": sum(1 for m in runs if m["counted"]),
           "runs_not_complete": [m["run"] for m in runs if not m["complete"]], "budget_stops": [m["run"] for m in runs if m["budget_stop"]],
           "passes": prim["passes"],
           "c_check": S.c_rule(runs, bool(ccheck)) if not dry else {"verdict": "NOT SCORED (dry: the toy card writes no C log)"},
           "safety_E174_S": safety(runs, rundirs), "c_excluded_tiles": prim.get("c_excluded", {}), "score": prim["score"],
           "as_complete_runs_C_not_required": comp["score"].get("rules", comp["score"]), "peaks": S.peaks(rundirs), "cells": prim["cells"],
           "run_rows": [{k: m.get(k) for k in ("session", "run", "idx", "label", "pass", "complete", "counted", "c_pass", "c_lines", "c_verdicts", "budget_stop",
                                                "burst_mhz", "burst_w", "die_start", "die_max", "peak_w", "c_w")} for m in runs]}
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=1)
    return res


def report(res):
    L = [f"E174 scoring: {res['runs']} burst runs, {res['runs_complete']} complete, {res['runs_counted']} counted, passes {res['passes']}; dry {res['dry']}; "
         f"protocols {res['protocols']}",
         f"  C-log coverage: required {res['c_log_coverage']['required']}, missing {res['c_log_coverage']['missing']}",
         "  E174-C: " + json.dumps({k: v for k, v in res["c_check"].items() if k not in ("by_tile", "runs_not_all_pass")})[:400],
         "  E174-S: " + json.dumps(res["safety_E174_S"])[:400], f"  tiles C excludes: {sorted(res['c_excluded_tiles'])}"]
    sc = res["score"]
    if "rules" in sc and "note" not in sc["rules"]:
        L.append(f"  tiles scored {sc['tiles_scored']}; left out {sc['left_out']}")
        for k, v in sc["rules"].items():
            L.append(f"  {k:10s} {json.dumps(v)[:400]}")
        for k in ("M9_carried", "X0_ratio_reported", "rise_per_board_w_over_21p5_least_squares", "by_format", "by_tier", "by_case", "zeros_levels"):
            L.append(f"  [{k}] {json.dumps(sc['reported'][k])[:500]}")
    else:
        L.append("  " + (sc.get("note") or json.dumps(sc.get("rules"))))
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
