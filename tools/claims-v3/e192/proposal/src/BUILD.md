# intbits: build and run

Scalar integer bit-flip and carry ladders on every minion, one hart each: register-to-register instructions only,
no load and no store in the timed loop. Written in the style of the public lab repo's `workloads/enercat`, against
the runtime's public interface and the public instruction set (RV64I) only.

## Build (on the box, in a folder of your own)

```bash
cmake -S . -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build -j4
python3 check_elf.py build/kernel/intbits.elf     # 16 timed loops, 259 instructions each, all 32-bit, aligned
./build/host/intbits_host --list                  # the arm table: values and designed counts (no device)
```

The host is card-only (the PCIe device layer). The kernel is plain C with inline assembly; it needs the SDK's
`et-common-libs` (U-mode) and the toolchain file, as every workload in the lab repo does.

## What one run is

```bash
et-who --check && [ -e /run/lock/etsoc-shire0.lock ] &&
  flock -n /run/lock/etsoc-shire0.lock timeout 10 ./build/host/intbits_host --arm add.a.f2 --seconds 4 --stop-file OUT/STOP
```

Only when `et-who --check` finds nobody holding a card node or lock, and never while a sampler of someone else runs;
the lock file is the one the host makes at boot (never create it). One card only: before opening anything the host
counts the card nodes (`/dev/et<N>_ops`). With one it runs; with several it runs only when `ET_DEVICES` names one
of them and the linked device layer reads `ET_DEVICES` (the lab's own test: `grep -aqw ET_DEVICES` on the binary;
the host's own code never spells the name out, so that test sees only the device layer); otherwise it refuses. After
opening, the runtime must list exactly one device.

Launches of 240,000,000 cycles (0.4 s at 600 MHz; `--window` at most 1.2e9) back to back for 4 s; no launch starts
unless it can end inside `--budget` seconds of holding the device (8.5 s by default, at most 9), in single-arm and in
suite mode alike, so the process ends inside `timeout 10`; nothing more is launched once the `--stop-file` exists. Each launch prints `INTBITS {json}`: the
arm, its four source values, the designed counts per instruction (bits that change between neighbouring instructions
on port A, port B, the result, the carry vector, the destination register's cells, and the instruction encoding), the
loop iterations, the instruction count of the bodies, the neighbourhood counters (instructions retired by thread 0,
instruction-cache requests and misses, L1 data misses) read before and after the loop, the cycles, the launch's epoch
bounds, and a check of the destination registers after one more A,B pair (`check_bad` must be 0).

`--arm NAME` picks a named arm; `--form pair|split|same|nop --op add|xor|sub|and|or --a0 --b0 --a1 --b1` runs any
other values (a custom arm: a bit-position sweep, a different Hamming distance, a different carry run).

## A session

```bash
ETTELEM=<the sampler> HEATER=<the heater host> bash run_session.sh OUT 9
SAMPLER=pvt PVT_SAMPLE=<the per-sensor sampler> ...                 # the same, with raw per-sensor temperature codes
ET_DEVICES=1 ...                                                     # on a host with several cards: card 1, lock shire1
DRY=1 bash run_session.sh OUT 9                                      # prints every device call, opens nothing
touch OUT/STOP                                                       # stops within one 0.4 s launch
python3 -B reduce_intbits.py OUT --out intbits.json
```

Before anything opens a card node, the session refuses (exit 2) on a host with several cards unless `ET_DEVICES`
names one and every binary it runs reads it, and refuses (exit 3) unless the card is free: `et-who --check` exits 0,
no other user's device process runs, and a probe of the card lock (`flock -n` on the existing lock file, opened
read-only, never created, as the lab's tools open it) succeeds. Only then one sampler for the whole session (10 Hz);
its EXIT trap (also on INT, TERM and HUP) stops it with SIGTERM, always. Its own time bound is `SAMPLER_S` (default
passes x 600 + 600 s); if the session shell is killed with SIGKILL, end the orphaned sampler with SIGTERM only, never
SIGKILL. `stopwatch.py` follows its file and writes `OUT/STOP` at a board reading above 80 W on three distinct
readings in a row (a repeated value is the same reading of the board meter), a die reading at or above 70 C, or a
sampler that has gone quiet. Then a smoke block: with a heater, one heater launch whose highest board reading must
stay under 70 W (else exit 9: the preheat would come too near the board stop), then three arms, 2 s each. Then the
passes, each under the card lock (fd 9, `flock -n`, never waited for; exit 75 if busy). Between passes the lock is
released for `GAP` seconds (30 by default), then the holder check is made again (every holder `et-who --check` lists
must be this session's own sampler on this card's nodes, and no other user's device process runs) before the lock is
taken; a holder stops the session (exit 3). A pass (`run_block.py`): 10 s idle (marked), two unrecorded burn-in runs of the anchor, the
anchor, the other 31 arms in an order shuffled by `hostname|pass`, the anchor again, 10 s idle (marked). Before every
run the approach: heater launches up to the preheat reading (59 C), idle down to the launch reading (58 C), at least
2 s with no device process; every run's record says how it was approached and whether a wait timed out. Pass 0 is a
warm-up and the reducer sets it aside. These scripts are a reference: the lab session's own kit (its block library,
stops and preflight) is meant to run the same arms in the same order.

## Files

| file | what |
|---|---|
| `intbits_args.h` | kernel arguments and the per-hart result record (shared by kernel and host) |
| `kernel/intbits.c` | the timed loops: nop sled; one instruction repeated; two alternating (one or two destinations); five opcodes |
| `kernel/crt.S`, `kernel/sections.ld` | startup and linker script, as in the lab repo's workloads |
| `host/main.cpp` | arm table, launches, counters, check, JSON lines |
| `arms.txt` | the measured arms of one pass and the anchor |
| `run_session.sh`, `run_block.py`, `stopwatch.py` | the reference session: sampler, live stops, approach, blocks |
| `reduce_intbits.py` | energy and electrons per instruction, contrasts, temperature, the registered ladders |
| `check_elf.py` | checks the built kernel's loops |
