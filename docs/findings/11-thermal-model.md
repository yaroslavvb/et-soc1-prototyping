# Finding: a three-line model from transistor flips to die temperature

**Sources:** E17 (the fit and the validation), E11 and E13 (the flip counts), E9 and E12 (the measurements
fitted), E15 and E16 (data it was tested on). Published as A4 §8.

The model answers: *given a workload's operand values and how many cores run it, what will the card draw and
how hot will the die get?*

---

## The model

```
flips   F_j(t) = N_j(pattern) × 1.10×10⁶ ops/s × active minions      four kinds j, counted in RTL
power   P(t)   = 12.6 W + 23.3 W · e^((T−80)/36) + 1.85 W · active/1024 + Σ_j e_j · F_j(t)
heat    T(t)   = 22.8 °C + Σ_k x_k(t),    τ_k · dx_k/dt = R_k · P(t) − x_k
```

| Flip kind *j* | Energy *e_j* | What it counts |
|---|---|---|
| register bit clocked | **3.18 fJ** | bits of a pipeline register that saw a clock edge with enable high |
| net toggle in the multiplier tree | 0.025 fJ | Booth encoders, carry-save adders, 4:2 compressors |
| other net toggle in the unit | **0.80 fJ** | exponent path, aligner, adder, normaliser, round, pipeline registers |
| operand-word bit toggled outside the unit | 15.5 fJ | register-file reads, bypass, fan-out to 8 lanes |

| Thermal stage τ_k | 1.5 s | 4 s | 60 s | 150 s | 400 s | 2,500 s | total |
|---|---|---|---|---|---|---|---|
| R_k (°C/W) | 0.106 | 0.050 | 0.234 | 0.136 | **0.860** | 0.081 | **1.47** |

The power line has a fixed part, leakage that grows exponentially with die temperature, the tensor state
machines of the active minions, and one energy per kind of flip. The heat line is a Foster chain: RC stages in
series, fitted on a fixed grid of time constants with every resistance held non-negative.

## How it was fitted, and what that does about overfitting

Three staged fits, each a least-squares with non-negative coefficients, so no stage can compensate for another
by borrowing its physics:

1. **Leakage** from the **idle** samples only — no launch within 4.5 s, 600 MHz — across all four sessions of
   21 September. Residual **0.20 W rms** over 64 to 88 °C.
2. **Flip energies** from the **busy** samples, with leakage held at what step 1 found. Residual **0.49 W rms**.
   These four numbers agree with an independent earlier fit that used only seconds 1–3 of the 46 short runs of
   E9.
3. **Thermal network** from the sensor reading driven by measured board power, over the whole session, with
   one intercept per session and one decay term per slow stage for the unknown starting state. Residual
   **0.63 °C rms**, against 0.29 °C that rounding to whole degrees would leave on its own.

Controls on overfitting:

- **Few, constrained parameters:** four flip energies, one state-machine term, two leakage numbers, and
  resistances on a *fixed* time-constant grid, all non-negative.
- **The effective sample size is runs, not samples.** The telemetry is 140,000 points at 10 Hz but heavily
  autocorrelated; the thermal part really rests on 27 runs.
- **The power half was cross-validated:** leave-one-pattern-out gives 0.50 W against 0.32 W in-sample (E9), and
  two separate sets of predictions were timestamped before measurement (E14, 0.92 W rms over 14 matrices).
- **One number is pinned from outside the fit:** the slowest stage is anchored by the single overnight idle
  equilibrium, 62 °C at 26.7 W.

## How well it predicts — held out, fitting nothing

The first published version of this report quoted a **12% median error** for the time to 90 °C without saying
that the thermal network and the leakage had been fitted on the very runs it was "predicting". That was a fit
number. The honest test (E17) refits **every** parameter on the first 7,400 s of the long session plus E9,
freezes the model, and predicts the 12 later runs. The thermal state at each launch comes from an observer
that has seen telemetry **up to that launch only**; from launch on, nothing measured enters the simulation.

| Test | Time to 90 °C | Ten-minute runs |
|---|---|---|
| **Held out in time** (12 runs, second half of E12) | median **9%**, worst 23%, 6 of 7 within 20% | end temperature **3.8 °C rms**, biased hot; 2 of 5 wrongly predicted to reach 90 °C |
| **Different session, new matrices** (E16), first-half model | median 7%, worst 65% | 5-minute run off by 1.0 °C |
| Same session, published model | median 2%, worst 68% | 5-minute run off by 0.2 °C |
| *(For reference: in-sample on E12)* | *median 12%* | *2.5 °C rms* |

The held-out runs include four patterns and two core counts the thermal fit had never seen.

### Where it breaks

- **Out to a few minutes it predicts about as well as it fits.** The big misses trace back to power, not heat:
  the DFT pair's power is 2.8 W low, and near this card's flip budget a watt of error is tens of seconds.
- **At ten minutes it runs hot,** by 3 to 5 °C on low-power runs.
- **The slow stages are not pinned down.** Between the half fit and the full fit the fast stages and the
  leakage barely move (0.106 and 0.050 °C/W at 1.5 and 4 s in both; 24.4 against 23.3 W of leakage at 80 °C),
  but the 400 s stage goes from 0.60 to 0.86 °C/W, the 1,000 s stage from 0.38 to nothing, and the
  operand-word energy from 20 to 15.5 fJ. **Do not quote the slow resistances as physics.**
- **It cannot run free for hours.** With a loop gain of 0.95, a 1% error in leakage grows into degrees and the
  simulated die drifts away within the hour. The model predicts *minutes ahead from a known state*.

## Two consequences worth knowing on their own

**Leakage is the biggest single item on an idle card** and it is what makes temperature so sensitive to flips
here: 23 of the 36 W an idle card draws at 80 °C, growing 0.65 W per °C.

**That closes a loop.** A watt of switching raises the die, the higher die leaks more, which raises it
further. Open loop the network gives 1.2 °C per sustained watt after ten minutes; with leakage feeding back it
gives **3.1 °C**, and the loop gain passes 1 at 82 °C:

| Sustained extra watt, for | 1 s | 10 s | 1 min | 10 min |
|---|---|---|---|---|
| network alone | 0.07 °C | 0.22 | 0.47 | 1.21 |
| with leakage feedback at 80 °C | 0.07 | **0.25** | **0.62** | **3.12** |

The practical consequence — a hard ceiling of about 3 W of sustained switching — is in
[12-heat-management.md](12-heat-management.md).

## Does it transfer to another card? Yes, up to one number

The strongest test available was re-running the strict protocol on aifoundry3 (E20): different silicon,
different heatsink, a launch temperature of 55.8 °C instead of 81.0 °C, and coefficients fitted entirely on
aifoundry2.

- **Applied unchanged, the model is off by 1.38 W rms** over eight operand patterns spanning 1.9 to 25 W.
- **The error is not scatter.** It is a consistent 8% overestimate, pattern by pattern: the ratios between
  patterns are right, only the overall size is wrong.
- **One scale factor of 0.924 fixes it**, leaving 0.20 W rms — as good as the in-sample fit on the card the
  coefficients came from.
- **Calibrating that factor on a single run** and predicting the other seven gives 0.36 W rms in the median
  and 0.27 W if the calibration run is random data. One matmul calibrates a new card.
- **The operating point does not explain the 8%**, and points the other way: aifoundry3 runs at 523 mV against
  518 mV at the same clock, so \(CV^2f\) predicts 2% *more* switching power, not 8% less. The gap is a
  property of the card — silicon, package or board regulator — and separating those needs a third working card.
- **The leakage law transfers too, further than it should.** Fitted on aifoundry2 between 62 and 90 °C and
  extrapolated 25 °C below that range onto the other card, it predicts aifoundry3's idle power to **+0.73 W**
  out of 25 W.
- **The thermal network does not transfer.** It never claimed to: 1.47 °C/W is one card in one chassis, and
  aifoundry3 sheds heat visibly faster. Nothing in this section uses it.

So: the *shape* of the data-dependence belongs to the design, and the *scale* and the *idle offset* belong to
the card.

## Reproducing

```
# fit (no card needed)
python3 tools/ettelem/flip_thermal_model.py DATA/long@13950 DATA/strict \
  --leak-only DATA/cold1 DATA/cold2 --anchor 62:26.7 --toggles DATA/toggles_all.json --out model.json

# held-out tests (fits nothing)
python3 tools/ettelem/validate_flip_model.py DATA/long@13950 --model DATA/model_firsthalf.json \
  --toggles DATA/toggles_all.json --after 7400
python3 tools/ettelem/validate_flip_model.py DATA/long2 --model DATA/model.json --toggles DATA/toggles_all.json
```

`DATA` is `docs/reports/data/2026-09-21-horace-aifoundry2/`. `tools/ettelem/finish_horace.sh` runs all of it.
