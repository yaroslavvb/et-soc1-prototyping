#!/usr/bin/env python3
"""anat-X1 / anat-X2 decision script, verifier's revision (25 Sep, written before any run). No card.

    crosscard_v3.py --a2 PASS_DIR... --a3 PASS_DIR... [--requesters 7,24,31] > tests.json

Uses the inventory's crosscard_tests.py for every prediction it gets right, and replaces three:
  P6  -> P6r: row hits only for pairs more than 150 cycles from the estimated refresh start (the published split moves
         from 96/4 to 90/8 or 99.7/1.2 when that estimate moves one 46-cycle bin, which would fail a pass for no
         physical reason); band no-refresh >= 0.98, across a refresh <= 0.02.
  P8 ms7 -> P8b and P8c: with a fence but no wait, the memory-shire effect of 19 Sep is in whether the row is still
         open (memory shires 0, 1, 2, 4: 42/70; 3, 5, 6, 7: 7/58), not in how slow the others are (no difference
         between memory shires among the loads that missed the row, permutation p = 0.23). P8b: open fraction
         (0,1,2,4) minus (3,5,6,7) in [0.20, 0.80], interval excluding 0. P8c: median of the loads that did not find
         the row open, against the closed-row model, in [+6, +30], interval excluding 0.
  X2  -> computed by extra_values.py --x2-only on req<S>/ (the inventory's reducer needs files a req folder lacks).
Each PASS_DIR must also hold l3map (gen_ops.py l3map --lines 8192), which the inventory's reducer requires.
"""
import argparse, json, os, subprocess, sys
INV = "/tmp/claude-1019/-home-yaroslavvb-claude/ed6d06d5-de26-4323-94f1-0dc808eafbda/scratchpad/validate3/inv/anatomy-work"
sys.path.insert(0, INV)
import crosscard_tests as cc  # noqa: E402
_inv_pass_values = cc.pass_values
HERE = os.path.dirname(os.path.abspath(__file__))


def extra(d, *args):
    out = subprocess.run([sys.executable, os.path.join(HERE, "extra_values.py"), "--data", d, *args],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def pass_values(d, reqs):
    v = _inv_pass_values(d, [])            # inventory values, no X2 (its X2 reducer cannot read a req folder)
    for k in ("P6_hit_no_refresh", "P6_hit_refresh", "P8_nodelay_ms7_resid"):
        v.pop(k, None)
    e = extra(d)
    v.pop("P5_closed_minus_open", None)
    v.update({"P6r_hit_no_refresh": e["P6r_hit_no_refresh"], "P6r_hit_refresh": e["P6r_hit_refresh"],
              "P5b_closed_minus_open": e["P5b_closed_minus_open_means"],
              "P8b_open_frac_diff": e["P8b_open_frac_diff"], "P8c_nonopen_resid": e["P8c_nonopen_resid_median"]})
    for s in reqs:
        dd = os.path.join(d, f"req{s}")
        if os.path.isdir(dd):
            x = extra(dd, "--requester", str(s), "--x2-only")
            v[f"X2_s{s}_l3_within4_frac"] = x["l3_within4_frac"]
            v[f"X2_s{s}_dram_within3_frac"] = x["dram_within3_frac"]
    return v


cc.BANDS.pop("P6_hit_no_refresh", None); cc.BANDS.pop("P6_hit_refresh", None); cc.BANDS.pop("P8_nodelay_ms7_resid", None)
cc.BANDS.update({"P6r_hit_no_refresh": (0.98, 1.0, None), "P6r_hit_refresh": (0.0, 0.02, None),
                 "P8b_open_frac_diff": (0.20, 0.80, 0.0), "P8c_nonopen_resid": (6, 30, 0.0)})
# A fraction bounded by 0 or 1 gets a one-sided band: with the inventory's two-sided rule a perfect replication
# fails (five passes at 0.998-1.000 give a 99% interval reaching above 1.0).
INF = float("inf")
cc.BANDS.pop("P5_closed_minus_open", None)
cc.BANDS.update({"P1_l3_within4_frac": (0.97, INF, None), "P2_dram_within3_frac": (0.85, INF, None),
                 "P6r_hit_no_refresh": (0.98, INF, None), "P6r_hit_refresh": (-INF, 0.02, None),
                 "P9_l2_rep0_48_frac": (0.90, INF, None), "P9_l2_rep12_37_frac": (0.90, INF, None),
                 "P5b_closed_minus_open": (10, 13, 0.0)})
for _s in (7, 24, 31):
    cc.BANDS[f"X2_s{_s}_l3_within4_frac"] = (0.97, INF, None)
    cc.BANDS[f"X2_s{_s}_dram_within3_frac"] = (0.85, INF, None)
cc.pass_values = pass_values

if __name__ == "__main__":
    cc.main()
