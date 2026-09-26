#!/usr/bin/env python3
"""V3-TEL reducer: the pre-registered items of PLAN3 §2 "V3-TEL" (TEL-P1..P7, TEL-S, TEL-Q, TEL-R, TEL-G), with the
bands, tests and decision rules exactly as registered (plan3.json experiments[V3-TEL].predictions and the
components' test_as_registered). Every choice the registration left open is fixed in README.md "Reduction", before
any data.

    python3 tools/claims-v3/tel/reduce.py --data <dir holding one directory per card, laid out like DATA_ROOT>
                                           --out verdicts.json [--expect aifoundry2,aifoundry3,aifoundry1-c0,aifoundry1-c1]

Input per card: <data>/<card>/tel/p<N>/ as block.sh writes it; only passes whose block.json says "ok" are used. Every
card directory present is read. It runs on partial data: a card with fewer than 3 kept passes gives INSUFFICIENT.

Output: {"exp": "tel", "items": [{"item", "claims", "per_card": {card: {..., "n", "status"}}, "test", "outcome",
"reading", "all_cards": {...}, "reading_all_cards", ...}], "cards": {...}, "idle_clock": {...}, "passes": {...},
"notes": [...]}.
- "outcome" is the REGISTERED outcome, computed from aifoundry2 and aifoundry3 only, exactly as registered: PASS (holds
  on every card the item names), FAIL, CARD-DIFFERENT (holds on one of the two cards) or INSUFFICIENT (a card has
  fewer than 3 kept passes).
- "all_cards" (amendment TEL-4C, README "Four cards") is the same test over every card the item tests: PASS (holds
  on every one), CARD-DIFFERENT (on some), FAIL (on none), INSUFFICIENT (a tested card, including an expected card
  with no data, has fewer than 3 kept passes). Items whose registered band names aifoundry2 or aifoundry3 only are
  REPORTED for the other cards (per_card status "reported"), not tested; items registered for each card are tested
  on every card unchanged.
- A new governor-free card (every card but aifoundry2 and aifoundry3) drops for the clock only BUSY samples: those
  inside a burst from 500 ms after its start; its idle brackets are never dropped for their clock (aifoundry1-c0
  idles at 300 MHz). aifoundry2 keeps its registered rule, aifoundry3 (pinned) has none.

Reused code: tools/ettelem/parse_sptrace_voltage.py parse() (voltage maps), workloads/enercat/analyze_catalogue.py
bursts_of() and rail_fall_curves() (f(1 s), the catalogue definition), the SP stats record layout of
workloads/memprobe/analyze_power.py read_trace() (via tel_util.spst_records); vectorised re-implementations with the
same model, grid and rules: validate3/pt-spatial-verify/v13_refresh.py and v13b_powercsv.py (refresh fits),
validate3/inv/pt-spatial-work/x2_reduce.py (planes, permutation p, same seed) and x3_reduce.py (peak-hold windows).
"""
import argparse
import collections
import glob
import json
import math
import os
import re
import statistics as st
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("V3_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the tree root (parsers, mesh layout)
sys.path.insert(0, HERE)
import tel_util as TU  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "tools", "ettelem"))
from parse_sptrace_voltage import parse as vparse, ring_entries  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "workloads", "enercat"))
import analyze_catalogue as AC  # noqa: E402
import numpy as np  # noqa: E402

A2, A3 = "aifoundry2", "aifoundry3"
CARDS = (A2, A3)                  # the registered cards: every registered outcome is computed from these two only
EXPECT = campaign.CAMPAIGN        # the campaign's cards (amendments TEL-4C, A4); --expect overrides
ALL = list(EXPECT)                # every card of this reduction: the expected cards and any other present (set in main)
PRESENT = set()                   # the cards with a directory under --data
PINNED = (A3,)                    # pinned at 600 MHz by a boot service: no clock rule
SETTLE_MS = 500.0                 # new governor-free cards: a burst's samples count as busy from 500 ms after its start
NEED = 3
T2 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169}  # 99% two-sided
T1 = {1: 31.821, 2: 6.965, 3: 4.541, 4: 3.747, 5: 3.365, 6: 3.143, 7: 2.998, 8: 2.896, 9: 2.821, 10: 2.764}  # 99% one-sided
TRIM = 1000.0          # ms: SP intervals within 1 s of a segment boundary are dropped
LAY = json.load(open(os.path.join(REPO, "docs/reports/data/2026-09-20-power-aifoundry2/summary.json")))["mesh"]["layout"]
S34 = [str(s) for s in range(34)]


def r3(x, k=3):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), k)


def tstat(v, table):
    v = [x for x in v if x is not None]
    n = len(v)
    if n < 2:
        return None
    m = st.mean(v)
    sd = st.stdev(v)
    return {"n": n, "mean": r3(m), "sd": r3(sd), "half": r3(table[min(n - 1, 10)] * sd / math.sqrt(n))}


def combine(pc, cards):
    s = [pc[c]["status"] for c in cards]
    if any(x == "insufficient" for x in s):
        return "INSUFFICIENT"
    if all(x == "holds" for x in s):
        return "PASS"
    if len(cards) == 2 and any(x == "holds" for x in s):
        return "CARD-DIFFERENT"
    return "FAIL"


def status_of(n, ok):
    return "insufficient" if n < NEED else ("holds" if ok else "fails")


def new_cards():
    return [c for c in ALL if c not in CARDS]


def clock_rule(card):
    """'a2': aifoundry2's registered rule (any sample off 600 MHz drops, idle arms included); None: aifoundry3, pinned;
    'busy': a new governor-free card, where only busy samples (inside a burst, from SETTLE_MS after its start) drop."""
    if card == A2:
        return "a2"
    if card in PINNED:
        return None
    return "busy"


def reported(n, **kw):
    d = {"n": n, "status": "reported",
         "note": "the registered band or rule names aifoundry2 or aifoundry3 only: reported for this card, not tested (amendment TEL-4C)"}
    d.update(kw)
    return d


def all_cards(pc, tested, **kw):
    """The four-card outcome over the cards the item tests (the others, status 'reported', are listed, not tested)."""
    s = {c: pc[c]["status"] for c in tested}
    if not tested or any(x == "insufficient" for x in s.values()):
        oc = "INSUFFICIENT"
    elif all(x == "holds" for x in s.values()):
        oc = "PASS"
    elif any(x == "holds" for x in s.values()):
        oc = "CARD-DIFFERENT"
    else:
        oc = "FAIL"
    d = {"outcome": oc, "tested": list(tested), "status": s,
         "reported": [c for c in ALL if c not in tested and pc.get(c, {}).get("status") == "reported"],
         "missing": [c for c in ALL if c not in PRESENT]}
    d.update(kw)
    return d


# ------------------------------------------------------------------------------------------------ loading
def tagged(path):
    out = collections.defaultdict(list)
    for l in TU.lines(path):
        m = re.match(r"^(\S+) (ENERCAT|SPARSITY) (\{.*\})\s*$", l)
        if m:
            try:
                out[m.group(1)].append(json.loads(m.group(3)))
            except ValueError:
                pass
    return out


def timed(rows):
    """A host process's timed launches: sparsity_host prints a calibration launch first ("launch": -1, ~18 ms, whose
    ghz reads ~0.586 because the wall time is mostly overhead) and then 0.5 s launches 0, 1, ...; the repository's
    analyses drop launch -1 (workloads/*/run_energy.py, analyze_power.py). Lines without a launch field (enercat) stay."""
    return [r for r in rows if r.get("launch", 0) >= 0]


def csv_tw(path):
    out = []
    for l in TU.lines(path):
        m = re.match(r"^(\d+),([0-9.]+)$", l.strip())
        if m:
            out.append((int(m.group(1)), float(m.group(2))))
    return out


def rb(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            return TU.read_bytes(p)
    return None


def load_pass(pdir, card):
    P = {"dir": pdir, "card": card, "pass": int(os.path.basename(pdir)[1:])}
    P["block"] = (TU.jl(os.path.join(pdir, "block.json")) or [{}])[0]
    P["marks"] = TU.jl(os.path.join(pdir, "marks.jsonl"))
    spans, open_ = collections.defaultdict(list), {}
    for m in P["marks"]:
        if m.get("ev") == "begin":
            open_[m["seg"]] = m["t_ms"]
        elif m.get("ev") == "end" and m["seg"] in open_:
            spans[m["seg"]].append((open_.pop(m["seg"]), m["t_ms"]))
    P["spans"] = spans
    recs = {}
    tr = os.path.join(pdir, "trace")
    for f in glob.glob(os.path.join(tr, "merged.spst*")) + glob.glob(os.path.join(tr, "*.done*")):
        for cyc, v in TU.spst_records(TU.read_bytes(f)):
            recs[cyc] = v
    P["spst"] = sorted(recs.items())
    P["extracts"] = TU.jl(os.path.join(tr, "extracts.jsonl"))
    for arm in ("E10", "E20", "E40"):
        P[arm] = sorted(TU.jl(os.path.join(pdir, arm.lower() + ".jsonl")), key=lambda s: s["t_ms"])
    P["PWR"] = csv_tw(os.path.join(pdir, "pwr.csv"))
    P["L10"] = csv_tw(os.path.join(pdir, "l10.csv"))
    P["reset"] = sorted(TU.jl(os.path.join(pdir, "reset.jsonl")), key=lambda s: s["t_ms"])
    P["bursts"] = tagged(os.path.join(pdir, "burst.jsonl"))
    g = os.path.join(pdir, "gov")
    P["sp0"], P["sp1"] = rb(os.path.join(g, "sp0.bin")), rb(os.path.join(g, "sp1.bin"))
    P["config"] = (TU.jl(os.path.join(g, "config.json")) or [None])[0]
    P["driver"] = TU.jl(os.path.join(g, "driver.json"))
    P["gov_runs"] = tagged(os.path.join(g, "runs.jsonl"))
    P["fw"] = "\n".join(TU.lines(os.path.join(g, "fw.txt")))
    try:
        P["die_block_start"] = int(open(os.path.join(g, "die_block_start.txt")).read().strip())
    except (OSError, ValueError):
        P["die_block_start"] = None
    dah = TU.jl(os.path.join(g, "die_after_heat.json"))
    P["die_after_heat"] = dah[0].get("die_c") if dah else None
    P["idle_clock"] = TU.jl(os.path.join(pdir, "idle_clock.jsonl"))
    d = os.path.join(pdir, "dbg")
    P["caps"] = {n: rb(os.path.join(d, n + ".bin")) for n in ("x2-idle", "x2-load", "x2-after", "x3-w1", "x3-w2", "x3-w3", "x3-w4")}
    P["wins"] = {k: sorted(TU.jl(os.path.join(d, "x3-w%d.jsonl" % k)), key=lambda s: s["t_ms"]) for k in (1, 2, 3, 4)}
    P["dbg_runs"] = tagged(os.path.join(d, "runs.jsonl"))
    return P


def load(root):
    out, notes = {}, []
    PRESENT.clear()
    PRESENT.update(c for c in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, c, "tel")))
    for c in sorted(PRESENT):
        if c not in ALL:
            ALL.append(c)
    for card in ALL:
        out[card] = []
        for pdir in sorted(glob.glob(os.path.join(root, card, "tel", "p*"))):
            if not re.fullmatch(r"p\d+", os.path.basename(pdir)):
                continue
            P = load_pass(pdir, card)
            if P["block"].get("status") != "ok":
                notes.append("%s %s: block status %r, pass not used" % (card, os.path.basename(pdir), P["block"].get("status")))
                continue
            out[card].append(P)
        out[card].sort(key=lambda P: P["pass"])
    return out, notes


def mhz_bad(samples, lo=None, hi=None):
    """aifoundry2 drop rule: any sample (inside [lo, hi] ms if given) with mhz.minion != 600."""
    for s in samples:
        if lo is not None and not (lo <= s["t_ms"] <= hi):
            continue
        m = s.get("mhz", {}).get("minion")
        if m is not None and m != 600:
            return True
    return False


def mhz_of(s):
    return (s.get("mhz") or {}).get("minion")


def mhz_count(vals):
    c = collections.Counter(v for v in vals if v is not None)
    return {str(k): c[k] for k in sorted(c)}


def mode(vals):
    vals = [v for v in vals if v is not None]
    return collections.Counter(vals).most_common(1)[0][0] if vals else None


def burst_clock_bad(card, R, lo, hi):
    """The clock rule for one burst [lo, hi] (host ms) over samples R: aifoundry2's registered rule (any sample in
    [lo, hi] off 600 MHz); a new governor-free card: busy samples only, in [lo + 500 ms, hi] (its first samples may
    still read the idle state's clock, 300 MHz on aifoundry1-c0); aifoundry3: none."""
    r = clock_rule(card)
    if r == "a2":
        return mhz_bad(R, lo, hi)
    if r == "busy":
        return mhz_bad(R, lo + SETTLE_MS, hi)
    return False


def burst_clock(R, lo, hi):
    """Where the clock was around one burst: the idle bracket before it, the ramp to 600 MHz, and the return to the
    idle bracket's clock after it when that is not 600 MHz (reported; no rule uses it)."""
    pre = mode(mhz_of(s) for s in R if lo - 3000 <= s["t_ms"] <= lo - 200)
    first = next((s["t_ms"] for s in R if lo <= s["t_ms"] <= hi and mhz_of(s) == 600), None)
    back = None
    if pre is not None and pre != 600:
        back = next((s["t_ms"] - hi for s in R if s["t_ms"] > hi and mhz_of(s) == pre), None)
    return {"idle_mhz_before": pre, "ramp_to_600_ms": None if first is None else first - lo,
            "busy_mhz": mhz_count(mhz_of(s) for s in R if lo <= s["t_ms"] <= hi), "back_to_idle_clock_ms": back}


def idle_readouts(P):
    """block.sh's idle-clock readouts (ettelem config with no sampler running), by label."""
    out = {}
    for r in P.get("idle_clock", []):
        c = r.get("config") or {}
        out[r.get("label")] = {"minion_mhz": c.get("minion_mhz"), "power_state_name": c.get("power_state_name"),
                               "minion_mv": c.get("minion_mv")}
    return out


def debug_idle_mhz(P):
    """The clock of the DEBUG block's idle state (the x2-idle capture): the 'debug' readout, else the X3 windows' idle
    samples (before each load burst, and the idle window)."""
    rows = [r for r in P.get("idle_clock", []) if str(r.get("label", "")).startswith("debug")
            and (r.get("config") or {}).get("minion_mhz") is not None]
    if rows:                                   # the last readout: after a wake launch (aifoundry1), if there was one
        return rows[-1]["config"]["minion_mhz"], "readout"
    vals = []
    for k in (1, 2, 3, 4):
        run = P["dbg_runs"].get("W%d" % k, [])
        lo = min((r["t_start_ms"] for r in run if "t_start_ms" in r), default=None)
        vals += [mhz_of(s) for s in P["wins"][k] if k == 4 or (lo is not None and s["t_ms"] < lo)]
    m = mode(vals)
    return m, ("x3 idle samples" if m is not None else "none")


def idle_ref_elsewhere(P):
    """A new governor-free card whose DEBUG-block idle state is not at 600 MHz: its idle capture sits at another
    operating point than its load captures, so Q4 and R6 (load against the idle reference) are reported, not tested."""
    m, _ = debug_idle_mhz(P)
    return clock_rule(P["card"]) == "busy" and m is not None and m != 600


def idle_summary(D, card):
    """Each card's idle clock, for the items that measure energy over idle or against an idle reference: the idle arms
    (E arms and the 'arms' readouts), the reset segment's idle brackets, and the DEBUG block's idle state."""
    rows, states = [], set()
    where = {"arms": set(), "reset brackets": set(), "DEBUG block": set()}
    for P in D.get(card, []):
        rd = idle_readouts(P)
        B = burst_spans(P)
        pre = [mhz_of(s) for b in B for s in P["reset"] if b["lo"] - 3000 <= s["t_ms"] <= b["lo"] - 200]
        arms = {a: mhz_count(mhz_of(s) for s in P[a]) for a in ("E10", "E20", "E40")}
        dm, src = debug_idle_mhz(P)
        wakes = sum(1 for k in rd if "+wake" in str(k))
        rows.append({"pass": P["pass"], "readouts": rd, "reset_idle_brackets_mhz": mhz_count(pre), "E_arms_mhz": arms,
                     "debug_idle_mhz": dm, "debug_idle_source": src, "wake_launches": wakes})
        where["arms"].update(int(k) for a in arms.values() for k in a)
        where["arms"].update(v["minion_mhz"] for k, v in rd.items() if k in ("start", "arms", "arms_end") and v["minion_mhz"] is not None)
        where["reset brackets"].update(v for v in pre if v is not None)
        if dm is not None:
            where["DEBUG block"].add(dm)
        states.update(v["power_state_name"] for v in rd.values() if v.get("power_state_name"))
    seen = sorted(set().union(*where.values()))
    nw = sum(r["wake_launches"] for r in rows)
    if not rows:
        note = "no data"
    elif not seen:
        note = "idle clock not recorded"
    elif seen == [600]:
        note = "idle at 600 MHz (%s)" % (", ".join(sorted(states)) or "state not read")
    else:
        note = "idle clock: %s MHz (%s); not the 600 MHz of its bursts%s" % (
            "; ".join("%s %s" % (k, "/".join(str(x) for x in sorted(v)) or "?") for k, v in where.items()),
            ", ".join(sorted(states)) or "state not read", "; %d wake launches" % nw if nw else "")
    return {"passes": rows, "idle_mhz_seen": seen, "idle_mhz_by_phase": {k: sorted(v) for k, v in where.items()},
            "power_states_seen": sorted(states), "idle_not_600": bool(seen) and seen != [600], "wake_launches": nw, "note": note}


# ------------------------------------------------------------------------------------------------ SP stats trace
def sp_key_rec(v):
    return (v[0][0], v[1][0], v[2][0], v[3][0])


def sp_key_sample(s):
    sp = s.get("sp")
    if not sp:
        return None
    return (int(round(sp["minion_w"][0] * 1000)), int(round(sp["sram_w"][0] * 1000)), int(round(sp["noc_w"][0] * 1000)),
            int(round(sp["board_avg_w"] * 100)))


def align(P):
    """Offset (ms) with host_ms = sp_us / 1000 + offset. Each ettelem sample carries the SP's current rail and board
    averages, which the SP also writes into that pass's stats record; the offset that makes each sample show the
    latest record before it (most samples matching exactly) is the alignment. One estimate per ettelem arm (E10, E20,
    E40); fallback: the extract-time anchor (host time of an extract minus its last record)."""
    recs = P["spst"]
    res = {"arms": {}, "anchors": []}
    for x in P["extracts"]:
        inf = x.get("info", {})
        if inf.get("n", 0) > 0 and inf.get("max_us"):
            res["anchors"].append(r3(x["t_begin_ms"] - inf["max_us"] / 1000.0, 1))
    if len(recs) < 50:
        res.update(offset=None, method="none", note="fewer than 50 SP stats records")
        return res
    c = np.array([r[0] for r in recs], dtype=np.float64) / 1000.0
    keys = [sp_key_rec(r[1]) for r in recs]
    ids = {}
    rid = np.array([ids.setdefault(k, len(ids)) for k in keys])
    where = collections.defaultdict(list)
    for i, k in enumerate(keys):
        where[k].append(i)
    for arm in ("E10", "E20", "E40"):
        S = [s for s in P[arm] if sp_key_sample(s) is not None]
        if len(S) < 20:
            continue
        ts = np.array([s["t_ms"] + s.get("took_ms", 0) / 3.0 for s in S], dtype=np.float64)
        sk = [sp_key_sample(s) for s in S]
        sid = np.array([ids.get(k, -1) for k in sk])
        cand = [t - c[j] for t, k in zip(ts, sk) for j in where.get(k, ())[:40]]
        if not cand:
            continue
        cand = np.array(cand)
        b = np.floor(cand / 100.0)
        u, n = np.unique(b, return_counts=True)
        centre = u[np.argmax(n)] * 100.0 + 50.0
        grid = np.arange(centre - 400.0, centre + 400.0, 1.0)
        score = np.empty(len(grid))
        for gi, off in enumerate(grid):
            j = np.searchsorted(c + off, ts, side="right") - 1
            ok = (j >= 0) & (rid[np.clip(j, 0, None)] == sid)
            score[gi] = ok.mean()
        best = score.max()
        plateau = grid[score >= best - 1e-12]
        res["arms"][arm] = {"offset": r3(float(np.median(plateau)), 1), "match": r3(best), "samples": len(S)}
    good = [v["offset"] for v in res["arms"].values() if v["match"] is not None and v["match"] >= 0.5]
    if good:
        res.update(offset=float(np.median(good)), method="sample-record match",
                   spread_ms=r3(max(good) - min(good), 1))
    elif res["anchors"]:
        res.update(offset=float(np.median(res["anchors"])), method="extract anchor (+-1 s)")
    else:
        res.update(offset=None, method="none")
    return res


def seg_ivals(h, dc, a, b):
    """SP pass intervals (ms) with both records inside [a + 1 s, b - 1 s] (host ms); gaps > 1 s are lost records."""
    m = (h[:-1] >= a + TRIM) & (h[1:] <= b - TRIM)
    d = dc[m]
    return d[(d > 0) & (d < 1000.0)]


def quiet_names(spans):
    return [k for k in spans if k in ("Q0", "Q") or k.startswith("G_") or k.startswith("W_")]


def sp_pass_values(P):
    out = {"pass": P["pass"], "align": align(P), "seg": {}, "Qseg": {}, "drops": [],
           "idle_mhz": {a: mhz_count(mhz_of(s) for s in P[a]) for a in ("E10", "E20", "E40")}}
    off = out["align"]["offset"]
    if off is None or len(P["spst"]) < 2:
        out.update(Q=None)
        for arm in ("PWR", "L10", "E10", "E20", "E40", "VOLT"):
            out[arm] = None
        return out
    c = np.array([r[0] for r in P["spst"]], dtype=np.float64) / 1000.0
    h = c + off
    dc = np.diff(c)
    pooled = []
    for name in quiet_names(P["spans"]):
        for i, (a, b) in enumerate(P["spans"][name]):
            d = seg_ivals(h, dc, a, b)
            key = name if i == 0 else "%s#%d" % (name, i + 1)
            out["Qseg"][key] = r3(float(np.median(d)), 2) if len(d) >= 20 else None
            pooled.extend(d.tolist())
    out["Q"] = r3(float(np.median(pooled)), 2) if len(pooled) >= 20 else None
    out["Q_n"] = len(pooled)
    for arm in ("PWR", "L10", "E10", "E20", "E40", "VOLT"):
        if arm in ("E10", "E20", "E40") and P[arm]:
            a, b = P[arm][0]["t_ms"], P[arm][-1]["t_ms"]
            if clock_rule(P["card"]) == "a2" and mhz_bad(P[arm]):   # idle arms: aifoundry2's registered rule only
                out["drops"].append("%s: a sample off 600 MHz" % arm)
                out[arm] = None
                continue
        elif P["spans"].get(arm):
            a, b = P["spans"][arm][0]
        else:
            out[arm] = None
            continue
        d = seg_ivals(h, dc, a, b)
        out["seg"][arm] = {"n": int(len(d)), "median": r3(float(np.median(d)), 2) if len(d) else None}
        out[arm] = r3(float(np.median(d)), 2) if len(d) >= 20 else None
    return out


# ------------------------------------------------------------------------------------------------ refresh fits (TEL-S)
def refresh_fit(cnt, dt, qs, kmax, rounded=False):
    """The periodic-refresh model of v13_refresh.py / v13b_powercsv.py: a refresh every P ms (100-400, 0.5 ms grid),
    each changing the reported value with probability q; the gap after k periods spans floor(kP/dt) or +1 polls, the
    latter with probability frac(kP/dt). Minimum multinomial negative log-likelihood over the grid, scanned in the
    scripts' order (P outer, q inner, strict <); rounded=True keeps v13b's quirk of storing the best as round(nll, 1)."""
    bins = sorted(cnt)
    n = np.array([cnt[b] for b in bins], float)
    P = np.arange(200, 801) / 2.0
    K = np.arange(1, kmax + 1)
    x = K[None, :] * P[:, None] / dt
    f = np.floor(x)
    fr = x - f
    A = np.zeros((len(P), kmax, len(bins)))
    for bi, b in enumerate(bins):
        A[:, :, bi] = np.where(f == b, 1 - fr, 0.0) + np.where(f + 1 == b, fr, 0.0)
    q = np.array(qs)
    W = q[:, None] * (1 - q[:, None]) ** (K[None, :] - 1)
    pr = np.einsum("pkb,qk->pqb", A, W)
    nll = -(np.log(np.maximum(pr, 1e-12)) * n[None, None, :]).sum(axis=2)
    best = None
    for i in range(len(P)):
        for j, v in enumerate(nll[i].tolist()):
            if best is None or v < best[0]:
                best = (round(v, 1) if rounded else v, i, j)
    _, i, j = best
    return float(P[i]), float(q[j]), float(nll[i, j])


def fit_ettelem10(S):
    """P_H: v13_refresh.py's rules (10 Hz poll: >= 500 samples, median poll 90-110 ms, intervals over polls of
    90-110 ms, <= 12 polls, >= 150 intervals; q 0.50-0.99, k <= 12)."""
    t = [s["t_ms"] for s in S if "board_w" in s]
    b = [s["board_w"] for s in S if "board_w" in s]
    if len(t) < 500:
        return None, "fewer than 500 samples"
    dts = sorted(y - x for x, y in zip(t, t[1:]))
    if not 90 <= dts[len(dts) // 2] <= 110:
        return None, "median poll not 90-110 ms"
    ch = [i for i in range(1, len(b)) if b[i] != b[i - 1]]
    cnt = collections.Counter()
    for i, j in zip(ch, ch[1:]):
        if all(90 <= t[k + 1] - t[k] <= 110 for k in range(i, j)) and j - i <= 12:
            cnt[j - i] += 1
    if sum(cnt.values()) < 150:
        return None, "fewer than 150 intervals"
    P, q, _ = refresh_fit(cnt, 100.0, [x / 100 for x in range(50, 100)], 12)
    return P, "n=%d q=%.2f" % (sum(cnt.values()), q)


def fit_any_poll(t, w):
    """P_L and P_H2: v13b_powercsv.py's rules (poll dt = median, intervals over polls within +-10 ms of it; q
    0.50-1.00, k <= 14); >= 30 intervals."""
    if len(t) < 50:
        return None, "fewer than 50 polls"
    d = [b - a for a, b in zip(t, t[1:])]
    dt = st.median(d)
    ch = [i for i in range(1, len(w)) if w[i] != w[i - 1]]
    cnt = collections.Counter()
    for i, j in zip(ch, ch[1:]):
        if all(abs(d[k] - dt) <= 10 for k in range(i, j)):
            cnt[j - i] += 1
    if sum(cnt.values()) < 30:
        return None, "fewer than 30 intervals"
    P, q, _ = refresh_fit(cnt, float(dt), [x / 100 for x in range(50, 101)], 14, rounded=True)
    return P, "n=%d dt=%.0f q=%.2f" % (sum(cnt.values()), dt, q)


# ------------------------------------------------------------------------------------------------ reset windows (P6, P7)
def windows(R, reset_ms=1000):
    """Windows of an ettelem --reset-ms log: a window closes at the sample whose since_reset_ms >= reset_ms (the reset
    follows that sample's reads), so that sample's min/max cover the whole window."""
    W, start = [], (R[0]["t_ms"] if R else None)
    for s in R:
        if s.get("since_reset_ms", -1) >= reset_ms:
            W.append({"start": start, "end": s["t_ms"], "close": s})
            start = s["t_ms"] + s.get("took_ms", 0)
    return W


def burst_spans(P):
    out = []
    for tag, rows in P["bursts"].items():
        rows = [r for r in rows if "t_start_ms" in r]
        if rows:
            out.append({"tag": tag, "lo": min(r["t_start_ms"] for r in rows), "hi": max(r["t_end_ms"] for r in rows), "runs": rows})
    return sorted(out, key=lambda b: b["lo"])


def p6_pass(P, E10):
    R, res = [s for s in P["reset"] if "sp" in s], {"pass": P["pass"]}
    if len(R) < 20:
        res["holds"] = None
        res["why"] = "no reset log"
        return res
    sr = [s.get("since_reset_ms", -1) for s in R]
    closers = [i for i, v in enumerate(sr) if v >= 1000]
    cyc_ok = (min(sr) >= 0 and len(closers) >= 3 and all(sr[i] <= 1300 for i in closers)
              and all(sr[i + 1] < 200 for i in closers if i + 1 < len(sr)))
    res["since_reset"] = {"min": min(sr), "max": max(sr), "windows": len(closers), "cycles_0_1000": cyc_ok}
    W = windows(R)
    B = burst_spans(P)
    fails = []
    if not cyc_ok:
        fails.append("since_reset_ms does not cycle 0-1000")
    if not B:
        res["holds"] = None
        res["why"] = "no bursts"
        return res
    last_hi = B[-1]["hi"]
    late_from = last_hi
    if clock_rule(P["card"]) == "busy":
        # a new governor-free card: if the idle clock changes after the last burst (the card entering its low-power idle
        # state), the rail steps again there, so the late windows start >= 8 s after that change instead (amendment TEL-4C)
        post = [s for s in R if s["t_ms"] > last_hi and mhz_of(s) is not None]
        ch = [b["t_ms"] for a, b in zip(post, post[1:]) if mhz_of(a) != mhz_of(b)]
        if ch:
            late_from = ch[-1]
            res["idle_clock_change_after_last_burst_ms"] = ch[-1] - last_hi
    late = [w for w in W if w["start"] >= late_from + 8000]
    late_undecided = not late and late_from > last_hi
    spans = [r3(w["close"]["sp"]["minion_w"][2] - w["close"]["sp"]["minion_w"][1]) for w in late]
    res["late_windows_max_minus_min_w"] = spans
    if late_undecided:
        pass
    elif not late:
        fails.append("no complete 1 s window >= 8 s after the last burst")
    elif max(spans) > 1.0:
        fails.append("a late window spans %.3f W > 1.0 W" % max(spans))
    first, dropped_all = [], False
    for b in B:
        if burst_clock_bad(P["card"], R, b["lo"], b["hi"]):
            first.append({"burst": b["tag"], "dropped": "a sample off 600 MHz" if P["card"] == A2 else "a busy sample off 600 MHz",
                          "clock": burst_clock(R, b["lo"], b["hi"])})
            continue
        pre = [s["sp"]["minion_w"][0] for s in R if b["lo"] - 3000 <= s["t_ms"] <= b["lo"] - 200]
        dur = [s["sp"]["minion_w"][0] for s in R if b["lo"] <= s["t_ms"] <= b["hi"] + 1000]
        w = [w for w in W if w["start"] <= b["lo"] + 1000 <= w["end"]]
        if not pre or not dur or not w:
            first.append({"burst": b["tag"], "dropped": "no idle, busy or window samples"})
            continue
        idle = st.median(pre)
        step = max(dur) - idle
        mx = w[0]["close"]["sp"]["minion_w"][2]
        first.append({"burst": b["tag"], "idle_w": r3(idle), "step_w": r3(step), "window_max_w": r3(mx),
                      "holds": mx >= idle + 0.5 * step, "clock": burst_clock(R, b["lo"], b["hi"])})
    res["first_second"] = first
    kept = [x for x in first if "holds" in x]
    if not kept:
        dropped_all = True                  # every burst dropped (off 600 MHz, no samples): the pass cannot decide P6
    elif not all(x["holds"] for x in kept):
        fails.append("a first-second window max below idle + 50% of the step")
    if E10 is None or len(E10) < 20:
        fails.append("no E10 log for the no-reset test")
        res["e10_max_never_falls"] = None
    else:
        mx = [s["sp"]["minion_w"][2] for s in E10 if "sp" in s]
        falls = sum(1 for a, b in zip(mx, mx[1:]) if b < a)
        res["e10_max_never_falls"] = falls == 0
        if falls:
            fails.append("E10 (no reset): the max falls %d times" % falls)
    res["fails"] = fails
    res["holds"] = not fails
    if dropped_all and not fails:
        res["holds"] = None
        res["why"] = "every burst dropped from the first-second test (a2 600 MHz rule or no samples): pass not used"
    elif late_undecided and not fails:
        res["holds"] = None
        res["why"] = "no complete window >= 8 s after the idle-clock change that followed the last burst: pass not used"
    return res


def p7_bursts(P):
    """f(1 s) per burst, the catalogue's definition (analyze_catalogue bursts_of + rail_fall_curves), on the reset log."""
    R = [s for s in P["reset"] if all(k in s for k in ("board_w", "sp", "temp_c", "mhz"))]   # samples with every read
    B = burst_spans(P)
    out = []
    if len(R) < 50 or not B:
        return out
    runs = []
    for i, b in enumerate(B):
        for r in b["runs"]:
            r = dict(r)
            r.update(cfg="fmadd_ps/random/h2", **{"pass": i})
            runs.append(r)
    try:
        bursts, arrays, spans = AC.bursts_of(R, runs)
    except (KeyError, ValueError, IndexError) as e:
        return [{"dropped": "bursts_of failed: %s" % e}]
    for b in bursts:
        tag = B[b["pass"]]["tag"]
        lo, hi = B[b["pass"]]["lo"], B[b["pass"]]["hi"]
        clk = burst_clock(R, lo, hi)
        if burst_clock_bad(P["card"], R, lo, hi):
            out.append({"pass": P["pass"], "burst": tag, "dropped": "a sample off 600 MHz" if P["card"] == A2 else "a busy sample off 600 MHz",
                        "clock": clk})
            continue
        cv = AC.rail_fall_curves([b], arrays, spans)
        if not cv:
            out.append({"pass": P["pass"], "burst": tag, "dropped": "outside the catalogue rule (> 8 W, >= 4 s idle each side)", "clock": clk})
            continue
        out.append({"pass": P["pass"], "burst": tag, "f1": r3(cv[0][int(np.argmin(np.abs(AC.RF_S - 1.0)))]),
                    "minion_over_w": r3(b["rails_over"]["minion_w"]), "clock": clk})
    return out


# ------------------------------------------------------------------------------------------------ DEBUG captures (Q, R)
def plane(vals):
    """x2_reduce.plane(): R^2 of a plane over the 32 grid shires and its permutation p (20,000 shuffles, seed 1)."""
    X = np.array([[1, *LAY[s]] for s in LAY], float)
    y = np.array([vals[s] for s in LAY], float)
    H = X @ np.linalg.pinv(X)

    def r2(Y):
        Y = np.atleast_2d(Y)
        res = Y - Y @ H.T
        sst = ((Y - Y.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
        out = np.where(sst > 0, 1 - (res ** 2).sum(axis=1) / np.where(sst > 0, sst, 1), 0.0)
        return out
    obs = float(r2(y)[0])
    rng = np.random.default_rng(1)
    perms = np.array([rng.permutation(y) for _ in range(20000)])
    ge = int((r2(perms) >= obs - 1e-12).sum())
    return {"r2": round(obs, 3), "p_perm": round((ge + 1) / 20001, 4)}


def cap_info(buf):
    if not buf:
        return None
    import io
    err = io.StringIO()
    m = vparse(buf, warn=err)
    ents = ring_entries(buf)
    full = "no pass has all" not in err.getvalue() and len(m) == 34
    return {"map": m, "shires": len(m), "full_pass": full, "temp_lines": len(re.findall(rb"Temp \[C\]", buf)),
            "mem_lines": len(re.findall(rb"MEM \d+ Voltage", buf)), "ring": ents is not None}


def x3_window(rows):
    """x3_reduce.py's per-window figures, unchanged."""
    f = lambda r: (r["t_ms"] / 1000, r["temp_c"]["minshire"][0], r["temp_c"]["minshire"][1], r["temp_c"]["minshire"][2],
                   r["sp"]["minion_c"][1], r["sp"]["minion_c"][2])
    R = [f(r) for r in rows if "temp_c" in r and "sp" in r]
    if len(R) < 5:
        return None
    t0 = R[0][0]
    first = [x for x in R if x[0] - t0 <= 1.0]
    reset_ok = all(x[2] >= x[1] - 2 and x[3] <= x[1] + 3 for x in first)
    rises = [R[i][3] - R[i][1] for i in range(1, len(R)) if R[i][3] > R[i - 1][3]]
    e = R[-1]
    return {"n": len(R), "reset_ok": reset_ok, "end_high_minus_spmax": e[3] - e[5], "end_low_minus_spmin": e[2] - e[4],
            "rise_excess": rises}


# ------------------------------------------------------------------------------------------------ items
def item(name, claims, pc, test, outcome, reading, **kw):
    d = {"item": name, "claims": claims, "per_card": pc, "test": test, "outcome": outcome, "reading": reading}
    d.update(kw)
    return d


def na(card):
    return {"status": "not registered", "n": 0, "note": "the item names the other card only"}


def p1_rows(SPVc):
    rows = [v for v in SPVc if v["Q"] is not None]
    return [{"pass": v["pass"], "Q_ms": v["Q"], "quiet_segment_medians": v["Qseg"],
             "in_band": all(131.6 <= m <= 135.6 for m in v["Qseg"].values() if m is not None) and any(m is not None for m in v["Qseg"].values())}
            for v in rows]


def p2_rows(SPVc):
    rows = [v for v in SPVc if v["Q"] is not None and v["PWR"] is not None]
    return [{"pass": v["pass"], "PWR_ms": v["PWR"], "Q_ms": v["Q"], "diff_ms": r3(v["PWR"] - v["Q"], 2),
             "holds": abs(v["PWR"] - v["Q"]) <= 1.5} for v in rows]


def p3_card(SPVc):
    rows = [v for v in SPVc if v["Q"] is not None and v["E10"] is not None]
    per = [{"pass": v["pass"], "E10_ms": v["E10"], "Q_ms": v["Q"], "diff_ms": r3(v["E10"] - v["Q"], 2), "E40_ms": v.get("E40"),
            "E10_ge_145": v["E10"] >= 145, "diff_gt_8": v["E10"] - v["Q"] > 8,
            "E40_ge_E10": (v["E40"] >= v["E10"]) if v.get("E40") is not None else None} for v in rows]
    t = tstat([p["diff_ms"] for p in per], T1)
    lb = r3(t["mean"] - t["half"], 2) if t else None
    ok = bool(per) and all(p["E10_ge_145"] for p in per) and lb is not None and lb > 0
    d = {"n": len(per), "passes": per, "diff_one_sided_99_lower_ms": lb, "t": t,
         "parts_not_in_decision": {"E10_minus_Q_gt_8_every_pass": all(p["diff_gt_8"] for p in per) if per else None,
                                   "E40_ge_E10_every_pass": all(p["E40_ge_E10"] for p in per) if per and all(p["E40_ge_E10"] is not None for p in per) else None}}
    return d, ok, lb


def p4_card(SPVc):
    rows = [v for v in SPVc if v["Q"] is not None and v["VOLT"] is not None]
    d = [r3(v["VOLT"] - v["Q"], 2) for v in rows]
    t = tstat(d, T2)
    dec, ok = None, False
    if t and len(d) >= NEED:
        lo, hi = t["mean"] - t["half"], t["mean"] + t["half"]
        dec = "confirmed" if lo > 5 else ("rejected" if lo >= -1.5 and hi <= 1.5 else "not resolved")
        ok = dec == "confirmed"
    return d, t, dec, ok


def p5_card(SPVc):
    rows = [v for v in SPVc if v["Q"] is not None and v["E10"] is not None]
    per = [{"pass": v["pass"], "E10_ms": v["E10"], "Q_ms": v["Q"], "slow": 255 <= v["E10"] <= 272 and v["Q"] >= 230,
            "q_lt_160": v["Q"] < 160} for v in rows]
    dec = None
    if len(per) >= NEED:
        dec = ("the SP loop is slow" if all(p["slow"] for p in per) else
               "sampler-induced" if all(p["q_lt_160"] for p in per) else "reported as is")
    return per, dec


def items_sp(D, SPV):
    out = []
    NEW = new_cards()
    # TEL-P1
    per = p1_rows(SPV[A2])
    pc = {A2: {"n": len(per), "passes": per, "status": status_of(len(per), all(p["in_band"] for p in per))}, A3: na(A3)}
    oc = combine(pc, [A2])
    for c in NEW:
        pr = p1_rows(SPV[c])
        pc[c] = reported(len(pr), passes=pr, registered_band_met_every_pass=all(p["in_band"] for p in pr) if pr else None)
    out.append(item("TEL-P1", ["hub-034", "hub-127", "hub-003", "hub-069", "hub-117"], pc,
                    "aifoundry2: the median SP stats pass interval of every quiet segment in 131.6-135.6 ms, in every pass (3/3)",
                    oc, "aifoundry2 quiet SP pass: %s ms per pass (%s)" % ([p["Q_ms"] for p in per], oc),
                    all_cards=all_cards(pc, [A2]),
                    reading_all_cards="quiet SP pass per card (ms): %s; tested on aifoundry2 only" % {c: [p["Q_ms"] for p in pc[c].get("passes", [])] for c in [A2] + NEW}))
    # TEL-P2
    per = p2_rows(SPV[A2])
    pc = {A2: {"n": len(per), "passes": per, "status": status_of(len(per), all(p["holds"] for p in per))}, A3: na(A3)}
    oc = combine(pc, [A2])
    for c in NEW:
        pr = p2_rows(SPV[c])
        pc[c] = reported(len(pr), passes=pr, registered_band_met_every_pass=all(p["holds"] for p in pr) if pr else None)
    out.append(item("TEL-P2", ["hub-034"], pc, "aifoundry2: |PWR - Q| <= 1.5 ms in every pass (3/3)", oc,
                    "aifoundry2 single-command poll (~16 ms) moves the pass by %s ms (%s)" % ([p["diff_ms"] for p in per], oc),
                    all_cards=all_cards(pc, [A2]),
                    reading_all_cards="PWR - Q per card (ms): %s; tested on aifoundry2 only" % {c: [p["diff_ms"] for p in pc[c].get("passes", [])] for c in [A2] + NEW}))
    # TEL-P3
    d3, ok, lb = p3_card(SPV[A2])
    per = d3["passes"]
    d3["status"] = status_of(len(per), ok)
    pc = {A2: d3, A3: na(A3)}
    oc = combine(pc, [A2])
    for c in NEW:
        dc, okc, _ = p3_card(SPV[c])
        pc[c] = reported(dc.pop("n"), registered_rule_met=okc if dc["passes"] else None, **dc)
    out.append(item("TEL-P3", ["hub-034", "hub-127", "pt-spatial-01"], pc,
                    "aifoundry2: E10 >= 145 ms in every pass and the 99% one-sided t lower bound (df n-1) on paired E10 - Q > 0",
                    oc, "aifoundry2 pass under ettelem 10 Hz: %s ms, E10 - Q lower bound %s ms (%s)" % ([p["E10_ms"] for p in per], lb, oc),
                    all_cards=all_cards(pc, [A2]),
                    reading_all_cards="E10 per card (ms): %s; tested on aifoundry2 only" % {c: [p["E10_ms"] for p in pc[c].get("passes", [])] for c in [A2] + NEW}))
    # TEL-P4
    d, t, dec, ok = p4_card(SPV[A2])
    pc = {A2: {"n": len(d), "VOLT_minus_Q_ms": d, "t99": t, "decision": dec, "status": status_of(len(d), ok)}, A3: na(A3)}
    oc = combine(pc, [A2])
    for c in NEW:
        dc, tc, decc, _ = p4_card(SPV[c])
        pc[c] = reported(len(dc), VOLT_minus_Q_ms=dc, t99=tc, decision=decc)
    out.append(item("TEL-P4", ["hub-034"], pc,
                    "aifoundry2: 99% t interval (df n-1) on VOLT - Q: above 5 ms -> DM_CMD_GET_MODULE_VOLTAGE lengthens the pass "
                    "(PASS); inside +-1.5 ms -> rejected (FAIL); else not resolved (FAIL)", oc,
                    "aifoundry2 VOLT - Q %s ms: %s" % (d, dec or "insufficient"), decision=dec,
                    all_cards=all_cards(pc, [A2]),
                    reading_all_cards="VOLT - Q per card: %s; tested on aifoundry2 only" % {c: pc[c].get("decision") for c in [A2] + NEW}))
    # TEL-P5
    per, dec = p5_card(SPV[A3])
    pc = {A3: {"n": len(per), "passes": per, "decision": dec, "status": status_of(len(per), dec == "the SP loop is slow")}, A2: na(A2)}
    oc = combine(pc, [A3])
    for c in NEW:
        pr, decc = p5_card(SPV[c])
        pc[c] = reported(len(pr), passes=pr, decision=decc)
    out.append(item("TEL-P5", ["hub-070", "dvfs-19"], pc,
                    "aifoundry3: every pass E10 median 255-272 ms and quiet >= 230 ms -> 'the SP loop is slow' (PASS); quiet < 160 "
                    "ms in every pass -> sampler-induced; anything else reported as is", oc,
                    "aifoundry3 SP pass quiet %s / E10 %s ms: %s" % ([p["Q_ms"] for p in per], [p["E10_ms"] for p in per], dec or "insufficient"),
                    decision=dec, all_cards=all_cards(pc, [A3]),
                    reading_all_cards="SP pass quiet / E10 per card (ms): %s; tested on aifoundry3 only" % {
                        c: [(p["Q_ms"], p["E10_ms"]) for p in pc[c].get("passes", [])] for c in [A3] + NEW}))
    return out


def idle_notes():
    return {c: IDLE.get(c, {}).get("note") for c in ALL}


def items_reset(D):
    out, pc6, pc7 = [], {}, {}
    for card in ALL:
        rows = [p6_pass(P, P["E10"]) for P in D[card]]
        kept = [r for r in rows if r["holds"] is not None]
        pc6[card] = {"n": len(kept), "passes": rows, "status": status_of(len(kept), all(r["holds"] for r in kept))}
        B = [b for P in D[card] for b in p7_bursts(P)]
        f1 = [b["f1"] for b in B if "f1" in b]
        npass = len({b["pass"] for b in B if "f1" in b})
        med = r3(st.median(f1)) if f1 else None
        pc7[card] = {"n": npass, "bursts_kept": len(f1), "bursts": B, "median_f1": med,
                     "status": status_of(npass, med is not None and 0.45 <= med <= 0.68)}
    oc = combine(pc6, list(CARDS))
    ac = all_cards(pc6, ALL)
    out.append(item("TEL-P6", ["hub-037"], pc6,
                    "exact, 0 failures, every kept pass on each card: since_reset_ms cycles 0-1000; every complete 1 s window "
                    "starting >= 8 s after the last burst has sp.minion_w max - min <= 1.0 W; the window holding each burst's "
                    "first second has max >= idle + 50% of the burst's minion-rail step; in E10 (no reset) the max never falls",
                    oc, "--reset-ms windows: %s (rung 6 %s)" % (
                        {c: pc6[c]["status"] for c in CARDS}, "stands" if oc == "PASS" else "reads 'untested / not working'" if oc in ("FAIL", "CARD-DIFFERENT") else "undecided"),
                    all_cards=ac, idle_clock=idle_notes(),
                    reading_all_cards="--reset-ms windows on every card: %s (%s)" % (ac["status"], ac["outcome"])))
    oc = combine(pc7, list(CARDS))
    ac = all_cards(pc7, ALL)
    out.append(item("TEL-P7", ["hub-036"], pc7,
                    "median f(1 s) over the kept bursts per card (9 = 3 per pass) inside 0.45-0.68 (a restarted average gives >= 0.9)",
                    oc, "f(1 s) under 1 s resets: a2 %s, a3 %s (%s)" % (pc7[A2]["median_f1"], pc7[A3]["median_f1"], oc),
                    all_cards=ac, idle_clock=idle_notes(),
                    reading_all_cards="f(1 s) under 1 s resets per card: %s (%s)" % ({c: pc7[c]["median_f1"] for c in ALL}, ac["outcome"])))
    return out


def item_S(D):
    pc = {}
    bands = {A2: {"L": (131, 140), "H": (152, 160)}, A3: {"L": (200, 245), "H": (258, 268)}}
    ref = {A2: 156, A3: 263}
    for card in ALL:
        per = []
        for P in D[card]:
            pl, nl = fit_any_poll([x[0] for x in P["L10"]], [x[1] for x in P["L10"]])
            E10 = [s for s in P["E10"]]
            E20 = [s for s in P["E20"]]
            a2rule = clock_rule(card) == "a2"                      # the E arms are idle: aifoundry2's registered rule only
            ph, nh = fit_ettelem10(E10) if not (a2rule and mhz_bad(E10)) else (None, "E10 dropped: a sample off 600 MHz")
            ph2, nh2 = (fit_any_poll([s["t_ms"] for s in E20 if "board_w" in s], [s["board_w"] for s in E20 if "board_w" in s])
                        if not (a2rule and mhz_bad(E20)) else (None, "E20 dropped: a sample off 600 MHz"))
            row = {"pass": P["pass"], "P_L": pl, "P_H": ph, "P_H2": ph2, "fit_notes": [nl, nh, nh2]}
            if pl is not None and ph is not None:
                row["H_minus_L"] = r3(ph - pl, 2)
            b = bands.get(card, bands[A2])                          # a new card: aifoundry2's bands, reported only
            rf = ref.get(card, ref[A2])
            row["band_L"] = None if pl is None else b["L"][0] <= pl <= b["L"][1]
            row["band_H"] = None if ph is None else b["H"][0] <= ph <= b["H"][1]
            row["H2_ge_H_plus_10"] = None if ph is None or ph2 is None else ph2 >= ph + 10
            row["P_H_within_5_of_%d" % rf] = None if ph is None else abs(ph - rf) <= 5
            if card not in CARDS:
                row["E_arms_idle_mhz"] = {a: mhz_count(mhz_of(s) for s in P[a]) for a in ("E10", "E20")}
            per.append(row)
        d = [r["H_minus_L"] for r in per if "H_minus_L" in r]
        t = tstat(d, T2)
        excl = None
        if t:
            lo, hi = t["mean"] - t["half"], t["mean"] + t["half"]
            excl = "positive" if lo > 0 else ("negative" if hi < 0 else "includes 0")
        full = [r for r in per if r["band_L"] is not None and r["band_H"] is not None and r["H2_ge_H_plus_10"] is not None]
        pc[card] = {"n": len(d), "passes": per, "H_minus_L_t99": t, "interval": excl,
                    "S_bands_every_pass": all(r["band_L"] and r["band_H"] and r["H2_ge_H_plus_10"] for r in full) if full else None,
                    "status": status_of(len(d), excl == "positive")}
        if card not in CARDS:
            pc[card]["S_bands_from"] = "aifoundry2's (S1/S2 are registered for aifoundry2 and aifoundry3 only): reported, not tested"
    oc = combine(pc, list(CARDS))
    pages = {c: (None if pc[c]["status"] == "insufficient" else "per sampler" if pc[c]["interval"] == "positive" else
                 "ettelem figure only" if pc[c]["interval"] == "includes 0" and pc[c]["H_minus_L_t99"] and abs(pc[c]["H_minus_L_t99"]["mean"]) < 5
                 else "as measured") for c in ALL}
    ac = all_cards(pc, ALL)
    return item("TEL-S", ["pt-spatial-01", "pt-spatial-13", "pt-spatial-15", "pt-spatial-16", "dvfs-73", "anatomy-08", "anatomy-110",
                          "energy-manual-159", "heat-15", "horace-lowpower-129", "matmul-sparse-testdrive-32",
                          "matmul-sparse-testdrive-96", "memhier-onchip-110"], pc,
                "paired over the passes per card: P_H - P_L 99% t interval (df n-1) excludes 0 and is positive on both cards -> "
                "'the sampler lengthens the pass' PROVEN-BOTH; S1/S2 bands (a2 P_L 131-140, P_H 152-160; a3 P_L 200-245, "
                "P_H 258-268; P_H2 >= P_H + 10) reported per pass", oc,
                "board refresh P_L/P_H/P_H2 a2 %s, a3 %s ms; pages: %s (%s)" % (
                    [(r["P_L"], r["P_H"], r["P_H2"]) for r in pc[A2]["passes"]],
                    [(r["P_L"], r["P_H"], r["P_H2"]) for r in pc[A3]["passes"]], {c: pages[c] for c in CARDS}, oc), pages=pages,
                all_cards=ac, reading_all_cards="P_H - P_L 99%% interval per card: %s; pages %s (%s)" % (
                    {c: pc[c]["interval"] for c in ALL}, pages, ac["outcome"]))


def item_Q(D):
    pc, idle_mean = {}, {}
    for card in ALL:
        per, idle_vecs = [], []
        for P in D[card]:
            ci = {k: cap_info(v) for k, v in P["caps"].items()}
            if ci["x2-idle"] is None:
                continue
            row = {"pass": P["pass"], "captures": {k: None if v is None else {x: v[x] for x in ("shires", "full_pass", "temp_lines", "mem_lines")}
                                                     for k, v in ci.items()}}
            caps = [v for v in ci.values() if v is not None]
            row["Q1_temp_lines_0"] = all(v["temp_lines"] == 0 for v in caps)
            row["Q1_mem_only_after_sample"] = all(ci[k]["mem_lines"] == 0 for k in ("x2-idle", "x2-load", "x2-after") if ci[k])
            row["Q1_34_lines_parse"] = all(v["full_pass"] for v in caps)
            iv = np.array([ci["x2-idle"]["map"][s]["mnn"][0] for s in S34], float) if ci["x2-idle"]["shires"] == 34 else None
            if iv is not None:
                idle_vecs.append((P["pass"], iv))
            ghz = [r.get("ghz") for r in timed(P["dbg_runs"].get("X2", []))]
            # the launch clock is a busy measure: aifoundry2's rule, and the new governor-free cards'; not aifoundry3's
            x2_drop = clock_rule(card) is not None and (not ghz or not all(g is not None and 0.59 <= g <= 0.61 for g in ghz))
            if ci["x2-load"] and ci["x2-load"]["shires"] == 34 and iv is not None and not x2_drop:
                lv = np.array([ci["x2-load"]["map"][s]["mnn"][0] for s in S34], float)
                dd = (lv - lv.mean()) - (iv - iv.mean())
                row["Q4"] = {"common_shift_mv": r3(lv.mean() - iv.mean(), 2), "sd_dev_change_mv": r3(dd.std(ddof=1)),
                             "max_abs_dev_change_mv": r3(abs(dd).max(), 2)}
                if idle_ref_elsewhere(P):
                    row["Q4"]["reported_only"] = "the idle capture is at %s MHz, the load at 600 MHz: two operating points (amendment TEL-4C)" % debug_idle_mhz(P)[0]
            elif x2_drop:
                row["Q4"] = {"dropped": "X2 launch off 0.59-0.61 GHz (%s rule)" % ("aifoundry2" if card == A2 else "busy-clock")}
            if card not in CARDS:
                row["debug_idle_mhz"] = debug_idle_mhz(P)[0]
            q5 = {}
            for k in ("x2-idle", "x3-w4"):
                if ci[k] and ci[k]["shires"] == 34:
                    m = ci[k]["map"]
                    q5[k + "|mnn_now"] = plane({s: m[s]["mnn"][0] for s in LAY})
                    if k == "x2-idle":
                        q5[k + "|sram_now"] = plane({s: m[s]["sram"][0] for s in LAY})
            row["Q5"] = q5
            per.append(row)
        n = len(per)
        pairs = {}
        for (pa, a), (pb, b) in [(x, y) for i, x in enumerate(idle_vecs) for y in idle_vecs[i + 1:]]:
            pairs["p%d~p%d" % (pa, pb)] = r3(float(np.corrcoef(a, b)[0, 1]))
        q2 = (all(v is not None and v >= 0.6 for v in pairs.values()) if len(idle_vecs) >= NEED else None)
        q4rows = [r["Q4"] for r in per if "Q4" in r and "sd_dev_change_mv" in r["Q4"] and "reported_only" not in r["Q4"]]
        q4rep = [r["Q4"] for r in per if "Q4" in r and "reported_only" in r["Q4"]]
        q4_not_tested = card not in CARDS and bool(q4rep) and not q4rows      # every pass's idle capture elsewhere
        t = tstat([r["sd_dev_change_mv"] for r in q4rows], T2)
        q4_ub = r3(t["mean"] + t["half"]) if t else None
        q4 = (q4_ub <= 0.5) if q4_ub is not None and len(q4rows) >= NEED else None
        q4_parts = {"common_fall_1_3_every_pass": all(-3 <= r["common_shift_mv"] <= -1 for r in q4rows) if q4rows else None,
                    "max_abs_dev_change_le_1_every_pass": all(r["max_abs_dev_change_mv"] <= 1 for r in q4rows) if q4rows else None}
        q5_min = all(v["p_perm"] >= 0.0042 for r in per for k, v in r["Q5"].items() if "mnn_now" in k) if per else None
        q5_sram = sum(1 for r in per if r["Q5"].get("x2-idle|sram_now", {}).get("p_perm", 1) < 0.0042)
        q5 = bool(q5_min) and (card != A2 or q5_sram >= 2)
        q1 = bool(per) and all(r["Q1_temp_lines_0"] and r["Q1_mem_only_after_sample"] for r in per) and \
            (card != A3 or all(r["Q1_34_lines_parse"] for r in per))
        if idle_vecs:
            idle_mean[card] = np.mean([v for _, v in idle_vecs], axis=0)
        if q4_not_tested:
            ok = q1 and q2 and q5
            n_eff = min(n, len(idle_vecs))
        else:
            ok = q1 and q2 and q4 and q5
            n_eff = min(n, len(idle_vecs), len(q4rows))
        pc[card] = {"n": n, "passes": per, "Q1": q1, "Q2_pairs_r": pairs, "Q2": q2, "Q4_sd_99_upper_mv": q4_ub, "Q4_t": t, "Q4": q4,
                    "Q4_parts_not_in_decision": q4_parts, "Q5_minion_now_no_plane": q5_min,
                    "Q5_sram_gradient_passes": q5_sram if card != A3 else None, "Q5": q5,
                    "status": status_of(n_eff, ok)}
        if card not in CARDS:
            pc[card]["reported_parts"] = {"Q1_34_lines_parse_every_pass": all(r["Q1_34_lines_parse"] for r in per) if per else None,
                                          "Q5_sram_gradient_passes": q5_sram,
                                          "note": "Q1's 34-line parse (aifoundry3) and Q5's SRAM gradient (aifoundry2) are reported, not tested"}
            if q4_not_tested:
                pc[card]["Q4"] = "not tested"
                pc[card]["Q4_reported"] = q4rep
    q3r = r3(float(np.corrcoef(idle_mean[A2], idle_mean[A3])[0, 1])) if A2 in idle_mean and A3 in idle_mean else None
    q3 = None if q3r is None else abs(q3r) < 0.45
    oc = combine(pc, list(CARDS))
    if oc == "PASS" and q3 is False:
        oc = "FAIL"
    q24 = [pc[c][k] for c in CARDS for k in ("Q2", "Q4")]
    offset = "kept" if all(x is True for x in q24) else ("dropped" if any(x is False for x in q24) else "undecided")
    # all cards: Q3 over every pair of cards, the offset sentence over every card's Q2 and tested Q4
    have = [c for c in ALL if c in idle_mean]
    q3_pairs = {"%s~%s" % (a, b): r3(float(np.corrcoef(idle_mean[a], idle_mean[b])[0, 1])) for i, a in enumerate(have) for b in have[i + 1:]}
    q3_all = (all(abs(v) < 0.45 for v in q3_pairs.values()) if len(have) == len(ALL) and len(have) >= 2 else None)
    ac = all_cards(pc, ALL, Q3_pairs_r=q3_pairs, Q3_holds_every_pair=q3_all)
    if ac["outcome"] == "PASS" and q3_all is False:
        ac["outcome"] = "FAIL"
    q24a = [pc[c][k] for c in ALL for k in ("Q2", "Q4") if pc[c][k] != "not tested"]
    ac["offset_sentence"] = "kept" if all(x is True for x in q24a) else ("dropped" if any(x is False for x in q24a) else "undecided")
    return item("TEL-Q", ["pt-spatial-10", "pt-spatial-12", "pt-spatial-46", "pt-spatial-47", "pt-spatial-48", "pt-spatial-49",
                          "pt-spatial-50", "pt-spatial-71", "hub-V04", "hub-012", "hub-025", "pt-spatial-61"], pc,
                "Q1 (a3: 34 'MS nn Voltage' lines parse; both: 0 'Temp [C]' lines, 'MEM n Voltage' only right after a sample); "
                "Q2 idle minion 'now' pattern r >= 0.6 for every pass pair; Q3 cross-card |r| < 0.45 (r >= 0.45 rejects per-chip "
                "offsets); Q4 99% upper bound (two-sided t, df n-1) of the pass-level sd of the deviation change <= 0.5 mV; Q5 minion "
                "'now' plane p >= 0.0042 in every idle capture, a2 SRAM 'now' p < 0.0042 in >= 2 of 3 passes. PASS needs all on both "
                "cards; Q2 or Q4 failing drops the offset sentence (pt-spatial-49)", oc,
                "voltage maps: Q2 %s, Q4 upper %s mV, Q3 r %s; offset sentence %s (%s)" % (
                    {c: pc[c]["Q2"] for c in CARDS}, {c: pc[c]["Q4_sd_99_upper_mv"] for c in CARDS}, q3r,
                    offset, oc),
                Q3_cross_card_r=q3r, Q3_holds=q3, offset_sentence=offset, all_cards=ac, idle_clock=idle_notes(),
                reading_all_cards="voltage maps on every card: Q2 %s, Q4 %s, Q3 every pair %s; offset sentence %s (%s)" % (
                    {c: pc[c]["Q2"] for c in ALL}, {c: pc[c]["Q4"] for c in ALL}, q3_all, ac["offset_sentence"], ac["outcome"]))


def item_R(D):
    pc = {}
    for card in ALL:
        per = []
        for P in D[card]:
            idle_cap = cap_info(P["caps"]["x2-idle"])
            idle_now = {s: idle_cap["map"][s]["mnn"][0] for s in S34} if idle_cap and idle_cap["shires"] == 34 else None
            elsewhere = idle_ref_elsewhere(P)
            wins = []
            for k in (1, 2, 3, 4):
                rows = P["wins"][k]
                w = x3_window(rows)
                if w is None:
                    continue
                w["window"] = k
                w["kind"] = "load" if k <= 3 else "idle"
                run = P["dbg_runs"].get("W%d" % k, [])
                lo = min((r["t_start_ms"] for r in run), default=None)
                hi = max((r["t_end_ms"] for r in run if "t_end_ms" in r), default=None)
                if card == A2 and mhz_bad(rows):
                    w["dropped"] = "a sample off 600 MHz"
                elif (clock_rule(card) == "busy" and w["kind"] == "load" and lo is not None and hi is not None
                      and burst_clock_bad(card, rows, lo, hi)):
                    w["dropped"] = "a busy sample off 600 MHz"          # the idle window and idle samples never drop here
                if card not in CARDS and w["kind"] == "load" and lo is not None and hi is not None:
                    w["clock"] = burst_clock(rows, lo, hi)
                if w["kind"] == "load":
                    cap = cap_info(P["caps"]["x3-w%d" % k])
                    if cap and cap["shires"] == 34 and idle_now and lo is not None:
                        below = sum(1 for s in S34 if cap["map"][s]["mnn"][1] <= idle_now[s] - 2)
                        pre = [r["die_mv"]["minion"] for r in rows if r["t_ms"] < lo and "die_mv" in r]
                        post = [r["die_mv"]["minion"] for r in rows if r["t_ms"] >= lo and "die_mv" in r]
                        if pre and post:
                            w["R6"] = {"lows_2mv_below_idle": below, "die_mv_fall": r3(st.median(pre) - min(post), 1)}
                wins.append(w)
            if not wins:
                continue
            kept = [w for w in wins if "dropped" not in w]
            load = [w for w in kept if w["kind"] == "load"]
            r6 = [w["R6"] for w in load if "R6" in w]
            row = {"pass": P["pass"], "windows": wins,
                   "R2_median": st.median([w["end_high_minus_spmax"] for w in load]) if load else None,
                   "R6": None if not r6 else {"median_lows_below": st.median([x["lows_2mv_below_idle"] for x in r6]),
                                              "median_die_mv_fall": st.median([x["die_mv_fall"] for x in r6])}}
            if row["R6"]:
                row["R6"]["holds"] = row["R6"]["median_lows_below"] >= 17 and row["R6"]["median_die_mv_fall"] <= 2.5
                if elsewhere:
                    row["R6"]["reported_only"] = ("the idle reference (x2-idle) is at %s MHz, the bursts at 600 MHz: two operating points "
                                                  "(amendment TEL-4C)" % debug_idle_mhz(P)[0])
            if card not in CARDS:
                row["debug_idle_mhz"] = debug_idle_mhz(P)[0]
            per.append(row)
        allw = [w for r in per for w in r["windows"] if "dropped" not in w]
        loadw = [w for w in allw if w["kind"] == "load"]
        idlew = [w for w in allw if w["kind"] == "idle"]
        R1 = all(w["reset_ok"] for w in allw) if allw else None
        vals = [w["end_high_minus_spmax"] for w in loadw]
        meds = [r["R2_median"] for r in per if r["R2_median"] is not None]
        if not vals:
            R2 = None
        elif not all(v in (2, 3, 4) for v in vals):
            R2 = "fails"
        elif all(m == 3 for m in meds):
            R2 = "holds"
        elif len(set(meds)) == 1:
            R2 = "own figure (%s)" % meds[0]
        else:
            R2 = "WITHIN-NOISE"
        rises = [x for w in loadw for x in w["rise_excess"]]
        R3 = (sum(1 for x in rises if x in (3, 4)) / len(rises) >= 0.8) if rises else None
        R4 = all(w["end_high_minus_spmax"] <= 2 for w in idlew) if idlew else None
        R5 = all(w["end_low_minus_spmin"] in (-1, -2) for w in allw) if allw else None
        r6p = [r["R6"]["holds"] for r in per if r["R6"] and "reported_only" not in r["R6"]]
        r6_not_tested = card not in CARDS and not r6p and any(r["R6"] and "reported_only" in r["R6"] for r in per)
        R6 = (sum(r6p) >= 2) if len(r6p) >= NEED else None
        parts = [R1, None if R2 is None else R2 == "holds", R3, R4, R5] + ([] if r6_not_tested else [R6])
        ok = all(x is True for x in parts)
        # a part that could not be computed (no kept window of its kind, fewer than 3 passes with an R6 figure) leaves the
        # card INSUFFICIENT unless another part has already failed
        n_eff = len(per) if (ok or False in parts) else min(len(per), NEED - 1)
        pc[card] = {"n": len(per), "passes": per, "R1_reset_resets_peak_hold": R1, "R2": R2,
                    "R3_share_3_or_4": r3(sum(1 for x in rises if x in (3, 4)) / len(rises)) if rises else None, "R3": R3,
                    "R4": R4, "R5": R5, "R6_passes_holding": sum(r6p), "R6": "not tested" if r6_not_tested else R6,
                    "status": status_of(n_eff, ok)}
    oc = combine(pc, list(CARDS))
    gate = {c: pc[c]["R1_reset_resets_peak_hold"] for c in CARDS}
    ac = all_cards(pc, ALL, R1_gate={c: pc[c]["R1_reset_resets_peak_hold"] for c in ALL})
    return item("TEL-R", ["pt-spatial-51", "pt-spatial-59", "pt-spatial-65", "pt-spatial-67", "pt-spatial-68", "pt-spatial-69",
                          "pt-spatial-70", "hub-022"], pc,
                "unit = pass (3 load windows are sub-samples). R1 (gate) reset within 1 s: low >= mean - 2, high <= mean + 3 in "
                "every window; R2 every load window high - SP max in {2,3,4} and every pass median 3 (equal but not 3 -> own "
                "figure; disagreeing -> WITHIN-NOISE); R3 >= 80% of rises at +3/+4; R4 idle windows high - SP max <= 2; R5 low - "
                "SP min in {-1,-2} in every window; R6 >= 17 of 34 lows >= 2 mV below idle with die_mv.minion falling <= 2.5 mV "
                "(pass medians) in >= 2 of 3 passes. PASS needs R1-R6 on both cards", oc,
                "peak-hold: R1 %s, R2 %s, R6 %s (%s)%s" % (gate, {c: pc[c]["R2"] for c in CARDS}, {c: pc[c]["R6"] for c in CARDS}, oc,
                                                         "" if all(gate.values()) else "; R1 failed: the claims stay UNDER-REPLICATED"),
                R1_gate=gate, all_cards=ac, idle_clock=idle_notes(),
                reading_all_cards="peak-hold on every card: R1 %s, R2 %s, R6 %s (%s)%s" % (
                    ac["R1_gate"], {c: pc[c]["R2"] for c in ALL}, {c: pc[c]["R6"] for c in ALL}, ac["outcome"],
                    "" if all(ac["R1_gate"].values()) else "; R1 failed on a card"))


GOV_DOWN = re.compile(rb"Power throttle down event, current pwr (\d+)\s+tdp level: (\d+)")
GOV_IDLE_OLD = re.compile(rb"Power idle state event, current pwr (\d+)\s+tdp level (\d+)")
GOV_IDLE_NEW = re.compile(rb"Power idle state event(?!, current pwr)")
GOV_UP = re.compile(rb"Power throttle up event")


def gov_events(buf):
    """Governor events in buffer order, as tools/ettelem/analyze_dvfs.py --sptrace reads them (the INFO-level rings
    do not walk as parse_sptrace_voltage.ring_entries() expects: 1 and 0 entries in the committed 22 Sep dumps)."""
    ev = []
    for m in re.finditer(rb"Power (idle state event(, current pwr \d+\s+tdp level \d+)?|throttle down event|throttle up event)", buf):
        txt = m.group(0)
        ev.append("down" if b"down" in txt else "up" if b"up event" in txt else ("idle" if b"current pwr" in txt else "idle_new"))
    return ev


def item_G(D):
    pc, fws = {}, {}
    for card in ALL:
        per = []
        for P in D[card]:
            if P["sp1"] is None or P["config"] is None:
                continue
            buf = P["sp1"]
            downs = [(int(a), int(b)) for a, b in GOV_DOWN.findall(buf)]
            idles = [(int(a), int(b)) for a, b in GOV_IDLE_OLD.findall(buf)]
            n_new = len(GOV_IDLE_NEW.findall(buf))
            ups = len(GOV_UP.findall(buf))
            ev = gov_events(buf)
            rep_idle = sum(1 for a, b in zip(ev, ev[1:]) if a == b == "idle")
            runs = P["gov_runs"]
            ghz = [r.get("ghz") for k in sorted(runs) for r in timed(runs[k])]
            procs = sorted(k for k in runs if re.fullmatch(r"G\d+", k) and timed(runs[k]))   # the 5 host processes
            cfg = P["config"]
            drv = P["driver"][0] if P["driver"] else {}
            m1 = re.search(r"Firmware release revision: Major: (\d+) Minor: (\d+) Revision: (\d+)", P["fw"])
            m2 = re.search(r"PMIC Firmware versions: Major: (\d+) Minor: (\d+) Revision: (\d+)", P["fw"])
            fw = [".".join(m.groups()) if m else None for m in (m1, m2)]
            row = {"pass": P["pass"], "config": {k: cfg.get(k) for k in ("tdp_w", "temp_threshold_c", "power_state_name")},
                   "down_lines": len(downs), "idle_lines_old_format": len(idles), "idle_lines_353f20e_format": n_new, "up_lines": ups,
                   "repeated_idle_events": rep_idle, "launch_processes": procs, "launch_ghz": ghz,
                   "driver": {k: drv.get(k) for k in ("tdp_w", "minion_boot_freq_mhz", "cm_shire_mask", "l3_kb")}, "fw": fw}
            launches_ok = len(procs) == 5 and bool(ghz) and all(g is not None and 0.59 <= g <= 0.61 for g in ghz)
            drv_ok = (drv.get("tdp_w") == 65 and drv.get("minion_boot_freq_mhz") == 600 and drv.get("cm_shire_mask") == "0xffffffff"
                      and drv.get("l3_kb") == 32768)
            fw_ok = fw == ["1.3.1", "1.5.0"]
            if card == A3:
                row["holds"] = (cfg.get("tdp_w") == 0 and cfg.get("temp_threshold_c") == 65 and cfg.get("power_state_name") == "max_power"
                                and len(downs) >= 5 and all(b == 0 for _, b in downs) and len(idles) >= 5 and all(b == 0 for _, b in idles)
                                and rep_idle <= 1 and ups == 0 and launches_ok and drv_ok and fw_ok)
            else:
                die = P["die_block_start"]
                warm = (die is not None and die >= 68) or (P["die_after_heat"] is not None and P["die_after_heat"] >= 68)
                row["die_ge_68"] = warm
                if not warm:
                    row["dropped"] = "readouts not on a die >= 68 C"
                row["holds"] = (cfg.get("tdp_w") == 65 and cfg.get("temp_threshold_c") == 65 and cfg.get("power_state_name") == "managed_power"
                                and n_new == 0 and launches_ok and drv_ok and fw_ok)
                row["governor_lines"] = len(downs) + len(idles) + n_new + ups
            row["parts"] = {"launches_0.59_0.61": launches_ok, "driver": drv_ok, "fw_1.3.1_1.5.0": fw_ok}
            per.append(row)
        kept = [r for r in per if "dropped" not in r]
        fws[card] = sorted({tuple(r["fw"]) for r in kept})
        if card in CARDS:
            pc[card] = {"n": len(kept), "passes": per, "status": status_of(len(kept), all(r["holds"] for r in kept))}
        else:   # a new card: the governor-free (aifoundry2) readouts, the 'both' parts and the firmware, reported
            pc[card] = reported(len(kept), passes=per, firmware=[list(x) for x in fws[card]],
                                aifoundry2_spec_met_every_kept_pass=all(r["holds"] for r in kept) if kept else None,
                                config_seen=sorted({json.dumps(r["config"], sort_keys=True) for r in per}))
    same_fw = len(fws.get(A2, [])) == 1 and fws.get(A2) == fws.get(A3)
    oc = combine(pc, list(CARDS))
    if oc == "PASS" and not same_fw:
        oc = "FAIL"
    a2k = [r for r in pc[A2]["passes"] if "dropped" not in r]
    if not a2k:
        d75 = None
    elif any(r["idle_lines_353f20e_format"] for r in a2k):
        d75 = "refuted: a 353f20e-format idle line on aifoundry2"
    elif not any(r["governor_lines"] for r in a2k):
        d75 = "no governor line on aifoundry2 in any pass: dvfs-75 stays one card"
    elif any(r["idle_lines_old_format"] for r in a2k):
        d75 = "aifoundry2 prints pre-60b40c10f idle lines: both cards run the older governor"
    else:
        d75 = "aifoundry2 governor lines without an idle event: format not decided"
    # tested on aifoundry2 and aifoundry3 only (the others are reported), with the registered same-firmware rule, so
    # all_cards equals the registered outcome
    ac = all_cards(pc, list(CARDS), firmware={c: [list(x) for x in fws.get(c, [])] for c in ALL},
                   same_firmware_every_card=len({x for c in ALL for x in fws.get(c, [])}) == 1)
    if ac["outcome"] == "PASS" and not same_fw:
        ac["outcome"] = "FAIL"
    return item("TEL-G", ["dvfs-07", "dvfs-40", "dvfs-41", "dvfs-42", "dvfs-43", "dvfs-44", "dvfs-46", "dvfs-51", "dvfs-75"], pc,
                "deterministic, every kept pass (>= 3) per card. a3: config 0 / 65 / max_power; sp1 >= 5 throttle-down lines "
                "'tdp level: 0' and >= 5 old-format idle lines 'tdp level 0', <= 1 repeated idle event, 0 throttle-up; a2 "
                "(die >= 68 C): 65 / 65 / managed_power, no 353f20e-format idle line; both: 5 launches at 0.59-0.61 GHz, driver "
                "tdp 65 / boot 600 / mask 0xffffffff / l3 32768, firmware 1.3.1 and PMIC 1.5.0, the same on both cards", oc,
                "governor readouts: a2 %s, a3 %s, firmware %s; dvfs-75: %s (%s)" % (pc[A2]["status"], pc[A3]["status"],
                                                                                 {c: fws.get(c) for c in CARDS}, d75, oc),
                same_firmware=same_fw, dvfs_75=d75,
                all_cards=ac,
                reading_all_cards="governor readouts tested on aifoundry2 and aifoundry3 only; firmware per card %s; the others' "
                                  "config %s" % ({c: fws.get(c) for c in ALL},
                                                 {c: pc[c].get("config_seen") for c in ALL if c not in CARDS}))


IDLE = {}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", default=",".join(EXPECT),
                    help="the cards the campaign expects (an expected card with no data makes all_cards INSUFFICIENT)")
    a = ap.parse_args()
    exp = [c for c in a.expect.split(",") if c]
    ALL[:] = list(dict.fromkeys(list(CARDS) + exp))       # the registered cards always take part
    D, notes = load(a.data)
    SPV = {c: [sp_pass_values(P) for P in D[c]] for c in ALL}
    for c in ALL:
        for v in SPV[c]:
            for x in v["drops"]:
                notes.append("%s p%d: %s" % (c, v["pass"], x))
    for c in ALL:
        IDLE[c] = idle_summary(D, c)
        if c not in PRESENT:
            notes.append("%s: no data directory (all_cards INSUFFICIENT for every item it is tested in)" % c)
    items = items_sp(D, SPV) + items_reset(D) + [item_S(D), item_Q(D), item_R(D), item_G(D)]
    out = {"exp": "tel", "plan_id": "V3-TEL", "data": os.path.abspath(a.data), "items": items,
           "cards": {"registered": list(CARDS), "all": list(ALL), "present": sorted(PRESENT), "missing": [c for c in ALL if c not in PRESENT],
                     "clock_rule": {c: clock_rule(c) for c in ALL}, "settle_ms": SETTLE_MS},
           "idle_clock": IDLE,
           "passes": {c: [{"pass": P["pass"], "block": P["block"], "sp": SPV[c][i]} for i, P in enumerate(D[c])] for c in ALL},
           "notes": notes}
    json.dump(out, open(a.out, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("%-7s %-14s %-14s %s" % ("item", "registered", "all_cards", "reading (registered)"))
    for it in items:
        print("%-7s %-14s %-14s %s" % (it["item"], it["outcome"], it["all_cards"]["outcome"], it["reading"]))
    for c in ALL:
        print("idle clock %-14s %s" % (c, IDLE[c]["note"]))


if __name__ == "__main__":
    main()
