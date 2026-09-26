#!/usr/bin/env python3
"""RL-f's low edge for the cards outside the 23 Sep catalogue, for tools/claims-v3/rl/reduce.py --low-edge.

    python3 tools/claims-v3/rl/export_low_edge.py --data <dir with one directory per card> --out <results>/inputs/low_edge.json
        [--cards aifoundry1-c1] [--root <tree>]

PLAN3 V3-RL, RL-f: relay own scratchpad against "a bracket low edge", per catalogue pass the mean of
l1fill/stride32/zeros and tstore/scp/zeros, as validate3's rings_relay_extra.py computed it for 23 Sep:

    low edge of pass K = 0.5 * (pJ/B of l1fill/stride32/zeros in pass K + pJ/B of tstore/scp/zeros in pass K)

aifoundry2 and aifoundry3 keep the 23 Sep catalogue (registered; rl/reduce.py reads it itself). Every other campaign
card takes its own V3-CATFULL catalogue (rl/README.md "--low-edge"). The bursts are cut exactly as
tools/claims-v3/catfull/reduce.py cuts them: its load_card (the used blocks only, cflib.pass_bursts: analyze_catalogue's
bursts_of per block, the catfull drop rules), each kept burst's value = cflib.value (pJ/B for these byte rows). A pass
is catfull's complete pass: all three parts p<K>1..p<K>3 used, the two rows possibly in different parts. A complete
pass that lacks a kept burst of either row gives no value (printed). Shape: {"<card>": [one value per pass, pass
order], ...}; "passes", "parts" and "unit" are records, not read by the reducer.
"""
import argparse
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = ("l1fill/stride32/zeros", "tstore/scp/zeros")
TWENTY_THIRD = ("aifoundry2", "aifoundry3")   # the 23 Sep catalogue's cards: RL-f reads their low edge from it


def catfull_reduce():
    """tools/claims-v3/catfull/reduce.py as a module (its load_card and the cflib it imports), unchanged."""
    p = os.path.join(HERE, "..", "catfull", "reduce.py")
    spec = importlib.util.spec_from_file_location("catfull_reduce", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    sys.path.append(os.path.join(HERE, ".."))
    import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cards", default=",".join(c for c in campaign.CAMPAIGN if c not in TWENTY_THIRD),
                    help="cards to export (default: the campaign's cards outside the 23 Sep catalogue)")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--also", default=",".join(TWENTY_THIRD),
                    help="cards printed for comparison only, never written (their registered low edge is 23 Sep's)")
    a = ap.parse_args()
    R = catfull_reduce()
    out = {"unit": "pJ/B", "quantity": "0.5 * (l1fill/stride32/zeros + tstore/scp/zeros) per complete V3-CATFULL "
           "pass (rings_relay_extra.py's low edge), bursts as tools/claims-v3/catfull/reduce.py keeps them",
           "passes": {}, "parts": {}}
    cards = [c for c in a.cards.split(",") if c]
    also = [c for c in a.also.split(",") if c and c not in cards]
    for c in cards + also:
        cd = os.path.join(a.data, c)
        if not os.path.isdir(os.path.join(cd, "catfull")):
            print(f"{c}: no catfull data")
            continue
        recs, _ = R.load_card(a.root, cd, c)
        used = [r for r in recs if r["used"]]
        parts = {}
        for r in used:
            parts.setdefault(r["pass"], set()).add(r["part"])
        complete = sorted(k for k, ps in parts.items()
                          if all(s in ps for s in range(1, max(r["parts"] for r in used if r["pass"] == k) + 1)))
        val = {}   # (pass, row) -> [value, block]
        for r in used:
            for b in r["kept"]:
                if b["cfg"] in ROWS:
                    val.setdefault((b["pass"], b["cfg"]), []).append((b["value"], r["block"]))
        vals, ks, where = [], [], {}
        for k in complete:
            got = [val.get((k, row), []) for row in ROWS]
            if any(len(g) != 1 for g in got):
                print(f"{c} pass {k}: kept bursts {[len(g) for g in got]} of {ROWS}: no value")
                continue
            x = 0.5 * (got[0][0][0] + got[1][0][0])
            vals.append(round(x, 6)); ks.append(k)
            where[k] = {row: {"pj_per_byte": round(g[0][0], 6), "block": g[0][1]} for row, g in zip(ROWS, got)}
        tag = "" if c in cards else "  (comparison only, not written: RL-f uses the 23 Sep catalogue on this card)"
        print(f"{c}: complete passes {complete}; low edge per pass {dict(zip(ks, vals))}"
              + (f", mean {sum(vals) / len(vals):.4f}" if vals else "") + tag)
        for k in ks:
            print(f"   pass {k}: " + ", ".join(f"{row} {w['pj_per_byte']:.4f} (block p{w['block']})" for row, w in where[k].items()))
        if c in cards:
            out[c], out["passes"][c], out["parts"][c] = vals, ks, where
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
