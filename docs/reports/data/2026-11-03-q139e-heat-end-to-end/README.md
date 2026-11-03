# Q139(e): heat over minutes predicted end to end from the bits, frozen for E154 (aifoundry3) and E161 (aifoundry2) (desk, Tue 3 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
items **9** (a steady state for heat), **8** (the heat path between sessions) and **6** (the power model). It answers Q138's final
critic, **rank 4**: "Heat over minutes predicted end to end from the computation's description... The bits-to-power-to-chain path for a
new kind has never been scored." Desk only: no card, no device command, nothing set, nothing refitted. Written 05:43-06:10 PST on the
Intel, after Q139(x)'s pool-6 predictions commit `d98d2e34` (05:39:23 PST) and before any E154 or E161 claim.*

*Amended and corrected after verification (amendment A1, a dated note, Tue 3 Nov 2026, from about 06:35 PST, committed before
E154's and E161's claims; desk only: no card, no device command, nothing refitted). An independent verifier rebuilt this lane's
predictions byte for byte and re-derived every aifoundry2 number and aifoundry3's H_M, K_L and K_O with its own code. It found one
major fault and six minor ones. None changes a registered rule, band, FAIL line, stop or verdict path: `predict_q139e.py`,
`predictions-q139e.json` and `.txt` are as committed in `455c46c1`, and this README gains lines only. **The main one:** the frozen
session table ran K_S at 3.4 s on every 4.4 s (share 0.773), not at the stated 3.456 s every 4.37 s (0.791), because the chain
code rounds each piece to whole 0.2 s steps. On the registered arm E machinery the plan reads **K_S +11.72 °C** over the 3.21 °C it
carries in (plateau 66.13 °C, peak 67.03 °C at a 51.2 °C room), not +11.37, and **K_Q +6.09 °C** over a 4.44 °C tail (its
61.73 °C plateau unchanged), not +6.21. E154's verdicts are unaffected, because arm E recomputes on the realized records. Every
correction is set out in [§ Amendment A1](#amendment-a1-corrections-after-verification-tue-3-nov-2026-before-e154s-and-e161s-claims)
at the end, with its numbers from [`amendment-a1.py`](amendment-a1.py) → [`amendment-a1.txt`](amendment-a1.txt)
([`amendment-a1.json`](amendment-a1.json)), which imports the frozen code unchanged and first rebuilds `predictions-q139e.json`
byte for byte. The header's "Written 05:43-06:10 PST" should read 05:43-06:00: the gate commit `455c46c1` is 06:00:48 PST.*

## Results first

Every heat-over-minutes score so far was given the board's measured watts, or E78's measured watts for the same kinds. Here the watts
come from the bits. Three frozen pieces are composed, and nothing is fitted:

1. **M8's power from the bits** for pool 6's four hold candidates
   ([`tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json`](../../../../tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json)
   and `-aifoundry2.json`, committed at `d98d2e34`).
2. **Q138(t)'s frozen heat chain**
   ([`../2026-11-02-q138t-heat-model/`](../2026-11-02-q138t-heat-model/README.md), `model-q138t.json`): five stages from board watts to
   the die, closed through the idle leakage law.
3. **aifoundry2's governor:** Q138(t)'s trip rule (a die that would pass the trip is pinned at 65.9 °C) and M8's burst cap, 65.2 W.

**aifoundry3 card 0, 600 MHz pinned** (E154). Rises are over what the chain carries into each hold, plateaus are the mean over the
hold's last 300 s, and absolute values assume a 51.2 °C room (E144's rest die; the JSON gives 49.5-53.0 °C):

| step | min | kind | power from the bits (S over idle, W) | launch pattern | plateau rise (°C) | plateau / peak (°C) | 95% band (°C) | FAIL beyond (°C) | M7 / M6 through the same chain (°C) |
|---|---|---|---|---|---|---|---|---|---|
| R0 | 5 | rest | | | | | | | |
| **H_M** | 11 | int8 full, E97's H1 again (E78's tile) | 9.648 (E78, measured) | natural chain (0.966) | 11.02 | 62.2 / 62.6 | 0.36 | 1.30 | the replicate, given E78's S |
| R1 | 3.5 | rest | | | | | | | |
| **K_S** | 10 | `fp32.real_smol_softmax_v_causal` | **15.674** (M8) | 7 dispatches every **4.37 s** (0.791) | **11.37** | 65.8 / 66.7 | **0.60** | 1.30 | 11.30 / 11.22 |
| R2 | 3.5 | rest | | | | | | | |
| **K_Q** | 10 | `int8.real_qwen_w8a8_v` | **9.241** (M8) | natural chain | **6.21** (from a 4.3 °C tail) | 61.7 / 62.0 | **0.94** | 1.88 | 6.23 / 6.26 |
| *subset ends* | *43.0* | | | | | | | | |
| R3 | 3.5 | rest | | | | | | | |
| **K_L** | 10 | `int8.b_line_zero_ff` | **5.935** (M8) | natural chain | **3.54** | 57.8 / 58.0 | **1.45** | 2.89 | **3.90 / 4.36** |
| R4 | 3.5 | rest | | | | | | | |
| **K_O** | 10 | `fp32.a_onebit_b5_third` | **11.427** (M8) | natural chain | **11.21** | 64.3 / 64.8 | **0.69** | 1.38 | 11.04 / 10.84 |
| R5 | 2.5 | rest | | | | | | | |

> **A1 (C1), Tue 3 Nov 2026, before E154:** on the registered arm E machinery (`score_e144.py`'s `s_on_grid`, `closed_on_grid`
> and `traj`, unchanged) the plan reads **K_S +11.72 °C** (plateau 66.13 °C, peak 67.03 °C; M7 / M6 11.65 / 11.57 °C) and
> **K_Q +6.09 °C** over a 4.44 °C tail (61.73 / 62.03 °C as above; M7 / M6 6.11 / 6.15 °C). H_M, K_L and K_O agree with the
> table to 0.002 °C. The table's K_S and K_Q rows came from the 0.2 s piece rounding (C1). K_S's band at the true pattern would
> be 0.61 °C; the registered 0.60 stands.

The plan runs **72.3 minutes** (the subset 43.0). The probe, smoke and stop tests come on top, inside 76 and 45. Holds from a rested
die, as fixed points at a 51.2 °C room: K_S 15.75, K_Q 10.92, K_L 6.80 and K_O 13.81 °C. The 10-minute windows read 92-95% of those
values ([`predictions-q139e.json`](predictions-q139e.json) › `aifoundry3.plateau_rise_fixed_point_C_by_room`).

- **Why K_S is duty-cycled.** At the natural chain the softmax tile's fixed point would be about 67 °C, with no margin under H_H's
  67.5 °C peak line. The shortest period at 7 dispatches (`--seconds 3.20`, 3.456 s recorded, A1.1's rule) that keeps the in-launch
  peak at or under 67.5 °C from a 51.5 °C room is **4.37 s** (share 0.791). In a warm room (R0's rest die 51.5-53.0 °C) it is 4.97 s
  (0.695). Above 53.0 °C, K_S becomes a rest.
- **H_M is E97's H1 again:** int8 full from rest, which is the replicate the critic asked to fit in. Its frozen reading is the rise per
  board W at 600 s, 0.858, which over E97's 0.898 gives **0.956**, inside Q138(t)'s PASS band [0.94, 1.06]. It is given E78's watts,
  not the bits.
- **K_L is the one hold where the models part.** M8 puts int8's whole-line tile 0.71 W below M6, and that shows up as 0.82 °C at the
  plateau (3.54 against 4.36 °C). The other three agree within 0.4 °C.

> **A1 (C1):** on the scorer's grid the shortest periods are 4.33 s from a 51.5 °C room and 4.90 s from 53.0 °C, so the
> registered 4.37 / 4.97 s are on the safe side. At them the in-session K_S peaks are 67.40 °C (51.5 °C room) and 67.35 °C
> (53.0 °C), and from a rested die 67.34 / 67.29 °C. That is still at or under 67.5 °C, with 0.10-0.15 °C of margin, not the
> 0.5 °C the frozen solve's 66.99 °C implied.

**aifoundry2 card 0, its own governor** (E161). The board comes from M8's burst relation, moved to the hold's die by the 0.442 W/°C
law. The die comes from the chain, anchored on the REST's measured die and board. The values below assume a 46.0 °C rest
(E144b's), with P_ref 21.93 W:

| step | min | kind | M8 burst board at 800 MHz (W) | regime predicted | plateau (°C) | clock over the last 300 s | peak board, expected / 95% (W) | 95% band (°C) |
|---|---|---|---|---|---|---|---|---|
| REST | 2 | | | | | | | |
| **G1q** | 13 | `int8.b_line_zero_ff` | 43.99 | **800 MHz, never trips** (fixed point 62.55 °C, 3.4 °C under the trip) | **62.55** (rise 16.55) | 800 MHz (share ≥ 790 MHz ≥ 0.90) | 48.8 / 53.3 | **3.15** (FAIL beyond 6.30) |
| END, REST | 2 + 2 | | | | | | | |
| **G2q** | 13 | `fp32.real_smol_softmax_v_causal` | 61.96 | **trip** (the 800 MHz fixed point would be 79.4 °C); M8's cap first, at about 48 s | **65.9** (the trip rule; simulated 65.66) | **681.6 MHz** from the bits (simulated 678.3) | 67.0 / 68.2 | 0.60 (FAIL beyond 1.20), clock ±35 MHz (FAIL ±70) |
| END2 | 2 | | | | | | | |

The plan runs **34 minutes**, inside 40. **Section 22's power rule:** both holds' 95% peaks (53.3 and 68.2 W) are far under 82 W.
The registered board stop is 80 W on three consecutive live samples, under section 22's 85 W, and must be tested in the smoke.

> **A1 (C4), before E161:** the 34 minutes are card-minutes by E144b's count, which leaves out E98's rest rule: 15 minutes with
> no launch before each hold, which E144b's queue ran before G1 and before G2. E161 keeps that rule before G1q and before G2q, so
> it needs about 64 minutes of wall time plus the smoke and stop tests (E144b: 69 minutes for 39.2 card-minutes). Without it,
> G2q's REST anchor carries G1q's tail (48.31 °C on the frozen chain, 2.31 °C over the room), and the clock rule recomputed there
> reads 28-34 MHz low.

**The bands, derived here.** Each is 1.96 × √(σ_chain² + (G σ_power)²):

| | σ_chain (1σ) | G (°C per W) | σ_power (W) | 1σ (°C) | 95% (°C) | the critic's form |
|---|---|---|---|---|---|---|
| aifoundry3 | 0.18 °C, E144's blind arm (a) rms | 1.0-1.25: the closed loop's d(plateau)/dS × share (the leakage loop adds 30-40% over the open chain's 0.87) | M8's own 95% D band / 1.96, with the zeros level's spread between sessions (0.106 W fp32, 0.071 W int8, 85 committed sessions) added in quadrature: 0.24-0.63 | 0.31-0.74 | 0.60-1.45 | 0.28-0.57 °C (√(0.18² + (0.87 σ)²)) |
| aifoundry2, 800 MHz | 0.76 °C, E144b G1's blind arm (a) rms | 0.938, the closed loop's gain at 800 MHz | √(1.443² + 0.442²) = 1.51: M8's pinned end-to-end board rms and the reference die's 1 °C | 1.61 | 3.15 | 1.30 °C (√(0.76² + (0.663 × 1.6)²)) |
| aifoundry2, trip | Q138(t)'s G2 band | — | — | — | ±0.60 | — |

These come out wider than the critic's scale for two reasons. The leakage loop amplifies a power error by 1/(1 − loop gain), about
1.4× on both cards, where the critic's form used the open chain's R. And on aifoundry3, int8 line tiles carry M8's widest D band,
±1.22 W.

> **A1 (C3, D4):** "85 committed sessions" are 85 reduction files from 17 data directories. They hold 78 distinct value sets,
> because several directories re-reduce one session at other leakage slopes, taus or dip rules, and they are read through a glob
> the frozen hash check does not cover; [`inputs-sidecar.json`](inputs-sidecar.json) lists them with their sha256. With one
> primary file per directory the spread is 0.074 / 0.067 / 0.055 W (fp32 / fp16 / int8), and the four bands would be
> 0.003-0.025 °C narrower. The registered bands stay. Their width against the critic's scale is departure D4.

**One derived number, from committed pre-pool-6 data:** aifoundry2's reference die for M8's burst board, **56.0 °C**. E144b G1's
800 MHz hold samples give board = 16.45 + 0.410 × die (8,723 samples). On that line, E80's int8 −1s burst board of 39.4 W (800 MHz,
first second, launched at a reading ≤ 55 °C) reads 55.97 °C ([`predictions-q139e.json`](predictions-q139e.json) ›
`aifoundry2.T_REF_check`). Without it, a burst board cannot be carried to a hold's die.

**Post hoc back-check (not a rule):** the same composition on E144b's G1 hold, int8 −1s, a hold neither M8 nor Q138(t) was fitted
on, with E78's measured D for the kind. It gives a plateau of 59.43 °C against 58.92 measured (+0.51 °C) and a board 1.9 W high. That
is M8's relation reading int8 −1s 1.3 W over E80's burst, partly offset by the session's 0.711 °C per W against the chain's 0.663
(`aifoundry2.backcheck_E144b_G1_posthoc`).

> **A1 (C5):** the back-check is not independent of T_REF: both come from E144b G1's samples. The independent check of the line
> is E80's sustained int8 −1s cell, from another session (31 Oct: 41.0 W at a 60.0 °C die, 796.9 MHz), which the line reads at
> 41.05 W.

## Registered rules (`predictions-q139e.json` › `rules`)

**E154, per pool-6 hold. Arm E, end to end (the primary):**
- **The model:** Q138(t)'s frozen chain, closed through E97's idle law from R0's measured rest die, on the session's realized dispatch
  records. Each record is on at the item's frozen S (`aifoundry3.S_table_W`).
- **The machinery:** `score_e144.py`'s arm (b), A1.2, with its `S78` table extended by `S_table_W`. Nothing else changes.
- **PASS:** |plateau error| ≤ band_95_C, and the rms of the checkpoints from 60 s to the end ≤ band_95_C.
- **FAIL:** |plateau error| > max(2 band_95_C, 1.30 °C).
- **Otherwise** INCONCLUSIVE.

**E154, arms reported beside E:**
- **Arm A, given watts.** `score_e144.py`'s arm (a), with its frozen bands. E − A on the plateau is the power path's share of the
  error.
- **M7 and M6.** Their S, run through the same chain.
- **H_M.** Q138(t)'s (b) and (c) replicate rules.
- **Session figure.** The rms of the pool-6 plateau errors (2 holds in the subset, 4 in the full design) is the card's out-of-sample
  error of heat over minutes from the bits.

**E161, G1q.** The 800 MHz fixed point from the REST's measured die and board.
- **PASS:** |plateau error| ≤ band_95_C, and the checkpoints' rms ≤ band_95_C.
- **FAIL:** beyond fail_beyond_C.
- **Clock:** the share at ≥ 790 MHz over the last 300 s, PASS ≥ 0.90 (E144b-K1's rule), FAIL < 0.75.

**E161, G2q.** The trip rule.
- **PASS:** the plateau within ±0.60 °C of 65.9, in the predicted regime. FAIL: outside ±1.20 °C, or the other regime.
- **Clock:** within ±35 MHz of the clock_MHz_at_plateau_rule recomputed at the session's rest die and board (681.6 MHz at 46.0 °C and
  21.93 W). FAIL outside ±70 MHz.

> **A1 (C2), before E161:** the rule stays as registered. ±35 MHz is the power path's 95% only (1.96 × 1.509 W over 0.0886 W per
> MHz is 33.4 MHz). The heat path's R moves the trip clock too: at the 0.685-0.711 °C per board W later sessions measured
> (against the frozen 0.663) it reads 670.7-658.7 MHz, 11-23 MHz low, and the trip plateau's ±0.60 °C moves it ±7 MHz. Beside
> the verdict, E161 reports the trip clock recomputed with R set to G1q's measured rise per board W.

**Stops:**
- **aifoundry3:** Q138(t)'s, unchanged. No launch at a firmware reading ≥ 70 °C; a hold ends at ≥ 72 °C or ≥ 65 W; the session ends
  at ≥ 74 °C.
- **aifoundry2:** a hold ends at a reading ≥ 72 °C, or at ≥ 80 W on three consecutive samples.

## What this does to predicting power and heat

**The term tested** is the whole path from a computation's description to its die over minutes: the bits, then M8's watts, then
Q138(t)'s closed chain, plus aifoundry2's governor. On aifoundry2 the same path gives a sustained clock from the bits (G2q's
681.6 MHz).

**Out-of-sample error, before:**
- **Given the measured board watts:** 0.04-0.18 °C rms on aifoundry3 (E144) and 0.37-0.76 °C on aifoundry2 (E144b).
- **From E78's measured watts for the same kinds:** plateaus −0.15 / +0.01 °C (E144).
- **From the bits:** never scored. The only bits-to-heat figure is over a 4.5 s run, 0.13-0.17 °C (M7, pool 5).

**After:** E154 and E161 measure it against these frozen numbers. **No out-of-sample error changes until then.** The expected
size of the composition's error at 95%:
- aifoundry3: 0.6-0.7 °C for the float kinds and 0.9-1.4 °C for the int8 kinds;
- aifoundry2: 3.2 °C below the trip. At the trip the die is the governor's, ±0.6 °C, and the bits set the clock to about ±35 MHz.

> **A1 (C1, C2):** K_S's expected rise is +11.72 °C over its 3.21 °C tail, not +11.37. "The bits set the clock to about ±35 MHz"
> overstates it: that is the power path's 95%, and the heat path's R can move the clock 11-23 MHz lower.

## What this cannot say

- **The 10-minute holds read 92-95% of their fixed points.** The plateau is defined as the same window in prediction and score, so it
  is like for like. It is not a steady state.
- **Two holds start on a tail.** K_Q starts 4.3 °C and K_S 3.2 °C above the room. The chain carries those tails; E144's H_L did the
  same and scored 0.04 °C.

  *A1 (C6), Tue 3 Nov 2026: K_Q's tail is 4.44 °C on the true K_S pattern. H_L is no precedent: it carried in 0.43 °C (its rest
  die 51.65 °C against R0's 51.22), and its 0.04 °C is its arm (a) rms, given the measured watts; its arm (b) plateau, from E78's
  S, read +0.01 °C. Tails of 3-4 °C have not been scored.*
- **aifoundry2's board law** is 0.442 W/°C at every clock, and its reference die is 56.0 ± 1 °C. The governor is modelled as one
  100 MHz step a second (Q138(t)'s rule) plus M8's 65.2 W cap. E144b G1 also stepped down 3-4% of the time at 59 °C, which no rule
  here explains.
- **No inlet thermometer.** The rest die stands in for the room (items 8 and 9), and the between-session plateau moves of
  0.3-0.8 °C (E97) remain.

## Device commands sent

None: this lane opened no device and ran nothing on any box. E154 and E161 each list and classify their own before the first launch,
with `tools/claims-v3/dmcmd_audit.py`.

## Departures

- **D1, the subset's minutes.** The brief allowed "3-4 kinds held 10-13 minutes each" and a subset of at most 45 minutes with the
  int8-full replicate if it fits. Fitting the replicate means 10-minute pool-6 holds and an 11-minute H_M; the full design has four
  pool-6 kinds plus the replicate.
- **D2, aifoundry2's reference die.** T_REF = 56.0 °C is the one number derived here, from E80's and E144b's committed data. M8 has
  no die term for a burst board.
- **D3, none in time:** about 30 minutes against the brief's 45.
- **D4 (dated Tue 3 Nov 2026, amendment A1, written before E154's and E161's data): the PASS lines are wider than the critic's
  decisive test.** They are 95% bands on the closed loop's gain, 1.7-4.1 times the critic's 0.35 °C on aifoundry3 and 2.4-3.1
  times its 1.0-1.3 °C on aifoundry2, so no hold's verdict separates M8 from M7 or M6. The informative figures are the session
  rms of the plateau errors and E − A per hold, not the PASS count (§ Amendment A1).

## How to reproduce

```bash
python3 docs/reports/data/2026-11-03-q139e-heat-end-to-end/predict_q139e.py > docs/reports/data/2026-11-03-q139e-heat-end-to-end/predictions-q139e.txt   # ~10 s
```

It checks the sha256 of every frozen input first: Q138(t)'s model, chain code and scorer, M8's pool-6 predictions for aifoundry3 and
aifoundry2, `m8.json` and E78's `e78.json`. Its output is byte-identical on a rerun. numpy 1.26.4, Python 3.9.

> **A1 (C3):** byte-identical at `455c46c1` only. From `99dc31f3` (06:27:49 PST) six of E152's aifoundry3 reduction files match
> the zeros-level glob too (n 91; fp32 sd 0.1059 against 0.1062 W), so a plain rerun at a later tree changes the JSON's bytes.
> `amendment-a1.py` rebuilds `predictions-q139e.json` byte for byte from the 85 files in `inputs-sidecar.json`, each
> sha256-checked, with E80's `cells.json` and E144b G1's telemetry (99 inputs checked in all):
>
> ```bash
> /usr/bin/python3 docs/reports/data/2026-11-03-q139e-heat-end-to-end/amendment-a1.py > docs/reports/data/2026-11-03-q139e-heat-end-to-end/amendment-a1.txt   # ~40 s
> ```

## Files

| file | what |
|---|---|
| `predict_q139e.py` | the composition: M8's S (aifoundry3) and burst relation (aifoundry2) through Q138(t)'s frozen chain, the duty solve, the governor's cap and trip, the bands and the rules |
| `predictions-q139e.json`, `.txt` | **frozen**: both designs, every hold's trajectory, plateau, peak, band and FAIL line, the plateaus by room, the M7/M6 arms, T_REF's check, the back-check, the rules |
| `amendment-a1.py` | amendment A1 (after verification, before E154/E161): rebuilds the frozen JSON byte for byte from the sidecar, then E154's plan on the registered arm E machinery, G2q's clock against the heat path, E161's rest rule, T_REF's line against E80's sustained cell, the text facts and D4 |
| `amendment-a1.json`, `.txt` | its output (byte-identical on a rerun) |
| `inputs-sidecar.json` | the inputs `predict_q139e.py` read at `455c46c1` without hashing them: the 85 zeros-level files with their sha256 and values, E80's `cells.json`, E144b G1's telemetry, and E144's `scored.json` (read by A1 only) |

## Amendment A1: corrections after verification (Tue 3 Nov 2026, before E154's and E161's claims)

An independent verifier of this lane (written up about 06:35 PST) rebuilt `predictions-q139e.json` and `.txt` byte for byte from a
snapshot of `455c46c1`. It re-derived with its own code every aifoundry2 number (T_REF from the raw telemetry included) and
aifoundry3's H_M, K_L and K_O. It checked the blind order: M8 was frozen at `122da8b6` before pool 6 entered the repo at
`d98d2e34`, and no E153, E154, E157, E160 or E161 claim came before the gate. It found the four public files free of private
content. It found one major fault and six minor ones. None changes a registered rule, band, FAIL line or stop, and none touches a
device. [`amendment-a1.py`](amendment-a1.py) imports `predict_q139e.py` and `score_e144.py` unchanged. It checks 99 inputs' sha256,
rebuilds the frozen JSON byte for byte (sha256 `60424edb…`), and only then prints the numbers below
([`amendment-a1.txt`](amendment-a1.txt), [`amendment-a1.json`](amendment-a1.json)); its own output is byte-identical on a rerun.
No frozen file was edited, and this README gains lines only. E154 and E161 check that this amendment's commit, like `455c46c1`,
precedes their claim and first launch.

- **C1 (major). K_S's design numbers were simulated at a rounded duty.** `predict_q139e.py` hands K_S's pieces, 3.456 s on and
  0.914 s off, to `heat_q138t.closed_loop`, which rounds each to whole 0.2 s steps. They ran as 3.4 s on every 4.4 s (share 0.773,
  S_eff 12.11 W), not 3.456 s every 4.37 s (0.791, the stated 12.40 W); the frozen K_S span, 1165.4-1768.2 s, is 137 × 4.4 s. The
  registered scorer integrates the dispatch records over each grid cell (`s_on_grid`). On the planned records at their exact
  times, arm E reads at a 51.2 °C room:

  | hold | frozen rise / plateau / peak (°C) | arm E on the plan (°C) | M7 / M6 through the chain, frozen → arm E (°C) |
  |---|---|---|---|
  | K_S | 11.365 / 65.78 / 66.68 (tail 3.211) | **11.722 / 66.13 / 67.03** (tail 3.211) | 11.296 / 11.218 → **11.651 / 11.571** |
  | K_Q | 6.207 / 61.73 / 62.03 (tail 4.318) | **6.091** / 61.73 / 62.03 (tail **4.440**) | 6.225 / 6.263 → **6.110 / 6.148** |
  | H_M, K_L, K_O | as frozen | within 0.002 °C | within 0.002 °C |

  So K_S's expected plateau rise is **+11.72 °C over a 3.21 °C carried-in tail**. From a rested die its fixed point is 15.75 °C,
  computed at the true share, and that stands. K_Q's is +6.09 °C over a 4.44 °C tail. The error was 0.36 °C, 60% of K_S's own 95%
  band. **E154's verdicts are unaffected**, because arm E is recomputed on the session's realized records with `s_on_grid`, as
  registered. The registered duty periods stand too. On the scorer's grid the shortest periods are 4.33 s (51.5 °C room, peak
  67.49 °C) and 4.90 s (53.0 °C, 67.49 °C), so 4.37 / 4.97 s are on the safe side. At them the in-session K_S peaks are 67.40 °C
  (51.5 °C room) and 67.35 °C (53.0 °C). That is still at or under the 67.5 °C line, but with 0.10-0.15 °C of margin, not the
  frozen solve's 0.51 °C (66.99 °C). K_S's band at the true pattern would be 0.61 °C (G 1.044 against the frozen 1.018); the
  registered 0.599 stands, as does its FAIL line, 1.30 °C. Where E154 reads its holds against the plan's numbers (as E144 read
  f5473428's), it uses this table for K_S and K_Q (`C1_E154_plan_on_the_registered_machinery`: `frozen_vs_armE_at_51.2C`,
  `on_plan`, `duty_solve`, `in_session_peaks_C`, `bands_at_true_pattern`).
- **C2. G2q's ±35 MHz clock band is the power path's 95% only.** 1.96 × 1.509 W (σ_P) over 0.0886 W per MHz at the trip clock is
  33.4 MHz. The trip clock follows P_ref + (65.9 − T_rest) / R, with R the chain's frozen 0.663 °C per board W. At the rise per
  board W later aifoundry2 sessions measured, 0.685, 0.689 and 0.707, and at E144b's (c) 0.711, it reads 670.7, 668.8, 660.5 and
  658.7 MHz, 11-23 MHz under 681.6. The trip plateau's own ±0.60 °C moves it ±7.2 MHz. The rule stays as registered. Beside the
  verdict, E161 reports the trip clock recomputed with R set to G1q's measured rise per board W (its plateau over the REST, as
  E144b's (c) reading), so a clock miss splits into power and heat. Read "the bits set the clock to about ±35 MHz" as "the power
  path sets it to about ±35 MHz at 95%, and the heat path's R can move it 11-23 MHz lower" (`C2_G2q_clock_and_the_heat_path`).
- **C3. The zeros-level spread, and the inputs the hash check left out.** "85 committed sessions" are 85 reduction files from 17
  data directories, matched by `zeros_spread_a3`'s glob `docs/reports/data/2026-1*/e*.json` (254 files at `455c46c1`). They hold
  78 distinct value sets, because several directories re-reduce one session at other leakage slopes, taus or dip rules, so the
  spread mixes footings. Read it as "85 reduction files over 17 data directories". One primary file per directory (16 have one)
  gives 0.074 / 0.067 / 0.055 W (fp32 / fp16 / int8), against 0.106 / 0.119 / 0.071. With it the four pool-6 bands would be
  0.003-0.025 °C narrower, and with no zeros term 0.008-0.050 °C narrower (`C3_zeros_spread_inputs`). The registered bands stay.
  `check_frozen()` hashed 7 inputs; the glob's files, E80's `cells.json` and E144b G1's telemetry were read unhashed.
  [`inputs-sidecar.json`](inputs-sidecar.json) lists them with their sha256 at `455c46c1`. A plain rerun of `predict_q139e.py` is
  byte-identical only at `455c46c1`: from `99dc31f3` (E152's results, 06:27:49 PST) six of E152's aifoundry3 files match the glob
  too (n 91; fp32 sd 0.1059), so the JSON's bytes change. `amendment-a1.py` rebuilds it from the sidecar's files byte for byte
  (`A0_reproduction`).
- **C4. E161's 34 minutes rely on E98's rest rule.** E144b's queue ran 15 minutes with no launch before each hold, outside its
  card-minute count (its session table: 22:01:42-22:16:42 before G1, 22:35:49-22:50:50 before G2). **E161 keeps that rule before
  G1q and before G2q.** Its plan is then 34 card-minutes by E144b's count, and about 64 minutes of wall time plus the smoke and stop
  tests (E144b took 69 minutes for 39.2 card-minutes); its claim and the 11:30 PST end gate must allow for that. Without the rule,
  on the frozen chain, G1q (62.5 °C at its end) followed by END 2 and REST 2 minutes leaves G2q's REST anchor at 48.31 °C, 2.31 °C
  over the 46.0 °C room. `a2_closed` starts each hold from rest at its REST reading, so the clock rule recomputed at that anchor
  would read 653.7 MHz (648.0 on the P_ref line), 28-34 MHz under 681.6. The chain carried on from G1q puts G2q's last 300 s at
  65.67 °C and 679.0 MHz, the same as from rest (65.66 °C, 678.3 MHz); after the rest rule the anchor is back at the room
  (0.00 °C). So if E161 cannot keep the rule before G2q, it evaluates G2q's rules at G1q's REST die and board, with the chain
  carried on from G1q, and declares that as a departure before its data (`C4_E161_rest_rule`).
- **C5. The back-check shares T_REF's session.** `tref_check` fits board = 16.45 + 0.410 × die on E144b G1's 800 MHz samples
  (n 8,723), and `a2_backcheck` then predicts that same hold (+0.51 °C). So the back-check cannot test the lane's one derived
  number. "A hold neither M8 nor Q138(t) was fitted on" is true, but T_REF came from it. The independent support is E80's
  sustained int8 −1s cell from another session (31 Oct; nine back-to-back 8 s processes, the last 40 s): 41.0 W at a 60.0 °C die
  and 796.9 MHz. The line reads 41.05 W at that die, or 59.88 °C for 41.0 W (`C5_T_REF_line_vs_E80_sustained`).
- **C6. Text slips** (the frozen text is left as written):
  - `rules` › E154 › subset says the full design is "(72.9 minutes of plan)". It is 72.5 minutes nominal and 72.34 as frozen,
    because each hold ends with its last whole cycle (72.23 at the true K_S pattern).
  - The header's "Written 05:43-06:10 PST" should read 05:43-06:00: `455c46c1` was committed at 06:00:48 PST, and the result
    followed at 06:02.
  - `predict_q139e.py`'s comment "the design's first 42.5 minutes" should read 43.0, as its `"minutes": 43.0` and `SUBSET_END`
    comment say.
  - "Two holds start on a tail … E144's H_L did the same and scored 0.04 °C". H_L carried in 0.43 °C (its rest die 51.65 °C
    against R0's 51.22), not 3-4 °C. Its 0.04 °C is arm (a)'s rms, given the measured watts; its arm (b) plateau, from E78's S,
    read +0.01 °C. Tails of 3.2-4.4 °C have not been scored.
  - "(0.106 W fp32, 0.071 W int8, 85 committed sessions)", and "Its output is byte-identical on a rerun": see C3.
- **D4 (a departure, dated Tue 3 Nov 2026, written before E154's and E161's data): the PASS lines are wider than the critic's
  decisive test.** The critic's rank 4 asked for the rms and plateau within √(chain² + (R × power rms)²): about 0.35 °C on
  aifoundry3 and about 1-1.3 °C governed on aifoundry2. The registered lines are 95% bands on the closed loop's gain. On
  aifoundry3 they are 0.60-0.69 °C (floats) and 0.94-1.45 °C (int8), 1.7-4.1 times the critic's 0.35 °C (2.2-2.6 times its form
  at this lane's σ). G1q's is 3.15 °C, 2.4-3.1 times 1.0-1.3 °C. Under them no hold's verdict separates M8 from M7 or M6: the
  largest gap on the plan, K_L's M8 − M6 of −0.82 °C, is 0.56 of its band (K_S +0.15, K_O +0.37, K_Q −0.06 °C). The float bands
  also leave out E97's between-session plateau moves of 0.3-0.8 °C. So the informative figures are the session rms of the pool-6
  plateau errors and E − A per hold (the power path's share of each error), reported with M7's and M6's S through the same chain.
  The PASS count is not the result (`D4_bands_vs_the_critic_scale`).

**What A1 does to predicting power and heat.** It corrects one term's expected value, not the model. Heat over minutes from the
bits is still unscored, so no out-of-sample error changes until E154 and E161. The expected plateau rise of `fp32.real_smol_softmax_v_causal`
on aifoundry3 at 79% duty is **+11.72 °C** (not +11.37) and of `int8.real_qwen_w8a8_v` **+6.09 °C** (not +6.21), both over the
tails they carry in; the expected 95% sizes stand (0.60-0.69 °C floats, 0.94-1.45 °C int8, 3.15 °C for G1q, ±0.60 °C at the
trip). G2q's clock from the bits carries ±35 MHz from the power path plus up to −23 MHz from the heat path's R, which E161 reports
beside its verdict. Kinds page [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
items 9, 8 and 6; Q138's final critic, rank 4 (its desk half; E154 and E161 score it).
