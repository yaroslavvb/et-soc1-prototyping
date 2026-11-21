# E224 pooled rules, dated note 20: the frozen scorer on both arms' committed measured sides at once, with THE PICK from E222's committed scores (MM1-v3.3 = MM1-v3.2 + AF4) - every verdict labelled R0 FAIL; HP1 TOO FEW, HP2 and HP3 NOT DECIDED, HP4-HP9 TOO FEW (MM1-v3.3 against MM1-v3.2); HP10 and HP11 NOT DECIDED, HP12 MM1-v3.2 BETTER (against MM1-v3); SW PASS (family P's switch-count rule); with verify-e224d's run beside, byte for byte

*Sat 21 Nov 2026 (week 47), PST; written from about 02:40 PST by round Q237's lane `scores-e224` at the desk on aifoundry2 (no card, no simulator, no device opened), under `/usr/bin/python3` 3.12.3 (`-I -B`), each numerical step single-threaded inside the round's CPU slots. It follows this directory's dated note 19 (arm B's scores) and arm A's dated note 2 ([`2026-11-21-e224-blind-matmul-aifoundry1-c1/README.md.dated-note-2.md`](../2026-11-21-e224-blind-matmul-aifoundry1-c1/README.md.dated-note-2.md)), both data commits (`96528ad2`, `087f9baa`), E222's scores commit `c661275c` (THE PICK), verify-e224d (HOLDS WITH FIXES) and fix-e224d (`d1516001`). New files only; nothing is changed, dropped, re-chosen or re-scored but by the frozen scorer's own registered functions on both committed arms at once, as the kit's step-13 headers leave to this lane.* **Labels:** **BLIND** (every forecast E224 scores was frozen before either arm's first device access: reg-e224's `FROZEN.txt` at 15:45:11 PST Fri 20 Nov 2026 (sha256 `54277e52...`, posted on the owner's coordination thread as E224's freeze line before any E222 datum), then E224's registration `7de83360` (committed 21:52:25 PST, pushed 21:52:30 PST) with the eight compositions' and MM1-v3.1's, MM1-v3's and MM1-v2's forecasts, the points, the bands, the rules and the scorer, and the kit `0fb6eb95` (21:57:24 PST); the model session's sealed forecast was registered in `71d217b8` (committed 23:27:36 PST), before either arm's first card command (arm A's session from 00:05:29 PST, arm B's from 00:10:10 PST Sat 21 Nov). **THE PICK is not chosen here:** it is E222's registered selection rule's output on E222's own data (aifoundry3 card 0), read by the frozen scorer from E222's committed scores, and every composition it could pick was frozen before any E222 datum); **R0 FAIL** on both arms, so every pooled verdict carries the label once an arm (the scorer's form: `[labelled: R0 FAIL] [labelled: R0 FAIL]`); the REPORTED parts are never verdicts; the readings beside them are **post hoc**.

## 1. The files this note adds

| file | what | bytes | sha256 | label |
|---|---|---|---|---|
| `scores-e224-pooled.json` | the frozen scorer [`tools/claims-v3/e224/score_e224.py`](../../../../tools/claims-v3/e224/score_e224.py) (`c851f3b4...`) on both committed measured sides at once (`--a` arm A's committed `data-e224a.json`, `--a-tag A`, `--b` arm B's committed `data-e224b.json`), the lab at `c661275c`: THE PICK, every per-arm rule of both arms, the pooled HP1-HP12 and SW, and the REPORTED tables | 129,093 | `a7b804628b6ddb24...` | BLIND (its REPORTED parts never verdicts) |
| `scores-e224-pooled.txt` | its printed lines (55 lines) | 2,083 | `76bf9fab75f7a7cc...` | printed lines |
| `README.md.dated-note-20.md` | this note | - | - | dated note |
| `SHA256SUMS-note20` | the three files above, then `SHA256SUMS-note19` (4 lines: with the earlier lists every file here is in a list but this one) | - | - | - |

## 2. Where it comes from: one registered call on both arms (this lane's desk checks)

- **The call.** `score_e224.py --lab <the lab> --a docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry1-c1/data-e224a.json --a-tag A --b <arm B's data-e224b.json> --out <dir>`, run by this lane, unchanged and in a CPU slot, on a tree exported from the lab clone's own objects at HEAD (`d1516001`), with `--lab` a no-checkout scratch clone of the lab moved to `c661275c` (the commit holding E222's scores). Arm A's input is its data commit's `data-e224a.json`; arm B's is step 13's reduction, committed byte for byte by dated note 19 and made again from the committed `session/` by E208's registered reducer, byte for byte.
- **verify-e224d's run, beside.** verify-e224d ran the same call on the same inputs at the lab's HEAD `c661275c` (its `work/frozen-both/`); this lane's JSON and printed lines are byte for byte its JSON and printed lines. With R2's re-made reduction as `--b`, or with `--labels` on one file holding both arms' committed (empty) label sets, the output is the same; with the lab at today's HEAD (`d1516001`) it is the same but for the pick record's `lab_head`. Each arm's block in it equals that arm's picked one-arm run (dated notes 2 and 19).
- **Each pooled count is the sum of its two arms' counts** (HP1-HP12; the scorer pools the cases with each case's own arm's tie).

**The printed lines** (`scores-e224-pooled.txt`, all of it):

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
P:HP1: TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP10: NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP11: NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP12: MM1-v3.2 BETTER [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP2: NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP3: NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP4: TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP5: TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP6: TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP7: TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP8: TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]
P:HP9: TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]
P:SW: PASS [labelled: R0 FAIL] [labelled: R0 FAIL]
PICK: PICKED: MM1-v3.3 = MM1-v3.2 + AF4
```

The `A:` and `B:` lines are each arm's own registered verdicts (dated notes 2 and 19 give their counts and misses); the `P:` lines are the registered pooled reading.

## 3. THE PICK

The words: "MM1-v3.3 := the composition E222's registered SELECTION RULE picks"; "The scorer reads the pick from E222's committed scores and never from anything else": "every file named `scores-e222*.json` in a `docs/reports/data/` folder whose name holds `e222`, as committed at the lab's HEAD". Without them "the MM1-v3.3 rules read PENDING until E222's scores are committed (a dated note says which), and the rest is scored"; "E222's own label (R0 or S6 FAIL) rides with the pick into every MM1-v3.3 verdict". E222's rule: "MM1-v3.3 = MM1-v3.2 plus every candidate term whose HC test reads '<candidate> BETTER' and whose NH test reads PASS"; "A NOT DECIDED or TOO FEW leaves that term out."

E222's two committed scores files (`scores-e222-A.json`, `scores-e222-cx.json` in [`2026-11-21-e222-blind-matmul-aifoundry3/`](../2026-11-21-e222-blind-matmul-aifoundry3/), committed in `c661275c` at 01:57:49 PST Sat 21 Nov, after both E224 arms' step 13 at 00:49:57 and 00:56:31) both read SEL **'MM1-v3.3 = MM1-v3.2 + AF4'** with no E222 label (E222's R0 and S6 PASS): HC-AF4 'MM1-v3.2 + AF4 BETTER' (12/2/0, p 0.0129) with NH-AF4 PASS; HC-posimb NOT DECIDED (5/3/2, p 0.727) and HC-L3S NOT DECIDED (9/4/5, p 0.267), so posimb and L3S stay out (E222's dated note 1 in that folder). So MM1-v3.3 = MM1-v3.2 + AF4 on both arms (AF4 acts at 5 points of arm A and 5 of arm B, only in energy).

## 4. The pooled head-to-heads' words, and the verdicts (BLIND; labelled R0 FAIL once an arm)

The words: per case or point "d = |ln(measured / second)| - |ln(measured / first)|", "decided when |d| exceeds the arm's tie (cycles 0.005 in ln, joules 0.01 in ln, watts 0.05 W on arm A and 0.1 W on arm B: E220's ties); the exact two-sided sign test over the decided: '<first> BETTER' at p < 0.05 with at least 8 decided, else NOT DECIDED; TOO FEW under 8." H1-H9 / HP1-HP9, MM1-v3.3 against MM1-v3.2 "on all points (H1 wall, H2 W given t, H3 J at rest given t), family D alone (H4-H6) and family L alone (H7-H9), per arm and pooled (each case with its own arm's tie)"; H10-H12 / HP10-HP12, MM1-v3.2 against MM1-v3 "on all points, the same three quantities".

| rule | first against second | scope | quantity | first closer / second closer / ties | n | p | the scorer's verdict | verify-e224d (own code) |
|---|---|---|---|---|---|---|---|---|
| **HP1** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | wall | 0/0/101 | 101 | - | **TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts and verdict |
| **HP2** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | Wg | 3/6/116 | 125 | 0.508 | **NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts, p and verdict |
| **HP3** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | all | JRg | 3/6/116 | 125 | 0.508 | **NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts, p and verdict |
| **HP4** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | wall | 0/0/57 | 57 | - | **TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts and verdict |
| **HP5** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | Wg | 1/2/54 | 57 | - | **TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts and verdict |
| **HP6** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | D | JRg | 1/2/54 | 57 | - | **TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts and verdict |
| **HP7** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | wall | 0/0/36 | 36 | - | **TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts and verdict |
| **HP8** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | Wg | 2/4/30 | 36 | - | **TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts and verdict |
| **HP9** | MM1-v3.3 (MM1-v3.2 + AF4) against MM1-v3.2 | L | JRg | 2/4/30 | 36 | - | **TOO FEW [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts and verdict |
| **HP10** | MM1-v3.2 against MM1-v3 | all | wall | 29/27/45 | 101 | 0.894 | **NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts, p and verdict |
| **HP11** | MM1-v3.2 against MM1-v3 | all | Wg | 28/17/64 | 109 | 0.135 | **NOT DECIDED [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts, p and verdict |
| **HP12** | MM1-v3.2 against MM1-v3 | all | JRg | 9/1/99 | 109 | 0.0215 | **MM1-v3.2 BETTER [labelled: R0 FAIL] [labelled: R0 FAIL]** | the same counts, p and verdict |

Stated before the data: "Per arm almost every H1-H9 reads TOO FEW by construction." On time, "every pick's power is at most 0.09: a NOT DECIDED or TOO FEW there says the models' time forecasts are within their errors of each other, not that they are equally good"; on energy "(HP2, HP3) a pick holding AF4 can decide on its ten gemmLnc points (power 0.35-0.67)". Measured: HP1 and every family-D and family-L test read TOO FEW (no wall-cycle case decided; 3 energy cases decided in family D, 6 in family L); HP2 and HP3, the two the registration said a pick holding AF4 could decide, read NOT DECIDED: MM1-v3.3 closer at 3, MM1-v3.2 at 6, of 9 decided (p 0.508). **MM1-v3.2 against MM1-v3:** HP12 (J at rest given t) reads MM1-v3.2 BETTER (9/1/99, p 0.0215); HP10 (wall) and HP11 (W given t) NOT DECIDED.

## 5. Family P's switch-count rule, registered pooled (BLIND; labelled R0 FAIL once an arm)

The words: SW is "registered pooled over both arms for MM1-v3.2" "(its switch counts are the registered inputs; MM1-v3.3 and every composition REPORTED beside, and each arm REPORTED)": "per pattern point Q1 e_V = ln(W measured / V), V the model's W given the measured op time with its counts, against e_N = ln(W measured / N), N the mean over zeros, ones and random of the same model's W given the same op time (cases at 3 W or more)"; "Q2 E210's metric e_D = [(V - V_R) - (W - W_R)] / D, D = W_R - W_Z measured at the shape's random and zeros twins (V_R the model's W given t at the random twin's own op time), against the null's [(N - V_R) - (W - W_R)] / D (cases with D > 0)"; "P1 rms(e_V) < rms(e_N); P2 the exact two-sided sign test on |e_N| - |e_V| (tie 0.01 in ln), the counts closer at p < 0.05 with at least 6 decided; P3 rms(e_D) < the null's; P4 P2's test on Q2 (tie 0.01 of D)"; PASS when P1-P4 hold, FAIL "when P1 or P3 fails or a sign test reads the null closer", NOT DECIDED otherwise.

Pooled, MM1-v3.2 with its counts (16 pattern points, 8 an arm): **PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5**; the scorer's verdict **PASS [labelled: R0 FAIL] [labelled: R0 FAIL]**. Per arm (REPORTED; dated notes 2 and 19): arm A PASS: Q1 n 8, rms e_V 13.07% vs e_N 35.03% (P1 HOLDS); P2 counts BETTER 7/0/1 p 0.0156; Q2 n 8, rms e_D 16.56% of D vs 42.22% (P3 HOLDS); P4 counts BETTER 8/0/0 p 0.00781; arm B NOT DECIDED: Q1 n 8, rms e_V 11.65% vs e_N 26.24% (P1 HOLDS); P2 NOT DECIDED 7/1/0 p 0.0703; Q2 n 8, rms e_D 16.12% of D vs 47.75% (P3 HOLDS); P4 counts BETTER 7/0/1 p 0.0156. Every model pooled (REPORTED):

| model | SW (REPORTED but MM1-v3.2's pooled) |
|---|---|
| MM1-v3.2 | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.2 + posimb | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.2 + AF4 | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.2 + L3S | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.2 + posimb + AF4 | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.2 + posimb + L3S | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.2 + AF4 + L3S | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.2 + all three | PASS: Q1 n 16, rms e_V 12.38% vs e_N 30.95% (P1 HOLDS); P2 counts BETTER 14/1/1 p 9.77e-4; Q2 n 16, rms e_D 16.34% of D vs 45.07% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3.1 | PASS: Q1 n 16, rms e_V 11.69% vs e_N 31.55% (P1 HOLDS); P2 counts BETTER 15/1/0 p 5.19e-4; Q2 n 16, rms e_D 16.31% of D vs 44.82% (P3 HOLDS); P4 counts BETTER 15/0/1 p 6.10e-5 |
| MM1-v3 | NO DATA (no pattern pricing at these points) |
| MM1-v2 | NO DATA (no pattern pricing at these points) |

R0's four wrong checks on each card sit at two of these pattern points (p3a, p3b): the frozen readers record a wrong check for R0 and keep the run's readings, so the rule reads all 16 pattern points as registered, and R0's label rides with its verdict.

## 6. Every other composition, pooled (REPORTED, never a verdict)

REPORTED, never a verdict: "every composition's bands and its H1-H9 against MM1-v3.2 (the seven not picked); per family (D, P, L) and forecaster the rms and bias of ln(measured / forecast) of the wall cycles and W given t; SW per arm and for every model; route m on arm B; family L's leads read per lead (L3S's edge points' wall errors, posimb's measured ln(wall a / wall b) per pair against each forecaster's, AF4's measured gemmLnc excess against its twin, against F3's and AF4's)".

**HP1-HP9 against MM1-v3.2** (first closer / MM1-v3.2 closer / ties; 'first BETTER' = the composition), each composition by the frozen scorer's own `h_cases()` and `decide()` over both arms, as the scorer does for the pick, and equal to verify-e224d's own:

| composition (first) against MM1-v3.2 | HP1 | HP2 | HP3 | HP4 | HP5 | HP6 | HP7 | HP8 | HP9 |
|---|---|---|---|---|---|---|---|---|---|
| MM1-v3.2 + posimb | first BETTER 8/1/92 p 0.0391 | TOO FEW 0/0/125 | TOO FEW 0/0/125 | TOO FEW 0/0/57 | TOO FEW 0/0/57 | TOO FEW 0/0/57 | first BETTER 8/1/27 p 0.0391 | TOO FEW 0/0/36 | TOO FEW 0/0/36 |
| MM1-v3.2 + AF4 (THE PICK: registered) | TOO FEW 0/0/101 | NOT DECIDED 3/6/116 p 0.508 | NOT DECIDED 3/6/116 p 0.508 | TOO FEW 0/0/57 | TOO FEW 1/2/54 | TOO FEW 1/2/54 | TOO FEW 0/0/36 | TOO FEW 2/4/30 | TOO FEW 2/4/30 |
| MM1-v3.2 + L3S | MM1-v3.2 BETTER 6/17/78 p 0.0347 | TOO FEW 1/0/124 | TOO FEW 0/0/125 | NOT DECIDED 3/7/47 p 0.344 | TOO FEW 1/0/56 | TOO FEW 0/0/57 | NOT DECIDED 3/10/23 p 0.0923 | TOO FEW 0/0/36 | TOO FEW 0/0/36 |
| MM1-v3.2 + posimb + AF4 | first BETTER 8/1/92 p 0.0391 | NOT DECIDED 3/6/116 p 0.508 | NOT DECIDED 3/6/116 p 0.508 | TOO FEW 0/0/57 | TOO FEW 1/2/54 | TOO FEW 1/2/54 | first BETTER 8/1/27 p 0.0391 | TOO FEW 2/4/30 | TOO FEW 2/4/30 |
| MM1-v3.2 + posimb + L3S | NOT DECIDED 14/18/69 p 0.597 | TOO FEW 1/0/124 | TOO FEW 0/0/125 | NOT DECIDED 3/7/47 p 0.344 | TOO FEW 1/0/56 | TOO FEW 0/0/57 | NOT DECIDED 11/11/14 p 1 | TOO FEW 0/0/36 | TOO FEW 0/0/36 |
| MM1-v3.2 + AF4 + L3S | MM1-v3.2 BETTER 6/17/78 p 0.0347 | NOT DECIDED 4/6/115 p 0.754 | NOT DECIDED 3/6/116 p 0.508 | NOT DECIDED 3/7/47 p 0.344 | TOO FEW 2/2/53 | TOO FEW 1/2/54 | NOT DECIDED 3/10/23 p 0.0923 | TOO FEW 2/4/30 | TOO FEW 2/4/30 |
| MM1-v3.2 + all three | NOT DECIDED 14/18/69 p 0.597 | NOT DECIDED 4/6/115 p 0.754 | NOT DECIDED 3/6/116 p 0.508 | NOT DECIDED 3/7/47 p 0.344 | TOO FEW 2/2/53 | TOO FEW 1/2/54 | NOT DECIDED 11/11/14 p 1 | TOO FEW 2/4/30 | TOO FEW 2/4/30 |

## 7. Each model's error by family, pooled (REPORTED)

The rms of ln(measured / forecast), in percent, over both arms' points (wall cycles at the time-scored points; W over idle given t at points measured at 3 W and above; J at rest given t); each figure equal to verify-e224d's own (n: wall / W / J at rest).

| model | D wall / W given t / J at rest (n) | P | L | all |
|---|---|---|---|---|
| MM1-v3.2 | 5.11 / 6.60 / 2.68 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.35 / 8.82 / 3.65 (36/30/36) | 5.93 / 8.03 / 3.31 (101/117/125) |
| MM1-v3.2 + posimb | 5.12 / 6.60 / 2.68 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.15 / 8.82 / 3.65 (36/30/36) | 5.84 / 8.03 / 3.31 (101/117/125) |
| MM1-v3.2 + AF4 | 5.11 / 6.96 / 3.31 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.35 / 8.80 / 3.67 (36/30/36) | 5.93 / 8.17 / 3.57 (101/117/125) |
| MM1-v3.2 + L3S | 5.02 / 6.63 / 2.70 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.45 / 8.83 / 3.66 (36/30/36) | 5.93 / 8.05 / 3.32 (101/117/125) |
| MM1-v3.2 + posimb + AF4 | 5.12 / 6.96 / 3.31 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.15 / 8.80 / 3.67 (36/30/36) | 5.84 / 8.17 / 3.57 (101/117/125) |
| MM1-v3.2 + posimb + L3S | 5.03 / 6.63 / 2.70 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.25 / 8.83 / 3.66 (36/30/36) | 5.84 / 8.05 / 3.32 (101/117/125) |
| MM1-v3.2 + AF4 + L3S | 5.02 / 7.00 / 3.34 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.45 / 8.82 / 3.68 (36/30/36) | 5.93 / 8.19 / 3.58 (101/117/125) |
| MM1-v3.2 + all three | 5.03 / 7.00 / 3.34 (57/55/57) | 3.77 / 9.38 / 3.87 (8/32/32) | 7.25 / 8.82 / 3.68 (36/30/36) | 5.84 / 8.19 / 3.58 (101/117/125) |
| MM1-v3.1 | 5.56 / 12.24 / 5.09 (57/55/57) | 3.29 / 8.71 / 3.64 (8/32/32) | 7.84 / 15.09 / 5.91 (36/30/36) | 6.34 / 12.23 / 5.03 (101/117/125) |
| MM1-v3 | 5.46 / 12.25 / 5.08 (57/55/57) | 3.36 / 4.09 / 1.80 (8/16/16) | 7.70 / 15.05 / 5.91 (36/30/36) | 6.23 / 12.32 / 5.05 (101/101/109) |
| MM1-v2 | 7.13 / 13.89 / 5.51 (57/55/57) | 2.86 / 7.60 / 2.74 (8/16/16) | 8.71 / 14.66 / 5.72 (36/30/36) | 7.51 / 13.34 / 5.27 (101/101/109) |

## 8. What the two arms say together (REPORTED, post hoc)

- **THE PICK on its own points.** Over all points AF4 lowers W over idle's rms on arm A (aifoundry1 card 1) from 9.56% (MM1-v3.2) to 9.06% and raises it on arm B (aifoundry2 card 0) from 6.31% to 7.26% (pooled 8.03% against 8.17%). By HP2's rule, at the 10 points AF4 acts on, MM1-v3.3 is closer at arm A's d29, arm A's g03, arm B's g01, MM1-v3.2 at arm A's g01, arm A's g02, arm B's d29, arm B's d30, arm B's g02, arm B's g03, and arm A's d30 ties (section 6 of notes 2 and 19); and at the three lead points g01-g03 the measured excess over the cooperative twin is 6.17-7.45 W on arm A and 6.62-8.16 W on arm B, against F3's 1.28-1.51 W and 3.53-7.88 W and AF4's 0.44-4.85 W and 2.30-9.66 W (section 10 of notes 2 and 19).
- **Time.** No term moves a wall-cycle forecast of the pick (AF4 acts only in energy); MM1-v3.2's pooled wall rms is 5.93% (MM1-v3 6.23%, MM1-v3.1 6.34%, MM1-v2 7.51%).
- **The switch inputs at new shapes.** With the counts MM1-v3.2's pattern-point W over idle reads 12.38% rms against the null's 30.95%, and the data-dependent share 16.34% of D against 45.07%.

## 9. verify-e224d's re-derivation, beside (its own code; verdict HOLDS WITH FIXES)

verify-e224d's own scorer equals the frozen scorer's two-arm run at `c661275c` in 1,662 of 1,662 values (the pick's rules 237 of 237), and its run of the frozen scorer is this file byte for byte (section 2). This lane: step 13 and the picked and pooled runs made again from committed bytes, 35 comparisons SAME; the facts 45 of 45 OK (every pooled count, p, verdict, switch-rule case and family figure re-made by the frozen scorer's functions, equal to its JSON and to verify-e224d's own).

## 10. Findings, answered as dated clauses (Sat 21 Nov 2026, after the data; post hoc; nothing re-scored)

1. **info, the pooled reading (verify-e224d's finding 5).** No card lane scored the pooled rules: the kit's step 13 scores its own arm alone, and both ran before THE PICK. **Answered here:** the frozen scorer's two-arm run with the lab holding E222's scores, committed byte for byte as verify-e224d made it.
2. **info, the double label.** Every pooled verdict reads `[labelled: R0 FAIL] [labelled: R0 FAIL]`: the scorer appends each arm's label (both arms failed R0). It is one label, R0 FAIL, from both arms; nothing else is meant.
3. **info, the energy head-to-heads.** HP2 and HP3 read NOT DECIDED (3/6/116), where the registration gave a pick holding AF4 a power of 0.35-0.67: by HP2's rule (HP3's counts are the same), at the 10 points AF4 acts on, MM1-v3.3 is closer at arm A's d29, arm A's g03, arm B's g01, MM1-v3.2 at arm A's g01, arm A's g02, arm B's d29, arm B's d30, arm B's g02, arm B's g03, and arm A's d30 ties. *Lead (post hoc, REPORTED):* at the three lead points g01-g03 the measured excess over the cooperative twin is 6.17-7.45 W on arm A and 6.62-8.16 W on arm B, against F3's 1.28-1.51 W and 3.53-7.88 W and AF4's 0.44-4.85 W and 2.30-9.66 W; a next gemmLnc candidate would be declared, fitted and frozen before a blind day of its own.

## 11. What this note does not do

It changes no committed file, datum, forecast, point, band, tie, rule, label or verdict; it does not re-choose THE PICK or lift R0's label; it scores no forecast of the model session's; and every composition but the pick is REPORTED only.

## 12. `SHA256SUMS-note20`

`SHA256SUMS-note20` lists the three files this note adds (this note among them), then `SHA256SUMS-note19`; `sha256sum -c SHA256SUMS-note20` from this directory reads every line OK.
