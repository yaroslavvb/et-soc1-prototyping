# E191's run kit: the blind day's runner on aifoundry1 card 1, ET_DEVICES=1 for every device process, the identity gate before the first launch and the watch at every launch, the runbook from aifoundry2 in E189's form with the look on both cards, and the defects E189's real day showed fixed as kit mechanics (Q178; kitted, not run)

*Sat 14 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q178, lane `kit-e191`). **Written after E189's data commit `fa9098c4`
(Sat 14 Nov 2026, 20:34:12 PST)**, so by E191's dated note 1 section 3 it registers only the kit's mechanics (how a registered step is
carried out) and stops and gates made stricter for safety, each named as such in section 4; **nothing here changes a forecast, a band, a
rule, a threshold, K, the order, the plan, the card time, the cap, a registered stop line or the scorer**, and nothing here reads E189's
measured numbers for any of them. **Changed in place before the land** by lane `fix-e191k` (Sat 14 Nov 2026, 22:39 PST on) after the
kit's verifier, `verify-e191k`, read it DOES NOT HOLD (1 major, 4 minor, 6 nits): section 1's verifier table names each finding and its fix,
all kit mechanics or gates made stricter for safety, none a registered number. **Changed in place again before the land** by lane
`fix-e191k2` (Q180, Sun 15 Nov 2026, 00:46 PST on) after the second verifier, `verify-e191k2`, read it HOLDS WITH FIXES (0 major, 0
minor, 6 nits): section 1's last table names each nit and its fix, again kit mechanics or gates made stricter for safety, none a
registered number. No card was claimed or opened (aifoundry2 has a card: every desk test that ran a host, a runner, a stand-in session or a
stand-in box ran in a sandbox with no /dev/et* and an empty /run/lock), no device command was sent, no lab box was reached (aifoundry1 was
read only through its committed records), nothing was posted. New files only, all under `tools/claims-v3/e191/`. The registration
[`E191.md`](E191.md) (`300d76e4`, its subtree `766e2463`, `SHA256SUMS-e191-registration` `e458fa82...`, 11 entries) and its dated note 1
[`E191.md.dated-note-1.md`](E191.md.dated-note-1.md) (`8c8f825f`, `SHA256SUMS-e191-note1` `45ebe831...`, 3 entries) stay as committed.
This is the kit E191.md 16 and note 1 section 8 ask for: **E189's kit (`b42dc95c`) ported to aifoundry1 card 1**, every E189 file unchanged
beside it (the host check, its frozen lines and E189's plan are run from E189's folder by path). No E191 datum exists.*

## Results first (desk checks of code; nothing is measured)

Every test below ran on aifoundry2 (Linux, /usr/bin/python3 3.12.3, g++-13 13.3.0, bubblewrap 0.9.0), last on Sun 15 Nov 2026 from 01:43 PST (fix-e191k2), from the files
as committed here, each that runs a host, the runner or a stand-in session inside the sandbox; every log was made by that run.

| check | result | log |
|---|---|---|
| **the runner's desk test** (`selftest_run_e191.py`, --dry sessions with `fake_card_e191.py`'s doubles): every case of E189's runner test on E191's runner with card 1's numbers (the stop lines on live samples, the die gate, the cap, the end bound, the gates, SHORT and FAILED RUN, the refusals, end to end through the unchanged reducer, `collect_e191.py` and the frozen scorer, R2E/R3E and the cut-tail control), then **note 1's identity cases I1-I10** (card 0's config read, 519 mV, no identity block, the sampler on card 0, ours on card 0, another login on card 0, a stray host of ours, a host on card 0 in the smoke and in a pass, a host whose card is not seen), **B1** (the 30 s bound, and card 1's lock HELD while the stuck host runs), **B2** (the stuck host outlives the wait: the lock released with it running, the closing read not run beside it), **F1-F3** (the sampler's freshness: a quiet sampler restarted, a dying one restarted, every sampler quiet: the queue stops; every host on a sample under 2 s old), **W1-W4** (et-who refused or garbled: unreadable before the first card command, before a pass, in the identity read), **Q1-Q3** (the early stop: the stop file and SIGTERM while a host runs, the stop file before the session), **D1** (the dry check's refusals), and after the second verifier (fix-e191k2) **R1's control** (every pass's sampler live, no flag), **F1-F3's flag checks**, **F4-F5** (lines without board_w are not live: the sampler restarted; every sampler so: the queue stops), **F6-F7** (a pass with 2 s or more without a live sample flagged, with the desk's idles and with the registered 8 s / 10 s) and **Q4-Q5** (an early stop at the gate, before and during the stop-path test, logged as one) | **SELFTEST-RUN-E191 62 of 62 PASS** | [`logs/selftest-run-e191.txt`](logs/selftest-run-e191.txt) |
| **the REAL path** (`desk/realpath_e191.py`, `desk/realpath_e191.sh`): run_e191.py WITHOUT --dry under the hostname aifoundry1 (a private UTS namespace) and a private PID namespace, E191's REAL guard, the real `timeout 10`, the real ps, et-who on PATH, stand-in reader, hosts, lock and nodes; through the box check, the lock, the identity gate (a) and (b), the stop-path test, the smoke and six passes, the stand-in reader under the name `ettelem` (skipped by pid in every per-pass count); RP2-RP14 each gate and stop on that path (RP14: card 1's lock HELD while the stuck host runs, the closing read after its end); RP15-RP21 the verifier's real-path cases (a quiet sampler restarted; holders of ours and of another login appearing on card 0 between passes; et-who refused before the first card command and between passes; a stray `sparseparity_host` whose comm ps cuts to 15 characters; the stop file during a host); RP22-RP25 the second verifier's (a kernel changed after its build and a record without the gate's OK line: refused at the box check; the reader printing lines without board_w: restarted, the pass flagged; the stop file at the start config read: an early stop at the gate); RW1 the wrong box (hostname aifoundry2) | **REALPATH-E191 26 of 26 PASS** | [`logs/realpath-e191.txt`](logs/realpath-e191.txt) |
| **the dry-vs-real audit** (`desk/dryaudit_e191.py`): every line of run_e191.py that reads the dry flag, what the real path does there, and the desk cases that ran it, each PASS in its committed log | **DRY-AUDIT-E191 21 of 21 COVERED** (one partial reading stated: section 8, item 4) | [`logs/dry-audit-e191.txt`](logs/dry-audit-e191.txt) |
| **THE KERNEL GATE on the REAL build** (`desk/realbuild_e191.sh`, fix-e191k): build_e191.sh with NO stand-in (the desk's real /opt/et, whose riscv gcc reads "() 15.1.0" as aifoundry1's does, real cmake and objcopy, the real pins) in a stand-in tree under the hostname aifoundry2: both programs BUILT through the gate (K1) and HARNESS OK with the built kernels (K2); aifoundry3's `.comment` written in and a debug byte changed: OK by the loadable identity (K3, K4); a `.rodata` byte, a `.text` byte and the entry point changed: each refused (K5-K7); sparse parity's sections, every program header (LOAD and GNU_STACK) and symbols equal E189's committed records of the kernel E189 ran (K8); the pins as built (K9); the identity's second form refuses a changed GNU_STACK header (its flags; its type set to PT_TLS), OS/ABI byte, e_version and an allocated section's entry size, which the first form accepted (K10, fix-e191k2) | **REALBUILD-E191 10 of 10 PASS** | [`logs/realbuild-e191.txt`](logs/realbuild-e191.txt) |
| **the ET_DEVICES reading** (`desk/etdevices_test_e191.sh`): the reading both ways on stand-in files, and **the REAL build_e191.sh under the hostname aifoundry1**: the hosts built against the desk's stock mock (no ET_DEVICES) refused, both; with a stand-in device layer that carries it, both BUILT, records `et_devices yes`; under aifoundry2 recorded as not a gate | **ETDEVICES-E191 8 of 8 PASS** | [`logs/etdevices-e191.txt`](logs/etdevices-e191.txt) |
| **the rest rule** (`rb/selftest_rest_e191.sh`): E190 arm B's, E184 arm B's, E164's and E172's committed aifoundry1 logs at their box paths, E191's own form (real, dry, cut, stopped at the box check, stopped at the identity gate), another tree of ours, a symlinked tree read once, a session on card 0, lib.sh's aifoundry1 block trees, energy.sh's form, none | **SELFTEST-REST-E191 11 of 11 PASS** | [`logs/selftest-rest-e191.txt`](logs/selftest-rest-e191.txt) |
| **step 10's two readings** (`rb/selftest_wait_e191.py`): the gate-stop pattern, read from s20's own text, against a whole E191 session (dry, and the real path's RP1, identity pass lines among them), every gate-stop sentence of the runner, the real path's gate-stop lines, and E189's and E190 arm B's committed real sessions; the BOUND line; the session found by its own script in a private PID namespace (a `bash -c` string, a `grep`, the desk's step 9 script and a dry run not counted) | **SELFTEST-WAIT-E191 6 of 6 PASS** | [`logs/selftest-wait-e191.txt`](logs/selftest-wait-e191.txt) |
| **the runbook** (`rb/selftest_rb_e191.sh` under `rb/selftest_rb_e191_ns.sh`: a private PID namespace, a fake ssh and rsync, a stand-in aifoundry1, the scratch repository with its own upstream): A-T, L1-L3, R, D, RS, LA (the REAL session_e191.sh stopping at its box check), WT1-WT3, C, C2, SC0-SC3 (step 13's real path) and Z, listed in the file's header | **SELFTEST-RB-E191 21 of 21 PASS** | [`logs/selftest-rb-e191.txt`](logs/selftest-rb-e191.txt) |
| the dry listing, every step with stand-ins | **13 steps, 0 exiting non-zero, 0 box calls**; the runbook's command lines pass note 1's item 4 (`desk/drylisting_check_e191.py`: 2 device-opening lines, each ET_DEVICES=1) | [`logs/dry-listing-e191.txt`](logs/dry-listing-e191.txt) |
| `dmcmd_audit` on the session's files (`preflight_e191.sh`) | **GO, 16 send sites, 0 disallowed, every one a READ**, no allow-list, no exception | [`logs/dmcmd-audit-e191.txt`](logs/dmcmd-audit-e191.txt) |
| the quick set (`desk/checks_e191.sh`) | **CHECKS-E191 17 of 17 PASS**: every .py compiles and every .sh parses; E191-COMMON and E191-IDENT SELF-CHECK PASS; the README checker's self-test, and the checker reading E189's committed README names the missing `host.rec`; the harness re-made (42 files) and HARNESS OK; PLANS SAME; E189's host check's lines; the registration's plan and forecast re-made, the E59 self-test PASS; NEVER RAN with E189's data left out; the runbook's command lines | [`logs/checks-e191.txt`](logs/checks-e191.txt) |

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** E191.md 15's and note 1 section 7's rows as they read them; the stock-take's inventory was not read again for this kit.
   Newer pieces are cited by commit: E191's registration (`300d76e4`) and note 1 (`8c8f825f`); E189's registration (`c86940c1`) and kit
   (`b42dc95c`); E189's real day (`fa9098c4`, its card lane's result and logs, read for defects only); E190's kit note 1 (`bff31df2`) and
   note 2 (`eee9fb7e`) and its data (`a6fafba4`); E192's kit (`a6fe5c20`).
2. **Used** (each unchanged, called or read by path; sha256 in [`SHA256SUMS-e191-kit`](SHA256SUMS-e191-kit) or the lists step 2 pins):
   E189's kit (its runner's form, its doubles' form, its host check `hostcheck_e189.py` with `hostcheck-e189.json` and `plan-e189.json`,
   its stand-in cmake and desk mock, its collector's form, its rest rule's and history check's form, its runbook's form); E190's kit note 1
   (the identity gate, the identity read, the host watch, the build's ET_DEVICES gate, the real-path test's form) and note 2 (step 10's
   pattern lesson); k6's runbook library (`rb_common.sh`, v3.1's `rb_run.py` and `nopath_q142s.py`); E172's look's identity rule; E164's
   card-1 config read form; `dmcmd_audit.py` and its table; energy.sh's reducer and stub, unchanged. *Check against an earlier
   measurement of the same quantity:* the rest rule's desk test reads E190 arm B's, E184 arm B's, E164's and E172's committed aifoundry1
   session logs at their box paths and reproduces each end; step 10's test reads E189's and E190 arm B's committed real sessions.
3. **Not used:** any card; any E189 measured number for any E191 forecast, band, rule, threshold, K, order, plan or cap; the counters arm
   (dropped, section 5); the host's package counter unless his go allows it; nothing of the private tier; any refit.
4. **Tiers:** public pieces only.
5. **Readiness:** this kit gates nothing by itself: a verifier checks it, a readiness critic gates the card.

## 1. What changes from E189's kit, item by item

**E191's dated note 1's kit lines** (section 1 items 1-5, sections 2 and 4; its section 8's list):

| note 1 | here |
|---|---|
| item 1: ET_DEVICES=1 for every device process; E189's two removals dropped; a config read made outside the runner sets it where k6's unsets it | `e191_common.device_env()` sets ET_DEVICES=1 and V3_DEVICE=1 for every process `run_e191.py` starts (the guard's config and sample, both hosts, the smoke, et-who); `session_e191.sh` exports them; E191's guard `ettelem_guard_e191.sh` refuses any box but aifoundry1 and any ET_DEVICES but 1 (exit 97 before the device opens: realpath RP8, RW1); step 7 `rb/s09_a1_reads_e191.sh` is k6's reads with `export ET_DEVICES=1` and card 1's lock; the build runs the host check with ET_DEVICES=1 |
| item 2: card 1's lock, never card 0's | `e191_common.LOCK = /run/lock/etsoc-shire1.lock`, flock -n, held to the end (RP2, R13); no command of the kit names card 0's lock or node |
| item 3(a): the start config read's stderr names /dev/et1_mgmt and device ID 1; minion_mv below 510; power_state_name never compared; the end read's stderr kept and reported | `e191_ident.config_identity`; `config-start.err`, `config-end.err`; TDP 65 W, threshold 65 C, 600 MHz (E191.md 2); a failure ends the session before the sampler: "IDENTITY GATE FAILED: ...: the gate, no launch" (I1-I3, RP7) |
| item 3(b): with the sampler running and before the smoke, et-who's lines of ours on card 1 only, one on /dev/et1_mgmt, none on card 0; counts, never a name | `e191_ident.etwho_identity` and, E190's addition, `sampler_identity` (the sampler's own /proc fds hold /dev/et1_mgmt and no card 0 node); `etwho-identity.txt`, `identity.json` (I4, RP9); another login's line on either card also refuses it (stricter: section 4) |
| item 4: the dry pass asserts ET_DEVICES=1 on every device-opening command of the runner and the runbook; nothing names etsoc-shire0, /dev/et0_ or ET_DEVICES=0; nothing unsets ET_DEVICES; no dev_mngt_service or et-powertop | the runner's side: `run_e191.py` records every command with its real form in `commands.jsonl` and every dry session ends with its device-command check (16 commands in a short session), which step 8 on the box requires (`E191-DRY ... dry-check=1`); D1 shows each forbidden form refused. The runbook's side: `desk/drylisting_check_e191.py` on the dry listing (step A of the runbook test; the quick set) |
| item 5: the doubles gain a card-0 case each, and the runner's desk test shows each stops the session before any launch | `fake_card_e191.py`: config card0/mv519/noident, et-who ours0/other0/other/ops, sampler card0, hosts card0/noident (I1-I10) |
| section 2: never run on card 1, frozen in 300d76e4 before any E189 datum; the never-run check (a) with Q166's progs folder and E189's data folder left out, (b) 300d76e4 an ancestor of E189's data commit and earlier, (c) no E191 data in any ref | step 2 (`rb/s03_desk_e191.sh`) runs all three; NEVER RAN at `fa9098c4` with both folders left out (the quick set); the runbook test's H4 refuses E191 data in a ref |
| section 4: E191's kit refuses at step 2 unless E189.md is 98b385b6 and its list bf1b1bbb | step 2 pins E189's registration list (10, `bf1b1bbb...`) and checks E189.md's own sha256 `98b385b6...` |
| section 8: the hosts built and checked on aifoundry1; dmcmd_audit GO at card 1's build; one session of ours on aifoundry1 at a time | step 6 builds both on the box (`build_e191.sh`); step 6's wait reads the preflight GO on the box; the look, the guard and the holder rule (section 4) |

**The defects and departures E189's real day and its readiness check showed, each carried in as kit mechanics** (E189's card lane, Q174's
re-run, its result and logs; ready-e189, Q168):

| what was seen | where | the fix here |
|---|---|---|
| a host stuck past the runner's 30 s bound: Python killed the `timeout` wrapper, not the host, returned rc 124, and the queue went on beside a host that might still hold the card | ready-e189 finding 1 (latent; the day's manual watch saw none) | `run_e191.py run_host`: Popen and a watched wait; past the bound nothing is killed, "BOUND: ..." is logged and **the queue stops** (B1, RP14); step 10 reads BOUND-SEEN (16) and the brief says report at once, kill nothing, keep the booking. A host that honours SIGTERM still ends by the real `timeout 10` (RP13, rc 124 at 10.0 s) |
| every SHORT copy burst read "host rc 1, status FAIL" in the session log and in step 10's output, the words of a FAILED RUN | E189's day, step 10 call 1 (its progress line) | each pass's line adds its reading in words: PASS, SHORT (k of K launches, the host's own budget: scored on its launches) or FAILED RUN (`e191_common.reading`; R11, R12, WT1) |
| the data README's Files table left out sparse parity's `host.rec` | E189's day, incident 1 | `collect_e191.py` writes `FILES.txt` (every file by path); the data README form (`rb/data-readme-form-e191.md`) lists it; `rb/readme_check_e191.py` refuses a README whose Files table misses a file `FILES.txt` names (on E189's committed README it names `host.rec`: the quick set) |
| the public-text scan matched the unchanged reducer's fixed note "assumed package power (RAPL is root-only)" in every energy.json | E189's day, incident 2 | the README form names it in its privacy section and the checker requires it; collected files are never edited |
| step 13 (the scorer) had no real-path test; its header said "on the Intel only" | ready-e189 nit 3 | `rb/s24_score_e191.sh` (the desk is aifoundry2) and the runbook test's SC0-SC3: not committed 10, a worktree change 16, a committed byte change 16, committed and clean 0 with `scores-e191.json`; it exits 0 whatever the words, so the brief says read them |
| the runbook desk test could not be re-run from the landed main (its pull diverged) and saw other lanes' stand-in sessions | ready-e189 nit 2 | its scratch repository has its own upstream; it runs in a private PID namespace (`rb/selftest_rb_e191_ns.sh`) |
| `flock -E 75` inside slot.sh is retried silently as "slot busy" | ready-e189 nit 5 | the brief's step 0 uses `-E 76` inside slot.sh |
| the window's offsets rounded up to the minute; the weekday from the clock in helper scripts; THE LOAD RULE before step 0 and step 2 | E189's day, departures 6 and incident 5 | the brief states each |
| step 10's session pattern must name the script step 9 launches (E183's two lost days) and the gate-stop pattern must not read the identity gate's pass line (E190's step 10 v2) | E183's and E190's days | s20 finds the session by its own script (`ours_live session_e191.sh`); its gate-stop phrases match none of the identity pass lines; both tested on the real names and committed logs (`rb/selftest_wait_e191.py`) |
| a quote inside a `${...:?}` word broke a script (E189's first kit) | found again here, in `etdevices_e191.sh`, by the ET_DEVICES test's first run | fixed before any log was made; the quick set parses every .sh |

**The kit's verifier (verify-e191k, Sat 14 Nov 2026 22:02-22:40 PST: DOES NOT HOLD, 1 major, 4 minor, 6 nits) and what changed before the
land (fix-e191k)**, each kit mechanics or a gate made stricter for safety (section 4); no registered number changes:

| # | the finding | the fix here | shown by |
|---|---|---|---|
| 1 (major) | E189's whole-ELF kernel pins came from aifoundry3's riscv gcc `(g1b306039a) 15.1.0`; aifoundry1's reads `() 15.1.0`; built with it (on aifoundry2, the same toolchain) each ELF differs from its pin (`.comment`, and the ledger's libgcc debug sections) while its `.text` is the registered one: step 6 would have built neither program | THE KERNEL GATE (`check_e191.py --kernel`, called by `build_e191.sh` and by `--box --built`): the `.text` the registered one always (E189.md 4); the whole ELF E189's pin or the `() 15.1.0` toolchain's (built here from two source paths: `2b2eb281...` ledger, `6ee70c92...` sparse parity), or else its loadable identity (the ELF header's entry, machine and flags, every PT_LOAD segment with its bytes, every SHF_ALLOC section with its bytes, the symbol table) the pinned one (`8c6e42df...`, `c3632ecc...` in its first form; re-made in its second form by fix-e191k2, the last table); the build record carries the gate's line | `desk/realbuild_e191.sh` K1-K9 (the real build, no stand-in; the identity shown equal to E189's committed section, segment and symbol records of sparse parity's kernel) |
| 2 | a quiet sampler went unseen: no freshness rule (five passes of the verifier's X9 started on no live sample) | E190's kit note 1's rule: a host process (smoke or pass) and the die gate need a sample under 2 s old (`SAMPLE_FRESH_S`); a quiet sampler is stopped (SIGTERM) and restarted; a pass with no live sample just before its host starts no host; each host's `sample_age_s_at_host_start` (run.json, smoke.json) | runner F1-F3; real path RP15 |
| 3 | a failed et-who read (rc 1, nothing on stdout: its privileged helper refused) counted as "no holder" | `e191_ident.etwho_unreadable`: rc other than 0, or neither a holder line nor the no-holder sentence, is UNREADABLE: refused before the first card command, a stop before a pass, the identity gate fails | runner W1-W4; real path RP18, RP19; the identity self-check |
| 4 | after a BOUND card 1's lock was released while our stuck host ran, and the closing config read started beside it | the runner keeps the lock (and the sampler reading) while that host runs, polling its end (nothing killed) until the end bound less the closing's share; the closing read only after it ends; queue.json's BOUND record `ended_ms`, or `alive_at_close` with `lock_released_with_bound_host_alive` (the brief: report it) | runner B1, B2; real path RP14 |
| 5 | no graceful early stop: a SIGTERM killed the runner (no closing, no queue.json, no manifest) | THE EARLY STOP: a file `STOP` in the session's directory, or a SIGTERM to the runner's own process, ends the queue after the running process, then the closing as for a stop line (`early_stop` in queue.json); before the first card command it refuses; the brief names both | runner Q1-Q3; real path RP21 |
| nit 6 | `DEV_COMM`'s `_host$` missed `sparseparity_host` (ps's 15-character comm `sparseparity_ho`) | `_ho(st)?$`, and for our own processes the executable's own name (/proc/<pid>/exe) too | real path RP20 |
| nit 7 | the stand-in reader ran as `python3`: the per-pass count never met an `ettelem` | the real-path test runs it under the name `ettelem` (a link to the interpreter) | real path RP1 (its comm read while it ran) |
| nit 8 | no test of the holder stop between passes | the verifier's X3 and X4 made kit cases | real path RP16, RP17 |
| nit 9 | our own live collector can hold the management node at step 7's read | step 7's message and the brief allow ONE re-run after the look reads FREE again | the brief, step 7 |
| nit 10 | "no stop changes" against section 4's stricter stops; LAND.md's "before the copy-back is committed" | "no registered stop line changes"; "before the land commit" | this file, the brief, the message, LAND.md |
| nit 11 | `minion_mv` had no floor: a failed read of 0 passed "below 510" | 450 < minion_mv < 510 in the identity gate and in step 7 (a gate made stricter for safety) | the identity self-check |

**The kit's second verifier (verify-e191k2, Sat 14 Nov 2026 23:55 PST to Sun 15 Nov 00:47 PST: HOLDS WITH FIXES, 0 major, 0 minor, 6
nits, none blocking the land) and what changed before the land (fix-e191k2, Q180)**, each kit mechanics or a gate made stricter for
safety (section 4); no registered number changes, and every registered file, list and anchor stays as committed:

| # | the nit | the fix here | shown by |
|---|---|---|---|
| 1 | the freshness rule counted any JSON line as a live sample: a reader whose power request failed but still printed lines kept the session "live" while the 65 W line read nothing (its break case with lines without board_w) | a LIVE sample carries every reading THE STOP LINES read, board_w, minshire[0] and the minion clock, each a number (`e191_common.sample_live`); only a live sample keeps the sampler live, counts as its start and passes the die gate; any other line is still kept and fed to the stop lines, and counted (queue.json `sampler_lines_not_live`); the ages are read on `time.monotonic()` | the common self-check (13 forms); runner F4, F5; real path RP24 |
| 2 | freshness was read only before a host: a sampler quiet inside a pass, or under 2 s before its host, left that pass a normal run with no flag (its X9b, X9c; RP15's pass 2 on a 1.6 s old sample) | each pass's run.json records the last live sample's age at its host's start and end and at the pass's end, the live samples in the host's span, and the largest gap between live samples in the host's span and in the whole pass; a pass with a gap of 2 s or more is flagged "the sampler was not live during this pass" (pass.json `flags` and `sampler_live`, its log line, queue.json `passes_sampler_not_live`); a flag only, the reducer and scorer read nothing of it; each smoke.json records the same age at its end and its gap | runner R1 (the control: no flag), F1-F3 (flag exactly at a gap of 2 s or more), F6 (a 3 s pause flagged though the age at the host's end was under 2 s), F7 (the registered 8 s / 10 s idles: the pass the sampler went quiet in is flagged, X9b's case); real path RP24 |
| 3 | an early stop asked for between the start config read and the stop-path test was logged "stop-path test failed" (16, its break case with the stop file at that moment) | the stop file or SIGTERM is read just before the stop-path test and just after it: "an early stop was asked for (...) before / during the stop-path test: the gate, no launch" (16, step 10's GATE-STOPPED, the closing as before); stop-path.json carries `early_stop` | runner Q4, Q5; real path RP25; step 10's G2 reads both new lines as gate stops |
| 4 (optional) | the loadable identity left out non-LOAD program headers, the OS/ABI byte and e_version (its O1-O4) | the identity's second form adds every program header (type, flags, addresses, sizes, alignment; the file offset left out as layout), e_ident[6..8], e_version and each allocated section's entry size; LOAD_SHA256 re-made from a real build (`2ef2747f...` ledger, `2dd06a90...` sparse parity; the ELFs are still `2b2eb281...` and `6ee70c92...`) | `desk/realbuild_e191.sh` K8 (sparse parity's two program headers equal E189's committed record) and K10 (GNU_STACK's flags, its type set to PT_TLS, the OS/ABI byte, e_version and an entry size: each refused; the first form accepted all five) |
| 5 (optional) | the runner's box check compared the host's sha256 with its build record but not the kernel's | the box check also needs each kernel at its build record's `kernel_sha256` and the record's own `KERNEL OK <prog>:` line (build_e191.sh writes both only after THE KERNEL GATE passed those bytes) | real path RP22 (a kernel changed after its build: refused, nothing started), RP23 (a record without the gate's OK line: refused) |
| 6 (wording) | the land message was tagged "(Q178)" and did not name the re-verification | tagged "(Q178, Q180)"; it names verify-e191k2 and this lane; scanned again | the land message |

## 2. Card-minutes and the cap (registered; unchanged)

About 95 card-minutes (12 + 6 + 50 + 6 + 20 = 94), **cap 110**: no pass starts after 108 card-minutes from the first card command, and the
session's last card command ends by 110 (E189's end bound, unchanged). The counters arm's 6 card-minutes go unused (section 5).

## 3. The box steps (from aifoundry2; the card lane's brief is [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

E191 runs alone on aifoundry1 card 1 (the booking key `aifoundry1` is the whole box), never beside another session of ours on either card,
and never on card 0. Run from the lab clone, each step with this day's `RB_OUT` (outside the repo, E191's own), the one `RB_LOCK` and, for
step 2, `RB_GITLOCK`. Exit codes are k6's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a
holder after 30 minutes; 16 a gate says stop; 17 call again.

| box step | file | what |
|---|---|---|
| 0 | (by hand) | the booking; THE LOAD RULE; `check_day2_v2.py tree --pull` under the lab-git lock; E191's anchor lines; THE QUIET HOLD |
| 1, the window | [`rb/s02_window_e191.sh`](rb/s02_window_e191.sh) `<day> <last start> <last end>` | FIRST; today's day only; G+1:30 / G+3:30 rounded up |
| 2, the desk check | [`rb/s03_desk_e191.sh`](rb/s03_desk_e191.sh) (outside the kit list; its sha256 in the anchor lines) | the window; the pull under the lab-git lock; ancestry; the history check; every list at its pins (11; 3; 10; 55; 165; 17, 6; 86; the kit's); E189.md the cited text; the harness; PLANS SAME; both self-checks; the registration's checks; NEVER RAN (a), (b), (c); the preflight; the desk tests' logs |
| 4, the look, FIRST on the box | [`rb/s05_look_e191.sh`](rb/s05_look_e191.sh) `[--wait]` | both cards: the identity by continuity (booted before E82's firmware read), et-who as counts by card, ps, our sessions and jobs; FREE only with nothing on either card; our login to RB_OUT |
| 3, the post | (the card lane's, if that day's go asks one) | the owner's call that day; named only |
| 5, the sync | [`rb/s07_a1_sync_e191.sh`](rb/s07_a1_sync_e191.sh) | the box read first; harness-e191.json's 42 files into aifoundry1:nekko/ (the build directories of ours: build/e191ledger, build/e191spp); HARNESS OK on the box |
| 6, the build | [`rb/s08_a1_build_e191.sh`](rb/s08_a1_build_e191.sh) `start`, then `wait` while 17 | the detached job a1-build-e191: both programs, the kernels through THE KERNEL GATE (the registered .text; a pinned ELF or the pinned loadable identity), the hosts by behaviour with ET_DEVICES=1 set, THE ET_DEVICES READING (a refusal); the records, the harness, the preflight and both self-checks read on the box; NO-THIRD-BUILD |
| 7, the reads | [`rb/s09_a1_reads_e191.sh`](rb/s09_a1_reads_e191.sh) | k6's reads for card 1: ET_DEVICES=1, card 1's lock, the guard's config with its stderr kept (/dev/et1_mgmt, ID 1, minion_mv between 450 and 510, TDP 65 W / 65 C / 600 MHz); both cards free; "no config read came back": one re-run after the look reads FREE again |
| 8, the dry pass | [`rb/s10_a1_dry_e191.sh`](rb/s10_a1_dry_e191.sh) `start`, then `wait` | the runner on the box with its doubles, the identity gate and the dry check in it |
| 9, the session | [`rb/s11_a1_session_e191.sh`](rb/s11_a1_session_e191.sh) `FULL [--rapl-allowed]` | k6's guard (no session of ours on aifoundry1, the identity by continuity), THE REST RULE (every tree and form of ours on aifoundry1, E190 arm B's included), today's dry pass and build, then session_e191.sh detached with ET_DEVICES=1 |
| 10, the wait | [`rb/s20_wait_e191.sh`](rb/s20_wait_e191.sh), while 17 | the session by its own script; GATE-STOPPED and BOUND-SEEN (16); each pass's reading in words; THE EARLY STOP (the stop file, or SIGTERM to the runner) ends it gracefully (0) |
| 11, the release, then the collection | [`rb/s22_collect_e191.sh`](rb/s22_collect_e191.sh) | one read-only copy back, COPY-BACK EXACT, the data directory `docs/reports/data/<day>-e191-blind-day-aifoundry1-c1/`, the reducer (unchanged), the scrub (box home and login), SHA256SUMS and FILES.txt, the desk-path gate, the history check |
| 12, the data commit | (the card lane's) | the README from [`rb/data-readme-form-e191.md`](rb/data-readme-form-e191.md), checked by [`rb/readme_check_e191.py`](rb/readme_check_e191.py), the public-text scan, commit_lab.sh |
| 13, the scorer, after the data commit | [`rb/s24_score_e191.sh`](rb/s24_score_e191.sh) | `score_e191.py` (registered, unchanged) on the committed data; RB_OUT/scores-e191.json; read the words |

## 4. The readings stated here before any E191 datum (each kit mechanics, or a stop or gate made stricter for safety, named so)

- **The holder rule covers both cards (a gate made stricter for safety).** Before the first card command and before each pass, the runner
  refuses on: another login's holder line on EITHER card (E189's foreign() already counted every card; kept), a line of ours on card 0 (a
  /dev/et0_ node or card 0's lock: another session of ours on aifoundry1), a line of ours on /dev/et1_ops while no host of ours runs (a
  stray host), another user's device process (E189's), and, new, a device process of ours other than the session's own sampler. The look
  (step 4) asks the same of the box: FREE only with no holder line on either card, no device process of anyone's and no session or job of
  ours. Card 0 is never opened by any step.
- **The box check (a gate, E190 arm B's form).** The real session refuses before its lock unless the host is aifoundry1, ET_DEVICES is 1,
  the reader `build/ettelem/ettelem` is at its pin `8008f96f...` (E157's, E164's, E172's and E190 arm B's on card 1), and each program's
  build record is today's, by build_e191.sh, with the host at its sha256 and the ET_DEVICES reading passed.
- **The identity bounds** are note 1's: /dev/et1_mgmt and device ID 1 on every identity line of the start config read; minion_mv below 510;
  et-who's lines of ours on card 1 only with one on /dev/et1_mgmt; the sampler holding /dev/et1_mgmt and no card 0 node; another login's
  holder line on either card also refuses the identity read (stricter for safety, matching the holder rule).
- **The watch (a stop made stricter for safety).** A host whose stderr names, or whose process tree holds, another card's node stops the
  session after that process; the pass is set aside ("identity: ..."). The hosts have no stop file and a device process is never killed,
  so that process ends by its own budget, at most `timeout 10`; in the smoke the first device-opening process (a 64 MiB copy, one launch) is
  where it would be seen. A device-opening smoke process that showed no card 1 (no PCIe target line, no node held) fails the smoke gate; in
  a pass it is flagged, reported.
- **The ET_DEVICES reading (a refusal, E190's kit note 1's).** On aifoundry1 the build refuses a host unless the host binary and
  /opt/et/lib/libdeviceLayer.a carry the string ET_DEVICES and CMakeCache.txt took the device layer from /opt/et: the one place this kit
  reads a string from a binary, and it can only refuse; the host's behaviour is still read by E189's host check, and its card at run time
  by the identity gate and the watch.
- **The 30 s bound (a stop made stricter for safety).** Past HOST_BOUND_S (30 s) the queue stops; nothing is killed. **After it
  (fix-e191k, finding 4; kit mechanics):** card 1's lock stays held, and the sampler reads, while that host runs; its end is polled every
  second until the end bound less the closing's share; the closing config read runs only after it has ended; if it still runs then, the
  lock is released with it running and the closing read is not run (recorded in queue.json, reported).
- **THE KERNEL GATE (kit mechanics; fix-e191k, finding 1).** The registered `.text` (E189.md 4) always; and the whole ELF E189's pin or
  the `() 15.1.0` toolchain's, or else the loadable identity the pinned one: no loadable byte, header or symbol may differ, so it is
  stricter than the registration (the `.text` alone) while accepting a toolchain that differs only in sections the card never loads.
- **The sampler's freshness (a gate made stricter for safety; finding 2).** A host process and the die gate need a sample under 2 s old.
  **A live sample (kit mechanics; fix-e191k2, the second verifier's nit 1):** one that carries board_w, minshire[0] and the minion clock,
  each a number; a line without one of them never keeps the sampler live (it is still kept and fed to the stop lines), so a reader that
  prints such lines is quiet and is restarted. **The sampler during a pass (kit mechanics; nit 2):** a pass with 2 s or more without a
  live sample between its start and its end carries the flag "the sampler was not live during this pass", reported; it is not set aside,
  and nothing scored reads the flag.
- **THE KERNEL GATE's identity, second form (stricter; fix-e191k2, nit 4)** reads every program header, e_ident[6..8], e_version and the
  allocated sections' entry sizes as well; **the box check (stricter; nit 5)** refuses a kernel no longer at its build record's sha256 or a
  record without the gate's OK line.
- **An early stop at the gate (kit mechanics; fix-e191k2, nit 3)** is logged as one ("... before / during the stop-path test: the gate,
  no launch"), never as a failed stop path.
- **et-who unreadable (a gate made stricter for safety; finding 3).** An et-who that exits other than 0, or answers with neither a holder
  line nor its no-holder sentence, refuses before the first card command and stops before a pass.
- **The early stop (kit mechanics; finding 5).** The stop file or a SIGTERM to the runner ends the queue after the running process, then
  the closing; before the first card command it refuses.
- **Our device processes (stricter; nit 6)** by ps's comm with `_ho(st)?$` and by our own executables' names; **the identity's floor
  (stricter; nit 11)** minion_mv above 450 as well as below 510.
- **The rest rule (kit mechanics).** E189's rule, read in every tree of ours on aifoundry1 (`~/nekko`, `~/aifoundry`,
  `~/claude/et-soc1-prototyping`, each real directory once), with lib.sh's aifoundry1 block trees; a session of ours on either card starts
  the 40 minutes.
- **ours_live (kit mechanics).** E190's by each process's own script, with one condition added: the command's first word is an
  interpreter (bash, sh, dash, python, python3), so a `grep` naming the session is never counted (its step 10 test found E190's counted it).
- **The pass's reading in words; FILES.txt; the README form and check (kit mechanics, section 1).**
- **Everything else is E189's kit section 4, unchanged:** the clock line counts the samples taken in a pass; a stop during a pass keeps
  that pass's 10 s of idle after; any smoke failure or stop in the smoke ends the session at the gate; the die gate (60 C, at most 10
  minutes, never past the cap; below 52 C labelled); the cap and the window; the end bound; one sampler; the adapter; the reducer's "dir";
  the build's re-run (at most two starts a Pacific day); the package counter only with `--rapl-allowed` and only as our own user.

## 5. The counters arm: DROPPED

E191.md 7 lets E191's kit run the counters arm only "if E189's kit keeps it (its desk test passed)". E189's kit dropped it (its KIT.md
section 5: no variant written, no desk test run), so **E191's kit drops it too**: the session logs "the counters arm: DROPPED" and its 6
card-minutes go unused; its frozen expectations stay in `forecast-e191.json`, unused. This is a registered option taken as registered,
not a change.

## 6. Files (all new, under tools/claims-v3/e191/)

| file | what | builds on |
|---|---|---|
| `e191_common.py` | the card (ET_DEVICES=1, shire1 lock, the reader's pin, the config line), the commands, the smoke, THE ADAPTER, the reading in words, THE STOP LINES | E189's `e189_common.py` |
| `e191_ident.py` | the identity gate (a) and (b), the sampler's nodes, the holder rule's lines, the host watch; its self-check | E190's `e190_note1.py` (arm B) |
| `run_e191.py`, `session_e191.sh` | the session runner and its detached wrapper | E189's runner; note 1 |
| `ettelem_guard_e191.sh` | the only way to the reader: config and sample, aifoundry1 and ET_DEVICES=1 only | E128's and E190's guards |
| `build_e191.sh`, `etdevices_e191.sh` | the box build and its ET_DEVICES reading | E189's build; E190's build v2 |
| `check_e191.py`, `harness-e191.json` | the 42 files the box runs or reads; PLANS SAME; THE KERNEL GATE and its pins (fix-e191k; the loadable identity's second form, fix-e191k2) | E189's harness |
| `preflight_e191.sh` | dmcmd_audit on the session's files | E189's preflight |
| `fake_card_e191.py` | the doubles, with card 1's identity and card 0's cases | E189's and E190's doubles |
| `collect_e191.py` | COPY-BACK EXACT, the data directory, the reducer (unchanged), the scrub (home and login), SHA256SUMS, FILES.txt | E189's and E190's collectors |
| `selftest_run_e191.py` | the runner's desk test | E189's |
| `desk/realpath_e191.py`, `desk/realpath_e191.sh` | the real-path desk test and its namespaces | E190's note 1 |
| `desk/dryaudit_e191.py` | the dry-vs-real audit | CONTEXT section 104's lesson |
| `desk/etdevices_test_e191.sh` | the ET_DEVICES reading's test, with the real build under aifoundry1's hostname | E190's build desk test |
| `desk/realbuild_e191.sh` | THE KERNEL GATE's test on the real build, no stand-in (fix-e191k; K10 and the widened K8, fix-e191k2) | the verifiers' kernel-pin finding and nit 4 |
| `desk/drylisting_check_e191.py` | note 1's item 4 on the runbook's command lines | note 1 |
| `desk/checks_e191.sh` | the quick set | |
| `rb/rb_e191.sh` | what every step sources (k6's library unchanged; E191's ours_live, pins, window, lab-git lock) | E189's `rb_e189.sh`, E190's `rb_e190.sh` |
| `rb/s02`, `rb/s03` (step 2, outside the list), `rb/s05`, `rb/s07`, `rb/s08`, `rb/s09`, `rb/s10`, `rb/s11`, `rb/s20`, `rb/s22`, `rb/s24` | the runbook's steps | E189's steps; k6's look and reads |
| `rb/rest_rule_e191.sh`, `rb/check_history_e191.py` | the rest rule and the history check | E189's |
| `rb/list_steps_e191.sh` | the dry listing | E189's |
| `rb/selftest_rb_e191.sh`, `rb/selftest_rb_e191_ns.sh`, `rb/selftest_rest_e191.sh`, `rb/selftest_wait_e191.py`, `rb/fake_cmake_e191.sh` | the runbook's desk tests and the stand-in cmake | E189's |
| `rb/data-readme-form-e191.md`, `rb/readme_check_e191.py` | the data README's form and its check | E189's README; its incidents 1 and 2 |
| `CARD-LANE-BRIEF.md` | the card lane's brief | E189's |
| `logs/` | every check above | |
| `SHA256SUMS-e191-kit` | every kit file but itself and step 2, the logs, and the unchanged files the kit calls | |

## 7. Device commands

`dmcmd_audit.py` on the session's file set (`preflight_e191.sh`): **GO, 16 send sites, 0 disallowed, every one a READ**, with no allow-list
and no exception: `ettelem config` (TDP level, temperature thresholds, power state, the ASIC's frequencies and voltage) and `ettelem sample`
(module power, SP statistics, temperature, the ASIC's and the module's voltage, frequencies), through E191's guard, which refuses
`--reset-ms` and every other word, any box but aifoundry1 and any ET_DEVICES but 1, before the device opens. The 16 sites are the guard's
11 (config 5, sample 6) and the runner's recorded config command line (5). The two hosts open card 1's ops node only (the identity gate and
the watch read it). No set, no reset, no statistics reset, no firmware query of any kind, no power cycle, card 0 never opened.

## 8. What the desk cannot show (for the verifier and the readiness critic)

1. **The two programs' first build on aifoundry1** is step 6 there, against aifoundry1's own /opt/et (its riscv gcc reads "() 15.1.0", as
   the desk's does: the real-build test shows the gate passes for that toolchain's kernels, path-independent; aifoundry1 itself is not
   read from the desk): the kernels' gate, the hosts'
   behaviour and the ET_DEVICES reading (E190 arm B's build passed the same reading there for E136's host on Fri 13 Nov 2026). A host
   without the string is refused (a safe failure: that program is SKIPPED).
2. **The ledger host's and sparse parity's host's identity block on card 1** has never been read: on aifoundry3 both print `PCIe target:
   /dev/et0_ops` and `Physical device ID: 0` in every pass of E189's committed data; with ET_DEVICES=1 on aifoundry1 the device layer is
   expected to print card 1's (E190 arm B's host did). A host whose block cannot be read fails the smoke gate (a safe failure).
3. **The runner has run only with its doubles and stand-ins** (the desk; on the day, step 8): the live reader, card 1's lock, et-who and the
   real hosts meet it first in the session.
4. **Other users' device processes:** the real ps read runs on the real path (RP1), but a positive count of another user's process cannot be
   made on the desk without a second login (the dry audit states it); E189's real session ran the same read before every pass.
5. **The collection** has run on stand-in sessions (the runbook test's gate-stopped one; the doubles' passes), not on a card's.
6. **Card time waits on his go** (`CARD-LANE-BRIEF.md`), after E189's real day (done, `fa9098c4`) and never beside another session of ours on
   aifoundry1.
7. **The device loader's own reading of an ELF** is not readable from the desk: the identity's second form (fix-e191k2) covers every
   program header and allocated section and the header's fields; what it still leaves out is file layout (the program headers' file
   offsets, sections the card never loads), which a toolchain may change without changing a loaded byte. A third toolchain that differs
   in a covered field is refused (SKIPPED, no data), never run.
8. **The real reader's lines without a stop line's reading** have never been seen (0 of the 37,101 committed real samples, verify-e191k2's
   read); the new live-sample rule and the per-pass flag are shown on the doubles and the real path's stand-in reader only.

## 9. Labels

Every figure quoted from E191.md, its note and their files (the forecasts, K, the order, the caps, the stops, the pins) is **registered**.
The desk tests' results are **desk checks of code**, not measurements; the end-to-end joules and the scorer's words come from the doubles
(energy_stub.py's alt card). The committed records the kit reads (the session logs at their box paths, the identity blocks in E189's data)
are **desk reads of committed records**. Nothing here is measured, blind or held out, and no E191 datum exists. This kit is written after
E189's data commit; by note 1 section 3 it is limited to mechanics and stricter gates (section 4), and it says nothing about a frozen number.

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), one job at a time per slot, each that runs a host, the runner, a
stand-in session or a stand-in box inside the sandbox (W/nodev.sh; the real-path, the runbook and step 10's tests in private PID namespaces,
the real-path, ET_DEVICES and real-build tests under a private hostname): the runner's test (about 16 minutes, the registered idles in its end-to-end and F7
cases), the real-path test (about 2.5 minutes), the real-build test (real cmake builds of both programs against /opt/et, about a
minute), the ET_DEVICES test and the runbook test (real g++-13 builds of both hosts, about 2 and 4
minutes), the rest rule's and step 10's tests, the dry listing, the quick set. No other box, no card.

SPDX-License-Identifier: Apache-2.0
