# E182's kit, dated note 1: the verifier's faults fixed before any E182 datum - the registered fallback runs end to end (steps 8, 10, 11 and 22 v2), the train host is built from exactly its pinned inputs, which step 7 v2 now sends (the E174 class), and the train runner's own stop check is tested live at the desk (Q153; new files only)

*Sat 7 Nov 2026 (week 45), written about 15:35-16:45 PST on the Intel, desk only (Q153, lane `fix-e182`): no card was claimed, no device
command was sent, no lab box or mini was reached, nothing was posted. It sits beside [KIT.md](KIT.md) (the kit, `41865c18`, 14:29:57 PST),
which stays as committed, as do the registration ([E182.md](E182.md), `58b88850`) and every file of their hash lists (32 and 79 OK after
this note). It answers the kit's adversarial verifier (`verify-e182`, 14:38-15:15 PST today: holds with fixes, 2 major, 7 minor): majors 1
and 2, minor 7 and the kit's words in minor 9. The registration's minors are [E182.md.dated-note-1.md](E182.md.dated-note-1.md). Both are
committed before any E182 datum. **No rule, forecast, threshold, statistic or registered power figure changes, and no file the session
runs changes:** `harness-e182.json` is unchanged (66 desk files, 73 on the box with the train host). What it adds: v2 files for runbook
steps 3, 7, 8, 10, 11 and 22 and the dry listing (section 4), a v2 build of the train host and the pins it reads (section 2), and three
desk tests (sections 1-3).*

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** KIT.md's block (INVENTORY.md read 13:30 PST); this note re-read INVENTORY.md's rows for the pieces it takes, Sat 7 Nov 2026
   about 16:05 PST: H07, H08, H24, H27, H28. The row ids are opaque pointers into a private inventory.
2. **Used** (each unchanged, called, sourced or imported by path; sha256 in [`SHA256SUMS-e182-note1`](SHA256SUMS-e182-note1)):
   - **E182's kit** (`41865c18`): every v2 step is its v1 file with the changes its header lists; `sync_paths_e182.py`, `check_e182.py`,
     `patch_host_e182.py`, `block_e182.sh`, `session_e182.sh`, `run_e182t.py` and `run_e182.py`, unchanged.
   - **E178's kit note 1** (`763307e7`, H27): its form for a kit note, its v2 sync ("gate and sync agree by construction, tested in a tree
     built from the sync list alone") and its rule "run step 5 once more, then step 6; if it reads wrong again, stop".
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`; v3.1's `rb_run.py`, H24) through `rb/rb_e182.sh`, unchanged.
   - **Q139(k)'s mock runtime** (`tools/claims-v3/ccheck/mockrt/`, H08) and **`desktest_host_e182.sh`'s compile line**: the desk build of the
     train host from the synced copy (section 2).
   - **E171's stops** (65 W, 70 C; H24, H28) as `e182_common.stops()` gives them, read, not changed.
   - **The workload's build** (`workloads/sparsity/`, unchanged since 28 Sep 2026; H07's runs built from it): which files it reads (section 2).
   *Check against the same operation:* the C-logging host on aifoundry3 (`build/ccheck/b/host/sparsity_host`, E178's box binary) was built by
   `build_host_ccheck.sh` with the same configure and target as the train host, so the box's cmake path is the one E178 ran on.
3. **Not used:** E172's card-1 kit; E180's and E184's kits' code; the PVT sampler (as KIT.md).
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

KIT.md's box steps are named by their numbers there (1 the window, 2 the desk check, 5 the sync, 6 the checks on the box, 8 the dry pass,
9 the session, 11 the collection); the files are `rb/s02`, `s03`, `s07`, `s08`, `s10`, `s11` and `s22`.

## 1. The registered fallback now runs through the runbook (the verifier's major 1)

**The fault.** KIT.md box step 6 says that if the train host's build fails, the day runs PASSES: step 6 again with `--no-trains`, then step 9
with `PASSES no`. Two steps in between could not do it:
- v1's dry pass (`rb/s10_a3_dry_e182.sh`) always dry-runs train block 18215 and the smoke with the trains on. `block_e182.sh`'s preflight
  needs the train host even under V3_DRY, so both exit 2, the dry job ends 1, and v1's step 9 refuses ("has not ended rc 0 today").
- v1's collection (`rb/s22_collect_e182.sh`) names `aifoundry3:aifoundry/build/e182host/SHA256` in its second rsync. After a build that never
  succeeded there is no such file, rsync exits 23, and the step dies before the collector.

**The fix, four v2 steps** (v1's files stay as committed):
- [`rb/s10_a3_dry_e182_v2.sh`](rb/s10_a3_dry_e182_v2.sh) `start|wait [--no-trains]`. With the trains it is v1's job, `a3-dry-e182`. With
  `--no-trains` it runs job `a3-dry-e182-nt`: 18220, the smoke with `E182_TRAINS=no`, and the start gate with `E182_PLAN=PASSES
  E182_TRAINS=no` (8). It runs no train block and needs no train host.
- [`rb/s11_a3_session_e182_v2.sh`](rb/s11_a3_session_e182_v2.sh) `FULL yes | PASSES no`. It reads the dry job its plan needs: FULL yes needs
  `a3-dry-e182`; PASSES no needs `a3-dry-e182-nt` (or `a3-dry-e182`). FULL no and PASSES yes are refused (10) before any call.
- [`rb/s22_collect_e182_v2.sh`](rb/s22_collect_e182_v2.sh) first reads which of its six sources the box holds, then copies only those. The
  session logs are required (14 without them). With no block, smoke or stop test it stops (16: nothing to collect). Each absent source is
  named, box-relative, in `build/e182-raw/logs/absent-on-box.txt`; the collector copies that file into the output's `logs/`, so the data
  README can say the build record is absent and why. Everything after the copies is v1's.
- [`rb/s08_a3_preflight_e182_v2.sh`](rb/s08_a3_preflight_e182_v2.sh) (section 2) names the fallback's three v2 steps in its stop message.

**The fallback, as it now runs:** step 6 v2 reads TRAIN-HOST-BUILD-FAILED (16) -> step 6 v2 `--no-trains` (HARNESS OK 70) -> step 8 v2
`start --no-trains`, then `wait --no-trains` -> step 9 v2 `PASSES no` -> steps 10 and 11 (v2's collection). Every train rule reads NOT
SCORED, as registered (E182.md section 7). Cap 40 card-minutes, the post `for 1 h`.

**The desk cases** ([`rb/selftest_rb_e182_v2.sh`](rb/selftest_rb_e182_v2.sh), fake ssh and rsync, a stand-in box; section 5):
- **F1:** the build fails (a stand-in cmake told to fail): step 6 v2 exits 16, its message names the three v2 steps, and the box holds no
  train host and no build record (v2's build removes an earlier one first).
- **F2:** on that box, step 8 v2 `start --no-trains` then `wait --no-trains`: the job ends rc 0 (18220 rc 0, the smoke with the trains off
  rc 0, the start gate 8), with no network call from the box. **F2v**, the fault shown: v1's step 8 on the same box ends 14 (18215 rc 2),
  and v1's step 9 `PASSES no` then refuses (10).
- **F3:** step 9 v2 `FULL no` refuses (10, no call); `FULL yes` is refused on the box (10: the trains' dry job ended 1); `PASSES no` is
  launched (0), and the stand-in session then stops at its own harness check (the stand-in binaries), opening nothing.
- **F4:** step 11 v2 after the failed build: both copies exit 0, `build/e182host/SHA256` is named absent, and the session and build logs are
  copied. The step then reaches the C-session gate, which stops it (14) because the stand-in raw tree holds no C log, by design: the copies
  are what is tested. **F4v**, the fault shown: v1's step 11 on the same box dies at its logs' copy (14). **F4c:** with a build record on
  the box, v2 copies it. **F4d:** with no block, smoke or stop test on the box, v2 stops (16) before any copy.

## 2. The train host is built from exactly its pinned inputs, which the sync sends (major 2, the E174 class)

**The fault.** `build_host_e182.sh` copies all of `workloads/sparsity/` on the box and runs cmake. Of the 13 committed files there, only
`host/main.cpp` was pinned (`harness-e182.json`) or synced. On aifoundry3 the rest came from an older tree, unpinned, and no test built the
host from what step 5 sends.

**What the build reads** (from the files' own text; [`make_harness_e182_note1.py`](make_harness_e182_note1.py) asserts every clause): the
top `CMakeLists.txt` builds `kernel/` as an ExternalProject and adds `host/`, and `sparsity_host` depends on `sparsity_kernel`, so the build
compiles the kernel too; `host/CMakeLists.txt` configures `host/Constants.h.in` and compiles `host/main.cpp` with the workload's top directory
included; `kernel/CMakeLists.txt` compiles `kernel/sparsity.c` and `kernel/crt.S` with `kernel/sections.ld`; `host/main.cpp` and
`kernel/sparsity.c` include `sparsity_args.h`; no other local include. That is **8 files beside main.cpp**. The other 4 committed files
(README.md, analyze.py, run_energy.py, run_lab.sh) are not read. The maker refuses unless git's list of the workload is exactly these 13.

**The fix:**
- [`harness-e182-note1.json`](harness-e182-note1.json): the 8 build inputs' sha256 and note 1's two box files'. main.cpp stays pinned by
  `harness-e182.json`.
- [`check_inputs_e182.py`](check_inputs_e182.py): the 10 files at their pins in a tree (NOTE1 FILES OK: 10 files), or a build's copy holding
  exactly the 9 inputs at their pins and nothing else (BUILD INPUTS OK: 9 files).
- [`build_host_e182_v2.sh`](build_host_e182_v2.sh): v1 with three changes. It checks the tree's inputs first; it copies exactly the 9
  (`check_inputs_e182.py --list`) and checks the copy before the patch; and it removes an earlier build record with `src/` and `b/`, so a
  failed build leaves none. The patch, cmake, the record's form (check_e182.py reads it unchanged) and the binary's strings are v1's.
- [`rb/s07_a3_sync_e182_v2.sh`](rb/s07_a3_sync_e182_v2.sh): v1's sync list (read from harness-e182.json by `sync_paths_e182.py`) **plus**
  every file of harness-e182-note1.json, read by the same tool, unchanged. Gate and sync agree by construction: 40 paths. Uncommitted
  changes in any of them refuse (16), and nothing is sent unless the lab clone reads HARNESS OK 66 and NOTE1 FILES OK 10. The rsync is v1's
  form with `-i`: the step reports any workload file whose content it sent. Such a file means the box held another copy until then. Its new
  copy is the committed one; step 6 v2 checks it before the build, and the smoke's train gate and the desk's check of C judge the host.
- [`rb/s08_a3_preflight_e182_v2.sh`](rb/s08_a3_preflight_e182_v2.sh): with the trains, `check_inputs_e182.py` first. If the inputs differ,
  nothing is built and an earlier build's host, copy and record are removed: TRAIN-HOST-INPUTS-DIFFER (16), "run step 5 v2 once more, then
  this step; if they differ again", the fallback (E178's kit note 1 rule). Then `build_host_e182_v2.sh`, then v1's checks (HARNESS OK 73,
  or 70 with `--no-trains`, which runs no input check and no build).

**The desk cases** (section 5):
- **S1:** step 5 v2's rsync alone builds the box tree. It holds all 66 non-built files of harness-e182.json and all 10 of
  harness-e182-note1.json at their sha256. There, `build_host_e182_v2.sh` runs with a stand-in cmake ([`rb/fake_cmake_e182.sh`](rb/fake_cmake_e182.sh))
  that refuses unless the copy holds the 9 inputs, then **compiles the copy's patched main.cpp, with the copy's `sparsity_args.h`, against
  Q139(k)'s mock runtime**. It reads BUILD OK, the copy is exactly the 9 pinned inputs, and the record names the registered patched source.
  `check_e182.py` on the box's terms then differs only in the four stand-in box binaries: the train host's source, record and binary agree.
  In V3_DRY that tree reads HARNESS OK 66, NOTE1 FILES OK 10, GO, 0 problems, the three V3_DRY blocks with the host the build made
  (18220: 70 launches; 18215: 4 anchors and 64 processes; the smoke 10 and 2), the start gate 8, and no network call.
- **S3:** an uncommitted change in `lib.sh`, then in `sparsity_args.h`: 16 each, no rsync.
- **F1b:** a build input changed on the box: step 6 v2 reads TRAIN-HOST-INPUTS-DIFFER (16) and builds nothing, removing S1's build first.
  Step 5 v2 again sends exactly that file and names it.
- What the desk cannot do: the real configure and build need the box's SDK and RISC-V toolchain. The kernel's three sources are checked
  present and pinned, and the kernel is not compiled at the desk. The first real compile is still step 6 v2 on the box, as registered.

## 3. The train runner's own stop check, tested live (minor 7)

[`selftest_stops_e182t.py`](selftest_stops_e182t.py) runs `run_e182t.py` non-dry at the desk. Its `--sparsity` is a stand-in host that opens
nothing and prints launch records; a stand-in sampler writes the live telemetry file; `ps` is a stand-in first on PATH. **SELFTEST-STOPS-E182T
8 of 8 PASS** ([`logs/selftest-stops-e182t.txt`](logs/selftest-stops-e182t.txt)):
- **K1, K2:** a board reading of 66 W, or `minshire[0]` 71 C, before the first process: exit 6, the stop named in STOP, the host never ran.
- **K3, K4:** the newest line 10 s old, or no line at all: exit 5.
- **K5:** another uid's `sparsity_host`: exit 3.
- **K6:** a STOP file already there: exit 2.
- **K7:** hot while process 0 runs: the watcher writes STOP, and the check before process 1 ends the train (6); the host ran once.
- **K8:** cool throughout: exit 0, two processes, 28 launch records.

The stop-path test 18202 stays as registered: it drives `run_e182.py`'s die, board and watch paths on the card.

## 4. KIT.md's words, corrected (minor 9's kit items)

- "HARNESS OK: 73 files (the four binaries, the train host's patched source and its build record)": the 73 also hold **the built host
  itself** (66 + 4 binaries + the patched source + the record + the binary).
- "about 11 s: one compile against the mock runtime and seven short runs": **nine host runs** (five trains, three refusals and the plain
  run). "The runbook's dry listing and desk test (about a minute)": **36 s**.
- "dmcmd_audit.py GO, 32 send sites, 0 disallowed, every one READ": every one READ **but the excepted `lib.sh:154` STATS_RESET site**, a
  forwarded `--reset-ms` E182 never passes (E153's reviewed exception). No write is sent.
- The committed dry listing (`logs/dry-listing-e182.txt`) reads "the two hash lists (32 and )": it was made before `SHA256SUMS-e182-kit`
  existed. The v2 listing (`logs/dry-listing-e182-v2.txt`) is made after both lists.
- The process nits the lane disclosed (sub-second Python outside the slot, one stray file list removed by its literal path) go to the
  records round.

## 5. The runbook as it now runs (KIT.md's box steps)

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window | `rb/s02_window_e182.sh` | no |
| 2, the desk check | **`rb/s03_desk_e182_v2.sh`** | v2: three hash lists with their counts (32, 79 and this note's), both harness files rebuilt, NOTE1 FILES OK 10, the four desk tests' logs, E182's paths and the workload clean |
| 3, the post | (the card lane's) | no |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no |
| 5, the sync | **`rb/s07_a3_sync_e182_v2.sh`** | v2 (section 2) |
| 6, the box's checks and the build | **`rb/s08_a3_preflight_e182_v2.sh [--no-trains]`** | v2 (sections 1 and 2) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the dry pass | **`rb/s10_a3_dry_e182_v2.sh start|wait [--no-trains]`** | v2 (section 1) |
| 9, the session | **`rb/s11_a3_session_e182_v2.sh FULL yes | PASSES no`** | v2 (section 1) |
| 10, the wait | `rb/s20_wait_e182.sh` | no |
| 11, the release, then the collection | **`rb/s22_collect_e182_v2.sh`** | v2 (section 1); its last line names E182-W-int8's verdict word (E182.md.dated-note-1.md section 2) |

v1's steps 2, 5, 6, 8, 9 and 11 are not run on the card day. The dry listing of both paths is
[`rb/list_steps_e182_v2.sh`](rb/list_steps_e182_v2.sh) ([`logs/dry-listing-e182-v2.txt`](logs/dry-listing-e182-v2.txt): 18 steps, 0 failing).

## 6. The checks, and what they re-ran

| check | result | log |
|---|---|---|
| the runbook v2's desk test (sections 1 and 2) | **SELFTEST-RB-E182-V2 19 of 19 PASS** | `logs/selftest-rb-e182-v2.txt` |
| the dry listing v2, both paths | 18 steps listed, 0 failing, no call | `logs/dry-listing-e182-v2.txt` |
| the train runner's stops, live (section 3) | **SELFTEST-STOPS-E182T 8 of 8 PASS** | `logs/selftest-stops-e182t.txt` |
| the registration note's checks | NOTE1-CHECKS-E182 10 of 10 PASS | `logs/note1-checks-e182.txt` |
| dmcmd_audit, note 1's box and desk files | GO, 0 send sites | `logs/dmcmd-audit-note1.txt` |
| dmcmd_audit, the runbook v2 with k6's steps 5 and 9 and the guard | GO, 11 sites, every one READ | `logs/dmcmd-audit-rb-v2.txt` |
| the frozen lists and both harness files, re-run after this note | registration 32/32, kit 79/79; both makers CHECK PASS; HARNESS OK 66; NOTE1 FILES OK 10; 0 problems | `logs/reruns-note1.txt` |

One desk-test fault was found and fixed on the test's first run, in the test itself. The stand-in ssh gave `bash -s` a seekable stdin. A
detached child then rewound the shared offset, and `bash -s` read its last lines again and again (a launch looped until its 60 s bound).
Over ssh the script arrives through a pipe; the stand-in now pipes it too. No runbook file changed for it.

**Compute:** on the Intel through the round's slot, one job at a time, at nice 10: the runbook test about 1.7 minutes, the stops test 7 s, the
note's checks 4 s, the audits and re-runs seconds. No bench job, mini, lab box or card was used. The tests wrote only under the round's
scratch (the runbook test's own scratch git repository and stand-in box).

## 7. For the readiness critic

- The train host's first real compile is still on the box (step 6 v2). If it fails, the fallback of section 1 now runs to its end.
- Step 5 v2 may change workload files on the box (the committed copies replace older ones). That is the point of the fix. The smoke's train
  gate and the desk's check of C judge the host built from them, and section 2's message names any such file.
- The collector has still not run end to end on a raw tree (KIT.md open item 3); F4 tests step 11 v2's copies only.
- Card time waits on his word.

SPDX-License-Identifier: Apache-2.0
