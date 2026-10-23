# V3-HLC: the camera half of the Hamming ladder (E63, Q122)

*Pre-registered Fri 23 Oct 2026 (week 43), before the first card pass. This commit freezes the design, the
predictions, the analysis code and the decision rules; any change after it goes in Amendments at the end,
dated, before the data it touches.*

**The ask** (the owner, Fri 23 Oct 2026): *"run the camera half of the Hamming ladder on aifoundry2. This is E-T10
of the 26 Sep camera plan, with E60's rungs in place of patterns. … Reuse E60's operand files (tools/claims-v3/hl)
and E62's camera tools (tools/claims-v3/hm). Switch the highest rung aifoundry2 can hold at 800 MHz against its zero
at about 0.05 Hz, with on-windows of 9.5 s or less and at least 5 minutes per rung. Record raw frames with the switch
times logged, and add a null run (equal watts, same place). In E62 the shutter fired every 8–10 s, so plan around
it."*

**The question.** E60 weighed a flipped operand bit with the board's power meter: on the quiet ladder `lq` (A = 1.0,
B alternating every cycle between b and b with its low h mantissa bits flipped) one flipped bit costs ~117 fJ at
0.52 V, and the rungs climb from +0.6 W to +12.3 W over the zero on a 600 MHz card. E62 showed that the thermal
camera behind aifoundry2's card sees *where* the work runs. This experiment asks whether the camera can weigh the
flips too: does switching the top rung against its zero, at a fixed clock, put a heat signal on the back of the
board that a lock-in can read, how many millikelvin per watt, and does a null of equal watts in the same place stay
flat? E-T10 of the 26 Sep plan ("make every image a wattmeter") with the ladder's rungs in place of its eight
patterns.

## Design

**Card and instrument, as they are.** aifoundry2 (governor-free: 600 MHz idle, 800 MHz busy below a ~65 °C die),
nothing changed on it. The Thermal Master P3 behind the card, recorded on aifoundry2 from the phone's lossless
`/stream.raw.z` by E62's `record_cam.py` (25 fps, 256 × 192, 1/64 K counts, the host's receive time on every
frame). **The camera's settings are not changed**: preset `visualize`, automatic shutter on, so the public live page
stays as it is. Everything is computed in raw counts; no absolute temperature is claimed.

**Kernel and operands: E60's, unchanged.** The Horace kernel (`sparsity_host --test fma --type fp32 --pattern none
--values file:<tiles>`): hart 0 of each running minion repeats one fp32 TensorFMA on one tile pair, 546 cycles per
op. Operands are E60's own files in `build/hl-gen2/tiles/` (sha256 in `session.json`): `lq_h23` (the top rung,
94,208 designed B bit flips per op per minion), `lq_h0` (its zero) and `lq_h8` (a middle rung, 32,768). The heater
binary is E62's on this card, `build/sparsity_t2`, with `--kernel` spelled out; its `file:` path is the same code
(both builds carry it) and its kernel is byte-identical to `build/sparsity`'s, which E60 ran these files through
(sha256 `990807f4…`). `tile_check.sh` proves it before the session: one short launch per operand with
`--dump-tiles`, compared byte for byte.

**The rung, and why 256 minions.** At the full card (E60's 1,024 minions) the zero alone draws 53.6 W on aifoundry2
at 800 MHz (E60, a 4 s run from 58 °C), +31 W over idle. Switched for minutes, that heats the die past the
governor's step: E62's 192-hart blocks sat at 43 W and a 63 °C die and held 800 MHz on 99% of samples, and the
clock stepped once the die mean reached 65 °C. So the ladder runs on **8 minions in each of the 32 shires (256 minions,
mask 0xffffffff)**, the same spread over the die as E62's bloom, where the alternation of lq_h23 and lq_h0 is
predicted at ~40–42 W on average and a 61–62 °C die: the top of the ladder, **lq_h23, holds 800 MHz**, so it is the
highest rung. The rule that checks it is the hold gate below.

**The switching.** One launch per phase, `--seconds 8.5 --budget 9.5` under `timeout 10` (a device hold of about
8.6–9.3 s, the on-window, never over 9.5 s), each phase idled out to its 10 s dwell (`run_hlc.py`'s `pad_to_dwell`), so
the two arms alternate on a fixed 20 s grid: **0.05 Hz**. The idle tail is the same in both arms, so it lands on 2f.

**The blocks, in this order** (`protocol.json`; 32.0 min, 180 launches):

| Block | Arms (first half of each lap, second half) | Laps: warm-up + analysed | Analysed |
|---|---|---|---|
| `E63-TOP` | lq_h23, lq_h0 | 9 + 21 | 7.0 min |
| `E63-NULL` | ones, pi (E60's anchors: 53.27 and 53.30 W on the full card) | 3 + 18 | 6.0 min |
| `E63-MID` | lq_h8, lq_h0 | 3 + 18 | 6.0 min |
| `E63-TOP2` | lq_h23, lq_h0 | 3 + 15 | 5.0 min |

60 s of idle before and after. **The null is equal watts in the same place**: the same 256 minions, the same kernel and
launch rhythm, two operand sets that draw the same power (E60, full card, 800 MHz: 53.27 ± 0.06 and 53.30 ± 0.40 W),
so its arms differ in what they compute and not in watts. TOP2 brackets MID with TOP, so slow drift in the camera's
response cannot fake the ratio.

**The shutter, planned around.** In E62 the automatic shutter fired every 4–10 s under load (141 and 298 events in two
sessions, median step 14–28 mK, 1–3 K at the 99th percentile). Each event replaces the camera's offset map, so a
pixel's level jumps at each one; between events the offset is constant and the camera's own drift is smooth. The
registered analysis therefore never bridges a step: it gives **every stretch between two shutter events a free
offset** and reads the signal only from the variation inside the stretches (below). With events at random phases of
the 20 s cycle this costs signal, not bias; their phase is tested (Rayleigh) in case they lock to the load. The dry run
before this commit (12:49–12:53 PDT, camera only, no card) saw 33 events in 230 s with the card idle, so the shutter
fires every ~7 s whatever the load does.

**Checked before this commit.** `test_lockin_hlc.py`: on synthetic sessions with shutter steps of up to 3 K, a
focal-plane drift that restarts at each event and 34 mK frame noise, the top rung's planted amplitude comes back within
its SE (z-scores over 6 components: mean +0.03, sd 1.19), the null stays flat (p 0.57, 0.40, 0.22), and a bridged and an
unbridged copy of the same data give the same numbers. On E62's own constant-power blocks (session 2), analysed at
0.05 Hz, the ROI read 4.4 ± 3.8 (NULLAA), 8.3 ± 10.1 (WE42), 2.5 ± 4.5 (NS42) and 10.8 ± 8.0 mK (NULLGEO, 8 laps),
all p ≥ 0.25. The dry run went through the runner, the recorder, `reduce_hm.py`, `fpa_trace.py` and the lock-in
(25.00 fps, no drops; the view has not moved since E62: shift 0, 0, correlation 0.98).

## Predictions (frozen with this commit)

- **Electrical** (E60 scaled to 256 minions; the lq ladder on aifoundry2 at 800 MHz runs 1.97× aifoundry3's at
  600 MHz, from h8 − h0): the board's step between arms **TOP +6.0 W** (4.5–7.5), **MID +1.6 W** (1.1–2.2), **NULL
  0.0 W** (±0.1). Per designed flipped bit, TOP ~170 fJ and MID ~130 fJ (the ladder bends up: high mantissa bits
  cost more), at 0.618 V.
- **Hold:** die mean 61–62 °C in TOP, 800 MHz in every analysed launch after its ramp.
- **Thermal:** E62's bloom (all 32 shires, +44.6 W) rises with a ~15–20 s time constant; through it the camera's ROI
  reads **~31 mK per watt of fundamental at 0.05 Hz, lagging the power by ~84°**. So **TOP's ROI fundamental ~110 mK**
  (50–400), **MID ~30 mK**, **NULL 0**. The same code on E62's constant-power blocks at 0.05 Hz read 2.5–10.8 mK with
  SE 3.8–10.1 mK (all p ≥ 0.25): the noise floor is **~4–5 mK per block**, so TOP's SNR ~20–30, MID's ~6–8.
- **Shape:** TOP's in-phase map has the bloom's shape (correlation with E62's bloom map > 0.5), and the capacitor
  field's low-emissivity tops under-report it (the high-passed map correlates positively with the bloom's high-pass).
- **The camera body does not breathe at f** (its focal-plane readings show no 0.05 Hz component, p > 0.01), and the
  shutter events fall at random phases (Rayleigh p > 0.01).

## Analysis (registered: `lockin_hlc.py`, run on `reduce_hm.py`'s output as it is)

1. `reduce_hm.py <RUNDIR> --out RED` (E62's, unchanged): 0.5 s bins of 2 × 2-binned frames (96 × 128) in mK on the
   host clock, the shutter events it finds, the runner's files. `fpa_trace.py` adds the focal plane's own readings.
2. **The ROI** is the warmest quarter of E62's bloom map (`prereg/e62_bloom_dt.npy`, ≥ its 75th percentile, 3,072
   binned pixels): the die's footprint as this camera sees it, from another session. If today's idle scene is
   shifted from E62's (`prereg/e62_scene.npy`, cross-correlation of the capacitor pattern) by more than 2 binned
   pixels, the map moves with it.
3. **The model**, per pixel and for the ROI mean, over a block's analysed laps:
   `y(t) = c_stretch(t) + spline(t) + Σ_laps [a_c sin φ + b_c (−cos φ)] + third-harmonic terms + noise`,
   φ = 2π (t − lap start)/lap length. Free offsets per stretch between shutter events (bins from 0.5 s before to
   1.0 s after an event, bins with under half the usual frames, and stretches under 2 s are dropped); cubic B-splines
   every 40 s for the camera's continuous drift; the third harmonic shared. Per lap z_c = a_c + i b_c: a signal
   lagging the switch by θ has phase θ. The block's amplitude Z is the inverse-variance-weighted mean of the laps
   (weights from the design alone), its SE from their weighted scatter, its p from flipping the signs of whole laps
   (exact up to 16 laps, else 20,000 draws).
4. **The electrical half on the same grid:** the board power (10 Hz, `tel.jsonl`) through the same lap model, giving
   its fundamental W; and the step, each lap's median power in arm A's launch minus arm B's, from 2.0 s after the
   launch starts to 0.3 s before it ends. **The transfer H = Z / W** (mK per W of fundamental) and its phase, the
   camera's lag; jackknife over laps.
5. **The hold gate:** a launch holds when ≥ 95% of its 10 Hz samples read 800 MHz from 1.5 s after its start to its end
   (the clock ramps from 600 MHz in the first ~0.7 s); a block holds when ≥ 95% of its analysed launches hold.

## Decision rules

1. **The camera weighs the top rung:** TOP's ROI amplitude has sign-flip p < 0.001 and lags the power by 0–180°
   (warming that follows the rung). Otherwise the camera cannot weigh these flips at this load: reported as a
   negative result.
2. **At 800 MHz:** TOP holds (the hold gate). If it does not, the run is repeated at 6 minions per shire under an
   amendment written before that run, and this one is reported as it is.
3. **The null is flat:** NULL's ROI amplitude along TOP's phase is within 3 SE of what NULL's own measured power
   predicts through TOP's transfer, and its sign-flip p ≥ 0.01. A null that fails voids rules 1, 4 and 5: the
   pipeline would be making signal.
4. **The image is a wattmeter:** MID's camera amplitude over TOP's (along the tops' phase; TOP and TOP2 averaged)
   equals MID's power fundamental over TOP's within 3 SE or 10%, whichever is wider.
5. **It repeats:** TOP2's transfer equals TOP's within 3 combined SE.

Reported beside them, with no verdict: the whole-frame amplitude; the transfers and lags; the per-flip electrical
prices; the camera amplitude per 10¹³ flips per second; the spatial correlations; the camera's focal-plane readings at
f; the shutter-phase test; and a plain lock-in on `reduce_hm.py`'s bridged frames (no stretches), so the reader can
see what the stretches buy.

## Etiquette and safety

The card is claimed in `#community-lab` before the first launch and released after. The runner (E62's, see
`run_hlc.py`'s header for the two additions) takes `/run/lock/etsoc-shire0.lock` without waiting, checks for other
users before the session and between every launch (another user ends the session), runs one `ettelem` sampler at
10 Hz, starts every launch under `timeout 10` with `--stop-file`, and stops at an 80 °C die or 70 W on two samples.
Raw frames stay on aifoundry2 in `build/e63/runs/` (gitignored), as E62's did.

## Running it (on aifoundry2, from `build/e63/code/`, a gitignored copy of this directory plus `hm/record_cam.py`,
`hm/p3rec.py` and `hm/reduce_hm.py`)

```bash
bash tile_check.sh ../runs/tiles-<date>                    # the operands come back byte for byte
python3 run_hlc.py --protocol protocol.json --list          # the plan; touches nothing
bash start_hlc.sh ../runs/<session>                         # the card session, detached
python3 reduce_hm.py ../runs/<session> --out ../runs/<session>-RED
python3 fpa_trace.py ../runs/<session> --out ../runs/<session>-RED/fpa.npz
python3 lockin_hlc.py ../runs/<session>-RED --protocol protocol.json --template prereg/e62_bloom_dt.npy \
    --scene-ref prereg/e62_scene.npy --fpa ../runs/<session>-RED/fpa.npz --out ../runs/<session>-ANA
```

## Files

| File | What |
|---|---|
| `protocol.json` | the session: sets (mask, minions, operands), blocks, laps, heater, safety |
| `run_hlc.py` | E62's runner plus per-set `--values` and `pad_to_dwell` (82 changed lines; everything else E62's) |
| `tile_check.sh`, `tile_compare.py` | the pre-session operand check |
| `start_hlc.sh` | starts the session detached (as E62's `start_e62.sh`) |
| `lockin_hlc.py` | the registered lock-in, transfer, hold gate and decision rules |
| `test_lockin_hlc.py` | synthetic sessions with planted signals, shutter steps and drift: recovery, null, coverage, blindness to per-stretch offsets |
| `fpa_trace.py` | the camera's focal-plane readings per frame |
| `prereg/e62_bloom_dt.npy`, `prereg/e62_gain.npy`, `prereg/e62_scene.npy` | E62 session 2's bloom map, gain map and idle scene (the ROI, the shape, the registration) |

## Amendments

**A0, Fri 23 Oct 2026, 12:56 PDT** (before any launch): `tile_check.sh` resolved its output directory after changing
to the tree root, so a relative path failed every redirection and no heater ran (its first call, 12:55). It now
resolves the output directory and its own directory to absolute paths first. Nothing else changes.

**A1, Fri 23 Oct 2026, 13:08 PDT** (written during session 1's NULL block, from telemetry only; no camera frame has been
reduced or looked at): **rule 2 failed in session 1.** In `E63-TOP`, 3 of the 42 analysed launches (#21 and #53,
lq_h23; #56, lq_h0) dropped to 600 MHz for 1.0–1.5 s, each 7.2–7.3 s after the launch started, the SRAM rail stepping
830 → 704 mV and back up through 700 MHz: 39 of 42 hold, under the registered 95%. The die read 56–57 °C and the PMIC
55–57 °C at every dip, so it is not the governor's 65 °C thermal step. As rule 2 directs, **the run is repeated as
session 2 at 6 minions per shire** (192 minions, `protocol-A1.json`: every set's `per_shire` 8 → 6, `harts` 256 → 192;
nothing else changes), right after session 1. Its predictions scale with the minions: TOP's board step ~4.1 W (3.4–5.6),
MID's ~1.2 W, the camera ×0.75. Session 1 runs to its end as registered and both sessions are reported, each scored by the
same five rules. If session 2's hold gate fails too there is no third session: the dips are then described (when in a
launch, which arm, at which load) as exploratory, and the camera numbers stand with the dips inside them, since the board
power that feeds the transfer is measured through them.

## Results

(after the run)
