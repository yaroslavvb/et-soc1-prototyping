#!/usr/bin/env python3
"""E185's data README, dated note 1, and note M1's dated note 1 (Thu 12 Nov 2026, after the data verifier): the figures the two notes
quote, read again from committed files. Post hoc: it decides nothing, scores nothing and changes no committed file. Standard library
only; it imports no lab module.

It reads this directory's README.md, README.md.dated-note-M1.md and arm-m1-e185.txt (as text: the lines the notes cite), scored-m11.json
and logs/config-session-start.json.time and logs/config-session-end.json.time; and, from the repository, as data or text only: the kit's
tools/claims-v3/e185/arms-e185-e181.json (E181's held-out figures), step 10 v2's script (the rest rule's patterns), E186's launch step
(its session log's path), and the committed session logs of E186 and of E184 arm S (their session-end lines' times, nothing else).

    python3 -B docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3/posthoc_note1_e185.py [--out <dir>]

Section 0 finds each line the notes cite by a short anchor and prints only the anchor and its line. Section 1 gives E181's held-out rms
on both of A1-1's readings against the README's printed figures, and counts A1-1's label. Section 2 gives each rule's D as the scorer
prints it against the subtraction of the printed rms, and the rms of the printed per-hold misses. Section 3 gives each hold's misses
(e = R - P) with what their signs mean. Section 4 gives E185-C's lines as printed and the B line's distance from its MISSES line.
Section 5 gives the card-minutes. Section 6 tests the rest rule's patterns against E186's, E184 arm S's and E185's session-log paths,
and gives the minutes from each earlier session's end to the first try's launch.

It writes posthoc-note1-e185.json and posthoc-note1-e185.txt beside itself (or in --out), with paths relative to this directory or the
repository's top and no run time, so a re-run from the same tree writes them byte for byte. Exit 0 when it ran, 2 on a usage error.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import fnmatch
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
D = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
ARMS_E181 = "tools/claims-v3/e185/arms-e185-e181.json"
STEP10 = "tools/claims-v3/e185/rb/s11_a3_launch_e185_v2.sh"
E186_LAUNCH = "tools/claims-v3/e186/rb/s11_a3_session_e186.sh"
E186_LOG = "docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/logs/session.log"
E184S_LOG = "docs/reports/data/2026-11-08-e184-sensor-validation/raw/aifoundry3/logs/session-S-t1794133299.log"
PROPOSED = "build/e18[0-9]/T[0-9]*/session.log"
A1_LABEL = "chosen by A10 after both readings were seen"
HOLDS = ["H_E", "L1", "L2", "H_E2", "S", "S2"]
# The lines the notes cite: (file, label, first line, last line, an anchor that must occur on the first line). The anchors are short
# and neutral; the lines' own text is never copied into the outputs.
ANCHORS = [
    ("README.md", "two tries: the launch row (the rest gate's reading)", 39, 39, "| launch (step 10, `rb/s11_a3_launch_e185_v2.sh`) |"),
    ("README.md", "two tries: the T0 row", 40, 40, "| T0 (session start) |"),
    ("README.md", "two tries: the session-end row", 44, 44, "| session end |"),
    ("README.md", "the rest gate did not see E186", 56, 60, "- **The rest gate did not see E186.**"),
    ("README.md", "the answer: E185-RF", 78, 78, "| **E185-RF**"),
    ("README.md", "the answer: E185-BF", 79, 79, "| **E185-BF**"),
    ("README.md", "the answer: E185-RB", 80, 80, "| **E185-RB**"),
    ("README.md", "the answer: E185-C on F", 82, 82, "| **E185-C on F**"),
    ("README.md", "the answer: E185-C on B", 83, 83, "| E185-C on B, reported"),
    ("README.md", "each hold: the sign convention", 91, 92, "**Each hold** (A10's reading; e = R"),
    ("README.md", "each hold: the post hoc paragraph", 103, 106, "Each arm's mean miss by kind, reported"),
    ("README.md", "each hold: the frozen chain's sentence, its second line", 106, 106, "runs warm on L1, L2 and S2"),
    ("README.md", "M11's readings: the pooled HM-CAL row", 116, 116, "| **HM-CAL** and **HM-CAL-I8**, pooled"),
    ("README.md", "the readings, labelled: card-minutes", 136, 136, "| card-minutes | **102.6** of the 105 cap"),
    ("README.md", "what it does: E181's held-out ranking", 207, 208, "E181's held-out ranking"),
    ("README.md.dated-note-M1.md", "the title (its clause after the anchor is set aside)", 1, 1, "both versions read alike;"),
    ("README.md.dated-note-M1.md", "the words are the reader's own", 7, 9, "**Reported, never a rule:**"),
    ("README.md.dated-note-M1.md", "the table", 33, 40, "| hold | the model's rise |"),
    ("README.md.dated-note-M1.md", "over the six rises", 42, 43, "- **Over the six rises:**"),
    ("README.md.dated-note-M1.md", "beside it", 44, 46, "- **Beside it, as M1-4 sets them**"),
    ("README.md.dated-note-M1.md", "the post hoc bullet (set aside)", 47, 48, "- *Post hoc, deciding nothing:*"),
    ("arm-m1-e185.txt", "v3's summary line", 19, 19, "v3 over the 6 rises read:"),
    ("arm-m1-e185.txt", "v3's beside line", 20, 20, "beside: E185-BEST's rms"),
    ("arm-m1-e185.txt", "v4's summary line", 34, 34, "v4 over the 6 rises read:"),
    ("arm-m1-e185.txt", "v4's beside line", 35, 35, "beside: E185-BEST's rms"),
    ("arm-m1-e185.txt", "v4 reads as v3", 36, 36, "v4 reads exactly as v3"),
]
MINUS = "\u2212"


def text(rel, top=False):
    with open(os.path.join(TOP if top else D, rel), encoding="utf-8") as f:
        return f.read()


def load(rel, top=False):
    return json.loads(text(rel, top))


def num(s):
    return float(s.replace(MINUS, "-"))


def s4(x):
    return f"{x:+.4f}"


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def glob_match(pattern, path):
    """A shell glob without '**': '*', '?' and '[...]' never cross a '/', so match component by component."""
    p, q = pattern.split("/"), path.split("/")
    return len(p) == len(q) and all(fnmatch.fnmatchcase(b, a) for a, b in zip(p, q))


def stamp(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def main(argv):
    out = D
    if argv:
        if len(argv) != 2 or argv[0] != "--out":
            print("usage: posthoc_note1_e185.py [--out <dir>]", file=sys.stderr)
            return 2
        out = argv[1]
    files = {f: text(f).splitlines() for f in ("README.md", "README.md.dated-note-M1.md", "arm-m1-e185.txt")}
    readme = files["README.md"]
    S = load("scored-m11.json")["E185"]
    R, O = S["rules"], S["one_pass_reported"]["rules"]
    lines = ["E185's data README, dated note 1, and note M1's dated note 1: post hoc figures from committed files (posthoc_note1_e185.py)",
             "inputs: README.md, README.md.dated-note-M1.md and arm-m1-e185.txt (as text), scored-m11.json, logs/config-session-*.json.time, "
             f"{ARMS_E181}, {STEP10} (as text), {E186_LAUNCH} (as text), {E186_LOG} and {E184S_LOG} (their session-end lines)", ""]

    # section 0: the lines the notes cite
    lines.append("## 0. The lines the notes cite (each found by its anchor on its first line; the lines' text is not copied)")
    anchors = []
    for fn, label, a, b, anchor in ANCHORS:
        body = files[fn]
        found = a - 1 < len(body) and anchor in body[a - 1]
        rec = {"file": fn, "label": label, "lines": [a, b], "anchor": anchor, "found_on_first_line": found}
        if fn == "README.md.dated-note-M1.md" and a == 1 and found:
            rec["characters_after_the_anchor_on_line_1"] = len(body[0]) - (body[0].index(anchor) + len(anchor))
        anchors.append(rec)
        extra = (f"; the line runs {rec['characters_after_the_anchor_on_line_1']} more characters after it"
                 if "characters_after_the_anchor_on_line_1" in rec else "")
        lines.append(f"{fn} lines {a}-{b} ({label}): anchor {anchor!r} {'FOUND' if found else 'NOT FOUND'} on line {a}{extra}")
    for fn in files:
        lines.append(f"{fn}: {len(files[fn])} lines")
    lines.append("")

    # section 1: E181's held-out figures and A1-1's label
    lines.append("## 1. E181's held-out rms on both readings (README lines 207-208; the verifier's fault 1)")
    A = load(ARMS_E181, top=True)
    two, one = A["two_pass"]["held_out"]["rms"], A["held_out"]["rms"]
    joined = readme[206] + " " + readme[207]
    m1 = re.search(r"held-out ranking \(Rl ([0-9.]+), B ([0-9.]+), F ([0-9.]+) \u00b0C\)", joined)
    m2 = re.search(r"read E185 better than it read E181 \(([0-9.]+) against\s+([0-9.]+) \u00b0C\)", joined)
    printed = {"Rl": m1.group(1), "B": m1.group(2), "F": m1.group(3)} if m1 else {}
    printed_pair = {"E185_F": m2.group(1), "E181_F": m2.group(2)} if m2 else {}
    sec1 = {"two_pass_A10": {k: two[k] for k in ("F", "B", "Rl", "n")}, "one_pass_stated": {k: one[k] for k in ("F", "B", "Rl", "n")},
            "readme_prints": printed, "readme_prints_pair": printed_pair}
    for name, rr in (("two_pass_A10", two), ("one_pass_stated", one)):
        r3 = {k: f"{rr[k]:.3f}" for k in ("Rl", "B", "F")}
        sec1[name + "_to_3_decimals"] = r3
        sec1[name + "_order"] = " < ".join(sorted(("Rl", "B", "F"), key=lambda k: rr[k]))
        sec1[name + "_matches_readme"] = bool(printed) and all(r3[k] == printed[k] for k in r3)
        sec1[name + "_F_to_2_decimals"] = f"{rr['F']:.2f}"
    sec1["E185_F_rms_A10"] = R["E185-BEST"]["rms_C"]["F"]
    sec1["label_count"] = {fn: sum(1 for ln in files[fn] if A1_LABEL in ln) for fn in ("README.md", "README.md.dated-note-M1.md")}
    lines.append(f"the README prints Rl {printed.get('Rl')}, B {printed.get('B')}, F {printed.get('F')} C, and the frozen chain "
                 f"{printed_pair.get('E185_F')} on E185 against {printed_pair.get('E181_F')} on E181")
    lines.append(f"two-pass, A10's reading (arms-e185-e181.json > two_pass > held_out > rms; A1-1's label 'held out; the reading {A1_LABEL}'): "
                 f"F {two['F']:.4f}, B {two['B']:.4f}, Rl {two['Rl']:.4f} (n {two['n']}); to 3 decimals Rl {sec1['two_pass_A10_to_3_decimals']['Rl']}, "
                 f"B {sec1['two_pass_A10_to_3_decimals']['B']}, F {sec1['two_pass_A10_to_3_decimals']['F']}: "
                 f"{'the README figures' if sec1['two_pass_A10_matches_readme'] else 'NOT the README figures'}; F to 2 decimals "
                 f"{sec1['two_pass_A10_F_to_2_decimals']}; order {sec1['two_pass_A10_order']}")
    lines.append(f"one-pass, the stated reading (> held_out > rms; A1-1's label 'held out; the reading stated at 20:03 PST'): F {one['F']:.4f}, "
                 f"B {one['B']:.4f}, Rl {one['Rl']:.4f} (n {one['n']}); to 3 decimals Rl {sec1['one_pass_stated_to_3_decimals']['Rl']}, "
                 f"B {sec1['one_pass_stated_to_3_decimals']['B']}, F {sec1['one_pass_stated_to_3_decimals']['F']}: "
                 f"{'the README figures' if sec1['one_pass_stated_matches_readme'] else 'not the README figures'}; F to 2 decimals "
                 f"{sec1['one_pass_stated_F_to_2_decimals']}; order {sec1['one_pass_stated_order']}")
    lines.append(f"E185's frozen chain, blind on A10's reading (scored-m11.json > E185 > rules > E185-BEST > rms_C > F): {sec1['E185_F_rms_A10']:.4f}, "
                 f"below E181's F on both readings: {sec1['E185_F_rms_A10'] < min(two['F'], one['F'])}")
    lines.append(f"A1-1's label ('{A1_LABEL}') occurs on {sec1['label_count']['README.md']} README line(s) and "
                 f"{sec1['label_count']['README.md.dated-note-M1.md']} note M1 line(s)")
    lines.append("")

    # section 2: each D as the scorer prints it and as the README subtracts it
    lines.append("## 2. Each D: the scorer's D_C against the subtraction of the printed rms (README lines 78-80; the verifier's nit 4)")
    reg = re.compile(r"= ([0-9.]+) " + MINUS + r" ([0-9.]+) = \*\*([+" + MINUS + r"][0-9.]+) \u00b0C\*\*")
    arm = re.compile(r"D ([+" + MINUS + r"][0-9.]+) \(([0-9.]+) " + MINUS + r" ([0-9.]+)\)")
    sec2 = []
    for i, name in enumerate(("E185-RF", "E185-BF", "E185-RB")):
        ln = readme[77 + i]
        for reading, rules, rx in (("A10's reading (registered)", R, reg), ("the stated reading's arm (reported, A1-1)", O, arm)):
            m = rx.search(ln)
            r = rules[name]
            if rx is reg:
                px, py, pd = (num(m.group(1)), num(m.group(2)), num(m.group(3))) if m else (None, None, None)
            else:
                pd, px, py = (num(m.group(1)), num(m.group(2)), num(m.group(3))) if m else (None, None, None)
            sub = round(px - py, 4) if m else None
            rec = {"rule": name, "reading": reading, "readme_operands": [px, py], "readme_D": pd, "operands_subtracted": sub,
                   "subtraction_reproduces_the_printed_D": m is not None and f"{sub:+.4f}" == f"{pd:+.4f}",
                   "scorer_rms_x_C": r["rms_x_C"], "scorer_rms_y_C": r["rms_y_C"], "scorer_D_C": r["D_C"],
                   "printed_D_is_the_scorer_D_C": m is not None and f"{pd:+.4f}" == f"{r['D_C']:+.4f}", "verdict": r["verdict"]}
            sec2.append(rec)
            lines.append(f"{name}, {reading}: README {px:.4f} - {py:.4f} = {s4(pd)}; the printed operands subtract to {s4(sub)} "
                         f"({'the same' if rec['subtraction_reproduces_the_printed_D'] else 'NOT the printed D'}); the scorer's D_C "
                         f"{s4(r['D_C'])} ({'= the printed D' if rec['printed_D_is_the_scorer_D_C'] else 'differs'}); {r['verdict']}")
    H = S["holds"]
    from_holds = {a: rms([H[h][f"e_{a}_C"] for h in HOLDS]) for a in ("F", "B", "Rl")}
    dh = {"RF": from_holds["Rl"] - from_holds["F"], "BF": from_holds["B"] - from_holds["F"], "RB": from_holds["Rl"] - from_holds["B"]}
    lines.append(f"a desk check, A10's reading: the rms of the six per-hold misses as the score prints them (4 decimals): F {from_holds['F']:.5f}, "
                 f"B {from_holds['B']:.5f}, Rl {from_holds['Rl']:.5f}; D RF {dh['RF']:+.5f}, BF {dh['BF']:+.5f}, RB {dh['RB']:+.5f}; "
                 f"tau {R['tau_C']}")
    lines.append("")

    # section 3: each hold's misses and what their signs mean
    lines.append("## 3. Each hold's misses, e = R - P (README lines 91-106; the verifier's nit 5): e > 0, the die rose more than the arm "
                 "predicted (the arm under-predicts); e < 0, less (the arm over-predicts)")
    sec3 = {}
    for h in HOLDS:
        e = {a: H[h][f"e_{a}_C"] for a in ("F", "B", "Rl")}
        sec3[h] = {"item": H[h]["item"], "R_C": H[h]["R_C"], "e_C": e,
                   "words": {a: ("under-predicts" if e[a] > 0 else "over-predicts" if e[a] < 0 else "exact") for a in e}}
        lines.append(f"{h:4s} {H[h]['item']:13s} R {H[h]['R_C']:.4f}; e_F {s4(e['F'])} (F {sec3[h]['words']['F']}), e_B {s4(e['B'])} "
                     f"(B {sec3[h]['words']['B']}), e_Rl {s4(e['Rl'])} (Rl {sec3[h]['words']['Rl']})")
    checks3 = {
        "F under-predicts L1, L2 and S2": all(H[h]["e_F_C"] > 0 for h in ("L1", "L2", "S2")),
        "F within 0.07 C on H_E and S": all(abs(H[h]["e_F_C"]) < 0.07 for h in ("H_E", "S")),
        "B over-predicts H_E and H_E2": all(H[h]["e_B_C"] < 0 for h in ("H_E", "H_E2")),
        "Rl over-predicts L1, L2 and S": all(H[h]["e_Rl_C"] < 0 for h in ("L1", "L2", "S")),
        "Rl within 0.19 C on H_E and H_E2": all(abs(H[h]["e_Rl_C"]) < 0.19 for h in ("H_E", "H_E2")),
    }
    for k, v in checks3.items():
        lines.append(f"{k}: {v}")
    lines.append("")

    # section 4: E185-C as printed
    lines.append("## 4. E185-C as the scorer printed it (README lines 82-83; the verifier's nit 6). Its rule (E185.md section 6): THE SHAPE "
                 "MISSES if the 95% interval excludes 0 and |mean| >= 0.05 C; THE SHAPE HOLDS if it lies inside +-0.10 C; else NOT RESOLVED. "
                 "The F line governs (A1-2); B and Rl are reported")
    sec4 = {}
    for reading, rules in (("A10", R), ("stated", O)):
        for a in ("F", "B", "Rl"):
            c = rules["E185-C"][a]
            lo, hi = c["ci95_C"]
            sec4[f"{reading}_{a}"] = {"mean_d_C": c["mean_d_C"], "ci95_C": [lo, hi], "n": c["n"], "verdict": c["verdict"],
                                     "interval_excludes_0": lo > 0 or hi < 0, "distance_of_nearer_end_from_0_C": round(min(abs(lo), abs(hi)), 4)}
            lines.append(f"{reading} {a:2s}: mean {s4(c['mean_d_C'])} C, 95% [{s4(lo)}, {s4(hi)}], n {c['n']}: {c['verdict']}; nearer end "
                         f"{sec4[f'{reading}_{a}']['distance_of_nearer_end_from_0_C']:.4f} C from 0")
    b = sec4["A10_B"]
    lines.append(f"A10's B line: |mean| {abs(b['mean_d_C']):.4f} >= 0.05, and its lower end lies {b['distance_of_nearer_end_from_0_C']:.4f} C "
                 "below 0, so it reads NOT RESOLVED by that margin")
    lines.append("")

    # section 5: the card-minutes
    lines.append("## 5. The card-minutes (README lines 40, 44 and 136; the verifier's nit 7)")
    t_start = datetime.datetime.fromisoformat(text("logs/config-session-start.json.time").strip())
    t_end = datetime.datetime.fromisoformat(text("logs/config-session-end.json.time").strip())
    m40 = re.search(r"\| T0 \(session start\) \| ([0-9:]+) PST \(`T([0-9]+)`\)", readme[39])
    m44 = re.search(r"\| session end \| ([0-9:]+) PST \(([0-9.]+) card-minutes", readme[43])
    day = "2026-11-12"
    try1_t0 = stamp(f"{day} {m40.group(1)}")
    try1_end = stamp(f"{day} {m44.group(1)}")
    later = (t_end - t_start).total_seconds() / 60
    first = (try1_end - try1_t0).total_seconds() / 60
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=int(m40.group(2)))
    sec5 = {"later_try": {"config_read_start": t_start.isoformat(), "config_read_end": t_end.isoformat(), "card_minutes": round(later, 1)},
            "first_try": {"T0": f"{day} {m40.group(1)} PST", "T0_epoch": int(m40.group(2)),
                          "T0_epoch_in_PST": (epoch - datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                          "session_end": f"{day} {m44.group(1)} PST", "card_minutes": round(first, 1),
                          "readme_prints": float(m44.group(2))},
            "cap_per_session_from_T0": 105, "all_on_card_0": round(later + first, 1),
            "readme_line_136_prints_102_6_and_109_2": "**102.6** of the 105 cap" in readme[135] and "109.2 minutes" in readme[135]}
    lines.append(f"the session collected: config reads {t_start.isoformat()} to {t_end.isoformat()}: {later:.1f} card-minutes, against the cap "
                 "of 105 per session from T0 (E185.md section 8)")
    lines.append(f"the first try (README lines 40 and 44): T0 {m40.group(1)} PST (T{m40.group(2)} = {sec5['first_try']['T0_epoch_in_PST']} PST) "
                 f"to its session end {m44.group(1)} PST: {first:.1f} card-minutes, no hold (the README prints {m44.group(2)})")
    lines.append(f"card 0 carried E185 for {later + first:.1f} minutes in all; README line 136 prints both figures: "
                 f"{sec5['readme_line_136_prints_102_6_and_109_2']}")
    lines.append("")

    # section 6: the rest rule
    lines.append("## 6. Step 10 v2's rest rule against the session logs on the box (README lines 39 and 56-60; the verifier's fault 3)")
    st = text(STEP10, top=True).splitlines()
    li = next(i for i, ln in enumerate(st) if ln.lstrip().startswith("for L in "))
    pats = re.match(r"\s*for L in (.*?); do", st[li]).group(1).split()
    el = text(E186_LAUNCH, top=True).splitlines()
    e186_form_line = next(i for i, ln in enumerate(el) if "build/e186/T$T0/session.log" in ln) + 1
    e186 = text(E186_LOG, top=True).splitlines()
    t0_186 = re.search(r"its files in build/e186/T([0-9]+)", e186[0]).group(1)
    end_rx = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) PST session end( \(T0 \d+\))?$")
    e186_end = [end_rx.match(ln).group(1) for ln in e186 if end_rx.match(ln)]
    e184s_end = [end_rx.match(ln).group(1) for ln in text(E184S_LOG, top=True).splitlines() if end_rx.match(ln)]
    paths = {"E186's session log": f"build/e186/T{t0_186}/session.log",
             "E184 arm S's session log": "build/e184/session-S-t1794133299.log",
             "E185's first try's session log": f"build/e185/T{m40.group(2)}/session.log"}
    sec6 = {"step10_line": li + 1, "patterns": pats, "proposed_for_a_later_kit": PROPOSED,
            "e186_log_form_line_in_launch_step": e186_form_line, "paths": {}}
    lines.append(f"{STEP10} line {li + 1}: {len(pats)} patterns: {' '.join(pats)}")
    lines.append(f"{E186_LAUNCH} line {e186_form_line} names E186's log as build/e186/T$T0/session.log; E186's T0 {t0_186} (its log's first line)")
    for what, p in paths.items():
        hits = [q for q in pats if glob_match(q, p)]
        sec6["paths"][what] = {"path": p, "matched_by_v2": hits, "matched_by_the_proposed_pattern": glob_match(PROPOSED, p)}
        lines.append(f"{what} {p}: v2's patterns matching it: {', '.join(hits) if hits else 'NONE'}; the proposed {PROPOSED}: "
                     f"{'matches' if glob_match(PROPOSED, p) else 'no match'}")
    m39 = re.search(r"\| ([0-9:]+)-[0-9:]+ PST, no flag\. The rest gate read ([0-9,]+) minutes since E184 arm S", readme[38])
    launch = stamp(f"{day} {m39.group(1)}")
    for what, ends in (("E184 arm S", e184s_end), ("E186", e186_end)):
        end = stamp(ends[-1])
        mins = (launch - end).total_seconds() / 60
        sec6[f"minutes_from_{what.replace(' ', '_')}_end"] = {"session_end_PST": ends[-1], "first_try_launch_PST": f"{day} {m39.group(1)}",
                                                             "minutes": round(mins, 2), "whole_minutes_as_the_rule_counts": int(mins // 1)}
        lines.append(f"{what}'s session end {ends[-1]} PST (its committed log's last 'session end' line) to the first try's launch "
                     f"{day} {m39.group(1)} PST: {mins:.2f} minutes ({int(mins // 1)} whole)")
    sec6["readme_line_39_prints"] = m39.group(2)
    sec6["readme_line_59_prints"] = re.search(r"about ([0-9,]+) minutes", readme[58]).group(1)
    lines.append(f"README line 39 prints {m39.group(2)} minutes (E184 arm S); line 59 prints about {sec6['readme_line_59_prints']} (E186); "
                 "both over the rule's 40 minutes and A7-4's hour")
    lines.append("")

    doc = {
        "_what": "E185's data README, dated note 1, and note M1's dated note 1: post hoc figures from committed files (posthoc_note1_e185.py)",
        "inputs": ["README.md", "README.md.dated-note-M1.md", "arm-m1-e185.txt", "scored-m11.json", "logs/config-session-start.json.time",
                   "logs/config-session-end.json.time", ARMS_E181, STEP10, E186_LAUNCH, E186_LOG, E184S_LOG],
        "cited_lines": anchors,
        "e181_held_out": sec1,
        "d": {"rules": sec2, "desk_rms_from_printed_holds": {k: round(v, 5) for k, v in from_holds.items()},
              "desk_D_from_printed_holds": {k: round(v, 5) for k, v in dh.items()}},
        "holds": sec3,
        "holds_checks": checks3,
        "e185_c": sec4,
        "card_minutes": sec5,
        "rest_rule": sec6,
    }
    with open(os.path.join(out, "posthoc-note1-e185.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(out, "posthoc-note1-e185.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip("\n") + "\n")
    nf = sum(1 for a in anchors if a["found_on_first_line"])
    e186_seen = bool(sec6["paths"]["E186's session log"]["matched_by_v2"])
    n_rep = sum(1 for r in sec2 if r["subtraction_reproduces_the_printed_D"])
    print(f"posthoc_note1_e185: anchors {nf} of {len(anchors)} found; E181's printed figures are the two-pass ones: "
          f"{sec1['two_pass_A10_matches_readme']}; label lines {sec1['label_count']['README.md']}; D subtractions reproducing "
          f"{n_rep} of {len(sec2)}; card-minutes {sec5['later_try']['card_minutes']} + {sec5['first_try']['card_minutes']} = "
          f"{sec5['all_on_card_0']}; E186's log matched by v2: {e186_seen}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
