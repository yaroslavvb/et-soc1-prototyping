# E84 — the speed of each kind of number on aifoundry1's card 0, under its own governor (Q130)

*Sat 31 Oct 2026 (week 44), aifoundry1 card 0. Pre-registration [`tools/claims-v3/kspeed/e84/`](../../../../tools/claims-v3/kspeed/e84/README.md)
(commit `337b03b2`, pushed before the claim). Amendment A1 (`1713a3f9`) was written after the read-only identity reads
and before any launch. The session ran 15:43:32–16:06:38 PDT: 35 of 35 runs, exit 0, 23.1 card-minutes. There was no
safety stop and no other-user hit. Nothing was set on the card.*

*Corrected after verification the same evening, at the desk with no card touched: see
[Corrections after verification](#corrections-after-verification-sat-31-oct-2026) and
[`corrections-check.txt`](corrections-check.txt). No number in `results.json` or `reduce.txt` changed, and no verdict
changed. The all-ones comparison and the "cooler card" reading of item 4 were wrong and are replaced.*

## Results first

1. **All four registered rules pass:**
   - **E84-P1**: zeros at least as fast as random data in every format, burst and sustained;
   - **E84-P2**: int8 the least throttled;
   - **E84-P3**: the limiting test matches the frozen label for 9 of 11 kinds in the burst and 10 of 11 sustained. The
     pass rests on the eight kinds predicted `none`, right 8 of 8 in both blocks. Of the three kinds predicted to be
     limited, 1 of 3 is right in the burst and 2 of 3 sustained ([`corrections-check.txt`](corrections-check.txt) C10);
   - **E84-S1** (secondary).

   Source: [`results.json`](results.json) `.rules`, [`reduce.txt`](reduce.txt).
2. **"Zeros run faster" belongs to the numbers.** On a second card, with a different board, PMIC firmware and cooling
   under the same governor build, zeros are at least as fast as random data in every format. The sustained speed
   ratios for fp16 and int8 are consistent with aifoundry2's, but each rests on single runs:

   | format | zeros ÷ random speed, sustained, card 0 | aifoundry2, same day (E80) |
   |---|---|---|
   | fp16 | 1.275× (one run each) | 1.297× (one run each) |
   | int8 | 1.008× (one run each) | 1.009× (its two random-data runs give 1.005–1.014×) |

   E80's two int8 runs differ by 0.9%, as much as the int8 effect itself, so the int8 agreement is within noise
   ([`corrections-check.txt`](corrections-check.txt) C4).
3. **How much faster in fp32, and why, belongs to the card.** On card 0, fp32 random data draws 72–75 W on the board at
   800 MHz: p800 is 72.4 and 73.6 W in the two bursts, and single readings reach 74.6 W. The PMIC's own readings reach
   75.00–76.25 W, at or over its **75 W over-power alarm** (post hoc, below). That alarm is a third limit, beside the
   governor's two (the 65 W power arm and the 65 °C thermal arm). It drops the clock to 300 MHz about once a second.
   - Zeros run 1.41× faster than random fp32 in the burst (pass-paired 1.35–1.47×) and **1.67× faster sustained**
     (1.655–1.682× over the two replicate pairs), so random data takes 1.67 times as long.
   - aifoundry2 gives 1.15× and 1.31× the same day, where only the TDP and thermal arms act. That is E83's zeros over
     E80's random data; over E83's own random-data anchor it is 1.14× and 1.29×
     ([`corrections-check.txt`](corrections-check.txt) C2, C4, C7).
   - In absolute terms random fp32 is slower here: 8.73 TFLOPS against aifoundry2's 10.69 in the burst, 7.30 against
     9.27 sustained.
4. **All-ones data run near full clock on both cards. Card 0 gets there by drawing less power, not by cooling better.**
   - **The clocks.** fp32 and fp16 ones held 793.5 and 795.6 MHz sustained on card 0 (one run each, limit none, die
     64.7 and 63.9 °C). aifoundry2's same-day runs held 782.4 MHz (E83: 771.7 thermal, 793.1 none) and 781.6 MHz (E80:
     792.9 none, 770.3 thermal). The 11–14 MHz gap is inside aifoundry2's own run-to-run spread of 21–23 MHz.
   - **The power.** At about the same die temperature, aifoundry2 draws 6.3–6.5 W more board power: 53.3 and 53.2 W
     against card 0's 47.1 and 46.7 W.
   - **The heat path.** Per board watt, card 0's die runs **1.1–1.5 °C hotter**, not cooler. Its die line over its 13
     sustained runs is 41.78 + 0.4753 °C per W and reaches 65.5 °C at 49.9 W; aifoundry2's (E83) reaches it at 53.4 W.
     Card 0's lower draw is what keeps all-ones data under the 65 °C trip.
   - **The stale numbers.** The 737.9 and 737.1 MHz quoted here before are E64's, from 23 Oct, when aifoundry2's heat
     path ran 1.38 °C hotter ([`corrections-check.txt`](corrections-check.txt) C1).

   The penalty for random data stays on both cards: fp16 randn goes thermal at 632 MHz here and at 610 on aifoundry2
   (one run each).
5. **Card 0 runs the same governor as aifoundry2** (amendment A1). It reads release 1.4.0, BL1 and BL2 0.22.0, PMIC
   1.6.1 and minions 0.25.1, not the 1.4.1 / 0.21.2 of the card table. Its configuration read 65 W TDP and a 65 °C
   threshold at the start and the end ([`ident/ident-154200.out`](ident/ident-154200.out),
   [`ident/final-160652.out`](ident/final-160652.out)).

## The cells (aifoundry1 card 0; aifoundry2 beside, from E80 unless marked E83, both run the same day)

Burst: one 6 s process from a die reading ≤ 55 °C, two passes. Sustained: nine back-to-back 8 s processes, from a die
reading ≤ 57 °C; the last 40 s of the work. All values are from [`results.json`](results.json) `.cells.<kind>`:

- MHz is the sampled clock;
- TFLOPS and TOPS are the kernel's own operations over its own wall time;
- p800 is the median board W in the first second at 800 MHz, and "over zeros" is p800 minus the type's zeros p800.
  Both are at 800 MHz and 603–604 mV, so "over zeros" is not E78's or E82's switching power, which is read at
  600 MHz (C11);
- the limit is measured / predicted.

| kind | burst MHz (passes) | burst rate | p800 W | over zeros | burst limit | sustained MHz | sustained rate | sus. board W | sus. die °C | sustained limit | aifoundry2 burst / sustained MHz |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 zeros | 800, 800 | 12.28 TFLOPS | 29.6 | 0 | none / none | 794.3 (2 runs) | 12.18 | 29.5 | 55.6 | none / none | 800 / 789.3 (E83) |
| fp32 ones | 800, 800 | 12.28 | 44.0 | 14.4 | none / none | 793.5 | 12.16 | 47.1 | 64.7 | none / none | 800 / 782.4 (E83) |
| fp32 randn | 667.4, 611.4 | **8.73** | 73.0 | 43.4 | power, none / power | **548.1** (2 runs) | **7.30** | 45.3 | 62.2 | **unresolved** / thermal | 711.9 / 604.3 |
| fp32 sparse90 | 800, 800 | 12.28 | 30.0 | 0.4 | none / none | 794.8 | 12.19 | 30.6 | 56.0 | none / none | 800 / 800 |
| fp32 bf16trunc | 800, 800 | 12.27 | 61.9 | 32.3 | **none** / power | 667.6 | 10.00 | 48.7 | 65.5 | thermal / thermal | 774.0 / 639.1 |
| fp16 zeros | 800, 800 | 24.55 TFLOPS | 29.5 | 0 | none / none | 794.1 | 24.35 | 29.6 | 56.0 | none / none | 800 / 789.8 |
| fp16 ones | 800, 800 | 24.55 | 43.5 | 14.0 | none / none | 795.6 | 24.40 | 46.7 | 63.9 | none / none | 800 / 781.6 |
| fp16 randn | 778.4, 773.5 | 23.53 | 68.6 | 39.1 | power / power | 631.9 | 19.11 | 49.0 | 65.8 | thermal / thermal | 730.6 / 609.5 |
| int8 zeros | 800, 800 | 84.30 TOPS | 29.8 | 0 | none / none | 794.6 | 83.71 | 30.9 | 56.9 | none / none | 800 / 800 |
| int8 full | 800, 800 | 84.30 | 42.2 | 12.4 | none / none | 788.7 | 83.08 | 44.4 | 62.8 | none / none | 800 / 793.4 |
| int8 neg_ones | 800, 800 | 84.30 | 33.3 | 3.4 | none / none | 794.1 | 83.65 | 34.3 | 58.9 | none / none | 777.5 / 796.9 |

**Card 0's own idle level** (`.runs[].idle_w`, `idle_mhz`): 19.0–21.2 W at 600 MHz between runs, die 49–57 °C at the
gates.

**Card 0 draws 4.5–9.8 W less absolute board power than aifoundry2 at 800 MHz** for the same tiles (p800). Absolute
board power is what the governor's power arm sees:

- fp32 zeros 29.6 against 34.1 W (E83);
- fp32 randn 73.0 against 82.7, fp16 randn 68.6 against 76.1, int8 full 42.2 against 48.9 (E80).

About 4.5–5.1 W of the gap is there with zero data: fp32, fp16 and int8 zeros differ by 4.5, 5.1 and 5.0 W. Over each
card's own zeros, the data's switching differs by only 1.1–5.3 W: fp32 randn 43.4 against 48.6 W, fp16 randn 39.1
against 41.5, int8 full 12.4 against 14.1 ([`corrections-check.txt`](corrections-check.txt) C8).

The sustained clock includes the climb at each 8 s process start (600 → 700 → 800 MHz in 0.5–1.4 s), 2.6–6.2% of
the samples on the kinds that reach 800 (`.cells.<kind>.sus_ramp_share`). It costs 0.6–1.5% of the rate: compare
fp32 zeros, 12.18 TFLOPS sustained against 12.28 in the burst.

## The rules, as registered

| rule | verdict | the numbers |
|---|---|---|
| E84-P1 zeros ≥ random − 10 MHz, 6 comparisons | **PASS** | zeros − random: fp32 +160.6 burst, +246.2 sustained; fp16 +24.0, +162.2; int8 0, +5.9 MHz |
| E84-P2 int8 the least throttled (± 5 MHz) | **PASS** | deficit to 800 MHz, burst: fp32 160.6, fp16 24.0, int8 0; sustained: 251.9, 168.1, 11.3 MHz |
| E84-P3 limit right for ≥ 9 of 11 per block | **PASS** | burst 9 of 11: missed fp32 randn (power, none) and bf16trunc (none, none; predicted power). Sustained 10 of 11: missed fp32 randn (unresolved twice; predicted thermal). The three kinds predicted to be limited: 1 of 3 burst, 2 of 3 sustained; the eight predicted none: 8 of 8 in both (C10) |
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

**On aifoundry2 it never fired.** None of aifoundry2's committed trace rings holds such a line or a 300 MHz operating
point: E80's 64 dumps (59 in the session), E64's 58 and E83's 125, all committed before E84's data. None of their
93,276 telemetry readings is at 300 MHz, though fp32 random data there read 80–88 W at 800 MHz
([`corrections-check.txt`](corrections-check.txt) C12). Whether its PMIC firmware (1.5.0) has another set point, or
does not raise the alarm, was not checked. *Dated 1 Nov 2026: [Q132(g)](../2026-11-01-q132-governor-desk/README.md) §a takes this up: aifoundry2 shows no alarm at any reading it reports, on a reading not shown to be card 0's quantity, firmware or board unknown.*

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
  - **Device holds.** Every kernel launch ran under `timeout 10` with the stop file: 139 launch processes, all rc 0.
    The `ettelem config` and `uptime` reads ran under `timeout 10` too. Two device openers did not, which the
    pre-registration's "`timeout 10` on every device process" missed:
    - the firmware read ran under `timeout 20`, with `dev_mngt_service`'s own 5,000 ms reply timeout (`-u 5000`)
      inside it. It finished within 15:42:00 (`run_e84.sh` line 65);
    - `run_hpl`'s sampler (`ettelem sample --seconds <plan + 900>`) runs outside any `timeout`, and the runner stops
      it with SIGTERM at each run's end. All 35 exited rc 0 after 11.8–87.7 s, with no `error` mark, no SIGKILL and
      no drain.

    The queue drain (`timeout 20`) never ran. The scripts stay as they ran
    ([`corrections-check.txt`](corrections-check.txt) C5).
- **Interim looks.** During the session only the runner's status lines were read (run counts and gate readings). The
  reduction ran after the session ended.

**Corrections of the pre-registration's description (not of any frozen prediction or rule).**

1. *"Between processes the clock drops to a 300 MHz / 398 mV point"*: not so in this session, nor in E60's own
   card-0 telemetry of 20 Oct. Corrected after verification (C6); the first version of this item said E60's 300 MHz
   samples "were most likely the same safe state", which overstated it.
   - **31 Oct.** Card 0 idled at 600 MHz / 519 mV between runs: every gate reading and both configuration reads say
     so. All 436 readings at 300 MHz are in the four fp32 random-data runs, the runs that logged the PMIC alarm.
   - **20 Oct (E60).** In all 12 committed card-0 telemetry files, 6,047 of the 6,133 readings under 25 W sit at
     600 MHz. One sits at 300 MHz, at the tail of an episode inside the work.
   - **E60's heater probe.** Its 300 MHz readings come in 33 episodes inside the work:
     - 10 follow a board reading of 70 W or more in the prior 0.4 s;
     - 20 follow the 600 → 700 → 800 climb with a lagged reading of 44.9–60.2 W;
     - 3 follow an idle-level reading of 27.6–28.1 W at 800 MHz / 604 mV.

     The first two kinds match the alarm cycle seen here. The 10 Hz telemetry cannot tie the last three to the
     alarm.
   - **What is not known.** E60's trace rings are not in the repository (the `.bin` files there are tiles), so the
     alarm is not confirmed for 20 Oct. Card 0's firmware on 20 Oct is not known either. The card table's 1.4.1 dates
     from 25 Sep, when card 0 did idle at 300 MHz / 398 mV (`14-card-behaviour.md`), and E84 read 1.4.0 on 31 Oct.
2. The sustained "ramp" is therefore the climb from the 600 MHz idle point, not from 300.

## What this changes for the blog material and the hub

- **The kinds table gains a second card.** These are the speed cells for 11 kinds on aifoundry1's card 0: burst and
  sustained MHz, TFLOPS/TOPS, p800 and p800 over zeros, sustained board W and die, and the limiting test.
- **Levels/Status: a third limit.** The PMIC's 75 W over-power alarm, with a 300 MHz safe state, limits fp32 random
  data on card 0. It sits beside the governor's 65 W power arm and 65 °C thermal arm. A blog sentence that says "two
  limits" should say "two, and on a card that runs closer to 75 W at 800 MHz, a third".
- **Cross-card comparisons** use aifoundry2's same-day runs (E80, E83), not E64's of 23 Oct. Card 0 differs from
  aifoundry2 in power, not in cooling: it draws 4.5–9.8 W less board power at 800 MHz, and per board watt its die
  runs 1.1–1.5 °C hotter (C1, C8).
- **Records.** Card 0's firmware on record is stale: it is 1.4.0 / BL2 0.22.0 / PMIC 1.6.1 / minions 0.25.1. It idled
  at 600 MHz on 31 Oct, and in E60's telemetry of 20 Oct, not at 300. The places to correct are `14-card-behaviour.md`'s
  card table and its "Firmware 1.4.1 idles at 300 MHz", which is a 25 Sep record.

## Corrections after verification (Sat 31 Oct 2026)

*The Q130 more-cards workflow's verifier checked E84. It found one major fault and ten minor ones, with the verdict
"holds with fixes". These corrections were made at the desk: no card was touched and nothing was re-run. No number in
`results.json` or `reduce.txt` changed (their sha256 is the first line of the check), no frozen input changed, and no
verdict changed. [`corrections-check.py`](corrections-check.py) prints every number below from committed files, and
[`corrections-check.txt`](corrections-check.txt) is its output (the same on Python 3.10 and 3.14).*

| | what was wrong | what changed |
|---|---|---|
| **C1** (major) | The all-ones comparison used E64's aifoundry2 numbers of 23 Oct (737.9 / 737.1 MHz) and called card 0 "the cooler card". | aifoundry2's same-day runs read 782.4 MHz (E83) and 781.6 MHz (E80), each with one of two runs thermal. Card 0's lead is 11–14 MHz, inside aifoundry2's own spread. Card 0's die line (13 runs) is 41.78 + 0.4753 °C per W and reaches 65.5 °C at 49.9 W, against aifoundry2's 53.4 W, so per board watt card 0 runs 1.1–1.5 °C hotter. "Better cooling" is withdrawn: the cause is about 6 W lower draw. See Results first, item 4. |
| C2 | aifoundry2's fp32 zeros came from E64, giving 1.13× / 1.33× and a zeros p800 of 35.0 W. | They now come from E83, the same day: 1.15× / 1.31× over E80's random data (1.14× / 1.29× over E83's anchor), and a zeros p800 of 34.1 W. In the cells table, fp32 zeros now read 800 / 789.3 and fp32 ones 800 / 782.4 (E83). |
| C3 | The idle level read 19.0–20.6 W, which is the burst runs' range. | It is 19.0–21.2 W over all 35 runs (`runs[].idle_w`). |
| C4 | The ratios carried no uncertainty, and fp16 and int8 "agreed to within 2%". | Each ratio now carries its pass-paired or replicate range: fp32 1.35–1.47× burst and 1.655–1.682× sustained, fp16 1.039–1.047× burst. fp16 and int8 sustained are one run each and are now called "consistent with" aifoundry2; the int8 agreement is within noise. |
| C5 | The pre-registration said "`timeout 10` on every device process". | That is true of the 139 launch processes and the configuration reads. The firmware read used `timeout 20`, and the sampler is bounded by SIGTERM, not by a timeout (35 of 35 rc 0). See Etiquette, above, and the dated note in the tool README. The scripts are left as they ran. |
| C6 | E60's 300 MHz readings "were most likely the same safe state". | 30 of E60's 33 episodes match the alarm cycle and 3 do not. E60 idled at 600 MHz, its rings are not committed, and card 0's firmware on 20 Oct is unknown. See correction 1, above. |
| C7 | fp32 random data "draws 73 W, enough to trip the 75 W alarm", and runs "1.67× slower". | It draws 72–75 W on the board, with PMIC readings of 75.00–76.25 W, at or over the 75 W alarm. Zeros run 1.67× faster: random data takes 1.67 times as long. |
| C8 | Card 0 drew "5–10 W less", in absolute watts with no label. | The gap is now labelled as absolute board power, which is what the power arm sees: 4.5–9.8 W. Of that, 4.5–5.1 W is there with zero data, and switching over zeros differs by 1.1–5.3 W. |
| C9 | The blog material written from E84 said zero operands "switch fewer wires", and E84 does not measure wires. | That material now says only what E84 measured: zero data draws less power in every format, on both cards. This README never made the claim. The toggle counts that would back "wires" have been provisional since Q130's RTL-formats revision 2 (`../2026-10-31-q130-rtl-formats/README.md`, §0), because the bench behind them does not compute the multiply-add. |
| C10 | P3's PASS was given without its split. | Of the three kinds predicted to be limited, 1 of 3 is right in the burst and 2 of 3 sustained; the eight predicted none are 8 of 8 in both blocks. See Results first, item 1, and the rules table. |
| C11 | "Over zeros" shares a name with E78's and E82's switching power but not its clock. | The text now states its conditions: 800 MHz and 603–604 mV, board power, first second. E78's and E82's switching power is at 600 MHz. |
| C12 | Found while checking C6: the README cited "aifoundry2's committed rings, E80's 59 and E64's". | It now cites E80's 64 dumps (59 in the session), E64's 58 and E83's 125, with no alarm and no 300 MHz point, and none of 93,276 telemetry readings at 300 MHz. |

## Files

| path | what |
|---|---|
| `s1/` | the session: `session.json`, `kspeed.json`, `e84.json` (frozen hashes, freeze commit `337b03b2`), `runs.jsonl`, `launches.jsonl.gz`, `tel/*.jsonl.gz` (10 Hz sampler), `sp/*.bin` (the trace ring after each run), `queries.jsonl`, `marks.jsonl`, `run.log`, `manifest.txt`, `end.json` |
| `smoke/` | the three 2 s smoke runs (not analysed) |
| `ident/` | the read-only identity reads (configuration, uptime, firmware revisions) and the closing reads |
| `logs/` | the runner's stage logs on the box |
| `results.json`, `reduce.txt`, `reduce.log` | the registered reduction (`reduce_e84.py`, with E80's `results.json` beside) |
| `posthoc/pmic.json`, `posthoc/pmic.txt` | the post-hoc PMIC alarm view |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind the corrections after verification, and its output: the same-day aifoundry2 comparisons, both cards' die lines, the intervals, the device holds, E60's 300 MHz episodes and aifoundry2's rings |

Reproduce on the Intel: `bash tools/claims-v3/kspeed/e84/collect_e84.sh` (it copies the raw session from aifoundry1 and
reduces it); `python3 tools/claims-v3/kspeed/e84/posthoc_pmic_e84.py <this dir>/s1 --out <this dir>/posthoc/pmic.json`;
in this directory, `python3 corrections-check.py > corrections-check.txt`.
