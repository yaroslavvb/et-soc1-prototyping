# E209's kit, dated note 1 (Tue 17 Nov 2026, after E209's session, before its data commit): the collection's scrub stop, fixed in E200's registered form (one line of fwgate's read record, the box's home written as "~"); the fixed collection and step 13's manifest read as new scripts; the order of steps 4 and 5 on a new box root

*Written on aifoundry2 from about 11:10 PST on Tue 17 Nov 2026 (week 47) by the clock, by the lane `note-e209` of round Q212. Desk only: no
card, no device command, no booking, no post; the session's files were read and never written. **New files only**, all under
`tools/claims-v3/e209/`: the registration [`E209.md`](E209.md), [`KIT.md`](KIT.md), every file of the kit's list `SHA256SUMS-e209-kit`,
step 2 (`rb/s03_desk_e209.sh`) and every other committed file stay as committed. **Nothing here changes a forecast, a point, a band, a rule,
a threshold, the order of the runs, the card time, the cap, a stop line, the scorer, E208's kit, the box files or any datum, and no score or
forecast number is in this note.** Labels: **registered** (E209.md, the kit, and this note's reading, stated before E209's data commit),
**measured** (the session's own files and their sha256), **desk check of code** (by file and line, at the committed bytes), **desk test**
(this note's test, on the real files read only and on stand-ins). Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2.*

## 1. The defect: the collection's scrub refused fwgate's real read record

- **What happened (measured; the card lane's runbook log).** E209's session ran on aifoundry2 card 0 from step 7's first card command at
  10:30:44 PST (fwgate's one firmware-revisions READ) to its end at 10:56:57 PST, runner rc 0 (session `1794940244-a2c0-E209`). Step 11
  (`rb/s22_collect_e209.sh`, which runs `collect_e209.py`) started at 10:57:21 PST and stopped with exit 16, in its words: "COLLECT STOPPED: THE
  SCRUB found 1 file(s) with a private string (['first/fwgate-aifoundry2-c0-20261117-103044.json: the login name']): nothing written in LAB;
  tell the orchestrator". Nothing was written in the lab. The card lane's stop path followed at 10:58:42 PST (the quiet-desk flag lowered,
  the collect span left, the hold line removed, the booking released).
- **The cause (desk check of code).** Line 34 of fwgate's read record, which step 7 copies into the session's `first/`, reads
  `"ledger": "<the box's home>/.local/state/fwgate/aifoundry2-c0.jsonl",`. There fwgate.py (`4d529a57...`, the box root's copy at its pin)
  writes the path of its attempt ledger for this card (`str(ledger_path(...))`, its line 588), whose folder outside a desk test is
  `real_ledger_dir()`: the user database's home plus `.local/state/fwgate` (its lines 108-109). **So every real READ record carries the box's
  home in that one line.** `collect_e209.py`'s scrub (its lines 129-147) refuses any copied file that holds the login name, the home path, the
  box root's path or the home root, so it could not pass a session whose step 7 sent a real READ: this boot's case (the reboot gate read
  NEEDS-READ).
- **Why the desk did not see it.** Every desk test of the kit ran fwgate in its desk mode, whose ledger folder is the desk's own
  (`FWGATE_LEDGER_DIR`, fwgate.py line 155), so no desk record held a home.
- **Nothing else is private (this lane's inventory, and the desk test's R1).** Read line by line with the scrub's own patterns (every file,
  `.gz` unpacked), the card lane's copy-back (224 files) and the checker's two outputs hold such a string in that one line alone, and the box
  root's session equals the copy-back file for file (224 of 224). The data directory R1 wrote from them (232 files: the build record, step
  6n's two files, the facts and the README among them) holds none after the mask.

## 2. The fix: E200's registered form, for that one line (registered here, before E209's data commit)

E200's collection wrote the box's home as "~" in the same ledger line (`collect_e200.py`'s scrub, its lines 130-131, registered before any
E200 datum), and E200 sitting 1's [`README.md.dated-note-1.md`](../../../docs/reports/data/2026-11-16-e200-regfile-sitting-1-aifoundry2/README.md.dated-note-1.md)
(section 1) records the result: the committed record differs from the box's manifest by that line alone. For E209:

- **In the committed copy only**, line 34 of `session/first/fwgate-aifoundry2-c0-20261117-103044.json` reads
  `"ledger": "~/.local/state/fwgate/aifoundry2-c0.jsonl",`, E200's committed line byte for byte. **Nothing else changes**, in that file or in
  any other: the session's `MANIFEST.sha256` stays as the box wrote it, and every other file is the box's bytes.
- **The raw record stays on aifoundry2, outside the lab:** in the card lane's box root and in its copy-backs (the first, made by the stopped
  step 11, and the one the fixed step 11 makes), each at the box's sha256.
- **The record's sha256, both ways** (measured, the desk test's case R1 on the real files; 111 lines either way, 2,311 bytes on the box and
  2,296 committed):

| `session/first/fwgate-aifoundry2-c0-20261117-103044.json` | sha256 |
|---|---|
| the box's bytes: line 20 of the session's `MANIFEST.sha256` (that list's own sha256 `e7ec7162a87b219e5dcf6704def364c8b6aabc58007bf7c7a43e6c9f1b5d5154`, 221 lines) | `a91fcc837457ffb2c447ceeb61800bfec3bde1eeab2a5f85884eb1ced95fe47d` |
| the committed bytes, that one line masked | `2d56a73219f7ba99b08986ef723a46477444feda7b3db7f255eb6e027e09a377` |

  With the box's home written back in place of the "~", the committed file reads the manifest's sha256 again; that is what step 13's
  manifest read checks (section 3).

**Dated sentence (Tue 17 Nov 2026, PST):** E209's collection writes the box's home as "~" in line 34 of
`session/first/fwgate-aifoundry2-c0-20261117-103044.json` (fwgate's attempt-ledger path), in its committed copy only, so that file alone
differs from its line in `session/MANIFEST.sha256`; every other file is the box's bytes, and any other private string still stops the
collection.

## 3. The fixed collection and step 13's manifest read: three new scripts

| step | the kit's script (unchanged, still in the kit's list) | this note's script (new) | what differs, and nothing else |
|---|---|---|---|
| 11, the collection | `collect_e209.py` (`e8195bf3...`) | [`collect_e209_n1.py`](collect_e209_n1.py) | (1) **THE MASK** before THE SCRUB, in the data directory's copy only; (2) the copy-back's name `RB_OUT/copy-n1/<SID>/` (`--copy-name`), with E208's checker's outputs in `RB_OUT/copy-n1/checks/`, refused (10) if that name is taken, so the stopped step 11's copy-back `RB_OUT/copy/<SID>/` and its `RB_OUT/checks/` stay as they are; (3) two printed lines (the copy-back's name; the masked line with both sha256) and `RB_OUT/copy-n1/mask-n1.json` with the same, outside the lab; (4) `--manifest-check SESSION_DIR` for step 13 |
| 11, its runbook step | `rb/s22_collect_e209.sh` (`f047b758...`) | [`rb/s22_collect_e209_n1.sh`](rb/s22_collect_e209_n1.sh) | runs `collect_e209_n1.py` (`RB_COPY_NAME`, default `copy-n1`); writes the collector's words to `RB_OUT/collect-n1.txt` (the stopped step's `collect.txt` stays); the collect span it requires outside a desk test is `RB_ONELAB_LANE`'s (default `RB_LANE`), so a lane that re-runs step 11 may hold the span under its own name while THE QUIET DESK FLAG stays the card lane's |
| 13, the reduction and the frozen scorer | `rb/s24_score_e209.sh` (`56542a98...`) | [`rb/s24_score_e209_n1.sh`](rb/s24_score_e209_n1.sh) | its one manifest read: in place of `sha256sum -c --quiet MANIFEST.sha256` in the committed session (its line 26), which the masked record fails by design (the desk test's M0 and W2: step 13 would refuse, 10), `collect_e209_n1.py --manifest-check`: every line read as `sha256sum -c` reads it, but fwgate's read record, which passes only when it holds exactly one masked ledger line and, with the box's home written back there, reads its manifest line and masks back to the same bytes |

- **THE MASK's reach, exactly:** only a file named `first/fwgate-aifoundry2-c0-<YYYYMMDD>-<HHMMSS>.json` (fwgate's read record as step 7
  copies it); only a line whose ledger path is exactly the user database's home plus `/.local/state/fwgate/aifoundry2-c0.jsonl` (the home is
  read as fwgate.py and the scrub read it); exactly one such line (two: exit 16, nothing written in the lab); no such line: nothing masked.
  THE SCRUB then reads that record as masked and every other file as copied, with `collect_e209.py`'s patterns and words: a login name, a
  home path, the box root's path or the home root anywhere else stops the collection with 16, as before.
- **What the masked line touches downstream (desk check of code):** E208's reducer (`reduce_mms.py`), the frozen scorer (`score_e209.py`) and
  the readings (`rb/post_e209.py`) name no fwgate record; E208's checker runs on the raw copy-back and names none either (its C6 reads every
  file's lines for a kill word, and the masked line holds none, as the raw does). So the mask changes no number, verdict or check reading.
- **E209's step 11 again (no card command: the session ran)**, from the card lane's RB_OUT and box root, with THE QUIET DESK FLAG raised as
  the card lane's (`rb/quiet_e209.sh raise card-e209`) and the collect span held:
  `RB_OUT=<card-e209's RB_OUT> E209_ROOT=<its box root> RB_QUIET=<the round's flag file> RB_LANE=card-e209 RB_W=<the round's folder>
  [RB_ONELAB_LANE=<the lane holding the collect span>] bash $W/slot.sh bash tools/claims-v3/e209/rb/s22_collect_e209_n1.sh`, which ends
  0 "DATA DIR docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2 written; THE QUIET DESK FLAG lowered after the copy-back" (the desk
  test's S1 wrote that directory, 232 files, from the real session into a stand-in lab). Then step 12 as the card-lane brief gives it, the
  data README's dated notes naming this masked line with its two sha256 (the form's `session/` row reads "byte for byte" but for it); then,
  after the data commit only, step 13 as `RB_OUT=... bash $W/slot.sh bash tools/claims-v3/e209/rb/s24_score_e209_n1.sh`. `rb/end_e209.sh`
  acts on RB_LANE's flag, spans, hold line and booking only: a lane that holds the span or the hold under its own name releases them itself.

## 4. The order of steps 4 and 5 on a new box root (a departure card-e209 took; both steps send nothing)

- **What happened (measured; the card lane's runbook log).** At 10:25:44 PST step 4 (`rb/s05_look_e209.sh`) refused with 16: "the reboot
  gate's look ended rc 2". The look runs fwgate.py from the box root (`e209_fwgate` in `rb/rb_e209.sh`), and on the new, empty box root the go
  lines require, only step 5 (`rb/s07_sync_e209.sh`, `make_box_e209.py sync`) puts it there. fwgate never ran: its ledger was unchanged since
  Mon 16 Nov 09:37:17 PST, and nothing was sent. At 10:28:03 step 5 ran ("SYNCED: 72 files at the harness's sha256", from HEAD `a90105da`),
  then at 10:28:07 step 4 again: "FREE; the reboot gate: NEEDS-READ". No step was otherwise changed and no gate was skipped: fwgate's own look
  gave its verdict after the sync.
- **Why the desk did not see it.** E200's look read fwgate from another place, and no desk test of E209's kit ran step 4 on a new, empty box
  root (the real-path test makes each box root with `make_box_e209.py sync` first).
- **The reading registered here,** for E209 and any later kit of E209's form: on a new, empty box root, step 5 runs before step 4. Both are
  no-device steps; step 4's verdict is then fwgate's own look on the synced copy, at its pin `4d529a57...`, which step 5 reads back. No
  script changes.

## 5. Step 2 and step 0 with this note (desk checks)

- **Step 2** (`rb/s03_desk_e209.sh` at its anchor `7eabc8ee...`, unchanged) takes this note: its history check allows additions under
  `tools/claims-v3/e209`, net and commit by commit, and none of the new files is named like a standard-library module; the six pinned lists
  are unchanged (no new file is in one, and `SHA256SUMS-e209-note-1` is among the lists step 2 only REPORTS); `preflight_e209.sh` audits a
  fixed list (the new scripts were audited apart: `dmcmd_audit: GO (0 send site(s), 0 disallowed; allow-list: none)`). Run in its desk mode
  in a scratch clone with this note's seven files committed locally (this note then a draft; step 2 never reads a note's text): **STEP2
  PASS** at 11:29:59 PST, on GitHub main `75ecdd29` plus this note (its history check: "56 additions and nothing else under tools/claims-v3/e209 since it, and commit by commit (2 commit(s) touching it, each adding only; no merge)"; each of the six pinned lists at its count and its own pin; `SHA256SUMS-e209-note-1` REPORTED, 6 OK of 6), and the control with one more file left untracked under the folder refused (10, "the paths E209 runs from are not clean").
- **Step 0's anchor read** (the readiness lane's `go_anchors_e209.sh`) reads NOT AS STATED once this note lands, on exactly **C3, H1a, H1b and H6d** (4 of 110 lines, read at 11:30 PST against the same scratch clone: the kit's commit is no longer the folder's last, and the folder's tree, its file count and the history read at HEAD change), by
  design (its own control "a note under tools/claims-v3/e209"): any later E209 session needs a fresh readiness. Steps 11-13 read no anchor
  line.

## 6. The desk test

[`desk/desktest_n1_e209.py`](desk/desktest_n1_e209.py), run from a scratch clone inside the round's slot and no-device sandbox while THE
QUIET DESK FLAG was absent; its log, as run, is [`logs/desktest-n1-e209.txt`](logs/desktest-n1-e209.txt) (the home written as `<home>`, the
login as `<login>`, the work folder as `<work>`): **DESKTEST-N1-E209 32 of 32 PASS**. That log is the test's third run (11:25:52 PST). Its
first (11:22:49) read 27 of 32: the test's own stand-in maker emptied each file it edited (it opened the file for writing before reading
it), so five F cases ran on emptied files; that was fixed in the test, not in the collector. The second (11:24:06) read 32 of 32, and the
third only reworded two of the test's descriptions and read the home root from the user database in place of a literal path.

| cases | what | result |
|---|---|---|
| R1 | the real session, `collect_e209_n1.py`, beside the stopped step's first copy-back | exit 0; `session/` equals the copy-back but for the record, which differs in its line 34 alone, that line E200's form; raw sha256 = its manifest line; nothing private in the data directory; its `SHA256SUMS` reads OK; the first copy-back untouched |
| R2 | the real session, `collect_e209.py` (the kit's) | exit 16 with card-e209's words: the stop, reproduced |
| EQ | `collect_e209.py` on a stand-in whose record is masked beforehand (its manifest line made to match) | its data directory equals R1's in every file but `session/MANIFEST.sha256` and `SHA256SUMS` (one line each): THE MASK and nothing else |
| C1, C2 | the copy-back's name taken; a bad name | exit 10 each, nothing written |
| P2 | a record whose ledger path holds no home (a desk ledger folder) | exit 0, nothing masked, the record at its own bytes |
| F1-F10 | the home in another line of the record; the login alone in fwgate's stderr; another user's home folder in `runner.out`; the box root's path there; the ledger line with another home; with another card's ledger; its text outside a record; two ledger lines; the home inside a `.gz` file; the record under another name | exit 16 each, naming the file, nothing written in the lab |
| M0-M7 | step 13's manifest read on R1's session folder | the kit's `sha256sum -c` FAILS on the record alone (M0); `--manifest-check` exit 0 with 1 line by THE MASK (M1), 0 on the raw copy-back (M6); exit 10 for another file changed, the record changed in a second line, the "~" read as another home, a file missing, the masked form under another name (M2-M5, M7) |
| S1-S4 | `rb/s22_collect_e209_n1.sh` | in its desk mode on the real session: exit 0, the stand-in flag lowered, its data directory equal to R1's; outside it: no span, exit 10; `RB_ONELAB_LANE` read for the span (refused without it, held with it, then a bad copy name refused before any write) |
| W1-W3 | `rb/s24_score_e209_n1.sh` in a stand-in repository with a committed stand-in data directory (the masked record and its manifest line only) | the manifest read passes, 1 by THE MASK, and the reducer runs (exit 14 on the stand-in, as it must); the kit's `rb/s24_score_e209.sh` refuses there at its manifest read (10); a second changed line: refused (10) before the reducer |
| Z | the card lane's RB_OUT, the box root's session, the repo | unchanged; no data path written in the repo |

## 7. Files (all new)

| file | what |
|---|---|
| `KIT.md.dated-note-1.md` | this note |
| `collect_e209_n1.py` | the fixed collection (section 3) |
| `rb/s22_collect_e209_n1.sh`, `rb/s24_score_e209_n1.sh` | step 11 and step 13 with it (section 3) |
| `desk/desktest_n1_e209.py`, `logs/desktest-n1-e209.txt` | the desk test and its log (section 6) |
| `SHA256SUMS-e209-note-1` | the sha256 of the six files above, paths from the lab's top |

SPDX-License-Identifier: Apache-2.0
