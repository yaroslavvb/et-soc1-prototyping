#!/usr/bin/env python3
"""E116 corrections after verification: the desk check (Sun 1 Nov 2026, written after the verifier's report).

Prints every number the README's "Corrections after verification" quotes, from committed files only: this
directory's frozen reduction and scores (e116.json, runs.csv, scored.json, scored-e88rules.json, posthoc.json),
the raw passes' config reads and run logs, tools/claims-v3/e116/predictions-e116.json, and the scored files of
E88, E92, E106 and E108. Standard library only. Everything here is post hoc: it changes no registered number and
no verdict.

    python3 docs/reports/data/2026-11-01-e116-split-replicate/corrections-check.py \
        > docs/reports/data/2026-11-01-e116-split-replicate/corrections-check.txt
"""
import csv
import hashlib
import json
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")
RAW = os.path.join(HERE, "aifoundry3", "rpath")
PASSES = ["11610", "11611", "11612", "11613", "11614"]
PARTS = ("i", "iii", "ii")


def load(*p):
    with open(os.path.join(*p)) as f:
        return json.load(f)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def mci(d, nd=3):
    return f"{d['mean']:.{nd}f} +- {d['ci95']:.{nd}f} (n {d['n']})"


s = load(HERE, "scored.json")
r = load(HERE, "scored-e88rules.json")
e = load(HERE, "e116.json")
ph = load(HERE, "posthoc.json")
pr = load(REPO, "tools", "claims-v3", "e116", "predictions-e116.json")
scale = pr["card_scale_e82"]["value"]

print("E116 corrections-check: post hoc, labelled; no registered number and no verdict changes")
print()
print("## 0. The frozen outputs this reads (sha256; the corrections change none of them)")
for fn in ("e116.json", "runs.csv", "scored.json", "scored-e88rules.json", "posthoc.json", "results.md",
           "results-e88rules.md", "reduce.txt"):
    print(f"  {sha(os.path.join(HERE, fn))}  {fn}")
print(f"  {sha(os.path.join(REPO, 'tools', 'claims-v3', 'e116', 'README.md'))}  tools/claims-v3/e116/README.md "
      "(the registration, left as frozen)")

# ---------------------------------------------------------------------------------------------- C1
print()
print("## C1. E88's own model (its frozen P bands) on aifoundry3, unscaled: band widths and what a card scale moves")
print("   scored-e88rules.json > primary.contrasts.*.predicted (mu, tol = the band's half-width) and .D;")
print("   predictions-e116.json > card_scale_e82 (E82's scale, aifoundry3 over card 1, per format)")
print(f"   E82's scale: {scale}")
rows = []
for k, v in r["primary"]["contrasts"].items():
    p = v["predicted"]
    fmt = v["a"].split(".")[0]
    D = v["D"]["mean"]
    verdict = r["primary"]["rules"]["P-" + k]["verdict"]
    shift = abs(p["mu"]) * (scale[fmt] - 1.0)
    rows.append((k, fmt, D, p["mu"], p["tol"], p["lo"], p["hi"], verdict, D - p["mu"], shift))
print(f"   {'contrast':8s} {'fmt':4s} {'measured':>8s} {'pred':>7s} {'+-tol':>6s} {'band':>17s} {'P':4s} "
      f"{'meas-pred':>9s} {'pct':>7s} {'scale moves':>11s} {'/tol':>5s}")
for k, fmt, D, mu, tol, lo, hi, vd, miss, shift in rows:
    pct = f"{100 * miss / mu:+.0f}%" if abs(mu) >= 1.0 else ""
    print(f"   {k:8s} {fmt:4s} {D:8.3f} {mu:7.3f} {tol:6.3f} {lo:8.3f}..{hi:7.3f} {vd:4s} {miss:+9.3f} {pct:>7s} "
          f"{shift:11.3f} {shift / tol:5.2f}")
tols = [x[4] for x in rows]
tols_f = [x[4] for x in rows if x[1] in ("fp32", "fp16")]
big = max(rows, key=lambda x: x[9])
rel = max(rows, key=lambda x: x[9] / x[4])
print(f"   P PASS {sum(1 for x in rows if x[7] == 'PASS')} of {len(rows)}; FAIL: "
      f"{', '.join(x[0] for x in rows if x[7] != 'PASS')}")
print(f"   band half-widths, all 19: {min(tols):.3f} to {max(tols):.3f} W; fp32 and fp16 only: "
      f"{min(tols_f):.3f} to {max(tols_f):.3f} W")
print(f"   the most E82's scale moves any prediction: {big[9]:.3f} W ({big[0]}); "
      f"the largest share of a half-width: {rel[9] / rel[4]:.2f} ({rel[0]})")
print("   misses inside a PASS band of 0.85 W or more: "
      + "; ".join(f"{x[0]} {x[2]:.2f} against {x[3]:.2f} ({x[8]:+.2f} W)" for x in rows
                  if x[7] == "PASS" and abs(x[8]) >= 0.85))

# ---------------------------------------------------------------------------------------------- C2
print()
print("## C2. The held fp32 sign (s_abs - c_abs, E88's M32s) and its walking half (s_walk - s_abs, R32s): every reading")
e88 = load(DATA, "2026-10-31-e88-result-path", "scored.json")["primary"]["contrasts"]
e92 = load(DATA, "2026-11-01-e92-sign-split", "scored.json")["contrasts"]
e106 = load(DATA, "2026-11-01-e106-held-signs", "scored.json")["primary"]["contrasts"]
e108 = load(DATA, "2026-11-01-e108-sign-located", "scored.json")["primary"]["quantities"]
held = [
    ("E88, aifoundry1 card 1", e88["M32s"]["D"], "2026-10-31-e88-result-path/scored.json > primary.contrasts.M32s.D"),
    ("E106, aifoundry1 card 1", e106["fp32.held"], "2026-11-01-e106-held-signs/scored.json > primary.contrasts.fp32.held"),
    ("E108, aifoundry1 card 1", e108["fp32.held_abs"],
     "2026-11-01-e108-sign-located/scored.json > primary.quantities.fp32.held_abs"),
    ("E92, aifoundry3", e92["fp32.s_abs-c_abs"]["D_w"], "2026-11-01-e92-sign-split/scored.json > contrasts.fp32.s_abs-c_abs.D_w"),
    ("E116, aifoundry3", r["primary"]["contrasts"]["M32s"]["D"], "scored-e88rules.json > primary.contrasts.M32s.D"),
]
for name, d, src in held:
    print(f"   held  {name:24s} {mci(d)}   [{src}]")
ms = [d["mean"] for _, d, _ in held]
print(f"   {len(held)} readings on two cards, {min(ms):.3f} to {max(ms):.3f} W (spread {max(ms) - min(ms):.3f} W)")
walk = [
    ("E88, aifoundry1 card 1", e88["R32s"]["D"], "2026-10-31-e88-result-path/scored.json > primary.contrasts.R32s.D"),
    ("E108, aifoundry1 card 1", e108["fp32.rest"], "2026-11-01-e108-sign-located/scored.json > primary.quantities.fp32.rest"),
    ("E116, aifoundry3", r["primary"]["contrasts"]["R32s"]["D"], "scored-e88rules.json > primary.contrasts.R32s.D"),
]
for name, d, src in walk:
    print(f"   walk  {name:24s} {mci(d)}   [{src}]")
w116 = walk[2][1]["mean"]
print(f"   E116's walking half over card 1's: {w116 / walk[0][1]['mean']:.3f} (E88), {w116 / walk[1][1]['mean']:.3f} (E108)")

# ---------------------------------------------------------------------------------------------- C4
print()
print("## C4. Rail and board shares (posthoc.json; points = share x 100)")
worst = {}
for card, rk, bk in (("aifoundry3 (E116)", "rail_e116", "board_e116"), ("card 1 (E88)", "rail_e88", "board_e88")):
    for fmt in ("fp32", "fp16", "int8"):
        rr, bb = ph[rk][fmt], ph[bk][fmt]
        d = [100 * (rr["share_" + q]["mean"] - bb["share_" + q]["mean"]) for q in PARTS]
        worst[card] = max(worst.get(card, 0.0), max(abs(x) for x in d))
        print(f"   {card:18s} {fmt}: rail {[rr['share_' + q]['mean'] for q in PARTS]} board "
              f"{[round(bb['share_' + q]['mean'], 4) for q in PARTS]}  rail - board {[round(x, 2) for x in d]}")
for card, w in worst.items():
    print(f"   rail against board, {card}: up to {w:.2f} points")
w3 = 0.0
for fmt in ("fp32", "fp16", "int8"):
    d = [100 * (ph["rail_e116"][fmt]["share_" + q]["mean"] - ph["rail_e88"][fmt]["share_" + q]["mean"]) for q in PARTS]
    w3 = max(w3, max(abs(x) for x in d))
    print(f"   rail, aifoundry3 - card 1, {fmt}: {[round(x, 2) for x in d]}")
print(f"   aifoundry3's rail shares against card 1's rail shares: up to {w3:.2f} points")

# ---------------------------------------------------------------------------------------------- C5
print()
print("## C5. Board watts, E116 over E88 (posthoc.json > ratio_e116_over_e88_board), against E82's scale")
allp = []
for fmt in ("fp32", "fp16", "int8"):
    q = ph["ratio_e116_over_e88_board"][fmt]
    allp += [(q[x], f"{fmt} ({x})") for x in PARTS]
    print(f"   {fmt}: parts (i) {q['i']:.4f}  (iii) {q['iii']:.4f}  (ii) {q['ii']:.4f};  r_walk total {q['total']:.4f};  "
          f"random anchor {q['anchor']:.4f};  E82's scale {scale[fmt]:.4f};  total over scale, less 1: "
          f"{(q['total'] - 1) / (scale[fmt] - 1):.2f}x")
lo, hi = min(allp), max(allp)
print(f"   the nine parts run from {lo[0]:.3f} ({lo[1]}) to {hi[0]:.3f} ({hi[1]})")

# ---------------------------------------------------------------------------------------------- C6
print()
print("## C6. Passes behind each format's split (scored.json > power)")
print(f"   kept passes: {s['power']['kept_passes']} {s['power']['passes']}; registered minimum "
      f"{pr['primary']['min_passes']} (the scorer counts kept passes)")
for fmt in ("fp32", "fp16", "int8"):
    sh = s["power"]["splits"][fmt]["shares"]
    print(f"   {fmt}: shares n = {[sh[k]['n'] for k in sh]}; S {s['power']['E116-S'][fmt]['verdict']}, "
          f"W {s['power']['E116-W'][fmt]['verdict']}")
for p in s["power"]["passes"]:
    have = sorted(k for k in e["per_pass"][p] if k.startswith("int8."))
    miss = [k for k in ("int8.c_cancel", "int8.r_cancel", "int8.r_walk") if k not in have]
    print(f"   pass {p}: int8 items {have}" + (f"; missing {miss}" if miss else ""))

# ---------------------------------------------------------------------------------------------- C7
print()
print("## C7. Pass 11613's int8 zero line (e116.json > anchors, gates; runs.csv; p11613/run.log)")
g = e["gates"]
a13 = e["anchors"]["11613"]["int8.zeros"]
a10 = e["anchors"]["11610"]["int8.zeros"]
print(f"   gates: zero_mid_departure_w {g['zero_mid_departure_w']} (needs three runs), zero_range_w {g['zero_range_w']}")
print(f"   11610 int8.zeros: n {a10['n']}, mid departure {a10['mid_departure_w']:+.3f} W -> set aside")
print(f"   11613 int8.zeros: n {a13['n']}, p80 {a13['p80']}, range {a13['range_w']:.3f} W, "
      f"mid departure {'not computed' if 'mid_departure_w' not in a13 else a13['mid_departure_w']}")
with open(os.path.join(RAW, "p11613", "run.log")) as f:
    for line in f:
        if "int8.zeros" in line and "skipped" in line:
            print("   run.log: " + line.strip().split("] ", 1)[-1])
with open(os.path.join(HERE, "runs.csv")) as f:
    rows13 = [x for x in csv.DictReader(f) if x["pass"] == "11613" and x["type"] == "int8"]
zpos = sorted(int(x["pos"]) for x in rows13 if x["item"] == "int8.zeros")
print(f"   11613 int8.zeros kept at positions {zpos}; int8 items before the first of them (the line is held flat "
      f"there): {sorted((int(x['pos']), x['item']) for x in rows13 if int(x['pos']) < zpos[0])}")
for item in ("int8.c_cancel", "int8.ones"):
    print(f"   {item} by pass: " + ", ".join(f"{p} {e['per_pass'][p][item]['D']:.3f}" for p in s["power"]["passes"]))
sh8 = s["power"]["splits"]["int8"]["shares"]
ref = {x["part"]: x["e88"] for x in s["power"]["E116-S"]["int8"]["parts"]}
band = s["power"]["E116-S"]["int8"]["parts"][0]["band"]
print(f"   int8 shares per pass (11611, 11612, 11613): " + "; ".join(f"{k} {sh8[k]['values']}" for k in sh8))
for k in sh8:
    v = sh8[k]["values"]
    m2 = sum(v[:2]) / 2.0
    print(f"   {k}: with 11613 {sh8[k]['mean']:.4f} (diff {sh8[k]['mean'] - ref[k]:+.4f}); without it {m2:.4f} "
          f"(diff {m2 - ref[k]:+.4f}); band +-{band}: {'inside' if abs(m2 - ref[k]) <= band else 'OUTSIDE'} without it")

# ---------------------------------------------------------------------------------------------- C8
print()
print("## C8. Wording checks")
n = 199874
t = {x["tile"]: x for x in s["E116-R0"]["tiles"]}
want = struct.pack(">f", float(n) * 2.0 ** 100).hex()
for tile in ("fp32.c_abs", "fp32.r_abs", "fp32.s_abs"):
    print(f"   {tile}: C[0][0] {t[tile]['c00_card']}, distinct C {t[tile]['distinct_c']}; n x 2^100 as fp32 = {want}: "
          f"{'equal' if t[tile]['c00_card'] == want else 'DIFFERENT'}")
h1 = r["primary"]["rules"]["H1-fp32"]
print(f"   H1-fp32 (ones - c_abs): {h1['stat']['mean']:.3f} +- {h1['stat']['ci95']:.3f} W, interval "
      f"{h1['stat']['lo']:.3f} to {h1['stat']['hi']:.3f}; rule: at most {h1['thr']} W, {h1['verdict']}")
for fmt in ("fp32", "fp16", "int8"):
    print(f"   E116-S {fmt} share moves: " + ", ".join(f"{x['diff']:+.4f} +- {x['ci95']:.4f}"
                                                   for x in s["power"]["E116-S"][fmt]["parts"]))
mv = []
for p in PASSES:
    for end in ("config_start", "config_end"):
        c = load(RAW, "p" + p, end + ".json")
        mv.append((p, end, c["minion_mv"], c["tdp_w"], c["temp_threshold_c"], c["minion_mhz"]))
print("   pass config reads (minion_mv): " + "; ".join(f"{p} {end.split('_')[1]} {m}" for p, end, m, *_ in mv))
print(f"   pass ends at 522 mV: {sum(1 for x in mv if x[1] == 'config_end' and x[2] == 522)} of {len(PASSES)}; "
      f"every read TDP/threshold/clock {sorted({(x[3], x[4], x[5]) for x in mv})}")
for end in ("config-session-start", "config-session-end"):
    c = load(HERE, "logs", end + ".json")
    print(f"   {end}: {c['minion_mv']} mV, TDP {c['tdp_w']} W, {c['temp_threshold_c']} C, {c['minion_mhz']} MHz")
for x in s["power"]["E116-T"]["items"]:
    print(f"   E116-T {x['item']}: {x['D']:.3f} against E78 {x['e78']:.4f}: {x['D'] - x['e78']:+.3f} W "
          f"({100 * (x['D'] - x['e78']) / x['e78']:+.1f}%), band {x['band']:.3f}, {x['verdict']}")
