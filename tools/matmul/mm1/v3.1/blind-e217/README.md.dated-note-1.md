# blind-e217: dated note 1, the folder as landed and verify-blind-e217's findings on it

*Thu 19 Nov 2026, Pacific time. Written by the lab's lane land-blind-e217 (round Q228) at 22:17 PST for this folder's commit, after verify-blind-e217 held it WITH FIXES (21:19-21:56 PST). Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), standard library only, single-threaded. This note changes no file of the folder and no number, forecast, rule or verdict; nothing in it is a measurement.*

## What is committed here

- **The folder** is decl-e217's land byte for byte: 81 files and `SHA256SUMS` (sha256 `996dd5ebaed6edc0...`, 81 of 81 OK), written at 12:25:58 PST, after the declaration (11:35:59), FROZEN.txt (11:37:53) and COUNTS-FROZEN.txt (12:22:24), before any E217 session.
- **The verification.** verify-blind-e217 re-derived the lab's blind score of E217 with its own code and checked this folder: every sha256 in FROZEN.txt and COUNTS-FROZEN.txt equals its file; its own caller re-made the nominal forecasts at the declared conditions, 30,948 fields bit-equal; its own driver over a fresh Verilator 5.042 build re-counted 14 of the new count points and one committed point bit-equal, and rebuilt four rows of the tables; the T1 and E1 band bases and the time twin keys re-derive; the contention term's walk features re-made for 93 of 125 configurations, 1,302 fields equal; the folder holds new files only. Its fixes are the four below, all to land texts; none changes a number.
- **This note adds four new files**, and `SHA256SUMS-note1` with their sha256. It edits no file:
  - `README.md.dated-note-1.md`, this note;
  - `counts-e217/as-frozen/counts-e217.csv` and `counts-e217/as-frozen/counts-e217-tiles.csv`, the frozen bytes of the two count CSVs (finding 1);
  - `scripts/SCRUB-MAP.json`, each landed script's sha256 as run and as landed (finding 4).
- **The blind score** made exactly as this folder declares is the next commit's folder, `../blind-e217-scores/`.

## The freeze lines, checked on this folder

Posted on the coordination Discussion as #13.1.1 (2026-11-19 12:26:07 PST in the round's record, 12:25:56 PST in the round log; the exact second is not checked), before E217's first session (its first card command 14:41:14.595 PST):

- `FROZEN.txt` `32311daf2e0ace10d4efdce2be7a3248fb82b2ab852c0acc45fa6c6f37bd42a8`: the posted sha256, equal here.
- `DECLARED-blind-e217.md` `099806dc1a5cb6c53ed7ea0645d5e2b3ae55e0d7734872a467019222da324405`: the posted sha256, equal here.
- `DECLARED-blind-e217.json` `633d725620d06295a144312956579fabc54462f109ea3a29e8026d992bdd4eb7`: the posted sha256, equal here.
- `forecasts-nominal-e217.csv` `4725efa361c16059bae8a5182a5455718ca1d053633293474668983370cdb3e6`: the posted sha256, equal here.
- `forecasts-nominal-e217.json` `611ca08d27c81f0972e5d2b1f23ac24d0455a602cfe87a665963d83af1fdc97c`: the posted sha256, equal here.
- `COUNTS-FROZEN.txt` `4867c1d0be500da2f2d2a7a8fd757a1b893b92d802616b2195f10a34bcc89e01`: the posted sha256, equal here.

FROZEN.txt and COUNTS-FROZEN.txt name 22 files by sha256, under decl-e217's own folder names. The README's map gives each one's place here (`work/step2/` is `inputs/step2/`, `cnt/counts/` is `counts-e217/`, `cnt/work/counts/` is `counts-e217/raw/`). Each was checked at that place:

| record, line | sha256 | listed as | here | check |
|---|---|---|---|---|
| FROZEN.txt 5 | `099806dc1a5cb6c5...` | `DECLARED-blind-e217.md` | `DECLARED-blind-e217.md` | byte-equal |
| FROZEN.txt 6 | `633d725620d06295...` | `DECLARED-blind-e217.json` | `DECLARED-blind-e217.json` | byte-equal |
| FROZEN.txt 7 | `4725efa361c16059...` | `forecasts-nominal-e217.csv` | `forecasts-nominal-e217.csv` | byte-equal |
| FROZEN.txt 8 | `611ca08d27c81f09...` | `forecasts-nominal-e217.json` | `forecasts-nominal-e217.json` | byte-equal |
| FROZEN.txt 10 | `0a13366ace4d819e...` | `scripts/s02b_nominal.py` | `scripts/s02b_nominal.py` | byte-equal |
| FROZEN.txt 11 | `023231764a69015a...` | `scripts/s02w_walk.py` | `scripts/s02w_walk.py` | byte-equal |
| FROZEN.txt 12 | `c4a1273acd59590f...` | `scripts/s02c_write.py` | `scripts/s02c_write.py` | byte-equal |
| FROZEN.txt 13 | `2842d09e88cec63e...` | `work/step2/fc-nominal.json` | `inputs/step2/fc-nominal.json` | byte-equal |
| FROZEN.txt 14 | `6c65696dfe40bbdc...` | `work/step2/walk-feats-e217.json` | `inputs/step2/walk-feats-e217.json` | byte-equal |
| FROZEN.txt 15 | `111937947f50bfcd...` | `logs/step1-sha256.txt` | `logs/step1-sha256.txt` | byte-equal |
| FROZEN.txt 16 | `e45e688ec492cab2...` | `logs/step2-sha256.txt` | `logs/step2-sha256.txt` | byte-equal |
| COUNTS-FROZEN.txt 5 | `dc8fcfcb52607b4c...` | `cnt/work/counts/new-fp32-S1.json` | `counts-e217/raw/new-fp32-S1.json` | byte-equal |
| COUNTS-FROZEN.txt 6 | `1c7bea3ba0887980...` | `cnt/work/counts/new-fp32-S2.json` | `counts-e217/raw/new-fp32-S2.json` | byte-equal |
| COUNTS-FROZEN.txt 7 | `934eccaf6879a002...` | `cnt/work/counts/new-launch.json` | `counts-e217/raw/new-launch.json` | byte-equal |
| COUNTS-FROZEN.txt 9 | `0169d260348ae8b0...` | `cnt/counts/counts-fp32-gemm-states.json` | `counts-e217/counts-fp32-gemm-states.json` | byte-equal |
| COUNTS-FROZEN.txt 10 | `6509e20d4fe21c94...` | `cnt/counts/counts-fp16-int8-launch.json` | `counts-e217/counts-fp16-int8-launch.json` | byte-equal |
| COUNTS-FROZEN.txt 11 | `bc569673fa05893b...` | `cnt/counts/counts-e217.csv` | `counts-e217/counts-e217.csv`, `counts-e217/as-frozen/counts-e217.csv` | LF copy (22047ea6...): equal once CRLF -> LF; the frozen bytes byte-equal at `counts-e217/as-frozen/counts-e217.csv` |
| COUNTS-FROZEN.txt 12 | `133a8cd6841e0286...` | `cnt/counts/counts-e217-tiles.csv` | `counts-e217/counts-e217-tiles.csv`, `counts-e217/as-frozen/counts-e217-tiles.csv` | LF copy (1b34d499...): equal once CRLF -> LF; the frozen bytes byte-equal at `counts-e217/as-frozen/counts-e217-tiles.csv` |
| COUNTS-FROZEN.txt 14 | `305e23efa918fedb...` | `forecasts-nominal-e217-counts.csv` | `forecasts-nominal-e217-counts.csv` | byte-equal |
| COUNTS-FROZEN.txt 15 | `590c0be2ebb30bd0...` | `forecasts-nominal-e217-counts.json` | `forecasts-nominal-e217-counts.json` | byte-equal |
| COUNTS-FROZEN.txt 16 | `56309408f537c1b5...` | `scripts/s04c_nominal_counts.py` | `scripts/s04c_nominal_counts.py` | byte-equal |
| COUNTS-FROZEN.txt 17 | `32311daf2e0ace10...` | `FROZEN.txt` | `FROZEN.txt` | byte-equal |

So 20 of the 22 keep their bytes at their mapped place, and the other two keep them in `counts-e217/as-frozen/`. In decl-e217's lane folder all 22 still equal their listed sha256.

## verify-blind-e217's findings on this folder, answered

1. **The two count CSVs (low).** Here `counts-e217/counts-e217.csv` (sha256 `22047ea66765709e...`) and `counts-e217/counts-e217-tiles.csv` (`1b34d499dbea581c...`) have LF line ends. decl-e217's land step copied them as text, and Python's universal newlines dropped the carriage returns. COUNTS-FROZEN.txt names the bytes the counting step wrote, which have CRLF line ends (`bc569673fa05893b...`, `133a8cd6841e0286...`; 32 and 12 lines).
   - **The content is equal** once CRLF -> LF. Neither CSV is a model input: the models read the two JSON tables, which are byte-equal here.
   - **The README's sentence** "every file keeps its bytes" holds for every listed file but these two.
   - **The answer:** the frozen bytes, copied byte for byte from decl-e217's lane folder, are now `counts-e217/as-frozen/counts-e217.csv` and `counts-e217/as-frozen/counts-e217-tiles.csv`. The sha256 of each is COUNTS-FROZEN.txt's line. The LF copies stay as verified.
2. **The round's strict public-text scan (low).** The scan (`pubscan_strict.py`, sha256 `76ea74d9...`) finds 8 hits in this folder. Each was read, and each is a false positive:
   - **6 hits** (two e-mail-address patterns each, three files): the value of the git URL rewrite in `scripts/env.sh` line 7, `scripts/cnt/env.sh` line 10 and `scripts/s01b_models.py` line 35. It is an environment-only rewrite of GitHub's scp-style address prefix to its HTTPS one, not an address or a credential, and the same value is in 36 committed lab files.
   - **2 hits**: a common word for a folder's top level, which the scan's pattern for the administrator account also matches, in `logs/progress.txt` line 2 (the kit copy's top folder) and `scripts/s02c_write.py` line 3 (the lane's top folder).
   - **They stay as they are.** These are the verified bytes, and `scripts/s02c_write.py` is one of FROZEN.txt's supporting files (`c4a1273a...`). This note and the other new files add no hit of that scan.
3. **A confidentiality abbreviation (nit).** `logs/progress.txt` line 41 holds the three-letter abbreviation for a non-disclosure agreement, in the land step's own scan result ("no ...-type name"), which names no such name. It was read and left as is; the same word is in 177 committed lab files.
4. **`scripts/s05_land.py` does not reverse (nit).** `scripts/SCRUB-MAP.json` now lists all 42 landed scripts (`scripts/` and `scripts/cnt/`), with each one's sha256 as run and as landed. The checks:
   - 22 are byte-equal to the scripts as run, and 20 carry placeholders for the box's paths (`<W>`, `<LAB>`, `<CORE_ET>`, `<VERILATOR_BIN>`, `<SCRATCH>`, and `~` for the home folder).
   - decl-e217's own replacement table, applied to each script as run, gives its landed bytes: 42 of 42.
   - The table applied backwards gives the bytes as run for 41 of 42: 19 of the 20 with placeholders (the verifier wrote 18). The verifier's own test, each placeholder standing for one string, agrees (19 of 20).
   - **The exception is `scripts/s05_land.py`**, because it holds the table itself. Its literal placeholder strings stay as they are, and its scratch entry, a literal path, reads ('<SCRATCH>', '<SCRATCH>') once replaced, so putting the strings back cannot tell the two apart. Its landed bytes are the table applied to its bytes as run, as for the others.
   - The strings the placeholders stand for are the box's paths, so they are not written here.
5. **The measured conditions (info).** The primary footing reads each run's conditions "from the data's start-of-run records only" (`DECLARED-blind-e217.md` line 61; `README.md` line 79). Its field list (line 62) also names two window values of each run's primary view, `kclock_mhz` and `rails.minion.mV`, beside the start die.
   - So T3 equals T1 by construction, and card 0 is forecast at its in-run governed clock and volts.
   - The nominal footing, frozen here before any datum, is the prior check, and it fails more widely.
   - Nothing changes: it was declared.

## What the verifier did not check

- The freeze post's exact second (12:25:56 or 12:26:07 PST): either is at least 135 minutes before E217's first card command.
- The energy twin keys (used as frozen), the T2, E2, E3, E4 and watts band bases, the counts of the other 17 new rows, and 32 of the 125 walk configurations.

SPDX-License-Identifier: Apache-2.0
