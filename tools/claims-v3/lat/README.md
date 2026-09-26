# V3-LAT: latency, cycle-count and bandwidth sweeps (PLAN3 §2 "V3-LAT", MUST, 104 claims)

The blocks re-run, on every card (aifoundry2, aifoundry3 and, since 25 Sep, aifoundry1's two cards: section
"Four cards"), the memhier pointer chases (memhier-onchip X1), the nocbench latency and
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
V3_DEVICE=0 bash tools/claims-v3/lat/block.sh 11     # aifoundry1: card 0 (card id aifoundry1-c0); V3_DEVICE=1: card 1
```

On a governor-free card the smoke heats to 76 C first (as before every pass unit; up to a few minutes on a cool die)
and prints the idle probe and the burst clock (`smoke clock: minion MHz inside kernel windows {...}; outside {...}`).
Run it on each of aifoundry1's cards before queueing their passes (section "Four cards").

Pass numbers (the `<pass>` of a queue line `lat <pass>`):

| pass | block |
|---|---|
| 1 2 3 | the whole pass K in one block (recommended on aifoundry3: ~11 min) |
| 11 12, 21 22, 31 32 | the first / second half of pass K (recommended on aifoundry2 and aifoundry1's cards: ~8-17 min each) |
| 4 5 | divergence-only short blocks (E4 (f): with passes 1-3 they are the 5 registered blocks) |
| 6-9 (61 62 ... 92) | a re-run of a dropped pass (a governor-free card's pass with launches off 600 MHz) |
| 41-49 | a re-run of a dropped divergence block |

Schedule (PLAN3 §2.13): passes of LAT on one card >= 30 min apart with other experiments between them; the two
halves of a pass may be separated by other blocks. Suggested aifoundry2 queue lines: `lat 11`, `lat 12`, ... ,
`lat 31`, `lat 32`, `lat 4`, `lat 5` (the same for aifoundry1-c0 and aifoundry1-c1); aifoundry3: `lat 1`, `lat 2`,
`lat 3`, `lat 4`, `lat 5`.

## What a pass does

Nine units in a per-pass shuffled order (`shuf --random-source=<(yes K)`, the same on every card), plus `c6` on
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
| div | (blocks 4, 5, 41-49 only) the divergence subset; on a card that idles below 600 MHz (aifoundry1-c0) also one 85 ms clock-witness TensorLoad (L2, 200,000 loads) before and after it | 4 (6) | 1-2 | 0.2 |

Card minutes per pass (card held by the block, heating included): **aifoundry2 ~20-30** (two halves of ~10-17;
the spread is the heater, which runs before every unit, nocbench invocation and sparsity group whenever the die
reads < 76 C), **aifoundry3 ~11**, **aifoundry1-c0 and aifoundry1-c1 ~17-27 each** (aifoundry2's units without
c6, two halves of ~8-15; their heating time is not measured yet, aifoundry2's is the estimate); divergence blocks
~1-2 (governor-free cards) / < 1 (a3); smoke < 1 min of device time (~1.5 min wall on a2, plus heating on a
governor-free card). The idle probe before each sampler start adds ~20 s per pass on every card. Three passes + two
divergence blocks: aifoundry2 ~65-95 min, aifoundry3 ~35 min (plan: 95 / 46), each aifoundry1 card ~55-85 min.

Every device process runs under `hold10` (timeout 10) and, where the host has it, `--budget 8` (memhier, nocbench
`run_lab` commands, sparsity, enercat; onchip and sgemm default to an 8 s budget). The block does not start while
a device process of ours runs on its card (lib.sh `ours_running`, per card with `V3_DEVICE`), checks for other
users before every launch and stops (block.json "fail", exit 3, so queue.sh sets the attempt aside and retries) if
anyone appears. On a governor-free card a unit whose sampler cannot start stops the block (its launches could not
be kept).
Telemetry, `.err` files and `stderr.log` are gzipped at the end of the block.

Output (`$DATA_ROOT/lat/p<pass>/`): `block.json`, `code.sha256`, `order.json` (also `gov_free`, `heat_c`, `device`),
`marks.jsonl` (unit begin/end, reheats, notes), `heat.jsonl` (heating curves, governor-free cards), `idle.jsonl` (the
idle probe before every sampler start: `unit`, `mhz`), and one directory per unit: the host printouts under the
`run_lab.sh` file names (`<name>.jsonl` / `.err.gz`), `sweep.jsonl` + `configs.txt` + `order.txt` (hl, rl; each
line carries `group`, `cfg`, `host`, `pass`), `sgemm-<i>.log` + `brackets.jsonl.gz` (sg), `runs.jsonl` +
`relay.jsonl` + `marks.jsonl` (c6), `launches.jsonl` (every process: name, rc, host start/end ms) and
`telemetry.jsonl.gz` (ettelem 10 Hz). The COOL reducer reads `c6/` (runs.jsonl labels as in run_hotline_power.sh;
relay.jsonl groups `rl2-dram` / `rl2-hop`); LAT's reducer does not use it.

## What is dropped, and why

aifoundry2's governor lifts the clock off 600 MHz below ~68 C, and memory-bound cycle counts depend on the
minion/NoC clock ratio, so on aifoundry2 (never on aifoundry3, which is pinned; aifoundry1's cards: the amended rule
of section "Four cards"):

- any launch whose telemetry samples within 0.2 s of it (or, if none falls there, the nearest sample on each side,
  each within 5 s) read `mhz.minion != 600`, or that has no sample at all, or whose cycles / wall time exceeds
  0.6 GHz (the host's `ghz` field, or `cycles_max / wall_s`) (plan: sampler rule of V3-LAT);
- any memhier chase whose `analyze.py` `point_ghz` is >= 0.65 (LAT-M2's rule; applied to every chase);
- any sgemm process unless the sampler bursts right before and right after it all read 600 MHz.

At the end of every unit on a governor-free card the block counts the unit's samples (sampler and sgemm brackets)
that read `mhz.minion != 600`; if there are any it writes an `off600` mark with the clocks seen to `marks.jsonl`, and
if any of them is not the card's idle point (a reading below 600 MHz of the block's idle probes, or
300 MHz on aifoundry1's cards) a note into
`block.json`, so the operator sees that a pass may need a re-run without running the reducer (which still decides
launch by launch).
A pass (or short block) counts for an item only if every launch that item uses in it is kept. A dropped pass is
re-run as pass 6-9 (divergence: 41-49) until each item has 3 kept passes (5 short blocks for LAT-S5).

## Four cards (amendment of 25 Sep 2026, fixed before any aifoundry1 data)

On 25 Sep the owner asked for every measurement to be re-run on every card after the day's machine fixes, and
aifoundry1 came back with two working cards. lib.sh names them `aifoundry1-c0` and `aifoundry1-c1` (`V3_DEVICE=0|1`
sets `ET_DEVICES`, so every process of the block, the sampler included, sees only that card as device 0) and gives
each its own `DATA_ROOT`. The amendment text for the plan's record is the LAT four-card amendment in `AMENDMENTS.md`.

| card | firmware | governor | idle point | heated to | drop rule | c6 | clock witnesses |
|---|---|---|---|---|---|---|---|
| aifoundry2 | 1.3.1 | free: TDP 65 W, threshold 65 C | 600 MHz | 76 C | registered | yes | no |
| aifoundry3 | 1.3.1 | pinned at 600 MHz by a boot service | 600 MHz | never | none (pinned) | no | no |
| aifoundry1-c0 | 1.4.1 | free: TDP 65 W, threshold 65 C | **300 MHz** (398 mV, 18.8 W board) | 76 C | amended | no | yes |
| aifoundry1-c1 | 1.2.0 | free: TDP 65 W, threshold 65 C | 600 MHz (499 mV, 32.9 W); 300 MHz counted as idle if seen | 76 C | amended | no | no |

**Per-card parameters** (`block.sh`; no test of a card name is left except this table's). Every card but aifoundry3
is governor free (lib.sh's `GOV_FREE`): heated to `HEAT_C` = 76 C before every unit, nocbench invocation and sparsity
group, its sampler required, its off-600 samples marked. aifoundry1's two cards take aifoundry2's values. `c6`
(V3-COOL's warm controls) stays on aifoundry2 only, because V3-COOL is registered for aifoundry2 only. New on every
card: an idle probe (lib.sh's `clock_mhz`, one 1 s management read) before every sampler start, written to
`idle.jsonl`, so the data say which idle state the card was in. New on aifoundry1-c0 (or any card whose idle probe in
a divergence block reads below 600 MHz): two clock witnesses in the divergence-only short blocks, because their four
2 ms kernels would otherwise have only idle samples around them. The block has no et_soc1 use-count check (it does
not call `run_lab.sh`'s `wait_free`, deviation 2); it relies on lib.sh's `others_present` (at the start and before
every launch) and `ours_running` (at the start, and in queue.sh's `wait_free`; per card when `V3_DEVICE` is set), so
the other card's queue on aifoundry1 does not block this one. With `V3_DEVICE` set, lib.sh's `drain_mgmt` is
replaced in the block by a logged no-op (last paragraph of this section).

**Where the physics may say otherwise: heating aifoundry1-c0.** What was measured (25 Sep ~16:40, two 2 s random
fp32 matmul launches 1 s apart, 10 Hz sampler; scratchpad `validate3/lessons.md`): c0 idled at 300 MHz / 398 mV / 18.6 W; during
the first launch its power did not rise and it moved to 600 MHz / 501-519 mV only at the launch's end (t = 4.3 s);
the second launch drew 49.4 W at 600 MHz; afterwards it idled at 600 MHz (26 W). The die temperature was not
recorded. So c0 leaves its low-power state under load and then stays at 600 MHz for a while, and the first launch
after a low-power idle may run slow or late. What the source says (the governor loop in the cards' May 2024 build and
353f20e; not measured on c0): an idle card is set to its flash boot frequency, and while a kernel runs the loop only
steps the clock down when the die reads above 65 C and up otherwise. On aifoundry2 the boot point, 600 MHz, is also
the lowest operating point, so a die above 65 C holds its bursts at 600: that is why it is heated. c0's boot point
is 300 MHz, so if firmware 1.4.1 follows that source, a c0 die heated above 65 C could step its bursts down below
600, and a cool one could climb above 600. Whether a heated c0 holds 600 MHz during kernels is therefore not known.
The amendment keeps aifoundry2's 76 C, the same procedure as on the other governor-free cards (it also means a
unit's first launch follows the heater's launches rather than a low-power idle, unless the die already reads 76 C).
The drop rule removes every burst that is not at 600, so c0's data stay clean, and the possible cost is card time
and an INSUFFICIENT c0. **Before queueing c0's passes, run `lat 1 --smoke` on c0**:
it heats to 76 C and prints the clock inside the kernel windows. If c0's bursts read below 600 there, its passes
would all be dropped; whether to spend its ~55-85 card minutes anyway is the operator's call. If the smoke's heating
does not reach 76 C (lib.sh's `heat_to` gives up after 150 launches, ~7.5 min; `heat.jsonl` and the log show it),
every unit, nocbench invocation and sparsity group of a pass would repeat that wait and a half-pass would run far
past 35 min: do not queue c0's passes then. Either way no rule changes. aifoundry1-c1 idles at 600 like aifoundry2, and the same reasoning makes heating right there.

**The amended drop rule** (`reduce.py`, aifoundry1's cards; aifoundry2 keeps the registered rule exactly, aifoundry3
is pinned). On c0 every sample between kernels reads 300 MHz (at least after a low-power idle), and under the
registered rule such samples within 0.2 s of a launch (or its nearest samples) would drop every launch. Checked: c0's
synthetic passes under the registered rule give INSUFFICIENT on all 16 items. aifoundry2 keeps the registered rule
because its idle point is 600 MHz: on its heated die an idle sample reads 600 and never drops a launch, and one that
reads off 600 means the governor has lifted the clock, which the registration drops (and changing its rule would
change the registered outcome).
1. A sample that reads the card's idle point (any reading below 600 MHz of the blocks' idle probes, plus 300 MHz,
   the low-power point queried on aifoundry1-c0 on 25 Sep, on both aifoundry1 cards: c1 has only been seen idling at
   600, but if it enters that state its idle samples must not drop its bursts) and lies outside every kernel window of its unit (every host record's
   `t_start_ms`-`t_end_ms`) is an *idle sample*. It is set aside: it neither drops nor supports a launch. A sample
   inside a kernel window is a burst sample whatever it reads, and a 300 MHz one drops the launches near it.
2. The registered rule applies to the remaining samples unchanged: those within 0.2 s of the launch, else the nearest
   one on each side within 5 s, must all read 600 MHz; cycles / wall time > 0.6 GHz drops.
3. A kernel of at least 5 ms whose cycles / wall time is below 0.45 GHz is dropped: it ran below 600 MHz (at 300 MHz
   it reads at most 0.30). The committed 600 MHz records have 1,997 such kernels (hot line 84, nocbench 26, sparsity
   386, onchip 45, enercat 1,456), and their lowest implied clock is 0.475 GHz (onchip); none is below 0.45.
   Memhier's clock estimate is clamped (`point_ghz`), so chases get no floor.
4. A launch whose only samples within reach are idle samples is kept on its own implied clock when its kernel is at
   least 5 ms (the floor above). Otherwise it takes its unit's verdict: kept if the unit has burst evidence and all of
   it (every non-idle sample, every implied clock of a kernel of at least 5 ms) reads 600 MHz / 0.45-0.6 GHz. A launch
   with no sample at all is dropped, as registered.
5. sgemm (no sampler may run while it holds the management node): kept if every bracket sample reads 600 MHz. If
   some read the idle point and none reads anything else, it is kept only when every other unit of the same block
   has the verdict "600 MHz"; the reading then says the clock during sgemm was not sampled. Such a process may also
   include c0's wake from its low-power state (the first launch after a low-power idle ran late on 25 Sep), which
   would lengthen its first launch: LAT-G's launch times on c0 are read with that caveat, and the reading counts
   these processes.
While aifoundry1-c1 idles at 600 and its probes read 600, its only idle point is the 300 MHz it has not been seen to
read, so on c1 the rule is in effect the registered one plus the floor of part 3. `cards[<card>]` in `verdicts.json` counts how every launch was judged (`launches_by_basis`) and gives
the idle probes, the idle points used, the clock readings inside kernel windows and the unit verdicts. A caveat the
data cannot remove: on c0 a short kernel kept on its unit's verdict (part 4) could have started at 300 MHz before the
governor stepped up. The count of such launches is in `launches_by_basis`, so the page can qualify c0's values.

**What the reducer adds.** `outcome` and `reading` stay the registered ones, computed only from aifoundry2 and
aifoundry3. They are byte-identical to the pre-amendment reducer's on the nine earlier test sets, and on four-card
data they ignore aifoundry1's cards. Each item gains `all_cards`, the same test over the four campaign cards plus any
other card directory under `--data` (or `--cards`):
- PASS if the item holds on every card, CARD-DIFFERENT if on some, FAIL if on none;
- INSUFFICIENT if a card lacks its repeats, including a campaign card with no data (the reading says "no data from ...");
- a registered either-card rule (LAT-S1 and sgemm mismatches, LAT-N3's drop, LAT-S3, LAT-S5, LAT-R3, LAT-R (i))
  applies to every card and decides FAIL, "decided by <card>".
Bands registered for each card apply unchanged. The parts whose band is a committed value of aifoundry2 or aifoundry3
are *reported* on the other cards, against both committed values, and not tested:
- LAT-H P1c, the unstopped host fractions "within ±2 pp of the committed per-card value";
- LAT-R (ii), each card's 5-offset line;
- LAT-R (v), the size / intensity / stage ratios "within ±5% of the committed per-card values".
LAT-H P1a's stopped configurations are the ones stopped on both committed cards (the same 42-row split on both).
`per_card` holds every card's values. LAT has no item on energy over idle; each card's idle clock is under `cards`.

**On aifoundry1, two queues share one host.** lib.sh lets each card run its own queue. LAT's timing is device-side
except LAT-G's "device held" time and the sgemm host's reference product, which share aifoundry1's CPU, and the two
boards share the chassis airflow. Prefer schedules in which c0's and c1's LAT blocks do not overlap. lib.sh's
`drain_mgmt` runs `/opt/et/bin/dev_mngt_service`, which is not `ET_DEVICES`-filtered and opens every card on
aifoundry1: a drain from one card's block while the other card's sampler runs is the two-openers case lib.sh
forbids. So with `V3_DEVICE` set the block replaces `drain_mgmt` by a logged no-op, which also covers lib.sh's
`heat_to`, `start_sampler` and `stop_sampler` (they call it by name), as `catfull` does. A management node that stays
stuck is then not drained: its unit's sampler fails to start and the block stops (governor-free card), and the queue
moves on.

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
4. **Heating**: `heat_to 76` before every unit, every nocbench invocation and every sparsity group on aifoundry2 and
   aifoundry1's cards, every governor-free card (the
   plan's order line says "before any group whose die reads < 70 C", its E4 detail "before every group"; heat_to
   returns at once when the die already reads >= 76). If the die cannot be read, the block drains the management
   queue once (not on aifoundry1, where the drain would open both cards: section "Four cards") and otherwise
   continues unheated (the clock rule then drops what ran off 600).
5. **nocbench on aifoundry3** also runs as the three aifoundry2 invocations (no heating there), so the group
   sequence is identical on every card; even passes (2, and re-runs 6, 8) reverse the 10 groups.
6. **The divergence subset** of passes 1-3 comes from the E4-extras unit (4 launches after a heat), not from the
   `diverge` group of `run_lab.sh`, so all 5 registered short blocks use one procedure; the `diverge` group feeds the
   per-pass parts of LAT-S5.
7. **ridge-X3 order**: the component detail says "right after E4's tload group"; the plan's pass order (shuffled
   units) wins. The 1- and 32-minion streams are shuffled per pass (seed K), as registered.
8. **c6 (V3-COOL warm controls)**: the plan asks for a copy of `run_hotline_power.sh` next to the original with
   `timeout 20` -> 10. The rules for these blocks forbid copies next to originals, so its five labels are inline in
   `block.sh`, under `hold10`, with lib.sh's sampler (not the runner's own start/kill) and heating to 76 C (plan:
   >= 70 C).
9. **Pass halves** (K1/K2) keep blocks under the 35-min limit on aifoundry2 (and aifoundry1's cards); the plan
   counted a2 passes as 32 min.
10. **Hot-line labels**: extras are labelled `req`, `alone`, `pace` (knee), `win`, `poll`, `warm` as in the plan;
    every line also carries `cfg`, its index in `configs.txt`, because some configurations share all printed fields
    (e.g. `local`, `shires` and `pace` rows at 32 x 32) and the warm-up is not printed.
11. **The scpself bus-error probe** (optional in the plan) is off unless `LAT_SCPSELF=1`; with it, a failed health
    launch afterwards stops the block. Claim hotline-relay-l2-52 is in LAT-H's claim list, but no P-part tests it:
    with the probe on, the reducer reports per pass what it did (`scpself_probe` under LAT-H: exit code, a printed
    line or not, the health launch) for the page's qualifier; it does not enter LAT-H's outcome.
12. **Other users**: the block aborts when someone appears (the plan's run_lab.sh waited up to 120 s per command).
13. **sgemm build on aifoundry2**: already built (build/sgemm/host/sgemm_host, 25 Sep 09:07), no build step here.
14. **Build on aifoundry1** (not done here): the memhier, nocbench, sparsity, enercat, onchip and sgemm hosts under
    `~/nekko/build/<name>/host/` (lib.sh's paths for every host but aifoundry2) and `build/ettelem/ettelem`, with
    `--clean-first` (rsync keeps mtimes); check `/usr/bin/time` exists (without it LAT-G's RSS part stays
    INSUFFICIENT on that card) and that `enercat_host --help` lists `--minions`.

## Reducing

```
python3 tools/claims-v3/lat/reduce.py --data <dir with one directory per card> --out verdicts.json [--cards a,b,c]
```

`<dir>/<card>` is laid out like `DATA_ROOT` (the collected `build/claims-v3/<card>`; cards aifoundry2, aifoundry3,
aifoundry1-c0, aifoundry1-c1). Needs numpy; imports `workloads/nocbench/analyze.py` (MARTY map, `search_layout`),
`workloads/memhier/analyze.py` (`point_ghz`) and `workloads/onchip/analyze_onchip.py` (ring geometry) from the tree,
and reads `ref_committed.json`. About 3-4 min with two cards' full data and 7.5 min with four (LAT-N2's layout
search, 12 restarts per pass; 150 MB); `--no-search` skips it (LAT-N2 is then INSUFFICIENT). `outcome` is the
registered outcome (aifoundry2 and aifoundry3); `all_cards` is the four-card outcome of section "Four cards", over
the four campaign cards and every other card directory present, or the cards given by `--cards`. It runs on partial data: blocks without an "ok" block.json and units without an "end" mark are
ignored, and every item lacking its kept repeats on a card is INSUFFICIENT. Each item in `verdicts.json` has
`item`, `claims`, `prediction`, `per_card` (every card's values, `n` kept repeats, per-pass details), `test`,
`outcome` (PASS / FAIL / CARD-DIFFERENT / INSUFFICIENT), `reading` and `all_cards` (`cards`, `outcome`, `holds` per
card, `reading`); `cards[<card>]` has the blocks read and skipped, the drop rule, the idle probes and idle points, and
how each launch was judged. CARD-DIFFERENT is used only where the registration
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

Four cards (scratchpad `validate3/fourcards/lat/`, `make_fourcards.py` on top of `synth()`; aifoundry1's cards get
their own draws of aifoundry2's layout; aifoundry1-c0's samples outside kernel windows, idle probes and sgemm
brackets read 300 MHz, its sampler phase is offset 37 ms so short kernels rarely have a sample inside, and its
divergence blocks carry the two witnesses). The pre-amendment and amended reducers give identical registered
outcomes, readings and aifoundry2/aifoundry3 values on the nine earlier sets, on the four-card sets, and on
aifoundry2's real V3-LAT data of 25 Sep (passes 1-3 as halves, block 4; aifoundry3's LAT data were not at hand). The
same aifoundry2 data read as if from aifoundry1-c0 or -c1 give aifoundry2's per-card values under the amended rule
(every launch kept on samples or 600 MHz brackets; none of its 969 kernels of >= 5 ms reads below 0.476 GHz).
- `pass4`: all_cards = the registered outcome on every item (LAT-N2 CARD-DIFFERENT with the search, from the
  aifoundry3 restart sensitivity above).
- `c0diff` (c0's L1 at 5.30; one c0 int8 deviation; c0's sgemm n=1024 at 18.5 ms): all_cards LAT-M1 CARD-DIFFERENT,
  LAT-S1 FAIL "decided by a1c0", LAT-G CARD-DIFFERENT; registered unchanged.
- `missing` (no aifoundry1-c1 directory): all_cards INSUFFICIENT on every item, "no data from a1c1"; with
  `--cards aifoundry1-c0,aifoundry2,aifoundry3` it equals pass4's.
- `c0slow` (c0's bursts at 300 MHz too): every c0 launch dropped (on samples, on the floor, on the unit verdict,
  sgemm on its block), c0 INSUFFICIENT everywhere, never a FAIL.
- `c1lift` (one 800 MHz sample inside a c1 hot-line launch): LAT-H INSUFFICIENT on c1 (2 kept passes).
- `nowit` (c0's short blocks without witnesses): LAT-S5 INSUFFICIENT on c0.
- `c0asreg` (c0's data under the registered rule): INSUFFICIENT on all 16 items.
- `c1lowidle` (review, `validate3/fourcards/lat/review/`): a third of c1's samples outside kernel windows read
  300 MHz while its idle probes read 600. With 300 MHz an idle point on c0 only, 659 c1 launches were dropped on
  those idle samples and c1 was INSUFFICIENT on 14 items. With 300 MHz an idle point on both aifoundry1 cards, c1
  keeps every launch and all_cards equals pass4's.
- Dry runs of every block kind (1-3, 11-32, 4, 5, 6, 61, 62, 41, smoke) on all four card ids (hostname shim,
  `V3_DEVICE=0|1`): all exit 0. aifoundry2's and aifoundry3's device calls are identical to the pre-amendment
  block's, except that aifoundry2's smoke now heats to 76 C.
