# E152's frozen numbers (written by make_predictions_e152.py)

E127's price per gate flip (whole, net of half its lane-position contrast): **262.9 fJ [246.5, 279.4]**; unnetted 277.7 [257.2, 298.1]. Op rate 1.121111e+09 /s. C8* = 1.2027 W; tau = 0.1203 W.

| dose n | flips above gd0 | C predicted, E127's price [95%] | M8 linear bench | M8 gtr only | M7 linear bench |
|---|---:|---:|---:|---:|---:|
| 1 | 510 | +0.1503 [+0.1409, +0.1598] | +0.1345 | +0.0804 | +0.1377 |
| 2 | 1020 | +0.3007 [+0.2818, +0.3195] | +0.2691 | +0.1608 | +0.2755 |
| 4 | 2040 | +0.6014 [+0.5637, +0.6391] | +0.5382 | +0.3217 | +0.5509 |
| 8 | 4080 | +1.2027 [+1.1273, +1.2781] | +1.0764 | +0.6434 | +1.1019 |

Models per flip (fJ): M8 whole at E127's pair 235.3, M8 gtr 140.7 (jackknife se 14.7), M7 whole 240.9, M7 gtr 145.5, M6 whole 247.9.

Bridge: E127 measured q_steady 4.718, q_chk 5.993 W (Q2 +1.275); M8 4.683 / 5.764 W.

gd0 - q_steady predicted +0.0723 W; gd8 - q_chk 0.

Planned 95% half-widths (sigma_tile 0.0481 W): 4 passes: delta_1_w 0.087, delta_2_w 0.081, delta_4_w 0.076, price_fJ 19.822; 5 passes: delta_1_w 0.068, delta_2_w 0.063, delta_4_w 0.060, price_fJ 15.467; 6 passes: delta_1_w 0.057, delta_2_w 0.053, delta_4_w 0.050, price_fJ 13.077
