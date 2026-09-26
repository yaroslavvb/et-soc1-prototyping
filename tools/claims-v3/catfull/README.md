# V3-CATFULL: the energy manual's full catalogue on four cards

Not in PLAN3. The owner asked on 25 Sep 2026, after that day's machine fixes, to re-run all measurements on all
cards, so the four-card campaign (aifoundry1-c0, aifoundry1-c1, aifoundry2, aifoundry3) runs E27's whole catalogue
again, three passes per card. Its rules are the amendment "catfull" (text in the scratchpad
`validate3/fourcards/amendment-catfull.md`, for AMENDMENTS.md), committed before any of its data. Suggested
experiment number when run: E46.

| file | what |
|---|---|
| `block.sh` | one block = one third of a pass on the local card: `bash tools/claims-v3/catfull/block.sh <KS> [--smoke]` |
| `cflib.py` | the part plan (which configurations a block runs), the post-block check, burst cutting with the drop rules, statistics |
| `reduce.py` | per-card and pooled values for every configuration, card-to-card ratios, the items: `reduce.py --data <dir> --out verdicts.json` |

The runner is V3-CAT's `tools/claims-v3/cat/run_catalogue_t10.py`, reused unchanged (its sha256 goes into every
block's `code.sha256`); the configurations are `workloads/enercat/run_catalogue.py`'s `configs()`, imported from
the tree, and the reduction is `workloads/enercat/analyze_catalogue.py` (`bursts_of`, `summarise`, `wire_fit`,
`sram_leakage`, `rail_fall_curves`, `rail_filter`), imported unchanged.

## Blocks, passes and parts

`<KS>` = pass K, part S: the schedule lines are `catfull 11`, `catfull 12`, `catfull 13`, `catfull 21` ... `catfull 33`
(9 blocks per card). Passes 4-9 exist for extra or replacement passes. A pass is the whole catalogue once: the 392
configurations in the order `random.Random(40<K>).shuffle` gives, cut into three consecutive parts (131, 130, 131);
block KS runs part S through the runner with `--only <its 130-131 exact names> --passes 1 --burst 3 --gap 4.5 --seed
40<K><S>` (the runner shuffles its part again with that seed). So each configuration runs once per pass, in a
different random order and a different third of the pass each time, and a re-run of a part repeats the same part.
Parts of one pass may run back to back or with other blocks between them; passes of one card should be >= 30 min
apart with other experiments' blocks between (PLAN3 2.13; last part of pass K to first part of pass K+1).

Order inside a block: `others_present` and `ours_running` (exit 3); preflight (files only: numpy, the plan, the runner,
analyze_catalogue.py, `build/enercat_v2/host/enercat_host` with `--jump-every` and its compiled-in kernel ELF, ettelem,
on governor-free cards the heater with `--per-shire`/`randn`; the runner's `--list` must select exactly the plan's
configurations); `block_begin catfull <KS>`; `code.sha256` (lib.sh, this directory, the runner, run_catalogue.py,
analyze_catalogue.py, the enercat host); `plan.json`; the card's clock before anything runs (`clock_mhz`, into
`pass.json` `idle_mhz_start`); on a governor-free card the preheat to >= 76 C (below); `pass.json`; `others_present`
again; `start_sampler telemetry.jsonl` (lib.sh: 10 Hz, retry, drain; on aifoundry1 without the drain, below); the
runner (every device process `timeout 10`, stdin /dev/null; it stops the part on another user, exit 3, or a stalled sampler, exit 4); a configuration whose burst
process printed no launch (aifoundry3's intermittent host crash, lessons.md) is run once more at the end of the part
(at most 12; runner output in `retry/`, its launches appended to `runs.jsonl`); `stop_sampler` (SIGTERM); the post-block
check `cflib.py check` (off-card) writes `check.json` and prints the status (its stderr goes to `check.err`, so a
numpy warning cannot become the status word); gzip; `block_end`. The clock read before anything runs is retried once
after 2 s if the sampler does not start (lib.sh: about one start in three fails right after a previous instance).

**No management drain on aifoundry1.** lib.sh's `drain_mgmt` runs `/opt/et/bin/dev_mngt_service -n 0`, a build that
ignores ET_DEVICES and opens every card (lessons.md): with `V3_DEVICE=1` it would drain card 0, not card 1, while card
0's own queue may be sampling. block.sh therefore replaces `drain_mgmt` by a logged no-op whenever `V3_DEVICE` is set,
so lib's `start_sampler` (second failed start), `stop_sampler` (after a SIGKILL) and the preheat never open the other
card. A card whose management queue stays blocked then fails its block (`sampler would not start`) instead.

`--smoke` (`catfull-smoke/p<n>`, under a minute, no heater): three configurations (`fmul.ps/random/h2` compute,
`tload/scp/random` with its prefill, `dramrow2/seq/random` with `--jump-every`), `--burst 1 --gap 4.5 --lead 3`, the
retry path, the check. Run it by hand once per card before the campaign (`V3_DEVICE=<n>` on aifoundry1): queue.sh
passes one argument to a block, so `catfull 1 --smoke` cannot be a schedule line.

Block status (block.json): `ok`; `offclock` (governor-free card: a burst was dropped for its clock; the queue re-runs the
part if the schedule is run again, and reduce.py uses the part with those bursts dropped); `partial` (configurations
without a launch after the retry; used); `others` (exit 3: moved aside and retried by the queue); `fail` (no telemetry,
more than half the configurations without a launch, sampler gone, runner crash). Files in `catfull/p<KS>/`:
`runs.jsonl.gz`, `telemetry.jsonl.gz`, `marks.jsonl.gz` (prefills), `configs.json`, `plan.json`, `pass.json`,
`preheat.jsonl`, `run.log`, `runner.out`, `retry/` (if any), `check.json`, `block.json`, `code.sha256`.

## Per-card parameters

| | aifoundry2 | aifoundry3 | aifoundry1-c0 | aifoundry1-c1 |
|---|---|---|---|---|
| lib.sh GOV_FREE | yes (TDP 65 W) | no: pinned at 600 MHz (et-board-clock-guard) | yes (TDP 65 W) | yes (TDP 65 W) |
| firmware | 1.3.1 | 1.3.1 | 1.4.1 | 1.2.0 |
| heater (lib.sh HEATER) | build/sparsity_t2 | none used | build/sparsity | build/sparsity |
| preheat before each part | >= 76 C | none | >= 76 C (aifoundry2's value) | >= 76 C (aifoundry2's value) |
| clock drop rule | busy samples + every launch (not the first after a bracket off 600 MHz); brackets never | none (recorded) | as aifoundry2 | as aifoundry2 |
| management drain (lib.sh drain_mgmt) | as lib.sh | as lib.sh | skipped (V3_DEVICE set) | skipped (V3_DEVICE set) |
| leakage correction | analyze_catalogue's law (aifoundry2's idle law, A80 23.257 W, T_L 36 C) on every card, as on 23 Sep | same | same | same |
| idle between bursts (lessons.md) | 600 MHz | 600 MHz | **300 MHz / 398 mV, "low_power"** (18.8 W board) | 600 MHz / 499 mV (32.9 W) |

- **Heating.** The 23 Sep catalogue started aifoundry2 on a warm die (71 C at its first sample) and the catalogue's own
  load kept it at 71-85 C and 600 MHz on every sample for 2.6 h, with no heater inside the run; aifoundry3 ran cool
  (50-58 C, pinned). catfull does the same per part: governor-free cards start each part at >= 76 C (lib.sh heat_to's
  loop and bound: 2 s random fp32 matmul launches, at most 150; here with `others_present` before every reading, and no
  management drain on aifoundry1, above), and no heater runs inside a part. aifoundry1's cards take aifoundry2's
  76 C: both report TDP 65 W and a 65 C temperature threshold, as aifoundry2 does (queried 25 Sep), and nothing measured on them says otherwise; whether their governors (firmware
  1.4.1 and 1.2.0) lift the clock on a cool die as aifoundry2's does is not known, which is why the clock rule stays.
  A preheat that stops short is recorded (`pass.json` `heat_reached`, block note) and the part runs anyway: the
  busy-sample rule decides.
- **aifoundry1-c0's idle state.** Its firmware (1.4.1) drops the minions to 300 MHz / 398 mV between kernels. A burst
  then runs at 600 MHz while its idle brackets sit at 300 MHz, so its energy over idle includes the step from that idle
  state to the 600 MHz operating point. Card 1, idle at 600 MHz, draws 32.9 W against card 0's 18.8 W at 300 MHz, so
  that step may be ~10-14 W, against a median 5.5 W (10-90%: 2.2-12.9 W) that a configuration adds over idle on
  aifoundry2 in the committed catalogue: card 0's values would be dominated by it and are not comparable with the
  other cards'. The idle brackets are therefore never a drop criterion (a rule that covered them would drop every
  burst there); every burst records its idle clock and busy clock, and reduce.py reports each card's idle state and
  leaves a card whose idle is not at 600 MHz out of the headline pooled values (`pooled_600idle`). The first launch of
  a burst that follows a bracket not at 600 MHz may carry the wake-up from 300 MHz, so there the implied-clock rule
  tests the launches after the first and records the first (`first_launch_ghz`, `first_launch_tested` false); after a
  600 MHz bracket every launch is tested. A slow first launch also lengthens the burst's wall time, which
  analyze_catalogue multiplies by the busy power (read from lo + 0.5 s on), so it biases that card's values up by up
  to ~1/8 of the first launch's slowdown (8 launches per burst); `first_launch_ghz_min` per card shows its size. If
  the card also drops to 300 MHz between the launches of one burst, the busy-sample rule drops those bursts, the blocks
  read `offclock`, and CF-COVER reports it.
- **Two cards in one host.** aifoundry1's two queues run at the same time on separate cards (lib.sh ours_running is
  per card); the cards share a chassis, so one card's load can warm the other. The die temperature of every burst is in
  the data (`die_c_busy`, `die_c_before`); nothing here corrects for it.

## What is dropped and why (cflib.py)

- Governor-free cards (all but aifoundry3): a burst whose busy samples (bursts_of's busy window, lo + 0.5 s .. hi) are
  not all at mhz.minion 600 (`mhz_busy_all_600`); or one of whose launches has an implied clock cycles_max / wall_s
  outside 0.595-0.605 GHz, except the first launch when the bracket before the burst is not all at 600 MHz (above). In
  the committed 23 Sep data every sample is at 600 MHz and every launch, the first included, in 0.598-0.600 GHz. Idle
  brackets are never tested and a bracket's clock never drops a burst.
- This differs from V3-CAT on aifoundry2, which also drops a burst with any idle-bracket sample off 600 MHz (PLAN3's
  R-clock: aifoundry2's governor lifts a cool idle to 700-800 MHz, 5-9 W higher, which enters the over-idle power).
  catfull does not (the four-card rule: brackets are never a drop criterion); instead CF-GAP carries
  `sensitivity_idle600_only`, the registered test recomputed without the bursts whose brackets were not all at
  600 MHz, with the count left out per card (reported, never the outcome).
- aifoundry3: no clock rule (pinned); clocks recorded.
- Every card: bursts bursts_of cannot cut (too few samples); a burst whose brackets overlap a heater launch (a guard:
  catfull runs no heater inside a part).
- Not dropped: slow-sampler bursts (median took_ms > 60), as analyze_catalogue keeps them; counted in check.json.
- Left out of the catalogue: `dramrow/stride256K/{zeros,random}` (2 of run_catalogue.py's 394 configurations). They ask
  for 2,048 slices of 8 MB (16.4 GB of card DRAM, and the host builds the same 16 GB fill in its own memory first); on
  23 Sep they printed no launch on either card (run.log "0 launches"), so the catalogue has no value for them, and on a
  shared host they would hold 16 GB of memory for up to 10 s.

## Card minutes

Measured on 23 Sep (runs.jsonl, first to last launch): **51.7 min per pass on aifoundry2 and 52.0 on aifoundry3**
(386 configurations; 3 passes in 155.5 and 156.4 min of telemetry, 2.6 h per card; 8.0 s per configuration, 8.6 s
with a scratchpad prefill, bursts 3.21 s long), and 0.9 min per pass for the six dramrow2 rows (aifoundry2 only).

catfull per block (131 configurations): runner ~17.6 min (bound from the runner's `--list`: 22.4 min), plus about
0.5 min of block overhead (die and clock reads, sampler start, 10 s lead, 7.5 s tail), plus the retry (0 to 2 min;
~10-20 s on aifoundry3 at its ~1% host-crash rate), plus the preheat on governor-free cards (0-3 min on aifoundry2,
typically; at most 150 launches, ~10-12 min).

| | aifoundry2 | aifoundry3 | aifoundry1-c0 | aifoundry1-c1 |
|---|---|---|---|---|
| per block (typical / bound) | 19-21 / 37 | 18-19 / 25 | 19-21 / 37 | 19-21 / 37 |
| per pass (3 blocks) | ~60 | ~55 | ~60 | ~60 |
| 3 passes | ~3.0 h | ~2.8 h | ~3.0 h | ~3.0 h |
| smoke | < 1 | < 1 | < 1 | < 1 |

A whole pass in one block would be ~53 min plus the preheat, over the ~35 min limit, hence three parts. The bound
adds the runner's own bound (22.4 min, 10 s per configuration against the 8 s measured), a full retry (12 x ~12 s)
and a preheat that needs all 150 launches (~12 min); with the measured 8 s per configuration it is ~33 min. The
aifoundry1 preheat times are unknown until the smoke and the first part; a card that needs the full 150 launches
every part adds ~30 min per pass.

## The items (reduce.py; rules fixed by the amendment before any data)

Unit = pass. A pass is complete when all three of its parts are used (ok, offclock or partial); pass-level items use
complete passes only, per-configuration values every kept burst. Fewer than 3 complete passes on a card: INSUFFICIENT
on that card. **Registered outcome** = over aifoundry2 and aifoundry3 (the committed catalogue's cards).
**all_cards** = over the four campaign cards (`--cards` changes the list) and any other card present: PASS if the item
holds on every card, CARD-DIFFERENT on some, FAIL on none, INSUFFICIENT if any card lacks repeats or data (with
`outcome_over_cards_with_repeats` over the others); an item registered for named cards is REPORTED on the others.

- **CF-GAP** (E27: aifoundry3 / aifoundry2 median 0.950 over the catalogue). Per complete pass on a card,
  g = 100 x median over configurations of ln(value / aifoundry2's mean for that configuration) (positive values only);
  Welch 99% of aifoundry3 - aifoundry2 on the pass values, as a ratio exp(g/100). PASS when the ratio's interval lies
  wholly below 1; FAIL otherwise. all_cards: REPORTED (the claim names these two cards); every other card's ratio to
  aifoundry2 and its interval are in `per_card`, with the card's idle state.
- **CF-COVER** (E27: all configurations at 600 MHz, none failed), registered for each card: >= 3 complete passes and
  every configuration of the catalogue kept (after the drop rules) in >= 3 passes. all_cards over the four cards.
- **CF-REP** (E27: pass-to-pass standard error 1.9% / 6.1% median / 90th percentile on aifoundry2, 1.2% / 3.6% on
  aifoundry3): REPORTED per card (analyze_catalogue's own statistic), the committed values beside.
- Every item that concerns energy over idle carries `idle_clock`: each card's idle state in words. A card's state is
  "600" when >= 90% of its kept bursts have every bracket sample at 600 MHz; otherwise it is the most common bracket
  clock among the other bursts (e.g. "300" on aifoundry1-c0, "mixed:600/700"), and the card leaves `pooled_600idle`.

Values (not items): `configs[cfg]` gives each card's mean, sd, se, n; `pooled_all` (every card), `pooled_600idle` (the
cards whose idle brackets are at 600 MHz in >= 90% of kept bursts: the headline for pooled tables), and
`pooled_registered` (aifoundry2 + aifoundry3, comparable with the committed `combined`), each as analyze_catalogue's
confidence bars (mean, range, sd within, 95% half-width, card difference); each card's ratio to aifoundry2; the
committed 23 Sep values beside, never pooled. `ratios`: every card against aifoundry2 and every pair (median and
10-90% over configurations, analyze_catalogue's cross_card), the committed cross_card beside. `vs_committed_23sep`:
new / committed per configuration on aifoundry2 and aifoundry3. `idle_clock` per card: bursts by idle clock, idle
samples by clock and the idle board power at each, the lead's clock, `idle_mhz_start`, busy clocks, the lowest first
launch clock.

## How to reduce

Collect every card's DATA_ROOT into `<dir>/<card>/catfull/p<KS>/` (e.g. `rsync -a aifoundry1:nekko/build/claims-v3/aifoundry1-c0/catfull <dir>/aifoundry1-c0/`), then

    python3 tools/claims-v3/catfull/reduce.py --data <dir> --out verdicts.json --catalogue-out catalogue4.json

`catalogue4.json` has analyze_catalogue.py's shape (cards/summary/wire/sram_leakage, bursts, combined, cross_card,
rail_filter) keyed by card id, plus `combined_600idle` and `combined_registered`. It runs on partial data.

Tested (scratchpad `validate3/fourcards/catfull/`): dry runs of all nine blocks and the smoke on the four card ids
(hostname shim, `V3_DEVICE=0/1`); synthetic four-card data (`mk_synth.py`: all four hold; aifoundry1-c0 dipping to
300 MHz inside three configurations' bursts; aifoundry1-c1 missing; aifoundry3 short of a complete pass), in which
aifoundry1-c0's 300 MHz idle and its slow first launch drop nothing; the reviewer's case `review/mk_rules.py` (a slow
first launch after a 600 MHz bracket is dropped on aifoundry2 and aifoundry1-c1 but kept on aifoundry1-c0; 700 MHz
brackets on aifoundry2 drop nothing, are counted in CF-GAP's sensitivity, and take aifoundry2 under the 90% idle rule,
out of `pooled_600idle`); and the committed 23 Sep raw data cut into this
layout (`mk_legacy.py`), which reproduces catalogue.json's per-configuration values to 6e-7, its wire slopes, rail
filter, cross_card (0.950, 10-90% 0.906-0.987) and pass-to-pass errors (1.9% / 6.1%, 1.2% / 3.6%).
