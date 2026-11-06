# E181: M11's session 2 on aifoundry3 card 0 (600 MHz pinned): the run kit, ported from E176's, with A6, A7 and A8 carried

*Desk preparation, Fri 6 Nov 2026 (week 45), about 01:10-02:40 PST, on the Intel: no card, no device command, no ssh to a lab box, no post in
the lab's channel, no Modal, no archive. Nothing here has touched a card. E181 is M11's session 2 (the orchestrator's number). It is M11's
first scored session, since E176 (session 1) was refused at G0 and scored nothing. It is step 1 of
[`../m11/REGISTRATION.md`](../m11/REGISTRATION.md) section 13, as A1-A8 amend it, for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **items 9 and 8** (heat over minutes; the
heat path between sessions). It runs on the owner's go for a card day, with fresh lab approvals, launched before 12:00 PST (A6's and A7's
cool-hour plan), before E178 on the same card.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 01:30 PST: public rows H07, H08, H12,
   H14, H24, H25 and L10 (opaque pointers), and the map's row 6 (aifoundry3's idle floor).
2. **Used.**
   - **E176's kit** (`03582d2f`; its dated notes 1 `6ecab3c5`, 2 `6b013ad9` and 3 `5db7bcf7`): `run_e176.py`, `block_e176.sh`,
     `session_e176.sh`, `smoke_gate_e176.py`, `preflight_e176.sh`, `collect_e176_v2.sh` and its box list, ported (the table below). Its
     design, smoke, stops, watcher, C wrapper, sampler, guards and card lock carry over unchanged.
   - **The q143k runbook** (`92a1b27f`, with step 22 v2 and its launch gate `6b013ad9`, and its dated note 2 `5db7bcf7`): every step ported to
     `rb/`, with note 2's fixes (below).
   - **M11's registration and amendments:** `3c31a91d`; A1 `f49b7ddd`, A2 `d3d97fe2`, A3 `ed24bc6e`, A4 `0b554d25`, A5 `9b084c66`, A6
     `95c75047`, A7 `65a93fbb` and A8 `80b92990`. A8 was written by this lane before the kit (the residue prediction, below).
   - **Round A's floor study** (`docs/reports/data/2026-11-05-q145a-a3-idle-floor/`, `95c75047`, with its dated note 1, `65a93fbb`): the
     floors, the residues and both gates on the history, which A6 and A7 rest on.
   - **Round A's footing law** (`../footing-law/FOOTING-LAW.md`, `c14e5f35`; its dated note 1, `65a93fbb`, N1; the study
     `docs/reports/data/2026-11-05-q145a-footing-law/`, `0f4204e9`): FL1's aifoundry3 law and FL5(c) as N1 fixes it, which M11's scorer v3
     computes on E181's rests.
   - **M11's scorer v2** (`ebdbb35c`), imported unchanged by the new [`../m11/score_m11_v3.py`](../m11/score_m11_v3.py).
   - **E176's committed pass** (`docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/`, `5db7bcf7`), named to the scorer as the card
     kind's earlier M11 session. Its refused G0 excludes it with its own reason.
   - Carried through E176's kit, unchanged: E97's runner (`run_e97b.py`), E89's sampler, E78's four tiles and `kinds.json`, Q139(k)'s check
     of C, E128's config guard, Q136(w)'s `dmcmd_audit.py` with E144's table, v3.1's `rb_run.py`, `nopath_q142s.py` and `ccdone_q142s.py`, and
     E164's login scrub.
   - *The same quantities at the same operating point, earlier:*
     - A8's residue prediction, 0.414 °C, against E176's measured 0.383 °C (the same smoke, the same card);
     - the DRY-INTEL pass's plan against E176's committed dry pass: 73.5 minutes; H_E 80 launches at 7.56 s; Z, L1, S and L2 85 each;
     - the FL5(c) estimator against N1's committed dry run on E97's rests: 0.3196 against 0.3106 W/°C, equal to the digit.
3. **Not used.**
   - `watcher_q142s`: it fixes run_hpl.py's race, and E181 runs E97's card class (E176's dated note 1).
   - aifoundry2 (E177): not built.
   - The host's NVMe composite as a gate, and an inlet thermometer (A6, A7: none exists).
   - A registered C rule for M11's holds: none is registered (fault 1 below, carried).
   - Q124's counts; anything of the NDA tier.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256 line;
   no NDA-tier piece, name, verdict, ratio or figure is cited.

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **A8, the residue prediction** (before the kit) | M6's step response on the planned smoke: **0.414 °C**, 0.086 °C under A6-2's 0.50 °C line; committed misses −0.25 to +0.06 °C (sd 0.13, n 4); A8-R reads the line referred to the prediction | `../m11/REGISTRATION.md.dated-note-A8.md`, `80b92990` |
| **DRY-INTEL**, in a tree built from step 7's sync list alone | **7 of 7 PASS**; it found a missing file first (below) | [`logs/dry-intel.txt`](logs/dry-intel.txt) |
| **the runbook's desk test**, stand-in ssh and rsync | **42 of 42 PASS** (95 s) | [`rb/logs/selftest.txt`](rb/logs/selftest.txt) |
| **M11's scorer v3 self-test** | **12 of 12 PASS** (40 s): a refused G0, a residue refusal and a passing session among them | `../m11/selftest-score-m11-v3.txt` |
| **device commands**, the kit | **GO, 38 send sites, 0 disallowed**, every one a READ; bare, NO-GO at exactly E176's two sites | [`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-bare.txt`](dmcmd-audit-bare.txt) |
| **device commands**, the runbook | **GO, 11 send sites** with E128's guard; NO-GO at exactly step 9's guard call without it | [`rb/logs/dmcmd-audit.txt`](rb/logs/dmcmd-audit.txt), [`rb/logs/dmcmd-audit-bare.txt`](rb/logs/dmcmd-audit-bare.txt) |
| **the dry listing** | 12 step calls, each exit 0, no ssh or rsync call | [`rb/logs/dry-listing.txt`](rb/logs/dry-listing.txt) |

**Every device command is a READ:** the two PMIC voltage-register reads the owner allowed on 2 November 2026. There is no statistics reset,
no firmware-revisions query, and no set of any kind (no governor, TDP, threshold or clock). No power cycle, and nothing that risks one.

**An E174-class defect found and fixed (inherited from E176's kit).** `run_e176.py` calls E97's `check_reused()`, which reads eight files.
One of them, `tools/claims-v3/e89/reduce_e89.py`, is in neither E176's box list nor its step 7's sync. E176 ran only because aifoundry3 kept
a matching copy from earlier sessions. DRY-INTEL, in a tree built from the sync list alone, stopped on it at once. **E181's box list names it:
30 entries, 27 repo files and the three box binaries**, so step 7 syncs it and step 8 checks it. Its sha256 equals E97's freeze
(`predictions-e97.json`'s harness block), as do the other seven.

## A6, A7 and A8 carried

| rule | where in the kit |
|---|---|
| **A6-1, the floor F0** | `run_e181.py`, the smoke pass, before its first launch: the 34-sensor mean (E97's `code_to_c`) over the first 3 s of the pass's own sampler file, with the firmware reading and board W, in a `floor` mark. F0 above 53.9 °C, or unreadable, ends the pass with exit 7 before any launch. `session_e181.sh` then ends the session: no smoke gate, no measured pass. `smoke_gate_e181.py` checks the mark (check 7) |
| **A6-2 with A8-4, the start gate** | `run_e181.py`, after R0 (5 minutes, its room the last 120 s): holds run only if R0's room ≤ 53.9 °C and R0's room − F0 − 0.414 ≤ 0.50 °C. F0 is read from the smoke pass's floor mark (`--floor-marks`). The `start_gate` mark records the room, both lines, F0, the residue, the 0.414 °C, the excess, `room_ok`, `residue_ok` and `passed`. A 10⁻⁹ °C tolerance keeps "at or under" true at a line in floating point (an excess of exactly 0.50 °C computes as 0.5000000000000016) |
| **A6-3, H_E's pattern** | the cool pattern at a room ≤ 51.5 °C (3.20 s every 7.56 s), the warm one in (51.5, 53.9] (2.60 s every 7.98 s) |
| **A6-4, unchanged** | every stop: no launch at a firmware reading ≥ 70 °C; a hold ends at ≥ 72 °C or ≥ 65 W; the pass ends at ≥ 74 °C, refused if looser. The plan, the holds and their order, and the 76-card-minute cap |
| **A6-5 with A7-1, FL5(c)** | M11's scorer v3, on the session's rests after its holds (R1-R5, rule F). The primary: per whole firmware degree in FL1's band against FL1. Beside it: the 34 codes in E97's 0.5 °C bins against E97's law, and the degrees 52-58 alone. Reported, never a gate |
| **A7-4, the rest** | step 11: under 40 minutes since our last real session end on this card, refused (the gate, kept). Under an hour, refused unless `--under-an-hour` (a logged departure from the plan) |
| **A6's and A7's cool-hour plan** | step 11: at or after 12:00 PST, refused unless `--after-noon` (logged); step 2 says whether his window keeps the plan |
| **A8-6 (disclosed)** | not resolved here: the chain reads only the measured pass, so the smoke's residue at H_E's anchor goes unseen. The estimate is −0.30 °C on H_E's e, against −0.12 °C for E144's H_H after its 8-minute R0. This bears on HM-E144 and HM-CAL. Named for the readiness critic |

## E176's note-2 runbook fixes, and the code verifier's two faults

- **Step 11's rest rule counted a V3_DRY session's end: FIXED, twice over.**
  - A V3_DRY session now writes its own log, `build/e181/session-dry.log`, ending "DRY session end". Only a real session writes
    `build/e181/session.log`.
  - Step 11 reads every session log of ours on this card (`build/e171`, `e176`, `e178`, `e180` and `e181`), on any day, and skips any session
    block whose lines carry `DRY` or `DESK:`. E176's own log holds such a block.
  - The desk test's S4 shows it: a dry end 10 minutes ago is skipped, and the real end 3 h ago decides. Step 10 checks on the box that its dry
    session left the real log untouched.
- **Fault 2, "the scorer writes before the gates": FIXED.**
  - `collect_e181.sh` never scores, and refuses to start if a scored file is already there.
  - Step 22 (`rb/s22_collect_e181.sh`) runs, in order: the lists; the collection; the session's own gates (`cclaunch_e181.py --gates-only`:
    F0-STOPPED or G0-REFUSED, exit 16, nothing scored); v3.1's cc_gate; the launch gate; the login scrub; the desk-path gate; a check that no
    scored file exists. **Only then** does it run `score_e181.sh`, followed by the desk-path gate on the scored files.
  - The desk test's C2-C20 and E2 each show no scored file after a stop.
- **Fault 1, "no registered rule reads a C FAIL for M11's holds": CARRIED, with note 2's words.** No C rule is registered: E166's form,
  which M11 keeps, reports C per launch. `cclaunch_e181.py` prints the count of C FAIL rows with "no registered rule reads them; 'computed
  correctly' only when all_pass is True". A record of E181 quotes the CCHECK-DONE and COUNT-OK lines, says "every launch the marks record was
  checked for C, N FAIL", and says "computed correctly" only when all_pass is True.
- **The same verifier's kit-v4 items: done.**
  - `cclaunch_e181.py` requires distinct `t_start_ms` (COUNT-DUP; desk test C20).
  - v3.1's `rb_run.py`, `nopath_q142s.py` and `ccdone_q142s.py`, with E164's scrub, are pinned by `rb_common_e181.sh`'s own hashes at every
    step's start (16 on a change; desk test P1) and by `rb/SHA256SUMS-rb-e181`.

## The run kit (E176's, ported)

| file | from E176's | what changed |
|---|---|---|
| [`run_e181.py`](run_e181.py) | `run_e176.py` | A6-1's floor mark and stop; A6-2 with A8-4's gate; WARM_HI 53.9; `--floor-marks`; the dry-only `E181_DRY_ROOM_C` and `E181_DRY_FLOOR_C`; passes 18101 and 18120; configs.json names the eight commits |
| [`block_e181.sh`](block_e181.sh) | `block_e176.sh` | E181's runner and names; `E181_FLOOR_MARKS` to the measured pass; exit 7 read as A6-1 in the smoke and as the start gate in the measured pass |
| [`session_e181.sh`](session_e181.sh) | `session_e176.sh` | the dry log apart; the smoke's exit 7 ends the session (A6-1); F0 handed to the measured pass |
| [`smoke_gate_e181.py`](smoke_gate_e181.py) | `smoke_gate_e176.py` | check 7: one floor mark, F0 readable from 8 or more samples and ≤ 53.9 °C, written before the smoke's first launch |
| [`preflight_e181.sh`](preflight_e181.sh) | `preflight_e176.sh` | E181's files in E176's list |
| [`frozen-e181.sha256`](frozen-e181.sha256) | `frozen-e176.sha256` | 30: E181's five card files, `reduce_e89.py` added, E176's 21 other repo entries and its three box binaries unchanged |
| [`collect_e181.sh`](collect_e181.sh), [`score_e181.sh`](score_e181.sh) | `collect_e176_v2.sh` | the collection without the scorer; the score as its own step, run by step 22 after the gates |
| [`dry_intel_e181.sh`](dry_intel_e181.sh) | E178's `dry_intel_e178.sh` (form) | DRY-INTEL in a tree built from step 7's sync list alone |
| [`rb/`](rb/) | `../q143k-runbook/` | every step ported (`s02`-`s22`, `cclaunch_e181.py`, the dry listing, the desk test and its data maker); step 11 is `s11_a3_launch_e181.sh`, a name ours_live's pattern can never match |

## Card-minutes, the order, the window, and the box steps

- **Card-minutes: about 75** (73.5 of plan and about 1.5 for the smoke and its stop tests), inside the registered **76-card-minute cap**,
  which `session_e181.sh` enforces from T0. An A6-1 stop costs about 0.1 card-minutes; a G0 refusal about 6.5, as E176's. **Wall time:**
  about 1.75 h on the box, then about 10 minutes of collection and score at the desk.
- **The order on aifoundry3 card 0:** E181 first, at least an hour after our last session there ended (E176's, Thu 17:27 PST), and launched
  before 12:00 PST. Then E178 FULL, after E181 has ended, at its own gates. Never two of our sessions on the card. Nothing of E181 on
  aifoundry1 or aifoundry2.
- **His go names the day, the last start and the last end.** Step 2 records them. E181 needs 76 minutes before the last end.
- **The day's one post** (section 15's rules; step 6, not scripted): the clause `using aifoundry3 for 2 h, until ~HH:MM PST
  [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
  - Every rewrite is made under the discord lock with EXPECT_TEXT.
  - E178's clause follows E181's, and " — released" is appended at the end, every word kept.
  - Never a second post.
- **The steps** (call each with this card day's `RB_OUT` outside the repo and `RB_LOCK`; exit codes are v3.1's):

| step | file | what |
|---|---|---|
| 2 | `rb/s02_window_e181.sh <day> <last start> <last end>` | the window; whether E181 fits (76 min) and whether the cool-hour plan holds |
| 3 | `rb/s03_desk_e181.sh` | pull; HEAD descends from A8 (`80b92990`); the paths clean; M11's thirteen lists and the footing law's two; the kit list; the runbook's list; the box list's 27 repo entries |
| 5 | `rb/s05_look_e181.sh aifoundry3 [--wait]` | look first; the holder rule; idle logins do not block |
| 6 | (not scripted) | the day's one post with aifoundry3's clause |
| 7 | `rb/s07_a3_sync_e181.sh` | the kit and the box list's 27 repo files, from the pushed commit only |
| 8 | `rb/s08_a3_preflight_e181.sh` | on the box: the box list 30 OK, the preflight GO, the runner's `--list` with no tile problem |
| 9 | `rb/s09_a3_reads_e181.sh` | et-lab-manifest; the config through E128's guard (0 W / 65 °C / 600 MHz); et-who |
| 10 | `rb/s10_a3_dry_e181.sh start` then `wait` | the box's dry job: the V3_DRY session (the real log untouched), the toy's full block, the room line, the residue line, A6-1, the session gate |
| 11 | `rb/s11_a3_launch_e181.sh [--later-try] [--under-an-hour] [--after-noon]` | the launch, after the rest rules and the cool-hour plan |
| 20 | `rb/s20_wait_e181.sh` | bounded waits; A6-1-STOPPED, GATE-STOPPED and G0-REFUSED read on their own (16) |
| 21 | (not scripted) | the release |
| 22 | `rb/s22_collect_e181.sh` | the collection, the gates, then the score (`docs/reports/data/<day>-e181-m11-session2-aifoundry3/`) |

## What each reading answers (registered; nothing is measured here)

E181 is the card kind's first scored session, so **k = 1 and nothing enters M11's primary**: every reading is reported, labelled "one
session", as a candidate for the next session (REGISTRATION.md § 6). The power figures are E176's README's, which A6-A8 leave unchanged.
- **HM-LG** at df (1, 3): GAIN 68.6% at a common 3.2% gain, LEVEL 65.2% at 0.27 °C, NOT SEPARATED 93.0% with no effect.
- **HM-E144:** does H_E repeat E144's H_H? Read with A8-6 in mind.
- **HM-HE:** weak in one session.
- **HM-CAL (A2)** on L1, S and L2, and **HM-CAL-I8 (A4)** on L2. Their agreement readings (A5) read NOT SCORED with one session.
- **FL5(c),** the footing law's first blind check: PASS if the rests' slope sits within 0.02 W/°C of FL1's at the same degrees. A FAIL from
  rests mostly at 52-55 °C may be FL1's own season-to-season spread (N1).

## What this does to predicting power and heat

Nothing yet: no frozen prediction changes, and no out-of-sample error moves until E181 runs. E181 then gives the first per-session reading
of heat over minutes on aifoundry3. Heat over minutes is still the largest open heat error: Q138(t)'s chain unscaled, 0.49 °C blind given the
watts.

## Compute

The Intel, through the round's local slot, one job at a time:
- A8's study (5 s);
- M11's scorer v3's self-test (40 s);
- the DRY-INTEL pass, four runs: the first stopped on `reduce_e89.py`; the second on a wrong constant in its own check of the toy's F0
  (51.433 °C, the toy's code 1950); the third passed; the committed fourth, 02:16:38-02:17:25 PST (48 s);
- the runbook's desk test, three runs. The first found two faults: the stand-in ssh's seekable stdin (S4-S6; real ssh hands the remote
  shell a pipe), and step 22 reading the gates' exit code where rb_run.py reports every non-zero exit as 14 (C17-C18). The second passed 42
  of 42. The committed third ran 02:17:25-02:19:01 PST (95 s), with `ccheck.py --jobs 2` inside E1-E2;
- the audits and the dry listing (seconds).

No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
