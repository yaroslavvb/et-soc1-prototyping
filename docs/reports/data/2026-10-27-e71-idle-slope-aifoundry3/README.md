# E71 — the idle leakage slope of the second card, over the band E65 and E67 ran in (Q129)

## Results

*Six cycles, `p21`–`p26`, Tue 27 Oct 2026 15:05–16:33 PDT on aifoundry3, 600 MHz and 523 mV. Every one
`block.json` `"status":"ok"`; none aborted, none dropped. The card was released in `#community-lab` after this
README was pushed. Reduced with the three commands in "Pre-registered analysis", unchanged.*

**aifoundry3's idle leakage slope over 58–62 °C, the band E65 and E67 launched in, is**

> ### 0.3803 ± 0.0036 W/°C
> median of 6 cycles; mean 0.3804, sd 0.0036, range 0.3749–0.3854; 95 % t ±0.0038, 99 % t ±0.0060;
> 791–856 admissible idle samples per cycle, rms 0.167–0.184 W, span 4 °C.

It replicates E44's three September cycles on this card (0.3799, sd 0.0006) **to 0.0004 W/°C after a month** of
intervening sessions on this card (E60, E63, E65, E67 and E70 among them). And it is **1.30 ×** the 0.2936 W/°C E66 measured on aifoundry2 —
but almost two thirds of that gap is the *band*, not the card:

| | 51–58 °C | 54–58 °C | 58–62 °C | 58–65 °C | 56–66 °C |
|---|---:|---:|---:|---:|---:|
| **aifoundry3, E71, 6 cycles** | 0.3200 ± 0.0038 † | 0.3276 ± 0.0024 | **0.3803 ± 0.0036** | 0.3957 ± 0.0025 | 0.3858 ± 0.0016 |
| aifoundry3, E44, 3 cycles (25–26 Sep) | 0.2943 † | 0.2943 † | 0.3799 | 0.3949 | 0.3808 |
| **aifoundry2, E66's 18 cycles, re-fitted** | **0.2936** (E66's published number) | 0.3053 | **0.3452 ± 0.0056** | 0.3452 | 0.3351 |

Medians of per-cycle fits, W/°C, ± the 95 % t half-width over cycles. † a band the cooling does not fully cover:
E71's floor is 52–53 °C and E44's 54–55 °C, so their "51–58" fits span 5–6 and 3–4 degrees, not 7.

**The slope is a strong function of temperature, on both cards.** Walking up the bands on aifoundry2 alone takes
0.2936 → 0.3053 → 0.3452 W/°C; on aifoundry3, 0.3200 → 0.3276 → 0.3803 → 0.3957. So of the +0.0867 W/°C between
E66's published figure and E71's, **+0.0516 (60 %) is the move from 51–58 °C to 58–62 °C on one card**, and
**+0.0351 (40 %) is the difference between the two cards at a common band.** The practical consequence: E66's
0.2936 W/°C was never the right correction for E65 or E67, even as an approximation for the other card — it is
77 % of the slope their runs actually needed.

**The published idle law gets the band dependence right and the level wrong by under 10 %.** The law in the
power model (`2026-09-21-horace-aifoundry2/model.json`, fitted on aifoundry2: P = 12.6349 + 23.2568·e^((T−80)/36) W)
has a mean slope of **0.3186 W/°C over 51–58 °C and 0.3708 over 58–62** — a +16 % rise across the two bands,
against the +18 % aifoundry2 measures and the +19 % aifoundry3 measures. Against the measurements its level is
8.5 % high for aifoundry2 at 51–58 (0.3186 vs 0.2936), 7.4 % high for aifoundry2 at 58–62 (0.3708 vs 0.3452),
and 2.5 % **low** for aifoundry3 at 58–62 (0.3708 vs 0.3803). So the law is a usable stand-in to within ~10 %
*if it is evaluated over the band in question* — and that, not the card, is what E66's single constant was
missing.

### Scoring

| Rule | Reading | Band | Verdict |
|---|---|---|---|
| **S1** the slope over 58–62 °C | median **0.3803** W/°C, sd **0.0036**, range 0.3749–0.3854 | [0.355, 0.405], sd ≤ 0.010 | **PASS** |
| **S2** identified | 6 cycles kept, all admissible; 99 % half-width **0.0060** | ≥ 5 cycles, ≤ 0.02 | **PASS** |
| **S3a** slope rises with temperature | 58–65 minus 54–58 = **+0.0681** (E71's own cycles); +0.1014 against E44's September 54–58, the registered wording | ≥ +0.04 | **PASS** |
| **S3b** the two cards at a common band | aifoundry2 58–62 median 0.3452 vs 0.3803: **+0.0351** | within ±0.06 | **PASS** |
| **S4** measured, not extrapolated | every cycle cooled to 52–53 °C; 791–856 samples in band | ≤ 58 °C, ≥ 300 samples | **PASS** |
| **S5** the price sensitivity | max abs shift **0.2411 W** (E67 clean, `nrd_b`); max relative **−8.97 %** (`abit_0`); no kept-pass set changed in any of the four reductions | ≤ 0.25 W, ≤ 10 %, unchanged | **PASS** |
| **S6** no verdict of E65 or E67 changes | none flips; D1 moves +0.47 → +0.71 %/°C and stays UNDECIDED (below) | — | **PASS** |

S5 passes on both thresholds but not by much on the relative one (−8.97 % against a registered ≤ 10 %), and the
shifts are **systematic, not noise**: in E65's blocks A and B, 22 of 37 prices move by more than their own
published SE and 11 by more than 2 SE (worst `bit_16`, 3.6 SE). The registration predicted the direction and the
reason, and both hold: an item's measurement window runs warmer than its own constant-operand zero's (mean
+0.32 °C in E65, +0.17 to +1.14 °C in E67), because it burns more power in the same two seconds, so a larger k
subtracts more from the item than from its zero.

### What it does to the two price lists (labelled sensitivities — nothing published is rewritten)

`leak_sensitivity.py` reproduced every published price **exactly** (worst |published − recomputed| = 0.000e+00 W)
at each reduction's own `auto` k before re-pricing, on all four reductions. The files are
`sensitivity-e65-ab.json`, `sensitivity-e65-blockD.json`, `sensitivity-e67.json`, `sensitivity-e67-clean.json`
(and `.txt`, per item). E65's `hl.json`, `hl-blockD.json`, `ladder.json` and E67's `hl.json`, `scored.json`,
`closure.json` are **untouched**.

| | k auto → 0.3803 | mean shift | the group that moves most | the group that moves least |
|---|---|---:|---|---|
| **E65 blocks A+B** (B-side, 32 positions + `bpi`) | 0.1824 → 0.3803 | −0.059 W | bits 0–9, the flat floor: 0.502 → 0.476 W, **−5.2 %** | sign bit 31, −0.7 % |
| **E67 registered** (A-side, 32 positions + grid + closures) | 0.1755 → 0.3803 | −0.070 W | A-side bits 0–9: 0.691 → 0.658 W, **−4.8 %** | `nrd_a`/`nrd_b`, −2.1 % |
| **E65 block D** | 0.0692 → 0.3803 | −0.034 W | `bit_22`, −1.5 % | `lq_h2`, 0.0 % |

Because fJ per flipped bit is the price divided by the designed flips and the measured rate, and neither moves
with k, **the relative shifts above are exactly the shifts in the published energies**. So, in E65's block A
terms: the flat floor of the mantissa price list reads about **103 fJ instead of 109**, `bit_22` **986 fJ instead
of 1008**, the exponent bits **166 instead of 174**, the sign bit 122 instead of 123 — and the span across the 32
positions **widens from 12.2× to 12.8×**, because the cheap positions lose a larger fraction than the dear ones.
The two-regime shape, the position of the knee at bit 10, and the exponent bits sitting above the low mantissa
and below bit 10's climb all survive unchanged.

**E65's block C (the hart ladder, C1–C3) is unaffected at all:** `hb/reduce_ladder.py` de-leaks each rung with
the mean of its two bracketing IDLE phases, not with a slope, so −0.51 ± 0.03 W + 27.1 mW/hart and the zeros line
stand exactly as published.

**E65's D1 is the one published number that moves materially, and it was called out in advance** (S6). D1 is
itself a temperature coefficient, so it is first order in k — and E65 scored it across two reductions that each
took their own `auto` value (**0.1824 W/°C for the 58 °C arm, 0.0692 for the 61 °C arm**). With one measured
slope for both arms (`d1_refit.py`, `d1-sensitivity.json`):

| | 58 °C arm | 61 °C arm | contrast over 3.00 °C | D1 |
|---|---:|---:|---:|---|
| as published (auto per arm) | 4.6272 W | 4.6931 W | +0.0659 W | **+22.0 ± 36.1 mW/°C = +0.47 ± 0.78 %/°C**, 95 % CI −1.05 to +1.99 |
| at E71's slope, one k | 4.5242 W | 4.6215 W | +0.0973 W | **+32.4 ± 39.6 mW/°C = +0.71 ± 0.87 %/°C**, 95 % CI −0.99 to +2.41 |

The verdict does not change — **CONSISTENT, UNDECIDED**: the registered band +0.3 to +0.5 %/°C still sits inside
the interval, and so does zero. But the point estimate moves half way toward the ~1.9 %/°C that E65's own
within-pass warming suggested, which strengthens E65's reading that 3 °C of gated leverage cannot separate this
drift from nothing and that a 10 °C ladder of setpoints is what would.

**E67's closure (the ~2× over-prediction of a random word) is essentially untouched**, because both sides of the
ratio move together: the A-side price list −4.3 %, its measured `nrd_a` step −2.1 %, so measured/predicted goes
0.433 → 0.443; on the B side 0.499 → 0.509. E70 settled that over-count as shared wires rather than interaction,
and E71's slope leaves that conclusion where it was.

### What it changes in Q128's chain, and what it does not

**It moves no pJ from "unaccounted" to "accounted".** Q128's waterfall rests on E38's registered random-MAC
means (5.783 pJ board, 4.337 pJ rail over idle, 3 cards), not on E65's or E67's per-position prices, and E38 is
untouched by this slope. What E71 changes is the **price list's own calibration**, two levels down the chain:

- The **single-bit price list that the bottom-up ledger is compared against** is 2–5 % cheaper than published,
  with the cheap positions cheapest: the measured flat floor is ~103 fJ, so the measured/predicted comparisons
  that use it tighten by a few per cent in the direction of the open-netlist figure, not away from it.
- The **registered 0.294 W/°C sensitivity E66 offered for aifoundry3's runs should not be used**: at E65/E67's
  band this card is 0.3803, and 0.294 is 77 % of it. Any further reduction of an aifoundry3 run corrected to a
  launch reading should use 0.3803 ± 0.0036 (58–62 °C) or 0.3957 (58–65 °C) and say which.
- **Q128 §5 item 3 closes for the second card.** Both cards' idle slopes are now measured on their own
  coolings: aifoundry2 0.2936 (51–58 °C) / 0.3452 (58–62 °C), aifoundry3 0.3200 (52–58 °C) / 0.3803 (58–62 °C).
  The 1.508 W/°C the registered estimator used is 4–5 × every one of them.
- **A new caution for the Levels tab:** a leakage slope is not a card constant. Over 51–65 °C it rises about
  0.009 W/°C per °C of die temperature on aifoundry2 and 0.011 on aifoundry3, so a correction quoted without its
  band is ambiguous at the 20–30 % level — **larger than the 10 % card-to-card difference it is usually invoked
  for, and larger than the error of simply evaluating the published idle law over the right band.**

### Departures from the registration

- **None in rule, band, code or command.** The two harness changes (the 420 s cooling through E66's
  `IDLE_COOL_S`, departure D1 for the logged-in users) were registered before the first launch and are described
  in Method.
- **The heater reached 82–84 °C, not the registered 90 °C target**, stopping on the 150-burst cap in all six
  cycles, where E44's September cycles reached 88–90 °C in 344–409 s. Registered method either way (the cap *is*
  the rule), and it costs nothing: the band of interest is 58–62 °C and every cycle swept it with 791–856
  samples. It does mean the cooling started ~6 °C lower and ran faster — each cycle reached 52–53 °C within its
  420 s where September needed 878 s to reach 54–55 — so E71's own 51–58 °C fit spans 5–6 degrees, not 7, and is
  marked † above.
- **Six cycles, not more.** The driver's deadline stopped it after `p26`; the registered minimum was 5.

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
| `passes/` | per kept pass: `cycle.json`, `block.json`, `marks.jsonl`, `heat.jsonl`, `launches.jsonl`, `check.json`,
  `code.sha256` (the 10 Hz telemetry stays on the box: ~1.3 MB gzipped per pass). Each `login` mark's `users` field —
  the other lab logins `who` showed during the cooling — is replaced by their count, as this repository is public |
| `d1_refit.py`, `d1-sensitivity.json` | E65's D1 re-fitted with one measured slope for both arms (it reproduces the published pair first) |
| `e71.log` | the driver's log |
