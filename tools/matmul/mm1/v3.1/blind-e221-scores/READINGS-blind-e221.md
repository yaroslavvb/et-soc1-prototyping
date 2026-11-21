# blind-e221: the scorer's readings where decl-e221's declaration is silent, stated BEFORE the read

*Lane blind-e221 (round Q235), aifoundry2's desk; written Fri 20 Nov 2026, Pacific time, after the measured-conditions forecasts were
hashed (17:52:57 PST, logs/step2-sha256.txt) and before any E221 measurement field is read. It is hashed with the scorer
(`scripts/s03_score.py`) in logs/step3-scorer-sha256.txt before the scorer's first read. Labels: registered (decl-e221's declaration),
desk, REPORTED (printed beside, deciding nothing). Nothing here changes a band, a tie, a model, a forecast, a case or the pass rule.*

The declaration (DECLARED-blind-e221.md 9cd8256b, .json b483f46c; FROZEN.txt 2df06f06; posted #15.2.1.1) names its form: "as
unread-e214, decl-e217 and decl-e219 did". Where it does not spell a step out, the scorer takes that form's reading (blind-e219's
scorer, verified by verify-blind-e219), as follows.

## R1. Which runs are read for time (not stated in decl-e221; decl-e219's section a, the form)

MM1's own loader conditions (data_v31.mms_runs_all = data_v3.mms_runs, line for line), applied to the 811 listed runs: the run ran,
its role is not null, it has an arm, its values are `gemmL<MB>x<NB>x<KB>:...` and its shires are present, and the primary view
(band600 on card 1, win on the governed cards) has T_op_us, cyc_op_max and n_launch >= 1; and the session's queue entry says ran,
rc 0 (every rc 0) and check exact or approx (decl-e219's queue condition). The scorer checks its selection and its readings against
MM1-v3.1's loader on the same bytes, and prints how many runs the queue condition removes beyond the loader's (if any).

## R2. Which runs are read for energy (not stated in decl-e221; data_v31.mms_runs_all's energy condition, E221's registered capped rule)

The same, and the primary view's dP_w is not None, its p_mean_w is truthy, the run is not capped and its role is not 'time'.

## R3. "At least 90% of its cases pass"

Integer arithmetic: a rule PASSES when 10 x passed >= 9 x n (0.9 x n in floating point is 99.00000000000001 at n = 110).

## R4. The test's NO DATA line (decl-e219's reading, verified by verify-blind-e219)

NO DATA only when no case is compared; TOO FEW under 10 untied cases (a comparison whose cases all tie reads TOO FEW).

## R5. The twin key's clock

The mean of the case's listed runs' start-of-run clocks (the primary view's kclock_mhz, step 2a), rounded to the nearest 25 MHz as
int(round(f / 25) x 25). At E221's measured clocks every case reads the nominal 25 MHz step (card 1 600; the governed cards 800), so
the twins equal the declaration's preview (MM1-v3.2 35 time / 31 energy, v3.1 17 / 15, v3 17 / 15, v2 8 / 8: checked, step 2c).
The composed forms carry their base model's flags (the terms and controls MM1-v3.1's, the two candidates MM1-v3.2's).

## R6. The watts set on each footing

A case is a WATTS case when its mean MM1-v3.2 W given t (over the case's energy runs) or its mean measured dP_w is under 3 W; the set
is the same for every model on a footing. On the nominal footing the set is fixed by that footing's MM1-v3.2 W given t; the number of
cases whose set differs between the footings is printed.

## R7. The label's times

The freeze post's time is the later of the round's record line (out/orch/q235-frozen-posts.txt: 06:22:58 PST) and the post's own
time (out/orch/discussion-seen-q188.json: 06:22:53.507 PST): 06:22:58. A session's first datum is its first card command, read as the
queue's t_first_ms (the session's own record), the README's stated time printed beside. A session is BLIND when its first datum and
the claim it ran under (the last CLAIM line for its key at or before its T0, out/orch/e221-releases.txt) both come after the freeze
post. The stopped first S1 start (05:53:56-05:55:27, no run; its folder never copied) is not a committed session and is not scored.

## R8. The REPORTED tables' forms

- **Classes:** each class's rms and bias per card (and pooled) for every model, no twin and all.
- **Mask ladders:** each MASK subset case against its whole-chip twin (same card, arm, format, kind at 0xffffffff): the measured
  ratio of the case-mean cycles an op (wall; counter mean) and each model's forecast ratio of its case-mean forecasts (over the runs
  read for time); error = forecast ratio / measured ratio - 1; rms and bias per placement family and per card and family.
- **Governed clocks:** on aifoundry1 card 0 and aifoundry2 card 0, every run's measured clock beside the nominal 800 MHz, with
  MM1-v3.2's per-run wall error on both footings (and E1 at 3 W and above).
- **Per class comparisons** (D0-D2 and D3 per class, D3c per class): the same sign test on the class's cases, REPORTED.
- **D3c:** MM1-v3.2+posimb vs MM1-v3.2 on the 461 subset-mask cases (H1, H2); MM1-v3.2+L3S vs MM1-v3.2 on its 272 full-mask cases
  (H1-H5); each candidate vs MM1-v3.1 beside on the same cases. REPORTED, deciding nothing.

## R9. One departure in how a frozen maker is loaded (not in what it computes; step 2b's docstring)

layout2's as-run h01_freeze.py and f02_private.py hard-code their lane folder, whose lab clone the orchestrator's 16:07 cleanup removed,
so they no longer import. The forecasts were made with the LANDED copies (tools/matmul/mm1/v3.3-cands/posimb/scripts, equal to the
as-run files but for the LANE and REG path lines, by SCRUB.json and a line diff), with LAYOUT2_LANE set to a stand-in folder (the
landed f02_private.py and this lane's archive of main). The maker's four checks re-made decl-e221's figures to the last digit (posimb's
306 frozen E220 rows exactly), and the code re-made decl-e221's frozen nominal forecasts bit for bit (214,915 fields, 0 differ).

## R10. Earlier reads, disclosed

Before this file: the conditions (step 2a: only the declared start-of-run fields; their ranges printed: clocks 797.6-799.3 MHz on the
governed cards and 599.2-599.5 MHz on card 1, minion 499-621 mV, die 40-47 C, one run without a minion rail reading); the key names of
one session's queue.json and the counts of its rc and check values (a1c1-S1: rc 0 on its 92 runs, check exact 82 / approx 10, 4 nulls);
the file names of one session's data folder. No time, cycles, power, energy or seconds field has been read.

SPDX-License-Identifier: Apache-2.0
