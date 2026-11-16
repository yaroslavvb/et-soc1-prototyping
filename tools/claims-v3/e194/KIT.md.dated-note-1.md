# E194's kit, dated note 1: E194's own firmware gate (rb/fwgate_e194.sh) and the three step versions that read it (step 2 v2, the look v2, the session v2), step 2 v2's never-run check leaving out E191's third-session folders, the v2 dry listing and their desk tests; written with E194.md's dated amendment A1, before any E194 datum (Q187, revised before its land in Q191)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q187, lane `amend-e194`; revised before its land the same evening, from about
22:10 PST, in Q191 by the lane `fix-amend194` after its verifier's findings: step 2 v2's never-run check and its desk test (A1-8), the
re-run tests and logs, section 5's items 6 to 8 and the labels), beside [KIT.md](KIT.md), which stays as committed, as
does every kit file. **Written after** E194's registration (`b6ef1ad3`), its kit (`f01e1cb2`) and fwread-e194's firmware read (`15cb0fcb`),
**and before any E194 datum.** It carries out [E194.md's dated amendment A1](E194.md.dated-amendment-A1.md) (A1-3, A1-4, A1-8): kit mechanics and
a gate, named here; **nothing here changes a forecast, a band, a rule, a threshold, K, the order, the plan, the card time, the cap, a
registered stop line, the die gate, the clock rule or the scorer.** New files only, all under `tools/claims-v3/e194/`. No card was claimed
or opened, no device command was sent, no other lab box was reached, nothing was posted. Every desk test below ran on aifoundry2 through
the round's slots (`slot.sh`, nice 10) inside the sandbox (`nodev.sh`: no /dev/et*, an empty /run/lock), the gate's test in its own PID
namespace, and only while the round's quiet-desk flag for aifoundry2 was down.*

## Results first (desk checks of code; nothing new is measured)

Run under `/usr/bin/python3` 3.12.3, bash 5.2.21, git 2.43.0 and bubblewrap 0.9.0, on Sun 15 Nov 2026 between 17:30 and 17:50 PST, and again
on the revised files between 22:10 and 22:50 PST (the logs below are the second runs'), from the files as committed here (the list and step
2 v2's pin of it aside, which the gate's test re-makes in its scratch repository).

| check | result | log |
|---|---|---|
| **the gate and its three step versions** (`rb/selftest_fwgate_e194.sh` under `rb/selftest_fwgate_e194_ns.sh`; a scratch repository at the commit before the amendment with the amendment as one stand-in commit, its own upstream; a stand-in aifoundry2 served by a fake ssh; the box's `uptime -s` this box's real boot unless a case says otherwise): **G1** the record as committed: RECORD EQUAL, the gate's own reading naming all seven fields; **B1-B6** the boot rule by the very box lines: this boot (2026-11-13 16:53:28) ok, a boot after the read (2026-11-15 15:30:00) STOP, a boot at the read's own second STOP, one second before ok, an unreadable boot STOP, another box STOP; **D1** a DIFFERENT record (the read's PMIC 1.5.0 -> 1.5.1, committed): refused, naming DIFFERENT(PMIC), the list, the tree and the comparison's rc 1; **D2** the same change made consistent (its list and comparison re-made): refused (DIFFERENT by the gate's own reading, the list's bytes, the tree); **D3** E69's own statement changed: refused (its bytes; the comparison cannot parse two statements that disagree); **M1** the record's directory removed: refused (missing); **M2** one file gone: refused (missing); **U1** an uncommitted README edit: refused; **K6** the v2 launch's guard text: k6's three lines byte for byte, k6's E69 block absent, E194's boot rule present; **LK1-LK4** the v2 look: FREE with the identity ok; 16 on a boot after the read; 16 on the DIFFERENT record and on the missing record BEFORE ANY BOX CALL; **IS1-IS3** the v2 session step: IDENTITY-STOP on a boot after the read, 16 on the DIFFERENT and the missing record before any box call, nothing launched; **LA1** with this boot and the record EQUAL: past the gate, the rest, the dry pass, the build and the P2 count, LAUNCHED (a stand-in session that opens nothing); **P1-P4** step 2 v2: 0 at every pin with FWGATE-E194 RECORD EQUAL and the read of record the only E194 data; 16 on a second E194 data commit, on the DIFFERENT record, on the amendment's list one line short; **N1** (A1-8) a stand-in E191 third-session folder at HEAD (`docs/reports/data/2026-11-16-e191-blind-day-aifoundry1-c1-s3/`, E191's second session's committed bytes, 269 files, so it names the instance): 0, the folder left out and named in the never-run check's line and the step's last line; **N2** a folder of another form at HEAD (`...-c1-s4`, the same bytes): 16 (never-ran); **N3** the third-session form in the worktree but not at HEAD, nothing else there: 16 (never-ran); **DL** the v2 dry listing (below) and its check; **Z** nothing left | **SELFTEST-FWGATE-E194 14 of 14 PASS** | [`logs/selftest-fwgate-e194.txt`](logs/selftest-fwgate-e194.txt) |
| the v2 dry listing (`rb/list_steps_e194_v2.sh`), every step with stand-ins | **13 steps, 0 exiting non-zero, 0 box calls beyond aifoundry2** (24 calls printed, each to aifoundry2); `desk/drylisting_check_e194.py` PASS (2 device-opening lines, each after an unset of ET_DEVICES and V3_DEVICE); the gate's record named in steps 2, 4 and 9; made after step 2 v2's AMENDPIN count was set, so it prints "pinned at 11 entries" and "the amendment's (11)" (the first listing, made before, printed 0 there); step 2 v2's `git ls-tree` call and its never-run line "E191's third-session folders at HEAD (0)" listed | [`logs/dry-listing-e194-v2.txt`](logs/dry-listing-e194-v2.txt) |

**What the first run of the gate's test caught (stated, not hidden):** case P3 read 0 where 16 was wanted because the test's own
`git cherry-pick -q` is not a git option, so the DIFFERENT record never reached the scratch repository's main; the test now commits D1's file
on main directly, and P3 reads 16. No gate, step or pin changed for it.

**What the revised test's first run showed (stated, not hidden):** it read 14 of 14 PASS, but N1's and N2's resets of the sparse scratch
repository printed one git warning per stand-in file ("not uptodate; will not remove from working tree", 538 lines). A probe showed git
2.43.0 removes such files anyway. The test now removes each stand-in folder before its reset, and checks that none is left before N3; the
second run read 14 of 14 PASS with no warning. No gate, step or pin changed for it.

## 1. What this note adds (each a new file; the kit's v1 files stay as committed and are not used on E194's day where a v2 exists)

| what | file | from |
|---|---|---|
| **E194's own firmware gate** | [`rb/fwgate_e194.sh`](rb/fwgate_e194.sh) | A1-3; k6's `rb_guard_text` (unchanged) |
| **step 2, v2** (outside the amendment's list; its sha256 in the amendment's anchor lines) | [`rb/s03_desk_e194_v2.sh`](rb/s03_desk_e194_v2.sh) | the kit's `rb/s03_desk_e194.sh`, every check kept; its never-run check also leaves out E191's third-session folders at HEAD (A1-8) |
| **the look, v2** | [`rb/s05_look_e194_v2.sh`](rb/s05_look_e194_v2.sh) | the kit's `rb/s05_look_e194.sh`, line for line but the identity |
| **the session, v2** | [`rb/s11_session_e194_v2.sh`](rb/s11_session_e194_v2.sh) | the kit's `rb/s11_session_e194.sh`, line for line but the identity |
| the v2 dry listing | [`rb/list_steps_e194_v2.sh`](rb/list_steps_e194_v2.sh) | the kit's `rb/list_steps_e194.sh` with the three v2 steps |
| the gate's desk test and its PID namespace | [`rb/selftest_fwgate_e194.sh`](rb/selftest_fwgate_e194.sh), [`rb/selftest_fwgate_e194_ns.sh`](rb/selftest_fwgate_e194_ns.sh) | the kit's runbook desk test's form |
| the logs | `logs/selftest-fwgate-e194.txt`, `logs/dry-listing-e194-v2.txt` | |
| the amendment, the brief's note, this note and their list | `E194.md.dated-amendment-A1.md`, `CARD-LANE-BRIEF.md.dated-note-1.md`, this file, `SHA256SUMS-e194-amendment-A1` (every file here but itself and step 2 v2) | |

## 2. The gate (kit mechanics for A1-3's registered conditions)

- **`e194_fwgate_record`** (desk side, in `RB_REPO`; `bash rb/fwgate_e194.sh record [<top>]`): FWGATE-E194 RECORD EQUAL (0) only when the
  record's directory and its ten files are there; its list 8 of 8 OK at sha256 `daa088c8...`; its README at `96fb19c5...`; host aifoundry2 in
  its etiquette read; `15cb0fcb` an ancestor of HEAD and the directory's tree at HEAD `6d1c3802...` (the commit's); nothing uncommitted
  there; E69's statements at `7faefb6a...` (CHANGE-RECORD.md) and `934919a1...` (E69's data README); the record's `compare_fwread.py`
  re-run (`/usr/bin/python3 -I -B`, from the top) exits 0, prints "VERDICT: EQUAL" and reproduces `comparison.txt` byte for byte; the
  gate's own reading of `fwread.stdout` and `fwread.stderr` (colour codes stripped): one command line (code 14), one "Service request
  succeeded", exactly one line per field and each equal to E69's value pinned in the gate (release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.5.0,
  the three minions 0.25.1); `fwread.meta.txt`: rc 0, card 0 under card 0's lock, the start at epoch 1794784922. Else FWGATE-E194 RECORD
  REFUSED (16) with every reason named (missing, list, list-bytes, readme-bytes, host, commit, tree, uncommitted, e69-change-record,
  e69-readme, compare, compare-verdict, compare-bytes, own-reading, DIFFERENT, meta).
- **`e194_fwgate_text look|launch`** (box side, after k6's prelude): `uptime -s` read on the box, `date -d` to epoch seconds, ok only when the
  box is aifoundry2, the epoch is a number and it is strictly below 1794784922 (2026-11-15 15:22:02 PST); the look prints "identity: ...: ok"
  or "identity: ...: STOP" (the look's v1 patterns), the launch prints IDENTITY-STOP and exits 3 (nothing launched) or "identity: ...: ok".
  **`bash rb/fwgate_e194.sh boot '<time>'`** runs those same lines with `uptime` stood in by the given time (the test's B1-B6).
- **`e194_guard_text_a1`**: k6's `rb_guard_text`'s first three lines verbatim (K6 checks them byte for byte against k6's own), then the
  launch's boot lines in place of k6's firmware block. **`e194_fwgate_desk`**: the record through k6's bounded runner (`rb_local`), 16 and
  no box call unless EQUAL.
- **Reads only.** The gate opens no device and sends no card command; it never sends the firmware-revisions query.

## 3. Step 2 v2's pins and rules (beside every v1 pin, unchanged)

- `AMENDPIN`: `SHA256SUMS-e194-amendment-A1` at its count and its own sha256 (set at the amendment's commit; both in the anchor lines);
  `FWPIN`: the read's `SHA256SUMS`, 8 entries, `daa088c8af935923ca3fb8654f84eee9b4f9311462b48484560928af4ee6772c`, every entry OK from its
  directory; the kit's list 78 entries at `2f3da024...` and every v1 list, as v1.
- The kit commit and the amendment commit (each by its content) ancestors of HEAD, beside v1's registration and E189 ancestry.
- **"E194 data in any ref"**: the commits of any ref naming a `docs/reports/data/*e194*` path must be exactly `15cb0fcb`, and every path
  they name must lie in its directory (v1 required none, and would refuse the read of record: the kit's anchor line 7 reads it as 1 line).
- FWGATE-E194 RECORD EQUAL; the amendment's two logs with their PASS lines, beside the kit's.
- **THE NEVER-RUN CHECK (A1-8):** v1's command, every exclusion kept, plus one `--exclude` for each directory at HEAD whose path is exactly
  `docs/reports/data/<YYYY-MM-DD>-e191-blind-day-aifoundry1-c1-s3` (read by `git ls-tree -d --name-only HEAD docs/reports/data/`, a logged
  call, and matched by the pattern `^docs/reports/data/[0-9]{4}-[0-9]{2}-[0-9]{2}-e191-blind-day-aifoundry1-c1-s3$`). The check's line in
  the runbook log names each (or 0), as do the step's last line and its log line; a failed `git ls-tree` refuses (16). A folder of any other
  form, or one of this form in the worktree but not at HEAD, is not left out: if it names the instance, NAMED BEFORE (16).

## 4. The card lane's steps, as amended

B, 0, H, 1 as the brief; **2: `rb/s03_desk_e194_v2.sh`**; Q; **4: `rb/s05_look_e194_v2.sh`**; 3 (none); 5, 6, 7, 8 as the brief; **9:
`rb/s11_session_e194_v2.sh FULL`**; 10, 11, Q', 12, 13, E as the brief. The window from the card lane's booking (A1-4). The brief's dated
note 1 ([`CARD-LANE-BRIEF.md.dated-note-1.md`](CARD-LANE-BRIEF.md.dated-note-1.md)) gives the rows.

## 5. What the desk cannot show (for the verifier and the readiness critic)

1. **The v2 look and launch have run only against the stand-in box** (the fake ssh, a stand-in `uptime`, et-who and session); their first
   real call is the card day's. The boot rule's lines were also run on this box's own boot by `fwgate_e194.sh boot "$(uptime -s)"` (a desk
   read: ok while the box has not rebooted since the read).
2. **The read's EQUAL rests on version numbers** (A1-2): another build carrying the same seven numbers would read the same.
3. **The boot is read by `uptime -s`, k6's way;** a clock step on the box between the boot and the read would move it. The kernel's own
   boot stamp agrees today (desk read).
4. **Step 2 v2 has run for real only on this lane's scratch clone** with the amendment's commit local; on the card day it runs on the lab
   clone after the land (its anchor lines name the commit).
5. Everything KIT.md section 8 lists but its item 1 (answered by A1) stands.
6. **The boot line passes any string GNU `date -d` parses** (added before the land, after the verifier's attacks A14 and A15): a
   blank-but-nonempty string (read as that day's 00:00) or a relative word would read as a time. `uptime -s` prints neither (it prints
   `YYYY-MM-DD HH:MM:SS`), and its empty output refuses (the verifier's case B7). The gate is unchanged.
7. **The boot rule reads the host's boot, k6's proxy** (added before the land): the gate's header says the card "has not restarted since
   the read", but what it reads is the host's `uptime -s`. A card reset or a driver reload without a host reboot is not seen by it (the
   lab sends neither: both stay forbidden, and no lane of ours may do either). The runner's identity gate (a) and (b) reads which card each
   process reached (its nodes, its device ID) at the session, not the card's firmware.
8. **E191's third-session folder has not landed** (added before the land): N1-N3, and the land's two full-tree runs of step 2 v2 (its
   LAND.md), use stand-ins carrying E191's second session's committed bytes under the third session's folder form; the real `-s3` record is
   first read on the day it is at HEAD.

## 6. Labels

Every figure quoted from E194.md and its amendment is **registered**. **Nothing new is measured here; the read's time, rc and seven values
are measured** (as committed in `15cb0fcb`). The desk tests' results are **desk checks of code**, not measurements. Nothing here is blind
or held out, and no E194 datum exists.

## Builds on

The kit (`f01e1cb2`: KIT.md 3, 4, 8 and 11; `rb/rb_e194.sh`, `rb/s03_desk_e194.sh`, `rb/s05_look_e194.sh`, `rb/s11_session_e194.sh`,
`rb/list_steps_e194.sh`, `rb/selftest_rb_e194.sh`'s form, `desk/drylisting_check_e194.py`), k6's `rb_common.sh` (`rb_guard_text`,
`rb_local`, `rb_remote`, unchanged), fwread-e194's record (`15cb0fcb`), E69's two statements, and E191's kit dated note 2 (the form of a
kit note carrying an amendment). *Check against an earlier measurement of the same quantity:* the gate re-reads fwread-e194's seven values
against E69's (EQUAL).

## Compute

On aifoundry2 through the round's local slots, one job at a time, in the sandbox: the gate's test (about 40 s to 5 minutes; seven runs of step
2 v2 on a sparse scratch repository), the v2 dry listing (seconds). No other box, no card.

SPDX-License-Identifier: Apache-2.0
