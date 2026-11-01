# V3-HLK: E85 — the thermal camera's view of different kinds of numbers (Q130)

*Pre-registered Sat 31 Oct 2026 (week 44), before the `#community-lab` claim and before the first launch. This
commit freezes the design, the protocol ([`protocol-e85.json`](protocol-e85.json)), the predictions
([`predictions.json`](predictions.json), sha256 `f4cb7198ad21b6f27b2a13c31e9f5f58a4f9c8100442f2b99d75d8380bbee938`, built by [`predict_e85.py`](predict_e85.py) from committed inputs pinned by
sha256), the analysis code ([`lockin_hlk.py`](lockin_hlk.py), which runs E63's `lockin_hlc.analyse_block`
verbatim) and the decision rules. Any change after it goes in Amendments at the end, dated, before the data it
touches.*

**The ask** (the owner, Sat 31 Oct 2026, about 08:40 PDT, Q130): *"… The goal is to collect material for blog
follow-up, fully explain the speed/heat/power issues of multiplying varying kinds of numbers. Run experiments on
aifoundry …"*, and at about 13:15: *"feel free to use more cards"*. In Q130's second workflow this is **E85**
(optional): the thermal camera's view of different kinds of numbers on aifoundry2, after E83 released the card.

**The question.** The board's power meter says the kind of number sets the power: on this card, at 800 MHz, random
fp32 data draws ~48.7 W more than fp32 zeros on the full card, random fp16 ~42.3 W more than fp16 zeros, and int8
over its whole byte range only ~14.1 W more than int8 zeros (E80 and E83's `burst_p800_w`). E63 showed that the
thermal camera behind the card weighs flipped bits: switching E60's top rung against its zero at 0.05 Hz put a
194 mK signal on the back of the board, ~53 mK per watt of fundamental, and a null of equal watts stayed flat. **Does
heat follow the numbers too?** Switch each kind against its own type's zeros at 0.05 Hz, and ask whether the camera
weighs the kinds exactly as the meter does: the same millikelvin per watt for fp32, fp16 and int8 data as for E63's
reference rung, measured in the same session, with the camera's gain drift tracked by the reference.

## Design

**Card and instrument, as they are.** aifoundry2, card 0, under its own governor (65 W / 65 °C, never set; read with
the lock held at the start and end). DVFS 600 / 700 / 800 MHz. The Thermal Master P3 behind the card, recorded on
aifoundry2 from the phone's lossless `/stream.raw.z` by E62's `record_cam.py` (25 fps, 256 × 192, the host's receive
time on every frame). **The camera's settings are not changed** (preset `visualize`, automatic shutter on). Everything
is in raw counts; no absolute temperature is claimed.

**Geometry: E63 amendment A1's, unchanged (also E73's).** 6 minions in each of the 32 shires, **192 minions**, mask
`0xffffffff`. One launch per phase, `--seconds 8.5 --budget 9.5` under `timeout 10`, idled out to a 10 s dwell
(`pad_to_dwell`), so the two arms alternate on a fixed 20 s grid: **0.05 Hz**. E63 session 1 ran 256 minions and
failed its hold gate (39 of 42 launches held: the governor's one-second idle-reset dips, not heat); A1's 192 held
(41 of 42), and E73's five blocks at 192 held 97.7–100% of samples. The task's "800 MHz on a die held below the
thermal test, or E63's 192-core variant if 256 cores dip" is therefore settled by E63's own record: E85 starts at 192
and makes no 256 attempt, which also keeps every earlier 0.05 Hz transfer (E63 A1, E73) at the same geometry. The
heaviest arm, fp32 randn, is predicted at ~39.8 W on the board (E63 A1's lq_h23 arm read 38.6 W) and a die below
60 °C, far from both governor tests.

**Kernel and binaries: the ones E63, E73, E80 and E83 ran.** `sparsity_host --test fma --pattern none --values
file:<tile> --type <type>` from aifoundry2's `build/sparsity_t2` (host sha256 `7adadf4f…`, kernel `990807f4…`).
Hart 0 of each running minion repeats one 16×16 TensorFMA on one tile pair; `file:` reads the raw A then B tile,
1,024 bytes each, in the chosen type's layout.

**The arms** (sets in [`protocol-e85.json`](protocol-e85.json); tiles are Q130(s) revision 2, `kinds.json` sha256
`9586568f…`, the files E80 and E83 measured; E60's `lq` files as E63 ran them):

| set | type | operand | sha256 |
|---|---|---|---|
| `REF23` / `REF0` | fp32 | E60 `lq_h23` / `lq_h0` (E63's top rung and its zero) | `cc18e774…` / `9094a633…` |
| `F32R` / `F32Z` | fp32 | kinds `fp32/randn` / `fp32/zeros` | `34b2add3…` / `e5a00aa9…` |
| `F16R` / `F16Z` | fp16 | kinds `fp16/randn` / `fp16/zeros` | `2ab30f0f…` / `e5a00aa9…` |
| `I8F` / `I8Z` | int8 | kinds `int8/full` (E64's int8 random) / `int8/zeros` | `f5a5f3bf…` / `e5a00aa9…` |
| `F32S90` | fp32 | kinds `fp32/sparse90` (against `F32Z`) | `1ff8d98e…` |

The three zeros files are the same 2,048 zero bytes; each runs in its own type, because a kind is compared with its
own format's zeros.

**The blocks, in this order** (42.0 card-minutes: 40.0 min of blocks and 60 s of idle before and after; cap 44):

| block | arm A vs arm B | laps (warm-up + analysed) | min |
|---|---|---|---|
| `E85-REF1` | lq_h23 vs lq_h0 (fp32) | 6 + 12 | 6.0 |
| `E85-F32` | fp32 randn vs fp32 zeros | 3 + 15 | 6.0 |
| `E85-I8` | int8 full vs int8 zeros | 3 + 18 | 7.0 |
| `E85-REF2` | lq_h23 vs lq_h0 | 3 + 12 | 5.0 |
| `E85-F16` | fp16 randn vs fp16 zeros | 3 + 15 | 6.0 |
| `E85-SP90` | fp32 sparse90 vs fp32 zeros | 3 + 12 | 5.0 |
| `E85-REF3` | lq_h23 vs lq_h0 | 3 + 12 | 5.0 |

**The reference, interleaved.** E63's transfer fell from 59 to 42 mK/W through its hour as the board and the camera
warmed; E73's three reference blocks drifted −44 ± 35%/h. So E63's reference rung pair runs first, in the middle and
last, every kind block sits next to one, and the kinds are read against a line through the three. int8 gets three
more laps than fp32 and fp16 because its signal is the smallest of the three main kinds; fp32 sparse90 (the task's
"if time allows") is the near-null kind: ~0.27 W at 192 minions, ~9 mK predicted, so it tests that the camera sees
almost nothing where the meter sees almost nothing.

**The one code addition: a type per set.** E63's runner takes `--type` from the protocol's heater section for every
launch. [`run_hlk.py`](run_hlk.py) imports `run_hlc.py` and runs it unchanged, wrapping only `_spawn_heater` so that
a launch of a set runs with that set's `type`; it refuses a protocol where one operand file appears under two
types. Each launch's full command line, `--type` included, is recorded in `launches.jsonl` by `run_hlc.py`, and every
`.py` and `.json` in the staged code directory is hashed into `session.json`. [`test_spawn_hlk.py`](test_spawn_hlk.py)
checks the wrapper with a fake `Popen`: all nine sets launch with their own type, and the heater's default is
restored.

## Predictions (frozen)

[`predict_e85.py`](predict_e85.py) → [`predictions.json`](predictions.json) and [`predictions.txt`](predictions.txt),
from committed inputs only, each refused unless its sha256 matches: E80's and E83's `results.json` (each kind's
`burst_p800_w`, the mean of both where both ran it), E63 session 2's `lockin.json`, E63's pooled 0.05 Hz transfer
(Q126, `posthoc/h3-rails-pooled.json`), E73's `lockin.json` and `kinds.json`.

- **Electrical.** A kind's step over its own zeros on 192 minions = (p800_kind − p800_zeros) × 192 / 1024, ±20%
  (E63 measured the rung's step on 256 and 192 minions within 1.5% of linear). The reference rung's step is the mean of
  the five earlier 192-minion top-rung blocks, 4.022 W, ±10%.
- **The board's 0.05 Hz fundamental** is 0.6185 × the step (the mean over six earlier 192-minion blocks: ~8.9 s
  launches in 10 s phases).
- **The camera, absolute** ("E63's measured mK per W"): E63's pooled 52.71 ± 1.98 mK per watt of fundamental at a
  95.4° lag, times the predicted fundamental; band [42.4 × 0.8, 71.1 × 1.2] × fundamental, 42.4–71.1 mK/W being the
  range of the six earlier 192-minion transfers (E63 A1 three, E73 three).
- **The core prediction: the ratio is 1.** Each kind's transfer H_kind (its camera fundamental over its own board
  fundamental) equals the reference line's H at the kind block's time, **R = 1.00** for every kind, and the kind lags the
  power by the reference's phase. Heat is heat: all kinds run on the same 192 minions, so a watt of switching warms
  the back of the board the same whatever numbers made it.

| block | kind | step W (band) | fundamental W | camera mK at 0.05 Hz (band) |
|---|---|---|---|---|
| E85-REF1/2/3 | lq_h23 vs lq_h0 | 4.022 (3.619–4.424) | 2.487 | 131.1 (105.4–176.8) |
| E85-F32 | fp32 randn | 9.125 (7.300–10.950) | 5.643 | 297.4 (191.2–481.5) |
| E85-I8 | int8 full | 2.640 (2.112–3.168) | 1.633 | 86.1 (55.3–139.3) |
| E85-F16 | fp16 randn | 7.938 (6.350–9.525) | 4.909 | 258.7 (166.4–418.8) |
| E85-SP90 | fp32 sparse90 | 0.274 (0.219–0.328) | 0.169 | 8.9 (5.7–14.4) |

Every block holds 800 MHz (≥ 95% of in-launch samples from 1.5 s at ≥ 790 MHz) at a die mean below 60 °C.

## Analysis (registered: [`lockin_hlk.py`](lockin_hlk.py), on `reduce_hm.py`'s output as it is)

1. `reduce_hm.py RUNDIR --out RED` and `fpa_trace.py` (E62's and E63's, unchanged).
2. **E63's lock-in, verbatim**, on every block: `lockin_hlc.analyse_block` with E63's ROI (the warm quarter of E62's
   bloom map, moved with the view if it shifted by more than 2 binned pixels), knobs and seed: a free offset for
   every stretch between shutter events, a 40 s drift spline, per-lap complex amplitudes, the inverse-variance mean,
   the lap-scatter SE, the sign-flip p; the board power through the same lap model; **H = Z / W** with its lap
   jackknife; the board step (each lap's median power in arm A's steady window minus arm B's).
3. **Added per block:** the analysed laps' mid-time; E73's hold measure (share of 10 Hz samples ≥ 790 MHz from 1.5 s
   into each analysed launch, die mean and max); the launches with an idle-reset dip; each arm's steady board level.
4. **The reference line** (E73's `ref_line`): a weighted straight line in time through the three reference blocks'
   |H| and a weighted constant phase. For a kind at time t: **R = |H_kind| / Href(t)**, SE_R = the kind's jackknife
   SE of |H| and the line's SE at t (with its covariance term), each over Href(t), in quadrature.
5. **The camera as a wattmeter** (reported, no verdict): each kind's camera fundamental through Href(t) and the
   session's own fundamental-per-step, read back as a board step in watts, against the meter's.

## Decision rules

1. **E85-R1 seen:** each main kind (F32, I8, F16) has ROI sign-flip p < 0.001 and a lag in (0°, 180°).
2. **E85-R2 heat follows watts:** each main kind's R equals 1 within max(3 SE_R, 0.10).
3. **E85-R3 pooled:** the inverse-variance mean of the three R equals 1 within max(3 SE, 0.05); its SE carries the
   line's error as fully correlated across the kinds.
4. **E85-R4 same lag:** each main kind's transfer phase equals the line's phase within max(3 SE, 15°).
5. **E85-R5 near-null:** SP90's camera amplitude along the reference camera direction equals Href(t) × its own board
   fundamental (projected the same way) within 3 SE. No detection is required.
6. **E85-R6 electrical:** each block's measured step inside its predicted band (scored per block).
7. **E85-R7 reference line:** the three reference |H| on a straight line, worst residual ≤ 3 SE (E73's R2). With
   fewer than three references it is not scored, and R2–R5 use the line through what there is.
8. **E85-R8 hold:** every block ≥ 95% of in-launch samples ≥ 790 MHz and a die mean below 65 °C (E73's R6). A block
   that fails still has its camera numbers scored (the board power feeding H is measured through any dip), flagged.
9. **E85-R9 absolute:** each main kind's ROI amplitude inside its frozen band (E63's mK per W, not drift-corrected).

Reported beside them with no verdict: the transfer of every block, each kind's mK per watt of step, its full-card
equivalent step (× 1024 / 192) against E80/E83's p800 difference, the camera-read step, the spatial correlations
with E62's bloom, the shutter-phase test, the FPA control and the idle-reset dips (`dips_hlc.py`).

**What the design can resolve, said before the data.** E63's and E73's 0.05 Hz blocks at 192 minions read the
reference with an SE of 6–12% per block, and the camera noise per block is ~10–15 mK whatever the amplitude. So
SE_R is expected near 0.08 for fp32 and fp16 randn and near 0.13–0.15 for int8 full (its ~86 mK signal): **R2 can
catch a departure of about 25–30% for fp32 and fp16, and only a gross one, about 40%, for int8.** The pooled ratio
(R3) resolves about 20%. That is what 45 card-minutes buy; a PASS means "equal within those bounds", not "equal".

## Checked before this commit

- **[`selftest_hlk.py`](selftest_hlk.py)** (E63's synthetic camera: a square-wave board power of the measured shape,
  a 15 s lag, a blob, a shutter every 2–12 s with per-pixel steps, a focal-plane drift restarting at each shutter,
  34 mK frame noise), laid out as E85's seven blocks at the predicted steps, with the camera's gain drifting 60 → 45
  over the session, F32 and F16 planted at R = 1 and I8 at R = 2: over six seeds R2 passed F32 and F16 and failed I8
  every time, and the 18 recovered ratios' z-scores had mean −0.38, sd 0.90, max |z| 2.48. A first version planted
  I8 at R = 1.3 and R2 passed it (recovered 1.065 ± 0.135): that is the int8 resolution above, found here, not after
  the data. At half the laps the sign-flip p cannot reach 0.001 (6–7 laps); the protocol's blocks have 12–18.
- **[`test_spawn_hlk.py`](test_spawn_hlk.py):** PASS.
- **The dry run on aifoundry2** (`protocol-e85-dry.json`: REF1, F32, REF2, 5 laps each, no card, the toy sampler, the
  real camera): the pipeline ran end to end; see Dry run below.

## Dry run

Sat 31 Oct 2026, 15:45–15:51 PDT on aifoundry2, `run_e85.sh dry` with `protocol-e85-dry.json` (REF1, F32, REF2, 5 laps
each, 20 s idle either side), the code staged from a copy of this directory (`HLK_SRC`), no card: the runner's dry
mode never starts a heater or a sampler on the device (its toy sampler draws the same watts for both arms, so there
is no electrical step and every H is meaningless by design). It checked the plumbing end to end on the box's
Python 3.12.3 / numpy 1.26.4: the runner (`stop_reason done`, 30 launches, 5.7 min), the recorder (8,502 packets in
340 s, 25.00 fps), `reduce_hm.py` (681 bins, 51 shutter events), `fpa_trace.py`, `lockin_hlk.py` (every block analysed,
the reference line through REF1 and REF2, every rule computed; R7 not scored with two references, as registered) and
`dips_hlc.py` (0 of 30 launches dipped), 13.5 s for the whole reduction. The camera's view against E62's idle scene:
(−1, −1) full-resolution pixels, peak correlation 0.97, template kept. The staged `run_hlc.py`, `lockin_hlc.py`,
`fpa_trace.py`, `record_cam.py`, `reduce_hm.py` and `p3rec.py` are byte-identical to E63's frozen copy on the box
(`build/e63/code`); the heater and kernel hash to `7adadf4f…` and `990807f4…`, and the seven tiles to `kinds.json`'s
and E60's sha256.

## Etiquette and safety

The card is claimed in `#community-lab` with one line after this commit is pushed, and the same post is edited at the
release. Planned card time: the operand check (~1 min) and the session (42 min), under 45 card-minutes. The runner
takes `/run/lock/etsoc-shire0.lock` without waiting, checks for other users before the session and between every
launch, runs one `ettelem` sampler at 10 Hz, starts every launch under `timeout 10` with `--stop-file`, and stops at an
80 °C die or 70 W on two samples. Nothing on the card is set. Raw frames stay on aifoundry2 in `build/e85/runs/`
(gitignored), as E62's, E63's and E73's do; their sha256 go in the data folder.

## Running it (on aifoundry2, from the lab checkout after `git pull --ff-only`)

```bash
bash tools/claims-v3/hlk/run_e85.sh stage                      # build/e85/code + SHA256SUMS
bash tools/claims-v3/hlk/run_e85.sh check                      # host, heater, tiles, card, camera, plan
bash tools/claims-v3/hlk/run_e85.sh tiles build/e85/runs/tiles # after the claim: the operands, byte for byte
bash tools/claims-v3/hlk/run_e85.sh go build/e85/runs/e85-card-1031
bash tools/claims-v3/hlk/run_e85.sh reduce build/e85/runs/e85-card-1031
```

## Files

| File | What |
|---|---|
| `protocol-e85.json`, `protocol-e85-dry.json`, `make_protocol_e85.py` | the session and the pipeline check, and their generator |
| `run_hlk.py`, `start_hlk.sh` | E63's runner plus a type per set; the detached start |
| `tile_check_hlk.py` | the operand check: one `--seconds 0` launch per set in its own type with `--dump-tiles`, compared byte for byte |
| `predict_e85.py`, `predictions.json`, `predictions.txt` | the frozen predictions and rules |
| `lockin_hlk.py` | the registered analysis: E63's `analyse_block` verbatim, the reference line, the rules |
| `selftest_hlk.py`, `test_spawn_hlk.py` | the synthetic check of the analysis and rules; the wrapper's test |
| `run_e85.sh` | stage, check, dry, tiles, go, watch, reduce |
| `figure_e85.py` | added after the run (no new numbers): the data folder's figure, from `analysis/` only; retitled after verification (int8 marked "not detected") |

## Amendments

None. The session ran as registered.

## Results

Added Sat 31 Oct 2026 after the run; everything is in the data folder,
[`docs/reports/data/2026-10-31-e85-camera-kinds/`](../../../docs/reports/data/2026-10-31-e85-camera-kinds/README.md).
One session, 15:54–16:36 PDT, 240 launches, 42.0 card-minutes, `stop_reason done`, the governor read 65 W / 65 °C at
both ends. **8 of the 9 rules pass as registered; R1 fails for int8, so int8's R2, R4 and R9 passes carry no
information.** fp32 randn and fp16 randn warm the die's footprint by 267.6 ± 19.9 and 227.0 ± 13.6 mK at 0.05 Hz,
52.10 ± 3.82 and 50.72 ± 3.21 mK per watt of fundamental. Their ratios to the drift-corrected reference are
0.869 ± 0.118 and 0.923 ± 0.080 (pooled with int8, 0.895 ± 0.086), with the reference's lag. The reference line's own
slope, −29 ± 29 %/h, does not by itself resolve a drift; against a constant reference, post hoc, the ratios read 0.97
and 0.95. int8 full read 64.5 ± 28.3 mK, p 0.054, in the session's noisiest shutter block (R1 FAIL, not detected);
fp32 sparse90 read 29.4 ± 22.3 mK for its 0.24 W, as expected. Post hoc, 20 more synthetic seeds show the analysis
reading R about 4% low with SEs 15–30% small (no verdict moves).

## Correction after verification (Sat 31 Oct 2026)

The pre-registered sentence "Nothing on the card is set" (Etiquette and safety, above, left as it was frozen) missed
one write. The runner is E63's `run_hlc.py`, unchanged, and it starts its sampler as
`ettelem sample --every-ms 100 --reset-ms 1000`. That sends the SP a statistics reset about once a second, and the SP
passes each one to the PMIC as the PMIC's own statistics reset (0x47; `tools/ettelem/ettelem.cpp`, `resetStats`).
E85's session sent it 2,205 times. No governor, TDP, threshold, clock, card reset, PCIe, driver or firmware command was
sent. Whether the reset counts as PMIC work under Q130 is for the orchestrator and the owner to rule. Post hoc, the
clock excursions cluster just after the resets. The data README's
[Corrections after verification](../../../docs/reports/data/2026-10-31-e85-camera-kinds/README.md#corrections-after-verification-sat-31-oct-2026)
covers this (C1, C9) and the other corrections. A later camera run on this tool should drop `--reset-ms`, as `kspeed`
does, or pre-register it, and should run a ~1 min smoke run under the claim before `go` (C7).
