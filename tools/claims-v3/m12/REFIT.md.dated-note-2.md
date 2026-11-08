# REFIT.md, dated note 2: the verifier's faults - his pair is in-sample by construction, not held out; 8 of E178's 40 kinds were fitted by word in E182; both train noises; H16 rests on F16-SAME; the int8 session anchor; the Builds-on check; the nits (Sun 8 Nov 2026, PST; Q158)

*Written Sun 8 Nov 2026 from 06:23 PST by the Intel's clock, desk only, by Q158's fix lane for M12, after the adversarial verifier of M12
(verify-m12, 05:37-06:05 PST) read the rules (`d5eb87b5`, git 04:56:09 PST) and the model, held-out test and candidates (`8b85b498`, git
05:11:13 PST). Its verdict: holds with fixes, 1 major fault (blocking: a label), 5 minor faults and 2 groups of nits. This note answers each
in the verifier's order. **It changes no number, rule, parameter or forecast of M12 and edits no committed file: each wrong label is
corrected here.** Every model figure below is re-derived from committed files by [`note2_m12.py`](note2_m12.py) (output
[`note2-m12.json`](note2-m12.json), key named beside each figure, and [`logs/note2-m12.txt`](logs/note2-m12.txt)). The clock times in
sections 6 and 8 come from records that are not committed: the clone's file times, the round's slot log and the m12-refit lane's
transcript. At lab `13a4b34d`, M12's own three check modes, its self-test and its two hash lists re-pass
([`logs/note2-checks-m12.txt`](logs/note2-checks-m12.txt)).*

## 0. What a registration takes

- **Take `candidates-m12.json` as frozen, unchanged:** Sun 8 Nov 2026 05:07:07 PST, sha256
  e97a2ae4fb27d6d161d1fd209f13a7fad91c10c1455a86b984625862fb734907 ([`FREEZE-m12.md`](FREEZE-m12.md)).
- **No candidate forecast is wrong as committed.** The blocking fault labels a held-out number; it is not a forecast. Faults 3-5 change no
  forecast value. So no corrected candidate file is frozen, and there is no `candidates-m12.1`.
- A registration that takes the file also states:
  - the int8 kinds' absolute levels are scored only with a registered session anchor, and the 14 trains as frozen (section 5);
  - H16 carries a stated fp16-scaled arm beside F16-SAME and M10 (section 4);
  - power and separation at both train noises (section 3);
  - its own Builds-on block, with the date the stock-take's inventory was read and its rows (section 6).

## 1. Fault 1 (major, blocking): his pair is in-sample by construction, not held out

M12's forecast of his pair is E182's T1: the same contrast on the same kinds. M12's int8 fit is pinned to T1.

| what | value | label | source |
|---|---|---|---|
| T1's kinds (A word / B word) | int8.e178_v5 (0x05050505 / 0x05050505) minus int8.e178_v4 (0x04040404 / 0x04040404) | | `note2-m12.json` > `f1_his_pair` > `T1_words` |
| E178-H-int8's kinds | the same two, the same words | | > `E178_H_int8_words`, `same_kinds_and_words` true |
| E182's T1, rule E182-HT | +0.0470 W [+0.0403, +0.0537], se 0.0033; POSITIVE, REPEAT AGREES, SIZE FAIL HIGH under P, P + ACC and E | blind, registered | E182's `trains-e182.json` > `trains` > `T1`; `scored.json` > `rules` > `E182-HT` |
| T1's leverage in M12's int8 fit | 0.953 (T2 0.980, T3 0.993, T4 0.015) | post hoc | > `trains_leverage` |
| M12's in-sample T1 | +0.047035 W (z -0.01) | post hoc | `m12.json` > `int8` > `in_sample` > `trains` > `T1` |
| k_walk | fitted 1.2391 fJ (se 0.139); from T1 alone 1.2376 at M12's betas, 1.2392 at E182-A's and E182-B's | post hoc | > `k_walk_*` |
| M12's pair on E178's rows | +0.047023 W (se 0.0032), T1's measured value plus 0.000022 | post hoc, in-sample by construction | `heldout-m12.json` > `his_pair_E178` |
| E178-H-int8 | +0.0532 W [+0.0217, +0.0848]; M10's P +0.1857, SIZE FAIL HIGH | blind, registered | E178's `scored.json` > `primary` > `rules` > `E178-H-int8` |

- **The corrected label:** his pair under M12 is **post hoc, in-sample by construction: E182's T1 contrast, already scored blind as E182-HT
  REPEAT AGREES**.
- "M12 +0.047 inside E178's [+0.022, +0.085], M10 +0.186 outside" restates two blind, registered results of the runs themselves:
  - E182-HT's REPEAT AGREES: E182's T1 estimate lies inside E178-H-int8's interval (E182.md section 5's rule);
  - E178-H-int8's SIZE FAIL HIGH against M10's P.

  It says nothing new about M12.
- **The records and the kinds page never quote it as M12's held-out success against M10,** and it never counts in M12's held-out score.
- **Where the wrong label stands** (unedited, corrected here):
  - README.md's title line, its held-out section, its labels and its "What it does to predicting power" (which counts his pair among
    what M12 "carries ... held out");
  - heldout-m12.md's "His pair" line (line 5);
  - REFIT.md sections 4 and 6;
  - `8b85b498`'s commit subject;
  - heldout-m12.json's top-level label, "held out, post hoc", which covers `his_pair_E178`.

  README.md and heldout-m12.md each get a pointer (their dated notes 1).

## 2. Fault 2 (minor): 8 of E178's 40 held-out kinds were fitted by word in E182

E182 ran the words of 8 of E178's 40 kinds, so those words entered M12's fit:
- int8: ones, neg_ones, e178_v4, e178_v5, e178_a4_b5, e178_a5_b4;
- fp32: e178_v4, e178_v5.

For those 8, the held-out test is a session transfer: the same words, read in another session. It is not the model reaching new kinds. The
other 32 are new to M12.

All rows below are held out, post hoc (`note2-m12.json` > `f2_shared_kinds`). The bootstrap is `heldout_m12.py`'s own: 2,000 draws,
`random.Random(1570)`. It reproduces the committed 40-kind interval exactly.

| E178 rows | n | M10 rms (bias), W | M12 rms (bias), W | centred rms, M10 -> M12 | 0 inside, M10 -> M12 | rms(M12) - rms(M10) [95%] |
|---|---:|---|---|---|---|---|
| all (as committed) | 40 | 0.1218 (-0.014) | 0.0678 (-0.038) | 0.121 -> 0.056 | 19 -> 32 | -0.054 [-0.083, -0.024] |
| **new to E182** | 32 | 0.1205 (+0.001) | **0.0604** (-0.033) | 0.121 -> 0.050 | 17 -> 28 | **-0.060 [-0.096, -0.023]** |
| also fitted by E182 | 8 | 0.1270 (-0.071) | 0.0915 (-0.059) | 0.105 -> 0.070 | 2 -> 4 | -0.035 [-0.071, +0.001] |
| int8, new | 7 | 0.217 (-0.190) | 0.086 (-0.081) | 0.104 -> 0.028 | 1 -> 4 | -0.131 [-0.207, -0.051] |
| int8, also fitted | 6 | 0.137 (-0.125) | 0.100 (-0.098) | 0.056 -> 0.016 | 1 -> 2 | -0.037 [-0.081, +0.009] |
| fp32, new | 12 | 0.091 (+0.082) | 0.037 (+0.022) | 0.038 -> 0.030 | 5 -> 12 | -0.054 [-0.072, -0.034] |
| fp32, also fitted | 2 | 0.092 (+0.089) | 0.062 (+0.060) | 0.022 -> 0.014 | 1 -> 2 | -0.030 [-0.038, -0.021] |
| fp16 (all 13 new) | 13 | 0.054 (+0.029) | 0.061 (-0.058) | 0.046 -> 0.021 | 11 -> 12 | +0.007 [-0.026, +0.034] |

- **The claims hold on the 32 new kinds:**
  - M12 halves M10's error (0.121 -> 0.060 W);
  - it carries int8's shape (centred 0.104 -> 0.028);
  - it reads all 12 new fp32 kinds inside.
- On the 8 fitted kinds the gain is not resolved.
- **The committed 40-kind figures stand,** labelled held out, post hoc, with this split beside them.

## 3. Fault 3 (minor): the trains' noise, registered and measured

**The noise the candidates used:** E182's registered train half-width, 0.0051 W at 32 units (se 0.00250 W;
`candidates-m12.json` > `train_noise`), for every train. They call it "E182's train noise".

**What E182's trains measured** (`note2-m12.json` > `f3_train_noise` > `se_measured_each_w`):
- int8, T1-T4: se 0.00330, 0.00219, 0.00247, 0.00257 W. The median, 0.00252, matches the registered noise.
- fp32, T5 and T6: se 0.00298 each, the mean 0.00298. That is higher than the registered noise.
- fp16: E182 ran no fp16 train. fp32's measured noise stands in for H16 (df 37 at 38 units).

Each power and separation below uses candidates_m12.py's formulas, with each train's half-width its se times t(0.975, df).

| train | M12 (se), W | M10, W | separation, registered -> measured | power if M12, registered -> measured |
|---|---|---:|---|---|
| H16 | +0.2051 (0.0026) | 0 | 57.0 -> 52.0 | 1.00 -> 1.00 |
| S23 | +0.1640 (0.0021) | 0 | 50.6 -> 45.2 | 1.00 -> 1.00 |
| S15 | +0.0820 (0.0010) | 0 | 30.3 -> 26.0 | 1.00 -> 1.00 |
| Q63-sign | +0.0292 (0.0017) | -0.0471 | 25.2 -> 25.1 | 1.00 -> 1.00 |
| Q63-swap | +0.0073 (0.0016) | +0.0785 | 24.2 -> 24.0 | 0.78 -> 0.77 |
| B23-B15, B15-B7 | +0.1405, +0.1261 (0.0069) | +0.0343, +0.0199 | 14.5 -> 14.2 | 1.00 -> 1.00 |
| Q3-sign | +0.1080 (0.0021) | +0.0785 | 9.0 -> 9.0 | 1.00 -> 1.00 |
| Q3-swap | +0.0015 (0.0003) | +0.0157 | 5.6 -> 5.6 | 0.08 -> 0.08 |
| A23-A15, A15-A7 | +0.0585, +0.0441 (0.0069) | +0.0343, +0.0199 | 3.3 -> 3.2 | 1.00 -> 1.00 |
| EB, EA | -0.0023 (0.0000) | -0.0023 | 0 -> 0 | 0.13 -> 0.10 |
| X8 | +0.1510 (0.0137) | +0.1553 | 0.3 -> 0.3 | 1.00 -> 1.00 |

- No forecast value changes.
- At the measured noise, the suggested first subset keeps its order: H16, S23, Q63-sign, Q63-swap, B23-B15, A23-A15, EB.
- A registration quotes both noises.

## 4. Fault 4 (minor): H16 holds only if F16-SAME does

- **What H16's frozen se covers:** 0.0026 W, M12's parameter se, which comes from fp32's placement alone. It leaves out F16-SAME's own
  extrapolation: E182 ran no fp16 kind.
- So H16's "power 1.00, separation 57" assume F16-SAME.
- The committed held-out fp16 rows already read F16-SAME's level about 0.06 W high (bias -0.058 W; `heldout-m12.json` > `groups` >
  `E178 fp16 (13)`). candidates-m12.md does not show this.
- **Post hoc, reported:** a regression through 0, fitted on E178's 13 fp16 kinds, which therefore no longer test it
  (`note2-m12.json` > `f4_fp16`):
  - What is regressed: e = D - (P10 + c_f) on M12's held-bit increment, gamma_A pc_A + gamma_B pc_B.
  - fp16 shows **0.497 (se 0.086)** of F16-SAME's level a bit.
  - fp32's own 14 kinds give 1.202 (se 0.135).
- **H16 at that fraction:**
  - The fraction measures fp16's level, not its placement: 11 of the 13 fp16 rows hold equal A and B words.
  - If fp16's placement scales with its level, H16 reads **+0.102 W (se 0.018) [+0.067, +0.136]**.
  - At fp32's measured train noise, with each arm's own se combined, that value sits 5.7 se from M10's 0 and 5.7 se from F16-SAME's
    +0.205.
  - So H16 still tells the three apart, and it stays a valid test, as committed.
- **A registration that takes H16** states an fp16-scaled arm beside F16-SAME and M10, and freezes its value and se itself.

## 5. Fault 5 (minor): the int8 kinds' absolute levels need a session anchor

- The frozen int8 candidate kinds' absolute levels carry E182's session level: c8 +1.682 W, se 0.014 (`note2-m12.json` >
  `f5_int8_session`).
- **E178's D minus E182's**, on the six int8 kinds both sessions ran: -0.048 to -0.113 W, mean -0.094.

  | kind | E178 - E182, W |
  |---|---:|
  | e178_a5_b4 | -0.113 |
  | e178_a4_b5 | -0.112 |
  | ones | -0.108 |
  | e178_v4 | -0.105 |
  | neg_ones | -0.081 |
  | e178_v5 | -0.048 |

- M12's bias on E178's 13 int8 kinds is -0.089 W, and arm M12-S1's shift is -0.074 W.
- FREEZE-m12.md's "What a registration would still owe" leaves this out; only the README's "What remains" names it.
- **The rule a registration states:**
  - The int8 kinds' absolute levels are scored only with a registered session anchor, in M12-S1's form: c8 moved by the session's own
    int8.full anchor against E182's.
  - The 14 trains, each a difference inside one session, are scored as frozen.

FREEZE-m12.md gets a pointer (its dated note 1).

## 6. Fault 6 (minor): the Builds-on block's "Checked" item

- **What item 1 says:** REFIT.md section 1, item 1 names the stock-take's rule. It gives neither the date the inventory was read nor any
  row.
- **The inventory was not read before the rules.** None of the m12-refit lane's tool calls names it: this lane read the tool inputs in
  that lane's workflow transcript, read only. Item 1 states the rule; it is not a check.
- **Read now, post hoc:** this is after the rules, the fit and the freeze, so it is not the block's own check. This lane read the
  stock-take's inventory on Sun 8 Nov 2026, between about 06:10 and 06:14 PST.
  - Public rows read: H09, H16, H20, H21, H24, H27, L23, P12, P29. The row ids are opaque pointers into a private inventory.
  - Pieces newer than the inventory (5 Nov) are cited by commit in REFIT.md section 1, item 2.
- **Taken,** each already by commit in item 2:
  - H09: the toggle bench, for the candidates' counts;
  - H21: M10;
  - H24: pool 8's class S, held out;
  - H27: E178, held out, and its flip model;
  - P12: the open RTL, through E178's flip model and accum.c;
  - P29: Verilator, for the bench.
- **Not used:**
  - row H16 (int8's Booth on B; not the candidate train H16): M12's int8 terms take E178's flip classes and per-side held bits, and add
    no recoding term.
  - H20 and L23 (the single-bit price lists by format and side): earlier measurements of per-side bit prices, neither used nor checked
    here. A registration that takes the candidates owes a check of M12's fp32 side ratio (B's held bit 4.4 times A's) against them, at
    their operating point.
- **Any registration that takes the candidates carries its own full block.**

## 7. Fault 7 (nits, code): re-checked here; no figure changes

1. **The flip model on all 24 of E182's kinds.** The code checks 3 of them. Run here on all 24, with E178's flip model compiled unchanged:
   24 of 24 equal forecast-e182.json's launch means (`note2-m12.json` > `f7_code_nits` > `a_flip_model_all_E182_kinds`).
2. **The reference tile's bench row.** The code never checks fp32.e182_a1_b3fffffff's row. It equals E182's committed counts
   (`tools/claims-v3/e182/bench/counts-e182.json`): the mean and all 3 points. The three zeros rows and fp32.ones equal E178's, mean and
   points (> `b_reference_rows`).
3. **M10's int8 rate.** M10's int8 column used E182's mean int8 rate, 1.920619e9 /s, where REFIT section 5 says median rates.
   - The median is 1.920658e9 /s (+0.0020%).
   - At the median, M10's int8 kinds move at most 4.1e-5 W and its int8 trains 3.2e-6 W (> `c_M10_int8_rate`).
   - M12's own int8 column uses the mean, by REFIT section 2's rule.
   - The rates used differ from E182's registered rates by +0.0084% (int8), +0.0026% (fp32) and -0.0042% (fp16).
4. **The two power forms.** The candidates' power includes M12's se, and their separation divides by the train's se combined with M12's,
   as candidates-m12.md says. REFIT section 5 says "in units of the train's se".
   - By REFIT's letter, at the registered noise, every separation is larger (> `f3_train_noise` > `trains` >
     `REFIT_letter_train_se_alone`):

     | train | separation by REFIT's letter |
     |---|---:|
     | H16 | 82.0 |
     | S23 | 65.6 |
     | B23-B15, B15-B7 | 42.5 |
     | S15 | 32.8 |
     | Q63-sign | 30.5 |
     | Q63-swap | 28.5 |
     | Q3-sign | 11.8 |
     | A23-A15, A15-A7 | 9.7 |
     | Q3-swap | 5.7 |
     | X8 | 1.7 |
     | EB, EA | 0 |

   - The committed, combined form is the more cautious one, and it stands.
5. **sigma_K's denominator,** which REFIT does not state. The code divides by n_K less the kinds rows' leverages, 17.94 effective degrees
   of freedom, and iterates (m12_common.joint_fit). Under n_K - p (15):
   - k_walk moves +1.9e-5 fJ and k_scp +8.7e-4 fJ;
   - the betas move -3e-6 W and c8 +1.7e-5 W.

   Under n_K - 1 and n_K the moves are smaller and of the other sign (> `e_sigma_K_denominator`).
6. **The one-base-word scope.** The code never checks it. All 13 of E171's class S tiles hold one word on one side and two words one bit
   apart on the other (> `f_one_base_word_scope`):
   - fp32: the two words' xor has one bit;
   - fp16: one bit in each half.

## 8. Fault 8 (nits, records), one line each

- **The bench build:** no committed M12 file records the build's hash. "Vtb a740318c..." rests on the lane's uncommitted check and on the
  reference rows above. Checked read only after the fact, through `run_remote --host mini` at 06:14:26 PST: the build directory the run
  named holds Vtb, accum, settle_count and run_kinds.py with the committed build record's hashes, each last modified before the run
  ([`logs/note2-bench-build-m12.txt`](logs/note2-bench-build-m12.txt); the record is
  `docs/reports/data/2026-11-04-q141t-s7-recount/step243/build-record-mini.json`). Post hoc.
- **Dated note 1** went into `8b85b498` (git 05:11:13) with the forecasts, so its "before any forecast" rests on the clone's file time
  (05:02:56) and the round's slot log (the stage re-run at 05:03:00, the forecast at 05:05:34), not on git order.
- **heldout-m12.md's bold GAIN and OFFSET** need the README's caveat too: the rule's bootstrap holds the measured values fixed, so the
  words test no noise. They are reported, never a verdict.
- **README.md's "the placement and held-bit terms carry E178's one-number kinds"** overstates the placement (`note2-m12.json` >
  `f8_records` > `placement_on_E178_fp32`).
  - The placement part, (gamma_B - gamma_A)(pc_B - pc_A)/2, is 0 on 12 of E178's 14 fp32 kinds, which hold equal A and B popcounts.
  - It enters only the two crossed kinds: e178_a4_b5 at +0.0051 W and e178_a5_b4 at -0.0051 W.
  - What carries the 14 is the held-bit level, (gamma_A + gamma_B)(pc_A + pc_B)/2: 0.016-0.130 W.
- **REFIT section 6's list of what was seen before the rules** leaves out three reads; add them:
  - E178's results.md and the first 60 lines of its README (04:35:28 PST);
  - E171's README, lines 60-130 (04:42:43 PST).

## 9. The labels, number by number, as corrected

| number | label |
|---|---|
| E178's 40 kinds (all, by format, the paired intervals) | held out, post hoc. 8 are a session transfer (fitted by word in E182); the 32 new ones are the model's held-out test (section 2) |
| his pair, E178-H-int8, under M12 | post hoc, in-sample by construction (E182's T1, scored blind as E182-HT REPEAT AGREES); not held out |
| pool 8's class S, both cards | held out, post hoc |
| arm M12-S1 | post hoc in the strong sense, reported |
| the gain/offset words | reported |
| the candidates' forecasts | forecast, frozen; not registered; blind for a run only once a registration commits them before its first datum |
| this note's figures | post hoc |
| the fp16 fraction and H16's fp16-scaled value | post hoc, reported |

Nothing in M12 is registered or blind. The only blind, registered numbers here are the runs' own verdicts, E182-HT and E178-H-int8.

## 10. Files

New files only, in this directory:
- this note;
- [`README.md.dated-note-1.md`](README.md.dated-note-1.md), [`heldout-m12.md.dated-note-1.md`](heldout-m12.md.dated-note-1.md) and
  [`FREEZE-m12.md.dated-note-1.md`](FREEZE-m12.md.dated-note-1.md): pointers to sections 0-5 and 8;
- `note2_m12.py`, the re-runs, with a `--check` mode, which writes `note2-m12.json` and `logs/note2-m12.txt`;
- `logs/note2-checks-m12.txt`, re-run at lab `13a4b34d`: note2_m12.py's check, M12's three check modes, its self-test and its two hash
  lists;
- `logs/note2-bench-build-m12.txt`;
- [`SHA256SUMS-m12-note2`](SHA256SUMS-m12-note2), covering every file above.

Nothing committed is edited. SHA256SUMS-m12 (37 of 37) and SHA256SUMS-m12-rules (1 of 1) still pass.

SPDX-License-Identifier: Apache-2.0
