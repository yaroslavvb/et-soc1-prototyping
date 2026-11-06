# E172 on aifoundry1c1: P8's rules at 600 MHz (score_p8_600.py)

Predictions `tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json` (1e55ac1ace1c); reduction `docs/reports/data/2026-11-05-e172-blind8-card1/e172.json` (ed95819b4c6f); kept passes [17210, 17211, 17212]; the session's float scale s = 1.00798 from ['fp32.randn', 'fp16.randn', 'fp16.anchor8_randn_a_8c7827', 'fp16.anchor8_randn_b_3a0fef', 'fp32.anchor8_randn_a_989b8a', 'fp32.anchor8_randn_b_833ac3'].

Sessions that must carry a C log: 5, all checked to the end: True; the stop-path test OK.

| rule | verdict | reading | line | n |
|---|---|---|---|---|
| P8-KC | PASS |  |  |  |
| P8-P1 | PASS | +0.2087 | [+0.0980, +0.3083] | 11 |
| P8-P2 | PASS | +0.2237 | [+0.0747, +0.2680] | 8 |
| P8-P3 | PASS | +0.1245 | [+0.1047, +0.2695] | 12 |
| P8-B1 | FAIL LOW | +0.1054 | [-0.0970, +0.0696] | 19 |
| P8-B2 | PASS | +0.0047 | [-0.1150, +0.0957] | 12 |
| P8-C1 | PASS | 29 | >= 27 | 31 |
| P8-M1 | BETTER | -0.0804 | [-0.1336, -0.0337] | 31 |
| P8-M1f | BETTER | -0.1116 | [-0.1788, -0.0528] | 19 |
| P8-M1i | NOT RESOLVED | +0.0086 | [-0.0036, +0.0192] | 12 |
| P8-A1 | BETTER | -0.0952 | [-0.1352, -0.0504] | 19 |
| P8-KA | PASS |  |  | 2 |
| P8-H1 | PASS | +0.2139 | [+0.1793, +0.4314] | 11 |
| P8-H2 | PASS | +0.2499 | [+0.1626, +0.4547] | 8 |
| P8-H3 | PASS | +0.1014 | [+0.0905, +0.2118] | 12 |
| P8-H4 | PASS | 31 | >= 27 | 31 |
| P8-LG | NOT SEPARATED | F_slope 0.541, F_level 1.024 |  | 12 |
| P8-G | FAIL |  |  |  |
| P8-HM | NOT SCORED |  |  |  |
