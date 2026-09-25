# Finding: on this card, only zeros can run at full load for long

[← Findings index](README.md) · published as [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment), sections 7 and 8
(A4) · numbers and sources: [05-claims.md](05-claims.md)

**Sources:** E12 (29 long runs), E16 (structured matrices), E17 (the budget), E9 (the 7 s baseline).

The 7-second experiments show the first two thermal stages. Running for minutes shows the rest, and it changes
the practical picture completely.

---

## Time from 80 °C to 90 °C

Every run starts from the same state (the strict start of [03-experiments.md](03-experiments.md)) and is
stopped at 90 °C. "Switching power" is what the flip counts say the workload adds, not a measurement.

| Workload | Active cores | Switching power | Result |
|---|---|---|---|
| random normal | 1,024 | 27.2 W | **90 °C in 19, 20, 20, 26 s** (4 runs) |
| random uniform | 1,024 | 25.5 W | 22 s |
| random mantissa | 1,024 | 24.5 W | 24 s |
| A ones, B random | 1,024 | 22.1 W | 29 s |
| random normal | 768 | 20.4 W | 35 s |
| random sign ±1 | 1,024 | 15.4 W | 53 s |
| random normal | 512 | 13.6 W | 84 s |
| π everywhere | 1,024 | 10.7 W | 104 s |
| **ones** | 1,024 | 10.7 W | **107, 162, 167 s** (3 runs) |
| random normal, 50% zeroed | 1,024 | 9.7 W | 107 s |
| random normal | 384 | 10.2 W | 119 s |
| random normal | 256 | 6.8 W | 276 s, 315 s |
| ones | 512 | 5.4 W | 473 s; a second run survived 602 s at 88 °C |
| random normal, 75% zeroed | 1,024 | 5.0 W | **never** — 87 °C after 10 min, still rising |
| checkerboard | 1,024 | 4.2 W | **never** — 87 °C after 10 min |
| random normal | 128 | 3.4 W | **never** — holds 81–82 °C for 10 min |
| ones | 256 | 2.7 W | **never** — die cools to 77 °C |
| **zeros** | 1,024 | 1.9 W | **never** — die cools to 76–78 °C |

The last two runs of the session (a second checkerboard run and random uniform on 512 cores) are left out of
this table: the card's cooling changed partway through the first of them, so their times are not comparable
with the rest. See the caveat on E12 in [03-experiments.md](03-experiments.md).

Three things fall out of this table:

- **Fewer cores buy much more time than the flips they remove**, because leakage feeds back: three quarters of
  the cores (20.4 W) lasts 35 s instead of 19–26, half (13.6 W) 84 s, three eighths (10.2 W) 119 s, a quarter
  (6.8 W) 276–315 s, and an eighth (3.4 W) never reaches 90 °C. What sets the time is the switching power, not where
  it comes from (next point).
- **Equal flip power gives equal heating regardless of where the flips come from.** Ones on all 1,024 cores
  (10.7 W, almost entirely register clocking) and random data on 384 cores (10.2 W, mostly data toggles) reach
  90 °C in 107–167 s and 119 s. The die does not care which transistors moved.
- **The same workload does not always take the same time.** Ones needed 107 s after a hot predecessor and
  162–167 s after a ten-minute zeros run. Every run starts at the same *reading*, but the heatsink behind it
  does not start in the same state, and over minutes that matters. This is the single largest source of
  scatter in the long runs, and it is why the model needs a state estimate rather than just a start temperature.

## The flip budget: about 3 W sustained

Solving the model's heat line for its steady state gives, for each sustained switching power, the temperature
the die would settle at — and the temperature above which it runs away instead. **The two meet at +3.1 W of
switching, with the die at 82 °C**, in 21 September's room (the fitted 22.8 °C intercept); on a warmer day the
budget is smaller, 0.3–0.7 W under 22 September's conditions. Beyond it there is no equilibrium on this card's
cooling, only a time to 90 °C.

The long runs agree: 2.7 W cooled, 3.4 W held 81–82 °C for ten minutes, 4.2 W crept to 87 °C and was still
rising at the end.

In flips, 3.1 W is roughly **10¹⁵ clocked register bits per second**, or a full-load random-data matmul run
**11% of the time**.

> The 1.47 °C/W behind this is **this card in this desktop chassis**, which idles at 62–80 °C. In server
> airflow the budget would be larger. The flip energies and the leakage belong to the chip design, up to a
> per-card scale of about 8% ([11-thermal-model.md](11-thermal-model.md)); the thermal resistance does not.

## Pricing a workload before running it

`tools/ettelem/predict_heat.py` wraps the three lines of the model. Give it the operand tiles (or a known
pattern name) and how many minions will run:

```
$ python3 tools/ettelem/make_tiles.py kaleidoscope k.bin
$ python3 tools/ettelem/predict_heat.py --model docs/reports/data/2026-09-21-horace-aifoundry2/model.json --tiles k.bin
flips per op and minion: 4096 of 4,096 multiply-adds valid; 2.47 M register bits clocked;
  74.3 M tree toggles; 13.27 M other toggles; 140 k operand-word toggles
switching power: register clocking 8.8 W, multiplier tree 2.1 W, rest of the unit 12.0 W,
  operand words 2.4 W, state machines 1.9 W; total 27.2 W on 1024 minions
board power at 80 C: 63.1 W (idle 35.9 W)
die temperature from an idle die at 80 C: 10 s: 86.5 C; reaches 90 C after 27 s
to hold 80 C indefinitely the card can shed 3.1 W of switching: run this workload 11% of the time
```

`predict_heat.py` starts from a die that has sat idle at 80 °C. The strict protocol heats to 84 °C and cools to
80, which leaves the heatsink warmer, so under the protocol the same pair reached 90 °C in 19 s, not 27
(`validate_flip_model.py`, which estimates the start state from telemetry, predicted 19.6 s). The accuracy below is
for that start state.

Useful options: `--active N` for fewer minions, `--start`, `--cap`, `--seconds`, `--json`.
The tiles are 2 × 1,024 raw bytes (A then B, 16 rows of 16 fp32), and the same file feeds the card through
`sparsity_host --values file:<path>`, so **the thing you priced is the thing you run**.

Accuracy to expect, from the held-out tests in [11-thermal-model.md](11-thermal-model.md): the time to a cap
within about 10% in the median out to a few minutes, worse near the budget where a watt of error is tens of
seconds, and 3–5 °C too hot at ten minutes (pessimistic: it wrongly had two of the five ten-minute held-out runs
reaching 90 °C).

## Levers, in order of effect

1. **Gate the multiply-adds.** A zero operand word costs nothing at all: 1.9 W for a full-rate matmul against
   27.2 W on random data. Structured sparsity that survives into the tiles (butterfly factors, bands, blocks)
   converts directly into thermal headroom.
2. **Drop precision.** Over idle, an int8 multiply-add costs 0.32 pJ against 6.02 pJ for fp32, and the int8
   unit also does 6.9× more multiply-adds per second (E15).
3. **Use fewer cores.** Power is linear in active minions, with no floor and no cliff, and the time to the cap
   grows much faster than that: a quarter of the chip ran more than ten times as long (276–315 s against 19–26 s),
   and an eighth never reached it.
4. **Duty-cycle.** The budget is about average power, so alternating a hot kernel with idle keeps the die
   stable at the duty cycle `predict_heat.py` prints.
5. **Do not mask by multiplying by zero.** `x · 0` leaves −0.0, which is not the all-zero bit pattern and is
   **not gated**: 46.7 W, like ones. Use a select.

## Operational notes for long runs

- **Cap the temperature in the runner, not by hand.** `run_horace_long.sh` polls the sensor and touches a file
  the host checks between 0.5 s launches (`sparsity_host --stop-file`), so a run ends cleanly at 90 °C, at
  73 W board power, or if telemetry goes stale.
- **Raise the host's device budget.** `sparsity_host` defaults to `--budget 8` seconds and will otherwise stop
  a "ten-minute" run after eight seconds — this silently truncated the first attempt at E12.
- **Allow seven minutes between hot runs.** After a run that hits 90 °C the die needs up to that long to return to
  80 °C, which is why 29 runs took four hours.
- **Watch for the environment changing.** Partway through E12 the card's cooling changed abruptly: under an
  unchanged workload (42.7 W at 84 °C, falling to 35.6 W as it cooled) the die fell from 84 to 72 °C in four
  minutes. Two runs had to be excluded from every fit.

## Related

- [11-thermal-model.md](11-thermal-model.md): the model behind the budget and `predict_heat.py`, and how well it
  predicts on runs it was not fitted to.
- [10-data-dependent-power.md](10-data-dependent-power.md): where the switching power of each pattern comes from.
- [14-card-behaviour.md](14-card-behaviour.md): the measurement protocol and the traps.
- [13-why-low-power.md](13-why-low-power.md): why leakage is the largest item on this card.
