# V3-LQ6 — E72: the same card at 600 MHz, and whether a flip's price follows V² or the clock

*Pre-registered Tue 27 Oct 2026 (week 44) **before the first card access**. Request Q129; the Horace
project. Card **aifoundry2 card 0**. Any change after this commit goes in the Amendments section at the
end, dated, before the data it touches.*

## The question, and why one card answers it better than three

E60 (20 Oct) priced a flipped operand bit on three cards at their natural operating points — aifoundry3
pinned at 600 MHz / 0.522 V by its boot policy, aifoundry2 and aifoundry1 free-running to 800 MHz at
0.618 V and 0.604 V — and read the ratio of per-flip energies against V². Its own decision rule said
what the alternative would look like: *"a ratio near 1.33 × 1.40 (≈ 1.87) would mean the energy per flip
scaled with f too, i.e. it was not a flip."* The ratio came out at 1.41 against 1.40 predicted, which
supports ½CV² — **but across cards**, and E60 had to read it against a card-to-card scale band of
0.88–0.99 measured on 26 Sep. That band is 12 % wide; the effect being tested is 40 %.

E72 removes the card. One card, one operand set, one harness, one night: aifoundry2 card 0 at **800 MHz**
(E60's own rows, already published) against aifoundry2 card 0 at **600 MHz** (this experiment). Nothing
differs but the operating point, so the scale factor is exactly 1 by construction.

It also closes a second thing. The Horace Hub's Levels tab lists **"a second card at 600 MHz"** as
missing: every 600 MHz row in the chain comes from aifoundry3, one card, whose idle leakage slope was
never measured. E72 makes the 600 MHz rung a two-card measurement, on the card whose leakage slope *was*
measured (E66, 0.2936 W/°C).

And it buys a ladder this card has never been able to run. E60's departure D5 kept the rungs above
h = 8 and the whole busy ladder `lb` off the 800 MHz cards, because their 800 MHz power passes the
governor's 65 W limit. At 600 MHz the same work draws about 53 % of that, so **the full lq ladder
(h = 1…23) and the full lb ladder run on this card for the first time.**

## How the clock is set — and it is not a clock command

🛑 `DM_CMD_SET_FREQUENCY` is forbidden in this workflow and is never sent. The clock is a *consequence*
of one governor field: the static TDP level goes to **0 W**, which is exactly aifoundry3's boot policy.
From the source of the running build (BL2 **0.22.0**, et-platform `836a4ab600e93c3059bb58c898edbc37744cd8d0`,
`services/thermal_pwr_mgmt.c:866-928`, `check_power_throttle_conditions`):

| branch | condition | gate |
|---|---|---|
| thermal down | `temperature_updated && T > sw_threshold` | `f > f_min` |
| power down | `pwr_updated && avg_soc_pwr_mW > tdp_level_mW` | `f > f_min` |
| power up | `pwr_updated && avg_soc_pwr_mW < tdp_level_mW` | `f < f_max` |

`avg_soc_pwr_mW` is an unsigned mW average and `tdp_level_mW` is 0, so at TDP 0 the **down** branch is
true under any load and the **up** branch is unreachable. The down branch is itself gated on
`f > f_min`, where `f_min = g_soc_power_reg.vmin_lut_limits.mnn_frequency_min_limit`. The card walks to
the LUT floor and stays there. No clock is commanded; the governor is simply given a target it can only
approach from above.

**Two corrections to E69's hazard note, both from the source.** (1) E69 wrote that *"the power-down
loop's exit needs averaged board power under 1.05 × TDP"*. In this build the macros
`UPPER_POWER_THRESHOLD_GUARDBAND` / `LOWER_POWER_THRESHOLD_GUARDBAND` (lines 212–223) are **defined and
never used** — the comparison is a bare `>` and `<` against `tdp_level_mW`. The conclusion is the same
and the mechanism is simpler. (2) aifoundry3's governor is **not** latched by a firmware state machine.
`POWER_UP` is "always allowed" from any throttle state (line 2269), so the governor pass after the
original TDP is written back sees `avg_pwr < 65000` and `f < f_max` and steps up. What latches
aifoundry3 is a boot-time **policy** that keeps re-writing 0 — the field manual's own note that its
*"600 MHz / NoC 400 MHz / TDP 0 policy is volatile; a stale success marker stopped the guard from
reapplying after reset"* describes a guard script, not a trapped loop. E69's restore of a 45 W cap to
65 W, and the stepping it then observed, is the empirical half of the same statement.

**The gate that stands behind the argument anyway:** `gov_e72.py gates` reads the vmin LUT
(`DM_CMD_GET_VMIN_LUT`, a pure `memcpy` out of the service processor's RAM copy of the persistent
config — `driver/flashfs.c:2073` — no SPI, no programming-mode change) and **refuses to run unless the
floor is 600 MHz**; and G1 below gates every single telemetry sample of every launch on 600 MHz, so a
pin that landed anywhere else is caught by the data and not by an argument.

One field is written: `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26). **The software temperature threshold is
not touched at all** — E69 moved it, E72 moves one knob — and a threshold that does not read 65 °C at
gate time is a NO-GO. Gates, evidence and the restore plan are in
[`CHANGE-RECORD.md`](CHANGE-RECORD.md), filled from Roman's field manual template.

## Protocol

E60's own harness, unchanged: `hl/block.sh` → `run_hl.py`, one pass = one replicate, 4 s runs, the
launch-temperature approach (preheat to 59 °C, launch at ≤ 58 °C), `anchor_pi` first and last in every
pass with two unrecorded burn-ins, the rest shuffled on the pass number, the card lock held for the
pass, `timeout 10` on every device process, the 10 Hz sampler for the whole pass, abort at 78 °C.

- **Items** (20): `anchor_pi, anchor_ones, anchor_zeros, anchor_randn, lq_h{0,1,2,4,8,12,16,23},
  lb_h{0,1,2,4,8,12,16,23}`.
- **Operands:** `build/hl-gen`, **the same files E60 ran**, checked byte for byte against E60's published
  `gen.sha256` by `run_e72.sh setup` (the check `run_e67.sh setup` does, pointed at E60's hashes).
- **Passes:** 5 planned, 3 the minimum for a verdict (the unit of replication is the pass, as E60
  registered). Cut order if time runs short: drop `lb_h16`, then `lb_h12`, then `anchor_zeros`, then
  passes — never below 3.
- **Reduction:** `reduce_e72.py`, which is `reduce_hl.py` with `gov_free=False` forced (the window on a
  pinned card starts at t₀+1 s; there is no 800 MHz ramp to wait for) and nothing else changed. The clock
  is inferred from the data by E60's own code and every run is gated against it.
- **Safety bound:** the pass stops at a 78 °C reading (lib.sh's own limit); board power is logged every
  100 ms and the session aborts and restores if any sample passes **85 W** (E69's bound, not raised).
- **The governor cannot outlive the session:** `gov_e72.py pin` arms a detached deadline watchdog that
  writes the original 65 W back after 75 min unless the session has released it.

## Frozen predictions ([`predictions.json`](predictions.json), generated by `predict_e72.py`)

All from data already in the repo. V₈₀₀ = **0.617411 V** (E60's measured mean on this card),
V₆₀₀ = **0.519 V** expected (E69 read `minion_mv: 519` at the 600 MHz point on this card twice today).
(0.519/0.617411)² = **0.70662**; × 600/800 = **0.52997**.

| | what | predicted | band | PASS if |
|---|---|---:|---|---|
| **V1** | lq h2→h8 secant, board, fJ per designed flipped bit | **85.69** | 77.1 – 94.3 | inside the band **and** outside the alternative's own ±10 % |
| | *the alternative (energy scaled with f too)* | *64.27* | *57.8 – 70.7* | *this is the hypothesis V1 refutes* |
| **V2** | the same on the minion rail | 60.50 | 51.4 – 69.6 | inside |
| **V3** | watts: `lq_h2` 1.040 W, `lq_h8` 3.398 W over `lq_h0` | — | ±10 % | both inside (h1, h4 reported only) |
| **V4** | bend: (full h ≥ 1 slope)/(h2→h8 secant) | 1.360 | 1.160 – 1.560 | inside — and so the full-ladder price 116.5 fJ (99.1 – 134.0) |
| **V5** | `lb` full slope / `lq` full slope | 1.113 | 0.963 – 1.263 | inside — and so `lb` 129.7 fJ (110.3 – 149.2) |
| **V6** | turn-on: `lb_h1`/`lq_h1` in watts | 3.291 | 1.975 – 4.607 | inside |
| **G1** | the pin | 600 MHz in **100 %** of samples; **zero** `Power throttle up` lines while TDP 0 is set | — | exactly that |
| **G2** | the pinned voltage | 0.519 V | 0.516 – 0.522 | inside |
| **G3** | the restore | TDP 65 W and threshold 65 °C read back; a post-restore burst reaching ≥ 700 MHz with ≥ 1 `Power throttle up` | — | exactly that |

V1's reference is **this card's own** 121.272 ± 0.613 fJ at 800 MHz (E60, 9 passes, 160 runs kept,
`--leak auto` 0.4420 W/°C there). V4's and V5's shapes are E60's **aifoundry3** numbers — 116.746 fJ
full ladder against an 85.86 fJ h2→h8 secant, and `lb` 129.918 fJ — and they are registered as *ratios*
precisely because a shape travels across cards better than a number of watts.

**Leakage slopes.** The price is a difference between two rungs measured in the same pass, so the slope
enters only through the small difference in within-run heating between them. The verdict is scored at the
registered `--leak auto`, exactly as E60 and E68 registered it, and the same reduction is reported at
**E66's measured 0.2936 W/°C** and at **E60's own 0.4420 W/°C on this card** as labelled sensitivities.

## Decision rules

- **V1 is the result.** If the measured secant is inside its band and outside the alternative's, the
  statement *"the price of a flipped bit follows V², not the clock"* is a measured, same-card result. If
  it lands inside the alternative's band instead, that is reported as **the registered hypothesis
  refuted**, not softened.
- **If both bands contain the measurement** (they do not overlap at ±10 %, but a wide measurement could
  reach both), the cell is **inconclusive** and is reported as such.
- **G1 is a gate, not a result.** A single telemetry sample at any clock other than 600 MHz voids the
  pass through E60's own clock gate; if the pin itself fails — the floor is not 600 MHz, or the clock
  moves — the session restores, reports **blocked**, and claims nothing about V².
- **A failed restore** stops everything: keep the card claim, write it up, alert with
  `notify.py --unblock`. No reset, no retry, per field manual rule 11.

## Files

`predict_e72.py` → `predictions.json` (the frozen predictions, derived from E60's published data);
`gov_e72.py` (gates, the one write, the deadline watchdog, restore, the back check); `run_e72.sh`
(setup / pin / smoke / go / restore / back); `reduce_e72.py` (E60's reducer with the pinned-card window);
[`CHANGE-RECORD.md`](CHANGE-RECORD.md) (the field manual's gates, PASS / FAIL / UNKNOWN per item).

## Amendments

*(none yet; anything after the pre-registration commit goes here, dated, before the data it touches)*
