# blind-e219: dated note 1, the folder as landed and verify-blind-e219's findings on it

*Fri 20 Nov 2026, Pacific time. Written by the lab's lane land-blind-e219 (round Q232) at 01:17 PST for this folder's commit, after verify-blind-e219 held it WITH FIXES (00:32-01:05 PST). Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), standard library only, single-threaded. This note changes no file of the folder and no number, forecast, rule or verdict; nothing in it is a measurement.*

## What is committed here

- **The folder** is decl-e219's land byte for byte: 38 files and `SHA256SUMS` (sha256 `f8e1e8eb9608763f...`, 38 of 38 OK), written at 18:42:13 PST on Thu 19 Nov, after the declaration (18:37:19), the nominal forecasts (18:37:34) and FROZEN.txt (18:37:50), before the freeze post and before any E219 session.
- **The verification.** verify-blind-e219 re-derived the lab's blind score of E219 with its own code and checked this folder:
  - every sha256 in FROZEN.txt equals its file, here and in decl-e219's lane folder;
  - its own caller re-made the nominal forecasts at the declared conditions: 12,494 of 12,510 fields bit-equal, and the other 16 differ by one unit in the last place (a pass's seconds and joules over idle of the three count controls at the 6 subset cases);
  - its own run list from the committed data equals `inputs/step1/runs-listed.json` with 0 field differences (392 runs, 314 cases; 203 runs and 139 cases in the domain), and all 175 out-of-domain cases raise KeyError in MM1-v3.1, MM1-v3 and MM1-v2;
  - its own driver over a fresh Verilator 5.042 build re-counted 4 points on E219's own kind tiles: three fp32 points bit-equal to E210's committed raw points (61 of 61 fields each), and the int8 full launch point equal to the committed counts-v2 point in 63 of 64 fields (the one other is a count of trace identifiers, not a switch-table input);
  - the T1, T3, E1, E3 and watts band bases and the twin keys re-derive from MM1-v3.1's landed points;
  - the folder holds new files only. Its fixes to this folder are the two below, both to land texts; none changes a number.
- **This note adds two new files**, and `SHA256SUMS-note1` with their sha256. It edits no file:
  - `README.md.dated-note-1.md`, this note;
  - `scripts/SCRUB-MAP.json`, each landed script's sha256 as run and as landed (finding 2).
- **The blind score** made exactly as this folder declares is the next commit's folder, `../blind-e219-scores/`.

## The freeze line, checked on this folder

Posted on the coordination Discussion as #14.1.1 (2026-11-19 18:42:34 PST in the round's record; 18:42:28.612 PST by the Discussion watcher's record of the post), before E219's first session. The five sessions' first card commands came 19:50:48.917 to 22:34:52.364 PST, 68.25 to 232.31 minutes after the post (counted from the later time, 18:42:34, as blind-e219 and the verifier read it), so all five are BLIND for this test:

- `FROZEN.txt` `73a2dd754b70d18a4a7803cd782b1179984d36185c762058d94219ad0fc69f1e`: the posted sha256, equal here.
- `DECLARED-blind-e219.md` `d629bd14aff6fe4d214931fc6bad6b684ab910cd42bb5afdc07b8f8f62330495`: the posted sha256, equal here.
- `DECLARED-blind-e219.json` `670caa8c2f29a5d1d95591df0cba3ab80047d0f4b5dc27b8f2568c1da480f479`: the posted sha256, equal here.
- `forecasts-nominal-e219.csv` `5433f8c4e88642bad32909a491eb47321a854fad7f2785a188d4ce8d072a3a67`: the posted sha256, equal here.
- `forecasts-nominal-e219.json` `d605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899`: the posted sha256, equal here.

FROZEN.txt names 11 files by sha256, under decl-e219's own folder names. The README's map gives each one's place here (`work/step2/` is `inputs/step2/`). Each was checked at that place:

| record, line | sha256 | listed as | here | check |
|---|---|---|---|---|
| FROZEN.txt 6 | `d629bd14aff6fe4d...` | `DECLARED-blind-e219.md` | `DECLARED-blind-e219.md` | byte-equal |
| FROZEN.txt 7 | `670caa8c2f29a5d1...` | `DECLARED-blind-e219.json` | `DECLARED-blind-e219.json` | byte-equal |
| FROZEN.txt 8 | `5433f8c4e88642ba...` | `forecasts-nominal-e219.csv` | `forecasts-nominal-e219.csv` | byte-equal |
| FROZEN.txt 9 | `d605db13b6342a28...` | `forecasts-nominal-e219.json` | `forecasts-nominal-e219.json` | byte-equal |
| FROZEN.txt 11 | `46d30dea607d7710...` | `scripts/s02b_nominal.py` | `scripts/s02b_nominal.py` | byte-equal |
| FROZEN.txt 12 | `4a745f7b70edb759...` | `scripts/s02w_walk.py` | `scripts/s02w_walk.py` | byte-equal |
| FROZEN.txt 13 | `b8b9a4072caa006a...` | `scripts/s02c_write.py` | `scripts/s02c_write.py` | byte-equal |
| FROZEN.txt 14 | `1c6172047d5aafa9...` | `work/step2/fc-nominal.json` | `inputs/step2/fc-nominal.json` | byte-equal |
| FROZEN.txt 15 | `9c13958d026c8a6f...` | `work/step2/walk-feats-e219.json` | `inputs/step2/walk-feats-e219.json` | byte-equal |
| FROZEN.txt 16 | `3ebd6e637165b499...` | `logs/step1-sha256.txt` | `logs/step1-sha256.txt` | byte-equal |
| FROZEN.txt 17 | `17699cfed6f3bdf8...` | `logs/step2-sha256.txt` | `logs/step2-sha256.txt` | byte-equal |

So all 11 keep their bytes at their mapped place, and in decl-e219's lane folder all 11 still equal their listed sha256. The other inputs here (`inputs/step1/`, `inputs/recheck/recheck.json`, `inputs/v32-status.json`) are byte-equal to decl-e219's lane files too.

## verify-blind-e219's findings on this folder, answered

1. **The round's strict public-text scan (low).** The scan (`pubscan_strict.py`, sha256 `76ea74d9...`) finds 14 hits in this folder. Each was read, and each is a false positive:
   - **8 hits** (two e-mail-address patterns each, four files): the value of the git URL rewrite in `scripts/env.sh` line 7, `scripts/s01b_models.py` line 32, `scripts/s05_land.py` line 27, `scripts/s06_result.py` line 16. It is an environment-only rewrite of GitHub's scp-style address prefix to its HTTPS one, not an address or a credential, and the same value is in 39 committed lab files at e97216b7.
   - **6 hits**: a common word for a folder's top level, which the scan's pattern for the administrator account also matches, in `logs/progress.txt` line 4, `scripts/s00b_setup_kit.sh` lines 4 and 21, `scripts/s02c_write.py` line 3, `scripts/s06_result.py` lines 2 and 177 (the kit copy's top folder, or the lane's own).
   - **They stay as they are.** These are the verified bytes, and `scripts/s02c_write.py` is one of FROZEN.txt's supporting files (`b8b9a407...`). The verifier's other answer, placeholders and rewording in the landed scripts, would change verified bytes and `SHA256SUMS`, so the hits are recorded as read here instead (decl-e217's note 1 did the same). This note and the other new file add no hit of that scan.
2. **`scripts/s05_land.py` does not reverse (nit).** `scripts/SCRUB-MAP.json` now lists all 19 landed scripts, with each one's sha256 as run and as landed. The checks:
   - 8 are byte-equal to the scripts as run, and 11 carry placeholders for the box's paths (`<W>`, `<LAB>`, `<SCRATCH>`, and `~` for the home folder).
   - decl-e219's own replacement table, applied to each script as run, gives its landed bytes: 19 of 19.
   - The table applied backwards gives the bytes as run for 18 of 19: 10 of the 11 with placeholders, as the verifier found.
   - **The exception is `scripts/s05_land.py`**, because it holds the table itself. Its literal placeholder strings stay as they are, its scratch entry, a literal path, reads ('<SCRATCH>', '<SCRATCH>') once replaced, and its own `~` stands for itself, so putting the strings back cannot tell them apart. Its landed bytes are the table applied to its bytes as run, as for the others.
   - `logs/step1-sha256.txt` names 8 scripts that carry placeholders here; the map's sha256 as run equals that log's line for all 8, so the log ties to the scripts as run through the map.
   - The strings the placeholders stand for are the box's paths, so they are not written here.
3. **The measured conditions (info).** The primary footing reads each run's conditions "from the data's start-of-run records only" (`DECLARED-blind-e219.md` line 84). Its field list (line 85) also names two window values of each run's primary view, `kclock_mhz` and `rails.minion.mV`, beside the start die. So T3 equals T1 by construction, as the declaration itself states. Nothing changes: it was declared.
4. **The CTRL tie to E217 (info).** The declared tie of E219's 8 CTRL configurations to E217's committed means could compare nothing: E217 never ran those configurations on the same card, and that was knowable from E217's registered schedules before this freeze. Post hoc, 4 of them ran on the other card; `../blind-e219-scores/` reports them beside (REPORTED). Nothing changes.
5. **The sealed forecast's digest (info).** The prefix `ba9e24aa` of the model session's sealed E219 forecast appears in `DECLARED-blind-e219.md` lines 81 and 137, in `DECLARED-blind-e219.json` (3 lines: the proposal's own words, which quote the full digest, and the two lines saying the forecast was not read) and in `scripts/s01e_declare.py` and `scripts/s06_result.py`. No forecast number appears anywhere here, and the full digest is already on main in E219's registration (`tools/claims-v3/e219/E219.md`).
6. **MM1-v3.2 (info).** MM1-v3.2 first entered GitHub main with 4e386f75 (committed 19:50:04 PST, pushed by 19:50:09): about 72 minutes after this freeze, 67.5 after the post (18:42:34), and under a minute before E219's first card command (44.9 s by its commit time). It was not on main at the declaration (`inputs/v32-status.json` reads NOT_ON_MAIN), so it is not declared here, and the blind score correctly does not score it.

## What the verifier did not check

- The freeze post's text on the Discussion itself (it read the round's record and the watcher's timestamp).
- The T2, E2 and E4 band bases (they need held-out predictions that are not in the landed files), fp16 counts, and the post hoc R-ladder fits and E217 other-card ratios (in `../blind-e219-scores/`).

SPDX-License-Identifier: Apache-2.0
