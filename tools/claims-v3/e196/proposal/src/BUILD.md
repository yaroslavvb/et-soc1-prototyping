# x14: build and run (request 1113-x14-zeroshare)

The fp32 TensorFMA loop of the public lab repo's `workloads/sparsity` (`--test fma`), with 29 pass arms and 2 A B B A
trains that differ only in their operand tiles and their row mask. Written from the public instruction set and
programmer's manuals (PRM 9.4: TensorFMA, its control word, tensor_mask), IEEE 754 binary32 arithmetic, the
runtime's public interface and the public lab repo's workload and kit style (E78's runner and reduction, E82's dip
rule, E109's row mask and session, E182's train statistic).

## Which harness

- **The passes** need no new code on the card: every pass arm is `--test fma --type fp32 --pattern none
  --values file:<tile>` with an optional `--row-mask` on the lab's unchanged `sparsity_host`, which the lab's E78 frame
  (`tools/claims-v3/kinds/run_e78.py`, `reduce_e78.py`) and E109 kit already drive. The arm table (`arms.json`) and
  the tiles are data for that frame. The lab's sparsity host does not read C back on file tiles; the read-backs here
  are a check of the premises, not a measurement.
- **The trains** alternate the row mask (and, generically, the tiles) launch by launch inside one process: the lab's
  E182 train host alternates tiles only, so it needs this small, generic host change (`x14_host --values-b ...
  --row-mask-b ... --abba ... --launches 13`). Nothing else differs from E182's train processes.
- `x14_host`, `run_session.sh`, `run_block.py`, `stopwatch.py` and `reduce_x14.py` are a complete reference
  implementation of both, in the lab's style; the lab session's own kit (its block library, stops, preflight and
  device-command audit) is meant to run the same arms and trains in the same way.

## What is here

| file | what |
|---|---|
| `kernel/sparsity.c`, `kernel/crt.S`, `kernel/sections.ld`, `kernel/CMakeLists.txt`, `sparsity_args.h` | the lab repo's sparsity kernel, **unchanged** (byte-identical to `workloads/sparsity` at the lab repo's commit 49a4152e); the built `sparsity.elf` is the lab's |
| `host/main.cpp`, `host/CMakeLists.txt`, `host/Constants.h.in` | `x14_host`: the lab's sparsity host trimmed to the fp32 TensorFMA loop, card only, with `--label`, the read-back of C after the first and the last launch of a process (`--zero-rows`: words of the named rows that are not zero; `--live-rows`: named rows that are all zero), the A B B A train (`--values-b`, `--row-mask-b`, `--label-b`, `--zero-rows-b`, `--live-rows-b`, `--abba`, `--launches`) and a one-card rule |
| `CMakeLists.txt` | builds both, as the lab's workload does |
| `make_x14.py` | the tiles, the arm table and the train table, with every designed count (operand flips, gated lane-micro-ops and their fraction, flips between live lane-micro-ops, row-mask runs, accumulator flips from an fp32 emulation, rows that must read zero or non-zero); `--check` re-derives everything from the written files |
| `arms.json`, `tiles/` | what `make_x14.py` writes (committed so that a reviewer can read them; the session regenerates and compares) |
| `run_session.sh`, `run_block.py`, `stopwatch.py` | a reference session: holder check, the configuration read at both ends, one sampler (started as the lab's lib.sh does), live stops, a smoke block with its gate, the trains, the passes, each block under the card lock, a deadline |
| `reduce_x14.py` | the registered reduction (passes and trains) |

## Build (on the box, in a folder of your own)

```bash
cmake -S . -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build -j4
python3 -B make_x14.py --lab-tiles <lab repo>/tools/claims-v3/kinds/tiles/fp32 --out gen
python3 -B make_x14.py --lab-tiles <lab repo>/tools/claims-v3/kinds/tiles/fp32 --out gen --check   # {"problems": []}
cmp gen/arms.json arms.json                                                                          # identical
python3 -B make_x14.py --list                                                                        # the arm and train tables
```

`make_x14.py` reads five of the lab's own E78 tiles (`zeros`, `ones`, `randn`, `sparse50`, `a_zeros_b_randn`; their
sha256 are in `arms.json`, as in the lab's `kinds.json`) and writes eight new ones from a seeded integer generator.

## One run, one train process

```bash
et-who --check && flock -n /run/lock/etsoc-shire0.lock timeout 10 ./build/host/x14_host \
    --values file:gen/tiles/h.bin --row-mask 0x00FF --zero-rows 0xFFFF --label I.H.m00FF --seconds 4 --stop-file OUT/STOP
et-who --check && flock -n /run/lock/etsoc-shire0.lock timeout 10 ./build/host/x14_host \
    --values file:gen/tiles/lab_zeros.bin --row-mask 0x1111 --zero-rows 0xFFFF --label T.Z.m1111 \
    --values-b file:gen/tiles/lab_zeros.bin --row-mask-b 0x000F --zero-rows-b 0xFFFF --live-rows-b none \
    --label-b I.Z.m000F --abba SFFS --launches 13 --stop-file OUT/STOP
```

`make_x14.host_args(arm, gen)` and `make_x14.train_args(train, table, gen, order)` give every arm's and every train
process's arguments (`run_block.py` uses them). Defaults: all 1,024 minions (`--shires 0xffffffff --per-shire 32`),
hart 0 of each; launches of about 0.5 s; no launch starts unless it can end inside `--budget` (8 s, at most 9) of
holding the device. Each launch prints `X14 {"label", "values", "row_mask", "kind", "abba", "minions", "iters",
"launch", "ops", "cycles_mean", "cycles_per_op", "wall_s", "t_start_ms", "t_end_ms", "tensor_errors", "ok"}`; each
read-back of C (after the calibration launch and after the last launch, never between measured launches) prints
`X14CHECK {"label", "kind", "after_launch", "zero_rows", "live_rows", "zero_rows_bad", "live_rows_zero", "ok"}`. A word
of C is zero when its magnitude bits are (a zero A times a negative B leaves -0.0). One card only: with several card
nodes the host runs only when the device selection variable names one and the linked device layer reads it.

## A session

```bash
LAB_REPO=<lab repo checkout> ETTELEM=<the sampler> bash run_session.sh OUT 6
LAB_REPO=<...> ETTELEM=<...> DROP_ARMS=F.Ae,Z.b50,I.H.mFFFF bash run_session.sh OUT 5    # the cut order, if short
DRY=1 LAB_REPO=<...> bash run_session.sh OUT 6          # prints every device call, opens nothing
touch OUT/STOP                                           # stops within one launch
python3 -B reduce_x14.py OUT                             # -> OUT/x14.json and a printed summary
```

The heater is this folder's own `x14_host` (`--values randn --label heater --seconds 2 --seed 1`): `HEATER` defaults
to `H` (`build/host/x14_host` beside `run_session.sh`). Both are made absolute, so the session can be started from any
directory, and the session refuses to start unless both are executable files. The lab's `sparsity_host` is not a
heater here: it takes other arguments and exits 2 on `--label`.

The order: the opening configuration read; the sampler; the smoke block and its gate (first the heater check: one
heater launch that must exit 0 with every launch record ok and no tensor error, its highest board reading at most
70 W, else nothing more runs; then every smoke arm and the first two processes of train T1 launched, every record ok
with no tensor error, every read-back of C ok, cycles per op within 0.5 % of 546 unmasked or with every row enabled
and 544 with a row masked, the train records in their order; a failed gate runs nothing more); train T1; train T2;
the passes; the sampler's stop; the closing configuration read, only when the card is free (after a session that
ended because the card was not free, or on a signal, it is skipped and `config-end.json` says why; otherwise the
holder check must pass again first). A block starts only if it can end before the deadline (`DEADLINE`, or
`SESSION_MIN` minutes from the start, 60 by default), and the stopwatch must still be running. A pass: 10 s idle
(marked), two unrecorded burn-in runs of K.pi, K.pi, the 28 other pass arms (fewer by `DROP_ARMS`, recorded in the
pass's `plan` mark in `marks.jsonl`) shuffled by "hostname|pass", K.pi again, 10 s idle (marked). A train block: 10 s
idle, K.pi, the train's 24 processes back to back (SFFS, FSSF, ...), K.pi, 10 s idle. Before every run the approach
(heater launches to 59 C, idle to 58 C, at least 2 s with no device process), as in the lab's E60 and E78 kits; a run
is on protocol only when that approach was kept, and two failed heater launches in a row end the block. The train's
processes follow the opening anchor's approach without one of their own, as in E182.

## Checked here (the request's own dir, not on a card)

- The kernel builds with the open SDK into an ELF identical to the one the lab's unchanged `workloads/sparsity` builds
  with the same SDK (`sha256` in `request.md`); `x14_host` builds with `-Wall -Wextra` and no warning.
- `make_x14.py --check`: no problem. `reduce_x14.py` on a synthetic session (five passes, both trains, injected dips,
  a launch not ok, a failed read-back, a pass with one anchor set aside, a train process off its order) returns every
  arm's watts within the noise, sets aside or flags each fault as registered, and reads both trains' known differences
  inside their 95 % intervals; with the cut order's three arms absent it reports them, and only what needs them, as
  empty.
- `run_session.sh` in its real mode against stand-ins for `et-who`, the sampler and the host (kept with the
  requester, not in `src/`): the closing configuration read is made after a normal end only once the holder check
  passes, and is skipped (`config-end.json` says why) after exit 3, with a holder present at the end, and on a signal;
  a heater that rejects the heater arguments fails the smoke gate at the heater check; `DROP_ARMS` runs the pass
  without the named arms and refuses an unknown name or the anchor before anything opens.
- An emulator-capable copy of this host (the same code plus the simulator's device layer, kept with the requester,
  not in `src/`) ran every arm and both trains (3-launch processes in both orders, and a desk test that switches
  between a random and a zero tile) on one minion in the open system emulator: every launch ok, no tensor error,
  every read-back of C ok; the counts are in `request.md`.
