# E114: card 0's fp16 and int8 sustained cells, replicated — three passes on aifoundry1 card 0 under its own governor (Q133)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) as of `1fe8377a18af`: the final critic's replicates (its item 8, "Replicates for the new sections": "E88's split itself, E91 and card 0's sustained cells were not re-run"), and [E84](../2026-10-31-e84-speed-aifoundry1-card0/README.md)'s correction C4 ("fp16 and int8 sustained are one run each").*

*Sun 1 Nov 2026 (week 44), Q133. Pre-registered in `59b1ad5c` (git commit time 14:16:51, pushed 14:16:54 PST, before the
claim and the first device access): [`tools/claims-v3/e114/E114.md`](../../../../tools/claims-v3/e114/E114.md), frozen
numbers and rules in [`predictions-e114.json`](../../../../tools/claims-v3/e114/predictions-e114.json) (sha256
`91731ced…`). No amendment. aifoundry1 card 0 under its own governor: TDP 65 W, threshold 65 °C, 600 MHz and 519 mV idle,
read at the start (14:18:10, [`ident/ident-141810.out`](ident/ident-141810.out)), after every run, at the session's start
and end, and after the session (14:39:47, [`ident/final-143947.out`](ident/final-143947.out)), never set: no governor
move, no reset, no PMIC command, no `--reset-ms`. The firmware read at the start is E84's: release 1.4.0, BL1 and BL2
0.22.0, PMIC 1.6.1, minions 0.25.1. Claim `1566577076486537337` in #community-lab, posted 14:18:00.629 PST, released by
editing the same post at 14:40 PST: **about 22.1 card-minutes of the registered 30** (the session itself ran
14:18:26–14:39:43, 15 of 15 runs, exit 0, 21.3 card-minutes).*

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
where E84 had them 0.8% faster. Post hoc, both int8 differences come from the clock's climb at each process start, which
the data do not change (§3). The secondary cross-card readings came out as frozen.

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

- **Four kinds sit at the 800 MHz cap, and their deficit is the climb at each process start.** fp16 ones and int8 full read
  800 MHz on every non-ramp sample of every run; fp16 zeros and int8 zeros did in four of their six runs, and the other two
  had 12–14 samples labelled `other` (`.mhz_nonramp`, `.sus_counts`). Their sustained rate varies by run with how many of
  the window's four process starts begin with the clock's climb from 600 MHz (§3). That makes fp16 zeros the widest of the
  four, ±3.2%: one run read 781.7 MHz with two climbs in the window, and one read 800 MHz with none.
- **Random fp16 runs 3.3% faster today than in E84** (19.73 against 19.107 TFLOPS, 657 against 632 MHz) and draws 3.3 W more
  board power, at the trip in both sessions (die 65.5 °C against 65.8). It runs as fast as the heat path lets it, and
  today's heat path ran cooler (§4). Its first run started from a 47 °C die, the session's first reading, and the other two
  from 55 °C: the first read 672.8 MHz against 648.2 and 650.8. Its cell is the widest, ±4.6%.
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

- **fp16: the gap replicates, smaller.** Zeros beat random fp16 by ×1.17–1.29 sustained on card 0, above R2's 1.15.
  Today's 1.23 sits below E84's single 1.27 because random fp16 ran faster under a cooler heat path, while zeros stayed at
  the cap. E84's pair lies inside today's 95% PI for one pass pair, 1.110–1.352 (`readme-numbers.txt` § C). Against
  aifoundry2's ×1.31 the difference is −0.080 (−0.146 to −0.015), DIFFERENT, as frozen: card 0's random fp16 runs 5.7%
  faster than aifoundry2's pooled runs (19.73 against 18.66 TFLOPS), and its zeros 0.8% slower (24.29 against 24.47,
  `readme-numbers.txt` § D). Two causes are named and not separated: card 0 draws 4.5–9.8 W less board power for the same
  tiles (E84 C8), so it reaches the trip at a higher clock, and today's heat path was cooler than 31 Oct's. aifoundry2's
  pool spans four sessions over two days; card 0's is one session.
- **int8: no speed difference belongs to the data.** Both kinds hold ~790 MHz with no limit acting, in every run of both
  sessions. Today zeros ran 0.8% slower, with an interval that excludes 1; E84 had them 0.8% faster, and E84's pair lies
  **outside** today's PI for one pass pair, 0.982–1.002. An interval over three pass pairs from one session does not cover
  what moves between sessions, and here the climb at each process start moves it (§3). Against aifoundry2 the reading is
  INCONCLUSIVE at a ±0.02 bar, as frozen.

### 3. Post hoc, labelled, never a verdict: why int8's sign flipped

[`posthoc/climb.txt`](posthoc/climb.txt) and [`posthoc/climb.json`](posthoc/climb.json), from
[`posthoc/posthoc_climb.py`](posthoc/posthoc_climb.py), written after the data when R3 read SLOWER.

Between two of a run's nine processes no kernel runs for 0.33 s (median, last kernel's end to the next process's first
kernel; 0.326–0.339 s today). At each process start the clock is either still at 800 MHz, with the first 800 MHz sample
within 0.15 s (0.23 s in E84), or it climbs from 600 MHz for 0.47–1.46 s; nothing falls between. Every run's first process
climbed, 15 of 15 today and 5 of 5 in E84: it follows the sampler start, the cooling gate and a 1 s pause. Of the eight
starts after it, **40 of 120 climbed today (33%) and 13 of 40 in E84 (32%)**. The climb does not depend on the data: over
all 27 process starts of a kind, the mean climb is 0.520 s for int8 zeros and 0.511 s for int8 full today. In E84 it was
0.570 and 0.646 s, over 9 starts each.

A sustained cell reads the last 40 s, which hold four process starts. Today the int8 zeros runs had 2, 2 and 2 long climbs
among theirs, and the int8 full runs 2, 1 and 1. In E84 zeros had 1 and full 2. The int8 full runs show what one climb
costs: 83.094 TOPS with two, against 83.640 and 83.666 with one, about 0.7%. That is the size of int8's ±0.8% in both
sessions. The same count spreads fp16 zeros, 24.363, 23.940 and 24.555 TFLOPS with 1, 2 and 0 long climbs.

A third of the starts after the first is what a once-a-second check would give if every check that falls in the 0.33 s idle
gap sends the clock to 600 MHz. That is the idle heartbeat [E100](../2026-11-01-e100-idle-reset/README.md) found at the
level of behaviour on aifoundry2: every check in a gap dipped, and a fall lasts one heartbeat. Card 0 matches it in rate.
This session does not test the mechanism.

**For the blog**, the int8 sustained cell on card 0 is "the same speed as zeros, within about 1%". The 1.008 and 0.992 are
each one session's draw of process-start climbs. A cell at the cap needs replicate runs **across sessions**, or more
process starts in its window, before a ±1% difference counts.

### 4. Context: today's heat path ran 1.7 °C cooler than 31 Oct's

Each run's die, minus E84's die line at the run's board W (41.780 + 0.4753 °C per W over E84's 13 sustained runs): **−1.67 ±
0.33 °C** over the 15 runs (−2.33 to −0.43; `results.json` › `context.die_vs_e84_line`). Today's own line is 39.36 +
0.4941 °C per W. It reaches 65.5 °C at 52.9 W, against 49.9 W on E84's line, and random fp16 settled at 52.36 W today
against E84's 49.04 W. Card 0's idle die read 46–47 °C at today's first gates, against 48–50 °C at E84's
(`readme-numbers.txt` § A). Today's session started at 14:18 PST, within half an hour of E84's start by the sun (15:43 PDT
is 14:43 PST). This is the drift of section 11's item 8, on a second card, between two afternoons: about 1.7 °C at the same
board W. It moved the thermal-limited cell, random fp16, by about 25 MHz (4%). The cells at the cap moved by at most 1.1%
between the sessions, which §3's climbs account for. No inlet temperature was read.

### 5. What this changes for the blog material and the hub

- **The kinds page's speed table** (section 1, "zeros ÷ random, speed"): card 0's sustained fp16 cell becomes **×1.23
  (1.17–1.29, three runs)** at the 65 °C trip, where it says ×1.27 from one run; its int8 cell becomes **×0.99–1.01, no
  limit: equal within about 1%**, where it says ×1.01. The footnote "Card 0: E84, one run a cell" gains "fp16 and int8
  sustained: E114, three runs".
- **"Consistent with aifoundry2" becomes measured.** Card 0's fp16 sustained gap is smaller than aifoundry2's (×1.23
  against ×1.31; DIFFERENT, secondary), for two named, unseparated causes: lower board power and a cooler day. Its int8 gap
  cannot be told from aifoundry2's at ±0.02. The sign holds on both cards and in every run: zeros are never slower than
  random fp16.
- **The final critic's replicates item** (its item 8): card 0's sustained cells are re-run for fp16 and int8, three runs a
  cell, one session. Still not re-run: card 0's fp32 cells (random fp32 trips its 75 W alarm), int8 `neg_ones`, and any
  replicate across sessions on card 0.
- **Records.** `14-card-behaviour.md`: on card 0, under E84's sustained shape, a third of the process starts after a run's
  first begin with a 0.47–1.46 s climb from 600 MHz (0.33 s idle between processes; 40 of 120 today, 13 of 40 in E84), and
  every first start does. Which of a window's four starts climb decides about ±1% in a sustained cell at the cap. Card 0's
  die line moved −1.67 ± 0.33 °C between the 31 Oct and 1 Nov afternoons.

## Registered against what happened

- **No amendment, no departure from the registered design.** The start read matched E84's (65 W / 65 °C; release 1.4.0,
  BL1 and BL2 0.22.0, PMIC 1.6.1, minions 0.25.1), so `run_e114.sh start` went on to the smoke. The smoke passed its checks
  (exit 0, two runs, every launch rc 0, 65 W / 65 °C after each), so it started the session at 14:18:25.
- **The failed prediction stands as failed.** R3 was frozen as SAME_WITHIN_BAR and read SLOWER. §3's explanation is post
  hoc and changes no verdict.
- **Nothing was set on the card**: no governor move, no TDP, threshold, clock or voltage set, no reset, no PMIC command,
  no `--reset-ms`. The configuration was read, never written: 65 W / 65 °C after all 15 runs (`results.json` ›
  `context.config_after_every_run`), and at the session's start and end reads (`s1/queries.jsonl`).
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
- **Others**: card 1 was free throughout. Two login sessions of other users were counted, and the runner's two-card rule
  treats a login alone as no hit (`s1/marks.jsonl`, `logins`). Nobody is named. No device process, holder or CI job of
  anyone else appeared.

## Files

| path | what |
|---|---|
| `s1/` | the session: `session.json`, `kspeed.json`, `e84.json` (the runner's; freeze commit `59b1ad5c`), `runs.jsonl`, `launches.jsonl.gz`, `tel/*.jsonl.gz` (10 Hz sampler), `sp/*.bin` (the trace ring after each run), `queries.jsonl`, `marks.jsonl`, `run.log`, `manifest.txt`, `end.json` |
| `smoke/` | the two 2 s smoke runs (fp16 randn, int8 full; not analysed) |
| `ident/` | the read-only start reads (configuration, uptime, firmware revisions) and the closing read |
| `logs/` | the runner's stage logs on the box, the dry smoke and `e114-start.json` (E114's hashes at the start) |
| `results.json`, `reduce.txt`, `reduce.log` | the registered reduction (`reduce_e114.py`) |
| `readme-numbers.py`, `readme-numbers.txt` | every number in this README, printed from the committed files (desk, after the data) |
| `posthoc/` | the climb at each process start, post hoc: `posthoc_climb.py`, `climb.txt`, `climb.json` |

Reproduce on the Intel: `bash tools/claims-v3/e114/collect_e114.sh` (it copies the raw session from aifoundry1 and
reduces it); in this directory, `python3 readme-numbers.py > readme-numbers.txt`; in `posthoc/`, `python3
posthoc_climb.py > climb.txt`.
