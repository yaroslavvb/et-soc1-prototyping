# E183's kit, dated note 4 (Thu 12 Nov 2026, before any E183 datum): the train change read from the host's behaviour instead of grepped from its bytes; E183's first rest rule; a read-only copy of Thursday's build records before any build; step 2 v5 and the runbook's new order; no rule, forecast, threshold, plan, cap, stop or reading changes

*Beside [KIT.md](KIT.md) (`cc597bf2`) and its dated notes 1-3 (`45e514e3`, `1e74546a`, `e8e9f4e1`); it edits nothing there, nor in
[E183.md](E183.md) or its notes. Written on the Intel, desk only, by the lane `kit-e183n` of Q164, begun at 08:14 PST Thu 12 Nov 2026 by the
clock; its commit's own time is git's. No card was claimed, no device command was sent, no lab box was reached, nothing was posted, no Modal.
Before the land it was read by a verifier (`verify-kit183`: holds with fixes, three minor faults and four nits, none blocking) and changed
by the lane `fix-kit183` (section 12 lists each fault and its answer).
It answers E183's card day of Thu 12 Nov 2026 (`card-e183`): two train-host builds on aifoundry3, at 06:36:55 and 06:38:45 PST, each read
"the host lacks the train change" (BUILD TREE OK at the 38 pins; the same host sha256 `3e9e7e98...` both times), so E183.md section 7's
registered fallback applied, SKIP: no device opened, 0 card-minutes, every rule NOT RUN. It answers the day's critic (`critic-q163`): its
finding 2 and its next ranks 2 and 7. **No E183 datum exists** (`git log --all` on `docs/reports/data/*e183*`: nothing). E183's notes M1
and M2 stand as committed, and blind.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **the train change's check on real builds**: the patched host and E180's unpatched one, each built by g++-13 at -O2 and -O3 and by clang++ at -O1 and -O2 | **DESKTEST-TRAIN-CHECK-E183 PASS, 42 of 42**: v1's grep fails both GCC builds and passes both clang builds of the patched host; the new check passes all four patched builds and fails all four unpatched; no run of it reached a device call | [`logs/desktest-train-check-e183.txt`](logs/desktest-train-check-e183.txt) |
| **the Intel dry pass v2**, with a real GCC -O2 host in the dry tree | **DRY-INTEL-E183-V2 PASS, 29 of 29**: block v2 runs every block of the plan, the smoke and the stop-path test; block v1 refuses the same host; block v2 refuses E180's host; a whole dry session v2; the device record empty, no network call | [`logs/dry-intel-e183-v2.txt`](logs/dry-intel-e183-v2.txt) |
| **the rest rule** on committed session logs of E184, E185, E186 and E182, and E183's own form; a real session with "DRY" inside a line; every dry marker the kits write | **SELFTEST-REST-E183 PASS, 13 of 13** | [`logs/selftest-rest-e183.txt`](logs/selftest-rest-e183.txt) |
| **the runbook v3 desk test** with a fake ssh and rsync: the records' copy (with the real rsync in remote mode too), step 6 v1 against v2 on a GCC -O2 build, step 8 v2, step 9 v2's rest rule, step 2 v5 | **SELFTEST-RB-E183-V3 PASS, 31 of 31** | [`logs/selftest-rb-e183-v3.txt`](logs/selftest-rb-e183-v3.txt) |
| **the dry listing v5** | 14 steps, 0 exiting non-zero, no ssh or rsync call; the look before the post; step 5a before steps 5 and 6 | [`logs/dry-listing-e183-v5.txt`](logs/dry-listing-e183-v5.txt) |
| **device commands** | the runbook as this note runs it: GO, 11 send sites, every one a READ (note 3's 11, the same); the session's file set as `preflight_e183_v2.sh` audits it on the box: GO, 32 sites, E180's one reviewed exception as before; this note's desk files: GO, 0 sites | [`logs/dmcmd-audit-note4-e183.txt`](logs/dmcmd-audit-note4-e183.txt) |
| **re-runs**: the harness v1 and v2, the build inputs, the registration, E183's earlier lists at their pins | as stated in the log | [`logs/reruns-note4-e183.txt`](logs/reruns-note4-e183.txt) |

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Thu 12 Nov 2026 at about 08:59 PST: public rows L06,
   H24 and H28 (opaque pointers), as E183's KIT.md and notes read them; their Checked rows stand.
2. **Used.** E183's kit and notes 1-3 (the files named below, each unchanged and called, sourced or ported line for line); E185's step 10
   v2 rest rule (`../e185/rb/s11_a3_launch_e185_v2.sh` lines 48-89, `ad2ed873`), ported with its patterns widened; E183's desk mock
   (`desk/mock_runtime_e183.cpp`) and E184's desk stubs (`../e184/desk/stubs`, unchanged); k6's drivers, unchanged; card-e183's desk
   reproduction and critic-q163's, which this note's desk test repeats on every build and extends.
3. **Not used.** Any change to a committed file; any E183 datum (none exists); anything of the private tier.
4. **Tiers.** Public tier only. No private-tier check is used, so there is no sha256 line.
5. **Readiness.** This block is the note's own.

## 1. The train change's check (card-e183's finding; critic-q163's finding 2)

**What failed.** `build_host_e183.sh` line 68, and `block_e183.sh` line 48 before every block, grep the compiled host for `--operands-b`
and `train_kind`. The host's own CMake flag is `-O2`; GCC at -O2 builds the 15-byte `,"train_kind":"` (the patched `host/main.cpp` line
494, a string short enough for the string's inline buffer) from two overlapping 8-byte immediates, so the bytes are never whole in the
binary and a correctly patched host fails the grep. The kit's desk tests grepped only stand-in binaries that carry the strings verbatim
(`dry_intel_e183.sh` line 26) and compiled the real host with clang at -O1, which keeps the literal. Whether a short literal survives
depends on its context (critic-q163's minimal program kept it under the same GCC), so this note greps no other literal for the change.

**The refusal the critic named is not before the device.** "a train needs --launches" is line 392, inside `run()`. `run()` is reached at
line 609, after `Session dev(o, elf)` at 604, whose constructor (128-161) creates the device layer (149,
`dev::IDeviceLayer::createPcieDeviceLayer`, which opens `/dev/et<N>_ops` and calls its ioctls), the runtime (151), a stream (155), loads
the kernel (156) and allocates device memory (159); and `run()` has copied the F image to the card (382-383) before the train's checks
begin (387). So `--operands-b` without `--launches` opens the device, loads code and writes card memory, then refuses: it is not safe before
a block. The desk test shows it on every patched build: the mock's device record holds `createPcieDeviceLayer`, `IRuntime::create`,
`getDevices`, `createStream`, `loadCode`, `mallocDevice` and `memcpyHostToDevice` before that refusal.

**The check used instead: the host's own behaviour, before any device call** ([`train_check_e183.sh`](train_check_e183.sh)). It runs the
host twice, each under `timeout 10`, with `LD_LIBRARY_PATH=/opt/et/lib` as the runner runs it and stdin from `/dev/null`:
1. `<host> --list`: rc 0, and a line for each of E180's two appended modes, `fadd.ps.acc` and `fadd.pi.acc` (the mode table v1's line 69
   grepped for);
2. `<host> --operands-b file:e183-train-check --abba SFFS --launches 13 --kernel ''`: rc 1; the whole line `FAIL: cannot read kernel ` on
   stderr; no `unknown option` and no `needs a value` there; nothing on stdout. A host without the patch refuses `--operands-b` in its
   options loop (rc 2, `unknown option --operands-b`).

**Neither run opens a device: the patched source, line by line** (`host/main.cpp` at the pinned `9b8f1a08...`). `main()` (549) first
registers g3log's three levels (550: the process's own memory, no file and no thread); then reads the options (552-600: string compares,
`strtoull`, `strtod` and `parseSize`, no input or output; `--list` prints the mode table and returns 0 inside the loop, 582-591); then
`readFile(o.kernel)` (602), whose `std::ifstream` of the empty path fails at its open and returns nothing (69-71), and the throw at 603,
caught at 610-612: `FAIL: cannot read kernel `, return 1. The first device call of the program, `createPcieDeviceLayer` (149), the runtime
(151) and every later call to either are in `Session`'s constructor and after it, reached only at 604. The image `--operands-b` names is
never opened (`sources()` reads it in `run()`, line 394). Before `main()`, the host's own namespace-scope objects are in-memory tables
(`PATTERNS` 90, `MESH` 339, the generated mode tables). In the open source of the three libraries the host links (et-platform `836a4ab`,
the revision the lab cites: the device layer, the runtime and the simulator), no function is marked `__attribute__((constructor))`, and the
only code that opens `/dev/et*` or calls an ioctl is the device layer's `DevicePcie` (its constructor, through `countDeviceNodes` and
`setupDeviceInfo`, and its methods), which only `IDeviceLayer::createPcieDeviceLayer` constructs. That last point is a reading of the open
source, not of the box's `/opt/et` binaries, whose revision the kit does not pin.

**What the check proves, and what it does not.** The binary the build left accepts the patch's three options in its options loop and lists
E180's two modes; with the patched source at its pin (`patch_host_e183.py` writes only `9b8f1a08...`) and the tree at its 38 pins (BUILD
TREE OK, before cmake), both unchanged from v1, it was built from the patched tree. It does not run a train: nothing may touch the device
before a block. The smoke's two T5 train processes, gated launch by launch (E183.md section 7, unchanged), read the train itself on the
card, as before. BUILD-E183.json's binaries are still checked before every session (`check_e183.py harness --binaries`, now inside
`harness_e183_v2.py`).

**The other binary greps, tested on the GCC builds as the critic's rank 7 asks.** v1's line 69 (`fadd.ps.acc`) survives in all eight desk
builds, and is replaced anyway by `--list`'s output. Block v1's line 49 (`file:`) survives in all eight and stays in block v2. Line 50 reads
the kernel path compiled into the host (a soft check: it refuses only a path it finds and cannot open); with a box-like path in place of the
desk stubs' `"x"`, both GCC -O2 and clang -O2 builds keep it whole, so it stays too.

## 2. The desk test on real builds ([`desk/desktest_train_check_e183.sh`](desk/desktest_train_check_e183.sh), 42 of 42)

E180's generator makes the tree twice; the patch goes on one (`9b8f1a08...`); the other is E180's host, the committed `3cad4adc...` (THE
NEGATIVE CONTROL). Each is built four ways against E184's desk stubs and linked with [`desk/mock_runtime_e183_v2.cpp`](desk/mock_runtime_e183_v2.cpp),
E183's mock with one addition: every device-layer and runtime call appends `MOCKDEV <call>` to the file `E183_DEVICE_RECORD` names. The
compilers: Homebrew GCC 13.2.0 and Apple clang 21.0.0 (the Intel's; the box's compiler is GCC, its version read by step 5a's copy of
Thursday's cmake log).

| build | binary sha256 | v1's grep | train_check_e183.sh | record after it | the critic's form (no `--launches`) |
|---|---|---|---|---|---|
| patched, g++-13 -O2 | `7bcc771000b604af...` | FAIL ('train_kind' absent) | OK | 0 lines | 10 device calls, then the refusal's throw (rc 139, below) |
| patched, g++-13 -O3 | `17251edd08bc4b4a...` | FAIL | OK | 0 | the same |
| patched, clang++ -O1 | `6e1d7d436bf966a6...` | pass | OK | 0 | rc 1, "a train needs --launches", after 10 device calls (and 4 on the way out) |
| patched, clang++ -O2 | `7c75325d163efb34...` | pass | OK | 0 | the same |
| E180's, g++-13 -O2 | `f03d922caccfa2e4...` | FAIL | MISSING (unknown option) | 0 | rc 2, unknown option, 0 device calls |
| E180's, g++-13 -O3 | `0c42eb483c23a72d...` | FAIL | MISSING | 0 | the same |
| E180's, clang++ -O1 | `006f6317a3651c2b...` | FAIL | MISSING | 0 | the same |
| E180's, clang++ -O2 | `f75931d2d10ac586...` | FAIL | MISSING | 0 | the same |

**A desk toolchain fault, named.** On this Mac, Homebrew GCC 13.2's binaries crash (rc 139) on any exception thrown after `Session` is
built: an unknown `--pattern` does the same (reported per build in the log), while the clang builds print the refusal and exit 1. So on the
GCC builds the critic's form leaves its record (the device reached) and no refusal text. The new check's own throw (line 603) comes before
`Session` and exits 1 on every build. The box's toolchain is Linux's, where the host's exceptions work as every earlier session's did. Every
desk compile runs with `SDKROOT` unset (the Mac's system Python exports the unversioned SDK, against which that GCC fails: a desk detail).

## 3. Where the new check runs: note 4's box files

| file | what | from |
|---|---|---|
| [`train_check_e183.sh`](train_check_e183.sh) | the check above | new |
| [`build_host_e183_v2.sh`](build_host_e183_v2.sh) | v1's build, lines 68-69 replaced by the check | `build_host_e183.sh` |
| [`block_e183_v2.sh`](block_e183_v2.sh) | v1's block, line 48 replaced by the check, its harness check v2 | `block_e183.sh` |
| [`queue_e183_v2.sh`](queue_e183_v2.sh) | v1's queue running block v2 | `queue_e183.sh` |
| [`session_e183_v2.sh`](session_e183_v2.sh) | v1's session with the harness v2, the preflight v2, block v2 and queue v2; its files and T0 names v1's | `session_e183.sh` |
| [`preflight_e183_v2.sh`](preflight_e183_v2.sh) | v1's device-command preflight with note 4's box files | `preflight_e183.sh` |
| [`harness_e183_v2.py`](harness_e183_v2.py), [`harness-e183-v2.json`](harness-e183-v2.json) | v1's own check (`check_e183.py`, imported unchanged) on v1's 80 files, then note 4's 7 box files and v1's harness file at their pins: `HARNESS OK: 87 files` (127 with the binaries and the build tree); made by [`make_harness_e183_v2.py`](make_harness_e183_v2.py) | new |

Every other line of each v2 is v1's. Step 5 (`rb/s07_a3_sync_e183.sh`, unchanged) syncs E183's whole directory, so it carries these files
to the box; their pins are read there by `harness_e183_v2.py` in step 6 v2's wait (with the binaries) and at the session's start, before
any device opens. k6's guard counts session v2 and queue v2 as sessions of ours (its `session_eNNN...sh` pattern).

## 4. E183's rest rule (none until now)

**What E183's steps read of our last session: nothing.** Step 9 (`rb/s11_a3_session_e183.sh`) sends k6's guard (`rb_guard_text`: no dry
pass of the runbook running, no LIVE session of ours) and the checks of today's build and dry pass, then launches; the day-2 brief says so
("E183's own launch step has no rest rule of its own", CARD-LANE-BRIEF.md section 2, item 2). So it read no session log, in no form: not
E185's `build/e185/T<T0>/session.log` (Thu 12 Nov, ended 06:15:21 PST), not E186's `build/e186/T<T0>/session.log` (Mon 9 Nov, ended
14:19:08 PST), not E184's `build/e184/session-<arm>-t<T0>.log` nor its own `build/e183/session-t<T0>.log`. On day 2 the order kept E183
after E185's collection; nothing gated E183's launch on a rest.

**The rule now** ([`rb/rest_rule_e183.sh`](rb/rest_rule_e183.sh), sent by step 9 v2 to the box after k6's guard and before the launch): no
E183 session starts within **40 minutes** of the end of our last real session on aifoundry3, the figure of E185's runbook gate. It is
E185's step 10 v2 rule (its block reading, both end forms, a block without its end counted at its last line) with its log patterns widened
to every form our kits write: `build/eNNN/session.log`, `build/eNNN/session-*.log`, `build/eNNN/T<T0>/session.log` and
`build/eNNN/T<T0>/session-*.log` for any run's directory. Dry logs are skipped by name, and dry or no-device blocks inside a log. A block
is dry only by the markers the kits write: a line whose words, after its time stamp if any, begin `DRY ` or `DRY:` (`DRY config ...`,
`DRY: the smoke gate ...`, `DRY session end`, lib.sh's untimed `DRY ettelem config` and `DRY hold10: ...`) or `DESK: `, or a `session start`
line ending ` DRY` (E181's and E185's) or `; DRY)` (E172's). E185's v2 reading took any `DRY` or `DESK:` anywhere in a line, so a real
session whose log printed such a word (`V3_DRY= (unset)`, say) was skipped (verify-kit183's nit). Every block the new reading calls dry, that
one called dry too, so it counts every session that one counted. On the lab's committed logs the two agree block by block: 62 session
blocks in 53 tracked logs, 6 dry by each (a desk check of fix-kit183, before the land). E185's own v2 never read E186's form (verify-e185d;
fix-q163d's desk case), and its desk case is repeated here. E185's hour (A7-4) is E185's plan and is not E183's.

**Desk cases** ([`rb/selftest_rest_e183.sh`](rb/selftest_rest_e183.sh), 13 of 13, on the committed logs at their box paths, "now" fixed):
RS1 E184's form, 30 minutes after its end REFUSED, 41 minutes rest 41; RS2 E185's form, 39 REFUSED, 40 rest 40 (the edge passes); RS3
E186's form, 10 REFUSED naming E186, and E185's v2 lines on the same tree read "no real session" (the gap); RS4 every form at once (E182,
E183's own, E184, E185, E186): the latest, E185's, rest 104; RS5 dry and no-device logs only: none counts; RS6 a cut E186-form session, its
last line 20 minutes back: REFUSED; RS7 no log; RS8 a real E185-form session with `V3_DRY=` and `DESK:` inside its lines, 10 minutes back:
REFUSED, while E185's v2 lines read "no real session" (the nit); RS9 each marker form inside logs named as real ones, each dry block 5
minutes back, beside a real block 50 minutes back: rest 50 (each of the reading's three clauses is the only marker of one block there, so
dropping any one of them reads a dry block as a session 5 minutes old, as fix-kit183's three mutants did). In the runbook test, S1-S4 send
the rule through step 9 v2 to a stand-in box.

**It is a gate of the runbook, not a rule of E183.md.** It only refuses a launch (10, nothing started); it changes no reading, plan, cap or
stop. E183.md section 7's order stands ("E183 may go first or follow any run"), now at least 40 minutes after our last real session there.
No E183.md amendment.

## 5. Step 5a, NEW: the read-only copy of Thursday's build records ([`rb/s06_a3_records_e183.sh`](rb/s06_a3_records_e183.sh))

Card-e183 left E183's build records on aifoundry3, not copied: the day's two build logs (`build/e183-build-logs/2026-11-12/`), the count
file `build/e183-build-attempts.txt`, the last build's cmake log `build/enercat-e183-cmake.log` (it names the box's compiler), the inputs
and tree checks (`build/e183-inputs.txt`, `build/e183-inputs-build.txt`, `build/e183-tree-check.txt`) and the build job's four files
(`build/q141k/jobs/a3-build-e183.sh`, `.out`, `.pid`, `.rc`). The next build rewrites the cmake log, the checks and the job's files. Step 5a
copies them first, with k6's bounds: the 15 s probe, then ONE rsync (the copy class's 600 s), relative paths kept, from
`aifoundry3:aifoundry/` into this day's `RB_OUT/box-records-e183/`; a printed login link stops it (11) and appends the box to `RB_LOCK`. The
box only sends: nothing there is written, moved or removed. At the desk it prints the cmake log's compiler lines and writes `RECORDS-COPIED`
(each file and its sha256). **Step 6 v2's start refuses (10) without the marker**, so no build comes first. A record not on the box is a
gap, named in the marker, and the step reads COPIED WITH GAPS (0), only when the box's own rsync says so: rsync's exit 23 (the runbook
log's `child_rc`) and, for every record not copied, its sender's own line `link_stat "<...>/<record>" failed: No such file or directory`.
The only other lines allowed are rsync's code-23 summary and, when not one record is on the box, any rsync line naming a broken pipe: with
every source missing the remote sender ends at once and the receiver prints `write error: Broken pipe (32)` (the real rsync 3.5.1 in remote
mode, on the desk; local mode did not). That is safe to pass then: the box's own rsync has named every record missing, so nothing was there
to lose. Anything else is 14 and no marker: another exit code, another error line (a record that could not be read, the box's
tree missing), or a record missing from the copy that the box's rsync did not name missing. So when every record is gone from the box the
copy reads COPIED WITH GAPS with 0 files and step 6 v2 can build; kit-e183n's first form of this step read that case as 14 every time and
the day could not build (verify-kit183's fault 1). **It runs once a day:** with `RECORDS-COPIED` already in the RB_OUT it refuses (16)
before any call, so a second run after step 6 cannot overwrite Thursday's records with the new day's (the same day: go on to step 5; a new
day: a new RB_OUT). The records stay in `RB_OUT`, outside the repo; a records round that commits any of them scrubs them first (E178's
`scrub_tree_e178.py`). **No tidy of aifoundry3 moves or removes E183's build records before a copy of them is on the desk** (step 5a's
`RECORDS-COPIED` on E183's next day, or a tidy lane's own read-only copy first).
Desk cases (the runbook test): R0 step 6 v2 before step 5a, refused, no call; R1 one probe and one rsync, 11 files at the box's own bytes,
the compiler line, the box's `build/` unchanged; R2 two records absent, COPIED WITH GAPS naming both; R3 a login link at the probe, 11, the
lock file appended, no rsync; R4 a protocol error, 14, no marker. R1-R4's stand-in rsync rewrites `host:path` into local paths, so R5-R11
run the real rsync in remote mode, its server started on the stand-in box by the stand-in ssh: R5 all 11 records, one probe and one
transport, the box unchanged; R6 two absent, each named by the box's rsync, COPIED WITH GAPS (9 files); R7 every record absent: rsync's
23 with its receiver's broken pipe, COPIED WITH GAPS, 0 files, the marker written (0); R8 a record present but unreadable: 14, no marker;
R9 the box's tree missing (rsync's `change_dir` line): 14, no marker; R10 step 5a again where the marker is: 16, no call, the marker
unchanged; R11 a login link during the transport: 11, the lock file appended, no marker; then the stand-in box as before R5.

## 6. Step 2 v5 ([`rb/s03_desk_e183_v5.sh`](rb/s03_desk_e183_v5.sh))

It runs step 2 v4 unchanged (the day-2 check v2 with its own pull, then step 2 v3, the check v1 and step 2 v2), then on the same HEAD:
- **E183's lists, found by "SHA256SUMS" anywhere in a file's name** under `tools/claims-v3/e183` (the records' owed item: a perimeter that
  matched only a name's start missed lists): the nine it knows, at their pinned counts and own sha256 -- the registration's 20
  (`6defebd4...`), the kit's 46 (`2e06e0cc...`), note 1's 46 (`24d0c583...`), kit note 2's 15 (`6ebc97db...`), kit note 3's 19
  (`3b472e38...`, pinned by no step before) and **this note's list, `SHA256SUMS-e183-kit-note4`, at 44 entries and its own bytes**, each
  with every entry OK, a gate; the brief's 15 (`02c8b2b6...`), its count and bytes a gate (its entries the day-2 check reads by their roles);
  notes M1's 25 (`c8bad971...`) and M2's 9 (`ced9afe2...`), reported, never a gate (october-forecast-model's arms are reported arms, so
  their files cannot stop E183). A changed, short or missing gate list stops the step (16); a list it does not know is reported, never a
  gate;
- `harness-e183-v2.json` re-made (`make_harness_e183_v2.py --check`: CHECK PASS), `harness_e183_v2.py`: `HARNESS OK: 87 files`, and this
  note's four desk tests' logs as committed;
- HEAD unchanged across them, else 16.

Step 2 v5 is not in this note's list: a file cannot hold the sha256 of a list that holds its own. E183's next day's anchor lines give its
sha256 beside the list's. Desk cases (the runbook test, on a scratch repository with v4 a stand-in and a stand-in list pinned in v5's
copy): P1 at its pins 0; P2 a changed entry in this note's list 16; P3 the list one line short 16; P4 kit note 3's list one line short 16;
P5 a list with SHA256SUMS in the middle of its name, unknown, reported, 0; P6 note M1's list changed, reported, 0; P7 v4's 16 passed on.

## 7. The runbook as it now runs

| step | file | from this note |
|---|---|---|
| **0, before step 1** | `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull`, under the lab clone's commit lock | unchanged (note 3's) |
| 1, the window | `rb/s02_window_e183.sh <day> <last start> <last end>` | unchanged |
| 2, the desk check | **`rb/s03_desk_e183_v5.sh`** | **new**: v4, then this note's lists, harness and logs |
| 4, the look (BEFORE the post) | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | unchanged |
| 3, the post | the card lane's, under the post's lock: `for 1.5 h` (FULL), `for 1 h` (SHORT) | unchanged |
| **5a, the build records** | **`rb/s06_a3_records_e183.sh`** | **new**: the read-only copy, before any build; once a day (16 on a second run) |
| 5, the sync | `rb/s07_a3_sync_e183.sh` | unchanged: it carries note 4's files |
| 6, the build | **`rb/s08_a3_build_e183_v2.sh start`**, then `wait` while it says 17 or 14 | **new**: build v2; refuses without step 5a |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | unchanged |
| 8, the dry pass | **`rb/s10_a3_dry_e183_v2.sh start`**, then `wait` | **new**: block v2 and session v2's start gate |
| 9, the session | **`rb/s11_a3_session_e183_v2.sh FULL`** (or `SHORT`) | **new**: the rest rule, then session v2 |
| 10, the wait | `rb/s20_wait_e183.sh`, again while it says 17 | unchanged |
| 11, the release, then the collection | the post's release; `rb/s22_collect_e183_v2.sh` | unchanged |
| after the data commit | `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 --data <E183's data dir>` | unchanged (note 3's) |

**Never run on E183's day:** step 2 v4, v3, v2 or v1 alone; step 6 v1 (`rb/s08_a3_build_e183.sh`), step 8 v1 (`rb/s10_a3_dry_e183.sh`),
step 9 v1 (`rb/s11_a3_session_e183.sh`), step 11 v1; and the v1 box files as a session's (`build_host_e183.sh`, `block_e183.sh`,
`queue_e183.sh`, `session_e183.sh`, `preflight_e183.sh`). The dry listing of this table: [`rb/list_steps_e183_v5.sh`](rb/list_steps_e183_v5.sh).
Step 6's re-run rule and E183.md section 7's fallback are v1's: a failed, overrun or lost build gets one re-run; after a second, SKIP.

## 8. What does not change

E183.md, its notes 1, M1 and M2, and every rule, forecast, threshold, power figure, plan, cap and stop: FULL about 52 card-minutes (cap
65), SHORT about 25 (cap 32), the stops (65 W, 70 C), every device command a READ. KIT.md and notes 1-3 and their files. The build inputs
(40) and the tree (38 pins, the patched `main.cpp` `9b8f1a08...`). The harness v1 (`harness-e183.json`, 80 files). The registered
fallback. Every new file is new; nothing committed is modified, renamed or removed, and no new module shares a name with another.

## 9. Labels

- **Registered, before any datum:** this note's train change's check, rest rule, step 5a's place and refusal, and step 2 v5's pins.
- **Desk checks of code, not measurements:** every test result here.
- **Reported:** october-forecast-model's arms (notes M1 and M2), unchanged and unread; their forecasts stay blind for E183.
- Nothing here is held out or post hoc, and nothing is measured.

## 10. Files ([`SHA256SUMS-e183-kit-note4`](SHA256SUMS-e183-kit-note4), 44 entries)

This note and [CARD-LANE-BRIEF.md.dated-note-3.md](CARD-LANE-BRIEF.md.dated-note-3.md); the box files of section 3 and
`make_harness_e183_v2.py`; [`dry_intel_e183_v2.sh`](dry_intel_e183_v2.sh), `desk/desktest_train_check_e183.sh`,
`desk/mock_runtime_e183_v2.cpp`; `rb/s06_a3_records_e183.sh`, `rb/s08_a3_build_e183_v2.sh`, `rb/s10_a3_dry_e183_v2.sh`,
`rb/s11_a3_session_e183_v2.sh`, `rb/rest_rule_e183.sh`, `rb/list_steps_e183_v5.sh`, `rb/selftest_rest_e183.sh`,
`rb/selftest_rb_e183_v3.sh` and `rb/fake_cmake_gcc_e183.sh` (the stand-in cmake that builds by GCC at -O2, desk only); the seven logs. It
also pins the unchanged files the new steps run, source, import or name: `rb/rb_e183.sh`, `rb/s02_window_e183.sh`, `rb/s03_desk_e183_v4.sh`,
`rb/s07_a3_sync_e183.sh`, `rb/s20_wait_e183.sh`, `rb/s22_collect_e183_v2.sh`, `check_e183.py`, `harness-e183.json`,
`SHA256SUMS-e183-kit-note3`, `CARD-LANE-BRIEF.md`, k6's `rb_common.sh`, `s05_look_k6.sh` and `s09_a3_reads_k6.sh`, and E185's
`rb/s11_a3_launch_e185_v2.sh` (the rest rule's source). Step 2 v5 is outside it (section 6).

    bash tools/claims-v3/e183/desk/desktest_train_check_e183.sh <scratch dir>
    bash tools/claims-v3/e183/dry_intel_e183_v2.sh <scratch dir>
    bash tools/claims-v3/e183/rb/selftest_rest_e183.sh <scratch dir>
    bash tools/claims-v3/e183/rb/selftest_rb_e183_v3.sh <scratch dir>
    bash tools/claims-v3/e183/rb/list_steps_e183_v5.sh <an empty scratch dir>

## 11. Open items (for the verifier, the readiness critic and the records)

1. A verifier read this note before the land (`verify-kit183`, section 12); fix-kit183's changes after it have had no second verifier, only
   their own desk tests here and the readiness checks after the land. E183 FULL only on his go, on a day with a fresh Tailscale approval
   for aifoundry3.
2. **The new build's first compile is on the box** (step 6 v2), as before: one re-run, then SKIP. The box's compiler is named by Thursday's
   cmake log, which step 5a copies; the desk built with GCC 13.2 and clang 21.
3. The libraries' load-time behaviour is read from the open source (section 1), not from the box's `/opt/et`.
4. Not done here (the critic's rank 7): moving aside, on the box, E185's first try's files, E183's build records after step 5a's copy, and
   E186's and E184's leftovers. E183's build records move only after a copy of them is on the desk (section 5).
5. **E183's next day has a Pacific date of Fri 13 Nov 2026 or later.** aifoundry3's `build/e183-build-attempts.txt` holds two
   `a3-build-e183 started` lines dated 2026-11-12 (card-e183's two builds), and step 6 v2 counts the day's starts by the Pacific date and
   refuses a third (NO-THIRD-BUILD, 16: E183.md section 7's SKIP "at a third start"), after the look and the day's post. A go later on
   Thu 12 Nov 2026 could only end in that SKIP (verify-kit183's fault 2).

## 12. Read before the land: verify-kit183's faults, and what changed (fix-kit183)

The verifier read kit-e183n's local commit (`65891963`, never pushed) and held it with fixes: three minor faults and four nits, none
blocking. Before the land, fix-kit183 answered each in these same files (none had been committed); every test above was run again on the
final bytes.
1. **Step 5a stuck when every record is gone from the box** (minor): real rsync in remote mode adds its receiver's broken pipe to the 23,
   which the first form read as a failure, every time. Fixed in `rb/s06_a3_records_e183.sh` (section 5: a gap must be named by the box's
   rsync, and the broken pipe is allowed only when no record is there); desk cases R5-R11 run the real rsync in remote mode.
2. **No day limit** (minor): section 11 item 5 and the brief's dated note 3 now say Fri 13 Nov 2026 or later; no code changes.
3. **The land's order** (minor): the scan runs on scratch copies before any file reaches the lab clone, and a stopped land removes its
   files by their paths (the land's own instructions; nothing in this note).
4. **`train_check_e183.sh`'s header** says it writes "two temporary files"; it writes four (`o1`, `e1`, `o2`, `e2`) in one `mktemp -d`
   directory, and its EXIT trap removes them all (the verifier found none left in 14 runs). The file is left as the verifier built and ran it.
5. **The rest rule's dry reading** took any `DRY` or `DESK:` in a line (inherited from E185's v2): now only the kits' markers (section 4;
   RS8, RS9).
6. **Step 5a twice**: a second run after step 6 would have overwritten the day's copy; it now refuses (16) before any call (R10).
7. **"E183 FULL first"** on a day shared with E187 or E188 (the brief's note 3) is a preference within E183.md section 7 ("E183 may go first
   or follow any run"), not a plan; the brief now says so.

SPDX-License-Identifier: Apache-2.0
