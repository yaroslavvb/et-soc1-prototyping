#!/usr/bin/env python3
"""The heat-per-millimetre reduction (analyze_wire.analyze) over the version-3 claims check's wire passes.

    python3 workloads/enercat/analyze_wire_v3.py docs/reports/data/2026-09-25-claims-v3/raw \\
        --out docs/reports/data/2026-09-24-wire-energy/wire3.json --pitch-x-mm 3.73 --pitch-y-mm 3.70

RAW is the check's layout, RAW/<card>/wire/p<N>/, one directory per pass as tools/claims-v3/wire/block.sh writes it
(tools/claims-v3/wire/README.md). analyze_wire.py reads the runner's layout (one directory per card and run, passes
inside runs.jsonl) and cannot tell aifoundry1's two cards apart by its directory name, so this adapter reads the passes
and hands the bursts to analyze_wire.analyze() unchanged:

  cards    the campaign's (tools/claims-v3/campaign.py: aifoundry2, aifoundry3, aifoundry1-c1); --cards overrides.
  passes   each card's passes whose block.json says "ok", the first six by pass number (reduce.MAX_REPEATS), as the
           check's reduction uses them.
  bursts   tools/claims-v3/wire/reduce.py load_card(): every burst reduced by analyze_wire.bursts() and kept or dropped
           exactly as the check's reduction keeps it (the registered rules on aifoundry2 and aifoundry3, the four-card
           rules on aifoundry1-c1: tools/claims-v3/wire/README.md, "Four cards"); the burst's host is the card's name.
  no-leak  the same bursts without the leakage correction (load_card's second set) for the "sensitivity" block, as
           analyze_wire.py's main() does, plus that block's disjoint_flows (descriptive; the check's secondary_noleak).

The 24 Sep runs (E31, E32: docs/reports/data/2026-09-24-wire{,2}-aifoundry{2,3}) are not pooled with these passes: the
check re-ran every pass and its registered test uses "only the new data ... nothing is pooled with E31/E32"
(tools/claims-v3/wire/registered/exp_test.py; README "Four cards"). The version-3 passes run 28 of the second run's
configurations (all pairs at P = 0, 1/2 and 1 over 0-6 hops; link-disjoint pairs at P = 0 and 1/2 over 1-5 hops), so
the blocks this output leaves empty (the first run's patterns, the two-term model over five densities and the frozen
line, the axes) stay in wire.json, the 24 Sep analysis, which the page keeps as the record of those patterns.

Added to analyze()'s output: "source" (what was read), "cards" (passes used and bursts kept and dropped per card), and
"loaded" (the all-pairs set over 1, 2, 3, 4 and 6 hops per card and pass, per bit per hop: random data, zeros and their
difference; the loaded-mesh counterpart of disjoint_flows' link-disjoint set, fitted over the distances the all-pairs
set ran).

This adapter leaves analyze_wire.py unchanged (its sha256 is recorded in the check's results/wire.json).
"""
import argparse
import collections
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "wire"))
import analyze_wire as AW   # noqa: E402  the page's reduction, unchanged
import reduce as R          # noqa: E402  the check's per-card loader and drop rules


def load(raw, cards):
    """Bursts of every card (with and without the leakage correction), per-card bookkeeping and drops."""
    aw, _E, _V3, WC = R.setup(ROOT)
    allb, nob, dropped, info = [], [], {}, {}
    for h in cards:
        ix, ixn, ci, _dumps = R.load_card(aw, WC, os.path.join(raw, h, "wire"), h)
        passes = sorted(ix)[:R.MAX_REPEATS]
        for p in passes:
            allb += [dict(b, host=h) for _, b in sorted(ix[p].items())]
            nob += [dict(b, host=h) for _, b in sorted(ixn.get(p, {}).items())]
        dropped[h] = [dict(x, dir=os.path.join(raw, h, "wire", f"p{x['pass']}")) for x in ci["bursts_dropped"] if x["pass"] in passes]
        info[h] = {"passes_used": passes, "passes_skipped": ci["passes_skipped"], "bursts_kept": sum(len(ix[p]) for p in passes),
                   "bursts_dropped": len(dropped[h]), "drop_rule": ci["drop_rule"], "implied_clock_ghz": ci["implied_clock_ghz"],
                   "idle_minion_mhz": ci["idle_state"].get("idle_minion_mhz"), "idle_noc_mhz": ci["idle_state"].get("idle_noc_mhz")}
    return allb, nob, dropped, info


def loaded(allb, hosts):
    """The all-pairs set (wu) over d = 1, 2, 3, 4, 6, per card and pass: fJ per bit per hop for random data, zeros and
    their difference, pooled as analyze() pools (analyze_wire.pool)."""
    by = collections.defaultdict(list)
    for b in allb:
        by[b["cfg"]].append(b)
    out = {}
    for key in ("pj_per_byte", "noc_pj_per_byte"):
        v5, v0, v1, vd = {}, {}, {}, {}
        for h in hosts:
            sl = {q: {f["pass"]: f["slope"] for f in AW.per_pass_slopes(
                [b for cfg, lst in by.items() if cfg.startswith(f"wu/p{q}/") for b in lst if b["host"] == h], key, (1, 2, 3, 4, 6))}
                for q in ("0", "0.5", "1")}
            v5[h] = [x / 8 * 1000 for x in sl["0.5"].values()]
            v0[h] = [x / 8 * 1000 for x in sl["0"].values()]
            v1[h] = [x / 8 * 1000 for x in sl["1"].values()]
            vd[h] = [(sl["0.5"][k] - sl["0"][k]) / 8 * 1000 for k in sl["0.5"] if k in sl["0"]]
        out[key] = {"random_fj_per_bit_hop": AW.pool(v5), "zeros_fj_per_bit_hop": AW.pool(v0), "ones_fj_per_bit_hop": AW.pool(v1),
                    "random_minus_zeros_fj_per_bit_hop": AW.pool(vd), "hops": [1, 2, 3, 4, 6]}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("raw", help="the check's raw directory: RAW/<card>/wire/p<N>/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cards", default=",".join(R.EXPECTED), help="comma-separated cards (default: the campaign's)")
    ap.add_argument("--pitch-x-mm", type=float, default=None)
    ap.add_argument("--pitch-y-mm", type=float, default=None)
    a = ap.parse_args()
    cards = [c for c in a.cards.split(",") if c]
    allb, nob, dropped, info = load(a.raw, cards)
    out = AW.analyze(allb, dropped, a)
    alt = AW.analyze(nob, {}, a)
    keys = ("toggle_fj_per_bit_transition_hop", "ones_fj_per_one_bit_hop", "s0_pj_per_byte_hop", "random_bit_fj_per_bit_hop")
    out["sensitivity"] = {"no_leak_correction": {st: {src: {k: ({q: alt["model"][st][src][k][q] for q in ("mean", "lo", "hi")}
                                                                | {"per_card": {h: c["mean"] for h, c in alt["model"][st][src][k]["per_card"].items()}})
                                                               if alt["model"][st][src][k] else None for k in keys}
                                                         for src in ("board", "noc_rail")} for st in ("v1", "v2")},
                          "disjoint_flows": alt["disjoint_flows"]}
    out["loaded"] = loaded(allb, out["hosts"])
    out["cards"] = info
    rel = os.path.relpath(os.path.abspath(a.raw), ROOT)
    out["source"] = {"raw": rel, "layout": "RAW/<card>/wire/p<N>/ (tools/claims-v3/wire/README.md)",
                     "cards": cards, "passes": "block.json ok, the first six by pass number",
                     "bursts": "tools/claims-v3/wire/reduce.py load_card(): the check's drop rules per card",
                     "adapter": "workloads/enercat/analyze_wire_v3.py"}
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"bursts kept: {len(allb)}; " + "; ".join(f"{h}: passes {info[h]['passes_used']}, kept {info[h]['bursts_kept']}, dropped {info[h]['bursts_dropped']}" for h in cards))
    for key, v in out["disjoint_flows"].items():
        for fam, e in v.items():
            if e["random_minus_zeros_fj_per_bit_hop"]:
                print(f"{fam:10s} ({key:15s}): data {e['random_minus_zeros_fj_per_bit_hop']['mean']:6.1f}  zeros {e['zeros_fj_per_bit_hop']['mean']:6.1f}"
                      f"  random {e['random_fj_per_bit_hop']['mean']:6.1f} fJ/bit/hop   "
                      + "  ".join(f"{h} {c['mean']:.1f}" for h, c in e["random_minus_zeros_fj_per_bit_hop"]["per_card"].items()))
    for key, e in out["loaded"].items():
        print(f"loaded 1-6 ({key:15s}): data {e['random_minus_zeros_fj_per_bit_hop']['mean']:6.1f}  zeros {e['zeros_fj_per_bit_hop']['mean']:6.1f}"
              f"  random {e['random_fj_per_bit_hop']['mean']:6.1f}  ones {e['ones_fj_per_bit_hop']['mean']:6.1f} fJ/bit/hop")


if __name__ == "__main__":
    main()
