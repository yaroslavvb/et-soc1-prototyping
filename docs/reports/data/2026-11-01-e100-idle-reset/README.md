# E100 data: the idle reset against launch gaps, and one long launch with no gap (Q132, Sun 1 Nov 2026, week 44, aifoundry2)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): "The governor's one-second idle reset" (old item 10).*

*Pre-registration [`tools/claims-v3/e100/`](../../../../tools/claims-v3/e100/README.md), commit `5e12c4bd` (00:49:28 PDT), pushed 00:49:33 PDT, 40 minutes before the first launch and about 10 minutes after the night's shared claim (C8). Smoke 01:30:00-01:30:21 PDT, session 01:30:21-01:53:51 PDT: 54 of 54 runs, 170 processes, every one rc 0, exit 0, 23.5 card-minutes (0.4 for the smoke). The clocks in the logs read PDT: the session ended before 02:00 PDT went back. No amendment. Nothing was set on the card.*

*Corrected after verification, Sun 1 Nov 2026, at the desk, with no card touched and nothing re-run: wrong sentences are replaced in place below, and § [Corrections after verification](#corrections-after-verification-sun-1-nov-2026) lists C1-C10. Every registered number and verdict stands.*

## Results first

1. **All five registered rules pass, the two primary ones and three secondary.** What was measured: a check once a second on the card's clock that reads idle in a gap between two kernels, and sends the clock to 600 MHz until the next check. The public firmware has a one-second heartbeat that reads "no kernel in use" in such a gap and does this. That the check is that heartbeat is read from public source and tested from outside, and any other once-a-second card-side check reading the same state would look the same from outside ([`results.json`](results.json) `.rules`, [`reduce.txt`](reduce.txt)).
2. **The falls follow the gap.** Falls in about 146 heartbeats at 800 MHz, on int8 zeros at about 35 W: 3 with no added gap, 3 with 5 ms, 10 with 20 ms, 33 with 100 ms. Each is inside its frozen band.
3. **One long launch has none.** In 50 kernels of about 4 s, none fell in 126 heartbeats inside them. N's count alone does not separate it from A0 (95% upper limit 2.4-2.9% per heartbeat against A0's 2.05%, Fisher p 0.25), so "a long kernel avoids them" rests on the next line. The gaps between N's processes did fall, 30 of 40, as D2 counts apart.
4. **The gap decides each heartbeat.** A lattice fitted on one round predicted the other round's 20 ms and 100 ms arms: all 39 heartbeats in a gap fell, and none of the 234 inside a kernel did (sensitivity 100%, specificity 100%, each round tested on the other's fit; 234 is one tied lattice's count, C6). That table holds 39 of those arms' 43 falls, and the other 4 fall to the registered rule that leaves out a point within 1 ms of a kernel's edge. Over all arms, all 61 falls first read -1.9 to +117.9 ms from the other round's lattice point, none off it: every check in a gap dipped, and every dip sits just after a check.
5. **A fall lasts one heartbeat:** median 1.10 s at 600 MHz (54 falls).
6. **No rise with the statistics reset was seen.** With it, the 20 ms arm read 12 falls against 10 without, both inside the same band (Fisher p 0.83; R's 95% count is 6.2-21, so D5 could not see less than about a factor of two). What carries it is the lattice: R's 12 falls all sit on it, 11 in a gap and 1 within an edge, while the reset's phase wanders run to run. The reset can delay the service processor by about 100 ms: two of those 12 first read about 105 and 118 ms after a lattice point that lay in the gap, each right at a reset (n = 2, post hoc, below).

**So the page's "no known firmware cause" is answered at the level of behaviour**, by a pre-registered test, on aifoundry2 under BL2 0.22.0 and minions 0.25.1, on one kind at about 35 W: the rate follows the time no kernel is in use, falls sit on a once-a-second lattice on the card's clock, and public source at one commit, `836a4ab`, has a heartbeat that does this. That is all "item 10 closes" means. It does not mean the cards' binary was shown to run that code: the cards report minions 0.25.1, and the public changelog tops out at 0.24.0 plus unreleased work. Nor is it established per card or per kind: E100 ran on one card and one kind, with E84's card 0 showing the same only in the desk reading's post-hoc view ([`2026-11-01-q132-governor-desk`](../2026-11-01-q132-governor-desk/README.md) §b).

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

The two rounds' periods came out at 1000.007 and 1000.003 ms. These are tie-breaks, not measurements: the objective ties over 1000.007-1000.016 ms in round 1 and 1000.003-1000.010 ms in round 2, and the scan keeps the lowest. Over the tied lattices the cross-round tables run 17-20, 0, 0-2, 112-117 and 20-22, 0, 0, 122-124, all PASS, sensitivity 1.000 and specificity at least 0.983, so "0 of 234" is one tie's count. The second period sits at the low edge of the registered range: the rule's text says within 0.006 ms of 1000.010, and the scorer's refinement goes 0.001 ms further. With the refinement held inside the text the table reads 39, 0, 0, 236. No process was left out for a limit in reach.

## Post hoc, labelled, never a verdict

[`posthoc_e100.py`](posthoc_e100.py), [`posthoc.txt`](posthoc.txt), [`posthoc.json`](posthoc.json), written after the registered scoring.

- **Every arm against the other round's lattice** (in a gap and fell, in a gap and no fall, in a kernel and fell, in a kernel and no fall): A0 0, 0, 1, 160; A5 2, 0, 0, 170; A20 7, 0, 0, 147; A100 32, 0, 0, 87; N 0, 0, 0, 161; R 11, 0, 0, 141. A0's one is a boundary hit: on the lattice fitted on the other round (period 1000.003 ms) the point is 5.2 ms inside the kernel, and on the whole-session lattice 0.8 ms inside.
- **The same falls, by gap** (gaps of 3 ms or more, the other round's lattice; a point in the gap: fell, stayed; no point: stayed, fell): A100 32, 0; 254, 1. A20 8, 0; 414, 2. R 11, 0; 398, 1. A5 2, 0; 429, 1. Each of those 5 no-point falls has a lattice point within 1.4 ms of the gap's edge.
- **What scores a lattice:** random phases reach sensitivity 0.9 in 1.75% of 400 draws and specificity 0.95 in 73%, so the sensitivity carries the table. Moved 10 ms the table is no longer clean.
- **One lattice over the whole session**, with a wider period range (in sample): 1000.0070 ms, table 53, 0, 0, 870. The objective is best at 1000.007-1000.008 ms, below 31 October's 1000.0098-1000.0105 ms.
- **Gaps between processes** (197 ms plus the random pause; median 751 ms), on that lattice: a lattice point in the gap against a fall, 76, 0, 0, 35. All 111 right. N's own gaps, which D2 counts apart: 30 of 40 hold a fall.
- **Where falls land.** Every fall came straight from 800 MHz, at a kernel's first instants: A0 x 2.2-3.8 ms; A5 -2.7 to 9.2 ms; A20 -0.6 to 1.4 ms; A100 -0.2 to 0.1 ms, its other 26 first read in the gap itself; R -0.4 to 1.5 ms, one first read in the gap. With a real gap the clock has fallen before the next kernel starts. One more A20 reading is stamped inside a kernel that ran whole at 0.800 GHz: the sampler's stamp comes before its slow reply, which is the `inside_kernel` 1 in `results.json`. It is not in N and not a fall inside a kernel.
- **The reset can delay the service processor; no rise in falls was seen.** R's 12 falls all sit on the other round's lattice, 11 in a gap and 1 within an edge, with `since_reset_ms` anywhere from 0 to 1000 at them.
  - Two of R's falls landed late, x 99.8 and 119.1 ms, in kernels at 0.648 and 0.658 GHz. Their lattice points lie 5.5 and 1.9 ms before those kernels' start stamps, in the gap, and the falls first read 104.5 and 117.9 ms after them, with `since_reset_ms` 0 at both. n = 2. That fits E85's 121 ms hold.
  - The first 800 reading after the first heartbeat inside a kernel: R median 0.365 s (sd 0.081), the others 0.285-0.331 s (sd 0.046-0.065).
  - R's falls at `since_reset_ms` 0 or 100: 4 of 12, against 17.7% of its readings (one-sided binomial p 0.148).
  - E85's trigger is therefore replaced: `2026-10-31-e85-camera-kinds/corrections-check.txt` C9 was suggestive only, and the falls sit on the once-a-second lattice with the reset or without.
- **The rings:** 193 POWER_IDLE records on 1.000004 s on the SP's tick, R 0.9926.

## Registered against what happened

- **Ran as registered:** every arm in both rounds, R included, no departure from the frozen files. `e100.json` and `session.json` record the sha256 of the protocol (`7e176833...`), predictions (`a6feb6ac...`), patch (`b123331e...`), runner, patched host (`4625fe5c...`) and kernel (`990807f4...`, a byte copy of the ELF E80 ran).
- **Card time:** 23.9 card-minutes against "about 30": the gates passed at once.
- **The tree on the box:** E100's files ran from `build/e100/code/`, so the shared checkout (at `0c187e12` that night) was not touched. Its `run_kspeed.py` and `run_hpl.py` match a desk machine's by sha256.
- **The first spec:** the spec of about 00:35 PDT had fixed gaps and other bands. They were changed before any data and the reason is in the pre-registration.
- **Dry run and smoke:** the scorer's self-test and `--dry` on a desk machine and the box before the slot; the smoke on the card passed `smoke_ok.py` ([`smoke/`](smoke/), [`go.log`](go.log)).
- **The order:** `5e12c4bd` was pushed at 00:49:33 PDT, 10 min 23 s after the shared claim of 00:39:10 PDT and 40 minutes before E100's first launch. E98's `c8e84226`, pushed at 00:38:23 PDT, named E100 and its slot before that claim, but not E100's rules, so the night's brief, rules pushed before the Discord claim and the first launch, was met for the launch and not for the claim. The tool README's header says "about 00:55 PDT"; it is frozen and stays.

## Card state and etiquette

- **aifoundry2, card 0**, release 1.4.0 / BL2 0.22.0 / PMIC 1.5.0 / minions 0.25.1 (E69's reading; not re-read here). Nothing was set: no governor, TDP, threshold, clock, voltage, or card reset. The statistics reset ran in arm R only, allowed by the owner's ruling of 31 October 2026.
- **Readings:** 13,934, highest die 57 C on `minshire[0]` (the array's top reads 58 C), highest board 36.52 W, none at 300 MHz. 56 `ettelem config` reads, all 65 W / 65 C. No alarm line in the rings.
- **The slot:** epoch 1793521800 to 1793524200, from the night's slot file. The smoke began in the slot's first seconds. The session released the card 16 minutes before the end. `et-who` read no holder before and after, and the runner's other-user checks had no hit.
- **The claim:** E98's lane's, `#community-lab` message `1566355908076765257` (for 8 h, until ~07:40 PST). E100 made no post and no release.

## What it changes

- **Item 10 of the kinds page's section 11 is answered at the level of behaviour, in the sense of Results above,** and "closes" means no more than that. The integration step should take this to the page and hubs in those words.
- **`docs/findings/14-card-behaviour.md`, "A one-second idle reset inside a launch":** "why it fires mid-launch is not known" and E85's "possible trigger" should give way to this chain, stated as tested from outside on one card and one kind. The climb's "launch to 800 MHz a median 0.67 s, at most 1.2 s" is the first heartbeat inside a kernel plus about 0.3 s.
- **For a measurement:** expect a fall at about 1 in 500 kernel boundaries with the sparsity host's stock launches, each costing about 0.3 s of full-speed work, with no dependence on the numbers visible in the desk reading's 25 falls, post hoc ([`ir-tests.txt`](../2026-11-01-q132-governor-desk/ir-tests.txt)). E100's own A0 reads 3 in 455 boundaries at 800 MHz, 1 in 152, 95% about 1 in 52 to 1 in 735: compatible with that, and no further support for it. A long kernel has no internal gap, and on the lattice no check inside one fell (0 of 234). Runs on a fixed grid (E63, E73, E85) hold one phase against the heartbeat, so they pile up at one time in the process.

## What a blog reader can now be told

- On aifoundry2, on int8 zeros, dips per about 146 once-a-second checks were 3, 3, 10 and 33 at added gaps of 0, 5, 20 and 100 ms, and 0 in 126 checks inside 50 kernels of about 4 s ([`results.json`](results.json) `.arms`, D2).
- A lattice fitted on one round predicted the other: 39 of 39 checks in a gap dipped, 0 of 234 inside a kernel, and all 61 dips sit just after a check ([`results.json`](results.json) D3, [`corrections-check.txt`](corrections-check.txt) C2).
- A dip lasts about 1.1 s at 600 MHz, about 0.3 s of lost full-speed work ([`results.json`](results.json) D4; the desk reading §b).
- The public firmware source describes this path: a heartbeat that looks once a second and, between two kernels, sees no kernel in use. It was tested from outside, not read from the binary (the desk reading §b).
- E100 ran one kind. In the desk reading's 25 falls across fp16, fp32 and int8, post hoc, no dependence on the format is visible ([`ir-tests.txt`](../2026-11-01-q132-governor-desk/ir-tests.txt), format p 0.49).

Not to be said from this directory: "the firmware on the card does X, proven"; "nothing to do with the numbers" sourced to E100; "predicts every dip"; "whatever the kind".

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier checked E100 after the data commit. It re-ran the frozen scorer and got `reduce.txt` and `results.json` byte for byte, recounted falls and heartbeats with its own code, and found the registration, the host change, the public chain and the card state sound. Every registered number and verdict stands, and no frozen or data file changed. It found faults in the prose built on them, all minor. Each was checked against the committed files ([`corrections-check.py`](corrections-check.py), [`corrections-check.txt`](corrections-check.txt), whose sections carry these numbers), and wrong sentences are replaced in place.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **"Nothing to do with the numbers", citing D3.** E100 ran one kind, int8 zeros, so D3 cannot say it | The blog list cites the desk reading's `ir-tests.txt`, post hoc, 25 falls, format p 0.49, and says E100 ran one kind |
| C2 | **"Predicts every dip".** D3's table holds 39 of the 43 falls in A20 and A100; 4 fall to the registered edge rule (A20 3, A100 1). Over all arms 52 sit in a gap, 1 is read inside a kernel (A0), 8 are left out. All 61 first read -1.9 to +117.9 ms from the other round's lattice point, none off it | "Every check in a gap dipped, and every dip sits just after a check": Results 4, the blog list. The gap-centred table is added under Post hoc |
| C3 | **The cause was stated flatly, and the limits omitted two.** Measured is a once-a-second check on the card's clock that reads idle in a gap. That it is `sp_iface.c`'s heartbeat is read from source. Any other once-a-second card-side check reading the same state would look the same from outside. The limits now add the version gap (0.25.1 against a public changelog at 0.24.0 plus unreleased) and one kind at about 35 W | Results 1 and the paragraph after Results 6 |
| C4 | **"The statistics reset does not cause falls."** D5's band passes up to 14: R 12 against A20 10, Fisher p 0.83, R's 95% count 6.2-21. What carries it is the lattice: R's 12 falls all sit on it, 11 in a gap and 1 within an edge, with `since_reset_ms` anywhere from 0 to 1000 | "No rise seen": Results 6, Post hoc. The two late falls now give their lattice points (5.5 and 1.9 ms before the kernels' starts, in the gap) and first readings (104.5 and 117.9 ms after them), `since_reset_ms` 0 at both. n = 2, post hoc |
| C5 | **"A0's one is a boundary hit, 1 ms off a lattice fitted on the other round."** On that lattice, period 1000.003 ms, the point is 5.2 ms inside the kernel. 0.8 ms is the whole-session lattice | Post hoc, first bullet |
| C6 | **The periods read as measurements.** 1000.007 and 1000.003 ms are tie-breaks; the objective ties over 1000.007-1000.016 and 1000.003-1000.010 ms, and the scan keeps the lowest. Over the ties the tables run 17-20, 0, 0-2, 112-117 and 20-22, 0, 0, 122-124, all PASS, so "0 of 234" is one tie's count. The rule's text says ±0.006 ms and the scorer reaches ±0.007 ms; held inside the text the table reads 39, 0, 0, 236 | The paragraph under the rules' table. The registered verdict stands |
| C7 | **N's gaps between processes were not reported,** and "a long kernel avoids them" leaned on N's 0 of 126, which alone does not separate N from A0 (95% upper limit 2.4-2.9% per heartbeat against 2.05%, Fisher p 0.25). The falls in those gaps: 30 of 40 | Results 3, Post hoc, What it changes: it rests on the lattice table, 0 of 234 |
| C8 | **The order of things.** `5e12c4bd` was pushed 10 min 23 s after the shared claim, so the night's brief, rules pushed before the Discord claim and the first launch, was not met for the claim, though E98's pre-registration had named E100 and its slot. It was met for the first launch. The tool README's header says about 00:55 PDT; the commit is 00:49:28 | The header, and a bullet under Registered against what happened. The tool README is frozen and stays |
| C9 | **"Highest die 57 C"** is `minshire[0]`; the array's top reads 58 C | Card state |
| C10 | **"Item 10 closes"** said more than was tested | Answered at the level of behaviour by a registered test, on one card and one kind, with a matching public source, not shown in the card's binary: the paragraph after Results 6, What it changes |

**Not taken as the verifier wrote it.** Its over-the-ties table read 0-1 false positives in round 1: a seventh tied table reads 19, 0, 2, 114 (specificity 0.983, still PASS). Held inside the rule's text the table reads 39, 0, 0, 236, where it wrote 235: one point, within a tie. A0's boundaries number 507 here, 455 at 800 MHz, where it wrote 508 and 1 in 169: the rate this is set beside counts boundaries at 800 MHz.

## Files

| path | what |
|---|---|
| `s1/`, `smoke/` | the sessions as run: `session.json`, `kspeed.json`, `e100.json`, `runs.jsonl`, `launches.jsonl.gz` (per-kernel records), `tel/<run>.jsonl.gz` (10 Hz), `sp/<run>.bin` (the ring after each run), `queries.jsonl`, `marks.jsonl`, `manifest.txt`, `run.log`, `end.json` |
| `go.log` | the waiter's log on the box |
| `results.json`, `reduce.txt` | the registered scoring |
| `posthoc_e100.py`, `posthoc.txt`, `posthoc.json` | the post-hoc views |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind § Corrections after verification |

Rebuild, from this directory, with Python 3 and no third-party modules:

```bash
python3 ../../../../tools/claims-v3/e100/reduce_e100.py s1 --out results.json > reduce.txt
python3 posthoc_e100.py s1 results.json --out posthoc.json > posthoc.txt
python3 corrections-check.py > corrections-check.txt
```
