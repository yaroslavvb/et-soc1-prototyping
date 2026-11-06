# E178's kit, dated note 1: the kit verifier's faults fixed before any E178 datum - the sync takes every harness file, E178-R-int8 read on the scored P with its power there, the login check reads every directory, a failed arm is dropped (Q146(f); new files only)

*Fri 6 Nov 2026 (week 45), written about 01:05-02:10 PST on the Intel, desk only (Q146(f), lane `kitfix-q146f`): no card was claimed, no
device command was sent, no lab box or mini was reached, nothing was posted. It sits beside [KIT.md](KIT.md) (the kit,
`a4aafc6f`, 23:06:28 PST Thu 5 Nov), which stays as committed, as does every file of the kit's, the registration's, A1's and A2's hash
lists (72, 76, 27 and 17 OK after this note). It answers the kit's adversarial verifier (`kitv-q146f`, 00:20-00:58 PST today: holds with
fixes, 0 critical, 0 major, 4 minor, 4 nits), the step Q146's readiness critic asked for before the session, and is committed with its
files before any E178 datum: `git log --all` shows no `docs/reports/data/*e178*`. It changes no rule, forecast, threshold, statistic or
registered power figure, and no file the box runs: harness-e178.json is unchanged (84 files). What it adds: three step files the runbook
now runs in place of v1's (section 6), one collection rule (section 4), one check (section 3), the power of one rule at the reading the
scorer makes (section 2), and four corrections of KIT.md's words (section 5).*

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md and MAP.md section 3, read Fri 6 Nov 2026 about 01:10-01:20 PST. Public rows read: P06,
   H19, H24, H25, H26, H27, H28. The row ids are opaque pointers into a private file.
2. **Used** (each unchanged, called, imported or followed by path; sha256 in [`SHA256SUMS-e178-kit-note1`](SHA256SUMS-e178-kit-note1)):
   - **Q143(k)'s step 7** (`tools/claims-v3/q143k-runbook/s07_a3_sync_q143k.sh`, `92a1b27f`): the form of the v2 sync, a path list read
     from the run's own box list (every repo file but `build/`), sent in one `rsync -a -c -R`. *Check against the same operation on the same
     box:* on 5 Nov 2026 at about 16:40 PST it synced 12 of the 20 files v2 adds, in this form, into aifoundry3's `~/aifoundry`, each at the
     sha256 harness-e178.json holds (`tools/claims-v3/e176/frozen-e176.sha256`), and E176's session ran from that tree at 17:21.
   - **E171's harness and runner on this box** (data `91f8ae40`): the 14 card-code files and four binaries checked there at the harness's
     sha256 at 11:38 PST on 5 Nov, and E78's six anchor tiles checked by sha256 in all four of its passes. Where they still match, the v2
     rsync sends nothing (`-c`).
   - **E174's departure D1** (`tools/claims-v3/e174/E174.md.dated-note-3.md`, `0a14c7bb`): "a bounded copy of exactly the committed
     files", made after its gate stopped; v2 makes that copy part of the sync, before any gate.
   - **E173's D1 made a registered rule for a later collection** (`d85d1e0f`): the precedent for registering a collection remedy before a
     run's data (section 4).
   - **E164's login scrub** (`tools/claims-v3/e164/scrub_etwho_e164.py`, `45aeda12`), imported unchanged by `scrub_tree_e178.py`: its
     patterns, its owner rule and its whole-word rule. **E78's runner** (`tools/claims-v3/kinds/run_e78.py`, `cfd94285`): the wording of
     its mid-pass stop, read, not run.
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`, `9a2630ff`; v3.1's `rb_run.py` and `nopath_q142s.py`, `0d2cb5dd`)
     through `rb/rb_e178.sh`, unchanged; **the kit's collector** `collect_e178.sh` (`a4aafc6f`), line for line in its v2; the kit's desk
     test `rb/selftest_rb_e178.sh`, case for case in its v2.
   - **The registered noise model** (`power_e178.py`, `48171930`; `power_e178_a1.py` and A1's operand-bit truths, `f421c67a`), unchanged,
     with their seeds. *Check:* on the same draws, the frozen-P column of section 2 reproduces power-e178.json's 36 E178-R-int8 cases and
     power-e178-a1.json's 10 (A) cases exactly.
   - **E171's committed reduction** (`docs/reports/data/2026-11-05-e171-blind8-aifoundry3/e171.json`): the spread of the measured int8
     rates over its 21 int8 items, 1.642e-4 of the mean (post hoc for E171; here only an input to section 2's noise).
   - **The kit verifier's sync-tree test** (its method, from its own scratch): the template of desk case S1 (section 1).
3. **Not used:**
   - P06, Esperanto's public power viruses (et-platform's `test-compute-kernels`): checked, not applicable. They hold fixed operands, not
     one number (E178.md section 9's reason). KIT.md's block lists P06 as checked but names it in neither list; this is that line (nit 8).
   - H19's and H24's one-level login scrubs (E170's, E172's and E174's collectors): not used; section 3's check replaces them for E178.
   - E172's card-1 kit: still owed, as KIT.md says.
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it. The logins and the uid in
   the desk tests are made up.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. The sync takes every file the harness names but the box binaries (fault 1, the E174 class; nit 7)

KIT.md's box steps are named by their numbers there: 2 the desk check (`rb/s03_*`), 5 the sync (`rb/s07_*`), 6 the checks on the box
(`rb/s08_*`), 11 the collection (`rb/s22_*`).

**The fault.** v1's sync ([`rb/s07_a3_sync_e178.sh`](rb/s07_a3_sync_e178.sh)) copies 60 of harness-e178.json's 80 non-binary files.
It relies on aifoundry3's `~/aifoundry` still holding the other 20 at their committed sha256:
- E163's 14 card-code files: `lib.sh`, `run_e78.py`, `e78_common.py`, `reduce_e78.py`, `kinds.json`, the guard, `dmcmd_audit.py` and its
  table, the host source, and the five ccheck files;
- E78's six anchor tiles: fp32 and fp16 zeros and randn, int8 zeros and full. v1's header leaves these out (nit 7).

Box step 6 checks all 84 before any device opens, so the risk was a lost window, never card time. Still, the day critic's kit v4 rule,
"gate and sync must agree, tested in a tree built from the sync list alone", was not met.

**The fix: [`rb/s07_a3_sync_e178_v2.sh`](rb/s07_a3_sync_e178_v2.sh), KIT.md's box step 5 from now on.**
- Its path list is v1's ten paths plus every other file harness-e178.json names but its four box binaries. The list is read from the
  harness itself by [`sync_paths_e178.py`](sync_paths_e178.py), so gate and sync agree by construction: 30 paths, all 80 non-binary files.
- The binaries are built on the box, never synced, and box step 6 still checks them.
- The rsync is v1's own form (`rsync -a -c -R --exclude __pycache__`, the form E171 and E176 used on this box). `-c` sends nothing where a
  file already matches, as all 20 did on 5 Nov.
- As in v1, uncommitted changes in any of the 30 paths refuse (16), and only the pushed commit is synced.
- New in v2: nothing is synced unless the lab clone's 80 files read at the harness's sha256 (`check_e178.py --desk`, as box step 2
  runs it), else 16. v2 sends 20 files v1 never sent; a later commit to one of them (`lib.sh` is shared by every kit) must stop here,
  before it can overwrite the box's good copy.

**The desk test** ([`rb/selftest_rb_e178_v2.sh`](rb/selftest_rb_e178_v2.sh), a scratch git repository and a stand-in box):
- **S1:** v2's own rsync alone builds the box tree, plus four stub binaries.
  - 84 of 84 harness files are present, and the 80 non-binary files are at their sha256.
  - Run there in V3_DRY, with network stand-ins that refuse: `check_e178.py` reads HARNESS OK 80; `preflight_e178.sh` reads GO (32 sites);
    `e178_common.py --verify` reads 0 problems.
  - Passes 17810-17813 make 78 launches each through the C wrapper, and the smoke 10.
  - The session's start gate exits 8, the smoke gate's imports resolve, and no network call is made.
- **S2:** v1's rsync alone leaves out exactly the 20 files (14 card-code files, 6 anchor tiles). This is the fault, shown.
- **S3:** an uncommitted change in `lib.sh` refuses with 16, and no rsync runs.
- **S4:** the same change committed (the tree clean, `lib.sh` no longer at the harness's sha256) refuses with 16, and no rsync runs.

**If box step 6 still reads a missing or different non-binary file:** run box step 5 (v2) once more, then box step 6. If it reads wrong
again, stop: no session starts, and no card time is spent (box step 6 opens no device). A differing binary stops as KIT.md's box step 6
says: a dated amendment registers it first.

## 2. E178-R-int8 is read on the scored P, as registered; its power at that reading (fault 2)

**The rule as registered** (E178.md section 5): "Spearman rho (average ranks for ties) of the scored P against the measured D over the
13 int8 kinds", rho >= 0.56. The scored P (E178.md section 4; KIT.md) is the frozen P x (the kind's measured rate / E171's rate); for int8
s = 1.

**The reading, stated before any datum:** E178-R-int8 is computed on the scored P, exactly as `score_e178.py` computes it, unchanged.
- The frozen P's ties (int8 ones = 2 = 4 = 8, and 3 = 6) do not survive the measured rates, which differ by parts in 10^4. So the scored P
  orders each tied group by measured rate.
- Average ranks still apply wherever an exact tie remains, in D or in P.
- A kind's rate moves its own P by about 3e-4 W, far inside D's noise, so breaking a tie this way is a coin toss with respect to D.

**Its power there.** The registered power was computed on the frozen P, ties exact. [`power_r_e178_note1.py`](power_r_e178_note1.py)
computes both readings on the same draws of D, with the registered generators. Each kind's rate is drawn as 1 + N(0, 1.642e-4), E171's
spread, from a separate generator. Output: [`power-r-e178-note1.txt`](power-r-e178-note1.txt) and `.json`.

| truth (FULL, n 4, sigma1 0.125) | P(PASS), frozen P (as registered) | P(PASS), scored P (the reading) |
|---|---|---|
| P, model error 0 | 0.9987 | 0.9979 |
| P, model error 0.03 W | 0.9952 | 0.9935 |
| every kind costs the same | 0.0246 | 0.0250 |
| A1-1's 1-bits of the A and B words, at P's spread | 0.6663 | 0.6414 |
| the same 1-bits, at the bridge's size | 0.1116 | 0.1086 |
| the 0-bits, at P's spread | 0.0000 | 0.0000 |

- At n 3 (one pass set aside): P 0.9973 becomes 0.9954, and the 1-bits at P's spread 0.6100 becomes 0.5836.
- So E178.md section 5's power line, "0.995-0.999 if P's order is right; 0.025 if every kind costs the same", reads **0.994-0.998 and
  0.025** at the scorer's reading.
- The line (0.56), the statistic and the verdict words are unchanged.
- The frozen-P column reproduces the committed figures exactly: 36 of 36 grid cases and A1's 10 of 10 (`--check` re-makes both files byte
  for byte).

## 3. The login check reads every directory, and run_e78's own stop line (fault 3)

**The fault.** v1's collection step (box step 11) ran E164's scrub check (`scrub_etwho_e164.py --check`) on the output's `logs/` only, and
that scrub reads one directory level. The verifier's case: a mid-pass "another user on this card" stop, from run_e78.py's
`others_on_card`. run_e78 writes it into that pass directory's `run.log` and `STOP`, which no check read.

Two corrections to that case, found here:
- **On aifoundry3 the entry is a uid, not a login.** `session_e178.sh` unsets `ET_DEVICES`, so run_e78 reads `ps`, and each entry reads
  `'<uid>:<pid>:<comm>'`. The login form, `'<node> <login> <pid>'`, is the et-holders path, taken only with `ET_DEVICES` set. E164's scrub
  withholds another account's uid as well (its `procs` rule), so the uid must not reach a public file either.
- **E164's `--check` does not read that line in any directory.** On a pass directory planted with both forms it reads "OK (0 left)". Desk
  case P6 shows v1's collection step passing such an output with exit 0. So the verifier's fix, E164's `--check` over every directory,
  would not by itself have closed the hole.

**The fix, two new files:**
- [`scrub_tree_e178.py`](scrub_tree_e178.py) imports E164's scrub unchanged.
  - It reads every file in every directory under the output, skipping `*.gz` and `*.bin` (C logs, telemetry and tile dumps, which carry no
    account).
  - It reports E164's leftovers and every entry of a run_e78 stop list that is not yet withheld. An entry it cannot parse counts as left.
  - `--check` rewrites nothing. Without `--check` it rewrites in place (the uid becomes `<another-uid>`, the login `<another-user>`, E164's
    whole-word rule now over the whole tree), then checks again.
  - With no box login recorded, every login counts as another account's.
- [`rb/s22_collect_e178_v2.sh`](rb/s22_collect_e178_v2.sh) is KIT.md's box step 11 from now on.
  - Its login check is `scrub_tree_e178.py --check` over the whole output, in place of v1's `logs/`-only check.
  - It runs LAST, after the C-session gate and the desk-path gate. A stop there therefore leaves one remedy, which its message names: the
    rewrite, then `--check` again (0 left), recorded in the data README.

**The desk cases** (`rb/selftest_rb_e178_v2.sh`):
- **P1:** a uid in a pass directory's `run.log` and `STOP` gives 16, after the desk-path gate passed.
- **P2:** a login in the smoke's `run.log` gives 16.
- **P3:** E164's own others-present form, in a pass directory, gives 16.
- **P4:** the owner's own et-who lines give 0.
- **P5:** the same lines with no login recorded give 16.
- **P6:** v1's collection step on P1's layout gives 0, the hole.
- **P7:** the remedy rewrites both lines, the check then reads 0 left, and the lines are kept with the uid withheld.

## 4. A failed arm is dropped, never left in the output (fault 4; registered before any datum)

The seven reduction arms are reported only; no verdict reads them.

**A correction to the verifier's case.** In the real collector the scorer's arm error string holds a repo-relative path:
`collect_e178.sh` passes `build/e178-out/...`, while the verifier's case X6 used an absolute scratch path. So that string would not stop
box step 11's desk-path gate. What does stop it is the failed arm's reduce log: a Python traceback carrying the lab clone's absolute module
paths, and numpy's path under this Mac's home directory. In desk case V2X, the dropped files hold 3 desk-path hits.

**The rule, [`collect_e178_v2.sh`](collect_e178_v2.sh), which box step 11's v2 runs:**
- an arm whose reduction exits non-zero is not scored;
- an arm the scorer reports as an error is dropped, and the session is scored again without it, once;
- a dropped arm's four files move to `build/e178-dropped-arms/<arm>/` (ignored by git, never committed);
- `arms-dropped.txt` in the output names each dropped arm with its reason: the exit status, or the exception's type, never a message or a
  path.

A dropped arm is named in the data README as this rule's use: registered here, not a departure chosen after the data. A later kit can keep
arm logs path-free at the source.

**The desk test** ([`selftest_collect_e178_v2.py`](selftest_collect_e178_v2.py), on selftest_collect_e178.py's relabelled real session):
- **V2:** with no arm failing, v2's scored.json, results.md, e178.json and runs.csv equal v1's byte for byte.
- **V2X:** one arm's reduction fails (a traceback) and another's is unreadable to the scorer. Both are dropped and named, the session is
  scored again, five arms are scored and none is in error, and the primary's rules and verdicts equal v1's.
- **P:** the desk-path gate reads 0 hits on all three outputs.
- **R:** each desk-test stand-in, set without `E178_DESKTEST=1`, refuses with 10.

## 5. KIT.md's words, corrected (nits 5-8)

- **E178-W-int8's line is 7.484 fJ a flip:** power-e178.json's `slope_P_fJ_per_flip`, 7.48427, which the scorer reads. KIT.md line 115's
  "7.4796" is a typo; E178.md's 7.48 and power-e178.txt's 7.484 agree.
- **The Intel dry pass holds 18 checks, 18 of 18 PASS,** not "19 of 19" (A2-3 says so too; re-run here, section 7).
- **v1's sync step's header** leaves E78's six anchor tiles out of the files left on the box. v2's header names them, and v2 syncs them
  (section 1).
- **KIT.md's Builds on, (3) Not used,** gains P06 (above).

## 6. The runbook as it now runs (KIT.md's box steps)

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window | `rb/s02_window_e178.sh` | no |
| 2, the desk check | **`rb/s03_desk_e178_v2.sh`** | v2: HEAD descends from `c212a345` (A2); five hash lists, each with its count: 76, 27, 72, A2's 17, this note's 47 |
| 3, the post | (the card lane's) | no |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no |
| 5, the sync | **`rb/s07_a3_sync_e178_v2.sh`** | v2: section 1 |
| 6, the checks on the box | `rb/s08_a3_preflight_e178.sh` | no |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the V3_DRY pass on the box | `rb/s10_a3_dry_e178.sh` | no |
| 9, the session | `rb/s11_a3_session_e178.sh` | no |
| 10, the wait | `rb/s20_wait_e178.sh` | no |
| 11, release, then collect | **`rb/s22_collect_e178_v2.sh`** | v2: sections 3 and 4 |

- The dry listing is [`rb/list_steps_e178_v2.sh`](rb/list_steps_e178_v2.sh), and the desk test is `rb/selftest_rb_e178_v2.sh`.
- The v1 files stay as committed, for the record. On the card day the v2 files run.

## 7. The checks after the fix

All were re-run with this note's files in place (logs in `logs/`):
- every frozen list: 76, 27, 72 and 17 OK;
- every `--check`: kinds (40), forecast, plan, flips_a1, kit, harness (84) and power_r (byte for byte);
- `e178_common --verify` 0 problems; `check_e178 --desk` HARNESS OK 80.

| check | result | against the committed log |
|---|---|---|
| the Intel dry pass (`dry_intel_e178.sh`, unchanged) | DRY-INTEL PASS, 18 of 18 | identical but dates and times |
| the scorer's self-test (unchanged) | 16 of 16 | identical but dates and times |
| the runbook's desk test, v1 (unchanged) | 17 of 17 | identical but dates and times |
| the runbook's desk test, v2 ([`logs/selftest-rb-e178-v2.txt`](logs/selftest-rb-e178-v2.txt)) | 31 of 31 | new |
| the dry listings, v1 and v2 ([`logs/dry-listing-e178-v2.txt`](logs/dry-listing-e178-v2.txt)) | 0 steps fail in either | v1 identical but dates, times and two clock readings (the window's minutes from now, the go's epoch) |
| the watcher test (unchanged) | K1-K5 PASS | the same verdicts; only epoch stamps and one read latency (0.056 s, was 0.055) differ |
| the collection's desk test, v1 (unchanged) | 5 of 5 | identical |
| the collection's desk test, v2 ([`logs/selftest-collect-e178-v2.txt`](logs/selftest-collect-e178-v2.txt)) | 6 of 6 | new |
| dmcmd_audit, the kit's four (the session's file set, without E153's exception, the desk files, the runbook's v1 steps) | GO 32 sites; NO-GO only at lib.sh:154; GO 0; GO 11 | identical |
| dmcmd_audit, every runbook step file v1 and v2 with k6's steps 5 and 9 ([`logs/dmcmd-audit-rb-v2.txt`](logs/dmcmd-audit-rb-v2.txt)) | GO, 11 sites, every one READ, all in E128's guard | new; its content equals v1's runbook audit line for line |
| dmcmd_audit, this note's desk files ([`logs/dmcmd-audit-desk-v2.txt`](logs/dmcmd-audit-desk-v2.txt)) | GO, 0 sites | new |

- None of the new files sends a device command. None names the firmware-revisions query, `--reset-ms`, a SET or a residency read.
- The full record is [`logs/reruns-note1.txt`](logs/reruns-note1.txt).

## 8. Labels

- Every rule, threshold and forecast here is registered: the registration `48171930`, A1 `f421c67a`, A2 `c212a345`.
- This note adds, before any E178 datum:
  - a reading of E178-R-int8 (section 2);
  - one collection rule (section 4);
  - one check (section 3);
  - the step files that carry them.
- No E178 datum exists, so nothing here is blind, held out or post hoc for E178.
- Section 2's shares and the desk tests' outputs are design arithmetic and plumbing on committed files; none of them is a forecast or a
  verdict.
- E171's rate spread is read from E171's committed reduction: post hoc for E171, and used here only as noise.

## 9. Files, the hash list, compute

- **New files (20):**
  - this note;
  - `sync_paths_e178.py`, `scrub_tree_e178.py`, `collect_e178_v2.sh`, `selftest_collect_e178_v2.py`;
  - `power_r_e178_note1.py`, `power-r-e178-note1.json`, `power-r-e178-note1.txt`;
  - `rb/s03_desk_e178_v2.sh`, `rb/s07_a3_sync_e178_v2.sh`, `rb/s22_collect_e178_v2.sh`, `rb/list_steps_e178_v2.sh`,
    `rb/selftest_rb_e178_v2.sh`;
  - `logs/selftest-rb-e178-v2.txt`, `logs/dry-listing-e178-v2.txt`, `logs/selftest-collect-e178-v2.txt` and `.json`,
    `logs/dmcmd-audit-rb-v2.txt`, `logs/dmcmd-audit-desk-v2.txt`, `logs/reruns-note1.txt`.
- **[`SHA256SUMS-e178-kit-note1`](SHA256SUMS-e178-kit-note1), 47 entries.** It covers these 20 and the 27 committed files they source,
  call, import or replace, each unchanged: KIT.md, the kit's and A2's lists, harness-e178.json, `rb_e178.sh`, the v1 step files and desk
  test, the collector, scorer, reducer and C-session rule, the collection's desk test and its stand-in, the noise model, the forecasts and
  power files, the k6 and v3.1 drivers, E164's scrub, run_e78.py and E171's e171.json.
  - Check it from the repository's root: `shasum -a 256 -c tools/claims-v3/e178/SHA256SUMS-e178-kit-note1`.
  - Box step 2's v2 checks it too.
- **Compute:** every job ran here through the round's local slot (`slot.sh`), one at a time, at nice 10 and one core:
  - the collection's v2 desk test, three runs while it was built, about 80 s each (01:23-01:29);
  - the runbook's v2 desk test (01:34:06-01:35:22);
  - section 2's power and its `--check` (01:36:56-01:42:48);
  - the re-runs of section 7 (01:45:30-01:54:38).

  No bench, mini, lab box or card was used. The collection tests wrote under the lab clone's `build/`, which git ignores, and removed what
  they wrote.

SPDX-License-Identifier: Apache-2.0
