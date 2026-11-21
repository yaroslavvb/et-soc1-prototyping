# decl-e223: the lab's BLIND test of its frozen matmul models on E223, DECLARED before any E223 datum

*Lane decl-e223 (round Q239), aifoundry2's desk; written Sat 21 Nov 2026 02:19:24 PST, Pacific time. Desk only: no card, no ssh, no simulator, no commit. Interpreter: /usr/bin/python3 3.12.3, -I -B, single-threaded, every numerical step one slot job. Inputs: a git archive of GitHub main c661275c (= LAB HEAD), the orchestrator's copy of E223's kit (SRC-SHA256SUMS.txt 627b622e...), Q238's frozen mask-posimb (FROZEN.txt 0cd8e9da...). Labels: registered (this file), measured, desk, post hoc, held out, blind; REPORTED = printed beside, deciding nothing.*

**The experiment.** E223 (#16, 01:25:49 PST Sat 21 Nov 2026): the model session's seventh matmul sweep, 1121-mmsweep7, of E136's rgm136 unchanged (kernel ELF aace138c...): 839 runs over 299 gemmL arms of the lab's kinds and an anchor in nine sessions (aifoundry1 card 1 S1-S3 at 600 MHz, card 0 S1-S3 low power, aifoundry2 card 0 S1-S3 under the sixth sweep's live stops 85 W x3 / 80 C), no designed tiles; a blind test of its frozen v3.7, the core-group placement law first with its held-out placements in 15 sets, then the held-walk edge, the L3 region, the wide-B wait and the masked energy terms; its sealed forecast eb5478f6... is not read here. The kit is the sixth sweep's (E221's) with its name changed: the same cards, bands, gates, reducer and run forms (reduce_mms.py, run_mms.py and mms_common.py equal E221's kit copy but for the sweep's name: checked by diff with the name masked, so the data JSON's fields are E221's).

**The state at this declaration** (W/out/orch/e223-releases.txt):
- #16 2026-11-21 01:25:49 PST: PROPOSAL: the NDA box's seventh matmul sweep (1121-mmsweep7): E136's rgm136 unchanged over 299 gemmL arms and an anchor in nine sessions (839 runs, about 517 planned card-minutes, no designed tiles); a blind test of its frozen v3.7 (frozen Fri 19:12 PST), the core-group placement law first (512 held-out placements in 15 sets), then the held-walk edge, the L3 region, the wide-B wait and the masked energy terms; its forecast sealed before any datum: sha256 eb5478f65e509cf28e1c46bb55da5a30cc757beab54ba9db7cebeee6465af4ee; aifoundry1 card 1 S1-S3 at 600 MHz (planned at or under 66.6 W, stop 75 W), card 0 S1-S3 low power (at or under 52 W, live stop 65 W); aifoundry2 card 0 S1-S3 (at or under 66.6 W, no time role) under the sixth sweep's live stops (85 W x3 / 80 C); the kit in ~/claude/work/ee-1121-mmsweep7/src/ on each box, built and dry-run before any claim.
- #16.1.1 2026-11-21 01:55:59 PST: PUSH aifoundry2: E223's kit pushed to aifoundry2 at 01:55 PST (53 files to ~/claude/work/ee-1121-mmsweep7/src/, built 01:55, kernel ELF aace138caf80... as pinned, host sha256 8cc73c4f706ba986...), dry runs next; aifoundry1's push waits for the owner's network approval; no session sends a card command before the lab's E223 freeze post.
- (no claim file for E223 at this declaration; aifoundry1's push waits for the owner's network approval (#16.1.1): its six sessions may not run tonight; a card with no session is NO DATA)

## 0. MM1's domain, first

- **EVERY E223 case is IN MM1's domain: all 299 arms and the anchor are rgm136's cooperative gemmL<MB>x<NB>x<KB> loop (no gemmLnc, no block, stream or TenB arm; arms.json and every schedule checked) at the lab's kinds (zeros, ones, random; fp32, fp16, int8) on the three cards MM1-v3.2 has per-card constants for; NO case is OUT OF DOMAIN, so none is left unforecast.**
- Evidence: probe p01: every one of the 695 cases has a form (finite wall and mean cycles, op time; energy FORECAST) in MM1-v3.2 695, MM1-v3.1 695, MM1-v3 695, MM1-v2 695 at the nominal footing (work/step1/domain-probe.json, status only); the models' code: mm1_v32.py, mm1_v31.py, mm1_v3.py and MM1-v2 take any gemmL<MB>x<NB>x<KB> token and shire mask on rgm136 (the masked map); the terms' scopes by their own code (posimb_rows / posimb_mask.in_scope: mask not 0xffffffff, kernel rgm136, arm gemmL; L3S's domain_key: the full mask; AF4: gemmLnc tokens only).

| class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | MM1-v3.3 | posimb, posimb-mask scope | L3S domain |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ANCHOR | the anchor (4x8x8 int8 random, whole chip): first, between blocks and last in each session | 3 | 70 | 0 / 3 | yes | yes | yes | yes | yes (= MM1-v3.2) | 0 | 3 |
| PLACE | the core-group placements (family 'place'): 11 gemmL shapes (MB 1-4, NB 1-16, KB 1-24; fp32, fp16, int8) placed on shire groups at subset masks of 1 to 28 shires (PL with its subfamilies PL1, P34, G10, G14, FLOOR, ND1/ND2/ND34, D1/D2/D4, CNT/CNT3, TYPE; KW, G111/K111, I8, MIX/COL/ROW, FEED); the proposal's placement law, its held-out placements in the HO sets | 421 | 457 | 421 / 0 | yes | yes | yes | yes | yes (= MM1-v3.2) | 421 | 0 |
| EDGE | the held-walk edge (EDG, EDG2, EDGR, HO-EDGE): 20 gemmL shapes at MB 2-16, NB 6-10, KB 1-2 (fp32, int8), whole chip | 59 | 59 | 0 / 59 | yes | yes | yes | yes | yes (= MM1-v3.2) | 0 | 59 |
| L3 | the L3 region (L3R, L3R2, HO-L3, e220-4; the proposal's words): 13 narrow-N gemmL shapes at MB 2-8, NB 1-2, KB 1-6, whole chip | 39 | 39 | 0 / 39 | yes | yes | yes | yes | yes (= MM1-v3.2) | 0 | 39 |
| WIDE | the wide-B wait (WID, WID2, HO-WIDE): 18 wide-N deep-K gemmL shapes at MB 1-6, NB 9-24, KB 16-32 (fp32), whole chip | 51 | 51 | 0 / 51 | yes | yes | yes | yes | yes (= MM1-v3.2) | 0 | 51 |
| GATE | the masked energy cases outside PLACE (GATE, GAT, HO-GATE, medium-2, TW, HO-TW): fp32 zeros of 1x12x8 and 2x6x10 at the whole chip and at gate masks of 5, 8 and 16 shires | 30 | 33 | 24 / 6 | yes | yes | yes | yes | yes (= MM1-v3.2) | 24 | 6 |
| KIND | the kinds (KND, KND2, N3, N4, HO-KIND, CW, v37-18): five gemmL shapes (1x12x8, 1x1x1, 2x1x16, 2x2x3, 2x6x10) at zeros, ones and random, at the whole chip and at 26 shires | 57 | 59 | 39 / 18 | yes | yes | yes | yes | yes (= MM1-v3.2) | 39 | 18 |
| CELL111 | the 1x1x1 cells outside PLACE (G111, G11, v37-6, HO-111): gemmL 1x1x1 fp32 zeros at single shires | 17 | 17 | 17 / 0 | yes | yes | yes | yes | yes (= MM1-v3.2) | 17 | 0 |
| SHAPE | the shape probes (SHAPE, SH2, syn): gemmL 1x10x10 and 2x8x8 fp32 zeros at the whole chip and at single shires | 18 | 18 | 12 / 6 | yes | yes | yes | yes | yes (= MM1-v3.2) | 12 | 6 |

**The held-out sets** (the proposal's 15 HO-<x> families; an arm may sit in two; every set is in the domain):

| set | cases | runs | by card | classes | subset / full |
|---|---|---|---|---|---|
| HO-111 | 14 | 14 | {"aifoundry1 card 0": 4, "aifoundry1 card 1": 4, "aifoundry2 card 0": 6} | {"CELL111": 14} | 14 / 0 |
| HO-Ccard | 3 | 3 | {"aifoundry2 card 0": 3} | {"PLACE": 3} | 3 / 0 |
| HO-EDGE | 40 | 40 | {"aifoundry1 card 0": 13, "aifoundry1 card 1": 14, "aifoundry2 card 0": 13} | {"EDGE": 40} | 0 / 40 |
| HO-G | 70 | 70 | {"aifoundry1 card 0": 26, "aifoundry1 card 1": 22, "aifoundry2 card 0": 22} | {"PLACE": 70} | 70 / 0 |
| HO-GATE | 36 | 36 | {"aifoundry1 card 0": 12, "aifoundry1 card 1": 12, "aifoundry2 card 0": 12} | {"PLACE": 24, "GATE": 12} | 36 / 0 |
| HO-KIND | 51 | 51 | {"aifoundry1 card 0": 16, "aifoundry1 card 1": 18, "aifoundry2 card 0": 17} | {"EDGE": 6, "WIDE": 6, "KIND": 39} | 39 / 12 |
| HO-L3 | 21 | 21 | {"aifoundry1 card 0": 7, "aifoundry1 card 1": 7, "aifoundry2 card 0": 7} | {"L3": 21} | 0 / 21 |
| HO-N | 24 | 24 | {"aifoundry1 card 0": 8, "aifoundry1 card 1": 8, "aifoundry2 card 0": 8} | {"PLACE": 24} | 24 / 0 |
| HO-P1 | 121 | 145 | {"aifoundry1 card 0": 43, "aifoundry1 card 1": 39, "aifoundry2 card 0": 39} | {"PLACE": 121} | 121 / 0 |
| HO-P1card | 2 | 2 | {"aifoundry2 card 0": 2} | {"PLACE": 2} | 2 / 0 |
| HO-P2 | 18 | 18 | {"aifoundry1 card 0": 6, "aifoundry1 card 1": 6, "aifoundry2 card 0": 6} | {"PLACE": 18} | 18 / 0 |
| HO-P34 | 21 | 21 | {"aifoundry1 card 0": 7, "aifoundry1 card 1": 7, "aifoundry2 card 0": 7} | {"PLACE": 21} | 21 / 0 |
| HO-S | 48 | 48 | {"aifoundry1 card 0": 16, "aifoundry1 card 1": 16, "aifoundry2 card 0": 16} | {"PLACE": 36, "SHAPE": 12} | 48 / 0 |
| HO-TW | 12 | 12 | {"aifoundry1 card 0": 4, "aifoundry1 card 1": 4, "aifoundry2 card 0": 4} | {"GATE": 12} | 12 / 0 |
| HO-WIDE | 41 | 41 | {"aifoundry1 card 0": 13, "aifoundry1 card 1": 14, "aifoundry2 card 0": 14} | {"WIDE": 41} | 0 / 41 |

- **MASKE221:** blind-e221's MASK class by its own definition (decl-e221's precedence ANCHOR, L2I8 (family L2I8), CELL1 (families CLK, PLS), then MASK = family PL): E223's arms.json carries no L2I8, CLK or PLS code, so MASKE221 = every non-anchor arm of family PL: 353 cases, 389 runs, all at subset masks (E223's PL arms have no whole-chip member; a whole-chip twin of a PL case is the case of the same card, token, format and kind at 0xffffffff wherever E223 runs one).
- **GATESET:** the masked energy cases: every arm of family GATE (93 cases), in whichever class (most are PLACE).
- **NOT APPLICABLE in effect:** AF4 (the gemmLnc energy term) acts at no E223 case (no gemmLnc arm): MM1-v3.3 = 'MM1-v3.2 + AF4' equals MM1-v3.2 on every case (checked to 1e-12 by its frozen per-row form), and so do 'MM1-v3.2 + posimb + AF4' = 'MM1-v3.2 + posimb', 'MM1-v3.2 + AF4 + L3S' = 'MM1-v3.2 + L3S', 'MM1-v3.2 + all three' = 'MM1-v3.2 + posimb + L3S' and 'MM1-v3.2 + AF4 + posimb-mask' = 'MM1-v3.2 + posimb-mask'; each is forecast and printed all the same (by its construction), and the MM1-v3.3 vs MM1-v3.2 sign test reads NO DATA (no untied case) by construction, declared here before any datum.
- **Domain limits, REPORTED apart:** IN the domain but beyond the fits, REPORTED apart (they enter the rules like every case): the core-group placements at shire masks no fit holds (most of E223's 50 masks), the 26-shire mask, MB up to 16, NB up to 24 and KB up to 32; aifoundry2 card 0 and aifoundry1 card 0 under their governors (the clock read from each run's start-of-run records; the nominal footing at 800 MHz); configuration twins (section c) split.
- **OUT OF DOMAIN: none** (0 cases): there is no E223 arm class without a frozen MM1 form, so every case is forecast and scored.

## a. The runs
- **listed**: 803 runs ({'anchor': 70, 'arm': 733}) of the schedules' 839 (36 nulls and each session's smoke left out), 695 cases (a case = card, arm, format, kind, mask); by session {'a1c0-S1': 90, 'a1c0-S2': 90, 'a1c0-S3': 86, 'a1c1-S1': 92, 'a1c1-S2': 90, 'a1c1-S3': 87, 'a2c0-S1': 93, 'a2c0-S2': 90, 'a2c0-S3': 85}; by card {'aifoundry1 card 0': 266, 'aifoundry1 card 1': 269, 'aifoundry2 card 0': 268} runs, {'aifoundry1 card 0': 231, 'aifoundry1 card 1': 232, 'aifoundry2 card 0': 232} cases; by format {'fp16': 6, 'fp32': 706, 'int8': 91} runs; by kind {'ones': 109, 'random': 169, 'zeros': 525} runs; by class {'ANCHOR': 70, 'PLACE': 457, 'GATE': 33, 'EDGE': 59, 'WIDE': 51, 'L3': 39, 'KIND': 59, 'SHAPE': 18, 'CELL111': 17} runs, {'ANCHOR': 3, 'PLACE': 421, 'GATE': 30, 'EDGE': 59, 'WIDE': 51, 'L3': 39, 'KIND': 57, 'SHAPE': 18, 'CELL111': 17} cases; subset masks 513 cases over 50 masks (150 subset configurations), the whole chip 182 cases; the 15 held-out sets 492 cases / 516 runs (an arm may sit in two sets)
- **ids**: E223|<card>-<S>|<i:03d>-<arm id>: the kit's own run key (run_mms.py), from src/sched/<card>-<S>.json and src/arms.json of the orchestrator's copy (SRC-SHA256SUMS.txt 627b622e..., 53/53; the kit's own SRC-SHA256SUMS 52/52); the list is work/step1/runs-listed.json
- **fit_inclusion**: NO E223 point can be in any fit: E223 has no datum for this lane. Checked all the same: no E223 token in any model's inputs or loaders (MM1-v3.2 13 files, MM1-v3.1 28, MM1-v3 115, MM1-v2 86, Q234 posimb 23, gemmlnc-af4 20, l3s 25, Q238 posimb-mask 29: 0 hits) and no E223 id in any landed point record (MM1-v3.2 to E215, MM1-v3.1 to E213, MM1-v3 to E212, MM1-v2 to E208; posimb and L3S to E219, AF4 to E218, posimb-mask to E224)
- **tiles**: E223 designs no tile: arms.json's tiles table is empty and its 9 tile files (6 named by arms) equal the lab's kinds (tools/claims-v3/kinds/tiles) byte for byte, each a committed blob; so no switch count is made (step 4 NOT NEEDED)

## b. The quantities
- **per_card**: aifoundry1 card 1 at 600 MHz (not governed); aifoundry1 card 0 low power under its governor (main band 800 MHz); aifoundry2 card 0 under its governor (main band 800 MHz), the kit's live stops
- **T1_wall**: cycles an op, the slowest minion: forecast cycles_per_op_wall / cyc_op_max - 1
- **T2_counter_mean**: the counter's mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1
- **T3_seconds**: seconds a pass (one GEMM): 64 MB NB KB x T_forecast(us) x 1e-6 / t_pass_s - 1 (the host's ops a minion a pass); at the measured clock T3 equals T1 identically (the reducer's T_op_us = wall / ops): both printed
- **E1_W_and_J_over_idle_given_t**: W over idle at the measured op time, W = A + B / t_meas (the predictor's W_affine at the run's conditions) against the primary view's dP_w; its relative error is also J over idle given t's (J = W t_meas on both sides); relative when the case's mean MM1-v3.2 W given t and its mean measured dP_w are both 3 W or more; else a WATTS case scored in watts (E215's form; the watts set fixed by MM1-v3.2 and the measurement, the same for every model)
- **E2_J_over_idle_t_forecast**: (W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc at the model's own op time; at a watts case W_fc - dP_w
- **E3_J_at_rest_given_t**: (P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run's rest, measured, given)
- **E4_J_at_rest_t_forecast**: (P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1
- **split**: per card; per format and kind; per class (ANCHOR, PLACE, EDGE, L3, WIDE, GATE, KIND, CELL111, SHAPE), THE PLACEMENTS FIRST; per held-out set (HO-111, HO-Ccard, HO-EDGE, HO-G, HO-GATE, HO-KIND, HO-L3, HO-N, HO-P1, HO-P1card, HO-P2, HO-P34, HO-S, HO-TW, HO-WIDE); MASKE221 (blind-e221's MASK by its own definition); GATESET (the masked energy cases); FULL and SUB; configuration twins apart (section c)

## The models
- **MM1-v3.2**: THE REGISTERED BASELINE (tools/matmul/mm1/v3.2, landed 4e386f75; SHA256SUMS d52c9cce, 58/58): mm1_v32.Model(out/mm1_v32_params.json).predict_many([{card, arm, fmt, kind, mask, f, kernel rgm136, V, t0_c}]); the pass rule's model (section f)
- **MM1-v3.3**: = 'MM1-v3.2 + AF4', E222's registered selection (SEL, read by E222's frozen scorer at 00:57 PST Sat; committed with E222's scores c661275c): by its frozen per-row form (tools/claims-v3/e224/desk/models_e224.py af4_rows, = gemmlnc-af4/scripts/s03_freeze.py's) on MM1-v3.2's forecast at the same conditions; AF4 acts at gemmLnc tokens only, so at every E223 case it is MM1-v3.2 exactly
- **MM1-v3.1**: tools/matmul/mm1/v3.1 (landed 2c971828; SHA256SUMS f6840d2d, 64/64): mm1_v31.Model(out/mm1_v31_params.json).predict_many
- **MM1-v3**: tools/matmul/mm1/v3 (landed b1493082; SHA256SUMS c24efc14, 170/170): mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel='rgm136', V=, t0_c=)
- **MM1-v2**: tools/matmul/mm1/v2 (SHA256SUMS eafb6558, 114/114) through MM1-v3's unread_v2_e212.call (blind-e221's caller): card 1 V None (the 0.517 V footing), the governed cards the measured volts (V_mv); energy for random, zeros and ones (E223's only kinds); no die term
- **MM1-v3.2 + posimb (REPORTED)**: Q234's layout2 candidate (landed tools/matmul/mm1/v3.3-cands/posimb/; FROZEN-e220 81d04c97), by E224's frozen caller models_e224.posimb_rows (h01_freeze.py's per-row form) at its all-data a_hop = 0.1333333152086018, a_lag = 0.4367172478570998: in scope at the subset masks of rgm136 gemmL (513 cases), MM1-v3.2 to the last bit elsewhere; energy MM1-v3.2's affine at the composed op time
- **MM1-v3.2 + L3S (REPORTED)**: Q234's l3-edge candidate (tools/matmul/mm1/v3.3-cands/l3s/), term_l3s.ModelL3S(MM1-v3.2's params, lam = 0.6908933059768666, the landed cache + E224's extra records + the frozen set model's records for E223's new full-mask shapes) by E224's caller: in its domain at the full mask (182 cases), MM1-v3.2 at the subset masks
- **compositions (REPORTED)**: by E222's and E224's construction, no refit (models_e224.compose and compose_sub, E222's SEL restricted to the joining terms): 'MM1-v3.2 + posimb + AF4', 'MM1-v3.2 + posimb + L3S', 'MM1-v3.2 + AF4 + L3S', 'MM1-v3.2 + all three'; E224's own checks run at every case (compose_sub at all three = compose; each single term = its own candidate)
- **MM1-v3.2 + posimb-mask (REPORTED)**: Q238's mask-posimb (track P), KEPT by its declared rule, FROZEN 01:48:34 PST (FROZEN.txt 0cd8e9da..., posted #1.30.1.2.1.1.1.1.1 at 01:49:15, before any E223 datum), its land folder copied unchanged to work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask/ (46/46 files equal its FROZEN.txt lines): posimb_mask.Model().predict_many_with_af4 at its constants {"a_hop": 0.4117348711927109, "a_lag": 0.33491919909092666, "a_al": -0.1046901474717002} on MM1-v3.2 4e386f75 unchanged; in scope at the subset masks of rgm136 gemmL; 'MM1-v3.2 + AF4 + posimb-mask' beside (its own construction)
- **Q238_read**: W/out/orch/q238-frozen-posts.txt read at Sat 21 Nov 2026 02:19:24 PST (copied to work/q238-frozen-posts-at-declaration.txt): mask-posimb: posted [('#1.30.1.2.1.1.1.1.1', '2026-11-21 01:49:15 PST', '0cd8e9da')], FROZEN.txt on disk 0cd8e9da, INCLUDED; mask-mesh: posted [('#1.30.1.2.1.1.1.1.1.1', '2026-11-21 02:03:18 PST', '3d4942fa')], FROZEN.txt on disk 487188c7, NOT INCLUDED; mask-ceiling: posted [], FROZEN.txt on disk none, NOT INCLUDED. mask-mesh's posted line (FROZEN 02:02:13) does not match its FROZEN.txt on disk (rewritten 02:03:37), so it is not in this freeze; mask-ceiling has no FROZEN.txt. A Q238 candidate that qualifies only after this read is not in this freeze: it can be scored on E223 only by a dated amendment hashed before E223's first datum, else as UNREAD
- **maker_checks**: before any output, step 2 re-makes: every row of E224's frozen forecast-e224.csv at the lab's kinds (both arms, every clock) by E224's own Models.forecast at this work copy, and every row of posimb-mask's frozen forecasts-compose-e222-e224.csv at the lab's kinds (probe p02: 2,431 and 294 rows, worst relative difference 0.0)

## The forecast procedure
- **footing_1_measured**: THE PRIMARY FOOTING: each frozen predictor unchanged at each run's measured conditions, read from the data's start-of-run records only (MM1's README section 5 form, as blind-e221 did): the primary view's kernel clock kclock_mhz; minion volts: card 1 the models' footing 0.517 V, the governed cards the primary view's rails.minion.mV / 1000 (else the model's own volts at f); the governed base by the model's own G_of_f(card, f); the run's die_start_c (50 C when absent). The candidates and compositions on MM1-v3.2's forecast at the same conditions, their features configuration-only. The callers: scripts/s02b_nominal.py's forecast_cases(cases, cond), the same code that makes the nominal forecasts (blind-e223 imports it unchanged, cond per run)
- **fields_read_before_scoring**: from each committed E223 data JSON ONLY: the top-level card, session and primary_view, and per run: run, i, ran, role, arm, values, type, shires, minions, die_start_c, arm_token, arm_family, ops_pass, ops_pass_ok, and the primary view's kclock_mhz and rails.minion.mV. No time, cycles, power, energy or seconds field is read until the forecasts at those conditions are hashed
- **footing_2_nominal**: the nominal forecasts frozen now (section h), scored beside by the same rules (REPORTED)
- **counts_as_inputs**: the switch counts are inputs, never fitted: each model's own tables (MM1-v3.1 and MM1-v3.2: MM1-v3's rows + counts 3e8991d0; counts-e214); E223's kinds (zeros, ones, random) are committed kinds with committed counts; E223 designs no tile, so no count is made (no counts-e217 rows: E224's callers run with e217=False)
- **order**: 0 the work copies -> 1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt (no step 4: no counts); after the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> the read and the scores

## c. The metric
- **error**: forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W
- **case**: a case's error = the mean of its runs' errors (each run at its own conditions); per-run figures REPORTED beside
- **twins**: per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs' measured clocks to 25 MHz) is in that model's TRAINING time configurations (a base model's landed out/points_time_*.csv, E146 store rungs out; a term's model: MM1-v3.2's keys UNION every point its term's fit read (gemmlnc-af4/data/s01_points.json, posimb/out/points_all.json, l3s/out/data/points_all.json, posimb-mask/out/points_all.json), a conservative twin); an energy case when that key and its kind are in its energy configurations (work/step1/twin-keys.json, 8e90e2c4); the no-twin cases carry the pass rule and the headline; twins and all cases printed beside. At the nominal clocks (a preview; the measured clock decides): MM1-v3.2 60 time / 49 energy twins of 695, MM1-v3.3 60 / 49, MM1-v3.1 32 / 24, MM1-v3 32 / 24, MM1-v2 17 / 14, posimb and L3S and their compositions 71 / 60, posimb-mask 135 / 125 (it was fitted on E221's 733 cases, many of whose configurations E223 repeats)

## d. The comparisons
- **test**: the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more cases; B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none
- **d**: per case d = |ln(1 + e_B)| - |ln(1 + e_A)| (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over every case both price (twins included); REPORTED beside over the cases that are twins for neither
- **ties_how**: E215's rule (rules_e215.ties_of) on the floors of work/step1/bands.json (decl-e221's, equal): card 1 E215 arm B's registered ties {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.1}; aifoundry1 card 0 {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.15} (E212 a1c0-S1/S2); aifoundry2 card 0 {'cycles_ln': 0.005, 'joules_ln': 0.02, 'seconds_ln': 0.005, 'watts_W': 0.4} (E212 a2c0-S1/S2: a weak floor, 3 cases with two runs)
- **D0_v33_vs_v32**: MM1-v3.3 vs MM1-v3.2 on H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t forecast (E2): per card and pooled over every case; it reads NO DATA by construction (AF4 acts at no E223 case), declared now
- **D1_v32_vs_v31**: MM1-v3.2 vs MM1-v3.1 on H1-H5: per card and pooled; per class and per held-out set REPORTED
- **D2_v32_vs_v3**: MM1-v3.2 vs MM1-v3 on H1-H5: per card and pooled; per class and per held-out set REPORTED
- **D3_masks_REPORTED**: deciding nothing: on THE PLACEMENT CLASS (PLACE, 421 cases), each REPORTED mask candidate vs MM1-v3.2 (MM1-v3.2 + posimb, MM1-v3.2 + posimb-mask) on H1 (wall), H2 (counter mean), H3 (seconds) and H5 (J over idle with t forecast), per card and pooled; the same on every subset-mask case (513), on MASKE221 (353) and on each held-out set, REPORTED; and the two against each other ('MM1-v3.2 + posimb-mask' vs 'MM1-v3.2 + posimb') beside
- **D4_L3S_REPORTED**: deciding nothing: 'MM1-v3.2 + L3S' vs MM1-v3.2 on its 182 full-mask cases (H1-H5), per card and pooled; the compositions vs MM1-v3.2 beside
- **D5_switch**: NOT APPLICABLE: E223 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random), so the switch route with counts against without has nothing to decide
- **verdicts**: each comparison is a verdict of its own, never part of PASS

## e. Reported beside (deciding nothing)
- **classes**: each class's rms and bias per card and model (the placements first, then the held-walk edge, the L3 region, the wide-B wait, the masked energy cases, the kinds, the 1x1x1 cells, the shape probes, the anchor), REPORTED
- **held_out_sets**: each of the 15 held-out sets' rms and bias per card and model, and part A's cells on each set alone, REPORTED
- **maske221**: blind-e221's MASK class by its own definition: rms and bias per card and model, part A's cells on it alone and on every case outside it (so E223 reads blind-e221's finding again), REPORTED
- **mask_ladders**: each subset case against its whole-chip twin (same card, token, format, kind at 0xffffffff) where E223 runs one: measured and forecast subset/full ratios per model, REPORTED
- **governed_clock**: on the governed cards: each run's measured clock beside the nominal 800 MHz and the nominal-footing error, REPORTED

## f. The pass rule (decided by a script)
- **part_A**: MM1-v3.2 on the PRIMARY footing by E215's rule form on each card over its NO-TWIN cases (every class): a case passes T1, T2, T3, E3, E4 when |error| is within the band, E1, E2 when |error| is within the band or, at a watts case, |watts difference| within the watts band; a rule PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 cases, NO DATA with none. PART A PASSES when no rule FAILS on any card and at least one rule PASSES; FAILS when any rule fails (named); else NOT DECIDED
- **bands**:
  - aifoundry1 card 1: {"E1": 0.14, "E2": 0.14, "E3": 0.05, "E4": 0.1, "T1": 0.1, "T2": 0.13, "T3": 0.1, "watts_W": 0.56}
  - aifoundry1 card 0: {"E1": 0.11, "E2": 0.13, "E3": 0.05, "E4": 0.1, "T1": 0.11, "T2": 0.16, "T3": 0.11, "watts_W": 0.56}
  - aifoundry2 card 0: {"E1": 0.11, "E2": 0.13, "E3": 0.05, "E4": 0.1, "T1": 0.1, "T2": 0.13, "T3": 0.1, "watts_W": 0.72}
- **bands_how**: E215's form by rules_e215.bases from MM1-v3.1's held-out errors (work/step1/bands.json, made by decl-e221's s01d_bands.py unchanged on this work copy: every band and tie equal to decl-e221's), the same bands for every model: a declared choice
- **part_A_others_REPORTED**: the same rules for MM1-v3.3 (identical to MM1-v3.2's by construction), MM1-v3.1 (the continuity with E215, E217, E219 and E221) and each REPORTED model, REPORTED, deciding nothing
- **part_S**: NOT APPLICABLE (no operand-pattern arm: D5)
- **verdict**: PASS when part A passes; FAIL when it fails (named); NOT DECIDED otherwise. Decided by a script: blind-e223's scorer (the scripts of the lane that scores E223, in blind-e221's form), implementing this declaration's sections exactly, code-tested on a stand-in day built from the frozen forecasts alone, and hashed (sha256 in its progress log, posted with the result) BEFORE its first read of any E223 measurement; a departure from this declaration is a dated amendment hashed before that read. The nominal footing (section h) by the same script and rules beside, REPORTED. A session that does not run, or runs short, is scored on what ran; a card with no session is NO DATA (aifoundry1's six sessions may never run under this freeze)

## g. The label rule
- **BLIND**: a session is BLIND for this test when FROZEN.txt's sha256 lines were posted on the Discussion (#16) before the session's first datum (its first card command, the session's own log)
- **UNREAD**: a session whose first datum precedes the freeze post is UNREAD for it, provided no lab lane had read its data before the post (data-e223's read times on record); else POST-READ (REPORTED)
- **printed**: every result line names its label, the freeze post time and the session's first card command time

## h. The nominal footing (a second footing, frozen now, scored beside)
- **aifoundry1 card 1**: f 600.0 MHz; V 0.517 V (the models' card-1 footing); die at start 60.0 C (the kit's a1c1 start-gate ceiling)
- **aifoundry1 card 0**: f 800.0 MHz (its planned clock: the kit's main band "800"); V the model's own volts at f; die at start 55.0 C (the kit's a1c0 start-gate ceiling)
- **aifoundry2 card 0**: f 800.0 MHz (the kit's main band "800" for the governed card, its planned governor point: nothing is set); V the model's own volts at f; die at start 55.0 C (the kit's a2c0 start-gate ceiling)
- **files**: forecasts-nominal-e223.csv and .json: one forecast a case and model for every case (every run of a case at the same nominal conditions), all 13 model columns (8 REPORTED)
- **scored**: by the same rules as the primary footing, beside it, REPORTED

## i. Earlier reads, disclosed
- **E223_data**: none read: by #16.1.1 no E223 session sends a card command before the lab's E223 freeze post, and W/out/orch/e223-releases.txt holds no claim or release at this declaration (not checked on the boxes: this lane made no ssh call); this lane opened no EE/sessions/ folder on aifoundry1 or aifoundry2 and no data folder named for E223
- **this_lane**: read the kit copy's arms.json, schedules, README, mms_common.py (the cards, bands and gates) and the 9 tile files' bytes against the lab's kinds; the frozen models' code; Q234's candidates and E222's and E224's callers as landed; Q238's mask-posimb as frozen; probe p01 (the domain, status only) and probe p02 (a code test of the nominal-forecast script: only its checks, counts, scopes and the factor ranges printed; its output deleted unread) ran before this declaration and chose nothing in it; no forecast of the model session's (its sealed eb5478f6... was not read)
- **others**: reg-e223 and data-e223 (Q239) run beside: the registration from #16 and the same copy, and the data lane waiting for this freeze and the releases; Q236 (E222's scores, committed c661275c), Q237 (E224) and Q238 (the mask candidates) beside

## The inputs, by sha256

- `ed4595b10697daa0d1923d3fcaca2a04b295e6ccdd0dc2e87e5f77448330004d`  work/step1/runs-listed.json
- `ba9fe87a6c8e101e57c63326068845a792aa827a8e476414697b8c9ad2a105b0`  work/step1/models-step1.json
- `8e90e2c44a8846f5ab13f26b69982d78031db8cba22328ac2c7af951387c1a41`  work/step1/twin-keys.json
- `526e6c8b28a3882ee547dfcd8bcee6679eb1eaf04dfe8791bc71bde11f32c00e`  work/step1/bands.json
- `3ed26d5eccd97e4a6d31fa14cd20c333cadb18c4876cb33df4c8af0ea077b0bd`  work/step1/domain-probe.json
- `6c199fc427c6a07fbb65d11e3f947d64b9b584d17a6942bcc63780ea0809e9b5`  work/lab-commit.txt
- `627b622e47daae5758a3e47932292d49517176fa7084a5e1e898ee7926b4c898`  work/e223-src/SRC-SHA256SUMS.txt
- `e624689ce71de35c2ac70f926a51cba9093cc058fd3edb46da6440566a0aacb3`  work/e223-src/src/arms.json
- `81a5732cc75df33762ae300426baddd484f0410ec34e7ae313912819ecf9dbcb`  work/e223-src/src/README.md
- `3c3fa3549356788b74e2615cc69cb8fefd999cf40db4380bdab845bab12ecb1d`  work/e223-src/src/mms_common.py
- `ca9710e75f6bfbe9631489b61f2ea612032411c777d49d5da228cfc34bd38d8f`  work/e223-src/src/reduce_mms.py
- `0cd8e9da11e1b0f0bedba342e40adf2a18e9ff112f87e5436d712f32fe5eafdc`  work/mask-posimb-FROZEN.txt
- `b82c1178cffb4da36afd09eff9d8af200ec249fbfc289bfe2f6eddecbaefe5ab`  work/mask-posimb-frozen-lines.txt
- `9737bba9795d621c86294c3336dabd3d3428baa052a2aa23130a3482a8238734`  work/q238-frozen-posts-at-setup.txt
- `9737bba9795d621c86294c3336dabd3d3428baa052a2aa23130a3482a8238734`  work/q238-frozen-posts-at-declaration.txt
- `d52c9cce15db12ed66873722b9ec5c07be1fdeec3027a23833c7e3d230d1d761`  work/lab/tools/matmul/mm1/v3.2/SHA256SUMS
- `c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab`  work/lab/tools/matmul/mm1/v3.2/out/mm1_v32_params.json
- `e9a1ced7aa2fe50c66f9a1c389cb6c0064979be1d5f149a299f7a82e54ba2d5f`  work/lab/tools/matmul/mm1/v3.2/mm1_v32.py
- `f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed`  work/lab/tools/matmul/mm1/v3.1/SHA256SUMS
- `d01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3`  work/lab/tools/matmul/mm1/v3.1/out/mm1_v31_params.json
- `c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74`  work/lab/tools/matmul/mm1/v3/SHA256SUMS
- `1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db`  work/lab/tools/matmul/mm1/v3/out/mm1_v3_params.json
- `916954ccaf477c3e4c858d1a6f68c2cb5d224339792e33bab4fa81908c7f2028`  work/lab/tools/matmul/mm1/v3/unread_v2_e212.py
- `eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2`  work/lab/tools/matmul/mm1/v2/SHA256SUMS
- `9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5`  work/lab/tools/matmul/mm1/v2/out/mm1_v2_params.json
- `acef395141bb0ca12f54b22d28a17e129154aa64b12b3f8c0d99ebbd95184ba8`  work/lab/tools/matmul/mm1/v3.3-cands/posimb/SHA256SUMS
- `93c2575b073a456b4ffeb91140c63a7d917ca93d2c40176259d74e7ebd2a3d88`  work/lab/tools/matmul/mm1/v3.3-cands/posimb/SHA256SUMS-note1
- `ef885cb8cdf37dffb1be511b2f6ccdaa1eb37a8f7780590bc95444c9c3e2f8b9`  work/lab/tools/matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS
- `d6f13cf2748c88f08bfee05c88c9e5e0efe36f754e642eed97cfa06a93430771`  work/lab/tools/matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS-note1
- `c5d4f03e4364d451f988c7bd09f63f380e78a93cdb2f6e472899594bbe731091`  work/lab/tools/matmul/mm1/v3.3-cands/l3s/SHA256SUMS
- `d9ec0f79db4e236ac6e51ae4a9021d41ace01db9a5264bcede8ae0ee65503b5f`  work/lab/tools/matmul/mm1/v3.3-cands/l3s/SHA256SUMS-note1
- `419dac6e69b354187261a347fcec2134a5024dbc1c95ae3e5d7ba052b46ae36c`  work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask/SHA256SUMS
- `8d19e0104693b14405abd3b0130e927f5076cc80cde057aac9bfe8e8bf1b6d3e`  work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask/posimb_mask.py
- `3cceb99239d7d71ffc911265e3aab7914463967a70785a28f11613fde1a1f8d5`  work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask/params-posimb-mask.json
- `057c96523a018cd7ed6159644378e1040197711f1415b104a715ec20b1546ee0`  work/lab/tools/claims-v3/e224/desk/models_e224.py
- `9420b5d1a4c88ad78f4e3141847e12aeb276b8ee4dc4ee239ce7aba045bf6355`  work/lab/tools/claims-v3/e224/SHA256SUMS-e224-registration
- `3b8b2b9140dea4f82b38abf330f7dbd3633358f0e809cf75c54b93b24eec8249`  work/lab/tools/claims-v3/e224/SHA256SUMS-e224-kit
- `bedaf2211676980abde4a9af3e0b2740026980ce6e473a23b5529624bce1eff2`  work/lab/tools/claims-v3/e224/forecast-e224.csv
- `590bcf249f4663c8b1819075029f6a93e329fd0756287370d01f21caac8f5bc9`  work/lab/tools/claims-v3/e222/desk/models_e222.py
- `de67150bee12bde15c50d0f1067d042a0cd0ca3a9a8ad74af577145d077acef7`  work/lab/tools/claims-v3/e222/SHA256SUMS-e222-registration
- `5a44879ca9c4f0c7d8c4084f4dca93886fe6b18bfb1cf1a81bb76cc29d6f2272`  work/lab/tools/claims-v3/e215/rules_e215.py
- `fd9d5ad1d9d7e8094ee9fc9ab848ae1426c2b517c1fded3e973973c6cac96dbc`  work/lab/workloads/nocbench/analyze.py
- `c320788fdc11cea7df21940721594ccc05c6b39a0deb02c12bde44ac6711afc4`  work/e223-src/src/sched/a1c0-S1.json
- `d4ff5a0e4910a342c23655a76a4d33e17d58412e8b35d99f126e1d8b02f6ec6e`  work/e223-src/src/sched/a1c0-S2.json
- `82f895412de9e453a68edc5a0a371b56f1fddd3d08c129cd6371e1acbd72af45`  work/e223-src/src/sched/a1c0-S3.json
- `c2e3bbaa03a42fa2b0d5e48b17ad79f010794b25218b3ddc786202b4663ce2d0`  work/e223-src/src/sched/a1c1-S1.json
- `7b6eec748800e99428567e9e2e95c51c5a8a0b57634094b77f9c970eb528affa`  work/e223-src/src/sched/a1c1-S2.json
- `c9dfc2e83a11dd6f132e16d476d6bb32d19004217829f407db7ee891921ee06a`  work/e223-src/src/sched/a1c1-S3.json
- `22dc466179ed3acbd3d3a6d85f122f0f55f95c96e7b1c26500b9832cdbf84ac3`  work/e223-src/src/sched/a2c0-S1.json
- `0dde66b218f42ff7ee74b599db36b09d75a9b7c5320f8d9f8700b609df017b03`  work/e223-src/src/sched/a2c0-S2.json
- `b4722dee2210b60062f055100fb31be7b3c858734eb199aa76c5e7969f5afe5d`  work/e223-src/src/sched/a2c0-S3.json
- `277ab8375fde51133678bcbf2fdf7b9414878e50a7c91f4ebc729ae954a7d75e`  scripts/env.sh
- `b1a131bd740bb31a2ad449f355df1df4e90595dbe2b69d27a91fb1470aa626d0`  scripts/p01_probe.py
- `a09c5eb30274bdbd76939c18ee28bd70a1cbf59b8f633b892e1f44242bc3c74e`  scripts/run_slot.sh
- `4cb53c5f8aaeb66f4a065aa73c6b88a83cca31e64f7dc449641c18549f5edf3e`  scripts/s00a_setup_lab.sh
- `63a07f5c01d29605a7c9feca58ddd4541c48c5607f88a6deabaa1b91cbd880bc`  scripts/s00b_setup_kit.sh
- `3dc5c609586caf5dadd858fe6044a9ad7def836c9f6af8115a9f8793851827ea`  scripts/s00d_more_lab.sh
- `860437436fe97202a8b103adca12c03043eafed3e525c590c5a6a9273b695c46`  scripts/s01_list.py
- `4c98de7cdfb09160adc8e0d7cc00a26216d56b3bb8b9e32f9a29e0207e1f67af`  scripts/s01b_models.py
- `171ce994633472e6c775c54375f9102807394e1396381fea182c407e2a390bc5`  scripts/s01d_bands.py
- `96eefa9ae39dd2a00c353da45c0986fa2051bc146fc496d37229c6b18f460b28`  scripts/s01e_declare.py
- `266eb6db5608e4dcc276238ef8d857d747d9a3ca0a0773569cf352881bed74c4`  scripts/s02b_nominal.py
- `8259225566f5468db3083e8c46c99641b239e1c72e356e05b6d68b6629212773`  scripts/s02c_write.py
- `2d0b1e5b614c42b4980f138b237eccf73095165b3cae1f5da6255edb38c5dd98`  scripts/s0xh_hash.sh

SPDX-License-Identifier: Apache-2.0
