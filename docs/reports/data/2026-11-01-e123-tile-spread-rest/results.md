# E123 results (score_e123.py; registration tools/claims-v3/e123/E123.md)

Passes kept: [12310, 12311]; single-pass fallback: False; leak {'mode': '0.1994', 'k_w_per_c': 0.1994, 'n_runs': -1}

## Rules of number: the primary (gate-share adjusted, class-pooled)

| rule | class | k | committed D, W | kind's mean D ± 95%, W | offset ± 95%, W | R2 | kind's S, W | E94-form R2 | plain tau, W |
|---|---|---|---|---|---|---|---|---|---|
| fp32.nn_like | G | 7 | 13.069 | 13.202 ± 0.139 | -0.133 ± 0.143 | **NO CORRECTION** | 15.194 | UNRESOLVED | 0.807 |
| fp16.sparse50 | G | 5 | 13.497 | 13.230 ± 0.146 | 0.267 ± 0.151 | **NO CORRECTION** | 15.188 | UNRESOLVED | 0.549 |
| fp16.wsparse50 | G | 4 | 7.039 | 7.263 ± 0.153 | -0.224 ± 0.158 | **NO CORRECTION** | 9.254 | UNRESOLVED | 0.863 |
| fp32.smallint | LF | 3 | 14.076 | 13.949 ± 0.130 | 0.127 ± 0.170 | **NO CORRECTION** | 15.846 | UNRESOLVED | 0.386 |
| fp32.sparse90 | LF | 3 | 0.545 | 0.680 ± 0.117 | -0.135 ± 0.161 | **NO CORRECTION** | 2.608 | NO CORRECTION | 0.177 |
| fp16.sparse90 | LF | 3 | 1.391 | 1.345 ± 0.118 | 0.046 ± 0.162 | **NO CORRECTION** | 3.270 | NO CORRECTION | 0.133 |
| fp16.wsparse90 | LF | 3 | 0.689 | 0.672 ± 0.117 | 0.017 ± 0.161 | **NO CORRECTION** | 2.688 | NO CORRECTION | 0.043 |
| fp16.smallint | LF | 2 | 17.039 | 16.853 ± 0.144 | 0.186 ± 0.185 | **NO CORRECTION** | 18.872 | — | 0.000 |
| int8.wsparse50 | LI | 3 | 3.207 | 3.258 ± 0.111 | -0.051 ± 0.162 | **NO CORRECTION** | 5.852 | NO CORRECTION | 0.000 |
| int8.sparse90 | LI | 3 | 1.177 | 1.302 ± 0.110 | -0.125 ± 0.161 | **UNRESOLVED** | 3.834 | UNRESOLVED | 0.134 |
| int8.wsparse90 | LI | 2 | 0.582 | 0.445 ± 0.133 | 0.137 ± 0.183 | **UNRESOLVED** | 2.971 | — | 0.171 |
| int8.ternary | LI | 2 | 5.151 | 5.118 ± 0.133 | 0.033 ± 0.183 | **NO CORRECTION** | 7.654 | — | 0.000 |

## Every rule

| rule | verdict | detail |
|---|---|---|
| E123-R5 | **PASS** | {"slope_left_w_per_unit": 0.5808255415170318, "se": 1.1674686220254167, "df": 12, "ci95": [-1.9630885858763512, 3.124739668910415], "n_draws": 16, "what": "the slope of the adjusted draws on their gate share, rule intercepts; 0 if the frozen slope is right"} |
| E123-R2e94:fp32.nn_like | **UNRESOLVED** | {} |
| E123-R1e94:fp32.nn_like | **PASS** | {} |
| E123-R2:fp32.nn_like | **NO CORRECTION** | {"offset_w": -0.1328154110795623, "halfwidth_w": 0.1432627932649086, "kind_mean_D_w": 13.202175411079564, "band_w": 0.5, "label": null} |
| E123-R2e94:fp16.sparse50 | **UNRESOLVED** | {} |
| E123-R1e94:fp16.sparse50 | **PASS** | {} |
| E123-R2:fp16.sparse50 | **NO CORRECTION** | {"offset_w": 0.2668525131886028, "halfwidth_w": 0.150730021339093, "kind_mean_D_w": 13.229668782036146, "band_w": 0.5, "label": null} |
| E123-R2e94:fp16.wsparse50 | **UNRESOLVED** | {} |
| E123-R1e94:fp16.wsparse50 | **PASS** | {} |
| E123-R2:fp16.wsparse50 | **NO CORRECTION** | {"offset_w": -0.22422011731514413, "halfwidth_w": 0.15797725585087408, "kind_mean_D_w": 7.26349439195942, "band_w": 0.5, "label": null} |
| E123-R2e94:fp32.smallint | **UNRESOLVED** | {} |
| E123-R1e94:fp32.smallint | **PASS** | {} |
| E123-R2:fp32.smallint | **NO CORRECTION** | {"offset_w": 0.1265778967423845, "halfwidth_w": 0.17039986355321926, "kind_mean_D_w": 13.948987103257615, "band_w": 0.5, "label": null} |
| E123-R2e94:fp32.sparse90 | **NO CORRECTION** | {} |
| E123-R1e94:fp32.sparse90 | **PASS** | {} |
| E123-R2:fp32.sparse90 | **NO CORRECTION** | {"offset_w": -0.13473300100642227, "halfwidth_w": 0.1611345954703837, "kind_mean_D_w": 0.6798125401485997, "band_w": 0.5, "label": null} |
| E123-R2e94:fp16.sparse90 | **NO CORRECTION** | {} |
| E123-R1e94:fp16.sparse90 | **PASS** | {} |
| E123-R2:fp16.sparse90 | **NO CORRECTION** | {"offset_w": 0.04600229385237253, "halfwidth_w": 0.16191692356097562, "kind_mean_D_w": 1.3450016777449985, "band_w": 0.5, "label": null} |
| E123-R2e94:fp16.wsparse90 | **NO CORRECTION** | {} |
| E123-R1e94:fp16.wsparse90 | **PASS** | {} |
| E123-R2:fp16.wsparse90 | **NO CORRECTION** | {"offset_w": 0.017319486004842122, "halfwidth_w": 0.1611026788325072, "kind_mean_D_w": 0.6719084351116927, "band_w": 0.5, "label": null} |
| E123-R2:fp16.smallint | **NO CORRECTION** | {"offset_w": 0.1855742033900576, "halfwidth_w": 0.18490749705297577, "kind_mean_D_w": 16.852926102498376, "band_w": 0.5, "label": null} |
| E123-R2e94:int8.wsparse50 | **NO CORRECTION** | {} |
| E123-R1e94:int8.wsparse50 | **INCONCLUSIVE** | {} |
| E123-R2:int8.wsparse50 | **NO CORRECTION** | {"offset_w": -0.0506233352242309, "halfwidth_w": 0.16180037765971098, "kind_mean_D_w": 3.257632361681694, "band_w": 0.25, "label": null} |
| E123-R2e94:int8.sparse90 | **UNRESOLVED** | {} |
| E123-R1e94:int8.sparse90 | **PASS** | {} |
| E123-R2:int8.sparse90 | **UNRESOLVED** | {"offset_w": -0.12491110310759779, "halfwidth_w": 0.16115158002617022, "kind_mean_D_w": 1.3021829775814007, "band_w": 0.25, "label": null} |
| E123-R2:int8.wsparse90 | **UNRESOLVED** | {"offset_w": 0.1368216445842046, "halfwidth_w": 0.18250731209685758, "kind_mean_D_w": 0.4450583554157936, "band_w": 0.25, "label": null} |
| E123-R2:int8.ternary | **NO CORRECTION** | {"offset_w": 0.033289606159967455, "halfwidth_w": 0.18254182238535188, "kind_mean_D_w": 5.117992507298038, "band_w": 0.25, "label": null} |
| E123-R3:fp32.nn_like | **PASS** | {"expected_sd_w": 0.8746, "tau_w": 0.8069439939174097, "tau_ci95_w": [0.5196010999065565, 1.7776915166043061], "q130n_expected_sd_w": 0.7951} |
| E123-R3:fp16.sparse50 | **PASS** | {"expected_sd_w": 0.6627, "tau_w": 0.5485990548872022, "tau_ci95_w": [0.3282918980447358, 1.5773543227903828], "q130n_expected_sd_w": 0.641} |
| E123-R3:fp16.wsparse50 | **PASS** | {"expected_sd_w": 0.6932, "tau_w": 0.8627386340378023, "tau_ci95_w": [0.48867048991779954, 3.216940527029299], "q130n_expected_sd_w": 0.5081} |
| E123-R4:G | **REPORTED** | {"df": 13, "s_w": 0.7519086139535245, "noise_of_one_tile_mean_w": 0.021209209789802123, "tau_w": 0.7516094285981266, "tau_ci95_w": [0.5446863349421915, 1.2111709875973125]} |
| E123-R4:LF | **PASS** | {"df": 9, "s_w": 0.21589936711932706, "noise_of_one_tile_mean_w": 0.04894508842690742, "tau_w": 0.21027818489184313, "tau_ci95_w": [0.14020547249456178, 0.3910972892534158], "x_w": 0.5} |
| E123-R4:LI | **PASS** | {"df": 6, "s_w": 0.1115932639746823, "noise_of_one_tile_mean_w": 0.0510652650484152, "tau_w": 0.09922396520023896, "tau_ci95_w": [0.050629848718583295, 0.24037136910411708], "x_w": 0.25} |
| E123-R6 | **PASS** | {"rms_w": 0.21231995088073077, "rms_no_move_w": 0.6902101305594931, "n": 16, "by_class_rms_w": {"G": 0.21231995088073077, "LF": 0.07792231194718076, "LI": 0.07904112382505739}, "by_class_no_move_w": {"G": 0.6902101305594931, "LF": 0.21240183846015087, "LI": 0.14782021338140852}} |
| E123-R7:gate_law | **PASS** | {"rms_w": 0.1061079604425791, "n": 11} |
| E123-R7:q130n | **PASS** | {"rms_w": 0.1249497462409249, "n": 11} |
| E123-R8 | **PASS** | {"rms_w": 0.07036735052450172, "rms_no_move_w": 0.7508373087982085, "n": 5} |
| E123-S1 | **PASS** | {"outside": []} |

## Verdicts at the arms (moves only)

- **dips_kept**: E123-R2:fp16.sparse50: NO CORRECTION -> UNRESOLVED; E123-R2:fp16.wsparse50: NO CORRECTION -> UNRESOLVED; E123-R2:fp32.smallint: NO CORRECTION -> UNRESOLVED; E123-R2:fp16.smallint: NO CORRECTION -> UNRESOLVED; E123-R2:int8.wsparse50: NO CORRECTION -> UNRESOLVED; E123-R2:int8.ternary: NO CORRECTION -> UNRESOLVED; E123-R4:LF: PASS -> INCONCLUSIVE
- **gates_off**: no verdict moves
- **auto**: E123-R1e94:int8.wsparse50: INCONCLUSIVE -> PASS
- **leak0.2414**: no verdict moves
- **leak0.3803**: E123-R1e94:int8.wsparse50: INCONCLUSIVE -> PASS; E123-R2:int8.wsparse50: NO CORRECTION -> UNRESOLVED; E123-R2:int8.ternary: NO CORRECTION -> UNRESOLVED; E123-S1: PASS -> FAIL
- **leak0.545**: E123-R2:fp32.smallint: NO CORRECTION -> UNRESOLVED; E123-R2e94:fp16.sparse90: NO CORRECTION -> UNRESOLVED; E123-R1e94:fp16.sparse90: PASS -> INCONCLUSIVE; E123-R2e94:int8.wsparse50: NO CORRECTION -> UNRESOLVED; E123-R1e94:int8.wsparse50: INCONCLUSIVE -> PASS; E123-R2:int8.wsparse50: NO CORRECTION -> UNRESOLVED; E123-R1e94:int8.sparse90: PASS -> INCONCLUSIVE; E123-R2:int8.ternary: NO CORRECTION -> UNRESOLVED; E123-R4:LI: PASS -> INCONCLUSIVE; E123-S1: PASS -> FAIL
- **leak0**: E123-R2e94:fp32.sparse90: NO CORRECTION -> UNRESOLVED; E123-R2e94:int8.wsparse50: NO CORRECTION -> UNRESOLVED; E123-R1e94:int8.wsparse50: INCONCLUSIVE -> PASS; E123-R2:int8.wsparse90: UNRESOLVED -> NO CORRECTION; E123-R4:LI: PASS -> INCONCLUSIVE; E123-S1: PASS -> FAIL

Tally (primary rules, secondary excluded): {'PASS': 11, 'NO CORRECTION': 10, 'UNRESOLVED': 2, 'REPORTED': 1}
