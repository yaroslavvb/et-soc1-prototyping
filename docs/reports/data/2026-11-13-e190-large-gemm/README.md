# E190: one 8,192³ GEMM in fp32, fp16 and int8 on two ET-SoC-1 cards, measured beside its frozen forecast: both arms ran the whole registered order

*Fri 13 Nov 2026 (week 46), PST, Q175's card lane `card-e190`, run from aifoundry2. Registered in `508d48d9`
([`E190.md`](../../../../tools/claims-v3/e190/E190.md): the question, the frozen forecasts, the rules R0 and S1-S8, the plan, the stops), kitted
in `241726bd` ([`KIT.md`](../../../../tools/claims-v3/e190/KIT.md)) with the kit's dated note 1 `bff31df2`
([`KIT.md.dated-note-1.md`](../../../../tools/claims-v3/e190/KIT.md.dated-note-1.md),
[`E190.md.dated-note-1.md`](../../../../tools/claims-v3/e190/E190.md.dated-note-1.md),
[`CARD-LANE-BRIEF.md.dated-note-1.md`](../../../../tools/claims-v3/e190/CARD-LANE-BRIEF.md.dated-note-1.md)), all before any E190 datum.
**Arm A**: aifoundry2's card 0 under its own governor, one session, T0 1794614878, 16:07:58-16:24:57 PST, **16.98 card-minutes**. **Arm B**:
aifoundry1's card 1 as found at 600 MHz, one session, T0 1794614924, 16:08:44-16:27:55 PST, **19.18 card-minutes**. Each session ran the
whole registered order (the smoke and 18 runs), every process ended rc 0, every check of C read exact or approx, no stop line tripped, and
nothing was set: reads only. **The owner waived the day's post: his words, Fri 13 Nov 2026 ~11:30 PST.***

**Labels.** Every figure from the sessions is **measured**. Every frozen point, band, rule, stop and plan figure is **registered**
(E190.md, `forecast-e190.json`, `plan-e190.json`). The cell values in the tables below are the mean of a cell's runs in the frozen
scorer's own form, computed for this README from `data-e190.json` (desk arithmetic of the measured runs): **they are not verdicts**. The
verdicts (R0, S1-S8) are the frozen scorer's (`score_e190.py`, unchanged), which runs only on this directory once it is committed
(`rb/s24_score_e190.sh`); its output and note 1's REPORTED readings (`rb/s25_report_e190_n1.sh`) are committed beside this directory by a
later lane. Nothing here changes a frozen number.

## The answer (measured), each beside its frozen point and band (registered)

One 8,192³ GEMM (2 × 8,192³ = 1.0995 × 10¹² operations) in E136's `rgm136`, unchanged: `gemmL8x16x16` (fp32), `gemmL8x16x8` (fp16),
`gemmL8x16x4` (int8), random data (`randn` for fp32 and fp16, `full` for int8, seed 1). Seconds a GEMM = Σ wall / Σ passes over a run's
counted launches (arm A: kernel clock at or above 790 MHz; arm B: 590-610 MHz); J over idle = (p_work − p_rest) t; J with the card at rest
= p_work t; a cell = the mean of its runs.

**Bursts** (one 6 s process a run, four runs a cell):

| arm, format | runs | seconds a GEMM, measured (registered point [band]) | J over idle, measured (registered) | J with the card at rest, measured (registered) | board W in the launches / at rest, measured | minion MHz mean (lowest), measured | die start → max, °C, measured |
|---|---|---|---|---|---|---|---|
| A fp32 | 4 | **0.2947** (0.3878 [0.2762, 0.4143]) | **8.943** (10.002 [6.571, 13.526]) | **15.911** (18.898 [12.483, 23.805]) | 53.99 / 23.64 | 800.0 (800) | 52.2 → 58.0 |
| A fp16 | 4 | **0.1403** (0.1411 [0.1366, 0.1708]) | **4.243** (4.068 [3.414, 5.267]) | **7.579** (7.303 [6.338, 9.505]) | 54.01 / 23.77 | 800.0 (800) | 52.9 → 58.0 |
| A int8 | 4 | **0.0691** (0.0680 [0.0659, 0.0710]) | **1.304** (1.247 [1.073, 1.443]) | **2.950** (2.807 [2.482, 3.204]) | 42.67 / 23.80 | 800.0 (800) | 53.0 → 56.0 |
| B fp32 | 4 | **0.3177** (0.4121 [0.3008, 0.4436]) | **5.332** (5.154 [2.969, 8.042]) | **15.205** (18.792 [12.500, 23.861]) | 47.86 / 31.07 | 600.0 (600) | 53.6 → 56.8 |
| B fp16 | 4 | **0.1527** (0.1535 [0.1486, 0.1842]) | **2.512** (2.156 [1.515, 3.079]) | **7.266** (7.235 [6.223, 9.648]) | 47.58 / 31.13 | 600.0 (600) | 53.8 → 56.8 |
| B int8 | 4 | **0.0752** (0.0736 [0.0712, 0.0766]) | **0.726** (0.530 [0.347, 0.736]) | **3.070** (2.964 [2.601, 3.468]) | 40.82 / 31.17 | 600.0 (600) | 53.9 → 55.8 |

**Sustained** (twelve 6 s processes back to back, the last 40 s read, two runs a cell):

| arm, format | runs | seconds a GEMM | J over idle | J with the card at rest | board W in the launches / at rest | minion MHz mean (lowest) | die start → mean of the last 40 s, °C |
|---|---|---|---|---|---|---|---|
| A fp32 | 2 | **0.2940** (0.3878 [0.2762, 0.4143]) | **9.984** (11.174 [7.406, 14.778]) | **16.832** (20.071 [13.318, 25.058]) | 57.25 / 23.30 | 800.0 (800) | 51.0 → 62.8 |
| A fp16 | 2 | **0.1404** (0.1411 [0.1366, 0.1708]) | **4.723** (4.488 [3.821, 5.776]) | **8.155** (7.724 [6.745, 10.014]) | 58.09 / 24.45 | 800.0 (800) | 55.3 → 64.6 |
| A int8 | 2 | **0.0690** (0.0680 [0.0659, 0.0710]) | **1.388** (1.305 [1.130, 1.504]) | **3.068** (2.866 [2.539, 3.265]) | 44.44 / 24.34 | 800.0 (800) | 54.8 → 59.2 |
| B fp32 | 2 | **0.3184** (0.4121 [0.3008, 0.4436]) | **6.505** (6.173 [3.341, 9.689]) | **16.404** (19.811 [12.872, 25.508]) | 51.52 / 31.09 | 600.0 (600) | 53.5 → 62.3 |
| B fp16 | 2 | **0.1525** (0.1535 [0.1486, 0.1842]) | **3.023** (2.583 [1.721, 3.847]) | **7.830** (7.662 [6.430, 10.416]) | 51.35 / 31.52 | 600.0 (600) | 54.6 → 62.6 |
| B int8 | 2 | **0.0751** (0.0736 [0.0712, 0.0766]) | **0.824** (0.635 [0.398, 0.899]) | **3.185** (3.069 [2.652, 3.632]) | 42.39 / 31.42 | 600.0 (600) | 54.5 → 58.3 |

What the measured numbers say beside the registered ones (measured against registered; read, not scored):

- **fp32 ran about a quarter faster than its frozen point on both cards**: 0.2947 s a GEMM at 800 MHz on arm A (frozen 0.3878) and 0.3177 s
  at 600 MHz on arm B (frozen 0.4121), close to the fast end of each band, the end E190.md 4.1 kept open for "the extra fresh lines cost
  nothing". The smoke said the same before any run: fp32's cycles an op read 0.76 (arm A) and 0.77 (arm B) of the point, fp16's and int8's
  0.98-1.01. fp16 ran within 0.6% of its point on both cards, int8 1.6% (arm A) and 2.2% (arm B) slower than its point.
- **One fp32 GEMM cost 8.94 J over idle on arm A and 5.33 J on arm B**, against 10.00 and 5.15 frozen; **with the card at rest, 15.91 and
  15.21 J**, against 18.90 and 18.79: the two cards again cost nearly the same with their rest included, as frozen, and both less than frozen
  because fp32 ran faster. fp16 cost 4.24 / 2.51 J over idle (frozen 4.07 / 2.16) and int8 1.30 / 0.726 J (frozen 1.25 / 0.530); with the
  card at rest fp16 7.58 / 7.27 J and int8 2.95 / 3.07 J.
- **The watts over idle came in above their frozen points on arm B**: the board read 47.9 W (fp32) and 47.6 W (fp16) in the launches over a
  31.1 W rest, 16.8 and 16.5 W over idle, and 40.8 W in int8's, 9.7 W over idle, where the transfer from arm A froze 12.5, 14.1 and 7.2 W. On
  arm A fp32's launches drew 54.0 W over a 23.6 W rest, 30.4 W over idle, against 25.8 W frozen (E190.md 4.2 lowered fp32's watts from g4k's
  30.6 W for the slower op it forecast); fp16 30.2 W (frozen 28.8) and int8 18.9 W (frozen 18.3).
- Which of these are inside or outside their bands is the scorer's to say (S1-S4), with S5-S8; this README states no verdict.

## Registered against what happened

| item | registered (E190.md, the kit and note 1) | happened (measured) |
|---|---|---|
| the cards | A: aifoundry2 card 0, its own governor, nothing set; B: aifoundry1 card 1 as found, 600 MHz | as registered; each identity gate and identity read passed (the lines below) |
| the start config | A 65 W / 65 °C; B 65 W / 65 °C / 600 MHz | A 65 W, 65 °C, low_power, 600 MHz at rest, 519 mV; B 65 W, 65 °C, low_power, 600 MHz, 499 mV |
| the closing config | read again at the end | A as at the start; B 65 W, 65 °C, 600 MHz, 499 mV, power state managed_power (see Departures, 5) |
| the stop-path test | each line trips on live samples, its file touched, a start refused | passed on both arms (board 0.3 s, die 0.1 s) |
| the smoke | 30 s at rest; one 2 s process a format; checks exact or approx; cycles an op 50-250% of the point; the host on the arm's own card; the board 2 W or more over the rest | passed on both arms: rest A 21.96 W / 46 °C, B 29.81 W / 51 °C; cycles an op A 0.76 / 0.98 / 1.00, B 0.77 / 0.99 / 1.01 of the point; the board's rise A 28.29 / 27.88 / 9.16 W, B 16.26 / 16.58 / 10.33 W |
| the order | per arm P1, S1, P2, S2, P3, S3, P4, S4, S5, S6: 4 bursts and 2 sustained runs a cell | 18 of 18 runs on each arm, in the registered order; none refused, none cut, none skipped |
| the processes | `--seconds 6 --budget 7.5` under `timeout 10`; two failed processes in a run stop the session | 84 in the runs and 3 in the smoke on each arm, every one rc 0; the longest 7.88 s (A) and 8.25 s (B); **P1 fp32's first process (proc-00, t1_ms − t0_ms): 7.832 s on arm A, 7.581 s on arm B** |
| the die gates | A 55 / 57 °C; B min(63, rest + 3) / min(64, rest + 4), 300 s at most | B's rest die 51 °C: gates 54 / 55 °C; every run started; the longest waits 34 s (A) and 44 s (B) |
| the card time | about 33.5 (A) and 25.2 (B) card-minutes; no run after 35; cap 40 | 16.98 (A) and 19.18 (B) |
| the peaks | predicted board peak A 58.8 W at the points, 64.5 W at the bands' top (line 82 W); B 53.9 / 61.5 W (line 70 W) | board maximum A 59.91 W (16:14:26 PST), B 52.82 W (16:22:56 PST) |
| the live stops | A board above 85 W on 3 samples; B above 75 W on 3; die at or above 80 °C (the mean, or the latch `minshire[2]`) | no sample above either board line; the shires' mean at most 66 °C (A) and 64 °C (B); the latch read 70 °C on A throughout and 60-66 °C on B; no trip |
| the clocks | A bursts at 800 MHz (counted at or above 790 MHz); B 600 MHz (counted 590-610 MHz) | A: 10,173 samples, minion clock 800 MHz in 5,268, 700 in 254, 600 in 4,651 (the rest reads and the first launches of a process included); of the runs' 1,411 launches with index ≥ 0, 1,179 at or above 790 MHz, 165 between 611 and 789, 67 at 590-610. B: 600 MHz in all 11,498 samples; 1 launch with index ≥ 0 below 590 MHz |
| R0 | every check of C exact or approx | every check exact (int8) or approx (fp32, fp16), in the smoke and in every run |
| S1-S8 | the frozen scorer | run after this commit (s24); committed beside this directory by a later lane |

## The sessions' identity lines (note 1), as the logs read them

Arm A (`aifoundry2/session.log`):

```
16:07:59 config start: {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": 519} (read, nothing set); the card's identity: PCIe target /dev/et0_mgmt, physical device ID 0
16:08:00 the identity read: et-who {"other_off_card": 0, "other_on_card": 0, "ours_off_card": 0, "ours_on_card": 2, "ours_on_mgmt": 1} (counts by card), the sampler holds ['/dev/et0_mgmt']: card 0 only
16:08:33 smoke fp32: rc 0, 9 launches, check approx, cycles an op 1789.587 (0.76 of the point); the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 28.29 W over the rest on 27 samples (at least 2 W): ok
16:08:37 smoke fp16: rc 0, 7 launches, check approx, cycles an op 1695.958 (0.98 of the point); the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 27.88 W over the rest on 25 samples (at least 2 W): ok
16:08:40 smoke int8: rc 0, 7 launches, check exact, cycles an op 1655.82 (1.00 of the point); the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 9.155 W over the rest on 24 samples (at least 2 W): ok
16:08:40 smoke gate passed: the runs start
16:24:57 config end: {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": 519}
16:24:57 session end (T0 1794614878)
```

Arm B (`aifoundry1-c1/session.log`):

```
16:08:44 config start: {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": 499} (read, nothing set); the card's identity: PCIe target /dev/et1_mgmt, physical device ID 1, minion_mv 499 below 510
16:08:45 the identity read: et-who {"other_off_card": 0, "other_on_card": 0, "ours_off_card": 0, "ours_on_card": 2, "ours_on_mgmt": 1} (counts by card), the sampler holds ['/dev/et1_mgmt']: card 1 only
16:09:19 smoke fp32: rc 0, 9 launches, check approx, cycles an op 1451.152 (0.77 of the point); the host's card: its own (stderr ['/dev/et1_ops'] [1], held ['/dev/et1_ops']); the board 16.26 W over the rest on 29 samples (at least 2 W): ok
16:09:23 smoke fp16: rc 0, 7 launches, check approx, cycles an op 1394.763 (0.99 of the point); the host's card: its own (stderr ['/dev/et1_ops'] [1], held ['/dev/et1_ops']); the board 16.58 W over the rest on 26 samples (at least 2 W): ok
16:09:25 smoke int8: rc 0, 7 launches, check exact, cycles an op 1363.326 (1.01 of the point); the host's card: its own (stderr ['/dev/et1_ops'] [1], held ['/dev/et1_ops']); the board 10.33 W over the rest on 25 samples (at least 2 W): ok
16:09:25 smoke gate passed: the runs start
16:27:55 config end: {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 1, "power_state_name": "managed_power", "minion_mhz": 600, "minion_mv": 499}
16:27:55 session end (T0 1794614924)
```

No line of either log names another card, neither session wrote an `identity_trip` mark, and no line holds a gate-stop phrase ("stop-path
test failed", "smoke gate failed", "no device opened", "the gate, no launch", "would not start"). Both `identity.json` files read their
arm's card at the start and the end of the session and in each smoke process.

## Departures and notes (dated Fri 13 Nov 2026, PST)

1. **The go.** The owner's standing words of the day: "Continue the experiments." (about 11:03) and "Nobody is using aifoundry machines.
   Feel free to use all four cards." / "Feel free to use all four cards, and you don't need to post on Discord." (about 11:25-11:30). They do
   not name E190's items one by one; the round's plan named E190 on aifoundry2's card and aifoundry1's card 1. The registered plan, order,
   stops, gates, card time and cap held unchanged.
2. **No post.** The owner waived the day's post: his words, Fri 13 Nov 2026 ~11:30 PST. Every other etiquette check stayed: k6's look before
   each arm (et-who, who, uptime, the holder rule: FREE on both boxes at 16:06), the card's lock held by each session, `timeout 10` a
   process, the runner's holder reads before each run.
3. **Step 10's reading.** The readiness check found before the day that step 10 v2 (`rb/s20_wait_e190_v2.sh`, line 38) prints
   GATE-STOPPED and exits 16 for every session that passed its identity gate, also while it runs: its pattern `the card.s identity: ` also
   matches the gate's pass line. Its fix (a dated note 2) was not landed before the day, so the card lane read every step-10 call by a rule
   stated before the launches: "RUN-RUNNING" means call again; "RUN-ENDED" with "MANIFEST-WRITTEN" means ended, and a gate stop only if a
   printed session line holds one of the five gate-stop phrases above. Five calls: arm A RUNNING (16:16:53), then ENDED with 212 files in
   its manifest (16:25:01); arm B RUNNING (16:17:38, 16:26:34), then ENDED with 212 files (16:28:12). Every call exited 16 by the defect,
   and no printed line held a gate-stop phrase. The sessions themselves were not touched by it.
4. **The window.** Written at 16:05:32 by step 1: day 2026-11-13, last start 17:51, last end 19:21 PST (the go plus 1 h 45 min and 3 h 15
   min). The launches were at 16:07:58 (A) and 16:08:44 (B); both copies were back by 16:28:22.
5. **Arm B's closing config read power state `managed_power` (1)** where its start read `low_power` (3); the TDP, the threshold, the clock
   and `minion_mv` read the same at both ends. Nothing was set (reads only, below). Reported as read, not explained here.
6. **A quiet desk on aifoundry2** (16:05:59-16:25:29 PST, from arm A's look to its copy-back): the round's other lanes were held from
   starting there any process named like a device process or a session script. The count of such processes of ours read 0 before the look
   (16:05:59) and before the launch (16:07:43), and the runner's own holder reads before each run saw none (the session ran to its end).
7. **The card time came in under the plan's estimate** (16.98 and 19.18 against about 33.5 and 25.2 card-minutes): every die gate opened
   within 44 s. The rule and the cap never bound.
8. **`SHA256SUMS` is the collector's** (`collect_e190.py`, 432 files): it pins every file but this README and itself.

## The A100 side

E190 is the ET-SoC-1 side of a GEMM-against-GEMM comparison at the same 8,192³ ([`E190.md.dated-note-1.md`](../../../../tools/claims-v3/e190/E190.md.dated-note-1.md),
section 1). The lab's public A100 measurement is **E135** ([`../2026-11-02-e135-a100-kinds/`](../2026-11-02-e135-a100-kinds/)), read under its
verified correction **C1**, "The comparison set a kernel against a chip": E135's ET-SoC-1 figures were a resident loop's, the A100's a
streaming GEMM. A comparison drawn from E135's committed files and these is labelled by its kernel (here `rgm136`'s vendor-pattern GEMM),
and no chip-level contrast is drawn from a gap's size alone. No figure of E135 and none of the owner's private A100 report is quoted here.

## Device commands sent

Reads only. Each session sent `ettelem config` at its start and end and `ettelem sample` at 10 Hz, through E190's guard
(`ettelem_guard_e190.sh`, which passes `config` and `sample --seconds --every-ms` only); the device-command audit (`dmcmd_audit.py` through
`preflight_e190_v2.sh`) read **GO, 22 send sites, 0 disallowed, every one a READ** at step 2, on each box after its build, and in each
session before its first device access. No set of any kind (TDP, threshold, clock, voltage), no reset, no statistics reset, no
firmware-revisions query, no residency read, no power cycle. The hosts opened their arm's ops node only (the identity lines above).

## Privacy and the public-text scan

The collector's scrub ran on both arms (the box's home path became `~`, our own box login `<login>`; no home-directory path and no login
left), and k6's desk-path gate read CLEAN over the 433 files it wrote. The public-text scan before the commit read every text file of this
directory, the text inside both `.gz` files and this README, with the lab's sanitizer (`tools/timeline/sanitize_extracts.py`: its fixed
list and the local privacy table) plus the private-network, Mac-home, scratch and e-mail patterns, and the round's classes over this README
(names under NDA, logins and home paths, private links, access words, and the three figures of the owner's private A100 report): **0 hits**
in the collected files; this README's first draft hit once, on its own words about home paths in this section, reworded before the commit.

## Files

| path | what |
|---|---|
| `aifoundry2/` | arm A's session directory as copied back (COPY-BACK EXACT against its `MANIFEST.sha256`), scrubbed: `session.log`, `queue.json`, `identity.json`, `config-start.json`/`.err`, `config-end.json`/`.err`, `etwho-before.txt`, `etwho-identity.txt` (counts only), `stop-path.json`, `STOPTEST-board`, `STOPTEST-die`, `harness.txt`, `preflight.txt`, `sampler.err`, `smoke/<format>/` (`proc.out`, `proc.err`, `smoke.json`), `runs/<run>/` (`run.json`, `proc-NN.out`, `proc-NN.err`), `telemetry.jsonl.gz` (the 10 Hz samples), `MANIFEST.sha256`, `runner.out`, `runner.rc` |
| `aifoundry1-c1/` | arm B's, in the same form |
| `data-e190.json` | the reducer's output (`reduce_e190.py`, unchanged): the frozen scorer's input |
| `reduce-e190.txt` | the reducer's table, every run of every cell |
| `SHA256SUMS` | every file above but this README |
