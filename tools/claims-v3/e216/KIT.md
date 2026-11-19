# E216's run kit: one session on aifoundry2 card 0 under its governor, run from aifoundry2 itself - E208's registered runner, unchanged and imported, with E216's registered stop lines (70 W x 3, 70 C) and FAMILY G (rgm136's gemmLnc branch on rgm211's host, built here at E211's pins), THE IDENTITY GATE PER PROCESS, THE WALK CHECK and THE KERNEL STOPS on family G, the G block last; one sampler with the stop lines live, the card's lock held with et-who empty, the config read and its identity gate first, the stop-path test, the smoke, 69 runs each under a plain `timeout 10` and never killed; THE QUIET DESK FLAG only after every other booked card lane's launch, THE REST RULE before any card command, THE REBOOT GATE, THE ONE-LAB RULE; the never-run search repeated and judged by each point's own reading; the collection with THE MASK and THE SCRUB tested on records that carry the box's home; E208's reducer and the frozen scorer after the data commit (Q227; kitted, not run)

*Thu 19 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q227, lane `kit-e216`, from 10:55 PST). No card was claimed or opened: aifoundry2 has
a card, so every desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its
sandbox (`W/nodev.sh`: no /dev/et* device node, an empty /run/lock), each only while THE QUIET DESK FLAG was absent. No device command was sent,
nothing was posted, no simulator was run, no other box was reached. New files only, all under `tools/claims-v3/e216/`. The registration
[`E216.md`](E216.md) (found by content: the commit that added it, its `tools/claims-v3/e216` subtree `60ddf6c9...`; `SHA256SUMS-e216-registration`
`ad903eaf...`, 37 entries) and every file its list names stay as committed. **No E216 datum exists, and no E215 datum was opened by this lane**
(its scans left `card-e215a` and `card-e215b` out by name, and the lab clone holds no E215 data folder). **Nothing here changes a forecast, a
band, a rule, a tie, a threshold, a point, the order, the card time, the cap, a stop or the scorer.** Where E216.md leaves a reading to the kit,
the reading is stated in section 4 before any datum.*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

## Results first (desk checks of code and desk reads of committed records; nothing is measured)

| check | result | log |
|---|---|---|
| **the REAL path** (`desk/realpath_e216.py`): runbook step 9's launch exactly as the card day makes it - the box root's `start_e216.sh`, then `session_e216.sh`, then `src/run_e216.py` (E208's runner imported, unchanged) on its real path (no --dry) - in a box root made by `make_box_e216.py sync`, each case in a sandbox of its own (two regular files at /dev/et0_ops and /dev/et0_mgmt, a private /run/lock, the host name aifoundry2), stand-ins for every device tool (the reader behind E208's guard, rgm136's host, rgm211's host, et-who; E208's doubles inside them), the REAL kernel ELFs (rgm136's at E136's pin: the identity gate per process reads it); at the real pace | **DESKTEST-REALPATH-E216 29 of 29 PASS**: **MAIN THROUGH THE WHOLE REGISTERED SCHEDULE** (the box check with both builds and the identity gate's check, the card's lock, the config and identity gates, the stop-path test with E216's lines 70 W x 3 / 70 C, the identity read, the 60 s opening rest, the smoke, all 69 runs in the registered order, **the G block last: its ten processes on rgm211's host with rgm136's real ELF, each GATE OK and walk 'mn' ok**, 70 of 70 processes gated, the closing config read, the clock in every sample; E208's reducer unchanged and the frozen scorer reading the session: R0 PASS, all 46 points read, the ten G points among them); STEP (a step inside y08b's busy window: FLAGGED; MAIN's y08b the control); the three stop lines at E216's numbers (BOARD above 70 W on 3 samples; DIE the shires' mean at 70 C; LATCH a risen latch at 70 C; LATCHHI a latch high from before: no trip); RUNTIME (a runtime line splitting the check record: no check read, R0 FAIL); HANG (a host deaf to SIGTERM: a LEFTOVER, the lock held until it ends by itself, NO SIGKILL); QUIET; HOLDER, BUSYLOCK, NOLOCK, WRONGCFG; TWOFAIL; **GWALK** (g07's walk fails: THE KERNEL STOP, g08-g01 never start, the 59 runs before stand), **GHANG** (g07's G host deaf to SIGTERM: a LEFTOVER after the G block's first process, resolved by itself, no SIGKILL), **GTRIP** (the board stop in the G block alone); GATE, STALE216, HOST216 (the box check: rgm211's ELF in rgm136's place, a stale E216 build record, a changed G host: no device opened); start_e216.sh's eight refusals; R-REAL | [`logs/realpath-e216.txt`](logs/realpath-e216.txt) |
| **the DRY audit** (`desk/dryaudit_e216.py`): every line of E208's `run_mms.py` and of `run_e216.py` that reads the dry flag, the real path there and the real-path cases that ran it | **DRY-AUDIT-E216 33 of 33 COVERED** (28 lines of E208's run_mms.py, 4 of run_e216.py, and start_e216.sh's E216_DESKTEST) | [`logs/dryaudit-e216.txt`](logs/dryaudit-e216.txt) |
| **the runner on the doubles** (`desk/selftest_run_e216.py`): whole dry sessions of the registered schedule (scale 0.02), the REAL built ELFs in each box root, then E208's reducer and the frozen scorer | **SELFTEST-RUN-E216 13 of 13 PASS**: FULL (69 runs, 70 processes gated, the ten G on rgm211's host's double as the last ten host calls, E216's lines in the stop-path record, R0 PASS, every point read); LINE71 / LINE69 (the board 71 W x 3 stops, 69.66 W at most does not: E216's 70 W line, not E208's 85 W); GTRIP (the board stop in the G block alone); KWALK, KCHECK, KTENSOR, KSLOW (THE KERNEL STOPS in g07: the walk, a wrong C (R0 FAIL), a tensor error, rc 124); KGATE (rgm211's ELF swapped in while N2 runs: g07's gate refuses, no process starts, THE IDENTITY GATE STOP); KGATE0 (the smoke's first process refused); ORDER (a G run moved before pass 2: refused at load) and OVER (a run at 64.5 W: refused); TWOFAIL (E208's rule unchanged) | [`logs/selftest-run-e216.txt`](logs/selftest-run-e216.txt) |
| **the host-output parsers on real committed bytes** (`desk/realbytes_kit_e216.py`) | **REALBYTES-E216 10 of 10 PASS**: E208's `parse_sparsity` on E209's session on THIS CARD (67 processes) and E212's S3 re-run (54), each process's records = the runner's own count; `parse_ident` on both (the ops node, the mgmt node, physical device ID 0, nothing else); **E216's walk check on every committed stdout of rgm211's host running gemmLnc** (15: E213 arm A, E213 arm B on card 1, E211 family C; 193 launch records, E208's `ok_launch` reading 163) each ok, and refusing rgm211's gemmLn stdouts (walk 'nm') and rgm136's own host's (no walk field); a runtime line spliced at every byte offset of a real gemmLnc launch record and its check record (810 splices: never a changed value; the launch dropped, or the check lost and the kernel stop following); **THE MASK on E209's REAL fwgate record carrying the box's home** (the raw bytes = E209's MANIFEST line a91fcc83..., masked to the committed 2d56a732... exactly, line 34; the scrub's patterns hit the raw, miss the masked; two ledger lines stop, 16); step 13's manifest read (1 line by THE MASK; 0 on the raw; another file changed: 10); **the whole collection on E209's real session with its raw record**: exit 0, only that line masked; a home planted in runner.out: THE SCRUB stops it (16) | [`logs/realbytes-e216.txt`](logs/realbytes-e216.txt) |
| **the runbook** (`desk/selftest_rb_e216.py`) | **SELFTEST-RB-E216 92 of 92 PASS** (fix-e216's re-run, the stand-in form; **87 of 87 in the committed-kit form**, which skips P4-P6, P14 and P17; the new cases Z1-Z4, G15-G18 and G8's words: section 12): the window (W1-W6); THE QUIET DESK FLAG on every path and THE P2 COUNT by each process's own script name (Q1-Q10); **THE ORDER** (O1-O7: two booked card lanes without markers: others 17, raise refused, no flag; one launched; a marker older than its booking; both launched: raise 0; an orchestrator's hold REPORTED, a card lane with no marker named waited for; RB_BOOKS refused outside a desk test); THE REST RULE (R1-R11: the lab's committed data at HEAD names E212's S3 re-run); step 7 and THE REBOOT GATE with the lab's fwgate in its desk mode (G1-G14: the box's real boot, after the last read: NEEDS-READ, one read EQUAL; a boot after the read; CONTINUITY; a DIFFERENT answer; the rest not open: nothing sent; ...); **STEP 2 AT EVERY PIN** in a scratch repository with a stand-in kit commit (P1-P17: STEP2 PASS; the kit pin's bytes and count; MM1-v3.1's list changed; the registration's list changed in a commit; a shadowing module; **the sealed record unregistered, registered, marked, and a later seal a comment line naming its second note**; an E216 datum in a ref; step 2 itself changed later; no desk span; a log without its PASS line; **the frozen scorer's print not the kit's: refused, step 2 runs no maker**); the launch, THE WAIT by the real script name, THE COLLECTION (S1-S10: a desk test's session refused outside a desk test; the scrub both ways; COPY-BACK EXACT; E208's checker; both build records; **THE MASK on a record carrying the box's home**; step 13's manifest read); E on every stop path (E1-E7: the flag, the spans, the hold line and the booking each released only if the lane's; a leftover keeps everything) | [`logs/selftest-rb-e216.txt`](logs/selftest-rb-e216.txt) |
| **step 13's label check and readings** (`rb/post_e216.py --selftest`) | **SELFTEST-POST-E216 8 of 8 PASS** (labels naming a point, a typo, a capital, not a list, not an object, not JSON; the readings: no run, route m only, no energy, labelled, the session's stop) | [`logs/selftest-post-e216.txt`](logs/selftest-post-e216.txt) |
| **the builds** (`desk/desktest_build_e216.sh`): the box root synced, E208's `build_mms.sh` unchanged, then `build_e216.sh`, against this box's /opt/et | **DESKTEST-BUILD-E216 6 of 6 PASS**: rgm136's ELF `aace138c...` (E136's pin EQUAL); rgm211's host built from E211's sources (10 of 10 at the pins), its eight refusals before its device stage, each in a bubblewrap; rgm136's ELF GATE OK for both families, rgm211's own ELF (`00402801...`, E211's whole-ELF pin) refused by both; the records of today; refused without E208's build of today, with a changed source, under the box lock; rgm211's ELF in rgm136's place: BUILD-FAILED (riscv gcc "() 15.1.0", g++ 13.3.0) | [`logs/desktest-build-e216.txt`](logs/desktest-build-e216.txt) |
| **the dry pass** (the box root's `src/dry_e216.sh 0.02` after the builds) | **DRY PASS a2c0 E216 (runner rc 0; 0 runs not clean)**: device calls 73 (config 2, sampler 1, host 70); 69 of 69 runs (2 null) in the registered order; 46 point ids; **70 of 70 processes GATE OK (10 'rgm136 gemmLnc', 60 'rgm136 gemmL'); the ten G processes the last ten host calls, on rgm211's host's double**; 33.94 card-minutes at the doubles' pace (unscaled); stop None | [`logs/drypass-e216.txt`](logs/drypass-e216.txt) |
| **step 6n's tool at the desk** (`desk/neverrun_card_e216.py`, the lab clone at the registration's local commit and the round's lane folders) | **NEVER-RUN-E216: 46 of 46 points never ran on aifoundry2 card 0** (fix-e216's re-run at the amended registration: 81,440 files, 9 points with hits that are no session record, REPORTED: y08a, y08b, f01-f07, all in E217's plan and registration copies; kit-e216's run: 81,371 files; E216's and E215's card lanes left out by name); y08a and y08b carry hits that are no session record (the model session's E217 plan copy, REPORTED: section 4 item 12); ran before the freeze line: none | [`logs/neverrun-desk-e216.txt`](logs/neverrun-desk-e216.txt) |
| **the dry listing** (`rb/list_steps_e216.sh`: every step in the brief's order with its script in full; nothing run) | **dry listing: 28 steps listed, 0 run, 0 box calls** (step 2 printed with its kit pin not yet set: the listing sits in the list that pin names) | [`logs/dry-listing-e216.txt`](logs/dry-listing-e216.txt) |
| **dmcmd_audit_v2** (`preflight_e216.sh`: every file the day runs, builds or sends a command from; no --allow) | **dmcmd_audit: GO (12 send site(s), 0 disallowed; allow-list: none)** | [`logs/dmcmd-audit-e216.txt`](logs/dmcmd-audit-e216.txt) |
| **the kit's checks** (as step 2 and the box run them) | make_box_e216.py check: CHECK PASS (77 files; the schedule re-made, 69 runs, the G block last); the identity gate's own check from the box root: CHECK PASS (rgm136's ELF, .text and loadable identity SAME as E206's); run_e216.check_sched on the schedule: PASS (57 'rgm136 gemmL' and 10 'rgm136 gemmLnc' process runs); the registration's list 40 of 40 OK (with its Amendment 1: fix-e216), E208's 57 of 57 and its src/ 48 of 48, MM1-v3.1's 64, MM1-v3's 170 and MM1-v2's 114 OK; the frozen scorer print-only byte for byte `logs/forecasts-print-e216.txt` and its self-test byte for byte `selftest-standins.json`, Amendment 1's `report_e216.py --selftest` byte for byte `reported-selftest-e216.json`, no registered file changed; every kill word in the kit's code a word that forbids it | [`logs/checks-e216.txt`](logs/checks-e216.txt) |

## 1. The kit: E208's registered runner, imported unchanged, with E216's lines and family G (E216.md 2 and 6)

**THE BOX ROOT** (`make_box_e216.py`; its every file in `harness-e216.json`, 77 files, each at its sha256): a folder of the card lane's own on
aifoundry2 (never inside the lab clone, never a model session's `ee-*` folder), E208's kit layout (`tools/claims-v3/e208/proposal/src/README.md`):

| what | files | from |
|---|---|---|
| E208's registered kit, every file UNCHANGED at its committed sha256 | 48 (`src/run_mms.py` `5dae80e0...`, `src/mms_common.py` `c3fc7883...` and `src/reduce_mms.py` `b9e32618...` (both pinned by E216.md 7 as the measured side), `src/mms_ident.py`, `src/fake_card_mms.py`, `src/guard_ettelem.sh`, `src/build_mms.sh`, `src/preflight_mms.sh`, `src/check_mms.py`, `src/status_mms.sh`, `src/stop_mms.sh`, the rgm136 and ettelem sources, the device-command table, the tiles, ...) | `tools/claims-v3/e208/proposal/src/` at its `SRC-SHA256SUMS` (`543e9298...`, 48 lines) |
| E216's box files | `src/run_e216.py` (the runner), `src/fake_card_e216.py` (rgm211's host's double), `src/ident_e216.py` (the identity gate), `src/build_e216.sh` (rgm211's host), `src/session_e216.sh`, `src/start_e216.sh`, `src/dry_e216.sh`, `src/sched/a2c0-E216.json` (the schedule) | `box/` here |
| the identity gate's inputs, unchanged | `src/kernel-e216.json` (the registration's `41feea0f...`), `src/e206/check_e206.py` (`fdbd35a6...`) and `src/e206/e206_common.py` (`9278e1f1...`) | the registration; `tools/claims-v3/e206/` |
| E211's rgm211 sources, unchanged | 10 files at `kernel-e216.json` > `kernels` > `rgm211` > `sources_sha256` (`host/main.cpp` `327f49b1...` among them) | `tools/claims-v3/e211/rgm211/` |
| the box's src/ list | `src/SRC-SHA256SUMS` (what E208's `check_mms.py --box` reads: every src/ file but itself) | `box/SRC-SHA256SUMS-e216` |
| the reboot gate and its records, unchanged | `fwgate/fwgate.py` (`4d529a57...`) and 6 records | `tools/claims-v3/fwgate/` |

**THE SCHEDULE** (`box/a2c0-E216.json`, `42c425da...`), made by `make_box_e216.py` from three registered files and nothing else, each at its pin:
`plan-e216.json` (`35090542...`: the order, each run's role, block, form, est_s and planning peak, the anchor), `points-e216.json` (`63899cae...`:
each point's arm token, format, mask and loop) and E209's registered `sched-e209.json` (`ec8713a7...`: E208's forms, timing, process and smoke,
which E216.md 6 names). Every point's data is random in E208's form (`<arm>:randn:src/tiles/<fmt>/randn.bin`, int8 `src/tiles/int8/full.bin`,
seed 1); the kit word `1116-mmsweep` and E208's line 80.0 W are the words E208's schedule reader (`mms_common.load_sched`, unchanged) requires;
E216's own line is `e216_line_w` 64.0. `make_box_e216.py check` re-makes it and compares it byte for byte. 69 runs: A1, N1, pass 1 (36), pass 2
(16), A5, N2, then the G block (runs 60-69: g07, g08, g09, g10, g03, g04, g05, g06, g02, g01).

**`src/run_e216.py` - EVERY CHANGE FROM E208'S RUNNER** (it imports `run_mms` and `mms_common` unchanged and subclasses `run_mms.Session`; for
the verifier, nothing else differs):
1. **The stop lines** E216.md 6 registers: `mms_common.Stops(70.0, 3, 70.0)` - E208's own class, E216's numbers - in place of E208's 85 W / 80 C
   for this card; the stop-path test runs with them and records them as the real lines. `mms_common.CARDS` itself is never changed (E208's
   reducer imports it).
2. **The line:** a run whose planning peak passes 64.0 W never starts (the schedule refused at load if one does).
3. **Family G:** a process whose `--values` arm is `gemmLnc<MB>x<NB>x<KB>` runs `build/e216rgm211/host/sparsity_host` (rgm211's host) with
   `--kernel build/rgm/kernel/sparsity.elf` (rgm136's ELF): E208's command line (`mms_common.host_argv`) but its first word.
4. **THE IDENTITY GATE PER PROCESS** (`src/ident_e216.py`: E211's gate in E215's form, the whole-ELF branch): right before every process (the
   smoke's, the anchors', every run's) its `--kernel` passes for its family (`rgm136 gemmL` or `rgm136 gemmLnc`): the `.text` pin `61315bf6...`
   AND the whole ELF pin `aace138c...`; a refusal starts no process and stops the session (THE IDENTITY GATE STOP); every gate's words go to the
   session's `gates.jsonl`.
5. **THE WALK CHECK** on every family-G process: rgm211's host's walk `mn` and `walk_ok` true on every launch, no tag, the check record's
   `walk_launches_bad` 0.
6. **THE KERNEL STOPS** on family G (E211's, for a kernel family new on the card): a G process with rc not 0 (a launch timeout among them), its
   check of C not exact or approx, a tensor error or a failed walk check stops the session at once.
7. **THE G BLOCK LAST:** the runner refuses a schedule in which a G run comes before a run of another family.
8. **The box check**, after E208's unchanged one: `build/BUILD-e216.json` today's BUILT on aifoundry2, rgm211's host at the sha256 it records,
   `ident_e216.py --check` CHECK PASS, rgm136's ELF passing for both families.
9. **`--dry`:** rgm211's host's double is `src/fake_card_e216.py` (E208's doubles imported, the walk fields added; desk knobs `--g-walk-fail`,
   `--g-check-wrong`, `--g-tensor-error`, `--g-slow`, `--g-extra-w`, refused without `--dry`).

**THE SECOND BUILD** (`src/build_e216.sh`, run by step 6 right after E208's `src/build_mms.sh`, which is unchanged): E211's rgm211 sources (10 of 10
at their pins) into `build/e216rgm211` (nice 10, 2 jobs, a plain `timeout 900`); rgm211's host's eight refusals before its device stage, each
inside a bubblewrap with no card node; rgm136's ELF passing the gate for both families and rgm211's own ELF refused by both; the record
`build/BUILD-e216.json`. **E216.md 2's contingency, decided before any datum: FAMILY G STANDS** - the kit builds rgm211's host on this box at
E211's pins and gates every gemmLnc process by E211's family C identity in its desk tests (the build test, the runner's self-test and the real
path below).

## 2. The session

| | |
|---|---|
| the card's lines | the config gate TDP 65 W, threshold 65 C, minion 600 MHz, power state 3 (E208's for this card, read never set); **the stops E216.md 6 registers: the board strictly above 70 W on 3 samples in a row, the shires' mean at or above 70 C, the hottest-sensor latch at or above 70 C once it has risen above its first reading**; the die gate a run starts under 55 C, waited at most 180 s; the line 64.0 W |
| the schedule (E216's registered order) | the smoke (`1x1x4` fp32 zeros, fp16 ones, int8 random, 2 s each), then 69 runs (A1, N1, pass 1, pass 2, A5, N2, the G block last); a burst = 10 s at rest, one process of 6 s (a 7.5 s budget) under a plain `timeout 10`, 5 s at rest; a null = 20 s, a 6.5 s window with no process, 20 s |
| the card time | no run starts after 45 card-minutes from the session's config read; the session ends at 55; the deadline is the window's last end; 29.85 card-minutes planned |
| a stop | touches the hosts' `--stop-file` (a host ends at its next launch boundary); a device process alive past its timeout's TERM is a LEFTOVER: the session ends at once, makes no closing read, holds the card's lock until no device process of ours is left (at most 10 minutes); nothing is ever killed |

## 3. The runbook ([`rb/`](rb/); the card lane's brief: [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

Every step is a local script on aifoundry2 (no ssh), sourcing `rb/rb_e216.sh`, with k6's exit codes and bounded waits (at most 520 s a call):

| step | script | what |
|---|---|---|
| 0' | `rb/s00_sealed_e216.sh` | S1, THE SEALED-FORECAST CHECK: every sha256 of the round's record on a line that is not a comment registered in `tools/claims-v3/sealed-e216/e216-freeze-lines.md` at HEAD; a comment line (a later seal) listed with the later note that holds it; fix-e216: a record that exists but cannot be read is refused (10), and a seal is read in either case of hex |
| 1 | `rb/s02_window_e216.sh <G>` | THE WINDOW: last start G + 1:30, last end G + 3:30 rounded up, G at 20:29:00 or earlier; `window.env` |
| 2 | `rb/s03_desk_e216.sh` (outside the kit's list; its sha256 compared with the land's anchor before it runs) | THE DESK CHECK: outside a desk test THE ONE-LAB RULE's desk span held; HEAD = GitHub's main (a fast-forward under the lab-git lock when due); the paths clean; the registration and the kit by content; THE HISTORY CHECK (`rb/check_history_e216.py`: additions only under the folder since the registration, net and commit by commit); seven lists at their pinned counts and own sha256 (E216's registration and kit, MM1-v3.1's, MM1-v3's and MM1-v2's folders, E208's registration and src/); **the frozen scorer PRINT-ONLY** (`score_e216.py --forecasts` byte for byte `logs/forecasts-print-e216.txt`; `--selftest-standins` into RB_OUT byte for byte the registered `selftest-standins.json`): **no registered maker is run** (E215's lesson); `make_box_e216.py check`; `preflight_e216.sh` GO; the kit's desk-test logs; THE FREEZE LINE; the sealed record (S1); no E216 datum in any ref |
| O, Q | `rb/quiet_e216.sh others [--wait]`, `raise|lower|check <lane>`, `count [--wait]` | THE ORDER (every other card lane of ours holding a booking past its launch step: its marker, named in RB_LAUNCHED, written after its booking; an orchestrator's hold REPORTED) and THE QUIET DESK FLAG (raise reads THE ORDER again; never another's flag overwritten or removed) and THE P2 COUNT |
| 5 | `rb/s07_sync_e216.sh` | THE SYNC: `make_box_e216.py sync <root>`, every file read back at its sha256 (before the look on a new box root) |
| 4 | `rb/s05_look_e216.sh` | THE LOOK: fwgate's look (no device), et-who, the device processes, CI jobs, the card's lock, the box root's lock |
| 6 | `rb/s08_build_e216.sh start|wait` (`rb/s08_builds_e216.sh` the two builds back to back) | THE BUILDS: E208's `build_mms.sh`, then E216's `build_e216.sh`, from the root, each under a plain `timeout 900` (two starts a day at most) |
| 8 | `rb/s10_dry_e216.sh start|wait` | THE DRY PASS: the root's `dry_e216.sh 0.02` |
| 6n | `rb/s06n_neverrun_e216.sh` | THE NEVER-RUN SEARCH REPEATED (`desk/neverrun_card_e216.py`: the registration's scan and rule, each point judged by its own token and a G point's twin's, every counted record dated against the freeze line; REPORTED; its labels to step 13) |
| 7 | `rb/s09_reads_e216.sh` | THE READS: the window, the flag, both builds and the dry pass of today, the P2 count, 6n under 30 minutes old, one session a day, THE REST RULE (`rb/rest_rule_e216.py`) BEFORE anything reaches the card, et-who free; fix-e216: THE CPU RULE's load gate (17 while the 1-minute load is 6 or more); then fwgate's look, its one read when NEEDS-READ, its guard; the stamp |
| 9 | `rb/s11_session_e216.sh` | THE SESSION: within 120 s of the stamp, the rest and fwgate's guard again, the P2 count, THE CPU RULE's load gate (fix-e216), then the root's `start_e216.sh` |
| 10 | `rb/s20_wait_e216.sh` | THE WAIT: the session by its real script name and E208's `status_mms.sh`; a LEFTOVER reported, nothing killed |
| 11 | `rb/s22_collect_e216.sh` | outside a desk test, THE ONE-LAB RULE's collect span held; THE COLLECTION (`collect_e216.py`): the box-tree gate, COPY-BACK EXACT, E208's data checker unchanged (C0-C8, REPORTED), THE MASK (fwgate's ledger line's home as "~" in the committed copy only), THE SCRUB, the data directory with README (`DATA-README-FORM-e216.md`) and SHA256SUMS; the flag lowered |
| 13 | `rb/s24_score_e216.sh` | after the data commit: the manifest read (`collect_e216.py --manifest-check`: one line by THE MASK); E208's reducer unchanged on the committed session; the labels checked (`rb/post_e216.py labels`); `score_e216.py` (frozen) with step 6n's labels; then `rb/post_e216.py after` (REPORTED: NO DATA named by family, the session's stop); then `report_e216.py` (fix-e216: Amendment 1's REPORTED readings); outputs in RB_OUT only |
| E | `rb/end_e216.sh` | THE END OF EVERY PATH: the flag, the desk or collect span, the hold line, the booking, each only if the lane's; nothing under a running session, nor while a device-named process of ours is alive or a session's `queue.json` records an unresolved leftover (17: everything kept) |
| - | `rb/list_steps_e216.sh` | THE DRY LISTING (nothing run) |

## 4. The readings stated here before any datum (where E216.md leaves a choice to the kit)

1. **The runner is E208's, imported** (section 1): E216.md 7 pins E208's reducer as the measured side, so the session must be E208's runner's
   form; family G and E216's lines need code E208's runner does not have, so `run_e216.py` subclasses it and changes only what section 1 lists.
2. **THE IDENTITY GATE on this card is the whole ELF** (this box's riscv gcc builds rgm136 at E136's whole-ELF pin, as E208's, E209's and E212's
   sessions here gated it), for both families; the loadable identity is recorded, never taken in its place.
3. **THE KERNEL STOPS on family G** are E211's (and E213's and E215's): rgm211's host never ran on this card. One failed G process stops the
   session; E208's two-in-a-row rule stays for the gemmL family.
4. **THE QUIET DESK FLAG's order** (E216.md 6, E213-answers item 13's form): `rb/quiet_e216.sh others` reads the bookings (`book.sh show`); a
   booking of another card lane of ours is past its launch step when its launch marker (E215's `RB_OUT/e215-T0-<arm>.txt`, written by its
   step 9, named in RB_LAUNCHED by the go lines) was written at or after its booking's time; an orchestrator's hold (`orch-...`) is not a card
   lane's and is REPORTED; a card lane's booking with no marker named is waited for. `raise` reads it again.
5. **The card time is counted from the session's own config read** (E208's runner, unchanged: `t_first`). When step 7 sends fwgate's one
   firmware read (NEEDS-READ), that read is the day's first card command and precedes the config read by at most 120 s (step 9's bound).
6. **A session that never reached the card is not a session on the card** (E209's reading, kept): E208's runner writes `t_first_ms` null when
   it ended at a gate before its first card command; THE REST RULE lists such a session and never counts it; "one session a day" counts only
   sessions that reached the card.
7. **A gate stop after the session reached the card** is collected and committed as the day's record and never reduced; a second session needs
   a dated amendment beside E216.md (step 2 refuses while an E216 data path exists in any ref).
8. **The clock in every sample:** the sampler's `mhz.minion` in every telemetry line; a step inside a busy window is flagged by the frozen scorer
   (STEP, route m: E216.md 7).
9. **No SIGKILL anywhere:** E208's runner sends SIGTERM only (a plain `timeout 10` on every device process, never `-k`) and leaves a device
   process alive past its TERM as a LEFTOVER; no E216 file sends or arranges a kill; the real-path cases read every record of each case for a
   kill word and every process for rc 137 or -9.
10. **Step 7 only once the rest has opened:** step 7 reads THE REST RULE before fwgate's look and before any card command; refused, it sends
    nothing; step 9 reads the rest again.
11. **The release records:** E208's and E212's (`RB_RELEASES` names both, joined by ':', and any later one the go lines add); every line naming
    aifoundry2 card 0 counts.
12. **Step 6n's judgement** (`desk/neverrun_card_e216.py`, REPORTED, never a gate): the registration's scan form, leaving out by name E216's own
    lanes (its records name every E216 token) and E215's card lanes (aifoundry3 card 0 and aifoundry1 card 1 by their bookings; E215's kit
    refuses any other box), and reading E215's committed data once E216's registration is on GitHub's main (before that it refuses, exit 5, a lab
    holding an E215 data folder: the registration's scan refused one outright). **A point is labelled 'ran before' only on evidence of a run on
    this card dated before the freeze line** (a measured point; a committed data file counted for this card; a lane file in a folder naming
    aifoundry2 or a2c0; a session record by its name in a folder naming no card); a lane file counted only because its folder names no card and
    that is no session record (an arm list, a plan, a desk scan) is REPORTED and never labels a point (the kit's desk run of this step at 11:33
    PST found the model session's E217 plan copy `W/out/data-e217/work/src/arms.json`, copied into the round's folders at 11:20 PST after the
    registration's scan, naming `gemmL1x8x24`, y08's token, for its aifoundry1 sessions: by the literal rule y08a and y08b would have left every
    rule; by this reading they stay, the hit REPORTED). **Registered by the registration's Amendment 1, A3 (fix-e216, before any E216 datum)**: since 13:14-13:17 PST E217's registration copy under `W/out/data-e217/work/reg-tree/` also names f01-f07's tokens, so the literal rule would now remove 9 points (y08a, y08b, f01-f07); this reading keeps them, every hit REPORTED. The orchestrator confirms it.
13. **The sealed record** (step 0's S1 and step 2's check 10): a sha256 the round's record lists on a line that is not a comment must be
    registered in `tools/claims-v3/sealed-e216/e216-freeze-lines.md` at HEAD before the booking; a later seal's record line is a comment.
14. **The data directory's name** is `docs/reports/data/<day>-e216-blind-matmul-aifoundry2/` (the day of the session's T0); its README holds no
    forecast number and no score.
15. **The labels are checked before the scorer reads them:** step 13 runs `rb/post_e216.py labels` on `RB_OUT/ranbefore-e216.json` and refuses
    (10) when an entry names no point of `points-e216.json` (the frozen scorer echoes a label as applied without checking it).
16. **The points the scorer leaves out unnamed are named** (step 13's `rb/post_e216.py after`, REPORTED): every point with no run read, with
    route m only, or with time but no energy, by family; and the session's stop.
17. **E keeps everything after a LEFTOVER** (E209's fix): `rb/end_e216.sh` refuses (17), releasing nothing, while a device-named process of ours
    is alive or a box-root session's `queue.json` records an unresolved leftover.
18. **THE ONE-LAB RULE in the steps:** outside a desk test, step 2 refuses (10) unless `onelab.sh show` lists the lane's desk span and step 11
    unless it lists its collect span; in a desk test each only reports it.
19. **The order of steps 4 and 5 on a new box root** (E209's kit note 1, section 4): the sync before the look (the look runs fwgate from the box
    root, which only the sync fills).
20. **THE MASK** (E209's kit note 1, E200's registered form), registered here before any E216 datum: fwgate's read record's one ledger line
    holds the box's home on every real READ; the collection writes it "~" in the data directory's copy only, and step 13's manifest read takes
    that one line back; any other private string stops the collection.
21. **Where fwgate's one read lands** (E216.md 6 says "--out <the data folder's fwgate/>"): in E209's form, the read's record goes into step 7's
    folder `first/<FIRST>` in the box root (`fwgate.py read --box aifoundry2 --card 0 --out <E216_ROOT>/first/<FIRST>`: one card on this box, no
    --both-nodes-ok), `start_e216.sh` copies that folder into the session's `first/`, and the data directory commits it as `session/first/`
    (its ledger line masked); the launch guard is `fwgate.py guard --extra <that folder>` at steps 7 and 9. The record, its words and its one
    call are the registration's; only the folder's name in the data directory is E209's.
22. **THE CPU RULE's launch gate** (fix-e216, verify-e216's F8): steps 7 and 9 read the host's 1-minute load (`/proc/loadavg`) and refuse,
    17, while it is 6 or more: at step 7 after the free check and before fwgate's look (nothing sent), at step 9 right before the launch
    (nothing launched; step 9 is called again within the stamp's 120 s, else step 7 again). The orchestrator keeps aifoundry2's other
    lanes light while the session runs.
23. **S1 reads every record it is given** (fix-e216, verify-e216's F7): a record that exists but cannot be read stops the day (10, never
    "sealed 0 of 0"); a seal's 64 hex digits are read in either case and compared case-insensitively with the notes.

## 5. THE REAL-PATH DESK TEST and the audit of every dry branch

A dry pass never runs the branches its flag skips, so E216's session was run on its REAL path at the desk: `desk/realpath_e216.py` makes a box root
with `make_box_e216.py sync`, puts the REAL kernel ELFs (rgm136's at E136's pin; rgm211's own, for the gate's refusal) and stand-ins at the built
hosts' and reader's paths (`desk/standin_e216.py`: E208's doubles, unchanged, with the die, the latch, a clock step, a runtime line, a host deaf to
SIGTERM and rgm211's host for family G as desk knobs), and launches `start_e216.sh` exactly as step 9 does, each case in a sandbox of its own
inside W/nodev.sh, **MAIN through the whole registered schedule: the smoke, the stop path, all 69 runs and the ten G points**.
`desk/dryaudit_e216.py` then lists every line of `run_mms.py` and of `run_e216.py` that reads the dry flag, the real path there and the cases that
ran it, each PASS in the committed log. E216's runbook has no dry mode (each step is a local script; the dry listing prints it and runs nothing).

## 6. Device commands

`preflight_e216.sh` (dmcmd_audit_v2 with its table v2, no --allow, no exception) over E208's runner, modules, guard, status, stop, build and
preflight scripts and rgm136's host source, rgm211's host source, E216's box files, the collector, every runbook step but step 2 (which calls
it), the never-run tool and fwgate: **dmcmd_audit: GO (12 send site(s), 0 disallowed; allow-list: none)** - `ettelem config` and `ettelem
sample` through E208's guard (TDP, thresholds, power state, frequencies, voltages; power, temperatures, SP statistics, voltages: every one a
READ) and fwgate's one firmware-revisions read (a READ by the owner's rulings). E208's runner also runs E208's own preflight (`src/preflight_mms.sh
--audit-only`, unchanged) in its box check before its first device access. ("Reads only" is exact on the management node; every runtime creation
also sends the ops node's abort to every submission queue of every card the device layer enumerates - harmless on a card held alone, and
aifoundry2 has one card; rgm211's host is rgm136's with the walk swap and the early refusals, the same device layer.) **The host's package
counter is not read.**

## 7. The parsers and the real bytes

Every parser on E216's path that reads a device tool's output was fed the lab's committed bytes of that tool (`desk/realbytes_kit_e216.py`): E208's
`parse_sparsity` read every host stdout of E209's session and of E212's S3 re-run on this card (E208's runner's own form, the form E216's
session writes), each process's launch count equal to the runner's own; `parse_ident` read exactly /dev/et0_ops and physical device ID 0 on
every host stderr and /dev/et0_mgmt, ID 0 on every config read. **Family G's own parser, the walk check** (`run_e216.walk_read`), read every
committed stdout of rgm211's host running a gemmLnc arm the lab holds (E213 arm A on aifoundry3, E213 arm B on aifoundry1 card 1, E211's family
C: no such bytes exist from this card, where gemmLnc never ran) and refused rgm211's gemmLn stdouts and rgm136's own host's; E208's `ok_launch`
(the reducer's) reads rgm211's records with their walk fields; a runtime line spliced at every byte offset of a real gemmLnc launch record and its
check record never gives a changed value (the record is dropped; a lost check record is THE KERNEL STOP). **THE MASK and THE SCRUB on a real
record that carries the box's home** (E209's fwgate read record, its raw bytes rebuilt at E209's MANIFEST sha256): masked to the committed bytes
exactly, the whole collection on E209's real session passing with that one line masked and stopping on a planted home. **REALBYTES-E216 10 of 10
PASS**. The collection runs E208's data lane's checker unchanged (C0-C8, REPORTED, never a gate).

## 8. What the desk cannot show

1. **rgm211's host on this card:** the desk built it here at E211's pins and ran it only to its eight refusals; it ran gemmLnc on aifoundry3 and
   aifoundry1 card 1 (E211, E213), never on this card. The host's own sha256 depends on the box root's path, so the gates are the kernel ELF's
   bytes (both families) and the build records of the day.
2. **gemmLnc's power on this card** at 799 MHz: every G point's planning peak with the term is under 64 W (the registration's plan); a G point
   well over its forecast can pass 70 W (E216.md 6); the G block runs last.
3. **The governor's clock** on E216's points: read in every sample and every launch, never set.
4. **Our own live collector** may hold the management node for a moment at the free checks (step 7 re-reads up to three times; E208's runner
   re-reads once after 5 s).
5. **fwgate's one read** happens only if its look reads NEEDS-READ; anything but EQUAL stops E216 on this boot.
6. **The card time at the card's pace:** the plan's 29.85 card-minutes is E209's measured pace; the desk's dry pass is the doubles' pace.

## 9. Files (all new, under tools/claims-v3/e216/; every one but step 2 and the list itself in `SHA256SUMS-e216-kit`)

| file | what |
|---|---|
| `KIT.md`, `CARD-LANE-BRIEF.md` | this file; the card lane's brief |
| `make_box_e216.py`, `harness-e216.json` | the box root and the schedule: make, check, sync |
| `box/run_e216.py`, `box/fake_card_e216.py`, `box/ident_e216.py`, `box/build_e216.sh`, `box/start_e216.sh`, `box/session_e216.sh`, `box/dry_e216.sh`, `box/a2c0-E216.json`, `box/SRC-SHA256SUMS-e216` | E216's box files and the box's src/ list |
| `preflight_e216.sh` | dmcmd_audit_v2 on the day's files |
| `collect_e216.py`, `DATA-README-FORM-e216.md` | the collection (THE MASK, THE SCRUB) and the data README's form |
| `rb/rb_e216.sh`, `rb/s00_sealed_e216.sh`, `rb/s02_window_e216.sh`, `rb/s03_desk_e216.sh` (step 2, outside the list; pinned by the land's anchor), `rb/check_history_e216.py`, `rb/quiet_e216.sh`, `rb/s05_look_e216.sh`, `rb/s07_sync_e216.sh`, `rb/s08_build_e216.sh`, `rb/s08_builds_e216.sh`, `rb/s10_dry_e216.sh`, `rb/s06n_neverrun_e216.sh`, `rb/s09_reads_e216.sh`, `rb/rest_rule_e216.py`, `rb/s11_session_e216.sh`, `rb/s20_wait_e216.sh`, `rb/s22_collect_e216.sh`, `rb/s24_score_e216.sh`, `rb/post_e216.py`, `rb/end_e216.sh`, `rb/list_steps_e216.sh` | the runbook |
| `desk/neverrun_card_e216.py` | step 6n's tool (the registration's scan and rule; the judgement) |
| `desk/desktest_build_e216.sh`, `desk/selftest_run_e216.py`, `desk/realpath_e216.py`, `desk/standin_e216.py`, `desk/dryaudit_e216.py`, `desk/realbytes_kit_e216.py`, `desk/selftest_rb_e216.py` | the desk tests |
| `logs/*` | their logs, as run; `logs/forecasts-print-e216.txt` the frozen scorer's print that step 2 compares byte for byte |
| `SHA256SUMS-e216-kit` | the kit's list (step 2 pins its count and its own sha256) |

## 10. Labels, and compute

Every figure here is a desk check of code or a desk read of committed records; nothing is measured, nothing is forecast anew. The desk ran under
`/usr/bin/python3` 3.12.3 on aifoundry2 (Ubuntu 24.04, 12 cores), every numerical job inside the round's CPU slots (`W/slot.sh`, nice 10) with
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1, one slot job at a time, every test that runs a built host, the
runner or a stand-in in the no-device sandbox (`W/nodev.sh`; bubblewrap), each only while THE QUIET DESK FLAG was absent and the 1-minute load
under 6. The builds ran at -j2.

## 11. Gaps and departures (none blocks; each stated before any datum)

1. **E216.md 2's contingency is decided: family G stands** (rgm211's host built here at E211's pins; every gemmLnc process gated by E211's family C
   identity; the desk tests above). No amendment is needed for it.
2. **The runner is a subclass of E208's** (section 1): E216.md 6 says the session is E208's form with its own stops and family G; E208's runner,
   run unchanged, could do neither (its 85 W / 80 C lines for this card, its one host), so `run_e216.py` adds them and changes nothing else; its
   every change is listed for the verifier.
3. **Step 6n's judgement** reads lane files counted only for "no card named" that are no session record as REPORTED, not as runs (section 4 item
   12): a reading the registration's text leaves to the kit; at the kit's desk run it decided y08a and y08b (kept; by the literal rule they
   would have left every rule because of the model session's E217 plan copy). Registered as the registration's Amendment 1, A3 (fix-e216), which also covers the later E217 registration copy's hits at f01-f07.
4. **THE ORDER's markers** are the other card lanes' own files, named by the go lines (RB_LAUNCHED); a booked card lane with no marker named is
   waited for (the conservative side); an orchestrator's hold is REPORTED and not waited for.
5. **The pace:** the dry pass at the doubles' pace reads about 34 card-minutes against the registered plan's 29.85 at E209's measured pace on this
   card; both under the rule (45) and the cap (55).
6. **What was not run:** no card, no simulator, no other box; the real-path stand-ins are the doubles (no gemmLnc power on this card was
   exercised: the stop lines were, at E216's numbers); `mms_common.py`'s own self-check (it asserts the six schedules of E208's src/ and reads E216's
   seventh as extra; E209's kit did not run it either).

## 12. fix-e216 (Q227, Thu 19 Nov 2026, 14:30-15:30 PST, before any E216 datum): verify-e216's findings answered

verify-e216 read HOLDS WITH FIXES (14:24 PST). fix-e216 answered its findings in a fresh scratch clone at GitHub main `4f648f24`, with
both land patches applied, as new files only. The registration's items are in its Amendment 1 ([`E216-amendment-1.md`](E216-amendment-1.md)):

- A1, P1's minimum of 5 decided pairs, re-frozen;
- A2, E1-E4's expected reading if the gemmLnc term is right, and the REPORTED reading without G;
- A3, the never-run reading, registered: this kit's item 12;
- A4, the power with errors shared by configuration, and the tallies by configuration, REPORTED;
- A5, D3's basis;
- A9, section 8's words;
- A10, the freeze line's timing.

The kit's items:

| finding | the kit's answer | tested by |
|---|---|---|
| F1, F2, F3, F4 (registration) | **Re-pinned to the amended registration:** step 2's REGPIN is `SHA256SUMS-e216-registration:40:778c77aa...` and the history check's REG_SUBTREE is `a4cf984a...` (the registration's local commit `7dd28414`, 41 new files). `logs/forecasts-print-e216.txt` is re-made: the frozen scorer's print differs only in its pins line (the rules' new sha256). **Step 13 also runs `report_e216.py`** (Amendment 1's REPORTED readings) into `RB_OUT/score/reported-e216.json` and `reported.out`; it fails as 14, after the scorer's outputs are written. | the runbook test's P1-P17 at the new pins; REPORT-CLI-E216 7 of 7 (`logs/report-cli-e216.txt`: step 13's two calls in their command-line form, on stand-in days) |
| F6 (THE ORDER's markers) | **No code change** (THE ORDER waits when a booked card lane's marker is not named: the safe side). A note in CARD-LANE-BRIEF section 2: card-e215b's second booking (13:21:36 PST) writes its RB_OUT under a new name, so if an E215 card lane holds a booking when card-e216 reaches O, the ready lane names that run's actual launch marker in RB_LAUNCHED (names only). | (O1-O7 unchanged) |
| F7 (step 0's S1) | **`rb/s00_sealed_e216.sh`:** a record that exists but cannot be read (not a readable regular file, or its read fails) is refused (10), never "sealed 0 of 0". A 64-hex sha256 is read in either case and compared lower-cased, case-insensitively. Step 2's check 10 calls the same file. | **Z1** (mode 000: 10; step 2 refuses too), **Z2** (a folder: 10), **Z3** (an upper-case seal unregistered: 10, sealed 0 of 1), **Z4** (registered in lower case: sealed 1 of 1; a missing record: sealed 0 of 0) |
| F8 (THE CPU RULE) | **`e216_load_gate` in `rb/rb_e216.sh`**, called by step 7 (after the free check, before fwgate's look and any card command) and step 9 (right before the launch): 17 while the host's 1-minute load is 6 or more (nothing sent; call again). Desk tests only: RB_LOAD stands in for the load, refused outside a desk test. | **G15** (7.25 at step 7: 17, no fwgate call, no folder, no stamp), **G16** (6.0 at step 9: 17 after the rest and the guard, nothing launched; at 0.5 the same call reaches `start_e216.sh`), **G17** (RB_LOAD outside a desk test: 10), **G18** (the host's own `/proc/loadavg` read and gated) |
| nit 1 | The runbook test reads its full count only in the stand-in form, the kit's files untracked as here; the committed-kit form skips P4-P6, P14 and P17. **After fix-e216: 92 of 92 in the stand-in form, and 87 of 87 in the committed-kit form** (the readiness lane runs it there). | the counts below |
| nit 4 | Step 1 takes G from 00:00:00 Friday, although the brief's day reads from 00:00:30. The booking step's day rule covers it, so the code is unchanged. | (W1-W6 unchanged) |
| nit 5 | CARD-LANE-BRIEF's step-0 row: the booking (B) comes before step 0, so a seal NOT REGISTERED, or an unreadable record, ends the day at E, which releases the booking. | (wording) |
| nit 6 | **G8 now also reads step 7's own words:** THE REBOOT GATE's stop, with no call of fwgate's guard. So a stop at the guard instead, verify-e216's mutation M5, would FAIL it. | G8 |

**The tests re-run** (aifoundry2, `/usr/bin/python3` 3.12.3 `-I -B`, every job in the round's slots single-threaded, the runbook test in
`W/nodev.sh`, the quiet-desk flag absent):

- **SELFTEST-RB-E216 92 of 92 PASS** (the stand-in form; a first run read 91 of 92, and its one FAIL was G8's new words check, written too
  strictly and then corrected);
- dmcmd_audit_v2 **GO** (12 send sites, 0 disallowed);
- the dry listing: 28 steps, 0 run, 0 box calls;
- **NEVER-RUN-E216 46 of 46** at the amended registration's local commit (81,440 files). 9 points carry hits that are no session record, all
  REPORTED: y08a, y08b and f01-f07, in E217's plan and registration copies under `W/out/data-e217/work/`, as verify-e216 found. None ran
  before the freeze line;
- **REPORT-CLI-E216 7 of 7**;
- the kit's checks (`logs/checks-e216.txt`): CHECK PASS, the identity check SAME, SCHEDULE CHECK PASS; the lists 40/40, 57/57, 48/48,
  64/64, 170/170 and 114/114 OK; the scorer's print and self-test byte for byte; `report_e216.py --selftest` byte for byte; the kill words
  as before.

**Not re-run** (no file they run changed; `make_box_e216.py check` reads the box files at their harness sha256): the builds (6/6), the
runner (13/13), the dry pass, the real bytes (10/10), the real path (29/29), the dry audit (33/33) and step 13's labels and readings
(`post_e216.py`, 8/8).

**After the kit's local commit:** step 2 ran for real at the committed kit's own pins (desk mode), and the runbook test was re-run in the
committed-kit form as a confirmation. fix-e216's result and its land dirs `OUT/fix-e216/land-reg` and `land-kit` hold their logs.

SPDX-License-Identifier: Apache-2.0
