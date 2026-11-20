# DECLARED: 'MM1-v3.2 + posimb', a layout term for equal-count shire masks (round Q234, lane layout2)

Written Fri 20 Nov 2026 (week 47), Pacific time, at aifoundry2's desk, BEFORE any fit of this form's constants. Desk only. Interpreter
/usr/bin/python3 3.12.3, numpy 1.26.4, `-I -B`, single-threaded (OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS = 1), every job in the round's CPU slots.

**What was looked at before this was written (disclosed; post hoc, in sample):** MM1-v3.2's all-data residuals ln(T_meas / T_v32) at the
640 subset points through E219 (`x02_explore.py`), their equal-count pairs (273, same experiment, card, arm, format, clock bin and shire
count), mask-level mesh numbers (mean and slowest active shire's hop to the 32 L3 homes on the MARTY map, mean hop to the memory shires, row
and column groups R, C), the single-to-four-shire residuals by shape (`x03_small.py`), and the measured wall / counter-mean ratio at every
subset point with a measured mean (`x04_imbalance.py`). The values of this form's two features at the data's points were computed
(`f02_private.py` -> `work/private_shared.json`) but NOT compared with any residual before this file was hashed; no constant of this form
was fitted. What the looks showed, and why this form: (1) at E218's KB-24 pairs the op time is a per-mask constant across four to five
shapes (0xf 1537.4, 0x3030 1473.8 cycles; 0x55555555 1603.2, 0xffff0000 1637.7-1642.6) and the E216 controls (0x101 vs 0x10001, equal R
and C) differ by 3.6-4.2%: a position effect, which the active shires' mean L3 latency on the mesh orders at E218 y01, y02-y06 and E216
y07/y08 (not at E218 y07/y08); (2) much of every pair difference is the wall's excess over the counter's mean (between shires: ln(wall/mean)
is exactly 0 at every single-shire point), and at E216 y01-y03 the slower layout (0x3: its DRAM stream B private to each shire) carries
ln(wall/mean) 0.028-0.044 where the faster (0x10001: its DRAM stream B shared by both shires) carries 0; at E218 y01 the slower (0x1010101:
its DRAM stream A private) 0.040, the faster (0xf000: A shared) 0. Across all 273 pairs the mean part and the imbalance part have equal
rms (0.078, 0.079) and correlate -0.59; most of E212's, E214's and E217's large pair differences are explained by neither feature here.

## 1. The base and the scope

- **The base:** MM1-v3.2 (tools/matmul/mm1/v3.2/, declaration f8e00a57, model 4e386f75) unchanged: its op time by `time_v31.Engine31`
  (T5r+G0+n32) at its constants. **No MM1-v3.2 constant is refitted** (two-stage): the term multiplies MM1-v3.2's op time and its two
  constants are fitted on the residuals of MM1-v3.2's own fold bases. Why two-stage: the term acts only at subset points; MM1-v3.2's time
  fit takes 18 starts a fold over 19 constants; lay-contention's joint refit (Q225) kept its two-stage term's sign.
- **Scope:** a point takes the term iff `layout_v32.is_layout_point(p)`: a subset mask (not 0xffffffff), kernel rgm136, an arm
  `gemmL<MB>x<NB>x<KB>` (rgm136's cooperative gemmL loop; never gemmLn, gemmLnc or run_gemm). Every other point keeps MM1-v3.2's forecast
  to the last bit, and so does every full-chip point.

## 2. The features (both exactly 0 at the full mask)

Per configuration (arm, mask), by `f02_private.py` (sha256 `1594dd8bcd485139b38a52d2a1c594dbf7b2b32477277aa83013b7b60811b1ab`): the walk is
verify-lay's committed `v01_map.my_steps` generator (tools/matmul/mm1/v3.2-terms/layout/controls-e215/, the generator layout_v32's features
use), its LRU logic (`v01_map.lru_fresh`, strict LRU at 32 MB of 1 KiB tiles, pass 2) run with each tile's asking shires carried along:

- L(s) = 110 + 12 hbar(s), hbar(s) = shire s's mean hop to the 32 L3 homes (PA[10:6]) on the MARTY map (the lab's L3 law
  110 + 12 x hops); Lmean_act, Lmax_act = the mean and the largest L(s) over the active shires; Lmean_full = the mean over all 32
  (154.953125 cycles).
- Fp = DRAM-served (fresh) requests whose tile one active shire alone asks / all requests; Fs = fresh requests whose tile two or more active
  shires ask (a shared tile counts once per asking shire) / all requests.
- **G1core = Lmean_act / Lmean_full - 1** (equal to verify-lay's G1, the hop-mean control's feature).
- **LAGcore = ((Lmax_act - Lmean_act) / Lmean_full) x Fp / (Fp + Fs)**, 0 when Fp + Fs = 0: the slowest active shire's L3-latency excess
  over the active mean, times the private share of the DRAM-served stream. 0 at one shire (Lmax = Lmean) and at every mask whose DRAM
  stream is all shared (the full chip: every A tile asked by 4 shires, every B tile by 8).

Per point j, at the base constants theta of the fold that scores or trains on it: **e_j** = MM1-v3.2's elasticity of its op time to its
four mesh-served memory constants: e = ln(T(theta with c3, m3, cF, mF x 1.01) / T(theta)) / ln(1.01), by `e01_base.py` (sha256
`2ce58eacc914fae96f6c047023ab99a1023d7bde43c1324c3e0c67b1cdf81d95`); about 1 at memory-bound points, about 0 where the op is L2-resident.

**Phi_hop = e x G1core; Phi_lag = e x LAGcore.**

## 3. The form (two new constants: a_hop, a_lag)

- wall op time: **T = T_v32 x g_w**, g_w = clip(1 + a_hop Phi_hop + a_lag Phi_lag, 0.3, 3.0) (wall cycles an op, the op time, seconds a
  GEMM);
- the counter's mean cycles an op: MM1-v3.2's mean x g_m, g_m = clip(1 + a_hop Phi_hop, 0.3, 3.0) (Phi_lag is the wall's excess over the
  mean between shires, so the mean takes only the position part);
- energy: MM1-v3.2's W over idle at an op time t (A_W + B_W / t, its own A_W and B_W unchanged) at the term's t: W over idle given a
  measured t is MM1-v3.2's own; with t forecast W = A_W + B_W / (T_v32 g_w); J over idle a GEMM = W x seconds; J at rest = (P_rest + W) x
  seconds (MM1-v3.2's rest law), as e218_v32.composed builds a composed forecast.
- **Expected signs (physics, stated before the fit; reported, not a rule):** a_hop > 0 (active shires farther from the L3 homes: longer
  latency, slower) and a_lag > 0 (a private DRAM stream lets the slowest shire set the wall); each near 1 if the memory-bound wall scales
  with the latency law.

## 4. The fit (post hoc as an act)

a = argmin over the fold's training points of sum_j (rho_j (1 + Phi_j a) - 1)^2, rho_j = T_base,j / T_meas,j (lay-contention's
`fit_consts`: linear least squares, numpy lstsq), over every training point (out-of-scope points have Phi = 0 and do not move a), E146's 87
store rungs out (MM1-v3.2's own `store_rung_ids`). The data: every committed time point through E219 in `work/points_all.json` (sha256
`79345900a388281c487680dc1e25229150ea4c5f56a447a312d750db9c6a5db0`, `d01_points.py` `3b61577d...`): MM1-v3.2's 2508 (E105-E215, its
fit's ids exactly), E216 46 (scored-e216.json measured route c), E217 486 cases (blind-e217's case table), E218 52 (scores-e218-A.json
measured), E219 139 in-domain cases (blind-e219's case table); 3231 points, 640 of them subset, in scope those of rgm136 gemmL.

## 5. The folds (held out) and the bases (e01_base.py's `work/base.npz`, sha256 `6d57e1da...`)

- **LOEO**, one fold per experiment E105 ... E219 (24 folds; **E215's, E216's, E217's, E218's and E219's named**): test = that
  experiment's points; base = MM1-v3.2's stored fold constants 'LOEO <exp>' for E105-E215, its all-data constants for E216-E219 (never in
  its fit); the term fitted on every other point at that base.
- **LOCO**, one fold per card (4): test = every point of that card; base = MM1-v3.2's stored 'LOCO <card>' constants.
- **THE LEAD'S FOLD, 'LO-Y'**: E216 and E218 held out together (the lead's equal-count pairs: E216's Y family and E218's Y family); base =
  the all-data constants.
- LOLO (compact / spread / other by fit_v31.lolo_class) at MM1-v3.2's stored LOLO constants: REPORTED.
- **Twins split:** a point is a twin if another experiment holds a point of the same card, kernel, arm, format and mask; every pooled
  figure is printed with and without twins; the guard reads without.

## 6. The metrics, the margin and the keep rule (stated before fitting)

- **M1, the lead's held-out error:** over the 15 equal-count pairs with data in both members (E216 y01-y08; E218 y01, y02, y04, y05, y06,
  y07, y08; a = the pair's first mask as registered), the rms of ln(T_a^ / T_b^) - ln(T_a / T_b), T^ from the LO-Y fold. MM1-v3.2's own M1
  is the same rms with its forecasts.
- **M2, the pooled held-out guard:** the rms of T^ / T_meas - 1 (%) over every LOEO-predicted point without a twin, all experiments, the 24
  folds.
- **M3, the placebo:** 100 draws i = 0..99; in draw i the scope points' (G1core, LAGcore) pairs are permuted among the scope points by
  numpy.random.default_rng(20261120 + i).permutation; Phi = e x the permuted pair; the LO-Y fold refitted; M1 recomputed.
- **KEEP iff all three:** **K1 M1 <= 0.80 x MM1-v3.2's M1** (the margin: a fifth of the lead's error); **K2 M2 <= MM1-v3.2's M2 + 0.05
  points**; **K3 the real M1 below the placebo's M1 in at least 95 of the 100 draws.** Otherwise the term is a rejected candidate and its
  forecasts are frozen and reported as such.
- **REPORTED beside (never deciding):** LOEO by fold, LOCO by card, LOLO, the LO-Y fold's rms at the 31 Y points, sign agreement at the 15
  pairs, the counter's mean at the Y points where MM1-v3.2 forecasts it, and two baselines fitted by the same procedure on the same folds:
  **'hop mean'** (T_v32 x (1 + a G1core) at every scope point, no e) and **'count only'** (T_v32 x (1 + b1 N1 + b2 N2), N1 = 1 - n/32,
  N2 = (1 - n/32)^2, verify-lay's N1+N2).

## 7. The forecasts to freeze

'MM1-v3.2 + posimb' at its all-data constants (the fit on every point through E219 at MM1-v3.2's all-data base) for every E220 point on
both arms of `OUT/reg-e220/POINTS.txt` (read only once it exists; no E220 datum is opened by this lane): wall cycles an op, mean cycles an
op, the op time, seconds a GEMM, W over idle at the forecast t with MM1-v3.2's A_W and B_W (so W given a measured t is MM1-v3.2's), J
over idle a GEMM with t forecast, J at rest a GEMM with t forecast; features at E220's configurations made by the same code; MM1-v3.2's
own forecast beside every row. Labelled 'MM1-v3.2 + posimb' if KEPT, 'MM1-v3.2 + posimb (rejected candidate)' if not; frozen with
sha256 and the time they were final; `OUT/layout2/FROZEN.txt` written the moment they are.

SPDX-License-Identifier: Apache-2.0
