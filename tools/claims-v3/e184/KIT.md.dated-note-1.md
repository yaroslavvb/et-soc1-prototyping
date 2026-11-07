# E184's kit, dated note 1 (Sat 7 Nov 2026, week 45, about 13:20-14:15 PST): kit v2, the verifier's faults fixed in new files before any datum - the smoke gate, the pass and session gates before the scorer, the runbook ported onto k6's drivers with a rest rule and an exact copy-back, every process of a hold gated, partial passes, and the kit's records

*Written on the Intel in Q153 (lane `fix-e184`), desk only: no card claimed, no device command sent, no lab box, mini or network reached
(every ssh and rsync of the tests below is a stand-in that serves a local directory), nothing posted or deployed. New files only: the kit
(`65f844be`) and every file its hash lists name stay as committed (registration 11 of 11 OK, kit 44 of 44 OK). It follows dated amendment
A2 ([`E184.md.dated-note-A2.md`](E184.md.dated-note-A2.md), committed alone just before it: `a887fc74`, 14:04:38 PST), whose readings kit
v2's scorer implements. No E184 datum exists: `git log --all` shows no `docs/reports/data/*e184*`.*

## Results first

| the verifier's fault | kit v2's fix | file | its test |
|---|---|---|---|
| 1 (major): the smoke gate censored E184-P's alternative | the 16-shire n = 19 quad a gross check, -0.15 to +0.30 W; the 32-shire bands kept | `check_e184_v2.py` | self-test v2 V3: a session whose small steps read E178's 0.29 passes the smoke at the desk (v1's band read such a session NO-GO in the verifier's test); A2-7's NO-GO chance 0.566 -> about 1e-6 |
| 2 (major): E184-C not specific to code-sized steps | A2-1's statistic | `score_e184_v2.py` runs `power_e184_a2.py`'s `scan_fit_a2` | V4 (a one-code step SEEN, near code 1024), V6 (one missing code at the reference: NONE SEEN) |
| 3 (major): no pass-level gate before the scorer | E180's set-aside rule, the 600 MHz re-read, the session gate (the smoke in the session's own log and again at the desk; both config reads as registered) | `reduce_e184_v2.py`, `score_e184_v2.py`, `collect_e184.sh` | V9 (a pass another user's process stopped: set aside), V10 (800 MHz: set aside), V11 (smoke gate failed: NOT SCORED), V12 and B2 (a config read moved: NOT SCORED), V13 (a stale session's log beside the real one) |
| 4 (major): the runbook not ported | E184's runbook on k6's `rb_common.sh`, unchanged: bounded calls, the login-link stop, the holder rule, detached build and dry jobs, the desk-path gate; the rest rule (every session file named by its T0); the exact copy-back | `rb/` (12 files), `session_e184{s,b}_v2.sh` | **SELFTEST-RB-E184 PASS, 27 of 27**, with stand-in ssh and rsync; the dry listing, 22 steps, 0 fail, no network call |
| minor 1-4, 6 | A2-2 to A2-6 | `score_e184_v2.py`, `reduce_e184_v2.py` | V7 (a +25 mW offset: the null-corrected R governs), V2 (A2-3's words), V8 (dips set aside), E0 |
| minor 5: a hold's processes ungated | gate() before every process of a hold | `run_e184_v2.py` | DESKTEST-RUNNER-E184-V2 U5: 27 of 27 hold processes each after a gate mark naming it |
| minor 7: one bad quad stopped an arm | "partial" only when the clock held and at least half the items read (a busy sample off 600 MHz is now "fail"); a partial pass exits 7 and the queue goes on | `check_e184_v2.py`, `block_e184{s,b}_v2.sh`, `queue_e184_v2.sh` | DRY-INTEL-E184-V2 3f |
| minor 8: image-copy coherence untested | stated as an assumption the smoke tests (section 6) | | |
| minor 9 (d-g) | the kit's records (section 7) | | self-test v2 B1 (E184-G's count) |

**Device commands: GO on every v2 file set** (`dmcmd_audit.py`): arm S **GO, 32 send sites, every one a READ**, no allow-list, E153's
reviewed exception at `lib.sh:154` as v1 ([`logs/dmcmd-audit-s-v2.txt`](logs/dmcmd-audit-s-v2.txt)); arm B **GO, 34 sites, STATS_RESET
alone allowed** (pass 18441, [`logs/dmcmd-audit-b-v2.txt`](logs/dmcmd-audit-b-v2.txt)); the desk files **GO, 26 sites**, the dry pass's two
guard-test lines excepted as v1's ([`logs/dmcmd-audit-desk-v2.txt`](logs/dmcmd-audit-desk-v2.txt)); the runbook **GO, 23 sites**, every one
a READ, E184's guard's reset forwarding excepted because the runbook calls that guard with `config` only
([`logs/dmcmd-audit-rb.txt`](logs/dmcmd-audit-rb.txt)). Kit v2 sends no command v1 did not.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sat 7 Nov 2026 about 13:47 PST (rows L06, L08, L11, H27, P03; A2's block). The ids are
   opaque pointers into a private inventory. E180's kit is newer than the inventory and is cited by commit.
2. **Used** (each unchanged, called or sourced by path, its sha256 in `harness-e184-v2.json` or [`SHA256SUMS-e184-kit-note1`](SHA256SUMS-e184-kit-note1)):
   - **k6's runbook drivers** (`tools/claims-v3/q141k-runbook/k6/rb_common.sh`, sourced unchanged; its v3.1 `rb_run.py` and `nopath_q142s.py`;
     its `s05_look_k6.sh` and `s09_a3_reads_k6.sh`, called unchanged). *Check:* E171 ran them on 5 Nov, and E178, E180 and E181 on 6 Nov
     (208 calls, all ok, as the card day's critic read them).
   - **E180's kit v2 and v3 runbook steps** (`tools/claims-v3/e180/rb/`, its kit notes 1 `90a1312f` and 2 `1e19a451`: s02, s03 v3, s07 v2,
     s08 v2, s10 v2, s11 v2, s20 v2, s22 v2) as the form ported, and its `sync_paths_e180.py`, called unchanged; **E178's
     `scrub_tree_e178.py`**, called unchanged. *Check:* E180 ran these steps on aifoundry3 on 6 Nov, 42.0 card-minutes.
   - **E180's `reduce_e180_v3.py`** lines 145-146: the pass set-aside rule, ported.
   - **E184's own kit** (`65f844be`): every v2 file is its v1 with the stated changes (each made by counted, exact replacements and listed
     in its header), and v1's readers are imported unchanged.
3. **Not used:** kit v4's one-kernel option (E184's quads are one process each by design); a host-side operand checksum (section 6).
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this note.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. The smoke gate (fault 1)

`check_e184_v2.py smoke` is v1's gate with one band changed: the 16-shire n = 19 quad, at E178's operating point where part P runs, is a gross
check, **-0.15 to +0.30 W** (v1: 0.05-0.30 W; expected +0.157 W). The other bands stay: the null within +-0.15 W, n = 121 on 32 shires within
0.70-1.30 W, every minion within 7.6-9.3 W, the instruction rate within 3%, every busy sample at 600 MHz; arm B's gate is v1's. A2-7 gives the
censoring v1's band imposed and v2's removes. The v2 sessions call this gate; the reducer re-runs it at the desk on the copied smoke pass.

## 2. The gates before the scorer (fault 3)

- **`reduce_e184_v2.py`** (v1's reader, imported, with): **the pass gate**, E180's rule (a pass whose `block.json` status is not "ok" or
  "partial" is set aside whole, listed with its reason, its quads kept nowhere) and a re-read of its telemetry (any busy sample off 600 MHz:
  set aside); **A2-5's refresh rule** in every block (a quad records how many it set aside; the pass and the arm their sum); **the session
  gate**: from `<card>/logs/` (the box's `build/e184/`), the session of the T0 given (`--t0`, which the runbook passes; else the newest real
  log there): its log says "smoke gate passed"; the smoke, checked again at the desk by `check_e184_v2.py smoke`, reads SMOKE GO; both config
  reads exist and read the card as registered (aifoundry3: TDP 0 W, 65 C, 600 MHz at both ends; card 1: 600 MHz at both, the same TDP and
  threshold at both).
- **`score_e184_v2.py`**: no rule of an arm whose session gate fails (NOT SCORED with the reasons); v1's `score_s` and `score_b` on the kept
  passes; A2-1 to A2-4 (E184-C's statistic and words; the governing R; the attribution; the gates).
- **`collect_e184.sh`**: the desk collector the runbook's step 11 runs: the raw copy into the day's output, each arm present reduced with its
  T0, both scored.

## 3. The runbook (fault 4)

**`rb/rb_e184.sh`** sources `q141k-runbook/k6/rb_common.sh` unchanged, as E180's `rb_e180.sh` does, and adds only the step names ("_e184"),
the base commit (`65f844be`) and `e184_arm`: arm S is aifoundry3 card 0 (tree `~/aifoundry`, card directory `aifoundry3`), arm B aifoundry1
card 1 (tree `~/nekko`, `aifoundry1-c1`, never card 0). Every remote call: a 15 s hard-killed probe first; then `rb_run.py` with its bound
(60 s a read or a launch, 600 s a copy or one wait); a login link on either stream kills the call, appends "<HH:MM:SS> <host> needs a check"
to `RB_LOCK` and exits 11; nothing prompts; every call is logged in `RB_OUT`. The holder rule is k6's (`s05_look_k6.sh <box>`, at most 30
minutes in all, then skip that card). The build and the V3_DRY pass run as detached jobs on the box; the session launches only if both ended
rc 0 today. Nothing a collector writes may hold a desk path.

**The rest rule.** The v2 sessions name every file they write by their T0 (`session-<arm>-t<T0>.log`, `queue-<arm>-t<T0>.out`,
`config-<arm>-t<T0>-{start,end}.json`, `dmcmd-preflight-<arm>-t<T0>.txt`), open their log with "budget anchor T0 <epoch>" and close it with
"session end (T0 <epoch>)". Step 9 takes T0 on the box once, writes it to `build/q141k/e184<s|b>.t0` before the launch and keeps it in
`RB_OUT/t0-<arm>.txt`; step 10 reads only that T0's log, refuses a log whose first line names another T0, and counts the run ended only on
that T0's end line. No earlier attempt's "session end" can satisfy it (the selftest's W3).

**The exact copy-back.** Step 11 copies the arm's `build/claims-v3/<card>/e184`, `e184-smoke` and `e184-stoptest` to
`build/e184-raw/<card>/` (the level `reduce_e184_v2.py` reads) and the box's `build/e184/` without the operand images to
`build/e184-raw/<card>/logs/`, checks that the stop-path test recorded no launch and that the copy holds this T0's log, runs `collect_e184.sh`
with that T0, then the desk-path gate, then the login check over every directory of the output (E178's `scrub_tree_e178.py --check`), last.

**The runbook as it now runs** (KIT.md's box steps):

| KIT.md box step | file |
|---|---|
| 1, his go and the window | `rb/s02_window_e184.sh <day> <last start> <last end>` (one `RB_OUT` per arm) |
| 2, the desk check | `rb/s03_desk_e184.sh` (the pull; HEAD descends from `65f844be`; the four hash lists with their counts, 11, 44, A2's 6 and this note's 45; harness v2 rebuilt; plan and images re-made; HARNESS OK) |
| 3, the day's one post | the card lane's, under the post's lock (the lab's rule: one post a day, rewritten at each reservation and release) |
| 4, look first | `q141k-runbook/k6/s05_look_k6.sh aifoundry3` or `aifoundry1` (k6's, unchanged; on aifoundry1 E172's look: card 1's lines, the identity since E82's read) |
| 5, the sync | `rb/s07_sync_e184.sh S` or `B` (every file of `harness-e184-v2.json`, 59) |
| 6, the build and the box checks | `rb/s08_build_e184.sh S|B start`, then `... wait` (repeat while 17) |
| 7, the reads | `rb/s09_reads_e184.sh S|B` |
| 8, the V3_DRY pass on the box | `rb/s10_dry_e184.sh S|B start`, then `... wait` |
| 9, the session | `rb/s11_session_e184.sh S|B` (only after steps 4-8 read clean today and the post names the card) |
| 10, the wait | `rb/s20_wait_e184.sh S|B` (repeat while 17) |
| 11, release, then collect | the post's release; then `rb/s22_collect_e184.sh S|B`; then the data directory `docs/reports/data/<day>-e184-sensor-validation/` and a data verifier |

**A second launch of an arm on one day** needs a dated departure first (as E180's note 2 says for its own): `block_begin` skips any pass
directory that holds a `block.json`, so the departure says whether the earlier pass directories were moved aside first.

## 4. Every process of a hold gated (minor 5)

`run_e184_v2.py` is v1 with one change: in arm B's holds, `gate()` (D1's other-user test, the stall check and the live stop) runs before
every process, as v1's docstring and KIT.md said; each call also writes a "gate" mark. The v2 blocks call it.

## 5. Partial passes (minor 7)

(The v2 files' headers count the verifier's thirteen faults in one list, majors first: there minor 5 is "fault 9" and minor 7 "fault 11".)
`check_e184_v2.py block` calls a pass "fail" when any busy sample is off 600 MHz (v1 called that "partial", which E180's rule keeps), and
"partial" only when the clock held and at least half the pass's items read; the v2 blocks exit 7 on "partial", and `queue_e184_v2.sh` goes on
after a 7 (a 1, 3 or 5 still stops it). The reducer keeps a partial pass's readable quads.

## 6. Image-copy coherence (minor 8): an assumption the smoke tests

The patched host copies each segment's operand image to the card before its launches, and the kernel loads its operands from that memory at
each launch (`kernel/enercat.c` line 146). No desk test can show the copy reaches those loads (the desk host runs on a mock runtime). If it
did not, every B block would read as its A block: the smoke's n = 121 quad (0.70-1.30 W) and its every-minion quad (7.6-9.3 W) would read
about 0 and stop the arm. A copy that reached only some harts would read as a low E184-K (reported, against its band). A host-side operand
checksum would need a new pinned patch and its own first compile on the box; it is not added.

## 7. The kit's records (minor 9, items d-g, and the lane's header times)

- (d) `score_e184.py`'s docstring gives "1.8 and 0.06 W" for B2's minion and NoC steps; A1-2 and the catalogue's card-1 row give **1.86 and
  0.12 W**. The code uses neither.
- (e) The trees: KIT.md is right, aifoundry3's is `~/aifoundry` and aifoundry1's `~/nekko` (k6's `rb_tree`); `lib.sh`'s line-3 comment
  ("aifoundry3 (~/nekko, a copy of it)") is older and wrong for aifoundry3.
- (f) The self-test's E184-G check allowed three binomial sd (+-0.107 percentage points at 6,886 samples). The generator itself wrote **12
  glitches in 6,886 samples** (0.174%, a high draw from its 0.087%): self-test v2's B1 counts them again from the raw files and finds the
  reader's count equal. The reader is right; the check was weak.
- (g) `logs/desktest-host-e184.txt` (H5) and `logs/desktest-runner-e184.txt` (U3) carry launch counts that depend on timing (launches in a
  fixed time on a mock), so they do not re-make byte for byte; both pass. The same holds for v2's runner log.
- KIT.md's header "about 11:30-12:50 PST" and A1's "about 12:30 PST" are estimates written before the kit's commit, which is **12:23:35 PST**.

## 8. Kit v2's files

| file | what | from |
|---|---|---|
| `check_e184_v2.py` | the harness (v2's), the post-block status, the smoke gate | `check_e184.py` |
| `run_e184_v2.py` | the runner, every hold process gated | `run_e184.py` |
| `block_e184s_v2.sh`, `block_e184b_v2.sh` | one pass of each arm (run v2, check v2, exit 7 on partial) | v1's |
| `queue_e184_v2.sh` | the queue (v2 blocks; goes on after a partial pass) | v1's |
| `session_e184s_v2.sh`, `session_e184b_v2.sh` | the sessions (check v2's gates, preflight v2, the T0-named files) | v1's |
| `preflight_e184_v2.sh` | `dmcmd_audit` on each arm's v2 file set | v1's |
| `make_harness_e184_v2.py`, `harness-e184-v2.json` | the box list: 59 files (17 of E184's, lib.sh, D1, E128's guard, the audit and its table, 37 enercat files) and the pinned patched source | v1's |
| `reduce_e184_v2.py`, `score_e184_v2.py`, `collect_e184.sh` | the gates, A2's readings, the desk collector | v1's reader and scorer, imported |
| `fake_card_e184_v2.py`, `selftest_score_e184_v2.py` | synthetic sessions with A2's and the gates' cases (v1's bytes with no new option, E0); the scorer's self-test | v1's |
| `desk/desktest_runner_e184_v2.py` | the runner's real path at the desk, plus U5 | v1's |
| `dry_intel_e184_v2.sh`, `interp_check_e184_v2.sh`, `audit_desk_e184_v2.sh`, `audit_rb_e184.sh` | the Intel dry pass, the interpreter check, the audits | v1's |
| `rb/` | the runbook (section 3), its dry listing and its desk test | E180's |
| `logs/` (v2) | every check below | |

## 9. The checks (each re-run by this lane; the logs are this commit's)

| check | result | log |
|---|---|---|
| the scorer's self-test v2 | **SELFTEST-SCORE-E184-V2 17 of 17** | `logs/selftest-score-e184-v2.txt` |
| v1's self-test, re-run unchanged | 14 of 14, its committed log re-made byte for byte | `logs/reruns-note1.txt` |
| the hash lists; the plan and images; no E184 data | registration 11 of 11, kit 44 of 44, A2 6 of 6 OK; plan and images IDENTICAL (467); no commit names `docs/reports/data/*e184*` | `logs/reruns-note1.txt` |
| the runbook's desk test | **SELFTEST-RB-E184 PASS, 27 of 27** (a real launch on the stand-in box, the rest rule, the real collector on both arms) | `logs/selftest-rb-e184.txt` |
| the runbook's dry listing | 22 steps, 0 exit non-zero, no ssh or rsync | `logs/dry-listing-e184.txt` |
| the Intel dry pass v2 | **DRY-INTEL-E184-V2 PASS**, 38 of 38 checks (v1's 37 and 3f), no stub executed, no network call | `logs/dry-intel-e184-v2.txt` |
| the runner's desk test v2 | **DESKTEST-RUNNER-E184-V2 5 of 5** (U5: 27 hold processes, each after a gate mark naming it; 47 gate marks) | `logs/desktest-runner-e184-v2.txt` |
| the interpreter check v2 | **INTERP-E184-V2 SAME** (3.9 and 3.13, with A2-5's rule exercised) | `logs/interp-check-e184-v2.txt` |
| the harness v2 | HARNESS OK: 59 files; `make_harness_e184_v2.py --check` CHECK PASS | `logs/harness-check-v2.txt` |
| A2's outputs under 3.9 and 3.13 | `a2-check-e184.json`, `power-e184-a2.json` and `.txt` IDENTICAL under both | `logs/reruns-note1.txt` |
| dmcmd_audit | S GO 32, B GO 34, desk GO 26, runbook GO 23 | `logs/dmcmd-audit-{s-v2,b-v2,desk-v2,rb}.txt` |

**Two faults the runbook's desk test caught in this lane's own first drafts, fixed before this commit.** (1) Step 9 read the launch's T0
with k6's `rb_val`, which substitutes only the part a pattern matches, so its first pattern returned the T0 with the rest of the line
attached; the pattern now takes the whole line and the T0 must be digits (case G4 found it, by launching for real on the stand-in box).
(2) The stand-in ssh first handed `bash -s` its script as a regular file: macOS's bash 3.2 then re-reads part of the script after a
background job forks (the two share the file offset), which garbled the launch line. Real ssh hands the box a pipe, which bash reads byte by
byte; the stand-in now pipes it too. E180's runbook desk test has the same stand-in, but none of its cases launches, so it never met this.

## 10. Open items (for the verifier, the readiness critic and the records)

1. **No verifier has read A2 or this note.** Card time only on his go and fresh approvals.
2. **The box build is still new:** the patched host's first compile against the real runtime is step 6; if it fails, that arm does not run
   that day.
3. **Arm B's B3** is read against September's aifoundry3 rows only, as registered.
4. **The rail witness** (A2-3) is not expected to resolve the small-to-large ratio, so a LOW or HIGH will most likely read "not separated".

## Compute

All on the Intel, desk only, through the round's local slot (`slot.sh`), one job at a time at nice 10, one core: A2's checks and powers
(about 1 minute each), the self-tests, the dry pass, the desk tests and the runbook's desk test (each a few minutes). The desk host's
compile with `clang++` ran inside the slot job. No Verilator bench was needed, so the mini was not used; no lab box, card or network call.

SPDX-License-Identifier: Apache-2.0
