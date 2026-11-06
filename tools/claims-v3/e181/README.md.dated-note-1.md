# E181, dated note 1 (Fri 6 Nov 2026, before any E181 datum): the kit verifier's faults fixed by new files; the runbook now runs s03 v2, s12, s11 v2 and s22 v2

*Beside [`README.md`](README.md) (`33cdccf6`), which stays as committed, as does every file of the kit. Written on the Intel, desk only (no card,
no lab box, no device command, no post), by the lane fix-e181 of E181's kit round, about 03:05-03:50 PST. **E181 is kitted, not run: no E181
datum exists.** The kit's verifier (verify-e181, about 02:30-02:54 PST) read the kit "holds with fixes": one major fault, at the registration's
level (A8-6), and eight minor ones. Each is answered below, by new files only, with M11's amendment A9 (`cd5bed77`) for the one that touches a
rule. **Nothing on the box changes:** the box list (`frozen-e181.sha256`, 30 entries), the runner, the block, the session, the smoke gate, the
preflight, every gate, stop and rest line, and the card-minutes (about 75, cap 76) are the kit's as committed and verified. So E178's runbook,
which counts `session_e181.sh` as ours, still sees E181's session.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 03:10 PST: public rows H14, H19, H25
   and H28 (opaque pointers).
2. **Used.**
   - **E181's kit** (`33cdccf6`) and its runbook `rb/`, unchanged; M11's **A9** (`cd5bed77`) and **scorer v4** (`../m11/score_m11_v4.py`,
     this note's commit).
   - **E176's lane's host windows** (`docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/room-rule/hostwin-*.out`, `5db7bcf7`): the form
     of step 12's reads (the sensors, 13 samples 10 s apart, each sensor's mean, min, max and count).
   - **E164's login scrub** (`tools/claims-v3/e164/scrub_etwho_e164.py`, pinned by `rb/rb_common_e181.sh`), unchanged, and the way E176's
     records ran it, in every directory with each `.gz` unpacked beside it (E176's data README, "Privacy").
   - **v3.1's runner and gates** (`rb_run.py`, `nopath_q142s.py`, `ccdone_q142s.py`) and `cclaunch_e181.py`, unchanged.
   - *The same quantities, earlier:* the runbook's device commands (v1's `rb/logs/dmcmd-audit.txt`, GO 11) against v2's (GO 11, the same sites);
     DRY-INTEL's committed log against its re-run (the same lines but times and the tree's file count).
3. **Not used.** A change to any box file (the runner's pattern edge, fault 8, and a dry name for step 10's smoke gate, fault 2): each would
   change the box list, its checks and the session script E178's runbook counts, all verified as they stand; the desk-side fixes below cover
   both. Anything of the NDA tier.
4. **Tiers.** Public tier only. No NDA-tier check is used, so there is no sha256 line.

## The faults and their fixes

| # | the verifier's fault | the fix (new files) | shown by |
|---|---|---|---|
| 1 | **major:** M11's readings run the chain on the measured pass alone, so the smoke's heat at H_E's anchor is unseen (A8-6, est. −0.30 °C on H_E's e) | **M11's A9** (`cd5bed77`) registers a REPORTED arm: the chain over the smoke and the measured pass together, anchors unchanged; **M11's scorer v4** reads it beside the registered reading, which still decides. Post hoc (A9-5), the part is about half of A8-6's estimate: the first hold moves +0.131 °C (E154) and +0.117 °C (E166) after a 5-minute R0, +0.021 °C after E144's 8; E176's planned smoke +0.147 °C at R0's anchor, so E181's H_E is expected near +0.15 °C on the arm. A record quotes HM-E144, HM-HE and HM-CAL with the arm beside them | v4's self-test A1-A4; the desk test's E1 |
| 2 | after an A6-1 stop or a failed smoke, step 22 stopped 14 on `rsync e181 rc=23` and never read the gates; and the dry session's `smoke-gate.json` was collected as the real one | **`collect_e181_v2.sh`:** a pass directory copied only when a bounded read finds it on the box ("absent on the box" otherwise); each file the session writes into `build/e181/` kept only if the session's own last block records it, else set aside in `logs/not-this-session/` with a README. **`rb/s22_collect_e181_v2.sh`:** after the marks' gates (F0-STOPPED, G0-REFUSED), the session log's own stops, 16 each: SMOKE-STOPPED, STOP-FILE, NO-DEVICE, NO-SESSION-LOG | E3 (and E3v1: v1 stops 14, the fault), C21-C24 |
| 3 | A6-5's host readings (the NVMe composite and coretemp at the session's start and end) are in no file of the kit | **`rb/s12_a3_host_e181.sh`, `start` and `end`:** E176's lane's host window (sysfs only, 13 samples 10 s apart; refused while a session of ours runs) into `build/e181/host-start.out` and `host-end.out`, which the logs' rsync collects; **v4** reports them under A6-5, never a gate | H1-H3; v4's H1; E1 |
| 4 | M11's scorer v3 writes the lines file before its own check of the `start_gate` marks, so a refused score leaves `scored-m11-lines.jsonl`; and the kit README's "C2-C20 and E2 each show no scored file after a stop" overstates | **v4** reads every mark before anything is written and stages the lines file, renaming it only after the whole score succeeds (`../m11/README-score-m11-v4.md`); **`score_e181_v2.sh`** runs v4; step 22 v2 names any scored file a failed score left. The README's claim, corrected: v1's desk test left scored files in C4 and C6 by design (its stand-in scorer writes them first) and did not check C7, C11 or C16; v2 checks C7 and C16, C1, C4, C6 and C11 keep the stand-in's files by design, and E6 shows the real scorer v4 leaves none | v4's W1-W3; E6 (and E6v1: v3 leaves the lines file, the fault) |
| 5 | step 22's login scrub `--check` read `$D/logs` only, one directory level | **`rb/scrub_all_e181.py`:** E164's scrub `--check`, unchanged, in every directory of the data directory, each `.gz` unpacked into a fresh directory outside the repo and checked there; step 22 v2 stops 16 on any login left | E5 (and E5v1: v1 scores, the fault) |
| 6 | the committed runbook audit (`rb/logs/dmcmd-audit.txt`) was made on `s11_a3_session_e181.sh` before its rename (its result holds on the committed files) | **new audit logs with their command lines in the header:** `rb/logs/dmcmd-audit-v2.txt` (every step file the runbook now calls, the collector v2, the score step v2, the scrub helper, scorer v4 and A9's arm, with E128's guard): **GO, 11 send sites**, the same sites as v1's log; `rb/logs/dmcmd-audit-bare-v2.txt`: NO-GO at exactly step 9's guard call, as v1's; the kit's `dmcmd-audit-note1.txt`: **GO, 38 sites**, identical to `dmcmd-audit.txt` but its header | the logs |
| 7 | the rest rule counts only "session end" lines, so a real session killed before its last line is invisible to it | **`rb/s11_a3_launch_e181_v2.sh`:** a real block without its end counts as ended at its last timestamped line (the log's final block: or the log's last write, the later); a block that ended at a session gate ("no device opened") is skipped; dry blocks are skipped as before; everything else is v1's | S7 (and v1 on the same log: it launches, the fault), S8; S1-S6 on v2 |
| 8 | at a room in (53.9, 53.9 + 10⁻⁹] °C the start gate passes through its tolerance while A6-3's pattern test (none) leaves H_E with no pattern | **not changed in the runner** (see Not used); **v4 flags it** (`A6_3_pattern_edge`) so a record names it. The room is a mean over at least 600 samples of 34-sensor means of codes 0.0609 °C apart, so its values sit on a lattice 0.0609 / (34 N) °C apart (1.5 × 10⁻⁶ °C at ten samples a second over R0's last 120 s); a room inside that 10⁻⁹ °C interval needs the room within one lattice step of 53.9 °C and on the one point floating point lifts past it, about 10⁻⁶ of sessions or fewer. If it happened, H_E would run as a rest and Z-L2 would run, every stop unchanged | v4's E1 |
| 9 | `../m11/README-score-m11-v3.md` opens with no Builds on block | **`../m11/README-score-m11-v3.md.dated-note-1.md`** gives v3's block; v4's README opens with its own | the files |

## The runbook from this note

Each step with this card day's `RB_OUT` outside the repo and `RB_LOCK`; the exit codes are v3.1's. **For E181, never s03, s11 or s22 v1 (and so
never `collect_e181.sh` or `score_e181.sh`).**

| step | file | what changed |
|---|---|---|
| 2 | `rb/s02_window_e181.sh <day> <last start> <last end>` | unchanged |
| 3 | **`rb/s03_desk_e181_v2.sh`** | v2: HEAD descends from A9 (`cd5bed77`) as well as A8; M11's fifteen lists (v1's thirteen, `-a9` 4 and `-score-m11-v4` 5) and the footing law's two; the kit's, the runbook's and **this note's** lists; the box list's 27 repo entries |
| 5 | `rb/s05_look_e181.sh aifoundry3 [--wait]` | unchanged (it records the box login the scrub of step 22 v2 needs) |
| 6 | (not scripted) | the day's one post, unchanged |
| 7-9 | `rb/s07_a3_sync_e181.sh`, `rb/s08_a3_preflight_e181.sh`, `rb/s09_a3_reads_e181.sh` | unchanged (step 7 syncs the kit directory with this note's files; the box list is unchanged) |
| 10 | `rb/s10_a3_dry_e181.sh start` then `wait` | unchanged |
| 12 start | **`rb/s12_a3_host_e181.sh start`** | new: A6-5's start window, right before the launch (about 2.5 minutes; no card time) |
| 11 | **`rb/s11_a3_launch_e181_v2.sh [--later-try] [--under-an-hour] [--after-noon]`** | v2: the rest rule (fault 7) |
| 20 | `rb/s20_wait_e181.sh` | unchanged |
| 12 end | **`rb/s12_a3_host_e181.sh end`** | new: A6-5's end window, after step 20 reads the session's end (0, or 16 at a gate) |
| 21 | (not scripted) | the release, unchanged |
| 22 | **`rb/s22_collect_e181_v2.sh`** | v2: the collector v2, the session log's stops, the scrub in every directory, the score v2 (M11's scorer v4: A9's arm, A6-5, the pattern edge) |

- **The verifier's operator note is superseded:** after step 20's A6-1-STOPPED, step 22 v2 reads 16 F0-STOPPED (not 14).
- **Wall time:** about 5 minutes more (the two host windows). **Card-minutes:** unchanged, about 75 (cap 76). Step 11's last start counts from
  the launch, so step 12's start window comes before it: allow its 2.5 minutes inside the window.

## Tests after the fix (the Intel, one job at a time through the round's local slot)

| check | result | file |
|---|---|---|
| **the runbook's desk test v2** (stand-in ssh and rsync; 58 cases, among them every v1 case on the v2 steps and each fault shown on v1) | **62 of 62 checks PASS** (197 s, 03:49:27-03:52:45 PST) | [`rb/logs/selftest-v2.txt`](rb/logs/selftest-v2.txt) |
| **the dry listing v2** | 14 step calls, each exit 0, no ssh or rsync call | [`rb/logs/dry-listing-v2.txt`](rb/logs/dry-listing-v2.txt) |
| **M11's scorer v4 self-test** | **12 of 12 PASS** (75 s) | `../m11/selftest-score-m11-v4.txt` |
| M11's scorer v3 self-test, re-run | 12 of 12 PASS, its json and txt byte for byte | `../m11/selftest-score-m11-v3.txt` (unchanged) |
| **DRY-INTEL**, re-run in a tree built from step 7's sync list alone | **7 of 7 PASS** (03:52:45-03:53:34 PST); the committed log's lines but times and the tree's file count (74 files with this note's) | [`logs/dry-intel-note1.txt`](logs/dry-intel-note1.txt) |
| **device commands**, the kit (`preflight_e181.sh`) | **GO, 38 send sites**, identical to `dmcmd-audit.txt` but its header | [`dmcmd-audit-note1.txt`](dmcmd-audit-note1.txt) |
| **device commands**, the runbook v2 | **GO, 11 send sites** with E128's guard (v1's sites); bare, NO-GO at exactly step 9's guard call | [`rb/logs/dmcmd-audit-v2.txt`](rb/logs/dmcmd-audit-v2.txt), [`rb/logs/dmcmd-audit-bare-v2.txt`](rb/logs/dmcmd-audit-bare-v2.txt) |

**Every device command is still a READ**: the two PMIC voltage-register reads the owner allowed (Mon 2 Nov 2026). Step 12 reads sysfs files
only and opens no device. There is no statistics reset, no firmware-revisions query and no set of any kind; no power cycle, and nothing that
risks one.

## Files (`SHA256SUMS-note1`)

This note; `collect_e181_v2.sh`, `score_e181_v2.sh`; `rb/s03_desk_e181_v2.sh`, `rb/s11_a3_launch_e181_v2.sh`, `rb/s12_a3_host_e181.sh`,
`rb/s22_collect_e181_v2.sh`, `rb/scrub_all_e181.py`, `rb/list_steps_e181_v2.sh`, `rb/selftest_rb_e181_v2.sh`; the logs `rb/logs/selftest-v2.txt`,
`rb/logs/dry-listing-v2.txt` (each with a header line naming its command, added after the run), `rb/logs/dmcmd-audit-v2.txt`,
`rb/logs/dmcmd-audit-bare-v2.txt`, `logs/dry-intel-note1.txt` and `dmcmd-audit-note1.txt`. M11's new files have their own lists:
`../m11/SHA256SUMS-a9` (A9) and `../m11/SHA256SUMS-score-m11-v4` (the scorer v4, its self-test, its README and v3's README's dated note).

## Still owed before card time (unchanged by this note)

A readiness critic's READY; his go naming the day, the last start and the last end (launch before 12:00 PST, 76 minutes for E181 before the
last end, E178 FULL after it on the same card); fresh lab approvals for aifoundry3; the day's one post.

SPDX-License-Identifier: Apache-2.0
