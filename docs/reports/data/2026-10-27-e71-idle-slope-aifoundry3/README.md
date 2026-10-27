# E71 — the idle leakage slope of the second card, over the band E65 and E67 ran in (Q129)

*Pre-registered Tue 27 Oct 2026 (week 44), 15:3x PDT on aifoundry3, **before the first E71 launch**. Any change
after this commit goes in the Amendments section at the end, dated, before the data it touches. Request Q129,
experiment E71; Q128 §5 item 3.*

## Why this pass

Every V3-HL price on aifoundry3 — all of E65's 32 B-side bit positions, all of E67's 32 A-side ones, the
interaction grid, the two random-word closures — is a board-power difference corrected to its launch reading with
**one leakage slope for the card**:

    p80 = p_raw − k · (t_win − t_launch)

E66 measured that slope on **aifoundry2**: 0.2936 W/°C over 51–58 °C, the median of 18 overnight cooling cycles.
**On aifoundry3 it has never been measured.** E65 and E67 both used `reduce_hl.py --leak auto`, which fits k from
the within-run drift of runs whose reading rises at least 1 °C (21 Sep's method): 0.182 W/°C for E65's blocks A
and B, 0.069 for its block D, 0.175 for E67's registered reduction and 0.168 for its clean one. Those are
estimates from a few seconds of a running kernel, and they are what every published price on this card rests on.

Two further reasons this card, not only this slope, is worth the card time:

- **The band is not E66's.** E65 and E67 launched every admissible run at **58.0 °C** and their measurement
  windows ran **58.0–62.4 °C** (median 59.8). E66's number is fitted over **51–58 °C** on a card whose governor
  holds the die near 51 °C at idle. A leakage term that grows exponentially with temperature has a different
  local slope in the two bands, so E66's figure is not transferable to E65/E67's correction even if the two
  cards were identical.
- **aifoundry3 can reach the whole band, and quickly.** Its clock is pinned at 600 MHz by a boot-time service
  (TDP 0; left exactly as it is — E71 moves no governor setting, reads none and sets none), and its heater
  reaches **88–90 °C**, where aifoundry2's governor holds its die at ~70 °C. E44's three September cycles on
  this card cooled 88 → 54–55 °C in 900 s and spent 128–167 s per cycle inside 58–62 °C.

## 🛑 What is already known: this is a replication test, not a blind one

E44 ran three short IDLE cycles on this card on 25–26 Sep 2026 (`idle/p1`, `p2`, `p3`; all three `block.json`
`"status":"ok"`). They are admissible under E66's own rule and E66's `idle_slope.py` fits them unchanged. Before
writing this registration, that fit was run — so the predictions below are **informed by three cycles of the same
card with the same harness**, and must be read as a test that six fresh cycles reproduce a month-old reading, not
as a blind prediction:

| pass | 58–62 °C | 56–62 °C | 58–65 °C | 56–66 °C | the lowest band it reached | floor |
|---|---:|---:|---:|---:|---:|---:|
| p1 (25 Sep) | **0.3799** | 0.3687 | 0.3949 | 0.3824 | 0.3132 (54–58) | 55 °C |
| p2 (25 Sep) | **0.3789** | 0.3596 | 0.3951 | 0.3800 | 0.2889 (54–58) | 55 °C |
| p3 (26 Sep) | **0.3800** | 0.3593 | 0.3944 | 0.3808 | 0.2943 (54–58) | 54 °C |
| median | **0.3799** | 0.3596 | 0.3949 | 0.3808 | 0.2943 | |

All in W/°C, one straight-line fit per cycle, rms 0.11–0.15 W, 1,285–1,668 kept samples in 58–62 °C.

Two things in that table set up E71's real question. The three cycles agree to **±0.0006 W/°C** in 58–62 °C — so
if six fresh cycles land anywhere near, the between-cycle spread is not where this measurement's uncertainty
lives. And the slope **rises steeply with temperature on this card**: 0.29 near the floor, 0.38 at 58–62 °C,
0.395 over 58–65. That is the shape an exponential leakage law has, and it means the gap between E66's 0.2936 and
this card's 0.38 may be **band, not card** — which is the comparison E71 is built to make, by fitting
aifoundry2's own E66 passes over 58–62 °C with the same tool.

## Method

`tools/claims-v3/idle/block.sh <pass>`, E66's harness, passes **21–29** (the IDLE-LONG range 11–49; p1–p3 are
E44's September cycles and p11–p30 are aifoundry2's, so these numbers collide with nothing). Per pass: 2 s
random-data fp32 fma bursts on 1,024 minions, back to back under `hold10`, until the minion-shire reading reaches
the card's registered **90 °C** target or 150 bursts or 900 s; then **`IDLE_COOL_S=420` s with no launch**,
`ettelem` at 10 Hz — board power, the three rails, clock, on-die voltage and temperature. The block takes the
card lock for the pass, polls every 10 s for another user's device process or a rise in the `et_soc1` use count
and aborts the cycle if it sees one, and releases the lock between passes. About 14 minutes per pass; the driver
is `tools/claims-v3/idle/run_e71.sh`, which starts a pass only while the clock leaves room for it to finish.

**Two changes to the harness, both default-preserving; aifoundry2's E66 passes would run exactly as they did.**

- **The cooling is 420 s, not aifoundry3's registered 2,700 s**, through the `IDLE_COOL_S` knob E66's amendment
  A3 added. E44's coolings reach 58 °C at +295 to +352 s from `cool_start` and 57 °C at +346 to +426 s; every
  second of the 58–62 °C band falls in the first 250 s. 420 s therefore collects the whole band with margin and
  spends none of the card's time at the floor. Its cost is that **51–58 °C is not reached** — the fit there is
  reported from E44's 900 s September cycles instead, and named as September data wherever it is used.
- **Departure D1, the one `hl/block.sh` already carries:** on aifoundry3 a user who is only *logged in* does not
  block the cycle (three other users keep idle tmux logins on this box, so `lib.sh`'s `who`-based test would
  refuse every pass); another user on **this card** does, read from `sudo -n /usr/local/sbin/et-holders`, failing
  closed when it is unreadable. Every device-level guard is untouched: `ours_running`, the `et_soc1` use count,
  `scan_procs` during the heat and the cooling, the card lock in `block_begin`, and the `login` mark that records
  a login appearing mid-cooling.

**What E71 does not touch.** No governor set or read, no `DM_CMD_SET_*`, no clock change, no card reset, no
firmware, no driver, no PCIe action. The card stays at the 600 MHz its boot policy pins it to, which is also the
clock E65 and E67 ran at.

## Pre-registered analysis

```bash
python3 tools/claims-v3/idle/idle_slope.py --data build/claims-v3/aifoundry3/idle \
        --passes <the kept passes> --bands 58-62,56-62,58-65,56-66,54-58,51-58 \
        --json docs/reports/data/2026-10-27-e71-idle-slope-aifoundry3/slopes.json
```

E66's `idle_slope.py`, with four options E71 adds that change no filter and no fit (`--data`, `--passes`,
`--bands`, `--json`; with none of them the tool prints exactly what it printed for E66). **E66's identification
rules, carried over unchanged:**

1. **Rule F** (`reduce.py` rule F / `flip_thermal_model.py` step 2a): a sample is admissible only if it is at
   least 20 s after `cool_start` — which is the last heater burst's end, so this subsumes the 4.5 s no-launch
   rule — and `mhz.minion == 600`. Board power is `board_w`; the die reading is `temp_c.minshire[0]`.
2. **A band is fitted only with ≥ 50 admissible samples and ≥ 3 distinct whole degrees in it**, else it is
   reported as "too few" and scored UNDECIDED, never fitted.
3. **One straight-line fit per cycle** (`np.polyfit` degree 1, board watts on die degrees). The **cycle is the
   unit of replication**: the headline is the median of the per-cycle slopes, reported with the mean, the sd and
   the range, exactly as E66 reported 0.2936 (median of 18; mean 0.2935, sd 0.0012, range 0.2917–0.2961).
4. **A pass whose `block.json` is not `ok`** — an intrusion, three failed heater bursts in a row, a sampler
   failure, a failed `--check-pass` — is dropped and named in the results. It is never re-registered.
5. Intervals over cycles are two-sided **t** intervals (95 % headline, 99 % for the identification test), on the
   between-cycle scatter.

**And the sensitivity, which is what the slope is for.** `tools/claims-v3/idle/leak_sensitivity.py` re-prices a
published V3-HL list at a different k from its own committed `runs.csv` and `manifest.json`:
`d price = −(k_new − k_old) · mean_over_passes(t_win(item) − t_win(zero))`, with `reduce_hl.py`'s pass set-aside
rule (`anchor_pi` drift above 0.3 W in p80) recomputed at each k, since that rule is the only place k can change
which passes are kept. The tool refuses to report anything unless it first **reproduces the published prices
exactly at the published k** (`--ref hl.json`; checked to 1e-6 W). Run for E65 blocks A+B, E65 block D, E67
registered and E67 clean. **The result is a labelled sensitivity beside each experiment's registered scoring. No
`verdicts.json`, `hl.json`, `scored.json` or published table of E65 or E67 is rewritten by E71.**

## Predictions, frozen with this commit

- **S1 — the slope over 58–62 °C, the band E65 and E67 ran in.** The median per-cycle slope lies in
  **[0.355, 0.405] W/°C** (p1–p3's 0.3799 ± 0.025), and the between-cycle **sd is ≤ 0.010 W/°C**. A median
  outside that band means a month, a different ambient and ~200 intervening card sessions moved this card's idle
  draw, and is reported as a failure to replicate, not as a new number.
- **S2 — it is identified.** At least **5** cycles are kept, every one of them admissible in 58–62 °C under rule
  2 above, and the **99 % t half-width over cycles is ≤ 0.02 W/°C**. If fewer than 5 cycles are kept, S1 is
  reported with its interval and scored UNDECIDED.
- **S3 — the slope rises with temperature, and that is most of the gap to E66.** Two parts, scored separately:
  (a) within this card, slope(58–65 °C) − slope(54–58 °C, E44's September cycles) ≥ **+0.04 W/°C**; (b) across
  the cards, aifoundry2's 18 E66 passes re-fitted over **58–62 °C** with this same tool land within
  **±0.06 W/°C** of E71's 58–62 median. If (b) fails, the two cards differ in leakage for real at a common band,
  and that — not the band — is the headline.
- **S4 — the band is measured, not extrapolated.** Every kept cycle reaches **≤ 58 °C** within its 420 s
  cooling, and has **≥ 300 admissible samples** in 58–62 °C. A cycle that does not reach 58 °C is kept for the
  warmer bands and named; if more than one does not, the 420 s cooling was mis-sized and that is the finding.
- **S5 — what it does to E65's and E67's price lists.** Moving k from each reduction's own `auto` value to E71's
  measured slope: **no kept-pass set changes**; **every price moves downward**; the **largest absolute shift is
  ≤ 0.25 W** and the **largest relative shift is ≤ 10 %**. Predicted at p1–p3's 0.3796 W/°C, already computed
  and disclosed here (`predicted-sensitivity-*.json`):

  | reduction | k (auto) | Δk | mean shift | max abs shift | largest relative shift | kept passes |
  |---|---:|---:|---:|---:|---:|---|
  | E65 blocks A+B | 0.1824 | +0.1972 | −0.058 W | 0.172 W (`bpi_22`) | −7.4 % (`bit_27`) | unchanged |
  | E65 block D | 0.0692 | +0.3104 | −0.034 W | 0.071 W (`bit_22`) | −1.5 % (`bit_22`) | unchanged |
  | E67 registered | 0.1755 | +0.2041 | −0.069 W | 0.233 W (`nrd_b`) | −4.2 % (`ix_a8`) | unchanged |

  The shift is downward on every item for one structural reason: a flipping item's measurement window runs
  **warmer** than its own constant-operand zero's (mean +0.32 °C in E65, +0.3 to +1.1 °C in E67), because it
  burns more power in the same 2 s, so a larger k takes more off the item than off its zero.
- **S6 — no verdict of E65 or E67 changes.** The shape of both price lists survives: the two-regime B-side
  (a flat low-mantissa floor, a monotone climb from bit 10, the exponent bits between), E65's C1/C3 hart-ladder
  verdicts, E67's P1–P8 as published. **One number is predicted to move materially and is called out in advance:**
  E65's **D1**, the switching drift with temperature (+0.47 ± 0.78 %/°C), is itself a temperature coefficient
  fitted on p80 against the launch reading, so it is first-order in k — it is re-fitted at the measured slope and
  reported as a labelled sensitivity. If any *other* published verdict flips, E71 says so in its results and does
  not quietly carry it.

## Decision rules

Each prediction is scored **PASS / FAIL / UNDECIDED** against its own stated band, in the results section of this
README. UNDECIDED where an interval straddles a band edge, where fewer than 3 cycles are kept, or where a band
was not admissible under rule 2. A failure is reported as a failure: a median outside S1's band is a failed
replication, and a sensitivity larger than S5's thresholds is a material correction to E65 and E67, reported as
such, with the affected tables named.

## Files

| File | What |
|---|---|
| `slopes.json`, `slopes.txt` | `idle_slope.py` over E71's kept passes: per cycle, per band, the fit and the per-degree dwell |
| `sep-p1p3.json` | the same tool over E44's three September cycles (the prior above, and the 51–58 °C band E71's 420 s cooling cannot reach) |
| `aifoundry2-58-62.json` | aifoundry2's 18 E66 passes re-fitted over 58–62 °C: S3(b), the card-to-card comparison at a common band |
| `predicted-sensitivity-*.json` | S5's predicted shifts at p1–p3's slope, frozen with this registration |
| `sensitivity-*.json` | the same at the measured slope, after the run — labelled sensitivities, beside E65's and E67's registered scoring |
| `passes/` | per kept pass: `cycle.json`, `block.json`, `marks.jsonl`, `heat.jsonl`, `launches.jsonl`, `check.json`, `code.sha256` (the 10 Hz telemetry stays on the box: ~1.7 MB gzipped per pass) |
| `e71.log` | the driver's log |
