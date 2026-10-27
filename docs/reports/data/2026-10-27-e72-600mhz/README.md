# E72 data: the same card at 600 MHz, and a flip's price against V² (Q129, Tue 27 Oct 2026, aifoundry2 card 0)

Pre-registration, frozen predictions and the field manual's change record:
[`tools/claims-v3/lq6/`](../../../../tools/claims-v3/lq6/README.md), commit `001811ab`, committed and
pushed at **14:58:51 PDT, before the first card access** (14:59:39); the G0 gates filled and committed
as `20c4249f` at **15:01:22**, ten seconds before the one write at 15:01:32.038. Request Q129. Card
claimed in `#community-lab` at **14:59:27 PDT** (message `1564760469741510737`).

> **Corrected at the desk on 27 Oct 2026, 16:0x–16:5x PDT**, after an independent review returned
> *holds-with-fixes* on eleven faults. No card was touched, nothing was re-measured and no measured
> number moved: every figure still comes from the same 125 kept runs of the same `runs.csv`. What
> changed is which of them may be quoted and how — **G3 is now PARTIAL, not PASS**; the V² test is
> re-run at matched leakage slopes on a fixed pass set and **fails there at three of four slopes**;
> `n = 2` is no longer claimed to be inside every reduction; and **"quote the rail, it is slope-free"
> is withdrawn**. The full list is [Corrections](#corrections-after-the-first-write-up-27-oct-desk-fix-pass)
> at the foot of this file.

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

*(E60's 800 MHz figure is quoted two ways in this file, 0.008 % apart: **121.27 ± 0.61** is its
per-pass designed-bit slope, which only h0/h2/h8 were run for on this card and which the frozen
prediction was built from; **121.26** is the same data through the h2 → h8 secant formula, the estimator
the matched tables apply identically to both experiments.)*

The measured ratio is **0.6529 ± 0.0257** against V²'s **0.7037** and the clock-scaling alternative's
**0.5278**. On the **minion rail** — which the leakage correction never touches, because
`reduce_hl.py` corrects the board only — it is **0.7547 ± 0.0423**, *above* V² and 40 % away from the
alternative.

🛑 **The registered V1 PASS holds at the registered reduction, and that reduction uses a different
leakage slope on each side of the ratio** (E60 at its own auto fit 0.4420 W/°C, E72 at its own 0.098).
Re-run the same ±10 % test with the prediction moved to the *same* slope as the measurement — the only
matched form of the test — and it fails at three of the four matched slopes
([`matched/matched-fixed.txt`](matched/matched-fixed.txt) § B):

| leakage slope, both sides | E60 @ 800 | V² prediction | ±10 % band | E72 @ 600 | |
|---|---:|---:|---|---:|---|
| *the registered row: each side at its own auto* | *121.26 ± 0.61* | *85.33* | *76.80–93.86* | *79.18 ± 3.09* | ***PASS** (−7.2 %)* |
| 0.000 | 126.44 ± 0.97 | 88.98 | 80.08–97.87 | 81.07 ± 3.57 | **PASS** (−8.9 %) |
| 0.098 (E72's own) | 125.29 ± 0.89 | 88.16 | 79.35–96.98 | 79.18 ± 3.09 | **FAIL** (−10.2 %) |
| **0.2936 (E66, measured on this card)** | 122.99 ± 0.76 | 86.55 | 77.89–95.20 | 75.42 ± 2.53 | **FAIL** (−12.9 %) |
| 0.4420 (E60's own) | 121.25 ± 0.69 | 85.32 | 76.79–93.85 | 72.56 ± 2.64 | **FAIL** (−15.0 %) |

The registered verdict stands as registered — a pre-registered rule is scored as it was written, and the
frozen prediction is E60's number at E60's own slope. But **the matched-slope re-test is the honest
reading of "the same card at two operating points", and it says the 600 MHz board price is about 10 %
below a pure V² extrapolation, not inside ±10 % of it.** That is the same ~10 % shortfall V3 reports.

**Every registered rule, and the one that failed:**

| | what | predicted | measured | verdict |
|---|---|---:|---:|---|
| **V1** | lq h2→h8 secant, board (fJ/bit) | 85.69 [77.12, 94.26] | **79.18 ± 3.09** | **PASS** (and outside the alternative's band) |
| **V2** | the same on the minion rail | 60.50 [51.43, 69.58] | **63.27** | **PASS** |
| **V3** | the watts of `lq_h2` and `lq_h8` | 1.040 / 3.398 W, ±10 % | **0.913 / 3.094 W** | **FAIL**: `lq_h8` is in band (−8.9 %), `lq_h2` is 12.2 % low |
| **V4** | bend = full h ≥ 1 slope / h2→h8 secant | 1.360 [1.160, 1.560] | **1.430** | **PASS** (full ladder 113.22 ± 0.47 fJ against 116.5 predicted) |
| **V5** | lb full slope / lq full slope | 1.113 [0.963, 1.263] | **1.108** | **PASS** (lb 125.45 ± 1.06 fJ against 129.7 predicted) |
| **V6** | turn-on, `lb_h1`/`lq_h1` in watts | 3.291 [1.975, 4.608] | **3.052** | **PASS** |
| **G1** | the pin: 600 MHz in every sample **and zero `Power throttle up` lines in the governor's log** | 100 % and zero | **100 %** (125/125 runs, 215/215 smoke samples); the log half never measured | **PARTIAL: PASS on the clock, UNMEASURED on the log** |
| **G2** | the pinned voltage | 0.519 [0.516, 0.522] V | **0.5179 V** | **PASS** |
| **G3** | the restore, the step back up **and at least one `Power throttle up` event** | 65 W / 65 °C read back, burst ≥ 700 MHz, ≥ 1 throttle-up event | **65 W / 65 °C read back twice; 600 → 700 → 800 MHz**; the event half never measured | **PARTIAL: PASS on the read-back and the clock step, UNMEASURED on the event** |

**So the count is: six of the nine registered rules pass in full (V1, V2, V4, V5, V6, G2), one fails as
registered (V3), and two are PARTIAL (G1, G3) because the same missing evidence — nobody dumped the
service processor's trace ring — leaves half of each unmeasured, and UNMEASURED is not PASS.** G3's
throttle-up clause had been dropped from this table and the rule written up as a plain PASS; both are
now scored half by half, from the committed telemetry and `gov.jsonl`, by
[`score_e72.py`](../../../../tools/claims-v3/lq6/score_e72.py) rather than in prose
([`verdicts.json`](verdicts.json) `.rules.G1`, `.rules.G3`, `.summary`).

**V3 is a real miss and is reported as one.** Both watt predictions came from the straight line through
this card's own 800 MHz `lq_h2` and `lq_h8` scaled by f·V², and both came in low — `lq_h8` by 8.9 %
(inside the band) and `lq_h2` by 12.2 % (outside it). The same ~10 % shortfall is what makes V1 land at
79.18 rather than 85.69 while still inside its band: the board price at 600 MHz is about 7 % below a
pure V² extrapolation of the 800 MHz price at the registered reduction, and 10–15 % below it once both
sides are reduced at the same leakage slope (the matched table above). V3 had no SE clause and `lq_h2` is the smallest rung in the
ladder (0.9 W against a 0.41 W residual rms), which is exactly where a ±10 % band is tightest.

## What the leakage slope does to it, and where the result is safe

Each experiment's registered reduction uses `reduce_hl.py --leak auto`, its own within-run fit, and the
two fits differ a lot because an 800 MHz run heats far more inside its window than a 600 MHz one
(0.4420 vs 0.098 W/°C). [`matched/matched-fixed.txt`](matched/matched-fixed.txt) re-reduces **both**
experiments at matched slopes, **on a fixed pass set**, with intervals:

| leakage slope (W/°C) | E60 @ 800 | E72 @ 600 | board ratio | rail ratio | n (board) | n (rail) |
|---|---:|---:|---:|---:|---:|---:|
| *each one's own `auto` — the registered row, **not matched*** | *121.26 ± 0.61* | *79.18 ± 3.09* | *0.6529 ± 0.0257* | *0.7389 ± 0.0402* | *2.43 ± 0.22* | *1.72 ± 0.31* |
| 0.000 | 126.44 ± 0.97 | 81.07 ± 3.57 | 0.6411 ± 0.0286 | 0.7547 ± 0.0423 | 2.53 ± 0.25 | 1.60 ± 0.32 |
| 0.098 (E72's auto) | 125.29 ± 0.89 | 79.18 ± 3.09 | 0.6320 ± 0.0250 | 0.7547 ± 0.0423 | 2.61 ± 0.23 | 1.60 ± 0.32 |
| **0.2936 (E66, measured on this card)** | 122.99 ± 0.76 | 75.42 ± 2.53 | 0.6132 ± 0.0210 | 0.7547 ± 0.0423 | 2.78 ± 0.19 | 1.60 ± 0.32 |
| 0.4420 (E60's auto, this card at 800) | 121.25 ± 0.69 | 72.56 ± 2.64 | 0.5985 ± 0.0220 | 0.7547 ± 0.0423 | 2.92 ± 0.21 | 1.60 ± 0.32 |

`n` is the exponent that reproduces the measured ratio as (V₆₀₀/V₈₀₀)ⁿ, and every ± is the per-pass SE
(the pass is the unit of replication, as E60 registered) propagated through the ratio into `n`. **The
registered law is n = 2; "the energy scaled with the clock as well" is equivalent to n = 3.637.**

- 🛑 **These rows are matched in sample; the first write-up's were not.** `reduce_hl.py` sets a pass
  aside when its `anchor_pi` drifts more than 0.3 W, and that drift is measured on the
  *leakage-corrected* power — so the slope decides which passes are kept. E60 keeps **9** passes at
  0.4420 and **8** at 0.000 / 0.098 / 0.2936, which is why the first table's E60 rail column took
  exactly two values and part of every row-to-row move there was a change of sample. Every matched row
  above is reduced on the **intersection — passes 2, 3, 4, 6, 7, 8, 9, 10, 143 of 180 runs** — so a
  row-to-row move is a slope move and nothing else. E72 keeps all 5 passes and 125/125 runs at every
  slope, so its column never had the problem.
- 🛑 **The board number is slope-sensitive and V1 does not pass at every slope.** At E66's measured
  0.2936 W/°C the secant reads 75.42 fJ, 2.2 % below the *frozen* band floor and 12.9 % below the
  matched-slope prediction; at E60's own 0.4420 it reads 72.56. The labelled sensitivities are published
  beside the registered verdict ([`sensitivity-leak-02936.json`](sensitivity-leak-02936.json),
  [`sensitivity-leak-04420.json`](sensitivity-leak-04420.json); their verdict files are now scored at
  their own slope, which they were not before — they had carried the registered slope's scatter).
- 🛑 **The rail is not slope-free. It is UNCORRECTED, which is a different thing** — and the earlier
  advice to "quote the rail" is **withdrawn**. `reduce_hl.py` applies `p80 = p_raw − k·ΔT` to the board
  only; the rail is a raw mean read over `[lo+1 s, lo+3 s)` against the board's `[lo, lo+2 s)`, because
  the rail telemetry is a 1 s running average — one second later and, on E60, **0.575 °C hotter** than
  the window the board is read in (on E72, 0.028 °C *cooler*: the asymmetry is between the two sides of
  the ratio). Priced at the same slopes the board carries, the rail moves **63.27 → 53.16 fJ (−16 %)**,
  the rail ratio **0.7547 → 0.6906** and `n` (rail) **1.60 → 2.11**
  ([`matched/matched-fixed.txt`](matched/matched-fixed.txt) § D). The rail cannot be corrected with its
  own within-run fit either: that fit reads **5.52 W/°C** on E60 and **1.11** on E72 — a launch
  transient, not leakage. Only the board has an independently measured idle slope to be corrected at
  (E66, 0.2936 W/°C on this card).
- **So the defensible statement is weaker than the first write-up's, in one direction only.** `n = 2` is
  **not** the point estimate of any reduction: the board family gives **2.43–2.92** and the rail family
  **1.60–1.72**, and the two *bracket* 2 from opposite sides rather than each containing it. On the
  board, 2 is inside the 95 % interval only in the registered mixed-slope row (1.9 SE) and outside it in
  every matched row (2.1–4.4 SE); on the rail it is inside everywhere (0.9–1.2 SE). What survives
  untouched is the half that does the work: **the clock-scaling alternative, n = 3.637, is excluded by
  every row on both board and rail, at 3.4 SE or more.** A flipped bit's price is a switching energy
  that follows the voltage far more closely than the clock — but this measurement does not pin the
  exponent to 2, it brackets it between about 1.6 and 2.9.
- **And the whole slope sensitivity rests on a sub-degree reading.** The correction enters the secant
  only as `k·(T_h8 − T_h2)/((32768−8192)·rate)`. That temperature difference, per pass, is **+0.85,
  0.00, +0.80, +0.05, +0.95 °C** — mean **0.53 °C**, and exactly **zero in pass 2** — from a die sensor
  that reports whole degrees. A 10 % swing in the published board price is driven by that, and it is
  also why the five per-pass secants spread **71.9 – 90.0 fJ** around their 79.18 mean.

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
the pin lands on is 600 and the card can go no lower. **That floor was established by hand, not by the
coded gate**: `dev_mngt_service` writes the LUT to a binary file rather than to stdout, so
`gov_e72.py`'s text parse found nothing and wrote `{"event": "vmin_floor", "floor_mhz": null}` into
`gov.jsonl`, then proceeded with an `UNKNOWN` note. The three points, the binary's digest and all three
independent parses of it (the session's, the reviewer's and the correction pass's) are now published in
[`vmin-lut.json`](vmin-lut.json); the gate itself is recorded as **UNKNOWN resolved by hand**, which is
not the same as enforced in code.

**Card state at handoff** ([`handoff-evidence.json`](handoff-evidence.json) says exactly which of these
readings are committed and which were only printed at the time). The committed `back_check` in
`gov.jsonl` at **15:24:31.194** reads `{"tdp_w": 65, "temp_threshold_c": 65, "power_state_name":
"low_power", "minion_mhz": 600, "minion_mv": 519}` — **equal to the originals** read at 14:59:39. A
further `ettelem config` at 15:24:48 and the module uptime of **1 d 0 h 12 m** (so the service processor
never reset, and the restore is a real write rather than a reboot's default) were read at the time but
**were not retained as files**; an independent reviewer repeated the read under the card lock at
**15:46:51** and got the same five fields. Firmware unchanged: release 1.4.0, BL1/BL2 0.22.0, PMIC
1.5.0, minions 0.25.1. The kernel log's `Error Event Detected` count was **234 before and 234 after**
(E69 had taken it 6 → 234 with 20 card-minutes of 10 Hz sampling): those counts were read on the host
and reported, **not committed**, and two later read-only host checks — the reviewer's and the correction
pass's at **16:06:35** — both still read 234 with the last such line at host uptime 84,342 s ≈ 14:38
PDT, *before* E72 began. No AER, no link error, no all-ones read. No flash, PMIC, reset, driver, PCIe,
clock or voltage action at any point. The deadline watchdog logged *"released by the session, nothing to
do"*.

## Departures and residuals, named

- **D1 — G1's governor-log half is UNMEASURED.** The registered rule asked for 600 MHz in every sample
  *and* zero `Power throttle up` lines in the governor's own log while TDP 0 was set. The clock half is
  measured 125/125 and 215/215. The log half is not: `hl/block.sh` does not dump the service
  processor's trace ring, and adding a dump per run was not in the registered protocol, so no governor
  log exists for these passes. It is reported as **unmeasured, not as a pass.** What stands in its place
  is the contrast with the return burst, which stepped to 800 MHz within one launch the moment the
  original TDP was back — the up-branch works, and it simply never fired while the cap was 0.
- **D1b — G3 has the same hole, and it was missed in the first write-up.** The registered G3 is *"65 W,
  65 °C, and a post-restore burst that reaches ≥ 700 MHz **with at least one `Power throttle up`
  event**"*. The event clause needs the same trace-ring dump D1 lacks, so it is UNMEASURED too, and G3
  is **PARTIAL**, not the PASS the first table and the change record recorded. Both are now scored half
  by half in [`verdicts.json`](verdicts.json). **The lesson for the next governor move is one line of
  harness: dump the service processor's trace ring per run, as the knob harness (E69) does — the two
  rules that went half-unmeasured are exactly the two that needed it.**
- **D2 — the ladder has four more rungs than E60 ran.** `build/hl-gen` has gained `lq_h3`, `lq_h6`,
  `lb_h3` and `lb_h6` since E60 (added for E65's work). They were included, which only improves the
  ladder. Byte-identity: **59 of 59 of E60's own operand files are unchanged**; the 60th line of E60's
  `gen.sha256` is `manifest.json`, which differs because the manifest has grown.
- **D3 — one benign kernel line, self-inflicted.** `ET 0000:02:00.0: Mgmt: Tried to open same device
  multiple times` at host uptime 85,783 s (≈15:03 PDT). That is this session's own `gov_e72.py status`
  poll running while a measurement pass held the card lock and the management node; the poll returned
  `null` and nothing else happened. Recorded rather than dropped; the lesson is not to poll the governor
  during a pass.
- **R1 — the board-vs-rail disagreement is itself a finding, it is not resolved here, and part of it is
  the estimator.** The rail ratio (0.755) is *above* V² and the board ratio (0.598–0.653) is *below* it.
  Board minus rail is the regulators plus whatever the board pays outside the minion rail, which is the
  Levels tab's "the rail at the launch temperature and the regulators (board → minion rail is only
  0.727)". **But the two sides are not reduced the same way**: the board is leakage-corrected and the
  rail is not, and they are read over windows a second apart. Price the rail at the same slopes the
  board carries and its ratio falls from 0.755 to 0.691 while the board's falls from 0.653 to 0.598 —
  the gap narrows but does not close, so part of the bracket is physics and part is the estimator, and
  E72 separates neither.
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
  same-card measurement**: the card factor is 1 by construction and the operand bytes are identical.
  What that measurement supports, stated at its real strength: the exponent is **1.60–2.92** across
  rail-or-board and leakage slope, which **excludes the clock-scaling alternative (3.637) everywhere at
  3.4 SE or more** but **does not pin the law to 2** — no reduction has 2 as its point estimate, and on
  the board 2 sits outside the 95 % interval at every matched slope. ½CV² remains the best-supported
  reading of the bit price and the per-cycle-overhead reading is refuted; the exponent itself is
  bracketed, not measured to be 2.
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

## Corrections after the first write-up (27 Oct, desk fix pass)

An independent adversarial review of E72 ran 15:36–15:55 PDT and returned **holds-with-fixes** on
eleven faults. It re-derived the headline secant to the digit (79.17567 ± 3.08546 fJ), re-read all
12,247 telemetry samples of the five passes at 600 MHz, confirmed the pre-registration ordering, and
**confirmed the restore itself on the card** with its own read-only `ettelem config` at 15:46:51 PDT.
It found nothing fabricated and no safety rule broken: the governor move, the restore and the rule-8
source argument all stand.

This pass fixed what can be fixed at a desk, 16:05–16:5x PDT. **No card was touched, no run repeated and
no measured quantity re-measured**; every number still comes from the same 125 kept runs of the same
`runs.csv`, and the new reduction tool self-tests against every published figure before it computes
anything new. The two host accesses were read-only and opened no device node (a kernel-log count, and a
parse of the LUT file the gate had already written).

**Verdicts that changed:**

- **C1 — G3 is PARTIAL, not PASS.** Its registered text ends *"with at least one `Power throttle up`
  event"*, and that clause had been dropped from the results table while the rule was written up as a
  plain PASS here and in the change record. It needs the governor log that D1 says was never dumped. G1
  and G3 are now both scored **half by half, in code**, from the committed telemetry and `gov.jsonl`
  (`score_e72.py`, which previously scored neither). The count is now **six rules pass in full, one
  fails (V3), two are PARTIAL**, where it had read "seven of eight scorable rules pass".
- **C2 — the V² test re-run at matched slopes fails at three of four.** The registered V1 compares E72's
  secant at E72's leakage slope against a prediction frozen from E60's secant at *E60's*. Moving the
  prediction to the measurement's slope — the only matched form of the test — gives PASS at slope 0 and
  FAIL at 0.098, 0.2936 and 0.4420 (−10.2 %, −12.9 %, −15.0 %). The table is in *The price of a flipped
  bit*, above, and in `matched/matched-fixed.txt` § B. **The registered PASS stands as registered**; it
  now carries the matched-slope re-test beside it. (The frozen band 77.12–94.26 and the matched row's
  76.80–93.86 differ because the frozen prediction was evaluated at the *expected* 0.519 V and at E60's
  per-pass designed-bit slope, while the matched rows use the *measured* 0.51792 V and the h2 → h8
  secant on both sides.)
- **C3 — "n = 2 is inside that range at every combination" is withdrawn.** It was read off point
  estimates. With each row's own per-pass SEs propagated, the board family gives 2.43–2.92 and the rail
  family 1.60–1.72: **no reduction has 2 as its point estimate**, and on the board 2 is inside 95 % only
  in the registered mixed-slope row. The half that survives is the decisive one — the clock-scaling
  alternative n = 3.637 is excluded by every row on both sides at ≥ 3.4 SE.
- **C4 — "the rail is slope-free, quote the rail" is withdrawn.** The rail is not corrected at all and
  is read over a window one second later than the board's; at the same assumed slopes it moves −16 %,
  more than the board's −10 %. Its own within-run fit (5.52 W/°C on E60, 1.11 on E72) is a launch
  transient and cannot be used to correct it, so the reviewer's preferred fix — correct the rail with
  its own fitted slope — is **not available on this data**, and the second fix is taken instead: the
  rail ratio is published as an *uncorrected* quantity from a later window, with its sensitivity to an
  assumed slope ( `matched/matched-fixed.txt` § D).

**Reductions and data that changed:**

- **C5 — the "five matched slopes" are now matched in sample.** `reduce_hl.py` chooses which passes to
  keep using the *leakage-corrected* `anchor_pi` drift, so the slope moved the sample: E60 kept 9 passes
  at 0.4420 and 8 at the three lower slopes. The matched family is now reduced on the intersection
  (passes 2,3,4,6,7,8,9,10; 143 of 180 runs) at every slope. E72's 5 passes / 125 runs were already
  stable at every slope. `matched/matched.txt` and `matched.json` are kept unchanged for the record;
  `matched/matched-fixed.*` supersede them.
- **C6 — every row now carries an interval**, and the sensitivity verdict files
  (`sensitivity-verdicts-*.json`) are scored at **their own slope**: they had reported each slope's
  secant against the *registered* slope's per-pass scatter, because `runs.csv` holds one `p80` column.
  `score_e72.py --leak` fixes that (SE 3.57 / 2.53 / 2.64 fJ at 0.000 / 0.2936 / 0.4420, against the
  registered 3.09).
- **C7 — the ΔT the whole leakage sensitivity rests on is published.** It is +0.85, 0.00, +0.80, +0.05,
  +0.95 °C per pass between the two rungs of the secant, mean 0.53 °C, from a sensor that reports whole
  degrees — with the per-pass secants (71.9–90.0 fJ) beside it.
- **C8 — the vmin-LUT gate is relabelled UNKNOWN-resolved-by-hand.** `gov.jsonl` records
  `floor_mhz: null`, and `gov_e72.py` proceeds on a null floor with an UNKNOWN note; the change record
  had listed the floor under *"bounds enforced in code, not only in prose"* and twice said the gate
  refuses to proceed without it. The substance is right and is now evidenced in
  [`vmin-lut.json`](vmin-lut.json) — the binary's digest and mtime, the three points (600/700/800 MHz)
  and three independent parses, including one made during this correction pass. **`gov.jsonl` itself is
  left exactly as the session wrote it**: a machine log of what a run did is not edited afterwards.
- **C9 — evidence described as committed, which was not.** The kernel-log counts before and after, the
  15:24:48 `ettelem config` and the module uptime were printed at the time and never saved.
  [`handoff-evidence.json`](handoff-evidence.json) now says exactly what is committed (the `back_check`
  event at 15:24:31.194), what was only printed, and what two later independent read-only checks found
  (the count still 234, last event ≈ 14:38 PDT, before E72).
- **C10 — four timestamps corrected against git and `gov.jsonl`.** The change record's "Opened 15:28",
  "GO 15:06" and "Signoff 15:50", and this file's "pushed at 14:57" / "committed at 15:06". Read
  literally, the GO stamp post-dated both the commit that recorded it (15:01:22) and the write it
  authorised (15:01:32.038). **The substantive ordering was and is correct** — pre-registration
  14:58:51 → claim 14:59:27 → first card read 14:59:39 → the one write 15:01:32.038 — and the reviewer
  verified it independently.
- **C11 — the Discord claim.** The release was appended at ~15:32 PDT and read back, but by 15:35:15 the
  message held only its first 83 characters, cut mid-clause, with no release suffix: a concurrent edit
  on the shared browser tab damaged this claim and E69's at the same minute. For about half an hour the
  channel therefore showed an **open** ~1 h claim on aifoundry2 that this experiment had in fact
  released. It was repaired at **16:04:52 PDT** by another agent of this workflow; the message now reads
  *"&lt;ai&gt; using aifoundry2 (about 1 h): the 600 MHz replicate, E72, the static TDP level at 0 —
  released, governor restored (TDP 65 W, read back), data"* with the data link, the `<ai>` tag renders
  literally, and `lab_reservations` reads the reservation as closed at 16:04:52. The first write-up's
  "released at 15:32 PDT … both the post and the edit were read back after sending" was true of the
  moment it was written and false of the channel twenty minutes later. **Lesson: on a shared tab, a
  claim is not released until it is re-read after the other writers have finished — read it back once
  more at the end of the session, not only at the moment of the edit.**

## Files

[`results.json`](results.json) / [`reduce.txt`](reduce.txt) (E60's reducer, registered slope),
[`runs.csv`](runs.csv) (every run with its gate verdict), [`verdicts.json`](verdicts.json) (the
registered rules scored, G1 and G3 half by half), `sensitivity-leak-*.json` and
`sensitivity-verdicts-*.json` (the labelled leakage sensitivities, each scored at its own slope),
[`matched/matched-fixed.txt`](matched/matched-fixed.txt) + [`matched-fixed.json`](matched/matched-fixed.json)
(**the corrected comparison**: both experiments at matched slopes on a fixed pass set, with per-row SEs,
the matched-slope V1 test, the rail study and the ΔT table, from
[`rematch_e72.py`](../../../../tools/claims-v3/lq6/rematch_e72.py), which self-tests against every
published number), `matched/matched.txt` + `matched.json` (the first, sample-unmatched version, kept for
the record), [`vmin-lut.json`](vmin-lut.json) (the LUT's three frequency points and their three parses),
[`handoff-evidence.json`](handoff-evidence.json) (which handoff readings are committed and which were
only printed), [`gov.jsonl`](gov.jsonl) (every governor event with argv, rc and millisecond timestamps),
`aifoundry2/e72/p1`–`p5` (the passes: telemetry at 10 Hz, runs, marks, the operand hashes that ran, the
host manifest), `aifoundry2/e72-smoke/p900` (the pinned smoke: 215/215 samples at 600 MHz) and
`aifoundry2/e72back-smoke/p901` (the return burst: 600 → 700 → 800 MHz at the restored settings).
