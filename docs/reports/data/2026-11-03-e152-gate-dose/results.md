# E152: the float B-lane gate's price per flip as a dose ladder: results
Written by `tools/claims-v3/e152/score_e152.py` from `e152.json` (the registered reading). Kept passes: [15210, 15211, 15212, 15213, 15214, 15215]; set aside: []; reducer arm: dips removed (E82 A2).

## Rules

| rule | verdict | what |
|---|---|---|
| E152-R1 | **INCONCLUSIVE** | tau_w +0.1203; C8_star_w +1.203; C8_w +1.162; C8_ci95_w +0.1491; worst_abs_plus_h_w +0.1247; worst_abs_minus_h_w -0.03728; delta n=1: +0.030 +- 0.067, n=2: +0.015 +- 0.110, n=4: +0.025 +- 0.095; concave (low doses dearer per flip) |
| E152-R2 | **INCONCLUSIVE** | price_fJ +251.5; ci95_fJ +21.92; E127_price_fJ +262.9; ratio_to_E127 +0.9566 |
| E152-S1 | **PASS** |  |
| E152-S2 | **PASS** | E127_w +1.275; Q2 +1.168 +- 0.239 |

## Doses (W over gd0; 95% t over kept passes; price = C / (flips above gd0 x op rate))

| n | tiles | C measured | C predicted (E127's price) | price fJ/flip [95%] | delta from the line | delta / C(8) |
|---|---|---:|---:|---:|---:|---:|
| 1 | gd1a, gd1b | +0.175 +- 0.078 | +0.150 | 306 [170, 442] | +0.030 +- 0.067 | +0.026 [-0.031, +0.082] |
| 2 | gd2a, gd2b | +0.305 +- 0.138 | +0.301 | 267 [146, 388] | +0.015 +- 0.110 | +0.013 [-0.081, +0.106] |
| 4 | gd4a, gd4b | +0.606 +- 0.103 | +0.601 | 265 [220, 310] | +0.025 +- 0.095 | +0.022 [-0.061, +0.105] |
| 8 | gd8 | +1.162 +- 0.149 | +1.203 | 254 [221, 287] | - | - |

## Tiles (D over fp32's zeros, W, 95% over kept passes)

| tile | family | flips/op | D |
|---|---|---:|---:|
| `fp32.gd0` | ladder | 16 | 4.668 +- 0.061 |
| `fp32.gd1a` | ladder | 526 | 4.862 +- 0.133 |
| `fp32.gd1b` | ladder | 526 | 4.824 +- 0.087 |
| `fp32.gd1h` | ladder | 528 | 4.863 +- 0.114 |
| `fp32.gd2a` | ladder | 1036 | 5.000 +- 0.138 |
| `fp32.gd2b` | ladder | 1036 | 4.947 +- 0.097 |
| `fp32.gd4a` | ladder | 2056 | 5.294 +- 0.093 |
| `fp32.gd4b` | ladder | 2056 | 5.254 +- 0.107 |
| `fp32.gd8` | ladder | 4096 | 5.830 +- 0.111 |
| `fp32.q_chk` | bridge | 4096 | 5.899 +- 0.122 |
| `fp32.q_steady` | bridge | 0 | 4.731 +- 0.185 |

## Reported

```
{
 "mirror_pairs_w": {
  "n=1": {
   "mean": 0.03825673812132754,
   "n": 6,
   "ci95": 0.2161183478424774,
   "lo95": -0.17786160972114987,
   "hi95": 0.2543750859638049,
   "sd": 0.20590419146923195,
   "values": [
    -0.14232906578506999,
    0.004338774470845408,
    0.04216685387923391,
    -0.18753125381107338,
    0.12993462844774228,
    0.382960491526287
   ]
  },
  "n=2": {
   "mean": 0.05366495969516786,
   "n": 6,
   "ci95": 0.15114098563812636,
   "lo95": -0.09747602594295851,
   "hi95": 0.20480594533329421,
   "sd": 0.1439977806436134,
   "values": [
    -0.04703348782528849,
    0.17249704087778994,
    0.15321152114948688,
    0.033760054363405345,
    0.1841231211383878,
    -0.17456849153277432
   ]
  },
  "n=4": {
   "mean": 0.039492447739682156,
   "n": 6,
   "ci95": 0.1661665213455369,
   "lo95": -0.12667407360585473,
   "hi95": 0.20565896908521905,
   "sd": 0.15831318149741525,
   "values": [
    -0.034499999999997755,
    -0.09630329244031444,
    -0.050845290479689,
    -0.029312088279230153,
    0.1228385962273606,
    0.32507676140996367
   ]
  }
 },
 "gd1h_minus_gd1_w": {
  "mean": 0.020071012574854663,
  "n": 6,
  "ci95": 0.1235884638468807,
  "lo95": -0.10351745127202604,
  "hi95": 0.14365947642173538,
  "sd": 0.117747442442343,
  "values": [
   0.04128714461334937,
   -0.18419551263762202,
   0.14262959660513452,
   0.09563743503887778,
   0.0686712633990254,
   -0.043603851569637087
  ],
  "flip_difference_per_op": 2,
  "what": "gd1h: 512 flips above gd0 at 258 boundaries, four live everywhere; gd1a/gd1b: 510 at 512 boundaries, live count 3-5"
 },
 "gd0_minus_q_steady_w": {
  "mean": -0.06313505793986884,
  "n": 6,
  "ci95": 0.1773177704480166,
  "lo95": -0.24045282838788545,
  "hi95": 0.11418271250814777,
  "sd": 0.16893740176024846,
  "values": [
   -0.04400238950886859,
   -0.19081327707600693,
   -0.1766064923548356,
   0.1289307986059569,
   0.14654264705730924,
   -0.2428616343627681
  ],
  "E127_additive_prediction_w": 0.07227735277056256
 },
 "gd8_minus_q_chk_w": {
  "mean": -0.06955751756232213,
  "n": 6,
  "ci95": 0.11287464814082258,
  "lo95": -0.18243216570314472,
  "hi95": 0.04331713057850045,
  "sd": 0.10753998165741159,
  "values": [
   -0.23281896771916166,
   0.023801468873855924,
   0.004608618031326728,
   0.018711469696928162,
   -0.06642313592421445,
   -0.16522455833266747
  ],
  "prediction_w": 0.0
 },
 "line_C_on_n": {
  "slope_w_per_lane": 0.141675799032731,
  "intercept_w": 0.03080506887183676,
  "intercept_over_C8": 0.026516408229983194,
  "what": "least squares of the mean C(n) on n = 1, 2, 4, 8; a positive intercept is a share spent whenever any lane flips (no interval: reported only)"
 },
 "per_dose_against_predictions": {
  "1": {
   "measured_w": 0.1750494371216753,
   "ci95_w": 0.07782156269980393,
   "E127_price_pred_w": 0.15034316130877648,
   "within_10pct_of_pred": false,
   "M8_linear_bench_w": 0.13454736328125008,
   "M8_gtr_only_w": 0.08042070305235335,
   "M7_linear_bench_w": 0.13773486328125006
  },
  "2": {
   "measured_w": 0.3053531050790905,
   "ci95_w": 0.13807238476705508,
   "E127_price_pred_w": 0.30068632261755296,
   "within_10pct_of_pred": true,
   "M8_linear_bench_w": 0.26909472656250016,
   "M8_gtr_only_w": 0.1608414061047067,
   "M7_linear_bench_w": 0.27546972656250013
  },
  "4": {
   "measured_w": 0.6062186116601351,
   "ci95_w": 0.10325952589144068,
   "E127_price_pred_w": 0.6013726452351059,
   "within_10pct_of_pred": true,
   "M8_linear_bench_w": 0.5381894531250003,
   "M8_gtr_only_w": 0.3216828122094134,
   "M7_linear_bench_w": 0.5509394531250003
  },
  "8": {
   "measured_w": 1.1617361071174113,
   "ci95_w": 0.14909646372316138,
   "E127_price_pred_w": 1.2027452904702118,
   "within_10pct_of_pred": true,
   "M8_linear_bench_w": 1.0763789062500007,
   "M8_gtr_only_w": 0.6433656244188268,
   "M7_linear_bench_w": 1.1018789062500005
  }
 },
 "models_per_flip_fJ": {
  "M6_whole_at_E127_pair": {
   "fJ": 247.94910036152328,
   "ladder_over_it": 1.0144898957769395
  },
  "M7_gtr": {
   "fJ": 145.5317013572915,
   "ladder_over_it": 1.7284334247298674
  },
  "M7_whole_at_E127_pair": {
   "fJ": 240.8934611100624,
   "ladder_over_it": 1.0442037564017568
  },
  "M8_gtr": {
   "fJ": 140.6529983888487,
   "ladder_over_it": 1.7883860270673795
  },
  "M8_gtr_jackknife_se": {
   "fJ": 14.744486702290823,
   "ladder_over_it": 17.06006197860154
  },
  "M8_whole_at_E127_pair": {
   "fJ": 235.31863503483407,
   "ladder_over_it": 1.0689415096535473
  }
 }
}
```

## Beside the primary

| reading | E152-R1 | E152-R2 | E152-S1 | E152-S2 |
|---|---|---|---|---|
| dips_kept | INCONCLUSIVE | CARRIES | PASS | PASS |
| leak0.1994 | LINEAR | CARRIES | PASS | PASS |
| leak0.3803 | INCONCLUSIVE | INCONCLUSIVE | FAIL | PASS |
| leak0 | INCONCLUSIVE | INCONCLUSIVE | FAIL | PASS |
| gates_off | INCONCLUSIVE | INCONCLUSIVE | PASS | PASS |
