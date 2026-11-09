# E186 scored (score_e186.py)

plan read: FULL; the session's float scale s: 1.008733231104833 (read from the float trains' anchors (reduce_e186.py anchors))

| rule | verdict | reading |
|---|---|---|
| E186-C | PASS | kinds not all PASS [], trains [] |
| E186-H16 | F16-SAME | +0.2031 [+0.1978, +0.2084] W; SIGN POSITIVE; SIZE M12 PASS, M10 FAIL LOW, SCALED FAIL LOW |
| E186-S23 | NEITHER | +0.1545 [+0.1491, +0.1599] W; SIGN POSITIVE; SIZE M12 FAIL HIGH, M10 FAIL LOW |
| E186-Q63SIGN | NEITHER | +0.0364 [+0.0308, +0.0421] W; SIGN POSITIVE; SIZE M12 FAIL LOW, M10 FAIL LOW |
| E186-Q63SWAP | M12 | +0.0107 [+0.0054, +0.0160] W; SIGN POSITIVE; SIZE M12 PASS, M10 FAIL HIGH |
| E186-B15B7 | M12 | +0.1398 [+0.1355, +0.1441] W; SIGN POSITIVE; SIZE M12 PASS, M10 FAIL LOW |
| E186-B23B15 | M12 | +0.1368 [+0.1316, +0.1421] W; SIGN POSITIVE; SIZE M12 PASS, M10 FAIL LOW |
| E186-Q3SIGN | M12 | +0.1083 [+0.1027, +0.1140] W; SIGN POSITIVE; SIZE M12 PASS, M10 FAIL LOW |
| E186-Q3SWAP | NEITHER | +0.0086 [+0.0035, +0.0138] W; SIGN POSITIVE; SIZE M12 FAIL LOW, M10 FAIL HIGH |
| E186-A15A7 | NEITHER | +0.0630 [+0.0577, +0.0683] W; SIGN POSITIVE; SIZE M12 FAIL LOW, M10 FAIL LOW |
| E186-A23A15 | M12 | +0.0591 [+0.0534, +0.0648] W; SIGN POSITIVE; SIZE M12 PASS, M10 FAIL LOW |
| E186-SPLIT3 | A+B | beta_A +0.00544 [+0.00325, +0.00763] (POSITIVE; SIZE M12 FAIL HIGH), beta_B +0.01406 [+0.01102, +0.01709] (POSITIVE; SIZE M12 FAIL LOW) W a bit a byte |
| E186-SPLIT63 | A+B | beta_A +0.01071 [+0.00912, +0.01230] (POSITIVE; SIZE M12 FAIL LOW), beta_B +0.01285 [+0.01057, +0.01513] (POSITIVE; SIZE M12 FAIL LOW) W a bit a byte |
| E186-GB | POSITIVE | +0.01387 [+0.01345, +0.01429] W a held bit; SIZE M12 PASS, M10 FAIL LOW |
| E186-GA | POSITIVE | +0.00421 [+0.00373, +0.00469] W a held bit; SIZE M12 PASS, M10 FAIL LOW |
| E186-S23R | DIFFERS LOW | S23 x 23/16 +0.2221 [+0.2144, +0.2298] W against T5 [+0.2299, +0.2419] |
| E186-M | NEITHER | M12 Q 32.48 (INCONSISTENT), M10 Q 10229.80 (INCONSISTENT) over 9 trains |
| E186-TR-N | AS FORECAST | largest ratio 1.035 |
| E186-LV | NOT SCORED | 0 kept kinds passes (FULL runs none: the trains read no level) |

## The pairing check (score_e186_v2.py, KIT.md.dated-note-1.md)

E186-PAIR: PASS; 10 train block(s) read; not paired: none

| train | block | launch records | paired | not paired, by check | C log |
|---|---|---|---|---|---|
| H16 | p18610 | 1064 | 1064 | 0 | c-log.jsonl |
| S23 | p18611 | 1064 | 1064 | 0 | c-log.jsonl |
| Q63-sign | p18612 | 896 | 896 | 0 | c-log.jsonl |
| Q63-swap | p18613 | 896 | 896 | 0 | c-log.jsonl |
| B15-B7 | p18614 | 1064 | 1064 | 0 | c-log.jsonl |
| B23-B15 | p18615 | 1064 | 1064 | 0 | c-log.jsonl |
| Q3-sign | p18616 | 896 | 896 | 0 | c-log.jsonl |
| Q3-swap | p18617 | 896 | 896 | 0 | c-log.jsonl |
| A15-A7 | p18618 | 1064 | 1064 | 0 | c-log.jsonl |
| A23-A15 | p18619 | 1064 | 1064 | 0 | c-log.jsonl |
