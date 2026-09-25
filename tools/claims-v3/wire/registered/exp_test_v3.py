"""EXP-heat-1 decision script, verifier's version (written 2026-09-25, before any run; supersedes nothing in
heat-work/exp_test.py, it adds to it).

    python3 exp_test_v3.py A2_DIR A3_DIR

Runs the pre-registered tests P1-P13 of heat-work/exp_test.py unchanged, plus:

  P14a/b (heat-22)  link-disjoint set, mesh rail: the d=4 point against the line through d = 1,2,3,5
                    (EQUIVALENCE: PASS only if the 99% interval lies inside +-3% for random data and +-4% for zeros,
                    on EACH card). Needs wsep/p0/hop5 and wsep/p0.5/hop5 in --only.
  P15a/b (heat-V04) mesh rail: [wu d=4 off the line through 1,2,3,6] minus [wsep d=4 off the line through 1,2,3,5],
                    random and zeros: predicted +1.5..+9% (random), +2..+10% (zeros), null 0.
  P16 (heat-42)     mesh rail, one hop: data part wu / wsep - 1 (EQUIVALENCE: 99% interval inside +-5% on each card).

Primary reduction: the page's (analyze_wire.bursts, leakage-corrected board power). Secondary, DESCRIPTIVE ONLY
(printed, never used for a verdict): the same bursts without the leakage correction (bursts(d, leak=False)), because
the correction's burst-to-burst scatter (sd 0.13-0.25 W) dominates the board free-link split in the existing data.
Verdicts: PASS / SIGN-ONLY / FAIL exactly as in exp_test.py; equivalence tests PASS or FAIL. Only new passes are used.
"""
import json, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..", "inv", "heat-work")
sys.dont_write_bytecode = True
sys.path.insert(0, W)
import exp_test as E          # the inventory's pre-registered P1-P13 (unchanged)
import analyze_wire as aw
NK, BK = E.NK, E.BK


def off_line(ix, p, pre, key, ref, d):
    s, i = E.sl(ix, p, pre, key, ref)
    l = d * s + i
    return (E.v(ix, p, f"{pre}{d}", key) - l) / l


EXTRA = [
    ("P14a", "heat-22", "mesh rail: wsep random, d=4 off the line through 1,2,3,5 (equivalence +-3%)",
     lambda ix, p: off_line(ix, p, "wsep/p0.5/hop", NK, (1, 2, 3, 5), 4), None, (-0.03, 0.03)),
    ("P14b", "heat-22", "mesh rail: wsep zeros, d=4 off the line through 1,2,3,5 (equivalence +-4%)",
     lambda ix, p: off_line(ix, p, "wsep/p0/hop", NK, (1, 2, 3, 5), 4), None, (-0.04, 0.04)),
    ("P15a", "heat-V04", "mesh rail: random, wu d4-off minus wsep d4-off",
     lambda ix, p: off_line(ix, p, "wu/p0.5/hop", NK, (1, 2, 3, 6), 4) - off_line(ix, p, "wsep/p0.5/hop", NK, (1, 2, 3, 5), 4), 0, (0.015, 0.09)),
    ("P15b", "heat-V04", "mesh rail: zeros, wu d4-off minus wsep d4-off",
     lambda ix, p: off_line(ix, p, "wu/p0/hop", NK, (1, 2, 3, 6), 4) - off_line(ix, p, "wsep/p0/hop", NK, (1, 2, 3, 5), 4), 0, (0.02, 0.10)),
    ("P16", "heat-42", "mesh rail: one hop, data part wu/wsep - 1 (equivalence +-5%)",
     lambda ix, p: (E.v(ix, p, "wu/p0.5/hop1", NK) - E.v(ix, p, "wu/p0/hop1", NK)) / (E.v(ix, p, "wsep/p0.5/hop1", NK) - E.v(ix, p, "wsep/p0/hop1", NK)) - 1, None, (-0.05, 0.05)),
]


def load_noleak(d):
    h, bs, dr = aw.bursts(d, leak=False)
    ix = collections.defaultdict(dict)
    for b in bs: ix[b["pass"]][b["cfg"]] = b
    return h, ix


if __name__ == "__main__":
    dirs = sys.argv[1:]
    E.EXP1 = E.EXP1 + EXTRA
    res = E.run("exp1", dirs)
    print("\nsecondary reduction, no leakage correction (descriptive, board tests only):")
    cards = dict(load_noleak(d) for d in dirs)
    for tid, claim, what, fn, null, rng in E.EXP1:
        if fn is None or "board" not in what: continue
        per = {}
        for h, ix in cards.items():
            vals = []
            for p in sorted(ix):
                try: vals.append(fn(ix, p))
                except (TypeError, KeyError, ZeroDivisionError): pass
            per[h] = E.ci(vals)
        res[tid]["secondary_noleak"] = per
        print(f"{tid:5s} {what}: " + " | ".join(f"{h[-1]}: {c.get('mean', float('nan')):.4g} [{c.get('lo99', float('nan')):.4g}, {c.get('hi99', float('nan')):.4g}] n{c.get('n')}" for h, c in per.items()))
    json.dump(res, open(os.path.join(HERE, "exp1_v3_result.json"), "w"), indent=1)
