# E183's kit, dated note 1: before any E183 datum, the reduction v2 reduces a stop block by E183.md section 5.1's process rule and refuses a process run on a wrong image or a block from before the session's T0; the collector v2 checks its frozen inputs at their pins first; step 2 v2 pins a third list of 46 (this note's files and the 29 shared files the runbook, the collector and the desk tests call); step 11 v2; the card lane's order with E185 and two record lines (Q155; new files only)

*Sat 7 Nov 2026 (week 45), on the Intel, desk only (Q155, lane `fix-e183`; the lane began 22:31 PST, and this note was first written
between 23:04 and 23:07 PST by the clock; its commit's own time is git's). No card was claimed, no device command was sent, no lab box or mini was reached,
and nothing was posted. It sits beside [KIT.md](KIT.md) (the kit, `cc597bf2`), which stays as committed, as do the registration
([E183.md](E183.md), `c98a7287`) and every file of both hash lists (20 and 46 OK). It answers the adversarial verifier of both commits
(`verify-e183`, Sat 7 Nov 2026 21:54-22:28 PST: **holds with fixes**, 4 minor faults and 6 nits, no critical or major one). Every fault is
fixed here or in [E183.md.dated-note-1.md](E183.md.dated-note-1.md), committed with this note, before any E183 datum: `git log --all` shows
no `docs/reports/data/*e183*`. **No box file changes:** `harness-e183.json` (80 files, 40 build inputs, the 38-file tree) is unchanged, and so
is everything step 5 sends and the session runs. No forecast, rule, threshold, registered power figure, plan, cap or stop changes. What it
adds is desk files: the reduction v2 and its self-test, the collector v2, step 2 v2 and step 11 v2, the dry listing v2, the runbook v2 desk
test, the checks behind E183.md's note 1, their logs and a hash list.*

## Results first

- **The reduction v2** ([`reduce_e183_v2.py`](reduce_e183_v2.py); v1 stays as committed) makes three changes and keeps everything else of v1
  line for line. **(1)** A block whose block.json reads `stop` is reduced by section 5.1's process rule: the process stop.json names gives
  no value, the ones before it keep theirs, and a stop block without its stop.json is set aside. **(2)** A process whose launch ran an image
  other than its kind's gives no value, by `check_e183.py`'s own test. **(3)** `--t0` is required, and a block whose `t0_ms` is missing or
  earlier than the session's T0 is set aside as not this session's. It also copies the box's post-block check (check.json) into each block
  as `box_check`, reported.
- **Its self-test, SELFTEST-SCORE-E183-V2 23 of 23 PASS** ([`logs/selftest-score-e183-v2.txt`](logs/selftest-score-e183-v2.txt), 108 s),
  through [`selftest_score_e183_v2.py`](selftest_score_e183_v2.py) and [`fake_card_e183_v2.py`](fake_card_e183_v2.py):
  - A1-A2 on E180's committed data;
  - **R1-R12:** v1's twelve synthetic sessions, each scored through v1's path and through v2's, give **equal scored files**, so v1's verdicts
    (14 of 14, `logs/selftest-score-e183.txt`) stand under v2;
  - **S1:** a stop in T5's process 150. v1 sets T5 aside and E183-HT reads NOT SCORED. v2 keeps 150 of 202 processes (75 units, +0.0092 W)
    and reads HT POSITIVE, the verifier's own case. S2-S4 cover a stop after a 13th launch, a stop at a closing anchor, and no stop.json;
  - **I1:** a wrong image. v1 used it, 52 of 52; v2 gives 51 of 52;
  - **T1-T3:** a stale block, a block with no t0_ms, and no `--t0`;
  - **N1:** TR-N's pool, as registered.
- **The collector v2** ([`collect_e183_v2.sh`](collect_e183_v2.sh)) first checks the three hash lists at their pinned counts: the
  registration 20, the kit 46 and this note's 46. Any miss stops it before a number is made. It then runs the reduction v2 with the
  session's T0 and the scorer, which is unchanged. **Step 11 v2** ([`rb/s22_collect_e183_v2.sh`](rb/s22_collect_e183_v2.sh)) is v1's with
  the collector v2.
- **Step 2 v2** ([`rb/s03_desk_e183_v2.sh`](rb/s03_desk_e183_v2.sh)) checks three lists at pinned counts with no override: 20, 46 and 46
  ([`SHA256SUMS-e183-note1`](SHA256SUMS-e183-note1)). It also checks this note's two desk tests' logs. Note 1's list pins **the 29 files
  outside E183's directory** that the runbook, the collector and the desk tests call, source, read or compile, which no E183 list pinned
  before:
  - k6's `rb_common.sh`, `s05_look_k6.sh` and `s09_a3_reads_k6.sh`;
  - v3.1's `rb_run.py` and `nopath_q142s.py`;
  - E180's `sync_paths_e180.py` and `check_elf_e180.py`; E178's `scrub_tree_e178.py`; E182's `e182_stats.py`;
  - E184's six desk stubs;
  - E180's `scored-e180.json`, its kernel listing, and its six passes' telemetry and launch records.
  
  Each is at the sha256 every other committed list names it with ([`logs/reruns-note1-e183.txt`](logs/reruns-note1-e183.txt)).
- **The runbook v2 desk test, SELFTEST-RB-E183-V2 8 of 8 PASS** ([`logs/selftest-rb-e183-v2.txt`](logs/selftest-rb-e183-v2.txt), 25 s,
  with a fake ssh and rsync):
  - the dry listing v2;
  - step 2 v2 without a window (10), at its pins (0), and with note 1's list one line short (v2 16, v1 0);
  - **C1: step 11 v2 runs the REAL collector v2 end to end on a synthetic session placed on the stand-in box.** That covers the exact
    copy-back (52 files), the pins, the reduction v2 with T0 (T5's block, left from an earlier session, set aside), the scorer (MECH
    RESULT), the desk-path gate and the login scrub;
  - a second run into the same raw tree is refused (10);
  - a registration file off its pin stops the collector v2 (1) with no reduced file.
- **dmcmd_audit:** the runbook as note 1 runs it reads GO with 11 send sites, every one E128's guard, the same as v1's log line for line;
  this note's desk files read GO with 0 sites ([`logs/dmcmd-audit-note1-e183.txt`](logs/dmcmd-audit-note1-e183.txt)). The dry listing v2
  shows 12 steps, 0 failing, the look before the post ([`logs/dry-listing-e183-v2.txt`](logs/dry-listing-e183-v2.txt)).

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** KIT.md's block (INVENTORY.md read about 20:20 PST; rows L06, L11, L20, H21, H24, H27, H28, P11, P12) and E183.md's note 1
   (rows L20, P11 and P12 re-read about 22:44 PST). The row ids are opaque pointers into a private inventory. Pieces newer than it are
   cited by commit: E183's registration (`c98a7287`) and kit (`cc597bf2`); E182's kit notes 2-4 (`22da6a7b`, `e0d31903`, `6b2d2ae6`), whose
   step 2 pinned its lists' counts and whose notes pinned the unchanged files their steps call; E185's kit note 1 (`ad2ed873`).
2. **Used** (each unchanged, called, sourced or imported by path; sha256 in [`SHA256SUMS-e183-note1`](SHA256SUMS-e183-note1) or in the
   kit's or the registration's list):
   - **E183's kit v1:** `reduce_e183.py` (the form of v2, line for line but the three changes), `fake_card_e183.py` (imported by the fake
     v2, unchanged), `check_e183.py` (its `train_faults` test, and its `block` check run by the fake v2), `score_e183.py` (unchanged, the
     scorer v2 reads under), `collect_e183.sh`, `rb/s03_desk_e183.sh`, `rb/s22_collect_e183.sh`, `rb/list_steps_e183.sh` and
     `rb/selftest_rb_e183.sh` (the forms of their v2s and its stand-ins). *Check against the same operation:* v1's twelve synthetic
     sessions score byte for byte the same through v1 and v2 (R1-R12), and the v1 runbook's 11 send sites are unchanged.
   - **lib.sh's block_begin and block_end** (`tools/claims-v3/lib.sh`, a box file in the harness): block_end writes `t0_ms` and `t1_ms`
     on the box's clock, and block_begin skips a block whose block.json exists ("already done"). Change 3 rests on the first; the record
     line of section 3 rests on the second.
   - **The runner's stop record** (`run_e183.py`, a box file): stop.json's `where` names "train T process k (orientation)" for a stop
     before or during a process, and the anchor's cfg for a stop at an anchor. Change 1 reads it as v1's rule did.
   - **E182's notes 2-4:** the form of a step 2 with every list at a pinned count, and of a note list pinning the unchanged files its
     steps call.
   - **The 29 shared files** of section 5, unchanged.
3. **Not used:** any box change; E180's and E182's scorers beyond `e182_stats.py`; any E183 datum (none exists).
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

KIT.md's box steps are named by their numbers there: 1 the window, 2 the desk check, 3 the post, 4 the look, 5 the sync, 6 the build, 7
the reads, 8 the dry pass, 9 the session, 10 the wait, 11 the collection. The files are `rb/s02`, `s03`, k6's `s05`, `s07`, `s08`, k6's
`s09`, `s10`, `s11`, `s20` and `s22`.

## The verifier's ten findings, and where each is fixed

| # | the finding | fixed by | tested by |
|---|---|---|---|
| 1, minor | a live stop sets aside the whole train block, against E183.md section 5.1's process rule | the reduction v2, change 1; E183.md's note 1, section 4 | S1-S4 |
| 2, minor | a 52-process train's half-width quoted as the z value, +-0.0098 W | E183.md's note 1, section 1: about 0.0103 W (t); TR-H's denominator kept, its offset named | `note1_checks_e183.py` part 2 |
| 3, minor | shared desk files the runbook and its tests call are in no E183 list; step 2 checks two lists; the collector checks none | note 1's list (46: 17 new files and 29 shared ones), step 2 v2 at its pins, the collector v2's pins | P1, P2, C1, C3; the re-runs |
| 4, minor, cross-kit | E185's rest gate cannot see E183's sessions | E183.md's note 1, section 5: on a day shared with E185, E185 first, always; E185's kit note 1 (`ad2ed873`) reads E183's log | E185's own R4 |
| 5, nit | two power figures rounded up | E183.md's note 1, section 2: those two and four more, six in all, read from `power-e183.json` | `note1_checks_e183.py` part 1 |
| 6, nit | the reduction never checks a launch's image | the reduction v2, change 2; E183.md's note 1, section 4 | I1 |
| 7, nit | TR-N pools a NOT SCORED train's quads, where KIT.md says "every scored train's" | KIT.md's word corrected here (section 4); the code and E183.md section 5.2 say "every train's" | N1 |
| 8, nit | block data are not T0-named; a stale block would be skipped and scored | the reduction v2, change 3, with the collector v2 passing T0; the record line of section 3 | T1-T3, C1 |
| 9, nit | rows L20, P11 and P12 read but not placed | E183.md's note 1, section 3 | - |
| 10, nit | T5's sampler runs 300 s past its 1,228 s estimate | the record line of section 7; no code change | - |

## 1. A stop block, by E183.md section 5.1's process rule (the verifier's fault 1)

**The fault**, checked here. `block_e183.sh` writes block.json `stop` when the runner exits 5, and `reduce_e183.py`'s `reduce_all` sets aside
every block that is not `ok` or `partial`. So v1 never reached its own rule ("a stop fired during it", from stop.json), and a stop at T5's
150th process lost its 150 good processes with it. KIT.md called its block rule a reading "where E183.md leaves a choice". Section 5.1
leaves none: it names the process.

**The fix, reduction v2, change 1.** `stop` joins `ok` and `partial` as a status that is reduced.
- The process stop.json names gives no value. If its launches were cut, it fails on "<n> launches" first; if all 13 were recorded, it
  reads "a stop fired during it".
- The processes after it never ran: "0 launches".
- A stop at an anchor names no process, so every process keeps its value, and that side's anchor pair reads None.
- A stop block without its stop.json is set aside, since its process cannot be named.
- The block's post-block check (check.json) is copied in as `box_check`, since its own word is no longer in the status.
- A block that reads `fail` or `others` is still set aside whole, as KIT.md registered. Section 5.1 names no process for those.

**Desk cases** (the verifier's V1 and V1b are S1): **S1**, **S2**, **S3** and **S4**, as in "Results first". E183.md section 7's "A stop
ends the session" is unchanged: the queue stops, and later blocks are not run.

## 2. The image (the verifier's nit 6)

The reduction v2 gives no value to a process whose launch record's `train_operands` does not end with its kind's image. The test is
`check_e183.py`'s `train_faults`, word for word, and it sits after the kind and orientation test. The box's post-block check already found
such a process, but it only marked the block `partial`, and a partial block was reduced, so v1 used the process. **I1** runs that check in
the fake v2 (`--box-check`), so the block reads `partial` with "process 3: a launch's image is not its kind's", and v2 gives process 3 no
value.

## 3. The session's T0 (the verifier's nit 8), and a record line for a second session

The reduction v2 requires `--t0`. The collector v2 passes `E183_T0`, the T0 step 9 recorded on the box's clock, which is the clock
block_end's `t0_ms` uses. A block whose `t0_ms` is missing, or earlier than T0, is set aside as not this session's. A session's first
train block starts after its harness check, preflight, config read, stop-path test and smoke, so a block of this session never precedes
its T0. **C1** puts a stale T5 block on the stand-in box, and step 11 v2 sets it aside and scores the other five.

**A line for the card lane (a record line; no action on the first session):** there is no E183 block on aifoundry3 before the first
session, because the dry pass writes under `build/claims-v3-dry/`. Before any second E183 session there (a re-run, which needs its own
dated amendment first), move `build/claims-v3/aifoundry3/e183` aside on the box. lib.sh's block_begin skips a block whose block.json
exists, so a stale block would not be measured again. The reduction v2 keeps it out of the scores either way.

## 4. TR-N's pool, KIT.md's words corrected (the verifier's nit 7)

KIT.md's "The scorer's readings" says "TR-N's pool: every scored train's quads". **Read: every reduced train's quads,** a NOT SCORED
train's among them, and not a set-aside block's. That is E183.md section 5.2's registered "every train's quads", and it is what
`score_e183.py`'s `tr_n` does, unchanged. TR-N reads the method's noise, and a train with too few units to score still gives valid quads.
**N1** shows it: T3 is cut to 6 units, and the scorer's pooled sd is the pool of all six trains' 1,266 quads (T3's 36 among them), not the
five scored trains'. TR-H stays the median over the scored trains, as registered.

## 5. The shared files pinned, and the collector's pins (the verifier's fault 3)

KIT.md's Builds on (2) said each used file's sha256 is "in harness-e183.json or SHA256SUMS-e183-kit". The 29 files of "Results first" were
in neither, step 2 checked only E183's two lists, and the scorer and collector never called `check_frozen`. Nothing was off its pin.
**From this note on, KIT.md's Builds on (2) reads "or SHA256SUMS-e183-note1".**
- [`SHA256SUMS-e183-note1`](SHA256SUMS-e183-note1) holds 46 entries: this note's 17 other new files and the 29 shared ones. Each shared
  file is at the sha256 every other committed list (or the registration's `inputs_sha256`) names it with. Each is touched by one commit
  ([`logs/reruns-note1-e183.txt`](logs/reruns-note1-e183.txt)).
- **Step 2 v2** checks it, with the registration's 20 and the kit's 46, each OK in full and at its pin, with no override. **P2:** the list
  one line short is refused by v2 (16, "SHA256SUMS-e183-note1(45 OK of 45; pinned 46)") and passed by v1.
- **The collector v2** checks the same three lists before it reduces anything, because step 11 runs hours after step 2. **C3:** one
  registration file changed, and it stops (1) with no reduced file.

## 6. The order with E185 (the verifier's fault 4)

The card lane's line, from E183.md's note 1 section 5: **on a day E183 shares with E185, E185 runs first.** E183's look, sync, build and dry
pass start only after E185's step-11 copy-back, and E183 never starts before E185 that day. That is E185.md section 8's own order. On a day
without E185, KIT.md's "The order on aifoundry3" stands. E185's kit note 1 (`ad2ed873`, 22:45:02 PST) made E185's rest gate read E183's
log form (`build/e18x/session-*.log`, both end forms), so its gate also holds in either order; this line does not depend on it.

## 7. T5's sampler margin (the verifier's nit 10): a record line

T5's block gives its sampler the runner's estimate plus 300 s: 1,227.9 + 300 s. A mean process time up to about 7.3 s fits; the plan's is
5.8 s, from E180's measured overheads (0.29 s median, 0.49 s at most). Slower processes would stop the sampler before the block ends. The
runner then exits 4, the block reads `fail`, and it is set aside whole, as KIT.md registered. **No code change and no action on the day.** If
T5's block reads "the sampler stopped writing", the data README names this margin, with the process times from the copied run.log, which
logs every 8th process's time and every process that came back short or non-zero.

## 8. The runbook as it now runs (KIT.md's box steps)

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window (FIRST) | `rb/s02_window_e183.sh` | no |
| 2, the desk check | **`rb/s03_desk_e183_v2.sh`** | v2: three lists at 20, 46 and 46; this note's two logs |
| 4, the look (BEFORE the post) | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no |
| 3, the post | the card lane's, under the post's lock | no |
| 5, the sync | `rb/s07_a3_sync_e183.sh` | no |
| 6, the train host's build | `rb/s08_a3_build_e183.sh start`, then `wait` while it says 17 | no |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the dry pass | `rb/s10_a3_dry_e183.sh start`, then `wait` | no |
| 9, the session | `rb/s11_a3_session_e183.sh FULL` (or `SHORT`) | no |
| 10, the wait | `rb/s20_wait_e183.sh`, again while it says 17 | no |
| 11, the release, then the collection | **`rb/s22_collect_e183_v2.sh`** | v2: the collector v2 |

v1's steps 2 and 11 are not run on the card day. The dry listing of this table is
[`rb/list_steps_e183_v2.sh`](rb/list_steps_e183_v2.sh). After step 11 the data directory is
`docs/reports/data/<day>-e183-vector-add-r2-aifoundry3/`, and its README names the reduction v2 and the session's T0.

## 9. The checks

| check | result | log |
|---|---|---|
| the reduction v2's self-test (sections 1-4) | **SELFTEST-SCORE-E183-V2 23 of 23 PASS**, 108 s | `logs/selftest-score-e183-v2.txt` |
| the runbook v2 desk test (steps 2 and 11 v2, the collector v2) | **SELFTEST-RB-E183-V2 8 of 8 PASS**, 25 s | `logs/selftest-rb-e183-v2.txt` |
| the dry listing v2 | 12 steps, 0 failing, the look before the post, no call | `logs/dry-listing-e183-v2.txt` |
| dmcmd_audit: the runbook as it now runs; this note's desk files | GO, 11 sites, every one READ (v1's, line for line); GO, 0 sites | `logs/dmcmd-audit-note1-e183.txt` |
| the re-runs: both lists, the harness, the shared files' pins, the tree, the data | 20 of 20 and 46 of 46; CHECK PASS; VERIFY OK; HARNESS OK 80; BUILD INPUTS OK 40; 29 shared files at their pins; 0 tracked files modified; no E183 datum | `logs/reruns-note1-e183.txt` |
| E183.md's note 1, sections 1-2 | six quoted figures read again; the t half-widths | `logs/note1-checks-e183.txt` |

Not re-run, because their files are unchanged and pinned by the kit's list: the host's desk test, the scorer's v1 self-test, the loop
compare's, the Intel dry pass and v1's runbook test (the verifier re-ran each at `cc597bf2`). R1-R12 re-run v1's twelve synthetic sessions
through v1's code.

## 10. Labels

- **Registered:** every forecast, rule, threshold, power figure, plan, cap and stop the scorer reads, as E183.md registers them at
  `c98a7287`, with E183.md's note 1. That includes E183.md's note 1 section 4's two added conditions, its order line, and this note's
  readings: the stop block by section 5.1, the image, the T0, TR-N's pool, and the record lines of sections 3 and 7. All are registered
  before any datum.
- **Desk checks of code, not measurements:** every test result here.
- **Post hoc:** E180's process overheads in section 7 (its committed run logs, as KIT.md cites them).
- Nothing here is **blind** or **held out**, and no E183 datum exists.

## 11. Open items (for the verifier, the readiness critic and the records)

1. A verifier of this note and E183.md's note 1, then a readiness critic. Card time only on his go, with fresh network approvals.
2. **The train host's first compile is on the box** (step 6), as before: one re-run, then SKIP.
3. **The collector v2 has run end to end on a synthetic session's raw tree** through the real step 11 v2 (C1). It has not run on a real
   session's raw tree; its first such run is the card day's step 11.
4. The loop compare needs the box's objdump, or it reads UNREAD (reported). Card 1 is not kitted. E180's recorded nits 7-9 stand for the
   box files E183 uses as E180 did (KIT.md open item 7).
5. **For the records round:** E183's registration, kit and both notes, with their labels; the corrected quotes (the half-widths about
   0.0103 / 0.0205 W and 0.0051 / 0.0101 W; NEITHER 0.90 / 0.86; HT POSITIVE under OFM 0.35 / 0.12 and under no difference 0.02 / 0.02);
   and this table of findings.

| file | what |
|---|---|
| `KIT.md.dated-note-1.md`, `E183.md.dated-note-1.md` | the two notes |
| `reduce_e183_v2.py`, `collect_e183_v2.sh` | the reduction v2, the collector v2 |
| `selftest_score_e183_v2.py`, `fake_card_e183_v2.py` | the reduction v2's self-test and its synthetic sessions |
| `note1_checks_e183.py` | E183.md's note 1, sections 1-2 |
| `rb/s03_desk_e183_v2.sh`, `rb/s22_collect_e183_v2.sh`, `rb/list_steps_e183_v2.sh`, `rb/selftest_rb_e183_v2.sh` | step 2 v2, step 11 v2, the dry listing v2, the runbook v2 desk test |
| `logs/selftest-score-e183-v2.txt`, `logs/selftest-rb-e183-v2.txt`, `logs/dry-listing-e183-v2.txt`, `logs/dmcmd-audit-note1-e183.txt`, `logs/reruns-note1-e183.txt`, `logs/note1-checks-e183.txt` | the checks above |
| `SHA256SUMS-e183-note1` | 46 entries: the 17 files above and the 29 shared files |

**Compute:** on the Intel through the round's slot, one job at a time, at nice 10. The self-test took 108 s, the runbook v2 desk test 25 s,
and the checks script under a minute; the listing, the audits and the re-runs took seconds. No bench job, mini, lab box or card was
used. The tests wrote only under the round's scratch.

SPDX-License-Identifier: Apache-2.0
