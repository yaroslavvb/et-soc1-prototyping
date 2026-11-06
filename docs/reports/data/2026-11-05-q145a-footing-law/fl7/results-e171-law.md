# E171 on aifoundry3: P8's rules at 600 MHz (score_p8_600.py)

Predictions `tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry3.json` (d68ff9f1e057); reduction `e171-law.json` (d7d933b0013b); kept passes [17110, 17111, 17112]; the session's float scale s = 0.98577 from ['fp32.randn', 'fp16.randn', 'fp16.anchor8_randn_a_8c7827', 'fp16.anchor8_randn_b_3a0fef', 'fp32.anchor8_randn_a_989b8a', 'fp32.anchor8_randn_b_833ac3'].

Sessions that must carry a C log: 5, all checked to the end: True; the stop-path test OK.

| rule | verdict | reading | line | n |
|---|---|---|---|---|
| P8-KC | PASS |  |  |  |
| P8-P1 | PASS | +0.1631 | [+0.0976, +0.2998] | 11 |
| P8-P2 | PASS | +0.2148 | [+0.0626, +0.2374] | 8 |
| P8-P3 | PASS | +0.1500 | [+0.1007, +0.2485] | 12 |
| P8-B1 | FAIL LOW | +0.0778 | [-0.0970, +0.0638] | 19 |
| P8-B2 | PASS | -0.0927 | [-0.1050, +0.0889] | 12 |
| P8-C1 | PASS | 30 | >= 27 | 31 |
| P8-M1 | BETTER | -0.0970 | [-0.1552, -0.0371] | 31 |
| P8-M1f | BETTER | -0.1385 | [-0.2153, -0.0562] | 19 |
| P8-M1i | NOT RESOLVED | +0.0032 | [-0.0102, +0.0139] | 12 |
| P8-A1 | BETTER | -0.0748 | [-0.1442, -0.0014] | 19 |
| P8-KA | PASS |  |  | 2 |
| P8-H1 | PASS | +0.1742 | [+0.1037, +0.2479] | 11 |
| P8-H2 | PASS | +0.2080 | [+0.0831, +0.2248] | 8 |
| P8-H3 | PASS | +0.1216 | [+0.1158, +0.2615] | 12 |
| P8-H4 | PASS | 27 | >= 27 | 31 |
| P8-LG | GAIN | F_slope 16.860, F_level 4.192 |  | 12 |
| P8-G | FAIL |  |  |  |
| P8-HM | NOT SCORED |  |  |  |
