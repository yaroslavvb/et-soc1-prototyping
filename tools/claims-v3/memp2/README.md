# memp2: DRAM rows and channels, the TensorLoad cache path, the 128 B/cycle cap, and the stride-256 row

Four open items of the hub's §5 and the energy manual, measured in one experiment:

| Item | Question | How |
|---|---|---|
| R33 (rung 33, `exp-dram-rows`) | Which physical address bits pick the DRAM bank, and which the controller (channel)? | memprobe programs `rowalt`, `refphase`, `rrd` (`workloads/memprobe/gen_ops2.py`) |
| R36 (rung 36, `exp-tensor-reload`) | Does the L2 keep the lines a TensorLoad fetched? | memprobe program `treload`: a timed TensorLoad op (`OP_TTLOAD`), twice on the same 16 lines |
| R43 (rung 43, `exp-cache-bottleneck`) | What caps a shire's own-scratchpad stream at 128 B per cycle? | memprobe `--tloop`: TensorLoad streams at strides 64 B, 256 B, 1 KB from 1-4 neighbourhoods, with the minions' starts in one sub-bank, spread over banks, or staggered over one bank's sub-banks |
| E102 (`energy-manual-102`, E45's caveat) | Stride-256 scratchpad reads: bandwidth and energy per byte (a replication of E46) | the catalogue runner over `scpline/*` and `spin/zeros/h1` with `build/enercat` (the g3log-fixed build) |

The theories, predictions and decision rules are in [`prereg/PREREG.md`](prereg/PREREG.md) (a draft until the
freeze); `reduce.py` holds the same rules as code. E102 is reported, not a registered PLAN3 verdict.

| File | What |
|---|---|
| `block.sh <pass>` | one block on the local card: 9xx smoke (a four-stage ladder), 10x / 20x development PROBE / ENERGY (aifoundry1 card 1), 11x / 21x validation (aifoundry3; aifoundry2 after DV2); `--binhash` |
| `series.sh <pass> ...` | several blocks in order, stopping at the first that does not exit 0 (use it instead of `queue.sh`, below) |
| `sysemu.sh [--quick]` | every new kernel path of `build/memprobe2` in `sys_emu` (no card); run once before any card time |
| `memp2lib.py` | the pass plan and card rules, R43's configurations and the smoke's ladder, binary hashes, the thermal and hang watcher, the V3_DRY simulators, the freeze, its check and the smoke gate |
| `reduce.py` | `--check-pass`, `--pass`, `--all --data --out`, `--self-test` (four dry worlds, every item's outcome and reading checked) |
| `deploy.sh <host>` | copies this directory and memprobe's sources to `~/nekko` (never `gen_ops.py`), `--build` builds `build/memprobe2`, checks digests; `--print` |
| `prereg/PREREG.md` | the pre-registration; `prereg/PREREG.sha256` and `LOCK.sha256` appear at the freeze |
| `schedule-aifoundry1-c1.txt`, `schedule-aifoundry3.txt` | `memp2 <pass>` lines, if `queue.sh` is used after all |

## What it needs on a host

- `build/memprobe2`: memprobe built with `-DMEMPROBE_EXT=ON` (the MP_EXT modes). Never `build/memprobe` or
  `build/memprobe-v3`: blocks of other experiments record their hashes. Without the option memprobe builds exactly as
  before (the kernel and host `.text` are byte-identical to HEAD's, checked again on 28 Sep after the review fixes).
  The host binary carries `memp2-src:<sha256 of host/main.cpp>:<sha256 of memprobe_args.h>`, and `block.sh` refuses
  a build whose tag does not match the tree (a stale build), or a kernel older than `kernel/memprobe.c`.
- `build/enercat` with the g3log fix (`registerRuntimeLogLevels`; checked by the preflight), never `build/enercat_v2`.
- `build/ettelem/ettelem` built on the host (so it honours `ET_DEVICES` on aifoundry1).
- Unchanged copies of `../lib.sh`, `../queue.sh`, `../cat/run_catalogue_t10.py`, `../cat/catlib.py`,
  `workloads/enercat/run_catalogue.py`, `workloads/enercat/analyze_catalogue.py` and `workloads/memprobe/gen_ops.py`
  (`deploy.sh` checks them).
- numpy: `block.sh` gets it through `lib.sh` (aifoundry1 `pylib/`, aifoundry3 `.venv`); `reduce.py` run by hand finds
  them itself.

## The card rules, and where the code enforces them

- **aifoundry1: card 1 only.** `V3_DEVICE=1` (lib.sh then exports `ET_DEVICES=1`); `block.sh` and `memp2lib.py plan`
  refuse card 0. lib's queue drain runs the stock `dev_mngt_service`, which opens card 0's management node too:
  `block.sh` replaces it with a logged no-op on aifoundry1, so a management-node failure there (no die temperature
  twice, a sampler that will not start or ignores SIGTERM for 30 s) writes `build/claims-v3/STOP` instead of draining.
- **Nobody else:** `et-who --check` (any holder: exit 3), lib's `others_present` and `ours_running` before the block;
  `others_present` and the STOP file between every two launches and before every energy replicate (the runner also
  checks before each configuration).
- **The card lock:** lib's `block_begin` takes `/run/lock/etsoc-shire<N>.lock` with `flock -n` on fd 9 for the whole
  block (a missing lock file is a refusal); every child runs with fds 8 and 9 closed.
- **10 s:** every launch runs under `timeout 10` (`launch`/`dev10`, the runner's `dev`). The sampler is the framework's
  exception: it runs across one energy replicate (about 100 s) and is stopped with SIGTERM only, as in every V3 power
  block.
- **A launch that does not finish stops everything.** The host's own 6 s timeout ("kernel did not finish", an aborted
  stream), `timeout 10`'s rc 124 or 137, a stream error, "HPSQ", or memprobe's exit 3 (an MP_EXT build ends at the
  first failed launch instead of launching the next): `block.sh` writes STOP and ends the block at once; during an
  energy replicate the watcher reads the runner's `run.log` for the same signs and stops the runner. After such a
  hang (28 Sep) every later launch failed and only a card reset cleared the card: a person looks before anything
  else runs there.
- **Heat:** no start above a minshire mean of 80 C (waits up to 300 s with no launch); a mean of 86 C stops the block
  and writes `build/claims-v3/STOP` (the hottest sensor ran at most 4 C above the mean in E53, so no sensor passes
  90 C); during an energy replicate `memp2lib.py watch` reads the live telemetry at 2 Hz and stops the runner there.
- **New code goes up in small steps.** `sysemu.sh` first (no card). Then the smoke's ladder on each card: (1) one
  minion of shire 0 at every stride, spread and source, 200 loads; (2) the four op programs on one hart (treload's
  timed TensorLoads); (3) one whole shire; (4) the chip; each stage only if nothing before it failed. A PROBE or
  ENERGY pass refuses to start without an ok smoke on the same card that ran the same kernel file.
- **Development and validation:** development passes run only on aifoundry1 card 1; validation passes only on
  aifoundry3 and aifoundry2. **Every pass on a validation card, its smoke included**, needs `MEMP2_LOCK_SHA256` equal
  to the sha256 of `LOCK.sha256` that the freeze printed, and every entry of `LOCK.sha256` verifying on that host:
  PREREG.md, the block files, the shared framework files, and the built kernel's `.text` (bound to the development
  build's). The freeze refuses to run twice.
- **aifoundry2** is refused unless `MEMP2_AFTER_DV2=1` and no DV2 queue or block process exists (`pgrep` on
  `schedule-dv2` and `tools/claims-v3/dv2v?/`).
- `V3_FORCE` only with `V3_DRY=1`.

### Why `series.sh` and not `queue.sh`

`queue.sh` (frozen by the DV2 lock; not edited) reads the die before each block through lib's `die_c`: that opens the
card's management node outside the card lock, before any `et-who` check, under `timeout 20`. `series.sh` only runs
the blocks in order; each block does its checks and reads the die under the lock with `timeout 10`. The blocks still
work under `queue.sh` (the schedules are kept), but use `series.sh`.

## How to run

Off the card (any machine with the tree; no device is opened):

```bash
python3 tools/claims-v3/memp2/reduce.py --self-test          # four dry worlds through gen -> simulate -> reduce
V3_DRY=1 V3_DEVICE=1 bash tools/claims-v3/memp2/block.sh 901   # on aifoundry1 (elsewhere: a hostname stub, see below)
```

Development on aifoundry1 card 1 (from the checkout on aifoundry2; aifoundry1's tree is `~/nekko`):

```bash
ssh aifoundry1 "et-who --check; echo rc=\$?; pgrep -af '[q]ueue.sh|[b]lock.sh|[s]eries.sh|[r]un_queue.sh'; uptime"
bash tools/claims-v3/memp2/deploy.sh aifoundry1 --build       # copy, build build/memprobe2 (nice, -j4), check digests
ssh aifoundry1 'cd ~/nekko && python3 tools/claims-v3/memp2/reduce.py --self-test && V3_DRY=1 V3_DEVICE=1 bash tools/claims-v3/memp2/series.sh 901 101 201 102 202 > /dev/null; et-who --check; echo rc=$?'
ssh aifoundry1 'cd ~/nekko && setsid nohup nice -n 19 bash tools/claims-v3/memp2/sysemu.sh > build/memp2-sysemu.log 2>&1 < /dev/null &'   # 15-25 min, no card
ssh aifoundry1 'tail -3 ~/nekko/build/memp2-sysemu.log'       # wait for "SYSEMU PASS"
ssh aifoundry1 'cd ~/nekko && V3_DEVICE=1 setsid nohup bash tools/claims-v3/memp2/series.sh 901 > build/claims-v3/memp2-901.log 2>&1 < /dev/null &'
ssh aifoundry1 'cd ~/nekko && V3_DEVICE=1 setsid nohup bash tools/claims-v3/memp2/series.sh 101 201 102 202 > build/claims-v3/memp2-dev.log 2>&1 < /dev/null &'
ssh aifoundry1 'cd ~/nekko && python3 tools/claims-v3/memp2/reduce.py --all --data build/claims-v3 --out build/claims-v3/memp2-dev'
```

The dry run on aifoundry1 writes under `build/claims-v3-dry/aifoundry1-c1/memp2/`; remove that directory afterwards if
another dry test shares it (its smoke only counts for dry passes).

The freeze, after development and before validation (in the checkout; collect a development PROBE pass's
`binaries.json` first), then deploy again:

```bash
scp aifoundry1:nekko/build/claims-v3/aifoundry1-c1/memp2/p101/binaries.json /tmp/memp2-dev-binaries.json
python3 tools/claims-v3/memp2/memp2lib.py freeze --binaries /tmp/memp2-dev-binaries.json   # prints MEMP2_LOCK_SHA256=<sha>
bash tools/claims-v3/memp2/deploy.sh aifoundry3 --build
ssh aifoundry3 'cd ~/nekko && MEMP2_LOCK_SHA256=<sha> setsid nohup bash tools/claims-v3/memp2/series.sh 911 111 211 112 212 > build/claims-v3/memp2-val.log 2>&1 < /dev/null &'
```

aifoundry2, after DV2: in the checkout, `nice cmake -S workloads/memprobe -B build/memprobe2 -DCMAKE_PREFIX_PATH=/opt/et
-DMEMPROBE_EXT=ON -Wno-dev && nice cmake --build build/memprobe2 -j4`, then `MEMP2_AFTER_DV2=1 MEMP2_LOCK_SHA256=<sha>
bash tools/claims-v3/memp2/series.sh 912 113 213 114 214`.

Reduce (collected raw data under `<root>/<card>/memp2/p<N>/`):
`python3 tools/claims-v3/memp2/reduce.py --all --data <root> --out <dir>` writes `memp2.json` and `memp2.log`.

Dry runs on a host other than the target: lib.sh names the card by `hostname`, so put a stub first in `PATH`
(`printf '#!/bin/sh\necho aifoundry1\n' > stub/hostname`) and keep `V3_DRY=1`; never run a block without it off its
own host. Dry hooks: `MEMP2_DRY_WORLD`, `MEMP2_DRY_DIE=a,b,...` (`x` = unreadable), `MEMP2_DRY_INTRUDE_AT=n`,
`MEMP2_DRY_FAIL_AT=<label>`, `MEMP2_DRY_HANG_AT=<label>` (for example `tloop:t1-s64`), `MEMP2_DRY_HANG_ENERGY=1`,
`MEMP2_DRY_DV2=1`. On a host where another framework queue runs (aifoundry2's DV2), a block or queue process is
"another framework queue or block" to it (`dv2lib.sh` `other_framework`, which ends its session) unless `V3_DRY` is
set in its environment: even a block that would refuse at once must run with `V3_DRY=1` there. `sysemu.sh` is worse
there: `memprobe_host` and `sys_emu` count as device processes to DV2's gate, so it refuses on aifoundry2 until DV2
has ended.

## What a block writes (`build/claims-v3/<card>/memp2/p<pass>/`)

`block.json` (lib), `pass.json`, `marks.jsonl`, `launches.jsonl` (every device process and its exit code),
`code.sha256` (and `LOCK.sha256`'s hash once frozen), `binaries.json` (sha256 and `.text` sha256), `manifest.txt`
(et-lab-manifest), `check.json` (`reduce.py --check-pass`); PROBE: `mp/` (the programs' labels `*.json.gz`, results
`*.u32.gz`, `gen.log` with the command that regenerates the op lists), `tl/` (`plan.jsonl`, one `<config>.out` of
MEMPROBE lines each, `<config>.err`); ENERGY: `e1/`-`e3/` (the runner's `runs`, `telemetry`, `marks` gzipped,
`configs.json`, `check.json`, `run.log`); `hang.json` or `thermal_stop.json` if the watcher stopped a replicate.
