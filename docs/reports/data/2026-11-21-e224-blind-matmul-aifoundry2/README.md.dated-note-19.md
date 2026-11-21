# E224 arm B data, dated note 19: the frozen scorer's output beside the data byte for byte, and THE PICK as E222's committed scores give it - MM1-v3.3 = MM1-v3.2 + AF4; every verdict labelled R0 FAIL; T1, T2, T3, E2 PASS, E1, E3, E4 FAIL; H1-H9 (MM1-v3.3 against MM1-v3.2) TOO FEW; H10 NOT DECIDED, H11 NOT DECIDED, H12 TOO FEW (MM1-v3.2 against MM1-v3); with verify-e224d's re-derivation beside each result

*Sat 21 Nov 2026 (week 47), PST; written from about 02:40 PST by round Q237's lane `scores-e224` at the desk on aifoundry2 (no card, no simulator, no device opened), under `/usr/bin/python3` 3.12.3 (`-I -B`), each numerical step single-threaded inside the round's CPU slots. It comes after this directory's data commit `087f9baa` (committed 00:55:55 PST, pushed by 00:56:17 PST), after E222's scores commit `c661275c` (01:57:49 PST: THE PICK), after the day's data verifier `verify-e224d` (HOLDS WITH FIXES, 02:01 PST: both arms re-derive exactly from their raw records, its own scorer equals both card lanes' scorer files and the frozen scorer's two-arm run, and the fixes it asks for are two dated notes) and after its fix lane `fix-e224d` (FIXED: commit `d1516001`, 02:27:39 PST, this directory's dated note 18). This note adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, nothing is dropped or re-chosen, and nothing is scored but by the frozen scorer's own registered call. The pooled rules over both arms (HP1-HP12, SW) are this directory's dated note 20, [`README.md.dated-note-20.md`](README.md.dated-note-20.md); the other arm's scores are in arm A's data directory [`2026-11-21-e224-blind-matmul-aifoundry1-c1/`](../2026-11-21-e224-blind-matmul-aifoundry1-c1/) (its dated note 2).* **Labels:** **BLIND** (every forecast E224 scores was frozen before either arm's first device access: reg-e224's `FROZEN.txt` at 15:45:11 PST Fri 20 Nov 2026 (sha256 `54277e52...`, posted on the owner's coordination thread as E224's freeze line before any E222 datum), then E224's registration `7de83360` (committed 21:52:25 PST, pushed 21:52:30 PST) with the eight compositions' and MM1-v3.1's, MM1-v3's and MM1-v2's forecasts, the points, the bands, the rules and the scorer, and the kit `0fb6eb95` (21:57:24 PST); the model session's sealed forecast was registered in `71d217b8` (committed 23:27:36 PST), before either arm's first card command (arm A's session from 00:05:29 PST, arm B's from 00:10:10 PST Sat 21 Nov). **THE PICK is not chosen here:** it is E222's registered selection rule's output on E222's own data (aifoundry3 card 0), read by the frozen scorer from E222's committed scores, and every composition it could pick was frozen before any E222 datum); **R0 FAIL** on every verdict of this arm (section 4); the REPORTED parts are never verdicts; the readings beside them are **post hoc**.

## 1. The files this note adds

12 new files. The first 8 are runbook step 13's outputs, copied byte for byte from the card lane's run folder (RB_OUT); the next two are the frozen scorer's same registered call made again by this lane once E222's scores were committed (section 3).

| file | what | bytes | sha256 | label |
|---|---|---|---|---|
| `data-e224b.json` | runbook step 13's reduction: E208's registered reducer [`tools/claims-v3/e208/proposal/src/reduce_mms.py`](../../../../tools/claims-v3/e208/proposal/src/reduce_mms.py) (`b9e32618...`) on the committed `session/` | 1,081,832 | `e5cf09f2b36e61a9...` | measured (reduced) |
| `reduce-e224b.txt` | the reducer's text table | 8,362 | `510efd5218a1b1c1...` | measured (reduced) |
| `reduce.out` | the reducer's printed lines (= `reduce-e224b.txt`) | 8,362 | `510efd5218a1b1c1...` | printed lines |
| `scores-e224.json` | the frozen scorer [`tools/claims-v3/e224/score_e224.py`](../../../../tools/claims-v3/e224/score_e224.py) (`c851f3b4...`) on that reduction (`--b`), the lab at the data commit: THE PICK read NO PICK, so the MM1-v3.3 rules read PENDING; R0, H10-H12, every model's bands, the REPORTED head-to-heads, the switch rule and the family table scored | 50,172 | `d3765f22f6096b10...` | BLIND (its REPORTED parts never verdicts) |
| `scores-e224.txt` | its printed lines (55 lines) | 1,273 | `b90fb44249cb8e86...` | printed lines |
| `score.out` | the scorer's printed lines as the step captured them (= `scores-e224.txt`) | 1,273 | `b90fb44249cb8e86...` | printed lines |
| `post-e224b.json` | [`rb/post_e224b.py`](../../../../tools/claims-v3/e224/rb/post_e224b.py) `after`: arm B's points the scorer leaves out of its rules, named, by family, and the session's stop | 327 | `9e787d78872efc69...` | REPORTED |
| `post.out` | its printed line | 129 | `43d43399517412c0...` | printed lines |
| `scores-e224-B-picked.json` | the scorer's call again, unchanged, with the lab holding E222's committed scores (`c661275c`): THE PICK read, and every MM1-v3.3 rule of this arm scored | 84,770 | `33447a98d6e087f9...` | BLIND (scored after the pick; the forecasts frozen before it) |
| `scores-e224-B-picked.txt` | its printed lines (55 lines) | 1,453 | `e4d8a9f6a688db20...` | printed lines |
| `README.md.dated-note-19.md` | this note | - | - | dated note |
| `SHA256SUMS-note19` | the 11 files above, then `README.md`, `SHA256SUMS` and `SHA256SUMS-note18` as committed (14 lines: with the earlier lists every file here is in a list but this one) | - | - | - |

## 2. Where they come from: step 13 on the data commit (this lane's desk checks)

- **The step.** The card lane `card-e224b` ran the kit's step 13, [`tools/claims-v3/e224/rb/s24_score_e224b.sh`](../../../../tools/claims-v3/e224/rb/s24_score_e224b.sh) (in the kit's list `SHA256SUMS-e224-kit`), inside a CPU slot after the data commit's push (the round's slot log: one job, slot 1, 00:56:30 PST, ended rc 0 at 00:56:31). The runbook log holds one step-13 block, "s24_score_e224b start" at 00:56:30 and "exit 0: scored: ..." at 00:56:31. The card lane's capture of the step prints, in order: the manifest check ("MANIFEST CHECK: 348 of 348 manifest lines OK (1 by THE MASK of E209's kit note 1 (E224's kit): ..."), "the data commit 087f9baae015 (2026-11-21 00:55:55 -0800); HEAD 087f9baae", "reduce_mms.py rc 0", "LABELS-OK: 0 label(s) of arm B's registered points (none)", "score_e224.py rc 0" and the scorer's lines, "post_e224b.py after rc 0" and the readings' line, then exit 0. The scorer's lines in the capture are `score.out` and `scores-e224.txt` byte for byte, the readings' line is `post.out`, and the reducer's printed lines are `reduce-e224b.txt` (`reduce.out`).
- **The lab it read.** `087f9baa` was committed at 00:55:55 PST and was the remote's main by 00:56:17 PST. The lab clone's reflog holds HEAD at `087f9baa` from 00:55:55 to its next move at 00:57:50 PST (E222's data commit), so the step read the lab there, before any E222 score existed: its JSON's pick record reads NO PICK (HEAD `087f9baa`), and the MM1-v3.3 rules PENDING, as the registration says.
- **The tools, at their pins in the data commit.** `score_e224.py` `c851f3b4...`, E220's `score_e220.py` `3c771990...`, E208's `reduce_mms.py` `b9e32618...` and its `mms_common.py` `c3fc7883...`; `points-e224.json`, `forecast-e224.json` and `rules-e224.json` at the registration list's sha256; the step's scripts `rb/s24_score_e224b.sh`, `rb/rb_e224b.sh`, `rb/post_e224b.py`, `collect_e224b.py` and `desk/neverrun_card_e224.py` at the kit list's sha256.
- **This directory since.** Every file of the data commit is unchanged at HEAD; the only additions are fix-e224d's two files (dated note 18 and `SHA256SUMS-note18`).
- **The labels.** The step's `ranbefore-e224b.json` is the committed one byte for byte and names no point (`"ran_before_points": {"B": []}`), so the scorer ran without `--labels`, as the step's script says.
- **The bytes and the times.** The eight files were written inside the step (00:56:31.126-00:56:31.343 PST); RB_OUT's `score/` holds these eight only; the JSON is in `main()`'s dump form and the text its lines; `post-e224b.json` is in `post_e224b.py`'s dump form; the sha256 of `scores-e224.json`, `scores-e224.txt` and `post-e224b.json` are the ones card-e224b's result names.
- **Made again.** This lane ran the step's three calls again, unchanged and in CPU slots, on a tree exported from the lab clone's own objects at `087f9baa`, with the scorer's `--lab` a no-checkout scratch clone of the lab moved to `087f9baa`: the reducer on the committed `session/`, the scorer on its reduction, and the readings after. All eight files came out byte for byte equal to RB_OUT's. verify-e224d re-derived arm B's measured side with its own code (section 11).

**The scorer's printed lines at the data commit** (`scores-e224.txt` = `score.out`, all of it):

```
A:E1: NO DATA
A:E2: NO DATA
A:E3: NO DATA
A:E4: NO DATA
A:H1: NO DATA
A:H10: NO DATA
A:H11: NO DATA
A:H12: NO DATA
A:H2: NO DATA
A:H3: NO DATA
A:H4: NO DATA
A:H5: NO DATA
A:H6: NO DATA
A:H7: NO DATA
A:H8: NO DATA
A:H9: NO DATA
A:R0: NO DATA
A:S6: NO DATA
A:T1: NO DATA
A:T2: NO DATA
A:T3: NO DATA
B:E1: PENDING (NO PICK)
B:E2: PENDING (NO PICK)
B:E3: PENDING (NO PICK)
B:E4: PENDING (NO PICK)
B:H1: PENDING (NO PICK)
B:H10: NOT DECIDED [labelled: R0 FAIL]
B:H11: NOT DECIDED [labelled: R0 FAIL]
B:H12: TOO FEW [labelled: R0 FAIL]
B:H2: PENDING (NO PICK)
B:H3: PENDING (NO PICK)
B:H4: PENDING (NO PICK)
B:H5: PENDING (NO PICK)
B:H6: PENDING (NO PICK)
B:H7: PENDING (NO PICK)
B:H8: PENDING (NO PICK)
B:H9: PENDING (NO PICK)
B:R0: FAIL
B:T1: PENDING (NO PICK)
B:T2: PENDING (NO PICK)
B:T3: PENDING (NO PICK)
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
P:SW: NOT DECIDED [labelled: R0 FAIL]
PICK: NO PICK (no committed scores-e222*.json in a docs/reports/data folder naming e222)
```

The `A:` lines read NO DATA: this call had no arm A input. **The `P:` lines are arm B alone, not the registered pooled reading** (clause 4 of section 12). The readings' line (`post.out`): ```
REPORTED: no run read 0, route m only 2, no energy 0, labelled []; by family {"D": {"route_m_only": 2}}; the session's stop None
```

## 3. THE PICK, as E222's committed scores give it

The words: "MM1-v3.3 := the composition E222's registered SELECTION RULE picks"; "The scorer reads the pick from E222's committed scores and never from anything else": "every file named `scores-e222*.json` in a `docs/reports/data/` folder whose name holds `e222`, as committed at the lab's HEAD". Without them "the MM1-v3.3 rules read PENDING until E222's scores are committed (a dated note says which), and the rest is scored"; "E222's own label (R0 or S6 FAIL) rides with the pick into every MM1-v3.3 verdict". E222's rule: "MM1-v3.3 = MM1-v3.2 plus every candidate term whose HC test reads '<candidate> BETTER' and whose NH test reads PASS"; "A NOT DECIDED or TOO FEW leaves that term out."

E222's two committed scores files (`scores-e222-A.json`, `scores-e222-cx.json` in [`2026-11-21-e222-blind-matmul-aifoundry3/`](../2026-11-21-e222-blind-matmul-aifoundry3/), committed in `c661275c` at 01:57:49 PST Sat 21 Nov, after both E224 arms' step 13 at 00:49:57 and 00:56:31) both read SEL **'MM1-v3.3 = MM1-v3.2 + AF4'** with no E222 label (E222's R0 and S6 PASS): HC-AF4 'MM1-v3.2 + AF4 BETTER' (12/2/0, p 0.0129) with NH-AF4 PASS; HC-posimb NOT DECIDED (5/3/2, p 0.727) and HC-L3S NOT DECIDED (9/4/5, p 0.267), so posimb and L3S stay out (E222's dated note 1 in that folder). So **MM1-v3.3 = MM1-v3.2 + AF4**, the composition the frozen scorer maps that string to (its `SEL_TO`): AF4 "at rgm136's gemmLnc points (F3 replaced by dW = S (c1 dup + c2 R4), c1 236.3, c2 597.3 pJ)", MM1-v3.2 everywhere else. On this arm its frozen forecasts differ from MM1-v3.2's at 5 points (d29, d30, g01, g02, g03), and only in energy (section 6).

**The picked run.** This lane ran the step's own scorer call again, unchanged and in a CPU slot, on a tree exported at HEAD (`d1516001`), with the scorer's `--lab` the scratch clone moved to `c661275c`: `scores-e224-B-picked.json` and `.txt`. Its pick record names the two E222 files, SEL 'MM1-v3.3 = MM1-v3.2 + AF4', E222's label none, HEAD `c661275c`; its arm B block equals the two-arm run's (dated note 20) in every field; the same call with the lab at HEAD (`d1516001`) gives the same bytes but for the pick record's `lab_head`. Every pick-independent field (R0, H10-H12, every model's bands, the REPORTED head-to-heads, the switch rule, the family table) is the same as in the step's file. Its printed lines:

```
A:E1: NO DATA
A:E2: NO DATA
A:E3: NO DATA
A:E4: NO DATA
A:H1: NO DATA
A:H10: NO DATA
A:H11: NO DATA
A:H12: NO DATA
A:H2: NO DATA
A:H3: NO DATA
A:H4: NO DATA
A:H5: NO DATA
A:H6: NO DATA
A:H7: NO DATA
A:H8: NO DATA
A:H9: NO DATA
A:R0: NO DATA
A:S6: NO DATA
A:T1: NO DATA
A:T2: NO DATA
A:T3: NO DATA
B:E1: FAIL [labelled: R0 FAIL]
B:E2: PASS [labelled: R0 FAIL]
B:E3: FAIL [labelled: R0 FAIL]
B:E4: FAIL [labelled: R0 FAIL]
B:H1: TOO FEW [labelled: R0 FAIL]
B:H10: NOT DECIDED [labelled: R0 FAIL]
B:H11: NOT DECIDED [labelled: R0 FAIL]
B:H12: TOO FEW [labelled: R0 FAIL]
B:H2: TOO FEW [labelled: R0 FAIL]
B:H3: TOO FEW [labelled: R0 FAIL]
B:H4: TOO FEW [labelled: R0 FAIL]
B:H5: TOO FEW [labelled: R0 FAIL]
B:H6: TOO FEW [labelled: R0 FAIL]
B:H7: TOO FEW [labelled: R0 FAIL]
B:H8: TOO FEW [labelled: R0 FAIL]
B:H9: TOO FEW [labelled: R0 FAIL]
B:R0: FAIL
B:T1: PASS [labelled: R0 FAIL]
B:T2: PASS [labelled: R0 FAIL]
B:T3: PASS [labelled: R0 FAIL]
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
P:SW: NOT DECIDED [labelled: R0 FAIL]
PICK: PICKED: MM1-v3.3 = MM1-v3.2 + AF4
```

Its `A:` lines read NO DATA and **its `P:` lines are arm B alone** (clause 4).

## 4. The registered rules' words, and the verdicts (BLIND; every one labelled R0 FAIL)

**R0.** The words: R0 "(every check of C exact or approx; the smoke good)" and, arm A, S6 "(every kept run at 590-610 MHz): a FAIL labels every other verdict of its arm and the pooled ones". Arm B: **R0 FAIL**: the scorer's four failures are checks of C read 'wrong' at `p3b run 14`, `p3a run 40`, `p3a run 73` and `p3b run 85`, at the same two fp16 pattern points as arm A (p3a, p3b at `gemmL1x1x25`), with the same counts on both cards (this README's note 12; dated note 18). fix-e224d's dated notes (commit `d1516001`, 02:27:39 PST) read the four checks at the desk: "the host's fixed check of C at K 25,600 against an fp32 accumulation that drops low bits, read at the desk, no wrong GEMM shown (NOT TESTED on a card)" (post hoc, REPORTED); verify-e224d's words: "It is the check failing, not a wrong GEMM." R0 stays FAIL by its registered words and labels every verdict; nothing is dropped. Both points keep their readings in the scorer's measured side (the switch rule reads 8 pattern points on this arm). S6 is arm A's rule only.

**MM1-v3.3's per-case and per-point rules.** The words: "each passes when |measured / forecast - 1| is within its band; a rule PASSES with at least 90% of its scored cases or points, FAIL otherwise, TOO FEW under 10, NO DATA with none; PENDING with no pick"; the bands are E220's for these two cards, "2 x the larger of its LOEO error without twins over every point and over the card's points, rounded up to a whole percent". "Points under 3 W over idle are scored in watts in E1 and E2: |W measured - W forecast| <= 0.52 W on both arms. Time is scored at the time-scored points only (family P's zeros and pattern points share their random twin's time case)." The ties on this arm: cycles 0.005 in ln, joules 0.01 in ln, watts points 0.1 W. Watts cells here (E1, E2): none.

| rule | quantity | band | passes / scored (needed) | MM1-v3.3's verdict | MM1-v3.2's (REPORTED) | the misses by family | the misses (measured / forecast - 1; a watts cell: measured - forecast) |
|---|---|---|---|---|---|---|---|
| **T1** | wall cycles an op | 11% | 46 / 49 (45) | **PASS** | PASS 46/49 | D/D-G-mid 1, L/AF4-NB56 1, L/posimb-pair 1 | d29 -13.96%, g01 -13.17%, y2b -11.66% |
| **T2** | the counter's mean cycles an op | 14% | 48 / 49 (45) | **PASS** | PASS 48/49 | D/D-L2 1 | d02 -16.41% |
| **T3** | seconds a GEMM | 11% | 46 / 49 (45) | **PASS** | PASS 46/49 | D/D-G-mid 1, L/AF4-NB56 1, L/posimb-pair 1 | d29 -13.97%, g01 -13.19%, y2b -11.68% |
| **E1** | J over idle given the measured op time | 10% (watts cells 0.52 W) | 54 / 61 (55) | **FAIL** | PASS 56/61 | D/D-G-L2 1, L/AF4-NB56 1, P/P-a 3, P/P-b 2 | d30 -22.84%, g02 +10.06%, p1a -10.83%, p3a -11.76%, p3b -10.81%, p4a -15.22%, p4b -15.88% |
| **E2** | J over idle with seconds forecast | 12% (watts cells 0.52 W) | 55 / 61 (55) | **PASS** | PASS 57/61 | D/D-G-L2 1, L/AF4-NB56 1, P/P-a 2, P/P-b 2 | d30 -23.82%, g02 +12.51%, p3a -13.64%, p3b -12.52%, p4a -16.13%, p4b -16.79% |
| **E3** | J at rest given the measured op time | 4% | 47 / 61 (55) | **FAIL** | FAIL 50/61 | D/D-G-L2 1, D/D-G-mid 1, D/D-beyond 1, D/D-mid 2, L/AF4-NB56 2, P/P-a 3, P/P-b 3, P/P-r 1 | d07 -4.66%, d13 -4.46%, d23 -5.20%, d29 +6.31%, d30 -15.18%, g02 +5.98%, g03 -5.40%, p1a -6.30%, p1b -4.42%, p3a -6.69%, p3b -6.39%, p3r -4.46%, p4a -7.38%, p4b -8.13% |
| **E4** | J at rest with seconds forecast | 10% | 54 / 61 (55) | **FAIL** | PASS 55/61 | D/D-G-L2 1, D/D-subset 1, L/AF4-NB56 1, L/posimb-pair 1, P/P-a 1, P/P-b 2 | d27 -10.12%, d30 -17.84%, g02 +11.46%, p3a -10.83%, p3b -10.29%, p4b -10.02%, y2b -11.09% |

Every miss is listed by its point id and counted by its family and subfamily (`points-e224.json`); the cell figures are the scorer's (`scores-e224-B-picked.json` > `arms` > `B` > `T1`...`E4` > `cells`). MM1-v3.2's column is REPORTED (its own bands, as the scorer's `bands_REPORTED_every_model` holds them).

**Where the pick and MM1-v3.2 part** (REPORTED, post hoc; a point 'lost' passes under MM1-v3.2 and misses under MM1-v3.3, a point 'gained' the other way): E1 loses d30, g02 and gains no point; E2 loses d30, g02 and gains no point; E3 loses d29, d30, g02, g03 and gains g01; E4 loses d30, g02 and gains g01.

**At or next to the line** (exact as registered; each stands): **T1** PASS 46/49 with 45 needed; its closest pass y3b at -10.934% against 11%, its closest miss y2b at -11.658% against 11%; **T3** PASS 46/49 with 45 needed; its closest pass y3b at -10.941% against 11%, its closest miss y2b at -11.676% against 11%; **E1** FAIL 54/61 with 55 needed; its closest pass d29 at +9.898% against 10%, its closest miss g02 at +10.056% against 10%; **E2** PASS 55/61 with 55 needed; its closest pass d23 at -10.784% against 12%, its closest miss g02 at +12.512% against 12%; **E4** FAIL 54/61 with 55 needed; its closest pass y3b at -9.971% against 10%, its closest miss p4b at -10.022% against 10%.

**Route m (REPORTED).** The words: arm B's measured side reads "per run in its primary view, ROUTE c when the view clock reads 790-810 MHz with no step, against the frozen 799.0 MHz column; ROUTE m otherwise, REPORTED against the column nearest its clock; a capped or thin run carries no energy". Runs at d06, d17, d28, y3b read route m; d06 and d17 have no route-c run and leave every registered rule (`post-e224b.json`: "route m only 2"), so 61 of the 63 registered points are scored, every one at the 799.0 MHz column.

## 5. The head-to-heads (BLIND)

The words: per case or point "d = |ln(measured / second)| - |ln(measured / first)|", "decided when |d| exceeds the arm's tie (cycles 0.005 in ln, joules 0.01 in ln, watts 0.05 W on arm A and 0.1 W on arm B: E220's ties); the exact two-sided sign test over the decided: '<first> BETTER' at p < 0.05 with at least 8 decided, else NOT DECIDED; TOO FEW under 8." H1-H9 / HP1-HP9, MM1-v3.3 against MM1-v3.2 "on all points (H1 wall, H2 W given t, H3 J at rest given t), family D alone (H4-H6) and family L alone (H7-H9), per arm and pooled (each case with its own arm's tie)"; H10-H12 / HP10-HP12, MM1-v3.2 against MM1-v3 "on all points, the same three quantities".

| rule | first against second | scope | quantity | first closer / second closer / ties | n | p | the scorer's verdict | verify-e224d (own code) |
|---|---|---|---|---|---|---|---|---|
| **H1** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | wall | 0/0/49 | 49 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H2** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | Wg | 1/4/56 | 61 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H3** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | JRg | 1/4/56 | 61 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H4** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | wall | 0/0/27 | 27 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H5** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | Wg | 0/2/25 | 27 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H6** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | JRg | 0/2/25 | 27 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H7** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | wall | 0/0/18 | 18 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H8** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | Wg | 1/2/15 | 18 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H9** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | JRg | 1/2/15 | 18 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |
| **H10** | MM1-v3.2 against MM1-v3 | all | wall | 14/15/20 | 49 | 1 | **NOT DECIDED [labelled: R0 FAIL]** | the same counts, p and verdict |
| **H11** | MM1-v3.2 against MM1-v3 | all | Wg | 8/8/37 | 53 | 1 | **NOT DECIDED [labelled: R0 FAIL]** | the same counts, p and verdict |
| **H12** | MM1-v3.2 against MM1-v3 | all | JRg | 4/1/48 | 53 | - | **TOO FEW [labelled: R0 FAIL]** | the same counts and verdict |

Stated before the data: "Per arm almost every H1-H9 reads TOO FEW by construction." On time, "every pick's power is at most 0.09: a NOT DECIDED or TOO FEW there says the models' time forecasts are within their errors of each other, not that they are equally good"; on energy "(HP2, HP3) a pick holding AF4 can decide on its ten gemmLnc points (power 0.35-0.67)". On this arm MM1-v3.3 and MM1-v3.2 differ by more than the tie at 5 of 61 points in W over idle and at none in wall cycles (H1 0/0/49): H1-H9 read TOO FEW, as the registration's power table said they would.

## 6. MM1-v3.3 against MM1-v3.2 where AF4 acts (REPORTED; the cases behind H2)

| point | family | what | measured W over idle | MM1-v3.2's W given t (ln error) | MM1-v3.3's (ln error) | closer (H2's rule) |
|---|---|---|---|---|---|---|
| d29 | D/D-G-mid | gemmLnc1x4x12.fp32.random.rgm136-gemmLnc | 41.49 W | 39.64 W (+0.0457) | 37.75 W (+0.0944) | MM1-v3.2 |
| d30 | D/D-G-L2 | gemmLnc1x6x2.int8.random.rgm136-gemmLnc | 32.89 W | 31.06 W (+0.0572) | 42.63 W (-0.2593) | MM1-v3.2 |
| g01 | L/AF4-NB56 | gemmLnc3x6x12.fp32.random.rgm136-gemmLnc | 35.97 W | 39.18 W (-0.0855) | 37.86 W (-0.0514) | MM1-v3.3 |
| g02 | L/AF4-NB56 | gemmLnc3x5x12.fp32.random.rgm136-gemmLnc | 34.81 W | 32.86 W (+0.0578) | 31.63 W (+0.0958) | MM1-v3.2 |
| g03 | L/AF4-NB56 | gemmLnc1x5x14.fp32.random.rgm136-gemmLnc | 36.24 W | 34.89 W (+0.0380) | 39.54 W (-0.0871) | MM1-v3.2 |

The point's measured W over idle and each model's W given the measured op time (the scorer's `predicted()`), ln(measured / forecast) in brackets; 'closer' by H2's rule (tie 0.01 in ln). AF4 moves no time forecast at any E224 point (checked at every point and column). Beside it (REPORTED): E220's G2 reading on these two cards, for F3 at its small-excess gemmLnc points: on aifoundry1 card 1 "the measured excess is 1.96-2.69 times F3's", on aifoundry2 card 0 "the measured excess is 1.47-2.15 times F3's"; and of the candidates "no candidate has a card factor".

## 7. Family P's switch-count rule on this arm (REPORTED; the registered reading is pooled, dated note 20)

The words: SW is "registered pooled over both arms for MM1-v3.2" "(its switch counts are the registered inputs; MM1-v3.3 and every composition REPORTED beside, and each arm REPORTED)": "per pattern point Q1 e_V = ln(W measured / V), V the model's W given the measured op time with its counts, against e_N = ln(W measured / N), N the mean over zeros, ones and random of the same model's W given the same op time (cases at 3 W or more)"; "Q2 E210's metric e_D = [(V - V_R) - (W - W_R)] / D, D = W_R - W_Z measured at the shape's random and zeros twins (V_R the model's W given t at the random twin's own op time), against the null's [(N - V_R) - (W - W_R)] / D (cases with D > 0)"; "P1 rms(e_V) < rms(e_N); P2 the exact two-sided sign test on |e_N| - |e_V| (tie 0.01 in ln), the counts closer at p < 0.05 with at least 6 decided; P3 rms(e_D) < the null's; P4 P2's test on Q2 (tie 0.01 of D)"; PASS when P1-P4 hold, FAIL "when P1 or P3 fails or a sign test reads the null closer", NOT DECIDED otherwise.

On arm B, MM1-v3.2 with its counts: **NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156**. Every model on this arm (REPORTED):

| model | SW (REPORTED but MM1-v3.2's pooled) |
|---|---|
| MM1-v3.2 | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.2 + posimb | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.2 + AF4 | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.2 + L3S | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.2 + posimb + AF4 | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.2 + posimb + L3S | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.2 + AF4 + L3S | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.2 + all three | NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3.1 | NOT DECIDED: Q1 n 8, rms e_V 11.03% vs e_N 26.57% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.06% of D vs 47.23% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156 |
| MM1-v3 | NO DATA (no pattern pricing at these points) |
| MM1-v2 | NO DATA (no pattern pricing at these points) |

MM1-v3 and MM1-v2 price no pattern tile, so their rule reads NO DATA; every MM1-v3.2 composition reads as MM1-v3.2, since none of the three terms acts at family P's points.

## 8. Every other composition (REPORTED, never a verdict)

REPORTED, never a verdict: "every composition's bands and its H1-H9 against MM1-v3.2 (the seven not picked); per family (D, P, L) and forecaster the rms and bias of ln(measured / forecast) of the wall cycles and W given t; SW per arm and for every model; route m on arm B; family L's leads read per lead (L3S's edge points' wall errors, posimb's measured ln(wall a / wall b) per pair against each forecaster's, AF4's measured gemmLnc excess against its twin, against F3's and AF4's)".

**The bands** (passes / scored, each with its verdict as the rule reads it):

| model | T1 | T2 | T3 | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|
| MM1-v3.2 | PASS 46/49 | PASS 48/49 | PASS 46/49 | PASS 56/61 | PASS 57/61 | FAIL 50/61 | PASS 55/61 |
| MM1-v3.2 + posimb | PASS 47/49 | PASS 48/49 | PASS 47/49 | PASS 56/61 | PASS 57/61 | FAIL 50/61 | PASS 55/61 |
| MM1-v3.2 + AF4 (THE PICK: registered) | PASS 46/49 | PASS 48/49 | PASS 46/49 | FAIL 54/61 | PASS 55/61 | FAIL 47/61 | FAIL 54/61 |
| MM1-v3.2 + L3S | PASS 47/49 | PASS 48/49 | PASS 47/49 | PASS 56/61 | PASS 57/61 | FAIL 49/61 | PASS 55/61 |
| MM1-v3.2 + posimb + AF4 | PASS 47/49 | PASS 48/49 | PASS 47/49 | FAIL 54/61 | PASS 55/61 | FAIL 47/61 | FAIL 54/61 |
| MM1-v3.2 + posimb + L3S | PASS 48/49 | PASS 48/49 | PASS 48/49 | PASS 56/61 | PASS 57/61 | FAIL 49/61 | PASS 55/61 |
| MM1-v3.2 + AF4 + L3S | PASS 47/49 | PASS 48/49 | PASS 47/49 | FAIL 53/61 | PASS 55/61 | FAIL 46/61 | FAIL 54/61 |
| MM1-v3.2 + all three | PASS 48/49 | PASS 48/49 | PASS 48/49 | FAIL 53/61 | PASS 55/61 | FAIL 46/61 | FAIL 54/61 |
| MM1-v3.1 | FAIL 43/49 | PASS 48/49 | FAIL 43/49 | FAIL 53/61 | FAIL 54/61 | FAIL 47/61 | FAIL 52/61 |
| MM1-v3 | FAIL 44/49 | PASS 48/49 | FAIL 44/49 | PASS 49/53 | PASS 49/53 | FAIL 46/53 | FAIL 46/53 |
| MM1-v2 | FAIL 38/49 | FAIL 44/49 | FAIL 38/49 | FAIL 45/53 | FAIL 44/53 | FAIL 36/53 | FAIL 45/53 |

**H1-H9 against MM1-v3.2** (first closer / MM1-v3.2 closer / ties; 'first BETTER' = the composition):

| composition (first) against MM1-v3.2 | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | H9 |
|---|---|---|---|---|---|---|---|---|---|
| MM1-v3.2 + posimb | TOO FEW 4/0/45 | TOO FEW 0/0/61 | TOO FEW 0/0/61 | TOO FEW 0/0/27 | TOO FEW 0/0/27 | TOO FEW 0/0/27 | TOO FEW 4/0/14 | TOO FEW 0/0/18 | TOO FEW 0/0/18 |
| MM1-v3.2 + AF4 (THE PICK: registered) | TOO FEW 0/0/49 | TOO FEW 1/4/56 | TOO FEW 1/4/56 | TOO FEW 0/0/27 | TOO FEW 0/2/25 | TOO FEW 0/2/25 | TOO FEW 0/0/18 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |
| MM1-v3.2 + L3S | NOT DECIDED 5/8/36 p 0.581 | TOO FEW 0/0/61 | TOO FEW 0/0/61 | TOO FEW 3/3/21 | TOO FEW 0/0/27 | TOO FEW 0/0/27 | TOO FEW 2/5/11 | TOO FEW 0/0/18 | TOO FEW 0/0/18 |
| MM1-v3.2 + posimb + AF4 | TOO FEW 4/0/45 | TOO FEW 1/4/56 | TOO FEW 1/4/56 | TOO FEW 0/0/27 | TOO FEW 0/2/25 | TOO FEW 0/2/25 | TOO FEW 4/0/14 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |
| MM1-v3.2 + posimb + L3S | NOT DECIDED 9/8/32 p 1 | TOO FEW 0/0/61 | TOO FEW 0/0/61 | TOO FEW 3/3/21 | TOO FEW 0/0/27 | TOO FEW 0/0/27 | NOT DECIDED 6/5/7 p 1 | TOO FEW 0/0/18 | TOO FEW 0/0/18 |
| MM1-v3.2 + AF4 + L3S | NOT DECIDED 5/8/36 p 0.581 | TOO FEW 1/4/56 | TOO FEW 1/4/56 | TOO FEW 3/3/21 | TOO FEW 0/2/25 | TOO FEW 0/2/25 | TOO FEW 2/5/11 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |
| MM1-v3.2 + all three | NOT DECIDED 9/8/32 p 1 | TOO FEW 1/4/56 | TOO FEW 1/4/56 | TOO FEW 3/3/21 | TOO FEW 0/2/25 | TOO FEW 0/2/25 | NOT DECIDED 6/5/7 p 1 | TOO FEW 1/2/15 | TOO FEW 1/2/15 |

Where each term acts: posimb "acts at 10 points on arm A and 10 on arm B", L3S "acts at 51 points on arm A and 49 on arm B", AF4 "acts at 5 points on arm A and 5 on arm B" (the registration's count, section 1).

## 9. Each model's error by family (REPORTED)

The rms of ln(measured / forecast), in percent: wall cycles at the time-scored points, W over idle given the measured op time at the points measured at 3 W and above, J at rest given the measured op time (the run's own measured rest); the scorer's `family_stats_REPORTED` rules for the first two, with J at rest and the family 'all' added by the scorer's own functions; each figure equal to verify-e224d's own (n: wall / W / J at rest).

| model | D wall / W given t / J at rest (n) | P | L | all |
|---|---|---|---|---|
| MM1-v3.2 | 5.72 / 5.07 / 2.87 (27/27/27) | 3.98 / 8.88 / 4.67 (4/16/16) | 6.64 / 5.14 / 2.94 (18/18/18) | 5.96 / 6.31 / 3.45 (49/61/61) |
| MM1-v3.2 + posimb | 5.72 / 5.07 / 2.87 (27/27/27) | 3.98 / 8.88 / 4.67 (4/16/16) | 6.41 / 5.14 / 2.94 (18/18/18) | 5.87 / 6.31 / 3.45 (49/61/61) |
| MM1-v3.2 + AF4 | 5.72 / 7.20 / 4.35 (27/27/27) | 3.98 / 8.88 / 4.67 (4/16/16) | 6.64 / 5.52 / 3.19 (18/18/18) | 5.96 / 7.26 / 4.13 (49/61/61) |
| MM1-v3.2 + L3S | 5.42 / 5.13 / 2.91 (27/27/27) | 3.98 / 8.88 / 4.68 (4/16/16) | 6.71 / 5.13 / 2.94 (18/18/18) | 5.83 / 6.33 / 3.47 (49/61/61) |
| MM1-v3.2 + posimb + AF4 | 5.72 / 7.20 / 4.35 (27/27/27) | 3.98 / 8.88 / 4.67 (4/16/16) | 6.41 / 5.52 / 3.19 (18/18/18) | 5.87 / 7.26 / 4.13 (49/61/61) |
| MM1-v3.2 + posimb + L3S | 5.42 / 5.13 / 2.91 (27/27/27) | 3.98 / 8.88 / 4.68 (4/16/16) | 6.48 / 5.13 / 2.94 (18/18/18) | 5.74 / 6.33 / 3.47 (49/61/61) |
| MM1-v3.2 + AF4 + L3S | 5.42 / 7.27 / 4.39 (27/27/27) | 3.98 / 8.88 / 4.68 (4/16/16) | 6.71 / 5.52 / 3.19 (18/18/18) | 5.83 / 7.29 / 4.15 (49/61/61) |
| MM1-v3.2 + all three | 5.42 / 7.27 / 4.39 (27/27/27) | 3.98 / 8.88 / 4.68 (4/16/16) | 6.48 / 5.52 / 3.19 (18/18/18) | 5.74 / 7.29 / 4.15 (49/61/61) |
| MM1-v3.1 | 6.48 / 8.95 / 5.12 (27/27/27) | 3.54 / 8.36 / 4.40 (4/16/16) | 7.37 / 7.50 / 4.45 (18/18/18) | 6.64 / 8.39 / 4.74 (49/61/61) |
| MM1-v3 | 6.31 / 8.82 / 5.07 (27/27/27) | 3.72 / 4.05 / 2.27 (4/8/8) | 7.19 / 7.57 / 4.48 (18/18/18) | 6.48 / 7.84 / 4.55 (49/53/53) |
| MM1-v2 | 8.12 / 9.72 / 5.42 (27/27/27) | 2.58 / 6.91 / 3.57 (4/8/8) | 8.07 / 7.13 / 4.20 (18/18/18) | 7.80 / 8.52 / 4.78 (49/53/53) |

## 10. The leads, read per lead (REPORTED, never verdicts)

- **posimb's equal-count layout pairs** (measured ln(wall a / wall b) against each forecaster's): y1 measured +0.0802, 'MM1-v3.2 + posimb' +0.0206, MM1-v3.2 +0.0000, MM1-v3.1 +0.0000, MM1-v3 +0.0000; y2 measured +0.1403, 'MM1-v3.2 + posimb' +0.0434, MM1-v3.2 +0.0000, MM1-v3.1 +0.0000, MM1-v3 +0.0000; y3 measured +0.1326, 'MM1-v3.2 + posimb' +0.0406, MM1-v3.2 +0.0000, MM1-v3.1 +0.0000, MM1-v3 +0.0000. The measured layout effect has posimb's sign at all three pairs and is 3.2-3.9 times its size; MM1-v3.2, MM1-v3.1 and MM1-v3 predict no difference.
- **AF4's gemmLnc points against their cooperative twins** (the measured excess W(g) - W(gt) at the measured op times, against F3's, MM1-v3.2's, and AF4's): g01 measured 35.97 W against its twin's 29.20 W (excess +6.77 W); F3's (MM1-v3.2) +7.88 W, AF4's +6.56 W; g02 measured 34.81 W against its twin's 28.19 W (excess +6.62 W); F3's (MM1-v3.2) +3.53 W, AF4's +2.30 W; g03 measured 36.24 W against its twin's 28.08 W (excess +8.16 W); F3's (MM1-v3.2) +5.01 W, AF4's +9.66 W.
- **L3S's L3 edges** (ln(measured / forecast) of the wall cycles, MM1-v3.2 / 'MM1-v3.2 + L3S'): e01 -0.0350 / -0.0471; e02 -0.0349 / -0.0464; e03 -0.0213 / -0.0368; e04 -0.0582 / -0.0708; e05 -0.0780 / -0.0832; e06 +0.0229 / +0.0230; rms over the six 4.64% / 5.51%.

## 11. verify-e224d's re-derivation, beside (its own code; verdict HOLDS WITH FIXES)

verify-e224d re-derived this arm from its raw records with its own code (1,890 of 1,890 primary-view fields; route c at 61 of 63 points, d06 and d17 route m only), scored every rule with its own scorer, and found it equal to both card lanes' scorer files (1,559 of 1,559 values, pick-independent) and to the frozen scorer run with both arms at `c661275c` (1,662 of 1,662; the pick's rules 237 of 237). This lane's checks of the same files: the provenance by the runbook logs 76 of 76 OK; step 13 and the picked and pooled runs made again from committed bytes, 35 comparisons SAME, none different; the facts 45 of 45 OK (every band, cell, head-to-head, switch-rule case and family figure re-made by the frozen scorer's own functions equal to its JSON and to verify-e224d's own scorer and leads).

## 12. Findings, answered as dated clauses (Sat 21 Nov 2026, after the data; post hoc; nothing re-scored)

1. **info, THE PICK came after step 13.** E222's scores were committed at 01:57:49 PST, after both arms' step 13 (00:49:57 and 00:56:31), so the card lanes' scorer files read NO PICK and every MM1-v3.3 rule PENDING, as the lab stood then (verify-e224d's finding 5). **Answered here:** the step's files are committed unchanged, and the same registered call made with the lab holding E222's scores is committed beside them (`scores-e224-B-picked.*`, section 3); the pooled rules are dated note 20. *Fix for future kits:* none needed (the registration foresaw it).
2. **medium, R0 FAIL (verify-e224d's finding 1; card-e224b's medium finding).** Answered by dated note 18: the same reading as arm A's (the host's fixed tolerance against an accumulation that drops low bits at 800 k-tiles, at the desk, post hoc, NOT TESTED on a card). R0 stays FAIL and labels every verdict here; nothing is dropped.
3. **low, this README's 'runs' and 'never-run' rows (verify-e224d's finding 3; card-e224b's).** They carry the registered form's wording ("105 of 103 ran", "NOT RUN"); this README's note 15 says so; no change. Step 6n did run: "63 of 63 registered points never ran on aifoundry2 card 0 by session records" (this README's note on step 6n). The lab checks C0_src and C2_runs read FAIL, REPORTED, never a gate (verify-e224d's finding 4; the same form as E216 and E220); no change.
4. **info, the one-arm files' `P:` lines.** Both of this arm's scorer files hold `P:HP1`-`P:HP12` and `P:SW` lines computed from arm B alone (the frozen scorer pools whatever arms it is given; their HP10-HP12 counts are this arm's H10-H12). They are not the registered pooled reading, which is dated note 20's two-arm run. The kit's step-13 header says "arm A's rules and the pooled rules read NO DATA in this file", which is wrong about the scorer for the pooled rules: they read arm B alone. *Fix for future kits:* correct that header sentence.
5. **info, H1-H9 TOO FEW.** As the registration's power table said before the data, the three terms barely act at E224's points: on this arm MM1-v3.3 and MM1-v3.2 differ by more than a tie at 5 points in energy and at none in time, so no per-arm head-to-head can decide. This says the two models' forecasts are within their errors of each other here, not that AF4 is right or wrong (E224.md section 8). *Fix:* none (E224.md section 8 said so before the data).
6. **info, verdicts at or next to the line.** **T1** PASS 46/49 with 45 needed; its closest pass y3b at -10.934% against 11%, its closest miss y2b at -11.658% against 11%; **T3** PASS 46/49 with 45 needed; its closest pass y3b at -10.941% against 11%, its closest miss y2b at -11.676% against 11%; **E1** FAIL 54/61 with 55 needed; its closest pass d29 at +9.898% against 10%, its closest miss g02 at +10.056% against 10%; **E2** PASS 55/61 with 55 needed; its closest pass d23 at -10.784% against 12%, its closest miss g02 at +12.512% against 12%; **E4** FAIL 54/61 with 55 needed; its closest pass y3b at -9.971% against 10%, its closest miss p4b at -10.022% against 10%. Each is exact as registered and stands.

## 13. What this note does not do

It changes no committed file, datum, forecast, point, band, tie, rule, label or verdict; it does not re-choose THE PICK, drop a point or lift R0's label; it scores nothing but by the frozen scorer's own registered call; it scores no forecast of the model session's (their seal is registered in `71d217b8` and stays theirs); and it reads no box, card or session folder of theirs.

## 14. `SHA256SUMS-note19`

`SHA256SUMS-note19` lists the 11 files this note adds (this note among them), then `README.md`, `SHA256SUMS` and `SHA256SUMS-note18` as committed; `sha256sum -c SHA256SUMS-note19` from this directory reads every line OK.
