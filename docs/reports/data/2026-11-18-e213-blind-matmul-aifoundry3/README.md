# E213 arm A, 2026-11-18, aifoundry3 card 0 at its pinned 600 MHz: MM1-v3's blind matmul day (90 points, 87 scored): RAN FULL (the smoke, the stop-path test, 105 of 105 runs)

*Wed 18 Nov 2026 (week 47), PST. E213, registered before any datum (`291c8201`, [`E213.md`](../../../../tools/claims-v3/e213/E213.md) with Amendment A1, made before the land; arm B's freeze line), kitted (`6efdb002`, [`KIT.md`](../../../../tools/claims-v3/e213/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e213/CARD-LANE-BRIEF.md)), verified (verify-e213: HOLDS WITH FIXES; fix-e213 before the land; land-e213: LANDED) and readiness-checked (ready-e213: READY WITH GAPS), all before any E213 datum; run on the owner's go (departure 1). **Arm A's freeze line: MM1-v3's land `b1493082`, pushed 20:52:46 PST Tue 17 Nov 2026**; step 0 read it on GitHub main ("STEP0-E213 arm A: 5 of 5 as stated (HEAD 8e91dda6df38, GitHub main 8e91dda6df38)"; the anchor read "115 of 115 as stated" at HEAD `8e91dda6` = GitHub main). rgm136 (E136's binary, unchanged) and rgm211 (E211's) built today on the box through their kernel gates (KERNEL OK: rgm136: rgm136 gemmL: rgm136, .text 61315bf6a449c282... the pinned one; ELF ff2723b81e2ce409... not the desk build's (sections the card never loads differ), its loadable identity 649d40793e459e51... the pinned; KERNEL OK: rgm211: rgm211 gemmLn: rgm211, .text 82c7980716a0f0ca... the pinned one; ELF 70c066e830883d51... not the desk build's (sections the card never loads differ), its loadable identity 1351a569e4a200cb... the pinne; KERNEL OK: rgm136: rgm136 gemmL: rgm136, .text 61315bf6a449c282... the pinned one; ELF ff2723b81e2ce409... not the desk build's (sections th; KERNEL OK: rgm211: rgm211 gemmLn: rgm211, .text 82c7980716a0f0ca... the pinned one; ELF 70c066e830883d51... not th); every process gated by its loop's own ELF (THE IDENTITY GATE PER PROCESS, the four families). Q216's card lane `card-e213a`, orchestrated from aifoundry2. Nothing was set on the card.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every point, order, window, threshold, stop and the cap is **registered** (E213.md; the kit). The per-point means, the millisecond and millijoule figures below are **desk arithmetic of the measured records** by the scorer's registered definitions (a run's wall cycles an op = cycles_gemm / ops a minion a GEMM), not verdicts. **The forecasts are BLIND** (MM1-v3's frozen at its land `b1493082`, `tools/matmul/mm1/v3/out/mm1_v3_e213.csv` `01a2fdae...`); no forecast number is quoted here. **No score is here:** the frozen scorer (step 13, `score_e213.py`) runs on this directory only after it is committed, and a later lane commits its words beside it. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures, dated (Wed 18 Nov 2026, PST; placed before the results, as the round's go asks)

1. **The go, his words, verbatim (quoted without links).** Sun 15 Nov 2026: **10:05:42** "continue, all machines are up"; **10:22:36** "don't worry about discord post, just use the machines, nobody is using them"; **17:21:16** "Feel free to use more cards in parallel, I don't need to reserve them"; **"Try again"** (received at or before 21:28:59; its exact second not known); "don't worry about hitting the limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before 21:51:09); "Make sure to incorporate suggestions from Fable when planning experiments" (received between 21:55 and 22:07:09). Mon 16 Nov 2026, received at or before 09:48:24 (a voice transcription in which "matte mold" is the matmul and "FME" the tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation." Tue 17 Nov 2026: "Try again" (read at 06:40:56) and "Continue from where you left off" (twice, at or before 16:4x). Beside them, reports of his words posted on the round's Discussion by the model session (not his own text): Mon 16 Nov 11:01:08 "There's no usage limit; feel free to use all the cards without restriction, since they look free every time I check the dashboard."; Mon 16 Nov 23:15:25 "There's no deadline; use the cards all night. Nobody else is using them except my lab session, which coordinates with you here." **His words name no experiment: the registered items are taken as their defaults** (E213.md 6): aifoundry3 card 0 at its pinned 600 MHz as found, reads only, nothing set; 46.3 card-minutes planned, no run after 60, cap 70; the 40-minute rest; one session; the window of E213.md 6. E213 is MM1-v3's blind matmul day, as his words of Mon 16 Nov ask ("just go as far as possible ... on the matmul operation").
2. **G = the booking on its day:** the card lane's `book.sh take aifoundry3 card-e213a` printed BOOKED at **06:32:00 PST** Wed 18 Nov 2026: last start G+1:30 and last end G+3:30 (E213.md 6), each rounded up to the whole minute: **08:02 and 10:02 PST** (`s02_window_e213.sh A 2026-11-18 08:02 10:02`, written by step 1). The session's first card command at 06:37:09 (before the last start) and its end at 07:19:59 (before the last end).
3. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE), step 7's reads (et-who clean), the session's holder check before its first card command, card 0's lock held for the session, and a plain `timeout 10` (never `-k`) on every device process.
4. **The host's package counter: not read** (E213.md 6): no step, option or code of the kit reads it (step 0's anchor G6: no line under `tools/claims-v3/e213` names it).
5. **The rest.** Our last session on aifoundry3 before E213, from the card lanes' own records: session 2026-11-17 13:21:34 -> 2026-11-17 13:39:35 PST (session end; the round folder card-e211/rb-e211/e211-raw/A/T1794950494-A/session.log); the lane's clock read before the booking: "1012 minutes since our latest session on aifoundry3 ended (2026-11-17 13:39:35 PST, session end; the round folder card-e211/rb-e211/e211-raw/A/T1794950494-A/session.log); the rest opened at 2026-11-17 14:19:35 PST". E213's committed rest rule, read on the box, printed at step 7 "1017 minutes since E211's session end (2026-11-17 13:39:35 PST; dry sessions and blocks that opened no device skipped)" and at step 9 "1017 minutes since E211's session end (2026-11-17 13:39:35 PST; dry sessions and blocks that opened no device skipped)" (40 required). Step 7's config read at 06:36:44 is reported apart from the session's card time.
6. **The never-run search, repeated right before the first card command** (step 6n, E213.md 4; its report, judgement and labels in this directory): at 06:36:36 PST, "NEVER-RUN-E213 arm A: 87 of 87 scored points never ran on any card (scan 334545d51fb7, 70775 files); ran before the freeze line (MM1-v3's land b1493082), labelled: none; ran after it (REPORTED, kept): none". Step 7's config read followed within 30 minutes. aifoundry3's and aifoundry1's own disks are not searched (as registered). It labelled no point: every scored point keeps its registered label (blind). It is REPORTED and changes no rule.
7. **"Reads only" is true of the management node**: as every runtime creation of the lab's runtime does, each host's creation also sends the ops node's abort on the card's submission queues; harmless on a card held alone (et-who empty, card 0's lock held, aifoundry3 has one card).
8. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, numerical steps single-threaded inside the round's CPU slots; the box ran the session with its own `python3` (3.12.3 by ready-e213's read-only look at 04:40:28 PST; not re-read by this lane). The orchestrating session is the round's session on its yvb3 Claude account. aifoundry2's own card was not touched.
9. **The model session's sealed forecast.** The model session's sealed forecast of E213's 131 points and 117 cases on both arms (sha256 `76f0b2f4643b8d2a599085041d6fcc5f063345465687f51ec75f7363c0b20325`, posted on the round's coordination thread at 05:23:27 PST Wed 18 Nov 2026, before either arm booked) was registered in `tools/claims-v3/sealed-e213/e213-freeze-lines.md` by `8e91dda6` (committed 06:21:46 PST) before this arm's booking (06:32:00) and its first card command; step 0's S1 read it registered (1 of 1). Its numbers are not quoted here (its sha256 only); the lab does not score it.
10. **The die line's hottest sensor** is read as E206.md's amendment A1 item 1 registers it and plan-e213.json adopts it (KIT.md section 4 item 1; not a departure): the latch (`minshire[2]`) read 51 C at the session's first sample and 61 C at its highest (lowest 51 C); the line trips on the shires' mean, or on the latch only once it has risen during the session above the lowest value it read. **The latch was live this time:** it reset when aifoundry3 rebooted at about 16:46 PST Tue 17 Nov 2026 (every committed sample before read 87 C, constant), so the 70 C line could trip on it; the orchestrator kept the registered line as landed (its answer 6, Wed 18 Nov 2026 05:5x PST: a trip is a registered, safe-side stop that keeps the runs done).
11. **The first config read since the reboot.** All three lab boxes rebooted between about 16:33 and 16:46 PST Tue 17 Nov 2026; step 7's config read was the first of this card since (ready-e213's GAP 2): aifoundry3: manifest kept on the box (build/q141k/), config TDP 0 W / 65 C / 600 MHz, et-who clean.
12. **The seal hold.** The orchestrator held aifoundry3's booking for that seal (`orch-hold-e213-seal`, from 05:52:24 PST until the seal's registration); the queue read QUEUE BUSY until 06:31:50 PST and this arm booked at once after it (E213.md section 0; the orchestrator's answer 2). Arm B (aifoundry1 card 1) is another card lane's; THE ONE-LAB RULE kept the two arms' desk and collect spans apart in LAB.

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | 42.83 (planned 46.3; no run after 60, cap 70); session 06:37:09-07:19:59 PST (T0 1795012628); step 7's config read at 06:36:44, reported apart | measured (the session's clock) |
| step 7's config read (before the session; k6's step 7, E128's guard, card 0's lock) | aifoundry3: manifest kept on the box (build/q141k/), config TDP 0 W / 65 C / 600 MHz, et-who clean | measured (READ) |
| the smoke: s01 gemmL2x2x2 (rgm136), s02 gemmLn2x2x2 (rgm211), s03 gemmLnc2x2x2 (rgm211's host on rgm136's ELF), s04 gemmL2x2x2 (rgm211's host and ELF: the family 'rgm211 gemmL''s own smoke, E213.md A1), fp32 random, 2 s each; then the stop-path test | 06:37:39 s01: the identity gate (rgm136 gemmL): GATE OK: rgm136 gemmL: rgm136, .text 61315bf6a449c282... the pinned one; ELF ff2723b81e2ce409... not the desk build's (sections the card never loads differ), its loadable identity 649d40793e459e51... the pinned one; 06:37:42 s01: the identity gate GATE OK; rc 0, 7 launches, check approx, no walk (rgm136's host prints none), the counter's mean 819.274 cycles an op (R0's band 200-4000: in; the check record's 819.275); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 24.29 W over the rest on 26 samples (at least 2 W): ok; 06:37:42 s02: the identity gate (rgm211 gemmLn): GATE OK: rgm211 gemmLn: rgm211, .text 82c7980716a0f0ca... the pinned one; ELF 70c066e830883d51... not the desk build's (sections the card never loads differ), its loadable identity 1351a569e4a200cb... the pinned one; 06:37:45 s02: the identity gate GATE OK; rc 0, 7 launches, check approx, walk nm on every launch, walk_ok true, walk_launches_bad 0, the counter's mean 754.505 cycles an op (R0's band 200-4000: in; the check record's 754.505); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 26.59 W over the rest on 26 samples (at least 2 W; 06:37:45 s03: the identity gate (rgm136 gemmLnc): GATE OK: rgm136 gemmLnc: rgm136, .text 61315bf6a449c282... the pinned one; ELF ff2723b81e2ce409... not the desk build's (sections the card never loads differ), its loadable identity 649d40793e459e51... the pinned one; 06:37:47 s03: the identity gate GATE OK; rc 0, 6 launches, check approx, walk mn on every launch, walk_ok true, walk_launches_bad 0, the counter's mean 755.0335 cycles an op (R0's band 200-4000: in; the check record's 754.883); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 35.65 W over the rest on 22 samples (at least 2 ; 06:37:47 s04: the identity gate (rgm211 gemmL): GATE OK: rgm211 gemmL: rgm211, .text 82c7980716a0f0ca... the pinned one; ELF 70c066e830883d51... not the desk build's (sections the card never loads differ), its loadable identity 1351a569e4a200cb... the pinned one; 06:37:50 s04: the identity gate GATE OK; rc 0, 7 launches, check approx, walk mn on every launch, walk_ok true, walk_launches_bad 0, the counter's mean 788.551 cycles an op (R0's band 200-4000: in; the check record's 788.556); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 26.22 W over the rest on 26 samples (at least 2 W; stop-path test passed: board tripped in 0.3 s, its file touched, start refused; die tripped in 0.1 s, its file touched, start refused; smoke gate passed: the runs start | measured |
| THE FAMILY SMOKE (E213.md A1, its own stop path) | s04 good (no family dropped; queue.json families_dropped {}) | measured |
| THE IDENTITY GATE PER PROCESS | 109 of 109 processes "GATE OK" (the smoke's and the runs'); by loop: rgm136 gemmL: GATE OK x91; rgm136 gemmLnc: GATE OK x7; rgm211 gemmL: GATE OK x6; rgm211 gemmLn: GATE OK x5 | measured (the gate's reading of the box's ELFs) |
| THE WALK CHECK | 18 of 18 rgm211-host processes ('rgm211 gemmLn': nm; 'rgm136 gemmLnc' and 'rgm211 gemmL': mn) with the registered walk on every counted launch, walk_ok true on every one and walk_launches_bad 0 | measured |
| runs: planned, started, with counted launches, not started | 105 / 105 / 105 / 0; runs without a counted launch: 0; not started: none; counted runs whose record differs from the point's: 0 | measured |
| how the session ended | session end (T0 1795012628); queue.json stop: none; runner rc 0 (runner.rc); HUNG lines: 0 | measured |
| telemetry samples, and those at 600 MHz | 25,659 / 25,659; off the clock: 0 | measured |
| board power, peak (the session; each family's run windows); the shires' mean, peak; the latch (minshire[2]) at the start and its highest | 64.22 W at 07:12:07; A:I 49.2 W (104-pass2-a004); A:I+P 49.06 W (084-pass1-a006); A:R 40.96 W (030-pass1-a019); A:R+P 40.37 W (095-pass2-a030); A:E 39.05 W (042-pass1-a036); A:C 50.17 W (014-pass1-a044); A:M 27.36 W (051-pass1-a061); A:P 64.22 W (087-pass1-a075); tie 44.17 W (092-tie-t01); the smoke 59.1 W; 58 C at 07:12:07; 51 C / 61 C at 07:19:58 (the stops: above 70 W on 3 samples, 70 C; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it; the line 65 W; the planning peak 52.01 W at a073) | measured |
| the session's rest reading (the smoke's) | smoke rest: 299 samples, board 22.68 W, die 47 C (the latch [51]); the die gate 51.0 C | measured |
| the opening and closing configuration reads | {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523} | measured (READ) |
| the identity lines | the card's identity: PCIe target /dev/et0_mgmt, physical device ID 0; the identity read: et-who {"other_off_card": 0, "other_on_card": 0, "ours_off_card": 0, "ours_on_card": 2, "ours_on_mgmt": 1} (counts by card), the sampler holds ['/dev/et0_mgmt']: card 0 only | measured |
| every check of C the hosts printed | {"approx": 59, "exact": 50}; runs that printed none (the reducer's `checks_missing`): 0 | measured |
| the session log's stop, drop, identity and HUNG lines | none | measured |
| per point (below; `reduce-e213.txt`) | 90 of 90 points with counted runs; no data: none | measured (reduce_e213.py) |
| the never-run search repeated right before the first card command (step 6n; `neverrun-e213-card.txt`, `.json`; `judge-e213-card.txt`, `.json`; `labels-e213.json`) | NEVER-RUN-E213 arm A: 87 of 87 scored points never ran on any card (scan 334545d51fb7, 70775 files); ran before the freeze line (MM1-v3's land b1493082), labelled: none; ran after it (REPORTED, kept): none; not searched, as registered: the boxes' own disks | a desk read; the labels go to the scorer (`--labels`) at step 13 |

### The smoke (each process's reduced values; the reducer's, `reduce-e213.txt` and `data-e213.json`)

| point | arm | loop | wall cycles an op | counter-mean cycles an op | ms a GEMM | p_work W | p_rest W | mJ over idle / at rest |
|---|---|---|---|---|---|---|---|---|
| s01 | `gemmL2x2x2` fp32 | rgm136 gemmL | 904.67 | 819.27 | 0.77255 | 47.02 | 22.69 | 18.8 / 36.33 |
| s02 | `gemmLn2x2x2` fp32 | rgm211 gemmLn | 855.85 | 754.5 | 0.73092 | 49.27 | 23.86 | 18.58 / 36.01 |
| s03 | `gemmLnc2x2x2` fp32 | rgm136 gemmLnc | 875.58 | 755.03 | 0.74803 | 58.33 | 47.23 | 8.303 / 43.63 |
| s04 | `gemmL2x2x2` fp32 | rgm211 gemmL | 887.99 | 788.55 | 0.75832 | 48.91 | 49.33 | -0.3185 / 37.09 |

The reducer's p_rest for a smoke process is the 5 s before it: the end of the session's rest reading for s01, and the previous smoke process's tail for s02-s04 (`reduce_e213.py`'s docstring, the kit's reading), so the smoke's "over idle" figures for s02-s04 sit on a warm base (s04's is below zero for that reason). The runner's smoke gate read each process's rise over the session's rest reading (smoke rest: 299 samples, board 22.68 W, die 47 C (the latch [51]); the die gate 51.0 C): s01 24.29 W (26 samples); s02 26.59 W (26 samples); s03 35.65 W (22 samples); s04 26.22 W (26 samples).

### Per point (each point's runs with counted launches; the reducer's values), by MM1-v3's families

J over idle = (p_work - p_rest) x t_gemm and J with the card at rest = p_work x t_gemm, a GEMM (the scorer's form); seconds in ms and joules in mJ a GEMM; wall cycles an op = cycles_gemm (the median of the slowest minion's counter a GEMM over the counted launches) over the point's ops a minion a GEMM; the counter's mean = the host's cycles_per_op (the median over the counted launches); the die = the shires' mean at the run's start. Desk arithmetic of measured records; means over the point's runs.

| point | family | arm | format, data | mask | loop | runs (n) | wall cycles an op | counter-mean cycles an op | ms a GEMM | p_work W | p_rest W | mJ over idle / at rest | die C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a001 | A:I | `gemmL2x1x2` | int8 random | 0xffffffff | rgm136 gemmL | 46 | 953.81 | 844.76 | 0.40731 | 33.77 | 23.71 | 4.098 / 13.75 | 51 |
| a002 | A:I | `gemmL2x1x2` | fp32 random | 0xffffffff | rgm136 gemmL | 7 | 898.56 | 805.71 | 0.3837 | 48.33 | 23.44 | 9.55 / 18.54 | 50 |
| a003 | A:I | `gemmL4x1x2` | int8 random | 0xffffffff | rgm136 gemmL | 6 | 953.77 | 844.79 | 0.81458 | 33.47 | 23.34 | 8.256 / 27.26 | 50 |
| a004 | A:I | `gemmL4x1x2` | fp32 random | 0xffffffff | rgm136 gemmL | 13, 104 | 898.41 | 805.72 | 0.76732 | 48.61 | 23.63 | 19.16 / 37.3 | 51 |
| a005 | A:I | `gemmL3x1x3` | int8 random | 0xffffffff | rgm136 gemmL | 3 | 970 | 866 | 0.93196 | 33.77 | 23.38 | 9.683 / 31.47 | 50 |
| a007 | A:I | `gemmL1x2x7` | int8 random | 0xffffffff | rgm136 gemmL | 41 | 969.69 | 866.41 | 1.4494 | 34.01 | 23.71 | 14.93 / 49.29 | 51 |
| a008 | A:I | `gemmL1x2x7` | fp32 random | 0xffffffff | rgm136 gemmL | 20 | 910.09 | 831.38 | 1.3602 | 48.29 | 23.71 | 33.43 / 65.69 | 51 |
| a009 | A:I | `gemmL1x2x11` | int8 random | 0xffffffff | rgm136 gemmL | 27 | 1389.9 | 1389.8 | 3.2642 | 32.32 | 23.71 | 28.1 / 105.5 | 51 |
| a010 | A:I | `gemmL1x2x11` | fp32 random | 0xffffffff | rgm136 gemmL | 36 | 1365 | 1364.9 | 3.2058 | 40.59 | 23.72 | 54.08 / 130.1 | 51 |
| a011 | A:I | `gemmL2x2x7` | int8 random | 0xffffffff | rgm136 gemmL | 12 | 1205.9 | 1205.8 | 3.6054 | 32.6 | 23.71 | 32.05 / 117.5 | 51 |
| a012 | A:I | `gemmL2x2x7` | fp32 random | 0xffffffff | rgm136 gemmL | 24 | 1188 | 1187.9 | 3.5512 | 42.22 | 23.79 | 65.45 / 149.9 | 51 |
| a013 | A:I | `gemmL1x3x9` | int8 random | 0xffffffff | rgm136 gemmL | 16, 103 | 1200.3 | 1200.2 | 3.46 | 32.8 | 23.68 | 31.56 / 113.5 | 51 |
| a014 | A:I | `gemmL1x3x9` | fp32 random | 0xffffffff | rgm136 gemmL | 43, 100 | 1187.2 | 1187.1 | 3.4215 | 42.17 | 23.49 | 63.9 / 144.3 | 50.5 |
| a015 | A:I | `gemmL2x3x6` | int8 random | 0xffffffff | rgm136 gemmL | 11 | 1183.6 | 1183.5 | 4.5494 | 32.7 | 23.68 | 41.06 / 148.8 | 51 |
| a016 | A:I | `gemmL2x3x6` | fp32 random | 0xffffffff | rgm136 gemmL | 21 | 1166.6 | 1166.6 | 4.4849 | 42.68 | 23.74 | 84.92 / 191.4 | 51 |
| a006 | A:I+P | `gemmL3x1x3` | fp32 random | 0xffffffff | rgm136 gemmL | 84 | 910.56 | 832.2 | 0.87489 | 48.52 | 23.75 | 21.67 / 42.45 | 51 |
| a017 | A:R | `gemmL1x1x18` | fp32 random | 0xffffffff | rgm136 gemmL | 19 | 1406.3 | 1395.5 | 2.7025 | 39.64 | 23.66 | 43.17 / 107.1 | 51 |
| a018 | A:R | `gemmL1x1x22` | fp32 random | 0xffffffff | rgm136 gemmL | 31 | 1408.3 | 1402.5 | 3.3086 | 39.92 | 23.68 | 53.73 / 132.1 | 51 |
| a019 | A:R | `gemmL1x1x26` | fp32 random | 0xffffffff | rgm136 gemmL | 30 | 1428.3 | 1424.4 | 3.9666 | 40.23 | 23.65 | 65.77 / 159.6 | 51 |
| a020 | A:R | `gemmL1x1x30` | fp32 random | 0xffffffff | rgm136 gemmL | 32 | 1545.1 | 1544.7 | 4.9487 | 39 | 23.71 | 75.66 / 193 | 51 |
| a021 | A:R | `gemmL1x1x34` | fp32 random | 0xffffffff | rgm136 gemmL | 25 | 1578.6 | 1578.5 | 5.7319 | 38.79 | 23.75 | 86.21 / 222.3 | 51 |
| a022 | A:R | `gemmL1x2x13` | fp32 random | 0xffffffff | rgm136 gemmL | 28 | 1470.2 | 1470.1 | 4.0809 | 39.59 | 23.67 | 64.97 / 161.6 | 51 |
| a023 | A:R | `gemmL1x2x18` | fp32 random | 0xffffffff | rgm136 gemmL | 9 | 1636.6 | 1636.6 | 6.2885 | 38.18 | 23.65 | 91.37 / 240.1 | 51 |
| a024 | A:R | `gemmL1x2x22` | fp32 random | 0xffffffff | rgm136 gemmL | 45 | 1637.8 | 1637.8 | 7.6936 | 38.29 | 23.71 | 112.2 / 294.6 | 51 |
| a025 | A:R | `gemmL2x1x8` | fp32 random | 0xffffffff | rgm136 gemmL | 39 | 1412.8 | 1399.5 | 2.4135 | 39.49 | 23.44 | 38.74 / 95.31 | 50 |
| a026 | A:R | `gemmL2x1x10` | fp32 random | 0xffffffff | rgm136 gemmL | 8 | 1410.8 | 1398.2 | 3.0125 | 39.56 | 23.62 | 48.02 / 119.2 | 51 |
| a027 | A:R | `gemmL3x1x6` | fp32 random | 0xffffffff | rgm136 gemmL | 26, 102 | 1416.3 | 1402.3 | 2.7216 | 39.66 | 23.66 | 43.55 / 108 | 50.8 |
| a028 | A:R | `gemmL3x1x7` | fp32 random | 0xffffffff | rgm136 gemmL | 47 | 1413.7 | 1400.1 | 3.1691 | 39.69 | 23.72 | 50.6 / 125.8 | 51 |
| a029 | A:R | `gemmL3x1x9` | fp32 random | 0xffffffff | rgm136 gemmL | 35 | 1411.4 | 1398.3 | 4.0682 | 39.62 | 23.72 | 64.68 / 161.2 | 51 |
| a030 | A:R+P | `gemmL4x1x6` | fp32 random | 0xffffffff | rgm136 gemmL | 76, 95 | 1416 | 1402.3 | 3.6284 | 39.52 | 23.55 | 57.95 / 143.4 | 50.5 |
| a031 | A:E | `gemmL1x3x40` | fp32 zeros | 0xffffffff | rgm136 gemmL | 38 | 1638.3 | 1638.3 | 20.939 | 27.44 | 23.54 | 81.66 / 574.6 | 51 |
| a032 | A:E | `gemmL1x3x40` | fp32 random | 0xffffffff | rgm136 gemmL | 4 | 1632.3 | 1632.3 | 20.921 | 37.9 | 23.41 | 303.1 / 792.9 | 50 |
| a033 | A:E | `gemmL2x2x44` | fp32 zeros | 0xffffffff | rgm136 gemmL | 5 | 1625.6 | 1625.6 | 30.601 | 27.3 | 23.49 | 116.6 / 835.4 | 50 |
| a034 | A:E | `gemmL2x2x44` | fp32 random | 0xffffffff | rgm136 gemmL | 10 | 1634.2 | 1634.2 | 30.754 | 38.19 | 23.68 | 446.1 / 1174 | 51 |
| a035 | A:E | `gemmL1x4x36` | fp32 zeros | 0xffffffff | rgm136 gemmL | 37 | 1637 | 1637 | 25.169 | 27.53 | 23.71 | 96.15 / 692.9 | 51 |
| a036 | A:E | `gemmL1x4x36` | fp32 random | 0xffffffff | rgm136 gemmL | 42, 101 | 1631.2 | 1631.2 | 25.075 | 38.07 | 23.6 | 362.8 / 954.6 | 50.5 |
| a089 (reference) | A:E | `gemmL4x8x8` | int8 random | 0xffffffff | rgm136 gemmL | 90 | 1418.8 | 1418.5 | 38.778 | 32.19 | 23.74 | 327.7 / 1248 | 51 |
| a090 (reference) | A:E | `gemmL4x8x8` | int8 random | 0xffffffff | rgm136 gemmL | 91 | 1418.4 | 1418.4 | 38.77 | 32.13 | 23.7 | 326.8 / 1246 | 51 |
| a037 | A:C | `gemmL3x2x1` | int8 random | 0xffffffff | rgm136 gemmL | 17 | 908.63 | 807.82 | 0.58199 | 33.47 | 23.75 | 5.657 / 19.48 | 51 |
| a038 | A:C | `gemmL3x2x1` | fp32 random | 0xffffffff | rgm136 gemmL | 33 | 872.06 | 775.59 | 0.55856 | 48.9 | 23.72 | 14.06 / 27.31 | 51 |
| a039 | A:C | `gemmL4x5x1` | int8 random | 0xffffffff | rgm136 gemmL | 2 | 912.94 | 878.4 | 1.9493 | 34.28 | 23.31 | 21.38 / 66.82 | 50 |
| a040 | A:C | `gemmL4x5x1` | fp32 random | 0xffffffff | rgm136 gemmL | 15 | 886.47 | 850.11 | 1.893 | 48.79 | 23.78 | 47.34 / 92.36 | 51 |
| a041 | A:C | `gemmL7x3x1` | int8 random | 0xffffffff | rgm136 gemmL | 44 | 1012.3 | 989.46 | 2.2695 | 33.87 | 23.71 | 23.06 / 76.87 | 51 |
| a042 | A:C | `gemmL7x3x1` | fp32 random | 0xffffffff | rgm136 gemmL | 40 | 984.74 | 962.81 | 2.2079 | 45.96 | 23.62 | 49.32 / 101.5 | 51 |
| a043 | A:C | `gemmL9x7x1` | int8 random | 0xffffffff | rgm136 gemmL | 18 | 906.89 | 843.16 | 6.0998 | 34.97 | 23.71 | 68.68 / 213.3 | 51 |
| a044 | A:C | `gemmL9x7x1` | fp32 random | 0xffffffff | rgm136 gemmL | 14 | 880.17 | 818.82 | 5.9201 | 49.64 | 23.75 | 153.2 / 293.8 | 51 |
| a045 | A:C | `gemmL10x10x1` | int8 random | 0xffffffff | rgm136 gemmL | 34 | 975.94 | 975.81 | 10.419 | 33.91 | 23.71 | 106.3 / 353.3 | 51 |
| a046 | A:C | `gemmL10x10x1` | fp32 random | 0xffffffff | rgm136 gemmL | 22 | 950.45 | 950.33 | 10.15 | 46.36 | 23.77 | 229.3 / 470.5 | 51 |
| a047 | A:C | `gemmL14x12x1` | int8 random | 0xffffffff | rgm136 gemmL | 29 | 1126.7 | 1125.2 | 20.207 | 32.92 | 23.71 | 186.1 / 665.2 | 51 |
| a048 | A:C | `gemmL14x12x1` | fp32 random | 0xffffffff | rgm136 gemmL | 23 | 1110.5 | 1108.6 | 19.993 | 43.5 | 23.76 | 394.6 / 869.6 | 51 |
| a049 | A:M | `gemmL2x8x8` | fp32 zeros | 0xffffffff | rgm136 gemmL | 61 | 1419.1 | 1418.9 | 19.391 | 26.9 | 22.81 | 79.31 / 521.6 | 48 |
| a050 | A:M | `gemmL2x8x8` | fp32 zeros | 0x3 | rgm136 gemmL | 48 | 1443.7 | 1395.5 | 19.728 | 24.32 | 23.69 | 12.43 / 479.8 | 51 |
| a051 | A:M | `gemmL2x8x8` | fp32 zeros | 0x11 | rgm136 gemmL | 54 | 1295 | 1295 | 17.696 | 23.58 | 23.09 | 8.671 / 417.3 | 49 |
| a052 | A:M | `gemmL2x8x8` | fp32 zeros | 0x1010101 | rgm136 gemmL | 69 | 1339.1 | 1339.1 | 18.3 | 23.45 | 22.71 | 13.63 / 429.2 | 48 |
| a053 | A:M | `gemmL2x8x8` | fp32 zeros | 0xf0000 | rgm136 gemmL | 60 | 1398.4 | 1371.5 | 19.1 | 24.16 | 22.87 | 24.64 / 461.5 | 48 |
| a054 | A:M | `gemmL2x8x8` | fp32 zeros | 0xf0f | rgm136 gemmL | 59 | 1421.9 | 1382.2 | 19.425 | 24.62 | 22.88 | 33.8 / 478.2 | 48 |
| a055 | A:M | `gemmL2x8x8` | fp32 zeros | 0x22222222 | rgm136 gemmL | 56 | 1256.8 | 1256.8 | 17.174 | 24.15 | 23 | 19.84 / 414.8 | 49 |
| a056 | A:M | `gemmL2x8x8` | fp32 zeros | 0x3030303 | rgm136 gemmL | 55 | 1351.7 | 1327.2 | 18.471 | 24.44 | 23.04 | 25.86 / 451.4 | 49 |
| a057 | A:M | `gemmL2x8x8` | fp32 zeros | 0xfff | rgm136 gemmL | 70 | 1423.7 | 1423.7 | 19.458 | 24.79 | 22.71 | 40.47 / 482.4 | 48 |
| a058 | A:M | `gemmL2x8x8` | fp32 zeros | 0x7070707 | rgm136 gemmL | 62 | 1363.7 | 1347.8 | 18.636 | 24.82 | 22.84 | 36.9 / 462.5 | 48 |
| a059 | A:M | `gemmL2x8x8` | fp32 zeros | 0xf0f0f0f | rgm136 gemmL | 66, 97 | 1376.7 | 1369.7 | 18.812 | 25.73 | 23.15 | 48.49 / 483.9 | 49.5 |
| a060 | A:M | `gemmL2x8x8` | fp32 zeros | 0x55555555 | rgm136 gemmL | 65 | 1336.1 | 1322.9 | 18.26 | 25.17 | 22.76 | 44.01 / 459.6 | 48 |
| a061 | A:M | `gemmL1x3x12` | fp32 zeros | 0xffffffff | rgm136 gemmL | 51 | 1460 | 1459.9 | 5.6124 | 27.22 | 23.31 | 21.94 / 152.8 | 50 |
| a062 | A:M | `gemmL1x3x12` | fp32 zeros | 0x3 | rgm136 gemmL | 53 | 1343.2 | 1343.1 | 5.1618 | 23.62 | 23.14 | 2.478 / 121.9 | 49 |
| a063 | A:M | `gemmL1x3x12` | fp32 zeros | 0x11 | rgm136 gemmL | 50, 99 | 1489 | 1242.4 | 5.7227 | 23.83 | 23.39 | 2.489 / 136.4 | 50 |
| a064 | A:M | `gemmL1x3x12` | fp32 zeros | 0x1010101 | rgm136 gemmL | 58 | 1507.8 | 1341.9 | 5.7963 | 23.84 | 22.92 | 5.333 / 138.2 | 48 |
| a065 | A:M | `gemmL1x3x12` | fp32 zeros | 0xf0000 | rgm136 gemmL | 57 | 1331.5 | 1331.5 | 5.1174 | 23.71 | 22.94 | 3.94 / 121.3 | 49 |
| a066 | A:M | `gemmL1x3x12` | fp32 zeros | 0xf0f | rgm136 gemmL | 64, 98 | 1378.5 | 1378.5 | 5.2981 | 24.38 | 23.12 | 6.702 / 129.2 | 49 |
| a067 | A:M | `gemmL1x3x12` | fp32 zeros | 0x22222222 | rgm136 gemmL | 52 | 1397.5 | 1176.9 | 5.3716 | 24.52 | 23.24 | 6.876 / 131.7 | 50 |
| a068 | A:M | `gemmL1x3x12` | fp32 zeros | 0x3030303 | rgm136 gemmL | 68 | 1379.7 | 1246.6 | 5.3027 | 24.15 | 22.74 | 7.477 / 128.1 | 48 |
| a069 | A:M | `gemmL1x3x12` | fp32 zeros | 0xfff | rgm136 gemmL | 49 | 1387.5 | 1387.5 | 5.3322 | 25.23 | 23.52 | 9.118 / 134.5 | 50 |
| a070 | A:M | `gemmL1x3x12` | fp32 zeros | 0x7070707 | rgm136 gemmL | 63 | 1358.6 | 1358.6 | 5.2212 | 24.66 | 22.77 | 9.868 / 128.8 | 48 |
| a071 | A:M | `gemmL1x3x12` | fp32 zeros | 0xf0f0f0f | rgm136 gemmL | 67, 96 | 1370.2 | 1370.2 | 5.2662 | 25.46 | 23.24 | 11.69 / 134.1 | 49.5 |
| a072 | A:M | `gemmL1x3x12` | fp32 zeros | 0x55555555 | rgm136 gemmL | 71 | 1443 | 1280.5 | 5.5438 | 25.32 | 22.67 | 14.69 / 140.4 | 48 |
| a073 | A:P | `gemmLn3x1x3` | fp32 random | 0xffffffff | rgm211 gemmLn | 85 | 871.15 | 766.01 | 0.83704 | 50.45 | 23.71 | 22.38 / 42.23 | 51 |
| a074 | A:P | `gemmL3x1x3` | fp32 random | 0xffffffff | rgm211 gemmL | 86, 93 | 892.75 | 795.46 | 0.85781 | 49.52 | 23.73 | 22.11 / 42.47 | 51 |
| a075 | A:P | `gemmLnc3x1x3` | fp32 random | 0xffffffff | rgm136 gemmLnc | 87 | 880.33 | 777.79 | 0.84567 | 62.93 | 23.75 | 33.13 / 53.22 | 51 |
| a076 | A:P | `gemmL1x6x5` | fp32 random | 0xffffffff | rgm136 gemmL | 80 | 1092.6 | 1079 | 3.4991 | 43.84 | 23.7 | 70.49 / 153.4 | 51 |
| a077 | A:P | `gemmLn1x6x5` | fp32 random | 0xffffffff | rgm211 gemmLn | 81 | 1063.5 | 1044.5 | 3.4058 | 44.35 | 23.75 | 70.16 / 151 | 51 |
| a078 | A:P | `gemmL1x6x5` | fp32 random | 0xffffffff | rgm211 gemmL | 82 | 1080.9 | 1060.4 | 3.4624 | 44.19 | 23.71 | 70.89 / 153 | 51 |
| a079 | A:P | `gemmLnc1x6x5` | fp32 random | 0xffffffff | rgm136 gemmLnc | 83, 94 | 982.54 | 957.79 | 3.1469 | 49.97 | 23.74 | 82.53 / 157.2 | 51 |
| a080 | A:P | `gemmLn4x1x6` | fp32 random | 0xffffffff | rgm211 gemmLn | 77 | 1335.8 | 1322.7 | 3.4232 | 40.14 | 23.46 | 57.1 / 137.4 | 50 |
| a081 | A:P | `gemmL4x1x6` | fp32 random | 0xffffffff | rgm211 gemmL | 78 | 1376.7 | 1358.9 | 3.527 | 39.86 | 23.54 | 57.56 / 140.6 | 50 |
| a082 | A:P | `gemmLnc4x1x6` | fp32 random | 0xffffffff | rgm136 gemmLnc | 79 | 1375.9 | 1356.9 | 3.5252 | 46.69 | 23.61 | 81.36 / 164.6 | 51 |
| a083 | A:P | `gemmL1x1x44` | fp32 random | 0xffffffff | rgm136 gemmL | 72 | 1633.8 | 1633.8 | 7.6546 | 37.29 | 22.71 | 111.6 / 285.4 | 48 |
| a084 | A:P | `gemmLn1x1x44` | fp32 random | 0xffffffff | rgm211 gemmLn | 73 | 1590.9 | 1590.9 | 7.4778 | 37.73 | 22.97 | 110.4 / 282.1 | 48 |
| a085 | A:P | `gemmL1x1x44` | fp32 random | 0xffffffff | rgm211 gemmL | 74 | 1613.8 | 1613.8 | 7.5902 | 37.63 | 23.11 | 110.2 / 285.6 | 49 |
| a086 | A:P | `gemmLnc1x1x44` | fp32 random | 0xffffffff | rgm136 gemmLnc | 75 | 1666.7 | 1659.1 | 7.8442 | 44.97 | 23.25 | 170.4 / 352.8 | 49 |
| a087 | A:P | `gemmLnc1x1x1` | int8 random | 0xffffffff | rgm136 gemmLnc | 89 | 358.7 | 357.94 | 0.038296 | 50.02 | 23.76 | 1.006 / 1.916 | 51 |
| a088 (reference) | A:P | `gemmL1x1x1` | int8 random | 0xffffffff | rgm136 gemmL | 88 | 389.78 | 388.02 | 0.041613 | 38.42 | 23.77 | 0.6096 / 1.599 | 51 |

### The ties (t01, `gemmL2x4x4` fp32 random, rgm136: the day offset the scorer reads)

| tie | n | wall cycles an op | counter-mean cycles an op | ms a GEMM | p_work W | p_rest W | mJ over idle / at rest | die C |
|---|---|---|---|---|---|---|---|---|
| t01 | 1 | 1121.6 | 1121.5 | 3.8314 | 42.6 | 23.21 | 74.29 / 163.2 | 49 |
| t01 | 92 | 1121.6 | 1121.5 | 3.8322 | 43.27 | 23.68 | 75.09 / 165.8 | 51 |
| t01 | 105 | 1121.7 | 1121.7 | 3.8325 | 43.42 | 23.68 | 75.65 / 166.4 | 51 |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside meter** (E184's arm S, the test of the meter itself, is pending). The watts carry that gain; a later calibration would move every joule by the same factor.

## Registered against happened

| registered (E213.md, plan-e213.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz (KIT.md 4) | `session/config-start.json` {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; config end {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; step 7's read: aifoundry3: manifest kept on the box (build/q141k/), config TDP 0 W / 65 C / 600 MHz, et-who clean; 25,659 of 25,659 samples at 600 MHz; nothing set |
| the freeze line on GitHub main before the booking (arm A MM1-v3's land `b1493082`) and the sealed-forecast check (step 0) | STEP0-E213 arm A: 5 of 5 as stated (HEAD 8e91dda6df38, GitHub main 8e91dda6df38); The model session's sealed forecast of E213's 131 points and 117 cases on both arms (sha256 `76f0b2f4643b8d2a599085041d6fcc5f063345465687f51ec75f7363c0b20325`, posted on the round's coordination threa |
| the rest: 40 minutes since our last session on aifoundry3 (E213.md 6) | step 7's and step 9's rest lines (departure 5) |
| the window: G = the booking; last start G + 1:30, last end G + 3:30; launch by the last start | G 06:32:00; last start 08:02, last end 10:02; the session 06:37:09-07:19:59, inside it |
| the never-run search right before the first card command (E213.md 4) | step 6n at 06:36:36; step 7 at 06:36:44 (within 30 minutes) |
| the smoke (s01-s04; s04 by E213.md A1 with its own stop path), then the stop-path test; the order: tie t01, pass 1 (90), tie, pass 2 (12), tie: 105 runs | smoke gate passed; stop-path test passed: board tripped in 0.3 s, its file touched, start refused; die trippe...; 105 of 105 runs in the registered order (queue.json) |
| the identity gate per process (the four families); the walk check; the kernel stops for the rgm211-host families | gates OK 109 of 109; walks OK 18 of 18; kernel stops: none |
| the stops and gates (KIT.md 4): board above 70 W on 3 samples, die at or above 70 C (the mean, or the risen latch), the die gate, two failed 'rgm136 gemmL' processes, K1, HUNG, the card-time rule, the window, the STOP file | none fired (queue.json stop null); HUNG lines 0; runs not started 0 |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | the preflight "dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)" at step 2 and on the box; every process's rc in `session/runs/*/run.json` and queue.json; HUNG lines: 0 |
| the cap: no run after 60 card-minutes, the session ends by 70; the registered subset if cut: 92 runs | the close at 42.83 card-minutes |
| the post waived; the package counter not read (E213.md 6) | the owner's words of Sun 15 Nov 2026 10:22:36 PST; not read |

## Device commands sent

READs only: the session's opening and closing `ettelem config` and its one 10 Hz sampler, all through E213's guard (dmcmd_audit_v2 GO, every send site a READ), and k6's step 7 config read through E128's guard; each host (rgm136's and rgm211's) opened the ops node of card 0 only (the runtime's creation aborts the submission queues of the card it enumerates, as every lab host's does: harmless on a card held alone); `et-who` sends no device command; step 6n sent nothing to a card (file reads only). No set, no reset, no statistics reset, no firmware write, no PMIC write.

## Files

`session/` (the box's session directory `T<T0>-A`, copied back exact and scrubbed; among its files `session.log`, `queue.json`, `identity.json`, `config-start.*`, `config-end.*`, `stop-path.json`, `telemetry.jsonl.gz`, `smoke/`, `runs/`, `reads/`, `runner.out`, `runner.rc`, `MANIFEST.sha256`), `data-e213.json` (the frozen scorer's input), `reduce-e213.txt` (the reducer's table), `neverrun-e213-card.txt`, `neverrun-e213-card.json`, `judge-e213-card.txt`, `judge-e213-card.json` and `labels-e213.json` (step 6n's report, judgement and labels, copied in by the collection), `SHA256SUMS` (the collected files; this README lies beside it). The scorer's outputs follow after the data commit (a later lane).

SPDX-License-Identifier: Apache-2.0
