# ablb: V3-ABL-B (PLAN3 §2, suggested E39)

Sparse-compute energy configurations (E3) and TenB streaming (E2), strict start, 5 s runs. Registered on aifoundry2
and aifoundry3; since 25 Sep also run on aifoundry1's two cards (section "Four cards"). Registered items: ABLB-2a,
2b, 2c, 3ab, 3c, 3d, 3e, 3f, 3g (16 claims).

## What a pass does

`bash tools/claims-v3/ablb/block.sh <pass>` runs one shuffled block (block index pass - 1) of the 18 configurations
in `v3-energy.cfg`. It uses the shared patched runner `../abla/ablrun.sh`; see `../abla/README.md` for the per-run
sequence: wait for the card, approach, re-check, `hold10` launch, and the sampler for the block.

- **Configurations.** The 11 CONFIGS of workloads/sparsity/run_energy.py, with arguments copied unchanged and checked
  against the file. Then gemv-dense-0. Then E2's six: int8 ones and int8 randn, each in L1 and with `--b-stream`, and
  fp16 randn in L1 and with `--b-stream`.
- **Start.** A governor-free card (aifoundry2, aifoundry1-c0, aifoundry1-c1) heats to 84 C and launches at 80 C.
  The pinned aifoundry3 heats to 57 C and launches at 55 C.
- **Seeds.** `--seed` is block + 1, so blocks 1-2 draw new x vectors for gemv; the plan widened the layer bands for
  this.

`--smoke` (`ablb-smoke`) holds the card for about 30 s (about 45 s on a governor-free card when the die starts below 76 C:
it first runs lib.sh's `heat_to 76`, before its sampler opens the management node). It fires one heater burst, then
does 3 s runs of gemv-dense-0, fma-rowmask, int8_randn_tenb and fp16_randn_tenb. It also runs int8 and fp16
`--b-stream` on the host's default small-integer operands (`int8_chk_tenb`, `fp16_chk_tenb`). Those are the only
operands whose results the host checks, because `--b-stream` had only run on silicon with fp32. The host's result
names are `both`, `math`, `prm-literal`, `wrong` and `unchecked` (main.cpp checkC; there is no `exact`). fp32/fp16
sums are checked only below 2^24, so the long timed fp16 launches print `unchecked`, while the 20,000-iteration
calibration launch is checked. `ablcheck.py --smoke` therefore fails the smoke unless each `*_chk_*` run has at least
one checked launch (`both`, `math` or `prm-literal`) and none `wrong` (the note says `CHECK-FAILED=` otherwise).

Data per pass: `$DATA_ROOT/ablb/p<N>/`, with the same files as abla.

## Card minutes per pass

| | aifoundry2 | aifoundry3 | aifoundry1-c0, aifoundry1-c1 |
|---|---|---|---|
| per pass (18 runs of 5 s) | ~19 min (~64 s start to start) | ~10 min (~31 s) | ~19 min each (aifoundry2's protocol; unmeasured heating and cooling) |
| 3 passes (plan: 59 / 30) | ~57 min | ~29 min | ~57 min each |
| safety cap per block | 35 min | 25 min | 35 min |

## What is dropped, and why

The rules are the same as abla's (`../abla/ablcore.py`). For the registered outcome a run is dropped if a launch is
not ok, it has no timed launch, the telemetry has a gap, or any mhz.minion sample in [t0-2 s, t1] is not 600; the
all-cards outcome uses the busy rule (only samples in [t0+0.3 s, t1] must be 600; see ../abla/README.md "Four cards"). The plan registers no dropout
rule for this experiment, so the metric is analyze_ablation.py's p80 - p_before ("dyn") as it is. Paired items use
only blocks in which both runs are kept. A pass 4+ fills blocks up to the registered 3. Fewer than 3 blocks on a
card gives INSUFFICIENT.

## Deviations from the plan's commands, with reasons

- **One invocation of 3 blocks becomes 3 passes** (block length). Paths are here instead of `build/v3abl/...`.
  Runner changes are as in abla.
- **The config has 18 lines.** The plan says "the 12 run_energy.py CONFIGS", but it lists 11, and
  run_energy.py has 11. With gemv-dense-0 and E2's 6 lines that makes 18, the plan's count.
- **sys_emu pre-check.** The plan's command, `--sysemu --test fma --type int8 --pattern none --values randn
  --b-stream ...`, cannot show exactness. The host checks results only for the default small-integer operands; with
  any `--values` it prints `unchecked` (workloads/sparsity/host/main.cpp, testFma: `rawValues`). The operator's check
  must omit `--values`:
  `build/sparsity/host/sparsity_host --sysemu --test fma --type int8 --pattern none --b-stream --shires 0x1 --per-shire 1 --iters 10`
  and the same with `--type fp16`; each launch must print `"result":"both"` or `"math"` (not `wrong`; with
  `--iters 10` nothing reaches 2^24, so nothing is `unchecked`). The smoke adds the same check on silicon.
- **Host flag.** run_energy.py passes `--budget 8`. The runner does not, but 8 s is the host's default on silicon.

## Readings of the registration

- **ABLB-2a.** The check covers every timed launch of every kept run, against the bands: L1 fp16 546.0 +-0.1, L1 int8
  318.0 +-0.1, TenB fp16 529 +-2, TenB int8 265-300. The clause "identical on the two cards within 0.5 cycle" is
  applied to TenB int8, which is the sentence it closes, using card means. Cross-card differences are reported for all
  six. Both cards inside the bands but TenB int8 differing by more than 0.5 gives CARD-DIFFERENT.
- **ABLB-2b.** Within-block paired TenB - L1, 99% t (df 2), for int8 randn and int8 ones. Both must exclude 0,
  positive, on a card. fp16 is reported only.
  - The "kernel" clause needs V3-MMB's pass-level mmbench int8 above-idle values, passed as `--mmb-values
    {"aifoundry2": [...], "aifoundry3": [...]}`. The test is Welch, one-sided alpha 0.01 (the lower end of the
    two-sided 98% interval) > 10 W on each card. Without the values it says "pending V3-MMB".
- **ABLB-2c.** For the aifoundry3 band, 0.92 x the aifoundry2 mean +- 1 W. On each card the 99% interval must exclude
  0 and the mean must lie in the band.
- **ABLB-3c.** The x value is nnz_a / a_elems x (rows on in row_mask) / 16, as the page's fit. It comes from each
  run's first launch record, so it follows the seed. The slope passes if its 99% t (df 2) excludes 0 and its mean is
  inside the band. rms is that of the line through the block-mean points, as the page's 0.33 W was.
- **ABLB-3e.** above-idle uJ per layer = dyn / (sum(iters) / (t_end - t_start)) x 1e6. Board uJ uses p80 and is stated
  with the die temperature. The outcome is PASS when the aifoundry3 means are in their bands and aifoundry2 / aifoundry3
  is in 1.08 +- 0.15, otherwise FAIL. It is never CARD-DIFFERENT, as registered.
- **ABLB-3f, ABLB-3g.** "Excludes 0" means excludes 0 with the predicted positive sign.

## Four cards (25 Sep 2026)

As V3-ABL-A (../abla/README.md "Four cards": parameters by `GOV_FREE`, aifoundry1's cards take aifoundry2's targets,
cap and leakage slope; the busy clock rule; the idle clock recorded; the per-card card check on aifoundry1; the
REGISTERED outcome unchanged from aifoundry2 and aifoundry3, plus `all_cards`). Items on aifoundry1's cards:

| item | on aifoundry1's cards | idle state |
|---|---|---|
| ABLB-2a cycles per op | tested (same bands); "identical on the cards within 0.5 cycle" becomes the spread of all tested cards' TenB int8 means <= 0.5 | none |
| ABLB-2b TenB - L1 | tested (paired, same rule); the kernel clause per card when `--mmb-values` holds that card | cancels |
| ABLB-2c int8 L1 above idle | REPORTED (a2 9.5-10.5 W; a3 0.92 x a2) | absolute |
| ABLB-3ab dense/zero saving | tested (0.80-0.92 on each card); watt bands informational (aifoundry2's) | absolute |
| ABLB-3c six-point line | REPORTED (slope bands per card) | cancels (slope) |
| ABLB-3d row mask | tested (0.7-1.5 on each card) | cancels |
| ABLB-3e uJ per layer | REPORTED with the ratio to aifoundry3; the joint a2/a3 check stays as registered | absolute |
| ABLB-3f gating alone | tested | cancels |
| ABLB-3g zeros vs spin | tested | cancels |

When aifoundry1-c0's idle bracket is in its low-power state (300 MHz / 398 mV; after a launch it can also idle at
600 MHz, so the state may differ from run to run) the absolute items include the step between that state and 600 MHz:
the dense/zero saving, for instance, falls because both powers carry it; the item's `idle_note` says so. The paired
items cancel the step only between runs that idled in the same state; when a card's runs idled in more than one state
(`idle_mixed_on`), `by_idle_state` gives the item on each state's runs alone (reported, not deciding).

## How to reduce

    python3 tools/claims-v3/ablb/reduce.py --data <dir with one directory per card> --out ablb.json [--mmb-values mmb.json] \
        [--expect aifoundry2,aifoundry3,aifoundry1-c0,aifoundry1-c1]

Output: an item list (registered fields, plus `all_cards` and `reading_all_cards`), plus `ablb.runs.json` with every
run. On the committed 18 Sep aifoundry3 energy runs (two
passes, so INSUFFICIENT) it reproduces the page: dense 17.26 W vs 17.34, zero 2.17 vs 2.37, slope 14.98 vs 14.83, and
67 / 17.5 / 6.8 uJ per layer vs 70 / 19 / 7. The small gaps come from p_before against the page's global idle
median. It was also tested on synthetic pred / shift / off600 + replacement / partial sessions (validate3/drv/ablb/)
and on synthetic four-card sessions (validate3/fourcards/ablb/: all hold; aifoundry1-c0's idle state differs; a card
missing; validate3/fourcards/review/syn/ablb/mixed: c0's runs alternating between the two idle states), and on
aifoundry2's real passes p1-p2, where its registered output is identical to the two-card reducer's.
