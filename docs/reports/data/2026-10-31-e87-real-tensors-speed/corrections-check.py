#!/usr/bin/env python3
"""E87: the desk check behind 'Corrections after verification' (Sat 31 Oct 2026). Written after an independent
verifier's report. Every number is read from committed files; none is a registered rule or changes a verdict.
Standard library only.

    python3 corrections-check.py > corrections-check.txt

C1  What the clock rules test. A no-model baseline beside R1 and R3: each real tile gets E80's cell for its format's
    random reference (fp32 randn, fp16 randn, int8 full; the tie cells frozen in predictions.json `anchors.*.tie_*`).
    How many S3 intervals hold 1.000 ('real = random'). The like-with-like ratio errors of Q130(n)'s predictor and of
    'real = random' (labelled).
C2  The burst difference real minus same-session randn (S2) in units of its 1 sigma (E83 C6: a two-pass cell's random
    part is 5.3 MHz), and the passes.
C3  int8 full's sustained runs in E80, E83 and E87; the share at 800 MHz of every int8 sustained run; every sustained
    run's residual from E87's die line.
C4  The fp32 and fp16 ratios as a property of three tiles: t on 2 df and its one-sided p; round 2 alone.
C5  The round-to-round differences of the like-with-like ratios (checks.txt K1 prints half-spreads).
C6  The burst rounds: die start and clock, round 2 minus round 1, over the 15 kinds and over the eight power-limited ones.
C7  p800 and the start temperature: every burst's p800 and die start, and the share above zeros in each round.
C8  int8 l0_mlp_up's burst passes.
C9  The closing config reads: the session's own end query (s1/queries.jsonl) and final-config.txt.
"""
import datetime as dt
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/kspeed/e87/predictions.json")))
R80 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e80-kinds-speed/results.json")))
R83 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json")))
C = R["cells"]
RUNS = R["runs"]
FMTS = ("fp32", "fp16", "int8")
NAMES = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")
TILES = [f"{t}/{n}" for t in FMTS for n in NAMES]
REF = {"fp32": "fp32/randn", "fp16": "fp16/randn", "int8": "int8/full"}
CELL_SIGMA = 5.3  # MHz, a two-pass burst cell's random part (E83 corrections-check.txt C6)
PDT = dt.timezone(dt.timedelta(hours=-7), "PDT")


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def p_one_sided_df2(t):
    # Student's t with 2 df: F(t) = 1/2 + t / (2 sqrt(t^2 + 2)), exactly.
    return 0.5 - t / (2 * math.sqrt(t * t + 2))


def bursts(kind):
    return {m["rep"]: m for m in RUNS if m["block"] == "BURST" and m["kind"] == kind}


def ratio(tile_c, ref_c, zeros_c):
    return (tile_c - zeros_c) / (ref_c - zeros_c)


LWL = R["posthoc"]["like_with_like_ratios"]

print("C1  what the clock rules test: Q130(n)'s frozen points against a no-model baseline (each real tile = E80's cell")
print("    for its format's random reference, predictions.json anchors.*.tie_*)")
rows = []
for k in TILES:
    t = k.split("/")[0]
    an = P["anchors"][REF[t]]
    fz = P["tiles"][k]["frozen"]
    c = C[k]
    rows.append({"k": k, "b": c["burst_mhz"], "b_rf": c["burst_mhz_without"], "bf": fz["burst_mhz"],
                 "bb": an["tie_burst_mhz"], "s": c["sus_mhz"], "sf": fz["sus_mhz"], "sb": an["tie_sus_mhz"]})
    print(f"    {k:18s} burst {c['burst_mhz']:6.1f}  frozen {fz['burst_mhz']:6.1f}  baseline {an['tie_burst_mhz']:6.1f} "
          f"({an['tie_to']} {REF[t]})  |  sustained {c['sus_mhz']:6.1f}  frozen {fz['sus_mhz']:6.1f}  "
          f"baseline {an['tie_sus_mhz']:6.1f}")
for label, rr in (("the nine", rows), ("the six fp32/fp16 tiles", rows[:6])):
    print(f"    rms over {label}: burst frozen {rms([r['b'] - r['bf'] for r in rr]):.2f}, baseline "
          f"{rms([r['b'] - r['bb'] for r in rr]):.2f} MHz; sustained frozen {rms([r['s'] - r['sf'] for r in rr]):.2f}, "
          f"baseline {rms([r['s'] - r['sb'] for r in rr]):.2f} MHz")
print(f"    reset-free bursts (A1's view) over the nine: frozen {rms([r['b_rf'] - r['bf'] for r in rows]):.2f}, "
      f"baseline {rms([r['b_rf'] - r['bb'] for r in rows]):.2f} MHz")
s3_in = [k for k in TILES if P["tiles"][k]["like_with_like"]["S3_ratio_interval"][0] <= 1.0
         <= P["tiles"][k]["like_with_like"]["S3_ratio_interval"][1]]
fr_in = [k for k in TILES if P["tiles"][k]["like_with_like"]["frozen_ratio_interval"][0] <= 1.0
         <= P["tiles"][k]["like_with_like"]["frozen_ratio_interval"][1]]
print(f"    'real = random' (ratio 1.000) lies inside the S3 interval of {len(s3_in)} of 9 tiles (S3's bar is 7): "
      f"all but {sorted(set(TILES) - set(s3_in))}")
print(f"    ... and inside the frozen ratio interval of {len(fr_in)} of 9 (all but {sorted(set(TILES) - set(fr_in))})")
print("    S4 with ratio 1.000 everywhere: fp32 1.000 < 1 False, fp16 1.000 < 1 False, int8 1.000 < 0.9 False; measured "
      + ", ".join(f"{r[0]} {r[1]} < {r[2]} {r[3]}" for r in R["rules"]["E87-S4"]["rows"]))
print("    like-with-like ratio errors, measured minus predicted (labelled, post hoc):")
for t in FMTS:
    meas = [LWL[f"{t}/{n}"] for n in NAMES]
    pred = [P["tiles"][f"{t}/{n}"]["like_with_like"]["ratio_to_ref_measured"] for n in NAMES]
    em = [m - p for m, p in zip(meas, pred)]
    en = [m - 1.0 for m in meas]
    order_m = [n for _, n in sorted(zip(meas, NAMES))]
    order_p = [n for _, n in sorted(zip(pred, NAMES))]
    print(f"      {t}: Q130(n) {', '.join(f'{e:+.4f}' for e in em)} (rms {rms(em):.4f}); 'real = random' "
          f"{', '.join(f'{e:+.4f}' for e in en)} (rms {rms(en):.4f}); cheapest to dearest measured {order_m}, "
          f"predicted {order_p}")
print()

print("C2  the burst difference, real tiles' mean minus same-session randn (E87-S2)")
sig = CELL_SIGMA * math.sqrt(1 / 3 + 1)
print(f"    1 sigma of (mean of three two-pass cells) - (one two-pass cell) = {CELL_SIGMA} x sqrt(1/3 + 1) = {sig:.2f} MHz")
for t in ("fp32", "fp16"):
    real = [C[f"{t}/{n}"]["burst_mhz"] for n in NAMES]
    ref = C[REF[t]]
    d = st.mean(real) - ref["burst_mhz"]
    rp = sorted(x for n in NAMES for x in C[f"{t}/{n}"]["burst_mhz_runs"])
    above = sum(1 for x in rp if x > max(ref["burst_mhz_runs"]))
    print(f"    {t}: real mean {st.mean(real):.2f} - randn {ref['burst_mhz']} = {d:+.2f} MHz ({100 * d / ref['burst_mhz']:+.2f}%), "
          f"{d / sig:+.2f} sigma; real passes {rp}, randn passes {ref['burst_mhz_runs']}; "
          f"{above} of 6 real passes above both randn passes")
for row in R["rules"]["E87-S2"]["rows"]:
    print(f"    {row[0]} sustained (labelled): real mean {row[4]['beside_sus_real_mean']} - randn {row[4]['beside_sus_randn']} "
          f"= {row[4]['beside_sus_diff']:+} MHz")
print("    registered expectation (pre-registration README, E87-S2): +1 MHz (fp32) and +5 MHz (fp16) on E83's relation")
print()

print("C3  int8 at the 65 C trip")
for name, RR in (("E80", R80), ("E83", R83), ("E87", R)):
    c = RR["cells"]["int8/full"]
    print(f"    {name} int8 full sustained {c['sus_mhz']} MHz, runs {c['sus_mhz_runs']}, limits {c['sus_limit_runs']}, "
          f"share at 800 {[s['800'] for s in c['sus_last']]}, board W {c['sus_w_runs']}, die {c['sus_die_runs']}")
dl = R["posthoc"]["die_line_e87"]
print(f"    E87 die line: die = {dl['a_c']} + {dl['k_c_per_w']} x board W (n {dl['n']}, rms {dl['rms_c']} C); "
      f"each sustained run's residual (die - line), its share at 800 MHz and its cell's limit label:")
res = []
for m in sorted((m for m in RUNS if m["block"] == "SUS"), key=lambda m: m["run"]):
    r = m["sus_die_mean"] - (dl["a_c"] + dl["k_c_per_w"] * m["sus_w_mean"])
    res.append(r)
    print(f"      {m['run']:32s} {m['sus_w_mean']:6.2f} W  {m['sus_die_mean']:5.1f} C  residual {r:+.2f} C  "
          f"share800 {m['sus_last']['800']:.3f}  {m['sus_mhz_mean']} MHz")
print(f"    residual rms over the 17 runs {rms(res):.3f} C (posthoc.die_line_e87 rms_c {dl['rms_c']})")
print(f"    switching term c (W, E64's basis): real {[C[f'int8/{n}']['c_w'] for n in NAMES]}, full {C['int8/full']['c_w']}")
i8 = [C[f"int8/{n}"]["sus_mhz"] for n in NAMES]
print(f"    real mean {st.mean(i8):.1f} - full {C['int8/full']['sus_mhz']} = {st.mean(i8) - C['int8/full']['sus_mhz']:+.1f} MHz "
      f"(checks.txt K4); one sustained run's 1 sigma on and near the knee 15.6 / 5.6 MHz (E83 C3)")
print()

print("C4  the fp32 and fp16 ratios across the three tiles")
for t in ("fp32", "fp16", "int8"):
    cell = [LWL[f"{t}/{n}"] for n in NAMES]
    mean, sd = st.mean(cell), st.stdev(cell)
    tt = (1 - mean) / (sd / math.sqrt(3))
    z, rf, rr = bursts(f"{t}/zeros"), bursts(REF[t]), None
    r2 = [ratio(bursts(f"{t}/{n}")[2]["c_w"], rf[2]["c_w"], z[2]["c_w"]) for n in NAMES]
    starts2 = [bursts(f"{t}/{n}")[2]["die_start"] for n in NAMES] + [rf[2]["die_start"], z[2]["die_start"]]
    print(f"    {t}: mean {mean:.4f}, between-tile sd {sd:.4f}, t against 1.000 = {tt:.2f} on 2 df, one-sided p "
          f"{p_one_sided_df2(tt):.3f}; round 2 alone {[round(x, 4) for x in r2]} (die starts {starts2})")
print()

print("C5  the like-with-like ratios round by round: |round 1 - round 2| (checks.txt K1 prints half of it)")
for t in FMTS:
    z, rf = bursts(f"{t}/zeros"), bursts(REF[t])
    out = []
    for n in NAMES:
        b = bursts(f"{t}/{n}")
        r1 = ratio(b[1]["c_w"], rf[1]["c_w"], z[1]["c_w"])
        r2 = ratio(b[2]["c_w"], rf[2]["c_w"], z[2]["c_w"])
        out.append(f"{n} {r1:.4f} / {r2:.4f} difference {abs(r1 - r2):.4f} half-spread {abs(r1 - r2) / 2:.4f}")
    print(f"    {t}: " + "; ".join(out))
print()

print("C6  the burst rounds, round 2 minus round 1")
kinds = sorted(C.keys())
power = [k for k in kinds if C[k]["burst_limit"] == "power"]
ds_all, ds_pow, dm_pow = [], [], []
for k in kinds:
    b = bursts(k)
    dd = b[2]["die_start"] - b[1]["die_start"]
    ds_all.append(dd)
    if k in power:
        ds_pow.append(dd)
        dm_pow.append(b[2]["burst_mhz"] - b[1]["burst_mhz"])
    print(f"    {k:18s} die start {b[1]['die_start']} -> {b[2]['die_start']} ({dd:+d} C)  burst {b[1]['burst_mhz']} -> "
          f"{b[2]['burst_mhz']}  limit {C[k]['burst_limit']}")
print(f"    die start: mean {st.mean(ds_all):+.2f} C over the {len(ds_all)} kinds; {st.mean(ds_pow):+.2f} C over the "
      f"{len(power)} power-limited kinds ({ds_pow})")
print(f"    burst clock on the {len(power)} power-limited kinds: mean {st.mean(dm_pow):+.2f} MHz, sd {st.stdev(dm_pow):.2f}")
print()

print("C7  p800 (the first second at 800 MHz, board W) and the start temperature")
for t in FMTS:
    z, rf = bursts(f"{t}/zeros"), bursts(REF[t])
    for n in NAMES:
        b = bursts(f"{t}/{n}")
        parts = []
        for rep in (1, 2):
            sh = (b[rep]["p800_w"] - z[rep]["p800_w"]) / (rf[rep]["p800_w"] - z[rep]["p800_w"])
            parts.append(f"round {rep}: {b[rep]['p800_w']} W from {b[rep]['die_start']} C, {REF[t]} {rf[rep]['p800_w']} W "
                         f"from {rf[rep]['die_start']} C, zeros {z[rep]['p800_w']} W from {z[rep]['die_start']} C, "
                         f"share above zeros {sh:.3f}")
        print(f"    {t}/{n}: cell p800 {C[f'{t}/{n}']['burst_p800_w']} W ({REF[t]} {C[REF[t]]['burst_p800_w']} W); "
              + "; ".join(parts))
print()

print("C8  int8 l0_mlp_up's burst passes")
c = C["int8/l0_mlp_up"]
print(f"    burst {c['burst_mhz']} MHz, passes {c['burst_mhz_runs']}, without the reset samples {c['burst_mhz_without_runs']}; "
      f"rate {c['burst_rate']} TOPS, passes {c['burst_rate_runs']}")
print()

print("C9  the closing config reads")
for line in open(os.path.join(HERE, "s1", "queries.jsonl")):
    q = json.loads(line)
    when = dt.datetime.fromtimestamp(q["t_ms"] / 1000, PDT).strftime("%H:%M:%S.%f")[:-3]
    print(f"    s1/queries.jsonl {q['tag']:6s} {when} PDT config_rc {q['config_rc']} {json.dumps(q['config'])}")
for line in open(os.path.join(HERE, "final-config.txt")):
    if line.startswith("==") or line.startswith("{") or line.startswith("rc "):
        print(f"    final-config.txt {line.rstrip()}")
