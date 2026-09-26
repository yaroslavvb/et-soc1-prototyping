# V3-MEM: memory anatomy, the cycle-counter window and the wake-up probe, on every card

This experiment is PLAN3.md section 2, "V3-MEM" (it merges anat-X1, anat-X2, E-hub-2 and EXP-dvfs-1; new code N1).
It tests 80 claims through 15 pre-registered items: MEM-P1 to P10, MEM-X2, MEM-R1 to R3 and MEM-W. It uses
`workloads/memprobe` op programs and needs no new device code.

**Four cards (amendment of 25 Sep, written before any aifoundry1 data; `validate3/fourcards/amendment-mem.md`).** The
campaign that re-runs every measurement runs this block on four cards: aifoundry2, aifoundry3, aifoundry1-c0 and
aifoundry1-c1 (on aifoundry1, `V3_DEVICE=0` or `1` selects the card through `ET_DEVICES`; lib.sh names it and gives it
its own `DATA_ROOT`). Nothing in the block tests a host name any more:

| what | aifoundry2 | aifoundry3 | aifoundry1-c0, aifoundry1-c1 |
|---|---|---|---|
| governor (lib.sh `GOV_FREE`) | free: heat to 76 C first | pinned at 600 MHz: no heater | free (TDP 65 W, threshold 65 C, as aifoundry2): heat to 76 C first |
| heater launches per heat | 0 on a die already at 76 C | none | at least 1, even on a die already at 76 C (card 0's low-power idle, below) |
| clock rule (`memv3.py clock_rule`) | `registered`: any X1 sample, and the probe's pre/post samples, off 600 MHz drop | `pinned`: recorded, never a drop | `busy`: only clock readings taken inside a memprobe kernel drop an X1 part; the probe is judged on its own clock |
| idle state record | the sampler's between-kernel readings | the same | the same, plus `ettelem config` at the start and end of a pass (`idle_state.jsonl`) |
| `et_soc1` use-count check | yes | yes | skipped (`V3_DEVICE` set: the module count covers both cards, and the other card's queue holds its own card); `ours_running` (per card) and `others_present` (users, their device processes, a CI job) decide |

aifoundry1's cards take aifoundry2's values (heat target 76 C before the X1 part and before the probe, the same
heater, the same 150-launch limit): the governor's thresholds are the same (TDP 65 W, 65 C). Physics that could make
them differ, and is not tuned around: card 0 (firmware 1.4.1) idles in a `low_power` state at 300 MHz / 398 mV, so if
its thermal step-down floor were below 600 MHz a hot die would run the kernels below 600 MHz; the busy rule then drops
those passes, and the items stay INSUFFICIENT on that card rather than being re-tuned after seeing data. The busy rule
exists because card 0's between-kernel readings are 300 MHz while a kernel may run at 600: under aifoundry2's rule every
card-0 pass would be dropped for its idle state. The one place the physics changes a parameter: card 0 left its 300 MHz
idle only at the end of its first 2 s heater launch in the 25 Sep clock test, and memprobe kernels last 2-85 ms, so on
aifoundry1's cards each heat (before the X1 part and before the probe) makes at least one heater launch even when the
die already reads 76 C; without it a pass started on a die left hot by the previous block could run its kernels at
300 MHz and be dropped. Card 1 idles at 600 MHz and gets the same launch (harmless: 2 s, under `hold10`).
aifoundry2 keeps its registered rule although its governor is free too: that rule is stricter (its idle brackets can
drop a pass), and on its 25 Sep passes every reading, busy or idle, was 600 MHz.

| file | what it is |
|---|---|
| `block.sh` | one pass on the local card: `bash tools/claims-v3/mem/block.sh <pass> [--smoke]` |
| `memv3.py` | file checks and drop rules (used by the block and the reducer); the counter-window and wake-up analyses |
| `reduce.py` | the decisions: `python3 tools/claims-v3/mem/reduce.py --data DIR --out verdicts.json` |
| `prereg/` | byte-identical copies of the pre-registered scratch reducers the plan names (hashes below) |

## What a pass does (`block.sh k`, exp name `mem`)

1. The block does not start, and exits 3, while another user is logged in, another user's device process runs, one of
   our own device processes still runs, or the `et_soc1` module's use count is not 0 (plan 2.13; skipped when
   `V3_DEVICE` is set, see above). It exits 2 if lib.sh's `GOV_FREE` and `memv3.py rule` disagree about the card. It
   exits 2 before touching the card if `workloads/memprobe/gen_ops.py` differs from the pre-registered copy
   `prereg/mp/gen_ops.py` (on aifoundry3 and aifoundry1 the tree is a synced copy; an older generator would write
   other programs under the same names).
2. On a busy-rule card (aifoundry1's two), `ettelem config` records the idle state (power state, minion clock and
   voltage) in `idle_state.jsonl`, with no kernel and no sampler running. Then `memprobe_host --info` reads the arena
   base. The block fails if the base is not 1 GB aligned (bits needs this, and so does P10).
3. The op lists are generated off-card with the plan's commands and seeds: `s = 100+k` for decomp, msmap, bits,
   refresh_jit and pagetimeout; seed 1 for ladder; `200+k` for the requester decomp; `20+k` for the wake-up probe.
   `t_rawodd` is the plan's `python3 -c` command, verbatim.
4. On a governor-free card (every card but aifoundry3), heat to 76 C (`heat76` in block.sh: lib.sh's `heat_to 76`
   loop, the same heater command, plus an `others_present` check before each heater launch). On a busy-rule card
   (aifoundry1's two) at least one heater launch is made even on a die already at 76 C. The block fails if the heater
   gives up (150 launches, or 4 failed die reads in a row: it never heats blind), and exits 3 (the queue retries) if
   another user arrives while it heats.
5. The 10 Hz sampler starts (`start_sampler`, with retry and drain). On a governor-free card the block fails if it
   does not start, because a pass without a clock reading is dropped there (registered and busy rules alike).
6. The 11 programs run in `shuf` order, each as its own process. The order is recorded in `order.txt`. The programs
   are t_raw, t_glitch, t_rawodd, ladder, decomp, l3map, msmap, bits, refresh, refresh_jit and pagetimeout.
7. ladder and then decomp run from requesters 7, 24 and 31 (`--hart 64*S`), into `req<S>/`.
8. The sampler stops (SIGTERM).
9. The wake-up probe runs in passes 1 to 3, and in any later pass while this card has fewer than 3 kept probes. On a
   governor-free card the die is first topped up to 76 C (`heat76`). Then come a 1 s sample (5 Hz) to
   `wake/pre.jsonl`, the probe (`--reps 20`, delays 0 to 16M cycles), and a 1 s sample to `wake/post.jsonl`. Under the
   registered rule (aifoundry2) a probe whose pre sample cannot start is skipped (it would be dropped); on the other
   cards the probe runs anyway. If another user has arrived by then (checked before the heat, between heater launches
   and before the probe), only the probe is skipped (`wake/skipped`, noted in block.json): the X1 part already ran and
   is kept, and a later pass re-runs the probe. On a busy-rule card `ettelem config` then records the idle state
   again (after the probe, or after the X1 part in a pass without one).
10. `drop.json` is written, the `.ops` files are deleted (they can be regenerated from the seeds), and the gen_ops
    label `.json` files and the telemetry are gzipped.

Every memprobe process runs under `hold10` (timeout 10) with `--budget 8`. Nothing else opens the management node
while the sampler runs, because memprobe opens only the ops node. Before each program, the block checks
`others_present` again. If someone has arrived, it stops the sampler, marks the block failed and exits 3; the queue
then retries the pass.

Passes 6 and later are conditional re-runs. A pass k > 5 does nothing (exit 0, no block.json, the card is not
opened) when the card already has 5 kept X1 passes and 3 kept wake-up probes, or when it has 5 kept X1 passes and the
missing probes will come from passes 1-3 that were never tried. It runs only the wake-up probe when the card has 5
kept X1 passes but fewer than 3 kept probes. A pass 1-3 that failed, or that the queue gave up on (only
`p<k>.attempt-*` left), is not counted as a future probe, so pass 4 or 5 (or 6-8) takes over its probe. Put `mem 6`,
`mem 7` and `mem 8` at the end of each card's schedule.

**Status.** A block is `fail` only if the arena base, the heater (governor-free cards), the sampler start
(governor-free cards) or one of the 11 core programs fails. A requester or probe failure is recorded in the note, and
in `drop.json` and `runs.jsonl`. A drop is recorded in the note (`x1 DROP (...)`, `probe DROP (...)`) while the block
stays `ok`. The reducer re-derives every drop from the files.

**Schedule.** Run 5 passes per card with at least 10 minutes between passes on one card (plan 2.13), interleaved with
other experiments, then `mem 6` to `mem 8`.

**Card minutes per pass.** aifoundry2 is measured (25 Sep, passes 1-3 of the first campaign, `block.json`); the
others are estimates.

| card | card minutes per pass | where the time goes |
|---|---|---|
| aifoundry2 | 0.3 to 1.7 (measured: 102 s, 24 s, 18 s) | p1 heated from 65 C (21 heater launches, about 80 s); on a die already at 75-78 C one or two die reads; 17 processes and the 4.9 s probe take about 15 s |
| aifoundry3 | 0.25 (measured: 15 s, 15 s, passes 1-2 of 25 Sep) | no heater |
| aifoundry1-c0, -c1 | about 0.5 to 3 | as aifoundry2, but their idle dies read 57-65 C, so a pass after a pause heats longer (card 0 idles at 18.8 W and cools faster); at least one 2 s heater launch per heat (about 4 s with start-up, twice in passes 1-3) and two `ettelem config` reads (about 1 s) |

The plan allowed 18 and 10 card minutes per 5 passes. The worst case is bounded by 17 × 10 s plus the lib's heat
limit, well under 35 min, so a pass is never split. On aifoundry1 each card runs its own queue (`V3_DEVICE=0` and `1`);
put `mem 1` to `mem 5`, then `mem 6` to `mem 8`, in each card's schedule.

**Smoke (`block.sh 1 --smoke`, exp `mem-smoke`, about 25 s of card time).** It checks each component in its smallest
form:
- `--info`;
- one 2 s heater launch on a governor-free card, with the die read before and after;
- the sampler;
- t_raw, t_rawodd and t_glitch;
- the plan's smoke test (a 16-line decomp from shire 7, `--hart 448`), plus a 4-line ladder for its L1 reference;
- a 1-rep wake-up probe between the 1 s pre and post samples;
- `memv3.py smoke`, which parses every output and prints the problems to `smoke.json`.

On a busy-rule card the smoke also records the idle state (at its start and end) and checks that every MEMPROBE program line carries the
kernel window (`t_start_ms`, `t_end_ms`), `cycles` and `wall_s` the busy rule reads; a build without them is a
problem. The block is ok only if there are no problems.

**Dry run.** `V3_DRY=1 bash tools/claims-v3/mem/block.sh <k> [--smoke]` prints every device call, including `--info`,
the heater, the samplers and each memprobe launch. `V3_FORCE=1` re-runs a finished pass and first moves the old
folder aside as `p<k>.attempt-<time>`.

## Per-pass layout (`build/claims-v3/<card>/mem/p<k>/`)

- Program data: `<prog>.u32` and `<prog>.json.gz` (labels) for the 11 programs; `req{7,24,31}/{ladder,decomp}`;
  `wake/wakeup.*`, `wake/pre.jsonl`, `wake/post.jsonl`.
- Telemetry and heating: `telemetry.jsonl.gz`, and `heat.jsonl` on governor-free cards; `idle_state.jsonl` on
  busy-rule cards (aifoundry1's two).
- Process logs: `info.log`, `memprobe.log` (MEMPROBE lines), `memprobe.err` (host stderr, one header per process),
  `runs.jsonl` (rc and times per process), `order.txt`, `gen.log`.
- Records: `code.sha256` (including the prereg copies and gen_ops.py), `binary.sha256` (the host and
  `kernel/memprobe.elf`), `drop.json`, `block.json`.
- Size: about 1.5 MB per pass.

## What is dropped, and why

- **aifoundry2 X1 part (registered rule).** An X1 part (the 11 programs plus the requesters, all under the sampler) is
  dropped if any sample has `mhz.minion != 600`, or if there is no telemetry (no sample with a clock reading). This is
  the plan's rule. A sample whose frequency request failed carries no `mhz` field (ettelem prints it only on success);
  it is a gap, not a sample off 600 MHz, and is counted as `n_no_clock` in the pass record. The refresh period and hop
  slope are never used to drop, because they are under test.
- **aifoundry3 X1 part (pinned).** It is never dropped on the clock, which is recorded. aifoundry3 is pinned at 600 MHz.
- **aifoundry1's X1 parts (busy rule, amendment).** The registered test is applied to the *busy* readings only: a
  sample is busy when it read the clock (at `t_ms + took_ms`: ettelem asks for the frequencies last of its six
  requests) inside a memprobe kernel window, `t_start_ms` to `t_end_ms` of the MEMPROBE program lines (host epoch ms,
  the sampler's clock). The X1 part is dropped if there is no telemetry or no clock reading at all, if no reading is
  busy, or if any busy reading is off 600 MHz. Readings between kernels (process start-up and tear-down, the gaps
  between processes) are idle brackets: they are recorded as the card's idle clock and never drop a pass. On the real
  aifoundry2 passes of 25 Sep the 17 kernels took about 0.4 s of a 4 s X1 part and 3 to 5 of the ~41 readings were
  busy, so a pass with no busy reading (then dropped and re-run) should be rare. A pass whose MEMPROBE lines carry no
  window (a build without the epoch stamps) falls back to the registered any-sample rule. There is no ramp allowance
  (V3-MMB forgives a busy reading below 600 MHz in a process's first second): a memprobe kernel lasts 2-85 ms, all of
  it inside any such ramp, and its latencies in cycles depend on the clock, so a busy reading off 600 MHz drops the
  X1 part. MEM-P5's refresh period (2,325 cycles at 600 MHz) remains a clock witness inside every kept pass.
- **Wake-up probe.** It is judged on its own, not on the X1 sampler. On aifoundry2 (registered rule) a probe whose
  pre or post samples show `!= 600` (or are missing) is dropped and re-run. This follows the binding rule, although
  EXP-dvfs-1's P6 only says the clock is "recorded" there. On aifoundry3 the probe is kept and P6 reports whether the
  clock was 600 MHz. On aifoundry1's cards (busy rule) the pre and post samples are idle brackets (card 0 reads
  300 MHz there), recorded, never a drop; the probe is judged on its own clock, its minion cycles over its wall time
  from its MEMPROBE line, which must lie in 594-602 MHz (`F_EFF_BAND`). This reads 599.84 MHz on each of aifoundry2's
  three real probes (the ~2 ms launch overhead of a 4.85 s kernel). The band's edges are about one sampler period
  (100 ms) at another operating point: 100 ms at 300 MHz lowers the probe's clock by about 6 MHz, 100 ms at 700 MHz
  raises it by about 2 MHz; a longer excursion drops the probe, a shorter one is not resolved (as with aifoundry2's
  5 Hz pre/post samples). The lower edge also allows about 50 ms of launch overhead. At 300 MHz the probe would need
  9.7 s and time out at the host's 6 s wait (incomplete, dropped). P6 on these cards is the probe's own clock.
- **Incomplete or failed blocks.** A program whose u32 count differs from its labels makes the X1 part incomplete.
  Any block whose `block.json` is not `ok` is not used, and neither are the queue's `p<k>.attempt-*` folders.
- **Extra passes.** The reducer uses the first 5 kept X1 passes and the first 3 kept probes on each card, in pass
  order. Later kept passes are listed in `<out>.passes.json` as unused. This is a fixed rule, not a choice.

## Deviations from the plan's commands, and why

- **Arena base once per pass.** `--info` runs once per pass, not once per session, because every pass is its own
  session, at least 10 minutes apart. The base is read from the `arena_base` field of the MEMPROBE line. The host
  prints `MEMPROBE {"test":"info","arena_base":"0x…"}`, so this is the same value as the plan's
  `grep -o '0x[0-9a-f]*' | head -1`.
- **Stopping the sampler.** The plan's `kill $SAMPLER` is lib.sh's `stop_sampler`, which sends SIGTERM and waits. The
  plan's `| tee -a memprobe.log` is an append to `memprobe.log`.
- **Pre and post samples.** They use `start_sampler <file> 1 --every-ms 200` (retry and drain), a 1.2 s wait, and
  then `stop_sampler`. The plan uses a bare `timeout 10 ettelem sample --seconds 1 --every-ms 200`. The samples are
  the same: ettelem reads its flags in order, so a later `--every-ms` overrides lib.sh's 100, as `ettelem.cpp` line
  194 shows.
- **Heat before the probe (governor-free cards).** The die is topped up to 76 C before the wake-up probe as well, not
  only once before the sampler. The binding rule is that memory-bound work on aifoundry2 starts at 76 C or above, and
  the X1 programs let the die cool; aifoundry1's cards take the same rule.
- **Skipped probe (registered rule, aifoundry2).** When the pre sample cannot start, the probe is skipped, because it
  would be dropped anyway. On the other cards the pre sample decides nothing, so the probe runs.
- **Timer programs in separate processes.** The E-hub-2 component ran t_raw, t_glitch and t_rawodd in one process;
  the merged V3-MEM plan, followed here, runs each in its own process. As a result, MEM-R3 reads e from the t_glitch
  launch itself (see below).
- **Re-runs.** Passes 6 and later are the plan's "re-run dropped passes until >= 3 kept (target 5)", made
  automatic. The wake-up probe runs past pass 3 only as such a re-run.
- **Mid-pass arrivals.** If another user arrives mid-pass, the block stops with rc 3 before the next program or
  heater launch (the queue retries the pass). After the X1 part it only skips the wake-up probe. The block also
  checks the `et_soc1` use count before it starts, except with `V3_DEVICE` set (aifoundry1: the count covers both
  cards, and the other card's queue legitimately holds its own).
- **Idle state (aifoundry1's cards).** Two `timeout 10 ettelem config` reads per pass, outside the sampler and with no
  kernel running, into `idle_state.jsonl`: not in the plan, whose two cards both idle at 600 MHz. The registered cards
  keep the registered procedure (no extra read); their idle clock is in the sampler's between-kernel readings.
- **Heating (governor-free cards).** `heat76` in block.sh repeats lib.sh's `heat_to 76` (same heater command, same
  150-launch limit, same `heat.jsonl` record) and adds an `others_present` check before each heater launch, which
  lib.sh's loop lacks. Like lib's `heat_to` it never heats blind: a failed die read launches nothing, and 4 failed
  reads in a row give up (without lib's drain, which on aifoundry1 would open both cards; the next block's
  `start_sampler` drains). On busy-rule cards it makes at least one launch per call (the four-card section). In a dry
  run it calls lib's `heat_to` stub (and prints the busy-rule launch), so the dry output still shows the heat.
- **Smoke.** The smoke test is larger than the plan's one 16-line decomp from shire 7, so that it checks every
  component (listed above).

Checked against the sources, all of which agree with the plan:
- **gen_ops flags.** Every gen_ops flag exists in `workloads/memprobe/gen_ops.py`. bits keeps its default
  `--pre-delay 2000`, as in the committed 19 Sep run.
- **memprobe_host.** `memprobe_host --hart H` launches on shire H/64 and copies the op list into that shire's own
  scratchpad (`host/main.cpp`, `kernel/memprobe.c`). The host waits at most 6 s per kernel. The probe's 16M-cycle
  delays make about 4.9 s at 600 MHz (E18 held the card for 4.9 s), so it fits.
- **Build paths.** The paths come from lib.sh. On aifoundry2 the host is `build/memprobe-v3/host/memprobe_host`,
  whose `kernel/memprobe.elf` has the same sha256 (`55c6dbab…`) as the 19 Sep build. On aifoundry3 it is
  `build/memprobe/host/memprobe_host` under `~/nekko`.
- **The requester reducer.** The inventory's `recompute_latency.py --requester` cannot read a `req<S>/` folder. X2
  uses the verifier's `extra_values.py --x2-only`, as the plan says.

## Reduction

```bash
# after collecting build/claims-v3/<card>/ of every card under one folder DIR (DIR/aifoundry2/mem/p1/...,
# DIR/aifoundry3/..., DIR/aifoundry1-c0/..., DIR/aifoundry1-c1/...; any other folder with a mem/ inside is read too)
python3 tools/claims-v3/mem/reduce.py --data DIR --out DIR/mem-verdicts.json   # also writes DIR/mem-verdicts.passes.json
```

The reducer runs off-card in under 1 s per pass. It works on partial data: with fewer than 3 kept passes on a card,
an item is `INSUFFICIENT`. Each record holds the item, its claims, the plan's prediction and decision rule, the test,
the per-card values and intervals, the outcome (`PASS`, `FAIL`, `CARD-DIFFERENT` or `INSUFFICIENT`) and a one-line
reading. MEM-R2 also carries the page wording.

**Registered and all-cards outcomes (four-card amendment).** `outcome` and `reading` are the registered ones,
computed exactly as before from aifoundry2 and aifoundry3 only (checked: on every synthetic set, and on the real
passes collected so far, aifoundry2 p1-p3 and aifoundry3 p1-p2, old and new reducers give identical registered
fields). Each record adds `all_cards`: the same per-card test on every card of the campaign
(the four expected cards, then any other card folder), with `per_card` holding all of them. `all_cards.outcome` is
`PASS` if the item holds on every tested card, `CARD-DIFFERENT` if on some, `FAIL` if on none, and `INSUFFICIENT`
while a tested card has fewer than 3 kept repeats; a card with no folder counts as lacking repeats and is listed in
`no_data`. `decided_outcome` is the same rule over the cards that have enough repeats, for partial reporting. Every
item is registered "each card", so it applies unchanged to aifoundry1's cards, except MEM-R2, whose count is
aifoundry2's: there `all_cards` tests aifoundry2 only, reports the other three cards' readouts
(`reported_only`), and gives the page wording over every card (`all_cards.page`). MEM-W's P6 is the pre/post clock on
aifoundry2 and aifoundry3 and the probe's own clock on aifoundry1's cards (`P6_basis`). MEM-W's `all_cards` also
carries each card's idle clock (`idle_clock`: the modal minion clock between kernels, from the X1 sampler's idle
readings, the probe's brackets and, on aifoundry1, `ettelem config`) and a note naming a card whose idle state
differs (aifoundry1-c0 is expected at 300 MHz, `low_power`): the probe's idle delays spin inside one kernel, so that
between-kernel state is not what P5 tests. The sidecar lists each pass's clock rule, busy and idle readings,
`idle_state` and the probe's own clock, and `idle_clock` per card.

**MEM-P1 to P10 and MEM-X2** use `prereg/`, unchanged. `reduce.py` stages each pass in a scratch copy (it un-gzips
the labels; `recompute_latency.py` never writes next to the data). It then calls `crosscard_v3.pass_values`, which
runs `recompute_latency.py --l1-ref --fixed-model`, `timer_window.py` and `extra_values.py`, including `--x2-only` for
each complete `req<S>/`. The bands, the one-sided rule for bounded fractions and the every-pass rules are those of
`crosscard_tests.py` as `crosscard_v3.py` modifies them. On top of that, `reduce.py` applies these rules from the V3
table:

- **MEM-P7.** The registered decision is "every pass, each card", so z must lie in [-3, 3] in every pass. The
  inventory's code put z under a 99% t-interval; that interval is still reported beside the rule.
- **MEM-P10.** "Arena base 1 GB aligned" is checked in every pass, from the MEMPROBE lines. A block stops on a
  misaligned base (the plan's assert), so such a pass is never kept; the reducer therefore also reads the base of
  every attempted pass folder, whatever its status, and a misaligned one fails the sub-test on that card.
- **MEM-P5.** A pass whose median locked-loop period is outside 512 to 651 cycles is reported and not tested for the
  slow fraction. If every pass on a card is outside, that sub-test does not apply.
- **Every-pass items, and the 3-repeat rule.** The plan's common rule is that fewer than 3 kept repeats on a card
  leave the claim as it is. It applies in both directions: an every-pass item (and MEM-R1, R2, R3) with fewer than
  3 kept passes on a card is undecided there even when a pass already shows an exception; the exception is listed in
  the reading ("seen: ..."). With 3 or more kept passes, any exception fails the item. The inventory's EXACT had no
  pass count.
- **anatomy-35.** It is restored only if P8b and P8c hold on both cards.

**MEM-R1 to R3** follow the registered test text (the plan's "validate3/hubv phase analysis" was inline code, not a
script) and are implemented in `memv3.py`:

- **Raw pairs (t_raw, t_rawodd).** A read at low bits `L <= e` returns 128 short with its low bits unchanged. So a
  pair `(L0, L1, d)` fits the windows e with `10 + 128([L0<=e] - [L1<=e]) == d`.
  - The registered readout uses only the pairs whose first read is at low bits 0 or 10 (t_raw), or at 0, 1, 10 or 11
    (t_rawodd), and whose difference is 10, 138 or -118. It is the set of e that fits them; the phases actually
    reached are reported. A pair with another difference is an R1 exception, not a reading of e, and a readout that
    no single e fits ("none fits") is not a reading either: neither can make R2's readouts "differ".
  - R1 uses every pair. The differences must be only 10, 138 or -118, and the set of e that fits all pairs must be
    non-empty and meet {9, 10, 11}.
- **t_glitch.** With no ±128 errors, e = 10. When the modal stamp phase of the -128 errors is 10 after that of the
  +128 errors, e = 9. When it is 10 before, e = 11. Anything else, including intervals other than 10, 138 or -118, is
  an R1 exception.
- **R2.** The readouts are sets, and "at least 2 distinct e" means that no single e fits every readout. The outcome
  is aifoundry2's, with at least 3 kept passes. aifoundry3 is reported (no prior), and so are aifoundry1's cards. The
  page wording is chosen only from cards with at least 3 kept passes (registered: the two cards; `all_cards.page`:
  every card).
- **R3.** R3 is per t_glitch launch: e = 10 needs 0 off-by-128 intervals, and e = 9 or 11 needs 1% to 3%. Since each
  program is its own process, e comes from the same launch, so R3 tests the size and the single-phase shape of the
  miscorrection.

**MEM-W** (EXP-dvfs-1) uses the first 3 kept probes per card:

- **P1.** For L1 and for L1-in-place, at least 19 of 20 lines must be exactly 0 at every idle, and every nonzero
  value must be ±128.
- **P2.** The L3 median difference at 16M must be within ±2.
- **P3.** The L2 values are first re-referenced to the frame the 59-62 / 48-51 bands were written in: the 22 Sep run,
  whose L1 read 17 raw. Each value is shifted by (the pass's median L1 value - 17). This is the plan's "every latency
  re-referenced to the pass's own L1 hit"; without it, a build that reads L1 at 10 would fail the band. P3b is the
  median at 300 cycles against the median at 16M, within 1.
- **P4.** Each DRAM difference at 16M gets a class: slow is +8..+15, fast is -7..+7, outlier is beyond ±30, and
  anything else is "other". A pass holds if 40% to 85% of lines are slow, no line is "other", and at most 2 are
  outliers. Class agreement means the same label at 1,000 and at 16M, pooled per card, at least 0.80.
- **P5 (the decision).** No level may have at least 18 of 20 lines at +5 or more at 16M.
  - PASS on a card when P5 holds in 3 of 3 probes.
  - "Wake-up claimed" when P5 fails in at least 2 of 3; a single failure is "mixed". Both count as not holding.
  - A failing P3b only drops the settling explanation (dvfs-14), and the reading says so.
- **P6.** P6 reports the pre and post clocks, and on aifoundry1's cards the probe's own clock (cycles / wall time),
  which is what decides there.

**Pre-registered code (`prereg/`)** is copied byte-for-byte from the scratch folders the plan names. The sha256 of
each copy equals its source's:

```
bc16d52ab35132ee8f3335b9f0f4b2ccf78ff7e9aa32ca95c52b7b0f16c092c0  crosscard_tests.py   (validate3/inv/anatomy-work/)
c14f7fb0a347f3bab24b541e9abfe1ad5057c3afe38ac152fda220ee2911c156  recompute_latency.py (validate3/inv/anatomy-work/)
9951c3c1287b02d8788543ccfc632088fa929e68128e8b26c41363a45c3cb896  timer_window.py      (validate3/inv/anatomy-work/)
379e1522c16f5cc9884263c83e29d63084989fdbe996d6a80db35e3502ac89b3  mp/gen_ops.py        (validate3/inv/anatomy-work/mp/, = workloads/memprobe/gen_ops.py)
7088701dafb4455148fabeafab8ead0b8fdf5b609c74d50505ac651f64a27bbe  crosscard_v3.py      (validate3/anatomy-verify/tests/)
3fac585cf840b5be43d5e10ad47068771ba87f591e37acec5ed7a3534d3f7a39  extra_values.py      (validate3/anatomy-verify/tests/)
```

`crosscard_v3.py` still names the scratch path of `crosscard_tests.py`. `reduce.py` imports the prereg copy first, so
the copies are what runs even after the scratch folder is gone.

**Tested (no card).** The data are under `validate3/drv/mem/`, built by `make_synth.py`.

| test data | result |
|---|---|
| the committed 19 Sep folder as one aifoundry2 pass | P1 to P10 values equal the verifier's `dryrun_v3.json`; the readouts already differ (t_raw e >= 10, t_glitch e = 9, as hub-001 found), but with one pass every item, R2 included, is `INSUFFICIENT` |
| 5 perturbed passes per card, with planted drops | the drops are applied: a 700 MHz sample, and an 800 MHz pre-sample on a probe |
| the same, with a planted aifoundry3 L3 shift | `CARD-DIFFERENT` on MEM-P1 |
| planted failures | P3, P7, R1 (e = 12), R2 (e constant) and MEM-W (wake-up claimed) all fail as expected |
| partial data | every item is `INSUFFICIENT` |
| a sixth kept pass | it is not used |

Reviewer's cases (`validate3/drv/mem/review/`, built by `make_review.py`; outputs `*-verdicts.json`):

| test data | result |
|---|---|
| `bothfail`: the same failures planted on both cards (L3 +6, one msmap line, refresh period 2,340, t_rawodd e = 12, +15 cycles on DRAM at 16M in 2 of 3 probes) | `FAIL` on MEM-P1, P3, P5, R1 and MEM-W (wake-up claimed on both cards) |
| `few`: aifoundry2 has 2 kept passes, one with an msmap failure | every item `INSUFFICIENT`; MEM-P3's reading lists the failure ("seen: ...") |
| `baddiff`: e = 10 everywhere, one aifoundry2 t_raw pair at low bits 0 with difference 11 | R1 `CARD-DIFFERENT` (the exception), R2 `FAIL` (e constant; the bad pair is not read as a second e) |
| `clock`: aifoundry2 pass with one sample lacking `mhz`, one with a 700 MHz sample, and a failed block on base 0x8050000000 | the gap pass is kept, the 700 MHz pass dropped; MEM-P10 `CARD-DIFFERENT` from the misaligned attempt |

Four-card cases (`validate3/fourcards/mem/`, built by `make_fourcards.py` from the same helpers; each run with this
reducer and with the previous two-card one, `orig/`, whose registered fields `cmp_registered.py` compares):

| test data | result |
|---|---|
| the nine earlier sets above (`fourcards/mem/regress/`) | registered fields (outcome, reading, page, per-card values of aifoundry2 and aifoundry3) identical to the two-card reducer's |
| `allpass`: every item holds on all four cards; aifoundry2 p2 has a 700 MHz reading between kernels and an 800 MHz pre-sample; aifoundry1-c0 idles at 300 MHz (`low_power`), has one busy reading at 700 (p2), a probe at 450 MHz (p3) and a pass with no busy reading (p4); aifoundry1-c1 has an 800 MHz reading between kernels (p5) | registered and `all_cards` `PASS` on all 15 items; aifoundry2's p2 dropped by its registered rule (X1 and probe); c0's p2 and p4 X1 parts and p3's probe dropped, its 300 MHz idle readings never; c1's p5 kept; MEM-W's note names a1c0's idle at 300 MHz |
| `c0diff`: as `allpass`, with aifoundry1-c0's L3 +6 cycles, t_rawodd e = 12 and a wake-up (+15 cycles on DRAM at 16M in 2 of 3 probes) | registered `PASS` everywhere; `all_cards` `CARD-DIFFERENT` on MEM-P1, R1 and W (a1c0 fails), `PASS` elsewhere |
| `missing`: as `allpass`, without aifoundry1-c1's folder | registered `PASS`; `all_cards` `INSUFFICIENT` (a1c1 "no data", `decided_outcome` `PASS`), except MEM-R2 (tested on a2 only) `PASS` |
| `c0slow`: as `allpass`, but aifoundry1-c0's busy readings are 300 MHz and its probes run at 299 MHz | every c0 X1 part and probe dropped; `all_cards` `INSUFFICIENT` with `decided_outcome` `PASS`; registered unchanged |
| `c0heated` (reviewer, `fourcards/mem/review/`): as `allpass`, but aifoundry1-c0 reads 600 MHz between kernels and in the probe brackets while `ettelem config` still reports 300 MHz `low_power` | `all_cards` `PASS` on all 15 items; MEM-W's note still names a1c0 as idling off 600 MHz (from its config reads) |
| real passes of 25 Sep (reviewer): aifoundry2 p1-p3 and aifoundry3 p1-p2, and the same with aifoundry3 p1 copied as p3 so every item decides | registered fields identical to the two-card reducer's; `memv3.py finish`, `kept` and `wake-needed` give the same decisions as the two-card version on these passes |

Dry runs (`V3_DRY=1`, from the tree root with the block's absolute path; aifoundry3 and aifoundry1 simulated with a
`hostname` shim, aifoundry1 with `V3_DEVICE=0` and `1`): the smoke and passes 1 to 8 on all four card ids exit 0.
aifoundry2's and aifoundry3's device calls equal those of the two-card block's dry runs; aifoundry1's cards add the
heater (with its at-least-one launch per heat) and the two `ettelem config` reads (smoke included). Logs in
`validate3/fourcards/mem/dry/` and, after the review's changes, `validate3/fourcards/mem/review/dry/`. On aifoundry1
without `V3_DEVICE` lib.sh stops the block (exit 2).
