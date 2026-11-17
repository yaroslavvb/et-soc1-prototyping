# E211 data, dated note 3: the frozen scorer's output, committed beside the data byte for byte - R0, S6, T1-T3 and E1-E4 PASS; T4 FAIL (rgm211 ran 2.9% and 5.8% fewer wall cycles at the two controls) and Amendment A1 not applied, so family W carries "the controls did not pass: not a model test" (W1 FAIL 5/10, W2 PASS, H1-H3 NOT DECIDED); H5 MM1 BETTER, H4 and H6 NOT DECIDED; CT and CE FAIL; with verify-e211d's re-derivation beside each result

*Tue 17 Nov 2026 (week 47), PST; written at about 14:51 PST by Q204's lane `scores-e211`, after this directory's data commit `38aaf004` (13:41:44 PST, pushed 13:41:48), after the day's data verifier `verify-e211d` (HOLDS WITH FIXES) and after dated note 2 (`0307eaaf`, committed 14:25:24 and pushed 14:25:26 by the lane `fix-e211d`, which answered the verifier's four wording findings). It adds new files only: no committed file, rule, band, forecast, label or scorer is changed, and nothing is re-scored. Labels: **registered** (E211.md with its Amendment A1; the kit), **measured** (this directory's records), **blind** (every forecast here: E211's own, frozen in `forecast-e211.json` `90e8d1ae...` at 00:14 PST and registered in `1393a649`, pushed 07:59:20; MM1-v2's column, frozen in `89aa0c94`, pushed 08:12:57; all before the booking at 13:16:49, step 7's config read at 13:21:20 and the session's first card command at 13:21:35), **REPORTED** (summaries and readings, never verdicts), **post hoc** (written after the data), **desk check of code** (this lane's checks and re-runs, and verify-e211d's own code). Every check named here ran on aifoundry2 under `/usr/bin/python3` 3.12.3 (`-I -B`).*

**The words.** The frozen scorer (`score_e211.py`, registered sha256 `21a4b5f1...`, with Amendment A1's clauses 1-3), run by the kit's step 13 on this directory's committed `data-e211.json`, printed: **R0 PASS** (every check of C exact or approx, every identity gate GATE OK, every walk as registered, the smoke's counter means inside the band); **S6 PASS** (every counted launch at 590-610 MHz); **T4 FAIL**: at the two controls, where both walks are one op stream, rgm211 ran 0.9714 and 0.9422 of rgm136's wall cycles (ln -0.0290 and -0.0596, against 0.01); **A1 NOT APPLIED** (the two controls differ by 0.0306 in ln, more than 0.005), so W1, W2 and H1-H3 read on the raw ratios and carry the registered words "the controls did not pass: not a model test". MM1's absolute rules at rgm211's 12 points all pass: **T1 11/12, T2 12/12, T3 11/12, E1 12/12, E2 12/12, E3 11/12, E4 12/12** (11 of 12 needed). On the ratio rgm211 / rgm136: **W1 FAIL** (5 of 10 W pairs within 0.05 in ln of MM1's ratio; 9 needed), **W2 PASS** (8 pairs decided, none against MM1's direction); **H1** (MM1 against F1) NOT DECIDED 8/2/0, p 0.109; **H2** (against the chip-lines null NC) NOT DECIDED 7/3/0, p 0.344; **H3** (against the no-walk null N0) NOT DECIDED 7/1/2, p 0.0703. On the wall cycles at rgm211's points: **H4** (against F1) NOT DECIDED 6/6/0, p 1.0; **H5** (against NC) **MM1 BETTER** 10/1/1, p 0.0117. **H6** (J over idle, MM1 against MM1-S) NOT DECIDED 8/2/2, p 0.109; **H7** NOT REGISTERED; **SR** READ; family C: **CT FAIL** and **CE FAIL** (1 of 2 each). verify-e211d's own code gives every one of these verdicts, counts and p values, and so does this lane's.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e211-A.json` | 29,826 | `71c991f917d22e55bf589b890e7158200e3e900aa9cb850838cd78a5aab6bcd6` | the frozen scorer's output (its `--out`): every rule with its counts, the per-point errors, the head-to-head results with their bootstrap intervals, and the REPORTED readings |
| `scores-e211-A.txt` | 561 | `ec863ed99a1305e6e1cfba53bdf4e6694e376f20e4061bcbd810ff7248a64693` | its printed lines: step 13's capture of the scorer's call, which the kit's step copies (the scorer writes no text file of its own) |
| `README.md.dated-note-3.md` | (this note) | listed in `SHA256SUMS-note3` | this dated note |
| `SHA256SUMS-note3` | 8 lines | (not listed in itself) | the three files above; `SHA256SUMS-note2`, which no list names; and `README.md`, `README.md.dated-note-1.md`, `README.md.dated-note-2.md` and `SHA256SUMS` as committed |

The two output files are card-e211's step-13 output files byte for byte. With `SHA256SUMS` (235 entries), `SHA256SUMS-note2` (7) and `SHA256SUMS-note3`, every one of the directory's 247 files is in a list except `SHA256SUMS-note3` itself.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 (`rb/s24_score_e211.sh A`, one blob from the kit `2b7f261f` to the lab's head) is the runbook log's last five lines (lines 91-95), at 13:42:02-13:42:03 PST, each rc 0 and status ok, one process for the five calls. Call 1 printed the data commit `38aaf004` and its subject; call 2 (this directory clean) printed nothing; call 3 read all 235 `SHA256SUMS` entries OK, in the list's order; call 4 printed "HISTORY OK: HEAD descends from the registration 1393a64935c0 (subtree fa109d01); 72 additions and nothing else under tools/claims-v3/e211 since it; ..."; call 5, the frozen scorer on `data-e211.json` with `--out`, printed the lines of section 3. The log shows no other run of the scorer on data; its stand-in self-test ran once, at step 2 (the kit's desk step `rb/s03_desk_e211.sh`, 13:19:51 PST, rc 0).
- **The bytes and their times.** The JSON was last written at 13:42:03.534 PST, inside call 5 (call 4's capture closed at 13:42:03.167, call 5's at 13:42:03.534); the text at 13:42:03.542, after call 5's capture closed, by the step's copy. The text equals that capture byte for byte, and it rebuilds exactly from the JSON by the scorer's own print statements (its `main()`, taken from the committed source).
- **The commit before it.** The data commit `38aaf004` was made at 13:41:44 PST and pushed at 13:41:48 (the lab clone's record of the push); the card lane ran step 13 from 13:42:02, the clone's HEAD then the data commit. During the step's calls the clone's HEAD moved once, at 13:42:03, to `d203e577` (E210's scores: five files added under E210's data directory and nothing else; clause 4).
- **The frozen files.** `score_e211.py` (`21a4b5f1...`), `forecast-e211.json` (`90e8d1ae...`), `rules-e211.json` (`53c54fbe...`) and `points-e211.json` (`234b496a...`) carry E211.md section 0's sha256 at the data commit and at the lab's head; the JSON's `inputs_sha256` names the same three pins. `tools/claims-v3/e211` is one tree (`172ce4bf...`) at the kit, the data commit and the head, and `data-e211.json` is `76dbb734...` at both. Since the data commit this directory has changed only by dated note 2's five additions (`0307eaaf`).
- **The re-runs** (14:37 PST, this lane, inside the round's CPU slot and its no-device sandbox): (1) the step's command in the lab clone's own tree, (2) the same under an audit hook that lists every file it opens, and (3) in a fresh tree holding only the five committed files it opened (`score_e211.py`, `forecast-e211.json`, `rules-e211.json`, `points-e211.json` and `data-e211.json`, taken from `38aaf004`'s objects; no bytecode cache): each run's JSON and printed lines equal the step's outputs byte for byte; the clone read 0 status lines before and after.
- **verify-e211d** (desk; its own code, written from E211.md section 7 and `rules-e211.json`, importing nothing from the kit, the scorer or any forecaster) re-derived every run from the raw files (284 numeric fields equal `data-e211.json`) and scored every rule: 22 of 22 verdicts and counts equal the scorer's, and 131 further numbers (the pair and family C ratios, the per-point errors, SR's s) differ by 0. Its re-run of the frozen scorer gave the two files byte for byte, and the scorer's stand-in self-test read SELFTEST PASS. This lane's own arithmetic (from `data-e211.json` and the frozen files; nothing imported from the kit, the scorer or a model) gives the 26 point means, the 12 pair ratios, the 84 per-point errors, every verdict, count, p value and per-pair d, and the bootstrap intervals by the registered recipe; each equals the scorer's JSON and verify-e211d's (largest difference 0).

## 3. The rules: their registered words, the verdicts, verify-e211d beside

The scorer's printed lines (`scores-e211-A.txt`, verbatim):

```
R0: PASS
S6: PASS
T4: FAIL
T1: PASS (11/12)
T2: PASS (12/12)
T3: PASS (11/12)
E1: PASS (12/12)
E2: PASS (12/12)
E3: PASS (11/12)
E4: PASS (12/12)
W1: FAIL (5/10)
W2: PASS
H1: NOT DECIDED (8/2/0, p 0.109375)
H2: NOT DECIDED (7/3/0, p 0.34375)
H3: NOT DECIDED (7/1/2, p 0.0703125)
H4: NOT DECIDED (6/6/0, p 1.0)
H5: MM1 BETTER (10/1/1, p 0.01171875)
H6: NOT DECIDED (8/2/2, p 0.109375)
H7: NOT REGISTERED
SR: READ
CT: FAIL
CE: FAIL
A1: NOT APPLIED: the two controls differ by 0.03060 in ln, more than consistency_ln 0.005; W1, W2 and H1-H3 read on the raw ratios
```

**The registered definitions** (E211.md section 7, quoted with its emphasis and code marks left out): "A run (E206's form): its die gate, 10 s at rest (p_rest = the median of its last 5 s), one host process --seconds 6 --budget 7.5 under a plain timeout 10, a 4 s tail. Measured, per run (the kit's reducer; the scorer's docstring has it exactly): counted launches are launch >= 0, ok, wall_s >= 0.1 s, the kernel clock in 590-610 MHz; t_gemm = sum of wall / sum of passes; the wall = the median of cycles_max / passes over ops a minion a GEMM (the slowest minion); the counter's mean = the median of the host's cycles_per_op; W over idle = p_work - p_rest; J over idle = W t_gemm; J with the card at rest = p_work t_gemm. A run whose host record differs from its point is set aside and flagged. A point = the mean of its kept runs (every block); a pair's ratio (rgm211 / rgm136) = the mean of its gemmLn runs over the mean of its gemmL runs in its own W or X block (adjacent, A B or A B B A); family C's ratio = the mean of the gemmLnc runs over the twin's C-block run." And for every head to head: "d = |ln(measured / second)| - |ln(measured / first)|; the first is closer where d > the tie, the second where d < -the tie; ties dropped."

Each rule's registered words (E211.md section 7's table: what it reads, its registered numbers and its verdict, quoted with their emphasis and code marks left out), the scorer's verdict, and verify-e211d's:

- **R0.** "every check of C exact or approx; every rgm211-host process prints walk_ok true on every launch with walk nm (gemmLn) or mn (gemmLnc) and walk_launches_bad 0; every process's identity gate GATE OK; the smoke's counter mean 50-250% of MM1's at s01-s03"; registered numbers: "-"; verdict: "PASS / FAIL; a FAIL labels every other verdict (the scorer attaches the label to every other rule: A1, clause 2)". **The scorer: PASS** (no reason listed). verify-e211d: PASS (identity 41 of 41 processes, walks 22 of 22, checks 39 approx and 2 exact with none missing; the smoke's counter means 1.04, 0.96 and 0.96 of MM1's).
- **S6.** "every counted launch's clock in 590-610 MHz, per point"; registered numbers: "590-610 MHz"; verdict: "PASS / FAIL". **The scorer: PASS** (no point outside). verify-e211d: PASS (the kernel clocks of the counted launches 599.26-599.70 MHz).
- **T4.** "THE CONTROLS: |ln ratio| at x01 and x02"; registered numbers: "0.01 (the two ELFs' layout bound)"; verdict: "PASS both / FAIL: family W's verdicts then read "the controls failed: not a model test", unless A1 applies (next row)". **The scorer: FAIL**: x01 0.97143 (ln -0.02898), x02 0.94216 (ln -0.05958), neither within 0.01. verify-e211d: FAIL, the same two ratios.
- **A1.** "Amendment A1, clause 1, before any datum: THE CONTROL-CORRECTED READING. With a = ln ratio at x01, b at x02 and c_hat = (a + b) / 2"; registered numbers: "consistency 0.005; |c_hat| at most 0.03"; verdict: "when T4 FAILs, a and b lie on one side of 0 within 0.005 of each other and |c_hat| <= 0.03: W1, W2 and H1-H3 are scored on each W pair's measured wall ratio over exp(c_hat), labelled so, the raw-ratio verdicts REPORTED beside; otherwise as registered, the corrected verdicts REPORTED beside (never verdicts)". **The scorer: NOT APPLIED**: "the two controls differ by 0.03060 in ln, more than consistency_ln 0.005"; c_hat -0.04428. verify-e211d: not applied (both controls on one side, |a - b| 0.030599, c_hat -0.044281). The magnitude condition fails too: |c_hat| 0.0443 is more than 0.03 (clause 2).
- **T1, T2, T3.** "MM1 at rgm211's 12 points: the wall, the counter's mean, seconds"; registered numbers: "13%, 16%, 13% (E207's bands: 2 x MM1-v1's larger held-out rms, rounded up)"; verdict: "PASS at >= 90% of the scored points; TOO FEW under 10". **The scorer: T1 PASS 11/12, T2 PASS 12/12, T3 PASS 11/12** (11 needed); the misses: w04n in T1 (+16.0% against 13%) and in T3 (+16.1%). verify-e211d: the same counts and misses.
- **E1, E2, E3, E4.** "J over idle given the measured seconds (MM1's affine W at the measured t_op) / with its seconds forecast; J at rest given / forecast"; registered numbers: "15%, 16%, 5%, 13%; a point forecast under 3 W in watts within 0.215 W (none of E211's: all forecasts 8-29 W)"; verdict: "as T". **The scorer: E1 PASS 12/12, E2 PASS 12/12, E3 PASS 11/12, E4 PASS 12/12**; the one miss: w01n in E3 (+5.37% against 5%). verify-e211d: the same.
- **W1.** "THE QUESTION: per W pair, |ln(measured ratio / MM1's)|"; registered numbers: "0.05"; verdict: "PASS at >= 90% of the scored pairs; TOO FEW under 8". **The scorer: FAIL**, 5 of 10 pairs inside 0.05 (9 needed), with the words "the controls did not pass: not a model test"; each other model's own count inside the same tolerance (REPORTED): F1 1, NC 3, N0 2. verify-e211d: FAIL 5/10, the same per-pair errors (section 4) and counts.
- **W2.** "THE DIRECTION, at the pairs whose MM1 ratio is >= 0.03 from 1 in ln (w02-w10): the measured ratio decides when |ln| >= 0.01 (the sign test's tolerance, critic-kernel2 finding 9: at 3x6x3, MM1's 0.968, a measured ratio within 1% of 1 decides nothing)"; registered numbers: "apply 0.03, decide 0.01, at least 6 decided"; verdict: "PASS if none decided misses; FAIL if one does; NOT DECIDED otherwise". **The scorer: PASS** (8 decided, 0 missed; w04 not decided, its measured ratio 0.99797 lying within 0.01 of 1), with the same words. verify-e211d: PASS, pair by pair the same.
- **H1.** "the ratio per W pair: MM1 against F1"; registered numbers: "tie 0.005 in ln"; verdict: "the exact two-sided sign test at 0.05 on the untied: MM1 BETTER / F1 BETTER / NOT DECIDED; TOO FEW under 6". **The scorer: NOT DECIDED** (MM1 closer 8, F1 closer 2, ties 0; exact two-sided p 0.109375), with the same words. verify-e211d: NOT DECIDED 8/2/0, p 0.109375, pair by pair the same closer (section 4).
- **H2.** "the ratio per W pair: MM1 against the chip-lines null NC"; registered numbers: "tie 0.005"; verdict: "as H1". **The scorer: NOT DECIDED** (MM1 closer 7, NC closer 3, ties 0; exact two-sided p 0.34375), with the same words. verify-e211d: NOT DECIDED 7/3/0, p 0.34375, pair by pair the same closer (section 4).
- **H3.** "the ratio per W pair: MM1 against the no-walk null N0"; registered numbers: "tie 0.005"; verdict: "as H1". **The scorer: NOT DECIDED** (MM1 closer 7, N0 closer 1, ties 2; exact two-sided p 0.0703125), with the same words. verify-e211d: NOT DECIDED 7/1/2, p 0.0703125, pair by pair the same closer (section 4).
- **H4.** "the wall cycles at rgm211's 12 points: MM1 against F1"; registered numbers: "tie 0.001"; verdict: "as H1". **The scorer: NOT DECIDED** (MM1 closer 6, F1 closer 6, ties 0; exact two-sided p 1.0). verify-e211d: NOT DECIDED 6/6/0, p 1.0.
- **H5.** "the wall cycles at rgm211's 12 points: MM1 against NC"; registered numbers: "tie 0.001"; verdict: "as H1". **The scorer: MM1 BETTER** (MM1 closer 10, NC closer 1, ties 1; exact two-sided p 0.01171875). verify-e211d: MM1 BETTER 10/1/1, p 0.01171875.
- **H6.** "J over idle given the measured seconds at rgm211's points: MM1 (fresh lines per shire-line) against MM1-S (A's per DRAM line)"; registered numbers: "tie 0.005"; verdict: "as H1 (a point with no fresh A line ties)". **The scorer: NOT DECIDED** (MM1 closer 8, MM1-S closer 2, ties 2; exact two-sided p 0.109375). verify-e211d: NOT DECIDED 8/2/2, p 0.109375.
- **H7.** "MM1-v2 against MM1-v1"; registered numbers: "-"; verdict: "NOT REGISTERED (section 0)". **The scorer: NOT REGISTERED.** MM1-v2's column is scored outside E211's rules (clause 6).
- **SR.** "THE STRIDE CARRYOVER: s = ln(ratio 2x8x4 / ratio 2x9x4) measured, against the four readings' s (literal -0.016; none +0.004; both +0.024; rgm136 only -0.136)"; registered numbers: "-"; verdict: "READ: the closest reading named (no verdict on MM1)". **The scorer: READ**: the measured s +0.2054 against the readings' literal -0.0164, none +0.0039, both halves +0.0240 and rgm136 only -0.1357; the closest named: both halves, still 0.181 from the measured s. verify-e211d: READ, the same s and the same closest reading.
- **CT.** "family C: the wall ratio within tol of C1's (0.956) at both shapes"; registered numbers: "0.02 in ln"; verdict: "PASS both / FAIL". **The scorer: FAIL** (1 of 2): c01's wall ratio 0.96897 lies within 0.02 in ln of C1's 0.95632; c02's 0.87794 does not (ln -0.0855). verify-e211d: FAIL 1/2.
- **CE.** "family C: the J over idle ratio within tol of C1's (1.17, 1.15) at both shapes"; registered numbers: "0.05 in ln"; verdict: "PASS both / FAIL". **The scorer: FAIL** (1 of 2): c02's J over idle ratio 1.15522 lies within 0.05 in ln of C1's 1.15281; c01's 1.38910 against C1's 1.16852 does not (ln +0.1729). verify-e211d: FAIL 1/2.

## 4. The ratio rgm211 / rgm136 per W pair: the head to head per shape pair, verify-e211d and note 2 beside

| pair | shape | measured wall ratio | MM1 (MM1-v1) | F1 | NC | N0 | MM1-v2 (REPORTED) | W1: ln(measured / MM1) | W2 | d (H1) | d (H2) | d (H3) | closer: H1 / H2 / H3 | verify-e211d's closer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w01 | 2x3x2 | 0.94605 | 0.99933 | 0.97959 | 0.97959 | 1 | 0.99930 | -0.0548 (outside) | not read (MM1 within 0.03 of 1) | -0.0200 | -0.0200 | +0.0007 | F1 / NC / tie | F1 / NC / tie |
| w02 | 3x3x4 | 1.09107 | 1.04430 | 1.15267 | 1.35156 | 1 | 1.06316 | +0.0438 (inside) | holds | +0.0111 | +0.1703 | +0.0433 | MM1 / MM1 / MM1 | MM1 / MM1 / MM1 |
| w03 | 3x6x3 | 0.98287 | 0.96806 | 0.82876 | 0.78621 | 1 | 0.93324 | +0.0152 (inside) | holds | +0.1554 | +0.2081 | +0.0021 | MM1 / MM1 / tie | MM1 / MM1 / tie |
| w04 | 2x8x4 | 0.99797 | 0.88052 | 0.87046 | 0.83622 | 1 | 0.85929 | +0.1252 (outside) | not decided | +0.0115 | +0.0516 | -0.1232 | MM1 / MM1 / N0 | MM1 / MM1 / N0 |
| w05 | 2x9x4 | 0.81270 | 0.89506 | 0.87298 | 0.84223 | 1 | 0.88956 | -0.0965 (outside) | holds | -0.0250 | -0.0608 | +0.1109 | F1 / NC / MM1 | F1 / NC / MM1 |
| w06 | 3x5x7 | 1.17364 | 1.18060 | 1.02721 | 1.26796 | 1 | 1.23050 | -0.0059 (inside) | holds | +0.1273 | +0.0714 | +0.1542 | MM1 / MM1 / MM1 | MM1 / MM1 / MM1 |
| w07 | 3x6x6 | 1.20269 | 1.14642 | 1.03425 | 1.28923 | 1 | 1.23426 | +0.0479 (inside) | holds | +0.1030 | +0.0216 | +0.1366 | MM1 / MM1 / MM1 | MM1 / MM1 / MM1 |
| w08 | 4x3x6 | 1.15601 | 1.24789 | 0.98344 | 1.17451 | 1 | 1.25101 | -0.0765 (outside) | holds | +0.0852 | -0.0606 | +0.0685 | MM1 / NC / MM1 | MM1 / NC / MM1 |
| w09 | 6x6x6 | 1.16732 | 1.23569 | 1.00000 | 1.25674 | 1 | 1.25686 | -0.0569 (outside) | holds | +0.0978 | +0.0169 | +0.0978 | MM1 / MM1 / MM1 | MM1 / MM1 / MM1 |
| w10 | 3x5x7, int8 | 1.16671 | 1.18060 | 1.02385 | 1.30059 | 1 | 1.23050 | -0.0118 (inside) | holds | +0.1188 | +0.0968 | +0.1424 | MM1 / MM1 / MM1 | MM1 / MM1 / MM1 |

The measured ratios are desk arithmetic of the measured runs (each pair's own W-block runs: the mean wall cycles an op of its gemmLn runs over that of its gemmL runs); the forecast columns are frozen (blind). W1 counts a pair inside when |ln(measured / MM1)| <= 0.05; W2 reads w02-w10 (MM1's ratio at least 0.03 from 1 in ln), decided where the measured ratio is at least 0.01 from 1 in ln. d as registered, with the tie 0.005: MM1 is closer where d > 0.005, the other model where d < -0.005, a tie otherwise. Every closer equals verify-e211d's and dated note 2's, and every d equals note 2's. All of these readings carry the registered words "the controls did not pass: not a model test".

**The control-corrected reading** (A1's form, REPORTED and never a verdict, from the scorer's own REPORTED block; each ratio over exp(c_hat), c_hat -0.04428): W1 FAIL 5/10; W2 FAIL (9 decided, 2 missed: w03 and w04); H1 NOT DECIDED 7/2/1 (p 0.1796875); H2 NOT DECIDED 5/3/2 (p 0.7265625); H3 NOT DECIDED 7/2/1 (p 0.1796875). Its ln(corrected / MM1) per pair: w01 -0.0105; w02 +0.0881; w03 +0.0595; w04 +0.1695; w05 -0.0522; w06 +0.0384; w07 +0.0922; w08 -0.0322; w09 -0.0126; w10 +0.0324. This lane's code gives the same readings.

## 5. MM1's errors at rgm211's 12 points (T1-T3, E1-E4) and the head to head per point (H4-H6)

| point | arm | T1 wall | T2 counter mean | T3 seconds | E1 J over idle, t given | E2 J over idle, t forecast | E3 J at rest, t given | E4 J at rest, t forecast | d (H4: MM1 vs F1) | d (H5: MM1 vs NC) | d (H6: MM1 vs MM1-S) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| w01n | `gemmLn2x3x2` (fp32) | -4.0% | -4.8% | -4.0% | +10.8% | +10.5% | **+5.4% (miss)** | +3.1% | +0.0947 (MM1) | -0.0072 (NC) | -0.0024 (tie) |
| w02n | `gemmLn3x3x4` (fp32) | +3.7% | +4.8% | +3.8% | +1.0% | +1.4% | +0.5% | +2.7% | +0.1788 (MM1) | +0.3500 (MM1) | +0.0131 (MM1) |
| w03n | `gemmLn3x6x3` (fp32) | +7.0% | +6.6% | +6.0% | -1.8% | -1.3% | -0.8% | +2.6% | -0.0347 (F1) | +0.0004 (tie) | +0.0142 (MM1) |
| w04n | `gemmLn2x8x4` (fp32) | **+16.0% (miss)** | +15.9% | **+16.1% (miss)** | +2.9% | +4.4% | +1.2% | +11.0% | +0.0016 (MM1) | +0.1034 (MM1) | -0.0100 (MM1-S) |
| w05n | `gemmLn2x9x4` (fp32) | -12.8% | -13.7% | -12.8% | +1.8% | +0.7% | +0.9% | -6.5% | +0.1171 (MM1) | +0.0152 (MM1) | -0.0105 (MM1-S) |
| w06n | `gemmLn3x5x7` (fp32) | -5.0% | -4.7% | -4.9% | -1.2% | -1.7% | -0.5% | -3.6% | -0.0230 (F1) | +0.1482 (MM1) | +0.0960 (MM1) |
| w07n | `gemmLn3x6x6` (fp32) | +0.0% | +0.4% | +0.1% | -0.6% | -0.6% | -0.3% | -0.2% | +0.0234 (MM1) | +0.1947 (MM1) | +0.0834 (MM1) |
| w08n | `gemmLn4x3x6` (fp32) | -7.4% | -7.1% | -7.3% | -1.7% | -2.5% | -0.7% | -5.4% | -0.0555 (F1) | +0.1197 (MM1) | +0.1012 (MM1) |
| w09n | `gemmLn6x6x6` (fp32) | -9.1% | -8.9% | -9.0% | -2.0% | -2.9% | -0.8% | -6.7% | -0.0850 (F1) | +0.0944 (MM1) | +0.1049 (MM1) |
| w10n | `gemmLn3x5x7` (int8) | -5.1% | -4.7% | -5.0% | +0.2% | -0.9% | +0.1% | -4.0% | -0.0256 (F1) | +0.2395 (MM1) | +0.1795 (MM1) |
| x01n | `gemmLn1x5x5` (fp32) | +2.6% | +1.9% | +2.7% | +0.4% | +0.6% | +0.2% | +1.7% | +0.2029 (MM1) | +0.1010 (MM1) | -0.0039 (tie) |
| x02n | `gemmLn3x1x8` (fp32) | -8.2% | -8.0% | -8.1% | -2.0% | -2.9% | -0.8% | -6.0% | -0.0799 (F1) | +0.0971 (MM1) | +0.0990 (MM1) |

Errors are measured / forecast - 1, the rules' form; the bands: T1 13%, T2 16%, T3 13%, E1 15%, E2 16%, E3 5%, E4 13%. H4 and H5 read the wall cycles an op with the tie 0.001, H6 the J over idle at the measured seconds with the tie 0.005 (d as registered). Each of the 84 errors equals the scorer's and verify-e211d's; the per-point closers give back the scorer's counts.

## 6. Each model's error (REPORTED: desk arithmetic of the measured records and the frozen forecasts)

Error = ln(measured / forecast); each cell is its rms over the set, then its mean in brackets, in percent (a positive mean: the card measured more than the model forecast). **J over idle, t given** = the model's W at the measured seconds times the measured t (MM1-v1's and MM1-v2's affine W = A + B / t_op at the measured t_op; MM1-S's affine W; F1's frozen W, which has no seconds term); **t forecast** = the model's own frozen J over idle; **J at rest, t given** = the measured p_rest times the measured t, plus the J given; **t forecast** = the measured p_rest times the model's seconds, plus its frozen J (F2's seconds are F1's). F1 and NC carry one cycles figure an op, read against the wall and against the counter's mean. MM1-v1 is E211's MM1 (its registered forecasts through the desk map); MM1-v2's column is the frozen `89aa0c94` (blind for E211, outside E211's rules: H7 NOT REGISTERED). A dash: the model forecasts no such quantity.

**rgm211 (gemmLn) at its 12 points: the absolute rules' set**

| model | wall cycles an op | counter's mean | seconds | J over idle, t given | J over idle, t forecast | J at rest, t given | J at rest, t forecast |
|---|---|---|---|---|---|---|---|
| MM1-v1 | 8.01 (-2.18) | 8.07 (-2.18) | 7.92 (-2.18) | 3.34 (+0.59) | 3.54 (+0.33) | 1.65 (+0.34) | 5.22 (-1.08) |
| MM1-v2 | 8.86 (-3.61) | 8.82 (-3.61) | 8.76 (-3.61) | 3.28 (-0.59) | 3.66 (-0.98) | 1.57 (-0.16) | 6.00 (-2.50) |
| F1 | 13.16 (-6.85) | 15.20 (-8.84) | 13.14 (-6.85) | 21.08 (+18.24) | 12.05 (+11.40) | 8.98 (+7.49) | 6.87 (+0.64) |
| NC | 20.99 (-13.62) | 21.93 (-15.61) | 20.91 (-13.61) | - | - | - | - |
| F2 | - | - | - | - | 26.11 (-17.86) | - | 14.86 (-10.99) |
| MM1-S | - | - | - | 9.51 (-5.60) | 9.95 (-5.82) | 3.75 (-2.08) | - |

**rgm136 (gemmL) at the 12 twins: four in MM1-v1's fit, three run in E207 before E211, five never run before E211**

| model | wall cycles an op | counter's mean | seconds | J over idle, t given | J over idle, t forecast | J at rest, t given | J at rest, t forecast |
|---|---|---|---|---|---|---|---|
| MM1-v1 | 3.69 (-0.86) | 3.52 (+0.11) | 3.67 (-0.77) | 2.58 (+0.13) | 2.76 (+0.02) | 1.25 (+0.12) | 2.97 (-0.43) |
| MM1-v2 | 2.86 (-1.23) | 2.67 (-0.26) | 2.82 (-1.15) | 2.72 (-1.10) | 2.88 (-1.22) | 1.25 (-0.41) | 2.60 (-1.15) |
| F1 | 15.74 (-13.42) | 16.61 (-14.45) | 15.66 (-13.34) | 24.87 (+23.69) | 10.77 (+10.35) | 10.01 (+9.51) | 6.76 (-3.83) |
| NC | 13.16 (-10.97) | 13.62 (-11.99) | 13.08 (-10.88) | - | - | - | - |
| F2 | - | - | - | - | 27.02 (-22.04) | - | 19.09 (-16.82) |
| MM1-S | - | - | - | 5.22 (-2.87) | 5.44 (-2.97) | 2.21 (-1.12) | - |

**The ratio rgm211 / rgm136 over the 10 W pairs** (ln(measured ratio / the model's ratio): rms, then the mean in brackets, in percent; then how many pairs lie within W1's 0.05)

| model | wall cycles an op (W1's ratio) | counter's mean | seconds | J over idle (the frozen ratios) |
|---|---|---|---|---|
| MM1-v1 | 6.46 (-0.70); 5 of 10 | 6.99 (-1.81); 5 of 10 | 6.45 (-0.80); 5 of 10 | 2.12 (+0.57); 10 of 10 |
| MM1-v2 | 7.37 (-1.97); 3 of 10 | 7.89 (-3.08); 3 of 10 | 7.32 (-2.07); 4 of 10 | 1.87 (+0.49); 10 of 10 |
| F1 | 12.84 (+8.77); 1 of 10 | 12.34 (+7.66); 0 of 10 | 12.71 (+8.68); 1 of 10 | 1.94 (+1.46); 10 of 10 |
| NC | 12.56 (-2.30); 3 of 10 | 12.55 (-3.40); 1 of 10 | 12.38 (-2.39); 3 of 10 | - |
| N0 | 13.51 (+6.04); 2 of 10 | 13.58 (+4.93); 2 of 10 | 13.52 (+5.94); 2 of 10 | 2.55 (+1.20); 10 of 10 |
| F2 | - | - | - | 14.62 (+5.21); 6 of 10 |
| MM1-S | - | - | - | 6.08 (-3.22); 6 of 10 |

So, at rgm211's points, MM1-v1 and MM1-v2 read the joules within about 3.3% rms given the measured seconds (F1 21%), and the cycles and seconds within about 8-9% (F1 13%, NC 21%); at the twins MM1's cycles are within 2.9-3.7%. On the ratio, MM1-v1's wall error is 6.5% rms against 12.8% for F1, 12.6% for NC and 13.5% for N0; the J over idle ratio moves little from 1 at these shapes, so every model but F2 and MM1-S reads it within 0.05 at all 10 pairs. These are REPORTED summaries, never verdicts; the registered verdicts are section 3's.

In score-v2-e211's form (forecast / measured - 1; its committed `tools/matmul/mm1/v2/score-e211.json`, `d38f148c`), the wall cycles at rgm211's points read MM1-v2 8.93%, MM1-v1 8.10%, F1 14.49% and NC 23.52% rms, and the J over idle given the seconds MM1-v2 3.21%, MM1-v1 3.21%, F1 18.42%; this lane's code reproduces all 58 of that file's aggregates for these two sets, and its ratio rms, exactly.

## 7. The scorer's REPORTED readings (its JSON; never verdicts)

- **The bootstrap intervals** (percentile 95% of the mean and the median d, 10,000 resamples, seeded as registered): H1 mean [+0.0279, +0.1048], median [+0.0111, +0.1188]; H2 mean [-0.0010, +0.1051], median [-0.0200, +0.1208]; H3 mean [+0.0088, +0.1092], median [+0.0021, +0.1366]; H4 mean [-0.0245, +0.0817], median [-0.0451, +0.1059]; H5 mean [+0.0680, +0.1793], median [+0.0548, +0.1714]; H6 mean [+0.0232, +0.0905], median [-0.0031, +0.1001]. This lane's code, on the same recipe, gives the same intervals, and the same for H1-H3's control-corrected reading.
- **Family C** (gemmLnc, rgm136's own non-cooperative branch, over its C-block twin; C0 the null ratio 1, C1 E101's rule, C2 the draft rule, REPORTED): c01 (`gemmLnc2x3x2` over w01m) wall 0.96897 (C1 0.95632; closer: C1), counter's mean 0.92197 (C1 0.91503), J over idle 1.38910 (C1 1.16852, C2 1.42862; closer: C1); c02 (`gemmLnc3x5x7` over w06m) wall 0.87794 (C1 0.95632; closer: C1), counter's mean 0.87785 (C1 0.91503), J over idle 1.15522 (C1 1.15281, C2 1.39156; closer: C1).
- **The timing simulation against the card** (his question; A1 clause 3's two columns): the measured wall cycles an op over the kit's sys_emu steps an op for the point's own ELF and walk (a 2x2x1 count at mask 0x1, not a law): gemmL (rgm136, 47.742 steps an op) 18.9-29.6 (median 24.2) over its 12 points; gemmLn (rgm211, 32.762) 26.1-42.3 (median 41.0); gemmLnc (40.566) 21.6-25.4 over its 2. Beside it, the measured cycles a GEMM over MM1's step column (rgm136's gemmL law at every point, so not the count of a gemmLn or gemmLnc point's own loop): gemmL 19.2-30.2, gemmLn 18.2-29.6, gemmLnc 18.6-22.0. The scorer's note: "Simulator steps: not time, and not instruction counts." The counter's mean over the tensor unit's floor reads a median 2.19 (gemmL), 2.52 (gemmLn) and 1.69 (gemmLnc).
- **MM1-v1's rest law against the measured rest** (the measured p_rest minus the law, over the 26 points): -1.22 to -0.40 W, median -0.44 W: the law reads 0.4-1.2 W above the card's rest on this day.
- **The twins** (rgm136's gemmL at each W and X pair's shape; MM1-v1's error as measured / forecast - 1, wall cycles and J over idle with the seconds forecast): in MM1-v1's fit (E206 arm A): w04m +2.4% / +0.2%, w06m -4.5% / -1.7%, w07m -4.7% / -2.5%, w10m -3.9% / -2.0% (rms 4.0% / 1.8%); run in E207 before E211: w01m +1.4% / +8.6%, w02m -0.7% / -0.1%, w09m -3.8% / -1.8% (rms 2.4% / 5.1%); never run before E211: w03m +5.4% / +1.6%, w05m -4.0% / -0.5%, w08m -0.0% / -0.4%, x01m +5.6% / +0.9%, x02m -2.6% / -1.6% (rms 4.1% / 1.1%); all 12: rms 3.69% / 2.84%.

## 8. Dated clauses (Tue 17 Nov 2026, PST)

1. **The outputs, now committed.** The README's line "The scorer's outputs follow after the data commit (a later lane)" and dated note 2's "The scorer's output is committed beside this directory by a later lane" are answered by this note's two output files.
2. **T4 and A1** (the card lane's finding, medium). At the controls, where MM1 and every other model forecast a ratio of 1, rgm211 ran 2.9% and 5.8% fewer wall cycles than rgm136. A1 applies only when T4 fails, both controls lie on one side of 0, |a - b| <= 0.005 and |c_hat| <= 0.03. Here both lie below 0, but |a - b| is 0.0306 and |c_hat| 0.0443: two of A1's conditions fail, and the scorer's A1 line names the first it checks. The offsets are larger than the desk estimate A1 clause 1 gave before the data (about -0.4% to -1.5% at x01), and A1 clause 1 stated before the data why the controls can differ: they compare two compiled loops. The kit's simulator record (`logs/simcheck-e211.txt`, committed with the kit) also counted rgm211's loop at fewer steps an op than rgm136's (32.762 against 47.742, the scorer's constants). So E211's ratio rules read the walk swap and the code difference together and cannot part them, and the registered words stand: W1, W2 and H1-H3 are "not a model test". The absolute rules (T1-T3, E1-E4, H4-H6) and family C carry no such label. E211.md's T4 row words the label "the controls failed: not a model test"; the scorer prints Amendment A1's label in `rules-e211.json`, "the controls did not pass: not a model test": one meaning, two wordings.
3. **The control-corrected reading is REPORTED only** (section 4): W1 FAIL 5/10, W2 FAIL, H1-H3 NOT DECIDED. It is never a verdict while A1 does not apply, as A1 registers.
4. **Step 13 beside E210's scores commit** (the card lane's finding, low). The lab clone held E210's five scores files, untracked, when step 13 began (5 status lines at 13:42:02), and the lane scores-e210 committed them as `d203e577` at 13:42:03, during step 13's calls. Call 2 read only this directory (clean), call 3 read every entry of this directory's list OK and call 4 read HISTORY OK; the scorer opens five files (this lane's audited re-run), none under E210's directory; and the fresh-tree re-run from `38aaf004`'s objects gives the same bytes. So the outputs are the frozen scorer's on the committed data.
5. **verify-e211d's four findings** (wording only) were answered by dated note 2 (`0307eaaf`); this note's per-pair readings (section 4) agree with note 2's table in every closer and every d. The card lane's own result named per-pair winners with a tie of 0; note 2 section 1 corrected them (w01 F1 / NC / tie, w03 MM1 / MM1 / tie), and section 4 here reads the same.
6. **MM1-v2 (H7 NOT REGISTERED).** MM1-v2's E211 column, frozen in `89aa0c94` (pushed 08:12:57 PST, before the booking and before any E211 datum), is scored outside E211's rules by the lane score-v2-e211 (`d38f148c`, REPORTED); section 6 shows it beside MM1-v1, REPORTED, and this lane's code reproduces that commit's aggregates. No E211 rule reads it.
7. **Step 6n's keys** (the card lane's FINDING 1; dated note 1): note 1 stands. No point's label changes, and the scorer's verdicts are read on blind forecasts.
8. **The model session's sealed forecast of E211** (registered under `tools/claims-v3/sealed-e211/` in `51d74428`, before the booking): no E211 rule scores it, and this note quotes no number of it.

## 9. NOT RUN

- The scorer's stand-in self-test by this lane (it ran at step 2, 13:19:51 PST, rc 0, and in verify-e211d's re-run: SELFTEST PASS).
- A re-derivation from the raw session files by this lane: it started from `data-e211.json` (verify-e211d re-derived it: 284 fields equal); verify-e211d's code was read and its outputs compared, not re-run.
- Any read of aifoundry1 or aifoundry3, and any card, device or simulator command.
- A scan for private numbers.
- The model session's sealed forecasts: never read, not scored.

SPDX-License-Identifier: Apache-2.0
