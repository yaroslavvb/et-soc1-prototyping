# E202's run kit: one pass over MNIST in int8 on aifoundry3 card 0, run from aifoundry2 in E189's runner form (one sampler, the stop lines live, the stop-path test, the smoke's five processes and its gate, the R rule per arm, the bursts T Z Z T T Z Z T), the program built on the box and read by its .text and its host's behaviour, the MNIST files fetched there by sha256, every host's result read from its own file, the runbook from the window to the scorer after the data commit, and the real-path, real-bytes, build, runbook and rest-rule desk tests run for real (Q193; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q193, lane `kit-e202`). No card was claimed or opened: aifoundry2 has a card,
so every desk test that runs a built host, the runner or a stand-in session ran in the round's CPU slot inside the no-device sandbox
(`W/nodev.sh`: no /dev/et*, an empty /run/lock), the real-path test each case inside a sandbox of its own within it, and only while THE
QUIET DESK FLAG was absent. No device command was sent, nothing was posted, no simulator ran. One box was reached once, read-only:
aifoundry3, Mon 16 Nov 03:18:07 PST, while no lane booked it (its python3 3.12.3 with numpy 1.26.4, gzip, curl, flock, rsync, cmake 3.28.3,
/opt/et's objcopy, and both MNIST mirrors answering: the facts the kit's step 6 rests on); nothing was written there. New files only, all
under `tools/claims-v3/e202/`, on the registration's local commit (reg-e202's patch applied after fix-mnist's at GitHub main `250f825b`:
E202.md and its 12 files as committed, the registration's subtree `d95a19d9...`, its list `3ff8830f...`; the program's subtree
`fb102551...`), every file of which stays as committed. This is the kit E202.md section 8 and the reg-e202 lane's open items ask for. **No
E202 datum exists. Nothing here changes a forecast, a band, a rule, a threshold, K, the order, the R rule, the card time, the cap, a stop
or the scorer.** Where E202.md leaves a reading to the kit, the reading is stated in section 4 before any datum.*

*Fixed before the land, Mon 16 Nov 2026 07:11-09:48 and 09:53-10:45 PST (Q193, resumed in Q198; lane `fix-e202`, answering verify-e202's HOLDS WITH FIXES; section 12):
an et-who that cannot be read is a holder (finding 1); a crash of the runner is named and step 10 reads the runner's exit (2); ledger v3
landed after the registration's freeze, so E202's v3 note is written here before any datum and step 2 requires it (3); etcfg's place in
E202.md 8.1 is read here (4); K1 also on a host that died or left no record (5); the rest rule's activity floor and the readiness reads of
E201's and E204's logs (6); the host's own launch timeout caps the R rule's R, stricter only (7); the closing config read is not sent
while our own sampler has not stopped (8); the README form's latency row and crash line (10); step 9 refuses on a HUNG marker, and the go's
reading of "after E201" (11). The registration's files are unchanged (its subtree `d95a19d9...`, list `3ff8830f...`): E202.md's line 11
(verify-e202's nit 9) stays as registered. No forecast, band, scored rule, threshold, K, order, cap or stop of the registration changed;
the R rule's cap (item 23) can only pick a smaller R than the registered rule's, and changes nothing at the forecast.*

## Results first (desk checks of code; nothing is measured)

Python everywhere at the desk: `/usr/bin/python3` 3.12.3 (numpy 1.26.4 for the reducer and the files' numpy model); this desk's /opt/et:
cmake 3.28.3, riscv64-unknown-elf-gcc 15.1.0, g++ 13.3.0 for the real builds.

| check | result | log |
|---|---|---|
| **THE REAL-PATH DESK TEST** (`desk/desktest_realpath_e202.sh`, `desk/realpath_e202.py`): `session_e202.sh`'s real path, DRY unset, exactly as step 9 launches it, in a sandbox named aifoundry3 with two regular files at /dev/et0_ops and /dev/et0_mgmt, against stand-ins at the tools' real paths (the sampler and config behind the box copy of E128's guard, the mnistmlp host, et-who), the host printing a runtime line INSIDE its stdout JSON on every process and the sampler inside every 25th line; the whole session (the smoke, the gate, the R rule, 12 bursts in the registered order, both anchors, the closing), then the collection, the unchanged reducer, the frozen scorer and the rest rule on its files; the refusals, the gates, the stops, the fallback, K1, the operator's stops; the audit of every dry branch | **fix-e202, on the fixed bytes: DESKTEST-REALPATH-E202 41 of 41 PASS** (10:07 PST start; the cases below and fix-e202's W1, W2, K1b, CR). kit-e202's run before the fix: DESKTEST-REALPATH-E202 37 of 37 PASS (run 4, Mon 16 Nov 05:30-05:52 PST, on the kit's final bytes): P 18 of 18 (17 host processes, every stdout split by a runtime line, every result read whole from its own file; the 12 bursts reduced by the unchanged reducer at -3.7% to +2.2% of the energy the stand-in card injected, inside 3% + 0.33 W/C x (t + 7 s) / J; the scorer's words), R1-R9, G1-G3, S1, FB, K1, SG, T, SIG, Z and the AUDIT (18 dry branches). Runs 1-3 (development, same day) found three defects of the TEST, each fixed before run 4: R2's nested sandbox left a /dev/et1_ops in the outer /dev; R7's `flock` child kept card 0's lock; T's expectation (a STOP file in a burst's rest before starts no host process, as the runner rightly did) | [`logs/desktest-realpath-e202.txt`](logs/desktest-realpath-e202.txt) |
| **THE REAL-BYTES TEST** (`desk/realbytes_e202.py`): every reader of a tool's output fed the lab's committed bytes (the mnistmlp host's nine real --out files; 1a4bc1e3's split stdout; the splice at every byte offset; E189's and E195's sampler lines; E195's raw config line; et-who's real text; other hosts' records) | **fix-e202, on the fixed bytes: REALBYTES-E202 13 of 13 PASS** (B1 also reads the R rule's detail; B6 the unreadable rule). kit-e202's run: 9 of 9 real records read exactly; 14,348 splices at every offset, 0 wrong; with no newline, 0 that pass the gate with a field changed; 16,411 of 16,411 real sampler lines; the split stdout never read (no --out file: no result); other hosts' records refused | [`logs/realbytes-e202.txt`](logs/realbytes-e202.txt) |
| **the runner on its doubles** (`selftest_run_e202.py`, the dry path step 8 runs): every gate, stop and branch the doubles drive, and END TO END on energy_stub.py's alt card with the registered rests through the collection, the reducer and the frozen scorer | **fix-e202, on the fixed bytes: SELFTEST-RUN-E202 51 of 51 PASS** (fix-e202's W1-W4, X1-X3, K1b, K1c, CL, R3 and the E2E v3 readings beside the cases below). kit-e202's run: 39 of 39 (05:01-05:09 PST): the order, the smoke, the gates (lock, holder, config, a cut config line, a dead sampler), the stops (66 W, 70 C in the smoke, the clock outside and inside a burst, the stale line both ways, split sampler lines), a holder before burst 3 and the closing NOT read, the fallback, no pair, a logits-only failure, an arm's end, K1, the R rule per arm (R 80; no R), the cap, the end bound, the die gate, the window, the refusals; END TO END: 4 bursts reduced at -3.5% to +2.3% of the injected energy (TOL about 10%), the frozen scorer's five words, the facts; a gate stop refused under docs/reports/data/ | [`logs/selftest-run-e202.txt`](logs/selftest-run-e202.txt) |
| **the build on this desk's real toolchain** (`desk/desktest_build_e202.sh`): build_e202.sh as it is in a stand-in box tree, the MNIST files FETCHED from the mirrors into an empty folder and checked by sha256, the weights and expected outputs made and pinned, the host read by its behaviour; four negative controls | **fix-e202, on the fixed bytes: DESKTEST-BUILD-E202 10 of 10 PASS** (10:07 PST, the MNIST files fetched again into an empty folder; build_e202.sh, files_e202.sh and hostcheck_e202.py unchanged). kit-e202's run (04:49 PST): E202-BUILT in 44 s; the .text `ace7bcb0...` (the ELF `5bab5365...`, aifoundry2's, as E202.md records); MNIST fetched into an empty folder, 18 of 18 at their pins; HOST-BEHAVIOUR OK 20 of 20; B2 a changed source refused at the harness; B3 a changed kernel refused at the .text gate; B4 a second start with the files kept; B5 a wrong pin refused | [`logs/desktest-build-e202.txt`](logs/desktest-build-e202.txt) |
| **the runbook** (`rb/selftest_rb_e202.sh`: a stand-in ssh and rsync, a stand-in box, the box's build REAL) | **fix-e202, on the fixed bytes: SELFTEST-RB-E202 23 of 23 PASS** (fix-e202's V3, HG, WT4, WT5, and P1 reading the v3 note, beside the cases below). kit-e202's run: 20 of 20 (05:28-05:29 PST): the dry listing; the window rule; the nested lab-git lock; step 2 at every pin and its refusals; four shadow cases; an E202 datum in another ref; the REAL build on the stand-in box; X, T; the login link, the hang, the cut wait; step 7 refused before the rest and run after it; the dry pass; the rest and same-day rules through step 9; the real session launched and read as a gate stop; the wait's pattern against the real name and a decoy; the gate stop's record; a changed byte; the scorer before the data commit. Its first try read 10 of 20: the stand-in box's guard counted another lane's `session_e204.sh` desk processes; its pgrep now counts the stand-in box's own processes only | [`logs/selftest-rb-e202.txt`](logs/selftest-rb-e202.txt) |
| **the rest rule** (`rb/selftest_rest_e202.sh`): E195's, E193's, E189's committed session logs (real bytes), E183's form, E202's own forms (the real-path test's session log, a dry pass, a refusal), a cut session, a no-device phrase inside a line (verify-e195's finding 4), energy.sh's folders | **fix-e202, on the fixed bytes: SELFTEST-REST-E202 19 of 19 PASS** (fix-e202's activity floor: R14-R18, R20) | [`logs/selftest-rest-e202.txt`](logs/selftest-rest-e202.txt) |
| the dry listing, every step with stand-ins | **fix-e202: dry listing: 13 steps listed, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e202.txt`](logs/dry-listing-e202.txt) |
| `dmcmd_audit_v2` on the session's files (`preflight_e202.sh`) | **fix-e202: GO (22 send site(s), 0 disallowed; allow-list: none)**: every send site a READ, no allow-list and no exception (22 before the fix: no send site added) | [`logs/dmcmd-audit-e202.txt`](logs/dmcmd-audit-e202.txt) |
| the kit's checks (`desk/checks_e202.sh`): the common self-check, the harness, the registration's list, forecast, plan and scorer self-test (its stub unchanged after), the preflight, the history check's names, every file's syntax | **fix-e202: CHECKS-E202 14 of 14 PASS** (the ledger v3 note re-made among them) | [`logs/checks-e202.txt`](logs/checks-e202.txt) |

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** E202.md (the registration, d95a19d9...) and the program (workloads/mnistmlp, fb102551...: its README, host and model);
   E189's kit (`tools/claims-v3/e189/`: the runner's form, its doubles, its collection, its runbook) and how its card day went (card-e189,
   Sat 14 Nov 2026: RAN FULL, the steps and their exits; its committed data fa9098c4); E190's kit (`tools/claims-v3/e190/`: one large
   tensor kernel per process, the build read by its kernel's bytes and its host's behaviour); E191's kit note 2 (`2d0fe517`: a host's
   result from a source no runtime print can split, tested on real bytes); E192's data note 1 (`4e964246`: step 7's configuration read
   only once the rest has opened); E195's kit and verify-e195 (its rest rule's own no-device forms; the closing config read only while
   et-who reads the card free; the brief's undesk and uncollect on every stop path; the cap's start); E196's kit (the real-path test's
   sandbox, the audit of dry branches, the gate stop's record, the same-day rule); k6 (`tools/claims-v3/q141k-runbook/k6/`);
   `tools/claims-v3/dmcmd_audit_v2.py` with `dmcmd_table_v2.json` (Q188's guards, landed); the round log's sections 110, 113-124.
2. **Used, unchanged** (called, sourced, imported or run by path; sha256 in [`SHA256SUMS-e202-kit`](SHA256SUMS-e202-kit) or the lists step
   2 pins): the registration's `plan_e202.py` (its `r_rule`, imported), `plan-e202.json`, `forecast-e202.json` (the doubles' seconds and
   watts only), `score_e202.py`, `weights/mnist-int8-trained.mlpw.gz`; the program's build inputs and its model (`fetch_mnist.sh`,
   `mnist_model.py`, `MNIST-SHA256SUMS`, `PINS-SHA256SUMS`); **k6's runbook drivers** (`rb_common.sh`, its look `s05_look_k6.sh` and reads
   `s09_a3_reads_k6.sh`; v3.1's `rb_run.py` and `nopath_q142s.py`); **E128's guard** (`e128/ettelem_guard.sh`); **E195's rest rule's code**,
   line for line; **energy.sh's reducer and stub** (`workloads/sparseparity/tools/energy_reduce.py`, `energy_stub.py`).
3. **Not used:** any card but aifoundry3 card 0; a simulator; the owner's private checkpoint (never read by this lane) and his A100 report;
   any private page; the UA = 0 fallback (not built; E202.md 8.2); coop4 (not built; E202.md 8.5).
4. **Tiers:** every file here is public tier and cites public pieces only.
5. **Readiness:** this kit gates nothing by itself: a verifier, a fix pass and a readiness check come next, then the session.

## 1. The kit, in E189's form

- **The runner** ([`run_e202.py`](run_e202.py), [`e202_common.py`](e202_common.py), [`session_e202.sh`](session_e202.sh)): E202's whole
  session on aifoundry3 card 0, one Python process, E189's form. Before anything, its refusals ("refused, no device opened: ...", rc 2): the
  host's name aifoundry3; exactly `/dev/et0_mgmt` and `/dev/et0_ops`; no desk-test variable; the synced files at harness-e202.json's sha256;
  the preflight GO; today's build record with the kernel's `.text` at E202.md's pin and the host and ELF at the record's sha256; every one of
  the 18 inputs at its pin. Then card 0's lock (`flock -n`, held to the end), et-who and ps (another login's holder or another user's
  device process: refused), **THE FIRST CARD COMMAND** (the start `ettelem config` through E128's guard, stamped as it starts: TDP 0 W, 65 C,
  600 MHz as found, else GATE-STOP; the cap counts from it), **ONE sampler** (10 Hz, through the guard) whose every line goes to THE STOP
  LINES as it arrives, with a watchdog for the stale line, **the stop-path test** (four lines), **anchor 1** (2 minutes), **THE SMOKE**
  (T-scp, Z-scp, T-dram, Z-dram with `--debug-logits`, and ACC on the test split with `--true-labels`; each its own arm; each die-gated and
  et-who-checked; its result from its own `--out` file; its labels kept), **THE GATE** (scp when T-scp and Z-scp read core PASS, else dram
  when T-dram and Z-dram do, else GATE-STOP), **THE R RULE** per arm (plan_e202.r_rule on the arm's own smoke, unchanged), **THE BURSTS**
  (the scored pair T Z Z T T Z Z T, then the dram pair T Z Z T REPORTED when scp is scored; each the die gate, et-who, 8 s at rest, ONE host
  process of R passes under `timeout 10`, 10 s at rest whatever a stop says), **anchor 2** if it ends inside the cap, then **THE CLOSING**
  (the sampler by SIGTERM, et-who, the closing config read ONLY while et-who reads the card free), "session end", the lock released,
  MANIFEST.sha256 last. Exit: 0 the queue ran, 2 refused, 3 GATE-STOP.
- **The box build** ([`build_e202.sh`](build_e202.sh), [`files_e202.sh`](files_e202.sh), [`hostcheck_e202.py`](hostcheck_e202.py)): the
  program into `build/e202mnist` (a new folder of E202's), the kernel by its `.text` (`ace7bcb0...`; the ELF reported beside E202.md's
  aifoundry3 build `0f74ff0d...`, never judged), THE FILES into `build/e202files` (the four MNIST files FETCHED on the box by the program's
  recipe, each accepted only by its sha256; the trained weights decompressed from the registration's `.gz` and checked by their pin; the
  random weights and the eight expected-output files regenerated there by the program's numpy model and checked by their pins: 18 of 18),
  THE HOST BY ITS BEHAVIOUR (20 cases: its CPU self-test; six refusals at parse, each also carrying a missing pins file so that even a host
  whose tested refusal failed would stop before the device; seven `--dry` plans of every registered launch; four `--ref` runs of the host's
  own reference against the expected files; the negative control; a wrong pin), and the record `build/e202mnist/BUILD-E202.json`.
- **The doubles** ([`fake_card_e202.py`](fake_card_e202.py)): config, et-who, a toy card's sampler (or energy_stub.py's under the same
  injections), and the mnistmlp host (its parser, its record's fields and form, one launch announced at its start). **The stand-ins**
  ([`desk/standin_e202.py`](desk/standin_e202.py)) put the same behaviour at the real tools' paths, their knobs from a case file.
- **The collection** ([`collect_e202.py`](collect_e202.py)): COPY-BACK EXACT; the data directory in E202.md 7.1's form (`smoke/<arm>/`,
  `bursts/<config>/b<k>/`, `session/`) or, when no burst ran, a gate stop's record under `docs/reports/gate-stops/`; each burst reduced by
  `energy_reduce.py`, unchanged; the scrub (the box's home and our box login); `session-facts-e202.json`; SHA256SUMS. **The harness**
  ([`check_e202.py`](check_e202.py), `harness-e202.json`: 30 files) and **the preflight** ([`preflight_e202.sh`](preflight_e202.sh)).
- **The runbook** ([`rb/`](rb/)) from aifoundry2 through k6's drivers, unchanged, in E189's step form with E195's and E196's later rules
  (section 3). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lane's brief; [`DATA-README-FORM-e202.md`](DATA-README-FORM-e202.md)
  the data README's form, with the meter's absolute-scale caveat.

## 2. Card-minutes and the cap (registered; unchanged)

About 17 card-minutes at the point, about 29 at the slow end with every die-gate wait (plan-e202.json), **cap 35**: no burst starts after
33 card-minutes from the first card command, and the session's last card command comes by 35 (section 4, items 1-2).

## 3. The order on aifoundry3, and the box steps

E202 runs alone on aifoundry3 card 0, after E201 when E201 runs (E201 and E204 were paused on Mon 16 Nov 2026 by the owner's
matmul focus: item 25), after the 40-minute rest that follows our last session there, and never while another session of ours runs
on the box. Run from the
lab clone, each step with this day's `RB_OUT` (outside the repo), the one `RB_LOCK` and, for step 2, `RB_GITLOCK`.

| box step | file | what |
|---|---|---|
| B, 0, H | (by hand) | the booking (G); `W/onelab.sh desk <lane>` (THE ONE-LAB RULE); `uptime` (THE LOAD RULE); GitHub main; the anchor lines; THE QUIET HOLD |
| 1 | [`rb/s02_window_e202.sh`](rb/s02_window_e202.sh) `<day> <last start> <last end>` | today only; the cap's 2,100 s before the last end |
| 2 | [`rb/s03_desk_e202.sh`](rb/s03_desk_e202.sh) (outside the kit's list), then `W/onelab.sh undesk <lane>` | the window; the pull under the lab-git lock (never nested: 16); the program and the registration by their content and ancestors of HEAD; the paths clean; the history check ([`rb/check_history_e202.py`](rb/check_history_e202.py)); every list at its count and its own bytes (12; 75; 23; 39; 17; the kit's); the harness; the common self-check; the forecast and plan re-made; the scorer's self-test, its stub unchanged; the preflight; the desk tests' logs; NO E202 DATUM in any ref; ledger v3 in HEAD, then E202's v3 note in HEAD and re-made (fix-e202: else 16) |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged (and the box-login file for step 11's scrub) |
| 3 | (none) | the post: the owner's standing waiver |
| 5 | [`rb/s07_a3_sync_e202.sh`](rb/s07_a3_sync_e202.sh) | the box read first; harness-e202.json's 30 files, committed and at their sha256, into `~/aifoundry` |
| 6 | [`rb/s08_a3_build_e202.sh`](rb/s08_a3_build_e202.sh) `start`, `wait` | the detached job `build_e202.sh`; at most two starts a Pacific day; E202-BUILT; the harness with the built kernel (33), the preflight and the self-check read on the box |
| 7 | [`rb/s09_a3_reads_e202.sh`](rb/s09_a3_reads_e202.sh) | **only once the rest has opened**: the rest rule on the box first (no card command), then the time stamped (RB_OUT/e202-step7.txt) and k6's step 7, unchanged |
| 8 | [`rb/s10_a3_dry_e202.sh`](rb/s10_a3_dry_e202.sh) `start`, `wait` | `run_e202.py --dry` on the box (the doubles, energy_stub's alt card): E202-DRY rc=0 bursts=4 |
| 9 | [`rb/s11_a3_session_e202.sh`](rb/s11_a3_session_e202.sh) | the window and its cap, k6's guard, **THE REST RULE** ([`rb/rest_rule_e202.sh`](rb/rest_rule_e202.sh), with fix-e202's activity floor), **THE HUNG MARKER** (fix-e202: a refusal), **THE SAME-DAY RULE**, today's dry pass and build; then `session_e202.sh` detached |
| 10 | [`rb/s20_wait_e202.sh`](rb/s20_wait_e202.sh), while 17 | the session found by **its real script's name** (rb_e202.sh's `E202_SESSION_PAT`); GATE-STOPPED from the runner's own lines only (16); the manifest; **the runner's exit status** (fix-e202: runner.rc not 0 with no gate line, 16, a CRASH line named; not written in 10 s, 14) |
| 11 | `W/onelab.sh collect <lane>`, then [`rb/s22_collect_e202.sh`](rb/s22_collect_e202.sh) | one read-only copy back; [`collect_e202.py`](collect_e202.py): COPY-BACK EXACT, the data directory or the gate stop's record, the reducer (unchanged), the scrub, facts, SHA256SUMS; the desk-path gate; the history check |
| 12 | (the card lane's, through the lab's commit script), then `W/onelab.sh uncollect <lane>` | the data directory with its README in the form, or the gate stop's record |
| 13 | [`rb/s24_score_e202.sh`](rb/s24_score_e202.sh) | after the data commit only, never on a gate stop's record: the frozen scorer, `score_e202.py DATA`; then the v3 note's REPORTED readings, `v3note_e202.py --score DATA` (fix-e202) |
| E | (by hand) | `undesk` or `uncollect` if held; `W/hold.sh remove`; `W/book.sh release aifoundry3` (every path ends here) |

The dry listing: [`rb/list_steps_e202.sh`](rb/list_steps_e202.sh). Its lines "run on the Intel" are k6's `rb_local` wording, unchanged: they
mean the desk (aifoundry2).

## 4. The readings stated here before any datum (where E202.md leaves a choice to the kit)

1. **The first card command and the cap.** E202.md 8: "no burst starts after 33 card-minutes from the first card command ... the session
   ends by 35". The kit reads the first card command as **the session's own first card command**, its start `ettelem config`, stamped as it
   starts (the runner logs it to the millisecond); **step 7's config read** (k6's, a few minutes before) is reported apart, its time in
   RB_OUT/e202-step7.txt: this is how the lab counted E189's day (card-e189: "Step 7's config read ... adds about 1 s") and how
   verify-e195's finding 3 asks a kit to state it. Steps 8 and 9 follow step 7 without delay (the brief).
2. **The end bound.** A burst (or a smoke process) starts only if its longest span (et-who's 30 s bound, 8 s at rest, the host's `timeout
   10` inside a 30 s bound, 10 s at rest: 78 s) ends before 35 minutes less the closing's share (CLOSE_S, 45 s: et-who's bound and the closing
   config read's): in effect no burst after 32:57, three seconds stricter than the registered 33:00; an anchor only if it ends by 33:00; the
   closing's waits on the sampler end 45 s before 35:00.
3. **THE CLOCK LINE.** E202.md 9: "every sample at 600 MHz; the first sample off it sets its burst aside, a second stops the session". The kit
   counts EVERY live sample of the session (E189's kit read its own words, "in any pass", as in-pass samples only; E202's name every
   sample: the stricter reading); a sample off the clock in a burst sets that burst aside (the first by the words; a later one too, since
   its burst holds a sample off the clock: stricter), one outside a burst sets nothing aside and counts toward the second.
4. **THE STALE LINE.** "A telemetry line older than 1 s stops the session": a line whose age at its arrival (now less its own `t_ms`) passes
   1 s, or no line for 1 s (a watchdog). On aifoundry3's committed telemetry the sampler's lines never came more than 101 ms apart (E189's
   whole session, 9,436 lines; E193's and E195's: desk reads of committed data, not a measurement of the day), so a healthy sampler is not
   expected to trip it. A dead sampler is therefore a stop; the sampler is restarted only before the queue (lib.sh's six attempts).
5. **The smoke.** The five processes in the registered order; **each process is its own arm** (plan-e202.json names T-scp ... ACC as arms;
   E202.md 9: "a record with an error flag, `tensor_error` other than 0 or a failed label check ends that arm"), so a failed smoke process
   ends its arm only and the others still run; each is die-gated and et-who-checked like a burst; ACC carries `--true-labels` and no debug
   logits; `--labels-out` on the five smoke processes only (240 KB each; the program README's recommendation; the host writes it after the
   device is closed; a burst's 23 MB of label lines is not kept); a stop line during the smoke, or K1, ends the session at the gate; the R
   rule only from an arm whose smoke reads core PASS (a complete record: item 10).
6. **A failed burst ends its arm.** A burst whose host checks fail (any of E202.md 7.2's) ends its configuration; the other configuration
   goes on (each is its own arm, as in the smoke); a configuration with fewer than 2 good bursts reads NO DATA (the scorer's rule).
7. **THE KIT'S STOP K1.** A launch that did not finish (the host's own "kernel did not finish", or `timeout 10`'s rc 124 cutting the
   process) may leave a hung hart: the session ends (nothing further starts); the card is never reset. Stricter than E202.md 9, never looser.
   **fix-e202 (verify-e202's finding 5):** also a host that died (rc 125 or more: a signal such as 134 or 139, or `timeout`'s own 125-127)
   and a host that left no `--out` record after its device opened (its "device ready" line on stderr, printed before the launch): the
   same reason applies. A smoke process with no record is therefore K1 (a GATE-STOP), no longer a failed arm.
8. **The start config.** TDP 0 W, threshold 65 C, minion 600 MHz as found (k6's step 7 gate and E189's runner's on this card), else
   GATE-STOP before the sampler: a card found off it voids E202.md 3's premise (the cycle counter maps to seconds only at a pinned 600 MHz).
9. **The closing config read only while et-who reads the card free** of every other login and every other user's device process
   (verify-e195's finding 1): else "closing config read: not read (et-who does not read the card free ...)", recorded in queue.json.
   **fix-e202 (finding 8):** and only once our own sampler has stopped: a sampler that ignores SIGTERM is left running (never killed) and
   the closing read is not sent ("not read: our sampler did not stop on SIGTERM"), since the management node is single-open.
10. **THE HOST'S RESULT** is read from its own `--out` file only (E202.md 7.1), and counts only when **complete** (every field the gate, the R
    rule, the adapter and the scorer read is present and of its type); the adapter marks an incomplete record bad, so the reducer fails
    its burst (no datum, never a failed prediction). The host's stdout is kept as `stdout.txt` and never read.
11. **The operator's stop.** `touch build/e202/T<T0>/STOP`, or SIGTERM / SIGINT to the runner: a registered stop (the process in flight
    finishes, the closing follows); the runner never kills a process and is never killed.
12. **The data directory and the gate stop's record.** `docs/reports/data/<day>-e202-mnist-int8-aifoundry3/` for a session that ran a
    burst; `docs/reports/gate-stops/<day>-e202-mnist-int8-T<T0>-aifoundry3/` for one that ran none (E196's form), so that step 2's "no E202
    datum in any ref" holds for a later try after a gate stop.
13. **THE SAME-DAY RULE** (E196's): an E202 session that opened the card today is never launched again that day; a launch that ended
    "refused, no device opened" may be launched once more (two such a day at most). Step 9 reads it on the box.
14. **THE REST RULE** is E195's code line for line (verify-e195's finding 4 answered: a block opened no device only by "refused, no device
    opened: ..." or "GATE-STOP: ... (no device opened)" at the line's start): the runner writes exactly the first form for every refusal
    before its first card command, and "GATE-STOP: ..." without that suffix after the card opened, so a gate stop after the card opened
    counts as a session for the next rest. Step 7 and step 9 both read it. **fix-e202 (finding 6): THE ACTIVITY FLOOR** after E195's
    lines: the newest write of any file in a T0-named folder of ours at any depth under `build/` (the dry paths, E202's own folders and
    `build/q141k` aside) also counts as a session's end when it is more than a minute past what the log forms read, whatever the log's
    name, depth or stamps (verify-e202's attack A5 found four forms the lines alone miss); it can only delay a launch.
15. **The box's tree and folders.** `~/aifoundry` (rsync, no git); E202's build `build/e202mnist`, its files `build/e202files`, its
    sessions `build/e202/T<T0>/` (the dry pass `build/e202/T<T0>-dry/`), its build count `build/e202-build-attempts.txt`: new folders only.
16. **The files on the box.** MNIST fetched there by the program's `fetch_mnist.sh` (two mirrors, each file only by its sha256); aifoundry3
    reached both mirrors at 03:18 PST Mon 16 Nov (the read-only look above); a fetch that fails is a failed build (E202-BUILD-FAILED: the
    files), never a copy from elsewhere. numpy at 4 threads, nice 10, under 4 GB of address space.
17. **The post and the package counter.** No post (the owner's standing waiver); the package counter not read (E202.md 10).
18. **Ledger v3** (E202.md 4.4). **fix-e202 (finding 3):** ledger v3 landed (`50795847`, 06:26:27 PST) after the registration's freeze,
    so its forecast of E202's load is frozen here, before any datum, in the dated note [`E202-ledger-v3-note.md`](E202-ledger-v3-note.md)
    with [`v3note_e202.py`](v3note_e202.py), `v3note-e202.json` and `.txt` (in this kit's list); step 2 now requires the note's four files
    in HEAD and its `--check` once `tools/ledger/frozen-v3.json` is in HEAD (else 16). REPORTED beside v2; the verdicts stay v2's.
19. **The meter's absolute scale** (critic-q193's addendum, item 4): the data README's form carries the caveat (one fixed gain for every
    board, never set beside an outside meter; E184's arm S pending).
20. **No desk knob on the real path.** The runner refuses its desk-only arguments and any desk-test variable without `--dry`, in its own
    log ("refused, no device opened"); build_e202.sh and files_e202.sh have no knob at all; RB_DESKTEST's two knobs live in the runbook's
    prelude only (the runbook test's short budget and lock wait), never set on a card day.
21. **ET-WHO UNREADABLE (fix-e202, verify-e202's finding 1; E191's rule, fix-e191k).** et-who is read only when it exits 0 and answers with
    a holder line or its no-holder sentence ("No process holds an ET-SoC-1 device node or card lock."): a plain et-who asks its privileged
    helper (et-holders), which exits 0 whether or not the card is held, so any other answer means the read failed. An unreadable et-who is a
    holder: before the first card command a refusal ("refused, no device opened: ... (et-who unreadable ...)"), before a start a stop,
    at the closing the config read not sent. The doubles' et-who now answers a holder with rc 0, as the real one does.
22. **A CRASH OF THE RUNNER (fix-e202, finding 2; E194's step 10).** The runner logs "CRASH: <type>: <message>" before the closing (the
    closing, "session end" and the manifest follow as before), writes the crash into queue.json and exits 1. Step 10 waits up to 10 s
    for runner.rc after the end: not 0 with no gate line is 16, "the runner exited <rc>" (with the CRASH line named); not written is 14.
    Step 11 collects a crash with no burst as a record under `docs/reports/gate-stops/`, named a crash's record; the facts carry runner.rc
    and the crash.
23. **THE HOST'S TIMEOUT CAP ON THE R RULE (fix-e202, finding 7).** The registered rule (plan_e202.r_rule, unchanged) picks R; the kit keeps
    it only if its predicted launch is at most the host's own launch timeout less 0.5 s (main.cpp: int(min(8 s, 2 x its guard model +
    1.5 s, the --budget time left at the launch)): 8 s at R 64-96, 6 s at R 48, 4 s at R 32, 3 s at R 16; the time left read from the
    arm's own smoke, 9.5 s less its launch's start after the process's start) and the host would not refuse it (its guard over 6 s, or
    less time left than its guard plus 0.5 s); else the largest smaller allowed R that passes; none: no burst for the arm. It binds only
    when a round exceeds 25 ms (twice the forecast's 13 ms slow end) or the host's set-up before its launch passes 3.5 s (then the time
    left lowers its timeout); at the forecast (3.0 s at the point, 4.6 s at the slow end, R 96, the cap 7.5 s with a set-up under 1.5 s,
    6.5 s under 2.5 s, 5.5 s under 3.5 s) it changes nothing. Stricter, never looser: the smoke records both Rs and the time left.
24. **etcfg (fix-e202, finding 4).** E202.md 8.1's "`etcfg` and `ettelem config` at both ends" is read as the two `ettelem config` reads
    (the governor's TDP level, threshold, power state, minion clock and voltage, through E128's guard): `tools/etcfg` reads the driver's
    static nameplate (65 W on every lab card, not what the governor uses: its README), and no kit of this card's line (E189's, E195's,
    E196's, whose runner form this kit follows) runs it, so no further device command is added. The design's "module uptime" read was
    not carried into E202.md and is not added here.
25. **THE HUNG MARKER AND "AFTER E201" (fix-e202, note 11).** Step 9 refuses (10) while any session log of ours on the box holds a HUNG
    marker (E197's kit writes "<time> HUNG: ..." when a device process of ours did not end after its timeout's TERM; any stamped "HUNG"
    line counts), until the owner's word and a dated kit amendment. "After E201" is read as never beside E201 (one session of ours per
    box, the booking) and after it when both run; if E201 does not run first, E202 still waits for the box's last session of ours and its
    rest, and its README says so. **Mon 16 Nov 2026 (fix-e202, resumed in Q198):** the owner's matmul focus (his words received at or
    before 09:48:24 PST) paused E201 and E204 and kept E202, so E202 runs on aifoundry3 without E201: after the box's last session of
    ours (by the round's records at this writing, E197's sitting 1) and its 40-minute rest, read as the brief says, with a departure
    line in its README.

## 5. Device commands

`preflight_e202.sh` runs `dmcmd_audit_v2.py` with its table v2, **no `--allow` and no `--except`**, over every file the session's chain
runs, builds or sends a command from (the runner and its common module, the wrapper, the build, the files and the host check, the harness
check, E128's guard, the program's host and kernel sources): **GO, 22 send sites, 0 disallowed, every one a READ**: E128's guard's
`ettelem config` (GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES,
GET_ASIC_VOLTAGE) and `ettelem sample` (GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE,
GET_ASIC_FREQUENCIES), and the runner's two calls of them, read as going through the guard; the host opens the ops node only
(`createPcieDeviceLayer(true, false)`; its runtime's creation aborts the submission queues of the card it enumerates, verify-scout's
lab-wide note of Mon 16 Nov: harmless on a card held alone, which the session's lock and et-who make it); the kernel sends nothing.
No set, no reset, no statistics reset, no firmware write, no PMIC write.

## 6. THE REAL-PATH DESK TEST and the audit of every dry branch

[`desk/desktest_realpath_e202.sh`](desk/desktest_realpath_e202.sh) and [`desk/realpath_e202.py`](desk/realpath_e202.py) run **the session's
real path, DRY unset**, exactly as step 9 launches it, in a stand-in aifoundry3 tree holding harness-e202.json's files as the sync puts
them, the kernel built by build_e202.sh today on this desk (its `.text` at the pin) and the 18 checked inputs, with the stand-ins at the
tools' real paths; the build record re-written with the stand-in host's sha256. The cases (in its log):

| case | what it runs | asserted |
|---|---|---|
| ST | the sandbox | aifoundry3; two regular files at /dev/et0_*; a private PID namespace; the tree's harness with the built kernel (33) |
| D | the dry pass in step 8's form | the smoke gate, 4 bursts, every line DRY, no stand-in called |
| **P** | **the whole real path**, every host's stdout split by a runtime line inside its JSON, every 25th sampler line too | the steps in order in the kits' log form, no DRY line; what reached the tools: config twice, ONE sampler, 17 host processes, nothing else; et-who 19 times; every argv the registered one; every host's result read from its own file though its stdout was split; THE ORDER and R 96; while it ran: the lock held, step 10's pattern matching the real wrapper and no decoy, k6's ours_live counting it; then the collection (COPY-BACK EXACT, 12 bursts reduced by the unchanged reducer, each burst's J over idle against the energy the stand-in card injected), the frozen scorer's words and the dram pair REPORTED, the rest rule reading the session |
| R1-R9 | another host's name; two cards; a synced file changed; the build record not today; the host not the recorded one; an input off its pin; the lock held; a holder; a desk-test variable | each refused before any card command, in the session's own log (rc 2) |
| G1-G3 | the start config at TDP 5 W; a dead sampler; the sampler quiet in anchor 1 | GATE-STOP (rc 3), no host process; six attempts through the guard; the stale line, the closing read |
| S1 | board 66 W in burst 1 | STOP; the host finishes; its 10 s rest after whole; nothing after; the closing read |
| FB | T-scp's smoke fails; a holder before burst 3 | the dram pair scored; STOP before burst 3; the closing config NOT sent |
| K1, SG | a launch that does not finish; no pair passing the smoke | STOP, nothing further; GATE-STOP after the smoke, the closing read |
| T, SIG | the operator's STOP file in burst 2's rest before its host; SIGTERM to the runner in anchor 1 | no host process for burst 2 (a stop starts nothing), nothing further, the closing read; a registered stop, no host process, the manifest |
| W1, W2 (fix-e202) | et-who's helper refused (rc 1, nothing on stdout) at the start; et-who rc 0 with neither a holder line nor its no-holder sentence from its 9th read | refused before any card command (rc 2); STOP before burst 3, the closing config NOT sent |
| K1b (fix-e202) | a host that dies mid-launch in burst 1 (rc 134, no --out record) | K1, nothing further |
| CR (fix-e202) | a file where the runner makes burst 1's folder: the runner crashes there | "CRASH: <type>: <message>" before the closing, queue.json's crash, the closing read, session end, the manifest, runner.rc 1 |
| Z | the end | no stand-in, sampler or session process left |
| AUDIT | [`desk/dry-branches-e202.tsv`](desk/dry-branches-e202.tsv) | every line of `run_e202.py` and `session_e202.sh` that branches on DRY (18) has a row naming the cases that run its real branch, every row's line is the file's own, and every named case passed in the same run |

## 7. The real-bytes test (the lesson of E191's first session)

[`desk/realbytes_e202.py`](desk/realbytes_e202.py): the host's result reader on **the mnistmlp host's own nine --out files from the
simulator** (read exactly; S3x's logits-only failure passes the gate; the six runs from before the host wrote `core_status` fail safe; a
simulator record is not a card's), on **1a4bc1e3's split stdout** (beside no --out file: no result, never the head; as the --out file: no
result; E191's first reader read `{}`, the negative control), on **the splice** (aifoundry1's runtime line at every byte offset of the nine
records: the exact record or none; with no newline, inside a string: every record read keeps every field the gate and the scorer read, or
fails the gate); the sampler reader on **E189's whole committed session telemetry and three of E195's passes** (every line read exactly; the
runtime text spliced at every offset of a line: a sample read keeps every field the stops and the reducer read, or the line is lost); the
config reader on **E195's raw config line** and E189's; the et-who reader on **E195's committed et-who text**; and **other hosts' real
records** (E189's ledger line, E190's rgm136 stdout) refused as not the mnistmlp host's. fix-e202: B6 also reads E195's real et-who text and
the holder form through the unreadable rule (both readable at rc 0; the real text unreadable at rc 1); B1 reads the R rule's detail too.

## 8. Files, the lists and step 2

| file | what |
|---|---|
| `run_e202.py`, `e202_common.py`, `session_e202.sh` | the runner, its common module (the smoke, the order, the R rule's call, the result reader, the adapter, the stop lines, et-who's lines), its detached wrapper |
| `build_e202.sh`, `files_e202.sh`, `hostcheck_e202.py` | the box build, the files, the host by its behaviour |
| `check_e202.py`, `harness-e202.json`, `preflight_e202.sh` | the harness (30 files), the device-command preflight |
| `fake_card_e202.py`, `collect_e202.py`, `selftest_run_e202.py` | the doubles; the collection's desk half; the runner's desk test |
| `desk/` | the real-path test and its stand-ins and audit table, the real-bytes test, the build's desk test, the kit's checks |
| `rb/` | the runbook's steps, the rest rule, the history check, the dry listing, the runbook's and the rest rule's desk tests |
| `KIT.md`, `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e202.md` | this file; the card lane's brief; the data README's form |
| `E202-ledger-v3-note.md`, `v3note_e202.py`, `v3note-e202.json`, `v3note-e202.txt` | fix-e202: E202's dated ledger v3 note (E202.md 4.4): ledger v3's forecast of the same load, frozen before any datum, REPORTED; `--check`; `--score DATA` after the data commit |
| `logs/*.txt` | the desk tests' logs (the scratch, the clone and the home masked) |
| `SHA256SUMS-e202-kit` | every kit file but itself and step 2 |

**Step 2 (`rb/s03_desk_e202.sh`) is outside `SHA256SUMS-e202-kit`** (a list cannot hold the sha256 of the file that pins the list): its own
sha256 and the list's are given in the land file's anchor lines.

## 9. What the desk cannot show (for the verifier and the readiness critic)

1. **The program on the card**: it has never run on silicon (E202.md 11): UA = 1, the debug path's 64 B TensorStore rows, scp staging at 32 x
   32 and the launch's length meet the card first in the smoke, whose gate and R rule read them.
2. **The box's build and files**: step 6 there, against aifoundry3's own /opt/et (its RISC-V GCC reports another version string: the ELF will
   differ as a file, E202.md 2; the gate is the `.text`), with the MNIST fetch from the mirrors (both answered at 03:18 PST Monday) and the
   numpy model on aifoundry3's python3 (3.12.3, numpy 1.26.4, read the same minute).
3. **The box's sampler, et-who, card lock and runtime**: the real `build/ettelem/ettelem`, `et-who` and the runtime meet the runner first on
   the day (step 7 reads the configuration through the same guard before).
4. **Another user's device process**: the ps rule for other users cannot be made at the desk (no other user's process can be started).
5. **The collection and the scorer** ran on the real-path test's and the doubles' sessions, not on a card's.
6. **Our own live collector on aifoundry3** reads the management node a few milliseconds a second while the card is free: a single et-who
   read that catches it reads a holder of OUR login (never counted: the runner counts other logins only), but the opening config read or
   the sampler's start could meet it as a busy node (E192's and E193's readiness estimate about 0.4-0.5 % an open, not measured): a
   GATE-STOP after the card opened, so no second try that day (the same-day rule).
7. **The stand-ins' names**: the desk tests place shell stand-ins at the host's and the sampler's real paths; each execs Python at once, so
   for its first milliseconds its process name is the real tool's. Every desk test waited for THE QUIET DESK FLAG to be absent.
8. **fix-e202's readings on the box** (KIT.md 4, items 21-25): the real et-who's answers when its helper fails, the real host's exit codes
   when it dies, the host's real set-up time (the R rule's cap reads it from each arm's own smoke) and the log forms of E201's and E204's
   kits meet the box first; the desk drives each through doubles, stand-ins and committed bytes only. The first two are fail-safe (each
   reads as a holder, or as K1); the cap can only pick a smaller R; the rest rule's floor can only delay a launch.

## 10. Findings for the verifier (desk checks of code)

| # | severity | what | here |
|---|---|---|---|
| 1 | low | E202.md 9's clock line words "every sample" where E189.md 11 said "in any pass"; the kit takes the stricter reading (section 4, item 3), which can stop a session E189's reading would not | for the go to confirm; no rule changes |
| 2 | low | the stale line (E202.md 9) makes a dead sampler a stop, so E189's restart of a dead sampler mid-session is not carried over | stated (section 4, item 4); aifoundry3's committed telemetry never gapped above 101 ms |
| 3 | low | E202.md names the first card command without saying whether step 7's read counts; the kit counts from the session's own and reports step 7's apart (E189's day; verify-e195's finding 3) | section 4, item 1; the stricter alternative (from step 7) would cost the minutes between steps 7 and 9 |
| 4 | note | the end bound makes the last burst start by 32:57, three seconds inside the registered 33:00 | section 4, item 2: so that the closing's et-who and config read fit before 35:00 at every bound |
| 5 | note | `--labels-out` on the smoke processes is the kit's addition (240 KB a process, host-side after the device closes); the bursts keep none | section 4, item 5; the program README recommends it on card runs |
| 6 | note | the smoke's arms each run even after another fails (each its own arm, E202.md 9's words with plan-e202.json's names); after a failed launch the host's checks catch a next launch's damage (the program README), and K1 ends the session on a launch that did not finish | section 4, items 5-7 |
| 7 | note | the real-path test's host is a stand-in (the real host has never run on a card); the real host's behaviour is read by hostcheck_e202.py on the real build, and its real --out bytes (the simulator's) by the real-bytes test | sections 6 and 7 |

## 11. Labels, and compute

Every figure quoted from E202.md and its files (the forecasts, K, the order, the caps, the stops, the pins) is **registered**. The desk tests'
results are **desk checks of code**, not measurements; every watt and degree in them is a stand-in's arbitrary value or the frozen
forecast's point driven through a toy card, never a measurement and never a reading of E202. The sampler gaps in section 4 are desk reads
of committed data. Nothing here is blind, held out or post hoc; no E202 datum exists. Compute: on aifoundry2 through the round's CPU slots
at nice 10, every logged desk test inside the no-device sandbox, THE QUIET DESK FLAG absent; the real builds with `-j4`; aifoundry3 read
once, read-only; no simulator, no card.

## 12. fix-e202: verify-e202's findings, answered before the land (Mon 16 Nov 2026)

| # | verify-e202's finding | the answer, and where | the test |
|---|---|---|---|
| 1 | minor: a failed et-who read counted as FREE (4 of its 7 failure modes) | E191's unreadable rule (`e202_common.etwho_unreadable`, `run_e202.foreign`): section 4, item 21; the doubles' et-who answers a holder with rc 0, as the real one | the common self-check's 11 forms; SELFTEST-RUN W1-W4; REALPATH W1, W2; verify-e202's own attack A1 re-run on the fixed runner |
| 2 | minor: a runner crash read as a clean end (step 10 exit 0) | "CRASH: <type>: <message>" before the closing and in queue.json, exit 1 (`run_e202.py`); step 10 reads runner.rc (`rb/s20_wait_e202.sh`); step 11 names a crash's record (`collect_e202.py`); the brief's step-10 row, section 3 and the README form: item 22 | SELFTEST-RUN X1-X3; REALPATH CR; SELFTEST-RB WT4, WT5; verify-e202's attack A2/A3 re-run |
| 3 | minor: ledger v3 landed after the freeze: the dated v3 note owed, and step 2's test missed other names | the note written and frozen here (`E202-ledger-v3-note.md`, `v3note_e202.py`, `.json`, `.txt`); step 2 requires its four files and its `--check` once ledger v3 is in HEAD: item 18 | V3NOTE CHECK PASS (CHECKS-E202); SELFTEST-RB P1 and V3; SELFTEST-RUN's E2E reads `--score` against the frozen scorer |
| 4 | low: etcfg registered in E202.md 8.1, never run, no word | read as the two `ettelem config` reads, no command added; the module uptime read not added: item 24 | (a reading, stated before any datum) |
| 5 | low: K1 missed a host that died mid-launch | K1 also on rc 125 or more and on no `--out` record after the device opened: item 7 | the common self-check; SELFTEST-RUN K1b, K1c; REALPATH K1b; verify-e202's attack A4 re-run |
| 6 | low: the rest rule missed 4 of 8 log forms | THE ACTIVITY FLOOR (item 14); the brief: ready-e202 reads E201's and E204's committed session logs through the rule (both paused on Mon 16 Nov: then the committed log of the box's last session of ours, E197 sitting 1's at this writing), and the booking waits 40 minutes after the box's last session of ours by the clock | SELFTEST-REST R14-R18, R20; verify-e202's attack A5 re-run |
| 7 | low: the R rule's 6 s ceiling above the host's own timeout below R 64 | the host's timeout cap after the registered rule, stricter only: item 23 | the common self-check (the timeouts, a 32.5 ms and a 45 ms round, 5 s left); SELFTEST-RUN R3 |
| 8 | nit: the closing read sent while our sampler would not stop | not sent then: item 9 | SELFTEST-RUN CL |
| 9 | nit: E202.md line 11 quotes the checkpoint's step-6 words | not taken: the registration is not re-made (its fix was "only if the registration is re-made anyway"); the phrase is E202's title | none |
| 10 | nit: no README row for the REPORTED latency; runner.rc named only 0 and 3 | both added to `DATA-README-FORM-e202.md` | (a form) |
| 11 | note: "after E201" with no rule if E201 never runs; HUNG markers not read | the go's reading (E201 paused on Mon 16 Nov by the owner's matmul focus: E202 runs without it, after the box's last session of ours and its rest), and step 9's refusal on a HUNG marker: item 25 | SELFTEST-RB HG |
| 12 | note: S1T at 10% mostly tests the rest law | a registered choice, unchanged; the README form tells the reader | none |

SPDX-License-Identifier: Apache-2.0
