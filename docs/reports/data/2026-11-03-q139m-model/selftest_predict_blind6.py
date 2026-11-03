#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(m): self-test of predict_blind6.py on blind pool 5 (tools/claims-v3/kinds/blind5, its counts-blind5.json).

M7 and M6 through predict_blind6.py must reproduce Q138(x)'s frozen pool-5 predictions (predictions-blind5-<card>.json, written
by Q138(m)'s predict_blind5.py) field for field on all three cards; M8's numbers on pool 5 are in sample (pool 5 is in its fit)
and test nothing.

    python3 selftest_predict_blind6.py <scratch dir>
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
B5 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind5")
FIELDS = {"a3": ("D_w", "D_95", "dT_win_c", "dT_win_95", "D600_a3_footing_w"),
          "a2": ("burst_mhz", "burst_mhz_95", "burst_board_w", "burst_board_95", "burst_D_w", "burst_die_rise_c", "burst_die_rise_95")}


def main():
    out = os.path.abspath(sys.argv[1])
    allok = True
    for card, cd in (("aifoundry3", "a3"), ("aifoundry1c1", "a3"), ("aifoundry2", "a2")):
        od = os.path.join(out, card)
        r = subprocess.run([sys.executable, os.path.join(HERE, "predict_blind6.py"), B5, card, "--counts",
                            os.path.join(B5, "counts-blind5.json"), "--out", od], capture_output=True, text=True, cwd=ROOT)
        if r.returncode:
            print(card, "FAILED", r.stderr[-800:])
            allok = False
            continue
        new = json.load(open(os.path.join(od, f"predictions-{card}.json")))["tiles"]
        old = json.load(open(os.path.join(B5, f"predictions-blind5-{card}.json")))["tiles"]
        n = bad = 0
        for t, rec in old.items():
            for m in ("M7", "M6"):
                for f in FIELDS[cd]:
                    if f not in rec[m]:
                        continue
                    n += 1
                    if new[t][m].get(f) != rec[m][f]:
                        bad += 1
                        if bad <= 5:
                            print(f"  {card} {t} {m} {f}: frozen {rec[m][f]} vs predict_blind6 {new[t][m].get(f)}")
        m8n = sum(1 for t in new if "M8" in new[t])
        print(f"{card}: {len(old)} tiles, {n} M7/M6 fields compared, {bad} differ; M8 predicted for {m8n} tiles"
              + (f"; M8 peak over 82 W (95% upper) on {sum(1 for t in new if new[t].get('M8', {}).get('peak_over_82w'))} tiles" if cd == "a2" else ""))
        allok &= bad == 0
    print("SELFTEST", "PASS" if allok else "FAIL")


if __name__ == "__main__":
    main()
