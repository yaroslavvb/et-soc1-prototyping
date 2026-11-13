# E189's run kit: the blind day's runner in energy.sh's form with live stops, the two hosts built on the box and read from their BEHAVIOUR (never grepped from their bytes), the rest rule over every session-log form of ours, the runbook from the window to the scorer after the data commit (Q167; kitted, not run)

*Thu 12 Nov 2026 (week 46), PST, on the Intel, desk only (Q167, lane `kit-e189`); fixed before landing on Fri 13 Nov 2026 on aifoundry2
(Q168, lane `fix-e189b`: section 10, each change named by the verifier's fault or nit), and again after that fix's own verifier (Q168,
lane `fix-fix189`: section 10's second part). No card was claimed or opened (aifoundry2 has a
card: every desk test there that runs a built host, the runner or a stand-in session ran in a sandbox with no /dev/et* and an empty
/run/lock), no device command was sent, no other box was reached, nothing was posted, no Modal, no archive. New files only, all under
`tools/claims-v3/e189/`. The registration [`E189.md`](E189.md), as re-made before any datum (its tools/claims-v3/e189 subtree `993e549a...`;
`SHA256SUMS-e189-registration` `bf1b1bbb...`, 10 entries), and every file its list names stay as committed. This is the kit E189.md section
16 asks for ("What the kit must add"), in the lab's kit form (E186's and E188's kits; E183's kit note 4's behavioural build check; E188's
dated note 1's rest rule v2 and step 2 v2). No E189 datum exists. **Nothing here changes a forecast, a band, a rule, a threshold, K, the
order, the card time, the cap, a stop or the scorer.** Where E189.md leaves a reading to the kit, the reading is stated in section 4 before
any datum.*

## Results first (desk checks of code; nothing is measured)

Every test below was run again on Fri 13 Nov 2026 on aifoundry2 (Linux, /usr/bin/python3 3.12.3, g++-13 13.3.0, clang 18.1.3), each that
runs a built host, the runner or a stand-in session inside a sandbox with no /dev/et* and an empty /run/lock; every log was replaced
(section 10), and the runbook's, the rest rule's, the dry listing's, the checks' and the preflight's again after section 10's second part
(the hosts' and the runner's tests read no file that part changed, so their logs stand).

| check | result | log |
|---|---|---|
| **the host check on real builds**: the ledger host (46a16bd0) and sparse parity's host, each built by g++-13 at -O2 and -O3 and by clang++ at -O1 and -O2 (clang 18.1.3 here) against the desk's device-recording mock; four negative controls (the ledger host's budget refusal at 9.9 s, its guard model at 25 GB/s, its `--expect` never read; sparse parity's est_s margin x1.35) | **DESKTEST-HOSTS-E189 67 of 67 PASS**: both hosts read HOST-BEHAVIOUR OK on all four builds; every negative control reads FAIL on all four; each host read as the other program reads FAIL; no run left a device-record line; sparse parity's `--dry` line for E189's instance equals the committed one made by the box's build, byte for byte | [`logs/desktest-hosts-e189.txt`](logs/desktest-hosts-e189.txt) |
| **the runner's stop path and gates** (dry sessions with the doubles): each stop line tripped on a live sample (board 66 W, minshire[0] 70 C, one and two samples off 600 MHz), the die gate, the cap, a start config off TDP 0 W, a holder, a failed smoke, a SHORT burst, a FAILED RUN, a held lock, a program not built, the refusals without `--dry`, a dead sampler, the end bound (R18: a sampler that ignores its first SIGTERM; R19: the die gate held at 62 C, stopped at the cap); and end to end on energy_stub.py's alt card through the collection's desk half (COPY-BACK EXACT, the reducer unchanged, the scrub, SHA256SUMS) and the frozen scorer, **each pass's reduced J over idle checked against the energy the card injected** (fault 1) and the S1 and S2 words asserted; two stopped passes on the alt card (the board line, the die line) reduced and scored, and the cut tail they replace (fault 2) | **SELFTEST-RUN-E189 27 of 27 PASS**; the E2E's six passes read +2.5, +1.9, -0.7, -4.5, -11.7 and -2.5% of the injected J over idle (within TOL: copy 12.8%, SHA-256 22.3%, sparse parity 8.8%); S1 and S2 NOT DECIDED; the stopped passes -4.8% (R2E, copy) and -14.4% (R3E, SHA-256), each scored on its configuration's two passes; the same pass cut 0.5 s after its host reads 9.9% low, flagged | [`logs/selftest-run-e189.txt`](logs/selftest-run-e189.txt) |
| **the rest rule**: E184's, E185's, E186's (committed logs), E183's, E188's and E189's forms, cut sessions of E188's and E189's forms, energy.sh's output folders, dry and no-device logs, a shared day | **SELFTEST-REST-E189 21 of 21 PASS** | [`logs/selftest-rest-e189.txt`](logs/selftest-rest-e189.txt) |
| **the runbook** (a fake ssh and rsync, a stand-in box): the window rule, the lab-git lock (absent and nested), step 2 at every pin, the history check, the sync, the build read by the real hosts' behaviour, the negative control through the runbook, NO-THIRD-BUILD, a login link (11 and the lock line), a hang (13), a cut wait (14), the box's dry pass, the rest rule through step 9, the real session stopping at its gate, the wait, the collection and COPY-BACK EXACT; the shadow cases (H2-H4: the verifier's tools/ledger/struct.py, the 3.9 way, a package and copy.py; H5-H8, section 10's second part: an added json.py in the reducer's folder through step 2, re.py in tools/claims-v3/ and subprocess.py in v3.1/, _strptime.py at the lab clone's top, and the same names untracked or staged, not committed); on Linux the nested lock with flock and the real session's gate in a sandbox | **SELFTEST-RB-E189 21 of 21 PASS** (16 on the Intel before section 10's changes, 17 before its second part); on its way the first kit's run found and fixed three faults a dry listing cannot see (sparse parity's host includes `cpu/sp.h`, which the harness lacked; a quote inside `session_e189.sh`'s `${...:?}` word; a slash in the collection's value read); its first Linux run found two of the desk's own (section 10) | [`logs/selftest-rb-e189.txt`](logs/selftest-rb-e189.txt) |
| the dry listing, every step with stand-ins | 13 steps, 0 exiting non-zero, **0 box calls** (k6's unchanged `rb_common.sh` labels each desk call "run on the Intel" whichever desk lists it) | [`logs/dry-listing-e189.txt`](logs/dry-listing-e189.txt) |
| `dmcmd_audit`, the session's files (`preflight_e189.sh`: the runner, the wrapper, the build, the host check, E128's guard, both hosts' sources) | **GO**, 11 send sites, 0 disallowed, **every one a READ**, no allow-list and no exception | [`logs/dmcmd-audit-e189.txt`](logs/dmcmd-audit-e189.txt) |
| the common module's self-check, the harness, the host check's frozen lines, the registration's checks | E189-COMMON SELF-CHECK PASS (the written order, K, the commands, the adapter, the stop lines: the clock line in a pass only); harness-e189.json CHECK PASS, HARNESS OK; HOSTCHECK-JSON CHECK PASS; FORECAST and PLAN CHECK PASS; the scorer's E59 self-test PASS; NEVER RAN; the history check's shadow names derived (struct, ast, copy among them), read in eight folders | [`logs/checks-e189.txt`](logs/checks-e189.txt) |

- **The runner, energy.sh's form** ([`run_e189.py`](run_e189.py), [`session_e189.sh`](session_e189.sh)): one session on aifoundry3 card 0 holding
  card 0's lock (`flock -n`) to its end. The first card command is `ettelem config` through E128's guard (TDP 0 W, 65 C, minion 600 MHz, else
  no launch); then ONE sampler (`ettelem sample --every-ms 100`, no statistics reset) for the whole session, every line fed live to THE STOP
  LINES; the stop-path test; the ramped smoke; idle anchor 1, rounds 1-2, anchor 2, rounds 3-4, anchor 3 (`plan-e189.json`'s order, never
  re-drawn); each pass the die gate, 8 s of idle, ONE host process under `timeout 10`, 10 s of idle; the closing `ettelem config`; "session
  end"; the manifest last. The pass's files are E189.md section 8.1's: `telemetry.jsonl.gz` (the session's samples over the pass), the
  ledger host's own line `host-raw.json` and the ADAPTER's `host.json`, or sparse parity's own `host.json`, `host.err`, `run.json` (energy.sh's
  marks), `pass.json`. **The reducer is energy.sh's, `workloads/sparseparity/tools/energy_reduce.py`, unchanged, run at the desk at the
  collection; `energy.sh` itself is not used and not edited.**
- **THE HOSTS ARE READ FROM THEIR BEHAVIOUR** ([`hostcheck_e189.py`](hostcheck_e189.py), [`build_e189.sh`](build_e189.sh)): step 6 builds both
  programs on the box (cmake against `/opt/et`, into `build/e189ledger` and `build/e189spp`), checks each kernel by its ELF's and its
  `.text`'s sha256 against the pins Q166 recorded (ledger `78708041...` / `5e00e45a...`; sparse parity `65dd07da...` / `3e14be32...`, the 29 Sep
  card file), and each host by what it does: the ledger's FIPS self-test, its `--dry` line for each of E189's five ledger configurations with
  their K, its refusals (no device flag; `--budget 9.6`; `--launches 101`; an unreadable `--expect`); sparse parity's `--dry` line for E189's
  instance equal to the committed one, its refusal of an unknown option offering `--variant m4|m1`, and its CPU self-test. **No string is
  grepped from any binary anywhere in this kit**; energy.sh's own grep (`launch_epoch_ms`) is reported in the desk test's log, never used.
- **THE REST RULE** ([`rb/rest_rule_e189.sh`](rb/rest_rule_e189.sh)): E188's rest rule v2 (its kit's dated note 1) in E189's words, with
  energy.sh's output folders added (in every tree of ours on the box): no E189 launch within 40 minutes of the end of our last real session on
  aifoundry3, a session cut mid-queue counted at its run's latest file write, dry and no-device blocks skipped by the kits' own markers.
- **The runbook** ([`rb/`](rb/)): each step in the kits' form through k6's drivers, unchanged (a 15 s hard-killed probe; 60 s for a read,
  600 s for a copy, one bounded wait, a detached launch; a printed login link stops the step with 11 and appends `<HH:MM:SS> aifoundry3 needs
  a check` to `RB_LOCK`, nothing retried; exit codes 0, 10-17); the window written that day for E189; step 2's pull under the lab-git lock,
  taken by step 2 itself (never run step 2 inside that lock); every list pinned by count and bytes, lists found by "SHA256SUMS" anywhere in a
  name; the build counted per Pacific day; the scorer after the data commit only.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's inventory as E189.md section 15 read it (Thu 12 Nov 2026, about 21:25 PST): public rows L06, L08, L10, L11,
   H04, H15, P23, P27 (opaque pointers into a private inventory). Pieces newer than it are cited by commit: E188's kit (`726a6b64`) and its
   dated note 1 (`16b41cf2`), E183's kit note 4 (`24b9b99e`), Q166's programs (`46a16bd0`), its counter (`69e85905`) and ledger v2 (`06d60fa2`,
   `80eb3bdf`), E189's registration as re-made before any datum (its subtree `993e549a...`).
2. **Used** (each unchanged, called, sourced or imported by path; sha256 in [`SHA256SUMS-e189-kit`](SHA256SUMS-e189-kit) or the lists step 2
   pins):
   - **E188's kit** (the form of the runbook, the rest rule v2, step 2 v2's lock rule, the window rule, the desk tests) and **E183's kit note 4**
     (a build read by its behaviour, desk-tested on real g++-13 and clang builds with negative controls). *Check against the same operation:*
     the rest rule's desk test reads E184's, E185's and E186's committed session logs at their box paths and reproduces E188 v2's readings of
     them (RS1-RS3, RS8).
   - **k6's runbook drivers** (`tools/claims-v3/q141k-runbook/k6/rb_common.sh`, its look and reads; v3.1's `rb_run.py`, `nopath_q142s.py`),
     **E128's guard** (`tools/claims-v3/e128/ettelem_guard.sh`), **Q136(w)'s `dmcmd_audit.py`** and its table.
   - **energy.sh's form and reducer** (`workloads/sparseparity/energy.sh`, read; `tools/energy_reduce.py` and `tools/energy_stub.py`,
     unchanged): the pass's brackets, the sampler's rate, the reducer's inputs. *Check against an earlier measurement of the same quantity:*
     the scorer's E59 self-test reproduces scores-v2.json's E59 rows from E59's committed reductions (registered, PASS).
   - **Q166's programs** (`workloads/ledger/` at `46a16bd0`; sparse parity's host and kernel at `a768f840`): their sources built as committed,
     their recorded kernel hashes, the committed `--dry` line of E189's instance and the SHA-256 digests `--expect` reads.
   - **E189's registration**: `plan-e189.json` (K, the order, the stops, the die gate, the cap), `forecast-e189.json` (the doubles' launch
     times and watts only), `score_e189.py` and `stub_e189.py` (unchanged), each checked against its list by step 2.
3. **Not used:** any card but aifoundry3 card 0; energy.sh itself (its `grep` of a binary and its per-pass sampler); the counters arm (dropped,
   section 5); the host's package counter unless his go allows it; anything of the archive or the private tier; any refit.
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit.
5. **Readiness:** this block is the kit's. A verifier checks it against the inventory and the cited commits; a readiness critic gates the card.

## 1. The critic's list (Q166's critic, its design's section 6) and the week's lessons, item by item

| item | here |
|---|---|
| (a) no binary-string checks: hosts by behaviour, kernels by section hashes | `hostcheck_e189.py` and `build_e189.sh`; desk test on 24 real builds (g++-13 -O2/-O3, clang -O1/-O2) with four negative controls, no device call reached |
| (b) a rest rule that reads every session-log form; a session cut mid-queue ends at its run's latest write; 40 minutes | `rb/rest_rule_e189.sh` (E188 v2's, plus energy.sh's folders); desk cases for E184's, E185's, E186's, E183's, E188's, E189's and energy.sh's forms (`rb/selftest_rest_e189.sh`) and through step 9 (`rb/selftest_rb_e189.sh` RS, LA) |
| (c) step 2 pins every list by count and bytes, and the frozen files by sha256 | `rb/s03_desk_e189.sh`: the registration's list (10), Q166's progs (165), the ledger v2's (17, 6), the counter's (86) and the kit's own list, each at its count and its own sha256; the registration found by its content; lists found by "SHA256SUMS" anywhere in a name |
| (d) the smoke gate and the reduction read with one reader | the smoke's gate is each program's own check (status PASS, every output checked); every pass is reduced by the one reducer, at the collection; no second reader exists |
| (e) a gate-stopped session's files are collected | step 10 says 16 with the manifest written; step 11 collects it (desk case LA, C) |
| (f) a one-Pacific-day window from the go; never two sessions of ours on aifoundry3; 40 minutes after E183 | `rb/s02_window_e189.sh`; k6's guard (`ours_live`, `jobs_live`) in steps 5, 6, 8 and 9; the rest rule |
| (g) a build-attempt count per Pacific day (NO-THIRD-BUILD) | `rb/s08_a3_build_e189.sh` with `build/e189-build-attempts.txt` (desk case T) |
| (h) K from the guard's arithmetic; a burst cut short never read as the program failing | K as registered (`plan-e189.json`); the ADAPTER marks a budget-cut burst "reps: k of K done" (the reducer flags it, the scorer reads SHORT) (desk cases R11, adapter self-check) |
| (i) SHA-256 always with `--expect` | `e189_common.host_argv` from `plan-e189.json` (its args carry `--expect`); the smoke's SHA-256 too; the scorer refuses a pass without every participant checked |
| (j) dmcmd_audit GO; the ledger host opens the ops node only; every command a READ | `preflight_e189.sh`: GO, 11 sites, every one READ (section 7) |
| (k) a desk dry pass with stubs that never opens a device or runs ssh, the alt stub card among them | `run_e189.py --dry` (the doubles and energy_stub.py's alt sampler): the runner's desk test, its end-to-end case, and step 8 on the box |
| (l) load_guard calm or warm before each check and step 2 | the card lane's brief, step 0 and step 2 |
| (m) the never-run check at the freeze's head | step 2 (`spp_never_ran.py`, Q166's progs folder left out, as registered): NEVER RAN |
| (n) every sample at 600 MHz: one off sets its pass aside, a second stops the session | THE STOP LINES (`e189_common.Stops`), live, counting the samples taken in a pass as E189.md 11 words it (section 4; desk cases R4, R5 and the common module's self-check) |
| (o) heat carries over: each launch gated on the die | the die gate before each pass (60 C, 10 minutes; desk case R6) and before each smoke run |
| E183's kit note 4 (a box build read by its behaviour, never a grep) | as (a), and through the runbook with a real GCC -O2 build (desk cases S, U) |
| E188's dated note 1 (the rest rule v2; step 2 v2's lock) | as (b); step 2 takes the lab-git lock for its pull only, and a nested step 2 stops with 16 (desk case N) |

## 2. Card-minutes and the cap (registered; unchanged)

About 95 card-minutes (12 + 6 + 50 + 6 + 20 = 94), **cap 110**: no pass starts after 108 card-minutes from the first card command. The counters
arm's 6 card-minutes go unused (section 5). The post: **'for 2 h'** alone, **'for 4 h'** after E183 the same day.

## 3. The order on aifoundry3, and the box steps

E189 runs alone on aifoundry3 card 0, after E183 on any shared day, never while another session of ours runs on the box; `et-who` clean; an idle
login does not block (the owner's ruling of 1 Nov 2026). Run from the lab clone, each step with this day's `RB_OUT` (outside the repo, E189's
own), the one `RB_LOCK` and, for step 2, `RB_GITLOCK`. The card lane's brief is [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md).

| box step | file | what |
|---|---|---|
| 0 | (by hand) | `check_day2_v2.py tree --pull` under the lab-git lock, E189's anchor lines, `load_guard --status` calm or warm |
| 1, the window | [`rb/s02_window_e189.sh`](rb/s02_window_e189.sh) `<day> <last start> <last end>` | FIRST; today's day only |
| 2, the desk check | [`rb/s03_desk_e189.sh`](rb/s03_desk_e189.sh) | the window; the pull under the lab-git lock; ancestry; the paths clean; the history check; every list at its pins; the harness; the host check's lines; the registration's checks; NEVER RAN; the preflight; the desk tests' logs |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged |
| 3, the post, after the look | (the card lane's) | `using aifoundry3 for 2 h, until ~HH:MM PST [doc](...)` (or 'for 4 h' after E183) |
| 5, the sync | [`rb/s07_a3_sync_e189.sh`](rb/s07_a3_sync_e189.sh) | the box read first, then harness-e189.json's files |
| 6, the build | [`rb/s08_a3_build_e189.sh`](rb/s08_a3_build_e189.sh) `start`, then `wait` while it says 17 | the detached job; LEDGER-BUILT / SPP-BUILT by the kernels' hashes and the hosts' behaviour; RB_OUT/e189-built.txt; the harness with the kernels, the preflight and the self-check read on the box |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's, unchanged (TDP 0 W / 65 C / 600 MHz, et-who clean) |
| 8, the dry pass | [`rb/s10_a3_dry_e189.sh`](rb/s10_a3_dry_e189.sh) `start`, then `wait` | the runner on the box with its doubles, no device |
| 9, the session | [`rb/s11_a3_session_e189.sh`](rb/s11_a3_session_e189.sh) `FULL [--rapl-allowed]` | the guard, THE REST RULE, today's dry pass and build, then `session_e189.sh` detached |
| 10, the wait | [`rb/s20_wait_e189.sh`](rb/s20_wait_e189.sh), while it says 17 | the T0 the runbook launched; the manifest written |
| 11, the release, then the collection | [`rb/s22_collect_e189.sh`](rb/s22_collect_e189.sh) | one read-only copy back, COPY-BACK EXACT, the data directory, the reducer (unchanged), the scrub, SHA256SUMS, the desk-path gate, the history check |
| 12, the data commit | (the card lane's, through the lab's commit script) | `docs/reports/data/<day>-e189-blind-day-aifoundry3/` |
| 13, the scorer, after the data commit | [`rb/s24_score_e189.sh`](rb/s24_score_e189.sh) | `score_e189.py` (registered, unchanged) on the committed data; its output to RB_OUT, committed by the records lane |

No read-only records step is needed for E189 on its own: E189 has never run on the box and builds into its own directories. On a day E183 runs
first, E183's own step 5a copies E183's records before E183's build, as E183's kit says.

## 4. The readings stated here before any datum (where E189.md leaves a choice to the kit)

- **The clock line, as E189.md 11 words it** (fixed Fri 13 Nov 2026, nit 1; the first kit counted every session sample, the stricter
  reading, without a dated amendment). Only the samples taken in a pass count; a pass is the runner's whole pass, from its first idle
  second to its last. The first sample off 600 MHz in a pass sets that pass aside; a second one, in that pass or any later one, stops the
  session. A sample off the clock outside a pass (the smoke, an idle anchor, between passes) is recorded in queue.json's `off_clock`
  (`counted` false) and reported, and sets nothing aside and stops nothing; every scored pass is still guarded by the reducer's own hard
  check (every busy sample at 600 MHz). A sample with no clock reading does not count (the reducer flags it). The stop-path test feeds its
  test line as a pass's, so its clock line trips on live samples.
- **A stop during a pass** (fixed Fri 13 Nov 2026, fault 2). The running host process finishes and is never killed; **that pass's 10 s of
  idle after the host then runs to its end** (no launch happens in it: only the sampler reads, the card idle), and the pass keeps its data,
  flagged "a stop line tripped during this pass" (reported); nothing further starts; the closing reads follow. This is what E189.md
  already implies: section 9 makes a pass "8 s of idle, ONE host process (a burst of K launches), 10 s of idle", section 11 says on a stop
  "the running process finishes (a device process is never killed), nothing further starts", and section 12 that "the passes done are
  scored": a pass whose
  host ran is done, and is scored in its registered form. Setting it aside instead would drop a pass section 12 scores. The first kit's
  runner returned from that idle at once on a stop, so the pass's telemetry ended about 0.5 s after its host and its J over idle read
  short by the SP average's tail: on the alt card the same stopped pass cut there reads 9.9% low (flagged "telemetry ends 5.5 s before
  the long window does"), whole it reads -4.8% of what the card injected (desk cases R2E and R3E reduce and score such a pass).
- **The smoke.** Any smoke run that fails, or a stop during the smoke, ends the session at the gate (E189.md section 12: no session).
- **The die gate** is read on the session's latest live sample before each pass and each smoke run: at or below 60 C, waiting at most 10
  minutes and never past the cap (the end bound, below), else that pass is skipped (no data); a die below 52 C is labelled in pass.json,
  never a block.
- **The cap and the window.** A pass starts only within 108 card-minutes of the first card command (the start `ettelem config`) and at least
  150 s before the window's last end; an idle anchor only if it ends within 108 card-minutes.
- **The end bound** (E189.md 10: "so the session ends by 110"; fixed Fri 13 Nov 2026, nit 3, and a fault found beside it). The last pass's
  start check is at 108:00 at the latest; et-who then takes at most 30 s (the runner's bound; `timeout 20` inside), the idle before 8 s,
  the host at most 30 s (the runner's bound; `timeout 10` inside) and the idle after 10 s: that pass ends by 109:18. **The die gate stops
  waiting at the cap** (its wait of up to 10 minutes could start at 107:59 in the first kit and run to about 118: not in the verifier's
  list, found here), and no sampler is restarted once no pass can start. The closing then waits on the sampler (SIGTERM, 30 s, then once
  more, 60 s) only until 15 s before 110:00 (each wait at least 2 s), and the closing config read has those 15 s (its own `timeout 10`):
  the session's last card command ends by 110:00. **What follows it sends no card command** (stated Fri 13 Nov 2026, fix-fix189,
  verify-fix189's nit 5; no rule and no code changes): the runner, still holding card 0's lock, compresses the session's telemetry
  (`telemetry.jsonl` read whole and written through gzip at its default level, 9), writes queue.json, logs "session end", releases the
  lock and writes MANIFEST.sha256. A full session's telemetry is 110 minutes of the 10 Hz sampler, 66,000 lines of about 705 B
  (46.5 MB): its compression took 0.32 s in each of five trials of the runner's own two lines on aifoundry2's i5-11600, on E186's
  committed sampler lines (a desk timing of code, not a measurement of the box; 46.5 MB became 1.0 MB), and the manifest's hashes take
  milliseconds; so "session end" and the lock's release come well under a second after the closing read. The first kit's closing waited 30 + 60 s whatever the time:
  about 110.8 at worst by the verifier's arithmetic. Desk cases R18 (a sampler that ignores its first SIGTERM: closed 9.2 s after the first
  card command under a 20 s desk bound) and R19 (the die gate held at 62 C: the wait stopped at the desk's cap, the session closed in 8.1 s).
- **One sampler for the session.** The sampler runs from after the start config read to before the closing one (the management node is held
  by one process at a time); a pass's telemetry is the session's samples from its first idle second to its last; a dead sampler is restarted
  (lib.sh's six attempts) while a pass could still start, and a session whose sampler will not start launches nothing.
- **The adapter** (E189.md 8.1's, `e189_common.adapt_ledger`): `reps_done` = launches, `reps_requested` = K, `launch_s` = `wall_s`,
  `launch_epoch_ms` = [the first launch's t0, the last launch's t1], `status` as the host said it; a burst the budget cut short with every other
  check good: `problems` ["reps: k of K done"] (SHORT, scored); any other FAIL: `reps_consistent` "bad" (a FAILED RUN, not a datum);
  `kernel.cycles_max` = `hart0_cycles.max`. The host's CPU time is the process's (getrusage of the children), as energy.sh's `times`.
- **The reducer's "dir"** field (the path of the folder it read) is set at the collection to the pass's path in the repository: the reducer
  itself is not changed. The box's home path becomes "~" in every collected text file, and the collection refuses any /home/ path left.
- **The build's re-run.** At most two starts a Pacific day; a second start only when the first built fewer than both programs (it rebuilds
  both); a program not built that day is SKIPPED (no data).
- **The host's package counter** is read only with `--rapl-allowed` (his go), and only if our own user can read it (never with raised privileges).

## 5. Dated kit note, Thu 12 Nov 2026, before any datum: THE COUNTERS ARM IS DROPPED

E189.md section 7 keeps the counters arm (a ledger-kernel variant reading `hpmcounter4`-`hpmcounter6` and calling system calls 9 and 10 after
start and end barriers; reported only) **only if its desk test passes**: the variant builds, its counter reads and system calls complete in the
simulator on every shire, its barrier holds, its program output still checks, and its added instructions are counted by `tools/counter`. This
kit wrote no such variant and ran no such test (no build or simulator run was made for it), so the test did not pass, and by section 7 the
arm is **dropped**, never improvised: the session never runs it (its log says so), and its 6 card-minutes go unused. Its frozen expectations
stay in `forecast-e189.json`, unused.

## 6. Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `e189_common.py` | the configurations' commands, the ramped smoke, the written order, THE ADAPTER, THE STOP LINES, the cap and the die gate | `plan-e189.json` |
| `run_e189.py`, `session_e189.sh` | the session runner (energy.sh's form, the live stops) and its detached wrapper | energy.sh; E188's session form |
| `fake_card_e189.py` | the doubles: config, et-who, an injecting sampler, the two hosts | energy_stub.py's form |
| `hostcheck_e189.py`, `hostcheck-e189.json` | the hosts read by their behaviour; the frozen expected lines and the kernels' pins | E183's kit note 4; Q166's BUILD-INFO and kernel.sha256 |
| `build_e189.sh` | the box build, its kernels' hashes and its hosts' behaviour | the programs' READMEs |
| `check_e189.py`, `harness-e189.json` | every file the box runs or reads, at its sha256 | E188's harness |
| `preflight_e189.sh` | dmcmd_audit on the session's files | E188's preflight |
| `collect_e189.py` | COPY-BACK EXACT, the data directory, the reducer (unchanged), the scrub, SHA256SUMS (exercised end to end by the runner's desk test) | E188's collector |
| `selftest_run_e189.py` | the runner's desk test (the stop path and every gate, the end-to-end case) | E188's stops test |
| `desk/desktest_hosts_e189.sh`, `desk/mock_rt_e189.cpp`, `desk/include/` | the hosts' desk test on real builds; the device-recording mock and its headers | E183's and E188's desk tests; the check of C's mock headers |
| `rb/` | the runbook's steps, the rest rule, the history check, the dry listing, the desk tests, the stand-in cmake | E188's runbook; k6's drivers |
| `CARD-LANE-BRIEF.md` | the card lane's brief for the day | E188's brief |
| `logs/` | every check above | |
| `SHA256SUMS-e189-kit` | the kit's files (step 2 aside), its logs and the unchanged files it calls | |

## 7. Device commands

`dmcmd_audit.py` on the session's file set (`preflight_e189.sh`): **GO, 11 send sites, 0 disallowed, every one a READ**, with no allow-list and
no exception: `ettelem config` (TDP level, temperature thresholds, power state, the ASIC's frequencies and voltage) and `ettelem sample`
(module power, SP statistics, temperature, the ASIC's and the module's voltage, frequencies), both through E128's guard, which refuses
`--reset-ms` and every other word before the device opens. The two hosts open the ops node only. No set, no reset, no statistics reset, no
firmware query of any kind, no power cycle and nothing near card 0's 75 W alarm.

## 8. What the desk cannot show (for the verifier and the readiness critic)

1. **The two programs' first build on the box** is step 6 there: the kernels' hashes and the hosts' behaviour are read against the box's own
   `/opt/et`. Q166 rebuilt both kernels on aifoundry3 to the same bytes; the hosts' `--dry` lines were checked on four desk builds only.
2. **The ledger programs' card path has never run** (E189.md section 14): the smoke is its first, ramped (64 MiB before 1 GiB).
3. **The runner has run only with its doubles** (the desk and, on the day, step 8): the live sampler, the card lock, et-who and the real hosts
   meet it first in the session.
4. **The collection** has run on a gate-stopped session staged by the runbook's desk test and on the doubles' passes, not on a card's.
5. Card time waits on his go, after E183's on any shared day (`CARD-LANE-BRIEF.md`).
6. **SHA-256's slow end leaves about 0.3-0.4 s under `timeout 10`** (nit 5; stated, not widened). `plan-e189.json` puts the process's end at
   9.29 s at the band's slow end: 0.4 s of set-up, 9 launches of 0.9447 s with their gaps (8.59 s), and 0.3 s after the launches. That
   0.3 s leaves out the host's own SHA-256 check: main.cpp hashes on the CPU, after closing the device, a sample of 64 participants when the
   messages pass 2^30 bytes in all (here 3.36 GB): 64 x 1.6384 MB = 104.9 MB. Its own code (the Sha256 struct of main.cpp at its pin, g++-13
   -O2 as the host is built, single-threaded) takes 0.330-0.387 s for that on aifoundry2's i5-11600 (five trials, about 300 MB/s, under a
   load of about 5; a desk timing of code, not a measurement of the card; aifoundry3's CPU is the same generation). So at the slow end the
   process may end at about 9.6-9.7 s: a margin of about 0.3-0.4 s. A cut there holds no device past 10 s (the device is already closed),
   but loses the host's JSON line: that pass is a FAILED RUN (no datum, never a failed prediction), reported. At the point (0.5704 s a
   launch) the process ends at about 6.2 s. No kit file can widen the margin: K, the arguments and the host's budget are registered
   (`plan-e189.json`), the host is Q166's at its pin, and `timeout 10` around every device-opening process is the lab's rule.

## 9. Labels

Every figure quoted from E189.md and its files (the forecasts, K, the order, the caps, the stops, the pins) is **registered**. The desk tests'
results are **desk checks of code**, not measurements; the end-to-end and stop cases' joules (E2E, R2E, R3E, the cut-tail control) and
their rule words come from the doubles (energy_stub.py's alt card driven by the doubles' launches): not a measurement, and not a reading
of E189; section 8's 0.33-0.39 s is a desk timing of the host's own code on aifoundry2's CPU, not a measurement of the card, and section
4's 0.32 s a desk timing of the runner's own closing compression there, on E186's committed sampler lines.
Nothing here is **blind** or **held out**, and no E189 datum exists. Q166's labels, where a file here leans on them, are its corrected ones
(E189.md section 3).

## 10. Changes before landing (Fri 13 Nov 2026, fix-e189b; its second part, fix-fix189)

*On aifoundry2 (Q168, lane `fix-e189b`), before any E189 datum, desk only (the header's conditions). The verifier, verify-e189 (Q167),
read the first registration and kit and found four minor faults and five nits; each is answered below, in a kit file or in the
registration as re-made before any datum. No forecast, band, given() formula, arm, rule, threshold, K, order, card time, cap, stop or
scorer changed.*

| verify-e189 | what it found | what changed |
|---|---|---|
| fault 1 | the end-to-end case could not check joules: the doubles announced each launch at its end, so the alt card saw only 26-33% of a launch's energy, and any verdict word passed | `fake_card_e189.py` announces each launch at its start, as `energy_stub.py`'s own host double does. `selftest_run_e189.py`'s E2E checks each pass's reduced J over idle against the energy the alt card injected, within TOL(c) = 3% + 0.33 W/C x (K t_point + 7 s) / (K J_point): the reducer's own 3%, plus one whole degree of the die reading at its leakage slope near 55 C over the long window [lo - 1 s, hi + 6 s], as a share of the burst's injected energy (copy 12.8%, SHA-256 22.3%, sparse parity 8.8%; the verifier's own scratch fix read -13.0% to +1.2%). It reads +2.5, +1.9, -0.7, -4.5, -11.7 and -2.5% here. The case fails unless E189-S1 and E189-S2 read NOT DECIDED: by construction t_k is the point and J over idle the point, and with three configurations scored and three NO DATA that is the injected values' word (PASS needs 5 scored, FAIL 2 outside). S1T's and S2T's words carry no information there (here FAIL and NOT DECIDED): the alt card idles about 2 W below the footing law the forecast's rest term uses |
| fault 2 | a stop during a pass skipped that pass's 10 s of idle after, yet the pass was kept and scored | `run_e189.py`: the idle after a host process runs whole whatever the stop lines say (section 4, with E189.md's grounds). New desk cases R2E and R3E (the verifier's R2/R3 shapes, on the alt card under the injections, `E189_FAKE_BASE=alt`) reduce and score the stopped pass: -4.8% and -14.4% of the injected, each scored on its configuration's two passes; a control cuts the same pass where the first kit cut it: 9.9% low, flagged. R2 and R3 now also check the stopped pass's idle after |
| fault 3 | S2's 15% had two readings | answered in the registration as re-made (E189.md 8.3: 0.85 <= mean t_k / point <= 1.15, the frozen scorer's own test; its e_t does not decide S2). No kit file changes |
| fault 4 | SHA-256's fast end (0.385 s) and sparse parity's (0.463 s) lie under the 0.5 s the sort was sized by | answered in the registration as re-made (E189.md 5.1: the reducer meters the burst, 3.5 and 4.2 s there). No kit file changes |
| nit 1 | the kit counted every session sample toward the clock line; E189.md 11 says "in any pass" | the kit follows the registration: `e189_common.Stops` counts the samples taken in a pass (section 4); the common module's self-check has the cases (outside a pass: recorded, not counted) |
| nit 2 | the history check's shadow list missed struct, ast and copy | `rb/check_history_e189.py` derives the names. On Python 3.10 or later: sys.stdlib_module_names and the built-in modules. On 3.9 (the Intel's /usr/bin/python3 3.9.6, which runs step 2 there): every module file and package in that interpreter's own standard-library directories, its lib-dynload, and its built-in and frozen modules; on 3.12 that way misses no importable standard-library module. It flags module files, extension modules and regular packages. Runbook desk cases H2-H4: the verifier's tools/ledger/struct.py (step 2 stops with 16; the 3.9 way also fails it), a package tools/ledger/ast/ and workloads/ledger/copy.py |
| nit 3 | the session could end at about 110.8, not by 110 | the end bound (section 4): the closing's waits end 15 s before 110:00; the die gate's 10-minute wait now stops at the cap, which could otherwise have ended the session near 118 (found here); desk cases R18 and R19 |
| nit 4 | "never run" should say "on a card" | in the registration as re-made (E189.md 1, 4 and 4.2) |
| nit 5 | SHA-256's slow end leaves about 0.4 s under `timeout 10` | stated in section 8 with the numbers (the host's own check timed on the desk); no kit file can widen it, for the reasons there |

Beside them:
- **The registration re-made.** E189.md was re-frozen before any datum (subtree `993e549a...`, list `bf1b1bbb...`, 10 entries; only E189.md and
  its list differ from the first freeze). The kit's pins follow it: `rb/rb_e189.sh`'s E189_REG_SUBTREE, `rb/check_history_e189.py`'s
  REG_SUBTREE, step 2's registration-list pin, CARD-LANE-BRIEF.md's anchor line; and the kit list and step 2's own pin are made again.
- **THE PORT: the kit runs from aifoundry2 (Linux) as well as from the Intel (macOS).** `rb/rb_e189.sh`'s pull takes the lab-git lock with
  `/usr/bin/lockf -k -t` where it exists, else `/usr/bin/flock -w ... -E 75`: the same exit 75 on a timeout, so a nested step 2 still stops
  with 16 (runbook case N, run on Linux with flock). `rb/selftest_rb_e189.sh` and `rb/selftest_rest_e189.sh` take GNU date as gdate or as
  date (checked to be GNU's) and the lock tool as lockf or flock; every BSD `sed -i ''` (`rb/fake_cmake_e189.sh`, `rb/selftest_rb_e189.sh`)
  became a portable copy written back. Runbook case LA accepts a Linux sandbox's gate: on the Intel the real runner stopped at the missing
  /run/lock; in the sandbox it stops before any launch at its start config (the stand-in box has no ettelem), and no smoke run starts. The
  runbook test's first Linux run (11 of 17) found two faults of the desk's, not of the kit's: the stand-in box runs on the desk, and Linux's
  pgrep, unlike macOS's, counts its caller's ancestors, so the box's ours_live read found the desk's own step 9 script
  (`s11_a3_session_e189.sh` holds "session_e189.sh") and refused RS and LA, and C and C2 after them (the stand-in box now has a pgrep
  that leaves its caller's ancestors out; on a card day that script runs on another machine); and the scratch clone's own `main` sat at
  the first kit's commit, so the test repository's pull diverged (P1, P4: the fixing lane's scratch clone, not the lab's). Step 11's
  desk-path gate (v3.1's nopath, which forbids the desk's own home) passes from aifoundry2 as well, although aifoundry2's home and
  aifoundry3's share one /home/<login> prefix (the reason E183's collection stops there: port-e183's finding): E189's collection replaces
  the box's home with "~" in every text and .gz file and refuses any /home/ path left before that gate runs (runbook case C, run on
  aifoundry2 with the stand-in box's home under the desk's). A grep
  of the kit for other macOS-only forms (stat -f, date -v or -j, /usr/local/bin, BSD find or xargs flags, mktemp -t, base64 -D, tail -r,
  grep -P, bash-4-only forms) found none on a card day's path; k6's `rb_common.sh` (unchanged) uses portable forms on the desk. **E188's
  two open ports, found here, reported, E188 not edited:** its step 2 v2 still calls /usr/bin/lockf, so on Linux it stops at its pull; and
  under aifoundry2's /usr/bin/python3 3.12.3 its forecast check reads CHECK FAIL, because forecast-e188.json keeps unrounded floats and 16
  of its lines differ in their last digit there (for example `M10_w` 8.233099847174708 against 8.23309984717471; its .txt agrees). E189's
  forecast rounds to 6 significant digits and passes there byte for byte.
- **The logs** under `logs/` were all made again on aifoundry2 (Linux, /usr/bin/python3 3.12.3 with numpy 1.26.4, g++-13 13.3.0, clang
  18.1.3), each desk test that runs a built host, the runner or a stand-in session inside the sandbox; the registration's own checks also
  pass there under 3.12.3, byte for byte.

**The second part (Fri 13 Nov 2026, fix-fix189).** *On aifoundry2 (Q168, lane `fix-fix189`), before any E189 datum, desk only (the
header's conditions). The changes above had their own verifier, verify-fix189 (Q168), which held them with fixes: one minor fault and four
nits, none in a forecast, band, given() formula, arm, K, the order, the card time, the cap, a stop, a threshold, a verdict rule or the
scorer. Each is answered below. E189.md and every file of the registration stay as frozen (subtree `993e549a...`, list `bf1b1bbb...`).*

| verify-fix189 | what it found | what changed |
|---|---|---|
| finding 1 (minor) | the history check took its shadow candidates from the additions on its PATHS, which name two files of `workloads/sparseparity/tools/` (`energy_reduce.py`, `energy_stub.py`), not the folder, although SYSPATH_DIRS lists it; `collect_e189.py` runs the reducer without -I, so that folder is first on the reducer's sys.path for every pass's J. An added `workloads/sparseparity/tools/json.py` (or `gzip.py`) read HISTORY OK both ways, the reducer imported it, and step 2 exited 0 | `rb/check_history_e189.py` reads its candidates from the folders themselves: a second `git diff --name-status --no-renames <base> HEAD -- <SYSPATH_DIRS>` (the files it lists as added) and `git status --porcelain --untracked-files=all -- <SYSPATH_DIRS>` (untracked, or staged as new: "a shadowing file not committed" fails too). Runbook desk case H5: an added `workloads/sparseparity/tools/json.py`; step 2 stops with 16 by the history check, which names it, and the 3.9 way fails it too. Case H8: an untracked `workloads/sparseparity/tools/gzip.py` and `tools/claims-v3/re.py` and a `_strptime.py` staged as new: HISTORY FAIL naming all three; then HISTORY OK on the clean tree. The reducer's call is unchanged: `-I` implies -s, which drops the user's site-packages, where numpy (which the reducer imports) may live for a desk's /usr/bin/python3; that cannot be checked for the Intel from aifoundry2, and the check now covers the folder |
| nit 2 | SYSPATH_DIRS left out `tools/claims-v3/` (`preflight_e189.sh` runs `dmcmd_audit.py` there without -I) and `tools/claims-v3/q141k-runbook/v3.1/` (k6's `rb_common.sh` runs `rb_run.py` and `nopath_q142s.py` there with -B only): an added `re.py` or `subprocess.py` there read HISTORY OK and was imported | both folders are in SYSPATH_DIRS, read by the second diff and the status above. Runbook desk case H6: an added `tools/claims-v3/re.py` and `v3.1/subprocess.py`: HISTORY FAIL naming both. **Found beside it, and closed the same way:** step 1 (`rb/s02_window_e189.sh`) runs its window script on stdin (`"$RB_PY" -B - ...`) from the lab clone's top, so its sys.path[0] is '' (the current directory), and `time.strptime` imports `_strptime`. A desk check: that script's own text, run in a scratch folder holding a `_strptime.py` that announces itself and exits 97, exited 97. The top is the eighth folder (its pathspec "."; only a module file directly in it, or a package directly under it, counts); case H7: an added `_strptime.py` at the top: HISTORY FAIL naming it. Step 1 runs before step 2, so such a file would reach step 1 and be refused at step 2, which ends the day. The check's own text lists the eight folders and what puts each one first |
| nit 3 | the re-made E189.md differs from the first freeze in one more place than its Re-made paragraph names | the dated sentence below; E189.md not changed, not re-frozen |
| nit 4 | E189.md 4.2's "the only runs of it, three 1/20,000 slices" leaves out a fourth simulator run | the dated sentence below; E189.md not changed, not re-frozen |
| nit 5 | section 4 said the session "closes by 110:00 and writes its manifest in well under a second", but the runner compresses the whole session's telemetry at gzip's level 9 before "session end" and the lock's release; the verifier estimated seconds for 40-46 MB | stated in section 4 with a desk timing of the runner's own two lines on E186's committed sampler lines: a full session's 46.5 MB took 0.32 s in each of five trials (it compresses to 1.0 MB), so "session end" and the lock's release still come well under a second after the closing read, the last card command, which ends by 110:00. No code and no rule changed |

- **Dated Fri 13 Nov 2026 (fix-fix189), before any E189 datum: E189.md's Status sentence** (verify-fix189's nit 3). Besides the three
  changes its "Re-made before any datum" paragraph lists, the re-made E189.md also changed its Status sentence: before the registration,
  E189 was named "only as proposed or as work under way", citing beside Q167's records (8fe0c75e: "proposed, not registered yet") their
  fix, f9632ee3: "not yet done". The citation is accurate (f9632ee3's `docs/findings/05-claims.md`: "Not yet done: E189's registration,
  kit, verifier, fix and readiness check"). The Re-made paragraph's "Nothing else changed" is to be read with this sentence: no forecast,
  band, rule, threshold, K, order, card time, cap, stop or verdict rule moved, and E189.md stays as frozen.
- **Dated Fri 13 Nov 2026 (fix-fix189), before any E189 datum: E189.md 4.2's "the only runs of it"** (verify-fix189's nit 4). Q166's progs
  folder holds four simulator runs of the never-run instance, of three slices: `runs/p2-new-s0`, `-s10000` and `-s19999` (three
  1/20,000 slices for Q166's counts), and `runs-fixq166/p2-new-s0-nbuf1`, slice 0 run again with `--nbuf 1` by Q166's fix lane (its
  `COMMANDS.txt`, line 10; the folder's README, `runs-fixq166/`). "Never run on a card" holds, and the never-run check (that folder left
  out, as registered) is unchanged.
- **The pins** made again: the kit list `SHA256SUMS-e189-kit` (55 entries, the same files) and step 2's KITPIN; the registration's pins
  are unchanged.
- **The logs** made again on aifoundry2: the runbook's (21 of 21), the rest rule's (21 of 21; it reads the runner's dry session log of
  the first part), the dry listing's (13 steps, 0 non-zero, 0 box calls), the checks' (the history check's names, now with its eight
  folders; harness-e189.json re-made unchanged) and the preflight's (GO, 11 send sites, every one a READ). The hosts' (67 of 67) and the
  runner's (27 of 27) logs stand from the first part: no file they read changed.

## Compute

On aifoundry2 for section 10's changes (Fri 13 Nov 2026), through the round's local slot (`slot.sh`, nice 10), one job at a time: the
runner's desk test (about 11 minutes, three alt-card sessions with the registered idles among it), the hosts' 24 builds, the rest rule's
stand-in trees, the runbook's desk test, the dry listing, and a desk timing of the host's own SHA-256 code. aifoundry2 is a lab box with a
card: every one of those that runs a built host, the runner or a stand-in session ran inside a sandbox with no /dev/et* and an empty
/run/lock, so its card and its lock were never opened; no other box, mini or bench job was used. For section 10's second part, the same
way: the runbook's desk test (about 2 minutes), the rest rule's, the dry listing, the checks, a desk timing of the runner's closing
compression, and the shadow cases on side branches. Before that, on the Intel through its
local slot, one job at a time, at nice 10: 24 host builds and a self-test build for the hosts' desk test (a few minutes), the runner's dry
sessions, the rest rule's stand-in trees, the runbook's desk test (a shared sparse clone, a stand-in box, three rounds of g++-13 -O2
builds of both hosts); no bench job, mini, lab box or card. The desk tests wrote only under the round's scratch.

SPDX-License-Identifier: Apache-2.0
