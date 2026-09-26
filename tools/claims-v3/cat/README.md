# V3-CAT: energy catalogue, a within-card temperature panel and the DRAM-row rows on aifoundry3

PLAN3 section 2, "V3-CAT (SHOULD)" (merges energy-manual EXP-EM2; suggested experiment number E45). Items CAT-a,
CAT-b, CAT-c, CAT-e, CAT-f; 14 claims. Written for aifoundry2 and aifoundry3; since 25 Sep it runs on four cards
(aifoundry2, aifoundry3, aifoundry1-c0, aifoundry1-c1: section "Four cards" below, and the amendment for V3-CAT in
`docs/reports/data/2026-09-25-claims-v3/AMENDMENTS.md`). Files:

| file | what |
|---|---|
| `block.sh` | one pass (one block) on the local card: `[V3_DEVICE=<0\|1>] bash tools/claims-v3/cat/block.sh <pass> [--smoke]` |
| `run_catalogue_t10.py` | the patched copy of `workloads/enercat/run_catalogue.py` (PLAN3 N6) that the block runs |
| `catlib.py` | burst cutting (analyze_catalogue's `bursts_of`, unchanged), drop rules, statistics, the post-pass check |
| `reduce.py` | the registered items: `reduce.py --data <dir> --out verdicts.json` |

## What a pass does

The pass number fixes arm, condition and seed (the registered interleave: per card, arm A and arm B alternate). A
card's design follows lib.sh's `GOV_FREE`, never its name: governor-free cards (aifoundry2, aifoundry1-c0,
aifoundry1-c1) run aifoundry2's registered design, the pinned card (aifoundry3) its own:

| card | pass: arm-condition |
|---|---|
| governor-free: aifoundry2, aifoundry1-c0, aifoundry1-c1 (11 blocks each) | 1 A-W, 2 B, 3 A-H, 4 A-W, 5 B, 6 A-H, 7 A-W, 8 B, 9 A-H, 10 A-W, 11 A-H |
| pinned: aifoundry3 (12 blocks) | 1 A-C, 2 B, 3 A-H, 4 B, 5 A-C, 6 B, 7 A-H, 8 B, 9 A-C, 10 B, 11 A-H, 12 B |

- **Arm A** (temperature panel): the 30 registered configurations (all >= 8 W over idle on both cards), `--passes 1
  --burst 3 --gap 4.5 --seed 20<k>`, k = the arm-A pass index (1-8 on aifoundry2, 1-6 on aifoundry3).
  - W (governor-free cards, warm, no hold): wait (die_c every 20 s, no launch, at most 10 min) until the die reads
    <= 82 C, then lib `heat_to 76`.
  - H (hold hot): governor-free cards `heat_to 76` (the binding rule), then on every card a preheat to the hold temperature
    (at most 40 heater launches, before the sampler starts), then `--hold-hot C`: before every configuration, up to 5
    heater launches until the running sampler's last minshire >= C, then 1.5 s of settling (`--heat-settle`) before the
    prefill and the gap. C = 88 on the governor-free cards; on aifoundry3 C = Tmax - 1,
    Tmax = the highest minshire in V3-IDLE's telemetry (`$DATA_ROOT/idle/p<N>/telemetry.jsonl.gz`), frozen at the first
    hot pass in `$DATA_ROOT/cat/hold_c.json` so every hot pass holds the same temperature (`CAT_HOLD_C=<C>` overrides).
  - C (aifoundry3, cool): no hold, no heater.
- **Arm B** (rows and bytes): `--only dramrow2,tload/dram,tstore/dram,l1fill/stride32,l1fill/stride64,tload/scp,fence,nop
  --passes 1` = 23 configurations, run_catalogue's defaults `--burst 3 --gap 5`, `--seed 30<k>`; governor-free cards
  `heat_to 76` first; aifoundry3 nothing.

Order inside a block: `others_present && exit 3`; preflight (files only: the enercat build has `--jump-every`, its
compiled-in kernel ELF exists, the heater has `--per-shire`/`randn`, every `--only` prefix selects something, numpy);
`block_begin cat <pass>`; `ettelem config` once (read-only: TDP, temperature threshold, power state, minion clock
and voltage) into `config_start.json` and pass.json's `config_start`, the card's idle state before the block touches
it; the temperature step above (die_c and heater only now, the sampler is not running; the
wait-for-cool and preheat loops call lib's `others_present` before every die reading); `start_sampler telemetry.jsonl`
(lib, 10 Hz, retry + drain); the runner (every device process `timeout 10`, stdin /dev/null; the heater hold reads the
die from `telemetry.jsonl.raw`, which the running sampler writes, so nothing else opens the management node; before
every configuration it stops the pass if lib's `others_present` finds someone (exit 3) or if `telemetry.jsonl.raw`
has not grown for 6 s, i.e. the sampler is gone (exit 4)); `stop_sampler` (SIGTERM); the post-pass check
(`catlib.py check`, off-card) writes `check.json`; gzip of telemetry/runs/marks; `block_end` (through `finish`, which
gives block_end a die reading of `null` instead of an empty one, so block.json stays valid JSON).

Block status: `ok`; `offclock` (governor-free cards only: on aifoundry2 a burst's busy or idle-bracket samples left
600 MHz, or its implied clock did; on aifoundry1's cards its busy samples or its implied clock did. R-clock says drop
and re-run, so the queue treats the pass as not done and re-runs it the next time the schedule runs, moving this
attempt aside to `p<N>.attempt-*`; if it is never re-run, reduce.py uses the pass with
those bursts dropped, as V3-CAT registered); `partial` (up to half the configurations printed no launch: reduce.py
uses the rest; the queue re-runs it if the schedule runs again); `others` (another user or another user's device
process appeared mid-block: the block stopped, exit 3, so the queue moves it aside and retries after 10 min; it never
opens the card again, not even for block_end's die reading); `fail` (no telemetry, more than half the configurations
without a launch, the sampler gone mid-pass, or the runner crashed). A forced re-run (`V3_FORCE=1`) or an interrupted
earlier attempt is moved aside first, so runs.jsonl is never appended to.

Files in `$DATA_ROOT/cat/p<N>/`: `runs.jsonl.gz` (one ENERCAT line per launch, as run_catalogue.py writes),
`telemetry.jsonl.gz`, `marks.jsonl.gz` (heater and prefill intervals), `run.log`, `configs.json` (the exact argument
lists run, the card id, the hostname and ET_DEVICES), `pass.json` (with `gov_free`, `device`, `config_start`),
`config_start.json`, `preheat.jsonl` (die readings of the temperature step), `check.json` (with the idle clock of
every burst's brackets, `idle_states`, the lead's clock `lead_mhz` and voltage, and the settled idle board power per
clock `idle_w_by_mhz`), `block.json`, `code.sha256`. About 0.1 MB per pass (gzipped).

`--smoke` (exp name `cat-smoke`, about 40 s of card time, no heat_to): three configurations, one of each kind that
can break (`fmul.ps/random` compute, `tload/scp/random` with its scratchpad prefill, `dramrow2/seq/random` with
`--jump-every`), `--burst 1 --gap 4.5 --lead 3`, one heater launch through the hold path (`--hold-hot 200 --hold-max 1
--hold-limit 1`, then the 1.5 s settle), sampler start/stop, post-pass check with bursts_of. The 4.5 s gap (the arm-A
gap) keeps the first burst after the heater clear of the heater guard below, so the smoke shows its bursts kept. It
passes (exit 0) on ok or offclock and always re-runs (earlier smoke directories are moved aside).

## Card minutes (the runner's own bound is in pass.json `max_s`: A 5.4 min, A-H 20.3, B 4.5)

| pass | aifoundry2 (measured 25 Sep, p1-p10) | aifoundry3 (estimate) | aifoundry1-c0 / -c1 (estimate) |
|---|---|---|---|
| A-W / A-C | 4.4-5.3 (heat_to included) | 4.5 | 5-9 (heat_to 76 from a 57-65 C idle: 1-4, 4.5 run) |
| A-H | 5.5-10.2 | 9-16, bound ~25 | 8-16 (heat_to + preheat to 88: 2-6) |
| B | 3.9 | 4 | 5-8 |
| all passes | 52 for 10 blocks, ~57 for 11 (plan: 81) | ~75 (plan: 78) | ~70-110 per card (no plan: amendment) |
| smoke | < 1 | < 1 | < 1 |

Worst case of one block on a governor-free card: heat_to's 150 launches (~9 min) + preheat's 40 (~2.5 min) + the A-H
runner bound (20.3 min) = ~32 min; a W block's 10 min wait for <= 82 C replaces heat_to (the die is then >= 76 C).
Every block stays under the ~35 min limit. PLAN3 2.13: passes of one experiment >= 30 min apart with other experiments'
blocks between; on aifoundry3 the first hot pass (pass 3) must come after V3-IDLE pass 1.

## What is dropped and why (catlib.py; exactly the registered rules, plus the four-card amendment)

- aifoundry2: a burst whose busy samples are not all at mhz.minion = 600 (`mhz_busy_all_600` false: V3-CAT's sampler
  line); or any of whose idle-bracket samples (the before and after windows bursts_of averages for it, cut exactly as
  it cuts them) is off 600 MHz (R-clock, "any sample": idle at 700-800 MHz is 5-9 W higher and would enter the
  burst's over-idle power); or with a launch whose implied clock cycles_max / wall_s is outside 0.595-0.605 GHz
  (R-clock). In the committed 23 Sep data every sample is at 600 MHz and every launch lies in 0.598-0.600 GHz, so none
  of these fires there.
- aifoundry1-c0 and aifoundry1-c1 (governor-free; amendment): a burst whose busy samples are not all at 600 MHz, or
  with a launch whose implied clock is outside 0.595-0.605 GHz; never on idle-bracket samples. Card 0 (firmware 1.4.1)
  was read idle in its "low_power" state at 300 MHz / ~400 mV before any launch, and at 600 MHz (~26 W) after two
  launches (25 Sep 16:40 test); where its brackets sit at 300 MHz the aifoundry2 rule would drop every burst. Its
  first launch after the low-power idle drew no extra power and the clock reached 600 MHz only at its end, so a burst
  that starts from that state is expected to be dropped by the busy-sample or implied-clock rule (the smoke on card 0
  shows whether it is). Every burst records `idle_state`, the clock of its bracket samples ("600", "300", another
  single value, or "mixed:a/b"), and `idle_minion_mv`; a bracket above 600 MHz on aifoundry1 (the governor's lift on a
  cool die) is counted and reported, not dropped, although on aifoundry2 such a bracket is dropped (R-clock): an idle
  5-9 W higher lowers that burst's over-idle power, and `idle_clock` shows how many such bursts a card kept.
- aifoundry3: no clock rule (pinned at 600 MHz; as registered).
- Every card: a burst whose idle brackets (lo - 3.5 s .. hi + 5.5 s, the widest window analyze_catalogue uses) overlap a
  heater launch padded -0.2 s before and +2.3 s after (2.3 s: the settling time analyze_catalogue itself leaves after a
  preceding burst before its idle window starts). This is a guard for the hold-hot design; the runner's `--hold-after
  5.8` and `--heat-settle 1.5` keep it from firing (the next burst's window starts >= 2.8 s after the heater).
- Bursts that `bursts_of` itself cannot cut (too few samples) are listed as dropped.
- Not dropped: bursts with a slow sampler (median took_ms > 60; reported per pass). analyze_catalogue keeps them and
  V3-CAT registered no starvation rule (in the committed data only 3 aifoundry2 DRAM bursts were slow).
- A pass is used when block.json says ok, offclock or partial and it is not a smoke pass. A card with fewer than 3 kept passes in
  a group an item needs leaves that item INSUFFICIENT (R-both).

## Deviations from the plan's commands (each with its reason)

1. **Sampler**: the runner does not start its own ettelem (run_catalogue.py does); block.sh starts it through lib.sh's
   `start_sampler` (retry, drain) and stops it with SIGTERM, as the framework requires.
2. **Timeouts**: `timeout 12` -> `timeout 10` in the prefill and burst calls, and the heater under `timeout 10` (as
   registered); stdin from /dev/null (lib.sh `hold10`). enercat's own `--budget` default (9.5 s) is left alone.
3. **Hold-hot timing**: the plan says "before a configuration's gap, up to 5 heater launches". Placed literally right
   after a burst, the heater would sit inside analyze_catalogue's idle window after that burst (2.3-5.5 s after it) and
   corrupt its idle. So the first heater launch of a configuration waits until 5.8 s after the previous burst ended.
   After the last heater launch the runner waits 1.5 s more (`--heat-settle`) before the prefill and the gap, so the
   next burst's idle window (from 3.5 s before it) starts >= 2.8 s after the heater ended, past the 2.3 s that
   analyze_catalogue leaves after any preceding burst (in the committed 23 Sep telemetry, board power after the end of
   a burst >= 15 W over idle still carries a median 1.7% of the step 1.5 s later on aifoundry2 and 1.0% at 2.25 s).
   Heater and prefill intervals go to marks.jsonl.
4. **Preheat before a hot pass** (at most 40 launches, before the sampler) and **wait for <= 82 C before a warm pass**
   (aifoundry2): not in the plan's command; they put the first configurations of a pass in the registered temperature
   range (W 74-82 C, H 88 C) instead of leaving them to the per-configuration hold.
5. **Arm B seed**: the plan gives none. With `--passes 1` run_catalogue shuffles with `Random(seed + 0)`, so the default
   seed 7 would run every arm-B pass in the same order; the block passes `--seed 30<k>`.
6. **Arm B timing**: the plan's arm-B command has no `--burst`/`--gap`, so run_catalogue's defaults apply (3 s / 5 s),
   which is also what the plan's "~10 s per configuration" cost assumes.
7. **Arm B size**: the eight `--only` prefixes select 23 configurations in run_catalogue.configs() (dramrow2 x 6, tload/dram
   x 3, tstore/dram x 3, tload/scp x 3, l1fill stride32/64 x 2 each, fence x 2, nop x 2), not the plan's "~27".
8. **Heater on aifoundry3**: lib.sh's HEATER, `build/sparsity/host/sparsity_host` (aifoundry3 has no sparsity_t2). Both
   builds come from the same source, workloads/sparsity (CMakeCache), and on aifoundry2 the two binaries have identical
   option sets (`--test fma`, `--type`, `--values randn`, `--per-shire`, default `--budget 8`); the preflight checks the
   aifoundry3 binary's strings for `--per-shire` and `randn`. The heater is needed there only for the A-H passes.
9. **Configurations imported, not copied**: the runner imports `configs()` from `workloads/enercat/run_catalogue.py` of
   the same tree, so its argument lists are the committed catalogue's; an `--only` prefix that selects nothing is an
   error (a stale copy on aifoundry3 would otherwise drop dramrow2 silently); `configs.json` records what ran.
10. **Tree root**: the runner takes `--root` (block.sh passes lib.sh's V3_ROOT) and chdirs there; `--lead` (default 10 s,
    the original's fixed sleep) exists only so the smoke can be short; `--dry`/V3_DRY prints every device command.
11. **Reduction**: analyze_catalogue.py's `bursts_of()` is imported and run on each pass directory (what its main does per
    directory before pooling per card), instead of running its main with `--out` on scratch copies. Checked on the
    committed 23 Sep raw data split into pass directories: every burst value equals catalogue.json's except the first
    and last burst of a pass (12 of 3,492), whose outer idle bracket changes when the neighbouring pass is cut away.
12. **Tmax on aifoundry3** is read from V3-IDLE's telemetry files (the maximum minshire over its passes present at the
    first hot pass), since the plan says only "Tmax-1 from V3-IDLE".
13. **Mid-block etiquette** (not in the plan's command): the runner stops the pass when lib's `others_present` finds
    another user or device process (exit 3; another kernel would also spoil the idle brackets), or when the sampler has
    stopped writing (exit 4: the bursts after it would be unmeasured). The wait-for-cool and preheat loops check
    `others_present` too. The sampler's own `--seconds` is the runner's bound + 300 s, a backstop only (stop_sampler
    ends it).
14. **Card id** (four-card campaign): the runner takes `--card` (block.sh passes lib.sh's CARD) and writes it as each
    runs.jsonl line's `host`, so analyze_catalogue.py, which groups bursts by `host`, keeps aifoundry1's two cards
    apart; on aifoundry2 and aifoundry3 the card id is the hostname, as before. configs.json also records the hostname
    and ET_DEVICES. The runner logs (does not hide) a failure of lib.sh inside its own others_present check.
15. **Idle state record** (four-card campaign): one read-only `ettelem config` at the block's start
    (`config_start.json`), before the temperature step, on every card; the per-burst bracket clock and the settled
    idle power per clock come from the telemetry the block already records.

## How the registered decision rules become outcomes (reduce.py; no new thresholds)

- Unit = pass; 99% two-sided t intervals (Welch where two groups); new passes only; the committed 23 Sep catalogue is
  printed beside under `committed_23sep`, never pooled.
- **CAT-a** per card: s_p = 100 x median over the 30-configuration panel of ln(value / config mean), config mean over the
  card's arm-A passes; Welch 99% on hot vs cool (W on aifoundry2, C on aifoundry3) pass values; dT = difference of the
  pass-mean busy die temperatures; beta = (hot - cool)/dT with the interval divided by dT. Interval excludes 0.21 %/C ->
  "card"; else excludes 0 -> "temperature"; else "not established" (dT <= 0 also gives "not established"). The claims
  hold on a card when it reads "card": both cards -> PASS, one -> CARD-DIFFERENT, none -> FAIL. The card-hypothesis band
  (hot - cool within +-0.5%) is reported as `card_band_ok`. An interval lying wholly above 0.21 still reads "card" (the
  registered rule), with a note.
- **CAT-b**: pass values m_p = 100 x median over the panel of ln(value / aifoundry2-W config mean); Welch 99% of
  aifoundry3-C minus aifoundry2-W as a ratio. For a predicted range with a null, the plan's verifier convention
  (heat-work/exp_test.py) is used: PASS when the interval excludes the null (ratio 1) AND the estimate lies in the
  predicted range (0.936-0.966); else FAIL. The verifier's SIGN-ONLY case (interval excludes the null, estimate
  outside the range) is a FAIL here, and the reading says "sign only" so the page can take the measured value (R-fail);
  the same holds for CAT-e and CAT-f.
- **CAT-c** per card, per operand set: one-way ANOVA over seq/rowhit/rowmiss p > 0.01 AND Welch 99% of rows (per pass, the
  mean of the three patterns) minus tload/dram excludes 0; a card holds when both operand sets do. Both cards -> PASS
  (PROVEN-BOTH), one -> CARD-DIFFERENT, none -> FAIL. The prediction's bands (within 15 pJ/B; rows 13-26% above
  tload/dram, registered for aifoundry3) are reported as `band_ok` and in the reading ("a3 prediction bands: met /
  missed ...; the page takes the measured value"), not used for the outcome, since the registered decision spells out
  its own conjunction.
- **CAT-e**: Welch 99% of tstore/dram/random - tload/dram/random per card. The band (+3.2 +- 3 pJ/B) is registered for
  aifoundry3 only, so the outcome is aifoundry3's (interval excludes 0 and estimate in [0.2, 6.2]); aifoundry2's interval
  is printed beside. PASS here therefore means "holds on aifoundry3", not "holds on both cards"; the page should say
  so for energy-manual-75 (aifoundry2 has no registered band to hold to).
- **CAT-f** per card: fill per byte = 2 x (l1fill/stride64 - l1fill/stride32, random, pJ per 32 B load, same pass) / 64,
  against tload/scp/random pJ/B; Welch 99% of the difference (null: ratio 1); holds when the interval excludes 0 and the
  ratio is in 0.65-0.85. Reported beside as registered "expected within noise": fence vs nop per card (Welch 99%). The
  stride-256 row (energy-manual-102) was dropped from arm B in the plan and is not measured, so that claim stays as it is.

## Four cards (amendment, 25 Sep 2026, before any aifoundry1 data)

aifoundry1 carries two cards, selected with `V3_DEVICE=0|1` (lib.sh exports `ET_DEVICES`, which the host's
deviceLayer honours: the selected card is device 0 to every program, the sampler included); their ids are
`aifoundry1-c0` and `aifoundry1-c1` and each has its own `DATA_ROOT` (`~/nekko/build/claims-v3/aifoundry1-c<n>`).
block.sh exports `V3_DEVICE` so the runner's own `others_present` (which sources lib.sh again) works there too.

- **Design**: both are governor-free (TDP 65 W, temperature threshold 65 C, as aifoundry2), so they run aifoundry2's
  11-block table (W/H arm A, B arm B) with aifoundry2's values: warm passes start <= 82 C after `heat_to 76`, hot
  passes hold 88 C (preheat <= 40 launches, per-configuration hold as on aifoundry2), arm B after `heat_to 76`,
  heater `build/sparsity/host/sparsity_host` (lib.sh HEATER). Nothing known today says otherwise: both report the
  same TDP (65 W) and temperature threshold (65 C) as aifoundry2, whose firmware (1.3.1) governor holds 600 MHz above
  that threshold, which `heat_to 76` puts the die over; card 1 (1.2.0) stayed at 600 MHz under a launch at 57-62 C.
  Three things are not known from source (the cards run releases 1.2.0 and 1.4.1, not 1.3.1) and are measured, not
  assumed: whether each card keeps 600 MHz under load above 65 C (the busy-sample and implied-clock rules decide per
  burst), when card 0 falls back to its 300 MHz low-power idle (recorded per burst), and how hot the cards get (the
  reduction uses the measured busy die temperatures, so a hold that falls short shrinks dT, it does not bias beta).
  The die reading is minshire[0]; card 0's 123 C peak-hold value (minshire[2]) is not used.
- **Leakage correction**: analyze_catalogue.py's own (aifoundry2's idle law, A80 23.3 W, T_L 36 C) on every card, as
  the 23 Sep catalogue applied it to aifoundry3; it corrects only the busy-minus-idle temperature difference.
- **Drops**: busy samples and implied clock only (above). The idle-bracket clock is recorded per burst and reported.
- **Idle state**: card 0 was read at 300 MHz / 398 mV (18.8 W board, "low_power") before any launch, and idled at
  600 MHz / ~26 W after two launches in a 16:40 test (how long it stays there is not known); card 1 idles at 600 MHz /
  499 mV (32.9-35 W). Which state card 0's brackets sit in during a pass is measured, not assumed. Where they sit at
  300 MHz, a burst's energy over idle includes the step from the low-power idle to the 600 MHz operating point, not
  only the work, and its catalogue values are not comparable with the other cards'. The step is a roughly constant
  number of watts, so it adds a different pJ/B (or pJ/op) to configurations with different rates, and dilutes
  CAT-a's hot/cool ratio. A tested card whose kept brackets in an item's passes are mostly (more than half) off
  600 MHz is still tested as registered for CAT-a, CAT-c and CAT-f, but reduce.py lists it under
  `all_cards.idle_caveat`, and its holds / fails is not read as evidence for or against the claim (the page says so;
  the outcome is not changed). Every item carries `idle_clock` (per card: bracket states, the power state at each
  block's start, the settled idle board power per clock) and the page must state it when a card's idle differs. At 600 MHz the three firmwares idle at different powers (1.4.1 ~26 W, 1.2.0 33-35 W,
  1.3.1 ~32 W at 74 C); over-idle values subtract each card's own idle, so this does not enter them.
- **Outcomes**: every item keeps its registered `outcome` from aifoundry2 and aifoundry3, computed exactly as before
  (tested: identical output on the 23 Sep legacy data, the real 25 Sep aifoundry2 passes and every earlier synthetic
  set). Each item adds `all_cards`: the item's per-card rule on every campaign card; PASS on every card, CARD-DIFFERENT
  on some, FAIL on none, INSUFFICIENT when a card lacks 3 kept repeats or has no data (`with_data` then gives the
  outcome over the cards that have them). CAT-a (per card, cool = W on a governor-free card), CAT-c (per card; the
  bands, registered for aifoundry3, stay `band_ok` reports on every card) and CAT-f ("on each card") apply unchanged.
  CAT-b's band is registered for the pair cool aifoundry3 / warm aifoundry2 and CAT-e's for aifoundry3 only: on
  aifoundry1's cards they are REPORTED (CAT-b: each card's W passes against aifoundry2-W as a ratio with its 99%
  interval; CAT-e: tstore - tload per card), not tested, and their `all_cards` outcome is the registered one.
- **Repeats**: aifoundry2's design gives 3 arm-B passes, the minimum; one burst of a CAT-c/e/f configuration dropped
  on a card leaves that card INSUFFICIENT until the pass is re-run (the queue re-runs an `offclock` pass when the
  schedule is run again).
- **Two cards in one chassis**: the two aifoundry1 queues may run at once (lib.sh's `ours_running` is per card), so
  one card's heater can warm the other. Nothing is dropped for it: the die temperatures are measured per burst, and
  CAT-a's dT uses them.

## How to reduce

Collect every card's `DATA_ROOT` into one directory laid out as `<dir>/<card>/cat/p<N>/...` (e.g.
`rsync -a aifoundry3:nekko/build/claims-v3/aifoundry3/cat <dir>/aifoundry3/`,
`rsync -a aifoundry1:nekko/build/claims-v3/aifoundry1-c0/cat <dir>/aifoundry1-c0/`, the same for `-c1`), then

    python3 tools/claims-v3/cat/reduce.py --data <dir> --out verdicts.json [--committed none]

It reads every `<card>/cat/` present, prints two lines per item (registered, all_cards; a third when a card's idle
differs) and writes `{"exp", "cards", "rules", "passes": {card: [...]}, "items": [{"item", "claims", "per_card",
"test", "outcome", "reading", "all_cards": {"outcome", "scope", "tested", "cards", "with_data", "reading",
"idle_caveat"},
"idle_clock", "committed_23sep"}]}` (a page builder that expects a bare list reads `.items`). It runs on partial data
(one card, fewer passes: those items say INSUFFICIENT). Tested on the committed 23 Sep raw data laid out as passes and
on synthetic data with known effects (scratchpad `validate3/drv/cat/`: mk_legacy.py, mk_synth.py; the review's
all-fail scenario and drop-rule mutations: mk_review.py, rev-*), and on four-card synthetic data
(`validate3/fourcards/cat/mk_synth4.py`: every item holding on all four cards; aifoundry1-c0 different; aifoundry1-c1
missing; aifoundry1-c0 short of repeats; card 0's 300 MHz brackets kept, off-clock busy samples dropped).
