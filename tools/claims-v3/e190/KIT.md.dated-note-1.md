# E190's kit, dated note 1, before any datum: the card's identity gated before any launch and watched at every launch, a real-path desk test, a live sampler before every process, the latch read as a latch; the v2 runner, build, harness, preflight, doubles and runbook steps; step 2 v2 (Q169, lane fix-e190; new files only)

*Fri 13 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q169, lane `fix-e190`; written between 14:15 and 15:30 PST by the clock; its
commit's own time is git's). No card was claimed or opened, no device command was sent, no lab box was reached and nothing was posted:
every test that runs a built host, the runner, a stand-in session or a stand-in reader ran in a sandbox with no /dev/et* and an empty
/run/lock. It answers E190's verifier (`verify-e190`, Fri 13 Nov 2026, 13:27-14:16 PST: **DOES NOT HOLD** for arm B as kitted; one
major finding, five minor, four nits). The kit (`241726bd`, [KIT.md](KIT.md), its list `SHA256SUMS-e190-kit` `d176b113...`, 56 entries)
and the registration (`508d48d9`, [E190.md](E190.md), `SHA256SUMS-e190-registration` `bfe58c58...`, 16 entries) stay as committed:
every file of theirs is unchanged, and where note 1 replaces a kit file it adds a `_v2` file beside it. **No E190 datum exists.
Nothing here changes a forecast, a band, a rule, a threshold, the order, the card time, the cap, a stop or the scorer.** The
registration's side of the verifier's findings (E135, the label, S6's words, fp16's reading, the process time) is
[E190.md.dated-note-1.md](E190.md.dated-note-1.md); the card lane's (the quiet desk, the hold) is
[CARD-LANE-BRIEF.md.dated-note-1.md](CARD-LANE-BRIEF.md.dated-note-1.md). All three are pinned by `SHA256SUMS-e190-kit-note1`, which
step 2 v2 (`rb/s03_desk_e190_v2.sh`, outside it) pins by count and bytes.*

## Results first (desk checks of code; nothing is measured)

| check | result | log |
|---|---|---|
| **the v2 runner on the doubles** (`selftest_run_e190_v2.py`): EVERY case of the kit's runner test (25: the gates, the stop lines on live samples, the die gate, the card-time rule, a hung and two failed hosts, THE ORDER, the refusals, the real runner stopping at its box check, END TO END through the frozen scorer on both arms) on the v2 runner, then note 1's 12: the identity gate (card 0's config read, 519 mV, no identity block), the identity read (the sampler on card 0, another login on card 1), the host watch (a host naming and holding card 0 in the smoke and in the runs), a host whose card cannot be told, a board that does not rise, a sampler that dies or hangs | **SELFTEST-RUN-E190-V2 37 of 37 PASS**; end to end: 36 runs reduced, t within 1.17e-6, J over idle within 0.47% of the injected; R0, S1-S6 PASS, S7 THE SAME SCALED, S8 STRICT; watts 25% over: S1 PASS, S2 and S3 FAIL | [`logs/selftest-run-e190-v2.txt`](logs/selftest-run-e190-v2.txt) |
| **the REAL path** (`desk/realpath_e190_v2.py`, `desk/realpath_e190_v2.sh`): run_e190_v2.py WITHOUT --dry, each arm under its box's hostname (a private UTS namespace) and a private PID namespace, with a stand-in reader behind the real guard, a stand-in et-who, a stand-in host named `sparsity_host`, a writable stand-in lock and the REAL kernel ELF at the pin | **REALPATH-E190-V2 13 of 13 PASS**: the real build v2 (arm A BUILT; arm B refused: this desk's stock device layer has no ET_DEVICES); the whole real path on both arms (the box check, the harness and preflight run, the lock, et-who and ps, the guard's config and sample, the identity gate and read, the smoke, the runs under the real `timeout 10`); the lock held; a hung host ended by `timeout 10` (rc 124 at 10.05 s); a device process of ours; the reader off its pin; card 0's config, sampler and host each stopped before or at the first launch; a v1 build record refused; a sampler death mid-run | [`logs/realpath-e190-v2.txt`](logs/realpath-e190-v2.txt) |
| **the build v2 on this desk's real toolchain** (`desk/desktest_build_e190_v2.sh`) | **DESKTEST-BUILD-E190-V2 5 of 5 PASS**: the kernel ELF at the pin `aace138c...`; the host's four refusals; the record v2; a changed source and a changed kernel refused; the v2 box check stops at the reader's pin only; **under the hostname aifoundry1 the build refuses this desk's stock device layer: "ET_DEVICES: the host has no ET_DEVICES"** | [`logs/desktest-build-e190-v2.txt`](logs/desktest-build-e190-v2.txt) |
| **the runbook v2** (`rb/selftest_rb_e190_v2.sh`: a fake ssh and rsync, two stand-in boxes, the real builds): the window rule, the lab-git lock, step 2 v2 at every pin (the three lists, each one line short), the history check and a shadow, the look, `ours_live` counting a v2 session by its own name (never by a command string, never by the v1 name), step 5 v2 on the git tree (17, then `pull`) and the rsync, a login link, a hang, NO-THIRD-BUILD with v1 and v2 starts counted together, the negative control, **the ET_DEVICES gate through the runbook on the stand-in aifoundry1**, the real build v2 of arm A, a cut wait, the dry passes v2, the rest rule, the REAL session v2 stopping at its box check, **the wait v2 reading a running `session_e190_v2.sh` as running (17) and none as gone (14)**, the copy-back v2, the data directory, a copy not exact | **SELFTEST-RB-E190-V2 31 of 31 PASS**; no lab box reached | [`logs/selftest-rb-e190-v2.txt`](logs/selftest-rb-e190-v2.txt) |
| the dry listing v2, every step for both arms with stand-ins | **23 steps, 0 exiting non-zero, 0 box calls** | [`logs/dry-listing-e190-v2.txt`](logs/dry-listing-e190-v2.txt) |
| `dmcmd_audit` on the v2 session's files (`preflight_e190_v2.sh`) | **GO, 22 send sites, 0 disallowed, every one a READ**, no allow-list, no exception (the kit's 22, unchanged) | [`logs/dmcmd-audit-e190-v2.txt`](logs/dmcmd-audit-e190-v2.txt) |
| the quick set | E190-COMMON and E190-NOTE1 SELF-CHECK PASS; harness-e190-v2.json CHECK PASS and HARNESS OK (26 files); forecast and plan --check PASS; the stub self-test PASS; the registration's list 16 of 16 OK and the kit's 56 of 56 OK; the fp16 reading re-made equal to its file; note 1's day report on the end-to-end sessions (each fp16 cell inside both bands; the clocks' highest 800 / 600 MHz on the doubles) | [`logs/checks-e190-v2.txt`](logs/checks-e190-v2.txt), [`logs/report-day-e190-v2.txt`](logs/report-day-e190-v2.txt) |

## 1. The card's identity (the verifier's finding 1, MAJOR)

**The fault.** Arm B's config gate compared TDP, threshold and clock, which card 0 reads the same (65 W / 65 C / 600 MHz in every
committed read of either card). The config read's stderr was thrown away, the build never checked that aifoundry1's host honours
`ET_DEVICES`, and the holder checks never saw a host. Had aifoundry1's device layer ignored `ET_DEVICES`, the random fp32, fp16 and int8
load would have gone to card 0 (whose 75 W PMIC alarm trips on fp32 random, E84) while the sampler watched an idle card 1.

**What note 1 adds, before any launch** (`run_e190_v2.py`, `e190_note1.py`):

1. **The identity gate on the start config read.** Its stderr is kept (`config-start.err`, `config-end.err`). The device layer prints
   its PCIe target and physical device ID there (E144's aifoundry2 read with arm A's reader: `/dev/et0_mgmt`, ID 0; E157's, E164's,
   E172's and E184's card-1 reads: `/dev/et1_mgmt`, ID 1; aifoundry1's card 0, where kept: `/dev/et0_mgmt`, ID 0, E84 and E114 as E191's
   dated note 1 counts them). Arm A must read `/dev/et0_mgmt`
   and ID 0; **arm B `/dev/et1_mgmt`, ID 1 and `minion_mv` below 510** (card 1 read 499 or 500 in every committed read; aifoundry1's
   card 0 and aifoundry2's card read 519: E191's dated note 1, section 1, by the same count). A read with no such line fails (the card
   cannot be told). Else the session ends at the gate, no sampler, no launch.
2. **The identity read, with the sampler running and before the smoke** (the stop-path test passed): et-who, as counts by card (never a
   login: `etwho-identity.txt`), must show at least one line of ours on the arm's mgmt node (the sampler's), none of ours off the arm's
   card (arm B: nothing of ours on card 0's nodes or lock) and no other login on the arm's card; AND the sampler's own open files
   (`/proc/<pid>/fd`, the same links et-who's fuser reads) must hold the arm's mgmt node and no other card's. Else the gate, no launch.
   A sampler restarted later is read the same way (another card: the identity stop below).
3. **The build v2 refuses an aifoundry1 host that would ignore `ET_DEVICES`** (`build_e190_v2.sh`): the host binary and
   `/opt/et/lib/libdeviceLayer.a` must both carry the string `ET_DEVICES`, and the build's `CMakeCache.txt` must take its device layer
   from `/opt/et` (the lab's own gates read it the same way: `workloads/pciebench/run_pcie.sh`, `tools/lab/dashboard/remote.sh`). The
   record carries `"builder": "build_e190_v2.sh"` and the reading; the v2 runner refuses any other record, and on arm B any record
   whose reading does not pass. On aifoundry2 (one card) the reading is recorded, never a gate.

**And at every launch:**

4. **The host watch** (`HostWatch`, every 0.1 s while a host runs): the host's stderr (the device layer prints the same block when the
   host opens its ops node: in the committed host and reader logs of September's card-1 runs, 2,343 `PCIe target: /dev/et1_ops` lines and
   26 `/dev/et1_mgmt`, none naming card 0; aifoundry2's, 1,480 `/dev/et0_ops` and 32 `/dev/et0_mgmt` (`desk/note1-reads-e190.txt`); and
   the same block before "device ready" in the sparsity hosts' logs on aifoundry2, E62) and the device nodes its process tree holds open
   or mapped. **Another card
   named or held: the hosts' stop file at once** (the host ends at its next launch boundary, as the stop lines do), the session stops,
   nothing further starts (`identity_trip` in `marks.jsonl`). On the doubles a host on card 0 ran 2 launches where an unstopped smoke
   process runs 7 or 8 (I6, RB4).
5. **The smoke's identity**: each smoke process must also have shown the arm's own card (stderr or held), and **the board must rise at
   least 2 W over the smoke's 30 s rest** (the median of the 10 Hz samples inside the process's launches, at least 3 of them; arm B's
   frozen W over idle is 7.2-14.0 W at the points, its band's low ends 4.9-10.2 W). Else the smoke gate fails. In the runs a process
   whose card was not seen is flagged (reported); one naming or holding another card stops the session (4).

The desk cases: the runner's I1-I9 on the doubles, and RB0-RB5 on the real path (section 2). The dry pass v2 asserts the identity read
(`s10_dry_e190_v2.sh`); its doubles hold stand-in nodes in the dry directory and print the device layer's block.

**What the desk cannot show**: the real device layer's stderr block and node on aifoundry1 for rgm136's host (the lab's card-1 host logs
show the block for other hosts; rgm136's own host has never run on card 1); the build's passing branch on aifoundry1 (no box was reached
in this lane: the box's step 6 v2 reads it on the day; a host without the string refuses arm B, a safe failure).

## 2. The real path, tested (the verifier's finding 2; CONTEXT section 104's lesson)

`desk/realpath_e190_v2.py` runs `run_e190_v2.py` without `--dry` on a stand-in box tree (every v2 harness file copied byte for byte,
the REAL kernel ELF at the pin from the real build v2), under bubblewrap with the arm's box as the hostname, a private PID namespace and
its own `/proc`, inside W/nodev.sh. Stand-ins: the reader behind the REAL guard (a script running the v2 doubles' `config` and `sample`),
`et-who` first on PATH (the doubles' et-who, which reads who holds the stand-in nodes and lock from `/proc`), the host named
`sparsity_host` (its sha256 in the stand-in record), a writable lock file; in-process the runner's reader pin, lock path and node
directory are set to the stand-ins'. Everything else is the real path: the box check with the harness v2 and preflight v2 run, the
lock (open, `flock -n`), the holders (et-who under `timeout 20` and the real `ps`), the config read through the guard under `timeout 10`
(its hostname and `ET_DEVICES` rules), the identity gate and read, the sampler through the guard, the stop-path test, the smoke, the
runs with each host under the real `timeout 10`, the closing config, the manifest. **13 of 13 PASS** (the table above).

## 3. A live sampler before every process (the verifier's finding 4)

Before every host process (the smoke's and the runs'), the sampler must be alive **with a sample received less than 2 s ago**; else the
run ends there, flagged ("the sampler was not live before process k"), and a sampler that is dead, or alive and silent, is stopped
(SIGTERM only) and restarted before the next run (in the smoke: the smoke gate fails). The die gate passes only on such a sample. Desk
cases F1 (dies in S1's second process: S1 ends before its third, the sampler restarts, rc 0), F2 (dies inside P1 fp32's one process: that
process runs out, the next run's gate restarts the sampler and P1 fp16 runs on live samples), F3 (hangs, alive and silent: S1 ends before
its fifth process, the stale sampler is stopped and restarted), RB6 on the real path. **The bound against the readers' record:** in
163,680 committed samples of both readers (aifoundry2's in E136, E146, E169 and E175; card 1's in E157, E164, E172 and E184) the gap
between samples has a median of 100 ms and is at most 145 ms, and none reaches 1 s, so a live 10 Hz sampler never reads stale at 2 s
(a desk read of committed records: [`desk/note1_reads_e190.py`](desk/note1_reads_e190.py) → [`desk/note1-reads-e190.txt`](desk/note1-reads-e190.txt)). **The limit, stated:** nothing is checked inside one
process; a sampler that dies mid-process leaves at most that process unwatched, at most 10 s under `timeout 10`, and the next process
does not start without a live sample.

## 4. The readings, restated or added before any datum (KIT.md section 4 stands where not named)

1. **KIT.md 4.1, the die line on `minshire[2]` (the verifier's nit 9).** `minshire[2]`, the hottest entry, is a LATCH held since the last
   statistics reset (docs/findings/14-card-behaviour.md, its dated note of Tue 3 Nov 2026), not the hottest sensor now. It last read 70 C
   on aifoundry2 (E160-E175) and 65 C on card 1 (E157-E172; 60 C at the end of E184 arm B, whose statistics reset re-armed it: the
   verifier's `s06_latch` reading of the committed telemetry). The line as
   the watcher reads it stands (a trip at 80 C on the mean or on the latch): a latch at 80 C or more would stop a session at its first
   sample, a safe failure that costs the session, never a load past a line. The die gates read `minshire[0]`, the mean.
2. **The identity bounds (new):** `minion_mv` below 510 on arm B; the board's rise in the smoke at least 2 W over at least 3 samples;
   a live sample under 2 s old. Each is the kit's reading, stated before any datum, and none touches a scored number.
3. **The smoke's doubles** run at no less than a quarter of their time (`E190_FAKE_SMOKE_SCALE`, the doubles' own), so that a desk
   sampler at 10 Hz sees the smoke's launches; the launch counts are the doubles' virtual clock's and do not change.

## 5. The files (all new, under tools/claims-v3/e190/)

| file | what | replaces, for the card day |
|---|---|---|
| `e190_note1.py` | the identity reads, the host watch, the board's rise, the sampler's freshness; its self-check | (added) |
| `run_e190_v2.py`, `session_e190_v2.sh` | the v2 runner and its wrapper | `run_e190.py`, `session_e190.sh` |
| `build_e190_v2.sh` | the build v2 (the `ET_DEVICES` gate on aifoundry1) | `build_e190.sh` |
| `check_e190_v2.py`, `harness-e190-v2.json` | the harness v2 (26 files) | `check_e190.py`, `harness-e190.json` |
| `preflight_e190_v2.sh` | the preflight v2 | `preflight_e190.sh` |
| `fake_card_e190_v2.py` | the v2 doubles | `fake_card_e190.py` |
| `selftest_run_e190_v2.py`, `desk/realpath_e190_v2.py`, `desk/realpath_e190_v2.sh`, `desk/desktest_build_e190_v2.sh` | the desk tests | the kit's (still valid for v1) |
| `rb/rb_e190_v2.sh`, `rb/s03_desk_e190_v2.sh` (step 2 v2, outside the list), `rb/s07_sync_e190_v2.sh`, `rb/s08_build_e190_v2.sh`, `rb/s10_dry_e190_v2.sh`, `rb/s11_session_e190_v2.sh`, `rb/s20_wait_e190_v2.sh`, `rb/s22_collect_e190_v2.sh`, `rb/s25_report_e190_n1.sh`, `rb/list_steps_e190_v2.sh`, `rb/selftest_rb_e190_v2.sh` | the runbook v2 (steps 1, 12 and 13 stay the kit's) | the kit's steps 2, 5, 6, 8, 9, 10, 11 |
| `report_e190_n1.py`, `reading-fp16-e190-n1.json`, `reading-fp16-e190-n1.txt` | E190.md note 1's two REPORTED readings | (added) |
| `desk/note1_reads_e190.py`, `desk/note1-reads-e190.txt` | the desk reads of committed records the bounds rest on (the sampler's gaps; the device layer's blocks by box) | (added) |
| `E190.md.dated-note-1.md`, `CARD-LANE-BRIEF.md.dated-note-1.md`, this note | the notes | (added) |
| `logs/*-v2.txt`, `logs/checks-e190-v2.txt`, `logs/report-day-e190-v2.txt` | every check above | |
| `SHA256SUMS-e190-kit-note1` | every file above but itself and step 2 v2 | |

The reducer, the collector, the scorer, the guard, the common module, the rest rule, the history check, the window step and the data and
score steps are the kit's and the registration's, unchanged: the v2 session writes the kit's session form (`build/e190/T<T0>-<arm>/`)
plus `config-*.err`, `identity.json`, `etwho-identity.txt` and an `ident` record for each process, which the collector copies with the
rest and the reducer does not read.

## 6. Device commands

`preflight_e190_v2.sh`: **GO, 22 send sites, 0 disallowed, every one a READ**, the kit's, unchanged. The identity reads send nothing to a
card: et-who stats the nodes (fuser), and `/proc/<pid>/fd` and `maps` are read for our own processes only. No set, no reset, no
statistics reset, no firmware query, no residency read, no drain, no power cycle.

## 7. Labels

The forecasts, bands, rules, order, caps and stops quoted are **registered** (E190.md). The desk tests' results are **desk checks of
code**; the end-to-end joules and the scorer's words come from the doubles. The committed reads this note cites (minion_mv, the
stderr blocks, the latches) are **desk reads of committed records**. Nothing here is measured, blind or held out, and no E190 datum
exists.

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), one job at a time, each that runs a built host, the runner, a
stand-in session or a stand-in reader inside the sandbox (W/nodev.sh; the real-path and runner tests in a private PID namespace too): the
v2 runner's test (about 9 minutes), the real-path test (about 2 minutes, two real builds), the build's test (three real builds), the
runbook's test, the dry listing. No other box.

SPDX-License-Identifier: Apache-2.0
