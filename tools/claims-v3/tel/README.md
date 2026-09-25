# V3-TEL: the meter chain (PLAN3 §2 "V3-TEL", suggested E41)

SP pass interval by sampler, `--reset-ms` windows, peak-hold, per-shire voltage maps and governor readouts. It merges
the inventory experiments E-hub-1, pt-spatial X4, X2, X3 and dvfs EXP-dvfs-2, and tests 53 claims. The items are
TEL-P1..P7, TEL-S, TEL-Q, TEL-R and TEL-G.

```
bash tools/claims-v3/tel/block.sh <pass>            # one pass on the local card (passes 1, 2, 3 on each card)
bash tools/claims-v3/tel/block.sh 1 --smoke         # the pipeline check, about 55 s of card time; data in tel-smoke/p1
V3_DRY=1 bash tools/claims-v3/tel/block.sh 1        # prints every device call, touches nothing
python3 tools/claims-v3/tel/reduce.py --data <dir holding aifoundry2/ and aifoundry3/> --out verdicts.json
```

The files:

- `block.sh` runs one pass or the smoke check.
- `tel_util.py` holds the standard-library helpers that `block.sh` calls on the card hosts. They draw the arm order,
  read the SP stats extracts, run the wrap guard, merge the extracts and check what a pass holds.
- `reduce.py` holds the pre-registered items and needs numpy. It imports the committed parsers from the tree it sits
  in, or from `V3_REPO` when that is set.

Schedule: three passes per card, at least 30 minutes apart, with other experiments' blocks in between. PLAN3 §2.13
interleaves them as a2 p1, a3 p1, a2 p2, a3 p2, a2 p3, a3 p3. The schedule lines are `tel 1`, `tel 2` and `tel 3`.
The smoke directory is `tel-smoke`. Re-running a smoke check needs `V3_FORCE=1`, which replaces the old smoke data.
On a full pass, `V3_FORCE=1` sets the old directory aside as `p<N>.attempt-<time>`. A leftover pass directory with no
`block.json` is always set aside, so data from two runs never mix.

## What a pass does (in this order)

1. **Governor readouts** at INFO log level, with no sampler (EXP-dvfs-2). The block first sets `ettelem loglevel info`.
   On aifoundry2 it runs `heat_to 76` first if the die is below 68 C. Then it runs `sptrace gov/sp0.bin`, `etcfg
   /dev/et0_mgmt` into `gov/driver.json`, and five `sparsity_host --test fma --type fp32 --pattern none --values zeros
   --shires 0xffffffff --per-shire 32 --seconds 2 --budget 5 --seed 1` launches 3 s apart. After those it runs
   `sptrace gov/sp1.bin` (after the launches and before any config query), `ettelem config` and
   `dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`.
2. **The arms** (E-hub-1 and X4).
   - On aifoundry2 the block first heats the die to at least 76 C.
   - It sends `SPST:enable` and takes an SPST extract, then waits 60 s in quiet (Q0).
   - It then runs the seven arms Q, PWR, L10, E10, E20, E40 and VOLT, in the order `random.Random(card*100 +
     pass).shuffle` gives. The order is logged in `arms_order.json`.
     - Q: 60 s quiet.
     - PWR: one `DM_CMD_GET_MODULE_POWER` after another for 60 s, about one per 16 ms.
     - L10: one call per 0.1 s sleep, 450 calls.
     - E10, E20 and E40: `ettelem sample` at 100, 50 and 25 ms, for 60, 60 and 30 s.
     - VOLT: `DM_CMD_GET_MODULE_VOLTAGE` 80 ms apart, for 60 s.
   - After each arm the block takes an SPST extract and waits 30 s in quiet (`G_<arm>`).
   - Before each arm, a wrap guard may add a quiet wait (`W_<arm>`), explained under Deviations.
3. **Reset segment** (E-hub-1, P6 and P7).
   - On aifoundry2 the block first reheats the die to 76 C.
   - It starts `ettelem sample --every-ms 100 --reset-ms 1000`. Then come 5 s of idle and three `enercat_host --pattern
     fmadd_ps --operands random --harts 2 --seconds 3 --budget 8` bursts, 10 s apart.
   - The sampler stops (SIGTERM) 12 s after the third burst.
   - Then the block sends `SPST:enable` and takes an extract.
4. **DEBUG block** (X2 and X3).
   - On aifoundry2 `heat_to 76` runs first; it does nothing on a die that is still at 76 C.
   - The block sets `ettelem loglevel debug`, waits 2 s and runs `sptrace dbg/x2-idle.bin`.
   - Next comes a 7 s `--values randn` burst (seed = pass), with `sptrace dbg/x2-load.bin` taken 4 s after its
     launch. The block then waits 20 s and runs `sptrace dbg/x2-after.bin`.
   - Then come three 14 s windows `ettelem sample --reset-ms 600000`, each with a 7 s randn burst (seed = window)
     launched 3 s in and `sptrace dbg/x3-w<k>.bin` right after the window, with 30 s between windows.
   - Then one idle window (`w4`), `loglevel info` and `SPST:enable`.
5. **Pack**. The block merges the SP stats extracts into `trace/merged.spst` (unique records in SP-time order) and
   gzips the telemetry. `tel_util.py check` writes `check.json` with what the pass holds, and `block.json` names
   anything missing.

Every device process runs under `hold10`, which is `timeout 10`. Every launch runs under `hold10`; the enercat launch
also gets `--budget 8`, and the governor launches `--budget 5`. The ettelem samplers run only through `start_sampler`
and `stop_sampler`, and nothing else opens the management node while one runs. The poll loops are bounded by a count
or by a time checked before each call, and no poller is ever killed mid-request.

Before the reset segment and before the DEBUG block, the block checks for other users again. The reset and the DEBUG
log level change what an et-powertop user sees. If someone is on the card, the block restores the card and exits 3,
and the queue retries the whole pass later. The EXIT trap stops the sampler, re-enables the SP stats trace and
restores the INFO log level.

## Card minutes per pass

| | aifoundry2 | aifoundry3 |
|---|---|---|
| governor readouts | 0.6 (+ heating when the die is below 68 C) | 0.6 |
| heat to 76 C before the arms, and reheats | 1-5 | 0 |
| arms (Q0, 7 arms, 8 extracts, 7 x 30 s gaps) | 11.1-12.6 (the upper end when the wrap guard waits) | 11.1-12.6 |
| reset segment | 0.9 | 0.9 |
| DEBUG block | 3.1 | 3.1 |
| **pass** | **about 17-23** | **about 16-17** |
| **3 passes** | **about 52-69** (plan: 60) | **about 48-52** (plan: 48) |

The management node is held almost throughout. Launch time on the ops node is small: 5 x 2 s of zeros, 3 x 3 s of
enercat, 4 x 7 s of randn, and the heater on aifoundry2.

The smoke check runs every component once and takes about 50-55 s of card time on either card. It has one zeros
launch, 1-2 s of each arm with no gaps between arms, a single extract after the arms and no wrap guard, a 1 s burst in
the reset segment, and one DEBUG window with a 1 s burst. It has no heating and no X2 burst. The reviewer's estimate
allows for sampler start-up and host setup of each launch: about 50-58 s. It passes when every component produced data (`check.json` `missing`
is empty).

## What is dropped, and why

- A pass whose `block.json` status is not `ok` is not used. The block aborts when a sampler cannot start, and exits 3
  when another user appears.
- The aifoundry2 rule "anything with `mhz.minion != 600` is dropped" is applied like this:
  - An ettelem arm (E10, E20 or E40) with any sample off 600 MHz is dropped from every item that uses it: its
    SP-interval value (P3 and its E40 part) and its refresh fit (P_H from E10, P_H2 from E20, in TEL-S). The
    alignment still uses it, because it does not depend on the clock.
  - A burst with any reset-log sample in [start, end] off 600 MHz is dropped from P6 (first-second test) and P7.
  - An X3 window with any sample off 600 MHz is dropped from TEL-R.
  - The X2 load capture is dropped from Q4 when a timed launch's `ghz` is outside 0.59-0.61. No sampler runs during it.
  - A pass whose three bursts are all dropped cannot decide P6's first-second test, so the pass is not used for P6.
- **Launch lines.** `sparsity_host` prints one line per launch. Each process starts with a calibration launch
  (`"launch": -1`, about 18 ms). Its `ghz` reads about 0.586 because overhead dominates its wall time (the 22 Sep
  aifoundry3 and 21 Sep aifoundry2 runs.jsonl give 0.583-0.590). Then come 0.5 s launches numbered 0, 1 and so on.
  Like the repository's analyses (`workloads/*/run_energy.py`, `analyze_power.py`), the reducer drops launch -1.
  "Every launch 0.59-0.61 GHz" (TEL-G) and the X2 clock check read the timed launches only. TEL-G also needs all five
  processes, tagged `G1`..`G5`, to have printed.
- aifoundry2 governor readouts that did not start on a die at 68 C or above are dropped from TEL-G. The die reading
  comes from `block_begin`'s reading or the last heater reading.
- SP pass intervals are dropped within 1 s of a segment boundary, as registered. Intervals over 1 s are also dropped,
  because they span records lost to a ring wrap.
- P7 drops bursts outside the catalogue rule: minion rail over idle must exceed 8 W, with at least 4 s of idle on each
  side. This is `analyze_catalogue.rail_fall_curves`, unchanged.
- At pack time, `dev_mngt_service` writes a text decode (`trace/dev0_traces.txt`) and the individual extracts. Both are
  deleted once `merged.spst` has passed its record-count check. `merged.spst` holds every unique record.

## Deviations from the plan's commands (sources win)

1. **ettelem `--reset-ms` switches the SP stats trace off. The block switches it back on.**
   - ettelem's `resetStats()` sends `DM_CMD_SET_STATS_RUN_CONTROL` with type 1 and control 2 (RESET_COUNTER only).
   - The firmware reads a control word without bit 0 (TRACE_ENABLE) as "disable the SP stats trace". This is
     `dm_svc_perf_stats_run_control` in ServiceProcessorBL2/services/performance.c. It is the same in the cards'
     May 2024 build (`validate3/fw-may2024/performance.c` l.562) and in 353f20e.
   - So the first `--reset-ms` sample stops all SPST records until something re-enables the trace. That would include
     every later pass's P1-P5, and anyone else's extracts.
   - The block therefore sends `dev_mngt_service -n 0 -t SPST:enable` in four places: after the reset segment, after
     the DEBUG block, in the EXIT trap, and at the start of the arms. The trap's re-enable is armed before each
     `--reset-ms` sampler starts, because `start_sampler`'s failed attempts reset the stats too. At the start of the arms it only restores the
     default if something left the trace off. It sends DM_CMD_SET_STATS_RUN_CONTROL with control 1: enable, no reset.
   - This is a bug in `tools/ettelem/ettelem.cpp`: `resetStats()` should send control 3. That file is not ours to change.
2. **An SPST extract after every arm, and a wrap guard. The plan had three extracts per pass.**
   - When the 1 MB stats ring (6,898 records) fills, the firmware resets the write offset to the header. This is
     `trace_check_buffer_full` in et-trace encoder.h.
   - An extract returns only the records written since that reset. `dumpRawTraceBuffer` writes `data_size` bytes.
   - The ring wraps every 15.4 min at 133.6 ms per pass, and phase 2 lasts about 12 min. So three extracts would lose
     the records between an extract and a wrap, which is usually part of one arm.
   - The block therefore extracts after each arm. Before each arm, `tel_util.py wrapwait` estimates from the last
     extract's record count when the ring will wrap. If that could happen inside the arm, the block waits in quiet
     until the wrap has passed (`W_<arm>`, at most about 85 s once per pass) and extracts again.
   - The smoke check skips the guard, which keeps it under 60 s. A wrap lost in a smoke check costs nothing.
3. **SP-to-host alignment uses exact sample-record matching instead of the three burst edges.**
   - The burst edges are gone because of deviation 1: the trace is off during the reset segment.
   - Each ettelem sample carries the SP's current rail and board averages (mW and 10 mW). The SP also writes those
     into that pass's stats record.
   - The offset at which each E10, E20 and E40 sample shows the latest record before it is found on a 1 ms grid. On
     synthetic data 99.7-100% of samples match and the offset is recovered exactly. The median over the arms that
     match at least 50% is used.
   - Fallback: the extract-time anchor (the extract's host time minus its last record, good to about ±0.5 s). The
     method is recorded per pass.
4. **PWR is a bounded copy of `scripts/et-power-log.sh`'s loop, not `timeout 62 bash scripts/et-power-log.sh 0 0`.**
   `timeout` sends SIGTERM to the whole process group. That kills a `dev_mngt_service` mid-request and poisons the
   management queue. PLAN3 N2 also says "bounded poll loops only". The block keeps the same command, the same sed and
   interval 0, with a 60 s limit checked before each call and each call under `timeout 10`.
5. **VOLT calls run under `hold10` (`timeout 10`) instead of `timeout 5`.** This is the framework helper, and it makes
   the calls show in dry runs. `-u 2000` still bounds each request.
6. **Quiet segments.**
   - The plan's order lists "60 s quiet, then the arms Q, PWR, ...". The block runs both: Q0 (60 s) and a shuffled Q
     arm (60 s).
   - The 30 s gaps and any wrap-guard waits are quiet too.
   - The arm-order seed is `card*100 + pass` (201-203 and 301-303). The plan's "K" was not specified.
7. **Reset segment.** The sampler runs until 12 s after the third burst ends (at most 80 s), instead of a fixed 45 s.
   - With the plan's timing the third burst ends 36-39 s in. P6's "every 1 s window starting ≥ 8 s after the last
     burst" could then be empty.
   - The third burst would also fail the catalogue rule of at least 4 s of idle after it, which P7's f(1 s) uses.
   - The enercat bursts get `--budget 8`. The host's default is 9.5 s, and the rule says `--budget ≤ 8` or timeout 10.
8. **DEBUG block.** The merged order (4) has no capture during a burst, but Q4 ("under the load") needs one. So the X2
   load and after captures run around their own 7 s randn burst before the X3 windows, as in the X2 component's
   command.
   - The "mem" capture of X2 is served by the X3 window-end captures, which come right after a sample.
   - A 2 s pause after `loglevel debug` lets the 8 KB ring fill with DEBUG-level passes before the idle capture.
9. **aifoundry2 heating.**
   - Phase 1 heats only when the die is below 68 C (EXP-dvfs-2's rule).
   - Before phase 2 the die is heated to 76 C (the plan), and again before phase 3 (the plan).
   - Before phase 4 there is one more `heat_to 76`. It is a no-op when the die is still warm. X2 and X3 want the load
     captures at 600 MHz / 0.52 V.
10. **Defensive `ettelem loglevel info` at the start** of phase 1, in case an interrupted block left DEBUG on. INFO is
    the level the plan restores.
11. **etcfg.** The block compiles `tools/etcfg/etcfg.c` once per host into `build/claims-v3-bin/etcfg`, outside the
    data tree. It is called with `/dev/et0_mgmt` explicitly, because by default it also tries `/dev/et1_mgmt`. It runs
    under `hold10`: it does open `/dev/et0_mgmt`, although its README says it does not.
12. **Launch result lines are tagged** (`G1..G5 SPARSITY`, `B1..B3 ENERCAT`, `X2` / `W1..W3 SPARSITY`) so the reducer
    knows which launch each line belongs to.
13. **Binaries.** `build/sparsity/host/sparsity_host` is used for the zeros and randn launches on both hosts, as the
    plan's commands say. aifoundry3 has no `sparsity_t2`, and TEL needs none of its features. The heater on
    aifoundry2 is lib.sh's `heat_to` (sparsity_t2). `ettelem` and `dev_mngt_service` flags were checked against
    `tools/ettelem/ettelem.cpp` and `device-management-application/src/dev_mngt_service.cc`. The `enercat_host` and
    `sparsity_host` flags were checked against their `host/main.cpp`.

## Reduction (every open choice, fixed before any data)

**Segments.**
- Segments are host-time spans from `marks.jsonl` (begin and end per activity).
- For E10, E20 and E40, the segment is the sampler's own first-to-last sample.
- Quiet segments are Q0, Q, `G_*` and `W_*`.
- Each segment's value is the median SP pass interval, with both records inside [start + 1 s, end − 1 s], intervals
  over 1 s dropped, and at least 20 intervals.
- A pass's **Q** is the median over all its quiet segments pooled. The paired differences PWR − Q, E10 − Q and
  VOLT − Q use this pooled Q.

**TEL-P1..P5 (SP stats intervals).**
- **TEL-P1** holds in a pass when *every* quiet segment's median is in 131.6-135.6 ms ("median over each quiet
  segment"). It must hold in every kept pass, and at least 3 passes are needed.
- **TEL-P2** needs |PWR − Q| ≤ 1.5 ms in every pass.
- **TEL-P3**: the outcome follows the decision rule alone: E10 ≥ 145 ms in every pass, and the one-sided 99% t lower
  bound (df n−1; 6.965 at df 2) on E10 − Q above 0. "E10 − Q > 8 ms" and "E40 ≥ E10" are reported per pass as parts
  that are not in the decision rule.
- **TEL-P4** uses the two-sided 99% t interval (9.925 at df 2) on VOLT − Q:
  - lower end above 5 ms: "confirmed", outcome PASS (VOLT lengthens the pass);
  - interval inside ±1.5 ms: "rejected", outcome FAIL;
  - otherwise: "not resolved", outcome FAIL.
  The `decision` field names which case it was.
- **TEL-P5** (aifoundry3):
  - every pass with E10 in 255-272 ms and Q ≥ 230 ms: "the SP loop is slow", PASS;
  - Q < 160 ms in every pass: "sampler-induced", FAIL;
  - otherwise: "reported as is", FAIL.

**TEL-P6 (the reset windows).**
- A window closes at the sample whose `since_reset_ms` ≥ 1000. ettelem resets after that sample's reads, so its
  min/max cover the whole window.
- "Cycles 0-1000" means all values are ≥ 0, every closing value is ≤ 1300 (one late 100 ms tick plus slack), every
  following value is < 200, and there are at least 3 windows.
- Late windows are the complete windows starting at least 8 s after the last burst's `t_end_ms`. Each needs
  `sp.minion_w` max − min ≤ 1.0 W, and at least one late window must exist.
- "The window holding each burst's first second" is the window containing start + 1 s. Its max must be at least
  idle + 0.5 × step, where:
  - idle is the median `sp.minion_w` average over [start − 3 s, start − 0.2 s];
  - step is the largest average over [start, end + 1 s] minus idle, which is about 94% of the true step after 3 s.
- "E10 max never falls" means `sp.minion_w[2]` never decreases in the same pass's E10.
- Zero failures are allowed per card, over at least 3 passes. A pass whose bursts were all dropped (the aifoundry2
  600 MHz rule) is not used, unless another part of it already failed.

**TEL-P7.**
- f(1 s) per burst comes from `analyze_catalogue.bursts_of` and `rail_fall_curves`, run on the reset log. This is the
  catalogue definition.
- The median is taken over the kept bursts of a card (9 when nothing is dropped), with bursts from at least 3 passes.

**TEL-S (board refresh period per poller).**
- P_H (E10) follows `v13_refresh.py`'s rules and model: 10 Hz polls, at least 500 samples, intervals over 90-110 ms
  polls, at most 12 polls, at least 150 intervals, q from 0.50 to 0.99.
- P_L (L10) and P_H2 (E20) follow `v13b_powercsv.py`'s rules. That script generalises the same model to any poll
  interval: median dt, polls within ±10 ms of it, q from 0.50 to 1.00, k ≤ 14, and its round(nll, 1) scan quirk.
  At least 30 intervals are needed.
- `v13_refresh.py` itself assumes a 100 ms poll and cannot fit E20.
- The outcome is PASS when the two-sided 99% t interval on P_H − P_L excludes 0 and is positive on both cards. It is
  CARD-DIFFERENT when that holds on one card, and FAIL otherwise.
- The S1/S2 bands and "P_H within ±5 ms of 156/263" are reported per pass.
- `pages` gives the page rule per card: "per sampler", "ettelem figure only" (the interval includes 0 and |mean| < 5
  ms), or "as measured".

**TEL-Q (voltage maps).**
- The captures are parsed by the committed `parse_sptrace_voltage.parse`.
- Q1:
  - The 34-lines-parse part is registered for aifoundry3. It is checked in every capture on aifoundry3 and reported
    on aifoundry2.
  - Every capture must have 0 `Temp [C]` lines.
  - `MEM n Voltage` lines must be absent from the idle, load and after captures. The window-end captures come right
    after a sample and may have them.
- Q2 uses the minion "now" of each pass's `x2-idle`, with r ≥ 0.6 for every pass pair.
- Q3 uses the mean idle pattern per card and needs |r| < 0.45.
- Q4 compares `x2-load` with `x2-idle` in the same pass. The "99% upper bound" is the upper end of the two-sided 99% t
  interval (the plan's stated standard, 9.925 at df 2) on the pass-level sd of the deviation change. It must be at
  most 0.5 mV. "Common level falls 1-3 mV" and "max |change| ≤ 1 mV" are reported per pass.
- Q5 is `x2_reduce.plane()` (seed 1, 20,000 shuffles, reproduced exactly):
  - minion "now" needs p ≥ 0.0042 in every idle capture (`x2-idle` and the idle window's `x3-w4`);
  - aifoundry2's SRAM "now" needs p < 0.0042 in the `x2-idle` capture of at least 2 of 3 passes.
- PASS needs Q1, Q2, Q4 and Q5 on both cards and Q3. The pt-spatial-49 offset sentence is kept only when Q2 and Q4
  hold on both cards.

**TEL-R (peak-hold windows).**
- The per-window figures are `x3_reduce.py`'s, unchanged. The unit is the pass.
- R1 must hold in every kept window.
- R2 is decided from each pass's median over its load windows.
- R3 pools the rises over all load windows of a card.
- R6 is judged per load window:
  - "lows below idle" counts the shires whose `x3-w<k>` minion low is at least 2 mV under the same pass's `x2-idle`
    "now";
  - "die_mv.minion fell" is the median before the burst's `t_start_ms` minus the minimum from the burst start to the
    window's end.
  - A pass holds R6 when the medians over its load windows give at least 17 shires and a fall of at most 2.5 mV. The
    card holds R6 when at least 2 of 3 passes do.
- PASS needs R1-R6 on both cards, with R2 "holds". When R1 fails, the reading says the claims stay under-replicated.
- A card is INSUFFICIENT when a part cannot be computed and no other part has failed. For example, no idle window
  may survive the drops, or fewer than 3 passes may give an R6 figure.

**TEL-G (governor readouts).**
- Governor events are read in buffer order, with `analyze_dvfs.py --sptrace`'s regex. The INFO rings do not walk with
  `ring_entries`: the committed 22 Sep dumps give 1 and 0 entries.
- A repeated idle event means two consecutive old-format idle events.
- On aifoundry2, the prediction "any idle-state line in the pre-60b40c10f format" holds unless a 353f20e-format line
  appears.
- The `dvfs_75` field says one of four things:
  - "refuted": a 353f20e-format line appeared;
  - "stays one card": aifoundry2 printed no governor line in any pass;
  - "both cards run the older governor": aifoundry2 printed an old-format idle line;
  - "not decided": none of the above.
- Firmware must be 1.3.1 with PMIC 1.5.0, the same on both cards.

**Outcomes.**
- INSUFFICIENT: a card the item names has fewer than 3 kept passes.
- PASS: the item holds on every card it names.
- CARD-DIFFERENT: the item holds on one of the two.
- FAIL: otherwise.

## Tests done (off the card)

Reviewer's tests (25 Sep), in `validate3/drv/tel/rev/`:
- `realruns.py` rewrites the synthetic launch logs the way `sparsity_host` prints them: a calibration launch, then
  0.5 s launches. Before the fix, this made TEL-G FAIL on both cards and TEL-Q INSUFFICIENT on aifoundry2.
- `failcase.py` makes five targeted failures, and each item turns as it should:
  - a late reset window spanning 1.6 W (TEL-P6 CARD-DIFFERENT);
  - aifoundry3 with `tdp_w` 65 in one pass (TEL-G CARD-DIFFERENT);
  - a peak-hold that was not reset (TEL-R R1, CARD-DIFFERENT);
  - a shuffled idle map (TEL-Q Q2, CARD-DIFFERENT);
  - SP passes 3 ms slower under PWR (TEL-P2 FAIL).
- `realruns.py --offclock` puts one 0.70 GHz launch in every process. TEL-G gives FAIL, and aifoundry2's Q4 becomes
  INSUFFICIENT.
- `V3_DRY=1` runs of passes 1-3 and of the smoke check, on both cards, after the fixes.

- `bash -n`, and `V3_DRY=1` runs of passes 1 and 2 and of the smoke check on aifoundry2 and aifoundry3. aifoundry3 was
  run with a fake `hostname` on PATH.
- `reduce.py` on synthetic passes built by `validate3/drv/tel/make_synth.py`:
  - SP records per segment, samples reading the latest record, pollers with their own refresh periods, reset windows
    as ettelem makes them, rings in the firmware's format, and the committed governor dumps.
  - Variants: all passes present (every item decides), one card with one pass (every item INSUFFICIENT), a band
    failure plus a failed block (FAIL and INSUFFICIENT), off-600 MHz samples (drops), and a restarted average
    (P7 FAIL). It also ran on the dry-run output, with empty files.
- `validate3/drv/tel/check_vs_legacy.py` reproduces the original scripts exactly on committed data:
  - `v13_refresh.py` per-log P on 8 logs, and `v13b_powercsv.py` on the 3 18 Sep power.csv files;
  - `x2_reduce.plane` r² and permutation p for all three rails of the 20 Sep dump;
  - `x3_reduce.py` on the E5 log;
  - `analyze_dvfs.py`'s event sequence on `sptrace-aifoundry3.bin`: 26 down, 27 idle, 1 repeated idle, 0 up.
  - f(1 s) on the catalogue's fmadd.ps random bursts comes out at 0.52-0.62 on aifoundry2 and 0.45-0.65 on
    aifoundry3.

## Known risks

- **The L10 poll interval sits close to the refresh period on aifoundry2.** The interval is about 115-120 ms (0.1 s
  sleep plus about 15 ms per call). Simulated with 450 polls around a true 135.5 ms, the per-pass P_L fit spread is
  131.5-138.5 ms at a 117 ms poll and 130.5-142 ms at a 130 ms poll. On aifoundry3 (true 232 ms) it is 231-232.5 ms.
  It is the registered design, so it is reported, not changed.
  - Reviewer's check (`validate3/drv/tel/rev/sim_tels.py`): 60 fits per poll interval, with P_H ~ N(156, 1.5). The
    chance that aifoundry2's 99% interval on P_H − P_L excludes 0 is about 0.84 at a 117 ms poll and 0.53-0.55 at
    125-130 ms.
  - The writer's own "good" synthetic set (130 ms poll) gives TEL-S CARD-DIFFERENT for this reason alone.
  - A CARD-DIFFERENT TEL-S with aifoundry2 "includes 0" is therefore weak evidence against S3. The page rule then
    decides on |mean| < 5 ms.
- **SPST has never been extracted on aifoundry3.** If the extract or the sample-record match fails there, P5 falls
  back to the anchor alignment or becomes INSUFFICIENT. `passes.<card>[].sp.align.method` in the verdicts records
  which.
- **The sample-record alignment is untested on real data.** No committed session has ettelem samples and SPST
  extracts together. The extract-anchor fallback was checked on the 19 Sep aifoundry2 extracts
  (`build/memprobe-power7`). Anchored at the extract's end, it sits 0.93-1.03 s after `analyze_power.align`'s
  least-squares offset. The block anchors at the extract's start, which is earlier by the extract's duration, so its
  error should be under 1 s. The 1 s trim at each segment edge absorbs that. `sp.align.method` says which method a
  pass used.
- **heat_to can take long on aifoundry2 in a cold room.** lib.sh's `heat_to` gives up after 150 rounds, about 12-14
  min. With three heats a pass could then pass the ~35 min block limit. On a card that idles at 72-80 C, each heat
  takes 1-2 min.
- **aifoundry3's ettelem must know `--reset-ms`, `sptrace` and `loglevel`.** The operator checks this before the
  smoke run.
