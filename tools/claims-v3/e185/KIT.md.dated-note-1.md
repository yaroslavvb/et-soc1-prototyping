# E185's kit, dated note 1 (Sat 7 Nov 2026, before any E185 datum): a later try can be collected (the collector v2 copies the two pass directories by name), a used data directory is refused, step 10 v2's rest rule reads E183's log, step 2 v2 checks the new lists, and the stale header lines are corrected; no box file, rule, plan, cap or stop changes

*Beside [KIT.md](KIT.md) (`460c352f`, 21:17:55 PST); it edits nothing there. Written on the Intel, desk only (no card, no device command,
no ssh to a lab box, no post in the lab's channel, no Modal), by the lane fix-e185 of Q155, from about 22:28 PST Sat 7 Nov 2026 until its
commit. It answers the kit's half of the adversarial verifier of A10, E185's registration and this kit (about 21:22-22:01 PST): its major
fault 1, its minor fault 6, and its nits (a), (b) and (e). The registration's half is E185.md's dated amendment A1
([`E185.md.dated-note-A1.md`](E185.md.dated-note-A1.md), `df4e6763`, 22:27:33 PST), committed before this note. **No E185 datum exists**
(`git log --all` on `docs/reports/data/*e185*`: nothing). **No box file changes:** `frozen-e185.sha256`'s 30 entries, the runner, the
session, the block, the smoke gate, the stops and the device commands are the kit's as committed, so the kit's audit (GO, 38 send sites)
stands as logged.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **the runbook's desk test v2**, stand-in ssh, rsync and pgrep serving a stand-in box | **SELFTEST-RB-E185-V2 PASS, 13 of 13** (A2, K, R4, R5, R1-R3, L1, L2, L3, C2-C4, E2, G1, S1, Z) | [`rb/logs/selftest-rb-v2.txt`](rb/logs/selftest-rb-v2.txt) |
| **the dry listing v2** | 14 scripted steps, every one exits 0, no ssh or rsync call, the look listed before the day's post | [`rb/logs/dry-listing-v2.txt`](rb/logs/dry-listing-v2.txt) |
| **device commands**, the runbook as it now runs (v1's step files with step 2, 10 and 14 v2 and the collector v2 in their place) | **GO, 11 send sites** with E128's guard, every one a READ; bare, NO-GO at exactly step 9's guard call | [`rb/logs/dmcmd-audit-v2.txt`](rb/logs/dmcmd-audit-v2.txt), [`rb/logs/dmcmd-audit-bare-v2.txt`](rb/logs/dmcmd-audit-bare-v2.txt) |

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sat 7 Nov 2026 at about 22:20 PST: public rows H24, H25
   and H28 (opaque pointers), as KIT.md read them.
2. **Used.**
   - **E185's kit** (`460c352f`): `collect_e185.sh`, `rb/s03_desk_e185.sh`, `rb/s11_a3_launch_e185.sh`, `rb/s22_collect_e185.sh` and
     `rb/list_steps_e185.sh`, each ported to its v2 here; `rb/selftest_rb_e185.sh`'s form; `rb/selftest_data_e185.py`, unchanged, as the
     stand-in box; `session_e185.sh`'s manifest (the two pass directories it covers) and `block_e185.sh`'s attempt rule (a pass directory
     moved aside as `p<pass>.attempt-<epoch>`), unchanged.
   - **E183's kit** (`cc597bf2`): its session's log, `build/e183/session-t<T0>.log`, and its last line, `session end (T0 <epoch>)`. **E184's
     kit note 2** (`571511d0`): `session_e184s_v2.sh`'s log, `build/e184/session-<arm>-t<T0>.log`, the same end line.
   - **E185's dated amendment A1** (`df4e6763`): its hash list, which step 2 v2 and step 14 v2 read.
   - **E181's committed passes** (`d4e5119d`), the stand-in box's smoke and measured pass, as in KIT.md.
   - *The same quantity, earlier:* on the kit's own stand-in box with no later try, v1's collector reads COPY-BACK EXACT 37 files (KIT.md's
     case C1). v2 reads the same 37 there (the desk test's C cases and S1), and the same 37 on the later try's box (L1, E2).
3. **Not used.** Any change to a box file; aifoundry1 or aifoundry2; anything of the NDA tier.
4. **Tiers.** Public tier only. No NDA-tier check is used, so there is no sha256 line.

## The runbook as it now runs (KIT.md's table, with this note's three steps)

| step | file | from this note |
|---|---|---|
| 1, the window | `rb/s02_window_e185.sh <day> <last start> <last end>` | unchanged |
| 2, the desk check | **`rb/s03_desk_e185_v2.sh`** | v1's checks, with HEAD descending from A1 (`df4e6763`) and the lists `SHA256SUMS-e185-a1` (5) and `SHA256SUMS-e185-kit-note1` read in full |
| 3, the look, FIRST | `rb/s05_look_e185.sh aifoundry3 [--wait]` | unchanged |
| 4, the day's post | (the card lane's, not scripted) | after the look |
| 5-7, sync, preflight, reads | `rb/s07_a3_sync_e185.sh`, `rb/s08_a3_preflight_e185.sh`, `rb/s09_a3_reads_e185.sh` | unchanged |
| 8, the dry pass | `rb/s10_a3_dry_e185.sh start`, then `wait` | unchanged |
| 9, the host's start window | `rb/s12_a3_host_e185.sh start` | unchanged |
| 10, the launch | **`rb/s11_a3_launch_e185_v2.sh [--later-try] [--under-an-hour] [--after-noon]`** | the rest rule also reads `build/e18x/session-*.log` (E183's and E184's) and both end forms |
| 11, the wait | `rb/s20_wait_e185.sh` | unchanged |
| 12, the host's end window | `rb/s12_a3_host_e185.sh end` | unchanged |
| 13, the release | (not scripted) | |
| 14, the collection | **`rb/s22_collect_e185_v2.sh`** | the collector v2; the lists A1's and this note's too; the "left on the box" line logged; a used data directory refused |

**v1's step 2, step 10 and step 14 (`s03_desk_e185.sh`, `s11_a3_launch_e185.sh`, `s22_collect_e185.sh`) are never run on E185's card day.**
Each v2 step sources the kit's `rb_common_e185.sh` unchanged, with the same exit codes (KIT.md).

## Fault by fault

### Major 1: a later try could never be collected

- **What v1 did.** After A6-1-STOPPED or G0-REFUSED (step 11's 16), step 10's `--later-try` moves the first smoke aside as
  `e185-smoke/p18501.try1`, and `block_e185.sh` moves a measured pass that did not end ok to `e185/p18520.attempt-<epoch>`. v1's collector
  copied all of `e185-smoke/` (it left out only `*.attempt-*`), so the exact copy-back read COPY-BACK EXTRA on `p18501.try1`. Step 14 then
  stopped with 16 on every collection, because the directory stays on the box. That came after up to about 103 more card-minutes.
- **What v2 does** ([`collect_e185_v2.sh`](collect_e185_v2.sh)):
  - It copies **the two pass directories by name**, `e185-smoke/p18501/` and `e185/p18520/`, which are the two that `session_e185.sh`'s
    manifest covers. Nothing else of `e185-smoke/` or `e185/` is copied.
  - One bounded read (60 s, `bash -s` on the box) says whether each pass directory is there, and names every other entry beside them. The
    collector prints them as `left on the box (not this session's manifest; an earlier try's, not copied): ...`, and step 14 v2 writes that
    line into the runbook's log for the records.
  - An earlier try's files stay on the box, read-only. They are not E185 data. A records round that wants them copies them by a read-only
    rsync of its own.
  - A failed presence read names both pass directories as not copied (`rsync ... rc=<n>`), and the collector stops.
- **Desk cases.**
  - L1, the later try's box (`p18501.try1` and `p18520.attempt-1793990000` beside this session's): v1 reads EXTRA (4); v2 reads COPY-BACK EXACT
    37 files, names both entries and copies neither.
  - E2: step 14 v2 runs end to end on that box. The copy-back is exact, A10's reading and E185's rules read SCORED (on the stand-in's five
    holds), and the line is in the runbook's log.
  - L3: the presence read fails (the stand-in ssh exits 255): both directories are named, and the collector stops (4).
- **One more case, named for the records.** A first try can be refused at G0 (its measured pass `p18520` kept, status "gate"), and a later
  try can then stop at A6-1 before its own measured pass. In that case `block_e185.sh` never moves the first `p18520` aside, so the later
  session's manifest, and the collection, carry the first try's measured pass. Step 14 stops at that pass's refusal (G0-REFUSED, 16) or at
  the later smoke's A6-1 (F0-STOPPED, 16), and nothing is scored. The records then name that pass by its own `block.json` and marks, whose
  times precede the later T0. A third try is refused (step 10).

### Nit (b): a used data directory

- **What v1 did.** A second collection into a directory a first one had filled read COPY-BACK EXTRA on `logs/host-start.out` and
  `logs/host-end.out`, the collector's own copies made after its check. Step 14's message after a failed score said "the collection stands"
  and did not say to remove the directory first.
- **What v2 does.** The collector v2 refuses a data directory that holds any file before any box call (`refusing: ...`, 3), and step 14 v2
  stops on it with 16. After a failed score, step 14 v2's message reads "... To collect again, remove `<the data directory>` first:
  collect_e185_v2.sh refuses a data directory that holds any file". Its two check-of-C messages say "remove `<the data directory>`" where v1
  said "remove what the collector wrote".
- **Desk cases:** L2, a second collection into L1's directory: refused (3), no ssh or rsync call. G1, step 14 v2 into E2's directory: 16, no
  rsync call. S1, a stand-in scorer that exits 1: 14, the removal named, no scored file.

### Minor 6: step 10's rest rule could not see E183

- **What v1 did.** Its rest rule read `build/e17x/session.log`, `build/e18[0-4]/session.log`, E184's `build/e184/session-*.log` and E185's
  `build/e185/T*/session.log`. E183's kit (`cc597bf2`) writes `build/e183/session-t<T0>.log`, so a session of E183 earlier the same day was
  invisible to E185's registered 40-minute rest gate. E183's and E184 v2's sessions also end `session end (T0 <epoch>)`, which v1 counted as
  a block without its end: at its last line, the same time, with a "note:".
- **What v2 does** ([`rb/s11_a3_launch_e185_v2.sh`](rb/s11_a3_launch_e185_v2.sh)). It reads every `build/e18x/session-*.log` too, with the
  dry ones skipped by name (`*-dry*`) as before, and it reads both end forms as the session's end. Everything else is v1's line for line;
  its refusal of an earlier smoke names v2.
- **Desk cases.**
  - R4: E183's log, its session ended 30 minutes ago. v1 launches (the fault, shown); v2 refuses (10).
  - R5: E184 v2's log, ended 3 h ago. v2 counts its rest from that line as a session end, about 180 minutes and no note; v1 prints the note.
- **The order.** E185.md § 8 still asks that E185 go first on a day it shares with another session of ours on aifoundry3, in the cool
  morning hour, with the other starting only after E185's collection has copied its files back. With v2 the rest gate holds in either
  order. E183's own launch step has no rest rule of its own (`cc597bf2`'s `rb/s11_a3_session_e183.sh`: k6's guard only), so E185 first is
  also the order that keeps E185's card rested.

### Found by this fix pass: v1's desk test did not reach the rest rule in R1 and R2

v1's committed desk test ran its rest cases R1 and R2 without `--after-noon`, and its committed log was made after 12:00 PST (about 21:14).
So step 10's noon gate refused both (10) before the rest rule ran. Their printouts carry no REFUSED line. The cases passed, but they did not
test the rest rule. Run here with `--after-noon` (case R1-R3), v1's own rest rule refuses both on the rest rule's words, as v2's does, and
launches R3. So **v1's rest rule was right for those cases; only its test was blind.**

v1's test also writes its stand-in window for today with a last end of 23:59, so its launch cases fail on the 105-minute gate when it is
run after about 22:14 PST. v2's test writes tomorrow's window, so it runs at any hour. No code of the kit changes for this.

### Nit (a): stale or false provenance in v1's runbook headers (corrected here; the files stay as committed)

| file (460c352f) | its header says | it should say |
|---|---|---|
| `rb/s11_a3_launch_e185.sh` | "It is s11_a3_launch_e185.sh (33cdccf6, which stays as committed) with ONE change, the rest rule (the E185 kit verifier's fault 7, Fri 6 Nov 2026; the kit's README.md.dated-note-1.md)" | E181's step 11 v2 (`s11_a3_launch_e181_v2.sh`, `dc35a540`; its rest rule was the E181 kit verifier's fault 7, E181's `README.md.dated-note-1.md`), ported to E185 |
| `rb/s12_a3_host_e185.sh` | "new; the E185 kit verifier's fault 3, Fri 6 Nov 2026; the kit's README.md.dated-note-1.md", and "where M11's scorer v4 reports" | E181's step 12 (the E181 kit verifier's fault 3, E181's note 1), ported; M11's scorer v5 reports the host windows |
| `rb/s22_collect_e185.sh` | "It is s22_collect_e185.sh (33cdccf6, ...) with the E185 kit verifier's faults 2, 4 and 5 fixed ... README.md.dated-note-1.md"; the lists "SHA256SUMS-score-m11-v4, -a9 and -score-m11-v3, E185's kit-e185.sha256, ... SHA256SUMS-note1"; "the rest set aside in logs/not-this-session/"; "the score v2 ... M11's scorer v4"; and the runbook log's label "M11's scorer v4" | E181's step 22 v2 (`dc35a540`), ported; the code checks `SHA256SUMS-score-m11-v5`, `-score-m11-v4`, `-a10`, `SHA256SUMS-e185-registration`, `-e185-kit` and `rb/SHA256SUMS-rb-e185`; E185's collector copies the T0 directory; the scorer is v5 (step 14 v2's header and label say so) |
| `rb/scrub_all_e185.py` | "the E185 kit verifier's fault 5, Fri 6 Nov 2026; the kit's README.md.dated-note-1.md" | E181's (the E181 kit verifier's fault 5, E181's note 1), ported |
| `rb/rb_common_e185.sh` | "RB_BASE defaults to M11's amendment A8 (80b92990)"; "ours_live names ... E178's and E180's (the next sessions planned on this card)" | the code's default is `98fe28b7` (E185's registration); ours_live's pattern names E182's, E183's, E184's and E185's sessions, blocks and runners (KIT.md's case O) |
| `rb/s02_window_e185.sh` | "REGISTRATION.md section 5's cap" | E185.md § 8's cap (105 card-minutes) |
| `rb/list_steps_e185.sh` | "as the kit's dated note 1 (README.md.dated-note-1.md) orders it ... (33cdccf6 ...) with the note's steps" | E181's listing (`dc35a540`), ported; it lists KIT.md's steps (v2's listing lists this note's) |

### Nit (e) and the card-minutes

- **Its own RB_OUT.** KIT.md says "this card day's RB_OUT", but every runbook writes `$RB_OUT/window.env`, so on a day E185 shares, E185's
  runbook gets **its own RB_OUT** (E182's card-lane rule: one RB_OUT per runbook), with the day's one RB_LOCK.
- **About 103 card-minutes, not "about 102"** (A1-8 (d)): `run_e185.py`'s 101.0-minute measured pass, the smoke with its stop tests (about
  1.4 minutes), and the session's own reads. The cap of 105, the pass's deadline at T0 + 104 minutes, step 10's 6,300 s gate and the post's
  "for 2.5 h" are unchanged.

## What the card day reads from this note

- The runbook table above, with step 2, 10 and 14 as v2. The day's brief names this note.
- E185's own RB_OUT, and E185 first on a shared day (E185.md § 8).
- After a later try, step 14 v2's "left on the box" line names the earlier try's directories. They stay on the box.
- The records quote E185.md with A1's labels, and E185-C's consequence from its F line (A1-2).

## What does not change

KIT.md, its files and lists, the box list (`frozen-e185.sha256`), the session, runner, block, smoke gate, stops, device commands and
budget stay as committed. So do E185.md and A1, M11's scorer v5, and E181's data. The v2 files are new; v1's stay as committed and are not
run on the card day.

## Files ([`SHA256SUMS-e185-kit-note1`](SHA256SUMS-e185-kit-note1))

This note; [`collect_e185_v2.sh`](collect_e185_v2.sh); [`rb/s03_desk_e185_v2.sh`](rb/s03_desk_e185_v2.sh),
[`rb/s11_a3_launch_e185_v2.sh`](rb/s11_a3_launch_e185_v2.sh), [`rb/s22_collect_e185_v2.sh`](rb/s22_collect_e185_v2.sh),
[`rb/list_steps_e185_v2.sh`](rb/list_steps_e185_v2.sh) and [`rb/selftest_rb_e185_v2.sh`](rb/selftest_rb_e185_v2.sh); the logs
`rb/logs/selftest-rb-v2.txt`, `dry-listing-v2.txt`, `dmcmd-audit-v2.txt` and `dmcmd-audit-bare-v2.txt`. The list also pins the unchanged
files the v2 steps source, call or copy: `rb/rb_common_e185.sh`, the other step files, `score_e185.sh`, `rb/cclaunch_e185.py`,
`rb/scrub_all_e185.py`, `rb/selftest_data_e185.py`, `session_e185.sh` and `block_e185.sh`.

    bash tools/claims-v3/e185/rb/selftest_rb_e185_v2.sh <a scratch directory outside the repo> > selftest-rb-v2.txt
    bash tools/claims-v3/e185/rb/list_steps_e185_v2.sh <an empty scratch directory> > dry-listing-v2.txt

## Compute

The Intel, through the round's local slot, one job at a time: development runs of the desk test into the lane's scratch (22:34 and
22:36 PST; the first failed its launch cases on the 105-minute gate with today's window, which is why v2's test writes tomorrow's), then the
committed runs of the desk test (129 s), the dry listing and the audits, 22:41:54-22:44:07 PST. Both audits' bodies are byte for byte v1's
(`rb/logs/dmcmd-audit.txt`, `dmcmd-audit-bare.txt`): the v2 files send no command v1's did not. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
