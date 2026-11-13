# E190's card-lane brief, dated note 1, before any datum: the v2 steps in place of the kit's, THE QUIET HOLD with several owners, the bookings, a quiet desk on aifoundry2 for arm A's window, the identity lines to read, the README's additions (Q169, lane fix-e190; new files only)

*Fri 13 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q169, lane `fix-e190`). It sits beside [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md)
(the kit, `241726bd`), which stays as committed; where this note and the brief differ, this note is the brief for the card day. It
answers E190's verifier's findings 3 and 5 (minor) and carries the kit note's v2 steps
([KIT.md.dated-note-1.md](KIT.md.dated-note-1.md)) and the registration note's README lines ([E190.md.dated-note-1.md](E190.md.dated-note-1.md)).
No E190 datum exists. Nothing here changes a forecast, band, rule, threshold, order, card time, cap, stop or the scorer.*

## 1. The steps (paths under `tools/claims-v3/e190/`): the kit's table, with note 1's v2 steps where note 1 replaces one

| # | the step | what to do with its exit |
|---|---|---|
| 0 | by hand: `uptime`; the anchor lines (OUT/fix-e190/ANCHOR-LINES.md: the registration, the kit and **note 1's commit** ancestors of HEAD; the registration's list 16, the kit's 56 and **note 1's list** at their counts and bytes, every entry OK; **step 2 v2** at its sha256; no E190 datum in any ref); **section 2's hold** and **section 3's bookings**; **section 4's quiet desk** | any line not as stated: no box step that day |
| 1 | `rb/s02_window_e190.sh <day> <last start> <last end>` (the kit's) | first; today's day only |
| 2 | **`rb/s03_desk_e190_v2.sh`** with `RB_GITLOCK` set, never inside the lab-git lock | anything but 0: no box step that day (one exception: a pull whose upstream did not answer) |
| 4 | per arm, k6's look (`../q141k-runbook/k6/s05_look_k6.sh aifoundry2` / `aifoundry1`) | FREE; a holder: bounded polls, at most 30 minutes |
| 3 | **no post** (waived: the owner's words of Fri 13 Nov 2026, about 11:30 PST) | |
| 5 | **`rb/s07_sync_e190_v2.sh A [pull]`** (aifoundry2's tree must hold note 1's commit: 17 until it does) and **`rb/s07_sync_e190_v2.sh B`** | 0: HARNESS OK (v2) on the box |
| 6 | per arm **`rb/s08_build_e190_v2.sh <A\|B> start`**, then `wait` while it says 17 | 0: RB_OUT/e190-built-v2-<arm>.txt; on arm B the record must read "the host and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES" (else 16: **no session of arm B that day**); NO-THIRD-BUILD counts the kit's and note 1's starts together |
| 8 | per arm **`rb/s10_dry_e190_v2.sh <A\|B> start`**, then `wait` | 0 (the dry pass v2 asserts the identity read on its doubles) |
| 9 | per arm **`rb/s11_session_e190_v2.sh <A\|B>`** | 0 launched `session_e190_v2.sh`; 10 refused: read why, never around it |
| 10 | per arm **`rb/s20_wait_e190_v2.sh <A\|B>`**, again while it says 17 | 0 ended with its manifest; 16 a gate stop (the identity gate and the identity read among them): still collect it |
| 11 | per arm **`rb/s22_collect_e190_v2.sh <A\|B>`** | 0 COPY-BACK EXACT |
| 12 | `rb/s23_data_e190.sh` (the kit's), then the data commit (section 2) | 0 COLLECTED |
| 13 | after the data commit only: `rb/s24_score_e190.sh` (the kit's), then **`rb/s25_report_e190_n1.sh`** (note 1's REPORTED readings into RB_OUT/report-e190-n1.txt) | |

**Never run the kit's steps 2, 5, 6, 8, 9, 10 or 11 on the card day**: the kit's runner has no identity gate, and the kit's wait and
copy-back count `session_e190.sh`, never `session_e190_v2.sh` (E183's lesson of Fri 13 Nov: a wait that counts a v1 name reads a false
RUN-GONE beside a v2 session). `rb/list_steps_e190_v2.sh` prints every step's commands (the dry listing, 23 steps).

## 2. THE QUIET HOLD, several owners (the verifier's finding 5; replaces the kit brief's section 2)

Since Fri 13 Nov 2026 about 13:20 PST the round's hold file holds one owner a line, and the round's hold script adds and removes the
lines (`bash W/hold.sh add <lane>`, `bash W/hold.sh remove <lane>`, `bash W/hold.sh list`; W the round's state folder). For E190:
- **before step 2**: `bash W/hold.sh add <lane>` (the card lane's own name). Never create, overwrite or edit the file by hand, and never
  remove another lane's line: E183's, E189's or E191's card lane may hold at the same time on another box;
- **the data commit** (step 12): through `commit_lab.sh`, new files only, with `LAB_QUIET_HOLD_OWNER=<lane>` set to that same name
  (commit_lab.sh commits only for an owner named on one of the lines, and refuses everyone else with 76); each card lane commits only its
  own paths;
- **after the data commit**, and **on every stop path** (a gate stop, NO-THIRD-BUILD, a refusal, a login link, a lost wait, the window
  closing): `bash W/hold.sh remove <lane>`. The file goes when no owner is left;
- step 2's pull runs under the lab-git lock, inside the lane's own hold (the hold stops other lanes' writes, not the owner's pull).

## 3. The bookings

`bash W/book.sh take aifoundry2 <lane>` before arm A's look and `bash W/book.sh take aifoundry1 <lane>` before arm B's (aifoundry1's key is
the whole box: never two sessions of ours there; E191 also needs card 1); `release` each after that arm's copy-back, and on every stop
path. A booking another lane holds: that arm does not run until it is released.

## 4. A quiet desk on aifoundry2 for arm A's window (the verifier's finding 3)

On aifoundry2 the desk and arm A's box are one machine and one user ID. The runner's holder read counts every device-named process of
ours (`*_host`, `ettelem`, `sys_emu`, `dev_mngt_service`, `et-powertop`, `mmbench_launch*`) and the runbook's `ours_live` every
`session_eNNN*.sh` or `queue_eNNN*` script of ours: another lane's stand-in session, stand-in reader, `sys_emu` or built host refuses arm
A's look, build, dry pass, launch and copy-back, and **mid-session it stops the session** (the verifier saw a runbook test read 23 of 29
beside another lane's stand-ins, and 29 of 29 alone). So **from arm A's step 4 to its step 11, no lane of ours on aifoundry2 runs a
stand-in or real session, a stand-in or real reader, `sys_emu`, a built host or a runbook desk test**; the orchestrator holds those lanes
for the window (desk lanes that only edit, read or commit are not affected). Before step 9 the card lane reads, as counts, our processes
on aifoundry2 that either rule would count (`ps` of our user ID: the device-named processes, and the scripts named `session_eNNN*.sh` or
`queue_eNNN*`); not 0: wait, bounded, or no session of arm A.

## 5. The lines to read in each session's log (`build/e190/T<T0>-<arm>/session.log`, via step 10 v2)

- `config start: {...} (read, nothing set); the card's identity: PCIe target /dev/et1_mgmt, physical device ID 1, minion_mv <n> below 510`
  (arm B; arm A: `/dev/et0_mgmt`, ID 0);
- `the identity read: et-who {...} (counts by card), the sampler holds ['/dev/et1_mgmt']: card 1 only`;
- `smoke <fmt>: ... the host's card: its own (stderr ['/dev/et1_ops'] [1], held ['/dev/et1_ops']); the board <x> W over the rest on <n>
  samples (at least 2 W): ok`, for each of the three formats.

Any of them absent, or naming card 0 on arm B: the session has stopped at a gate (16) or by the identity stop (`identity_trip` in
`marks.jsonl`), and nothing further ran. Collect it (step 11 v2), report it, and never re-run around it the same day. An identity stop
that touched the stop file mid-process on arm B means a host ran on card 0 for at most a launch or two: say so in the lane's result, with
the session's `identity.json`.

## 6. What the README adds (the registration note's lines)

Results first, as the kit brief's step 12b, and also: "the owner waived the day's post: his words, Fri 13 Nov 2026 ~11:30 PST"; E135
cited as the lab's public A100 side, under its correction C1 ("a kernel against a chip"), with E190 as the GEMM-against-GEMM side, and no
figure of the owner's private A100 report; the blindness label as E190.md.dated-note-1.md section 2 reads it; S6 as the scorer reads it,
with the clock's highest and arm B's samples outside 590-610 MHz from RB_OUT/report-e190-n1.txt (REPORTED); fp16's S1 and S4 also
against the same-size reading from the same file (the verifier's reading, REPORTED); P1 fp32's first process time; each session's
identity lines (section 5).

## 7. Never (in addition to the kit brief's section 5)

- Never the kit's v1 runbook steps 2, 5, 6, 8, 9, 10 or 11 on the card day (section 1).
- Never a session of arm B without step 6 v2's passing `ET_DEVICES` reading, nor past a failed identity gate or identity read.
- Never remove, overwrite or edit another lane's hold line; never commit under another lane's name.
- Never run a stand-in or real session, reader, `sys_emu`, built host or runbook desk test of ours on aifoundry2 inside arm A's window.

SPDX-License-Identifier: Apache-2.0
