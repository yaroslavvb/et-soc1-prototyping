# E72 data: the same card at 600 MHz, and a flip's price against V² (Q129, Tue 27 Oct 2026, aifoundry2 card 0)

Pre-registration, frozen predictions and the field manual's change record:
[`tools/claims-v3/lq6/`](../../../../tools/claims-v3/lq6/README.md), commit `001811ab`, pushed at
**14:57 PDT before the first card access**; the G0 gates filled and committed as `20c4249f` at 15:06,
before the one write. Request Q129. Card claimed in `#community-lab` at **14:59:27 PDT** (message
`1564760469741510737`).

E60 (20 Oct) tested ½CV² by comparing three *different* cards at their natural operating points, and had
to read the result against a card-to-card scale band of 0.88–0.99 — a 12 % band under a 40 % effect.
E72 runs **the same card, the same operand bytes and the same reducer** at 600 MHz instead of 800 MHz,
so the scale factor is 1 by construction. The clock comes from one governor field: the static TDP level
goes to 0 W, which is aifoundry3's boot policy. **No clock command was sent.**

## Results first

**The pin worked exactly as the source said it would.** 215 of 215 telemetry samples in the smoke pass
and every one of the 125 kept measurement runs sat at **600 MHz, 517.9 mV**, with zero runs dropped by
E60's own clock gate — on a card that had reached 800 MHz under this same load in every previous
experiment. The restore put it back with no reset: the return burst stepped **600 → 700 → 800 MHz**
(98 samples at 800, 2 at 700, 619 mV, 59.7 W) within one 6 s launch.

**The price of a flipped bit follows the voltage, not the clock.** `lq` h2 → h8 secant, board, per
designed flipped B mantissa bit, E60's own estimator:

| | fJ per flipped bit | against |
|---|---:|---|
| E60, this card, **800 MHz**, 0.6174 V | 121.27 ± 0.61 | — |
| **E72, this card, 600 MHz, 0.5179 V** | **79.18 ± 3.09** | registered prediction **85.69**, band 77.12–94.26 → **V1 PASS** |
| *the alternative: if the energy scaled with f too* | *64.27* | *band 57.84–70.70 — the measurement is **4.8 SE** above it* |

The measured ratio is **0.6529** against V²'s **0.7037** and the clock-scaling alternative's **0.5278**.
On the **minion rail**, which no board-leakage correction touches, it is **0.7389–0.7547** — *above* V²
and 40 % away from the alternative.

**Every registered rule, and the one that failed:**

| | what | predicted | measured | verdict |
|---|---|---:|---:|---|
| **V1** | lq h2→h8 secant, board (fJ/bit) | 85.69 [77.12, 94.26] | **79.18 ± 3.09** | **PASS** (and outside the alternative's band) |
| **V2** | the same on the minion rail | 60.50 [51.43, 69.58] | **63.27** | **PASS** |
| **V3** | the watts of `lq_h2` and `lq_h8` | 1.040 / 3.398 W, ±10 % | **0.913 / 3.094 W** | **FAIL**: `lq_h8` is in band (−8.9 %), `lq_h2` is 12.2 % low |
| **V4** | bend = full h ≥ 1 slope / h2→h8 secant | 1.360 [1.160, 1.560] | **1.430** | **PASS** (full ladder 113.22 ± 0.47 fJ against 116.5 predicted) |
| **V5** | lb full slope / lq full slope | 1.113 [0.963, 1.263] | **1.108** | **PASS** (lb 125.45 ± 1.06 fJ against 129.7 predicted) |
| **V6** | turn-on, `lb_h1`/`lq_h1` in watts | 3.291 [1.975, 4.608] | **3.052** | **PASS** |
| **G1** | the pin: 600 MHz in every sample | 100 % | **100 %** (125/125 runs, 215/215 smoke samples) | **PASS on the clock; the governor-log half is UNMEASURED** (below) |
| **G2** | the pinned voltage | 0.519 [0.516, 0.522] V | **0.5179 V** | **PASS** |
| **G3** | the restore and the step back up | 65 W / 65 °C read back, burst ≥ 700 MHz | **65 W / 65 °C; 800 MHz reached** | **PASS** |

**V3 is a real miss and is reported as one.** Both watt predictions came from the straight line through
this card's own 800 MHz `lq_h2` and `lq_h8` scaled by f·V², and both came in low — `lq_h8` by 8.9 %
(inside the band) and `lq_h2` by 12.2 % (outside it). The same ~10 % shortfall is what makes V1 land at
79.18 rather than 85.69 while still inside its band: the board price at 600 MHz is about 7 % below a
pure V² extrapolation of the 800 MHz price. V3 had no SE clause and `lq_h2` is the smallest rung in the
ladder (0.9 W against a 0.41 W residual rms), which is exactly where a ±10 % band is tightest.

## What the leakage slope does to it, and where the result is safe

Each experiment's registered reduction uses `reduce_hl.py --leak auto`, its own within-run fit, and the
two fits differ a lot because an 800 MHz run heats far more inside its window than a 600 MHz one
(0.4420 vs 0.098 W/°C). [`matched/matched.txt`](matched/matched.txt) re-reduces **both** experiments at
five slopes, the only way to compare them honestly:

| leakage slope (W/°C) | E60 @ 800 | E72 @ 600 | board ratio | E60 rail | E72 rail | rail ratio | n (board) | n (rail) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| each one's own `auto` | 121.26 | 79.18 | 0.6529 | 85.62 | 63.27 | 0.7389 | 2.43 | 1.72 |
| 0.000 | 126.44 | 81.07 | 0.6411 | 83.83 | 63.27 | 0.7547 | 2.53 | 1.60 |
| 0.098 (E72's auto) | 125.29 | 79.18 | 0.6320 | 83.83 | 63.27 | 0.7547 | 2.61 | 1.60 |
| **0.2936 (E66, measured on this card)** | 122.99 | 75.42 | 0.6132 | 83.83 | 63.27 | 0.7547 | 2.78 | 1.60 |
| 0.4420 (E60's auto) | 121.26 | 72.56 | 0.5984 | 85.62 | 63.27 | 0.7389 | 2.92 | 1.72 |

`n` is the exponent that reproduces the measured ratio as (V₆₀₀/V₈₀₀)ⁿ. **The registered law is n = 2;
"the energy scaled with the clock as well" is equivalent to n = 3.64.**

- 🛑 **The board number is slope-sensitive and V1 would not pass at every slope.** At E66's measured
  0.2936 W/°C the secant reads 75.42 fJ, 2.2 % below the band floor, and at E60's own 0.4420 it reads
  72.56, 5.9 % below. The registered verdict stands at the registered slope, and the two labelled
  sensitivities are published beside it
  ([`sensitivity-leak-02936.json`](sensitivity-leak-02936.json),
  [`sensitivity-leak-04420.json`](sensitivity-leak-04420.json)).
- **The rail number is not.** The minion-rail difference is a rail reading, so the board-power leakage
  correction never enters it: it is 63.27 fJ at every slope, and the rail ratio moves only between
  0.7389 and 0.7547 (and that only because the two E60 reductions keep slightly different run sets).
- **So the defensible statement is the one that holds everywhere in that table:** the measured exponent
  is **1.60–2.92** depending on rail-or-board and on the leakage slope; **n = 2 is inside that range at
  every combination, and n = 3.64 is outside it at every combination.** A flipped bit's price is a
  switching energy that follows the voltage. It is not a per-cycle overhead, and E60's cross-card
  reading of the same law is confirmed on one card with the card factor removed.

## The second card at 600 MHz (the Levels tab's missing row)

Every 600 MHz row in the chain came from aifoundry3. E72 gives the same measurement on aifoundry2 at
almost the same operating point — 0.5179 V against 0.5218 V, a V² ratio of 0.985 — with the same operand
bytes, and the two cards agree far better than E60's 0.88–0.99 card band:

| | aifoundry2 (E72) | aifoundry3 (E60) | ratio |
|---|---:|---:|---:|
| `lq` full ladder, board | 113.22 ± 0.47 fJ | 116.75 ± 0.61 fJ | **0.970** |
| `lq` full ladder, rail | 85.07 fJ | 87.52 fJ | 0.972 |
| `lb` full ladder, board | 125.45 ± 1.06 fJ | 129.92 ± 0.48 fJ | 0.966 |
| `lb` full ladder, rail | 92.17 fJ | 96.85 fJ | 0.952 |
| turn-on `lq_h1` | 0.593 ± 0.046 W | 0.594 W | 0.998 |
| turn-on `lb_h1` | 1.809 ± 0.042 W | 1.954 W | 0.925 |

Rung by rung the two cards sit within 0.90–1.09 of each other on `lq` and 0.90–0.96 on `lb`. **A
flipped mantissa bit costs 113 ± 0.5 fJ at the board on this card at 600 MHz** (844 fF, 2.7 × 10⁶
electrons), against 117 ± 0.6 fJ on the other card at the same point.

## Two ladders this card had never been able to run

E60's departure D5 kept the rungs above h = 8 and the whole busy ladder off the 800 MHz cards, because
their 800 MHz power passes the governor's 65 W limit. At 600 MHz the same work draws about half that, so
E72 ran the full ladder (board watts over each family's own zero, mean of 5 passes):

| h | 1 | 2 | 3 | 4 | 6 | 8 | 12 | 16 | 23 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lq` (quiet partner, A = 1.0) | 0.593 | 0.913 | 1.238 | 1.549 | 2.141 | 3.094 | 5.245 | 8.117 | 11.834 |
| `lb` (busy partner, A = π) | 1.809 | 2.283 | 2.766 | 3.208 | 3.685 | 4.325 | 7.754 | 9.861 | 14.479 |

- **The ladder is bent, and the bend is the same shape the other card showed.** The h ≥ 1 line is
  0.5197 W/h with a −0.473 W intercept and a 0.411 W residual rms over an 11.24 W span, while the
  h2 → h8 secant is 0.3635 W/h: a bend of **1.430** against aifoundry3's 1.360 (V4 PASS). A single
  flipped-bit price is a local slope, not a constant — which is the same thing E68 found from the other
  direction when a 12-bit mask over-predicted a whole random word ~2×.
- **The busy partner costs 3.05× more for the first bit and only 1.11× more per bit after that**
  (V6 and V5). Turning the multiplier tree on is most of what the first flip buys.
- **New 600 MHz anchors for this card** (board, mean of 5 passes): zeros **27.06 W**, ones **35.16 W**,
  pi **35.26 W**, randn **51.05 W** — all far under the 85 W bound, and `randn`, which E69 could not
  run *sustained* at 800 MHz on this card at its own default settings, runs comfortably at 600.
- **The RTL predictions**, scaled to this card's f and V by E60's own factor (scale 1.0036, i.e. this is
  essentially the predictions' native operating point), read rms **1.79 W** over 14 items with
  measured/predicted **0.811** — against aifoundry3's rms 1.28 W and 0.832 at the same point. The RTL
  still over-predicts the ladder by about a fifth.

## The session

Five passes, 15:02:20 → 15:23:57 PDT, through E60's own `hl/block.sh` with `HL_EXPN=e72`: 24 items a
pass, `anchor_pi` first and last, two unrecorded burn-ins, the rest shuffled per pass, every item on
1,024 minions, 4 s a run, launched at 58 °C after 59 °C, under the card lock with `timeout 10` on every
device process. **125 runs, 125 kept** — zero clock failures, zero voltage failures, zero launch
failures, zero cycles-per-op failures, and no pass set aside. Die 47 → 55 °C on the first pass and
54 → 55 °C on the other four. Highest board reading in any kept window: **51.38 W** (`anchor_randn`, pass 3). Minion voltage over all
125 runs: **517–519 mV**.

Governor: **TDP 65 → 0 W at 15:01:32.038 PDT and 0 → 65 W at 15:24:07.531**, two commands, both rc 0, both read
back (`gov.jsonl`). The software temperature threshold was **never written** and read 65 °C throughout.
The vmin LUT read at gate time holds exactly three minion points — **600, 700, 800 MHz** — so the floor
the pin lands on is 600 and the card can go no lower.

**Card state at handoff.** An independent `ettelem config` after the last run:
`{"tdp_w": 65, "temp_threshold_c": 65, "power_state_name": "low_power", "minion_mhz": 600,
"minion_mv": 519}` — **equal to the originals** read at 14:59:39. Module uptime **1 d 0 h 12 m**, so the
service processor never reset and the restore is a real write, not a reboot's default. Firmware
unchanged: release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions 0.25.1. The kernel log's
`Error Event Detected` count was **234 before and 234 after**: E72 added none (E69 had taken it 6 → 234
with 20 card-minutes of 10 Hz sampling). No AER, no link error, no all-ones read. No flash, PMIC, reset,
driver, PCIe, clock or voltage action at any point. The deadline watchdog logged *"released by the
session, nothing to do"*.

## Departures and residuals, named

- **D1 — G1's governor-log half is UNMEASURED.** The registered rule asked for 600 MHz in every sample
  *and* zero `Power throttle up` lines in the governor's own log while TDP 0 was set. The clock half is
  measured 125/125 and 215/215. The log half is not: `hl/block.sh` does not dump the service
  processor's trace ring, and adding a dump per run was not in the registered protocol, so no governor
  log exists for these passes. It is reported as **unmeasured, not as a pass.** What stands in its place
  is the contrast with the return burst, which stepped to 800 MHz within one launch the moment the
  original TDP was back — the up-branch works, and it simply never fired while the cap was 0.
- **D2 — the ladder has four more rungs than E60 ran.** `build/hl-gen` has gained `lq_h3`, `lq_h6`,
  `lb_h3` and `lb_h6` since E60 (added for E65's work). They were included, which only improves the
  ladder. Byte-identity: **59 of 59 of E60's own operand files are unchanged**; the 60th line of E60's
  `gen.sha256` is `manifest.json`, which differs because the manifest has grown.
- **D3 — one benign kernel line, self-inflicted.** `ET 0000:02:00.0: Mgmt: Tried to open same device
  multiple times` at host uptime 85,783 s (≈15:03 PDT). That is this session's own `gov_e72.py status`
  poll running while a measurement pass held the card lock and the management node; the poll returned
  `null` and nothing else happened. Recorded rather than dropped; the lesson is not to poll the governor
  during a pass.
- **R1 — the board-vs-rail disagreement is itself a finding, and it is not resolved here.** The rail
  ratio (0.755) is *above* V² and the board ratio (0.598–0.653) is *below* it. Board minus rail is the
  regulators plus whatever the board pays outside the minion rail; the two bracket V² from opposite
  sides, which is consistent with a V²-type switching energy plus a smaller term that scales
  differently, and E72 cannot separate them. The Levels tab's "the rail at the launch temperature and
  the regulators (board → minion rail is only 0.727)" is exactly this gap.
- **R2 — no independent reviewer saw the run**, and **R3 — no independent hardware recovery path exists
  for this fleet** (no PMIC console, probe or programmer route; `/dev/mtd0` on these hosts is host BIOS,
  not card SPI; card resets are forbidden). Both are recorded as limitations, not passes. They are why
  E72 wrote one non-persistent field, never raised the cap, sent no clock command, and armed a watchdog.
- **R4 — the build-identity residual on field manual rule 8** stands as E69 recorded it: the card
  exposes no BL2 git hash through any allowed query, so the source read establishes the behaviour of *a*
  BL2 0.22.0. The BL2 0.20.0 review of the same path agrees, so both plausible builds do.

## What it changes

**It moves no pJ from "unaccounted" to "accounted".** Q128's 3.837 pJ per random fp32 multiply-add
against the board, and 2.39 pJ against the rail, are untouched: E72 measured how an already-measured
price moves with the operating point, not a new term in the ledger. What it changes is the *kind* of
quantity the chain's bit price is:

- Q128 step 6 reads a flipped bit's cost as a switching energy ½CV². That was supported by three
  different cards at three operating points, with a 12 % card band under the test. **E72 makes it a
  same-card measurement**: the card factor is 1, the operand bytes are identical, and the exponent comes
  out 1.60–2.92 against the clock-scaling alternative's 3.64. The identification survives.
- **The Levels tab's "a second card at 600 MHz" is closed**, and closed well: the two cards agree to
  3 % on the board and 3–5 % on the rail at the same operating point, which is tighter than the
  0.88–0.99 band the chain has been carrying since 26 Sep.
- Two rows the tab did not ask for arrive with it: the **full h ≥ 1 ladder** and the **busy-partner
  ladder** now exist on aifoundry2, the card whose idle leakage slope was actually measured (E66). The
  bend — a per-bit price that is a local slope, 1.43× steeper over the whole ladder than over h2 → h8 —
  is the same shape on both cards, which is what E70's saturation ladder is built to explain.
- **A governor method is now proven twice.** E69 moved the cap and the threshold; E72 pinned the clock
  at the floor and put it back. Both restored cleanly with no reset, and E72's source read adds the part
  E69 left as a hazard: there is no firmware latch — `POWER_UP` is always allowed, and aifoundry3's pin
  is a boot-time policy. **aifoundry3's governor can be un-pinned by writing its TDP back**, which no
  experiment has needed yet but which E71 and anything else wanting 800 MHz on that card will.

## Files

[`results.json`](results.json) / [`reduce.txt`](reduce.txt) (E60's reducer, registered slope),
[`runs.csv`](runs.csv) (every run with its gate verdict), [`verdicts.json`](verdicts.json) (the
registered rules scored), `sensitivity-leak-*.json` and `sensitivity-verdicts-*.json` (the labelled
leakage sensitivities), [`matched/`](matched/matched.txt) (both experiments re-reduced at five matched
slopes), [`gov.jsonl`](gov.jsonl) (every governor event with argv, rc and millisecond timestamps),
`aifoundry2/e72/p1`–`p5` (the passes: telemetry at 10 Hz, runs, marks, the operand hashes that ran, the
host manifest), `aifoundry2/e72-smoke/p900` (the pinned smoke: 215/215 samples at 600 MHz) and
`aifoundry2/e72back-smoke/p901` (the return burst: 600 → 700 → 800 MHz at the restored settings).
