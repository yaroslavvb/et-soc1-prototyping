# E184's kit, dated note 3 (Sat 7 Nov 2026, week 45, written from 21:08 PST by the clock): dated amendment A4's reducer before any datum - reduce v4 tests the config reads' keys, not their truthiness; the collector v3 and step 11 v3 run it; step 2 v3 pins eight lists and refuses without the window; and two records of kit note 2 corrected

*Written on the Intel in Q155 (lane `fix-q154k`), desk only: no card claimed, no device command sent, no lab box, mini or network reached
(every ssh and rsync of the tests below is a stand-in that serves a local directory), nothing posted or deployed. New files only: the kit
(`65f844be`), kit notes 1 (`eab0c70e`) and 2 (`571511d0`) and every file their hash lists name stay as committed (registration 11 of 11, kit
44 of 44, A2 6 of 6, kit note 1 45 of 45, A3 3 of 3, kit note 2 20 of 20 OK). It follows dated amendment A4
([`E184.md.dated-note-A4.md`](E184.md.dated-note-A4.md), committed alone just before it), whose rule its code implements. It answers critic-q154's
first and third nits and the adversarial verifier of A3 and kit note 2 (`verify-q154k`, 19:55-20:29 PST today: holds with fixes, 2 minor and 3
nits), its fault 2 and its nits 3 and 4. **No box file changes:** the harness's 59 files (`harness-e184-v2.json`) are kit note 1's, byte for
byte. No E184 datum exists: `git log --all` shows no `docs/reports/data/*e184*`.*

## Results first

| what was wrong | the fix | file | its test |
|---|---|---|---|
| the session gate took any JSON object as a read and checked the two edges only when both were non-empty (A4-1) | A4's gate: a read lacking `tdp_w`, `temp_threshold_c` or `minion_mhz`, or holding a null among them, is MISSING and replaced by step 7's read; a complete read not as registered is MOVED; each edge is checked on its own; a step-7 file is a read only when complete; a value matches a registered number only when it is a JSON number | `reduce_e184_v4.py` | **SELFTEST-REDUCE-E184-V4 37 of 37** (`logs/selftest-reduce-e184-v4.txt`): K1-K20 with the critic's partial-read case (K1) and empty-`{}` case (K3), the verifier's H4, H5, H6, H15 and H16 (K4, K5, K6, K15, K16), and K4 end to end (KF); A3-3's twelve cases and five whole sessions read as under v3 |
| step 11 v2's collector runs reduce v3 | `collect_e184_v3.sh` runs reduce v4 (`reduced-e184{s,b}-v4.json`) and score v3, unchanged; step 11 v3 calls it | `collect_e184_v3.sh`, `rb/s22_collect_e184_v3.sh` | runbook desk test v3 **C2p** (a partial end read, replaced: holds, LINEAR), **C2e** (start `{}`, end MOVED: every rule NOT SCORED), **C2ev** (the same through step 11 v2: the arm scored, the fault) |
| E184's step 2 does not itself refuse without the window (critic-q154's nit 3) | step 2 v3 refuses (10) unless the window was written today in its RB_OUT, as E182's step 2 does, and pins eight lists: 11, 44, 6, 45, 3, 20, A4's **1** and this note's **18** | `rb/s03_desk_e184_v3.sh` | desk test v3 **K** (no window: 10, no call); the dry listing v3; step 2 v3 run for real after this commit |
| kit note 2's "With no level left out, every number is v2's" (the verifier's nit 3) | corrected in words, section 6 | (this note) | the verifier's case C1 |
| step 10b overwrites `$RB_OUT/config-B-reads.json` (its nit 4) | stated in words, section 6 | (this note) | |

**Everything else reads as before.** On five whole synthetic sessions (V1 and B1, V1 with its end read moved to 65 W, B1 with its end TDP 41 W,
V1 with a failed smoke gate and a stale earlier session) reduce v4's output is v3's key for key, but for the reducer's and the gate's names,
the two new status fields and the reasons' words (as many reasons, the same gate). A3-3's twelve gate cases (G0-G11) read the same. The
runbook desk test v3 passes v2's 34 cases with the v3 steps, and four new ones: **SELFTEST-RB-E184-V3 PASS, 38 of 38**.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sat 7 Nov 2026 at 20:47 PST (rows H27 and H28, A4's block). The ids are opaque pointers
   into a private inventory. Newer pieces are cited by commit.
2. **Used** (each unchanged, called, imported or sourced by path; their sha256 in kit note 2's or kit note 1's list):
   - **Kit note 2's files** (`571511d0`): `reduce_e184_v3.py` (v4 imports its windows, its `.time` reader and its ISO printer, and runs
     v2's reduction through it unchanged), `score_e184_v3.py` (called unchanged), `collect_e184_v2.sh`, `rb/s03_desk_e184_v2.sh`,
     `rb/s22_collect_e184_v2.sh`, `rb/list_steps_e184_v2.sh`, `rb/selftest_rb_e184_v2.sh`, `audit_rb_e184_v2.sh`, `audit_desk_e184_v3.sh` and
     `interp_check_e184_v3.sh`, each v-next file being its predecessor with the stated changes (counted, exact replacements; each file's
     header lists them). *Check:* the v2 runbook cases re-run under the v3 steps (34 of 34 within the 38), and v3's own gate cases re-run under
     v4 (G0-G11).
   - **fake_card_e184_v2.py** (kit note 1), unchanged: every synthetic session.
   - **k6's runbook drivers** through `rb/rb_e184.sh`, unchanged.
   - **A4** for the rule; **A3** for the windows and the record.
3. **Not used:** a session that retries its config reads (A4 says why).
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this note.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. The reducer v4 (A4)

`reduce_e184_v4.py` calls v2's reduction unchanged (the pass gate, A2-5) and replaces v3's session gate by A4's. Each edge's file is read
once and named: `complete`, `failed (no value for <keys>)`, `absent`, `empty`, `no JSON object` or `dry` (`session.config_status`). A complete
read is the session's own and is checked on its own; anything else with its attempt recorded is MISSING and replaced as A3-3 says, by a
complete step-7 read only (each step-7 file's status is in `session.step7_reads`); a dry read is never replaced. Arm B's "the same TDP and
threshold at both ends" is checked once both edges hold a read, and only between numbers. The departure's words name A3 and A4. Every other
field of the reduced file is v3's.

## 2. The collector v3

`collect_e184_v3.sh` is v2's collector with `reduce_e184_v4.py` in place of v3, writing `reduced-e184s-v4.json` and `reduced-e184b-v4.json`,
and `score_e184_v3.py` unchanged (`scored-e184-v3.json` and `.md`, the success line "scored-e184-v3.md written"). Each arm's T0 is kept as in
v2. A collection by v2 of the same day can sit beside it; the scored files are v3's either way, and the data verifier reads which reducer
wrote them in `reduced-*.json` > `reducer`.

## 3. The runbook as it now runs (it governs E184's steps)

Kit note 2 section 3's table, with steps 2 and 11 in v3. Every other step, file and rule is kit note 2's.

| KIT.md box step | file |
|---|---|
| 1, his go and the window | `rb/s02_window_e184.sh <day> <last start> <last end>` (one `RB_OUT` per arm), **first** |
| 2, the desk check | **`rb/s03_desk_e184_v3.sh`**: kit note 2's checks with **eight** hash lists and their counts pinned (11, 44, 6, 45, 3, 20, 1 and 18); it refuses (10) unless step 1 wrote this RB_OUT's window today |
| 4, look first | `q141k-runbook/k6/s05_look_k6.sh aifoundry3` or `aifoundry1` (k6's, unchanged) |
| 3, then the day's one post | the card lane's, under the post's lock, only after the look reads the card free |
| 5, the sync | `rb/s07_sync_e184.sh S` or `B` |
| 6, the build and the box checks | `rb/s08_build_e184.sh S|B start`, then `... wait` (repeat while 17) |
| 7, the reads | `rb/s09_reads_e184_v2.sh S|B` |
| 8, the V3_DRY pass on the box | `rb/s10_dry_e184.sh S|B start`, then `... wait` |
| 9, the session | `rb/s11_session_e184.sh S|B` |
| 10, the wait | `rb/s20_wait_e184.sh S|B` (repeat while 17) |
| 10b, step 7 again | `rb/s09_reads_e184_v2.sh S|B after`, right after step 10 exits 0 and before the release (kit note 2's rule, unchanged) |
| 11, release, then collect | the post's release; then **`rb/s22_collect_e184_v3.sh S|B`**: kit note 2's copy-back, then **`collect_e184_v3.sh`**, which reduces with **`reduce_e184_v4.py`** (A3-3 with A4) and scores with `score_e184_v3.py`; then the data directory `docs/reports/data/<day>-e184-sensor-validation/` and a data verifier |

**What the card lane and the data verifier read.** `scored-e184-v3.md` and `.json` govern, written from `reduced-e184{s,b}-v4.json`. A session
gate that holds with a departure (A3-3 with A4) is named in the data README with the step-7 read it used and the replaced read's status (for
example "failed (no value for tdp_w)"). Steps 2 v1-v2 and 11 v1-v2 are not run on the card day. If step 11 v2 was run by mistake, step 11 v3
can be run after it on the same copy: it reduces again with v4 and writes the scored files again.

## 4. The reducer's self-test v4

`selftest_reduce_e184_v4.py` (its header lists the cases): five whole sessions (Q1-Q5) and A3-3's twelve gate cases (G0-G11) read as under
v3; A4's cases K1-K20 read as A4 says and v3 differently where A4-1 says it was wrong; KF and K1F run the reducer and score v3 end to end.
37 of 37 PASS under `/usr/bin/python3` 3.9.6 (about 2 minutes, one core). **The interpreter check v4** (`interp_check_e184_v4.sh`) runs v3's
sessions with arm S's start read made partial and a step-7 read before T0, besides v3's emptied end read, so A4's key test and two
replacements run under both interpreters: **INTERP-E184-V4 SAME** (3.9 and 3.13).

## 5. The checks (each run by this lane; the logs are this commit's)

| check | result | log |
|---|---|---|
| the reducer's self-test v4 | **SELFTEST-REDUCE-E184-V4 37 of 37 PASS** | `logs/selftest-reduce-e184-v4.txt` |
| the interpreter check v4 | **INTERP-E184-V4 SAME** (3.9 and 3.13, two departures each) | `logs/interp-check-e184-v4.txt` |
| the runbook's desk test v3 | **SELFTEST-RB-E184-V3 PASS, 38 of 38** (v2's 34 with the v3 steps, K, C2p, C2e, C2ev) | `logs/selftest-rb-e184-v3.txt` |
| the runbook's dry listing v3 | 0 exited non-zero, no ssh or rsync; step 2 v3 listed once, step 11 v3 once an arm | `logs/dry-listing-e184-v3.txt` |
| dmcmd_audit | runbook v3 GO, 23 sites (the same 23 as kit note 2's audit: the four v3 files send nothing); desk v4 GO, 0 sites | `logs/dmcmd-audit-{rb-v3,desk-v4}.txt` |
| the hash lists, the harness, no E184 data | the eight lists at step 2 v3's pins (A4's and this note's checked after they were made); the box list CHECK PASS, 59 files; no committed E184 file changed; no commit names `docs/reports/data/*e184*` | `logs/reruns-note3.txt` |

## 6. Kit note 2's records, corrected (the verifier's nits 3 and 4)

- **(nit 3) Kit note 2 section 1, "With no level left out, every number is v2's"** (its line 63), reads: *with no level left out, A2-1's reading
  of E184-C (its verdict, its fit and its reference median) is v2's; the reported registered statistic is v2's only when the reference level
  also keeps 4 or more quads*, because score v3 keeps the reference level in that statistic's fit only with 4 or more (A3-4). The verifier's
  case C1, the reference cut to 3 quads and nothing else: `levels_left_out` empty and A2-1's reading v2's, but the reported registered
  statistic has 24 levels, 288 quads and T 2.33676 against v2's 25, 291 and 2.3413. That statistic is reported only, never a verdict, so no
  reading changes.
- **(nit 4) `$RB_OUT/config-B-reads.json` holds the latest read.** Kit note 1 recorded arm B's TDP and threshold "as read" in that file
  before the session; step 7 v2 (`rb/s09_reads_e184_v2.sh`, its line 68) writes it in both of its modes, so after step 10b it holds the
  read taken after the session. Nothing reads it. Both reads stay on the box as `build/e184/config-B-step7-<epoch>.json`, and step 11 copies
  them into the data's logs, where the reducer reads them.

## 7. Kit note 3's files (their sha256 in [`SHA256SUMS-e184-kit-note3`](SHA256SUMS-e184-kit-note3), 18)

| file | what | from |
|---|---|---|
| `KIT.md.dated-note-3.md` | this note | |
| `reduce_e184_v4.py` | A4's session gate | `reduce_e184_v3.py`, imported |
| `selftest_reduce_e184_v4.py` | the reducer's self-test v4 | `selftest_score_e184_v3.py`'s gate cases |
| `collect_e184_v3.sh` | the desk collector with reduce v4 | `collect_e184_v2.sh` |
| `interp_check_e184_v4.sh` | 3.9 against 3.13 | `interp_check_e184_v3.sh` |
| `audit_rb_e184_v3.sh`, `audit_desk_e184_v4.sh` | the device-command audits | v2's, v3's |
| `rb/s03_desk_e184_v3.sh` | step 2 v3: eight lists pinned, the window first | `rb/s03_desk_e184_v2.sh` |
| `rb/s22_collect_e184_v3.sh` | step 11 v3: `collect_e184_v3.sh` | `rb/s22_collect_e184_v2.sh` |
| `rb/list_steps_e184_v3.sh`, `rb/selftest_rb_e184_v3.sh` | the dry listing and the runbook's desk test | v2's |
| `logs/` (7 files) | the checks above | |

## 8. Open items (for the verifier, the readiness critic and the records)

1. **No verifier has read A4 or this note.** Card time only on his go and fresh approvals.
2. Kit note 2's other gaps stand: both arms' patched hosts compile first at step 6; arm B's identity (aifoundry1 not rebooted since 31 Oct
   2026, 13:45:24 PDT, or IDENTITY STOP and no firmware query).
3. Stated limits, unchanged: A3-1's censoring of E184-P's high side above a gain of about 1.6; the one-shire calibration effect; the rail
   witness rarely separates the meter from the power (A2-3).
4. Step 2 v3 is run for real on the committed tree after this commit (it needs E184's paths clean and the pins committed).

## Labels

- **Registered:** A4's rule (its own commit, before this one); the pins, the plan, the caps and the stops, unchanged.
- **Desk checks of code, not measurements:** every test result here.
- **Post hoc:** the verifier's case C1's figures (nit 3), a desk computation on synthetic sessions, quoted from its run.
- Nothing is blind or held out, and no E184 datum exists.

## Compute

All on the Intel, desk only, through the round's local slot (`slot.sh`), one job at a time at nice 10, one core: the reducer's self-test (about
2 minutes), the interpreter check (43 s), the runbook's desk test v3 (about 2 minutes), the dry listing and the audits (seconds). No lab box,
card, mini or network call.

SPDX-License-Identifier: Apache-2.0
