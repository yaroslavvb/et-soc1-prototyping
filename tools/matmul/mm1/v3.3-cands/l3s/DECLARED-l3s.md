# DECLARED: MM1-v3.2 + L3S, the L3's set overflow for the A operand (an MM1-v3.3 candidate)

*Lane l3-edge, round Q234, Fri 20 Nov 2026, Pacific time. Written at aifoundry2's desk before the term's one constant was fitted:
nothing below was chosen after a fit of lam. Desk only: no card, no simulator. Interpreter: /usr/bin/python3 3.12.3, numpy 1.26.4,
scipy 1.11.4, single-threaded (OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = NUMEXPR_NUM_THREADS = 1), every job inside the
round's CPU slots. No E220 datum was opened; E220's point list (reg-e220's POINTS.txt, final 05:24:17 PST) was read for its points only.*

Labels as MM1's records use them: *registered* = in this file before the fit; *post hoc* = after its data existed; *held out* = left out
of the fit that scores it; *blind* = scored on data that did not exist when the forecast was frozen; *REPORTED* = printed, never deciding.
Error = ln(forecast / measured), rms and bias in % (of that log).

## 1. The lead

gemmL2x1x7 (a 39 MiB GEMM: A 28, B 7, C 4 MiB) ran 12.7-14.9% slower than MM1-v3.1 forecast on aifoundry3 card 0 and aifoundry1 card 1
(E215, report v2's verify finding M4). MM1-v3.2's own held-out op times there (its LOEO E215 fold, `tools/matmul/mm1/v3.2/out/points_time_v32.csv`)
are 13.8-15.5% low at all four points (fp32 and int8, both cards); gemmL3x1x7 (55 MiB) and gemmL1x1x7 (23 MiB) are within 0.1%.

## 2. The mechanism (what is known, what is assumed, what the walk shows)

**Known (public sources, read this round):**
- the L3 in the shire cache's reset mode M0: 1 MB a shire, 32 MB in all; the line's home shire PA[10:6] (the lab's own measurement,
  `docs/et-soc1-notes.md`, agrees); 4-way set-associative, 64-byte lines, write-back and write-allocate, true LRU per set; the set
  index within the home: bank PA[12:11], sub-bank PA[14:13], set PA[22:15] (256 sets a sub-bank in M0). So the chip's 2^17 L3 sets are
  indexed by PA[22:6] and repeat every 8 MiB: an 8 MiB stretch of addresses puts one line in every set, and a set holds 4
  (the public core-et repository's `docs/CORE-ET-Shire-Cache-Specification.pdf`, sections 1.1, 1.3 tables 4-7, 1.4.1.2 and 2.14.4; the
  lab's notes cite the same document);
- the kernel's addresses and order (MM1-v3.1's walk, `tools/matmul/mm1/v3.1/walk/walk/walk_v31.py`, checked EXACT against traced
  simulator runs at 448 of 448 working harts): per op step the chip asks 32 distinct A tiles and 32 distinct B tiles (1 KiB each, 16
  lines), and stores every minion's C tile after each row half;
- rgm136's host allocates the C pool (MB NB 2 MiB), then A (MB KB 2 MiB), then B (KB NB 1 MiB) through the runtime's 4 KiB-block
  allocator (`tools/claims-v3/e136/rgm136/host/main.cpp` testArm; et-platform's MemoryManager), so A starts |C| after C and B |A|
  after A.

**Assumed (not measured here):** the card runs mode M0 (the reset mode; the lab's notes and the memory-levels design say M0's split);
one arm a device process, so the three pools sit contiguous in that order (a shift of all three only permutes the sets); a tile's 16
lines share its fate (they fill 16 consecutive sets of the same 8 MiB position); the chip in lock step as the walk counts it, one
L3 request a distinct tile a step; the shires' L2 hits at KB <= 2 counted as L3 accesses (the model has no L2); the B operand's extra
retention past the edge (MM1-v3.2's plateau, pB) not modelled; DRAM pages, bandwidth and time not modelled.

**What the walk shows (desk, no fitted constant).** At NB = 1 and MB >= 2 every A tile is used once a pass, so its exact LRU stack
distance is the pass's whole footprint: 39.0 MiB at gemmL2x1x7 (MM1-v3's closed form says 38.5), B's 15.0 MiB. A fully associative
32 MiB LRU would miss every A tile there; MM1-v3.2's retention (x1 37.33 MB, w1 2.39 MB) keeps 38% of them; the 4-way set-associative
L3 above, driven by the kernel's own addresses (`l3s_feature.py`, sha256 below), keeps 14.3%: only the sets whose 8 MiB position
holds at most 4 of the pass's lines keep their A lines (C 1 + A 3 or 4 + B 0 or 1 lines a set here). The measured op times imply about 3%
(post hoc, from MM1-v3.2's own class prices). Just past 32 MiB, whole-pass (cyclic) reuse falls off the cliff that LRU has under
cyclic access, set by set: the retention is a property of how many lines each 8 MiB position holds, not of a smooth function of the
distance.

**Looked at before this declaration (post hoc exploration of committed data, disclosed; lam was not fitted):** at 338 full-mask
rgm136 gemmL points with KB >= 3 and footprints of 25-60 MiB (E105-E215 in MM1-v3.2's table), MM1-v3.2's all-data op times read
3.92% rms; the same points priced by MM1-v3.2's own constants with A's place taken from the set model (B kept as MM1-v3.2 has it)
3.62%; with every place from the set model 7.90% (the set model is far too pessimistic for B, which is why the term leaves B alone).
The set model is too pessimistic for A as well at small overflows (gemmL2x1x6, 34 MiB: 75% kept against about 89% implied;
gemmL1x1x12, 38 MiB: 25% against about 36%), right at gemmL1x1x10 (32 MiB, 100%), gemmL1x1x11 (35 MiB, 68% against about 70%),
gemmL1x1x13 (41 MiB, 0%), gemmL3x1x5 (41 MiB, 0%), gemmL4x1x4 (44 MiB, 0%). Hence one weight, fitted.

## 3. The form: MM1-v3.2 + L3S (one new constant)

- **Domain:** the gemmL-family loops (rgm136 gemmL and gemmLnc, rgm211 gemmL and gemmLn) at the full mask 0xffffffff, any KB. Every
  other point (subset masks, run_gemm's arms) is MM1-v3.2 unchanged. (At subsets MM1-v3.2 maps the full chip's lines by its own
  convention; their layout is the layout lanes' question.)
- **Feature** (no fitted constant; `l3s_feature.py` `a_shares`, the full-mask fast path of `l3sim.py`, equal to it at 6 of 6
  check shapes): per row half r (0 = B's far use, MM1's Q0; 1 = B's second use, Q1), the share of A tile requests that hit in the
  4-way set-associative L3 in the walk's second pass, h_r; the set model's A fresh share f_sa,r = 1 - h_r.
- **MM1-v3.2's own A shares** in that half at the constants in use: f_v32,r = sum_b Q_r[2, b] (fresh), l3_v32,r = sum_b Q_r[1, b].
- **The shift:** dA_r = clip(f_v32,r - f_sa,r, -l3_v32,r, f_v32,r); Q'_r = Q_r + lam dA_r outer((0, 1, -1), sum_a Q_r[a, :]); a
  negative cell (possible only where Q_r is not an outer product: rgm211's walk map) is clipped to 0 and the half renormalized, and
  counted. The L2 class and B's marginal do not move.
- **Time:** MM1-v3.2's op-time engine (T5r+G0+n32 at its constants) prices Q' with its own class costs (`costs.py`, which re-makes the
  engine to 4.4e-16): T' = T_v32 + (price(Q') - price(Q)), so lam = 0 is MM1-v3.2 bit for bit. The counter's mean, seconds and every
  other output follow MM1-v3.2's predictor.
- **Energy:** MM1-v3.2's predictor (`mm1_v32.Model._one`) on Q' and T' (its lines n2, n3, nF from Q'); no energy constant refitted.
- **The constant:** lam in [0, 1] (0: MM1-v3.2; 1: A's place as the set model says). Fitted by least squares on ln(T' / T_measured)
  over the fit's time points (`scipy.optimize.minimize_scalar`, bounded, xatol 1e-10). Points outside the domain carry no lam.

## 4. Data

Every committed matmul time point through E219 (`data_all.py`, sha256 below; 3,408 points): E105-E215 as MM1-v3.2's table has them
(2,508, with its own LOEO and LOCO predictions and twin flags); E216 46 (its registered points with the frozen scorer's measured
route c); E217 599 runs (the lab's blind-score tables); E218 52 (MM1-v3.2's E218 points with the frozen scorer's measured table); E219
203 in-domain runs. Twins split by MM1-v3.1's rule (`fit_v31.cfg_t`: card, kernel, arm, format, mask, clock to 25 MHz): a held-out
point is a twin when a training point of another experiment (store rungs aside, as MM1-v3.2 does) has its configuration.

## 5. Held out (two-stage: MM1-v3.2's constants per fold as it froze them, lam refitted per fold)

- **The base in each fold:** MM1-v3.2's own fold constants (`out/fits/time_T5r+G0+n32.json`, 41 folds) where the fold is one of
  them; MM1-v3.2's all-data constants where the held-out experiment is E216, E217, E218 or E219 (MM1-v3.2 never saw them). In every
  fold lam is fitted on the fold's training points (every point not held out, E105-E219) at that fold's base constants, then the
  held-out points are forecast with both.
- **LOEO:** MM1-v3.2's 20 experiment folds (E105, E107, E119, E126, E136, E146, E158, E159, E168, E169, E190, E206, E207, E208,
  E209, E211, E212, E213, E214, E215) and E216, E217, E218, E219. **Pooled LOEO without twins** over all 24.
- **LOCO:** MM1-v3.2's four card folds (E216-E219's points on the held-out card tested there).
- **The lead's fold:** LOEO E215, scored at the four gemmL2x1x7 points (E215 a3 and c1, fp32 and int8).
- **REPORTED:** the EDGE fold (every domain point whose full-chip footprint 2 MB KB + NB KB + 2 MB NB lies in (32, 48] MiB, held out
  together, base all-data); MM1-v3.2's other folds (LOKO, LOLO, leave rgm211 out, the LOEO sub-folds); per experiment; and energy (W over
  idle given the measured t) where a point's measured W is in hand.

## 6. The keep rule (stated before the fit)

The candidate is **kept** only if all three hold:
- **K1 (the lead):** in the lead's fold the held-out wall-cycles rms at the four gemmL2x1x7 points falls by at least **3.0 points**
  below MM1-v3.2's own held-out rms there (both from the same fold);
- **K2 (no pooled loss):** the pooled LOEO wall-cycles rms without twins (section 5, every point, both models on the same points) is
  at most MM1-v3.2's **+ 0.05 points**;
- **K3 (placebo):** the real feature's in-sample SSE reduction (all points, MM1-v3.2's all-data constants, lam fitted) is larger than
  a placebo's in at least **95 of 100** draws; a placebo permutes the feature (the pair f_sa,0, f_sa,1) among the domain's points
  (random.Random('l3s-placebo|<draw>').shuffle over the points in data order), re-clips dA at each receiving point's own bounds and
  refits lam.
Otherwise it is **rejected**, and its forecasts are frozen all the same as a rejected candidate's.

## 7. E220's freeze

For every point of reg-e220's POINTS.txt on both arms (arm A aifoundry1 card 1 at 600 MHz; arm B aifoundry2 card 0 at 799 MHz, with
700 and 600 MHz columns as E220 freezes them): 'MM1-v3.2 + L3S' at the all-data lam and MM1-v3.2 beside it (as a check of the
predictor call), each with wall cycles an op, the counter's mean, seconds a GEMM, W over idle at the forecast t (and its A + B / t
form for W given a measured t), J over idle with t forecast, J at rest with the rest law (REPORTED as MM1-v3.2 reports it); new files
with sha256 and the time they were final; OUT/l3-edge/FROZEN.txt written the moment they are. Frozen whether or not the candidate is
kept (then labelled 'rejected candidate').

## 8. Frozen with this declaration (sha256)

- `scripts/l3s_feature.py` 8a7b506a09baae1602dd208b4e2b11d34b656605e53e785e363c6d74ebb513f0 (the feature)
- `scripts/l3sim.py` 14c3f399748eaedb4bb69dbf19f9f18d217a1c79537ab25e96bf3d9d2df49edf (the general model and its check)
- `scripts/costs.py` 66bb02024b2867af0ae0439d2981fdd609f4dc0a6bdd1bcc30ed3afd84a20b19 (MM1-v3.2's prices split)
- `scripts/term_l3s.py` 99918f0abaa3d404d2b5372758506607415f2f0369d14b4616d98317c7ed6b86 (the term)
- `scripts/data_all.py` 810f708935a12fc57266109c7301103ac3718e3f7e769391fa9d4f1e792747cf (the data)
- `work/feature/l3s_cache.json` 6171c473e57534be7ca6828f08d989887b770d1197d98044068fa9efaac0668c (the feature at 600 shapes: every
  full-mask gemmL-family shape through E219 and E220's)
- `work/data/points_all.json` e2edc32a0415dbf47d6e1a96638e666aadb005b9791e090a1aed8c271a1d9db3 (the 3,408 points)
- MM1-v3.2 as landed (`tools/matmul/mm1/v3.2/`, 4e386f75; out/mm1_v32_params.json and out/fits/time_T5r+G0+n32.json read, never changed).
Checks before this file (`validate.py`): MM1-v3.2's engine at its all-data constants re-makes its table's all-data op times (max
relative difference 0) and its frozen E218 forecasts (0); the price split re-makes the engine (4.4e-16); lam = 0 equals MM1-v3.2 bit for bit.

## 9. Not done here

No card, no simulator run, no commit in the lab clone. The fit script and the freeze script are written after this file and implement
it as stated; any departure is recorded in the README as a departure.
