# Dated note 1 beside the data README: term S's figures as the verifier's fixes leave them (Fri 6 Nov 2026, week 45; written from 03:57 PST)

*A dated note beside [`README.md`](README.md) (`6f9ae408`). It changes no committed file, and no verdict: **term S does not enter, on
the 95 steps that ran and on the 99 steps § 3.1 defines.** Everything below is **post hoc**: it was computed after term S's outputs and
after an independent verifier's reading of them.*

*The re-runs are the ones registered in the registration's
[dated note 2](../../../../tools/claims-v3/m10-s/REGISTRATION.md.dated-note-2.md), committed with its code before any output in
`1c43f5cb` (03:51:16 PST). They were written by:*
- *[`term_s_note2.py`](../../../../tools/claims-v3/m10-s/term_s_note2.py) (`1c43f5cb`): the census, the checks and the comparison;*
- *its `fit99` v2, [`term_s_note2_v2.py`](../../../../tools/claims-v3/m10-s/term_s_note2_v2.py) (`f8c3c9be`, 03:53:31). v1's `fit99`
  stopped on its first run before writing any output: its own reproduction check keyed E102's fp32 and fp16 `bj_0` alike.*

*Both run on `term_s_v2.py` unchanged, as one slot job each on the Intel (03:51:56 and 03:53:51 PST). The hash list is
[`SHA256SUMS-note2`](SHA256SUMS-note2).*

## 1. The training set is 99 steps, and term S still does not enter

**The census.** T_S on every committed tile of the seven lists (`note2-census-output.txt`) finds 99 single B bits: the 95 plus E67's
grid margins `ix_b0`, `ix_b8`, `ix_b16` and `ix_b22`, and no other. E67's four:
- A is one word, 0x3fb10bd0, over the grid's base `ix_z`;
- aifoundry3 at 600 MHz;
- the step factor on M10's footing is 0.99638 (E67's leak 0.17545 W/°C);
- on the law, FL3's k_s is 0.3612 W/°C at T_mid 58.875 °C.

**The registered fit, unchanged, on both sets** (`note2-term-s-reg-99.json`, `note2-term-s-law-99.json`; both stop unless the 95
committed steps reproduce, and they reproduce to 0.0 W). Errors are measured − predicted, in W.

| | 95 steps (as run) | 99 steps (§ 3.1's set) |
|---|---:|---:|
| S0, M10 as frozen: rms (bias) | 0.222 (−0.103) | 0.218 (−0.099) |
| S3, one value per position: rms (bias) | 0.179 (−0.022) | 0.179 (−0.021) |
| **E1**, S3 − S0 [the registered step bootstrap] | −0.043 [−0.083, −0.006]: holds | −0.040 [−0.077, −0.006]: holds |
| **E2**, aifoundry3 / card 1 | −0.054 / **+0.018**: fails | −0.047 / **+0.008**: fails |
| **E3**, pool 6's and 7's 13 S kinds | **+0.008** [−0.014, +0.042]: fails | **+0.008** [−0.014, +0.042]: fails |
| enters | **no** | **no** |
| σ_S, fp32 / fp16 | 0.167 / 0.217 | 0.168 / 0.217 |
| on the law: S0 → S3; E1; E2 card 1; E3 | 0.222 → 0.175; −0.047 [−0.087, −0.009]; +0.018; +0.005 | 0.218 → 0.175; −0.043 [−0.080, −0.009]; +0.008; +0.005 |

- **E67's four steps read nearly unbiased under M10 as frozen:** S0 bias +0.002 W, rms 0.102 W. Left out in turn, S3 reads 0.216 W
  there (bias +0.162 W). So the per-position term moves E67's steps the wrong way, as it moves pool 8's.
- **The 99-step S3 table differs from the 95-step one only at fp32 bits 0, 8, 16 and 22.** At aifoundry3's nominal rate:

  | fp32 bit | 95 steps | 99 steps |
  |---:|---:|---:|
  | 0 | −0.38 W | −0.32 W |
  | 8 | −0.12 W | −0.12 W |
  | 16 | −0.01 W | −0.01 W |
  | 22 | −0.15 W | −0.09 W |

  No pool-8 class-S tile sits at those positions. They sit at fp32 bits 7, 13, 19 and 26, and fp16 bits 2, 4, 7 and 10.
- **Every pool-8 figure is therefore unchanged:**
  - 600 MHz: 0.273 → 0.357 W and 0.238 → 0.323 W;
  - the 800 MHz cap: +1.062 → +1.183 W and +0.713 → +0.827 W;
  - B1: +0.092 → +0.120 W and +0.105 → +0.132 W, and +0.018 / +0.082 W without class S;
  - on the law: 0.262 → 0.354 W and 0.227 → 0.304 W.
- **Strike** "E67 has no B single bit" and "no E67 item passes" wherever they are quoted. Results § 1's "95 steps in six runs" is the
  run as made. § 3.1's set is 99 steps in seven runs: 79 fp32 and 20 fp16, 85 on aifoundry3 and 14 on card 1.

## 2. M10's step error by list and A word, post hoc (n = 4 and n = 5): the A = 1.0 hint does not hold

The verifier read E67's unbiased steps as a hint that M10's over-pricing of the lists goes with A = 1.0. E65's A = π steps contradict
that. They hold a dense A word too, and they read the most over-priced of all (`note2-checks.json` › `by_list_and_A_99`):

| A word (aifoundry3 and card 1) | steps | S0 bias (rms), W |
|---|---:|---:|
| fp32, A = 1.0 | 70 | −0.066 (0.198) |
| fp32, A = π (E65's `bpi_*`) | 5 | **−0.438** (0.456) |
| fp32, A = 0x3fb10bd0 (E67's grid) | 4 | **+0.002** (0.102) |
| fp16, A = 1.0 | 20 | −0.149 (0.212) |

At the same four positions, on the same card at 600 MHz, the S0 residual by list and A word:

| fp32 bit | E65, A = 1.0 | E65, A = π | E67, A = 0x3fb10bd0 |
|---:|---:|---:|---:|
| 0 | −0.309 | −0.537 | −0.071 |
| 8 | +0.058 | −0.450 | −0.098 |
| 16 | −0.031 | −0.434 | +0.013 |
| 22 | −0.226 | −0.204 | +0.163 |

What separates E65's A = π steps from E67's at the same positions is not resolved here. Candidates are the session and the B base
words. E67's grid passes also ran under another user's host load, at a lower launch rate; the measured rate is the one used. This is a
reading, never a test.

## 3. E1 resampled by run, post hoc

A run is one list: its session, its base words and its reduction. The by-run interval comes from 10,000 draws over runs. The table
gives seed 146; seeds 147 and 148 agree with it to 0.002 W (`note2-checks.json` › `E1_by_runs`). The step bootstrap is the registered one, and this code reproduces it exactly.

| set | S3 − S0, W | step bootstrap (registered) | by run | draws ≥ 0 | jackknife SE over runs |
|---|---:|---|---|---:|---:|
| 95 steps, M10's footing | −0.043 | [−0.083, −0.006] | [−0.067, **+0.001**] | 3.1-3.3% | 0.020 |
| 95 steps, the law | −0.047 | [−0.087, −0.009] | [−0.074, **+0.001**] | 3.0-3.3% | 0.022 |
| 99 steps, M10's footing | −0.040 | [−0.077, −0.006] | [−0.063, **+0.007**] | 4.6-5.0% | 0.021 |
| 99 steps, the law | −0.043 | [−0.080, −0.009] | [−0.069, **+0.006**] | 4.2-4.6% | 0.022 |

**By run** (95 steps, M10's footing): E65 −0.066, E70 −0.230, E79 −0.035 and E147 −0.088 W; **E102 +0.018 and E134 +0.043 W read
worse with S3**. With the 99 steps, E67 reads +0.114 W, also worse.

So E1 holds by its registered step bootstrap in every set, but **resampled by run its interval reaches +0.001 to +0.009 W** (over the sets and seeds): the lists'
held-out gain is not resolved at the run level.

## 4. The structure reading (results § 5), corrected, post hoc

M10's committed held-out errors fall into five classes by T_S on each tile's bytes (`posthoc-structure.json`). They cover M10's 737
float rows of its 959; int8 rows are not classed. Results § 5 left out the fifth class, "zero, eight lane words", and mixed steps with
whole tiles:

| class | rows | kind of row | M10 held-out bias (rms), W |
|---|---:|---|---:|
| a single B bit, one base word in every lane | 23 | whole tiles | **+0.098** (0.251) |
| a single B bit, eight base words: E102's 10 on card 1 and E127's `q_chk` | 11 | whole tiles | **+0.008** (0.177) |
| a single B bit, eight base words: E147's 15 | 15 | steps, each over its own zero | −0.069 (0.198) |
| zero, one word in every lane | 34 | whole tiles | **+0.069** (0.096) |
| zero, eight lane words: E102's `hq` zeros on card 1 | 3 | whole tiles | **+0.078** (0.090) |
| everything else | 651 | | −0.024 (0.186) |

**Like for like, whole tiles** (`note2-checks.json` › `structure.whole_tile_comparison`):
- **One word in every lane:** single bits − zeros = +0.098 − 0.069 = **+0.029 W** (card 1 alone +0.023 W).
- **Eight lane words:** single bits − zeros = +0.008 − 0.078 = **−0.070 W** (card 1 alone −0.095 W).
- E147's steps, eight words over their own zeros, read −0.069 W, the same as that difference.

**The reading the records quote** (post hoc, not a test):
- M10 under-prices constant-lane tiles by about 0.07 W whether the lanes share one word or eight. The eight-word case has only 3 rows,
  all on one card.
- M10 prices a single bit's own step about 0.10 W higher when the lanes hold eight words than when they hold one: −0.07 W against
  +0.03 W.
- The lists, as steps over their own zeros, see only the second part.

So results § 5's "the class-S miss follows one word in every lane, not the position of the bit" is **only partly supported**, and the
bit's position is never tested. A one-word term should be registered against both parts, the constant-lane level and the bit's step,
and against A's word (§ 2).

## 5. The registered band, computed post hoc on pool 8's class S at 600 MHz

The band is h_S = √(h_M10² + (k_M10 σ_S)²), with k_M10 2.002 and σ_S 0.167 W (fp32) and 0.217 W (fp16). Here h_M10 is the scorer's own
M10 band half-width (`scored.json` › `M10_primary_95`): 0.31-0.41 W, which widens to 0.53-0.55 W (`note2-checks.json` › `band_pool8`).

| | aifoundry3 (E171) | card 1 (E172) |
|---|---:|---:|
| M10 inside its own band (the scorer's own count) | 7 of 8 | 7 of 8 |
| M10 + term S inside the term's band | 7 of 8 | 8 of 8 |

The term's band covers more only because it is wider. The rms grows (0.273 → 0.357 W and 0.238 → 0.323 W), and nothing enters.

## 6. Labels, hashes, times and roundings

- **S0 is "M10 as frozen", in sample on 25 of its 95 steps.** M10's own fit saw those rows: E147's 15 steps, and the item and zero rows
  of 10 of E102's 14. On those rows M10's held-out errors read 0.198 W rms against 0.194 W in sample on both lists. That optimism of
  0.004 W moves no figure (`note2-checks.json` › `S0_in_sample`).
- **Six of `law-k.json`'s `law_sha256` values are path-dependent:** E78, E82, E86, E90, E92 and E95.
  - Each is the hash of the reduction that the committed run wrote. Those reductions' `dirs` lists name that run's scratch directory.
  - This lane re-ran the committed code. The six reductions are identical apart from `dirs`, and the other 24 are identical byte for
    byte. 25 of `law-k.json`'s 31 entries are identical, and the other 10 outputs and both self-tests come out byte for byte
    (`note2-compare-output.txt`).
- **True commit times** (the registration's dated note 2, item 8): `REGISTRATION.md` 02:28:32 PST, not "about 02:31"; `term_s.py`
  02:34:39; this README and dated note 1 02:55:32.
- **Two roundings:**
  - P8-M1 on the law for E171 is −0.052 W **[−0.105, −0.003]** (results § 4 says −0.106);
  - the exponent bits 28-30's measured steps run **0.74-1.10 W**, not 0.80-1.10 (E65's bit 30 is 0.735 W).

  Results § 1's other figures check: fp32 bit 0 is M10 0.92-0.96 W against 0.60-0.62 W measured, and the lists' agreement median is
  0.087 W, the median span over 27 positions.

## Files

| file | what |
|---|---|
| [`note2-census-output.txt`](note2-census-output.txt) | the census's summary: 99 single B bits in seven lists |
| [`note2-census-fit99.json`](note2-census-fit99.json), [`note2-fit99-output.txt`](note2-fit99-output.txt) | the census in full, and the 99-step fit's summary on both footings |
| [`note2-term-s-reg-99.json`](note2-term-s-reg-99.json), [`note2-term-s-law-99.json`](note2-term-s-law-99.json) | the registered fit on the 99 steps, in `term-s-reg.json`'s and `term-s-law.json`'s form, with the frozen 99-step table |
| [`note2-checks.json`](note2-checks.json), [`note2-checks-output.txt`](note2-checks-output.txt) | E1 by runs; S0 in sample; by list and A word; the five classes; the band; the roundings |
| [`note2-compare-output.txt`](note2-compare-output.txt) | this lane's re-run of the committed code against this directory |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | these files, this note, the registration's note 2 and the code |

**Re-run** from the top of the tree, with numpy 1.26 on one core:
- `python3 -B tools/claims-v3/m10-s/term_s_note2.py census`;
- `python3 -B tools/claims-v3/m10-s/term_s_note2_v2.py fit99 --out <dir> --tmp <dir>`;
- `python3 -B tools/claims-v3/m10-s/term_s_note2.py checks --out <dir>`, which reads the 99-step files in `<dir>`.

SPDX-License-Identifier: Apache-2.0
