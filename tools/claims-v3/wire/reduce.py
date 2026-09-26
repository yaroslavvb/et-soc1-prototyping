#!/usr/bin/env python3
"""V3-WIRE reduction: the pre-registered items of PLAN3 V3-WIRE, exactly as registered, plus the four-card outcome.

    python3 tools/claims-v3/wire/reduce.py --data DIR --out verdicts.json [--root TREE] [--beside A2_DIR A3_DIR] [-q]

DIR holds one directory per card laid out like DATA_ROOT (DIR/<card>/wire/p<N>/ as block.sh writes them): aifoundry2,
aifoundry3, aifoundry1-c0, aifoundry1-c1, and any other card directory present (a name like aifoundry<N>[-c<M>]).
Only pass directories whose block.json says "ok" are used (p<N>.attempt-* directories, which queue.sh sets aside, never).
--root is the tree whose workloads/enercat/analyze_wire.py reduces the bursts (default: the current directory).
--beside prints the committed 3-pass runs (runner layout, e.g. docs/reports/data/2026-09-24-wire2-aifoundry{2,3}) next
to the new values; they never enter a test (PLAN3 R-new).

Two outcomes per item:
  "outcome"    the REGISTERED outcome, from aifoundry2 and aifoundry3 only, computed exactly as before the four-card
               amendment (same bursts, same drop rules, same statistics, same words).
  "all_cards"  the four-card amendment (AMENDMENTS.md, 25 Sep, before any data of aifoundry1's cards): the same
               per-card test on every card (aifoundry2, aifoundry3, aifoundry1-c0, aifoundry1-c1 and any other card
               present): PASS it holds on every card; CARD-DIFFERENT it holds on some; FAIL on none (a "sign" card, null
               excluded with the mean outside the range, does not hold); INSUFFICIENT a card (an expected one included)
               has fewer than 3 kept passes. "over_sufficient" gives the same words over the
               cards that do have 3 kept passes. No WIRE band is specific to one card (P1-P16 were registered "per card"
               with one range, WIRE-FILL "on each card"), so every item is tested on aifoundry1's cards unchanged.
  per_card holds every card's values; aifoundry2's and aifoundry3's are the registered ones in both outcomes.

Drop rules per card:
  aifoundry2, aifoundry3  as registered: analyze_wire.bursts() (any sample in the burst or its idle brackets off
               600 MHz, a starved sampler, too few samples) and, on aifoundry2, R-clock (a launch's implied clock
               cycles_max / wall_s outside 0.595-0.605 GHz).
  aifoundry1's cards (and any other new card)  analyze_wire.bursts() with its clock test narrowed to the burst's own
               samples (bursts()'s "busy" window: first launch + 0.5 s to the last launch's end); an idle bracket's clock
               never drops a burst (aifoundry1-c0 idles at 300 MHz "low_power" between kernels). R-clock on every
               governor-free card (all but aifoundry3), per launch, except that the FIRST launch of a burst whose idle
               bracket before it sat below 600 MHz may go down to 0.585 GHz (the governor's ramp from its idle clock: a
               ramp of at most ~20 ms at 300 MHz); every other launch keeps 0.595-0.605 GHz.
Every card's idle state (minion and NoC clock and voltage in the idle brackets, against the bursts) is reported in
cards[<card>]["idle_state"], and every energy-over-idle item carries "idle_clock" (each card's idle minion clock) and,
when a card's idle state differs from its bursts' on the rail the item reads, an "idle_note" that says whether the
item's statistic cancels a constant over-idle power (differences of two data patterns at the same hops and bandwidth)
or not.

Items (PLAN3 V3-WIRE "Pre-registered predictions and decision rules"):
  WIRE-P1-16  reported as one item per registered sub-test, P1-P12 and P14a-P16. The statistics, nulls and ranges are
              registered/exp_test.py EXP1 + registered/exp_test_v3.py EXTRA, imported unchanged (verbatim copies of
              validate3/inv/heat-work/exp_test.py and validate3/heat-verify/exp_test_v3.py; sha256 in README.md). Each
              burst is reduced by workloads/enercat/analyze_wire.bursts() (board power leakage-corrected over idle
              brackets; mesh rail over the last 0.6 s), dropped as above. Unit: the pass; per card the statistic is
              computed per pass and a 99% t-interval (df = n - 1) formed over the first six passes (by pass number) in
              which it can be computed (6 registered; later passes exist only as re-runs of passes that lost bursts).
              Outcome per the registered rule and PLAN3 R-both:
                per card: holds = n >= 3, interval excludes the null, mean inside the range (equivalence items P10,
                P14a/b, P16: the whole interval inside the range); sign = excludes the null, mean outside; fails =
                otherwise; insufficient = fewer than 3 kept passes.
                PASS both hold; SIGN-ONLY both exclude the null on the same side and a mean is outside the range (the
                page states the new per-card values); CARD-DIFFERENT one holds and the other fails, or both exclude
                the null on opposite sides; FAIL otherwise; INSUFFICIENT a card has fewer than 3 kept passes.
              "registered_verdict" repeats exp_test.run()'s own PASS/SIGN-ONLY/FAIL for the same values.
              Board items also carry "secondary_noleak" (the same bursts without the leakage correction): DESCRIPTIVE
              ONLY, as registered; it decides nothing.
  WIRE-P1-16/P13  the board per-second bound on the link-disjoint fixed part (extra.py's psb for wsep): descriptive;
              the page keeps "cannot rule out" if its upper 99% bound stays above 50% (outcome DESCRIPTIVE).
  WIRE-FILL   every DUMP word equals its EXPECT word in all 12 --dump-slice launches on each card (4 fills x 3):
              PASS all match on both cards; FAIL any mismatch on either card (deterministic, registered); INSUFFICIENT
              fewer than 3 complete launches of a fill on a card (tstore_uniq excepted if the host refused a DRAM
              slice on that card, i.e. all three launches failed with a "refusing" message, which the plan allows: the
              pattern is then dropped and the reading says so). A launch is complete only with 256 DUMP and 256
              EXPECT words and every ENERCAT line ok:true (a failed kernel launch leaves the slice unwritten: that is
              a failed launch, INSUFFICIENT until re-run, not a mismatch). all_cards: per card holds (all complete
              and matching), fails (a mismatch), insufficient (a fill short).
"""
import argparse
import collections
import contextlib
import datetime
import glob
import hashlib
import json
import math
import os
import re
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)
CARDS = ("aifoundry2", "aifoundry3")                                   # the registered outcome's cards
EXPECTED = campaign.CAMPAIGN                                         # the campaign's cards (--cards overrides)
PINNED = ("aifoundry3",)                   # lib.sh: aifoundry3 is pinned at 600 MHz; every other card is governor-free
CARD_RE = re.compile(r"aifoundry\d+(-c\d+)?$")
SHORT = {"aifoundry2": "a2", "aifoundry3": "a3", "aifoundry1-c0": "a1c0", "aifoundry1-c1": "a1c1"}
MAX_REPEATS, MIN_REPEATS = 6, 3
CLOCK_BAND = (0.595, 0.605)
FIRST_LAUNCH_FLOOR = 0.585    # new cards: first launch of a burst that starts from an idle clock below 600 MHz
FILLS = ("bern:0.25", "alt:64", "frz", "uq:0.25")
UNITS = {**{k: ("fJ/bit/hop", 1) for k in ("P1", "P2", "P3", "P4", "P5a", "P5b")},
         **{k: ("%", 100) for k in ("P6a", "P6b", "P7a", "P7b", "P7c", "P7d", "P7e", "P7f", "P10", "P12", "P13",
                                    "P14a", "P14b", "P15a", "P15b", "P16")},
         "P8": ("hop", 1), "P9": ("hop", 1), "P11a": ("fJ/mm", 1), "P11b": ("fJ/mm", 1)}
EQUIV_NOTE = "equivalence"
# Statistics in which a constant over-idle power (a card whose idle brackets sit at another operating point than its
# bursts) cancels: differences of the random-data and zeros configurations at the same hops, which run at the same
# bandwidth (0.1% apart in the 25 Sep aifoundry2 passes), so wall/bytes is the same in both terms. Every other
# statistic (a zeros or a total slope, a ratio of slopes, a point off a line, an exit step, a per-second bound) takes
# the step times wall/bytes, which grows with the hop distance as the bandwidth falls.
STEP_CANCELS = ("P1", "P3", "P5a", "P10", "P16")


def short(h):
    return SHORT.get(h, h)


def setup(root):
    enercat = os.path.join(root, "workloads", "enercat")
    if not os.path.exists(os.path.join(enercat, "analyze_wire.py")):
        raise SystemExit(f"no workloads/enercat/analyze_wire.py under {root}: pass --root <tree root>")
    sys.path.insert(0, enercat)
    sys.path.insert(0, os.path.join(HERE, "registered"))
    sys.path.insert(0, HERE)
    import analyze_wire as aw   # noqa: E402
    import exp_test as E        # noqa: E402  registered P1-P13
    import exp_test_v3 as V3    # noqa: E402  registered P14-P16
    import wire_check as WC     # noqa: E402  the dump parser the block uses
    return aw, E, V3, WC


def block_status(d):
    p = os.path.join(d, "block.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p)).get("status")
    except ValueError:
        return "unreadable block.json"


def implied_bad(aw, d):
    """(cfg, pass) of bursts with a launch whose implied clock is outside CLOCK_BAND, and the range seen."""
    bad, g = set(), []
    for r in aw.jl(os.path.join(d, "runs.jsonl")):
        if r.get("wall_s"):
            x = r["cycles_max"] / r["wall_s"] / 1e9
            g.append(x)
            if not CLOCK_BAND[0] <= x <= CLOCK_BAND[1]:
                bad.add((r["cfg"], r["pass"]))
    return bad, g


def burst_list(runs):
    """analyze_wire.bursts()'s own grouping: ((cfg, pass), launches, first start s, last end s), in time order."""
    groups = collections.OrderedDict()
    for r in runs:
        groups.setdefault((r["cfg"], r["pass"]), []).append(r)
    return sorted(((k, rs, min(r["t_start_ms"] for r in rs) / 1000.0, max(r["t_end_ms"] for r in rs) / 1000.0)
                   for k, rs in groups.items()), key=lambda b: b[2])


@contextlib.contextmanager
def busy_clock_only(aw, d):
    """analyze_wire.bursts() with its clock test narrowed to the bursts' own samples: while this is active, every
    telemetry sample of directory d outside all bursts' busy windows (bursts()'s 'busy': first launch + 0.5 s to the
    last launch's end) reads 600 MHz to it. Nothing else changes: same brackets, powers, leakage correction, drops."""
    orig = aw.jl

    def jl(path):
        rows = orig(path)
        if os.path.basename(path) != "telemetry.jsonl" or not rows:
            return rows
        wins = [(lo, hi) for _, _, lo, hi in burst_list(orig(os.path.join(d, "runs.jsonl")))]
        for s in rows:
            t = s["t_ms"] / 1000.0
            if not any(t >= lo + 0.5 and t <= hi for lo, hi in wins):
                s["mhz"] = dict(s.get("mhz") or {}, minion=600)
        return rows
    aw.jl = jl
    try:
        yield
    finally:
        aw.jl = orig


def _g(s, a, b):
    x = s.get(a)
    return x.get(b) if isinstance(x, dict) else None


def clock_states(aw, d):
    """Per burst, the operating point in its idle brackets and in its busy window, with bursts()'s own windows:
    {(cfg, pass): {"idle_mhz", "idle_mv", "idle_noc_mhz", "idle_noc_mv", "busy_mhz", "busy_mv", "busy_noc_mhz",
    "busy_noc_mv": lists of sample values, "before_mhz": the modal minion clock of the bracket before the burst}}."""
    tel, runs, marks = (aw.jl(os.path.join(d, n)) for n in ("telemetry.jsonl", "runs.jsonl", "marks.jsonl"))
    if not tel or not runs:
        return {}
    t = [s["t_ms"] / 1000.0 for s in tel]
    col = {"mhz": [_g(s, "mhz", "minion") for s in tel], "mv": [_g(s, "die_mv", "minion") for s in tel],
           "noc_mhz": [_g(s, "mhz", "noc") for s in tel], "noc_mv": [_g(s, "die_mv", "noc") for s in tel]}
    other = [any(m["t_start_ms"] / 1000.0 - 0.2 <= x <= m["t_end_ms"] / 1000.0 + 0.6 for m in marks) for x in t]
    bl = burst_list(runs)
    out = {}
    for i, (k, rs, lo, hi) in enumerate(bl):
        prev_hi = bl[i - 1][3] if i else t[0]
        next_lo = bl[i + 1][2] if i + 1 < len(bl) else t[-1]
        before = [j for j, x in enumerate(t) if max(prev_hi + 2.0, lo - 3.5) <= x <= lo - 0.3 and not other[j]]
        after = [j for j, x in enumerate(t) if hi + 0.5 <= x <= min(next_lo - 0.3, hi + 3.8) and not other[j]]
        busy = [j for j, x in enumerate(t) if lo + 0.5 <= x <= hi]
        st = {}
        for name, v in col.items():
            st["idle_" + name] = [v[j] for j in before + after if v[j] is not None]
            st["busy_" + name] = [v[j] for j in busy if v[j] is not None]
        bm = [col["mhz"][j] for j in before if col["mhz"][j] is not None]
        st["before_mhz"] = collections.Counter(bm).most_common(1)[0][0] if bm else None
        out[k] = st
    return out


def implied_bad_new(aw, d, states):
    """R-clock on a governor-free new card: {(cfg, pass): why}, all launch values, first-launch values of bursts that
    started from an idle clock below 600 MHz (the ramp)."""
    bad, g, ramp = {}, [], []
    for k, rs, lo, hi in burst_list(aw.jl(os.path.join(d, "runs.jsonl"))):
        from_low = (states.get(k, {}).get("before_mhz") or 600) < 600
        for i, r in enumerate(sorted(rs, key=lambda r: r["t_start_ms"])):
            if not r.get("wall_s"):
                continue
            x = r["cycles_max"] / r["wall_s"] / 1e9
            floor = FIRST_LAUNCH_FLOOR if (i == 0 and from_low) else CLOCK_BAND[0]
            (ramp if (i == 0 and from_low) else g).append(x)
            if not floor <= x <= CLOCK_BAND[1] and k not in bad:
                bad[k] = (f"implied clock {x:.4f} GHz outside {floor}-{CLOCK_BAND[1]} GHz"
                          + (" (first launch, from a lower idle clock)" if floor != CLOCK_BAND[0] else f" (launch {i + 1})"))
    return bad, g, ramp


def _hist(vals):
    c = collections.Counter(vals)
    n = sum(c.values())
    return {str(k): round(v / n, 4) for k, v in sorted(c.items())} if n else {}


def _med(vals):
    return round(float(statistics.median(vals)), 1) if vals else None


def _mode(vals):
    return collections.Counter(vals).most_common(1)[0][0] if vals else None


def idle_summary(states, pre_burst):
    """A card's idle state over every burst of its ok passes (kept or dropped)."""
    acc = collections.defaultdict(list)
    for st in states:
        for k, v in st.items():
            if isinstance(v, list):
                acc[k] += v
    s = {"idle_minion_mhz": _hist(acc["idle_mhz"]), "idle_minion_mv_median": _med(acc["idle_mv"]),
         "idle_noc_mhz": _hist(acc["idle_noc_mhz"]), "idle_noc_mv_median": _med(acc["idle_noc_mv"]),
         "busy_minion_mhz": _hist(acc["busy_mhz"]), "busy_minion_mv_median": _med(acc["busy_mv"]),
         "busy_noc_mhz": _hist(acc["busy_noc_mhz"]), "busy_noc_mv_median": _med(acc["busy_noc_mv"]),
         "idle_samples": len(acc["idle_mhz"]), "busy_samples": len(acc["busy_mhz"])}
    s["idle_minion_mhz_mode"], s["busy_minion_mhz_mode"] = _mode(acc["idle_mhz"]), _mode(acc["busy_mhz"])
    s["idle_noc_mhz_mode"], s["busy_noc_mhz_mode"] = _mode(acc["idle_noc_mhz"]), _mode(acc["busy_noc_mhz"])
    # the minion rail's idle operating point differs from the bursts' (board power items); the NoC's (mesh rail items)
    s["differs_minion"] = (s["idle_minion_mhz_mode"] is not None and s["busy_minion_mhz_mode"] is not None
                           and s["idle_minion_mhz_mode"] != s["busy_minion_mhz_mode"])
    s["differs_noc"] = (s["idle_noc_mhz_mode"] is not None and s["busy_noc_mhz_mode"] is not None
                        and s["idle_noc_mhz_mode"] != s["busy_noc_mhz_mode"])
    if pre_burst:
        s["pre_burst_records_minion_mhz"] = _hist(pre_burst)   # block.sh's idle_state.jsonl, the sampler's last line
    return s


def load_card(aw, WC, base, card):
    """New data of one card: {pass: {cfg: burst}} with and without the leakage correction, plus bookkeeping.
    aifoundry2/aifoundry3: exactly the registered reduction; any other card: the four-card drop rules (module doc)."""
    registered = card in CARDS
    gov_free = card not in PINNED
    ix, ixn = collections.defaultdict(dict), collections.defaultdict(dict)
    info = {"passes_ok": [], "passes_skipped": {}, "bursts_kept": 0, "bursts_dropped": [], "implied_clock_ghz": None,
            "drop_rule": ("registered: any sample in the burst or its idle brackets off 600 MHz"
                          + (", implied clock 0.595-0.605 GHz" if card == "aifoundry2" else "")) if registered else
                         ("four-card: samples in the burst's busy window off 600 MHz (idle brackets never drop)"
                          + (", implied clock 0.595-0.605 GHz (first launch from a lower idle clock >= 0.585)" if gov_free else "")),
            "governor_free": gov_free}
    if not os.path.isdir(base):
        info["missing"] = True
    dumps, ghz, ramp, states, pre = [], [], [], [], []
    only_idle = 0
    for d in sorted(glob.glob(os.path.join(base, "p*"))):
        m = re.fullmatch(r"p(\d+)", os.path.basename(d))
        if not m or not os.path.isdir(d):
            continue
        p = int(m.group(1))
        st = block_status(d)
        if st != "ok":
            info["passes_skipped"][p] = st or "no block.json"
            continue
        if os.path.isdir(os.path.join(d, "dump")):
            dumps += [dict(WC.parse_dump(f), pass_=p) for f in sorted(glob.glob(os.path.join(d, "dump", "dump_*.txt")))]
        if not os.path.exists(os.path.join(d, "runs.jsonl")) and not os.path.exists(os.path.join(d, "runs.jsonl.gz")):
            info["passes_skipped"][p] = "no runs.jsonl"
            continue
        try:
            if registered:
                _, bs, dr = aw.bursts(d)
                _, bsn, _ = aw.bursts(d, leak=False)
            else:
                with busy_clock_only(aw, d):
                    _, bs, dr = aw.bursts(d)
                    _, bsn, _ = aw.bursts(d, leak=False)
        except Exception as e:   # e.g. an empty telemetry file
            info["passes_skipped"][p] = f"unreadable: {e!r}"
            continue
        # descriptive (never decides which passes or bursts a registered card keeps)
        try:
            cs = clock_states(aw, d)
        except Exception as e:
            cs = {}
            info.setdefault("idle_state_errors", []).append(f"p{p}: {e!r}")
        states += list(cs.values())
        pre += [r["sample"]["mhz"]["minion"] for r in WC.jl(os.path.join(d, "idle_state.jsonl"))
                if isinstance(r.get("sample"), dict) and _g(r["sample"], "mhz", "minion") is not None]
        if registered:
            bad, g = implied_bad(aw, d)
            if card != "aifoundry2":
                bad = set()
            bad = {k: "implied clock outside 0.595-0.605 GHz" for k in bad}
            # descriptive: bursts that the four-card rule would keep but the registered rule dropped for an idle
            # bracket's clock (decides nothing; shows whether the two rules differ on this card)
            try:
                with busy_clock_only(aw, d):
                    _, bsb, _ = aw.bursts(d)
                kept = {(b["cfg"], b["pass"]) for b in bs}
                only_idle += sum(1 for b in bsb if (b["cfg"], b["pass"]) not in kept
                                 and any(x["cfg"] == b["cfg"] and x["why"] == "clock left 600 MHz" for x in dr))
            except Exception as e:
                info.setdefault("idle_state_errors", []).append(f"p{p} busy-rule comparison: {e!r}")
        else:
            bad, g, r0 = implied_bad_new(aw, d, cs) if gov_free else ({}, [], [])
            ramp += r0
            if not gov_free:
                g = [r["cycles_max"] / r["wall_s"] / 1e9 for r in aw.jl(os.path.join(d, "runs.jsonl")) if r.get("wall_s")]
        ghz += g
        for x in dr:
            why = x["why"]
            if not registered and why == "clock left 600 MHz":
                why = "clock left 600 MHz inside the burst"
            info["bursts_dropped"].append({"pass": p, "cfg": x["cfg"], "why": why})
        for b in bs:
            k = (b["cfg"], b["pass"])
            if k in bad:
                info["bursts_dropped"].append({"pass": p, "cfg": b["cfg"], "why": bad[k]})
                continue
            ix[p][b["cfg"]] = b
            info["bursts_kept"] += 1
        for b in bsn:
            if (b["cfg"], b["pass"]) not in bad:
                ixn[p][b["cfg"]] = b
        info["passes_ok"].append(p)
    if ghz:
        info["implied_clock_ghz"] = [round(min(ghz), 5), round(max(ghz), 5)]
    if ramp:
        info["first_launch_from_low_idle_ghz"] = [round(min(ramp), 5), round(max(ramp), 5)]
        info["first_launch_from_low_idle_n"] = len(ramp)
    if registered:
        info["bursts_dropped_only_for_idle_clock"] = only_idle
    info["idle_state"] = idle_summary(states, pre)
    return ix, ixn, info, dumps


def load_beside(aw, d):
    """A committed run in the runner's layout (one directory, passes in runs.jsonl): {pass: {cfg: burst}}."""
    ix = collections.defaultdict(dict)
    _, bs, _ = aw.bursts(d)
    for b in bs:
        ix[b["pass"]][b["cfg"]] = b
    return ix


def values(ix, fn):
    """fn over the passes in order; the first MAX_REPEATS passes where it can be computed (exp_test.run's catch)."""
    vals, used = [], []
    for p in sorted(ix):
        if len(vals) >= MAX_REPEATS:
            break
        try:
            x = fn(ix, p)
        except (TypeError, KeyError, ZeroDivisionError):
            continue
        if x is None:
            continue
        vals.append(x)
        used.append(p)
    return vals, used


def card_status(c, null, rng):
    if c.get("n", 0) < MIN_REPEATS:
        return "insufficient"
    if null is None:
        return "holds" if rng[0] <= c["lo99"] and c["hi99"] <= rng[1] else "fails"
    if not (c["lo99"] > null or c["hi99"] < null):
        return "fails"
    return "holds" if rng[0] <= c["mean"] <= rng[1] else "sign"


def combine(per, null):
    st = {h: per[h]["status"] for h in CARDS}
    if "insufficient" in st.values():
        return "INSUFFICIENT"
    a, b = st["aifoundry2"], st["aifoundry3"]
    if a == b == "holds":
        return "PASS"
    if {a, b} == {"holds", "fails"}:
        return "CARD-DIFFERENT"
    if a in ("holds", "sign") and b in ("holds", "sign"):
        same = (per["aifoundry2"]["mean"] - null) * (per["aifoundry3"]["mean"] - null) > 0
        return "SIGN-ONLY" if same else "CARD-DIFFERENT"
    return "FAIL"


def registered_verdict(per, null, rng):
    """exp_test.run()'s own verdict for the same per-card values (its n >= 3 rule, no INSUFFICIENT)."""
    cs = [per[h] for h in CARDS]
    if null is None:
        return "PASS" if all(c.get("n", 0) >= 3 and rng[0] <= c["lo99"] and c["hi99"] <= rng[1] for c in cs) else "FAIL"
    excl = all(c.get("n", 0) >= 3 and (c["lo99"] > null or c["hi99"] < null) for c in cs)
    inr = all(rng[0] <= c["mean"] <= rng[1] for c in cs if "mean" in c)
    return "PASS" if excl and inr else ("SIGN-ONLY" if excl else "FAIL")


def fmt(c, tid):
    unit, k = UNITS.get(tid, ("", 1))
    n = c.get("n", 0)
    if n == 0:
        return "no data"
    if "lo99" not in c:
        return f"1 pass ({c['vals'][0] * k:.3g}{unit if unit == '%' else ' ' + unit})" if c.get("vals") else f"n={n}"
    u = "%" if unit == "%" else " " + unit
    return f"{c['mean'] * k:.3g}{u} [{c['lo99'] * k:.3g}, {c['hi99'] * k:.3g}] n={n}"


def fmt_rng(rng, tid):
    unit, k = UNITS.get(tid, ("", 1))
    return f"{rng[0] * k:g}..{rng[1] * k:g}{'%' if unit == '%' else ' ' + unit}"


CONSEQUENCE = {
    "PASS": "holds on both cards as predicted",
    "SIGN-ONLY": "the effect is there on both cards but a mean is outside the predicted range: the page states the new per-card values",
    "FAIL": "the prediction failed: the claim is dropped or qualified and the page takes the measured values",
}


def test_text(null, rng, tid):
    if null is None:
        return (f"{EQUIV_NOTE}: 99% t-interval over pass values (df n-1, up to 6 passes) must lie inside {fmt_rng(rng, tid)} "
                f"on each card; PASS both, CARD-DIFFERENT one, FAIL neither; INSUFFICIENT < 3 kept passes on a card")
    return (f"99% t-interval over pass values (df n-1, up to 6 passes) per card, null {null}, predicted {fmt_rng(rng, tid)}: "
            f"PASS both exclude the null with means in range; SIGN-ONLY both exclude it (same side), a mean outside; "
            f"CARD-DIFFERENT holds on one card and fails on the other; FAIL otherwise; INSUFFICIENT < 3 kept passes on a card")


def reading(tid, what, per, null, rng, outcome):
    vals = "; ".join(f"{SHORT[h]} {fmt(per[h], tid)}" for h in CARDS)
    if outcome == "INSUFFICIENT":
        few = " and ".join(SHORT[h] for h in CARDS if per[h]["status"] == "insufficient")
        why = f"fewer than 3 kept passes on {few}: the claim stays as it is"
    elif outcome == "CARD-DIFFERENT":
        held = [SHORT[h] for h in CARDS if per[h]["status"] == "holds"]
        why = (f"holds on {held[0]} only: the page states per-card values" if len(held) == 1
               else "the null is excluded on both cards but on opposite sides: the page states per-card values")
    else:
        why = CONSEQUENCE[outcome]
    if null is not None and outcome in ("SIGN-ONLY", "CARD-DIFFERENT", "FAIL"):
        # a range that lies wholly on one side of the null: say so when a card's mean is on the other side (the
        # registered rule still calls both-sides-excluded SIGN-ONLY; the reading must not suggest the predicted sign)
        side = 1 if rng[0] >= null else (-1 if rng[1] <= null else 0)
        wrong = [SHORT[h] for h in CARDS if side and "mean" in per[h] and (per[h]["mean"] - null) * side < 0
                 and per[h].get("status") in ("sign", "holds")]
        if wrong:
            why += f" (the sign is opposite to the prediction on {' and '.join(wrong)})"
    return f"{tid} {what}: {vals}; predicted {fmt_rng(rng, tid)}: {outcome}, {why}."


# ---------------------------------------------------------------------------------------------------------------
# The four-card outcome (amendment of 25 Sep, before any aifoundry1 data)

def _over(st, hs):
    if not hs:
        return None
    held = [h for h in hs if st[h] == "holds"]
    return "PASS" if len(held) == len(hs) else ("CARD-DIFFERENT" if held else "FAIL")


def combine_all(per, cards, null=None):
    """PASS holds on every card; CARD-DIFFERENT on some; FAIL on none; INSUFFICIENT a card lacks 3 kept repeats."""
    st = {h: per[h]["status"] for h in cards}
    suff = [h for h in cards if st[h] != "insufficient"]
    res = {"cards": list(cards), "outcome": "INSUFFICIENT" if len(suff) < len(cards) else _over(st, cards),
           "over_sufficient": _over(st, suff), "holds_on": [h for h in cards if st[h] == "holds"],
           "sign_only_on": [h for h in cards if st[h] == "sign"], "fails_on": [h for h in cards if st[h] == "fails"],
           "insufficient_on": [h for h in cards if st[h] == "insufficient"],
           "missing": [h for h in cards if per[h].get("missing")]}
    if null is not None:
        sides = {h: (1 if per[h]["mean"] > null else -1) for h in suff if st[h] in ("holds", "sign")}
        if suff and len(sides) == len(suff):
            res["null_excluded"] = "same side" if len(set(sides.values())) == 1 else "opposite sides"
    return res


def idle_note(tid, what, cards, cinfo):
    """Energy-over-idle items: each card's idle minion clock, and a note when a card's idle state differs."""
    board = "board" in what
    clock = {h: {"idle_minion_mhz": cinfo[h]["idle_state"].get("idle_minion_mhz_mode"),
                 "idle_minion_mhz_share": cinfo[h]["idle_state"].get("idle_minion_mhz", {}),
                 "idle_minion_mv": cinfo[h]["idle_state"].get("idle_minion_mv_median"),
                 "idle_noc_mhz": cinfo[h]["idle_state"].get("idle_noc_mhz_mode")} for h in cards}
    diff = [h for h in cards if cinfo[h]["idle_state"].get("differs_minion" if board else "differs_noc")]
    if not diff:
        return clock, None
    rail = "minion" if board else "NoC"
    parts = []
    for h in diff:
        s = cinfo[h]["idle_state"]
        if board:
            parts.append(f"{h} idled at {s['idle_minion_mhz_mode']} MHz ({s['idle_minion_mv_median']} mV) against "
                         f"{s['busy_minion_mhz_mode']} MHz in its bursts")
        else:
            parts.append(f"{h}'s NoC idled at {s['idle_noc_mhz_mode']} MHz against {s['busy_noc_mhz_mode']} MHz in its bursts")
    note = ("; ".join(parts) + f": its {'board' if board else 'mesh-rail'} energy over idle includes the step of the "
            f"{rail} rail from its idle operating point to the burst's")
    if tid in STEP_CANCELS:
        note += (", which cancels in this statistic (a difference of the random-data and zeros configurations at the "
                 "same hops and bandwidth)")
    else:
        note += (", which this statistic does not cancel (it grows as wall/bytes with the hop distance): a result that "
                 f"differs on {' and '.join(diff)} alone cannot be told apart from its idle state and is not read as a "
                 "difference in the wire")
    return clock, note


def reading_all(tid, what, per, cards, rng, ac, note):
    vals = "; ".join(f"{short(h)} {fmt(per[h], tid)}" for h in cards)
    o = ac["outcome"]
    bits = []
    if ac["holds_on"]:
        bits.append("holds on " + ", ".join(short(h) for h in ac["holds_on"]))
    if ac["sign_only_on"]:
        bits.append("null excluded, mean outside the range on " + ", ".join(short(h) for h in ac["sign_only_on"]))
    if ac["fails_on"]:
        bits.append("fails on " + ", ".join(short(h) for h in ac["fails_on"]))
    if ac["insufficient_on"]:
        bits.append("fewer than 3 kept passes on " + ", ".join(short(h) + (" (no data)" if h in ac["missing"] else "")
                                                                 for h in ac["insufficient_on"]))
    txt = f"{tid} on all cards: {vals}; predicted {fmt_rng(rng, tid)}: {o} ({'; '.join(bits)})"
    if o == "INSUFFICIENT" and ac["over_sufficient"]:
        txt += f"; over the cards with 3 kept passes: {ac['over_sufficient']}"
    if ac.get("null_excluded") and o != "PASS":
        txt += (f"; the null is excluded on every card with 3 kept passes, "
                f"{'on the same side' if ac['null_excluded'] == 'same side' else 'but on opposite sides'}")
    if note:
        txt += f". Idle state: {note}"
    return txt + "."


def psb(E, aw, ix, p, fam="wsep", key="pj_per_byte"):
    """extra.py's per-second bound (the page's P13 statistic), with reader shires from the burst's own target map."""
    ds = (1, 2, 3, 4)
    z = [E.v(ix, p, f"{fam}/p0/hop{d}", key) for d in ds]
    bw = []
    for d in ds:
        b = ix[p][f"{fam}/p0.5/hop{d}"]
        bw.append(b["bytes_per_s"] / aw.link_sharing(b["target_map"])["reader_shires"])
    return E.line(ds, [z[0] * bw[0] / b for b in bw])[0] / E.line(ds, z)[0]


def fill_per_card(ds):
    by = collections.defaultdict(list)
    for r in ds:
        by[r["operands"]].append(r)
    refused = []
    uq = by.get("uq:0.25", [])
    # only an explicit refusal by the host ("refusing ...") drops the pattern; any other failure of the three
    # launches (no device, a kernel that did not finish) leaves them incomplete, i.e. INSUFFICIENT
    if uq and all((not r["complete"]) and r.get("refused") for r in uq):
        refused.append("uq:0.25")
    need = 3 * sum(1 for f in FILLS if f not in refused)
    complete = [r for r in ds if r["complete"] and r["operands"] not in refused]
    mism = [f"p{r['pass_']}/{r['file']}" for r in complete if r["mismatches"]]
    c = {"launches": len(ds), "complete": len(complete), "needed": need,
         "matched": sum(1 for r in complete if not r["mismatches"]), "with_mismatch": mism,
         "first_mismatch": next((r["first_mismatch"] for r in complete if r["mismatches"]), None),
         "incomplete": [f"p{r['pass_']}/{r['file']}" + (f" ({r['error']})" if r["error"] else "") for r in ds if not r["complete"]],
         "by_fill": {f: {"launches": len(by.get(f, [])), "matched": sum(1 for r in by.get(f, []) if r["complete"] and not r["mismatches"])} for f in FILLS},
         "refused_patterns": refused, "n": len(complete)}
    c["fills_short"] = [f for f in FILLS if f not in refused and sum(1 for r in by.get(f, []) if r["complete"]) < 3]
    c["status"] = "fails" if mism else ("insufficient" if c["fills_short"] else "holds")
    return c


def fill_item(card_dumps, allc, cinfo):
    per = {h: fill_per_card(card_dumps.get(h, [])) for h in allc}
    for h in allc:
        if cinfo[h].get("missing"):
            per[h]["missing"] = True
    bad_any = [h for h in CARDS if per[h]["with_mismatch"]]
    short_ = [h for h in CARDS if per[h]["fills_short"]]
    if bad_any:
        out = "FAIL"
        rd = (f"WIRE-FILL: a DUMP word differs from its EXPECT word on {' and '.join(SHORT[h] for h in bad_any)} "
              f"({', '.join(per[h]['with_mismatch'][0] for h in bad_any)}): FAIL, the page drops 'checked byte for byte'.")
    elif short_:
        out = "INSUFFICIENT"
        rd = (f"WIRE-FILL: " + "; ".join(f"{SHORT[h]} {per[h]['matched']}/{per[h]['needed']} launches complete and matching"
                                         + (f" (fewer than 3 of {', '.join(per[h]['fills_short'])})" if per[h]["fills_short"] else "")
                                         for h in CARDS)
              + ": INSUFFICIENT, the claim stays as it is.")
    else:
        out = "PASS"
        rd = ("WIRE-FILL: every DUMP word equals its EXPECT word in "
              + " and ".join(f"all {per[h]['matched']} launches on {SHORT[h]}" for h in CARDS)
              + ": PASS; the page says the check is of the store kernel on a DRAM slice, not of the scratchpad image.")
    for h in CARDS:
        if per[h]["refused_patterns"]:
            rd += f" tstore_uniq refused a DRAM slice on {SHORT[h]}: that pattern is dropped (the plan allows it)."
    ac = combine_all(per, allc)
    bits = []
    for h in allc:
        c = per[h]
        if c["status"] == "holds":
            bits.append(f"{short(h)} all {c['matched']} match")
        elif c["status"] == "fails":
            bits.append(f"{short(h)} mismatch in {c['with_mismatch'][0]}")
        else:
            bits.append(f"{short(h)} {c['matched']}/{c['needed']} complete and matching"
                        + (" (no data)" if c.get("missing") else f" (fewer than 3 of {', '.join(c['fills_short'])})"))
        if c["refused_patterns"]:
            bits[-1] += ", tstore_uniq refused a DRAM slice (dropped)"
    ac["reading"] = (f"WIRE-FILL on all cards: {'; '.join(bits)}: {ac['outcome']}"
                     + (f"; over the cards with every fill complete: {ac['over_sufficient']}"
                        if ac["outcome"] == "INSUFFICIENT" and ac["over_sufficient"] else "") + ".")
    return {"item": "WIRE-FILL", "registered_item": "WIRE-FILL", "claims": ["heat-V01"],
            "what": "byte-for-byte check of the store kernel's image on a DRAM slice (--dump-slice 1024, 4 fills x 3 launches)",
            "per_card": per,
            "test": "deterministic: every DUMP word equals its EXPECT word in all 12 launches (256 words each) on each card; "
                    "any mismatch FAILS; fewer than 3 complete launches (256 words, ENERCAT ok) of a fill on a card is INSUFFICIENT",
            "outcome": out, "reading": rd, "all_cards": ac}


def card_dirs(data, expected=EXPECTED):
    """Every card of the campaign (EXPECTED or --cards), then any other card directory present under DATA."""
    present = sorted(n for n in os.listdir(data) if CARD_RE.fullmatch(n) and os.path.isdir(os.path.join(data, n))) \
        if os.path.isdir(data) else []
    return list(expected) + [n for n in present if n not in expected]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--beside", nargs=2, metavar=("A2_DIR", "A3_DIR"))
    ap.add_argument("-q", "--quiet", action="store_true")
    ap.add_argument("--cards", default=",".join(campaign.CAMPAIGN),
                    help="comma-separated cards all_cards expects (default: tools/claims-v3/campaign.py)")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    aw, E, V3, WC = setup(root)
    tests = list(E.EXP1) + list(V3.EXTRA)
    allc = card_dirs(a.data, [c for c in a.cards.split(",") if c])

    cards, ixs, ixns, card_dumps = {}, {}, {}, {}
    for h in allc:
        ixs[h], ixns[h], cards[h], card_dumps[h] = load_card(aw, WC, os.path.join(a.data, h, "wire"), h)
    beside = {}
    if a.beside:
        for h, d in zip(CARDS, a.beside):
            beside[h] = load_beside(aw, d)

    items = []
    for tid, claim, what, fn, null, rng in tests:
        if fn is None:   # P13, descriptive
            per = {}
            for h in allc:
                v, used = values(ixs[h], lambda ix, p: psb(E, aw, ix, p))
                per[h] = dict(E.ci(v), passes=used)
                per[h]["keeps_cannot_rule_out"] = (per[h]["hi99"] > 0.5) if "hi99" in per[h] else None
                if cards[h].get("missing"):
                    per[h]["missing"] = True
            keep = [SHORT[h] for h in CARDS if per[h]["keeps_cannot_rule_out"]]
            rd = (f"P13 {what}: " + "; ".join(f"{SHORT[h]} {fmt(per[h], 'P13')}" for h in CARDS) + ": descriptive; "
                  + (f"upper 99% bound above 50% on {' and '.join(keep)}, so the page keeps 'cannot rule out' there"
                     if keep else "no card has an upper 99% bound above 50% (or too few passes)") + ".")
            clock, note = idle_note(tid, what, allc, cards)
            keep_all = [h for h in allc if per[h]["keeps_cannot_rule_out"]]
            ac = {"cards": allc, "outcome": "DESCRIPTIVE", "keeps_cannot_rule_out_on": keep_all,
                  "reading": (f"P13 on all cards: " + "; ".join(f"{short(h)} {fmt(per[h], 'P13')}" for h in allc)
                              + ": descriptive; " + (f"upper 99% bound above 50% on {', '.join(short(h) for h in keep_all)}"
                                                     if keep_all else "no card has an upper 99% bound above 50% (or too few passes)")
                              + (f". Idle state: {note}" if note else "") + ".")}
            it = {"item": f"WIRE-P1-16/{tid}", "registered_item": "WIRE-P1-16", "claims": [claim], "what": what,
                  "per_card": per, "test": "descriptive (registered): the page keeps 'cannot rule out' if the upper 99% bound stays above 50%",
                  "outcome": "DESCRIPTIVE", "reading": rd, "all_cards": ac, "idle_clock": clock}
            if note:
                it["idle_note"] = note
            if beside:
                it["committed_beside"] = {h: E.ci(values(beside[h], lambda ix, p: psb(E, aw, ix, p))[0]) for h in CARDS}
            items.append(it)
            continue
        per = {}
        for h in allc:
            v, used = values(ixs[h], fn)
            c = dict(E.ci(v), passes=used)
            if len(v) == 1:   # E.ci gives only n below 2; keep the one value for the page
                c["vals"] = [round(float(v[0]), 4)]
            c["status"] = card_status(c, null, rng)
            if "board" in what:
                vn, usedn = values(ixns[h], fn)
                c["secondary_noleak"] = dict(E.ci(vn), passes=usedn, note="descriptive only, decides nothing")
            if cards[h].get("missing"):
                c["missing"] = True
            per[h] = c
        out = combine(per, null)
        clock, note = idle_note(tid, what, allc, cards)
        ac = combine_all(per, allc, null)
        ac["idle_step_cancels"] = tid in STEP_CANCELS
        ac["reading"] = reading_all(tid, what, per, allc, rng, ac, note)
        it = {"item": f"WIRE-P1-16/{tid}", "registered_item": "WIRE-P1-16", "claims": [claim], "what": what,
              "per_card": per, "null": null, "predicted": list(rng),
              "test": test_text(null, rng, tid), "outcome": out,
              "registered_verdict": registered_verdict(per, null, rng),
              "reading": reading(tid, what, per, null, rng, out), "all_cards": ac, "idle_clock": clock}
        if note:
            it["idle_note"] = note
        if beside:
            it["committed_beside"] = {h: E.ci(values(beside[h], fn)[0]) for h in CARDS}
        items.append(it)
    items.append(fill_item(card_dumps, allc, cards))

    sha = {os.path.relpath(p, HERE): hashlib.sha256(open(p, "rb").read()).hexdigest()
           for p in sorted(glob.glob(os.path.join(HERE, "registered", "*.py"))) + [os.path.join(root, "workloads", "enercat", "analyze_wire.py")]}
    res = {"exp": "V3-WIRE", "plan": "docs/reports/data/2026-09-25-claims-v3/PLAN3.md (V3-WIRE) and AMENDMENTS.md (four cards)",
           "reduced_at": datetime.datetime.now().isoformat(timespec="seconds"), "data": os.path.abspath(a.data),
           "beside": list(a.beside) if a.beside else None, "code_sha256": sha,
           "registered_cards": list(CARDS), "all_cards": allc,
           "cards": cards, "outcomes": dict(collections.Counter(i["outcome"] for i in items)),
           "outcomes_all_cards": dict(collections.Counter(i["all_cards"]["outcome"] for i in items)), "items": items}
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, default=float)
    if not a.quiet:
        for h in allc:
            c = cards[h]
            s = c["idle_state"]
            print(f"{h}: " + ("NO DATA; " if c.get("missing") else "")
                  + f"passes ok {c['passes_ok']}, skipped {c['passes_skipped']}, bursts kept {c['bursts_kept']}, "
                  f"dropped {len(c['bursts_dropped'])}, implied clock {c['implied_clock_ghz']}, "
                  f"idle {s.get('idle_minion_mhz')} MHz / busy {s.get('busy_minion_mhz')} MHz")
        for i in items:
            print(f"{i['outcome']:14s} {i['reading']}")
            print(f"  all cards: {i['all_cards']['outcome']:14s} {i['all_cards']['reading']}")
        print(f"-> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
