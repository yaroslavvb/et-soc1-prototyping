#!/usr/bin/env python3
"""Q140(x): which pool-7 tiles are left out on aifoundry2 by section 22's 82 W stop, from the frozen predictions.

    python3 -B admission_aifoundry2.py [<predictions-blind7-aifoundry2.json>] [--out <admission-aifoundry2-82w.json>]

The rule (registered with the predictions, Q140(x)): a tile is LEFT OUT on aifoundry2 (it does not run there as designed) if its
predicted 95% upper peak board power exceeds 82 W under any of
  - M9's primary aifoundry2 prediction (Q140(l)'s part, the a2_q140l block: M8's peak rule, unchanged, on M9's D at its band top),
  - M9 through M8's frozen relation (the same peak rule on the same D: it must agree with the line above), or
  - M8 as frozen (its own D at its band top),
the union, because 82 W is a safety stop (section 22: aifoundry2's PMIC over-power configuration is unknown and Q138's bursts
peaked at 87.95-87.98 W). M7 and M6 predict no peak. Tiles whose EXPECTED peak passes 82 W, and those within 2 W of it at 95%, are
listed too. Writes the per-tile values and the priority-1 coverage per class that stays on aifoundry2. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LINE = 82.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pred", nargs="?", default=os.path.join(HERE, "predictions-blind7-aifoundry2.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "admission-aifoundry2-82w.json"))
    a = ap.parse_args()
    raw = open(a.pred, "rb").read()
    P = json.loads(raw)
    assert P["card"] == "aifoundry2", P["card"]
    primary = P.get("a2_part", {}).get("primary")
    per, out_by, exp_over, near = {}, {}, {}, []
    for n, r in sorted(P["tiles"].items()):
        q = r["M9"].get("a2_q140l") or {}
        rows = {"M9_a2_q140l": (q.get("peak_board_w"), q.get("peak_board_hi95_w")),
                "M9_m8_relation": (r["M9"]["peak_board_w"], r["M9"]["peak_board_hi95_w"]),
                "M8": (r["M8"]["peak_board_w"], r["M8"]["peak_board_hi95_w"])}
        if not q:
            raise SystemExit(f"{n}: no a2_q140l block (run predict_blind7.py with --a2-terms)")
        if abs(rows["M9_a2_q140l"][1] - rows["M9_m8_relation"][1]) > 0.01:
            raise SystemExit(f"{n}: M9's two peak paths disagree: {rows}")
        by = [k for k, (_, hi) in rows.items() if hi > LINE]
        ex = [k for k, (e, _) in rows.items() if e > LINE]
        hi = max(h for _, h in rows.values())
        per[n] = {"type": r["type"], "priority": r["priority"], "case": r["case"],
                  "peak_expected_w": {k: v[0] for k, v in rows.items()}, "peak_hi95_w": {k: v[1] for k, v in rows.items()},
                  "left_out": bool(by), "left_out_by": by,
                  "M9_primary_burst": {"mhz": q["burst_mhz"], "board_w": q["burst_board_w"], "group": q["group"]},
                  "M8_burst": {"mhz": r["M8"]["burst_mhz"], "board_w": r["M8"]["burst_board_w"]}}
        if by:
            out_by[n] = by
        if ex:
            exp_over[n] = ex
        if not by and hi > LINE - 2.0:
            near.append([n, hi])
    kept = [n for n in per if not per[n]["left_out"]]
    cov = {}
    for n in per:
        if per[n]["priority"] == 1:
            c = str(per[n]["case"]).split()[0]  # the manifest's case is its class letter, then its description
            cov.setdefault(c, {"priority1": 0, "kept_on_aifoundry2": 0})
            cov[c]["priority1"] += 1
            cov[c]["kept_on_aifoundry2"] += int(not per[n]["left_out"])
    res = {"_what": "Q140(x): pool 7's tiles left out on aifoundry2 by section 22's 82 W stop, from the frozen predictions",
           "rule": "left out if the predicted 95% upper peak board power exceeds 82 W under M9's primary aifoundry2 prediction (Q140(l)'s "
                   "part), M9 through M8's relation, or M8 as frozen (the union; M7 and M6 predict no peak)",
           "source": os.path.basename(a.pred), "source_sha256": hashlib.sha256(raw).hexdigest(), "m9_primary_on_aifoundry2": primary,
           "line_w": LINE, "n_tiles": len(per), "left_out": sorted(out_by), "left_out_by": out_by,
           "expected_peak_over_82w": exp_over, "kept_within_2w_at_95": sorted(near, key=lambda x: -x[1]),
           "highest_hi95_kept_w": max((max(per[n]["peak_hi95_w"].values()), n) for n in kept) if kept else None,
           "n_kept": len(kept), "priority1_coverage_by_case": dict(sorted(cov.items())), "per_tile": per}
    json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
    left = []
    for n, v in sorted(out_by.items()):
        hi, ex = max(per[n]["peak_hi95_w"].values()), max(per[n]["peak_expected_w"].values())
        left.append(f"{n} ({'+'.join(v)}; 95% {hi:.2f} W, expected {ex:.2f} W, p{per[n]['priority']})")
    near_s = ", ".join(f"{n} {h:.2f} W" for n, h in res["kept_within_2w_at_95"]) or "none"
    cov_s = ", ".join(f"{c} {v['kept_on_aifoundry2']}/{v['priority1']}" for c, v in res["priority1_coverage_by_case"].items())
    print(f"aifoundry2 82 W stop: {len(out_by)} of {len(per)} tiles left out: " + (", ".join(left) or "none"))
    print(f"  expected peak over 82 W: {sorted(exp_over) or 'none'}; kept within 2 W of the line at 95%: {near_s}")
    print(f"  highest 95% peak kept: {res['highest_hi95_kept_w']}; priority-1 coverage kept per case: {cov_s}")


if __name__ == "__main__":
    main()
