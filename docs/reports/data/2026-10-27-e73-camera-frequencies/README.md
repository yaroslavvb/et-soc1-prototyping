# E73 data: the heat path's time constants, three frequencies on one camera (Q129, Tue 27 Oct 2026, aifoundry2)

One card session of [`tools/claims-v3/hlf`](../../../../tools/claims-v3/hlf/README.md), 15:57–16:40 PDT,
`protocol.json` (= the pre-registration's `protocol-e73.json`), 192 harts — 6 minions in each of the 32 shires,
E63 amendment A1's geometry unchanged, with only the number of 10 s launches in a half period varied: five blocks,
**248 launches**, 43.4 min of card time inside a 52 card-min cap, `stop_reason done`, none failed. The raw frames
(2.85 GB, the camera's lossless stream with the host's receive time on every frame) stay on aifoundry2, gitignored, as
E62's and E63's do; everything left there is listed with its sha256 in `left-on-aifoundry2.sha256` and in
[Left on aifoundry2](#left-on-aifoundry2-not-committed) below.

**Nothing on the card or the camera was changed.** The governor was read once before the first launch
(`tdp_w 65, temp_threshold_c 65, low_power, minion 600 MHz / 519 mV` — E72's restored originals) and left alone. No
governor, clock, PMIC, reset, PCIe, driver or firmware command is part of E73. The card lock was held for every
launch, every launch ran under `timeout 10`, and `et_who` was empty at the start.

## RESULTS

**1. 0.01 Hz exists.** `E73-F10`'s ROI fundamental is **322.8 ± 20.6 mK** (15.7 SE, sign-flip p = 0.0029) on a
4.16 W board step; the transfer is **H(0.01 Hz) = 145.2 ± 16.5 mK/W at a lag of 59.4 ± 4.3°**. R1 **PASS**.

**2. The heat path is low-pass, measured rather than assumed.** Against the session's own 0.05 Hz reference line
(58.58 ± 3.55 mK/W at the session mid-time), |H| rises to **1.396 ± 0.255** at 0.025 Hz and **2.610 ± 0.391** at
0.01 Hz. R3 **PASS**.

**3. Both pre-registered models fail the registered discriminator — and that is the result.** R4 has no PASS by
design. The lag at 0.01 Hz was predicted at **42.19°** by M1 (one 12.19 s pole and a 1.32 s transport delay) and
**26.41°** by M2 (two 3.73 s poles). It measures **59.36 ± 4.31°**: **3.98 SE** from M1 and **7.64 SE** from M2, so
neither survives at 2 SE. The magnitude, as the registration predicted, does not separate them — 2.610 ± 0.391
against M1's 3.142 (1.36 SE) and M2's 2.252 (0.91 SE) — the phase does, and it refuses both. The real path lags
*more* at 0.01 Hz than either rival fitted to the old two points.

**4. Across all nine frequencies the data choose a ~16 s pole plus about a second of extra lag, and cannot say what
the second is.** Weighted complex least squares over the 14 included transfer points, one real positive gain, exactly
as registered (`analysis/fit.txt`, `analysis/fit.json`):

| model | parameters (Δχ² = 1) | G₀ / mK/W | χ² / dof | AIC | ΔAIC | group delay / s |
|---|---|---|---|---|---|---|
| P1 one pole | τ = **24.8** [19.7, 32.8] | 352 [284, 441] | 20.34 / 26 | 24.34 | **+7.51** | 24.8 [19.7, 32.8] |
| **P1D one pole + delay** | τ = **15.98** [12.56, 20.91], T_d = **1.009** [0.696, 1.320] | **250.5** [205, 307] | 10.83 / 25 | **16.83** | — | **16.99** [13.62, 21.58] |
| P2 two poles | τ₁ = **15.57** [11.75, 20.78], τ₂ = **1.005** [0.646, 1.452] | 252 [208, 308] | 11.57 / 25 | 17.57 | +0.74 | 16.58 [12.89, 21.69] |
| P2D two poles + delay | τ₁ = 15.94, τ₂ = 0.205, T_d = 0.806 | 250 [204, 309] | 10.83 / 24 | 18.83 | +2.00 | 16.14 [13.47, 21.54] |

- **one pole alone is excluded**: Δχ² = 9.51 for one extra parameter, ΔAIC +7.51;
- **P1D and P2 are not distinguishable** (ΔAIC 0.74): the extra second is either a transport delay of
  1.01 s [0.70, 1.32] or a second pole of 1.00 s [0.65, 1.45], and 14 points at this noise cannot tell them apart;
- the **group delay is 17.0 s [13.6, 21.6]**, longer than M1's 13.51 s (just outside the 68% interval) and 2.3× M2's
  7.47 s. That is the quantity the registration named, and it comes out bigger than either rival.
- the `Δχ² = 1` intervals of the group delay and of G₀ are profiled in `posthoc/prior-anchors.json`
  (`registered_group_delay`), because the frozen script reports those two as point values only.

**5. The two prior anchors, in the same fit, say the same thing** (post hoc, `posthoc/prior-anchors.json`, no
verdict). With E63 A1's 0.05 Hz point (52.71 ± 1.98 mK/W at 99.11°) and Q126's 0.15 Hz third harmonic
(18.41 ± 5.45 at 150.56°) added under their own gain — the camera's absolute gain is not the same on two afternoons —
P1D gives τ = 15.73 s [12.61, 19.97], T_d = 1.105 s [0.90, 1.32], group delay 16.83 s [13.63, 21.37], and one pole
alone loses by ΔAIC 27. The anchors' fitted gain is **1.075×** E73's, and E73's own 0.05 Hz reference line sits
1.44 SE above E63's anchor: the two sessions agree.

**6. What the camera reads is about a fifth of what the board holds.** The preferred shape attenuates 0.05 Hz to
**0.195** of its zero-frequency response, so the 0.05 Hz number E63 and Q128's coda quote (58.6 ± 3.6 mK/W here,
52.7 ± 2.0 in E63 A1) is a *fifth* of the steady rise: **G₀ = 250.5 mK/W [205, 307]** per sustained watt on the
board, 63% of it reached in 17.0 s and 95% in 49 s. This is an extrapolation of the fitted family below 0.01 Hz,
where nothing is measured — see result 8.

**7. 0.05 Hz was measured twice over, by two routes, and they agree.** `E73-F10`'s fifth harmonic against the
reference line: complex difference **3.31 ± 15.52 mK/W (0.21 SE)**. R5 **PASS**. The reference line itself holds
(R2 **PASS**): three blocks on a straight line, worst residual 0.45 SE, χ² 0.31/1, a constant phase of 98.60°
(χ² 0.006/2), and a gain drift of **−44.1%/h** — E63's drift is still there and still uncorrected for by anything
but this line.

**8. The one thing the fit does not swallow.** The 0.01 Hz lag sits **1.7σ above** the preferred model's own curve
(P1D gives 48.8° there, the data 59.4 ± 4.3 — 2.4 SE on that point's error alone), and it is the largest residual in
every fit. The fitted family wants more low-frequency lag than it can produce while still matching 0.07–0.175 Hz. A
third, longer pole or a distributed (diffusive) path would do it; nothing below 0.01 Hz is measured, so that is
**suggested, not established**, and it is the new open item this experiment leaves.

**9. Hold.** R6 **PASS**: from 1.5 s into each launch, **≥ 97.7%** of the in-launch telemetry samples of every
block's analysed laps read ≥ 790 MHz (REF1 100%, F25 99.6%, REF2 99.4%, F10 99.7%, REF3 97.7%), and every block's
die mean is **55.1–56.9 °C** (max 58.3) against the registered 65 °C bar, with `abs_stop_c 80` and
`board_cap_w 70` never approached (~35 W loud, ~26 W quiet). **9 of 248 launches** carried the governor's
one-second idle-reset dip to 600 MHz (REF3 4, F10 3, F25 1, REF2 1; 8 of the 9 on the ZERO arm) — counted and
reported **without a verdict**, which is both the registered rule and E63's lesson.

## What this changes

- **In the energy ledger: nothing.** Not one of Q128's unaccounted **3.837 pJ** per fp32 multiply-add (board) or
  2.39 pJ (rail) moves. E73 measures the path from the die to the back of the board, not the price of a flip.
- **In the coda of Q128's chain ("Back out", the camera weighs the flips).** The coda's camera numbers — 194 mK at
  0.05 Hz for 5.44 W, 59 ± 3 mK/W, "the heat 87–99° behind" — now have a path attached rather than a single
  frequency: a **16.0 s [12.6, 20.9] pole with 1.0 s [0.7, 1.3] of extra lag**, a **group delay of 17.0 s
  [13.6, 21.6]**, and an attenuation of **0.195 at 0.05 Hz**, so the coda's mK/W is a fifth of the steady-state
  **250 mK/W [205, 307]**. The lag at 0.05 Hz that "one pole cannot give" is now explained without a free-running
  second pole: one pole and about a second of transport (or a 1 s second pole — the data do not choose).
- **In the Horace Hub's Levels tab, row "Coda · Back out".** Its Missing cell loses *"the heat path's time constants
  (the same lock-in at a second frequency)"*: three frequencies and nine harmonics in one session, with intervals,
  and both pre-registered rivals refuted by the phase. What stays missing in that cell: **a gain that holds still**
  (it drifted −44.1%/h here, as it drifted 59 → 42 mK/W in E63), **millimetres** (a rigid mount, a fiducial or a
  measured lens distance), and the new item from result 8 — **a frequency below 0.01 Hz**, where the extra
  low-frequency lag would be either confirmed as a longer third pole or ruled out.

## What was registered and what happened

| rule | registered bar | measured | verdict |
|---|---|---|---|
| R1 detected at 0.01 Hz | ROI ≥ 3 SE, sign-flip p ≤ 0.01, board ≥ 5 SE | 15.7 SE, p = 0.0029, board 42.7 SE | **PASS** |
| R2 the reference line | three 0.05 Hz blocks within 3 SE of a weighted line | worst residual 0.45 SE, χ² 0.31/1 | **PASS** |
| R3 low-pass | ratio > 1 at 0.025, and bigger again at 0.01, each by ≥ 1 SE | 1.396 ± 0.255, then 2.610 ± 0.391 | **PASS** |
| R4 the group delay | *no PASS by design*: name the model surviving at 2 SE | 59.36 ± 4.31° vs M1 42.19° (3.98 SE) and M2 26.41° (7.64 SE) — **neither** | **REPORTED, both refuted** |
| R5 0.05 Hz twice over | F10's 5th harmonic within 3 SE of the line's H(0.05) | 0.21 SE | **PASS** |
| R6 hold | ≥ 95% of in-launch samples ≥ 790 MHz per block, die mean < 65 °C | ≥ 97.7%, 55.1–56.9 °C | **PASS** |
| inclusion | a point enters the fit only at board ≥ 5 SE | 14 of 25 points included | as registered |

Predictions were frozen in `predictions.json` before the first launch and nothing was fitted to E73 data: M1's
378 mK and M2's 271 mK for F10's fundamental against a measured **322.8 ± 20.6 mK** (the magnitude was always the
weak discriminator), and M1's 42.19° against M2's 26.41° for the lag, which is the one that decided — against both.

The run itself went to plan: five blocks in the registered order (REF1 F25 REF2 F10 REF3), 30/48/30/110/30 launches,
warm-up cycles dropped as registered (3/2/3/1/3), 12/10/12/10/12 laps analysed, 25,004 telemetry samples at 10 Hz,
and the camera 65,004 packets at **25.0006 fps with 0 gaps, 0 reconnects, 0 partial frames** over 2,600 s. The
camera-only check at 15:44 PDT (`camcheck/`, no card involved) found 2,377 packets at 25.011 fps, 0 gaps, 11 shutter
events in 95 s, and the view in the same place: a shift of (−1, −1) full-resolution pixels, (0, 0) binned, peak
correlation 0.941, so E62's template was kept, not rolled.

The shutter fired **287 times** in the session (6.6 a minute, E63's rate) and nothing was bridged: every stretch
between two events got its own free offset, 12 to 51 stretches a block, and the signal was read only from the
variation inside the stretches. The shutter's phase is flat against the drive in every block
(Rayleigh p = 0.13–0.77), so it cannot be making the signal. The focal-plane thermistor VTEMP carries nothing at
f₀ in any block (0.02–0.21 mK against its own SE, p = 0.60–0.86); the header's `fpa_c` does move with the drive,
which is E63's finding that `fpa_c` is the scene's own mean and not the focal plane. The in-phase maps still carry
the capacitor field's emissivity pattern — r with E62's bloom 0.53–0.86 raw, 0.78–0.85 high-passed, highest
(0.856) in the 0.01 Hz block where the signal is largest — so this is heat on the board, not something in the
camera.

## Departures from the plan, dated

1. **0.025 Hz in place of the 0.02 Hz the ask names** — registered in the pre-registration itself (Tue 27 Oct,
   before the first launch), not a post-hoc change. A half period must be a whole number of launches, because
   `timeout 10` caps a device hold at 10 s; the alternative, stretching the idle tail from ~1.1 s to 4 s, walks into
   the one hazard E63 measured (the governor's idle-reset clock dip, about 1 launch in 45 at any load). On a 10 s
   dwell the ladder is 0.05/N Hz, so E73 took 0.025 and 0.01, which bracket 0.02, and kept E63's launch geometry
   exactly — which is what makes E63's own 0.05 Hz number a valid anchor.
2. **Tue 27 Oct 16:45 — the session's own agent died with the data still on the box.** The card run finished at
   16:40 and the registered reduction at 16:42; the agent was cut off by its account's 5-hour limit at 16:45 while
   copying the files to the Intel. **Finished Wed 28 Oct 2026 by a second agent with no card access of any kind**
   (no launch, no `ettelem`, no card lock, no governor read). Two consequences, both resolved:
   - the interrupted copy had staged no telemetry: its collector looked for `tel.jsonl.gz` or `tel.jsonl.raw`, and
     the runner had written `tel.jsonl`. The 17.7 MB raw file was gzipped on the box on 28 Oct and fetched
     (`session/tel.jsonl.gz`, 645 kB, sha256 `074a4f0a…`, from `tel.jsonl` sha256 `6785d738…`).
   - every other committed file was checked byte-for-byte against the box's copy by sha256 before this commit; all
     26 match.
3. **Wed 28 Oct — the frozen copy of `lockin_hlf.py` on the card host is one edit behind the committed
   registration, and it makes no numerical difference; shown, not asserted.** The code was staged at 15:52 Tue; the
   committed file (`1228d765`) carries a 15:53 edit whose whole content is the seven lines that let it find
   `lockin_hlc.py` in either layout (repo sibling, or the frozen subdirectory `run_e73.sh stage` builds). On 28 Oct
   the lock-in and the fit were **re-run on the box from the same RED with the committed file**: `lockin.json` came
   back byte-identical (sha256 `d29e801f…`), `fit.txt` identical, all five `*-maps.npz` identical, and `fit.json`
   differs only in the input path it records. Every number in this README is therefore a number the committed code
   produces. (The run's own `session.json` records the staged hashes, so the difference is auditable there too.)
4. **Wed 28 Oct — the fit that includes the two prior anchors is post hoc and carries no verdict**
   (`posthoc/prior-anchors.json`, `tools/claims-v3/hlf/posthoc/fit_priors.py`). The frozen `fit_hlf.py` fits E73's
   own points only, with one gain, and that is what the rules are scored on. Putting E63's 0.05 Hz and Q126's
   0.15 Hz into the same fit needs two choices that were made after the data were seen: a **second gain** (the
   camera's absolute gain differs between afternoons — the fit measures 1.075× between them) and a **circular error
   for the pooled anchors** (their registered SEs are measured along the pooled vector; the isotropic SEs from the
   same committed file are used instead, 3.409 and 9.265 mK/W). Three sensitivities are in that file: one gain for
   everything (P1D τ 14.75 s, T_d 1.14 s, still ΔAIC +29 over one pole), the anchors' SEs along the vector, and the
   pooled vector's own 0.05 Hz phase (95.39°) in place of the registered mean-of-lags (99.11°). None changes the
   conclusion.
5. **A note on R6, not a departure.** `analysis/lockin.json`'s per-block `holds` flag is E63's *per-launch* bar and
   reads `false` for `E73-REF3` (20 of 24 launches clean, 0.833). The **registered** R6 gate is the share of
   in-launch *samples* at ≥ 790 MHz and the die mean, and both pass in all five blocks; the per-launch dip count is
   reported without a verdict, exactly as registered, because a per-launch gate fails on the governor's idle-reset
   dip at any load (E63's lesson, which is why A1 exists).
6. The post-hoc fit was run on the Intel with the system python (3.9.6, numpy 1.26.4); the registered reduction ran
   on aifoundry2 (python 3.12.3). Nothing in the registered numbers depends on the Intel.

## Files

| Path | What |
|---|---|
| `session/` | the runner's record: `session.json` (protocol and code hashes, heater and kernel hashes, git head, caps, stop reason, the governor read, `et_who`), `protocol.json`, `launches.jsonl` (every launch, its operand file and its timing), `phases.jsonl` (each phase's planned and realised span: the lock-in's laps), `blocks.jsonl`, `marks.jsonl`, `run.log`, the telemetry `tel.jsonl.gz` (10 Hz: board power, rails, clock, 34 shire sensors), and the recorder's `cam/done.json` and `cam/gaps.jsonl` |
| `red/` | from `reduce_hm.py` (E62's, unchanged): `ffc.json` (every shutter event it found), `meta.json`, `scene.npy` (the idle scene, 192 × 256 °C); and `fpa.npz` from `fpa_trace.py` (per frame: the focal-plane thermistor VTEMP and the header's `fpa_c`) |
| `analysis/lockin.json` | `lockin_hlf.py`: per block the ROI and frame amplitudes per lap, the board step, the registered fundamental, the kept odd harmonics for camera and board, every transfer point H(kf₀) with its lap jackknife, the hold gate, the shutter-phase test, the FPA control |
| `analysis/fit.json`, `analysis/fit.txt` | `fit_hlf.py`: the reference line, the 25-point transfer table, the four model fits with Δχ² = 1 intervals, and the six rules scored |
| `analysis/E73-*-maps.npz` | per pixel, 96 × 128: the complex amplitude at each block's f₀ and its SEs, the in-phase map, the ROI |
| `dips.json` | the one-second clock dips inside launches (`dips_hlc.py`), reported with no verdict |
| `camcheck/` | the 95 s camera-only recording of 15:44 PDT, no card involved: the stream's health and the view's registration against E62 |
| `posthoc/prior-anchors.json` | **post hoc, Wed 28 Oct 2026, no verdict**: the same shapes fitted with E63's 0.05 Hz and Q126's 0.15 Hz anchors included under their own gain, the sensitivities, and the Δχ² = 1 intervals of the group delay and G₀ for the registered E73-only fits ([`tools/claims-v3/hlf/posthoc/`](../../../../tools/claims-v3/hlf/posthoc/fit_priors.py)) |
| `left-on-aifoundry2.sha256` | the sha256 of all 535 files of the run left on the box, paths relative to the lab checkout there |

## Left on aifoundry2, not committed

On aifoundry2, under `build/e73/` of the lab checkout (`sha256sum -c left-on-aifoundry2.sha256` from there checks
every one):

| File | Bytes | sha256 |
|---|---|---|
| `runs/e73-card-1027/cam/cam.p3rec` (the raw camera stream) | 2,848,528,181 | `c96679eee64fb85798b9882dc5af5ef51c6a8ca22d5bc0d58cbf7a61284ce97b` |
| `runs/e73-card-1027-RED/frames.npz` (the reduced cube, 5,201 bins × 96 × 128) | 191,891,769 | `ff778a82f7a4c9691d8be086c9cdeac544e2d3664a3b7c5fbc0abc8ededc77e` |
| `runs/e73-card-1027/tel.jsonl` (the raw telemetry; its gzip is committed) | 17,660,398 | `6785d738a121be1a4fbeb5aaf1ad160ad61c62f3eec7d3ca056442e0cf16309f` |
| `runs/e73-card-1027/cam/status.jsonl` (521 camera health polls) | 227,001 | `0f2734d1ccb6b3e5d65f3bb185b1d760073e6bd48f9d7816fdf1ca318eca16ab` |
| `runs/e73-card-1027/cam/record.log` | 19,618 | `a4827d229565189c0203dddb0d1add8204bba9fa365d314f9df3c44a6bd4041f` |
| `runs/e73-card-1027/logs/` (497 per-launch `.out`/`.err` files, 5.0 MB) | — | in `left-on-aifoundry2.sha256` |

The RED directory also holds its own copies of the session records (`blocks/launches/marks/phases/protocol/session`,
`ffc.json`, `fpa.npz`, `meta.json`, `scene.npy`, `tel.jsonl`) and the ANA directory the analysis outputs; the
committed copies above are byte-identical to them.

## Rebuild

On aifoundry2, from `build/e73/code/` (the frozen copy), or on any machine with numpy and the RED directory:

```bash
python3 reduce_hm.py <RUNDIR> --out <RED>                       # ~2.8 GB of frames -> frames.npz, ffc.json, scene.npy
python3 fpa_trace.py <RUNDIR> --out <RED>/fpa.npz
python3 lockin_hlf.py <RED> --protocol protocol-e73.json --template prereg/e62_bloom_dt.npy \
    --scene-ref prereg/e62_scene.npy --fpa <RED>/fpa.npz --out <ANA>
python3 fit_hlf.py <ANA>/lockin.json --protocol protocol-e73.json --predictions predictions.json \
    --out <ANA>/fit.json --md <ANA>/fit.txt
python3 dips_hlc.py <RED> --out <ANA>/dips.json
# post hoc, on any machine, from the committed fit.json:
python3 tools/claims-v3/hlf/posthoc/fit_priors.py <ANA>/fit.json \
    --predictions tools/claims-v3/hlf/predictions.json \
    --pooled docs/reports/data/2026-10-23-e63-camera-hamming-ladder/posthoc/h3-rails-pooled.json \
    --out posthoc/prior-anchors.json
```

`reduce_e73.sh` in `tools/claims-v3/hlf/` runs the first five in order against one run directory.
