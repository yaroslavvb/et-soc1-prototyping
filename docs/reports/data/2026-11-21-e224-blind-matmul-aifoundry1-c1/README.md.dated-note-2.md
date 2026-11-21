# E224 arm A data, dated note 2: the frozen scorer's output beside the data byte for byte, and THE PICK as E222's committed scores give it - MM1-v3.3 = MM1-v3.2 + AF4; every verdict labelled R0 FAIL; S6 PASS; T1, T2, T3, E4 PASS, E1, E2, E3 FAIL; H1-H9 (MM1-v3.3 against MM1-v3.2) TOO FEW; H10 NOT DECIDED, H11 NOT DECIDED, H12 TOO FEW (MM1-v3.2 against MM1-v3); with verify-e224d's re-derivation beside each result

*Sat 21 Nov 2026 (week 47), PST; written from about 02:40 PST by round Q237's lane `scores-e224` at the desk on aifoundry2 (no card, no simulator, no device opened), under `/usr/bin/python3` 3.12.3 (`-I -B`), each numerical step single-threaded inside the round's CPU slots. It comes after this directory's data commit `96528ad2` (committed 00:49:45 PST, pushed 00:49:50 PST), after E222's scores commit `c661275c` (01:57:49 PST: THE PICK), after the day's data verifier `verify-e224d` (HOLDS WITH FIXES, 02:01 PST: both arms re-derive exactly from their raw records, its own scorer equals both card lanes' scorer files and the frozen scorer's two-arm run, and the fixes it asks for are two dated notes) and after its fix lane `fix-e224d` (FIXED: commit `d1516001`, 02:27:39 PST, this directory's dated note 1). This note adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, nothing is dropped or re-chosen, and nothing is scored but by the frozen scorer's own registered call. The pooled rules over both arms (HP1-HP12, SW) are dated note 20 of arm B's data directory, [`2026-11-21-e224-blind-matmul-aifoundry2/README.md.dated-note-20.md`](../2026-11-21-e224-blind-matmul-aifoundry2/README.md.dated-note-20.md); the other arm's scores are in arm B's data directory [`2026-11-21-e224-blind-matmul-aifoundry2/`](../2026-11-21-e224-blind-matmul-aifoundry2/) (its dated note 19).* **Labels:** **BLIND** (every forecast E224 scores was frozen before either arm's first device access: reg-e224's `FROZEN.txt` at 15:45:11 PST Fri 20 Nov 2026 (sha256 `54277e52...`, posted on the owner's coordination thread as E224's freeze line before any E222 datum), then E224's registration `7de83360` (committed 21:52:25 PST, pushed 21:52:30 PST) with the eight compositions' and MM1-v3.1's, MM1-v3's and MM1-v2's forecasts, the points, the bands, the rules and the scorer, and the kit `0fb6eb95` (21:57:24 PST); the model session's sealed forecast was registered in `71d217b8` (committed 23:27:36 PST), before either arm's first card command (arm A's session from 00:05:29 PST, arm B's from 00:10:10 PST Sat 21 Nov). **THE PICK is not chosen here:** it is E222's registered selection rule's output on E222's own data (aifoundry3 card 0), read by the frozen scorer from E222's committed scores, and every composition it could pick was frozen before any E222 datum); **R0 FAIL** on every verdict of this arm (section 4); the REPORTED parts are never verdicts; the readings beside them are **post hoc**.

## 1. The files this note adds

6 new files. The first 2 are runbook step 13's outputs, copied byte for byte from the card lane's run folder (RB_OUT); the next two are the frozen scorer's same registered call made again by this lane once E222's scores were committed (section 3).

| file | what | bytes | sha256 | label |
|---|---|---|---|---|
| `scores-e224-A.json` | runbook step 13's frozen scorer [`tools/claims-v3/e224/score_e224.py`](../../../../tools/claims-v3/e224/score_e224.py) (`c851f3b4...`) on `data-e224a.json` with step 6n's `labels-e224.json`, the lab at the data commit: THE PICK read NO PICK, so the MM1-v3.3 rules read PENDING; R0, S6, H10-H12, every model's bands, the REPORTED head-to-heads, the switch rule and the family table scored | 49,840 | `610dcd74c395ccaf...` | BLIND (its REPORTED parts never verdicts) |
| `scores-e224-A.txt` | its printed lines: the step's capture of the scorer's call, which the step copies (55 lines) | 1,263 | `8d8cf9aa3eb5a7ca...` | printed lines |
| `scores-e224-A-picked.json` | the same call again, unchanged, with the lab holding E222's committed scores (`c661275c`): THE PICK read, and every MM1-v3.3 rule of this arm scored | 86,369 | `63ccfc1bd17f06fd...` | BLIND (scored after the pick; the forecasts frozen before it) |
| `scores-e224-A-picked.txt` | its printed lines (55 lines) | 1,443 | `d3c6dda5fef2e738...` | printed lines |
| `README.md.dated-note-2.md` | this note | - | - | dated note |
| `SHA256SUMS-note2` | the 5 files above, then `README.md`, `SHA256SUMS` and `SHA256SUMS-note1` as committed (8 lines: with the earlier lists every file here is in a list but this one) | - | - | - |

## 2. Where they come from: step 13 on the data commit (this lane's desk checks)

- **The step.** The card lane `card-e224a` ran the kit's step 13, [`tools/claims-v3/e224/rb/s24_score_e224a.sh`](../../../../tools/claims-v3/e224/rb/s24_score_e224a.sh) `A` (in the kit's list `SHA256SUMS-e224-kit`), inside a CPU slot after the data commit (the round's slot log: one job, slot 1, 00:49:56 PST, ended rc 0 at 00:49:57). The runbook log's last six lines are the step's six calls, each rc 0 and all from one process: (1) the data directory committed: `96528ad2d E224 arm A data: ...`; (2) the directory clean: nothing printed; (3) the data's `SHA256SUMS`: 577 of 577 entries OK; (4) the history check: "HISTORY OK: HEAD descends from the registration 7de833605903 (subtree a46c1682); 123 additions and nothing else under tools/claims-v3/e224 since it; ..."; (5) step 6n's labels: "LABELS-OK: 0 label(s) of arm A's registered points (none)"; (6) the frozen scorer with `--lab` (the lab clone), `--a data-e224a.json --a-tag A --labels labels-e224.json`, whose printed lines (below) are `scores-e224-A.txt` and whose JSON is `scores-e224-A.json`. The six commands are exactly those `s24_score_e224a.sh A` writes.
- **The lab it read.** `96528ad2` was committed at 00:49:45 PST and pushed by 00:49:50 PST. The lab clone's reflog holds HEAD at `96528ad2` from 00:49:45 to its next move at 00:55:55 PST (arm B's data commit), so the step read the lab there, before any E222 score existed: its JSON's pick record reads NO PICK ("no committed scores-e222*.json in a docs/reports/data folder naming e222", HEAD `96528ad2`), and the MM1-v3.3 rules PENDING, as the registration says.
- **The scorer and its inputs, at their pins.** `score_e224.py` is `c851f3b4...` at `96528ad2` and at HEAD, and E220's `score_e220.py` (its pinned readers) `3c771990...`. The scorer refuses (exit 4) unless `points-e224.json`, `forecast-e224.json` and `rules-e224.json` read the sha256 the registration's list records; each does (`44c790ff`, `31b1202c`, `90019f89`). The step's scripts `rb/s24_score_e224a.sh`, `rb/rb_e224a.sh`, `rb/check_history_e224a.py` and `desk/neverrun_card_e224.py` read their kit-list sha256 there. From the lab's top, `sha256sum -c` reads `SHA256SUMS-e224-registration` 31 of 31 and `SHA256SUMS-e224-kit` 120 of 120 at HEAD; the kit's folder and `tools/claims-v3/e224-notes/` are unchanged from `96528ad2` to HEAD.
- **This directory since.** Every file of the data commit is unchanged at HEAD; the only additions are fix-e224d's six files (dated note 1, its desk check's code, text and JSON, the manifest list, `SHA256SUMS-note1`).
- **The labels.** Step 6n's committed `labels-e224.json` names no point (`"ran_before_points": {"A": []}`).
- **The bytes and the times.** The scorer wrote its JSON and text at 00:49:57.005 PST into its own output folder in RB_OUT, and the step copied both into RB_OUT's `scores-e224-A.json` and `.txt` at 00:49:57.016; the copies are byte for byte the scorer's, and the text is the step's capture 6 byte for byte. The JSON is in `main()`'s dump form (one-space indent, sorted keys), and the text is `main()`'s lines from its verdicts. The two sha256 are the ones card-e224a's result names. The slot log shows no run of the scorer on an arm's data before this step.
- **Made again.** This lane ran call 6 again, unchanged and in a CPU slot, on a tree exported from the lab clone's own objects at `96528ad2`, with the scorer's `--lab` a no-checkout scratch clone of the lab whose HEAD and index were moved to `96528ad2`: the JSON, the text and the printed lines came out byte for byte equal to RB_OUT's and to the step's capture. verify-e224d re-derived every field of it with its own code (section 11).

**The scorer's printed lines at the data commit** (`scores-e224-A.txt`, all of it):

```
A:E1: PENDING (NO PICK)
A:E2: PENDING (NO PICK)
A:E3: PENDING (NO PICK)
A:E4: PENDING (NO PICK)
A:H1: PENDING (NO PICK)
A:H10: NOT DECIDED [labelled: R0 FAIL]
A:H11: NOT DECIDED [labelled: R0 FAIL]
A:H12: TOO FEW [labelled: R0 FAIL]
A:H2: PENDING (NO PICK)
A:H3: PENDING (NO PICK)
A:H4: PENDING (NO PICK)
A:H5: PENDING (NO PICK)
A:H6: PENDING (NO PICK)
A:H7: PENDING (NO PICK)
A:H8: PENDING (NO PICK)
A:H9: PENDING (NO PICK)
A:R0: FAIL
A:S6: PASS
A:T1: PENDING (NO PICK)
A:T2: PENDING (NO PICK)
A:T3: PENDING (NO PICK)
B:E1: NO DATA
B:E2: NO DATA
B:E3: NO DATA
B:E4: NO DATA
B:H1: NO DATA
B:H10: NO DATA
B:H11: NO DATA
B:H12: NO DATA
B:H2: NO DATA
B:H3: NO DATA
B:H4: NO DATA
B:H5: NO DATA
B:H6: NO DATA
B:H7: NO DATA
B:H8: NO DATA
B:H9: NO DATA
B:R0: NO DATA
B:T1: NO DATA
B:T2: NO DATA
B:T3: NO DATA
P:HP1: PENDING (NO PICK)
P:HP10: NOT DECIDED [labelled: R0 FAIL]
P:HP11: NOT DECIDED [labelled: R0 FAIL]
P:HP12: TOO FEW [labelled: R0 FAIL]
P:HP2: PENDING (NO PICK)
P:HP3: PENDING (NO PICK)
P:HP4: PENDING (NO PICK)
P:HP5: PENDING (NO PICK)
P:HP6: PENDING (NO PICK)
P:HP7: PENDING (NO PICK)
P:HP8: PENDING (NO PICK)
P:HP9: PENDING (NO PICK)
P:SW: PASS [labelled: R0 FAIL]
PICK: NO PICK (no committed scores-e222*.json in a docs/reports/data folder naming e222)
```

The `B:` lines read NO DATA: this call had no arm B input. **The `P:` lines are arm A alone, not the registered pooled reading** (clause 4 of section 12).

## 3. THE PICK, as E222's committed scores give it

The words: "MM1-v3.3 := the composition E222's registered SELECTION RULE picks"; "The scorer reads the pick from E222's committed scores and never from anything else": "every file named `scores-e222*.json` in a `docs/reports/data/` folder whose name holds `e222`, as committed at the lab's HEAD". Without them "the MM1-v3.3 rules read PENDING until E222's scores are committed (a dated note says which), and the rest is scored"; "E222's own label (R0 or S6 FAIL) rides with the pick into every MM1-v3.3 verdict". E222's rule: "MM1-v3.3 = MM1-v3.2 plus every candidate term whose HC test reads '<candidate> BETTER' and whose NH test reads PASS"; "A NOT DECIDED or TOO FEW leaves that term out."

E222's two committed scores files (`scores-e222-A.json`, `scores-e222-cx.json` in [`2026-11-21-e222-blind-matmul-aifoundry3/`](../2026-11-21-e222-blind-matmul-aifoundry3/), committed in `c661275c` at 01:57:49 PST Sat 21 Nov, after both E224 arms' step 13 at 00:49:57 and 00:56:31) both read SEL **'MM1-v3.3 = MM1-v3.2 + AF4'** with no E222 label (E222's R0 and S6 PASS): HC-AF4 'MM1-v3.2 + AF4 BETTER' (12/2/0, p 0.0129) with NH-AF4 PASS; HC-posimb NOT DECIDED (5/3/2, p 0.727) and HC-L3S NOT DECIDED (9/4/5, p 0.267), so posimb and L3S stay out (E222's dated note 1 in that folder). So **MM1-v3.3 = MM1-v3.2 + AF4**, the composition the frozen scorer maps that string to (its `SEL_TO`): AF4 "at rgm136's gemmLnc points (F3 replaced by dW = S (c1 dup + c2 R4), c1 236.3, c2 597.3 pJ)", MM1-v3.2 everywhere else. On this arm its frozen forecasts differ from MM1-v3.2's at 5 points (d29, d30, g01, g02, g03), and only in energy (section 6).

**The picked run.** This lane ran the step's own scorer call again, unchanged and in a CPU slot, on a tree exported at HEAD (`d1516001`), with the scorer's `--lab` the scratch clone moved to `c661275c`: `scores-e224-A-picked.json` and `.txt`. Its pick record names the two E222 files, SEL 'MM1-v3.3 = MM1-v3.2 + AF4', E222's label none, HEAD `c661275c`; its arm A block equals the two-arm run's (dated note 20) in every field; the same call with the lab at HEAD (`d1516001`) gives the same bytes but for the pick record's `lab_head`. Every pick-independent field (R0, S6, H10-H12, every model's bands, the REPORTED head-to-heads, the switch rule, the family table) is the same as in the step's file. Its printed lines:

```
A:E1: FAIL [labelled: R0 FAIL]
A:E2: FAIL [labelled: R0 FAIL]
A:E3: FAIL [labelled: R0 FAIL]
A:E4: PASS [labelled: R0 FAIL]
A:H1: TOO FEW [labelled: R0 FAIL]
A:H10: NOT DECIDED [labelled: R0 FAIL]
A:H11: NOT DECIDED [labelled: R0 FAIL]
A:H12: TOO FEW [labelled: R0 FAIL]
A:H2: TOO FEW [labelled: R0 FAIL]
A:H3: TOO FEW [labelled: R0 FAIL]
A:H4: TOO FEW [labelled: R0 FAIL]
A:H5: TOO FEW [labelled: R0 FAIL]
A:H6: TOO FEW [labelled: R0 FAIL]
A:H7: TOO FEW [labelled: R0 FAIL]
A:H8: TOO FEW [labelled: R0 FAIL]
A:H9: TOO FEW [labelled: R0 FAIL]
A:R0: FAIL
A:S6: PASS
A:T1: PASS [labelled: R0 FAIL]
A:T2: PASS [labelled: R0 FAIL]
A:T3: PASS [labelled: R0 FAIL]
B:E1: NO DATA
B:E2: NO DATA
B:E3: NO DATA
B:E4: NO DATA
B:H1: NO DATA
B:H10: NO DATA
B:H11: NO DATA
B:H12: NO DATA
B:H2: NO DATA
B:H3: NO DATA
B:H4: NO DATA
B:H5: NO DATA
B:H6: NO DATA
B:H7: NO DATA
B:H8: NO DATA
B:H9: NO DATA
B:R0: NO DATA
B:T1: NO DATA
B:T2: NO DATA
B:T3: NO DATA
P:HP1: TOO FEW [labelled: R0 FAIL]
P:HP10: NOT DECIDED [labelled: R0 FAIL]
P:HP11: NOT DECIDED [labelled: R0 FAIL]
P:HP12: TOO FEW [labelled: R0 FAIL]
P:HP2: TOO FEW [labelled: R0 FAIL]
P:HP3: TOO FEW [labelled: R0 FAIL]
P:HP4: TOO FEW [labelled: R0 FAIL]
P:HP5: TOO FEW [labelled: R0 FAIL]
P:HP6: TOO FEW [labelled: R0 FAIL]
P:HP7: TOO FEW [labelled: R0 FAIL]
P:HP8: TOO FEW [labelled: R0 FAIL]
P:HP9: TOO FEW [labelled: R0 FAIL]
P:SW: PASS [labelled: R0 FAIL]
PICK: PICKED: MM1-v3.3 = MM1-v3.2 + AF4
```

Its `B:` lines read NO DATA and **its `P:` lines are arm A alone** (clause 4).

## 4. The registered rules' words, and the verdicts (BLIND; every one labelled R0 FAIL)

**R0 and S6.** The words: R0 "(every check of C exact or approx; the smoke good)" and, arm A, S6 "(every kept run at 590-610 MHz): a FAIL labels every other verdict of its arm and the pooled ones". Arm A: **R0 FAIL**: the scorer's four failures are checks of C read 'wrong' at `p3a run 35`, `p3a run 76`, `p3b run 8` and `p3b run 92`, family P's two fp16 pattern points at `gemmL1x1x25` (p3a, E212's tile `fld16_mant`; p3b, E217's tile `h_th_in`); their random and zeros twins passed (measured). fix-e224d's dated notes (commit `d1516001`, 02:27:39 PST) read the four checks at the desk: "the host's fixed check of C at K 25,600 against an fp32 accumulation that drops low bits, read at the desk, no wrong GEMM shown (NOT TESTED on a card)" (post hoc, REPORTED); verify-e224d's words: "It is the check failing, not a wrong GEMM." R0 stays FAIL by its registered words and labels every verdict; nothing is dropped. The frozen reader records a wrong check for R0 and keeps the run's readings (E220's pinned `read_a`), so p3a and p3b stay in the energy rules and the switch rule. **S6 PASS** (every kept run at 590-610 MHz; this directory's README: "23,521 of 23,521 samples at 600 MHz", measured).

**MM1-v3.3's per-case and per-point rules.** The words: "each passes when |measured / forecast - 1| is within its band; a rule PASSES with at least 90% of its scored cases or points, FAIL otherwise, TOO FEW under 10, NO DATA with none; PENDING with no pick"; the bands are E220's for these two cards, "2 x the larger of its LOEO error without twins over every point and over the card's points, rounded up to a whole percent". "Points under 3 W over idle are scored in watts in E1 and E2: |W measured - W forecast| <= 0.52 W on both arms. Time is scored at the time-scored points only (family P's zeros and pattern points share their random twin's time case)." The ties on this arm: cycles 0.005 in ln, joules 0.01 in ln, watts points 0.05 W. Watts cells here (E1, E2): d25, d26, y1a, y1b, y2a, y2b, y3a, y3b.

| rule | quantity | band | passes / scored (needed) | MM1-v3.3's verdict | MM1-v3.2's (REPORTED) | the misses by family | the misses (measured / forecast - 1; a watts cell: measured - forecast) |
|---|---|---|---|---|---|---|---|
| **T1** | wall cycles an op | 12% | 48 / 52 (47) | **PASS** | PASS 48/52 | L/AF4-NB56 3, L/posimb-pair 1 | g01 +12.17%, g02 +19.69%, g03 +15.73%, y2b -12.83% |
| **T2** | the counter's mean cycles an op | 14% | 50 / 52 (47) | **PASS** | PASS 50/52 | L/AF4-NB56 2 | g02 +19.88%, g03 +16.10% |
| **T3** | seconds a GEMM | 12% | 47 / 52 (47) | **PASS** | PASS 47/52 | D/D-G-mid 1, L/AF4-NB56 3, L/posimb-pair 1 | d29 +13.05%, g01 +12.21%, g02 +20.13%, g03 +15.31%, y2b -12.75% |
| **E1** | J over idle given the measured op time | 12% (watts cells 0.52 W) | 56 / 64 (58) | **FAIL** | FAIL 55/64 | D/D-G-L2 1, D/D-G-mid 1, D/D-L2 1, L/AF4-NB56 2, P/P-a 2, P/P-b 1 | d05 -19.91%, d29 +12.45%, d30 -14.60%, g01 +27.99%, g02 +37.16%, p3a -12.00%, p4a -18.50%, p4b -18.91% |
| **E2** | J over idle with seconds forecast | 12% (watts cells 0.52 W) | 56 / 64 (58) | **FAIL** | FAIL 55/64 | D/D-G-L2 1, D/D-G-mid 1, D/D-L2 1, L/AF4-NB56 2, P/P-a 2, P/P-b 1 | d05 -19.69%, d29 +14.40%, d30 -14.56%, g01 +29.29%, g02 +39.84%, p3a -12.45%, p4a -18.77%, p4b -19.14% |
| **E3** | J at rest given the measured op time | 4% | 55 / 64 (58) | **FAIL** | FAIL 55/64 | D/D-G-L2 1, D/D-G-mid 1, L/AF4-NB56 3, P/P-a 3, P/P-b 1 | d29 +5.38%, d30 -6.57%, g01 +10.69%, g02 +13.71%, g03 +4.15%, p1a -4.03%, p3a -4.19%, p4a -4.94%, p4b -5.57% |
| **E4** | J at rest with seconds forecast | 10% | 58 / 64 (58) | **PASS** | PASS 58/64 | D/D-G-mid 1, L/AF4-NB56 3, L/posimb-pair 2 | d29 +13.67%, g01 +19.16%, g02 +28.17%, g03 +13.06%, y2b -12.96%, y3b -10.94% |

Every miss is listed by its point id and counted by its family and subfamily (`points-e224.json`); the cell figures are the scorer's (`scores-e224-A-picked.json` > `arms` > `A` > `T1`...`E4` > `cells`). MM1-v3.2's column is REPORTED (its own bands, as the scorer's `bands_REPORTED_every_model` holds them).

**Where the pick and MM1-v3.2 part** (REPORTED, post hoc; a point 'lost' passes under MM1-v3.2 and misses under MM1-v3.3, a point 'gained' the other way): E1 loses no point and gains g03; E2 loses no point and gains g03.

**At or next to the line** (exact as registered; each stands): **T1** PASS 48/52 with 47 needed; its closest pass d29 at +11.997% against 12%, its closest miss g01 at +12.169% against 12%; **T3** PASS 47/52 with 47 needed; its closest pass y3b at -10.778% against 12%, its closest miss g01 at +12.207% against 12%; **E4** PASS 58/64 with 58 needed; its closest pass d15 at +8.419% against 10%, its closest miss y3b at -10.943% against 10%.

## 5. The head-to-heads (BLIND)

The words: per case or point "d = |ln(measured / second)| - |ln(measured / first)|", "decided when |d| exceeds the arm's tie (cycles 0.005 in ln, joules 0.01 in ln, watts 0.05 W on arm A and 0.1 W on arm B: E220's ties); the exact two-sided sign test over the decided: '<first> BETTER' at p < 0.05 with at least 8 decided, else NOT DECIDED; TOO FEW under 8." H1-H9 / HP1-HP9, MM1-v3.3 against MM1-v3.2 "on all points (H1 wall, H2 W given t, H3 J at rest given t), family D alone (H4-H6) and family L alone (H7-H9), per arm and pooled (each case with its own arm's tie)"; H10-H12 / HP10-HP12, MM1-v3.2 against MM1-v3 "on all points, the same three quantities".

| rule | first against second | scope | quantity | first closer / second closer / ties | n | p | the scorer's verdict | verify-e224d (own code) |
|---|---|---|---|---|---|---|---|---|
| **H1** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | wall | 0/0/52 | 52 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H2** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | Wg | 2/2/60 | 64 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H3** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | JRg | 2/2/60 | 64 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H4** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | wall | 0/0/30 | 30 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H5** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | Wg | 1/0/29 | 30 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H6** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | JRg | 1/0/29 | 30 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H7** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | wall | 0/0/18 | 18 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H8** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | Wg | 1/2/15 | 18 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H9** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | JRg | 1/2/15 | 18 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H10** | MM1-v3.2 against MM1-v3 | all | wall | 15/12/25 | 52 | 0.701 | **NOT DECIDED [labelled: R0 FAIL]** | the same counts, p and verdict |
| **H11** | MM1-v3.2 against MM1-v3 | all | Wg | 20/9/27 | 56 | 0.0614 | **NOT DECIDED [labelled: R0 FAIL]** | the same counts, p and verdict |
| **H12** | MM1-v3.2 against MM1-v3 | all | JRg | 5/0/51 | 56 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |

Stated before the data: "Per arm almost every H1-H9 reads TOO FEW by construction." On time, "every pick's power is at most 0.09: a NOT DECIDED or TOO FEW there says the models' time forecasts are within their errors of each other, not that they are equally good"; on energy "(HP2, HP3) a pick holding AF4 can decide on its ten gemmLnc points (power 0.35-0.67)". On this arm MM1-v3.3 and MM1-v3.2 differ by more than the tie at 4 of 64 points in W over idle and at none in wall cycles (H1 0/0/52): H1-H9 read TOO FEW, as the registration's power table said they would.

## 6. MM1-v3.3 against MM1-v3.2 where AF4 acts (REPORTED; the cases behind H2)

| point | family | what | measured W over idle | MM1-v3.2's W given t (ln error) | MM1-v3.3's (ln error) | closer (H2's rule) |
|---|---|---|---|---|---|---|
| d29 | D/D-G-mid | gemmLnc1x3x13.fp32.random.rgm136-gemmLnc | 24.35 W | 19.17 W (+0.2390) | 21.65 W (+0.1173) | MM1-v3.3 |
| d30 | D/D-G-L2 | gemmLnc2x5x1.int8.random.rgm136-gemmLnc | 19.75 W | 16.85 W (+0.1590) | 23.13 W (-0.1578) | tie |
| g01 | L/AF4-NB56 | gemmLnc3x6x12.fp32.random.rgm136-gemmLnc | 22.49 W | 18.42 W (+0.1998) | 17.57 W (+0.2468) | MM1-v3.2 |
| g02 | L/AF4-NB56 | gemmLnc3x5x12.fp32.random.rgm136-gemmLnc | 22.77 W | 17.54 W (+0.2612) | 16.60 W (+0.3160) | MM1-v3.2 |
| g03 | L/AF4-NB56 | gemmLnc1x5x14.fp32.random.rgm136-gemmLnc | 23.24 W | 17.84 W (+0.2644) | 21.18 W (+0.0927) | MM1-v3.3 |

The point's measured W over idle and each model's W given the measured op time (the scorer's `predicted()`), ln(measured / forecast) in brackets; 'closer' by H2's rule (tie 0.01 in ln). AF4 moves no time forecast at any E224 point (checked at every point and column). Beside it (REPORTED): E220's G2 reading on these two cards, for F3 at its small-excess gemmLnc points: on aifoundry1 card 1 "the measured excess is 1.96-2.69 times F3's", on aifoundry2 card 0 "the measured excess is 1.47-2.15 times F3's"; and of the candidates "no candidate has a card factor".

## 7. Family P's switch-count rule on this arm (REPORTED; the registered reading is pooled, dated note 20)

The words: SW is "registered pooled over both arms for MM1-v3.2" "(its switch counts are the registered inputs; MM1-v3.3 and every composition REPORTED beside, and each arm REPORTED)": "per pattern point Q1 e_V = ln(W measured / V), V the model's W given the measured op time with its counts, against e_N = ln(W measured / N), N the mean over zeros, ones and random of the same model's W given the same op time (cases at 3 W or more)"; "Q2 E210's metric e_D = [(V - V_R) - (W - W_R)] / D, D = W_R - W_Z measured at the shape's random and zeros twins (V_R the model's W given t at the random twin's own op time), against the null's [(N - V_R) - (W - W_R)] / D (cases with D > 0)"; "P1 rms(e_V) < rms(e_N); P2 the exact two-sided sign test on |e_N| - |e_V| (tie 0.01 in ln), the counts closer at p < 0.05 with at least 6 decided; P3 rms(e_D) < the null's; P4 P2's test on Q2 (tie 0.01 of D)"; PASS when P1-P4 hold, FAIL "when P1 or P3 fails or a sign test reads the null closer", NOT DECIDED otherwise.

On arm A, MM1-v3.2 with its counts: **PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.03% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781**. Every model on this arm (REPORTED):

| model | SW (REPORTED but MM1-v3.2's pooled) |
|---|---|
| MM1-v3.2 | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.03% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.2 + posimb | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.03% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.2 + AF4 | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.03% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.2 + L3S | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.02% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.2 + posimb + AF4 | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.03% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.2 + posimb + L3S | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.02% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.2 + AF4 + L3S | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.02% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.2 + all three | PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.02% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3.1 | PASS: Q1 n 8, rms e_V 12.31% vs e_N 35.84% (P1 HOLDS); P2 counts BETTER 8/0/0 p 0.00781; Q2 n 8, rms e_D 16.56% of D vs 42.27% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781 |
| MM1-v3 | NO DATA (no pattern pricing at these points) |
| MM1-v2 | NO DATA (no pattern pricing at these points) |

MM1-v3 and MM1-v2 price no pattern tile, so their rule reads NO DATA; every MM1-v3.2 composition reads as MM1-v3.2, since none of the three terms acts at family P's points.

## 8. Every other composition (REPORTED, never a verdict)

REPORTED, never a verdict: "every composition's bands and its H1-H9 against MM1-v3.2 (the seven not picked); per family (D, P, L) and forecaster the rms and bias of ln(measured / forecast) of the wall cycles and W given t; SW per arm and for every model; route m on arm B; family L's leads read per lead (L3S's edge points' wall errors, posimb's measured ln(wall a / wall b) per pair against each forecaster's, AF4's measured gemmLnc excess against its twin, against F3's and AF4's)".

**The bands** (passes / scored, each with its verdict as the rule reads it):

| model | T1 | T2 | T3 | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|
| MM1-v3.2 | PASS 48/52 | PASS 50/52 | PASS 47/52 | FAIL 55/64 | FAIL 55/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.2 + posimb | PASS 48/52 | PASS 50/52 | PASS 48/52 | FAIL 55/64 | FAIL 55/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.2 + AF4 (THE PICK: registered) | PASS 48/52 | PASS 50/52 | PASS 47/52 | FAIL 56/64 | FAIL 56/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.2 + L3S | PASS 47/52 | PASS 50/52 | PASS 47/52 | FAIL 55/64 | FAIL 55/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.2 + posimb + AF4 | PASS 48/52 | PASS 50/52 | PASS 48/52 | FAIL 56/64 | FAIL 56/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.2 + posimb + L3S | PASS 47/52 | PASS 50/52 | PASS 48/52 | FAIL 55/64 | FAIL 55/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.2 + AF4 + L3S | PASS 47/52 | PASS 50/52 | PASS 47/52 | FAIL 56/64 | FAIL 56/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.2 + all three | PASS 47/52 | PASS 50/52 | PASS 48/52 | FAIL 56/64 | FAIL 56/64 | FAIL 55/64 | PASS 58/64 |
| MM1-v3.1 | PASS 49/52 | PASS 50/52 | PASS 48/52 | FAIL 56/64 | FAIL 56/64 | FAIL 56/64 | FAIL 56/64 |
| MM1-v3 | PASS 49/52 | PASS 50/52 | PASS 48/52 | FAIL 50/56 | FAIL 50/56 | PASS 51/56 | FAIL 49/56 |
| MM1-v2 | FAIL 45/52 | PASS 48/52 | FAIL 45/52 | FAIL 48/56 | FAIL 48/56 | PASS 51/56 | FAIL 49/56 |

**H1-H9 against MM1-v3.2** (first closer / MM1-v3.2 closer / ties; 'first BETTER' = the composition):

| composition (first) against MM1-v3.2 | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | H9 |
|---|---|---|---|---|---|---|---|---|---|
| MM1-v3.2 + posimb | TOO FEW 4/1/47 | TOO FEW 0/0/64 | TOO FEW 0/0/64 | TOO FEW 0/0/30 | TOO FEW 0/0/30 | TOO FEW 0/0/30 | TOO FEW 4/1/13 | TOO FEW 0/0/18 | TOO FEW 0/0/18 |
| MM1-v3.2 + AF4 (THE PICK: registered) | TOO FEW 0/0/52 | TOO FEW 2/2/60 | TOO FEW 2/2/60 | TOO FEW 0/0/30 | TOO FEW 1/0/29 | TOO FEW 1/0/29 | TOO FEW 0/0/18 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |
| MM1-v3.2 + L3S | MM1-v3.2 BETTER 1/9/42 p 0.0215 | TOO FEW 1/0/63 | TOO FEW 0/0/64 | TOO FEW 0/4/26 | TOO FEW 1/0/29 | TOO FEW 0/0/30 | TOO FEW 1/5/12 | TOO FEW 0/0/18 | TOO FEW 0/0/18 |
| MM1-v3.2 + posimb + AF4 | TOO FEW 4/1/47 | TOO FEW 2/2/60 | TOO FEW 2/2/60 | TOO FEW 0/0/30 | TOO FEW 1/0/29 | TOO FEW 1/0/29 | TOO FEW 4/1/13 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |
| MM1-v3.2 + posimb + L3S | NOT DECIDED 5/10/37 p 0.302 | TOO FEW 1/0/63 | TOO FEW 0/0/64 | TOO FEW 0/4/26 | TOO FEW 1/0/29 | TOO FEW 0/0/30 | NOT DECIDED 5/6/7 p 1 | TOO FEW 0/0/18 | TOO FEW 0/0/18 |
| MM1-v3.2 + AF4 + L3S | MM1-v3.2 BETTER 1/9/42 p 0.0215 | TOO FEW 3/2/59 | TOO FEW 2/2/60 | TOO FEW 0/4/26 | TOO FEW 2/0/28 | TOO FEW 1/0/29 | TOO FEW 1/5/12 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |
| MM1-v3.2 + all three | NOT DECIDED 5/10/37 p 0.302 | TOO FEW 3/2/59 | TOO FEW 2/2/60 | TOO FEW 0/4/26 | TOO FEW 2/0/28 | TOO FEW 1/0/29 | NOT DECIDED 5/6/7 p 1 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |

Where each term acts: posimb "acts at 10 points on arm A and 10 on arm B", L3S "acts at 51 points on arm A and 49 on arm B", AF4 "acts at 5 points on arm A and 5 on arm B" (the registration's count, section 1).

## 9. Each model's error by family (REPORTED)

The rms of ln(measured / forecast), in percent: wall cycles at the time-scored points, W over idle given the measured op time at the points measured at 3 W and above, J at rest given the measured op time (the run's own measured rest); the scorer's `family_stats_REPORTED` rules for the first two, with J at rest and the family 'all' added by the scorer's own functions; each figure equal to verify-e224d's own (n: wall / W / J at rest).

| model | D wall / W given t / J at rest (n) | P | L | all |
|---|---|---|---|---|
| MM1-v3.2 | 4.48 / 7.79 / 2.49 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 8.00 / 12.45 / 4.25 (18/12/18) | 5.89 / 9.56 / 3.17 (52/56/64) |
| MM1-v3.2 + posimb | 4.50 / 7.79 / 2.49 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 7.82 / 12.45 / 4.25 (18/12/18) | 5.81 / 9.56 / 3.17 (52/56/64) |
| MM1-v3.2 + AF4 | 4.48 / 6.72 / 1.95 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 8.00 / 12.16 / 4.10 (18/12/18) | 5.89 / 9.06 / 2.92 (52/56/64) |
| MM1-v3.2 + L3S | 4.63 / 7.81 / 2.49 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 8.12 / 12.47 / 4.26 (18/12/18) | 6.01 / 9.57 / 3.17 (52/56/64) |
| MM1-v3.2 + posimb + AF4 | 4.50 / 6.72 / 1.95 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 7.82 / 12.16 / 4.10 (18/12/18) | 5.81 / 9.06 / 2.92 (52/56/64) |
| MM1-v3.2 + posimb + L3S | 4.65 / 7.81 / 2.49 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 7.94 / 12.47 / 4.26 (18/12/18) | 5.94 / 9.57 / 3.17 (52/56/64) |
| MM1-v3.2 + AF4 + L3S | 4.63 / 6.73 / 1.96 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 8.12 / 12.19 / 4.11 (18/12/18) | 6.01 / 9.07 / 2.93 (52/56/64) |
| MM1-v3.2 + all three | 4.65 / 6.73 / 1.96 (30/28/30) | 3.55 / 9.86 / 2.86 (4/16/16) | 7.94 / 12.19 / 4.11 (18/12/18) | 5.94 / 9.07 / 2.93 (52/56/64) |
| MM1-v3.1 | 4.57 / 14.73 / 5.07 (30/28/30) | 3.02 / 9.04 / 2.68 (4/16/16) | 8.27 / 22.01 / 7.08 (18/12/18) | 6.04 / 15.35 / 5.29 (52/56/64) |
| MM1-v3 | 4.57 / 14.82 / 5.09 (30/28/30) | 2.97 / 4.13 / 1.16 (4/8/8) | 8.18 / 21.92 / 7.06 (18/12/18) | 5.99 / 15.85 / 5.49 (52/48/56) |
| MM1-v2 | 6.09 / 16.97 / 5.59 (30/28/30) | 3.12 / 8.24 / 1.48 (4/8/8) | 9.30 / 21.46 / 6.92 (18/12/18) | 7.22 / 17.16 / 5.69 (52/48/56) |

## 10. The leads, read per lead (REPORTED, never verdicts)

- **posimb's equal-count layout pairs** (measured ln(wall a / wall b) against each forecaster's): y1 measured +0.0836, 'MM1-v3.2 + posimb' +0.0206, MM1-v3.2 +0.0000, MM1-v3.1 +0.0000, MM1-v3 +0.0000; y2 measured +0.1471, 'MM1-v3.2 + posimb' +0.0434, MM1-v3.2 +0.0000, MM1-v3.1 +0.0000, MM1-v3 +0.0000; y3 measured +0.1311, 'MM1-v3.2 + posimb' +0.0406, MM1-v3.2 +0.0000, MM1-v3.1 +0.0000, MM1-v3 +0.0000. The measured layout effect has posimb's sign at all three pairs and is 3.2-4.1 times its size; MM1-v3.2, MM1-v3.1 and MM1-v3 predict no difference.
- **AF4's gemmLnc points against their cooperative twins** (the measured excess W(g) - W(gt) at the measured op times, against F3's, MM1-v3.2's, and AF4's): g01 measured 22.49 W against its twin's 16.32 W (excess +6.17 W); F3's (MM1-v3.2) +1.28 W, AF4's +0.44 W; g02 measured 22.77 W against its twin's 16.02 W (excess +6.75 W); F3's (MM1-v3.2) +1.49 W, AF4's +0.55 W; g03 measured 23.24 W against its twin's 15.79 W (excess +7.45 W); F3's (MM1-v3.2) +1.51 W, AF4's +4.85 W.
- **L3S's L3 edges** (ln(measured / forecast) of the wall cycles, MM1-v3.2 / 'MM1-v3.2 + L3S'): e01 -0.0219 / -0.0328; e02 -0.0275 / -0.0378; e03 -0.0170 / -0.0307; e04 -0.0399 / -0.0512; e05 -0.0738 / -0.0784; e06 +0.0206 / +0.0206; rms over the six 3.87% / 4.59%.

## 11. verify-e224d's re-derivation, beside (its own code; verdict HOLDS WITH FIXES)

verify-e224d re-derived this arm from its raw records with its own code (945 of 945 run fields), scored every rule with its own scorer, and found it equal to both card lanes' scorer files (1,559 of 1,559 values, pick-independent) and to the frozen scorer run with both arms at `c661275c` (1,662 of 1,662; the pick's rules 237 of 237). This lane's checks of the same files: the provenance by the runbook logs 76 of 76 OK; step 13 and the picked and pooled runs made again from committed bytes, 35 comparisons SAME, none different; the facts 45 of 45 OK (every band, cell, head-to-head, switch-rule case and family figure re-made by the frozen scorer's own functions equal to its JSON and to verify-e224d's own scorer and leads).

## 12. Findings, answered as dated clauses (Sat 21 Nov 2026, after the data; post hoc; nothing re-scored)

1. **info, THE PICK came after step 13.** E222's scores were committed at 01:57:49 PST, after both arms' step 13 (00:49:57 and 00:56:31), so the card lanes' scorer files read NO PICK and every MM1-v3.3 rule PENDING, as the lab stood then (verify-e224d's finding 5). **Answered here:** the step's files are committed unchanged, and the same registered call made with the lab holding E222's scores is committed beside them (`scores-e224-A-picked.*`, section 3); the pooled rules are dated note 20. *Fix for future kits:* none needed (the registration foresaw it).
2. **medium, R0 FAIL (verify-e224d's finding 1; card-e224a's open issue).** Answered by dated note 1 of this directory (section 2): the host's fixed tolerance against an accumulation that drops low bits at 800 k-tiles, read at the desk, post hoc, NOT TESTED on a card. R0 stays FAIL by its registered words and labels every verdict here; nothing is dropped. *Fix for future kits:* scale the check's tolerance with K, or check pattern tiles at small K only (dated note 1's suggestion).
3. **low, the session manifest (verify-e224d's finding 2).** Answered by dated note 1, section 3 (215 of 562 lines fail by the scrub alone).
4. **info, the one-arm files' `P:` lines.** Both of this arm's scorer files hold `P:HP1`-`P:HP12` and `P:SW` lines computed from arm A alone (the frozen scorer pools whatever arms it is given; their HP10-HP12 counts are this arm's H10-H12). They are not the registered pooled reading, which is dated note 20's two-arm run. The kit's step-13 script says so ("arm B's and the pooled rules NO DATA or arm A's alone in this file").
5. **info, H1-H9 TOO FEW.** As the registration's power table said before the data, the three terms barely act at E224's points: on this arm MM1-v3.3 and MM1-v3.2 differ by more than a tie at 4 points in energy and at none in time, so no per-arm head-to-head can decide. This says the two models' forecasts are within their errors of each other here, not that AF4 is right or wrong (E224.md section 8). *Fix:* none (E224.md section 8 said so before the data).
6. **info, verdicts at or next to the line.** **T1** PASS 48/52 with 47 needed; its closest pass d29 at +11.997% against 12%, its closest miss g01 at +12.169% against 12%; **T3** PASS 47/52 with 47 needed; its closest pass y3b at -10.778% against 12%, its closest miss g01 at +12.207% against 12%; **E4** PASS 58/64 with 58 needed; its closest pass d15 at +8.419% against 10%, its closest miss y3b at -10.943% against 10%. Each is exact as registered and stands.

## 13. What this note does not do

It changes no committed file, datum, forecast, point, band, tie, rule, label or verdict; it does not re-choose THE PICK, drop a point or lift R0's label; it scores nothing but by the frozen scorer's own registered call; it scores no forecast of the model session's (their seal is registered in `71d217b8` and stays theirs); and it reads no box, card or session folder of theirs.

## 14. `SHA256SUMS-note2`

`SHA256SUMS-note2` lists the 5 files this note adds (this note among them), then `README.md`, `SHA256SUMS` and `SHA256SUMS-note1` as committed; `sha256sum -c SHA256SUMS-note2` from this directory reads every line OK.
