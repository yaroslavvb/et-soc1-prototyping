# Amendments to the pre-registered plan

Each amendment is recorded before any data of the experiment it touches exists. The run code that implements the
plan is committed under `tools/claims-v3/` (one directory per experiment, with its `README.md` listing where the code
departs from PLAN3's command lines and why); every block records the sha256 of the code it ran (`code.sha256`).

**A1 (25 Sep 2026, before any V3-IDLE data).** IDLE-b ("every whole-degree bin inside -0.23 ± 0.3 W") leaves out
each cycle's first and last bin. The die temperature is read in whole degrees, so a cycle's edge bins average only
part of a degree and are biased by 0.1-0.3 W on aifoundry2 (the reviewer's simulation), which would fail the item
from rounding, not physics. `tools/claims-v3/idle/reduce.py`.

**Readings confirmed, not amendments** (the reviewers asked; the registered rules stand as the code implements them):
- a telemetry sample with no clock field is a gap, not a drop (V3-MEM); with fewer than three kept passes a card is
  undecided even after an every-pass failure (all experiments);
- band items pass only when the 99% interval excludes the null *and* the estimate lies in the band; a sign-only
  result counts as a failure (V3-CAT, V3-WIRE, V3-ABL);
- V3-X5 keeps its registered hot target on aifoundry3 (65 °C launch, 68 °C preheat) although it is probably out of
  reach there; the registered correction to the launch temperature applies, and the reached temperatures are reported;
- V3-RL's RL-g scratchpad parts pool the zeros and random passes as registered; their readings say so;
- the scratchpad bus-error probe (`LAT_SCPSELF`) is not run: it faults a shared card on purpose, and the claim it
  would test (hotline-relay-l2-52) stays labelled one card.

## A2 (25 Sep 2026, before any data from aifoundry1's cards): the campaign on four cards

After the machine fixes of 25 September the owner asked for every measurement to be re-run on every card. aifoundry1's two
cards now work (card 0 firmware 1.4.1, card 1 firmware 1.2.0; aifoundry2 and aifoundry3 run 1.3.1), so the version-3
experiments run on four cards: aifoundry1-c0, aifoundry1-c1, aifoundry2, aifoundry3. The registered outcome of every item
is computed exactly as before from aifoundry2 and aifoundry3; each item gains an `all_cards` outcome over every card
with enough kept repeats (PASS if it holds on each, CARD-DIFFERENT if on some, FAIL if on none, INSUFFICIENT while a card
lacks repeats). Items whose registered value belongs to one card are reported, not tested, on aifoundry1's cards.
Decisions use the post-fix campaign only; the passes run before the fixes (25 Sep, 10:00-16:19) are kept as a
pre-fix set. A new experiment, `catfull`, re-runs the energy manual's full catalogue (three passes per card).
The rules specific to each experiment follow, as their reviewers wrote them before any aifoundry1 data.

### A2.mem

**A<n> (25 Sep 2026, before any aifoundry1 data): V3-MEM on four cards.** The owner asked for every measurement on
every card after the machine fixes of 25 Sep, so V3-MEM runs its registered passes (5 per card, then the conditional
re-runs 6 to 8) on aifoundry2, aifoundry3, aifoundry1-c0 and aifoundry1-c1. On aifoundry1, `V3_DEVICE=0|1` selects the
card. The commands, seeds, programs, shuffled order, requesters, wake-up probe and bands are the registered ones.
Nothing registered changes for aifoundry2 and aifoundry3: their device calls are identical in dry runs to the version
that ran passes 1-3 on 25 Sep, and their drop rules and decision code are the same. The one change they share is in a
failure path: the heater loop no longer launches when a die read fails (below). On every earlier test set, on the
four-card sets and on the real passes of 25 Sep (aifoundry2 p1-p3, aifoundry3 p1-p2), each item's registered outcome,
reading and per-card values came out identical, and so did the per-pass keep/drop decisions. The rules for
aifoundry1's cards are fixed here, before any of their data:

- *The cards.* aifoundry1-c0 runs firmware 1.4.1 with TDP 65 W and a 65 C threshold. Between kernels it idles in a
  `low_power` state at 300 MHz and 398 mV (18.8 W). aifoundry1-c1 runs firmware 1.2.0 with TDP 65 W and a 65 C
  threshold, and idles at 600 MHz and 499 mV (32.9 W). The governor is free on both cards.
- *Blocks.* A governor-free card (lib.sh `GOV_FREE`: every card except aifoundry3) is treated as aifoundry2 is:
  - it heats to 76 C before the X1 part and again before the wake-up probe (same heater command, 150-launch limit);
  - a block whose sampler does not start fails.
  aifoundry1's cards take 76 C because their threshold (65 C) and TDP (65 W) are aifoundry2's. This is not retuned
  after data. One parameter differs because the physics does: on aifoundry1's cards each heat makes at least one
  heater launch even when the die already reads 76 C or more. In the 25 Sep clock test card 0 left its 300 MHz `low_power`
  idle only at the end of its first 2 s launch and then stayed at 600 MHz, while memprobe kernels last 2-85 ms; a
  pass started on a die left hot by the previous block would otherwise run its kernels at whatever the idle state is.
  Card 1 (idle at 600 MHz) gets the same launch; it costs about 4 s per heat. If card 0's firmware still ran the
  kernels below 600 MHz (after the launch, or at a thermal step-down floor on the hot die), the rule below drops those
  passes, and the items stay INSUFFICIENT on that card.
  On every governor-free card, aifoundry2 included, the heater loop never heats blind: a failed die read launches
  nothing, and 4 failed reads in a row end the heat (before the X1 part the block then fails and the queue moves on;
  before the probe, the probe proceeds as after any heat that gave up). Before, a failed read was followed by a heater
  launch. This changes nothing on a pass whose die reads succeed, which is every pass so far.
- *Idle state.* Every aifoundry1 pass (and smoke) records the card's idle state at its start and end in
  `idle_state.jsonl`: power state, minion MHz and mV from `timeout 10 ettelem config`, read while no kernel and no
  sampler runs. The start read comes before any heating, so it shows the idle state the card rests in. The registered
  cards keep the registered procedure, so they get no extra read. For them, the idle clock comes from the sampler's
  between-kernel readings.
- *Use count.* With `V3_DEVICE` set, the `et_soc1` module use-count check is skipped, because the module serves both
  cards and the other card's queue may hold its own card. Two checks decide instead: `ours_running`, which is per
  card, and `others_present`, which covers other users, their device processes and a running CI job.
- *Clock rule on aifoundry1's cards: X1 part (the "busy" rule).* The registered aifoundry2 test (at least one clock
  reading, every reading 600 MHz) is applied only to the busy readings:
  - A reading is busy when the sampler read the clock inside a memprobe kernel window. The reading time is
    `t_ms + took_ms`, because ettelem asks for the frequencies last. The window is `t_start_ms` to `t_end_ms` from
    the pass's MEMPROBE program lines: 11 programs and 6 requester launches.
  - An X1 part is dropped when there is no telemetry, no clock reading, or no busy reading, or when any busy reading
    is off 600 MHz.
  - Readings between kernels (process start-up and tear-down, and the gaps between processes) are idle brackets. They
    are recorded as the card's idle clock and never drop a pass. Without this rule, card 0's 300 MHz idle would drop
    every one of its passes.
  - Unlike V3-MMB's rule, there is no ramp allowance. A memprobe kernel lasts 2-85 ms, so all of it would fall inside
    a ramp, and its latencies in cycles depend on the clock.
  - On the 25 Sep aifoundry2 passes, the 17 kernels took about 0.4 s of a 4 s X1 part, and 3 to 5 of about 41
    readings were busy. A pass with no busy reading should therefore be rare; such a pass is dropped and re-run.
  - A pass whose MEMPROBE lines carry no window (a build without the epoch stamps) falls back to the registered
    any-sample rule. On aifoundry1's cards the smoke block fails on such a build.
- *Clock rule on aifoundry1's cards: wake-up probe.* The probe is judged on its own clock:
  - The clock is minion cycles over wall time from its MEMPROBE line. The probe is kept if it is complete and that
    clock lies in 594-602 MHz.
  - On aifoundry2's three real probes of 25 Sep this read 599.84 MHz each time: the overhead of a 4.85 s launch is
    about 2 ms.
  - The band's edges are about one sampler period (100 ms) at another operating point: 100 ms at 300 MHz lowers the
    probe's clock by about 6 MHz, 100 ms at 700 MHz raises it by about 2 MHz. A longer excursion drops the probe; a
    shorter one is not resolved, as it would not be by aifoundry2's 5 Hz pre/post samples either. The lower edge also
    allows about 50 ms of launch overhead (aifoundry2's is about 2 ms; a firmware with a slower launch path would drop
    every probe, and the smoke's 1-rep probe shows the overhead first).
  - At 300 MHz the probe would need 9.7 s and time out at the host's 6 s wait.
  - The pre and post 1 s samples are idle brackets (card 0 reads 300 MHz there). They are recorded and never drop the
    probe, and the probe runs even if the pre sample fails.
  - If the MEMPROBE line lacks cycles or wall time, the registered pre/post rule applies.
  - On these cards, P6 is the probe's own clock.
- *aifoundry2 keeps its registered rule.* Its governor is free too, but its registered any-sample rule stays, for the
  registered outcome and for its column in `all_cards`. That rule is stricter than the busy rule (its idle brackets
  can drop a pass), and on its 25 Sep passes every reading, busy or idle, was 600 MHz.
- *Decisions.* `outcome` and `reading` stay the registered ones, from aifoundry2 and aifoundry3 exactly as before.
  Each item adds `all_cards`, which applies the registered per-card test unchanged on every card of the campaign.
  Every card has its values in `per_card`.
  - PASS: the item holds on every tested card. CARD-DIFFERENT: it holds on some. FAIL: it holds on none.
  - INSUFFICIENT: a tested card, including one with no data folder, has fewer than 3 kept repeats.
  - `decided_outcome` applies the same rule over the cards that have enough repeats.
  - Every V3-MEM item is registered "each card" and applies unchanged, except MEM-R2, whose count is aifoundry2's.
    There, `all_cards` tests aifoundry2 only and reports the other three cards' readouts. The page wording is also
    given over every card, as reported.
  - anatomy-35's restoration stays the registered two-card rule. The all-cards reading states whether P8b and P8c
    hold on every card.
  - MEM-W's `all_cards` carries each card's idle clock between kernels and its `ettelem config` reads, with a note
    naming a card whose idle state differs (card 0 is expected at 300 MHz, `low_power`; a card counts as differing if
    its modal idle reading or any config read is off 600 MHz). The probe's idle delays spin inside one kernel, so that
    between-kernel state is not what P5 tests.
- *Code.* `tools/claims-v3/mem/` has block.sh `9e4ac97e…`, memv3.py `22ac005b…` and reduce.py `43991309…` (sha256).
  The four-card tests are in `validate3/fourcards/mem/` and `validate3/fourcards/mem/review/`.
- *Operator.* aifoundry2's queue ran mem p1-p3 with the two-card code; if it is resumed, passes 4-8 run this code
  (same device calls and decisions on aifoundry2; `code.sha256` differs). Add `mem 1`..`mem 8` to both aifoundry1
  schedules, and sync `workloads/memprobe/gen_ops.py` and `tools/claims-v3/mem/` to `~/nekko` on aifoundry1 (the block
  refuses to start on a gen_ops.py that differs from `prereg/mp/`).

### A2.lat

**A-LAT-4C (25 Sep 2026, before any V3-LAT data from aifoundry1's cards).** V3-LAT also runs on aifoundry1's two
cards, `aifoundry1-c0` (firmware 1.4.1, TDP 65 W, threshold 65 C, idles at 300 MHz / 398 mV) and `aifoundry1-c1`
(firmware 1.2.0, TDP 65 W, threshold 65 C, idles at 600 MHz / 499 mV), selected by `V3_DEVICE=0|1`. Each runs the
aifoundry2 schedule: passes 1-3 as halves (`lat 11` ... `lat 32`) and the divergence blocks `lat 4`, `lat 5`. The
registered outcome of every item is unchanged: it is computed exactly as before, from aifoundry2 and aifoundry3
only. It is identical to the pre-amendment reducer's on the nine earlier test sets, on four-card test data and on
aifoundry2's real V3-LAT data of 25 Sep (passes 1-3, block 4). What changes, all fixed here before any aifoundry1
data (`tools/claims-v3/lat/`, README section "Four cards"):

- *Blocks.*
  - aifoundry1's cards are governor free and take aifoundry2's procedure: heated to 76 C before every unit, nocbench
    invocation and sparsity group, the sampler required, halves 11-32 recommended.
  - The c6 unit (V3-COOL's warm controls) stays on aifoundry2 only, because V3-COOL is registered for aifoundry2 only.
  - Every card now records its idle clock before each sampler start (`idle.jsonl`, one 1 s management read, ~20 s per
    pass). `order.json` also records `gov_free`, `heat_c` and `V3_DEVICE`.
  - On aifoundry1-c0 (or any governor-free card whose last idle probe reads below 600 MHz) the divergence-only short
    blocks (4, 5, 41-49) add one 85 ms clock-witness launch (all-minion TensorLoad from L2, 200,000 loads) before and
    after the subset, since their four 2 ms kernels would otherwise have only idle samples around them.
  - On a governor-free card the smoke heats to 76 C (aifoundry2's smoke included) and prints the clock inside and
    outside the kernel windows.
  - The block does not start while one of our device processes runs on its card (`ours_running`, per card when
    `V3_DEVICE` is set) or another user is present (`others_present`, also before every launch). It has no et_soc1
    use-count check, so the other card's queue on aifoundry1 does not block it.
  - With `V3_DEVICE` set, lib.sh's `drain_mgmt` is a logged no-op inside the block, including where lib.sh's
    `heat_to`, `start_sampler` and `stop_sampler` call it: `/opt/et/bin/dev_mngt_service` is not `ET_DEVICES`-filtered
    and would open the other card while that card's sampler holds its management node. A node that stays stuck then
    fails the unit instead of being drained.
- *Heating aifoundry1-c0: where the physics may say otherwise.* Measured on 25 Sep (two 2 s random fp32 matmul
  launches 1 s apart, 10 Hz sampler): c0 idled at 300 MHz / 18.6 W; during the first launch its power did not rise
  and it reached 600 MHz only at the launch's end; the second launch drew 49.4 W at 600 MHz; afterwards it idled at
  600 MHz (26 W). The die temperature was not recorded. So c0 leaves its low-power state under load and then stays
  at 600 MHz for a while, and the first launch after a low-power idle may run slow or late. Read from the governor
  source, not measured on c0: while a kernel runs, the loop steps the clock down when the die reads above 65 C and up
  otherwise. c0's boot point is 300 MHz (aifoundry2's is 600 MHz, its lowest point, which is why heating holds
  aifoundry2 at 600). So a c0 heated to 76 C could step its bursts down below 600, and a cool c0 could climb above
  600. Whether a heated c0 holds 600 MHz during kernels is not known. Heating stays at aifoundry2's 76 C, and the
  drop rule removes what does not run at 600, so c0 may end INSUFFICIENT. If c0 cannot reach 76 C, lib.sh's heat_to
  gives up after 150 launches, about 7.5 min for each heating call. The smoke on c0 shows the burst clock and the
  heating time before its passes are queued. Not queueing them changes no rule.
- *Drop rule on aifoundry1's cards* (drop_rule "idle-aware"). aifoundry2 keeps the registered rule: its idle point is
  600 MHz, so an idle sample there drops a launch only when it reads off 600, which means the governor lifted the
  clock, as registered. aifoundry3 is pinned.
  1. A sample that reads the card's idle point and lies outside every kernel window of its unit is set aside. The
     idle point is a reading below 600 MHz of the blocks' idle probes, or 300 MHz on both aifoundry1 cards, which
     is the low-power point queried on c0 on 25 Sep. c1 has only been seen idling at 600 MHz, but if it enters
     that state its idle samples must not drop its bursts. A sample inside a kernel window is a burst sample,
     whatever it reads.
  2. The registered rule applies unchanged to the remaining samples: within 0.2 s of the launch, else the nearest on
     each side within 5 s, all must read 600 MHz; cycles / wall time > 0.6 GHz drops.
  3. A kernel of at least 5 ms whose cycles / wall time is below 0.45 GHz is dropped. None of the committed 600 MHz
     kernels of at least 5 ms (1,997: hot line, nocbench, sparsity, onchip, enercat) reads below 0.475 GHz, and
     none of aifoundry2's 969 such kernels from 25 Sep reads below 0.476 GHz.
  4. A launch whose only samples within reach are idle samples is kept on its own implied clock when its kernel is at
     least 5 ms. Otherwise it takes its unit's verdict: kept if the unit has burst evidence and every non-idle sample
     and implied clock in it reads 600 MHz / 0.45-0.6 GHz. A launch with no sample at all is dropped, as registered.
     Caveat: on c0 a short kernel kept this way could have started below 600 MHz before the governor stepped up.
  5. sgemm is kept if all its bracket samples read 600 MHz. If some read the idle point and none reads anything else,
     it is kept only when every other unit of its block has the verdict "600 MHz". Caveat: such a process may include
     c0's wake from its low-power state, which would lengthen its first launch, so LAT-G's launch times on c0 carry
     that qualifier.

  `cards[<card>]` counts how every launch was judged (`launches_by_basis`) so the page can qualify c0's values.
  Without this rule c0's 300 MHz idle samples would drop every launch there: its synthetic passes under the
  registered rule give INSUFFICIENT on all 16 items. The same aifoundry2 data read as if from aifoundry1's cards give
  aifoundry2's values under this rule.
- *Four-card outcome.* Each item adds `all_cards`, over aifoundry1-c0, aifoundry1-c1, aifoundry2, aifoundry3 and any
  other card directory present:
  - PASS if the item holds on every card, CARD-DIFFERENT if on some, FAIL if on none;
  - INSUFFICIENT if a card lacks its repeats, a card with no data included;
  - the registered either-card rules (LAT-S1 and sgemm mismatches, LAT-N3's drop, LAT-S3, LAT-S5, LAT-R3, LAT-R (i))
    apply to every card and decide FAIL.
- *Bands.* Bands registered for each card apply unchanged. The parts whose band is a committed value of aifoundry2 or
  aifoundry3 are reported on aifoundry1's cards against both committed values, and not tested:
  - LAT-H P1c (unstopped host fractions ±2 pp);
  - LAT-R (ii) (each card's 5-offset line);
  - LAT-R (v)'s size, intensity and stage ratios (±5%).

  LAT-H P1a's stopped configurations are those stopped on both committed cards (the same split on both).
  `per_card` gives every card's values. LAT has no item on energy over idle; each card's idle probes and idle
  points are reported under `cards`.
- *Two cards on one host.* aifoundry1's two queues share the host CPU, which affects LAT-G's device-held time and the
  sgemm host's reference product, and they share the chassis airflow. c0's and c1's LAT blocks should not overlap.

### A2.mmb

**A<n> (25 Sep 2026, before any aifoundry1 data): V3-MMB on four cards.** The owner asked for every measurement on
every card after the machine fixes of 25 Sep, so V3-MMB runs its four registered passes on aifoundry2, aifoundry3,
aifoundry1-c0 and aifoundry1-c1. aifoundry1's two cards are not in the registration. Nothing registered changes for
aifoundry2 and aifoundry3: their drop rules, code paths and outcomes stay as they were. This includes aifoundry2's
registered load-step rule, which drops a pass for any sample off 600 MHz, idle samples included. Every idle sample on
aifoundry2 has read 600 MHz so far, and it enters `all_cards` with that registered rule. On every earlier test set, on
the new four-card sets and on the passes collected so far (two per card), each item's registered outcome and every
aifoundry2/aifoundry3 value came out identical. The rules for aifoundry1's cards are fixed here, before any of their
data:

- *The cards.* aifoundry1-c0 runs firmware 1.4.1 with TDP 65 W and a 65 C threshold. Between kernels it idles in a
  `low_power` state at 300 MHz and 398 mV (18.8 W). aifoundry1-c1 runs firmware 1.2.0 with TDP 65 W and a 65 C
  threshold, and idles at 600 MHz and 499 mV (32.9 W). The governor is free on both cards.
- *Blocks.* A governor-free card (lib.sh `GOV_FREE`) is treated as aifoundry2 is. It heats to 76 C before each E1
  workload, before ridge-X1 and before the load step. Its smoke block includes one heater launch. aifoundry1's cards use
  the same 76 C because their threshold (65 C) and TDP (65 W) are aifoundry2's. The pinned card (aifoundry3) keeps its
  60 s sleep before the load step. Every block records the card's idle state at its start and end (`idle-state.jsonl`:
  `ettelem config`'s power_state, minion MHz and mV, plus a die and clock reading). `order.json` records `gov_free`,
  `device` and `heat_c`.
- *Clock rules on aifoundry1's cards: only busy samples count.* A busy sample is one inside a launch's window, taken
  from the MMBENCH/MEMPROBE `t_start_ms`/`t_end_ms`. Idle brackets never drop anything. A busy sample below 600 MHz
  within 1 s of a process's first launch start is a ramp from the idle state: it is recorded and does not drop anything.
  Any other busy sample off 600 MHz drops that E1 launch, or the whole load-step pass. The registered implied_ghz band
  (0.595-0.605) applies on every card. A ridge-X1 process whose launch 0 alone is below the band (a ramp after the 3 s
  gap) still loses that launch, but the end-of-block check notes it instead of re-running the pass. Any other launch off
  the band re-runs the pass, as on every card.
- *E1 power values on aifoundry1's cards.* A workload's power values are kept if every timed launch is kept. They are
  also kept if the only dropped launch is launch 0 and the only reason is an implied_ghz below 0.595: that ramp falls
  inside the registered 1 s settle, before the power window starts. In that case per-W values use the kept launches.
- *Load-step reducer.* aifoundry1's cards have no measured rail filter, so their filtered values use aifoundry2's tau
  (1.148 s).
- *Verdicts.* Each item keeps its registered outcome from aifoundry2 and aifoundry3 and adds `all_cards`, with these
  outcomes:
  - PASS: it holds on every card on which it is tested.
  - CARD-DIFFERENT: it holds on some of those cards, or their 99% intervals disagree in sign.
  - FAIL: it holds on none.
  - INSUFFICIENT: a tested card has fewer than 3 kept passes. A missing card counts as having none.
  - REPORTED: the item is registered for aifoundry2 or aifoundry3 only.

  A band given for one registered card is reported on aifoundry1's cards, not tested. A clause registered for each card
  is tested on them unchanged. Item by item, on aifoundry1's cards:

  | Item | Tested | Reported only |
  |---|---|---|
  | MMB-a | L2 bands | DRAM band |
  | MMB-b | Throughput, exactness | Smoke clause (registered for aifoundry3) |
  | MMB-c | – | Whole item (watt bands) |
  | MMB-d | – | Whole item (compares aifoundry3 with aifoundry2) |
  | MMB-e | – | Whole item (lead bands) |
  | MMB-f | As on aifoundry3: L2 rise > 0, DRAM ~0 within ±0.5 W | – |
  | MMB-X1 a, b, c | All three, unchanged | – |
  | MMB-T | P4, P5, P6 (interval excludes 0), P8, P9; P7's tau = 0 overshoot and dip | P1, P2, P3, P10; P7's filtered clause |
- *Expected before the data.* If aifoundry1-c0 idles at 300 MHz in these blocks, then:
  - P9 ("600 MHz throughout", every sample) does not hold there.
  - P4 (minion rail over the cool1 baseline) and P6 (droop from idle0) include the step from the low-power idle to the
    600 MHz burst, and so do MMB-c's above-idle watts.

  A CARD-DIFFERENT on those items is therefore read as the idle state, not as DRAM, droop or matmul physics. Items that
  use an idle bracket carry each card's idle clock, and the reading names any card whose idle is not at 600 MHz.
- *The wake from `low_power` (measured 25 Sep ~16:40, before this campaign).* In a clock test on aifoundry1-c0 (two 2 s
  fp32 launches 1 s apart), the first launch after the low-power idle drew no extra power, and the clock reached 600 MHz
  only at its end, about 2.3 s in. The second launch ran at 600 MHz (49.4 W), and the card then idled at 600 MHz (26 W),
  not at 300. In a block, the smoke launches and the heater wake the card before any measured phase. If c0 stays awake,
  its idle brackets read 600 MHz and the expectations above do not arise. If it goes back to `low_power` during the
  block's idle gaps and the wake again takes longer than the 1 s ramp allowance, the rule is not widened after seeing
  the data:
  - The E1 calibration launch runs slow, so the timed launches are shorter and the power window shrinks (`cal.jsonl` and
    `meta.json` record this).
  - An E1 launch 0 with busy samples below 600 MHz after its first second drops that workload's power values.
  - A load-step pass whose first matmul or DRAM process has such samples is dropped.
  - A ridge-X1 process with slow launches after launch 0 re-runs the pass.

  c0's affected items then read INSUFFICIENT, and its idle-state records say why. The operator checks the `passcheck.err`
  of c0's smoke block and first pass before letting its queue continue.

Code: `tools/claims-v3/mmb/` (README "Four cards"). The sha256 values of the files as amended:

| File | sha256 |
|---|---|
| `cardrules.py` | `b3e922dfbe2bfebb917dc172be18c792469f204e4b0cf1e63b8d47d7b365e1c0` |
| `mmbench_power_v3.py` | `97a7a24079781992787d3cfee94ee2410e58433a88835d2d008f065894bd8843` |
| `passcheck.py` | `c8bff2e97fd67666a4a2a62669e4a115785dad69e1cd67a6c49cc2eb1b0a2417` |
| `reduce.py` | `8a06491ab737ed56b15f2b565c24806836df844d7eee737a47666aba9d9b6e01` |
| `x1_reduce.py` | `aacac4a2fc353660ffaf00e8344e8bcfa41473db7b80cbb64c15a26550ccd24d` |
| `block.sh` | `67703299e51e25ed993936f18a81149266163378ab80ad6535d39a4d5d808345` |

### A2.abla

**V3-ABL-A on four cards (25 Sep 2026, before any data from aifoundry1's cards).** The owner asked for every
measurement to be repeated on every card after the day's machine fixes, so V3-ABL-A also runs on aifoundry1's two
cards (aifoundry1-c0, firmware 1.4.1; aifoundry1-c1, firmware 1.2.0). Nothing registered for aifoundry2 and aifoundry3
changes: their REGISTERED outcome is computed from their data exactly as before, with the registered clock rule
(checked: the new reducer's registered output is identical to the old one on every synthetic and legacy test set, and
on aifoundry2's real passes collected so far).
What is added, decided before any aifoundry1 data exists:

1. *Parameters.* aifoundry1's cards are governor-free with aifoundry2's configuration (TDP 65 W, threshold 65 C), so
   they take aifoundry2's protocol and reduction: heat to 84 C, launch when the die reads 80 C, 45 min block cap,
   leakage slope 0.81 W/C at 80.9 C (their own slopes are unmeasured; the slope multiplies only the few degrees the die
   rises by seconds 1-3). Four passes per card, replacements from pass 5 as registered. The blocks select these by
   governor (lib.sh `GOV_FREE`) and a per-card leak table, not by host name.
2. *Clock rule for the all-cards outcome.* aifoundry1-c0's firmware idles in a low-power state at 300 MHz / 398 mV
   after a long idle, but stayed at 600 MHz (26 W) after a launch in the 25 Sep clock test, so its pre-launch idle
   bracket may be in either state, and may differ from run to run. The registered rule ("any sample in [t0-2 s, t1]
   off 600 MHz") covers that bracket, so it would drop every run whose bracket is in the low-power state. The
   all-cards outcome therefore uses, on every card, the busy rule: the clock test covers the samples the busy metrics
   read, [t0+0.3 s, t1]; the idle bracket's clock, voltage and power are recorded (telemetry, and starts.jsonl
   `idle_mhz` / `idle_mv`), not tested. Where the busy rule changes aifoundry2's or aifoundry3's outcome, the output
   says so. A burst that itself runs off 600 MHz (the clock test's first launch after the low-power idle reached
   600 MHz only at its end) is dropped by the busy rule; if that happens to aifoundry1-c0's bursts generally, its items
   are INSUFFICIENT, and no other operating point, launch temperature or wake-up launch is substituted after the data
   are seen.
3. *All-cards outcome.* Each item gains `all_cards`: PASS if it holds on every card on which it is tested, FAIL if on
   none, CARD-DIFFERENT if on some, INSUFFICIENT if a card lacks 3 kept repeats or has no data. Tested on aifoundry1's
   cards: ABL-T1, ABL-T5's fp32/int8 ratio (registered "on each card"), the T5 EM4 rider (switching > 0 per card),
   ABL-T7, ABL-EM4c. REPORTED on aifoundry1's cards, not tested, because their bands are given for aifoundry2 or
   aifoundry3 only: ABL-T2, T3, T4, T5's pJ-per-MAC bands, T6, T8 (each shown against both registered cards' values)
   and ABL-R (decided on aifoundry3; each card's fit stated). ABL-EM4d stays aifoundry2 only.
4. *Idle state.* Items about energy over idle carry each card's idle clock, voltage and idle power by state. On a
   card whose idle bracket sits below the burst's operating point, differences between configurations (T1, T2, T3,
   T8) cancel the idle state only between runs that idled in the same state, while absolute over-idle values (T4, T5,
   the EM4 rider, T6, T7) include the step between idling at 600 MHz and idling at 300 MHz. If a card's runs idled in
   more than one state, differences carry the step too; the output then flags the card (`idle_mixed_on`) and reports,
   beside the outcome and without changing it, the item on each idle state's runs alone (`by_idle_state`). The firmware
   releases also idle at different powers at 600 MHz (26 W on 1.4.1, 33-35 W on 1.2.0, 32 W on 1.3.1), so every
   card's idle power is stated with its over-idle values. The all-cards outcome is computed as stated; wherever
   aifoundry1-c0 fails such an item with its idle state off 600 MHz or mixed, the page says that its idle state
   differs, and gives its values as over its own idle state.
5. *Card checks on aifoundry1.* The et_soc1 use count counts both cards of the host, and the other card's queue holds
   its own card, so the runner does not use it there: "the card is held" means another user's device process or CI
   job, or one of our own device processes that can open this card (ET_DEVICES unset or this card, and any
   dev_mngt_service, which ignores ET_DEVICES and opens every card), other than this block's sampler.

### A2.ablb

**V3-ABL-B on four cards (25 Sep 2026, before any data from aifoundry1's cards).** V3-ABL-B also runs on aifoundry1's
two cards. The REGISTERED outcome of every item is computed from aifoundry2 and aifoundry3 exactly as before (checked:
identical output, also on aifoundry2's real passes so far). Added, before any aifoundry1 data exists, with the
parameters, clock rule, idle-clock record and card checks of the V3-ABL-A four-card amendment (aifoundry1's cards: heat
to 84 C, launch at 80 C, 35 min cap, leakage slope 0.81 W/C at 80.9 C; three passes per card, replacements from pass
4; the busy clock rule [t0+0.3 s, t1] for the all-cards outcome):

1. *All-cards outcome* (PASS on every tested card, FAIL on none, CARD-DIFFERENT on some, INSUFFICIENT if a card lacks
   3 kept blocks or has no data). Tested on aifoundry1's cards, as registered "on each card": ABLB-2a (every band; the
   clause "identical on the two cards within 0.5 cycle" becomes: the spread of all tested cards' TenB int8 means is
   <= 0.5 cycle), 2b (paired TenB - L1; the kernel clause per card when V3-MMB's values for that card are given),
   3ab (saving 0.80-0.92), 3d (ratio 0.7-1.5), 3f, 3g. REPORTED, not tested, because the band is given per registered
   card: 2c (9.5-10.5 W / 0.92 x aifoundry2), 3c (slope bands), 3e (uJ per layer, stated with the ratio to
   aifoundry3; its joint aifoundry2/aifoundry3 check stays as registered and never gives CARD-DIFFERENT).
2. *Idle state.* Items about energy over idle carry each card's idle clock, voltage and idle power by state. When
   aifoundry1-c0's idle bracket is in its low-power state (300 MHz / 398 mV; after a launch it may instead idle at
   600 MHz, so the state can differ from run to run), paired differences (2b, 3c's slope, 3d, 3f, 3g) cancel it only
   between runs that idled in the same state, while absolute over-idle values (2c, 3ab's dense and zero watts and so
   its saving, 3e) include the step between idling at 600 MHz and at 300 MHz. If a card's runs idled in more than one
   state, the output flags it (`idle_mixed_on`) and reports the item on each state's runs alone (`by_idle_state`),
   without changing the outcome. The all-cards outcome is computed as stated; wherever aifoundry1-c0 fails such an
   item with its idle state off 600 MHz or mixed, the page says that its idle state differs.

### A2.x5

**V3-X5 on four cards (25 Sep 2026, before any data from aifoundry1's cards).** V3-X5 also runs on aifoundry1's two
cards. The REGISTERED outcome and verdict stay those of aifoundry2 and aifoundry3, computed exactly as before (checked:
identical output, also on aifoundry2's real passes so far). Added, before any aifoundry1 data exists, with the clock
rule, idle-clock record and card checks of the V3-ABL-A four-card amendment:

1. *Parameters.* aifoundry1's cards are governor-free with aifoundry2's configuration, so they use aifoundry2's arms:
   hot 83 C launch / 86 C preheat, cool 76 / 79 C (both above aifoundry2's governor window; aifoundry1's windows
   are unmeasured), 20 / 20 min caps, reduced at 83.9 / 76.9 C with leakage slope 0.81 W/C. Three passes per card
   (hot, cool), replacements from pass 4.
2. *All-cards outcome.* The card hypothesis is registered for each card (hot - cool switching inside +-0.5 W for fp32
   uniform and randn, Welch 99.75%), so it is tested on every card with the busy clock rule: PASS = card property on
   every card, CARD-DIFFERENT = on some (named), FAIL = on none, INSUFFICIENT = a card lacks 3 kept runs per pattern and
   arm or has no data. The temperature-effect reading is registered on aifoundry3; it is reported for every card,
   not tested.
3. *aifoundry1-c0's idle state.* Its idle bracket may be at 300 MHz / 398 mV (after a long idle) or at 600 MHz
   (after a launch), while the burst runs at 600 MHz. With the bracket at 300 MHz, switching subtracts an idle power
   that follows the low-power state's leakage slope, while the burst's power follows the 600 MHz slope, so hot - cool
   carries (busy slope - idle slope) x 7 C besides any change in switching; if the arms' runs idled in different
   states, it also carries the step between the states' idle powers. Its result is computed and counted as stated,
   with the idle note (and, when the states are mixed, the hypothesis on each state's runs alone, reported); when
   aifoundry1-c0's idle state is off 600 MHz or mixed, the pages must say that on this card the design does not
   separate card from temperature, whatever the interval shows, and must not read a positive hot - cool there as a
   temperature effect.

### A2.tel

**TEL-4C (25 Sep 2026, before any aifoundry1 data and before the four-card V3-TEL passes): V3-TEL on four cards.**
The owner asked for every measurement to be re-run on every card after the day's machine fixes. V3-TEL therefore runs
three passes on each of aifoundry2, aifoundry3, aifoundry1-c0 and aifoundry1-c1. aifoundry1-c0 runs firmware 1.4.1
and idles in a 300 MHz / 398 mV `low_power` state. aifoundry1-c1 runs firmware 1.2.0 and idles at 600 MHz / 499 mV.
Both have TDP 65 W and a 65 C threshold, as aifoundry2 has. Implemented in `tools/claims-v3/tel/` (README "Four
cards").

1. **The registered outcomes do not change.** Every item's registered outcome is computed from aifoundry2 and
   aifoundry3 only, with the registered rules. The reducer gives identical registered outcomes, readings and
   aifoundry2/aifoundry3 values on every earlier synthetic set and on the real aifoundry2 passes 1-3 of 25 Sep (alone,
   and copied under all four card names).
   - **The one change to aifoundry2's and aifoundry3's procedure:** every pass now reads the idle clock (`ettelem
     config`: power state, minion MHz and mV, about 0.1 s) six times, between segments: at the start of phase 1 (after
     `loglevel info`, before `sptrace gov/sp0.bin` and the five launches), before the arms, after the arms, before the
     reset segment, before the DEBUG block's `loglevel debug`, and at the end. None falls inside an arm, a quiet
     segment, the reset log or the DEBUG block, and `sp1.bin` is still read after the launches and before phase 1's own
     config query. Their other device calls, arm orders and seeds are unchanged (dry runs compared with the 25 Sep dry
     runs, and the code diff against the block that ran aifoundry2's passes 1-3). No registered rule reads these
     records.
2. **The all-cards outcome.** A new outcome per item covers every card the item tests: PASS if the item holds on every
   card, CARD-DIFFERENT if it holds on some, FAIL if it holds on none, INSUFFICIENT if a tested card has fewer than 3
   kept passes. An expected card with no data counts as INSUFFICIENT.
   - **Tested on all four cards:** TEL-P6, TEL-P7, TEL-S's decision (P_H - P_L > 0), TEL-Q's Q1 (the Temp and MEM
     parts), Q2, Q4 and Q5 (minion "now"), and TEL-R's R1-R6. TEL-Q also needs Q3 (|r| < 0.45) for every pair of
     cards.
   - **Reported for aifoundry1's cards, not tested,** because their registered values name aifoundry2 or aifoundry3:
     TEL-P1-P4, TEL-P5, TEL-G, the S1/S2 bands, Q1's 34-line parse and Q5's SRAM gradient. For TEL-P1-P5 and TEL-G
     the all-cards outcome therefore equals the registered one (TEL-G keeps its same-firmware rule).
3. **aifoundry1's cards take aifoundry2's governor-free values.** They heat to 76 C before the arms, the reset segment
   and the DEBUG block, and take governor readouts only on a die at or above 68 C. The other differences:
   - Arm-order seeds are 1001-1003 (card 0) and 1101-1103 (card 1).
   - `dev_mngt_service -n` is the card's index (it ignores ET_DEVICES), and etcfg reads `/dev/et<index>_mgmt`.
   - Before any SPST work, the firmware must read 1.4.1 on card 0 and 1.2.0 on card 1, or the pass aborts.
   - The reset log runs 20 s after the last burst instead of 12 s.
   - Before the reset segment and the DEBUG block, a card whose idle clock reads off 600 MHz gets up to two 2 s heater
     launches (card 0's first launch after a low-power idle drew no power until its end).
   - Because `dev_mngt_service` opens both cards' management nodes, a TEL pass on aifoundry1 takes the whole host. It
     holds a host lock, waits (at most 45 min) for the other card's running block to end, then keeps a marker process
     that stops the other card's queue until the pass ends. The other card's schedule is delayed by that much. No
     running block is interrupted: a block that the other queue started at the same moment exits 3 at its own start
     check, or runs to its end while the TEL pass waits, and the queue retries it.
   - The idle clock is read at the same six points as on the other cards (item 1).
   - aifoundry1-c1 showed no clock boost at 57-62 C on 25 Sep, so its heating may be unnecessary; it keeps
     aifoundry2's values anyway, so that the governor-free cards are treated alike.
4. **Clock rules.** aifoundry2 keeps its registered rule, and aifoundry3 has none. aifoundry2's rule also drops an idle
   E arm or a whole X3 window (idle part included) with any sample off 600 MHz; it stays, in its all-cards status too,
   because changing it would change the registered outcome (aifoundry2 idled at 600 MHz in all three 25 Sep passes).
   On aifoundry1's cards only busy samples are dropped: a burst or X3 load window is dropped when a sample from 500 ms
   after its start to its end reads off 600 MHz. Idle arms, idle brackets and the idle window are never dropped for
   their clock. The 500 ms allows for the clock rising after the minions start. The X2 launch-clock check (0.59-0.61
   GHz) applies as on aifoundry2.
5. **The physics on aifoundry1's cards.**
   - **P6.** The late windows start 8 s after the last idle-clock change following the last burst, if there is one. A
     pass with no such window cannot decide P6.
   - **Q4 and R6.** These compare load captures with the idle capture. They are reported, not tested, on a pass whose
     DEBUG-block idle clock (the last reading, after any wake) is off 600 MHz, since the two captures are then at
     different operating points. If no pass qualifies, the card is decided without them.
   - **P7.** P7 stays as registered. Its reading names each card's idle clock, because a card whose idle state differs
     before and after a burst mixes the set-point step into f(1 s).

### A2.wire

**A-WIRE-4 (25 Sep 2026, before any data of aifoundry1's cards): V3-WIRE on four cards.** After the machine fixes
of 25 Sep the owner asked for every measurement to be re-run on every card, so V3-WIRE runs its 6 passes (28
configurations, WIRE-FILL's 12 dump launches in pass 1) on aifoundry2, aifoundry3, aifoundry1-c0 (firmware 1.4.1) and
aifoundry1-c1 (firmware 1.2.0), aifoundry1's cards selected with `V3_DEVICE=0|1`. `tools/claims-v3/wire/` (README.md,
section "Four cards").

1. *The registered outcome is unchanged.* Each item's `outcome`, `registered_verdict` and `reading` come from
   aifoundry2 and aifoundry3 only, with the registered drop rules and statistics. Checked before any campaign data:
   every field of the previous reducer's output is present and equal in the new one (outcomes, `cards`, and every
   item's outcome, verdict, reading, test and aifoundry2/aifoundry3 values) on the passes collected on 25 Sep
   (aifoundry2 p1-p5, aifoundry3 p1), on the E32 split, on review sets A-F and on the four-card synthetic sets. The
   only differences are added fields.
2. *The campaign re-runs every pass.* 6 new passes on every card. The passes of 25 Sep collected before the fixes
   (aifoundry2 p1-p5, aifoundry3 p1) are moved out of `DATA_ROOT` before the campaign starts, because `block_begin`
   would skip a pass whose `block.json` exists, and they do not enter either outcome.
3. *A four-card outcome is added* (`all_cards`). Each card gets the registered per-card test: holds, sign (null
   excluded, mean outside the range), fails, or insufficient with fewer than 3 kept passes.
   - PASS if the item holds on every card, CARD-DIFFERENT if on some, FAIL if on none, INSUFFICIENT if any card, a
     missing one included, lacks 3 kept passes.
   - A "sign" card does not hold: four "sign" cards give FAIL here, where the registered two-card rule says SIGN-ONLY.
     The reading lists the sign cards, and `null_excluded` says whether every sufficient card excludes the null on
     the same side.
   - `over_sufficient` gives the same words over the cards that do have 3 kept passes.
   - aifoundry2's and aifoundry3's values are their registered ones, so each card has one set of values.
4. *Every item is tested on aifoundry1's cards and none is only reported.* No WIRE band is specific to one card:
   P1-P16 were registered "per card" with one range, and WIRE-FILL "on each card".
5. *Parameters for aifoundry1's cards.* Both cards are governor-free (TDP 65 W, temperature threshold 65 C), so they
   take aifoundry2's values: `heat_to 76` before each pass, a 2 s heater before a configuration whose die is below
   69 C, and R-clock. The leakage correction of `analyze_wire` (aifoundry2's idle-law fit, which the plan already
   applies to both registered cards) is unchanged. The shuffle seeds are 51 + p - 1 for c0 and 61 + p - 1 for c1.
6. *Drop rules.*
   - aifoundry1's cards: aifoundry1-c0 idles in a "low_power" state at 300 MHz / 398 mV between kernels, so a sample
     off 600 MHz drops a burst only when it lies in the burst's busy window (first launch + 0.5 s to the last
     launch's end). An idle bracket never drops a burst. The starved-sampler and too-few-samples rules are unchanged.
   - Ramp allowance: a burst whose idle bracket before it sat below 600 MHz starts with the governor's ramp, so its
     first launch's implied clock may go down to 0.585 GHz, a ramp of at most ~20 ms at 300 MHz. Every later launch,
     and every launch of a burst that starts from 600 MHz, keeps 0.595-0.605 GHz. The 0.585 GHz floor is chosen
     without any measurement of c0's ramp.
   - aifoundry2 and aifoundry3 keep the registered rule in both outcomes: a sample off 600 MHz in an idle bracket
     still drops a burst there, since that rule is what the registered outcome is. The reducer reports, per card,
     how many bursts that rule dropped for an idle-bracket clock alone (`bursts_dropped_only_for_idle_clock`; 0 on
     the five aifoundry2 passes of 25 Sep). The end-of-block note counts the same.
   - Decided now, whatever the data show. If c0 is slower to ramp than 0.585 GHz allows, or returns to 300 MHz
     between the launches of one burst, its bursts are dropped by R-clock. If its governor holds a point below
     600 MHz under load on a die above 65 C, its busy samples leave 600 MHz and its bursts are dropped. In either
     case c0 comes out INSUFFICIENT and the bands are not widened after seeing pass data. `V3_DEVICE=0 ... block.sh 1
     --smoke` shows the first-launch and busy clocks before the campaign; any change after the smoke would be a
     further amendment, made before c0's first pass.
7. *Idle state recorded and read.* The block records the sampler's line just before every burst
   (`idle_state.jsonl`). The reduction reports each card's idle minion and NoC clocks and voltages against its
   bursts'. On a card whose brackets sit at a different operating point from its bursts, the energy over idle
   includes the step between the two: board items see the minion rail's step, and mesh-rail items see a NoC step
   only if the NoC's idle clock differs. This step is a constant power, which enters a per-byte value as
   step x wall/bytes:
   - It cancels in P1, P3, P5a, P10 and P16, which difference the random-data and zeros configurations at the same
     hops and bandwidth.
   - It does not cancel in any other item, because the bandwidth falls with the hop distance.
8. *Expected before any data.* c0's step on board power is probably of the order of 10 W. It idles at 18.8 W against
   30-33 W on the cards that idle at 600 MHz; its own step has not been measured. That is as large as the wire bursts'
   own 2-17 W over idle, so c0 may well be CARD-DIFFERENT on board items whose statistic does not cancel the step
   (P4, P5b, P6b, P7d-f, P9, P11b; P13 is descriptive). In a synthetic check with a 10 W board step (and a 1 W NoC
   step), P4, P5b, P7d and P11b left their bands on c0 (and P2, P11a, P12, P14b on the mesh rail); the other
   non-cancelling items moved but stayed inside their bands. Such a difference, on c0 alone and in a non-cancelling
   item, cannot be told apart from its idle state. The page does not read it as a difference in the wire; it gives
   c0's value with its idle state, and each energy item's `idle_note` says whether its statistic cancels the step.
9. *WIRE-FILL four-card outcome.* On each card the item holds if every launch is complete and matching, fails on a
   mismatch, and is insufficient if a fill is short. The registered rule (any mismatch on aifoundry2 or aifoundry3
   FAILS) is unchanged.

### A2.rl

**A-RL (25 Sep 2026, before any V3-RL data from aifoundry1's cards): V3-RL on four cards.** After the 25 Sep machine
fixes the owner asked for every measurement on every card. V3-RL therefore also runs its 6 passes on aifoundry1's two
cards:
- `aifoundry1-c0`: firmware 1.4.1, TDP 65 W. After a long idle it rests in a "low_power" state at 300 MHz / 398 mV
  (18.8 W board).
- `aifoundry1-c1`: firmware 1.2.0, TDP 65 W. It idles at 600 MHz / 499 mV (32.9 W).

Code: `tools/claims-v3/rl/{block.sh,quality.py,reduce.py,README.md}` ("Four cards").

1. **The registered outcomes do not change.** Every item's `outcome` is still computed from aifoundry2 and
   aifoundry3 alone, with the registered rules. The reducer before and after this change gives identical registered
   items (outcome, reading, prediction_held, kept passes, dropped bursts) in three checks:
   - on the real 25 Sep passes (aifoundry2 p1-p5, aifoundry3 p1-p2);
   - on the same with aifoundry1 card directories added beside them;
   - on every earlier synthetic test set.
2. **Heat: aifoundry1's cards take aifoundry2's 76 C** before each half and the relay, with `lib.sh`'s heater
   (build/sparsity).
   - Their governor inputs match aifoundry2's: TDP 65 W and software threshold 65 C (`ettelem config`).
   - The clock reason to heat is shown only for aifoundry2: its firmware 1.3.1 lifts the clock off 600 MHz below
     about 68 C. The 25 Sep clock test on aifoundry1 (two 2 s launches per card) saw no boost on card 1 at 57-62 C,
     and card 0 went from 300 MHz up to 600 MHz and no higher.
   - The heat is kept on both cards anyway, for three reasons: it guards against a boost that two launches cannot
     rule out; it puts every governor-free die at aifoundry2's temperature, which the card comparisons and the
     leakage correction assume; and on card 0 the heater's launches wake the card from its low-power state before
     each half.
   - The leakage correction keeps its registered constant (23.3 W at 80 C, T_L 36 C). aifoundry1's cards have no
     measurement of their own.
3. **The 600 MHz rules count busy samples only on aifoundry1's cards.** A busy sample is one inside a burst's window
   as `reduce_dir` takes it: [first run start + 0.5 s, last run end]. One exception: when two launches of a burst are
   more than 50 ms apart, the samples from one launch's end to 50 ms after the next one's start are launch gaps, not
   busy samples.
   - Only the relay has such gaps: it runs separate processes, 190 ms apart on aifoundry2 and 230 ms on aifoundry3
     on 25 Sep.
   - The 50 ms covers launch latency only (onchip_host stamps `t_start_ms` just before the launch). So a kernel that
     runs below 600 MHz is caught, not excused.
   - The rules on these cards:
     - a pass with any busy sample off 600 MHz is dropped and re-run (PLAN3's common rule, restricted to busy
       samples);
     - a burst with more than 2% of its busy samples off 600 MHz is dropped (the V3-RL burst rule, restricted the
       same way);
     - idle brackets and launch gaps never drop anything, so a 300 MHz idle on card 0 cannot drop a burst or a pass.
       Their clock is recorded.
   - aifoundry2 is also governor-free, but it keeps its registered "any sample" rule. Its heated die idles at
     600 MHz (0 of 23,575 samples off 600 MHz in its five 25 Sep passes), and changing the rule would change its
     registered outcome. aifoundry3 keeps its burst rule over the burst and its idle brackets. aifoundry2's
     `all_cards` values use its registered rule too, so its kept passes are the same in both outcomes.
4. **Two outcomes are fixed now for aifoundry1's cards.**
   - Card 0 waking from low power: in the clock test, card 0's first launch after a low-power idle showed no power
     rise, and the card reached 600 MHz only at the end of it (about 4 s). Afterwards it idled at 600 MHz (26 W) and
     did not drop back within the test. If it still falls back to low power in a 10 s idle gap or a relay launch
     gap, its next burst starts below 600 MHz. The busy rule then fails the pass, which is re-run.
   - A hot die held below 600 MHz: if firmware 1.4.1 or 1.2.0 holds bursts on a hot die below 600 MHz, the busy
     rule fails those passes too.
   - Either way, if it happens in every pass, that card's items stay INSUFFICIENT. The rule is not changed after the
     data. Read the smoke's and the first pass's `quality-windows.json` (the busy, gap and bracket clock
     histograms) and `state.jsonl` before the rest of the queue.
5. **The idle state is reported, not corrected.** Every V3-RL value is energy over idle.
   - On a card whose idle brackets are at 300 MHz, the over-idle values include the step from that state up to
     600 MHz.
   - Even at 600 MHz the three firmware releases idle differently: 26 W (1.4.1), 33-35 W (1.2.0) and 32 W (1.3.1)
     in the 25 Sep clock test.
   - So an absolute over-idle value (W or pJ/B) that comes out CARD-DIFFERENT on aifoundry1's cards may reflect what
     the firmware does at idle rather than the workload. The page does not read it as a silicon difference.
   - A difference of two bursts on the same card largely cancels the step: spin - ring, the c4 rows,
     L2 - scratchpad, random - zeros.
   - Each item carries every card's idle clock (`idle_clock_mhz`), plus an `idle_note` when a card's idle brackets
     are not at 600 MHz. The page says so wherever that card appears.
   - Each pass on every card records `ettelem config` (power state, clock and voltage) at its start and end in
     `state.jsonl`, and each window's clock and voltage in `quality-windows.json`. These reads are new on aifoundry2
     and aifoundry3 as well. They are read-only, run under `hold10` outside every sampler window, and change no
     value.
6. **A second outcome, `all_cards`, over aifoundry1-c0, aifoundry1-c1, aifoundry2 and aifoundry3.** A card with
   fewer than 3 kept repeats makes the outcome INSUFFICIENT; the verdict over the other cards is given for
   information. `per_card` holds all four cards' values.
   - **Items tested on each card:** PASS if the item holds on every card, CARD-DIFFERENT if on some, FAIL if on
     none. These are RL-f, RL-h part 1, RL-X3 (a), (d) and (e), and RL-X4 (under its registered side/overlap rule).
     Bands registered for both cards apply to every card.
   - **Items that compare the cards:** the registered Welch comparison over every pair of cards, each pair at
     1 - 0.01/pairs (Bonferroni). If any pair differs, the outcome is CARD-DIFFERENT with per-card values; otherwise
     PASS with the pooled value. These are RL-a, RL-d (both parts), and RL-g L1 and own scratchpad.
   - **RL-h part 2** uses the same pairwise comparison. PASS also needs every pairwise difference within
     +-0.1 pJ/B; if no pair differs but some difference is outside +-0.1, the outcome is FAIL.
   - **RL-g L2 - scratchpad** uses the same pairwise comparison. When no pair differs, each card's interval is
     checked against 0, as registered.
   - **Values registered for one card only** are reported for aifoundry1's cards, not tested: the RL-a, RL-d and
     RL-g per-card bands, and the a3/a2 ratio.
   - **Items decided on one named card** stay decided there, with the other cards reported: RL-b on aifoundry2 and
     RL-c on aifoundry3.
7. **Inputs from the other experiments for aifoundry1's cards.**
   - RL-f's low edge comes from the card's own full catalogue (V3-CATFULL), passed as `--low-edge`. Each value is
     0.5 x (l1fill/stride32/zeros + tstore/scp/zeros) for one catalogue pass, as for 23 Sep, and at least two
     passes are needed. aifoundry2 and aifoundry3 keep the 23 Sep catalogue.
   - RL-X4's FLOP side comes from the card's V3-ABL-A blocks, under its id in `--flop`. Its byte side is the V3-RL
     passes alone, since these cards have no 23 Sep passes.
   - Without these inputs, the card is INSUFFICIENT for that item.
8. **Scheduling.** The two aifoundry1 queues may run at the same time in one chassis. Every burst is bracketed by its
   own idle, so slow thermal coupling between the cards mostly cancels. PLAN3's >= 30 minutes between passes applies
   to each card.

### A2.idle

**A2, V3-IDLE on four cards (25 Sep 2026, before any V3-IDLE data of aifoundry1's cards).** On the owner's request
to re-run every measurement on every card after the day's machine fixes, V3-IDLE runs on aifoundry2, aifoundry3,
aifoundry1-c0 and aifoundry1-c1 (aifoundry1's two cards, selected with `V3_DEVICE=0|1`). What changes, decided before
any of their data:

- *Blocks.* aifoundry1's cards take aifoundry2's governor-free values: heat to 88 C (at most 150 bursts or 900 s), and
  5400 s of cooling in an IDLE-LONG pass. Both cards are governor-free at TDP 65 W like aifoundry2, and their
  heatsinks are not characterised, so the longer cooling is kept. Their heater is lib's HEATER there, `build/sparsity`
  (as on aifoundry3; aifoundry2 uses `build/sparsity_t2`, built from the same sources), with the same arguments.
  aifoundry3 is unchanged (target 90 C, which it does not reach, and 2700 s). Each pass also records the card's idle
  state: the minion clock and on-die minion voltage of the sampler's line before heating (`cycle_start`) and at the
  end of the cooling (`cool_end`), and the clock histogram of the cooling window (`check.json`). On aifoundry1 the
  `et_soc1` use count is not checked, because the module serves both cards and the other card's queue may hold its own
  card. The intrusion check is per card instead: another user's device process or a CI job counts whatever card it
  uses, and so do our own processes on this card or with no `ET_DEVICES`, and `dev_mngt_service` (which opens every
  card). Our own processes on the other card do not count; the polls that saw one are recorded (`other_card_polls`).
  Without the use count, a process that opens the card under a name the check does not know (for example a Python
  program on the runtime library) is not seen on aifoundry1 during the cycle; on aifoundry2 and aifoundry3 the use
  count still catches it.
- *Sample rule.* aifoundry2 keeps its registered rule (samples off 600 MHz dropped), and aifoundry3 keeps its own
  (pinned at 600 MHz: off-600 samples counted, not dropped). On aifoundry1's cards rules A, K and F keep the samples
  at the card's idle clock and drop the others. The expected clock is 600 MHz on both. aifoundry1-c1 (firmware 1.2.0)
  idles at 600 MHz / 499 mV, as aifoundry2 does. aifoundry1-c0 (firmware 1.4.1) rests in "low_power" at 300 MHz / 398
  mV, but in the 25 Sep clock test it moved to 600 MHz during its first launch and stayed there, idle, afterwards; its
  cooling after the heater is therefore expected at 600 MHz. If fewer than half of a card's cooling samples (the
  rule-A window, pooled over its kept cycles) are at the expected clock, the card's most common cooling clock is used
  instead (for example 300 MHz if c0 falls back into low_power), so a card's idle samples are never all dropped for
  being at its own idle clock. The idle-clock note and the item's `reading_all_cards` then name the fallback, and the
  block's pass check warns. The heater bursts are never measured in V3-IDLE, because every launch window (1 s before
  to 6 s after) is dropped, so no rule on busy samples applies.
- *Reduction.* The registered outcome of every item is computed exactly as before, from aifoundry2 and aifoundry3
  only. Every IDLE item's band is a value given for aifoundry2 (b, c, d, k; L's T_L, A80 and slope at 80 C) or for
  aifoundry3 (0, a, e, f; L's slope at 56 C and offset). So aifoundry1's cards are **reported, not tested**. Their
  per-card values are computed exactly as for the registered card, with an informational flag saying whether that
  card's band would hold. The added `all_cards` outcome is taken over the tested cards with enough kept repeats: PASS
  if the item holds on every card, CARD-DIFFERENT if on some, FAIL if on none, INSUFFICIENT if a tested card lacks
  repeats. For V3-IDLE that makes it equal to the registered outcome. Every item carries each card's idle clock,
  minion voltage and firmware. aifoundry1's cards run other firmware (1.4.1, 1.2.0) than aifoundry2 and aifoundry3
  (1.3.1), and in the clock test the three releases idled at different power at the same 600 MHz (26, 33-35 and 32 W),
  so aifoundry1's idle values are stated per card. A card idling off 600 MHz (aifoundry1-c0, if it cools in low_power)
  is at another operating point than the law and the other cards, so its residual to the law is not comparable, and
  the page says so.
- *Schedule.* On each aifoundry1 card: `idle 1`, `idle 2` and `idle 3`, >= 30 min apart and on at least two days.
  `idle 11-13` are optional and run overnight from a schedule of their own. Each card's `idle 1 --smoke` runs first
  (sampler, heater, idle-state fields). The first short pass's heating (`heat.jsonl`, `heat_end`) is then checked
  before the rest, because no one knows how firmware 1.4.1 and 1.2.0 behave near 88 C; the 150-burst / 900 s cap
  bounds it in any case.

Code: `tools/claims-v3/idle/block.sh`, `reduce.py`, and `README.md` ("Four cards").

### A2.cat

**V3-CAT on four cards (25 Sep 2026, before any V3-CAT data from aifoundry1).** The owner asked for every measurement
to be re-run on every card, so the next campaign runs V3-CAT on aifoundry2, aifoundry3, aifoundry1-c0 and
aifoundry1-c1 (aifoundry1's two cards are selected with `V3_DEVICE=0|1`, which sets `ET_DEVICES`). What was known of
aifoundry1's cards when this was written: their `ettelem config` reads (25 Sep 15:2x) and a two-launch clock test
(16:40); no catalogue burst had been run on either. Code: `tools/claims-v3/cat/` (block.sh, catlib.py, reduce.py,
run_catalogue_t10.py; README "Four cards").

- *Registered outcome unchanged.* Every item's registered outcome is still computed from aifoundry2 and aifoundry3 only,
  with their registered designs and drop rules. The reducer's registered fields (outcome, reading, test, the per-card
  values of aifoundry2 and aifoundry3, committed_23sep) are identical to the previous code's on the 23 Sep legacy
  data, on the real 25 Sep aifoundry2 passes (p1-p10, alone and with a stand-in aifoundry3), and on every earlier
  synthetic set; the pass listings only gain fields (each dropped burst's `idle_state`).
- *Design on aifoundry1's cards.* Both cards are governor-free (static TDP 65 W, temperature threshold 65 C, as
  aifoundry2; their firmware releases, 1.4.1 on card 0 and 1.2.0 on card 1, differ from aifoundry2's 1.3.1, so
  whether they hold 600 MHz under load is decided per burst by the drop rules), so they run aifoundry2's registered
  design unchanged: 11 blocks per card (arm A: 4 warm W, 4 hot H; arm B: 3), W passes start at <= 82 C after
  heating to >= 76 C, H passes hold 88 C, arm B starts after heating to >= 76 C, with the same seeds. The heater is `build/sparsity/host/sparsity_host`, as on aifoundry3. The leakage
  correction is analyze_catalogue.py's own: the idle law fitted on aifoundry2 (A80 = 23.3 W, T_L = 36 C), applied
  unchanged to every card as the 23 Sep catalogue applied it to aifoundry3, and not refitted per card. It corrects
  only the busy-minus-idle temperature difference of a 3 s burst, a few percent of the burst's power.
- *Drop rules on aifoundry1's cards.* A burst is dropped when any of its busy samples is off 600 MHz, or when a launch's
  implied clock (cycles_max / wall_s) is outside 0.595-0.605 GHz. Idle-bracket samples never cause a drop there, at
  any clock. Card 0 (firmware 1.4.1) was read idle in its "low_power" state at 300 MHz / 398 mV before any launch, so
  aifoundry2's idle-bracket rule could drop every burst on it. The rule is also not applied to brackets above 600 MHz,
  which aifoundry2 does drop (R-clock): such an idle is 5-9 W higher and lowers that burst's over-idle power, so their
  number is reported per card. Instead, each burst records the clock of its idle brackets (`idle_state`), and each
  block records the card's power state, clock and voltage at its start (`ettelem config`, read-only). aifoundry2
  keeps its registered idle-bracket rule (R-clock), and aifoundry3 still has no clock rule.
- *Added four-card outcome (`all_cards`).* For each item, the per-card rule is applied to every campaign card. The
  outcome is PASS if the item holds on every card, CARD-DIFFERENT if it holds on some, FAIL if it holds on none, and
  INSUFFICIENT if a card has fewer than 3 kept repeats or no data (the outcome over the cards that do have data is
  given beside it).
  - These apply unchanged to aifoundry1's cards: CAT-a (per card; the cool condition on a governor-free card is W,
    as on aifoundry2), CAT-c (per card; the dramrow2 bands registered for aifoundry3 remain reports on every card) and
    CAT-f ("on each card").
  - These are REPORTED on aifoundry1's cards, not tested: CAT-b, whose band 0.951 ± 0.015 is registered for cool
    aifoundry3 / warm aifoundry2 (each aifoundry1 card's W passes are reported against aifoundry2-W as a ratio with its
    99% interval), and CAT-e, whose band +3.2 ± 3 pJ/B is registered for aifoundry3 only (tstore - tload is reported
    per card). For these two items `all_cards` equals the registered outcome.
- *Idle state is stated, not corrected.* In the 16:40 test, card 0's idle stayed at 600 MHz (~26 W) after two launches.
  How long it stays there before going back to 300 MHz is not known, so its brackets may sit at 600 MHz, at 300 MHz or
  at both; this is measured, not assumed. Every item carries the clock of each card's idle brackets and its settled
  idle board power per clock. Where a card's brackets are not at 600 MHz, its energies over idle include the step from
  that idle to the 600 MHz operating point. The page states this beside that card's values, and does not compare them
  with the other cards' as like for like. No correction for the step is applied. Because the step is roughly constant
  in watts, it adds a different pJ/B (or pJ/op) to configurations that run at different rates, and it dilutes
  CAT-a's hot/cool ratio. A tested card whose kept brackets in an item's passes are mostly (more than half) off
  600 MHz is still tested as registered for CAT-a, CAT-c and CAT-f, but the reducer lists it under
  `all_cards.idle_caveat`, and its holds / fails there is not read as evidence for or against the claim; the page
  says so. The outcome itself is not changed by this.
- *Stated in advance.*
  - Three arm-B passes is the minimum. If one burst of a CAT-c/e/f configuration is dropped, that card is INSUFFICIENT
    until the pass is re-run.
  - In the 16:40 test, card 0's first launch after its low-power idle drew no extra power, and the clock reached
    600 MHz only at the end of that launch. A burst that starts from that state, or any launch that runs partly below
    600 MHz, is expected to be dropped by the busy-sample or implied-clock rule. If every burst is dropped, the card is
    INSUFFICIENT; the rules are not relaxed. The card-0 smoke (`V3_DEVICE=0 bash tools/claims-v3/cat/block.sh 1
    --smoke`) is run and its check.json read first. It decides nothing, because its result does not change this
    design.
  - The two aifoundry1 cards may run their queues at the same time, so one card's heater can warm the other. Nothing is
    dropped for this, because each burst's die temperature is measured and CAT-a uses the measured dT.
  - The 88 C hold and the 76 C preheat are targets. If a card falls short, dT gets smaller and CAT-a's interval
    widens; beta is not biased. The die reading is minshire[0]; card 0's 123 C peak-hold value (minshire[2]) is not
    used.

### A2.catfull

**A? (number it on commit), V3-CATFULL: the energy manual's full catalogue on four cards (25 Sep 2026, before any
V3-CATFULL data).** The owner asked to re-run every measurement on every card after the day's machine fixes. So the
four-card campaign (aifoundry2, aifoundry3, aifoundry1-c0 and aifoundry1-c1, the last two selected with
`V3_DEVICE=0|1`) re-runs E27's whole catalogue. This experiment is not in PLAN3. Its rules are fixed here, before any
of its data, on every card.

- *What runs.* `workloads/enercat/run_catalogue.py`'s configurations, imported from the tree. That is 392 of its 394:
  the two `dramrow/stride256K` ones are left out. They ask for 2,048 slices of 8 MB each (16.4 GB of card DRAM, and
  the host fills the same 16 GB in its own memory first). On 23 Sep they printed no launch on either card, so the
  catalogue has no value for them. The `dramrow2` rows (E28, aifoundry2 only until now) are included. There are
  **3 passes per card**. A pass is the whole catalogue once, in the order `random.Random(40<K>).shuffle` gives, cut
  into three consecutive parts of 130-131 configurations. Part S of pass K is one block (`catfull KS`: 11 12 13 21 ...
  33). Each block runs V3-CAT's runner `tools/claims-v3/cat/run_catalogue_t10.py` with E27's timing: `--passes 1
  --burst 3 --gap 4.5 --seed 40<K><S>`, every device process under `timeout 10`, the host `build/enercat_v2`.
  `ettelem` samples at 10 Hz through lib.sh. A configuration whose burst printed no launch is run once more at the end
  of its block (at most 12). On aifoundry1 (`V3_DEVICE` set) lib.sh's management drain is never run: its
  `dev_mngt_service -n 0` ignores ET_DEVICES and would reach card 0 whichever card the block uses, while card 0's own
  queue may be sampling. A card whose management queue stays blocked fails its block instead.
- *Heating.* This follows the 23 Sep catalogue: a warm start, then no heater during the run. Governor-free cards
  (aifoundry2, aifoundry1-c0, aifoundry1-c1) are heated to >= 76 C before each block's sampler starts. This is lib.sh
  heat_to's loop and bound (2 s random fp32 matmul launches, at most 150). aifoundry1's two cards take aifoundry2's
  value: both report TDP 65 W and a 65 C threshold, as aifoundry2 does. aifoundry3 is pinned at 600 MHz and is not
  heated. A preheat that stops short is recorded, and the block runs anyway. The leakage correction is
  analyze_catalogue's, unchanged: aifoundry2's idle law (A80 23.257 W, T_L 36 C) on every card, as on 23 Sep. It is not
  refitted for aifoundry1's cards, since nothing measured there says otherwise.
- *Drop rules, busy samples only.* On a governor-free card, a burst is dropped when a busy sample (lo + 0.5 s .. hi,
  analyze_catalogue's busy window) is off 600 MHz. It is also dropped when a launch has an implied clock
  (cycles_max / wall_s) outside 0.595-0.605 GHz. The idle brackets are never tested, and a bracket's clock never drops
  a burst. aifoundry1-c0 (firmware 1.4.1) idles in its "low_power" state at 300 MHz / 398 mV between kernels, so a rule
  on its brackets would drop every burst. There is one exception to the launch rule. When the bracket before a burst is
  not all at 600 MHz, the burst's first launch is recorded but not tested, because it may carry the wake-up from
  that state. After a 600 MHz bracket every launch is tested; on 23 Sep every first launch read 0.598-0.600 GHz on both
  cards. A slow first launch lengthens the burst's wall time, which the reduction multiplies by the busy power, so it
  biases that card's values up by up to about an eighth of that launch's slowdown. Each card's lowest first-launch
  clock is reported. aifoundry3 has no clock rule. On every card, bursts that analyze_catalogue cannot cut are
  dropped. Slow-sampler bursts are kept, as E27 kept them. Each burst records the clock of the bracket before it,
  of both brackets together, and of its busy samples.
- *Difference from V3-CAT on aifoundry2.* V3-CAT keeps PLAN3's R-clock rule on aifoundry2, which also drops a burst
  with any idle-bracket sample off 600 MHz. The reason is that aifoundry2's governor lifts a cool idle to 700-800 MHz,
  5-9 W higher, and that enters the over-idle power. catfull does not drop on brackets on any card. Instead CF-GAP
  reports `sensitivity_idle600_only`: the registered test recomputed without the bursts whose brackets were not all at
  600 MHz, with the number left out per card. This is reported, never the outcome. With the preheat and the catalogue's
  own load, 23 Sep's aifoundry2 had every sample at 600 MHz for 2.6 h.
- *The idle state.* A card's idle is "at 600 MHz" when at least 90% of its kept bursts have every idle-bracket sample
  at 600 MHz. Otherwise its state is the most common bracket clock among the other bursts (expected: "300" on
  aifoundry1-c0). On a card whose idle is not at 600 MHz, the energy over idle includes the step from that idle state
  to the 600 MHz operating point. Its values are reported per card, with the reason, and left out
  of the headline pooled values (`pooled_600idle`). `pooled_all` (every card) and `pooled_registered` (aifoundry2 +
  aifoundry3) are given beside them. Every item that concerns energy over idle carries each card's idle state.
- *Items.* The unit is a pass. A pass counts when all three of its parts are used (block status ok, offclock or
  partial). Fewer than 3 such passes leaves a card INSUFFICIENT. The registered outcome is over aifoundry2 and
  aifoundry3, the committed catalogue's cards. `all_cards` is over the four cards: PASS if the item holds on every
  card, CARD-DIFFERENT if on some, FAIL if on none, INSUFFICIENT if a card lacks repeats or data. The outcome over the
  cards with repeats is given beside it.
  - **CF-GAP** (E27: aifoundry3 / aifoundry2 = 0.950 in the median over the catalogue). For each pass,
    g = 100 x median over configurations of ln(value / aifoundry2's mean for that configuration). The test is a Welch
    99% interval on aifoundry3 - aifoundry2, read as a ratio. PASS when that interval lies wholly below 1; otherwise
    FAIL. The claim names these two cards, so aifoundry1's cards are **reported, not tested**: their ratio to
    aifoundry2 is given with the same interval.
  - **CF-COVER** (E27: every configuration measured at 600 MHz, none failed). This applies to each card, unchanged on
    aifoundry1's: >= 3 complete passes, and every configuration kept in >= 3 passes after the drop rules.
  - **CF-REP** (E27: pass-to-pass standard error 1.9% / 6.1% on aifoundry2, 1.2% / 3.6% on aifoundry3): reported per
    card, with no test.
  - Values, not items: each configuration's mean, sd, se and n per card; the pooled values; every card's ratio to
    aifoundry2 and every pair of cards (the median and 10-90% over configurations); the committed 23 Sep values
    beside, never pooled.
- *Schedule.* On each card: `catfull 11` to `catfull 33`, after one smoke run by hand on that card (`bash
  tools/claims-v3/catfull/block.sh 1 --smoke`, with `V3_DEVICE=<n>` on aifoundry1; queue.sh passes a single argument,
  so the smoke cannot be a schedule line). Passes are
  >= 30 min apart, with other blocks between them; parts of one pass may run back to back. Card time is about 60 min
  per pass (55 on aifoundry3), so about 3 h per card.

Code: `tools/claims-v3/catfull/` (`block.sh`, `cflib.py`, `reduce.py`, `README.md`). Every block records the sha256 of
lib.sh, this directory, the runner, run_catalogue.py, analyze_catalogue.py and the enercat host.

## A3 (25 Sep 2026, before any data from aifoundry1's cards): the other-user check on aifoundry1

On aifoundry2 and aifoundry3 a block still does not start while any other user is logged in (the lab's rule). On
aifoundry1 another user has kept an idle session open since 18 September (a shell and a long-running interactive
program, no ET device process, no card held), so under that rule the machine could never be measured, which the owner
asked for. On a host with several cards a login alone therefore no longer blocks; using the cards does: a device node
held by another user (the machine's `et-who` helper lists every user's open nodes), another user's device process, a
running CI job, or the card's lock file (`/run/lock/etsoc-shire<N>.lock`, which every block holds). Blocks that re-check
during a run keep doing so and stop (exit 3) if another user takes a card. `tools/claims-v3/lib.sh` `others_present`.
