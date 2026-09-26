#!/usr/bin/env python3
"""V3-MEM decisions (PLAN3.md section 2, "V3-MEM"): the 15 pre-registered items MEM-P1..P10, MEM-X2, MEM-R1..R3 and
MEM-W, exactly as registered. No card.

    python3 tools/claims-v3/mem/reduce.py --data DIR --out verdicts.json

DIR holds one folder per card (aifoundry2/, aifoundry3/, aifoundry1-c0/, aifoundry1-c1/, and any other card folder
with a mem/ inside), each laid out like the card's DATA_ROOT (build/claims-v3/<card>): the passes are
DIR/<card>/mem/p<k>/. Only passes whose block.json says "ok" count; the drop rules are applied here from the pass's own
files (drop.json is only a note for the operator), with each card's clock rule (memv3.clock_rule: aifoundry2's
registered rule, aifoundry3 pinned, the busy rule on every other card). Works on partial data: an item with fewer than
3 kept passes on a card is INSUFFICIENT there.

verdicts.json is a list with one record per item: {"item", "claims", "prediction", "test", "per_card": {<every card>},
"outcome": PASS | FAIL | CARD-DIFFERENT | INSUFFICIENT, "reading", "all_cards": {"outcome", "reading", ...}}.
"outcome" and "reading" are the registered ones, computed exactly as before from aifoundry2 and aifoundry3 only.
"all_cards" (the four-card amendment) covers every card of the campaign (the four expected ones and any other card
folder present): PASS if the item holds on every tested card, CARD-DIFFERENT if on some, FAIL if on none, INSUFFICIENT
while a tested card (a missing one included) has too few kept repeats; "decided_outcome" is the same over the cards
that have enough. An item whose registered test names one card (MEM-R2: aifoundry2) is tested there only and reported
for the others. A sidecar <out>.passes.json lists every pass seen, kept or dropped, and why, with each card's clocks
inside and between kernels (the idle clock).

MEM-P1..P10 and MEM-X2 use the pre-registered decision code in prereg/ (byte-identical copies of the scratch reducers
the plan names: crosscard_tests.py and recompute_latency.py of the inventory, crosscard_v3.py and extra_values.py of the
verifier, their sha256 in README.md); this file only applies the drop rules, stages each pass in a scratch copy, and
maps the per-key results onto the plan's items. MEM-R1..R3 (the counter window) and MEM-W (the wake-up probe) are in
memv3.py, written from the registered test text (no scratch script existed for them).
"""
import argparse
import datetime
import sys
sys.dont_write_bytecode = True
import gzip
import json
import math
import os
import shutil
import sys
import tempfile

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"   # the prereg scripts run as subprocesses; keep the tree clean
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(HERE, "prereg")
sys.path.insert(0, HERE)
sys.path.insert(0, PRE)
import memv3  # noqa: E402
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)
import crosscard_tests as cc  # noqa: E402  (the copy in prereg/; crosscard_v3 below then reuses this module)
import crosscard_v3 as ccv3  # noqa: E402,F401  (patches cc.BANDS and cc.pass_values: P5b, P6r, P8b, P8c, X2, one-sided)

CARDS = memv3.CARDS          # the registered pair: "outcome" and "reading" are theirs, computed as registered
SHORT = memv3.SHORT
ALL = list(campaign.CAMPAIGN)   # main() sets it: the campaign's cards (--cards), then any other card folder under --data
PRESENT = set()              # cards with a <card>/mem folder under --data
INF = float("inf")


def short(c):
    return SHORT.get(c, c)

# The items as registered (plan3.json experiments[V3-MEM].predictions), with the keys of the pass-level values each uses.
ITEMS = [
    ("MEM-P1", ["anatomy-12", "anatomy-17", "anatomy-30", "anatomy-41", "anatomy-43"],
     ["P1_l3_within4_frac", "P1_l3_slope", "P1_l3_intercept"]),
    ("MEM-P2", ["anatomy-05", "anatomy-11", "anatomy-13", "anatomy-16", "anatomy-19", "anatomy-20", "anatomy-24",
                "anatomy-49", "anatomy-50", "anatomy-51", "anatomy-52", "anatomy-101"],
     ["P2_dram_within3_frac", "P2_dram_median_resid"]),
    ("MEM-P3", ["anatomy-18", "anatomy-47", "anatomy-48"], ["P3_msmap_match"]),
    ("MEM-P4", ["anatomy-54", "anatomy-55", "anatomy-57"],
     ["P4_row_conflict_extra", "P4_seq_col", "P4_seq_row", "P4_seq_bank"]),
    ("MEM-P5", ["anatomy-01", "anatomy-40", "anatomy-58", "anatomy-59", "anatomy-60", "anatomy-61", "anatomy-62",
                "anatomy-63", "anatomy-65"],
     ["P5_refresh_period", "P5b_closed_minus_open", "P5_max_extra", "P5_locked_slow_frac", "P5_locked_max"]),
    ("MEM-P6", ["anatomy-07", "anatomy-46", "anatomy-64", "anatomy-69"], ["P6r_hit_no_refresh", "P6r_hit_refresh"]),
    ("MEM-P7", ["anatomy-66", "anatomy-67", "anatomy-68"], ["P7_pagetimeout_z", "P7_late_hits"]),
    ("MEM-P8", ["anatomy-04", "anatomy-29", "anatomy-31", "anatomy-32", "anatomy-33", "anatomy-34", "anatomy-35",
                "anatomy-36", "anatomy-37", "anatomy-105", "anatomy-106"],
     ["P8_ladder_L2", "P8_ladder_L3", "P8_ladder_MEM", "P8_nofence_resid", "P8b_open_frac_diff", "P8c_nonopen_resid"]),
    ("MEM-P9", ["anatomy-45"], ["P9_l2_rep0_48_frac", "P9_l2_rep12_37_frac"]),
    ("MEM-P10", ["anatomy-03", "anatomy-28", "anatomy-94", "anatomy-95", "anatomy-99", "anatomy-100", "anatomy-102",
                 "anatomy-103", "anatomy-V01", "anatomy-121"],
     ["P10_raw_fixed_all10", "P10_raw_off_frac", "P10_stamps_at_11_short", "P10_arena_aligned"]),
    ("MEM-X2", ["anatomy-05", "anatomy-22", "anatomy-50"],
     [f"X2_s{s}_{k}" for s in memv3.REQUESTERS for k in ("l3_within4_frac", "dram_within3_frac")]),
    ("MEM-R1", ["hub-001", "hub-063", "hub-047", "hub-062", "anatomy-96"], None),
    ("MEM-R2", ["hub-V05"], None),
    ("MEM-R3", ["anatomy-100", "anatomy-103"], None),
    ("MEM-W", ["dvfs-04", "dvfs-13", "dvfs-14", "dvfs-15", "dvfs-54", "dvfs-55", "dvfs-57", "dvfs-77", "dvfs-V05"], None),
]
# Keys reported beside an item (no band of their own).
DESCRIPTIVE = {"MEM-P3": ["P3_msmap_lines"], "MEM-P5": ["P5_locked_period_med"],
               "MEM-P8": ["P8_ladder_MEM_within6", "P8_nodelay_fast"], "MEM-P10": ["P10_kernel_misses"]}

# Every-pass rules: the inventory's deterministic items (cc.EXACT: msmap 64/64, the timer fix, stamps at low bits 11,
# <= 3 late hits, locked max < 250) plus two the V3 table states: arena base 1 GB aligned (P10) and MEM-P7's
# "every pass, each card" for the pooled z in [-3, 3] (the inventory's code put z under a 99% t-interval; the
# t-interval is still reported beside it).
EVERY = dict(cc.EXACT)
EVERY["P10_arena_aligned"] = lambda v, p: v is True
EVERY["P7_pagetimeout_z"] = lambda v, p: -3 <= v <= 3
ARENA_MISALIGNED = {}      # card -> ["p<k> 0x..."]: blocks that stopped on a base not 1 GB aligned (filled by main)
LOOP_PERIOD = (512, 651)   # MEM-P5: a pass whose median locked-loop period is outside this is reported, not failed

# Every item: a card with fewer than 3 kept passes is undecided (plan section 2), whatever its passes show.
TESTS = {
    "MEM-P1": "99% t (df = passes-1) of the pass values inside [11.5, 12.5] (slope, excluding 0) and [107, 113] "
              "(intercept); within-4 fraction one-sided: lower end of the 99% interval >= 0.97; each card.",
    "MEM-P2": "lower end of the 99% interval of the within-3 fraction >= 0.85; 99% t of the median residual inside "
              "[-3, 3]; each card.",
    "MEM-P3": "every kept pass: the rising counter is the PA[8:6] memory shire for 64/64 lines; each card.",
    "MEM-P4": "99% t inside [32, 48] (row conflict, excl. 0), [-15, -9] (same row, excl. 0), [6, 12] (other row, excl. "
              "0), [-2, 2] (other bank); each card.",
    "MEM-P5": "99% t inside [2322, 2328] (period), [10, 13] (closed - open means, excl. 0), [170, 250] (max extra), "
              "[0.22, 0.28] (locked slow fraction; passes with median loop period outside 512-651 reported, not "
              "tested); locked max < 250 in every pass; each card.",
    "MEM-P6": "one-sided 99% bounds: no-refresh row hits lower end >= 0.98, across-refresh upper end <= 0.02; each card.",
    "MEM-P7": "every pass: pooled z in [-3, 3] and <= 3 of 300 late pairs open; each card (99% t of z reported).",
    "MEM-P8": "99% t inside [46, 50], [167, 175], [303, 315] (ladder L2, L3, DRAM medians), [30, 90] (no-fence, "
              "excl. 0), [0.20, 0.80] (P8b, excl. 0), [6, 30] (P8c, excl. 0); each card.",
    "MEM-P9": "one-sided: lower end of the 99% interval >= 0.90 for the rep-0 '48' (44-52) and rep-1/2 '37' (<= 40) "
              "fractions; each card.",
    "MEM-P10": "every pass: t_raw all 10 after the <11 fix, no stamp at low bits 11 short, arena base 1 GB aligned; "
               "99% t of the +-128 pair fraction inside [0.140, 0.172]; each card.",
    "MEM-X2": "lower end of the 99% interval over passes >= 0.97 (L3 within 4) and >= 0.85 (DRAM within 3), for each "
              "requester 7, 24, 31; each card.",
    "MEM-R1": "deterministic, every launch (t_raw, t_glitch, t_rawodd of every kept pass): raw pair differences only "
              "10, 138, -118 and one window 0..e with e in {9, 10, 11} fits them (t_glitch: its +-128 pattern reads "
              "e = 9, 10 or 11); any exception fails (decided with at least 3 kept passes on a card).",
    "MEM-R2": "aifoundry2: >= 2 distinct e among its readouts (no single e fits every readout; a readout with a pair "
              "outside 10/138/-118 or that no e fits is not a reading), with at least 3 kept passes; aifoundry3 "
              "reported per readout (no prior). The outcome is aifoundry2's.",
    "MEM-R3": "exact per t_glitch launch: 0 intervals off by 128 when e = 10, 1-3% when e = 9 or 11 (e read from the "
              "same launch); at least 3 launches per card.",
    "MEM-W": "per wake-up pass (P1-P4 reported); PASS on a card if P5 holds in 3 of 3 kept passes; a wake-up is claimed "
             "if P5 fails in >= 2 of 3; else mixed.",
}
PREDICTIONS = {}  # filled from plan3.json.gz when it is present (for the record; the code above is what decides)


def _clean(x):
    if isinstance(x, float):
        return None if math.isnan(x) else ("inf" if x == INF else "-inf" if x == -INF else x)
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    return x


def fmt(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, (int,)):
        return str(x)
    if isinstance(x, float):
        return f"{x:.{nd}g}" if abs(x) < 1e4 else f"{x:.1f}"
    return str(x)


# ---------------------------------------------------------------- staging and pass values
def stage(pdir, tmp):
    """Copy a pass's program outputs into a scratch folder, un-gzipping the labels (the prereg scripts read <name>.json;
    recompute_latency.py must never write next to the collected data)."""
    def cp(src_dir, dst_dir, names):
        os.makedirs(dst_dir, exist_ok=True)
        for n in names:
            j = memv3.find(src_dir, n + ".json")
            u = os.path.join(src_dir, n + ".u32")
            if j and os.path.exists(u):
                with memv3._open(j) as f, open(os.path.join(dst_dir, n + ".json"), "w") as g:
                    shutil.copyfileobj(f, g)
                shutil.copy(u, os.path.join(dst_dir, n + ".u32"))
    cp(pdir, tmp, memv3.X1_PROGS)
    for s in memv3.REQUESTERS:
        rd = os.path.join(pdir, f"req{s}")
        if os.path.isdir(rd):
            cp(rd, os.path.join(tmp, f"req{s}"), memv3.REQ_PROGS)


_cache = {}
_orig_run = cc.run


def _run_cached(script, *args):
    k = (script,) + tuple(args)
    if k not in _cache:
        _cache[k] = _orig_run(script, *args)
    return _cache[k]


cc.run = _run_cached   # pass_values and this file then share one recompute_latency.py run per folder


def x1_values(pdir, status, tmp_root):
    tmp = tempfile.mkdtemp(prefix="memv3-", dir=tmp_root)
    try:
        stage(pdir, tmp)
        # requester folders are passed only when complete (crosscard_v3 reads them if the folder exists)
        for s, ok in status["req_complete"].items():
            if not ok:
                shutil.rmtree(os.path.join(tmp, f"req{s}"), ignore_errors=True)
        v = cc.pass_values(tmp, list(memv3.REQUESTERS))      # = crosscard_v3.pass_values (patched in)
        L = cc.run("recompute_latency.py", "--data", tmp, "--l1-ref", "--fixed-model")
        v["P5_locked_period_med"] = L["refresh_locked"]["period_med"]
        v["l1_ref_shift"] = L.get("l1_ref_shift")
        v["P10_arena_aligned"] = status["arena_aligned"]
        return v
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- per-key tests
def subtest(key, rows, card=None):
    """rows: [(pass, value dict)] of the kept passes of one card."""
    got = [(k, p[key], p) for k, p in rows if p.get(key) is not None]
    n = len(got)
    res = {"n": n, "values": {f"p{k}": v for k, v, _ in got}}
    if key == "P5_locked_slow_frac":
        lo_p, hi_p = LOOP_PERIOD
        excl = [k for k, _, p in got if not (lo_p <= p.get("P5_locked_period_med", 0) <= hi_p)]
        if excl:
            res["reported_not_tested"] = [f"p{k}" for k in excl]
            got = [g for g in got if g[0] not in excl]
            n = len(got)
            if n == 0:
                res.update({"rule": "not applicable: every pass's loop period is outside 512-651", "holds": None,
                            "not_applicable": True})
                return res
    if key in EVERY:
        fails = [f"p{k}" for k, v, p in got if not EVERY[key](v, p)]
        if key == "P10_arena_aligned" and ARENA_MISALIGNED.get(card):
            # a block that stopped on a misaligned base (the plan's assert) has no kept values, but it is a failed
            # prediction for this card, not a missing pass
            fails += [f"{x} (block stopped)" for x in ARENA_MISALIGNED[card]]
        # plan section 2: fewer than 3 kept repeats on a card leaves the claim as it is, a failure included
        res.update({"rule": "every pass", "fail_passes": fails,
                    "holds": (False if fails else True) if n >= 3 else None})
        if key in cc.BANDS and n >= 2:   # reported beside the every-pass rule (MEM-P7's z)
            m, l, h = cc.interval([float(v) for _, v, _ in got])
            res.update({"mean": m, "ci99": [l, h]})
        return res
    lo, hi, null = cc.BANDS[key]
    vals = [float(v) for _, v, _ in got]
    if not vals:
        res.update({"rule": "99% t", "holds": None})
        return res
    m, l, h = cc.interval(vals)
    ok = l is not None and lo <= l and h <= hi and (null is None or not (l <= null <= h))
    one = "one-sided (lower end)" if hi == INF else "one-sided (upper end)" if lo == -INF else "99% t"
    res.update({"rule": one, "mean": m, "ci99": [l, h], "band": [lo, hi], "excludes": null,
                "holds": ok if n >= 3 else None})
    return res


def combine(tests):
    hs = [t["holds"] for t in tests.values() if not t.get("not_applicable")]
    if any(h is False for h in hs):
        return False
    if hs and all(h is True for h in hs):
        return True
    return None


def outcome(h2, h3):
    if h2 is None or h3 is None:
        return "INSUFFICIENT"
    if h2 and h3:
        return "PASS"
    if not h2 and not h3:
        return "FAIL"
    return "CARD-DIFFERENT"


def _over(hs):
    """PASS / CARD-DIFFERENT / FAIL over decided cards (None when there is none)."""
    if not hs:
        return None
    if all(hs):
        return "PASS"
    if not any(hs):
        return "FAIL"
    return "CARD-DIFFERENT"


ALL_CARDS_TEST = ("the registered per-card test, unchanged, on every card of the campaign (aifoundry2, aifoundry3, "
                  "aifoundry1-c1 (amendment A4) and any other card folder present): PASS if it holds on every tested "
                  "card, CARD-DIFFERENT if on some, FAIL if on none, INSUFFICIENT while a tested card (a missing one "
                  "included) has fewer than 3 kept repeats; a test registered for one card only is reported, not "
                  "tested, on the others.")


def all_cards(per, tested=None):
    """The all-cards outcome of an item (amendment for aifoundry1's two cards): per = {card: {"holds": ...}}."""
    tested = list(ALL if tested is None else tested)
    holds = {c: per[c]["holds"] for c in tested}
    lacking = [c for c in tested if holds[c] is None]
    dec = [holds[c] for c in tested if holds[c] is not None]
    return {"outcome": "INSUFFICIENT" if lacking else (_over(dec) or "INSUFFICIENT"), "test": ALL_CARDS_TEST,
            "cards": list(ALL), "tested": tested, "reported_only": [c for c in ALL if c not in tested],
            "no_data": [c for c in ALL if c not in PRESENT], "holds": holds, "lacking_repeats": lacking,
            "decided_outcome": _over(dec), "decided_cards": [c for c in tested if holds[c] is not None]}


def describe_fail(tests):
    out = []
    for k, t in tests.items():
        if t.get("holds") is False:
            if t.get("rule") == "every pass":
                out.append(f"{k} fails in {','.join(t['fail_passes'])}")
            else:
                l, h = t["ci99"]
                out.append(f"{k} {fmt(t['mean'])} [{fmt(l)}, {fmt(h)}] vs [{fmt(t['band'][0])}, {fmt(t['band'][1])}]")
    return "; ".join(out)


def card_phrase(card, pc):
    s = short(card)
    if pc["holds"] is True:
        return f"{s} holds ({pc['n']} passes)"
    if pc["holds"] is False:
        return f"{s} fails ({pc['n']} passes: {describe_fail(pc['tests'])})"
    seen = [f"{k} fails in {','.join(t['fail_passes'])}" for k, t in pc["tests"].items() if t.get("fail_passes")]
    return f"{s} undecided ({pc['n']} kept passes" + (f"; seen: {'; '.join(seen)})" if seen else ")")


def phrase_all(card, text):
    """A card's phrase in an all-cards reading: 'no data' for a card with no folder under --data."""
    return f"{short(card)} no data" if card not in PRESENT else text


def keyed_item(item, claims, keys, kept):
    per = {}
    for card in ALL:
        rows = kept[card]
        tests = {k: subtest(k, rows, card) for k in keys}
        extra = {k: {f"p{p}": v.get(k) for p, v in rows} for k in DESCRIPTIVE.get(item, [])}
        per[card] = {"n": len(rows), "passes": [f"p{p}" for p, _ in rows], "tests": tests, "reported": extra,
                     "holds": combine(tests)}
    oc = outcome(per["aifoundry2"]["holds"], per["aifoundry3"]["holds"])
    reading = f"{oc}: " + "; ".join(card_phrase(c, per[c]) for c in CARDS)
    ac = all_cards(per)
    ac_reading = f"{ac['outcome']}: " + "; ".join(phrase_all(c, card_phrase(c, per[c])) for c in ALL)
    if item == "MEM-P8":
        hs = [per[c]["tests"][k]["holds"] for c in CARDS for k in ("P8b_open_frac_diff", "P8c_nonopen_resid")]
        reading += (". anatomy-35 restored (P8b and P8c hold on both cards)" if all(h is True for h in hs) else
                    ". anatomy-35 stays rewritten (P8b/P8c do not hold on both cards)" if any(h is False for h in hs)
                    else ". anatomy-35 undecided")
        ha = {c: [per[c]["tests"][k]["holds"] for k in ("P8b_open_frac_diff", "P8c_nonopen_resid")] for c in ALL}
        bad = [short(c) for c, v in ha.items() if any(h is False for h in v)]
        ac_reading += (". anatomy-35's P8b and P8c hold on every card" if all(h is True for v in ha.values() for h in v)
                       else f". anatomy-35's P8b/P8c fail on {', '.join(bad)}" if bad
                       else ". anatomy-35's P8b/P8c undecided on some card")
    if item == "MEM-P5":
        na = [short(c) for c in CARDS if per[c]["tests"]["P5_locked_slow_frac"].get("reported_not_tested")]
        if na:
            reading += f". Locked-loop slow fraction reported, not tested, for passes on {', '.join(na)} (loop period)"
        na = [short(c) for c in ALL if per[c]["tests"]["P5_locked_slow_frac"].get("reported_not_tested")]
        if na:
            ac_reading += (f". Locked-loop slow fraction reported, not tested, for passes on {', '.join(na)} "
                           "(loop period)")
    ac["reading"] = ac_reading
    return {"item": item, "claims": claims, "per_card": per, "outcome": oc, "reading": reading, "all_cards": ac}


# ---------------------------------------------------------------- the counter window
def timer_items(timers):
    """timers[card] = [(k, {prog: readout})]."""
    res = {}
    per1, per2, per3 = {}, {}, {}
    for card in ALL:
        rows = timers[card]
        launches = [(k, name, r) for k, t in rows for name, r in t.items() if r is not None]
        exc = [f"p{k}/{name}: {r['r1_why']}" for k, name, r in launches if not r["r1_ok"]]
        n = len(rows)
        per1[card] = {"n": n, "launches": len(launches), "exceptions": exc,
                      "readouts": {f"p{k}/{name}": r.get("e_readout") for k, name, r in launches},
                      "diffs": {f"p{k}/{name}": r.get("diffs") for k, name, r in launches if "diffs" in r},
                      "holds": (False if exc else True) if n >= 3 else None}
        sets = [set(r["readout_set"]) for k, name, r in launches if r.get("readout_set") is not None]
        inter = set.intersection(*sets) if sets else None
        varies = sets != [] and not inter
        per2[card] = {"n": n, "readouts": per1[card]["readouts"], "informative_readouts": len(sets),
                      "common_e": memv3._rng(inter) if inter is not None else None, "varies": varies}
        if card == "aifoundry2":
            per2[card]["holds"] = (True if varies else False) if n >= 3 else None
        elif card == "aifoundry3":
            per2[card]["holds"] = None
            per2[card]["note"] = "no prior: reported per readout"
        else:
            per2[card]["holds"] = None
            per2[card]["note"] = ("reported per readout, not tested: the registered count (>= 2 distinct e) is "
                                  "aifoundry2's")
        gl = [(k, r) for k, name, r in launches if name == "t_glitch"]
        exc3 = [f"p{k}: e {r['e']}, {r['plus128'] + r['minus128']} of {r['intervals']} off by 128" for k, r in gl
                if not r["r3_ok"]]
        per3[card] = {"n": len(gl), "launches": {f"p{k}": {"e": r["e"], "off128_frac": r["off128_frac"],
                                                             "plus_phase": r.get("plus_phase"),
                                                             "minus_phase": r.get("minus_phase")} for k, r in gl},
                      "exceptions": exc3, "holds": (False if exc3 else True) if len(gl) >= 3 else None}
    # R1
    r1 = lambda c: (f"{short(c)} {per1[c]['launches']} launches, "  # noqa: E731
                    + (f"{len(per1[c]['exceptions'])} exceptions ({per1[c]['exceptions'][0]})" if per1[c]["exceptions"]
                       else "no exception"))
    oc = outcome(per1["aifoundry2"]["holds"], per1["aifoundry3"]["holds"])
    rd = "; ".join(r1(c) for c in CARDS)
    ac = all_cards(per1)
    ac["reading"] = f"{ac['outcome']}: " + "; ".join(phrase_all(c, r1(c)) for c in ALL)
    res["MEM-R1"] = {"per_card": per1, "outcome": oc, "reading": f"{oc}: {rd}", "all_cards": ac}
    # R2
    h2 = per2["aifoundry2"]["holds"]
    oc = "PASS" if h2 is True else "FAIL" if h2 is False else "INSUFFICIENT"
    const_both = all(per2[c]["n"] >= 3 and not per2[c]["varies"] for c in CARDS)
    anyvar = any(per2[c]["n"] >= 3 and per2[c]["varies"] for c in CARDS)

    # the readouts that pin e to one value (t_glitch always; t_rawodd when it reached 10 and 11)
    def single_valued(cards):
        rng = set()
        for c in cards:
            for _, t in timers[c]:
                for r in t.values():
                    if r and r.get("readout_set") is not None and len(r["readout_set"]) == 1:
                        rng.add(r["readout_set"][0])
        return sorted(rng)
    rng = single_valued(CARDS)
    if const_both:
        page = (f"low 7 bits 0-{per2['aifoundry2']['common_e']} (a2) / 0-{per2['aifoundry3']['common_e']} (a3) read "
                "128 short (both cards)")
    elif anyvar:
        page = ("the window is 10-12 cycles and changes between launches; check corrected intervals for +-128 outliers"
                + (f" (single-valued readouts seen: e = {', '.join(map(str, rng))})" if rng else ""))
    else:
        page = "undecided (fewer than 3 kept passes on a card)"
    # the same page rule over every card of the campaign (reported; the registered outcome is aifoundry2's count)
    const_all = all(per2[c]["n"] >= 3 and not per2[c]["varies"] for c in ALL)
    anyvar_all = any(per2[c]["n"] >= 3 and per2[c]["varies"] for c in ALL)
    rng_all = single_valued(ALL)
    if const_all:
        page_all = ("low 7 bits " + " / ".join(f"0-{per2[c]['common_e']} ({short(c)})" for c in ALL)
                    + " read 128 short (every card)")
    elif anyvar_all:
        page_all = ("the window is 10-12 cycles and changes between launches; check corrected intervals for +-128 "
                    "outliers"
                    + (f" (single-valued readouts seen: e = {', '.join(map(str, rng_all))})" if rng_all else "")
                    + f" (varies on {', '.join(short(c) for c in ALL if per2[c]['n'] >= 3 and per2[c]['varies'])})")
    else:
        page_all = "undecided (fewer than 3 kept passes on a card)"
    ac = all_cards(per2, tested=["aifoundry2"])
    ac["page"] = page_all
    ac["reading"] = (f"{ac['outcome']} (tested on a2 only, as registered): "
                     + "; ".join(phrase_all(c, f"{short(c)} e {'varies' if per2[c]['varies'] else 'constant'} "
                                               f"(common e {per2[c]['common_e']}, {per2[c]['n']} kept passes)")
                                 for c in ALL) + f". Page (every card): {page_all}")
    res["MEM-R2"] = {"per_card": per2, "outcome": oc, "page": page,
                     "reading": f"{oc}: a2 e {'varies' if per2['aifoundry2']['varies'] else 'constant'} "
                                f"(common e {per2['aifoundry2']['common_e']}, {per2['aifoundry2']['informative_readouts']}"
                                f" readouts); a3 e {'varies' if per2['aifoundry3']['varies'] else 'constant'} "
                                f"(common e {per2['aifoundry3']['common_e']}). Page: {page}", "all_cards": ac}
    # R3
    r3 = lambda c: f"{short(c)} " + ", ".join(  # noqa: E731
        f"{p} e={v['e']} {fmt(100 * v['off128_frac'], 2) if v['off128_frac'] is not None else '-'}%"
        for p, v in per3[c]["launches"].items())
    oc = outcome(per3["aifoundry2"]["holds"], per3["aifoundry3"]["holds"])
    rd = "; ".join(r3(c) for c in CARDS)
    ac = all_cards(per3)
    ac["reading"] = f"{ac['outcome']}: " + "; ".join(phrase_all(c, r3(c)) for c in ALL)
    res["MEM-R3"] = {"per_card": per3, "outcome": oc, "reading": f"{oc}: {rd}", "all_cards": ac}
    return res


# ---------------------------------------------------------------- the wake-up probe
def wake_item(wakes, idle):
    """wakes[card] = [(k, wake_values, status)] of the kept wake-up passes, in pass order; idle = idle_summary()."""
    per = {}
    for card in ALL:
        rule = memv3.clock_rule(card)
        rows = [(k, w, s) for k, w, s in wakes[card] if w.get("evaluable")]
        used = rows[:3]
        p5 = [w["P5"]["holds"] for _, w, _ in used]
        fails = sum(1 for x in p5 if not x)
        if len(used) < 3:
            holds, verdict = None, f"{len(used)} of 3 kept probes"
        elif fails == 0:
            holds, verdict = True, "no wake-up >= 5 cycles up to 16M cycles (P5 3 of 3)"
        elif fails >= 2:
            holds, verdict = False, f"wake-up claimed (P5 fails in {fails} of 3)"
        else:
            holds, verdict = False, "mixed (P5 fails in 1 of 3)"
        same = [x for _, w, _ in used for x in w["P4"].get("same_class_1000_16M", [])]
        agree = sum(same) / len(same) if same else None
        passes = {}
        for k, w, s in used:
            passes[f"p{k}"] = {"P1": w["P1"]["holds"], "P2": w["P2"]["holds"], "P2_median": w["P2"]["median_diff_16M"],
                               "P3a": w["P3"]["holds_a"], "P3b_settling": w["P3"]["holds_b"],
                               "P3_L2_noidle_idle16M": [w["P3"]["noidle_median"], w["P3"]["idle16M_median"]],
                               "P4": w["P4"]["holds"], "P4_slow_frac": w["P4"]["slow_frac"],
                               "P5": w["P5"]["holds"], "P5_lines_ge5": w["P5"]["lines_ge5_by_level"],
                               "P6_clock": {"pre": s["pre"]["mhz_minion"], "post": s["post"]["mhz_minion"]},
                               "P6_probe_mhz_eff": s.get("probe_mhz_eff"),
                               "l1_raw": w["l1_raw_median"], "shift_to_22sep_frame": w["shift_to_22sep_frame"]}
        if rule == "busy":
            # the probe's own clock (cycles / wall time); its pre/post samples are idle brackets, reported in P6_clock
            lo, hi = memv3.F_EFF_BAND
            fs = [s.get("probe_mhz_eff") for _, _, s in used]
            p6 = all(f is not None and lo <= f <= hi for f in fs) if used else None
            basis = f"the probe's own clock (cycles / wall time) in {lo:g}-{hi:g} MHz"
        else:
            p6 = all(s["pre"]["all600"] and s["post"]["all600"] for _, _, s in used) if used else None
            basis = "pre/post samples all 600 MHz"
        per[card] = {"n": len(used), "kept_probes": [f"p{k}" for k, _, _ in rows], "passes": passes,
                     "P4_same_class_pooled": agree, "P4_same_class_holds": (agree >= 0.80) if agree is not None else None,
                     "P6_600MHz": p6, "P6_basis": basis, "clock_rule": rule, "decision": verdict, "holds": holds}
    oc = outcome(per["aifoundry2"]["holds"], per["aifoundry3"]["holds"])

    def sub(c):
        pc = per[c]
        if not pc["passes"]:
            return f"{short(c)}: no kept probe"
        n = len(pc["passes"])
        cnt = lambda key: sum(1 for v in pc["passes"].values() if v[key] is True)  # noqa: E731
        s = (f"{short(c)}: {pc['decision']}; P1 {cnt('P1')}/{n}, P2 {cnt('P2')}/{n}, P3a {cnt('P3a')}/{n}, "
             f"P3b {cnt('P3b_settling')}/{n}, P4 {cnt('P4')}/{n}, same class at 1,000 and 16M "
             f"{fmt(pc['P4_same_class_pooled'], 2)}{'' if pc['P4_same_class_holds'] is not False else ' (< 0.80)'}")
        if cnt("P3b_settling") < n:
            s += " (P3b failing drops only the settling explanation, dvfs-14)"
        if c == "aifoundry3" and pc["P6_600MHz"] is False:
            s += ", P6 fails: pre/post clock not 600 MHz"
        if pc["clock_rule"] == "busy":
            fs = [v["P6_probe_mhz_eff"] for v in pc["passes"].values() if v["P6_probe_mhz_eff"] is not None]
            s += (f", probe clock {fmt(min(fs), 4)}-{fmt(max(fs), 4)} MHz" if fs else ", probe clock not recorded")
        return s
    ac = all_cards(per)
    note = idle_note(idle)
    ac["reading"] = (f"{ac['outcome']}: " + "; ".join(phrase_all(c, sub(c)) for c in ALL) + f". {note}")
    ac["idle_clock"] = idle
    return {"per_card": per, "outcome": oc, "reading": f"{oc}: " + "; ".join(sub(c) for c in CARDS), "all_cards": ac,
            "idle_clock_note": note}


# ---------------------------------------------------------------- the idle clock (between kernels)
def idle_summary(idle_rows):
    """idle_rows[card] = [pass_status of every block-ok pass]: the clock the card reads between kernels (the X1
    sampler's readings outside kernel windows, the probe's pre/post samples) and, on busy-rule cards, the idle state
    `ettelem config` reports at the start and end of a pass."""
    out = {}
    for card in ALL:
        x1, br, ps, cm = {}, {}, {}, {}
        for s in idle_rows.get(card, []):
            for k, v in ((s.get("clock_split") or {}).get("idle") or {}).get("mhz_minion", {}).items():
                x1[k] = x1.get(k, 0) + v
            w = s.get("wake") or {}
            for side in ("pre", "post"):
                for k, v in ((w.get(side) or {}).get("mhz_minion") or {}).items():
                    br[k] = br.get(k, 0) + v
            for r in s.get("idle_state") or []:
                if r.get("power_state_name"):
                    ps[r["power_state_name"]] = ps.get(r["power_state_name"], 0) + 1
                if r.get("minion_mhz") is not None:
                    cm[str(r["minion_mhz"])] = cm.get(str(r["minion_mhz"]), 0) + 1
        tot = {}
        for d in (x1, br, cm):
            for k, v in d.items():
                tot[k] = tot.get(k, 0) + v
        modal = max(tot, key=lambda k: (tot[k], k)) if tot else None
        # the card idles off 600 MHz if most of its idle readings are, or if `ettelem config` (read with no kernel and
        # no sampler, before the heat) ever found it off 600 (aifoundry1-c0's low_power state), even when the heated
        # card then stayed at 600 between kernels
        out[card] = {"passes": len(idle_rows.get(card, [])), "modal_mhz": modal, "x1_between_kernels_mhz": x1,
                     "probe_brackets_mhz": br, "config_power_state": ps, "config_minion_mhz": cm,
                     "differs_from_600": (modal is not None and modal != "600") or any(k != "600" for k in cm)}
    return out


def idle_note(idle):
    def one(c):
        v = idle[c]
        if v["modal_mhz"] is None:
            return f"{short(c)} -"
        cfg = [f"{k} MHz x{n}" for k, n in sorted(v["config_minion_mhz"].items())]
        cfg += [f"{k} x{n}" for k, n in sorted(v["config_power_state"].items())]
        return f"{short(c)} {v['modal_mhz']} MHz" + (f" (ettelem config: {', '.join(cfg)})" if cfg else "")
    diff = [short(c) for c in ALL if idle[c]["differs_from_600"]]
    return ("Idle clock between kernels: " + ", ".join(one(c) for c in ALL)
            + (f"; {', '.join(diff)} idle(s) off 600 MHz (another idle state)" if diff else "")
            + ". The probe's idle delays spin inside one kernel, so a card's between-kernel idle state is not what P5 "
              "tests.")


# ---------------------------------------------------------------- main
def load_plan():
    here_root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    p = os.path.join(here_root, "docs/reports/data/2026-09-25-claims-v3/plan3.json.gz")
    if not os.path.exists(p):
        return None
    try:
        with gzip.open(p, "rt") as f:
            plan = json.load(f)
        e = [x for x in plan["experiments"] if x["id"] == "V3-MEM"][0]
        return {x["item"]: x for x in e["predictions"]}
    except Exception:  # noqa: BLE001
        return None


def discover(data, expected=campaign.CAMPAIGN):
    """The cards: the campaign's (aifoundry2, aifoundry3 first), then any other folder with a mem/ inside."""
    present = set()
    if os.path.isdir(data):
        present = {n for n in os.listdir(data) if os.path.isdir(os.path.join(data, n, "mem"))}
    return list(expected) + sorted(present - set(expected)), present


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="folder with one folder per card (aifoundry2/, aifoundry3/, "
                                                  "aifoundry1-c0/, aifoundry1-c1/) laid out like DATA_ROOT")
    ap.add_argument("--out", required=True, help="verdicts.json")
    ap.add_argument("--tmp", default=None, help="scratch folder for staged copies (default: the system temp dir)")
    ap.add_argument("--cards", default=",".join(campaign.CAMPAIGN),
                    help="comma-separated cards all_cards expects (default: tools/claims-v3/campaign.py)")
    a = ap.parse_args()
    cards, present = discover(a.data, [c for c in a.cards.split(",") if c])
    ALL[:] = cards
    PRESENT.clear()
    PRESENT.update(present)
    plan = load_plan()
    passes_log = {c: [] for c in ALL}
    kept = {c: [] for c in ALL}
    timers = {c: [] for c in ALL}
    wakes = {c: [] for c in ALL}
    idle_rows = {c: [] for c in ALL}
    errors = []
    for card in ALL:
        root = os.path.join(a.data, card, "mem")
        for k, d in memv3.pass_dirs(root):
            for base in sorted({l.get("arena_base") for l in memv3.memprobe_lines(d) if l.get("arena_base")}):
                if int(base, 16) % (1 << 30):
                    ARENA_MISALIGNED.setdefault(card, []).append(f"p{k} {base}")
        for k, d in memv3.pass_dirs(root):
            b = memv3.block_status(d)
            entry = {"pass": k, "dir": d, "block_status": (b or {}).get("status"), "note": (b or {}).get("note")}
            passes_log[card].append(entry)
            if not b or b.get("status") != "ok":
                entry["used"] = "no (block not ok)"
                continue
            s = memv3.pass_status(d, card)
            idle_rows[card].append(s)
            sp = s["clock_split"]
            entry.update({"x1_keep": s["x1_keep"], "x1_reason": s["x1_reason"], "telemetry": s["telemetry"],
                          "clock_rule": s["clock_rule"],
                          "clock_split": {"kernel_windows": sp["kernel_windows"], "busy": sp["busy"]["mhz_minion"],
                                          "idle": sp["idle"]["mhz_minion"], "unplaced": sp["unplaced"],
                                          "x1_launch_mhz_eff": sp["x1_launch_mhz_eff"]},
                          "idle_state": s["idle_state"],
                          "arena_bases": s["arena_bases"], "req_complete": s["req_complete"],
                          "wake": s["wake"] and {x: s["wake"][x] for x in ("complete", "keep", "reason", "rule",
                                                                         "probe_mhz_eff")}})
            if s["x1_keep"] and len(kept[card]) >= memv3.X1_TARGET:
                entry["used"] = f"no: the card already has {memv3.X1_TARGET} kept passes (the first ones are used)"
            elif s["x1_keep"]:
                try:
                    kept[card].append((k, x1_values(d, s, a.tmp)))
                    timers[card].append((k, memv3.timer_readouts(d)))
                except Exception as e:  # noqa: BLE001
                    errors.append(f"{card} p{k}: X1 reduction failed: {e!r}")
                    entry["x1_error"] = repr(e)
            if s["wake"] and s["wake"]["keep"] and len(wakes[card]) >= memv3.WAKE_NEEDED:
                entry["wake_used"] = f"no: the card already has {memv3.WAKE_NEEDED} kept probes"
            elif s["wake"] and s["wake"]["keep"]:
                try:
                    wakes[card].append((k, memv3.wake_values(os.path.join(d, "wake")), s["wake"]))
                except Exception as e:  # noqa: BLE001
                    errors.append(f"{card} p{k}: wake-up reduction failed: {e!r}")
    idle = idle_summary(idle_rows)
    ti = timer_items(timers)
    wi = wake_item(wakes, idle)
    out = []
    for item, claims, keys in ITEMS:
        if keys is not None:
            rec = keyed_item(item, claims, keys, kept)
        elif item in ti:
            rec = {"item": item, "claims": claims, **ti[item]}
        else:
            rec = {"item": item, "claims": claims, **wi}
        rec["test"] = TESTS[item]
        if plan and item in plan:
            rec["prediction"] = plan[item]["prediction"]
            rec["decision_rule"] = plan[item]["decision_rule"]
            if sorted(plan[item]["claims"]) != sorted(claims):
                errors.append(f"{item}: claims differ from plan3.json.gz")
        ordered = {k: rec[k] for k in ("item", "claims", "prediction", "decision_rule", "test", "per_card", "outcome",
                                       "reading") if k in rec}
        ordered.update({k: v for k, v in rec.items() if k not in ordered})
        out.append(_clean(ordered))
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    side = os.path.splitext(a.out)[0] + ".passes.json"
    with open(side, "w") as f:
        json.dump(_clean({"generated": datetime.datetime.now().isoformat(timespec="seconds"), "data": os.path.abspath(a.data),
                          "cards": ALL, "present": sorted(PRESENT),
                          "clock_rule": {c: memv3.clock_rule(c) for c in ALL},
                          "passes": passes_log, "errors": errors, "idle_clock": idle,
                          "kept": {c: {"x1": [f"p{k}" for k, _ in kept[c]], "wake": [f"p{k}" for k, _, _ in wakes[c]]}
                                   for c in ALL}}), f, indent=1, default=str)
    for r in out:
        print(f"{r['item']:8s} {r['outcome']:14s} {r['reading'][:220]}")
        print(f"{'':8s} all cards: {r['all_cards']['outcome']:14s} {r['all_cards']['reading'][:260]}")
    for e in errors:
        print("ERROR", e, file=sys.stderr)


if __name__ == "__main__":
    main()
