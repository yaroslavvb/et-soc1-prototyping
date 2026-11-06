# E178 on aifoundry3: one-number matrices, E178.md section 5's rules and A1's E178-S-int8 (score_e178.py)

Reduction `build/e178-out/2026-11-06-e178-one-number-aifoundry3/e178.json` (811f371e6412); kept passes [17810, 17811, 17812, 17813]; the session's float scale s = 1.00590 from ['fp32.randn', 'fp16.randn'].

Sessions that must carry a C log: 5, all checked to the end: True; the stop-path test OK.

Each kept pass ran plan-e178.json's order: {'17810': True, '17811': True, '17812': True, '17813': True}.

The smoke's C, reported (fp32.e178_uf must read +0 throughout; int8.e178_v85 and int8.e178_v127 wrap): anchor_pi 6/6; fp16.e178_v5 6/6; fp16.zeros 6/6; fp32.e178_uf 6/6; fp32.randn 6/6; fp32.zeros 6/6; int8.e178_v127 6/6; int8.e178_v85 6/6; int8.full 6/6; int8.zeros 6/6.

| rule | verdict | SIZE (P / F) | reading | interval or line | n |
|---|---|---|---|---|---|
| E178-C | PASS |  | 2190 of 2190 launches PASS; left out [] |  |  |
| E178-H-int8 | POSITIVE | FAIL HIGH / FAIL HIGH | +0.0532 W (dP +0.1857, dF +0.1871) | [+0.0217, +0.0848] | 4 |
| E178-H-fp32 | NOT RESOLVED | PASS / PASS | +0.0523 W (dP +0.0087, dF +0.0303) | [-0.0459, +0.1505] | 4 |
| E178-H-fp16 | NOT RESOLVED | PASS / PASS | +0.0558 W (dP +0.0173, dF +0.0389) | [-0.0038, +0.1154] | 4 |
| E178-U | NOT RESOLVED | PASS / FAIL HIGH | +0.0452 W (dP +0.0743, dF +0.1303) | [-0.0314, +0.1217] | 4 |
| E178-S-int8 | NOT RESOLVED | FAIL HIGH / FAIL HIGH | +0.0582 W (dP +0.3555, dF +0.3580) | [-0.0770, +0.1935] | 4 |
| E178-R-int8 | PASS |  | rho +0.643 | >= 0.560 | 13 |
| E178-W-int8 | FAIL HIGH |  | 2.78 fJ/flip (P 7.48) | [1.51, 4.05] | 13 |
| E178-E-int8 | PASS |  | spread 0.0669 W | <= 0.2460 | 4 |
| E178-E-fp32 | PASS |  | spread 0.1048 W | <= 0.1958 | 6 |
| E178-E-fp16 | PASS |  | spread 0.1749 W | <= 0.1811 | 6 |

Beside, never a verdict: 127 - neg_ones +0.0271 W [-0.0828, +0.1371] (dP +0.2420).

The owner's sentence (A1-1): not measured: the four rules do not read together (A1-1).

SIZE: FAIL HIGH = the forecast above the measured interval (the model prices more than the card reads); FAIL LOW = below.

Arms (reported beside, never the verdict):

- session_own: E178-H-int8 NOT RESOLVED, E178-H-fp32 NOT RESOLVED, E178-H-fp16 NOT RESOLVED, E178-U NOT RESOLVED, E178-S-int8 NOT RESOLVED, E178-R-int8 PASS, E178-W-int8 FAIL HIGH, E178-E-int8 PASS, E178-E-fp32 PASS, E178-E-fp16 PASS
- auto_dips_removed: E178-H-int8 POSITIVE, E178-H-fp32 NOT RESOLVED, E178-H-fp16 NOT RESOLVED, E178-U NOT RESOLVED, E178-S-int8 NOT RESOLVED, E178-R-int8 PASS, E178-W-int8 FAIL HIGH, E178-E-int8 PASS, E178-E-fp32 PASS, E178-E-fp16 PASS
- kfrozen_dips_kept: E178-H-int8 NOT SCORED, E178-H-fp32 NOT SCORED, E178-H-fp16 NOT SCORED, E178-U NOT SCORED, E178-S-int8 NOT SCORED, E178-R-int8 NOT SCORED, E178-W-int8 NOT SCORED, E178-E-int8 NOT SCORED, E178-E-fp32 NOT SCORED, E178-E-fp16 NOT SCORED
- leak0.1994: E178-H-int8 POSITIVE, E178-H-fp32 NOT RESOLVED, E178-H-fp16 NOT RESOLVED, E178-U NOT RESOLVED, E178-S-int8 NOT RESOLVED, E178-R-int8 PASS, E178-W-int8 FAIL HIGH, E178-E-int8 PASS, E178-E-fp32 PASS, E178-E-fp16 PASS
- leak0.3803: E178-H-int8 NOT RESOLVED, E178-H-fp32 NOT RESOLVED, E178-H-fp16 NOT RESOLVED, E178-U NOT RESOLVED, E178-S-int8 NOT RESOLVED, E178-R-int8 FAIL, E178-W-int8 FAIL HIGH, E178-E-int8 PASS, E178-E-fp32 PASS, E178-E-fp16 PASS
- leak0: E178-H-int8 POSITIVE, E178-H-fp32 NOT RESOLVED, E178-H-fp16 NOT RESOLVED, E178-U NOT RESOLVED, E178-S-int8 NOT RESOLVED, E178-R-int8 PASS, E178-W-int8 FAIL HIGH, E178-E-int8 PASS, E178-E-fp32 PASS, E178-E-fp16 PASS
- gates_off: E178-H-int8 POSITIVE, E178-H-fp32 NOT RESOLVED, E178-H-fp16 NOT RESOLVED, E178-U NOT RESOLVED, E178-S-int8 NOT RESOLVED, E178-R-int8 PASS, E178-W-int8 FAIL HIGH, E178-E-int8 PASS, E178-E-fp32 PASS, E178-E-fp16 PASS
