# E184 arm B: card 1's SRAM rail on aifoundry1 card 1 - its average follows a 0.52 s filter on the rise and the fall (E184-T PASS, 0.515 s [0.472, 0.558] and 0.520 s [0.489, 0.551]); its reset windows show the two-phase signature at every level, with the rail carrying about 1.41 times its reading (f 0.708 [0.707, 0.710]), but the ratios moved across loads by 0.081, past the registered 0.06 (E184-M NOT RESOLVED, not SUPPORTED); 17.2 card-minutes, blind

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6** (E178's int8 pair read +0.053 W against M10's +0.186 W: how well can power be read). It answers the owner's question of Fri 6 Nov
2026, about 14:05 PST ("Are there more accurate ways of checking power draw? ... Also, allow the possibility that maybe there's something
wrong with the sensors"), as registered in [`tools/claims-v3/e184/E184.md`](../../../../tools/claims-v3/e184/E184.md) with its dated amendments
[A1](../../../../tools/claims-v3/e184/E184.md.dated-note-A1.md), [A2](../../../../tools/claims-v3/e184/E184.md.dated-note-A2.md),
[A3](../../../../tools/claims-v3/e184/E184.md.dated-note-A3.md) and [A4](../../../../tools/claims-v3/e184/E184.md.dated-note-A4.md), and kitted by
[`KIT.md`](../../../../tools/claims-v3/e184/KIT.md) with its dated notes [1](../../../../tools/claims-v3/e184/KIT.md.dated-note-1.md),
[2](../../../../tools/claims-v3/e184/KIT.md.dated-note-2.md) and [3](../../../../tools/claims-v3/e184/KIT.md.dated-note-3.md) (whose section 3
table governed every step). Sun 8 Nov 2026 (week 45), the card day Q156, on the owner's go of Sat 7 Nov about 21:30 PST, aifoundry1 **card 1
only** (`V3_DEVICE=1`, `ET_DEVICES=1`, lock `etsoc-shire1`, 600 MHz), during E182's session on aifoundry3. **Blind:** every forecast and rule
below was committed before the session's opening config read on the card. **This directory holds arm B only.** Arm S, the staircase on
aifoundry3 card 0, runs later the same day by its own lane, after E182's copy-back; that lane adds its files beside these.*

- **Card:** aifoundry1 card 1 (the device layer's PCIe target `/dev/et1_mgmt`, physical device 1), **600 MHz in all 9,418 samples**; `ettelem
  config` through E184's guard at the session's start (00:15:19 PST) and end (00:32:29): TDP 65 W, threshold 65 °C, managed_power, 600 MHz,
  499 mV both times, and the same at box step 7 (00:14:33) and its re-run after the session, step 10b (00:32:48). **Nothing was set.** Card 0
  was never opened, locked or read.
- **Card session** 00:15:19-00:32:29 PST, **17.2 card-minutes** (T0 + 1,030 s), inside the cap of 25 (1,500 s): the stop-path test 18432,
  the smoke 18431 and its gate (passed at 00:15:54), then **all five passes as registered**: 18440 (B1 plain, 282 s), 18441 (B1 with the
  statistics reset every second, 282 s), 18442 (B2, the step response, 82 s), 18443 and 18444 (B3, the cross-card set, 149 s each). Every
  pass read **ok** with every loaded item launched (9 of 9, 9 of 9, 6 of 6, 16 of 16, 16 of 16); **none set aside**
  (`reduced-e184b-v4.json` > `set_aside_passes` {}).
- **The session gate holds, with no departure:** both session config reads are the session's own and complete, as registered
  (`reduced-e184b-v4.json` > `session`: `config_status` complete / complete, `config_from` "the session's own read" at both edges,
  `departures` []). A4's replacement of a failed read was not needed.
- **The statistics reset ran in pass 18441 alone:** `since_reset_ms` is 0 or more in all 2,670 of its samples and −1 in all 6,748 others.
- **No stop fired**: the highest live readings were **45.69 W board** (pass 18441) and **65 °C** on any `temp_c.minshire` field (the stops 66
  W / 72 °C; the registration's expected peak about 46.5 W). The stop-path test fired both stops on live samples with no launch.
- **Every device-management command sent was a read but the ruled statistics reset** (§ Device commands sent).

## The answer (the registered rules, blind)

Every figure is `scored-e184-v3.json` > `arm_B` (the scorer v3 on `reduced-e184b-v4.json`, the reducer v4 with A4).

| rule | registered forecast | reading | verdict |
|---|---|---|---|
| **E184-T**, the SRAM rail's step response on the rise (B2, A1's reader; six bursts) | 0.54 s (E58), PASS if the 95% t interval lies in 0.44-0.64 s | **0.515 s [0.472, 0.558]**, n 6 | **PASS** |
| **E184-T**, the same on the fall | 0.54 s, band 0.44-0.64 s | **0.520 s [0.489, 0.551]**, n 6 | **PASS** |
| **E184-M** (H-MIX), the SRAM statistic in 1 s reset windows (pass 18441, ten levels, 32-67 steady samples each) | min/avg **0.628** and max/avg **1.589** at every level, f **0.698**; SUPPORTED if every level's min/avg lies in 0.55-0.71 and max/avg in 1.40-1.78, the min/avg medians span at most 0.06, and f's interval lies inside 0.65-0.75 | min/avg **0.592-0.673** (every level inside its band), max/avg **1.533-1.636** (inside), pooled f **0.708 [0.707, 0.710]** (inside); the min/avg medians **span 0.081**; pooled min/avg [0.648, 0.654] | **NOT RESOLVED** (the span is past 0.06; REFUTED needs a span over 0.10 or a pooled min/avg above 0.90) |

**What it reads as:** the SRAM rail's average on card 1 is a first-order filter of about 0.52 s, as E58 read it in September (0.525 s by
kind; 0.54 and 0.52 s on the rise and fall), so A1's reader holds on this card. Its reset windows carry the two-phase signature at every load
(the SRAM rail's minimum sits at 0.59-0.67 of its average and its maximum at 1.53-1.64, where card 1's minion and NoC rails read 0.97 / 1.03
and 0.95 / 1.05 in the same windows), and the pooled f puts the rail at about **1.41 times its reading** (`implied_rail_over_reading`
1.41205; the registration's forecast about 1.43). But the ratio is not constant across the loads at the registered tolerance: the idle level
reads min/avg 0.592 and the nine loaded levels 0.641-0.673. So H-MIX is not SUPPORTED, and neither is it REFUTED: the 1/f correction of card
1's SRAM figures stays a reading, not a law (E184.md section 7 holds it for a records round either way).

## Reported beside, never a verdict

| reading (registered, reported) | forecast | today | source |
|---|---|---|---|
| the control: card 1's minion and NoC rails in the same reset windows, min/avg and max/avg | minion 0.980 / 1.022; NoC 0.962 / 1.036 | minion **0.969 / 1.026**; NoC **0.955 / 1.047** | `arm_B` > `control` |
| **E184-R**, each rail's average restart after a reset, over its last value before it (median over pass 18441) | SRAM 0.77, band 0.72-0.82; the other rails within 2% | SRAM **0.800** (n 161); minion **1.0007** (n 165); NoC **1.0003** (n 164) | `reported` > `E184-R` |
| **E184-X**, B3's SRAM share of the board step over aifoundry3's September share, median over sixteen configurations and two passes | **0.718** (September 0.650-0.756 over these sixteen) | **0.640** (n 32) | `reported` > `E184-X` |
| **E184-G**, card 1's minion-average glitch rate over every arm-B pass but the reset pass (A1-3: the smoke 18431 and 18440, 18442-18444) | 0.087%, band 0.03-0.15% | **0 of 6,742** samples (below the band) | `reported` > `E184-G` |
| E184-T's control rails (A1-2: read the same way, never a verdict) | minion 1.08 s, band 0.90-1.35; NoC 1.08 s, band 0.90-1.25 | minion rise **1.407 s [1.398, 1.415]** (OUTSIDE), fall **1.338 s [1.279, 1.397]** (NOT RESOLVED); NoC **3.25 s** on both edges, the reader's grid edge (B2 moves the NoC rail by 0.20-0.25 W, a step A1-2 says no tau is read on) | `reported` > `E184-T_control_rails` |
| the plain pass's (18440) rail averages by level | | idle: minion 9.532, NoC 3.435, SRAM 2.237 W; `tstore/scp/random` on 32 shires: 11.852, 3.722, 8.102 W | `reported` > `plain_pass_avg_w` |

In pass 18441 the PMIC's first update after each reset makes the minion average equal its running maximum in 328 of 2,670 samples, as A1-3
says it would; that pass is outside E184-G's count, by A1-3.

## Post hoc (written after the data; deciding nothing)

From [`posthoc-armb-e184.json`](posthoc-armb-e184.json), made by [`posthoc_armb_e184.py`](posthoc_armb_e184.py) from this directory's reduced
and scored files and the registration's inputs and forecasts (the same bytes under `/usr/bin/python3` 3.9.6 and `python3` 3.13.11):

- **E184-M's span is the idle level's.** Without the idle level the nine loaded levels span **0.032** (0.641-0.673), inside 0.06; the idle
  level (board 31.94 W, SRAM average 1.811 W, 67 steady samples) reads 0.592. September's committed medians were idle 0.6268 (219 samples,
  board 38.1 W) and busy 0.6305 (61 samples, board 40.79 W). `> E184-M_by_level`.
- **E184-X's shortfall is card 1's own, since September.** Today's card-1 share over September's card-1 share has a median of **0.897**, and
  September's card-1 share over aifoundry3's is the forecast's **0.718**: their product is the registered statistic's 0.640. For the same
  sixteen configurations, today's board steps are a median **1.049** times September's on card 1 and its SRAM-rail steps **0.938** times.
  `> E184-X_split`.
- **E184-T, burst by burst:** the SRAM rail's tau 0.46-0.58 s on the rise and 0.49-0.57 s on the fall, its step 5.72-5.99 W; the minion
  rail's 1.40-1.42 s and 1.28-1.42 s on a 2.17-2.26 W step; the NoC rail's step 0.20-0.25 W. `> E184-T_bursts`.

## The readings, labelled

- **Blind, registered:** E184-T's and E184-M's verdicts and figures; each forecast was committed before the session's opening config read
  (00:15:19 PST).
- **Reported, registered before the data:** the control, E184-R, E184-X, E184-G, the control rails' tau and the plain pass's averages
  (E184.md section 5.3, A1-2, A1-3).
- **Post hoc:** the three readings of § Post hoc, and the card-minute and peak figures read from the session's own files.

## Registered before any data, and what the box ran

Every E184 text below was committed before the session's opening config read on the card, one ancestry chain in the lab repository (Sat 7
Nov 2026, PST): the registration `c6417611` (11:27:45), the kit with A1 `65f844be` (12:23:35), A2 `a887fc74` (14:04:38, alone), kit note 1
with kit v2 `eab0c70e` (14:11:30), A3 `3b48cf7b` (18:10:08, alone), kit note 2 `571511d0` (18:30:34), A4 `a5f8ec1a` (21:11:38, alone) and kit
note 3 `f9dcddac` (21:13:30). The readiness critics of Q154 and Q155 read E184 READY WITH GAPS (arm B's gaps: its host's first compile on
the box, and aifoundry1 not rebooted since E82's firmware read, which only the look can show). `git log --all` showed no
`docs/reports/data/*e184*` before this commit.

The owner's go came at about 21:30 PST on Sat 7 Nov with the lab boxes' fresh network approvals; the window, recorded by arm B's step 1 at
00:01:55: no session starts after 05:30 PST and every run ends by 07:45 PST (Sun 8 Nov). Arm B ran by kit note 3's section 3 table, each
step with arm B's own runbook output directory and the day's one lock file; every remote call came after a 15 s probe and ran under its
bound. Arm B's runbook log holds 51 calls from step 2 to step 11 (steps 1 and 2 and the first probe run by the card day's claim at
00:01:55-00:02:57, the rest by arm B's lane), all rc 0; the longest, a session wait, ran 525.8 s of its 600 s; no login link appeared:

| box step | when (PST) | what it read |
|---|---|---|
| 1, `rb/s02_window_e184.sh 2026-11-08 05:30 07:45` | 00:01:55 | the window (above) |
| 2, `rb/s03_desk_e184_v3.sh` | 00:02:14-00:02:27 | pulled (`45e514e3` = origin/main); HEAD descends from `65f844be`; E184's paths clean; the eight lists 11/44/6/45/3/20/1/18 OK; harness v2 rebuilt; the plan and the 467 images re-made; HARNESS OK 59; no E184 data in any ref |
| 4, `q141k-runbook/k6/s05_look_k6.sh aifoundry1` | 00:11:56-00:11:58, and again 00:15:12-00:15:13, right before the launch | E172's look first: **identity ok**, the host booted 2026-10-26 15:02:04, before E82's firmware read of 2026-10-31 13:45:24 PDT (no firmware query sent); then the holder rule: **FREE**, et-who's "No process holds an ET-SoC-1 device node or card lock" (0 holder lines, card 1's 0), no device process of ours or of another account; 9 terminals logged in (an idle login does not block) |
| 3, the post | 00:13:32-00:13:52 | arm B's clause added to the day's one post (§ Card and post) |
| 5, `rb/s07_sync_e184.sh B` | 00:13:57-00:13:59 | every file of `harness-e184-v2.json`, 59 files in 7 paths, after `check_e184_v2.py harness` read them at the harness's sha256 |
| 6, `rb/s08_build_e184.sh B start`, `wait` | 00:14:04-00:14:07; 00:14:13 | the job 00:14:05-00:14:09, rc 0: `build_e184.sh` **BUILD OK** (the patched host's first compile against the real runtime on a box), HARNESS OK 61 with the binaries, `preflight_e184_v2.sh B` GO (34 send sites, 0 disallowed, the allow-list STATS_RESET alone) |
| 7, `rb/s09_reads_e184_v2.sh B` | 00:14:33-00:14:34 | `et-lab-manifest` kept on the box; the config through E184's guard under card 1's lock: 65 W / 65 °C / managed_power / 600 MHz / 499 mV, kept on the box as step 7's read; et-who clean |
| 8, `rb/s10_dry_e184.sh B start`, `wait` | 00:14:39-00:14:42; 00:14:48-00:14:49 | the dry job 00:14:40-00:14:41, rc 0: pass 18442's six items, the smoke's three and the stop-path test as V3_DRY, and the start gate refusing with 8 ([`raw/aifoundry1-c1/logs/session-B-dry-t1794125681.log`](raw/aifoundry1-c1/logs/session-B-dry-t1794125681.log)) |
| 9, `rb/s11_session_e184.sh B` | 00:15:18-00:15:24 | the window's gates; k6's guard (no dry pass or session of ours running; the identity again: ok); both jobs ended rc 0 today; launched detached with T0 1794125719 (00:15:19) |
| 10, `rb/s20_wait_e184.sh B` | 00:15:30-00:32:33, two bounded calls | the first said "call again" (00:24:16), the second read this T0's session end |
| 10b, `rb/s09_reads_e184_v2.sh B after` | 00:32:47-00:32:48 | after this T0's end line: the config as at the start, kept on the box as step 7's read; et-who clean |
| 11, the release, then `rb/s22_collect_e184_v3.sh B` | 00:32:54-00:33:16; 00:33:33-00:33:51 | the post's release; then the two copies back, `collect_e184_v3.sh` at nice 10 (`reduce_e184_v4.py`, `score_e184_v3.py`) and the gates (below) |

The session ([`raw/aifoundry1-c1/logs/session-B-t1794125719.log`](raw/aifoundry1-c1/logs/session-B-t1794125719.log),
[`raw/aifoundry1-c1/logs/queue-B-t1794125719.out`](raw/aifoundry1-c1/logs/queue-B-t1794125719.out)): T0 and the harness check with the
binaries (HARNESS OK 61) and the device-command preflight (GO) at 00:15:19; et-who, then the opening config read; the stop-path test 18432
00:15:19-00:15:23; the smoke 18431 00:15:23-00:15:54 (three bursts, 275 busy samples at 600 MHz) and its gate; the queue's five passes
00:15:54-00:32:19, each admitted by the budget rule (budget 1,500 s from T0, 60 s reserve); the queue done at T0 + 1,030 s; the closing
config read, et-who and the session end at 00:32:29. The die read 54-59 °C at the blocks' edges. The host binary in every pass is the day's
one build, `cf6dae89…` (each pass's `code.sha256`).

## Who checked it

Step 11 v3 ran its gates in order, each passing: the two copies back (the passes, smoke and stop-path test; the box's `build/e184/` without
the operand images); the stop-path test checked to have recorded no launch; the copy checked to hold this T0's session log;
`collect_e184_v3.sh` ("scored-e184-v3.md written ... (reduce_e184_v4.py, A4)"); the desk-path gate (`nopath: 78 files read ... 0 hit(s):
CLEAN`); and last the login check over every directory (`scrub_tree_e178.py --check`: `OK (59 files in 11 directories read, 0 left)`). This
directory equals that collection file for file, plus this README, [`SHA256SUMS-arm-b`](SHA256SUMS-arm-b) and the post hoc pair. No data
verifier has read it yet: the card day's verifier and fix pass for E184 follow its data commit.

## Device commands sent

As registered (E184.md section 4; kit v2's arm-B block): every telemetry call through E184's guard (`ettelem config` with no argument,
`ettelem sample --seconds --every-ms`, and `--reset-ms 1000` in pass 18441 alone): `ettelem config` at box step 7, at the session's start and
end, and at step 10b; `ettelem sample` at 10 Hz in every block. Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS,
GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE,
**GET_MODULE_VOLTAGE**: **all READs**, the two in bold PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **The one
WRITE: SET_STATS_RUN_CONTROL, the statistics reset (type 1, control 2), once a second in pass 18441 only**, the owner's ruling of 31 October
2026. **Never sent**: any other SET_*, the firmware-revisions query (the identity came from the host's boot time), any residency read, any
governor, TDP, threshold or clock set, any reset, and `dev_mngt_service` (the block's drain is a refusal). The enercat host opens the card
through the runtime only (kernel load, copies, launches). The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any
device opened: **GO**, 34 send sites, 0 disallowed, the allow-list STATS_RESET alone
([`raw/aifoundry1-c1/logs/dmcmd-preflight-B-t1794125719.txt`](raw/aifoundry1-c1/logs/dmcmd-preflight-B-t1794125719.txt)); the same at step 6.
No power cycle, and nothing that risks one.

## Card and post

`et-who` at the looks (00:11:57 and 00:15:12 PST), at box step 7 (00:14:33), at the session's start and end, and at step 10b (00:32:48): no
process held a device node or card lock on either card, and no other account ran a device process. Every block's own check before its
runs let them all go, and no others-present line was written. 9 terminals were logged in; an idle login does not block, and no login is
named in any file. This was our only session on aifoundry1; card 0 was never used. Beside it, on aifoundry3, E182 ran by its own lane.

Sun 8 Nov's one `#community-lab` post is message `1568898719959744554`, created by the card day's claim at 00:03:23 PST. Each edit below ran
under the Discord lock with `EXPECT_TEXT` (the post's text as a fresh read gave it) and `EXPECT_CHANNEL=community-lab`: a dry run, then the
save, then a read back from a fresh plan (one post that day, its text equal to the intended one). Before arm B it read
`<ai> **Claude says:** using aifoundry3 for 2 h, until ~02:03 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
- **00:13:46 PST, after the look read card 1 FREE**, arm B's clause was added, every other word kept:
  `<ai> **Claude says:** using aifoundry3 for 2 h, until ~02:03 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry1 card 1 for 1 h, until ~01:13 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
- **00:33:11 PST, at arm B's release** (after step 10b), its clause was dropped, every other word kept, since aifoundry3 was still held:
  `<ai> **Claude says:** using aifoundry3 for 2 h, until ~02:03 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.

No other post was made, and no earlier day's post was touched.

## Privacy and the public-text scan (before the commit)

- **Logins.** Step 11 v3's last gate read every directory of the collection with `scrub_tree_e178.py --check` (0 left). Before this commit
  the final bytes were read again, this README and `SHA256SUMS-arm-b` among them: `scrub_tree_e178.py --check` over this directory (63 files
  in 11 directories, 0 left); E164's `scrub_etwho_e164.py --check` (unchanged; `--owner` the box login of this repository's owner) in every
  directory of this one and of a scratch copy of the text inside its 19 `.gz` files (29 directories, every one rc 0); and a search of both
  for lib.sh's and D1's "others present" line and run_e78's "another user on this card" stop line: 0 lines in the data's files (the first
  search over the final bytes found 2, both this README's own sentence naming the two patterns, so the search leaves the README out). The
  session log's et-who readings say "No process holds an ET-SoC-1 device node or card lock".
- **The public-text scan** (`tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home, scratch and e-mail
  patterns) over every text file and the text inside every `.gz` of this directory: 63 text files and 19 `.gz` files, 7 matches, every one
  the owner's own box home path, the reviewed class E166's, E171's, E176's, E178's, E180's and E181's committed data carry; no other match.
  The runbook's desk-path gate (`nopath_q142s.py`) read the collection and then this whole directory (82 files), 0 hits. This README,
  `SHA256SUMS-arm-b` and the commit's message were
  also scanned on their own (0 matches). The lab's private name table is absent on the Intel, so names were checked against the fixed list
  only (a stated coverage limit).

## Files

All files of step 11 v3's collection and score of arm B are here as step 11 left them (`diff -r` against `build/e184-out/`: equal), plus
this README, [`SHA256SUMS-arm-b`](SHA256SUMS-arm-b) (it pins every file but the READMEs and the lists themselves) and the post hoc pair.

| file | what |
|---|---|
| `scored-e184-v3.json`, `scored-e184-v3.md` | the scorer v3's output as arm B's collection wrote it: arm B's rules and reported readings, the session gate; arm S "NOT SCORED (no reduced file)" until its own collection |
| `reduced-e184b-v4.json` | the reduction (v2's, unchanged) with A3-3's gate and A4: every pass's levels, fits and shares, the reset windows, the restarts, the glitch census, the session gate with its config reads and step 7's reads |
| `t0-B.txt` | arm B's T0, kept so that a later collection of arm S re-reduces arm B with its own T0 (kit note 2 section 2) |
| `raw/aifoundry1-c1/e184/p18440`-`p18444` | the passes as the box wrote them (`telemetry.jsonl.gz`, `runs.jsonl.gz`, `marks.jsonl.gz`, `run.log`, `runner.out`, `configs.json`, `check.json`, `block.json`, `code.sha256`) |
| `raw/aifoundry1-c1/e184-smoke/p18431`, `raw/aifoundry1-c1/e184-stoptest/p18432` | the smoke and the stop-path test (its board and die `stoptest.json` and outputs) |
| `raw/aifoundry1-c1/logs/` | the session's own files, named by T0: `session-B-t1794125719.log`, `queue-B-t1794125719.out`, `session-B-t1794125719.out`, the two session config reads with their times and the device layer's stderr, `dmcmd-preflight-B-t1794125719.txt`; the two step-7 reads (`config-B-step7-1794125673.json` before, `-1794126768.json` after); step 8's dry start gate `session-B-dry-t1794125681.log` |
| `posthoc_armb_e184.py`, `posthoc-armb-e184.json` | § Post hoc's reader and its output |

**When arm S is collected** (its own lane, later today), `collect_e184_v3.sh` reduces arm B again with this T0 from the same raw tree and
scores both arms together into `build/e184-out/`; arm B's scores there read the same (the reducer and the scorer are deterministic, the
bootstrap seeded: re-run here on this directory's raw tree, both gave these files byte for byte). This directory's files are arm B's, as
committed; arm S's lane adds its own files and list beside them.

## What it does to predicting power

E184 asks whether the sensors read power right; arm B asks it of card 1's SRAM rail, the one rail whose reset windows looked two-phase in
September. It fills no cell of the kinds table (it reads no kind's price); it sets how card 1's SRAM figures may be read:
- **The rail's time constant holds** (E184-T PASS: 0.515 / 0.520 s against E58's 0.525-0.54 s), so a card-1 SRAM rail reading can be
  deconvolved with E58's filter model as A1 does; that part of reading card 1's power is confirmed blind.
- **The SRAM reading is not yet a fixed fraction of what the rail carries** (E184-M NOT RESOLVED): the two-phase signature is there at every
  load, and pooled it says the rail carries about 1.41 times its reading (f 0.708), close to the forecast 1.43; but the ratio moved with the
  load (idle 0.592 against 0.641-0.673 loaded, a span of 0.081 against the registered 0.06). So a single 1.4x correction of card 1's SRAM rows
  is not established; any re-derivation waits for a records round and should treat the factor as load-dependent until a rule says otherwise.
- **Cross-card (reported):** card 1's SRAM share of B3's steps over aifoundry3's September share reads 0.640 against the forecast 0.718;
  post hoc, the shortfall is card 1's own since September (its SRAM steps 0.94 and its board steps 1.05 times September's): card 1's SRAM
  share of these steps is about 0.90 of its September share, so September's card-1 rows overstate it by about 11% today.

SPDX-License-Identifier: Apache-2.0
