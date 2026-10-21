# E61 — independent re-reduction

Wed 21 Oct 2026 (week 43), ~02:05 PDT. Role: independent re-reduction of the deterministic
transistor-flip campaign from the raw passes and the README's own definitions.

`reduce_dtf.py` and the two wf2 copies were **not** read. The only thing taken from E60's
`reduce_hl.py` is the power window and the leakage rule, as the role allows (lines 74–145 of that
file: `runs_of_pass` and `leak_slope`). Everything else — the gates, the zero-rung algebra, the
per-flip conversions, the slopes, the between-pass statistics — is written from the pre-registration
(`tools/claims-v3/dtf/README.md` §4, §5, §8, §9 and amendments A1/A2) and the manifest
`manifest-a2.json`.

## Files

| file | what |
|---|---|
| `<E61 working copy>/wf3/independent/numbers.json` | **the result**: every quantity with value, plain SE, robust SE (MAD×1.4826), median, pass count, unit, per-pass series, and a note on how it was formed; plus `bookkeeping`, `cross_card_ties` and `t_against_registered_targets` |
| `<E61 working copy>/wf3/independent/headline.md` | the same numbers as two markdown tables (board leg and minion-rail leg) |
| `<E61 working copy>/wf3/independent/stage1.py` | raw passes → one record per run (window, p80, rail, rate, gates) |
| `<E61 working copy>/wf3/independent/stage2.py` | run records → the registered quantities (`stage2.py [out.json] [--no-setaside] [--leak=fit\|zero\|e60] [--rate=nominal\|wall]`) |
| `<E61 working copy>/wf3/independent/handcheck.py` | a deliberately separate 30-line recomputation of one pass's e_out straight from the raw files |
| `<E61 working copy>/wf3/independent/sens_noset.json`, `sens_leak0.json`, `sens_leake60.json`, `sens_ratewall.json` | the four sensitivity arms (§ Sensitivity below) |
| `<E61 working copy>/wf3/independent/report_p80.txt`, `report_rail.txt` | grouped console view, by family |
| `<E61 working copy>/wf3/independent/diag.py`, `leakdiag.py`, `survey.py`, `survey2.py`, `probe.py`, `sens.py`, `report.py`, `headline.py` | diagnostics and printers |

**Pipeline check.** `handcheck.py`, written independently of `stage1`/`stage2`, reproduces
aifoundry3 pass 1's e_out from the B 2×2 as **28.0000 fJ** against the pipeline's per-pass
**28.002 fJ**, with all eight p80 levels and both legs matching. The window, the rate and the
zero-rung algebra are therefore not a transcription of anything.

## What was usable

| card | clock | V (die, minion) | passes finished | used | set aside | gate-failed runs | leak k |
|---|---|---|---|---|---|---|---|
| aifoundry3 | 600 MHz, pinned | 522 mV | 1–7 | **7** | none | 0 / 434 | 0.040 W/°C |
| aifoundry2 | 800 MHz, gov-free | 618 mV | 1–13 | **12** | p4 | 0 / 312 | 0.271 W/°C |
| aifoundry1-c0 | 800 MHz, gov-free | 604 mV | 1–12 | **8** | p6, p7, p10, p12 | 9 / 456 | 0.210 W/°C |
| aifoundry2 `dtf-cam` | 800 MHz | — | 1–4 | **4** | none | 0 / 80 | — |

Skipped as unfinished (no `block.json`): `aifoundry3/dtf/p8` (43 of 62 runs written) and
`aifoundry2/dtf/p14` (13 of 24). Nothing in them was read beyond the absence of `block.json`.

The nine gate failures are all on aifoundry1 c0 and are all the same thing — the governor-free
window caught the clock still ramping (`clocks in window [600, 700, 800]`, `die_mv` 554–575 against
the pass median 604, or `ramp_ms` 1787/2129 > 1500). Items hit: `xin_h32` ×2, `xin_h0`, `d2B_h32`,
`d1b_h32`, `r_not_r1` ×2, `r_and_r2`, `r_and_c2`. On aifoundry3 and aifoundry2, **every** run passed
every gate.

**A2's rate table reproduces exactly**, which is the determinism evidence (C13/C15):

| mode | op | aifoundry3 | aifoundry2 | aifoundry1 c0 | A2 says |
|---|---|---|---|---|---|
| 202, 300, 302, 306, 307, 308 | fnot / c2.fand / c2.fadd / addr.a0,a1,a3 | 0.58144–0.58148 | 0.58141–0.58145 | 0.58140–0.58151 | 0.5814 |
| 177, 179, 191, 301, 303, 309 | fand / fxor / fmadd / c2.for / c2.fxor / addr.a5 | 0.60877–0.60891 | 0.60882–0.60887 | 0.60882–0.60894 | 0.6088 |
| 304 | un1a.fnot | 0.73560 | — | 0.73561 | 0.7356 |
| 305 | un1b.fnot | 0.75738 | — | 0.75738 | 0.7574 |
| 177 `--harts 2` | fand, 2048 participants | — | — | 0.37311 | 0.3731 |

Within-mode relative SD across runs is 0.0002–0.0092% (E60's was 0.013–0.056%). Over the 71
item/zero-rung pairs, the largest within-mode rate deviation is **0.0072%** — 70× inside the 0.5%
gate. The only pair outside it is `d5_a5` vs `d5_a0` at **+4.69%** (mode 309 vs 306), exactly the
4.7% A2 predicted, so a5 is reported beside the ladder and never in it. `participants` equals
`participants_expected` on every kept run (1024, or 2048 for R's two-hart arms, or 512 for family 7,
whose measured per-hart rate is 0.5815 — the 512-hart arms are not read as a rate change).

## The numbers

Full tables with both legs: `headline.md`. Every entry below is
**mean ± between-pass SE [robust SE] (n = surviving passes)**, board power, leak-corrected (p80).
The minion-rail leg is in `numbers.json` under the same key with `_rail`; on aifoundry3 the
board/rail ratio comes out **1.29** for e_in and **1.26** for e_out (the README quotes ~1.33).

**e_in, the `xin` ladder.** aifoundry3 **19.604 ± 0.269** fJ/port bit excluding (0,0),
**20.753 ± 0.120** including it (n=7). E60's two readings are 19.71 (ladder fit) and 20.83 ± 0.10
(joint fit) — |t| = 0.40 and 0.64. The rail leg gives 16.066 ± 0.112 fJ against E60's 16.28.
aifoundry2 25.576 ± 0.848 / 28.596 ± 0.453 (n=12); aifoundry1 c0 25.088 ± 0.169 / 26.800 ± 0.189
(n=7). Single rungs on aifoundry3: h8 24.987 ± 0.863, h16 22.749 ± 0.273, h32 20.995 ± 0.066 — the
ladder is sublinear, which is what the intercept is.

**The ladder intercept.** X: **0.2751 ± 0.0401 W** on aifoundry3 (E60's fitted +0.273 W, reproduced
to 0.7%), = 735.5 ± 107.1 fJ/op = **45.97 ± 6.70 fJ per changed 32-bit source word** against E60's
48.0. N (the R1/R2/R3 discriminator): `d1n` **0.2276 ± 0.0365 W**, `d1nz` **0.2566 ± 0.0562 W**
(n=7); on aifoundry1 c0 `d1nz` **0.2820 ± 0.0470 W** (n=8). Both sit on R2 (0.273) and neither
excludes R1 (0.137) at the 3-SE-equivalent |t| of 5.02 — |t| vs R1 is 2.48 and 2.13, vs R2 1.24 and
0.29, vs R3 6.23 and 4.57. `d1nz`'s SE (0.056 W) exceeds one third of the 0.136 W separation, so by
§9 rule 4 that arm is **under-resolved**; `d1n`'s (0.037 W) does not, and two arms are satisfied, so
it is **OPEN** with R3 excluded.

**e_out, the B 2×2.** aifoundry3 **26.976 ± 0.292** fJ/result bit at h=32 and **27.610 ± 0.917** at
h=16 (n=7). The two legs agree: fand (B−A) 26.794 ± 0.167, for (D−C) 27.158 ± 0.680. The raw watt
combination (B+D)−(A+C) is **5.0510 ± 0.0564 W** against the registered base 5.678 W (R2 would make
it 5.951). (B−A)−(D−C) = 2g_op + g_res = **−0.1501 ± 0.0760 W**, registered base 0.000.
aifoundry2 37.480 ± 0.502 (n=12), aifoundry1 c0 34.341 ± 0.964 (n=7). Put on aifoundry3's scale by
each card's own e_in (×1.3779 and ×1.2914, measured tonight), the three cards read **26.98, 27.20,
26.59** fJ. 44.38 fJ is excluded at 59 SE; 30.00 fJ at 10.3 SE on aifoundry3 and 14.9 SE on
aifoundry2 (aifoundry1 c0: 4.50, just inside its 5.02 window).

**e_in(fand) and e_in(for).** From `d2A`: **25.882 ± 0.147** fJ/port bit at h=32 and
**27.534 ± 0.343** at h=16 (aifoundry3). From `d2C`: 25.812 ± 0.251 at h=32. The h=16 reading sits
inside the C14/C64 interval [26.0, 30.2]; the h=32 reading is 0.8 SE below its lower edge. On
aifoundry1 c0 the registered `fand` tie `ain_h8` gives **34.344 ± 1.322** fJ (= 26.59 on the
aifoundry3 scale) against E60's 28.10 ± 0.70; `ain_h32` (the deliberate zero-word corner)
28.047 ± 0.243.

**Family N, (in + out) per flipping bit.** aifoundry3 slope form over h = 8/16/32:
`d1n` **49.964 ± 0.880**, `d1nz` **50.036 ± 0.868** fJ. Single-rung h=32: 52.357 ± 0.707 and
52.713 ± 0.638. aifoundry1 c0 `d1nz` slope (h = 8/16/32) 66.152 ± 0.295 fJ (= 51.2 on the
aifoundry3 scale). **The zero-word term**: `d1n − d1nz` at h=32 is **−0.182 ± 0.380** fJ/flipping bit
on aifoundry3 (−0.0166 ± 0.0347 W), **−1.765 ± 0.940** on aifoundry2 and **−0.927 ± 0.257** on
aifoundry1 c0; the slope form on aifoundry3 is **−0.072 ± 0.439** fJ. At h=0 the two arms differ by
+0.016 ± 0.050 W (aifoundry3), −0.107 ± 0.037 (aifoundry2), +0.004 ± 0.064 (aifoundry1 c0). So the
sign is negative on all three cards (the all-zero arm is *cheaper*, as E60's −3.8% suggested) but it
is 0.5 SE on the pinned card, 1.9 SE on aifoundry2 and 3.6 SE on aifoundry1 c0 — none reaching its
3-SE-equivalent.

**Family V, the cell bit (A2 form).** aifoundry3 only, n=7.
**e_cell = 0.560 ± 0.498 fJ** per flipped cell bit from the A2 slope difference
(slope(1B vs `d1b_h0`, mode 305) − slope(1A vs `d1a_h0`, mode 304), each at its own rate, x = 8h).
Single rungs: **1.244 ± 0.319** fJ at h=32 and **1.928 ± 0.601** at h=16 — the *per-bit* price does
not rise with h (≈0.115 W at h=16 against ≈0.148 W at h=32), which is why the slope form reads lower
than either rung. The pair's own h=0 null is **+0.0012 ± 0.0393 W**, i.e. clean. Each arm's own
slope: 1A 50.672 ± 0.217, 1B 51.233 ± 0.475 fJ/flipping bit. 10 fJ is excluded at 19 SE; zero is not
excluded (|t| = 1.12 on the slope form, 3.90 at h=32, against the 5.02 window). On aifoundry1 c0
there are **no V zero rungs**, so only the raw cross-mode difference exists:
`d1b_h32 − d1a_h32` = 0.8506 ± 0.1867 W, rate-confounded by 3.0% and **not** a cell price.

**Family C, the carry ladder.** Slope per carry node (x = 8L, L = 2/8/16/29, free intercept):
aifoundry3 **28.618 ± 0.688** fJ, aifoundry1 c0 **34.973 ± 0.585** fJ (= 27.08 on the aifoundry3
scale). This slope is e_out(add) + e_carry, because `d3_L`'s result bits grow by the same 8L.
**Slope − e_out(B 2×2, same passes) = 1.643 ± 0.595 fJ per carry node** on aifoundry3 and
0.467 ± 1.442 on aifoundry1 c0. Taking e_out(add) from `d3z` instead gives **0.484 ± 0.882**
(aifoundry3). E46's 1.7 fJ is 0.1 SE away; the page's 14.2 fJ is excluded at 21 SE. Curvature: the
ripple (L) form's rms residual is 0.0444 ± 0.0130 W against the prefix (L·log₂L) form's
0.1058 ± 0.0175 W, so the data prefer **linear in L**. `d3p_L29 − d3_L29` (the page-exact
zero-operand arm) = +0.0134 ± 0.0597 W on aifoundry1 c0 — a null.

**The gate ladder** (aifoundry3, n=7), fJ per (port + result) bit — double it for e_in+e_out per
flipping bit: OR (`d2D`) **26.485 ± 0.279**, XOR (`d2X`) **28.000 ± 0.138**, ADD (`d3z`)
**27.008 ± 0.278**. Contrasts: XOR−OR **+1.515 ± 0.384** (|t| = 3.95), ADD−OR **+0.523 ± 0.408**,
ADD−XOR **−0.992 ± 0.284**. The spread is 1.5 fJ on 26–28 fJ (5.7%), and the ranking is
OR < ADD < XOR, which is **not** gate depth.

**Family M.** Every pattern reads *below* `xin_h16` at matched counts. aifoundry3:
`m_phase0` −0.0349 ± 0.0571, `m_nib` −0.0856 ± 0.0575, `m_pair` −0.1079 ± 0.0241,
`m_byte` −0.2149 ± 0.0736 W. aifoundry2: −0.0407 ± 0.0546, −0.2913 ± 0.0839,
`m_nib_c` −0.2588 ± 0.0527, −0.4484 ± 0.0761, −0.3232 ± 0.0571; `m_solid_z` (page-exact,
confounded) −0.3720 ± 0.0201. **Complement control**: `m_nib − m_nib_c` = **−0.0325 ± 0.0958 W** on
aifoundry2 — symmetric, as a capacitive effect must be. Spearman ρ over the four k_adj levels is
**−0.571 ± 0.229** (aifoundry3) and **−0.533 ± 0.160** (aifoundry2): the rank order runs the *wrong*
way, and ≥ 0.90 is excluded at 6.4 SE. Level-to-level steps are 0.02–0.23 W with SEs of 0.05–0.10 W,
so no step reaches 3 SE on aifoundry3.

**Family A, the address ladder** (aifoundry3, n=7). The A2 ladder a0/a1/a3 (modes 306–308, one rate)
gives **442.6 ± 20.9 fJ per address bit**; the a1→a3 two-point slope **358.9 ± 37.8**. Raw deltas:
a1 **+0.4659 ± 0.0335 W**, a3 **+0.9787 ± 0.0411 W**, a5 (rate-confounded) **+1.6736 ± 0.0144 W**.
This is 14× the README's own 0.074 W ceiling at 2 fJ/bit and 5.7× the page's 0.171 W. Per-rung
readings are not linear either (a1 652.1 ± 46.9, a3 456.6 ± 19.2, a5 447.5 ± 3.9 fJ/bit), so the
quantity is not a per-address-bit constant. 32 fJ/bit is excluded at 19.6 SE, but **upward**.
**Gated vs live** at matched Δ and matched mode: Δ=0 **+0.0296 ± 0.0097 W**,
Δ=3 **+0.0899 ± 0.0491 W** (live minus all-zero image); the live ladder's own slope is
484.7 ± 9.8 fJ/bit against the gated 442.6 ± 20.9.

**Family Z.** `d6_one − d6_zero` = **+0.1127 ± 0.0975 W = 0.301 ± 0.261 pJ/op** (aifoundry3, n=7);
the median over passes is 0.127 pJ/op and the robust SE 0.057 — pass 6 reads 1.810 pJ/op against
0.025–0.233 for the other six. On the minion rail the same quantity is **−0.002 ± 0.058 pJ/op**.
2.5 pJ/op is excluded at 8.4 SE; 0.5 pJ/op is not (|t| = 0.76), nor is our 0.147 (|t| = 0.59).

**Family R** (aifoundry1 c0, n=8). **ρ = 1.1166 ± 0.0242** (per-op deltas 7513.5 ± 104.9 fJ at
`--harts 1` and 8378.5 ± 149.0 at `--harts 2`). 1.000 is excluded at |t| = 4.81 against its 4.53
window; 1.123 is 0.27 SE away and 1.140 is 0.97 SE away. **This verdict is arm-dependent** — see
Sensitivity. The `fnot` leg: `(r_not_r1 − r_not_c1)` = 3.0819 ± 0.0453 W = 6470.1 ± 95.0 fJ/op,
**÷ 95.556 = 67.710 ± 0.994 fJ per flip**; subtracting family N's measured intercept on the same
card and the same `fnot.pi` shape (`d1nz`, 0.2820 W) gives **61.515 ± 0.994 fJ**. The §5.3 target
[52.00, 53.10] fJ is on aifoundry3's scale; dividing by this card's own e_in ratio (1.2914) gives
**47.63 ± 0.77 fJ**, below that interval.

**Family 7 / E-D7 tier 1** (aifoundry2 `dtf-cam`, n=4). West−East board power:
**−0.0382 ± 0.3814 W** on the loud pair and **+0.0394 ± 0.0756 W** on the quiet pair — the halves
are electrically symmetric. Half-die result-path load: W **1.9310 ± 0.2462 W**, E
**2.0086 ± 0.2098 W**, which as an energy is **31.67 ± 4.04** and **32.95 ± 3.44** fJ per result bit
against aifoundry2's full-die 37.48 ± 0.50. (The README's [1.33, 1.42] W interval is on aifoundry3's
scale and 600 MHz; the matching figure for aifoundry2 from tonight's own e_out is 2.29 W.)

## The choices I had to make

1. **`ops/s` = `ops / (cycles_max / clock)` with the card's nominal clock** (600 or 800 MHz), as the
   role specified, averaged over the launch records that overlap the power window. Each ec launch is
   exactly 240,000,000 cycles and `cycles_max / wall_s` reads 599.4 MHz (aifoundry3) and 798.7 MHz
   (both gov-free cards), so the kernel occupies essentially the whole launch and there is no
   duty-cycle correction to make. Using each record's own `cycles_max / wall_s` instead of the
   nominal clock lowers every rate by 0.10–0.17% and raises every per-flip energy by the same
   amount — the `--rate=wall` arm, which moves nothing by more than 0.1 SE. The record's own
   `ops_per_s` field (= ops/wall_s) and the prorated `rate` were not used, per §8.2.
2. **"Launches lying inside the power window" = overlapping it** (`ov > 0`), not fully contained.
   Launches are ~300–400 ms and the window is 2 s, so this is 5–7 launches either way and the mean
   rate is identical to 1e-4.
3. **The leakage slope is weakly identified on aifoundry3.** E60's rule fits dP/dT per run over runs
   whose reading rises ≥ 1 °C, then takes the median. On aifoundry3 the within-run `minshire`
   temperature range is **median 0.00 °C** (the sensor steps in whole degrees) and only 101 of 434
   runs qualify; the surviving per-run slopes run −0.03 to +0.16 W/°C with median **0.040**, against
   E60's **0.203** for the same card. aifoundry2 (0.271, 249/312 runs) and aifoundry1 c0 (0.210,
   392/456) are better conditioned. I kept the fitted value as primary and ran E60's slopes as a
   sensitivity arm. It matters almost nothing for differences — every run launches at the same
   target temperature (58.0 °C, 57.0 °C on aifoundry1 c0) so the correction is near-constant and
   cancels — but it does move the **intercepts** (see Sensitivity).
4. **The minion rail is not leak-corrected.** E60 corrects board power with a board-fitted dP/dT;
   applying the same slope to a different supply would be wrong, so `rail` is the raw window mean
   over [window start + 1 s, window start + 3 s) (E60's "seconds 2–4", never past the run).
5. **Cross-mode quantities are differences of per-flip slopes, per A2.** B's e_out is
   `[(d2B−d2A)/rate(300) + (d2D−d2C)/rate(301)] / 2`, each difference inside one opcode and each arm
   against its own h=0 zero — not the watt combination divided by one rate. The raw watt combination
   and the version without zero subtraction are both in `numbers.json`
   (`BD_minus_AC_h32_W_p80`, `..._noZeroSub`); they differ by 0.03–0.08 W.
6. **Family V's x-variable is 8h flips/s**, the unit in which one designed flip is simultaneously one
   port bit, one result bit and (in 1B) one cell bit. Then slope(1B) − slope(1A) is e_cell directly,
   which is the README's "e_cell = the slope ÷ cell bits". Normalising by (vs1 + result) = 16h
   instead would halve every V number.
7. **Family C's "slope minus e_out" needed a choice of e_out**, because e_out(add) is not separately
   identified: `d3z` gives e_in(add) + e_out(add), and no `fadd` arm with a static result exists. I
   report both — minus the B-family e_out (1.643 ± 0.595 fJ) and minus
   `2·d3z_per_(port+result)_bit − e_in(fand from d2A)` (0.484 ± 0.882 fJ), which assumes
   e_in(add) = e_in(fand). The README's own wording ("slope/8 − e_out(add), with e_out(add) from
   `d3z`") does not resolve this; the second arm is my reading of it.
8. **The gate ladder is quoted per (port + result) bit**, matching §5.2's "a few percent of 26.00 fJ
   per (port + result) bit". Doubling gives e_in + e_out per flipping bit, which is how family N is
   quoted. Both conventions are in `numbers.json`.
9. **Family A's fit includes the (0,0) point**, since A2 makes a0 the ladder's own zero rung and the
   ladder is then a0/a1/a3 with a free intercept (3 points, 1 df). The a1→a3 two-point slope is
   reported beside it because the two disagree by 2.2 SE — the ladder is not linear.
10. **Family M's reference.** Each M item's manifest zero is `xin_h0`, but the registered contrast is
    against `xin_h16` (identical designed counts, same mode 179), so I subtract `xin_h16` directly.
    `m_nib`/`m_nib_c` are averaged into one k_adj level before the Spearman ρ, as registered.
11. **Set-aside, read literally** (§8.9: "more than 5% of its runs fail a gate (floor 2 runs)"). On a
    38-run pass 2 failures is 5.26%, so aifoundry1 c0 loses p6, p7 and p10 for what are per-run
    clock-ramp glitches rather than pass-level faults. The drift arm removes aifoundry2 p4
    (+0.75 W > the 3×SD threshold 0.63 W) and aifoundry1 c0 p12 (+1.44 W > 1.27 W); note the SD that
    sets those thresholds is itself inflated by the outlier it is judging. All of this is reversible
    with `--no-setaside` (`sens_noset.json`).
12. **Degrees of freedom.** aifoundry3 ends with **7** passes, not the 8 its pass 8 would have given
    and not the 12 A1 planned — p8 was unfinished at fetch time and p9–p12 were still running. §9's
    "never below 6" floor holds, but every aifoundry3 3-SE-equivalent |t| is **5.02** (interpolated
    between the tabled 5.51 at 6 and 4.53 at 8), not 4.53. aifoundry1 c0 ends with 8 (4.53) and
    aifoundry2 with 12 (4.09→ I used the tabled 4.09 for ≥10).
13. **The h=0 rungs of family B are not all same-mode.** `d2A_h0`/`d2B_h0` are both mode 300 and
    `d2C_h0`/`d2D_h0` both mode 301, so those two differences are legal; `d2A_h0 − d2C_h0`
    (−0.1024 ± 0.0096 W) and `d2B_h0 − d2D_h0` (−0.0824 ± 0.0207 W) cross modes 300/301 and carry
    their 4.7% rate difference. They are reported as α(opcode) with that caveat, not used in any
    energy.
14. **Family 7's half-die arms were converted at 512 participating harts** (measured per-hart rate
    0.5815), so the per-result-bit energy is comparable with the full-die figure.
15. Nothing was read from `reduce_dtf.py` or either wf2 copy. I did read E60's committed
    `hl.json` → `gates` to get its three leakage slopes by card for the sensitivity arm
    (aifoundry3 0.2026, aifoundry2 0.4420, aifoundry1 c0 0.3273); the README quotes the same three
    numbers without saying which card each belongs to.

## Sensitivity

Four arms, all regenerated from `stage1.json`: `--no-setaside` (keep every finished pass),
`--leak=zero` (no leakage correction), `--leak=e60` (E60's own per-card slopes), `--rate=wall`
(each record's own `cycles_max / wall_s`).

Almost everything is robust. Over the 20 headline quantities the largest moves are:

| quantity | primary | no set-aside | leak = 0 | leak = E60 | rate = wall |
|---|---|---|---|---|---|
| aifoundry3 e_out (B h32) | 26.976 ± 0.292 | same | 26.920 ± 0.340 | 27.204 ± 0.204 | 27.003 ± 0.293 |
| aifoundry3 e_in (with origin) | 20.753 ± 0.120 | same | same | same | 20.774 ± 0.120 |
| aifoundry3 `d1nz` intercept, W | 0.2566 ± 0.0562 | same | 0.2828 ± 0.0587 | **0.1497 ± 0.0537** | same |
| aifoundry3 `d1n` intercept, W | 0.2276 ± 0.0365 | same | 0.2464 ± 0.0358 | **0.1509 ± 0.0481** | same |
| aifoundry3 e_cell (slope) | 0.560 ± 0.498 | same | 0.589 ± 0.501 | 0.444 ± 0.493 | same |
| aifoundry3 e_carry (− e_out B) | 1.643 ± 0.595 | same | 1.800 ± 0.585 | 1.002 ± 0.747 | same |
| aifoundry3 A slope, fJ/addr bit | 442.6 ± 20.9 | same | 452.5 ± 21.2 | 402.6 ± 22.5 | 443.1 ± 21.0 |
| aifoundry1 c0 ρ | **1.1166 ± 0.0242 (n=8)** | **1.0942 ± 0.0294 (n=10)** | 1.1090 ± 0.0319 | 1.1214 ± 0.0212 | same |
| aifoundry2 e_out (B h32) | 37.480 ± 0.502 | 37.499 ± 0.462 | 38.919 ± 0.596 | 36.573 ± 0.457 | 37.538 ± 0.503 |

**Two places where the arm changes a registered verdict.**

- **Family N's intercept.** With E60's 0.2026 W/°C on aifoundry3 instead of my fitted 0.040, both N
  intercepts fall to ≈0.150 W and the reading flips from "sits on R2, R1 not excluded" to "sits on
  R1, R2 not excluded". The X intercept does not move (0.2751 W either way — it is a slope-fit
  intercept over three rungs measured at the same launch temperature), which is itself an argument
  that the N shift is an artefact of the correction rather than of the data. The intercept is the
  one quantity in the campaign that the leakage choice decides, so it should be reported with that
  flagged.
- **Family R's ρ.** 1.1166 ± 0.0242 over 8 passes excludes 1.000 at |t| = 4.81 against the 4.53
  window; keeping aifoundry1 c0's five set-aside passes gives 1.0942 ± 0.0294 over 10, |t| = 3.20
  against 4.09 — which does **not** exclude 1.000. The per-pass series is 1.236, 1.135, 1.122,
  1.082, 0.993, 1.153, 1.107, 1.105 (and 1.116, 0.894 for the two excluded passes), i.e. one pass
  sits on each hypothesis. I would report ρ as **partial interleaving, OPEN**, with both arms shown,
  rather than as a clean exclusion of 1.000.

## Two things worth flagging beyond the numbers

- **The measured issue rate for mode 179 is 0.6088, not E60's 0.5791** — +5.1%, on all three cards,
  with a within-mode SD of 0.008%. Every watt-stated target in §5.4 was computed at the old rate, so
  the watt columns read ~5% high against our measurements by construction (e.g. `xin_h32` 4.021 W
  tonight against E60's 3.841 W, while the per-bit energy is 20.995 against 21.09 fJ). This is the
  exact failure §5.0 point 1 was written to avoid, and it is also the S10/C16/C59 "reported, not
  gated" row firing on mode 179 itself.
- **Family A is the one family whose measurement is nowhere near its design envelope.** 0.98 W at
  Δ = 3 against a registered ceiling of 0.074 W, with the per-bit reading falling from 652 to 457 to
  447 fJ across a1/a3/a5 and the live-operand arm reading *higher* than the gated one. The rate gate
  is clean (0.006% within 306/307/308) and `participants` is exact, so whatever moves is not issue
  rate or hart count — but it is also not plausibly "energy per toggled register-index bit" at 440 fJ
  a bit. Modes 306/307/308 are three separately emitted kernels reading f0↔{f0, f1, f7}; something
  other than the address Hamming distance differs between them. I would report the ladder as a
  measurement of *something* that scales with Δ and refuse to name it e_addr.
