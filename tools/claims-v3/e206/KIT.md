# E206's run kit: both arms (aifoundry3 card 0, aifoundry1 card 1) from aifoundry2, in E190's kit form: one runner with one sampler and the stop lines live, the identity gate, read and watch, E206's smoke and then the stop-path test, every run under a plain `timeout 10` and never killed; rgm136 built on each box through the kernel gate; the host's records read past any runtime line; the runbook with step 7 only once the rest has opened; the reducer to the frozen scorer's form (Q198; kitted, fixed before the land, not run)

*Mon 16 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q198, lanes `kit-e206` and `fix-e206`). No card was claimed or opened: aifoundry2
has a card, so every desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its
sandbox (no /dev/et*, an empty /run/lock). No device command was sent, nothing was posted. One box was reached: aifoundry3, for ONE read-only
look while no lane booked it (Mon 16 Nov 2026 12:02 PST: the box tree, its reader's sha256, its riscv gcc's version string; nothing written
there, no device opened). aifoundry1 was not reached (yielded to the model session's own sweeps since 11:04 PST). New files only, all under
`tools/claims-v3/e206/`. The registration [`E206.md`](E206.md), with its amendment A1 made before the land (its commit found by content: the
commit that added E206.md, its `tools/claims-v3/e206` subtree `114c094b...`; `SHA256SUMS-e206-registration` `d9fb06e4...`, 25 entries) and
every file its list names stay as committed. **No E206 datum exists. Nothing here changes a forecast, a band, a rule, a threshold, the order,
the card time, the cap, a stop or the scorer.** Where E206.md leaves a reading to the kit, the reading is stated in section 4 before any datum;
one of them (item 1, the die line's hottest sensor) was the kit's reading of a registered line that cannot be read literally on arm A's card:
the verifier accepted it in substance and E206.md's amendment A1 now registers it. **Section 9 lists the verifier's findings and the fixes
made before the land** (lane `fix-e206`: the operator's STOP file, a sampler that will not stop, the runbook's desk test once the kit is
committed, the board line's samples, the runtime-line parser's second pass, a runtime line naming another card, the card lane's bounded waits).*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

## Results first (desk checks of code and desk reads of committed records; nothing is measured)

| check | result | log |
|---|---|---|
| **the runner on the doubles** (`selftest_run_e206.py`): both arms' short path with the identity gate and read, the smoke and THEN the stop-path test (E206.md 7's order), the 87 C latch tripping nothing; every config gate (TDP, card 0's block, 519 mV, no block, a failed read, a read HUNG past its TERM, a runtime line); every holder (another login, ours on card 0, another login on card 0 at arm B's start, et-who unreadable, a device process, a CI job, the lock held); the sampler dead, on card 0, silent, dying; the stop-path test with no live sample; the smoke (a wrong check, a crash, a host on card 0, no rise, a runtime line inside a record, records of another mask); K1; **a host hung past its TERM (HUNG, exit 8, no closing read, NOTHING KILLED: the double ended by itself)**; a host ended by TERM (rc 124); two failures in a row; a run whose records name another command (never read as data; the frozen scorer sets it aside and flags it); the board, the mean and the latch lines; 72.0 W not above 72; the die gate; the card-time rule; an operator's SIGTERM; a crash; **added before the land (fix-e206): the operator's STOP file touched mid-session (nothing further starts) and there before the start (refused); a sampler deaf past both SIGTERM waits (the session stops, never two samplers, no closing read, nothing killed); a runtime line naming card 0 on arm B's smoke, first run and config read (identity trips) and on arm A (its own card); 95 W on every other sample with no board reading between (trips)**; **THE ORDER**: both arms' whole registered sequence (241 and 229 runs), every key and argv the registered; the refusals without `--dry` and the REAL runner stopping at its box check; **END TO END** on both arms through the reducer and the FROZEN scorer | **SELFTEST-RUN-E206 53 of 53 PASS**; OR-A: PASS: rc 0; 241 runs of 241, every key and argv the registered (0 differ); 125 s; OR-B: PASS: rc 0; 229 runs of 229, every key and argv the registered (0 differ); 119 s; E2-A: PASS: 24 point runs; t_gemm worst 1.08e-06; J over idle against the injected watts x seconds worst 0.67%; E2-B: PASS: 24 point runs; t_gemm worst 1.08e-06; J over idle worst 0.47%; HG: PASS: rc 8; the hung double ended by itself after 14.0 s, nothing killed it; SF, S0, DF, RT, RT2, RTC, BN: PASS (section 9) | [`logs/selftest-run-e206.txt`](logs/selftest-run-e206.txt) |
| **the REAL path** (`desk/realpath_e206.py`, `desk/realpath_e206.sh`): run_e206.py WITHOUT --dry, each arm under its box's hostname (a private UTS namespace) and a private PID namespace, stand-ins for the reader behind the REAL guard, et-who, the host, the lock and the nodes, the REAL kernel ELF from the REAL build: the box check (kernel gate, harness, preflight), the lock, et-who and ps, the identity gate and read, the smoke, the stop-path test, the first tie and two points; a host hung past its TERM under the real `timeout 10` (left, ending by itself); a changed .text refused; **arm B's identity both ways** (card 1's forms pass; card 0's config, the sampler on card 0, a host on card 0, **a missing ET_DEVICES** (the runner's environment and the REAL guard), **a second card's holder** (another login, and a process of ours, on card 0) refused); a sampler death; aifoundry1's runtime line inside the host's records | **REALPATH-E206 17 of 17 PASS** | [`logs/realpath-e206.txt`](logs/realpath-e206.txt) |
| **the parsers on real committed bytes** (`desk/realbytes_e206.py`): E190's 174 committed rgm136 stdouts on both cards (87 carrying aifoundry1's runtime line), E190's 12 card-1 bursts through the reducer against E190's committed reduction, the runtime line at every byte offset of a real record, two runtime lines nested one inside the other at every offset of the same records (fix-e206), 1a4bc1e3's and 7156ac15's split stdouts against their committed readings, the config line, and the identity gate both ways on 21 committed config forms | **REALBYTES-E206 7 of 7 PASS** | [`logs/realbytes-e206.txt`](logs/realbytes-e206.txt) |
| **the build on this desk's real toolchain** (`desk/desktest_build_e206.sh`; riscv gcc "() 15.1.0", g++ 13.3.0, cmake 3.28.3) | **DESKTEST-BUILD-E206 7 of 7 PASS** | [`logs/desktest-build-e206.txt`](logs/desktest-build-e206.txt) |
| **the runbook** (`rb/selftest_rb_e206.sh`: a fake ssh and rsync, two stand-in boxes, the real builds): the window rule (another arm, another runbook, another day), the lab-git lock, step 2 at every pin, the history check and a shadow, an arm's data refusing its own step 2 and reported by the other's, the look, ours_live, the sync to both boxes, a login link, a hang, NO-THIRD-BUILD, the ET_DEVICES gate through the runbook, the real build of arm A, **step 7 refusing with no config read sent until the rest has opened**, arm B's step 7 (card 1's forms, card 0's refused, a card-0 holder), the dry passes, the HUNG marker, the same-day rule, the REAL session stopping at its box check, step 10's readings (running, gone, HUNG, K1, CRASH, a STOP line), the copy-back, the gate stop's record, a copy not exact, a session that ran through step 12's data directory and step 13's frozen scorer; run with the kit's files untracked (as here) and, after the kit's local commit, with the kit committed (fix-e206) | **SELFTEST-RB-E206 27 of 27 PASS** (the kit untracked, this log) | [`logs/selftest-rb-e206.txt`](logs/selftest-rb-e206.txt) |
| the dry listings, every step of each arm with stand-ins | **arm A: dry listing: 14 steps listed, 0 exited non-zero, 0 box calls**; **arm B: dry listing: 14 steps listed, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e206-A.txt`](logs/dry-listing-e206-A.txt), [`logs/dry-listing-e206-B.txt`](logs/dry-listing-e206-B.txt) |
| `dmcmd_audit_v2` on the session's files (`preflight_e206.sh`: the runner, its two modules, the wrapper, the build, the harness check, the guard, the host's source) | **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)**, every one a READ, no allow-list, no exception | [`logs/dmcmd-audit-e206.txt`](logs/dmcmd-audit-e206.txt) |
| the quick set | 12 lines PASS / OK / GO (the two modules' self-checks, the harness re-made and at its sha256, the registration's four checks and its two self-tests, its list, the preflight, bash -n of every shell file); no call in the kit's code sends a kill (the lines naming one are prose, listed) | [`logs/checks-e206.txt`](logs/checks-e206.txt) |

## 1. The kit, in E190's form

- **The runner** ([`run_e206.py`](run_e206.py), [`session_e206.sh`](session_e206.sh), [`e206_common.py`](e206_common.py),
  [`e206_ident.py`](e206_ident.py)): one arm's whole session on its box (E190's run_e190_v2.py with its note 1's identity module). Before
  anything opens: the host name is the arm's (arm B: its device environment carries ET_DEVICES=1; arm A's does not), build/e206rgm's record
  today's BUILT by build_e206.sh on this box (arm B: its ET_DEVICES reading passing), the kernel through THE KERNEL GATE again, the host at the
  sha256 the build recorded, the arm's reader at its pin, the 20 tiles at their manifests' sha256, the harness (HARNESS OK) and the preflight
  (dmcmd_audit_v2 GO). Then the card's lock (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD COMMAND `ettelem config`
  through [`ettelem_guard_e206.sh`](ettelem_guard_e206.sh) under a plain `timeout 10` with its stderr kept (the start config and THE IDENTITY
  GATE; the card time counts from it), ONE sampler (10 Hz) whose every line feeds THE STOP LINES as it arrives, THE IDENTITY READ, the smoke
  and then the stop-path test, the arm's registered sequence, the closing config, "session end", MANIFEST.sha256 last. Nothing is set. Every
  start (each run, each smoke process, every rest read) first reads the operator's STOP file; never two samplers at once (fix-e206, section 9).
- **No SIGKILL anywhere** (W/out/orch/kill-rule.txt; AGENT.md "never kill -9"): every device process is under a plain `timeout 10`; the
  runner waits for it with a bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the
  stop file, starts nothing further, sends no further card command (no closing config read), closes the session and LEAVES the process
  (exit 8). et-who, the harness check and the preflight are waited on with a bound and left past it (a failed read, never a kill). The
  sampler is stopped by SIGTERM only. The build runs under a plain `timeout`. The one kill in the whole path is k6's bounded runner's
  (rb_run.py, unchanged, every kit's): past a call's bound it ends THE DESK'S OWN ssh client, rsync or collector (TERM, then KILL); never a
  process on a box, where nothing of E206's sends any signal to a device process.
- **The build** ([`build_e206.sh`](build_e206.sh), [`check_e206.py`](check_e206.py)): E136's rgm136 unchanged, into **build/e206rgm** (a new
  folder of ours) on each box; the kernel through THE KERNEL GATE (E191's kit fix: the .text always the registered `61315bf6...`, and the
  whole ELF the registered `aace138c...` or its loadable identity the pinned `649d4079...`, the identity of the registered ELF itself, made from
  a real build on this desk); the host by its behaviour (four refusals main.cpp makes before its device Session); on aifoundry1 the ET_DEVICES
  reading as a gate; build/e206rgm/BUILD-e206.json.
- **The doubles** ([`fake_card_e206.py`](fake_card_e206.py)): config (the arm's committed start config and its identity block), et-who (who
  holds the stand-in nodes and lock, from /proc), a toy card's sampler driven by the launches the host double announces (its latch at the arm's
  committed 87 C or 66 C), and the host (rgm136's SPARSITY records on a virtual clock at each point's F1 seconds and watts; modes for every
  failure the tests need, among them a host that IGNORES its TERM).
- **The reducer** ([`reduce_e206.py`](reduce_e206.py)): each arm's session into the frozen scorer's data form (score_e206.py's docstring) and a
  table. **The collection** ([`collect_e206.py`](collect_e206.py)): COPY-BACK EXACT, the arm's data directory (or a gate stop's record), the
  scrub, the reducer, SHA256SUMS. **The harness** ([`check_e206.py`](check_e206.py), `harness-e206.json`, 46 files) and **the preflight**
  ([`preflight_e206.sh`](preflight_e206.sh)).
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged, per arm (the arm the first word of every box step; one
  RB_OUT per arm): the window; step 2 (the pull under the lab-git lock, both lists pinned by count and bytes, the history check, the harness,
  the registration's checks and the scorer's self-tests, the preflight, the desk tests' logs; outside the kit's list); the look (k6's); the
  sync; the build; **step 7, only once the rest has opened**; the dry pass; the session; the wait; the copy-back; the data directory; the
  scorer after the data commit. **No post and no release** (waived). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lane's brief,
  with THE ONE-LAB RULE and THE QUIET HOLD in its step table; [`DATA-README-FORM-e206.md`](DATA-README-FORM-e206.md) is the data README's
  form.

## 2. Card-minutes and the cap (registered; unchanged)

Arm A 92.6 card-minutes planned (241 runs), arm B 87.6 (229 runs) (plan-e206.txt); no run starts once the arm's card time passes 112
minutes; at 120 the session ends after the run in progress; a started run is cut only by a stop. The registered subset if cut: the smoke,
tie 1, pass 1 and tie 2 (every point once).

## 3. The order on each box

The card lane's full table, with the booking, THE ONE-LAB RULE (desk / undesk around steps 0-2, collect / uncollect around step 11 to the
data commit's push), THE QUIET HOLD and the end of every path, is [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps:

| step | file | what |
|---|---|---|
| 1 | `rb/s02_window_e206.sh <A\|B> <day> <last start> <last end>` | first; today only; the arm's own window (G = its booking) in its own RB_OUT |
| 2 | `rb/s03_desk_e206.sh <A\|B>` (outside the kit's list) | the window; the pull under the lab-git lock; the registration and the kit found by content, ancestors of HEAD; the paths clean; HISTORY OK; both lists at their pins; the harness; both self-checks; the registration's checks and the scorer's two self-tests; the preflight; the desk tests' logs; no datum of this arm in any ref |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` / `aifoundry1` | k6's, unchanged (et-who, who, uptime, the holder rule; aifoundry1's identity by continuity); our login recorded for the scrub |
| 5 | `rb/s07_sync_e206.sh <A\|B>` | the rsync into `~/aifoundry` (A) or `~/nekko` (B); HARNESS OK on the box |
| 6 | `rb/s08_build_e206.sh <A\|B> start`, then `wait` | the detached build, NO-THIRD-BUILD, the record (KERNEL OK; arm B the ET_DEVICES reading), the harness, the preflight and both self-checks on the box |
| 7 | `rb/s09_reads_e206.sh <A\|B>` | THE REST RULE on the box first, no card command (10 while it has not run); then the config read: arm A k6's step 7 unchanged (TDP 0 W / 65 C / 600 MHz, et-who clean); arm B E206's own (card 1 through E206's guard with ET_DEVICES=1: 65 W / 65 C / 600 MHz, `/dev/et1_mgmt`, ID 1, minion_mv below 510, et-who clean on card 1 and card 0) |
| 8 | `rb/s10_dry_e206.sh <A\|B> start`, then `wait` | the runner on the box with its doubles, no device |
| 9 | `rb/s11_session_e206.sh <A\|B>` | k6's guard and aifoundry1's identity by continuity, THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e206.sh` detached |
| 10 | `rb/s20_wait_e206.sh <A\|B>` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e206.sh <A\|B>` | one read-only copy back, COPY-BACK EXACT |
| 12 | `rb/s23_data_e206.sh <A\|B>` | the data directory `docs/reports/data/<day>-e206-matmul-sweep-<aifoundry3\|aifoundry1-c1>/` (or a gate stop's record under `docs/reports/gate-stops/`), the scrub, the reducer, SHA256SUMS, the desk-path gate, the history check; then the card lane's data commit |
| 13 | `rb/s24_score_e206.sh <A\|B>` | after the data commit only: score_e206.py (registered, unchanged) on the committed data-e206.json |

## 4. The readings stated here before any datum (where E206.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH (the kit's reading; accepted in substance by the verifier and registered, before the land, by
   E206.md's amendment A1 item 1).** E206.md 6 registers each arm's die line on "the
   shires' mean or the hottest shire sensor (E190's watcher)". The telemetry's `minshire[2]`, which E190's watcher read as the hottest
   sensor, is a latch held since the card's last statistics reset (docs/findings/14-card-behaviour.md, its dated note of Tue 3 Nov 2026;
   E190's kit note 1, item 4.1), not the hottest sensor now: **on aifoundry3 card 0 it reads 87 C in every committed sample of E189, E195,
   E196 and E197** (and 66 C on card 1 in E198's and E199's), so read as a level it would trip arm A's 70 C line at the session's first
   sample and arm A could never run. The telemetry carries no live reading of the hottest sensor, and a statistics reset (which would re-arm
   the latch) is outside E206's allowance (none). So the line trips **on the shires' mean (`minshire[0]`) at or above the line, or on the latch
   only when it has risen during the session above the lowest value it read since the session's first sample and reads at or above the line**
   (a new maximum since the session began is the one live reading of the hottest sensor the telemetry gives). This is never looser than what
   the telemetry can show, but it is looser than the literal words on a card whose latch already reads above the line: a sensor between the
   line and the latch (on aifoundry3, between 70 and 87 C) is seen only through the mean. Arm A's planning peak die is 59.1 C (the mean),
   its F1 reported die 52-61 C. The die gate reads the mean, as E190's did. `e206_common.Stops`; desk cases G1 (the 87 C latch trips nothing),
   D1 (the mean at 70 C trips), D2 (the latch rising to 88 C trips), and the latch after a drop (a reset by another) rising past the line.
2. **The other stop lines** (E206.md 6): arm A board above 70 W on 3 samples in a row, die at or above 70 C; arm B above 72 W on 3, die at or
   above 80 C; the board strictly above the line on 3 samples in a row that carry a board reading, a sample with no board reading neither
   counting nor breaking the row (fixed before the land, the verifier's finding 7; E206.md A1 item 2: the first version restarted the count
   there, so 95 W on every other sample with no reading between never tripped). A trip touches the hosts'
   `--stop-file` at once: the running host ends its loop at its next launch boundary (about 0.5 s; this host's own path, proven on silicon by
   E146), never killed; nothing further starts; the run's 4 s read and the closing follow.
3. **The smoke, then the stop-path test** (E206.md 7's order): 30 s at rest (the rest die: the median of the shires' mean over it; the die
   gates are formed from it), then one process each of p001, p046 and p021 with `--seconds 2 --budget 3.5` (the budget is E146's and E190's
   smoke's), not die-gated (E146's and E190's smoke); each must exit 0 with every launch ok, its check of C exact or approx, its cycles an op
   (the check record's, E190's reading) within 50-250% of F1's point, the board at least 2 W over the rest during its launches (at least 3
   samples; E190's note 1), and the host on the arm's own card (the watch); THEN the stop-path test on live samples (test thresholds every
   sample crosses: 0 W on 3 samples, 0 C; each test line touching its own file, never the hosts' stop file, and refusing a start; no launch).
   Any failure: the smoke gate failed, no run (a gate stop).
4. **The start config** (plan-e206.json): arm A TDP 0 W / 65 C / 600 MHz, arm B 65 W / 65 C / 600 MHz, read as found, nothing set; read again
   at the end (never after a HUNG, nor while the sampler would not stop).
5. **The identity** (E190's note 1, unchanged in substance): arm A `/dev/et0_mgmt`, physical device ID 0 on the config read's stderr (the same
   reader prints exactly that block on aifoundry3: E189's committed sampler.err); arm B `/dev/et1_mgmt`, ID 1 and minion_mv below 510 (card 1
   read 499 or 500 in every committed read; card 0 519; aifoundry3 523). The identity read with the sampler running; the host watch at every
   process; a host naming or holding another card stops the session at once (in the smoke: the smoke gate).
6. **The holders.** Arm A: any holder line of another login, another user's device process, a CI job, any other device process of ours. Arm B:
   a holder line of another login on card 1, any line of ours on card 0 (never two of our sessions on aifoundry1; the model session's processes
   run under the same login and count as ours), a CI job, any other device process of ours; and **at the session's start, a holder line on card 0
   of ANY login** (the kit's start rule, stricter than k6's: every runtime creation sends an abort to every submission queue of every card its
   device layer enumerates, verify-scout's correction of Mon 16 Nov 2026; only ET_DEVICES=1 keeps it off card 0, and that is proven only by
   the session's own identity reads); later, another login's line on card 0 is reported in the run, never a stop. **An unreadable et-who is a
   holder** (E202's fix). Counts only.
7. **The die gate**: arm A min(60, rest die + 4) C, arm B min(63, rest die + 3) C, on a live sample (under 2 s old) only, waiting at most 300 s
   and never past the card-time rule or a stop; else that run is NO DATA.
8. **A run**: the die gate, the holders again (et-who and ps), 10 s at rest (p_rest = the median board W of its last 5 s), ONE host process
   `timeout 10 sparsity_host <the point's registered host_args> --kernel <ELF> --stop-file <STOP>`, a 4 s read. A live sampler before the
   process, else the run ends there flagged and the sampler is restarted (SIGTERM to a stale one); **a stale sampler that will not stop on
   SIGTERM is left running, never killed, and the session stops: no second reader of the management node is started, and the closing config
   read is not sent while it lives** (fixed before the land, the verifier's finding 4).
9. **Failures.** A failed process (rc not 0, `timeout 10`'s 124 among them) is flagged; **two failed processes in a row stop the session**
   (E190's E64 rule, for one-process runs). **K1**: a host whose stderr says "kernel did not finish" (a launch that did not finish: it may
   leave a hung hart) stops the session at once. **HUNG** (item 1 of section 1): exit 8. A crash of the runner is named and exits 1, its closing
   run.
10. **Card time** counts from the start config read (the session's own first card command; step 7's read is reported apart). A run starts
    only if the card time is under 112 minutes and its longest length (28 s once its gate has passed) fits the 120-minute cap less 60 s of
    closing and ends 90 s before the window's last end.
11. **The readers**: arm A aifoundry3's `build/ettelem/ettelem` (`16037641...`, read there on Mon 16 Nov 2026 12:02 PST; the reader of every
    aifoundry3 kit through E128's guard), arm B the lab's card-1 reader (`8008f96f...`, E157's, E164's, E172's, E190's and E198's pin); one
    guard, `config` and `sample` only, aifoundry3 with ET_DEVICES unset and aifoundry1 with ET_DEVICES=1, any other box refused.
12. **THE REST RULE** (E206.md 6): each arm's first card command at least 40 minutes after our previous session on that box ended (on aifoundry1,
    either card). E202's rule (every session-log form of ours, the activity floor) with one addition: **the model session's folders**
    (`~/claude/work/ee-*/`, its newest file a session's end: it runs its own sweeps on aifoundry1 under the same login). Steps 7 and 9 read it on
    the box, step 7 BEFORE its config read (no card command while the rest has not run).
13. **THE HUNG MARKER and THE SAME-DAY RULE** (E202's): step 9 refuses while any session log of ours on the box holds a HUNG line; a session of
    the arm that opened the card earlier that day refuses another; after sessions that opened no device, a third try refuses.
14. **The window budget**: step 9 launches only with 7,500 s (the 120-minute cap and 5 minutes) before the last end, so the launch comes by
    G + 1:25 (a reading stricter than the registered last start G + 1:30, never looser); the runner itself keeps every run inside the last end.
15. **The data directories**: one per arm, `docs/reports/data/<day>-e206-matmul-sweep-aifoundry3/` and `...-aifoundry1-c1/`, each with
    `session/`, `data-e206.json`, `reduce-e206.txt`, SHA256SUMS and the README; a session in which no run started is a gate stop's record under
    `docs/reports/gate-stops/<day>-e206-matmul-sweep-T<T0>-<box>/` (E202's form), never scored. Step 2 of an arm refuses on a datum of that
    arm and reports the other's.
16. **The scrub**: the box's home becomes "~" and our own box login "<login>" in every text and .gz file; any /home/ path or the login left
    refuses the collection.
17. **The reducer's readings**: a run's records through the host-records parser with its own command line; counted launches launch >= 0, ok,
    wall_s >= 0.1 s, a pass, the kernel clock in 590-610 MHz; cycles an op the median of the counted launches' cycles_per_op, cycles a GEMM the
    median of cycles_max / passes; p_work the median board W inside the counted launches; p_rest the median of the 5 s before the process;
    die_start the mean of the shires' mean then; die the highest shires' mean in the work window; mhz, mhz_min and **mhz_max** the mean,
    the lowest and the highest minion clock inside the counted launches (mhz_max added before the land for the amended S6, E206.md A1 item 4);
    **the ties' runs go to "ties", never into p001's point runs** (a point's two runs are its pass 1 and pass 2 runs).
18. **The host's records** are read from a source no runtime print can split (item "THE HOST'S RECORDS" of e206_common's docstring); the
    runtime lines are removed pass after pass until none is left (two nested lines included: fixed before the land, the verifier's finding 9).
19. **No post, no release** (waived: the owner's words of Sun 15 Nov 2026, 10:22:36 PST). **The host's package counter is not read.**
20. **Arm B is conditional** (E206.md 6): while `W/out/orch/claim-aifoundry1.txt` exists the queue helper prints QUEUE CANCELLED (exit 4) and
    the card lane returns SKIPPED, books nothing, opens nothing. aifoundry1's identity by continuity is k6's guard's (booted before E82's
    firmware read of 31 Oct 2026); a reboot since would stop step 9 with 16 (IDENTITY-STOP), and arm B then needs the lab's firmware read and
    a dated note first.
21. **The sealed forecasts** (E206.md 0): a sealed sha256 the model session posts for E206's points before an arm's data commit is registered
    in `tools/claims-v3/sealed-e206/e206-freeze-lines.md` before that arm runs; the card lane checks the round's record of them at its step 0.
22. **THE OPERATOR'S STOP FILE** (CARD-LANE-BRIEF 2; fixed before the land, the verifier's finding 1): `touch build/e206/T<T0>-<arm>/STOP` on
    the box is a registered stop: the running host ends at its next launch boundary (it reads the same file), and the runner reads the file
    before every start (each run, each smoke process, every rest read; E202's form), so nothing further starts; the closing follows. A STOP
    file already in the session's folder when the runner starts is a refusal before any device ("refused, no device opened"), and the file is
    kept (the first version removed it at its start and never read it again).
23. **A runtime line naming another card** ("Opening device N", N not the arm's card, on a host's, a config read's or the sampler's stdout) is
    an identity trip: on the start config read the identity gate (no launch), in the smoke the smoke gate, in a run the session's stop (fixed
    before the land, the verifier's finding 10; the first version dropped and counted it). "Opening device 1" on arm B and "Opening device 0"
    on arm A are the arm's own card: dropped and counted, as before.

## 5. Files

| file | what |
|---|---|
| `e206_common.py` | the arms, the build's pins, the tiles, the stop lines and the latch reading, the gates, the order, the argv, the counted launch, the host-records and config parsers; its self-check |
| `e206_ident.py` | the identity reads, the host watch, the board's rise, the sampler's freshness (E190's note 1's module); its self-check |
| `run_e206.py`, `session_e206.sh` | the runner (both arms) and its detached wrapper |
| `ettelem_guard_e206.sh` | the only way the runner reads a card: `config`, `sample --seconds --every-ms` |
| `build_e206.sh` | the box build and its record |
| `check_e206.py`, `harness-e206.json` | every file a box runs or reads, at its sha256 (46); THE KERNEL GATE |
| `preflight_e206.sh` | dmcmd_audit_v2 on the session's files |
| `fake_card_e206.py` | the doubles |
| `reduce_e206.py` | the scorer's data form from a session |
| `collect_e206.py` | COPY-BACK EXACT; the data directory or the gate stop's record, the scrub, the reducer, SHA256SUMS |
| `selftest_run_e206.py` | the runner's desk test, end to end through the frozen scorer |
| `desk/realpath_e206.py`, `desk/realpath_e206.sh` | the real-path desk test |
| `desk/realbytes_e206.py` | the parsers and the identity gate on real committed bytes |
| `desk/desktest_build_e206.sh` | the build's desk test on the real toolchain, with the kernel gate's cases |
| `rb/` | the runbook's steps, its common file, the rest rule, the history check, the dry listing, its desk test |
| `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e206.md` | the card lane's brief; the data README's form |
| `logs/` | every check above |
| `SHA256SUMS-e206-kit` | the kit's files (step 2, `rb/s03_desk_e206.sh`, aside: it pins this list), its logs |

## 6. Device commands

`preflight_e206.sh` (dmcmd_audit_v2, its table v2): **GO (11 send site(s), 0 disallowed; allow-list: none)**, with no allow-list and no exception: `ettelem config` (GET_MODULE_STATIC_TDP_LEVEL,
GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) and `ettelem sample` (GET_MODULE_POWER,
GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES), each through the guard, which refuses
`--reset-ms` and every other word before the device opens; on aifoundry3 the same reader (the reviewed variant 'ettelem'). The host opens the
ops node only. Step 7 on arm A sends k6's config read through E128's guard (the same five READs), on arm B E206's guard's. No set, no reset, no
statistics reset, no firmware query, no residency read, no drain (`dev_mngt_service` is never run), no power cycle. The identity reads send
nothing to a card: et-who stats the nodes, and /proc is read for our own processes only.

## 7. What the desk cannot show

1. **rgm136 has never run on aifoundry3** (the registration: "aifoundry3 has never built rgm136 for its card"): its build's kernel gate there
   (the loadable identity under aifoundry3's toolchain) is shown on this desk's toolchain with aifoundry3's .comment written in (B4), not on
   the box; a refusal there is a safe failure (no session of arm A that day).
2. **The runner has met only its doubles and stand-ins**: the live sampler, the card lock, et-who and the real host meet it first in the
   session. The stop-file path on silicon is E146's (the same host). aifoundry1's host of rgm136 ran in E190 (arm B).
3. **aifoundry1 was not reached** (yielded): arm B's build, reader pin and identity forms rest on E190's, E191's, E198's and E199's records.
4. **The latch reading** (section 4 item 1) rests on committed telemetry; the session's own first samples show the latch it starts from.
5. Card time waits on the queue, the rest, the day, the booking and a readiness lane's go lines (CARD-LANE-BRIEF.md).

## 8. Labels

Every figure quoted from E206.md and its files (the forecasts, the order, the caps, the stops, the gates, the pins) is **registered**. The desk
tests' results are **desk checks of code**, not measurements; the end-to-end joules and the scorer's words come from the doubles (the frozen
forecast's points driven through a toy card): not a measurement and not a reading of E206. The committed reads the kit cites (the latches, the
identity blocks, E190's and E191's outputs) are **desk reads of committed records**; the aifoundry3 reader's sha256 and toolchain string are a
**read-only look** at the box. Nothing here is **blind** or **held out**, and no E206 datum exists. Python: `/usr/bin/python3` 3.12.3.

## 9. Fixed before the land (Q198 lane `fix-e206`, Mon 16 Nov 2026 from 14:43 PST, before any E206 datum)

The adversarial verifier of the registration and this kit (lane `verify-e206`, HOLDS WITH FIXES) found the items below on the bytes of the first
kit commit (`6fc4d1be`, never landed). Each is answered in these bytes with its desk case, and every desk test then ran again on them (the
results table above). Nothing here is measured; nothing was run on a card.

| # | the verifier's finding | the fix | its desk case (result) |
|---|---|---|---|
| 1 (medium) | the operator's STOP file did not stop the session: the runner removed it at its start and never read it again, so run 003 started after STOP was touched during run 002 | `run_e206.stopped()` reads the file before every start (the run loop, `may_start`, every rest read; E202's form); a STOP file already there at the start is a refusal before any device, the file kept (section 4 item 22) | `selftest_run_e206.py` SF (touched during run 002: run 003 never starts, rc 0) and S0 (there before the start: 16, no config read): PASS |
| 2 (medium) | the runbook's desk test read 25 of 27 FAIL once the kit was committed: its stand-in kit came from untracked files only, and (found by the fix lane's own first try, the same 25 of 27, P1 and DA) step 2's `git pull --ff-only` in the scratch then diverged from the lab clone's main, which holds the real kit commit | `rb/selftest_rb_e206.sh`: with the kit commit in the lab clone's history, the scratch repository is built at that commit's parent, the kit's files are taken from HEAD, and the scratch's main follows a local branch at that parent (its pull up to date); otherwise the untracked files and the lab clone's HEAD, as before | run in both states on these bytes: the kit untracked, SELFTEST-RB-E206 27 of 27 PASS (`logs/selftest-rb-e206.txt`); the kit committed, at the local kit commit, run once more after this file was written (its words are in the fix lane's result, not in this file) |
| 3 (minor; an amendment) | the die line's latch reading needed a dated amendment | E206.md amendment A1 item 1 registers it (section 4 item 1); the code is unchanged | G1, D1, D2 and the common self-check's latch cases: PASS |
| 4 (minor) | a second sampler could start beside one that would not stop (the verifier's DEAF2: two processes on the management node at once) | a sampler left running after SIGTERM stops the session: no second sampler, no closing config read while it lives; `queue.json` names it (`samplers_left`) | DF (a double deaf for 110 s, past the runner's two waits of 30 and 60 s): PASS: one sampler ever started, at most 1 process on the stand-in management node at any poll, the session stopped ("the sampler would not stop on SIGTERM ... no second reader"), no closing config read, the double ended by itself after 110.1 s (nothing killed it) |
| 5 (minor; the registration) | R0 missed the tie runs' checks and those of runs with no counted launch | `score_e206.py` R0 reads every check of C of the day (E206.md A1 item 3) | stand-in cases J and K (R0 FAIL, as stated): PASS; the verifier's scorer attacks 11 of 11 as stated |
| 6 (minor; the registration) | S6 read the mean as the maximum | `mhz_max` in the run form (`reduce_e206.py` writes it) and S6 reads it (E206.md A1 item 4) | stand-in case L (S6 FAIL at a 700 MHz sample under a 609 MHz mean): PASS; E2-A and E2-B through the reducer and the frozen scorer: PASS |
| 7 (minor) | a sample with no board reading restarted the board line's count | such a sample neither counts nor breaks the row (section 4 item 2; E206.md A1 item 2) | BN (95 W on every other sample trips at the third reading, both arms) and the common self-check's three board cases: PASS |
| 8 (minor; the brief) | some waits inside the onelab spans had no bound (step 0's load wait, step 2's retry, step 11's other exits) | CARD-LANE-BRIEF.md 2: the load rule before `desk`; step 2 and step 11 leave their span before any wait, each retry bounded; every exit of step 11 mapped | a desk read of the brief |
| 9 (nit) | `drop_runtime` made one pass, so of two nested runtime lines one was left in the record | it removes runtime lines until none is left | REALBYTES RB-NEST: PASS: 2,940 splices into real card-1 records, every one read the same records; the common self-check's nested cases: PASS |
| 10 (nit) | a runtime line naming another card was only counted | an identity trip on a host's, a config read's or the sampler's stdout (section 4 item 23) | RT (arm B's smoke: 16; arm A, its own card: rc 0), RT2 (arm B's first run: STOP, rc 0), RTC (arm B's config read: the gate, 16): PASS |
| 11 (note; the registration) | the one-shire points sit 0.2-0.8 W over idle | E206.md section 8 says so (A1 item 5) | - |
| 12 (gap) | aifoundry1's folders not searched; arm B cancelled | none while arm B stays cancelled (`claim-aifoundry1.txt`: QUEUE CANCELLED, the card lane returns SKIPPED); each card lane re-runs the never-run search before its data commit (CARD-LANE-BRIEF 2, step 12) | - |

**The pins moved with the registration:** step 2's `REGPIN` (25 entries, `d9fb06e4...`), `rb/rb_e206.sh`'s `E206_REG_SUBTREE` and
`rb/check_history_e206.py`'s `REG_SUBTREE` (`114c094b...`); step 2's `KITPIN` (the kit's list, re-made last); `harness-e206.json` re-made (46
files). **Unchanged:** every forecast, band, point, order, plan figure and stop number; the kernel pins and the readers' pins; the kit's file
list (46 files); dmcmd_audit_v2 GO (11 send sites, every one a READ).

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), one job at a time, each that runs a built host, the runner or a stand-in
inside the sandbox (W/nodev.sh; the real-path test in private UTS and PID namespaces): the runner's desk test (about 11 minutes), the
real-path test (two real builds), the build's test (two real builds), the runbook's test (two real builds), the real-bytes test, the dry
listings. On aifoundry3: one read-only look (seconds). No simulator run. The fix lane ran the whole suite once more on its bytes (15:11:55-15:28:56 PST, about 17 minutes),
and the runbook's test once more with the kit committed; it reached no box.

SPDX-License-Identifier: Apache-2.0
