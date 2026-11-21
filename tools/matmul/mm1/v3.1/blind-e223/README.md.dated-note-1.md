# blind-e223: dated note 1, the folder as landed and verify-blind-e223's findings on it

*Sat 21 Nov 2026, Pacific time. Written by the lab's lane land-blind-e223 (round Q239) at 08:44 PST for this folder's first commit, after verify-blind-e223 held the lab's blind test of E223 WITH FIXES (07:55-08:31 PST). Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), standard library only, single-threaded. This note changes no file of the folder and no number, forecast, rule or verdict; nothing in it is a measurement.*

## What is committed here

- **The folder** is decl-e223's land byte for byte: 40 files and `SHA256SUMS` (sha256 `ae3faecee1160d96...`, 40 of 40 OK). They were written at 02:27:46 PST on Sat 21 Nov, after the declaration (hashed 02:19:31), the nominal forecasts (made 02:19:40-02:21:38) and FROZEN.txt (02:22:09), and before any E223 session.
- **The verification.** verify-blind-e223 re-derived the lab's blind score of E223 with its own caller and its own scorer, and checked this folder:
  - FROZEN.txt equals its posted line, its 7 file lines re-hash 7 of 7, every listed file was written before the post, and the declaration's inputs re-hash 64 of 64;
  - the work copy the nominal forecasts were made from equals GitHub main blob for blob, 3,177 of 3,177 files;
  - its own run list, from E223's registration on main and the declaration's stated rules, holds 803 runs and 695 cases, equal to `inputs/step1/runs-listed.json` in 17,666 of 17,666 run fields and 3,475 of 3,475 case fields;
  - its own caller re-made the nominal forecasts bit for bit: 82,705 of 82,705 fields equal to `forecasts-nominal-e223.json` and to amendment 1's forecasts (695 cases). The terms' scopes at the nominal footing are as declared: posimb 513, L3S 182, posimb-mask 513;
  - the twin keys re-derived from each model's landed point records equal `inputs/step1/twin-keys.json` (and the amendment's), and the nominal-clock twin previews are as declared; no E223 point is in any model's fit record;
  - the bands and ties equal the declaration's text and `inputs/step1/bands.json`, which equals decl-e221's file but for its 'what' line;
  - the folder holds new files only: no path at GitHub main, and no commit on any ref ever touched one. Its fixes to this folder are the two below, both to land texts; none changes a number.
- **This note adds two new files**, and `SHA256SUMS-note1` with their sha256. It edits no file:
  - `README.md.dated-note-1.md`, this note;
  - `scripts/SCRUB-MAP.json`, each landed script's sha256 as run and as landed (finding 3).
- **Dated amendment 1** (`DECLARED-blind-e223-amendment-1.*`, `FROZEN-amend1.txt`, its nominal forecasts and `scripts/amend1/`) follows in this same folder as the next commit, with its own `README.md.dated-note-2.md`. The blind score made exactly as the declaration and the amendment declare is the commit after, `../blind-e223-scores/`.

## The freeze line, checked on this folder

Posted on the coordination Discussion as #16.1.1.1 (2026-11-21 02:23:46 PST in the round's record; 02:23:46.349 PST by the post's own stamp), before E223's first session. Amendment 1 followed as #16.1.1.1.1 at 02:40:33 PST. E223's three aifoundry2 card 0 sessions sent their first card commands at 02:50:39.312, 03:30:38.649 and 04:08:32.022 PST. That is 26.883, 66.872 and 104.761 minutes after this post, each under a claim posted after both freeze posts, so all three are BLIND for this test. aifoundry1's six sessions had not run when it was scored.

- `FROZEN.txt` `5551c2d7b7b6b5bc40526997a2d8bcbfe62fc8b1468da514781fa59d7543b850`: the posted sha256, equal here.
- The post names the four frozen files by their first 8 hex digits, and FROZEN.txt gives each in full. Both agree with the file here:
  - `DECLARED-blind-e223.md` `f2795ec352ca6244e8af2167b5b9742e1c2dad7fa6e844eb6035957b8398b3c7`;
  - `DECLARED-blind-e223.json` `c74dc54746780a8d9a952e871a81510913b5e33c6934bdf6a23ee5124ee76e02`;
  - `forecasts-nominal-e223.csv` `dc47385df5af5db0bf6ba4dcdc49f453506f8df88eb07ee488e3527d3bd32082`;
  - `forecasts-nominal-e223.json` `aeb174a7ea93a73b0baeac3d404fe57013694118dfb39e2963fe1fc388aa424f`.

FROZEN.txt names 7 files by sha256, under decl-e223's own folder names. The README's map gives each one's place here (`work/step2/` is `inputs/step2/`). Each was checked at that place:

| FROZEN.txt line | sha256 | listed as | here | check |
|---|---|---|---|---|
| 3 | `f2795ec352ca6244...` | `DECLARED-blind-e223.md` | `DECLARED-blind-e223.md` | byte-equal |
| 4 | `c74dc54746780a8d...` | `DECLARED-blind-e223.json` | `DECLARED-blind-e223.json` | byte-equal |
| 5 | `dc47385df5af5db0...` | `forecasts-nominal-e223.csv` | `forecasts-nominal-e223.csv` | byte-equal |
| 6 | `aeb174a7ea93a73b...` | `forecasts-nominal-e223.json` | `forecasts-nominal-e223.json` | byte-equal |
| 8 | `ab0ae70cbd41d40e...` | `logs/step1-sha256.txt` | `logs/step1-sha256.txt` | byte-equal |
| 9 | `b11a802475ae85c1...` | `logs/step2-sha256.txt` | `logs/step2-sha256.txt` | byte-equal |
| 10 | `ce01e77fec05f13c...` | `work/step2/fc-nominal.json` | `inputs/step2/fc-nominal.json` | byte-equal |

- **All 7 keep their bytes** at their mapped place, and in decl-e223's lane folder all 7 still equal their listed sha256.
- **FROZEN.txt's line 12 names two other lanes' freeze records** by sha256: mask-mesh's `487188c7...` and mask-ceiling's `1649ba5b...`. The declaration left both candidates out, and amendment 1 adds them. Neither record is a file of this folder. Both are on main: `tools/matmul/mm1/v3.4-cands/mesh/FROZEN.txt` and `tools/matmul/mm1/v3.4-cands/mask-ceiling/FROZEN.txt.superseded-022113`.
- **The other inputs here are byte-equal to decl-e223's lane files**, 12 of 12: `inputs/step1/`, `inputs/recheck/recheck.json`, the Q238 posts as read, the posimb-mask FROZEN.txt, the kit copy's `SRC-SHA256SUMS.txt` and the lab commit.
- **The README says the landed scripts' sha256 differ from the as-run hashes** in the step logs. That holds for 9 of the 16 scripts.
  - `logs/step1-sha256.txt` names 24 files. 13 keep their bytes at their place here.
  - 4 work files are here under `inputs/` names, byte-equal. `work/lab-commit.txt`, `work/mask-posimb-FROZEN.txt` and `work/q238-frozen-posts-at-declaration.txt` keep their names under `inputs/`, and `work/e223-src/SRC-SHA256SUMS.txt` is `inputs/e223-src-SRC-SHA256SUMS.txt`.
  - The other 7 are scripts that carry placeholders here. They tie to their bytes as run through `scripts/SCRUB-MAP.json` (finding 3).
  - `logs/step2-sha256.txt` names 5 files, and all 5 keep their bytes here. Among them is the declared caller, `scripts/s02b_nominal.py` (`266eb6db...`).
- **`logs/progress.txt` is the first 32 of the 34 lines** in decl-e223's lane log now. The two later lines (the land and its check) were written after the land was made.

## verify-blind-e223's findings on this folder, answered

1. **The round's strict public-text scan (finding 2, low).** The scan (`pubscan_strict.py`, sha256 `76ea74d9...`) finds 14 hits in this folder. Each was read, and each is a false positive:
   - **6 hits** (two e-mail-address patterns each, three files): the value of the git URL rewrite in `scripts/env.sh` line 7, `scripts/s01b_models.py` line 33 and `scripts/s05_land.py` line 26. It is an environment-only rewrite of GitHub's scp-style address prefix to its HTTPS one, not an address or a credential. The same value is in 52 committed lab files under `tools/` at a517aa7d.
   - **8 hits**: a common word for a folder's top level (said of the repository, the kit and the lane folder), which the scan's pattern for the administrator account also matches. They are in `README.md` lines 11 and 12, `logs/progress.txt` lines 2 and 3, `scripts/s00b_setup_kit.sh` lines 4 and 21, `scripts/s01e_declare.py` line 2 and `scripts/s02c_write.py` line 3.
   - **The quotes in the frozen declaration** are beside these hits. `DECLARED-blind-e223.md` lines 5, 8, 9 and 141, and the same four lines in `DECLARED-blind-e223.json` (17208, 17210, 17211, 17933), quote E223's proposal and push posts and say the seal was not read. They hold the model session's kit folder by its home-relative name, the prefix `eb5478f6` of its sealed forecast's digest, and the model session's own two-word name for its box. `scripts/s00b_setup_kit.sh` line 3 names the same folder in a comment, and `scripts/s01e_declare.py` lines 124 and 349 name the prefix, saying it is not read.
     - All three are already public in E223's registration on main (`tools/claims-v3/e223/E223.md`: the folder on 4 lines, `eb5478f6` on 2, the box's name on 4).
     - No number of the sealed forecast appears anywhere here.
   - **They stay as they are.** These are the verified bytes. The declaration is frozen and posted, and `scripts/s01e_declare.py` and `scripts/s02c_write.py` are named by `logs/step1-sha256.txt`, a file FROZEN.txt names. Rewording would change verified bytes and `SHA256SUMS`, so the hits are recorded as read here instead, as decl-e219's and decl-e221's notes 1 did. This note and the other new file add no hit of that scan.
2. **No scrub map (finding 3, nit).** `scripts/SCRUB-MAP.json` now lists all 16 landed scripts, with each one's sha256 as run and as landed. The checks:
   - 7 are byte-equal to the scripts as run, and 9 carry placeholders for the box's paths (`<W>`, `<LAB>`, `<SCRATCH>`; the table's `~` for the home folder replaced nothing in any script).
   - decl-e223's own replacement table, applied to each script as run, gives its landed bytes: 16 of 16.
   - The table applied backwards gives the bytes as run for 14 of 16: 7 of the 9 with placeholders, as the verifier found.
   - **`scripts/s05_land.py` does not reverse**, because it holds the table itself. Its literal placeholder strings stay as they are, its scratch entry, a literal path, reads ('<SCRATCH>', '<SCRATCH>') once replaced, and its own `~` stands for itself. So putting the strings back cannot tell them apart.
   - **`scripts/s00b_setup_kit.sh` does not reverse** either. As run, it holds one literal `~` (line 3, the comment that names the kit's home-relative folder), and the table applied backwards would turn it into the home folder. The verifier's regex test, in which `~` is not a placeholder, passes for it.
   - For both, the landed bytes are the table applied to the bytes as run, as for the others.
   - `logs/step1-sha256.txt` names 7 scripts that carry placeholders here. The map's sha256 as run equals that log's line for all 7, so the log ties to the scripts as run through the map.
   - The strings the placeholders stand for are the box's paths, so they are not written here.
3. **MM1-v2's volts (finding 4, low; it confirms blind-e223's reading R9).** The declaration's text gives MM1-v2 the governed card's measured minion volts, while its frozen caller, `scripts/s02b_nominal.py`, passes `V_mv` None. The verifier made both columns, and both are bit-equal to blind-e223's. They differ in energy only (E1 5.03% as the text reads and 4.99% as coded, on aifoundry2 card 0's no-twin cases), and MM1-v2 decides nothing. Nothing changes here; a later declaration should state its caller's volts in code.
4. **The NO DATA reading (finding 5, info).** The declaration's NO DATA ("no untied case", its own reading at D0) and blind-e221's ("no case compared") label 1,232 REPORTED cells differently. In every one of them, every case ties: D0 by construction, the reference's H2, and small per-set blocks. No D1 or D2 verdict changes, per card or pooled.
5. **The measured conditions (finding 7, info).** The primary footing's conditions include two window values of each run's primary view (`kclock_mhz`, `rails.minion.mV`), which the declaration names itself. So T3 equals T1 by construction (170/218 for both on aifoundry2 card 0), as on E221. Nothing changes: it was declared.

## What the verifier did not check

- The Discussion posts' own text. It read the round's records and the watcher's stamps.
- The band bases. `inputs/step1/bands.json` equals decl-e221's, whose bases verify-blind-e221 re-derived for T1, E1, E3 and watts; the arithmetic from the file is checked.
- MM1-v3.1's loader run on E223's bytes. Its own run selection equals the scoring lane's, run by run.
- **NOT RUN:** the maker checks A and B, which blind-e223 re-ran (the verifier's caller re-makes the frozen nominal forecasts bit for bit); any reading of the model session's sealed forecast; switch counts (E223 designs no tile).

SPDX-License-Identifier: Apache-2.0
