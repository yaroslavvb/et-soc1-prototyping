# E206 arm A, 2026-11-16, aifoundry3 card 0 at 600 MHz as found: the matmul sweep: RAN FULL (the smoke, the stop-path test, 241 of 241 runs)

*Mon 16 Nov 2026 (week 47), PST. E206, registered before any datum (`eb2f7ac2`, [`E206.md`](../../../../tools/claims-v3/e206/E206.md) with its amendment A1; forecasts frozen in `forecast-e206.json`, sha256 `d8f3a8b1...`), kitted (`906699ea`, [`KIT.md`](../../../../tools/claims-v3/e206/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e206/CARD-LANE-BRIEF.md)), verified (verify-e206: HOLDS WITH FIXES; fix-e206: FIXED, before the land) and readiness-checked (ready-e206: READY WITH GAPS), all before any E206 datum; no E206 file changed since the kit (step 0: "86 of 86 as stated" at HEAD `906699ea`; steps 2 and 12: HISTORY OK). Q198's card lane `card-e206a`, orchestrated from aifoundry2. Run on the owner's go (his standing words of Sun 15 Nov 2026 and his matmul focus of Mon 16 Nov 2026: departure 1). rgm136 (E136's binary, unchanged), built today on the box through the kernel gate (BUILD-GATE KERNEL OK: .text 61315bf6a449c282... the registered; ELF ff2723b81e2ce409... not the registered (the difference lies in sections the card never loads); its loadable identity 649d40793e459e51... the pinned one). Arm B (aifoundry1 card 1) did not run: cancelled by the orchestrator (departure 5). Nothing was set on the card.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every point, order, window, threshold, stop and the cap is **registered** (E206.md; the kit). The per-point means and the millisecond and millijoule figures below are **desk arithmetic of the measured records** (the reducer's per-run values), not prices and not verdicts. **No score is here:** the frozen scorer (step 13, `score_e206.py`) runs on this directory only after it is committed, and a later lane commits its words beside it. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures, dated (Mon 16 Nov 2026, PST; placed before the results, as the round's go asks)

1. **The go, his words, verbatim (quoted without links).** Sun 15 Nov 2026: **10:05:42** "continue, all machines are up"; **10:22:36** "don't worry about discord post, just use the machines, nobody is using them"; **17:21:16** "Feel free to use more cards in parallel, I don't need to reserve them (things are automatically updated on [the lab dashboard's page]), currently I see only 1 card is being used, feel free to use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known); "don't worry about hitting the limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before 21:51:09); "Make sure to incorporate suggestions from Fable when planning experiments" (received between 21:55 and 22:07:09). Mon 16 Nov 2026, received at or before 09:48:24 (a voice transcription in which "matte mold" is the matmul and "FME" the tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation." Beside them, reports of his words posted on the round's Discussion (not his own text): Sun 19:34:12 "The aifoundry cards are all free right now (I can see it on the lab dashboard's live view, though a collector is running on them); feel free to use them."; Mon 11:01:08 "There's no usage limit; feel free to use all the cards without restriction, since they look free every time I check the dashboard." **His words name no experiment: the registered items are taken as their defaults** (E206.md 6): arm A on aifoundry3 card 0, 600 MHz as found, reads only, nothing set; 92.6 card-minutes planned, no run after 112, cap 120; the 40-minute rest; one session; the window of E206.md 6. E206 is the matmul sweep his words of Mon 16 Nov ask for.
2. **G = the booking:** the card lane's `book.sh take aifoundry3 card-e206a` printed BOOKED at **16:51:28 PST** Mon 16 Nov: last start G+1:30 and last end G+3:30 (E206.md 6), each rounded up to the whole minute: **18:22 and 20:22 PST** (`s02_window_e206.sh A 2026-11-16 18:22 20:22`, written by step 1; the window file's `RB_GO_EPOCH` is the moment step 1 wrote it, not his go). The session's first card command at 16:53:22 (before the last start) and its end at 18:22:16 (before the last end).
3. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE), step 7's reads (et-who clean), the session's holder check before its first card command, card 0's lock held for the session, and a plain `timeout 10` (never `-k`) on every device process.
4. **The host's package counter: not read** (E206.md 6): no step, option or code of the kit reads it (step 0's anchor G6: no line under `tools/claims-v3/e206` names it).
5. **Arm B cancelled by the orchestrator.** Since 11:04:17 PST Mon 16 Nov aifoundry1 is yielded to the model session's own matmul size sweeps (the Discussion, 11:01:08 PST), so the queue helper read QUEUE CANCELLED for arm B and its card lane returned SKIPPED without booking or reaching aifoundry1. E206 reads arm A alone (E206.md 6: arm B's points NO DATA, never a failure).
6. **The rest.** The box's last session of ours before E206 was E202's (session end 12:33:10 PST, data `ec9c9fe8`); the rest by the clock was 258 minutes at the booking; E206's committed rest rule, read on the box, printed at step 7 "259 minutes since E202's session end (2026-11-16 12:33:10 PST; dry sessions and blocks that opened no device skipped)" and at step 9 "260 minutes since E202's session end (2026-11-16 12:33:10 PST; dry sessions and blocks that opened no device skipped)" (40 required). Step 7's config read at 16:53:08 is reported apart from the session's card time.
7. **The never-run search re-run** (CARD-LANE-BRIEF.md 2 step 12): run from a copy of the registered scanner (never LAB's own `desk/neverrun_e206.py`, whose report mode writes `desk/neverrun-e206.json` beside itself: ready-e206's finding 1), its four scans made before the session (after step 4's FREE, before the sync and the build), the report at step 12; REPORTED below, it changes no rule.
8. **"Reads only" is true of the management node** (ready-e206's gap 5): as every runtime creation of the lab's runtime does, each host's creation also sends the ops node's abort on the card's submission queues; harmless on a card held alone (et-who empty, card 0's lock held, aifoundry3 has one card).
9. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3; the box ran the session with its own `python3` (3.12.3 by the readiness lane's look at 16:21:39 PST; not re-read by this lane). The orchestrating session is the round's session on its yvb3 Claude account.
10. **Sealed forecasts.** None was posted for E206 before this data commit (the round's record lists none; step 0's anchor S1 read "0 of 0"). The lab's own matmul model MM1-v0 froze its forecasts for E206's 119 points publicly at 13:04:57 PST (committed `2d1413f5`, `tools/matmul/mm1/v0/`) before any E206 datum: a later lane scores them on this directory; they are not one of E206's rules.
11. **The die line's hottest sensor** is read as E206.md's amendment A1 item 1 registers it (KIT.md section 4 item 1; not a departure): the latch (`minshire[2]`) read 87 C at the session's first sample and 87 C at its highest; the line trips on the shires' mean, or on the latch only once it has risen during the session.

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | 88.9 (no run after 112, cap 120); session 16:53:22-18:22:16 PST (T0 1794876802); step 7's config read at 16:53:08, reported apart | measured (the session's clock) |
| the smoke: p001, p046, p021 (2 s each), then the stop-path test | 16:53:55 p001: rc 0, 7 launches, check approx, cycles an op 1121.824 (0.83 of F1's point 1358.0); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 18.49 W over the rest on 27 samples (at least 2 W): ok; 16:53:59 p046: rc 0, 7 launches, check approx, cycles an op 819.198 (0.82 of F1's point 999.7); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 22.42 W over the rest on 26 samples (at least 2 W): ok; 16:54:01 p021: rc 0, 7 launches, check exact, cycles an op 787.54 (1.10 of F1's point 713.8); records: 0 runtime line(s) dropped, 0 unparsed, 0 not its command's; the host's card: its own (stderr ['/dev/et0_ops'] [0], held ['/dev/et0_ops']); the board 9.5 W over the rest on 26 samples (at least 2 W): ok; stop-path test passed: board tripped in 0.3 s, its file touched, start refused; die tripped in 0.1 s, its file touched, start refused; smoke gate passed: the runs start | measured |
| runs: planned, started, with counted launches, not started | 241 / 241 / 241 / 0; runs without a counted launch: 0; not started: none | measured |
| how the session ended | session end (T0 1794876802); queue.json stop: none; runner rc 0 (runner.rc); HUNG lines: 0 | measured |
| telemetry samples, and those at 600 MHz | 53,265 / 53,265; off the clock: 0 | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | 59.54 W at 17:16:40; 61 C at 18:10:25; 87 C / 87 C (the stops: arm A 70 W / 70 C; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it) | measured |
| the session's rest reading (the smoke's 30 s) | smoke rest: 299 samples, board 24.57 W, die 51 C (the latch [87]); the die gate 55.0 C | measured |
| the opening and closing configuration reads | {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523} | measured (READ) |
| the identity lines | the card's identity: PCIe target /dev/et0_mgmt, physical device ID 0; the identity read: et-who {"other_off_card": 0, "other_on_card": 0, "ours_off_card": 0, "ours_on_card": 2, "ours_on_mgmt": 1} (counts by card), the sampler holds ['/dev/et0_mgmt']: card 0 only; the smoke hosts: {"p001": {"stderr_targets": ["/dev/et0_ops"], "held": ["/dev/et0_ops"]}, "p021": {"stderr_targets": ["/dev/et0_ops"], "held": ["/dev/et0_ops"]}, "p046": {"stderr_targets": ["/dev/et0_ops"], "held": ["/dev/et0_ops"]}} | measured |
| every check of C the hosts printed | {"approx": 131, "exact": 110} (the smoke: ['approx', 'approx', 'exact']) | measured |
| the die at each run's start (the shires' mean) and the highest in a run's work window | 52.0-55.0 C; 61 C | measured |
| the never-run search re-run before the commit (desk/neverrun_e206.py, from a copy) | The re-run in the go lines' form (the copied scanner, four scans made at 16:52 PST before the session: the lab's committed data at HEAD, our lanes' folders, this desk's work folders, our folders on aifoundry3) reads "E206 points never run on any card: 0 of 119 ...; never on aifoundry3: 102; never on aifoundry1 card 1: 116 (110 of arm B's 113); points whose only card records name no card: 90". That reading counts desk records as runs, which a desk inspection of its hits (post hoc) shows: in our lanes' folders, the E206 kit lanes' desk-test stand-ins (the doubles' records and host command lines; the six extra "aifoundry3" points come from the runbook test's stand-in boxes) and the model track's compilations of the lab's records; in this desk's work folders, the command lists of the model session's DRY pass of its sweep (one folder, 15:40:28 PST: 25 E206 shapes, no device). Read without the lanes' folders (post hoc, the same copied scanner): 75 of 119 never run on any card (95 registered; the 20 more are all that dry pass's commands), never on aifoundry3: 108 and never on aifoundry1 card 1: 116, both as registered. No card record of an E206 point newer than the registration was found: the model session's run folder held no GEMM record at the scan. | a desk read, REPORTED (the reading without the lanes' folders: post hoc) |

### Per point (each point's two runs: pass 1 / pass 2; the reducer's values, `reduce-e206.txt` and `data-e206.json`)

J over idle = (p_work - p_rest) x t_gemm and J with the card at rest = p_work x t_gemm, a GEMM (the scorer's form); seconds in ms and joules in mJ a GEMM; cycles an op the median of the host's counter (the mean over minions) over the counted launches, cycles a GEMM the median of the slowest minion's counter over passes. Desk arithmetic of measured records.

| point | family | M x N x K | format | kind | shires (mask) | runs | cycles an op | cycles a GEMM | ms a GEMM | p_work W | p_rest W | mJ over idle (mean) | mJ at rest (mean) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| p001 | star | 2048 x 2048 x 2048 | fp32 | random | 32 (full) | 2 | 1121.4 | 2,296,724 | 3.831 / 3.832 | 44.76 | 24.9 | 75.94 / 76.25 (76.09) | 171.5 |
| p002 | star | 2048 x 2048 x 8192 | int8 | random | 32 (full) | 2 | 1136.8 | 2,328,358 | 3.884 / 3.884 | 34.28 | 24.85 | 36.71 / 36.51 (36.61) | 133.1 |
| p003 | star | 2048 x 2048 x 4096 | fp16 | random | 32 (full) | 2 | 1121.3 | 2,296,553 | 3.831 / 3.831 | 43.28 | 24.8 | 70.87 / 70.72 (70.8) | 165.8 |
| p004 | star | 1024 x 2048 x 2048 | fp32 | random | 32 (full) | 2 | 831.77 | 932,136 | 1.555 / 1.555 | 49.39 | 24.46 | 38.67 / 38.83 (38.75) | 76.79 |
| p005 | star | 1024 x 2048 x 8192 | int8 | random | 32 (full) | 2 | 866.23 | 993,236 | 1.657 / 1.657 | 35.37 | 24.84 | 17.45 / 17.45 (17.45) | 58.6 |
| p006 | star | 4096 x 2048 x 2048 | fp32 | random | 32 (full) | 2 | 1121.2 | 4,592,685 | 7.66 / 7.662 | 44.78 | 24.9 | 152 / 152.6 (152.3) | 343.1 |
| p007 | star | 4096 x 2048 x 8192 | int8 | random | 32 (full) | 2 | 1137 | 4,657,571 | 7.769 / 7.771 | 34.2 | 24.82 | 72.95 / 72.81 (72.88) | 265.8 |
| p008 | star | 8192 x 2048 x 2048 | fp32 | random | 32 (full) | 2 | 1121.2 | 9,185,706 | 15.32 / 15.33 | 44.48 | 24.73 | 301.7 / 303.6 (302.7) | 681.8 |
| p009 | star | 8192 x 2048 x 8192 | int8 | random | 32 (full) | 2 | 1136.9 | 9,314,219 | 15.54 / 15.54 | 34.27 | 24.83 | 146.8 / 146.4 (146.6) | 532.3 |
| p010 | star | 8192 x 2048 x 4096 | fp16 | random | 32 (full) | 2 | 1121.4 | 9,187,402 | 15.32 / 15.32 | 43.23 | 24.67 | 285 / 283.9 (284.5) | 662.5 |
| p011 | star | 2048 x 512 x 2048 | fp32 | random | 32 (full) | 2 | 831.72 | 466,098 | 0.7775 / 0.7775 | 49.79 | 24.77 | 19.45 / 19.45 (19.45) | 38.71 |
| p012 | star | 2048 x 512 x 8192 | int8 | random | 32 (full) | 2 | 866.01 | 496,570 | 0.8283 / 0.8282 | 35.36 | 24.82 | 8.722 / 8.742 (8.732) | 29.29 |
| p013 | star | 2048 x 1024 x 2048 | fp32 | random | 32 (full) | 2 | 831.8 | 932,283 | 1.555 / 1.555 | 49.77 | 24.75 | 38.93 / 38.88 (38.9) | 77.39 |
| p014 | star | 2048 x 1024 x 8192 | int8 | random | 32 (full) | 2 | 866.25 | 993,213 | 1.657 / 1.657 | 35.36 | 24.82 | 17.38 / 17.55 (17.47) | 58.59 |
| p015 | star | 2048 x 4096 x 2048 | fp32 | random | 32 (full) | 2 | 1374.6 | 5,634,664 | 9.399 / 9.42 | 41.72 | 24.8 | 159.3 / 159.2 (159.3) | 392.6 |
| p016 | star | 2048 x 4096 x 8192 | int8 | random | 32 (full) | 2 | 1361.3 | 5,577,163 | 9.309 / 9.3 | 33.59 | 24.91 | 80.99 / 80.53 (80.76) | 312.5 |
| p017 | star | 2048 x 8192 x 2048 | fp32 | random | 32 (full) | 2 | 1375 | 11,345,835 | 18.93 / 18.92 | 41.42 | 24.51 | 320.4 / 320 (320.2) | 784 |
| p018 | star | 2048 x 8192 x 8192 | int8 | random | 32 (full) | 2 | 1368.4 | 11,289,985 | 18.84 / 18.83 | 33.38 | 24.62 | 164.5 / 165.3 (164.9) | 628.7 |
| p019 | star | 2048 x 8192 x 4096 | fp16 | random | 32 (full) | 2 | 1375.7 | 11,348,048 | 18.93 / 18.92 | 40.79 | 24.88 | 301.7 / 300.4 (301) | 771.9 |
| p020 | star | 2048 x 2048 x 512 | fp32 | random | 32 (full) | 2 | 760.11 | 438,627 | 0.7316 / 0.7317 | 50.52 | 24.77 | 18.81 / 18.87 (18.84) | 36.96 |
| p021 | star | 2048 x 2048 x 2048 | int8 | random | 32 (full) | 2 | 787.54 | 453,443 | 0.7564 / 0.7564 | 34.61 | 24.69 | 7.435 / 7.564 (7.499) | 26.17 |
| p022 | star | 2048 x 2048 x 1024 | fp32 | random | 32 (full) | 2 | 819.17 | 926,333 | 1.545 / 1.545 | 49.95 | 24.77 | 38.86 / 38.95 (38.91) | 77.19 |
| p023 | star | 2048 x 2048 x 4096 | int8 | random | 32 (full) | 2 | 854.13 | 985,187 | 1.644 / 1.643 | 35.26 | 24.8 | 17.27 / 17.11 (17.19) | 57.94 |
| p024 | star | 2048 x 2048 x 4096 | fp32 | random | 32 (full) | 2 | 1434.7 | 5,876,846 | 9.801 / 9.806 | 41.07 | 24.55 | 160.6 / 163.5 (162.1) | 402.7 |
| p025 | star | 2048 x 2048 x 16384 | int8 | random | 32 (full) | 2 | 1437.5 | 5,888,111 | 9.824 / 9.825 | 33.07 | 24.56 | 83.7 / 83.41 (83.56) | 324.9 |
| p026 | star | 2048 x 2048 x 8192 | fp32 | random | 32 (full) | 2 | 1521.9 | 12,467,532 | 20.8 / 20.8 | 40.32 | 24.75 | 322.1 / 325.8 (324) | 838.7 |
| p027 | star | 2048 x 2048 x 32768 | int8 | random | 32 (full) | 2 | 1529.7 | 12,530,973 | 20.91 / 20.9 | 32.78 | 24.57 | 171.8 / 171.6 (171.7) | 685.3 |
| p028 | star | 2048 x 2048 x 16384 | fp16 | random | 32 (full) | 2 | 1521.7 | 12,465,584 | 20.79 / 20.79 | 39.36 | 24.84 | 301.5 / 302.1 (301.8) | 818.3 |
| p029 | kladder | 1024 x 512 x 512 | fp32 | random | 32 (full) | 2 | 537.98 | 34,521 | 0.05758 / 0.05758 | 58.7 | 24.83 | 1.953 / 1.949 (1.951) | 3.38 |
| p030 | kladder | 1024 x 512 x 2048 | int8 | random | 32 (full) | 2 | 388.02 | 24,946 | 0.04161 / 0.04161 | 39.55 | 24.79 | 0.6146 / 0.6146 (0.6146) | 1.646 |
| p031 | kladder | 1024 x 512 x 1024 | fp16 | random | 32 (full) | 2 | 537.98 | 34,520 | 0.05758 / 0.05758 | 55.7 | 24.75 | 1.777 / 1.788 (1.783) | 3.207 |
| p032 | kladder | 1024 x 512 x 1024 | fp32 | random | 32 (full) | 2 | 805.86 | 115,071 | 0.1919 / 0.1919 | 50.17 | 24.89 | 4.843 / 4.862 (4.852) | 9.63 |
| p033 | kladder | 1024 x 512 x 4096 | int8 | random | 32 (full) | 2 | 844.9 | 122,126 | 0.2037 / 0.2037 | 35.07 | 24.91 | 2.068 / 2.072 (2.07) | 7.144 |
| p034 | kladder | 1024 x 512 x 2048 | fp32 | random | 32 (full) | 2 | 831.72 | 233,062 | 0.3888 / 0.3887 | 49.64 | 24.72 | 9.657 / 9.721 (9.689) | 19.3 |
| p035 | kladder | 1024 x 512 x 8192 | int8 | random | 32 (full) | 2 | 866.04 | 248,290 | 0.4141 / 0.4141 | 35.33 | 24.82 | 4.344 / 4.357 (4.35) | 14.63 |
| p036 | kladder | 1024 x 512 x 4096 | fp16 | random | 32 (full) | 2 | 831.72 | 233,060 | 0.3888 / 0.3888 | 48.15 | 24.91 | 9.043 / 9.027 (9.035) | 18.72 |
| p037 | kladder | 1024 x 512 x 4096 | fp32 | random | 32 (full) | 2 | 831.13 | 465,862 | 0.777 / 0.7771 | 49.58 | 24.72 | 19.36 / 19.27 (19.32) | 38.53 |
| p038 | kladder | 1024 x 512 x 16384 | int8 | random | 32 (full) | 2 | 866.33 | 496,366 | 0.8279 / 0.828 | 35.34 | 24.9 | 8.627 / 8.661 (8.644) | 29.26 |
| p039 | kladder | 1024 x 512 x 8192 | fp32 | random | 32 (full) | 2 | 1395.1 | 1,440,591 | 2.403 / 2.403 | 40.89 | 24.8 | 38.65 / 38.67 (38.66) | 98.26 |
| p040 | kladder | 1024 x 512 x 32768 | int8 | random | 32 (full) | 2 | 1426.6 | 1,483,111 | 2.473 / 2.474 | 32.56 | 24.65 | 19.51 / 19.67 (19.59) | 80.55 |
| p041 | kladder | 1024 x 512 x 16384 | fp32 | random | 32 (full) | 2 | 1579.2 | 3,234,259 | 5.383 / 5.403 | 40.06 | 24.82 | 82.2 / 82.13 (82.16) | 216 |
| p042 | kladder | 1024 x 512 x 65536 | int8 | random | 32 (full) | 2 | 1546.3 | 3,166,828 | 5.277 / 5.286 | 32.91 | 24.58 | 44.09 / 43.95 (44.02) | 173.8 |
| p043 | kladder | 1024 x 512 x 32768 | fp16 | random | 32 (full) | 2 | 1580.2 | 3,236,167 | 5.391 / 5.392 | 39.17 | 24.88 | 77.41 / 76.72 (77.07) | 211.2 |
| p044 | square | 1024 x 1024 x 1024 | fp32 | random | 32 (full) | 2 | 819.32 | 231,666 | 0.3865 / 0.3864 | 49.95 | 24.75 | 9.716 / 9.753 (9.735) | 19.3 |
| p045 | square | 1024 x 1024 x 1024 | fp16 | random | 32 (full) | 2 | 744.58 | 107,687 | 0.1796 / 0.1796 | 48.45 | 24.43 | 4.311 / 4.318 (4.315) | 8.704 |
| p046 | square | 2048 x 2048 x 2048 | fp16 | random | 32 (full) | 2 | 819.17 | 926,341 | 1.545 / 1.545 | 48.28 | 24.89 | 36.15 / 36.13 (36.14) | 74.6 |
| p047 | square | 3072 x 3072 x 3072 | fp32 | random | 32 (full) | 2 | 1150.5 | 7,953,475 | 13.27 / 13.27 | 44.06 | 24.81 | 247.4 / 263.6 (255.5) | 584.6 |
| p048 | square | 3072 x 3072 x 3072 | fp16 | random | 32 (full) | 2 | 1117.5 | 3,862,367 | 6.443 / 6.443 | 43.59 | 24.83 | 121.5 / 120.4 (120.9) | 280.9 |
| p049 | square | 4096 x 4096 x 4096 | fp32 | random | 32 (full) | 2 | 1418.3 | 23,242,152 | 38.77 / 38.78 | 41.23 | 24.79 | 638.1 / 636.9 (637.5) | 1599 |
| p050 | square | 4096 x 4096 x 4096 | fp16 | random | 32 (full) | 2 | 1376.4 | 11,287,902 | 18.84 / 18.82 | 40.78 | 24.82 | 299.4 / 301.6 (300.5) | 767.9 |
| p051 | square | 4096 x 4096 x 4096 | int8 | random | 32 (full) | 2 | 1110.6 | 4,549,262 | 7.587 / 7.588 | 34.51 | 24.83 | 73.25 / 73.61 (73.43) | 261.9 |
| p052 | square | 6144 x 6144 x 6144 | fp32 | random | 32 (full) | 2 | 1435.7 | 79,393,100 | 132.5 / 132.4 | 40.95 | 24.64 | 2140 / 2179 (2160) | 5424 |
| p053 | square | 6144 x 6144 x 6144 | fp16 | random | 32 (full) | 2 | 1229.5 | 34,174,068 | 56.95 / 56.68 | 42.16 | 24.79 | 988 / 985.6 (986.8) | 2395 |
| p054 | square | 6144 x 6144 x 6144 | int8 | random | 32 (full) | 2 | 1129.5 | 15,616,295 | 26.05 / 26.05 | 34.55 | 24.86 | 252 / 252.8 (252.4) | 899.9 |
| p055 | square | 8192 x 8192 x 8192 | fp32 | random | 32 (full) | 2 | 1450.1 | 190,068,861 | 317.3 / 317.2 | 41.03 | 24.83 | 5147 / 5136 (5141) | 1.302e+04 |
| p056 | square | 8192 x 8192 x 8192 | fp16 | random | 32 (full) | 2 | 1388.7 | 91,414,264 | 152.6 / 152.5 | 40.7 | 24.93 | 2410 / 2403 (2406) | 6208 |
| p057 | square | 8192 x 8192 x 8192 | int8 | random | 32 (full) | 2 | 1368.6 | 45,151,804 | 75.38 / 75.26 | 33.56 | 24.85 | 657.3 / 655.6 (656.4) | 2528 |
| p058 | extreme | 8192 x 512 x 2048 | fp32 | random | 32 (full) | 2 | 1407.4 | 2,913,062 | 4.858 / 4.861 | 41.11 | 24.81 | 79.28 / 79.08 (79.18) | 199.7 |
| p059 | extreme | 8192 x 512 x 8192 | int8 | random | 32 (full) | 2 | 1448.3 | 3,012,661 | 5.024 / 5.028 | 32.96 | 24.84 | 40.74 / 40.9 (40.82) | 165.7 |
| p060 | extreme | 1024 x 8192 x 2048 | fp32 | random | 32 (full) | 2 | 1368.4 | 5,664,373 | 9.454 / 9.454 | 41.78 | 24.91 | 159.2 / 160 (159.6) | 395 |
| p061 | extreme | 1024 x 8192 x 8192 | int8 | random | 32 (full) | 2 | 1365.2 | 5,648,020 | 9.424 / 9.429 | 33.52 | 24.88 | 81.42 / 81.56 (81.49) | 316 |
| p062 | extreme | 1024 x 7680 x 2048 | fp32 | random | 32 (full) | 2 | 1082.1 | 4,207,509 | 7.018 / 7.019 | 45.35 | 24.79 | 143.9 / 144.7 (144.3) | 318.3 |
| p063 | extreme | 1024 x 7680 x 8192 | int8 | random | 32 (full) | 2 | 1093.5 | 4,254,200 | 7.097 / 7.097 | 34.61 | 24.86 | 69.26 / 69.2 (69.23) | 245.6 |
| p064 | extreme | 8192 x 8192 x 512 | fp32 | random | 32 (full) | 2 | 1141.6 | 9,554,054 | 15.94 / 15.94 | 44.28 | 24.84 | 310.4 / 309.4 (309.9) | 705.8 |
| p065 | extreme | 8192 x 8192 x 2048 | int8 | random | 32 (full) | 2 | 1166.3 | 9,759,165 | 16.28 / 16.28 | 33.99 | 24.8 | 149.1 / 150.2 (149.6) | 553.3 |
| p066 | extreme | 8192 x 512 x 8192 | fp32 | random | 32 (full) | 2 | 1395.5 | 11,528,746 | 19.24 / 19.23 | 40.59 | 24.52 | 308 / 310 (309) | 780.6 |
| p067 | extreme | 1024 x 8192 x 8192 | fp32 | random | 32 (full) | 2 | 1436.8 | 23,541,094 | 39.27 / 39.27 | 41.19 | 24.89 | 636.9 / 643.1 (640) | 1617 |
| p068 | extreme | 3072 x 2560 x 3584 | fp32 | random | 32 (full) | 2 | 1173.4 | 7,885,607 | 13.15 / 13.16 | 43.98 | 24.74 | 251.6 / 254.5 (253.1) | 578.5 |
| p069 | extreme | 3072 x 2560 x 7168 | fp16 | random | 32 (full) | 2 | 1173.7 | 7,887,811 | 13.16 / 13.16 | 42.61 | 24.81 | 233.5 / 234.9 (234.2) | 560.6 |
| p070 | extreme | 3072 x 2560 x 14336 | int8 | random | 32 (full) | 2 | 1179.5 | 7,927,447 | 13.23 / 13.23 | 33.85 | 24.57 | 121.8 / 123.6 (122.7) | 447.7 |
| p071 | anchor | 1 block(s) of 1024 x 512 x 512 a pass | fp32 | random | 32 (full) | 2 | 536.86 | 34,444 | 0.05745 / 0.05745 | 58.09 | 24.45 | 1.936 / 1.93 (1.933) | 3.337 |
| p072 | anchor | 1 block(s) of 1024 x 512 x 1024 a pass | fp16 | random | 32 (full) | 2 | 536.87 | 34,444 | 0.05745 / 0.05746 | 55.31 | 24.69 | 1.761 / 1.759 (1.76) | 3.178 |
| p073 | anchor | 1 block(s) of 1024 x 512 x 2048 a pass | int8 | random | 32 (full) | 2 | 299.75 | 19,295 | 0.03218 / 0.03219 | 42.81 | 24.18 | 0.6023 / 0.5971 (0.5997) | 1.378 |
| p074 | anchor | 8 block(s) of 1024 x 512 x 512 a pass C shared | fp32 | random | 32 (full) | 2 | 753.89 | 439,937 | 0.7338 / 0.7339 | 51.01 | 24.59 | 19.42 / 19.36 (19.39) | 37.43 |
| p075 | anchor | 8 block(s) of 1024 x 512 x 1024 a pass C shared | fp16 | random | 32 (full) | 2 | 753.9 | 439,939 | 0.7338 / 0.7338 | 48.47 | 24.05 | 17.82 / 18.01 (17.92) | 35.57 |
| p076 | anchor | 8 block(s) of 1024 x 512 x 2048 a pass C shared | int8 | random | 32 (full) | 2 | 786.38 | 458,795 | 0.7653 / 0.7653 | 34.74 | 24.32 | 7.951 / 7.993 (7.972) | 26.58 |
| p077 | anchor | 16 block(s) of 1024 x 512 x 512 a pass C shared | fp32 | random | 32 (full) | 2 | 1410.8 | 1,444,655 | 2.41 / 2.41 | 40.11 | 24.23 | 38.25 / 38.26 (38.26) | 96.66 |
| p078 | anchor | 16 block(s) of 1024 x 512 x 1024 a pass C shared | fp16 | random | 32 (full) | 2 | 1410.8 | 1,444,680 | 2.41 / 2.41 | 39.09 | 24.14 | 35.99 / 36.07 (36.03) | 94.21 |
| p079 | anchor | 16 block(s) of 1024 x 512 x 2048 a pass C shared | int8 | random | 32 (full) | 2 | 1403.9 | 1,437,613 | 2.398 / 2.399 | 32.17 | 24.27 | 18.71 / 19.19 (18.95) | 77.16 |
| p080 | zeros | 1024 x 512 x 512 | fp32 | zeros | 32 (full) | 2 | 537.99 | 34,522 | 0.05758 / 0.05758 | 28.82 | 24.72 | 0.2309 / 0.2413 (0.2361) | 1.659 |
| p081 | zeros | 1024 x 512 x 2048 | int8 | zeros | 32 (full) | 2 | 388.01 | 24,946 | 0.04161 / 0.0416 | 28.77 | 24.48 | 0.181 / 0.176 (0.1785) | 1.197 |
| p082 | zeros | 1024 x 512 x 2048 | fp32 | zeros | 32 (full) | 2 | 831.74 | 233,066 | 0.3888 / 0.3887 | 28.66 | 24.27 | 1.714 / 1.699 (1.707) | 11.14 |
| p083 | zeros | 1024 x 512 x 4096 | fp16 | zeros | 32 (full) | 2 | 831.74 | 233,066 | 0.3887 / 0.3888 | 28.8 | 24.48 | 1.668 / 1.687 (1.677) | 11.2 |
| p084 | zeros | 1024 x 512 x 16384 | fp32 | zeros | 32 (full) | 2 | 1576.2 | 3,228,109 | 5.381 / 5.391 | 28.2 | 24.25 | 20.93 / 21.65 (21.29) | 151.9 |
| p085 | zeros | 1024 x 512 x 65536 | int8 | zeros | 32 (full) | 2 | 1545.4 | 3,164,938 | 5.276 / 5.288 | 27.96 | 24.16 | 20 / 20.1 (20.05) | 147.7 |
| p086 | zeros | 2048 x 2048 x 2048 | fp32 | zeros | 32 (full) | 2 | 1121.4 | 2,296,751 | 3.832 / 3.832 | 28.55 | 24.33 | 16.29 / 16.09 (16.19) | 109.4 |
| p087 | zeros | 2048 x 2048 x 4096 | fp16 | zeros | 32 (full) | 2 | 1121.2 | 2,296,499 | 3.831 / 3.831 | 28.53 | 24.29 | 15.99 / 16.51 (16.25) | 109.3 |
| p088 | zeros | 2048 x 2048 x 8192 | int8 | zeros | 32 (full) | 2 | 1136.9 | 2,328,521 | 3.884 / 3.884 | 28.28 | 24.55 | 14.1 / 14.88 (14.49) | 109.8 |
| p089 | zeros | 8192 x 8192 x 8192 | fp32 | zeros | 32 (full) | 2 | 1450.5 | 190,127,436 | 317.3 / 317.3 | 28.7 | 24.69 | 1299 / 1245 (1272) | 9105 |
| p090 | zeros | 8192 x 8192 x 8192 | int8 | zeros | 32 (full) | 2 | 1368.8 | 45,161,862 | 75.3 / 75.42 | 28.02 | 24.28 | 288.4 / 275.3 (281.8) | 2112 |
| p091 | zeros | 8192 x 8192 x 512 | fp32 | zeros | 32 (full) | 2 | 1141.4 | 9,555,678 | 15.94 / 15.94 | 28.73 | 24.27 | 70.45 / 71.73 (71.09) | 457.9 |
| p092 | zeros | 1 block(s) of 1024 x 512 x 512 a pass | fp32 | zeros | 32 (full) | 2 | 536.86 | 34,443 | 0.05745 / 0.05746 | 28.21 | 24.35 | 0.2177 / 0.2255 (0.2216) | 1.621 |
| p093 | zeros | 16 block(s) of 1024 x 512 x 512 a pass C shared | fp32 | zeros | 32 (full) | 2 | 1410.9 | 1,444,743 | 2.41 / 2.41 | 27.91 | 24.31 | 8.773 / 8.592 (8.682) | 67.28 |
| p094 | subset | 512 x 1024 x 2048 (rows 128 and columns 128 of each 1024 x 512 C block) | fp32 | random | 1 (s1) | 2 | 1215.4 | 9,956,582 | 16.61 / 16.61 | 24.99 | 24.28 | 11.29 / 12.29 (11.79) | 415 |
| p095 | subset | 512 x 1024 x 8192 (rows 128 and columns 128 of each 1024 x 512 C block) | int8 | random | 1 (s1) | 2 | 1258.8 | 10,311,742 | 17.2 / 17.2 | 24.66 | 24.25 | 7.396 / 6.88 (7.138) | 424.2 |
| p096 | subset | 512 x 4096 x 2048 (rows 128 and columns 512 of each 1024 x 512 C block) | fp32 | random | 4 (s4r) | 2 | 1003 | 9,968,412 | 16.64 / 16.62 | 27.09 | 24.35 | 45.91 / 45.38 (45.65) | 450.6 |
| p097 | subset | 512 x 4096 x 8192 (rows 128 and columns 512 of each 1024 x 512 C block) | int8 | random | 4 (s4r) | 2 | 1037.1 | 10,314,550 | 17.2 / 17.2 | 25.7 | 24.29 | 24.43 / 24.08 (24.26) | 442.1 |
| p098 | subset | 1024 x 4096 x 2048 (rows 256 and columns 512 of each 1024 x 512 C block) | fp32 | random | 8 (s8r) | 2 | 1037.4 | 9,087,087 | 15.16 / 15.16 | 29.78 | 24.36 | 82.47 / 81.72 (82.09) | 451.4 |
| p099 | subset | 1024 x 4096 x 8192 (rows 256 and columns 512 of each 1024 x 512 C block) | int8 | random | 8 (s8r) | 2 | 1074.2 | 9,533,244 | 15.77 / 15.82 | 27.33 | 24.49 | 45.56 / 43.99 (44.78) | 431.7 |
| p100 | subset | 4096 x 1024 x 2048 (rows 1024 and columns 128 of each 1024 x 512 C block) | fp32 | random | 8 (s8c) | 2 | 1231.9 | 10,092,320 | 16.84 / 16.83 | 28.87 | 24.37 | 75.59 / 75.76 (75.67) | 485.9 |
| p101 | subset | 4096 x 1024 x 8192 (rows 1024 and columns 128 of each 1024 x 512 C block) | int8 | random | 8 (s8c) | 2 | 1226.6 | 10,049,126 | 16.76 / 16.76 | 26.76 | 24.38 | 40.57 / 38.97 (39.77) | 448.5 |
| p102 | subset | 2048 x 4096 x 2048 (rows 512 and columns 512 of each 1024 x 512 C block) | fp32 | random | 16 (s16) | 2 | 1123.5 | 9,203,806 | 15.35 / 15.35 | 34.27 | 24.23 | 153.4 / 154.6 (154) | 526.1 |
| p103 | subset | 2048 x 4096 x 8192 (rows 512 and columns 512 of each 1024 x 512 C block) | int8 | random | 16 (s16) | 2 | 1136.3 | 9,308,851 | 15.53 / 15.53 | 29.54 | 24.38 | 80.9 / 79.12 (80.01) | 458.6 |
| p104 | subset | 4096 x 4096 x 2048 | fp32 | random | 32 (full) | 2 | 1375.6 | 11,279,898 | 18.83 / 18.83 | 40.93 | 24.15 | 315.4 / 316.6 (316) | 770.6 |
| p105 | subset | 4096 x 4096 x 8192 | int8 | random | 32 (full) | 2 | 1359.3 | 11,136,041 | 18.57 / 18.6 | 32.98 | 24.25 | 161.7 / 162.9 (162.3) | 613 |
| p106 | subset | 128 x 128 x 512 (rows 128 and columns 128 of each 1024 x 512 C block) | fp32 | random | 1 (s1) | 2 | 538.83 | 34,485 | 0.05752 / 0.05752 | 25.19 | 24.29 | 0.05005 / 0.05407 (0.05206) | 1.449 |
| p107 | subset | 128 x 128 x 2048 (rows 128 and columns 128 of each 1024 x 512 C block) | int8 | random | 1 (s1) | 2 | 389.31 | 24,916 | 0.04156 / 0.04154 | 24.68 | 24.26 | 0.0185 / 0.01662 (0.01756) | 1.026 |
| p108 | subset | 256 x 512 x 512 (rows 256 and columns 512 of each 1024 x 512 C block) | fp32 | random | 8 (s8r) | 2 | 538.05 | 34,489 | 0.05753 / 0.05753 | 32.21 | 24.52 | 0.4412 / 0.443 (0.4421) | 1.853 |
| p109 | subset | 256 x 512 x 2048 (rows 256 and columns 512 of each 1024 x 512 C block) | int8 | random | 8 (s8r) | 2 | 387.97 | 24,936 | 0.04159 / 0.04159 | 28.06 | 24.63 | 0.1435 / 0.1418 (0.1427) | 1.167 |
| p110 | kinds | 1024 x 512 x 512 | fp32 | real | 32 (full) | 2 | 537.99 | 34,520 | 0.05758 / 0.05758 | 57.72 | 24.31 | 1.916 / 1.931 (1.923) | 3.323 |
| p111 | kinds | 2048 x 2048 x 2048 | fp32 | real | 32 (full) | 2 | 1121.4 | 2,296,918 | 3.832 / 3.832 | 43.84 | 24.46 | 74.3 / 74.18 (74.24) | 168 |
| p112 | kinds | 1024 x 512 x 1024 | fp16 | real | 32 (full) | 2 | 537.98 | 34,522 | 0.05758 / 0.05758 | 54.87 | 24.38 | 1.756 / 1.756 (1.756) | 3.159 |
| p113 | kinds | 2048 x 2048 x 2048 | fp16 | real | 32 (full) | 2 | 819.18 | 926,353 | 1.545 / 1.545 | 47.13 | 24.38 | 35.28 / 35.05 (35.16) | 72.84 |
| p114 | kinds | 1024 x 512 x 2048 | int8 | real | 32 (full) | 2 | 388.02 | 24,945 | 0.04161 / 0.04161 | 36.65 | 24.23 | 0.5172 / 0.5168 (0.517) | 1.525 |
| p115 | kinds | 2048 x 2048 x 2048 | int8 | real | 32 (full) | 2 | 787.55 | 453,441 | 0.7563 / 0.7564 | 32.95 | 24.41 | 6.467 / 6.444 (6.456) | 24.92 |
| p116 | kinds | 1024 x 512 x 512 | fp32 | sparse50 | 32 (full) | 2 | 537.99 | 34,520 | 0.05758 / 0.05757 | 39.44 | 24.21 | 0.8796 / 0.874 (0.8768) | 2.271 |
| p117 | kinds | 2048 x 2048 x 2048 | fp32 | sparse50 | 32 (full) | 2 | 1121.5 | 2,296,956 | 3.831 / 3.831 | 35.1 | 24.28 | 41.3 / 41.61 (41.45) | 134.5 |
| p118 | kinds | 1024 x 512 x 2048 | int8 | sparse50 | 32 (full) | 2 | 388.02 | 24,943 | 0.04161 / 0.04161 | 36.61 | 24.31 | 0.5152 / 0.5084 (0.5118) | 1.523 |
| p119 | kinds | 2048 x 2048 x 2048 | int8 | sparse50 | 32 (full) | 2 | 787.54 | 453,444 | 0.7564 / 0.7564 | 32.5 | 24.25 | 6.233 / 6.244 (6.239) | 24.58 |

### The ties (p001: the start, the middle and the end)

| run | ms a GEMM | cycles an op | p_work W | p_rest W | mJ over idle | mJ at rest | die C (start -> highest) |
|---|---|---|---|---|---|---|---|
| 1 | 3.8314 | 1121.4 | 43.69 | 24.05 | 75.25 | 167.4 | 52 -> 56 |
| 121 | 3.831 | 1121.2 | 43.99 | 24.18 | 75.89 | 168.5 | 53 -> 56 |
| 241 | 3.8309 | 1121.2 | 44.75 | 24.82 | 76.35 | 171.4 | 55 -> 58 |

The drift reading over the ties is the scorer's (REPORTED), after the data commit.

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle and with the card at rest carry that gain; a later calibration would move every one by the same factor.

## Registered against happened

| registered (E206.md, plan-e206.json, KIT.md) | happened |
|---|---|
| arm A: aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz (KIT.md 4) | `session/config-start.json` {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; config end {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}; step 7's read the same; 53,265 of 53,265 samples at 600 MHz; nothing set |
| the rest: 40 minutes since our last session on the box (E206.md 6) | E202's session end 12:33:10 PST; step 7's and step 9's rest lines (departure 6) |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | G 16:51:28; last start 18:22, last end 20:22; the session 16:53:22-18:22:16, inside it |
| the smoke, then the stop-path test; the order tie, pass 1, tie, pass 2, tie | smoke gate passed; stop-path test passed: board tripped in 0.3 s, its file touched, start...; 241 of 241 runs in the registered order (queue.json) |
| the stops and gates (KIT.md 4): board above 70 W on 3 samples, die at or above 70 C (the mean, or the risen latch), the die gate, two failed processes, K1, HUNG, the card-time rule, the window, the STOP file | none fired (queue.json stop null); HUNG lines 0; runs not started 0 |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | the preflight "dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)" at step 2 and on the box at step 6; every process's rc in `session/runs/*/run.json` and queue.json; HUNG lines: 0 |
| the cap: no run after 112 card-minutes, the session ends by 120 | the close at 88.9 card-minutes |
| the post waived; the package counter not read (E206.md 6) | the owner's words of Sun 15 Nov 2026 10:22:36 PST; not read |

## Device commands sent

READs only: the session's opening and closing `ettelem config` and its one 10 Hz sampler, all through E206's guard (dmcmd_audit_v2 GO, every send site a READ), and k6's step 7 config read through E128's guard; each rgm136 host opened the ops node of card 0 only (the runtime's creation aborts the submission queues of the card it enumerates, as every lab host's does: harmless on a card held alone); `et-who` sends no device command. No set, no reset, no statistics reset, no firmware write, no PMIC write.

## Files

`session/` (the box's session directory `T<T0>-A`, copied back exact and scrubbed; among its files `session.log`, `queue.json`, `identity.json`, the box check's `kernel.txt`, `harness.txt` and `preflight.txt`, `config-start.*`, `config-end.*`, `stop-path.json`, `telemetry.jsonl.gz`, `smoke/`, `runs/`, `reads/`, `runner.out`, `runner.rc`, `MANIFEST.sha256`), `data-e206.json` (the frozen scorer's input), `reduce-e206.txt` (the reducer's table), `SHA256SUMS` (every file but this README). The scorer's outputs follow after the data commit (a later lane).

SPDX-License-Identifier: Apache-2.0
