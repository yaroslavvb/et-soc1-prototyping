# blind-e221: dated note 1, the folder as landed and verify-blind-e221's findings on it

*Fri 20 Nov 2026, Pacific time. Written by the lab's lane land-blind-e221 (round Q235) at 19:05 PST for this folder's commit, after verify-blind-e221 held it WITH FIXES (18:12-18:55 PST). Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), standard library only, single-threaded. This note changes no file of the folder and no number, forecast, rule or verdict; nothing in it is a measurement.*

## What is committed here

- **The folder** is decl-e221's land byte for byte: 39 files and `SHA256SUMS` (sha256 `a83c90fc58ed233e...`, 39 of 39 OK), written at 06:22:26 PST on Fri 20 Nov, after the declaration (06:15:39), the nominal forecasts (06:17:05) and FROZEN.txt (06:17:38), and before the freeze post and any E221 session.
- **The verification.** verify-blind-e221 re-derived the lab's blind score of E221 with its own code and checked this folder:
  - every sha256 in FROZEN.txt equals its file, here and in decl-e221's lane folder, and the declaration's 52 input sha256 re-hash 52 of 52;
  - its own caller re-made the nominal forecasts at the declared nominal conditions bit for bit: 116,784 fields (the four base models, 12,976 fields each, and the eight composed forms, 8,110 each);
  - its own run list from the committed data and the registered schedules equals `inputs/step1/runs-listed.json` in 17,842 of 17,842 fields (811 runs: 740 arm and 71 anchor; 733 cases);
  - the frozen makers' own functions re-made the features in `inputs/step2/` with 0 field differences: the contention term's walk at 142 of 142 configurations, posimb's private-share features (its landed `f02_private`) at 132 of 132, and L3S's shares at 63 of 63;
  - the twin keys in `inputs/step1/twin-keys.json` re-derive from each model's landed point records (twins, time / energy: MM1-v3.2 35/31, MM1-v3.1 17/15, MM1-v3 17/15, MM1-v2 8/8). The band bases B1 and every card's B2 re-derive for T1, E1, E3 and watts (one last digit aside: finding 5), and all 24 bands follow from `inputs/step1/bands.json` by the declared arithmetic;
  - its own driver over a fresh build of the RTL bench re-counted 5 points on E221's own kind tiles (the kit's 9 tiles are the lab's kinds byte for byte): three fp32 points equal to E210's committed raw points (123 of 123 numeric leaves each), and two int8 points equal to the committed counts-v2 points in 143 of 144 leaves. The other leaf, a count of trace identifiers, is 256 lower at both; it is not a switch-table input;
  - the folder holds new files only. Its fixes to this folder are the two below, both to land texts; none changes a number.
- **This note adds two new files**, and `SHA256SUMS-note1` with their sha256. It edits no file:
  - `README.md.dated-note-1.md`, this note;
  - `scripts/SCRUB-MAP.json`, each landed script's sha256 as run and as landed (finding 2).
- **The blind score** made exactly as this folder declares is the next commit's folder, `../blind-e221-scores/`.

## The freeze line, checked on this folder

Posted on the coordination Discussion as #15.2.1.1 (2026-11-20 06:22:58 PST in the round's record; 06:22:53.507 PST by the post's own time), before E221's first session. The nine sessions' first card commands came 06:32:57.848 to 15:51:19.767 PST, 9.997 to 568.363 minutes after the post (counted from the later time, 06:22:58, as blind-e221 and the verifier read it), each under a claim posted after it, so all nine are BLIND for this test:

- `FROZEN.txt` `2df06f06b7d4c16caca6ceb56cff8d6c47abcb6fec6e6671ce72c700378b299b`: the posted sha256, equal here.
- `DECLARED-blind-e221.md` `9cd8256bbc9a40b2850094bf936c02d2efd8fe65b886e95b92774dd1d5bc9f1b`: the posted sha256, equal here.
- `DECLARED-blind-e221.json` `b483f46cdcc0138d912e445a01fadb84a113cce0967f80e2b3f0ebe1f08c8ec4`: the posted sha256, equal here.
- `forecasts-nominal-e221.csv` `e3361847c4d1600b1b3deeaac3a42131b26f7bcb6434450bd8094c4965cbe59a`: the posted sha256, equal here.
- `forecasts-nominal-e221.json` `f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831`: the posted sha256, equal here.

FROZEN.txt names 13 files by sha256, under decl-e221's own folder names. The README's map gives each one's place here (`work/step2/` is `inputs/step2/`). Each was checked at that place:

| record, line | sha256 | listed as | here | check |
|---|---|---|---|---|
| FROZEN.txt 6 | `9cd8256bbc9a40b2...` | `DECLARED-blind-e221.md` | `DECLARED-blind-e221.md` | byte-equal |
| FROZEN.txt 7 | `b483f46cdcc0138d...` | `DECLARED-blind-e221.json` | `DECLARED-blind-e221.json` | byte-equal |
| FROZEN.txt 8 | `e3361847c4d1600b...` | `forecasts-nominal-e221.csv` | `forecasts-nominal-e221.csv` | byte-equal |
| FROZEN.txt 9 | `f787561175410898...` | `forecasts-nominal-e221.json` | `forecasts-nominal-e221.json` | byte-equal |
| FROZEN.txt 11 | `b43030186fe153b9...` | `scripts/s02b_nominal.py` | `scripts/s02b_nominal.py` | byte-equal |
| FROZEN.txt 12 | `0a8571ccfbcc8a9f...` | `scripts/s02w_walk.py` | `scripts/s02w_walk.py` | byte-equal |
| FROZEN.txt 13 | `342138469cba6ed5...` | `scripts/s02f_cands.py` | `scripts/s02f_cands.py` | byte-equal |
| FROZEN.txt 14 | `84bc47b8f7021c9e...` | `scripts/s02c_write.py` | `scripts/s02c_write.py` | byte-equal |
| FROZEN.txt 15 | `a80943cb770dc7f5...` | `work/step2/fc-nominal.json` | `inputs/step2/fc-nominal.json` | byte-equal |
| FROZEN.txt 16 | `b316da119b61c2ec...` | `work/step2/walk-feats-e221.json` | `inputs/step2/walk-feats-e221.json` | byte-equal |
| FROZEN.txt 17 | `848db0174a64edd8...` | `work/step2/cand-feats-e221.json` | `inputs/step2/cand-feats-e221.json` | byte-equal |
| FROZEN.txt 18 | `deb15fa9340303c3...` | `logs/step1-sha256.txt` | `logs/step1-sha256.txt` | byte-equal |
| FROZEN.txt 19 | `49e4de9a690e5a72...` | `logs/step2-sha256.txt` | `logs/step2-sha256.txt` | byte-equal |

So all 13 keep their bytes at their mapped place, and in decl-e221's lane folder all 13 still equal their listed sha256. The other inputs here (`inputs/step1/`, `inputs/recheck/recheck.json`) are byte-equal to decl-e221's lane files too. The README says the landed scripts' sha256 differ from the as-run hashes in FROZEN.txt and the step logs. That holds for 10 of the 19 scripts, and for none of the 4 that FROZEN.txt names or the 2 that `logs/step2-sha256.txt` names: those keep their bytes. The 7 lines of `logs/step1-sha256.txt` that name a script with placeholders tie to the bytes as run through `scripts/SCRUB-MAP.json` (finding 2).

## verify-blind-e221's findings on this folder, answered

1. **The round's strict public-text scan (low).** The scan (`pubscan_strict.py`, sha256 `76ea74d9...`) finds 14 hits in this folder. Each was read, and each is a false positive:
   - **8 hits** (two e-mail-address patterns each, four files): the value of the git URL rewrite in `scripts/env.sh` line 7, `scripts/s01b_models.py` line 33, `scripts/s05_land.py` line 27, `scripts/s06_result.py` line 15. It is an environment-only rewrite of GitHub's scp-style address prefix to its HTTPS one, not an address or a credential, and the same value is in 45 committed lab files at 1a259ddc.
   - **6 hits**: a common word for a folder's top level, which the scan's pattern for the administrator account also matches, in `logs/progress.txt` line 6, `scripts/s00b_setup_kit.sh` lines 4 and 21, `scripts/s01e_declare.py` line 2, `scripts/s02c_write.py` line 3, `scripts/s06_result.py` line 2 (the kit copy's top folder, or the lane's own).
   - **They stay as they are.** These are the verified bytes, and `scripts/s02c_write.py` is one of FROZEN.txt's supporting files (`84bc47b8...`). The verifier's other answer, placeholders and rewording in the landed scripts, would change verified bytes and `SHA256SUMS`, so the hits are recorded as read here instead, as decl-e219's note 1 did for its 14. This note and the other new file add no hit of that scan.
2. **`scripts/s05_land.py` does not reverse (nit).** `scripts/SCRUB-MAP.json` now lists all 19 landed scripts, with each one's sha256 as run and as landed. The checks:
   - 9 are byte-equal to the scripts as run, and 10 carry placeholders for the box's paths (`<W>`, `<LAB>`, `<SCRATCH>`, and `~` for the home folder).
   - decl-e221's own replacement table, applied to each script as run, gives its landed bytes: 19 of 19.
   - The table applied backwards gives the bytes as run for 18 of 19: 9 of the 10 with placeholders, as the verifier found.
   - **The exception is `scripts/s05_land.py`**, because it holds the table itself. Its literal placeholder strings stay as they are, its scratch entry, a literal path, reads ('<SCRATCH>', '<SCRATCH>') once replaced, and its own `~` stands for itself, so putting the strings back cannot tell them apart. Its landed bytes are the table applied to its bytes as run, as for the others.
   - `logs/step1-sha256.txt` names 7 scripts that carry placeholders here; the map's sha256 as run equals that log's line for all 7, so the log ties to the scripts as run through the map.
   - The strings the placeholders stand for are the box's paths, so they are not written here.
3. **The measured conditions (info).** The primary footing reads each run's conditions "from the data's start-of-run records only" (`DECLARED-blind-e221.md` line 69). Its field list (line 70) also names two window values of each run's primary view, `kclock_mhz` and `rails.minion.mV`, beside the start die. So T3 equals T1 by construction, as the declaration itself states (line 47). This is decl-e219's form too. Nothing changes: it was declared.
4. **The run selection (info).** The declaration names its form ("as unread-e214, decl-e217 and decl-e219 did", line 69) but does not write the run selection out. The scoring lane's readings R1-R2, hashed before its read, take decl-e219's explicit selection: the queue condition removed 0 runs, and 14 capped runs were not read for energy. The T1 misses are 24-26% of each card's cases against a 10% allowance, so no reasonable selection changes the verdict. Nothing changes.
5. **One band basis's last digit (info).** `inputs/step1/bands.json` gives aifoundry1 card 0's E1 basis B2 as 5.4169. Re-derived from MM1-v3.1's landed records it is 5.416798, which rounds to 5.4168 (verify-blind-e219 read 5.4168 for the same basis). B1 (5.4762) sets that card's E1 band, so the band, 11%, is unchanged.
6. **aifoundry2 card 0's weak floors (info).** decl-e221's own low finding: that card's ties and watts band rest on E212's 3 cases with two runs (the watts band 0.72 W; the ties 0.02 in ln joules and 0.4 W). They decided no rule: E221 has no watts case on that card (all 130 no-twin watts cases are on aifoundry1 card 1).
7. **S1's stopped first start (info).** Its preflight host-load reading (05:53:25 PST, aifoundry1 card 1) comes before the freeze post, in the box-cumulative preflight file of the six aifoundry1 data folders. It is not a card command, and the stopped start (05:53:56-05:55:27 PST, no run) is neither committed as a session nor scored. Nothing changes.
8. **The kit copy's record (info).** The orchestrator's record of its copy of E221's kit, outside the lab (FROZEN.txt names the copy's sums, `5680112f...`), dates the copy "Thu 19 Nov"; it was made at 05:54:33 PST on Fri 20 Nov, as decl-e221 itself found. Its "no claim file for aifoundry1" was true of the file then, though S1's claim had been posted at 05:53:45. E221's registration records both as its departure D1 (`tools/claims-v3/e221/E221.md`). The record's one-word fix is the orchestrator's; the copy checks 53 of 53, so nothing here changes.
9. **One maker's copy as run (info).** decl-e221's copy of the L3S maker's `energy_rep.py`, taken at 05:59, differs from the as-run hash in that maker's own rewrite list (the maker probably changed it after the copy). No forecast path uses it: the L3S term imports `costs` and `l3s_feature`, and both match. Nothing changes.
10. **The sealed forecast's digest (info).** The prefix `cab693ef` of the model session's sealed E221 forecast appears in `DECLARED-blind-e221.md` lines 5, 8 and 123 (line 8 quotes the proposal's record, with the full digest; the other two say the forecast was not read), in `DECLARED-blind-e221.json` (3 lines, the same three) and in `scripts/s01e_declare.py` and `scripts/s06_result.py`, where it is said not to be read. No forecast number appears anywhere here, and the full digest is already on main in E221's registration (`tools/claims-v3/e221/E221.md`).

## What the verifier did not check

- The freeze post's text on the Discussion itself (it read the round's record and the watcher's timestamp).
- The T2, E2 and E4 band bases: they need held-out predictions that are not in the landed files. Their arithmetic from `inputs/step1/bands.json` is checked.
- fp16 counts, and whether any lane read the model session's sealed forecast (only its digest appears, in the lines above).
- **NOT RUN:** the four maker checks on the makers' own E215 and E220 rows. The verifier's composed forecasts equal the frozen nominal ones here, which the makers as run made, and that covers E221.

SPDX-License-Identifier: Apache-2.0
