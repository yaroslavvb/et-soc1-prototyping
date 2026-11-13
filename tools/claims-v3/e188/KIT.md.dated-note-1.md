# E188's kit, dated note 1: the rest rule v2 (a session cut mid-queue ends at its run's latest write), step 9 v2 and step 2 v2; verify-e188's six faults answered (Q165, before any E188 datum)

*Thu 12 Nov 2026 (week 46), PST, on the Intel, in Q165 (lane `fix-e188`), desk only: no card claimed, no device command sent, no lab box
reached, nothing posted, no Modal, no mordast. New files only, all under `tools/claims-v3/e188/`. [`KIT.md`](KIT.md) (`726a6b64`), every file
the kit list names (`SHA256SUMS-e188-kit`, 106 of 106 OK) and step 2 v1 (`rb/s03_desk_e188.sh`) stay as committed. **No E188 datum exists.**
This note changes no rule, forecast, threshold, statistic, registered power figure, plan, cap, stop or device command. The registration's side
of the same verifier's faults is [`E188.md.dated-amendment-A1.md`](E188.md.dated-amendment-A1.md) and
[`E188.md.dated-note-1.md`](E188.md.dated-note-1.md), committed before this note, alone (`SHA256SUMS-e188-a1`).*

## Results first (desk checks of code; nothing is measured)

| check | result | log |
|---|---|---|
| **the rest rule v2** on stand-in box trees: v1's twenty cases (E182's, E183's, E184's, E185's, E186's and E188's forms, dry and no-device blocks, the kits' markers, a cut session, a shared day) run on v2 under the box's `set -u`; three sessions cut mid-queue (E188's, E186's and E183's forms) read by v1 and by v2; dry paths; an ended session; a cut session beside another run's later write | **SELFTEST-REST-E188-V2 PASS (32 of 32)**: v1's twenty verdict lines unchanged; v1 reads the cut E188 session as rested 92 minutes at 09:35 (verify-e188's case V2: a launch 10 minutes after the card was last driven), v2 REFUSED at 10 minutes and rest 40 at the edge; E186's form v1 rest 75, v2 REFUSED 29; E183's form v1 rest 90, v2 REFUSED 18 and rest 40 at 09:52; dry files at 08:55 do not count (rest 120); a session with its "session end" reads the same on v1 and v2 (rest 60); a cut session's end is its own run's latest write (rest 60 from E186's end) | [`logs/selftest-rest-e188-v2.txt`](logs/selftest-rest-e188-v2.txt) |
| **the runbook v2** with a fake ssh and rsync on a stand-in box (v1's setup; the stand-in cmake builds the host with g++-13 -O2): the cases that run step 2 or step 9 (A, K, W1-W3, G, P1-P5, H1, S1, D, O, RS, L, C, Z) on step 2 v2 and step 9 v2, and three new: P6 and P7 (step 2 v2's own pins, a change taken before the anchor so step 2 v1's history check cannot see it), RS3 (a cut E188 session on the box) | **SELFTEST-RB-E188-V2 16 of 16 PASS**: P6 and P7 step 2 v1 passes, then step 2 v2 refuses (16) naming the list against its pin; RS3 step 9 v2 refused (10), "REFUSED: 10 minutes since E188's last real session activity", nothing launched; L the launch (0) once the cut session is moved aside, its rest line naming E183's end | [`logs/selftest-rb-e188-v2.txt`](logs/selftest-rb-e188-v2.txt) |
| the dry listing v2, both paths, stand-in ssh, rsync and scp | 19 steps, 0 exiting non-zero, 0 box calls; step 2 v2 once; step 9 v2 on both paths, its remote script carrying the rest rule v2's lines; no line of v1's step 2 or step 9 headers; against v1's committed listing it differs only in those steps, its title line and clock values | [`logs/dry-listing-e188-v2.txt`](logs/dry-listing-e188-v2.txt) |

The cases of v1's runbook test that run neither step 2 nor step 9 (X3, N1, U, R, V, N6, LJ: steps 6 and 8, unchanged by this note) are v1's
committed log's ([`logs/selftest-rb-e188.txt`](logs/selftest-rb-e188.txt), 21 of 21). No step but 2 and 9 changes.

## 1. verify-e188's six faults, item by item

| # | the fault (verify-e188, all minor, none blocking) | answer |
|---|---|---|
| 1 | tier: E188.md section 2 describes the NDA-tier file beyond its bare sha256 line | E188.md's dated note 1, sections 1-2: the departure recorded, those passages set aside as description (no rule reads them), records repeat none of them, a train's cost restated from public sources (E182's sizing rule and half-width, `plan-e188.json`) |
| 2 | section 8 says the arms' readings go "into files beside the data"; the kit writes them outside the repo, with no dated amendment | E188.md's dated amendment A1-1: outside the repo, the private Horace Hub only, public records name the arms by their committed files; the kit's gate (`rb/check_arms_e188.py`) already does this, so KIT.md's "departs from E186's form" now matches the registration |
| 3 | latent: the rest rule reads a session cut mid-queue as ended at its last log line ("queue starts"), because the queue and the blocks never write the session log | **this note: THE REST RULE v2** (section 2), step 9 v2 that sends it, step 2 v2 that pins it, and their desk tests |
| 4 | inherited: a die stop during the smoke's train processes sends the session to the fallback, where section 12 says a stop ends the queue | E188.md's dated amendment A1-2: the reading registered before any datum (a failed smoke train gate: no train that day, the fallback under the live stops, E188-LV its reading). The box files are not changed here: see section 4 |
| 5 | inherited: a non-finite telemetry sample trips no stop | a records line (section 4); the code change is left to a later kit note, for the reason section 4 gives |
| 6 | nit: E188-C's and E188-SCHED's FAIL word is implied, not stated | E188.md's dated note 1, section 3 (FAIL quoted as "not PASS"; E188-SCHED's vacuous PASS quoted so) |

## 2. THE REST RULE v2 ([`rb/rest_rule_e188_v2.sh`](rb/rest_rule_e188_v2.sh))

v1 (`rb/rest_rule_e188.sh`, E183's kit note 4's rule in E188's words) reads only session logs. In E186's and E188's form
(`build/eNNN/T<T0>/session.log`) the queue writes `T<T0>/queue.out` and the blocks write their own directories under
`build/claims-v3/aifoundry3/`, and in E183's form (`build/e183/session-t<T0>.log`) the queue writes `build/e183/queue-t<T0>.out`: none of
them writes the session log. So a session whose shell died mid-queue, with no "session end", was counted as ended at its last log line,
"smoke gate passed: queue starts", which can be the queue's length (up to about 90 minutes) before the card was last driven. It is reachable
only after an abnormal kill of the session's shell (k6's guard refuses while a session or queue of ours is live), and it under-reads the rest,
so v2 closes it.

**v2's one change:** a real block with no "session end" is counted as ended at the LATEST of (a) its last timestamped line and (b) its log's
last write, the log's final block only, both as v1, and (c), new, **the latest write of any regular file of the same run outside the dry
paths**, under `build/<run>/` (its session directories, queue outputs, block lists and config reads) and under its real block trees
`build/claims-v3/aifoundry3/<run>` and `build/claims-v3/aifoundry3/<run>-*`. Each file's write is read with `date -r`, as v1 reads a log's.
Dry paths are skipped: a "-dry" or "dry-t" anywhere in the path (E183's `session-dry-t<T0>.log` and `queue-dry-t<T0>.out`, E184's
`session-<arm>-dry-t<T0>.log`, every `T<T0>-dry/`); dry blocks write `build/claims-v3-dry/`, which is not read. **A block with its "session
end" is read exactly as v1 reads it.** Reading a cut session's end later only delays a launch; it never lets one start sooner than v1 would.
The 40-minute gate, its messages' form ("REFUSED: <m> minutes since E<run>'s ...", exit 3) and every log form v1 reads are unchanged.

## 3. Step 9 v2 and step 2 v2

- **Step 9 v2** ([`rb/s11_a3_session_e188_v2.sh`](rb/s11_a3_session_e188_v2.sh)) is step 9 v1 line for line but the rest lines it sends to
  the box (the rest rule v2) and its name in the runbook's log (`s11_a3_session_v2_e188`). Its T0 goes to `build/q141k/e188.T0` and
  `RB_OUT/e188-T0.txt` as v1's, so step 10 (`rb/s20_wait_e188.sh`) and step 11 (`rb/s22_collect_e188.sh`) read it unchanged.
- **Step 2 v2** ([`rb/s03_desk_e188_v2.sh`](rb/s03_desk_e188_v2.sh)) runs step 2 v1 unchanged inside it, in E183's step 2 v5 form, and then
  on the same HEAD: the two new lists (`SHA256SUMS-e188-a1` and `SHA256SUMS-e188-kit-note1`), each at its pinned count, its own pinned sha256
  and every entry OK, a gate (16); this note's three desk tests' logs as committed; HEAD unchanged. Step 2 v1 reports both lists as lists it
  does not pin, never as a gate; step 2 v2 pins them. Step 2 v2 is outside this note's list (a file cannot hold its own list's sha256): the
  go names its sha256 beside the list's.
- **The dry listing v2** ([`rb/list_steps_e188_v2.sh`](rb/list_steps_e188_v2.sh)) is v1's with steps 2 and 9 replaced.

**On E188's day, from this note on:** step 2 is `rb/s03_desk_e188_v2.sh` and step 9 is `rb/s11_a3_session_e188_v2.sh` (FULL yes, or PASSES
no in the fallback); every other step is KIT.md section 3's and `CARD-LANE-BRIEF.md`'s (its dated note 1 says the same). Never step 2 v1
alone and never step 9 v1 that day.

## 4. Faults 4 and 5: why the box files are not changed here

Every file the session runs on the box is pinned by `harness-e188.json` (77 files), which `check_e188.py`, both runners and the smoke gate
check at the session's start and in every block; the sync (step 5) copies exactly its files, the build's checks (step 6) read HARNESS OK 79
against it, and the session's device-command preflight audits the same files. Changing the smoke gate (fault 4) or the stop test in
`run_e188.py` (fault 5) means a new harness and with it a new check, preflight, sync, build count, dry pass and launch: the box side of the
kit made again, with its own desk tests and verifier (E183's kit note 4 did that, 32 files). Neither fault is a safety gap (verify-e188's own reading): every launch
waits on the live stops. So:

- **Fault 4** is answered by the reading A1-2 registers before any datum; a later kit note may make the smoke's kinds gate also fail on a STOP
  under the smoke's train part or a die reading at or above 70 C, with its own dated amendment before the data it governs.
- **Fault 5, a records line.** `run_e188._check_line`, the per-launch test of both runners and the watcher's, compares `board_w` with 65 and
  `temp_c.minshire[0]` with 70 by plain comparisons, so a non-finite reading is neither at nor above a stop: that one sample is passed over and
  the next (0.1 s later) is read; a later finite sample at or above a stop still trips, and a sampler that stops writing stops the train
  runner (its stale check). E188.md section 6's stop is read so: "at or above" a finite line. Treating a non-finite sample as a stop is left to
  the same later kit note. Beside it (not one of the verifier's faults; the same edge critic-q158 noted for E186's launch reading, carried):
  E182's train reduction, which E188 imports unchanged, admits a non-finite `board_w` sample into a launch's mean (`reduce_e182._telemetry`
  keeps any number), so such a sample would leave that train's estimate unreadable; a later kit note may drop non-finite samples, by a dated
  amendment before the data it governs.

## 5. Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** as KIT.md's block (the stock-take's INVENTORY.md as E188.md section 1 read it); pieces newer than it cited by commit: E188's
   registration (`878b6f63`) and kit (`726a6b64`), E183's kit note 4 (`24b9b99e`, its step 2 v5 form).
2. **Used**, each unchanged and by path: E188's kit (its rest rule v1, step 9 v1, step 2 v1, dry listing v1 and runbook desk test v1, each
   the base of its v2; the kit list's 106 files); E183's step 2 v5 (`tools/claims-v3/e183/rb/s03_desk_e183_v5.sh`, the form of step 2 v2);
   k6's runbook drivers (`tools/claims-v3/q141k-runbook/k6/rb_common.sh`, unchanged); the committed session logs of E182, E184, E185 and E186
   (v1's rest cases, unchanged). *Check against the same operation:* v1's twenty rest cases give the same verdict lines on v2.
3. **Not used:** anything of the card, the box, mordast, october-forecast-model or the private tier.
4. **Tiers:** every file here is public tier and cites public pieces only.
5. **Readiness:** this block is the note's. A verifier checks it.

## 6. Files

| file | what | builds on |
|---|---|---|
| `KIT.md.dated-note-1.md` | this note | |
| `CARD-LANE-BRIEF.md.dated-note-1.md` | the card lane's steps 2 and 9 from this note on; the go's lines | `CARD-LANE-BRIEF.md` |
| `rb/rest_rule_e188_v2.sh` | THE REST RULE v2 (section 2) | `rb/rest_rule_e188.sh` |
| `rb/s11_a3_session_e188_v2.sh` | step 9 v2 | `rb/s11_a3_session_e188.sh` |
| `rb/s03_desk_e188_v2.sh` | step 2 v2 (outside this note's list) | `rb/s03_desk_e188.sh`; E183's step 2 v5 |
| `rb/list_steps_e188_v2.sh` | the dry listing v2 | `rb/list_steps_e188.sh` |
| `rb/selftest_rest_e188_v2.sh`, `logs/selftest-rest-e188-v2.txt` | the rest rule v2's desk test and its log | `rb/selftest_rest_e188.sh` |
| `rb/selftest_rb_e188_v2.sh`, `logs/selftest-rb-e188-v2.txt` | the runbook desk test v2 and its log | `rb/selftest_rb_e188.sh` |
| `logs/dry-listing-e188-v2.txt` | the dry listing v2's log | |
| `SHA256SUMS-e188-kit-note1` | the sha256 of this note's files but step 2 v2 (10) | |

## 7. Labels, and what the desk cannot show

Every check here is a **desk check of code**; nothing is measured, **blind** or **held out**, and no E188 datum exists. The rest rule v2 has
run on stand-in trees and a stand-in box, never on aifoundry3's own tree: there it reads every cut block's run (one `date -r` a file), inside
step 9's 60 s read. Card time waits on the owner's go (`CARD-LANE-BRIEF.md`; on any shared day E183 runs first).

## Compute

On the Intel through the round's local slot, one job at a time, at nice 10: the rest rule's desk test (seconds), the runbook's desk test
(about 6 minutes, two g++-13 -O2 builds of the host on the stand-in box) and the dry listing. No mini, lab box or card was used.

SPDX-License-Identifier: Apache-2.0
