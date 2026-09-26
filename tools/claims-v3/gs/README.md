# V3-GS: gathers, scatters and packed atomics on three cards (E48)

The owner asked on 25 Sep 2026: "After prev measures done, perform comprehensive throughput measurements for gather
and scatter on all of the cards and insert it into an appropriate location." This experiment measures the rate
(elements per second, cycles per instruction) and the energy (pJ per element) of the vector unit's indexed memory
instructions (gathers, scatters, their L1-bypassing and 32-byte-block forms, the packed atomics) and of the scalar and
scatter-add baselines on the same address streams. The measurement matrix and the model it tests are in the design
(`DESIGN.md`, written 25 Sep before any code, in the session scratchpad `gathscat/`); these rules are fixed here before
any gs data exists. Suggested experiment number: E48 (the design said E47, but `docs/reports/data/2026-09-25-claims-v3/
PLAN3.md` already suggests E35-E47 for the claims-v3 experiments, E47 for horace-lowpower X3; take the next free
number when the run is recorded in `docs/findings/03-experiments.md`).

| file | what |
|---|---|
| `block.sh` | one block: `bash tools/claims-v3/gs/block.sh <KS> [--smoke]` (K = pass 1-9; S = 0 check, 1 energy, 2 rate) |
| `run_gs_t10.py` | the runner: V3-CAT's `tools/claims-v3/cat/run_catalogue_t10.py`, unchanged, on the gs configurations |
| `gslib.py` | the plan per block, the post-block checks (C, E, R, smoke), the missing-launch list |
| `reduce.py` | the items below, per card and over the cards: `reduce.py --data <dir> --out verdicts.json --gs-out gs.json` |
| `../schedule-gs-<card>.txt` | the queue schedules for aifoundry2, aifoundry3, aifoundry1-c1 |

The device code and host are `workloads/enercat` built with `-DENERCAT_GS=ON` into **`build/enercat_gs`** (the
catalogue's `build/enercat` and `build/enercat_v2` are never rebuilt with it; without the option the kernel ELF is
byte-identical to the committed catalogue's). The configurations are `workloads/enercat/gs_catalogue.py`; the
generated tables and kernel cases come from `workloads/enercat/gen_gs.py`; the analysis is
`workloads/enercat/analyze_gs.py`, which cuts bursts with catfull's `cflib.pass_bursts` (and so
`analyze_catalogue.bursts_of`), both imported unchanged.

## Build (each host, from its own tree)

```
cmake -B build/enercat_gs -S workloads/enercat -DCMAKE_PREFIX_PATH=/opt/et -DENERCAT_GS=ON -Wno-dev
nice cmake --build build/enercat_gs -j4
```

The host binary compiles in the path of its own kernel ELF (`build/enercat_gs/kernel/enercat.elf`); block.sh checks
that both exist, that the host knows `--gs-index` and that the kernel has `gs_run`.

## What a launch does

Every participating hart walks a table one tile at a time (k <- (k + P) mod ntiles, P odd so ntiles visits cover every
tile once; the walk starts on a different tile per hart) and issues eight indexed instructions per visit on the tile
base. The index vectors (f0-f7) hold 64 signed 32-bit byte offsets from one of seven patterns (unit, s2, s4, s16,
line, rand, bcast; `enercat_gs.h`). The timed loop runs eight visits between deadline checks (enercat's 0.4 s window);
a verify launch (`--verify N`) runs exactly N visits and the host checks: every gathered vector of every visit (a
masked-off lane must keep the sentinel), the whole table after scatters and scatter-adds for 16 sampled harts (all when
fewer), every counter of a shared table after atomics (no lost update), the old values a private famo returns (lane
order), the scalar loads' sum, the probe's cases. Tables: private per hart in DRAM (filled by DMA with a hash of
(hart, word) as floats in [0.5, 1), or zeros), the hart's 16 KB of its own shire's scratchpad or of a shire 2 hops away
(copied in by the kernel at every launch with a global store), or a shared counter table per shire (256 KB) or per
chip (8 MB) for the atomics. Tables of up to 64 KB are warmed by one untimed walk (not for the atomics).

What "rand" means, for the reports: within a visit the 64 elements fall on the 64 distinct lines of one 4 KB tile, in a
fixed random order (one random word per line), and the walk visits the tiles in a scrambled order (step ~0.618 x the
number of tiles). So a "random" gather at 4 KB per hart repeats the same 64-line cycle every visit (it thrashes the
8-line L1 and hits the L2), and at 256 KB per hart it is random lines within 4 KB tiles, the tiles in scrambled order,
2,048 such streams at once: not independent uniform addresses over the table. The `lines_per_instr` a launch reports
is distinct lines per visit over instructions per visit, computed from the offsets actually used (rand folded into a
256 B / 512 B / 1 KB table touches 4 / 8 / 16 lines a visit, not 64), and it is what line bytes/s and pJ per line use.

Refusals before any launch (host): an atomic on a scratchpad (a bus error on silicon), a shared table for anything
but the atomics (the L1 is not coherent), every lane of a shared table on one word (hot line), an offset outside its
tile or not aligned to the element size, a scratchpad table over 16 KB per hart, a gs mode with no table (it would
write physical address 0).

## Blocks, passes, the schedule

| block | set | configurations | timing | typical | bound (runner) |
|---|---|---|---|---|---|
| `gs 10` | C | 159: one verify launch per E and R configuration (sets CE, CR) and the semantic probe (CP) | `--burst 0 --gap 0.3 --lead 0`, no sampler | ~6 min | 8 min |
| `gs K1` | E | 101 at 1,024 minions | `--burst 3 --gap 4.5` (E27), sampler, preheat >= 76 C on governor-free cards | ~16 min + preheat | 18 min + preheat |
| `gs K2` | R | 57 at 1 minion, 32 in one shire, 32 spread | `--burst 1 --gap 1`, sampler, preheat; on governor-free cards the runner's hold (`--hold-hot 74 --hold-max 3 --hold-after 0 --heat-settle 0.3`: heater launches before a configuration while the die is under 74 C) | ~4 min (+ any hold) | 18 min with every hold |
| `--smoke` | smoke | 8 (four timed, four verified) | `--burst 1 --gap 4.5 --lead 3`, no heater | ~1.5 min | 2 min |

Schedule per card (`tools/claims-v3/schedule-gs-<card>.txt`): `gs 10`, `gs 11`, `gs 12`, `sleep 900`, `gs 21`, `gs 22`,
`sleep 900`, `gs 31`, `gs 32`, `end`: about 70 min of card time and 1.5 h of wall time. It starts only after the card's
current queue has logged `queue ends` (the owner's "after prev measures done"); on aifoundry1 with `V3_DEVICE=1`
(card 1; card 0 is excluded, 115-117 C under load, and block.sh refuses it).

Order inside a block (catfull's): `others_present` and `ours_running` (exit 3); preflight (files only: numpy, the plan,
the shim and the t10 runner, the gs host and kernel, ettelem, on governor-free E/R blocks the heater; the runner's
`--list` must select exactly the plan's configurations); `block_begin gs <KS>`; `code.sha256` (lib.sh, this directory,
the t10 runner, gs_catalogue.py, analyze_catalogue.py, analyze_gs.py, cflib.py, the gs host and kernel); `plan.json`;
for E/R the clock before anything runs and the preheat (catfull's loop: `others_present` before every reading, no
management drain with `V3_DEVICE`); `pass.json`; `others_present`; for E/R `start_sampler`; the runner (every device
process `timeout 10`, stdin /dev/null; exit 3 on another user, 4 on a stalled sampler); one retry of configurations
without a launch (at most 12, `retry/`); `stop_sampler` (SIGTERM); the check (`gslib.py check`, stderr to
`check.err`); gzip; `block_end`.

E and R blocks leave out every configuration whose verify launch failed in the card's latest C block (`check.json` of
the highest `gs K0` with status ok or checkfail; recorded in `pass.json` "excluded"). An E or R block with no C block
stops at preflight (exit 2). A C block whose verify launches fail ends `checkfail` (exit 1: the queue logs it and
goes on); rerun it with a later pass number (`gs 20`) after a fix.

Block status: C `ok` / `checkfail` / `fail`; E catfull's `ok` / `offclock` / `partial` / `fail`; R `ok` / `offclock`
(a configuration with no launch at 600 MHz) / `partial` / `fail`; `others` (exit 3: moved aside, retried by the queue).
Files in `gs/p<KS>/`: `runs.jsonl.gz`, `telemetry.jsonl.gz` (E, R), `configs.json`, `plan.json`, `pass.json`,
`preheat.jsonl`, `run.log`, `runner.out`, `retry/`, `check.json`, `block.json`, `code.sha256`.

## Drop rules (fixed before data)

- **E**: catfull's, through `cflib.pass_bursts` unchanged: governor-free cards drop a burst with busy samples off
  600 MHz or a launch whose implied clock (cycles_max / wall_s) is outside 0.595-0.605 GHz (the first launch after an
  idle bracket off 600 MHz is recorded, not tested); idle brackets are never a drop criterion; every card drops bursts
  bursts_of cannot cut. Slow-sampler bursts (median took_ms > 60) are kept and counted.
- **R**: per launch, governor-free cards drop a launch whose implied clock is outside 0.595-0.605 GHz or whose busy
  telemetry samples are not all at 600 MHz; aifoundry3 (pinned): no clock rule, clocks recorded. (Added in review,
  before data: the R block's load is near idle for ~4 min, and aifoundry2's die falls from 88 to 66 C in a 900 s idle,
  so on governor-free cards the runner re-heats to 74 C between configurations rather than lose launches to the clock
  rule; R reads no idle brackets, so the heater needs no spacing from the bursts.)
- **C**: none; a configuration passes when its one verify line says `"ok": true` (and the launch did).
- aifoundry1-c1 (firmware 1.2.0) and aifoundry2 (1.3.1) are governor-free and preheated to >= 76 C; aifoundry3 (1.3.1)
  is pinned at 600 MHz and not heated.

## Items (reduce.py; rules fixed before data)

Unit: the pass. Intervals: 99% two-sided t over pass values (>= 3 passes per card, else INSUFFICIENT). Per card a
TESTED item is PASS when its interval lies inside the range, FAIL when wholly outside, INCONCLUSIVE otherwise; over the
three cards PASS (all), FAIL (all), CARD-DIFFERENT (mixed), INCONCLUSIVE or INSUFFICIENT. The tested items check the
design's model; a FAIL says the model is wrong and never changes a measured value.

| item | kind | what |
|---|---|---|
| GS-RATE | reported | elements/s, cycles per instruction and pJ per element for every E configuration, per card and pooled (over every card's pass values; also pooled over aifoundry2 + aifoundry3 only, the energy manual's catalogue card set, for rows set beside its tables); R rates, pooled the same way |
| GS-L1 | tested | `fgw.ps` rand from L1 (512 B per hart): cycles per instruction per minion in [7, 12] |
| GS-MH | tested | `fgw.ps` rand from L2 (4 KB) and own scratchpad (16 KB): 0.5-2x the 2-miss-handler bound (23.9 G elements/s), and h2/h1 <= 1.2 (L2: h2 4 KB vs h1 8 KB at 1,024 minions; scratchpad: one minion, R) |
| GS-UC | tested | `fgwl.ps` rand L2, one minion: h2/h1 in [1.6, 2.4] (strict per-thread order of L1-bypassing operations) |
| GS-DRAM | tested | `fgw.ps` rand, 256 KB per hart: line bytes/s within +-25% of 76 GB/s |
| GS-ADD | reported | updates/s and nJ per update: `upd` (gather + fadd.ps + scatter) at four levels, `famoaddl.pi` shire table, `famoaddg.pi` chip table, both on a private word, `amoaddl.w`, `amoaddg.w`; the first over 10 G updates/s |
| GS-CONFLICT | reported | the lane whose value remains when every lane of a scatter hits one word (prediction: lane 7) |
| GS-CHECK | tested | every C launch passes on every card (the verify launches are the detector of erratum 1.3: a gather or scatter that skips elements after a resumed one ends with gsc_progress = 0, so the exit reading cannot see it), and every launch of every used E and R block, kept or dropped burst alike, ends with gsc_progress = 0 on every hart and ok (a sanity check) |
| GS-CARD | reported | each card's median ratio to aifoundry2 over configurations (pJ/element, elements/s); the catalogue's 0.950 beside |

## Changes from the design (before any data)

- R has 57 configurations, not 56: `fgwl.ps` rand L2 with both harts of one minion, which GS-UC needs (the design's R
  has only the one-hart case). C therefore has 159 (157 + this one + the probe).
- Verify launches store every gathered vector of every visit instead of lane sums (an exact check per element), and
  all gs code uses only caller-saved FP registers (f0-f7, f10-f17, f28), so the compiler never saves or restores an FP
  register inside it (a restore followed by a save is itself a VPURF hazard; sys_emu's checker flagged one).
- DRAM tables are filled by DMA before the first launch (as the catalogue's `tload/dram` fills its 512 MB), not by the
  kernel: no fill energy inside a burst, and the model's initial contents are exact. Scratchpad tables are copied in
  by the kernel at every launch with a global store (`fswg.ps`), so no copy of the table is dirty in the L1 for the
  L/G forms to miss.
- sys_emu's memory checker does not model local stores to a scratchpad line (it leaves the line's time stamp behind
  and its shire dirty for good): the kernel waives its read checks around the copy-out after `fscwl.ps` on a
  scratchpad and its write checks around the scratchpad fill, with sys_emu's hints `slti x0, x0, 0x603..0x606`
  (no-ops on silicon); the host compares every value in both cases.

## Review, 25 Sep (before any card time)

- Erratum 1.3 in timed launches: a gather or scatter interrupted mid-way (in U-mode only an IPI can do it) and resumed
  can make the next one skip up to 7 elements, and both then end with gsc_progress = 0. The timed launches therefore
  cannot detect it; they can overcount by at most 7 elements per interrupt, negligible against ~10^8 elements per
  launch. The per-launch `gsc_nonzero` count is kept as a sanity check; only the verify launches detect skips.
- Packed atomics: each `famo` overwrites its addend register with the old values, and the next visit's `fbci.pi`
  rewrites that register 8 instructions after the last `famo`. The kernel assumes the pipeline orders this
  write-after-write (as it orders reads through the scoreboard). If it does not, only the counters' values change,
  not the rate; the C block's counter check would fail and the E/R blocks would leave the configuration out.
- The pre-burst table fill (512 MB by DMA for the 256 KB-per-hart configurations, as the catalogue's `tload/dram`) sits
  in the burst's idle bracket before it. In catfull's and V3-CAT's `tload/dram` bursts on aifoundry2 (p11-p22, p1-p7)
  the idle before and after agree within 0.1-0.3 W, as for configurations without a fill: the DMA does not show on
  the board meter at this resolution.
- Where the results go (design section 5) stands, with two points for the report step: rows placed beside the energy
  manual's catalogue tables (two cards) use `combined_catalogue` (aifoundry2 + aifoundry3) with aifoundry1-c1 (firmware
  1.2.0) beside as a third card, while the gs pages and notes use the three-card pool; and every "random" in a table is
  described as above (random lines within 4 KB tiles), not as uniform random addresses.

## Deployment (by hand, per host, only after that host's queue has logged `queue ends`)

1. aifoundry3 and aifoundry1: rsync `workloads/enercat`, `tools/claims-v3/gs` and `tools/claims-v3/schedule-gs-*.txt`
   to `~/nekko` (never over a running script; `scripts/deploy-lab.sh` uses BSD tar flags and fails on Linux).
2. Build `build/enercat_gs` there (the two commands above, `nice -j4`); never rebuild `build/enercat_v2`. The lab
   toolchains are older than the VM's: the build must assemble every gs mnemonic, and
   `objdump -d build/enercat_gs/kernel/enercat.elf` must show all 26 of them (`fg{w,h,b}{,l,g}.ps`,
   `fsc{w,h,b}{,l,g}.ps`, `fg32{w,h,b}.ps`, `fsc32{w,h,b}.ps`, `famoadd{l,g}.pi`; on aifoundry2, binutils 2.45 and gcc
   15.1.0, each appears 80-163 times). If an assembler lacks one, stop: do not substitute encodings by hand.
3. The smoke by hand: `bash tools/claims-v3/gs/block.sh 1 --smoke` (`V3_DEVICE=1` on aifoundry1); it must end `ok`.
4. The queue: `setsid nohup tools/claims-v3/queue.sh tools/claims-v3/schedule-gs-<card>.txt >
   build/claims-v3/queue-gs-<card>.log 2>&1 < /dev/null &` (with `V3_DEVICE=1` on aifoundry1).

## Simulator validation (before any card time)

`build/enercat_gs/host/enercat_host --sysemu --shires 0x1 --budget 1e9 --suite <file> --sim-args "-vpurf_warn"`, run as
`nice -n 19 taskset -c 10,11` and only while a queue block has just begun (lib.sh counts `sys_emu` and `*_host` as the
queue's own device processes). `gs_catalogue.py --sim-suite <file> --sim-set C [--sim-multi] [--sim-timed]` writes the
suites: every configuration scaled to shire 0 (or shires 0 and 2) with two minions and at most 8 visits. On 25 Sep all
159 C configurations passed their verify, with no VPURF warning at a kernel PC and only the two waived memory-checker
cases (results in the session scratchpad `gathscat/sim/`). Rerun after the review's host change (21:01-21:06, inside
catfull p23, `nice -n 19 taskset -c 10,11`, each suite under `timeout`): all 159 C configurations on shires 0 and 2
passed (20.2 M values checked; lane 7 wins every conflict; every probe case passes), all 166 E, R and smoke
configurations ran one timed launch each with every hart reporting and `gsc_progress` 0; no VPURF warning at a kernel
PC, and memory-checker warnings only at the two waived PCs (`gathscat/review/`).
