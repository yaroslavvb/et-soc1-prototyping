# E195's run kit: a lab port of the proposal's session that keeps every arm, order, window and stop, its record read whole, no SIGKILL anywhere, the memory shires' counters not read (their clear-free reading not established at the card's running build), the runbook from aifoundry2, THE REAL-PATH DESK TEST with its audit of every dry branch, and THE REAL-BYTES TEST (Q185; fixed in Q191 before any datum; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q185, lane `kit-e195`). No card was claimed or opened (aifoundry2 has a card:
every desk test that ran the session, the runner, a stand-in or a built host ran in the round's CPU slot inside the no-device sandbox, each
real-path case in its own sandbox inside it, and only while THE QUIET DESK FLAG was absent), no device command was sent, no lab box was
reached, nothing was posted, no simulator ran. New files only, all under `tools/claims-v3/e195/`, on the registration's local commit
(`tools/claims-v3/e195` subtree `7b9aa484...`, `SHA256SUMS-e195-registration` `ba6849ce...`, 41 entries, made by lane `reg-e195`), every
file of which stays as committed. This is the kit E195.md section 18.2 asks for. **No E195 datum exists, and the forecast stays sealed:
no forecast number is in any file here, and nothing here scores against it.** Nothing here changes an arm, a value, the order, a window, a
threshold, a stop, the cap, a rest or the reduction. Where E195.md leaves a reading to the kit, it is stated in section 4 before any
datum. **The card** is the one E195.md section 3 identified from the lab's records, read again here: E75 ran on aifoundry3 (its entry in
`docs/findings/03-experiments.md`), E139 on "aifoundry3 card 0, 600 MHz" (its data README), and aifoundry3 is pinned at 600 MHz by a zero
TDP (`docs/findings/14-card-behaviour.md`); aifoundry3 has one card. **Fixed in Q191** (lane `fix-e195`, Sun 15 Nov 2026, before any
E195 datum and before this kit landed): verify-e195's seven findings are answered in section 15 (the closing config read only while
`et-who --check` reads the card free, as the registered session reads; the one-lab calls on every stop path of the brief; where the cap
counts from, read and dated before any datum; the rest rule's no-device line; the dry listing re-made and its sample day today; the
runbook's dry branches audited line by line). No arm, value, order, window, threshold, stop, number, rest or reduction changed.*

## Results first (desk checks of code; nothing is measured)

Python everywhere: `/usr/bin/python3` 3.12.3 (numpy 1.26.4) on aifoundry2; cmake 3.28.3, riscv64-unknown-elf-gcc "() 15.1.0" and g++ 13.3.0
from this box's /opt/et for the builds; bubblewrap 0.9.0 for the sandboxes.

| check | result | log |
|---|---|---|
| **THE REAL-PATH DESK TEST**: `session_e195.sh`'s real path, DRY unset, exactly as step 9 launches it, and through it the kit's blocks, the registered lib_x09.sh and lib.sh, the kit's runner, the registered watcher and smoke gate and E128's guard, against stand-ins for every device tool (`fake_card_e195.py`: the sampler and its config, the heater and anchor, the host printing X09MEM lines, et-who and the holder helper behind sudo), each case in its own sandbox (a plain scratch file at /dev/et0_ops, its own card lock file, a private PID namespace, the host name aifoundry3) and its own stand-in box (the session's stop file lives in E195's root): **P at real timing through the smoke and passes 910 and 911 whole, then the operator's stop; F the whole session; the runtime line inside every record (SP, S2, SL); a crash (X1); every live stop (B1 on the live .raw, D1, T1); a stuck sampler never killed (K1); the holders (H1-H4: H2, H3 and H4 assert no closing config read while another user holds the card), the lock (L1, L2), the node count (N2, N0), the config gate (C1), both smoke gates (G65, GP, G2), signals to the session (SG) and to a block (BS), a dead watcher (DW), the deadline (DW, DL), the session's stop file alone (NR), the dry path (Y1), nine refusals (R1-R9) and the preflight's NO-GO (PF)**; THE REGISTERED REDUCER and the kit's leftover checker on P's passes; and THE AUDIT of every dry branch | **DESKTEST-REALPATH-E195 199 of 199 PASS** (Q191: 22:28-22:39 PST, the fixed kit; Q185's run 190 of 190 at 17:04-17:18): P: the first card command stamped, both config reads through the guard under the card lock, the watcher, the smoke's 8 device calls and both smoke gates, passes 910 and 911 whole in the registered order (33 runs each), 66 host calls each `--no-ms` and under the block's card lock, the operator's stop before p912, each of the 3 samplers stopped by one SIGTERM; **the registered reducer on P's two passes (headline [911], warm-up 910, nothing set aside) and the leftover checker**; F: the 8 passes in the registered order, exit 0; SP, S2, SL: 310 records a pass read whole, the dropped line logged in 31 runs; X1: a traceback, exit 4; B1, D1, T1: each live stop; K1: the stuck sampler never killed (two SIGTERMs, no SIGKILL), the closing read skipped, no second sampler; BS: the host in flight ended by itself with the lock still held, no SIGTERM to the runner; H2, H3, H4: the closing config read not sent while another user holds the card (one config read, the start's; two `et-who --check` calls; the "not read" line); in every case nothing left and nothing killed (every device stand-in's start matched by its own end); the audit: 27 lines, each with a row whose cases passed | [`logs/desktest-realpath-e195.txt`](logs/desktest-realpath-e195.txt) |
| **THE REAL-BYTES TEST**: the kit's runner itself on replays of committed card bytes (aifoundry1's split line of 1a4bc1e3 and all 31 host lines of E191's second session; aifoundry3's four E193 device-stdout files; the runtime line at every byte offset of a real aifoundry3 line), the registered runitems.py beside it as the negative control; where aifoundry3's runtime writes (E192's and E193's stderr); the census of the runtime line in the lab's raw records | **REALBYTES-E195 8 of 8 PASS**: RB1 the split line read whole (status PASS, 2,048 records) and the registered runitems.py's JSONDecodeError (the defect reproduced); RB2 31 of 31 host lines of E191's second session read whole, the registered runner failing all 26 with the line inside; RB3 aifoundry3's 30 X04 records read identically by both, 0 lines dropped; RB4 728 of 728 offsets, two lines, the line's start, and the runner at 10 offsets; RB5 an unknown text fails closed; RB6 706 runtime blocks on E192's stderr, none on any stdout; RB7 800 at a line's start, 17 inside a host's line, 91 quoted, 0 of another form | [`logs/realbytes-e195.txt`](logs/realbytes-e195.txt) |
| **the runbook** with a fake ssh and rsync on a stand-in box (the box's build REAL: cmake with this desk's /opt/et, check_elf.py, the arm table, the generator's check with numpy): the window rule, the lab-git lock (absent and nested), step 2 at every pin, the history check and its shadows, an E195 datum in a ref, the sync, the build and its count, the login check, a hang, a cut wait, **step 7's rest gate before its config read**, the dry pass, the rest rule and a left stop file through step 9, **the real session_e195.sh launched and found by the wait by its real script name** and a decoy, no second session that day, the collection, **the registered reducer and the leftover checker on the committed data**, a changed box file, **a gate stop collected as its record under gate-stops/** | **SELFTEST-RB-E195 22 of 22 PASS** (Q191: 22:40-22:52 PST, its new last case AUDIT-RB: the runbook's 60 lines that read RB_DRY, each with a row whose cases passed in that run; Q185's run 21 of 21 at 17:06-17:18; RB_LOCK a copy of the round's lock file of checks, RB_GITLOCK a scratch lock; the stand-in session ran the smoke and passes 910 and 911 at the host's real launch timing, then the operator's stop) | [`logs/selftest-rb-e195.txt`](logs/selftest-rb-e195.txt) |
| **the rest rule**: E183's, E189's, E192's, E193's, **E188's** and E195's own forms, a dry pass, refusals and gate stops that opened no device, a cut E195 session at its data folder's latest write, energy.sh's folders, the newest of several, and the real-path test's own P log; a session that ran with the phrase inside a copied tool text (R17) and another kit's no-device ending (R18) | **SELFTEST-REST-E195 18 of 18 PASS** (R16 on the logged real-path test's P log; R17 and R18, Q191: the no-device line, the old rule failing both) | [`logs/selftest-rest-e195.txt`](logs/selftest-rest-e195.txt) |
| the dry listing, every step with stand-ins | 13 steps listed, 0 exited non-zero, **0 box calls** | [`logs/dry-listing-e195.txt`](logs/dry-listing-e195.txt) |
| `dmcmd_audit`, every file the session's chain runs, sources, builds or reads (`preflight_e195.sh`) | **GO, 44 send sites, 0 disallowed**, no allow-list; every send site a READ but the one reviewed, conditional exception the registered preflight carries (lib.sh line 154's forwarded arguments, STATS_RESET; E195's sampler forwards none: section 7) | [`logs/dmcmd-audit-e195.txt`](logs/dmcmd-audit-e195.txt) |
| the quick set (`desk/checks_e195.sh`): compile and parse; the harness; the ports re-made by their exact replacements; the dry listing against the registration's; the audit table re-made; the preflight; **the kit's generator output from the registered source built here**; the rest rule's one changed line; the sampler's stop changed only in its SIGKILL branch; the history check's names and no datum; the runbook's audit table re-made (Q11, Q191) | **CHECKS-E195 11 of 11 PASS** | [`logs/checks-e195.txt`](logs/checks-e195.txt) |

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** E195.md (the registration, its freeze line, the local registration commit); E192's and E193's kits (their KIT.md, briefs,
   runbooks and desk tests, their go lines and how their card days went: E192 ran FULL on Sat 14 Nov 2026, its data note 1 the lesson that
   step 7's config read ran before the rest; E193 ran both sittings FULL on Sun 15 Nov 2026); E188's port (its session form on aifoundry3,
   whose session log the rest rule reads); E191's kit note 2 (`2d0fe517`: the JSON-split fix, the real-bytes test, the relaunch rule); k6's
   runbook drivers; the round log's sections 104, 109 and 116 (the lessons).
2. **Used, unchanged** (called, sourced or run by path; sha256 in [`SHA256SUMS-e195-kit`](SHA256SUMS-e195-kit) and the harness): the
   registered `proposal/src` (lib_x09.sh, watch_x09.py, smoke_gate_x09.py, make_x09.py, check_elf.py, reduce_x09.py, the host and kernel
   sources) and `desk/` (loops_e195.py, the arm table, the order); the lab's `lib.sh`, `text_hash.sh`, E128's `ettelem_guard.sh`,
   `dmcmd_audit.py` with `dmcmd_table.json`; k6's `rb_common.sh`, `s05_look_k6.sh` and `s09_a3_reads_k6.sh` with v3.1's `rb_run.py` and
   `nopath_q142s.py`; E183's desk-path gate; E178's scrub; E193's rest rule's code (line for line, but its refusal's words).
3. **Not used:** any forecast number; any private page; a simulator; any other card.
4. **Tiers:** every file here is public tier and cites public pieces only.
5. **Readiness:** this kit gates nothing by itself: a verifier, a fix pass and a readiness check come next, then the owner's go.

## 1. The session: a lab port of the proposal's session, and why (not the registered session as committed)

**Which.** `session_e195.sh` is a lab port of the registered `proposal/src/session_x09.sh`; its blocks are `block_e195.sh`, the registered
`block_x09.sh` made by **nine exact replacements** (desk/port_e195.py, `--check` re-makes it byte for byte), with **`lib_e195.sh`** sourced
after the registered `lib_x09.sh`; its runner is **`runitems_e195.py`**, the lab's `runitems.py` made by **four exact replacements**.
Unchanged and run as registered: lib.sh, lib_x09.sh, watch_x09.py, smoke_gate_x09.py, make_x09.py's output (gen-e195-noms/), the host and
kernel built from proposal/src, check_elf.py, reduce_x09.py.

**Why a port.** The registered session cannot run as committed under the lab's rules, for four reasons E195.md itself names: (1) lib.sh's
`stop_sampler` SIGKILLs a sampler that ignores SIGTERM for 30 s, and block_x09.sh's signal path SIGTERMs the runner while its device process
runs (a host whose stdout is the runner's pipe then dies at its next record by SIGPIPE: the real-path case BS found it on the stand-ins),
where E195.md 10 says the kit replaces that branch and kills nothing; (2) runitems.py reads each record by one `json.loads` of a stdout line,
which a runtime line inside it would break (CONTEXT 116; E195.md 4 asks the kit to read it whole); (3) the kits' session form (its files in
`build/e195/T<T0>/` of the box's tree, where every rest rule of ours reads them; MANIFEST.sha256 last for the exact copy-back) and each
session's data in its own folder, so no earlier session's pass is ever skipped as "already done" by lib.sh's block_begin; (4) E195.md 18.2's
gates around the session (the pins, the first card command, the one ops node, the start config gate, the cap, the kit's 65 W / 65 C smoke
gate). Every arm, value, order, pass, window rule and stop of the registered session is kept: the smoke 901 and its items, passes 910-917
(910 the warm-up), the registered smoke gate, the watcher (70 W on 3 samples, on the live telemetry), the die stop at 70 C, the 38-minute rule,
the deadline rule with the longest pass so far (360 s until one has run) and 60 s for the close, 15 s between passes, a pass in flight never
cut, a pass that fails ending the queue; the runner's approach, shuffle, anchor, burn-ins, `timeout 10` and records.

| session_x09.sh | session_e195.sh | why |
|---|---|---|
| its files in the tree's `build/x09/` | `<tree>/build/e195/T<T0>/` (the box's tree, ~/aifoundry); "session start", "session end (T0 <T0>)"; MANIFEST.sha256 last (the session directory and its data folder, paths from the tree's top), session.rc after it | the rest rules of every later kit read `build/e*/T*/session.log`; the collection's exact copy-back |
| data in `build/claims-v3/<card>/x09/` | `build/claims-v3/aifoundry3/x09-T<T0>/` in E195's root (`X9_EXPN`, a knob of the registered scripts) | a second session never meets an earlier one's passes as "already done" |
| refusals: the tree, the window, USER, stop files, the preflight | the same, and: the host's name aifoundry3; E195's root path; harness-e195.json at the launch's sha256 and every file at its pin (HARNESS OK); today's build record and the host, kernel, sampler and heater at its hashes; this T0's data folder new; preflight_e195.sh (the kit's file set) | E195.md 18.2: nothing runs that is not pinned |
| `et-who`, then the config read only while `et-who --check` reads free | THE FIRST CARD COMMAND is the holder check (lib.sh's two ps rules and `et-who --check`), stamped as it starts; exactly one ops node `/dev/et0_ops` and the lock file; then the start config read through E128's guard under the card lock (`timeout 10`): TDP 0 W, 65 C, 600 MHz as found, else GATE-STOP; **the closing config read likewise only while its own `timeout 20 et-who --check` reads the card free** (else "closing config read: not read (et-who --check does not read the card free ...)", its lines in etwho-check-end.txt: Q191, verify-e195's finding 1) | E195.md 3 and 6: one card, as found; the cap counts from the session's first card command (section 4); the registered cfg() at both ends (request.md 8.3, 9) |
| `X9_DEADLINE` as given | the earlier of `X9_DEADLINE` (step 9 sets it to the earlier of the window's last end and the launch + 45 minutes) and the first card command + 45 minutes | E195.md 6 |
| the registered smoke gate | the registered gate, then the kit's: the smoke's highest board reading below 65 W and its highest die reading below 65 C (`check_e195.py smoke`, every sample of the smoke pass, the heater bursts included) | E195.md 5 (the lab's choice) |
| blocks in the foreground; no trap | blocks in the background, waited by `bg_wait`; TERM, INT, HUP write the session's stop file and the running pass's STOP and the session closes (the block is waited for, never killed) | a signal stops the session cleanly |
| — | a stuck sampler stops the queue and the closing config read is skipped | nothing opens the management node beside it |
| `--dry`-less dry runs (`V3_DRY=1` per block by hand) | `--dry`: every refusal and pin, then each block with `V3_DRY=1`, the listing checked against desk/dry-e195-noms-aifoundry3.txt (`check_e195.py dry`) | step 8's dry pass |
| exit 0 / 8 / 3 | 0 the queue ended by the plan (every pass, the 38-minute or the deadline rule); 1 a live stop, a holder, a failed pass or the operator; 3 a gate; 4 a pass that ended without a registered stop (runitems exit 1, a traceback); 8 a refusal | step 10 reads them |

**block_e195.sh's nine replacements** (desk/port_e195.py `--diff` prints each): the header; X9 = the registered source beside the port;
lib_x09.sh from X9 and **lib_e195.sh** after it; the preflight's file check, the build hint, the listing, code.sha256 and the run naming
runitems_e195.py and X9; and **the signal path**: `on_signal` calls lib_e195.sh's `x9k_on_signal` (below).

**lib_e195.sh's four functions**: (1) `stop_sampler` is lib.sh's but for its SIGKILL branch: a sampler still alive 30 s after its SIGTERM is
never killed and no drain is sent: it is left to end at its own `--seconds` bound (the pass's estimate plus 900 s); the block writes the
pass's STOP, the session's stop file and `<pass>/SAMPLER-STUCK`, copies what the sampler wrote and leaves its .raw file; (2) `start_sampler`
is lib.sh's without the extra-argument forwarding (no word but `--seconds` and `--every-ms` can reach `ettelem sample`) and starts no sampler
while a stuck one lives; (3) `die_c` sends no management read beside a stuck sampler; (4) **`x9k_on_signal`**: a signal to a block writes the
pass's STOP and the session's stop file FIRST, lets the runner end by itself at its next item (at most 180 s; the host in flight stops after
its launch because it reads the session's stop file, the heater after its calibration launch), never signalling it while it runs (only
after 180 s does it get the registered SIGTERM, reported), then stops the sampler and keeps the card lock until no device process of ours
runs (`x9k_wait_ours`, at most 30 s, never a signal). Under `V3_DRY` lib.sh's stubs stay.

**runitems_e195.py's four replacements**: a docstring head; `import re`; `drop_runtime()` (E191 kit note 2's `RUNTIME_LINE`,
`Opening device [0-9]+\n`, removed wherever it fell, and the lines removed); and the record loop reading `drop_runtime(r.stdout)` with one
run.log line naming the dropped text when there is any. A JSON line holds no raw newline, so the removal never cuts into the host's own text;
every other byte is read as runitems.py reads it (an unknown text inside a record still fails the parse and ends the pass: never a wrong
datum). No record, mark, exit code or order changes: the dry listing is the registration's, call for call (but `--no-ms`, section 4).

## 2. The box: E195's root, and the box's tools

- **E195's root** is `build/claims-v3/aifoundry3/e195` under the box's tree (`~/aifoundry`): a folder of ours. Step 5's `rsync -R` puts
  each harness file at its repository path there (the registration's 41 and its list, the kit's box files, the lab's lib.sh, text_hash.sh,
  E128's guard, dmcmd_audit.py and its table); step 6 builds into its `build/x09mem` and writes `build/x09mem-built.txt`; each session's data
  go to its `build/claims-v3/aifoundry3/x09-T<T0>/`; the session's own files to the box tree's `build/e195/T<T0>/`.
- **The box's tools**, unchanged: `et-who --check`, the card lock `/run/lock/etsoc-shire0.lock`, coreutils' `timeout`, util-linux's `flock`,
  **the sampler `build/ettelem/ettelem` and the heater and anchor `build/sparsity/host/sparsity_host`, the box tree's own builds**, which
  every aifoundry3 kit uses (E132 and E139 ran this very runner and heater on this card): step 6 links them into E195's root (the block library
  finds them there), reads each by sha256 into the record, and reads the heater's option parser by behaviour (E192's way: the registered
  heater arguments and `--stop-file`, then an unknown option: exit 2 at it, before anything). The session checks both against the record.
- **The generator's output** the session runs is the kit's committed `gen-e195-noms/` (make_x09.py `--no-ms` from the desk build's host;
  step 6 re-makes it on the box from the box host's bytes with the tree's numpy and compares it byte for byte, where the tree has numpy).

## 3. The runbook from aifoundry2 ([`rb/`](rb/); the card lane's brief: [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

Each step a script in E192's form through k6's drivers, unchanged (a 15 s hard-killed probe; 60 s for a read, 600 s for a copy, one bounded
wait, a detached launch; a printed login link stops the step with 11 and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`,
nothing retried; exit codes 0, 10-17). One RB_OUT.

| box step | file | what |
|---|---|---|
| 0 | (by hand) | `uptime` (THE LOAD RULE), `onelab.sh desk`, the anchor lines |
| 1, the window | [`rb/s02_window_e195.sh`](rb/s02_window_e195.sh) `<day> <last start> <last end>` | today only; the cap (2,700 s) before the last end |
| 2, the desk check | [`rb/s03_desk_e195.sh`](rb/s03_desk_e195.sh) (outside the kit's list) | the window; the pull under the lab-git lock (never nested: 16); HEAD descends from e8a85229, the registration (by its content, subtree 7b9aa484) and the kit (by its content); the paths clean; the history check ([`rb/check_history_e195.py`](rb/check_history_e195.py)); both lists at their counts and their own bytes, every entry OK; lists not pinned reported; the freeze line; the harness re-made and at its sha256; PORT CHECK PASS; DRYLISTING-E195 PASS; no E195 datum in any ref; the preflight GO; the desk tests' logs; HEAD unchanged; then `onelab.sh undesk` |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged |
| 3, the post | (the card lane's) | waived by his standing words |
| 5, the sync | [`rb/s07_a3_sync_e195.sh`](rb/s07_a3_sync_e195.sh) | the box read first (no session or job of ours; E195's root made), the harness's files, committed and at their sha256, into E195's root; HARNESS OK on the box |
| 6, the build | [`rb/s08_a3_build_e195.sh`](rb/s08_a3_build_e195.sh) `start`, then `wait` | the detached job [`build_e195.sh`](build_e195.sh) (section 2); at most two starts a Pacific day; then the box's pins and tools read |
| 7, the reads | [`rb/s09_a3_reads_e195.sh`](rb/s09_a3_reads_e195.sh) | **THE REST RULE FIRST, read on the box, and no config read before the rest has run** (E192's data note 1); then k6's `s09_a3_reads_k6.sh`, unchanged |
| 8, the dry pass | [`rb/s10_a3_dry_e195.sh`](rb/s10_a3_dry_e195.sh) `start`, then `wait` | `session_e195.sh --dry` on the box: E195-DRY OK (288 device calls, the kit's committed listing) |
| 9, the session | [`rb/s11_a3_session_e195.sh`](rb/s11_a3_session_e195.sh) `FULL` | the window and the cap, k6's guard, today's dry pass and build, no stop file left in E195's root, no second E195 session that day after one that opened the card (one relaunch after a launch that opened no device), **THE REST RULE** ([`rb/rest_rule_e195.sh`](rb/rest_rule_e195.sh)); then `session_e195.sh` detached, DRY unset, with `X9_LATEST_START` the last start and `X9_DEADLINE` the earlier of the last end and the launch + 45 minutes |
| 10, the wait | [`rb/s20_wait_e195.sh`](rb/s20_wait_e195.sh), while it says 17 | the session found by its real script name (`session_e195(_v[0-9]+)?\.sh`); its end read from its own T0's log; GATE-STOPPED and MAIN-CRASHED read from its own lines (16); the manifest |
| 11, the collection | [`rb/s22_collect_e195.sh`](rb/s22_collect_e195.sh) (`onelab.sh collect` before) | E183 note 5's gate inputs first; one read-only copy back; [`collect_e195.py`](collect_e195.py): COPY EXACT, the data directory or **a gate stop's record under `docs/reports/gate-stops/`**, our login masked, the scrub, facts, SHA256SUMS; the desk-path gate twice; E178's scrub; no datum |
| 12, the commit | (the card lane's, through the lab's commit script; then `onelab.sh uncollect`) | `docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3/`, its README in [`DATA-README-FORM-e195.md`](DATA-README-FORM-e195.md)'s form |
| 13, the reduction, after the data commit | [`rb/s24_reduce_e195.sh`](rb/s24_reduce_e195.sh) | the main passes only (p910-p917 whose block.json reads ok), each pass's records checked against the session's manifest and its gen.sha256 against gen-e195-noms/; **the registered reducer, unchanged, `--warmup 910`, never `--forecast`**; then `check_e195.py leftover` |

The dry listing: [`rb/list_steps_e195.sh`](rb/list_steps_e195.sh). Its lines "run on the Intel" are k6's `rb_local` wording, unchanged: they
mean the desk (aifoundry2 when the card lane runs from there).

## 4. The readings stated here before any datum (where E195.md leaves a choice to the kit)

- **THE MEMORY SHIRES' COUNTERS: NOT READ; every x9_ item runs `--no-ms`** (E195.md 4 and 12: "if it cannot, every `x9_` item runs with
  `--no-ms` by a dated kit note before any datum"). What the source shows: the public firmware tree `et-platform` at its newest revision
  `836a4ab` (its master, read by `git ls-remote` on Sun 15 Nov 2026; no tags), which declares `device-minion-runtime` **0.25.0** (its CHANGELOG
  at 0.24.0 and Unreleased): the user-mode system call 10 is handled by the worker's `syscall_handler` (`WorkerMinion/src/syscall.c`,
  `SYSCALL_PMC_MS_SAMPLE` → `SYSCALL_PMC_MS_SAMPLE_INT`), then the machine minion's (`MachineMinion/src/syscall.c` line 133 →
  `sample_ms_pmcs(arg1, arg2)`), which stops the counter, samples it and starts it (`et-common-libs/src/etsoc/drivers/pmu/pmu.c` lines 64-81):
  two read-modify-writes of that memory shire's `DDRC_PERFMON_CTL_STATUS` that clear and set the counter's start bit (bits 0, 4, 17), every
  other bit written back as read, and one read of the counter; no counter register is written, and no reset bit (bits 1, 5, 18) is set by the
  call or held in the firmware's configured value `0xC80644` (`pmu.h`, `MachineMinion/src/main.c` line 87). The files on that path last
  changed in January 2024 and October 2025 (a licence header). **But the cards report minions 0.25.1** (E79's read of aifoundry3, 31 Oct
  2026; `docs/findings/14-card-behaviour.md`), a build not in the public history: the clear-free reading holds for the version-matched public
  source and is **NOT ESTABLISHED at the card's running build**, so by the registered rule every item runs `--no-ms`: the kit's manifest is
  `gen-e195-noms/` (make_x09.py `--no-ms`: the same 32 items, arguments and counts but ` --no-ms` on every x9_ item; counts.json byte for byte
  the registration's), the registered smoke gate does not ask for the counters (it reads configs.json), the reducer's C6 reads NO DATA, and
  every write price carries E195.md 4's label (a full-line store assumed to reach memory once, unread). A dated amendment before any datum
  may restore the default on the version-matched source's evidence (the owner's or the lab's call, as for E118's rule 8: "PASS for the
  version-matched source, UNKNOWN for the exact running build"); the kit does not run that variant as it stands.
- **THE RECORD-READING RULE** (E195.md 4; CONTEXT 116): the kit's runner reads the host's record from a source no runtime print can split
  (section 1: the one runtime line the lab has ever seen on a host's stdout is removed wherever it fell). The evidence beside it: the
  x09mem host prints nothing on stdout before it opens the device and each record with one `printf` and an `fflush` after its launch
  (`host/main.cpp` lines 506-523, 612-619); aifoundry3's runtime printed no line on stdout in E193's four committed device-stdout files and
  writes its device-layer block to stderr (E192's committed stderr: 706 blocks; the real-bytes test RB3, RB6); the aifoundry1 line appears
  only where ET_DEVICES is set (the session unsets it). THE REAL-BYTES TEST (section 6) feeds the runner the committed bytes.
- **The block's signal path and the sampler's stop** (E195.md 10): lib_e195.sh (section 1); nothing is ever killed.
- **The first card command** is the session's holder check (`et-who --check` with lib.sh's two ps rules), stamped as it starts; the cap of
  45 card-minutes counts from it.
- **Where the cap counts from: a dated reading (Q191, lane `fix-e195`, Sun 15 Nov 2026, before any E195 datum; verify-e195's finding 3).**
  E195.md 6 counts the rest from "E195's first card command of any kind" (step 7's config read counts), the cap of 45 card-minutes
  "from E195's first card command to its last", and sets the session's clock window as `X9_DEADLINE` = the earlier of the last end and
  "the session's launch plus 45 minutes". Read with request.md 10, which sizes the 45 as the session's own ("Smoke and the config reads
  about 2 minutes; 8 passes (1 warm-up and 7 headline) about 41 minutes: about 43 card-minutes (40-44), never more than 45"), **the cap
  counts from the session's first card command** (its holder check, `first-card-command.txt`), as the clock window does. Step 7's single
  config read (k6's step 7, the lab's own read before the session; step 8's dry pass of about 3 minutes lies between) is a card command
  for the rests (G3) and is **reported apart**: the data README gives its time and the minutes from it to the session's last card command
  (for a full session about 46-48). Counted from step 7's read instead, the session would keep about 41-42 of its 45 minutes, and the
  deadline rule (now + the longest pass + 60 s) could refuse a last pass that the 38-minute rule allows: a registered pass lost to a
  read the lab added. No number changes (the cap stays 45; the 38-minute and deadline rules as registered) and no code changes: step 9's
  `X9_DEADLINE` and the session's own deadline already count from the launch and from the first card command.
- **The deadline**: `X9_DEADLINE` from step 9 = the earlier of the window's last end and the launch + 45 minutes; the session takes the
  earlier of that and the first card command + 45 minutes. The registered rules then hold the session inside it (no pass after the 38th
  minute; none that would end after the deadline with the longest pass so far and 60 s for the close); a pass in flight is never cut, so a
  pass longer than every earlier one can carry the session past the cap: reported as a departure, never cut short (E195.md 6).
- **The start config gate**: `"tdp_w":0`, `"temp_threshold_c":65`, `"minion_mhz":600` in the start read (k6's strings), else GATE-STOP;
  the closing read is reported, never a gate, and is sent only while its own `et-who --check` reads the card free (the registered cfg();
  Q191). A tool's stderr is never copied into the session log: the line names its file and size (Q191, verify-e195's finding 4).
- **The smoke's gates**: the registered smoke_gate_x09.py, then the kit's peak gate (`check_e195.py smoke`): board_w below 65 W and
  temp_c.minshire[0] (the reading the runner's 70 C stop reads) below 65 C over every sample of the smoke pass, at least 100 samples.
- **The rest**: 40 minutes before E195's first card command of any kind, read on the box from every session-log form of ours there (E183's,
  E188's, E189's, E192's, E193's and E195's own among them), at step 7 (before its config read) and at step 9 (before the launch); the next
  session of ours there rests 40 minutes after E195's "session end".
- **One session a day**: a session that opened the card (its start config read, or any gate or pass after it) is that day's E195 session;
  a launch that opened no device may be launched once more from the same RB_OUT inside the same window (E192's G4, E191 note 2's relaunch
  rule), its first T0 kept in RB_OUT/e195-relaunch.txt.
- **A gate stop's record**: a session that ended at a gate before any pass is collected under `docs/reports/gate-stops/<day>-e195-x09-
  dramtoggle-T<T0>-aifoundry3/`, never under `docs/reports/data/`, never reduced (E193's fix).
- **Stop files left** in E195's root refuse the next session (the registered rule) until a dated note moves them aside.
- **The data directory**: the box's bytes (each pass's telemetry.jsonl.gz as the block wrote it), our own box login masked in every text
  file but the records the reducer reads; facts-e195.json holds what the README's results need.
- **Step 13 reduces the main passes only**: p910-p917 whose block.json reads ok, `--warmup 910`, never p901, never `--forecast`
  (E195.md 7); a pass that did not end ok is reported, not reduced.

## 5. THE REAL-PATH DESK TEST and the audit of every dry branch (the lessons of CONTEXT 104 and 109)

[`desk/desktest_realpath_e195.py`](desk/desktest_realpath_e195.py) runs **the session's real path, DRY unset**, exactly as step 9 launches it,
against [`fake_card_e195.py`](fake_card_e195.py)'s stand-ins (each named as the real tool in `ps`, so lib.sh's rules see them; the host
prints X09MEM lines with the real host's keys and reads the session's stop file before each launch; the sampler writes 10 Hz lines on the
live .raw from a small card model; the heater bumps the die so the runner's approach heats once and launches; et-who and the holder helper
in et-holders' form) and loggers in front of `timeout` and `flock`; each case in its own sandbox and its own stand-in box, the session's first
process a wrapper that lets the case's stand-ins end by themselves before the PID namespace goes (so a stuck stand-in sampler ends by itself,
as the real one would at its bound). Every case asserts its exit, its gate line or none, the session's own lines, the stand-ins' calls, the
manifest verifying, nothing left running, and **nothing killed** (every device stand-in that started logged its own end). Its cases are in
its header and its log.

**The audit** ([`desk/dry-branches-e195.tsv`](desk/dry-branches-e195.tsv), made from the files' own lines by
[`desk/drybranches_e195.py`](desk/drybranches_e195.py)): every line of session_e195.sh that reads `DRYF`, of block_e195.sh, lib_e195.sh,
lib.sh and lib_x09.sh that reads `V3_DRY`, and of runitems_e195.py that reads `a.dry` (27 lines), what the dry path does there, what the
real path does, and the cases that ran the real branch; the test fails if a line has no row, a row's text differs, or a named case failed.
**The runbook's audit** (Q191, verify-e195's nit 7): [`rb/dry-branches-rb-e195.tsv`](rb/dry-branches-rb-e195.tsv), made from the files'
own lines by [`rb/drybranches_rb_e195.py`](rb/drybranches_rb_e195.py): the 60 lines of rb_e195.sh, the ten steps and k6's rb_common.sh
that read `RB_DRY`, each with its function, what the dry listing does, what the real path does, and the runbook desk test's cases that
ran it; the desk test's last case, AUDIT-RB, checks the table against the files with that run's own results, and one branch no E195
step reaches is named so (k6's rb_nopath: step 11 uses E183's desk-path gate). rb/list_steps_e195.sh is the dry listing itself.
Reachable only by reading, not at the desk: the 38-minute rule (it needs 38 minutes of session; one integer compare, session_x09.sh's own);
lib.sh's `start_sampler` retries (a sampler that fails to start six times; never on the stand-ins); the runner's three-unreached stop.

## 6. THE REAL-BYTES TEST ([`desk/realbytes_e195.py`](desk/realbytes_e195.py))

The kit's one host-output parser is its runner. The test runs it, unchanged, on replays of committed card bytes (a replay tool prints a
committed stdout file byte for byte as the host), and the registered runitems.py beside it as the negative control: RB1 aifoundry1's split
line (1a4bc1e3) read whole by the kit's runner and failed by runitems.py (the day's defect reproduced); RB2 all 31 host lines of E191's
second session (26 with the runtime line inside the JSON); RB3 aifoundry3's four E193 device-stdout files read identically by both; RB4 the
runtime line at every byte offset of a real aifoundry3 line, two at once, at the line's start; RB5 an unknown text inside a line still
failing the parse (never a wrong datum); RB6 aifoundry3's runtime on stderr; RB7 the census of the runtime line in the lab's raw records
(every occurrence of the one form the kit drops). E192's data directory holds no raw host stdout (its runner kept the parsed records and
the raw stderr), so E192's real bytes enter as its committed stderr (RB6); E193's four device-stdout files are the raw aifoundry3 host
stdout the lab has committed (RB3, RB4).

## 7. Device commands

`dmcmd_audit.py` on the session's file set (`preflight_e195.sh`: the session, its blocks and library, its runner, the checker, the harness,
the build; the registered lib_x09.sh, watch_x09.py, smoke_gate_x09.py, make_x09.py, the host's main.cpp, x09mem_args.h and the kernel's
x09mem.c; the lab's lib.sh, text_hash.sh and E128's guard): **GO, 44 send sites, 0 disallowed, no allow-list**. **Every send site is a READ**: the samplers' `ettelem sample`
(GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES) at lib_e195.sh's
start_sampler and die_c and lib.sh's die_c, clock_mhz and start_sampler, and E128's guard line 31; the config read's `ettelem config`
(GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) at the
guard's line 18 (the session's three config-read lines go through it); lib.sh's drain (GET_MODULE_POWER through dev_mngt_service, lines 139
and 143), a READ that lib_x09.sh refuses at run time; and **one reviewed exception, the lab's own for E180, E183 and the registered
preflight_x09.sh**: lib.sh line 154's forwarded `"$@"` could carry a statistics reset (STATS_RESET); E195's sampler is lib_e195.sh's
`start_sampler`, which forwards nothing, and lib.sh's is overridden and never called. The host opens the ops node only
(`createPcieDeviceLayer(true, false)`; the runtime's loads, copies, allocations and launches); the kernel's system call 10 is not made
(`--no-ms`, section 4); `et-who --check`, et-holders and `flock` send no device command. No set, no reset, no statistics reset, no PMIC write,
no firmware query.

## 8. The predicted peak against aifoundry3's stops, and how the kit keeps E195 under them

The memory arms drive DRAM from all 1,024 minions; the writes (flat tensor stores) are new on this meter. E195.md 10's table, registered:
the 31 arms 2-11 W over rest, about 37 W at most, and the approach's heater bursts about 54 W (quoted from the proposal); this card's record
with the same runner and heater, E132 (heater bursts 53.60 W, its DRAM items at most 35.06 W, die mean 61 C at most) and E139 (53.52 W)
(measured, public); the approach's set points (heat to 59 C, launch at 58 C); the smoke's gate below 65 W and below 65 C; the live stops 70 W
on three samples in a row and 70 C. The record's highest readings sit 16.4 W and 9 C under the stops. **How the kit keeps E195 under them:**
nothing in the kit can raise the clock or the power limit (no set of any kind; the start config gate refuses any session not at TDP 0 W,
65 C, 600 MHz as found); the workload is the registered one (1,024 harts in memory-bound or clock-paced loops, the heater only between runs);
the smoke holds the first flat write (x9_wr_u4) and the heater, and **the kit's gate refuses every pass unless the smoke's highest board
reading is below 65 W and its highest die reading below 65 C**; the watcher reads each pass's live telemetry and stops at 70 W on three
samples (the real-path case B1: the stop on a live .raw, the pass ended at its next item); the runner's die stop at 70 C before every device
process and all through every approach (D1); a stale sampler stops the pass (T1); the session's stop file reaches every launch within 0.4 s
(NR); the cap and the deadline bound the time at load. aifoundry3 makes no thermal step at its zero TDP, so the session's own die stop is the
brake: it is never disabled and no stop is relaxed. A launch that does not finish needs a card reset, which is never this run's to make.

## 9. What the checker reads after the reduction ([`check_e195.py`](check_e195.py) `leftover`)

E195.md 7's property of the registered code, made visible: for each headline pass and direction, every term the reducer takes as zero (the
floor's one, high pin and toggle prices; the random closure's toggle price), each named with the arms whose kept runs it lacked (the
reducer's own `runs_of_pass`, `session`, `CONTRASTS` and `RATE_OF` imported from the registered file by path, never copied); the rails'
measured volts (the mean of `sp.<rail>_mv[0]` over each pass's telemetry) beside the reducer's fixed 0.522, 0.698 and 0.484 V; and the
session's peaks against the live stops. It changes no number; the data README names the passes with a zero-filled term beside the floor and
"any line".

## 10. reg-e195's findings, answered

| reg-e195 | what | here |
|---|---|---|
| minor 1 | the floor's missing terms read as zero | `check_e195.py leftover` lists them by pass (section 9); the README names them |
| minor 2 | the smoke counted as a headline pass if given | step 13 gives the reducer p910-p917 with block.json ok only, `--warmup 910` |
| minor 3 | the paced store and no-store loops 16 bytes apart mod 32 | step 6 reads the heads of aifoundry3's build (`loops_e195.py` in build_e195.sh, kept in the record); C2 reads it in the data |
| minor 4 | a runtime line inside the X09MEM JSON would end the pass | the kit's runner reads the record whole; the real-bytes test (sections 1, 4, 6) |
| minor 5 | lib.sh's SIGKILL of a sampler; the lock freed while a device process runs | lib_e195.sh (section 1): no SIGKILL; the signal path writes the stop files first and keeps the lock until no device process of ours runs |
| nit 6 | the rails' electrons at fixed volts | the leftover checker reports the measured volts beside |
| nit 7 | R8b forced UNRESOLVED below 5 passes | registered; read with the data |
| open: syscall 10 | whether it clears the counters | NOT ESTABLISHED at the running build: `--no-ms` (section 4) |
| open: the session's real path | holder parsing, lock, sampler, approach, watcher on a live .raw, config reads | THE REAL-PATH DESK TEST (section 5) |

## 11. What the desk cannot show (for the verifier and the readiness critic)

1. **The host on the card**: the desk ran the real host only to its listing and its image dumps (no device); its launches, its X09MEM lines
   and its timing meet the card first in the smoke.
2. **The box's build**: step 6 there, against aifoundry3's own /opt/et; its ELF may differ from the desk's (reported, never judged).
3. **The box's sampler, heater, holder check and et-holders**: the real tools meet the session first on the day (step 7 reads the config
   through the same guard before; E132 and E139 ran this runner and heater on this card).
4. **Another user's device process**: lib.sh's and lib_x09.sh's ps rules for other users cannot be made at the desk (no other user's
   process can be started); the holder lines of another user are made by the stand-in et-holders (H1-H4).
5. **The real card's power, die and rates**: every watt and degree at the desk is a stand-in's arbitrary test value.
6. **The 38-minute rule, lib.sh's start_sampler retries and the runner's three-unreached stop** (section 5) were read, not run.
7. **A stuck sampler on the card** ends at its own bound (about 46 minutes for a pass); the next session of ours on aifoundry3 waits for it.
8. Card time waits on the owner's go (CARD-LANE-BRIEF.md section 1).

## 12. Files

| file | what |
|---|---|
| `session_e195.sh` | the session (section 1) |
| `block_e195.sh`, `lib_e195.sh`, `runitems_e195.py` | the ports and the kit's library changes (section 1); `desk/port_e195.py` makes and checks the ports |
| `check_e195.py` | the smoke's peak gate, the dry listing check, the leftover checker, the peaks |
| `harness_e195.py`, `harness-e195.json` | every file the box runs or reads, at its sha256 (the sync list) |
| `build_e195.sh` | the box build, its checks and the box's tools |
| `preflight_e195.sh` | dmcmd_audit on the session's files |
| `gen-e195-noms/` | the generator's output the session runs (`--no-ms`) |
| `collect_e195.py` | COPY-BACK EXACT, the data directory or a gate stop's record, the scrub, facts, SHA256SUMS |
| `fake_card_e195.py` | the stand-ins for the desk tests (never on the box) |
| `desk/desktest_realpath_e195.py`, `desk/dry-branches-e195.tsv`, `desk/drybranches_e195.py` | the real-path desk test and its audit |
| `rb/drybranches_rb_e195.py`, `rb/dry-branches-rb-e195.tsv` | the runbook's dry-branch audit (Q191; checked by the runbook desk test) |
| `desk/realbytes_e195.py` | the real-bytes test |
| `desk/drylisting_e195.py`, `desk/dry-e195-noms-aifoundry3.txt` | the dry listing the dry pass is checked against |
| `desk/checks_e195.sh`, `desk/port_e195.py` | the quick set; the ports |
| `rb/` | the runbook's steps, the rest rule, the history check, the dry listing, the runbook's and the rest rule's desk tests |
| `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e195.md` | the card lane's brief; the data README's form |
| `logs/` | every check above |
| `SHA256SUMS-e195-kit` | the kit's files (step 2 aside), its logs, and the unchanged files it calls |

**Step 2 (`rb/s03_desk_e195.sh`) is outside `SHA256SUMS-e195-kit`** (a file cannot hold the sha256 of a list that holds its own): its own
sha256 and the list's are given in the land file's anchor lines.

## 13. Labels, and compute

Every figure quoted from E195.md (the arms, the cap, the stops, the rests, the pins) is **registered**; the proposal's sizing and power
figures are **quoted from the proposal**; E132's and E139's peaks are **measured, public**. The desk tests' results are **desk checks of
code**, not measurements; every watt and degree in them is a stand-in's arbitrary test value, not a forecast and not a measurement. Nothing
here is blind, held out or post hoc; no E195 datum exists. Compute: on aifoundry2 through the round's CPU slot at nice 10, each test that ran
a built host, the session, the runner or a stand-in inside the no-device sandbox; builds `-j4` (seconds); the real-path desk test in 14 minutes of wall time (17:04-17:18 PST; its P case at the hosts' real timing, 603 s; F 669 s; the rest in batches beside them, each in its own sandbox); the runbook test in 12 minutes (17:06-17:18 PST: the box's real build, the box's dry pass, a stand-in session of two passes at the host's real launch timing); in Q191 (fix-e195) the real-path desk test again at 22:28-22:39 PST and the runbook test at 22:40-22:52 PST, each after a wait for one of the round's three shared CPU slots; the real-bytes test, the quick set, the rest-rule test and the dry listing in seconds to a minute each; the development runs before them (section 14) the same way; no simulator, no other
box, no card.

## 14. What the development runs found, before the logged runs (desk checks of code; each fixed in a kit file)

| run | found | fixed in |
|---|---|---|
| real-path development runs | **a defect the registered block carries: its signal path SIGTERMs the runner while a device process runs, and that host (its stdout the runner's pipe) dies at its next record by SIGPIPE** instead of "running on" as E195.md 10 expected (the BS case: the host's start logged, no end logged, no signal received) | `lib_e195.sh`'s `x9k_on_signal` (the stop files first; the runner ends by itself); `block_e195.sh` replacement 8 |
| real-path development runs | the session's manifest listed its own temporary file (`MANIFEST.sha256.tmp`) | `session_e195.sh`: `! -name 'MANIFEST.sha256*'` |
| real-path development runs | faults of the test's own: cases shared one stand-in box, so one case's stop file (in E195's root) reached the others; the signal case matched bubblewrap's command line, not the session's; the PID namespace's teardown ended a stuck stand-in before it could end by itself; the "nothing killed" check could not see a SIGKILL (now every stand-in logs its own end) | `desk/desktest_realpath_e195.py`, `fake_card_e195.py` |
| runbook development run | **the history check passed an empty pathspec to git (the tree's top), which git refuses, so it saw no added or untracked shadow at all** (H2, H3) | `rb/check_history_e195.py`: the top as "." |
| real-bytes development run | faults of the test's own: the self-test's stdout (no record) counted as a host line; a dry stub's text in a tool's source counted in the census of raw records | `desk/realbytes_e195.py` |
| quick-set development run | the preflight's verdict line read from the wrong stream | `desk/checks_e195.sh` |
| the public-text scan, after the first logged runs | a setup line in the brief named the round's private paths; a stand-in message and a comment carried scanned words | `CARD-LANE-BRIEF.md`, `fake_card_e195.py`, `rb/selftest_rb_e195.sh`; the real-path, runbook and rest-rule tests then ran again for the logs here, on the final bytes |

## 15. verify-e195's findings, answered (Q191, lane `fix-e195`, Sun 15 Nov 2026, before any E195 datum and before the land)

| verify-e195 | what | answered here |
|---|---|---|
| medium 1 | the closing config read was sent without `et-who --check` (the registered cfg() reads only while the card reads free; H2, H3 and the verifier's VH0 sent it 8-16 s after another user's holder appeared) | `session_e195.sh` `closing()`: `timeout 20 et-who --check` first (its lines in etwho-check-end.txt); any exit but 0: "closing config read: not read (et-who --check does not read the card free: exit N, k holder line(s) in etwho-check-end.txt)" and no read; the dry line names the check. The real-path test: H2, H3 and a new H4 (the verifier's VH0, a holder in the smoke) each assert one config read only (the start's), two `et-who --check` calls, the "not read" line and no config-session-end.json; P asserts both reads follow an `et-who --check` that read free; the audit row re-made (P, K1, L2, H2, H3, H4); harness-e195.json re-made |
| minor 2 | the brief's stop paths missed the one-lab calls | CARD-LANE-BRIEF.md row E: `onelab.sh undesk` and `uncollect` on every path (each removes only this lane's own flag and is harmless with none), then `hold.sh remove` and `book.sh release`; steps 0, H, 1, 2, 11 and 12 send every failure to E; section 3 says so |
| minor 3 | the cap's start against E195.md 6's letter | section 4's dated reading (the session's first card command, as E195.md 6's clock window and request.md 10 count it; step 7's read reported apart); the brief's G2; the data README form's results and cap rows. No number and no code changed |
| minor 4 | the rest rule read "no device opened" anywhere in a line, and the session copied tool stderr into its log | `rb/rest_rule_e195.sh`: a block opened no device only by E195's own two forms at a line's start ("refused, no device opened: ", "GATE-STOP: ... (no device opened)"); `session_e195.sh` names a stderr file and its size instead of copying its text (`errsz`); the rest test's R17 (the verifier's case I, now counted) and R18 (E183's ending form, now counted: the safe direction, it only delays a launch); the old rule fails both (logged as a negative control in the lane's folder); the quick set's Q8 reads the two changed lines. A later kit whose rest rule reads E195's logs should take the same line |
| nit 5 | the committed dry listing showed a placeholder count | `logs/dry-listing-e195.txt` re-made after the kit list's count was final |
| nit 6 | the dry listing's sample day was fixed at 2026-11-15 | `rb/list_steps_e195.sh`: the day defaults to today (Pacific); step 1 and the day rules read the real day either way |
| nit 7 | the runbook's RB_DRY lines had no line-by-line audit | `rb/dry-branches-rb-e195.tsv` and `rb/drybranches_rb_e195.py` (section 5); the runbook desk test's case AUDIT-RB; the quick set's Q11 |
| open | the registration's build re-run (the verifier's s15) was not run | the quick set's Q7 built the registered source here again (cmake with /opt/et, check_elf.py, the arm table and the generator byte for byte) |

SPDX-License-Identifier: Apache-2.0
