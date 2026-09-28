#!/usr/bin/env python3
"""Heat placement (HP, DESIGN2): the reducer. It works on whatever blocks exist (partial data gives None / INSUFFICIENT).

    reduce.py --check-pass <block dir> --card C          block.sh's end-of-block check (stdlib only; prints a note)
    reduce.py --data <card data dir> --card C --dev [--out dev.json]
                                                         development report: every item REPORTED with its 99% CI
    reduce.py --data <dir> --card aifoundry3 --p1 [--out p1.json]
                                                         power step 1 and D-S, D-L16, D-L8 (DESIGN2 §2.4, §5.3)
                                                         --p1 and --p3 take every edge and run parameter from the
                                                         blocks' own plan.json and runs.jsonl, never from the current
                                                         params files; they refuse a block without that record and an
                                                         item whose blocks ran at different edges (README departure 35)
    reduce.py --data <dir> --card aifoundry3 --p3 --cal-card1 <card-1 data dir> [--out registration.json]
                                                         power step 3: the registration rule, beta, the primary
                                                         contrast, n_val (prereg.py turns it into PREREG.md); it
                                                         refuses without card 1's V0 data (the CV ratio) unless
                                                         --allow-no-card1, which is then stated in the output
    reduce.py --data <dir> --card aifoundry1-c1 --val --prereg tools/claims-v3/hp/prereg/prereg.json
              [--amendment AMENDMENT.md] [--out verdicts.json]
                                                         validation: each registered item's result and V3 outcome
                                                         word, on the first n_val usable blocks of each type; it
                                                         refuses unless the PREREG lock holds (PREREG.md, prereg.json,
                                                         params-val, the code) and every validation block ran under
                                                         this PREREG with the locked binaries; a reducer fix after
                                                         the freeze needs --amendment (DESIGN2 §6.4), recorded

<card data dir> is build/claims-v3/<card> (the blocks are under hp/p<pass>/). Definitions, all fixed in DESIGN2 before
any data:
  observables (§2.1): hplib.run_observables (t0 from the heater's own t_start_ms; t66 = the first sample with
      temp_c.minshire[0] >= 66 minus t0, censored at C = 7 s (Tier S) or 150 s (Tier L); W_idle; sw_W; ops_rate;
      tau_c; Delta-hot and iota_io from the 1 s peak-hold windows; the clock and sampler-gap void rules);
  kappa (§2.1): a Foster network (tools/ettelem/flip_thermal_model.py's TAUS, nnls and lowpass, unchanged) fitted to
      the block's uniform-power and idle samples (its CAL run(s), the ALL24 preheats and the cool-downs: everything but
      each measured run's launch + 30 s) with measured board_w as input, simulated from the block's first sample; per run the
      gain g that scales the run's switching power (board_w - W_idle over the launch) to best reproduce the readings
      from t0 - 2 s to the launch end + 10 s; gate: the predicted whole-degree floor equals the reading in >= kappa_gate
      (0.90) of the window's samples, else None;
  contrasts (§2.2): L(A/B) = ln min(t66_A, C) - ln min(t66_B, C), no pair dropped for censoring; L_adj = L -
      beta (ln tau_c,A - ln tau_c,B); L_P = L + ln(sw_W_A / sw_W_B); L_ops = L + ln(ops_A / ops_B); kappa, Delta-hot,
      iota_io as A - B; a sign count over blocks (censored runs ranked longest, two censored runs tied) with an exact
      binomial p;
  outcomes (§2.3): SIGN+/SIGN- hold if the 99% CI excludes 0 on the predicted side, fail if it excludes 0 on the
      other side or lies wholly inside +-band; NONZERO holds if it excludes 0, fails inside +-band; EQUIV holds inside
      +-band, fails wholly outside; otherwise None; < 3 kept blocks None. V3's words over the registered cards;
  void rules (§4.4): run void (rc, clock, edge, sampler gap, safety stop, WORK outside +-5% of the block median; the
      block's re-run replaces it); block void (a run's tau_c outside [0.5, 2] x the block median, or the W_idle range
      > 1.0 W, both as frozen in the round's params); a block is kept only if every registered pair in it is complete
      (development: every registrable item's placements; validation: the registered items'), else it is dropped from
      every item.
"""
import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hplib as H  # noqa: E402
from hplib import ci99, mean, median, outcome, sd, load_jsonl, heater_lines, run_observables  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# ---- items (DESIGN2 §4.1): (id, block type, (A, B) or special, statistic, band key, fixed prediction or None)
PAIR_ITEMS = [
    ("PLACE-t", "L16", ("PER16@32", "INT16@32"), "L", "band_t", None),
    ("PLACE-kappa", "L16", ("PER16@32", "INT16@32"), "kappa", "band_kappa", None),
    ("PLACE8-t", "L8", ("PER16@16", "INT16@16"), "L", "band_t", None),
    ("PLACE-tS", "S", ("PER16@32", "INT16@32"), "L", "band_t", None),
    ("PLACE-kappa-S", "S", ("PER16@32", "INT16@32"), "kappa", "band_kappa", None),
    ("MEM", "L8", ("MEM8", "CEN8"), "L", "band_t", None),
    ("EDGE", "L8", ("EDGE8", "CEN8"), "L", "band_t", None),
    ("GRAD-EW", "G8", ("E8b", "W8b"), "L", "band_t", "NONZERO"),
    ("GRAD-NS", "G8", ("N8b", "S8b"), "L", "band_t", "NONZERO"),
]
SPECIAL_ITEMS = [
    ("LIN", "L8", "lin", "band_kappa", "EQUIV"),
    ("CONC", "S", "conc", "band_conc_c", "SIGN+"),
    ("MAP", "S", "map", "band_map_c", "SIGN+"),
]
REPORTED_ONLY = [
    ("SPREAD", "L16", ("UNI32@16", "INT16@32"), "L"),
    ("CONC-L", "L16", "conc_l"),
    ("INTRA-TILE", "L16", "intra"),
]
# DESIGN2 names a primary item for L16 only (PLACE-t, §0 and §4.1). For S, L8 and G8, §2.4 step 5's "the type's primary
# item" is undefined: there n_val is the smallest n in [5, n_max] at which ANY candidate of the type meets step 4
# (choose_n_val; README departure 22, fixed 27 Sep before P3; review low: picking CONC, PLACE8-t and GRAD-EW capped
# every other item of the type at n_val = 5 whenever that pick was no candidate)
PRIMARY_OF_TYPE = {"L16": "PLACE-t"}
# the placements each item needs in a block (a block is kept only if every registered item's are complete: §4.4)
ITEM_NAMES = {it[0]: set(it[2]) for it in PAIR_ITEMS}
ITEM_NAMES.update({"LIN": {"UNI32@16", "INT16@16", "PER16@16"}, "CONC": {"INT16@32", "PER16@32", "UNI32@16"},
                   "MAP": {"B4NE", "B4SW"}})
ITEM_TYPE = {it[0]: it[1] for it in PAIR_ITEMS}
ITEM_TYPE.update({it[0]: it[1] for it in SPECIAL_ITEMS})
# POWER and WORK are registered EQUIV on every pair of a registered item (§2.4 step 6, §4.5); LIN's second pair is
# the identity P_UNI = P_I + P_P (§4.6): power UNI - (INT + PER), work ln(ops_UNI / mean(ops_INT, ops_PER))
POWER_WORK_PAIRS = {it[0]: [tuple(it[2])] for it in PAIR_ITEMS}
POWER_WORK_PAIRS.update({"CONC": [("INT16@32", "UNI32@16"), ("PER16@32", "UNI32@16")], "MAP": [("B4NE", "B4SW")],
                         "LIN": [("PER16@16", "INT16@16"), ("UNI32@16", ("INT16@16", "PER16@16"))]})
# README departure 37 (27 Sep 2026, decided before any validation data): Tier S's POWER cannot be computed for a pair
# with INT16@32: sw_W is the median over t0 + 1 s .. t0 + t66 (§5.5, unchanged), and INT16@32 crosses 66 C in < 1 s from
# S_S 64 (R1c: 0.86-0.97 s), so its window is empty. POWER is waived for those pairs (PLACE-tS, PLACE-kappa-S and CONC's
# INT16@32-UNI32@16), reported as POWER_WAIVED_WORD, never INSUFFICIENT; equal power for INT/PER/UNI rests on Tier L
# (R1c L16: INT16@32 13.96, PER16@32 13.87, UNI32@16 13.83 W; every pair within +-0.5 W). WORK is not waived.
POWER_WAIVED = {"S": {"INT16@32"}}
POWER_WAIVED_WORD = "waived: no window in Tier S; see Tier L"


def power_waived(typ, pair):
    """True if POWER is waived for this pair of an item of block type typ (README departure 37)."""
    A, B = pair
    return bool(POWER_WAIVED.get(typ, set()) & ({A} | set(B if isinstance(B, tuple) else (B,))))


REDUCER_FILES = ("reduce.py", "hplib.py", "sptrace_events.py", "placements.json", "flip_thermal_model.py")
BLOCK_MIN_CARD1 = {"L16": 7, "L8": 14, "S": 10, "G8": 10}      # DESIGN2 §6.1 estimates, minutes per block
PRIORITY = ["L16", "L8", "S", "G8"]
CARD1_CAP_MIN = 300


# ------------------------------------------------------------------------------------------------ check-pass
def check_pass(out, card):
    """Stdlib only. Exit 0 if the block has at least one run with telemetry and heater output."""
    runs = load_jsonl(os.path.join(out, "runs.jsonl"))
    plan = H.load_json(os.path.join(out, "plan.json"), {}) or {}
    if not runs:
        print("no runs")
        return 1
    n_tel = n_heat = n66 = n_edge_miss = n_stop = 0
    rcs = []
    for r in runs:
        tel = load_jsonl(os.path.join(out, "tel-%s.jsonl" % r["idx"]))
        hl = heater_lines(os.path.join(out, "heater-%s.out" % r["idx"]))
        n_tel += len(tel) >= 20
        n_heat += bool(hl)
        n66 += r.get("first66_live_ms") is not None
        n_edge_miss += (r.get("tier") in ("S", "L") and not r.get("edge_ok"))
        n_stop += bool(r.get("stop"))
        rcs += r.get("rcs", [])
    bad_rc = [x for x in rcs if x != 0]
    note = "%d runs (%s): telemetry %d, heater lines %d, first 66 live %d, edge misses %d, stops %d, rc %s" % (
        len(runs), (plan.get("info") or {}).get("type", "?"), n_tel, n_heat, n66, n_edge_miss, n_stop,
        "all 0" if not bad_rc else bad_rc)
    sps = sorted(glob.glob(os.path.join(out, "sp-*.bin")))
    if sps:
        try:
            import sptrace_events as SE
            lv = SE.level(SE.events(open(sps[-1], "rb").read()))
            note += ", %d SP dumps (last at %s)" % (len(sps), lv)
        except Exception as e:
            note += ", SP dump unreadable (%s)" % e
    print(note)
    return 0 if n_tel and n_heat else 1


# ------------------------------------------------------------------------------------------------ loading
def load_blocks(data, card, rounds=None):
    """Every finished hp block of a card: {pass, round, type, k, params, runs: [(record, observables)], ...}."""
    blocks = []
    for bj in sorted(glob.glob(os.path.join(data, "hp", "p*", "block.json"))):
        d = os.path.dirname(bj)
        b = H.load_json(bj) or {}
        plan = H.load_json(os.path.join(d, "plan.json"), {}) or {}
        info = plan.get("info") or {}
        if b.get("status") != "ok" or not info or info.get("skip"):
            continue
        if info.get("type") not in ("S", "L16", "L8", "G8", "SCOUT", "CAL", "B1"):
            continue
        if rounds and info.get("round") not in rounds:
            continue
        # the params the block ran with, as its plan.json recorded them; the current params file only for a block
        # that recorded none (--dev and --val keep that fallback; --p1 and --p3 refuse such a block: require_records)
        recorded = bool(plan.get("params"))
        P = plan.get("params") or H.resolve_params(info.get("round", "r1"), card)
        runs = []
        for r in load_jsonl(os.path.join(d, "runs.jsonl")):
            tel = load_jsonl(os.path.join(d, "tel-%s.jsonl" % r["idx"]))
            hl = heater_lines(os.path.join(d, "heater-%s.out" % r["idx"]))
            o = run_observables(r, tel, hl, card, P)
            runs.append({"rec": r, "obs": o, "tel": tel, "hl": hl})
        blk = {"dir": d, "pass": info.get("pass"), "round": info.get("round"), "type": info.get("type"),
               "k": info.get("k"), "params": P, "params_recorded": recorded, "plan_runs": plan.get("runs") or [],
               "runs": runs, "void": [], "seed": info.get("seed")}
        work_void(blk)
        block_void(blk)
        blocks.append(blk)
    return blocks


def work_void(blk):
    P = blk["params"]
    rates = [x["obs"]["ops_rate"] for x in blk["runs"] if x["rec"].get("role") == "meas" and x["obs"].get("ops_rate")
             and not x["obs"]["void"]]
    med = median(rates)
    for x in blk["runs"]:
        o = x["obs"]
        if med and o.get("ops_rate") and abs(math.log(o["ops_rate"] / med)) > P.get("void_work", 0.05):
            o["void"].append("WORK outside +-%.0f%% of the block median" % (100 * P.get("void_work", 0.05)))


def kept_runs(blk):
    """The latest non-void attempt of each slot of the block's measured runs: {slot: (rec, obs)}."""
    by = {}
    for x in blk["runs"]:
        r = x["rec"]
        if r.get("role") != "meas":
            continue
        by.setdefault(r.get("slot"), []).append(x)
    out = {}
    for slot, lst in by.items():
        ok = [x for x in lst if not x["obs"]["void"]]
        if ok:
            out[slot] = ok[-1]
    return out


def block_void(blk):
    P = blk["params"]
    kr = list(kept_runs(blk).values())
    taus = [x["obs"].get("tau_c_s") for x in kr if x["obs"].get("tau_c_s")]
    med = median(taus)
    if med and blk["type"] in ("S", "L16", "L8", "G8"):
        lo, hi = P.get("void_tauc_lo", 0.5) * med, P.get("void_tauc_hi", 2.0) * med
        bad = [t for t in taus if not lo <= t <= hi]
        if bad:
            blk["void"].append("tau_c %s outside [%.2f, %.2f] s" % (bad, lo, hi))
    w = [x["obs"].get("W_idle") for x in kr if x["obs"].get("W_idle") is not None]
    if w and max(w) - min(w) > P.get("void_widle_range_w", 1.0):
        blk["void"].append("W_idle range %.2f W > %.2f W" % (max(w) - min(w), P.get("void_widle_range_w", 1.0)))


def by_name(blk):
    """{placement name: [obs, ...]} of the block's kept measured runs."""
    out = {}
    for slot, x in sorted(kept_runs(blk).items()):
        out.setdefault(x["rec"]["name"], []).append(x)
    return out


def usable(blk):
    """A block enters the items only if it is not void and every registered pair in it is complete (§4.4)."""
    return not blk["void"] and not blk.get("incomplete")


def mark_incomplete(blocks, items=None):
    """blk['incomplete'] = the needed placements missing from the block; items: the registered item ids (validation),
    or None for every registrable item (development: every pair counts as registered)."""
    ids = list(ITEM_NAMES) if items is None else [i for i in items if i in ITEM_NAMES]
    for blk in blocks:
        if blk["type"] not in ("S", "L16", "L8", "G8"):
            continue
        need = set()
        for i in ids:
            if ITEM_TYPE.get(i) == blk["type"]:
                need |= ITEM_NAMES[i]
        blk["incomplete"] = sorted(need - set(by_name(blk)))


# ------------------------------------------------------------------------------------------------ run records
# P1 and P3 take every run parameter (the start edge above all) from each block's own files, never from the current
# params files: a round's params file is edited between rounds (D-L16 and D-L8 set params-r1's S_L and S_L8 for R1c
# after the R1b scouting blocks), so re-reading it judged old blocks as if they had run at the new edges (27 Sep: after
# params-r1 became S_L 61 / S_L8 64, --p1 on the R1b blocks, which ran at S_L 60 / S_L8 63, said "S_L 62" and
# "censored at S_L8 = 64: L8 and G8 dropped"). A block without the record is refused, never filled in from a params file.
# RUN_PARAM_KEYS: the params that set how a run is run and censored; with the type and the recorded start edge they are
# "identical parameters" (DESIGN2 §2.4 P1 and P3, §5.4).
RUN_PARAM_KEYS = ("S_L", "S_L8", "S_S", "target_S", "target_L_over", "target_L8_over", "chain_cap_s", "C_L", "C_S",
                  "chain_launch_s", "chain_after_66", "S_launch_s")


def params_edge(blk):
    """The start edge the block's own plan.json params give its runs (hplib.plan's rule), or None (CAL, B1)."""
    P, typ, k = blk["params"], blk["type"], blk.get("k")
    if typ == "S" or (typ == "SCOUT" and k == 3):
        return P.get("S_S")
    if typ == "L16" or (typ == "SCOUT" and k == 1):
        return P.get("S_L")
    if typ in ("L8", "G8") or (typ == "SCOUT" and k == 2):
        return P.get("S_L8")
    return None


def run_edge(blk, x):
    """A run's start edge as its block recorded it: runs.jsonl's 'edge', else plan.json's entry for the run's slot."""
    e = x["rec"].get("edge")
    if e is None:
        pr, s = blk.get("plan_runs") or [], x["rec"].get("slot")
        if isinstance(s, int) and 1 <= s <= len(pr):
            e = pr[s - 1].get("edge")
    return e


def require_records(blocks, who):
    """Refuse (exit) unless every block recorded its params (plan.json) and ONE start edge for all its runs that agrees
    with those params; sets blk['edge']. The current params files are never consulted. who: 'P1' or 'P3'."""
    for blk in blocks:
        if not blk.get("params_recorded"):
            raise SystemExit("%s refused: block p%s has no params in its plan.json, so the edge and parameters it ran "
                             "at are not recorded (the current params file is not what it ran at)" % (who, blk["pass"]))
        pe = params_edge(blk)
        seen = {}
        for x in blk["runs"]:
            e = run_edge(blk, x)
            e = pe if e is None else e
            if e is None:
                raise SystemExit("%s refused: block p%s run %s has no recorded start edge (runs.jsonl, plan.json)"
                                 % (who, blk["pass"], x["rec"].get("idx")))
            if pe is not None and e != pe:
                raise SystemExit("%s refused: block p%s run %s recorded edge %s, but its plan.json params give %s: the "
                                 "block's records disagree" % (who, blk["pass"], x["rec"].get("idx"), e, pe))
            seen.setdefault(e, []).append(x["rec"].get("idx"))
        if len(seen) > 1:
            raise SystemExit("%s refused: block p%s ran at more than one start edge (%s)" % (
                who, blk["pass"], "; ".join("%s: runs %s" % kv for kv in sorted(seen.items()))))
        blk["edge"] = next(iter(seen)) if seen else pe


def same_params_key(blk):
    """'Identical parameters' (DESIGN2 §2.4, §5.4): the block type, its recorded start edge and the run parameters of
    its own plan.json (require_records sets the edge)."""
    P = blk["params"]
    return (blk["type"], blk.get("edge")) + tuple(P.get(k) for k in RUN_PARAM_KEYS)


def edges_of(blks):
    """{edge: [passes]} of blocks (for the reports)."""
    out = {}
    for b in sorted(blks, key=lambda b: b["pass"]):
        out.setdefault(str(b.get("edge")), []).append(b["pass"])
    return out


def one_key(blks, what, who):
    """The blocks one item (or one decision) pools must share one parameter key: DESIGN2 pools only runs and blocks
    'with identical parameters' (§2.4 P1, P3; §5.4) and nowhere pools blocks run at different edges. Refuses (exit)
    otherwise, naming the edges and the parameters that differ; returns {edge: [passes]}."""
    groups = {}
    for b in blks:
        groups.setdefault(same_params_key(b), []).append(b["pass"])
    if len(groups) > 1:
        keys = list(groups)
        diff = [n for i, n in enumerate(("type", "edge") + RUN_PARAM_KEYS) if len({k[i] for k in keys}) > 1]
        names = ("type", "edge") + RUN_PARAM_KEYS
        desc = "; ".join("%s: p%s" % (", ".join("%s %s" % (n, k[names.index(n)]) for n in diff),
                                      ", p".join(str(p) for p in sorted(ps))) for k, ps in groups.items())
        raise SystemExit("%s refused: %s would pool blocks run at different parameters (%s); DESIGN2 pools only "
                         "identical parameters (§2.4, §5.4)" % (who, what, desc))
    return edges_of(blks)


# ------------------------------------------------------------------------------------------------ kappa
def kappa_block(blk, card):
    """The block's kappa per run (DESIGN2 §2.1); needs numpy. Sets obs['kappa'] and obs['kappa_gate']."""
    try:
        import numpy as np
        sys.path.insert(0, os.path.join(ROOT, "tools", "ettelem"))
        from flip_thermal_model import TAUS, nnls, lowpass, DT
    except Exception as e:
        blk["kappa_note"] = "kappa not computed: %s" % e
        return
    P = blk["params"]
    gate = P.get("kappa_gate", 0.90)
    samp = sorted([(s["t_ms"], s["temp_c"]["minshire"][0], s.get("board_w")) for x in blk["runs"] for s in x["tel"]
                   if s.get("t_ms") and (s.get("temp_c") or {}).get("minshire") and s.get("board_w") is not None])
    if len(samp) < 100:
        blk["kappa_note"] = "too few samples"
        return
    t = np.array([s[0] for s in samp]) / 1000.0
    tt = np.arange(t[0], t[-1], DT)
    Pw = np.interp(tt, t, np.array([s[2] for s in samp]))
    j = np.clip(np.searchsorted(t, tt), 0, len(t) - 1)
    jm = np.clip(j - 1, 0, len(t) - 1)
    near = np.where(np.abs(t[j] - tt) < np.abs(t[jm] - tt), j, jm)
    valid = np.abs(t[near] - tt) <= 0.15
    Tread = np.array([s[1] for s in samp], float)[near]
    slow = [k for k, tau in enumerate(TAUS) if tau >= 60]
    lps = [lowpass(Pw, tau, x0=float(Pw[0])) for tau in TAUS]
    dec = [np.exp(-(tt - tt[0]) / TAUS[k]) for k in slow]
    X = np.column_stack([np.ones(len(tt))] + dec + lps)
    nfree = 1 + len(slow)

    def mask_of(o, pre=2.0, post=10.0):
        if o.get("t0_ms") is None:
            return None
        return (tt >= o["t0_ms"] / 1000.0 - pre) & (tt <= o["t_end_ms"] / 1000.0 + post) & valid
    # the fit set: every uniform-power or idle sample of the block (the CAL run(s), every ALL24 preheat burst, every
    # cool-down and edge wait), i.e. everything but each measured placement run's launch and the 30 s after it. The
    # CAL chain alone (about a minute) cannot identify the slow stages that carry heat into runs minutes later (on the
    # synthetic self-test a planted kappa of 1.0 came back 0.4-1.0; README.md, departures)
    cal = valid.copy()
    for x in blk["runs"]:
        o = x["obs"]
        if x["rec"].get("role") == "meas" and o.get("t0_ms") is not None:
            cal &= ~((tt >= o["t0_ms"] / 1000.0) & (tt <= o["t_end_ms"] / 1000.0 + 30.0))
    if not any(x["rec"].get("role") == "cal" and not x["obs"]["void"] for x in blk["runs"]) or cal.sum() < 300:
        blk["kappa_note"] = "no usable CAL run or too few uniform-power samples"
        return
    y = Tread + 0.5
    th = nnls(X[cal], y[cal], free=nfree)
    pred = X @ th
    R = th[nfree:]
    fit_match = float(np.mean(np.floor(pred[cal]) == Tread[cal]))
    blk["kappa_network"] = {"R": [float(v) for v in R], "match_cal": fit_match, "n_cal": int(cal.sum())}
    for x in blk["runs"]:
        o = x["obs"]
        if x["rec"].get("role") != "meas" or o.get("t0_ms") is None or o.get("W_idle") is None:
            continue
        m = mask_of(o)
        on = (tt >= o["t0_ms"] / 1000.0) & (tt <= o["t_end_ms"] / 1000.0)
        dP = np.where(on, Pw - o["W_idle"], 0.0)
        B = sum(R[k] * lowpass(dP, tau, x0=0.0) for k, tau in enumerate(TAUS))
        if m is None or m.sum() < 20 or float(np.sum(B[m] ** 2)) <= 0:
            continue
        gm1 = float(np.sum((y[m] - pred[m]) * B[m]) / np.sum(B[m] ** 2))
        fit = pred + gm1 * B
        match = float(np.mean(np.floor(fit[m]) == Tread[m]))
        o["kappa_raw"] = 1.0 + gm1
        o["kappa_match"] = match
        o["kappa"] = 1.0 + gm1 if match >= gate else None


# ------------------------------------------------------------------------------------------------ contrasts
def lnr(a, b):
    return math.log(a / b) if a and b and a > 0 and b > 0 else None


def pair_contrast(blk, A, B, beta=None):
    n = by_name(blk)
    if A not in n or B not in n or not usable(blk):
        return None
    a, b = n[A][0]["obs"], n[B][0]["obs"]
    if a.get("ln_t66_c") is None or b.get("ln_t66_c") is None:
        return None
    L = a["ln_t66_c"] - b["ln_t66_c"]
    c = {"L": L, "censored": [a["censored"], b["censored"]],
         "L_P": (L + lnr(a.get("sw_W"), b.get("sw_W"))) if lnr(a.get("sw_W"), b.get("sw_W")) is not None else None,
         "L_ops": (L + lnr(a.get("ops_rate"), b.get("ops_rate"))) if lnr(a.get("ops_rate"), b.get("ops_rate")) is not None else None,
         "kappa": (a["kappa"] - b["kappa"]) if a.get("kappa") is not None and b.get("kappa") is not None else None,
         "dhot": (a["dhot"] - b["dhot"]) if a.get("dhot") is not None and b.get("dhot") is not None else None,
         "iota_io": (a["iota_io"] - b["iota_io"]) if a.get("iota_io") is not None and b.get("iota_io") is not None else None,
         "power_w": (a["sw_W"] - b["sw_W"]) if a.get("sw_W") is not None and b.get("sw_W") is not None else None,
         "work": lnr(a.get("ops_rate"), b.get("ops_rate")),
         "ln_tauc": lnr(a.get("tau_c_s"), b.get("tau_c_s"))}
    c["L_adj"] = (L - beta * c["ln_tauc"]) if beta is not None and c["ln_tauc"] is not None else None
    return c


def special_value(blk, kind):
    n = by_name(blk)
    if not usable(blk):
        return None
    g = lambda name, key: n[name][0]["obs"].get(key) if name in n else None
    if kind == "lin":
        kU, kI, kP = g("UNI32@16", "kappa"), g("INT16@16", "kappa"), g("PER16@16", "kappa")
        pI, pP = g("INT16@16", "sw_W"), g("PER16@16", "sw_W")
        if None in (kU, kI, kP, pI, pP) or pI + pP <= 0:
            return None
        return kU - (pI * kI + pP * kP) / (pI + pP)
    if kind in ("conc", "conc_l"):
        name = "UNI32@16"
        a, b, u = g("INT16@32", "dhot"), g("PER16@32", "dhot"), g(name, "dhot")
        return None if None in (a, b, u) else 0.5 * (a + b) - u
    if kind == "map":
        ne = [x["obs"].get("iota_io") for x in n.get("B4NE", []) if x["obs"].get("iota_io") is not None]
        sw = [x["obs"].get("iota_io") for x in n.get("B4SW", []) if x["obs"].get("iota_io") is not None]
        return mean(ne) - mean(sw) if ne and sw else None
    if kind == "intra":
        kU, kI, kP = g("UNI32@16", "kappa"), g("INT16@32", "kappa"), g("PER16@32", "kappa")
        return None if None in (kU, kI, kP) else kU - 0.5 * (kI + kP)
    return None


def sign_count(blocks, A, B):
    """Sign count over blocks: censored runs ranked longest, two censored runs tied (dropped)."""
    pos = neg = ties = 0
    for blk in blocks:
        n = by_name(blk)
        if A not in n or B not in n or not usable(blk):
            continue
        a, b = n[A][0]["obs"], n[B][0]["obs"]
        if a.get("t66_c") is None or b.get("t66_c") is None:
            continue
        ca, cb = a["censored"], b["censored"]
        if ca and cb:
            ties += 1; continue
        if ca:
            pos += 1; continue
        if cb:
            neg += 1; continue
        d = a["t66_c"] - b["t66_c"]
        pos += d > 0; neg += d < 0; ties += d == 0
    n = pos + neg
    return {"A_longer": pos, "B_longer": neg, "ties": ties, "p_two_sided": H.binom_two_sided(min(pos, neg), n) if n else None}


def place_mean(blk, name, key):
    """The mean of a placement's kept runs' observable in a block (B4NE/B4SW have 2 repeats)."""
    v = [x["obs"].get(key) for x in by_name(blk).get(name, []) if x["obs"].get(key) is not None]
    return mean(v) if v else None


def power_work(blocks, A, B):
    """Per usable block: POWER = sw_W_A - sw_W_B (B a tuple: their sum), WORK = ln(ops_A / ops_B) (B a tuple: the mean
    of their per-minion rates)."""
    pw, wk = [], []
    for blk in blocks:
        if not usable(blk):
            continue
        Bs = B if isinstance(B, tuple) else (B,)
        a_w, a_o = place_mean(blk, A, "sw_W"), place_mean(blk, A, "ops_rate")
        b_w = [place_mean(blk, x, "sw_W") for x in Bs]
        b_o = [place_mean(blk, x, "ops_rate") for x in Bs]
        if a_w is not None and None not in b_w:
            pw.append(a_w - sum(b_w))
        if a_o and None not in b_o and all(b_o):
            wk.append(math.log(a_o / mean(b_o)))
    return pw, wk


def pair_label(pair):
    A, B = pair
    return "%s-%s" % (A, "+".join(B) if isinstance(B, tuple) else B)


def run_level_resid_sd(blocks, stat, names):
    """s_run: the residual SD of a run-level statistic after an additive block + placement fit (DESIGN2 §2.4 P1)."""
    rows = []
    for bi, blk in enumerate(blocks):
        if not usable(blk):
            continue
        for name, lst in by_name(blk).items():
            if name not in names:
                continue
            v = lst[0]["obs"].get(stat)
            if v is not None:
                rows.append((bi, name, v))
    if len(rows) < 4:
        return None, len(rows)
    # alternating means (balanced or nearly): iterate block and placement effects
    bl = {b: 0.0 for b, _, _ in rows}
    pl = {p: 0.0 for _, p, _ in rows}
    mu = mean([v for _, _, v in rows])
    for _ in range(50):
        for p in pl:
            vs = [v - mu - bl[b] for b, q, v in rows if q == p]
            pl[p] = mean(vs)
        for b in bl:
            vs = [v - mu - pl[p] for c, p, v in rows if c == b]
            bl[b] = mean(vs)
    res = [v - mu - bl[b] - pl[p] for b, p, v in rows]
    df = len(rows) - len(bl) - len(pl) + 1
    if df <= 0:
        return None, len(rows)
    return math.sqrt(sum(r * r for r in res) / df), len(rows)


STAT_OF = {"L": "ln_t66_c", "kappa": "kappa", "dhot": "dhot", "iota_io": "iota_io"}


def item_values(blocks, item, beta=None, primary="L"):
    """Per-block values of an item (list), from the blocks of its type."""
    out = []
    iid, typ = item[0], item[1]
    for blk in blocks:
        if blk["type"] != typ:
            continue
        if isinstance(item[2], tuple):
            c = pair_contrast(blk, item[2][0], item[2][1], beta)
            if c is None:
                continue
            key = item[3]
            if key == "L" and primary == "L_adj":
                key = "L_adj"
            v = c.get(key)
        else:
            v = special_value(blk, item[2])
        if v is not None:
            out.append((blk["pass"], v))
    return out


def summarise(blocks, card, beta=None, primary=None):
    """Every item (registrable, special, reported-only) with its per-block values and 99% CI, REPORTED."""
    P = blocks[0]["params"] if blocks else H.DEFAULTS
    res = {}
    for it in PAIR_ITEMS:
        vals = item_values(blocks, it, beta, (primary or {}).get(it[0], "L"))
        c = ci99([v for _, v in vals])
        r = {"type": it[1], "pair": list(it[2]), "stat": it[3], "band": P[it[4]], "n_blocks": len(vals),
             "values": vals, "ci99": c}
        if it[3] == "L":
            r["sign_count"] = sign_count([b for b in blocks if b["type"] == it[1]], *it[2])
            for k in ("L_P", "L_ops", "L_adj", "power_w", "work", "kappa", "dhot", "iota_io"):
                vv = []
                for blk in blocks:
                    if blk["type"] == it[1]:
                        cc = pair_contrast(blk, it[2][0], it[2][1], beta)
                        if cc and cc.get(k) is not None:
                            vv.append(cc[k])
                r[k] = ci99(vv) or ({"values": vv} if vv else None)
        res[it[0]] = r
    for iid, typ, kind, bandk, pred in SPECIAL_ITEMS:
        vals = item_values(blocks, (iid, typ, kind))
        res[iid] = {"type": typ, "stat": kind, "band": P[bandk], "fixed_prediction": pred, "n_blocks": len(vals),
                    "values": vals, "ci99": ci99([v for _, v in vals])}
    for it in REPORTED_ONLY:
        vals = item_values(blocks, it)
        res[it[0]] = {"type": it[1], "reported_only": True, "n_blocks": len(vals), "values": vals,
                      "ci99": ci99([v for _, v in vals])}
    # gradient leakage (§4.2): corrected PLACE-t, approximate
    ew, ns, pt = (res.get(k, {}).get("ci99") for k in ("GRAD-EW", "GRAD-NS", "PLACE-t"))
    if ew and ns and pt:
        gc, gr = ew["mean"] / 3.25, -ns["mean"] / 2.0
        res["PLACE-t"]["gradient_corrected_mean"] = pt["mean"] - (0.31 * gr - 0.31 * gc)
        res["PLACE-t"]["gradient_correction_note"] = "approximate: G8 runs at 256 minions, L16 at 512 (DESIGN2 §4.2)"
    return res


# ------------------------------------------------------------------------------------------------ power steps
def projected(s, P, est, band, ptype):
    """The smallest n in [n_min, n_max] with h(n) <= reg_factor x band (EQUIV) or x |estimate| (SIGN, NONZERO)."""
    target = P["reg_factor"] * (band if ptype == "EQUIV" else abs(est))
    for n in range(P["n_min"], P["n_max"] + 1):
        h = H.projected_half(s, n)
        if h is not None and h <= target:
            return n, h, target
    return None, H.projected_half(s, P["n_max"]), target


def p1(blocks, card):
    """DESIGN2 §2.4 P1 and §5.3 D-S, D-L16, D-L8 on the R1 blocks. Every edge and run parameter is the one each block
    recorded (require_records); the current params-r1 file gives only the power step's n_max and reg_factor."""
    r1 = [b for b in blocks if b["round"] == "r1" and b["type"] in ("S", "L16", "SCOUT")]
    require_records(r1, "P1")
    P = H.resolve_params("r1", card)
    out = {"card": card, "round": "r1", "blocks": [b["pass"] for b in r1], "items": {}, "decisions": {},
           "block_edges": {str(b["pass"]): b["edge"] for b in r1}, "notes": [],
           "power_params": {"n_max": P["n_max"], "reg_factor": P["reg_factor"], "from": P["_params_source"]}}
    summ = summarise([b for b in r1 if b["type"] in ("S", "L16")], card)
    for it in PAIR_ITEMS + [(i, t, k, None, bk, p) for i, t, k, bk, p in SPECIAL_ITEMS]:
        iid, typ = it[0], it[1]
        if typ not in ("S", "L16"):
            continue
        blks = [b for b in r1 if b["type"] == typ]
        # P1's s_run is over "all R1 runs with identical parameters" (§2.4): one parameter key per item, or refuse
        edges = one_key([b for b in blks if usable(b)], "item %s (R1 %s blocks)" % (iid, typ), "P1")
        stat = STAT_OF.get(it[3]) if isinstance(it[2], tuple) else None
        names = set(it[2]) if isinstance(it[2], tuple) else set(H.BLOCK_SETS[typ])
        if stat:
            s_run, nrow = run_level_resid_sd(blks, stat, names)
            s = math.sqrt(2) * s_run if s_run is not None else None
        else:
            v = [x for _, x in summ[iid]["values"]]
            s = sd(v)
            nrow = len(v)
        c = summ[iid]["ci99"]
        est = c["mean"] if c else None
        band = summ[iid]["band"]
        reach = None
        if s is not None:
            h_max = H.projected_half(s, P["n_max"])
            reach = h_max <= P["reg_factor"] * max(band, abs(est) if est is not None else 0)
        out["items"][iid] = {"s": s, "rows": nrow, "estimate": est, "band": band,
                             "h_at_n_max": H.projected_half(s, P["n_max"]) if s else None, "reachable": reach,
                             "edges": edges}
    for typ in ("S", "L16"):
        its = [k for k, v in out["items"].items() if (dict((i[0], i[1]) for i in PAIR_ITEMS + [(x[0], x[1]) for x in SPECIAL_ITEMS])[k] == typ)]
        ok = [out["items"][k]["reachable"] for k in its]
        out["decisions"]["keep_" + typ] = any(ok) if any(o is not None for o in ok) else None
        if typ == "L16" and out["decisions"]["keep_L16"] is not True:
            out["decisions"]["keep_L16"] = True
            out["decisions"]["L16_note"] = ("no L16 item reaches the power rule at n_max, but L16 is never dropped "
                                            "(DESIGN2 §8): its items would be reported, not tested; the Q2 number is "
                                            "reported whatever is registered (§10)")
    # D-S: Tier S t66 stays a candidate only if <= 5% of INT16 and PER16 Tier S runs are censored at 7 s
    out["decisions"]["D-S"] = d_s(r1)
    # D-L16 (scouting 1601): UNI32@16 median t66 in 40-100 s, <= 5% censored; S_L moves from the edge the scouting
    # runs RAN at (their block's record), never from the current params file
    scb = [(b, x) for b in r1 if b["type"] == "SCOUT" and b["k"] == 1 for x in kept_runs(b).values()
           if x["rec"]["name"] == "UNI32@16"]
    sc = [x["obs"] for _, x in scb]
    med = median([o["t66_s"] for o in sc if not o["censored"]])
    anyc = any(o["censored"] for o in sc)
    S_L, ran = ran_at([b for b, _ in scb], "D-L16 (the UNI32@16 scouting runs)")
    if not sc:
        d = {"S_L": None, "why": "no scouting data: no decision (the current params file is not an edge any block ran at)"}
    elif anyc or (med is not None and med > 100):
        d = {"S_L": min(62, S_L + 1), "why": "median %s s or censored: raise by 1" % med}
    elif med is not None and med < 40:
        d = {"S_L": max(59, S_L - 1), "why": "median %s s < 40: lower by 1" % med}
    else:
        d = {"S_L": S_L, "why": "median %s s in 40-100" % med}
    out["decisions"]["D-L16"] = dict(d, ran_at=S_L, blocks=ran)
    # D-L8 (scouting 1602): CEN8 median t66 in 40-100 s with no censored scouting run, within 61-64
    # CEN8's median t66 (§5.3); "no censored scouting run" covers every measured run of the L8 scouting block. S_L8
    # (and "censored at S_L8 = 64") is the edge the scouting runs RAN at, as their block recorded it
    sc8b = [(b, x) for b in r1 if b["type"] == "SCOUT" and b["k"] == 2 for x in kept_runs(b).values()]
    sc8 = [x["obs"] for _, x in sc8b]
    med8 = median([o["t66_s"] for o in sc8 if o.get("name") == "CEN8" and o.get("t66_s") is not None and not o["censored"]])
    anyc8 = any(o["censored"] for o in sc8)
    S_L8, ran8 = ran_at([b for b, _ in sc8b], "D-L8 (the L8 scouting runs)")
    if not sc8:
        d8 = {"S_L8": None, "keep_L8_G8": None,
              "why": "no scouting data: no decision (the current params file is not an edge any block ran at)"}
    elif anyc8 and S_L8 >= 64:
        d8 = {"S_L8": S_L8, "keep_L8_G8": False, "why": "censored at S_L8 = 64: L8 and G8 dropped"}
    elif anyc8 or (med8 is not None and med8 > 100):
        d8 = {"S_L8": min(64, S_L8 + 1), "keep_L8_G8": True, "why": "median %s s or censored: raise by 1" % med8}
    elif med8 is not None and med8 < 40:
        d8 = {"S_L8": max(61, S_L8 - 1), "keep_L8_G8": True, "why": "median %s s < 40: lower by 1" % med8}
    else:
        d8 = {"S_L8": S_L8, "keep_L8_G8": True, "why": "median %s s in 40-100" % med8}
    d8["G0_note"] = "G0 (the Foster fit of the V3-IDLE curves) is not implemented here; its steady-state flag must be checked by hand"
    d8.update(ran_at=S_L8, blocks=ran8)
    out["decisions"]["D-L8"] = d8
    # the current params-r1 is only reported: after D-L16/D-L8 it holds R1c's edges, not the scouting runs'
    for key, e, dd in (("S_L", S_L, "D-L16"), ("S_L8", S_L8, "D-L8")):
        if e is not None and P.get(key) != e:
            out["notes"].append("%s gives %s %s now; %s used the edge its scouting block(s) ran at, %s %s (p%s)" % (
                P["_params_source"], key, P.get(key), dd, key, e, ", p".join(str(p) for p in out["decisions"][dd]["blocks"])))
    return out


def ran_at(blks, what):
    """(the one start edge the blocks recorded, their passes) for a D-rule (§5.3); (None, []) without blocks. Scouting
    runs at two edges are refused: the rule moves the edge they ran at, so there must be exactly one."""
    blks = sorted({id(b): b for b in blks}.values(), key=lambda b: b["pass"])
    if not blks:
        return None, []
    e = one_key(blks, what, "P1")
    return blks[0]["edge"], sorted(p for ps in e.values() for p in ps)


def d_s(r1_blocks, who="P1"):
    """D-S (§5.3): PLACE-tS stays a candidate only if <= 5% of the R1 Tier S INT16/PER16 runs are censored at 7 s. The
    runs' blocks must share one start edge and parameter key (one_key); the edges are reported."""
    srb = [(b, x) for b in r1_blocks if b["type"] in ("S", "SCOUT") and b["round"] == "r1" for x in kept_runs(b).values()
           if x["obs"].get("tier") == "S" and x["rec"]["name"] in ("INT16@32", "PER16@32")]
    sr = [x["obs"] for _, x in srb]
    blks = list({id(b): b for b, _ in srb}.values())
    edges = one_key(blks, "D-S (the R1 Tier S INT16/PER16 runs)", who) if blks else {}
    frac = (sum(o["censored"] for o in sr) / len(sr)) if sr else None
    return {"censored_fraction": frac, "runs": len(sr), "PLACE-tS_candidate": frac is not None and frac <= 0.05,
            "edges": edges}


def beta_fit(blocks):
    """beta: the pooled within-block slope of ln min(t66, C) on ln tau_c over the Tier L measured runs (placement
    effects removed too)."""
    xs, ys = [], []
    for blk in blocks:
        if blk["type"] not in ("L16", "L8", "G8") or not usable(blk):
            continue
        pts = [(math.log(x["obs"]["tau_c_s"]), x["obs"]["ln_t66_c"], x["rec"]["name"]) for x in kept_runs(blk).values()
               if x["obs"].get("tau_c_s") and x["obs"]["tau_c_s"] > 0 and x["obs"].get("ln_t66_c") is not None]
        if len(pts) < 2:
            continue
        mx, my = mean([p[0] for p in pts]), mean([p[1] for p in pts])
        xs += [p[0] - mx for p in pts]; ys += [p[1] - my for p in pts]
    sxx = sum(x * x for x in xs)
    return (sum(x * y for x, y in zip(xs, ys)) / sxx) if sxx > 0 else None


def cv_cal(runs):
    """The run-level SD of ln t66 (censored runs at C) of CAL chains (§2.4, §6.1)."""
    v = [math.log(o["t66_c"]) for o in runs if o.get("t66_c")]
    return sd(v), len(v)


def p3(blocks, card, card1=None, allow_no_card1=False):
    """DESIGN2 §2.4 P3: the registration rule, beta, the primary, n_val per type (step 5) and every registered item
    re-checked at its type's n_val (step 4); the card-1 budget (§8).
    card1: {'data': card-1 data dir, 'blocks': its V0 blocks} for CV_card1 (V0's chains at the settled S_L edge).
    Every edge and run parameter is the one each block recorded (require_records): aifoundry3's frozen S_L is the edge
    its R3 L16 blocks ran at, V0's rule runs on the params the V0 blocks recorded, and an item pools only blocks with
    one parameter key (one_key). The current params-r3 file gives only the bands, n_min, n_max and reg_factor."""
    P = H.resolve_params("r3", card)
    dev = [b for b in blocks if b["round"] in ("r1", "r2", "r3") and b["type"] in ("S", "L16", "L8", "G8", "SCOUT")]
    require_records(dev, "P3")
    r3 = [b for b in dev if b["round"] == "r3"]
    beta = beta_fit(dev)
    out = {"card": card, "beta": beta, "items": {}, "n_val": {}, "types_kept": [], "notes": [],
           "power_params": {"n_min": P["n_min"], "n_max": P["n_max"], "reg_factor": P["reg_factor"],
                            "from": P["_params_source"]},
           # beta is the pooled WITHIN-block slope over development (§2.2): block effects drop out, so it pools edges
           "beta_edges": {t: edges_of([b for b in dev if b["type"] == t and usable(b)]) for t in ("L16", "L8", "G8")}}
    # CV ratio (§2.4): aifoundry3's tier-L CAL chains of its R3 L16 blocks at the frozen S_L, i.e. the ONE edge those
    # blocks recorded (not params-r3's S_L now); card 1's V0 chains at the edge V0 settled on (review F5)
    r3l16 = [b for b in r3 if b["type"] == "L16" and not b["void"]]
    s_l = None
    if r3l16:
        one_key(r3l16, "CV_a3 (aifoundry3's R3 L16 CAL chains)", "P3")
        s_l = r3l16[0]["edge"]
        if P.get("S_L") != s_l:
            out["notes"].append("%s gives S_L %s now; the R3 L16 blocks ran at S_L %s, which P3 uses" % (
                P["_params_source"], P.get("S_L"), s_l))
    a3 = [x["obs"] for b in r3l16 for x in b["runs"]
          if x["rec"].get("role") == "cal" and x["rec"].get("name") == "ALL24" and x["rec"].get("tier") == "L"
          and b["edge"] == s_l and not x["obs"]["void"]]
    cv_a3, n_a3 = cv_cal(a3)
    cv_c1 = n_c1 = v0 = None
    if card1:
        v0b = sorted([b for b in card1["blocks"] if b["type"] == "CAL"], key=lambda b: b["pass"])
        require_records(v0b, "P3")
        Pv0 = v0_recorded_params(v0b)
        if Pv0 is None:
            v0 = {"why": "no finished V0 block in %s" % card1["data"]}
        else:
            v0 = H.v0_edge(card1["data"], "aifoundry1-c1", "L", Pv0)
            fp = v0.get("final_pass")
            fb = [b for b in v0b if b["pass"] == fp]
            if fb and fb[0]["edge"] != v0.get("final"):
                raise SystemExit("P3 refused: V0 settled at edge %s, but its block p%s recorded edge %s" % (
                    v0.get("final"), fp, fb[0]["edge"]))
            c1 = [x["obs"] for b in fb for x in b["runs"]
                  if x["rec"].get("role") == "meas" and x["rec"].get("name") == "ALL24" and not x["obs"]["void"]]
            cv_c1, n_c1 = cv_cal(c1)
            cur = H.resolve_params("v0", "aifoundry1-c1")
            chg = [k for k in V0_RULE_KEYS if cur.get(k) != Pv0.get(k)]
            if chg:
                out["notes"].append("%s differs now from what the V0 blocks ran with (%s); P3 uses the V0 blocks' own "
                                    "record" % (cur["_params_source"], ", ".join("%s %s -> %s" % (k, Pv0.get(k), cur.get(k))
                                                                                for k in chg)))
    if cv_c1 is None or not cv_a3:
        if not allow_no_card1:
            raise SystemExit("P3 refused: CV_card1 needs card 1's V0 chains at the settled S_L edge (--cal-card1 <card-1 "
                             "data dir>; V0 settled: %s) and CV_a3 aifoundry3's R3 L16 CAL chains at the S_L they "
                             "recorded, %s (%d runs); --allow-no-card1 uses ratio 1 and says so" % (
                                 v0 and v0.get("why"), s_l, n_a3))
        ratio = 1.0
        out["notes"].append("CV ratio NOT AVAILABLE (card-1 V0 data %s): ratio 1 used, card-1 intervals NOT inflated "
                            "(--allow-no-card1)" % ("missing" if cv_c1 is None else "present, aifoundry3's CAL missing"))
    else:
        ratio = max(1.0, cv_c1 / cv_a3)
    out["cv"] = {"aifoundry3": cv_a3, "aifoundry3_runs": n_a3, "aifoundry3_what": "R3 L16 CAL chains at S_L=%s" % s_l,
                 "aifoundry3_edge": s_l, "aifoundry3_blocks": sorted(b["pass"] for b in r3l16),
                 "card1": cv_c1, "card1_runs": n_c1,
                 "card1_what": "V0 chains at the settled edge %s (pass %s)" % (v0 and v0.get("final"), v0 and v0.get("final_pass")),
                 "card1_edges": edges_of(card1["blocks"]) if card1 else None,
                 "ratio_used": ratio}
    keys = {same_params_key(b) for b in r3}
    pool = [b for b in dev if same_params_key(b) in keys]
    out["pooled_blocks"] = sorted(b["pass"] for b in pool)
    ds = d_s([b for b in dev if b["round"] == "r1"], "P3")
    out["D-S"] = ds
    prim = {}
    items = PAIR_ITEMS + [(i, t, k, None, bk, p) for i, t, k, bk, p in SPECIAL_ITEMS]
    for it in items:
        iid, typ, pair, stat, bandk, fixed = it
        blks = [b for b in pool if b["type"] == typ]
        # "pooled over R1-R3 blocks with identical parameters" (§2.4, §5.4): one key per item, or refuse
        edges = one_key([b for b in blks if usable(b)], "item %s (R1-R3 %s blocks)" % (iid, typ), "P3")
        cands = {}
        for pr in (["L", "L_adj"] if stat == "L" else [None]):
            vals = [v for _, v in item_values(blks, it if isinstance(pair, tuple) else (iid, typ, pair), beta, pr or "L")]
            s_blk = sd(vals)
            if isinstance(pair, tuple):
                s_run, _ = run_level_resid_sd(blks, STAT_OF.get(stat, "ln_t66_c"), set(pair))
                s2 = math.sqrt(2) * s_run if s_run is not None else None
            else:
                s2 = None
            s = max([x for x in (s_blk, s2) if x is not None], default=None)
            if s is not None and len(vals) < 6 and s2 is not None:
                s = s2 if s_blk is None else max(s_blk, s2)
            cands[pr or "L"] = (vals, s)
        if stat == "L" and cands.get("L_adj", ([], None))[1] is not None and cands["L"][1] is not None and \
                cands["L_adj"][1] < cands["L"][1]:
            choice = "L_adj"
        else:
            choice = "L"
        prim[iid] = choice
        vals, s = cands[choice]
        c = ci99(vals)
        band = P[bandk]
        rec = {"type": typ, "primary": choice if stat == "L" else stat, "dev_ci99": c, "s": s,
               "s_card1": s * ratio if s is not None else None, "band": band, "n_dev_blocks": len(vals), "edges": edges}
        if c is None or c["n"] < 3:
            rec.update(candidate=False, registered=False, reason="fewer than 3 development blocks")
        elif iid == "PLACE-tS" and not ds.get("PLACE-tS_candidate"):
            rec.update(candidate=False, registered=False,
                       reason="D-S: %s of the R1 Tier S INT16/PER16 runs censored at 7 s (> 5%% or no data)" % ds.get("censored_fraction"))
        else:
            # the candidate type (§2.4 steps 1-2) with the precedence of README departure 18: a CI wholly inside the
            # band is EQUIV (negligible) even if it also excludes 0
            inside = -band < c["lo"] and c["hi"] < band
            if inside:
                ptype = "EQUIV"
            elif c["lo"] > 0 or c["hi"] < 0:
                ptype = "NONZERO" if fixed == "NONZERO" else ("SIGN+" if c["lo"] > 0 else "SIGN-")
            else:
                ptype = None
            if fixed in ("SIGN+", "EQUIV") and ptype != fixed:
                rec.update(candidate=False, registered=False,
                           reason="development does not support the fixed prediction %s (got %s)" % (fixed, ptype))
            elif ptype is None:
                rec.update(candidate=False, registered=False,
                           reason="direction: the development CI neither excludes 0 nor lies inside the band")
            else:
                n, h, target = projected(rec["s_card1"], P, c["mean"], band, ptype)
                rec.update(candidate=True, prediction=ptype, projected_n=n, projected_h=h, target_h=target)
        out["items"][iid] = rec
    # §2.4 step 5: n_val per type (choose_n_val: L16 by its primary PLACE-t; S, L8, G8 by the first candidate to reach
    # step 4). Step 4 is then re-checked for every candidate of the type AT n_val (review F4).
    out["n_val_rule"] = {}
    for typ in PRIORITY:
        its = {k: v for k, v in out["items"].items() if v["type"] == typ}
        if not any(v.get("candidate") for v in its.values()):
            for k, v in its.items():
                v.setdefault("registered", False)
            continue
        n_val, rule, note = choose_n_val(typ, its, P)
        out["n_val_rule"][typ] = rule
        if note:
            out["notes"].append(note)
        out["n_val"][typ] = n_val
        for k, v in its.items():
            if not v.get("candidate"):
                v["registered"] = False
                continue
            h = H.projected_half(v["s_card1"], n_val)
            v["h_at_n_val"] = h
            if h is not None and h <= v["target_h"]:
                v["registered"] = True
                v.pop("reason", None)
            else:
                v["registered"] = False
                v["reason"] = ("power at n_val = %d: h = %.3g > 0.7 x %s = %.3g"
                               % (n_val, h if h is not None else float("nan"),
                                  "band" if v["prediction"] == "EQUIV" else "|estimate|", v["target_h"]))
        if any(v.get("registered") for v in its.values()):
            out["types_kept"].append(typ)
        else:
            out["n_val"].pop(typ, None)
            out["notes"].append("type %s dropped: no item registered at its n_val" % typ)
    # the card-1 cap (§8): drop types in reverse priority (G8, S, L8; never L16)
    def total():
        return sum(out["n_val"][t] * BLOCK_MIN_CARD1[t] for t in out["types_kept"])
    for t in ("G8", "S", "L8"):
        if total() <= CARD1_CAP_MIN:
            break
        if t in out["types_kept"]:
            out["types_kept"].remove(t); out["n_val"].pop(t, None)
            out["notes"].append("type %s dropped for the card-1 cap (%d min)" % (t, CARD1_CAP_MIN))
            for k, v in out["items"].items():
                if v["type"] == t and v.get("registered"):
                    v.update(registered=False, reason="type dropped for the card-1 time cap")
    for k, v in out["items"].items():
        if v.get("registered"):
            v["power_work_pairs"] = [pair_label(pp) for pp in POWER_WORK_PAIRS.get(k, [])]
            v["power_waived_pairs"] = [pair_label(pp) for pp in POWER_WORK_PAIRS.get(k, []) if power_waived(v["type"], pp)]
    out["card1_minutes"] = total()
    out["primary"] = prim
    return out


# the inputs of V0's edge rule (hplib.v0_edge): P3 takes them from the V0 blocks' own plan.json, as they ran
V0_RULE_KEYS = ("S_L", "S_L8", "L8_offset", "T_cal_s") + RUN_PARAM_KEYS


def v0_recorded_params(v0b):
    """The params card 1's V0 blocks recorded (plan.json), for re-running V0's rule as it ran; None without blocks.
    Refuses (exit) if the blocks recorded different rule inputs (params-v0 edited between V0 blocks)."""
    if not v0b:
        return None
    seen = {}
    for b in v0b:
        seen.setdefault(json.dumps([b["params"].get(k) for k in V0_RULE_KEYS], sort_keys=True), []).append(b["pass"])
    if len(seen) > 1:
        raise SystemExit("P3 refused: card 1's V0 blocks recorded different V0 parameters (%s): %s" % (
            ", ".join(V0_RULE_KEYS), "; ".join("%s: p%s" % (k, ", p".join(map(str, v))) for k, v in seen.items())))
    return dict(v0b[0]["params"])


def choose_n_val(typ, its, P):
    """§2.4 step 5 for one block type: (n_val, rule, note). L16: the smallest n in [n_min, n_max] meeting step 4 for its
    primary item PLACE-t, else n_min. S, L8, G8 (no primary item in DESIGN2): the smallest n meeting step 4 for any
    candidate of the type (the smallest projected n), else n_min. its: {item: P3 record with candidate, projected_n}."""
    pi = PRIMARY_OF_TYPE.get(typ)
    if pi:
        pn = its.get(pi, {}).get("projected_n") if its.get(pi, {}).get("candidate") else None
        rule = "primary %s" % pi
        if pn is None:
            return P["n_min"], rule, ("type %s: its primary item %s cannot reach step 4 by n_max = %d: n_val = %d (§2.4 "
                                      "step 5)" % (typ, pi, P["n_max"], P["n_min"]))
        return pn, rule, None
    reach = sorted((v["projected_n"], k) for k, v in its.items() if v.get("candidate") and v.get("projected_n") is not None)
    if not reach:
        return P["n_min"], "first candidate to reach step 4", ("type %s: no candidate reaches step 4 by n_max = %d: "
                                                                "n_val = %d (§2.4 step 5)" % (typ, P["n_max"], P["n_min"]))
    return reach[0][0], "first candidate to reach step 4 (%s)" % reach[0][1], None


def h11_word(words):
    """H11 (transfer: every registered SIGN item holds on card 1): FAIL as soon as one SIGN item FAILs, else
    INSUFFICIENT if one is INSUFFICIENT, else PASS (review low: [FAIL, INSUFFICIENT] read INSUFFICIENT)."""
    if any(w == "FAIL" for w in words):
        return "FAIL"
    if words and all(w == "PASS" for w in words):
        return "PASS"
    return "INSUFFICIENT"


# ------------------------------------------------------------------------------------------------ validation
def select_val_blocks(blocks, prereg):
    """Per type, the first n_val usable blocks in pass order (void or incomplete blocks do not count and are replaced
    by later ones, §4.4); later usable blocks are extra: listed, never used (§6.4, review F10)."""
    n_val = (prereg.get("frozen") or {}).get("n_val") or {}
    used, extra, skipped = [], {}, {}
    for typ in sorted({b["type"] for b in blocks}):
        k = 0
        for b in sorted([b for b in blocks if b["type"] == typ], key=lambda b: b["pass"]):
            if not usable(b):
                skipped.setdefault(typ, []).append({"pass": b["pass"], "void": b["void"], "incomplete": b.get("incomplete")})
            elif k < int(n_val.get(typ, 0)):
                used.append(b); k += 1
            else:
                extra.setdefault(typ, []).append(b["pass"])
    have = {t: sum(1 for b in used if b["type"] == t) for t in n_val}
    return used, {"n_val": n_val, "used": have, "extra_blocks_not_used": extra, "void_or_incomplete": skipped}


def validate(blocks, card, prereg):
    reg = prereg.get("items", {})
    beta = prereg.get("beta")
    prim = prereg.get("primary", {})
    regd = [i for i, r in reg.items() if r.get("registered")]
    mark_incomplete(blocks, regd)
    blocks, counts = select_val_blocks(blocks, prereg)
    summ = summarise(blocks, card, beta, prim)
    out = {"card": card, "items": {}, "blocks": counts,
           "family_size": sum(1 for v in reg.values() if v.get("registered"))}
    sign_items = []

    def word(ptype, vals, band, typ):
        holds, c = outcome(ptype, vals, band)
        need, have = int(counts["n_val"].get(typ, 0)), counts["used"].get(typ, 0)
        if have < need:        # never a verdict from fewer than the frozen n_val blocks (no optional stopping)
            return {"holds": None, "ci99": c, "outcome": "INSUFFICIENT",
                    "reason": "%d of the frozen n_val = %d usable %s blocks" % (have, need, typ)}
        return {"holds": holds, "ci99": c, "outcome": H.card_verdicts({card: holds}, [card])}
    for iid, r in reg.items():
        s = summ.get(iid)
        if not r.get("registered"):
            out["items"][iid] = {"outcome": "reported, not tested", "reason": r.get("reason"), "value": s and s.get("ci99")}
            continue
        vals = [v for _, v in (s or {}).get("values", [])]
        out["items"][iid] = dict(word(r["prediction"], vals, r["band"], r["type"]), prediction=r["prediction"],
                                 band=r["band"], primary=prim.get(iid))
        if r["prediction"].startswith("SIGN"):
            sign_items.append(iid)
        # POWER and WORK on every pair of a registered item (§2.4 step 6; CONC, MAP and LIN included)
        tb = [b for b in blocks if b["type"] == r["type"]]
        for pp in POWER_WORK_PAIRS.get(iid, []):
            pw, wk = power_work(tb, *pp)
            lab = "" if iid in dict((i[0], 1) for i in PAIR_ITEMS) else " " + pair_label(pp)
            if power_waived(r["type"], pp):      # README departure 37: no sw_W window; the same pair in Tier L, reported
                pwl, _ = power_work([b for b in blocks if b["type"] == "L16"], *pp)
                out["items"][iid + "/POWER" + lab] = {
                    "outcome": POWER_WAIVED_WORD, "prediction": "EQUIV", "band": H.DEFAULTS["band_power_w"],
                    "holds": None, "ci99": ci99(pw), "tier_L_ci99": ci99(pwl), "tier_L_blocks": len(pwl),
                    "reason": "Tier S sw_W window (t0 + 1 s .. t0 + t66) is empty for INT16@32 (crosses 66 C in < 1 s); "
                              "waived in PREREG (README departure 37); tier_L_ci99: the same pair in this card's L16 "
                              "blocks, reported"}
            else:
                out["items"][iid + "/POWER" + lab] = dict(word("EQUIV", pw, H.DEFAULTS["band_power_w"], r["type"]),
                                                          prediction="EQUIV", band=H.DEFAULTS["band_power_w"])
            wkr = word("EQUIV", wk, H.DEFAULTS["band_work"], r["type"])
            out["items"][iid + "/WORK" + lab] = dict(wkr, prediction="EQUIV", band=H.DEFAULTS["band_work"])
            if wkr["holds"] is False:
                out["items"][iid]["note"] = "WORK failed: decide on L_ops (DESIGN2 §4.5)"
    if sign_items:
        ws = [out["items"][i]["outcome"] for i in sign_items]
        out["items"]["H11"] = {"outcome": h11_word(ws), "of": sign_items, "words": ws}
    else:
        out["items"]["H11"] = {"outcome": "not tested", "reason": "no SIGN item registered (DESIGN2 §4.1)"}
    out["items"]["TRIG-A"] = {"outcome": "not tested (waived in PREREG)",
                              "reason": (prereg.get("trig_a_card1") or {}).get("waiver") or
                              "no card-1 clock-step protocol in this implementation (README departure 19)"}
    return out


def val_lock(prereg_path, vblocks, amendment=None):
    """reduce.py --val's lock (review F1): PREREG.md against PREREG.sha256; the prereg.json given is the one PREREG.md
    locks; every locked file unchanged (a changed file only with --amendment, recorded); every validation block ran
    under this PREREG (its prereg-lock.json), with the locked binaries (binaries.json) and the locked code
    (code.sha256). Returns (ok, why, record)."""
    pdir = os.path.dirname(os.path.abspath(prereg_path))
    canon = os.path.join(HERE, "prereg")
    if not H.dry() and os.path.abspath(pdir) != canon:
        return False, "--prereg must be %s/prereg.json on a real reduction (another PREREG only under V3_DRY)" % H.rel(canon), None
    ok, why, mdh = H.md_and_sha(os.path.join(pdir, "PREREG.md"), os.path.join(pdir, "PREREG.sha256"))
    if not ok:
        return False, why, None
    lock = H.parse_lock(os.path.join(pdir, "PREREG.md"))
    bad, amended = [], []
    if lock.get("prereg_json") != H.rel(prereg_path):
        bad.append("%s is not the prereg.json PREREG.md locks (%s)" % (H.rel(prereg_path), lock.get("prereg_json")))
    for rp, h in sorted((lock.get("files") or {}).items()):
        p = os.path.join(ROOT, rp)
        if os.path.isfile(p) and H.sha256(p) == h:
            continue
        if amendment and os.path.basename(rp) in REDUCER_FILES:
            amended.append(rp)
        else:
            bad.append("%s %s" % (rp, "changed" if os.path.isfile(p) else "missing"))
    lb = lock.get("binaries") or {}
    for blk in vblocks:
        d = blk["dir"]
        r = H.load_json(os.path.join(d, "prereg-lock.json")) or {}
        if r.get("prereg_md_sha256") != mdh:
            bad.append("block p%s ran under PREREG %s, not %s" % (blk["pass"], str(r.get("prereg_md_sha256"))[:12], mdh[:12]))
        # a block run with V3_FORCE (a re-run into a finished block's directory: DESIGN2 §6.4) is never evidence
        forced = "V3_FORCE" in (r.get("overrides") or [])
        for m in load_jsonl(os.path.join(d, "marks.jsonl")):
            if m.get("ev") == "block_begin" and "V3_FORCE" in str(m.get("overrides") or ""):
                forced = True
        if forced:
            bad.append("block p%s ran with V3_FORCE (a re-run into a finished block's directory)" % blk["pass"])
        bj = H.load_json(os.path.join(d, "binaries.json")) or {}
        for role, ent in lb.items():
            if (bj.get(role) or {}).get("sha256") != ent.get("sha256"):
                bad.append("block p%s ran binary %s with sha256 %s, locked %s" % (
                    blk["pass"], role, str((bj.get(role) or {}).get("sha256"))[:12], str(ent.get("sha256"))[:12]))
        code = {}
        for line in open(os.path.join(d, "code.sha256")) if os.path.exists(os.path.join(d, "code.sha256")) else []:
            f = line.split()
            if len(f) == 2:
                code[f[1]] = f[0]
        for rp, h in (lock.get("files") or {}).items():
            if rp in code and code[rp] != h:
                bad.append("block p%s ran %s with sha256 %s, locked %s" % (blk["pass"], rp, code[rp][:12], h[:12]))
    if bad:
        return False, "; ".join(bad[:12]) + (" (and %d more)" % (len(bad) - 12) if len(bad) > 12 else ""), None
    rec = {"prereg_md_sha256": mdh, "files_locked": len(lock.get("files") or {}), "blocks_checked": len(vblocks)}
    if amended:
        rec["amendment"] = {"file": H.rel(amendment), "sha256": H.sha256(amendment), "changed_reducer_files": amended}
    return True, "PREREG %s holds for %d validation blocks" % (mdh[:12], len(vblocks)), rec


# ------------------------------------------------------------------------------------------------ TRIG-B on a card
def probe_class_of(data):
    """The class of the card's newest R0 probe (pass 8xx), or None."""
    ps = sorted(glob.glob(os.path.join(data, "hp", "p8[0-9][0-9]", "probe.json")))
    return (H.load_json(ps[-1]) or {}).get("class") if ps else None


def trigb_card(data, card, blocks, candidate=False):
    """TRIG-B on a card; candidate: the probe said ALIVE_CANDIDATE (found at WARNING), so the first thermal down event
    must be followed by an idle event or the card is reclassified STUCK (§3.2)."""
    import sptrace_events as SE
    dumps, anchors, samples, runs = [], [], [], []
    for blk in sorted(blocks, key=lambda b: b["pass"]):
        d = blk["dir"]
        if not os.path.exists(os.path.join(d, "sp-idle.bin")):
            continue
        dumps.append(os.path.join(d, "sp-idle.bin"))
        anchors += H.session_anchors(d)
        for x in sorted(blk["runs"], key=lambda x: x["rec"]["idx"]):
            p = os.path.join(d, "sp-%s.bin" % x["rec"]["idx"])
            if os.path.exists(p):
                dumps.append(p)
            samples += [(s["t_ms"], s["temp_c"]["minshire"][0], s["temp_c"]["minshire"][2]) for s in x["tel"]
                        if s.get("t_ms") and (s.get("temp_c") or {}).get("minshire")]
            if x["rec"].get("role") == "meas" and x["obs"].get("t0_ms"):
                runs.append({"idx": "%s/%s" % (blk["pass"], x["rec"]["idx"]), "t0_ms": x["obs"]["t0_ms"],
                             "t_end_ms": x["obs"]["t_end_ms"]})
    if len(dumps) < 2:
        return {"holds": None, "why": "no TRIG-B dumps on %s" % card}
    samples.sort()
    return SE.trigb_evaluate(dumps, sorted(anchors), samples, runs, candidate=candidate)


# ------------------------------------------------------------------------------------------------ CLI
def jdump(o, path):
    s = json.dumps(o, indent=1, default=lambda x: None)
    if path:
        open(path, "w").write(s + "\n")
    else:
        print(s)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check-pass")
    ap.add_argument("--card")
    ap.add_argument("--data", action="append")
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--p1", action="store_true")
    ap.add_argument("--p3", action="store_true")
    ap.add_argument("--val", action="store_true")
    ap.add_argument("--prereg")
    ap.add_argument("--cal-card1")
    ap.add_argument("--allow-no-card1", action="store_true")
    ap.add_argument("--amendment")
    ap.add_argument("--no-kappa", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.check_pass:
        sys.exit(check_pass(a.check_pass, a.card or ""))
    if not a.data or not a.card:
        ap.error("--data and --card are required (or --check-pass)")
    blocks = []
    for d in a.data:
        blocks += load_blocks(d, a.card)
    if not a.no_kappa:
        for b in blocks:
            if b["type"] in ("S", "L16", "L8", "G8"):
                kappa_block(b, a.card)
    base = {"card": a.card, "blocks": [{"pass": b["pass"], "round": b["round"], "type": b["type"], "void": b["void"],
                                         "kappa_network": b.get("kappa_network"), "kappa_note": b.get("kappa_note"),
                                         "runs": [{k: x["obs"].get(k) for k in ("idx", "name", "role", "t66_s", "censored",
                                                                                 "sw_W", "kappa", "dhot", "iota_io",
                                                                                 "tau_c_s", "W_idle", "void", "flags")}
                                                  for x in b["runs"]]} for b in blocks]}
    if a.p1:
        mark_incomplete(blocks)
        jdump(dict(base, p1=p1(blocks, a.card)), a.out); return
    if a.p3:
        mark_incomplete(blocks)
        c1 = {"data": a.cal_card1, "blocks": load_blocks(a.cal_card1, "aifoundry1-c1", rounds=["v0"])} if a.cal_card1 else None
        jdump(dict(base, registration=p3(blocks, a.card, c1, allow_no_card1=a.allow_no_card1)), a.out); return
    if a.val:
        pr = H.load_json(a.prereg) if a.prereg else None
        if not pr:
            ap.error("--val needs --prereg prereg.json")
        vb = [b for b in blocks if b["round"] == "val"]
        ok, why, lockrec = val_lock(a.prereg, vb, a.amendment)
        if not ok:
            sys.exit("reduce.py --val refused: %s" % why)
        res = validate(vb, a.card, pr)
        res["lock"] = dict(lockrec, why=why)
        if pr.get("trigb_registered"):
            cand = (pr.get("probes") or {}).get(a.card) == "ALIVE_CANDIDATE"
            tb = trigb_card(a.data[0], a.card, vb, candidate=cand)
            res["items"]["TRIG-B"] = {"holds": tb.get("holds"), "outcome": H.card_verdicts({a.card: tb.get("holds")}, [a.card]),
                                      "detail": tb}
        jdump(dict(base, validation=res), a.out); return
    # --dev (default): everything reported
    dev = [b for b in blocks if b["round"] in ("r1", "r2", "r3")]
    mark_incomplete(dev)
    res = {"items": summarise(dev, a.card), "beta": beta_fit(dev),
           "note": "development values are REPORTED (DESIGN2 §2.5); none is a test",
           "incomplete_blocks": {str(b["pass"]): b["incomplete"] for b in dev if b.get("incomplete")}}
    if any(os.path.exists(os.path.join(b["dir"], "sp-idle.bin")) for b in blocks):
        res["trigb"] = trigb_card(a.data[0], a.card, blocks, candidate=probe_class_of(a.data[0]) == "ALIVE_CANDIDATE")
    b1 = [b for b in blocks if b["type"] == "B1"]
    if b1:
        res["B1"] = b1_report(b1[0])
    jdump(dict(base, dev=res), a.out)


def b1_report(blk):
    """The one-shot (aifoundry3, STUCK): the printed T of the first thermal event, and the host mean and high at it
    (the event's SP time mapped to host time by the tick fit on the power lines of the same dumps)."""
    import sptrace_events as SE
    evs, seen = [], set()
    for p in sorted(glob.glob(os.path.join(blk["dir"], "sp-*.bin"))):
        for e in SE.events(open(p, "rb").read()):
            if e["ts"] is not None and (e["ts"], e["text"]) not in seen:
                seen.add((e["ts"], e["text"])); evs.append(e)
    anchors = H.session_anchors(blk["dir"])
    sp = [(e["ts"], "start") for e in evs if e["kind"] in SE.POWER_START] + \
         [(e["ts"], "end") for e in evs if e["kind"] == "power_idle"]
    fit = SE.fit_ticks(sp, sorted(anchors)) if sp and anchors else None
    samples = sorted((s["t_ms"], s["temp_c"]["minshire"][0], s["temp_c"]["minshire"][2]) for x in blk["runs"]
                     for s in x["tel"] if s.get("t_ms") and (s.get("temp_c") or {}).get("minshire"))
    th = sorted([e for e in evs if e["kind"] in SE.THERMAL], key=lambda e: e["ts"])
    first = th[0] if th else None
    at = None
    if first and fit and fit["resid_max_ms"] <= 300:
        h = fit["a_ms"] + fit["b_ms_per_tick"] * first["ts"]
        win = [s for s in samples if h - 500 <= s[0] <= h + 500]
        at = {"host_ms": h, "mean": sorted({s[1] for s in win}), "high": sorted({s[2] for s in win})}
    return {"thermal_lines": [{"kind": e["kind"], "T": e.get("T"), "ts": e["ts"]} for e in th],
            "first_event": first and {"kind": first["kind"], "T": first.get("T")}, "at_event": at, "tick_fit": fit,
            "host_first_mean_66": next((s for s in samples if s[1] >= 66), None),
            "host_first_high_66": next((s for s in samples if s[2] >= 66), None),
            "reading": "H1 predicts a printed T of 66 with the host mean at 66; H1' predicts the host mean at about "
                       "62-64 with the high at 66. One observation on the development card: reported, never registered."}


if __name__ == "__main__":
    main()
