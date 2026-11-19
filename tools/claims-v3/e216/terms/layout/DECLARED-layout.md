# Layout terms for MM1-v3.1: the forms and the keep rule, declared before any held-out score is computed (round Q225, lane lay-contention)

Written Thu 19 Nov 2026 at about 09:22 PST, after a desk look at MM1-v3.1's committed in-sample and LOEO residuals by mask
(`scripts/s01_explore.py`, `scripts/s02_pairs.py`, reading only `tools/matmul/mm1/v3.1/out/points_time_v31.csv` at 2c971828) and
after the walk and mesh features were computed (`scripts/s03_features.py`), and before any fold of any form below was fitted or
scored. That look was not blind: it saw residuals of the same committed points the folds score (post hoc). No E215 datum exists or is
opened; E215's registered point list (tools/claims-v3/e215/points-e215.csv, 4cb2c2ad) is read for its shapes and masks only.

## What every form is

MM1-v3.1's time model (`time_v31.py`, form T5r+G0+n32, frozen 2c971828) times a factor on the subset points of the gemmL family
(every loop the masked walk covers: rgm136 gemmL and gemmLnc, rgm211 gemmLn and gemmL; mask not 0xffffffff):

    T = T_v31 x (1 + sum_i a_i x Phi_i(kernel, shape, mask)),  every Phi_i = 0 at the full mask by construction

so the term is exactly zero at the full chip and on every point the walk does not cover (run_gemm). At most two constants a_i.

The features (desk, from committed sources; `work/s03_features.json`):

- **Phi_fresh** (the per-controller load): the walk's strict-LRU (32 MB) DRAM lines per lock step over the chip's line requests per
  step, minus the same at the full mask: fresh(mask) / (16 n R_s) - fresh(full) / (16 x 32 R_s), where R_s = 12 tile reads a
  shire-step (coop; 64 for gemmLnc). Lines interleave over the eight memory shires by PA[8:6], so every controller carries 1/8 of the
  fresh lines: this is each controller's load per requested line, against the full chip's (which MM1-v3.1's level map assumes at every
  mask: its shape bank is keyed by the arm, never the mask).
- **Phi_link** (mesh contention): the busiest directed mesh link's L3-return load (home -> requester, dimension-ordered routes on the
  public mesh map, every active shire receiving 192 lines a step, 12 from each of the step's 16 homes; the halves of PA[10:6]
  alternate with k) over the same at the full mask, minus n / 32 (the share MM1-v3.1's chi terms already scale by).
- **Phi_hop** (hop distance): the slowest active shire's mean L3 latency over the 32 homes, (110 + 12 h_max(mask)) /
  (110 + 12 h_max(full)) - 1 (the lab's measured L3 hit law; h = mean Manhattan hops to the 32 homes).
- **Phi_fan** (shared-operand fan-out): the request-weighted mean number of active shires asking each distinct tile of a step,
  sum k^2 / sum k over A and B tiles, per active shire, minus the full chip's: fanw(mask) / n - fanw(full) / 32.

The forms: **F1** Phi_fresh; **F2** Phi_link; **F3** Phi_hop; **F4** Phi_fan; **F5** Phi_fresh + Phi_fan; **F6** Phi_fresh +
Phi_link; **F7** Phi_fresh + Phi_hop. (T7's own levels with one of these, as a joint refit with the T7 bank, is NOT RUN here: T7's
fits took 170-740 s a fold in Q222; F1 carries T7's strict-LRU level information as one constant instead.)

## How each is fitted and scored (post hoc, held out)

For each fold of MM1-v3.1's committed fit record (`out/fits/time_T5r+G0+n32.json`): the base T_v31 is that fold's own fitted constants
(re-predicted with `time_v31.Engine31` and checked against the stored held-out predictions), the a_i are the linear least-squares
solution of the fold's training residuals (forecast / measured - 1, E146's store rungs out, as fit_v31), and the held-out points get
T_v31(fold) x (1 + sum a_i Phi_i). The base constants are not refitted with the term (a two-stage fit; disclosed).

- **LOEO**: the 18 experiment folds; pooled rms over the no-twin points (twin_LOEO = 0 in points_time_v31.csv; n 1299). MM1-v3.1:
  4.72%.
- **LOLO**: item 4's three layout classes (compact, spread, other), each held out with its own fold record; rms over every subset point
  (n 212, as v3.1's table). Read two ways: (a) as declared (the compact fold's eta where its optimizer stopped, 2.0: v3.1 89.78%) and
  (b) with the compact fold's eta at its neutral 0 for the held-out points (the README's post hoc re-read), for the base and the form
  alike.
- **Pairs**: E212's and E213's equal-shire-count layout pairs (same card, kernel, arm, format, clock and n; different masks): the
  share whose measured order the forecast gets right, in sample (all-data) and held out (LOEO).

## The keep rule

A form is kept only if (1) its LOLO (b) is lower than MM1-v3.1's LOLO (b), (2) its LOLO (a) is not higher than MM1-v3.1's LOLO (a),
and (3) its pooled LOEO (no twins) is at most 4.72% (MM1-v3.1's). Among kept forms the lowest LOLO (b) wins; within 0.10 points the
form with fewer constants, then the lower pooled LOEO. If no form is kept: NOT FROZEN.

The winner's frozen forecasts: its all-data constants (fitted on every training point of the all-data record, base = MM1-v3.1's
frozen all-data constants) applied to MM1-v3.1's own forecast of every E215 point (both arms; the base re-made with Engine31 at
theta_all and checked against the frozen files), wall cycles an op and seconds a GEMM.
