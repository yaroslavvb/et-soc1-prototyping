# The joined load model (Q126), 26 October 2026

One model that takes a load and returns board watts, the clock the governor gives it, the die temperature, the
speed and the energy per unit of work. Until now four pieces did parts of this and none of them joined:

- the flip model, [`tools/ettelem/predict_heat.py`](../../../../tools/ettelem/predict_heat.py) — fp32
  TensorFMA32 tiles only, with no clock, voltage, card or temperature input, a static part of 27.11 W at every
  clock and no term for the cost of running a kernel at all;
- the instruction-and-byte catalogue, [`docs/energy-manual/`](../../../energy-manual/README.md) — 161
  instructions and every memory level, but no predictor reads it;
- E60 and E61's measured per-flip prices — in no predictor;
- E64's governor and heat path — in its own reduction.

The model is [`tools/ettelem/load_model.py`](../../../../tools/ettelem/load_model.py); its command line is
[`tools/ettelem/predict_load.py`](../../../../tools/ettelem/predict_load.py).

## The form

```
P_board = idle(T, card)                     the idle law, re-anchored on E64's own 600 MHz floor
        + k_clk * (s(f) - 1)                the clock-dependent static part (E64's floor by clock)
        + c0 * s(f)                         a per-kernel offset, paid once while any hart runs
        + p_sm * (active/1024) * s(f)       the tensor state machines
        + flips * prices * s(f) * k_T * k_card      the four fitted flip prices, zero-gated
        + catalogue rows * k_card           instructions, bytes per memory level, bytes per mesh hop

s(f, V) = (f/600) * (V/0.517)^2      k_T = 1 + temp_coeff * (T - T_fit)
```

f, V, the card, the die temperature, the switching-temperature coefficient and the card scale are **arguments**,
not constants applied by hand afterwards. `predict_heat.py` keeps the same four arguments with defaults that
reproduce its old numbers to the digit (`--f 600 --volts 0.517 --card aifoundry2 --temp-coeff 0`).

## The files

| File | What |
|---|---|
| `frozen_predictions.json` | predictions for four loads the model never saw, with the rule and the assumptions behind each. Committed and pushed **before** `scores.json` |
| `scores.json` | the same predictions against the committed measurements |
| `fit.txt` | the fitted static constants and their residuals, as `load_model.py` prints them |
| `backtest_e64_e62.json` | how the new terms changed E64's 103-point rms and E62's hart ladder |

## How frozen the predictions are

Frozen by commit order: `frozen_predictions.json` was pushed to `main` before any score was computed, and no
coefficient and no rule was changed after a predicted number was put beside its measurement. **It is not blind.**
The session read the four experiments' records while choosing their operating points — the duty cycles, the
op rates, the die temperatures and the cards all come from the same files that carry the measured watts — so a
measured value was on screen before its prediction was written. E13's and E38's pre-registrations were stronger
than this one. What this does establish is that one script, with coefficients from other experiments, produces
every number without a person in the loop.

The model's coefficients come from E17 (21 Sep), E44, E60, E61, E62, E64 and the energy manual's catalogue, and
from nothing in E37, E39, E43 or E59.
