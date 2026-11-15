# x04clock: what an awake core costs per cycle, against a core that waits

A standalone workload in the style of the lab repo's `workloads/enercat` (runtime API only, kernel plus host, one
CMake build). It asks the board meter and the minion rail:

1. **A waiting hart against the firmware's idle park.** A user-mode hart cannot execute `wfi` (PRM 1.3). A thread
   that returns from a kernel waits in the open worker firmware's post-launch barrier, a blocking fast-credit wait
   (`csrw fcc`, PRM ch. 11), until the last thread of its shire returns; shires left out of a launch stay in the
   firmware's idle park (`wfi`). So a launch in which every worker returns at once (`tk`), on 2, 11, 21 and 32
   shires, prices a shire of credit-waiting harts against a shire in the park; three launch lengths (0.1, 0.2,
   0.4 s) bound the per-launch work. A user credit wait (`wait2`) is compared with the firmware's (`tk`).
2. **What one awake core-cycle costs**, as a duty ladder on one 64-slot no-op body: each period every worker waits
   for a credit, then runs the body for a set fraction of the period (0, 33, 67, 100 %). Every hart stamps the cycle
   counter at each wake and at the body's exit, so the awake fraction is measured in cycles. The same duty at
   4,096- and 1,024-cycle periods prices (or bounds) a wake.
3. **Per core or per neighbourhood**: the no-op sled on 7, 15, 23 and 31 workers a shire (neighbourhoods 1, 2 and 3
   first), and 8 workers packed in one neighbourhood against 8 spread over three.
4. **Instruction classes at equal issue**: a 512-slot no-op sled in which one slot in every P (P = 1, 2, 4, 8, 16)
   holds an instruction of one class, on zeros: `fsgnj.s`, `fadd.s`, `fadd.ps`; `fadd.ps` with the lane mask `m0` set
   to 1, 2 and 4 lanes; and `fadd.ps` at 1/8 density in two orders (spread, and all 64 in a row). The issue count is
   the same in every arm; only the fraction and the order of the class's slots change, so the price per class
   instruction is read at each density and in each order.
5. **One hart against two, and a divide chain**, as A B B A trains inside one device process (three launches a
   segment): no idle baseline is needed and a linear drift cancels.

## Arms

`arms.tsv` lists them (name, block, host options): blocks S (the firmware's waits), D (duty), W (workers a shire),
T (trains), C (instruction classes), and the anchor `spin2` (both harts of no-ops on 31 workers a shire), run at
every block boundary.

Minion 0, thread 0 of every launched shire is the shire's **timekeeper in every arm**: it reads the cycle counter
for the launch's window and, in the arms that wait, stores one credit per period into the shire's `CREDINC`
registers for the waiting threads (SDK `etsoc/isa/fcc.h`). Workers are the minions of `--minions` (1..31).

Nothing can leave a hart blocked:
- **start handshake**: a waiting thread empties its counter, then writes its ready word (a local atomic in a host
  buffer, tagged with the launch's epoch); the timekeeper starts its periods only when every waiting thread of its
  shire is ready (or after `--hs-limit` cycles), then writes the go word;
- a waiting thread that finds the go word already written has missed the start: it skips its waits and flags
  itself; the host counts that launch as incomplete (exit status 3), and nothing is blocked;
- the timekeeper sends three spare credits at the end and waits 4,096 cycles before it returns, so nothing is in
  flight; the firmware empties the counters after every kernel, and its barrier tolerates a stray credit.

The neighbourhood counters `hpmcounter4/5/7/8` are read by thread 0 of minions 0, 8, 16 and 24 with the four-read
safe form, after that minion's thread 1 has said it is done (public erratum 1.23). They are checks; the slot counts
are the denominators.

## Build

```bash
cmake -S . -B build/x04clock -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/x04clock -j4
python3 gen_blocks.py > kernel/x04_blocks.inc     # only if gen_blocks.py changes; the generated file is included
```

Build in a folder of ours on the box (`W=~/claude/work/ee-1113-x04-clock`, this `src/` copied to `$W/src`), never
in the lab session's trees. The sampler is the lab repo's `tools/ettelem`, read from the lab's checkout (`LAB`, read
only) and built into our folder:
`cmake -S $LAB/tools/ettelem -B $W/build/ettelem -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build $W/build/ettelem -j4`.
The kernel is built with RVC off inside every timed body, so every slot is a four-byte instruction. Class
instructions read `f0..f7` (zeros, loaded once from a host buffer) and write `f8..f15`, which nothing reads.

## Run

```bash
# one arm on a card, by hand, after `et-who --check` says free: 0.4 s launches for 4 s, under the 10 s rule
ET_DEVICES=0 flock -n /run/lock/etsoc-shire0.lock timeout -k 1 10 ./build/x04clock/host/x04clock_host --arm wait --t1 same --seconds 4
# a train: A B B A, three launches a segment
ET_DEVICES=0 flock -n /run/lock/etsoc-shire0.lock timeout -k 1 10 ./build/x04clock/host/x04clock_host --seg-launches 3 \
    --arm tk --t1 off --then --arm spin --t1 off --then --arm spin --t1 off --then
# session A (blocks S, D, W, T) and session B (block C): 9 passes each, pass 0 a warm-up set aside.
# --device 0 selects the card (ET_DEVICES) and its lock /run/lock/etsoc-shire0.lock; the stop file is OUT/STOP.
python3 run_x04.py OUT_A --host build/x04clock/host/x04clock_host --telemetry SESSION_TELEMETRY.jsonl \
    --telemetry-pid SAMPLER_PID --blocks S,D,W,T --device 0 --deadline EPOCH
python3 run_x04.py OUT_B --host build/x04clock/host/x04clock_host --sampler $W/build/ettelem/ettelem \
    --blocks C --device 0 --deadline EPOCH
python3 run_x04.py OUT --host H --smoke --telemetry T.jsonl --telemetry-pid PID   # one short pass of five arms
python3 run_x04.py OUT --host H --dry                            # prints every device call, opens nothing
python3 reduce_x04.py OUT [--pvt PER_SENSOR.jsonl]               # watts over idle, trains, fits, registered checks
```

Every launch prints `X04 {json}`: workers per thread, slots issued, awake cycles (duty arms), credits taken and
drained, the timekeeper's credits and handshake cycles, late or unsynced flags, cycles, the neighbourhood counters,
and the launch's epoch bounds.

The runner, on the card's rules: it counts the device nodes first (exactly `/dev/et<N>_ops`, or it does not start;
the host program checks the same before it opens the device); it runs the lab's holder check (`et-who --check`) and
probes the card lock before the sampler opens the management node and again before every block, waiting at most
10 minutes for a free card. The holder check exempts one process only: the session's sampler, by its process id, on
this card's management node (the sampler the runner started, or with `--telemetry` the process given by
`--telemetry-pid`, which must have that file open for writing). Any other holder, whatever its user, means the card
is taken. The lock file is opened read-only, as `flock(1)` opens it, and never truncated; it is opened only after
the holder check, held per block, and unlocked and closed between blocks; between passes nothing is launched for
`--pass-gap` seconds (30) with the lock closed (the session's sampler keeps the management node). Every device
process runs under `timeout -k 1 10` and the host stops launching at 9.5 s after the device's opening. Stopped by a
signal, the runner ignores further signals and blocks them for its clean-up: a running device process gets SIGTERM
through its `timeout` (which kills it 1 s later) and is waited for before the lock is released, then the sampler it
started is stopped with SIGTERM and waited for. It stops the session on a device process that fails or is killed by `timeout`, on three incomplete
launches, on the stop file (default `OUT/STOP`) or the deadline, and on the telemetry (board above 65 W three
samples in a row, die at or above 70 C, a minion clock other than 600 MHz three samples in a row, a stalled
sampler). There is no heater: nothing here warms the die toward a stop. A train that did not get all its launches
is marked `"ok": false` and dropped by the reduction.
