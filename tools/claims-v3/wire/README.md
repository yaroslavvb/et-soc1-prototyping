# V3-WIRE: heat per millimetre, third run, and the byte-for-byte fill check

PLAN3 §2 "V3-WIRE" (SHOULD; merges heat:EXP-heat-1 and heat:EXP-heat-2; suggested E42). Both cards, 6 passes per card,
28 configurations per pass. Claims tested: heat-01, -02, -05b, -06, -19, -21a, -21b, -22, -23, -32, -42, -43, -48, -75,
-V04 (item WIRE-P1-16) and heat-V01 (item WIRE-FILL).

## Files

| file | what it is |
|---|---|
| `block.sh` | one pass per block: `bash tools/claims-v3/wire/block.sh <pass> [--smoke]`; `V3_DRY=1` prints every device call |
| `configs.json` | the 28 configurations: `run_wire.py --set v2 --only wu/p0/,wu/p0.5/,wu/p1/,wsep/p0/,wsep/p0.5/`, in the runner's list order, generated from `workloads/enercat/run_wire.py` `configs_v2()` |
| `wire_cfgs.py` | prints a pass's configurations in its shuffled order (no device access); `--check-runner` compares the table with the tree's `run_wire.py` |
| `wire_check.py` | end-of-block checks, standard library only: `dump` (DUMP against EXPECT) and `pass` (launches, samples, bursts marked for dropping) |
| `reduce.py` | the pre-registered tests, on the data of both cards |
| `registered/exp_test.py`, `registered/exp_test_v3.py`, `registered/tdist.py` | verbatim copies of the pre-registered test scripts (`validate3/inv/heat-work/exp_test.py`, `validate3/heat-verify/exp_test_v3.py`, `validate3/inv/heat-work/tdist.py`), imported unchanged by `reduce.py` |

sha256 of the registered copies (identical to the scratch originals written on 25 Sep before any run):
`exp_test.py` e783ecd0f5a5d53009106c99f80bfbb8c45f1471d145599742f872ea022fb371,
`exp_test_v3.py` 85a13138873ff890368b13c46b5102046f721ce2ba90f611ccc13a8334d37a2b,
`tdist.py` 8aff2a423bcfac63491694edeb739cc4d31d0bd3638185638a74fa8f47fc358d.

## What a pass does

`block.sh <pass>` runs `run_wire.py`'s pass loop in bash, so that every device call goes through `lib.sh`:

1. `others_present && exit 3`; also exit 3 if one of our own device processes runs (`ours_running`, which `queue.sh`
   checks too; it stops a manual smoke from starting a second sampler beside a running block, and note that another
   session's fake test binaries named `ettelem`/`enercat_host` under the same uid count); `block_begin wire <pass>` (die read, code hashes), pre-flight: `build/enercat_v2/host/enercat_host`,
   `build/ettelem/ettelem`, and on aifoundry2 `$HEATER` must exist; `wire_cfgs.py` writes the pass's order
   (`order.tsv`, `order.json`); `--check-runner` notes in `run.log` whether this tree's `run_wire.py` still matches the table.
2. **Pass 1 only (WIRE-FILL):** 12 separate launches before heating and before the sampler, each
   `hold10 enercat_host --pattern P --operands O --slice-bytes 32K --seconds 0.3 --window 60000000 --dump-slice 1024 --budget 8`
   for (tstore_raw bern:0.25), (tstore_raw alt:64), (tstore_raw frz), (tstore_uniq uq:0.25), 3 each, into
   `dump/dump_<O>_<r>.txt`; `wire_check.py dump` compares every DUMP word with its EXPECT word. `WIRE_DUMPS=1` repeats
   them in another pass (only if pass 1's were incomplete).
3. aifoundry2: `heat_to 76` (the curve in `heat.jsonl`); the block fails if the heater gives up.
4. `start_sampler telemetry.jsonl <28 x 18 + 300 s>` (10 Hz), 8 s settle.
5. For each configuration, in the order `random.Random(seed).shuffle` gives, seed 31 + pass - 1 on aifoundry2 and
   41 + pass - 1 on aifoundry3 (block pass N has the order of the runner's pass N-1 under `--seed 31` / `--seed 41`):
   - stop with exit 3 if another user's device process appeared; check the sampler (dead, or no new line since the last
     configuration: `stop_sampler` (SIGTERM), `start_sampler`, logged in `run.log`);
   - aifoundry2: if the die, read from the running sampler's last line (not `die_c`, which would open the management
     node), is below 69 C, one `hold10 $HEATER --test fma --type fp32 --pattern none --values randn --shires 0xffffffff
     --per-shire 32 --seconds 2 --seed 1`, marked `heater` in `marks.jsonl`;
   - prefill: `hold10 enercat_host --pattern tstore_uniq --operands uq:P --slice-bytes 32K --scp --seconds 0.3 --window 60000000 --budget 8`, marked `fill`;
   - 5 s idle; burst: `hold10 enercat_host <configs.json args> --seconds 3 --window 240000000 --budget 8` (8 launches of
     0.4 s, about 3.2 s), its `ENERCAT {...}` lines appended to `runs.jsonl` as `{"host", "pass", "cfg", ...}`; 4 s idle.
6. 8 s idle, `stop_sampler`, `wire_check.py pass` (first removes truncated JSON lines from `runs.jsonl`, `marks.jsonl`
   and `telemetry.jsonl`, counted in the note: `analyze_wire.jl` raises on one and the reduction would lose the whole
   pass; then writes `pass_check.json` and prints the note for `block.json`), gzip the telemetry, `block_end ok|fail`.
   The block fails only if the telemetry is empty or no burst launched (for `--smoke`: also if a configuration did not
   launch, a dump is missing, differs or comes from a failed launch, or the heater failed).

Before `block_begin`, a directory of the same pass left by an interrupted attempt (no `block.json`), or any earlier
attempt when `V3_FORCE=1` is set, is moved aside to `p<N>.attempt-<epoch>` (as `queue.sh` does), because the block
appends to `runs.jsonl`, `marks.jsonl` and `telemetry.jsonl` and two attempts would merge into one burst. A pass whose
`block.json` exists is skipped by `block_begin` ("already done", exit 0), so to repeat a failed smoke run
`V3_FORCE=1 bash tools/claims-v3/wire/block.sh 1 --smoke` (or use the next pass number).

`--smoke` (`wire-smoke/p<N>`): one dump launch of each of the 4 fills, the sampler, on aifoundry2 one forced mid-pass
heater launch, then two configurations with the real timings (wu/p0.5/hop4: `--hop-distance` with `--uniq-regions`;
wsep/p0/hop5: `--pairs`), 2 s settle and 1 s tail. About 45 s of card time (35.6 s wall against fake binaries).

## Card minutes

E32 took 12.9 s per configuration on both cards (fill 0.56-0.60 s, 5 s, burst 3.2 s, 4 s).

| | aifoundry2 | aifoundry3 |
|---|---|---|
| one pass (28 configurations, settle, tail, sampler start, die reads) | ~6.5 min + `heat_to 76` (~0.5-2 min from a 70-75 C die) + up to 28 x 2.5 s of mid-pass heater (0 in E31/E32) = ~8-9.5 min | ~6.5 min |
| pass 1 extra (12 dump launches) | ~0.5 min | ~0.5 min |
| 6 passes | ~50-57 min | ~40 min |
| smoke | ~45 s | ~40 s |

The plan's 45 / 38 min assumed one runner invocation; the extra on aifoundry2 is the per-block `heat_to 76`. Passes
are separate blocks, >= 30 min apart with other experiments between (PLAN3 §2.13). A block is ~7-10 min; the worst case
on aifoundry2 (`heat_to` using all 150 tries, ~9 min, then a heater before every configuration) is ~18 min, under the
~35 min block limit.

## What is dropped, and why

- A **burst** (one configuration in one pass) is dropped by `workloads/enercat/analyze_wire.bursts()`, as registered:
  any sample in the burst or its idle brackets off 600 MHz; a starved sampler (median `took_ms` > 60 in the burst);
  too few samples (< 5 in the burst or < 4 in the bracket before it).
- On aifoundry2 a burst is also dropped if any of its launches has an implied clock (`cycles_max / wall_s`) outside
  0.595-0.605 GHz (PLAN3 R-clock). In the committed E32 runs the implied clock was 0.5990-0.5997 GHz on both cards, so
  this drops nothing unless the clock moved between samples.
- A **pass** is not used unless its `block.json` says `"status":"ok"`; `p<N>.attempt-*` directories (set aside by
  `queue.sh`) are never read.
- A statistic that cannot be computed in a pass (a burst it reads directly was dropped) skips that pass. A line fit
  (`exp_test.sl`) still uses a pass that keeps >= 3 of its points, as the registered code does.
- Per item and card the first **six** passes (by pass number) with a value are used. **Re-run rule (operator):** when a
  block's note shows bursts marked for dropping or configurations not launched, add one more pass on that card with the
  next number (`wire 7`, ...); it then replaces the lost repeat for the items that lost it.

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
   number (1-6), not the runner's 0-2.
3. **aifoundry2 starts every pass on a die >= 76 C** (`heat_to 76`, binding rule), and keeps the runner's mid-pass
   heater below 69 C (`--warm-c 69`, as the plan's command). aifoundry3 runs no heater (the plan's aifoundry3 command
   has no `--warm-c`; `$HEATER` there would be `build/sparsity/...`, never called).
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
8. **Implied clock** (R-clock) is applied per burst, at the granularity of the plan's WIRE drop rule, on aifoundry2 only.
9. A foreign device process appearing mid-pass ends the block with exit 3 (the queue retries it later); logins alone
   do not.

## How to reduce

Collect `build/claims-v3/<card>/wire/` from both hosts into one directory laid out like `DATA_ROOT`, then, from the
tree root on aifoundry2 (numpy needed):

    python3 tools/claims-v3/wire/reduce.py --data <dir>/ --out <dir>/wire-verdicts.json \
        --beside docs/reports/data/2026-09-24-wire2-aifoundry2 docs/reports/data/2026-09-24-wire2-aifoundry3

`<dir>` holds `aifoundry2/wire/p1..p6` and `aifoundry3/wire/p1..p6`. `--beside` (optional) prints the committed
3-pass values next to the new ones, never in a test. It works on partial data (one card, fewer passes) and then says
INSUFFICIENT. Output: `{"exp", "cards": {per card: passes used/skipped, bursts kept/dropped with reasons, implied
clock range}, "outcomes", "items": [...]}`; each item has `item`, `claims`, `per_card` (n, mean, lo99, hi99, vals,
passes, status; board items also `secondary_noleak`, descriptive), `test`, `outcome`, `registered_verdict`, `reading`.

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
