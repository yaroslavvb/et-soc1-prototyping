# The effect of overheating: the card measurements (E53, OH)

The owner's request of 28 September 2026 (~09:00 PDT; to be recorded as Q61): outside research on throttling and
overheating, validated on the ET-SoC-1 where relevant, on one page called "The effect of overheating". This directory
holds the **card part** (E53): two pre-registered experiments and one by-product, run on aifoundry3 and aifoundry1's
card 1 on 28 September, and their reductions; and the **page part**: the analyses of the existing record, the page's
numbered sources and its data (section "The page" below). The page is `docs/reports/2026-09-28-effect-of-overheating.html`
(sources `docs/reports/sources/effect-of-overheating.*`).

- **OH-1**: how far the hottest of the 34 minion-shire sensors leads their mean (the value the BL2 0.20.0 governor
  compares with 65 °C; on these two cards the governor does not act: aifoundry3's is latched by its zero TDP and card 1's
  0.18.0 build never moves its clock, so the numbers are statistics of the sensors) under the most concentrated load the heater can make, one shire at full occupancy, against a
  central 2 × 2 block and idle.
- **OH-2**: nine exact-checked kernels (tensor FMA fp32/fp16/int8, a GEMV, mmbench int8 and fp32, the DRAM and mesh
  relays, a cross-shire scratchpad probe) from rest to a die mean of 82–84 °C, the DRAM refresh period at the hot end,
  and a cooling tail with one more battery once the mean reads ≤ 65 °C.
- **OH-3** (no extra card time): idle board power against the die mean, from the idle stretches of both, against the
  E44 idle laws.

The tools are [`tools/claims-v3/oh/`](../../../../tools/claims-v3/oh) (its README has the rules and how they are
enforced); the frozen predictions and decision rules are
[`tools/claims-v3/oh/prereg/PREREG.md`](../../../../tools/claims-v3/oh/prereg/PREREG.md), frozen at 10:11 PDT on
28 September before any OH-1 or OH-2 block, SHA-256
`8d620b64dc60239a104c59e3d9bd8c42cf1b4adb9e482460499dedc836f36661` (a copy is `PREREG.md` here).

**Status (28 September 2026, 12:05 PDT): done.** Both queues ended; every registered verdict is in
`reductions/verdicts.json`. Two amendments were frozen during the run, each before any data it touches (below); the
registered predictions and decision rules never changed. The current PREREG.md (amendment 2) has SHA-256
`1b34d189b5d9eb3d08d245da6dfacf042b255b9e606c9d1054b0e2d0622c7bb1`; amendment 1's was
`067a32b41014fdc65d0880008d090d022075b812c63e360d8dc831c4222ad22e`.

## Verdicts (as registered; `reductions/verdicts.json`)

| Item | Rule (short) | aifoundry3 | aifoundry1 card 1 |
|---|---|---|---|
| OH1-a | every analysed 1 s window: hottest sensor − mean ≤ +4 °C | PASS (max +3, 418 windows) | PASS (max +3, 259 windows) |
| OH1-b | median gap, one central shire ≤ central 2×2 block, per block | PASS (3 of 3 blocks: +2 vs +2) | PASS (2 of 2: +2 vs +2) |
| OH1-c | each load's median gap within ±1 °C of idle's | PASS (ONE-C +1, ONE-NE 0, B4C +1) | PASS (0, 0, 0) |
| OH2-a | 0 wrong / tensor-error / not-ok checked launches | PASS: 171 checked, 0 bad, 0 void | PASS: 171 checked, 0 bad, 0 void |
| OH2-b | work per cycle hot (80–85 °C) vs rest within 0.1 % | PASS, 18 of 18 metrics (largest 0.05 %) | INSUFFICIENT: the card never reached 80 °C |
| OH2-c | heater's implied clock 0.5994–0.5995 GHz per 5 °C band | PASS, 7 bands 50–85 °C (median 0.5995) | PASS, 5 bands 55–80 °C (median 0.5994) |
| OH2-d | gap under the whole-chip heater ≤ +4; median grows 0/+1 from 60–70 to 80–85 | PASS (max +3; 2 → 3) | max PASS (+3); growth not testable (no 80–85) |
| OH2-e | refresh period 2,325.4 ± 0.1 cycles | PASS (2,325.4 at die means 52 and 75 °C) | PASS (2,325.4 at 54 and 73 °C) |
| OH3-a | idle board power per degree within ±1.5 W of E44's law | PASS (18 bins 60–77 °C, max 0.20 W off) | PASS (10 bins 60–70 °C, max 0.22 W off) |
| OH3-b | refitted doubling interval 17–25 °C | PASS (19.4 °C; 19.4–22.2) | PASS (25.0 °C; 20.8–31.2) |

Caveats that go with the verdicts: card 1 **plateaued at a die mean of 76 °C** (hottest sensor 79 °C) under the frozen
heater (ALL24 above 75 °C, its board-power rule) at the chain duty (≤ 150 s chains, 15 s gaps), so its hot bands B3
and B4 ran at 70–76 °C and OH-2's card-1 claims stop there; aifoundry3 reached 82 °C (sensor 84). The memprobe refresh
programs of both B4 bands ran at die means of 75 and 73 °C (the band's hold had not recovered after a chain gap), not
at 82–84 °C.

## Descriptive numbers (no verdicts; `reductions/extras.json`, `extras.py`)

- **The 0.20.0 rule's decision point** (every OH window whose mean read 64–66 °C, 91 on card 1, 89 on aifoundry3): when
  the mean reads 65 °C the hottest sensor reads 66–68 °C (median 67) on both cards; at a mean of 66 °C, the first
  reading the firmware's `mean > 65` acts on, the hottest sensor reads 67–69 °C (median 68).
- **The gap by load** (1 s windows): idle median +1 to +2 (max +3); one shire at full occupancy median +2 (max +2); the
  central 2×2 block median +2 to +3 (max +3); the whole-chip heater median +2 at 55–65 °C and +2 to +3 above (aifoundry3
  +3 at 70–85 °C, card 1 +3 at 65–75 °C and +2 at 75–80 °C; max +3 inside heater launches). Over every window of the OH-2 blocks, +4 occurred 17 times (aifoundry3 12 at 75–85 °C,
  card 1 5 at 70–75 °C), never +5.
- **Work per cycle on card 1's warmest band** (70–80 °C, OH2-b's statistic): 17 of 18 metrics within 0.1 % of rest; the
  DRAM relay −0.39 % on card 1 and +0.41 % on aifoundry3 (opposite signs; its own launch-to-launch spread at rest is
  0.75 %).
- **Die voltages against the mean** (every sample, load and idle): minion rail 523 → 520 mV on aifoundry3 and 499 →
  498 mV on card 1 from 50–55 °C to the hottest band; SRAM 698 → 697 and 751 mV flat; NoC 484 → 483 and 486 mV flat.
- **Totals, aborted attempts included:** 663 checked launches (1,395 compared result records: every sweep point, tile
  set or relay counts once) on the two cards, 0 wrong, 0 tensor errors, 0 not-ok, 0 void; the hottest checked launch:
  aifoundry3 at a mean of 81 °C (hottest sensor 84 °C), card 1 at 73 °C (78 °C).
- **Card 0**, read only by the guard (5,353 samples at 1 Hz): 60–63 °C throughout; its standing SP statistics still
  read a mean maximum of 119 °C, a sensor peak-hold of 123 °C, I/O shire 118 °C and a board maximum of 75.24 W (never
  reset). Maxima during OH (every block, aborted ones included): aifoundry3 a mean of 82 °C, a sensor of 85 °C and
  67.2 W; card 1 76 °C, 79 °C and 71.6 W. No soft cap (86 °C sensor, 85 °C mean, 78 W) and no hard stop ever acted.

## What ran, where and when (28 September 2026, PDT, each host's clock)

| Time | Card | Block | What |
|---|---|---|---|
| 09:40–10:11 | — | — | tools written (`tools/claims-v3/oh/`), self-tests, V3_DRY runs of 901/201/101-103 on both hosts (no device access; `et-who` clean after each) |
| 10:11 | — | PREREG | frozen, SHA-256 `8d620b64dc60239a104c59e3d9bd8c42cf1b4adb9e482460499dedc836f36661` |
| 10:11:47–10:12:11 | aifoundry3 | p901 smoke | every battery kernel checked OK once; refresh period 2,325.4 |
| 10:12:12–10:12:43 | card 1 | p901 smoke | the same; card-0 guard 60 °C |
| 10:13–10:33 | both | p201 (aborted, `p201.aborted-a1`) | B0–B2; `oh_heat_to` held the die at its target to the time cap (a bug); stopped by hand (SIGTERM, STOP) |
| 10:39 | — | amendment 1 | the heating loop's target test (`tgt_hit`); aborted blocks out of the verdicts; SHA-256 `067a32b4…` |
| 10:39–10:59 | both | p201 (aborted, `p201.aborted-a2`) | aifoundry3 B0–B3, card 1 B0–B2; the upper targets were above what the heater reaches at the chain duty; stopped by hand |
| 11:06 | — | amendment 2 | band heating 300 s, holds 30 s, B4 target 82 °C, the plateau hold; SHA-256 `1b34d189…` |
| 11:06:41–11:39:36 | aifoundry3 | p201 | OH-2, B0–B4 and the tail: 164 checked launches |
| 11:06:46–11:43:22 | card 1 | p201 | OH-2; plateau at 76 °C from B3 on (`plateau` marks): 164 checked launches |
| 11:40:57–12:04:52 | aifoundry3 | p101, p102, p103 | OH-1, Williams rows 1–3 |
| 11:44:44–11:57:56 | card 1 | p101, p102 | OH-1, Williams rows 1–2 |

Card time with the card lock held: about 97 min on aifoundry3 and 90 min on card 1 (40 min of each in the two
aborted attempts). Nothing ran on aifoundry2 or on aifoundry1's card 0. Longest chain of back-to-back launches 147.2 s;
longest device process 4.7 s.

## Files

| Path | What |
|---|---|
| `raw/<card>/oh/p<pass>/` | every block: `block.json`, `marks.jsonl` (each step), `launches.jsonl` (every device process: kind, name, host times, rc, chain, status), `tel-<run>.jsonl.gz` (10 Hz with the 1 s statistics reset), `k.tar.gz` (every process's output), `mp/` (the refresh programs' labels, results and generator log), `stats-before.jsonl.gz` (the standing SP statistics, read before the block's first reset), `guard.jsonl.gz` (card 1: card 0's read-only guard), `binaries.json`, `code.sha256`, `prereg-lock.json`, `plan.txt`, `check.json`, `manifest.txt` (`et-lab-manifest`) |
| `raw/<card>/oh/p201.aborted-a1`, `-a2` | the stopped OH-2 attempts (status `aborted`; finalised by hand: telemetry gzipped, outputs tarred) |
| `reductions/` | `verdicts.json`, `oh1.json` (every analysed window), `oh2.json` (every checked launch and each item), `oh3.json`, `oh2-aborted.json` (the aborted attempts' checked launches), `checks.json` (`--check-pass` of every verdict block), `extras.json` (the descriptive numbers above) |
| `logs/` | the two queue logs and the two smoke logs |
| `PREREG.md` | the original freeze (10:11); the amended one is `tools/claims-v3/oh/prereg/PREREG.md` (with `PREREG-before-amendment-1.md`, `-2.md`) |
| `collect.sh` | copies the blocks from the hosts (read-only) and runs the reducer |
| `extras.py` | the descriptive numbers (`reductions/extras.json`) |
| `scripts/` | the analyses of the existing record (no card time), each writing `analysis/<name>.json` beside its printed text: `max_temps.py` (the highest readings per card over every telemetry file), `correct_vs_temp.py` (every launch record joined to telemetry: checked, wrong, tensor errors, by die temperature; this directory left out), `timing_vs_temp.py` (the heater's cycles per op by temperature; the catalogue hot against warm), `hot_minus_mean.py` (E52's and E51's hottest-minus-mean), `idle_vs_temp.py` (E44's idle laws per card), `runaway.py` (the aifoundry2 model's loop gain and equilibria), `events_vs_temp.py` (aifoundry2's kernel-log events against the die), and `derived.py` (arithmetic on cited inputs: Arrhenius factors, the mean-against-maximum wear model, TI's derating, DRAM retention scaling, the power-limit sums, the Coffin-Manson ratio of a swing to 120 °C against one to 65 °C) |
| `analysis/` | their outputs (`.json` for the page, `.txt` as printed) |
| `sources.json` | the page's 69 numbered sources (60 outside, 9 of the ET-SoC-1's own), each with its URL, what the page uses from it and a flag for second-hand reads |
| `build_overheat_data.py` | writes `overheat.json`, the page's data, from `reductions/`, `analysis/` and `sources.json`; refuses to build if the page cites a source key that `sources.json` lacks |
| `overheat.json` | the page's data |

## The page

"The effect of overheating" answers the owner's questions from outside sources first, then the ET-SoC-1's firmware and
data. Every ET number on it comes from `overheat.json`; the firmware's thresholds cite the file and line at et-platform
`ffca4cbb4` (BL2 0.20.0, the build of aifoundry2 and aifoundry3; each card's build and governor state is from
`docs/findings/14-card-behaviour.md`, and the service processor's own clock and system-temperature readouts from the DVFS
page's `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`); the temperature-inversion curves are an illustration with chosen parameters, labelled as such. Build, from
the repository root (NODE_PATH as in MIRROR.md when the worktree has no `node_modules`):

```
V=docs/reports/data/2026-09-28-overheating
for s in max_temps correct_vs_temp timing_vs_temp hot_minus_mean idle_vs_temp runaway events_vs_temp derived; do
  python3 $V/scripts/$s.py > $V/analysis/$s.txt; done
python3 $V/build_overheat_data.py
python3 scripts/build-report.py effect-of-overheating $V/overheat.json docs/reports/2026-09-28-effect-of-overheating.html
docs/reports/data/2026-09-24-report-review/tools/check_page.sh docs/reports/2026-09-28-effect-of-overheating.html   # and DARK=1
```

Reproduce: `bash collect.sh` (needs the hosts) or, from the committed raw data,
`python3 tools/claims-v3/oh/reduce.py --all --data docs/reports/data/2026-09-28-overheating/raw --out docs/reports/data/2026-09-28-overheating/reductions`
then `python3 docs/reports/data/2026-09-28-overheating/extras.py`.

## Rules and their reading (for the owner to confirm)

- **The SP statistics reset** (`ettelem --reset-ms 1000`) is the one write to the cards: it clears the SP's min/max
  statistics once a second (and sends the PMIC its statistics reset), as E52 did on these two cards. Without it no
  windowed hottest sensor exists, and the "stop at 88 °C on any sensor" rule could not be enforced. Every block first
  recorded the standing statistics read-only. Card 0's statistics were never reset.
- **The card-0 guard** (card 1 blocks) opened card 0's management node read-only at 1 Hz, with no lock and no launch, as
  E52 did; "never card 0" was read as "no work, lock, reset or configuration on card 0".
- **Claiming the machines on the lab's Discord** is a step only a person can do; it was not done.

## Not measured, and the asks for the hub

- **Transistor speed against temperature from the 34 process detectors: not measurable without a firmware change.**
  Their oscillator select is `MEASUREMENT_DISABLED`, their read functions have no caller and the PVT blocks are
  reachable only by the service processor. Ask: an SP BL2 build that selects an internal delay chain, keeps the
  31-cycle gate, samples the PDs with each temperature pass and exposes the counts (a DM command or a trace line),
  flashed by the lab admin. The registered prediction (PREREG.md): on the minion rail (~0.50–0.525 V) the count changes
  by less than ±2 % between 55 and 85 °C, more likely up than down; on a rail ≥ 0.70 V it falls, by less than 5 %.
- Not within the rules: a DLL delay-estimation sweep (M-mode, neighbourhood resets), a clock or voltage shmoo (admin
  settings), the power-limit hypothesis for the ~120 °C stop (board power near the 88 W input), a DRAM retention hold.
- Card 1 could not be taken above a 76 °C mean with the frozen heater rule (ALL24 above 75 °C) at the chain duty; its
  board stayed at or below 71.6 W, so ALL32 there (about 6 W more) would still sit under the 78 W soft cap. A hotter
  card-1 test needs ALL32 above 75 °C, longer chains or a heavier heater (the owner's call).
