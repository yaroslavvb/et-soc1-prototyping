# M12's candidate kinds and frozen forecasts (candidates_m12.py; REFIT.md section 5)

A candidate for the next one-number registration, **not registered**. aifoundry3, s = 1, W over each format's zeros; rates int8 1.920619e+09 /s, fp32 1.117211e+09 /s, fp16 1.117241e+09 /s. M12 is post hoc (fitted on E182); these forecasts become blind only if a registration commits them before its first datum.

Each train at E182's train noise: half-width 0.0051 W at 32 units (se 0.00250 W). Power = the chance the train's 95% interval excludes 0; separation = |M12 - M10| over the train's se combined with M12's.

| train | first - second | M12, W (se) | M10, W | power if M12 | power if M10 | separation (se) |
|---|---|---:|---:|---:|---:|---:|
| Q3-swap | int8.m12_a1_b3 - int8.m12_a3_b1 | +0.0015 (0.0003) | +0.0157 | 0.08 | 1.00 | 5.6 |
| Q3-sign | int8.m12_am1_bm3 - int8.m12_a1_b3 | +0.1080 (0.0021) | +0.0785 | 1.00 | 1.00 | 9.0 |
| Q63-swap | int8.m12_a1_b63 - int8.m12_a63_b1 | +0.0073 (0.0016) | +0.0785 | 0.78 | 1.00 | 24.2 |
| Q63-sign | int8.m12_am1_bm63 - int8.m12_a1_b63 | +0.0292 (0.0017) | -0.0471 | 1.00 | 1.00 | 25.2 |
| X8 | int8.m12_a1_b63 - int8.m12_a1_b3 | +0.1510 (0.0137) | +0.1553 | 1.00 | 1.00 | 0.3 |
| B23-B15 | fp32.m12_a1_b3f80ffff - fp32.m12_a1_b3f8000ff | +0.1405 (0.0069) | +0.0343 | 1.00 | 1.00 | 14.5 |
| B15-B7 | fp32.m12_a1_b3f8000ff - fp32.ones | +0.1261 (0.0069) | +0.0199 | 1.00 | 1.00 | 14.5 |
| A23-A15 | fp32.m12_a3f80ffff_b1 - fp32.m12_a3f8000ff_b1 | +0.0585 (0.0069) | +0.0343 | 1.00 | 1.00 | 3.3 |
| A15-A7 | fp32.m12_a3f8000ff_b1 - fp32.ones | +0.0441 (0.0069) | +0.0199 | 1.00 | 1.00 | 3.3 |
| S15 | fp32.m12_a1_b3f8000ff - fp32.m12_a3f8000ff_b1 | +0.0820 (0.0010) | +0.0000 | 1.00 | 0.04 | 30.3 |
| S23 | fp32.m12_a1_b3f80ffff - fp32.m12_a3f80ffff_b1 | +0.1640 (0.0021) | +0.0000 | 1.00 | 0.04 | 50.6 |
| H16 | fp16.m12_a3c00_b3fff - fp16.m12_a3fff_b3c00 | +0.2051 (0.0026) | +0.0000 | 1.00 | 0.04 | 57.0 |
| EB | fp32.m12_a1_b3ff80000 - fp32.m12_a1_b3f80000f | -0.0023 (0.0000) | -0.0023 | 0.13 | 0.13 | 0.0 |
| EA | fp32.m12_a3ff80000_b1 - fp32.m12_a3f80000f_b1 | -0.0023 (0.0000) | -0.0023 | 0.13 | 0.13 | 0.0 |

| kind | A word | B word | pc A / B | M12, W (se) | M10, W | new tile |
|---|---|---|---|---:|---:|---|
| int8.m12_a1_b3 | 0x01010101 | 0x03030303 | 4 / 8 | 1.7683 (0.0111) | 1.7929 | yes |
| int8.m12_a3_b1 | 0x03030303 | 0x01010101 | 8 / 4 | 1.7669 (0.0111) | 1.7772 | yes |
| int8.m12_am1_bm3 | 0xffffffff | 0xfdfdfdfd | 32 / 28 | 1.8764 (0.0112) | 1.8714 | yes |
| int8.m12_am3_bm1 | 0xfdfdfdfd | 0xffffffff | 28 / 32 | 1.8778 (0.0112) | 1.8871 | yes |
| int8.m12_a1_b63 | 0x01010101 | 0x3f3f3f3f | 4 / 24 | 1.9193 (0.0102) | 1.9482 | yes |
| int8.m12_a63_b1 | 0x3f3f3f3f | 0x01010101 | 24 / 4 | 1.9120 (0.0102) | 1.8697 | yes |
| int8.m12_am1_bm63 | 0xffffffff | 0xc1c1c1c1 | 32 / 12 | 1.9485 (0.0102) | 1.9011 | yes |
| int8.m12_am63_bm1 | 0xc1c1c1c1 | 0xffffffff | 12 / 32 | 1.9558 (0.0102) | 1.9796 | yes |
| fp32.ones | 0x3f800000 | 0x3f800000 | 7 / 7 | 8.3341 (0.0174) | 8.2314 | committed |
| fp32.e182_a1_b3fffffff | 0x3f800000 | 0x3fffffff | 7 / 30 | 8.7142 (0.0222) | 8.3060 | committed |
| fp32.m12_a1_b3f8000ff | 0x3f800000 | 0x3f8000ff | 7 / 15 | 8.4603 (0.0167) | 8.2513 | yes |
| fp32.m12_a3f8000ff_b1 | 0x3f8000ff | 0x3f800000 | 15 / 7 | 8.3782 (0.0167) | 8.2513 | yes |
| fp32.m12_a1_b3f80ffff | 0x3f800000 | 0x3f80ffff | 7 / 23 | 8.6008 (0.0188) | 8.2855 | yes |
| fp32.m12_a3f80ffff_b1 | 0x3f80ffff | 0x3f800000 | 23 / 7 | 8.4367 (0.0187) | 8.2855 | yes |
| fp32.m12_a1_b3f80000f | 0x3f800000 | 0x3f80000f | 7 / 11 | 8.3928 (0.0167) | 8.2369 | yes |
| fp32.m12_a3f80000f_b1 | 0x3f80000f | 0x3f800000 | 11 / 7 | 8.3518 (0.0167) | 8.2369 | yes |
| fp32.m12_a1_b3ff80000 | 0x3f800000 | 0x3ff80000 | 7 / 11 | 8.3905 (0.0167) | 8.2347 | yes |
| fp32.m12_a3ff80000_b1 | 0x3ff80000 | 0x3f800000 | 11 / 7 | 8.3495 (0.0167) | 8.2347 | yes |
| fp16.m12_a3c00_b3fff | 0x3c003c00 | 0x3fff3fff | 8 / 28 | 8.6620 (0.0216) | 8.2773 | yes |
| fp16.m12_a3fff_b3c00 | 0x3fff3fff | 0x3c003c00 | 28 / 8 | 8.4569 (0.0216) | 8.2773 | yes |

Checks: {"bench": {"check_mismatch_all_zero": true, "fp16.zeros": {"equal": true, "vpu_nets_map": 58382.0}, "fp32.ones": {"equal": true, "vpu_nets_map": 97693.33333333333}, "fp32.zeros": {"equal": true, "vpu_nets_map": 58258.0}, "int8.zeros": {"equal": true, "vpu_nets_map": 19068.0}}, "flip_model_reproduces_e182": {"fp32.e178_v4": true, "int8.e182_a1_b15": true, "int8.ones": true}}
