# E68 — the stage map: which pipeline stage spends a flipped bit's energy (Q128(b), aifoundry2, 26 Oct 2026)

Pre-registration, predictions and amendments A1–A6: [`tools/claims-v3/sm/README.md`](../../../../tools/claims-v3/sm/README.md),
commit `b88c6bdc`, pushed at 21:0x PDT before the first measured launch at 21:11:45. Request Q128(b). Card
aifoundry2, claimed in `#community-lab` at 21:09 PDT (message `1564491254660595715`).

## What it measures, and why it can

E60 and E65 priced a flipped operand bit at the board. Nothing had said **where in the 7-stage pipeline** that
energy goes, so the gate-level stage splits of Q126(d) and Q126(e) had never met the hardware.

The lever is exact arithmetic, not a model: **an fp32 multiplier never sees a sign or an exponent.** The Booth
recoder reads *a*'s significand and the rows are 0, ±b, ±2b in *b*'s significand; the signs meet in one XOR and
the exponents in one small adder, both outside the tree. So an item whose two alternating B words share their
significand drives **bit-identical switching** through the Booth rows, the Wallace tree, its register and the
product adder — f1 and f2 frozen by construction — while f3 (align), f4 (add + leading-one), f5 (normalise) and
f6 (round) see two different results every cycle. The RTL bench confirms it rather than assuming it: `sm_sgn`,
`sm_e1`, `sm_e16`, `sm_e64` and `sm_pi_sgn` show **exactly 0** toggles in every tree-only module above their own
zero, and `sm_sgnlo`'s stage vector equals `sm_lo12`'s plus `sm_sgn`'s to the last toggle in every column.

## The session

41 passes, 22:30:20 PDT back to 21:11:45, through E60's `hl/block.sh` with `HL_EXPN=sm`: 13 items a pass,
`anchor_pi` first and last, the order reshuffled per pass, every item on **512 minions at 800 MHz**, 4 s a run,
launched at 58 °C after 59 °C, under the card lock with `timeout 10` on every process.

**574 runs, 453 kept.** Every kept run held 800 MHz throughout its window and the highest kept board reading was
**51.1 W**, far under the governor's ~65 W limit — the 512-minion sizing did its job. 121 runs were dropped by
the registered clock gate: this card idles at 600 MHz and the governor raises it during the launch, so a run
whose [t₀+1 s, t₀+3 s) window still holds the ramp is not a 800 MHz measurement (its voltage gate fires on the
same runs). **Two passes were aborted and restarted, and both are published here** as non-ok passes:
`aifoundry2/sm/p1.attempt-1793074293` (21:10:12, 72 run records over 6 items, killed at 21:11:22 by a
`USER: unbound variable` fault in `lib.sh`, which reads `$USER` under `set -u` in a tmux session started
without it) and `aifoundry2/sm/p8.attempt-1793075288` (21:26:00, 96 run records, killed by hand by this
session — amendment A5, which named only this one). Both carry `"status":"failed","note":"signal"`, and
neither can reach a number: `reduce_sm.py`'s `gather` reads only directories named `p` followed by digits,
so an `attempt` directory is skipped before any gate runs. The 41 scored passes are `p1`–`p41`.

## Prices

Registered `dP_W` (per-pass difference from the item's own zero, leakage-corrected at A1's 1.508 W/°C from 433
kept runs), with the per-flipped-bit price in E60's unit (A6).

🛑 **The leakage slope is the one number in this reduction not measured on this experiment's own data, and it
moves every price.** A1's `--leak auto` estimator returned **1.508 W/°C**; E66 measured this card's idle
leakage the same night, on the same card, over the band E68 ran in, at **0.296 W/°C** (51–58 °C, rms 0.116 W,
2,248 samples) and 0.311 W/°C over 51–67 °C — **5.1× smaller**. Every price is therefore given at both, and
the second is the better-supported one (A7). The registered scoring stays at A1's slope, as registered.

| item | what moves | passes | dP (W) at A1's 1.508 | fJ/bit at A1's 1.508 | dP (W) at E66's 0.296 | fJ/bit at E66's 0.296 |
|---|---|---:|---:|---:|---:|---:|
| `sm_lo12` | f1/f2, mantissa 0–11 | 24 | 4.312 ± 0.101 | 117.5 ± 2.8 | 4.987 ± 0.098 | **135.9 ± 2.7** |
| `sm_hi12` | f1/f2, mantissa 11–22 | 22 | 6.352 ± 0.156 | 173.3 ± 4.3 | 7.127 ± 0.120 | 194.4 ± 3.3 |
| `sm_sp12` | f1/f2, 12 bits spread | 23 | 6.870 ± 0.138 | 187.4 ± 3.8 | 7.932 ± 0.144 | 216.3 ± 3.9 |
| `sm_sgn` | **f3–f6 only** | 25 | 0.548 ± 0.111 | 179.3 ± 36.3 | 0.495 ± 0.085 | **161.8 ± 27.7** |
| `sm_e1` | f3–f6 only, shift 1 | 25 | 0.617 ± 0.141 | 201.9 ± 46.1 | 0.683 ± 0.113 | 223.3 ± 37.0 |
| `sm_e16` | f3–f6 only, shift 16 | 25 | 0.345 ± 0.097 | 112.8 ± 31.7 | 0.376 ± 0.084 | 123.2 ± 27.6 |
| `sm_e64` | f3–f6 only, saturating | 24 | 0.863 ± 0.098 | 282.5 ± 32.0 | 0.844 ± 0.095 | 276.4 ± 31.0 |
| `sm_sgnlo` | both | 24 | 4.756 ± 0.116 | 119.7 ± 2.9 | 5.379 ± 0.097 | 135.4 ± 2.4 |
| `sm_pi_sgn` | f3–f6 only, busy partner | 25 | 0.383 ± 0.120 | 125.3 ± 39.3 | 0.451 ± 0.132 | 147.6 ± 43.2 |

The busy items (whose window heats most) move 16 %; the frozen-tree items move the other way and by less.
Full table at eight slopes, with both fits: [`leak-sensitivity.txt`](leak-sensitivity.txt).

**The ladder reproduces to about 10 %, and the earlier claim that it reproduced exactly was an artefact of
the leakage slope** (corrected here; the first version of this file, and A6, got the comparison wrong — A7).
Two things were wrong with it. First the attribution: **116.7 and 129.9 fJ are both E60's `aifoundry3` card at
600 MHz**, its quiet (A = 1.0) and busy (A = π) ladders (`03-experiments.md` §E60; `hl.json` `lq`/`lb`) —
not aifoundry1 at 800 MHz, and 129.9 is not E65's. Second, the comparison that matters was never made:
E60 ran **this same card**, aifoundry2 at 800 MHz, and read **121.3 ± 0.6 fJ** per designed flipped bit.

Against that, corrected at the same leakage slope E60 itself fitted on this card (0.442 W/°C), E68 reads
**133.7 ± 2.5 fJ against E60's 121.3 ± 0.6 — about 10 % higher**, with a 12-bit mask instead of single bits
and half the minions. At A1's 1.508 W/°C it reads 117.5, 3 % *below* E60; the apparent bullseye on "116.7"
was a coincidence of quoting the wrong card against an over-corrected price. The defensible statement is
that **a flipped mantissa bit costs 118–136 fJ at the board on this card, about 10 % more than E60 measured
on it when both are corrected alike** — a reproduction across experiments and operand designs, not an
identity, and the leakage correction is a larger uncertainty than the difference between the two cards.

**And a bit that never enters the multiplier costs about as much, per bit, as one that does.** `sm_sgn` is
**161.8 ± 27.7 fJ** per flipped bit against `sm_lo12`'s 135.9 ± 2.7 at E66's measured slope, with **zero**
tree toggles — a difference of 25.9 ± 27.8 fJ, i.e. the two are indistinguishable. (At A1's 1.508 the pair
reads 179.3 ± 36.3 against 117.5 ± 2.8, which would make the frozen bit look 1.5× dearer; the measured slope
makes the weaker and safer claim, and it is the one to quote.) Whatever a flipped bit costs, the multiplier
is not where most of it goes. In **watts** the sign bit is of course far cheaper — 0.495 ± 0.085 W against
4.987 ± 0.098 W — because it is one bit against twelve; it is the per-bit price that matches.

## The registered verdicts

| | outcome | reading |
|---|---|---|
| **P1** multiplier share in [0.35, 0.85] | **FAIL** | s_mul = **−0.17**: the registered two-column fit wants a *negative* multiplier coefficient (b_mul −0.177 ± 0.160, b_back +2.480 ± 0.284 W per million toggles/op) |
| **P2** additivity within max(2 SE, 10%) | **PASS** | `sm_lo12` + `sm_sgn` = 4.860 W against `sm_sgnlo` 4.756 W, **+0.105 W** against a 0.476 W tolerance |
| **P3** a frozen-multiplier flip still costs, share in [0.02, 0.25] | **PASS** | 0.548 ± 0.111 W, **4.9 SE** above zero; 0.127 of `sm_lo12` |
| **P4** the busy partner buys nothing when the tree is frozen | **FAIL** | \|`sm_pi_sgn` − `sm_sgn`\| = 0.166 W: inside the 0.5 W band, outside the 25 %-of-`sm_sgn` clause (0.137 W) |
| **P5** the aligner ladder rises with shift distance | **FAIL** | e1 0.617, e16 **0.345**, e64 0.863 W — not monotone, though e64/e1 = 1.40 is inside [1.2, 2.2] |
| **P6** position inside the mantissa matters | **PASS** | sp12 − lo12 = **+2.558 W** at 15 SE; hi12 +2.040 W |
| **P7** the clock held | **PASS** | every kept run at 800 MHz, highest kept board 51.1 W |

## What the failures mean

**P1 is a real failure of the column definition, not of the correction.** b_mul is negative at *every* leakage
slope tried — −0.086 at 0 W/°C, −0.100 at the published law's 0.36, −0.104 at 0.456, −0.135 at 1.0, −0.177 at
A1's 1.508 ([`leak-sensitivity.txt`](leak-sensitivity.txt)) — so it is not an artefact of A1. The registered
columns group the bench's counts **by file**, and two files sit in *both* the fraction path and the exponent
path: `txfma_csa` (inside the tree's compressors, and in `txfma_e1`, `e2`, `e5` and `f3`) and `txfma_adder`
(the product adder, and the exponent adder). For `sm_e16` the 201,216 `txfma_adder` toggles are the *exponent*
adder — the fraction never changes — yet the registered map books them to f4. The back-end column is therefore
inflated for the frozen items, the fit prices it high, and the multiplier is left to absorb the error.

**With the columns the arithmetic justifies, the fit is sensible** ([`posthoc.txt`](posthoc.txt), post-hoc and
reported as such, never in place of the registered scoring). An item either changes the significand or does
not; a frozen-significand item has bit-identical tree inputs, so *all* of its toggles are outside the
multiplier, and a sign-and-exponent-frozen item leaves the exponent path still. Putting `txfma_csa` and
`txfma_adder` on the side the item's own arithmetic dictates, and dropping the four wrapper files whose nets
are their children's ports named again one level up:

- **b_mul = +0.517 ± 0.161 W per million toggles/op** (+0.650 ± 0.188 at E66's slope)
- **b_back = +0.957 ± 0.264** (+1.000 ± 0.305), i.e. a back-end toggle costs **1.85×** a multiplier toggle
  — but that ratio is itself slope-dependent, 1.54 at E66's measured 0.296
- **s_mul = 0.50 ± 0.15** for a 12-bit mantissa flip (0.55 ± 0.15 at E66's slope): between about a third and
  two thirds of its in-unit cost is the multiplier. This is the one quantity here that is **stable against the
  leakage slope** (0.50–0.56 across all eight), which is why it survives as the result
- residual rms **0.429 W** over nine items spanning 0.35–6.87 W

🛑 **Two caveats, both against this fit.** (1) It fits the nine items *worse* than the registered columns it
replaces — **rms 0.429 W against the registered fit's 0.179 W** at the same slope, and the gap holds at every
slope (0.429–0.478 against 0.179–0.184). Its residuals are structured, not noise: `sm_hi12` +0.923,
`sm_sp12` +0.525, `sm_lo12` −0.479 — the three mantissa items that span the data, alternating in sign — and
the rms exceeds the whole measured price of `sm_sgn` (0.548 W) and `sm_e16` (0.345 W). So the post-hoc split
buys a positive `b_mul` at the cost of fit quality: it is a **diagnosis of the column definition, not a better
model**. (2) The two columns are **96 % anti-correlated** (corr −0.957), so the split between them is the
weakest part of the result; both coefficients are only ~3.2 SE from zero, and a 1 SE excursion on the pair
spans s_mul ≈ 0.35–0.65. The gate level said the multiplier is 0.11–0.13 pJ
of a 745 fJ board flip (15–17 %); in-unit, measured, it is about half — the rest of the board number is the
operand bus, the register file's read ports, the result path and the accumulator, all outside the unit.

**P4 failed on a difference that is not there.** 0.166 W against a combined SE of 0.163 W is 1.0 SE: the busy
partner's effect on a frozen-tree flip is consistent with zero, which is what P4 predicted. The registered rule
simply had no SE clause, so a null result scored FAIL on the tighter of its two bands. Reported as written.

**P5 falsified something worth keeping.** The RTL's back-end counts rise monotonically with the exponent step
(573 k, 708 k, 990 k for ±1, ∓16, ∓64) and the energy does not: `sm_e16` costs 0.345 ± 0.097 W where `sm_e1`
costs 0.617 ± 0.141. Per back-end toggle the three read 1.08, 0.49 and 0.87 W per million — a 2.2× spread
inside one family whose tree is frozen and whose only difference is how far the aligner shifts. **Energy is not
proportional to RTL-name toggles even within one stage group**, which is the sharpest limit this experiment
puts on step 6 of the chain: a toggle count is not a price list.

**P2 is the result the model needed.** The RTL says a sign flip and twelve mantissa flips add exactly; the card
says their *energies* add too, to 0.105 W in 4.8 — about 2 %. A linear per-stage energy model is therefore not
ruled out in principle; what fails is pricing its columns by counting RTL names.

## Files

| | |
|---|---|
| `predictions.json` | the RTL design matrix, frozen before the first launch: per item, per stage, absolute and minus its own zero |
| `verdicts.json` | the registered reduction: gates, per-item prices, the fit, P1–P7 |
| `runs.csv` | every run: raw and corrected board power, launch and window readings, clock, voltage, cycles per op, rate |
| `posthoc.txt` | the post-hoc column definition and its fit |
| `leak-sensitivity.txt` | every price in W and in fJ per flipped bit, and both fits, under eight leakage slopes, with E66's direct measurement of this card's idle leakage beneath |
| `operands-manifest.json` | the eleven items, their masks, designed flip counts and frozen-significand flags |
| `aifoundry2/sm/p*.attempt-*/` | the two aborted, restarted attempts, published so the record matches the tree; `gather` never reads them |
| `aifoundry2/sm/p*/` | the 41 kept passes: telemetry, marks, runs, configs, the lab manifest and the operand checksums. The per-pass `tiles/` are left out (identical in every pass; `gen.sha256` pins them and `make_sm.py` regenerates them) and `runs.jsonl` is gzipped |

Reproduce: `python3 tools/claims-v3/sm/make_sm.py build/sm-gen --check`, then
`HL_GEN=$PWD/build/sm-gen HL_EXPN=sm HL_PER_SHIRE=16 bash tools/claims-v3/hl/block.sh <pass> anchor_pi,anchor_zeros,smz_,sm_`,
then `python3 tools/claims-v3/sm/reduce_sm.py --data build/claims-v3/aifoundry2/sm --gen build/sm-gen --pred predictions.json --out verdicts.json`.
