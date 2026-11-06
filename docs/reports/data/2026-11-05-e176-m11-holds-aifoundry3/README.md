# E176: M11's first heat-over-minutes session on aifoundry3 - G0-REFUSED: no hold ran, nothing is scored, and this is not a failed prediction (R0's room read 53.582 °C against G0's 53.0 °C line)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**items 9 and 8, heat over minutes**. E176 is M11's first session (H_E, Z, L1, S, L2), as
[`REGISTRATION.md`](../../../../tools/claims-v3/m11/REGISTRATION.md) section 13 and its dated amendments A1-A5 register it and as
[`e176/README.md`](../../../../tools/claims-v3/e176/README.md) kits it.*

***G0-refused, not scored, not a failed prediction.** This directory is the evidence of a gate that worked: the session ran its checks,
the smoke with its five stop tests on live samples, and R0, and then G0, the registered start gate, refused the measured pass. No hold ran,
so no M11 reading exists: every one reads NOT SCORED. Step 22 v2 stopped at NO-LAUNCH (exit 14) by design, and the lane committed nothing.
The records round (Q143(r), Thu 5 Nov 2026 evening) committed the collection here as it was collected, unchanged, so that the figures the
records quote rest on committed files, under [E176's dated note 3](../../../../tools/claims-v3/e176/README.md.dated-note-3.md) and the
[q143k runbook's dated note 2](../../../../tools/claims-v3/q143k-runbook/README.md.dated-note-2.md): exit 14 means "do not score", not
"do not record".*

*Thu 5 Nov 2026 (week 45), the evening card round (Q143(c)), aifoundry3 card 0 at 600 MHz pinned (TDP 0 W, 65 °C, max_power, 600 MHz,
523 mV read at the session's start and end, nothing set). Registered before any E176 data, one ancestry chain: M11's registration
`3c31a91d` (07:41:57 PST), A1 `f49b7ddd` (08:44:59), A2 `d3d97fe2` (10:07:42), A3 `ed24bc6e` (11:07:48), A4 `0b554d25` (12:16:24), M11's
scorer and E176's kit `03582d2f` (12:38:01), the q143k runbook `92a1b27f` (12:45:55), E176's dated note 1 `6ecab3c5` (12:47:30), A5
`9b084c66` (13:46:11), M11's scorer v2 `ebdbb35c` (14:35:18) and step 22 v2 `6b013ad9` (14:55:39). The owner's go for the day's card time
came at about 11:15 PST ("feel free to use all 4 cards for experiments"), covering each registered experiment once it is kitted and passed
by a readiness critic; the readiness critic (15:34-15:56 PST, at lab `04159d14`) read E176 READY and set the window: no session starts after
18:30 PST and every run ends by 20:30 PST. The box's tree was synced at `04159d14` (16:39:56 PST: the kit's 29 frozen files OK, its
device-command audit GO with 38 send sites, 0 disallowed). The day's one `#community-lab` post (message 1567984130841641044) named
aifoundry3 from 16:31:09 PST ("using aifoundry3 for 2 h, until ~18:30 PST") and was released at 18:08:34 PST (" — released" appended,
every word kept; Discord's edit stamp 18:08:32.486).*

## The answer

| what | reading | line or rule | verdict |
|---|---|---|---|
| **G0, the start gate** | **R0's room, the 34-sensor mean over its last 120 s: 53.582 °C** (firmware 52.999 °C), at 17:27:34 PST | holds run only if the room is at most 53.0 °C ([`e176/README.md`](../../../../tools/claims-v3/e176/README.md), lines 79 and 188) | **REFUSED**: pass 17620 ended with exit 7, "no hold ran" |
| every M11 reading | HM-E144, HM-CAL (A2), HM-CAL-I8 (A4), HM-LG at df (1, 3), HM-HE, and A5's HM-CAL-AG and HM-I8-AG | one session, and no hold | **NOT SCORED** (`score_m11_v2.py`: "NOT SCORED: no session passed its start gate"); nothing enters M11 |
| the smoke's check of C | `CCHECK-DONE … 57 launches, PASS 57, ROUNDING 0, UNMODELLED 0, FAIL 0, all_pass True` (fp32 27, int8 30); `COUNT-OK p17601: 57 checked launches in 7 processes` | every launch the marks record was checked for C | 57 of 57 computed correctly (all_pass True) |
| the measured pass | `NO-LAUNCH p17620: its marks record no launch: no hold ran, so nothing is scored` | step 22 v2's launch gate | step 22 v2 exit 14 at 18:08:55 PST, by design |
| the smoke's gate | GO, with its five stop tests run on live samples (below) | E166's form | GO |

Sources: [`aifoundry3/e176/p17620/marks.jsonl`](aifoundry3/e176/p17620/marks.jsonl) (kinds `room` and `start_gate`),
[`logs/session.log`](logs/session.log) ("pass 17620 rc=7"), [`scored-m11.json`](scored-m11.json) and [`scored-m11.md`](scored-m11.md),
[`ccheck/ccheck-all.json`](ccheck/ccheck-all.json) and [`ccheck/ccheck.txt`](ccheck/ccheck.txt), [`logs/smoke-gate.json`](logs/smoke-gate.json).

## The readings, labelled

Everything in this table is measured on the card in this session, except the rows marked **post hoc**, which were read afterwards from
committed data and decide nothing.

| what | reading | source |
|---|---|---|
| card-minutes | **6.4** of a 76 cap: config reads at 17:21:16 and 17:27:38 PST; the smoke 17:21:17-17:22:29, then pass 17620's R0 17:22:34-17:27:34 (300 s); session start (T0) 17:21:15, launched at 17:21:20 | `logs/config-session-start.json.time`, `config-session-end.json.time`, `logs/session.log` |
| the card's idle floor at the start | **53.202 °C** 34-sensor mean, firmware 52 °C, board 23.97 W, at the smoke's first sample (17:21:17), 4 h 46 min after E171 ended on this card (12:35:33). It is already above G0's line | `aifoundry3/e176-smoke/p17601/telemetry.jsonl.gz`, first line |
| R0's fall after the smoke | the 34-sensor mean fell from **54.814 °C** at +0 s to **53.487 °C** at +300 s, at −1.689 °C per 10 min over R0's last 240 s, so G0's window sat about **0.38 °C above the floor** | `aifoundry3/e176/p17620/telemetry.jsonl.gz`; `scored-m11.json` › `sessions` › `S1:p17620` › `room_drift_over_R0_C_per_10min` |
| earlier floors on this card, **post hoc** | at a session's first sample: E154 (Tue 3 Nov 17:53:00) 50.982 °C, firmware 50 °C; E166 (Wed 4 Nov 14:20:52) 51.838 °C, 51 °C; E171 (this morning, 11:38:27) firmware 49 °C, board 23.52 W. The floor moves 2-3 °C between sessions and within a day | those runs' committed smoke telemetry, first lines |
| the five stop tests (the smoke) | the gate line at 1 °C: 0 launches; the hold die and hold board lines: the holds ended with 0 launches; the in-launch board line at 28.49 W ended the launch in flight (board read 50.76 W); the session line at 1 °C ended the block with exit 6 (die 54 °C, 34-sensor mean 55.04 °C, board 24.52 W) | `logs/smoke-gate.json`; `aifoundry3/e176-smoke/p17601/marks.jsonl` |
| peaks | the smoke: board 51.55 W, firmware 57 °C, 34-sensor mean 57.88 °C; pass 17620 (R0 only): 25.08 W, 54 °C, 54.82 °C. Stops: a hold ends at ≥ 72 °C or ≥ 65 W, no launch at ≥ 70 °C, the pass ends at ≥ 74 °C | the two `telemetry.jsonl.gz` |
| clock and statistics | 600 MHz in 3,776 of 3,776 samples (712 + 3,064); `since_reset_ms` −1 in every sample (no statistics reset); the service processor's running board maximum 68.9 W, unchanged (set before today) | the two `telemetry.jsonl.gz` |
| config at both ends | TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV at the session's start and end | `logs/config-session-start.json`, `logs/config-session-end.json` |

## The room rule for the one later try, and its proxy's resolution

The kit allows one later try after a G0 refusal (`s11_a3_session_q143k.sh --later-try`, which moves the smoke aside once), on a rested card.
The card's own temperature can be read only inside a session, so the E176 lane wrote a rule for "the room has cooled" first, at **17:34:16
PST** (the file's own time), after the host baseline window (17:31:50-17:33:50) and **before** its comparison window (18:05:40-18:07:40). It
is [`room-rule/room-rule.txt`](room-rule/room-rule.txt), copied unchanged from the lane's scratch by the records round, with the five host
windows it read ([`room-rule/`](room-rule/), the host's own sysfs sensors, never the card):
- the host's NVMe composite (hwmon `nvme temp1`), averaged over 13 samples, at least 0.5 °C under the baseline's 38.850 °C (at or under
  38.350 °C), and
- the mean of the host's `coretemp` temp2-temp9 no more than 1.0 °C above the baseline's (host load unchanged).

**It read 38.850 °C in every sample of all five windows** (the baseline, 17:41, 17:50, 17:59 and the comparison), so the rule was not met
and no later try ran; never a third. **Post hoc** (the round's critic): that sensor reports whole kelvins (38.850 °C = 312 K), so the rule
could only ever show a cooling of 1 °C or more. And the card's own floor, 53.202 °C at 17:21, was already over G0's line, with about 0.4 °C
of the smoke's residue on top, so a rest alone could not pass G0 tonight; a later try also had to launch by about 19:14 PST to fit 76
minutes before 20:30.

## Two defects the session showed, and one claim withdrawn

- **The runbook's rest rule counted a dry session.** `s11_a3_session_q143k.sh` greps the last "session end" in the box's
  `build/e176/session.log`, and step 10's V3_DRY session had written one there (line 76, 16:40:26; the first 78 lines of
  [`logs/session.log`](logs/session.log) are that dry session's). So step 11 refused until 17:20:26. The lane read the rule and the log, did
  not call step 11 early, waited in four bounded remote waits (16:46:38-17:20:58, a holder read in each) and launched at 17:21:20; step 11
  printed "rest: 40 minutes since E176's session end". Neither the runbook's desk test (its case S3 used E171's end) nor the readiness
  critic's timeline caught it. The outcome was not affected: the floor at 17:21 was already above G0's line. It is a kit v4 item.
- **The scorer writes before the gates.** `collect_e176_v2.sh` runs `score_m11_v2.py` before step 22 v2's C gate and launch gate, so at
  the exit 14 the three `scored-m11.*` files had already been written. They are kept here exactly as written: the scorer's NOT SCORED
  output. Their label "post hoc" (`scored-m11.md`'s first line) comes from the absent first launch record, which the scorer's precedence
  check needs; it does not come from commit order, since every registration commit above is older than 17:21:15. `scored-m11-lines.jsonl`
  is the collector's own; the round's critic re-ran the scorer and found its JSON and MD byte for byte the same and the lines file
  different only in its write stamps (`t`).
- **Withdrawn: "known to have computed every measured launch correctly".** No registered rule reads a C FAIL for M11's holds (neither
  M11's registration with A1-A5 nor E176's kit registers a C rule; E166's form reports C per launch). So the runbook's dated note 1 and
  `cclaunch_q143k.py` overclaim. What holds here is the count: every launch the marks record was checked for C (57, all in the smoke),
  57 PASS, FAIL 0, all_pass True.

## Who checked it

No data verifier was assigned to E176 in its round. The evening round's critic (18:51-19:20 PST, desk only) re-derived it from this
copy: G0's room 53.5819 °C from 1,200 of 1,200 samples by its own code (E97's `code_to_c`, re-typed); the scorer's outputs as above;
`cclaunch_q143k.py` on the copy NO-LAUNCH p17620 and COUNT-OK p17601, rc 4 (step 22's exit 14); the smoke's 57 C records from a fresh
reference cache identical in every field.

## Privacy and the public-text scan (before the commit)

- **Logins.** E164's `scrub_etwho_e164.py --check` (unchanged, it rewrites nothing; `--owner` the box login of this repository's owner) in
  **every** directory of a scratch copy with each `.gz` unpacked beside it (the scrub reads one directory level and text files only): 8 of 8
  directories read "OK (0 left)". The only box home path in the copy is the owner's own (316 occurrences). The session log's et-who
  readings say "No process holds an ET-SoC-1 device node or card lock"; another account's idle terminal on the box (an idle login, by the
  owner's ruling of 1 November) is named in no file.
- **The public-text scan** (`tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home and e-mail patterns): 45 text
  files, 290 matches, every one the owner's box home path or the configs' tree key that names it, the reviewed class E166's and E171's committed
  data carry; inside the 3 `.gz` files 28 matches of the same class and 0 outside it. The lab's private name table is absent on the Intel,
  so names were checked against the fixed list only (a stated coverage limit).

## Files

All 48 files of step 22 v2's collection are here as collected (652 KB), with three additions by the records round: this README, the
`room-rule/` copies and [`SHA256SUMS`](SHA256SUMS), which pins every file but this README and itself.

| path | what |
|---|---|
| `aifoundry3/e176-smoke/p17601/` | the smoke as the box wrote it: `block.json`, `configs.json`, `marks.jsonl`, `runs.jsonl`, `run.log`, `telemetry.jsonl.gz`, `c-log.jsonl`, the config reads at both ends, the `STOP`/`HOLDSTOP` files of its stop tests, the binary, code and generator hashes, `manifest.txt`, the sampler's files |
| `aifoundry3/e176/p17620/` | the measured pass: R0 and G0's refusal (`marks.jsonl`, `STOP`, `run.log`, `telemetry.jsonl.gz`, `block.json`, the config reads, the hashes); `runs.jsonl` is empty because no hold launched |
| `ccheck/` | the check of C: `ccheck-all.json`, `ccheck.txt` and the smoke's C log (`c-log-p17601.jsonl.gz`) |
| `logs/` | `session.log` (the dry session's 78 lines, then the session), `smoke-gate.json`, `dmcmd-preflight.txt` (the box's device-command audit, GO), the config reads with their times and stderr, `session.out` (empty) |
| `scored-m11.json`, `scored-m11.md`, `scored-m11-lines.jsonl` | M11's scorer v2 output, NOT SCORED, written before the gates and kept as written |
| `room-rule/` | the E176 lane's rule (`room-rule.txt`, 17:34:16 PST) and its five host windows (`hostwin-base.out`, `-w1`, `-w2`, `-w3`, `-cmp.out`), copied unchanged |

## What it does to predicting power and heat

Nothing measured, so no error moves and nothing enters M11. Heat over minutes stays Q138(t)'s chain unscaled, **0.49 °C rms blind given the
watts** over nine large rises (the grouping post hoc), still the largest open heat error; M11's in-session calibration (HM-CAL near 0.10 °C
against 0.27-0.28 °C unscaled if A2's premise holds; HM-CAL-I8 near 0.076 °C on L2) is untested. **Post hoc and not registered:**
aifoundry3's idle floor moves 2-3 °C between sessions and within a day (50.98 °C Tue, 51.84 °C Wed, firmware 49 °C this morning, 53.20 °C this
evening), which is exactly the session level M11's holds exist to read; and a G0 line fixed at 53.0 °C, read about 0.4 °C above the floor
after the smoke, rules out a warm evening. Before M11's next session, a registration question is answered first, with its own run number
and kit (E176's dated note 2, section 3): move G0 or the warm pattern by a dated amendment, or plan the session for a cool hour.

SPDX-License-Identifier: Apache-2.0
