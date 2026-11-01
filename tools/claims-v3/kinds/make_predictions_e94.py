#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E94 (Q132): write predictions-e94.json, E94's freeze, from committed sources only. Every number below is read from the
file it names, or computed here from those files, never retyped; each source is recorded with its sha256.

    python3 tools/claims-v3/kinds/make_predictions_e94.py      # writes predictions-e94.json

What it freezes, before any E94 data exist:
  per tile   its gate share and bus bits (e94/e94.json); Q130(n)'s predictor's point (real/make_real.py, fitted on E78's 51
             kinds, unchanged) and its delta against E78's committed tile of the rule, on aifoundry3's scale and on card 1's
             (divided by E82's per-type card scale); the gate law's delta on card 1;
  per rule   kinds.json's replicate band; the between-draw SD and the committed tile's offset each law expects, from 400
             simulated draws of the rule (seed tags "E94-sim/<type>/<kind>/<r>"), and E90's numbers on aifoundry3;
  desk table the same two laws on every other random kind of the table, so the rows no card runs here carry a frozen number;
  rules      thresholds, bands and the power of each rule by simulation.

The gate law (noticed on E90's published draws at the desk before this freeze, never tested on new tiles):
    D(draw) = D(committed) x (1 - gate share of the draw) / (1 - gate share of the committed tile)
Power is proportional to the live share of lane-cycles. It has no fitted number; its one input is the committed tile's D.
"""
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "real"))
import make_kinds as mk  # noqa: E402
import make_real as mr  # noqa: E402

E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E82_JSON = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json"
E82_NODIPS = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json"
E82_SCORED = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json"
E90_JSON = "docs/reports/data/2026-10-31-e90-signs-spread/e90.json"
E90_SCORED = "docs/reports/data/2026-10-31-e90-signs-spread/scored.json"
E94_JSON = f"{K}/e94/e94.json"
REUSED = ("tools/claims-v3/lib.sh", f"{K}/e78_common.py", f"{K}/run_e78.py", f"{K}/reduce_e78.py", f"{K}/kinds.json")
E94_BOX_FILES = tuple(f"{K}/{f}" for f in ("e94_common.py", "run_e94.py", "reduce_e94.py", "block_e94.sh", "queue_e94.sh",
                                           "run_e94.sh", "make_e94.py"))
N_SIM = 400
REP_BAND = {"fp32": 0.50, "fp16": 0.50, "int8": 0.25}     # E86-R5's session-tie bands; E90-R4's band for fp32/fp16
GATED_RULES = ("fp32.sparse50", "fp16.nn_like", "fp32.nn_like", "int8.sparse50")
FLOAT_GATED = ("fp32.sparse50", "fp16.nn_like", "fp32.nn_like")
DENSE_FLOAT = ("fp32.randn", "fp16.randn", "fp16.uniform01")
INT8_RULES = ("int8.full", "int8.sparse50")
X_FLOAT = 0.30            # R4a
X_INT8 = 0.25             # R4b
BRIDGED = ("fp32.sparse50", "fp16.nn_like", "fp16.uniform01")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def seed_of(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "little")


def draw_raw(t, kind, rng):
    """One fresh tile of a rule; word-granular rules as make_kinds.replicate_draws builds them."""
    if kind.startswith("wsparse"):
        base = "full" if t == "int8" else "randn"
        a, b = mk.draw_elements(t, base, rng)
        aw, bw = mk.words_of(mk.encode(a, b, t))
        return mk.from_words(*mk.word_sparsify(aw, bw, int(kind[len("wsparse"):]) / 100.0, rng))
    a, b = mk.draw_elements(t, kind, rng)
    return mk.encode(a, b, t)


def t975(df):
    table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
             11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086}
    return table.get(max(df, 1), 1.96 + 2.4 / max(df, 1))


def main():
    e78 = load(E78_JSON)
    e82 = load(E82_JSON)
    nod = load(E82_NODIPS)
    s82 = load(E82_SCORED)
    e90 = load(E90_JSON)
    s90 = load(E90_SCORED)
    spec = load(E94_JSON)
    kinds = load(f"{K}/kinds.json")
    scale = s82["cross_card"]["primary"]["x3"]["per_type_median"]
    P, rows = mr.fit_predictor(e78, ROOT)

    def q(raw, t):
        return mr.predict_D(P, t, mr.features(raw, t), rows[t])

    D78 = {n: v["D"]["mean"] for n, v in e78["items"].items()}
    D82 = {n: v["D"]["mean"] for n, v in e82["items"].items()}
    Dn = {n: v["D"]["mean"] for n, v in nod["items"].items()}

    def nod_sd(name):
        v = [nod["per_pass"][str(p)][name]["D"] for p in nod["passes"] if name in nod["per_pass"][str(p)]]
        return statistics.stdev(v)

    rules = {}
    tiles = {}
    for rule_name, n in spec["rules"].items():
        t, kind = rule_name.split(".", 1)
        v = kinds["kinds"][t][kind]
        raw_c = open(os.path.join(HERE, v["file"]), "rb").read()
        qc = q(raw_c, t)
        g_c = v["stats"]["gated_lane_frac"]
        rep = v["replicates"]
        # 400 simulated draws of the rule, beside kinds.json's replicates (which count only gate share and bus bits)
        pts, gs = [], []
        for r in range(N_SIM):
            raw = draw_raw(t, kind, np.random.default_rng(seed_of(f"E94-sim/{t}/{kind}/{r}")))
            f = mr.features(raw, t)
            pts.append(mr.predict_D(P, t, f, rows[t])["point_w"])
            gs.append(1.0 - f["u"])
        pts, gs = np.array(pts), np.array(gs)
        D_c = Dn[rule_name]
        slope = D_c / (1.0 - g_c)
        law_q = {"mean_a3_w": round(float(pts.mean()), 4), "sd_a3_w": round(float(pts.std(ddof=1)), 4),
                 "sd_card1_w": round(float(pts.std(ddof=1)) / scale[t], 4),
                 "committed_point_a3_w": qc["point_w"],
                 "committed_minus_mean_a3_w": round(qc["point_w"] - float(pts.mean()), 4),
                 "committed_minus_mean_card1_w": round((qc["point_w"] - float(pts.mean())) / scale[t], 4),
                 "z": round((qc["point_w"] - float(pts.mean())) / max(float(pts.std(ddof=1)), 1e-9), 3)}
        law_g = {"slope_w_per_unit_live_share": round(slope, 4),
                 "sd_card1_w": round(slope * rep["gated_lane_frac"]["sd"], 4),
                 "committed_minus_mean_card1_w": round(slope * (rep["gated_lane_frac"]["mean"] - g_c), 4),
                 "z": round((g_c - rep["gated_lane_frac"]["mean"]) / rep["gated_lane_frac"]["sd"], 3)
                 if rep["gated_lane_frac"]["sd"] else 0.0}
        rec = {"type": t, "kind": kind, "committed": rule_name, "committed_is_anchor": rule_name in
               ("fp32.randn", "fp16.randn", "int8.full"), "committed_sha256": v["sha256"],
               "committed_gated_lane_frac": g_c, "committed_bus_bits_per_op": v["stats"]["bus_bits_per_op"],
               "replicates": {q_: rep[q_] for q_ in ("gated_lane_frac", "bus_bits_per_op")},
               "committed_inside_band": {q_: bool(rep[q_]["p2.5"] <= v["stats"][q_] <= rep[q_]["p97.5"])
                                         for q_ in ("gated_lane_frac", "bus_bits_per_op")},
               "committed_bus_z": round((v["stats"]["bus_bits_per_op"] - rep["bus_bits_per_op"]["mean"]) /
                                        rep["bus_bits_per_op"]["sd"], 3),
               "D_e78_a3_w": round(D78[rule_name], 4), "D_e82_card1_w": round(D82[rule_name], 4),
               "D_e82_nodips_card1_w": round(D_c, 4),
               "e82_nodips_between_pass_sd_w": round(nod_sd(rule_name), 4),
               "law_q130n": law_q, "law_gate": law_g,
               "law_bus": {"sd_card1_w": round(D_c / rep["bus_bits_per_op"]["mean"] * rep["bus_bits_per_op"]["sd"], 4),
                           "committed_minus_mean_card1_w": round(D_c * (1.0 - rep["bus_bits_per_op"]["mean"] /
                                                                        v["stats"]["bus_bits_per_op"]), 4),
                           "what": "power proportional to the operand-bus bits: D(committed) x bus(draw) / bus(committed)"},
               "band_w": REP_BAND[t], "scale": scale[t],
               "fresh": [], "bridge": []}
        rules[rule_name] = rec
    for name, e in spec["tiles"].items():
        t = e["type"]
        c = e["rule_of"]
        raw = open(os.path.join(HERE, "e94", e["file"]), "rb").read()
        qd = q(raw, t)
        pc = rules[c]["law_q130n"]["committed_point_a3_w"]
        g_c = rules[c]["committed_gated_lane_frac"]
        g = e["stats"]["gated_lane_frac"]
        dg = rules[c]["D_e82_nodips_card1_w"] * ((1.0 - g) / (1.0 - g_c) - 1.0)
        tiles[name] = {"type": t, "rule_of": c, "group": e["group"], "sha256": e["sha256"], "seed_tag": e["seed_tag"],
                       "gated_lane_frac": g, "bus_bits_per_op": e["stats"]["bus_bits_per_op"],
                       "inside_rule_band": e.get("inside_rule_band"),
                       "q130n_point_a3_w": qd["point_w"], "q130n_pi95_a3_w": qd["pi95_w"],
                       "q130n_delta_a3_w": round(qd["point_w"] - pc, 4),
                       "q130n_delta_card1_w": round((qd["point_w"] - pc) / scale[t], 4),
                       "gate_law_delta_card1_w": round(dg, 4),
                       "bus_law_delta_card1_w": round(rules[c]["D_e82_nodips_card1_w"] *
                                                      (e["stats"]["bus_bits_per_op"] / rules[c]["committed_bus_bits_per_op"] - 1.0), 4),
                       "D_pred_q130n_card1_w": round(rules[c]["D_e82_nodips_card1_w"] + (qd["point_w"] - pc) / scale[t], 4),
                       "D_pred_gate_law_card1_w": round(rules[c]["D_e82_nodips_card1_w"] + dg, 4)}
        rules[c]["fresh" if e["group"] == "draw" else "bridge"].append(name)
    # E90's numbers on aifoundry3, the other card of the bridge (R8), read from E90's committed scoring
    for c in BRIDGED:
        r = rules[c]
        sp = s90["spread"][c]
        r["e90_a3"] = {"D_committed_w": round(sp["D_means_w"][0], 4),
                       "D_draws_w": [round(x, 4) for x in sp["D_means_w"][1:]],
                       "sd_between_tiles_w": round(sp["sd_between_tiles_w"], 4),
                       "sd_between_passes_one_tile_w": round(sp["sd_between_passes_one_tile_w"], 4)}
    bridge = {}
    for name in tiles:
        if tiles[name]["group"] != "bridge":
            continue
        d = s90["draws"][spec["tiles"][name]["e90_name"]]
        m = d["minus_committed_w"]
        bridge[name] = {"e90_name": spec["tiles"][name]["e90_name"], "offset_a3_w": round(m["mean"], 4),
                        "offset_a3_se_w": round(m["se"], 4), "scale": rules[tiles[name]["rule_of"]]["scale"]}
    # the gate law, read back on E90's published draws (where it was noticed): the backdrop to E94-R6, not a test of it
    retro, q_retro = [], []
    for name, b in bridge.items():
        c = tiles[name]["rule_of"]
        if c not in GATED_RULES:
            continue
        g_c = rules[c]["committed_gated_lane_frac"]
        pred = rules[c]["e90_a3"]["D_committed_w"] * ((1.0 - tiles[name]["gated_lane_frac"]) / (1.0 - g_c) - 1.0)
        retro.append({"draw": name, "offset_a3_w": b["offset_a3_w"], "gate_law_a3_w": round(pred, 4),
                      "q130n_a3_w": tiles[name]["q130n_delta_a3_w"]})
    retrospective = {"what": "the gate law and Q130(n) on E90's six gated draws, aifoundry3; known before this freeze",
                     "draws": retro,
                     "gate_law_rms_w": round(math.sqrt(sum((x["offset_a3_w"] - x["gate_law_a3_w"]) ** 2 for x in retro) / len(retro)), 4),
                     "q130n_rms_w": round(math.sqrt(sum((x["offset_a3_w"] - x["q130n_a3_w"]) ** 2 for x in retro) / len(retro)), 4),
                     "no_offset_rms_w": round(math.sqrt(sum(x["offset_a3_w"] ** 2 for x in retro) / len(retro)), 4)}
    # ------------------------------------------------- the desk table: every other random kind of the table
    desk = {}
    for t in ("fp32", "fp16", "int8"):
        for kind, v in kinds["kinds"][t].items():
            nm = f"{t}.{kind}"
            rep = v.get("replicates")
            if not rep or kind.endswith("sorted"):
                continue
            g_c = v["stats"]["gated_lane_frac"]
            raw_c = open(os.path.join(HERE, v["file"]), "rb").read()
            pc = q(raw_c, t)["point_w"]
            pts = []
            for r in range(N_SIM):
                raw = draw_raw(t, kind, np.random.default_rng(seed_of(f"E94-sim/{t}/{kind}/{r}")))
                pts.append(mr.predict_D(P, t, mr.features(raw, t), rows[t])["point_w"])
            pts = np.array(pts)
            g_m, g_s = rep["gated_lane_frac"]["mean"], rep["gated_lane_frac"]["sd"]
            row = {"gated_committed": g_c, "gated_rule_mean": g_m, "gated_rule_sd": g_s, "gated_band":
                   [rep["gated_lane_frac"]["p2.5"], rep["gated_lane_frac"]["p97.5"]],
                   "bus_committed": v["stats"]["bus_bits_per_op"], "bus_rule_mean": rep["bus_bits_per_op"]["mean"],
                   "bus_rule_sd": rep["bus_bits_per_op"]["sd"],
                   "D_e78_a3_w": round(D78[nm], 4), "D_e82_card1_w": round(D82[nm], 4),
                   "q130n_sd_a3_w": round(float(pts.std(ddof=1)), 4),
                   "q130n_committed_minus_mean_a3_w": round(pc - float(pts.mean()), 4),
                   "measured_by_e94": nm in rules}
            if g_c < 1.0:
                sl = D78[nm] / (1.0 - g_c)
                row["gate_law_sd_a3_w"] = round(sl * g_s, 4)
                row["gate_law_committed_minus_mean_a3_w"] = round(sl * (g_m - g_c), 4)
            desk[nm] = row
    # ------------------------------------------------- power, by simulation (normal tile and noise components)
    rng = np.random.default_rng(seed_of("E94-power"))
    power = {"sims": 20000, "note": "tile component and committed offset at each law's expectation, one tile's between-pass SD "
             "at E82's dips-removed value on this card"}

    def sim_rule(k, tau, sig, delta, band, n, sims=20000):
        tau_i = rng.normal(0, tau, (sims, k))
        nz = rng.normal(0, sig / math.sqrt(n), (sims, k))
        y = tau_i + nz
        yc = delta + rng.normal(0, sig / math.sqrt(n), sims)
        ms = sig ** 2 * rng.chisquare(k * (n - 1), sims) / (k * (n - 1))
        ybar, s2 = y.mean(axis=1), y.var(axis=1, ddof=1)
        D = yc - ybar
        tk = t975(k - 1)
        # the offset's interval as score_e94 computes it: Satterthwaite's df for s^2/k (k-1 df) + MS_res/n (k(n-1) df)
        var = s2 / k + ms / n
        dfs = var ** 2 / ((s2 / k) ** 2 / (k - 1) + (ms / n) ** 2 / (k * (n - 1)))
        tq = np.array([t975(int(x)) for x in np.minimum(dfs, 1000)])
        hw = tq * np.sqrt(var)
        pi = tk * np.sqrt(s2) * math.sqrt(1 + 1 / k)
        own = t975(k * (n - 1)) * np.sqrt(ms / n)
        r1 = np.where(np.abs(D) + own <= pi, 0, np.where(np.abs(D) - own > pi, 1, 2))
        r2 = np.where(np.abs(D) + hw <= band, 0, np.where((np.abs(D) - hw > 0) & (np.abs(D) >= band), 1, 2))
        f = lambda a, v: round(float(np.mean(a == v)), 3)  # noqa: E731
        return {"R1_inside": f(r1, 0), "R1_outside": f(r1, 1), "R1_inconclusive": f(r1, 2),
                "R2_no_correction": f(r2, 0), "R2_correction": f(r2, 1), "R2_unresolved": f(r2, 2),
                "kind_mean_halfwidth_median_w": round(float(np.median(tk * np.sqrt(s2 / k))), 3)}

    for c, r in rules.items():
        k = len(r["fresh"]) + len(r["bridge"])
        sig = r["e82_nodips_between_pass_sd_w"]
        lawg = r["law_gate"]
        lawq = r["law_q130n"]
        tau = lawg["sd_card1_w"] if c in GATED_RULES else lawq["sd_card1_w"]
        power[c] = {"k": k, "sigma_pass_w": sig, "tau_w": tau}
        for lab, delta in (("gate_law", lawg["committed_minus_mean_card1_w"]), ("q130n", lawq["committed_minus_mean_card1_w"])):
            if c not in GATED_RULES and lab == "gate_law":
                continue
            for n in (3, 2):
                power[c][f"{lab}_n{n}"] = sim_rule(k, tau, sig, delta, r["band_w"], n)

    def chi2q(df, p, n=200000):
        return float(np.quantile(rng.chisquare(df, n), p))

    def sim_pooled(group, X, taus):
        dfs = [len(rules[c]["fresh"]) + len(rules[c]["bridge"]) - 1 for c in group]
        sig2 = float(np.mean([rules[c]["e82_nodips_between_pass_sd_w"] ** 2 for c in group]))
        df = sum(dfs)
        qlo, qhi = chi2q(df, 0.025), chi2q(df, 0.975)
        out = {"df": df, "sigma_pass_w": round(math.sqrt(sig2), 3), "x_w": X,
               "chi2_factor_on_sd": [round(math.sqrt(df / qhi), 3), round(math.sqrt(df / qlo), 3)]}
        for tau in taus:
            for n in (3, 2):
                N2 = sig2 / n
                s2 = (tau ** 2 + N2) * rng.chisquare(df, 20000) / df
                up = np.sqrt(np.maximum(0, df * s2 / qlo - N2))
                lo = np.sqrt(np.maximum(0, df * s2 / qhi - N2))
                out[f"tau{tau}_n{n}"] = {"PASS": round(float(np.mean(up <= X)), 3), "FAIL": round(float(np.mean(lo > X)), 3),
                                         "INCONCLUSIVE": round(float(np.mean((up > X) & (lo <= X))), 3)}
        return out

    power["R4a"] = sim_pooled(DENSE_FLOAT, X_FLOAT, (0.05, 0.10, 0.20, 0.30, 0.50))
    power["R4b"] = sim_pooled(INT8_RULES, X_INT8, (0.05, 0.10, 0.20, 0.40))

    # ------------------------------------------------- the freeze
    reg = {
        "experiment": "E94", "title": "tile-to-tile spread: what a kind costs (aifoundry1 card 1, 600 MHz)",
        "request": "Q132, item 11 of the kinds page's section 11", "date": "2026-11-01",
        "registration": f"{K}/E94.md", "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600,
                                                "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "inputs_frozen": {
            "e78_reduction": {"path": E78_JSON, "sha256": sha(E78_JSON)},
            "e82_reduction": {"path": E82_JSON, "sha256": sha(E82_JSON)},
            "e82_nodips": {"path": E82_NODIPS, "sha256": sha(E82_NODIPS)},
            "e82_scored": {"path": E82_SCORED, "sha256": sha(E82_SCORED)},
            "e90_reduction": {"path": E90_JSON, "sha256": sha(E90_JSON)},
            "e90_scored": {"path": E90_SCORED, "sha256": sha(E90_SCORED)},
            "make_real": {"path": f"{K}/real/make_real.py", "sha256": sha(f"{K}/real/make_real.py")},
            "make_kinds": {"path": f"{K}/make_kinds.py", "sha256": sha(f"{K}/make_kinds.py")},
            "e90_json": {"path": f"{K}/e90/e90.json", "sha256": sha(f"{K}/e90/e90.json")},
            "e94_json": {"path": E94_JSON, "sha256": sha(E94_JSON)},
        },
        "harness": {"reused_unchanged_sha256": {r: sha(r) for r in REUSED},
                    "e94_files_sha256": {r: sha(r) for r in E94_BOX_FILES},
                    "e94_json_sha256": sha(E94_JSON)},
        "plan": {"passes": [9410, 9411, 9412], "smoke": 9401, "runs_per_pass": 76,
                 "items_per_pass": "the tie twice, E78's six anchors three times, E94's 51 draws and 5 E78 kinds once",
                 "reduction_primary": "dips removed, leak 0.2414 (E82's)", "min_kept_passes_scored": 2,
                 "min_tile_passes": 2},
        "card_budget": {"card_minutes_about": 40, "queue_budget_s": 2400, "first_pass_estimate_s": 730,
                        "queue_deadline": "2026-11-01 07:00 PST", "every_run_ends_by": "07:15 PST"},
        "card_scale": {"per_type": scale, "source": f"{E82_SCORED} cross_card.primary.x3.per_type_median"},
        "rules_of_number": rules, "tiles": tiles, "bridge": bridge, "retrospective_e90": retrospective, "desk_table": desk,
        "power": power,
        "predictor": {t: {k_: P[t][k_] for k_ in ("selected", "cols", "beta", "rms_loo_w", "pi95_halfwidth_w")} for t in P},
        "session_tie": {"reference": f"{E82_NODIPS} items.<cell>.D.mean (dips removed, as E94's primary)",
                        "cells": {c: {"ref_w": round(Dn[c], 4), "band_w": b, "e82_primary_w": round(D82[c], 4)}
                                  for c, b in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25),
                                               ("fp32.sparse50", 0.5), ("fp16.nn_like", 0.5), ("fp16.uniform01", 0.5),
                                               ("fp32.nn_like", 0.5), ("int8.sparse50", 0.25))}},
        "rules": {
            "E94-R1": {"what": "the committed tile lies inside the draws' spread: the 95% prediction interval of one more draw",
                       "per_rule": "PASS if |offset| + m <= PI, FAIL if |offset| - m > PI, else INCONCLUSIVE; offset = D(committed) "
                                   "- mean D(draws), PI = t(0.975, k-1) x s x sqrt(1 + 1/k), s = SD of the draws' pass means, m = "
                                   "t(0.975, df_res) x sqrt(MS_res / n), the committed tile's own repeatability"},
            "E94-R2": {"what": "does the committed tile's row need a correction",
                       "per_rule": "NO CORRECTION if |offset| + hw <= band; CORRECTION if |offset| - hw > 0 and |offset| >= band; else "
                                   "UNRESOLVED; hw = t(0.975, k-1) x sqrt(s^2 / k + MS_res / n), the draw as the unit",
                       "band_w": REP_BAND},
            "E94-R3": {"what": "the gate law's between-draw SD holds in the gated rules", "rules": list(GATED_RULES),
                       "per_rule": "PASS if law_gate.sd_card1_w lies inside the tile component's 95% interval, FAIL if outside "
                                   "(two-way)"},
            "E94-R4a": {"what": "a float kind with no zeros barely moves with the draw", "rules": list(DENSE_FLOAT), "x_w": X_FLOAT,
                        "rule": "pooled tile component: PASS if its 95% upper bound <= x, FAIL if its lower bound > x, else INCONCLUSIVE"},
            "E94-R4b": {"what": "int8 barely moves with the draw", "rules": list(INT8_RULES), "x_w": X_INT8, "rule": "as R4a"},
            "E94-R5": {"what": "Q130(n)'s frozen deltas track where a fresh draw lands against the committed tile",
                       "over": "the 42 fresh draws", "rule": "PASS if rms <= 0.50 W, rms < rms(no offset) and no draw with predicted "
                       "|delta| >= 0.30 W is resolved (95%, paired per pass) on the other side of zero; FAIL if rms > 1.00 W, rms >= "
                       "rms(no offset) or any such draw is; else INCONCLUSIVE"},
            "E94-R6": {"what": "the gate law's frozen deltas track where a fresh draw lands against the committed tile",
                       "over": "the 24 fresh draws of the gated rules", "rule": "PASS if rms <= 0.30 W and rms < rms(no offset); FAIL "
                       "if rms > 0.60 W or rms >= rms(no offset); else INCONCLUSIVE"},
            "E94-R7": {"what": "inside a kind, does the tile's own statistic say which draw costs more",
                       "over": "the 18 fresh draws of the float gated rules, each centred on its rule's mean, for each law",
                       "rules": list(FLOAT_GATED),
                       "rule": "PASS if centred residual rms <= 0.6 x centred SD, FAIL if >= centred SD, else INCONCLUSIVE"},
            "E94-R8": {"what": "a draw's offset from the committed tile is the same on both cards", "over": "E90's nine draws",
                       "rule": "rms of offset(card 1) x scale - offset(aifoundry3): PASS if <= 0.30 W, FAIL if > 0.60 W, else INCONCLUSIVE"},
            "E94-R9": {"what": "each law's frozen offset of the committed tile from its kind's mean, against the measured offset",
                       "rules": list(GATED_RULES), "rule": "for each law, rms over the four gated rules: PASS if <= 0.50 W, FAIL if > 1.00 W, "
                       "else INCONCLUSIVE. The desk table may speak for a row no card ran only if E94-R6 and this rule both PASS for the gate law"},
            "E94-S1": {"what": "the session tie (a check on the session, not on any law)",
                       "rule": "each cell's D within its band of E82's dips-removed value; a failure means the session moved"},
        },
        "not_scored_if": "fewer than 2 kept passes in the primary reduction: every rule NOT SCORED. A tile with fewer than 2 kept "
                         "runs' passes is left out of its rule and named; a rule left with fewer than 3 draws is UNRESOLVED.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e94.json"), "w"), indent=1)
    for c, r in rules.items():
        q_, g_ = r["law_q130n"], r["law_gate"]
        print(f"{c:16s} k {len(r['fresh'])}+{len(r['bridge'])} D82n {r['D_e82_nodips_card1_w']:7.3f} sigma {r['e82_nodips_between_pass_sd_w']:.3f} "
              f"SD gate {g_['sd_card1_w']:.3f} q130n {q_['sd_card1_w']:.3f} bus {r['law_bus']['sd_card1_w']:.3f}; offset gate {g_['committed_minus_mean_card1_w']:+.3f} "
              f"q130n {q_['committed_minus_mean_card1_w']:+.3f}; inside band {r['committed_inside_band']}")
    print("sha256 predictions-e94.json", sha(f"{K}/predictions-e94.json"))
    print(json.dumps({k_: v_ for k_, v_ in retrospective.items() if k_ != "draws"}))
    print(json.dumps(power["R4a"]))
    print(json.dumps(power["R4b"]))
    for c in rules:
        print(c, json.dumps({k_: v_ for k_, v_ in power[c].items() if k_.endswith("n3")}))


if __name__ == "__main__":
    main()
