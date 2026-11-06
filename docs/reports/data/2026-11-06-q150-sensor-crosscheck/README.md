# Q150(fault-xcheck): the card's meters tested against each other on committed data, post hoc - no meter artifact explains E178's small int8 pair; aifoundry3's meter now refreshes every 155-166 ms, not the 263 ms the records give; the delivery-loss fit leaves the random TensorFMA kinds 0.4-0.95 W above it, with an off-rail curve the September catalogue does not show; card 1's +10% after V squared is seen half to three quarters by the independent board meter, and is not a voltage misreading

*The owner's question of Fri 6 Nov 2026, about 14:05 PST, after E178's result (Q150): "Are there more accurate ways of checking power draw?
Maybe there are multiple sensors. I think there are per-shire power draw sensors. Also, allow the possibility that maybe there's something
wrong with the sensors." This directory is the part of Q150 that tests the sensors against each other. **Desk only, on committed data
only, and POST HOC throughout:** everything here was read after every run's data was committed; no card, box or device was touched; no
registered number, rule, threshold or verdict of any run changes. Its sibling, [`2026-11-06-q150-meter-checks/`](../2026-11-06-q150-meter-checks/README.md)
(Q150's inventory lane), reads the meters' reset windows and voltage monitors.*

## The answer

| question | reading (post hoc) | verdict |
|---|---|---|
| **Could a meter artifact shrink E178-H-int8 (int8 5s - 4s) from M10's +0.186 W to +0.053 W, about 3.5x?** | Read on every meter: board +0.053 W [+0.022, +0.085] as scored, **+0.075 [+0.042, +0.107] without the leak correction**; minion rail +0.026 to +0.054 W by filter model, every interval under the rail's forecast +0.156; SRAM rail +0.001 ± 0.008, NoC rail -0.000 ± 0.008; off the three rails +0.030 [-0.020, +0.080] (its forecast +0.030 inside). Across the 13 int8 one-number kinds the board's D against the forecast has slope **0.375 ± 0.076**, the minion rail's **0.328 ± 0.070**, and the rail against the board 0.80, the anchors' own share. The anchors read 0.36-1.8% from their three earlier sessions on this card. | **No.** Two independent meters see the same small difference and the same compression. The one meter-side term is the leak correction, fed by the whole-degree die reading: it takes 0.021 W [-0.008, +0.050] off the pair (0.40 to 0.29 of the forecast, a factor 1.4), where the pair's real extra heat would justify at most 0.004 W. The rest, about 2.5x, is the model's. |
| Board against the three rails plus the delivery-loss fit, E46's catalogue | the fit reproduces exactly (rms 0.3323 / 0.3078 / 0.4780 W, aifoundry2 / aifoundry3 / card 1); instructions +0.04 to +0.08 W mean residual; DRAM 1.0-1.2 W rms (random above, zeros below, as published); pass-to-pass offsets within ±0.044 W; the minion rail's share of the board within 0.3-0.5% across a session's passes; no curvature (b = -0.0004 ± 0.0004, +0.0006 ± 0.0004, -0.0008 ± 0.0007 per W) | closes, as published |
| The same on the TensorFMA sessions E171, E172, E178 | E178's 219 one-number runs -0.035 W on 6.45 W (-0.2%); the random anchors **+0.42 / +0.58 W** on aifoundry3 (E171 / E178, +1.8% / +3.1%) and **+0.95 W** on card 1 (+5.2%); the off-rail watts curve up with the minion rail, **b = +0.0040 ± 0.0002, +0.0042 ± 0.0002, +0.0035 ± 0.0004 per W**, with every filter model and in a late window; the zeros' residual does not drift within a session (-0.05 ± 0.09, +0.03 ± 0.09, +0.28 ± 0.28 W/h) | **the fit does not carry to the random TensorFMA kinds**; the cause is not placed |
| Card 1's rail excess after V squared (1.08-1.10 x aifoundry3 at equal work per op) | on pool 8's 63 shared items: minion rail **1.098** (the reductions) to 1.101 (raw), **board 1.054 to 1.076**; the minion share of the board 1.043 / 1.024 x aifoundry3's; card 1's set point 500 mV against a measured 498.3-499.0 mV (aifoundry3 525 / 521.2-522.1) | **not a voltage misreading. Half to three quarters of it is on the independent board meter too** (real power per op, or the board meter's gain); 2-4% sits between card 1's rail and its board (a rail-meter gain or the regulator's efficiency). The data cannot separate the two halves. |
| Electrical against thermal, E181's five holds (aifoundry3) | the chain closes on the fp32 hold to 0.28% (-0.039 °C on 14.09 °C) and misses Z, L1 and L2 by +0.35, +0.25, +0.50 °C; the best single board gain is -1.7% and only lowers the rms from 0.293 to 0.256 °C; heat taken to follow the three rails lowers it to 0.205 °C (first order); L1 and L2, the same item, differ by 0.24 °C with 0.25 W less power in L2 and a 0.48 W warmer rest before it | **the board's gain is stable against the chain's calibration to about 0.3% on aifoundry3; the misses are the thermal model's, not a meter gain** |
| Electrical against thermal, across cards (the 4.5 s window, every kept run) | °C per board W, with an intercept: aifoundry3 0.115-0.121 over four sessions, card 1 0.129-0.133 over three (**1.10x**); per minion-rail W 0.145-0.152 against 0.155-0.161 (1.05x) | each card's heat per watt is stable to ±1-3% across sessions; **across cards the thermal path is unknown, so heat cannot give a card's meter gain** (if anything it reads card 1's meters low, not high) |
| The meters' limits on today's data | aifoundry3's board value changes every **163-166 ms** and its rails every **154.7-155.0 ms** (E171, E178), card 1's every 169-171 and 156.7-156.9 ms; the sampler took 22 ms (11 ms in E181's), never over 24 ms; the minion rail's lag re-fitted on E178: **τ 0.94 s, delay 0.20 s**; quanta 10 mW (board), 1 mW (rails), 1 mV, 1 °C, one PVT code | **the records' 263 ms for aifoundry3 (E41, 26 Sep) and E58's 0.255 s pass delay are stale**; E78's registered 0.95 s / 0.2 s model fits today's telemetry |
| The noise budget, E178 | one sample's sd in a run's window 0.062 W; 12 distinct values in a 2 s window; the meter's own floor on a run's mean **0.018 W**; run to run **0.082 W** (board), 0.104 (minion rail), 0.011 (SRAM), 0.013 (NoC); pass to pass 0.057 W (board); the leak correction alone 0.047 W within a kind | the run-to-run scatter is 4.5x the meter's sampling floor: **the chip and its thermal state set the noise, not the meter** |

## Builds on

- **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 14:40 PST. Public rows read: P01, P03, P11, L03, L06, L08, L11, L15, L22,
  H07, H14, H22, H24, H27, H28. The ids are opaque pointers into a private inventory.
- **Used (every input is a committed file, read at the lab HEAD the outputs name, each checked equal to HEAD's blob; their sha256 are in
  `crosscheck.json` › `inputs_sha256`):**
  - E46's catalogue and the delivery-loss fit: [`2026-09-23-energy-manual/catalogue.json`](../2026-09-23-energy-manual/catalogue.json),
    `catalogue-23sep.json` and `unmetered_fit.json` beside it (`tools/ettelem/fit_unmetered.py`'s coefficients, reproduced to 0.0001 W rms);
  - pool 8's E171 (aifoundry3) and E172 (card 1), and today's E178 and E181: each primary reduction's `runs.csv` and `e1NN.json`, every kept
    pass's `telemetry.jsonl.gz` and `runs.jsonl`, E178's `scored.json`, E181's `scored-m11.json`;
  - the anchors' sessions on each card: E153, E163 (aifoundry3) and E157, E164 (card 1), each `e1NN.json` and `runs.csv`;
  - the reduction itself: `tools/claims-v3/kinds/reduce_e78.py`'s windows, deconvolution and zeros interpolation, re-implemented here and
    checked: this script's board D and minion Drail equal the committed `runs.csv` columns to 0.0000 W on all 883 kept runs of E171, E172
    and E178 (`crosscheck.json` › `B_tensorfma` › `sessions` › `checks`);
  - E58's per-rail filter (findings 14, "The telemetry", the rails row; `05-claims.md` lines 770-773) and E78's registered model;
  - M7's 4.5 s heat law (`2026-11-03-q139m-model/README.md` line 131) and Q138(t)'s chain as E181's scorer ran it;
  - the energy manual's [`09-method.md`](../../../energy-manual/09-method.md) and its dated notes 1-2 (the public firmware's one fixed board-meter
    gain; the rails' and the board average's filters), findings 14 and 19.
- **Not used:** the card schematic's sense network (still owed, `09-method.md`'s dated note 1); E180's data (another run's, not read here);
  any lab hardware or firmware rung (the riser, the camera, a signed image); the forecasts' model files beyond E178's own `scored.json`.
- **Tiers:** public only.

## 1. The board against the three rails plus the delivery-loss fit

The fit: unmetered W = a × minion W + b × SRAM W + c × NoC W + d × DRAM bytes, per card (aifoundry3 0.181 / 0.043 / 0.294 / 72.7 pJ/B; card 1
0.102 / 0.540 / 0.205 / 81.6). The residual is the board less the three rails less that.

**E46's catalogue (26 Sep, three shuffled passes on each card), configuration means** (`A_catalogue`):

| card | instructions (312): mean residual | on-chip bytes (63) | DRAM (17): rms; random / zeros | pass offsets | minion share by pass | curvature b per W |
|---|---|---|---|---|---|---|
| aifoundry2 | +0.079 W | +0.038 W | 0.99 W; +0.88 / -0.06 | -0.022, -0.009, +0.032 | 0.830, 0.832, 0.828 | -0.0004 ± 0.0004 |
| aifoundry3 | +0.044 W | +0.010 W | 0.99 W; +0.89 / -0.10 | +0.010, +0.005, -0.014 | 0.838, 0.838, 0.836 | +0.0006 ± 0.0004 |
| card 1 | +0.072 W | +0.054 W | 1.19 W; +0.94 / -0.16 | +0.006, +0.037, -0.044 | 0.881, 0.883, 0.886 | -0.0008 ± 0.0007 |

Between the 23 and 26 September catalogues the minion share of the board moved +1.1% on aifoundry2 and -0.5% on aifoundry3 over the
configurations both ran with more than 8 W on the minion rail. Over the instructions the residual against the die's temperature reads
+0.021 ± 0.005 W per °C on aifoundry2, -0.051 ± 0.021 on aifoundry3 and +0.006 ± 0.020 on card 1.

**The TensorFMA sessions, run by run** (`B_tensorfma`). D is the kind less its type's zeros at the same time, on every meter, raw (no leak
correction on any meter), the rails deconvolved with the session's own re-fitted minion lag (E171 τ 1.00 s, delay 0.15 s; E172 0.94 / 0.20;
E178 0.94 / 0.20) and E58's SRAM and NoC time constants:

| session | class | runs | board D, W | board - (rails + fit), W | share of D: minion / off-rail |
|---|---|---|---|---|---|
| E178, aifoundry3 | one-number kinds | 219 | 6.45 | **-0.035** (-0.2%) | 0.836 / 0.152 |
| E178 | random anchors | 36 | 18.43 | **+0.579** (+3.1%) | 0.807 / 0.179 |
| E171, aifoundry3 | `anchor_pi` | 8 | 8.55 | -0.182 | 0.860 / 0.128 |
| E171 | random anchors | 36 | 18.43 | **+0.415** (+1.8%) | 0.818 / 0.169 |
| E171 | pool tiles, D ≥ 3 W | 235 | 14.83 | +0.213 | 0.828 / 0.160 |
| E172, card 1 | random anchors | 27 | 18.09 | **+0.951** (+5.2%) | 0.836 / 0.144 |
| E172 | pool tiles, D ≥ 3 W | 175 | 14.56 | +0.623 | 0.850 / 0.130 |

- **The off-rail watts grow faster than the minion rail's** in all three sessions: off-rail = a m + b m², b = +0.0040 ± 0.0002 (E171),
  +0.0042 ± 0.0002 (E178), +0.0035 ± 0.0004 (E172) per W, so the off-rail share runs from 0.16-0.17 at 5 W to 0.22-0.23 at 20 W on aifoundry3
  (0.12 to 0.18 on card 1). b stays at 0.0038-0.0045 on aifoundry3 and 0.0035 on card 1 with E58's filter and E78's, and at 0.0043-0.0045 on
  aifoundry3 in a late window (3-4 s after the launch, where the rails have nearly settled), so it is not the filter. The September catalogue's instructions, over the same 0-27 W of minion rail, show none.
  A regulator's conduction loss (about 1 mΩ would do), a nonlinearity of either meter that appeared after September (both cards changed
  service-processor firmware since), or an off-rail consumer of the TensorFMA work would each look like this; these data cannot tell them apart.
- **The rails' filter moves a 2 s window's rail level by 0.2-0.4 W on a 20 W step:** E171's random-anchor residual reads +0.23 W with E58's
  filter, +0.42 with the re-fitted one and +0.65 with E78's. A matched pair (the same timing, nearly the same level) cancels it: E178's int8
  pair moves by at most 0.011 W between the three.
- **Stability:** the random anchors read within 0.36% (fp32), 0.38% (fp16) and 1.8% (int8) over E153, E163, E171 and E178 on aifoundry3
  (3-6 Nov), and 0.30 / 0.20 / 1.0% over E157, E164 and E172 on card 1; their minion share stays within 0.795-0.802 and 0.831-0.836
  (`D_thermal` › `anchor_stability`). Neither meter's gain moved against the other by more than about 1% over those days.

**Card 1 against aifoundry3, pool 8's 63 shared items with D ≥ 2 W on both** (`C_card1_vs_a3`; per item in `card1-vs-a3-items.json`):

| card 1 / aifoundry3 | the reductions' own D and Drail (leak-corrected) | raw, re-fitted filter |
|---|---|---|
| board, per op | 0.963 | 0.983 |
| minion rail, per op | 1.003 | 1.008 (1.010 without card 1's 22 running-maximum samples) |
| V squared, aifoundry3 over card 1 (on-die minion reading) | 1.0943 | 1.0943 |
| **board after V squared** | **1.054** | **1.076** |
| **minion rail after V squared** | **1.098** | **1.101** |
| minion share of the board | 1.043 | 1.024 |
| off the rails | | 0.81 |

- **Not a voltage misreading.** Card 1's set point is 500 mV and it reads 498.3 mV busy and 499.0 at rest; aifoundry3's 525 against 521.2 and
  522.1. The SP's `minion_mv` and the on-die `die_mv.minion` agree to the millivolt in 95.8% (aifoundry3) and 98.6% (card 1) of samples and
  never differ by more than 2 mV, so they are one measurement, not two; the set point confirms it within 2 mV, as the sibling directory
  also reads. A misreading big enough for the 10% would be about 25 mV.
- **Most of it is on both meters.** After V squared the board, an independent 12 V meter, reads 5.4-7.6% high where the rail reads 9.8-10.1%:
  55-75% of the rail's excess. That part is real power per op (more switched capacitance, or energy that does not scale as V squared between
  499 and 521 mV) or the board meter's own gain (the public PMIC firmware divides every board's 12 V reading by one fixed factor, so a board's
  sense-path tolerance goes uncorrected). The remaining 2.4-4.3% sits between card 1's rail and its board: a rail-meter gain or the regulator's
  efficiency. The fit's minion coefficients (0.181 against 0.102) read as a gain would give 1.072. **Only an external meter (the riser, rung
  8) separates these.**
- **Heat does not settle it.** With an intercept (the whole-degree reading's offset at the launch edge), card 1's window rises 0.129-0.133 °C per
  board W over E157, E164 and E172 against aifoundry3's 0.115-0.121 over E153-E178 (`H_heat_sessions`), 1.10x, and 1.05x per minion-rail W.
  A card that heats more per measured watt has either a weaker thermal path or meters that read low; it is no evidence for a card-1 rail that
  reads high. Each card's own figure is stable across sessions to ±1-3%. (M7's law, 0.1186 / 0.1151 °C per board W, is a fit through 0 over
  24 experiments; through 0 the per-session figures here scatter 0.101-0.130 because the intercept moves.)
- Card 1's minion rail returned its running maximum in 22 of E172's 23,045 samples (aifoundry3: none in 33,218 and 26,024), 8 kept runs with
  one near their windows: the known glitch of findings 14, worth 0.2% on the card ratio here.

## 2. The electrical watts against the thermal response: E181's five holds

Each hold's watts are its mean over its 600 s less the mean over the last 120 s of the rest before it (the chain's own anchor window), on
every meter; R, P and e are the scorer's (`scored-m11.json`). One session, aifoundry3 (`D_thermal`):

| hold | item | board above rest, W | on-rail share | board - (rails + fit), W | dips (gap duty) | e = R - P, °C | e / P |
|---|---|---|---|---|---|---|---|
| H_E | fp32.randn (duty-cycled) | 16.03 | 0.835 | +0.21 | 11 (0.50%) | -0.039 | -0.3% |
| Z | fp32.zeros | 2.08 | 0.898 | -0.11 | 0 (3.86%) | +0.345 | +49% |
| L1 | int8.full | 11.77 | 0.874 | -0.40 | 140 (3.77%) | +0.253 | +2.7% |
| S | int8.neg_ones | 4.90 | 0.895 | -0.28 | 115 (3.76%) | -0.008 | -0.2% |
| L2 | int8.full | 11.52 | 0.872 | -0.35 | 147 (3.77%) | +0.496 | +6.0% |

- **A board gain does not explain the misses:** the one gain that fits best is -1.7% and leaves 0.256 °C rms of 0.293.
- **Heat that follows the three rails explains part:** scaling each hold's predicted rise by its on-rail share over H_E's leaves 0.205 °C rms
  (first order; the power history is ignored). The int8 holds put more of their board watts on the die's rails than fp32 random does
  (0.87 against 0.835), and the delivery-loss fit reads them 0.28-0.40 W below it (the curvature of section 1).
- **L1 and L2 are the same item.** Their misses differ by 0.24 °C while L2 drew 0.25 W less above its rest and its rest ran 0.48 W warmer
  (its anchor 53.33 °C against 51.88): the miss follows the session's warming floor, a thermal-model term.
- So on aifoundry3 **the board's gain agrees with the chain's calibration to about 0.3%** (H_E), and nothing here says a meter is wrong.

## 3. The meters' own limits on today's data

Every kept pass of E171, E172 and E178, and E181's measured pass, as committed (`E_limits` › `passes`):

| reading | quantum | refresh (mean time between changes) | notes |
|---|---|---|---|
| `board_w` | 10 mW (every value a multiple) | aifoundry3 163-166 ms, card 1 169-171 ms, E181 147 ms | an instant held for one SP pass; repeats lengthen the board's figure |
| `sp.board_avg_w` | 10 mW | about 158 ms | the PMIC's average: re-fitted τ 1.01 s with no delay (E58: 1.05 s, current) |
| minion, SRAM, NoC rails | 1 mW | minion 154.7-155.0 ms (aifoundry3), 156.7-156.9 (card 1) | the minion lag re-fitted on E178: **τ 0.94 s, delay 0.20 s** (E58, 29 Sep: 1.06 s and 0.255 s); SRAM and NoC barely move in TensorFMA work (0.008 W per board W), so their filters cannot be re-fitted here |
| `die_mv` | 1 mV | | the minion rail read 521, 522 or 523 mV in every E178 and E181 sample |
| `temp_c.minshire[0]` | 1 °C | | the whole-degree firmware mean |
| E181's 34 PVT codes | 1 code (0.061 °C); their mean 1/34 code | 107 ms | |
| the sampler | | 22 ms a sample (11 ms in E181's) | no sample over 24 ms: nothing starved the meter |

- **aifoundry3 now refreshes as often as aifoundry2.** Findings 14 and `09-method.md` give a new value every 263 ms under the 10 Hz sampler there
  (E41, 26 Sep, release 1.3.1), and E58 a one-pass delay of 0.255 s. Every aifoundry3 pass read here changes its rails every 155 ms; the
  card has run another service-processor build since 7 October. E78's registered model (τ 0.95 s, delay 0.2 s) fits today's telemetry; E58's
  delay does not.
- **The dips are real.** A board reading that lands in a 1-3 ms launch gap is held for a pass. Inside the launch spans, the share of samples
  that read a dip is 0.64-1.37 of the gaps' duty in every E171, E172 and E178 pass, and 0.45 in E181's holds (whose gaps run 3.8% of the time):
  the dips are the gaps' own instants, sampled at random, and the board meter's aperture is shorter than a gap. Kept, they give the true mean
  power (gaps included), which is what heats the die; removed, as every primary reduction does, the in-launch power, up to about 0.5% higher.
- **E181's sampler counts a command mismatch on every tick** (44,166 of 44,166): the on-die voltage reply carries another command id, which
  E89's amendment A2 found and the sampler tolerates by matching on the tag. It is a firmware quirk, not a meter fault.
- **The noise budget (E178):** one sample's sd inside a run's window is 0.062 W, so the 10 mW quantum is 0.16 of it and dithers away; a 2 s
  window holds 20 samples but 12 distinct values, so the meter's own floor on a run's mean is 0.018 W. The run-to-run scatter is 0.082 W on the
  board's D (0.104 on the minion rail, whose deconvolution amplifies its end readings; 0.011 SRAM; 0.013 NoC) and the pass-to-pass 0.057 W.
  The leak correction, k times the whole-degree window rise, scatters 0.047 W within a kind. The meter's sampling is a quarter of the scatter.

## 4. E178's int8 pair through every meter

E178-H-int8 in the scorer's form (per pass the mean over segments of D(5s) - D(4s); over the four kept passes the mean and t(0.975, 3)
interval), on every reading (`F_int8_pair`):

| meter | 5s - 4s, W (95%) | forecast | reading |
|---|---|---|---|
| board, as scored (leak-corrected) | **+0.0532 [+0.0217, +0.0848]** | +0.1857 | reproduces the scorer |
| board, no leak correction (dips removed) | **+0.0746 [+0.0421, +0.1072]** | | 0.40 of the forecast |
| the leak correction itself, k x the whole-degree window rise over zeros | +0.0214 [-0.0076, +0.0505] | at most +0.004 from the pair's real heat | the 5s windows read 0.10 °C [-0.04, +0.25] warmer in whole degrees |
| minion rail, the reduction's Drail | +0.0261 [-0.0281, +0.0804] | +0.1560 | forecast above |
| minion rail, raw, re-fitted / E78 / E58 filter | +0.043 [-0.016, +0.103] / +0.044 [-0.015, +0.102] / +0.054 [+0.030, +0.079] | +0.1560 | forecast above in every model |
| SRAM rail, raw | +0.0012 [-0.0066, +0.0089] | | nothing |
| NoC rail, raw | -0.0001 [-0.0084, +0.0083] | | nothing |
| off the three rails | +0.0302 [-0.0195, +0.0799] | +0.0302 | forecast inside |
| the die, whole-degree window rise | +0.104 °C [-0.037, +0.245] | +0.022 °C at the forecast (M7's law) | not resolvable: E178 recorded no per-sensor codes |

**What each artifact could do, and does:**
- **Gain:** a gain that shrank the pair 3.5x would shrink everything; the session's fp32 and fp16 random anchors read 1.009 and 1.002 of E171's
  (the scorer's own scale), int8.full 7.09 W against 7.11-7.22 in the three earlier sessions. Excluded.
- **Filter:** the board reading is not filtered; the rails' filter is undone, and a linear filter does not shrink a steady difference. The three
  filter models move the rail's pair by 0.011 W. Excluded.
- **Quantization:** 10 mW against a 0.062 W sample sd, averaged over about 12 values a window, 3 couples a pass and 4 passes: no bias. Excluded.
- **Staleness:** each reading is an instant held for about 155 ms, and the two kinds share every timing; the dips go out by the same rule.
  Excluded.
- **The meter missing part of the power:** the board meter reads the 12 V input only, but the minion rail, a separate meter on the regulator
  that feeds the cores, sees the same small difference, and SRAM and NoC see none. Excluded for both at once.
- **The rail's averaging:** a running average keeps a steady level. Excluded.
- **The whole-degree die reading, through the registered leak correction:** -0.021 W, a factor 1.4 of the 3.5. The registered footing stands;
  this only says how much of the shrink the reading carries.

**The cross-kind slope against the anchors.** Over the 13 int8 one-number kinds, measured D against the scored forecast P: board slope 0.375 ±
0.076 (intercept 0.99 W), minion rail 0.328 ± 0.070, the rail against the board 0.80 ± 0.12; per flip, 2.78 ± 0.58 fJ on the board (E178-W-int8's
2.78) and 2.42 ± 0.53 fJ on the rail. The kinds' common level is near the forecast (P 1.71-2.17 W above zeros, D 1.59-1.82 W) while their spread
is compressed, on both meters alike, and the anchors that span 0 to 7 W in int8 read at their usual level. **A meter that read the anchors right
and compressed only the one-number kinds' differences would need a dead band near 1.7 W on two independent meters; the model's per-flip price
for one-number kinds is what is too high.**

## Faults and limits, as found

1. **Stale records (FAULT, records):** aifoundry3's 263 ms refresh (findings 14's telemetry table, `09-method.md` item 1) and E58's 0.255 s pass
   delay no longer describe the card: today 155 ms (rails) and 163-166 ms (board).
2. **The delivery-loss fit does not carry to the random TensorFMA kinds (LIMIT):** +0.4 to +0.95 W above it, with an off-rail curve (b about
   +0.004 per W) the September catalogue does not show. Cause not placed (the regulator, a meter nonlinearity, or the work).
3. **The rails' filter is the largest systematic in a 2 s rail level (LIMIT):** 0.2-0.4 W on a 20 W step between the models; it cancels in
   matched pairs.
4. **Card 1's +10% after V squared (NOT SEPARABLE):** not a voltage misreading; 55-75% of it on the independent board meter; 2-4% between
   card 1's rail and its board.
5. **The two minion-voltage fields are one measurement (LIMIT):** V squared rests on it and on the set point, which agree within 2 mV.
6. **Card 1's minion rail returns its running maximum (KNOWN FAULT, confirmed):** 22 of 23,045 samples in E172; 0.2% on the card ratio.
7. **The dips (NOT A FAULT):** true instants of the launch gaps, at their duty.
8. **Heat against the board (CLOSES on fp32):** aifoundry3's board gain agrees with the chain to about 0.3%; the int8 and zeros holds' misses
   are the thermal model's.
9. **Heat across cards (NOT SEPARABLE):** card 1 heats 1.10x per board W, 1.05x per rail W; the cards' thermal paths are not known.
10. **E178's int8 pair (NOT A METER ARTIFACT):** both meters agree; the leak correction from the whole-degree die reading carries a factor 1.4.

## What it changes

Nothing registered. For the next card time: register the rails' filter from the session's own telemetry (or E78's model) and state the SP
pass as measured on the day; register a one-number pair's footing with and without the leak correction, or read the die with the per-sensor
codes (E181's sampler) so the correction no longer rests on whole degrees; put an external meter on one card (the riser) before claiming a
card's gain. The sensor-validation registration and the ranking of methods are Q150's synthesis, not this directory's.

## Reproduce

From the top of the repository, with numpy:

    python3 docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_crosscheck.py --out docs/reports/data/2026-11-06-q150-sensor-crosscheck

It refuses any input that git does not track at HEAD or whose bytes differ from HEAD's blob, records each input's sha256, and writes
`crosscheck.json`, `crosscheck.txt` and `card1-vs-a3-items.json`. A run takes about a minute on one core.

## Files

| file | what |
|---|---|
| `q150_crosscheck.py` | the study: sections A-F and H, every input checked against HEAD |
| `crosscheck.json` | every reading, by section, with the inputs' sha256 and the lab HEAD it read |
| `crosscheck.txt` | the readings in one page |
| `card1-vs-a3-items.json` | pool 8's 63 shared items, card 1 against aifoundry3, on every meter |
| `SHA256SUMS` | every file here but itself |

SPDX-License-Identifier: Apache-2.0
