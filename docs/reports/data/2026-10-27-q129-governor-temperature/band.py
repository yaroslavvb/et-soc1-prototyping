#!/usr/bin/env python3
"""Q129: every aifoundry2 per-flipped-bit price on ONE leakage slope, and the band it gives.

Collects E60's (re-reduced here), E68's (already published as a sensitivity) and E63's (re-reduced here)
prices at E66's measured idle slope and at each source's own registered slope, and prints the band.

  python3 band.py <repo-root> <e60-sens.json> <e63-s1.json> <e63-s2.json> --out per-bit-band.json
"""
import argparse
import json
import os

E66_SLOPE = 0.2936     # E66, 18 cycles, 51-58 C, median
E66_RANGE = (0.2917, 0.2961)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("e60")
    ap.add_argument("e63_s1")
    ap.add_argument("e63_s2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    D = os.path.join(a.repo, "docs/reports/data")
    E60 = json.load(open(a.e60))
    rows = []

    # ── E60, this card's lq ladder and its x-in energy. Registered slope: --leak auto = 0.442 (its own
    #    busy-window estimate). Both pass-gate modes are reported; "live" is the registered gate re-applied.
    for mode in ("live", "frozen"):
        reg = E60[mode]["0.442"]
        new = E60[mode]["0.2936"]
        for key, label, scale in (("designed", "E60 lq, per designed flipped B bit", 1e15),
                                  ("bus", "E60 lq, per bus flip (RTL)", 1e15),
                                  ("nets", "E60 lq, per net toggle (RTL)", 1e15)):
            rows.append({"source": "E60", "gate": mode, "item": label,
                         "registered_slope": 0.442, "registered_fJ": reg["lq"][key]["fJ"],
                         "registered_se_fJ": (reg["lq"][key]["se_J"] or 0) * 1e15,
                         "e66_slope": E66_SLOPE, "e66_fJ": new["lq"][key]["fJ"],
                         "e66_se_fJ": (new["lq"][key]["se_J"] or 0) * 1e15,
                         "passes": len(new["passes"]), "runs_kept": new["n_runs_kept"]})
        rows.append({"source": "E60", "gate": mode, "item": "E60 e_in, per x-in port bit",
                     "registered_slope": 0.442, "registered_fJ": reg["ec"]["e_in"]["fJ"],
                     "registered_se_fJ": (reg["ec"]["e_in"]["se_J"] or 0) * 1e15,
                     "e66_slope": E66_SLOPE, "e66_fJ": new["ec"]["e_in"]["fJ"],
                     "e66_se_fJ": (new["ec"]["e_in"]["se_J"] or 0) * 1e15,
                     "passes": len(new["passes"]), "runs_kept": new["n_runs_kept"]})

    # ── E68, already published as a labelled sensitivity (leak-sensitivity.txt); quoted, not recomputed
    E68_REG, E68_NEW = {}, {}
    txt = open(os.path.join(D, "2026-10-27-e68-stage-map/leak-sensitivity.txt")).read().splitlines()
    # only the FIRST table in that file is the fJ-per-flipped-bit one; the second is dP in watts
    head, done = None, False
    for ln in txt:
        if done:
            break
        if ln.startswith("slope W/C") and head is None:
            head = ln.split()[2:]
        elif head and ln.startswith("sm_"):
            parts = ln.replace("+-", " ").split()
            name, vals = parts[0], parts[1:]
            pairs = [(float(vals[2 * i]), float(vals[2 * i + 1])) for i in range(len(vals) // 2)]
            if len(pairs) == len(head):
                E68_NEW[name] = dict(zip(head, pairs))
            if name == "sm_pi_sgn":
                done = True
    for name, d in E68_NEW.items():
        rows.append({"source": "E68", "gate": "registered", "item": f"E68 {name}, per flipped bit",
                     "registered_slope": 1.508, "registered_fJ": d["1.508"][0],
                     "registered_se_fJ": d["1.508"][1],
                     "e66_slope": 0.294, "e66_fJ": d["0.294"][0], "e66_se_fJ": d["0.294"][1],
                     "passes": None, "runs_kept": 453})

    # ── E63, the camera session's board step. Its published prices carry NO leakage correction at all.
    for sess, path in (("s1", a.e63_s1), ("s2", a.e63_s2)):
        E = json.load(open(path))
        for b, e in E["blocks"].items():
            if not e["slopes"]["0.0"]["fj_per_flip"]:
                continue
            rows.append({"source": f"E63 {sess}", "gate": "registered",
                         "item": f"E63 {b}, per designed flipped B bit",
                         "registered_slope": 0.0, "registered_fJ": e["slopes"]["0.0"]["fj_per_flip"],
                         "registered_se_fJ": e["slopes"]["0.0"]["fj_se"],
                         "e66_slope": E66_SLOPE, "e66_fJ": e["slopes"]["0.2936"]["fj_per_flip"],
                         "e66_se_fJ": e["slopes"]["0.2936"]["fj_se"],
                         "dT_c": e["dT_c_mean"], "passes": None, "runs_kept": e["n_laps"]})

    def band(sel):
        v = [r["e66_fJ"] for r in rows if sel(r)]
        return (round(min(v), 1), round(max(v), 1), len(v)) if v else None

    whole = lambda r: ("designed flipped B bit" in r["item"]) and r.get("gate") in ("live", "registered")
    stage = lambda r: r["source"] == "E68"
    out = {"e66_slope_W_per_C": E66_SLOPE, "e66_slope_range": E66_RANGE, "rows": rows,
           "band_whole_word_designed_bit_fJ": band(whole),
           "band_e68_stage_resolved_fJ": band(stage),
           "note": ("Every row is aifoundry2, the card E66 measured. A price 'per designed flipped B bit' "
                    "divides the measured watts by the designed B-side flips per op; E68's rows are the "
                    "stage-resolved prices for named bit groups, so they bracket the whole-word number "
                    "from both sides rather than agreeing with it.")}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print("Every aifoundry2 per-flipped-bit price, at its own registered leakage slope and at E66's "
          "measured 0.2936 W/C")
    print("%-9s %-40s %-7s %11s %7s %13s %8s %6s"
          % ("source", "item", "gate", "registered", "slope", "at E66 0.2936", "change", "n"))
    for r in rows:
        ch = (r["e66_fJ"] / r["registered_fJ"] - 1) * 100 if r["registered_fJ"] else 0
        print("%-9s %-40s %-7s %8.3f fJ %7.3f %10.3f fJ %+7.1f%% %6s"
              % (r["source"], r["item"].split(" ", 1)[1], r["gate"], r["registered_fJ"],
                 r["registered_slope"], r["e66_fJ"], ch, r["runs_kept"]))
    print("")
    print("band, whole-word designed-bit prices at E66's slope: %s-%s fJ over %d rows"
          % out["band_whole_word_designed_bit_fJ"])
    print("band, E68's stage-resolved prices at E66's slope:    %s-%s fJ over %d rows"
          % out["band_e68_stage_resolved_fJ"])
    return 0


if __name__ == "__main__":
    main()
