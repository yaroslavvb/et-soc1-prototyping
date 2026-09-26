# abla: V3-ABL-A (PLAN3 §2, suggested E38)

Tensor-unit energy by operands, precision, structure and active minions, strict start, 7 s runs. Registered on
aifoundry2 and aifoundry3; since 25 Sep also run on aifoundry1's two cards (section "Four cards" below).
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
   2. It approaches the launch temperature. A governor-free card (aifoundry2, aifoundry1-c0, aifoundry1-c1) heats to
      >= 84 C with 2 s fp32-randn bursts under hold10, then idles until the die reads <= 80 C. The pinned aifoundry3
      does the same with 60 / 55 C. Before every burst it checks the
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

On aifoundry1 (V3_DEVICE set) steps 3 and 3.1 do not use the et_soc1 use count, which counts both cards of the host
while the other card's queue holds its own card: "someone else holds the card" is then another user's device process
or CI job (lib.sh's OTHER_COMM), or one of our own device processes that can open this card (ET_DEVICES unset or this
card, lib.sh's ours_running rule; a dev_mngt_service whatever its ET_DEVICES, since that binary ignores it and opens
every card), other than this session's sampler. session.json records which check ran.

Files per pass (`$DATA_ROOT/abla/p<N>/`): telemetry.jsonl.gz, runs.jsonl (block -9 = heater bursts), starts.jsonl
(start temperature, approach time, heater bursts, whether the preheat was reached, seed, time waited for other users,
and the idle clock and voltage read from the sampler just before the launch: idle_mhz, idle_mv),
ends.jsonl (host exit code), order.<block>, config.cfg, session.json, host.log, check.json, tiles.check,
code.sha256, block.json.

`--smoke` (`abla-smoke`) holds the card for about 20 s (up to ~35 s on a cool governor-free card: it first runs lib.sh's
`heat_to 76`, before its sampler opens the management node, so the smoke also starts on a warm die). It starts the
sampler, fires one heater burst, then does 3 s runs of m_negzero (reads a structured tile on this host), int8_ones,
fp16_zeros and spin. `ablcheck.py --smoke` then
requires every launch to be ok and every telemetry field the reducers read to be present, and prints cycles/op.

## Card minutes per pass

| | aifoundry2 | aifoundry3 | aifoundry1-c0, aifoundry1-c1 |
|---|---|---|---|
| per pass (23 runs) | ~26 min (committed strict sessions: 66-69 s start to start) | ~13 min (E20: 33 s start to start) | ~26 min each (aifoundry2's protocol; their heating and cooling rates are unmeasured) |
| 4 passes (plan: 115 / 65) | ~105 min | ~53 min | ~105 min each |
| safety cap per block (`ABL_CAP_S`) | 45 min | 30 min | 45 min |

Schedule `abla 1` .. `abla 4` as separate queue lines, at least 30 min apart with other experiments between them
(PLAN3 §2.13).

## What is dropped, and why

`ablcore.py` decides which runs are kept. For the registered outcome (aifoundry2 and aifoundry3) it drops a run when:

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

## Four cards (25 Sep 2026: aifoundry1's two cards)

The owner asked for every measurement on every card after the day's machine fixes, so the campaign runs on
aifoundry2, aifoundry3, aifoundry1-c0 and aifoundry1-c1 (lib.sh: `V3_DEVICE=0|1` on aifoundry1). The amendment for
aifoundry1's cards (docs/reports/data/2026-09-25-claims-v3/AMENDMENTS.md) is committed before any of their data.

**Parameters.** The blocks choose them by what the card is, not by host name. Launch temperatures follow the
governor (lib.sh's `GOV_FREE`): a governor-free card heats to 84 C and launches at 80 C, above the window where its
governor lifts the clock; the pinned aifoundry3 uses 60 / 55 C. aifoundry1's cards are governor-free with aifoundry2's
configuration (TDP 65 W, threshold 65 C), so they take aifoundry2's values: targets, cap, and the reduction's leakage
slope 0.81 W/C at 80.9 C. Their own slopes are unmeasured; the slope multiplies only the few degrees between the
launch temperature and seconds 1-3, so a 30% error in it (0.24 W/C) moves a run's switching by 0.24 W per degree of
that rise, and largely cancels in differences between patterns that heat alike. Physics that a parameter cannot fix
is handled in the reduction (below).

**aifoundry1-c0 can idle at 300 MHz.** Its firmware (1.4.1) idles in a "low_power" state at 300 MHz / 398 mV
(18.8 W board) after a long idle, and a burst runs at 600 MHz. The aifoundry1 clock test (25 Sep ~16:40, two 2 s
launches 1 s apart) showed both idle states: the first launch after the low-power idle showed no power rise and the
clock reached 600 MHz only at its end; after it the card idled at 600 MHz (26 W) and the second launch drew 49.4 W. So
which state a block's idle brackets are in (each run follows an approach that may end with tens of seconds of idle)
is not known in advance; it may differ from run to run. The registered rule ("any sample in [t0-2 s, t1] off 600 MHz")
covers the pre-launch idle bracket and would drop every run whose bracket is in the low-power state. So:

- *Busy rule* (`kept_busy`): the clock test covers only the samples the busy metrics read, [t0+0.3 s, t1] (p_mean's
  window, which contains p_early's; the first 0.3 s after the launch are read by no metric). Every other condition is
  the registered one. The idle bracket is recorded, not tested: `idle_state` (e.g. "300", "600", "mixed 300-600"),
  `idle_mhz_min/max`, `idle_mv`, beside `busy_mv`; starts.jsonl also records the clock and voltage the sampler read
  just before the launch. A run whose burst itself starts in the low-power state (as the clock test's first launch) has
  busy samples off 600 MHz and is dropped by the busy rule.
- *What the idle state does to the metrics.* switching and dyn subtract p_before, the idle bracket's power. When the
  bracket is in the 300 MHz / 398 mV state, the over-idle values include the step from idling at 600 MHz to idling at
  300 MHz (several watts): differences between configurations whose runs idled in the same state cancel it; absolute
  over-idle values (pJ per MAC, spin, the minion-count intercept, the dense/zero saving, uJ per layer) do not; and
  hot - cool at two launch temperatures (V3-X5) also carries (busy leakage slope - idle leakage slope) x the
  temperature step. If a card's runs idled in MORE THAN ONE state (`idle_mixed_on`), a difference between two runs in
  different states carries the step and does not cancel either; `by_idle_state` then gives the item on each state's
  runs alone (reported, never deciding; usually INSUFFICIENT, since each state holds only part of the runs). The
  reducers attach each card's idle clock, voltage and idle power by state (`idle_w_by_state`; the firmware releases
  idle at different powers even at 600 MHz: 26 W on 1.4.1, 33-35 W on 1.2.0, 32 W on 1.3.1) to every item about energy
  over idle, with the kind of effect, so the page can say when a card's idle state differs.
- *If aifoundry1-c0's bursts are not at 600 MHz* (its governor's operating points above the 65 C threshold are
  unknown), the busy rule drops them and its items are INSUFFICIENT. No other operating point or launch temperature is
  substituted after seeing data. Run the smoke on each aifoundry1 card first: its note shows `busy-off600` and the
  idle clocks (`idle-mhz`).

**Block note.** `ablcheck.py` gives both rules: `off600` (registered), `busy-off600` (four-card rule), and the idle
clocks seen (`idle-mhz 300:23`). Neither fails the block; a pass 5+ replaces runs dropped by the busy rule on
aifoundry1's cards, as the registered replacement does for aifoundry2.

**Reduction.** Each item keeps its REGISTERED outcome, computed exactly as before from aifoundry2 and aifoundry3 with
the registered rule (checked: identical output on the synthetic and legacy test sets, and on aifoundry2's real
passes collected so far, abla p1-p4, ablb p1-p2, x5 p1-p2). Each item gains `all_cards`:

- The busy rule on every card of `--expect` (default the four campaign cards) and any other card directory found. Per
  card: PASS / FAIL / INSUFFICIENT where the item is registered for each card; REPORTED where its band is given for
  aifoundry2 or aifoundry3 only (the card's values are shown against both cards' bands, `vs_<card>_values`, with the
  outcome each would give as `would_be`); N/A for aifoundry2-only checks.
- Outcome over the tested cards: PASS on every one, FAIL on every one, CARD-DIFFERENT on some; INSUFFICIENT when one
  lacks the kept repeats or has no data (`cards_missing`).
- `registered_cards_busy_vs_registered_rule` flags where the busy rule changes aifoundry2's or aifoundry3's outcome.
- `idle_clock` (idle clock, voltage and power by state per card), `idle_differs_on`, `idle_note` on items about
  energy over idle; `idle_mixed_on` and `by_idle_state` (the item on each idle state's runs alone, reported) for a
  tested card whose runs idled in more than one state.
- `per_card` holds all four cards: aifoundry2 / aifoundry3 as registered; aifoundry1's cards under the busy rule with
  aifoundry2's reduction parameters (`"rule": "busy"`).

Which V3-ABL-A items are tested on aifoundry1's cards:

| item | on aifoundry1's cards | idle state |
|---|---|---|
| ABL-T1 negative zero | tested (same bands on both cards) | cancels (if the runs idled in the same state) |
| ABL-T2, T3, T8 | REPORTED (a2 / a3 values) | cancels (same condition) |
| ABL-T4 structured matrices | REPORTED (a3: 0.924 x model; a2: its E15 values) | absolute |
| ABL-T5 | tested: the fp32/int8 ratio in [15, 23] (registered "on each card"); pJ per MAC bands REPORTED | absolute |
| ABL-T5-EM4 rider | tested (switching > 0 per card); each card / aifoundry2 ratio reported | absolute |
| ABL-T6 spin | REPORTED (1.46 / 1.35 W bands) | absolute |
| ABL-T7 active minions | tested (same band and bound on both cards) | absolute |
| ABL-R refit | REPORTED (decided on aifoundry3); each card's fit stated | the free constant absorbs it |
| ABL-EM4c cycles per op | tested (exact) | none |
| ABL-EM4d | N/A (aifoundry2 against its own 21 Sep session) | none |

**Card checks on aifoundry1** (runner, above): no use count; processes only.

**Structured tiles.** aifoundry1's tree (~/nekko) needs the same rsync of the 21 Sep structured tiles as aifoundry3;
the block fails before any launch if `tiles.sha256` does not match.

## How to reduce

    python3 tools/claims-v3/abla/reduce.py --data <dir with one directory per card, like DATA_ROOT> --out abla.json \
        [--expect aifoundry2,aifoundry3,aifoundry1-c0,aifoundry1-c1]

It writes a list of items, each `{item, claims, per_card, test, outcome, reading, all_cards, reading_all_cards}` with
sub-test intervals, pass numbers used and robustness, to `abla.json`. The per-run table (both rules' keep decisions
and the idle clocks) goes to `abla.runs.json`. It runs on partial data: missing cards or passes give INSUFFICIENT.
Tested on the committed 21 Sep / E9 / E20 sessions laid out as passes, on synthetic sessions (validate3/drv/abla/:
pred, shift, off600 + replacement pass, dropout, model, partial), and on synthetic four-card sessions
(validate3/fourcards/abla/: all four hold with aifoundry1-c0 idling at 300 MHz; aifoundry1-c0's idle state 9 W below
its 600 MHz idle, plus a busy-off-600 run and its replacement pass; aifoundry1-c1 missing; and, in
validate3/fourcards/review/syn/, aifoundry1-c0's runs alternating between the two idle states, or all but one per pass
at 300 MHz, where differences fail on c0 and `by_idle_state` shows the per-state view).

## Files

`block.sh` (the pass), `ablrun.sh` (patched runner, shared), `ablcore.py` (per-run metrics, both clock rules,
statistics and the all-cards combination, shared),
`ablcheck.py` (end-of-block check, shared), `abl_a.cfg`, `tiles.sha256`, `x1_predictions.json` (registered),
`reduce.py`.
