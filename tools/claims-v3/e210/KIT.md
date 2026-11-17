# E210's run kit: the switch test on aifoundry3 card 0 from aifoundry2, in E206's kit form (its arm A, which ran FULL on this card) as kit-e207 ported it: one runner with one sampler and the stop lines live, the identity gate, read and watch, E210's opening (60 s at rest; the smoke of random@S1, zeros@S1 and random@S2 against E206's cycles an op at the shape; THE PROBE of maxalte@S2 at 64 W / 63 C; then the stop-path test), 171 runs in the registered order of chained A B B A blocks, each under a plain `timeout 10` and never killed; rgm136 built on the box through the kernel gate and the 489 pattern tiles synced at their sha256; the host's records read past any runtime line; the never-run search repeated before the first card command and again before the data commit; step 7 only once the rest has opened; the reducer to the frozen scorer's form (Q202; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q202, lane `kit-e210`). No card was claimed or opened: aifoundry2 has a card, so
every desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox (no
/dev/et*, an empty /run/lock). No device command was sent, nothing was posted, no simulator was run. One box was reached: aifoundry3, read-only, while no lane booked it (Tue 17 Nov 2026 01:25:19 PST: the reader's sha256 (the pin `16037641...`, unchanged), its riscv gcc's version string `(g1b306039a) 15.1.0`, python3's (3.12.3), the card lock's presence, no `build/e210*` and no `build/e207*` there, E206 arm A's session the newest of ours (ended 18:22:16 PST Mon 16 Nov 2026), no model-session folder there; Tue 17 Nov 2026 01:55:10-01:55:40 PST: step 6n's remote scan, run for real from a scratch RB_OUT, E210's registered scanner on stdin over our folders there (108,115 files in 30.7 s, at nice 19), reads only; nothing written there, no device opened). aifoundry1 was not reached.
New files only, all under `tools/claims-v3/e210/`. The registration [`E210.md`](E210.md) (found by content: the commit that added it, its
`tools/claims-v3/e210` subtree `adef3701...`; `SHA256SUMS-e210-registration` `4219474f...`, 523 entries; amended before any datum by its A1, fix-e210) and every file its list names stay as
committed. **No E210 datum exists. Nothing here changes a forecast, a band, a rule, a threshold, the order, the card time, the cap, the probe, a
stop or the scorer** (the registration's own amendment A1, made by fix-e210 before any datum, re-froze the scorer and changed what the
never-run search counts: section 9). Where E210.md leaves a reading to the kit, the reading is stated in section 4 before any datum.*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained."

## Results first (desk checks of code and desk reads of committed records; nothing is measured)

| check | result | log |
|---|---|---|
| **the runner on the doubles** (`selftest_run_e210.py`): the short path with the identity gate and read, the opening (the rest, the smoke of random@S1, zeros@S1 and random@S2 each read against E206's cycles an op at the shape, THE PROBE, THEN the stop-path test), the 87 C latch tripping nothing; every config gate; every holder; the sampler dead, on card 1, silent, dying, deaf past both SIGTERM waits; the stop-path test with no live sample; the smoke's failures (a wrong check, a crash, a host on card 1, no rise, card 0's runtime line inside a record, records of another mask, the counter at 3 x the shape's, **the operator's STOP file during the smoke, named as the STOP's**); **a tile file missing from the box tree** (the host fails after its device opened, as rgm136 does); K1; **a host hung past its TERM (HUNG, exit 8, NOTHING KILLED: the double ended by itself)**; a host ended by TERM (rc 124); two failures in a row; records of another mask set aside by the frozen scorer's quorum; the board, the mean and the latch lines; 70.0 W not above 70; the die gate; the card-time rule; an operator's SIGTERM; the STOP file mid-session and before the start; a crash; card 1's runtime line on a smoke host, a run's host and the config read; **THE PROBE's rule** (IN; the board above 64 W: maxalte's runs NOT STARTED, no stop; the die at 63 C; a probe process that crashed); **THE ORDER**: the whole registered sequence (171 runs), every key and argv the registered; **END TO END** three times through the reducer and the FROZEN scorer on the registered cut subset; **A SAMPLER SILENT THROUGH A RUN** (fix-e210's case QS: a finished session's copy with every sample inside two runs' counted launches taken out; the reducer, the collection and the re-frozen scorer, E210.md A1 item 6) | **SELFTEST-RUN-E210 58 of 58 PASS** (fix-e210's pass; QS: reduce rc 0, the two runs without clock keys, p_work null, flagged; collect COLLECTED; score rc 0, highmant8@S2, hd4@S2 and maxalte@S2 NO DATA with three blocks set aside by their clock, the drift on the 3 random runs with a power, R0 PASS); OR: PASS: rc 0; 171 runs of 171, every key and argv the registered (72 of them a 61-file --values string), 3333 host records read as their commands' (0 differ); 88 s; E2-R1: PASS: session rc 0, reduce rc 0, score rc 0; 126 runs reduced; t_gemm worst 6.61e-07; W over idle against the injected worst 0.52%; R0 PASS; rules {"B10_REPORTED": "PASS", "B5": "PASS", "H1": "R1 BETTER", "H2": "R1 BETTER", "H3": ...; E2-R3L: PASS: session rc 0, reduce rc 0, score rc 0; 126 runs reduced; t_gemm worst 6.61e-07; W over idle against the injected worst 0.49%; R0 PASS; rules {"B10_REPORTED": "FAIL", "B5": "FAIL", "H1": "UNDECIDED", "H2": "R1 BETTER", "H3": ...; E2-R3: PASS: session rc 0, reduce rc 0, score rc 0; 122 runs reduced; t_gemm worst 6.61e-07; W over idle against the injected worst 0.59%; R0 PASS; rules {"B10_REPORTED": "FAIL", "B5": "FAIL", "H1": "UNDECIDED", "H2": "R3 BETTER", "H3": ...; PB-W: PASS: rc 0; the probe OUT (board max 66.41 W, die max 57 C; 'the board read 66.41 W, above 64 W'); maxalte's runs [('044-pass2-maxalte-S2', False), ('045-pass2-maxalte-S2', False)]; the other 8 runs ran 8; 22 s; HG: PASS: rc 8; the run's process hung [True]; the hung double: 'the hung double ended by itself after 14.0 s (pid 1845146); nothing killed it' (20 s after the session began); R9: PASS: rc 0; run 007's process rc [1]: 'FAIL: cannot read 2 x 1024 bytes of tiles from tools/claims-v3/e210/tiles/fp32/bhalfeq/bhalfeq_37.bin' | [`logs/selftest-run-e210.txt`](logs/selftest-run-e210.txt) |
| **the REAL path** (`desk/realpath_e210.py`, `desk/realpath_e210.sh`): run_e210.py WITHOUT --dry under aifoundry3's hostname (a private UTS namespace) and a private PID namespace, stand-ins for the reader behind the REAL guard, et-who, the host, the lock and the nodes, the REAL kernel ELF from the REAL build_e210.sh: the box check (the kernel gate, the 493 tiles, the harness of 518 files, the preflight), the lock, et-who and ps, the identity gate and read, the opening (the smoke, the probe, the stop-path test), the tie and two runs (004 sparse50@S1; 007 bhalfeq@S1, its 61 tile files read by the host stand-in from the stand-in tree as rgm136's fillPools reads them); a host hung past its TERM under the real `timeout 10` (left, ending by itself); the lock held; a device process of ours; the reader off its pin; a changed .text; ET_DEVICES three ways; another login on card 0; the other card three ways; card 1's and card 0's runtime lines; a sampler death; a build record without its builder; the operator's STOP file | **REALPATH-E210 14 of 14 PASS** | [`logs/realpath-e210.txt`](logs/realpath-e210.txt) |
| **the parsers on real committed bytes** (`desk/realbytes_e210.py`): E206 arm A's 244 committed stdouts from THIS card (the same host and binary); **E206 arm A's 241 committed runs through E210's reduce_run give E206's committed data-e206.json field for field**, and its smoke through E210's smoke reading (p029, p080 and p034, E210's smoke and reference points, among them); **E210's 61-file --values strings inside E206's real records**; E190's 174 committed rgm136 stdouts on both cards (87 carrying aifoundry1's runtime line) and its 12 card-1 bursts against its committed reduction; runtime lines of card 0 and card 1, single and nested, at every byte offset of real aifoundry3 records; 1a4bc1e3's and 7156ac15's split stdouts; E206's committed config line with runtime lines at every offset; the identity gate both ways on 12 committed config forms | **REALBYTES-E210 10 of 10 PASS**; RB-E206R: 241 runs (119 points and 3 ties) read by reduce_e210.reduce_run, and the smoke (3 checks, cycles at ['p001', 'p021', 'p046']): field for field E206's committed data-e206.json (equal); E210's smoke references among them, p029/p080/p034's runs at [537.98, 537.99, 831.72, 831.73] cycles an op; RB-LONG: E206's p029 records with bhalfeq@S1's values string (3371 characters, 61 tile files; the longest line 3770 bytes): 15 launch records and 1 check record(s) read whole against its own command line; against lowmant8@S1's 15 not read; 184 runtime-line splices in the long record, 0 read ... | [`logs/realbytes-e210.txt`](logs/realbytes-e210.txt) |
| **the build on this desk's real toolchain** (`desk/desktest_build_e210.sh`): aifoundry3's build, the kernel gate's cases (aifoundry3's .comment form, a .rodata byte, a .text byte), a changed source, aifoundry1 and aifoundry2 refused, the runner's box check, the guard on other boxes and with ET_DEVICES and the statistics reset | **DESKTEST-BUILD-E210 8 of 8 PASS** | [`logs/desktest-build-e210.txt`](logs/desktest-build-e210.txt) |
| **the runbook** (`rb/selftest_rb_e210.sh`: a fake ssh and rsync, a stand-in aifoundry3, the real build): the window rule, the lab-git lock, step 2 at every pin (the registration's 523, the kit's, MM1-v1's 77) with the registration's checks recomputed, the history check and a shadow, E210's data refusing step 2 and a gate stop's record reported, the look, ours_live, the sync, a login link, a hang, NO-THIRD-BUILD, the real build, **step 6n on stand-in roots** (a negzero tile named in the lab's data and an hd4 tile named in a box run folder found; E210's own lanes, E210's own dry pass and the model session's folder left out; the --desk-only form; **E210.md A1 item 1's verdict first**: a host-refusal case naming noise read "elsewhere (never a run)", a plan naming a highmant8 tile not a run, a launch record naming noise flipping all nine as registered), **step 7 refusing with no config read sent without a fresh 6n report and until the rest has opened**, the dry pass with the probe, the HUNG marker, the same-day rule (dated inside today), the last start, step 9 without today's 6n report, the REAL session stopping at its box check, step 10's readings, the copy-back, **step 12 refusing before step 12n**, the gate stop's record, a copy not exact, a session that ran through step 12's data directory (both never-run reports in it) and step 13's FROZEN scorer | **SELFTEST-RB-E210 28 of 28 PASS** | [`logs/selftest-rb-e210.txt`](logs/selftest-rb-e210.txt) |
| the dry listing, every step with stand-ins | **dry listing: 16 steps listed, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e210.txt`](logs/dry-listing-e210.txt) |
| `dmcmd_audit_v2` on the session's files (`preflight_e210.sh`: the runner, its two modules, the wrapper, the build, the harness check, the guard, the host's source) | **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)**, every one a READ, no allow-list | [`logs/dmcmd-audit-e210.txt`](logs/dmcmd-audit-e210.txt) |
| the quick set | 11 lines PASS / OK / GO / yes (the two modules' self-checks, the harness re-made and at its sha256, the registration's points and forecasts recomputed byte for byte and its kernel sources re-hashed, the re-frozen scorer's self-test byte-identical to the committed, the registration's list (523) and MM1-v1's folder list, the preflight); bash -n of every shell file of the kit: 24 files, 0 with a syntax error; python3 compile of every Python file of the kit (in memory, no __pycache__ written): 24 files (the registration's among them), 0 that do not parse; calls that could send a kill in the kit's own code (subprocess .kill(), os.kill, signal.SIGKILL, 'kill -9', 'timeout -k' outside prose): 0 (the lines naming one are prose, listed) | [`logs/checks-e210.txt`](logs/checks-e210.txt) |

## 1. The kit, in E206's form

- **The runner** ([`run_e210.py`](run_e210.py), [`session_e210.sh`](session_e210.sh), [`e210_common.py`](e210_common.py),
  [`e210_ident.py`](e210_ident.py)): E206's runner for its arm A (`tools/claims-v3/e206/run_e206.py`, landed in `906699ea`, which ran E206 arm A
  FULL on this card: 241 of 241 runs, data `d7e4f35e`), as kit-e207 ported it (its local commit `4bd6e38c`), every behaviour unchanged but E210's
  opening (the rest, the smoke, THE PROBE, the stop-path test), E210's order (`points-e210.json` › `runs`: 171 runs, each its registered
  `host_args`), the card-time rule (85 / 95), one arm, and the files' names. Before anything opens: the host name is aifoundry3, the device
  environment carries no ET_DEVICES (the runner drops an inherited one), build/e210rgm's record today's BUILT by build_e210.sh on this box, the
  kernel through THE KERNEL GATE again, the host at the sha256 the build recorded, the reader at its pin (`16037641...`), the 493 tiles at their
  sha256 (the four kinds tiles at kinds.json's, E210's 489 at the registration list's), the harness (HARNESS OK: 518 files, the registration's
  frozen points and forecasts among them) and the preflight (dmcmd_audit_v2 GO). Then the card's lock (`flock -n`, held to the end), the holders
  (counts only), THE FIRST CARD COMMAND `ettelem config` through [`ettelem_guard_e210.sh`](ettelem_guard_e210.sh) under a plain `timeout 10`
  with its stderr kept (the start config and THE IDENTITY GATE; the card time counts from it), ONE sampler (10 Hz) whose every line feeds THE
  STOP LINES as it arrives, THE IDENTITY READ, the opening, the registered sequence, the closing config, "session end", MANIFEST.sha256 last.
  Nothing is set. Every start (each run, each smoke or probe process, every rest read) first reads the operator's STOP file; never two samplers
  at once.
- **No SIGKILL anywhere** (W/out/orch/kill-rule.txt; AGENT.md "never kill -9"): every device process is under a plain `timeout 10`; the runner
  waits for it with a bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the stop
  file, starts nothing further, sends no further card command (no closing config read), closes the session and LEAVES the process (exit 8).
  et-who, the harness check and the preflight are waited on with a bound and left past it (a failed read, never a kill). The sampler is stopped
  by SIGTERM only. The build runs under a plain `timeout`. The one kill in the whole path is k6's bounded runner's (rb_run.py, unchanged, every
  kit's): past a call's bound it ends THE DESK'S OWN ssh client, rsync or collector; never a process on a box, where nothing of E210's sends any
  signal to a device process. (The quick set lists every line of the kit naming a kill: each is prose.)
- **The build** ([`build_e210.sh`](build_e210.sh), [`check_e210.py`](check_e210.py)): E136's rgm136 unchanged, into **build/e210rgm** (a new
  folder of ours) on aifoundry3; the kernel through THE KERNEL GATE (the .text always the registered `61315bf6...`, and the whole ELF the
  registered `aace138c...` or its loadable identity the pinned `649d4079...`, E206's pin, which E206 arm A's build on this box met); the host by
  its behaviour (four refusals main.cpp makes before its device Session); the ET_DEVICES reading recorded, never a gate (one card);
  build/e210rgm/BUILD-e210.json. Any box but aifoundry3 is refused before anything is built. **No host change, no kernel change, no new
  generator**: E210's patterns reach the host as tile files (E210.md 2), so no host-side generator was written and none is built.
- **The doubles** ([`fake_card_e210.py`](fake_card_e210.py)): config (aifoundry3's committed start config and its identity block), et-who (who
  holds the stand-in nodes and lock, from /proc), a toy card's sampler driven by the launches the host double announces (its latch at the
  committed 87 C), and the host (rgm136's SPARSITY records on a virtual clock at E206's measured random seconds and counter at the shape, the
  same for every case; its watts E206's random W at the shape plus one frozen route's dJ, `E210_FAKE_TRUTH`; THE TILE READ: it opens the device
  first, then reads every tile file of --values from its working directory as fillPools does, failing as the real host fails on a missing or
  short file; modes for every failure the tests need, among them a host that IGNORES its TERM).
- **The reducer** ([`reduce_e210.py`](reduce_e210.py)): the session into the frozen scorer's data form (`{"experiment": "E210", "runs": {...},
  "smoke": {...}, "probe": {...}}`, score_e210.py's docstring) and a table; E206's per-run reading line for line (E206 arm A's committed runs come
  back field for field). **The collection** ([`collect_e210.py`](collect_e210.py)): COPY-BACK EXACT, the data directory (or a gate stop's record),
  the scrub, the reducer, both never-run reports, SHA256SUMS. **The harness** ([`check_e210.py`](check_e210.py), `harness-e210.json`, 518 files)
  and **the preflight** ([`preflight_e210.sh`](preflight_e210.sh)).
- **The never-run search, repeated** ([`desk/neverrun_card_e210.py`](desk/neverrun_card_e210.py), [`rb/s06n_neverrun_e210.sh`](rb/s06n_neverrun_e210.sh)):
  E210.md section 4's repeat, at step 6n and step 12n (section 4 item 17 below), with E210's own registered scanner and report, unchanged.
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged (the arm A the first word of every box step; one RB_OUT): the
  window; step 2 (the pull under the lab-git lock, the three lists pinned by count and bytes, the history check, the harness, the registration's
  checks recomputed and the scorer's self-test byte-identical, the preflight, the desk tests' logs; outside the kit's list); the look (k6's); the
  sync; the build; **step 6n**; **step 7, only once the rest has opened and within 30 minutes of 6n**; the dry pass; the session; the wait; the
  copy-back; **step 12n**; the data directory; the scorer after the data commit. **No post and no release** (waived).
  [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lane's brief, with THE ONE-LAB RULE and THE QUIET HOLD in its step table;
  [`DATA-README-FORM-e210.md`](DATA-README-FORM-e210.md) is the data README's form.

## 2. Card-minutes and the cap (registered; unchanged)

About 73 card-minutes planned (`points-e210.json` › `plan`: 171 runs at 26 s at S1 and 22.5 s at S2, E206 arm A's pace on this card, and about
210 s of opening); no run starts once the card time passes 85 minutes; at 95 the session ends after the run in progress (the round's cap is 100);
a started run is cut only by a stop. The registered subset if cut: the opening and passes 1-4 (every kind twice at both shapes, 126 runs, about
55 card-minutes).

## 3. The order on the box

The card lane's full table, with the booking, THE ONE-LAB RULE (desk / undesk around steps 0-2, collect / uncollect around step 11 to the data
commit's push), THE QUIET HOLD and the end of every path, is [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps:

| step | file | what |
|---|---|---|
| 1 | `rb/s02_window_e210.sh A <day> <last start> <last end>` | first; today only; the window (G = the booking) in its own RB_OUT |
| 2 | `rb/s03_desk_e210.sh A` (outside the kit's list) | the window; the pull under the lab-git lock; the registration and the kit found by content, ancestors of HEAD; the paths clean; HISTORY OK; the registration's list (523), the kit's list and MM1-v1's folder list (77) at their pins; the harness; both self-checks; `points_e210.py` and `forecast_e210.py <top> --check` (recomputed byte for byte), `desk/kernel_e210.py --check`; the scorer's self-test byte-identical; the preflight; the desk tests' logs; no E210 datum in any ref |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | k6's, unchanged (et-who, who, uptime, the holder rule); our login recorded for the scrub |
| 5 | `rb/s07_sync_e210.sh A` | the rsync of the harness's 518 files into `~/aifoundry`; HARNESS OK on the box |
| 6 | `rb/s08_build_e210.sh A start`, then `wait` | the detached build, NO-THIRD-BUILD, the record (KERNEL OK), the harness, the preflight and both self-checks on the box |
| 6n | `E210_ROUND_OUT=<OUT> rb/s06n_neverrun_e210.sh A [--desk-only]` | THE NEVER-RUN SEARCH REPEATED: E210's registered scanner over the lab at HEAD, the round's lane folders and HOME/claude/work at the desk and over our folders on aifoundry3 (a bounded read), E210's own folders and the model session's left out; the registered report, scrubbed; RB_OUT/e210-neverrun.txt (REPORTED) |
| 7 | `rb/s09_reads_e210.sh A` | 6n's report under 30 minutes old, then THE REST RULE on the box, no card command (10 while either fails); then k6's step 7 unchanged (TDP 0 W / 65 C / 600 MHz, et-who clean) |
| 8 | `rb/s10_dry_e210.sh A start`, then `wait` | the runner on the box with its doubles, no device (the probe IN; runs 004 and 007 read their tile files from the box tree) |
| 9 | `rb/s11_session_e210.sh A` | the last start (k6's), the cap before the last end, today's 6n report, k6's guard, THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e210.sh` detached |
| 10 | `rb/s20_wait_e210.sh A` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e210.sh A` | one read-only copy back, COPY-BACK EXACT |
| 12n | `E210_ROUND_OUT=<OUT> rb/s06n_neverrun_e210.sh A --late` | THE NEVER-RUN SEARCH AGAIN BEFORE THE DATA COMMIT (E210.md 4): the desk's three roots, after the copy-back; RB_OUT/e210-neverrun-late.txt (REPORTED) |
| 12 | `rb/s23_data_e210.sh A` | step 12n's report written after the copy-back, else 10; the data directory `docs/reports/data/<day>-e210-switch-test-aifoundry3/` (or a gate stop's record under `docs/reports/gate-stops/`), the scrub, the reducer, both never-run reports, SHA256SUMS, the desk-path gate, the history check; then the card lane's README and data commit |
| 13 | `rb/s24_score_e210.sh A` | after the data commit only: `score_e210.py DATA.json --out SCORED.json --txt SCORED.txt` (registered, unchanged) on the committed data-e210.json |

## 4. The readings stated here before any datum (where E210.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH** (E206.md amendment A1 item 1, which E210.md 6 adopts in words: "the die (the shires' mean, or
   the hottest sensor's latch once it has risen during the session)"): the line trips on the shires' mean (`minshire[0]`) at or above 70 C, or on
   the latch (`minshire[2]`) only when it has risen during the session above the lowest value it read since the session's first sample and reads
   at or above 70 C. On aifoundry3 card 0 the latch read 87 C in every committed sample of E189, E195, E196, E197 and E206 arm A.
   `e210_common.Stops`, E206's line for line.
2. **The other stop lines** (E210.md 6): the board strictly above 70 W on 3 samples in a row that carry a board reading (a sample with none
   neither counts nor breaks the row: E206.md A1 item 2). A trip touches the host's `--stop-file` at once: the running host ends its loop at its
   next launch boundary (about 0.5 s), never killed; nothing further starts; the run's 4 s read and the closing follow.
3. **THE OPENING** (E210.md 6: "60 s at rest; the smoke ...; the probe ...; the stop-path test on live samples (no launch); two random@S1 warm-up
   runs"): 60 s at rest (the rest die: the median of the shires' mean over it; the die gate is formed from it), then one process each of
   random@S1, zeros@S1 and random@S2 with `--seconds 2 --budget 3.5` (the budget is E146's, E190's, E206's and E207's smoke's), each with the
   host arguments of its case's first run, not die-gated; each must exit 0 with every launch ok, its check of C exact or approx, its cycles an op
   (the CHECK record's `cycles_per_op`: the counter's mean, as E190's and E206's smoke read it) within 50-250% of **E206's measured cycles an op
   at the shape** (forecast-e210.json › calibration › S › e206_points: random@S1 p029 537.98, zeros@S1 p080 537.99, random@S2 p034 831.72; read
   through the file's frozen sha256), the board at least 2 W over the rest during its launches (at least 3 samples), and the host on card 0 (the
   watch). Any failure: the smoke gate failed, no run (a gate stop); a STOP file (or another stop) during a smoke process is named first in the
   gate's words (verify-e207's finding V4). The warm-up ties are runs 001 and 002 of the registered order.
4. **THE PROBE** (E210.md 6: "one checked 2 s process of maxalte@S2: every board sample at or under 64 W and the die under 63 C, else maxalte
   leaves the session - a registered rule, logged, its runs skipped and its case NO DATA; the probe's own readings are reported, never scored"):
   after the smoke and before the stop-path test; **under the die gate** (min(60, rest die + 4) C, at most 300 s: a gate not met leaves maxalte
   out, no probe process) and **after a 10 s rest read** (the run form's: E206's); ONE process `--seconds 2 --budget 3.5` with maxalte@S2's
   registered host arguments; **its window from the process's start to the end of a 4 s tail** (the run form's tail: the die lags the board);
   **IN** when that window holds at least one board reading and one die reading, every board reading at or under 64 W and every die reading
   under 63 C, the die read as the stop line reads it (the shires' mean, and the latch once it has risen above the session's lowest reading);
   else **OUT**. A probe process that ends badly (rc not 0, no launch, a check of C not exact or approx) is also OUT (the line could not be
   shown) and counts as a failed process for "two failed processes in a row"; K1, HUNG, an identity trip or a stop line during the probe stop
   the session as anywhere (a gate stop: no run has started). OUT: every maxalte@S2 run is not started (`ran: false`, the probe's reason named),
   the random runs around them run as registered (they serve the neighbouring blocks), nothing else changes; the probe's checks go to the
   scorer's `probe` entry (R0 reads them) and its readings to `probe_reading` (REPORTED).
5. **The start config** (E210.md 6): TDP 0 W / 65 C / 600 MHz, read as found, nothing set; read again at the end (never after a HUNG, nor while
   the sampler would not stop).
6. **The identity**: `/dev/et0_mgmt`, physical device ID 0 on the config read's stderr (E189's and E206 arm A's committed aifoundry3 reads print
   exactly that block); no minion_mv bound (a one-card box). The identity read with the sampler running; the host watch at every process; a host
   naming or holding another card stops the session at once (in the opening: the smoke gate). The box itself is told by its hostname.
7. **The holders** (E206 arm A's): any holder line of another login, another user's device process, a CI job, any other device process of ours.
   **An unreadable et-who is a holder** (E202's fix). Counts only.
8. **The die gate**: min(60, rest die + 4) C, on a live sample (under 2 s old) only, waiting at most 300 s and never past the card-time rule or a
   stop; else that run is NO DATA.
9. **A run**: the die gate, the holders again (et-who and ps), 10 s at rest (p_rest = the median board W of its last 5 s), ONE host process
   `timeout 10 sparsity_host <the run's registered host_args> --kernel <ELF> --stop-file <STOP>`, a 4 s read. The `--values` string stays as
   registered: its tile paths are read relative to the box tree's root, the host's working directory, as E206 arm A ran (the kit adds the
   absolute paths of `--kernel` and `--stop-file`, E210.md 2's words). A live sampler before the process, else the run ends there flagged and the
   sampler is restarted (SIGTERM to a stale one); a stale sampler that will not stop on SIGTERM is left running, never killed, and the session
   stops.
10. **Failures.** A failed process (rc not 0, `timeout 10`'s 124 among them) is flagged; **two failed processes in a row stop the session**
    (E190's E64 rule, for one-process runs). **K1**: a host whose stderr says "kernel did not finish" stops the session at once. **HUNG**: exit
    8. A crash of the runner is named and exits 1, its closing run.
11. **Card time** counts from the start config read (the session's own first card command; step 7's read is reported apart). A run starts only
    if the card time is under 85 minutes and its longest length (28 s once its gate has passed) fits the 95-minute cap less 60 s of closing and
    ends 90 s before the window's last end.
12. **The reader**: aifoundry3's `build/ettelem/ettelem` (`16037641...`, read there on Mon 16 Nov 2026 by E206's kit and by kit-e207), through one
    guard, `config` and `sample` only, ET_DEVICES unset, any other box refused.
13. **THE REST RULE** (E210.md 6): the first card command at least 40 minutes after our previous session on aifoundry3 ended. E206's rule (every
    session-log form of ours, the activity floor, the model session's folders `~/claude/work/ee-*/` by their files' times), its floor now leaving
    out E210's own folders, so E207's session (and E206 arm A's) count. Steps 7 and 9 read it on the box, step 7 BEFORE its config read.
14. **THE HUNG MARKER and THE SAME-DAY RULE** (E202's): step 9 refuses while any session log of ours on the box holds a HUNG line; an E210
    session that opened the card earlier that day refuses another; after sessions that opened no device, a third try refuses.
15. **The window**: step 9 launches only before the registered last start G + 1:30 (k6's `rb_need_start`) and with 6,000 s (the 95-minute cap
    and 5 minutes) before the last end (G + 3:30); the last start binds; the runner itself keeps every run inside the last end.
16. **The data directory**: `docs/reports/data/<day>-e210-switch-test-aifoundry3/` with `session/`, `data-e210.json`, `reduce-e210.txt`, the two
    never-run reports (`neverrun-e210-card.*`, `named-by-card.json`; `neverrun-e210-late.*`, `named-by-late.json`), SHA256SUMS and the README; a
    session in which no run started is a gate stop's record under `docs/reports/gate-stops/<day>-e210-switch-test-T<T0>-aifoundry3/` (E202's
    form), never scored. Step 2 refuses on any E210 datum. **The scrub**: the box's home becomes "~" and our own box login "<login>" in every text
    and .gz file; any /home/ path or the login left refuses the collection.
17. **THE NEVER-RUN SEARCH, REPEATED** (E210.md section 4: "A pattern the model session runs before E210's card day stays in E210 but is no longer
    'never run'; E210's card lane repeats this search before its data commit and says which"): twice. **Step 6n**, right before step 7's config
    read (the day's first card command; step 7 refuses unless 6n ended within the last 30 minutes, step 9 without that day's report), runs E210's
    registered scanner and report UNCHANGED (`desk/neverrun_e210.py`, at its registration-list sha256) over the registered four roots: at the desk
    the lab clone at HEAD, the round's lane folders (named by `E210_ROUND_OUT`, so no private path is written in the kit) and HOME/claude/work; on
    aifoundry3 the registered tops there that exist. **Step 12n** (`--late`), after the copy-back and before step 12 (which refuses without it),
    runs the desk's three roots again. **Left out by the scanner's own `--exclude`** (verify-e207's findings 1 and 3, taken in before any datum):
    E210's own folders (in the lab `tools/claims-v3/e210` and any `docs/reports/data/*e210*`; in the round's folder every top-level folder named
    `<role>-e210[<suffix>]`; on aifoundry3 `build/e210`, `build/e210rgm` and the synced `tools/claims-v3/e210`), and the model session's folders
    `~/claude/work/ee-*/` on both boxes (the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026: no lab lane reads their uncommitted session
    folders; their released sessions are committed in the lab, which is searched). The registered report's own markers keep counting
    sw-design-a's desk tiles as desk files. For a pattern found run, `named-by.json` lists the text files whose GEMM --values strings name the
    hit tile (verify-e207's finding 1: the paths of each hit). **The registered rule's two conditions are reported apart**: its verdict reads
    every law SEE HITS when (i) any GEMM string anywhere names a generator rgm136 does not draw, whatever file the string is in, or (ii) a
    law-passing tile file outside the desk folders is named by a GEMM; the words give the verdict and then each condition with its sources
    (`named-by.json`, and each generator's files in the report's text), so the card lane can say which patterns ran before. The result is
    REPORTED, never a gate, and changes nothing: E210.md 4 keeps the pattern in E210 and in every rule; the README says which. NOT SEARCHED, as
    registered: aifoundry1's own folders. **As amended (E210.md A1 item 1, fix-e210):** both conditions count a GEMM string only inside a host
    launch record (a `SPARSITY` record's `values` field, or a record split from its prefix that keeps its `launch` field); a string anywhere
    else (a refusal check, a script, a plan, a schedule) is listed apart and is never a run. The registration's `desk/neverrun_gens_e210.py`
    classes every string over the same roots (at the desk, and on aifoundry3 in step 6n's same bounded read, from stdin), and the words give
    A1's verdict first, then the tile files named in launch records and anywhere, the generators in launch records and elsewhere, and the
    registered rule as first written.
18. **The host's records** are read from a source no runtime print can split (e210_common's docstring); the runtime lines are removed pass after
    pass until none is left; **a runtime line naming another card than card 0** is an identity trip; card 0's own line is dropped and counted.
19. **No post, no release** (waived: the owner's words of Sun 15 Nov 2026, 10:22:36 PST). **The host's package counter is not read.**
20. **The sealed forecasts** (E210.md 0): a sealed sha256 the model session posts for E210's cases before the first card command is registered in
    `tools/claims-v3/sealed-e210/e210-freeze-lines.md` before that command; the card lane checks the round's record of them at its step 0; step 2
    reports any such note (REPORTED). Its numbers never enter the lab.
21. **THE OPERATOR'S STOP FILE** (CARD-LANE-BRIEF 2): `touch build/e210/T<T0>-A/STOP` on the box is a registered stop: the running host ends at
    its next launch boundary, and the runner reads the file before every start; the closing follows. A STOP file already in the session's folder
    when the runner starts is a refusal before any device, and the file is kept.
22. **The reducer's readings** (E210.md 6 and 8, score_e210.py's docstring): `ran` true when the run's one process started (a run the gate, the
    cap, the probe or a stop kept from starting is `ran: false` with its reason); counted launches launch >= 0, ok, wall_s >= 0.1 s, a pass, the
    kernel clock in 590-610 MHz; t_gemm = sum of wall / sum of passes; cycles an op the median of the host's cycles_per_op (the counter's mean);
    p_work the median board W inside the counted launches; p_rest the median of the 5 s before the process; mhz_min and mhz_max the lowest and
    highest minion clock inside the counted launches; checks every check of C the process printed (**a process that printed none has checks []**: the scorer as
    re-frozen by E210.md A1 item 5 reports it by name, `R0` › `missing_REPORTED`, never an R0 FAIL, and Q sets its run aside; the first freeze
    read it as an R0 FAIL); **A QUIET SAMPLER** (E210.md A1 item 6, fix-e210): a run with counted launches but no telemetry sample inside them
    carries no `mhz`, `mhz_min` or `mhz_max` key at all and `p_work_w` null, flagged "no telemetry sample inside the counted launches" and
    listed in `runs_without_a_sample_inside`; the scorer sets it aside by Q and the table prints it; a sample's board W, die or clock that is
    not a finite number is no reading (never NaN into a median); record
    {arm, type, minions, shire_mask} of the counted launches (records of another command are not read, their own fields passed on so the
    scorer's quorum sets the run aside).

## 5. Files

| file | what |
|---|---|
| `e210_common.py` | the arm, the build's pins, the tiles, the opening and the probe's rule, the stop lines and the latch reading, the gate, the order, the argv, the counted launch, the host-records and config parsers; its self-check |
| `e210_ident.py` | the identity reads, the host watch, the board's rise, the sampler's freshness (E206's module, the arm's table only changed); its self-check |
| `run_e210.py`, `session_e210.sh` | the runner and its detached wrapper |
| `ettelem_guard_e210.sh` | the only way the runner reads a card: `config`, `sample --seconds --every-ms` |
| `build_e210.sh` | the box build and its record |
| `check_e210.py`, `harness-e210.json` | every file the box runs or reads, at its sha256 (518); THE KERNEL GATE |
| `preflight_e210.sh` | dmcmd_audit_v2 on the session's files |
| `fake_card_e210.py` | the doubles |
| `reduce_e210.py` | the scorer's data form from a session |
| `collect_e210.py` | COPY-BACK EXACT; the data directory or the gate stop's record, the scrub, the reducer, the never-run reports, SHA256SUMS |
| `selftest_run_e210.py` | the runner's desk test, end to end through the frozen scorer |
| `desk/realpath_e210.py`, `desk/realpath_e210.sh` | the real-path desk test |
| `desk/realbytes_e210.py` | the parsers, the reducer and the identity gate on real committed bytes |
| `desk/desktest_build_e210.sh` | the build's desk test on the real toolchain, with the kernel gate's cases |
| `desk/neverrun_card_e210.py` | the never-run search repeated (steps 6n and 12n: the desk half and the report) |
| `rb/` | the runbook's steps (6n and 12n among them), its common file, the rest rule, the history check, the dry listing, its desk test |
| `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e210.md` | the card lane's brief; the data README's form |
| `logs/` | every check above |
| `SHA256SUMS-e210-kit` | the kit's files (step 2, `rb/s03_desk_e210.sh`, aside: it pins this list), its logs |

## 6. Device commands

`preflight_e210.sh` (dmcmd_audit_v2, its table v2): **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)**, with no allow-list and no exception: `ettelem config`
(GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) and `ettelem
sample` (GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES), each through
the guard, which refuses `--reset-ms` and every other word before the device opens. The host opens the ops node only. Step 7 sends k6's config
read through E128's guard (the same five READs). No set, no reset, no statistics reset, no firmware query, no residency read, no drain
(`dev_mngt_service` is never run), no power cycle. The identity reads send nothing to a card: et-who stats the nodes, and /proc is read for our
own processes only. Steps 6n and 12n send nothing to a card (file reads only).

## 7. What the desk cannot show

1. **The runner has met only its doubles and stand-ins**: the live sampler, the card lock, et-who and the real host meet it first in the
   session. But its code is E206's, which met all of them on this card (E206 arm A, 241 of 241 runs), and E210's changes are the opening (the
   probe new), the order, the card-time numbers and the files' names.
2. **The tile files on the card**: the host has read E210's tile files only as the doubles read them (2 x 1,024 bytes each, relative to the
   working directory); rgm136's real fillPools reads them the same way after its device opens (a file missing or short fails the process there,
   case R9), and step 5's harness check and the box check hash all 493 on the box before any device opens. The host's own check of C on the card
   is the registration's (E210.md 2: 64 sampled C tiles against its double reference); the desk's reference is the registration's
   `desk/check_gemm_e210.py` (every pattern at both shapes, PASS), which the kit does not re-run.
3. **The build on aifoundry3** is shown on this desk's toolchain with aifoundry3's .comment written in (B4); E206 arm A's build there met the same
   gate.
4. **Steps 6n and 12n** are shown on stand-in roots by the runbook's test; step 6n was also run once for real against the real roots from a scratch RB_OUT (Tue 17 Nov 2026 01:54:10-01:56:38 PST, aifoundry3 unbooked): `NEVER-RUN 0 of 9 patterns; RAN BEFORE: negzero signs lowmant8 highmant8 bhalfeq badjeq hd4 maxalte arow50; by named tile files: 0 of 9 named; generators not the host's: noise in 16 desk file(s)` (REPORTED). Every flip came from condition (i): the generator `noise` in E211's host-refusal checks (reg-e211's and kit-e211's `gemmLn2x2x2:noise:...` and `gemmLnc2x2x2:noise:...`, which the host refuses before any device: never a run); condition (ii) found no law-passing tile file named by a GEMM (2,655 law-passing tile files outside the desk folders, none named). The scans: the lab at HEAD 63,817 files (10.8 s), the round's lane folders 365,216 (33.1 s; kit-e210 and reg-e210 left out), the work folder 128,401 (15.2 s; nine model-session folders left out), aifoundry3 108,115 (30.6 s). A desk read, REPORTED, not the card lane's repeat. The first try at 01:46:45 gave the registered verdict alone (the words before the two conditions were split out), which is what this run's split answers. **Under E210.md A1 item 1** (fix-e210's desk read, Tue 17 Nov 2026 07:12:45-07:15:44 PST, from its scratch clone at GitHub main `f155c8ca` with the registration and this kit, aifoundry3 NOT SEARCHED while the orchestrator's booking held it): `NEVER-RUN 9 of 9 patterns (A1); by named tile files in launch records: 0 of 9 named; anywhere (the registered condition ii): 2 of 9 named (signs highmant8); generators not the host's in launch records: none; elsewhere (never a run): noise in 27 file(s); the registered rule as first written: 0 of 9` (REPORTED). The two named anywhere are E212's own tiles (`fld_sign.bin`, `den4.bin`) in its planned arms and schedules, copied into the round's folders by Q208's lanes: plans, not runs.
5. Card time waits on the queue (E207 first), the rest, the day, the booking and a readiness lane's go lines (CARD-LANE-BRIEF.md).

## 8. Labels

Every figure quoted from E210.md and its files (the forecasts, the order, the caps, the stops, the gates, the probe, the pins) is **registered**.
The desk tests' results are **desk checks of code**, not measurements; the end-to-end joules and the scorer's words come from the doubles (E206's
measured random at the shape and the frozen routes driven through a toy card): not a measurement and not a reading of E210. The committed reads
the kit cites (the latches, the identity blocks, E190's and E206's outputs) are **desk reads of committed records**; the aifoundry3 reads are
**read-only looks** at the box. Nothing here is **blind** or **held out**, and no E210 datum exists. Python: `/usr/bin/python3` 3.12.3.

## 9. fix-e210: verify-e210's kit findings answered (Q202, Tue 17 Nov 2026, before any E210 datum)

The adversarial verifier (`verify-e210`) read the registration and this kit as HOLDS WITH FIXES. Its registration findings are answered by
E210.md's amendment A1; its kit findings here. **Unchanged:** every file the box runs (the runner and its two modules, the wrapper, the guard,
the build and its check, the doubles, the preflight, the points and the forecasts: `harness-e210.json` re-made only for the registration list's
new sha256, 518 entries, one line changed), the order, the opening, the probe, the stops, the gates, the card time and the cap. Desk checks of
code and desk reads only.

| finding | what was done | desk proof |
|---|---|---|
| 1 major (kit-e210's finding 1): the never-run verdict reads strings that are not runs | E210.md A1 item 1: both conditions count a GEMM string only inside a host launch record (condition (ii)'s case found by fix-e210: E212's plans, copied into the round's folders, name two of E212's tiles that pass the signs and highmant8 laws). `desk/neverrun_card_e210.py` runs the registration's new `desk/neverrun_gens_e210.py` over the same roots (refusing it off its registration-list sha256) and gives A1's verdict first, then the tile files named in launch records and anywhere, the generators in launch records and elsewhere, and the registered rule as first written (`named-by.json` › `A1_item_1`); `rb/s06n_neverrun_e210.sh` runs it on aifoundry3 in the same bounded read, from stdin (`--a3` without `--a3-gens` is refused); the brief's row 6n and the README form read it | the runbook test's NR, five runs on stand-in roots: NR1 (aifoundry3 searched) and NR2 (desk only) as before; NR3 a refusal check naming noise: A1 8 of 9, the registered rule 0 of 9; NR4 a plan naming a highmant8 tile: A1 8 of 9, condition (ii) anywhere 2 of 9; NR5 a launch record naming noise: A1 0 of 9, as registered. The real desk read (07:12:45-07:15:44 PST): NEVER-RUN 9 of 9 (A1) (section 7.4) |
| 2 medium: a sampler silent through a run crashes the reducer's table, so the collection refuses | `reduce_e210.py`: a run with counted launches but no telemetry sample inside them carries no clock key and `p_work_w` null, flagged and listed (`runs_without_a_sample_inside`); a reading that is not a finite number is no reading; the table None-safe (4.22). The frozen scorer's half is E210.md A1 item 6 (the scorer re-frozen) | `selftest_run_e210.py` case QS (above): reduce rc 0, collect COLLECTED, the re-frozen scorer rc 0; on the same copy the kitted reducer and the first freeze each exit 1 (fix-e210's record) |
| 3 minor: the sign tests take a pattern's two shapes as independent | E210.md A1 item 3: the scorer reports the pattern-level lines H1p-H4p; the brief's row 13 reads each BETTER beside its line | the scorer's self-test (registration) |
| 4 minor: the power table | E210.md A1 item 4 (B5 tests per-case fidelity to about 2-3% of D) | fix-e210's own simulation |
| 5 minor: R0 strict | E210.md A1 item 5: R0 reads the printed checks; a process that printed none is REPORTED by name (`R0` › `missing_REPORTED`); 4.22, the brief's row 13 and the README form name each | the scorer's self-test, cases Y5-Y8 |
| 6 note: the probe | E210.md A1 item 7; the README form says how a tripped probe is reported | - |
| 7 note: kappa and "the tensor unit's" | none (E210.md A1 item 8) | - |

**The registration's pins** follow A1: `rb/check_history_e210.py`'s and `rb/rb_e210.sh`'s registration subtree `adef3701...` (was `45b1b2d1...`,
never landed), step 2's REGPIN 523 entries (`4219474f...`), the history check's 524 files; the harness re-made (its line for the registration's
list); the kit's list `SHA256SUMS-e210-kit` re-made (45 entries) and KITPIN set. **The runbook test's own two fixes** (no runbook step changed):
case P2 reads the registration list's count instead of typing it (its first run here read 27 of 28: P2 typed the first list's 521); case NR reads
NR3's report before NR4 runs (step 6n names its folder by the second, and in the second run NR4 wrote into NR3's folder: 27 of 28).

**The fixed kit's desk tests, re-run** (one slot job inside the sandbox, 2026-11-17 07:23:01 PST to 07:43:39 PST; the runbook test, the dry
listing, the preflight and the quick set again 07:51:13-07:53:39 PST, after its two fixes, inside the sandbox AND a private PID namespace
(`bwrap --unshare-pid --proc /proc`, as the real-path test runs): the runbook test's stand-in aifoundry3 is this desk, so its ours_live counts
any session script of ours running here, and its third run (07:48:06-07:49:58) read 19 of 28 while verify-e209's stand-in `session_e209.sh`
processes ran on this desk from 07:49:19 (kit-e210's finding 2)): SELFTEST-RUN-E210 58 of 58 PASS; REALPATH-E210 14 of 14 PASS; REALBYTES-E210 10
of 10 PASS; DESKTEST-BUILD-E210 8 of 8 PASS; SELFTEST-RB-E210 28 of 28 PASS; the dry listing 16 steps, 0 non-zero, 0 box calls;
dmcmd_audit_v2 GO (11 READ sites); the quick set 11 lines (logs/). After that pass the re-frozen scorer's eight new self-test cases were renamed to Y1-Y8 (the public-text scans read three of their first labels as process names): eight label strings in its self-test, its score() unchanged (`42e26343...`, E210.md section 0; the pass above ran `28310245...`, identical but for those strings); the registration was re-committed and the runbook test, the dry listing, the preflight and the quick set were run again on it (their logs are those runs'), and the runbook test once more with the kit committed (28 of 28 each; fix-e210's record).

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), each test that runs a built host, the runner or a stand-in inside the
sandbox (W/nodev.sh; the real-path test in private UTS and PID namespaces): the runner's desk test (about 20 minutes, its three end-to-end
sessions the longest), the real-path test (one real build), the build's test (four real builds), the runbook's test (one real build), the
real-bytes test, the dry listing. On aifoundry3: read-only looks (seconds). No simulator run. kit-e210's final pass ran as one slot job inside the sandbox, 2026-11-17 01:25:22 PST to 01:45:51 PST (the runbook's test, the dry listing, the preflight's log and the quick set again 01:57:25-01:59:44 PST). **The logs now committed are fix-e210's** (section 9): the runner's, the real path's, the real bytes' and the build's from 07:23:01-07:41:09 PST; the runbook's, the dry listing's, the preflight's and the quick set's from 08:05:57-08:08:23 PST (on the registration as re-committed after the self-test labels' rename), inside a private PID namespace as well.

SPDX-License-Identifier: Apache-2.0
