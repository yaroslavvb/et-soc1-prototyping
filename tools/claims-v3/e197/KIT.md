# E197's run kit: the proposal's reference session as registered (the lab's runner, departure D1) driven on aifoundry3 card 0 with the box's own tools, two sittings, the first card command at step 7's read with the rest read before it, the kit's watch (its live stops, its smoke check, the end-stop and a hang watch that never kills), the runbook from aifoundry2 from the window to the reduction after the data commit, THE REAL-PATH DESK TEST with its audit of every dry branch, and the host-output parser fed real card bytes (Q185; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q185, lane `kit-e197`; the verifier's fixes and the registration's new pins
by Q191's lane `fix-e197`, from 22:07 PST the same day; the second verifier's two fixes, the registration's pins again and every
desk test re-run by Q191's lane `fix2-e197`, Mon 16 Nov 2026 from 00:12 PST; all before the land). No card was claimed or opened (aifoundry2 has a card:
every desk test that ran the session, the runner, a stand-in or a built host ran in the round's CPU slot inside the no-device sandbox, each
case in a sandbox of its own), no device command was sent, no other box was reached, nothing was posted, no simulator ran. New files only,
all under `tools/claims-v3/e197/`, on the registration's commit (the registration with redaction R1, a local commit on GitHub main `391b459b`; its
`tools/claims-v3/e197` subtree `da6c3e89...`; `SHA256SUMS-e197-registration` `992a35e5...`, 35 entries), every file of which stays as
committed. This is the kit E197.md 18.2 asks for. **No E197 datum exists, and the forecast stays sealed (sha256 `e8e1746e...`): no
forecast number is in any file here, and nothing here scores against it.** Nothing here changes a train, a kind, a value, the order, a
window, a threshold, a stop of the registration, a cap or the reduction; the kit adds stops that end a sitting early (E197.md 9 allows it).
Where E197.md leaves a reading to the kit, it is stated in section 4 before any datum.*

## Results first (desk checks of code; nothing is measured)

Python everywhere: `/usr/bin/python3` 3.12.3 on aifoundry2; cmake 3.28.3, riscv64-unknown-elf-gcc "() 15.1.0" and g++ 13.3.0 from this
box's /opt/et for the desk build and the runbook test's real build. Every watt, degree and rate in a test is a stand-in's arbitrary test
value, never a forecast and never a measurement.

| check | result | log |
|---|---|---|
| **THE REAL-PATH DESK TEST**: `session_e197.sh`'s real path, DRY unset, exactly as step 9 launches it, and through it the reference session with the lab's runner, against stand-ins for every device tool (the sampler behind the box's own copy of E128's guard, et-who, ps, a host printing REGFILE lines in the real host's form), each case in its own sandbox (two regular files at /dev/et0_ops and /dev/et0_mgmt, a private /run/lock with the card's lock, a private PID namespace, the host name aifoundry3): the dry path (three plans); **sitting 1 whole, full and short, and sitting 2 whole, their host processes in the registered order call for call, then the registered reducer on their own files and the pooled reduction**; every stop (by hand, in a block and in the gap; the kit's board stop at its own boundary, the clock stop, the die, a quiet sampler, a missing die field, no sample at all; a signal to the wrapper and to run_session.sh; the watch killed; two failed processes; a timeout end); the smoke (the runner's gate: check_bad, letters, rates; the kit's smoke check: participants, an anchor's exit); **runtime lines in the host's output with E191's committed bytes** (inside a line: the smoke stops, the safe side; between lines: harmless); the holders and the lock at the start, after the sampler and between blocks; **a HUNG host (no KILL)**; a crash; the cap; every refusal; run_session.sh's own refusals run alone; the watch's end-stop alone; and the audit of every dry branch | **DESKTEST-REALPATH-E197 401 of 401 PASS** (62 cases, R7b added by `fix-e197`: the first card command 300 s back, refused by the 120 s bound; the watch's end-stop alone, the audit; the session's whole sittings at a fast stand-in pace: P 437 s, SH 409 s, P2 163 s) | [`logs/desktest-realpath-e197.txt`](logs/desktest-realpath-e197.txt) |
| **the runbook** with a fake ssh and rsync on a stand-in box: the window rule, the lab-git lock (absent and nested), step 2 at every pin, the history check and its shadows, no E197 datum in any ref, the sync, **the real build on the stand-in box** (make_images and check_elf, the host's table SAME, its four refusals, its signal read, the session's dry listings SAME x3), NO-THIRD-BUILD, a login link (into a COPY of the round's lock file), a hang, a cut wait, the dry pass, **the rest at step 7 before any card command (no config read sent)**, the stamp kept, step 9 refused 11 minutes after step 7, sitting 2's three refusals at step 7 (no config read sent), no second try on a smoke-failed day, **the real session launched and found by the wait by its real script name**, its gate stop collected as a gate stop's record, the retry in a new RB_OUT, the wait on the real-path test's sessions (whole, stopped, gate-stopped, crashed, hung), the collection, step 13 before and after the data commit, the data README form's own re-make commands (the same json, byte for byte), and sitting 2's pooled reduction | **SELFTEST-RB-E197 23 of 23 PASS** (F1b added by `fix-e197`: step 9 refuses a stamp 300 s back) | [`logs/selftest-rb-e197.txt`](logs/selftest-rb-e197.txt) |
| **the host-output parser on real bytes**: the registered runner's own parse loop (lines 204-212, taken from its syntax tree) on E191's committed split bytes (at every offset of a REGFILE line), on aifoundry3's committed host output (E193's four device-stdout files; E192's and E193's launch records; E192's device stderr), on stand-in streams with runtime lines, and the E197 host's print discipline | **REALBYTES-E197 23 of 23 PASS** (section 8) | [`logs/realbytes-e197.txt`](logs/realbytes-e197.txt) |
| **the rest rule**: E183's, E189's, E192's, E193's, a later kit's (E195) and E197's own forms (sitting 1 read before sitting 2), dry passes and gate stops that opened no device skipped, a cut session at its run's latest write, energy.sh's folders, the newest of several, and the real-path test's own sitting 1, gate stop and dry pass | **SELFTEST-REST-E197 19 of 19 PASS** | [`logs/selftest-rest-e197.txt`](logs/selftest-rest-e197.txt) |
| the dry listing, both sittings, every step with stand-ins | **25 steps listed, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e197.txt`](logs/dry-listing-e197.txt) |
| `dmcmd_audit`, every file whose commands the sittings send (`preflight_e197.sh`) | **GO, 11 send sites, 0 disallowed, every one a READ**, no allow-list and no exception (section 6) | [`logs/dmcmd-audit-e197.txt`](logs/dmcmd-audit-e197.txt) |
| the harness, the history check's names, and the kit's checker on the registration's own synthetic sessions | harness CHECK PASS and HARNESS OK (45 files); the checker's CHECKS READ on the exact, noisy and stop sessions (the noisy T11 NOT SCORED by its rate gate as the reducer decides); the summary's stop classes; drycmp's negative control | **CHECKS-E197 14 of 14 PASS**, [`logs/checks-e197.txt`](logs/checks-e197.txt) |

## 1. The session: the proposal's reference session as registered, driven with the box's tools (no lab port)

`session_e197.sh` runs the reference session E197.md 5 registers: `proposal/src/run_session.sh`, `proposal/src/stopwatch.py` and
`proposal/src/trains.tsv`, with **the lab's runner `lab/run_trains.py` in place of `src/run_trains.py` (departure D1: `timeout 10`, never
a KILL)**, all four at the registration's sha256, unchanged. **Why the registered runner and not a port:** E197.md 5 registers the
reference session's own protocol (the blocks, the trains, their order, the processes and orientations, the anchors, the idles, the
smoke and its gate, the stops, the 30 s gaps with the holder check, the deadline) by its code; a port would have to re-make every one and
prove it equal, and the session already carries the lab's rules the kit needs (one card, `et-who --check` with only the session's sampler
exempt by its process id, the card lock opened read-only per block and kept by every device process's descriptor, the sampler stopped by
SIGTERM only, the signal trap). run_session.sh runs the runner and the stopwatch from its own folder, so the wrapper copies the four
files into the sitting's `ref/` and checks each there against the registration's list. The wrapper adds only what E197.md 18.2 asks, each
before the session or through the registered stop file `OUT/STOP`:

| the wrapper's step | what | why |
|---|---|---|
| 1 | refusals before anything (exit 2, "no device opened by the session"): the host's name aifoundry3 (hostname and Python's); USER the login; harness-e197.json at the sha256 the launch passes, every file of it at its pin (`harness_e197.py --box`: the registration's 35 among the 45); the registration's list at `992a35e5...`; the host, E128's guard and the box's sampler present, the host the one today's build recorded; `preflight_e197.sh` GO; **exactly /dev/et0_ops and /dev/et0_mgmt**, by name; `ref/`'s four files at the registration's sha256; on the real path the first card command today and at most 120 s back (FIRST_MAX), its cap before the window's last end, and the card's lock file present | nothing runs that is not pinned; one card; no device opened before these (E197.md 3) |
| 2 | the free check (et-who --check within 30 s, no other user's device process, a probe of the existing card lock: exit 3, "no device opened by the session") | E197.md 5 |
| 3 | `CAP_S` = the cap - 60 s - (now - the first card command), never more than the window's last end - 120 s - now; ETTELEM = E128's guard | section 4 (the cap, the deadline) |
| 4 | **the kit's watch** (`watch_e197.py`) beside the reference session; a watch that dies while the session runs is a stop (the wrapper writes STOP); a signal to the wrapper writes STOP and waits for the session's own end | section 4 (the kit's stops) |
| 5 | the reference session, `run_session.sh <OUT> full\|short\|ext`, with H (the host built that day), ETTELEM, GAP 30, LOCK; ET_DEVICES, SAMPLER, DRY unset | E197.md 5 |
| 6 | when run_session.sh exits before its own EXIT trap (its refusals, its free check), the wrapper writes OUT/SESSION_DONE itself (one JSON line naming it: E192's fix 1), so the watch and the stopwatch end | E192's kit, verify-e192's finding 1 |
| 7 | the summary (`check_e197.py summary`): the runner's smoke gate, the kit's smoke check, the blocks begun and complete, the deadline's marks, the stop and whether it names the card, `SITTING-RESULT: ...` (step 7 and step 9 read it before sitting 2), and `GATE-STOP: ...` when no block of trains.tsv began; a crash written apart ("the trains ended without a registered stop": exit 9); the card time from the first card command; "session end (T0 <T0>)" in the kits' form; MANIFEST.sha256 last, wrapper.rc after it | every rest rule of ours reads the log; the collection's exact copy-back reads the manifest |

`--dry` runs the same refusals, then the reference session's own DRY mode (every device call printed, nothing opened), compared by
`check_e197.py drycmp` with the registration's `desk/dry-e197-<plan>.txt` (the host and OUT written as the registration's, the clock stamps
dropped): **429, 331 and 277 device calls, LISTING SAME**. Its directory is `build/e197/T<T0>-dry`, every line marked DRY: every rest rule
skips it. Exit codes: 0 done (every block, or the runner's deadline skipped or cut trains); 2 a refusal; 3 the card not free, or a
holder between blocks; 9 a crash; else the reference session's own (75 the lock busy, 7 the smoke gate, 8 a stop by the stop file: the
kit's watch, the stopwatch, the wrapper or by hand, so a registered stop after the trains began ends 8, not 0; 4 telemetry, 5 failing
device processes, 6 hot, 128 + n a signal). No step reads this code: step 10 reads the session log (the sentence corrected by
`fix-e197`, verify-e197's F4).

## 2. The box: E197's root, the sitting's directory and the box's tools

- **E197's root** is `build/claims-v3/aifoundry3/e197` under the box's tree (`~/aifoundry`): a folder of ours, never another session's
  tree (the proposal's BUILD.md names a folder of its own; E192's and E193's kits put theirs here, where the rest rules' "latest write of a
  cut run" reads it). Step 5's rsync -R puts each harness file at its repository path there; step 6 builds into its `build/regfile` and
  writes `build/regfile-built.txt` there.
- **The sitting's directory** is `build/e197/T<T0>/`: session.log, first-card-command.txt, harness.txt, preflight.txt, run_session.out,
  watch.jsonl, watch.out, summary.txt, `ref/` (the four registered files), `run/` (the reference session's OUT: telemetry.jsonl,
  runs.jsonl, marks.jsonl, stderr.txt, session.log, sampler.err, stopwatch.err, STOP and SESSION_DONE when there), MANIFEST.sha256,
  wrapper.rc.
- **The box's tools**, unchanged: the sampler `build/ettelem/ettelem`, the box's own build, through E128's guard (the audit table's
  reviewed variant 'ettelem'; `sample --seconds --every-ms` and `config` only; every aifoundry3 kit's); `et-who --check`
  (/usr/local/bin: it stats, never opens a node); the card lock `/run/lock/etsoc-shire0.lock` (opened read-only, never created);
  coreutils' `timeout` (never `-k`); util-linux's `flock`.

## 3. The runbook from aifoundry2, both sittings ([`rb/`](rb/); the card lane's brief: [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

Each step a script in E193's form through k6's drivers, unchanged (a 15 s hard-killed probe; 60 s for a read, 600 s for a copy, one bounded
wait, a detached launch; a printed login link stops the step with 11 and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`,
nothing retried). **One RB_OUT per sitting.** **THE ORDER: 5, 6, 8, then, once the rest has opened, 7 and 9 back to back.**

| box step | file | what |
|---|---|---|
| 0 | (by hand) | `uptime` (THE LOAD RULE), the go's anchor lines, GitHub main |
| 1, the window | [`rb/s02_window_e197.sh`](rb/s02_window_e197.sh) `<1\|2> <day> <last start> <last end>` | the window for that sitting, today only; which plan fits now |
| 2, the desk check | [`rb/s03_desk_e197.sh`](rb/s03_desk_e197.sh) (outside the kit's list) | the window; the pull under the lab-git lock (never nested: 16); HEAD descends from e8a85229, the registration (by its content and subtree `da6c3e89...`) and the kit; the paths clean; the history check ([`rb/check_history_e197.py`](rb/check_history_e197.py)); both lists at their counts and their own bytes; lists not pinned reported; the harness re-made and at its sha256; the preflight GO; the desk tests' logs; HEAD unchanged; **no E197 datum in any ref** (none before sitting 1; only sitting 1's own before sitting 2) |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged (sends nothing to the card) |
| 3, the post | (the card lane's) | the owner's standing waiver, unless his go names a post |
| 5, the sync | [`rb/s07_a3_sync_e197.sh`](rb/s07_a3_sync_e197.sh) | the box read first (no session or job of ours; E197's root made), then harness-e197.json's files, committed and at their sha256, into E197's root |
| 6, the build | [`rb/s08_a3_build_e197.sh`](rb/s08_a3_build_e197.sh) `start`, then `wait` | the detached job [`build_e197.sh`](build_e197.sh) under `timeout 900` (no -k): cmake with the box's /opt/et; `make_images.py --check` and `check_elf.py` (gates: E197.md 11); the ELF report (beside the desk build's `feafba8d...`/`ce8c93c6...`, never a gate); **the host's table byte for byte the registration's** (a gate); four refusals before the device layer (a gate); **the host's signal handling re-read on this build** (SIGNAL-READ, reported); the session's dry listings with this host (LISTING SAME x3, a gate); the hashes in build/regfile-built.txt; **at most two starts a Pacific day** |
| 8, the dry pass | [`rb/s10_a3_dry_e197.sh`](rb/s10_a3_dry_e197.sh) `start`, then `wait` | the wrapper's dry path on the box (sitting 1 both plans: the plan is chosen later; sitting 2 ext), each LISTING SAME; RB_OUT/e197-<n>-dry-ok.txt |
| 7, the reads | [`rb/s09_a3_reads_e197.sh`](rb/s09_a3_reads_e197.sh) `<1\|2>` | **before anything reaches the card**: the last start, today's build and dry pass, no session or job of ours, **THE REST RULE** ([`rb/rest_rule_e197.sh`](rb/rest_rule_e197.sh)) read on the box, and for sitting 2 sitting 1's SITTING-RESULT; then **the plan decided and the first card command stamped** (RB_OUT/e197-<n>-first.txt, once a sitting); then k6's reads, unchanged (`../q141k-runbook/k6/s09_a3_reads_k6.sh`: the config through E128's guard, TDP 0 W / 65 C / 600 MHz, never set; et-who clean) |
| 9, the sitting | [`rb/s11_a3_session_e197.sh`](rb/s11_a3_session_e197.sh) `<1\|2>` | the first card command at most 120 s back and the plan's cap before the last end; k6's guard, the rest rule again, today's dry pass and build, no second try on a day the sitting's smoke failed, for sitting 2 sitting 1 held first and no crashed sitting 1; then `session_e197.sh` detached, DRY unset |
| 10, the wait | [`rb/s20_wait_e197.sh`](rb/s20_wait_e197.sh) `<1\|2>`, while it says 17 | the session found by its real script name; a gate read only from its own `GATE-STOP:` lines (16); a crash only from "the trains ended without a registered stop" (CRASHED, 16); **a HUNG line read at once, ended or not (16: kill nothing)**; the manifest |
| 11, the collection | [`rb/s22_collect_e197.sh`](rb/s22_collect_e197.sh) `<1\|2>` | E183 note 5's gate inputs first; how the session ended, read on the box; one read-only copy back; [`collect_e197.py`](collect_e197.py): COPY-BACK EXACT, **the data directory, or for a sitting that ended before any block its gate stop's record under `docs/reports/gate-stops/`**, the scrub, facts, SHA256SUMS; the desk-path gate as E183 note 5 ported it for aifoundry2; the history check |
| 12, the commit | (the card lane's, through the lab's commit script) | `docs/reports/data/<day>-e197-regfile-sitting-<n>-aifoundry3/`, its README in [`DATA-README-FORM-e197.md`](DATA-README-FORM-e197.md)'s form, or the gate stop's record with that file's gate-stop form |
| 13, the reduction, after the data commit | [`rb/s24_reduce_e197.sh`](rb/s24_reduce_e197.sh) `<1\|2>` | each committed run/ checked against the box's manifest, then **the registered reducer, unchanged, never `--prediction`** (sitting 1 alone: regfile-e197-s1.json; after sitting 2 the pooled reduction of both: regfile-e197.json, E197's registered result), then the kit's checker; its outputs to RB_OUT, committed by the records lane |

The dry listing of both sittings: [`rb/list_steps_e197.sh`](rb/list_steps_e197.sh). Its lines "run on the Intel" are k6's `rb_local`
wording, unchanged: they mean the desk (aifoundry2).

## 4. The readings stated here before any datum (where E197.md leaves a choice to the kit)

- **The first card command is step 7's config read.** E197.md 6: "the first command of the sitting that reaches the card or its
  management node (a configuration read included) or the sitting's first holder check, whichever comes first". Step 7's `ettelem config`
  (five READs through E128's guard) reaches the management node and comes before every holder check of the session (the wrapper's free
  check and run_session.sh's); k6's look (step 4) is the runbook's look at the box, not the sitting's holder check: `et-who` runs
  `et-holders`, which stats the nodes and never opens them, so it sends nothing to the card (E193's data note 1 read it so; E197.md 18.2
  lists the look apart). Step 7's wrapper stamps the moment just before k6's call (no command of the sitting reaches the card before it)
  into RB_OUT, **once a sitting** (a second call keeps the first stamp: step 7 again after its 17), and step 9 passes it to the wrapper.
  **The rest is read by step 7's wrapper on the box before the stamp, so nothing reaches the card for a sitting before its rest has
  opened** (E192's data note 1's lesson, E197.md 6's sentence). Step 9 refuses more than 120 s after the stamp (16), and the wrapper again
  on the box (FIRST_MAX), so the cap's loss to the steps between stays inside the deadline's margin (the table under "The cap and the
  deadline"; both bounds were 600 s until `fix-e197`, verify-e197's F2); a try that passes that bound needs a new RB_OUT and its own
  step 7 (step 1, step 6's wait, step 8, then 7 and 9: the runbook test's retry RT).
- **The second sitting is part of E197** (E197.md 6 registers it, the lab's choice, before any datum: request.md section 10 leaves it to
  "the lab session's and the owner's call", and the post offers it). The kit carries it whole: its own RB_OUT, window, dry pass (the ext
  plan, 277 device calls), step 7 (the rest 40 minutes after sitting 1's end, and sitting 1's SITTING-RESULT read before any card
  command), launch, wait, collection and data commit, and step 13's pooled reduction of both sittings (regfile-e197.json, E197's
  registered result; sitting 1's own regfile-e197-s1.json stays beside it). The owner can withhold it (CARD-LANE-BRIEF.md 1, G2).
- **The plan** (E197.md 6, the lab's reading): sitting 1 runs the full plan when, at its first card command, the time left to the window's
  last end holds the full cap (3,000 s) and the kit's closing steps (900 s: the collection must start 10 minutes before the last end);
  else the short plan (2,400 s + 900 s); else no sitting that day (16, nothing sent). Sitting 2 runs the ext plan (2,100 s + 900 s). Step 7
  decides and logs it before its stamp; the plan is never switched mid-sitting. Step 8 lists both of sitting 1's plans in advance.
- **The cap and the deadline** (E197.md 10): run_session.sh counts CAP_S from its sampler's start and sets its deadline 60 s before
  that; the wrapper sets CAP_S = the cap - 60 s - (now - the first card command), so the runner's deadline falls at the first card
  command + the cap - 120 s (plus the few seconds of run_session.sh's own free check), never past the window's last end - 180 s (E193's
  kit's margin). Why 120 s and not 60: a block that starts just before the deadline still runs its 10 s idles and its six anchors
  (about 68 s at a card's pace) and the next 30 s gap before the session ends; with the deadline at the cap - 120 s even that ends inside
  the cap, and **the watch's end-stop at the first card command + the cap - 30 s** (a STOP: the launch in flight finishes, never a kill)
  bounds what is left. The margin, for the readiness check: at the proposal's 5.7 s a train process (E193's 12-launch spans on this card
  read 4.82 s for 12 launches, 0.402 s a launch, and its device opened in 0.18 s), sitting 1's full plan runs about 45 minutes from the
  sampler's start. **What the gap from step 7's stamp to the sampler's start costs** (desk arithmetic: verify-e197's timing model of
  run_session.sh and the lab's runner, run again by `fix-e197`; the runner starts a train only when n x 6.2 s + 30 s fit before its
  deadline, and a block that loses trains ends with its anchors and is reduced as it stands; the gap is at most about 125 s now, since
  step 9 and the wrapper refuse past 120 s and the sampler starts a few seconds after the wrapper's check):

  | plan (cap) | 5.5-5.7 s a process | 5.8 s | 5.9 s | 6.0 s | 6.1 s | 6.2 s | at the old 600 s bound (5.5-5.8 s) |
  |---|---|---|---|---|---|---|---|
  | sitting 1, full (3,000 s) | whole | whole | T15 lost from a gap of about 120 s | T15 from about 90 s | T15 from about 30 s | T15 at any gap; T12 too from about 120 s | T13, T12 and T15 lost; at 5.8 s all of block D |
  | sitting 1, short (2,400 s) | whole | T12 lost from about 120 s | T12 from about 90 s | T12 from about 60 s | T12 from about 30 s | T12 at any gap; T13 too from about 120 s | three or four trains lost (T8, T10, T13, T12) |
  | sitting 2, ext (2,100 s) | whole | whole | whole | whole | whole | whole | every train lost (T1, T7, T14) |

  At the planned 5.7 s a process every plan is whole at any gap the bounds allow; at 6.2 s the full plan loses T15 whatever the gap
  (the runner's own rule); a short gap keeps every other train, so step 9 follows step 7 at once. The wrapper refuses a session with less than 300 s of CAP_S left (no
  block could run).
- **The sampler: the plain one, through E128's guard** (E197.md 4: the lab's choice unless a dated kit note chooses the per-sensor
  sampler; none does). `sample --seconds <CAP_S + 600> --every-ms 100`, no statistics reset; the reduction and the stops read only the
  fields both samplers give. **Why not the per-sensor sampler request.md prefers** (E192's kit audited its command as a READ, its G3):
  it would change no reading (the same five fields), and it is a second path, run_session.sh's `SAMPLER=pvt` branch, that no desk test
  of this kit runs and whose commands this kit's device-command audit does not cover, so it would meet the card day untested for no field the
  reduction reads.
- **The kit's stops** (`watch_e197.py`; E197.md 9's "the box's, the kit's"): board power at or above 65 W on three distinct readings in a
  row (the stopwatch's "distinct readings" rule; the proposal's own stop is above 65 W), a die reading at or above 70 C, a minion clock
  other than 600 MHz or missing on three samples in a row. **The kit's smoke check:** the runner's smoke gate reads neither the
  participants nor the smoke's anchors, so once its gate mark reads ok the watch reads every smoke launch (ok, check_bad 0, 1,024
  participants) and every smoke device process (exit 0, at least two launches; a train process 13): else STOP within block A's first 10 s
  idle, before its first device process (a gate stop: no train). **The end-stop** (above). **The hang watch** (departure D1): a host
  process alive 12 s after the watch first saw it has outlived its timeout's TERM: STOP, a `HUNG:` line in the session log, nothing else;
  never a signal, the lock left with the process's own descriptor; step 10 reads HUNG at once and the lane escalates (CARD-LANE-BRIEF.md 3).
- **"No device opened by the session."** A refusal or a holder before the session's sampler started writes `GATE-STOP: ... (no device
  opened by the session)` (step 7's config read was sent: the words say the session's own): every rest rule of ours skips such a session,
  so a new try does not wait 40 minutes for five READs. A gate stop with the sampler started counts.
- **What names the card** (E197.md 6's list, for sitting 2's condition): a stop by the stopwatch (board, die, a quiet sampler), by the
  runner (a die reading, stale or missing telemetry, a device process ended by its timeout or a signal, two failed in a row, the smoke
  gate), or by the watch with `"card": true` (its board, die and clock stops, the smoke check, a hung host); not a stop by hand, a signal
  to the wrapper or to run_session.sh, the watch gone, the end-stop, a holder or the lock between blocks, or the deadline.
- **Sitting 2's condition** (E197.md 6) is read from sitting 1's own summary line on the box: `SITTING-RESULT: smoke passed; train
  blocks complete <k >= 1> ...; card stop none`, and no sitting-1 log with a crash; step 7 refuses (10) before any card command, and step 9
  again. Anything else needs a dated amendment.
- **No second try of a sitting on the day its smoke failed** (the runner's gate or the kit's check): the kit's conservative reading of
  E197.md 11 ("no train block that sitting"), E193.md 11's rule; a later day's try needs no amendment (no train datum exists). After a
  gate stop before the smoke (a holder, the lock, a refusal): the sitting is tried again once the gate clears, in a new RB_OUT.
- **A crash** (run_session.sh ending with an exit that is no registered stop, or a stop exit with no STOP written): "the trains ended
  without a registered stop", exit 9; step 10 reads CRASHED; the lane kills nothing, collects, commits the records and stops the day; a
  dated note decides whether its trains are reduced; no sitting 2 before that note (steps 7 and 9 refuse).
- **The data directories**: one a sitting in which a block began, `docs/reports/data/<day>-e197-regfile-sitting-<n>-aifoundry3/`
  (session/, ref/, run/, the telemetry as `run/telemetry.jsonl.gz`, gzip with no name and mtime 0); a sitting that ended before any block:
  its gate stop's record `docs/reports/gate-stops/<day>-e197-regfile-sitting-<n>-T<T0>-aifoundry3/`, never under docs/reports/data/,
  never reduced (E193's kit's form). **The scrub**: the box's home becomes `~`; every holder line's user and our own login become
  `<login>`; ref/'s four files keep the registration's bytes (checked).
- **The checker's two readings** (E197.md 8, registered there): the I-cache row as the two medians and their ratio, no verdict word; the
  L1 data miss row as the per-launch medians by kind, F beside S, REPORTED.
- **The host-output parser: the registered runner's, unchanged; no amendment** (section 8).

## 5. THE REAL-PATH DESK TEST and the audit of every dry branch (the lessons of sections 104, 109 and 116)

[`desk/desktest_realpath_e197.sh`](desk/desktest_realpath_e197.sh) and [`desk/realpath_e197.py`](desk/realpath_e197.py) run **the
sitting's real path, DRY unset**, exactly as step 9 launches it, with the stand-ins of [`fake_card_e197.py`](fake_card_e197.py) (the
sampler behind the box's own copy of E128's guard, et-who, ps, the host printing REGFILE lines in main.cpp's printf form with the kind's
fields from the registration's table byte for byte, honouring the stop file, the budget and the node count), each case in a bubblewrap of
its own (a private /dev with /dev/et0_ops and /dev/et0_mgmt as regular files, a private /run/lock with the card's lock file, a private
PID namespace: the hang watch reads /proc), inside the no-device sandbox. Its cases are listed in its own header and its log; among them
**sitting 1 whole (full and short) and sitting 2 whole at a fast stand-in pace, their 429, 331 and 277 host processes in the registered
order call for call**, then the registered reducer on the real path's own files (every train's units = processes / 2) and the pooled
reduction of both sittings (T1 67 + 115 = 182 units). The stand-in host reports each launch's span as a card's 0.4 s (its lines' start and
end), so the reducer's reading window [start + 170 ms, end] holds board samples at the fast pace.

**The audit** ([`desk/dry-branches-e197.tsv`](desk/dry-branches-e197.tsv)): every line of `session_e197.sh` that branches on its dry mode
(6), of `run_session.sh` that branches on DRY (4) and the real-path regions its DRY block skips (17), and of `lab/run_trains.py` that
branches on `a.dry` (4): what the dry path does there, what the real path does, and the cases that run it. The test reads the files' own
lines and fails if one has no row, a row's text differs, or a named case did not pass in the run. **NOT RUN, each with why** (in the
table): run_session.sh line 87 (the binary's ET_DEVICES test on a several-card host needs a character device, and the wrapper refuses
several cards first); free_before_sampler's and free_with_sampler's "et-who --check failed" (exit 2: the wrapper reads et-who the same way
just before); stopwatch's "no telemetry sample in the first 60 s" (the runner's own reading stops first, case B9); line 196's STOP at the
loop's top between the smoke and block A (a few milliseconds; block A's own first check and idle read the same file, G1); the pvt
sampler branch (line 176: not on the session's path); and the runner's mid-train cut (lab/run_trains.py lines 298-304: a train that
fits at its start is cut only when its processes run slower than 6.2 s with its 30 s of slack spent, which a host inside its 8.5 s budget
reaches only near the end of a long train; its skip of a train that cannot fit, lines 290-294, ran: C1).

## 6. Device commands

`dmcmd_audit.py` with the stock table on the sittings' file set (`preflight_e197.sh`: the wrapper, the watch, the checker, the build, the
harness, run_session.sh, stopwatch.py, the lab's runner, the host's main.cpp, regfile_args.h, the kernel's regfile.c, E128's guard):
**GO, 11 send sites, 0 disallowed, every one a READ**, no allow-list and no exception. Every send site, read: E128's guard line 18
(`ettelem config`: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES,
GET_ASIC_VOLTAGE: k6's step 7) and line 31 (`ettelem sample`: GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE,
GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES: the session's one sampler); run_session.sh line 178's `"$ETTELEM" sample`
resolves through the wrapper's own `ETTELEM=` line to the guard, a scanned program ("its own lines are what it sends"; the wrapper writes
the guard's path out on that line so the audit can follow it: written `ETTELEM=$GUARD`, the first run read NO-GO, VARIANT_UNRESOLVED). The
host opens the ops node only (`createPcieDeviceLayer(true, false)`; the runtime's loads, copies, allocations and launches); the kernel sends
nothing; `et-who --check` sends no device command. **Never sent by any file of E197:** a statistics reset, any `DM_CMD_SET_*`, a governor,
TDP, threshold or clock set, a reset or power cycle, a PMIC command, the firmware-revisions query, a KILL to any process.

## 7. What the checker reads after the reduction (`check_e197.py checks`)

E197.md 8's rows as the registered reducer reports them, in E197.md 8's words with their numbers: per train, the gates (check_bad and
ok, participants, the clock, the rate within 0.5 %: APPLIED, with the reducer's dropped counts; F/S rates within 0.05 % and at least 8
units: PASS or NOT SCORED), the reports (retired / body, the I-cache medians and their ratio, the L1d per-launch medians F beside S, the
slow harts, the rail voltage samples off 3 mV: REPORTED or FLAGGED); the anchors' drift (0.3 W); the train gain and its reading rule; the
cell reading; the stops the reducer saw. Nothing is scored against any forecast.

## 8. The host-output parser and the real bytes (the round's lesson of Sun 15 Nov 2026, section 116; reg-e197's open issue 2)

[`desk/realbytes_e197.py`](desk/realbytes_e197.py) executes **the registered runner's own parse loop** (lab/run_trains.py lines 204-212,
compiled from the file's syntax tree, never re-written) on real card bytes and stand-ins (log: REALBYTES-E197 23 of 23):
- **E191's committed split bytes** (1a4bc1e3, at its SHA256SUMS): as committed, nothing kept and no exception; its runtime line
  ("Opening device 1" and its newline) transplanted inside a REGFILE line in the E197 host's exact form, **at every one of its 715
  interior offsets: the launch dropped every time**; before the line or after its newline: kept.
- **aifoundry3's real host output**: E193's four committed device-stdout files (two sittings, the smoke and the main run, each one whole
  device process's stdout): 30 host lines, **no other byte**; E193's 2,808 and 1,350 and E192's 3,255 launch records read whole by parsers
  that raise on a split host line; aifoundry3's runtime prints its device table on **stderr** (706 tables in E192's committed stderr).
  And E192's build compared its host's `--list` output with the registration's table byte for byte on aifoundry3 and read it equal (its
  data README's build row, quoted): no runtime byte on stdout at the library's load either, so build_e197.sh's same compare of
  `--list --json` is not exposed to one.
- **stand-ins**: a runtime line between two REGFILE lines (both kept); inside one (dropped); a newline-less fragment glued before or after
  one (dropped).
- **the E197 host's print discipline** (main.cpp): one printf a line, ending in its newline, then fflush; the device opened before the
  first launch; **the longest line the format can print is 1,554 B (a typical one 716 B), under PIPE_BUF (4,096 B): one atomic write to a
  pipe, so no other writer's bytes can land inside a line.**

**The kit's reading, stated before any datum (E197.md 18.2's condition, "if a split can occur there, proposes the fix as a dated
amendment"):** E191's split arose because its ledger host printed one line in two parts around the device open; the E197 host cannot,
and aifoundry3's runtime has printed nothing on a host's stdout in any committed output. **A split cannot occur on aifoundry3 by these
readings: no amendment is proposed.** The residual, a newline-less runtime fragment glued to a line's start or end (which no aifoundry3
output shows), fails safe: in the smoke the runner's gate stops the sitting before any train (no data: the real-path test's SP1 runs a
split end to end with E191's bytes), in a train that one process gives no value (two in a row stop the sitting): never a wrong datum. The
runner keeps no copy of a dropped line's text; its stderr names the failed process.

## 9. reg-e197's open issues, answered

| reg-e197 | what | here |
|---|---|---|
| 1 | request.md section 5's sizing table ("the frozen top-down lines") published in the byte-for-byte copy | answered in the registration before the land: redaction R1 (E197.md 0) withholds every number of request.md's lines 207-237 in the committed copy and registers the received file by its sha256 (verify-e197's F1), and E197.md 17.11 and 13 withhold every figure of those lines they named from the lab's record (`fix2-e197`, verify2-e197's finding); nothing the kit runs reads those lines; before R1: not the kit's to decide: the copy is the registration's; no kit file quotes a number of it, and nothing here compares or scores against it. **Open for the orchestrator** (the model session's word before the land) |
| 2 | the runner keeps a launch only from a whole REGFILE line | section 8: tested on real bytes; no split can occur on aifoundry3 by the readings; no amendment proposed; the residual fails safe |
| 3 | with `-k 1` dropped, a host that hangs in teardown holds up its block | the hang watch (section 4): STOP, a HUNG line, step 10's HUNG (16), kill nothing, keep the lock and escalate; real-path cases HG (a host ignoring TERM 14 s: no KILL, the session ends at its next check) and HG2 (one that ends at 11.5 s: the runner's timeout stop, exit 5) |
| 4 | the host's signal handling read only on aifoundry2's link | build_e197.sh re-reads it on aifoundry3's build (SIGNAL-READ: the host's and every /opt/et library's imports of a signal or crash-handler installer), reported, never a gate (a host that ignores TERM is the hang watch's). This desk's link: the host and libetrt import none; libg3log carries one that nothing in the link calls |
| 5 | figures not found in the public tree (quoted only) | unchanged: the kit cites none of them |

## 10. What the desk cannot show (for the verifier and the readiness critic)

1. **The host on the card**: the desk ran the real host only to its table and its refusals; its launches, its REGFILE lines, its
   teardown and the runtime's prints meet the card first in the smoke.
2. **The box's build**: step 6 there, against aifoundry3's own /opt/et; its ELF may differ from the desk's (reported); its runtime library
   is aifoundry3's own build (the signal read reports it).
3. **The box's sampler and holder check**: the real `build/ettelem/ettelem` behind the guard and `et-who` meet the session first on the
   day (step 7 reads the config through the same guard just before).
4. **Another user's device process**: the rule is run_session.sh's and the wrapper's own `ps` line, run against a stand-in `ps`, never a
   real other user's process.
5. **The collection** ran on stand-in sessions (the real-path test's and the runbook test's), not on a card's.
6. **The deadline's margin** at the card's real pace (section 4) and **our live collector's single-open reads** meeting step 7 or the
   sampler (CARD-LANE-BRIEF.md 6, gap 4): estimates, not measured.
7. Card time waits on the owner's go (CARD-LANE-BRIEF.md 1).

## 11. Files

| file | what |
|---|---|
| `session_e197.sh` | the sitting's wrapper on the box (section 1) |
| `watch_e197.py` | the kit's watch: its live stops, the smoke check, the end-stop, the hang watch |
| `check_e197.py` | drycmp, the summary, the section 8 checker |
| `harness_e197.py`, `harness-e197.json` | every file the box runs or reads, at its sha256 (45) |
| `build_e197.sh`, `preflight_e197.sh` | the box build and its checks; dmcmd_audit on the sittings' files |
| `collect_e197.py` | COPY-BACK EXACT, the data directory or the gate stop's record, the scrub, facts, SHA256SUMS (desk) |
| `fake_card_e197.py` | the stand-ins for the desk tests (never on the box) |
| `desk/desktest_realpath_e197.sh`, `desk/realpath_e197.py`, `desk/dry-branches-e197.tsv` | the real-path desk test and its audit table |
| `desk/realbytes_e197.py`, `desk/checks_e197.py` | the real-bytes parser test; the harness, history and checker checks |
| `rb/` | the runbook's steps (s02 s03 s07 s08 s09 s10 s11 s20 s22 s24), its common file, the rest rule, the history check, the dry listing, the runbook's and the rest rule's desk tests |
| `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e197.md` | the card lane's brief; the data README's form |
| `logs/` | every check above |
| `SHA256SUMS-e197-kit` | the kit's files (step 2 aside) and its logs |

**Step 2 (`rb/s03_desk_e197.sh`) is outside `SHA256SUMS-e197-kit`** (a file cannot hold the sha256 of a list that holds its own): its own
sha256 and the list's are given in the land file's anchor lines.

## 12. Labels, and compute

Every figure quoted from E197.md (the trains, the caps, the stops, the rests, the pins) is **registered**; the proposal's figures are
**quoted from the proposal** (the model session's); the desk tests' results are **desk checks of code**, not measurements; every watt
and degree in them is a stand-in's arbitrary test value. The process-time and launch figures in section 4 are E193's committed records
on this card (**measured**, there), used here as a desk estimate of the margin. Nothing here is blind, held out or post hoc; no E197
datum exists. Compute: on aifoundry2 through the round's CPU slot at nice 10, the desk build and the runbook test's real build with -j4
under a 4 GB cap, every run of a built host, the session, the runner or a stand-in inside the no-device sandbox; the real-path test's
cases four at a time in their own sandboxes; no simulator, no other box, no card.

SPDX-License-Identifier: Apache-2.0
