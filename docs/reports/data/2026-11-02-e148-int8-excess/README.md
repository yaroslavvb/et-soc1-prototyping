# E148: two A rows put back 0.16 ± 0.10 W of int8's no-issue excess - the A path is excluded as its sole per-row carrier; W1 reads WALK (TenC's read-address walk) on the range frozen from E129 (per cycle excluded by 0.001 W), but at this session's own scale every registered single-carrier reading is excluded (post hoc), and a walk-plus-A-path mix or the walk counted in address-bit toggles fits, each on equal per-op work in the two formats; one row removes 0.75 ± 0.08 W (Q138, aifoundry1 card 1, 600 MHz, ten passes)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 11, "int8
zeros' extra 0.61 W"**, the complaint this answers: with nothing issued, int8's TensorFMA loop costs 2.11 W over idle against fp32's 0.38 W on
aifoundry3 (E109) and 1.57 ± 0.21 W more than fp32's on this card (E124's Y1), and the item's open part is "where the 1.7 W goes among what int8
alone runs every cycle ... and the premise of E129's split". It builds on [Q136(c)](../2026-11-02-q136c-tima-bench/README.md) (the TIMA bench's
counts: TenC's reads, the TIMA controls, TenTMP's staging, the scratchpad's 64-bit A reads), [E129](../2026-11-02-e129-int8-noissue/README.md)
(this card: one A row removes 0.70 ± 0.42 W, V1 INCONCLUSIVE) and [E124](../2026-11-01-e124-int8-zeros-replicate/README.md) (this card's
frame and per-read ceilings).*

*Mon 2 Nov 2026 (week 45), Q138, lane a1c1-e148-int8-excess. Pre-registered in [`tools/claims-v3/e148/README.md`](../../../../tools/claims-v3/e148/README.md)
with [`predictions-e148.json`](../../../../tools/claims-v3/e148/predictions-e148.json), committed as **`19eb22a4`** at 22:10:00 PST and pushed by
`commit_lab.sh` before the claim (22:11:45 PST) and before any device opened (22:11:58). **aifoundry1 card 1** (`V3_DEVICE=1`, its own lock), release
1.4.0 (BL1 and BL2 0.22.0), after [E142](../2026-11-02-e142-blind5-card1/README.md) released it at 21:35:48. `ettelem config` was read 26 times under
card 1's lock with `timeout 10`, through E128's allow-list (the session's start, 22:11:58, and end, 22:45:56, and both ends of the stop-path test, the
smoke and every pass): **TDP 65 W, threshold 65 °C, 600 MHz, 499 mV in every read** (power state `low_power` 6 times, `managed_power` 20). **Nothing
was set and no WRITE was sent** (§ Device commands sent; `since_reset_ms` −1 in all 19,056 samples). **Card session 22:11:58–22:45:56 PST, 34.0
card-minutes of the 40 allowed**: the stop-path test 14802, the smoke 14801 and **ten passes, 14810–14819 (172–206 s each), all kept**. The card was
claimed at 22:11:45 by rewriting the day's one card post in `#community-lab` (message `1566837317765963987`) and released at 22:46:37 by rewriting it
again (§ How it ran).*

*Corrected after verification (a dated note, Mon 2 Nov 2026, about 23:45 PST; desk only: no card opened, no device command, nothing re-run, no
Modal). An independent verifier re-ran the pipeline on the committed raw passes (every scored file byte-identical), regenerated the frozen
predictions byte-identically at `19eb22a4`, recomputed every statistic by hand and confirmed that every command sent was a read. It found seven
faults in how the result was read, three major and four minor; none changes a measured number, a rule, a frozen prediction or a registered
verdict. Each is corrected in place, marked "corrected after verification, C<n>" or "added after verification, C<n>", and listed with the title's
old wording in [§ Corrections after verification](#corrections-after-verification-mon-2-nov-2026) at the end. The numbers they quote are printed by
[`posthoc/posthoc_e148.py`](posthoc/posthoc_e148.py) → [`posthoc/posthoc.txt`](posthoc/posthoc.txt) (sections 4–6, new; sections 1–3 print
exactly what they printed before) and [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt).
The main ones: **C1**, against the null "a second row changes nothing" the registered readings cut the out-of-sample error on a new shape by
about 0.02–0.06 W, not from 0.9 to 0.13 W (the bench's 0.9 W miss is its miss on N1, known since E129); **C2**, W2 excludes the A path as the
*sole* per-row carrier, and the registered two-term solve still gives it about 0.15 W; **C3**, W1's WALK rests on E129's wide frozen range, and at
this session's own N − N1 the registered walk count is excluded, as the A path and per cycle are (post hoc). The registration
([`tools/claims-v3/e148/`](../../../../tools/claims-v3/e148/README.md), `19eb22a4`), `scored.json`, `results.md`, the reductions and the raw
passes are unchanged.*

**In plain words.** With nothing issued, an int8 matmul loop on this chip still draws about 1.6 W more than the same loop in fp32. This morning one
row of A took 0.7 W of that away, which left open what the removed part follows: the accumulator memory's changing read address (the "walk"), or the
way int8 stages A. Two rows of A separate them, because the walk turns on while the A staging falls. **Two rows put back 0.16 W, so the A staging
cannot be all of the removed part, and the walk is the registered reading that holds, if the two formats spend the same energy per operation**
(measured only to ±63 pJ, which could carry the 0.16 W instead). But it holds only on the wide range frozen from this morning's three passes: at
this session's own scale the walk counted the registered way (reads at a new address) over-predicts the 0.16 W about twofold and is excluded, as
the A staging alone and a per-cycle cost are (post hoc). What fits this session's numbers is a mix, the walk plus some A staging (about 0.60 and
0.15 W of the 0.75 W), or the walk counted in address bits that change, a count chosen after the data (0.17 W predicted). More than half of the
excess, 0.88 W, stays at one row; whether that is work int8 does every cycle or one row's own A staging, no shape here separates *(corrected
after verification, C2, C3, C6: this said the A staging "is excluded as the carrier, and the walk is what holds", and "work int8 does every cycle
that no shape here separates")*.

## Results

**All ten passes kept on the registered primary** (E78's `reduce_e78.py` unchanged through `reduce_e148.py`: leakage frozen at 0.2414 W/°C, card 1's
launch-gap dips removed, 1–10 samples a pass, E78's run and pass gates, card 1's 65/65 config gate): 140 runs, none failing a gate, a median of one
heat a launch (at most two). The relaxed reduction keeps the same ten. ([`scored.json`](scored.json) › `n_passes`, `which_reduction_scores` =
"primary"; [`e148.json`](e148.json) › `passes_set_aside` = [])

1. **Two A rows put back D21 = N2 − N1 = +0.159 ± 0.096 W** (95% +0.063 to +0.256; ten passes, paired inside each). **W1 reads WALK**: the walk's
   frozen range (+0.118 to +0.474 W) overlaps it, the A path's (−0.681 to −0.170 W) and per cycle's (+0.026 to +0.062 W) do not. **The per-cycle
   exclusion is by 0.001 W** (D21's lower bound 0.0629 against the range's top 0.0619); under the leakage-`auto` arm (0.141 W/°C, fitted on the
   session's 91 runs) D21 is +0.141 ± 0.090 W and W1 reads INCONCLUSIVE (C and W consistent). **WALK rests on the W range frozen from E129's
   three-pass N − N1 (0.280–1.122 W): at this session's own N − N1 the registered walk count predicts D21 = 0.316 W and, like T and C, is
   excluded (post hoc, result 6)** *(added after verification, C3)*. **W2 RISES** in every arm: two rows cost int8 more than one, so **int8's A
   staging (TenTMP and the scratchpad's 64-bit A reads), which falls at two rows, is excluded as the sole per-row carrier** (W2's registered
   line); the registered two-term solve still gives it 3.43 ± 1.68 pJ a 64-bit A read, about 0.15 W of N − N1 (result 5), and only the post hoc
   toggle count removes it *(corrected after verification, C2: this said "is excluded as the per-row carrier")*.
   **Reading D21 as the walk assumes equal per-op work in the two formats**, E129's premise: both op rates fall by about a third from one row to two,
   so a per-op difference Δe enters D21 as about −3.4 × 10⁹ × Δe, and E129 measured Δe only to −4 ± 63 pJ (`one_row.e_op_diff_at_r1_rate_w`,
   −0.04 ± 0.62 W at the one-row rate), which allows +0.01 ± 0.21 W of D21. The A path's exclusion as the sole carrier holds at that allowance:
   D21 net of it, the walk's share, is about +0.15 ± 0.23 W (the two half-widths in quadrature; −0.09 to +0.38 W), still above T's range, which
   ends at −0.17 W, but not resolved from zero *(corrected after verification, C5: this said "+0.02 ± 0.21 W" and "+0.14 ± 0.23 W";
   [`posthoc/posthoc.txt`](posthoc/posthoc.txt) section 4)*. (`scored.json` › `rules.W1`, `rules.W2`; `scored-auto.json` › `rules.W1`; E129
   `scored.json` › `one_row`)
2. **N2, a shape no model was fitted on, against what each frozen reading predicted for it.** Measured, N2 = S(`m0r2.int8.zeros`) −
   S(`m0r2.fp32.zeros`) = **1.043 ± 0.087 W**. Predicted (this session's N1 plus each reading's frozen D21): the walk 1.180 W (error −0.137 W), per
   cycle 0.927 W (+0.115 W), the A path 0.458 W (+0.585 W); the bench at its own constants in the card's order 0.082–0.162 W (+0.88 to +0.96 W).
   **Only D21 was frozen:** N1 here is this session's measurement, so each reading's N2 error is its D21 error, and the bench's 0.9 W miss is its
   miss on N1 (its constants give N1 0.07–0.14 W against 0.884 W), known since E129 (its V2). Like for like, on D21 the null "a second row changes
   nothing" errs by +0.159 W and the bench's frozen D21 by +0.137 to +0.148 W; on N2 from what was frozen before the run, E129's N1 alone errs by
   +0.177 W, and E129's N1 plus the walk's or per cycle's D21 by −0.119 and +0.133 W (§ What it does to predicting power and heat;
   [`posthoc/posthoc.txt`](posthoc/posthoc.txt) section 6) *(added after verification, C1)*. (`scored.json` › `reported.N2_out_of_sample`)
3. **E129 replicates, now resolved** (T1 PASS ×2, Y1 PASS). With nothing issued, int8's sixteen-row loop costs **N = 1.631 ± 0.049 W** more than
   fp32's (E129 1.566, E124 1.567); with one A row **N1 = 0.884 ± 0.077 W** (E129 0.865 ± 0.357); so **one A row removes N − N1 = 0.747 ± 0.084 W**
   (E129 0.701 ± 0.421). V1 on this session alone is INCONCLUSIVE (N1's 0.807–0.960 W straddles N/2 = 0.815 W); **V1p, pooled with E129's three
   passes (13), reads PER-CYCLE**: N1 − N/2 = +0.071 ± 0.068 W, its lower bound +0.004 W, so more than half of the excess stays at one A row. Under
   leakage `auto` both read PER-CYCLE. (`scored.json` › `rules.T1`, `rules.Y1`, `rules.V1`, `rules.V1p`)
4. **The silicon keeps the RTL's schedule at two rows** (R6 PASS ×6). Every arm's cycles per op equal the frozen prediction, the bench's plus E109's
   7.75: **`m0r2` 96.0 (fp32) and 94.0 (int8)**, a schedule no card had run, the bench's 88.25 and 86.25 + 7.75 to the cycle; `m0` 544.001 / 318.001;
   `m0r1` 62.0 / 62.0. The smoke read the same. (`scored.json` › `rules.R6`; [`logs/session.log`](logs/session.log), the smoke lines)
5. **The registered two-term solve** (reported, no verdict) puts N − N1 and D21 on the two counts at once: **p_w = 75.5 ± 16.8 fJ a TenC read at
   a new address and p_t = 3.43 ± 1.68 pJ a 64-bit A read**. That p_t is 5.6 times the most any scratchpad read can cost on this card at fp32's own
   no-issue level (0.61 ± 0.13 pJ, E124 `extras.json` › `reported.read_ceiling_fp32_pj`), so the two-term reading needs int8's A staging to cost far
   more than a read. Its p_t is resolved from zero (95% 1.75–5.11 pJ): of N − N1 at sixteen rows it gives the walk 0.595 ± 0.132 W and the A path
   0.152 ± 0.074 W, and one row's own A staging 0.271 ± 0.133 W inside N1 ([`posthoc/posthoc.txt`](posthoc/posthoc.txt) section 5) *(added after
   verification, C2)*. (`scored.json` › `reported.two_term`)
6. **Post hoc, deciding nothing** ([`posthoc/posthoc.txt`](posthoc/posthoc.txt)): at this session's own N − N1, the walk counted as the registration
   counted it, reads at a new address (× 0.4225), predicts D21 = 0.316 W and is excluded (D21 minus it −0.156 ± 0.077 W). Counted in **TenC
   read-address bits that change** (the bench's `raddr_tog`: 7,680 an op at sixteen rows, 1.875 bits a change, and 512 at two rows, one bit a change;
   × 0.2254 a second), a count chosen after the data were seen, it predicts **0.168 W, consistent (−0.009 ± 0.085 W)**, with no A-path term. Its
   one-term price is **50.5 ± 5.7 fJ an address-bit toggle** (or 94.8 ± 10.6 fJ a read at a new address; E129's post hoc was 89). A per-cycle share
   on its own (× 0.0506 of N1) is excluded (+0.115 ± 0.098 W), and so is the A path on its own (+0.613 ± 0.136 W): **no registered single-carrier
   reading fits this session's own numbers**; what fits is the two-term mixture (by construction: two equations, two unknowns) or the toggle count,
   chosen after the data *(added after verification, C3)*. Three rows would test the toggle count with a gap of 0.16 of the walk's sixteen-row
   share (0.542 against 0.385), but at three rows the formats' op rates differ by 16%.

**What it changes.** Item 11 narrows on both of its open parts. **The per-row part:** one A row removes 0.75 ± 0.08 W, and a second row puts back a
fifth of that while int8's A staging falls below one row's, so the staging is excluded as its sole carrier (W2, every arm; the two-term solve still
gives it about 0.15 W of the 0.75) and TenC's read-address walk is the registered reading that holds (W1 WALK on the primary; the per-cycle
reading's exclusion rests on 0.001 W and fails under the leakage arm) *(corrected after verification, C2: this said "excluded as its carrier")*.
WALK rests on E129's wide frozen range: at this session's own N − N1 the walk counted as registered over-predicts D21 twofold and is excluded too,
so what the per-row part follows is a walk-plus-A-path mixture or the walk counted in address-bit toggles (post hoc), not yet a registered count
*(added after verification, C3)*. **The premise of E129's split** (equal per-op work in the two formats) is not tested further, and the walk's reading of D21 needs it too: a per-op
difference between the formats at E129's ±63 pJ could carry D21 instead. A run that measures each format's per-op work at one and two rows (a K = 8
partner for each, as E109's `m0k8`) would remove it. **The per-cycle part:** pooled over 13 passes, more than half of N
stays at one row (V1p PER-CYCLE, lower bound +0.004 W): about 0.88 W of int8's 1.63 W stays at one A row, whether as work it does every cycle
whatever the walk or as one row's own A staging (0.27 W of it under the two-term solve), and nothing here separates those, or TenC's reads as
such, the TIMA controls and the core *(corrected after verification, C6: this said "is work it does every cycle whatever the walk")*.

## What it does to predicting power and heat

*(Rewritten after verification, C1, C3 and C6. The first version's table and its summary are quoted in
[§ Corrections after verification](#corrections-after-verification-mon-2-nov-2026), C1.)*

**The term measured:** int8's no-issue floor, the part of an int8 matmul's power that no data and no issued micro-op sets, 1.63 W over fp32's on this
card at sixteen rows. Before E148 no model term carried it and its shape-dependence was unknown (E129's split INCONCLUSIVE). After E148 it has a
two-part form, **N(shape) ≈ N1 + (a per-row part)**: N1 ≈ 0.88 W stays at one A row (V1p; per-cycle work or one row's own A staging, not
separated), and the per-row part is 0.75 W at sixteen rows. **Which count the per-row part follows is not settled.** The registered count (TenC
reads at a new address), priced at this session's N − N1 (94.8 fJ a read), predicts the two-row point twofold too high; the walk counted in
address-bit toggles (50.5 ± 5.7 fJ a toggle) fits it, a count chosen after the data; the two-term mixture (75.5 fJ a new-address read plus
3.43 pJ a 64-bit A read) fits it by construction.

**Out-of-sample error, like for like.** What was frozen before the run is each reading's D21, the change a second row makes; this session's N1
is measured, so a reading's N2 error (this session's N1 plus its D21) is its D21 error ([`posthoc/posthoc.txt`](posthoc/posthoc.txt) section 6).

| predictor of D21 (measured +0.159 ± 0.096 W) | predicted D21 | error |
|---|---:|---:|
| null: a second row changes nothing | 0 | +0.159 W |
| the bench at its own constants, card order (Q136(c)'s pricing; frozen) | +0.011 to +0.023 W | +0.137 to +0.148 W |
| per cycle, registered C (frozen) | +0.044 W | +0.115 W |
| the walk in reads at a new address, at E129's N − N1, registered W (frozen) | +0.296 W | −0.137 W |
| the A path, registered T (frozen) | −0.425 W | +0.585 W |
| *post hoc:* the registered walk count at this session's N − N1 | *+0.316 W* | *−0.156 W* |
| *post hoc:* the walk in address-bit toggles at this session's N − N1 (count chosen after the data) | *+0.168 W* | *−0.009 W* |

Each error carries the measurement's ±0.096 W; the two post hoc rows' paired residuals are −0.156 ± 0.077 and −0.009 ± 0.085 W.

| predictor of N2 from what was frozen before the run (measured 1.043 ± 0.087 W) | predicted N2 | error |
|---|---:|---:|
| E129's N1 alone (a second row changes nothing) | 0.865 W | +0.177 W |
| E129's N1 + the bench's frozen D21 | 0.877–0.888 W | +0.155 to +0.166 W |
| E129's N1 + per cycle's D21 (C) | 0.909 W | +0.133 W |
| E129's N1 + the walk's D21 (W) | 1.162 W | −0.119 W |
| E129's N1 + the A path's D21 (T) | 0.440 W | +0.603 W |
| the bench at its own constants, all of N2 | 0.082–0.162 W | +0.88 to +0.96 W |

**So the registered readings cut the error of predicting a new shape's floor by about 0.02–0.06 W against the null** (on D21 from 0.16 to
0.12–0.14 W; on N2 from 0.18 to 0.12–0.13 W), **not from 0.9 to 0.13 W**: the bench's 0.9 W is its failure to price N1 (its constants give N1
0.07–0.14 W against 0.884 W), known since E129 (V2). The walk in the registered count, priced at this session's own N − N1, does no better than the
null (−0.156 against +0.159 W); only the toggle count, chosen after the data, does (−0.009 W), and it needs a registered test (three rows with
K = 8 partners, result 6). Every row but the bench's assumes equal per-op work in the two formats (result 1). **Heat** follows power through card
1's die rise per board watt (M7's H2, 0.1151 °C/W): a 0.16 W difference is 0.02 °C, below what the 4.5 s readout resolves, so E148 scores power
only.

## The arms (primary reduction)

D is over the format's zeros (interpolated between the pass's three zeros anchors) and S over the idle bracket, ± 95% over 10 passes (t 2.262).
"Cycles" is the median over the kept runs. Source: `e148.json` › `items`, `per_pass`; [`readme-numbers.txt`](readme-numbers.txt).

| item | cycles | ops/s (10⁹) | D, W | S, W |
|---|---|---|---|---|
| `fp32.zeros` | 546.001 | 1.1209 | 0 | +1.629 ± 0.026 |
| `int8.zeros` | 318.001 | 1.9248 | 0 | +2.236 ± 0.023 |
| `anchor_pi` | 546.001 | 1.1208 | +8.138 ± 0.024 | +9.846 ± 0.071 |
| `m0.fp32.zeros` | 544.001 | 1.1251 | −1.529 ± 0.058 | +0.132 ± 0.044 |
| `m0.int8.zeros` | 318.001 | 1.9247 | −0.441 ± 0.053 | +1.762 ± 0.048 |
| `m0r1.fp32.zeros` | 62.0 | 9.8640 | −0.386 ± 0.058 | +1.287 ± 0.052 |
| `m0r1.int8.zeros` | 62.0 | 9.8646 | −0.046 ± 0.032 | +2.171 ± 0.073 |
| **`m0r2.fp32.zeros`** | **96.0** | 6.3751 | −0.789 ± 0.062 | **+0.908 ± 0.054** |
| **`m0r2.int8.zeros`** | **94.0** | 6.5108 | −0.319 ± 0.043 | **+1.951 ± 0.059** |

Idle 33.02 W. Going from one row to two lowers both formats' level, fp32's by 0.379 ± 0.063 W and int8's by only 0.220 ± 0.090 W: B's traffic falls
with the op rate in both, and int8 alone adds the walk back. (`scored.json` › `stats.r2_over_r1_fp32`, `stats.r2_over_r1_int8`)

## The registered rules against the data

`scored.json` is `score_e148.py`'s output with `predictions-e148.json` on the primary, chosen by the set-aside rule over the relaxed reduction. The
arms: dips kept, leakage `auto`, and the relaxed reduction.

| rule | registered line | **E148 (primary, 10 passes)** | dips kept | leakage `auto` (0.141 W/°C) | relaxed |
|---|---|---|---|---|---|
| **W1** (primary) | D21's 95% interval against the frozen ranges W, T, C | **WALK** (+0.159 ± 0.096; W consistent, T and C excluded) | WALK | **INCONCLUSIVE** (C, W; +0.141 ± 0.090) | WALK |
| W2 | D21's lower bound > 0 | **RISES** (+0.063) | RISES | RISES | RISES |
| R6 | \|measured − predicted\| ≤ 2 cycles | **PASS ×6** (every difference ≤ 0.001) | PASS ×6 | PASS ×6 | PASS ×6 |
| Y1 | N's lower bound ≥ 0.84 W | **PASS** (+1.631 ± 0.049) | PASS | PASS | PASS |
| V1 | N1 against N/2 | **INCONCLUSIVE** (0.884 ± 0.077 against 0.815) | INCONCLUSIVE | PER-CYCLE | INCONCLUSIVE |
| V1p | N1 − N/2, pooled with E129's 3 passes | **PER-CYCLE** (+0.071 ± 0.068, 13 passes) | PER-CYCLE | PER-CYCLE | PER-CYCLE |
| T1 | N, N1 within 0.5 W of E129's | **PASS ×2** (1.631 vs 1.566; 0.884 vs 0.865) | PASS ×2 | PASS ×2 | PASS ×2 |

**One verdict moves with an arm: W1** (and V1). The dips-kept arm reproduces every N, N1, N2 and D21 exactly; leakage `auto` lowers D21 by 0.018 W
and brings the per-cycle range back inside its interval. The registered primary carries the verdict, and the margin is stated where it is used.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | committed and pushed before the claim and the first launch | `19eb22a4` committed 22:10:00 PST and pushed by `commit_lab.sh` before the claim (22:11:45); first device process 22:11:58 (the opening config read) |
| desk | the bench run and its identity check; the predictions; the self-test; the preflight; `bash -n`; the reducer's mechanical run. On the box: `check_e148.py`, the preflight, `bash -n`, a stub queue, `V3_DRY` of the stop test, smoke and pass 14810 | [`selftest.txt`](../../../../tools/claims-v3/e148/selftest.txt) PASS (A–C); [`dmcmd-audit.txt`](../../../../tools/claims-v3/e148/dmcmd-audit.txt) GO; the box's checks 22:08:02–22:09:25 PST ([`logs/desk/`](logs/desk/)) |
| stop test | before the smoke: the die, board and watcher stops each exit 6 on a live sample, no launch | 22:11:59–22:12:05: die stop on a sample read 0.102 s after it was taken, board 0.084 s, watcher 0.031 s; rc 6 three times ([`aifoundry1-c1/e148-stoptest/p14802/`](aifoundry1-c1/e148-stoptest/p14802/)) |
| smoke | seven items, 2 s runs; E109's gate | 22:12:14–22:12:57; every item 6 launch records, all `ok`, `tensor_errors` 0: SMOKE-GATE PASS; `m0r2` at 96.0 and 94.0 cycles |
| passes | 14810–14819 as the budget allows; about 600 s each expected | **all ten**, 172–206 s each (rc 0); the queue's rule ran out of passes, not budget (22:45:56, T0 + 2,038 s, limit T0 + 2,250 s) |
| kept | the primary carries if ≥ 3; else the relaxed one | **10 of 10** by E78's gates; the relaxed reduction keeps the same 10 |
| runs | 14 a pass | 140 of 140 ran and all are kept; a median of 1 heat a launch, at most 2 |
| stops | `build/e148/STOP`; board ≥ 66 W or a minion-shire reading ≥ 72 °C on a live sample (before every launch, every 0.1 s while waiting, and by the in-run watcher); run_e78's `--max-c 72`; another user's device process or this card's lock | none fired. In all 19,056 samples: board at most **59.79 W** (stop 66), the hottest-shire field 65 °C throughout (its latch; stop 72), the shires' mean 51–61 °C, 600 MHz, `since_reset_ms` −1 ([`telemetry-max.json`](telemetry-max.json)). The field named `pmic` (at most 61 °C) is the shire mean, not the PMIC's temperature: it equals `minshire[0]` in 19,050 of 19,056 samples, the rest by ±1 ([`corrections-numbers.txt`](corrections-numbers.txt)). No PMIC temperature is read on this build, so the margin is the board's 59.79 W, the shire mean's 61 °C and the latch's 65 °C *(corrected after verification, C4: this said "the PMIC's reading at most 61 °C")*. The in-run watcher computes a line's age but does not refuse a stale one; between launches run_e78 stops on a line older than 3 s, so a dead sampler could go unseen for at most one 4 s run, and no gap between two samples exceeded 101 ms in any block *(added after verification, C7)* |
| budget | at most 40 card-minutes, first config read to last; no session after 23:00 PST; passes end by 23:45 PST | **34.0** (22:11:58–22:45:56); claim to release 34.9 min (22:11:45–22:46:37) |
| config | read at both ends, never set | TDP 65 W, 65 °C, 600 MHz, 499 mV in all 26 reads |

## Departures (dated)

- **Mon 2 Nov 2026, the passes ran three times faster than registered, so all ten fit.** The registration projected 600 s a pass from E129's cool
  morning (536–663 s, a median of 5–8 heats a launch). This session's die stayed warm, a median of one heat a launch, and the passes took 172–206 s.
  The queue's budget rule, unchanged, started every pass it had (14810–14819) and ended at T0 + 2,038 s, inside its T0 + 2,250 s limit. Recorded,
  not amended: no rule depended on the number of passes beyond the registered minimum of three.
- **The day's post's plan read lagged at the release.** `delete_msg.mjs --plan` gave the post's text without a clause that a later lane had added
  (aifoundry3's), so `edit_replace.mjs` with `EXPECT_TEXT` refused (exit 7), as its rule says; the release text was rebuilt from what the edit box
  held, dropping only this card's clause, and saved (§ How it ran).

## How it ran

22:08:02–22:09:25 PST, before the commit, on the box with no device opened: Python 3.12.3; `check_e148.py` HARNESS OK (25 files: E129's 20 reused
files and the 5 binaries, every one byte-identical to E129's freeze); the preflight GO; every script parsed; the queue's budget rule on a 1 s stub;
`V3_DRY` of the stop test, the smoke and pass 14810 ([`logs/desk/`](logs/desk/)). `et-who`: no process held a device node or card lock. 22:10:00 the
registration committed (`19eb22a4`); `commit_lab.sh` pushed it before the claim. 22:11:45 the claim: the day's one card post, which read
`<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, was rewritten to
`<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry1 card 1 for 1 h, until ~23:11 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
(`edit_replace.mjs` with `EXPECT_TEXT`, dry run, save, read back, under the discord lock). 22:11:58 `session_e148.sh` started detached on the box
(`setsid nohup`, T0 = the launch): the 23:00 gate; `check_e148.py` (HARNESS OK); the preflight (GO); `et-who` (no holder); the opening config read;
the stop-path test 14802; the smoke 14801 and its gate; `queue_e148.sh`; the closing config read at 22:45:56; `et-who` (no holder). The other lab user's
idle logins were present throughout; no other user's process, device node or card lock was seen (E78's departure D1 for `aifoundry1-c*`).

Each pass ran E78's two burn-in runs of π, then 14 registered runs: π first and last, each format's zeros once in each of three segments, and E148's six
arms dealt round-robin with seed `E148|aifoundry1-c1|<pass>`. Each run launched at a 58 °C die reading after a 59 °C preheat, with 2 s quiet and 4 s
FMA runs on all 1,024 minions. The waits on the box were four bounded `ssh … 'bash -s'` calls that read the session's log lines only; nothing was
copied off the box until the session had ended.

22:46:37 the release: the post then held three clauses (aifoundry2's, this card's and aifoundry3's, added meanwhile; the plan's cached source lagged,
so `EXPECT_TEXT` refused with exit 7 and the text was rebuilt from the edit box). It was rewritten to the two still held,
`<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry3 for 1 h, until ~23:40 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`,
every word of theirs kept, and the rendered post read the same at the save. 22:46:4x the data were collected to the Intel
([`collect_e148.sh`](../../../../tools/claims-v3/e148/collect_e148.sh), and the box's desk checks into [`logs/desk/`](logs/desk/)), then reduced and scored
with [`pipeline_e148.sh`](../../../../tools/claims-v3/e148/pipeline_e148.sh) (six seconds). `reduce_e148.py` checks the 20 reused files' sha256 against
the freeze before it reads anything.

## Device commands sent

Every command the run sent to card 1, classified at registration from the source of its running build: release 1.4.0, BL1 and BL2 0.22.0,
et-platform **`836a4ab`** (the version-matched revision of Q136(w)'s table, E129's dated note C1 and E142's audit of the same command set).
Q136(w)'s checker on every file the session runs read **GO: 32 send sites, 0 disallowed, no WRITE allowed**, at the desk
([`dmcmd-audit.txt`](../../../../tools/claims-v3/e148/dmcmd-audit.txt)) and on the box before the first device opened
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt), 22:11:58 PST). **The run sent no WRITE** (`since_reset_ms` −1 in every sample).

| # | sent by | command (id) | class (BL2 0.22.0, `836a4ab`, under `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| 1 | `ettelem config` (session start and end, each block's start and end) | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | READ: `thermal_power_monitor.c:339` → `thermal_pwr_mgmt.c:613`, a copy from SP RAM |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | READ: `:438` → `:665`, SP RAM |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23) | READ: `:48` → `:551`, SP RAM |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | READ: `performance.c:41` → `io_pll.c:907-960`, PLL register reads |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32) | READ: `thermal_pwr_mgmt.c:1142`, PVT reads and two `pmic_get_voltage` I2C register reads (allowed by the owner's rule of 2 November 2026) |
| 6 | `ettelem sample` (the 10 Hz sampler; `lib.sh`'s 1 s die reads) | `DM_CMD_GET_MODULE_POWER` (33) | READ: `:984`, SP RAM |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60) | READ: `performance.c:404` → `thermal_pwr_mgmt.c:2780`, SP RAM, no reset |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | READ: `:732`, PVT sensor reads |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31) | READ: `:1010`, nine `pmic_get_voltage` register reads (allowed) |
| — | `lib.sh:154`'s forwarded arguments (a possible `--reset-ms` = `DM_CMD_SET_STATS_RUN_CONTROL`, 62) | WRITE, conditional: **never sent** (the reviewed exception: `block_e148.sh:104` passes the file and the duration only, and `ettelem_guard.sh` refuses `--reset-ms`) | |
| — | `lib.sh`'s `drain_mgmt` (`dev_mngt_service`) | **never sent**: replaced by a refusal in `block_e148.sh` | |
| — | `sparsity_host` (E109's `build/e109`; E78's heater `build/sparsity`) | the Master Minion's device-ops: DMA writes and reads of device DRAM, kernel launches, an abort on a 6 s overrun: the workload, not a device-management command | |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads; they open no device node | |

Not sent: the statistics reset, the SP log level (67), `sptrace`, `dev_mngt_service`, the firmware-revisions query (14), a residency read, any
governor, TDP, threshold, clock or voltage set, any reset.

## What this cannot say

- **RTL, not silicon, and a later revision.** The walk and the A path are counted in core-et's later revision (Erbium), not the ET-SoC-1's own RTL;
  the silicon matching the bench's cycles (R6) shows the schedule carries over, not the energy of each event.
- **The per-cycle candidates stay together.** No shape separates TenC's reads as such, the TIMA controls and the core: all three run every int8
  cycle at the same rate in every arm here (and TenC's reads cancel in the card's order if fp32 reads TenC too, Q136(c) result 3).
- **W1's per-cycle exclusion is 0.001 W wide** and does not survive the leakage-`auto` arm; W2 (the A path's exclusion) survives every arm.
- **Equal per-op work in the two formats is assumed, not measured here.** No arm of E148 measures each format's per-op work; E129's estimate
  (Δe = −4 ± 63 pJ an op) allows ±0.21 W of D21, so the walk's share of D21 is not resolved from zero without the premise (result 1).
- **The readings are single-carrier readings.** Each puts all of E129's N − N1 on one event. The reported two-term solve fits both counts with two
  equations and no residual; the post hoc toggle count fits one count, chosen after the data. Neither is a test. At this session's own N − N1 all
  three registered readings are excluded (post hoc, result 6), so W1's WALK holds on E129's wide frozen range only *(added after verification,
  C3)*.
- **Two rows are not exactly equal-rate.** int8 runs 94 cycles an op and fp32 96, so int8 does 2.1% more ops a second. At Q136(c)'s fp32-level
  bounds that buys int8 at most about 0.02 W of TenB writes and 0.01 W of scratchpad bits (`predictions-e148.json` › `bench_per_s_card_order`), and
  at E129's per-op price (about 80 pJ an op) about 0.01 W: below D21's interval.

## Files

`e148.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the primary reduction); `scored.json`, `results.md`, `score.log` (`score_e148.py`; the set-aside rule
chose the primary); `e148-relaxed.json`, `scored-relaxed.json`, `results-relaxed.md` and logs (always run, not needed); `e148-dipskept.json`,
`e148-auto.json` with their `scored-*`, `results-*`, `runs-*`, `reduce-*` (the two arms); `readme-numbers.txt` (every number above, printed by
[`numbers_e148.py`](../../../../tools/claims-v3/e148/numbers_e148.py), written after the run); `telemetry-max.json`
([`telemetry_max_e148.py`](../../../../tools/claims-v3/e148/telemetry_max_e148.py), E142's, after the run); `posthoc/` (post hoc, deciding nothing:
`posthoc_e148.py` and its `posthoc.txt`/`posthoc.json`, whose sections 4–6 were added after verification, and `bench_ladder_e148.py` with
`bench-ladder.json`, the bench's walk counts at 1–16 rows); `corrections-numbers.py` → `corrections-numbers.txt` (after verification: the `pmic`
field against the shire mean, the margins, the watcher's test and run_e78's stale limit, the largest gap between samples);
`aifoundry1-c1/e148/p1481[0-9]/` (every pass's raw data: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_start.json`,
`config_end.json`, `manifest.txt`, `binaries.sha256`, `code.sha256`, `gen.sha256`, `configs.json`, `plan.json`, `run.log`, `block.json`);
`aifoundry1-c1/e148-smoke/p14801/`; `aifoundry1-c1/e148-stoptest/p14802/` (with `STOP.die`, `STOP.board`, `STOP.watch`, `stoptest.rc`); `logs/` (the
session, its two config reads with their times, the queue, the preflight, `binaries.sha256`, `T0`; `logs/desk/`, the box's checks before the claim).
The registration and code are in [`tools/claims-v3/e148/`](../../../../tools/claims-v3/e148/README.md).

Rerun from the repo root: `bash tools/claims-v3/e148/pipeline_e148.sh <out dir> docs/reports/data/2026-11-02-e148-int8-excess/aifoundry1-c1/e148/p1481[0-9]`
(needs `uv` for numpy). Post hoc: `python3 docs/reports/data/2026-11-02-e148-int8-excess/posthoc/posthoc_e148.py`. Corrections:
`python3 docs/reports/data/2026-11-02-e148-int8-excess/corrections-numbers.py`.

## Blog sentences, each with its baseline, its card and its source

*Any line about the RTL is about its later revision (Erbium, core-et), not the ET-SoC-1's own.*

- An int8 matmul loop with nothing to multiply still draws 1.63 W more than the same loop in fp32 on this chip, and giving it a single row of A takes
  0.75 ± 0.08 W of that away, measured over ten independent passes. [aifoundry1 card 1, 600 MHz; `scored.json` › `stats.N`, `stats.N_minus_N1`]
- Adding a second row puts 0.16 W back, while the way int8 stages A falls below one row's: so the staging cannot be all of the cost. If the two
  formats spend the same energy per operation, the accumulator memory's changing read address is the registered reading that holds, but only on
  the wide range frozen from the morning's three passes: at this session's own scale it fits only mixed with some staging (about 0.15 of the
  0.75 W) or counted in the address bits that change, a count chosen after the data. [aifoundry1 card 1; `scored.json` › `rules.W1`, `rules.W2`,
  `reported.two_term`; `posthoc/posthoc.txt` sections 1 and 5; the premise, E129 `scored.json` › `one_row`] *(corrected after verification, C2,
  C3: this said "so the staging is not what costs" and "is the reading that holds")*
- The open RTL predicted the two-row loop's timing to the cycle on silicon it had never been run on: 96 cycles an op in fp32 and 94 in int8.
  [aifoundry1 card 1; `scored.json` › `rules.R6`]
- Frozen before the run, the readings predicted the second row's 0.16 W change to within 0.12–0.14 W, against 0.16 W for assuming no change at
  all: a gain of 0.02–0.06 W. The simulation's own constants missed the two-row excess by 0.9 W because they miss its one-row level, as the
  morning's run had shown. [aifoundry1 card 1; `posthoc/posthoc.txt` section 6; `scored.json` › `reported.N2_out_of_sample`] *(corrected after
  verification, C1: this set the readings' 0.12–0.14 W miss on the change against the constants' 0.9 W miss on the whole excess)*
- Counting the accumulator address's changing bits rather than its changes, a count chosen after the data, prices the walk at about 50 fJ a bit and
  predicts the second row's 0.16 W to 0.01 W; a run at another row count would test it. [aifoundry1 card 1; `posthoc/posthoc.txt`]
- More than half of the excess, about 0.88 W, stays at one row of A: work int8 does every clock cycle, or that one row's own staging; no shape
  tried here separates them. [aifoundry1 card 1, E129 and E148 pooled, 13 passes; `scored.json` › `rules.V1p`; `posthoc/posthoc.txt` section 5]
  *(corrected after verification, C6: this said "work int8 does every clock cycle whatever the address does")*

## Corrections after verification (Mon 2 Nov 2026)

An independent verifier (lane `verify-a1c1-e148-int8-excess`, about 23:00–23:30 PST) re-ran the pipeline on the committed raw passes (every
scored file byte-identical), regenerated the frozen predictions byte-identically at `19eb22a4`, recomputed every statistic by hand, re-read every
send site and its handler at et-platform `836a4ab`, and checked the registration's order, the stops and the day's post. Its verdict: the run holds,
with fixes to how it is read. The corrections below (desk only, about 23:45 PST) change no measured number, rule, frozen prediction or registered
verdict. Their numbers are printed in [`posthoc/posthoc.txt`](posthoc/posthoc.txt), sections 1 and 4–6, and
[`corrections-numbers.txt`](corrections-numbers.txt). The title said: "the A path is excluded as its per-row carrier; with equal per-op work in the
two formats, TenC's read-address walk is the registered reading that holds (W1 WALK, per cycle excluded by 0.001 W)" (C2, C3).

- **C1 (major): the out-of-sample error compared unlike predictors.** § What it does to predicting power and heat said "the registered readings
  predict a new shape's floor to about 0.12–0.14 W (of 1.04 W), against the bench's 0.9 W", from a table headed "predictor, frozen before the
  run": the bench at its own constants, card order, 0.08–0.16 W (+0.88 to +0.96 W); per cycle 0.927 W (+0.115 W); the walk at E129's N − N1
  1.180 W (−0.137 W); the A path 0.458 W (+0.585 W); post hoc, the walk in toggles 1.052 W (−0.009 W). Two things were wrong. Each reading's N2
  there is this session's measured N1 plus a frozen D21, so only D21 was frozen and the N2 error is the D21 error (posthoc section 6c). And the
  bench's row priced all of N2 from its constants, so its 0.9 W miss is its miss on N1 (0.07–0.14 W against 0.884 W), which E129's V2 had already
  shown. Like for like, the null "a second row changes nothing" errs by +0.159 W on D21 and the bench's own frozen D21 by +0.137 to +0.148 W;
  from what was frozen before the run, E129's N1 alone predicts N2 to +0.177 W, and E129's N1 plus the walk's or per cycle's D21 to −0.119 and
  +0.133 W. So the registered readings gain about 0.02–0.06 W over the null, and the walk in the registered count, priced at this session's own
  N − N1, gains nothing (−0.156 against +0.159 W). The section is rewritten with a D21 table and an N2 table; result 2 and blog sentence 4 are
  corrected to match. The kinds page's prediction table has no E148 row yet; one added later should read the same way.
- **C2 (major): "excluded as the per-row carrier" dropped W2's word "sole".** The registered line reads "RISES (two rows cost int8 more than one:
  the A path is excluded as the sole per-row carrier)" (`predictions-e148.json` › `rules.W2.verdicts`). The registered two-term solve, reported,
  still prices the A path at 3.43 ± 1.68 pJ a 64-bit A read, resolved from zero (95% 1.75–5.11): 0.152 ± 0.074 W of N − N1 at sixteen rows, and
  0.271 ± 0.133 W inside N1 (posthoc section 5). Only the post hoc toggle count fits with no A-path term, so the data do not separate a zero share
  from about a fifth of the per-row part. The title, the plain words, result 1, What it changes and blog sentence 2 now say "sole" or "cannot be
  all of it".
- **C3 (major): the walk was presented as holding.** W1's WALK is the registered verdict and it is correct, but it rests on the W range frozen from
  E129's three-pass N − N1 (0.280–1.122 W). At this session's own N − N1 (0.747 ± 0.084 W) the registered walk count predicts D21 = 0.316 W and
  is excluded (D21 minus it −0.156 ± 0.077 W), as T (+0.613 ± 0.136 W) and C (+0.115 ± 0.098 W) are (posthoc section 1): no registered
  single-carrier reading fits this session's own numbers. What fits is the two-term mixture (by construction; about 0.60 W of walk and 0.15 W of
  A path) or the walk counted in address-bit toggles, a count chosen after the data. The title, the plain words, results 1 and 6, What it changes,
  What it does to predicting power and heat, What this cannot say and blog sentence 2 now say so. The item-11 wording handed to the integration
  lanes says that E148 narrows the item, as § What it changes does, not that it answers it.
- **C4 (minor): "the PMIC's reading at most 61 °C".** At `836a4ab`, `get_module_current_temperature` fills the field named `pmic` from the minion
  shires' PVT average (`thermal_pwr_mgmt.c:732-745`; [14-card-behaviour.md](../../../findings/14-card-behaviour.md), the `temp_c.pmic` row; E127
  C5, E128 C6, E142 C3). Here it equals the shire mean in 19,050 of 19,056 samples and differs by ±1 in the other six (corrections-numbers.txt).
  No PMIC temperature was read, so it is no over-temperature margin: the margin is the board's 59.79 W (stop 66), the shire mean's 61 °C and the
  hottest-shire latch's 65 °C (stop 72). The stops row is corrected.
- **C5 (minor): the premise allowance.** Result 1 said a per-op difference "allows +0.02 ± 0.21 W of D21" and put the walk's share at "about
  +0.14 ± 0.23 W", hand arithmetic in no committed file. From the committed inputs (E129's per-op difference −3.9 ± 63.3 pJ, int8's op-rate
  change −3.358 × 10⁹ a second) it is +0.013 ± 0.213 W, and D21 net of it is +0.146 ± 0.234 W (−0.087 to +0.380). That is still above T's range,
  which ends at −0.170 W, so the A path's exclusion as the sole carrier holds at the allowance, while the rise net of it is not resolved from
  zero. It is now computed in posthoc section 4.
- **C6 (minor): "work int8 does every clock cycle".** V1p measures only what stays at one row. N1 still holds one row's A staging and any other
  one-row cost (0.27 W of A path under the two-term solve), so "every clock cycle" is one reading of it, not a measurement. The plain words, What
  it changes, What it does to predicting power and heat and blog sentence 6 now say "stays at one row", with per-cycle work and one row's A
  staging as the candidates.
- **C7 (minor): the in-run watcher has no stale-line test.** `run_e148.py`'s `_check_line` (lines 46–68, E142's) computes a line's age and only
  prints it (corrections-numbers.txt), so a sampler that died mid-run would leave the watcher, and the host program's STOP check it feeds, reading
  the last line. Between launches run_e78's `reading()` stops on a line older than 3 s (`--stale-s`), so the exposure is at most one run (4 s,
  under `timeout 10`). It did not happen here: the largest gap between two samples was 101 ms in every block. The registered runner is unchanged;
  the next runner that copies this watcher (E142's and E145's line) should make `_check_line` return a stop for a line older than about 1 s.
