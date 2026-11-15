# Request 1113-x04-clock: wait against spin, and which part of the clock a user program wakes

Family X04 (the clock). Designer: ee-x04-clock. Written Fri 13 Nov 2026; **revision 2** the same day, after two
independent reviews (isolation, physics and statistics; public safety and feasibility). Source: `src/` (public,
card-only build; name scan `HITS 0`). Forecast: `prediction.json` (never pushed; sha256 in `log.md`, which keeps the
superseded first freeze's line). Private reasoning (why each arm has its shape, how the forecast was made): the
designer's own dir, not here. Only the forecast's sha256 stands for it here.

## 0. What changed in revision 2

**Safety fix (after the two independent reads of revision 2, same day).** `src/run_x04.py`, `src/host/main.cpp`
and `src/README.md` changed; the kernel, `arms.tsv`, the reducer and the forecast did not (their registered hashes
stand). The runner now: counts the device nodes and refuses unless `/dev/et<N>_ops` is the only one (the host checks
the same before it opens the device, and refuses a `--budget` over 9.5 s); runs the lab's holder check
(`et-who --check`; since fix 2, only the session's sampler, by process id, is exempt) and probes the card lock before the sampler opens
the management node and before every block, waiting at most 10 minutes; opens the lock file read-only, as
`flock(1)` does, never truncating it; requires the lock (default from `--device`) and a stop file (default
`OUT/STOP`); launches nothing for 30 s between passes, lock released; runs every device process under `timeout -k 1 10`; stops
its sampler with SIGTERM in every case, also when it is itself stopped by a signal; stops on the clock only after
three samples in a row off 600 MHz (as for the board); marks a train that did not get all its launches `ok: false`,
so the reduction drops it. Forecast-derived signal sizes were taken out of section 6.

**Safety fix 2 (after an independent read of the first fix, same day).** Only `src/run_x04.py` and `src/README.md`
changed; the kernel, `arms.tsv`, the reducer and the forecast did not. When the runner is stopped by a signal while a
device process runs, it now ends that process (SIGTERM to its `timeout`, which kills it 1 s later) and waits for it
before it releases the card lock; the signal handler sets the ignores first and the clean-up runs with the signals
blocked. The holder check no longer exempts holders by user: the one exempt holder is the session's sampler, by
process id, on this card's management node (with `--telemetry`, the process given by `--telemetry-pid`, which must
have the file open for writing). Between blocks and passes the lock file is closed, not only unlocked.

- **The firmware's post-launch wait.** In the open worker firmware, every thread that returns from a kernel empties
  its credit counters and then blocks in a credit barrier with all 64 threads of its shire until the last one
  returns; only after that does it go back to the idle park (`wfi`). So during a launch every non-working hart of a
  launched shire sits in a credit wait, and the first draft's "wait against the park" pair (`wait2 - tk`) compared a
  credit wait with a credit wait. Now: `tk` is run on 2, 11, 21 and 32 launched shires (the shires left out stay in
  `wfi`), so the slope prices a shire of credit-waiting harts against a shire in the park; three launch lengths
  bound the per-launch work; `wait2 - tk` is registered as a null (a user credit wait against the firmware's); the
  pure nulls `wait1` and `spin1w` are gone. **The operator should confirm that the card's worker firmware has the
  same post-launch barrier** (the open source is the evidence here; the build on the card is unseen).
- **No heater.** The anchor could not hold a 57-58 C start; runs now start from the card's own idle (an idle-down
  wait to the session's idle reading + 2 C, at most 30 s, logged), and temperature is taken out by the leakage law.
- **Start handshake** (no hart can stay blocked): see section 9.
- **One body for the duty ladder** (64 slots, with `duty100` as its top), awake fraction measured in cycles.
- **Worker ladder** (7, 15, 23, 31 workers a shire) and a packed-against-spread pair: per core against per
  neighbourhood.
- **Lone pairs as A B B A trains** inside one device process: one hart against none, one against two, a divide chain,
  `fadd.s` against `fadd.ps`, packed against spread, spread against clustered `fadd.ps`.
- **Mask ladder** (`m0` = 1, 2, 4, 8 lanes at P = 1) in place of the single mask arm at P = 16.
- **Rails fitted through the meter's filter** (tau 1.05 s) instead of windowed; stops, dip rule, clock check and the
  registered checks are now in the code.

## 1. The question

What does an awake core cost per core-cycle, by the part of its clock a user program can switch on?

1. **A waiting hart against the firmware's idle park.** A user-mode hart cannot run `wfi` (PRM 1.3). Does a hart
   blocked on a fast credit (`csrw fcc`, PRM ch. 11; the firmware's own post-launch wait) cost what the idle park
   costs, or what a stalled, awake core costs (the lab's E23 row: 1,024 minions stalled on a contended atomic,
   1.19 W over idle)? Measured as the slope of `tk` over launched shires, and by the duty ladder's intercept, and by
   the train `tk | spin1`.
2. **The awake core per cycle, independent of duty**: a duty ladder of no-op spin against credit wait (awake
   fraction about 0, 1/3, 2/3, 1, measured in cycles); slope = awake price per core-cycle, intercept = waiting
   price; the same duty at 16 and 64 times shorter periods prices or bounds a wake.
3. **Per core or per neighbourhood**: the worker ladder's slope and its last step (the one that wakes no further
   neighbourhood), and 8 workers packed against spread.
4. **Each instruction class per cycle, at equal issue**: one instruction of a class in every P issue slots of a
   no-op stream (P = 1, 2, 4, 8, 16), on zeros: `fsgnj.s`, `fadd.ps`, and `fadd.s` at P = 16; `fadd.ps` with `m0` =
   1, 2, 4 lanes; `fadd.ps` at 1/8 density spread against in a row: the price per class instruction at each
   density and in each order.
5. **One hart against two**, and a dependent divide chain.

New against what the lab ran: the awake core (spin h1/h2), the no-issue floor (E109, E129, E148, E155) and the full-
rate catalogue are priced; a launched-shire ladder of the firmware's wait, a wait-against-spin duty ladder, a worker
ladder by neighbourhood and an instruction-class density ladder are not. `spin2` repeats the catalogue's two-hart
**no-op** row (`nop`, 2.496 W, not the `spin` row) as this run's anchor; `faddps_p1` and `fsgnjs_p1` repeat two
catalogue rows on 992 worker minions: a check of the meter's scale.

## 2. Arms and ladder steps (`src/arms.tsv`)

Workers: minions 1..31 of all 32 shires (992 minions) unless an arm says otherwise. Minion 0 thread 0 of every
launched shire is the timekeeper in every arm (a cycle-counter loop; in the arms that wait it stores one credit per
period into the shire's `CREDINC` registers). Launches are 0.4 s (240,000,000 cycles) unless an arm says otherwise.

| block | arm | what every worker does | host options |
|---|---|---|---|
| anchor | spin2 | both harts: 512-slot no-op sled | `--arm spin --t1 same` |
| S | tk_s2, tk_s11, tk_s21, tk | return at once (firmware's credit wait); 2, 11, 21, 32 shires launched | `--arm tk --t1 off [--shires 0x3 / 0x7ff / 0x1fffff]` |
| S | tk_l100, tk_l200 | as `tk`, launches of 0.1 and 0.2 s | `... --window 60000000 / 120000000` |
| D | wait2 | both harts in a user credit wait (one credit per 65,536 cycles): duty 0 | `--arm wait --t1 same` |
| D | duty33, duty67, duty100 | per 65,536-cycle period: credit wait, then the 64-slot sled for 33 / 67 / 100 % | `--arm duty --t1 same --duty-pct 33 / 67 / 100` |
| D | duty33f, duty33k | as duty33 with 4,096- and 1,024-cycle periods | `... --period 4096 / 1024` |
| W | w7, w15, w23 | spin2 on 7, 15, 23 workers a shire (minions 8 up: neighbourhoods 1, 2, 3 first) | `--arm spin --t1 same --minions 0x7f00 / 0x7fff00 / 0x7fffff00` |
| T | tr_tk_spin1 | A: `tk`; B: hart 0 no-ops, hart 1 returns | `--seg-launches 3 --arm tk --t1 off --then --arm spin ...` |
| T | tr_spin1_spin2 | A: one hart of no-ops; B: two | |
| T | tr_tk_stall2 | A: `tk`; B: both harts, dependent 64-bit `div` chain on zeros | |
| T | tr_faddps_fadds | A: `fadd.ps` every slot; B: `fadd.s` every slot | |
| T | tr_packed_spread | A: 8 workers in neighbourhood 1; B: 8 spread 3/3/2 over 1-3 (both harts no-ops) | `--minions 0xff00` / `0x03070700` |
| T | tr_spread_cluster | A: `fadd.ps` one in every 8 slots; B: the same 64 `fadd.ps` in a row, then 448 no-ops | `--every 8` / `--every 8 --cluster` |
| C | faddps_p1, p2, p4, p8, p16 | both harts: one `fadd.ps` in every P slots, no-ops between | `--arm mix --cls fadd_ps --every P --t1 same` |
| C | fsgnjs_p1, p2, p4, p8 | the same with `fsgnj.s` | `--cls fsgnj_s` |
| C | fadds_p16 | the same with `fadd.s`, P = 16 | `--cls fadd_s` |
| C | faddpsm1_p1, faddpsm2_p1, faddpsm4_p1 | `fadd.ps` every slot with `m0` = 0x01, 0x03, 0x0f | `--mask` |

34 arms plus the anchor; six of them trains (A B B A, three 0.4 s launches a segment, one device process).
Ladders: tk over shires (4 points), tk over launch length (3, a bound), duty (`wait2`, `duty33`, `duty67`,
`duty100`), workers (`w7`, `w15`, `w23`, `spin2`), `fadd.ps` density (`spin2` and P = 16 .. 1), `fsgnj.s` density
(`spin2` and P = 8 .. 1), mask lanes (1, 2, 4, 8).

## 3. Card, clock, cores

lab host 3 card 0 (the reference card): 600 MHz pinned, mesh 400 MHz, as it is; nothing set. No voltage,
frequency, firmware, governor or fan change; no root. Blocks S and D (every arm below 2.5 W over idle) would fit
lab host 1 card 0 ("low-power runs only"), but its governed clock steps on a busy launch: lab host 3 is asked for.

## 4. What is measured

Board power (`board_w`, 12 V input) and the minion, SRAM and mesh rails with their millivolts (`sp.*_w`, `sp.*_mv`),
`temp_c.minshire`, `mhz.minion`: one `ettelem sample --every-ms 100` for the whole session (the lab session's own,
`--telemetry FILE --telemetry-pid PID`, or one started by the runner, `--sampler`, never both). On this card, the per-sensor temperature
codes (`pvt_sample.py`, read-only) if the lab session agrees to record them beside the sampler; the reducer reads them
with `--pvt`. Electrons per event on a rail = (rail W over idle / rail V) / (e x events per s).

## 5. Protocol (`src/run_x04.py`)

- Two sessions, each standing alone: **A** = blocks S, D, W, T; **B** = block C. Each: 9 passes, pass 0 a
  registered warm-up set aside. Each pass: the anchor `spin2` at every block boundary (first in each block, and once
  more at the end of the pass), the block's arms in a seeded shuffled order (seed 1113 x pass x block).
- Each run: idle-down (die reading at most the session's idle reading + 2 C, at most 30 s, logged), 5 s idle gap,
  then one device process under `timeout -k 1 10` (budget 9.5 s from the device's opening; a launch starts only if it
  can finish, its 2 s wait included, inside the budget): 4 s of 0.4 s launches, or a train of 12 launches.
- Board: burst seconds 0.5 to the end (the lab's method); train segments: from 0.5 s after the segment's first
  launch to its last launch's end. Rails: fitted per run through the meter's first-order filter (tau 1.05 s, 1.5
  meter passes late), with the input constant on each interval (idle before, burst or segment, idle after).
- One card: `--device 0` (exported as `ET_DEVICES`); the runner and the host refuse unless `/dev/et0_ops` is the
  only ops node. Before the sampler starts and before every block: the lab's holder check (`et-who --check`) and the
  card lock (`flock -n` on `/run/lock/etsoc-shire0.lock`, opened read-only), waiting at most 10 minutes, then a stop.
  The only holder exempted is the session's sampler, by process id, on the card's management node; any other holder,
  of any user, means the card is taken. The lock is held per block, unlocked and closed between blocks; between
  passes nothing is launched for 30 s with the lock closed (the sampler keeps the management node). Stopped by a
  signal, the runner ends a running device process (SIGTERM to its `timeout`) and waits for it before releasing the
  lock, then stops its own sampler. Stop file
  (default `OUT/STOP`) and deadline before every run; `--smoke` = one short pass of five arms (2 s bursts, one
  train); `--dry` prints every device call and check and opens nothing. The lab session's own `lib.sh` checks, preflight and smoke as it kits the run; if it
  wraps the runner in its session script, pass `--telemetry` with its sampler's file and `--telemetry-pid` with that
  sampler's process id, so that nothing here opens the management node.
- **Card time** (lock held, device opening counted at 1.5 s a process): session A 26 runs a pass x 9 = **about 42
  card-minutes**; session B 15 runs a pass x 9 = **about 24 card-minutes**; plus a smoke (about 1 minute) and any
  idle-down waits. About 70 card-minutes in all, in two sittings (plus 4 minutes of pass gaps a sitting, nothing launched).

## 6. Events per second, and the signal budget

At 600 MHz: worker minion-cycles 992 x 6.0e8 = 5.95e11 per s (W ladder: 7, 15, 23 x 32 x 6e8). Slots issued per
second (catalogue issue rates on this card): `spin2` and every `mix` arm about 4.64e11 (0.39 per hart-cycle); class
instructions 4.64e11 / P per s; the duty arms' awake fractions are about 0.33, 0.67, 1 (stamped in cycles); credits
9.1e6 per s (65,536-cycle period), 1.45e8 (4,096), 5.8e8 (1,024); launches 2.5, 5, 10 per s. The card's own counts
replace all of these (section 7).

Steps against the floor (top-down scale, from the lab's public catalogue; floor 0.032 W rms about a ladder line,
E60's eight passes of 4 s runs): the smallest pricing-ladder steps are 0.33 W (workers, if a waiting hart costs the
stalled price), 0.34-0.41 W (tk over shires, same condition), 0.37 W (duty), 0.46-0.49 W (the class ladders'
sparse end): each at least 10 times the floor. Two ladders are judged by their fitted slope, not a single step: the
mask ladder (slope standard error about 0.006 W a lane, from the floor) and the launch-length ladder (a bound on
the per-launch work). Trains: the floor of an A B B A contrast is about 0.011 W over eight passes (Estimated: about
2.7 board readings a segment); a contrast is read against that floor, or reported as a registered null.

## 7. Denominators, and how they are read

Every launch prints `X04 {json}`: per thread the workers that reported, slots issued (loops x 512, or x 64 in the
duty sled), awake cycles (duty arms: each hart stamps the cycle counter at each wake and at the sled's exit), credits
taken (must equal periods x waiting threads) and drained at start, the timekeeper's credits and handshake cycles,
late and bailout flags, cycles per hart (`hpmcounter3`), and, read by thread 0 of minions 0, 8, 16, 24 at its end
with the four-read safe form after its own thread 1 is done, `hpmcounter4/5` (retired instructions per thread over
the neighbourhood's 8 minions) and `hpmcounter7/8` (I-cache requests and misses): checks only. Worker minion-cycles =
workers x cycles; class instructions = slots / P; the duty arms' awake fraction = awake cycles / (harts x cycles);
the train segments carry their own slot rates (equal issue in each pair is checked there).

## 8. Sanity checks (registered before data; computed by `src/reduce_x04.py`)

1. `spin2` against the catalogue's two-hart **no-op** row on this card (2.496 W), scaled by 992/1024: within 15 %.
2. `faddps_p1` and `fsgnjs_p1` against their catalogue rows (10.212, 6.122 W), scaled: within 15 %.
3. Anchor drift between block boundaries under 0.1 W; a block above is flagged (and the anchor-detrended values
   reported beside the plain ones).
4. Every launch `ok` (all workers reported, none late, credits balanced); a run with a failed launch is dropped.
5. `mhz.minion` 600 in every busy sample; a burst with any other clock, or with the field missing, is dropped.
6. Duty ladder linear in the measured awake fraction: residuals of the line through its four points under 0.05 W.
7. Nulls, reported with their intervals: `wait2 - tk`, `fadds_p16 - faddps_p16`; `duty33f` and `duty33k` off the duty
   line (a price per wake, or its bound).
8. Dip rule: a board reading more than 4 W below its window's median is dropped.
9. `stall2` is called a stalled pipeline only if its divides per hart-cycle come out well below the no-op issue rate;
   otherwise it is a divide issue loop, and named so.

## 9. Constraints and what must not be done

- **No hart can stay blocked.** Every credit wait has its partner in its own shire. Each waiting thread empties its
  counter and reports ready (a local atomic in a host buffer, tagged with the launch's epoch); the timekeeper starts
  its periods only when every waiting thread of its shire has reported (or after 6,000,000 cycles), then writes the
  go word; a thread that finds the go word already written skips its waits and flags itself (the host then exits 3:
  nothing blocked, the launch not counted). The timekeeper sends three spare credits at the end and waits 4,096
  cycles; the firmware empties the counters after the kernel, and its barrier tolerates a stray credit.
- **Stops, in the code**: a device process that exits 1 or any unexpected status, or is killed by `timeout`, stops
  the session (a launch that did not finish: tell the lab admin; a hung hart needs a card reset); three incomplete
  launches stop it; on the telemetry: board above 65 W on three samples in a row, die at or above 70 C, minion clock
  other than 600 MHz (or missing) on three samples in a row, or a stalled sampler; a card not free for 10 minutes
  before a block. The stop file is checked before every run. There is no heater, so nothing of ours warms the die
  toward a stop; the stops sit far above every arm (section 9, last point).
- Never on two cards of one host at once (the runner and the host refuse a host with more than one card node);
  never beside another session of ours on lab host 1.
- No host compute beside the run; build on the box in a folder of ours (`~/claude/work/ee-1113-x04-clock/`), never in
  the lab session's trees. The sampler is the lab repo's `tools/ettelem`, read from the lab's checkout and built into
  the same folder of ours (`src/README.md`).
- The `fadd.ps` P = 1 arms put the board about 10 W over idle for 4 s: far below every stop.

## 10. Builds and the emulator (evidence that it runs)

- `src/` builds with the open SDK on this box (`cmake -S src -B build -DCMAKE_PREFIX_PATH=/opt/et`): kernel and host,
  no warnings from the sources. The kernel ELF is byte-identical to the one built with the simulator's device layer
  added (the designer's private copy), sha256 `bd5770bab12f2b39379960b434af2dfe5cf46f2e75278a26580d5694c03be2ec`.
- Every arm ran in the open system emulator, one shire unless the arm launches more (31 workers), short windows
  (24,576 cycles; credit periods divided by 16, at least 1,024; one launch a train segment): one boot, all arms.
  The emulator has no timing model (one slot per cycle per hart), so only its counts carry over, and its clean
  handshake does not test launch skew (the handshake does, on the card).

| arm | seg | shires | workers t0/t1 | window cycles | slots issued | awake cycles | credits taken / drained | tk credits | handshake cycles | late | retired, thread 0 (4 nbhd counters) | ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| spin2 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 815071 | yes |
| tk_s2 |  | 2 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 60860 | yes |
| tk_s11 |  | 11 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 334828 | yes |
| tk_s21 |  | 21 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 638732 | yes |
| tk |  | 1 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 30412 | yes |
| tk_l100 |  | 1 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 30412 | yes |
| tk_l200 |  | 1 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 30412 | yes |
| wait2 |  | 1 | 31/31 | 24576 | 0 | 0 | 372 / 0 | 6 | 1043 | 0 | 51982 | yes |
| duty33 |  | 1 | 31/31 | 24576 | 452352 | 509268 | 372 / 0 | 6 | 1043 | 0 | 308816 | yes |
| duty67 |  | 1 | 31/31 | 24576 | 928512 | 1044948 | 372 / 0 | 6 | 1043 | 0 | 576656 | yes |
| duty100 |  | 1 | 31/31 | 24576 | 1357056 | 1527060 | 0 / 0 | 0 | 0 | 0 | 808983 | yes |
| duty33f |  | 1 | 31/31 | 6144 | 119040 | 134292 | 372 / 0 | 6 | 1043 | 0 | 102896 | yes |
| duty33k |  | 1 | 31/31 | 6144 | 119040 | 134292 | 372 / 0 | 6 | 1043 | 0 | 102896 | yes |
| w7 |  | 1 | 7/7 | 24576 | 344064 | 0 | 0 / 0 | 0 | 0 | 0 | 210171 | yes |
| w15 |  | 1 | 15/15 | 24576 | 737280 | 0 | 0 / 0 | 0 | 0 | 0 | 414851 | yes |
| w23 |  | 1 | 23/23 | 24576 | 1130496 | 0 | 0 / 0 | 0 | 0 | 0 | 619531 | yes |
| tr_tk_spin1 | A | 1 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 30412 | yes |
| tr_tk_spin1 | B | 1 | 31/0 | 24576 | 761856 | 0 | 0 / 0 | 0 | 0 | 0 | 814284 | yes |
| tr_tk_spin1 | B | 1 | 31/0 | 24576 | 761856 | 0 | 0 / 0 | 0 | 0 | 0 | 814284 | yes |
| tr_tk_spin1 | A | 1 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 30412 | yes |
| tr_spin1_spin2 | A | 1 | 31/0 | 24576 | 761856 | 0 | 0 / 0 | 0 | 0 | 0 | 814284 | yes |
| tr_spin1_spin2 | B | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 815199 | yes |
| tr_spin1_spin2 | B | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 815199 | yes |
| tr_spin1_spin2 | A | 1 | 31/0 | 24576 | 761856 | 0 | 0 / 0 | 0 | 0 | 0 | 814284 | yes |
| tr_tk_stall2 | A | 1 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 30412 | yes |
| tr_tk_stall2 | B | 1 | 31/31 | 24576 | 1357056 | 0 | 0 / 0 | 0 | 0 | 0 | 807135 | yes |
| tr_tk_stall2 | B | 1 | 31/31 | 24576 | 1357056 | 0 | 0 / 0 | 0 | 0 | 0 | 807135 | yes |
| tr_tk_stall2 | A | 1 | 0/0 | 24576 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 30412 | yes |
| tr_faddps_fadds | A | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| tr_faddps_fadds | B | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816183 | yes |
| tr_faddps_fadds | B | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816183 | yes |
| tr_faddps_fadds | A | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| tr_packed_spread | A | 1 | 8/8 | 24576 | 393216 | 0 | 0 / 0 | 0 | 0 | 0 | 235015 | yes |
| tr_packed_spread | B | 1 | 8/8 | 24576 | 393216 | 0 | 0 / 0 | 0 | 0 | 0 | 246876 | yes |
| tr_packed_spread | B | 1 | 8/8 | 24576 | 393216 | 0 | 0 / 0 | 0 | 0 | 0 | 246876 | yes |
| tr_packed_spread | A | 1 | 8/8 | 24576 | 393216 | 0 | 0 / 0 | 0 | 0 | 0 | 235015 | yes |
| tr_spread_cluster | A | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| tr_spread_cluster | B | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 815967 | yes |
| tr_spread_cluster | B | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 815967 | yes |
| tr_spread_cluster | A | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| faddps_p1 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| faddps_p2 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| faddps_p4 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| faddps_p8 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| faddps_p16 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| fsgnjs_p1 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816255 | yes |
| fsgnjs_p2 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816255 | yes |
| fsgnjs_p4 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816255 | yes |
| fsgnjs_p8 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816255 | yes |
| fadds_p16 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816183 | yes |
| faddpsm1_p1 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| faddpsm2_p1 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |
| faddpsm4_p1 |  | 1 | 31/31 | 24576 | 1523712 | 0 | 0 / 0 | 0 | 0 | 0 | 816087 | yes |

53 launches, 35 arms, 0 not ok

  Read: every launch complete, nobody late, credits balanced in every waiting arm (372 = 6 periods x 62 threads; the
  timekeeper's handshake took about 1,000 emulated cycles); the duty arms' stamped awake cycles over (62 harts x the
  window) are 0.334, 0.686 and 1.002 for duty33, duty67 and duty100, and 0.353 for the short periods; slots per
  worker-hart are the window in the spin and class arms (one slot per cycle in the emulator) and scale with workers in
  the W arms (7, 15, 23 a shire); the clustered and spread bodies issue the same slots; the `tk` arms retire only the
  timekeepers' loops (30,412 a shire, so 2, 11 and 21 shires give 2, 11 and 21 times one). The emulator reads
  `hpmcounter5`, `7` and `8` as 0 (not modelled): on the card they are read as they are. Run: one boot (114 s), then
  35 arms and 53 launches in about 165 s of wall time.

## 11. Status

`draft`. Every point of both reviews is answered in the code, the protocol or the forecast (section 0; the safety
points: the start handshake, the three spares, the stops in code, the safe counter reads; `src/` scans `HITS 0`), the
source builds here with the open SDK, and every arm ran in the open emulator with the counts above; the forecast is
re-frozen (`log.md`). Not yet `ready` because `src/` changed in every file after the reviewers' line-by-line read, so
BRIEF section 10's independent read of `src/` has to be done again (the safety fixes of section 0 changed the runner,
the host and the README once more). Open for the operator: confirm that the card's
worker firmware has the post-launch credit barrier; whether the lab session records the per-sensor temperature codes;
the lab hosts are written "lab host 1" and "lab host 3" here and in `PROPOSAL.md` (the operator may put the lab's own names back); card time (about 70 card-minutes in two
sittings; lab host 3 is spoken for tonight: E183, then E189). The forecast stays on this box (only its sha256 goes
into the proposal).
