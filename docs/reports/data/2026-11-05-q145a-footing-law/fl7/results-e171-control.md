# E171 on aifoundry3: P8's rules at 600 MHz (score_p8_600.py)

Predictions `tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry3.json` (d68ff9f1e057); reduction `docs/reports/data/2026-11-05-e171-blind8-aifoundry3/e171.json` (da1be39fa199); kept passes [17110, 17111, 17112, 17113]; the session's float scale s = 1.00615 from ['fp32.randn', 'fp16.randn', 'fp16.anchor8_randn_a_8c7827', 'fp16.anchor8_randn_b_3a0fef', 'fp32.anchor8_randn_a_989b8a', 'fp32.anchor8_randn_b_833ac3'].

Sessions that must carry a C log: 5, all checked to the end: True; the stop-path test OK.

| rule | verdict | reading | line | n |
|---|---|---|---|---|
| P8-KC | PASS |  |  |  |
| P8-P1 | PASS | +0.1759 | [+0.0976, +0.2998] | 11 |
| P8-P2 | FAIL | +0.2381 | [+0.0626, +0.2374] | 8 |
| P8-P3 | PASS | +0.1314 | [+0.1007, +0.2485] | 12 |
| P8-B1 | FAIL LOW | +0.0924 | [-0.0970, +0.0638] | 19 |
| P8-B2 | PASS | +0.0354 | [-0.1050, +0.0889] | 12 |
| P8-C1 | PASS | 30 | >= 27 | 31 |
| P8-M1 | BETTER | -0.0650 | [-0.1215, -0.0120] | 31 |
| P8-M1f | BETTER | -0.0907 | [-0.1645, -0.0199] | 19 |
| P8-M1i | NOT RESOLVED | +0.0019 | [-0.0175, +0.0184] | 12 |
| P8-A1 | BETTER | -0.0620 | [-0.0926, -0.0325] | 19 |
| P8-KA | PASS |  |  | 2 |
| P8-H1 | PASS | +0.1871 | [+0.1037, +0.2479] | 11 |
| P8-H2 | PASS | +0.1930 | [+0.0831, +0.2248] | 8 |
| P8-H3 | PASS | +0.1226 | [+0.1158, +0.2615] | 12 |
| P8-H4 | PASS | 28 | >= 27 | 31 |
| P8-LG | NOT SEPARATED | F_slope 1.026, F_level 0.081 |  | 12 |
| P8-G | FAIL |  |  |  |
| P8-HM | NOT SCORED |  |  |  |
