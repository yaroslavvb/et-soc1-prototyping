# V3-WIRE: heat per millimetre, third run, and the byte-for-byte fill check

PLAN3 §2 "V3-WIRE" (SHOULD; merges heat:EXP-heat-1 and heat:EXP-heat-2; suggested E42). Registered on two cards
(aifoundry2, aifoundry3); run on four since the four-card amendment of 25 Sep (aifoundry2, aifoundry3, aifoundry1-c0,
aifoundry1-c1: section "Four cards" below). 6 passes per card, 28 configurations per pass. Claims tested: heat-01, -02,
-05b, -06, -19, -21a, -21b, -22, -23, -32, -42, -43, -48, -75, -V04 (item WIRE-P1-16) and heat-V01 (item WIRE-FILL).

## Files

| file | what it is |
|---|---|
| `block.sh` | one pass per block: `bash tools/claims-v3/wire/block.sh <pass> [--smoke]` (on aifoundry1 with `V3_DEVICE=0` or `1`); `V3_DRY=1` prints every device call |
| `configs.json` | the 28 configurations: `run_wire.py --set v2 --only wu/p0/,wu/p0.5/,wu/p1/,wsep/p0/,wsep/p0.5/`, in the runner's list order, generated from `workloads/enercat/run_wire.py` `configs_v2()` |
| `wire_cfgs.py` | prints a pass's configurations in its shuffled order (no device access); `--check-runner` compares the table with the tree's `run_wire.py` |
| `wire_check.py` | end-of-block checks, standard library only: `dump` (DUMP against EXPECT) and `pass` (launches, samples, bursts marked for dropping by the card's own drop rule, the idle state) |
| `reduce.py` | the pre-registered tests: the registered outcome on aifoundry2 and aifoundry3, exactly as registered, and the four-card outcome (`all_cards`) on every card |
| `registered/exp_test.py`, `registered/exp_test_v3.py`, `registered/tdist.py` | verbatim copies of the pre-registered test scripts (`validate3/inv/heat-work/exp_test.py`, `validate3/heat-verify/exp_test_v3.py`, `validate3/inv/heat-work/tdist.py`), imported unchanged by `reduce.py` |

sha256 of the registered copies (identical to the scratch originals written on 25 Sep before any run):
`exp_test.py` e783ecd0f5a5d53009106c99f80bfbb8c45f1471d145599742f872ea022fb371,
`exp_test_v3.py` 85a13138873ff890368b13c46b5102046f721ce2ba90f611ccc13a8334d37a2b,
`tdist.py` 8aff2a423bcfac63491694edeb739cc4d31d0bd3638185638a74fa8f47fc358d.

## What a pass does

`block.sh <pass>` runs `run_wire.py`'s pass loop in bash, so that every device call goes through `lib.sh`:

1. `others_present && exit 3`; also exit 3 if one of our own device processes runs (`ours_running`, which `queue.sh`
   checks too; it stops a manual smoke from starting a second sampler beside a running block, and note that another
   session's fake test binaries named `ettelem`/`enercat_host` under the same uid count; with `V3_DEVICE` set, only our
   processes on the same card count, so aifoundry1's two cards run their own queues); `block_begin wire <pass>` (die
   read, code hashes), pre-flight: `build/enercat_v2/host/enercat_host`, `build/ettelem/ettelem`, and on a
   governor-free card (`lib.sh` `GOV_FREE`: every card but aifoundry3) `$HEATER` must exist; `wire_cfgs.py` writes the pass's order
   (`order.tsv`, `order.json`); `--check-runner` notes in `run.log` whether this tree's `run_wire.py` still matches the table.
2. **Pass 1 only (WIRE-FILL):** 12 separate launches before heating and before the sampler, each
   `hold10 enercat_host --pattern P --operands O --slice-bytes 32K --seconds 0.3 --window 60000000 --dump-slice 1024 --budget 8`
   for (tstore_raw bern:0.25), (tstore_raw alt:64), (tstore_raw frz), (tstore_uniq uq:0.25), 3 each, into
   `dump/dump_<O>_<r>.txt`; `wire_check.py dump` compares every DUMP word with its EXPECT word. `WIRE_DUMPS=1` repeats
   them in another pass (only if pass 1's were incomplete).
3. Governor-free cards (aifoundry2, aifoundry1-c0, aifoundry1-c1): `heat_to 76` (the curve in `heat.jsonl`); the block
   fails if the heater gives up.
4. `start_sampler telemetry.jsonl <28 x 18 + 300 s>` (10 Hz), 8 s settle.
5. For each configuration, in the order `random.Random(seed).shuffle` gives, seed 31 + pass - 1 on aifoundry2 and
   41 + pass - 1 on aifoundry3 (block pass N has the order of the runner's pass N-1 under `--seed 31` / `--seed 41`),
   51 + pass - 1 on aifoundry1-c0 and 61 + pass - 1 on aifoundry1-c1 (orders of their own):
   - stop with exit 3 if another user's device process (or a CI job, `lib.sh` `OTHER_COMM`) appeared; check the
     sampler (dead, or no new line since the last configuration: `stop_sampler` (SIGTERM), `start_sampler`, logged in
     `run.log`);
   - governor-free cards: if the die, read from the running sampler's last line (not `die_c`, which would open the management
     node), is below 69 C, one `hold10 $HEATER --test fma --type fp32 --pattern none --values randn --shires 0xffffffff
     --per-shire 32 --seconds 2 --seed 1`, marked `heater` in `marks.jsonl`;
   - prefill: `hold10 enercat_host --pattern tstore_uniq --operands uq:P --slice-bytes 32K --scp --seconds 0.3 --window 60000000 --budget 8`, marked `fill`;
   - 5 s idle; the idle state: the sampler's last complete line, as it is (minion and NoC clock and voltage, board
     power, die), appended to `idle_state.jsonl` as `{"kind":"pre_burst","cfg","pass","t_ms","sample"}` (not to
     `marks.jsonl`, whose every entry `analyze_wire.bursts()` cuts out of the idle brackets);
   - burst: `hold10 enercat_host <configs.json args> --seconds 3 --window 240000000 --budget 8` (8 launches of
     0.4 s, about 3.2 s), its `ENERCAT {...}` lines appended to `runs.jsonl` as `{"host", "pass", "cfg", ...}`; 4 s idle.
6. 8 s idle, `stop_sampler`, `wire_check.py pass --clock-rule window|busy [--gov-free]` (first removes truncated JSON
   lines from `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl` and `idle_state.jsonl`, counted in the note:
   `analyze_wire.jl` raises on one and the reduction would lose the whole pass; then marks the bursts the reduction
   will drop under the card's own rule, records the idle state per burst and per pass, writes `pass_check.json` and
   prints the note for `block.json`, which gives the samples off 600 MHz, how many of them fell inside bursts, and the
   idle clock of the brackets), gzip the telemetry, `block_end ok|fail`.
   The block fails only if the telemetry is empty or no burst launched (for `--smoke`: also if a configuration did not
   launch, a dump is missing, differs or comes from a failed launch, or the heater failed).

Before `block_begin`, a directory of the same pass left by an interrupted attempt (no `block.json`), or any earlier
attempt when `V3_FORCE=1` is set, is moved aside to `p<N>.attempt-<epoch>` (as `queue.sh` does), because the block
appends to `runs.jsonl`, `marks.jsonl` and `telemetry.jsonl` and two attempts would merge into one burst. A pass whose
`block.json` exists is skipped by `block_begin` ("already done", exit 0), so to repeat a failed smoke run
`V3_FORCE=1 bash tools/claims-v3/wire/block.sh 1 --smoke` (or use the next pass number).

`--smoke` (`wire-smoke/p<N>`): one dump launch of each of the 4 fills, the sampler, on a governor-free card one forced
mid-pass heater launch, then two configurations with the real timings (wu/p0.5/hop4: `--hop-distance` with `--uniq-regions`;
wsep/p0/hop5: `--pairs`), 2 s settle and 1 s tail. About 45 s of card time (35.6 s wall against fake binaries).

## Card minutes

E32 took 12.9 s per configuration on both cards (fill 0.56-0.60 s, 5 s, burst 3.2 s, 4 s). The five passes of this
block run on aifoundry2 on 25 Sep (`build/claims-v3/aifoundry2/wire/p1-p5`) took 384-408 s from `block_begin` to
`block_end`: 373 s from the first fill to the end in every pass, `heat_to 76` 0-18 s (the die was at 71-80 C from the
blocks before), no mid-pass heater, pass 1's 12 dumps ~20 s.

| | aifoundry2 | aifoundry3 | aifoundry1-c0 | aifoundry1-c1 |
|---|---|---|---|---|
| one pass (28 configurations, settle, tail, sampler start, die reads) | 6.4-6.8 min measured (heat_to from a warm die); ~8-9.5 min from a 70 C die with mid-pass heaters | ~6.5 min | ~6.5 min + `heat_to 76` from its idle die (65 C at 300 MHz on 25 Sep: ~1-3 min) + mid-pass heaters (it idles at 18.8 W against ~32 W, so its die falls faster between bursts: up to 28 x 2.6 s) = ~8-11 min | ~6.5 min + `heat_to 76` from its idle die (57 C on 25 Sep: ~2-5 min) + mid-pass heaters (up to 28 x 2.6 s) = ~8.5-12.5 min |
| pass 1 extra (12 dump launches) | ~0.3 min | ~0.3 min | ~0.3 min | ~0.3 min |
| 6 passes | ~40-57 min | ~40 min | ~50-66 min | ~52-75 min |
| smoke | ~45 s | ~40 s | ~45 s | ~45 s |

aifoundry1's heating times are estimates (its cards have not been heated yet); `heat_to` gives up after 150 tries
(~9-10 min), which fails the block rather than measuring on a cool die.

The plan's 45 / 38 min assumed one runner invocation; the extra on aifoundry2 is the per-block `heat_to 76`. Passes
are separate blocks, >= 30 min apart with other experiments between (PLAN3 §2.13). A block is ~7-12 min; the worst case
on a governor-free card (`heat_to` using all 150 tries, ~9-10 min, then a heater before every configuration) is ~18 min,
under the ~35 min block limit, so a pass is never split.

## What is dropped, and why

- A **burst** (one configuration in one pass) on aifoundry2 or aifoundry3 is dropped by
  `workloads/enercat/analyze_wire.bursts()`, as registered: any sample in the burst or its idle brackets off 600 MHz;
  a starved sampler (median `took_ms` > 60 in the burst); too few samples (< 5 in the burst or < 4 in the bracket
  before it).
- On aifoundry2 a burst is also dropped if any of its launches has an implied clock (`cycles_max / wall_s`) outside
  0.595-0.605 GHz (PLAN3 R-clock). In the committed E32 runs the implied clock was 0.5990-0.5997 GHz on both cards, and
  0.5982-0.5996 GHz in the five 25 Sep passes on aifoundry2, so this drops nothing unless the clock moved between samples.
  The end-of-block check marks by the same rule (`--clock-rule window`) and names a burst marked for its idle brackets
  alone ("clock off 600 MHz in the idle brackets only"; `marked_for_idle_bracket_clock_only`).
- On **aifoundry1's cards** (and any card added later) the same `bursts()` code runs with its clock test narrowed to the
  burst's own samples (its `busy` window: first launch + 0.5 s to the last launch's end); an idle bracket's clock never
  drops a burst. R-clock applies to every launch (both cards are governor-free), except that the first launch of a burst
  whose idle bracket before it sat below 600 MHz may go down to 0.585 GHz (section "Four cards"). `reduce.py` does
  this by handing `bursts()` a view of the telemetry in which only samples outside every busy window read 600 MHz
  (`busy_clock_only`); every other number is the registered code's. The end-of-block check marks bursts by the same
  rule (`--clock-rule busy`).
- A **pass** is not used unless its `block.json` says `"status":"ok"`; `p<N>.attempt-*` directories (set aside by
  `queue.sh`) are never read.
- A statistic that cannot be computed in a pass (a burst it reads directly was dropped) skips that pass. A line fit
  (`exp_test.sl`) still uses a pass that keeps >= 3 of its points, as the registered code does.
- Per item and card the first **six** passes (by pass number) with a value are used. **Re-run rule (operator):** when a
  block's note shows bursts marked for dropping or configurations not launched, add one more pass on that card with the
  next number (`wire 7`, ...); it then replaces the lost repeat for the items that lost it.

## Four cards (amendment of 25 Sep 2026, before any data of aifoundry1's cards)

The owner asked for every measurement to be re-run on every card after the machine fixes of 25 Sep, so V3-WIRE runs
on aifoundry2, aifoundry3, aifoundry1-c0 and aifoundry1-c1 (aifoundry1's cards through `V3_DEVICE=0|1`, `lib.sh`).
The amendment text for AMENDMENTS.md is `validate3/fourcards/amendment-wire.md`. What changes:

- **The registered outcome stays** (`outcome`, `registered_verdict`, `reading` of every item): aifoundry2 and aifoundry3
  only, computed exactly as before (checked: every field of the old `reduce.py`'s output is present and equal in the
  new one's, only fields are added, on the passes collected on 25 Sep (aifoundry2 p1-p5, aifoundry3 p1), the E32 split,
  review sets A-F, P, T and t1-t5, and the four-card synthetic sets).
- **Every pass is re-run** (the owner's request): 6 new passes per card. Before the campaign, move the 25 Sep passes
  out of `DATA_ROOT` (`build/claims-v3/aifoundry2/wire/p1-p5`, aifoundry3's `wire/p1`), since `block_begin` skips a
  pass whose `block.json` exists ("already done"); they enter neither outcome.
- **A four-card outcome is added** (`all_cards`): each card gets the registered per-card test (holds / sign / fails /
  insufficient); PASS it holds on every card, CARD-DIFFERENT on some, FAIL on none, INSUFFICIENT a card (a missing one
  included) has fewer than 3 kept passes. A "sign" card (null excluded, mean outside the range) does not hold, so four
  sign cards give FAIL here where the registered two-card rule says SIGN-ONLY; the reading lists them, and
  `null_excluded` says whether the null is excluded on the same side on every card with 3 kept passes.
  `over_sufficient` is the same words over the cards that have 3 kept passes. aifoundry2's and aifoundry3's per-card
  values, and their drop rules, are the registered ones in both outcomes (one set of values per card). `per_card` holds
  all four cards.
- **No WIRE band is specific to one card:** P1-P16 were registered "per card, 6 passes" with one range for both cards,
  and WIRE-FILL "on each card", so every item is tested on aifoundry1's cards unchanged; nothing is only reported.
- **Parameters** (the governor-free values of aifoundry2 unless the physics says otherwise): heat_to 76 C before each
  pass and a 2 s heater below 69 C mid-pass, as on aifoundry2 (both cards: TDP 65 W, temperature threshold 65 C,
  governor free); the leakage correction of `analyze_wire` (aifoundry2's idle-law fit, 23.3 W e^((T-80)/36)) unchanged,
  as the plan applies it to both registered cards (it corrects for the die's temperature difference between burst and
  brackets only; a voltage step between them, as on c0, stays in the idle step below); shuffle seeds 51 + p - 1 (c0)
  and 61 + p - 1 (c1).
- **Drop rule** (the physics that differs: aifoundry1-c0, firmware 1.4.1, idles in a "low_power" state at 300 MHz /
  398 mV between kernels): a sample off 600 MHz drops a burst only if it lies in the burst's busy window; the idle
  brackets never do, else every c0 burst would go (checked on synthetic c0 data: the registered rule drops 28 of 28
  bursts of a pass, the busy rule none). For the same reason, a burst that starts from an idle clock below 600 MHz
  begins with the governor's ramp, which lengthens its first 0.4 s launch: that launch's implied clock may go down to
  0.585 GHz (a ramp of at most ~20 ms at 300 MHz, under 0.6% of the 3.2 s burst); every later launch, and every launch
  of a burst that starts from 600 MHz (aifoundry1-c1, which idles at 600 MHz / 499 mV), keeps 0.595-0.605 GHz. The
  0.585 GHz floor is a choice made without any measurement of c0's ramp. Decided now: if c0 ramps more slowly, or
  drops back to 300 MHz between the launches of one burst, R-clock drops those bursts; if its governor holds a point
  below 600 MHz under load on a die above 65 C, the busy-window rule drops them; either way c0 comes out INSUFFICIENT
  and the bands are not widened after pass data. Run `V3_DEVICE=0 bash tools/claims-v3/wire/block.sh 1 --smoke` first
  and read `first_launch_ghz`, `implied_ghz`, `before_mhz` and `idle_state` in `wire-smoke/p1/pass_check.json`; a
  change after the smoke is a further amendment, made before c0's first pass.
  aifoundry2 and aifoundry3 keep the registered rule in both outcomes (an idle-bracket sample off 600 MHz still drops a
  burst there). `reduce.py` reports per card how many bursts it dropped for an idle-bracket clock alone
  (`bursts_dropped_only_for_idle_clock`: 0 on the five aifoundry2 passes of 25 Sep), and the end-of-block check lists
  them (`marked_for_idle_bracket_clock_only`, counted in the note).
- **Idle state recorded:** the block writes the sampler's line just before every burst to `idle_state.jsonl`;
  `wire_check.py` and `reduce.py` read the minion and NoC clocks and voltages of every bracket from the telemetry
  (`cards[<card>].idle_state`: histograms, medians, `differs_minion`, `differs_noc`).
- **What c0's idle state does to the items** (a reading decided now): on a card whose brackets sit at another operating
  point than its bursts, the energy over idle includes the step between the two, a constant power per burst that
  enters each per-byte value as step x wall/bytes. It cancels where a statistic is a difference of the random-data and
  zeros configurations at the same hops, which run at the same bandwidth (P1, P3, P5a, P10, P16: `STEP_CANCELS`); it
  does not cancel anywhere else (zeros and total slopes, ratios, points off a line, exit steps, P13), because the
  bandwidth falls with the hop distance (wsep: 1,444 GB/s at one hop to 448 GB/s at five on 25 Sep), so wall/bytes
  grows 3.2-fold. Board items see the minion rail's step (on the order of 10 W: c0 idles at 18.8 W, the 600 MHz cards
  at 30-33 W), mesh-rail items only a NoC step (the NoC's own idle clock is recorded). Checked on synthetic data (c0
  given a 10 W board and 1 W NoC step): the five STEP_CANCELS statistics moved by at most 0.32%, every other one by
  7-670%. Each energy item carries `idle_clock` (every card's idle minion clock) and, when a card's idle state differs
  on the rail it reads, `idle_note`, which says whether the step cancels. Expected before any data: c0's board step is
  probably of the order of 10 W (not measured on c0 itself), as large as the bursts' own 2-17 W over idle, so c0 may
  well be CARD-DIFFERENT on board items that do not cancel it (P4, P5b, P6b, P7d-f, P9, P11b; in the synthetic check
  below P4, P5b, P7d and P11b left their bands). Such a result,
  on c0 alone and in a non-cancelling item, cannot be told apart from its idle state: the page does not read it as a
  difference in the wire and gives c0's value with its idle state.
- **WIRE-FILL** runs on every card in pass 1 (12 launches); its all-card outcome: per card holds (all complete and
  matching), fails (a mismatch), insufficient (a fill short).

## Deviations from the plan's commands (sources win)

1. **The runner is not run.** The plan runs `workloads/enercat/run_wire.py ... --passes 6` unmodified. Its host
   launches use `timeout 12` with the host's default `--budget 9.5`, and it `kill()`s (SIGKILL) a sampler that failed
   to start or stalled; the v3 rules require `timeout 10` (or `--budget` <= 8) and SIGTERM only, and every device call
   must go through `lib.sh`. `block.sh` repeats the runner's pass loop with the same arguments (`configs.json`, checked
   against `configs_v2()`), the same fill command, the same timings (5 s / 3 s / 4 s, 8 s settle, 8 s tail), the same
   `marks.jsonl` and `runs.jsonl` records, and every enercat launch under `hold10` with `--budget 8` (the burst process
   holds the card about 3.6 s, the fill about 0.6 s). The sampler is `lib.sh`'s (6 start attempts with a drain after the
   second, where the runner makes 8).
2. **One pass per block**, >= 30 min apart (framework and §2.13), instead of one invocation of 6 back-to-back passes
   started on both cards at once. The shuffle seeds are the runner's (31 + p on aifoundry2, 41 + p on aifoundry3), so
   each pass has the order the runner would have given it; `pass` in `runs.jsonl`/`marks.jsonl` is the block's pass
   number (1-6), not the runner's 0-2. aifoundry1's cards, which the plan did not have, take 51 + p (c0) and 61 + p (c1).
3. **aifoundry2 starts every pass on a die >= 76 C** (`heat_to 76`, binding rule), and keeps the runner's mid-pass
   heater below 69 C (`--warm-c 69`, as the plan's command). aifoundry3 runs no heater (the plan's aifoundry3 command
   has no `--warm-c`; `$HEATER` there would be `build/sparsity/...`, never called). aifoundry1's cards, governor-free
   like aifoundry2, do as aifoundry2 (four-card amendment), with `$HEATER` = `build/sparsity/host/sparsity_host`.
4. **WIRE-FILL.** The plan's top-level command reads `--pattern $1 --operands $2` without splitting `$OP`; the component
   detail has `set -- $OP`, which the block does. `--budget 8` added. The launches run in pass 1's block before
   heating and before the sampler ("before the first pass"). Checked in the sources: without `--scp`, `main.cpp`
   allocates 2048 DRAM slices for `tstore_uniq` (`stream` mode) and the kernel writes `slice + (g*2 + r)*slice_bytes`,
   so `tstore_uniq` does not refuse a DRAM slice; the reducer still handles a refusal as the plan allows. The dump is
   hart 0's DRAM slice against `src[i % 128]` (`src[i]` for uq), i.e. the store kernel on a DRAM slice, never the
   scratchpad image (the tool skips `--dump-slice` when `--scp` is set), which is the caveat heat-V01 must keep.
   A launch counts only if it printed 256 DUMP and 256 EXPECT words and every `ENERCAT` line says `"ok":true`: the host
   prints DUMP/EXPECT even when the kernel failed, and an unwritten slice would otherwise read as a mismatch and FAIL
   the claim for a launch failure (it is INSUFFICIENT until re-run with `WIRE_DUMPS=1`). tstore_uniq counts as
   refused (pattern dropped) only if all three launches failed with the host's `refusing ...` message; any other
   error (no device, a kernel that did not finish) is a failed launch.
5. **Output** goes to `$DATA_ROOT/wire/p<N>/` (framework) instead of `docs/reports/data/2026-09-2X-wire3-<card>`.
6. **Reduction.** The plan's `python3 validate3/heat-verify/exp_test_v3.py <a2 dir> <a3 dir>` takes one runner-layout
   directory per card. `reduce.py` imports the same registered code (verbatim copies) and applies it to the block
   directories; run on the committed E32 data split into this layout it reproduces the verifier's dry run
   (`validate3/heat-verify/dryrun_exp1_v3_existing.json`) exactly: 25/25 verdicts, every mean, interval and no-leak
   value with relative difference 0.
7. **Outcome words.** The framework's PASS / FAIL / CARD-DIFFERENT / INSUFFICIENT, plus the registered SIGN-ONLY; P13 is
   DESCRIPTIVE. CARD-DIFFERENT (holds on one card, fails on the other; or the null excluded on opposite sides) and
   INSUFFICIENT (< 3 kept passes on a card) follow PLAN3 R-both; `registered_verdict` keeps exp_test's own
   PASS/SIGN-ONLY/FAIL for the same numbers. WIRE-FILL follows its item rule: any mismatch on either card is FAIL.
   The registered rule calls "null excluded on both cards, a mean outside the range" SIGN-ONLY even when the mean is on
   the other side of the null from a one-sided predicted range; the outcome is kept, and the reading then adds "the
   sign is opposite to the prediction on <card>" so the page does not state the predicted sign.
   Not a deviation, for the reader of the verdicts: P10's statistic is the d=0 data part divided by the d=1 data part
   (claim heat-19: "the data-dependent energy is zero at d = 0, 1.5% of its one-hop value"), tested for equivalence
   inside -4..+4%; the plan's "d=0 data part within +-4% of d=1" means |d=0 part| <= 4% of the d=1 part, which is what
   the registered code tests.
8. **Implied clock** (R-clock) is applied per burst, at the granularity of the plan's WIRE drop rule, on aifoundry2
   and (four-card amendment) on aifoundry1's cards, never on the pinned aifoundry3.
9. A foreign device process (or a CI job) appearing mid-pass ends the block with exit 3 (the queue retries it later);
   logins alone do not. On aifoundry1 a foreign process on the other card counts too (another user's processes cannot
   be told apart by card).

## How to reduce

Collect `build/claims-v3/<card>/wire/` from every host into one directory laid out like `DATA_ROOT`, then, from the
tree root on aifoundry2 (numpy needed):

    python3 tools/claims-v3/wire/reduce.py --data <dir>/ --out <dir>/wire-verdicts.json \
        --beside docs/reports/data/2026-09-24-wire2-aifoundry2 docs/reports/data/2026-09-24-wire2-aifoundry3

`<dir>` holds `aifoundry2/wire/p1..p6`, `aifoundry3/wire/p1..p6`, `aifoundry1-c0/wire/p1..p6` and
`aifoundry1-c1/wire/p1..p6` (any other `aifoundry<N>[-c<M>]` directory is read too). `--beside` (optional) prints the
committed 3-pass values next to the new ones, never in a test. It works on partial data (a card missing, fewer passes)
and then says INSUFFICIENT. Output: `{"exp", "registered_cards", "all_cards", "cards": {per card: passes used/skipped,
bursts kept/dropped with reasons, drop rule, implied clock range, first-launch ramp range, idle_state}, "outcomes"
(registered), "outcomes_all_cards", "items": [...]}`; each item has `item`, `claims`, `per_card` (every card: n, mean,
lo99, hi99, vals, passes, status; board items also `secondary_noleak`, descriptive), `test`, `outcome` (registered),
`registered_verdict`, `reading`, `all_cards` (outcome, over_sufficient, holds_on, sign_only_on, fails_on,
insufficient_on, missing, null_excluded, idle_step_cancels, reading), `idle_clock` and, when a card's idle state
differs, `idle_note`.

## Tests done off the card (25 Sep)

- `bash -n`; `V3_DRY=1` passes 1 and 2 and `--smoke` on aifoundry2, and pass 1 and `--smoke` as aifoundry3 (a fake
  `hostname` on PATH): pass 1 shows 68 device launches (12 dumps, 28 fills, 28 bursts), `heat_to 76` and the sampler on
  aifoundry2 only, seeds 31 / 41, no heater on aifoundry3.
- A scratch copy of the tree with fake binaries (scripts that print synthetic samples and ENERCAT/DUMP lines and open
  no device) ran `--smoke`, a smoke with a DUMP mismatch, an off-600 MHz clock and a sampler that dies every 12 s
  (block fails; both bursts marked; the sampler restarted by SIGTERM + `start_sampler`), and one full pass per card
  (aifoundry2 with the die below 69 C, so the heater ran before every configuration).
- `reduce.py` on the committed E32 data split into this layout (exact reproduction, above), on one card only, on 2
  passes, with a failed block, an attempt directory and a pass without `block.json`, on 7 passes with implied-clock drops
  (the item that lost a burst takes pass 7), on the fake full passes, and on synthetic dumps (all match: PASS; one
  mismatch on one card: FAIL; tstore_uniq refused on one card: PASS on 9 there; a missing launch: INSUFFICIENT); and the
  outcome rules on 13 constructed cases.
- Review (25 Sep, after the above): `bash -n`; `V3_DRY=1` passes 1, 2 and `--smoke` on both cards again (68 / 56 / 9 device
  launches on aifoundry2, 68 / 56 / 8 on aifoundry3; `heat_to` and the heater on aifoundry2 only); `--smoke` in the fake
  tree with a leftover attempt directory (set aside, 2/2 bursts kept by `analyze_wire.bursts()`); `reduce.py` on the
  E32 split (25/25 registered verdicts and every value identical to `dryrun_exp1_v3_existing.json`) and on review sets
  under `validate3/drv/wire/review/syn/` built by `review/mk.py` (6 passes per card from E32): unchanged data (25 PASS
  including WIRE-FILL, P7f CARD-DIFFERENT, P13 DESCRIPTIVE); P12 made null on both cards (FAIL) and on aifoundry3 only (CARD-DIFFERENT, registered FAIL); P12 reversed in
  sign (SIGN-ONLY with the opposite-sign note); a dump mismatch on one card (FAIL); a failed launch with a differing
  word (INSUFFICIENT, not FAIL); three uq launches failing with "no ET devices found" (INSUFFICIENT) or with the
  refusal message (PASS on 9); a truncated telemetry and runs line (the pass is lost without the sanitising step and
  kept with it); 2 passes on one card (INSUFFICIENT); no data (INSUFFICIENT).

## Four-card tests (25 Sep, off the card; data under `validate3/fourcards/wire/`)

- `bash -n block.sh`; `V3_DRY=1 V3_FORCE=1` passes 1, 2 and `--smoke` on all four card ids, run from the tree root with
  the block's absolute path (aifoundry3 and aifoundry1 through a `hostname` shim on PATH, aifoundry1 with
  `V3_DEVICE=0` / `1`): 68 / 56 / 9 device launches on aifoundry2, aifoundry1-c0 and aifoundry1-c1 (heat_to 76 in the
  passes, the forced heater in the smoke), 68 / 56 / 8 on aifoundry3 (no heat_to, no heater); `run.log` records seeds
  31/32, 41/42, 51/52, 61/62, `gov_free`, `clock_rule` window / window / busy / busy and `et_devices` all / all / 0 / 1;
  28 `idle_state.jsonl` lines per pass; aifoundry1 without `V3_DEVICE` stops with exit 2 (lib.sh).
- The idle-state recorder (`tel_line` and its `printf`) on a real telemetry file with a truncated last line: the last
  complete sample, valid JSON; `null` without a sampler file.
- `wire_check.py pass` on today's aifoundry2 pass 1 (copy): the same bursts marked as the old version (none), idle
  600 MHz in 100% of brackets; on synthetic aifoundry1-c0 passes (idle at 300 MHz): the window rule marks 28 of 28
  bursts, the busy rule none, and in the "drops" set exactly the broken bursts (two first launches at 0.580 GHz, a
  fourth launch at 0.590 GHz, a 300 MHz sample inside a burst); aifoundry1-c1's first launch at 0.590 GHz from a
  600 MHz idle is marked (no ramp allowance).
- `reduce.py` registered fields (outcomes, cards, every item's outcome, registered_verdict, reading, test, per_card of
  aifoundry2/aifoundry3) identical to the previous version's on the E32 split, today's five aifoundry2 passes with the
  E32 aifoundry3 passes, and review sets A-F.
- `reduce.py` on four-card sets built by `validate3/fourcards/wire/mk4.py` (aifoundry2/3 = review set A; c0 from
  aifoundry2's passes with its idle at 300 MHz / 398 mV and every first launch at 0.590 GHz; c1 from aifoundry3's):
  all4: all_cards 25 PASS + P7f CARD-DIFFERENT, as the registered outcome (every item passes on all four cards where it
  passes on the registered two); drops: the 4 c0 and 1 c1 broken bursts dropped with their reasons; c0diff (c0 also
  pays a 10 W board and 1 W NoC step at idle, one dump mismatch on c0): the STEP_CANCELS items still hold on c0 (moved
  <= 0.32%); P2, P4, P5b, P7d, P11a, P11b, P12, P14b and WIRE-FILL become CARD-DIFFERENT (P7f already was), the other
  non-cancelling items move 7-60% but stay inside their wide bands; every energy item carries the idle note; the
  registered outcome is unchanged; missing (no aifoundry1-c1): every all_cards outcome INSUFFICIENT with `over_sufficient` PASS /
  CARD-DIFFERENT over the other three. In every set the registered fields equal review set A's.
- Review (25 Sep, off the card; data under `validate3/fourcards/wire/rv/`): the previous `reduce.py` (from `git show
  HEAD`) and the new one on the real passes (validate3/data: aifoundry2 p1 + aifoundry3 p1; aifoundry2 p1-p5 +
  aifoundry3 p1; aifoundry2 p1-p5 as both cards), the E32 split, review sets A-F, P, T, t1-t5, fakedata and the
  four-card sets: every field of the old output present and equal in the new one (only the `code_sha256` key's
  relative path differs, since the old copy ran from scratch). `V3_DRY=1 V3_FORCE=1` passes 1, 2 and `--smoke` on the
  four card ids again (68 / 56 / 9 launches, 68 / 56 / 8 on aifoundry3). A variant (`rv/mkv1.py`): c0 with a 0.4 s
  300 MHz ramp at every burst start and a 1.5 s 600 MHz tail after it (kept: outside the busy window), one c0 sample at
  300 MHz 0.7 s into a burst (dropped, "inside the burst"), and one aifoundry2 after-bracket sample at 700 MHz
  (dropped by the registered rule, `bursts_dropped_only_for_idle_clock` 1, marked by `wire_check.py` "in the idle
  brackets only"); registered fields unchanged.
