# E184 arm S: not run - the smoke's 16-shire n = 19 quad read +0.358 W, above +0.30 W, so its gate stopped the session before any pass (E184.md.dated-note-A3.md, A3-1); post hoc, that reading carries one refresh 3.11 W below its block, a partial dip the gate's reader keeps and A2-5's rule sets aside (with it the quad reads +0.185 W, 1.18 of its registered step); 0.75 card-minutes on aifoundry3 card 0

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6** (E178's int8 pair read +0.053 W against M10's +0.186 W: how well can power be read). Registered in
[`tools/claims-v3/e184/E184.md`](../../../../tools/claims-v3/e184/E184.md) with its dated amendments
[A1](../../../../tools/claims-v3/e184/E184.md.dated-note-A1.md), [A2](../../../../tools/claims-v3/e184/E184.md.dated-note-A2.md),
[A3](../../../../tools/claims-v3/e184/E184.md.dated-note-A3.md) and [A4](../../../../tools/claims-v3/e184/E184.md.dated-note-A4.md), and kitted by
[`KIT.md`](../../../../tools/claims-v3/e184/KIT.md) with its dated notes [1](../../../../tools/claims-v3/e184/KIT.md.dated-note-1.md),
[2](../../../../tools/claims-v3/e184/KIT.md.dated-note-2.md) and [3](../../../../tools/claims-v3/e184/KIT.md.dated-note-3.md) (whose section 3
table governed every step). Sun 8 Nov 2026 (week 45), the card day Q156, on the owner's go of Sat 7 Nov about 21:30 PST, aifoundry3 **card 0**
at 600 MHz pinned, after E182's session and its copy-back on the same card. This file sits beside arm B's [`README.md`](README.md), which stays
as committed; **everything named here is arm S's and new.***

- **Card:** aifoundry3 card 0 (`0000:02:00.0`, PCIe 16.0 GT/s x8), **600 MHz in all 286 busy samples** of the smoke. `ettelem config` through
  E128's guard read **TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV** at box step 7 (02:20:26 PST), at the session's start (02:21:39),
  and at step 10b after the session's end (02:24:54). **Nothing was set.**
- **Card session** 02:21:39-02:22:24 PST: **45 s, 0.75 card-minutes** (cap 135). T0 1794133299. The stop-path test 18402 (02:21:40-02:21:43:
  both stops fired before a run and in the watcher, no launch), the smoke 18401 (02:21:43-02:22:24: four quads, 72 launches, every quad
  readable), then **the smoke gate: NO-GO**, and the session took its end config read and ended. **No pass ran** (18410-18418 never started).
- **No stop fired**: the highest live readings were **44.11 W board** (the smoke's every-minion quad; the registration's expected peak about
  44.5 W) and **56 °C** on `minshire[0]` (the stops 65 W / 70 °C).
- **Every device-management command sent was a READ**; arm S sends no WRITE (§ Device commands sent).

## The answer, as A3-1 words it

**E184 arm S not run: the smoke's 16-shire n = 19 quad read +0.358 W, above +0.30 W.** The gate (`check_e184_v2.py smoke`, kit note 1 section 1)
on the box and again at the desk on this directory's copy ([`smoke-gate-desk-arm-s.txt`](smoke-gate-desk-arm-s.txt)):
`SMOKE NO-GO: m16 n19 read 0.358 W, outside -0.15-0.30`. That was the only failing band: the null, the 32-shire n = 121 step, the
every-minion step, the instruction rate (every launch within 0.11% of the median) and the clock all read inside theirs.

By A3-1 this is **never an E184-P verdict**, and the arm is **not re-launched that day** without a dated departure. So **no rule of arm S has a
reading**: E184-N (the null step), E184-L (the ladder's linearity), E184-P (the int8 pair's operating point and METER EXCLUDED), E184-J (a jump
between levels) and E184-C (the scan across code 1024) are all **not scored**, and their registered forecasts (N NULL, L LINEAR, P LINEAR and
METER EXCLUDED, J NONE SEEN, C NONE SEEN; the governing LINEAR powers 0.953 and 0.952, A3-2) stay untested.

| smoke quad (registered band, kit note 1 section 1) | registered step (E184.md section 5.1, 8.256 mW a minion) | the gate's reading (v1's reader) | in band |
|---|---|---|---|
| 32 shires, n = 0, the null (-0.15 to +0.15 W) | 0 | **-0.0051 W** | yes |
| 32 shires, n = 121 (0.70 to 1.30 W) | +0.9990 W | **+0.8101 W** | yes |
| 32 shires, n = 1024, every minion (7.6 to 9.3 W) | +8.4541 W | **+8.5874 W** | yes |
| **16 shires, n = 19** (-0.15 to +0.30 W) | **+0.1569 W** | **+0.3578 W** | **no** |

## Post hoc (written after the data; deciding nothing)

From [`posthoc-arms-e184.json`](posthoc-arms-e184.json), made by [`posthoc_arms_e184.py`](posthoc_arms_e184.py) from this directory's copy of
the smoke with the kit's own readers imported unchanged (`check_e184.quads`, the gate's; `reduce_e184_v2.read_process_a2`, the reducer's,
which adds A2-5's refresh rule):

- **The 16-shire quad's +0.358 W carries one partial dip.** Its first A block (nine kept refreshes, median 29.85 W) holds one refresh at
  **26.74 W, 3.11 W below the block's median**; E82 amendment A2's dip rule kept it, so that block reads 29.51 W against the second A block's
  29.85, and the quad's contrast reads +0.358 W. **A2-5's rule** (a kept refresh more than 0.5 W from its block's median is set aside;
  registered in A2 for the reducer) sets it aside, and the quad then reads **+0.1847 W, 1.18 of its registered +0.157 W step**, inside the band.
  So the stop points to a dip the box's gate keeps, not to a meter or a power reading long at E178's operating point.
- **The 32-shire n = 121 quad carries one too:** a refresh at 33.60 W, 2.43 W below its second B block's median (36.03 W); the gate's reader
  gives +0.810 W, A2-5's +0.963 W (0.96 of the step). The null and the every-minion quads have none (A2-5 reads them the same: -0.0051 and
  +8.5874 W, the latter 1.016 of its step).
- **Why the gate saw it and the registration's figures did not:** A2-5 governs the reducer only, as kit note 2's nit (f) says of the box's
  calibration; the box's smoke gate also reads with v1's reader. A2-5 counted such refreshes in about 5% of quads on E180's bursts, moving a
  contrast by 0.05-0.17 W, at depths of 0.72-2.34 W; A3-1's NO-GO table (about 1e-6 at a linear meter) is one quad's Gaussian noise
  (`power_e184_a3.py`'s `k_section`), with no dip in it. One dip lowers its block's mean by its depth over the block's refreshes and moves the
  contrast by half that, so a dip deeper than about 2.3-2.6 W (eight or nine refreshes a block) in one of the 16-shire quad's A blocks takes a
  true +0.157 W step past +0.30 W. Today's, 3.11 W, is deeper than any of E180's five.
- **As a pointer only:** one 16-shire quad read with A2-5's rule at 1.18 of its step is far from E178's 0.29, the reading E184-P exists to
  test; one quad is not E184-P (96 quads in three visits), and nothing here is scored.

## The readings, labelled

- **Registered, blind:** the smoke gate's bands and its NO-GO (kit note 1 section 1), with A3-1's reporting words; every forecast and rule
  of arm S, untested today.
- **Measured, reported:** the gate's four readings above, the config reads, the card-minutes and the peaks, read from the session's own files.
- **Post hoc:** § Post hoc.

## Registered before any data, and what the box ran

Every E184 text was committed before the session's opening config read on the card, in one ancestry chain (Sat 7 Nov 2026, PST): the
registration `c6417611` (11:27:45), the kit with A1 `65f844be` (12:23:35), A2 `a887fc74` (14:04:38, alone), kit note 1 `eab0c70e` (14:11:30),
A3 `3b48cf7b` (18:10:08, alone), kit note 2 `571511d0` (18:30:34), A4 `a5f8ec1a` (21:11:38, alone) and kit note 3 `f9dcddac` (21:13:30). The
readiness critics of Q154 and Q155 read E184 READY WITH GAPS (arm S's gap: its host's first compile on the box). The lab's HEAD at this
arm's look was `0f6a8c45` (E182's data, 02:09:59 PST Sun), and no E184 file had changed since `f9dcddac`.

The window, recorded by arm S's step 1 at 00:01:55: no session starts after 05:30 PST and every run ends by 07:45 PST (Sun 8 Nov); a launch
needs the arm's 8,100 s before the last end. Arm S ran by kit note 3's section 3 table, after E182's session and its step 11 copy-back on the
same card (E182's card lane's brief, section 2), with arm S's own runbook output directory and the day's one lock file. Every remote call came
after a 15 s probe and ran under its bound: 26 calls from step 4 on, 25 rc 0 and one rc 14 (step 11's first copy, below); the longest, the
session wait, 30.3 s of its 600 s; no login link appeared.

| box step | when (PST) | what it read |
|---|---|---|
| 1, `rb/s02_window_e184.sh 2026-11-08 05:30 07:45` | 00:01:55 (the claim lane) | the window (above) |
| 2, `rb/s03_desk_e184_v3.sh` | 00:02:00-00:02:14 (the claim lane) | at `45e514e3` = origin/main; HEAD descends from `65f844be`; E184's paths clean; the eight lists 11/44/6/45/3/20/1/18 OK; harness v2 rebuilt; the plan and the 467 images re-made; HARNESS OK 59; no E184 data in any ref |
| 4, `q141k-runbook/k6/s05_look_k6.sh aifoundry3` | 02:18:58-02:18:59, and again 02:21:31-02:21:32, right before the launch | **FREE**: et-who's "No process holds an ET-SoC-1 device node or card lock" (0 holder lines), no device process of ours or of another account; idle logins only (an idle login does not block); the host booted 2026-10-26 15:18:24 |
| 3, the post | 02:19:06-02:19:12 | read back: it already held arm S's clause (§ Card and post); not edited |
| 5, `rb/s07_sync_e184.sh S` | 02:19:20-02:19:22 | every file of `harness-e184-v2.json`, 59 files in 7 paths, after `check_e184_v2.py harness` read them at the harness's sha256 |
| 6, `rb/s08_build_e184.sh S start`, `wait` | 02:19:29-02:19:32; 02:19:37 | the job 02:19:30-02:19:34, rc 0: `build_e184.sh` **BUILD OK** (the patched host's first compile against the real runtime on aifoundry3), HARNESS OK 61 with the binaries, `preflight_e184_v2.sh S` GO (32 send sites, 0 disallowed, no allow-list) |
| 7, `rb/s09_reads_e184_v2.sh S` | 02:20:25-02:20:26 | `et-lab-manifest` kept on the box; the config through E128's guard under card 0's lock: 0 W / 65 °C / max_power / 600 MHz / 523 mV, kept on the box as step 7's read; et-who clean |
| 8, `rb/s10_dry_e184.sh S start`, `wait` | 02:20:32-02:20:35; 02:20:41 | the dry job rc 0: pass 18410's 108 quads, the smoke's four and the stop-path test as V3_DRY, and the start gate refusing with 8 |
| 9, `rb/s11_session_e184.sh S` | 02:21:38-02:21:44 | the window's gates; k6's guard (no dry pass or session of ours running); both jobs ended rc 0 today; launched detached with T0 1794133299 (02:21:39) |
| 10, `rb/s20_wait_e184.sh S` | 02:22:03-02:22:34, one bounded call | the session's end at its gate: `smoke gate failed (stop test rc 0, smoke rc 0, gate 1): no pass runs`, then `session end (T0 1794133299)`; the step exits 16 (GATE-STOPPED) |
| 10b, `rb/s09_reads_e184_v2.sh S after` | 02:24:54-02:24:55 | after this T0's end line: the config as at the start, kept on the box as step 7's read; et-who clean |
| 11, the release, then `rb/s22_collect_e184_v3.sh S` | 02:25:01-02:26:24; 02:26:34-02:26:36 | the post's release; then the first copy back **exited 23** (below), and the step stopped (14) |

The session's own lines, as step 10's wait printed them from the box's session log: `session start, arm S, kit v2 (budget anchor T0 1794133299
= 02:21:39 PST)`; at the launch, `HARNESS OK: 61 files`, `dmcmd_audit preflight rc=0 (dmcmd_audit: GO (32 send site(s), 0 disallowed;
allow-list: none))`, `No process holds an ET-SoC-1 device node or card lock.` and the start config read
`{"tdp_w":0,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,"minion_mv":523}`; `stop-path test rc=0`;
`e184-smoke p18401 ends: ok 4/4 quads readable; busy samples 286, all 600 MHz: True`; `smoke rc=0`; the gate's line; `session end (T0
1794133299)`.

### Step 11 v3 stopped at its first copy (what is here, and what is still on the box)

Step 11 v3's first copy names the arm's three pass directories, `e184`, `e184-smoke` and `e184-stoptest`. Only the queue makes `e184`, and the
gate stopped the session before the queue, so the box holds no `e184` directory: rsync copied `e184-smoke` and `e184-stoptest`, reported the
third as missing and exited 23, and the step stopped (14, "the copy back exited non-zero") **before its second copy (the box's `build/e184/`,
the session's own files), before the collector (`collect_e184_v3.sh`: reduce v4 with A4, score v3) and before its desk-path and login
gates.** The kit's tests never collected a gate-stopped session. No other copy or box command was run in its place.

- **Here:** the smoke and the stop-path test, exactly as that first copy brought them ([`raw/aifoundry3/`](raw/aifoundry3/), 20 files, with
  the collector's own exclusions); the stop-path test recorded no launch (step 11 v3's own check, run at the desk); the gate's re-run at the
  desk; the post hoc pair; this README and [`SHA256SUMS-arm-s`](SHA256SUMS-arm-s).
- **Still on aifoundry3** (in our own tree's `build/e184/`, collected by nothing yet): the session's log, its `.out`, the two session config
  reads with their times and the device layer's stderr, `dmcmd-preflight-S-t1794133299.txt`, step 7's two reads (`config-S-step7-1794133226.json`
  before and `-1794133494.json` after) and the dry pass's start-gate log. Their contents named above come from the runbook's own printed
  output. **No `reduced-e184s-v4.json` and no arm S score exist**: by A3-1 there is no arm S verdict to score, and the reducer's session gate
  would read NOT SCORED (the log has no "smoke gate passed" line; the smoke re-checked at the desk reads NO-GO).
- A later collection needs a dated kit note whose step 11 copies only the pass directories that exist; it would add its files beside these
  (arm B's `scored-e184-v3.*` stay as committed).

## Device commands sent

As registered (E184.md section 4; kit v2's arm-S block), every telemetry call through E128's guard: `ettelem config` at box step 7, at the
session's start and end, and at step 10b; `ettelem sample` at 10 Hz in the stop-path test and the smoke, with no `--reset-ms`. Sent:
GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**,
GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all READs**, the two in bold the PMIC
voltage-register reads the owner's rule of 2 November 2026 allows. **Arm S sends no WRITE**: no statistics reset, no other SET_*, no
firmware-revisions query, no residency read, no governor, TDP, threshold or clock set, no reset. The enercat host opens the card through the
runtime only (kernel load, copies, launches). The checker (`dmcmd_audit.py`, unchanged), run by step 6 and again by the session before any
device opened: **GO**, 32 send sites, 0 disallowed, no allow-list. No power cycle, and nothing that risks one.

## Card and post

`et-who` at the two looks (02:18:59 and 02:21:32 PST), at step 7, at the session's start and at step 10b: no process held a device node or card
lock, and no other account ran a device process. Idle logins were present; an idle login does not block, and no login is named in any file.
One session of ours on aifoundry3 at a time: E182's session there had ended at 01:53:47 and its copy-back at 01:58:15.

Sun 8 Nov's one `#community-lab` post is message `1568898719959744554`, created by the card day's claim at 00:03:23 PST; E182's lane rewrote
aifoundry3's clause to arm S's at 01:54:29. At this arm's look it read
`<ai> **Claude says:** using aifoundry3 for 2.5 h, until ~04:24 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, so it
was not edited then. **At the release (02:25:16 PST)**, after step 10b, under the Discord lock with `EXPECT_TEXT` (the post's text as a fresh
read gave it) and `EXPECT_CHANNEL=community-lab`, a dry run, then the save: the last card held, so ` — released` was appended, every word kept:
`<ai> **Claude says:** using aifoundry3 for 2.5 h, until ~04:24 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`.
It read back the same from the edit box and from a fresh plan (one post that day, released). No other post was made, and no earlier day's
post was touched.

## Privacy and the public-text scan (before the commit)

The login checks and the public-text scan read this directory's final bytes before the commit (step 11 v3's own login gate never ran, since
the step stopped first); their results are in the commit's record: `scrub_tree_e178.py --check` over the whole directory with the box login
of this repository's owner, E164's `scrub_etwho_e164.py --check` in every directory of it and of a scratch copy of the text inside its `.gz`
files, a search for the others-present and another-user stop lines, the runbook's desk-path gate (`nopath_q142s.py`), and the public-text scan
(`tools/timeline/sanitize_extracts.py`'s fixed list plus the private-network, Mac-home, scratch and e-mail patterns) over every text file and
the text inside every `.gz`. The lab's private name table is absent on the Intel, so names were checked against the fixed list only (a stated
coverage limit).

## Files (arm S's, all new)

| file | what |
|---|---|
| `raw/aifoundry3/e184-smoke/p18401/` | the smoke as the box wrote it (`telemetry.jsonl.gz`, `runs.jsonl.gz`, `marks.jsonl.gz`, `run.log`, `runner.out`, `configs.json`, `check.json`, `block.json`, `code.sha256`, and `sched/` with the four quads' schedules) |
| `raw/aifoundry3/e184-stoptest/p18402/` | the stop-path test (its board and die `stoptest.json` and outputs, `telemetry.jsonl.gz`, `block.json`, `code.sha256`) |
| `smoke-gate-desk-arm-s.txt` | `check_e184_v2.py smoke` (unchanged) on this directory's copy of the smoke |
| `posthoc_arms_e184.py`, `posthoc-arms-e184.json` | § Post hoc's reader and its output |
| `SHA256SUMS-arm-s` | the sha256 of every file above |
| `README-arm-s.md` | this file |

Re-make from the top of the repository (the same bytes under `/usr/bin/python3` 3.9):

```
D=docs/reports/data/2026-11-08-e184-sensor-validation
/usr/bin/python3 -B tools/claims-v3/e184/check_e184_v2.py smoke $D/raw/aifoundry3/e184-smoke/p18401 | cmp - $D/smoke-gate-desk-arm-s.txt
/usr/bin/python3 -B $D/posthoc_arms_e184.py $D/raw/aifoundry3/e184-smoke/p18401 | cmp - $D/posthoc-arms-e184.json
```

## What it does to predicting power

E184 asks whether the board meter reads power right; arm S asks it of small, known steps, above all at E178's int8 operating point, where E178
read his pair at 0.29 of M10's frozen forecast. **Today it gives no answer:** the smoke gate stopped the arm before any pass, so E184-L, E184-P,
E184-N, E184-J and E184-C have no reading, and whether E178's +0.053 W is the card's or the meter's stays open. It fills no cell of the kinds
table. What the stop does tell, post hoc: the box's smoke gate reads without A2-5's refresh rule, so one partial dip in one block can stop
the arm; read with that rule, the one 16-shire step the smoke took sits at 1.18 of its registered size, not near 0.29. A re-run on another day
needs, each as a dated note first: the smoke gate read with A2-5's rule (a box-file change), or the risk accepted in words; today's smoke and
stop-path pass directories moved aside on the box (`lib.sh`'s block bookkeeping skips a pass directory that already holds a `block.json`, so
the gate would read today's smoke again); and a step 11 that collects a gate-stopped session.

SPDX-License-Identifier: Apache-2.0
