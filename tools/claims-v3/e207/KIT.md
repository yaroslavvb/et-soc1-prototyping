# E207's run kit: the blind matmul day on aifoundry3 card 0 from aifoundry2, in E206's kit form (its arm A, which ran FULL on this card): one runner with one sampler and the stop lines live, the identity gate, read and watch, the smoke (b01, b02, b03 against MM1-v1's counter-mean forecast) and then the stop-path test, 109 runs each under a plain `timeout 10` and never killed; rgm136 built on the box through the kernel gate; the host's records read past any runtime line; the never-run search repeated right before the first card command; step 7 only once the rest has opened; the reducer to the frozen scorer's form (Q199; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q199, lane `kit-e207`). No card was claimed or opened: aifoundry2 has a card, so
every desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox (no
/dev/et*, an empty /run/lock). No device command was sent, nothing was posted, no simulator was run. One box was reached: aifoundry3, three
times, read-only, each while no lane booked it (Mon 16 Nov 2026 22:19:25 PST: the reader's sha256 (the pin, unchanged), its riscv gcc's version
string, python3's, the card lock's presence, the build folder's names, E206 arm A's session end; 22:41:31 PST: how many files the never-run
step's roots hold there; 22:58:55-22:59:00 PST: step 6n run for real from a scratch RB_OUT, E206's scanner on stdin over its run folders at nice
19; nothing written there, no device opened). aifoundry1 was not reached. New files only, all under `tools/claims-v3/e207/`.
The registration [`E207.md`](E207.md) (found by content: the commit that added it, its `tools/claims-v3/e207` subtree `d2089226...` with
amendment A1, fix-e207's (before it `ac8854b4...`); `SHA256SUMS-e207-registration` `b97becf2...`, 24 entries) and every file its list names stay as committed. **No E207 datum exists. Nothing here
changes a forecast, a band, a rule, a threshold, the order, the card time, the cap, a stop or the scorer.** Where E207.md leaves a reading to the
kit, the reading is stated in section 4 before any datum.*

*Fixed by Q199's lane `fix-e207`, Tue 17 Nov 2026, before any E207 datum, beside the registration's amendment A1 (section 9): step 6n counts
only card runs, never reads the model session's folders and dates what it counts against MM1-v1's freeze; step 13 runs the after-score tool;
the runbook test's same-day case holds at every hour; the brief's open paths are stated. The results below are the fixed kit's, re-run.*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

## Results first (desk checks of code and desk reads of committed records; nothing is measured)

| check | result | log |
|---|---|---|
| **the runner on the doubles** (`selftest_run_e207.py`): the short path with the identity gate and read, the smoke (b01, b02, b03, each read against MM1-v1's counter-mean forecast) and THEN the stop-path test, the 87 C latch tripping nothing; every config gate (TDP, card 1's block, no block, a failed read, a read HUNG past its TERM, card 0's runtime line); every holder (another login on card 0 and on card 1, et-who unreadable, a device process of ours, a CI job, the lock held); the sampler dead, on card 1, silent, dying, deaf past both SIGTERM waits; the stop-path test with no live sample; the smoke (a wrong check, a crash, a host on card 1, no rise, card 0's runtime line inside a record, records of another mask, the counter's mean at 3 x MM1-v1's); K1; **a host hung past its TERM (HUNG, exit 8, no closing read, NOTHING KILLED: the double ended by itself)**; a host ended by TERM (rc 124); two failures in a row; a run whose records name another mask (never read as data; the FROZEN scorer sets it aside, the point NO DATA); the board, the mean and the latch lines; 70.0 W not above 70; the die gate; the card-time rule; an operator's SIGTERM; the operator's STOP file touched mid-session and there before the start; a crash; card 1's runtime line on a smoke host, a run's host and the config read (identity trips); **THE ORDER**: the whole registered sequence (109 runs), every key and argv the registered and every host record read as its command's; the refusals without `--dry`, `--arm B`, and the REAL runner stopping at its box check; **END TO END** twice through the reducer and the FROZEN scorer | **SELFTEST-RUN-E207 50 of 50 PASS**; OR: PASS: rc 0; 109 runs of 109, every key and argv the registered, 1635 host records read as their commands' (0 differ); 59 s; E2-A: PASS: session rc 0, reduce rc 0, score rc 0; 24 point runs; t_gemm worst 1.00e-06; J over idle against the injected watts x seconds worst 0.51% (24 runs of 3 W or more); rules {"E1": "PASS", "E2": "PASS", "E3": "PASS", ...; E2-W: PASS: session rc 0, reduce rc 0, score rc 0; 24 point runs; t_gemm worst 1.00e-06; J over idle against the injected watts x seconds worst 0.32% (24 runs of 3 W or more); rules {"E1": "FAIL", "E2": "FAIL", "E3": "FAIL", ...; HG: PASS: rc 8; the run's process hung [True]; the hung double: 'the hung double ended by itself after 14.0 s (pid 1234142); nothing killed it' (19 s after the session began); DF: PASS: rc 0; most processes on the stand-in management node at once 1; samplers started 1; left [1239831]; the stop 'the sampler would not stop on SIGTERM (pid(s) [1239831], left running, never killed): no second read'; the ...; SA: PASS: rc 0; n06's run: t_gemm None, the host's record {'arm': 'gemmL2x3x16', 'minions': 1024, 'shire_mask': '0x1fffffffe', 'type': 'int8'}; the scorer set it aside [{'n': 2, 'mismatch': {'shire_mask': ['0x1fffffffe', ... | [`logs/selftest-run-e207.txt`](logs/selftest-run-e207.txt) |
| **the REAL path** (`desk/realpath_e207.py`, `desk/realpath_e207.sh`): run_e207.py WITHOUT --dry under aifoundry3's hostname (a private UTS namespace) and a private PID namespace, stand-ins for the reader behind the REAL guard, et-who, the host, the lock and the nodes, the REAL kernel ELF from the REAL build_e207.sh: the box check (the kernel gate, the harness with MM1-v1's frozen file, the preflight), the lock, et-who and ps, the identity gate and read, the smoke, the stop-path test, the tie and two points; a host hung past its TERM under the real `timeout 10` (left, ending by itself); the lock held; a device process of ours; the reader off its pin; a changed .text; ET_DEVICES three ways; another login on card 0; the other card three ways (config, sampler, host); card 1's and card 0's runtime lines; a sampler death; a build record without its builder; the operator's STOP file | **REALPATH-E207 14 of 14 PASS** | [`logs/realpath-e207.txt`](logs/realpath-e207.txt) |
| **the parsers on real committed bytes** (`desk/realbytes_e207.py`): E206 arm A's 244 committed stdouts from THIS card (the same host and binary) read as a plain reader reads them; **E206 arm A's committed session through E207's reducer gives E206's committed data-e206.json field for field (241 runs, the smoke, the queue)**; E190's 174 committed rgm136 stdouts on both cards (87 carrying aifoundry1's runtime line) and its 12 card-1 bursts against its committed reduction; runtime lines of card 0 and card 1, single and nested, at every byte offset of real aifoundry3 records (a subset run's and the tie's); 1a4bc1e3's and 7156ac15's split stdouts against their committed readings; E206's committed config line with runtime lines at every offset; the identity gate both ways on 12 committed config forms | **REALBYTES-E207 9 of 9 PASS** | [`logs/realbytes-e207.txt`](logs/realbytes-e207.txt) |
| **the build on this desk's real toolchain** (`desk/desktest_build_e207.sh`; riscv gcc "() 15.1.0", g++ 13.3.0, cmake 3.28.3): aifoundry3's build, the kernel gate's cases (aifoundry3's .comment form, a .rodata byte, a .text byte), a changed source, aifoundry1 and aifoundry2 refused, the runner's box check, the guard on other boxes and with ET_DEVICES and the statistics reset | **DESKTEST-BUILD-E207 8 of 8 PASS** | [`logs/desktest-build-e207.txt`](logs/desktest-build-e207.txt) |
| **the runbook** (`rb/selftest_rb_e207.sh`: a fake ssh and rsync, a stand-in aifoundry3, the real build): the window rule (another arm, another runbook, another day, the arm B), the lab-git lock, step 2 at every pin (the registration's, the kit's, MM1-v1's), the history check and a shadow, E207's data refusing step 2 and a gate stop's record reported, the look, ours_live, the sync, a login link, a hang, NO-THIRD-BUILD, the real build, **step 6n on stand-in roots (fix-e207: a point in a data directory dated before the freeze RAN BEFORE, one in a box folder with no date TO DATE, one in a card lane's session after the freeze AFTER THE FREEZE (kept), another experiment's desk double DESK-ONLY (dismissed), the model session's folder never read, E207's own desk and dry records subtracted, the --desk-only form)**, **step 7 refusing with no config read sent without a fresh 6n report and until the rest has opened**, the dry pass, the HUNG marker, the same-day rule, **the last start**, **step 9 without today's 6n report**, the REAL session stopping at its box check, step 10's readings (running, gone, HUNG, K1, CRASH, a STOP line), the copy-back, the gate stop's record, a copy not exact, a session that ran through step 12's data directory (6n's report and its dating in it) and step 13's FROZEN scorer and the after-score tool (its labels from 6n's dating) | **SELFTEST-RB-E207 28 of 28 PASS** | [`logs/selftest-rb-e207.txt`](logs/selftest-rb-e207.txt) |
| **fix-e207's checks** (section 9): step 6n's fixed code on stand-in roots (every place class and dating rule, both forms); its desk half for real on the real roots (aifoundry3 not read); the kit's FIRST step-6n code on the same lab and lane folders (the model session's folders left out); `postscore_e207.py --selftest` (the registration's, A1 item 3) | the stand-in words both AS EXPECTED; real: **NEVER-RUN 53 of 53 points, 47 of 47 cases; DESK-ONLY (dismissed): b04 b15 b25**; the first code: NEVER-RUN 50 of 53 points, 44 of 47 cases; RAN BEFORE: b04 b15 b25 (finding 1, live); **selftest-postscore: PASS (31 of 31 checks as stated)** | the lane's record (OUT/fix-e207); [`selftest-postscore.txt`](selftest-postscore.txt) |
| the dry listing, every step with stand-ins | **dry listing: 15 steps listed, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e207.txt`](logs/dry-listing-e207.txt) |
| `dmcmd_audit_v2` on the session's files (`preflight_e207.sh`: the runner, its two modules, the wrapper, the build, the harness check, the guard, the host's source) | **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)**, every one a READ, no allow-list, no exception | [`logs/dmcmd-audit-e207.txt`](logs/dmcmd-audit-e207.txt) |
| the quick set | 15 lines PASS / OK / GO / yes (the two modules' self-checks, the harness re-made and at its sha256, the registration's four checks, the scorer's --forecasts and two self-tests and (fix-e207) the after-score tool's self-test each byte-identical to the committed, the registration's list (24) and MM1-v1's folder list, the preflight); bash -n of every shell file of the kit: 22 files, 0 with a syntax error; python3 compile of every Python file of the kit and the after-score tool (in memory, no __pycache__ written): 19 files, 0 that do not parse; calls that could send a kill in the kit's own code (subprocess .kill(), os.kill, signal.SIGKILL, 'kill -9', 'timeout -k' outside prose): 0 (the lines naming one are prose, listed) | [`logs/checks-e207.txt`](logs/checks-e207.txt) |

## 1. The kit, in E206's form

- **The runner** ([`run_e207.py`](run_e207.py), [`session_e207.sh`](session_e207.sh), [`e207_common.py`](e207_common.py),
  [`e207_ident.py`](e207_ident.py)): E206's runner for its arm A (`tools/claims-v3/e206/run_e206.py`, landed in `906699ea`, which ran E206 arm A
  FULL on this card: 241 of 241 runs, data `d7e4f35e`), every behaviour unchanged but the plan and the order (109 runs: t01, pass 1, t01, pass 2,
  t01), the smoke's points and their check against MM1-v1's counter-mean forecast, the card-time rule (60 / 70), one arm (arm B's paths removed)
  and the files' names. Before anything opens: the host name is aifoundry3, the device environment carries no ET_DEVICES (the runner drops an
  inherited one), build/e207rgm's record today's BUILT by build_e207.sh on this box, the kernel through THE KERNEL GATE again, the host at the
  sha256 the build recorded, the reader at its pin (`16037641...`, read again on the box at 22:19 PST), the 10 tiles at their manifests' sha256,
  the harness (HARNESS OK: 37 files, MM1-v1's frozen blind-day file among them) and the preflight (dmcmd_audit_v2 GO). Then the card's lock
  (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD COMMAND `ettelem config` through
  [`ettelem_guard_e207.sh`](ettelem_guard_e207.sh) under a plain `timeout 10` with its stderr kept (the start config and THE IDENTITY GATE; the
  card time counts from it), ONE sampler (10 Hz) whose every line feeds THE STOP LINES as it arrives, THE IDENTITY READ, the smoke and then the
  stop-path test, the registered sequence, the closing config, "session end", MANIFEST.sha256 last. Nothing is set. Every start (each run, each
  smoke process, every rest read) first reads the operator's STOP file; never two samplers at once.
- **No SIGKILL anywhere** (W/out/orch/kill-rule.txt; AGENT.md "never kill -9"): every device process is under a plain `timeout 10`; the runner
  waits for it with a bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the stop
  file, starts nothing further, sends no further card command (no closing config read), closes the session and LEAVES the process (exit 8).
  et-who, the harness check and the preflight are waited on with a bound and left past it (a failed read, never a kill). The sampler is stopped
  by SIGTERM only. The build runs under a plain `timeout`. The one kill in the whole path is k6's bounded runner's (rb_run.py, unchanged, every
  kit's): past a call's bound it ends THE DESK'S OWN ssh client, rsync or collector; never a process on a box, where nothing of E207's sends any
  signal to a device process. (The quick set lists every line of the kit naming a kill: each is prose.)
- **The build** ([`build_e207.sh`](build_e207.sh), [`check_e207.py`](check_e207.py)): E136's rgm136 unchanged, into **build/e207rgm** (a new
  folder of ours) on aifoundry3; the kernel through THE KERNEL GATE (the .text always the registered `61315bf6...`, and the whole ELF the
  registered `aace138c...` or its loadable identity the pinned `649d4079...`, E206's pin, which E206 arm A's build on this box met on Mon 16 Nov
  2026); the host by its behaviour (four refusals main.cpp makes before its device Session); the ET_DEVICES reading recorded, never a gate (one
  card); build/e207rgm/BUILD-e207.json. Any box but aifoundry3 is refused before anything is built.
- **The doubles** ([`fake_card_e207.py`](fake_card_e207.py)): config (aifoundry3's committed start config and its identity block), et-who (who
  holds the stand-in nodes and lock, from /proc), a toy card's sampler driven by the launches the host double announces (its latch at the
  committed 87 C), and the host (rgm136's SPARSITY records on a virtual clock at each point's MM1-v1 seconds, its counter's mean at MM1-v1's
  counter-mean forecast and its watts at MM1-v1's W over idle; the tie at E206 arm A's measured p001; modes for every failure the tests need,
  among them a host that IGNORES its TERM).
- **The reducer** ([`reduce_e207.py`](reduce_e207.py)): the session into the frozen scorer's data form (`{"experiment": "E207", "arms": {"A":
  ARM}}`, score_e207.py's docstring) and a table; E206's reducer line for line (its committed reduction of E206 arm A comes back field for
  field). **The collection** ([`collect_e207.py`](collect_e207.py)): COPY-BACK EXACT, the data directory (or a gate stop's record), the scrub,
  the reducer, SHA256SUMS. **The harness** ([`check_e207.py`](check_e207.py), `harness-e207.json`, 37 files) and **the preflight**
  ([`preflight_e207.sh`](preflight_e207.sh)).
- **The never-run search, repeated** ([`desk/neverrun_card_e207.py`](desk/neverrun_card_e207.py), [`rb/s06n_neverrun_e207.sh`](rb/s06n_neverrun_e207.sh)):
  E207.md section 4's repeat right before the first card command (section 4 item 17 below).
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged (the arm A the first word of every box step; one RB_OUT):
  the window; step 2 (the pull under the lab-git lock, the three lists pinned by count and bytes, the history check, the harness, the
  registration's checks and the scorer's forecasts and self-tests byte-identical, the preflight, the desk tests' logs; outside the kit's list);
  the look (k6's); the sync; the build; **step 6n, the never-run search**; **step 7, only once the rest has opened and within 30 minutes of 6n**;
  the dry pass; the session; the wait; the copy-back; the data directory; the scorer after the data commit. **No post and no release**
  (waived). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lane's brief, with THE ONE-LAB RULE and THE QUIET HOLD in its step table;
  [`DATA-README-FORM-e207.md`](DATA-README-FORM-e207.md) is the data README's form.

## 2. Card-minutes and the cap (registered; unchanged)

40.6 card-minutes planned (the smoke and 109 runs at E206 arm A's measured 21.96 s a run on this card; plan-e207.txt); no run starts once the
card time passes 60 minutes; at 70 the session ends after the run in progress; a started run is cut only by a stop. The registered subset if
cut: the smoke, tie 1, pass 1 and tie 2 (runs 1-55: every point once, about 20.8 card-minutes).

## 3. The order on the box

The card lane's full table, with the booking, THE ONE-LAB RULE (desk / undesk around steps 0-2, collect / uncollect around step 11 to the data
commit's push), THE QUIET HOLD and the end of every path, is [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps:

| step | file | what |
|---|---|---|
| 1 | `rb/s02_window_e207.sh A <day> <last start> <last end>` | first; today only; the window (G = the booking) in its own RB_OUT |
| 2 | `rb/s03_desk_e207.sh A` (outside the kit's list) | the window; the pull under the lab-git lock; the registration and the kit found by content, ancestors of HEAD; the paths clean; HISTORY OK; the registration's list, the kit's list and MM1-v1's folder list at their pins; the harness; both self-checks; the registration's checks; the scorer's --forecasts and two self-tests byte-identical to their committed outputs; the preflight; the desk tests' logs; no E207 datum in any ref |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | k6's, unchanged (et-who, who, uptime, the holder rule); our login recorded for the scrub |
| 5 | `rb/s07_sync_e207.sh A` | the rsync into `~/aifoundry`; HARNESS OK on the box |
| 6 | `rb/s08_build_e207.sh A start`, then `wait` | the detached build, NO-THIRD-BUILD, the record (KERNEL OK), the harness, the preflight and both self-checks on the box |
| 6n | `E207_ROUND_OUT=<OUT> rb/s06n_neverrun_e207.sh A [--desk-only]` | THE NEVER-RUN SEARCH REPEATED: E206's scanner over the lab at HEAD, the round's lane folders and HOME/claude/work at the desk and over aifoundry3's run folders (a bounded read), E207's own folders subtracted; the registration's matching from a copy; RB_OUT/e207-neverrun.txt (REPORTED) |
| 7 | `rb/s09_reads_e207.sh A` | 6n's report under 30 minutes old, then THE REST RULE on the box, no card command (10 while either fails); then k6's step 7 unchanged (TDP 0 W / 65 C / 600 MHz, et-who clean) |
| 8 | `rb/s10_dry_e207.sh A start`, then `wait` | the runner on the box with its doubles, no device |
| 9 | `rb/s11_session_e207.sh A` | the last start (k6's), the cap before the last end, today's 6n report, k6's guard, THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e207.sh` detached |
| 10 | `rb/s20_wait_e207.sh A` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e207.sh A` | one read-only copy back, COPY-BACK EXACT |
| 12 | `rb/s23_data_e207.sh A` | the data directory `docs/reports/data/<day>-e207-blind-matmul-aifoundry3/` (or a gate stop's record under `docs/reports/gate-stops/`), the scrub, the reducer, step 6n's report, SHA256SUMS, the desk-path gate, the history check; then the card lane's README (and a dated note if a point ran before) and data commit |
| 13 | `rb/s24_score_e207.sh A` | after the data commit only: score_e207.py (registered, unchanged) on the committed data-e207.json |

## 4. The readings stated here before any datum (where E207.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH** (E206.md amendment A1 item 1, which E207.md 6 and plan-e207.json adopt in words): the
   line trips on the shires' mean (`minshire[0]`) at or above 70 C, or on the latch (`minshire[2]`) only when it has risen during the session
   above the lowest value it read since the session's first sample and reads at or above 70 C. On aifoundry3 card 0 the latch read 87 C in
   every committed sample of E189, E195, E196, E197 and E206 arm A. `e207_common.Stops`, E206's line for line; desk cases G1, D1, D2 and the
   self-check's latch cases.
2. **The other stop lines** (E207.md 6): the board strictly above 70 W on 3 samples in a row that carry a board reading (a sample with none
   neither counts nor breaks the row: E206.md A1 item 2, adopted). A trip touches the host's `--stop-file` at once: the running host ends its
   loop at its next launch boundary (about 0.5 s; this host's own path, proven on silicon by E146), never killed; nothing further starts; the
   run's 4 s read and the closing follow.
3. **The smoke, then the stop-path test** (plan-e207.json "smoke"): 30 s at rest (the rest die: the median of the shires' mean over it; the die
   gate is formed from it), then one process each of b01, b02 and b03 with `--seconds 2 --budget 3.5` (the budget is E146's, E190's and E206's
   smoke's), not die-gated; each must exit 0 with every launch ok, its check of C exact or approx, its cycles an op (the CHECK record's
   `cycles_per_op`: the counter's mean, as E190's and E206's smoke read it and as reduce_e207.py hands it to the scorer's R0) within 50-250% of
   MM1-v1's counter-mean forecast (784.2 cycles an op at all three; MM1-v1's frozen CSV, read through its pin), the board at least 2 W over the
   rest during its launches (at least 3 samples), and the host on card 0 (the watch); THEN the stop-path test on live samples (test thresholds
   every sample crosses: 0 W on 3 samples, 0 C; each test line touching its own file, never the host's stop file, and refusing a start; no
   launch). Any failure: the smoke gate failed, no run (a gate stop).
4. **The start config** (plan-e207.json): TDP 0 W / 65 C / 600 MHz, read as found, nothing set; read again at the end (never after a HUNG,
   nor while the sampler would not stop).
5. **The identity**: `/dev/et0_mgmt`, physical device ID 0 on the config read's stderr (E189's and E206 arm A's committed aifoundry3 reads
   print exactly that block); no minion_mv bound (a one-card box). The identity read with the sampler running; the host watch at every
   process; a host naming or holding another card stops the session at once (in the smoke: the smoke gate). The box itself is told by its
   hostname (the box check, the guard and the build refuse every box but aifoundry3), since another box's card 0 prints the same block.
6. **The holders** (E206 arm A's): any holder line of another login (on any node: aifoundry3 has one card), another user's device process, a
   CI job, any other device process of ours. **An unreadable et-who is a holder** (E202's fix). Counts only.
7. **The die gate**: min(60, rest die + 4) C, on a live sample (under 2 s old) only, waiting at most 300 s and never past the card-time rule or
   a stop; else that run is NO DATA.
8. **A run**: the die gate, the holders again (et-who and ps), 10 s at rest (p_rest = the median board W of its last 5 s), ONE host process
   `timeout 10 sparsity_host <the point's or the tie's registered host_args> --kernel <ELF> --stop-file <STOP>`, a 4 s read. A live sampler
   before the process, else the run ends there flagged and the sampler is restarted (SIGTERM to a stale one); a stale sampler that will not stop
   on SIGTERM is left running, never killed, and the session stops: no second reader of the management node is started, and the closing config
   read is not sent while it lives.
9. **Failures.** A failed process (rc not 0, `timeout 10`'s 124 among them) is flagged; **two failed processes in a row stop the session**
   (E190's E64 rule, for one-process runs). **K1**: a host whose stderr says "kernel did not finish" stops the session at once. **HUNG** (item 1
   of section 1): exit 8. A crash of the runner is named and exits 1, its closing run.
10. **Card time** counts from the start config read (the session's own first card command; step 7's read is reported apart). A run starts only
    if the card time is under 60 minutes and its longest length (28 s once its gate has passed) fits the 70-minute cap less 60 s of closing and
    ends 90 s before the window's last end.
11. **The reader**: aifoundry3's `build/ettelem/ettelem` (`16037641...`, read there on Mon 16 Nov 2026 at 12:02 PST by E206's kit and at 22:19
    PST by this kit), through one guard, `config` and `sample` only, ET_DEVICES unset, any other box refused.
12. **THE REST RULE** (E207.md 6): the first card command at least 40 minutes after our previous session on aifoundry3 ended. E206's rule (every
    session-log form of ours, the activity floor, the model session's folders `~/claude/work/ee-*/`), its floor now leaving out E207's own
    folders, so E206 arm A's folders count (its session ended 18:22:16 PST Mon 16 Nov 2026: E207's rest opened 19:02:16 PST). Steps 7 and 9
    read it on the box, step 7 BEFORE its config read (no card command while the rest has not run).
13. **THE HUNG MARKER and THE SAME-DAY RULE** (E202's): step 9 refuses while any session log of ours on the box holds a HUNG line; an E207
    session that opened the card earlier that day refuses another; after sessions that opened no device, a third try refuses.
14. **The window**: step 9 launches only before the registered last start G + 1:30 (k6's `rb_need_start`) and with 4,500 s (the 70-minute cap
    and 5 minutes) before the last end (G + 3:30); the last start binds (E206's 120-minute cap had made its budget the binding rule); the runner
    itself keeps every run inside the last end.
15. **The data directory**: `docs/reports/data/<day>-e207-blind-matmul-aifoundry3/` with `session/`, `data-e207.json`, `reduce-e207.txt`,
    step 6n's report (`neverrun-e207-card.txt`, `neverrun-e207-card.json`, and since fix-e207 its dating `ranbefore-e207-card.json`, copied in by
    collect_e207.py's `--neverrun` and listed in SHA256SUMS),
    SHA256SUMS and the README; a session in which no run started is a gate stop's record under
    `docs/reports/gate-stops/<day>-e207-blind-matmul-T<T0>-aifoundry3/` (E202's form), never scored. Step 2 refuses on any E207 datum.
16. **The scrub**: the box's home becomes "~" and our own box login "<login>" in every text and .gz file; any /home/ path or the login left
    refuses the collection.
17. **THE NEVER-RUN SEARCH, REPEATED** (E207.md section 4: "the card lane repeats this search right before its first card command (... any new
    E208 session included); a point found run then stays in E207 but is labelled 'ran before' and leaves every head-to-head and every rule (a
    dated note before the data commit)"): step 6n runs E206's scanner, unchanged (`95b290c0...`), over the registered roots and more: at the desk
    the lab clone at HEAD, the round's lane folders (named by `E207_ROUND_OUT`, so no private path is written in the kit) and HOME/claude/work;
    on aifoundry3 HOME/aifoundry/build, HOME/claude/work and HOME/claude/et-soc1-prototyping/build (a superset of the registered aifoundry3
    roots). **E207's own folders are subtracted by the scanner's own counts** (each scanned apart, its counts taken away key by key and card by
    card): on aifoundry3 `build/e207/` (E207's dry passes print the doubles' records of E207's own points; an E207 session's runs are E207's,
    never "before" it) and in the lane folders every top-level folder named `<role>-e207[<suffix>]` (reg-, kit-, verify-, fix-, land-, ready-,
    card-e207 and any second lane of theirs: their desk tests' doubles print every E207 point by the thousand, and none of them has card time
    before the session). Step 9 refuses without a 6n report from that day. The registration's matching (`desk/neverrun_e207.py`,
    unchanged) runs from a copy beside a copy of `points-e207.json`, both checked against `SHA256SUMS-e207-registration`, since it writes its
    report beside itself and the committed report must never be overwritten. E208's planned arms are read at whatever bytes the file has
    (its sha256 reported). Step 7 refuses unless 6n ended within the last 30 minutes ("right before"). The result is REPORTED, never a gate: a
    point that ran before goes into the card lane's dated note before the data commit; the frozen scorer is never changed. NOT SEARCHED, as
    registered: aifoundry1's own folders. **As fixed by fix-e207 (section 9; E207.md A1 items 1-3): what is counted, what is dismissed, the model
    session's folders not read, and the dating against MM1-v1's freeze.**
18. **The host's records** are read from a source no runtime print can split (e207_common's docstring); the runtime lines are removed pass after
    pass until none is left; **a runtime line naming another card than card 0** (on a host's, a config read's or the sampler's stdout) is an
    identity trip: on the start config read the identity gate, in the smoke the smoke gate, in a run the session's stop; card 0's own line is
    dropped and counted (aifoundry3's runtime printed none in E206 arm A's 244 committed stdouts).
19. **No post, no release** (waived: the owner's words of Sun 15 Nov 2026, 10:22:36 PST). **The host's package counter is not read.**
20. **The sealed forecasts** (E207.md 0): a sealed sha256 the model session posts for E207's points before the data commit is registered in
    `tools/claims-v3/sealed-e207/e207-freeze-lines.md` before the card day; the card lane checks the round's record of them at its step 0.
21. **THE OPERATOR'S STOP FILE** (CARD-LANE-BRIEF 2): `touch build/e207/T<T0>-A/STOP` on the box is a registered stop: the running host ends at
    its next launch boundary (it reads the same file), and the runner reads the file before every start, so nothing further starts; the closing
    follows. A STOP file already in the session's folder when the runner starts is a refusal before any device, and the file is kept.
22. **The reducer's readings** (E207.md 7, the scorer's docstring): counted launches launch >= 0, ok, wall_s >= 0.1 s, a pass, the kernel clock
    in 590-610 MHz; t_gemm = sum of wall / sum of passes; cycles a GEMM the median of cycles_max / passes (the scorer's wall: cycles_gemm / ops a
    minion a GEMM); cycles an op the median of the host's cycles_per_op (the scorer's counter's mean); p_work the median board W inside the counted
    launches; p_rest the median of the 5 s before the process; die_start the mean of the shires' mean then; die the highest shires' mean in the
    work window; mhz, mhz_min and mhz_max the mean, the lowest and the highest minion clock inside the counted launches; the tie's runs go to
    "ties", never into a point's runs.

## 5. Files

| file | what |
|---|---|
| `e207_common.py` | the arm, the build's pins, the tiles, MM1-v1's frozen file, the stop lines and the latch reading, the gate, the order, the argv, the counted launch, the host-records and config parsers; its self-check |
| `e207_ident.py` | the identity reads, the host watch, the board's rise, the sampler's freshness (E206's module, the arm's table only changed); its self-check |
| `run_e207.py`, `session_e207.sh` | the runner and its detached wrapper |
| `ettelem_guard_e207.sh` | the only way the runner reads a card: `config`, `sample --seconds --every-ms` |
| `build_e207.sh` | the box build and its record |
| `check_e207.py`, `harness-e207.json` | every file the box runs or reads, at its sha256 (37); THE KERNEL GATE |
| `preflight_e207.sh` | dmcmd_audit_v2 on the session's files |
| `fake_card_e207.py` | the doubles |
| `reduce_e207.py` | the scorer's data form from a session |
| `collect_e207.py` | COPY-BACK EXACT; the data directory or the gate stop's record, the scrub, the reducer, SHA256SUMS |
| `selftest_run_e207.py` | the runner's desk test, end to end through the frozen scorer |
| `desk/realpath_e207.py`, `desk/realpath_e207.sh` | the real-path desk test |
| `desk/realbytes_e207.py` | the parsers, the reducer and the identity gate on real committed bytes |
| `desk/desktest_build_e207.sh` | the build's desk test on the real toolchain, with the kernel gate's cases |
| `desk/neverrun_card_e207.py` | the never-run search repeated (step 6n's desk half and its report) |
| `rb/` | the runbook's steps (step 6n among them), its common file, the rest rule, the history check, the dry listing, its desk test |
| `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e207.md` | the card lane's brief; the data README's form |
| `logs/` | every check above |
| `SHA256SUMS-e207-kit` | the kit's files (step 2, `rb/s03_desk_e207.sh`, aside: it pins this list), its logs |

## 6. Device commands

`preflight_e207.sh` (dmcmd_audit_v2, its table v2): **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)**, with no allow-list and no exception: `ettelem config`
(GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) and `ettelem
sample` (GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES), each through
the guard, which refuses `--reset-ms` and every other word before the device opens. The host opens the ops node only. Step 7 sends k6's config
read through E128's guard (the same five READs). No set, no reset, no statistics reset, no firmware query, no residency read, no drain
(`dev_mngt_service` is never run), no power cycle. The identity reads send nothing to a card: et-who stats the nodes, and /proc is read for our
own processes only. Step 6n sends nothing to a card (file reads only).

## 7. What the desk cannot show

1. **The runner has met only its doubles and stand-ins**: the live sampler, the card lock, et-who and the real host meet it first in the
   session. But its code is E206's, which met all of them on this card (E206 arm A, 241 of 241 runs), and E207's changes are the plan, the
   order, the smoke's forecast file, the card-time numbers and the removal of arm B.
2. **The build on aifoundry3** is shown on this desk's toolchain with aifoundry3's .comment written in (B4); E206 arm A's build there met the
   same gate on Mon 16 Nov 2026 (the loadable identity `649d4079...`).
3. **Step 6n** is shown on a stand-in box by the runbook's test and was also run once for real at the desk from a scratch RB_OUT (Mon 16 Nov
   2026 22:58:15-22:59:00 PST, aifoundry3 unbooked): `NEVER-RUN 53 of 53 points, 47 of 47 cases` (the desk's scans 39.8 s; aifoundry3's run
   folders 39,414 files in 4.6 s, inside the wait class's 600 s bound; the round's lane folders 658 GEMM configurations raw and 554 once
   kit-e207's own desk tests' 106 were subtracted, the registered search's own count; E208's arms at the registered sha256): a desk read,
   REPORTED, not the card lane's repeat, which comes right before the card day's first card command. Its fixed code's desk half was run for
   real again on Tue 17 Nov 2026 at 01:03-01:04 PST (aifoundry3 not read): section 9.
4. Card time waits on the queue, the rest, the day, the booking and a readiness lane's go lines (CARD-LANE-BRIEF.md).

## 8. Labels

Every figure quoted from E207.md and its files (the forecasts, the order, the caps, the stops, the gates, the pins) is **registered**. The desk
tests' results are **desk checks of code**, not measurements; the end-to-end joules and the scorer's words come from the doubles (MM1-v1's frozen
forecasts driven through a toy card): not a measurement and not a reading of E207. The committed reads the kit cites (the latches, the identity
blocks, E190's, E191's and E206's outputs) are **desk reads of committed records**; the aifoundry3 reader's sha256, toolchain string and file
counts are **read-only looks** at the box. Nothing here is **blind** or **held out**, and no E207 datum exists. Python: `/usr/bin/python3`
3.12.3.

## 9. fix-e207: verify-e207's kit findings answered (Q199, Tue 17 Nov 2026, before any E207 datum)

The adversarial verifier (`verify-e207`) read the registration and this kit as HOLDS WITH FIXES. Its registration findings are answered by E207.md's
amendment A1; its kit findings here. **Unchanged:** every file the box runs or reads (the runner, its modules, the wrapper, the guard, the build
and its check, the doubles, the preflight, the plan and points: `harness-e207.json` and its 37 entries as committed), the order, the stops, the
gates, the card time and the cap. Desk checks of code and desk reads only.

| finding | what was done | desk proof |
|---|---|---|
| 1 major: step 6n counts other experiments' desk doubles as "ran before" | `desk/neverrun_card_e207.py` rewritten: every folder scanned on its own (E206's scanner unchanged); COUNTED only the lab's data directories, the card and data lanes' folders (`card-*`, `data-*`, the earlier rounds' card lanes), `~/claude/work` but `ee-*`, aifoundry3's run folders; every other record DISMISSED and listed with its paths (DESK-ONLY); E207's own lanes, `tools/claims-v3/e207` (note 13) and `build/e207` subtracted; every counted record of an E207 point or case found again path by path (the scanner's own line rule) and DATED against MM1-v1's freeze (E207.md A1 item 2): RAN BEFORE, TO DATE, AFTER THE FREEZE; `ranbefore-e207.json` (the places, the dated paths, the labels it proposes) beside the words; a failure of the dating labels every counted hit (said) | the stand-in test (every class and rule) both word lines AS EXPECTED; the runbook test's NR case; real (01:03-01:04 PST): the fixed code NEVER-RUN 53 of 53 points, 47 of 47 cases, DESK-ONLY (dismissed): b04 b15 b25; the first code on the same lab and lane folders: RAN BEFORE: b04 b15 b25 (another kit's desk doubles of its own points, which share E207's keys) |
| 2 medium: E209 may run E207's shapes first | E207.md A1 item 2: "ran before" means before MM1-v1's freeze; a later run is REPORTED and stays in every rule | the stand-in test's AFTER cases (a session T0 after the freeze; a data directory dated 17 Nov) |
| 3 medium: no mechanism for the exclusion | E207.md A1 item 3 and `postscore_e207.py` (the registration's): labels from the card lane's `ranbefore-e207-labels.json`, else 6n's proposal; the scorer's own cells re-tallied; the registered verdict; **step 13 (`rb/s24_score_e207.sh`) runs it right after the scorer** (`postscore-e207-A.json` / `.txt` in RB_OUT); its failure leaves the scorer's outputs and is said; `collect_e207.py` copies 6n's `ranbefore-e207.json` in as `ranbefore-e207-card.json` | `selftest-postscore.txt` PASS (31 checks); the runbook test's CD case: the dating file in the data directory's SHA256SUMS, the after-score tool's registered verdicts in RB_OUT with its labels read from that file |
| 4 medium: 6n reads the model session's folders | `~/claude/work/ee-*/` never read (its `src/arms.json` only); their released sessions are committed and read in the lab; the gap stated (E207.md A1 item 1) | the real run's words: NOT READ, the nine `ee-*` folders by name |
| 5 minor: the runbook test's case SD depends on the clock | the stand-in session log's last write is dated inside today (45 minutes ago, or 00:00:01 today when that was yesterday); the rest rule reads its "session end" line, still 45 minutes old | the runbook test 28 of 28 PASS; the case's other branch forced in a copy of the test (the lane's record) |
| 9 minor (the kit's half): runs that printed no check | `collect_e207.py` prints "checks of C: n of m runs printed none" for the README; the brief and the README form carry it | collect's line in the runbook test's CD case: "checks of C: 0 of 3 runs printed none" (seen, not asserted) |
| 10 minor: the brief's open paths; a STOP during the smoke | CARD-LANE-BRIEF.md: row 6n (every word of its line and what to do; exit 10's two causes), row 11 (after the sixth failed collect: E, the files left on the box), row 12 (the dated note and the labels file; the README's checks count; a failed data commit moves the collected directory out of the lab clone, so no other lane's step H is blocked), row 13 (the after-score tool), section 2 (a smoke gate beside the STOP file: read the STOP file's presence and time before writing it up) | desk read |
| 11, 12, 15 notes | none needed (the verifier's own reading) | - |

**The registration's pins** follow A1: `rb/check_history_e207.py`'s and `rb/rb_e207.sh`'s registration subtree `d2089226...` (was `ac8854b4...`,
never landed), step 2's REGPIN 24 entries; the kit's list `SHA256SUMS-e207-kit` re-made (45 entries) and KITPIN set.

**The fixed kit's desk tests, re-run** (2026-11-17 01:20:41 PST to 01:35:08 PST (the runbook test again 01:36:18-01:38:51 PST, after its case P2 was taught to read the registration's count, and the quick set again at 01:43:56 PST), slot jobs inside the sandbox): SELFTEST-RUN-E207 50 of 50 PASS; REALPATH-E207 14 of 14 PASS; REALBYTES-E207 9 of 9 PASS; DESKTEST-BUILD-E207 8 of 8 PASS; 28 of 28 runbook
cases PASS; the dry listing; dmcmd_audit_v2; the quick set (logs/).

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), each test that runs a built host, the runner or a stand-in inside the
sandbox (W/nodev.sh; the real-path test in private UTS and PID namespaces): the runner's desk test (about 10 minutes), the real-path test (one
real build), the build's test (four real builds), the runbook's test (one real build), the real-bytes test, the dry listing. On aifoundry3: two
read-only looks (seconds). No simulator run. The final pass that wrote these logs ran as one slot job inside the sandbox, 2026-11-17 01:20:41 PST to 01:35:08 PST (the runbook test again 01:36:18-01:38:51 PST, after its case P2 was taught to read the registration's count, and the quick set again at 01:43:56 PST: fix-e207's; kit-e207's ran 2026-11-16 23:02:40 PST to 2026-11-16 23:17:11 PST).

SPDX-License-Identifier: Apache-2.0
