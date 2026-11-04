#!/usr/bin/env python3
"""Q140(q) part A: G4's registered fit (REGISTRATION.md, 49575094). Desk only.

    nice -n 10 python3 -B fit_g4.py > fit-g4.txt       (writes loso-g4.json, g4.json, rows-g4.json; 4 worker processes)

Rows: the 56 sustained GEMM-pattern runs of Q139(q)'s posthoc-g3-inputs.json (E119, E126, E136, E146) and E159's nine holds rebuilt
on e159_g3.score's path (g4_model.e159_inputs): 65 runs, five sessions. Loss per run (G3's): (clock/15)^2 + (W/2)^2 + (die/1)^2.
Folds: leave one session out; every constant chosen inside each fold on the other four sessions.
Forward rule: A0 = G3 nested (k_eff on {0, 0.1, 0.2, 0.3, 0.442}, trip on {65.1 ... 65.9}); then T_Z (beta x delta, fallback),
T_D (one die law from T_ref 54.38 C, k_D on {0.44, 0.47, 0.50}, replacing k_eff) and T_G (a boundary dip at 618 MHz, d_G on
{0, 0.03, 0.06, 0.09, 0.12}, P_G on {44, 48, 52, 56} W), each added to the model kept so far; a term carries if the held-out loss
falls in at least 3 of the 5 sessions and pooled; kept if it carries. T_S (M8's span fraction) is structural and reported.
SPDX-License-Identifier: Apache-2.0
"""
import itertools
import json
import math
import os
import sys
from multiprocessing import Pool

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g4_model as G4  # noqa: E402

G = G4.G
LAB = G4.LAB
RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}
SESS = ("E119", "E126", "E136", "E146", "E159")
K_GRID = (0.0, 0.1, 0.2, 0.3, 0.442)
TRIP_GRID = (65.1, 65.3, 65.5, 65.7, 65.9)
KD_GRID = (0.44, 0.47, 0.50)
DG_GRID = (0.0, 0.03, 0.06, 0.09, 0.12)
PG_GRID = (44.0, 48.0, 52.0, 56.0)
INP = None


def load_inputs():
    inp = json.load(open(os.path.join(G4.G3D, "posthoc-g3-inputs.json")))
    inp = inp + G4.e159_inputs()
    for c in inp:
        c["type"] = G4.cell_type(c["cell"])
    return inp


def _init():
    global INP
    INP = load_inputs()


def eval_cfg(cfg):
    """cfg: (key, arm dict) -> key, per-run predictions"""
    key, arm = cfg
    out = []
    for c in INP:
        a = dict(arm)
        if "lev_override" in arm and c["run"] in arm["lev_override"] and c["session"] == "E136":
            a["lev"] = {int(f): v for f, v in arm["lev_override"][c["run"]].items()}
        p = G4.run_arm(c, a)
        out.append(p)
    return key, out


def loss_rows(errs):
    return float(sum(sum((e[q] / RULE[q]) ** 2 for q in RULE) for e in errs))


def stats(errs):
    o = {}
    for q in RULE:
        e = np.array([x[q] for x in errs])
        o[q] = {"rms": round(float(np.sqrt(np.mean(e ** 2))), 4), "mean": round(float(np.mean(e)), 4),
                "inside": int(np.sum(np.abs(e) <= RULE[q])), "n": int(len(e))}
    return o


class Grid:
    def __init__(self, inp, preds):
        self.inp = inp
        self.preds = preds       # key -> list of predictions per run
        self.err = {k: [{q: c["meas"][q] - p[q] for q in RULE} for c, p in zip(inp, v)] for k, v in preds.items()}
        self.sess = [c["session"] for c in inp]

    def loss(self, key, sess_in=None, sess_out=None):
        e = [x for x, s in zip(self.err[key], self.sess) if (sess_in is None or s in sess_in) and (sess_out is None or s != sess_out)]
        return loss_rows(e)

    def nested(self, keys):
        """per held-out session: the key best on the other four, its held-out loss, rows and errors"""
        res = {}
        for s in SESS:
            best = min(keys, key=lambda k: self.loss(k, sess_out=s))
            rows = [i for i, ss in enumerate(self.sess) if ss == s]
            e = [self.err[best][i] for i in rows]
            res[s] = {"chosen": best, "loss": loss_rows(e), "errs": e, "idx": rows}
        return res


def pooled(nest):
    errs = []
    for s in SESS:
        errs += nest[s]["errs"]
    return errs


def step_verdict(prev, new):
    lower = [s for s in SESS if new[s]["loss"] < prev[s]["loss"] - 1e-9]
    lp, ln = sum(prev[s]["loss"] for s in SESS), sum(new[s]["loss"] for s in SESS)
    carries = len(lower) >= 3 and ln < lp - 1e-9
    return {"sessions_lower": lower, "n_lower": len(lower), "pooled_loss_prev": round(lp, 3), "pooled_loss_new": round(ln, 3), "carries": carries,
            "per_session": {s: {"prev": round(prev[s]["loss"], 3), "new": round(new[s]["loss"], 3)} for s in SESS}}


def boot_paired(ea, eb, n=10000, seed=140):
    """rms(ea) - rms(eb) over runs, 95%"""
    rng = np.random.default_rng(seed)
    ea, eb = np.asarray(ea), np.asarray(eb)
    m = len(ea)
    d = []
    for _ in range(n):
        i = rng.integers(0, m, m)
        d.append(math.sqrt(np.mean(ea[i] ** 2)) - math.sqrt(np.mean(eb[i] ** 2)))
    return [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]


def main():
    inp = load_inputs()
    print(f"rows: {len(inp)} runs; sessions " + ", ".join(f"{s} {sum(c['session'] == s for c in inp)}" for s in SESS), flush=True)
    cfgs = {}
    for k, tr in itertools.product(K_GRID, TRIP_GRID):
        cfgs[("A0", k, tr)] = {"k": k, "trip": tr}
        cfgs[("Z", k, tr)] = {"k": k, "trip": tr, "zeros": True}
    for kd, tr in itertools.product(KD_GRID, TRIP_GRID):
        cfgs[("ZD", kd, tr)] = {"k": kd, "trip": tr, "zeros": True, "T_ref": G4.T_REF}
        cfgs[("D", kd, tr)] = {"k": kd, "trip": tr, "T_ref": G4.T_REF}
    with Pool(4, initializer=_init) as pool:
        preds = dict(pool.map(eval_cfg, list(cfgs.items()), chunksize=1))
    grid = Grid(inp, preds)
    # reproduction check: A0 at G3's frozen constants reproduces fit-g3.json's in-sample row on the 56 runs and E159's blind G3 row
    fz = grid.err[("A0", 0.1, 65.5)]
    s56 = stats([e for e, c in zip(fz, inp) if c["session"] != "E159"])
    s9 = stats([e for e, c in zip(fz, inp) if c["session"] == "E159"])
    f3 = json.load(open(os.path.join(G4.G3D, "fit-g3.json")))["final"]["in_sample"]
    r159 = json.load(open(os.path.join(LAB, "docs/reports/data/2026-11-03-e159-gemm-sustained/results.json")))["all_scored"]["summary"]
    rep = {"56_runs_here": {q: s56[q]["rms"] for q in RULE}, "56_runs_fit_g3": {q: f3[q]["rms"] for q in RULE},
           "E159_here": {q: s9[q]["rms"] for q in RULE}, "E159_results_json": {q: r159[f"G3.{q}"]["rms"] for q in RULE}}
    worst = max(max(abs(rep["56_runs_here"][q] - rep["56_runs_fit_g3"][q]) for q in RULE), max(abs(rep["E159_here"][q] - rep["E159_results_json"][q]) for q in RULE))
    print(f"REPRODUCTION: G3 at (0.1, 65.5) here vs committed: {rep}; worst |diff| {worst:.4f}", flush=True)
    if worst > 0.002:
        raise SystemExit("A0 does not reproduce G3's committed scores")
    keys = lambda tag: [k for k in cfgs if k[0] == tag]  # noqa: E731
    steps, models = [], {}
    models["A0"] = grid.nested(keys("A0"))
    kept = ""
    cur = "A0"
    # T_Z
    nz = grid.nested(keys("Z"))
    v = step_verdict(models[cur], nz)
    steps.append(dict(v, term="T_Z", against=cur))
    if v["carries"]:
        kept += "Z"
        cur = "Z"
        models["Z"] = nz
    # T_D
    tagD = "ZD" if "Z" in kept else "D"
    nd = grid.nested(keys(tagD))
    v = step_verdict(models[cur], nd)
    steps.append(dict(v, term="T_D", against=cur))
    if v["carries"]:
        kept += "D"
        cur = tagD
        models[tagD] = nd
    # T_G on the model kept so far
    base = [(k, cfgs[k]) for k in keys(cur)]
    gcfg = {}
    for (k0, arm), dg, pg in itertools.product(base, DG_GRID, PG_GRID):
        if dg == 0 and pg != PG_GRID[0]:
            continue
        gcfg[(cur + "G",) + k0[1:] + (dg, pg)] = dict(arm, dip=(dg, pg))
    with Pool(4, initializer=_init) as pool:
        preds_g = dict(pool.map(eval_cfg, list(gcfg.items()), chunksize=1))
    cfgs.update(gcfg)
    grid.preds.update(preds_g)
    grid.err.update({k: [{q: c["meas"][q] - p[q] for q in RULE} for c, p in zip(inp, v_)] for k, v_ in preds_g.items()})
    ng = grid.nested(list(gcfg))
    v = step_verdict(models[cur], ng)
    steps.append(dict(v, term="T_G", against=cur))
    if v["carries"]:
        kept += "G"
        models[cur + "G"] = ng
        cur = cur + "G"
    final_keys = [k for k in cfgs if k[0] == cur]
    final = min(final_keys, key=lambda k: grid.loss(k))
    g4_nested = models[cur]
    # reference arms
    g3_frozen = ("A0", 0.1, 65.5)
    ref = {"G3_as_frozen": grid.err[g3_frozen], "G3_nested": pooled(models["A0"]), "G4_nested": pooled(g4_nested), "G4_final_in_sample": grid.err[final]}
    order = []
    for s in SESS:
        order += models["A0"][s]["idx"]
    # pooled lists are in session order; reorder the per-run arms to the same order
    ref["G3_as_frozen"] = [grid.err[g3_frozen][i] for i in order]
    ref["G4_final_in_sample"] = [grid.err[final][i] for i in order]
    by_sess = {}
    for name, nest in (("G3_nested", models["A0"]), ("G4_nested", g4_nested)):
        by_sess[name] = {s: stats(nest[s]["errs"]) for s in SESS}
    by_sess["G3_as_frozen"] = {s: stats([grid.err[g3_frozen][i] for i in models["A0"][s]["idx"]]) for s in SESS}
    boots = {q: boot_paired([e[q] for e in ref["G3_nested"]], [e[q] for e in ref["G4_nested"]]) for q in RULE}
    boots_frozen = {q: boot_paired([e[q] for e in ref["G3_as_frozen"]], [e[q] for e in ref["G4_nested"]]) for q in RULE}
    # large GEMMs only (E136, E146, E159) and E159 alone
    idx_sess = {s: models["A0"][s]["idx"] for s in SESS}

    def sub(errs_by_run, sessions):
        e = []
        for s in sessions:
            e += errs_by_run[s]
        return stats(e)
    e_g3n = {s: models["A0"][s]["errs"] for s in SESS}
    e_g4n = {s: g4_nested[s]["errs"] for s in SESS}
    e_g3f = {s: [grid.err[g3_frozen][i] for i in idx_sess[s]] for s in SESS}
    subsets = {"large_gemms_E136_E146_E159": {"G3_as_frozen": sub(e_g3f, ("E136", "E146", "E159")), "G3_nested": sub(e_g3n, ("E136", "E146", "E159")),
                                              "G4_nested": sub(e_g4n, ("E136", "E146", "E159"))},
               "E159_held_out": {"G3_as_frozen_blind": stats(e_g3f["E159"]), "G3_nested": stats(e_g3n["E159"]), "G4_nested": stats(e_g4n["E159"])}}
    per_run = []
    for s in SESS:
        for j, i in enumerate(idx_sess[s]):
            c = inp[i]
            per_run.append({"session": s, "run": c["run"], "cell": c["cell"], "meas": {q: round(c["meas"][q], 3) for q in RULE},
                            "T_start": round(c["T_start"], 2),
                            "G3_as_frozen": {q: round(grid.preds[g3_frozen][i][q], 3) for q in RULE},
                            "G3_nested": {q: round(grid.preds[models["A0"][s]["chosen"]][i][q], 3) for q in RULE},
                            "G4_nested": {q: round(grid.preds[g4_nested[s]["chosen"]][i][q], 3) for q in RULE},
                            "G4_final": {q: round(grid.preds[final][i][q], 3) for q in RULE}})
    farm = cfgs[final]
    g4 = {"_model": "G4 (Q140(q)): G3 plus the terms the registered forward rule kept, constants chosen on all five sessions", "registration": "49575094",
          "kept_terms": [t for t, ch in (("T_Z", "Z"), ("T_D", "D"), ("T_G", "G")) if ch in kept] + ["T_S (structural)"],
          "constants": {"k_W_per_C": farm["k"], "k_is": "T_D's k_D from T_ref" if farm.get("T_ref") else "G3's k_eff from the run's start die",
                        "T_ref_C": farm.get("T_ref"), "trip_C": farm["trip"], "zeros_level": bool(farm.get("zeros")),
                        "beta": G4.BETA if farm.get("zeros") else None, "delta_fallback_w": G4.DELTA_FALLBACK if farm.get("zeros") else None,
                        "dip": None if not farm.get("dip") else {"d_G": farm["dip"][0], "P_G_w": farm["dip"][1], "f_dip_mhz": G4.F_DIP}},
          "g3_frozen_base": {"commit": "91def7c4", "chain": "Q138(t) model-q138t.json a2", "burst_cap": [G.WB, G.SB], "off_share": G.OFF_SHARE, "anchor_s": G.ANCHOR_S,
                             "window_s": G.SUS_LAST_S},
          "final_in_sample": stats(grid.err[final]), "nested_pooled": stats(pooled(g4_nested))}
    out = {"what": "Q140(q) G4's registered fit, nested leave one session out over five sessions (65 sustained runs)", "registration": "49575094",
           "rows": {s: len(idx_sess[s]) for s in SESS}, "grids": {"k_eff": K_GRID, "trip": TRIP_GRID, "k_D": KD_GRID, "d_G": DG_GRID, "P_G": PG_GRID},
           "reproduction_check": dict(rep, worst_abs_diff=round(worst, 5)),
           "forward_steps": steps, "kept": kept, "final_key": list(final), "final_arm": {k: v for k, v in farm.items() if k != "lev_override"},
           "nested_choices": {name: {s: list(nest[s]["chosen"]) for s in SESS} for name, nest in models.items()},
           "pooled": {"G3_as_frozen": stats(ref["G3_as_frozen"]), "G3_nested": stats(ref["G3_nested"]), "G4_nested": stats(ref["G4_nested"]),
                      "G4_final_in_sample": stats(ref["G4_final_in_sample"])},
           "by_session": by_sess, "subsets": subsets,
           "paired_boot_G3_nested_minus_G4_nested_rms": boots, "paired_boot_G3_frozen_minus_G4_nested_rms": boots_frozen,
           "models_nested_pooled": {name: stats(pooled(nest)) for name, nest in models.items()}}
    json.dump(out, open(os.path.join(HERE, "loso-g4.json"), "w"), indent=1)
    json.dump(g4, open(os.path.join(HERE, "g4.json"), "w"), indent=1)
    json.dump(per_run, open(os.path.join(HERE, "rows-g4.json"), "w"), indent=0)
    print("FORWARD STEPS (held-out loss per session; carries if lower in >= 3 of 5 and pooled):")
    for st in steps:
        print(f"  {st['term']} vs {st['against']}: lower in {st['n_lower']} of 5 {st['sessions_lower']}; pooled {st['pooled_loss_prev']} -> {st['pooled_loss_new']}: "
              f"{'CARRIES, kept' if st['carries'] else 'does not carry'}; per session {st['per_session']}")
    print(f"kept: {kept or 'none'}; final key {final}; final arm {g4['constants']}")
    for name, nest in models.items():
        print(f"  nested choices {name}: " + ", ".join(f"{s} {nest[s]['chosen'][1:]}" for s in SESS))
    print("POOLED (measured - predicted):")
    for k, v_ in out["pooled"].items():
        print(f"  {k:20s} " + "  ".join(f"{q} {v_[q]['rms']:.3f} ({v_[q]['mean']:+.3f}) {v_[q]['inside']}/{v_[q]['n']}" for q in RULE))
    print("BY SESSION (rms):")
    for name, d in by_sess.items():
        print(f"  {name:14s} " + " | ".join(f"{s} {d[s]['mhz']['rms']:.1f} MHz {d[s]['w']['rms']:.2f} W {d[s]['die']['rms']:.2f} C" for s in SESS))
    print("SUBSETS:", json.dumps(subsets))
    print("paired bootstrap, G3 nested - G4 nested rms (95%):", boots)
    print("paired bootstrap, G3 as frozen - G4 nested rms (95%):", boots_frozen)


if __name__ == "__main__":
    main()
