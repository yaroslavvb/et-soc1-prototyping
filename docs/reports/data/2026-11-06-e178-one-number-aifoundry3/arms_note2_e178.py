#!/usr/bin/env python3
"""E178's data README, dated note 2 (Fri 6 Nov 2026, the card day Q149, after the data commit f7820e70 and its fix f68f0380): E178's
three REPORTED arms, each read on this directory's committed data by its own registered reading. None is a verdict of E178: no E178
rule, threshold or verdict reads any of them.

  (1) Q148(c)'s constant-lane term (tools/claims-v3/m10-c/: REGISTRATION.md sections 5-6, its dated note 2). Its two registered
      scorers ran as their files say (termc.py score; termc_note2.py score) and wrote arm-m10c-termc-e178.json and
      arm-m10c-note2-e178.json beside this file. This script re-runs both in memory (termc.score_session; termc_note2.score_split
      with the frozen bridge kinds, checked again by bytes), requires each to equal its file byte for byte, evaluates the
      registration's "what would show the term is not wanted", and reads beside (not a registered reading) each kind against the
      forecast's frozen 95% predictive interval.
  (2) october-forecast-model, by E178's dated note M1 section M1-4: the scored figure per kind (m1-october-forecast-model.json ›
      scored › kinds); the ranking by format (power_e178.spearman, imported unchanged) of the scored figure against E178's measured D;
      each contrast a - b as the scored figure of a less that of b, set against the board and rail intervals A4's reader gives
      (rail-arm-e178.json): inside, above or below; the model's three extremes (two are not among the reader's 52 contrasts: they are
      read here by the reader's own pass-form statistic, rail_e178.views with score_e178.pair_xs and interval, after that route
      reproduces every pass-form contrast of the reader); its ties and E178-E's equal groups, reported only; and the levels, each kind's
      figure against its measured D and Drail, unscaled, each reading naming its column.
  (3) the minion-rail arm as the card lane committed it (rail-arm-e178.json, A4's reader v2): quoted and recounted.

    python3 -B arms_note2_e178.py [--dir <this directory>] [--out <dir>]    # writes arms-note2-e178.json and arms-note2-e178.txt

The Intel's /usr/bin/python3 (3.9, numpy 1.26; numpy through termc.py). One core, a few seconds. It reads only committed files, each
checked first against a committed hash list whose own sha256 is pinned below, and writes only its two outputs. Readings use words of
their own (inside / above / below; reads above 0 / below 0 / spans 0), never E178's verdict words; Q148(c)'s rule words (BETTER, NOT
RESOLVED, enters) are its own registration's, for M10's next blind pool.
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "docs/reports/data/2026-11-06-e178-one-number-aifoundry3"
E178T = "tools/claims-v3/e178"
M10C = "tools/claims-v3/m10-c"
TYPES = ("fp32", "fp16", "int8")
FLOATS = ("fp32", "fp16")
TOL = 1e-12
NEVER = "REPORTED, never a verdict of E178: no E178 rule, threshold or verdict reads it"
# each hash list this script trusts, pinned by its own sha256 (the lists as committed at f7820e70, 97a5e16b, 6b5ad913 and d62d0c8f)
LISTS = {RUN + "/SHA256SUMS": "75801d1b99b02827ae7291cfa690ff21e49097524b6aadacbadb3d68669b6dae",
         E178T + "/SHA256SUMS-e178-m1": "80cef420fcc0f97bd0b2c26011f2fb032cd06671bd633a09ca372ef1b8969fef",
         M10C + "/SHA256SUMS": "35363d9ed167f823aa5b669d352500109556f34d117f835eeca5d4fd3e0a25ff",
         M10C + "/SHA256SUMS-note2": "27ea19adf7cc8a5d0fa014b807515b0cb8ebf8acf85dc524235c7d1bb1c980c6"}
# what each list pins that this script reads (RUN/SHA256SUMS names its files relative to RUN)
NEEDS = {RUN + "/SHA256SUMS": ["scored.json", "e178.json", "runs.csv", "rail-arm-e178.json"],
         E178T + "/SHA256SUMS-e178-m1": [E178T + "/m1-october-forecast-model.json", E178T + "/score_e178.py", E178T + "/power_e178.py",
                                         E178T + "/rail_e178.py", E178T + "/forecast-e178.json", E178T + "/kinds-e178.json"],
         M10C + "/SHA256SUMS": [M10C + "/termc.py", M10C + "/termc-fit.json", M10C + "/forecast-m10c-e178.json", "tools/claims-v3/m10-s/term_s.py",
                                "docs/reports/data/2026-11-04-q142m-m10/predict_m10.py", "docs/reports/data/2026-11-04-q142m-m10/fit_m10.py"],
         M10C + "/SHA256SUMS-note2": [M10C + "/termc_note2.py", M10C + "/termc-note2.json"]}
OUT_TERMC, OUT_NOTE2 = "arm-m10c-termc-e178.json", "arm-m10c-note2-e178.json"
M1_FIG_FLOAT = "power above zeros at 600 MHz, a3 / c1 (W)"


def stop(msg):
    raise SystemExit("ARMS NOTE 2 STOPPED: " + msg)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(p):
    return json.load(open(p))


def where(lo, hi, f):
    return "inside" if lo <= f <= hi else ("above" if f > hi else "below")


def reads(lo, hi):
    return "reads above 0" if lo > 0 else ("reads below 0" if hi < 0 else "spans 0")


def r4(x):
    return None if x is None else round(x, 4)


def pins(top):
    out = []
    for lst, want_list in LISTS.items():
        p = os.path.join(top, lst)
        if not os.path.exists(p) or sha(p) != want_list:
            stop(f"{lst} is not the committed list (sha256 {sha(p)[:12] if os.path.exists(p) else 'missing'})")
        want = {}
        for ln in open(p):
            if ln.strip():
                h, q = ln.split(None, 1)
                want[q.strip().lstrip("*")] = h
        for rel in NEEDS[lst]:
            full = os.path.join(top, RUN, rel) if lst == RUN + "/SHA256SUMS" else os.path.join(top, rel)
            have = sha(full) if os.path.exists(full) else "missing"
            if want.get(rel) != have:
                stop(f"{rel}: sha256 {have[:12]} is not {lst}'s {str(want.get(rel))[:12]}")
            out.append({"path": (RUN + "/" + rel) if lst == RUN + "/SHA256SUMS" else rel, "sha256": have, "pinned_by": lst})
    return out


# ------------------------------------------------------------------------------------------------- (1) Q148(c)
def arm_m10c(top, d, scored, sd):
    sys.path.insert(0, os.path.join(top, M10C))
    import termc as TC  # noqa: E402  (unchanged: the registered rule)
    import termc_note2 as N2  # noqa: E402  (unchanged: the split, dated note 2)
    fitj = TC.load(os.path.join(top, M10C, "termc-fit.json"))
    reg = TC.score_session(scored, fitj)
    s_reg = json.dumps(reg, indent=1, sort_keys=True) + "\n"
    if open(os.path.join(sd, OUT_TERMC)).read() != s_reg:
        stop(f"{OUT_TERMC} is not termc.score_session's output on this scored.json")
    frozen = set(TC.load(os.path.join(top, M10C, "termc-note2.json"))["split"]["bridge_kinds"])
    _, _, by_bytes, _ = N2.split_kinds(fitj)
    if set(by_bytes) != frozen:
        stop("the bridge kinds by bytes are not dated note 2's frozen four")
    sp = N2.score_split(scored, fitj, frozen)
    if open(os.path.join(sd, OUT_NOTE2)).read() != json.dumps(sp, indent=1, sort_keys=True) + "\n":
        stop(f"{OUT_NOTE2} is not termc_note2.score_split's output on this scored.json")
    if sp["registered_rule"] != reg:
        stop("the split's registered rule is not termc.score_session's")
    fc = load(os.path.join(top, M10C, "forecast-m10c-e178.json"))["kinds"]
    lev = fitj["levels"]
    sig = {f: lev["primary_K"][f]["sigma_C_w"] for f in FLOATS}
    L95 = {f: lev["primary_K"][f]["L_95_w"]["a3"] for f in FLOATS}
    Kc = {f: {"L_w": lev["arm_K_card"]["a3"][f]["L_w"], "L_95_w": lev["arm_K_card"]["a3"][f]["L_95_w"]} for f in FLOATS}
    K = scored["primary"]["reported"]["kinds"]
    kinds = []
    for r in reg["kinds"]:
        k, f = r["kind"], r["fmt"]
        c = fc[k]["cards"]["a3"]
        lo, hi = c["forecast_predictive_95_w"]
        half = 1.96 * sig[f]
        kinds.append({"kind": k, "fmt": f, "bridge": k in frozen, "D_w": K[k]["D_w"], "P_scored_w": K[k]["P_w"], "x_w": r["x_w"],
                      "x_prime_w": r["x_prime_w"], "frozen_forecast_w": c["forecast_w"], "frozen_predictive_95_w": [lo, hi],
                      "D_against_the_frozen_predictive_interval": where(lo, hi, K[k]["D_w"]),
                      "x_prime_within_1.96_sigma_C": where(-half, half, r["x_prime_w"])})
    cnt = {}
    for f in FLOATS + ("all",):
        ks = [x for x in kinds if f in ("all", x["fmt"])]
        cnt[f] = {"n": len(ks)}
        for key in ("D_against_the_frozen_predictive_interval", "x_prime_within_1.96_sigma_C"):
            cnt[f][key] = {w: sum(1 for x in ks if x[key] == w) for w in ("inside", "above", "below")}
    rmsf = {f: {"n": sum(1 for r in reg["kinds"] if r["fmt"] == f),
                "rms_x_w": TC.rms([r["x_w"] for r in reg["kinds"] if r["fmt"] == f]),
                "rms_x_prime_w": TC.rms([r["x_prime_w"] for r in reg["kinds"] if r["fmt"] == f])} for f in FLOATS}
    for f in FLOATS:
        if abs(rmsf[f]["rms_x_prime_w"] - rmsf[f]["rms_x_w"] - reg["C2_d_w"][f]) > TOL:
            stop(f"{f}: the per-format rms does not give the rule's C2 d")
    m = reg["reported_m_level_w"]
    holds0 = {f: m[f]["lo95_w"] <= 0 <= m[f]["hi95_w"] for f in FLOATS}
    excl = {f: m[f]["hi95_w"] < L95[f][0] or m[f]["lo95_w"] > L95[f][1] for f in FLOATS}
    unwanted = reg["C1"]["verdict"] == "WORSE" or all(holds0[f] and excl[f] for f in FLOATS)
    return {"what": "Q148(c)'s constant-lane term, a REPORTED arm for E178 (REGISTRATION.md sections 5-6; dated note 2's split)",
            "label": NEVER + "; the rule's own words decide only whether the term enters M10 for the next blind pool",
            "scorers": {"registered": f"termc.py score -> {OUT_TERMC}", "split": f"termc_note2.py score -> {OUT_NOTE2}",
                        "reproduced_in_memory_byte_for_byte": True, "bridge_kinds_by_bytes": sorted(by_bytes)},
            "registered_rule": {k: reg[k] for k in ("C1", "C2_d_w", "C2_holds", "enters_M10_for_the_next_blind_pool", "reported_m_level_w",
                                                    "reported_L_w", "reported_arms_d_w")},
            "L_95_w": L95, "sigma_C_w": sig, "arm_K_card_a3": Kc, "rms_by_format": rmsf,
            "not_wanted_test": {"rule": "C1 WORSE; or m's interval holding 0 and excluding L's interval in both formats (REGISTRATION.md "
                                        "section 6)", "C1_WORSE": reg["C1"]["verdict"] == "WORSE", "m_holds_0": holds0,
                                "m_excludes_L_interval": excl, "shows_the_term_not_wanted": unwanted},
            "split_23_new": {k: sp["split"][k] for k in ("n_kinds", "C1", "C2_d_w", "C2_holds", "C1_BETTER_and_C2", "m_level_w",
                                                        "agrees_with_the_rule")},
            "bridge_4": {"kinds": sp["bridge_kinds"], "m_level_w": sp["bridge"]["m_level_w"],
                         "x_w": {r["kind"]: r["x_w"] for r in sp["bridge"]["kinds"]}},
            "beside_not_registered": {"what": "each kind read against the forecast's frozen 95% predictive interval: D against P + L +- "
                                              "1.96 sigma_C as frozen (s = 1, E171's zeros rate), and x' within +- 1.96 sigma_C (P at the "
                                              "session's s and measured rate, as the registered x' is)", "counts": cnt},
            "kinds": kinds}, TC


# ------------------------------------------------------------------------------------------------- (2) october-forecast-model
def arm_m1(top, d, scored, TC):
    sys.path.insert(0, os.path.join(top, E178T))
    import rail_e178 as R  # noqa: E402  (unchanged: load_runs, views, and score_e178 through R.S())
    import power_e178 as PW  # noqa: E402  (unchanged: spearman, M1-4's statistic)
    s = R.S()
    m1 = load(os.path.join(top, E178T, "m1-october-forecast-model.json"))
    if m1.get("model") != "october-forecast-model":
        stop("the M1 file does not name october-forecast-model")
    M = {k: v["w_a3"] for k, v in m1["scored"]["kinds"].items()}
    AT = {k: ("the die" if v["at"] == "the die" else "as table 1 states it") for k, v in m1["scored"]["kinds"].items()}
    v1 = {r["kind"]: r["values"][M1_FIG_FLOAT][0] for r in m1["rows"]["october-forecast-model"]}
    band2 = {r["kind"]: r["values"]["band, a3 (W)"] for r in m1["rows"]["october-forecast-model int8 v2"]}
    K = scored["primary"]["reported"]["kinds"]
    kept = sorted(k for k, v in K.items() if v.get("c_kept") and v.get("D_w") is not None and (v.get("n") or 0) >= 2)
    if sorted(M) != sorted(K):
        stop("M1's 40 kinds are not scored.json's")
    res = load(os.path.join(d, "e178.json"))
    rows = R.load_runs(os.path.join(d, "runs.csv"))
    rv, pv = R.views(rows, res)
    passes = [int(p) for p in res["passes"]]
    rail = load(os.path.join(d, "rail-arm-e178.json"))

    def pass_form(a, b, col):
        xs = s.pair_xs(pv[col], passes, a, b)
        v = [xs[p]["x"] for p in sorted(xs)]
        mm, lo, hi, _ = s.interval(v)
        return {"mean_w": mm, "lo95_w": lo, "hi95_w": hi, "n": len(v), "interval_reads": reads(lo, hi)}

    # the route for contrasts the reader does not list: it must reproduce every pass-form contrast the reader does
    mx, npf = 0.0, 0
    for c in rail["contrasts"]:
        if c["form"] != "pass":
            continue
        npf += 1
        for col in ("board", "rail"):
            mine = pass_form(c["a"], c["b"], col)
            for key in ("mean_w", "lo95_w", "hi95_w"):
                mx = max(mx, abs(mine[key] - c[col][key]))
            if mine["n"] != c[col]["n"]:
                stop(f"{c['name']}: n {mine['n']} against the reader's {c[col]['n']}")
    if mx > TOL:
        stop(f"the pass-form route differs from the reader's by {mx} W")
    route = {"pass_form_contrasts_reproduced": npf, "columns": ["board", "rail"], "max_abs_diff_w": mx}

    # the ranking (M1-4): Spearman, average ranks, of the scored figure against measured D, by format; P's beside (the scorer's own)
    rank = {}
    fr = scored["primary"]["reported"]["floats_ranking_and_slope"]
    for t in TYPES:
        ks = [k for k in kept if k.startswith(t + ".")]
        D = [K[k]["D_w"] for k in ks]
        rP = PW.spearman([K[k]["P_w"] for k in ks], D)
        want = scored["primary"]["rules"]["E178-R-int8"]["rho"] if t == "int8" else fr[t]["spearman_P"]
        if abs(rP - want) > TOL:
            stop(f"{t}: the scored P's rho {rP} is not the scorer's {want}")
        rank[t] = {"n": len(ks), "rho_model": PW.spearman([M[k] for k in ks], D), "rho_scored_P_beside": rP,
                   "model_at": AT[ks[0]], "kinds": ks}

    def entry(name, group, form, a, b, board, railc, P_frozen=None, src="the reader (rail-arm-e178.json)"):
        f = M[a] - M[b]
        e = {"name": name, "group": group, "form": form, "a": a, "b": b, "model_w": f, "model_at": AT[a], "intervals_from": src,
             "board": {k: board[k] for k in ("mean_w", "lo95_w", "hi95_w", "n")}, "rail": {k: railc[k] for k in ("mean_w", "lo95_w", "hi95_w", "n")}}
        e["board"]["interval_reads"] = reads(board["lo95_w"], board["hi95_w"])
        e["rail"]["interval_reads"] = reads(railc["lo95_w"], railc["hi95_w"])
        e["model_is_board"] = where(board["lo95_w"], board["hi95_w"], f)
        e["model_is_rail"] = where(railc["lo95_w"], railc["hi95_w"], f)
        if P_frozen is not None:
            e["P_frozen_board_w"] = P_frozen["board"]
            e["P_frozen_is_board"] = where(board["lo95_w"], board["hi95_w"], P_frozen["board"])
            e["P_frozen_rail_w"] = P_frozen["rail"]
            e["P_frozen_is_rail"] = where(railc["lo95_w"], railc["hi95_w"], P_frozen["rail"])
        return e

    contrasts = []
    pdiff = []
    for c in rail["contrasts"]:
        e = entry(c["name"], c["group"], c["form"], c["a"], c["b"], c["board"], c["rail"],
                  {"board": c["forecast_w"]["board"]["P_w"], "rail": c["forecast_w"]["rail"]["P_w"]})
        # E178's frozen P beside: its board reading must be the scorer's own reading of the scored dP (SIZE for a rule, P_inside else)
        sb = c.get("scorer_board") or {}
        if "size" in sb and sb["size"] is not None:
            same = {"PASS": "inside", "FAIL HIGH": "above", "FAIL LOW": "below"}[sb["size"]] == e["P_frozen_is_board"]
        elif "P_inside" in sb and sb["P_inside"] is not None:
            same = (sb["P_inside"] is True) == (e["P_frozen_is_board"] == "inside")
        else:
            same = None
        if same is False:
            pdiff.append(c["name"])
        contrasts.append(e)
    in52 = {(c["a"], c["b"]): c for c in rail["contrasts"]}

    def read_pair(a, b, name, group):
        if (a, b) in in52:
            c = in52[(a, b)]
            return entry(name, group, c["form"], a, b, c["board"], c["rail"], src=f"the reader (rail-arm-e178.json: {c['name']})")
        return entry(name, group, "pass", a, b, pass_form(a, b, "board"), pass_form(a, b, "rail"),
                     src="not among the reader's 52: the reader's pass-form statistic, here")

    # the five rule contrasts (M1-4's table) and the model's own stated figures
    rules = []
    for rc in m1["rule_contrasts"]:
        c = next(x for x in rail["contrasts"] if x["name"] == rc["rule"])
        e = entry(rc["rule"], "rule", c["form"], rc["a"], rc["b"], c["board"], c["rail"],
                  {"board": c["forecast_w"]["board"]["P_w"], "rail": c["forecast_w"]["rail"]["P_w"]})
        if abs(round(e["model_w"], 4) - rc["model_w_a3"]) > 1e-9:
            stop(f"{rc['rule']}: the model's figure {e['model_w']} is not M1-4's {rc['model_w_a3']}")
        e["how_M1_4"] = rc["how"]
        rules.append(e)
    beq = 0.047  # the model's own "about +0.047 W board-equivalent" for int8 5s - 4s (per_pair_as_written, int8 v2): its figure, not a scaling
    if "about +0.047 W board-equivalent" not in m1["per_pair_as_written"]["october-forecast-model int8 v2"]:
        stop("the int8 v2 per-pair line does not carry the board-equivalent figure")
    h = next(x for x in rail["contrasts"] if x["name"] == "E178-H-int8")
    own = {"figure_w": beq, "source": "the int8 v2 per-pair line, as written: 'about +0.047 W board-equivalent'",
           "is_board": where(h["board"]["lo95_w"], h["board"]["hi95_w"], beq),
           "is_board_pass_form": where(*[next(x for x in rail["contrasts"] if x["name"].startswith("his_4_5 2"))["board"][k]
                                         for k in ("lo95_w", "hi95_w")], beq)}
    # the model's extremes (M1's own list)
    ext = [read_pair(v["highest"], v["lowest"], f"the model's extreme, {t}", "model extreme") for t, v in m1["model_extremes"].items()]
    for e, (t, v) in zip(ext, m1["model_extremes"].items()):
        if abs(round(e["model_w"], 4) - v["model_w_a3"]) > 1e-9:
            stop(f"{t}'s extreme: {e['model_w']} is not M1's {v['model_w_a3']}")
    # ties in the model's scored figures (reported only, M1-4), and E178-E's equal groups beside
    ties = []
    for t in TYPES:
        ks = [k for k in kept if k.startswith(t + ".")]
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                if round(M[a], 4) == round(M[b], 4):
                    x, y = (a, b) if (a, b) in in52 or (b, a) not in in52 else (b, a)
                    ties.append(read_pair(x, y, f"a tie in the model's figures, {t}", "tie (reported only)"))
    eq = {}
    for t in TYPES:
        r = scored["primary"]["rules"][f"E178-E-{t}"]
        mem = r["members"]
        mv = [M[k] for k in mem]
        pvv = [K[k]["P_w"] for k in mem]
        eq[t] = {"members": mem, "model_spread_w": max(mv) - min(mv), "scored_P_spread_w": max(pvv) - min(pvv),
                 "measured_spread_w": r["spread_w"], "rule_line_w": r["line_w"], "model_at": AT[mem[0]]}
    # the levels: each kind's figure against its measured D (board) and Drail (minion rail), unscaled
    lev, per = {}, []
    for k in kept:
        bd = [pv["board"]["per_pass"][str(p)][k]["D"] for p in passes if pv["board"]["per_pass"].get(str(p), {}).get(k, {}).get("D") is not None]
        rl = [pv["rail"]["per_pass"][str(p)][k]["D"] for p in passes if pv["rail"]["per_pass"].get(str(p), {}).get(k, {}).get("D") is not None]
        mb, lob, hib, _ = s.interval(bd)
        mr, lor, hir, _ = s.interval(rl)
        if abs(mb - K[k]["D_w"]) > TOL or len(bd) != K[k]["n"]:
            stop(f"{k}: the per-pass D mean {mb} is not scored.json's {K[k]['D_w']}")
        f = M[k]
        e = {"kind": k, "type": k.split(".")[0], "model_w": f, "model_at": AT[k], "D_w": mb, "D_95_w": [lob, hib], "n": len(bd),
             "model_is_D": where(lob, hib, f), "Drail_w": mr, "Drail_95_w": [lor, hir], "model_is_Drail": where(lor, hir, f),
             "D_minus_model_w": mb - f, "model_over_D": f / mb, "model_over_Drail": f / mr, "D_over_model": mb / f,
             "P_scored_w": K[k]["P_w"], "D_minus_P_w": K[k]["D_minus_P_w"],
             "table1_figure_w": v1[k], "table1_over_D": v1[k] / mb,
             "check_or_blind": "check" if k in m1["labels"]["check_not_test"] else "blind"}
        if k in band2:
            lo2, hi2 = band2[k]
            e.update(band_a3_w=[lo2, hi2], measured_D_against_band=where(lo2, hi2, mb), measured_Drail_against_band=where(lo2, hi2, mr))
        per.append(e)
    for t in TYPES:
        ps = [x for x in per if x["type"] == t]
        x = TC.t_interval([p["D_minus_model_w"] for p in ps])
        xP = TC.t_interval([p["D_minus_P_w"] for p in ps])
        lev[t] = {"n": len(ps), "model_at": ps[0]["model_at"], "D_minus_model_w": x, "D_minus_scored_P_w_beside": xP,
                  "model_over_D": {"min": min(p["model_over_D"] for p in ps), "max": max(p["model_over_D"] for p in ps),
                                   "mean": sum(p["model_over_D"] for p in ps) / len(ps)},
                  "model_over_Drail": {"min": min(p["model_over_Drail"] for p in ps), "max": max(p["model_over_Drail"] for p in ps),
                                       "mean": sum(p["model_over_Drail"] for p in ps) / len(ps)},
                  "model_is_D": {w: sum(1 for p in ps if p["model_is_D"] == w) for w in ("inside", "above", "below")},
                  "model_is_Drail": {w: sum(1 for p in ps if p["model_is_Drail"] == w) for w in ("inside", "above", "below")},
                  "check_kinds_model_over_D": {p["kind"]: p["model_over_D"] for p in ps if p["check_or_blind"] == "check"},
                  "blind_kinds_model_over_D": {"min": min(p["model_over_D"] for p in ps if p["check_or_blind"] == "blind"),
                                               "max": max(p["model_over_D"] for p in ps if p["check_or_blind"] == "blind")}}
        if t == "int8":
            lev[t]["D_over_model"] = {"min": min(p["D_over_model"] for p in ps), "max": max(p["D_over_model"] for p in ps),
                                      "mean": sum(p["D_over_model"] for p in ps) / len(ps),
                                      "against": "int8 v2's units, as written: 'the board adds roughly a quarter on these cards'"}
            lev[t]["table1_int8_ones_over_D_beside"] = {"value": next(p["table1_over_D"] for p in ps if p["kind"] == "int8.ones"),
                                                        "against": "table 1's units, as written: '0.99x / 0.93x for int8 ones' "
                                                                   "(table 1's int8 rows, superseded by int8 v2: reported only)"}
            lev[t]["measured_against_the_model_band_beside"] = {
                "what": "int8 v2's own band (its 'band, a3 (W)' column: the held-operand term from 0 up to the lab's measured "
                        "ones-against-neg_ones residual), at the die; where each measured column reads against it, unscaled; not scored",
                "D": {w: sum(1 for p in ps if p["measured_D_against_band"] == w) for w in ("inside", "above", "below")},
                "Drail": {w: sum(1 for p in ps if p["measured_Drail_against_band"] == w) for w in ("inside", "above", "below")},
                "Drail_inside": [p["kind"] for p in ps if p["measured_Drail_against_band"] == "inside"]}
    lev["own_level_band_as_written"] = ("on the committed ones kinds the model reads 0.97-0.98x the measured D on aifoundry3 and 0.93x on "
                                        "card 1 (fp32 and fp16 alike), and 0.99x / 0.93x for int8 ones")

    # counts over the reader's 52 (48 distinct readings), the model and E178's frozen P side by side
    def counts(lst, key):
        return {w: sum(1 for e in lst if e.get(key) == w) for w in ("inside", "above", "below")}
    dk = set()
    distinct = []
    for e in contrasts:
        sig_ = (e["a"], e["b"], e["form"])
        if sig_ not in dk:
            dk.add(sig_)
            distinct.append(e)
    cnt = {"all_52": {k: counts(contrasts, k) for k in ("model_is_board", "model_is_rail", "P_frozen_is_board", "P_frozen_is_rail")},
           "distinct_48": {k: counts(distinct, k) for k in ("model_is_board", "model_is_rail", "P_frozen_is_board", "P_frozen_is_rail")},
           "n_distinct": len(distinct)}
    resolved = [e for e in distinct if e["board"]["interval_reads"] != "spans 0"]
    cnt["board_resolved"] = {"n": len(resolved), "names": [e["name"] for e in resolved],
                             "model_is_board": counts(resolved, "model_is_board"), "P_frozen_is_board": counts(resolved, "P_frozen_is_board")}
    rres = [e for e in distinct if e["rail"]["interval_reads"] != "spans 0"]
    cnt["rail_resolved"] = {"n": len(rres), "names": [e["name"] for e in rres],
                            "model_is_rail": counts(rres, "model_is_rail"), "P_frozen_is_rail": counts(rres, "P_frozen_is_rail")}
    by_grp = {}
    for e in distinct:
        g = e["group"].replace("reported: ", "")
        by_grp.setdefault(g, []).append(e)
    cnt["by_group_distinct"] = {g: {"n": len(v), "model_is_board": counts(v, "model_is_board"), "P_frozen_is_board": counts(v, "P_frozen_is_board"),
                                    "model_is_rail": counts(v, "model_is_rail")} for g, v in sorted(by_grp.items())}
    cnt["P_frozen_board_reading_against_the_scorers_own"] = {
        "what": "E178's frozen P beside the model is read here against the board interval; the scorer read its scored dP (s and the measured "
                "rates applied); a contrast where the two readings differ is named", "contrasts_compared": sum(1 for c in rail["contrasts"] if
                                                                                                         (c.get("scorer_board") or {})),
        "differ": pdiff}
    return {"what": "october-forecast-model, a REPORTED arm for E178 (E178.md.dated-note-M1.md, M1-4)", "label": NEVER,
            "model": "october-forecast-model", "scored_figure": m1["scored"]["figure"],
            "int8": "int8 figures are at the die (int8 v2), set against the board and the rail unscaled; each reading names its column",
            "route_check": route, "ranking": rank, "rule_contrasts": rules, "int8_his_pair_model_own_board_equivalent": own,
            "model_extremes": ext, "ties_reported_only": ties, "equal_groups_beside": eq, "levels": lev, "levels_per_kind": per,
            "contrasts_52": contrasts, "counts": cnt}


# ------------------------------------------------------------------------------------------------- (3) the rail arm, quoted
def arm_rail(d):
    j = load(os.path.join(d, "rail-arm-e178.json"))
    cs = j["contrasts"]

    def cnt(col, key, words):
        return {w: sum(1 for c in cs if c[col].get(key) == w) for w in words}
    names = {pos: [c["name"] for c in cs if c["rail"]["forecast_P_is"] == pos] for pos in ("above", "below")}
    keep = ("E178-H-int8", "E178-H-fp32", "E178-H-fp16", "E178-U", "E178-S-int8", "beside: 127 - neg_ones", "beside: 85 - 127",
            "bridge 2: int8.neg_ones - int8.ones", "extremes 4: int8.e178_v85 - int8.ones", "his_4_5 2: int8.e178_v5 - int8.e178_v4")
    rows = []
    for c in cs:
        if c["name"] in keep:
            rows.append({"name": c["name"], "a": c["a"], "b": c["b"], "form": c["form"],
                         **{col: {k: c[col][k] for k in ("mean_w", "lo95_w", "hi95_w", "n", "interval_reads")} for col in ("board", "rail", "off")},
                         "rail_forecast_P_w": c["forecast_w"]["rail"]["P_w"], "rail_forecast_P_is": c["rail"]["forecast_P_is"],
                         "off_forecast_P_w": c["forecast_w"]["off"]["P_w"], "off_forecast_P_is": c["off"]["forecast_P_is"]})
    return {"what": "the minion-rail arm (E178 dated note A3, read by A4's reader v2), as the card lane committed it: quoted, recounted",
            "label": "reported, never a verdict (E178.md.dated-note-A3.md)", "reader": j["reader"], "reader_sha256": j["reader_sha256"],
            "kept_passes": j["kept_passes"], "flagged": j["flagged"], "cross_check_with_scored_json_ok": j["cross_check_with_scored_json"]["ok"],
            "consistency_ok": j["consistency"]["ok"], "kept_runs": j["consistency"]["kept_runs"],
            "kept_runs_without_Drail": j["consistency"]["kept_runs_without_Drail"], "distinct": {k: j["distinct"][k] for k in
                                                                                             ("contrasts", "distinct_readings", "distinct_kind_pairs")},
            "frozen_ratio": j["frozen"]["ratio"],
            "recount_52": {"rail_forecast_P": cnt("rail", "forecast_P_is", ("inside", "above", "below")),
                           "rail_interval": cnt("rail", "interval_reads", ("reads above 0", "reads below 0", "spans 0")),
                           "off_forecast_P": cnt("off", "forecast_P_is", ("inside", "above", "below")),
                           "off_interval": cnt("off", "interval_reads", ("reads above 0", "reads below 0", "spans 0")),
                           "board_interval": cnt("board", "interval_reads", ("reads above 0", "reads below 0", "spans 0")),
                           "rail_forecast_P_above": names["above"], "rail_forecast_P_below": names["below"],
                           "rail_reads_above_0": [c["name"] for c in cs if c["rail"]["interval_reads"] == "reads above 0"],
                           "rail_reads_below_0": [c["name"] for c in cs if c["rail"]["interval_reads"] == "reads below 0"],
                           "off_forecast_P_above": [c["name"] for c in cs if c["off"]["forecast_P_is"] == "above"],
                           "off_forecast_P_below": [c["name"] for c in cs if c["off"]["forecast_P_is"] == "below"],
                           "off_reads_above_0": [c["name"] for c in cs if c["off"]["interval_reads"] == "reads above 0"],
                           "off_reads_below_0": [c["name"] for c in cs if c["off"]["interval_reads"] == "reads below 0"]},
            "rows_quoted": rows}


# ------------------------------------------------------------------------------------------------- the text
def f4(x):
    return f"{x:+.4f}"


def iv(e):
    return f"{e['mean_w']:+.4f} [{e['lo95_w']:+.4f}, {e['hi95_w']:+.4f}]"


def text(o):
    L = []
    P = L.append
    a, b, c = o["m10c"], o["m1"], o["rail"]
    P("E178's data README, dated note 2: E178's three REPORTED arms on the committed data (arms_note2_e178.py). " + NEVER + ".")
    P("Inputs, each checked against its committed hash list: " + "; ".join(f"{x['path']} ({x['sha256'][:12]})" for x in o["inputs"]) + ".")
    P("")
    P("(1) Q148(c)'s constant-lane term, its registered rule (termc.py score; re-run here in memory, byte for byte):")
    r = a["registered_rule"]
    C1 = r["C1"]
    P(f"  C1 over {C1['n_kinds']} float kinds: rms(x) {C1['rms_M10_w']:.4f} -> rms(x') {C1['rms_M10C_w']:.4f} W, d {C1['d_w']:+.4f} W, "
      f"95% [{C1['lo95_w']:+.4f}, {C1['hi95_w']:+.4f}]: {C1['verdict']}")
    P(f"  C2: d fp32 {r['C2_d_w']['fp32']:+.4f}, fp16 {r['C2_d_w']['fp16']:+.4f} W; holds: {r['C2_holds']}; "
      f"enters M10 for the next blind pool: {r['enters_M10_for_the_next_blind_pool']}")
    P("  rms by format (W): " + "; ".join(f"{f} {a['rms_by_format'][f]['rms_x_w']:.4f} -> {a['rms_by_format'][f]['rms_x_prime_w']:.4f} "
                                         f"({a['rms_by_format'][f]['n']} kinds)" for f in FLOATS))
    for f in FLOATS:
        m = r["reported_m_level_w"][f]
        P(f"  m {f}: {m['mean_w']:+.4f} [{m['lo95_w']:+.4f}, {m['hi95_w']:+.4f}] W over {m['n']} kinds, against L {r['reported_L_w'][f]:+.4f} "
          f"[{a['L_95_w'][f][0]:+.4f}, {a['L_95_w'][f][1]:+.4f}] (aifoundry3's own arm K-card {a['arm_K_card_a3'][f]['L_w']:+.4f} "
          f"[{a['arm_K_card_a3'][f]['L_95_w'][0]:+.4f}, {a['arm_K_card_a3'][f]['L_95_w'][1]:+.4f}])")
    P(f"  the arms' d: K-card {r['reported_arms_d_w']['K_card']:+.4f}, R {r['reported_arms_d_w']['R']:+.4f} W")
    nw = a["not_wanted_test"]
    P(f"  what would show the term is not wanted: C1 WORSE {nw['C1_WORSE']}; m holds 0 {nw['m_holds_0']}; m excludes L's interval "
      f"{nw['m_excludes_L_interval']}: shown not wanted: {nw['shows_the_term_not_wanted']}")
    s2 = a["split_23_new"]
    P(f"  the split (dated note 2, REPORTED), the 23 new kinds: C1 d {s2['C1']['d_w']:+.4f} [{s2['C1']['lo95_w']:+.4f}, {s2['C1']['hi95_w']:+.4f}] "
      f"{s2['C1']['verdict']}; C2 d fp32 {s2['C2_d_w']['fp32']:+.4f}, fp16 {s2['C2_d_w']['fp16']:+.4f}, holds {s2['C2_holds']}; agrees with the "
      f"rule {s2['agrees_with_the_rule']}")
    for f in FLOATS:
        m = s2["m_level_w"][f]
        P(f"    m {f} (new): {m['mean_w']:+.4f} [{m['lo95_w']:+.4f}, {m['hi95_w']:+.4f}] over {m['n']}")
    br = a["bridge_4"]
    P("  the 4 bridge kinds apart: " + "; ".join(f"{k} x {br['x_w'][k]:+.4f}" for k in br["kinds"]) + "; m " +
      "; ".join(f"{f} {br['m_level_w'][f]['mean_w']:+.4f} (n {br['m_level_w'][f]['n']})" for f in FLOATS))
    cn = a["beside_not_registered"]["counts"]
    P("  beside, not registered: D inside the frozen predictive interval (s = 1): " +
      "; ".join(f"{f} {cn[f]['D_against_the_frozen_predictive_interval']}" for f in FLOATS) + "; x' within +-1.96 sigma_C: " +
      "; ".join(f"{f} {cn[f]['x_prime_within_1.96_sigma_C']}" for f in FLOATS))
    XP = "x'"
    P(f"  {'kind':18s} {'bridge':6s} {'D':>8s} {'P(scored)':>9s} {'x':>8s} {XP:>8s} {'frozen P+L':>10s} {'pred. 95% (s=1)':>20s} D-in   x'-in")
    for k in a["kinds"]:
        P(f"  {k['kind']:18s} {('yes' if k['bridge'] else ''):6s} {k['D_w']:8.4f} {k['P_scored_w']:9.4f} {k['x_w']:+8.4f} {k['x_prime_w']:+8.4f} "
          f"{k['frozen_forecast_w']:10.4f} [{k['frozen_predictive_95_w'][0]:8.4f}, {k['frozen_predictive_95_w'][1]:8.4f}] "
          f"{k['D_against_the_frozen_predictive_interval']:6s} {k['x_prime_within_1.96_sigma_C']}")
    P("")
    P("(2) october-forecast-model, by E178's dated note M1, M1-4 (the scored figure: floats table 1's a3 column; int8 int8 v2's a3 die column):")
    rc = b["route_check"]
    P(f"  route check: the reader's pass-form statistic reproduces its {rc['pass_form_contrasts_reproduced']} pass-form contrasts on the board "
      f"and rail to {rc['max_abs_diff_w']:.1e} W")
    for t in TYPES:
        k = b["ranking"][t]
        P(f"  ranking {t}: Spearman rho {k['rho_model']:+.3f} over {k['n']} kinds (E178's scored P beside: {k['rho_scored_P_beside']:+.3f})")
    P("  the five rule contrasts and the model's extremes, against the board and rail intervals:")
    for e in b["rule_contrasts"] + b["model_extremes"]:
        P(f"    {e['name']:28s} {e['a']} - {e['b']}: model {e['model_w']:+.4f} ({e['model_at']}); board {iv(e['board'])} -> {e['model_is_board']}; "
          f"rail {iv(e['rail'])} -> {e['model_is_rail']}" + (f"; E178's frozen P {e['P_frozen_board_w']:+.4f} {e['P_frozen_is_board']}" if
                                                            'P_frozen_board_w' in e else "") + f" [{e['intervals_from']}]")
    ow = b["int8_his_pair_model_own_board_equivalent"]
    P(f"  int8 5s - 4s, the model's own board-equivalent +{ow['figure_w']:.3f} W: {ow['is_board']} the couple-form board interval, "
      f"{ow['is_board_pass_form']} the pass-form one")
    P("  ties in the model's figures (reported only):")
    for e in b["ties_reported_only"]:
        P(f"    {e['a']} - {e['b']}: model {e['model_w']:+.4f}; board {iv(e['board'])} ({e['board']['interval_reads']}), "
          f"rail {iv(e['rail'])} ({e['rail']['interval_reads']}) [{e['intervals_from']}]")
    P("  E178-E's equal groups beside (spreads, W): " + "; ".join(
        f"{t}: model {v['model_spread_w']:.4f}, scored P {v['scored_P_spread_w']:.4f}, measured {v['measured_spread_w']:.4f} "
        f"(line {v['rule_line_w']:.4f})" for t, v in b["equal_groups_beside"].items()))
    cn = b["counts"]
    P(f"  over the reader's 52 (48 distinct): model inside / above / below the board interval {cn['distinct_48']['model_is_board']}, the rail "
      f"interval {cn['distinct_48']['model_is_rail']}; E178's frozen P beside: board {cn['distinct_48']['P_frozen_is_board']}, rail "
      f"{cn['distinct_48']['P_frozen_is_rail']} (all 52: model board {cn['all_52']['model_is_board']}, rail {cn['all_52']['model_is_rail']})")
    br_ = cn["board_resolved"]
    P(f"  the {br_['n']} distinct board intervals that do not span 0: model {br_['model_is_board']}, P {br_['P_frozen_is_board']}: "
      + "; ".join(br_["names"]))
    rr_ = cn["rail_resolved"]
    P(f"  the {rr_['n']} distinct rail intervals that do not span 0: model {rr_['model_is_rail']}, P {rr_['P_frozen_is_rail']}: "
      + "; ".join(rr_["names"]))
    for g, v in cn["by_group_distinct"].items():
        P(f"    {g}: {v['n']}; model board {v['model_is_board']}, rail {v['model_is_rail']}; P board {v['P_frozen_is_board']}")
    pq = cn["P_frozen_board_reading_against_the_scorers_own"]
    P(f"  E178's frozen P on the board against the scorer's own reading of its scored dP: {pq['contrasts_compared']} compared, differ in "
      f"{len(pq['differ'])}" + (": " + "; ".join(pq["differ"]) if pq["differ"] else ""))
    P("  the levels (each kind's figure against its measured D and Drail, unscaled; intervals over kept passes):")
    for t in TYPES:
        v = b["levels"][t]
        x = v["D_minus_model_w"]
        P(f"    {t} ({v['model_at']}), {v['n']} kinds: D - model {x['mean_w']:+.4f} [{x['lo95_w']:+.4f}, {x['hi95_w']:+.4f}] W (D - scored P beside "
          f"{v['D_minus_scored_P_w_beside']['mean_w']:+.4f}); model/D {v['model_over_D']['min']:.3f}-{v['model_over_D']['max']:.3f} (mean "
          f"{v['model_over_D']['mean']:.3f}); model/Drail {v['model_over_Drail']['min']:.3f}-{v['model_over_Drail']['max']:.3f}; model "
          f"inside / above / below D's interval {v['model_is_D']}, Drail's {v['model_is_Drail']}; the check kinds' model/D "
          + ", ".join(f"{k} {q:.3f}" for k, q in v["check_kinds_model_over_D"].items()) +
          f"; the blind kinds' {v['blind_kinds_model_over_D']['min']:.3f}-{v['blind_kinds_model_over_D']['max']:.3f}")
        if t == "int8":
            q = v["D_over_model"]
            P(f"      int8 D/model {q['min']:.3f}-{q['max']:.3f} (mean {q['mean']:.3f}), against {q['against']}; table 1's int8 ones/D "
              f"{v['table1_int8_ones_over_D_beside']['value']:.3f}, against {v['table1_int8_ones_over_D_beside']['against']}")
            bb = v["measured_against_the_model_band_beside"]
            P(f"      against int8 v2's own band (beside, not scored): D {bb['D']}, Drail {bb['Drail']} (Drail inside: "
              + ", ".join(bb["Drail_inside"]) + ")")
    P(f"    the model's own level band, as written: {b['levels']['own_level_band_as_written']}")
    P(f"  {'kind':18s} {'model':>8s} {'D':>8s} {'D 95%':>19s} is   {'Drail':>8s} {'Drail 95%':>19s} is   model/D")
    for p in b["levels_per_kind"]:
        P(f"  {p['kind']:18s} {p['model_w']:8.4f} {p['D_w']:8.4f} [{p['D_95_w'][0]:8.4f}, {p['D_95_w'][1]:8.4f}] {p['model_is_D']:6s} "
          f"{p['Drail_w']:8.4f} [{p['Drail_95_w'][0]:8.4f}, {p['Drail_95_w'][1]:8.4f}] {p['model_is_Drail']:6s} {p['model_over_D']:.4f}")
    P("  every contrast of the reader's 52 (model; board interval -> model, P; rail interval -> model, P):")
    for e in b["contrasts_52"]:
        P(f"    {e['name'][:58]:58s} {e['model_w']:+.4f}; B {iv(e['board'])} {e['model_is_board']}, {e['P_frozen_is_board']}; "
          f"R {iv(e['rail'])} {e['model_is_rail']}, {e['P_frozen_is_rail']}")
    P("")
    P(f"(3) the minion-rail arm as committed ({c['reader']}, sha256 {c['reader_sha256'][:12]}): kept passes {c['kept_passes']}; "
      f"{c['kept_runs']} kept runs, {c['kept_runs_without_Drail']} without a Drail; flagged {len(c['flagged'])}; cross-check with scored.json "
      f"{c['cross_check_with_scored_json_ok']}; {c['distinct']['contrasts']} contrasts, {c['distinct']['distinct_readings']} distinct readings")
    rc3 = c["recount_52"]
    P(f"  recount over 52: the rail P forecast {rc3['rail_forecast_P']}; the rail interval {rc3['rail_interval']}; the off-rail P "
      f"forecast {rc3['off_forecast_P']}; the off-rail interval {rc3['off_interval']}; the board interval {rc3['board_interval']}")
    P("  the rail P forecast above: " + "; ".join(rc3["rail_forecast_P_above"]))
    P("  the rail P forecast below: " + "; ".join(rc3["rail_forecast_P_below"]))
    P("  the rail reads above 0: " + "; ".join(rc3["rail_reads_above_0"]) + "; below 0: " + "; ".join(rc3["rail_reads_below_0"]))
    P("  off the rail, the P forecast above: " + "; ".join(rc3["off_forecast_P_above"]) + "; below: " + "; ".join(rc3["off_forecast_P_below"]))
    P("  off the rail, the interval reads above 0: " + "; ".join(rc3["off_reads_above_0"]) + "; below 0: " + "; ".join(rc3["off_reads_below_0"]))
    for rw in c["rows_quoted"]:
        P(f"    {rw['name'][:44]:44s} board {iv(rw['board'])}; rail {iv(rw['rail'])} ({rw['rail']['interval_reads']}), P {rw['rail_forecast_P_w']:+.4f} "
          f"{rw['rail_forecast_P_is']}; off {iv(rw['off'])} ({rw['off']['interval_reads']}), P {rw['off_forecast_P_w']:+.4f} {rw['off_forecast_P_is']}")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=HERE, help="E178's data directory (default: this file's)")
    ap.add_argument("--out", default=None, help="where the two outputs go (default: --dir)")
    ap.add_argument("--scorers", default=None, help="where Q148(c)'s two scorer outputs are (default: --dir)")
    a = ap.parse_args(argv)
    d = os.path.abspath(a.dir)
    top = os.path.abspath(os.path.join(d, "..", "..", "..", ".."))
    if os.path.relpath(d, top) != RUN:
        stop(f"--dir is not {RUN} inside a lab tree")
    sd = os.path.abspath(a.scorers or d)
    inputs = pins(top)
    scored = load(os.path.join(d, "scored.json"))
    if scored.get("card") != "aifoundry3" or scored["primary"].get("kept_passes") != [17810, 17811, 17812, 17813]:
        stop("scored.json is not E178's aifoundry3 session with its four kept passes")
    m10c, TC = arm_m10c(top, d, scored, sd)
    o = {"_what": "E178's data README, dated note 2: E178's three REPORTED arms read on the committed data (arms_note2_e178.py)",
         "label": NEVER, "run": "E178", "card": "aifoundry3", "inputs": inputs,
         "scorer_outputs_beside": {OUT_TERMC: sha(os.path.join(sd, OUT_TERMC)), OUT_NOTE2: sha(os.path.join(sd, OUT_NOTE2))},
         "m10c": m10c, "m1": arm_m1(top, d, scored, TC), "rail": arm_rail(d)}
    out = os.path.abspath(a.out or d)
    js = json.dumps(o, indent=1, sort_keys=True) + "\n"
    txt = text(o)
    for bad in {top, os.path.expanduser("~"), HERE, out}:
        if bad and bad != os.sep and (bad in js or bad in txt):
            stop("an output would carry a desk path")
    open(os.path.join(out, "arms-note2-e178.json"), "w").write(js)
    open(os.path.join(out, "arms-note2-e178.txt"), "w").write(txt)
    print(f"ARMS NOTE 2: wrote arms-note2-e178.json and arms-note2-e178.txt ({len(o['m1']['contrasts_52'])} contrasts; Q148(c) C1 "
          f"{m10c['registered_rule']['C1']['verdict']}, enters {m10c['registered_rule']['enters_M10_for_the_next_blind_pool']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
