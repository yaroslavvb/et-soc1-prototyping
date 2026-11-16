# E198 sitting B's data README, dated note 1 (Mon 16 Nov 2026): step 13's outputs on the data commit `ce94a428` and THE TRANSPORT SCORER's on both sittings, with their printed lines, committed beside the data; E198-T1 FAIL (decided 36, hold 28, miss 8) and E198-T2 PASS (decided 36, hold 35, miss 1); the measured, reduced prices beside aifoundry3's; the data verifier's re-derivation agrees; no reading of README.md changes

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `ce94a428`. Written on aifoundry2 on Mon 16 Nov 2026 from 09:49 PST by the clock (this text generated at 10:07:20 PST from the files it cites), desk only (no card, no lab box, no device, no post), by round Q196's lane `reduce-e198`, after E198's data verifier `verify-e198d` (09:24-09:50 PST: HOLDS; one nit, one post hoc reading, two notes, the card lane's own incident and one open item, each answered in section 7). README.md hands these outputs to a later lane (its lines 28-30: "their outputs (`x04-e198-B.json`, `checks-e198-B.json`) and the transport scorer's are committed by a later lane"; its item "The scores" under "What E198's README adds to E193's form"), as does step 13's script ([`rb/s24_reduce_e198.sh`](../../../../tools/claims-v3/e198/rb/s24_reduce_e198.sh), its header: "the records lane commits them beside the data in a later commit"). This lane is that later lane. **No number, price, check, verdict or gate reading of README.md changes.** **The sealed forecast stays sealed:** E198.md's freeze line 2 (the model session's card-1 forecast) is named there by its sha256 only; no number of it is here and nothing here scores against it. Forecast 1, the lab's (`forecast-e198.json`, sha256 524f49ad..., E193's committed aifoundry3 prices), is public, and E198.md 5 scores card 1 against it: its prices stand beside card 1's below. Interpreter: `/usr/bin/python3` 3.12.3 with the system's numpy 1.26.4, on aifoundry2. Labels: **registered** (E198.md, A1 and the kit as committed), **measured** (the session's committed records, and the registered reducer's prices from them), **desk check of code** (this lane's re-run and comparisons), **desk arithmetic** (this lane's arithmetic on the committed outputs), **REPORTED** (E198.md 7's readings, and the data verifier's figures, read and not re-run here), **post hoc** (read after the data; it decides nothing).*

## 1. The new files

| file | what | lines | bytes | sha256 |
|---|---|---|---|---|
| [`x04-e198-B.json`](x04-e198-B.json) | the registered reducer's output ([`reduce_x04.py`](../../../../tools/claims-v3/e193/proposal/src/reduce_x04.py), sha256 98bbc174..., run unchanged by step 13; E198.md 19's `x04-e198-B.json`), byte for byte from the card lane's runbook folder: 14 arms (block C has no train), their watts over idle on the board and the rails, the fits and the reducer's own check fields | 7,107 | 176,260 | `8421a0ab...` |
| [`checks-e198-B.json`](checks-e198-B.json) | the kit's checker's output ([`check_e193.py`](../../../../tools/claims-v3/e193/check_e193.py) `checks`, sha256 1351df2d...): E193.md 8's nine checks on card 1 (E198.md 7: REPORTED), byte for byte | 89 | 1,891 | `25144f1f...` |
| [`x04-e198-B.txt`](x04-e198-B.txt) | the reducer's printed lines: step 13's copy of the runbook's capture of that call (stdout and stderr as they came), byte for byte | 18 | 1,128 | `67b02c76...` |
| [`checks-e198-B.txt`](checks-e198-B.txt) | the checker's printed lines, copied byte for byte from the runbook's capture of that call | 11 | 391 | `c63ee5ba...` |
| [`scores-e198.json`](scores-e198.json) | THE TRANSPORT SCORER's output ([`score_e198.py`](../../../../tools/claims-v3/e198/score_e198.py) `score`, sha256 1d2b211e..., unchanged, its forecast pinned at 524f49ad...) on both sittings' reductions: the 36 scored prices, the two rules' counts and words, the per-sitting REPORTED words and E198.md 7's REPORTED readings. **Not byte for byte the card lane's copy: section 8** (its two path fields name the repo paths) | 1,872 | 39,450 | `9cc4e039...` |
| [`scores-e198.txt`](scores-e198.txt) | the scorer's printed lines, byte for byte the card lane's copy of the runbook's capture of that call | 45 | 4,565 | `973ada2a...` |
| `README.md.dated-note-1.md` | this note | | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these 7 files, `README.md` and `SHA256SUMS`; `SHA256SUMS` pins the 57 collected files, so every file here is pinned but `SHA256SUMS-note1` itself. The scorer's files are here because the scorer reads both sittings and ran after this sitting's data commit; sitting A's note 1 points here.

## 2. When, where and on which commit step 13 ran

From the card lane's runbook log (`runbook.log`) and its capture of each call, kept outside the repository in its runbook folder for this sitting, and from the lab clone's own log of its HEAD:

- **Step 13** ([`rb/s24_reduce_e198.sh`](../../../../tools/claims-v3/e198/rb/s24_reduce_e198.sh) `B`, the kit's, `aacf2d4a...` in `SHA256SUMS-e198-kit`): Mon 16 Nov 2026, **09:20:00-09:20:01 PST**, on aifoundry2, in the lab clone with its HEAD at **`ce94a428`**, this sitting's data commit (git 09:19:44 PST; pushed by 09:19:48 PST, when the remote's main read `ce94a428`), which stayed the clone's HEAD until E200's sitting-2 data commit, `ca53ed29`, came at 10:06:26 PST.
- **Its gates**, the log's lines 80-84, each rc 0: the data directory committed (the call names `ce94a428` as the last commit touching it); the directory clean (no line); its `SHA256SUMS`, every entry (57 of 57 OK); the history check ("HISTORY OK"); the reducer at its registered sha256 (`98bbc174...`). The step then copied `x04/runs.jsonl` and unpacked `x04/telemetry.jsonl.gz` into its folder and checked both against `session/MANIFEST.sha256` (the box's bytes).
- **The reducer**, line 85: `/usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py RB_OUT/e198-reduce-B/x04 --out RB_OUT/x04-e198-B.json`, rc 0 in 0.5 s (the runbook writes each line at the call's end). `x04-e198-B.json` was last written at 09:20:01.337, the capture of its printed lines at 09:20:01.362, and the step's copy, `x04-e198-B.txt`, at 09:20:01.387.
- **The checker**, line 86: `/usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks RB_OUT/x04-e198-B.json RB_OUT/e198-reduce-B/x04 --out RB_OUT/checks-e198-B.json`, rc 0 in 0.4 s; `checks-e198-B.json` was last written at 09:20:01.818, its capture at 09:20:01.818. Line 86 is the log's last line (86 lines): nothing ran through the runbook in that folder after the checker.
- **The scorer** (`rb/s24_reduce_e198.sh score`, its own runbook folder, 2 lines, both rc 0): at 09:20:12 PST the scorer at its registered sha256 (`1d2b211e...`), then `/usr/bin/python3 -I -B tools/claims-v3/e198/score_e198.py score --a RB_OUT/x04-e198-A.json --b RB_OUT/x04-e198-B.json --out RB_OUT/scores-e198.json`, rc 0 in 0.0 s, with the clone's HEAD at `ce94a428`. The scores file records each reduction's sha256, and both equal the two step-13 reductions (`dc0ef689...`, `8421a0ab...`); it was last written at 09:20:12.156, the capture of its printed lines at 09:20:12.156, the step's copy `scores-e198.txt` at 09:20:12.164.
- **The inputs:** the copied `x04/runs.jsonl` (1,350 lines) and the unpacked telemetry are byte-equal to the files committed in `ce94a428` and to the box's manifest's entries. **The code:** `tools/claims-v3/e193` is tree `431bee42` and `tools/claims-v3/e198` tree `3c5c225e` at A1 (`9e59ca0d`), at both data commits, at E200's `548d736e` between them, and at `4a59c4ec`, the lab clone's HEAD when this note was written; no commit touched either after A1. **The card lane's log of step 13** holds, between its header and its rc line ("rc 0"), the captures and the step's two lines, byte for byte.

## 3. A desk check of code: this lane's re-run

At 09:57:25-28 PST, from this lane's fresh extract of `ce94a428`'s own tree (made from the lab clone's objects; no clone, no checkout), in the round's CPU slot, under the no-device wrapper (a private /dev with no card node) and a 4 GB cap: the inputs built as step 13 builds them and checked against the box's manifest (2 of 2); the reducer rc 0 and the checker rc 0. **`x04-e198-B.json`, `checks-e198-B.json` and both printed-line files came out byte-equal** to the card lane's files and to the runbook's captures. The scorer, re-run on the two re-run reductions (byte-equal to the committed ones) from a copy of the tree's top with the repo paths given, printed lines byte-equal to `scores-e198.txt` and to its capture, and wrote the committed `scores-e198.json` (section 8).

## 4. The measured, reduced prices beside aifoundry3's (sitting B)

Card 1's columns are the registered reducer's on this directory (measured: board W over idle, mean +- SE over the measured passes 1-8; n the reducer's n, which for the anchor `spin2` counts its runs, 2 a pass). aifoundry3's are E198.md 4's forecast 1 (E193's committed prices, `forecast-e198.json`). h = 1.96 x sqrt(se1^2 + se3^2); T1 holds when abs(v1 - v3) <= h (the column shows abs(v1 - v3) - h: zero or below holds); T2 holds when v1 lies in [min(0.952 v3, 1.144 v3) - h, max(0.952 v3, 1.144 v3) + h] (E198.md 5). The ratio is printed where abs(v3) >= 0.5 W (E198.md 7). The T1 and T2 words are the scorer's (`scores-e198.json`); the margin column is desk arithmetic on its numbers.

| price | kind | card 1, W +- SE (n) | aifoundry3, W +- SE (n) | card 1 / aifoundry3 | h, W | abs(v1 - v3) - h, W | T1 | T2 |
|---|---|---|---|---|---|---|---|---|
| `faddps_p1` | arm | 8.5694 +- 0.0172 (8) | 8.7854 +- 0.0234 (8) | 0.975 | 0.0569 | +0.1591 | **miss** | hold |
| `faddps_p16` | arm | 2.3721 +- 0.0391 (8) | 2.4011 +- 0.0333 (8) | 0.988 | 0.1006 | -0.0717 | hold | hold |
| `faddps_p2` | arm | 6.0557 +- 0.0399 (8) | 6.2005 +- 0.0316 (8) | 0.977 | 0.0999 | +0.0449 | **miss** | hold |
| `faddps_p4` | arm | 4.2240 +- 0.0432 (8) | 4.2608 +- 0.0381 (8) | 0.991 | 0.1129 | -0.0761 | hold | hold |
| `faddps_p8` | arm | 2.9496 +- 0.0551 (8) | 3.0812 +- 0.0379 (8) | 0.957 | 0.1310 | +0.0007 | **miss** | hold |
| `faddpsm1_p1` | arm | 8.2562 +- 0.0228 (8) | 8.4548 +- 0.0233 (8) | 0.977 | 0.0639 | +0.1347 | **miss** | hold |
| `faddpsm2_p1` | arm | 8.2902 +- 0.0198 (8) | 8.5083 +- 0.0187 (8) | 0.974 | 0.0533 | +0.1647 | **miss** | hold |
| `faddpsm4_p1` | arm | 8.3801 +- 0.0161 (8) | 8.5716 +- 0.0337 (8) | 0.978 | 0.0731 | +0.1184 | **miss** | hold |
| `fadds_p16` | arm | 2.3987 +- 0.0337 (8) | 2.3717 +- 0.0312 (8) | 1.011 | 0.0901 | -0.0631 | hold | hold |
| `fsgnjs_p1` | arm | 4.5223 +- 0.0564 (8) | 4.6253 +- 0.0341 (8) | 0.978 | 0.1292 | -0.0262 | hold | hold |
| `fsgnjs_p2` | arm | 3.7292 +- 0.0410 (8) | 3.6958 +- 0.0351 (8) | 1.009 | 0.1058 | -0.0724 | hold | hold |
| `fsgnjs_p4` | arm | 2.8604 +- 0.0415 (8) | 2.9023 +- 0.0261 (8) | 0.986 | 0.0961 | -0.0541 | hold | hold |
| `fsgnjs_p8` | arm | 2.3010 +- 0.0244 (8) | 2.3117 +- 0.0159 (8) | 0.995 | 0.0571 | -0.0464 | hold | hold |
| `spin2` | arm | 2.4515 +- 0.0288 (16) | 2.5176 +- 0.0233 (16) | 0.974 | 0.0726 | -0.0064 | hold | hold |

Sitting B's T1 misses: `faddps_p8` (by 0.0007 W), `faddps_p2` (by 0.0449 W), `faddpsm4_p1` (by 0.1184 W), `faddpsm1_p1` (by 0.1347 W), `faddps_p1` (by 0.1591 W), `faddpsm2_p1` (by 0.1647 W). T2 misses: none.

**REPORTED, beside them (E198.md 7):**

- **The minion rail** (the same reducer's minion-rail prices under T1's and T2's arithmetic; not scored, E198.md 4): sitting B's 14 prices, T1 arithmetic holds on 12, T2 on 14; over both sittings T1 PASS (hold 30 of 36) and T2 PASS (hold 36 of 36).
- **The anchors** (card 1 / aifoundry3): `faddps_p1` 0.9754; `fsgnjs_p1` 0.9777; `spin2` 0.9737; the minion rail's volts, card 1's mean 0.499 V over aifoundry3's 0.523 V, squared: 0.9103. E198.md 6 set the catalogue's 0.943 (the two-hart no-op), 0.999 (`fadd.ps`) and 0.996 (`fsgnj.s`) beside them.
- **The fits** (the reducer's unweighted lines; each SE from that card's own points; linear in the scored prices, so not scored):

| fit, term | unit | card 1 | aifoundry3 | h | T1 arithmetic | T2 arithmetic |
|---|---|---|---|---|---|---|
| `ladder_faddps`, slope | pJ an op (the slope x 10^12; x is ops a second) | 15.9 | 16.31 | 0.2587 | misses | holds |
| `ladder_faddps`, intercept | W | 2.3 | 2.346 | 0.07449 | holds | holds |
| `ladder_fsgnjs`, slope | pJ an op (the slope x 10^12; x is ops a second) | 5.959 | 6.178 | 0.4027 | holds | holds |
| `ladder_fsgnjs`, intercept | W | 2.203 | 2.191 | 0.07344 | holds | holds |
| `mask_lanes`, slope | W a lane | 0.0453 | 0.04664 | 0.01091 | holds | holds |
| `mask_lanes`, intercept | W | 8.204 | 8.405 | 0.05211 | misses | holds |

- **E193's nine checks on card 1** (`check_e193.py checks`, the kit's checker, unchanged): `CHECKS READ: 1 PASS, 2 PASS, 2 FAIL, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 NOT COMPUTED, 7 REPORTED, 8 REPORTED, 9 NOT COMPUTED`, the same words E193 read on aifoundry3 for its sitting B: `checks-e198-B.txt` is byte for byte E193's committed `checks-e193-B.txt` (desk check: the two files compared byte for byte; the checker prints the words only, its numbers are in the JSON). Checks 1 and 2 compare card 1's arms with aifoundry3's catalogue rows scaled by 992/1024, as registered, and are read so.

## 5. The rules' words as committed (both sittings; `scores-e198.json` in sitting B's directory)

- **E198-T1, the prices as measured: FAIL (decided 36 of 36, hold 28, miss 8).** E198.md 5: FAIL if 8 or more decided prices miss.
- **E198-T2, the prices up to a card-to-card scale in [0.952, 1.144]: PASS (decided 36 of 36, hold 35, miss 1).**
- **Per sitting (REPORTED, never a verdict of the day):** sitting A T1 PASS (decided 22 of 22, hold 20, miss 2), T2 PASS (decided 22 of 22, hold 21, miss 1); sitting B T1 FAIL (decided 14 of 14, hold 8, miss 6), T2 PASS (decided 14 of 14, hold 14, miss 0).
- **The pair, read as E198.md 1 says:** FAIL and PASS: E193's prices transport to card 1 only up to a card scale inside the band, not as measured. The scorer's last line: `VERDICTS: E198-T1 FAIL, E198-T2 PASS`.
- **The misses:** T1 `A/train/tr_faddps_fadds`, `A/train/tr_tk_stall2`, `B/arm/faddps_p1`, `B/arm/faddps_p2`, `B/arm/faddps_p8`, `B/arm/faddpsm1_p1`, `B/arm/faddpsm2_p1`, `B/arm/faddpsm4_p1`; T2 `A/train/tr_faddps_fadds`.
- **REPORTED, how far apart the cards are (E198.md 7.1):** the fitted scale 0.9785 +- 0.0016 (weighted least squares through the origin over the 36 decided board prices); 32 of them within h of it; card 1 / aifoundry3 over the 26 prices with abs(v3) >= 0.5 W: median 0.9896, least 0.9330, greatest 1.0444. Fitted on card 1's data, so never a rule.

## 6. The data verifier's re-derivation beside them (REPORTED; its figures read, not re-run here)

`verify-e198d` (09:24-09:50 PST, verdict HOLDS) re-derived the day with its own code under `/usr/bin/python3` 3.12.3: it imports nothing from the kit's runner, reducer or scorer and uses no numpy, and reads the committed raw files with the forecast as frozen at `62b102fe`. Its words: E198-T1 FAIL (decided 36, hold 28, miss 8), E198-T2 PASS (decided 36, hold 35, miss 1), the per-sitting words the same as the scorer's; the fitted scale 0.97854 +- 0.00163, 32 within h, median ratio 0.98965; E193's checks 1-8 on card 1 the same words (check 9 not run by it). Its own comparison: the largest difference per run, watts over idle, 1.8e-14 W; per price 6.2e-15 W; per SE 1.7e-15 W; 0 mismatches in n, decided and the T1/T2 words; the 7 fits' 14 judgments equal.

**This lane's comparison of its file with the committed scores (desk check of code):** over the 36 prices, the largest abs difference in v1 is 6.2e-15 W, in se1 1.7e-15 W and in h 3.2e-15 W; the decided, T1 and T2 words differ on 0 prices and n on 0; the 36 minion-rail prices differ by at most 9.3e-15 W with 0 word differences; the 14 fit judgments differ on 0.

## 7. The data verifier's findings, answered (dated clauses, Mon 16 Nov 2026, this lane)

1. **Nit (kit text):** `rb/s22_collect_e198a1.sh` line 93 still prints "write its README in the lab's form (DATA-README-FORM-e198.md)", the form A1 retires. *Answered:* the committed README follows `DATA-README-FORM-e198-a1.md` (its header names E198's own two freeze lines and no E193 forecast hash); the printed wording is the kit's, for a later kit note; nothing in this directory changes.
2. **Post hoc: E198-T1's FAIL sits exactly at its registered threshold of 8 misses.** *Answered, desk arithmetic of the committed scores (post hoc; it decides nothing):* the 8 T1 misses by abs(v1 - v3) - h, smallest first: `faddps_p8` 0.00067 W (0.5% of its h); `tr_tk_stall2` 0.00199 W (5.7% of its h); `tr_faddps_fadds` 0.01813 W (15.2% of its h); `faddps_p2` 0.04493 W (45.0% of its h); `faddpsm4_p1` 0.11838 W (161.9% of its h); `faddpsm1_p1` 0.13473 W (210.9% of its h); `faddps_p1` 0.15914 W (279.6% of its h); `faddpsm2_p1` 0.16474 W (308.9% of its h). The two nearest, `faddps_p8` and `tr_tk_stall2`, miss by less than 0.0025 W; with one fewer miss T1 would read PASS (29 of 36 = 80.6% hold, at least 80% needed). **The registered rule decides: E198-T1 FAIL stands.** It does not rest on rounding: the verifier's independent figures agree with the scorer's to about 1e-14 W (section 6). E198.md 14 said before the data that 1.96 is the normal quantile, not Student's (about 2.14 for the combined degrees of freedom), that under identical cards T1 is expected to hold on about 34 of 36, not 36, and that one session's prices are correlated, so misses may cluster: 6 of the eight are sitting B's `fadd.ps` arms, on which card 1 reads 2.2-4.3% lower than aifoundry3. T2's one miss, `tr_faddps_fadds`, lies 0.0161 W outside its band.
3. **Note: the die peaked at 55 C** in both sittings against E198.md 9's predicted 53 C. *Answered:* README.md already says so (lines 69-70 and 143): the prediction assumed a 50 C idle, the card idled at 52 C, the rise was the predicted 3 C, and the peak stayed 15 C under the 70 C stop. A prediction, not a stop or a rule; nothing changes.
4. **Note: card-minutes counted from step 7's config read** (a READ of card 1 about 30 s before the first card command) instead of the holder check. *Answered, desk arithmetic of README.md's times:* sitting A 43.87 against README.md's 43.30 (cap 60); sitting B 27.95 against 27.42 (cap 50); sitting B's rest from sitting A's end to its step 7 read 40.32 minutes (at least 40). All inside the caps and the rest. README.md counts from the first card command, as E193's form and the kit do; its figures stand.
5. **Incident (the card lane's own, self-reported):** one read-only step-10 wait of sitting A was started with a shell background `&` at 07:43:00 PST, against the round's rule. *Answered:* by the card lane's report it was a bounded wait that read the session's state only and ended at 07:51:45 with no other effect; nothing in the data, the reductions or this note depends on it.
6. **Open: step 13's outputs were not committed.** *Answered by this note and sitting A's note 1:* committed at the hashes the card lane named (`x04-e198-A.json` `dc0ef689...`, `checks-e198-A.json` `4b437f3f...`, `x04-e198-B.json` `8421a0ab...`, `checks-e198-B.json` `25144f1f...`), with their printed lines; `scores-e198.json` as sitting B's section 8 says.

## 8. Departure (dated Mon 16 Nov 2026, this lane)

**`scores-e198.json` is not the card lane's copy byte for byte.** That copy (sha256 `12bddf55...`) records each reduction's path as the card lane gave it to the scorer: an absolute desk path that names a lab login, which the lab's public files never carry. The committed file is the registered scorer (`score_e198.py`, `1d2b211e...`, unchanged, run under `/usr/bin/python3 -I -B`) run by this lane on the two byte-identical reductions, from a copy of the tree's top, given their repo paths (`--a docs/reports/data/2026-11-16-e198-x04-clock-sitting-a-aifoundry1-c1/x04-e198-A.json --b docs/reports/data/2026-11-16-e198-x04-clock-sitting-b-aifoundry1-c1/x04-e198-B.json`). Leaf by leaf it differs from the card lane's copy in 2 of 1,464 values, `card1_files.A.path` and `card1_files.B.path` (lines 980 and 984 of 1,872); every other value is equal: the verdicts, the counts, the 36 prices, the REPORTED readings, the rules, the forecast's sha256 and each reduction's sha256. `scores-e198.txt` names no path and is the card lane's copy byte for byte. The other four files here are byte for byte.

## 9. Re-make it

From the top of the repository (nothing here opens a device); set R to an empty folder outside the repository (the first line), then run the rest as they stand:

    D=docs/reports/data/2026-11-16-e198-x04-clock-sitting-b-aifoundry1-c1; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS-note1)
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04-e198-B.json" > "$R/x04-e198-B.txt" 2>&1
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04-e198-B.json" "$R/x04" --out "$R/checks-e198-B.json" > "$R/checks-e198-B.txt" 2>&1
    /usr/bin/python3 -I -B tools/claims-v3/e198/score_e198.py score --a docs/reports/data/2026-11-16-e198-x04-clock-sitting-a-aifoundry1-c1/x04-e198-A.json --b "$D/x04-e198-B.json" --out "$R/scores-e198.json" > "$R/scores-e198.txt" 2>&1
    for f in x04-e198-B.json checks-e198-B.json x04-e198-B.txt checks-e198-B.txt scores-e198.json scores-e198.txt; do cmp "$R/$f" "$D/$f" && echo "$f: byte for byte"; done

They check this note's list, unpack the main run's telemetry, run the registered reducer and the kit's checker as step 13 does, then the scorer on the two committed reductions by their repo paths (so its path fields match the committed file), and compare each output with the committed file: each line should end "byte for byte". README.md's own "Re-make it" checks the inputs against the box's manifest first.

## 10. This note's rules

No number of a sealed forecast, and no score against one. No lab user's login, no desk path, no access detail. Times are Pacific, from the real clock. The interpreter is named. A check not run is NOT RUN: **this lane did not re-derive the reduction or the scores with its own code** (the data verifier did, section 6); it re-ran the registered programs (section 3) and compared files. Check 9 of E193.md 8 was not re-derived by the verifier either; its word is the kit checker's.

SPDX-License-Identifier: Apache-2.0
