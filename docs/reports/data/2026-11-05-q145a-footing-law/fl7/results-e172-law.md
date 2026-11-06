# E172 on aifoundry1c1: P8's rules at 600 MHz (score_p8_600.py)

Predictions `tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json` (1e55ac1ace1c); reduction `e172-law.json` (ec997f9a9c3f); kept passes [17210, 17211, 17212, 17213]; the session's float scale s = 0.98528 from ['fp32.randn', 'fp16.randn', 'fp16.anchor8_randn_a_8c7827', 'fp16.anchor8_randn_b_3a0fef', 'fp32.anchor8_randn_a_989b8a', 'fp32.anchor8_randn_b_833ac3'].

Sessions that must carry a C log: 5, all checked to the end: True; the stop-path test OK.

| rule | verdict | reading | line | n |
|---|---|---|---|---|
| P8-KC | PASS |  |  |  |
| P8-P1 | PASS | +0.1841 | [+0.0980, +0.3083] | 11 |
| P8-P2 | PASS | +0.1998 | [+0.0747, +0.2680] | 8 |
| P8-P3 | PASS | +0.2160 | [+0.1047, +0.2695] | 12 |
| P8-B1 | FAIL LOW | +0.0741 | [-0.0970, +0.0696] | 19 |
| P8-B2 | FAIL HIGH | -0.1669 | [-0.1150, +0.0957] | 12 |
| P8-C1 | PASS | 27 | >= 27 | 31 |
| P8-M1 | BETTER | -0.0807 | [-0.1371, -0.0240] | 31 |
| P8-M1f | BETTER | -0.1292 | [-0.2040, -0.0472] | 19 |
| P8-M1i | WORSE | +0.0093 | [+0.0014, +0.0191] | 12 |
| P8-A1 | NOT RESOLVED | -0.0607 | [-0.1217, +0.0077] | 19 |
| P8-KA | PASS |  |  | 2 |
| P8-H1 | PASS | +0.2722 | [+0.1793, +0.4314] | 11 |
| P8-H2 | PASS | +0.2874 | [+0.1626, +0.4547] | 8 |
| P8-H3 | PASS | +0.1040 | [+0.0905, +0.2118] | 12 |
| P8-H4 | PASS | 31 | >= 27 | 31 |
| P8-LG | BOTH | F_slope 7.952, F_level 5.150 |  | 12 |
| P8-G | FAIL |  |  |  |
| P8-HM | NOT SCORED |  |  |  |
