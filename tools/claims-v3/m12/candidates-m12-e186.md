# M12's and M10's forecasts for E186's merged candidate list (candidates_m12_e186.py)

A forecast for a registration to take, **not registered**. aifoundry3, s = 1, W over each format's zeros; rates int8 1.920619e+09 /s, fp32 1.117211e+09 /s, fp16 1.117241e+09 /s (candidates-m12.json's). M12 is post hoc (fitted on E182) and M10 frozen; these forecasts become blind for a run only if its registration commits them before its first datum. M12's 20 kinds and 14 trains are candidates-m12.json's frozen values (recomputed here: equal); the other 19 kinds and 8 trains are new here, from M12 as committed.

Registered train noise: half-width 0.0051 W at 32 units (se 0.00250 W). Measured (E182): se int8 0.00252, fp32 0.00298 W (fp16: fp32's). Separation = |M12 - M10| over the train's se combined with M12's; power = the chance the train's 95% interval excludes 0.

| train | first - second | M12, W (se) | M10, W | sep. registered | sep. measured | power if M12 (reg.) | from |
|---|---|---:|---:|---:|---:|---:|---|
| H16 (= R5) | K19 fp16.m12_a3c00_b3fff - K20 fp16.m12_a3fff_b3c00 | +0.2051 (0.0026) | +0.0000 | 57.0 | 52.0 | 1.00 | frozen |
| S23 | K13 fp32.m12_a1_b3f80ffff - K14 fp32.m12_a3f80ffff_b1 | +0.1640 (0.0021) | +0.0000 | 50.6 | 45.2 | 1.00 | frozen |
| S15 | K11 fp32.m12_a1_b3f8000ff - K12 fp32.m12_a3f8000ff_b1 | +0.0820 (0.0010) | +0.0000 | 30.3 | 26.0 | 1.00 | frozen |
| Q63-sign | K07 int8.m12_am1_bm63 - K05 int8.m12_a1_b63 | +0.0292 (0.0017) | -0.0471 | 25.2 | 25.1 | 1.00 | frozen |
| Q63-swap | K05 int8.m12_a1_b63 - K06 int8.m12_a63_b1 | +0.0073 (0.0016) | +0.0785 | 24.2 | 24.0 | 0.78 | frozen |
| R3 | K10 fp32.e182_a1_b3fffffff - K09 fp32.ones | +0.3801 (0.0198) | +0.0746 | 15.3 | 15.3 | 1.00 | new |
| B15-B7 | K11 fp32.m12_a1_b3f8000ff - K09 fp32.ones | +0.1261 (0.0069) | +0.0199 | 14.5 | 14.2 | 1.00 | frozen |
| B23-B15 | K13 fp32.m12_a1_b3f80ffff - K11 fp32.m12_a1_b3f8000ff | +0.1405 (0.0069) | +0.0343 | 14.5 | 14.2 | 1.00 | frozen |
| Q3-sign | K03 int8.m12_am1_bm3 - K01 int8.m12_a1_b3 | +0.1080 (0.0021) | +0.0785 | 9.0 | 9.0 | 1.00 | frozen |
| Q3-swap | K01 int8.m12_a1_b3 - K02 int8.m12_a3_b1 | +0.0015 (0.0003) | +0.0157 | 5.6 | 5.6 | 0.08 | frozen |
| R4 | K21 fp32.e182_a3fffffff_b1 - K09 fp32.ones | +0.1443 (0.0197) | +0.0746 | 3.5 | 3.5 | 1.00 | new |
| A15-A7 | K12 fp32.m12_a3f8000ff_b1 - K09 fp32.ones | +0.0441 (0.0069) | +0.0199 | 3.3 | 3.2 | 1.00 | frozen |
| A23-A15 | K14 fp32.m12_a3f80ffff_b1 - K12 fp32.m12_a3f8000ff_b1 | +0.0585 (0.0069) | +0.0343 | 3.3 | 3.2 | 1.00 | frozen |
| X8 | K05 int8.m12_a1_b63 - K01 int8.m12_a1_b3 | +0.1510 (0.0137) | +0.1553 | 0.3 | 0.3 | 1.00 | frozen |
| EA | K18 fp32.m12_a3ff80000_b1 - K16 fp32.m12_a3f80000f_b1 | -0.0023 (0.0000) | -0.0023 | 0.0 | 0.0 | 0.13 | frozen |
| EB | K17 fp32.m12_a1_b3ff80000 - K15 fp32.m12_a1_b3f80000f | -0.0023 (0.0000) | -0.0023 | 0.0 | 0.0 | 0.13 | frozen |
| R1 | K22 fp32.e186_a3fd55555_b3fffffff - K23 fp32.e186_a3ffff800_b3fffffff | +0.0093 (0.0000) | +0.0093 | 0.0 | 0.0 | 0.95 | new |
| R2 | K24 fp32.e186_a3fd55555_b1 - K25 fp32.e186_a3ffff800_b1 | +0.0191 (0.0000) | +0.0191 | 0.0 | 0.0 | 1.00 | new |
| R6 | K31 int8.e186_a1_b64 - K33 int8.e186_a2_b32 | +0.0000 (0.0000) | +0.0000 | 0.0 | 0.0 | 0.04 | new |
| R7 | K35 int8.e186_a4_b16 - K33 int8.e186_a2_b32 | +0.0000 (0.0000) | +0.0000 | 0.0 | 0.0 | 0.04 | new |
| R8 | K26 fp32.e186_a3f800001_b3fffffff - K27 fp32.e186_a3fc00000_b3fffffff | -0.0493 (0.0000) | -0.0493 | 0.0 | 0.0 | 1.00 | new |
| R9 | K26 fp32.e186_a3f800001_b3fffffff - K28 fp32.e186_a3f800004_b3fffffff | -0.0012 (0.0000) | -0.0012 | 0.0 | 0.0 | 0.06 | new |

| id | kind | A word | B word | pc A / B | M12, W (se) | M10, W | also | tile |
|---|---|---|---|---|---:|---:|---|---|
| K01 | int8.m12_a1_b3 | 0x01010101 | 0x03030303 | 4 / 8 | 1.7683 (0.0111) | 1.7929 | - | M12's tile (8b85b498) |
| K02 | int8.m12_a3_b1 | 0x03030303 | 0x01010101 | 8 / 4 | 1.7669 (0.0111) | 1.7772 | - | M12's tile (8b85b498) |
| K03 | int8.m12_am1_bm3 | 0xffffffff | 0xfdfdfdfd | 32 / 28 | 1.8764 (0.0112) | 1.8714 | - | M12's tile (8b85b498) |
| K04 | int8.m12_am3_bm1 | 0xfdfdfdfd | 0xffffffff | 28 / 32 | 1.8778 (0.0112) | 1.8871 | - | M12's tile (8b85b498) |
| K05 | int8.m12_a1_b63 | 0x01010101 | 0x3f3f3f3f | 4 / 24 | 1.9193 (0.0102) | 1.9482 | - | M12's tile (8b85b498) |
| K06 | int8.m12_a63_b1 | 0x3f3f3f3f | 0x01010101 | 24 / 4 | 1.9120 (0.0102) | 1.8697 | - | M12's tile (8b85b498) |
| K07 | int8.m12_am1_bm63 | 0xffffffff | 0xc1c1c1c1 | 32 / 12 | 1.9485 (0.0102) | 1.9011 | - | M12's tile (8b85b498) |
| K08 | int8.m12_am63_bm1 | 0xc1c1c1c1 | 0xffffffff | 12 / 32 | 1.9558 (0.0102) | 1.9796 | - | M12's tile (8b85b498) |
| K09 | fp32.ones | 0x3f800000 | 0x3f800000 | 7 / 7 | 8.3341 (0.0174) | 8.2314 | e186.fp32.one_one | committed before M12 |
| K10 | fp32.e182_a1_b3fffffff | 0x3f800000 | 0x3fffffff | 7 / 30 | 8.7142 (0.0222) | 8.3060 | e186.fp32.one_w | committed before M12 |
| K11 | fp32.m12_a1_b3f8000ff | 0x3f800000 | 0x3f8000ff | 7 / 15 | 8.4603 (0.0167) | 8.2513 | - | M12's tile (8b85b498) |
| K12 | fp32.m12_a3f8000ff_b1 | 0x3f8000ff | 0x3f800000 | 15 / 7 | 8.3782 (0.0167) | 8.2513 | - | M12's tile (8b85b498) |
| K13 | fp32.m12_a1_b3f80ffff | 0x3f800000 | 0x3f80ffff | 7 / 23 | 8.6008 (0.0188) | 8.2855 | - | M12's tile (8b85b498) |
| K14 | fp32.m12_a3f80ffff_b1 | 0x3f80ffff | 0x3f800000 | 23 / 7 | 8.4367 (0.0187) | 8.2855 | - | M12's tile (8b85b498) |
| K15 | fp32.m12_a1_b3f80000f | 0x3f800000 | 0x3f80000f | 7 / 11 | 8.3928 (0.0167) | 8.2369 | - | M12's tile (8b85b498) |
| K16 | fp32.m12_a3f80000f_b1 | 0x3f80000f | 0x3f800000 | 11 / 7 | 8.3518 (0.0167) | 8.2369 | - | M12's tile (8b85b498) |
| K17 | fp32.m12_a1_b3ff80000 | 0x3f800000 | 0x3ff80000 | 7 / 11 | 8.3905 (0.0167) | 8.2347 | - | M12's tile (8b85b498) |
| K18 | fp32.m12_a3ff80000_b1 | 0x3ff80000 | 0x3f800000 | 11 / 7 | 8.3495 (0.0167) | 8.2347 | - | M12's tile (8b85b498) |
| K19 | fp16.m12_a3c00_b3fff | 0x3c003c00 | 0x3fff3fff | 8 / 28 | 8.6620 (0.0216) | 8.2773 | e186.fp16.one_w | M12's tile (8b85b498) |
| K20 | fp16.m12_a3fff_b3c00 | 0x3fff3fff | 0x3c003c00 | 28 / 8 | 8.4569 (0.0216) | 8.2773 | e186.fp16.w_one | M12's tile (8b85b498) |
| K21 | fp32.e182_a3fffffff_b1 | 0x3fffffff | 0x3f800000 | 30 / 7 | 8.4784 (0.0221) | 8.3060 | e186.fp32.w_one | committed tile, its own label |
| K22 | fp32.e186_a3fd55555_b3fffffff | 0x3fd55555 | 0x3fffffff | 19 / 30 | 8.7153 (0.0299) | 8.2708 | e186.fp32.a13_w | new tile (this lane) |
| K23 | fp32.e186_a3ffff800_b3fffffff | 0x3ffff800 | 0x3fffffff | 19 / 30 | 8.7060 (0.0299) | 8.2615 | e186.fp32.a2_w | new tile (this lane) |
| K24 | fp32.e186_a3fd55555_b1 | 0x3fd55555 | 0x3f800000 | 19 / 7 | 8.4097 (0.0174) | 8.2707 | e186.fp32.a13_one | new tile (this lane) |
| K25 | fp32.e186_a3ffff800_b1 | 0x3ffff800 | 0x3f800000 | 19 / 7 | 8.3907 (0.0174) | 8.2516 | e186.fp32.a2_one | new tile (this lane) |
| K26 | fp32.e186_a3f800001_b3fffffff | 0x3f800001 | 0x3fffffff | 8 / 30 | 8.6793 (0.0228) | 8.2681 | e186.fp32.ab0_w | new tile (this lane) |
| K27 | fp32.e186_a3fc00000_b3fffffff | 0x3fc00000 | 0x3fffffff | 8 / 30 | 8.7286 (0.0228) | 8.3174 | e186.fp32.ab22_w | new tile (this lane) |
| K28 | fp32.e186_a3f800004_b3fffffff | 0x3f800004 | 0x3fffffff | 8 / 30 | 8.6805 (0.0228) | 8.2693 | e186.fp32.ab2_w | new tile (this lane) |
| K29 | fp32.e186_a1_b3f800001 | 0x3f800000 | 0x3f800001 | 7 / 8 | 8.3474 (0.0172) | 8.2314 | e186.fp32.one_bb0 | new tile (this lane) |
| K30 | fp32.e186_a1_b3fc00000 | 0x3f800000 | 0x3fc00000 | 7 / 8 | 8.3622 (0.0172) | 8.2462 | e186.fp32.one_bb22 | new tile (this lane) |
| K31 | int8.e186_a1_b64 | 0x01010101 | 0x40404040 | 4 / 4 | 1.7728 (0.0094) | 1.7226 | e186.int8.01_40 | new tile (this lane) |
| K32 | int8.e186_a64_b1 | 0x40404040 | 0x01010101 | 4 / 4 | 1.7728 (0.0094) | 1.7226 | e186.int8.40_01 | new tile (this lane) |
| K33 | int8.e186_a2_b32 | 0x02020202 | 0x20202020 | 4 / 4 | 1.7728 (0.0094) | 1.7226 | e186.int8.02_20 | new tile (this lane) |
| K34 | int8.e186_a32_b2 | 0x20202020 | 0x02020202 | 4 / 4 | 1.7728 (0.0094) | 1.7226 | e186.int8.20_02 | new tile (this lane) |
| K35 | int8.e186_a4_b16 | 0x04040404 | 0x10101010 | 4 / 4 | 1.7728 (0.0094) | 1.7226 | e186.int8.04_10 | new tile (this lane) |
| K36 | int8.e186_a16_b4 | 0x10101010 | 0x04040404 | 4 / 4 | 1.7728 (0.0094) | 1.7226 | e186.int8.10_04 | new tile (this lane) |
| K37 | int8.e178_v8 | 0x08080808 | 0x08080808 | 4 / 4 | 1.7222 (0.0138) | 1.7064 | e186.int8.08_08 | committed tile, its own label |
| K38 | int8.e186_am1_bm64 | 0xffffffff | 0xc0c0c0c0 | 32 / 8 | 1.9427 (0.0128) | 1.7707 | e186.int8.ff_c0 | new tile (this lane) |
| K39 | int8.e186_am64_bm1 | 0xc0c0c0c0 | 0xffffffff | 8 / 32 | 1.9515 (0.0128) | 1.8649 | e186.int8.c0_ff | new tile (this lane) |

Checks: {"bench": {"check_mismatch_all_zero": true, "fp16.m12_a3c00_b3fff": {"against": "M12", "mean_equal": true, "points_equal": true}, "fp16.zeros": {"against": "E178", "mean_equal": true, "points_equal": true}, "fp32.e182_a1_b3fffffff": {"against": "E182", "mean_equal": true, "points_equal": true}, "fp32.e182_a3fffffff_b1": {"against": "E182", "mean_equal": true, "points_equal": true}, "fp32.m12_a1_b3f8000ff": {"against": "M12", "mean_equal": true, "points_equal": true}, "fp32.ones": {"against": "E178", "mean_equal": true, "points_equal": true}, "fp32.zeros": {"against": "E178", "mean_equal": true, "points_equal": true}, "int8.e178_v8": {"against": "E178", "mean_equal": true, "points_equal": true}, "int8.m12_a1_b3": {"against": "M12", "mean_equal": true, "points_equal": true}, "int8.zeros": {"against": "E178", "mean_equal": true, "points_equal": true}}, "flip_model_reproduces_e182_all_24": {"equal": 24, "of": 24}, "frozen_m12_reproduced": {"kinds_equal": 20, "of_kinds": 20, "of_trains": 14, "trains_equal": 14}}
