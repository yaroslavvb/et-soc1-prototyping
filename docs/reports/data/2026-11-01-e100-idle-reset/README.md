# E100 data: the idle reset against launch gaps, and one long launch with no gap (Q132, Sun 1 Nov 2026, week 44, aifoundry2)

*Pre-registration [`tools/claims-v3/e100/`](../../../../tools/claims-v3/e100/README.md), commit `5e12c4bd` (00:49:28 PDT), pushed before the first launch. Smoke 01:30:00-01:30:21 PDT, session 01:30:21-01:53:51 PDT: 54 of 54 runs, 170 processes, every one rc 0, exit 0, 23.5 card-minutes (0.4 for the smoke). The clocks in the logs read PDT: the session ended before 02:00 PDT went back. No amendment. Nothing was set on the card.*

## Results first

1. **All five registered rules pass, the two primary ones and three secondary.** Item 10's cause is the one the public firmware describes: a one-second heartbeat that reads "no kernel in use" in the gap between two kernels sends the clock to its idle point until the next heartbeat ([`results.json`](results.json) `.rules`, [`reduce.txt`](reduce.txt)).
2. **The falls follow the gap.** Falls in about 146 heartbeats at 800 MHz, on int8 zeros at about 35 W: 3 with no added gap, 3 with 5 ms, 10 with 20 ms, 33 with 100 ms. Each is inside its frozen band.
3. **One long launch has none.** In 50 kernels of about 4 s, none fell in 126 heartbeats inside them.
4. **The gap decides each heartbeat.** A lattice fitted on one round predicted the other round's 20 ms and 100 ms arms: all 39 heartbeats in a gap fell, and none of the 234 inside a kernel did (sensitivity 100%, specificity 100%, each round tested on the other's fit).
5. **A fall lasts one heartbeat:** median 1.10 s at 600 MHz (54 falls).
6. **The statistics reset does not cause falls.** With it, the 20 ms arm read 12 falls against 10 without, both inside the same band. It can delay the service processor by about 100 ms: two of those 12 landed 100-119 ms into a kernel, each right at a reset (post hoc, below).

**So item 10 closes**, on aifoundry2 under BL2 0.22.0 and minions 0.25.1. Two limits stay: the chain is read from public source at `836a4ab` and tested from outside, and the cards' binary was not read; and E100 ran on one card, with E84's card 0 showing the same in the desk reading's post-hoc view ([`2026-11-01-q132-governor-desk`](../2026-11-01-q132-governor-desk/README.md) §b).

## The arms

Int8 zeros, 1024 minions. Added gaps are random, uniform from 0 to twice the mean. A process is 7.5 s of kernels of 850,000 iterations (0.338 s at 800 MHz), N one kernel of 10,000,000 (3.98-4.29 s). Two rounds in opposite order. From [`results.json`](results.json) `.arms` and [`posthoc.txt`](posthoc.txt) view 1:

| arm | mean added gap | measured gap, mean | idle share of the time | processes | heartbeats | falls (round 1 + 2) | falls per heartbeat | predicted falls | frozen band | in band |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| A0 | 0 | 1.27 ms | 0.57% | 24 | 146.3 | **3** (1 + 2) | 2.05% | 0.96 | 0-4 | yes |
| A5 | 5 ms | 6.36 ms | 2.02% | 24 | 145.8 | **3** (1 + 2) | 2.06% | 3.59 | 0-7 | yes |
| A20 | 20 ms | 21.42 ms | 6.00% | 24 | 146.6 | **10** (5 + 5) | 6.82% | 8.51 | 3-14 | yes |
| A100 | 100 ms | 101.78 ms | 21.90% | 24 | 147.7 | **33** (17 + 16) | 22.34% | 29.78 | 20-42 | yes |
| N | no gap inside | | 0 | 50 | 126.1 | **0** (0 + 0) | 0 | 0 | 0 | yes |
| R | 20 ms, with `--reset-ms 1000` | 21.11 ms | 5.87% | 24 | 146.7 | **12** (5 + 7) | 8.18% | 8.51 | 3-14 | yes |

The kernel counters agree: 3, 3, 10, 33, 0 and 10. R's other two are the late falls of view 8, whose kernels ran too long at 800 MHz for the kernel rule. Idle share adds 0.7 ms per gap to the host's stamps, the difference between the 2.0 ms zone and the 1.29 ms stamp gap of the desk reading.

**A0 and A5 cannot be told apart here:** 3 falls each. A0's 3 sits above its 0.96 (one-sided Poisson p about 0.07) and inside its band. The rise is clear from A5 to A20 to A100, a factor of 11.

## The rules, as registered

| rule | verdict | the numbers |
|---|---|---|
| **D1** the rate follows the gap (primary) | **PASS** | A100 33 in 20-42, A20 10 in 3-14, A0 3 in 0-4, bands recomputed at the heartbeats exposed |
| **D2** one long launch has no fall inside (primary) | **PASS** | 0 falls inside a kernel over 126.1 heartbeats, against a floor of 100 |
| **D3** the gap decides each heartbeat (secondary) | **PASS** | across the rounds, A20 and A100: in a gap and fell 39, in a gap and no fall 0, in a kernel and fell 0, in a kernel and no fall 234. Sensitivity 1.000, specificity 1.000; needed 0.90 and 0.95. Each way: 17, 0, 0, 112 and 22, 0, 0, 122 |
| **D4** a fall lasts one heartbeat (secondary) | **PASS** | first 600 reading to first higher reading: median 1.101 s over 54 (needed 1.0-1.25). A100: 2 of 31 last 1.9 s or more, 6.5% (needed 3-35%, model 13.9%) |
| **D5** the statistics reset (secondary) | **PASS** | R's 12 falls in A20's band, 3-14 |

The two rounds' periods came out at 1000.007 and 1000.003 ms. The second sits at the low edge of the registered range (1000.004-1000.016 ms, refined by ±0.001 ms), and its table is clean anyway. No process was left out for a limit in reach.

## Post hoc, labelled, never a verdict

[`posthoc_e100.py`](posthoc_e100.py), [`posthoc.txt`](posthoc.txt), [`posthoc.json`](posthoc.json), written after the registered scoring.

- **Every arm against the other round's lattice** (in a gap and fell, in a gap and no fall, in a kernel and fell, in a kernel and no fall): A0 0, 0, 1, 160; A5 2, 0, 0, 170; A20 7, 0, 0, 147; A100 32, 0, 0, 87; N 0, 0, 0, 161; R 11, 0, 0, 141. A0's one is a boundary hit, 1 ms off a lattice fitted on the other round.
- **One lattice over the whole session**, with a wider period range (in sample): 1000.0070 ms, table 53, 0, 0, 870.
- **Gaps between processes** (197 ms plus the random pause; median 751 ms), on that lattice: a lattice point in the gap against a fall, 76, 0, 0, 35. All 111 right.
- **Where falls land.** Every fall came straight from 800 MHz, at a kernel's first instants: A0 x 2.2-3.8 ms; A5 -2.7 to 9.2 ms; A20 -0.6 to 1.4 ms; A100 -0.2 to 0.1 ms, its other 26 first read in the gap itself; R -0.4 to 1.5 ms, one first read in the gap. With a real gap the clock has fallen before the next kernel starts. One more A20 reading is stamped inside a kernel that ran whole at 0.800 GHz: the sampler's stamp comes before its slow reply, which is the `inside_kernel` 1 in `results.json`. It is not in N and not a fall inside a kernel.
- **The reset delays the service processor; it does not cause falls.**
  - Two of R's falls landed late, x 99.8 and 119.1 ms, in kernels at 0.648 and 0.658 GHz, with `since_reset_ms` 0 at both. That fits E85's 121 ms hold.
  - The first 800 reading after the first heartbeat inside a kernel: R median 0.365 s (sd 0.081), the others 0.285-0.331 s (sd 0.046-0.065).
  - R's falls at `since_reset_ms` 0 or 100: 4 of 12, against 17.7% of its readings (one-sided binomial p 0.148).
  - E85's trigger is therefore replaced: `2026-10-31-e85-camera-kinds/corrections-check.txt` C9 was suggestive only, and the falls sit on the heartbeat with the reset or without.
- **The rings:** 193 POWER_IDLE records on 1.000004 s on the SP's tick, R 0.9926.

## Registered against what happened

- **Ran as registered:** every arm in both rounds, R included, no departure from the frozen files. `e100.json` and `session.json` record the sha256 of the protocol (`7e176833...`), predictions (`a6feb6ac...`), patch (`b123331e...`), runner, patched host (`4625fe5c...`) and kernel (`990807f4...`, a byte copy of the ELF E80 ran).
- **Card time:** 23.9 card-minutes against "about 30": the gates passed at once.
- **The tree on the box:** E100's files ran from `build/e100/code/`, so the shared checkout (at `0c187e12` that night) was not touched. Its `run_kspeed.py` and `run_hpl.py` match the Intel's by sha256.
- **The first spec:** the spec of about 00:35 PDT had fixed gaps and other bands. They were changed before any data and the reason is in the pre-registration.
- **Dry run and smoke:** the scorer's self-test and `--dry` on the Intel and the box before the slot; the smoke on the card passed `smoke_ok.py` ([`smoke/`](smoke/), [`go.log`](go.log)).

## Card state and etiquette

- **aifoundry2, card 0**, release 1.4.0 / BL2 0.22.0 / PMIC 1.5.0 / minions 0.25.1 (E69's reading; not re-read here). Nothing was set: no governor, TDP, threshold, clock, voltage, or card reset. The statistics reset ran in arm R only, allowed by the owner's ruling of 31 October 2026.
- **Readings:** 13,934, highest die 57 C, highest board 36.52 W, none at 300 MHz. 56 `ettelem config` reads, all 65 W / 65 C. No alarm line in the rings.
- **The slot:** epoch 1793521800 to 1793524200, from the night's slot file. The smoke began in the slot's first seconds. The session released the card 16 minutes before the end. `et-who` read no holder before and after, and the runner's other-user checks had no hit.
- **The claim:** E98's lane's, `#community-lab` message `1566355908076765257` (for 8 h, until ~07:40 PST). E100 made no post and no release.

## What it changes

- **Item 10 of the kinds page's section 11 closes.** The integration step should take this to the page and hubs.
- **`docs/findings/14-card-behaviour.md`, "A one-second idle reset inside a launch":** "why it fires mid-launch is not known" and E85's "possible trigger" should give way to this chain. The climb's "launch to 800 MHz a median 0.67 s, at most 1.2 s" is the first heartbeat inside a kernel plus about 0.3 s.
- **For a measurement:** expect a fall at about 1 in 500 kernel boundaries with the sparsity host's stock launches, each costing about 0.3 s of full-speed work, wherever the numbers are. A long kernel has no internal gap, so it avoids them. Runs on a fixed grid (E63, E73, E85) hold one phase against the heartbeat, so they pile up at one time in the process.

## What a blog reader can now be told

- The one-second dip has nothing to do with the numbers: the firmware checks once a second whether a kernel is running, and between two kernels the answer is no ([`results.json`](results.json) D3).
- Adding idle time between kernels raises the dips: 3, 3, 10 and 33 per 146 checks for gaps of 0, 5, 20 and 100 ms ([`results.json`](results.json) `.arms`).
- One long kernel has none: 0 in 126 checks ([`results.json`](results.json) D2).
- Knowing when the checks fall predicts every dip: all 39 checks in a gap dipped and none of the 234 inside a kernel did ([`results.json`](results.json) D3).
- A dip lasts about 1.1 s at 600 MHz, about 0.3 s of lost full-speed work ([`results.json`](results.json) D4; the desk reading §b).

## Files

| path | what |
|---|---|
| `s1/`, `smoke/` | the sessions as run: `session.json`, `kspeed.json`, `e100.json`, `runs.jsonl`, `launches.jsonl.gz` (per-kernel records), `tel/<run>.jsonl.gz` (10 Hz), `sp/<run>.bin` (the ring after each run), `queries.jsonl`, `marks.jsonl`, `manifest.txt`, `run.log`, `end.json` |
| `go.log` | the waiter's log on the box |
| `results.json`, `reduce.txt` | the registered scoring |
| `posthoc_e100.py`, `posthoc.txt`, `posthoc.json` | the post-hoc views |

Rebuild, from this directory, with Python 3 and no third-party modules:

```bash
python3 ../../../../tools/claims-v3/e100/reduce_e100.py s1 --out results.json > reduce.txt
python3 posthoc_e100.py s1 results.json --out posthoc.json > posthoc.txt
```
