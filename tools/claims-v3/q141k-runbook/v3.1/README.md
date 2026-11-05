# Q142(s) v3.1: the card day's runbook after v3's verifier

*Wed 4 Nov 2026 (week 45), about 21:15-22:15 PST. Written and tested on the Intel, desk only: no card was claimed, no device command
was sent, no ssh reached a lab box, nothing was posted. New files only. v1 ([`../README.md`](../README.md), lab `e962227a`), v2
([`../v2/README.md`](../v2/README.md), `16771f36`) and v3 ([`../v3/README.md`](../v3/README.md), `326f1293`) stay as committed, byte for
byte. Nothing here changes a registration, a frozen file, a prediction, a stop or a rule of any run.*

v3 answered the card half's critic (Q141's card half, 4 Nov 2026), next step 4: make the next card day's runbook safe. v3's verifier
read it the same evening (about 20:18-21:05 PST) and found that it holds with fixes. v3.1 fixes what the verifier found in the
runbook:
- **fault 1**, which v2 and v3 share;
- **nits 5 and 8**, in v3's own fixes.

The verifier's other findings concern the watcher fix and its record, and are fixed beside them:
- the watcher amendment's five statements: [`../../hpl/run_hpl.py.dated-note-2.md`](../../hpl/run_hpl.py.dated-note-2.md);
- E163's README had no link back to v3's fix of its D1 (the owner's rule of 29 Oct 2026, a fix always links the original complaint):
  [`README.md.dated-note-q142s.md`](../../../../docs/reports/data/2026-11-04-e163-blind7-aifoundry3/README.md.dated-note-q142s.md).

A dated note beside v3's README says v3.1 supersedes it: [`../v3/README.md.dated-note.md`](../v3/README.md.dated-note.md).

## Results first

- **Fault 1 (minor): no version of step 22 read whether a collection's check of C finished.** `ccheck.py` exits 1 both when it crashes
  and when a launch's C is wrong (`ccheck.py:732`), and it writes its `--out` file only when it runs to its end (`ccheck.py:729-731`).
  The collectors print `ccheck rc=N` and go on, and the scorers then score without the check. The verifier found this in `e163` and
  `e166`; it holds in `e164`, `e165` and `e167` too. v3.1's `cc_gate` reads each check's `--out` file with
  [`ccdone_q142s.py`](ccdone_q142s.py). The step stops (14) before it says "collected" unless every file is there, holds `ccheck.py`'s
  summary and was written by this collection. A genuine C FAIL is a finished check: it goes on to the registered C rules, as before.
- **The end-to-end run with the real collector, reducer, C check and scorer** ([`logs/e2e-ccheck.txt`](logs/e2e-ccheck.txt)). It ran
  over E163's committed raw layout, in a scratch clone without the C check's RTL source, so the check crashed.
  - The scorer still wrote `results.md`. 17 of E163's 28 registered rules read NOT SCORED, and 5 C rules that pass on the data read
    FAIL (K14-C, KC, KE, KEprime and KE-C).
  - v2 said "E163 collected and scored".
  - v3 stopped, but only because the crash's traceback held a desk path: 16, for the wrong reason.
  - v3.1 stopped at its C gate: 14, "E163's check of C did not finish".
  - With the RTL source back, v3.1 collected E163 exactly as committed: 43 top-level outputs byte for byte once the pass prefix is
    normalised, all 28 verdicts identical, no desk path.
- **Nit 5: s13 read the launcher's exit 9 as a failure.** That refusal's line is `check_e164.py`'s `HARNESS DIFFERS - refusing:`, which
  v3's pattern missed. So v3 exited 14, against its own header. v3.1 exits 10. A `check_e164.py` that crashes, and so prints no such
  line, still exits 14.
- **Nit 8: the desk-path gate passed a path that was not there.** v3's `nopath_q142s.py` printed `MISSING` and read CLEAN. v3.1 counts
  it as a hit (exit 3), and `rb_nopath` stops the step (16) with its own message.
- **The desk test, [`logs/selftest.txt`](logs/selftest.txt): 589 of 589 checks pass**, in 302 s. A stand-in `ssh` and `rsync` sit
  first on PATH, and no lab box is reached. v3's cases A-F, X1-X10 and Y1-Y12 run against v3.1 (397 checks, as in v3). Z0-Z7 add 112,
  with v3 run beside each fault. V has 39 checks and the dry listing's E 41. The other checks:
  - the dry listing, 50 of 50 steps exit 0, with no ssh or rsync call;
  - `dmcmd_audit` GO on v3.1's file set with E128's guard beside it (11 send sites, all READ), as v3's;
  - the public-text scan, CLEAN.
- **None of it bit on 4 Nov, as far as the committed records show.** Every check of C that the card half's collections ran finished,
  all PASS (case Z0, on the ten committed checks): E163 4,062 launches, E164 3,896, E165 2,758 (s1 2,734, the smoke 20, the stop test
  4), E166 6,692 and E167 3,377. For the nits: E164's session ran (14:19:34-15:17:53 PST), and each collection's outputs are in its
  committed data directory.

## What v3.1 changes

| # | severity | what v3 does | where | v3.1 | cases |
|---|---|---|---|---|---|
| 1 | minor | Reads nothing of a collection's check of C. A crashed check leaves no `--out` file, and the scorer runs without it: E163's 17 rules NOT SCORED and 5 C rules FAIL, as "collected and scored". The same goes for `e166` (`collect_e166.sh:24`), `e164` (`collect_e164.sh:84`), `e165` (`collect_e165_bounded.sh:83` checks each session and reads nothing) and `e167` (step 22's own checks, whose status it never read) | `s22_collect.sh`, [`ccdone_q142s.py`](ccdone_q142s.py) (new) | `cc_gate` after each collector, once the checks that read the collector's own output have run: every `--out` file must be there, be JSON with `ccheck.py`'s summary (its launch count the file's own), count at least one launch, and be written since the collector began. A file left by an earlier try is refused; that matters for `e166`, whose collector never clears its `ccheck/`. Else the step stops (14), nothing scored as registered. A C FAIL is no stop | Z0, Z1a-d, Z2a-c, Z5, Z6, Z7; the end-to-end run |
| 5 | nit | `s13` reads the launcher's refusals by `^REFUSED\|^usage\|^not a date`, which misses exit 9's line, `HARNESS DIFFERS - refusing:` (`check_e164.py:49`, through `launch_e164_a1.sh:64`). So that refusal exits 14, against v3's own header | `s13_a1_launch.sh` | The pattern also reads `^HARNESS DIFFERS`: every refusal the launcher's header lists exits 10. A launcher failing any other way, a crashed `check_e164.py` among them, exits 14 | Z3, Z3b |
| 8 | nit | `nopath_q142s.py` prints `MISSING` for a path that is not there, and still reads CLEAN with exit 0. So a collector that wrote somewhere else passes the gate without one of its files being read | `nopath_q142s.py`, `rb_common.sh`'s `rb_nopath` | A missing path is a hit (exit 3). `rb_nopath` stops the step (16) with its own message: an output this step should have written is not there | Z4a, Z4b |

Also changed:
- Every step's name carries `_v3.1` in the log and its messages.
- The dry listing names `v3.1/`.

The order inside each collection step matters, because `rb_has` reads the last call's output. Each `cc_gate` comes after the checks
that read the collector's own lines (`results.md written`, `score rc=0`, a failed copy) and before the login scrub and the desk-path
gate. A first draft put it before them, and the desk test caught that: Y1 and Y2 then read the gate's output in place of the
collector's.

## What the read checked and found sound

The verifier re-ran v3's desk test (453 of 453), its dry listing (50 of 50, no ssh or rsync) and its audits (GO; bare NO-GO at exactly
`s09_a3_reads.sh:24`). It read every fault of v3's list in v2's code and confirmed the fix of each. It ran v3's `s22 e163` end to end
with the real collector, reducer, C check and scorer, in a sparse scratch clone with a stand-in aifoundry3 rebuilt from E163's committed
raw layout. v3's route reproduced E163's registered collection byte for byte, with no desk path. v2's route wrote the clone's absolute
path into 18 files, 2,457 times: wider than v3's README's one-pass "97 rows", and v3 covers all of it. v3.1 keeps every one of those
fixes. Its own end-to-end run repeats the byte-for-byte collection (§ The desk tests).

## Using v3.1

The steps, their arguments, their order, the times, the collection commands and the device-command policy are v1's
([`../README.md`](../README.md): "The steps", "The times", "Collect and score"). Call each step under `v3.1/`:

    bash tools/claims-v3/q141k-runbook/v3.1/<script> <args>

Use the same `RB_OUT` (this card day's own directory, outside the repo) and `RB_LOCK` (the file a login check is appended to). v3.1
reads the same box state as v1, v2 and v3 (`build/q141k/` under each tree), so a lane can switch at any step. The exit codes are v3's,
with two additions:
- 14 also covers a collection's check of C that did not finish;
- 16 also covers an output that is not there.

## For the next card day (carried from v3)

- **v3.1's steps still name E163-E169's kits.** A later card day's runs (E171 on) come with their own kits. Port each step to them as
  v1 ported the go checklist, and set `RB_BASE` to that day's kit commit. Keep these, and the gates:
  - `rb_common.sh`, `rb_run.py`, `nopath_q142s.py` and `ccdone_q142s.py`;
  - a `cc_gate` after every collector that checks C, naming the `--out` files it writes.
- **A run on `run_hpl.py`** installs [`../../hpl/watcher_q142s.py`](../../hpl/watcher_q142s.py) as its dated amendment says, and its
  kit's frozen hash list carries the file. This covers the next governed bursts, heat holds, GEMM and stride runs on aifoundry2, and
  card 0's on aifoundry1. v3.1 launches E163-E169's frozen runners, so v3.1 itself does not change which watcher runs.
- **Not done here: aifoundry2's housekeeping** (the card-half critic's next step 9). The backup tar, `stash@{0}` and the old
  `reduce_e77.py` copy in `~/claude/work` stay on the box, because this round touched no lab box. It is one bounded box step for the
  next lane on aifoundry2: our own files only.

## What it does to predicting power and heat

Nothing to any number: no frozen prediction, band, rule, stop, registration or verdict changes, and no new blind test is made. What it
keeps is that a blind test's power and heat scores are never collected on a check of C that did not finish. Such a check would have
left 17 of E163's 28 rules unscored and 5 of its C rules reading FAIL, under "collected and scored". The power model's blind error
(rank 1) and the per-tile C exclusions it rests on are then read only from runs whose C was checked to the end.

## Device commands sent

v3.1 sends no command of its own. A device-touching step only calls the kits' audited scripts on the box, and in step 9 E128's guard
with `config`, as v2 and v3 do. `ccdone_q142s.py` and `nopath_q142s.py` read files at the desk only.

[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt) has `dmcmd_audit.py` on v3.1's files with that guard scanned beside them: **GO, 11 send
sites, 0 disallowed, no allow-list, no exception**. Every one is a line of `e128/ettelem_guard.sh` and every command is READ, as for
v1, v2 and v3. Without the guard ([`logs/dmcmd-audit-bare.txt`](logs/dmcmd-audit-bare.txt)) it reads **NO-GO at exactly step 9's call**
(`v3.1/s09_a3_reads.sh:24`, 6 send sites), as v2's and v3's do.

## The desk tests

- [`selftest_runbook.sh`](selftest_runbook.sh) → [`logs/selftest.txt`](logs/selftest.txt): **589 of 589 checks pass** (302 s).
  - v1's cases A-F, v2's X1-X10 and v3's Y1-Y12 run against v3.1 (397 checks, as in v3), with v1 and v2 run beside them as v3's test
    did.
  - Z0-Z7 cover the verifier's findings, with v3 run beside each:
    - Z0, the gate on the card half's ten committed checks of C;
    - Z1, E163: a crash, a genuine C FAIL, a truncated file, a check of 0 launches;
    - Z2, E166's real collector: a crash, a finished check, an earlier try's file;
    - Z3, s13's exit 9 and a crashed `check_e164.py`;
    - Z4, a missing path, both in the gate and in `rb_nopath`;
    - Z5-Z7, the E164, E165 and E167 collections.
  - V checks that the 21 files v3.1 keeps from v3 are byte for byte v3's, and the 18 of them that v3 kept from v2 are v2's.
  - The stand-ins' sleeps are 3647 and 3648 s, so no other version's test's clean-up touches this one's.
- [`e2e_ccheck_q142s.sh`](e2e_ccheck_q142s.sh) → [`logs/e2e-ccheck.txt`](logs/e2e-ccheck.txt): the real collector, end to end, as above,
  in 228 s. It runs in a sparse scratch clone with stand-in boxes, never the lab clone. Its log records the sha256 of the four files it
  tests, which are the committed ones.
- [`list_steps.sh`](list_steps.sh) → [`logs/dry-listing.txt`](logs/dry-listing.txt): **50 of 50 steps exit 0**. A logging stand-in
  ssh and rsync first on PATH saw no call. Five of its lines are the new C gates (e163, e164, e165, e166, e167).
- [`logs/diff-v3-v3.1.txt`](logs/diff-v3-v3.1.txt): every change from v3, as a unified diff of each file v3.1 changes.
- [`logs/public-text-scan.txt`](logs/public-text-scan.txt): the public-text scan of this pass's new files, **CLEAN**.

All ran on the Intel through the round's local slots, one job at a time, at nice 10. The desk test, the dry listing and the scans each
used one core. The end-to-end run's C check used `collect_e163.sh`'s 2 jobs for about a minute. The runbook's collection step runs at
the desk by design: it needs this Mac's tree and Python. No batch work went to a lab box or the mini.

## Files

| file | what |
|---|---|
| `s22_collect.sh` | step 22: v3's, with `cc_gate` after every collection that checks C |
| `ccdone_q142s.py` | new: did each check of C finish? |
| `s13_a1_launch.sh` | step 13: v3's, with the launcher's exit 9 read as a refusal |
| `nopath_q142s.py` | the desk-path gate: v3's, with a missing path a hit |
| `rb_common.sh` | v3's, with `rb_nopath`'s message for a missing output, `_v3.1` step names and the listing's directory |
| `s01`-`s03`, `s05`, `s07`-`s12`, `s14`-`s20`, `rb_run.py`, `list_steps.sh`, `frozen26.py`, `anchors_e165.py` | v3's, byte for byte (case V). Their usage lines name v1's, v2's or v3's path; call them under `v3.1/` |
| `selftest_runbook.sh`, `e2e_ccheck_q142s.sh` | the desk tests |
| `logs/` | `selftest.txt`, `e2e-ccheck.txt`, `dry-listing.txt`, `dmcmd-audit.txt`, `dmcmd-audit-bare.txt`, `diff-v3-v3.1.txt`, `public-text-scan.txt` |

SPDX-License-Identifier: Apache-2.0
