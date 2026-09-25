# V3-RL: rings, levels and relay energy with spin brackets and controlled scratchpad contents

PLAN3 section 2, "V3-RL" (docs/reports/data/2026-09-25-claims-v3/PLAN3.md). It merges energy-manual EXP-EM3,
memhier-onchip-X3 and ridge-X4 (reduction only), and tests 30 claims through 9 pre-registered items
(RL-a, b, c, d, f, g, h, X3, X4). There are 6 passes per card, one block per pass, at least 30 minutes apart.

```
bash tools/claims-v3/rl/block.sh <pass>            # one pass on the local card (queue line: "rl <pass>")
bash tools/claims-v3/rl/block.sh <pass> --smoke    # every component once, about 20 s of device time
V3_DRY=1 bash tools/claims-v3/rl/block.sh <pass>   # print every device call, touch nothing
python3 tools/claims-v3/rl/reduce.py --data <dir with aifoundry2/ aifoundry3/> --out verdicts.json --flop abla_flop.json
```

## What one pass does

A pass runs on one card. Everything is relative to the tree root (`lib.sh` cds there), so the same script runs in
this repository on aifoundry2 and in `~/nekko` on aifoundry3. Every device process goes through `hold10`
(`timeout 10`) and gets `--budget 8`.

1. **Heat** (aifoundry2 only, `heat_to 76`; it does nothing on aifoundry3). The sampler is off while this runs,
   because `heat_to` opens the management node.
2. **Half A: rings.** The half gets its own 10 Hz sampler (`start_sampler`, with retries and one drain). After
   8 s of idle it runs: `nocbench --test spin` (label `nspin-first`), then the eleven rings `pair neigh shire
   xshire1 xshire16 xshire8 xshire2 xshire4 xshire6 shire-c4 xshire1-c4` (`--test shift --rings R --count 32|4`,
   reversed on even passes), then `nocbench --test spin` again (`nspin-last`). Each burst is 5 s of launches
   (`--seconds 5`) followed by 10 s of idle. The sampler stops with SIGTERM.
3. **Heat.**
4. **Half B: levels.** Its own sampler, then: `memhier --test spin` (`mspin-first`); the ABBA group; `l1`, `l3`,
   `dram`; a prefill; `scp-remote`; `memhier --test spin` (`mspin-last`).
   - The ABBA group on odd passes is `l2-1, prefill, scp-local-1, scp-local-2, l2-2`. On even passes it is BAAB:
     `prefill, scp-local-1, l2-1, l2-2, scp-local-2`.
   - Each prefill is `enercat_host --pattern tstore --operands zeros|random --slice-bytes 64K --scp --seconds 0.3
     --window 60000000 --budget 8`: zeros on odd passes, random on even passes.
   - Each prefill sits in its own 10 s idle gap, so it falls in no burst's idle bracket.
   - The memhier arguments are the ones in `run_rings_levels_power.sh`.
5. **Heat.**
6. **Relay.** Its own sampler, then `onchip_host --test relay --medium dram|scp|hop --stage-bytes 1M --stages
   640|19000|7800 --work 1 --budget 8`, launched back to back for 8 s per medium, with 10 s of idle after each
   medium.
7. **Quality check.** The block then:
   - counts the samples that are off 600 MHz (on aifoundry2 any such sample fails the pass; on aifoundry3, which
     is pinned, the count is recorded and the reducer's burst rule applies);
   - checks that every label and both prefills produced output;
   - checks that every launch exited 0 and that every half has more than 300 samples;
   - gzips the telemetry.

   If any check fails, the block ends `fail` (exit 1) and `quality.json` records why. queue.sh does not retry a
   failed block by itself: run the same schedule line again later (the queue skips passes whose `block.json` says
   `ok` and sets a failed attempt aside as `p<K>.attempt-<ts>`). If another user logs in between the halves, the
   block stops with exit 3 and the queue retries the pass after 10 minutes.

   **Early stop.** A launch that hits the 10 s cap (exit 124 or 137), or a third failed launch in a pass, stops
   the pass at once: the sampler is stopped (SIGTERM), the telemetry so far is gzipped, and `block.json` says
   `fail`. The pass has to be re-run anyway, and the card is not held for the rest of it. The same path runs on
   SIGTERM/SIGINT, on a sampler that will not start, on a heat that gives up, and on another user arriving. The
   smoke does not stop on failed launches (it reports them all), only on one that hits the cap.

   **Never two of ours.** Besides `others_present`, the block exits 3 at its start, and stops with exit 3 between
   the halves, when one of our own device processes is still running (`lib.sh` `ours_running`): a smoke started
   by hand while the queue runs another block, or a sampler that did not exit.

Output goes to `$DATA_ROOT/rl/p<K>/`:
- `pass.json`: the order and the contents of this pass
- `heat-{A,B,relay}.jsonl`
- `A/`, `B/`, `relay/`: each holds `telemetry.jsonl.gz`, `runs.jsonl`, `marks.jsonl` and `launches.jsonl` (the
  exit code of every launch). `B/` also holds `prefill.jsonl`.
- `quality.json`, `block.json`

Raw data is under 0.5 MB per pass (gzipped telemetry).

**Card minutes per pass:**

| part | minutes |
|---|---|
| half A | 3.6 (13 bursts x ~15.7 s, plus 14 s of lead and tail) |
| half B | 3.3 (10 bursts, 2 prefills) |
| relay | 1.2 |

That is about 8 minutes per pass on aifoundry3, of which about 35% is device time and the rest is sampler idle.
aifoundry2 adds three heats of about 0.5 to 2 minutes each, so a pass takes about 10 to 13 minutes. Over 6 passes
the total is about 50 minutes on aifoundry3 and 60 to 80 minutes on aifoundry2 (the plan estimated 43 and 72).
Each block stays well under 35 minutes.

**Smoke** (`--smoke`, exp `rl-smoke`) runs every component once. Bursts are 0.5 s with 1 s gaps:
- nocbench spin, the `pair` ring and the `xshire1-c4` ring;
- memhier spin, l1, l2, l3, dram, a zeros prefill, scp-local and scp-remote;
- one relay launch per medium;
- on aifoundry2, one 1 s heater launch and one `die_c` after the sampler stops.

That is about 40 s of wall time and 15 to 20 s of device time. The smoke fails if any label is missing or any
launch exits non-zero. To repeat it, use `V3_FORCE=1` or another pass number.

## What is dropped, and why

- **Bursts.** A burst is dropped when the minion clock was off 600 MHz in more than 2% of its samples, or when the
  sampler's median latency during the burst was over 60 ms. This is the V3-RL rule, the same as
  `analyze_reruns.py`. On aifoundry2, xshire16 starves the management path (sampler medians of 75 to 146 ms on
  23 Sep), so it is always dropped there, and the xshire16 items are INSUFFICIENT on aifoundry2.
- **Passes.** An aifoundry2 pass is dropped whole, and re-run, when any telemetry sample in it is off 600 MHz.
  This is PLAN3's common rule ("aifoundry2 repeats with any sample off 600 MHz are dropped and re-run"), which is
  stricter than the burst rule. The block marks such a pass `fail` right away, and the reducer checks again.
  aifoundry3 is pinned at 600 MHz and has no pass-level rule: an off-600 sample there only drops a burst whose
  samples are more than 2% off (the V3-RL burst rule). The reducer also skips passes whose `block.json` status is
  not `ok`, dry runs, and `p<K>.attempt-*` directories (earlier attempts that the queue set aside).
- **Parity.** A re-run keeps its pass number, so it keeps its parity: its contents (zeros or random) and its
  order. RL-h needs 3 kept passes of each contents on each card, so a card needs all of passes 1 to 6.

## Deviations from the plan's commands, and why

1. **Where the runner lives.** The plan asked for new runners `tools/ettelem/run_rl_spin_v3.sh` and
   `run_onchip_power10.sh` next to the originals. Their logic is instead in `block.sh`, as the framework
   requires. Nothing is placed next to an original, and the paths resolve from `lib.sh`'s `V3_ROOT`, not from
   `$(dirname $0)/../..`.
2. **The prefill does not cover all of memhier's buffer.** The plan made this a precondition ("First confirm in
   memhier's kernel that the scp-local buffer starts at the enercat slice base"), and the sources show the two
   bases differ:
   - memhier's scp-local and scp-remote buffers start at scratchpad offset 0: `stream_base` is 0 for the
     scratchpad, and minion m reads `[m*64K, m*64K+64K)` (`workloads/memhier/kernel/memhier.c`, `MH_SCP_ADDR`).
   - enercat writes its slices from offset 256 KB: `a.scp_off = 256 * 1024` in `workloads/enercat/host/main.cpp`,
     so minion j writes `[256K + j*64K, ...)`.
   - The prefill therefore covers the buffers of memhier minions 4 to 31, which is 28 of 32, or 87.5% of the bytes
     each scp-local and scp-remote burst reads. The first 256 KB cannot be prefilled: a tensor store at scratchpad
     offset 0 faults (docs/findings/18-on-chip-relay.md), and no existing binary writes there.
   - No tool in this repository writes that region (enercat and onchip start at 256 KB), so its contents should
     be the same in every pass and on both contents arms, unless another user's work writes it. The
     zeros-versus-random contrast is diluted by one eighth, and "equal contents" means equal on 87.5% of the
     bytes.
   - The registered bands are kept unchanged (no new freedom). The owner may prefer to amend RL-h before the first
     run.
3. **Labels.** `analyze_reruns.reduce_dir` merges every run that shares a label into one span. The ABBA bursts
   are therefore labelled `l2-1`, `l2-2`, `scp-local-1` and `scp-local-2`, and the brackets `nspin-first`,
   `nspin-last`, `mspin-first` and `mspin-last`. Prefill output goes to `prefill.jsonl`, not `runs.jsonl`, so it
   is not reduced as a burst.
4. **Prefill placement.** A prefill runs after the previous burst's 10 s gap and is followed by another 10 s gap.
   `reduce_dir` brackets a burst with idle from `[prev_end+3 s, prev_end+8 s]` and `[start-6 s, start-0.3 s]`, so
   neither bracket sees the prefill. The plan registered a prefill before scp-remote as well, and it is kept,
   although nothing writes the scratchpad between the ABBA group and scp-remote.
5. **Relay.** `hold10` replaces `timeout 40`, and `--budget 8` is added (onchip's default is 8 s anyway). The
   relay order `dram, scp, hop` is not reversed on even passes, because the plan reverses only the ring order.
6. **Samplers.** There is one sampler per half and one for the relay ("ettelem sample --every-ms 100 for each
   half"). Each is stopped before the next `heat_to`, because nothing else may open the management node while a
   sampler runs.
7. **Stricter pass handling than the plan wrote.**
   - The pass-level off-600 rule on aifoundry2 (the V3-RL line names only the 2% burst rule; PLAN3's common rules
     and the lab rules require it for aifoundry2).
   - Block failure on a non-zero launch exit, a missing label, or a short half, and the early stop above.
   - The mid-pass check for other users, and the start and mid-pass check for our own device processes (exit 3).
8. **Flags checked against the sources** (`workloads/*/host/main.cpp`): nocbench and memhier `--budget`,
   `--seconds` and `--count`; memhier `--scp-shift`; enercat `--pattern tstore`, `--operands`, `--slice-bytes`,
   `--scp`, `--window` and `--budget`; onchip `--medium`, `--stages`, `--stage-bytes`, `--work` and `--budget`.
   All of them exist in this tree. enercat `--budget`, `--scp` and the 256 KB offset have been in its committed
   source since its first commit (23 Sep, the energy manual whose catalogue ran `tstore --scp` on aifoundry3).
   The smoke confirms the aifoundry3 builds before the queue runs.
9. **The heater.** On aifoundry2 the heater is `lib.sh`'s `HEATER` (sparsity_t2). aifoundry3 needs no heater:
   `heat_to` returns at once there, and the smoke skips the heater launch.

## Reduction (reduce.py)

`--data` points at a directory holding `aifoundry2/` and `aifoundry3/`, each laid out like `DATA_ROOT`. Run the
reducer inside a repository tree, because it reads these committed files:
- the 23 Sep rl-passes (the byte side of RL-X4);
- the 23 Sep catalogue (the bracket low edge of RL-f);
- the ridge-points page (the RL-X4 ridges).

It works on partial data: one card, or fewer passes. An item without 3 kept passes per card is INSUFFICIENT.

- **Burst reduction.** A verbatim copy of `tools/ettelem/analyze_reruns.reduce_dir`: bracketing idle,
  leakage-corrected. It was checked against the repository function on all 23 Sep rl and relay passes: 660
  fields, largest difference 0. pJ/B is over-idle W x span / bytes. A level with two ABBA bursts takes the mean
  of the kept ones. A spin takes the mean of its kept first and last brackets.
- **Statistics.** 99% t intervals on pass-level values, and Welch between cards. The t quantiles are computed
  without scipy and match the plan's table: 9.925, 5.841, 4.604 and 4.032.
- **Outcomes.** Each item is split into its parts. Every entry has `item`, `part`, `claims`, `per_card`, `test`,
  `outcome`, `prediction_held` (whether the registered numbers came true) and `reading`.

| item | what is computed | outcome rule |
|---|---|---|
| RL-a | Slope of pJ/B against mean hops over `xshire8/1/4/2/6`, per pass | Welch 99% of a2 - a3 excludes 0 -> CARD-DIFFERENT; else PASS with the pooled slope (+-50% on the page) |
| RL-b | intercept - shire ring - slope, per pass | Decided on aifoundry2: 99% interval > 0 -> PASS; else FAIL. aifoundry3 is printed |
| RL-c | shire-c4 - shire, and xshire1-c4 - xshire1, per pass | Decided on aifoundry3: interval > 0 -> PASS. aifoundry2 is printed |
| RL-d | Per-pass relay DRAM/hop ratio, and relay DRAM pJ/B | Welch 99% on logs, a2 vs a3: excludes 0 -> CARD-DIFFERENT; else PASS (pooled) |
| RL-f | Relay scp minus the catalogue low edge, per catalogue pass: mean of l1fill/stride32/zeros and tstore/scp/zeros, as `rings_relay_extra.py` | Welch interval < 0 on both cards -> PASS ("8% below its bracket"); on one card -> CARD-DIFFERENT; neither -> FAIL ("at the low edge") |
| RL-g | L1 a2 - a3; own scratchpad a3 - a2 (as RL-a); L2 - scratchpad per card, paired within the pass over the four ABBA bursts | Welch excludes 0 -> CARD-DIFFERENT; both card intervals contain 0 -> PASS ("the same within +-10%"); one card contains 0 -> CARD-DIFFERENT; both exclude 0 on the same side -> FAIL |
| RL-h, part 1 | Per card, the zeros-pass mean of scp-local and the random-pass mean | Each mean in its band (1.7-2.3 and 3.7-4.7) on both cards -> PASS; on one card -> CARD-DIFFERENT; else FAIL |
| RL-h, part 2 | Welch a3 - a2 within each contents group | Excludes 0 in either group -> CARD-DIFFERENT; else both point differences within +-0.1 -> PASS ("the difference is contents"); else FAIL |
| RL-X3 (a) | For each of the 11 rings, per pass: nocbench spin W - ring W over idle | Interval > 0 on both cards -> PASS ("less than spinning"); on one card -> CARD-DIFFERENT; else FAIL ("about as much as spinning (+-x W)"). The noleak and before-only variants are reported as a robustness check |
| RL-X3 (d) | Each pass's spin W | In band on every pass (nocbench 2.2-2.6, memhier 2.3-2.8): on both cards -> PASS; on one card -> CARD-DIFFERENT |
| RL-X3 (e) | Per pass, the mean W of pair/neigh/shire against the mean of the five 1 KB xshire rings; and scp-remote pJ/B against min(xshire8, xshire16 if kept) | Holds on every pass (the min-inside against max-across margin is printed too): on both cards -> PASS; on one card -> CARD-DIFFERENT |
| RL-X4 | Balance interval [byte lo / FLOP hi, byte hi / FLOP lo] per card, for the three rows | Both cards on the predicted side -> PASS; both on the other side -> FAIL; opposite sides -> CARD-DIFFERENT; any overlap -> FAIL ("ranges overlap: no verdict") |

More on RL-X4:
- The byte side is the 23 Sep passes plus the V3-RL passes, as registered. The item is still INSUFFICIENT until
  V3-RL itself has 3 kept passes on each card, so that the old passes cannot carry it alone.
- The three rows are: L3 random against the spec ridge of 3.0; other shire random against 3.0; and in-shire
  TensorSend (the shire ring) zeros against the measured ridge of 8.78.
- The FLOP side comes from V3-ABL-A through `--flop`, a JSON file of this shape:
  `{"unit": "pJ/FLOP", "aifoundry2": {"random": [one value per ABL-A block, fp32 randn], "zeros": [fp32 zeros]},
  "aifoundry3": {...}}`. With `"unit": "pJ/MAC"` the values are halved. Without `--flop`, RL-X4 is INSUFFICIENT.

**Known limits of the registered rules.** The code implements them as written.
- **RL-g's scratchpad parts are confounded by the contents arm.** Every V3-RL pass is prefilled, zeros and random
  alternating on the same schedule on both cards. "Own scratchpad a3 - a2" over all passes, and "L2 - scratchpad",
  therefore mix two contents, and their intervals widen to about +-2 pJ/B. They will read PASS through variance
  inflation. The readings say "confounded", and `info_by_contents` gives the per-contents values. RL-h is the
  meaningful test. The owner should decide before the first run whether these two parts are replaced by RL-h.
- **RL-f is limited by the catalogue side.** The low edge has 3 catalogue passes per card with an sd of about
  0.15 pJ/B, so the Welch interval stays near +-0.5 pJ/B even with 6 new passes. On the 23 Sep data it was
  [-0.86, +0.16] on aifoundry2. The expected result is "at the low edge" unless V3-CAT's new catalogue rows are
  admitted, which is not registered.
- **RL-b and RL-c are decided on one card each, as registered.** The other card's interval is printed.

**Tests** (in `validate3/drv/rl/`):
- `legacy/`: the 23 Sep passes rearranged into this layout. The reducer reproduces the registered reducers'
  numbers: a2 slope 2.27 [1.29, 3.25]; a3 1.33 [0.13, 2.52]; Welch +0.945 [0.208, 1.681]; a2 step 3.25
  [-3.48, 9.98]; L1 0.86 and 0.68; scratchpad 2.40 and 2.63.
- `gen_synth.py`: synthetic passes with known injected values in this exact label scheme, with leakage, drift,
  noise and a starved aifoundry2 xshire16. It recovers the injected values and gives the expected outcomes.
  Further cases: partial data (one card, 2 passes: all INSUFFICIENT), an aifoundry2 pass with one sample off
  600 MHz (dropped, so RL-h is INSUFFICIENT; the same sample in an aifoundry3 pass drops nothing), dry-run output,
  and an empty directory.
- `review/gen_fail.py`: a data set built to fail (no leaving-the-shire step, no small-message cost, spins out of
  band, rings drawing as much as spinning, scp-remote dearer than the rings, L3 below its ridge, relay scratchpad
  above the low edge, scratchpad levels that ignore the prefill). The reducer gives FAIL on each of those items.
- `faketree/`, `review/faketree/`: `block.sh` run against a fake device layer. This covers a clean pass, off-600
  samples on each card, a launch that exits 124, three launches that exit 2, a failed relay medium, a heat
  failure, another user arriving mid-pass (exit 3), SIGTERM mid-pass, and the smoke (clean, with a failed
  prefill, and with a relay launch at the cap). In every case each sampler start is matched by a stop.
