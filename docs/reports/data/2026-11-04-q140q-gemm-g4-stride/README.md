# Q140(q): G4 for a governed large GEMM's sustained path, and a block-stride term from the L3's public set mapping

*Wed 4 Nov 2026 (week 45), Q140's desk half, on the Intel, about 02:00-02:55 PST. Desk only: no card, no device command, no
ssh to a lab box, no Discord, no Modal, nothing from the private archive. It answers Q139's final critic's **rank 5** ("The large
GEMM's sustained path: G3 to G4") and **rank 6** ("A large GEMM's time per op on new shapes"). On the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) that is **item 1** ("Where a
large GEMM falls") and, through the power path, **item 6**. The owner's goal, 2 November 2026: to predict the power requirement and
heat generation of numeric computations as accurately as possible.*

***Registered first:** [`REGISTRATION.md`](REGISTRATION.md) and [`registration.json`](registration.json), committed in
`49575094` at **02:26 PST**, before any fit, score or prediction of this lane was computed.*

## The answer

**G4 = G3 + Q140(l)'s zeros level + the governor's process-boundary dips.** The registered forward rule kept two of the three
candidate terms and **rejected the start-die term**. Leave one session out over five sessions (65 sustained GEMM-pattern runs:
E119, E126, E136, E146 and E159), G4 reads the window board to **1.33 W** and the window die to **0.58 °C** rms, against G3
nested's 1.89 W and 0.76 °C. Both gains are resolved by a paired bootstrap. The clock does not move: **10.3 against 10.5 MHz**,
not resolved ([`loso-g4.json`](loso-g4.json); [`fit-g4.txt`](fit-g4.txt)).

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
| **G4 nested** | **10.34 (−4.17)** | 53 | **1.33 (−0.32)** | 57 | **0.58 (−0.06)** | 58 |
| G4 final (in sample) | 10.42 (−4.95) | 53 | 1.23 (−0.40) | 59 | 0.53 (−0.09) | 60 |
| paired bootstrap, G3 nested − G4 nested rms [95%] | [−1.29, +1.41] not resolved | | **[+0.41, +0.69]** | | **[+0.09, +0.26]** | |

**E159 held out** (G3 was blind on it): clock 8.68 → **7.73 MHz**, board 1.94 → **1.81 W**, die 0.99 → **0.93 °C**. Inside the
critic's bands: 8, 7 and 5 of 9 holds, against G3's 8, 5 and 6. So on E159, G4 would still fail the board and die rules (8 of 9).
**The 23 large GEMMs** (E136, E146, E159): G3 nested 11.4 MHz / 1.54 W / 0.82 °C → G4 nested **10.8 MHz / 1.29 W / 0.69 °C**.

**The stride term fails as registered.** SM puts E146's tile-level trace through the ET-SoC-1's public L3 map: shire PA[10:6],
bank [12:11], sub-bank [14:13], set [22:15], 4 ways, so the L3 index repeats every 8 MB. It uses true LRU (assumed) and the
runtime's buffer offsets, and nothing is fitted. It reproduces every L3-held rung and makes power-of-two panels collapse. But
past 32 MB it keeps almost none of a far B panel, where the card kept about half. So it reads every far shape 13-23% slow:

- rms over all 69 committed cells **13.0%**, against ISO's **7.3%** and STRICT's **12.6%**;
- on E146's ladder, out of sample for every model, 13.6% against ISO's 10.6%;
- F6 −17%, against ISO's +0.5%.

None of S1-S3 is met ([`stride-sm.txt`](stride-sm.txt)). Post hoc, random replacement on the same map reads 10.3% and
LRU-position insertion 13.5% ([`posthoc-sm-policies.txt`](posthoc-sm-policies.txt)). So the miss is not the replacement policy
alone. The likelier gap is the trace model (32 shires in lock step, E136's L2 model). No DRAM channel or bank term was
registered: no public source found gives the address-to-memshire interleave.

## The reported checks (registered; no selection)

From [`checks-g4.txt`](checks-g4.txt) / [`checks-g4.json`](checks-g4.json):

- **(i) The die law works on bursts.** E158's 42 zeros bursts never entered P0. Their first-second board reads P0 3.57 W high
  (mean −3.53); with T_Z, 2.59 W (−2.54); with T_Z and the one die law at 0.47 W/°C from 54.38 °C, **0.64 W** (+0.41). The bursts
  started at 47.3-48.3 °C, about 6.5 °C under the reference. So the start-die term is right for a burst's first second. It is
  wrong for a held window: T_D doubled the sustained loss, and post hoc the start offset alone (G3's in-run constant kept) still
  reads the board at 1.73 W against G4's 1.33 ([`posthoc-g4.txt`](posthoc-g4.txt) P1).
- **(ii) E159's three zeros holds.** Their window boards spread 0.057 W over starts of 52-57 °C. G4 spreads them **0.44 W**
  (G3 0.10), because its in-run constant runs from each run's start die. Its misses are −1.32 / −1.71 / −1.69 W, against G3's
  −2.45 / −2.49 / −2.43 W. The level is closer; the start dependence is not physical. G4's E168 predictions carry the same
  signature: an int8 hold from a cold start is predicted 1.3 W *higher* in the window than from a warm one.
- **(iii) T_S on E136's four other-kind runs.** The real kinds are unchanged, since M8's span fraction equals E95's r_real to
  1%. fp32 sparse50 goes **+0.38 → +2.96 W** (φ_M8 0.30). Post hoc, in E136's bursts the measured fraction is 0.45-0.60 for fp32
  sparse50, 0.66 for fp16 sparse50, and **0.77 for int8 sparse50 (M8 0.78) and 0.80 for int8 real (M8 0.79)**
  ([`posthoc-g4.txt`](posthoc-g4.txt) P3). So M8's kinds-loop fraction misses a float sparse GEMM, likely its memory path's own
  switching, and holds for int8. E168's two other kinds are int8.

## E168: G4's frozen predictions (critic rank 5)

[`predictions-e168.json`](predictions-e168.json) / [`.txt`](predictions-e168.txt), from [`predict_e168.py`](predict_e168.py) with
the frozen `g4.json`. Scorer: [`score_e168.py`](score_e168.py). Run `check` before the claim (9 frozen files,
[`frozen-sha256-e168.json`](frozen-sha256-e168.json)) and `score <session dir>` after. `selftest` puts E159's session through
the scorer's path and reproduces the fit's G4 predictions to 0.0004 ([`selftest-score-e168.txt`](selftest-score-e168.txt)).

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

## What this does to predicting power and heat

- **Terms tested** on a governed large GEMM's sustained power path (aifoundry2):
  - Q140(l)'s zeros level **carries**;
  - the governor's process-boundary dip **carries**;
  - the start-die term (one die law, 0.44-0.50 W/°C from 54.38 °C) **does not**;
  - M8's span fraction holds for int8 and real kinds and **fails for fp32 sparse50** (+2.6 W).
- **Out of sample, before → after**, leave one session out over 65 runs:
  - board 1.89 → **1.33 W** rms (G3 as frozen: 1.79);
  - window die 0.76 → **0.58 °C** (0.73);
  - clock 10.45 → **10.34 MHz**, not resolved (10.10).

  E159 held out: 8.68 → 7.73 MHz, 1.94 → 1.81 W, 0.99 → 0.93 °C.
- **Heat:** the chain is unchanged. The die gain comes from the power path: the window die's bias falls from −0.32 to −0.06 °C.
- **For bursts,** the die law takes E158's zeros first-second board from 3.57 to **0.64 W** rms. That is a start-die term for
  burst power, out of sample.
- **The time term:** the L3's public set map with true LRU does not predict time per op (13% rms against ISO's 7.3%). Time on a
  new shape stays ISO's 6-11%, with 8-13% single misses at power-of-two strides. Post hoc, strict LRU reads those collapses to
  within 6.5%.

## Registered against what happened, number by number

| # | registered (`49575094`) | what happened |
|---|---|---|
| A1 | base G3 at `91def7c4` | as registered; A0 at (0.1, 65.5) reproduces G3's committed in-sample 56-run score and E159's blind score to 0.0004 (`loso-g4.json` `reproduction_check`) |
| A2 | T_Z, T_D, T_G in order; T_S structural | as registered; T_Z and T_G kept, T_D rejected (D2 on T_G's clock) |
| A3 | 65 runs, five sessions, nested LOSO, grids | as registered |
| A4 | forward rule: ≥ 3 of 5 sessions and pooled | as registered; d_G chosen at its grid's top (0.12), see P2 |
| A5 | scored arms, paired bootstrap, checks (i)-(iii) | as registered (`loso-g4.json`, `checks-g4.json`) |
| A6 | E168's shapes, nine holds, nominal starts, the primary | as registered (D4) |
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

## What it cannot say

- **One card, one governor build (BL2 0.22.0), five sessions.** E146 gives two sustained runs; E159 is the only session that is
  new for G3.
- **G4's in-run leakage is an effective constant.** It is 0.2 W/°C from the run's start die. Its start dependence is not
  physical: E159's zeros spread 0.44 W predicted against 0.06 measured, and int8 cold starts are predicted to draw more. The one
  die law that fixes this structurally fails the clock. The board's die dependence differs between a burst's first second and a
  held window, and no form tested here carries both.
- **The dip term is a window-mean device.** It folds the boundary and mid-process dips into one boundary dip. Its gate (56 W)
  and length (12%) come from five sessions, and E159's fold chose (0.06, 44 W).
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

**Rerun**, from this directory:

- `nice -n 10 /usr/bin/python3 -B fit_g4.py > fit-g4.txt` (about 4 min, 4 workers);
- `/usr/bin/python3 -B checks_g4.py > checks-g4.txt`;
- `/usr/bin/python3 -B predict_e168.py > predictions-e168.txt`;
- `nice -n 10 python3 -B stride_sm.py > stride-sm.txt` (about 4 min, 4 workers), then `/usr/bin/python3 -B peaks_e169.py > peaks-e169.txt`;
- `/usr/bin/python3 -B score_e168.py check`, then `selftest > selftest-score-e168.txt`.

## Device commands sent

None. This lane opened no device node, took no card lock and sent nothing.
