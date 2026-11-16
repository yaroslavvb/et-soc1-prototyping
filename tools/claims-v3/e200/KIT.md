# E200's run kit: E197's kit ported to aifoundry2 card 0 under its governor and run from aifoundry2 itself - E197's reference session with E200's runner (W1), THE CLOCK RULE live as C3 (the smoke's clock, three processes in a row), the die gate, aifoundry2's own stop lines, the lab's firmware gate (fwgate) as THE REBOOT GATE, the configuration gate, THE QUIET DESK FLAG, the box-tree gate, the runbook on this box from the booking to the reduction after the data commit, and the real-path, real-bytes, runbook, fwgate and rest-rule desk tests (Q192; kitted, fixed before the land, not run)

*Mon 16 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q192, lanes `kit-e200` and `fix-e200`). **Written after E200's registration**
([`E200.md`](E200.md), its list `SHA256SUMS-e200-registration` sha256 `3e3e7d40...`, 17 entries; its subtree `c479c271...`: the registration
as fixed before the land, its freeze line in section 0) **and after E197's registration and kit landed on GitHub main** (`ea4b4ad7` and `2c68a633`, Mon 16 Nov 2026 02:01 PST;
E197's subtree `a4fe6d55...`, byte for byte the land directories E200's registration read), **and before any E200 datum.** No card was
claimed or opened (aifoundry2 has a card: every desk test that ran the session, the runner, a stand-in or a built host ran in the round's CPU
slot inside the no-device sandbox, each case in a sandbox of its own, and only while THE QUIET DESK FLAG was absent), no device command was
sent, no other lab box was reached, nothing was posted, no simulator ran. New files only, all under `tools/claims-v3/e200/`; every file of
E197 and E194 and fwgate stays as committed. This is the kit E200.md 19 asks for. **No E200 datum exists, and the forecast stays sealed: no
forecast number is in any file here, and nothing here scores against it.** Nothing here changes a train, a kind, a value, the order, a
window, a threshold, a cap, the reduction or the comparison; the kit adds stops and gates that end a sitting early, each named so (E200.md
19's last paragraph, E197.md 9).*

*Fixed before the land and before any datum, Mon 16 Nov 2026, PST (Q192, lane `fix-e200`; desk only: no card, no device command, no other
box, nothing posted): verify-e200's findings answered (section 13): the registration's freeze line and its moved pins (F1), C3's wait for a
process's records (F2), no sitting after a die-gate stop that day (F3), the settles' wait for our live collector's reader (F4), the
wrapper's firmware-record words (F5), a fwgate record added after the kit read before it is trusted (F6), the flag's form (F7), the rail
row's reading (F8). Every desk test below ran again on the fixed state (05:56-06:20 PST).*

## Results first (desk checks of code; nothing is measured)

Python everywhere: `/usr/bin/python3` 3.12.3 on aifoundry2; cmake 3.28.3, riscv64-unknown-elf-gcc "() 15.1.0" and g++ 13.3.0 from this
box's /opt/et for the runbook test's real build; GNU patch 2.7.6; bubblewrap 0.9.0. Every watt, degree, clock and rate in a test is a
stand-in's arbitrary test value, never a forecast and never a measurement.

| check | result | log |
|---|---|---|
| **THE REAL-PATH DESK TEST**: `session_e200.sh`'s real path, DRY unset, exactly as step 9 launches it, and through it E197's reference session with E200's runner, against stand-ins for every device tool (the reader behind E200's guard with the governor's climb inside each process, the die gate's reads, et-who, ps, a host printing REGFILE lines in the real host's form), each case in its own sandbox (two regular files at /dev/et0_ops and /dev/et0_mgmt, a private /run/lock with the card's lock, a private PID namespace, the host name aifoundry2, step 7's folder with fwgate's EQUAL record): the dry path (three plans); **sitting 1 whole, full and short, and sitting 2 whole, their host processes in the registered order call for call with W1's window, then E200's registered reduction on their own files and the pooled reduction**; **THE CLOCK RULE BOTH WAYS at the real pace** (RC1 800 MHz counts: every process kept, launches 0-4 not read and 5-12 read; RC2 a step down inside the busy window: that process NOT COUNTED; RC4 a climb at 1.6 s set aside and one at 1.4 s kept; RCM the session's median clause); **C3** (three processes in a row off 800 MHz: the watch's STOP); **the smoke's clock** (a step after 1.5 s, a last launch at 600 MHz by its own count, a governor that never steps up: GATE-STOP before block A); **aifoundry2's own lines** (86 W held on every sample; the latch at 80 C); **the die gate** (passed on its third read; held for its bound: GATE-STOP, counted by the rest rules); the free check's re-read for our live collector; every stop (by hand, the kit's 65 W stop at its boundary, the die, a quiet sampler, a signal to the wrapper and to run_session.sh, the watch killed, two failed processes, a timeout end, a HUNG host with no KILL and no end-of-sitting config read); the smoke's gates; **runtime lines in the host's output with E191's committed bytes**; the holders and the lock; a crash; the cap; every refusal (the reader at its real pin, the W1 diff, step 7's folder and the firmware identity); run_session.sh's own refusals alone; the watch's end-stop alone; **the watch against the runner's write order** (WO, fix-e200: a process's records late, split, or never written: C3 judges it on its 13 records, or not at all after 3 s); and the audit of every dry branch | **547 of 547 PASS: 82 cases (the audit: 31 rows, the 69 cases they name all passed)** | [`logs/desktest-realpath-e200.txt`](logs/desktest-realpath-e200.txt) |
| **the runbook** with a fake ssh and rsync on a stand-in aifoundry2 box (its tree ~/claude/et-soc1-prototyping): the window rule (with its 2:00 rule), the lab-git lock (absent and nested), step 2 at every pin (E197's two lists, E200's registration and E197 references, the kit's), the history check and its shadows, the harness check naming a fwgate record added after the kit and step 2 reading it against its committed source (fwgate's check-records OK; one with no source refused: P5), THE FREEZE LINE checked and printed, no E200 datum in any ref, the sync into E200's root, **the real build on the stand-in box** (make_images and check_elf, the host's table SAME, its four refusals, its signal read, E200's runner made by W1 at 8774027b..., the dry listings SAME x3 but W1), NO-THIRD-BUILD, a login link (into a COPY of the round's lock file), a hang, a cut wait, the dry pass, **the rest at step 7 before any card command (E194's session form on this card; no config read sent)**, fwgate's look CONTINUITY and the config read kept in step 7's folder, the stamp kept, step 9 refused past 120 s, sitting 2's three refusals at step 7, no second try on a smoke-failed day, **no card command (step 7) and no launch (step 9) on a day an E200 log holds the die gate's GATE-STOP** (DG7, DG9), **THE QUIET DESK FLAG** (the look and the launch refused with it down; another lane's flag never overwritten or removed; a device-named process of ours: step 9's P2 count refuses), **the real session launched and found by the wait by its real script name**, its gate stop collected as a gate stop's record, a desk-test session refused by the collection outside a desk test, the retry in a new RB_OUT, the wait on the real-path test's sessions (whole, stopped, gate-stopped, crashed, hung), the collection with THE BOX-TREE GATE, step 13 before and after the data commit, the data README form's own re-make commands (the same json, byte for byte), and sitting 2's pooled reduction | **27 of 27 PASS** | [`logs/selftest-rb-e200.txt`](logs/selftest-rb-e200.txt) |
| **THE REBOOT GATE as the runbook calls it** (fwgate in its own desk mode, no /dev/et* at all): the look NEEDS-READ; step 7's one read EQUAL (exactly `-m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000` under the card's lock, one call) into step 7's folder, then the config read; step 7 again: no second read; step 9's guard ok and the launch; a DIFFERENT answer: step 7 16 with no config read, the look 16 (STOPPED), step 9 IDENTITY-STOP; the card held at the read: 17, nothing sent | **7 of 7 PASS** | [`logs/selftest-fwgate-e200.txt`](logs/selftest-fwgate-e200.txt) |
| **the host-output parser on real bytes**: E200's runner made by W1 (8774027b...), its parse loop (lines 204-212, E197's line for line) taken from its syntax tree, on E191's committed split bytes (every offset of a REGFILE line), on **this card's committed host output** (E194's 32 host stdouts, E190 arm A's 84 process stdouts: no runtime byte on stdout; the device table on stderr), on aifoundry3's (E193's, E192's), on stand-in streams, and the E197 host's print discipline | **29 of 29 PASS** | [`logs/realbytes-e200.txt`](logs/realbytes-e200.txt) |
| **the rest rule**: E194's eleven cases (E190 arm A's committed form on this card, E194's forms, other trees, block trees, energy.sh, the older run logs); **E194's committed session log on this card at its box path** (30 minutes REFUSED, 41 rest 41); E200's own forms (sitting 1 before sitting 2, its dry pass, two gate stops before the session's run skipped, a die-gate stop counted); a cut E200 sitting counted at its root's latest write; and this box's real trees, read-only | **14 of 14 PASS** | [`logs/selftest-rest-e200.txt`](logs/selftest-rest-e200.txt) |
| the quick set: the harness, the history check's names, **the kit's checker on the registration's own synthetic governed sessions** (governor: 400 of 400 kept; faults: each planted clock fault set aside by its clause; nogov: the median NOT 800, every process set aside), the summary, the checker's refusal of E197's reducer's output, drycmp (W1 SAME; two negative controls), the wait's session name on the real script, the guard's mode, **a fwgate record added after the kit** (named and passed, in the sync list; a pinned record or box file changed by a byte: CHECK FAIL) | **27 of 27 PASS** | [`logs/checks-e200.txt`](logs/checks-e200.txt) |
| the dry listing, both sittings, every step with stand-ins | **25 steps, 0 exited non-zero, 0 box calls beyond aifoundry2** | [`logs/dry-listing-e200.txt`](logs/dry-listing-e200.txt) |
| `dmcmd_audit_v2`, every file whose commands the sittings send (`preflight_e200.sh`, fwgate.py among them) | **GO, 12 send sites, every one a READ** | [`logs/dmcmd-audit-e200.txt`](logs/dmcmd-audit-e200.txt) |

## 1. What changes from E197's kit, item by item

| what | E197's kit (aifoundry3 card 0, from aifoundry2) | here (aifoundry2 card 0, from aifoundry2 itself) |
|---|---|---|
| the box and its tree | aifoundry3, `~/aifoundry`, E197's root `build/claims-v3/aifoundry3/e197` | aifoundry2 itself, reached by k6's drivers by ssh to this box (E194's way), its tree `~/claude/et-soc1-prototyping` (a git checkout whose `build/` is ignored), E200's root `build/claims-v3/aifoundry2/e200` (the synced files and the build: a build folder of ours, never the box tree's own files) |
| the runner | E197's lab runner (D1) at 91c46f4e... | **E200's runner**: E197's lab runner with W1 applied by `patch -o` (the wrapper into the sitting's ref/, the build into build/run_trains-e200.py), checked at **8774027b...**; the dry listings E197's but W1 (`check_e200.py drycmp`) |
| the reader | `build/ettelem/ettelem` through E128's guard | `build/ettelem-hpl/ettelem` (77a46171..., E136's, E190 arm A's and E194's on this card) through **E200's guard** (`ettelem_guard_e200.sh`: E194's allow-list, aifoundry2 and ET_DEVICES / V3_DEVICE unset only, the reader named from the box tree; mode 100755: run_session.sh runs `"$ETTELEM"` as a program); its pin checked by the build, step 7 and the wrapper |
| the reboot gate | none (k6 never gated aifoundry3) | **the lab's fwgate** (E200.md 8): its look at step 4 (the desk, no device), its one read at step 7 on NEEDS-READ (the sitting's first card command, after the rest), its guard at step 9; the read's record in step 7's folder, copied into the session's `first/` (k6's identity by continuity refuses this boot: replaced) |
| the configuration | k6's reads (TDP 0 W / 65 C / 600 MHz) | step 7's own read through E200's guard under the card lock, kept in step 7's folder, read by E194's `e194_common.py --config-line`: **TDP 65 W, threshold 65 C, 600 MHz at rest** (E200.md 3), /dev/et0_mgmt and device ID 0 alone, minion_mv 450-600 (E194's bounds); **the end read** by the wrapper, reported |
| the clock | the watch's stop: a clock other than 600 MHz on three samples | **C3** (E200.md 4): three train processes in a row whose samples from their first launch + 1.5 s to their last launch's end leave 800 MHz end the sitting; **the smoke's clock**: both smoke train processes by THE CLOCK RULE (samples and the last launch's own count, 780-810 MHz) before block A; C1 and C2 are the reduction's (`reduce_e200.py`) |
| the die gate | none | **57 C** (minshire[0]), read by the wrapper after the free check through E200's guard (`sample --seconds 1 --every-ms 200` under the card lock), every 20 s for up to 10 minutes, in the cap; else GATE-STOP (counted by the rest rules) |
| the stop lines | 65 W (distinct readings), 70 C | the same, and **aifoundry2's own**: board above 85 W on 3 samples in a row; minshire[0] or the latch minshire[2] at or above 80 C |
| the free check | et-who once | et-who **re-read up to 3 times 2 s apart while every holder line is a reader of ours on /dev/et0_mgmt** (our live collector; E194's re-read) |
| the quiet desk | none (another box) | **THE QUIET DESK FLAG** (`rb/quiet_e200.sh`, RB_QUIET = W/locks/quiet-desk-aifoundry2, "e200 <lane> <time>"): every step from the look to the collection refuses without it; THE P2 COUNT before the look and in step 9's launch call |
| the collection | E183 note 5's desk-path gate | **THE BOX-TREE GATE** (E194's) before anything is written, fwgate's ledger path allowed by name; then the scrub and k6's desk-path gate; a session whose start line names DESKTEST refused outside a desk test |
| the rest rule | aifoundry3's trees | E194's rule: every tree of ours on this box, E194's and E190 arm A's sessions, the older run logs, E200's own forms |
| the window | G+1:30 / G+3:00 | **G = the booking, last start G+1:30, last end G+3:30** (E194's A1-4; step 1 refuses a last end that is not the last start + 2:00) |
| the reduction | E197's reducer | **`reduce_e200.py`** (registered, unchanged): E197's reducer by path and sha256 with C1 and C2; the checker reads its "e200" key |

## 2. The session (`session_e200.sh`)

It runs E197.md 5's reference session (E197's `run_session.sh`, `stopwatch.py`, `trains.tsv` at E197's registration's sha256) with E200's
runner, copied and made into the sitting's `ref/` and checked there, and adds only what E200.md 19 asks:

| step | what | why |
|---|---|---|
| 1 | refusals before anything (exit 2, "no device opened by the session"): the box tree's layout; the host's name aifoundry2 (hostname and Python's); USER the login; harness-e200.json at the sha256 the launch passes, every file of it at its pin; E197's registration list at `992a35e5...`; the host, E200's guard and the reader present, **the reader at its pin**; the host the one today's build recorded; `preflight_e200.sh` GO (dmcmd_audit_v2); exactly /dev/et0_ops and /dev/et0_mgmt; ref/'s three E197 files at E197's registration's sha256; **W1's diff at 24224f12... and the runner it makes at 8774027b...**; on the real path **step 7's folder** (build/e200/first-s<n>-<FIRST>, its config read) with the firmware identity the launch passed (FWGATE read: fwgate's records there all EQUAL, one at least, the newest read on this boot, a second layer under step 9's fwgate guard; continuity: none), copied into first/; the first card command today and at most 120 s back, its cap before the window's last end, the lock file present | nothing runs that is not pinned; one card; no device opened before these |
| 2 | the free check (et-who --check, re-read for a reader of ours on the management node; other users' device processes; a probe of the existing card lock: exit 3, "no device opened by the session") | E197.md 5; E194's re-read |
| 3 | **THE DIE GATE** (57 C, every 20 s, up to 10 minutes, in the cap): exit 12 and a counted GATE-STOP when it does not pass | E200.md 9 |
| 4 | `CAP_S` = the cap - 60 s - (now - the first card command), never more than the window's last end - 120 s - now (at least 300 s); ETTELEM = E200's guard | E197's kit section 4 |
| 5 | **the kit's watch** (`watch_e200.py`) beside the reference session (its stops, C3, the smoke check with the smoke's clock, the end-stop, the hang watch) | E200.md 4, 9 |
| 6 | the reference session, `run_session.sh <OUT> full\|short\|ext` | E197.md 5 |
| 7 | SESSION_DONE by the wrapper when run_session.sh exits before its own | E192's fix 1 |
| 8 | **the configuration at the sitting's end**, when the sampler ran, no host hung and et-who reads free: one config read through the guard under the lock, reported | E200.md 3 |
| 9 | the summary (`check_e200.py summary`: the smoke gate, the kit's smoke check, the clock's verdicts, the blocks, the stop and whether it names the card, SITTING-RESULT, GATE-STOP), a crash written apart (exit 9), "session end (T0 <T0>)", MANIFEST.sha256 last, wrapper.rc after it | every rest rule of ours reads the log |

`--dry` runs the refusals, then the reference session's own DRY mode with E200's runner, compared with E197's listings but W1: **429, 331
and 277 device calls, LISTING SAME, each with W1's window**; its directory `build/e200/T<T0>-dry` (every rest rule skips it). Exit codes:
E197's, and 12 the die gate (or too little cap left after it).

## 3. The runbook ([`rb/`](rb/); the card lane's brief: [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

Each step a script in E197's form through k6's drivers, unchanged, every box call to aifoundry2 itself; **THE ORDER: Q, 4, 5, 6, 8, then,
once the rest has opened, 7 and 9 back to back.**

| box step | file | what |
|---|---|---|
| 0 | (by hand) | the booking (G); THE ONE-LAB RULE's desk span; `uptime` (THE LOAD RULE); the go's anchor lines; GitHub main; THE QUIET HOLD |
| 1, the window | [`rb/s02_window_e200.sh`](rb/s02_window_e200.sh) `<1\|2> <day> <last start> <last end>` | G+1:30 / G+3:30 from the booking, the 2:00 rule; which plan fits now |
| 2, the desk check | [`rb/s03_desk_e200.sh`](rb/s03_desk_e200.sh) (outside the kit's list) | the window; the pull under the lab-git lock; HEAD descends from 72514ce5, E197's registration (subtree da6c3e89) and kit, E200's registration (subtree c479c271) and kit; the paths clean; the history check; the lists at their pins (35, 39, 17, 19 and the kit's); the harness, **a fwgate record added since the kit read against its committed sources** (check-records OK, one source at least); the preflight GO; the desk tests' logs; **THE FREEZE LINE** (E200.md 0, whole on one line; printed with any later dated note beside E200.md); HEAD unchanged; **no E200 datum in any ref** (E197's data reported, never a gate) |
| Q | [`rb/quiet_e200.sh`](rb/quiet_e200.sh) `raise <lane>`, `count --wait` | THE QUIET DESK FLAG up right before the look; THE P2 COUNT 0 |
| 4, the look | [`rb/s05_look_e200.sh`](rb/s05_look_e200.sh) `[--wait]` | fwgate's look at the desk (no device): CONTINUITY, NEEDS-READ, or 16; et-who and ps as counts, our sessions and jobs, the P2 count; FREE; our login to RB_OUT |
| 5, the sync | [`rb/s07_sync_e200.sh`](rb/s07_sync_e200.sh) | the box read first; harness-e200.json's files, committed and at their sha256, into E200's root |
| 6, the build | [`rb/s08_build_e200.sh`](rb/s08_build_e200.sh) `start`, then `wait` | [`build_e200.sh`](build_e200.sh) detached under `timeout 900` (no -k): E197's proposal built with this box's /opt/et; E197's checks (gates); the ELF report; the host's table SAME (a gate); four refusals (a gate); the signal read (reported); **E200's runner by W1 at 8774027b... (a gate)**; the dry listings SAME x3 but W1 (a gate); **the reader at its pin (a gate)**; at most two starts a day |
| 8, the dry pass | [`rb/s10_dry_e200.sh`](rb/s10_dry_e200.sh) `start`, then `wait` | the wrapper's dry path (sitting 1 both plans; sitting 2 ext), each LISTING SAME |
| 7, the reads | [`rb/s09_reads_e200.sh`](rb/s09_reads_e200.sh) `<1\|2>` | **before anything reaches the card**: the last start, today's build and dry pass, no session or job of ours, **THE REST RULE** ([`rb/rest_rule_e200.sh`](rb/rest_rule_e200.sh)), **no sitting on a day an E200 log holds the die gate's GATE-STOP**, sitting 2's condition, fwgate's look; then the plan and **the first card command stamped** (RB_OUT/e200-<n>-first.txt with FWGATE and FIRSTDIR, once a sitting); then in one box call (each read after a settle of up to 6 s for our device processes and our live collector's reader, lab-monitor) fwgate's read on NEEDS-READ (EQUAL, else 16; 17 held), the reader's pin, the config read kept in step 7's folder, et-who; **the configuration gate** |
| 9, the sitting | [`rb/s11_session_e200.sh`](rb/s11_session_e200.sh) `<1\|2>` | the first card command at most 120 s back and the cap before the last end; on the box k6's guard's first lines, **fwgate's guard over step 7's folder** (identity ok, else IDENTITY-STOP 16), the rest rule again, today's dry pass and build, no second try on a smoke-failed day, no sitting on a die-gate-stopped day, sitting 2's condition, THE P2 COUNT; then `session_e200.sh` detached, DRY, ET_DEVICES and V3_DEVICE unset |
| 10, the wait | [`rb/s20_wait_e200.sh`](rb/s20_wait_e200.sh) `<1\|2>`, while 17 | **the session found by its real script name as its own script** (`ours_live session_e200.sh`); GATE-STOPPED, CRASHED, HUNG (16: kill nothing); the manifest |
| 11, the collection | [`rb/s22_collect_e200.sh`](rb/s22_collect_e200.sh) `<1\|2>` | the box read; one read-only copy back; [`collect_e200.py`](collect_e200.py): COPY-BACK EXACT, **THE BOX-TREE GATE**, the data directory or the gate stop's record, the scrub, facts, SHA256SUMS; k6's desk-path gate; the history check; then Q lowered |
| 12, the commit | (the card lane's, through commit_lab.sh) | `docs/reports/data/<day>-e200-regfile-sitting-<n>-aifoundry2/`, its README in [`DATA-README-FORM-e200.md`](DATA-README-FORM-e200.md)'s form |
| 13, the reduction, after the data commit | [`rb/s24_reduce_e200.sh`](rb/s24_reduce_e200.sh) `<1\|2>` | each committed run/ against the box's manifest, then **`reduce_e200.py`, unchanged, never `--prediction`** (sitting 1: regfile-e200-s1.json; after sitting 2 the pooled regfile-e200.json, E200's registered result), then the checker |

The dry listing of both sittings: [`rb/list_steps_e200.sh`](rb/list_steps_e200.sh) (its desk calls read "run on the Intel": k6's
`rb_local` wording, unchanged; the desk here is aifoundry2 itself).

## 4. The readings stated here before any datum (each kit mechanics, or a stop or gate made stricter for safety, named so)

- **The first card command (E197.md 6, E200.md 8).** Step 7's first command to the card: fwgate's one firmware read when its look reads
  NEEDS-READ, else the config read; both come before every holder check of the session. Step 7 reads the rest and fwgate's look (no
  device) on the box first, then stamps the moment at the desk just before the box call that sends it, once a sitting (a second call keeps
  the stamp and its folder; a stamp whose folder exists already on the box sends nothing and is dropped: 17). Step 9 and the wrapper refuse
  more than 120 s after it.
- **fwgate's read and step 7's folder (kit mechanics).** The read writes its record into `build/e200/first-s<n>-<FIRST>/` beside the config
  read's stdout and stderr; step 9's guard reads that folder as `--extra`; the wrapper requires the folder, its config read, and for FWGATE
  read fwgate's records there all EQUAL (at least one), the newest read on this boot, and copies the folder into the session's `first/`
  (committed with the data, E200.md 8): a second layer of verdict and boot only; fwgate's own guard over the folder, which also reads the
  raw answers, the day, the card and the reference, is step 9's, in the same box call just before the launch (it stopped all 11 of
  verify-e200's attacks). A read that is
  not EQUAL stops E200 on this boot (fwgate's ledger): reported, never retried. If a later round adds `15cb0fcb`'s read to fwgate's records,
  the look reads CONTINUITY and nothing is sent: the harness pins fwgate's records as they were when the kit was made, and step 2's
  harness check names a record added since and passes (fwgate's records are additions only, the history check's rule) once step 2
  has read it against its committed sources (fwgate's check-records OK, and one source at least: a record with none is no read of record;
  fix-e200, verify-e200's F6); the sync carries it, so fwgate reads the same records on the box as at the desk's look (kit mechanics).
- **The configuration gate (E200.md 3) and E194's identity bounds (stricter).** TDP 65 W, threshold 65 C, 600 MHz at rest; /dev/et0_mgmt
  and device ID 0 alone; minion_mv strictly between 450 and 600. The end read is reported, never a gate, and made only while the card reads
  free and no host hung.
- **THE DIE GATE (E200.md 9; its form here, kit mechanics).** In the wrapper, after the free check: every sample of a 1 s read at or below
  57 C passes; a read with no sample (our live collector holding the node) is read again; up to 10 minutes; its stop is counted by the rest
  rules (no "no device opened" words: its reads came after the first card command), and no sitting follows that day: steps 7 and 9 refuse
  a day whose E200 log holds the die gate's GATE-STOP (E200.md 9's "else no sitting that day"; fix-e200, verify-e200's F3).
- **C3 (E200.md 4; its reading here).** The watch judges each train process of a block of trains.tsv once its 13 launch records are in
  (the runner writes a process's mark before its records: a mark with fewer is read again each poll until all 13 are in, a later mark is
  written, or 3 s pass; fix-e200, verify-e200's F2) and the telemetry reaches its last launch's end (at most 3 s late in all): its samples from its first launch's start + 1.5 s to its last launch's end, 800 MHz within 1 MHz (a
  sample with no clock not judged); a process with no record or no sample there is not judged (it neither counts nor resets the run);
  three OFF in a row: STOP, naming the card. The smoke's clock: both smoke train processes, at least one sample in the window, all at 800
  MHz, and the last launch's own count 780-810 MHz; else the kit's smoke check fails (a gate stop).
- **aifoundry2's own lines (E200.md 9).** Board strictly above 85 W on 3 samples in a row (a sample with no board starts the count again);
  minshire[0] or the latch minshire[2] at or above 80 C; E189's lines (65 W distinct readings, 70 C) read first.
- **The free check's re-read (kit mechanics, E194's).** While every holder line is a reader of ours on /dev/et0_mgmt, et-who is read again
  up to 3 times 2 s apart; anything else refuses at once. run_session.sh's own checks read once (registered, unchanged).
- **The desk-test variables (kit mechanics).** `E200_DESKTEST=1` with `E200_CAP_S`, `E200_READER_SHA256`, `E200_DIE_MAX_S`,
  `E200_DIE_POLL_S` (the wrapper; the build and step 7 read the reader's): the card day never sets them; the session's start line names
  DESKTEST when set, and **the collection refuses such a session** unless RB_DESKTEST=1 and --allow-desktest (the runbook test only).
- **Everything else is E197's kit section 4, unchanged:** the plan (full, short, ext by the cap and 900 s of closing steps), the cap and
  the deadline (the first card command + the cap - 120 s; the end-stop at the cap - 30 s), the plain sampler, "no device opened by the
  session", what names the card, sitting 2's condition, no second try on a smoke-failed day, a crash, the data directories and gate stops,
  the scrub, the checker's two readings.

## 5. THE REAL-PATH DESK TEST and the audit of every dry branch

[`desk/desktest_realpath_e200.sh`](desk/desktest_realpath_e200.sh) and [`desk/realpath_e200.py`](desk/realpath_e200.py) run the sitting's
real path, DRY unset, exactly as step 9 launches it, with the stand-ins of [`fake_card_e200.py`](fake_card_e200.py). **Two paces:** the
fast pace (launch_s 0.02, each launch reporting a card's 0.4 s span, the reported timeline running ahead of real time) runs the whole
sittings with the stand-in's "hold" clock (800 MHz from the first host process on); the real pace (launch_s 0.4, real time = reported
time) runs THE CLOCK RULE's cases with the "climb_hold" clock (each process at 600 MHz for its climb, 800 MHz after and between processes)
or the "climb" clock (600 MHz at rest), with E200_CAP_S 420 so that block A runs T2 and the sitting ends after block B's anchors.
Every real-path case runs with E200_DESKTEST=1 and E200_READER_SHA256 (the stand-in reader's), the session's start line naming DESKTEST;
case RP runs without them and is refused by the reader's real pin. **Case WO** (fix-e200) runs the real watch alone on scratch files written in the runner's own order (a process's mark first, its records after it): records late, split, or never written. **The audit** ([`desk/dry-branches-e200.tsv`](desk/dry-branches-e200.tsv)):
every line of `session_e200.sh` that branches on its dry mode, of E197's `run_session.sh` that branches on DRY and the real-path regions its
DRY block skips, and of E197's lab runner that branches on `a.dry` (E200's runner's lines are E197's: W1 touches two window words), each with
the cases that run it; the test reads the files' own lines and fails if one has no row, a row's text differs, or a named case did not pass.
**NOT RUN, each with why** (E197's, unchanged): run_session.sh line 87 (a several-card host), its "et-who --check failed" branches, the
stopwatch's first-60-s branch, line 196's STOP between the smoke and block A, the pvt sampler branch, the runner's mid-train cut.

## 6. Device commands

`dmcmd_audit_v2.py` with its table v2 on the sittings' file set (`preflight_e200.sh`: the wrapper, the watch, the checker, the build, the
harness, E200's guard, E197's run_session.sh, stopwatch.py and lab runner (from which E200's runner is made: W1 adds no command), the
host's main.cpp, regfile_args.h, the kernel's regfile.c, E194's common module, fwgate.py): **GO, 12 send sites, 0 disallowed, every one a
READ**, no allow-list and no exception: E200's guard's `config` (5 READs: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS,
GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) and `sample` (6 READs a sample: GET_MODULE_POWER, GET_SP_STATS,
GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES), the reader resolved to its reviewed variant
(`build/ettelem-hpl` = ettelem-dv2); fwgate's `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (READ in the table v2, id 14, by the owner's rulings:
"Firmware revisions query was a false positive. It should have never been forbidden. Reading operations and firmware are always allowed.",
Sun 15 Nov 2026 15:07:01 PST; "Yeah, fix the corresponding guards. I don't want to modify firmware, but commands which read firmware should
be fine.", 15:09:49 PST), sent once a boot, only on NEEDS-READ. run_session.sh's `"$ETTELEM" sample` and the wrapper's die gate resolve
through the wrapper's own lines to the guard. The host opens the ops node only; `et-who --check` sends no device command. **Never sent by any
file of E200:** a statistics reset, any `DM_CMD_SET_*`, a governor, TDP, threshold or clock set, a reset or power cycle, a PMIC write, a
firmware change, a KILL to any process.

## 7. What the checker reads after the reduction (`check_e200.py checks`)

E197.md 8's rows as E200's reduction reports them, in E197's words with their numbers, but **the clock row read by C1** and **THE CLOCK
RULE's tallies per session** (the median clock and whether it is 800 MHz; processes judged, kept, set aside by the median, by samples after
1.5 s, by a missing last launch, by the own count; launches asked, not read before 2.0 s, read, unmatched; the anchors' windows), from the
reduction's `e200` key; a result without that key is refused (exit 3). Nothing is scored against any forecast. E197's REPORTED row
"rail voltage samples beyond +-3 mV of the session median in the train's spans" reads high by design on this card: every train process's
span includes its climb, run at the 600 MHz point's lower voltage, so a high count there is no rail fault (fix-e200, verify-e200's F8; the
data README form says so).

## 8. The host-output parser and the real bytes (the round's lesson of Sun 15 Nov 2026)

[`desk/realbytes_e200.py`](desk/realbytes_e200.py) makes E200's runner as the kit does and executes its parse loop (E197's lines 204-212,
unchanged by W1) on real card bytes: E191's split (dropped at every interior offset; kept before and after), **this card's committed host
output** (E194's 32 host stdouts and E190 arm A's 84 process stdouts: every line the host's own; the runtime's device table on stderr),
aifoundry3's (E193's, E192's), stand-ins, and the E197 host's print discipline (one printf a line, at most 1,554 B, under PIPE_BUF). **The
kit's reading, stated before any datum: a split cannot occur on aifoundry2 by these readings; no amendment is proposed;** the residual (a
newline-less fragment glued to a line) fails safe (a smoke gate stop, or one process's value lost). E197's own outputs are not committed at
this kit's HEAD (E197 has not run): NOT RUN.

## 9. reg-e200's open issues, answered

| reg-e200 | what | here |
|---|---|---|
| 1 | the freeze line: none at the registration | **registered by fix-e200 before the land** in E200.md 0 (sha256 2eba6ef4..., #2.5.1.2.3, 01:28:51 PST Mon 16 Nov 2026); step 2 checks it whole on one line and prints it, with any later dated note beside E200.md; first stated as: fix-e200 adds it from the orchestrator's record of posted hashes (E200.md 0), or a dated note before the first datum; nothing in the kit reads it |
| 2 | re-pin if E197 lands with other bytes | E197 landed byte for byte (subtree a4fe6d55, the registration's da6c3e89; land-e197's anchor lines all SAME): no re-pin needed |
| 3 | T15 at the cap | unchanged (E200.md 10): the runner's own rule skips it at long climbs; never a failed check (CARD-LANE-BRIEF.md 6) |
| 4 | the rail share includes the climb | REPORTED, unchanged |
| 5 | the governor in E197's 0.43 s gap | the stand-in climbs every process again (the conservative reading); C1, C2 and C3 hold either way |
| 6 | the kit must add C3, fwgate with dmcmd_audit_v2, the configuration and die gates, the runner made from W1, a climbing stand-in sampler | all added (sections 1-4; the stand-in's three clocks, section 5) |

## 10. What the desk found, and what it cannot show

1. **A session cut short reads a 600 MHz median and gives no datum (REPORTED, registered behaviour).** C1's session clause sets aside every
   process of a session whose median clock is not 800 MHz (E197's rate R is computed at that median). On the card a whole sitting's trains
   fill it (about 37 of 46 minutes at 800 MHz), but the real-pace case RCM (a sitting cut by the cap after T2, idle most of its time at the
   stand-in's 600 MHz rest) reads a 600 MHz median: 18 of 18 processes set aside, T2 NOT SCORED. A sitting stopped very early (more idle
   than trains) would give no datum. Not changed (the reduction is registered); stated for the verifier and the readiness critic.
2. **The host on this card:** the desk ran the real host only to its table and its refusals; its launches, its REGFILE lines and the
   runtime's teardown meet the card first in the smoke (C3 reads the smoke's own counts before any train).
3. **The governor's climb:** the stand-in's climbs (0.9 s, 1.4 s, 1.6 s, steps to 700 and 600 MHz) are test values; the card's are E190 arm
   A's measured 0.01-1.33 s.
4. **The box's reader and holder check** meet the session first on the day (step 7 reads the config through the same guard just before).
5. **Our live collector's single-open reads** meeting run_session.sh's own free check (read once, registered): a collision there is a gate
   stop before the sampler, tried again in a new RB_OUT; not measured.
6. **fwgate's real read** (the vendor CLI on this card): only its desk stand-in answered here; fwgate's own tests cover its parse on the
   committed answers. Step 7 waits up to 6 s for no device process of ours and no read of our live collector's reader before it (the collector
   reads through a copy of the reader named lab-monitor, which DEV_COMM does not match: fix-e200, verify-e200's F4; a busy node
   would stop E200 for the boot, fwgate's README); not measured.
7. **The collection** ran on stand-in sessions (the real-path test's and the runbook test's), not on a card's.
8. Card time waits on the owner's standing go and the round's readiness check (CARD-LANE-BRIEF.md 1).

## 11. Files (all new, under tools/claims-v3/e200/)

| file | what |
|---|---|
| `session_e200.sh` | the sitting's wrapper on the box (section 2) |
| `watch_e200.py` | the kit's watch: its live stops with aifoundry2's lines, C3, the smoke check with the smoke's clock, the end-stop, the hang watch |
| `check_e200.py` | drycmp (W1), the summary, the checker with C1's tallies |
| `ettelem_guard_e200.sh` | the only way to the reader (mode 100755) |
| `harness_e200.py`, `harness-e200.json` | every file the box runs or reads, at its sha256 (a fwgate record added later: named, synced, not pinned) |
| `build_e200.sh`, `preflight_e200.sh` | the box build (E200's runner by W1, the reader's pin) and dmcmd_audit_v2 on the sittings' files |
| `collect_e200.py` | COPY-BACK EXACT, THE BOX-TREE GATE, the data directory or the gate stop's record, the scrub, facts, SHA256SUMS |
| `fake_card_e200.py` | the stand-ins for the desk tests (never on the box) |
| `desk/desktest_realpath_e200.sh`, `desk/realpath_e200.py`, `desk/dry-branches-e200.tsv` | the real-path desk test and its audit table |
| `desk/realbytes_e200.py`, `desk/checks_e200.py` | the real-bytes parser test; the quick set |
| `rb/` | the runbook's steps (s02 s03 s05 s07 s08 s09 s10 s11 s20 s22 s24), its common file, the quiet desk flag, the rest rule, the history check, the dry listing, and the desk tests of the runbook, of fwgate's calls and of the rest rule |
| `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e200.md` | the card lane's brief; the data README's form |
| `logs/` | every check above |
| `SHA256SUMS-e200-kit` | the kit's files (step 2 aside) and its logs |

**Step 2 (`rb/s03_desk_e200.sh`) is outside `SHA256SUMS-e200-kit`** (a file cannot hold the sha256 of a list that holds its own): its own
sha256 and the list's are given in the land file's anchor lines.

## 12. Labels, and compute

Every figure quoted from E200.md or E197.md (the trains, the caps, the stops, the rests, the window, the pins) is **registered**; the
committed records the tests read (E191's split bytes, E194's and E190 arm A's host output on this card, E194's session log, E193's and
E192's outputs) are **desk reads of committed records**; the tests' results are **desk checks of code**, not measurements; every watt,
degree and clock in them is a stand-in's arbitrary test value. Nothing here is blind, held out or post hoc; no E200 datum exists. Compute:
on aifoundry2 through the round's CPU slot at nice 10; the runbook test's real build with -j4; every run of a built host, the session, the
runner or a stand-in inside the no-device sandbox, and only while THE QUIET DESK FLAG was absent; the real-path cases four at a time in
their own sandboxes; no simulator, no other box, no card.

## 13. Fixed before the land (fix-e200): verify-e200's findings

verify-e200 (Q192) verified the registration and this kit before the land: HOLDS WITH FIXES, one fix required before the land (F1), three
minors and five nits. fix-e200 answered each, before any E200 datum, and ran every desk test again on the fixed state:

| finding | what | here |
|---|---|---|
| F1 (required) | the freeze line was in no E200 file | registered in E200.md 0 (sha256 `2eba6ef4...`, #2.5.1.2.3, 01:28:51 PST); the registration's list and subtree re-made (`3e3e7d40...`, `c479c271...`) and every pin of the kit on them moved (step 2's PINS line and `want=` subtree, `rb/check_history_e200.py`'s REG_SUBTREE, this file's header); step 2 checks the freeze line whole on one line and prints it, with any later dated note beside E200.md (E199's step 2's form); the logs, the kit's list and step 2's KITPIN re-made |
| F2 (minor) | C3 could judge a process before the runner had written its records | `watch_e200.py` judges a mark only once its 13 records are in, a later mark is written, or 3 s pass; real-path case WO (records late, split, never written) |
| F3 (minor) | "else no sitting that day" after a die-gate stop was not enforced | steps 7 and 9 refuse a day whose E200 log holds the die gate's GATE-STOP: no card command, no launch; runbook cases DG7, DG9 |
| F4 (minor) | step 7's settles did not see our live collector's reader | both settles also wait for `lab-monitor` (the collector's copy of the reader); the texts corrected (section 10 item 6, the brief, step 7's comments) |
| F5 (nit) | the wrapper's firmware-record check is a partial second layer; its words said "alone" | its words now say what it checks (every record EQUAL, one at least, the newest read on this boot); fwgate's full guard stays step 9's, in the same box call just before the launch; the optional second guard call in the wrapper was not added (the real-path test's stand-in records are not fwgate's own reads) |
| F6 (nit) | a fwgate record added after the kit was trusted unread | step 2 reads it with `fwgate.py check-records` (desk, no device) and requires one committed source at least; the runbook test's stand-in record now carries E194's committed read (`15cb0fcb`) as its source, and case P5 adds one with none: refused (16) |
| F7 (nit) | the flag's form | THE QUIET DESK FLAG is raised and lowered only with `rb/quiet_e200.sh` (`raise card-e200` writes `e200 card-e200 <time>`); a flag written by hand in the round's `<lane> <time>` form makes every step refuse (the safe side); the brief says so, and the readiness check's go lines should name the call |
| F8 (nit) | the rail-voltage report row reads high by design | said so in section 7 and in the data README form |
| F9 (nit) | E200.md 9's top line | reworded in E200.md, its arithmetic unchanged |

The verifier's observation (case RCM, registered behaviour: a sitting cut very short reads a 600 MHz session median and gives no datum) is
unchanged; it is section 10 item 1, for the readiness check.

SPDX-License-Identifier: Apache-2.0
