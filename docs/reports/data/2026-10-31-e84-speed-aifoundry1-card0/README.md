# E84 — the speed of each kind of number on aifoundry1's card 0, under its own governor (Q130)

*Sat 31 Oct 2026 (week 44), aifoundry1 card 0. Pre-registration [`tools/claims-v3/kspeed/e84/`](../../../../tools/claims-v3/kspeed/e84/README.md)
(commit `337b03b2`, pushed before the claim). Amendment A1 (`1713a3f9`) was written after the read-only identity reads
and before any launch. The session ran 15:43:32–16:06:38 PDT: 35 of 35 runs, exit 0, 23.1 card-minutes. There was no
safety stop and no other-user hit. Nothing was set on the card.*

## Results first

1. **All four registered rules pass:**
   - **E84-P1**: zeros at least as fast as random data in every format, burst and sustained;
   - **E84-P2**: int8 the least throttled;
   - **E84-P3**: the limiting test matches the frozen label for 9 of 11 kinds in the burst and 10 of 11 sustained;
   - **E84-S1** (secondary).

   Source: [`results.json`](results.json) `.rules`, [`reduce.txt`](reduce.txt).
2. **"Zeros run faster" belongs to the numbers.** On a second card, with a different board, PMIC firmware and cooling
   under the same governor build, zeros are at least as fast as random data in every format. The sustained speed
   ratios for fp16 and int8 agree with aifoundry2's to within 2%:

   | format | zeros ÷ random speed, card 0 | aifoundry2 |
   |---|---|---|
   | fp16 | 1.27× | 1.30× (E80) |
   | int8 | 1.008× | 1.009× (E80) |
3. **How much faster in fp32, and why, belongs to the card.** On card 0, fp32 random data draws 73 W at 800 MHz,
   enough to trip the **PMIC's 75 W over-power alarm** (post hoc, below). That alarm is a third limit, beside the
   governor's two (the 65 W power arm and the 65 °C thermal arm). It drops the clock to 300 MHz about once a second.
   - Random fp32 runs 1.41× slower than zeros in the burst and **1.67× slower sustained**. aifoundry2 gives 1.13× and
     1.33× (zeros from E64, random from E80), where only the TDP and thermal arms act.
   - In absolute terms random fp32 is slower here: 8.73 TFLOPS against aifoundry2's 10.69 in the burst, 7.30 against
     9.27 sustained.
4. **The cooler card removes the penalty for all-ones data.** fp32 and fp16 ones run at full clock sustained on card 0:
   793.5 and 795.6 MHz, die at most 66 and 65 °C, limit none. On the hotter aifoundry2 they throttled thermally to 737.9
   and 737.1 MHz on 23 Oct (E64). E80's two fp16 ones runs today read 792.9 and 770.3, one of them thermal.
   The penalty for random data stays on both cards: fp16 randn goes thermal at 632 MHz here and at 610 on aifoundry2.
5. **Card 0 runs the same governor as aifoundry2** (amendment A1). It reads release 1.4.0, BL1 and BL2 0.22.0, PMIC
   1.6.1 and minions 0.25.1, not the 1.4.1 / 0.21.2 of the card table. Its configuration read 65 W TDP and a 65 °C
   threshold at the start and the end ([`ident/ident-154200.out`](ident/ident-154200.out),
   [`ident/final-160652.out`](ident/final-160652.out)).

## The cells (aifoundry1 card 0; aifoundry2 beside, from E80 unless marked E64)

Burst: one 6 s process from a die reading ≤ 55 °C, two passes. Sustained: nine back-to-back 8 s processes, from a die
reading ≤ 57 °C; the last 40 s of the work. All values are from [`results.json`](results.json) `.cells.<kind>`:

- MHz is the sampled clock;
- TFLOPS and TOPS are the kernel's own operations over its own wall time;
- p800 is the median board W in the first second at 800 MHz, and "over zeros" is p800 minus the type's zeros p800;
- the limit is measured / predicted.

| kind | burst MHz (passes) | burst rate | p800 W | over zeros | burst limit | sustained MHz | sustained rate | sus. board W | sus. die °C | sustained limit | aifoundry2 burst / sustained MHz |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 zeros | 800, 800 | 12.28 TFLOPS | 29.6 | 0 | none / none | 794.3 (2 runs) | 12.18 | 29.5 | 55.6 | none / none | 790.5–793.7 / 800 (E64) |
| fp32 ones | 800, 800 | 12.28 | 44.0 | 14.4 | none / none | 793.5 | 12.16 | 47.1 | 64.7 | none / none | 773.8–795.2 / 737.9 (E64) |
| fp32 randn | 667.4, 611.4 | **8.73** | 73.0 | 43.4 | power, none / power | **548.1** (2 runs) | **7.30** | 45.3 | 62.2 | **unresolved** / thermal | 711.9 / 604.3 |
| fp32 sparse90 | 800, 800 | 12.28 | 30.0 | 0.4 | none / none | 794.8 | 12.19 | 30.6 | 56.0 | none / none | 800 / 800 |
| fp32 bf16trunc | 800, 800 | 12.27 | 61.9 | 32.3 | **none** / power | 667.6 | 10.00 | 48.7 | 65.5 | thermal / thermal | 774.0 / 639.1 |
| fp16 zeros | 800, 800 | 24.55 TFLOPS | 29.5 | 0 | none / none | 794.1 | 24.35 | 29.6 | 56.0 | none / none | 800 / 789.8 |
| fp16 ones | 800, 800 | 24.55 | 43.5 | 14.0 | none / none | 795.6 | 24.40 | 46.7 | 63.9 | none / none | 800 / 781.6 |
| fp16 randn | 778.4, 773.5 | 23.53 | 68.6 | 39.1 | power / power | 631.9 | 19.11 | 49.0 | 65.8 | thermal / thermal | 730.6 / 609.5 |
| int8 zeros | 800, 800 | 84.30 TOPS | 29.8 | 0 | none / none | 794.6 | 83.71 | 30.9 | 56.9 | none / none | 800 / 800 |
| int8 full | 800, 800 | 84.30 | 42.2 | 12.4 | none / none | 788.7 | 83.08 | 44.4 | 62.8 | none / none | 800 / 793.4 |
| int8 neg_ones | 800, 800 | 84.30 | 33.3 | 3.4 | none / none | 794.1 | 83.65 | 34.3 | 58.9 | none / none | 777.5 / 796.9 |

**Card 0's own idle level** (`.runs[].idle_w`, `idle_mhz`): 19.0–20.6 W at 600 MHz between runs, die 49–57 °C at the
gates. **At 800 MHz card 0 draws 5–10 W less than aifoundry2** for the same tiles: fp32 zeros 29.6 against 35.0 W
(E64), fp32 randn 73.0 against 82.7, fp16 randn 68.6 against 76.1, int8 full 42.2 against 48.9.

The sustained clock includes the climb at each 8 s process start (600 → 700 → 800 MHz in 0.5–1.4 s), 2.6–6.2% of
the samples on the kinds that reach 800 (`.cells.<kind>.sus_ramp_share`). It costs 0.6–1.5% of the rate: compare
fp32 zeros, 12.18 TFLOPS sustained against 12.28 in the burst.

## The rules, as registered

| rule | verdict | the numbers |
|---|---|---|
| E84-P1 zeros ≥ random − 10 MHz, 6 comparisons | **PASS** | zeros − random: fp32 +160.6 burst, +246.2 sustained; fp16 +24.0, +162.2; int8 0, +5.9 MHz |
| E84-P2 int8 the least throttled (± 5 MHz) | **PASS** | deficit to 800 MHz, burst: fp32 160.6, fp16 24.0, int8 0; sustained: 251.9, 168.1, 11.3 MHz |
| E84-P3 limit right for ≥ 9 of 11 per block | **PASS** | burst 9 of 11: missed fp32 randn (power, none) and bf16trunc (none, none; predicted power). Sustained 10 of 11: missed fp32 randn (unresolved twice; predicted thermal) |
| E84-S1 format means of the sustained deficit (secondary) | **PASS** | fp32 80.3, fp16 59.5, int8 7.5 MHz |

**The misses, said plainly.**

- **bf16trunc's burst.** The prediction carried E80's *predicted* aifoundry2 p800 (79.9 W) at a factor 0.907 to
  68–75 W. Card 0 measured 61.9 W. E80's own measurement on aifoundry2 was 69.5 W, so the carried number was 10 W too
  high at its source. With the PMIC's running average peaking at 63.2–63.8 W (`.runs[].burst_avg_max_w`), under the
  65 W TDP, a 6 s burst never meets the power arm and runs at 800 MHz.
- **fp32 random data in both blocks.** Its limit is neither of the two the rules name:
  - burst pass 2 logged no throttle-down line at all, so it reads `none`;
  - the sustained runs read `unresolved`: 270–275 of ~340 samples are below 800 MHz with neither a thermal nor a
    power label, the die at most 63–64 °C and the PMIC average 41.3 W.

  The trace ring names the cause, read post hoc below. P3's pass therefore rests on the other kinds, and the table
  marks fp32 randn's cells.
- **The ratios of item 3 use the kernel's own rate.** The sampled clock understates the fp32 random-data loss. The
  kernel's cycles over wall time read 0.593 and 0.544 GHz in the two bursts, against sampled means of 667 and 611
  MHz. For the kinds that hold 800 MHz the two agree (0.799 GHz). Item 3 and the blog points therefore use the kernel's
  rates. P1 and P2 use the sampled clock, as registered, and pass either way.

## Post hoc, labelled, never a verdict: the PMIC's over-power alarm

[`posthoc/pmic.json`](posthoc/pmic.json) and [`posthoc/pmic.txt`](posthoc/pmic.txt), from
[`tools/claims-v3/kspeed/e84/posthoc_pmic_e84.py`](../../../../tools/claims-v3/kspeed/e84/posthoc_pmic_e84.py),
written after the data.

**Where it appears.** In all four fp32 random-data runs, and in no other run of the 35 or of the smoke, the ring holds
lines like

`Pmic_Controller_Handle_Pmic_Error_Event: (step 250 mW) power = 75750 mW, alarm set point = 75000 mW`

with the power reading 75.00–76.25 W. Each alarm is followed by a power-status record in throttle state 3
(POWER_SAFE) and `New OP: Freq 300 MNN 400`.

**The cycle.** The governor's power arm then climbs back one point a pass, 300 → 600 → 700 → 800 MHz, because its
running average (44–48 W) is far under the 65 W TDP. At 800 MHz the alarm trips again within 0.1–0.6 s. The cycle
is a median 1.106 s from one safe state to the next.

**What it costs.**

- Over a whole sustained run the work samples sit 31–32% at 300 MHz, 32–34% at 600, 25% at 700 and only 10–11% at
  800.
- The kernel's own effective clock is 0.475–0.479 GHz, against a sampled 551 MHz. The gap is not explained here; one
  candidate is a stall at each of the cycle's four operating-point changes.

**On aifoundry2 it never fired.** None of aifoundry2's committed rings, E80's 59 and E64's, holds such a line, though
its fp32 random data read 80–88 W at 800 MHz. Whether its PMIC firmware (1.5.0) has another set point, or does not
raise the alarm, was not checked.

**A check on the reading.** Earlier alarm lines stay in the 4 KB ring for a few runs, so the raw dumps of seven later
runs still contain them. The ring reader keeps only entries newer than the previous dump (`sptrace_full.since`). Every
one of those leftover lines is older than the previous dump's newest entry.

## Registered against what happened

- **Firmware (A1).** Not 1.4.1 / 0.21.2 as on record but 1.4.0 / BL2 0.22.0 / PMIC 1.6.1, read after the claim and
  before any launch. No frozen item changed.
- **Card time.** 23.1 card-minutes for the session against a 60-minute cap: the cooling gates passed at once, with
  0.1–1.9 s holds. With the identity reads (15:42:00), the smoke (15:42:50–15:43:12) and the closing reads (16:06:52),
  card 0 was in use 15:42–16:07 PDT.
- **Etiquette.**
  - The claim was posted at 15:41:50 PDT, after the pre-registration was pushed: `#community-lab` message
    `1566220684185829469`, *"using aifoundry1 card 0 for 1.5 h, until ~17:15 PDT"*. That same post was edited at
    16:08 to append " — released", and read back.
  - Card 1 was free throughout: E82 released it at 15:03.
  - The other user's two idle login sessions were counted and never named (`s1/marks.jsonl`, `logins`). No device
    process, holder or CI job of anyone else appeared.
- **Interim looks.** During the session only the runner's status lines were read (run counts and gate readings). The
  reduction ran after the session ended.

**Corrections of the pre-registration's description (not of any frozen prediction or rule).**

1. *"Between processes the clock drops to a 300 MHz / 398 mV point"*: not so in this session. Card 0 idled at
   600 MHz / 519 mV between runs: every gate reading and both configuration reads say so. The 300 MHz point appeared
   only after a PMIC alarm. In E60's heater probe the 300 MHz samples sat next to 74–75 W board readings, so they
   were most likely the same safe state. That is a post-hoc reading of committed telemetry; E60's rings were not read
   for it.
2. The sustained "ramp" is therefore the climb from the 600 MHz idle point, not from 300.

## What this changes for the blog material and the hub

- **The kinds table gains a second card.** These are the speed cells for 11 kinds on aifoundry1's card 0: burst and
  sustained MHz, TFLOPS/TOPS, p800 and p800 over zeros, sustained board W and die, and the limiting test.
- **Levels/Status: a third limit.** The PMIC's 75 W over-power alarm, with a 300 MHz safe state, limits fp32 random
  data on card 0. It sits beside the governor's 65 W power arm and 65 °C thermal arm. A blog sentence that says "two
  limits" should say "two, and on a card that runs closer to 75 W at 800 MHz, a third".
- **Records.** Card 0's firmware on record is stale: it is 1.4.0 / BL2 0.22.0 / PMIC 1.6.1 / minions 0.25.1. It idles
  at 600 MHz in this session, not 300 (`14-card-behaviour.md`'s card table and its "Firmware 1.4.1 idles at
  300 MHz").

## Files

| path | what |
|---|---|
| `s1/` | the session: `session.json`, `kspeed.json`, `e84.json` (frozen hashes, freeze commit `337b03b2`), `runs.jsonl`, `launches.jsonl.gz`, `tel/*.jsonl.gz` (10 Hz sampler), `sp/*.bin` (the trace ring after each run), `queries.jsonl`, `marks.jsonl`, `run.log`, `manifest.txt`, `end.json` |
| `smoke/` | the three 2 s smoke runs (not analysed) |
| `ident/` | the read-only identity reads (configuration, uptime, firmware revisions) and the closing reads |
| `logs/` | the runner's stage logs on the box |
| `results.json`, `reduce.txt`, `reduce.log` | the registered reduction (`reduce_e84.py`, with E80's `results.json` beside) |
| `posthoc/pmic.json`, `posthoc/pmic.txt` | the post-hoc PMIC alarm view |

Reproduce on the Intel: `bash tools/claims-v3/kspeed/e84/collect_e84.sh` (it copies the raw session from aifoundry1 and
reduces it); `python3 tools/claims-v3/kspeed/e84/posthoc_pmic_e84.py <this dir>/s1 --out <this dir>/posthoc/pmic.json`.
