# E180's kit, dated note 1: the adversarial verifier's kit faults fixed before any E180 datum - D1's other-user rule in the block and in the runner's check before every run, the telemetry guard, a sync that takes every harness file, the login check over every directory, the reported arms' reduction and scorer, and a disassembly walk of the accumulating sums (Q146(f); new files only)

*Fri 6 Nov 2026 (week 45), written about 03:35-04:00 PST on the Intel, desk only (Q146(f), lane `addfix-q146f`): no card was claimed, no
device command was sent, no lab box was reached, nothing was posted. It sits beside [KIT.md](KIT.md) (the kit, `c92f627b`, 01:40:21 PST),
which stays as committed, as does every file of its hash list and the registration's (55 and 71 OK). It follows the registration's
[dated note A1](E180.md.dated-note-A1.md) (`879197e3`, 03:34:44 PST; 41 OK), which it implements, and answers E180's adversarial verifier
(`addv-q146f`, 01:45-02:45 PST: holds with fixes, 3 major, 6 minor, 2 nits) on the kit's side: fault 1 (major), faults 5, 6 and 8, the build
half of nit 10, and nit 11. It is committed before any E180 datum: `git log --all` shows no `docs/reports/data/*e180*`.*

*Unlike E178's kit note, this one changes files the box runs: v1's block, runner, queue, session, preflight and harness are replaced by v2
files (v1's stay as committed, for the record), because fault 1 lives in them. No registered rule, threshold, plan, order or forecast
changes; the scorer's registered readings are v1's code on v1's reduction, and A1's rules and reported arms are added beside them.*

## In short

- **Fault 1 is fixed.** v1's block and runner used lib.sh's stock other-user test, which counts every login `who` lists; aifoundry3's
  standing idle logins would have stopped E180 at its first block. v2 applies **D1** (E178's and E171's rule, verbatim, in one file both
  call): an idle login does not block; another user on this card, another user's device process or an unreadable et-holders does, at
  the block and **before every run**. Desk test outside V3_DRY, with stand-in `who`, `ps` and `sudo`: **13 of 13**.
- **The telemetry guard** (E171's and E178's change 6) is in the v2 block; **the sync** takes every file the harness names (the E174
  class); **the login check reads every directory** of the output; the box build's **disassembly walk** of the accumulating loop is
  recorded for A1-7.
- **The checks:** DRY-INTEL-V2 **24 of 24**; the runbook's v2 desk test **26 of 26**; the scorer's v2 self-test **7 of 7** (v1's rules
  identical on all 90 readings); the disassembly walk's test **9 of 9** on a real committed objdump listing; `dmcmd_audit` **GO**, 32 sites,
  every one READ; HARNESS OK, 86 files (v2).
- **Card-minutes, the plan and the stops are unchanged** (FULL about 43, cap 50). One cost: the check before every run now calls
  et-holders through `sudo -n` (about 300 times in a FULL session), as the block does before its sampler.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md and MAP.md section 3, read Fri 6 Nov 2026 about 03:00-03:10 PST. Public rows read: H24, H25,
   H27, H28, L20, L21; MAP rows 5 and 41. The row ids are opaque pointers into a private file.
2. **Used** (each unchanged, sourced, called, imported or followed by path; sha256 in [`SHA256SUMS-e180-kit-note1`](SHA256SUMS-e180-kit-note1)):
   - **D1, the other-user rule** (`tools/claims-v3/e178/block_e178.sh` lines 35-50 with its comment 32-34, `a4aafc6f`; the same text in
     `tools/claims-v3/e171/block_e171.sh` lines 34-49, `1b80da20`), copied verbatim into [`others_d1_e180.sh`](others_d1_e180.sh) (a diff
     against both reads identical). *Check against the same operation on the same box:* E171 ran this function on aifoundry3 on 5 Nov
     2026 with other users' idle logins present (the card day critic: 5 idle terminals, no block), and E176 the same evening.
   - **E128's telemetry guard and its self-test** (`tools/claims-v3/e128/ettelem_guard.sh`; `selftest_e128.py` `guard_checks`,
     `07b82303`): change 6 of E171 and E178, as v2's change 3. *Check:* E171's and E178's blocks set it the same way (their lines 30-31).
   - **E178's kit note 1** (`763307e7`): its sync v2's form (`sync_paths_e178.py`, `rb/s07_a3_sync_e178_v2.sh`) for
     [`sync_paths_e180.py`](sync_paths_e180.py) and step 7 v2, and its tree-wide login check, **`scrub_tree_e178.py`, used unchanged** (it
     imports E164's `scrub_etwho_e164.py`, `45aeda12`, whose patterns already read D1's and lib.sh's others-present lists).
   - **E61's objdump walk** (V3-DTF, L21: `tools/claims-v3/dtf/check_elf.py`, `d0d68abb`, run as a gate on all three boxes' builds on
     21 Oct 2026, `docs/reports/data/2026-10-21-dtf/proof/elfcheck-aifoundry*.txt`, and the toolchain's objdump at the path its
     `block.sh` used) for [`check_elf_e180.py`](check_elf_e180.py); its committed aifoundry2 listing
     (`docs/reports/data/2026-10-21-dtf/proof/enercat-df-aifoundry2.dis.txt`, `7eb1ec79`) as the desk test's real input. *Check:* the
     port finds the registered mode 160's loop in that listing once (64 ops, 72 instructions), as E61's check found its own modes.
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`, `9a2630ff`) through `rb/rb_e180.sh`, unchanged; **E180's kit v1**
     (`c92f627b`), file by file where v2 replaces it; **E180's dated note A1** (`879197e3`): the reported arms, rules A1-1, A1-5 and A1-7,
     and their frozen inputs (`footing-e180-a1.json`, `offset-e180-a1.json`).
   - **The catalogue's reduction** (`workloads/enercat/analyze_catalogue.py`), imported unchanged by v2's reducer, and **the anatomy's rule
     A** (`877e7476`, `posthoc_note1_q145a.py` `burst_rises`), ported line for line into `reduce_e180_v2.py`, checked by the self-test's V6.
3. **Not used:**
   - run_e78.py's per-run check (`others_on_card`, ps only on aifoundry3: E178's runner): E180's runner applies the block's own D1 before
     every run instead, so the two checks are one rule.
   - A free in-session die-rise coefficient (A1 section 4.3) and Q136(b)'s footing B (A1's Builds on, Not used).
   - E172's card-1 kit: still owed, as KIT.md says.
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it. The logins, uids and pids
   in the desk tests are made up.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. D1's other-user rule, in the block and before every run (fault 1, major)

**The fault.** `block_e180.sh` lines 18 and 82 call lib.sh's stock `others_present`, which with no V3_DEVICE counts every other user `who`
lists (lib.sh lines 62-79), and `run_e180.py` runs the same stock function in a fresh shell before every run. aifoundry3 carries two other
lab users' standing idle logins, so the session's stop-path block 18002 would have exited 3 at line 18: no smoke, no pass, the window and
the day's post wasted (it fails closed: nothing beyond the config reads opens the card). V3_DRY stubs the test (lib.sh line 213), so v1's
DRY-INTEL, the box's dry pass and the runbook's desk test could not see it.

**The fix, new files:**
- [`others_d1_e180.sh`](others_d1_e180.sh): D1's case block, verbatim from E178's and E171's blocks. Sourced after lib.sh; outside a dry
  run it replaces the stock test on aifoundry3 and aifoundry1's cards.
- [`block_e180_v2.sh`](block_e180_v2.sh): v1's block with D1 sourced (change 1), its runner v2 (change 2), the telemetry guard (change 3,
  section 3) and v2's harness check (change 4). It also exports V3_DEVICE when set, so the runner's check reads the same card.
- [`run_e180_v2.py`](run_e180_v2.py): v1's runner with one change: its check before every configuration runs lib.sh plus
  `others_d1_e180.sh`, the block's own function, and a check that fails to run at all counts as someone present (v1 logged it and went
  on). `--check-others` runs the check once for the desk test.
- [`session_e180_v2.sh`](session_e180_v2.sh) and [`queue_e180_v2.sh`](queue_e180_v2.sh): v1's, calling the v2 files.

**The desk test** ([`selftest_others_e180_v2.sh`](selftest_others_e180_v2.sh), [`logs/selftest-others-e180-v2.txt`](logs/selftest-others-e180-v2.txt);
13 of 13), outside V3_DRY, in a scratch tree, with stand-ins for `hostname`, `who` (two idle logins), `ps` and `sudo -n
/usr/local/sbin/et-holders`; each case through the three call paths (the sourced function, the runner's `--check-others`, the block):

| case | D1 | runner | block v2 |
|---|---|---|---|
| U1 two other users' idle logins only | no one | 0 | passes the test (stops at its preflight: no build in the tree) |
| U1' the same, lib.sh's stock test and v1's block | someone present | - | **v1 exits 3: the fault, shown** |
| U2, U3 another user holds card 0's node, or its lock | present | 3 | 3 |
| U4, U5 another user's device process; a CI job | present | 3 | 3 |
| U6 et-holders unreadable | present (fails closed) | 3 | 3 |
| U7 our own holder line; U8 another user on card 1's node only | no one | 0 | passes the test |

- **R1:** a 47-run pass of the runner, non-dry, with a stub host, the idle logins present: every run is checked and run, "done".
- **R2:** another user's device process appears after the third run: the pass stops before the fourth (exit 3), and run.log records
  `others present: ... procs=[1001:6666:sparsity_host ] holders=[]`.
- **S1:** that run.log through `scrub_tree_e178.py --check` is caught (the uid), and after the rewrite reads 0 left (section 4).

## 2. The reduction and the scorer, v2 (the registration's dated note A1 sections 1, 4, 5 and 7)

- [`reduce_e180_v2.py`](reduce_e180_v2.py) runs v1's reduction first and returns its every field unchanged (each kind's D, the kept runs,
  the set-aside passes), then adds A1 section 4.1's per-burst readings for the same kept bursts, from the same telemetry and
  `bursts_of`: `rise`, `D_FL1`, `D_E60`, `R_raw` and **`R`, the net minion rail on footing A**.
- [`score_e180_v2.py`](score_e180_v2.py) scores every registered rule with v1's `score_e180.score` on that D, then adds:
  - **A1-7:** the box's `elfcheck-e180.txt` (section 5): FAIL for mode 261 makes E180-A NOT SCORED (v1's record kept beside); UNREAD or
    no file labels it "walk not verified"; PASS "walk verified by disassembly";
  - **A1-5:** E180-A's SIZE read against P's hart-offset band (+0.752 to +4.261 W): "not separated from the harts' start offset" when the
    interval meets the band and SIZE is not PASS; its arm reading "not a price test";
  - **A1-1:** E180-L flagged footing-limited when P's slope sits within 0.002 W a bit of either end of its interval;
  - **A1's reported arms RA1-RA5 and the die rise per kind**, each with its 95% interval and where each frozen forecast sits.
- [`collect_e180_v2.sh`](collect_e180_v2.sh): v1's collector with the two v2 programs and `--elfcheck logs/elfcheck-e180.txt`.
- **The self-test** ([`selftest_score_e180_v2.py`](selftest_score_e180_v2.py), [`logs/selftest-score-e180-v2.txt`](logs/selftest-score-e180-v2.txt);
  7 of 7; it needs /usr/bin/python3, with numpy):
  - **V1:** on v1's own synthetic sessions (10 truths and cases), every registered rule reads as v1's: 90 of 90 readings identical;
  - **V2:** the reported arms read P inside on the rail and on each footing, and C above;
  - **V3:** A1-7's three readings and the 262 mark;
  - **V4:** A1-1 flags an L interval P sits 0.0016 W a bit under, and not one P sits mid in (half-width 0.0047);
  - **V5:** A1-5's reading of an A truth 1.3 x P's;
  - **V6:** raw passes through `reduce_e180_v2.py`, with a flat die (v1's fields unchanged; D_FL1 = D_E60 = D, R = R_raw = the rail's rise /
    0.94 to 1e-14) and with a die that steps up in each burst (the footing algebra to 4e-15 W; R_raw - R = 0.81 k21 x the filtered rise /
    0.94 exactly; the filtered rise 0.82 of the step).

## 3. The telemetry guard (fault 6)

`block_e180_v2.sh` sets `ETTELEM=tools/claims-v3/e128/ettelem_guard.sh`, so the sampler, `die_c` and `clock_mhz` reach the reader only as
`ettelem sample --seconds <n> --every-ms <n>`, and replaces lib.sh's `drain_mgmt` with a refusal, so `dev_mngt_service` (GET_MODULE_POWER) is
never run: E171's and E178's change 6, as E153's change 5. v1's block also skipped the drain on card 1 only; v2 refuses it everywhere.
Its preflight checks the reader the guard execs (`build/ettelem/ettelem`) beside the guard. DRY-INTEL-V2's new check 1d reads it from the
files: the guard set, the drain a refusal, the session's config reads through the guard, no direct reader call in the block or runner.
The guard's own refusals (`--reset-ms`, any word but config and sample) are E128's `selftest_e128.py` `guard_checks`. The audit reads GO
as v1's did (32 sites, every one READ).

## 4. The sync takes every harness file; the login check reads every directory (faults 8 and 5)

**The harness, v2:** [`make_harness_e180_v2.py`](make_harness_e180_v2.py) writes [`harness-e180-v2.json`](harness-e180-v2.json), 61 files: v1's
56 less the five v2 replaces (block, preflight, queue, runner, session) plus the ten the v2 session runs or reads (the v2 files, D1's file,
`check_elf_e180.py`, A1 and its hash list). [`check_e180_v2.py`](check_e180_v2.py) checks it (v1's image and binaries checks, imported):
HARNESS OK, 86 files with the 25 images ([`logs/harness-check-v2.txt`](logs/harness-check-v2.txt)).

**The sync, v2** ([`rb/s07_a3_sync_e180_v2.sh`](rb/s07_a3_sync_e180_v2.sh), with [`sync_paths_e180.py`](sync_paths_e180.py)): v1's two
paths plus every other file harness-e180-v2.json names, read from the harness itself, so step 8's check and the sync agree by construction.
That adds the four v1 never sent: lib.sh, E128's guard, `dmcmd_audit.py` and its table. As in E178's v2:
- uncommitted changes refuse (16);
- nothing is synced unless the lab clone's harness files read at their sha256 (16), since v2 sends shared files v1 left alone.

Desk cases in [`rb/selftest_rb_e180_v2.sh`](rb/selftest_rb_e180_v2.sh) (a scratch git repository and a stand-in box):
- **S2:** v1's rsync alone leaves out exactly those four files, the fault shown;
- **S1:** v2's rsync alone builds a tree holding every harness file at its sha256, and in that tree, with stub binaries and V3_DRY,
  `check_e180_v2.py` reads HARNESS OK, the preflight GO, pass 18010 runs its 47 configurations through the E180 host, the session's start
  gate exits 8, and no network call is made;
- **S3, S4:** an uncommitted, then a committed, change to lib.sh: 16, and no rsync.

**The login check, v2** ([`rb/s22_collect_e180_v2.sh`](rb/s22_collect_e180_v2.sh)): `scrub_tree_e178.py --check` over every directory of the
output, after the desk-path gate, in place of v1's E164 check of `logs/` alone. The pass directories' `run.log`, where the runner writes
D1's others-present line when it stops a pass, was read by nothing in v1.
- **P1:** that line, with another account's uid and login, in a pass directory: 16.
- **P2:** the owner's own et-who holder line: 0.
- **P3:** v1's step 22 on P1's layout: 0, the hole.
- **P4:** the rewrite the stop message names, then `--check`: 0 left, the line kept with the uid and login withheld.

## 5. Do the accumulating sums walk? The build's disassembly walk (nit 10)

[`rb/s08_a3_build_e180_v2.sh`](rb/s08_a3_build_e180_v2.sh) adds one reported step to v1's build job, after `build_e180.sh`:
- the box's kernel is disassembled with the toolchain's objdump (`/opt/et/bin/riscv64-unknown-elf-objdump`, E61's) into
  `build/e180-kernel-dis.txt`;
- [`check_elf_e180.py`](check_elf_e180.py) walks modes 261 and 262 (and 160, a control) into `build/e180/elfcheck-e180.txt`, which step
  22 v2 copies back with the session's logs.

It is not a gate of the build step: its parse of the two new modes has never met the box's own listing. A1-7 reads it at scoring.

**The walk** is E61's check ported. Unchanged from E61's: its parse, its register names, the 64-op body found once, the loop's backward
branch within 30 instructions, and no other f-register instruction in the loop. Added for the sums, which must persist across the loop:
- the zeroing block (`fxor.pi f8..f15, f0, f0`) is found before the loop and outside it;
- no instruction writes f8-f15 between that block and the loop;
- no call is made inside the loop.

A reading is FAIL only when the body is found and one of these fails; UNREAD when the listing cannot answer.

**Its test** ([`selftest_elf_e180.py`](selftest_elf_e180.py), [`logs/selftest-elf-e180.txt`](logs/selftest-elf-e180.txt); 9 of 9) runs on the
committed real listing:
- E0: 261 and 262 are absent from it (UNREAD), and the control finds mode 160's loop once;
- E1 and E2: 261's and 262's forms built from that real loop, with the zeroing block where 261's source puts it: PASS;
- E3-E5: a write to f9 inside the loop, a write to f10 before it, a call inside it: FAIL;
- E6, E7: no zeroing block, or the body twice: UNREAD;
- E8: a trailing rounding-mode operand: PASS.

That real listing shows the compiler saving and restoring fs0 and fs1 (f8 and f9, callee-saved in the ABI) around each case. In E1 they sit
before the zeroing block, as they must; one between the block and the loop would read FAIL.

## 6. The runbook as it now runs (KIT.md's box steps)

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window | `rb/s02_window_e180.sh` | no |
| 2, the desk check | **`rb/s03_desk_e180_v2.sh`** | HEAD descends from `879197e3` (A1); four hash lists, each with its count: 71, 55, A1's 41, this note's 90; harness v2 |
| 3, the post | (the card lane's) | no |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no |
| 5, the sync | **`rb/s07_a3_sync_e180_v2.sh`** | section 4 |
| 6, the build and the checks on the box | **`rb/s08_a3_build_e180_v2.sh`** | v2's harness and preflight; the disassembly walk (section 5); job `a3-build-e180-v2` |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the V3_DRY pass on the box | **`rb/s10_a3_dry_e180_v2.sh`** | v2's block and session; job `a3-dry-e180-v2` |
| 9, the session | **`rb/s11_a3_session_e180_v2.sh`** | launches `session_e180_v2.sh`; needs the two v2 jobs ended rc 0 today |
| 10, the wait | **`rb/s20_wait_e180_v2.sh`** | looks for `session_e180_v2.sh` by name |
| 11, release, then collect | **`rb/s22_collect_e180_v2.sh`** | section 2's collector and section 4's login check |

- **Why step 10 needed a v2.** v1's wait looks for `session_e180\.sh`, which does not match the v2 session's name, and would read it as
  gone. Desk case W3 shows v1 exiting 14 on a running v2 session; W2 shows v2 reading 17, "call again".
- **Why step 9 needs v2's jobs.** Desk case G4: with v1's dry pass and build ended rc 0 today but not v2's, step 11 v2 refuses (10) and
  launches nothing.
- **The rest of the desk test.** Every v1 case passes on the v2 steps: the dry listing; a login link, a silent probe, a launch past its
  bound; no window, past the last start, no jobs today; no offset; a failed gate; the collection's four cases; the stand-in refusal.
- [`rb/list_steps_e180_v2.sh`](rb/list_steps_e180_v2.sh) is the dry listing ([`logs/dry-listing-e180-v2.txt`](logs/dry-listing-e180-v2.txt):
  0 steps fail, no network call).
- k6's `ours_live` counts `session_e180_v2.sh` and `queue_e180_v2.sh` by the lab's naming rule (`(queue|session)_e[0-9]+[a-z0-9_]*`), so one
  session of ours at a time still holds.

## 7. The checks after the fix ([`logs/reruns-note1.txt`](logs/reruns-note1.txt))

| check | result |
|---|---|
| the hash lists: the registration's, the kit's, A1's | 71, 55, 41 OK |
| plan and forecasts `--check`; v1's harness `--check` and HARNESS OK 81 | PASS, unchanged |
| v1's scorer self-test under /usr/bin/python3 | 12 of 12, identical to its committed log |
| the same under the PATH python3 (3.13, no numpy) | 10 of 12: nit 11's case, now named (section 8) |
| `make_harness_e180_v2.py --check`; `check_e180_v2.py harness` | CHECK PASS; HARNESS OK, 86 files (v2) |
| the Intel dry pass, v2 ([`logs/dry-intel-v2.txt`](logs/dry-intel-v2.txt)) | DRY-INTEL-V2 PASS, 24 of 24 (v1's 23 on the v2 files, and 1d) |
| D1's desk test | 13 of 13 |
| the scorer's v2 self-test | 7 of 7 |
| the disassembly walk's test | 9 of 9 |
| the runbook's v2 desk test ([`logs/selftest-rb-e180-v2.txt`](logs/selftest-rb-e180-v2.txt)) | 26 of 26 |
| `dmcmd_audit`, the v2 session's files ([`logs/dmcmd-audit-v2.txt`](logs/dmcmd-audit-v2.txt)) | GO, 32 send sites, 0 disallowed, every one READ |
| the same without E153's exception ([`logs/dmcmd-audit-noexcept-v2.txt`](logs/dmcmd-audit-noexcept-v2.txt)) | NO-GO only at lib.sh:154 (the statistics reset, never sent) |
| the v2 and A1 desk files ([`logs/dmcmd-audit-desk-v2.txt`](logs/dmcmd-audit-desk-v2.txt)) | GO, 0 send sites |
| the v2 runbook steps with k6's steps 5 and 9 ([`logs/dmcmd-audit-rb-v2.txt`](logs/dmcmd-audit-rb-v2.txt)) | GO, 11 send sites, all E128's guard's |

None of the new files sends a device command beyond v1's set; none names the firmware-revisions query, `--reset-ms`, a SET or a residency
read. The objdump the build step runs reads a file; it opens no device.

## 8. KIT.md's and A1's words, corrected

- **Nit 11.** KIT.md's self-test line: the scorer's self-test needs a python3 with numpy (S9 and S10 import analyze_catalogue). On the
  Intel that is **/usr/bin/python3**, as step 22 already sets.
- **KIT.md's "an idle login does not block (D1)"** was not true of v1's files. It is true of v2's (section 1).
- **KIT.md's "lib.sh's look ... `others_present` before every run"** (the runner's protocol) reads, for v2, D1's rule before every run.
- **A1 section 7** calls the objdump walk "E60's `tools/claims-v3/dtf/check_elf.py`". It is **E61's** (V3-DTF, the one-gate experiments,
  21 Oct). So A1's "Not used" line for L21 (E61) holds for the registration, and the kit now uses L21's check (above).

## 9. Labels

- **Registered** (before any E180 datum): every rule, threshold, plan and forecast of E180.md (`4dc5035f`) and dated note A1 (`879197e3`),
  unchanged; this note adds no rule, and implements A1's.
- No E180 datum exists, so nothing here is blind, held out or post hoc for E180. The desk tests' outputs are plumbing on synthetic or
  committed inputs; none is a forecast or a verdict.

## 10. Files, the hash list, compute; what remains open

- **New files (40, and the hash list):**
  - this note;
  - the box files `others_d1_e180.sh`, `block_e180_v2.sh`, `run_e180_v2.py`, `queue_e180_v2.sh`, `session_e180_v2.sh`, `check_e180_v2.py`,
    `preflight_e180_v2.sh`, `check_elf_e180.py`, `harness-e180-v2.json`;
  - the desk files `make_harness_e180_v2.py`, `sync_paths_e180.py`, `reduce_e180_v2.py`, `score_e180_v2.py`, `collect_e180_v2.sh`;
  - the tests `selftest_others_e180_v2.sh`, `selftest_score_e180_v2.py`, `selftest_elf_e180.py`, `dry_intel_e180_v2.sh`;
  - the runbook steps `rb/s03_desk_e180_v2.sh`, `rb/s07_a3_sync_e180_v2.sh`, `rb/s08_a3_build_e180_v2.sh`, `rb/s10_a3_dry_e180_v2.sh`,
    `rb/s11_a3_session_e180_v2.sh`, `rb/s20_wait_e180_v2.sh`, `rb/s22_collect_e180_v2.sh`, `rb/list_steps_e180_v2.sh`, `rb/selftest_rb_e180_v2.sh`;
  - the logs `logs/selftest-others-e180-v2.txt`, `logs/dry-intel-v2.txt`, `logs/selftest-score-e180-v2.txt`, `logs/selftest-elf-e180.txt`,
    `logs/selftest-rb-e180-v2.txt`, `logs/dry-listing-e180-v2.txt`, `logs/dmcmd-audit-v2.txt`, `logs/dmcmd-audit-noexcept-v2.txt`,
    `logs/dmcmd-audit-desk-v2.txt`, `logs/dmcmd-audit-rb-v2.txt`, `logs/harness-check-v2.txt`, `logs/reruns-note1.txt`.
- **[`SHA256SUMS-e180-kit-note1`](SHA256SUMS-e180-kit-note1), 90 entries:** these 40 and the 50 committed files they source, call, import,
  replace or read, each unchanged. Box step 2's v2 checks it. Check it from the repository's root:
  `shasum -a 256 -c tools/claims-v3/e180/SHA256SUMS-e180-kit-note1`.
- **Compute:** every check ran here through the round's local slot (`slot.sh`), one job at a time at nice 10 and one core, 03:36-03:52
  PST (the times are in `logs/reruns-note1.txt`). No bench, mini, lab box or card was used for the kit. The tests ran in this lane's
  scratch, never in the lab clone, and their trees were removed by literal path.
- **Open, for the readiness critic and the records:**
  1. A readiness critic of `879197e3` and this commit. Card time only on his go and fresh aifoundry3 approvals.
  2. The E180 build has never been compiled on a box (KIT.md open item 2, unchanged), and neither has the disassembly walk met the box's
     own listing: step 6 v2 prints its line, and A1-7 reads it.
  3. aifoundry1 card 1, the fallback: v2's block keeps v1's `V3_DEVICE=1` path (D1 reads card 1's holders there), but no card-1 runbook
     exists.
  4. The october-forecast-model freeze (E180.md section 8) is not committed.
  5. The records quote E180-H's power as A1 section 2 says: 0.37-0.88, about 0.75 at the debiased noise.

SPDX-License-Identifier: Apache-2.0
