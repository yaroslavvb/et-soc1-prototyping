# E114: card 0's fp16 and int8 sustained cells, replicated — three passes on aifoundry1 card 0 under its own governor (Q133)

*It answers the final critic's item 8, "Replicates for the new sections" ("E88's split itself, E91 and card 0's sustained
cells were not re-run"), which the Horace hub's Status fold keeps under "What Q132 did to the two lists it set out from". That item is not a numbered item of the kinds page's
[section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) as of
`1fe8377a18af`. It also answers [E84](../2026-10-31-e84-speed-aifoundry1-card0/README.md)'s correction C4 ("fp16 and int8
sustained are one run each"). §4 bears on section 11's **item 8, "The heat path drifts between sessions"**: a second card
ran 1.7 °C cooler at the same board power between two afternoons.*

*Sun 1 Nov 2026 (week 44), Q133. Pre-registered in `59b1ad5c` (git commit time 14:16:51, pushed 14:16:54 PST, before the
claim and the first device access): [`tools/claims-v3/e114/E114.md`](../../../../tools/claims-v3/e114/E114.md), frozen
numbers and rules in [`predictions-e114.json`](../../../../tools/claims-v3/e114/predictions-e114.json) (sha256
`91731ced…`). No amendment. aifoundry1 card 0 under its own governor: TDP 65 W, threshold 65 °C, 600 MHz and 519 mV idle,
read at the start (14:18:10, [`ident/ident-141810.out`](ident/ident-141810.out)), after every run, at the session's start
and end, and after the session (14:39:47, [`ident/final-143947.out`](ident/final-143947.out)), never set: no governor
move, no TDP, threshold, clock or voltage set, no reset, no `--reset-ms`. **One PMIC command was sent, against the
workflow's rule**: the firmware-revisions query at the start (14:18:10), which writes the PMIC's firmware-management
command register twice (C1, below). It read E84's firmware: release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.6.1, minions
0.25.1. Claim `1566577076486537337` in #community-lab, posted 14:18:00.629 PST, released by editing the same post at 14:40
PST: **about 22.1 card-minutes of the registered 30** (the session itself ran 14:18:26–14:39:43, 15 of 15 runs, exit 0,
21.3 card-minutes).*

*Corrected after verification the same afternoon, at the desk, with no card touched and nothing re-run. Wrong sentences are
replaced in place below. [Corrections after verification](#corrections-after-verification-sun-1-nov-2026) lists C1–C9, and
[`corrections-check.txt`](corrections-check.txt) prints their numbers from committed files. No number in `results.json` or
`reduce.txt` changed, and no verdict changed. Two passages were wrong and are replaced: the sentence denying a PMIC command
(C1), and §3's account of int8's sign (C2).*

**What ran.** E84's sustained shape, unchanged: nine back-to-back 8 s processes from a die reading ≤ 57 °C, read over the
last 40 s of the work, on five kinds (fp16 zeros, ones and randn; int8 zeros and full), three passes in the registered
shuffled order, by E84's runner unchanged. **The sustained rate** is the kernel's own operations over its own wall time
(TFLOPS for fp16, TOPS for int8). **ρ** is the mean over passes of rate(zeros) ÷ rate(random) in the same pass, random being
fp16 randn and int8 full. Intervals are 95%, t(0.975, n − 1) × sd / √n over the three runs or pairs; a prediction interval
(PI) is the range one new run would fall in, t(0.975, n − 1) × sd × √(1 + 1/n).

## Results first

**Three of the four primary rules pass, and one frozen prediction failed.** E84's five single runs fall inside today's
prediction intervals (R1), zeros run clearly faster than random fp16 (R2), and every run's limit repeats (R4). The int8
reading came out SLOWER, not the frozen SAME_WITHIN_BAR (R3 WRONG): today int8 zeros ran 0.8% slower than random int8,
where E84 had them 0.8% faster. Post hoc, both int8 differences are differences of clock. At the sampled clock the
pass-paired rates agree within 0.2%. The clock differs by how many times the governor's once-a-second idle check dropped
it to 600 MHz inside the window, and nothing in that reads the data (§3). The secondary cross-card readings came out as
frozen.

| rule | says | threshold | happened | verdict |
|---|---|---|---|---|
| **E114-R1** | E84's single run of each kind inside today's 95% PI, sustained rate | ≥ 4 of 5 | 5 of 5 | **PASS** |
| **E114-R2** | ρ16, zeros ÷ random fp16 | lower end ≥ 1.15 | **1.2312 ± 0.0605** (1.1707–1.2917) | **PASS** |
| **E114-R3** | ρ8, zeros ÷ random int8: a reading, frozen as SAME_WITHIN_BAR | FASTER / SLOWER / SAME_WITHIN_BAR (holds 1, inside 0.98–1.02) / INCONCLUSIVE | **0.9919 ± 0.0048** (0.9871–0.9967): excludes 1 from below, so SLOWER | **WRONG** (SLOWER) |
| **E114-R4** | each run's sustained limit equals E84's for its kind | ≤ 1 of ≥ 14 differs | 15 of 15 equal | **PASS** |
| E114-S1, fp16 (secondary) | ρ16(card 0) − ρ16(aifoundry2) | ALIKE inside ±0.05; DIFFERENT when 0 is outside | −0.0802 ± 0.0653 (−0.1455 to −0.0149) | DIFFERENT, as frozen |
| E114-S1, int8 (secondary) | ρ8(card 0) − ρ8(aifoundry2) | ALIKE inside ±0.02 | −0.0174 ± 0.0264 (−0.0438 to +0.0090) | INCONCLUSIVE, as frozen |

Source: [`results.json`](results.json) › `rules`, written by
[`reduce_e114.py`](../../../../tools/claims-v3/e114/reduce_e114.py) as registered; [`reduce.txt`](reduce.txt) is its
console output. R1's prediction intervals are wide at three runs (±4.97 sd), so its PASS says E84's runs are not outliers,
not that the cells agree to the precision of one run.

### 1. The five cells, three runs each

| kind | sustained rate (95%) | runs | sampled MHz (95%) | board W | die °C (max) | limit | E84's single run (31 Oct) |
|---|---|---|---|---|---|---|---|
| fp16 zeros | **24.29 ± 0.78** TFLOPS | 24.363, 23.940, 24.555 | 791.9 ± 23.2 | 28.69 | 53.5 (53–55) | none ×3 | 24.354, 794.1 MHz, 29.60 W, 56.0 °C |
| fp16 ones | **24.374 ± 0.055** TFLOPS | 24.399, 24.364, 24.358 | 794.8 ± 1.7 | 45.92 | 62.2 (62–64) | none ×3 | 24.395, 795.6, 46.72, 63.9 |
| fp16 randn | **19.73 ± 0.91** TFLOPS | 20.150, 19.508, 19.530 | 657.3 ± 33.6 | 52.36 | 65.5 (66–67) | thermal ×3 | 19.107, 631.9, 49.04, 65.8 |
| int8 zeros | **82.79 ± 1.17** TOPS | 82.254, 82.977, 83.141 | 787.1 ± 8.7 | 29.74 | 54.3 (55) | none ×3 | 83.709, 794.6, 30.87, 56.9 |
| int8 full | **83.47 ± 0.80** TOPS | 83.094, 83.640, 83.666 | 792.7 ± 6.8 | 43.64 | 60.4 (61) | none ×3 | 83.078, 788.7, 44.42, 62.8 |

Source: `results.json` › `cells.<kind>.rate`, `.mhz`, `.w`, `.die`, `.die_max`, `.limits` and `.e84`;
[`readme-numbers.txt`](readme-numbers.txt) § B. Board W is absolute (not over zeros). The die is the minion-shire mean
sensor over the last 40 s. Every run held its kind's E84 limit: random fp16 at the 65 °C trip (84–96% of the window labelled
thermal), the other four with ≥ 90% of non-ramp samples at 800 MHz.

- **Four kinds sit at the 800 MHz cap, and their deficit is the governor's falls to 600 MHz.** fp16 ones and int8 full read
  800 MHz on every non-ramp sample of every run. fp16 zeros and int8 zeros did in four of their six runs. The other two had
  12–14 samples labelled `other` (`.mhz_nonramp`, `.sus_counts`). Each was a fall to 600 MHz in the middle of a process,
  4.0 s and 7.0 s in, after a 1–2 ms gap between kernels (`corrections-check.txt` C2). A sustained rate varies by run with
  how many falls its window holds. Most come at a process start, where the clock climbs back from 600 MHz, and a few come
  inside a process (§3). That makes fp16 zeros the widest of the four, ±3.2%: one run read 781.7 MHz with three falls in
  the window (two at process starts, one inside a process), and one read 800 MHz with none.
- **Random fp16 ran 3.3% faster today than in E84** (19.73 against 19.107 TFLOPS; its sampled clock 657 against 632 MHz,
  4.0% faster) and drew 3.3 W more board power, at the trip in both sessions (die 65.5 °C against 65.8). It runs as fast
  as the heat path lets it, and today's heat path ran cooler (§4). Its first run started from a 47 °C die, the session's
  first reading, and the other two from 55 °C: the first read 672.8 MHz against 648.2 and 650.8. Its cell is the widest,
  ±4.6%.
- **The four cooler kinds drew 0.8–1.1 W less than in E84 and ran 1.7–2.6 °C cooler at about the same clock**, as a cooler
  die leaks less (§4). E84's board W and die for int8 zeros, and its die for int8 full, lie outside today's PIs (`.w`,
  `.die`, `e84_inside_pi95`; random fp16's die PI has no width, 65.5 °C in all three runs). These are context, not rules.

### 2. Zeros over random, sustained, now with an interval

| format | card 0, E114 (3 pass pairs) | pairs | card 0, E84 (one run each) | aifoundry2 (E80, E83, E87, E96) |
|---|---|---|---|---|
| fp16 | **×1.231 (1.171–1.292)** | 1.209, 1.227, 1.257 | ×1.275 | ×1.311 (zeros 4 runs, random 6) |
| int8 | **×0.992 (0.987–0.997)** | 0.990, 0.992, 0.994 | ×1.008 | ×1.009 (zeros 4 runs, random 8) |

Source: `results.json` › `rho.fp16`, `rho.int8` (pairs and the ratio of the cells' means, 1.231 and 0.9919, beside them);
aifoundry2 from `predictions-e114.json` › `aifoundry2_pool`; `rules.E114-S1`.

- **fp16: the gap replicates.** Zeros beat random fp16 by ×1.17–1.29 sustained on card 0, above R2's 1.15. Today's 1.23
  sits below E84's single 1.27, a difference inside one session's spread: E84's pair lies inside today's 95% PI for one
  pass pair, 1.110–1.352 (`readme-numbers.txt` § C). What the two days do resolve is the heat path (§4). Random fp16 runs
  at the trip, and it ran 3.3% faster in rate today under a cooler heat path, while zeros stayed at the cap. Against
  aifoundry2's ×1.31 the difference is −0.080 (−0.146 to −0.015), DIFFERENT, as frozen: card 0's random fp16 runs 5.7%
  faster than aifoundry2's pooled runs (19.73 against 18.66 TFLOPS), and its zeros 0.8% slower (24.29 against 24.47,
  `readme-numbers.txt` § D). Two causes are named and not separated: card 0 draws 4.5–9.8 W less board power for the same
  tiles (E84 C8), so it reaches the trip at a higher clock, and today's heat path was cooler than 31 Oct's. aifoundry2's
  pool spans four sessions over two days; card 0's is one session.
- **int8: no speed difference belongs to the data.** Both kinds hold ~790 MHz with no limit acting, in every run of both
  sessions. Today zeros ran 0.8% slower, with an interval that excludes 1; E84 had them 0.8% faster, and E84's pair lies
  **outside** today's PI for one pass pair, 0.982–1.002. An interval over three pass pairs from one session does not cover
  what moves between sessions. Here what moves it is the count of the governor's falls to 600 MHz inside each window (§3).
  Against aifoundry2 the reading is INCONCLUSIVE at a ±0.02 bar, as frozen.

### 3. Post hoc, labelled, never a verdict: why int8's sign flipped

*Replaced after verification (C2). The first version said that which of a window's four process starts began with a climb
from 600 MHz set int8's sign. Pass 1 contradicts that: both kinds had two such climbs in the window, yet pass 1 has the
largest deficit.*

Sources, all written after the data. When R3 read SLOWER: [`posthoc/climb.txt`](posthoc/climb.txt) and
[`posthoc/climb.json`](posthoc/climb.json), from [`posthoc/posthoc_climb.py`](posthoc/posthoc_climb.py). After the
verifier's report: [`corrections-check.txt`](corrections-check.txt) C2 (every fall in the window), and
[`posthoc/lattice.txt`](posthoc/lattice.txt) from [`posthoc/posthoc_lattice.py`](posthoc/posthoc_lattice.py), which runs
[Q132(g)](../2026-11-01-q132-governor-desk/README.md)'s heartbeat lattice on this session with its code unchanged.

**The gap and the climb.** Between two of a run's nine processes no kernel runs for 0.33 s (median, last kernel's end to
the next process's first kernel; 0.326–0.339 s today). At each process start the clock is either still at 800 MHz, with
the first 800 MHz sample within 0.15 s (0.23 s in E84), or it climbs from 600 MHz for 0.47–1.46 s; no climb lies between.
Every run's first process climbed, 15 of 15 today and 5 of 5 in E84: it follows the sampler start, the cooling gate and a
1 s pause. Of the eight starts after it, **40 of 120 climbed today (33%) and 13 of 40 in E84 (32%)**. The climb does not
depend on the data: over all 27 process starts of a kind, the mean climb is 0.520 s for int8 zeros and 0.511 s for int8
full today. In E84 it was 0.570 and 0.646 s, over 9 starts each.

**What sets a window's clock: every fall in it.** A sustained cell reads the last 40 s: four process starts and about 36 s
of kernels. The clock also falls inside a process, rarely, when the same check lands in a 1–2 ms gap between two kernels.
Counting every fall to 600 MHz that reaches the window while kernels run (`corrections-check.txt` C2):

| | pass 1 | pass 2 | pass 3 | E84 |
|---|---|---|---|---|
| int8 zeros: falls in the window (at a start + inside a process) | 3 (2 + 1) | 2 (2 + 0) | 2 (2 + 0) | 1 (1 + 0) |
| int8 full: falls in the window | 2 (2 + 0) | 1 (1 + 0) | 1 (1 + 0) | 2 (2 + 0) |
| samples below 800 MHz in the window, zeros / full | 36 / 22 | 24 / 12 | 22 / 13 | 12 / 24 |
| ρ8, zeros ÷ full, sustained rate | 0.98989 | 0.99207 | 0.99373 | 1.00760 |
| rate ratio ÷ sampled-clock ratio | 0.9981 | 0.9995 | 0.9994 | 1.0001 |

- Zeros had one more fall than full in each of today's three pairs, and one fewer in E84's.
- Pass 1's extra fall came inside a process, 4.0 s into one of int8 zeros' processes, after a 2 ms gap between kernels. Its
  start climbs tie, 2 and 2.
- At the sampled clock the data leave the rate alone, to within 0.2%. That is the table's last row. fp16 zeros against
  ones, both at the cap, read 0.9987–1.0009 in the same passes (E84 1.0002).
- So int8's ±0.8% is a difference of clock, and the clock difference is the count of falls in the window.
- What one fall costs shows in the int8 full runs: 83.094 TOPS with two, against 83.640 and 83.666 with one, about 0.7%.
  That is the size of int8's ±0.8% in both sessions.
- The same count spreads fp16 zeros: 24.363, 23.940 and 24.555 TFLOPS with 1, 3 and 0 falls. The middle run's three include
  one inside a process, 7.0 s in, after a 1 ms gap. E84's fp16 zeros run had one, 0.5 s into a process that started at
  800 MHz.

**The falls are the governor's once-a-second idle check.** Q132(g) §b reads it in public source. The Master Minion's
heartbeat reports "no kernel in use" whenever it lands between two kernels, and the service processor then drops the clock
to its 600 MHz boot point at once. In Q132(g), a lattice fitted on E84's three falls predicted all 72 of E84's gaps
between processes on this card. [E100](../2026-11-01-e100-idle-reset/README.md) then tested the behaviour, pre-registered,
with controlled gaps on aifoundry2, and passed all five rules: all 39 heartbeats in a gap fell, and none of the 234 inside a
kernel did. Run on this session with Q132(g)'s code unchanged ([`posthoc/lattice.txt`](posthoc/lattice.txt)):

- **One lattice.** The session's five clean falls inside a process (sampler and kernel rules, every process of the 15 runs)
  sit on one lattice: period 1000.0191 ms (E84's on this card was 1000.0186), residuals within 0.55 ms over 1,110 beats.
- **95 of 95 gaps predicted.** That lattice, fitted on those five falls alone, predicts every gap between processes: the 31
  gaps holding a lattice point all fell, and the 64 holding none all stayed at 800 MHz. The 25 gaps after random fp16's last
  kernel at the trip are left out, as Q132(g) leaves them.
- **The climb waits for a heartbeat.** It ends at the next heartbeat that sees a kernel: the first 800 MHz reading comes
  0.39 ± 0.05 s (median, sd; 35 later starts) after the first lattice point inside a kernel. Measured from the process's
  first kernel, it comes 1.26 ± 0.15 s later.

A 0.33 s gap in a 1 s period holds a heartbeat a third of the time (31 of 95 here). A heartbeat lands in one of the 1–2 ms
gaps inside a process rarely (5 falls in 135 processes). Which gaps hold one follows from where a free-running 1 s timer
falls against each run's process timing. In its 25 falls, Q132(g) §b saw no dependence on format, die or power (p 0.49,
0.91 and 0.93: "no dependence visible"). All of this is post hoc, on one session, and no card was run for it.

**For the blog**, the int8 sustained cell on card 0 is "the same speed as zeros, within about 1%". The 1.008 and 0.992 are
differences of clock: each window caught a different number of the governor's once-a-second falls. A cell at the cap
needs replicate runs **across sessions**, or more process starts in its window, before a ±1% difference counts.

### 4. Context: today's heat path ran 1.7 °C cooler than 31 Oct's

Each run's die, minus E84's die line at the run's board W (41.780 + 0.4753 °C per W over E84's 13 sustained runs): **−1.67
°C**, about ±0.5 °C at 95% once the line's own fit error is counted. That is ±0.51: the line's standard error at today's
mean board W is 0.19 °C, and today's within-session one is 0.15 °C (`corrections-check.txt` C3). The ±0.33 in
`results.json` › `context.die_vs_e84_line` is today's within-session spread alone, and the runs read −2.33 to −0.43. It
is one session each afternoon. Today's own line is 39.36 + 0.4941 °C per W. It reaches 65.5 °C at 52.9 W, against 49.9 W
on E84's line, and random fp16 settled at 52.36 W today against E84's 49.04 W. Card 0's idle die read 46–47 °C at today's
first gates, against 48–50 °C at E84's (`readme-numbers.txt` § A). Q132(g) §c found, post hoc, that across sessions on
aifoundry2 the 76 s die line moves with the card's die at rest, a proxy for the room, with no change in the heat path
itself required. Today's lower rest die fits that. No rate per °C is quoted here:
[E98](../2026-11-01-e98-heat-path-drift/README.md) bars quoting one. Today's session started at 14:18 PST, within half an
hour of E84's start by the sun (15:43 PDT is 14:43 PST). This is the drift of
[section 11's item 8](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), "The heat path
drifts between sessions", on a second card, between two afternoons: about 1.7 °C at the same board W. It moved the
thermal-limited cell, random fp16, by about 25 MHz (4%; its rate by 3.3%). The cells at the cap moved by at most 1.1%
between the sessions, which §3's falls account for. No inlet temperature was read.

### 5. What this changes for the blog material and the hub

- **The kinds page's speed table** (section 1, "zeros ÷ random, speed"): card 0's sustained fp16 cell becomes **×1.23
  (1.17–1.29, three runs)** at the 65 °C trip, where it says ×1.27 from one run; its int8 cell becomes **×0.99–1.01, no
  limit: equal within about 1%**, where it says ×1.01. The note under the table, "Card 0: E84, two burst passes per cell,
  one sustained run per cell (two for fp32).", gains "fp16 and int8 sustained: E114, three runs a cell".
- **Section 1's lead and its paragraph.** "On a second card the sign holds; so does the size in int8 and in fp16 sustained
  (single runs)" and "fp16's ×1.27 is consistent with aifoundry2's ×1.30–1.32 and int8's ×1.01 with its ×1.01, each
  resting on single runs" no longer hold for fp16. On card 0 the fp16 sustained gap is smaller, ×1.23 against ×1.31 (S1
  DIFFERENT, a secondary rule; card and day confounded). int8's is equal within about 1% on both cards.
- **"Consistent with aifoundry2" becomes measured.** Card 0's fp16 sustained gap is smaller than aifoundry2's (×1.23
  against ×1.31; DIFFERENT, secondary), for two named, unseparated causes: lower board power and a cooler day. Its int8 gap
  cannot be told from aifoundry2's at ±0.02. The sign holds on both cards and in every run: zeros are never slower than
  random fp16.
- **The final critic's replicates item** (its item 8, kept in the Horace hub's Status fold): card 0's sustained cells are
  re-run for fp16 and int8, three runs a cell, one session. Still not re-run: card 0's fp32 cells (random fp32 trips its
  75 W alarm), int8 `neg_ones`, and any replicate across sessions on card 0.
- **Section 11's item 8** ("The heat path drifts between sessions") gains a second card. Card 0's die line moved −1.67 °C
  (about ±0.5) at the same board power between the 31 Oct and 1 Nov afternoons, one session each, with its rest die lower.
- **Records.** `14-card-behaviour.md`: on card 0, under E84's sustained shape, the governor's once-a-second idle check
  drops the clock to 600 MHz in a third of the 0.33 s gaps between processes. It also does so, rarely, in a 1–2 ms gap
  between kernels. Today that was 31 of 95 gaps and 5 falls in 135 processes, on one heartbeat lattice that predicts 95 of
  95 gaps. 40 of 120 later starts climbed today, and 13 of 40 in E84. Every first start climbs. How many falls a window
  holds decides about ±1% in a sustained cell at the cap. Card 0's die line moved −1.67 °C (about ±0.5) between the
  31 Oct and 1 Nov afternoons. `03-experiments.md`, `05-claims.md` and the hub carry C1's sentence: E114 sent one PMIC
  command, the revisions query.

## Registered against what happened

- **No amendment, no departure from the registered design.** The start read matched E84's (65 W / 65 °C; release 1.4.0,
  BL1 and BL2 0.22.0, PMIC 1.6.1, minions 0.25.1), so `run_e114.sh start` went on to the smoke. The smoke passed its checks
  (exit 0, two runs, every launch rc 0, 65 W / 65 °C after each), so it started the session at 14:18:25.
- **The failed prediction stands as failed.** R3 was frozen as SAME_WITHIN_BAR and read SLOWER. §3's explanation is post
  hoc and changes no verdict.
- **Nothing was set on the card**: no governor move, no TDP, threshold, clock or voltage set, no reset, no `--reset-ms`.
  The configuration was read, never written: 65 W / 65 °C after all 15 runs (`results.json` ›
  `context.config_after_every_run`), and at the session's start and end reads (`s1/queries.jsonl`).
- **One PMIC command was sent (C1).** The registration and `run_e114.sh` call the start's firmware read "read only" and say
  "no PMIC command". That is wrong. The query, `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`, ran once at 14:18:10, under both
  cards' locks with `timeout 10` (`ident/ident-141810.out`). At et-platform `836a4ab`, whose bootloaders' project version,
  0.22.0, is card 0's BL2, its handler (`services/firmware_update.c:1091` → `:903`) calls `pmic_get_fw_version`
  (`driver/pmic_controller.c:952`). That writes the PMIC's firmware-management command register twice, `ACTIVE_SLOT` then
  `VERSION` (`:2543`, `:2581-2587`), and reads its data register after each.
  - Under the lab's standard since [E85](../2026-10-31-e85-camera-kinds/README.md)'s correction C1, a DM command the
    service processor passes to the PMIC is a PMIC command. The workflow's rule allowed none but the statistics reset.
  - [E118](../../../../tools/claims-v3/e118/CHANGE-RECORD.md), on this card half an hour later, classes this exact query
    as "a PMIC command, not sent" and takes the firmware identity from the module's unbroken uptime instead.
  - It was one read-type query, routine in the lab since September (E69, E72, E79, E82, E84) and named in E114's
    registration before the run. The card answered normally afterwards: E118's gate reads at 14:50:39 found its uptime
    unbroken and 65 W / 65 °C.
  - No other PMIC write was sent. As in every lab run with the stock sampler, `ettelem config` (17 times in the session, plus
    the start and closing reads) and each of the 12,695 sampler readings send `GET_ASIC_VOLTAGE`. The readings also send
    `GET_MODULE_VOLTAGE`. These read PMIC voltage registers, with no write (E118's change record lists the handlers;
    `tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp:160, 206-207`).
  - The stage script's comment is left as it ran; its sha256 is in `logs/e114-start.json`. Later card runs take firmware
    identity by uptime continuity, as E118 does, never by this query.
- **The runner and binaries are E84's.** `run_e84.py`, `run_kspeed.py`, `run_hpl.py`, `reduce_hpl.py` and `reduce_e84.py`
  are byte for byte E84's, and so are `sparsity_host`, `sparsity.elf` and `ettelem-e84`
  ([`logs/e114-start.json`](logs/e114-start.json)). Every tile was checked against `kinds.json` before the session
  (`s1/kspeed.json`). The runner writes the session's `e84.json` under E84's name and with E84's `predictions.json` hash:
  that is the unchanged code speaking. Its `freeze_commit` reads E114's `59b1ad5c`.
- **Device holds.** All 135 launch processes ran under `timeout 10` with the stop file, and all exited rc 0. The cooling
  gates all passed within 0.1 s, at die readings of 47–57 °C. Run starts were 84.2–86.9 s apart. The `ettelem config` and
  `uptime` reads and the firmware read ran under `timeout 10` (the firmware read with both cards' locks held non-blocking
  for the one call). The sampler (`ettelem sample`) runs outside a `timeout` and is stopped with SIGTERM by `run_hpl.py`,
  as in E84: 15 starts, 15 stops, no error mark (`s1/marks.jsonl`).
- **Interim looks.** While the session ran, only the runner's status lines (run counts and gate readings) and the first
  lines of `marks.jsonl` (the login count and the start configuration) were read. The reduction ran after the session
  ended, on the complete session.

## Card time and etiquette

- **Before the claim**: the registration pushed at 14:16:54. `#community-lab` was read at 14:17: nothing claimed
  aifoundry1. Card 1's last claim had been released at 13:49 (E112), and aifoundry2 and aifoundry3 each had an open Claude
  claim. `et-who` showed no holder on either card at 14:07 and 14:16, and no device process.
- **The claim**: `1566577076486537337`, posted 14:18:00.629 PST: *"using aifoundry1 card 0 for 1 h, until ~15:20 PST"*,
  in the form `lab_reservations` parses. At 14:40 the same post was edited to append " — released", and read back:
  "<ai> Claude says: using aifoundry1 card 0 for 1 h, until ~15:20 PST doc — released (edited)".
- **Card time**: claim to release about 22.1 card-minutes. First device access was the identity read at 14:18:10, and the
  last the closing read at 14:39:48.
- **Others**: card 1 was free throughout and untouched, except that the one revisions call opened its management node
  once, read-only, under card 1's lock (C7). The stock `dev_mngt_service` opens every card's node even with `-n 0`. E112
  had released card 1 at 13:49, and `et-who` showed no holder. Two login sessions of other users were
  counted, and the runner's two-card rule treats a login alone as no hit (`s1/marks.jsonl`, `logins`). Nobody is named.
  No device process, holder or CI job of anyone else appeared.
- **The kernel log was not read by E114 (C8).** Other lanes' committed reads bracket card 0's error events (post hoc,
  `corrections-check.txt` C8):
  - 575 at Q132(g)'s read, 00:13 PDT on 1 Nov (252 SP runtime errors, 177 PMIC over-power events, 146 thermal-throttling
    events; [`host/err-aifoundry1.txt`](../2026-11-01-q132-governor-desk/host/err-aifoundry1.txt)).
  - 701 at E118's read at 14:50:39 PST, 126 more.
  - The last event is at host uptime 520,656.76 s. By the boot time in Q132(g)'s read, that is 14:39:41 PST. That is 2 s
    before E114's last throttle-residency reads, at 14:39:43.4. Over six days the kernel's timestamps and the wall clock
    can differ by seconds, so the 2 s does not separate the two.
  - E114 read the residency of states 4–6 after every run and at the session's start and end, and all 51 of those reads
    returned rc −5. [E77](../2026-11-01-e77-rail-one-temperature/README.md)'s amendment A1 notes that E69's rings show every
    read of states 5 and 6 logging a service-processor error.
  - E114's own rings show the same. Every dump after a run of a kind at the cap holds 3–6 "Unexpected power throtlling
    state" and "get_throttle_time()" lines. The random fp16 dumps hold none, because throttle records filled their 8 KB.
  - Random fp16 also held the 65 °C trip in all three of its runs.
  - So E114 likely raised some of the 126. How many host events, and of which kind, is unknown: that needs the log's own
    lines and timestamps, a read-only count on aifoundry1 while card 0 is free.

## Corrections after verification (Sun 1 Nov 2026)

*The Q133 verifier checked E114 and returned "holds with fixes": two major faults and seven minor ones. These corrections
were made at the desk the same afternoon: no card was touched and nothing was re-run. No number in `results.json` or
`reduce.txt` changed (their sha256 is the check's first section), no frozen input changed, and no verdict changed.
[`corrections-check.py`](corrections-check.py) prints the numbers below from committed files, and
[`corrections-check.txt`](corrections-check.txt) is its output (the same on Python 3.9 and 3.13).*

| | what was wrong | what changed |
|---|---|---|
| **C1** (major) | The header, "Registered against what happened" and the registration said "no PMIC command", and the stage script's comment says the same. The start's firmware-revisions query is a PMIC command. At et-platform `836a4ab` it writes the PMIC's firmware-management command register twice (`ACTIVE_SLOT`, then `VERSION`). That makes it a PMIC command under the lab's standard since E85 C1, and it falls outside the statistics reset the owner allowed. | Both passages now name the one query (14:18:10), the source lines, what mitigates it, and the samplers' voltage reads (no write). A dated note added to the registration's After-the-data note corrects its sentence without editing it. The stage script is left as it ran (hashed in `logs/e114-start.json`). It is flagged to the orchestrator so the owner can be told, as E85 C1 was. Later card runs take firmware identity by uptime continuity (E118). |
| **C2** (major) | §3 said "which of the window's four starts climb sets the sign" and called 1.008 and 0.992 "each one session's draw of process-start climbs". §1 put the two slowest runs at the cap down to start climbs. Pass 1 contradicts it: both int8 kinds had two start climbs in the window, yet pass 1 has the largest deficit. Each slow run also had a fall inside a process. | §3 is replaced. int8's ±0.8% is a clock difference (rate per clock 0.9981–1.0001). Counting every fall in the window, zeros had one more than full in each of today's pairs and one fewer in E84's. Run on this session, Q132(g)'s lattice, fitted on five falls inside processes, predicts 95 of 95 gaps between processes. All of it is post hoc, and no verdict moves. |
| C3 | The heat path's −1.67 ± 0.33 °C left out the fit error of E84's line. | −1.67 °C, about ±0.5 °C at 95% with the line's standard error (0.19 °C at today's mean board W). The ±0.33 is labelled within-session. There was one session each afternoon. |
| C4 | §2 put 1.23 against 1.27 down to the cooler day, and §1 gave random fp16's +3.3% in rate beside clock figures that differ by 4%. | E84's pair lies inside today's one-pair PI (1.110–1.352), so the gap's difference is inside one session's spread. What the two days resolve is the die line. Units are now matched: +3.3% in rate, +4.0% (+25 MHz) in clock. |
| C5 | §5 misquoted the kinds page's note under the speed table. It also named no change to section 1's lead, which S1's fp16 DIFFERENT contradicts. | The note is quoted as it stands, with the E114 clause appended. The lead sentence and its paragraph are listed. |
| C6 | The first line placed the final critic's item 8 in section 11 of the kinds page, which has no replicates item. Section 11's item 8 ("The heat path drifts between sessions"), which §4 bears on, was not linked. | The first line says where item 8 is kept (the Horace hub's Status fold) and links section 11's item 8. §4 and §5 link it too. |
| C7 | "Card 1 was untouched". | The revisions call opened card 1's management node once, read-only, under card 1's lock while card 1 was free. |
| C8 | Nothing was said about the kernel log or card 0's error events. | E114 did not read the kernel log. Other lanes' reads bracket card 0's events (575, then 701). The last one maps to 14:39:41 PST, 2 s before E114's last residency reads of states 4–6 (rc −5). E114's own rings hold the service processor's throttle-state error lines. How many host events E114 raised is unknown. |
| C9 | §3 and §4 built on E100 but not on Q132(g)'s §b (the heartbeat lattice; 72 of 72 gaps on E84) or §c (the die line follows the rest die). | Both are cited. §b's lattice was also run on this session at the desk, labelled post hoc (`posthoc/posthoc_lattice.py`). |

## Files

| path | what |
|---|---|
| `s1/` | the session: `session.json`, `kspeed.json`, `e84.json` (the runner's; freeze commit `59b1ad5c`), `runs.jsonl`, `launches.jsonl.gz`, `tel/*.jsonl.gz` (10 Hz sampler), `sp/*.bin` (the trace ring after each run), `queries.jsonl`, `marks.jsonl`, `run.log`, `manifest.txt`, `end.json` |
| `smoke/` | the two 2 s smoke runs (fp16 randn, int8 full; not analysed) |
| `ident/` | the start reads (configuration and uptime, read only; the firmware-revisions query, a PMIC command, C1) and the closing read |
| `logs/` | the runner's stage logs on the box, the dry smoke and `e114-start.json` (E114's hashes at the start) |
| `results.json`, `reduce.txt`, `reduce.log` | the registered reduction (`reduce_e114.py`) |
| `readme-numbers.py`, `readme-numbers.txt` | every number in this README's first version, printed from the committed files (desk, after the data) |
| `corrections-check.py`, `corrections-check.txt` | the numbers behind the corrections after verification (desk; post hoc where marked) |
| `posthoc/` | post hoc: the climb at each process start (`posthoc_climb.py`, `climb.txt`, `climb.json`), and Q132(g)'s heartbeat lattice run on this session (`posthoc_lattice.py`, `lattice.txt`, `lattice.json`) |

Reproduce on the Intel: `bash tools/claims-v3/e114/collect_e114.sh` (it copies the raw session from aifoundry1 and
reduces it); in this directory, `python3 readme-numbers.py > readme-numbers.txt` and `python3 corrections-check.py >
corrections-check.txt`; in `posthoc/`, `python3 posthoc_climb.py > climb.txt` and `python3 posthoc_lattice.py >
lattice.txt`.
