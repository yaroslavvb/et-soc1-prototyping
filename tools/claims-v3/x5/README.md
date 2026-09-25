# x5: V3-X5 (PLAN3 §2, suggested E40)

Is aifoundry3's 0.92-0.95 switching scale a property of the card, or of its cooler launch temperature? Each card
launches the same patterns at two temperatures. Registered item: X5 (9 claims).

## What a pass does

`bash tools/claims-v3/x5/block.sh <pass>` runs the plan's pair hi<b>, lo<b> with b = pass - 1. These are two
one-block invocations of the shared runner `../abla/ablrun.sh` on `x5.cfg`: fp32 zeros, ones, uniform and randn, plus
fp16 randn (the EM4 temperature-arm pattern). Runs are 7 s, block index 0, SEED_OFFSET b, so seed b+1. The hot and
cool arms of a pass therefore run the same random tiles, and the passes differ from each other. Each arm has its own
10 Hz sampler, stopped with SIGTERM before the next one starts:

| card | hot: launch / preheat | cool: launch / preheat | reduced at |
|---|---|---|---|
| aifoundry2 | 83 / 86 C | 76 / 79 C | 83.9 / 76.9 C, leak 0.81 W/C |
| aifoundry3 | 65 / 68 C | 55 / 60 C | 65.9 / 55.9 C, leak 0.55 W/C |

Data: `$DATA_ROOT/x5/p<N>/hi<b>/` and `lo<b>/`. These are session directories with the same files as an abla pass.
`block.json` is in `p<N>/`. `--smoke` (`x5-smoke`) holds the card for about 12 s (up to ~25 s on aifoundry2, which
first runs lib.sh's `heat_to 76` before any sampler opens the management node): both arms' session paths, including
the sampler stop and restart, one heater burst each, and 3 s of fp32 uniform (hot) and fp16 randn (cool).
The runner changes of `../abla/README.md` apply (use count 0 before each arm's sampler starts, the sampler's own
count as the baseline, a card check before every heater burst, no blind heating).

## Card minutes per pass

| | aifoundry2 | aifoundry3 |
|---|---|---|
| per pass (hot + cool, 10 runs) | ~13-15 min (first cool run waits for ~88 -> 76 C) | ~10 min if 68 C is reached; up to ~20 min if not (60 bursts per hot run) |
| 3 passes (plan: 38 / 30) | ~40-45 min | 30-60 min |
| safety caps (hot / cool arm) | 20 / 20 min | 25 / 15 min |

Schedule `x5 1`, `x5 2`, `x5 3` in the AM rounds, as the plan's "X5 hi<b> + lo<b>" items.

## What is dropped, and why

The rules are the same as abla's. A run is dropped if a launch is not ok, it has no timed launch, the telemetry has a
gap, or any mhz.minion sample in [t0-2 s, t1] is not 600. On aifoundry2 the cool arm's 76 C is kept above the
governor's window, so a run that is still off 600 MHz is dropped. The V3-ABL-A dropout rule applies to power samples.
A pass 4+ replaces dropped runs, up to 3 per pattern per temperature. Fewer than 3 gives INSUFFICIENT.

## Deviations from the plan's commands, with reasons

- **Passes and paths.** Pass p is the plan's pair (hi<p-1>, lo<p-1>), as in the schedule. Paths are here instead of
  `build/v3x5/...`, and the runner changes are as in abla. SEED_OFFSET enters both seed expressions, as registered.
  The shuffle, `random.Random(block + 11)` with block 0, is therefore the same fixed order in all six invocations. The
  plan does not add SEED_OFFSET to the shuffle; a common order cancels in hot - cool.
- **The aifoundry3 hot target may be unreachable.** No committed aifoundry3 telemetry exceeds 61 C: E20, the wire
  runs and the catalogue all top out there. If 68 C is not reached, the runner does what the original does: after 60
  bursts it launches at whatever temperature the die has. starts.jsonl records `preheat_reached`.
  - The registered reduction corrects to target + 0.9 = 65.9 C, but p_before is measured at the actual start
    temperature. That biases hot switching upward by 0.55 W per degree of shortfall. The synthetic test with a 3 C
    shortfall reads +1.6-1.8 W, a spurious "temperature effect".
  - The reducer reports the measured launch temperatures per arm and prints a WARNING when an arm's mean is more than
    0.5 C below its target. It also gives an unregistered diagnostic: hot - cool with each run's own launch
    temperature. **This needs an owner decision before the aifoundry3 passes:** lower the aifoundry3 hot target, for
    example to 60 / 62 C, or accept the registered reduction with the warning.

## Reading of the registration

- **Metric.** Switching as V3-ABL-A, with the dropout rule, per directory, with the table's leak and launch
  temperature.
- **Test.** Per card and pattern (fp32 uniform, fp32 randn), the Welch 99.75% interval (Bonferroni over 4) of hot -
  cool.
- **Verdict** (`verdict` field):
  - "card property" if all four intervals lie inside +-0.5 W;
  - "temperature effect" if both aifoundry3 intervals exclude 0 with positive sign and their points are >= +0.4 W;
  - "not separated" otherwise.
- **Reported outside the decision.** fp16 randn, fp32 zeros and fp32 ones, with the same test.
- **Outcome field.** PASS = card property. CARD-DIFFERENT = the card hypothesis (both intervals inside +-0.5 W) holds
  on one card only. FAIL otherwise, which covers "temperature effect" and "not separated"; the pages then say
  "temperature contributes" or "the card or its temperature".
- **Power.** At n = 3 v 3, the half-width is about 5.5 x the run sd. The +-0.5 W window needs run sd <= ~0.09 W.
  E15/E20 uniform run sd was 0.04-0.07 W.

## How to reduce

    python3 tools/claims-v3/x5/reduce.py --data <dir with aifoundry2/ and aifoundry3/> --out x5.json

Output: an item list of one item (X5) with per-card intervals, measured launch temperatures and diagnostics, plus
`x5.runs.json`. It was tested on synthetic sessions: card property, temperature effect, aifoundry3 shortfall, off600
+ replacement, and partial (validate3/drv/x5/). The committed E9/E20 blocks were also laid out as hi/lo arms to
check the mechanics only.
