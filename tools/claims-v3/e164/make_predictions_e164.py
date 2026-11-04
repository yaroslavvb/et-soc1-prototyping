#!/usr/bin/env python3
"""E164 (Q141(b)): write predictions-e164.json, the machine form of E164.md's registration (lab 4286f0a8), and planned-intervals.txt,
before any claim of aifoundry1 card 1 for E164 and before any E164 data exists. Standard library only.

E164 adds no prediction. Every model number is copied from Q140(x)'s committed card-1 predictions for pool 7
(tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry1c1.json, lab 75802201, made by Q140(m)'s predict_blind7.py with nothing
refitted). The power reference errors are M9's nested leave-one-kind-out errors of every card-1 row (ref-errors-m9.json, recomputed by
ref_errors_e164.py with Q140(m)'s fit_m9.run_family unchanged, equal to rows-m9.json's committed M9_nested_err_w). The heat reference is a
deterministic normal sample with M9's carried card-1 heat rms (m9.json > heat, M7's law). Rank 7's references are E157's registered
primary reduction (e157.json, Q139(u)'s footing) for K7's 8 tiles (pick7-e164.json) and the scale's six random anchors. Each source's
sha256 is checked against the value written here and recorded. The plan, the stops, the rules in words, the scheme the scorer reads
(score_e164.py) and the precision of each rule before the data are written here too; the hashes of every file the box runs are the kit's
(harness-e164.json, committed with the kit).

    python3 -B tools/claims-v3/e164/make_predictions_e164.py      # writes predictions-e164.json and planned-intervals.txt beside it
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P7 = "tools/claims-v3/kinds/blind7"
P6 = "tools/claims-v3/kinds/blind6"
QM = "docs/reports/data/2026-11-04-q140m-m9"
QU = "docs/reports/data/2026-11-03-q139u-footing"
E157D = "docs/reports/data/2026-11-03-e157-blind6-card1"
E153D = "docs/reports/data/2026-11-03-e153-blind6-aifoundry3"
SOURCES = {   # the frozen inputs and the sha256 each must have
    f"{P7}/predictions-blind7-aifoundry1c1.json": "22fe64be1b648f1aac222490c2548e5c4f920932c93ff470f5bb34ab9d9b27c0",
    f"{P7}/blind7.json": "24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552",
    f"{P7}/MANIFEST": "92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a",
    f"{P7}/SHA256SUMS": "df8610eeece7703e0aecb3bff58e226bff45320e0c54ae29c504a4ef8ed48239",
    f"{P7}/counts-blind7.json": "0749922588daf81f684d5e7804d337cf38d6b3c8519a99903b535118492caa57",
    f"{P7}/rank4_rule.json": "4b9ccaf006fff9bc92041bf470fe8520e7443f790c02dd1ba3e1ee62293f2507",
    f"{P7}/score_rank4.py": "2aba0a82898c96521f35fa402a376cb303588791775da2c7d4b8004bb8998897",
    f"{P6}/blind6.json": "4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03",
    f"{P6}/SHA256SUMS": "8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509",
    f"{QM}/m9.json": "322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835",
    f"{QM}/nested-m9.json": "f6057e3b9f055d538182485756fbe7cde27f96f8af7617085314d68ebada44a0",
    f"{QM}/rows-m9.json": "96ec405065257a543f7385711ad1841eb37316cc0148c362f35727534d05d41e",
    f"{QU}/footing.json": "f589efaad1fc9b19390658f16a5ffd4ca71e23cde59fbcf2f5cc88c267a73a97",
    f"{E157D}/e157.json": "0b6d0fcba7b822c691004294948949001f23e66a44c49edb0c2d39d18910c2a8",
    f"{E153D}/e153.json": "afff8cb2eca522ebdc9e22138850aef9d92bf482d8ebb4a0aae2faa4ef14be38",
    "tools/claims-v3/ccheck/pick6.py": "b4b92dc14001609f4d4a9528ec7f3eafc23f9a7ae59d6962c240b119d1a327e6",
    "tools/claims-v3/ccheck/ccheck.py": "2f806fe6080baeea33558ddd49fded16f2ebcb8c02f494217dfd32cc033c0a22",
    "tools/claims-v3/e164/E164.md": None,              # the registration (lab 4286f0a8): recorded, its bytes checked against git below
    "tools/claims-v3/e164/pick7-e164.json": None,
    "tools/claims-v3/e164/ref-errors-m9.json": None,
}
FORMATS = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")
M9_TERM = 0.9615998850616304            # m9.json card1_scale_by_format fp32 / fp16 (M8's kept term); int8 0.9615854710541776
K7_SCALE_ANCHORS = {"floats": ["fp32.randn", "fp16.randn", "fp32.anchor6_randn", "fp16.anchor6_randn"],
                    "int8": ["int8.full", "int8.anchor6_full"]}
POOL6_EXTRA = ("fp32.anchor6_randn", "fp16.anchor6_randn", "int8.anchor6_full")
E78_FRAME = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full", "anchor_pi")
SMOKE = ("anchor_pi", "fp32.zeros", "fp32.randn", "fp32.uniform_pm1", "fp32.anchor7_zeros", "fp32.real_qwen_softmax_v",
         "fp16.randn_x8", "fp16.zeros", "int8.anchor7_full_a", "int8.b_line_zero_55", "int8.zeros")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def pick6():
    spec = importlib.util.spec_from_file_location("pick6", os.path.join(ROOT, "tools/claims-v3/ccheck/pick6.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def binom_low(n, p=0.95, alpha=0.025):
    c = 0.0
    for k in range(n + 1):
        c += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if c >= alpha:
            return k
    return n


def interval(ref, mix, draws, seed, stat):
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        xs = []
        for t, k in sorted(mix.items()):
            e = ref[t]
            xs += [e[rng.randrange(len(e))] for _ in range(k)]
        vals.append(math.sqrt(sum(x * x for x in xs) / len(xs)) if stat == "rms" else sum(xs) / len(xs))
    vals.sort()
    return [round(vals[int(0.025 * draws)], 4), round(vals[int(0.5 * draws)], 4), round(vals[int(0.975 * draws) - 1], 4)]


def per_pass(e, name):
    return [float(e["per_pass"][str(p)][name]["D"]) for p in e["passes"] if name in e["per_pass"].get(str(p), {})]


def k7_planned(k7, anchors, draws=4000, seed=16407, n_new=4):
    """K7D's and K7W's chance of passing when nothing changed between the sessions (planning only): each tile's and each anchor's
    per-pass value in both sessions drawn independently around one true mean with E157's own per-pass sd; E157 with its 3 kept
    passes, E164 with n_new; the registered statistic and verdicts applied."""
    pk = pick6()
    rng = random.Random(seed)
    fam = {t: ("int8" if t.startswith("int8.") else "floats") for t in k7}
    passd, passw, within = 0, 0, {t: 0 for t in k7}
    for _ in range(draws):
        def sess(sd_src, n):
            out = {}
            for t, v in list(sd_src.items()):
                xs = [v["mean"] + rng.gauss(0.0, v["sd"]) for _ in range(n)]
                m = sum(xs) / n
                s = statistics.stdev(xs)
                out[t] = (m, s / math.sqrt(n))
            return out
        both = dict(k7)
        both.update(anchors)
        old, new = sess(both, 3), sess(both, n_new)
        scale, sse = {}, {}
        for f, an in K7_SCALE_ANCHORS.items():
            rat = sorted((old[a][0] / new[a][0], a) for a in an)
            mid = rat[1:3] if len(rat) == 4 else rat
            scale[f] = sum(r for r, _ in mid) / len(mid)
            sse[f] = math.sqrt(sum((r * math.hypot(old[a][1] / old[a][0], new[a][1] / new[a][0])) ** 2 for r, a in mid)) / len(mid)
        nin_d, nin_w = 0, 0
        for t in k7:
            s = scale[fam[t]]
            d = s * new[t][0] - old[t][0]
            if abs(d) <= 0.05:
                nin_d += 1
                within[t] += 1
            vo, vn = old[t][1] ** 2, (s * new[t][1]) ** 2
            nu = (vo + vn) ** 2 / (vo ** 2 / (3 - 1) + vn ** 2 / (n_new - 1))
            hw = pk.t975(nu) * math.sqrt(vo + vn + (new[t][0] * sse[fam[t]]) ** 2)
            if abs(d) <= hw:
                nin_w += 1
        passd += nin_d >= 7
        passw += nin_w == len(k7)
    return {"draws": draws, "seed": seed, "n_passes": {"E157": 3, "E164": n_new},
            "P_K7D_pass": passd / draws, "P_K7W_pass": passw / draws, "P_within_0p05_by_tile": {t: v / draws for t, v in within.items()},
            "how": "planning only, nothing measured: no change between sessions, independent per-pass noise at E157's own per-pass sd for "
                   "every tile and anchor in both sessions, the registered scale (rank 4's median form over E78's and pool 6's random "
                   "anchors) and the registered verdicts"}


def main():
    for rel, want in SOURCES.items():
        have = sha(rel)
        if want is not None and have != want:
            raise SystemExit(f"{rel}: sha256 {have} != the committed {want}")
        SOURCES[rel] = have
    pred = json.load(open(os.path.join(ROOT, P7, "predictions-blind7-aifoundry1c1.json")))
    man = json.load(open(os.path.join(ROOT, P7, "blind7.json")))
    spec = {t["name"]: t for t in man["tiles"]}
    sub = man["subsets"]
    m9 = json.load(open(os.path.join(ROOT, QM, "m9.json")))
    nested = json.load(open(os.path.join(ROOT, QM, "nested-m9.json")))
    footing = json.load(open(os.path.join(ROOT, QU, "footing.json")))
    rer = json.load(open(os.path.join(HERE, "ref-errors-m9.json")))
    pick = json.load(open(os.path.join(HERE, "pick7-e164.json")))
    e157 = json.load(open(os.path.join(ROOT, E157D, "e157.json")))
    e153 = json.load(open(os.path.join(ROOT, E153D, "e153.json")))
    spec6 = {t["name"]: t for t in json.load(open(os.path.join(ROOT, P6, "blind6.json")))["tiles"]}
    tiles = {}
    for name, t in sorted(pred["tiles"].items()):
        s = spec[name]
        row = {"type": t["type"], "priority": int(t["priority"]), "pool_anchor": bool(s.get("anchor")), "case": t["case"],
               "class": "0" if s.get("anchor") else s["case"][:1], "real": bool(s.get("real")),
               "hold_candidate": bool(s.get("hold_candidate")), "sha256": t["sha256"], "file": f"{P7}/{s['file']}",
               "sha256_matches_manifest": t["sha256_matches_manifest"]}
        for m in ("M9", "M8", "M7", "M6"):
            x = t[m]
            row[m] = {"D_w": x["D_w"], "D_95": x["D_95"], "S_w": x["S_w"], "dT_win_c": x["dT_win_c"], "dT_win_95": x["dT_win_95"],
                      "D600_a3_footing_w": x["D600_a3_footing_w"]}
        tiles[name] = row
    assert len(tiles) == 61 and all(tiles[n]["sha256_matches_manifest"] for n in tiles)
    assert all(tiles[n]["sha256"] == spec[n]["sha256"]["whole"] for n in tiles)
    p1 = {f: sorted(n for n, r in tiles.items() if r["type"] == f and r["priority"] == 1) for f in FORMATS}
    p1_all = sorted(n for f in FORMATS for n in p1[f])
    assert [len(p1[f]) for f in FORMATS] == [17, 9, 22] and len(p1_all) == 48
    nonanchor = sorted(n for n, r in tiles.items() if not r["pool_anchor"])
    real12 = sorted(n for n in nonanchor if tiles[n]["real"])
    real10 = sorted(sub["real"])
    assert len(real12) == 12 and set(real10) <= set(real12) and all(tiles[n]["priority"] == 1 for n in real10) and len(real10) == 10
    classes = {c: sorted(n for n in p1_all if tiles[n]["class"] == c) for c in "SELHUR"}
    assert {c: len(v) for c, v in classes.items()} == {"S": 7, "E": 6, "L": 7, "H": 6, "U": 12, "R": 10}
    u12, u17 = sorted(sub["unaimed_synthetic"]), sorted(sub["unaimed_with_float_real"])
    assert sorted(classes["U"]) == u12 and len(u17) == 17
    # K7: the pick, its E157 per-pass readings, and the scale's anchors' (E78's and pool 6's random anchors) readings in E157
    k7 = {}
    for r in pick["pick"]:
        n = r["tile"]
        pp = per_pass(e157, n)
        k7[n] = {"type": r["type"], "case": r["case"], "priority": r["priority"], "sha256": r["sha256"], "file": r["file"],
                 "E157": {"mean": e157["items"][n]["D"]["mean"], "se": e157["items"][n]["D"]["se"], "n": e157["items"][n]["D"]["n"],
                          "per_pass": pp, "sd": statistics.stdev(pp)},
                 "E153_D": e153["items"][n]["D"]["mean"], "repeat_band_W_E157": r["repeat_band_W_E157"]}
        assert abs(statistics.mean(pp) - k7[n]["E157"]["mean"]) < 1e-9 and spec6[n]["sha256"]["whole"] == r["sha256"]
    k7_anchors = {}
    for a in K7_SCALE_ANCHORS["floats"] + K7_SCALE_ANCHORS["int8"]:
        pp = per_pass(e157, a)
        k7_anchors[a] = {"mean": e157["items"][a]["D"]["mean"], "se": e157["items"][a]["D"]["se"], "n": e157["items"][a]["D"]["n"],
                         "per_pass": pp, "sd": statistics.stdev(pp)}
        assert abs(statistics.mean(pp) - k7_anchors[a]["mean"]) < 1e-9
    pool6_extra = {n: {"type": spec6[n]["type"], "sha256": spec6[n]["sha256"]["whole"], "file": f"{P6}/{spec6[n]['file']}"}
                   for n in POOL6_EXTRA}
    # references
    pools = {**nested["families"]["float"]["band"]["pools"], **nested["families"]["int8"]["band"]["pools"]}
    p_rms = {f: pools[f"{f}|c1"]["rms_w"] for f in FORMATS}
    p_n = {f: pools[f"{f}|c1"]["n"] for f in FORMATS}
    p_ref = {f: rer["card1_by_format"][f] for f in FORMATS}
    assert all(len(p_ref[f]) == p_n[f] for f in FORMATS)
    assert all(abs(math.sqrt(sum(x * x for x in p_ref[f]) / len(p_ref[f])) - p_rms[f]) < 1e-9 for f in FORMATS)
    hp = m9["heat"]["interval_pool_by_format_card_c"]
    h_rms = {f: hp[f"{f}|aifoundry1-c1"]["rms_c"] for f in FORMATS}
    rng = random.Random("E164|heat-reference")
    h_ref = {f: [rng.gauss(0.0, h_rms[f]) for _ in range(2000)] for f in FORMATS}
    min_tiles = {"fp32": 6, "fp16": 4, "int8": 6, "floats": 8, "real": 8, "unaimed": 10}
    bs = {"draws": 20000, "seed": 16400}
    precision = {}
    for rid, f in (("E164-P1", "fp32"), ("E164-P2", "fp16"), ("E164-P3", "int8")):
        precision[rid] = {"tiles": len(p1[f]), "rms_interval_W": interval(p_ref, {f: len(p1[f])}, 4000, 1, "rms")}
    precision["E164-B1"] = {"tiles": len(p1["fp32"]) + len(p1["fp16"]),
                            "mean_interval_W": interval(p_ref, {"fp32": len(p1["fp32"]), "fp16": len(p1["fp16"])}, 4000, 2, "mean")}
    precision["E164-B2"] = {"tiles": len(p1["int8"]), "mean_interval_W": interval(p_ref, {"int8": len(p1["int8"])}, 4000, 3, "mean")}
    for rid, f in (("E164-H1", "fp32"), ("E164-H2", "fp16"), ("E164-H3", "int8")):
        precision[rid] = {"tiles": len(p1[f]), "rms_interval_C": interval(h_ref, {f: len(p1[f])}, 4000, 4, "rms")}
    precision["E164-C1"] = {"tiles": 48, "binomial_low_2p5": binom_low(48)}
    precision["E164-H4"] = {"tiles": 48, "binomial_low_2p5": binom_low(48)}
    precision["E164-K7"] = k7_planned({t: {"mean": v["E157"]["mean"], "sd": v["E157"]["sd"]} for t, v in k7.items()},
                                      {a: {"mean": v["mean"], "sd": v["sd"]} for a, v in k7_anchors.items()})
    rules = {
        "E164-PC": "the C check: every measured launch of a pool-7 tile in a kept pass has a C record (same t_start_ms and t_end_ms) that "
                   "tools/claims-v3/ccheck/ccheck.py check judges PASS (bit-exact; ROUNDING, UNMODELLED, FAIL and an unrecorded launch "
                   "count as not checked); PASS if every pool-7 tile's launches do, else FAIL naming them; a tile with any launch not PASS "
                   "leaves the scored set of every rule below (named); every rule is also given over all tiles, beside",
        "E164-P1": "power fp32: rms(D - M9) over the 17 priority-1 fp32 tiles (at least 6) against the 2.5-97.5% range of the rms of as "
                   "many draws with replacement from M9's nested errors of every card-1 fp32 row (ref-errors-m9.json): PASS at or below "
                   "the 97.5% point, FAIL above; below the 2.5% point reported as better than the nested score says",
        "E164-P2": "power fp16: as P1, the 9 priority-1 fp16 tiles (at least 4), card-1 fp16 rows",
        "E164-P3": "power int8: as P1, the 22 priority-1 int8 tiles (at least 6), card-1 int8 rows",
        "E164-B1": "bias, floats: mean(D - M9) over the 26 priority-1 float tiles (at least 8) against the 2.5-97.5% range of the mean of "
                   "as many draws (the same format mix) from the same errors: PASS inside, FAIL HIGH below it (M9 predicts too much), "
                   "FAIL LOW above it",
        "E164-B2": "bias, int8: as B1, the 22 priority-1 int8 tiles (at least 6)",
        "E164-C1": f"coverage, power: tiles inside M9's frozen 95% band among the 48 priority-1 tiles; PASS if at least the 2.5% point "
                   f"of Binomial(n, 0.95) ({binom_low(48)} of 48), FAIL if fewer; NOT SCORED under 10",
        "E164-M1": "M9 against M6 (rank 1's primary): d = rms(M9 errors) - rms(M6 errors) over the priority-1 tiles, 95% interval by a "
                   "paired bootstrap over tiles (5,000 draws): BETTER ('resolved below zero') if the upper bound < 0, WORSE if the lower "
                   "bound > 0, else NOT RESOLVED; card 1's half of 'on both 600 MHz cards' (E163 has aifoundry3's)",
        "E164-M2": "M9 against M8: as M1",
        "E164-U1": "M9 against M6 on the 12 unaimed tiles (blind7.json subsets.unaimed_synthetic, at least 10): the same paired bootstrap; "
                   "PASS ('no worse') unless the 95% interval lies above zero (lower bound > 0: FAIL); d and its interval reported, and "
                   "the same reading on the 17 (unaimed_with_float_real) beside, never a verdict",
        "E164-H1": "heat fp32: rms(dT_win - M9's dT) over the priority-1 fp32 tiles (at least 6) against the 2.5-97.5% range of the rms of "
                   "as many draws from a deterministic normal sample of 2,000 points with M9's carried card-1 heat rms for fp32: PASS at "
                   "or below the 97.5% point, FAIL above",
        "E164-H2": "heat fp16: as H1 (at least 4)",
        "E164-H3": "heat int8: as H1 (at least 6)",
        "E164-H4": f"coverage, heat: as C1, M9's frozen dT band ({binom_low(48)} of 48)",
        "E164-R1": "the real-tile sub-rule (rank 9): rms(D - M9) over the 10 priority-1 real tiles (at least 8) at or below the 97.5% point "
                   "of the rms of as many draws (same format mix) from the errors of the pool's own non-real non-anchor tiles (all "
                   "priorities): PASS, else FAIL; all 12 real tiles reported beside",
        "E164-R2": "the real-tile sub-rule: every measured one of the 10 priority-1 real tiles inside M9's frozen 95% band: PASS, else FAIL "
                   "naming them; all 12 reported beside",
        "E164-X1": "the card term on pool 7, floats (scored only if E163's committed primary reduction of pool 7 on aifoundry3 exists when "
                   "this lane reduces, else NOT SCORED and handed on with the code): the median over non-anchor float tiles with D >= 5 W "
                   "on both cards, in both cards' scored sets, of D(card 1) / D(aifoundry3), each card's registered primary, 95% interval "
                   "by a bootstrap over tiles (5,000 draws): PASS if it holds M9's 0.9616, FAIL if not; M7's and M6's 0.9711 reported",
        "E164-X2": "the card term, int8: as X1 with D >= 1 W on both cards (M7's and M6's 0.9735 reported)",
        "RK4": "Q140(x)'s paired-anchor rule (tools/claims-v3/kinds/blind7/rank4_rule.json), scored unchanged by score_rank4.py through "
               "pair_rank4_e164.py on E163's and E164's registered scored.json; E164 registers only its inputs",
        "E164-K7C": "C, rank 7's tiles: every launch of K7's 8 tiles in the session (the smoke's included) has its C record and is PASS; FAIL "
                    "if any is ROUNDING, UNMODELLED, FAIL or unrecorded; the literal 'exact or within rounding' reported beside",
        "E164-K7D": "rank 7's rule as the critic wrote it: per family s_f = the median over the family's scale anchors of D_E157(a) / "
                    "D_E164(a) (floats fp32.randn, fp16.randn, fp32.anchor6_randn, fp16.anchor6_randn, the mean of the middle two of four; "
                    "int8 int8.full and int8.anchor6_full, the mean of the two); per tile delta = s_f x D_E164 - D_E157, each D the "
                    "session's registered primary mean over its kept passes (Q139(u)'s footing on both); PASS if |delta| <= 0.05 W on at "
                    "least 7 of 8, else FAIL naming them; NOT SCORED if fewer than 7 tiles are measured with at least 2 kept passes or a "
                    "family's scale lacks an anchor",
        "E164-K7W": "beside K7D: |delta| <= t_0.975(nu) sqrt((s_f se_E164)^2 + se_E157^2 + (D_E164 se_s)^2), nu by Welch-Satterthwaite on "
                    "the two tile terms (pick6.py), se_s = sqrt(sum se_i^2) / k over the k anchors whose ratios form the median, se_i = "
                    "r_i sqrt(se_rel_E157^2 + se_rel_E164^2): PASS if all 8 inside, else FAIL; NOT SCORED as K7D",
        "E164-K7": "K7 = K7C AND K7D; K7' = K7C AND K7W: one new session of the two rank 7's rule asks",
        "E164-PCa": "C, the frame and the scale's anchors: every launch of E78's six anchors, the tie and pool 6's three random anchors in "
                    "the session PASS and recorded, else FAIL naming them",
        "min_passes": "fewer than 2 kept passes on the primary: every rule but the C rules NOT SCORED; a tile with fewer than 2 kept passes "
                      "is left out and named",
    }
    reg = {
        "experiment": "E164",
        "date": "2026-11-04",
        "registration": "tools/claims-v3/e164/E164.md (lab 4286f0a8, Wed 4 Nov 2026 09:18:57 PST); this file is its machine form",
        "request": "Q141(b), the card half's desk preparation (the owner's mandate of Mon 2 Nov 2026, ~18:40 PST; goal: predict power and "
                   "heat as accurately as possible); kinds page section 11 item 6 (#11-what-is-still-open); Q139 critic ranks 1, 4, 7, "
                   "14 (card 1's half); Q140 critic card_half[1], desk_next 1 and 7",
        "card": "aifoundry1 card 1 (aifoundry1-c1, V3_DEVICE=1 / ET_DEVICES=1, lock etsoc-shire1), 600 MHz, TDP 65 W and threshold 65 C "
                "as read, never set",
        "frozen_inputs": {"sha256": SOURCES,
                          "commits": {"pool7_and_predictions": "75802201 (Q140(x), 03:27:39 PST); dated notes 3c9bb2ba (04:18:24 PST)",
                                      "m9": "1f244140 (Q140(m), 01:12:04 PST; registration 8dfafae3, 00:45:51 PST)",
                                      "m9_aifoundry2_part_not_used": "5b98bd5c / 245caffe / 5c98c0c5",
                                      "heat_replicates_not_used": "11174d20 / c9aaf179 / a4fe976d / ac06c9be",
                                      "g4_stride_not_used": "49575094 / e39d06da / 1bfaa4e4",
                                      "e157_parent": "registration 01676499; data fb2e5c6e, 80420324; corrections 7931262e, 26096a60",
                                      "e153": "8e18eb67", "ccheck": "60b91395, corrected 4946a992 (Q139(k))",
                                      "registration": "4286f0a8 (E164.md, pick7_e164.py)"},
                          "band_rule_M9": pred["band_rule_M9"], "band_rule_M8": pred["band_rule_M8"]},
        "scheme": {"prefix": "E164", "primary": "M9", "models": ["M9", "M8", "M7", "M6"],
                   "compare": [["M1", "M6"], ["M2", "M8"]], "reported_compare": ["M7"],
                   "unaimed": {"rule": "U1", "set": "unaimed12", "beside": "unaimed17"},
                   "repeat": {"kind": "k7", "label": "K7", "frame": "q139u_footing", "min_inside": 7, "min_scored": 7, "line_w": 0.05,
                              "scale_anchors": K7_SCALE_ANCHORS},
                   "frame_c": list(E78_FRAME) + list(POOL6_EXTRA), "card_term_rules": ["X1", "X2"], "cheap_read_scale": False,
                   "other_card": "E163"},
        "plan": {
            "passes": [16410, 16411, 16412, 16413, 16414], "planned_passes": 4, "smoke": 16401, "stoptest": 16402,
            "smoke_items": list(SMOKE), "runs_per_pass": 96, "runs_per_pass_priority2_dropped": 92, "burn_in_runs": 2,
            "min_kept_passes_scored": 2, "min_tile_passes": 2, "min_tiles": min_tiles,
            "order": "Random('E164|aifoundry1-c1|<pass>'): the 70 tiles other than pool 7's two int8 random anchors (59 of pool 7, K7's 8, "
                     "pool 6's three random anchors; 66 with the priority-2 tests dropped) shuffled and dealt in that order into three "
                     "segments of floor(n/3), floor(n/3) and the rest; each segment gets E78's six anchors and pool 7's two int8 random "
                     "anchors once and is reshuffled with the same generator; the tie first and last",
            "every_segment": ["int8.anchor7_full_a", "int8.anchor7_full_b"],
            "priority2_drop_first": sorted(sub["priority2_tests"]),
            "protocol": "E78's: heat to 59 C, launch at 58 C after 2.0 s quiet, 4 s runs, 1,024 minions, 600 MHz",
            "c_check": "every measured launch through tools/claims-v3/ccheck/sparsity_ccheck.sh: the patched host "
                       "build/ccheck/b/host/sparsity_host --c-log <pass>/c-log.jsonl --c-poison, kernel build/sparsity/kernel/sparsity.elf; "
                       "the heater unchanged; checked at the desk with ccheck.py check, never on the box",
            "budget_s_from_session_start": 3900, "reserve_s": 60, "card_minutes_max": 65, "first_pass_estimate_s": 900, "gap_s": 10,
            "expected_card_minutes": "about 56-58 (four passes of 827-848 s: E157's 658-675 s for 78 launches scaled to 98; the stop-path "
                                     "test and the smoke about 1.5 min)",
            "deadline": "E164_DEADLINE, set at the launch from the round's time gate less 10 minutes (the queue refuses without it)",
            "stops": {"board_w": 66.0, "die_hottest_shire_c": 72.0, "run_e78_max_c": 72.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0,
                      "how": "the newest line of the running sampler's file, read by the main path before every launch and every 0.1 s "
                             "while it waits and by the in-run watcher every 0.1 s for the whole pass (E142's, kept by E157)"},
            "reduction": {"primary": f"reduce_e164.py --leak {footing['slopes']['c1']['k_w_per_c']!r} --no-refit (Q139(u)'s footing: card "
                                     "1's frozen slope, E82 A2's dips removed once; E78's gates; card 1's config gate)",
                          "k_w_per_c": footing["slopes"]["c1"]["k_w_per_c"],
                          "arms": ["leak auto (the session's own fitted slope)", "dips kept at the primary slope",
                                   "leak 0.2955 and 0.3320 (Q139(u)'s slope interval)", "anchor gates relaxed"]},
            "bootstrap": bs, "paired_draws": 5000,
        },
        "model": {"name": "M9 (Q140(m), 1f244140), scored; M8, M7 and M6 frozen beside it",
                  "units": "D: W over the type's own zeros at 600 MHz on card 1 on Q139(u)'s footing (the card term in each model's "
                           "prediction); dT: C, the die reading over the window less the launch reading, over the kinds run (4.5 s)",
                  "card_term_applied": {"M9": M9_TERM, "M9_int8": m9["families"]["int8"]["card1_scale_by_format"]["int8"],
                                        "M8": 0.9615998850616304, "M7_floats": 0.9711174157693975, "M7_int8": 0.9734515623123359},
                  "heat_coef_card1": {"S": m9["heat"]["coef"]["S|aifoundry1-c1"], "ST": m9["heat"]["coef"]["ST|aifoundry1-c1"]},
                  "heat_pool_card1_rms_c": h_rms, "power_pool_card1_rms_w": p_rms, "power_pool_card1_n": p_n,
                  "zeros_S_w_card1": pred["zeros_S_w"]},
        "tiles": tiles,
        "k7": {"tiles": k7, "scale_anchors_E157": k7_anchors, "pick": "pick7-e164.json (pick7_e164.py, lab 4286f0a8)",
               "reference_session": "E157 (e157.json, its registered primary: Q139(u)'s footing, kept passes 15710, 15712, 15713)"},
        "pool6_extra": pool6_extra,
        "reference_errors": {"power_card1": p_ref, "heat_normal_card1": h_ref, "n": {f: len(p_ref[f]) for f in FORMATS},
                             "note": "power: M9's nested leave-one-kind-out errors of every card-1 row (ref-errors-m9.json, fit_m9.run_family "
                                     "unchanged; equal to rows-m9.json's M9_nested_err_w and to nested-m9.json's pools); heat: a "
                                     "deterministic normal sample (2,000 points, Random('E164|heat-reference')) with M9's carried card-1 "
                                     "heat rms per format"},
        "sets": {"priority1_by_format": p1, "priority1_all": p1_all, "nonanchor": nonanchor, "real": real10, "real_beside": real12,
                 "nonreal_nonanchor": sorted(set(nonanchor) - set(real12)), "classes": classes, "unaimed12": u12, "unaimed17": u17,
                 "priority2_tests": sorted(sub["priority2_tests"]), "anchors_random_float": sub["anchors"]["random_float"],
                 "anchors_random_int8": sub["anchors"]["random_int8"], "anchors_zeros": sub["anchors"]["zeros"],
                 "k7": sorted(k7), "k7_scale_anchors": K7_SCALE_ANCHORS, "pool6_extra": list(POOL6_EXTRA)},
        "precision_before_data": precision,
        "rules": rules,
        "reported_not_verdicts": [
            "M8's, M7's and M6's rms, bias and coverage beside M9's on every set and per format; every model on all 52 non-anchor tiles",
            "the per-class readings S, E, L, H, U, R: rms and bias of each model, M9 - M6 and M9 - M8 by the same paired bootstrap per class",
            "U17 beside U1; R12 beside R1 and R2; the priority-2 tests; the pool's nine anchors",
            "fp32.b_onebit_b20_pi's error beside M9's committed 27-point recount of its byte twin (-0.311 +- 0.198 W: dated note A1-2)",
            "Q141(t)'s arm (M9's frozen prices on pool 7's S tiles recounted at 27 launch points), if committed before E164's claim",
            "heat at the measured run length (H2's ST term), the die rise per board W against 0.1151 C/W, the duty against 0.9963",
            "the C check's per-tile counts and the launch gaps; E78's anchors and the tie against E157's on this card",
            "K7's unscaled delta and each family's scale with its standard error; every rule at the reduction's arms and over all tiles "
            "with the C check's exclusions put back"],
        "expected": "P2, P3 PASS; P1 PASS or FAIL; B1 PASS or FAIL HIGH; B2 PASS; C1 PASS; M1 NOT RESOLVED; M2 BETTER or NOT RESOLVED; U1 "
                    "PASS; H1-H4 PASS; R1 PASS, R2 PASS or FAIL on one tile; X1, X2 PASS; RK4 floats PASS, int8 PASS more likely than "
                    "not; K7D FAIL, K7W PASS; PC, K7C, PCa PASS (E164.md, What I expect)",
        "binomial_low_2p5": {"10": binom_low(10), "12": binom_low(12), "48": binom_low(48), "52": binom_low(52), "61": binom_low(61)},
    }
    out = os.path.join(HERE, "predictions-e164.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    L = ["E164 planned intervals (make_predictions_e164.py, before any data): the 2.5% / 50% / 97.5% points of each rule's statistic "
         "under the registered reference (power: M9's nested card-1 per-row errors; heat: the normal sample with M9's carried card-1 "
         "heat rms), 4,000 draws"]
    for rid in ("E164-P1", "E164-P2", "E164-P3"):
        L.append(f"{rid}: rms over {precision[rid]['tiles']} tiles, W: {precision[rid]['rms_interval_W']}")
    for rid in ("E164-B1", "E164-B2"):
        L.append(f"{rid}: mean over {precision[rid]['tiles']} tiles, W: {precision[rid]['mean_interval_W']}")
    for rid in ("E164-H1", "E164-H2", "E164-H3"):
        L.append(f"{rid}: rms over {precision[rid]['tiles']} tiles, C: {precision[rid]['rms_interval_C']}")
    L.append(f"E164-C1: at least {binom_low(48)} of 48 inside")
    L.append(f"E164-H4: at least {binom_low(48)} of 48 inside")
    k = precision["E164-K7"]
    L.append(f"E164-K7 (planning, no change between sessions, E157's per-pass spreads, {k['draws']} draws): P(K7D PASS) "
             f"{k['P_K7D_pass']:.3f}, P(K7W PASS) {k['P_K7W_pass']:.3f}; P(|delta| <= 0.05 W) by tile " +
             json.dumps({t: round(v, 3) for t, v in k["P_within_0p05_by_tile"].items()}))
    L.append("E164-K7 references (E157, Q139(u)'s footing, kept passes): " +
             json.dumps({t: [round(v["E157"]["mean"], 4), round(v["E157"]["se"], 4)] for t, v in k7.items()}))
    L.append("E164-K7 scale anchors in E157 (mean, se): " +
             json.dumps({a: [round(v["mean"], 4), round(v["se"], 4)] for a, v in k7_anchors.items()}))
    open(os.path.join(HERE, "planned-intervals.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"wrote {out}: {len(tiles)} pool-7 tiles, {len(k7)} K7 tiles; power reference rms {p_rms}; heat {h_rms}")


if __name__ == "__main__":
    main()
