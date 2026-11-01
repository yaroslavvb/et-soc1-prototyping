# E81 — the DRAM pattern question: is a two-value image cheap because it repeats? (Q130)

*Dated 1 Nov 2026: which mechanism carries this effect is taken up by [E99](../2026-11-01-e99-dram-mechanism/README.md): read data-bus inversion behaves as live and the 1 W floor is gone, on one card; narrowed, not closed.*

*Corrected after verification, Sat 31 Oct 2026 (§ [Corrections after verification](#corrections-after-verification),
C1–C8). The compute-rail statement is narrowed: going from zeros to data adds 0.075–0.153 W on the minion rail, and
the pattern effects never reach it. The intervals are now said to be statistical at the registered leakage slope,
and each headline number is given at the two registered sensitivities. The per-event account is one candidate
encoding, with DBI-DC beside it and its code committed. An interim look is disclosed. No number in `dp.json`, its two
leakage arms, `runs.csv` or the post-hoc dip view changed, no verdict changed, and no registered file changed.*

## Results

*Ten passes, `p8110`–`p8119`, Sat 31 Oct 2026 14:49:35–15:13:02 PDT on aifoundry3 card 0, 600 MHz, `--harts 1`
(1,024 harts), eleven DRAM items and the drift anchor per pass, after a smoke (`p8101`, 14:47:47). **22.8
card-minutes** of the registered 45. Every pass `block.json` `"status":"ok"`, 130 runs, **no run-gate failure**.
Pre-registered in `14f219ef` (14:45 PDT) before the claim (14:47:21) and the first launch. Reduced with `reduce.sh`
(the registered `tools/claims-v3/dp/reduce_dp.py`, unchanged). Pass 8110 is the registered warm-up and pass 8119 is
set aside by the registered drift rule (−0.647 W), so **the headline is eight passes, 8111–8118** (df = 7). Every
number below is from `dp.json` `headline` unless it says otherwise. Intervals are 95 % t over the eight headline
passes at the registered `auto` leakage slope (0.0132 W/°C). The two registered sensitivities move the headline
numbers by up to −0.20 W, more than some of those intervals (§ [The leakage footing](#the-leakage-footing)).*

**The hub's question has a two-part answer.** A two-value alternating image is cheaper than random data at the same
changed-bit and carried-one counts **partly because it repeats, but mostly because of where its ones sit inside each
line:**

> | at E75's k256 counts (256 bits change between lines, 256 ones per line) | W | pJ per 64 B line | share |
> |---|---:|---:|---:|
> | E75's own image (`dp_c2`: two values, ones in contiguous runs) over zeros | 1.866 [1.751, 1.980] | 1,591 | — |
> | **the arrangement:** the same bits scattered inside each line (`dp_s2 − dp_c2`) | **+0.996** [0.936, 1.055] | **+849** | **61 %** [57, 65] |
> | **the period:** 8,192 distinct random lines instead of a fixed scattered 2-cycle (`dp_bern − dp_s2`)¹ | **+0.640** [0.574, 0.706] | **+546** | **39 %** [35, 43] |
> | the whole step, E75's image → random bits at its counts (`dp_bern − dp_c2`) | **+1.636** [1.600, 1.671] | +1,395 | 100 % |
>
> *95 % t intervals over the eight headline passes, at the registered leakage slope. At the registered sensitivities,
> 0.2936 and 0.3803 W/°C, the arrangement reads 0.929 / 0.909 W, the period 0.654 / 0.658 W and the whole step
> 1.583 / 1.567 W: a 58.5 / 41.5 and a 57.7 / 42.3 split (`dp-leak0.2936.json`, `dp-leak0.3803.json`
> `headline.contrasts_W`, `headline.shares`). A line is one 64 B DRAM line; the line rate is measured,
> 1.1729 × 10⁹ lines/s (75.1 GB/s of lines).*
>
> *¹ `dp_bern` differs from `dp_s2` in two ways besides its period. Its consecutive lines differ in a random set of
> bit positions, where `dp_s2`'s always differ in the same 256 (π of bits 0–255). And its counts per line spread by
> about ±11 bits around 256, where `dp_s2`'s are exactly 256: the two match only on average, to 0.05 %
> (`gen/counts.json`). The registration expected that spread to move nothing measurable, since E75's DRAM response to
> ones is near-linear around 256. "The period" is the short name for this step to random lines. A scattered 4-line
> cycle, whose consecutive lines differ in four different sets of 256 positions, costs no more than the 2-cycle
> (below).*

So **"compressible" fits only the smaller part.** A short repeat is enough to get all of what repetition saves: a
scattered **4-line** cycle costs what a scattered 2-line cycle costs (`per_s_2to4` +0.030 W [−0.061, +0.122], absent
by the registered rule at all three leakage slopes), and the whole period effect appears between four distinct lines
and 8,192 (`per_s_4tolong` +0.610 W [0.496, 0.723]). The arrangement costs at every period: **+0.547 W** [0.388,
0.706] at period 1 (where no line ever changes), **+0.996** at period 2 and **+1.124** [1.034, 1.213] at period 4.

**What this does to E75's "36.6 %".** At random's own counts the gap is measured directly here, with no model:

| step, at random's counts (192 changes, 290 ones per line) | W over zeros | share of the chord |
|---|---:|---:|
| a contiguous two-value image (`dp_c2r`) | 2.063 [2.028, 2.098] | **64 %** |
| + scattering its ones (`dp_s2r − dp_c2r`) | +0.808 [0.679, 0.938] | **+25 %** |
| + the rest, to random floats (`dp_random − dp_s2r`) | +0.351 [0.105, 0.597] | **+11 %** |
| = the zeros-to-random chord (`dp_random − dp_zeros`) | **3.222** [3.093, 3.350] (E75: 3.250) | 100 % |

**An image with random's counts in E75's arrangement** (two values, ones in contiguous runs, a 2-line period)
**costs 64 % of the chord** when it is measured. E75's two-count model (a price per changed bit and per carried one,
fitted on its two arms) gave those counts 36.6 %. It extrapolated to a (k = 0, w = 0) intercept that sits 0.81–1.43 W
above the zeros anchor, because the first carried ones cost the most, and it counted that step as unexplained (E75's
`README.md` lines 45–46; its `mf.json` `levels.dram.two_term_model[].zeros_residual_W`, −0.81 to −1.43 W). The counts
alone do not set the cost: the same counts scattered (`dp_s2r`) cost 2.871 W, 89 % of the chord. Of the 36 % the
contiguous image leaves (1.159 W [1.032, 1.286]), **scattering its ones closes 0.808 W**. That is 70 % as a ratio of
the means, and 72 % [57, 86] as the mean of the per-pass ratios (`shares.arrangement_share_of_gap_r`). The remaining
0.351 W is a net: the long period's +0.640 W (measured on random bits, `period_s`), less the 0.280 W that random
floats save over random bits (`random_minus_bern`), less 0.010 W for the two scattered images' counts
(`dp_s2 − dp_s2r`).

**Random floats cost 0.280 W [0.226, 0.334] less than random bits** (`dp_random − dp_bern`), despite carrying 32
more ones per line. A likely part of the reason is that the top byte of every float in [0.5, 2) is the same (0x3F),
so a quarter fewer bits change between consecutive words and lines (190 against 256 per line) and between a line's
two halves (95 against 128; `gen/counts.json`). But the post-hoc count model below accounts for only 89 of the 239 pJ
per line (`posthoc-counts.txt`), so most of the saving is not explained here.

**Most of it is off the compute rail, but not the step from zeros to data** (post hoc, D4: `posthoc_rail.py`,
`posthoc-rail.txt`, from `runs.csv` `rail`, read as within-pass differences like the board). Going from zeros to any
data image raises the minion rail by 0.075–0.153 W: random +0.152 W [0.097, 0.208], 4.7 % of the board's 3.222 W
chord, and `dp_c2` +0.099 W [0.057, 0.141]. So reading non-zero data costs something in the cores too, a few per
cent of the board's step. The step does not follow the window's temperature (`dp_c1` warms 0.66 °C over its launch
reading and adds 0.153 W; `dp_s2` warms 0.98 °C and adds 0.101 W), so it is unlikely to be the rail's own leakage.
**The pattern effects never reach the rail.** No arrangement or period contrast moves it by more than 0.08 W either
way: `arr2` +0.003 W [−0.038, +0.043] and `period_s` +0.033 W [−0.012, +0.078], against +0.996 and +0.640 W on the
board. The pattern-dependent part of a DRAM load's energy, the 1.6 W this experiment is about, is on the memory side:
the DRAM, its interface and the paths between them.

### Every item

| item | period | arrangement | k | w | W over zeros (95 %) | pJ per line |
|---|---:|---|---:|---:|---:|---:|
| `dp_zeros` | 1 | — | 0 | 0 | 0 (32.252 W absolute) | 0 |
| `dp_c4` | 4 | contiguous (Hadamard) | 256 | 256 | 1.768 [1.645, 1.891] | 1,507 |
| `dp_c2` = E75's k256 bytes | 2 | contiguous | 256 | 256 | 1.866 [1.751, 1.980] | 1,591 |
| `dp_c1` = E75's k0 bytes | 1 | contiguous | 0 | 256 | 2.046 [1.880, 2.211] | 1,744 |
| `dp_c2r` | 2 | contiguous | 192 | 290 | 2.063 [2.028, 2.098] | 1,759 |
| `dp_s1` | 1 | scattered | 0 | 256 | 2.593 [2.384, 2.802] | 2,210 |
| `dp_s2` | 2 | scattered | 256 | 256 | 2.861 [2.720, 3.003] | 2,440 |
| `dp_s2r` | 2 | scattered | 192 | 290 | 2.871 [2.738, 3.004] | 2,448 |
| `dp_s4` | 4 | scattered (Hadamard) | 256 | 256 | 2.892 [2.722, 3.061] | 2,465 |
| `dp_random` | 8,192 | floats in [0.5, 2) | 190.2 | 288.3 | 3.222 [3.093, 3.350] | 2,747 |
| `dp_bern` | 8,192 | random bits | 256.1 | 256.0 | **3.501** [3.394, 3.609] | **2,985** |

Read down the table: every contiguous image costs less than every scattered one, whatever its period or counts; the
two long-period images cost the most; and among images of the same arrangement and period, the counts move little
(E75's own k-arm finding, reproduced: `dp_c1 − dp_c2` = +0.180 W [0.108, 0.252], E75 +0.20). At E71's leakage slope
(0.3803 W/°C) every item reads 0.03–0.20 W lower (`dp-leak0.3803.json`), and those three readings still hold, though
`dp_c1` and `dp_c2r` trade places.

### Scoring

| # | prediction (registered) | reading | verdict |
|---|---|---|---|
| P1a | chord 2.65–3.85 W (E75 3.250) | **3.222** [3.093, 3.350] | **PASS** |
| P1b | `dp_c2 − dp_zeros` 1.30–2.50 W (E75 1.933) | **1.866** [1.751, 1.980] | **PASS** |
| P1c | `dp_c1 − dp_c2` −0.10 to +0.50 W (E75 +0.20) | **+0.180** [0.108, 0.252] | **PASS** |
| P2 | arrangement at period 2, 0.40–1.60 W | **+0.996** [0.936, 1.055] | **PASS** |
| P3a | arrangement at period 1, 0.40–1.60 W | **+0.547** [0.388, 0.706] | **PASS** |
| P3b | arrangement at period 4, 0.40–1.60 W | **+1.124** [1.034, 1.213] | **PASS** |
| **P4** | **no period effect** (`dp_bern − dp_s2` inside ±0.30 W) | **+0.640** [0.574, 0.706], present | **FAIL** — the hub's alternative holds in part: a long period costs |
| P5 | `dp_random − dp_s2r` within ±0.35 W | **+0.351** [0.105, 0.597] | **FAIL**, by 0.0007 W on the mean (+0.35066, `scored.P5_closure_at_random_counts.mean_W`); its interval is wide because two dip samples in one pass (8115) pull `dp_s2r` down (below) |
| P6 | `dp_random − dp_c2r` 0.70–1.80 W | **+1.159** [1.032, 1.286] | **PASS** |
| P7 | `dp_random − dp_bern` −0.30 to +0.45 W | **−0.280** [−0.334, −0.226] | **PASS**, at the low edge: random floats are *cheaper* than random bits, which the registration did not expect (it expected +0.1 W from the extra ones) |

**8 of 10 pass.** The registered hub rule reads **"both: the repetition and the arrangement each cost"**
(`dp.json` `hub.verdict`). Every verdict is the same at the two leakage sensitivities (`dp-leak0.2936.json`,
`dp-leak0.3803.json`; the registered auto slope is 0.0132 W/°C, from 47 runs): the arrangement at period 2 reads
0.996 / 0.929 / 0.909 W and the period 0.640 / 0.654 / 0.658 W across auto / 0.2936 / 0.3803 W/°C.

### The leakage footing

The registered estimator corrects each run to its launch reading with the `auto` leakage slope, which these 47 runs
put at 0.0132 W/°C. That barely corrects: the windows warm 0.44–0.98 °C over their launch readings on average per
item (`posthoc-rail.txt`) and at most 1.2 °C in any run (`runs.csv` `t_win − start_c`), so no run moves by more than
0.016 W. The registration reports two sensitivities: 0.2936 W/°C (E66's slope, measured on aifoundry2) and
0.3803 W/°C (E71's measured idle slope for this card, over the 58–62 °C band these runs launch in).
The difference between the three is a systematic, and the statistical intervals do not include it:

| contrast | auto [95 %] | 0.2936 W/°C [95 %] | 0.3803 W/°C [95 %] |
|---|---:|---:|---:|
| `arr1` (s1 − c1) | +0.547 [0.388, 0.706] | +0.529 [0.341, 0.718] | +0.524 [0.311, 0.737] |
| `arr2` (s2 − c2) | +0.996 [0.936, 1.055] | +0.929 [0.834, 1.024] | +0.909 [0.786, 1.031] |
| `arr4` (s4 − c4) | +1.124 [1.034, 1.213] | +1.031 [0.873, 1.188] | +1.002 [0.799, 1.205] |
| `arr2r` (s2r − c2r) | +0.808 [0.679, 0.938] | +0.759 [0.633, 0.886] | +0.744 [0.607, 0.881] |
| `period_s` (bern − s2) | +0.640 [0.574, 0.706] | +0.654 [0.606, 0.702] | +0.658 [0.610, 0.707] |
| `per_s_2to4` (s4 − s2) | +0.030 [−0.061, +0.122] | +0.064 [−0.045, +0.172] | +0.074 [−0.052, +0.200] |
| `per_s_4tolong` (bern − s4) | +0.610 [0.496, 0.723] | +0.591 [0.466, 0.715] | +0.585 [0.443, 0.726] |
| `per_c_2to4` (c4 − c2) | −0.098 [−0.150, −0.046] | −0.038 [−0.155, +0.079] | −0.020 [−0.182, +0.143] |
| `s1_to_s2` (s2 − s1) | +0.269 [0.115, 0.423] | +0.195 [0.061, 0.329] | +0.172 [0.029, 0.315] |
| `pattern_total` (bern − c2) | +1.636 [1.600, 1.671] | +1.583 [1.517, 1.650] | +1.567 [1.478, 1.656] |
| `resid_r` (random − s2r, P5) | +0.351 [0.105, 0.597] | +0.359 [0.119, 0.600] | +0.362 [0.121, 0.603] |
| `random_minus_bern` | −0.280 [−0.334, −0.226] | −0.282 [−0.331, −0.232] | −0.282 [−0.344, −0.221] |
| `chord` (random − zeros) | +3.222 [3.093, 3.350] | +3.083 [2.926, 3.241] | +3.040 [2.860, 3.220] |
| arrangement share of `pattern_total` | 0.609 [0.571, 0.647] | 0.585 [0.545, 0.626] | 0.577 [0.527, 0.626] |

*From `dp.json`, `dp-leak0.2936.json` and `dp-leak0.3803.json`, `headline.contrasts_W` and `headline.shares`.*

Every registered verdict is the same at all three slopes. Five contrasts move outside their `auto` interval at a
sensitivity: `arr2`, `arr4`, `pattern_total` and `chord`, and `per_c_2to4` (below). Every item over zeros reads
0.03–0.20 W lower at 0.3803 W/°C (`dp_s2` 2.861 → 2.664 W). Two readings do not survive the footing, so this README
does not make them.
`per_c_2to4` (a contiguous 4-cycle *cheaper* than a contiguous 2-cycle, −0.098 W at `auto`) reaches zero at both
sensitivities. `s1_to_s2` (reported, not scored) goes from present to unresolved. `c1_minus_c2` also goes from absent
to unresolved at 0.3803 W/°C, though P1c, a range test on the mean, passes at all three.

### The board meter's dips (a labelled post-hoc view; no registered verdict rests on it)

aifoundry3's board reading now and then lands on the 1–2 ms gap between two of a run's 0.4 s launches, and the
service processor holds the near-idle value for two 100 ms samples: E82's amendment A2 found the same on aifoundry1
card 1 the same afternoon. The registered estimator has no gate for it. **85 dip samples in ten passes, 12 of them
inside a run's [1 s, 3 s) window** (`dips.json`): two each in 8115's `dp_s2r` (−0.85 W on that run) and `dp_zeros`, in
8119's closing `anchor_pi` (the whole of 8119's −0.647 W drift) and in the warm-up's `dp_c1`, and one each in 8111's
`dp_s1`, an `anchor_pi` of 8113, 8114's `dp_s4` and 8115's `dp_c2r`. With those samples removed by E82's definition and every gate unchanged (`posthoc_dips.py`,
`dp-posthoc-dips.json`, nine headline passes because 8119 is no longer set aside): arrangement at period 2 **+1.012**,
period **+0.635**, the whole step **+1.647**, and P5 reads **+0.237** [0.196, 0.277] — inside its range. **The
registered result stands: P5 is a FAIL**; the view shows that its failure is the meter's, and that no other verdict
moves.

### What the arrangement and the period cost per event (derived; the count model is post hoc)

The registered derived reading (`derived_not_scored`) divides each arrangement contrast by the toggles it adds between
consecutive 16-, 32- and 64-bit pieces of the stream, under an in-order mapping of a line onto a narrower path. **No
single width fits all four**: at 16 bits the arrangement costs 2.1, 4.2, 5.3 and 3.4 pJ per added toggle at periods 1,
2, 4 and at random's counts; at 64 bits the period-4 contrast even *removes* toggles (−35.5) while costing +1.124 W. So
the arrangement is not "toggles on one narrow bus".

**Post hoc, labelled (D2): a description of these ten items, not a measurement.** The model is a least-squares fit
with no intercept over the ten data items. It tried every 2-, 3- and 4-subset that contains `w` of seven per-line
counts:

- `w`, the ones;
- `k`, the changes between consecutive lines;
- `beat16`, `beat32` and `beat64`, the toggles between consecutive 16-, 32- and 64-bit pieces;
- `half`, the bits that differ between a line's two 32 B halves;
- `k_if_long`, which is k counted only when the stream has more than four distinct lines. This count was built after
  the data showed that a 4-line cycle costs what a 2-line one does.

That makes 41 models (`tools/claims-v3/dp/posthoc_counts.py`; all 41 are printed in `posthoc-counts.txt`). The best
fits the ten items to **71 pJ per line rms** against 1,500–3,000 pJ per line (largest residual −132 pJ, `dp_s1`):

    pJ per line over zeros ≈ 4.1 × (ones) + 3.9 × (toggles between consecutive 16-bit pieces)
                           + 2.4 × (toggles between the line's two 32 B halves)
                           + 2.2 × (bits changed between consecutive lines, only when the stream has > 4 distinct lines)

**One candidate reading of that shape** has three parts. A 64 B line moves as 16-bit beats over the DRAM interface
(the ones and the beat-to-beat toggles). It moves as two 32 B halves on a wide path. And there are paths that each
carry only every N-th line of a stream, with N a multiple of 4. If consecutive lines are spread over channels or banks
that way, a period of 2 or 4 gives every such path one constant value, so nothing on it ever changes. That would also
explain why E75's DRAM k-arm (changes between consecutive lines of one hart's stream) was flat.

**A second candidate encoding fits about as well: LPDDR4x read DBI-DC**, the data-bus inversion that E75's
registration named as a risk. With DBI-DC, a byte with more than four ones is sent inverted, with its DBI pin driven
high. So the cost goes with the pins driven high, not with toggles. Contiguous runs make whole 0xFF bytes, each sent
as one high pin (32 per line). Scattered or random bits leave about 3.4 high pins in every byte (205–226 per line).
Swap `beat16` for that count and the fit is 113 against 128 pJ per line rms at three counts (`w`, the count and
`k_if_long`), and 83 against 71 at four (with `half`). See `posthoc-counts.txt`, head to head; that count was added
after the verification named DBI-DC. Ten items do not separate the two encodings, and neither is measured. This
card's read-DBI setting, its address-to-channel map and its data-pin mapping are not known here.

## What ran, and what was registered

| | registered (`tools/claims-v3/dp/`, `14f219ef`) | happened |
|---|---|---|
| command | E75's DRAM command unchanged: `flw_pat --harts 1 --seconds 4 --window 240000000 --stride 64 --slice-bytes 131072 --region 131072`, E75's binary | the same; the dry run printed exactly the eleven registered command lines (`logs/e81-dry.log`) |
| items | eleven DRAM items (E75's k0 and k256 bytes, their scattered twins, a Hadamard 4-cycle contiguous and scattered, `bern:0.5`, a contiguous and a scattered 2-cycle at random's counts, E75's zeros and random) + `anchor_pi` first and last | all of them, every pass |
| harness | E75's `mf/block.sh` and `mf/queue_mf.sh` unchanged, `MF_GEN=build/dp-gen MF_EXPN=dp`; `runitems.py` | the same; all twelve harness files hashed identical on the box and the Intel before the first launch (`logs/e81-box.sha`) |
| passes | smoke 8101, then 8110–8119; 8110 the warm-up, headline 8111–8119 | smoke 8101 (14:47:47–14:49:22, every launch ok); passes 8110–8119 (14:49:35–15:13:02, 1.99–2.22 min each). 8110 the warm-up; **8119 set aside** by the drift rule (−0.647 W: a meter dip in its closing anchor, above); headline 8111–8118, eight passes, df = 7 |
| budget | at most 45 card-minutes; `build/mf-STOP` at 38 | **22.8 card-minutes** (smoke 1.61 + passes 21.20); the 38-minute stop never acted; card session 14:47:45–15:13:33 PDT |
| claim | one post in `#community-lab` after the registration and before the first launch, edited at the release | posted 14:47:21 PDT, released 15:17 PDT by editing the same post (` — released` appended, every word kept) |
| card state | nothing set; `ettelem config` read only, under the lock, `timeout 10`, at both ends | `tdp_w` 0, `temp_threshold_c` 65, 600 MHz, 523 mV, `max_power` at 14:47:45 and at 15:13:33 (`ident/`); nothing written. Every launch at a 58.0 °C reading after a 59 °C preheat; window means 58.0–59.2 °C; worst window median `took_ms` 22 ms |

## Departures, dated

- **D1 (31 Oct 2026, after the registered reduction) — a labelled post-hoc view of the board meter's dips**
  (`tools/claims-v3/dp/posthoc_dips.py`, `dips.json`, `dp-posthoc-dips.json`, `reduce-posthoc-dips.txt`). The dips
  were found while reading the registered result, so this is not an amendment: it moves no registered verdict and
  is reported beside the result. It uses E82 amendment A2's definition unchanged (a sample more than 4 W below both
  samples two steps away), on a copy of the telemetry, every gate unchanged.
- **D2 (31 Oct 2026, after the data) — the per-event account is post hoc.** The registered derived reading (toggles
  at 16, 32 and 64 bits) is reported as registered. The four-count model beside it was chosen among 41 count models
  after the data were seen. They are every 2-, 3- and 4-subset that contains `w` of seven candidate counts: `w`, `k`,
  `beat16`, `beat32`, `beat64`, `half` and `k_if_long`. `k_if_long` was itself built after the data showed that a
  4-line cycle costs what a 2-line one does. The code, `tools/claims-v3/dp/posthoc_counts.py`, was in the lane's
  scratch until the verification and is committed now, with its output `posthoc-counts.txt`; it reproduces the
  coefficients above exactly. Its DBI-DC comparison was added after the verification named DBI-DC. It prints four
  head-to-head fits and searches nothing.
- **D3 (inherited, as E60–E79) — two device processes outside `timeout 10`.** `lib.sh`'s `die_c` in `block_begin` /
  `block_end` runs `ettelem sample --seconds 1` under `timeout 20`, and the telemetry sampler runs for the whole pass:
  `lib.sh`'s frozen design (`033d0776`), as in every block since E60. Every enercat and sparsity launch ran under
  `timeout 10`. The registration's Risks list and `run_e81.sh`'s header say that `mf/block.sh` "caps every device
  process at `timeout 10`". That wording was inaccurate for exactly these two processes (corrected after
  verification, C8). In E81 the sampler's SIGKILL path never fired: no log has a SIGKILL, drain or "ignored SIGTERM"
  line, and all ten passes ended with rc=0 (`logs/e81-dp.log`).
- **D4 (31 Oct 2026, after the verification) — the minion-rail reading is post hoc.** The registration says nothing
  about the rail. The README first said "none of it is on the compute rail", from the span of `runs.csv` `rail`
  across the items; the verification showed that span is the zeros item against every data item.
  `tools/claims-v3/dp/posthoc_rail.py` reads the rail as the registered reducer reads the board: per headline pass,
  within-pass differences, a t interval, raw rail power with no leakage correction. Its output is `posthoc-rail.txt`.
- **D5 (31 Oct 2026, 14:52–14:55 PDT; disclosed after verification, C6) — an interim reduction of the warm-up
  pass.** The queue ran from 14:49:35 to 15:13:17. While it ran, the lane copied the smoke (`p8101`), the warm-up pass
  8110 and the first files of 8111 to its scratch on the Intel, finishing between 14:52:32 and 14:52:51. At 14:55:09
  it ran the registered reducer on pass 8110 alone: arrangement at period 2 +1.049 W, period +0.623 W, `resid_r`
  +0.306 W. 8110 is the registered warm-up, never in the headline. No rule, item, threshold or analysis changed
  afterwards; the only file added to `tools/claims-v3/dp/` before the verification is the labelled `posthoc_dips.py`
  (D1). The copy's few seconds of box I/O fell during pass 8111's `dp_c1` or `dp_s2r` run. Those read 2.039 and
  2.986 W over zeros. The other headline passes read 1.888–2.051 and 2.863–2.958 W, leaving out 8115, whose dips are
  described above (`dp.json` `per_pass`).
- **Not departures, for the record.** The registration's random counts were the law's (191.1 changes, 290.7 ones per
  line); the replica of the host's own source gives the realized 190.17 and 288.26, and `dp_c2r`/`dp_s2r` were built
  at 192/290 as registered (1.7 ones from random's, about 0.007 W at E75's e_one). The 38-minute stop rule never
  acted. P7 passed at its low edge in the direction the registration did not expect (it expected random floats about
  0.1 W *above* random bits).

## Corrections after verification

*Sat 31 Oct 2026, after the Q130 workflow's verifier checked this directory.* It reproduced every number in
`dp.json` from the raw telemetry with its own reducer. It confirmed the scoring, the code identity, the timing chain
and the card's state. It found one major and seven minor faults in how the results were stated. Each is corrected in
place above; this list says what changed and why. No number in `dp.json`, `dp-leak0.2936.json`,
`dp-leak0.3803.json`, `runs.csv`, `dips.json` or `dp-posthoc-dips.json` changed, and no verdict changed. No
registered file changed: `tools/claims-v3/dp/` gained `posthoc_counts.py` and `posthoc_rail.py`, both labelled post
hoc, beside `posthoc_dips.py`.

- **C1 (major) — the compute rail.** Results said, in bold, "None of it is on the compute rail", from the 8.32–8.48 W
  span of `runs.csv` `rail` across the items. That span is the zeros item alone (8.322 W) against every data item
  (8.398–8.475 W). Read as within-pass differences (D4, `posthoc-rail.txt`), going from zeros to data adds
  0.075–0.153 W on the minion rail: random +0.152 W [0.097, 0.208], 4.7 % of the chord. No arrangement or period
  contrast moves the rail by more than 0.08 W. The Results paragraph and What it changes 3 now say so.
- **C2 — the leakage footing.** The intervals were given without saying that they are statistical at the registered
  `auto` slope. New § The leakage footing gives each headline contrast at all three slopes. At the sensitivities,
  five contrasts move outside their `auto` intervals and the items over zeros read up to 0.20 W lower. Two readings
  do not survive: `per_c_2to4`'s apparent saving, and `s1_to_s2`'s presence. No verdict changes.
- **C3 — E75's 36.6 %, restated.** The 64 % is an image: random's counts in E75's contiguous 2-cycle arrangement
  (2.063 / 3.222 W). The same counts scattered cost 89 % (`dp_s2r`, 2.871 W). So the counts do not explain 64 % on
  their own, and the section now says so. The workflow's summary of this result said "the count explains 64 %" and
  gave "the long repeat period" "most of the remaining 11 %". The 11 % nets the long period's +0.640 W against the
  floats' −0.280 W, and that summary is corrected too.
- **C4 — mechanism and cause.** (a) The account by 16-bit beats, two 32 B halves and paths that carry every N-th line
  is now one candidate encoding. LPDDR4x read DBI-DC is named beside it, with a head-to-head fit in
  `posthoc-counts.txt`. (b) Random floats are cheaper "because" the top byte never changes is now "a likely part of
  the reason": the count model accounts for 89 of the 239 pJ per line. (c) The period step is now described as
  8,192 distinct random lines against a fixed scattered 2-cycle, with its two other differences (note ¹).
- **C5 — the post-hoc model's code.** `posthoc_counts.py` and its output are committed. D2 names the seven candidate
  counts and says that `k_if_long` was built after the data.
- **C6 — an interim look, not disclosed before.** The reduction of the warm-up pass at 14:55 PDT, while the queue
  ran, is now departure D5.
- **C7 — slips.** (1) "Scattering closes 70 %" is the ratio of the means; the mean of the per-pass ratios is 72 %
  [57, 86] (`shares.arrangement_share_of_gap_r`); both are given. (2) `dp_bern` matches the file images' counts only
  on average, to 0.05 %; What it changes 3 and note ¹ say so. (3) The intercept "0.8–1.4 W above the zeros anchor"
  now cites E75's README and `mf.json`. (4) P5 fails by 0.0007 W, not 0.001 W.
- **C8 — the registration's wording on `timeout 10`.** D3 now says that the registration's "every device process"
  was inaccurate for `die_c` and the whole-pass sampler.

## What it changes

1. **The Horace hub's Status item 6 closes** — answered, with an experiment number. At the same changed-bit and
   carried-one counts, a two-value alternating image is cheaper than random data by **1.636 W** [1.600, 1.671] per
   75 GB/s of DRAM lines (1,395 pJ per 64 B line). **61 % of that is the arrangement** of the ones inside each line,
   which costs at every period. **39 % is the step from a fixed scattered 2-cycle to 8,192 distinct random lines**
   (the period), and it appears only with a long period: four distinct lines are as cheap as two. At E71's leakage
   slope the split is 58 / 42. So the image is "compressible" in the narrow sense of the hub's hypothesis, because
   repetition saves. But the larger part of what E75's images missed is where their ones sat.
2. **E75's DRAM reading is refined, not overturned.** Carried ones are the biggest single term: the contiguous
   two-value image at random's own counts is 64 % of the chord, measured directly (E75's 36.6 % left out the
   convex first step from zeros). But a bit-counting model of DRAM energy needs two more terms that E75's design
   held fixed by construction. One is **where the ones sit inside a line** (+0.81 W at random's counts, 25 % of the
   chord). The other is **the period**: 8,192 distinct random lines cost +0.64 W more than a scattered 2-cycle at
   256/256, and a 4-line cycle costs nothing more. Counting ones and the changes between consecutive lines of one
   stream is not enough.
3. **For the blog material.** The same number of bytes, with the same number of ones and the same number of changes
   from line to line (on average, for the random bits), can cost 1.6 W more to read from DRAM depending only on their
   pattern — half the 3.2 W zeros-to-random range. Random *floats* cost 0.28 W less than random *bits*; a likely part
   of the reason is that a float's top byte never changes. The pattern's part never reaches the compute rail. The
   step from zeros to any data adds 0.075–0.153 W there, at most 5 % of the chord.
4. **The Levels tab's memory-path row** gains E81's two measured numbers, the arrangement and the period. It may
   carry the per-event account as a labelled post-hoc description, with DBI-DC beside it. It does not move the
   arithmetic waterfall: this is the memory path.
5. **What would settle the mechanism.** Two things, neither run here. A period ladder between 4 and 8,192 lines
   would find where the period effect starts, and so how many ways consecutive lines are spread. The host's `file:`
   operand takes exactly 256 B (four lines), so it needs a host change, registered first. And the memory
   controller's configuration, read from the firmware and driver sources: its read-DBI setting would decide between
   the two candidate encodings, and its address-to-channel map and data-pin mapping would test the "each path
   carries every N-th line" reading directly.

## Files

| file | what it is |
|---|---|
| `passes/p8101` | the smoke (`anchor_pi`, `dp_bern`, `dp_s2`), not reduced |
| `passes/p8110`–`p8119` | the ten passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `code.sha256`, `gen.sha256`, `text.sha256`, `manifest.txt`, `run.log` |
| `gen/` | `make_dp.py`'s output regenerated on the Intel: `manifest.json` (the items, their commands and counts, π), `srcs/*.bin` (the eight 256 B images, byte-identical to the box's: every pass's `gen.sha256`), `counts.json` (every count, including the replica's realized counts of `random` and `bern:0.5`) |
| `dp.json` | the reduction at the registered `auto` leakage slope — the result |
| `dp-leak0.2936.json`, `dp-leak0.3803.json` | the two labelled sensitivities |
| `runs.csv` | one row per run: pass, item, launch reading, p_raw, p80, rail, rate, median `took_ms`, gate failures |
| `reduce.sh`, `reduce.txt` | the reduction commands and their printed output |
| `dips.json`, `dp-posthoc-dips.json`, `reduce-posthoc-dips.txt` | **post hoc, labelled** (D1): every board-meter dip and where it falls, and the registered reducer on dip-filtered copies of the passes |
| `posthoc-counts.txt` | **post hoc, labelled** (D2): all 41 count models, the best model's account of `dp_bern − dp_random`, and the DBI-DC head to head |
| `posthoc-rail.txt` | **post hoc, labelled** (D4): the minion rail per item and per registered contrast, with the board's and the window temperature's |
| `ident/` | `ettelem config` at the start and the end of the card session, and `et-lab-manifest` |
| `logs/` | the queue log, the smoke log, the dry run, the box's harness hashes |

Code: `tools/claims-v3/dp/` (`make_dp.py`, `src_replica.cpp`, `run_e81.sh`, `predictions.json`, `reduce_dp.py`,
`README.md` — the registration), with E75's `tools/claims-v3/mf/block.sh`, `queue_mf.sh` and `make_mf.py` and the
runner `tools/claims-v3/runitems.py`, all unchanged. Post hoc, labelled: `posthoc_dips.py` (D1), `posthoc_counts.py`
(D2) and `posthoc_rail.py` (D4).

## Reproducing it

    # on aifoundry3, in ~/aifoundry
    bash tools/claims-v3/dp/run_e81.sh setup
    bash tools/claims-v3/dp/run_e81.sh smoke 8101
    bash tools/claims-v3/dp/run_e81.sh go 8110 10
    # on any machine with the lab repo, numpy and GCC
    g++ -O2 -std=c++17 -o build/dp-replica tools/claims-v3/dp/src_replica.cpp
    build/dp-replica random 1 > build/random.bin; build/dp-replica bern:0.5 1 > build/bern50.bin
    python3 tools/claims-v3/mf/make_mf.py build/mf-gen
    python3 tools/claims-v3/dp/make_dp.py docs/reports/data/2026-10-31-e81-dram-pattern/gen --check --builtins build --e75-gen build/mf-gen
    bash docs/reports/data/2026-10-31-e81-dram-pattern/reduce.sh
    # the labelled post-hoc views (D1, D2, D4)
    D=docs/reports/data/2026-10-31-e81-dram-pattern
    python3 tools/claims-v3/dp/posthoc_dips.py $D/passes/p811? --work build/e81-dipwork --out $D/dips.json
    python3 tools/claims-v3/dp/reduce_dp.py build/e81-dipwork/p811? --gen $D/gen \
      --pred tools/claims-v3/dp/predictions.json --out $D/dp-posthoc-dips.json
    python3 tools/claims-v3/dp/posthoc_counts.py $D --builtins build > $D/posthoc-counts.txt
    python3 tools/claims-v3/dp/posthoc_rail.py $D > $D/posthoc-rail.txt
