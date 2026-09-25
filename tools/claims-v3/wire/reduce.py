#!/usr/bin/env python3
"""V3-WIRE reduction: the pre-registered items of PLAN3 V3-WIRE, exactly as registered.

    python3 tools/claims-v3/wire/reduce.py --data DIR --out verdicts.json [--root TREE] [--beside A2_DIR A3_DIR] [-q]

DIR holds aifoundry2/ and aifoundry3/ laid out like DATA_ROOT (DIR/<card>/wire/p<N>/ as block.sh writes them). Only
pass directories whose block.json says "ok" are used (p<N>.attempt-* directories, which queue.sh sets aside, never).
--root is the tree whose workloads/enercat/analyze_wire.py reduces the bursts (default: the current directory).
--beside prints the committed 3-pass runs (runner layout, e.g. docs/reports/data/2026-09-24-wire2-aifoundry{2,3}) next
to the new values; they never enter a test (PLAN3 R-new).

Items (PLAN3 V3-WIRE "Pre-registered predictions and decision rules"):
  WIRE-P1-16  reported as one item per registered sub-test, P1-P12 and P14a-P16. The statistics, nulls and ranges are
              registered/exp_test.py EXP1 + registered/exp_test_v3.py EXTRA, imported unchanged (verbatim copies of
              validate3/inv/heat-work/exp_test.py and validate3/heat-verify/exp_test_v3.py; sha256 in README.md). Each
              burst is reduced by workloads/enercat/analyze_wire.bursts() (board power leakage-corrected over idle
              brackets; mesh rail over the last 0.6 s; dropped if any sample in the burst or its brackets left 600 MHz,
              or the sampler starved), and on aifoundry2 also dropped if any launch's implied clock (cycles_max /
              wall_s) is outside 0.595-0.605 GHz (PLAN3 R-clock). Unit: the pass; per card the statistic is computed
              per pass and a 99% t-interval (df = n - 1) formed over the first six passes (by pass number) in which it
              can be computed (6 registered; later passes exist only as re-runs of passes that lost bursts).
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
              a failed launch, INSUFFICIENT until re-run, not a mismatch).
"""
import argparse
import collections
import datetime
import glob
import hashlib
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = ("aifoundry2", "aifoundry3")
SHORT = {"aifoundry2": "a2", "aifoundry3": "a3"}
MAX_REPEATS, MIN_REPEATS = 6, 3
CLOCK_BAND = (0.595, 0.605)
FILLS = ("bern:0.25", "alt:64", "frz", "uq:0.25")
UNITS = {**{k: ("fJ/bit/hop", 1) for k in ("P1", "P2", "P3", "P4", "P5a", "P5b")},
         **{k: ("%", 100) for k in ("P6a", "P6b", "P7a", "P7b", "P7c", "P7d", "P7e", "P7f", "P10", "P12", "P13",
                                    "P14a", "P14b", "P15a", "P15b", "P16")},
         "P8": ("hop", 1), "P9": ("hop", 1), "P11a": ("fJ/mm", 1), "P11b": ("fJ/mm", 1)}
EQUIV_NOTE = "equivalence"


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


def load_card(aw, WC, base, card):
    """New data of one card: {pass: {cfg: burst}} with and without the leakage correction, plus bookkeeping."""
    ix, ixn = collections.defaultdict(dict), collections.defaultdict(dict)
    info = {"passes_ok": [], "passes_skipped": {}, "bursts_kept": 0, "bursts_dropped": [], "implied_clock_ghz": None}
    dumps, ghz = [], []
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
            _, bs, dr = aw.bursts(d)
            _, bsn, _ = aw.bursts(d, leak=False)
        except Exception as e:   # e.g. an empty telemetry file
            info["passes_skipped"][p] = f"unreadable: {e!r}"
            continue
        bad, g = implied_bad(aw, d)
        ghz += g
        if card != "aifoundry2":
            bad = set()
        for x in dr:
            info["bursts_dropped"].append({"pass": p, "cfg": x["cfg"], "why": x["why"]})
        for b in bs:
            if (b["cfg"], b["pass"]) in bad:
                info["bursts_dropped"].append({"pass": p, "cfg": b["cfg"], "why": "implied clock outside 0.595-0.605 GHz"})
                continue
            ix[p][b["cfg"]] = b
            info["bursts_kept"] += 1
        for b in bsn:
            if (b["cfg"], b["pass"]) not in bad:
                ixn[p][b["cfg"]] = b
        info["passes_ok"].append(p)
    if ghz:
        info["implied_clock_ghz"] = [round(min(ghz), 5), round(max(ghz), 5)]
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


def psb(E, aw, ix, p, fam="wsep", key="pj_per_byte"):
    """extra.py's per-second bound (the page's P13 statistic), with reader shires from the burst's own target map."""
    ds = (1, 2, 3, 4)
    z = [E.v(ix, p, f"{fam}/p0/hop{d}", key) for d in ds]
    bw = []
    for d in ds:
        b = ix[p][f"{fam}/p0.5/hop{d}"]
        bw.append(b["bytes_per_s"] / aw.link_sharing(b["target_map"])["reader_shires"])
    return E.line(ds, [z[0] * bw[0] / b for b in bw])[0] / E.line(ds, z)[0]


def fill_item(card_dumps):
    per, bad_any, short = {}, [], []
    for h in CARDS:
        ds = card_dumps.get(h, [])
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
        per[h] = {"launches": len(ds), "complete": len(complete), "needed": need,
                  "matched": sum(1 for r in complete if not r["mismatches"]), "with_mismatch": mism,
                  "first_mismatch": next((r["first_mismatch"] for r in complete if r["mismatches"]), None),
                  "incomplete": [f"p{r['pass_']}/{r['file']}" + (f" ({r['error']})" if r["error"] else "") for r in ds if not r["complete"]],
                  "by_fill": {f: {"launches": len(by.get(f, [])), "matched": sum(1 for r in by.get(f, []) if r["complete"] and not r["mismatches"])} for f in FILLS},
                  "refused_patterns": refused, "n": len(complete)}
        per[h]["fills_short"] = [f for f in FILLS if f not in refused
                                 and sum(1 for r in by.get(f, []) if r["complete"]) < 3]
        if mism:
            bad_any.append(h)
        if per[h]["fills_short"]:
            short.append(h)
    if bad_any:
        out = "FAIL"
        rd = (f"WIRE-FILL: a DUMP word differs from its EXPECT word on {' and '.join(SHORT[h] for h in bad_any)} "
              f"({', '.join(per[h]['with_mismatch'][0] for h in bad_any)}): FAIL, the page drops 'checked byte for byte'.")
    elif short:
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
    return {"item": "WIRE-FILL", "registered_item": "WIRE-FILL", "claims": ["heat-V01"],
            "what": "byte-for-byte check of the store kernel's image on a DRAM slice (--dump-slice 1024, 4 fills x 3 launches)",
            "per_card": per,
            "test": "deterministic: every DUMP word equals its EXPECT word in all 12 launches (256 words each) on each card; "
                    "any mismatch FAILS; fewer than 3 complete launches (256 words, ENERCAT ok) of a fill on a card is INSUFFICIENT",
            "outcome": out, "reading": rd}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--beside", nargs=2, metavar=("A2_DIR", "A3_DIR"))
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    aw, E, V3, WC = setup(root)
    tests = list(E.EXP1) + list(V3.EXTRA)

    cards, ixs, ixns, card_dumps = {}, {}, {}, {}
    for h in CARDS:
        ixs[h], ixns[h], cards[h], card_dumps[h] = load_card(aw, WC, os.path.join(a.data, h, "wire"), h)
    beside = {}
    if a.beside:
        for h, d in zip(CARDS, a.beside):
            beside[h] = load_beside(aw, d)

    items = []
    for tid, claim, what, fn, null, rng in tests:
        if fn is None:   # P13, descriptive
            per = {}
            for h in CARDS:
                v, used = values(ixs[h], lambda ix, p: psb(E, aw, ix, p))
                per[h] = dict(E.ci(v), passes=used)
                per[h]["keeps_cannot_rule_out"] = (per[h]["hi99"] > 0.5) if "hi99" in per[h] else None
            keep = [SHORT[h] for h in CARDS if per[h]["keeps_cannot_rule_out"]]
            rd = (f"P13 {what}: " + "; ".join(f"{SHORT[h]} {fmt(per[h], 'P13')}" for h in CARDS) + ": descriptive; "
                  + (f"upper 99% bound above 50% on {' and '.join(keep)}, so the page keeps 'cannot rule out' there"
                     if keep else "no card has an upper 99% bound above 50% (or too few passes)") + ".")
            it = {"item": f"WIRE-P1-16/{tid}", "registered_item": "WIRE-P1-16", "claims": [claim], "what": what,
                  "per_card": per, "test": "descriptive (registered): the page keeps 'cannot rule out' if the upper 99% bound stays above 50%",
                  "outcome": "DESCRIPTIVE", "reading": rd}
            if beside:
                it["committed_beside"] = {h: E.ci(values(beside[h], lambda ix, p: psb(E, aw, ix, p))[0]) for h in CARDS}
            items.append(it)
            continue
        per = {}
        for h in CARDS:
            v, used = values(ixs[h], fn)
            c = dict(E.ci(v), passes=used)
            if len(v) == 1:   # E.ci gives only n below 2; keep the one value for the page
                c["vals"] = [round(float(v[0]), 4)]
            c["status"] = card_status(c, null, rng)
            if "board" in what:
                vn, usedn = values(ixns[h], fn)
                c["secondary_noleak"] = dict(E.ci(vn), passes=usedn, note="descriptive only, decides nothing")
            per[h] = c
        out = combine(per, null)
        it = {"item": f"WIRE-P1-16/{tid}", "registered_item": "WIRE-P1-16", "claims": [claim], "what": what,
              "per_card": per, "null": null, "predicted": list(rng),
              "test": test_text(null, rng, tid), "outcome": out,
              "registered_verdict": registered_verdict(per, null, rng),
              "reading": reading(tid, what, per, null, rng, out)}
        if beside:
            it["committed_beside"] = {h: E.ci(values(beside[h], fn)[0]) for h in CARDS}
        items.append(it)
    items.append(fill_item(card_dumps))

    sha = {os.path.relpath(p, HERE): hashlib.sha256(open(p, "rb").read()).hexdigest()
           for p in sorted(glob.glob(os.path.join(HERE, "registered", "*.py"))) + [os.path.join(root, "workloads", "enercat", "analyze_wire.py")]}
    res = {"exp": "V3-WIRE", "plan": "docs/reports/data/2026-09-25-claims-v3/PLAN3.md (V3-WIRE)",
           "reduced_at": datetime.datetime.now().isoformat(timespec="seconds"), "data": os.path.abspath(a.data),
           "beside": list(a.beside) if a.beside else None, "code_sha256": sha,
           "cards": cards, "outcomes": dict(collections.Counter(i["outcome"] for i in items)), "items": items}
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, default=float)
    if not a.quiet:
        for h in CARDS:
            c = cards[h]
            print(f"{h}: passes ok {c['passes_ok']}, skipped {c['passes_skipped']}, bursts kept {c['bursts_kept']}, "
                  f"dropped {len(c['bursts_dropped'])}, implied clock {c['implied_clock_ghz']}")
        for i in items:
            print(f"{i['outcome']:14s} {i['reading']}")
        print(f"-> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
