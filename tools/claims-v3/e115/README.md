# E115: blind pool 3 on the card — the power model M5 against 25 tiles written before it was read (Q133, aifoundry3 card 0, 600 MHz)

*Pre-registered Sun 1 Nov 2026 (week 44), on the Intel, before the Discord claim and before any card has run a tile of the pool, in
Q133's run. **Answers item 6 of the kinds page's section 11**, "A power model across kinds"
([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), the list as
it read at `1fe8377a18af`). **Every prediction E115 scores is Q133(b)'s, frozen before this was written**: the pool
([`../kinds/blind3/`](../kinds/blind3/README.md), `a9167033`), the model M5 and the predictions for the pool from M5 and M4
(`64b4124e`), the contrasts' 95% intervals (`0fae735f`). E115 adds no prediction of M5's or M4's. What it adds is frozen in
[`predictions-e115.json`](predictions-e115.json), written by [`make_predictions_e115.py`](make_predictions_e115.py) from the committed
sources it names, every number read from its file: the hashes it refuses to run without, the plan, the rules and their thresholds, the
reference errors behind R1 and R2, the session tie, and one comparator (F0r, below). Any change after this commit goes in Amendments,
dated, before the data it touches. Card: **aifoundry3 card 0 only**, 600 MHz pinned, TDP 0 and threshold 65 °C as read, never set. E115
writes no knob: no governor move, no TDP, threshold or clock set, no reset, no `--reset-ms`, no PMIC command.*

## The question

Q133(b) refitted the bench's power model on thirteen experiments and froze it as **M5**: M4's form with the adder priced per float
format. Scored by nested leave-one-kind-out, M5 reads 0.201 W rms over 283 float rows (95% bootstrap over kinds 0.180–0.222 W) and
0.262 W over 78 int8 rows. Its gain over M4's own form refitted, 0.011 W, is not resolved, and the per-format term was added after a first
look at the misses (Q133(b) C1, C2). So the open question is not whether M5 fits the kinds it was fitted on; it is **whether that accuracy
holds on kinds nobody fitted, on the open cases item 6 lists**. Blind pool 3 is 25 tiles built on those cases (signs alternating on
moving sums, exponents spread under a gate, gated kinds three ways, the A side with a busy and a quiet partner, the memory path's own
term, the zero level, another stream) and committed before its designer read the model. E115 measures them on the card the
constants are on, beside E78's anchors, with E78's code, protocol and reduction, and asks:

1. **Is M5 as accurate on the blind pool as its nested leave-one-kind-out score says?** Floats (R1) and int8 (R2), each against the
   interval that score implies for that many tiles.
2. **Do its frozen 95% intervals hold?** (R3)
3. **Do the pool's seven built-in contrasts land inside their frozen intervals?** (R4) One of them, `m_blines_eq` − `m_bpair_eq`, moves
   B's in-lane alternation and its line-to-line bits apart, which the bench (no memory path) cannot price: it reads both ways.
4. **Does M5 beat M4?** (R5) The two differ by at most 0.20 W on any pool tile, so this is expected to stay unresolved; the comparator
   F0r splits the refit from the per-format term, reported.

## The models and the pool, frozen elsewhere

| what | file | sha256 | frozen in |
|---|---|---|---|
| the pool: 25 tiles, `open_case`, `priority` | [`../kinds/blind3/blind3.json`](../kinds/blind3/blind3.json), `SHA256SUMS`, `tiles/` | `60dfbf12…`, `d100a9c7…` | `a9167033`, 10:53:35 PST, before M4's files were opened |
| M5 (floats `F10_add_by_format`, int8 `I0_I3`) | [`m5.json`](../../../docs/reports/data/2026-11-01-q133b-power-model/m5.json) | `c19f2c7b…` | `64b4124e` |
| M5's and M4's predictions for the pool, footings a3 / c1 / new, anchor ratios | [`../kinds/blind3/predictions-blind3.json`](../kinds/blind3/predictions-blind3.json) | `5f28091a…` | `64b4124e` |
| the seven contrasts' 95% intervals | [`../kinds/blind3/contrasts-blind3.json`](../kinds/blind3/contrasts-blind3.json) | `399128b9…` | `0fae735f`, 12:57:41 PST |
| M5's nested leave-one-kind-out errors (R1's and R2's reference) | [`loko.json`](../../../docs/reports/data/2026-11-01-q133b-power-model/loko.json) | recorded in `predictions-e115.json` | `64b4124e` |

`make_predictions_e115.py` checks each file against the hash Q133(b) published and refuses on any difference; `run_e115.py`,
`reduce_e115.py` and `run_e115.sh setup` check the pool's four files and every tile again. **M4** is as frozen for E103 (`b995463e`;
`predictions-e103.json` `7ac59cae…`), carried in `predictions-blind3.json`. **The independence of the pool is half met**: Q133(b) had no
Agent tool, so the pool was designed by the lane that fitted M5, before it read M4's files but after reading commit subjects that name
M4's form (the pool's README, § The independence protocol). E115 cannot change that; it says so wherever it reports.

**The footing.** D is board power over the type's own zeros at 600 MHz, as E78's reduction reads it. aifoundry3 card 0 is the card M5's
constants are on, so the registered footing is **a3**, the predictions as frozen, with no scale. Sessions on this card have read
`fp32.randn` from 24.32 W (E95) to 24.95 W (E92), and M5's training rows carry that session-to-session spread, so its nested errors and
R1's reference already include it. The **anchor footing** (each prediction times the session's measured anchor over the model's predicted
anchor, `predictions-blind3.json`'s ratios) is reported beside every verdict, and a verdict that differs there is marked footing-sensitive.
This run does not test "a new card without a scale": that needs another card, and Q133 put E115 here.

**F0r, a comparator E115 adds (reported, never a verdict).** M4's float form (core, bus, other nets, clocked bit), refitted on Q133(b)'s
283 rows with no per-format term: Q133(b)'s committed full-fit constants (`loko.json` › `families.float.coef_fJ_fit_on_all_by_form.F0_M4`:
1.604, 7.904, 2.256, 1.056 fJ) on its committed counts, through its own feature code (`fit_m5.py`). The same code reproduces M5's frozen a3
predictions for all 19 float tiles exactly (max difference 0.0 W). M5 against F0r is the per-format term alone; F0r against M4 is the
refit alone. F0r differs from M5 by at most 0.14 W on any tile; for int8, F0r is M5's own I3 refit.

## What runs

| | |
|---|---|
| a run | E78's: `sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions, heat to 59 °C, launch at 58 °C after 2.0 s quiet |
| the tiles | all 25 of blind pool 3 (20 priority 1, 5 priority 2; the window holds all 25, so none is dropped): `tools/claims-v3/kinds/blind3/tiles/<type>/<kind>.bin`, 2,048 bytes each (A then B), items `<type>.<kind>` |
| anchors | E78's six (each type's zeros and its random kind: `fp32.randn`, `fp16.randn`, `int8.full`) **three times in every pass**, once in each third: drift, the zero level D is measured over, and the anchor footing |
| the tie | `anchor_pi` (the host's built-in fp32 pi), first and last in every pass |
| a pass | 45 runs: the tie, three segments of E78's six anchors and 9, 8, 8 of the 25 tiles, the tie. The 25 are shuffled with `Random("E115\|aifoundry3\|<pass>")` and dealt round-robin; each segment is shuffled again (`e115_common.pass_order`). Two unrecorded `anchor_pi` burn-in runs open each pass |
| passes | **11510–11512 (three), at least two kept needed to score.** Smoke **11501**: blind3.json's eight 2 s runs (the tie, `fp32.s_pair0`, `fp32.g_blanes_alt`, `fp32.zeros`, `fp32.randn`, `fp16.s_inword0`, `int8.g_awords_alt`, `int8.zeros`), no preheat, read for cycles per op before any pass |
| config reads | `ettelem config` under the card lock with `timeout 10` at both ends of every block; the smoke's start read is the session-start read, and the queue reads once more when it ends (the session-end read) |
| data | raw: aifoundry3 `~/aifoundry/build/claims-v3/aifoundry3/kinds/p115<nn>/`, logs `build/e115-logs/`; results [`docs/reports/data/2026-11-01-e115-blind-pool/`](../../../docs/reports/data/2026-11-01-e115-blind-pool/) |

## What is E78's, byte for byte

E115 runs E78's card code and reduction **unchanged**, as E86, E90, E92, E95 and E103 did; `run_e115.py`, `reduce_e115.py` and
`run_e115.sh setup` check these against `predictions-e115.json` › `harness.reused_unchanged_sha256` and refuse to run on any difference:
`tools/claims-v3/lib.sh` `033d0776…`, `kinds/e78_common.py` `c58923a5…`, `kinds/run_e78.py` `f3efd783…`, **`kinds/reduce_e78.py`
`6a158cee…`**, `kinds/kinds.json` `9586568f…`. `e115_common.install()` replaces `load_items` (E78's items plus the pool's 25 tiles, every
number copied from `blind3.json`) and `pass_order` on the shared `e78_common` module in memory, then `run_e78.main()` /
`reduce_e78.main()` run as they are. So every run gate (600 MHz, ±3 mV, launch at 58 °C after 2.0 s quiet, records ok, cycles per op
within 0.5% of 546 / 546 / 318, ≥ 15 window samples, duty ≥ 0.97, **the tile the host dumps equal to the item's registered sha256**), every
pass gate (> 2 failed runs; each type's zeros line 0.25 W and range 0.60 W; random range 1.0 W; pi drift 0.60 W; TDP 0 / threshold 65 at both
ends), the interpolation of each type's zeros, **D = p80 − Ẑ_type(t0)**, S, pJ per op and ΔT are E78's own. New, ported with marked changes:
`e115_common.py` (from `kinds/e103_common.py`, as Q133(b) asked), `run_e115.py` (from `run_e103.py`), `block_e115.sh` (from `block_e95.sh`, E95's
aifoundry3 block), `queue_e115.sh` (from `queue_e95.sh`, its budget counted from the session start as E112's), `run_e115.sh`, `reduce_e115.py`
(from `reduce_e95.py`, with `reduce_e103.py`'s two arms), `collect_e115.sh`. Same binary as E67–E95 (`build/sparsity/host/sparsity_host`,
26 Sep); no rebuild. As for every kind, a `file:` run checks no arithmetic.

| | E95 (the last kinds run on this card) | E115 | why |
|---|---|---|---|
| items | 30 real2 tiles + 3 of E86's, 6 anchors three times, the tie twice: 53 | the 25 pool tiles, 6 anchors three times, the tie twice: **45** | the question |
| order | `Random("E95\|aifoundry3\|<pass>")` | `Random("E115\|aifoundry3\|<pass>")`, the same dealing | E115's items |
| passes | 9510–9513 (+9514), at least three kept | **11510–11512, at least two kept** | the 30 card-minute cap: three passes fit, four do not |
| leakage | primary `auto`; arms 0.1994, 0.3803, 0 | the same | as on this card since E78 |
| dips arm | registered fallback | the same (`reduce_e115.py --drop-dips`) | E95's |

## The frozen predictions

D in W over the type's own zeros, aifoundry3 card 0, 600 MHz. M5 and M4 from `predictions-blind3.json` (a3 footing; the interval is
t(0.975, n − 2) × √(pool² + x′Cx + m²), pool the rms of M5's nested errors for that format on this card); F0r from `predictions-e115.json`.
† `fp16.s_wpair0`'s bench count carries fp16's window-model residue (5 of 256 accumulator words differ from software at each launch point):
it is scored as frozen, and R1 is also reported without it.

| tile | open case | prio | **M5, a3 [95%]** | M4, a3 [95%] | F0r | M5 ÷ anchor |
|---|---|---:|---:|---:|---:|---:|
| `fp16.a_mant_b_randn` | a-side-busy-partner | 1 | **21.78** [21.43, 22.14] | 21.97 [21.61, 22.34] | 21.92 | 0.9894 |
| `fp32.a_colconst_b_randn` | a-side-busy-partner | 2 | **23.17** [22.72, 23.61] | 23.15 [22.71, 23.58] | 23.07 | 0.9455 |
| `fp32.a_lo8_b_pi` | a-side-busy-partner | 1 | **10.68** [10.29, 11.07] | 10.82 [10.43, 11.20] | 10.72 | 0.4360 |
| `fp32.a_lo8_b_randn` | a-side-busy-partner | 1 | **22.23** [21.80, 22.65] | 22.18 [21.77, 22.58] | 22.10 | 0.9072 |
| `int8.a_colconst_b_full` | a-side-busy-partner | 2 | **3.17** [2.50, 3.84] | 3.30 [2.40, 4.19] | (= M5) | 0.4535 |
| `int8.a_low2_b_full` | a-side-busy-partner | 1 | **4.82** [4.29, 5.36] | 4.87 [4.19, 5.55] | (= M5) | 0.6909 |
| `int8.st_f32bytes` | another-stream | 2 | **6.69** [6.22, 7.16] | 6.63 [6.08, 7.18] | (= M5) | 0.9582 |
| `fp16.x_logu_s50` | exponents-spread-gate | 1 | **7.71** [7.35, 8.07] | 7.69 [7.33, 8.04] | 7.72 | 0.3502 |
| `fp32.x_logu_bsteady` | exponents-spread-gate | 2 | **13.88** [13.49, 14.26] | 13.82 [13.46, 14.17] | 13.78 | 0.5664 |
| `fp32.x_logu_s50` | exponents-spread-gate | 1 | **8.27** [7.88, 8.66] | 8.20 [7.84, 8.55] | 8.22 | 0.3375 |
| `fp16.g_blanes_alt` | gated-kinds | 2 | **12.44** [12.08, 12.80] | 12.46 [12.10, 12.82] | 12.48 | 0.5652 |
| `fp32.g_arows_alt` | gated-kinds | 1 | **13.29** [12.90, 13.69] | 13.24 [12.87, 13.60] | 13.22 | 0.5426 |
| `fp32.g_blanes_alt` | gated-kinds | 1 | **14.00** [13.60, 14.40] | 13.94 [13.57, 14.30] | 13.94 | 0.5713 |
| `fp32.g_blanes_steady` | gated-kinds | 1 | **13.22** [12.83, 13.60] | 13.21 [12.84, 13.58] | 13.16 | 0.5394 |
| `int8.g_awords_alt` | gated-kinds | 1 | **4.71** [4.24, 5.17] | 4.69 [4.13, 5.25] | (= M5) | 0.6737 |
| `int8.g_bpairs_steady` | gated-kinds | 1 | **3.76** [3.30, 4.21] | 3.71 [3.18, 4.24] | (= M5) | 0.5380 |
| `fp32.m_blines_eq` | memory-path | 1 | **24.80** [24.40, 25.20] | 24.79 [24.39, 25.19] | 24.70 | 1.0122 |
| `fp32.m_bpair_eq` | memory-path | 1 | **16.42** [16.03, 16.80] | 16.48 [16.11, 16.85] | 16.38 | 0.6701 |
| `fp16.s_inword0` | signs-moving-sums | 1 | **16.68** [16.34, 17.02] | 16.88 [16.51, 17.25] | 16.80 | 0.7577 |
| `fp16.s_wpair0` † | signs-moving-sums | 1 | **21.44** [21.08, 21.81] | 21.56 [21.19, 21.93] | 21.51 | 0.9740 |
| `fp32.s_bridge` | signs-moving-sums | 1 | **25.32** [24.93, 25.72] | 25.27 [24.89, 25.65] | 25.19 | 1.0336 |
| `fp32.s_drift12` | signs-moving-sums | 1 | **24.70** [24.30, 25.11] | 24.71 [24.30, 25.12] | 24.61 | 1.0083 |
| `fp32.s_pair0` | signs-moving-sums | 1 | **24.64** [24.25, 25.03] | 24.62 [24.24, 25.01] | 24.54 | 1.0058 |
| `fp32.z_single` | zero-level | 1 | **0.01** [−0.36, 0.39] | 0.01 [−0.34, 0.36] | 0.01 | 0.0006 |
| `int8.z_diag` | zero-level | 1 | **1.85** [1.39, 2.31] | 1.88 [1.32, 2.44] | (= M5) | 0.2649 |

The anchors M5 predicts on this footing (in-sample kinds, for the anchor footing only): `fp32.randn` 24.50, `fp16.randn` 22.02,
`int8.full` 6.98 W (`predictions-blind3.json` › `anchors_predicted_a3_w`).

**The contrasts** (`contrasts-blind3.json`; each point is the difference of the two tiles' frozen predictions, each interval the two
tiles' 95% half-widths in quadrature, which on training pairs held 95.5% of 1,680 float differences, Q133(b) C5). E115 measures each as
D(plus) − D(minus) inside each kept pass, averaged over passes:

| contrast | isolates | **M5, a3 [95%]** | M4, a3 [95%] |
|---|---|---:|---:|
| `fp32.g_blanes_alt` − `fp32.g_blanes_steady` | gate switching every cycle against a steady gate, same gated fraction | **+0.78** [+0.23, +1.34] | +0.73 [+0.21, +1.24] |
| `fp32.a_lo8_b_randn` − `fp32.a_lo8_b_pi` | the same A side with a busy and a quiet partner | **+11.55** [+10.97, +12.12] | +11.36 [+10.80, +11.92] |
| `fp32.m_blines_eq` − `fp32.m_bpair_eq` | B alternating in-lane with no line changes, against lines changing with no in-lane alternation | **+8.38** [+7.82, +8.94] | +8.31 [+7.76, +8.86] |
| `fp32.s_drift12` − `fp32.s_pair0` | a sum that drifts up against one that returns to 0 | **+0.06** [−0.50, +0.63] | +0.08 [−0.48, +0.65] |
| `fp32.s_bridge` − `fp32.s_pair0` | a sum that climbs and walks back against one that returns every step | **+0.68** [+0.12, +1.24] | +0.65 [+0.11, +1.19] |
| `fp32.x_logu_s50` − `fp32.x_logu_bsteady` | exponents spread: a random 50% word gate against a steady lane gate | **−5.61** [−6.16, −5.06] | −5.62 [−6.12, −5.12] |
| `fp16.s_wpair0` − `fp16.s_inword0` | fp16: cancelling across k-groups against inside the two-term update | **+4.76** [+4.26, +5.26] | +4.68 [+4.15, +5.20] |

**The memory-path pair, read both ways, decided now.** The bench has no memory path, so its +8.38 W is all compute and the operand bus
(2.99 W multiplier, 2.05 W adder, 2.61 W other nets, 0.74 W bus). Only `m_bpair_eq`'s B lines change (3,552 bits an op against 0), while
`m_blines_eq`'s B half-lines change about twice as often (3,680 against 1,776). **BELOW** the interval fits a cost for B lines that change;
**ABOVE** fits a cost for half-lines that change; either could instead be compute the bench misprices; **INSIDE** says no memory-path term
at this interval's resolution (±0.56 W), not that there is none.

## Decision rules

All on the primary reduction (E78's, `auto` leakage, dips kept, E78's gates) and the a3 footing. **Fewer than 2 kept passes: every rule
NOT SCORED**, and the dips-removed arm is then the reading reported, labelled as that arm (E95's rule). A tile with fewer than 2 kept passes is
left out and named; R1 and R5 need at least 5 tiles, R2 3, R4 5 contrasts, else UNRESOLVED. Bootstraps over tiles: 10,000 draws, seed 11500.
Every verdict is also computed at the arms (leakage 0.1994, 0.3803 and 0; dips removed; gates off) and on the anchor footing; one that
moves is marked arm-sensitive or footing-sensitive.

**"The nested-LOO interval" for n tiles.** M5's nested score, 0.201 W [0.180, 0.222], is the rms of 283 rows; the rms of 16 new tiles
scatters more. So R1's interval is the 2.5–97.5% range of the rms of the tiles' own format mix drawn with replacement from M5's nested
leave-one-kind-out errors of the same format (150 fp32 and 133 fp16 rows from both cards; int8: 78 rows), 100,000 draws, seed 11500,
recomputed by the scorer for the tiles that actually ran. For the planned sets it is, frozen here:

| set | n | interval, W | its median | beside it, reported: the a3 rows alone | the 283- / 78-row interval |
|---|---:|---|---:|---|---|
| priority-1 floats (12 fp32, 4 fp16) | 16 | **[0.135, 0.288]** | 0.199 | [0.125, 0.236] | [0.180, 0.222] |
| int8, all six | 6 | **[0.124, 0.432]** | 0.234 | [0.105, 0.332] | [0.210, 0.320] |

| rule | what | PASS if | FAIL if | else |
|---|---|---|---|---|
| **E115-R1** | **the float family:** rms(D − M5) over the priority-1 float tiles | rms ≤ the interval's upper bound (0.288 W planned; below its lower bound is marked "better than the nested score says") | rms > the upper bound | — |
| **E115-R2** | **the int8 family:** rms(D − M5) over the int8 tiles | rms ≤ the upper bound (0.432 W planned) | rms > the upper bound | — |
| **E115-R3** | **coverage:** share of every tile that ran with D inside M5's frozen 95% interval | ≥ 80% | < 60% | INCONCLUSIVE |
| **E115-R4** | **the contrasts:** share of the seven inside their frozen M5 interval; each read INSIDE, BELOW or ABOVE | ≥ 85% (6 of 7) | < 65% (4 of 7 or fewer) | INCONCLUSIVE (5 of 7) |
| **E115-R5** | **M5 against M4:** rms(D − M4) − rms(D − M5) over the priority-1 floats, paired bootstrap over tiles | **M5 BETTER** if the 95% interval is above 0 | **M4 BETTER** if below 0 | UNRESOLVED |
| **E115-S1** | the session tie against E78, E95's bands: `fp32.randn` 24.72, `fp16.randn` 22.16, `anchor_pi` 8.36 (±0.50 W), `int8.full` 7.06 (±0.25 W) | all inside | any outside | a failure means the session moved, never a verdict on the model |

**Why these values, before the data.** R1 and R2 take M5's own claim at its word: a blind set drawn like its nested rows should land
inside the range those rows imply, and the pool, built on the open cases, is harder than the rows, so a FAIL says the open cases are
where the model's accuracy ends. R3's 80% is E103-R7's line between intervals usable on new kinds and not (E103 read 83% on a pool built
to break M4); below 60% they say little. R4's line allows one contrast of seven outside its 95% interval, about what chance gives. R5 is
expected to stay UNRESOLVED and says so.

**Reported, never a verdict** (`scored.json` › `reported`, `results.md`): per format (fp32 and fp16, priority 1 and all; int8), the rms
and bias of M5, M4 and F0r; **per open case**, n, the mean D − M5 with its 95% interval over tiles, the rms of M5 and M4, and how many
tiles fall inside; **the per-format term** (M5 against F0r, paired bootstrap over the priority-1 floats, and on the fp16 tiles apart) and
**the refit** (F0r against M4); int8's M5 against M4; R1 without `fp16.s_wpair0`, R1 against the a3-only interval and against the
283-row interval; every tile's D with its 95% interval over passes, M5 [95%], D − M5, M4, D − M4 and F0r; the session's anchors.

**What I expect, frozen so it can be wrong:** R1 PASS, near 0.27 W, with the largest misses on the fp32 sign tiles and
`fp32.x_logu_s50`, reading above M5 (as E103's `c_near_rand`, `s_bhalf_alt` and `x_e_g` did); R2 PASS; R3 PASS, about 21 of 25; R4 PASS or
INCONCLUSIVE, `s_bridge` − `s_pair0` the likeliest outside; the memory pair INSIDE; R5 UNRESOLVED; S1 PASS.

**The statement the page gets, decided now.** R1 PASS: "M5's nested leave-one-kind-out accuracy held on a blind pool of the open cases
on its own card: X W rms over 16 float tiles, inside the [0.135, 0.288] W it implies." R1 FAIL: "it did not: X W, above the 0.288 W its
nested score implies", with the open cases that broke it. R5 is stated as measured, and if UNRESOLVED, item 6's "E115 decides" becomes "E115
could not tell M5 from M4". **Only tiles that ran are scored. No tile is dropped, re-drawn or added after the first pass, and no model,
interval or threshold changes.**

## What the rules cannot say

One card, the card the constants are on, so "a new card without a scale" stays open. Three passes at most: a tile's D has t(2) = 4.30
on its interval (12.7 with two passes). The pool's independence is half met (above). R1's reference rows come from both cards and
thirteen experiments; on this card alone the interval is tighter ([0.125, 0.236] W), and that reading is reported beside, never the
verdict. The contrasts' intervals treat the two tiles' errors as independent; on training pairs that held 95.5% (Q133(b) C5), not more.
A D says what a tile costs, not which stage spends it; the memory pair's reading is a fit to a cost, not a location. No clock, voltage or
other card is tried. M5 and M4 differ by at most 0.20 W on any tile and F0r and M5 by at most 0.14 W, so a pool this size can hardly
separate them.

## Self-test

[`selftest_e115.py`](selftest_e115.py) writes synthetic aifoundry3 passes with E78's own generator (`kinds/selftest_e78.make_pass`) after
installing E115's items and order, with E78's measured D for its kinds, then runs `reduce_e115.py` and `score_e115.py` on four worlds:
**model** (every tile at M5: R1, R2, R3, R4 PASS, every contrast INSIDE, S1 PASS, R5 not M4 BETTER), **dips** (the same with meter dips
injected: the dips arm removes every injected sample, keeps every pass and scores R1 PASS), **m4** (every tile at M4: R5 not M5 BETTER),
and **off** (the open cases broken: R1, R2, R3 and R4 FAIL, the memory pair BELOW), and checks that two kept passes score and one does
not. [`selftest.txt`](selftest.txt): **25 of 25**. Nothing there is a measurement. (In the dips world the primary set all three synthetic
passes aside: three dip pairs a pass is more than this card shows, and it is why the dips arm is the registered fallback.)

## Card budget

**At most 30 card-minutes**, from the session-start config read (the smoke's) to the session-end read, the smoke and the heating gates
included. Expected about 24: the smoke ~1 min, then three passes of ~7.5 min (47 launches at E92's and E95's 9.3–10.2 s a launch) with
15 s between. `queue_e115.sh` starts a pass only if its projected end (the longest measured pass; 480 s until the first ends) is inside
**1,590 s** of the session start and before **18:50 PST**; a pass in flight is never cut. No session starts after 18:00 PST; every run ends by
19:00 PST. It starts only after the previous aifoundry3 lane (E110) has released the card (released 14:27:15 PST), with `et-who` clean and
no open claim in `#community-lab`.

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__` `tools/claims-v3/e115/` and
`tools/claims-v3/kinds/blind3/` to `aifoundry3:aifoundry/tools/claims-v3/`. On aifoundry3, from `~/aifoundry`:

```bash
bash tools/claims-v3/e115/run_e115.sh setup     # no device access: hashes, tiles, binary, plan, a V3_DRY pass, the queue's stub test
# -> read #community-lab, then post the claim (one line, "for 1 h, until ~HH:MM PST")
bash tools/claims-v3/e115/run_e115.sh smoke     # the session-start config read (TDP 0, threshold 65), eight 2 s runs; cycles/op 546 / 546 / 318
bash tools/claims-v3/e115/run_e115.sh go        # detached; the budget rule decides; the queue ends with the session-end read
bash tools/claims-v3/e115/run_e115.sh wait      # bounded waits only
```

Then copy `build/claims-v3/aifoundry3/kinds/p115*`, `kinds-smoke/p11501` and `build/e115-logs/` to the Intel and run
`PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e115/collect_e115.sh 'p115[1-9][0-9]' <copy>`; copy
`build/e115-out/2026-11-01-e115-blind-pool/` to `docs/reports/data/`, write its README (results first; registered against happened;
departures dated; linking section 11 item 6), push, and release the claim by editing it.

## Files

New, all in `tools/claims-v3/e115/`: `README.md` (this), `predictions-e115.json` and `make_predictions_e115.py` (the freeze),
`e115_common.py` (the items, the order, `install()`), `run_e115.py` (run_e78.py unchanged with E115's items), `block_e115.sh`,
`queue_e115.sh`, `run_e115.sh` (the card side), `reduce_e115.py` (reduce_e78.py unchanged, two labelled arms), `score_e115.py` (every rule),
`collect_e115.sh` (reduce, arms, score, assemble), `selftest_e115.py` and `selftest.txt`. Their sha256 are in `predictions-e115.json` ›
`harness.e115_files_sha256`. Data: `docs/reports/data/2026-11-01-e115-blind-pool/`.

## Amendments

*(none yet)*
