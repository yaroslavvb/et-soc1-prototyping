# abla: V3-ABL-A (PLAN3 §2, suggested E38)

Tensor-unit energy by operands, precision, structure and active minions, strict start, 7 s runs, both cards.
Registered items: ABL-T1..T8 (a Bonferroni family of 19 sub-tests per card), the EM4 rider of T5, ABL-R, ABL-EM4c,
ABL-EM4d (60 claims). This directory also holds the runner and reduction core shared with `ablb` and `x5`.

## What a pass does

`bash tools/claims-v3/abla/block.sh <pass>` runs one shuffled block of the 23 configurations in `abl_a.cfg`. The
config is the plan's x1.cfg (19 lines, unchanged) plus fp16_zeros, fp16_ones, int8_zeros and int8_ones from
tools/ettelem/ablation.cfg. Block index = pass - 1. The shuffle is `random.Random(block + 11)`, as in the original
runner, and so are the seeds (`--seed block + 1`). Structured tiles use seed `(block % 2) + 1`, so passes 1-4 use seeds
1, 2, 1, 2.

1. `others_present && exit 3`, `block_begin abla <pass>`. The block then hashes the shared runner, this directory, the
   host binary and its source, and PLAN3.md into `code.sha256`.
2. It checks the 12 structured tiles against `tiles.sha256` (committed copies; aifoundry3 needs the rsync). A mismatch
   fails the block before any launch.
3. `abl_session` in `ablrun.sh` (the patched run_ablation.sh) first waits until the et_soc1 use count is 0 (nobody
   holds the card; at most 15 min, else exit 3), starts the 10 Hz sampler with `start_sampler`, and records the use
   count with only the sampler open (`use_count_sampler` in session.json; the plan expects 1). Then, for each
   configuration:
   1. It waits while the card is held by someone else: the et_soc1 use count is above the sampler's own, or
      another user's device process is running. The wait is capped at 15 min, after which the block fails with exit 3.
   2. It approaches the launch temperature. aifoundry2 heats to >= 84 C with 2 s fp32-randn bursts under hold10, then
      idles until the die reads <= 80 C. aifoundry3 does the same with 60 / 55 C. Before every burst it checks the
      card again, and stops the approach (wait, then approach again) if someone else took it; it never heats blind:
      five sampler reads without a die temperature stop the block (exit 1, "sampler lost").
   3. It checks the card again. If the card was taken during the approach, it waits and approaches again.
   4. It runs `hold10 build/sparsity/host/sparsity_host <args> --seconds 7 --seed <s>`. The host's own `--budget`
      (default 8 s) also applies.
4. It waits 20 s (not when someone else is waiting for the card), stops the sampler with SIGTERM, and gzips the
   telemetry. `ablcheck.py` then writes `check.json` and
   the block note, which gives runs kept, failed and off-600, and dropped samples.
5. `block_end ok` if the session completed and at most 2 runs failed. Otherwise `block_end fail`, with exit 3 when
   someone else held the card mid-block.

Files per pass (`$DATA_ROOT/abla/p<N>/`): telemetry.jsonl.gz, runs.jsonl (block -9 = heater bursts), starts.jsonl
(start temperature, approach time, heater bursts, whether the preheat was reached, seed, time waited for other users),
ends.jsonl (host exit code), order.<block>, config.cfg, session.json, host.log, check.json, tiles.check,
code.sha256, block.json.

`--smoke` (`abla-smoke`) holds the card for about 20 s (up to ~35 s on aifoundry2: it first runs lib.sh's
`heat_to 76`, before its sampler opens the management node, so the smoke also starts on a warm die). It starts the
sampler, fires one heater burst, then does 3 s runs of m_negzero (reads a structured tile on this host), int8_ones,
fp16_zeros and spin. `ablcheck.py --smoke` then
requires every launch to be ok and every telemetry field the reducers read to be present, and prints cycles/op.

## Card minutes per pass

| | aifoundry2 | aifoundry3 |
|---|---|---|
| per pass (23 runs) | ~26 min (committed strict sessions: 66-69 s start to start) | ~13 min (E20: 33 s start to start) |
| 4 passes (plan: 115 / 65) | ~105 min | ~53 min |
| safety cap per block (`ABL_CAP_S`) | 45 min | 30 min |

Schedule `abla 1` .. `abla 4` as separate queue lines, at least 30 min apart with other experiments between them
(PLAN3 §2.13).

## What is dropped, and why

`ablcore.py` decides which runs are kept. It drops a run when:

- a launch did not print `ok`, or there is no timed launch (host failure, or killed by timeout 10);
- the telemetry does not cover the windows (under 5 samples in seconds 1-3, or under 3 before the launch);
- any `mhz.minion` sample in [t0-2 s, t1] is not 600. The plan says "any sample": this window covers every sample the
  metrics read, including the pre-launch idle that p_before uses.

Power samples more than 2 W below the median of seconds 1-3 are removed from p_early. This is the registered dropout
rule, and the count is reported. A pass whose block.json is not `ok` is ignored. Dropped runs are replaced from later
passes (5, 6, ...) up to the registered 4 per configuration. This is the plan's "dropped and re-run": if a pass has
off-600 runs, run `abla 5`. Fewer than 3 kept runs of a configuration on a card gives INSUFFICIENT.

## Deviations from the plan's commands, with reasons

- **One invocation of 4 blocks becomes 4 passes.** This keeps a block at or under ~35 min so the queue can
  interleave. The shuffles and seeds are the same as the one-invocation runner.
- **Paths.** The plan has `build/v3abl/run_ablation_v3.sh`, `build/v3abl/abl_a.cfg` and the data in `build/v3abl-a`.
  Here they are `tools/claims-v3/abla/ablrun.sh` (functions, not a script), `abl_a.cfg`, and
  `build/claims-v3/<card>/abla/p<N>/`. The runner works from `$V3_ROOT`, set by lib.sh, never from its own location.
- **Sampler.** The original runner starts its own `ettelem sample --seconds 14000` and kills it on EXIT. This runner
  uses lib.sh's `start_sampler` (first-line wait, retry, drain) and `stop_sampler` (SIGTERM only). Its duration is
  the block cap + 900 s, so a last run that starts just before the cap (its approach can take 60 bursts + 600 s of
  idle) cannot outlive the sampler; the sampler is stopped with SIGTERM when the session ends.
- **Launches.** Every launch goes through `hold10`. Timeout 10 is the plan's patch; it was secs + 5.
- **Safety stops the original lacked.** The block stops if the sampler is dead or its last line is more than 5 s old
  (checked before each heater burst and every 5 s while idling), or if the block cap is reached.
- **Other-user check.** The plan's patch waits while the use count is > 1 before each run. This runner requires the
  count to be 0 before its sampler starts and uses the count measured with only its sampler open as the "1" (if
  ettelem held two handles, a fixed 1 would make every run wait 15 min and the block exit 3; session.json records
  it). It also counts other users' device processes, repeats the check before every heater burst and after the
  approach, and caps the wait at 15 min.
- **Heater bursts.** They use the run host, as the original runner and the plan's commands do. That is
  build/sparsity/host/sparsity_host, not lib.sh's HEATER (sparsity_t2 on aifoundry2). On aifoundry2 the two binaries
  are builds of the same workloads/sparsity sources; their Constants.h differ only in the kernel ELF path.
  lib.sh's `heat_to 76` is not called. The approach already heats to >= 84 C and launches at 80 C, with the sampler
  as the only opener of the management node.
- **x1_predictions.json.** It is copied here, and reduce.py checks its sha256 (9533af32...). PLAN3.md's hash goes into
  every block's code.sha256.
- **Reduction.** The plan's `analyze_ablation.py` + `x1_reduce.py` are implemented in `ablcore.py` + `reduce.py`.
  x1_reduce.py did not exist; validate3's pt-spatial x1_reduce.py is a different experiment. On the committed 21 Sep
  session, ablcore reproduces analyze_ablation.py's p80, p_before, p_early, t_early and work rate exactly (max
  difference 0).

## Readings of the registration (no new freedom; each choice is stated)

- **Metric.** switching = p_early' - leak x (t_early - launch) - p_before, with the dropout rule. aifoundry2 uses
  0.81 W/C at 80.9 C and aifoundry3 0.55 W/C at 55.8 C.
- **Difference sub-test.** The Bonferroni interval (alpha 0.01/19) excludes 0 with the predicted sign, the point
  estimate is inside the tolerance, and the registered robustness holds. Robustness means the page's p_early metric
  (dyn) and p_mean - p_before give the same sign.
- **Equivalence sub-test** (T1 vs ones, T4's three non-DFT). The interval lies inside +-1.0 W.
- **T3 tolerances.** signs-ones uses +-1.0 W, as in x1_predictions.json. The plan's table prints "(+-1.5)" only after
  mant-signs.
- **T4.** aifoundry3: D = switching - 0.924 x model_switching_W (x1_predictions.json); the three non-DFT
  equivalences are D inside +-1.0 W, and the DFT and ReLU differences are D = +2.7 / +1.3 +- 1.0 W. aifoundry2
  "repeats its E15 values": the three equivalences are switching - a2_measured_E15_W inside +-1.0 W (the E15 values
  themselves, not the model: they differ by -0.21 to +0.35 W), and DFT / ReLU are switching - 1.0 x model = the E15
  misses +2.95 / +1.38 +- 1.0 W, i.e. the E15 values with the difference rule's sign condition (above the model).
- **T4 is a one-sample test.** The model is a constant. With df 3, t is 16.05 at alpha 0.01/19, so the half-width is
  about 8 x the run sd. The plan's "4.8 x run sd" is for the two-sample tests. The +-1 W equivalences therefore need
  run sd <= ~0.12 W. E15's sd for these configurations was 0.00-0.09 W.
- **T5.** pJ per MAC = switching / (MAC per s) x 1e12, with MAC per s as in analyze_ablation.py. The fp32/int8 ratio
  uses Welch on logs: the point is in [15, 23] and the interval excludes 1.
- **EM4 rider.** It is reported as a separate item, `ABL-T5-EM4`, for energy-manual-53/54/56/57. Per card, the 99% t
  interval of per-run switching excludes 0 for each of the 6 fp16/int8 patterns. The a3/a2 ratio's 99% interval is
  reported against 0.92 +- 0.04, and the reading counts how many of the six ratio points fall in 0.88-0.96 (the
  prediction is reported, not part of the item's outcome, as EXP-EM4's test (a) registers it).
- **T7.** The ratio passes if its point is in [0.98, 1.10]. There is no sign condition, because the band contains 1.
  The intercept is from least squares of per-run switching on active minions (256, 512, 1024); the upper end of its
  Bonferroni interval must be <= 0.5 W.
- **ABL-R** is descriptive. The four flip energies are refitted by non-negative least squares (constant free), using
  the RTL counts of toggles_all.json, on the 14 fp32 patterns' mean switching. The fit is reported per card with its
  leave-one-out rms, alongside the p80 fit, half-differences, the within-run drift slope and launch temperatures.
  The outcome is decided on aifoundry3 only: leave-one-out rms <= 0.6 W is PASS.
- **ABL-EM4c.** Every timed launch (launch >= 0) of every kept fma run must read 546.00 or 318.00 at 2 decimals.
  The calibration launch reads 546.03 because of the launch overhead on 20,000 iterations, so it is excluded. Any
  launch off its value is a FAIL (exact, deterministic); PASS needs at least 3 kept runs (separate processes) of each
  of fp32, fp16 and int8 on the card, else INSUFFICIENT (the common 3-repeat rule). The committed a2 sessions pass:
  1,065 launches.
- **ABL-EM4d** is aifoundry2 only. The 21 Sep ablation session is re-reduced with the same leak 0.81 and windows. For
  each of the 9 EM4 tensor patterns, the Welch 99% interval of new - old p80 must include 0. The 2% prediction is
  reported. Other common patterns are reported outside the decision.

## How to reduce

    python3 tools/claims-v3/abla/reduce.py --data <dir with aifoundry2/ and aifoundry3/ like DATA_ROOT> --out abla.json

It writes a list of items, each `{item, claims, per_card, test, outcome, reading}` with sub-test intervals, pass
numbers used and robustness, to `abla.json`. The per-run table goes to `abla.runs.json`. It runs on partial data:
missing cards or passes give INSUFFICIENT. Tested on the committed 21 Sep / E9 / E20 sessions laid out as passes, and
on synthetic sessions (validate3/drv/abla/: pred, shift, off600 + replacement pass, dropout, model, partial).

## Files

`block.sh` (the pass), `ablrun.sh` (patched runner, shared), `ablcore.py` (per-run metrics and statistics, shared),
`ablcheck.py` (end-of-block check, shared), `abl_a.cfg`, `tiles.sha256`, `x1_predictions.json` (registered),
`reduce.py`.
