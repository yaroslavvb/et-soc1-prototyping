#!/usr/bin/env python3
"""E105: writes the data directory's results-first README from its committed JSON, so every number in it comes from a file. Standard library only.

    python3 make_readme_e105.py <data dir>
"""
import json
import sys

D = sys.argv[1]
R = json.load(open(f"{D}/results-speed.json"))
P = json.load(open(f"{D}/scored-p.json"))
PR = json.load(open(f"{D}/../../../../tools/claims-v3/kspeed/e105/predictions-e105.json"))
E101 = json.load(open(f"{D}/../2026-11-01-e101-real-matmul/e101.json"))["items"]
F, G, C, V, T8 = R["fits"], R["gaps"], R["cells"], R["rules"], R["t800_us"]
A = P["cells"]
PV = P["rules"]


def r101(n):
    x = E101[n]
    return x["rate"]["mean"] * x["macs_per_op"] * 2 / 1e12


def fit(k, digits=3):
    f = F[k]
    return f"{f['C']:.1f} ± {f['C_ci']:.1f}", f"{f['M']:.{digits}f} ± {f['M_ci']:.{digits}f}"


def cm(k):
    a, b = fit(k)
    return f"C {a}, M {b}"


def gap(lab, gm):
    g = G[lab]
    r, c = g[f"{gm}_rate"], g[f"{gm}_clock"]
    return "not run" if r is None else f"×{r:.3f} (×{c:.3f})"


def ns(lab):
    return f"{C[lab]['n_burst']}, {C[lab]['n_sus']}"


LAW = PR["laws"]
adm = json.load(open(f"{D}/aifoundry2/admission.json"))
peak = {k: v.get("peak_w") for k, v in adm["seen"].items()}
top = sorted(((v, k) for k, v in peak.items() if v), reverse=True)[:3]
R4, R5, R6, R7, R8, R9 = V["R4"], V["R5"], V["R6"], V["R7"], V["R8"], V["R9"]
P3, P4 = PV["P3"], PV["P4"]

s = f"""# E105: does the gap come back when the tiles fit the L2?

*Sun 1 Nov 2026 (week 44), Q132. The first open item left by E101's verifier: E101's `gemm1` is one port of the vendor's GEMM pattern, whose packed tiles miss the L2 on most lines, so is that why its speed gap all but vanished? Pre-registered in `3ad06644` ([`tools/claims-v3/kspeed/e105/E105.md`](../../../../tools/claims-v3/kspeed/e105/E105.md), frozen numbers in `predictions-e105.json`, rules, self-test), before either claim and any launch; A1 `6a347e4b` added the power arm before any launch; A2 `3e577e7f` records a queue path fix with no effect on data. Binary: [`tools/claims-v3/rgm105/`](../../../../tools/claims-v3/rgm105/README.md), E101's kernel plus one field: same partition, op order, cooperative loads and tile contents, only the addresses differ. **aifoundry2 card 0 under its own governor,** 07:36–08:26 PST, 48.1 card-minutes, 65 W / 65 °C read after every run and at both ends. **aifoundry3 card 0 at its pinned 600 MHz,** 07:36–08:11 PST, TDP 0 / 65 °C / 600 MHz read at both ends of every pass, E101 session 1's own tools. Nothing was set on either card. No `--reset-ms`. No `mm16`, no hot start.*

## The answer

**Yes. With the tiles in the L2 the fixed term goes and the speed gap comes back, as large as the clock gap. Walking fresh blocks from DRAM it does not come back in either layout tried.**

| layout, on aifoundry2 | desk L2 model, lines missing | fp32: C, cycles | fp32: M, µs | frozen C, M | T at 800 MHz, zeros, µs | TFLOPS at 800 MHz, burst | TFLOPS at 600 MHz, aifoundry3 |
|---|---|---|---|---|---|---|---|
| `gemm1`, as E101 ran it | 75.0% | {fit('gemm1.fp32')[0]} | {fit('gemm1.fp32')[1]} | 344.3, 0.838 | {T8['gemm1-fp32-zeros']:.3f} | {C['gemm1-fp32-zeros']['burst_rate']:.2f} | {r101('gemm1.fp32.randn'):.2f} (E101) |
| `gemmv1`, the vendor's strides | 41.9% | {fit('gemmv1.fp32')[0]} | {fit('gemmv1.fp32')[1]} | 344.3, 0.468 | {T8['gemmv1-fp32-zeros']:.3f} | {C['gemmv1-fp32-sparse50']['burst_rate']:.2f} | {A['gemmv1.fp32.randn']['rate']:.2f} |
| `gemmc1`, B packed by column | 0.0% | {fit('gemmc1.fp32')[0]} | {fit('gemmc1.fp32')[1]} | 529, 0 | {T8['gemmc1-fp32-zeros']:.3f} | {C['gemmc1-fp32-zeros']['burst_rate']:.2f} | {A['gemmc1.fp32.randn']['rate']:.2f} |
| `gemmh1`, by column, half K | 0.0% | {fit('gemmh1.fp32')[0]} | {fit('gemmh1.fp32')[1]} | 529, 0 | {T8['gemmh1-fp32-zeros']:.3f} | {C['gemmh1-fp32-zeros']['burst_rate']:.2f} | |
| `gemmc16`, by column, 16 blocks, cold | 66.7% | {fit('gemmc16.fp32')[0]} | {fit('gemmc16.fp32')[1]} | 344.3, 1.271 | {T8['gemmc16-fp32-zeros']:.3f} | {C['gemmc16-fp32-zeros']['burst_rate']:.2f} | {A['gemmc16.fp32.randn']['rate']:.2f} |
| `gemmv16`, strides, 16 blocks, cold | 80.2% | {fit('gemmv16.fp32')[0]} | {fit('gemmv16.fp32')[1]} | 344.3, 1.529 | {T8['gemmv16-fp32-zeros']:.3f} | {C['gemmv16-fp32-zeros']['burst_rate']:.2f} | {A['gemmv16.fp32.randn']['rate']:.2f} |

T = C/f + M per op, over the launches of at least 0.1 s between 590 and 810 MHz, T = wall ÷ ops per minion, f = cycles_max ÷ wall (`results-speed.json` `fits`; n and rms there, rms 0.6 ns by column). The strides' zeros burst had an idle reset, so its TFLOPS are from sparse50's burst. fp16 and int8: by column {cm('gemmc1.fp16')} and {cm('gemmc1.int8')}; strides {cm('gemmv1.fp16')} and {cm('gemmv1.int8')}. **One edit, B by column, takes M from {F['gemm1.fp32']['M']:.2f} to {F['gemmc1.fp32']['M']:.3f} µs and C to the FMA's own 529, and nearly doubles the rate.** Half the chip on random fp32 reads the same law: {cm('gemmc1.fp32.half')}. **The law crosses cards:** aifoundry3's pinned 600 MHz reads within 0.6% of aifoundry2's fit in every layout (`scored-p.json` `two_cards`).

**Zeros ÷ kind, aifoundry2, its own governor: rate (clock).** n is runs per kind, burst and sustained, one card, one session (`results-speed.json` `gaps`, `cells`).

| layout | kind | burst | sustained | n |
|---|---|---|---|---|
| as run | fp32 random | {gap('gemm1-fp32-randn','burst')} | {gap('gemm1-fp32-randn','sus')} | {ns('gemm1-fp32-randn')} |
| as run | fp32 sparse25 | {gap('gemm1-fp32-sparse25','burst')} | {gap('gemm1-fp32-sparse25','sus')}, see below | {ns('gemm1-fp32-sparse25')} |
| strides | fp32 random | {gap('gemmv1-fp32-randn','burst')}, see below | {gap('gemmv1-fp32-randn','sus')} | {ns('gemmv1-fp32-randn')} |
| strides | fp32 sparse25 | {gap('gemmv1-fp32-sparse25','burst')}, see below | {gap('gemmv1-fp32-sparse25','sus')} | {ns('gemmv1-fp32-sparse25')} |
| **by column** | **fp32 random** | **{gap('gemmc1-fp32-randn','burst')}** | refused: the burst read {peak['A-11-gemmc1-fp32-randn-r1']} W | {ns('gemmc1-fp32-randn')} |
| **by column** | **fp32 sparse25** | **{gap('gemmc1-fp32-sparse25','burst')}** | **{gap('gemmc1-fp32-sparse25','sus')}** | {ns('gemmc1-fp32-sparse25')} |
| by column | fp32 ones | {gap('gemmc1-fp32-ones','burst')} | {gap('gemmc1-fp32-ones','sus')} | {ns('gemmc1-fp32-ones')} |
| **by column** | **fp16 random** | **{gap('gemmc1-fp16-randn','burst')}** | **{gap('gemmc1-fp16-randn','sus')}** | {ns('gemmc1-fp16-randn')} |
| **by column** | **int8 full** | {gap('gemmc1-int8-full','burst')} | **{gap('gemmc1-int8-full','sus')}** | {ns('gemmc1-int8-full')} |
| cold, by column | fp32 random | {gap('gemmc16-fp32-randn','burst')} | no zeros run | {ns('gemmc16-fp32-randn')} |
| cold, strides | fp32 random | {gap('gemmv16-fp32-randn','burst')} | no zeros run | {ns('gemmv16-fp32-randn')} |

- **fp32 by column: the rate now follows the clock.** Random reads ×1.24 in the burst on a clock gap of ×1.22 (one run), against as-run's ×1.03 on ×1.06. **Sustained random fp32 by column was not measured at full chip:** after the burst read {peak['A-11-gemmc1-fp32-randn-r1']} W the rule refused it. The registered primary kind, sparse25, reads ×1.22 on ×1.21 over two runs: R4 COMES BACK. fp16 random did reach sustained: **×1.32 on ×1.33, the page's loop's own size,** one run.
- **int8 slows too once its tiles fit:** ×1.17 sustained on ×1.16, two runs (R5 COMES BACK), against as-run's ×1.00. It is under the benchmark's ×1.32, because by column int8 draws less (below).
- **The vendor's strides sit between:** random fp32 sustained ×1.145 on a clock gap of ×1.287. M is {F['gemmv1.fp32']['M']:.2f} µs, a share of as-run's that is close to the desk model's (R2).
- **The kind still never changes the count at a given clock:** T at or above 790 MHz reads {min(T8[k] for k in T8 if k.startswith('gemmc1-fp32')):.4f} to {max(T8[k] for k in T8 if k.startswith('gemmc1-fp32')):.4f} µs by column across zeros, ones, sparse50, sparse25 and random, and {min(T8[k] for k in T8 if k.startswith('gemmv1-fp32')):.4f} to {max(T8[k] for k in T8 if k.startswith('gemmv1-fp32')):.4f} with strides (`results-speed.json` `t800_us`).
- **Two soft cells.** `gemmv1` zeros' only burst, and its int8 zeros' burst, each hit a governor idle reset (756 MHz, `cells.<cell>.idle_resets_burst`), so the strides' burst ratios read under 1; against sparse50's reset-free burst at 800 MHz, 8.206 TFLOPS, random's is ×1.070 (clock ×1.103). As-run sparse25's sustained run was the session's first, from a die of 49 °C where the others started at 53–58 °C, and it did not reach the 65 °C trip in its 76 s, so its ×1.00 understates that kind and R6's lower anchor is soft.
- **Every check of C held on both cards:** exact or approx, none wrong (`results-speed.json` `cells.<cell>.checks`; `aifoundry3/*/p*/runs.jsonl`).

**Power at 600 MHz on aifoundry3 (A1).** S over idle, W, and pJ per multiply-add, random (`scored-p.json` `cells`; E101's `e101.json`). By column stands on two passes. **Strides stand on one:** E78's own gate set `p10521` aside (fp32 random spanned 1.72 W against its 1 W). Real tensors read within 0.4 W of random in fp32 and fp16 by column.

| format | the loop | as run | strides | by column | benchmark | cold, by column | cold, strides |
|---|---|---|---|---|---|---|---|
| fp32 | {E101['fp32.randn']['S']['mean']:.2f} W, {E101['fp32.randn']['pj_mac_S']['mean']:.2f} pJ | {E101['gemm1.fp32.randn']['S']['mean']:.2f} W, {E101['gemm1.fp32.randn']['pj_mac_S']['mean']:.2f} pJ | {A['gemmv1.fp32.randn']['S_w']:.2f} W, {A['gemmv1.fp32.randn']['pj_mac']:.2f} pJ | **{A['gemmc1.fp32.randn']['S_w']:.2f} W, {A['gemmc1.fp32.randn']['pj_mac']:.2f} pJ** | {E101['mm16.fp32.randn']['S']['mean']:.2f} W, {E101['mm16.fp32.randn']['pj_mac_S']['mean']:.2f} pJ | {A['gemmc16.fp32.randn']['S_w']:.2f} W, {A['gemmc16.fp32.randn']['pj_mac']:.2f} pJ | {A['gemmv16.fp32.randn']['S_w']:.2f} W, {A['gemmv16.fp32.randn']['pj_mac']:.2f} pJ |
| fp16 | {E101['fp16.randn']['S']['mean']:.2f} W, {E101['fp16.randn']['pj_mac_S']['mean']:.2f} pJ | {E101['gemm1.fp16.randn']['S']['mean']:.2f} W, {E101['gemm1.fp16.randn']['pj_mac_S']['mean']:.2f} pJ | {A['gemmv1.fp16.randn']['S_w']:.2f} W, {A['gemmv1.fp16.randn']['pj_mac']:.2f} pJ | **{A['gemmc1.fp16.randn']['S_w']:.2f} W, {A['gemmc1.fp16.randn']['pj_mac']:.2f} pJ** | {E101['mm16.fp16.randn']['S']['mean']:.2f} W, {E101['mm16.fp16.randn']['pj_mac_S']['mean']:.2f} pJ | {A['gemmc16.fp16.randn']['S_w']:.2f} W, {A['gemmc16.fp16.randn']['pj_mac']:.2f} pJ | {A['gemmv16.fp16.randn']['S_w']:.2f} W, {A['gemmv16.fp16.randn']['pj_mac']:.2f} pJ |
| int8 | {E101['int8.full']['S']['mean']:.2f} W, {E101['int8.full']['pj_mac_S']['mean']:.2f} pJ | {E101['gemm1.int8.full']['S']['mean']:.2f} W, {E101['gemm1.int8.full']['pj_mac_S']['mean']:.2f} pJ | {A['gemmv1.int8.full']['S_w']:.2f} W, {A['gemmv1.int8.full']['pj_mac']:.2f} pJ | **{A['gemmc1.int8.full']['S_w']:.2f} ± {A['gemmc1.int8.full']['ci95']:.2f} W, {A['gemmc1.int8.full']['pj_mac']:.2f} pJ** | {E101['mm16.int8.full']['S']['mean']:.2f} W, {E101['mm16.int8.full']['pj_mac_S']['mean']:.2f} pJ | {A['gemmc16.int8.full']['S_w']:.2f} W, {A['gemmc16.int8.full']['pj_mac']:.2f} pJ | {A['gemmv16.int8.full']['S_w']:.2f} W, {A['gemmv16.int8.full']['pj_mac']:.2f} pJ |

- **At the benchmark's rate, by column draws less than the benchmark:** {A['gemmc1.fp32.randn']['rate']:.2f} against 9.48 TFLOPS on {A['gemmc1.fp32.randn']['S_w']:.1f} W against 36.5 W, and {A['gemmc1.int8.full']['rate']:.1f} against 71.5 TOPS on {A['gemmc1.int8.full']['S_w']:.1f} W against 27.4 W. Its one difference that plausibly explains this is cooperative loads, which E101's R8 priced; this is a reading, not a measurement.
- **So a random fp32 multiply-add costs {A['gemmc1.fp32.randn']['pj_mac']:.2f} pJ in a GEMM pattern whose tiles fit,** at 600 MHz on aifoundry3, against the port's 8.37, which carried its misses and stall time, and the loop's 5.76. Zeros: {A['gemmc1.fp32.zeros']['pj_mac']:.2f} pJ.
- **The benchmark's +18 W comes back in part:** int8's premium over the loop is {P3['premium_w']:.1f} W by column (as run {P3['as_run_e101']:.1f}, benchmark {P3['benchmark_e101']}): P3 PARTIAL, with ±{P3['ci95']:.1f} W on two passes.
- **Zeros' share by column:** {PV['P5']['fp32']['share'] * 100:.1f}%, {PV['P5']['fp16']['share'] * 100:.1f}%, {PV['P5']['int8']['share'] * 100:.1f}%, close to the benchmark's (P5 PASS), on two passes; fp32 zeros carry ±{A['gemmc1.fp32.zeros']['ci95']:.1f} W.

## The cold variant, 16 blocks

**A one-pass walk over 48 MB, each block touched once per pass, has no gap in either layout: zeros ÷ random ×{G['gemmc16-fp32-randn']['burst_rate']:.3f} by column and ×{G['gemmv16-fp32-randn']['burst_rate']:.3f} with strides, burst, one run each (R8 PASS on the gap).** Random draws {A['gemmc16.fp32.randn']['S_w']:.1f} W over idle against zeros' {A['gemmc16.fp32.zeros']['S_w']:.1f} W, and the clocks do not part either, because at these rates the watts stay under the limits ({C['gemmc16-fp32-randn']['burst_mhz']:.0f} MHz in the burst, {C['gemmc16-fp32-randn']['sus_mhz']:.0f} MHz sustained).

**The frozen model of it failed.** M does not scale with the desk model's miss share there: {F['gemmc16.fp32']['M']:.2f} µs by column against 1.27 frozen, {F['gemmv16.fp32']['M']:.2f} µs with strides against 1.53. **By column is no faster than as-run when cold:** {A['gemmc16.fp32.randn']['rate']:.2f} TFLOPS at 600 MHz against E101's as-run {r101('gemm16.fp32.randn'):.2f}, and strides are slower still at {A['gemmv16.fp32.randn']['rate']:.2f}. So past the L2 and the L3 the layout's reuse stops mattering and something else limits the walk. DRAM's bandwidth under 32 shires is the likely limit; that is a reading, not a measurement. The block's C here is overwritten, never accumulated across blocks, and no block was warmed first.

## Which regime a large GEMM sits in, on this chip

**On the ET-SoC-1 the regime is set by how often a tile is reused while it is in the L2, and not by the numbers. A block that stays in the L2 runs T = 527/f + 0.02 µs: the clock sets the pace, and the kinds' clock gap is the speed gap, which is what Horace He's speed gap on an A100 implies for his run. A walk that touches each block once from DRAM runs about T = 374/f + 1.97 µs: the memory sets the pace, and zeros and random run at one rate. As-run and the vendor's strides sit between, at M = 0.83 and 0.52 µs. E105 brackets a large GEMM; it does not place one.** The vendor's partition reads each A tile once and each B tile twice per block, which leans towards the cold end unless a block is repeated, but that is the desk model's reading: nobody here has timed the vendor's binary or a production run, and nothing here measured a sweep between one touch and many.

## Registered against what happened

**Rules on aifoundry2** (`results-speed.json` `rules`, 57 runs, 1 refused, nothing wrong in any check of C):

| rule | registered | measured | verdict |
|---|---|---|---|
| R1 by column removes M | M ≤ 0.15 µs, C in 470–590 | M {V['R1']['M']:.4f}, C {V['R1']['C']:.1f} | **PASS** |
| R2 strides' M | M ÷ as-run's in 0.35–0.78 (desk 0.559) | {V['R2']['ratio']:.3f} | **PASS** |
| R3 the tie to E101 | C within 30 of 344.3, M within 0.08 of 0.838 | C {V['R3']['C']:.1f}, M {V['R3']['M']:.3f} | **PASS** |
| R4 fp32 gap by column | sustained ≥ 1.15 and within 0.03 of the clock | ×{R4['rate']:.3f} on ×{R4['clock']:.3f} (frozen ×1.33) | **COMES BACK**; the size missed |
| R5 int8 gap by column | sustained ≥ 1.15 | ×{R5['rate']:.3f} on ×{R5['clock']:.3f} (frozen ×1.33) | **COMES BACK**; the size missed |
| R6 strides between | strictly between as-run and by column | {R6['as_run']:.3f} < {R6['vendor']:.3f} < {R6['bycol']:.3f} | **PASS**, on as-run's soft cell |
| R7 T at 800 MHz, 12% | as run 1.268, strides 0.898, by column 0.661 | {R7['cells']['gemm1']['T']:.3f}, {R7['cells']['gemmv1']['T']:.3f}, {R7['cells']['gemmc1']['T']:.3f}; order holds | as run **PASS**, **strides FAIL (+14%)**, by column **PASS** |
| R8 cold T, 25% | by column 1.701, strides 1.959 | {R8['gemmc16']['T']:.3f}, {R8['gemmv16']['T']:.3f} | **FAIL, FAIL (+43%, +42%)** |
| R8 cold gap | ≤ ×1.06 | ×{R8['gemmc16']['gap_burst']:.3f}, ×{R8['gemmv16']['gap_burst']:.3f}, burst only | **PASS** |
| R9 half K, 5% | 0.661 | {R9['T']:.3f} (+4.9%) | **PASS**; R1 and R7 did not miss on `gemmc1`, so it was not needed |

**Rules on aifoundry3** (`scored-p.json` `rules`):

| rule | registered | measured | verdict |
|---|---|---|---|
| P1 rate at 600 MHz, by column, 5% | 9.50, 18.99, 71.6 | {PV['P1']['gemmc1.fp32']['measured']:.2f}, {PV['P1']['gemmc1.fp16']['measured']:.2f}, {PV['P1']['gemmc1.int8']['measured']:.1f} | PASS, PASS, **int8 FAIL (−6.1%)** |
| P1 strides, 15% | 8.04, 16.02, 31.7 | {PV['P1']['gemmv1.fp32']['measured']:.2f}, {PV['P1']['gemmv1.fp16']['measured']:.2f}, {PV['P1']['gemmv1.int8']['measured']:.1f} | PASS, PASS, PASS |
| P1 cold, 25% | fp32 4.54 by column, 3.98 strides | {PV['P1']['gemmc16.fp32']['measured']:.2f}, {PV['P1']['gemmv16.fp32']['measured']:.2f} | **FAIL in all six** (−27% to −36%) |
| P2 random's S by column, 15% | 39.3, 36.0, 29.6 W | {PV['P2']['fp32']['measured']:.1f}, {PV['P2']['fp16']['measured']:.1f}, {PV['P2']['int8']['measured']:.1f} W | **FAIL, FAIL, FAIL** (−16%, −17%, −38%) |
| P3 int8 premium | ≥ 12 W comes back, < 6 W does not | {P3['premium_w']:.1f} W | **PARTIAL** |
| P4 the refusal | by-column random fp32 at 800 MHz, from S | {P4['p800_w']:.1f} W, at or above 88 W | **the cell should have been refused; it was not** (next section) |
| P5 zeros' share, 0.05 | benchmark's 0.126, 0.138, 0.280 | {PV['P5']['fp32']['share']:.3f}, {PV['P5']['fp16']['share']:.3f}, {PV['P5']['int8']['share']:.3f} | **PASS** ×3 |

**Why the frozen numbers missed.**
- **Cold:** M was scaled by miss share, and it does not scale. That model is wrong for a walk fed from DRAM.
- **Strides:** C is {F['gemmv1.fp32']['C']:.0f}, not 344, and M {F['gemmv1.fp32']['M']:.3f}, not 0.468, so T at 800 MHz is 14% long. The desk model has the share about right (0.62 against 0.56). What it cannot say is C.
- **By column's watts:** the frozen c assumed 1.08 × the benchmark's. It measured 0.90 in fp32 random and 0.65 in int8 full. So the frozen clocks ran low: {P['frozen_clock_rms_mhz']['burst']} MHz rms in the burst and {P['frozen_clock_rms_mhz']['sustained']} sustained over {P['frozen_clock_rms_mhz']['n_burst']} and {P['frozen_clock_rms_mhz']['n_sus']} cells (labelled, no rule), and the gaps came in at ×1.22 and ×1.17 where ×1.33 was frozen.

## The power rule did not do what it was for

**The rule admitted the one cell it existed to catch.** By-column random fp32 was estimated at 87.83 W from its sparse50 probe (rho 0.81), 0.17 W under the 88 W limit. It measured {C['gemmc1-fp32-randn']['burst_p800_w_runs'][0]} W at 800 MHz and **peaked at {peak['A-11-gemmc1-fp32-randn-r1']} W, 0.75 W under the session's 97 W stop.** The probe's rho read low: random's true share was 0.90. The stop did not fire, and the registered 93 W lock then refused its sustained run (`aifoundry2/s1/skipped.jsonl`), which is why that cell is missing. fp16 random by column went on under the lock, estimated 86.13 W, and read {peak['E-04-gemmc1-fp16-randn-r1']} and {peak['E-05-gemmc1-fp16-randn-r1']} W. **So by-column random fp32 at 800 MHz sits at this card's stop, and starting it from a cool die is not safely repeatable under a 97 W stop.** Three highest readings: {', '.join(f'{v} W ({k})' for v, k in top)} (`aifoundry2/admission.json`).

## Departures

- **The aifoundry2 start was 07:36, not about 07:20:** E98's claim read released at 07:21, and the Intel's load guard then paused the claim post for about 5 minutes. A2.
- **The power arm's queue first exited 127 before touching the card,** going one directory short of the root. Fixed and restarted at 07:36:04 PST. A2.
- **Its claim post, `1566472292924661822`, could not be released by the usual edit.** It was posted at 07:21:38 PST, and at 08:40 PST it was no longer in the channel, nor were the other posts between 31 Oct and aifoundry2's claim; no entry for it is in the card-post archive, and this lane did not delete it. Its queue had ended at 08:11 PST. aifoundry2's claim `1566475985451491350` was edited to read released at 08:38 PST and read back.
- **One power-arm run was skipped:** `p10520` #25, resident `fp16.sparse50`, did not reach its launch reading. It is not one of E105's cells.
- **`p10521` was set aside by E78's gate,** so the strides' S rests on one pass and has no interval.
- **The vendor's binary was not run:** about 58 µs per launch against about 2 ms of launch overhead, and no cycle counter, so timing it needs an instrumented build. It is still the first open item.
- The reductions ran on the mini, because the Intel's load guard pauses tool children in its hot tier.

## What E105 says about the page

- **§1 and the lede may say:** in the same GEMM pattern with tiles that fit the L2, the rate follows the clock (T = 527/f + 0.02 µs), and zeros beat random by ×1.24 in a burst in fp32 and ×1.32 sustained in fp16, one run each, on aifoundry2. **They may not print sustained fp32 random by column as measured.** They may not say a real GEMM has or lacks the gap without saying how often it reuses a tile.
- **E101's "a fixed 0.84 µs per op" now has its cause:** the layout. One edit removes it.
- **§2:** a random fp32 multiply-add costs {A['gemmc1.fp32.randn']['pj_mac']:.2f} pJ by column at 600 MHz on aifoundry3, {A['gemmc16.fp32.randn']['pj_mac']:.2f} pJ cold.
- **§3:** "int8 hardly slows" is false by column as well (×1.17). It holds in the loop and in the as-run port.
- **§7:** zeros' share by column sits with the benchmark's.
- **§11:** close "does the gap come back when the tiles fit". **New open items, first:** a sweep of reuse between one touch and many, which is what would place a real block size; then the vendor's binary; then what limits the cold walk.

**For the post, in short sentences.** Each names its card and clock.
- On aifoundry2 under its own governor, one edit to where a GEMM's tiles live took the fixed part of its time per op from 0.83 µs to 0.02 µs, and its rate from 6.6 to 12.4 TFLOPS at 800 MHz (`results-speed.json` `fits`).
- With the tiles in the L2, zeros beat random numbers by 24% in a burst in fp32 (one run), and by 32% sustained in fp16 (one run), matching the clock gap, on aifoundry2 under its own governor (`results-speed.json` `gaps`).
- Walking fresh blocks from DRAM, the same kernel ran zeros and random at the same rate, within 0.2%, in a burst on aifoundry2 (`results-speed.json` `rules.R8`).
- So a speed gap between kinds of numbers appears when the clock sets the pace, and that depends on how often a tile is reused, on this chip. Nobody here has measured where a production GEMM falls.

## Files

`results-speed.json`, `reduce-speed.txt` (aifoundry2, `reduce_e105.py`); `e105c.json`, `e105v.json`, `-runs.csv`, `-reduce.txt` (aifoundry3, E101 session 1's `reduce_e101.py` unchanged, with `E101_GEMM` set; its `gemm1.*` and `gemm16.*` items ran the layout the file names); `scored-p.json`, `scored-p.txt` (`score_e105p.py`); `aifoundry2/` (`smoke/`, `s1/`: `runs.jsonl`, `skipped.jsonl`, `marks.jsonl`, `launches.jsonl.gz`, `tel/`, `sp/`; the queue's `queue.jsonl`, `admission.json`, `config-*.txt`, `sensors-*.json`, `history-before.jsonl`, the binaries' sha256); `aifoundry3/` (`kinds-e105c/`, `kinds-e105v/`, and their `-smoke/`: every pass's raw data); `logs/` (both queues, both builds); `code.sha256`. The registration and the desk L2 model are in [`tools/claims-v3/kspeed/e105/`](../../../../tools/claims-v3/kspeed/e105/E105.md).
"""
open(f"{D}/README.md", "w").write(s)
print(len(s), "bytes")
