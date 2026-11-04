# Q140(q): G4 for a governed large GEMM's sustained path, and a block-stride term from the L3's public set mapping

*Wed 4 Nov 2026 (week 45), Q140's desk half, on the Intel, about 02:00-02:55 PST. Desk only: no card, no device command, no
ssh to a lab box, no Discord, no Modal, nothing from the private archive. It answers Q139's final critic's **rank 5** ("The large
GEMM's sustained path: G3 to G4") and **rank 6** ("A large GEMM's time per op on new shapes"). On the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) that is **item 1** ("Where a
large GEMM falls") and, through the power path, **item 6**. The owner's goal, 2 November 2026: to predict the power requirement and
heat generation of numeric computations as accurately as possible.*

***Registered first:** [`REGISTRATION.md`](REGISTRATION.md) and [`registration.json`](registration.json), committed in
`49575094` at **02:26 PST**, before any fit, score or prediction of this lane was computed.*

*Corrected after verification, Wed 4 Nov 2026, from 03:26 PST to this commit, after the registered result (`e39d06da`) and its
verifier's report. The verifier found three moderate faults and ten minor ones. Each corrected passage is marked "corrected after
verification, C<n>", n being the verifier's fault number, and the old wording is in
[§ Corrections after verification](#corrections-after-verification). No frozen file, fitted number, registered score, rule or
verdict changed. `g4.json`, `predictions-e168.json`, `predictions-e169.json`, the scorer and every registered output are as
committed. The registration keeps its text; [`REGISTRATION-A1.md`](REGISTRATION-A1.md) is its dated amendment, written after
every fit and score and before any E168 or E169 claim. Two corrections are new post hoc readings that weaken the quoted
held-out figures (C1, C2). The registered figures are nested in the constants only, and leave out T_S. With the term selection
nested too and T_S applied as G4 is frozen, the window board reads **1.47 W** and the window die **0.63 °C**, against the
registered 1.33 W and 0.58 °C and G3 nested's 1.89 W and 0.76 °C. The board's gain survives every reading. The die's is
marginal over sessions. **The clock gains nothing** (10.7-11.1 MHz against G3 nested's 10.45).*

## The answer

**G4 = G3 + Q140(l)'s zeros level + a model term for the governor's process-boundary dips** (*corrected after verification,
C9:* it said "the governor's process-boundary dips"; T_G is fitted to window means, not a measured governor rule). The
registered forward rule kept two of the three candidate terms and **rejected the start-die term**. Leave one session out over
five sessions (65 sustained GEMM-pattern runs: E119, E126, E136, E146 and E159), G4 *without T_S* reads the window board to
**1.33 W** and the window die to **0.58 °C** rms, against G3 nested's 1.89 W and 0.76 °C. Both gains are resolved by a paired
bootstrap. The clock does not move: **10.3 against 10.5 MHz**, not resolved ([`loso-g4.json`](loso-g4.json);
[`fit-g4.txt`](fit-g4.txt)).

*Corrected after verification, C1 and C2 ([`corrections.txt`](corrections.txt)):* those figures carry two optimisms.

- **C1, the selection.** The rule chose the terms on the same outer held-out losses it reports (A4, as registered), so the
  figures are nested in the constants only. Nested in the selection too, by an inner leave one session out on the four
  training sessions, T_G fails the inner rule in E119's fold, and at 3 of 4 in E146's as well. The pooled errors then read
  **1.42 W, 0.60 °C and 10.7-11.1 MHz** (inner rule 2 of 4 / 3 of 4).
- **C2, T_S.** The figures are G4 without T_S: E136's four other-kind runs were scored on E136's levels. G4 as frozen, with T_S,
  reads **1.38 W and 0.61 °C**.
- **Both:** **1.47 W, 0.63 °C and 10.7-11.1 MHz**.

The board's gain over G3 nested is resolved in every reading, over runs and over the five sessions resampled (+0.42 W
[+0.09, +0.77] with both). The die's gain is resolved over runs, but over sessions it is marginal once the selection is nested:
+0.13 °C [−0.01, +0.27] with both. The clock gains nothing. With the selection nested at 3 of 4 it reads 0.63 MHz *worse* than G3
nested, [−1.53, +0.18] over runs, and worse whichever session is dropped. G4 as frozen is unchanged: with T_S applied in the
choice, the constants on all five sessions are still `g4.json`'s (0.2 W/°C, 65.5 °C, 0.12, 56 W). So E168's frozen predictions
follow A4's letter.

| step (held-out loss, G3's: Σ (clock/15)² + (W/2)² + (die/1)²) | sessions lower | pooled loss | verdict |
|---|---|---|---|
| A0 = G3 nested (k_eff, trip chosen per fold) | — | 127.1 | base |
| **T_Z** Q140(l)'s zeros level, β·δ (fallback δ) | 4 of 5 (E119, E126, E136, E159) | 127.1 → **100.9** | **carries, kept** |
| **T_D** one die law from 54.38 °C at k_D 0.44-0.50 W/°C, replacing G3's k_eff | 1 of 5 (E146) | 100.9 → **204.6** | **does not carry** |
| **T_G** a dip at 618 MHz opening each process (d_G of its kernel time, when L800 ≥ P_G) | 5 of 5 | 100.9 → **81.5** | **carries, kept** |

**G4 as frozen** ([`g4.json`](g4.json)): G3's loop and chain unchanged; every level + β·δ_t (β 0.648, δ the format's fallback,
−1.51 to −1.54 W); leakage k_eff = **0.2 W/°C** above the run's start die (G3's form; it was 0.1); the trip at **65.5 °C**; a
dip of **12%** of each process's kernel time at the start of the process when the raised 800 MHz level is at least **56 W**.
M8's span fraction (T_S) sets the level of a kind other than zeros and the format's random.

| 65 runs, measured − predicted | clock, MHz rms (mean) | inside 15 MHz | board, W rms (mean) | inside 2 W | window die, °C rms (mean) | inside 1 °C |
|---|---|---|---|---|---|---|
| G3 as frozen (0.1 W/°C, 65.5 °C; blind on E159 only) | 10.10 (−6.55) | 56 | 1.79 (−0.95) | 42 | 0.73 (−0.43) | 53 |
| G3 nested (the fair before) | 10.45 (−6.43) | 56 | 1.89 (−0.71) | 39 | 0.76 (−0.32) | 53 |
| **G4 nested, without T_S** (registered; *C2*: the label was "G4 nested") | **10.34 (−4.17)** | 53 | **1.33 (−0.32)** | 57 | **0.58 (−0.06)** | 58 |
| G4 final (in sample, without T_S) | 10.42 (−4.95) | 53 | 1.23 (−0.40) | 59 | 0.53 (−0.09) | 60 |
| paired bootstrap, G3 nested − G4 nested rms [95%] | [−1.29, +1.41] not resolved | | **[+0.41, +0.69]** | | **[+0.09, +0.26]** | |
| *post hoc, C2:* G4 as frozen, with T_S | 10.33 (−4.19) | 53 | 1.38 (−0.28) | 56 | 0.61 (−0.04) | 57 |
| *post hoc, C1:* the selection nested too, inner 2 of 4 / 3 of 4 | 10.69 / 11.09 (−5.2 / −5.3) | 53 | 1.42 (−0.22 / −0.20) | 55 | 0.60 (−0.03) | 58 |
| *post hoc, C1 and C2:* both, inner 2 of 4 / 3 of 4 | 10.68 / 11.08 (−5.2 / −5.3) | 53 | **1.47** (−0.18 / −0.16) | 54 | **0.63** (−0.01) | 57 |
| *post hoc:* G3 nested − both (3 of 4), over runs; over sessions | [−1.52, +0.19]; [−1.16, +0.07] | | [+0.24, +0.60]; [+0.09, +0.77] | | [+0.01, +0.23]; [−0.01, +0.27] | |

**E159 held out of the constants' fit** (G3 was blind on it; *corrected after verification, C4:* T_G's form and its 618 MHz were
read off E159's own H1, its C1, so E159 is not blind for G4): clock 8.68 → **7.73 MHz**, board 1.94 → **1.81 W**, die 0.99 →
**0.93 °C**. Inside the critic's bands: 8, 7 and 5 of 9 holds, against G3's 8, 5 and 6. So on E159, G4 would still fail the board
and die rules (8 of 9). The dip clock's value barely matters: at 600 or 650 MHz, E159 reads 7.80 / 7.71 MHz, 1.81 / 1.82 W and
0.93 / 0.92 °C ([`corrections.txt`](corrections.txt) C4). Neither C1 nor C2 touches E159: its fold keeps T_G with the same
constants, and it has no other kind.
**The 23 large GEMMs** (E136, E146, E159): G3 nested 11.4 MHz / 1.54 W / 0.82 °C → G4 nested, without T_S, **10.8 MHz / 1.29 W /
0.69 °C**. *Corrected after verification, C2:* G4 as frozen, with T_S, reads **10.8 MHz / 1.43 W / 0.76 °C** there, because
E136's fp32 sparse50 hold goes from +0.38 to +2.96 W. With the selection nested too it reads 10.8-11.9 MHz / 1.43-1.44 W /
0.76 °C.

**The stride term fails as registered.** SM puts E146's tile-level trace through the ET-SoC-1's public L3 map: shire PA[10:6],
bank [12:11], sub-bank [14:13], set [22:15], 4 ways, so the L3 index repeats every 8 MB. It uses true LRU (assumed) and the
runtime's buffer offsets, and nothing is fitted. It reproduces every L3-held rung. Past 32 MB it keeps almost none of a far B
panel, where the card kept about half, so it reads every far shape 13-23% slow. *Corrected after verification, C3:* that holds
at power-of-two strides and at the others alike. SM does predict a collapse at the power-of-two strides, but a deeper one than
the card's (far-B share at K4n8 −0.69 against the card's −0.20, at K6n4 −0.29 against +0.18; S3 in
[`stride-sm.txt`](stride-sm.txt)). Its time errors there, −13% to −22% (S2 failed on each of the five), are no smaller than on
far shapes at other strides (K2n9 −13.7%, K4n7 −17.4%, K6n5 −18.4%). So SM's error is mostly a level, not a stride effect; how
it reads the step at a power-of-two stride is under E169 below.

- rms over all 69 committed cells **13.0%**, against ISO's **7.3%** and STRICT's **12.6%**. *Corrected after verification, C6:*
  ISO's figure is partly in sample. Its retention curve was fitted on E158's 42 cells, where it reads 4.7% (SM 12.3%, STRICT
  13.7%). On E146's 27 cells it reads 10.0% (SM 14.0%, STRICT 10.8%; [`corrections.txt`](corrections.txt) C6);
- on E146's ladder, out of sample for the retention models, 13.6% against ISO's 10.6% (*corrected after verification, C6:* it
  said "out of sample for every model"; MAB's prices are in sample on E146's L2 and D8 for every arm, as B5 says);
- F6 −17%, against ISO's +0.5%.

None of S1-S3 is met ([`stride-sm.txt`](stride-sm.txt)). Post hoc, random replacement on the same map reads 10.3% and
LRU-position insertion 13.5% ([`posthoc-sm-policies.txt`](posthoc-sm-policies.txt)). So the miss is not the replacement policy
alone. The likelier gap is the trace model (32 shires in lock step, E136's L2 model). No DRAM channel or bank term was
registered: no public source found gives the address-to-memshire interleave.

## The reported checks (registered; no selection)

From [`checks-g4.txt`](checks-g4.txt) / [`checks-g4.json`](checks-g4.json):

- **(i) The zeros level and the die law on bursts** (*corrected after verification, C7:* the heading said "The die law works on
  bursts"). E158's 42 zeros bursts never entered P0. Their first-second board reads P0 3.57 W high (mean −3.53); with T_Z, 2.59 W
  (−2.54); with T_Z and the one die law at 0.47 W/°C from 54.38 °C, **0.64 W** (+0.41). The bursts started at 47.3-48.3 °C, about
  6.5 °C under the reference. *Corrected after verification, C7:* so the check is **consistent with the die law's offset**; it
  does not test its slope. The bursts' start dies span only 1.0 °C (6.0-7.1 °C under the reference), so the law's offset alone,
  with no slope, reads 0.62 W, and the best constant offset (−2.54 W) 0.47 W. The registration left k_D open once T_D was
  rejected; `checks_g4.py` set 0.47 W/°C, the middle of A2's grid, before any output ([`REGISTRATION-A1.md`](REGISTRATION-A1.md)
  item 4). At 0.44 and 0.50 the check reads 0.54 and 0.78 W. Of the drop from 3.57 to 0.64 W, T_Z takes 3.57 → 2.59 and the die
  law the rest ([`corrections.txt`](corrections.txt) C7). The die law is wrong for a held window: T_D doubled the sustained loss,
  and post hoc the start offset alone (G3's in-run constant kept) still reads the board at 1.73 W against G4's 1.33
  ([`posthoc-g4.txt`](posthoc-g4.txt) P1).
- **(ii) E159's three zeros holds.** Their window boards spread 0.057 W over starts of 52-57 °C. G4 spreads them **0.44 W**
  (G3 0.10), because its in-run constant runs from each run's start die. Its misses are −1.32 / −1.71 / −1.69 W, against G3's
  −2.45 / −2.49 / −2.43 W. The level is closer; the start dependence is not physical. G4's E168 predictions carry the same
  signature: an int8 hold from a cold start is predicted 1.3 W *higher* in the window than from a warm one. *Corrected after
  verification, C8:* E168 as designed cannot test that, because its three int8 holds all start warm. A card lane that wants it
  tested adds an int8 zeros hold from a cold start by a dated amendment before its claim; its nominal prediction is already
  frozen (`both_nominal_starts`: 37.66 W cold against 36.33 W warm; [`REGISTRATION-A1.md`](REGISTRATION-A1.md) item 5).
- **(iii) T_S on E136's four other-kind runs.** The real kinds are unchanged, since M8's span fraction equals E95's r_real to
  1%. fp32 sparse50 goes **+0.38 → +2.96 W** (φ_M8 0.30). Post hoc, in E136's bursts the measured fraction is 0.45-0.60 for fp32
  sparse50, 0.66 for fp16 sparse50, and **0.77 for int8 sparse50 (M8 0.78) and 0.80 for int8 real (M8 0.79)**
  ([`posthoc-g4.txt`](posthoc-g4.txt) P3). *Corrected after verification, C5:* for the real floats it is 0.99 (fp32) and 1.02
  (fp16) on E136's g4k bursts, against M8's 0.99 and 0.98, but **1.30** on its g2k fp32 real burst (M8 0.99): the real-kind
  agreement is shown on the g4k holds and bursts, not on every burst. So M8's kinds-loop fraction misses a float sparse GEMM,
  likely its memory path's own switching, and holds for int8. E168's two other kinds are int8.

## E168: G4's frozen predictions (critic rank 5)

[`predictions-e168.json`](predictions-e168.json) / [`.txt`](predictions-e168.txt), from [`predict_e168.py`](predict_e168.py) with
the frozen `g4.json`. Scorer: [`score_e168.py`](score_e168.py). Run `check` before the claim (9 frozen files,
[`frozen-sha256-e168.json`](frozen-sha256-e168.json)) and `score <session dir>` after. `selftest` puts E159's session through
the scorer's path and reproduces the fit's G4 predictions to 0.0004 ([`selftest-score-e168.txt`](selftest-score-e168.txt)).
*Corrected after verification, C11:* `check` does not hash `score_e168.py` itself, nor three modules and four data files its score
path also loads (`predict_e83.py`, which `make_predictions_e119.py` imports; `surface_hpl.py`; `surface_hpl_t.py`; E105's
`results-speed.json`; E107's `e107.json` and `scored.json`; `predictions-e101.json`).
[`frozen-sha256-e168-scorer.txt`](frozen-sha256-e168-scorer.txt) lists the sha256 of all 18 files, so before the claim also run
`shasum -a 256 -c frozen-sha256-e168-scorer.txt` from this directory ([`REGISTRATION-A1.md`](REGISTRATION-A1.md) item 6). The
list comes from a trace of the score path, [`trace-scorer-e168.txt`](trace-scorer-e168.txt), which also checks that the sidecar
covers every one of its 16 files.

The design: aifoundry2 card 0 under its own governor, nothing set, E136's rgm136 binary unchanged. Three shapes nobody has run,
chosen so that their line split is not a stride question:

| shape | arm | footprint (A / B / C) | lines an op missing the L2 (L3 / fresh) |
|---|---|---|---|
| S1 | `gemmL1x3x3` (1,024 × 1,536 × 1,536) | 6 / 9 / 6 = 21 MB | 192 / 0 |
| S2 | `gemmL3x3x2` (3,072 × 1,536 × 1,024) | 12 / 6 / 18 = 36 MB | 176 / 0 |
| S3 | `gemmL3x5x3` (3,072 × 2,560 × 1,536) | 18 / 15 / 30 = 63 MB | 132 / 60 |

Nine holds of 12 processes × 8 s, about 106 s each, with the last 40 s read:

| hold | P0(800) | predicted peak | **G4: MHz, W, die** | G3 as frozen | E136's law |
|---|---|---|---|---|---|
| S1 fp32 random, cold (46 °C) | 67.17 W | 75.7 W | **689.2, 57.95, 65.39** | 691.2, 57.05, 65.49 | 745.3, 62.1, 61.6 |
| S1 fp32 random, warm (55 °C) | | | **657.0, 53.10, 65.44** | 656.8, 53.04, 65.50 | 745.3, 62.1, 65.0 |
| S2 fp32 random, cold | 68.12 | 76.6 | **681.9, 57.87, 65.40** | 683.9, 56.99, 65.49 | 738.6, 62.1, 61.6 |
| S2 fp32 random, warm | | | **650.6, 53.09, 65.44** | 650.4, 53.03, 65.50 | 738.6, 62.1, 65.0 |
| S3 fp32 random, cold | 59.72 | 68.2 | **767.3, 59.43, 64.65** | 777.1, 59.33, 65.09 | 796.6, 59.4, 60.5 |
| S3 fp32 random, warm | | | **725.0, 53.55, 65.38** | 725.7, 53.34, 65.49 | 796.6, 59.4, 63.9 |
| S2 int8 zeros, warm | 37.13 | 45.6 | **800, 36.33, 55.96** | 800, 37.27, 56.42 | 800, 37.1, 54.7 |
| S2 int8 W8A8 real (`real_smol_w8a8_down`, φ 0.773), warm | 43.97 | 52.5 | **800, 43.91, 59.67** | 800, 44.46, 59.97 | 800, 44.0, 57.5 |
| S2 int8 sparse50 (φ 0.783), warm | 44.06 | 52.6 | **800, 44.01, 59.72** | 800, 44.56, 60.01 | 800, 44.1, 57.5 |

- *Corrected after verification, C10:* **the int8 W8A8 hold's matrix is one real tile pair** (1 KB of A and 1 KB of B, the
  2,048-byte `int8.real_smol_w8a8_down.bin`) cycled over the whole GEMM by rgm136's generator `tiles`. So it tests one real
  tile's bits in a GEMM, not a whole weight panel. The sparse50 hold uses the generator `sparse50`, which draws its tiles with
  half the elements zero (8,192 distinct per pool; [`REGISTRATION-A1.md`](REGISTRATION-A1.md) item 5).
- **Every predicted peak is under 82 W**, the highest 76.6 W, so nothing is duty-cycled. The stops: board above 85 W on 3 live
  samples, or a die at or above 76 °C, both tested in the smoke.
- **The rules** (the critic's; registered A7): per hold, measured − G4: clock within 15 MHz, board within 2 W, window die within
  1 °C, each on at least 8 of 9 holds.
- **The increment rule:** each int8 kind's window board over int8 zeros', within 15% of S2's span. G4 predicts 7.58 W (W8A8)
  and 7.68 W (sparse50); the band is ±1.33 W (span 8.86 W).
- **Beside G4:** E136's law and G3 as frozen. If the session runs kinds zeros anchors first, `--anchors` adds an arm with its
  own δ.
- **Budget:** about 45 card-minutes (cap 55), since three cold starts need rests to about 46 °C.
- **Device commands:** E159's chain, every command READ; the lane re-runs `dmcmd_audit.py`.

## E169: the stride term's frozen predictions (critic rank 6)

[`predictions-e169.json`](predictions-e169.json), from [`stride_sm.py`](stride_sm.py) and [`peaks_e169.py`](peaks_e169.py): fp32
zeros bursts in E158's harness, T800 from launches at or above 790 MHz. Predicted peaks are 46.9 W at most; E158's zeros bursts
peaked at 36.1 W.

| | arm | panel stride | SM T800 (µs) | ISO | STRICT | SM / ISO − 1 |
|---|---|---|---|---|---|---|
| P1 | `gemmL1x8x5` | 8 MB: all five blocks share sets | 2.7355 | 1.8849 | 1.9958 | +45% |
| P2 | `gemmL2x8x3` | 8 MB, two row blocks | 2.0912 | 1.7437 | 2.0602 | +20% |
| P3 | `gemmL1x4x8` | 4 MB: blocks two apart share sets | 2.7066 | 1.8918 | 2.1257 | +43% |
| N1 | `gemmL1x7x5` | 7 MB | 1.9958 | 1.8849 | 1.9958 | +6% |
| N2 | `gemmL2x6x3` | 6 MB | 1.9374 | 1.6487 | 2.0817 | +18% |
| N3 | `gemmL1x5x8` | 5 MB | 2.0667 | 1.8918 | 2.1257 | +9% |

The rules (registered B7): SM within 3% on every shape, and resolved on P1-P3 (|SM − ISO| / ISO ≥ 3% and the measured T800
closer to SM). **On the committed ladder SM already fails** (above), so E169 as designed mostly tests ISO against strict LRU at
power-of-two strides. Post hoc, STRICT reads the four collapses within 6.5% (D4 +2.1%, D8 +0.1%, K4n8 +6.5%, K6n4 −5.9%), where
ISO misses by 8.5-13%. The collapses behave like "no retention", and the plateau like "half".

*Corrected after verification, C3 (post hoc, [`corrections.txt`](corrections.txt) C3):* most of SM's miss is its retention level
rather than its set index. Take each of S2's five collapses against the nearest rung of its own ladder that is not one. SM's step
from that rung is closer to the card's than ISO's in 5 of the 6 pairs, and closer than STRICT's in all 6:

| collapse / rung | card | SM | ISO | STRICT |
|---|---|---|---|---|
| E158 K4n8 / K4n7 | 1.29 | 1.22 | 1.10 | 1.00 |
| E158 K6n4 / K6n3 | 1.33 | 1.32 | 1.21 | 1.00 |
| E158 K6n4 / K6n5 | 1.15 | 1.09 | 1.00 | 1.00 |
| E146 D4 / D2 | 1.26 | 1.30 | 1.19 | 1.01 |
| E158 D4 / D2 | 1.27 | 1.30 | 1.19 | 1.01 |
| E146 D8 / D2 (the exception) | 1.31 | 1.46 | 1.19 | 1.07 |

So the L3's 8 MB index remains a candidate cause of the collapses' extra time, though SM's retention level is wrong
everywhere past 32 MB, its collapses run too deep, and it overshoots D8. This reading came after the registered test failed;
E169 tests it.

## What this does to predicting power and heat

- **Terms tested** on a governed large GEMM's sustained power path (aifoundry2):
  - Q140(l)'s zeros level **carries** (*corrected after verification, C1:* in every fold, with the selection nested too);
  - the process-boundary dip, T_G, **carries** as registered (*C1:* in 3 or 4 of the 5 folds with the selection nested; *C9:* a
    model term fitted to window means, not a measured governor rule);
  - the start-die term (one die law, 0.44-0.50 W/°C from 54.38 °C) **does not** (in no fold, nested or not);
  - M8's span fraction holds for int8 and, on E136's g4k runs, for the real kinds, and **fails for fp32 sparse50** (+2.6 W)
    (*C5:* E136's g2k fp32 real burst measured 1.30 against M8's 0.99).
- **Out of sample, before → after**, leave one session out over 65 runs, rms. *Corrected after verification, C1 and C2:* the
  registered "after" is nested in the constants only and leaves T_S out; the readings under it are post hoc.

  | 65 runs | board | window die | clock |
  |---|---|---|---|
  | before: G3 nested (G3 as frozen) | 1.89 W (1.79) | 0.76 °C (0.73) | 10.45 MHz (10.10) |
  | after, registered: G4 nested, without T_S | **1.33** | **0.58** | 10.34, not resolved |
  | G4 as frozen, with T_S (C2) | 1.38 | 0.61 | 10.33 |
  | the selection nested too (C1; inner 2 of 4 / 3 of 4) | 1.42 | 0.60 | 10.69 / 11.09 |
  | **both** | **1.47** | **0.63** | **10.68 / 11.08** |

  The board's gain is resolved in every reading, over runs and over sessions. The die's gain is resolved over runs in every
  reading; over sessions it is marginal once the selection is nested (+0.13 °C [−0.01, +0.27] with both). **The clock gains
  nothing.**

  E159, held out of the constants' fit (T_G was designed from its H1, C4): 8.68 → 7.73 MHz, 1.94 → 1.81 W, 0.99 → 0.93 °C, the
  same in every reading.
- **Heat:** the chain is unchanged. The die gain comes from the power path: the window die's bias falls from −0.32 to −0.06 °C
  (−0.01 to −0.04 °C in the post hoc readings).
- **For bursts** (*corrected after verification, C7*): the zeros level and the die law together take E158's zeros first-second
  board from 3.57 to **0.64 W** rms, T_Z alone to 2.59 W. That is consistent with the die law's offset 6-7 °C under the
  reference, out of sample. It is not a test of the law's slope: a constant offset does as well (0.47 W).
- **The time term:** the L3's public set map with true LRU does not predict time per op: 13% rms against ISO's 7.3%. *Corrected
  after verification, C6:* ISO's figure is partly in sample; on E146's 27 cells SM reads 14.0% against ISO's 10.0%. Time on a new
  shape stays ISO's 6-11%, with 8-13% single misses at power-of-two strides. Post hoc, strict LRU reads those collapses to within
  6.5%. *C3, post hoc:* SM's step at a power-of-two stride is closer to the card's than ISO's in 5 of 6 pairs, so its set index
  stays a candidate for that step.

## Registered against what happened, number by number

| # | registered (`49575094`) | what happened |
|---|---|---|
| A1 | base G3 at `91def7c4` | as registered; A0 at (0.1, 65.5) reproduces G3's committed in-sample 56-run score and E159's blind score to 0.0004 (`loso-g4.json` `reproduction_check`) |
| A2 | T_Z, T_D, T_G in order; T_S structural | as registered; T_Z and T_G kept, T_D rejected (D2 on T_G's clock). *Corrected after verification, C2:* T_S was applied in no scored row and not in choosing `g4.json`'s constants (A1 item 2) |
| A3 | 65 runs, five sessions, nested LOSO, grids | as registered |
| A4 | forward rule: ≥ 3 of 5 sessions and pooled | as registered; d_G chosen at its grid's top (0.12), see P2. *Corrected after verification, C1:* the rule chose the terms on the outer held-out losses, so the scores are nested in the constants only (A1 item 1) |
| A5 | scored arms, paired bootstrap, checks (i)-(iii) | as registered (`loso-g4.json`, `checks-g4.json`). *Corrected after verification, C7:* check (i)'s k_D, 0.47, was set in code (A1 item 4) |
| A6 | E168's shapes, nine holds, nominal starts, the primary | as registered (D4). *Corrected after verification, C8, C10:* no int8 hold starts cold; the W8A8 hold is one tile pair cycled (A1 item 5) |
| A7 | E168's rules | frozen in `predictions-e168.json`, applied by `score_e168.py` |
| A8 | the 82 W rule | every hold ≤ 76.6 W |
| B1-B3 | SM: the public map, the allocator's offsets, no fitted constant; sensitivity arms ALIGNED and A_STRICT | as registered; ALIGNED makes L3-held K2 rungs collapse (−13 to −25%), so the allocator's offsets matter |
| B4 | no DRAM term | none |
| B5 | S1-S3 on committed data | all three fail (above) |
| B6-B7 | E169's six shapes and rules | frozen in `predictions-e169.json` |
| — | **post hoc**, written after the registered results were read; nothing frozen depends on them | [`posthoc_sm_policies.py`](posthoc_sm_policies.py) (two other replacement policies); [`posthoc_g4.py`](posthoc_g4.py) P1 the start offset alone (loss 107.6 against G4's 81.5), P2 the dip's grid edge (0.12 is the in-sample best of 0.12 / 0.15 / 0.18), P3 E136's bursts against M8's span fraction; the STRICT reading of the collapses |

**Departures** (dated Wed 4 Nov 2026):

- **D1.** `fit_g4.py`'s first run stopped at `import numpy` under the default `python3`, with nothing computed. It was rerun
  under `/usr/bin/python3` (3.9.6, numpy 1.26.4). `stride_sm.py` and `posthoc_sm_policies.py` use the standard library only.
- **D2.** T_G's dip clock is **min(618 MHz, G3's clock at that step)**, and the registration said "618 MHz". The two differ only
  where the governor already holds below 618 MHz (E119's c16r8 at 603-607 MHz). This was written into `g4_model.py` before the
  first fit but not into the registration. The dip's length comes from each process's kernel stretch in the run's mask: the
  measured windows when scoring, the planned schedule for nominal predictions.
- **D3.** Files beyond the registration's list: `frozen-sha256-e168.json` and `score_e168.py`'s check and self-test,
  `peaks_e169.py` (E169's peak records, added to `predictions-e169.json` before any commit), and the two post hoc scripts.
- **D4.** `predictions-e168.json` was rebuilt once before any commit to add the both-starts table that A6 requires
  (`both_nominal_starts`). Same `g4.json`; no number at the registered starts changed.
- **D5** (*added after verification, C12*). At 02:47 PST, after their outputs had been read, the repository-path variable in
  `stride_sm.py` and in the post hoc `posthoc_sm_policies.py` was renamed to `REPO`, and both were rerun. Their outputs are
  byte-identical to the first run's ([`REGISTRATION-A1.md`](REGISTRATION-A1.md) item 7).

## What it cannot say

- **One card, one governor build (BL2 0.22.0), five sessions.** E146 gives two sustained runs; E159 is the only session that is
  new for G3.
- **G4's in-run leakage is an effective constant.** It is 0.2 W/°C from the run's start die. Its start dependence is not
  physical: E159's zeros spread 0.44 W predicted against 0.06 measured, and int8 cold starts are predicted to draw more. The one
  die law that fixes this structurally fails the clock. The board's die dependence differs between a burst's first second and a
  held window, and no form tested here carries both.
- **The dip term is a window-mean device.** It folds the boundary and mid-process dips into one boundary dip. Its gate (56 W)
  and length (12%) come from five sessions, and E159's fold chose (0.06, 44 W). *Corrected after verification, C9:* it is a
  model term, not a measured governor rule. Its gate is on the model's raised 800 MHz level, not on a measured power. E159's
  measured dips were 5 of 7 at a process start and 2 mid-process (E159's README, C1). With the selection nested it fails the
  inner rule in E119's fold, and at 3 of 4 in E146's too (C1). Post hoc, its gate is not held at its grid's edge (56 W, the
  top of 44-56): in sample at G4's k and trip, P_G 60, 64 and 68 W raise the loss from 74.1 to 87.5-88.6
  ([`corrections.txt`](corrections.txt) C9).
- **M8's span fraction misses float sparse GEMMs** (above).
- **The stride term:** SM's L3 map is the ET-SoC-1's HAL register resets, and its 4 ways come from the HAL's way field. The LRU
  and the tag RAM's 5-bit field come from a later RTL revision (`core-et`). No public source gives the DRAM interleave, and the
  pools' device addresses were never logged.

## Files

| file | what |
|---|---|
| `REGISTRATION.md`, `registration.json` | the registration, committed first (`49575094`, 02:26 PST) |
| `g4_model.py` | G4: G3 imported unchanged, the terms, E159's inputs on its scorer's path, T_S's levels, M8's D per row |
| `fit_g4.py` → `fit-g4.txt`, `loso-g4.json`, `g4.json`, `rows-g4.json` | the registered fit: grids, folds, forward steps, every arm, per-run predictions, the freeze |
| `checks_g4.py` → `checks-g4.txt`, `checks-g4.json` | the registered reported checks (i)-(iii) |
| `predict_e168.py` → `predictions-e168.json`, `predictions-e168.txt` | E168's design, levels, nominal predictions, rules |
| `score_e168.py`, `frozen-sha256-e168.json`, `selftest-score-e168.txt` | E168's scorer, its hash check and self-test |
| `stride_sm.py` → `stride-sm.txt`, `stride-sm.json`, `predictions-e169.json`; `peaks_e169.py` → `peaks-e169.txt` | SM: the committed-data scores and E169's freeze |
| `posthoc_sm_policies.py` → `posthoc-sm-policies.txt`, `.json`; `posthoc_g4.py` → `posthoc-g4.txt`, `.json` | post hoc, labelled |
| [`REGISTRATION-A1.md`](REGISTRATION-A1.md) | the registration's dated amendment, after every fit and score, before any E168 or E169 claim (added after verification) |
| [`corrections_q140q.py`](corrections_q140q.py) → [`corrections.txt`](corrections.txt), [`corrections.json`](corrections.json) | the corrections after verification, post hoc: C0 (the registered results reproduced), C1-C4, C6, C7, C9 |
| [`frozen-sha256-e168-scorer.txt`](frozen-sha256-e168-scorer.txt) | the sha256 of the scorer and of every file its score path loads, 18 in all (C11) |
| [`trace_scorer_e168.py`](trace_scorer_e168.py) → [`trace-scorer-e168.txt`](trace-scorer-e168.txt) | the score path's 16 files, traced, and the sidecar checked against them (C11) |

**Rerun**, from this directory:

- `nice -n 10 /usr/bin/python3 -B fit_g4.py > fit-g4.txt` (about 4 min, 4 workers);
- `/usr/bin/python3 -B checks_g4.py > checks-g4.txt`;
- `/usr/bin/python3 -B predict_e168.py > predictions-e168.txt`;
- `nice -n 10 python3 -B stride_sm.py > stride-sm.txt` (about 4 min, 4 workers), then `/usr/bin/python3 -B peaks_e169.py > peaks-e169.txt`;
- `/usr/bin/python3 -B score_e168.py check`, then `selftest > selftest-score-e168.txt`;
- after verification: `shasum -a 256 -c frozen-sha256-e168-scorer.txt`; `/usr/bin/python3 -B trace_scorer_e168.py >
  trace-scorer-e168.txt`; and `nice -n 10 /usr/bin/python3 -B corrections_q140q.py > corrections.txt` (about 12 min on a loaded
  Intel, 4 workers).

## Device commands sent

None. This lane opened no device node, took no card lock and sent nothing.

## Corrections after verification

*Wed 4 Nov 2026, from 03:26 PST to this commit, by the fix pass, after the registered result (`e39d06da`) and its verifier's
report. Desk only: no card, no device command, no ssh to a lab box, no Discord, no Modal, nothing from the private archive.
Nothing frozen changed: `g4.json`, `predictions-e168.json`, `predictions-e169.json`, `frozen-sha256-e168.json`, the scorer and
every registered output are byte-identical to `e39d06da`. The verifier re-ran every committed script, found every output
byte-identical, and found three moderate faults and ten minor ones in what this README and the lane's result say. Each was re-checked against the
committed files before it was corrected, and each is numbered here as the verifier numbered it. The registration keeps its
text; [`REGISTRATION-A1.md`](REGISTRATION-A1.md) is its dated amendment, written after every fit and score and before any E168
or E169 claim.*

*Every new number is printed by [`corrections_q140q.py`](corrections_q140q.py) → [`corrections.txt`](corrections.txt)
([`corrections.json`](corrections.json)), and the scorer's file list by [`trace_scorer_e168.py`](trace_scorer_e168.py) →
[`trace-scorer-e168.txt`](trace-scorer-e168.txt). The corrections script imports the registered code (`fit_g4.py`,
`g4_model.py`, `checks_g4.py`), never a `main()`. It first reproduces `loso-g4.json`'s registered results exactly (C0: the four
pooled losses, every fold's choice, the final constants, the pooled scores and the registered bootstrap), and stops if it
cannot.*

### C1: the term selection was not nested (moderate)

**What the text said.** *The answer*: "Leave one session out over five sessions (65 sustained GEMM-pattern runs: E119, E126,
E136, E146 and E159), G4 reads the window board to **1.33 W** and the window die to **0.58 °C** rms, against G3 nested's 1.89 W
and 0.76 °C. Both gains are resolved by a paired bootstrap. The clock does not move: **10.3 against 10.5 MHz**, not resolved".
*What this does*: "**Out of sample, before → after**, leave one session out over 65 runs: board 1.89 → **1.33 W** rms ...;
window die 0.76 → **0.58 °C** ...; clock 10.45 → **10.34 MHz**, not resolved".

**The fault.** The forward rule kept and dropped T_Z, T_D and T_G on the same outer held-out losses it then reports, as A4
registers. So those figures are nested in the constants, not in the choice of terms.

**Now.** *The answer*, the pooled table and *What this does* label the registered figures as nested in the constants only, and
give the post hoc readings beside them ([`corrections.txt`](corrections.txt) C1). With the selection nested, T_G fails the inner
rule in E119's fold (lower in 2 of 4; pooled 64.6 → 65.1), and under a 3-of-4 inner rule in E146's as well. The pooled errors
then read 1.42 W / 0.60 °C / 10.69 MHz (inner 2 of 4) or 1.42 W / 0.60 °C / 11.09 MHz (3 of 4), against the registered 1.33 /
0.58 / 10.34. Over sessions the die's gain is then marginal ([−0.01, +0.28] °C at 3 of 4). The clock reads worse than G3 nested:
−0.63 MHz at 3 of 4, [−1.53, +0.18] over runs, and worse whichever session is dropped. The inner fits rest on three sessions
each, so these figures lean pessimistic, as the registered ones lean optimistic. Re-choosing the terms on them would be a refit
after the scores were seen. So G4 and every verdict stand, and E168 tests G4 blind.

### C2: the scores were G4 without T_S (moderate)

**What the text said.** The table's row "**G4 nested**", and *The answer*'s "**The 23 large GEMMs** (E136, E146, E159): G3
nested 11.4 MHz / 1.54 W / 0.82 °C → G4 nested **10.8 MHz / 1.29 W / 0.69 °C**". The lane's blog point 1: "about 1.3 W of board
power and 0.6 C of die temperature on sessions the model never saw".

**The fault.** G4 as frozen, and as applied to E168, includes T_S. `fit_g4.py` never applies it (no configuration sets
`lev_override`), so E136's four other-kind runs were scored on E136's levels, and `g4.json`'s constants were chosen on those
rows.

**Now.** The registered figures are labelled "without T_S", and G4 as frozen is scored post hoc beside them
([`corrections.txt`](corrections.txt) C2). It reads 1.38 W / 0.61 °C / 10.33 MHz on the 65 runs with each fold's registered
constants (1.39 W / 0.61 °C with T_S in the choice too), and 1.43 W / 0.76 °C on the 23 large GEMMs. With the selection nested as
well, 1.47 W / 0.63 °C. On E136's four runs T_S moves fp32 sparse50 from +0.38 to +2.96 W and from +0.50 to +1.62 °C, and the
three real kinds by at most 0.04 W. With T_S in the choice, the final constants equal `g4.json`'s, so the freeze is what A4
describes ([`REGISTRATION-A1.md`](REGISTRATION-A1.md) item 2). The lane's blog point 1 now says about 1.4-1.5 W and 0.6-0.8 °C.

### C3: "makes power-of-two panels collapse" (moderate, in the lane's blog point)

**What the text said.** Here: "It reproduces every L3-held rung and makes power-of-two panels collapse. But past 32 MB it keeps
almost none of a far B panel, where the card kept about half. So it reads every far shape 13-23% slow". The lane's blog point
5: "The chip's published cache layout (an index that repeats every 8 MB, four ways) explains why matrices laid out at
power-of-two strides run slow, but taken literally it predicts far too little reuse for everything else".

**The fault.** S2 (SM within 3% on each collapse) failed on every one, by −13% to −22%. SM reads far shapes at other strides
just as slow, and post hoc STRICT, which has no set index, reads the collapses within 6.5%. "Explains" rounds a registered
failure into a success.

**Now.** The stride paragraph says SM's time errors are as large at the power-of-two strides as at the others, and that SM's
collapses are deeper than the card's. The E169 section adds a post hoc reading that keeps the correction from overshooting:
SM's step from a neighbouring rung to a collapse is closer to the card's than ISO's in 5 of 6 pairs and than STRICT's in all 6.
So the 8 MB index remains a candidate cause of the collapses' extra time, and most of SM's failure is its retention level. The blog
point now reads: the published cache layout, taken literally, keeps almost nothing of a returning block past 32 MB, where the
card keeps about half, except at power-of-two panel strides, which run as if nothing were kept; the layout's 8 MB index is a
candidate cause that E169 will test.

### C4: E159 was not blind for G4 (minor)

**What the text said.** "**E159 held out** (G3 was blind on it)" and, in *What this does*, "E159 held out: 8.68 → 7.73 MHz,
1.94 → 1.81 W, 0.99 → 0.93 °C".

**The fault.** T_G's form and its 618 MHz come from E159's own H1 (E159's README, C1), as A2 says. E159 is held out of the
constants' fit only.

**Now.** "E159 held out of the constants' fit", with the note that T_G was designed from E159's H1. Post hoc, the dip clock's
value barely matters: at 600 or 650 MHz, E159 reads 7.80 / 7.71 MHz, 1.81 / 1.82 W and 0.93 / 0.92 °C, against 7.73 MHz, 1.81 W
and 0.93 °C ([`corrections.txt`](corrections.txt) C4).

### C5: P3's real kinds (minor)

**What the text said.** The lane's result quoted P3 as "fp32/fp16 real 0.99-1.02 vs 0.98-0.99". **Now:** fp32 real reads 0.99
on E136's g4k burst and 1.30 on its g2k burst (M8 0.99 for both), fp16 real 1.02 (M8 0.98). Check (iii) says the real-kind
agreement is shown on the g4k holds and bursts, not on every burst.

### C6: "out of sample for every model", and ISO's all-cells figure (minor)

**What the text said.** "on E146's ladder, out of sample for every model, 13.6% against ISO's 10.6%", and "rms over all 69
committed cells **13.0%**, against ISO's **7.3%**". **Now:** out of sample for the retention models, with MAB's prices in sample
on E146's L2 and D8 for every arm (B5's own words). ISO's 7.3% is partly in sample: 4.7% on E158's 42 cells, where its curve was
fitted, and 10.0% on E146's 27 cells (SM 12.3% and 14.0%, STRICT 13.7% and 10.8%).

### C7: check (i) (minor)

**What the text said.** "**(i) The die law works on bursts.** ... So the start-die term is right for a burst's first second."
*What this does*: "**For bursts,** the die law takes E158's zeros first-second board from 3.57 to **0.64 W** rms. That is a
start-die term for burst power, out of sample." The lane's blog point 3 credited the whole drop to the die's temperature.
**Now:** consistent with the die law's offset, not a test of its slope (the bursts start within 1.0 °C of each other; the
offset alone reads 0.62 W and the best constant offset 0.47 W); k_D 0.47 is the grid's middle, set in code before any output
(0.44 and 0.50 read 0.54 and 0.78 W); T_Z takes 3.57 → 2.59 W of the drop and the die law the rest.

### C8: "a falsifiable signature in E168" (minor, in the lane's result)

**What the result said.** "int8 cold starts are predicted 1.3 W higher in the window than warm ones (a falsifiable signature
in E168)". **Now:** E168 as designed cannot test it, since its three int8 holds all start warm. Check (ii) says so, and how a
card lane would add the test (A1 item 5). E168's design is unchanged.

### C9: the dip stated as governor behaviour (minor, in the lane's blog point)

**What the result said.** Blog point 2: "the governor briefly drops the clock to about 620 MHz at the start of each process
when the work draws more than about 56 W". Here, *The answer* called the term "the governor's process-boundary dips".
**Now:** both name a model term: the clock dips to about 620 MHz for a share of each process when the would-be 800 MHz power is
high. The gate is on the model's raised level; E159's own fold chose (0.06, 44 W); E159's measured dips were 5 of 7 at a process
start and 2 mid-process. *What it cannot say* adds the gate's post hoc check above its grid (C9 in
[`corrections.txt`](corrections.txt)).

### C10: the W8A8 "weight panel" (minor)

**Now:** the E168 section says that the W8A8 hold's matrix is one real tile pair cycled over the whole GEMM, so it tests one
real tile's bits in a GEMM, not a whole weight panel, and that the sparse50 hold's tiles are drawn.

### C11: the scorer's own hash (minor)

**Now:** [`frozen-sha256-e168-scorer.txt`](frozen-sha256-e168-scorer.txt) pins the scorer and every file its score path loads
(18 in all), checked with `shasum -a 256 -c` (A1 item 6). [`trace-scorer-e168.txt`](trace-scorer-e168.txt) lists that path's 16
files: 8 that `check` hashes, and 8 that it does not (the scorer and the 7 named in the E168 section). `score_e168.py` is
unchanged, so its `check` still prints CHECK OK (9 files).

### C12: an undisclosed rename (minor)

**Now:** D5.

### C13: two time stamps (minor, in the lane's result)

**What the result said.** "registration (02:26:29 PST)" and "pushed 02:49:40 PST". **Now:** `49575094` was committed at
02:26:25 and pushed at 02:26:29; `e39d06da` was committed at 02:49:40 and pushed at 02:50:04 (A1 item 8).

### Corrected in the lane's result only

The headline, `prediction_effect`, `numbers`, `open_issues` and `for_integration` now carry C1, C2, C4, C7 and C13; blog points
1, 2, 3 and 5 are rewritten (C2, C9, C7, C3), and point 4's "so data movement adds its own share" now reads "likely because".
