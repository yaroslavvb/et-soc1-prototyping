# E186's kit, dated note 1: the trains' pairing check over every train block, step 5 never beside a session of ours, the session scale's route in step 2 and the history check, and KIT.md's pairing sentence corrected (Q158; before any datum)

*Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only (Q158, lane `fix-e186`): no card was claimed, no device command was sent, no lab
box was reached, nothing was posted. **No E186 datum exists** (`git log --all` shows no `docs/reports/data/*e186*`). It answers the E186
verifier's faults 1, 3 and 4 and its nit 6 on the kit (`523002be`, git 08:57:34 PST); its fault 2, its ruling and its nit 5 are answered in
the registration's dated amendment A1 ([`E186.md.dated-amendment-A1.md`](E186.md.dated-amendment-A1.md), `17cf100f`, git 10:18:16 PST,
committed alone first). New files only: [`KIT.md`](KIT.md), [`KIT-BRIEF.md`](KIT-BRIEF.md) and every kit file stay as committed, and the
runbook's other steps are v1's. **No rule's statistic, threshold or words change, and no forecast, plan, cap, stop or device command
changes.** The one new reading, a train not paired reads NOT SCORED, is A1-2's, registered before this note.*

## Results first

- **Fault 1, the pairing.** KIT.md's sentence that the trains' reduction requires the host's own record on every process is not so (section
  1). [`pairing_e186.py`](pairing_e186.py) now reads the smoke gate's per-launch pairing over **every** train block at collection, with each
  tile's identity taken from its **registered bytes** (FNV-1a 64, the check of C's own hash), and [`score_e186_v2.py`](score_e186_v2.py)
  reads a train not paired as NOT SCORED (A1-2), with `score_e186.py` run unchanged behind it. **On E182's six committed train blocks the
  check pairs 5,712 of 5,712 launch records** (post hoc, a check of code), so the desk's hash equals the one the box's C-logging host writes.
  **SELFTEST-SCORE-E186-V2 12 of 12 PASS**: v2's scored file equals v1's word for word on M12's, M10's and the fail-closed worlds; each of
  five faults (a launch's kind off the schedule with its records consistent, a tile path, a C record's hash, a missing C record, no C log)
  makes its train NOT SCORED, leaves E186-C PASS and every other train's words as v1's.
- **Fault 3, step 5 beside a session of ours.** [`rb/s07_a3_sync_e186_v2.sh`](rb/s07_a3_sync_e186_v2.sh) reads the box first (k6's
  `ours_live` and `jobs_live`) and refuses (10) before step 5 v1 runs. The verifier's case HS, re-made: step 5 v1 syncs beside a session of
  ours (0, one rsync call); step 5 v2 refuses (10) with no rsync call; likewise beside a live runbook job.
- **Fault 4, the scale route outside step 2 and the history check.** [`rb/check_history_e186_v2.py`](rb/check_history_e186_v2.py) is v1's
  check, loaded by its path and run unchanged, with the route's six lists added to its perimeter, and
  [`rb/s03_desk_e186_v2.sh`](rb/s03_desk_e186_v2.sh) (step 2 v1 first, unchanged) holds the six at their counts and own bytes (209, 16, 9,
  68, 10, 160). The verifier's case (a committed one-byte edit of M10's `m10.json` with its list line rewritten): v1's check reads HISTORY OK,
  v2's refuses; step 2 v1 reads 0, step 2 v2 refuses (16); step 11 v2 stops before any scoring.
- **Fault 2:** no code change. The scorer's "s not read" reading (KIT.md section 4) is now registered by A1-1, with its power on the
  registration's own sessions (E186-M over the five trains reads the true model in 0.91-0.99 of sessions); KIT.md section 4's "a point for
  the verifier" is answered. A1-1b registers E186-LV's NOT SCORED in the fallback's branch.
- **Nit 6** (the brief's "about 93" card-minutes): the brief's dated note 1 ([`KIT-BRIEF.md.dated-note-1.md`](KIT-BRIEF.md.dated-note-1.md))
  quotes 89-99 beside it. **Nit 5** (the second candidate list's file stem): A1-3's records line.
- **The runbook as it now runs** (section 5): steps 2, 5 and 11 are v2's; every other step is v1's. The dry listing v2, both paths: every
  step exits 0, no call.

## 1. KIT.md's pairing sentence, corrected (fault 1)

KIT.md ("Results first", the check of C's limit, and section 4's E186-C bullet) says the six equal-C trains' pairing *rests on the host's
own record (`train_kind`, `train_values`, the C record's fnv), which the smoke's train gate reads against the schedule on H16 and the
trains' reduction requires on every process.* **The second half is not so:** E182's `reduce_train` (`tools/claims-v3/e182/reduce_e182.py`
lines 170-182, imported unchanged) requires 13 launches after the calibration, every record ok, and the orientation fields; it reads no
`train_kind`, no `train_values` and no C record. Only the smoke's train gate (`smoke_gate_e186.py` train(), lines 211-258) read the record
against the schedule, on H16's two smoke processes; and `score_e186.c_status` files any launch whose `train_kind` is not `F`, a missing one
included, under the second kind. **Read instead:** the six trains' pairing rests on the host's record, which E186-PAIR (A1-2) reads at
collection on every launch of every train block (section 2), and, for the operands themselves, on the train host's construction.

## 2. The pairing check, at collection (fault 1)

[`pairing_e186.py`](pairing_e186.py) reads, for every launch record of every train block the raw copy holds (p18610-p18619; the
calibration launch included), A1-2's five checks: (1) a process and launch of the plan's, once; (2) the registered schedule's kind for
that launch (the smoke gate's schedule, unchanged); (3) the train's type, where the record names one; (4) the scheduled kind's registered
tile in `train_values`; (5) a C record in the block's C log at the launch's start and end times whose fnv is the FNV-1a 64 of that kind's
registered tile bytes. Each tile is first checked against its registered sha256 (`e186_common.load_items`, which refuses a tile off the
merged list). The C log is the block's own (`c-log.jsonl` or `.gz`), else the collector's one copy (`ccheck/c-log-p<block>.jsonl.gz`).

[`score_e186_v2.py`](score_e186_v2.py) runs it on the raw copy, then runs `score_e186.py`'s `score` UNCHANGED with its per-train interval
wrapped for the one call: a train not paired reads NOT SCORED, with the pairing check named in its `why`, so every rule downstream reads it
as E186.md section 5.3 reads a train NOT SCORED. E186-TR-N is re-read with `score_e186`'s own lines, the trains not paired left out (with no
train left out it must equal v1's reading, or v2 refuses). E186-C is not touched. The scored file gains `rules > E186-PAIR` (PASS, or FAIL
with the trains), `pairing` (every train's counts and its first failures) and `scorer_v2` (the three files' sha256); results-e186.md gains a
pairing table. Note M1's reader reads v2's file as it read v1's (a train NOT SCORED is "not read" there).

[`collect_e186_v2.sh`](collect_e186_v2.sh) is `collect_e186.sh` line for line with its scorer changed to v2, and step 11 v2 runs it.
[`fake_card_e186_v2.py`](fake_card_e186_v2.py) gives the kit's synthetic sessions (fake_card_e186.py's, unchanged) the C log a card's block
holds, and the five faults the self-test reads.

**What it cannot show:** that the card's operands were the recorded tiles. For the six equal-C trains that rests on the train host itself:
E182's patch (`patch_host_e182.py` lines 87-91) sets the device pointers, the C log's tiles and both record fields from one variable, and
DESKTEST-HOST-E186 runs that source against the mock runtime (31 of 31 PASS, re-run by the verifier byte for byte). A per-launch tile hash
written by the host beside its record would close it, in a later kit.

## 3. Step 5 v2 (fault 3)

[`rb/s07_a3_sync_e186_v2.sh`](rb/s07_a3_sync_e186_v2.sh): the window and the last start (as v1), the probe, then ONE bounded read on
aifoundry3 (k6's prelude; `ours_live`, any `session_eNNN.sh` or `queue_eNNN.sh` of ours; `jobs_live`, a runbook job of any day still
running, step 6's build job among them). Either above 0 is `REFUSED` on the box and 10 at the desk, before anything is synced; else it
prints `NOT-BESIDE-OURS` and runs step 5 v1 unchanged. The read is pgrep and /proc only: no device command. The jobs_live refusal is this
note's addition beside the verifier's ours_live: a sync under step 6's live build would change the tree the build reads; no registered
order runs step 5 while a job runs (after TRAIN-HOST-INPUTS-DIFFER the build job has not started).

## 4. The session scale's route in step 2 and the history check (fault 4)

The float scale s (E186.md section 4.2) is read by `score_e178.session_scale`, which runs pool 8's predictor: `predict_pool8_a2.check_lists`
(the predictor's `SHA256SUMS` and `SHA256SUMS-a2`), `predict_pool8.check_inputs` (`tools/claims-v3/m10/POOL8-SHA256SUMS`, and M10's
`m10.json` and `m10-s7.json` against M10's `SHA256SUMS` and `SHA256SUMS-a2`), `predict_pool8.frozen` (M10's, M9's and M7's modules and
files, all named by those lists), and `score_e178.pool8_pred` (pool 8's frozen predictions for the card, against the freeze's
`SHA256SUMS`). None of these lists was in step 2 or in v1's history check, so a committed change to a listed file made together with its
list line passed both and was refused only by the predictor's own check, at scoring: s not read, the four ladder trains' SIZE words,
E186-GB and E186-GA NOT SCORED, after the card time.

- **The history check v2** ([`rb/check_history_e186_v2.py`](rb/check_history_e186_v2.py)) loads `rb/check_history_e186.py` by its path (so
  `python3 -I` keeps its meaning) and runs it unchanged, with its `LISTS` widened by the six lists (`POOL8-SHA256SUMS` 209 and the freeze's
  160 read from the lab's top; the predictor's 16 and 9; M10's 68 and 10 read beside them) and kit note 1's two (`SHA256SUMS-e186-a1`,
  `SHA256SUMS-e186-note1`). Each list and every file it names joins E186's paths: 501 named files outside the core directories, against
  v1's 55. It prints `HISTORY-V2: ...` (the lists and their counts) before v1's verdict line. Its m1 mode is v1's.
- **Step 2 v2** ([`rb/s03_desk_e186_v2.sh`](rb/s03_desk_e186_v2.sh)) runs step 2 v1 first, unchanged (and stops with its exit code if it is
  not 0), then the history check v2, the six lists each OK in full at its pinned count and its own committed sha256, A1's list (14) at its
  count and bytes, kit note 1's list at its count (40; it lists step 2 v2, so its bytes are held by the history check), and kit note 1's
  desk tests' logs as committed.
- **Step 11 v2** ([`rb/s22_collect_e186_v2.sh`](rb/s22_collect_e186_v2.sh)) runs the history check v2 after COPY-BACK EXACT and before any
  scoring: a change since step 2 stops the step (16), the raw copy kept, nothing scored.
- **A limit kept from v1:** outside the core directories only the files the lists name are read, so an untracked file there (one never
  committed) is not seen; an uncommitted edit of a named file is (the history check's status read).

## 5. The runbook as it now runs (KIT.md section 3's table, with kit note 1's rows)

| KIT.md box step | file (this note's in bold) |
|---|---|
| 1, the window | `rb/s02_window_e186.sh <day> <last start> <last end>` (v1) |
| 2, the desk check | **`rb/s03_desk_e186_v2.sh`** (step 2 v1 inside it, first) |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` |
| 3, the post, after the look | the card lane's |
| 5, the sync | **`rb/s07_a3_sync_e186_v2.sh`** (the read on the box first, then step 5 v1) |
| 6, the build and the box's checks | `rb/s08_a3_build_e186.sh start`, then `wait` while it says 17, or 14 with "no reading" (v1) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` |
| 8, the dry pass | `rb/s10_a3_dry_e186.sh start`, then `wait` (v1) |
| 9, the session | `rb/s11_a3_session_e186.sh FULL yes` (or `PASSES no`) (v1) |
| 10, the wait | `rb/s20_wait_e186.sh`, while it says 17 (v1) |
| 11, the release, then the collection | **`rb/s22_collect_e186_v2.sh`** (the history check v2, the collector v2 with the pairing check) |

The fallback runs as KIT.md section 3 says, with step 11 v2. **On the day, steps 2, 5 and 11 run only as v2;** their v1 files are never
run by hand (v2 runs v1's steps 2 and 5 inside it). The dry listing of both paths is [`rb/list_steps_e186_v2.sh`](rb/list_steps_e186_v2.sh).

## 6. The checks (desk checks of code; nothing measured)

| check | result | log |
|---|---|---|
| the pairing check on E182's committed trains, a fault in each copy, and the scorer v2 on synthetic sessions (v1 beside) | **SELFTEST-SCORE-E186-V2 12 of 12 PASS** | `logs/selftest-score-e186-v2.txt` |
| the history check v2 against v1 on the lab's own history (the verifier's case, pool 8's inputs, the freeze, M10's own list, a planted module, an uncommitted edit, the m1 mode) | **SELFTEST-HISTORY-E186-V2 9 of 9 PASS** | `logs/selftest-history-e186-v2.txt` |
| the runbook's v2 steps, fake ssh and rsync, a stand-in box (the dry listing; step 2 v2's refusals and pins; step 5 v2 beside a session or a job; step 11 v2's copy-back, history check and the scale route's change) | **SELFTEST-RB-E186-V2 13 of 13 PASS** | `logs/selftest-rb-e186-v2.txt` |
| the dry listing v2, both paths | 19 steps, 0 failing, no call | `logs/dry-listing-e186-v2.txt` |
| `dmcmd_audit`, kit note 1's runbook files with k6's library, and its desk files | GO, 0 send sites, 0 disallowed, in both sets: kit note 1 adds no device command (the runbook's 11 READ sites stay k6's reads through E128's guard, unchanged: `logs/dmcmd-audit-rb-e186.txt`) | `logs/dmcmd-audit-note1-e186.txt` |
| A1's power re-made | CHECK PASS (10:16:26-10:17:46 PST) | A1 |

## 7. Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sun 8 Nov 2026 at 10:11:55 PST. Public rows read: H07, H08, H09, H24, H27, H28. Newer
   pieces by commit: E182's data (`0f6a8c45`), E186's registration (`a41408d9`), note M1 (`3adb8bfe`), kit (`523002be`) and A1 (`17cf100f`).
2. **Used** (unchanged, imported, loaded, sourced or run; sha256 in [`SHA256SUMS-e186-note1`](SHA256SUMS-e186-note1)): the kit's scorer,
   items, synthetic sessions, reductions, note M1's reader, copy-back, C-session rule, runbook library and steps (`523002be`); k6's runbook
   library and steps; the check of C's `fnv64` (H08, H09); E182's items and committed train blocks (`0f6a8c45`; H27's descendant). *Check
   against the same operation:* the pairing check on E182's six committed trains pairs every launch record (5,712).
3. **Not used:** any card time; any rule or forecast not named above; the october-forecast-model's notes and reader beyond step 11's
   unchanged M1 gate.
4. **Tiers:** public tier; it cites public pieces only.
5. **Readiness:** a verifier checks this block against INVENTORY.md and the cited commits.

## 8. What the desk cannot show, and what remains

1. The pairing check has read E182's real train blocks and the kit's synthetic ones, never an E186 card's: its first real reading is the
   session's step 11.
2. The six equal-C trains' operands rest on the train host's construction (section 2).
3. Outside the core directories an untracked file is not read (section 4).
4. Note M2 (later versions' forecasts, and v4's on M12's set), additions only, with its own reader and gate, before the first datum; step 2
   v2 reads its list as v1 does (reported, never a gate).
5. A verifier of `17cf100f` and this note, then the readiness critic; card time waits on his go (`KIT-BRIEF.md` with its dated note 1).

## Labels

A1's readings are **registered** (`17cf100f`). The pairing check on E182's committed data is **post hoc**, a check of code deciding
nothing. Every desk test here is a check of code at the desk, not a measurement: nothing is **blind** or **held out**, and no E186 datum
exists.

## Compute

On the Intel through the round's local slot, one job at a time: A1's power and its re-make (about 80 s each, one core), the scorer v2's
self-test (about 50 s), the history check v2's desk test, the runbook's v2 desk test and the dry listing (minutes). No bench job, mini, lab
box or card was used. The desk tests wrote only under the round's scratch.

SPDX-License-Identifier: Apache-2.0
