# V3-LAT: latency, cycle-count and bandwidth sweeps (PLAN3 §2 "V3-LAT", MUST, 104 claims)

The blocks re-run, on both cards, the memhier pointer chases (memhier-onchip X1), the nocbench latency and
collective probes (X2), the sparsity cycle-count sweeps and their extras (matmul-sparse-testdrive E4), the scalar
SGEMM (E5), the enercat lone-minion DRAM streams (ridge-X3), the hot-line sweep (E-HL1) and the relay sweep (E-RL1).
On aifoundry2 each pass also runs V3-COOL's steady-600 warm controls (E-HL2 / E-RL2 warm block). The reducer tests
the 16 registered items LAT-M1 ... LAT-R.

Files: `block.sh` (one block), `reduce.py` (verdicts), `make_ref.py` + `ref_committed.json` (the committed per-card
values three items compare against, fixed before the first run), this README.

## Running

```
bash tools/claims-v3/lat/block.sh 1 --smoke          # smoke test, < 1 min of card time; data in $DATA_ROOT/lat-smoke/p1
V3_DRY=1 bash tools/claims-v3/lat/block.sh 11        # print every device call of a block, touch nothing
```

Pass numbers (the `<pass>` of a queue line `lat <pass>`):

| pass | block |
|---|---|
| 1 2 3 | the whole pass K in one block (recommended on aifoundry3: ~11 min) |
| 11 12, 21 22, 31 32 | the first / second half of pass K (recommended on aifoundry2: ~10-17 min each) |
| 4 5 | divergence-only short blocks (E4 (f): with passes 1-3 they are the 5 registered blocks) |
| 6-9 (61 62 ... 92) | a re-run of a dropped pass (an aifoundry2 pass with launches off 600 MHz) |
| 41-49 | a re-run of a dropped divergence block |

Schedule (PLAN3 §2.13): passes of LAT on one card >= 30 min apart with other experiments between them; the two
halves of a pass may be separated by other blocks. Suggested aifoundry2 queue lines: `lat 11`, `lat 12`, ... ,
`lat 31`, `lat 32`, `lat 4`, `lat 5`; aifoundry3: `lat 1`, `lat 2`, `lat 3`, `lat 4`, `lat 5`.

## What a pass does

Nine units in a per-pass shuffled order (`shuf --random-source=<(yes K)`, the same on both cards), plus `c6` on
aifoundry2. A half-pass block runs the first or second part of that order, cut where the estimated aifoundry2
minutes balance (`c6` joins the lighter half). The order is written to `order.json`.

| unit | what | processes | a2 min | a3 min |
|---|---|---|---|---|
| mc | memhier `run_lab.sh` group `chase`, commands copied verbatim (9 chases, 3 s apart) | 9 | 3-4 | 2.5 |
| ms | memhier group `scp` (local scratchpad sweep, 4 scratchpad-map rows from shires 0/7/24/31) | 5 | 1.5-2.5 | 1 |
| noc | nocbench `run_lab.sh` groups `classes counts stream functs` / `matrix sync` / `allreduce barrier xallreduce loaded` (the a2 plan's three invocations, heat before each); even passes run the 10 groups in reverse | 32 | 4-6 | 2.5 |
| sp | sparsity `run_lab.sh` groups `fma tload gemv diverge` (heat before each group on a2) | 44 | 5-7 | 2.5 |
| e4x | E4 extras: all-minion TensorLoad from L2 at 2,000/20,000/200,000 loads and from DRAM at 2,000/20,000; layer draws `--seed 2`, `3`; the divergence subset (static/refill at alpha 3 and 2, seed 1) | 11 | 1-2 | 0.6 |
| x3 | ridge-X3: enercat `tload_pat` 1 KB DRAM streams from one minion and from minion 0 of all 32 shires (3 s each, shuffled) | 2 | 0.5-1.5 | 0.3 |
| sg | E5: `sgemm_host` n=64/1 shire, 512/1, 512/32, 1024/32, `--reps 3`, under `/usr/bin/time -v` | 4 | 1-1.5 | 0.7 |
| hl | E-HL1: the 42 `run_hotline.sh` configurations + the plan's 35 extras (edge N=19,21-23; N-minion baselines; knee P=9000-10500; windows 3e6/24e6/60e6 x 4 homes; pollers; warm-up 0/10), shuffled | 77 | 1-2.5 | 0.5 |
| rl | E-RL1: 2 probes + the 86 `run_onchip.sh` relay rows + offsets d = 1..31, shuffled | 119 | 1-2.5 | 0.6 |
| c6 | aifoundry2 only, for V3-COOL: `run_hotline_power.sh`'s 5 labels x 3 launches of 2 s windows (8 s idle first, 10 s gaps), then 20 relay DRAM `--stages 640` + 10 hop `--stages 7800` | 45 | 2.5-3.5 | - |
| div | (blocks 4, 5, 41-49 only) the divergence subset | 4 | 1-2 | 0.2 |

Card minutes per pass (card held by the block, heating included): **aifoundry2 ~20-30** (two halves of ~10-17;
the spread is the heater, which runs before every unit, nocbench invocation and sparsity group whenever the die
reads < 76 C), **aifoundry3 ~11**; divergence blocks ~1-2 (a2) / < 1 (a3); smoke < 1 min of device time (~1.5 min
wall on a2). Three passes + two divergence blocks: aifoundry2 ~65-95 min, aifoundry3 ~35 min (plan: 95 / 46).

Every device process runs under `hold10` (timeout 10) and, where the host has it, `--budget 8` (memhier, nocbench
`run_lab` commands, sparsity, enercat; onchip and sgemm default to an 8 s budget). The block checks for other
users before every launch and stops (block.json "fail", exit 3, so queue.sh sets the attempt aside and retries) if
anyone appears. On aifoundry2 a unit whose sampler cannot start stops the block (its launches could not be kept).
Telemetry, `.err` files and `stderr.log` are gzipped at the end of the block.

Output (`$DATA_ROOT/lat/p<pass>/`): `block.json`, `code.sha256`, `order.json`, `marks.jsonl` (unit begin/end,
reheats, notes), `heat.jsonl` (a2 heating curves), and one directory per unit: the host printouts under the
`run_lab.sh` file names (`<name>.jsonl` / `.err.gz`), `sweep.jsonl` + `configs.txt` + `order.txt` (hl, rl; each
line carries `group`, `cfg`, `host`, `pass`), `sgemm-<i>.log` + `brackets.jsonl.gz` (sg), `runs.jsonl` +
`relay.jsonl` + `marks.jsonl` (c6), `launches.jsonl` (every process: name, rc, host start/end ms) and
`telemetry.jsonl.gz` (ettelem 10 Hz). The COOL reducer reads `c6/` (runs.jsonl labels as in run_hotline_power.sh;
relay.jsonl groups `rl2-dram` / `rl2-hop`); LAT's reducer does not use it.

## What is dropped, and why

aifoundry2's governor lifts the clock off 600 MHz below ~68 C, and memory-bound cycle counts depend on the
minion/NoC clock ratio, so on aifoundry2 (never on aifoundry3, which is pinned):

- any launch whose telemetry samples within 0.2 s of it (or, if none falls there, the nearest sample on each side,
  each within 5 s) read `mhz.minion != 600`, or that has no sample at all, or whose cycles / wall time exceeds
  0.6 GHz (the host's `ghz` field, or `cycles_max / wall_s`) (plan: sampler rule of V3-LAT);
- any memhier chase whose `analyze.py` `point_ghz` is >= 0.65 (LAT-M2's rule; applied to every chase);
- any sgemm process unless the sampler bursts right before and right after it all read 600 MHz.

At the end of every aifoundry2 unit the block counts the unit's samples (sampler and sgemm brackets) that read
`mhz.minion != 600`; if there are any it writes an `off600` mark to `marks.jsonl` and a note into `block.json`, so the
operator sees that a pass needs a re-run without running the reducer (which still decides launch by launch).
A pass (or short block) counts for an item only if every launch that item uses in it is kept. A dropped pass is
re-run as pass 6-9 (divergence: 41-49) until each item has 3 kept passes (5 short blocks for LAT-S5).

## Deviations from the plan's commands (the sources win)

1. **One sampler for everything.** The plan logs the clock with `run_lab.sh`'s `dev_mngt_service` loop (clock.csv,
   memhier/nocbench/sparsity) and ettelem for the rest. The rules for these blocks allow samplers only through
   lib.sh's `start_sampler`/`stop_sampler` and nothing else on the management node while one runs, so every unit runs
   the 10 Hz ettelem sampler instead (it also gives the die temperature); there is no clock.csv. The host programs
   memhier, nocbench, sparsity, enercat and onchip open only the ops node (`createPcieDeviceLayer(true, false)`).
2. **`run_lab.sh` is not called**; its commands, file names, order within a group and pauses (3 s memhier/nocbench,
   2 s sparsity) are copied into `block.sh`, so every device call goes through `hold10` (visible in a dry run) and so
   its `wait_free` (which waits for the et_soc1 use count to reach 0) does not wait out our own sampler.
3. **sgemm opens the management node itself** (`createPcieDeviceLayer(true, true)`, workloads/sgemm/host/main.cpp:49).
   The plan starts ettelem before it; that would put two openers on the node. Instead a ~1 s sampler burst runs right
   before and right after each sgemm process (the burst between two processes serves as both, 2-3 s from each: 5
   sampler starts per unit instead of 8). `/usr/bin/time -v` runs inside `hold10` (`timeout 10 /usr/bin/time -v
   sgemm_host ...`; timeout signals its whole process group), not outside it. Without `/usr/bin/time` (check
   aifoundry3) the block notes it, the RSS part of LAT-G has no data, and LAT-G stays INSUFFICIENT on that card.
4. **Heating**: `heat_to 76` before every unit, every nocbench invocation and every sparsity group on aifoundry2 (the
   plan's order line says "before any group whose die reads < 70 C", its E4 detail "before every group"; heat_to
   returns at once when the die already reads >= 76). If the die cannot be read, the block drains the management
   queue once and otherwise continues unheated (the clock rule then drops what ran off 600).
5. **nocbench on aifoundry3** also runs as the three aifoundry2 invocations (no heating there), so the group
   sequence is identical on both cards; even passes (2, and re-runs 6, 8) reverse the 10 groups.
6. **The divergence subset** of passes 1-3 comes from the E4-extras unit (4 launches after a heat), not from the
   `diverge` group of `run_lab.sh`, so all 5 registered short blocks use one procedure; the `diverge` group feeds the
   per-pass parts of LAT-S5.
7. **ridge-X3 order**: the component detail says "right after E4's tload group"; the plan's pass order (shuffled
   units) wins. The 1- and 32-minion streams are shuffled per pass (seed K), as registered.
8. **c6 (V3-COOL warm controls)**: the plan asks for a copy of `run_hotline_power.sh` next to the original with
   `timeout 20` -> 10. The rules for these blocks forbid copies next to originals, so its five labels are inline in
   `block.sh`, under `hold10`, with lib.sh's sampler (not the runner's own start/kill) and heating to 76 C (plan:
   >= 70 C).
9. **Pass halves** (K1/K2) keep blocks under the 35-min limit on aifoundry2; the plan counted a2 passes as 32 min.
10. **Hot-line labels**: extras are labelled `req`, `alone`, `pace` (knee), `win`, `poll`, `warm` as in the plan;
    every line also carries `cfg`, its index in `configs.txt`, because some configurations share all printed fields
    (e.g. `local`, `shires` and `pace` rows at 32 x 32) and the warm-up is not printed.
11. **The scpself bus-error probe** (optional in the plan) is off unless `LAT_SCPSELF=1`; with it, a failed health
    launch afterwards stops the block. Claim hotline-relay-l2-52 is in LAT-H's claim list, but no P-part tests it:
    with the probe on, the reducer reports per pass what it did (`scpself_probe` under LAT-H: exit code, a printed
    line or not, the health launch) for the page's qualifier; it does not enter LAT-H's outcome.
12. **Other users**: the block aborts when someone appears (the plan's run_lab.sh waited up to 120 s per command).
13. **sgemm build on aifoundry2**: already built (build/sgemm/host/sgemm_host, 25 Sep 09:07), no build step here.

## Reducing

```
python3 tools/claims-v3/lat/reduce.py --data <dir with aifoundry2/ and aifoundry3/> --out verdicts.json
```

`<dir>/<card>` is laid out like `DATA_ROOT` (the collected `build/claims-v3/<card>`). Needs numpy; imports
`workloads/nocbench/analyze.py` (MARTY map, `search_layout`), `workloads/memhier/analyze.py` (`point_ghz`) and
`workloads/onchip/analyze_onchip.py` (ring geometry) from the tree, and reads `ref_committed.json`. About 3-4 min
with both cards' full data (LAT-N2's layout search, 12 restarts per pass); `--no-search` skips it (LAT-N2 is then
INSUFFICIENT). It runs on partial data: blocks without an "ok" block.json and units without an "end" mark are
ignored, and every item lacking its kept repeats on a card is INSUFFICIENT. Each item in `verdicts.json` has
`item`, `claims`, `prediction`, `per_card` (values, `n` kept repeats, per-pass details), `test`, `outcome`
(PASS / FAIL / CARD-DIFFERENT / INSUFFICIENT) and `reading`. CARD-DIFFERENT is used only where the registration
lets the page give per-card values. Where it names one page action decided by either card, one card with its repeats
decides and the item is FAIL (the reading says "decided by aN"): "any deviation (mismatch) falsifies" (LAT-S1, the
mismatch part of LAT-G, at any n); LAT-N3 "dropped if the bound is >= +12.02 on either card"; LAT-S3 "the 2,000 -
20,000 difference excludes 0 at 99% on both cards"; LAT-S5 "must exclude 0 with positive sign on both cards to keep
'from alpha = 2'"; LAT-R3 "k_hat above 4.5 on either card" and "(one - 32 minions) excludes 0 positive on both";
LAT-R "(i) fails on either card -> drop". A `block.json` that is not valid JSON (lib.sh writes `"die_c_end":,` when
the die cannot be read at the end) is still read for its status. Non-finite numbers are written as null.

Where the registration leaves a definition open, the reducer uses (fixed here, before any run):

- **LAT-M1**: L1 = sizes <= 512 B, read buffer 768 B-2 KB, L2 4 KB-512 KB of `chase-dram` and
  `chase-dram-sweep-from24`, plus `chase-scp-local` up to 2 MB; the knees hold when 512 B reads L1, 768 B and 2 KB read
  the read buffer and 4 KB reads L2; hart 1 = `chase-dram-thread1`; pointer checks = every chase of mc and ms.
- **LAT-M2**: a requester's L3 (DRAM) value in a pass = the median of its kept 4 MB (256 MB) hart-0 chases; a pass
  counts if each of shires 0/7/24/31 keeps at least one of each (the component detail's rule). The requester effect
  passes if its 99% t interval excludes 0 and overlaps [8.2, 11.2].
- **LAT-M3**: 124 points (31 remote scratchpads x 4 rows); the 6 pairs among shires 0, 7, 24, 31.
- **LAT-N1**: "32-minion allreduce" = the one-tree 32-minion row of `allreduce-c1`; "shire barrier" = both
  `barrier-shire1` and `barrier-shire32`.
- **LAT-N2**: the 1 KB matrix fits split at 5 hops (<= 5, > 5); "blocking credit in shire" = every
  `fcc-inshire-block` pair.
- **LAT-N3**: "99% bootstrap upper bound" = the 99.5th percentile (upper end of the two-sided 99% interval, as the
  plan's other 99% intervals and noc_audit.py); seed 1, 10,000 draws, pairs weighted w_i x w_j. A bound between +6
  and +12.02 is "neither kept nor dropped" and counts as not holding. On the committed 18 Sep data the bound is +9.2,
  so this outcome is likely.
- **LAT-N4**: "all ok" = every nocbench line of the pass.
- **LAT-S1**: "every line ok" = every sparsity line of the `sp` unit.
- **LAT-S2**: the 4-line band "45-47 +- 2" is [43, 49] for both L2 and scratchpad.
- **LAT-S3**: "1-8 lines within 20% of it" = pass-mean c(L) / pass-mean c(16) within +-20%; the 2,000 - 20,000
  difference is paired per pass (L2, 16 lines), 99% t with df n-1.
- **LAT-S4**: us = `cycles_per_layer_mean` / 600 MHz; "masked at 0%" = `gemv-tree-masked` at 0, "plain" =
  `gemv-tree-dense` at 0, "at 99%" = `gemv-tree-skip` at 0.99; seeds 2-3 = the extras at 0.99, each seed's pass mean.
- **LAT-S5**: lane efficiencies equal to 18 Sep at the printed 4 decimals (the 18 Sep draw is aifoundry3's; the
  draw is the same on both cards); throughput = 8 x useful lane iterations / `cycles_mean` x 600 MHz (sparsity
  analyze.py's `tfma_chip_mean`), within 3% every pass; the alpha-2 band applies to the mean over the short blocks.
- **LAT-G**: a pass value = the mean of its 3 launches; "process wall 0.2-0.4 s" is tested on the host's
  `device held for X s total` (the claim's "device held per run"; `/usr/bin/time`'s elapsed, which includes the host
  reference product, is recorded only); held time and RSS on pass means (per pass, the mean over its kept
  processes). A process with no `mismatches` line (timed out, or stopped on a kernel error) is not kept and is listed
  under `incomplete`; it is not a mismatch. A part with fewer than 3 pass means (e.g. RSS on a card without
  `/usr/bin/time`) leaves LAT-G INSUFFICIENT, not FAIL; `launch_times_within_5pct`, `held_in_0.2_0.4` and
  `rss_in_1.5_2.5GB` give the parts separately. Mismatches in dropped (off-600) runs are reported, not counted.
- **LAT-R3**: B/minion-cycle = lines x 64 x iters / `cycles_max` (sparsity) and bytes / participants / `cycles_max`
  averaged over the process's launches (enercat).
- **LAT-H**: host fraction = host ops / (same-pass alone count); P1 uses the 32-minion alone row of the same home
  (as committed), P2/P5/P6 the N-minion alone rows; "stopped" = committed per-card fraction < 1%; stopped counts and
  DRAM-homed fractions are checked per launch; shares = pass-mean share of every shire in the 32-per-shire fairness
  rows and the 4 placement rows; cycles per atomic = `cycles_max / total_ops` (the host's field): fairness rows and
  placement 0 / scp:0 -> 10.00, own / scp:own -> 0.31.
- **LAT-R**: permutation p = (count + 1) / (100,000 + 1), seed 1; geometry g = mean of offsets g and 32-g
  (g = 16 alone); (v) "two-stage ratio" and "advantage" = hop/DRAM; DRAM at 256 MB vs 64 MB = `bigsize` 8 MB vs 2 MB
  per shire (x 32 shires per buffer); committed ratios from `ref_committed.json`.
- Every 99% t interval is two-sided with df = n - 1 (n can exceed 3 when re-run passes exist).

Tested (scratchpad `validate3/drv/lat/`, `make_testdata.py`): the committed runs laid out as one pass per card
reproduce the committed numbers (L3 169.0/160.7/159.3/168.9, matrix 150.0 + 12.02 x hops, stream fits
40.0/85.9/134.8/223.8 + 2.33/4.00/3.00/4.64, hot-line P1 counts, ...) and give INSUFFICIENT everywhere; a synthetic
3-pass set gives PASS on every item but LAT-N3 ("neither", as the committed flag data would) and LAT-N2, where the
repository's annealing search found MARTY's distances in only 10 of 12 restarts on one of six jittered copies of the
18 Sep matrix (the registered "12/12" is sensitive to the search itself, not only to the card); variants give
INSUFFICIENT (a2 with two passes; one 800 MHz sample inside an a2 launch), CARD-DIFFERENT (aifoundry3's L1 at
5.30) and FAIL (an int8 deviation, an sgemm mismatch).

Review variants (scratchpad `validate3/drv/lat/rev/make_variants.py`, built on `synth()`): `fail2` (hot-line edge
N=22 at 50% of alone on both cards; sgemm n=1024 at 18.5 ms on both; a2 L3 from shire 24 +5 cycles; a3 32-minion
enercat at 1.40; a2 relay offsets flat; a3 alpha-2 refill - static = -0.02 T/s) gives LAT-H FAIL (P2), LAT-G FAIL
(launch times, not a mismatch), LAT-M2 CARD-DIFFERENT, and LAT-R3, LAT-R, LAT-S5 FAIL decided by one card;
`normss` (no `/usr/bin/time` lines on a3) gives LAT-G INSUFFICIENT; `timeout` (an a2 sgemm cut short) gives LAT-G
INSUFFICIENT with the run listed as incomplete; `badjson` (block.json with `"die_c_end":,`) reads like synth.
