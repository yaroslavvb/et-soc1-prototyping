# x09mem: build and run

Memory traffic with designed data on every minion, one hart each: 64 B lines read from DRAM (a 32 B vector load per
line through the L1) or written to it (a 512 B tensor store of f0..f15), flat out or paced by the cycle counter, with
the bits of every line chosen by an image rule. Written in the style of the public lab repo's `workloads/enercat`
(its `flw_pat` and `tstore_raw` accesses), against the runtime's public interface, the open SDK's headers and the public
instruction set only. The run protocol is the public lab repo's `tools/claims-v3/runitems.py`, unchanged, and its
`lib.sh` with the changes the lab's own E180 and E183 blocks make to it (`lib_x09.sh`).

## Build (on the box, in a folder of your own)

```bash
cmake -S . -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build -j4
python3 check_elf.py build/kernel/x09mem.elf                     # the five timed loops: 8 or 1 access, wraps, x31
./build/host/x09mem_host --list                                  # the arm table (no device is opened)
python3 make_x09.py build/x09-gen --host build/host/x09mem_host --check   # manifest + counts, from the host's bytes
```

The host is card-only (the PCIe device layer). Before opening anything it counts the card nodes (`/dev/et<N>_ops`)
and runs only when there is exactly one: it is for a host with one card, never reads a device-selection variable, and
refuses on a host with two. After opening, the runtime must list exactly one device. Launches of 240,000,000 cycles (0.4 s at
600 MHz) back to back for `--seconds` (4); no launch starts unless it can end inside `--budget` (8.5 s, at most 9);
nothing more is launched once `--stop-file` exists. Each launch prints `X09MEM {json}` with the fields of the
catalogue's `ENERCAT` line that the lab's reductions read (`ops` = lines moved, or accesses for the two no-traffic
controls; `t_start_ms`, `t_end_ms`, `ok`, `cycles_max`, `ops_per_s`, `bytes_per_s`) and the denominators: loop
iterations, accesses, lines, the neighbourhood counters `hpmcounter4` (thread-0 instructions retired) and `hpmcounter6`
(L1 miss requests) before and after the loop (one record per neighbourhood), the memory shires' mesh read and write
request counts sampled through the user-mode system call of the open SDK by one hart before and after its loop
(`--no-ms` turns it off), the paced loops' polls and late slots, whether the paced slots were spread (`phase`), and a
CRC of the image. Paced arms spread the 1,024 harts' slots evenly over each period (minion m starts (m x period)/1024
cycles into the launch; `--no-phase` starts them together).

## One run by hand

```bash
et-who --check && [ -e /run/lock/etsoc-shire0.lock ] &&
  flock -n /run/lock/etsoc-shire0.lock timeout 10 ./build/host/x09mem_host --item wr.u4 --seconds 4 --stop-file OUT/STOP
```

`--item NAME` picks an arm of the table; `--mode rd|wr|rdl1|wrscp|wrnst --image SPEC --period CYCLES` runs any other
(a different byte, run length, ones density or rate). `--buffers-only` builds what would be copied to the card, times
it and opens nothing (0.3 s and 285 MB of host memory for a read arm: done before the device is opened, so the device
is held for the launches only). `--check-slice` reads hart 0's swept region back after the launches and compares it
with the image (`--fill-word W`: the word unwritten memory holds, counted apart). `--dump-image FILE` writes an arm's
bytes without a device (what `make_x09.py --check` reads). Image rules (every 64 B line):

| rule | bytes |
|---|---|
| `z` | zeros |
| `b:XX` | every byte XX |
| `first:XX` | the line's first byte XX, the rest zeros (`first:01`: one bit a line) |
| `alt:XX:YY:N` | runs of N bytes alternately XX and YY from the line's first byte |
| `par:XX:YY` | the whole line XX or YY: for writes by the minion's parity, for reads by bit 4 of the line index |
| `rnd` | random bytes, a different line everywhere (`--seed`) |

Reads: the host fills every hart's swept region (128 KB, 0-7 KB into a 136 KB slice: the catalogue's bank spread) with
the image before the first launch. Writes: the host gives each minion its 512 B image (eight lines); the kernel loads it
into f0..f15 inside the timed loop's own asm statement and stores it, 512 B at a time, through the hart's 256 KB slice.
The two paced write controls: `wrscp` stores the same 512 B into the minion's own scratchpad region; `wrnst` runs the
same loop, instruction for instruction, with the tensor store replaced by a write of zero to the floating-point flags,
so nothing is stored anywhere (it is paced only).

## A pass (one block on the card), and the session

The scripts run in a tree laid out as the lab repo's own: this `src/` at `<tree>/tools/claims-v3/x09/`, beside the lab
repo's `tools/claims-v3/lib.sh`, `runitems.py`, `text_hash.sh`, `dmcmd_audit.py` with `dmcmd_table.json`, and
`e128/ettelem_guard.sh`, with `build/ettelem/ettelem` and `build/sparsity/host/sparsity_host` built in it (the lab's
own tree, or a folder of one's own holding copies of those public files). Everything is written under that tree's
`build/`, and only when `X9_ROOT` names it: `lib.sh` works in the tree it sits in, and the block (exit 2) and the
session (exit 8) refuse unless `X9_ROOT` is that tree's absolute path.

```bash
# from the tree's root
cmake -S tools/claims-v3/x09 -B build/x09mem -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/x09mem -j4
python3 tools/claims-v3/x09/make_x09.py build/x09-gen --host build/x09mem/host/x09mem_host --check   # [--no-ms]
X9_ROOT=$PWD V3_DRY=1 bash tools/claims-v3/x09/block_x09.sh 910      # prints every device call, opens nothing
X9_ROOT=$PWD bash tools/claims-v3/x09/block_x09.sh 910               # one pass
bash tools/claims-v3/x09/preflight_x09.sh                            # the device-command audit: GO
# the whole session, detached, from a script file, inside the window of the day's go:
X9_ROOT=$PWD X9_LATEST_START='<date>' X9_DEADLINE='<date>' \
  setsid nohup bash tools/claims-v3/x09/session_x09.sh > build/x09/session.out 2>&1 < /dev/null &
python3 tools/claims-v3/x09/reduce_x09.py <pass dirs> --gen build/x09-gen --out x09.json   # the registered reduction
python3 tools/claims-v3/x09/selftest_x09.py build/x09-gen <scratch dir>   # the reducer on synthetic data: PASS
```

`session_x09.sh` is the lab's E139 session and queue ported, with the gates of its E183 session. Before any device
opens it refuses without `X9_ROOT` naming its tree, without the window of the day's go (`X9_LATEST_START`, after which
no session starts, and `X9_DEADLINE`), with a `USER` that is not this login, with a stop file present, or unless the
device-command preflight (`preflight_x09.sh`: the lab's `dmcmd_audit.py` on every file the session runs) reads GO.
Then: et-who and a read-only config read at both ends (through the lab's E128 guard, only while `et-who --check` reads
the card free); the board-power watcher `watch_x09.py` (no block starts unless it runs); the smoke block 901 of
`anchor_pi`, `x9_rd_rnd`, `x9_wr_u4`, `x9_wrh_rnd`, `x9_wrh_nst` and its gate `smoke_gate_x09.py`; passes 910-917,
910 the registered warm-up. A pass starts only before the session's 38th minute and when the longest pass so far (360 s
until one has run) and the close still end before the deadline. The generator and the reducer need numpy: on the
card's host the tree's own environment (lib.sh adds it), or run `make_x09.py` at a desk and copy `build/x09-gen`
(generic counts; its files' bytes do not depend on numpy's version). `make_x09.py --no-ms` runs every item without the
memory shires' counters: the gate then does not ask for them and the reducer's C6 reads NO DATA.

`block_x09.sh` is `tools/claims-v3/mf/block.sh` (E75) with this host and manifest and `lib_x09.sh`'s four changes to
`lib.sh`: every telemetry call through the lab's E128 guard and `lib.sh`'s drain of the management queue refused (as
the lab's E180 v2 and E183 v3 blocks); `X9_ROOT` must be the tree; the holder test against this login (`id -un`); the
kits' other-user test on every host. The rest is `lib.sh`'s block, lock and sampler and `runitems.py`'s approach
(heater bursts to 59 C, launch at 58 C), shuffled items, the drift anchor `anchor_pi` first and last, `timeout 10` per
device process, records `runs.jsonl`, `marks.jsonl`. Each pass also records `text.sha256` (the host, the heater, and
the kernel ELF the host launches: file and disassembly) and `code.sha256` (every source file of the run, the manifest,
the binaries). These are a reference: the lab session's own kit (its stops, preflight and audits) is meant to run the
same items in the same way.

## Files

| file | what |
|---|---|
| `x09mem_args.h` | kernel arguments and the per-hart record (shared by kernel and host) |
| `kernel/x09mem.c`, `crt.S`, `sections.ld`, `CMakeLists.txt` | the device kernel: five timed loops, each one asm statement |
| `host/main.cpp`, `CMakeLists.txt`, `Constants.h.in` | the host: arm table, images, fill, launches, records, checks |
| `CMakeLists.txt` | builds both (ExternalProject for the kernel, as the lab's workloads) |
| `check_elf.py` | the kernel's loops against the design |
| `make_x09.py` | the arm table, designed counts per line, and the runner's manifest; `--check` recomputes from the host's bytes |
| `block_x09.sh` | one pass as a `lib.sh` block run by `runitems.py` |
| `lib_x09.sh` | the block's changes to `lib.sh`: the E128 guard and no drain, the tree, the login, the other-user test |
| `preflight_x09.sh` | the lab's device-command audit on every file the session runs (GO or no device opens) |
| `reduce_x09.py` | the reduction, the sanity checks and the rules, registered before any datum |
| `selftest_x09.py` | the reducer on synthetic data: the pipeline, and every verdict's reach at the lab's scatter |
| `session_x09.sh`, `watch_x09.py`, `smoke_gate_x09.py` | the session (a reference for the lab's kit), the board stop, the smoke gate |
