# E188, 2026-11-15, aifoundry3 card 0 at 600 MHz as found: RAN FULL - the stop-path test, the smoke, both kinds passes and all seven fp32 A B B A trains in 85.18 card-minutes, reads only, no stop; A's 23 held bits cost what M12 and E186 price a held A bit (E188-GA23 +0.00403 W a bit, SIZE M12 PASS, REPEAT AGREES), but one held B bit costs more than M12's price and E186's (E188-GB1 +0.01699 W, SIZE M12 FAIL LOW, REPEAT DIFFERS HIGH), FLAT across the five places tried; adjacent against spaced held bits does not resolve (E188-PAIR -0.0002 W, BOTH); E188-M NEITHER

*Sun 15 Nov 2026 (week 46), PST, the round's card lane `card-e188` (Q186), orchestrated from aifoundry2. Registered in `878b6f63`
([`E188.md`](../../../../tools/claims-v3/e188/E188.md), Thu 12 Nov 2026) with its dated amendment A1 and note 1 (`6e6d23dc`) and amendment A2
(`f9632ee3`); kitted in `726a6b64` ([`KIT.md`](../../../../tools/claims-v3/e188/KIT.md),
[`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e188/CARD-LANE-BRIEF.md)) with its dated notes 1 (`16b41cf2`) and 2 (`e4c45385`, the
Linux port, landed Sun 15 Nov 13:08:20 PST); verified and readiness-checked (READY WITH GAPS). T5's set: seven fp32 trains (B05, PAIR, B19,
AALL, B10, B22, B04, in that registered order) and two same-session kinds passes. **Blind:** every forecast, line, rule and threshold below
was committed on Thu 12 Nov 2026, before any E188 datum and before this session's first card command (15:14:13 PST, step 7's config read);
M12 (as frozen, `8b85b498`) and M10 (frozen, `6829c9ba`) are the blind arms. Nothing was set on the card.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every line, threshold and rule is
**registered** (E188.md with its amendments, the kit). The rules' words below are the **kit's scorer's** (`score_e188.py`, unchanged since
`726a6b64`), run by step 11 v2 at the desk on this directory before the commit and printed in [`results-e188.md`](results-e188.md). The
block spans, sample counts, the clock count and the peaks are **desk arithmetic of the measured records** (each block's
`telemetry.jsonl.gz` and `marks.jsonl`, and `logs/queue.out`), not prices and not rules. The desk steps ran under `/usr/bin/python3` 3.12.3
on aifoundry2.

## Departures and notes (dated Sun 15 Nov 2026, PST; each set before the session, written here after the collection)

1. **G1, the go: E188 NAMED.** The owner's words at **15:05:27 PST Sun 15 Nov 2026**, verbatim: "yes, feel free to run it, feel free to
   read firmware as well". They answer the orchestrator's message, which asked two things, the second verbatim: "E188 (aifoundry3, about 82-93
   card-minutes): run it? ... I'd hold it unless you specifically want it." The orchestrator's reading, recorded before the session: "yes,
   feel free to run it" answers "E188 ... run it?", so E188 is named, FULL on aifoundry3 card 0 as registered
   (E188.md: "Card time needs the owner's go with a day and a window in PST"; the kit's note 2: "E188 runs only on the owner's go naming
   it"). His second clause concerns a firmware read on another card for another run; E188 sends no firmware query (E188.md section 6).
2. **G2, the day and one window.** His words give no window. The readiness check's form (a), a dated departure: G = the moment this lane
   held the aifoundry3 booking, **15:10:41 PST**; last start G+1:30 and last end G+3:30, each rounded up to the whole minute: **16:41 and
   18:41 PST** on Sun 15 Nov 2026 (step 1: `s02_window_e188.sh 2026-11-15 16:41 18:41`, written 15:12:56). The session launched at 15:15:19
   (T0 15:15:14) and ended at 16:40:25; step 11 started at 16:40:45, more than 10 minutes before the last end.
3. **G3, access: a fresh network-access approval for aifoundry3, nothing to name.** The session was orchestrated from aifoundry2, a lab box
   that reaches aifoundry3 without that check (E188.md asks "a fresh ... approval for aifoundry3"). The kit's login-link stop stayed live (an
   exit 11 with its lock line ends the day's box steps); no step met a login link (the round's lock file held the same lines before and
   after the day's steps).
4. **G4, the order and the rests.** E183 was not running that day (E188.md's "after E183" does not arise). On aifoundry3 our last session
   before E188 was E193's sitting B, which ended at 12:16:41 PST (its data `96ef447c`), so E188's 40-minute rest had been open since
   **12:56:41**. Step 7's config read, the day's first card command, ran at 15:14:13, after the rest had opened (E192's data note 1's
   lesson). Step 9 read the rest on the box at the launch, verbatim: "rest: 178 minutes since E193's session end (2026-11-15 12:16:41 PST;
   dry sessions and blocks that opened no device skipped)". After this session no session of ours on aifoundry3 before 17:20:25 PST.
5. **G5, the post: the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST**, verbatim: "don't worry about discord post, just
   use the machines, nobody is using them" (standing until he says otherwise). No claim (step 3) and no release (step 11's first part);
   E188.md section 6's "using aifoundry3 for 2 h, until ~HH:MM PST" was not posted. Every other etiquette check stood: k6's look (et-who,
   who, uptime, the holder rule: FREE at 15:13:48), step 7's reads (et-who clean at 15:14:13), the session's holder check before its first
   card command and again at its close ("No process holds an ET-SoC-1 device node or card lock."), and the kit's card lock and
   per-process timeout, unchanged.
6. **G6, the host's package counter: not read** (no E188 file reads it).
7. **The desk.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, by the kit's note 2 (the Linux port); the
   kit's desk was the Intel under 3.9.6, so the collector's and scorer's printed figures may differ from a 3.9 run's in their last digits.
   The orchestrating session is the round's session on its yvb3 Claude account. The brief's load guard was read as `uptime` on aifoundry2:
   the 1-minute load 0.78 at step 0 and 0.91 at step 2 (at most 8).
8. **The lab's top, read three times, each "TOP OK"** (step T at 15:12:56, step 2 at 15:13:04, step 11 within 16:40:45-16:45:18), each
   verbatim: "TOP OK: the lab's top: 18 entries, 0 module files or packages; tools/claims-v3/e183/rb/: 47 entries, 1 module files or packages
   (nopath_spell_e183.py); none named as a module the system python finds; no byte-code a module's name imports, no .pth file (the names
   /usr/bin/python3 3.12.3 finds: its built-in modules and 5 folders outside the lab clone)".
9. **The pre-launch read** (the readiness check's `prelaunch_e188.sh`, read only, at 15:15:03), verbatim: "USER-READ: set by the login
   yes; equal to the login's own name yes", "STOP-READ: no stale stop (build/e188/STOP and build/claims-v3/STOP absent)", "PRELAUNCH-E188
   OK".
10. **The day's booking, the quiet hold and the one-lab rule.** One booking of aifoundry3, owner `card-e188`, from 15:10:41 PST to this
   commit; the round's quiet hold named `card-e188` from 15:12:52 (step H, the lab clone's status 0 lines) to this commit; the one-lab rule
   kept this lane's desk span (steps 0, H, T, 1 and 2: 15:12:42-15:13:15) and its span from the collection to this commit's push (from
   16:40:37) apart from any other lane's: it waited for neither.

## Results

### The rules' words (the kit's scorer, `score_e188.py`; registered rules, blind), as printed in `results-e188.md`

plan read: FULL; the session's float scale s: 1.013768875192206 (read); kept kinds passes [18820, 18821]

| rule | verdict | reading |
|---|---|---|
| E188-C | PASS | kinds not all PASS [], trains [] |
| E188-SCHED | PASS | 7448 of 7448 launch records paired; not paired [] |
| E188-B05 | NEITHER | +0.0204 [+0.0159, +0.0249] W; SIGN POSITIVE; SIZE M12 FAIL LOW (line +0.0133), M10 FAIL LOW (line -0.0000) |
| E188-PAIR | BOTH | -0.0002 [-0.0058, +0.0054] W; SIGN NOT RESOLVED; SIZE M12 PASS (line +0.0013), M10 PASS (line +0.0013) |
| E188-B19 | NEITHER | +0.0181 [+0.0133, +0.0228] W; SIGN POSITIVE; SIZE M12 FAIL LOW (line +0.0120), M10 FAIL LOW (line -0.0013) |
| E188-AALL | M12 | +0.1684 [+0.1638, +0.1731] W; SIGN POSITIVE; SIZE M12 PASS (line +0.1454), M10 FAIL LOW (line +0.0758) |
| E188-B10 | M12 | +0.0144 [+0.0095, +0.0193] W; SIGN POSITIVE; SIZE M12 PASS (line +0.0132), M10 FAIL LOW (line -0.0001) |
| E188-B22 | M12 | +0.0324 [+0.0282, +0.0367] W; SIGN POSITIVE; SIZE M12 PASS (line +0.0284), M10 FAIL LOW (line +0.0151) |
| E188-B04 | M12 | +0.0151 [+0.0092, +0.0210] W; SIGN POSITIVE; SIZE M12 PASS (line +0.0150), M10 FAIL LOW (line +0.0018) |
| E188-GB1 | POSITIVE | +0.01699 [+0.01485, +0.01913] W a held B bit over ['B04', 'B05', 'B10', 'B19', 'B22']; SIZE M12 FAIL LOW; REPEAT DIFFERS HIGH |
| E188-BPOS | FLAT | Q 5.87 against 9.49 at 4 df |
| E188-GA23 | POSITIVE | +0.00403 [+0.00383, +0.00423] W a held A bit (AALL / 23); SIZE M12 PASS; REPEAT AGREES |
| E188-M | NEITHER | M12 Q 19.81 (INCONSISTENT), M10 Q 1915.69 (INCONSISTENT) over 7 trains |
| E188-TR-N | AS FORECAST | ratio 0.989 |
| E188-LV | NOT SCORED | FULL: the trains are the reading (E188-LV is the fallback's rule) |

- **The registered words** (E188.md sections 5.1 and 5.2): SIZE FAIL LOW = the model's line is below the measured band (it prices less than
  the card reads); FAIL HIGH = above. A train's interval is t(0.975, n - 1) over its units: 38 in every train here (df 37). E188-GB1's REPEAT compares with E186-GB's measured
  interval [+0.01345, +0.01429] and E188-GA23's with E186-GA's [+0.00373, +0.00469] (E188.md section 5.3); M12's gamma_B is +0.01328 and its
  gamma_A +0.00303 W a held bit (se 0.00086 each). E188-M's 95% point is 14.07 at seven trains; E188-BPOS's 9.49 at four degrees of freedom.
- **E188-C: PASS. E188-SCHED: PASS** (E188.md note 1 section 3: each is PASS or "not PASS"; both read PASS, so no train reads NOT SCORED).
- **What the words say, in E188.md section 5.4's own terms.** One held B mantissa bit costs about +0.017 W, at every place tried (bits 4, 5,
  10, 19 and 22 read FLAT), which is more than M12's one price a side (FAIL LOW) and more than E186 read for a held B bit among sixteen
  (REPEAT DIFFERS HIGH): one bit alone costs more than a bit among others. Three of the five one-bit trains (B10, B22, B04) sit inside M12's
  bands, two (B05, B19) above them. A's 23 held bits cost +0.00403 W a bit, the price E186 read over 16 (REPEAT AGREES) and inside M12's band.
  Two held B bits adjacent against spaced: no difference resolved (PAIR's interval holds 0, and both models' line, +0.0013 W, lies inside
  its band). Jointly neither model is
  consistent over the seven trains (M12 Q 19.81 against 14.07; M10 Q 1,915.69). The train noise read as forecast (TR-N ratio 0.989).

### The session (measured)

| what | value | label |
|---|---|---|
| card-minutes, T0 (the session's first config read) to "session end" | **85.18** (15:15:14 to 16:40:25 PST, 5,111 s; the queue done at T0 + 5,111 s; cap 100 = 6,000 s, 60 s kept for the closing read) | measured (the session's clock) |
| the plan and the queue | **FULL as registered**: the stop-path test 18802, the smoke 18801 (both gates PASS at 15:16:33), then 9 queue items in the registered order: the kinds pass 18820, the trains 18810 B05, 18811 PAIR, 18812 B19, 18813 AALL, 18814 B10, 18815 B22, 18816 B04, and the kinds pass 18821, admitted by the budget rule (projected 410 s; started at T0 + 4,724 s, ended at T0 + 5,101 s against the budget's last end T0 + 5,940 s) | measured (`logs/queue.out`) |
| train processes, by exit status | **76 a train, every one exit 0** (532 in all); 14 launch records a process: **1,064 a train, 7,448 in all, 7,448 paired** | measured |
| the check of C | **8,744 of 8,744 launches PASS** (ROUNDING 0, UNMODELLED 0, FAIL 0); 10 of 10 listed sessions carry a C log checked to its end (FINISHED); the stop-path test carries none | measured (`ccheck/`) |
| telemetry samples, and those not at 600 MHz | **49,881 / 0** (`mhz.minion` 600 in every sample, and `sp.minion_mhz[0]` the same; `since_reset_ms` -1 in every sample: no statistics reset) | measured |
| board power, peak and lowest | **54.31 W** (15:33:01 PST, train 18810's closing fp32.randn anchor run); lowest 22.65 W (15:15:18, the stop-path test) | measured (desk arithmetic) |
| die, `temp_c.minshire[0]`, peak and lowest | **63 C** (first at 15:33:01, the same run; 63 C in every train block); lowest 49 C | measured (desk arithmetic) |
| live stops (board at or above 65 W, `minshire[0]` at or above 70 C) | **none fired**; the stop-path test 18802 fired its die, board and watcher stops on live samples with no launch (rc 6 each; the test rc 0) | measured |
| the config at both ends | TDP 0 W, threshold 65 C, power state max_power, minion 600 MHz, 523 mV at the start (15:15:14) and **the same at the close** (16:40:25); also at step 7 (15:14:13) and the smoke's two ends | measured (READ) |
| runs set aside | **one**: in the kinds pass 18821, run 22 (`fp32.pi`, segment 1) was skipped by E78's approach rule, verbatim "launch reading not reached (hot 59.0 C, now 59.0 C after 0 heats, 1.9 s, quiet 1.91 s): skipped"; no stop, nothing retried; the kinds reduction kept 87 of 87 runs over the two passes | measured |

| block | span (PST, from `logs/queue.out`) | block time | processes or runs | samples | board peak | die peak |
|---|---|---:|---|---:|---:|---:|
| 18802 stop-path test | 15:15:14-15:15:28 | | no launch; three stops fired | 114 | 23.48 W | 49 C |
| 18801 smoke | 15:15:28-15:16:33 | | 13 kinds items (6 launches each), then B05's two processes (SFFS, FSSF) | 625 | 50.08 W | 54 C |
| 18820 kinds pass | 15:16:33-15:23:23 | 410 s | 44 runs and 2 burn-ins | 4,069 | 53.74 W | 62 C |
| 18810 B05 | 15:23:33-15:33:27 | 594 s | 76 | 5,908 | 54.31 W | 63 C |
| 18811 PAIR | 15:33:37-15:43:27 | 590 s | 76 | 5,868 | 54.04 W | 63 C |
| 18812 B19 | 15:43:37-15:53:33 | 596 s | 76 | 5,928 | 54.01 W | 63 C |
| 18813 AALL | 15:53:43-16:03:34 | 591 s | 76 | 5,887 | 54.09 W | 63 C |
| 18814 B10 | 16:03:44-16:13:40 | 596 s | 76 | 5,922 | 54.11 W | 63 C |
| 18815 B22 | 16:13:50-16:23:42 | 592 s | 76 | 5,889 | 54.14 W | 63 C |
| 18816 B04 | 16:23:52-16:33:48 | 596 s | 76 | 5,935 | 54.14 W | 63 C |
| 18821 kinds pass | 16:33:58-16:40:15 | 377 s | 43 runs (one skipped) and 2 burn-ins | 3,736 | 53.90 W | 62 C |

- **The smoke and its two gates** (the session log, verbatim): "telemetry: 625 samples, board 22.83-50.08 W, shire mean 49-54 C,
  since_reset_ms [-1]"; "C log: 15 host records, 106 C records, 78 launch records, 0 unpaired, 0 flagged"; "launch gaps with the C log:
  median 3.0 ms, max 3 ms over 52 gaps (registered: median <= 10 ms)"; "SMOKE-GATE (kinds) PASS {'bad': []}"; "train: 2 processes, 28
  launch records, median cycles per op 546.001, median gap 3.0 ms, 0 launches without their C record"; "SMOKE-GATE (train) PASS {'bad':
  []}"; "smoke gate passed: queue starts (plan FULL)" (15:16:33). Each of the twelve file tiles' dumps equals its sha256 (the built-in tie,
  `anchor_pi`, has none to compare); the clock read 0.5994-0.5997 GHz by the launches' own cycle counts.
- **The trains** opened and closed with E78's fp32.zeros and fp32.randn runs, launched at the band (58 C after 59 C); the session's float
  scale s = 1.01377 was read from the trains' fp32.randn anchors (`e188-anchors.json`).

### Reported beside, never a verdict (E188.md section 5.4)

- `scored-e188.json` > `reported`: each train's two halves, orientations and carry-over (`trains-e188.json`); the kinds passes' contrasts
  (`reduce.txt`, `runs.csv`); BALL - AALL, the difference of the two kinds' mean contrasts over fp32.ones in the two kinds passes,
  **+0.2503 W**, beside E182's T5 interval [+0.2299, +0.2419]; E188-LV's arithmetic over the kinds pass's eight kinds, reported only (FULL).
- october-forecast-model's arms (`ofm-e188.json`) are reported arms only: their reader, `rb/check_arms_e188.py`, runs only after this
  commit, through its own gate, and its readings stay outside the repository (E188.md A1-1). Nothing of them is in this directory.

## Registered against happened

| item | registered (E188.md with A1, A2 and note 1; the kit) | happened |
|---|---|---|
| card and clock | aifoundry3 card 0 at 600 MHz pinned, TDP 0 W / 65 C / max_power / 600 MHz read at both ends; nothing set | the same, 523 mV, at both ends; 600 MHz in 49,881 of 49,881 samples; nothing set |
| plan | FULL; the fallback PASSES only after two failed builds or a failed smoke train gate | FULL; the train host built on the first attempt (3 s, TRAIN-HOST-BUILT); both smoke gates PASS |
| order | the stop-path test, the smoke, 18820, B05, PAIR, B19, AALL, B10, B22, B04, then 18821 if its projected end fits | exactly that, 18821 included |
| card-minutes | about 82.4 at E182's piece times, 91.3-92.8 at E186's measured block times; cap 100 | 85.18 |
| trains | 76 processes (38 units) of 13 launches after the calibration launch, each | 76 processes, 14 launch records each, every process exit 0, all 38 units |
| kinds passes | 44 runs and E171's two burn-ins each | 18820: 44 runs; 18821: 43 runs and one skipped by E78's approach rule; two burn-ins each |
| stops | board at or above 65 W, or `minshire[0]` at or above 70 C, on a live sample; a stop ends the queue | none fired; peaks 54.31 W and 63 C |
| C and pairing | E188-C and E188-SCHED over every launch | 8,744 of 8,744 PASS; 7,448 of 7,448 paired |
| rest | at least 40 minutes after our last session on aifoundry3 | 178 minutes (step 9's rest line) |
| window and post | his go's window; the day's one post | G2's window (16:41 / 18:41); the post waived (G5) |
| network approval | a fresh approval for aifoundry3 | nothing to name from aifoundry2 (G3) |
| desk | the Intel, Python 3.9.6 | aifoundry2, `/usr/bin/python3` 3.12.3 (the kit's note 2) |

## The day's steps (the card lane's record; the go lines' steps, each with its exit)

B booking 15:10:41 (0); D the one-lab desk span 15:12:42 (0); 0 the anchor read in the lab clone, "GO-ANCHORS-E188: 23 of 23 as stated"
at HEAD `e8a85229` = GitHub main, status 0 lines (15:12:46, 0); H the quiet hold, status 0 lines (15:12:52, 0); T "TOP OK" (15:12:56, 0); 1
the window (15:12:56, 0: "E188 plans that fit now: E188-FULL E188-PASSES"); 2 the desk check v3 (15:13:00-15:13:04, 0: HISTORY OK, TOP OK,
FORECAST-TOL-E188 PASS: 16 floats differ in their last digits, the largest at 0.0805 of the tolerance; "the readers' interpreter Python
3.12.3; commits naming E188 data: 0"); U (15:13:15, 0); 3 the post SKIPPED (G5); 4 the look, FREE (15:13:48, 0); 5 the sync (15:13:54, 0:
46 paths); 6 the build, attempt 1 (15:14:00-15:14:03, 0: TRAIN-HOST-BUILT, HARNESS OK 79, preflight GO); 7 the config read (15:14:13, 0:
TDP 0 W / 65 C / 600 MHz, 523 mV, et-who clean); 8 the dry pass (15:14:20-15:14:51, 0: JOB-DONE a3-dry-e188 rc=0); P the pre-launch read
(15:15:03, 0); 9 the launch, FULL yes (15:15:19, 0: T0 15:15:14); 10 ten bounded waits (nine "still runs", 17; the tenth 0 at 16:40:28:
RUN-ENDED, MANIFEST-WRITTEN 326 files); C the collect span (16:40:37, 0); 11 the release SKIPPED (G5), the collection
(16:40:45-16:45:18, 0: COPY-BACK EXACT 326 files, HISTORY OK, TOP OK, E188-SCHED PASS, nopath CLEAN, scrub-tree OK: 250 files in 38
directories read, 0 left); 12 this commit.

## Device commands sent

As registered (E188.md section 6, "Device commands"): E182's and E186's, unchanged, every telemetry call through E128's guard (`ettelem
config` and `ettelem sample --seconds --every-ms`), plus step 7's config read through the same guard. The train host opens the card through
the runtime only (kernel load, copies, launches). Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS,
GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE and
GET_MODULE_VOLTAGE: **all READs** (the two voltage reads are the PMIC voltage-register reads the owner's rule of 2 November 2026 allows).
**Never sent:** the statistics reset (`since_reset_ms` -1 in all 49,881 samples; its one send site, `lib.sh:154`, is E153's reviewed
exception, which E188 never passes), any SET, governor, TDP, threshold or clock set, any reset, a power cycle, the firmware-revisions query, a
residency read. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send sites, 0
disallowed ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)); the same at step 6. The board's highest live reading was 54.31 W.

## Privacy and the public-text scan (before the commit)

Step 11's gates passed on this directory: the desk-path gate ("nopath: 350 files read under 1 path(s); 0 missing; 0 hit(s): CLEAN"; its
spelling check the same) and the login scrub ("scrub-tree: OK (250 files in 38 directories read, 0 left)"). The paths the box wrote carry
the box account's home, which is the lab account named after the owner, as in E186's committed data. The round's public-text scans ran over
every file of this directory (the text inside each `.gz` included), this README and the commit message (three runs, 16:55-17:10 PST, the
README reworded between them and read again alone after its last edit; before the commit): `pubscan_all.py` (unchanged) read 267 text files and the text of 21 `.gz` files, 46,099 hits, every one the owner's own box path
(46,081) or a block configuration's top-folder key naming it (18), **0 outside them**, and 0 hits in the commit message; the round's class scan
(`tiers_scan.sh`, unchanged) found, in this README, two lines, each read and kept: the owner's quoted words of 10:22:36 PST and the reported
arms' model named by its files; in the commit message, none; in the collected text files, the box account's home in paths (as above) and
the device runtime's own printout of its memory-region base addresses in the two config reads' `.err` files (12 lines each, as in E186's
committed data), no other class. The login scrub's check, run again on the placed directory: "scrub-tree: OK (252 files in 38 directories
read, 0 left)".

## Files

| path | what |
|---|---|
| `results-e188.md`, `scored-e188.json`, `score.log` | the kit's scorer's words and its full output |
| `pairing-e188.status.txt` | the pairing check's line (E188-SCHED) |
| `trains-e188.json`, `reduce-trains.log` | the trains' reduction (E182's statistic through E186's) |
| `e188-anchors.json`, `reduce-anchors.txt`, `reduce-anchors.log`, `runs-anchors.csv` | the anchors' reduction and the session's float scale |
| `reduce.txt`, `reduce.log`, `runs.csv`, `e188.json` | the kinds passes' reduction (E178's, on E182's footing) |
| `ccheck/` | the check of C over every listed session |
| `code.sha256` | the desk's code at the collection |
| `aifoundry3/e188-stoptest/p18802/`, `aifoundry3/e188-smoke/p18801/`, `aifoundry3/e188/p188*/` | each block's own records: telemetry, marks, runs, the train records, C logs, configs, manifests |
| `logs/` | the session log, the queue's output, the box's manifest (`MANIFEST.sha256`, 326 files, read back exactly), the config reads at both ends, the preflight, the block list, the day's step-6 record (`logs/step6/`) |
| `SHA256SUMS` | every file of this directory but this README and itself |

SPDX-License-Identifier: Apache-2.0
