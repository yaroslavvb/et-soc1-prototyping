# decl-e223 AMENDMENT 1 (dated): mesh and the mask ceiling join the lab's blind test of E223 as REPORTED, before any E223 datum

*Lane amend-e223 (round Q239a), aifoundry2's desk; written Sat 21 Nov 2026 02:36:29 PST, Pacific time. Desk only: no card, no ssh, no simulator, no commit.
Interpreter: /usr/bin/python3 3.12.3, -I -B, single-threaded, every numerical step one slot job. New files beside the frozen declaration
(decl-e223's FROZEN.txt 5551c2d7..., frozen 02:22:09 PST, posted on #16 at 02:23:46 PST): no frozen file is
edited. Labels as the declaration's: registered (this file), measured, desk, post hoc, held out, blind; REPORTED = printed beside, deciding
nothing.*

**Why an amendment.** The declaration's own rule (its Q238_read): "A Q238 candidate that qualifies only after this read is not in this
freeze: it can be scored on E223 only by a dated amendment hashed before E223's first datum, else as UNREAD". Two Q238 freezes qualified
after its 02:19:24 PST read. W/out/orch/q238-frozen-posts.txt read again at 2026-11-21 02:29:01 PST (sha256 fdf2d28c13786dd3...):
- **mask-mesh** 'MM1-v3.2 + mesh' (track M, KEPT by its declared rule): FROZEN.txt `487188c7f0ddce244f09abb05aeca4427e69d4be9133e87154863cdc4abec425`, final 02:03:37 PST; its correct freeze
  line posted at 02:23:42 PST (#1.30.1.2.1.1.1.1.1.1.2, the correction: the 02:03:18 post named the superseded first write 3d4942fa). On
  disk = posted = the land's FROZEN.txt; all 47 files it lists re-hashed equal; the land's SHA256SUMS
  51/51 OK; every file this amendment calls (mesh_term.py,
  mesh_l3.py, compose_af4.py, params-mesh.json, features-mesh.json) equal to FROZEN.txt as run.
- **mask-ceiling** 'MM1-v3.2 + mask-ceiling' (track C, a nonparametric REFERENCE, REPORTED, never a model candidate): the posted freeze line
  (#1.30.1.2.1.1.1.1.1.1.1, 02:21:44 PST) names FROZEN.txt `1649ba5ba69e1061af112e0ce6b98e4d42101080cd9e202f1bacea51edb8b45f` (its 02:21:13 write, kept as FROZEN.txt.superseded-022113). Its
  lane rewrote FROZEN.txt at 02:22:21 PST (`bf6e2d9643bd8869...`, not posted at this read), changing only
  README.md, SCRUB.json, SHA256SUMS, logs/progress.txt, scripts/l01_readme.py; every file this amendment calls (mask_ceiling.py, params-mask-ceiling.json,
  scripts/r_common.py, rf_core.py, f01_features.py) is equal under both lines, so its forecasts are the same under either. This amendment
  names the posted line.

## 0. What changes, and what does not

- **Added: three REPORTED columns, deciding nothing:** 'MM1-v3.2 + mesh', 'MM1-v3.2 + AF4 + mesh' (by construction, no refit) and the
  reference 'MM1-v3.2 + mask-ceiling'. Unchanged: the pass rule (part A on MM1-v3.2), the bands and ties, D0-D2, D4, D5, the label rule for
  every declared column, the nominal conditions, the case list (695 cases, 803 runs; decl-e223 work/step1/runs-listed.json ed4595b1...)
  and every model the declaration names.
- **MM1's domain:** every E223 case is in each added column's domain: mesh acts at the 513 subset-mask cases of rgm136 gemmL and is
  MM1-v3.2 to the last bit at the 182 full-chip cases; the reference acts at 454 cases (rgm136 gemmL with MB x NB >= 2
  at a shire subset) and its factor is exactly 1 at the other 241; AF4 acts at no E223 case (no gemmLnc arm). OUT OF
  DOMAIN: none.

## The added models

- **MM1-v3.2 + mesh (REPORTED)**: Q238's mask-mesh, its land folder copied unchanged to work/lab/tools/matmul/mm1/v3.4-cands/mesh/, at
  its frozen constants {"a_set": 0.7377811362331885, "a_hop": 0.8265683148782694} (variant 'laggard') on MM1-v3.2 4e386f75 unchanged, called as its README's
  section 6 says: `mesh_term.Model(json.load(open('out/params-mesh.json')), 'out/features-mesh.json').time_many(points)` with
  MASK_MESH_REPO = the lab copy, points {arm, kernel 'rgm136', fmt, mask, f}. The record: T = time_many's op time; cycles an op = T x f;
  the counter's mean = cycles / MM1-v3.2's rho; seconds a pass = ops x T; W over idle at a measured t = MM1-v3.2's A + B / t (so E1 is
  MM1-v3.2's); with t forecast at this T (E2, E4, H5). Its features are configuration-only (arm and mask: the walk's sets and latencies); a
  configuration missing from its frozen features cache is made by its own mesh_l3.simulate (no constant), as the README says.
- **MM1-v3.2 + AF4 + mesh (REPORTED, by construction, no refit)**: `scripts/compose_af4.py composed(specs, mesh)` unchanged (README
  section 6). AF4 acts at no E223 case, so it equals 'MM1-v3.2 + mesh' at every case (checked to 1e-12 at the nominal footing): declared now,
  its tests repeat mesh's.
- **MM1-v3.2 + mask-ceiling (a REFERENCE, REPORTED, never a model candidate)**: Q238's mask-ceiling, its land folder copied unchanged to
  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/ (the all-data forest, params-mask-ceiling.json f991b637...), called as its README's
  section 7 says: `python3 -I -B mask_ceiling.py --points <points.json> --out <factors.json>`: the factor (1 off its scope); the forecast is
  MM1-v3.2's own row with T_op_us, cycles_per_op_wall and seconds_per_gemm times the factor, the counter's mean MM1-v3.2's (the reference
  forecasts none), W over idle at a measured t = MM1-v3.2's A + B / t, with t forecast at the new T. Its features: the configuration (arm,
  mask, format) and the clock f.

## The forecast procedure

- **footing_1_measured** (the primary footing): the declaration's, unchanged: each frozen predictor at each run's measured conditions,
  read from the data's start-of-run records only (the primary view's kclock_mhz; card 1 0.517 V, the governed cards rails.minion.mV /
  1000; die_start_c, 50 C when absent). The callers: this lane's `scripts/s03_forecast.py` `forecast_amend1(cases, cond)`, the same code
  that makes this amendment's nominal forecasts (cond per run {'f', 'V', 't0_c'}), each term on MM1-v3.2's forecast at the same conditions.
- **fields read before scoring** and **order**: the declaration's: after the data, the conditions read, then the measured-conditions
  forecasts of every column (these three with them) hashed, then the scorer hashed, then the read and the scores.
- **footing_2_nominal**: forecasts-nominal-e223-amend1.csv and .json, frozen with this amendment (section h).

## c. The metric

- The declaration's: error = forecast / measured - 1; rms % and signed mean (bias) %; watts cases rms and mean in W; a case's error = the
  mean of its runs' errors.
- **twins**: per column by the declaration's own rule: MM1-v3.2's keys UNION every point its term's fit read (mesh: out/points-mesh.json,
  4311 points, 1fc09683...; the reference: inputs/points_all.json, 4311 points,
  0090bbdd...; 'MM1-v3.2 + AF4 + mesh' AF4's data/s01_points.json too), time and (with the kind) energy alike,
  a conservative twin: work/step2/twin-keys-amend1.json. At the nominal clocks (a preview; the measured clock decides), time / energy twins
  of 695: MM1-v3.2 + mesh 135 / 125; MM1-v3.2 + AF4 + mesh 135 / 125; MM1-v3.2 + mask-ceiling 135 / 125. No E223 point is in any fit (0 E223 ids in either points file).

## d. The comparisons

- **D3a_masks_REPORTED** (deciding nothing; the declaration's D3_masks_REPORTED form exactly): on THE PLACEMENT CLASS (PLACE, 421
  cases), each of 'MM1-v3.2 + mesh', 'MM1-v3.2 + AF4 + mesh' and the reference 'MM1-v3.2 + mask-ceiling' vs MM1-v3.2 on H1 (wall), H2
  (counter mean), H3 (seconds) and H5 (J over idle with t forecast), per card and pooled; the same on every subset-mask case (513), on
  MASKE221 (353) and on each held-out set (HO-111 (14), HO-Ccard (3), HO-EDGE (40), HO-G (70), HO-GATE (36), HO-KIND (51), HO-L3 (21), HO-N (24), HO-P1 (121), HO-P1card (2), HO-P2 (18), HO-P34 (21), HO-S (48), HO-TW (12), HO-WIDE (41)), REPORTED.
- **D3b_beside_REPORTED**: 'MM1-v3.2 + mesh' vs 'MM1-v3.2 + posimb-mask' and vs 'MM1-v3.2 + posimb'; the reference vs 'MM1-v3.2 + mesh' and
  vs 'MM1-v3.2 + posimb-mask'; the same cases, quantities and test.
- **test**: the declaration's: the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is
  closer in more cases, B BETTER the other way, NOT DECIDED otherwise, TOO FEW under 10 untied cases, NO DATA with none; per case d =
  |ln(1 + e_B)| - |ln(1 + e_A)| (at a watts case |dW_B| - |dW_A| in W); ties by E215's rule on the declaration's floors (work/step1/bands.json
  526e6c8b); over every case both price (twins included), REPORTED beside over the cases that are twins for neither.
- **declared now, by construction**: 'MM1-v3.2 + AF4 + mesh' = 'MM1-v3.2 + mesh' at every E223 case, so its tests repeat mesh's; the
  reference's H2 is MM1-v3.2's counter mean, so its H2 test vs MM1-v3.2 reads NO DATA (no untied case); E1 (W given t) is MM1-v3.2's for all
  three columns, so no E1 comparison is made for them; at the full-chip cases mesh is MM1-v3.2 to the last bit, and the reference is
  MM1-v3.2 wherever it is out of scope: those cases tie.
- **verdicts**: each comparison a verdict of its own, never part of PASS; the reference is never a candidate: its rows bound what a mask
  term built from its features reaches, printed as a reference.

## e. Reported beside (deciding nothing)

- The declaration's section e with the three columns in each: the classes (the placements first), the 15 held-out sets, MASKE221 (part A's
  cells on it alone and on every case outside it), the mask ladders (measured and forecast subset/full ratios per model) and the governed
  clock, REPORTED.

## f. The pass rule

- Unchanged: part A on MM1-v3.2 by the declaration's rule form and bands decides PASS / FAIL / NOT DECIDED. part_A_others_REPORTED gains
  the three columns (the same rules, REPORTED, deciding nothing).

## g. The label rule

- The declaration's, with this amendment's FROZEN.txt for the three columns: a session is BLIND for them when this amendment's FROZEN.txt
  sha256 lines were posted on #16 before the session's first datum (its first card command, the session's own log); UNREAD when its first
  datum precedes that post and no lab lane read its data before the post; else POST-READ (REPORTED). If this amendment is not posted before
  E223's first datum it lapses, and the three columns are scored post hoc, labelled so.

## h. The nominal footing

- The declaration's section h conditions, unchanged: aifoundry1 card 1 600 MHz, 0.517 V, die at start 60 C; aifoundry1 card 0 and
  aifoundry2 card 0 800 MHz, the model's own volts at f, 55 C.
- **files**: forecasts-nominal-e223-amend1.csv and .json: one forecast a case and model for every case (every run of a case at the same
  nominal conditions), the three added columns, each by its frozen code unchanged; MM1-v3.2's column stays the declaration's frozen one
  (re-made by mm1_v32.Model.predict_many at the declaration's specs and checked equal at every case before any output).

## i. Earlier reads, disclosed

- **E223 data**: none read: this lane opened no EE/sessions/ folder on any box, made no ssh call and opened no data folder named for E223.
  W/out/orch/e223-releases.txt at this amendment (5620d3a23a9edd12...) holds the proposal (#16 01:25:49) and aifoundry2's push (#16.1.1
  01:55:59, "no session sends a card command before the lab's E223 freeze post"), no claim and no release; claim files: none.
- **this lane**: read the frozen declaration, its scripts and its work copy (copied to work/lab); mask-mesh's and mask-ceiling's frozen
  files, READMEs, lane logs and results; probe p01 (the walk's and the ceiling's feature-making times at 5 E223 configurations, no forecast)
  and probe p02 (a code test of scripts/s03_forecast.py on 31 of the 695 cases: only its checks, scopes and factor ranges printed, its
  output deleted) ran before this amendment and chose nothing in it.
- **mask-ceiling's README**: the posted FROZEN.txt's README bytes (66297333...) are not on disk: the land carries the 02:22:21 text
  (4a575a33...; its lane's log: section 3b added, no number changed); the call form is read from it and from mask_ceiling.py's own
  docstring, which is equal under both lines.
- **mesh's features cache**: 119 of E223's 162 mesh configurations (arm and mask, with their full-chip references) are not among
  features-mesh.json's 600: the frozen walk makes them at forecast time, as its README says; the walk re-makes cached configurations'
  features bit for bit (checked in p02 and in the run).

## The inputs, by sha256

- `80b4b03f7f2cfe197556973938608714910ce4e55bd31d9912d8dfbbaa913a01`  work/step1/frozen-checks.json
- `5551c2d7b7b6b5bc40526997a2d8bcbfe62fc8b1468da514781fa59d7543b850`  work/step1/decl-e223-FROZEN.txt
- `487188c7f0ddce244f09abb05aeca4427e69d4be9133e87154863cdc4abec425`  work/step1/mask-mesh-FROZEN.txt
- `1649ba5ba69e1061af112e0ce6b98e4d42101080cd9e202f1bacea51edb8b45f`  work/step1/mask-ceiling-FROZEN-posted-1649ba5b.txt
- `bf6e2d9643bd886984f370b37017a7a915051d1bdeed73fd4eb6f59dce7a112f`  work/step1/mask-ceiling-FROZEN-disk.txt
- `fdf2d28c13786dd3846bc3690140c930c0d748d20076bc5683e0b2a9b57efa7d`  work/step1/q238-frozen-posts-at-amendment.txt
- `b69ba1fe730dfb0c5de7b2cbd4379bf2d043b3aacc0a857feb4a9edaf5e69b27`  work/step2/twin-keys-amend1.json
- `487188c7f0ddce244f09abb05aeca4427e69d4be9133e87154863cdc4abec425`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/FROZEN.txt
- `bf6d5fb75e109658428368a93397d3ba1baac7aad130d43bf81359ddd5dac005`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/SHA256SUMS
- `85c465dc3ae9715b4c095329a450e02f0f4240f4154039875c83ab4d9622a025`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/README.md
- `c8ee1ea9f044d1919712b081a32331f3f5080e043b35042432943124cb2366ac`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/scripts/mesh_term.py
- `fb591e1ed6a048b954bc4c007365cb765368f2eab26cbae79bd733a35d0274b1`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/scripts/mesh_l3.py
- `04c28b969714d2b4a0e734f7a343383fc72708bb7ba7cedb5e9310723c7f2a47`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/scripts/compose_af4.py
- `b4e3ff8e3fd07e1e76761e82a9d48428b0ad17f31d7c83d4c69ef433cb11293f`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/out/params-mesh.json
- `76ffbf216950818b9be9779967e45345c601160f1774d588f574add75582dff1`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/out/features-mesh.json
- `1fc09683d9541df27121f72999adc43423724613562e8748eb097e7ee7eb6aef`  work/lab/tools/matmul/mm1/v3.4-cands/mesh/out/points-mesh.json
- `bf6e2d9643bd886984f370b37017a7a915051d1bdeed73fd4eb6f59dce7a112f`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/FROZEN.txt
- `9bb5734fbacb145a45161a786c589ae62ef6d6dce6da8cf692542eee3675c68a`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/SHA256SUMS
- `4a575a339eee58e93171b8a1d6add9d8d680153a4c22f135af654364820e3612`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/README.md
- `3674c568c34891f7b8ceedccf36fa5e6a4ba9d5c18669504e5aaef2f9af806f1`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/mask_ceiling.py
- `f991b63787a4b3990328a8d1f232413f3b91ae0005df011d8a3a9c03c2fbe1d8`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/params-mask-ceiling.json
- `4a43e05482775f1599c2e05b39ba20d04c9d1b7eb3c0c4fa11d1b3adbb1771ce`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/scripts/r_common.py
- `5f92ba5af3d2f3fde39e5d2e9bba493ace193611ee983a62a7315fbb72523c97`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/scripts/rf_core.py
- `fd9e8df17b3e8b42d842090e68f78621117f706bdd60cf751160dcebd7ae3e18`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/scripts/f01_features.py
- `0090bbddae5e0ceb575248139fd1c01799bd219198708d911b98651b4e3e3d0f`  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/inputs/points_all.json
- `d52c9cce15db12ed66873722b9ec5c07be1fdeec3027a23833c7e3d230d1d761`  work/lab/tools/matmul/mm1/v3.2/SHA256SUMS
- `c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab`  work/lab/tools/matmul/mm1/v3.2/out/mm1_v32_params.json
- `e9a1ced7aa2fe50c66f9a1c389cb6c0064979be1d5f149a299f7a82e54ba2d5f`  work/lab/tools/matmul/mm1/v3.2/mm1_v32.py
- `ef885cb8cdf37dffb1be511b2f6ccdaa1eb37a8f7780590bc95444c9c3e2f8b9`  work/lab/tools/matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS
- `8eb5b7621fd71a78f6964ff0d85466174e5663874ac1db37697d6f3723a983b0`  scripts/p01_time.py
- `f49bc4168d9fc55b4e5db158b1bbac721403de6a7b74c1503fd80c9efb2bb593`  scripts/s01_check.py
- `319c73e770b45539a0d4c1a1e641e4a5e3b90f4f650a1a70b91548ffc3b16307`  scripts/s02_amend.py
- `ce31175815d5c53dca8a4473f06684a69d1e423a87dfe9e5cf73fe1482872545`  scripts/s03_forecast.py
- `ed4595b10697daa0d1923d3fcaca2a04b295e6ccdd0dc2e87e5f77448330004d`  OUT/decl-e223/work/step1/runs-listed.json
- `8e90e2c44a8846f5ab13f26b69982d78031db8cba22328ac2c7af951387c1a41`  OUT/decl-e223/work/step1/twin-keys.json
- `526e6c8b28a3882ee547dfcd8bcee6679eb1eaf04dfe8791bc71bde11f32c00e`  OUT/decl-e223/work/step1/bands.json
- `5620d3a23a9edd1252ab5cd90f0b92a9040bbaafe977bdd431756e3fff38a811`  W/out/orch/e223-releases.txt

SPDX-License-Identifier: Apache-2.0
