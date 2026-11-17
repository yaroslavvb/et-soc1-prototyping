# E210, 2026-11-17, aifoundry3 card 0 at its pinned 600 MHz: the switch test (nine operand patterns never run in a GEMM, at gemmL1x1x1 and gemmL1x1x4, in chained A B B A blocks against random): RAN SHORT (142 of 171 runs: the card-time rule, no run after 85 card-minutes, left runs 143-171 unstarted; the registered subset (the opening and passes 1-4) complete)

*Tue 17 Nov 2026 (week 47), PST. E210, registered before any datum (`7b59f719`, [`E210.md`](../../../../tools/claims-v3/e210/E210.md) with its amendment A1; the routes R1, R3, R3L, R2 and R4 frozen in `forecast-e210.json` `dbc2d3f3...`), kitted (`8f420314`, [`KIT.md`](../../../../tools/claims-v3/e210/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e210/CARD-LANE-BRIEF.md)), verified (verify-e210: HOLDS WITH FIXES; fix-e210: FIXED WITH GAPS, before the land; land-e210: LANDED) and readiness-checked (ready-e210: READY WITH GAPS), all before any E210 datum; no E210 file changed since the kit (step 0: "114 of 114 as stated" at HEAD `75ecdd29` = GitHub main; steps 2 and 12: HISTORY OK). Q202c's card lane `card-e210`, orchestrated from aifoundry2. Run on the owner's go (his standing words of Sun 15 Nov 2026 and his matmul focus of Mon 16 Nov 2026: departure 1). rgm136 (E136's binary, unchanged; the patterns reach the host as tile files), built today on the box through the kernel gate (BUILD-GATE KERNEL OK: .text 61315bf6a449c282... the registered; ELF ff2723b81e2ce409... not the registered (the difference lies in sections the card never loads); its loadable identity 649d40793e459e51... the pinned one). Nothing was set on the card.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every case, order, window, threshold, stop and the cap is **registered** (E210.md; the kit). The per-case means and the millisecond and millijoule figures below are **desk arithmetic of the measured records** (the reducer's per-run values), not prices and not verdicts. **The forecasts are frozen before any E210 datum and blind to every E210 datum**, informed by the lab's committed data (E206, E208, E65, MM1-v1: E210.md's label); no forecast number is quoted here (they stay in `forecast-e210.json`). **No score is here:** the frozen scorer (step 13, `score_e210.py` as re-frozen by A1) runs on this directory only after it is committed, and a later lane commits its words beside it. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures, dated (Tue 17 Nov 2026, PST; placed before the results, as the round's go asks)

1. **The go, his words, verbatim (quoted without links).** Sun 15 Nov 2026: **10:05:42** "continue, all machines are up"; **10:22:36** "don't worry about discord post, just use the machines, nobody is using them"; **17:21:16** "Feel free to use more cards in parallel, I don't need to reserve them (things are automatically updated on [the lab dashboard]), currently I see only 1 card is being used, feel free to use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known; and again "Try again", read at 06:40:56 PST Tue 17 Nov 2026); "don't worry about hitting the limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before 21:51:09); "Make sure to incorporate suggestions from Fable when planning experiments" (received between 21:55 and 22:07:09). Mon 16 Nov 2026, received at or before 09:48:24 (a voice transcription in which "matte mold" is the matmul and "FME" the tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation." Beside them, reports of his words posted on the round's Discussion by the model session (not his own text): Mon 16 Nov 11:01:08 "There's no usage limit; feel free to use all the cards without restriction, since they look free every time I check the dashboard."; Mon 16 Nov 23:15:25 "There's no deadline; use the cards all night. Nobody else is using them except my lab session, which coordinates with you here." **His words name no experiment: the registered items are taken as their defaults** (E210.md 6): aifoundry3 card 0 at its pinned 600 MHz as found, reads only, nothing set; about 73 card-minutes planned, no run after 85, the session ends at 95; the 40-minute rest; one session; the window of E210.md 6. E210 is the card test of the "transistor switches" part of his matmul words of Mon 16 Nov.
2. **G = the booking on its day:** the card lane's `book.sh take aifoundry3 card-e210` printed BOOKED at **11:05:20 PST** Tue 17 Nov 2026: last start G+1:30 and last end G+3:30 (E210.md 6), each rounded up to the whole minute: **12:36 and 14:36 PST** (`s02_window_e210.sh A 2026-11-17 12:36 14:36`, written by step 1; the window file's `RB_GO_EPOCH` is the moment step 1 wrote it, not his go). The session's first card command at 11:11:19 (before the last start) and its end at 12:36:20 (before the last end).
3. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE), step 7's reads (et-who clean), the session's holder check before its first card command, card 0's lock held for the session, and a plain `timeout 10` (never `-k`) on every device process.
4. **The host's package counter: not read** (E210.md 6): no step, option or code of the kit reads it (step 0's anchor G6: no line under `tools/claims-v3/e210` names it).
5. **The rest.** The box's last session of ours before E210 was E207's (session end 07:53:54 PST Tue 17 Nov 2026, data `867f6a3f`): the rest opened at 08:33:54 PST. E210's committed rest rule, read on the box, printed at step 7 "197 minutes since E207's session end (2026-11-17 07:53:54 PST; dry sessions and blocks that opened no device skipped)" and at step 9 "197 minutes since E207's session end (2026-11-17 07:53:54 PST; dry sessions and blocks that opened no device skipped)" (40 required). Step 7's config read at 11:10:55 is reported apart from the session's card time.
6. **The booking and a sealed forecast.** The model session announced a sealed forecast of E210's 22 cases at 09:14:55 PST Tue 17 Nov 2026 (its post #11.4.1.1.1.1) and asked that E210's booking wait for it. The orchestrator then held aifoundry3's booking for it from 09:45:09 PST (as `orch-hold-e210-seal`), so that E210's first card command would come after the seal. The model session posted the sha256 at 10:05:27 PST, in a reply in the same thread (#11.4.1.1.1.1.1.1): `81a84eb62936aa572f2f42f33dcccd2414ecae64300381bbdada63efa9c77ae3`. The seal was registered as a freeze line of E210 in `tools/claims-v3/sealed-e210/e210-freeze-lines.md` (commit `75ecdd29`, pushed 11:02:46 PST, the lane `seal-e210`); its desk commit waited for another card lane's quiet hold on the lab clone (E209's card day on aifoundry2), which cleared at 10:58:42 PST. That was before E210's first card command and before any E210 datum. The orchestrator released its hold before 11:05:20 PST (the card lane's booking wait read the box free at 11:05:20), and the card lane booked at 11:05:20 PST. Step B's sealed check and step 0's sealed-forecast check (anchor S1) read "1 of 1", the record was read again right before step 7 ("1 of 1", reported), and step 2 read "sealed-forecast note commits (reported): 1". The forecast stays sealed: none of its numbers is here, and no lab rule scores it (E210.md section 0).
7. **The never-run search, repeated right before the first card command** (step 6n, E210.md 4 and A1 item 1; its report `neverrun-e210-card.txt`, `neverrun-e210-card.json` and `named-by-card.json` in this directory): at 11:10:47 PST, "NEVER-RUN 9 of 9 patterns (A1); by named tile files in launch records: 0 of 9 named; anywhere (the registered condition ii): 2 of 9 named (signs highmant8); generators not the host's in launch records: none; elsewhere (never a run): noise in 31 file(s); the registered rule as first written: 0 of 9 (6n; aifoundry3 searched)". step 6n (named-by-card.json): A1's verdict NEVER IN A GEMM for 9 of 9 patterns. **Again before the data commit** (step 12n; `neverrun-e210-late.*`, `named-by-late.json`): at 12:40:09 PST, "NEVER-RUN 9 of 9 patterns (A1); by named tile files in launch records: 0 of 9 named; anywhere (the registered condition ii): 2 of 9 named (signs highmant8); generators not the host's in launch records: none; elsewhere (never a run): noise in 30 file(s); the registered rule as first written: 0 of 9 (late; aifoundry3 not searched in this form)". step 12n (named-by-late.json): A1's verdict NEVER IN A GEMM for 9 of 9 patterns. **A1's verdict** (both conditions count a GEMM string only inside a host launch record) is the one that decides; the registered condition (ii) read anywhere and the registered rule as first written are given beside it (E210.md 4: a pattern found run stays in E210, no rule changes, the frozen scorer is never changed). The model session's own `ee-*` work folders were not read (E210.md A1 item 1). It is REPORTED and changes no rule.
8. **"Reads only" is true of the management node**: as every runtime creation of the lab's runtime does, each host's creation also sends the ops node's abort on the card's submission queues; harmless on a card held alone (et-who empty, card 0's lock held, aifoundry3 has one card).
9. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3; the box ran the session with its own `python3` (3.12.3 by ready-e210's read-only look at 09:05:30 PST; not re-read by this lane). The orchestrating session is the round's session on its yvb3 Claude account.
10. **The die line's hottest sensor** is read as E206.md's amendment A1 item 1 registers it and E210.md 6 adopts it (KIT.md section 4 item 1; not a departure): the latch (`minshire[2]`) read 87 C at the session's first sample and 87 C at its highest (lowest 87 C); the line trips on the shires' mean, or on the latch only once it has risen during the session above the lowest value it read.

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | 85.01 (planned about 73; no run after 85, the session ends at 95); session 11:11:19-12:36:20 PST (T0 1794942678); step 7's config read at 11:10:55, reported apart | measured (the session's clock) |
| step 7's config read (before the session; E128's guard, card 0's lock) | aifoundry3: manifest kept on the box (build/q141k/), config TDP 0 W / 65 C / 600 MHz, et-who clean | measured (READ) |
| the opening: 60 s at rest; the smoke (random@S1, zeros@S1, random@S2, 2 s each) | the opening's rest: 599 samples, board 22.94 W, die 48 C (the latch [87]); the die gate 52.0 C; 11:12:22 random@S1: rc 0, 7 launches, check approx, cycles an op 537.973 (1.000 of E206's 537.98 at p029); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 32.57 W over the rest on 26 samples (at least 2 W): ok; 11:12:25 zeros@S1: rc 0, 7 launches, check exact, cycles an op 538.003 (1.000 of E206's 537.99 at p080); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 4.6 W over the rest on 26 samples (at least 2 W): ok; 11:12:28 random@S2: rc 0, 7 launches, check approx, cycles an op 831.773 (1.000 of E206's 831.72 at p034); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 24.63 W over the rest on 26 samples (at least 2 W): ok (references: E206 arm A's measured cycles an op at the shape, p029 537.98, p080 537.99, p034 831.72) | measured |
| THE PROBE (maxalte@S2, 2 s, under the die gate) and the stop-path test | 11:12:28 the probe maxalte@S2: one 2 s process (gate 52.0 C, die 52 C after 0 s); 11:12:45 the probe maxalte@S2: IN (board max 50.09 W, die max 53 C on 69 samples): it stays in the session; the reducer's reading: verdict IN, board max 50.09 W, die max 53 C on 69 samples; stop-path test passed: board tripped in 0.3 s, its file touched, start refused; die tripped in 0.1 s, its file touched, start refused; smoke gate passed: the runs start | measured; the probe's readings REPORTED, never scored |
| runs: planned, started, with counted launches, not started (why) | 171 / 142 / 142 / 29; runs without a counted launch: 0; not started: 29 run(s) 143-pass5-signs-S1..171-close-random-S1 (the card-time rule: no run after 85 card-minutes) | measured |
| the registered subset if cut (the opening and passes 1-4: runs 001-126, every kind twice at both shapes) | 126 of 126 runs started: COMPLETE; runs not started by the card-time rule: 29 (143-171); by the probe: 0 | measured (the queue) |
| the die gate and the pace | the gate 52.0 C (min(60, the session's rest die 48 C + 4)); waits before the 142 started runs: median 13 s, longest 35 s (each under the 300 s bound; no run NO DATA by the gate); the pace 35.2 s a run from the first run's start to the last's (planned 26 s at S1 and 22.5 s at S2 from E206 arm A's pace, whose gate waits were 8-14 s): so the card-time rule (no run after 85 card-minutes) came at run 143 | measured |
| runs and processes the scorer sets aside or reports by name (E210.md A1 items 5 and 6) | processes that printed no check of C: 0 (the scorer's `R0` › `missing_REPORTED` names them after the data commit); runs with counted launches but no telemetry sample inside them (`runs_without_a_sample_inside`): 0 | measured |
| how the session ended | session end (T0 1794942678); queue.json stop: none; runner rc 0 (runner.rc); HUNG lines: 0 | measured |
| telemetry samples, and those at 600 MHz | 50,930 / 50,930; off the clock: 0; the counted launches' clock 600-600 MHz | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | 58.66 W at 12:00:09; 59 C at 12:35:49; 87 C / 87 C (the stops: above 70 W on 3 samples, 70 C; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it; the line 65 W: the planning peaks S1 59.54 W, S2 62.05 W) | measured |
| the opening and closing configuration reads | {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523} | measured (READ) |
| the identity lines | the card's identity: PCIe target /dev/et0_mgmt, physical device ID 0; the identity read: et-who {"other_off_card": 0, "other_on_card": 0, "ours_off_card": 0, "ours_on_card": 2, "ours_on_mgmt": 1} (counts by card), the sampler holds ['/dev/et0_mgmt']: card 0 only; sampler started (attempt 1, pid 3027206, every 100 ms); the smoke hosts: {"random@S1": {"stderr_targets": ["/dev/et0_ops"], "held": ["/dev/et0_ops"]}, "random@S2": {"stderr_targets": ["/dev/et0_ops"], "held": ["/dev/et0_ops"]}, "zeros@S1": {"stderr_targets": ["/dev/et0_ops"], "held": ["/dev/et0_ops"]}} | measured |
| every check of C the hosts printed (the runs; the smoke; the probe) | {"approx": 112, "exact": 30}; the smoke {"random@S1": ["approx"], "random@S2": ["approx"], "zeros@S1": ["exact"]}; the probe {"maxalte@S2": ["approx"]} | measured |
| the die at each run's start (the shires' mean) and the highest in a run's work window | 50.0-52.0 C; 59 C | measured |
| the session log's stop, identity and HUNG lines | none | measured |
| per block (R P P R, chained): the pattern runs' mean J over idle less the flanking random runs' mean; the time equality (cycles an op and t_gemm within +-0.1%) | the scorer's (after the data commit); this README gives the reducer's runs only | measured; the block values are the scorer's |
| the random runs' drift (J over idle a GEMM over the session, the ties left out) | random@S1: 30 runs, first 1.933 mJ, last 1.94 mJ, range 1.932-1.947 mJ, mean 1.938 mJ; random@S2: 20 runs, first 9.644 mJ, last 9.649 mJ, range 9.611-9.692 mJ, mean 9.655 mJ | measured; REPORTED (a block's chained form cancels a linear drift) |
| the never-run search, repeated (step 6n right before the first card command; step 12n before the data commit) | 6n at 11:10:47: "NEVER-RUN 9 of 9 patterns (A1); by named tile files in launch records: 0 of 9 named; anywhere (the registered condition ii): 2 of 9 named (signs highmant8); generators not the host's in launch records: none; elsewhere (never a run): noise in 31 file(s); the registered rule as first written: 0 of 9 (6n; aifoundry3 searched)"; step 6n (named-by-card.json): A1's verdict NEVER IN A GEMM for 9 of 9 patterns. 12n at 12:40:09: "NEVER-RUN 9 of 9 patterns (A1); by named tile files in launch records: 0 of 9 named; anywhere (the registered condition ii): 2 of 9 named (signs highmant8); generators not the host's in launch records: none; elsewhere (never a run): noise in 30 file(s); the registered rule as first written: 0 of 9 (late; aifoundry3 not searched in this form)"; step 12n (named-by-late.json): A1's verdict NEVER IN A GEMM for 9 of 9 patterns | a desk read, REPORTED (E210.md 4: a pattern found run stays in E210; this README says which) |

### Per case (the reducer's values, `reduce-e210.txt` and `data-e210.json`; desk means of measured runs)

J over idle = (p_work - p_rest) x t_gemm and J with the card at rest = p_work x t_gemm, a GEMM (the scorer's form); seconds in ms and joules in mJ a GEMM; cycles an op the median of the host's counter (the mean over minions) over the counted launches. Runs: planned / started / with counted launches. The block values (pattern less its flanking random runs) are the scorer's.

| case | role | arm | runs | cycles an op | ms a GEMM | p_work W | p_rest W | mJ over idle (mean) | mJ at rest (mean) |
|---|---|---|---|---|---|---|---|---|---|
| random@S1 | reference | gemmL1x1x1 | 36 / 32 / 32 | 537.984 | 0.0575807 | 57.58 | 23.94 | 1.937 | 3.316 |
| zeros@S1 | control | gemmL1x1x1 | 4 / 4 / 4 | 537.981 | 0.0575829 | 28.08 | 23.95 | 0.2376 | 1.617 |
| ones@S1 | control | gemmL1x1x1 | 4 / 4 / 4 | 537.986 | 0.0575825 | 37.38 | 23.98 | 0.771 | 2.152 |
| sparse50@S1 | control | gemmL1x1x1 | 4 / 4 / 4 | 537.984 | 0.0575834 | 39.14 | 24.02 | 0.8707 | 2.254 |
| arow50@S1 | reported | gemmL1x1x1 | 6 / 6 / 6 | 537.984 | 0.057581 | 45.12 | 24.02 | 1.216 | 2.598 |
| badjeq@S1 | test | gemmL1x1x1 | 6 / 6 / 6 | 537.989 | 0.0575781 | 57.67 | 24.05 | 1.936 | 3.32 |
| bhalfeq@S1 | test | gemmL1x1x1 | 6 / 6 / 6 | 537.992 | 0.0575844 | 48.51 | 24.04 | 1.409 | 2.794 |
| hd4@S1 | test | gemmL1x1x1 | 6 / 6 / 6 | 537.986 | 0.0575797 | 51.93 | 24.04 | 1.606 | 2.99 |
| highmant8@S1 | test | gemmL1x1x1 | 6 / 4 / 4 | 537.984 | 0.0575773 | 45.4 | 24.02 | 1.231 | 2.614 |
| lowmant8@S1 | test | gemmL1x1x1 | 6 / 4 / 4 | 537.986 | 0.0575801 | 43.56 | 24 | 1.126 | 2.508 |
| negzero@S1 | test | gemmL1x1x1 | 6 / 6 / 6 | 537.987 | 0.0575815 | 36.99 | 24 | 0.7479 | 2.13 |
| signs@S1 | test | gemmL1x1x1 | 6 / 4 / 4 | 537.984 | 0.057583 | 41.33 | 24 | 0.9977 | 2.38 |
| random@S2 | reference | gemmL1x1x4 | 27 / 20 / 20 | 831.738 | 0.38876 | 48.78 | 23.95 | 9.655 | 18.96 |
| zeros@S2 | control | gemmL1x1x4 | 4 / 4 / 4 | 831.746 | 0.388771 | 28.29 | 23.94 | 1.692 | 11 |
| ones@S2 | control | gemmL1x1x4 | 4 / 4 / 4 | 831.742 | 0.388748 | 34.77 | 23.97 | 4.199 | 13.52 |
| sparse50@S2 | control | gemmL1x1x4 | 4 / 4 / 4 | 831.742 | 0.38876 | 36.89 | 24.02 | 5.003 | 14.34 |
| bhalfeq@S2 | test | gemmL1x1x4 | 6 / 4 / 4 | 831.743 | 0.388771 | 43.36 | 24 | 7.526 | 16.86 |
| hd4@S2 | test | gemmL1x1x4 | 6 / 4 / 4 | 831.736 | 0.388757 | 45.45 | 24.03 | 8.326 | 17.67 |
| highmant8@S2 | test | gemmL1x1x4 | 6 / 4 / 4 | 831.74 | 0.388761 | 40.29 | 23.98 | 6.34 | 15.66 |
| lowmant8@S2 | test | gemmL1x1x4 | 6 / 4 / 4 | 831.744 | 0.388763 | 39.19 | 23.96 | 5.918 | 15.23 |
| maxalte@S2 | test | gemmL1x1x4 | 6 / 4 / 4 | 831.735 | 0.388748 | 51.13 | 24.03 | 10.54 | 19.88 |
| negzero@S2 | test | gemmL1x1x4 | 6 / 4 / 4 | 831.746 | 0.388784 | 34.19 | 23.94 | 3.985 | 13.29 |

### The ties (001 and 002, the warm-ups; 171, the closing; random@S1)

| run | ms a GEMM | cycles an op | p_work W | p_rest W | mJ over idle | die C (start -> highest) |
|---|---|---|---|---|---|---|
| 001-open-random-S1 | 0.0575835 | 537.991 | 56.57 | 23.31 | 1.915 | 50 -> 56 |
| 002-open-random-S1 | 0.0575819 | 537.981 | 57.1 | 23.65 | 1.926 | 51 -> 57 |
| 171-close-random-S1 | NOT STARTED | | | | | |

Beside them, E206 arm A's p029 on this card (random at gemmL1x1x1, its 2 runs, committed in `d7e4f35e`, measured): 0.0575822 ms a GEMM, cycles an op 537.982, 1.951 mJ over idle (means). Desk arithmetic; REPORTED.

### Per run (the reducer's values)

| run | case | cycles an op | ms a GEMM | p_work W | p_rest W | mJ over idle | die C (start -> highest) | clock MHz (min-max) |
|---|---|---|---|---|---|---|---|---|
| 001-open-random-S1 | random@S1 | 537.991 | 0.0575835 | 56.57 | 23.31 | 1.915 | 50 -> 56 | 600-600 |
| 002-open-random-S1 | random@S1 | 537.981 | 0.0575819 | 57.1 | 23.65 | 1.926 | 51 -> 57 | 600-600 |
| 003-pass1-random-S1 | random@S1 | 537.979 | 0.0575824 | 57.42 | 23.85 | 1.933 | 52 -> 58 | 600-600 |
| 004-pass1-sparse50-S1 | sparse50@S1 | 537.99 | 0.0575846 | 39.09 | 24.02 | 0.8678 | 52 -> 55 | 600-600 |
| 005-pass1-sparse50-S1 | sparse50@S1 | 537.984 | 0.0575862 | 39.09 | 23.98 | 0.8704 | 52 -> 55 | 600-600 |
| 006-pass1-random-S1 | random@S1 | 537.992 | 0.0575765 | 57.61 | 24.02 | 1.934 | 52 -> 58 | 600-600 |
| 007-pass1-bhalfeq-S1 | bhalfeq@S1 | 537.994 | 0.0575876 | 48.5 | 24.04 | 1.409 | 52 -> 57 | 600-600 |
| 008-pass1-bhalfeq-S1 | bhalfeq@S1 | 537.99 | 0.0575863 | 48.44 | 24.05 | 1.405 | 52 -> 57 | 600-600 |
| 009-pass1-random-S1 | random@S1 | 537.986 | 0.0575801 | 57.62 | 24.02 | 1.934 | 52 -> 58 | 600-600 |
| 010-pass1-highmant8-S1 | highmant8@S1 | 537.981 | 0.0575738 | 45.42 | 24.02 | 1.232 | 52 -> 56 | 600-600 |
| 011-pass1-highmant8-S1 | highmant8@S1 | 537.993 | 0.0575806 | 45.41 | 24.01 | 1.233 | 52 -> 56 | 600-600 |
| 012-pass1-random-S1 | random@S1 | 537.995 | 0.057584 | 57.67 | 23.94 | 1.942 | 52 -> 58 | 600-600 |
| 013-pass1-arow50-S1 | arow50@S1 | 537.987 | 0.0575784 | 45.09 | 24.04 | 1.212 | 52 -> 56 | 600-600 |
| 014-pass1-arow50-S1 | arow50@S1 | 537.986 | 0.0575772 | 45.11 | 23.98 | 1.217 | 52 -> 56 | 600-600 |
| 015-pass1-random-S1 | random@S1 | 537.976 | 0.057585 | 57.56 | 24.01 | 1.932 | 52 -> 58 | 600-600 |
| 016-pass1-badjeq-S1 | badjeq@S1 | 537.987 | 0.0575701 | 57.61 | 24.03 | 1.933 | 52 -> 58 | 600-600 |
| 017-pass1-badjeq-S1 | badjeq@S1 | 537.979 | 0.0575837 | 57.63 | 24.05 | 1.934 | 52 -> 59 | 600-600 |
| 018-pass1-random-S1 | random@S1 | 537.986 | 0.0575828 | 57.69 | 24.08 | 1.935 | 52 -> 58 | 600-600 |
| 019-pass1-ones-S1 | ones@S1 | 537.979 | 0.0575825 | 37.39 | 24.08 | 0.7664 | 52 -> 55 | 600-600 |
| 020-pass1-ones-S1 | ones@S1 | 537.986 | 0.0575799 | 37.36 | 23.9 | 0.775 | 52 -> 55 | 600-600 |
| 021-pass1-random-S1 | random@S1 | 537.97 | 0.0575799 | 57.6 | 23.91 | 1.94 | 52 -> 58 | 600-600 |
| 022-pass1-lowmant8-S1 | lowmant8@S1 | 537.987 | 0.0575807 | 43.59 | 24.03 | 1.126 | 52 -> 56 | 600-600 |
| 023-pass1-lowmant8-S1 | lowmant8@S1 | 537.989 | 0.0575812 | 43.52 | 23.95 | 1.127 | 52 -> 56 | 600-600 |
| 024-pass1-random-S1 | random@S1 | 537.989 | 0.0575878 | 57.68 | 23.98 | 1.94 | 52 -> 58 | 600-600 |
| 025-pass1-negzero-S1 | negzero@S1 | 537.982 | 0.057575 | 37.06 | 24.08 | 0.7473 | 52 -> 55 | 600-600 |
| 026-pass1-negzero-S1 | negzero@S1 | 537.988 | 0.0575774 | 36.97 | 23.95 | 0.7497 | 52 -> 54 | 600-600 |
| 027-pass1-random-S1 | random@S1 | 537.976 | 0.0575735 | 57.6 | 23.9 | 1.94 | 52 -> 58 | 600-600 |
| 028-pass1-signs-S1 | signs@S1 | 537.981 | 0.0575775 | 41.36 | 24.04 | 0.9975 | 52 -> 55 | 600-600 |
| 029-pass1-signs-S1 | signs@S1 | 537.984 | 0.0575845 | 41.31 | 23.95 | 0.9997 | 52 -> 55 | 600-600 |
| 030-pass1-random-S1 | random@S1 | 537.99 | 0.0575813 | 57.61 | 23.95 | 1.938 | 52 -> 58 | 600-600 |
| 031-pass1-hd4-S1 | hd4@S1 | 537.986 | 0.0575741 | 51.94 | 24.04 | 1.606 | 52 -> 57 | 600-600 |
| 032-pass1-hd4-S1 | hd4@S1 | 537.989 | 0.057582 | 51.84 | 24.04 | 1.601 | 52 -> 57 | 600-600 |
| 033-pass1-random-S1 | random@S1 | 537.976 | 0.0575778 | 57.65 | 24.02 | 1.936 | 52 -> 58 | 600-600 |
| 034-pass1-zeros-S1 | zeros@S1 | 537.974 | 0.057584 | 28.13 | 24.07 | 0.2338 | 52 -> 53 | 600-600 |
| 035-pass1-zeros-S1 | zeros@S1 | 537.982 | 0.0575786 | 28.04 | 23.85 | 0.2413 | 52 -> 53 | 600-600 |
| 036-pass1-random-S1 | random@S1 | 537.992 | 0.0575784 | 57.44 | 23.78 | 1.938 | 52 -> 58 | 600-600 |
| 037-pass2-random-S2 | random@S2 | 831.741 | 0.388789 | 48.83 | 24.02 | 9.644 | 52 -> 57 | 600-600 |
| 038-pass2-highmant8-S2 | highmant8@S2 | 831.743 | 0.388782 | 40.33 | 24.04 | 6.333 | 52 -> 55 | 600-600 |
| 039-pass2-highmant8-S2 | highmant8@S2 | 831.737 | 0.38875 | 40.28 | 23.96 | 6.342 | 52 -> 55 | 600-600 |
| 040-pass2-random-S2 | random@S2 | 831.734 | 0.388786 | 48.8 | 23.95 | 9.661 | 52 -> 56 | 600-600 |
| 041-pass2-hd4-S2 | hd4@S2 | 831.735 | 0.388772 | 45.4 | 24.03 | 8.308 | 52 -> 56 | 600-600 |
| 042-pass2-hd4-S2 | hd4@S2 | 831.737 | 0.388726 | 45.48 | 24.04 | 8.334 | 52 -> 56 | 600-600 |
| 043-pass2-random-S2 | random@S2 | 831.738 | 0.38876 | 48.79 | 24.02 | 9.63 | 52 -> 56 | 600-600 |
| 044-pass2-maxalte-S2 | maxalte@S2 | 831.739 | 0.388752 | 51.15 | 24.04 | 10.54 | 52 -> 57 | 600-600 |
| 045-pass2-maxalte-S2 | maxalte@S2 | 831.731 | 0.388759 | 51.04 | 24.02 | 10.5 | 52 -> 57 | 600-600 |
| 046-pass2-random-S2 | random@S2 | 831.738 | 0.388757 | 48.87 | 24.02 | 9.661 | 52 -> 57 | 600-600 |
| 047-pass2-bhalfeq-S2 | bhalfeq@S2 | 831.743 | 0.388778 | 43.44 | 24.02 | 7.55 | 52 -> 56 | 600-600 |
| 048-pass2-bhalfeq-S2 | bhalfeq@S2 | 831.746 | 0.388782 | 43.32 | 24.02 | 7.503 | 52 -> 56 | 600-600 |
| 049-pass2-random-S2 | random@S2 | 831.737 | 0.3888 | 48.77 | 24.02 | 9.623 | 52 -> 56 | 600-600 |
| 050-pass2-zeros-S2 | zeros@S2 | 831.75 | 0.388762 | 28.34 | 24.05 | 1.668 | 52 -> 53 | 600-600 |
| 051-pass2-zeros-S2 | zeros@S2 | 831.744 | 0.388794 | 28.24 | 23.84 | 1.709 | 52 -> 52 | 600-600 |
| 052-pass2-random-S2 | random@S2 | 831.742 | 0.38878 | 48.63 | 23.74 | 9.677 | 51.8 -> 56 | 600-600 |
| 053-pass2-lowmant8-S2 | lowmant8@S2 | 831.747 | 0.388776 | 39.13 | 23.95 | 5.902 | 52 -> 55 | 600-600 |
| 054-pass2-lowmant8-S2 | lowmant8@S2 | 831.746 | 0.388774 | 39.13 | 23.91 | 5.917 | 52 -> 55 | 600-600 |
| 055-pass2-random-S2 | random@S2 | 831.735 | 0.38878 | 48.63 | 23.91 | 9.611 | 52 -> 56 | 600-600 |
| 056-pass2-negzero-S2 | negzero@S2 | 831.741 | 0.38878 | 34.22 | 24 | 3.971 | 52 -> 54 | 600-600 |
| 057-pass2-negzero-S2 | negzero@S2 | 831.751 | 0.388787 | 34.19 | 23.88 | 4.006 | 52 -> 54 | 600-600 |
| 058-pass2-random-S2 | random@S2 | 831.739 | 0.388765 | 48.78 | 23.85 | 9.692 | 52 -> 56 | 600-600 |
| 059-pass2-ones-S2 | ones@S2 | 831.74 | 0.388751 | 34.78 | 24.02 | 4.181 | 52 -> 54 | 600-600 |
| 060-pass2-ones-S2 | ones@S2 | 831.745 | 0.388765 | 34.78 | 23.9 | 4.23 | 52 -> 54 | 600-600 |
| 061-pass2-random-S2 | random@S2 | 831.736 | 0.388779 | 48.83 | 23.91 | 9.688 | 52 -> 56 | 600-600 |
| 062-pass2-sparse50-S2 | sparse50@S2 | 831.742 | 0.388775 | 36.89 | 24.04 | 4.996 | 52 -> 54 | 600-600 |
| 063-pass2-sparse50-S2 | sparse50@S2 | 831.744 | 0.388746 | 36.88 | 24.01 | 5.003 | 52 -> 54 | 600-600 |
| 064-pass2-random-S2 | random@S2 | 831.737 | 0.388752 | 48.79 | 24 | 9.635 | 52 -> 57 | 600-600 |
| 065-pass3-random-S1 | random@S1 | 537.99 | 0.0575835 | 57.72 | 24.08 | 1.937 | 52 -> 59 | 600-600 |
| 066-pass3-zeros-S1 | zeros@S1 | 537.989 | 0.057582 | 28.11 | 24.05 | 0.2338 | 52 -> 53 | 600-600 |
| 067-pass3-zeros-S1 | zeros@S1 | 537.979 | 0.0575869 | 28.04 | 23.84 | 0.2416 | 52 -> 53 | 600-600 |
| 068-pass3-random-S1 | random@S1 | 537.973 | 0.0575857 | 57.39 | 23.76 | 1.937 | 52 -> 58 | 600-600 |
| 069-pass3-hd4-S1 | hd4@S1 | 537.973 | 0.0575808 | 51.87 | 24.02 | 1.604 | 52 -> 57 | 600-600 |
| 070-pass3-hd4-S1 | hd4@S1 | 537.988 | 0.0575784 | 51.98 | 24.04 | 1.609 | 52 -> 57 | 600-600 |
| 071-pass3-random-S1 | random@S1 | 537.977 | 0.0575808 | 57.7 | 24.07 | 1.936 | 52 -> 59 | 600-600 |
| 072-pass3-signs-S1 | signs@S1 | 537.989 | 0.0575883 | 41.34 | 24.07 | 0.9946 | 52 -> 55 | 600-600 |
| 073-pass3-signs-S1 | signs@S1 | 537.98 | 0.0575817 | 41.3 | 23.95 | 0.999 | 52 -> 55 | 600-600 |
| 074-pass3-random-S1 | random@S1 | 537.986 | 0.0575863 | 57.66 | 23.93 | 1.942 | 52 -> 58 | 600-600 |
| 075-pass3-negzero-S1 | negzero@S1 | 537.991 | 0.0575852 | 36.97 | 24.08 | 0.7423 | 52 -> 55 | 600-600 |
| 076-pass3-negzero-S1 | negzero@S1 | 537.988 | 0.0575832 | 36.96 | 23.91 | 0.7515 | 52 -> 54 | 600-600 |
| 077-pass3-random-S1 | random@S1 | 537.991 | 0.0575816 | 57.66 | 23.89 | 1.945 | 52 -> 58 | 600-600 |
| 078-pass3-lowmant8-S1 | lowmant8@S1 | 537.978 | 0.0575803 | 43.54 | 24.04 | 1.123 | 52 -> 56 | 600-600 |
| 079-pass3-lowmant8-S1 | lowmant8@S1 | 537.991 | 0.0575784 | 43.58 | 23.99 | 1.128 | 52 -> 56 | 600-600 |
| 080-pass3-random-S1 | random@S1 | 537.987 | 0.0575763 | 57.62 | 23.95 | 1.939 | 52 -> 58 | 600-600 |
| 081-pass3-ones-S1 | ones@S1 | 537.993 | 0.0575827 | 37.39 | 24.02 | 0.7699 | 52 -> 55 | 600-600 |
| 082-pass3-ones-S1 | ones@S1 | 537.988 | 0.0575849 | 37.36 | 23.94 | 0.7728 | 52 -> 55 | 600-600 |
| 083-pass3-random-S1 | random@S1 | 537.988 | 0.0575804 | 57.62 | 23.89 | 1.942 | 52 -> 58 | 600-600 |
| 084-pass3-badjeq-S1 | badjeq@S1 | 537.991 | 0.0575798 | 57.67 | 24.04 | 1.937 | 52 -> 59 | 600-600 |
| 085-pass3-badjeq-S1 | badjeq@S1 | 537.995 | 0.0575777 | 57.77 | 24.05 | 1.941 | 52 -> 58 | 600-600 |
| 086-pass3-random-S1 | random@S1 | 537.982 | 0.05758 | 57.67 | 24.05 | 1.936 | 52 -> 58 | 600-600 |
| 087-pass3-arow50-S1 | arow50@S1 | 537.982 | 0.057577 | 45.14 | 24.04 | 1.215 | 52 -> 56 | 600-600 |
| 088-pass3-arow50-S1 | arow50@S1 | 537.997 | 0.0575867 | 45.07 | 23.98 | 1.215 | 52 -> 56 | 600-600 |
| 089-pass3-random-S1 | random@S1 | 537.985 | 0.0575761 | 57.54 | 23.99 | 1.932 | 52 -> 58 | 600-600 |
| 090-pass3-highmant8-S1 | highmant8@S1 | 537.984 | 0.0575699 | 45.42 | 24.05 | 1.23 | 52 -> 56 | 600-600 |
| 091-pass3-highmant8-S1 | highmant8@S1 | 537.978 | 0.057585 | 45.36 | 23.99 | 1.231 | 52 -> 56 | 600-600 |
| 092-pass3-random-S1 | random@S1 | 537.977 | 0.0575779 | 57.69 | 23.99 | 1.94 | 52 -> 58 | 600-600 |
| 093-pass3-bhalfeq-S1 | bhalfeq@S1 | 537.998 | 0.0575777 | 48.51 | 24.04 | 1.409 | 52 -> 57 | 600-600 |
| 094-pass3-bhalfeq-S1 | bhalfeq@S1 | 537.989 | 0.057587 | 48.53 | 24.02 | 1.411 | 52 -> 57 | 600-600 |
| 095-pass3-random-S1 | random@S1 | 537.983 | 0.0575793 | 57.71 | 24.08 | 1.936 | 52 -> 59 | 600-600 |
| 096-pass3-sparse50-S1 | sparse50@S1 | 537.975 | 0.0575773 | 39.19 | 24.08 | 0.87 | 52 -> 55 | 600-600 |
| 097-pass3-sparse50-S1 | sparse50@S1 | 537.985 | 0.0575855 | 39.2 | 24.01 | 0.8747 | 52 -> 55 | 600-600 |
| 098-pass3-random-S1 | random@S1 | 537.991 | 0.0575802 | 57.61 | 23.99 | 1.936 | 52 -> 58 | 600-600 |
| 099-pass4-random-S2 | random@S2 | 831.733 | 0.388744 | 48.83 | 24.05 | 9.633 | 52 -> 57 | 600-600 |
| 100-pass4-sparse50-S2 | sparse50@S2 | 831.743 | 0.388777 | 36.96 | 24.03 | 5.027 | 52 -> 54 | 600-600 |
| 101-pass4-sparse50-S2 | sparse50@S2 | 831.74 | 0.388743 | 36.82 | 23.99 | 4.988 | 52 -> 54 | 600-600 |
| 102-pass4-random-S2 | random@S2 | 831.739 | 0.388736 | 48.83 | 23.96 | 9.666 | 52 -> 56 | 600-600 |
| 103-pass4-ones-S2 | ones@S2 | 831.74 | 0.388715 | 34.78 | 24.04 | 4.175 | 52 -> 54 | 600-600 |
| 104-pass4-ones-S2 | ones@S2 | 831.744 | 0.388759 | 34.74 | 23.91 | 4.21 | 52 -> 54 | 600-600 |
| 105-pass4-random-S2 | random@S2 | 831.744 | 0.388784 | 48.76 | 23.91 | 9.661 | 52 -> 56 | 600-600 |
| 106-pass4-negzero-S2 | negzero@S2 | 831.746 | 0.388789 | 34.18 | 24 | 3.956 | 52 -> 54 | 600-600 |
| 107-pass4-negzero-S2 | negzero@S2 | 831.745 | 0.388779 | 34.18 | 23.88 | 4.004 | 52 -> 54 | 600-600 |
| 108-pass4-random-S2 | random@S2 | 831.738 | 0.388728 | 48.72 | 23.85 | 9.668 | 52 -> 56 | 600-600 |
| 109-pass4-lowmant8-S2 | lowmant8@S2 | 831.743 | 0.388752 | 39.26 | 24.02 | 5.925 | 52 -> 55 | 600-600 |
| 110-pass4-lowmant8-S2 | lowmant8@S2 | 831.74 | 0.388752 | 39.22 | 23.97 | 5.928 | 52 -> 55 | 600-600 |
| 111-pass4-random-S2 | random@S2 | 831.739 | 0.388767 | 48.76 | 23.95 | 9.645 | 52 -> 56 | 600-600 |
| 112-pass4-zeros-S2 | zeros@S2 | 831.747 | 0.388764 | 28.34 | 24.04 | 1.672 | 52 -> 53 | 600-600 |
| 113-pass4-zeros-S2 | zeros@S2 | 831.745 | 0.388766 | 28.23 | 23.81 | 1.718 | 52 -> 53 | 600-600 |
| 114-pass4-random-S2 | random@S2 | 831.743 | 0.388738 | 48.58 | 23.77 | 9.645 | 52 -> 56 | 600-600 |
| 115-pass4-bhalfeq-S2 | bhalfeq@S2 | 831.739 | 0.38878 | 43.35 | 23.99 | 7.527 | 52 -> 55 | 600-600 |
| 116-pass4-bhalfeq-S2 | bhalfeq@S2 | 831.744 | 0.388745 | 43.34 | 23.99 | 7.522 | 52 -> 55 | 600-600 |
| 117-pass4-random-S2 | random@S2 | 831.738 | 0.388739 | 48.87 | 23.99 | 9.672 | 52 -> 56 | 600-600 |
| 118-pass4-maxalte-S2 | maxalte@S2 | 831.731 | 0.388721 | 51.16 | 24.02 | 10.55 | 52 -> 57 | 600-600 |
| 119-pass4-maxalte-S2 | maxalte@S2 | 831.74 | 0.38876 | 51.19 | 24.04 | 10.55 | 52 -> 57 | 600-600 |
| 120-pass4-random-S2 | random@S2 | 831.733 | 0.388742 | 48.96 | 24.03 | 9.691 | 52 -> 57 | 600-600 |
| 121-pass4-hd4-S2 | hd4@S2 | 831.738 | 0.388752 | 45.5 | 24.02 | 8.348 | 52 -> 56 | 600-600 |
| 122-pass4-hd4-S2 | hd4@S2 | 831.735 | 0.388776 | 45.42 | 24.04 | 8.312 | 52 -> 56 | 600-600 |
| 123-pass4-random-S2 | random@S2 | 831.738 | 0.388736 | 48.83 | 24.02 | 9.645 | 52 -> 57 | 600-600 |
| 124-pass4-highmant8-S2 | highmant8@S2 | 831.743 | 0.388744 | 40.27 | 23.99 | 6.329 | 52 -> 55 | 600-600 |
| 125-pass4-highmant8-S2 | highmant8@S2 | 831.738 | 0.388767 | 40.29 | 23.95 | 6.354 | 52 -> 55 | 600-600 |
| 126-pass4-random-S2 | random@S2 | 831.738 | 0.388747 | 48.8 | 23.98 | 9.649 | 52 -> 57 | 600-600 |
| 127-pass5-random-S1 | random@S1 | 537.991 | 0.0575794 | 57.68 | 24.03 | 1.938 | 52 -> 59 | 600-600 |
| 128-pass5-bhalfeq-S1 | bhalfeq@S1 | 537.991 | 0.0575838 | 48.56 | 24.04 | 1.412 | 52 -> 57 | 600-600 |
| 129-pass5-bhalfeq-S1 | bhalfeq@S1 | 537.99 | 0.057584 | 48.55 | 24.08 | 1.409 | 52 -> 57 | 600-600 |
| 130-pass5-random-S1 | random@S1 | 537.989 | 0.0575817 | 57.62 | 24.04 | 1.934 | 52 -> 59 | 600-600 |
| 131-pass5-negzero-S1 | negzero@S1 | 537.99 | 0.0575854 | 37.02 | 24.05 | 0.7469 | 52 -> 55 | 600-600 |
| 132-pass5-negzero-S1 | negzero@S1 | 537.983 | 0.0575826 | 36.97 | 23.95 | 0.7497 | 52 -> 55 | 600-600 |
| 133-pass5-random-S1 | random@S1 | 537.981 | 0.0575821 | 57.73 | 23.91 | 1.947 | 52 -> 58 | 600-600 |
| 134-pass5-hd4-S1 | hd4@S1 | 537.99 | 0.057576 | 51.95 | 24.04 | 1.607 | 52 -> 58 | 600-600 |
| 135-pass5-hd4-S1 | hd4@S1 | 537.987 | 0.0575868 | 51.98 | 24.05 | 1.608 | 52 -> 58 | 600-600 |
| 136-pass5-random-S1 | random@S1 | 537.99 | 0.0575796 | 57.75 | 24.05 | 1.94 | 52 -> 59 | 600-600 |
| 137-pass5-badjeq-S1 | badjeq@S1 | 537.991 | 0.0575742 | 57.64 | 24.04 | 1.934 | 52 -> 59 | 600-600 |
| 138-pass5-badjeq-S1 | badjeq@S1 | 537.988 | 0.0575829 | 57.69 | 24.06 | 1.936 | 52 -> 59 | 600-600 |
| 139-pass5-random-S1 | random@S1 | 537.983 | 0.0575791 | 57.76 | 24.06 | 1.94 | 52 -> 59 | 600-600 |
| 140-pass5-arow50-S1 | arow50@S1 | 537.974 | 0.0575866 | 45.17 | 24.04 | 1.217 | 52 -> 56 | 600-600 |
| 141-pass5-arow50-S1 | arow50@S1 | 537.978 | 0.0575799 | 45.17 | 24.01 | 1.218 | 52 -> 56 | 600-600 |
| 142-pass5-random-S1 | random@S1 | 537.974 | 0.0575764 | 57.66 | 23.97 | 1.94 | 52 -> 59 | 600-600 |
| 143-pass5-signs-S1 | signs@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 144-pass5-signs-S1 | signs@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 145-pass5-random-S1 | random@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 146-pass5-highmant8-S1 | highmant8@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 147-pass5-highmant8-S1 | highmant8@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 148-pass5-random-S1 | random@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 149-pass5-lowmant8-S1 | lowmant8@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 150-pass5-lowmant8-S1 | lowmant8@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 151-pass5-random-S1 | random@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 152-pass6-random-S2 | random@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 153-pass6-maxalte-S2 | maxalte@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 154-pass6-maxalte-S2 | maxalte@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 155-pass6-random-S2 | random@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 156-pass6-negzero-S2 | negzero@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 157-pass6-negzero-S2 | negzero@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 158-pass6-random-S2 | random@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 159-pass6-lowmant8-S2 | lowmant8@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 160-pass6-lowmant8-S2 | lowmant8@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 161-pass6-random-S2 | random@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 162-pass6-bhalfeq-S2 | bhalfeq@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 163-pass6-bhalfeq-S2 | bhalfeq@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 164-pass6-random-S2 | random@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 165-pass6-highmant8-S2 | highmant8@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 166-pass6-highmant8-S2 | highmant8@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 167-pass6-random-S2 | random@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 168-pass6-hd4-S2 | hd4@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 169-pass6-hd4-S2 | hd4@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 170-pass6-random-S2 | random@S2 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |
| 171-close-random-S1 | random@S1 | NOT STARTED (the card-time rule: no run after 85 card-minutes) | | | | | | |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle carry that gain; E210's routes' constants absorb it, and the fractions of D are unaffected (E210.md 9).

## Registered against happened

| registered (E210.md, points-e210.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz | `session/config-start.json` {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; config end {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; step 7's read: aifoundry3: manifest kept on the box (build/q141k/), config TDP 0 W / 65 C / 600 MHz, et-who clean; 50,930 of 50,930 samples at 600 MHz; nothing set |
| the rest: 40 minutes since our last session on aifoundry3 (E207's) | E207's session end 07:53:54 PST Tue 17 Nov; step 7's and step 9's rest lines (departure 5) |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | G 11:05:20; last start 12:36, last end 14:36; the session 11:11:19-12:36:20, inside it |
| the never-run search repeated before the first card command and before the data commit | step 6n at 11:10:47; step 7 at 11:10:55 (within 30 minutes); step 12n at 12:40:09 |
| the opening: 60 s at rest, the smoke, THE PROBE (64 W / 63 C), the stop-path test; then 171 runs in the registered order | the smoke gate passed; the probe IN; the stop-path test passed; 142 of 171 runs started in the registered order (queue.json) |
| the stops and gates (KIT.md 4): board above 70 W on 3 samples, die at or above 70 C (the mean, or the risen latch), the die gate, two failed processes, K1, HUNG, the card-time rule, the window, the STOP file | no stop line fired (queue.json stop null); the card-time rule (no run after 85 card-minutes) left runs 143-171 unstarted (29 runs; a registered stop: the runs done stand and are scored as they stand); the die gate waited before runs (no run NO DATA by it); HUNG lines 0; runs not started 29 |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | the preflight "dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)" at step 2 and on the box at step 6; every process's rc in `session/runs/*/run.json` and queue.json; HUNG lines: 0 |
| the cap: no run after 85 card-minutes, the session ends by 95 | the close at 85.01 card-minutes, the last run started before 85; runs 143-171 not started by the card-time rule; the registered subset (the opening and passes 1-4) complete |
| the post waived; the package counter not read (E210.md 6) | the owner's words of Sun 15 Nov 2026 10:22:36 PST; not read |

## Device commands sent

READs only: the session's opening and closing `ettelem config` and its one 10 Hz sampler, all through E210's guard (dmcmd_audit_v2 GO, every send site a READ), and k6's step 7 config read through E128's guard; each rgm136 host opened the ops node of card 0 only (the runtime's creation aborts the submission queues of the card it enumerates, as every lab host's does: harmless on a card held alone); `et-who` sends no device command; steps 6n and 12n sent nothing to a card (file reads only). No set, no reset, no statistics reset, no firmware write, no PMIC write.

## Files

`session/` (the box's session directory `T<T0>-A`, copied back exact and scrubbed; among its files `session.log`, `queue.json`, `identity.json`, `config-start.*`, `config-end.*`, `stop-path.json`, `telemetry.jsonl.gz`, `smoke/`, `probe/`, `runs/`, `reads/`, `runner.out`, `runner.rc`, `MANIFEST.sha256`), `data-e210.json` (the frozen scorer's input), `reduce-e210.txt` (the reducer's table), `neverrun-e210-card.txt`, `neverrun-e210-card.json`, `named-by-card.json` (step 6n's report) and `neverrun-e210-late.txt`, `neverrun-e210-late.json`, `named-by-late.json` (step 12n's), copied in by the collection, `SHA256SUMS` (all of these; this README lies beside it). The scorer's outputs follow after the data commit (a later lane).

SPDX-License-Identifier: Apache-2.0
