#!/usr/bin/env python3
"""E186's data README, dated note 1 (Mon 9 Nov 2026, after the data verifier): the figures the note quotes, read again from this
directory's committed files. Post hoc: it decides nothing, scores nothing and changes no committed file. Standard library only; it
imports no lab module.

It reads this directory's README.md (as text: the lines the note cites), trains-e186.json and scored-e186.json, and, as data only,
the kit's frozen forecasts (tools/claims-v3/e186/forecast-e186.json: the candidates' rates).

    python3 -B docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/posthoc_note1_e186.py [--out <dir>]

Section 0 finds each README line the note cites by a short anchor and prints only the anchor and its line. Section 1 gives each
train's measured rate over the candidates' rate for its type, the range by family against the README's printed figures, and the rate
the scorer used. Section 2 gives E186-SPLIT3's and E186-SPLIT63's beta_A and beta_B intervals, whether each side's two intervals
overlap, and, as post hoc arithmetic that no rule reads, each side's difference between the two products with its standard error.
Section 3 gives E186-S23R's two intervals and the gap between them.

It writes posthoc-note1-e186.json and posthoc-note1-e186.txt beside itself (or in --out), with paths relative to this directory or the
repository's top and no run time, so a re-run from the same tree writes them byte for byte. Exit 0 when it ran, 2 on a usage error.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
D = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
FORECAST = "tools/claims-v3/e186/forecast-e186.json"
ORDER = ["H16", "S23", "Q63-sign", "Q63-swap", "B15-B7", "B23-B15", "Q3-sign", "Q3-swap", "A15-A7", "A23-A15"]
# The README lines the note cites: (label, first line, last line, an anchor that must occur on the first line). The anchors are short
# and neutral; the lines' own text is never copied into the outputs.
ANCHORS = [
    ("plain words: the int8 price per held bit", 74, 76, "the price per bit moves with"),
    ("plain words: E186-S23R", 77, 78, "Moving 16 bits costs less than 16/23"),
    ("reported beside: rates against the candidates'", 96, 98, "Each train's lines at s = 1"),
    ("reported beside: the head of the arms' bullet", 99, 99, "**october-forecast-model's arms**"),
    ("reported beside: the note M1 sub-bullet", 100, 101, "**Note M1, v4**"),
    ("reported beside: the note M2 sub-bullet", 102, 104, "**Note M2**"),
    ("reported beside: the passage set aside, from", 103, 104, "Each arm's"),
    ("reported beside: the arms table", 106, 111, "| arm | trains read |"),
    ("reported beside: the arms table's parenthesis", 113, 113, "(error = the arm's"),
    ("the readings, labelled", 117, 123, "**Blind:**"),
    ("departures: the first wait call", 170, 172, "**The first wait call was stopped at the desk.**"),
    ("card and post: the login sentence", 208, 208, "No login is named in any file."),
    ("files: note M1's row", 245, 245, "| `arm-m1-e186.json`"),
    ("files: note M2's row", 246, 246, "| `arm-m2-e186.json`"),
    ("what it does to predicting power: M12's structure", 259, 262, "**M12's structure carries"),
    ("what it does to predicting power: beta_A alone", 260, 260, "beta_A 0.0054 at product 3"),
    ("what it does to predicting power: S23R's clause", 261, 261, "moving 16 bits costs less than 16/23"),
    ("what it does to predicting power: the bullet set aside", 263, 265, "**october-forecast-model (reported):**"),
    ("what it does to predicting power: the last bullet", 266, 266, "**E186 is the first blind test"),
]


def load(rel, top=False):
    with open(os.path.join(TOP if top else D, rel), encoding="utf-8") as f:
        return json.load(f)


def f4(x):
    return f"{x:.4f}"


def sgn(x, n=5):
    return f"{x:+.{n}f}"


def main(argv):
    out = D
    if argv:
        if len(argv) != 2 or argv[0] != "--out":
            print("usage: posthoc_note1_e186.py [--out <dir>]", file=sys.stderr)
            return 2
        out = argv[1]
    with open(os.path.join(D, "README.md"), encoding="utf-8") as f:
        readme = f.read().splitlines()
    T = load("trains-e186.json")["trains"]
    S = load("scored-e186.json")
    F = load(FORECAST, top=True)
    R = S["rules"]
    lines = ["E186's data README, dated note 1: post hoc figures from this directory's committed files (posthoc_note1_e186.py)",
             "inputs: README.md (as text), trains-e186.json, scored-e186.json, " + FORECAST + " (the candidates' rates)", ""]

    # section 0: the README lines the note cites
    lines.append("## 0. The README lines the note cites (each found by its anchor on its first line; the lines' text is not copied)")
    anchors = []
    for label, a, b, anchor in ANCHORS:
        found = anchor in readme[a - 1] if a - 1 < len(readme) else False
        anchors.append({"label": label, "lines": [a, b], "anchor": anchor, "found_on_first_line": found})
        lines.append(f"lines {a}-{b} ({label}): anchor {anchor!r} {'FOUND' if found else 'NOT FOUND'} on line {a}")
    lines.append(f"README.md: {len(readme)} lines")
    lines.append("")

    # section 1: the measured rates against the candidates'
    lines.append("## 1. Each train's measured rate over the candidates' rate for its type (README lines 96-98; fault 2)")
    cand = F["rates_per_s"]
    lines.append("candidates' rates (forecast-e186.json > rates_per_s): "
                 + ", ".join(f"{k} {cand[k]:.6e}" for k in sorted(cand)) + " TensorFMA ops a second")
    rows = []
    for tid in ORDER:
        t = T[tid]
        typ = t["type"]
        meas = t["rate_per_s"]
        q = meas / cand[typ]
        st = S["trains"][tid]
        used = st.get("rate_used_per_s")
        rows.append({"train": tid, "type": typ, "family": "int8" if typ == "int8" else "float", "rate_measured_per_s": meas,
                     "rate_candidates_per_s": cand[typ], "ratio": q, "scorer_rate_used_per_s": used,
                     "scorer_used_the_measured_rate": used == meas and st.get("rate_measured") is True})
        lines.append(f"{tid:9s} {typ:5s} measured {meas:.6e}, candidates' {cand[typ]:.6e}, ratio {q:.6f}; the scorer used "
                     f"{used:.6e} ({'the measured rate, exactly' if used == meas else 'NOT the measured rate'})")
    fam = {}
    printed = {"float": {"ratio": "1.0016-1.0017", "rates": "1.11896e9-1.11906e9"},
               "int8": {"ratio": "1.0004", "rates": "1.92117e9-1.92125e9"}}
    for fname in ("float", "int8"):
        rr = [r for r in rows if r["family"] == fname]
        lo = min(rr, key=lambda r: r["ratio"])
        hi = max(rr, key=lambda r: r["ratio"])
        rlo = min(r["rate_measured_per_s"] for r in rr)
        rhi = max(r["rate_measured_per_s"] for r in rr)
        a, b = f4(lo["ratio"]), f4(hi["ratio"])
        ratio_words = a if a == b else f"{a}-{b}"
        rates_words = f"{rlo / 1e9:.5f}e9-{rhi / 1e9:.5f}e9"
        fam[fname] = {"trains": len(rr), "ratio_min": lo["ratio"], "ratio_min_train": lo["train"], "ratio_max": hi["ratio"],
                      "ratio_max_train": hi["train"], "ratio_to_4_decimals": ratio_words, "rates_to_5_decimals": rates_words,
                      "readme_prints_ratio": printed[fname]["ratio"], "readme_prints_rates": printed[fname]["rates"],
                      "ratio_reads": "OK" if ratio_words == printed[fname]["ratio"] else "DIFFERS",
                      "rates_read": "OK" if rates_words == printed[fname]["rates"] else "DIFFERS"}
        lines.append(f"{fname}: {len(rr)} trains; ratio {lo['ratio']:.5f} ({lo['train']}) to {hi['ratio']:.5f} ({hi['train']}), to 4 "
                     f"decimals {ratio_words}; the README prints {printed[fname]['ratio']}: {fam[fname]['ratio_reads']}. Rates "
                     f"{rates_words}; the README prints {printed[fname]['rates']}: {fam[fname]['rates_read']}")
    n_used = sum(1 for r in rows if r["scorer_used_the_measured_rate"])
    lines.append(f"the scorer's lines used each train's measured rate, exactly: {n_used} of {len(rows)} trains "
                 "(so no rule reads the README's rounded ratios)")
    lines.append("")

    # section 2: the int8 price per held bit at the two products
    lines.append("## 2. beta_A and beta_B at products 3 and 63 (README lines 74-76; fault 4a)")
    sp = {}
    for side in ("beta_A", "beta_B"):
        b3 = R["E186-SPLIT3"][side]
        b63 = R["E186-SPLIT63"][side]
        overlap = not (b63["lo"] > b3["hi"] or b3["lo"] > b63["hi"])
        diff = b63["mean"] - b3["mean"]
        se = math.sqrt(b3["se"] ** 2 + b63["se"] ** 2)
        sp[side] = {"product_3": {k: b3[k] for k in ("mean", "lo", "hi", "se")},
                    "product_63": {k: b63[k] for k in ("mean", "lo", "hi", "se")},
                    "intervals_overlap": overlap,
                    "posthoc_difference_63_minus_3": diff, "posthoc_difference_se": se, "posthoc_z": diff / se}
        lines.append(f"{side}: product 3 {sgn(b3['mean'])} [{sgn(b3['lo'])}, {sgn(b3['hi'])}], product 63 {sgn(b63['mean'])} "
                     f"[{sgn(b63['lo'])}, {sgn(b63['hi'])}] W a held 1-bit a byte; the 95% intervals "
                     f"{'OVERLAP' if overlap else 'ARE APART'}. Post hoc arithmetic, no rule reads it: 63 less 3 {sgn(diff, 4)} W, "
                     f"se {se:.4f} (the two products' trains are separate blocks), z {diff / se:+.1f}")
    lines.append(f"verdicts as scored: E186-SPLIT3 {R['E186-SPLIT3']['verdict']}, E186-SPLIT63 {R['E186-SPLIT63']['verdict']}")
    lines.append("")

    # section 3: E186-S23R's margin
    lines.append("## 3. E186-S23R: S23 x 23/16 against E182's T5 (README lines 77-78 and 261; fault 4b)")
    r = R["E186-S23R"]
    x, t5 = r["s23_times_23_16"], r["T5"]
    gap = t5["lo"] - x["hi"]
    s23 = R["E186-S23"]["estimate"]
    s3 = {"verdict": r["verdict"], "s23": {k: s23[k] for k in ("mean", "lo", "hi", "hw")},
          "s23_times_23_16": {k: x[k] for k in ("mean", "lo", "hi", "hw")}, "T5": {k: t5[k] for k in ("mean", "lo", "hi")},
          "gap_T5_lo_minus_s23x_hi": gap, "gap_over_s23x_half_width": gap / x["hw"],
          "s23_hi_times_23_16": s23["hi"] * 23 / 16}
    lines.append(f"S23 {sgn(s23['mean'], 4)} [{sgn(s23['lo'], 4)}, {sgn(s23['hi'], 4)}] W; times 23/16 {sgn(x['mean'])} "
                 f"[{sgn(x['lo'])}, {sgn(x['hi'])}] (half-width {x['hw']:.4f}); E182's T5 {sgn(t5['mean'])} [{sgn(t5['lo'])}, "
                 f"{sgn(t5['hi'])}]")
    lines.append(f"the gap, T5's lower end less the scaled upper end: {gap:+.6f} W ({gap / x['hw'] * 100:.2f}% of the scaled "
                 f"half-width); the intervals {'do not overlap' if gap > 0 else 'overlap'}: {r['verdict']} as scored")
    lines.append("")

    doc = {
        "_what": "E186's data README, dated note 1: post hoc figures from this directory's committed files (posthoc_note1_e186.py)",
        "inputs": ["README.md", "trains-e186.json", "scored-e186.json", FORECAST],
        "readme_lines": anchors,
        "rates": {"candidates_per_s": cand, "trains": rows, "families": fam,
                  "scorer_used_measured_rate": f"{n_used} of {len(rows)}"},
        "split": sp,
        "s23r": s3,
    }
    with open(os.path.join(out, "posthoc-note1-e186.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(out, "posthoc-note1-e186.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip("\n") + "\n")
    nf = sum(1 for a in anchors if a["found_on_first_line"])
    print(f"posthoc_note1_e186: anchors {nf} of {len(anchors)} found; rates float {fam['float']['ratio_reads']} "
          f"int8 {fam['int8']['ratio_reads']}; scorer used the measured rate {n_used} of {len(rows)}; "
          f"S23R gap {gap:+.6f} W")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
