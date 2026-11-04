#!/usr/bin/env python3
"""Q140(q): the corrections after verification, post hoc (Wed 4 Nov 2026, after the registered result e39d06da and its verifier's
report). Desk only, committed inputs only. Nothing here opens a device, and nothing frozen is changed, refitted or re-chosen.

    nice -n 10 /usr/bin/python3 -B corrections_q140q.py > corrections.txt      (writes corrections.json; 4 worker processes)

It imports the registered code (fit_g4.py, g4_model.py, checks_g4.py) unchanged, never a main(), and first reproduces
loso-g4.json's registered results exactly (C0). Every other number is a post hoc reading, never a verdict. The C numbers follow the
verifier's fault numbers:
  C1  the forward rule with the term selection itself nested inside each outer fold: an inner leave one session out on the four
      training sessions (constants chosen on three, scored on the fourth), the inner rule "lower in at least 3 of 4" or "2 of 4",
      and pooled; then the kept terms' constants chosen on the four and the held-out session predicted. Paired bootstraps of
      G3 nested - each reading, over runs (fit_g4.boot_paired, as registered) and over sessions (5 clusters), and a jackknife.
  C2  G4 as frozen, i.e. with T_S (M8's span fraction, checks_g4.check_iii's phi) on E136's four other-kind runs: (a) each fold's
      registered constants, (b) constants chosen with T_S in the training rows, (c) the final constants chosen on all five
      sessions with T_S, against g4.json's; and C1 and C2 together.
  C3  the stride term at the power-of-two collapses: SM's time error there against far shapes at other strides, and the step from
      each collapse to the nearest rung of its own ladder that is not one (measured, SM, ISO, STRICT; stride-sm.json's rows).
  C4  the dip clock at 600 and 650 MHz in place of E159 C1's 618 MHz (E159 held out, and pooled).
  C9  the dip's gate above its grid (P_G 60, 64, 68 W), in sample at g4.json's k and trip, d_G 0.09 and 0.12.
  C6  the stride scores split by session (ISO's retention curve was fitted on E158's cells).
  C7  check (i) across the k_D grid, and against a constant offset with no slope.
  C5  post hoc P3's measured span fractions, every burst.
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
import fit_g4 as FG  # noqa: E402  (the registered fit, imported unchanged)
import g4_model as G4  # noqa: E402

RULE, SESS = FG.RULE, FG.SESS
Q = tuple(RULE)
F_REG = 618.0
LARGE = ("E136", "E146", "E159")


# ------------------------------------------------------------------ configurations, built exactly as fit_g4.main builds them
def base_cfgs():
    c = {}
    for k, tr in itertools.product(FG.K_GRID, FG.TRIP_GRID):
        c[("A0", k, tr)] = {"k": k, "trip": tr}
        c[("Z", k, tr)] = {"k": k, "trip": tr, "zeros": True}
    for kd, tr in itertools.product(FG.KD_GRID, FG.TRIP_GRID):
        c[("ZD", kd, tr)] = {"k": kd, "trip": tr, "zeros": True, "T_ref": G4.T_REF}
        c[("D", kd, tr)] = {"k": kd, "trip": tr, "T_ref": G4.T_REF}
    return c


def g_cfgs(base, tag):
    """T_G's grid on the family `tag`, in fit_g4.main's order and key form"""
    out = {}
    for k0, arm in base.items():
        if k0[0] != tag:
            continue
        for dg, pg in itertools.product(FG.DG_GRID, FG.PG_GRID):
            if dg == 0 and pg != FG.PG_GRID[0]:
                continue
            out[(tag + "G",) + k0[1:] + (dg, pg)] = dict(arm, dip=(dg, pg))
    return out


# ------------------------------------------------------------------ the worker: fit_g4.eval_cfg's loop body on a subset of rows
def _init():
    FG._init()


def eval_task(task):
    """(name, key, arm, f_dip, rows) -> name, key, f_dip, rows, predictions; the per-run body is fit_g4.eval_cfg's"""
    name, key, arm, fdip, rows = task
    G4.F_DIP = fdip
    try:
        idx = list(range(len(FG.INP))) if rows is None else list(rows)
        out = []
        for i in idx:
            c = FG.INP[i]
            a = dict(arm)
            if "lev_override" in arm and c["run"] in arm["lev_override"] and c["session"] == "E136":
                a["lev"] = {int(f): v for f, v in arm["lev_override"][c["run"]].items()}
            out.append(G4.run_arm(c, a))
        return name, key, fdip, idx, out
    finally:
        G4.F_DIP = F_REG


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def boot_sessions(ea, eb, sess, n=10000, seed=141):
    """rms(ea) - rms(eb), the five sessions resampled with replacement (all of a drawn session's runs), 95%"""
    rng = np.random.default_rng(seed)
    ea, eb = np.asarray(ea), np.asarray(eb)
    by = {s: np.array([i for i, x in enumerate(sess) if x == s]) for s in SESS}
    d = []
    for _ in range(n):
        pick = rng.integers(0, len(SESS), len(SESS))
        ii = np.concatenate([by[SESS[j]] for j in pick])
        d.append(math.sqrt(np.mean(ea[ii] ** 2)) - math.sqrt(np.mean(eb[ii] ** 2)))
    return [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]


def main():
    inp = FG.load_inputs()
    sess = [c["session"] for c in inp]
    n = len(inp)
    order = [i for s in SESS for i in range(n) if sess[i] == s]   # fit_g4 pools in session order; so do the stats and bootstraps here

    def ro(v):
        return [v[i] for i in order]
    reg = json.load(open(os.path.join(HERE, "loso-g4.json")))
    g4j = json.load(open(os.path.join(HERE, "g4.json")))
    import checks_g4 as CK  # noqa: E402  (the registered checks, imported unchanged)

    # T_S's levels on E136's four other-kind runs, with check (iii)'s phi (M8's frozen D), as check_iii applies them
    c3 = CK.check_iii()
    ts_lev = {}
    for c in inp:
        if c["session"] == "E136" and (c["cell"].endswith("-real") or c["cell"].endswith("-sparse50")):
            t = c["type"]
            kind = "real" if c["cell"].endswith("-real") else "sparse50"
            ts_lev[c["run"]] = {f: float(v) for f, v in G4.levels_phi136("g4k", t, c3["phi"][f"{t}.{kind}"]["phi_M8"]).items()}
    ts_rows = [i for i, c in enumerate(inp) if c["session"] == "E136" and c["run"] in ts_lev]

    base = base_cfgs()
    cfgs = dict(base)
    cfgs.update(g_cfgs(base, "Z"))
    cfgs.update(g_cfgs(base, "ZD"))
    zg_keys = [k for k in cfgs if k[0] == "ZG"]
    tasks = [("main", k, a, F_REG, None) for k, a in cfgs.items()]
    tasks += [("ts", k, dict(a, lev_override=ts_lev), F_REG, ts_rows) for k, a in cfgs.items()]
    tasks += [("fdip", k, cfgs[k], f, None) for f in (600.0, 650.0) for k in zg_keys]
    kc, tc = g4j["constants"]["k_W_per_C"], g4j["constants"]["trip_C"]
    pg_cfgs = {("ZGx", kc, tc, dg, pg): {"k": kc, "trip": tc, "zeros": True, "dip": (dg, pg)} for dg in (0.09, 0.12) for pg in (52.0, 56.0, 60.0, 64.0, 68.0)}
    tasks += [("pg", k, a, F_REG, None) for k, a in pg_cfgs.items()]
    print(f"rows {n}; T_S rows {[inp[i]['cell'] for i in ts_rows]}; tasks {len(tasks)}", flush=True)
    with Pool(4, initializer=_init) as pool:
        res = pool.map(eval_task, tasks, chunksize=2)
    P = {}
    PTS = {}
    PF = {600.0: {}, 650.0: {}}
    PG = {}
    for name, key, fdip, idx, out in res:
        if name == "main":
            P[key] = out
        elif name == "ts":
            PTS[key] = dict(zip(idx, out))
        elif name == "pg":
            PG[key] = out
        else:
            PF[fdip][key] = out

    def ensure(tag):
        """a T_G family the inner rule reaches that is not computed yet (A0G, DG)"""
        if any(k[0] == tag for k in P):
            return
        extra = g_cfgs(base, tag[:-1])
        tk = [("main", k, a, F_REG, None) for k, a in extra.items()] + [("ts", k, dict(a, lev_override=ts_lev), F_REG, ts_rows) for k, a in extra.items()]
        with Pool(4, initializer=_init) as pool:
            for name, key, fdip, idx, out in pool.map(eval_task, tk, chunksize=2):
                if name == "main":
                    P[key] = out
                else:
                    PTS[key] = dict(zip(idx, out))
        cfgs.update(extra)
        print(f"computed {tag}: {len(extra)} configurations", flush=True)

    def errs(key, ts=False, pf=None):
        pr = (PF[pf][key] if pf else P[key])
        e = [{q: c["meas"][q] - p[q] for q in Q} for c, p in zip(inp, pr)]
        if ts:
            for i, p in PTS[key].items():
                e[i] = {q: inp[i]["meas"][q] - p[q] for q in Q}
        return e

    EC = {}

    def err_c(key, ts=False, pf=None):
        kk = (key, ts, pf)
        if kk not in EC:
            EC[kk] = errs(key, ts, pf)
        return EC[kk]

    def loss_on(key, sessions, ts=False, pf=None):
        return FG.loss_rows([x for x, s in zip(err_c(key, ts, pf), sess) if s in sessions])

    def best(keys, sessions, ts=False, pf=None):
        return min(keys, key=lambda k: loss_on(k, sessions, ts, pf))

    def keysof(tag):
        return [k for k in cfgs if k[0] == tag]

    def outer(tag_by_sess, ts_choose=False, ts_apply=False, pf=None):
        """per held-out session s: the family tag_by_sess[s], its constants chosen on the other four, s predicted"""
        e = [None] * n
        chosen = {}
        for s in SESS:
            train = [x for x in SESS if x != s]
            b = best(keysof(tag_by_sess[s]), train, ts_choose, pf)
            chosen[s] = list(b)
            ee = err_c(b, ts_apply, pf)
            for i in range(n):
                if sess[i] == s:
                    e[i] = ee[i]
        return e, chosen

    def st(e, subset=None):
        ii = [i for i in order if subset is None or sess[i] in subset]
        o = {}
        for q in Q:
            v = np.array([e[i][q] for i in ii])
            o[q] = {"rms": round(float(np.sqrt(np.mean(v ** 2))), 4), "mean": round(float(np.mean(v)), 4),
                    "inside": int(np.sum(np.abs(v) <= RULE[q])), "n": int(len(v))}
        o["loss"] = round(FG.loss_rows([e[i] for i in ii]), 3)
        return o

    out = {"what": "Q140(q) corrections after verification, post hoc (never a verdict); committed inputs only", "after": "e39d06da",
           "T_S_rows": [inp[i]["cell"] for i in ts_rows]}

    # ---------------------------------------------------------------- C0: the registered results, reproduced
    allS = {t: {s: None for s in SESS} for t in ("A0", "Z", "ZD", "ZG")}
    c0 = {}
    for tag in ("A0", "Z", "ZD", "ZG"):
        tot = 0.0
        for s in SESS:
            train = [x for x in SESS if x != s]
            b = best(keysof(tag), train)
            allS[tag][s] = b
            tot += loss_on(b, [s])
        c0[tag] = round(tot, 3)
    regsteps = {st_["term"]: st_ for st_ in reg["forward_steps"]}
    e_g3n, _ = outer({s: "A0" for s in SESS})
    e_g4n, ch_g4n = outer({s: "ZG" for s in SESS})
    fin = best(zg_keys, SESS)
    chk = {
        "pooled_losses": {"A0": c0["A0"], "Z": c0["Z"], "ZD": c0["ZD"], "ZG": c0["ZG"]},
        "registered": {"A0": regsteps["T_Z"]["pooled_loss_prev"], "Z": regsteps["T_Z"]["pooled_loss_new"], "ZD": regsteps["T_D"]["pooled_loss_new"],
                       "ZG": regsteps["T_G"]["pooled_loss_new"]},
        "nested_choices_equal": all(list(allS[t][s]) == reg["nested_choices"][t][s] for t in ("A0", "Z", "ZG") for s in SESS),
        "final_key": list(fin), "final_key_registered": reg["final_key"],
        "G4_nested_pooled": {q: st(e_g4n)[q]["rms"] for q in Q}, "G4_nested_registered": {q: reg["pooled"]["G4_nested"][q]["rms"] for q in Q},
        "G3_nested_pooled": {q: st(e_g3n)[q]["rms"] for q in Q}, "G3_nested_registered": {q: reg["pooled"]["G3_nested"][q]["rms"] for q in Q},
        "paired_boot_runs": {q: FG.boot_paired(ro([e[q] for e in e_g3n]), ro([e[q] for e in e_g4n])) for q in Q},
        "paired_boot_runs_registered": reg["paired_boot_G3_nested_minus_G4_nested_rms"]}
    # the subset worker against fit_g4.eval_cfg for the final key (all rows)
    FG.INP = inp
    _, ref = FG.eval_cfg((tuple(fin), cfgs[fin]))
    chk["eval_equal_fit_g4_eval_cfg_worst"] = max(abs(a[q] - b[q]) for a, b in zip(P[fin], ref) for q in Q)
    # check (iii)'s T_S errors at the final constants against this script's T_S rows
    t3 = {r["cell"]: r["err_G4_with_T_S"] for r in c3["runs"]}
    chk["T_S_rows_equal_check_iii_worst"] = max(abs(round(inp[i]["meas"][q] - PTS[fin][i][q], 3) - t3[inp[i]["cell"]][q]) for i in ts_rows for q in Q)
    ok = (all(abs(chk["pooled_losses"][t] - chk["registered"][t]) < 1e-9 for t in chk["registered"]) and chk["nested_choices_equal"]
          and chk["final_key"] == chk["final_key_registered"] and chk["G4_nested_pooled"] == chk["G4_nested_registered"]
          and chk["G3_nested_pooled"] == chk["G3_nested_registered"] and chk["paired_boot_runs"] == chk["paired_boot_runs_registered"]
          and chk["eval_equal_fit_g4_eval_cfg_worst"] == 0.0 and chk["T_S_rows_equal_check_iii_worst"] <= 0.0011)
    chk["ok"] = ok
    out["C0_reproduction"] = chk
    print("C0 REPRODUCTION of loso-g4.json:", json.dumps(chk), flush=True)
    if not ok:
        raise SystemExit("C0 failed: the registered results are not reproduced")

    readings = {"G3_nested (before)": e_g3n, "G4_nested_without_T_S (registered)": e_g4n}

    # ---------------------------------------------------------------- C1: the term selection nested
    c1 = {}
    for need in (3, 2):
        tag_by, logs = {}, {}
        for s in SESS:
            train = [x for x in SESS if x != s]

            def nl(tag):
                ks = keysof(tag)
                return {u: loss_on(best(ks, [x for x in train if x != u]), [u]) for u in train}
            cur, prev, log = "A0", nl("A0"), []
            for term in ("T_Z", "T_D", "T_G"):
                tag = {"T_Z": "Z", "T_D": "ZD" if cur == "Z" else "D", "T_G": cur + "G"}[term]
                ensure(tag)
                new = nl(tag)
                lower = [u for u in train if new[u] < prev[u] - 1e-9]
                carries = len(lower) >= need and sum(new.values()) < sum(prev.values()) - 1e-9
                log.append({"term": term, "tag": tag, "n_lower": len(lower), "of": len(train), "pooled_prev": round(sum(prev.values()), 3),
                            "pooled_new": round(sum(new.values()), 3), "carries": carries})
                if carries:
                    cur, prev = tag, new
            tag_by[s], logs[s] = cur, log
        e, chosen = outer(tag_by)
        e_ts, chosen_ts = outer(tag_by, ts_choose=False, ts_apply=True)
        e_ts2, chosen_ts2 = outer(tag_by, ts_choose=True, ts_apply=True)
        c1[f"inner_{need}_of_4"] = {"kept_by_fold": tag_by, "chosen": chosen, "inner_logs": logs, "pooled": st(e), "large_gemms": st(e, LARGE),
                                    "E159": st(e, ("E159",)),
                                    "with_T_S_registered_way": {"pooled": st(e_ts), "large_gemms": st(e_ts, LARGE), "chosen": chosen_ts},
                                    "with_T_S_in_choice": {"pooled": st(e_ts2), "large_gemms": st(e_ts2, LARGE), "chosen": chosen_ts2}}
        readings[f"G4_selection_nested_{need}_of_4"] = e
        readings[f"G4_selection_nested_{need}_of_4_with_T_S"] = e_ts
    out["C1_selection_nested"] = c1

    # ---------------------------------------------------------------- C2: G4 as frozen, with T_S
    e_a, ch_a = outer({s: "ZG" for s in SESS}, ts_choose=False, ts_apply=True)
    e_b, ch_b = outer({s: "ZG" for s in SESS}, ts_choose=True, ts_apply=True)
    fin_ts = best(zg_keys, SESS, ts=True)
    c2 = {"a_registered_fold_constants": {"pooled": st(e_a), "large_gemms": st(e_a, LARGE), "E136": st(e_a, ("E136",)), "chosen": ch_a,
                                          "equal_registered_choices": ch_a == {s: reg["nested_choices"]["ZG"][s] for s in SESS}},
          "b_constants_chosen_with_T_S": {"pooled": st(e_b), "large_gemms": st(e_b, LARGE), "E136": st(e_b, ("E136",)), "chosen": ch_b},
          "c_final_constants_with_T_S": {"key": list(fin_ts), "g4_json_key": reg["final_key"], "equal": list(fin_ts) == reg["final_key"],
                                         "in_sample_with_T_S_at_g4_json_key": st(err_c(tuple(reg["final_key"]), True)),
                                         "in_sample_with_T_S_at_its_own_key": st(err_c(fin_ts, True))},
          "without_T_S_registered": {"pooled": st(e_g4n), "large_gemms": st(e_g4n, LARGE), "E136": st(e_g4n, ("E136",))},
          "G3_nested": {"pooled": st(e_g3n), "large_gemms": st(e_g3n, LARGE), "E136": st(e_g3n, ("E136",))},
          "rows": {inp[i]["cell"]: {"without_T_S": {q: round(e_g4n[i][q], 3) for q in Q}, "with_T_S": {q: round(e_a[i][q], 3) for q in Q}} for i in ts_rows}}
    out["C2_G4_as_frozen_with_T_S"] = c2
    readings["G4_as_frozen_with_T_S (a)"] = e_a
    readings["G4_as_frozen_with_T_S (b)"] = e_b

    # ---------------------------------------------------------------- bootstraps and jackknife against G3 nested
    boots = {}
    sess_o = ro(sess)
    for name, e in readings.items():
        if name.startswith("G3_nested"):
            continue
        a = {q: ro([x[q] for x in e_g3n]) for q in Q}
        b = {q: ro([x[q] for x in e]) for q in Q}
        jk = {}
        for s in SESS:
            ii = [i for i in range(n) if sess_o[i] != s]
            jk[s] = {q: round(rms([a[q][i] for i in ii]) - rms([b[q][i] for i in ii]), 4) for q in Q}
        boots[name] = {"rms": {q: round(rms(b[q]), 4) for q in Q}, "gain": {q: round(rms(a[q]) - rms(b[q]), 4) for q in Q},
                       "paired_boot_runs": {q: FG.boot_paired(a[q], b[q]) for q in Q},
                       "paired_boot_sessions": {q: boot_sessions(a[q], b[q], sess_o) for q in Q},
                       "jackknife_gain_range": {q: [min(jk[s][q] for s in SESS), max(jk[s][q] for s in SESS)] for q in Q}}
    out["gains_against_G3_nested"] = boots

    # ---------------------------------------------------------------- C4: the dip clock
    c4 = {}
    for f in (600.0, 650.0):
        e, ch = outer({s: "ZG" for s in SESS}, pf=f)
        c4[str(f)] = {"E159": st(e, ("E159",)), "E159_chosen": ch["E159"], "pooled": st(e)}
    c4["618.0"] = {"E159": st(e_g4n, ("E159",)), "E159_chosen": ch_g4n["E159"], "pooled": st(e_g4n)}
    out["C4_dip_clock"] = c4

    # ---------------------------------------------------------------- C9: the dip's gate above its grid, in sample
    c9 = {}
    for key in pg_cfgs:
        e = [{q: c["meas"][q] - p[q] for q in Q} for c, p in zip(inp, PG[key])]
        c9[f"d_G {key[3]} P_G {key[4]}"] = st(e)
    same = ("ZG",) + tuple(reg["final_key"][1:])
    c9["check_equal_registered_final"] = max(abs(a[q] - b[q]) for a, b in zip(PG[("ZGx",) + same[1:]], P[same]) for q in Q)
    out["C9_gate_above_grid_in_sample"] = c9

    # ---------------------------------------------------------------- C6: the stride scores by session
    sm = json.load(open(os.path.join(HERE, "stride-sm.json")))
    c6 = {}
    for s in ("E158", "E146"):
        rr = [r for r in sm["rows"] if r["session"] == s]
        c6[s] = {"n": len(rr)}
        for m in ("SM", "ISO", "STRICT"):
            c6[s][m] = round(rms([r[m]["rel"] for r in rr]), 4)
    rr = sm["rows"]
    c6["all"] = {"n": len(rr), **{m: round(rms([r[m]["rel"] for r in rr]), 4) for m in ("SM", "ISO", "STRICT")}}
    far = [r for r in rr if r["SM"]["rel"] < -0.10]
    c6["SM_below_minus_10pct"] = sorted(((r["session"] + ":" + r["cell"], round(r["SM"]["rel"], 4)) for r in far), key=lambda x: x[1])
    out["C6_stride_by_session"] = c6

    # ---------------------------------------------------------------- C3: the power-of-two collapses
    R = {r["session"] + ":" + r["cell"]: r for r in sm["rows"]}
    coll = ["E146:D4.fp32", "E146:D8.fp32", "E158:D4.fp32", "E158:K4n8.fp32", "E158:K6n4.fp32"]   # S2's five (stride-sm.txt)
    pairs = [("E146:D4.fp32", "E146:D2.fp32"), ("E146:D8.fp32", "E146:D2.fp32"), ("E158:D4.fp32", "E158:D2.fp32"),
             ("E158:K4n8.fp32", "E158:K4n7.fp32"), ("E158:K6n4.fp32", "E158:K6n3.fp32"), ("E158:K6n4.fp32", "E158:K6n5.fp32")]
    c3 = {"rule": "each of S2's five collapses (fp32) against the nearest rung of its own ladder that is not a collapse, on each side where one "
                  "exists (D8's nearest, D4, is one, so D2); the step is the collapse's T800 over that rung's",
          "SM_rel_at_collapses": {k: round(R[k]["SM"]["rel"], 4) for k in coll},
          "SM_rel_far_fp32_other_strides": dict(sorted(((k, round(r["SM"]["rel"], 4)) for k, r in R.items()
                                                        if k.endswith(".fp32") and k not in coll and r["SM"]["rel"] < -0.10), key=lambda x: x[1])),
          "far_B_share_S3": {k: v for k, v in sm["S3_shares"].items()} if isinstance(sm.get("S3_shares"), dict) else sm.get("S3_shares"),
          "steps": []}
    for a, b in pairs:
        row = {"collapse": a, "rung": b, "measured": round(R[a]["T800_meas"] / R[b]["T800_meas"], 4)}
        for m in ("SM", "ISO", "STRICT"):
            row[m] = round(R[a][m]["T800"] / R[b][m]["T800"], 4)
        row["SM_closer_than_ISO"] = abs(row["SM"] - row["measured"]) < abs(row["ISO"] - row["measured"])
        row["SM_closer_than_STRICT"] = abs(row["SM"] - row["measured"]) < abs(row["STRICT"] - row["measured"])
        c3["steps"].append(row)
    c3["SM_closer_than_ISO"] = f"{sum(r['SM_closer_than_ISO'] for r in c3['steps'])} of {len(pairs)}"
    c3["SM_closer_than_STRICT"] = f"{sum(r['SM_closer_than_STRICT'] for r in c3['steps'])} of {len(pairs)}"
    out["C3_collapses"] = c3

    # ---------------------------------------------------------------- C7: check (i) across k_D, and a constant offset
    r158 = json.load(open(os.path.join(G4.LAB, "docs/reports/data/2026-11-03-e158-l3-retention/results.json")))
    R7, cells = r158["rules"]["R7"]["cells"], r158["cells"]
    ez, dts = [], []
    for c, v in sorted(R7.items()):
        t = c.split("-")[1]
        ds = [x for x in cells[c]["burst_die_start"] if x is not None]
        Ts = sum(ds) / len(ds)
        ez.append(v["p800_w"] - v["P0"] - G4.BETA * G4.DELTA_FALLBACK[t])
        dts.append(Ts - G4.T_REF)
    ez, dts = np.array(ez), np.array(dts)
    c7 = {"n": int(len(ez)), "die_start_C": [round(float(dts.min() + G4.T_REF), 2), round(float(dts.max() + G4.T_REF), 2)],
          "die_start_minus_T_ref_C": [round(float(dts.min()), 2), round(float(dts.max()), 2)], "T_Z_alone": {"rms": round(rms(ez), 3), "mean": round(float(ez.mean()), 3)}}
    for kd in FG.KD_GRID:
        e = ez - kd * dts
        c7[f"k_D_{kd}"] = {"rms": round(rms(e), 3), "mean": round(float(e.mean()), 3)}
        e0 = ez - kd * float(dts.mean())
        c7[f"offset_only_{kd}"] = {"rms": round(rms(e0), 3), "mean": round(float(e0.mean()), 3), "offset_w": round(kd * float(dts.mean()), 3)}
    c7["best_constant_offset"] = {"rms": round(float(ez.std()), 3), "offset_w": round(float(ez.mean()), 3)}
    c7["registered_value_reproduced"] = c7["k_D_0.47"]["rms"] == json.load(open(os.path.join(HERE, "checks-g4.json")))["i_E158_zeros_bursts"]["rms"]["err_ZD"]
    out["C7_check_i"] = c7

    # ---------------------------------------------------------------- C5: P3's fractions
    ph = json.load(open(os.path.join(HERE, "posthoc-g4.json")))
    out["C5_P3"] = [{"cell": r["cell"], "measured": r["span_fraction_measured_in_bursts"], "phi_M8": r["phi_M8"]} for r in ph["P3_E136_bursts"]["rows"]]

    json.dump(out, open(os.path.join(HERE, "corrections.json"), "w"), indent=1)

    # ---------------------------------------------------------------- printout
    def line(o):
        return "  ".join(f"{q} {o[q]['rms']:.3f} ({o[q]['mean']:+.3f}) {o[q]['inside']}/{o[q]['n']}" for q in Q) + f"  loss {o['loss']}"
    print("\nC1 (post hoc): the forward rule with the term selection nested in each outer fold")
    for k, v in c1.items():
        print(f"  {k}: kept by fold {v['kept_by_fold']}")
        for s in SESS:
            print(f"     {s}: " + "; ".join(f"{x['term']} {x['n_lower']}/{x['of']} {x['pooled_prev']}->{x['pooled_new']} {'kept' if x['carries'] else 'not'}"
                                         for x in v["inner_logs"][s]) + f"; constants {v['chosen'][s][1:]}")
        print(f"     pooled       {line(v['pooled'])}")
        print(f"     large GEMMs  {line(v['large_gemms'])}")
        print(f"     E159         {line(v['E159'])}")
        print(f"     + T_S (fold constants as built)   pooled {line(v['with_T_S_registered_way']['pooled'])}")
        print(f"                                       large  {line(v['with_T_S_registered_way']['large_gemms'])}")
        print(f"     + T_S (constants chosen with it)  pooled {line(v['with_T_S_in_choice']['pooled'])}")
    print("\nC2 (post hoc): G4 as frozen, with T_S on E136's four other-kind runs")
    for k in ("without_T_S_registered", "a_registered_fold_constants", "b_constants_chosen_with_T_S", "G3_nested"):
        v = c2[k]
        print(f"  {k:30s} pooled {line(v['pooled'])}")
        print(f"  {'':30s} large  {line(v['large_gemms'])}")
        print(f"  {'':30s} E136   {line(v['E136'])}")
    print(f"  (a) fold constants equal the registered: {c2['a_registered_fold_constants']['equal_registered_choices']}; (b) chosen {c2['b_constants_chosen_with_T_S']['chosen']}")
    print(f"  (c) final constants chosen with T_S: {c2['c_final_constants_with_T_S']['key']} against g4.json's {reg['final_key']}: equal {c2['c_final_constants_with_T_S']['equal']}")
    for cell, v in c2["rows"].items():
        print(f"     {cell:20s} without T_S {v['without_T_S']} | with T_S {v['with_T_S']}")
    print("\nGAINS against G3 nested (rms G3 nested - rms reading; 95%: over runs as registered; over sessions; jackknife range)")
    for name, v in boots.items():
        print(f"  {name}")
        for q in Q:
            print(f"     {q:4s} rms {v['rms'][q]:.3f}  gain {v['gain'][q]:+.3f}  runs {v['paired_boot_runs'][q]}  sessions {v['paired_boot_sessions'][q]}  jackknife {v['jackknife_gain_range'][q]}")
    print("\nC4 (post hoc): the dip clock")
    for f in ("600.0", "618.0", "650.0"):
        print(f"  {f} MHz: E159 {line(c4[f]['E159'])} chosen {c4[f]['E159_chosen']}; pooled {line(c4[f]['pooled'])}")
    print("\nC9 (post hoc, in sample at g4.json's k and trip): the dip's gate above its grid (44-56 W)")
    for k, v in c9.items():
        if k.startswith("d_G"):
            print(f"  {k}: {line(v)}")
    print(f"  ZGx at g4.json's constants equals the registered final row: worst |diff| {c9['check_equal_registered_final']}")
    print("\nC3: the stride term at the power-of-two collapses (fp32)")
    print("  SM's time error at the collapses: " + ", ".join(f"{k} {v:+.3f}" for k, v in c3["SM_rel_at_collapses"].items()))
    print("  SM's time error on far fp32 shapes at other strides (below -10%): " + ", ".join(f"{k} {v:+.3f}" for k, v in c3["SM_rel_far_fp32_other_strides"].items()))
    print(f"  the step, collapse T800 over the nearest rung that is not one ({c3['rule']}):")
    for r in c3["steps"]:
        print(f"     {r['collapse']:16s} / {r['rung']:16s} measured {r['measured']:.3f}  SM {r['SM']:.3f}  ISO {r['ISO']:.3f}  STRICT {r['STRICT']:.3f}")
    print(f"  SM's step closer to the card's than ISO's: {c3['SM_closer_than_ISO']}; than STRICT's: {c3['SM_closer_than_STRICT']}")
    print("\nC6: the stride term's T800 rms by session (ISO's curve was fitted on E158's cells)")
    for s in ("E158", "E146", "all"):
        print(f"  {s}: n {c6[s]['n']}  SM {c6[s]['SM']:.4f}  ISO {c6[s]['ISO']:.4f}  STRICT {c6[s]['STRICT']:.4f}")
    print("  SM below -10%: " + ", ".join(f"{a} {b:+.3f}" for a, b in c6["SM_below_minus_10pct"]))
    print("\nC7: check (i), E158's zeros bursts, p800 - predicted (W)")
    print(f"  die starts {c7['die_start_C']} C, i.e. {c7['die_start_minus_T_ref_C']} C from T_ref; T_Z alone {c7['T_Z_alone']}")
    for kd in FG.KD_GRID:
        print(f"  k_D {kd}: die law {c7[f'k_D_{kd}']}; its offset alone at the mean start {c7[f'offset_only_{kd}']}")
    print(f"  the best constant offset: {c7['best_constant_offset']}; k_D 0.47 reproduces checks-g4.json: {c7['registered_value_reproduced']}")
    print("\nC5: P3's measured span fractions in E136's bursts against M8's phi")
    for r in out["C5_P3"]:
        print(f"  {r['cell']:20s} measured {r['measured']}  phi_M8 {r['phi_M8']}")


if __name__ == "__main__":
    main()
