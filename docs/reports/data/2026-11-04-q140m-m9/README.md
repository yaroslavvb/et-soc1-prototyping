# Q140(m): M9, the power model at 600 MHz - a radix-4 Booth partial-product term takes int8 from 0.25-0.26 W to 0.18 W out of kind and pool 6's named int8 misses to within 0.2 W; no float term moves pool 6, and the bench at nine launch points shows the bit-20 single-bit miss is its own three-point launch average (-1.0 W at M9's prices); frozen before blind pool 7

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds" (items 15, 12 and 7 feed its terms). It answers the Q139 final critic's open **rank 1**: M9,
"a power model more accurate than M6 on new kinds at 600 MHz", built from pool 6's named misses (a high single B bit on a 1/3 base
word, exponent-heavy fp32, int8 with B held, and M8's near-whole-byte discount), each candidate registered before fitting, scored
nested leave one kind out with M6, M7, M8 and M9 on the same folds, then frozen for blind pool 7. The owner's goal for this work, in
his words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately as
possible.*

*Wed 4 Nov 2026 (week 45), 00:29-01:12 PST (the freeze commit, `1f244140`, 01:12:04), Q140(m), desk only, on the Intel (`nice -n 10`, at most 4 threads or bench jobs; corrected after verification, C7: for about 2 minutes about 5 processes ran at once): no card
was opened, no device command was sent, no lab box, Discord, Modal or archive was touched, and nothing was measured in watts here.
Every watt comes from a committed experiment, named where it is used. **The registration, [`M9-REGISTRATION.md`](M9-REGISTRATION.md),
was committed and pushed (`8dfafae3`, 00:45:51 PST) before `fit_m9.py` existed, before any candidate feature was computed on any
row and before the bench check ran.** Blind pool 7 was being written at the same time by an independent designer; this lane never
read that designer's scratch, and pool 7 is not in the tree. M9 builds on Q139(m)'s M8 ([`../2026-11-03-q139m-model/`](../2026-11-03-q139m-model/README.md),
imported unchanged), Q139(u)'s footing ([`../2026-11-03-q139u-footing/`](../2026-11-03-q139u-footing/README.md)), pool 6's two
600 MHz sessions ([E153](../2026-11-03-e153-blind6-aifoundry3/README.md), [E157](../2026-11-03-e157-blind6-card1/README.md)), the
toggle bench (`rtl-sim/fma_toggle_v2/`) and, for aifoundry2, Q140(l)'s part ([`../2026-11-04-q140l-a2-session-terms/`](../2026-11-04-q140l-a2-session-terms/)).*

*Corrected after verification (a dated note, Wed 4 Nov 2026, from 01:45 PST; desk only: no card, no device command, no lab box,
Discord, Modal or archive). An independent verifier re-ran every committed script (each output byte-identical) and re-derived the
int8 result independently. It found eight faults; none changes a frozen file, form, price, band, prediction or registered verdict,
so **M9 is not re-frozen**. Each is marked in place "corrected after verification, C<n>" and set out in
[§ Corrections after verification](#corrections-after-verification-wed-4-nov-2026) at the end; every original word stays. The main
one, **C1: the bench check's post hoc finding is stronger than its evidence.** The three-point launch average does over-count
`b_onebit_b20_third`, by about 1.0 W against nine points at M9's prices. But the nine-point mean itself carries ±0.4-0.5 W (1 s.e.)
there. So the corrected error (+0.28 / −0.04 W) is not resolved from zero or from ±0.5 W. The title's and § 6's "the miss is the
bench's three-point launch average, not a price the model lacks" is withdrawn, and so is "the next model needs nine-point counts".
A convergence rule for the launch average was registered before any count beyond nine points
([`recount-rule/RECOUNT-RULE.md`](recount-rule/RECOUNT-RULE.md), `b4444dd4`, 01:53:26 PST); its first step is C9. **C3:** pool 6's
int8 figures are like for like only against the older forms refitted on the same folds: 0.159-0.189 W (aifoundry3) and
0.169-0.185 W (card 1) → 0.118 / 0.112 W, not the blind 0.20-0.33 W. **C2:** M9 leaves pool 6's int8 4.5 s heat error where it
was (0.13 °C rms).*

## Results

**What this does to prediction** (every M9 figure is the registered nested procedure's, leave one kind out on the same folds as the
other models: out of kind, **not blind**, since the candidates were named from pool 6's misses; W rms of measured − predicted D on
the one footing; "blind" marks the frozen models' registered scores on pool 6, which they never saw):

| quantity | before | after (M9, nested) | resolved? (paired bootstrap, 95%) | source |
|---|---|---|---|---|
| **int8, every row** (174 rows, 83 kinds) | M8's form 0.261 W, M7's 0.256, M6's 0.251 (refitted per fold); M8 / M7 / M6 as frozen 0.267 / 0.252 / 0.242 (in sample on most rows) | **0.177 W** | **yes**, against every one: −0.075 [−0.111, −0.040] W against M6's form, −0.065 [−0.107, −0.027] against M6 as frozen | `nested-m9.json` › `families.int8.same_folds.all`, `paired_bootstrap_over_kinds.all` |
| **int8, pool 6's 12 priority-1 kinds** | blind: M8 0.296 / 0.327 W, M7 0.231 / 0.285, M6 0.199 / 0.222 (aifoundry3 / card 1); *like for like (corrected after verification, C3), the forms refitted on the same folds: M8's 0.159 / 0.180, M7's 0.177 / 0.185, M6's 0.189 / 0.169* | **0.118 / 0.112 W** | yes against M8 and M7 on both cards; against M6 on card 1 (−0.101 [−0.170, −0.029]), not on aifoundry3 (−0.074 [−0.147, +0.012]) (bootstrap over kinds against the frozen models at each row's measured rate, D1) | `summary-m9.txt`; `nested-m9.json` › `families.int8.paired_bootstrap_over_kinds` |
| **floats, every row** (681 rows, 370 kinds) | M8's form 0.194 W, M7's 0.197, M6's 0.198; M8 / M7 / M6 as frozen 0.189 / 0.207 / 0.202 | **0.193 W** | no, against every refitted form (−0.001 [−0.009, +0.007] against M8's) | `families.float.same_folds.all` |
| **fp32, pool 6's 12 priority-1 kinds** | blind: M8 0.330 / 0.386 W, M7 0.313 / 0.395, M6 0.310 / 0.377 | **0.308 / 0.358 W** | no | `summary-m9.txt` |
| **fp16, pool 6's 6 priority-1 kinds** | blind: M8 0.125 / 0.098 W, M7 0.121 / 0.136, M6 0.154 / 0.134 | 0.134 / 0.123 W | no | `summary-m9.txt` |
| **all three formats, pool 6's 30 priority-1 kinds** (the critic's set) | blind: M8 0.286 / 0.323 W, M7 0.252 / 0.314, **M6 0.243 / 0.283** | **0.217 / 0.243 W** | against M8 yes on both cards; against M6 no (−0.026 [−0.076, +0.011] on aifoundry3, −0.040 [−0.080, +0.006] on card 1) | `summary-m9.json` › `combined` |
| the same without the critic's six named-miss tiles (24) | blind: M8 0.190 / 0.184, M7 0.174 / 0.174, M6 0.193 / 0.177 W | 0.186 / 0.173 W | no (within 0.012 W of every model) | `summary-m9.json` |
| the six named-miss tiles themselves (12 rows) | blind, aifoundry3 / card 1: `int8.bheld_bit4` −0.54 / −0.43 W (M8), `int8.a_zeros_b_lineflip` +0.62 / +0.78, `int8.b_line_zero_ff` +0.36 / +0.38, `fp32.b_onebit_b20_third` −0.81 / −1.09 | bheld_bit4 −0.16 / −0.06, a_zeros_b_lineflip −0.05 / +0.14, b_line_zero_ff −0.01 / +0.02, bheld_bit1 −0.15 / −0.19, bheld_bit7 +0.14 / +0.06; **b20_third −0.72 / −1.00** | — | `summary-m9.txt` |
| int8 on pool 5's rows (E141 / E142, out of kind) | M8's form 0.352 / 0.294 W; M8 as frozen 0.344 / 0.319 (in sample) | **0.150 / 0.178 W** | — | `families.int8.same_folds.exp E141`, `exp E142` |
| 95% bands | M8: k 2.20 floats / 2.83 int8 (*2.84: `m8.json` gives 2.835; corrected after verification, C8*) | **k 2.00 floats / 1.86 int8**; floats 647 of 681 inside, pool rows 126 of 133 (each left out of k: 126); int8 165 of 174, pool rows 64 of 65 (64) | a calibration, not a test | `families.*.band` |
| card 1's scale | M8's C0 0.9616 | **0.9616** (M8's card term kept: the same E78/E82 pairs) | — | `m9.json` › `families.*.card1_scale_by_format` |
| heat | M7's law (0.1186 / 0.1151 °C per board W over a 4.5 s run) | **carried unchanged**, applied to M9's S | — | `m9.json` › `heat` |
| aifoundry2 | M8's relation (cap 65.20 W) | **nothing fitted here**: M9's D at 600 MHz goes through M8's frozen relation by default, or Q140(l)'s part with `--a2-terms` | — | `predict_blind7.py` |

**In plain words.** M9 is the lab's model of the watts a matmul draws over the same kernel on zeros, from the bytes it multiplies, at
600 MHz. **For int8 it finds the missing piece.** int8's multiply is written as a plain `*` in the open RTL, so the toggle bench never
saw the array of partial products a synthesised multiplier builds. A radix-4 Booth recoder on B (E151's registered verdict) turns
each B byte into four digits; a digit of zero makes its row of partial products go quiet whatever A does. Counting those rows' bit
flips straight from the tile's bytes (`bpp_r4`, priced at 2.2 ± 0.3 fJ a flip) explains why a B held at one bit (one or two live
digits) draws less than random B (three on average), and why B lines of 0x55/0xAA (four live digits each) draw more: int8's error
over every committed row falls from about 0.25 W to 0.18 W out of kind, and on pool 6's int8 tiles from 0.20-0.33 W (blind, the
older models) to 0.11-0.12 W *(corrected after verification, C3: like for like, the older forms refitted on the same folds read
0.16-0.19 W there, so the gain on pool 6 is 0.04-0.06 W)*. **For the floats nothing registered helps on new kinds.** An exponent-stage price (`xstage`, 0.65 ±
0.36 fJ over the rest's 2.08) passes the rule by 0.004 W over all rows but leaves pool 6's fp32 at 0.31 / 0.36 W, and the term aimed at
the single bit on a 1/3 base word (`lq1`, from the bench's launch points) does not lower the nested error, so it is dropped; that
tile still reads 0.7-1.0 W high. **The bench says why:** counted at nine points of a launch instead of three, the bench's own count for
that tile falls by 18%, which at M9's prices is −1.0 W, the size of the miss; and the same count error runs from −1.0 W to +0.7 W over
four base words at bit 20. The miss is in how the bench averages a launch, so the next model needs nine-point counts, not another price.
*(Withdrawn after verification, C1: the nine-point mean itself carries ±0.4-0.5 W at 1 s.e. on that tile, so the miss is not shown to
be the launch average alone, and nine points are not shown to be enough.)*
Over all three formats, on the 30 kinds the critic scores, M9 reads 0.217 / 0.243 W (aifoundry3 / card 1) against M6's blind 0.243 /
0.283 W: better, but not by a margin the bootstrap resolves, and not blind. Pool 7 is the test.

**1. Registered against post hoc, number by number** (the registration's sections; everything not listed as post hoc ran as
registered, with no amendment):

| # | registered (`8dfafae3`, 00:45:51 PST) | what ran | registered or post hoc |
|---|---|---|---|
| R1 | rows: M8's 767 + pool 6's 44 new kinds on both cards from E153's and E157's primary reductions | 855 rows (681 float, 174 int8), none missing | registered |
| R2 | anchors, E78's anchors and the K1 re-runs left out; each pool-6 tile its own kind | as registered | registered |
| R3 | candidate features: `c_end`; `xfld32`; `xstage32` or `xstage`; `lq1`; `bsat`, `bsat_cap` or neither; `bpp_r4`; `bnz_a` | all computed for every row (each row's bench counts matched by its own bench features, departure D2) | registered |
| R4 | 24 float and 12 int8 forms, M8's card term C0 fixed | as registered | registered |
| R5 | leave one kind out; M9 nested, M8's/M7's/M6's (and M5's) forms refitted, M8/M7/M6 as frozen, on the same folds | as registered | registered |
| R6 | a feature stays only if nested(all forms) < nested(forms without it); the frozen form the plain best among forms within the kept set | floats: `c_end`, `xfld32`, `xstage` kept, `xstage32` (equal) and `lq1` (0.1930 with, 0.1925 without) not; frozen `G8+c_end+xstage`. int8: `bsat`, `bpp_r4` kept, `bsat_cap`, `bnz_a` not; frozen `J8+bsat+bpp_r4` | registered |
| R7 | bootstrap over kinds, 2,000 draws, seed 140, on all rows, pool 6, pool 6 without the six | as registered (`paired_bootstrap_over_kinds`) | registered |
| R8 | the check: M8/M7/M6 as frozen reproduce E153's and E157's registered predictions within 0.002 W, else stop | 264 predictions, largest difference 0.00005 W: PASS | registered |
| R9 | bands: k = max(q95 all rows, q95 pools 3-6's rows) | floats 1.996 (both quantiles alike), int8 1.864 (all rows) | registered |
| R10 | heat carried from M7; aifoundry2 not fitted, M8's relation by default or Q140(l)'s part | as registered | registered |
| R11 | the bench check at four base words (§ 8): expectation α > 0 | α = +0.224, **MET** (§ 6) | registered (the check); the comparison with `lq1`'s price, the two pool-6 tiles at nine points and the spread count are **post hoc**, since `lq1` was not kept |
| P1 | the three formats together on pool 6 per card, against the frozen models' registered blind errors, with a bootstrap over tiles (`summarize_m9.py`) | § 4 | **post hoc** (a summary of the registered outputs, no fit) |
| P2 | the frozen form's own leave-one-kind-out errors, and the procedure restricted to the kept features, beside the registered nested score | `M9_frozen_form_loko`, `M9_restricted_nested` | **post hoc** (the kept set was chosen on all rows) |
| P3 | pool 6 by case | § 4 | **post hoc** |

**2. The selection** (`nested-m9.json` › `families.<family>.feature_tests`; nested rms over all the family's rows, W):

| feature | nested with every form | nested without the forms that hold it | stays? |
|---|---:|---:|---|
| `c_end` (M8's C-register term) | 0.1930 | 0.1987 | **yes** |
| `xfld32` (exponent bits on the bus, fp32) | 0.1930 | 0.1935 | yes (not in the frozen form: the plain best among the kept forms leaves it out, 0.1925 against 0.1927) |
| `xstage32` (the bench's exponent stage, fp32) | 0.1930 | 0.1930 | no |
| `xstage` (the bench's exponent stage, both float formats) | 0.1930 | 0.1970 | **yes** |
| `lq1` (the launch-shape term for single bits) | 0.1930 | 0.1925 | **no** |
| `bsat` (M8's near-whole-byte discount, refitted) | 0.1769 | 0.1830 | **yes** |
| `bsat_cap` (bounded at 1,024 bits an op) | 0.1769 | 0.1769 | no |
| `bpp_r4` (Booth partial products, B recoded) | 0.1769 | 0.1798 | **yes** |
| `bnz_a` (A's flips × B's live digits) | 0.1769 | 0.1769 | no |

The float procedure's inner step chose the form with every candidate (`G8+c_end+xfld32+xstage+lq1`) in 369 of 370 folds; the
rule then removes `lq1`, whose removal lowers the nested error. int8's chose `J8+bsat+bpp_r4` in all 83. Dropped from the frozen
forms in turn (plain leave one kind out): floats `c_end` 0.1970 and `xstage` 0.1937 against 0.1925; int8 `bsat` 0.1852 and
`bpp_r4` **0.2614** against 0.1769. Without `bpp_r4`, M8's discount (`J8+bsat`) is the worst int8 form there is (0.2614).

**3. M9, frozen** ([`m9.json`](m9.json), written by [`fit_m9.py`](fit_m9.py); fJ per count, ± 1 s.e., jackknife by kind; M8's in
brackets):
- **Floats, `G8+c_end+xstage`**: mult 1.647 ± 0.028 (1.629), add32 1.623 ± 0.035 (1.630), add16 1.560 ± 0.044 (1.579), bus 7.12 ±
  0.47 (6.81), rest 2.078 ± 0.184 (2.284), clk 0.657 ± 0.064 (0.633), gtr 146 ± 16 (141), glive 2.74 ± 0.44 nJ an op at every slot
  live (2.90), c_end 6.19 ± 1.91 (6.44), **xstage 0.65 ± 0.36** (new: the exponent stage's count is priced at rest + xstage).
- **int8, `J8+bsat+bpp_r4`**: nets_nobus 2.822 ± 0.108 (3.405), bus 7.5 ± 1.6 (11.3), clk 2.204 ± 0.133 (2.073), b138 +21.6 ± 7.4
  (+5.1), bsat −29.3 ± 9.4 (−56.8), **bpp_r4 +2.205 ± 0.271 fJ per Booth partial-product bit flip** (new). The array term takes part
  of the generic net price (nets_nobus 3.41 → 2.82) and half of M8's discount (bsat −57 → −29).
- **Card term**: M8's C0, 0.9616 on both families. **Interval pools** (M9's nested rms, W): fp32 aifoundry3 0.200, card 1 0.211;
  fp16 0.168, 0.178; int8 0.169, 0.185. **Band k**: floats 1.996, int8 1.864. **Heat**: M7's law and band, as M8.

**4. The same folds, every model** (rms of measured − predicted D, W; nested or leave one kind out, except the frozen columns; on
pool 6 the frozen models are scored at each row's measured rate here, departure D1, and their registered blind figures are in
`summary-m9.txt`):

| rows | n | **M9 nested** | M8's form | M7's form | M6's form | M5's form | M8 frozen | M7 frozen | M6 frozen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fp32, aifoundry3 | 241 | **0.200** | 0.208 | 0.215 | 0.218 | 0.235 | 0.202 | 0.216 | 0.219 |
| fp32, card 1 | 171 | **0.211** | 0.218 | 0.213 | 0.198 | 0.218 | 0.216 | 0.231 | 0.215 |
| fp16, aifoundry3 | 124 | **0.168** | 0.150 | 0.159 | 0.172 | 0.220 | 0.147 | 0.164 | 0.164 |
| fp16, card 1 | 145 | **0.178** | 0.171 | 0.174 | 0.182 | 0.189 | 0.165 | 0.196 | 0.187 |
| int8, aifoundry3 | 90 | **0.169** | 0.262 | 0.253 | 0.253 | 0.259 | 0.266 | 0.243 | 0.244 |
| int8, card 1 | 84 | **0.185** | 0.260 | 0.259 | 0.250 | 0.253 | 0.269 | 0.262 | 0.240 |
| pool 6 fp32, aifoundry3, priority 1 | 12 | **0.308** | 0.324 | 0.314 | 0.317 | 0.327 | 0.338 | 0.320 | 0.316 |
| pool 6 fp32, card 1, priority 1 | 12 | **0.358** | 0.377 | 0.366 | 0.358 | 0.373 | 0.390 | 0.381 | 0.360 |
| pool 6 fp16, aifoundry3, priority 1 | 6 | **0.134** | 0.120 | 0.129 | 0.161 | 0.127 | 0.124 | 0.140 | 0.181 |
| pool 6 fp16, card 1, priority 1 | 6 | **0.123** | 0.116 | 0.123 | 0.165 | 0.106 | 0.129 | 0.097 | 0.114 |
| pool 6 int8, aifoundry3, priority 1 | 12 | **0.118** | 0.159 | 0.177 | 0.189 | 0.185 | 0.290 | 0.224 | 0.192 |
| pool 6 int8, card 1, priority 1 | 12 | **0.112** | 0.180 | 0.185 | 0.169 | 0.178 | 0.322 | 0.277 | 0.213 |
| pool 6 floats, without the six (all 26 kinds, both cards) | 52 | **0.230** | 0.239 | 0.228 | 0.211 | 0.228 | 0.258 | 0.230 | 0.214 |
| pool 6 int8, without the six (12 kinds, both cards) | 24 | **0.156** | 0.355 | 0.270 | 0.230 | 0.241 | 0.413 | 0.289 | 0.215 |
| E147's single-bit steps | 70 | 0.221 | 0.225 | 0.232 | 0.235 | 0.231 | 0.218 | 0.224 | 0.229 |

**Pool 6, the three formats together, against the frozen models' registered blind errors** (post hoc summary P1,
[`summary-m9.txt`](summary-m9.txt); paired bootstrap over tiles, 2,000 draws, seed 140):

| card, set | n | **M9 nested** | M8 blind | M7 blind | M6 blind | M9 − M6 | M9 − M8 |
|---|---:|---:|---:|---:|---:|---|---|
| aifoundry3, priority 1 | 30 | **0.217** | 0.286 | 0.252 | 0.243 | −0.026 [−0.076, +0.011] | −0.069 [−0.129, −0.016] |
| card 1, priority 1 | 30 | **0.243** | 0.323 | 0.314 | 0.283 | −0.040 [−0.080, +0.006] | −0.080 [−0.158, −0.026] |
| aifoundry3, all 44 new kinds | 44 | **0.227** | 0.339 | 0.281 | 0.245 | −0.018 [−0.071, +0.031] | −0.112 [−0.228, −0.020] |
| card 1, all 44 new kinds | 44 | **0.248** | 0.366 | 0.319 | 0.274 | −0.026 [−0.080, +0.043] | −0.118 [−0.237, −0.026] |
| aifoundry3, priority 1 without the six | 24 | **0.186** | 0.190 | 0.174 | 0.193 | −0.007 [−0.057, +0.036] | −0.004 [−0.030, +0.023] |
| card 1, priority 1 without the six | 24 | **0.173** | 0.184 | 0.174 | 0.177 | −0.003 [−0.054, +0.043] | −0.011 [−0.036, +0.014] |

By the pool's cases (both cards, all 44 kinds; M9 nested against M8 / M7 / M6 blind): **L, int8 whole-line, 0.159 against 0.699 /
0.420 / 0.337 W; B, int8 B-position, 0.165 against 0.314 / 0.366 / 0.252**; C, the C-register candidate, 0.054 against 0.097 / 0.172
/ 0.248; Z, zeros' transport, 0.226 against 0.417 / 0.231 / 0.259; R, real tiles, 0.145 against 0.151 / 0.169 / 0.151; W, power-law
weights, 0.153 against 0.121 / 0.127 / 0.122; **E, exponent-heavy, 0.293 against 0.288 / 0.247 / 0.209 (mean +0.175: the card still
pays more than M9 on these)**; **S, single bits on other base words, 0.419 against 0.484 / 0.518 / 0.463** (b20_third −0.72 /
−1.00 W).

**5. Bands.** Power half-width = k × √(pool² + s² xᵀCx), with M9's nested pools and k = 1.996 (floats) and 1.864 (int8), the larger
of the all-rows and pool-rows 95th percentiles of |nested residual| / pool. Floats: 647 of 681 rows inside, pools 3-6's rows 126 of
133 (126 with each left out of k), pool 6's 50 of 54; int8: 165 of 174, pool rows 64 of 65 (64), pool 6's 34 of 34. A calibration on
rows the procedure held out kind by kind, not a test.

**6. The bench check at four base words** (registration § 8; [`bench-check/`](bench-check/); bench only, no board watt):

The 16 single-bit tiles (A = 1.0; B = w with bit k flipped in columns 8-15; four base words, bits 12, 17, 20 and 21) were counted by
the same bench build (its seven files hash as Q139(x)'s, [`bench-check/bench-sha256.txt`](bench-check/bench-sha256.txt)) at the nine
midpoints of ninths of a 0.5 s launch, which include the bench's three, 00:46:29-01:05:50 PST, 4 jobs at nice 10; C equal to
software at every point (`check_mismatch` 0). [`benchcheck_m9.py`](benchcheck_m9.py) → [`bench-check/benchcheck.txt`](bench-check/benchcheck.txt):

| base word | bit 12 | bit 17 | bit 20 | bit 21 |
|---|---:|---:|---:|---:|
| 1/3 `0x3EAAAAAB` | +0.047 | −0.517 | **−0.995** | −0.399 |
| E67's `0x3FBBC9E4` | +0.012 | −0.316 | −0.720 | −0.539 |
| E79's / E102's `0x3FBD207C` | +0.045 | +0.018 | −1.037 | −0.921 |
| π `0x40490FDB` | +0.069 | −0.209 | **+0.665** | +0.367 |

*The bench's own error from averaging a launch at three points instead of nine, at M9's frozen prices (W of D; negative: the
three-point average over-counts).* *(Corrected after verification, C1: each nine-point mean carries its own error. At 1 s.e., the
larger of the sample and interleaved-rule estimates, it is 0.08-0.12 W at bit 12, 0.12-0.27 W at bit 17, 0.37-0.65 W at bit 20 and
0.43-0.98 W at bit 21; per tile in [`recount-rule/RECOUNT-RULE.md`](recount-rule/RECOUNT-RULE.md) § 5.)*

- **Registered expectation: α > 0. MET:** α = +0.224, r(lq1, m3 − m9) = +0.56. A high first point does mean the three-point
  average over-counts.
- **But the error is large, and the base word sets its sign.** At bit 20 it runs from −1.04 W (E79's word) to +0.67 W (π); at bit
  12 it is within ±0.07 W on every word. `lq1` follows it only partly (on 1/3's bit 21 the two have opposite signs), which is why
  `lq1` as a priced term failed the rule. Post hoc, its price in the form holding every float candidate, fitted on all rows, is −0.33
  fJ a net against the bench's own −α × 1.97 fJ = −0.44 fJ (ratio 0.74).
- **Post hoc, and the main finding:** two of the 16 tiles are pool 6's `fp32.b_onebit_b12_third` and `fp32.b_onebit_b20_third`, byte
  for byte, and the bench reproduces their committed counts at its three points exactly. With the nine-point launch average at M9's
  frozen prices, **b20_third's M9 error moves from −0.72 / −1.00 W to +0.28 / −0.04 W** (aifoundry3 / card 1; M8 as frozen −0.77 /
  −1.04 → +0.23 / −0.09 W), and b12_third's from +0.32 / +0.22 to +0.28 / +0.18 W. So the critic's "high single B bit on a 1/3 base
  word" miss is the bench's three-point launch average, not a price the model lacks. The base-word term the critic asked for is a
  count of the launch at more points. *(Corrected after verification, C1: the nine-point mean carries ±0.51 W (1 s.e.) on
  b20_third, so +0.28 / −0.04 W is not resolved from zero or from ±0.5 W; the direction holds (the three-point average over-counts
  by about 2-2.6 s.e.), the last two sentences are withdrawn. b12_third's figures mix forms: its nested error comes from the form
  holding `lq1`, the correction from the frozen form's prices; like for like, the frozen form's own error moves from +0.24 / +0.15
  to +0.20 / +0.10 W, ±0.12 W.)*
- **What a nine-point recount would cover (post hoc):** of M9's 611 float rows with a counts row (E147's steps aside), 77 have a
  three-point spread over 10% of their mean and 29 over 20% (median 1.3%). Recounting those, E147's steps and their zeros, and pool 7's
  tiles at nine points is about two bench-hours at 4 jobs. *(Corrected after verification, C1: the recount is sized by the
  convergence rule in [`recount-rule/`](recount-rule/RECOUNT-RULE.md), not set at nine points; the 77 rows are 45 counted tiles.)*

**7. aifoundry2.** Nothing is fitted here. [`predict_blind7.py`](predict_blind7.py) gives every tile M9's D at 600 MHz on aifoundry3's
footing with its 95% band, and then:
- **without `--a2-terms`**: M8's frozen aifoundry2 relation, bands and peak rule (`m8.json` › `aifoundry2`, carried in `m9.json` ›
  `aifoundry2_default`), applied to M9's D: the burst clock, board, burst D, die rise, P800, the expected and 95% peak and the 82 W
  flag, exactly as `predict_blind6.py` did for M8's D;
- **with `--a2-terms <m9_a2.json>`** (Q140(l)'s part, applied by Q140(x)): it imports `predict_m9_a2.py` beside that JSON and calls
  its `burst(D, t, anchors, die_starts, D_band_hw)` for every tile with M9's D and half-band, the session's own zeros-anchor reads from
  `--a2-session <json>` (`{format: [{burst_w, burst_mhz, die_start}, ...]}`) and a die start from `--a2-die-start`; the result is each
  tile's `M9.a2_q140l` block and `a2_part.primary` = `a2_q140l`. Tested here on Q140(l)'s uncommitted draft (it ran, in scratch);
  nothing of Q140(l)'s is committed by this lane. *(Corrected after verification, C6: Q140(l) had committed its part, `5b98bd5c` at
  01:04:31 PST, before this README was written. On the committed part the predictor's output equals the draft run's.)*
- Always: `a2-inputs-aifoundry2.json`, M9's and M8's D at 600 MHz per tile with M9's band, the input any aifoundry2 relation takes.

**8. The predictor and its self-test.** `predict_blind7.py <pool_dir> <card>` (aifoundry3 | aifoundry1c1 | aifoundry2) reads a pool in
blind pool 5's layout (`blind7.json` preferred) and the bench's counts for its tiles at the bench's three launch points (`--counts`;
without them it prints the bench command and exits 2), and writes `predictions-<card>.json` and `.md`: per tile M9's, M8's, M7's and
M6's D with 95% bands and die rise (aifoundry3, card 1), or the bursts (aifoundry2). M8, M7 and M6 go through `predict_blind6.py`'s code
paths unchanged. **Self-test** ([`selftest_predict_blind7.py`](selftest_predict_blind7.py) →
[`selftest-predict-blind7.txt`](selftest-predict-blind7.txt)): on pool 6, M8's, M7's and M6's predictions equal Q139(x)'s committed
`predictions-blind6-<card>.json` field for field on all three cards (1,200 + 1,200 + 2,300 fields, 0 differ), and the 372 values of
M9's terms the predictor recomputes from the counts and the bytes for pool 6's 44 kinds equal `rows-m9.json`'s (0 differ): **PASS,
5,072 fields**. Pool 6 is in M9's fit, so M9's numbers there test nothing.

## What this does to predicting power and heat

**Terms tested** (each registered before it was computed): M8's near-whole-byte discount kept, bounded or dropped (kept, refitted at
−29 ± 9 fJ a bit, about half of M8's; the bound at 1,024 bits did not help); an exponent-field term for fp32 from the bytes (`xfld32`,
passes the rule but is not in the frozen form) and from the bench (`xstage32` no; `xstage` on both float formats yes, +0.65 ± 0.36 fJ a
count); a base-word term for single bits from the bench's launch points (`lq1`, not kept: it does not lower the nested error); a
held-B int8 term (`bpp_r4`, the radix-4 Booth partial products with B recoded, kept at 2.2 ± 0.3 fJ a flip; the simpler `bnz_a` not).
**Out-of-sample error before → after** (nested leave one kind out, the same folds, one footing; out of kind, not blind): **int8 over
every committed row 0.251-0.261 W (M6's, M7's, M8's forms) → 0.177 W, resolved against every model**; int8 on pool 6's 12 priority-1
kinds, blind before, 0.199-0.296 W (aifoundry3) and 0.222-0.327 W (card 1) → 0.118 and 0.112 W *(corrected after verification, C3:
like for like, the older forms refitted on the same folds, 0.159-0.189 W and 0.169-0.185 W → 0.118 and 0.112 W)*; floats over every row 0.194-0.198 W →
0.193 W, not resolved; fp32 on pool 6's 12 priority-1 kinds 0.310-0.330 / 0.377-0.395 W blind → 0.308 / 0.358 W; all three formats on
the 30 kinds the critic scores, M6's blind 0.243 / 0.283 W → 0.217 / 0.243 W (not resolved against M6; resolved against M8). The
critic's bound, every model at 0.17-0.19 W on the 24 kinds without the six, is where M9 lands (0.186 / 0.173 W): the int8 named misses
are closed, the fp32 single bit (b20_third, −0.72 / −1.00 W) and the exponent-heavy excess (+0.18 W mean over 20 rows) are not.
**The bench term corrected, post hoc:** the bench's three-point launch average is wrong by −1.04 to +0.67 W on single high mantissa
bits, depending on the base word, and on b20_third by −1.0 W; with nine points that tile's error would be +0.28 / −0.04 W. The next
model's single-bit term is a nine-point count (77 of 611 float rows spread over 10% between the three points), registered first.
*(Corrected after verification, C1: ±0.4-0.5 W at 1 s.e. on that tile, not resolved; the next model's count is sized by the
convergence rule, not set at nine.)*
**Heat is unchanged in form**: M7's law is carried, so the die's rise follows M9's predicted board watts; on int8 kinds whose power
M9 now predicts 0.1-0.4 W better, the 4.5 s rise moves by 0.01-0.05 °C. The blind before → after is pool 7's (E163, E164).
*(Corrected after verification, C2: that is below the die's whole-degree readout, and pool 6's int8 4.5 s heat error is unchanged:
0.126 / 0.129 °C rms with M9's D on the 12 priority-1 kinds (aifoundry3 / card 1), against M8's registered 0.128 / 0.123 °C.)*

## Departures

- **D1** *(decided while writing `fit_m9.py`, before any fit ran; not in the registration)*. In the same-folds tables every model,
  the frozen ones included, is scored at each row's measured op rate (M8's convention for its own pool-5 rows). Pool 6's sessions ran
  at a duty of 0.9932, against the nominal 0.9963, because the C log's DMA widened the gap between launches (E153's README), so on pool
  6's rows the frozen models' errors there differ from E153's and E157's registered ones by about 0.3% of D. The check R8 is run at the
  nominal rate their predictions used (it passes to 0.00005 W), and their registered blind errors are the "blind" figures above
  (`nested-m9.json` › `check_frozen_pool6.registered_blind_tables`). **For pool 7:** `predict_blind7.py` predicts at the nominal rate;
  a pool-7 session that logs C as E153 did will read about 0.3% low against it on every tile.
- **D2** *(after run 1 stopped on it, before any fit)*. The registration did not say how a row finds its bench counts. Matching by
  M6's tile-hash index left 94 rows unmatched (E93's, E95's, E121's and E131's tiles are counted under other names in Q133(b)'s and the
  E94/E95 counts), so run 1 stopped before fitting, as the code required. Each row is now matched to the committed counts row whose
  M5 bench features equal its own (to 0.01 count), across every counts file of this bench, with a stop if two matching rows disagree on
  the launch points: 785 rows matched, 0 unmatched, 0 ambiguous; E147's steps use E147's merged counts, item minus its own zero.
- **D3** The PATH's python3 has no numpy; every run used the Intel's `/usr/bin/python3` 3.9.6 with numpy 1.26.4, with `-B` (no
  bytecode in the tree).

## What this cannot say

- **Nothing here is blind.** The candidates were named after reading pool 6's committed misses (E153, E157), the critic's six tiles
  and the bench's committed per-point counts of pool 6's S tiles and of twelve E147 tiles; pool 6 is training data now. Pool 7 is the
  test. *(Dated note, Wed 4 Nov 2026: the registration says "five E147 tiles"; the per-point counts of twelve were printed before it
  was written (`aj_19`, `aq`, `bj_2`, `bj_17`, `bj_21`, `bj_24`, `bj_25`, `bj_26`, `bj_28`, `bj_29`, `bp_21`, `hq`), three of them
  quoted there. Its text stays as committed.)*
- **The float terms are not shown to help new kinds.** `xstage` passes the registered rule by 0.004 W over 681 rows and is kept, but
  M9's fp32 on pool 6 is level with M6's, and fp16's over every row is a little worse than M8's form (0.168 / 0.178 against 0.150 /
  0.171 W): the nested procedure mostly picked a form holding `lq1` too. The frozen form's own leave-one-kind-out error (post hoc,
  P2) is 0.192 W over all floats.
- **`bpp_r4` is a count of a multiplier nobody has seen.** It assumes radix-4 Booth on B with each row's partial product inverted for
  a negative digit; the silicon's netlist is not public (the private archive's half of item 12 stays private). It is a fitted price on
  a modelled count, resolved out of kind on 83 int8 kinds, and its reading as the array's switching is a hypothesis the blind pool
  tests.
- **`bsat` survives at half its size** beside `bpp_r4`; with both, b_line_55_aa still reads +0.23 / +0.34 W and the df-1.5 power-law
  tile (61.7% gated) went from −0.11 to +0.18 W.
- **The single bit on 1/3 is explained post hoc, not fixed.** `lq1` failed the rule. The bench check (§ 6) shows the bench's own
  three-point launch average over-counts that tile by about 1.0 W at M9's prices (±0.4-0.5 W at 1 s.e. of the nine-point mean;
  corrected after verification, C1), but the nine-point counts exist for 16 tiles only,
  two of them pool 6's; M9's training rows and pool 7's predictions use three-point counts, so M9 keeps the miss on any such tile.
- One lane wrote M9 and its scoring code; pool 7's designer is independent, and E163 and E164 are its test.

## Order (PST, Wed 4 Nov 2026)

1. 00:29 brief read; 00:30-00:44 the critic's rank 1, M8's registration, README and code, M7's, M6's and M5's code, Q139(u)'s rule,
   pool 6's README and predictions note, E153's and E157's READMEs and power rows, E147's README, `make_kinds.py`'s streams, `tima_top.v`,
   the bench's per-point counts of pool 6's S tiles and twelve E147 tiles; one bench point-run timed on pool 6's zeros anchor (19 s).
2. 00:45:51 **the registration committed and pushed** (`8dfafae3`).
3. 00:46:29 the bench check started (§ 6; 16 tiles × 9 points, 4 jobs, nice 10, in scratch).
4. 00:47-00:52 `fit_m9.py` written; the Booth features checked on ten pool-6 tiles (zeros 0; the all-gated tile 0).
5. 00:52:25 run 1 stopped at D2 (no fit); 00:53:48-00:54:11 run 1 again, into scratch, read; 00:56:12-00:56:46 **the freeze**, into
   this directory: every same-folds table and `m9.json` identical to run 1's.
6. 00:57-01:05 `predict_blind7.py`, its self-test (PASS), the plug-in tried on a mock and on Q140(l)'s draft (scratch), `summarize_m9.py`.
7. 01:05:50 the bench check ended; 01:06-01:10 `benchcheck_m9.py`, then this README.

## Files

| file | what |
|---|---|
| [`M9-REGISTRATION.md`](M9-REGISTRATION.md) | the registration, committed first (`8dfafae3`, 00:45:51 PST) |
| [`fit_m9.py`](fit_m9.py) | the fit: M8's rows plus pool 6's, the candidate features (the Booth count, the bench's exponent stage and launch shape), the 36 forms, the nested procedure and the per-feature rule, every model on the same folds, the bootstraps, the band rule, the check of the frozen models, the freeze |
| [`m9.json`](m9.json) | **the freeze**: per family the form, kept features, constants (J), jackknife covariance, card term, interval pools, band k; heat carried from M7; M8's aifoundry2 block as the default; the band rule in words |
| [`nested-m9.json`](nested-m9.json), [`fit-output.txt`](fit-output.txt) | every form's plain errors, the inner picks, the feature tests, the same-folds tables for every model by format, card, experiment and pool-6 subset, the bootstraps, the bands, the largest misses, pool 6's rows, the check |
| [`rows-m9.json`](rows-m9.json) | the 855 rows with every feature and the counts row each was matched to |
| [`summarize_m9.py`](summarize_m9.py), [`summary-m9.json`](summary-m9.json), [`summary-m9.txt`](summary-m9.txt) | post hoc P1 and P3: pool 6's three formats together per card against the registered blind errors, by case, the six tiles |
| [`predict_blind7.py`](predict_blind7.py) | the frozen predictor for pool 7 (M9, M8, M7, M6; three cards; aifoundry2 through M8's relation or Q140(l)'s part) |
| [`selftest_predict_blind7.py`](selftest_predict_blind7.py), [`selftest-predict-blind7.txt`](selftest-predict-blind7.txt) | the self-test on pool 6 |
| [`benchcheck_m9.py`](benchcheck_m9.py), [`bench-check/`](bench-check/) | § 6: the 16 tiles' maker and manifest, the bench's counts at nine launch points, the build's hashes, the result |
| [`recount-rule/`](recount-rule/RECOUNT-RULE.md) | *added after verification (C1, C9)*: the convergence rule for the bench's launch average (`RECOUNT-RULE.md`, `recount_rule.py`, the pilot's tiles and points, the recount set), registered in `b4444dd4` before any count beyond nine points; then the 27-point sizing step's counts and result |

sha256 at the freeze: `m9.json` **`322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835`**; `fit_m9.py`
`0b3f1074c4a84865dd2f6e6e4e018a56ce28e016b22b6fbfd66b74a1520752f5`; `nested-m9.json`
`f6057e3b9f055d538182485756fbe7cde27f96f8af7617085314d68ebada44a0`; `rows-m9.json`
`96ec405065257a543f7385711ad1841eb37316cc0148c362f35727534d05d41e`; `predict_blind7.py`
`32b5cdac865945e88e4616a30de78ce93eaf97381fe38f3d62aab5cbf158c2d1`; `bench-check/counts-cal.json`
`904337ddafd2760f47e3136f4d33b3c6468a454700cc9acfd9b65742e5625fd7`; the registration `M9-REGISTRATION.md`
`5d8546cbfe1df58ce39d526e8067c1e595177d144e338a585a675211c7058605` (as committed in `8dfafae3`). Imported unchanged at run time
(the predictor reads them; `git diff 8dfafae3 --` over them must be empty before pool 7's predictions): Q139(m)'s `fit_m8.py`,
`m8.json`, `predict_blind6.py`'s code paths (copied, self-tested), Q138(m)'s `fit_m7.py`, `m7.json`, `predict_blind5.py`, Q137(m)'s
`fit_m6.py`, `m6_rows.py`, `m6.json`, Q133(b)'s `fit_m5.py`, Q139(u)'s `reduce_footing.py` and `footing.json`,
`tools/claims-v3/kinds/make_kinds.py`, `blind5/make_blind5.py`, E147's `posthoc_m7_e147.py`, E119's `make_predictions_e119.py`, and
the counts files `fit_m9.COUNTS_FILES` names.

Rerun from the top of the tree, with a python that has numpy:

```
python3 -B docs/reports/data/2026-11-04-q140m-m9/fit_m9.py <scratch dir> > docs/reports/data/2026-11-04-q140m-m9/fit-output.txt   # ~40 s
python3 -B docs/reports/data/2026-11-04-q140m-m9/summarize_m9.py
python3 -B docs/reports/data/2026-11-04-q140m-m9/selftest_predict_blind7.py <scratch dir> > docs/reports/data/2026-11-04-q140m-m9/selftest-predict-blind7.txt
python3 -B docs/reports/data/2026-11-04-q140m-m9/benchcheck_m9.py
# pool 7: count its tiles with the bench at its default three launch points (Q133(b)'s build; predict_blind7.py prints the command), then per card
python3 -B docs/reports/data/2026-11-04-q140m-m9/predict_blind7.py tools/claims-v3/kinds/blind7 aifoundry3 --counts <counts.json>
python3 -B docs/reports/data/2026-11-04-q140m-m9/predict_blind7.py tools/claims-v3/kinds/blind7 aifoundry2 --counts <counts.json> \
    --a2-terms docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json
```

## Corrections after verification (Wed 4 Nov 2026)

*Desk only, from 01:45 PST: no card, no device command, no lab box, Discord, Modal or archive. Each correction comes after M9's fit,
scores and freeze (`1f244140`) and touches none of them: no frozen file, form, price, band, prediction or registered verdict
changes, and M9 is not re-frozen. Every original word above stays; the marks "corrected after verification, C<n>" point here.*

- **C1 (the main one): the post hoc bench finding is stronger than its evidence.** The bench's per-point counts are spiky, not
  smooth, so the nine-point launch average carries its own error. Priced at M9's frozen prices, the larger of the sample s.e. and the
  interleaved-rule s.e. (the three interleaved three-point rules among the nine) is 0.51 W on `cal_third_b20` (0.38 W by the sample
  alone), 0.98 W on `cal_third_b21`, 0.37-0.65 W on the other bit-20 tiles, and 0.08-0.27 W at bits 12 and 17
  ([`recount-rule/RECOUNT-RULE.md`](recount-rule/RECOUNT-RULE.md) § 5 lists all 16). In the verifier's words: *post hoc, on
  b20_third the three-point launch average over-counts by about 1.0 W against a nine-point average; the nine-point mean itself carries
  ±0.4-0.5 W (1 s.e.) of sampling error at M9's prices, so the corrected error (+0.28 / −0.04 W) is not resolved from zero or from
  ±0.5 W.* The direction holds: on that tile the three-point rule's mean is 2.0-2.6 s.e. above the nine-point one. **Withdrawn:**
  "not a price the model lacks", "the next model needs nine-point counts, not another price", "the base-word term the critic asked
  for is a count of the launch at more points", "the next model's single-bit term is a nine-point count", and the title's "shows the
  bit-20 single-bit miss is its own three-point launch average". How much of the single-bit miss is the bench's quadrature and how
  much a price is open. The b12_third figures in § 6 mix forms: its nested error comes from the form holding `lq1` (the inner pick in
  369 of 370 folds), the correction from the frozen form's prices. Like for like, the frozen form's own leave-one-kind-out error goes
  from +0.244 / +0.148 W to +0.197 / +0.103 W (aifoundry3 / card 1), ±0.12 W. b20_third's fold picked the frozen form, so its figures
  are like for like. **What replaces "nine points by default":** a convergence rule registered before any count beyond nine
  ([`recount-rule/RECOUNT-RULE.md`](recount-rule/RECOUNT-RULE.md), lab `b4444dd4`, committed 01:53:26 PST; its header's "about 02:00"
  is that commit). A tile's N-point average is converged when e(N) ≤ 0.10 W at M9's prices; N is tripled from 9, at most to 243; the
  calibration set's largest first N meeting the bound is N\*, and the recount of the 77 rows (45 counted tiles), E147's 70 tiles and
  pool 7's float tiles is sized by it. Its first step is C9.
- **C2: the heat claim.** The lane's result said "int8 kinds come 0.01-0.05 C closer"; that was never scored and is withdrawn. M7's
  carried law (g × S, as `predict_blind7.py` computes it) applied to M9's out-of-kind D, against `rows-m9.json`'s measured `dT_win`:
  on pool 6's 12 priority-1 int8 kinds, 0.126 / 0.129 °C rms (aifoundry3 / card 1) against M8's registered blind heat predictions
  (Q139(x)'s `predictions-blind6-<card>.json`) at 0.128 / 0.123 °C; on all 17 int8 kinds 0.190 / 0.141 against 0.184 / 0.134 °C.
  M9 is closer on 6 and 7 of the 12 tiles, 7 and 8 of the 17; the per-tile shift is 0.000-0.127 °C, below the die's whole-degree
  readout (aifoundry3's measured rises are 0.25, 0.75, 0.81, 1.00 and 1.04 °C). So: **the 4.5 s rise moves by 0.01-0.05 °C on int8
  kinds M9 predicts 0.1-0.4 W better, below the readout; pool 6's int8 4.5 s heat error is unchanged, 0.13 °C rms on aifoundry3 and
  card 1.**
- **C3: pool 6's int8 before → after, like for like.** The "blind before" figures are the frozen models' registered scores; M9's
  are out of kind, from a fit that holds pool 6's other int8 kinds and features named from pool 6's misses. On the same folds, M8's,
  M7's and M6's forms refitted read 0.159 / 0.177 / 0.189 W on aifoundry3 and 0.180 / 0.185 / 0.169 W on card 1, against M9's 0.118
  / 0.112 W (`nested-m9.json` › `families.int8.same_folds['pool 6 int8|a3, priority 1']` and `['pool 6 int8|c1, priority 1']`). The
  like-for-like gain over the best older form is 0.041 W (aifoundry3) and 0.057 W (card 1), not 0.08-0.21 W. Without the six
  named-miss tiles (7 int8 kinds) M9 is level with the refitted forms on aifoundry3 (0.118 against 0.115-0.117 W) and 0.04-0.05 W
  better on card 1 (0.111 against 0.150-0.162 W). The resolved gain over every committed int8 row, 0.251-0.261 → 0.177 W, stands.
- **C4: the mechanism, in words.** The lane's blog point said three sample points "miss a short early regime". The data say the
  opposite: on b20_third the bench's first point (n = 91,575, a sixth of the way in) falls in a short regime of high switching (3.53
  M nets against 1.97 and 1.95 M at its neighbours) and counts it as a third of the launch. On the other spiky tiles the high points
  fall mid-launch and late. "Where the accumulator's rounding position meets the flipping bit" is the registration's hypothesis, not
  a tested fact.
- **C5: the check before pool 7's predictions.** "git diff 1f244140 over M9's directory must be empty" fails as written, because
  `f4c93ae9` and these corrections change this README and add `recount-rule/`. The check is
  `git diff --name-only --diff-filter=MDRT 1f244140 -- docs/reports/data/2026-11-04-q140m-m9/ ':!docs/reports/data/2026-11-04-q140m-m9/README.md'`,
  which must print nothing (no frozen file modified, deleted, renamed or retyped since the freeze; files added later are allowed),
  with `m9.json`'s and `predict_blind7.py`'s sha256 as in § Files.
- **C6: Q140(l)'s part was committed.** Q140(l) committed it in `5b98bd5c` (01:04:31 PST), 7.5 minutes before M9's freeze commit;
  § 7, written 01:06-01:10, still called it a draft. On the committed part (`m9_a2.json` sha256 `cc6fbccc…`, `predict_m9_a2.py`
  `420b887e…`; the draft's predictor was `e82df306…`), `predict_blind7.py` on pool 6 for aifoundry2 calls Q140(l)'s `burst()` as
  primary on 50 of 50 tiles, and every one of the 7,450 tile fields equals the draft run's (the verifier found the same on 250 of
  them). Q140(x) still runs it on pool 7, with the part Q140(l) has committed last.
- **C7: cores.** The bench check's 4 jobs (00:46:29-01:05:50) overlapped `fit_m9.py` (00:52:25-00:56:46, about 1 core), the
  self-test, the plug-in tests and `summarize_m9.py`: about 5 busy processes for about 2 minutes in all, over section 24's 4 cores a
  lane. Desk only; no result is affected. The fix pass ran its bench at 3 jobs, so the lane stays within 4 cores.
- **C8: a rounding slip.** M8's int8 band k is 2.835 (`m8.json` › `families.int8.band_k`), so 2.84, not 2.83.
- **C9: the convergence rule's first step** (pending at this commit). The 14 calibration tiles above the bound at nine points are
  being counted at 27 (252 new points, 3 jobs, from 01:54:29 PST). The result is added in the next dated commit.
