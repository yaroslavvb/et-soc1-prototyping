#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q145(b) fix, v2 of term_s_note2.py's fit99 (a new file beside term_s_note2.py, 1c43f5cb, which stays as committed).

term_s_note2.py's fit99 stopped on its first run (in a job started 03:51:56 PST) before writing any of its outputs: its own check keyed the
committed steps by (run, item), and E102 holds an fp32 and an fp16 step under one name, bj_0, so it compared an fp16 step with an
fp32 one. This file keys them by (run, format, item) and changes nothing else: the census, the patch of
term_s_v2's step list and FL3 lookup, term_s_v2.run_fit, the outputs' names and the checks and compare commands are term_s_note2.py's,
imported unchanged. Every figure it writes is POST HOC (REGISTRATION.md.dated-note-2.md).

    python3 -B term_s_note2_v2.py fit99 --out <dir> --tmp <dir>
    python3 -B term_s_note2_v2.py census | checks --out <dir> | compare ...   (term_s_note2.py's, unchanged)

SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import term_s_note2 as N2  # noqa: E402  (1c43f5cb, unchanged)

TS, QD, load = N2.TS, N2.QD, N2.load


def fit99(out_dir, tmp):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    cen = N2.census()
    added = N2.patch(cen)
    if sorted(added) != ["ix_b0", "ix_b16", "ix_b22", "ix_b8"]:
        N2.stop(f"the census's E67 steps are {added}, not the four ix_b margins: write that up before any fit")
    summary = {"label": "POST HOC: the registered fit (term_s_v2.run_fit, unchanged) on the 99 steps REGISTRATION.md section 3.1 "
                        "defines, the 95 of term_s_v2 plus E67's four; written after the 95-step outputs and the verifier's reading",
               "added_steps": ["E67:fp32." + a for a in sorted(added)], "code": "term_s_note2_v2.py (fit99), term_s_note2.py (the rest)"}
    for footing, base in (("reg", None), ("law", os.path.join(QD, "m10-law.json"))):
        res, name = TS.run_fit(tmp, footing, base)
        com = load(os.path.join(QD, f"term-s-{footing}.json"))
        old = {(s["run"], s["fmt"], s["item"]): s for s in com["steps"]}
        if len(old) != len(com["steps"]):
            N2.stop(f"{footing}: the committed steps' keys are not unique")
        worst = 0.0
        for s in res["steps"]:
            o = old.get((s["run"], s["fmt"], s["item"]))
            if o is None:
                continue
            for q in ("meas_w", "pred_w", "r_w"):
                worst = max(worst, abs(float(s[q]) - float(o[q])))
        n_common = sum(1 for s in res["steps"] if (s["run"], s["fmt"], s["item"]) in old)
        if n_common != 95 or worst > 1e-12 or res["n_steps"] != 99:
            N2.stop(f"{footing}: the 95 committed steps do not reproduce (common {n_common}, worst {worst}) or n is {res['n_steps']}")
        res["note2"] = dict(summary, footing=footing, committed_95_reproduce={"steps": n_common, "worst_abs_w": worst})
        fn = f"note2-term-s-{footing}-99.json"
        json.dump(res, open(os.path.join(out_dir, fn), "w"), indent=1, default=str)
        e = res["entry"]
        summary[footing] = {"file": fn, "n_steps": res["n_steps"], "best": e["best_form"], "enters": e["enters"],
                            "E1": {k: e["E1"][k] for k in ("d_rms_w", "lo95", "hi95", "holds")}, "E2": e["E2"],
                            "E3": {k: e["E3"][k] for k in ("d_rms_w", "lo95", "hi95", "holds", "rms_M10_heldout_w", "rms_M10S_w")},
                            "forms_all": {f: res["by_form"][f]["all"] for f in TS.FORMS},
                            "run_E67": {f: res["by_form"][f].get("run E67") for f in TS.FORMS},
                            "sigma_S_w": res["sigma_S_w"], "committed_95_reproduce": {"steps": n_common, "worst_abs_w": worst}}
        p8 = res["posthoc_pool8"]
        if footing == "reg":
            summary[footing]["posthoc_pool8"] = {r: (p8[r]["class_S_N1"] if r in ("E171", "E172") else
                                                     {k: v for k, v in p8[r]["class_S_scored"].items() if k != "tiles"})
                                                 for r in ("E171", "E172", "E173", "E174")}
            summary[footing]["B1"] = {r: {"F1": p8[r]["F1_B1"], "F1_without_S": p8[r]["F1_without_S"]} for r in ("E171", "E172")}
        else:
            summary[footing]["posthoc_pool8_law"] = {r: p8[r]["class_S_N1"] for r in ("E171", "E172")}
    json.dump({"census": cen, "fit99": summary}, open(os.path.join(out_dir, "note2-census-fit99.json"), "w"), indent=1, default=str)
    print(json.dumps({"census": cen["summary"], "fit99": {k: v for k, v in summary.items() if k in ("reg", "law")}}, indent=1, default=str))
    return 0


def main(argv):
    if argv and argv[0] == "fit99":
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd")
        ap.add_argument("--out", required=True)
        ap.add_argument("--tmp", required=True)
        a = ap.parse_args(argv)
        return fit99(a.out, a.tmp)
    return N2.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
