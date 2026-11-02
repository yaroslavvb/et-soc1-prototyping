# E125 — E113's A-side ladder on a second card (aifoundry1 card 1), scored

Passes run [12501, 12502, 12503, 12504, 12505, 12506, 12507, 12508], kept [12502, 12503, 12504, 12505, 12506, 12507, 12508] (E113's gates: E67's two and E70's D-a). Runs 208, failed a per-run gate 0. Card scale s (aifoundry3 over card 1, E82 fp32) 1.030017.

## Pass health

| pass | runs | failed | anchor_pi drift (W) | constant-operand spread (W) | op rate (G minion-ops/s, card) | set aside |
|---|---|---|---|---|---|---|
| 12501 | 26 | 0 | 0.328 | 0.328 | 1.1209 | anchor_pi drift +0.328 W |
| 12502 | 26 | 0 | 0.184 | 0.184 | 1.1209 | — |
| 12503 | 26 | 0 | 0.086 | 0.271 | 1.1210 | — |
| 12504 | 26 | 0 | 0.113 | 0.293 | 1.1209 | — |
| 12505 | 26 | 0 | 0.211 | 0.234 | 1.1210 | — |
| 12506 | 26 | 0 | 0.135 | 0.267 | 1.1208 | — |
| 12507 | 26 | 0 | 0.243 | 0.243 | 1.1210 | — |
| 12508 | 26 | 0 | 0.232 | 0.280 | 1.1211 | — |

## Z: E113's seven rules, scored by score_e113.py unchanged on card 1

| rule | E125 (card 1) | E113 (aifoundry3) | same |
|---|---|---|---|
| P1 | PASS | PASS | yes |
| P2 | REJECTED | REJECTED | yes |
| P3 | PASS | PASS | yes |
| P4 | which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k | which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k | yes |
| P5 | PASS | PASS | yes |
| P6 | PASS | PASS | yes |
| P7 | PASS | PASS | yes |

P4's one-parameter reading on card 1: the mirror law (the same mask's B rung, scaled) collapses the A side better than a curve in S_A.

**Z: REPLICATES**

## X: card 1 against E113 in the same frame (dips removed; a watt quantity at E113 / s)

| rule | quantity | E113 | prediction | card 1 | ± SE (n) | d | h | w | verdict |
|---|---|---|---|---|---|---|---|---|---|
| X-alq_h1 | dW(alq_h1) over aq_h0, W | 0.349 | 0.339 | 0.300 | 0.038 (7) | -0.039 | 0.134 | 0.60 | **PASS** |
| X-alq_h2 | dW(alq_h2) over aq_h0, W | 0.945 | 0.917 | 0.965 | 0.028 (7) | 0.047 | 0.087 | 0.60 | **PASS** |
| X-alq_h3 | dW(alq_h3) over aq_h0, W | 0.944 | 0.917 | 0.911 | 0.021 (7) | -0.006 | 0.074 | 0.60 | **PASS** |
| X-alq_h4 | dW(alq_h4) over aq_h0, W | 1.586 | 1.539 | 1.601 | 0.026 (7) | 0.061 | 0.084 | 0.60 | **PASS** |
| X-alq_h6 | dW(alq_h6) over aq_h0, W | 2.041 | 1.981 | 2.031 | 0.011 (7) | 0.049 | 0.054 | 0.60 | **PASS** |
| X-alq_h8 | dW(alq_h8) over aq_h0, W | 2.016 | 1.958 | 2.048 | 0.019 (7) | 0.090 | 0.077 | 0.60 | **PASS** |
| X-alq_h12 | dW(alq_h12) over aq_h0, W | 3.508 | 3.406 | 3.422 | 0.026 (7) | 0.016 | 0.107 | 0.60 | **PASS** |
| X-alq_h16 | dW(alq_h16) over aq_h0, W | 5.709 | 5.542 | 5.556 | 0.011 (7) | 0.014 | 0.165 | 0.60 | **PASS** |
| X-alq_h23 | dW(alq_h23) over aq_h0, W | 7.609 | 7.387 | 7.307 | 0.029 (7) | -0.080 | 0.098 | 1.00 | **PASS** |
| X-als_h2 | dW(als_h2) over aq_h0, W | 1.167 | 1.133 | 1.149 | 0.048 (7) | 0.016 | 0.132 | 0.60 | **PASS** |
| X-als_h3 | dW(als_h3) over aq_h0, W | 2.707 | 2.628 | 2.675 | 0.015 (7) | 0.047 | 0.076 | 0.60 | **PASS** |
| X-als_h4 | dW(als_h4) over aq_h0, W | 2.821 | 2.739 | 2.738 | 0.029 (7) | -0.001 | 0.094 | 0.60 | **PASS** |
| X-als_h6 | dW(als_h6) over aq_h0, W | 4.175 | 4.054 | 4.027 | 0.032 (7) | -0.027 | 0.116 | 0.60 | **PASS** |
| X-als_h8 | dW(als_h8) over aq_h0, W | 4.854 | 4.712 | 4.788 | 0.025 (7) | 0.076 | 0.130 | 0.60 | **PASS** |
| X-als_h12 | dW(als_h12) over aq_h0, W | 6.054 | 5.878 | 5.898 | 0.034 (7) | 0.020 | 0.151 | 0.60 | **PASS** |
| X-als_h16 | dW(als_h16) over aq_h0, W | 6.506 | 6.316 | 6.190 | 0.021 (7) | -0.126 | 0.111 | 0.60 | **PASS** |
| X-D1_A8 | dW(als_h8) - dW(alq_h8), paired per pass, W | 2.837 | 2.754 | 2.740 | 0.029 (7) | -0.014 | 0.133 | 0.60 | **PASS** |
| X-rho8-low | rho(8), low layout, A over B per designed bit | 1.230 | 1.230 | 1.278 | 0.019 (7) | 0.048 | 0.066 | 0.30 | **PASS** |
| X-rho8-spread | rho(8), spread layout, A over B per designed bit | 1.354 | 1.354 | 1.387 | 0.010 (7) | 0.033 | 0.036 | 0.30 | **PASS** |
| X-nrd | dW(nrd_a) / dW(nrd_b), paired per pass | 0.664 | 0.664 | 0.663 | 0.002 (7) | -0.001 | 0.013 | 0.05 | **PASS** |
| X-c | the mirror's c refitted per pass on E70's aifoundry3 B rungs (absorbs the card scale) | 0.681 | 0.661 | 0.662 | 0.002 (7) | 0.001 | 0.013 | 0.05 | **PASS** |

The A rungs together: 16 of 16 PASS, 0 FAIL: **PASS**.

Reported beside them, never a verdict: the same rules against E113's registered numbers (dips kept, six passes):

| rule | E113 registered | prediction | card 1 | d | h | verdict |
|---|---|---|---|---|---|---|
| X-alq_h1 | 0.314 | 0.305 | 0.300 | -0.005 | 0.173 | PASS |
| X-alq_h2 | 0.951 | 0.923 | 0.965 | 0.042 | 0.094 | PASS |
| X-alq_h3 | 0.950 | 0.922 | 0.911 | -0.011 | 0.082 | PASS |
| X-alq_h4 | 1.594 | 1.547 | 1.601 | 0.053 | 0.090 | PASS |
| X-alq_h6 | 2.045 | 1.985 | 2.031 | 0.046 | 0.063 | PASS |
| X-alq_h8 | 2.026 | 1.967 | 2.048 | 0.081 | 0.085 | PASS |
| X-alq_h12 | 3.504 | 3.402 | 3.422 | 0.020 | 0.124 | PASS |
| X-alq_h16 | 5.743 | 5.576 | 5.556 | -0.019 | 0.179 | PASS |
| X-alq_h23 | 7.598 | 7.377 | 7.307 | -0.070 | 0.105 | PASS |
| X-als_h2 | 1.177 | 1.143 | 1.149 | 0.007 | 0.137 | PASS |
| X-als_h3 | 2.641 | 2.564 | 2.675 | 0.111 | 0.240 | PASS |
| X-als_h4 | 2.827 | 2.745 | 2.738 | -0.007 | 0.102 | PASS |
| X-als_h6 | 3.941 | 3.827 | 4.027 | 0.201 | 0.429 | INCONCLUSIVE |
| X-als_h8 | 4.844 | 4.703 | 4.788 | 0.085 | 0.153 | PASS |
| X-als_h12 | 6.061 | 5.884 | 5.898 | 0.014 | 0.176 | PASS |
| X-als_h16 | 6.504 | 6.314 | 6.190 | -0.124 | 0.133 | PASS |
| X-D1_A8 | 2.818 | 2.735 | 2.740 | 0.005 | 0.145 | PASS |
| X-rho8-low | 1.366 | 1.366 | 1.278 | -0.088 | 0.278 | INCONCLUSIVE |
| X-rho8-spread | 1.350 | 1.350 | 1.387 | 0.037 | 0.039 | PASS |
| X-nrd | 0.664 | 0.664 | 0.663 | -0.001 | 0.016 | PASS |
| X-c | 0.678 | 0.658 | 0.662 | 0.004 | 0.017 | PASS |

Reported, never a verdict: this ladder's own scale, E113's A rungs over card 1's through the origin, 1.0314 (rms 0.058 W over 16 rungs), against E82's 1.0300.

## N1: the low layout's A/B ratio at k = 2 and 4 against k = 8, within card 1's passes

- r2 = dW(alq_h2) / dW(lq_h2): 0.960 ± 0.039 (n 7); E113 across sessions 1.019
- r4 = dW(alq_h4) / dW(lq_h4): 0.930 ± 0.021 (n 7); E113 across sessions 1.054
- r8 = dW(alq_h8) / dW(lq_h8): 0.639 ± 0.009 (n 7); E113 across sessions 0.621
- N1 = (r2 + r4)/2 − r8: 0.306 ± 0.023 (n 7), 95% [0.250, 0.362]; E113 across sessions 0.415; threshold 0.2

**N1: SMALL-K EXCESS**

## Arms (reported, never verdicts)

| arm | passes kept | P1-P7 | Z | X A rungs | N1 | D1_A(8) | c refit | rho8 low / spread | nrd ratio |
|---|---|---|---|---|---|---|---|---|---|
| all passes (E67's gates, no D-a) | [12501, 12502, 12503, 12504, 12505, 12506, 12507, 12508] | P1:PASS P2:REJECTED P3:PASS P4:which P5:PASS P6:PASS P7:PASS | REPLICATES | PASS (16/0) | SMALL-K EXCESS (0.284) | 2.710 ± 0.039 | 0.6612 | 1.267 / 1.369 | 0.660 |
| E113's own reduction (dips kept, leak auto) | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | P1:PASS P2:REJECTED P3:PASS P4:which P5:PASS P6:PASS P7:PASS | REPLICATES | PASS (16/0) | SMALL-K EXCESS (0.337) | 2.686 ± 0.066 | 0.6589 | 1.301 / 1.368 | 0.663 |
| dips kept, leak 0.2414 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | P1:PASS P2:REJECTED P3:PASS P4:which P5:PASS P6:PASS P7:PASS | REPLICATES | PASS (16/0) | SMALL-K EXCESS (0.334) | 2.669 ± 0.065 | 0.6568 | 1.305 / 1.367 | 0.663 |
| dips removed, leak auto | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | P1:PASS P2:REJECTED P3:PASS P4:which P5:PASS P6:PASS P7:PASS | REPLICATES | PASS (16/0) | SMALL-K EXCESS (0.308) | 2.757 ± 0.030 | 0.6638 | 1.274 / 1.388 | 0.663 |
| dips removed, leak 0.2 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | P1:PASS P2:REJECTED P3:PASS P4:which P5:PASS P6:PASS P7:PASS | REPLICATES | PASS (16/0) | SMALL-K EXCESS (0.310) | 2.771 ± 0.031 | 0.6655 | 1.270 / 1.389 | 0.663 |
| dips removed, leak 0.3 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | P1:PASS P2:REJECTED P3:PASS P4:which P5:PASS P6:PASS P7:PASS | REPLICATES | PASS (16/0) | SMALL-K EXCESS (0.300) | 2.696 ± 0.027 | 0.6562 | 1.290 / 1.385 | 0.663 |
| dips removed, leak 0.4 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | P1:PASS P2:REJECTED P3:PASS P4:which P5:PASS P6:PASS P7:PASS | REPLICATES | PASS (16/0) | SMALL-K EXCESS (0.290) | 2.622 ± 0.024 | 0.6470 | 1.311 / 1.380 | 0.663 |
