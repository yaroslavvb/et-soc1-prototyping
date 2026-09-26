# V3-RL: rings, levels and relay energy with spin brackets and controlled scratchpad contents

PLAN3 section 2, "V3-RL" (docs/reports/data/2026-09-25-claims-v3/PLAN3.md). It merges energy-manual EXP-EM3,
memhier-onchip-X3 and ridge-X4 (reduction only), and tests 30 claims through 9 pre-registered items
(RL-a, b, c, d, f, g, h, X3, X4). There are 6 passes per card, one block per pass, at least 30 minutes apart.
It runs on four cards: aifoundry2, aifoundry3, and aifoundry1's two cards (card ids `aifoundry1-c0` and
`aifoundry1-c1`, selected with `V3_DEVICE=0|1`; see "Four cards" below). The registered outcomes are still computed
from aifoundry2 and aifoundry3 alone; the reducer adds an `all_cards` outcome over the four.

```
bash tools/claims-v3/rl/block.sh <pass>              # one pass on the local card (queue line: "rl <pass>")
V3_DEVICE=1 bash tools/claims-v3/rl/block.sh <pass>  # on aifoundry1: card 1 (V3_DEVICE=0: card 0; required there)
bash tools/claims-v3/rl/block.sh <pass> --smoke      # every component once, about 20 s of device time
V3_DRY=1 bash tools/claims-v3/rl/block.sh <pass>     # print every device call, touch nothing
python3 tools/claims-v3/rl/reduce.py --data <dir with one directory per card> --out verdicts.json \
    --flop abla_flop.json [--low-edge catfull_low_edge.json] [--cards aifoundry1-c0,aifoundry1-c1,aifoundry2,aifoundry3]
python3 tools/claims-v3/rl/quality.py <pass dir> --scope all|busy|none   # a pass's windows and 600 MHz rule (files only)
```

## What one pass does

A pass runs on one card. Everything is relative to the tree root (`lib.sh` cds there), so the same script runs in
this repository on aifoundry2 and in `~/nekko` on aifoundry3 and aifoundry1. Every device process goes through
`hold10` (`timeout 10`) and gets `--budget 8`.

0. **Card state** (`card_state start`): one `ettelem config` (read-only: TDP, temperature threshold, power state and
   its name, minion clock and voltage) into `state.jsonl`, then 2 s of pause. It records which idle state the card
   rests in (aifoundry1's card 0 idles in "low_power" at 300 MHz). A failed read records `null`; the pass goes on.
1. **Heat** (governor-free cards, lib.sh `GOV_FREE`: aifoundry2 and aifoundry1's two cards; `heat_to 76`; it does
   nothing on the pinned aifoundry3). The sampler is off while this runs, because `heat_to` opens the management
   node.
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
   medium. Then `card_state end`: the idle state after 16 s of idle.
7. **Quality check.** The block then:
   - runs `quality.py` on the pass (files only) and writes `quality-windows.json`: every telemetry sample falls in
     one window (busy, launch gap, idle bracket, other), each window has its clock histogram and median minion
     voltage, and `idle_clock_mhz` is the idle brackets' most common clock;
   - applies the card's pass-level 600 MHz rule (`OFF600`, see "Four cards"): on aifoundry2 any sample off
     600 MHz fails the pass (registered); on aifoundry1's cards any **busy** sample off 600 MHz fails it (the idle
     brackets and launch gaps are never counted, so card 0's 300 MHz idle cannot fail a pass; if `quality.py`
     cannot say, the pass fails); on aifoundry3, which is pinned, the count is recorded and the reducer's burst
     rule applies;
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
- `pass.json`: the order and the contents of this pass, and the card's parameters (`device`, `gov_free`, `heat_c`,
  `off600_scope`)
- `state.jsonl`: `ettelem config` at the start and the end of the pass (the idle state)
- `heat-{A,B,relay}.jsonl`
- `A/`, `B/`, `relay/`: each holds `telemetry.jsonl.gz`, `runs.jsonl`, `marks.jsonl` and `launches.jsonl` (the
  exit code of every launch). `B/` also holds `prefill.jsonl`.
- `quality.json` (counts, busy counts, idle clock, rule), `quality-windows.json` (quality.py's full output),
  `block.json`

Raw data is under 0.5 MB per pass (gzipped telemetry).

**Card minutes per pass:**

| part | minutes |
|---|---|
| half A | 3.6 (13 bursts x ~15.7 s, plus 14 s of lead and tail) |
| half B | 3.3 (10 bursts, 2 prefills) |
| relay | 1.2 |
| card state | 0.1 (two `ettelem config` reads with 2 s pauses) |

That is about 8 minutes per pass on aifoundry3, of which about 35% is device time and the rest is sampler idle;
its two passes of 25 Sep took 8.0 and 8.0 minutes (`block.json` t0 to t1). A governor-free card adds three heats.
The five aifoundry2 passes of 25 Sep took 9.4, 8.2, 8.0, 9.3 and 9.1 minutes. aifoundry1's two cards are
governor-free and heat like aifoundry2; their heat times are not known yet. Their dies idled at 57-65 C on 25 Sep,
and aifoundry3 needed about 150 2 s heater launches to go from 55 C to 88 C, so the first heat of a pass may take
several minutes: count 9 to 16 minutes per pass. Over 6 passes that is about 50 minutes on aifoundry3, 55 minutes on
aifoundry2 and 55 to 95 minutes on each of aifoundry1's cards. A normal pass stays well under 35 minutes; the bound
is `heat_to`'s 150 launches (about 8 to 10 minutes per heat), after which the pass fails rather than run on.

**Smoke** (`--smoke`, exp `rl-smoke`) runs every component once. Bursts are 0.5 s with 1 s gaps:
- nocbench spin, the `pair` ring and the `xshire1-c4` ring;
- memhier spin, l1, l2, l3, dram, a zeros prefill, scp-local and scp-remote;
- one relay launch per medium;
- one `card_state smoke` (checks that `ettelem config` answers on this card; recorded, not a smoke criterion);
- on a governor-free card (aifoundry2, aifoundry1-c0, aifoundry1-c1), one 1 s heater launch and one `die_c` after
  the sampler stops.

Run the smoke on each of aifoundry1's cards before their queues start (`V3_DEVICE=0` and `V3_DEVICE=1`): it checks
the aifoundry1 builds of nocbench, memhier, enercat, onchip and the heater, and the sampler through `ET_DEVICES`.

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
- **aifoundry1's cards** (amendment, before any of their data): the same two rules on **busy** samples only. A
  pass with any busy sample off 600 MHz is dropped and re-run; a burst with more than 2% of its busy samples off
  600 MHz is dropped. The idle brackets and the relay's launch gaps never drop anything; their clock is recorded.
  See "Four cards".
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
9. **The heater.** On a governor-free card the heater is `lib.sh`'s `HEATER`: sparsity_t2 on aifoundry2,
   build/sparsity on aifoundry1. aifoundry3 needs no heater: `heat_to` returns at once there, and the smoke skips
   the heater launch. (Under `V3_DRY=1` the stubbed `heat_to` prints its line on every card, aifoundry3 included.)
10. **Card state.** `ettelem config` at the start and the end of each pass (not in the plan): a read-only record of
   the card's idle state, needed since aifoundry1's card 0 idles at 300 MHz.

## Four cards (25 Sep: aifoundry1's two cards join)

The owner asked for every measurement on every card after the 25 Sep machine fixes, so the campaign runs the full
6 passes on four cards. `lib.sh` gives each card its id, data directory and `GOV_FREE`; the block takes the rest
from this table (`HEAT_C`, `OFF600` at the top of `block.sh`). The heater, the heats and the smoke's heater launch
follow `GOV_FREE`; the one card-name test left is the registered pass rule of aifoundry2 (`OFF600=all`).

| card | firmware | governor | heat before each half and the relay | pass-level 600 MHz rule | burst rule counts | heater |
|---|---|---|---|---|---|---|
| aifoundry2 | 1.3.1 | free (TDP 65 W) | 76 C | any sample (registered) | burst + idle brackets (registered) | sparsity_t2 |
| aifoundry3 | 1.3.1 | pinned at 600 MHz (boot service) | none | none, recorded (registered) | burst + idle brackets (registered) | none |
| aifoundry1-c0 | 1.4.1 | free (TDP 65 W); idles "low_power" 300 MHz / 398 mV | 76 C | busy samples (amendment) | busy samples (amendment) | sparsity |
| aifoundry1-c1 | 1.2.0 | free (TDP 65 W); idles 600 MHz / 499 mV | 76 C | busy samples (amendment) | busy samples (amendment) | sparsity |

**Why these values** (decided before any aifoundry1 data):
- **Heat target, 76 C.** aifoundry1's cards take aifoundry2's value. `ettelem config` gave both the same governor
  inputs as aifoundry2 (TDP 65 W, software temperature threshold 65 C). On aifoundry2 (firmware 1.3.1) the
  governor lifts the clock off 600 MHz below about 68 C and holds the lowest point above 65 C. The aifoundry1
  clock test of 25 Sep (two 2 s matmul launches per card, lessons.md) saw no boost on card 1 (firmware 1.2.0) at
  57-62 C, and card 0 (1.4.1) went from 300 MHz up to 600 MHz and no higher. So the clock reason to heat is shown for aifoundry2 only. The
  heat is kept on both of aifoundry1's cards anyway: it is a precaution against a boost that two launches cannot
  rule out, it puts every governor-free card at the same die temperature as aifoundry2 (the leakage correction
  and the card comparisons assume similar dies), and on card 0 the heater's launches wake it from its low-power
  state before the half starts. Not known: whether firmware 1.4.1 or 1.2.0 can step a hot die *below*
  600 MHz (1.3.1's lowest point is 600 MHz; card 0 has a 300 MHz state). If it does, busy samples fall off
  600 MHz, the pass fails by rule, and the card's items stay INSUFFICIENT: the rule is not changed after the data.
  The heater is `lib.sh`'s `HEATER` (build/sparsity/host/sparsity_host on aifoundry1, as on aifoundry3).
- **The 600 MHz rules on busy samples only.** The registered rules count idle samples too: aifoundry2's pass rule
  counts every sample, and the burst rule (`clock_moved_frac` in `reduce_dir`) counts the burst and its idle
  brackets. Card 0 idles at 300 MHz after a long idle, so those rules could drop every burst and every pass there.
  On aifoundry1's cards the rules count busy samples only, the samples inside a burst's window as `reduce_dir`
  takes it (`[first run start + 0.5 s, last run end]`). One refinement is decided now as well. The relay runs
  separate processes about 190 ms apart on aifoundry2 and 230 ms apart on aifoundry3 (the 25 Sep passes; ring and
  level kernels follow each other within 6 ms). The samples from one relay launch's end to 50 ms after the next
  one's start are "launch gaps" and are not busy: between two processes no kernel runs. The 50 ms covers only
  the launch latency (onchip_host stamps `t_start_ms` just before the launch). A kernel that still runs below
  600 MHz after it is a busy sample off 600 MHz. On the 25 Sep aifoundry2 relay, a 300 ms margin would have put
  57 in-kernel samples out of 174 (a third of the relay's kernel time) outside the check; with 50 ms none are.
  Card 1 idles at 600 MHz, but it gets the same rule: both of aifoundry1's cards are handled alike.
  aifoundry2 is also governor-free, but it keeps its registered "any sample" rule (PLAN3's common rules). Its
  heated die idles at 600 MHz (0 of 23,575 samples off 600 MHz in its five 25 Sep passes), and changing its rule
  would change its registered outcome. aifoundry3 keeps its registered burst rule. So their registered outcomes
  cannot move.
- **Card 0 waking from low power.** In the clock test, card 0's first launch after a low-power idle showed no
  power rise, and the card reached 600 MHz only at the end of it (about 4 s). After that the card idled at 600 MHz
  (26 W) and did not drop back within the test. The heats wake it before each half. If it still falls back to
  its low-power state in a 10 s idle gap (or a relay launch gap), its next burst starts below 600 MHz. The busy
  rule then fails the pass, which is re-run; if that happens every time, card 0 stays INSUFFICIENT. That outcome
  is decided now and is not changed after the data. The smoke and the first pass show which case holds: read
  `quality-windows.json` (the busy and bracket clock histograms) and `state.jsonl`.
- **Leakage correction.** `reduce_dir`'s leakage slope (23.3 W at 80 C, T_L 36 C) is the registered constant for
  both cards; it applies to aifoundry1's cards unchanged (no measurement of their own).
- **The idle state is energy's baseline.** Every V3-RL value is energy over idle. On a card whose idle brackets are
  at 300 MHz / 398 mV, every over-idle watt includes the step from that state up to 600 MHz. Its values are not
  comparable with a card idling at 600 MHz. The block records the idle clock (`state.jsonl`,
  `quality-windows.json`). The reducer puts each card's idle clock on every item (`idle_clock_mhz`) and adds
  `idle_note` when a card's brackets are not at 600 MHz. A difference of two bursts on the same card (spin - ring,
  the c4 rows, L2 - scratchpad, random - zeros) largely cancels the step. Nothing is dropped for it, and no
  correction is invented: the page says so. Even at 600 MHz the three firmware releases idle differently: 26 W
  (1.4.1), 33-35 W (1.2.0) and 32 W (1.3.1, aifoundry2 at 74 C) in the 25 Sep clock test. So an absolute
  over-idle value (W or pJ/B) that differs on aifoundry1's cards may come from what the firmware gates at idle,
  not from the workload. The page must not read such a CARD-DIFFERENT as a silicon difference; the same-card
  differences are the comparable ones.
- **No module use-count check** in this block (it relies on `ours_running` and `others_present`, per card in
  `lib.sh`).

**The all_cards outcome.** Every item keeps its registered `outcome`, computed from aifoundry2 and aifoundry3
exactly as before. The reducer before and after the change gives identical registered items on the real 25 Sep
passes (aifoundry2 p1-p5, aifoundry3 p1-p2), with aifoundry1 card directories added beside them, and on all earlier
test sets. Each item also gets `all_cards`, which covers the cards in `--cards` (by default the four, plus
any other card under `--data`). It has `outcome`, `reading`, the cards tested and reported, and `lacking` (a card
with fewer than 3 kept repeats). When a card is lacking, the outcome is INSUFFICIENT, and `over_sufficient` gives
the verdict over the other cards for information. `per_card` holds every card's values.

| item | all_cards test | aifoundry1's cards |
|---|---|---|
| RL-a slope; RL-d ratio and relay DRAM; RL-g L1 and own scratchpad | the registered Welch comparison over every pair of cards, each pair at 1 - 0.01/pairs (Bonferroni; with two cards this is the registered 99%): a pair differs -> CARD-DIFFERENT (per-card values), else PASS (pooled) | compared; the per-card bands (registered for aifoundry2 and aifoundry3 only) are reported, not tested |
| RL-g L2 - scratchpad | a pair differs -> CARD-DIFFERENT; else each card's interval against 0: every card -> PASS, some -> CARD-DIFFERENT, none -> FAIL | as the other cards; bands reported only |
| RL-b step | decided on aifoundry2, as registered | reported (interval in `info_step_ci99`) |
| RL-c small messages | decided on aifoundry3, as registered (its predicted values are aifoundry3's) | reported (sign on each card in `info_sign_each_card`) |
| RL-f relay scratchpad vs low edge | each card against its own catalogue's low edge: below on every card -> PASS, some -> CARD-DIFFERENT, none -> FAIL | tested against `--low-edge` (below); INSUFFICIENT without it |
| RL-h part 1 (bands 2.0 / 4.2) | registered for each card: in both bands on every card -> PASS, some -> CARD-DIFFERENT, none -> FAIL | tested |
| RL-h part 2 (equal contents) | every pair within each contents group (Bonferroni): a pair differs -> CARD-DIFFERENT; else every pairwise difference within +-0.1 -> PASS; else FAIL | compared |
| RL-X3 (a), (d), (e) | registered for both cards: holds on every card -> PASS, some -> CARD-DIFFERENT, none -> FAIL; the (a) and (d) bands apply to every card | tested |
| RL-X4 balance vs ridge | the registered rule over every card: all on the predicted side -> PASS, any overlap -> FAIL (no verdict), all on the other side -> FAIL, opposite sides -> CARD-DIFFERENT | tested with V3-RL passes only (no 23 Sep passes); the FLOP side must be in `--flop` under the card's id |

**`--low-edge`** is RL-f's low edge for the cards outside the 23 Sep catalogue:
`{"aifoundry1-c0": [...], "aifoundry1-c1": [...]}`. Each value is one catalogue pass on that card (V3-CATFULL):
0.5 x (l1fill/stride32/zeros + tstore/scp/zeros) pJ/B, as `rings_relay_extra.py` computed it for 23 Sep. At least
two passes are needed. aifoundry2 and aifoundry3 always use the 23 Sep catalogue, as registered.

## Reduction (reduce.py)

`--data` points at a directory holding one directory per card (`aifoundry2/`, `aifoundry3/`, `aifoundry1-c0/`,
`aifoundry1-c1/`), each laid out like `DATA_ROOT`; every card directory with an `rl/` inside is read. Run the
reducer inside a repository tree, because it reads these committed files (and `quality.py` beside it):
- the 23 Sep rl-passes (the byte side of RL-X4);
- the 23 Sep catalogue (the bracket low edge of RL-f);
- the ridge-points page (the RL-X4 ridges).

It works on partial data: any cards, or fewer passes. An item without 3 kept passes per card is INSUFFICIENT.

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

**Four-card tests** (in `validate3/fourcards/rl/`, 25 Sep):
- `regress.py`: the reducer before and after the four-card change, compared on the registered part of every item
  (per_card restricted to aifoundry2 and aifoundry3), the pass logs and the dropped bursts. It is identical on the
  five real aifoundry2 passes of 25 Sep, on every older test set below (12 runs), and on the four-card sets.
  The review (`review/`) repeated it on the real passes collected so far (`validate3/data/`: aifoundry2 p1-p2,
  aifoundry3 p1-p2), on all real passes (aifoundry2 p1-p5 with aifoundry3 p1-p2, and with aifoundry3 made up to 6
  passes from relabelled copies so the registered path runs past INSUFFICIENT), and on the same with copies placed
  as aifoundry1-c0/-c1: identical each time (outcome, reading, prediction_held, kept passes, dropped bursts).
- `gen_synth4.py`: synthetic passes on four cards, with relay launches 0.19 s apart and card 0 idling at 300 MHz /
  398 mV. Four sets:
  - `allpass`: every card the same; every all_cards outcome PASS except xshire16, which aifoundry2's starved
    sampler leaves INSUFFICIENT; card 0 keeps all 6 passes;
  - `c0differs`: card 0's idle 7 W lower. The absolute items give CARD-DIFFERENT (slope, relay, L1, spin in band,
    RL-h bands) and the differences stay PASS (spin - ring, c4, L2 - scratchpad, inside - across);
  - `missing`: aifoundry1-c1 absent, so every all_cards is INSUFFICIENT with `over_sufficient` given (except RL-b
    and RL-c, decided on their named cards), or it covers three cards with `--cards`;
  - `drops`: a busy 800 MHz sample on card 0 drops its pass; a bracket 800 MHz sample keeps the pass on card 0,
    card 1 and aifoundry3 and drops it on aifoundry2 (registered).

  Those sets put 0.1 s of 300 MHz inside every relay kernel of card 0, which the first launch-gap rule (300 ms into
  the next kernel) excused. With the 50 ms rule such samples count, so the review regenerated the sets with
  `review/gen_synth4b.py` (`--launch-idle S`: seconds of idle clock inside each relay kernel, default 0) in
  `review/syn/`: `allpass`, `c0differs` (`--c0-step 7`), `missing` and `drops` give the results above (card 0
  keeps its passes: its 300 MHz gaps and brackets drop nothing), and `wake` (`--launch-idle 0.1`: card 0's kernels
  start at 300 MHz) drops every card 0 pass by the busy rule (21 of 1,262 busy samples off 600 MHz each), leaving
  card 0 INSUFFICIENT and the registered outcomes unchanged. `review/qsnip/` runs the block's own `qv` and
  decision lines (copied verbatim) on these passes: all / busy / none give the expected pass or fail.
- `qtest/`: the block's quality snippet (extracted, no device calls) on those passes, and with `quality.py`
  missing: aifoundry1 passes then fail, aifoundry2 and aifoundry3 are unaffected.
- `dry/`: `V3_DRY=1` blocks (passes 11 and 12, and the smoke) on all four card ids (hostname shim, `V3_DEVICE=0|1`),
  and aifoundry1 without `V3_DEVICE` (exit 2). Repeated in `review/dry/` (passes 81, 82 and smoke 83): every pass
  has 30 device calls under `hold10` (28 with `--budget 8`, 2 `ettelem config`), 3 heats and 3 samplers; the smoke
  has the heater on the three governor-free cards only.

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
