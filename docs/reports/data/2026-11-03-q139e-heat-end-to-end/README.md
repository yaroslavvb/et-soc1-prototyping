# Q139(e): heat over minutes predicted end to end from the bits, frozen for E154 (aifoundry3) and E161 (aifoundry2) (desk, Tue 3 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
items **9** (a steady state for heat), **8** (the heat path between sessions) and **6** (the power model). It answers Q138's final
critic, **rank 4**: "Heat over minutes predicted end to end from the computation's description... The bits-to-power-to-chain path for a
new kind has never been scored." Desk only: no card, no device command, nothing set, nothing refitted. Written 05:43-06:10 PST on the
Intel, after Q139(x)'s pool-6 predictions commit `d98d2e34` (05:39:23 PST) and before any E154 or E161 claim.*

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

**The bands, derived here.** Each is 1.96 × √(σ_chain² + (G σ_power)²):

| | σ_chain (1σ) | G (°C per W) | σ_power (W) | 1σ (°C) | 95% (°C) | the critic's form |
|---|---|---|---|---|---|---|
| aifoundry3 | 0.18 °C, E144's blind arm (a) rms | 1.0-1.25: the closed loop's d(plateau)/dS × share (the leakage loop adds 30-40% over the open chain's 0.87) | M8's own 95% D band / 1.96, with the zeros level's spread between sessions (0.106 W fp32, 0.071 W int8, 85 committed sessions) added in quadrature: 0.24-0.63 | 0.31-0.74 | 0.60-1.45 | 0.28-0.57 °C (√(0.18² + (0.87 σ)²)) |
| aifoundry2, 800 MHz | 0.76 °C, E144b G1's blind arm (a) rms | 0.938, the closed loop's gain at 800 MHz | √(1.443² + 0.442²) = 1.51: M8's pinned end-to-end board rms and the reference die's 1 °C | 1.61 | 3.15 | 1.30 °C (√(0.76² + (0.663 × 1.6)²)) |
| aifoundry2, trip | Q138(t)'s G2 band | — | — | — | ±0.60 | — |

These come out wider than the critic's scale for two reasons. The leakage loop amplifies a power error by 1/(1 − loop gain), about
1.4× on both cards, where the critic's form used the open chain's R. And on aifoundry3, int8 line tiles carry M8's widest D band,
±1.22 W.

**One derived number, from committed pre-pool-6 data:** aifoundry2's reference die for M8's burst board, **56.0 °C**. E144b G1's
800 MHz hold samples give board = 16.45 + 0.410 × die (8,723 samples). On that line, E80's int8 −1s burst board of 39.4 W (800 MHz,
first second, launched at a reading ≤ 55 °C) reads 55.97 °C ([`predictions-q139e.json`](predictions-q139e.json) ›
`aifoundry2.T_REF_check`). Without it, a burst board cannot be carried to a hold's die.

**Post hoc back-check (not a rule):** the same composition on E144b's G1 hold, int8 −1s, a hold neither M8 nor Q138(t) was fitted
on, with E78's measured D for the kind. It gives a plateau of 59.43 °C against 58.92 measured (+0.51 °C) and a board 1.9 W high. That
is M8's relation reading int8 −1s 1.3 W over E80's burst, partly offset by the session's 0.711 °C per W against the chain's 0.663
(`aifoundry2.backcheck_E144b_G1_posthoc`).

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

## What this cannot say

- **The 10-minute holds read 92-95% of their fixed points.** The plateau is defined as the same window in prediction and score, so it
  is like for like. It is not a steady state.
- **Two holds start on a tail.** K_Q starts 4.3 °C and K_S 3.2 °C above the room. The chain carries those tails; E144's H_L did the
  same and scored 0.04 °C.
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

## How to reproduce

```bash
python3 docs/reports/data/2026-11-03-q139e-heat-end-to-end/predict_q139e.py > docs/reports/data/2026-11-03-q139e-heat-end-to-end/predictions-q139e.txt   # ~10 s
```

It checks the sha256 of every frozen input first: Q138(t)'s model, chain code and scorer, M8's pool-6 predictions for aifoundry3 and
aifoundry2, `m8.json` and E78's `e78.json`. Its output is byte-identical on a rerun. numpy 1.26.4, Python 3.9.

## Files

| file | what |
|---|---|
| `predict_q139e.py` | the composition: M8's S (aifoundry3) and burst relation (aifoundry2) through Q138(t)'s frozen chain, the duty solve, the governor's cap and trip, the bands and the rules |
| `predictions-q139e.json`, `.txt` | **frozen**: both designs, every hold's trajectory, plateau, peak, band and FAIL line, the plateaus by room, the M7/M6 arms, T_REF's check, the back-check, the rules |
