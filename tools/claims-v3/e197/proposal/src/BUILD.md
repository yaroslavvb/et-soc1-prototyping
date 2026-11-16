# regfile: build and run

The integer register file's reads and writes on every minion, one hart each: register-to-register instructions
only, no load, no store and no branch inside the timed loop. Written in the style of the public lab repo's
`workloads/enercat`, against the runtime's public interface and the public instruction set (RV64I) only. The
contrasts are A B B A trains inside one device process, the public lab repo's train form (E182, E183).

## Build (on the box, in a folder of your own)

```bash
python3 make_images.py --check .                    # re-derives every kind's counts; the generated files match
cmake -S . -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build -j4
python3 check_elf.py build/kernel/regfile.elf       # 17 timed loops, 131 instructions each, all 32-bit, aligned,
                                                    # each body word for word as make_images.py encodes its form,
                                                    # and the same tail and padding words after it in every loop
./build/host/regfile_host --list                    # the kind table: designed counts per instruction (no device)
python3 make_images.py --frame                      # fetched-bit changes where each train's bodies meet the frame
```

The kernel built on the box need not have the sha256 registered here (the box's SDK may differ): `check_elf.py` on
the box's own build is the gate, and the box ELF's sha256 is recorded with the data. The emulator counts in the
request were made with the build here.

The host is card-only (the PCIe device layer). The kernel is plain C with one inline-assembly loop per form; it
needs the SDK's `et-common-libs` (U-mode) and the toolchain file, as every workload in the lab repo does.
`make_images.py --emit .` regenerates `kernel/regfile_bodies.inc` and `host/regfile_kinds.h` (both are committed).

## Forms, images, kinds

A form is one loop body of 128 instructions; an image is the values of the registers the form names; a kind is a
(form, image) pair, named `form.image`. Every kind of one form runs byte-identical code. Every loop has the same frame
around its body: the loop's own `addi x10, x10, 1 ; csrr x13, hpmcounter3 ; bltu x13, x28` (registers that no form
names, written out in the assembly so no compiler chooses them), then 29 copies of `addi x28, x28, 2` (the deadline
register is dead once the loop ends; they run once, at the end), so the 64-byte block holding the branch and the
block after it are the same bytes in every form. That instruction's fields are chosen from the encoding so that where
a body meets the frame, the two kinds of each train change about the same number of fetched bits at every aligned
block size from 8 to 64 bytes (`--frame` prints it; `--check` bounds the cell pair and the write pair at 4 bits an
iteration). `make_images.py` holds the seventeen forms, the thirty-four kinds, and for each kind the designed counts
per instruction in the steady stream: bits
that change between neighbouring instructions in the register named by bits 19:15 (`f1`) and 24:20 (`f2`), the same
only where the instruction uses that operand (`a1`, `a2`), the result (`res`), the destination's stored value
(`cell`), the two source fields (`i1`, `i2`), the destination field (`iw`), the encoding (`enc`), and the ones held in
the two named registers (`h1`, `h2`).

## What one run is

```bash
et-who --check && [ -e /run/lock/etsoc-shire0.lock ] &&
  flock -n /run/lock/etsoc-shire0.lock timeout -k 1 10 ./build/host/regfile_host --train rot.x64,rot2.x64 --orient SFFS \
     --launches 13 --stop-file OUT/STOP
```

A train process is 13 launches of 240,000,000 cycles (0.4 s at 600 MHz): launch 0 settles with the orientation's
first letter, launch n >= 1 takes letter (n - 1) mod 4 of the orientation, F is the first kind and S the second, so
every quad of launches (1-4, 5-8, 9-12) reads D(F) - D(S). `--kind NAME --seconds S` runs bursts of one kind;
`--kinds A,B,...` a suite. Only when `et-who --check` finds nobody holding a card node or lock, and never while a
sampler of someone else runs; the lock file is the one the host makes at boot (never create it). One card only:
before opening anything the host counts the card nodes (`/dev/et<N>_ops`). With one it runs; with several it runs
only when `ET_DEVICES` names one of them and the linked device layer reads `ET_DEVICES` (the lab's own test:
`grep -aqw ET_DEVICES` on the binary; the host's own code never spells the name out, so that test sees only the
device layer); otherwise it refuses. After opening, the runtime must list exactly one device. No launch starts unless
it can end inside `--budget` seconds (8.5 by default, at most 9) of holding the device, so the process ends inside
`timeout 10`; nothing is launched once the `--stop-file` exists.

Each launch prints `REGFILE {json}`: the kind, its designed counts, the launch index and its letter, the loop
iterations (their sum over the harts, and the fewest and most of any one hart), the body instructions, the neighbourhood counters (instructions retired by thread 0,
instruction-cache requests and misses, L1 data misses) read before and after the loop, the cycles, `x1` and `x3`
(the loop's own instructions name them in a field), the deadline, the launch's epoch bounds, and `check_bad`: the
harts whose written registers do not hold, after the loop, the values the kind's model gives (must be 0).

## A session

```bash
ETTELEM=<the sampler> bash run_session.sh OUT full                  # or short; ext: the optional second sitting
SAMPLER=pvt PVT_SAMPLE=<the per-sensor sampler> ...                 # the same, with raw per-sensor temperature codes
ET_DEVICES=1 ...                                                     # on a host with several cards: card 1, lock shire1
DRY=1 bash run_session.sh OUT full                                   # prints every device call, opens nothing
touch OUT/STOP                                                       # stops within one 0.4 s launch
python3 -B reduce_regfile.py OUT [OUT2] --out regfile.json         # a second sitting's OUT pools by unit
```

Every session writes to a fresh OUT: a folder that holds a file of an earlier session (`SESSION_DONE`, `STOP`, the
telemetry, the run or mark records, the error files) is refused (exit 2), because its `SESSION_DONE` would end the
live stops at once and its records would mix two sessions. A dry run leaves only `session.log` there.

Run a session only inside a window that the lab session has named for this request: its holder check sees other
users' device processes and the card's holders, not the queue of an account between that queue's blocks.

Before anything opens a card node, the session refuses (exit 2) on a host with several cards unless `ET_DEVICES`
names one and every binary it runs reads it, and refuses (exit 3) unless the card is free: `et-who --check` exits 0,
no other user's device process runs, and a probe of the card lock (`flock -n` on the existing lock file, opened
read-only, never created, as the lab's tools open it) succeeds. Only then one sampler for the whole session (10 Hz);
its EXIT trap stops it with SIGTERM, always. A TERM, INT or HUP to the session writes `OUT/STOP` at once, leaves the
device process in flight to end after its launch (it is sent TERM if it is still there 5 s later), then stops the
sampler. `stopwatch.py` follows its file and writes `OUT/STOP` at a board reading above 65 W on three distinct
readings in a row, a die reading at or above 70 C, or a sampler that has gone quiet. Then the smoke block (`run_trains.py OUT smoke`): the three anchors as 1 s bursts, two
train processes of T8's kinds (recorded under the label `smoke`: they enter no train), and a gate (26 launches ok,
letters as planned, rates within 3 %); a failed gate ends the session (exit 7). Then the blocks A, B, C, D of
`trains.tsv` (or E, the optional second sitting), each under the card lock (fd 9, `flock -n`, never waited for;
exit 75 if busy). Every device process of a block keeps fd 9 open, and the lock is released by closing it, never by
an explicit unlock, so it lasts while any of them runs. The smoke block and the first block run back to back (the lock
is free only while the holder check is made between them); between two blocks of `trains.tsv` the lock is released
for `GAP` seconds (30 by default). The holder check is made again before every block's lock is taken (every holder
`et-who --check` lists must be this session's own sampler on this card's nodes, and no other user's device process
runs); a holder stops the session (exit 3). A block: 10 s idle (marked); the anchors `nop.z`, `res.k0`, `res.k64`,
each a 3 s burst after 4.5 s of idle; the block's trains, each `processes` device processes back to back, no gap, no
heater, orientations alternating from the train's first; the anchors in reverse; 10 s idle (marked). No train starts
unless it fits before the session's cap (`CAP_S`, 3,000 s full, 2,400 s short, 2,100 s ext, less 60 s), and no train
process unless it would end before then even at its timeout's 11 s bound, so a train is cut only when its processes
run slower than planned. A device process killed by its timeout, ended by a signal or not started, or two failed
device processes in a row (a non-zero exit, no launch record, a launch not ok, a train process short of 13 launches),
write `OUT/STOP` and end the session (exit 5). These scripts are a reference: the lab session's own kit (its block
library, stops and preflight) is meant to run the same trains in the same order.

## Files

| file | what |
|---|---|
| `make_images.py` | the forms, images, kinds and designed counts; the loop frame; emits the two generated files; `--check`, `--frame` |
| `regfile_args.h` | kernel arguments and the per-hart result record (shared by kernel and host) |
| `kernel/regfile.c`, `kernel/regfile_bodies.inc` | the timed loops: one asm statement per form; the generated bodies |
| `kernel/crt.S`, `kernel/sections.ld` | startup and linker script, as in the lab repo's workloads |
| `host/main.cpp`, `host/regfile_kinds.h` | kinds, launches, trains, counters, register check, JSON lines; the generated kind table |
| `trains.tsv` | the registered train plan: blocks, trains, kinds, processes, first orientations, the short plan |
| `run_session.sh`, `run_trains.py`, `stopwatch.py` | the reference session: sampler, live stops, smoke gate, blocks |
| `reduce_regfile.py` | the train statistic, its gates and reports, the per-bit prices, electrons, carry-over and gain |
| `check_elf.py` | checks the built kernel's loops against `make_images.py` |
