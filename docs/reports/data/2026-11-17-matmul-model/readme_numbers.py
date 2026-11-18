#!/usr/bin/env python3
"""The matmul model report's check list: every number of README.md found in its committed file. Desk.

    /usr/bin/python3 -I -B readme_numbers.py --repo <the lab's top> --numbers <numbers.json from make_figures.py> \
        [--readme README.md] [--out readme-numbers.txt]

Each check names a phrase of README.md (it must be there, whitespace aside), the tokens it prints, and where they come from:
  N    numbers.json (make_figures.py's output, itself computed from pinned committed files), formatted as printed;
  T    a committed text file that must hold the committed literal(s); each token, commas aside, must be in a literal;
  R    a committed literal holding a number that, rounded as printed, is the token;
  J    a committed JSON value, formatted as printed;
  CSV  a committed CSV cell, scaled and formatted as printed;
  GT   a commit's own time (git log), as printed;
  ROW  a row of the README's big table, rebuilt cell by cell from numbers.json, and read from a committed table where one exists;
  F    a named function over committed files or numbers.json.
Every check prints one line: PASS or FAIL, the phrase, the value found, the file and the commit that last touched it. Then every number of
README.md that no check covers is listed (dates, times, commit ids, section numbers, identifiers), for a reader to judge. Exit 1 on any FAIL.
Reads only; standard library only; git is called read-only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys

V0 = "tools/matmul/mm1/v0/README.md"
V1 = "tools/matmul/mm1/v1/README.md"
V2 = "tools/matmul/mm1/v2/README.md"
V2S = "tools/matmul/mm1/v2/score-e207.md"
V2F = "tools/matmul/mm1/v2/forecasts-e207.csv"
V2S11 = "tools/matmul/mm1/v2/score-e211.md"
V2J11 = "tools/matmul/mm1/v2/score-e211.json"
CMP = "tools/matmul/mm1/v1/out/compare_e206.md"
NB = "docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md"
E206 = "tools/claims-v3/e206/E206.md"
E207 = "tools/claims-v3/e207/E207.md"
E208 = "tools/claims-v3/e208/E208.md"
E209 = "tools/claims-v3/e209/E209.md"
E210 = "tools/claims-v3/e210/E210.md"
E211 = "tools/claims-v3/e211/E211.md"
K211 = "tools/claims-v3/e211/KIT.md"
E212 = "tools/claims-v3/e212/E212.md"
D207 = "docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md"
D207N1 = "docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md.dated-note-1.md"
S207 = "docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt"
D209 = "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md"
N15 = "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md"
N15J = "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/posthoc-note15-e209.json"
D210 = "docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md"
N210 = "docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md"
D211 = "docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/README.md"
S211 = "docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.txt"
S211J = "docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.json"
S207J = "docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.json"
DA = "docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/README.md"
DB = "docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md"
SA = "docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/scores-e206-A.json"
REP = "docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/repeat-e208-a2c0-S1r.md"
REPR = "docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/README.md"
R129 = "docs/reports/data/2026-11-02-e129-int8-noissue/results.md"
R148 = "docs/reports/data/2026-11-02-e148-int8-excess/readme-numbers.txt"
R155 = "docs/reports/data/2026-11-03-e155-int8-floor-rows/readme-numbers.txt"
C155 = "docs/reports/data/2026-11-03-e155-int8-floor-rows/corrections-numbers.txt"
E129M = "tools/claims-v3/e129/E129.md"
PTS = "tools/claims-v3/e206/points-e206.json"
NOTES = "docs/et-soc1-notes.md"
CLAIMS = "docs/findings/05-claims.md"

QUOTE = ("I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor "
         "switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well "
         "the timing simulation for the matte mold matches reality and the energy.")
BL = "blind"
SEALS = [("bc750c73", "tools/claims-v3/sealed-e206/e206-freeze-lines.md"), ("9db8898a", "tools/claims-v3/sealed-e206/e206-freeze-lines-2.md"),
         ("26a17d64", "tools/claims-v3/sealed-e207/e207-freeze-lines.md"), ("087fa8fd", E208),
         ("2adc7fd3", "tools/claims-v3/sealed-e209/e209-freeze-lines.md"), ("81a84eb6", "tools/claims-v3/sealed-e210/e210-freeze-lines.md"),
         ("7e5a361e", "tools/claims-v3/sealed-e211/e211-freeze-lines.md"), ("4d77f137", E212),
         ("8f2df483", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S2/README.md")]


def checks(cfg):
    C = []

    def add(printed, src, note=""):
        C.append({"printed": printed, "src": src, "note": note})

    b = BL
    # ---------------------------------------------------------------- the words and the summary
    add("A *shire* is a group of 32 minions", ("T", NOTES, "32 minions / 64 harts", ["32"]))
    add("it runs two *harts*", ("T", NOTES, "32 minions / 64 harts", []), "two harts a minion: 64 harts / 32 minions")
    add("the band of footprints just past the 32 MB L3 (33-70 MB)", ("T", NB, "the knee (33-70 MB)", ["33", "70"]))
    add("192 cache lines", ("T", V1, "requests 192 lines", ["192"]))
    add("on 265 blind GEMM points", ("N", "timing.sim_ratio.all.n", "{:d}", ["265"]))
    add("the card took 8 to 34 times the simulator's step count (median 24;", ("N", ["timing.sim_ratio.all.min", "timing.sim_ratio.all.max",
                                                                                 "timing.sim_ratio.all.median"], "{:.0f}", ["8", "34", "24"]))
    add("the counts come from a law fitted to 11 simulator runs", ("T", E206, "a post hoc desk fit on 11 sys_emu runs of rgm136", ["11"]))
    add("(12 micro-loop configurations, 18 registered readings within 2 cycles, one card)", ("F", "r6_summary", ["12", "18"]))
    add("filled 17 to 99% of each op (median 39%)", ("N", ["timing.tensor_share.all.min", "timing.tensor_share.all.max", "timing.tensor_share.all.median"],
                                                     "pct0", ["17", "99", "39"]))
    add("**4.7 to 9.5%** rms in cycles", ("N", ["blind_summary.mm1_cyc_min", "blind_summary.mm1_cyc_max"], "{:.1f}", ["4.7", "9.5"]))
    add("**3.2 to 11.9%** in joules over idle", ("N", ["blind_summary.mm1_jo3_min", "blind_summary.mm1_jo3_max"], "{:.1f}", ["3.2", "11.9"]))
    add("against **17.1 to 23.0%**", ("N", ["blind_summary.F1_cyc_min", "blind_summary.F1_cyc_max"], "{:.1f}", ["17.1", "23.0"]))
    add("**18.4 to 31.0%** for F1", ("N", ["blind_summary.F1_jo3_min", "blind_summary.F1_jo3_max"], "{:.1f}", ["18.4", "31.0"]))
    add("**52.7 to 82.0%** for F2", ("N", ["blind_summary.F2_jo3_min", "blind_summary.F2_jo3_max"], "{:.1f}", ["52.7", "82.0"]))
    add("MM1's cycles error rose from 3-4% on the old kernel to 8-9% on the variant", ("F", "e211_span", ["3-4", "8-9"]))
    # report-fix (Q215): the summary's new or reworded numbers
    add("E211's controls show the compiled code alone moves the cycles by 3-6%", ("F", "e211_controls_span", ["3-6"]))
    add("the registered comparison was UNDECIDED (5 cases)", ("T", N210, ["**UNDECIDED** (4 to 0, 1 tie)", "R2 forecasts 5 test cases"], ["5"]))
    add("for E207's four such points and passed, -6.0% to +7.1%", ("F", "e207_b49_b52_span", ["-6.0", "+7.1"]))
    add("MM1-v2 prices no energy for a tile kind without a resident price on that card", ("T", V2S, "Its energy is NOT FORECAST at b49-b52 (the blind4 and blind3 kinds)", []))
    add("*Unread*: scored on data that existed before the forecast but that the model never read", ("T", V2, "*Unread*: scored on data that existed but that the model never read", []),
        "the lab's own definition (MM1-v2's README)")
    add("The low end in cycles, 4.7%, is arm B", ("N", f"{b}.E206B.models.v1.cyc_mean.rms_pct", "{:.1f}", ["4.7"]))
    add("MM1-v2 read 5.0% and MM1-v1 5.9%", ("N", [f"{b}.E207.models.v2.cyc_mean.rms_pct", f"{b}.E207.models.v1.cyc_mean.rms_pct"], "{:.1f}", ["5.0", "5.9"]))
    add("to **1.9%** of the data-dependent power", ("N", "switch.routes.R1.rms_over_D_pct", "{:.1f}", ["1.9"]))
    add("against 16 to 47% for the bit-flip prices and 20% for the nearest measured kind",
        ("N", ["switch.routes.R3L.rms_over_D_pct", "switch.routes.R3.rms_over_D_pct", "switch.routes.R4.rms_over_D_pct"], "{:.0f}", ["16", "47", "20"]))
    add("to about **0.4%** in cycles", ("N", "repeat.E208.cyc_op_mean.rms_pct", "{:.1f}", ["0.4"]))
    add("**1.2%** in joules over idle", ("N", "repeat.E208.J_op.rms_pct", "{:.1f}", ["1.2"]))
    # ---------------------------------------------------------------- 1
    add("at or before 09:48:24 PST", ("T", V0, "at or before 09:48:24 PST", []))
    add(QUOTE.split(" so I")[0], ("T", V0, QUOTE, []), "the quote, whole, as committed")
    # ---------------------------------------------------------------- 2
    add("The ET-SoC-1 has 1,088 minions in 34 shires (32 compute shires, a master and a spare)",
        ("T", NOTES, "34 minion shires (32 compute + master + spare) = 1088 minions", ["1,088", "34", "32"]))
    add("the lab's kernels use 1,024 of them, in 32 shires of 32", ("T", CLAIMS, "1,024 (32 shires × 32) of 1,088 on the chip", ["1,024", "32"]))
    add("the chip shares a 32 MB L3", ("T", NOTES, "1 MB per shire, 32 MB shared", ["32"]))
    add("run at a fixed 600 MHz (aifoundry3 card 0", ("T", DA, "aifoundry3 card 0 at 600 MHz as found", ["600"]))
    add("aifoundry1 card 1 in the tests below", ("T", DB, "aifoundry1 card 1 at 600 MHz", []))
    add("about 800 MHz in E208's GEMMs", ("T", V2, "card 0 ran at 800 MHz", ["800"]))
    add("M = 1,024·MB, N = 512·NB, K = 512·KB·w (w = 1, 2, 4 for fp32, fp16, int8)",
        ("T", V0, "M = 1,024·MB, N = 512·NB, K = 512·KB·w, with w = 1 / 2 / 4", ["1,024", "512"]))
    add("each minion does 64·MB·NB·KB", ("T", V0, "Each minion does 64·MB·NB·KB ops a GEMM", ["64"]))
    add("4,096 multiply-adds in fp32, 8,192 in fp16 and 16,384 in int8", ("F", "macs_per_op", ["4,096", "8,192", "16,384"]))
    add("asks for 192 cache lines, 64 of A and 128 of B", ("T", V1, "an op of a shire requests 192 lines: A 64 (4 tiles x 16 lines) and B 128",
                                                          ["192", "64", "128"]))
    add("x50 = 39.7 MB and s = 4.53 MB", ("T", V2, "x50 39.7 MB, s 4.53 MB", ["39.7", "4.53"]))
    add("527.48 cycles + 0.0176 µs in fp32 and fp16, and 283.03 cycles + 0.0146 µs in int8",
        ("T", V0, ["fp32 and fp16: 527.48/f + 0.0176 µs", "int8: 283.03/f + 0.0146 µs"], ["527.48", "0.0176", "283.03", "0.0146"]))
    add("529 and 270 cycles", ("T", V0, "floor: 529 / 270 cycles", ["529", "270"]))
    add("scale with (V / 0.517 V)²", ("T", V2, "(V / 0.517 V)^2", ["0.517"]))
    add("58.9, 245.1 and 794.7 pJ", ("T", V2, "b2/d2 58.9/501.2, b3/d3 245.1/1,150.2, bF/dF 794.7/1,298.6 pJ a line a shire-op", ["58.9", "245.1", "794.7"]))
    add("501.2, 1,150.2 and 1,298.6 pJ", ("T", V2, "b2/d2 58.9/501.2, b3/d3 245.1/1,150.2, bF/dF 794.7/1,298.6 pJ a line a shire-op",
                                          ["501.2", "1,150.2", "1,298.6"]))
    add('"one transistor gate, one fin, charged or discharged by a net transition"',
        ("T", V0, "One transistor switch is one transistor gate, one fin, charged or discharged by a net transition", []))
    add("6,144 × 3,072 × 3,072, fp32, random data, all 32 shires", ("T", D207, "| b25 | past | 1 | 6144 x 3072 x 3072 | fp32 | random | 32 (`0xffffffff`) |",
                                                                   ["6,144", "3,072", "32"]))
    add("| 0 / 115.98 / 76.02 |", ("CSV", V2F, "b25", ["lines_L2", "lines_L3", "lines_F"], 1.0, ["{:.0f}", "{:.2f}", "{:.2f}"], ["0", "115.98", "76.02"]))
    add("| 1,173.8 |", ("CSV", V2F, "b25", ["cycles_per_op_mean"], 1.0, ["{:,.1f}"], ["1,173.8"]))
    add("| 1,161.2 |", ("T", D207, "| 2 | 1161.2 | 16,054,045 | 26.78 / 26.77 |", ["1,161.2"]))
    add("| 27.34 |", ("CSV", V2F, "b25", ["seconds_per_gemm"], 1000.0, ["{:.2f}"], ["27.34"]))
    add("26.78 / 26.77 (two runs)", ("T", D207, "26.78 / 26.77", ["26.78", "26.77"]))
    add("| 528.7 |", ("CSV", V2F, "b25", ["J_over_idle_per_gemm"], 1000.0, ["{:.1f}"], ["528.7"]))
    add("519.8 (mean of 529.8 and 509.8)", ("T", D207, "529.8 / 509.8 (519.8)", ["519.8", "529.8", "509.8"]))
    add("counted 4.1 to 6.2 × 10^15", ("CSV", V2F, "b25", ["switches_counted_lo", "switches_counted_hi"], 1e-15, ["{:.1f}", "{:.1f}"], ["4.1", "6.2"]))
    add("estimated 3.4 / 8.5 / 14.9 × 10^15", ("CSV", V2F, "b25", ["switches_estimated_lo", "switches_estimated_central", "switches_estimated_hi"], 1e-15,
                                               ["{:.1f}", "{:.1f}", "{:.1f}"], ["3.4", "8.5", "14.9"]))
    add("own two runs (529.8 against 509.8)", ("T", D207, "529.8 / 509.8 (519.8)", ["529.8", "509.8"]))
    add("fitted on 769 GEMM time points", ("T", V0, "fitted on 769 GEMM points", ["769"]))
    add("682 energy points", ("T", V0, "least squares on 682 GEMM points", ["682"]))
    add("from 11 earlier experiments", ("T", V0, "11 earlier experiments", ["11"]))
    add("(888 time and 791 energy points)", ("T", V1, ["888 time points", "791 energy points"], ["888", "791"]))
    add("(1,072 time and 964 energy points)", ("T", V2, ["1,072 time points", "964 energy points"], ["1,072", "964"]))
    add("cycles 4.70% for MM1-v1 against 5.91% for MM1-v0's form refitted", ("T", V1, "cycles LOEO **4.70%** for v1 against **5.91%** for v0's form",
                                                                           ["4.70", "5.91"]))
    add("5.41% for MM1-v2 against 5.70% for MM1-v1's form refitted", ("T", V2, "cycles LOEO **5.41%** v2 against **5.70%** for v1's form", ["5.41", "5.70"]))
    add("(769, 888 and 1,072 points)", ("T", V2, "| LOEO all (1,072) | **5.41** (-0.1) | **5.70** (-0.2) |", ["1,072"]), "769 and 888 by the checks above")
    add("so MM1-v0's 5.54%", ("T", V0, "**5.54% rms**", ["5.54"]))
    # ---------------------------------------------------------------- 3
    add('"a post hoc desk fit on 11 sys_emu runs of rgm136 ... the simulator has no timing, its steps are instructions"',
        ("T", E206, ["a post hoc desk fit on 11 sys_emu runs of rgm136", "the simulator has no timing, its steps are instructions"], ["11"]))
    add("46.625 steps an op + 24.25 a C-tile row", ("T", E206, "46.625 an op + 24.25 a C-tile row", ["46.625", "24.25"]))
    add("with + 92 a launch in MM1's column", ("T", V1, "46.625 an op + 24.25 a\nC-tile row + 92 a launch", ["92"]))
    add("about 5 steps for each stack load", ("T", K211, "about 5 steps for each stack load", ["5"]))
    add("rgm136's loop runs 36 instructions an op and 47.742 steps", ("T", K211, ["36 instructions an op in rgm136's gemmL", "| 47.742 (gemmL, mn) |"],
                                                                     ["36", "47.742"]))
    add("**265 points** of E206's two arms and E207", ("N", "timing.sim_ratio.all.n", "{:d}", ["265"]))
    add("(161 distinct configurations", ("N", "timing.sim_ratio.distinct_configurations", "{:d}", ["161"]))
    add("**8.2 to 33.9 times**", ("N", ["timing.sim_ratio.all.min", "timing.sim_ratio.all.max"], "{:.1f}", ["8.2", "33.9"]))
    add("**median 24.0**", ("N", "timing.sim_ratio.all.median", "{:.1f}", ["24.0"]))
    add("(quartiles 19.4 and 29.4", ("N", ["timing.sim_ratio.all.q1", "timing.sim_ratio.all.q3"], "{:.1f}", ["19.4", "29.4"]))
    add("all 32 shires took 537.98 cycles an op in fp32 and 388.02 in int8", ("F", "l1x1x1_cycles", ["537.98", "388.02"]))
    add("rgm211's compiled loop takes 32.762 steps an op against rgm136's 47.742 (31 instructions against 36)",
        ("T", K211, ["| 32.762 (gemmLn, nm) |", "| 47.742 (gemmL, mn) |", "**31 in rgm211's\ngemmLn**", "36 instructions an op in rgm136's gemmL"],
         ["32.762", "47.742", "31", "36"]))
    add("where only the compiled code differs, ran 3-6% fast", ("F", "e211_controls_span", ["3-6"]))
    add("plus one constant of 7.75 cycles set on the card in E109", ("T", C155, "54.25 + 7.75 = 62 (measured 62.0)", ["7.75"]))
    add("**18 of 18 registered readings within 2 cycles**", ("F", "r6_count", ["18", "18"]))
    add("all with zeros data on aifoundry1 card 1", ("T", E129M, "(Q136, aifoundry1 card 1)", ["1"]))
    add("12 micro-loop configurations, all with zeros data", ("F", "r6_configs", ["12"]))
    add("within 2 cycles", ("T", E129M, "≤ 2.0", ["2"]))
    add("544.0 forecast against 544.001 measured in fp32", ("T", R129, "| R6 m0.fp32.zeros | PASS (measured 544.001, predicted 544.0) |", ["544.0", "544.001"]))
    add("318.0 against 318.001 in int8", ("T", R129, "| R6 m0.int8.zeros | PASS (measured 318.001, predicted 318.0) |", ["318.0", "318.001"]))
    add("62.0 against 62.0 for an op with one row of A", ("T", R129, "| R6 m0r1.fp32.zeros | PASS (measured 62.0, predicted 62.0) |", ["62.0"]))
    add("527.48 cycles + 0.0176 µs is 538 cycles in fp32 at 600 MHz", ("N", "timing.floor_at_600_fp32_e119", "{:.0f}", ["538"]))
    add("the card measured 537.98 at `gemmL1x1x1`", ("F", "l1x1x1_cycles_fp32", ["537.98"]))
    add("**546** (E101's resident loop, the RTL bench's reach, which E206 registered as its floor) and 544",
        ("T", E206, "resident floor (546 cycles an op in fp32 and fp16, 318 in int8: E101's resident loop on aifoundry3", ["546"]))
    add("and 544 (the bench's m0 loop)", ("T", R129, "| R6 m0.fp32.zeros | PASS (measured 544.001, predicted 544.0) |", ["544"]))
    add("**538** (E119's law with B streamed, at 600 MHz)", ("N", "timing.floor_at_600_fp32_e119", "{:.0f}", ["538"]))
    add("and **529**, the floor MM1 never goes under", ("T", V0, "floor: 529 / 270 cycles", ["529"]))
    add("In int8 the same roles are taken by 318, 292 and 270", ("F", "int8_roles", ["318", "292", "270"]))
    add("filled **17 to 99%** of each op on the card", ("N", ["timing.tensor_share.all.min", "timing.tensor_share.all.max"], "pct0", ["17", "99"]))
    add("**median 39%**, over **285 blind points**", ("N", ["timing.tensor_share.all.median", "timing.tensor_share.all.n"], "mixed_pct0_int", ["39", "285"]))
    add("(546 or 318 cycles, the scorers' registered readings) it filled 21 to 101%, median 40%, over 265 points; 12 of them",
        ("F", "registered_share", ["546", "318", "21", "101", "40", "265", "12"]))
    add("Over the floor with B through the tile buffer (529 or 270 cycles)", ("T", V0, "floor: 529 / 270 cycles", ["529", "270"]))
    add("Near 99% sit the ops whose tiles stay in the L2", ("N", "timing.tensor_share.all.max", "pct0", ["99"]))
    add('"gives instructions and bytes, never the level that served a line"', ("T", V0, "gives instructions and bytes, never the level that served a line", []))
    add("read joules over idle **18.4 to 31.0%** rms", ("N", ["blind_summary.F1_jo3_min", "blind_summary.F1_jo3_max"], "{:.1f}", ["18.4", "31.0"]))
    add("Its miss is a scale, not a shape: about a quarter low in every family on E207",
        ("T", V2S, "F1 is low on J over idle in every family by about a quarter (bias -24.4% given the seconds; -21% to -29% by family): a scale, not a shape", []))
    add("which lost to MM1-v1's full-chip lines on every fold", ("T", V1, "it lost every time", []))
    add("read **52.7 to 82.0%** rms", ("N", ["blind_summary.F2_jo3_min", "blind_summary.F2_jo3_max"], "{:.1f}", ["52.7", "82.0"]))
    add('"+94% to +160% at the long-K points ... against -19% to -42% at one K block"',
        ("T", V2S, ["+94% to +160% at the long-K points", "against -19% to -42% at one K block"], ["94", "160", "19", "42"]))
    add("its byte convention, which counts every shire's request", ("T", V2S, "Its byte convention counts every shire's request", []))
    add("the same models read 6.5 to 10.1% (F1) and 16.4 to 18.3% (F2)", ("F", "rest_span", ["6.5", "10.1", "16.4", "18.3"]))
    # ---------------------------------------------------------------- 4: the first table
    add("| 119 (108 never on this card, 95 never on any) |", ("T", E206, "**95 of the 119 points never ran on any card** (91 as a shape in any data kind); **108 never ran on aifoundry3",
                                                            ["119", "108", "95"]))
    add("| 113 (85 never on this card) |", ("T", NB, ["| never run on card 1 before arm B | 10.0 / 4.7 / 18.5 (85) |", "| seconds a GEMM |"], ["85"]))
    add("| 113 (85", ("T", E206, "(110 of\narm B's 113)", ["113"]))
    add("| 53, 47 distinct cases (all never run on any card at both freezes) |", ("T", V1, "53 points on aifoundry3 card 0, every one never run anywhere (47 distinct",
                                                                                  ["53", "47"]))
    add("| 45, 41 time cases (all never on this card) |", ("T", E209, ["tested on 45 points of the lab's GEMM (rgm136) that never ran on this card",
                                                                        "over the 41 time cases"], ["45", "41"]))
    add("| 26 (rgm211's 12 never run on any card) |", ("T", V2S11, ["Every one of the 26 points and 12 shape pairs is read",
                                                                     "rgm211's 12 points (the kernel no card had run)"], ["26", "12"]))
    for c_, t_ in (("2d1413f5", "13:35:10"), ("eb2f7ac2", "16:01:50"), ("e35a06cb", "20:13:57"), ("d3f031d1", "21:18:46"), ("25d2e74e", "21:14:55"),
                   ("4e518735", "02:06:29"), ("3ca4b717", "01:44:45"), ("1393a649", "07:59:17"), ("89aa0c94", "08:12:53")):
        pre = {"2d1413f5": "Mon ", "eb2f7ac2": "Mon ", "e35a06cb": "Mon ", "25d2e74e": "Mon ", "4e518735": "Tue ", "3ca4b717": "Tue ", "1393a649": "Tue ",
               "89aa0c94": "Tue "}.get(c_, "")
        add(f"`{c_}` ({pre}{t_})", ("GT", c_, t_))
    add("| Mon 16 Nov 16:53:08 |", ("T", DA, "step 7's config read at 16:53:08, reported apart", []))
    add("| Tue 17 Nov 00:13:12 |", ("T", DB, "Step 7's config read at 00:13:12 is reported apart from the session's card time", []))
    add("| Tue 17 Nov 07:06:30 |", ("T", D207, "step 7's config read at 07:06:30, reported apart", []))
    add("| Tue 17 Nov 10:30:44 |", ("T", D209, "the day's first card command, stamped 10:30:44 PST", []))
    add("| Tue 17 Nov 13:21:20 |", ("T", V2S11, "| **E211's first card command** (step 7's config read, read only) | **13:21:20** |", []))
    # ---------------------------------------------------------------- 4: the big table, every cell
    for t_, mods in (("E206A", ("v0", "F1", "F2")), ("E206B", ("v0", "v1", "F1", "F2")), ("E207", ("v1", "v2", "F1", "F2")),
                     ("E209", ("v1", "v2", "F1", "F2")), ("E211r", ("v1", "v2", "F1", "F2", "NC")), ("E211t", ("v1", "v2"))):
        for m_ in mods:
            add(f"ROW {t_} {m_}", ("ROW", t_, m_))
    add("| the same schedule five hours apart (E208, aifoundry2 card 0) | 0.41 | 0.38 | 1.16 |",
        ("N", ["repeat.E208.cyc_op_mean.rms_pct", "repeat.E208.T_op_us.rms_pct", "repeat.E208.J_op.rms_pct"], "{:.2f}", ["0.41", "0.38", "1.16"]))
    add("| the two runs of each point in one day (E206's arms, E207) | 0.04 to 0.19 | 0.04 to 0.16 | 1.0 to 1.8 |",
        ("F", "within_day_span", ["0.04", "0.19", "0.04", "0.16", "1.0", "1.8"]))
    add("time at every point (119 and 113)", ("N", [f"{b}.E206A.models.v0.cyc_mean.n", f"{b}.E206B.models.v1.cyc_mean.n"], "{:d}", ["119", "113"]))
    add("(101 for MM1-v0 on arm A, 98 for both MM1 versions on arm B)", ("N", [f"{b}.E206A.models.v0.jo_g3.n", f"{b}.E206B.models.v1.jo_g3.n",
                                                                              f"{b}.E206B.models.v0.jo_g3.n"], "{:d}", ["101", "98", "98"]))
    add("arm B's MM1-v1 reads 14.3% (n 105) and arm A's MM1-v0 9.8% (n 109)", ("N", [f"{b}.E206B.models.v1.jo_g.rms_pct", f"{b}.E206B.models.v1.jo_g.n",
                                                                                   f"{b}.E206A.models.v0.jo_g.rms_pct", f"{b}.E206A.models.v0.jo_g.n"],
                                                                               ["{:.1f}", "{:d}", "{:.1f}", "{:d}"], ["14.3", "105", "9.8", "109"]))
    add("XREF: 14.30% (n 105) committed", ("T", NB, "| J over idle, given the measured seconds |", []), "arm B's committed all-points table")
    add("MM1-v1 reads 0.21 W rms on arm B's 7 and MM1-v0 0.31 W on arm A's 8", ("N", [f"{b}.E206B.under_3W.v1.rms_w", f"{b}.E206B.under_3W.v1.n",
                                                                                     f"{b}.E206A.under_3W.v0.rms_w", f"{b}.E206A.under_3W.v0.n"],
                                                                                 ["{:.2f}", "{:d}", "{:.2f}", "{:d}"], ["0.21", "7", "0.31", "8"]))
    add("(46 for MM1-v2, 50 for MM1-v1, 47 for F1, 46 for F2)", ("N", [f"{b}.E207.models.v2.jo_g3.n", f"{b}.E207.models.v1.jo_g3.n",
                                                                       f"{b}.E207.models.F1.jo_g3.n", f"{b}.E207.models.F2.jo_g3.n"], "{:d}", ["46", "50", "47", "46"]))
    add("time per case over the 47 cases", ("N", f"{b}.E207.n.cases_scored", "{:d}", ["47"]))
    add("time per case over the 41 cases", ("N", f"{b}.E209.n_cases", "{:d}", ["41"]))
    add("(45 for MM1-v2, 39 for MM1-v1, 42 for F1@800 and F2@800; no E209 point read under 3 W)",
        ("N", [f"{b}.E209.models.v2.jo_g3.n", f"{b}.E209.models.v1.jo_g3.n", f"{b}.E209.models.F1.jo_g3.n", f"{b}.E209.models.F2.jo_f3.n",
               f"{b}.E209.n_points_under_3W_measured"], ["{:d}", "{:d}", "{:d}", "{:d}", "zero_as_no"], ["45", "39", "42", "42", "no"]))
    add("on the scorer's own footing, the rms of ln, it reads 82.2%", ("N", f"{b}.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct", "{:.1f}", ["82.2"]))
    add("every point above 3 W", ("N", f"{b}.E211.W_min_measured", "above3", ["3"]))
    # never-run subsets
    add("24 of its 119 points are bridges from experiments in MM1-v0's own fit", ("N", [f"{b}.E206A.subsets.ran_before_any_card.n", f"{b}.E206A.n_points"],
                                                                                   "{:d}", ["24", "119"]))
    add("(11 of them on aifoundry3 itself)", ("F", "armA_on_a3", ["11"]))
    add("On the 95 points never run on any card MM1-v0 read **10.2% (-2.9)** in cycles and **10.4%** in joules over idle (8.8% at 3 W and above)",
        ("N", [f"{b}.E206A.subsets.never_any_card.n", f"{b}.E206A.subsets.never_any_card.models.v0.cyc_mean.rms_pct",
               f"{b}.E206A.subsets.never_any_card.models.v0.cyc_mean.bias_pct", f"{b}.E206A.subsets.never_any_card.models.v0.jo_g.rms_pct",
               f"{b}.E206A.subsets.never_any_card.models.v0.jo_g3.rms_pct"], ["{:d}", "{:.1f}", "{:.1f}", "{:.1f}", "{:.1f}"],
         ["95", "10.2", "-2.9", "10.4", "8.8"]))
    add("on the 24 bridges, 6.2% and 7.1%", ("N", [f"{b}.E206A.subsets.ran_before_any_card.n", f"{b}.E206A.subsets.ran_before_any_card.models.v0.cyc_mean.rms_pct",
                                                   f"{b}.E206A.subsets.ran_before_any_card.models.v0.jo_g.rms_pct"], ["{:d}", "{:.1f}", "{:.1f}"],
                                             ["24", "6.2", "7.1"]))
    add("On the 85 points never run on card 1, MM1-v1 read 4.7% in cycles and 15.5% in joules over idle (n 77)",
        ("T", NB, "| never run on card 1 before arm B | 10.0 / 4.7 / 18.5 (85) | 16.4 / 15.5 (77) / 23.2 (85) / 82.6 (81) |", ["85", "4.7", "15.5", "77"]))
    # report-fix (Q215): the same subset rebuilt by make_figures.py (arm B's README, item 8's list), its committed figures first, then at >= 3 W
    add("XREF: never on card 1 before arm B, rebuilt: 85 points, MM1-v1 4.7 in cycles, 15.5 (n 77) in J over idle on every point",
        ("N", [f"{b}.E206B.subsets.never_card1_before_armB.n", f"{b}.E206B.subsets.never_card1_before_armB.models.v1.cyc_mean.rms_pct",
               f"{b}.E206B.subsets.never_card1_before_armB.models.v1.jo_g.rms_pct", f"{b}.E206B.subsets.never_card1_before_armB.models.v1.jo_g.n"],
         ["{:d}", "{:.1f}", "{:.1f}", "{:d}"], ["85", "4.7", "15.5", "77"]), "equals arm B's dated note 1 (the check above)")
    add("its joules over idle read 12.7% (n 71; desk)", ("N", [f"{b}.E206B.subsets.never_card1_before_armB.models.v1.jo_g3.rms_pct",
                                                            f"{b}.E206B.subsets.never_card1_before_armB.models.v1.jo_g3.n"], ["{:.1f}", "{:d}"], ["12.7", "71"]))
    add("with the seconds forecast (F1's), it read 43.7% on E209 (82.2% as the scorer's rms of ln: it under-forecasts) and 30.8% on E211",
        ("N", [f"{b}.E209.models.F2.jo_f3.rms_pct", f"{b}.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct", f"{b}.E211.sets.rgm211_12.F2.jo_f3.rms_pct"],
         "{:.1f}", ["43.7", "82.2", "30.8"]))
    add("(E209's data README, item 6)", ("T", D209, ["6. **(e) The never-run search, repeated**", "E206 arms A and B\n   (e30's shape; aifoundry3 card 0 and aifoundry1 card 1)"],
                                         ["6"]), "e30 (gemmL2x8x4 int8) = E206's p016 (points-e206.json)")
    add("leaves E206's 119 points out as one fold", ("T", V2, "| LOEO, E206 (its fold, 119) |", ["119"]))
    add("MM1-v0 already carried an awake power of 3.660 W for it", ("T", V0, "aifoundry1 card 1 3.660 W", ["0", "3.660"]))
    add("its 53 points never ran on any card before MM1-v1 and MM1-v2 were frozen", ("T", V1, "53 points on aifoundry3 card 0, every one never run anywhere",
                                                                                     ["53"]))
    add("at 05:30 and 06:16 PST", ("T", V2S, "05:30:01 and 06:16:04 PST Tue 17 Nov 2026", ["05:30", "06:16"]))
    add("at 45 points never run on that card", ("T", E209, "tested on 45 points of the lab's GEMM (rgm136) that never ran on this card", ["45"]))
    add("(4 of them in both models' fit, 3 run in E207 before the freeze, 5 never run)",
        ("T", V2S11, "(rgm136: 4 in both models' fit, 3 run in E207 before the freeze, 5 never run)", ["4", "3", "5"]))
    add("its 12 rgm136 twins", ("T", V2S11, "the 12 gemmL twins", ["12"]))
    # E207
    add("at least 90% of its cases or points sit within twice MM1-v1's larger held-out error", ("T", E207, "a rule's verdict: PASS if at least 90% of its", ["90"]))
    add("13 to 16% per case in cycles and seconds", ("T", E207, ["| **T2** | cycles an op, the counter's mean (the host's cycles_per_op), per case | **16%** |",
                                                                 "| **T1** |"], ["16"]), "T1 and T3 at 13% (E207.md section 7 table)")
    add("15 to 16% per point in joules over idle", ("T", E207, ["| **E1** | J over idle given the measured seconds, per point (at 3 W and above) | **15%** |",
                                                                "| **E2** | J over idle with the seconds forecast, per point (at 3 W and above) | **16%** |"],
                                                    ["15", "16"]))
    add("5% and 13% with the card at rest", ("T", E207, ["| **E3** |", "| **E4** |"], []), "the E3 and E4 rows of E207.md section 7")
    add("T1 45/47, T2 44/47, T3 45/47", ("T", S207, "T1 PASS (45/47 within 0.13)\nT2 PASS (44/47 within 0.16)\nT3 PASS (45/47 within 0.13)", ["45", "47", "44"]))
    add("E1 50/53, E2 48/53, E3 51/53, E4 50/53", ("T", S207, "E1 PASS (50/53 within 0.15)\nE2 PASS (48/53 within 0.16)\nE3 PASS (51/53 within 0.05)\nE4 PASS (50/53 within 0.13)",
                                                   ["50", "53", "48", "51"]))
    add("39 to 8 (exact sign test p 5.5e-06", ("R", S207, "H1 MM1-v1 BETTER (MM1-v1 closer 39, other closer 8, ties 0, p 5.539621596994948e-06)",
                                               "5.539621596994948e-06", "{:.1e}", "5.5e-06"))
    add("H2 on the counter's mean 45 to 2", ("T", S207, "H2 MM1-v1 BETTER (MM1-v1 closer 45, other closer 2, ties 0", ["45", "2"]))
    add("H3 and H4 against F2 on joules over idle 47 to 2 each", ("T", S207, ["H3 MM1-v1 BETTER (MM1-v1 closer 47, other closer 2, ties 0",
                                                                              "H4 MM1-v1 BETTER (MM1-v1 closer 47, other closer 2, ties 0"], ["47", "2"]))
    add("(7/0/0 against F1, 8/0/0 against F2)", ("T", V2S, ["(sign test p 5.5e-06: MM1-v1 BETTER; families 7/0/0: MM1-v1 BETTER)",
                                                           "(sign test p 4.4e-12: MM1-v1 BETTER; families 8/0/0: MM1-v1 BETTER)"], ["7", "0", "8"]))
    add("closer at 24 cases against 18, p 0.44", ("T", V2S, "| MM1-v2 vs MM1-v1 | cycles, the wall | 24 | 18 | 5 | 0.441 | NOT DECIDED |", ["24", "18", "0.44"]))
    add("(30 against 11, p 0.0043)", ("T", V2S, "| MM1-v2 vs MM1-v1 | J at rest, t forecast | 30 | 11 | 8 | 0.00432 | MM1-v2 BETTER |", ["30", "11", "0.0043"]))
    add("but the family-level check does not confirm it (families 5 / 0 / 3: NOT DECIDED)",
        ("T", V2S, "| MM1-v2 vs MM1-v1 | J at rest, t forecast | 30 | 11 | 8 | 0.00432 | MM1-v2 BETTER | +0.0065 | 5 / 0 / 3: NOT DECIDED |", ["5", "0", "3"]))
    # E209
    add("62 of 62 runs in 26.16 card-minutes", ("T", D209, ["| runs | 62 of 62 ran; not run: none |", "**26.16 card-minutes**"], ["62", "26.16"]))
    add("first card command 10:30:44 PST, 8 h 46 min after", ("T", N15, "MM1-v2's forecasts (`3ca4b717`) precede T0 by 8 h 46 min", ["8", "46"]))
    add("29 shapes, three formats, four data kinds, five shire counts", ("T", E209, "29 shapes, three formats, four data kinds, five shire counts", ["29"]))
    add("15,675 of 15,675 samples carry it (600 MHz 11,545, 700 MHz 131, 800 MHz 3,999)",
        ("T", D209, "15,675 of 15,675: 600 MHz 11,545, 700 MHz 131, 800 MHz 3,999", ["15,675", "600", "11,545", "700", "131", "800", "3,999"]))
    add("it stepped inside every device process", ("T", D209, "It stepped inside all 64 device processes' windows", []))
    add("19% in cycles and seconds, 14% and 15% in joules over idle, 5% and 13% with the card at rest",
        ("T", E209, ["| **T1m / T1c** | cycles an op, the wall, per time case (m: given the measured clock; c: with the clock forecast) | **19%** |",
                     "| **E1** | J over idle given the measured seconds (and clock), per point | **14%** |",
                     "| **E2m / E2c** | J over idle with the seconds forecast, per point | **15%** |",
                     "| **E3** | J with the card at rest given the measured seconds and rest, per point | **5%** |",
                     "| **E4m / E4c** | J with the card at rest with the seconds forecast (the measured rest), per point | **13%** |"],
         ["19", "14", "15", "5", "13"]))
    add("pass when at least 90% of cases or points sit within twice MM1-v2's larger held-out error", ("T", E209, "PASS if at least 90%", ["90"]))
    add("T1m, T1c, T2m, T2c, T3m and T3c PASS at 39 of 41", ("T", N15, "T1m, T1c, T2m, T2c, T3m and T3c PASS at 39 of 41", ["39", "41"]))
    add("E1 PASS 45/45, E2m 42/45, E2c 41/44, E3 43/45, E4m 42/45, E4c 41/44",
        ("T", N15, "E1 PASS 45/45, E2m 42/45, E2c 41/44, E3 43/45, E4m 42/45, E4c 41/44", ["45", "42", "41", "44", "43"]))
    add("K1 (the clock forecast) PASS 44/45", ("T", N15, "K1 PASS 44/45", ["44", "45"]))
    add("XREF: E209 rules in the scorer's output", ("F", "e209_rules", []), "every count above equals scored-e209.json's rules")
    add("wall cycles **7.2%**, MM1-v1 9.3%, F1@800 18.1%", ("N", [f"{b}.E209.registered_summaries_ln.v2_m cycles wall.rms_ln_pct",
                                                               f"{b}.E209.registered_summaries_ln.v1_m cycles wall.rms_ln_pct",
                                                               f"{b}.E209.registered_summaries_ln.F1 cycles wall.rms_ln_pct"], "{:.1f}", ["7.2", "9.3", "18.1"]))
    add("seconds **5.4%** (45 points), MM1-v1 5.6% (39)", ("N", [f"{b}.E209.registered_summaries_ln.v2 J over idle given t.rms_ln_pct",
                                                              f"{b}.E209.registered_summaries_ln.v2 J over idle given t.n",
                                                              f"{b}.E209.registered_summaries_ln.v1 J over idle given t.rms_ln_pct",
                                                              f"{b}.E209.registered_summaries_ln.v1 J over idle given t.n"], ["{:.1f}", "{:d}", "{:.1f}", "{:d}"],
                                                          ["5.4", "45", "5.6", "39"]))
    add("F2@800 with its seconds 82.2%", ("N", f"{b}.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct", "{:.1f}", ["82.2"]))
    add("(+0.0158, 95% [+0.0037, +0.0293] in ln)", ("T", N15, "**MM1-v2 BETTER**: the mean d +0.0158, 95% [+0.0037, +0.0293]", ["+0.0158", "95", "+0.0037", "+0.0293"]))
    add("the sign test reads 17 against 11 (p 0.345: NOT DECIDED)", ("T", N15, "the sign test, 17 against 11, p 0.345: **NOT DECIDED**", ["17", "11", "0.345"]))
    add("the families split 2 against 2", ("T", N15, "and the families split 2 against 2", ["2"]))
    add("The subsets carry 67% of the summed difference", ("T", N15, "**The subsets carry 67% of the summed d**", ["67"]))
    add("(H5, 38 against 3, p 1.05e-08)", ("T", N15, "| H5 (cycles, the wall, against F1@800) | **MM1-v2 BETTER**: the sign test, 38 against 3, p 1.05e-08 |",
                                          ["5", "38", "3", "1.05e-08"]))
    add("(H6, 35 against 5, p 1.38e-06)", ("T", N15, "**MM1-v2 BETTER**: 35 against 5, p 1.38e-06", ["6", "35", "5", "1.38e-06"]))
    add("(e39) ran 24% more cycles than MM1-v2 forecast", ("R", N15, "| T1m, T3m (19%) | PASS 39 of 41 | 2 | e39 +23.96%, e15 +19.34% |", "23.96", "{:.0f}", "24"))
    add("`gemmL3x1x5` fp32 (e15) 19%", ("R", N15, "| T1m, T3m (19%) | PASS 39 of 41 | 2 | e39 +23.96%, e15 +19.34% |", "19.34", "{:.0f}", "19"))
    add("failed T2's 19% band by 0.03 points", ("F", "e42_margin", ["19", "0.03"]))
    add("The stride step at NB 8 measured 1.297 against MM1-v2's 1.187", ("T", N15, "measured **1.297**; MM1-v2 1.187", ["8", "1.297", "1.187"]))
    add("int8 at one K block (e07) ran 1.158 times MM1-v2's wall cycles", ("T", N15, "measured **x1.158**", ["1.158"]))
    add("real int8 tiles saved 9.0% of the joules against MM1-v2's 2.7%", ("T", N15, "Real int8 data save 9.0% against random, and MM1-v2 forecast 2.7%",
                                                                         ["9.0", "2.7"]))
    # E211
    add("38 of 38 runs and the smoke in 17.99 card-minutes", ("T", D211, ["the smoke, the stop-path test, 38 of 38 runs", "| 17.99 (planned 20.4"], ["38", "17.99"]))
    add("(13%, 16% and 13% in cycles and seconds; 15%, 16%, 5% and 13% in joules), PASS at 90% of rgm211's 12 points",
        ("T", E211, ["**13%, 16%, 13%** (E207's bands", "**15%, 16%, 5%, 13%**", "PASS at >= 90% of the scored points", "MM1 at rgm211's 12 points"],
         ["13", "16", "15", "5", "90", "12"]))
    add("**T1 11/12, T2 12/12, T3 11/12, E1 12/12, E2 12/12, E3 11/12, E4 12/12: PASS**",
        ("T", cfg["S211"], ["T1: PASS (11/12)", "T2: PASS (12/12)", "T3: PASS (11/12)", "E1: PASS (12/12)", "E2: PASS (12/12)", "E3: PASS (11/12)",
                            "E4: PASS (12/12)"], ["11", "12"]), cfg["S211_note"])
    add("ran 2.9% and 5.8% fewer wall cycles on rgm211", ("T", V2S11, "rgm211 ran 2.9% and 5.8% fewer wall cycles an op at x01 and x02", ["2.9", "5.8"]))
    add("(tolerance 0.01 in ln)", ("T", E211, "| **0.01** (the two ELFs' layout bound)", ["0.01"]))
    add("(the two controls differ by 0.031 in ln)", ("T", V2S11, "the two controls differ by 0.031 in ln", ["0.031"]))
    add("W1, the ratio rule, reads FAIL 5/10", ("T", cfg["S211"], "W1: FAIL (5/10)", ["1", "5", "10"]), cfg["S211_note"])
    add("MM1 BETTER (10/1/1, p 0.0117)", ("R", cfg["S211"], "H5: MM1 BETTER (10/1/1, p 0.01171875)", "0.01171875", "{:.4f}", "0.0117"), cfg["S211_note"])
    add('W2 (the direction) PASS, with the same words, "the controls did not pass: not a model test"', ("F", "e211_w2_caveat", []),
        "scores-e211-A.json rules.W2: verdict and caveat")
    add("(frozen 5 h 8 min before the first card command;", ("T", V2S11, "5 h 8 min 23 s before E211's first card command", ["5", "8"]))
    add("its wall cycles read **8.9%** rms (+4.0), MM1-v1 8.1%, F1 14.5%, NC 23.5%",
        ("N", [f"{b}.E211.sets.rgm211_12.v2.cyc_wall.rms_pct", f"{b}.E211.sets.rgm211_12.v2.cyc_wall.bias_pct", f"{b}.E211.sets.rgm211_12.v1.cyc_wall.rms_pct",
               f"{b}.E211.sets.rgm211_12.F1.cyc_wall.rms_pct", f"{b}.E211.sets.rgm211_12.NC.cyc_wall.rms_pct"], "{:.1f}", ["8.9", "4.0", "8.1", "14.5", "23.5"]))
    add("on the 12 rgm136 twins MM1-v2 read 2.9% and MM1-v1 3.7%", ("N", [f"{b}.E211.sets.twins_12.v2.cyc_wall.rms_pct", f"{b}.E211.sets.twins_12.v1.cyc_wall.rms_pct"],
                                                                     "{:.1f}", ["2.9", "3.7"]))
    add("(3.2% for both versions; F1 18.4%)", ("N", [f"{b}.E211.sets.rgm211_12.v2.jo_g3.rms_pct", f"{b}.E211.sets.rgm211_12.v1.jo_g3.rms_pct",
                                                     f"{b}.E211.sets.rgm211_12.F1.jo_g3.rms_pct"], "{:.1f}", ["3.2", "3.2", "18.4"]))
    add("The ratio rgm211 / rgm136 over 10 pairs, rms of ln: MM1-v2 0.074, MM1-v1 0.065, F1 0.128, NC 0.126, N0 (no walk effect) 0.135",
        ("T", V2S11, ["MM1-v2 rms 0.074 (bias +0.020), MM1-v1 0.065, F1 0.128, NC 0.126, N0 0.135", "(10 W pairs, raw, ln(model / measured))"],
         ["10", "0.074", "0.065", "0.128", "0.126", "0.135"]))
    add("but its cycles error rose from 3-4% to 8-9%", ("F", "e211_span", ["3-4", "8-9"]))
    # E206
    add("MM1-v0 closer than F1 at **89 of 119** points in cycles", ("N", [f"{b}.E206A.h2h.v0<F1:cyc_mean.closer", f"{b}.E206A.h2h.v0<F1:cyc_mean.n"], "{:d}",
                                                                   ["89", "119"]))
    add("**96 of 109** in joules over idle; closer than F2 at **104 of 109**", ("N", [f"{b}.E206A.h2h.v0<F1:jo_g.closer", f"{b}.E206A.h2h.v0<F1:jo_g.n",
                                                                                   f"{b}.E206A.h2h.v0<F2:jo_g.closer", f"{b}.E206A.h2h.v0<F2:jo_g.n"], "{:d}",
                                                                               ["96", "109", "104", "109"]))
    add("MM1-v1 closer than F1 at **87 of 113** in cycles and **85 of 105** in joules over idle; closer than F2 at **99 of 105**",
        ("N", [f"{b}.E206B.h2h.v1<F1:cyc_mean.closer", f"{b}.E206B.h2h.v1<F1:cyc_mean.n", f"{b}.E206B.h2h.v1<F1:jo_g.closer",
               f"{b}.E206B.h2h.v1<F1:jo_g.n", f"{b}.E206B.h2h.v1<F2:jo_g.closer", f"{b}.E206B.h2h.v1<F2:jo_g.n"], "{:d}", ["87", "113", "85", "105", "99", "105"]))
    add("XREF: 87 of 113 (committed)", ("T", NB, "| cycles an op, the counter's mean | 85/113 | 87/113 | 69/113 (1 tied) | - | - |", []), "arm B's committed head to head")
    add("XREF: 85 of 105 / 99 of 105 (committed)", ("T", NB, "| J over idle, given the measured seconds | 83/105 | 85/105 | 66/105 | 101/105 | 99/105 |", []))
    add("MM1-v1 was closer than MM1-v0 at 69 of 113 in cycles", ("N", [f"{b}.E206B.h2h.v1<v0:cyc_mean.closer", f"{b}.E206B.h2h.v1<v0:cyc_mean.n"], "{:d}",
                                                                 ["69", "113"]))
    # report-fix (Q215): the same head-to-head joule counts on E207's footing (points of 3 W and above)
    add("On E207's footing, the points of 3 W and above: closer than F1 at 91 of 101 and than F2 at 99 of 101",
        ("N", [f"{b}.E206A.h2h.v0<F1:jo_g3.closer", f"{b}.E206A.h2h.v0<F1:jo_g3.n", f"{b}.E206A.h2h.v0<F2:jo_g3.closer", f"{b}.E206A.h2h.v0<F2:jo_g3.n"],
         "{:d}", ["91", "101", "99", "101"]))
    add("At the points of 3 W and above: closer than F1 at 81 of 98 and than F2 at 95 of 98 (desk)",
        ("N", [f"{b}.E206B.h2h.v1<F1:jo_g3.closer", f"{b}.E206B.h2h.v1<F1:jo_g3.n", f"{b}.E206B.h2h.v1<F2:jo_g3.closer", f"{b}.E206B.h2h.v1<F2:jo_g3.n"],
         "{:d}", ["81", "98", "95", "98"]))
    # the repeat floor
    add("The same 85-run schedule", ("T", REPR, "RAN FULL (85 of 85 runs)", ["85"]))
    add("repeated to **0.41%** rms in cycles an op", ("N", "repeat.E208.cyc_op_mean.rms_pct", "{:.2f}", ["0.41"]))
    add("0.38% on the slowest minion", ("N", "repeat.E208.cyc_op_max.rms_pct", "{:.2f}", ["0.38"]))
    add("0.38% in seconds", ("N", "repeat.E208.T_op_us.rms_pct", "{:.2f}", ["0.38"]))
    add("**1.19%** in watts over idle", ("N", "repeat.E208.dP_w.rms_pct", "{:.2f}", ["1.19"]))
    add("**1.16%** in joules over idle", ("N", "repeat.E208.J_op.rms_pct", "{:.2f}", ["1.16"]))
    add("(0.72% with the die corrected to 50 C, post hoc)", ("N", "repeat.E208.J_op_c50.rms_pct", "{:.2f}", ["0.72"]))
    add("XREF: 0.409% committed", ("T", REP, "| cycles an op (mean over minions) | 71 | -0.002% | 0.409% |", []), "E208's committed repeat table")
    add("XREF: 1.163% committed", ("T", REP, "| J over idle an op (nJ) | 60 | -0.932% | 1.163% |", []))
    add("differed by 0.04 to 0.19% rms in cycles and 1.0 to 1.8% in joules over idle", ("F", "within_day_span2", ["0.04", "0.19", "1.0", "1.8"]))
    add("MM1's blind errors are 3 to 23 times the session repeat", ("N", ["blind_summary.over_repeat_min", "blind_summary.over_repeat_max"], "{:.0f}", ["3", "23"]))
    # the separate session's sweeps and seals
    add("rgm136 unchanged, 74 arms on three cards", ("T", E208, "over 74 arms", ["74"]))
    add("221 arms and an anchor in 10 sessions", ("T", E212, "over 221 arms and an anchor in 10 sessions", ["221", "10"]))
    add("is in progress: as of `724e8f39`, nine of its ten sessions are committed (`d2ece7e8`, `5601b6a7`, `7726e127`, `a90105da`, `7dfba40b`, "
        "`ebe552fe`, `d8de38b0`, `58f01105`, `724e8f39`)",
        ("F", "e212_sessions_at", ["nine", "d2ece7e8", "5601b6a7", "7726e127", "a90105da", "7dfba40b", "ebe552fe", "d8de38b0", "58f01105", "724e8f39"]),
        "the E212 data folders in the tree of 724e8f39, each with the commit that added it")
    add("`8f2df483`, was sealed at 12:58:15 PST, 3 min 50 s before the first session it covers (a1c1-S2) made its first card command",
        ("T", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S2/README.md",
         "was sealed by #11.7.1 (12:58:15 PST, sha256 `8f2df48375701d3b6304e233d3d8c09e2ba9ee85ef431c9faabdc258094d010d`), 3 min 50 s before this "
         "session's first card command", ["12:58:15", "3", "50"]))
    add("XREF: every sealed sha256 in its registration", ("F", "seals", []), "each sha256 prefix of the table found in the file that registers it")
    # ---------------------------------------------------------------- 5
    add("nine fp32 operand patterns never run in a GEMM, at two shapes", ("T", E210, "for nine fp32 operand patterns never run in a GEMM", []))
    add("random minus zeros: 29.78 W and 20.53 W", ("T", E210, "S1 D = 29.78 W, S2 D = 20.53 W", ["29.78", "20.53"]))
    add("the time equality PASS in all 20 cases", ("T", N210, "the time equality **T PASS** in all 20 cases", ["20"]))
    add("B5 (R1 within 5% of D", ("T", N210, "every band was 0.05 D", ["5"]), "0.05 D = 5% of D")
    add("PASS 13 of 13", ("T", N210, "**B5 PASS** (13 of 13 scored test cases inside the switch route's band; 10 needed)", ["13"]))
    add("the nearest measured kind (H1, 10 to 1)", ("T", N210, "than R4, the null (H1: 10 to 1, 2 ties)", ["1", "10"]))
    add("the raw bit-flip price (H2, 12 to 0)", ("T", N210, "than R3, the raw bit-flip price (H2: 12 to 0, 1 tie)", ["2", "12", "0"]))
    add("the bit-flip price with one scale (H3, 10 to 0)", ("T", N210, "(H3: 10 to 0, 3 ties)", ["3", "10", "0"]))
    add("UNDECIDED (4 to 0 with 1 tie; 5 cases, too few to decide, as registered)", ("T", N210, ["**UNDECIDED** (4 to 0, 1 tie)", "R2 forecasts 5 test cases"],
                                                                                     ["4", "0", "1", "5"]))
    add("R1's error is **0.481 W rms, 1.87% of D**", ("T", N210, "**0.481 W rms, 1.87% of D**", ["0.481", "1.87"]))
    add("against 3.849 W (16.19%) for the scaled bit flips, 5.128 W (19.71%) for the nearest kind, 5.575 W (21.22%, 5 cases) for MM1-v1's kind term "
        "and 12.165 W (47.48%) for the raw bit flips",
        ("T", N210, ["| R3L, the bit-flip price with one scale | 13 | 3.849 | +0.816 | 16.19% |", "| R4, the null (nearest kind) | 13 | 5.128 | +0.496 | 19.71% |",
                     "| R2, MM1-v1's kind term | 5 | 5.575 | -4.691 | 21.22% |", "| R3, the raw bit-flip price | 13 | 12.165 | +7.834 | 47.48% |"],
         ["3.849", "16.19", "5.128", "19.71", "5.575", "21.22", "5", "12.165", "47.48"]))
    add("sits within 0.8% of the calibrated one", ("F", "kappa_span", ["0.8"]))
    add("(S1 1.6767 × 10^16 switches a J against 1.6733 × 10^16; S2 1.6235 against 1.6367 × 10^16)",
        ("T", N210, ["**S1 kappa 1.6767 x 10^16 switches a J**", "against the calibrated 1.6733 x 10^16", "**S2 kappa 1.6235 x 10^16**", "against 1.6367 x 10^16"],
         ["1", "1.6767", "16", "1.6733", "2", "1.6235", "1.6367"]))
    add("H1 is UNDECIDED (6 to 1, 1 tie)", ("T", N210, "UNDECIDED (6/1/1)", ["1", "6"]))
    add("142 of 171 runs, when the card-time rule stopped new runs at 85.01 card-minutes", ("T", D210, ["RAN SHORT (142 of 171 runs", "| 85.01 (planned about 73"],
                                                                                            ["142", "171", "85.01"]))
    add("the die gate made each run about 35 s, not the planned 26", ("T", N210, ["the session took 35.1 s a run", "against the plan's 26 s (S1)"], ["35", "26"]))
    add("9 of the 13 test cases are scored on 2 of 3 blocks", ("T", N210, "So 9 of the 13 test cases are scored on 2 of 3 blocks", ["9", "13", "2", "3"]))
    add("committed data put ones at about 0.31 of D where the count says about 0.05", ("T", E210, "ones at about 0.05 of D against 0.31 measured", ["0.31", "0.05"]))
    # ---------------------------------------------------------------- 6
    add("(M a multiple of 1,024, N of 512, K of a block)", ("T", E209, "M a multiple of 1,024, N of 512, K of one block per format", ["1,024", "512"]))
    add("E211 shows a recompiled kernel's cycles drift 8-9%", ("F", "e211_span_hi", ["8-9"]))
    add("MM1-v2's energy reads 10.13% against 9.15% for MM1-v1's form", ("T", V2, "LOCO 10.13% against 9.15% (the awake power does not carry across cards)",
                                                                       ["10.13", "9.15"]))
    add("and MM1-v1's 14.2-42.1%", ("T", V1, "| W over idle, LOCO aifoundry3 / card 1 / aifoundry2 | 21.2% / 14.2% / 42.1% |", ["14.2", "42.1"]))
    add("missed the int8 saving by 6 points", ("F", "kinds_gap", ["6"]))
    # report-fix (Q215): MM1-v1 on E207's b49-b52 (the verification's medium finding)
    add("E207's real and designed tiles b49-b52 were NOT FORECAST in energy by MM1-v2", ("T", V2S, "Its energy is NOT FORECAST at b49-b52 (the blind4 and blind3 kinds)", []))
    add('("blind4: M6; blind3: M5"', ("T", V1, "(blind4: M6; blind3: M5)", []), "MM1-v1's rule for a kind with no ledger row")
    add("given the measured seconds read -5.4%, -6.0%, +4.2% and +7.1% at b49-b52, with E1 and E2 PASS at all four",
        ("F", "e207_b49_b52", ["-5.4", "-6.0", "+4.2", "+7.1"]), "scores-e207-A.json points b49-b52: MM1-v1's given J over idle / measured - 1; rules E1, E2")
    add("On arm B's 14 all-zero points", ("N", f"{b}.E206B.classes.data kind: zeros.n", "{:d}", ["14"]))
    add("joules over idle **27.8%** rms (**+25.7%** bias)", ("N", [f"{b}.E206B.classes.data kind: zeros.jo_g.v1.rms_pct",
                                                                   f"{b}.E206B.classes.data kind: zeros.jo_g.v1.bias_pct"], "{:.1f}", ["27.8", "25.7"]))
    add("MM1-v0 33.7% (+31.4%)", ("N", [f"{b}.E206B.classes.data kind: zeros.jo_g.v0.rms_pct", f"{b}.E206B.classes.data kind: zeros.jo_g.v0.bias_pct"],
                                  "{:.1f}", ["33.7", "31.4"]))
    add("where F1 read 13.5%", ("N", f"{b}.E206B.classes.data kind: zeros.jo_g.F1.rms_pct", "{:.1f}", ["13.5"]))
    add("closer at 13 of the 14", ("T", NB, "where F1 is closer at 14 and 13 of 14 points (F1 13.5% rms)", ["13", "14"]))
    add("XREF: zeros committed", ("T", NB, "| data kind: zeros | 14 | 9.2 (-4.6) / 3.9 (-1.7) / 19.0 (+10.7) | 33.7 (+31.4) / 27.8 (+25.7) / 13.5 (+5.2)", []),
        "arm B's committed class row")
    add("watts over idle +21.2% (42 runs", ("T", V2, "zeros on card 1: W over idle +21.2% (42 runs", ["21.2", "42"]))
    add("(2.406 W at 1,024 minions against MM1-v1's 3.257 W)", ("T", V2, "Pmin 2.406 W (v1 3.257 from one shape)", ["2.406", "3.257"]))
    add("the subset points of 3 W and above read 7.0% for MM1-v1", ("N", f"{b}.E206B.classes.subset (mask < 32 shires).jo_g3.v1.rms_pct", "{:.1f}", ["7.0"]))
    add("the 7 under 3 W (1, 4 or 8 shires, 0.31 to 2.78 W over idle) read -0.05 to +0.39 W off, MM1-v1 high at 6 of them, and its four one-shire "
        "points sit +0.18 to +0.22 W high", ("F", "armB_under3", ["7", "1", "4", "8", "0.31", "2.78", "-0.05", "+0.39", "6", "+0.18", "+0.22"]))
    add("+62% and +43% at the two smallest", ("T", NB, "by +62% and +43%", ["62", "43"]))
    add("-14.0% (mask 0x3) and -10.2% (0xfff) in wall cycles; MM1-v2's contention on the DRAM stream alone moved them to -0.5% and -0.9%",
        ("T", V2S, "from MM1-v1's -14.0% (0x3) and -10.2% (0xfff) to -0.5% and -0.9%", ["14.0", "10.2", "0.5", "0.9"]))
    add("3x6x4 fp32 on 12 shires (0xfff)", ("T", V2S, "3x6x4 fp32 on 12 shires (0xfff)", ["12"]))
    add("+13.3%: on that mask", ("T", V2S, "947.8 cycles an op measured, +13.3%", ["13.3"]))
    add("faster than on 2 or on 24 shires", ("T", V2S, "faster than on 2 shires (0x3, 1066.7) or on 24 (0xffffff, 1080.0), which no model forecast", ["2", "24"]))
    add("On E209 the one shire 0x80000000 ran 24% over MM1-v2", ("R", N15, "| T1m, T3m (19%) | PASS 39 of 41 | 2 | e39 +23.96%, e15 +19.34% |", "23.96", "{:.0f}", "24"))
    add("MM1-v2 was closer than MM1-v1 at 6 of the 9 subset points", ("T", N15, "On the wall, MM1-v2 is closer at 6 of 9 subset points", ["6", "9"]))
    add("E209's step at NB 8 measured 1.297 against MM1-v2's 1.187", ("T", N15, "measured **1.297**; MM1-v2 1.187", ["8", "1.297", "1.187"]))
    add("int8 at one K block ran 1.158 times MM1-v2's wall cycles on E209 (e07)", ("T", N15, "measured **x1.158**", ["1.158"]))
    add("and -14.0% on E207 (n01)", ("T", V2S, "against MM1-v2's 741.2 (-14.0%", ["14.0"]))
    add("-18.4% (E207's n02, int8) and -13.6% (n03, fp32)", ("T", V2S, "n02 (int8) -18.4% for MM1-v2 (MM1-v1 -19.9%) and n03 (fp32) -13.6%", ["18.4", "13.6"]))
    add("int8 inside the L3 ran 6.3 to 6.5% more cycles than fp32", ("F", "e207_int8_l3_span", ["6.3", "6.5"]),
        "scores-e207-A.json cases: measured wall cycles, int8 / fp32 - 1, at 1x3x2, 2x3x2, 3x2x2 and 1x4x3 (score-e207.md rounds the top to 6.6)")
    add("rgm211's controls ran 3-6% fast, and MM1's cycles error there was 8-9%", ("F", "e211_controls_and_hi", ["3-6", "8-9"]))
    add("(e44, 788.9 MHz measured against 764.1 forecast)", ("T", N15, "it measured 788.9 MHz against the forecast's 764.1", ["788.9", "764.1"]))
    add("two of 55 runs whose capped state MM1-v2 read wrong", ("T", N15, "MM1-v2's capped forecast agrees with 53 of 55 kept runs'", ["55"]), "55 - 53 = 2")
    # ---------------------------------------------------------------- 7
    add("about 16 minutes in all", ("T", V2, "about 16 minutes in all", ["16"]))
    return C


# ---------------------------------------------------------------- evaluation

def get(N, path):
    special = ["data kind: zeros", "subset (mask < 32 shires)", "v2_m cycles wall", "v1_m cycles wall", "F1 cycles wall", "F2 J over idle",
               "v2 J over idle given t", "v1 J over idle given t", "v0<F1:cyc_mean", "v0<F1:jo_g", "v0<F2:jo_g", "v1<F1:cyc_mean", "v1<F1:jo_g",
               "v1<F2:jo_g", "v1<v0:cyc_mean"]
    parts, rest = [], path
    while rest:
        hit = None
        for sname in special:
            if rest.startswith(sname + ".") or rest == sname:
                hit = sname
                break
        if hit:
            parts.append(hit)
            rest = rest[len(hit) + 1:]
        else:
            head, _, rest = rest.partition(".")
            parts.append(head)
    cur = N
    for p in parts:
        cur = cur[p]
    return cur


def fmt(v, f):
    if f == "pct0":
        return f"{100 * v:.0f}"
    if f == "{:d}":
        return str(int(v))
    if f == "zero_as_no":
        return "no" if v == 0 else str(v)
    if f == "above3":
        return "3" if v > 3.0 else f"NOT ABOVE 3 ({v})"
    return f.format(v)


def norm_num(s):
    return s.replace(",", "").lstrip("+")


def git_last(repo, rel):
    try:
        return subprocess.run(["git", "-C", repo, "log", "-1", "--format=%h", "--", rel], capture_output=True, text=True, timeout=60).stdout.strip() or "-"
    except Exception:  # noqa: BLE001
        return "?"


def git_time(repo, c):
    out = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%ci", c], capture_output=True, text=True, timeout=60).stdout.strip()
    return out.split()[1] if out else None


ROWNAME = {"E206A": "E206 arm A", "E206B": "E206 arm B", "E207": "E207", "E209": "E209", "E211r": "E211, rgm211's 12 points",
           "E211t": "E211, the 12 rgm136 twins"}
MODNAME = {"v0": "MM1-v0", "v1": "MM1-v1", "v2": "MM1-v2", "F1": "F1", "F2": "F2", "NC": "NC (the chip-lines null)"}


def modname(t, m):
    if t == "E209" and m in ("F1", "F2"):
        return m + "@800"
    return MODNAME[m]


def row_expected(N, t, mod):
    if t in ("E211r", "E211t"):
        m = N["blind"]["E211"]["sets"]["rgm211_12" if t == "E211r" else "twins_12"][mod]
    else:
        m = N["blind"][t]["models"][mod]
    cells = []
    for q in ("cyc_mean", "t", "jo_g3", "jo_f3", "jr_g"):
        a = m.get(q)
        cells.append(f"{a['rms_pct']:.1f} ({a['bias_pct']:+.1f})" if a else "-")
    return cells


def readme_row(readme, t, mod):
    tname, mname = ROWNAME[t], modname(t, mod)
    cur = None
    for ln in readme.splitlines():
        cells = [c.strip().replace("**", "") for c in ln.strip().strip("|").split("|")]
        if len(cells) == 7 and cells[0]:
            cur = cells[0]
        if len(cells) == 7 and cells[1] == mname and (cells[0] == tname or (cells[0] == "" and cur == tname)):
            return cells[2:], ln
    return None, None


def committed_row(repo, t, mod):
    """The same cells as a committed table prints them, where one exists (None: desk only). Only the quantities on the same footing."""
    if t == "E206B":
        txt = open(os.path.join(repo, NB)).read()
        col = {"v0": 1, "v1": 2, "F1": 3, "F2": 4}[mod]
        rows = {"cyc_mean": "| cycles an op, the counter's mean |", "t": "| seconds a GEMM |", "jr_g": "| J at rest, given the measured seconds |"}
        out = {}
        for q, start in rows.items():
            ln = [x for x in txt.splitlines() if x.startswith(start)][0]
            cell = [c.strip() for c in ln.strip().strip("|").split("|")][col]
            mm = re.match(r"([\d.]+)% \(([-+][\d.]+)%\)", cell)
            out[q] = f"{mm.group(1)} ({mm.group(2)})" if mm else "-"
        return out
    if t == "E207":
        txt = open(os.path.join(repo, V2S)).read()
        col = {"v2": 1, "v1": 2, "F1": 3, "F2": 4}[mod]
        rows = {"cyc_mean": "| cycles an op, the counter's mean (per case) |", "t": "| seconds a GEMM (per case) |",
                "jo_g3": "| J over idle given the measured seconds (>= 3 W) |", "jo_f3": "| J over idle with the seconds forecast (>= 3 W) |",
                "jr_g": "| J with the card at rest given the measured seconds |"}
        out = {}
        for q, start in rows.items():
            ln = [x for x in txt.splitlines() if x.startswith(start)][0]
            cell = [c.strip() for c in ln.strip().strip("|").split("|")][col]
            mm = re.match(r"([\d.]+)% \(([-+][\d.]+)\)", cell)
            out[q] = (mm.group(1), mm.group(2)) if mm else "-"
        return out
    if t in ("E211r", "E211t"):
        txt = open(os.path.join(repo, V2S11)).read()
        head = "**rgm211's 12 points (gemmLn" if t == "E211r" else "**the 12 gemmL twins (rgm136"
        seg = txt[txt.index(head):]
        seg = seg[:seg.index("\n\n**", 10)] if "\n\n**" in seg[10:] else seg
        col = {"v2": 1, "v1": 2, "F1": 3, "F2": 4, "NC": 5}[mod]
        rows = {"cyc_mean": "| cycles an op, the counter's mean |", "t": "| seconds a GEMM |", "jo_g3": "| J over idle, given the measured seconds |",
                "jo_f3": "| J over idle, seconds forecast |", "jr_g": "| J with the card at rest, given the seconds (measured rest) |"}
        out = {}
        for q, start in rows.items():
            ln = [x for x in seg.splitlines() if x.startswith(start)][0]
            cell = [c.strip() for c in ln.strip().strip("|").split("|")][col]
            mm = re.match(r"([\d.]+)% \(([-+][\d.]+)%\)", cell)
            out[q] = f"{mm.group(1)} ({mm.group(2)})" if mm else "-"
        return out
    return None


def run_f(name, repo, N):
    B = N["blind"]
    if name in ("r6_count", "r6_configs", "r6_summary"):
        n, tot, cfgs = 0, 0, set()
        for rel_p in (R129, R148, R155):
            txt = open(os.path.join(repo, rel_p)).read()
            if rel_p == R129:
                for m in re.finditer(r"\| R6 (\S+)\.zeros \| (\w+) \(measured ([\d.]+), predicted ([\d.]+)\) \|", txt):
                    tot += 1
                    if m.group(2) == "PASS" and abs(float(m.group(3)) - float(m.group(4))) <= 2.0:
                        n += 1
                    cfgs.add(m.group(1))
            else:
                ln = [x for x in txt.splitlines() if x.startswith("rule R6:")][0]
                d = json.loads(ln.split(":", 1)[1])
                for k, v in d.items():
                    tot += 1
                    if v["verdict"] == "PASS" and abs(v["predicted"] - v["measured"]) <= 2.0:
                        n += 1
                    cfgs.add(k)
        out = {"r6_count": [str(n), str(tot)], "r6_configs": [str(len(cfgs))], "r6_summary": [str(len(cfgs)), str(n)]}[name]
        return out, f"{R129}, {R148}, {R155} (readings {tot}, passing within 2 cycles {n}, configurations {len(cfgs)})"
    if name == "macs_per_op":
        P = json.load(open(os.path.join(repo, PTS)))["points"]
        out = []
        for fm in ("fp32", "fp16", "int8"):
            vals = {p["macs_per_gemm"] / (p["minions"] * p["ops_per_minion_per_gemm"]) for p in P if p["format"] == fm and p["arm"].startswith("gemmL")}
            assert len(vals) == 1, vals
            out.append(f"{vals.pop():,.0f}")
        return out, PTS
    if name in ("l1x1x1_cycles", "l1x1x1_cycles_fp32"):
        S = json.load(open(os.path.join(repo, SA)))["readings"]["A"]["a_contention"]
        a = [x for x in S["gemmL1x1x1.fp32"] if x["mask"] == "0xffffffff"][0]["cycles_per_op"]
        c = [x for x in S["gemmL1x1x1.int8"] if x["mask"] == "0xffffffff"][0]["cycles_per_op"]
        return ([f"{a:.2f}", f"{c:.2f}"] if name == "l1x1x1_cycles" else [f"{a:.2f}"]), SA
    if name == "int8_roles":
        v = 283.03 + 0.0146 * 600
        txt = open(os.path.join(repo, E206)).read()
        ok = "318 in int8" in txt and "floor: 529 / 270 cycles" in open(os.path.join(repo, V0)).read()
        return (["318", f"{v:.0f}", "270"] if ok else ["literal missing"]), f"{E206}; {V0} (283.03 + 0.0146 µs x 600 MHz = {v:.2f})"
    if name == "registered_share":
        g = N["timing"]["tensor_share_registered"]
        txt = open(os.path.join(repo, E206)).read()
        lit = "546 cycles an op in fp32 and fp16, 318 in int8" in txt
        return (["546" if lit else "?", "318" if lit else "?", f"{100 * g['all']['min']:.0f}", f"{100 * g['all']['max']:.0f}",
                 f"{100 * g['all']['median']:.0f}", str(g["all"]["n"]), str(g["above_1"])], "numbers.json timing.tensor_share_registered; " + E206)
    if name == "rest_span":
        f1 = [B[t]["models"]["F1"]["jr_g"]["rms_pct"] for t in ("E206A", "E206B", "E207", "E209")] + [B["E211"]["sets"]["rgm211_12"]["F1"]["jr_g"]["rms_pct"]]
        f2 = [B[t]["models"]["F2"]["jr_g"]["rms_pct"] for t in ("E206A", "E206B", "E207")]
        return [f"{min(f1):.1f}", f"{max(f1):.1f}", f"{min(f2):.1f}", f"{max(f2):.1f}"], "numbers.json (F1 and F2 jr_g over the tests that price it)"
    if name == "within_day_span":
        w = N["repeat"]["within_day"]
        c = [w[k]["cyc_mean"]["rms_pct"] for k in w]
        t = [w[k]["t"]["rms_pct"] for k in w]
        j = [w[k]["j_over_3W"]["rms_pct"] for k in w]
        return [f"{min(c):.2f}", f"{max(c):.2f}", f"{min(t):.2f}", f"{max(t):.2f}", f"{min(j):.1f}", f"{max(j):.1f}"], "numbers.json repeat.within_day"
    if name == "within_day_span2":
        w = N["repeat"]["within_day"]
        c = [w[k]["cyc_mean"]["rms_pct"] for k in w]
        j = [w[k]["j_over_3W"]["rms_pct"] for k in w]
        return [f"{min(c):.2f}", f"{max(c):.2f}", f"{min(j):.1f}", f"{max(j):.1f}"], "numbers.json repeat.within_day"
    if name in ("e211_span", "e211_span_hi"):
        S = B["E211"]["sets"]
        lo = sorted([S["twins_12"]["v2"]["cyc_wall"]["rms_pct"], S["twins_12"]["v1"]["cyc_wall"]["rms_pct"]])
        hi = sorted([S["rgm211_12"]["v2"]["cyc_wall"]["rms_pct"], S["rgm211_12"]["v1"]["cyc_wall"]["rms_pct"]])
        a, b_ = f"{lo[0]:.0f}-{lo[1]:.0f}", f"{hi[0]:.0f}-{hi[1]:.0f}"
        return ([a, b_] if name == "e211_span" else [b_]), "numbers.json (E211 wall cycles, MM1-v1 and MM1-v2, twins and rgm211)"
    if name in ("e211_controls_span", "e211_controls_and_hi"):
        c = B["E211"]["controls"]
        f = sorted([100 * (1 - math.exp(c["x01_ln"])), 100 * (1 - math.exp(c["x02_ln"]))])
        s = f"{f[0]:.0f}-{f[1]:.0f}"
        if name == "e211_controls_span":
            return [s], f"{V2J11} controls (x01, x02 in ln)"
        S = B["E211"]["sets"]
        hi = sorted([S["rgm211_12"]["v2"]["cyc_wall"]["rms_pct"], S["rgm211_12"]["v1"]["cyc_wall"]["rms_pct"]])
        return [s, f"{hi[0]:.0f}-{hi[1]:.0f}"], f"{V2J11}"
    if name == "armA_on_a3":
        A = B["E206A"]
        return [str(A["n_points"] - A["subsets"]["never_this_card"]["n"])], "numbers.json (119 - the 108 never on aifoundry3)"
    if name == "e209_rules":
        r = B["E209"]["rules"]
        want = {"T1m": (39, 41), "T1c": (39, 41), "T2m": (39, 41), "T2c": (39, 41), "T3m": (39, 41), "T3c": (39, 41), "E1": (45, 45), "E2m": (42, 45),
                "E2c": (41, 44), "E3": (43, 45), "E4m": (42, 45), "E4c": (41, 44), "K1": (44, 45)}
        bad = [k for k, (p, s) in want.items() if (r[k]["pass"], r[k]["scored"]) != (p, s) or r[k]["verdict"] != "PASS"]
        h = B["E209"]["h2h"]
        hw = {"H1": "MM1-v2 BETTER", "H2": "MM1-v2 BETTER", "H3": "MM1-v2 BETTER", "H4": "NOT DECIDED", "H5": "MM1-v2 BETTER", "H6": "MM1-v2 BETTER"}
        bad += [k for k, v in hw.items() if h[k]["verdict"] != v]
        if r["R0"]["verdict"] != "PASS":
            bad.append("R0")
        return ([] if not bad else ["MISMATCH " + ",".join(bad)]), "scored-e209.json rules and head_to_head"
    if name == "e212_sessions_at":
        # report-fix (Q215): the count dated at a named commit, so that the check reads the same at any later HEAD
        at = "724e8f39"
        ls = subprocess.run(["git", "-C", repo, "ls-tree", "--name-only", at, "docs/reports/data/"], capture_output=True, text=True, timeout=60).stdout.split()
        dirs = [x for x in ls if x.startswith("docs/reports/data/2026-11-17-e212-mmsweep2-")]
        added = []
        for d_ in dirs:
            lg = subprocess.run(["git", "-C", repo, "log", "--diff-filter=A", "--format=%ct %h", "--abbrev=8", at, "--", d_], capture_output=True, text=True,
                                timeout=60).stdout.split("\n")
            lg = [x.split() for x in lg if x.strip()]
            t_, h_ = min((int(x[0]), x[1]) for x in lg)
            added.append((t_, h_[:8], d_.rsplit("-", 2)[-2] + "-" + d_.rsplit("-", 1)[-1]))
        added.sort()
        words = {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
        return [words.get(len(dirs), str(len(dirs)))] + [h for _, h, _ in added], (f"git ls-tree {at} docs/reports/data/ (" +
                                                                                    ", ".join(f"{s} {h}" for _, h, s in added) + ")")
    if name in ("e207_b49_b52", "e207_b49_b52_span"):
        # report-fix (Q215): MM1-v1's blind J over idle given the measured seconds at E207's four kinds points, from the frozen scorer's output
        S = json.load(open(os.path.join(repo, S207J)))
        errs, ok = [], True
        for pid in ("b49", "b50", "b51", "b52"):
            p = S["points"][pid]
            errs.append(p["mm1_v1"]["given"]["J_over"] / p["measured"]["j_over"] - 1.0)
            ok &= all(S["rules"][r]["cells"][pid] == "PASS" for r in ("E1", "E2"))
        if not ok:
            return ["E1 or E2 NOT PASS at b49-b52"], S207J
        out = [f"{100 * e:+.1f}" for e in errs]
        if name == "e207_b49_b52":
            return out, f"{S207J} points b49-b52 (mm1_v1.given.J_over / measured.j_over - 1; E1 and E2 cells PASS)"
        return [f"{100 * min(errs):+.1f}", f"{100 * max(errs):+.1f}"], f"{S207J} points b49-b52"
    if name == "e207_int8_l3_span":
        C = json.load(open(os.path.join(repo, S207J)))["cases"]
        r = [100 * (C[f"{sh}|int8|0xffffffff"]["measured"]["cyc_wall"] / C[f"{sh}|fp32|0xffffffff"]["measured"]["cyc_wall"] - 1.0)
             for sh in ("gemmL1x3x2", "gemmL2x3x2", "gemmL3x2x2", "gemmL1x4x3")]
        return [f"{min(r):.1f}", f"{max(r):.1f}"], f"{S207J} cases ({', '.join(f'{x:.3f}' for x in r)}%)"
    if name == "e211_w2_caveat":
        w2 = json.load(open(os.path.join(repo, S211J)))["rules"]["W2"]
        good = w2.get("verdict") == "PASS" and w2.get("caveat") == "the controls did not pass: not a model test"
        return ([] if good else [f"MISMATCH {w2.get('verdict')} / {w2.get('caveat')}"]), f"{S211J} rules.W2"
    if name == "e42_margin":
        r = json.load(open(os.path.join(repo, N15J)))["C_margins_POST_HOC"]["rules"]["T2m"]
        band, v = r["band"], r["failing"]["gemmL6x6x6|int8|0xf000"]
        return [f"{100 * band:.0f}", f"{100 * (v - band):.2f}"], f"{N15J} (T2m: e42 {v:.5f} against the band {band})"
    if name == "seals":
        bad = [s for s, f in SEALS if s not in open(os.path.join(repo, f)).read()]
        return ([] if not bad else ["MISSING " + ",".join(bad)]), ", ".join(f for _, f in SEALS)
    if name == "kappa_span":
        k = N["switch"]["kappa"]
        d = max(abs(k[s]["ratio"] - 1) for s in k)
        return [f"{100 * d:.1f}"], "numbers.json switch.kappa (scores-e210-A.json)"
    if name == "kinds_gap":
        d = json.load(open(os.path.join(repo, N15J)))["B_readings_a_to_d"]["d_kinds"]
        e = [x for x in d if x["pair"] == "e35/e01"][0]
        gap = 100 * ((1 - e["measured"]) - (1 - e["MM1-v2"]))
        return [f"{gap:.0f}"], f"{N15J} (e35/e01: measured {e['measured']:.3f}, MM1-v2 {e['MM1-v2']:.3f})"
    if name == "armB_under3":
        det = B["E206B"]["under_3W_detail"]
        sub = {p: v for p, v in det.items() if v["class"] == "subset (mask < 32 shires)"}
        shires = sorted({bin(int(v["mask"], 16)).count("1") for v in sub.values()})
        Ws = [v["W"] for v in sub.values()]
        w1 = [v["w_lo_g"]["v1"] for v in sub.values()]
        one = [v["w_lo_g"]["v1"] for v in sub.values() if v["mask"] == "0x1"]
        out = [str(len(sub))] + [str(x) for x in shires] + [f"{min(Ws):.2f}", f"{max(Ws):.2f}", f"{min(w1):+.2f}", f"{max(w1):+.2f}",
                                                             str(sum(1 for x in w1 if x > 0)), f"{min(one):+.2f}", f"{max(one):+.2f}"]
        return out, "numbers.json blind.E206B.under_3W_detail"
    raise SystemExit("unknown function " + name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--numbers", required=True)
    ap.add_argument("--readme", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    N = json.load(open(a.numbers))
    readme = open(a.readme).read()
    cfg = {"S211": S211, "S211_note": "E211's registered scorer output, committed beside its data"}
    if not os.path.isfile(os.path.join(a.repo, S211)):
        raise SystemExit(f"{S211} is not committed at this tree")
    fl, lines_of, ln_no, prev_ws = [], [], 1, False
    for ch in readme:
        if ch.isspace():
            if not prev_ws:
                fl.append(" ")
                lines_of.append(ln_no)
            prev_ws = True
        else:
            fl.append(ch)
            lines_of.append(ln_no)
            prev_ws = False
        if ch == "\n":
            ln_no += 1
    flat = "".join(fl)
    L, nfail, spans = [], 0, []
    for i, c in enumerate(checks(cfg), 1):
        src = c["src"]
        kind = src[0]
        ok, found, where = True, "", ""
        printed = re.sub(r"\s+", " ", c["printed"])
        xref = printed.startswith("XREF:")
        if kind != "ROW" and not xref and printed not in flat:
            ok, found = False, "PHRASE NOT IN README; "
        try:
            if kind == "N":
                paths = src[1] if isinstance(src[1], list) else [src[1]]
                fmts = src[2] if isinstance(src[2], list) else [src[2]] * len(paths)
                if src[2] == "mixed_pct0_int":
                    fmts = ["pct0", "{:d}"]
                toks = src[3]
                vals = [fmt(get(N, p), f) for p, f in zip(paths, fmts)]
                if [norm_num(v) for v in vals] != [norm_num(t) for t in toks]:
                    ok = False
                found += ", ".join(vals)
                where = "numbers.json: " + ", ".join(paths)
                for t in toks:
                    if t.lstrip("+-") not in printed:
                        ok, found = False, found + f" [token {t} not in phrase]"
            elif kind == "T":
                txt = open(os.path.join(a.repo, src[1])).read()
                ntxt = re.sub(r"\s+", " ", txt)
                lits = src[2] if isinstance(src[2], list) else [src[2]]
                miss = [l_ for l_ in lits if l_ not in txt and re.sub(r"\s+", " ", l_) not in ntxt]
                if miss:
                    ok, found = False, found + "COMMITTED TEXT NOT FOUND: " + miss[0][:80]
                else:
                    found += "found"
                alln = norm_num(" ".join(lits))
                for t in src[3]:
                    if t.lstrip("+-") not in printed:
                        ok, found = False, found + f" [token {t} not in phrase]"
                    if norm_num(t).lstrip("-") not in alln:
                        ok, found = False, found + f" [token {t} not in the literal]"
                where = f"{src[1]} @ {git_last(a.repo, src[1])}"
            elif kind == "R":
                txt = open(os.path.join(a.repo, src[1])).read()
                if src[2] not in txt and src[2] not in re.sub(r"\s+", " ", txt):
                    ok, found = False, found + "COMMITTED TEXT NOT FOUND"
                v = src[4].format(float(src[3]))
                if v != src[5] or src[3] not in src[2]:
                    ok = False
                if src[5] not in printed:
                    ok, found = False, found + f" [token {src[5]} not in phrase]"
                found += f"{src[3]} -> {v}"
                where = f"{src[1]} @ {git_last(a.repo, src[1])}"
            elif kind == "CSV":
                rows = {r["id"]: r for r in csv.DictReader(open(os.path.join(a.repo, src[1]), newline=""))}
                r = rows[src[2]]
                vals = [fm.format(float(r[col]) * src[4]) for col, fm in zip(src[3], src[5])]
                if vals != src[6]:
                    ok = False
                found += ", ".join(vals)
                where = f"{src[1]} @ {git_last(a.repo, src[1])} (row {src[2]}: {', '.join(src[3])})"
            elif kind == "GT":
                tm = git_time(a.repo, src[1])
                if tm != src[2]:
                    ok = False
                found, where = found + str(tm), f"git log {src[1]} (the commit's own time, PST)"
            elif kind == "F":
                vals, where = run_f(src[1], a.repo, N)
                if vals != src[2]:
                    ok = False
                found += ", ".join(vals) if vals else "all present"
                for t in src[2]:
                    if t.lstrip("+-") not in printed:
                        ok, found = False, found + f" [token {t} not in phrase]"
            elif kind == "ROW":
                exp = row_expected(N, src[1], src[2])
                got, ln = readme_row(readme, src[1], src[2])
                com = committed_row(a.repo, src[1], src[2])
                qs = ("cyc_mean", "t", "jo_g3", "jo_f3", "jr_g")
                com_ok = True
                if com is not None:
                    m = (N["blind"]["E211"]["sets"]["rgm211_12" if src[1] == "E211r" else "twins_12"][src[2]] if src[1] in ("E211r", "E211t")
                         else N["blind"][src[1]]["models"][src[2]])
                    for q, cc in com.items():
                        if src[1] == "E207":
                            if cc == "-":
                                com_ok &= m.get(q) is None
                                continue
                            dr, db = len(cc[0].split(".")[1]), len(cc[1].split(".")[1])
                            com_ok &= f"{m[q]['rms_pct']:.{dr}f}" == cc[0] and f"{m[q]['bias_pct']:+.{db}f}" == cc[1]
                        else:
                            com_ok &= cc == exp[qs.index(q)]
                ok = got == exp and com_ok
                found = f"README {got} | numbers.json {exp}" + (f" | committed {com} ({'agree' if com_ok else 'DISAGREE'})" if com is not None
                                                                 else " | committed table: none (desk)")
                where = {"E206A": "numbers.json (make_figures.py on d7e4f35e, 50476f31, 2d1413f5, eb2f7ac2)",
                         "E206B": f"numbers.json and {NB} @ {git_last(a.repo, NB)} (time and rest cells; energy over idle at >= 3 W is desk)",
                         "E207": f"numbers.json and {V2S} @ {git_last(a.repo, V2S)}",
                         "E209": "numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)",
                         "E211r": f"numbers.json and {V2S11} @ {git_last(a.repo, V2S11)}", "E211t": f"numbers.json and {V2S11} @ {git_last(a.repo, V2S11)}"}[src[1]]
                printed = f"ROW {ROWNAME[src[1]]} / {modname(src[1], src[2])}"
                if ln:
                    for mm in re.finditer(re.escape(re.sub(r"\s+", " ", ln.strip())), flat):
                        spans.append((mm.start(), mm.end()))
        except Exception as e:  # noqa: BLE001
            ok, found = False, f"ERROR {type(e).__name__}: {e}"
        nfail += 0 if ok else 1
        if kind != "ROW" and not xref:
            for mm in re.finditer(re.escape(printed), flat):
                spans.append((mm.start(), mm.end()))
        L.append(f"{i:3d} {'PASS' if ok else 'FAIL'} | {printed[:110]} | {found[:260]} | {where}" + (f" | {c['note']}" if c["note"] else ""))
    toks = []
    for m in re.finditer(r"(?<![\w.`])[-+]?\d[\d,]*(?:\.\d+)?(?![\w`])", flat):
        if not any(s0 <= m.start() and m.end() <= e0 for s0, e0 in spans):
            toks.append((lines_of[m.start()], m.group(0)))
    nchk = len(L)
    L.append("")
    L.append(f"CHECKS: {nchk} run, {nfail} FAIL")
    L.append(f"NUMBERS OF README.md NO CHECK COVERS ({len(toks)}: dates, times, ids, section numbers, counts named in the text; for a reader to judge):")
    by = {}
    for ln_no, s in toks:
        by.setdefault(ln_no, []).append(s)
    for ln_no in sorted(by):
        L.append(f"  line {ln_no}: {' '.join(by[ln_no])}")
    L.append(f"interpreter: {sys.executable} {sys.version.split()[0]}")
    out = "\n".join(L) + "\n"
    print(out)
    if a.out:
        open(a.out, "w").write(out)
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
