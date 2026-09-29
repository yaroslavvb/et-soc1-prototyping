# PCIE2: two DMA commands at once, and where a host write lands (hub rungs 34 and 35)

Two questions the PCIe page (E50, `docs/reports/2026-09-27-et-soc1-pcie-link.html`) left open, run with the owner's
method: theories and numeric predictions first (`PREREG.md`), development on aifoundry1's card 1, a freeze
(`freeze.sh`: `LOCK.sha256`, `PREREG.sha256`), validation on aifoundry3, and later aifoundry2 as a third card.

- **Rung 35.** Two host-to-card DMA commands in flight move half as much as one (D19: 0.49x on all three cards).
  A sweep of 2 x {1, 4, 16, 64} MB with one and two commands in flight, plain and split into 8 DMA elements, and
  two streams with one command each, separates a per-command cost (T35-A), a rate that halves while two H2D
  commands overlap (T35-B, a shared read engine, or T35-C, the IOMMU), a slow onset (T35-E), an element effect
  (T35-X) and a one-stream effect (T35-S). B and C need a host rebooted with `iommu=pt` to separate: not now.
- **Rung 34.** The first touch of each line after a host copy, timed in a kernel launched without the L3 flush,
  against the same lines' DRAM and L3 references: through the L3 homes with allocation (T34-A, the sources' reading),
  through them without (T34-B), to the memory shires with the L3 copy invalidated (T34-C) or left stale (T34-D).

The probe is `workloads/pciebench` (its README): `--test conc` gained `--mb`, `--elements`, `--copy`, `--trials`,
`--cfgs` and `--shuffle` (with none of them it is the 27 September test), and `--test touch` is new, with the kernel
`kernel/touch.c` and the shared `touch_args.h`.

| File | What |
|---|---|
| `block.sh <pass>` | one pass on the local card: 1-99 validation (frozen only), 100-899 development, 900+ smoke; `--preflight <pass>` (files only), `--binhash` |
| `pcie2lib.py` | the pass's plan (ten processes, order shuffled per pass), the telemetry summary, the V3_DRY stub of the probe |
| `reduce.py` | `--check-pass`, `--data <root> [--dev]` (verdicts and theories), `--self-test`, `--print-predictions` |
| `PREREG.md` | theories, predictions, the rule; frozen by `freeze.sh` before validation |
| `run_passes.sh` | runs a schedule's passes, stopping at the first that fails (development and validation: below) |
| `freeze.sh`, `deploy.sh` | the freeze (`LOCK.sha256`, `PREREG.sha256`, `TEXT.sha256`); the copy to a lab tree with digest checks |
| `schedule-dev-aifoundry1-c1.txt`, `schedule-val-aifoundry3.txt` | development (smoke + 3 passes), validation (5 passes) |

## The etiquette, and where the code enforces it

- **Never aifoundry1's card 0**: `block.sh` refuses `aifoundry1-c0`; on aifoundry1 `V3_DEVICE=1` (lib.sh then exports
  `ET_DEVICES=1`, and the probe and ettelem built there open card 1 only). `block.sh` and `run_pcie.sh` refuse, on
  aifoundry1, a probe or ettelem that does not contain the name `ET_DEVICES` (a build against the stock device layer,
  which has none, would open card 0 as device 0). Nothing runs `dev_mngt_service` (the stock build opens every card's
  management node; lib's `drain_mgmt` is overridden), and nothing reads card 0's temperature.
- **Nobody else**: before every device-opening process, the samples included, lib's `others_present` and
  `ours_running` and `et-who --check` (any holder, or a failing check, stops the pass with exit 3). `et-who --check`
  sees both of aifoundry1's cards, so anyone on card 0 (a guard sampler, a CI job) defers a card-1 pass too:
  conservative, and it can cost a retry (run_passes.sh waits 10 minutes, three tries).
- **One process at a time under the lock, 10 s each**: `flock -n /run/lock/etsoc-shire<N>.lock` around each process,
  released when it exits, 1 s between processes (the block does not use lib's `block_begin`, which holds the lock for
  a whole block); `timeout 10` on each; the probe stops starting work at `--budget 8.5`.
- **A failure stops everything at once**: a probe process that exits non-zero ends the pass (exit 1) before anything
  else opens the card; one that looks hung (killed by the timeout, or an output naming HPSQ, "did not finish", "did
  not drain", abort) ends it with exit 5 and writes `build/claims-v3/STOP`. `run_passes.sh` stops at any pass that is
  not ok (it retries only exit 3), so both development and validation run with it: `queue.sh` would log a failed
  block and go on to the next pass on a shared card.
- **90 C**: a 1 s sample before, after the fifth process and at the end (three tries each, since ettelem fails to start
  about one time in three); any die at 90 C or more stops the pass (exit 4) and writes `build/claims-v3/STOP`; no reading
  in three tries stops it too (exit 3). Neither card is heated: DMA timing does not depend on the die, and both
  development and validation cards run at a fixed 600 MHz (the samples record the clock).
- **The code that runs is the code in the tree**: the probe carries the sha256 of `main.cpp`, `touch_args.h` and
  `touch.c` it was built from (CMake writes them into `Constants.h`; the probe prints them on its `open` line), and
  every pass refuses a probe whose hashes differ from the tree's (`block.sh --preflight <pass>` shows the check without
  a device). Once frozen, the kernels compiled into the probe must also have the `.text` in `TEXT.sha256`.
- **Not aifoundry2** until the DV2 validation ends (about 17:00 PDT, 29 September): `block.sh`, `run_pcie.sh` and
  `schedule.sh` refuse it unless `PCIE2_ALLOW_AIFOUNDRY2=1` / `PCIE_ALLOW_AIFOUNDRY2=1`.
- **No queue.sh**: on a two-card host queue.sh reads the die before each block with lib's `die_c` (ettelem under
  `timeout 20`, without the card lock), and on any host it goes on after a failed block; `run_passes.sh` runs the
  same schedule lines without either.

## Development on aifoundry1's card 1 (from a checkout; the main session runs every card step)

```bash
# 0. the dry checks, anywhere (no device): the reduction's self-test and one dry pass acting as the card
python3 tools/claims-v3/pcie2/reduce.py --self-test
V3_DRY=1 PCIE2_DRY_CARD=aifoundry1-c1 bash tools/claims-v3/pcie2/block.sh 101
# 1. look first, then build the probe on aifoundry1 into ~/nekko/build/pciebench (nice, -j4) and copy this directory
ssh aifoundry1 'et-who --check; echo "et-who rc $?"; pgrep -af "[t]ools/claims-v3/" || echo "no framework process"'
scripts/deploy-lab.sh aifoundry1 workloads/pciebench                         # only on rc 0 and no process above
bash tools/claims-v3/pcie2/deploy.sh aifoundry1                              # copies pcie2/, checks every digest
# 2. on aifoundry1, files only: the probe is this tree's and honours ET_DEVICES, and so does ettelem; then a dry pass
ssh aifoundry1 'cd ~/nekko && V3_DEVICE=1 bash tools/claims-v3/pcie2/block.sh --preflight 101'
ssh aifoundry1 'cd ~/nekko && V3_DRY=1 V3_DEVICE=1 bash tools/claims-v3/pcie2/block.sh 101 && et-who --check'
# 3. the smoke and three passes, detached (about 2 minutes of card time over about 8 minutes)
ssh aifoundry1 'cd ~/nekko && mkdir -p build/claims-v3 && V3_DEVICE=1 setsid nohup bash tools/claims-v3/pcie2/run_passes.sh \
    tools/claims-v3/pcie2/schedule-dev-aifoundry1-c1.txt > build/claims-v3/pcie2-dev-aifoundry1-c1.log 2>&1 < /dev/null &'
ssh aifoundry1 'tail -4 ~/nekko/build/claims-v3/pcie2-dev-aifoundry1-c1.log; pgrep -af "[r]un_passes.sh" || echo finished'
# 4. the fixed run_pcie.sh's first run on a card (TODO part B), once run_passes.sh has finished: about 15 s of card time
ssh aifoundry1 'cd ~/nekko && TREE=$PWD V3_DEVICE=1 setsid nohup timeout 300 workloads/pciebench/run_pcie.sh 101 \
    > build/pcie-run101-aifoundry1-c1.log 2>&1 < /dev/null &'
# 5. collect and reduce (development values: reported, never judged)
rsync -a aifoundry1:nekko/build/claims-v3/aifoundry1-c1/pcie2/ build/pcie2-raw/aifoundry1-c1/pcie2/
rsync -a aifoundry1:nekko/build/pcie-data/aifoundry1-c1/r101/ build/pcie-data/aifoundry1-c1/r101/
python3 tools/claims-v3/pcie2/reduce.py --data build/pcie2-raw --dev --md build/pcie2-raw/dev.md
```

The preflight and the dry pass on aifoundry1 (step 2) never open a device: they check that lib.sh accepts
`V3_DEVICE=1` there, that the build is of this tree's sources and that python3 and the plan work. A development pass
that fails can be fixed and rerun as a new number (104, ...); record in PREREG.md any change to a prediction before
the freeze. A pass that stops with exit 5 has written `build/claims-v3/STOP` on aifoundry1: find out why before
removing it.

## The freeze, then validation on aifoundry3

```bash
# before the freeze: a compile-only build on aifoundry3 (no card), to catch a runtime API difference while the code
# can still change; only when nothing runs there
ssh aifoundry3 'et-who --check; echo "et-who rc $?"; pgrep -af "[t]ools/claims-v3/" || echo "no framework process"'
scripts/deploy-lab.sh aifoundry3 workloads/pciebench
# the freeze, in the checkout: self-test, the kernels' .text (TEXT.sha256), LOCK.sha256, PREREG.sha256; note the sha256
bash tools/claims-v3/pcie2/freeze.sh
scripts/deploy-lab.sh aifoundry3 workloads/pciebench && bash tools/claims-v3/pcie2/deploy.sh aifoundry3
ssh aifoundry3 'cd ~/nekko && bash tools/claims-v3/pcie2/block.sh --preflight 1 && V3_DRY=1 bash tools/claims-v3/pcie2/block.sh 1'
ssh aifoundry3 'cd ~/nekko && setsid nohup bash tools/claims-v3/pcie2/block.sh 901 > build/claims-v3/pcie2-smoke-aifoundry3.log 2>&1 < /dev/null &'
ssh aifoundry3 'cd ~/nekko && setsid nohup bash tools/claims-v3/pcie2/run_passes.sh tools/claims-v3/pcie2/schedule-val-aifoundry3.txt \
    > build/claims-v3/pcie2-val-aifoundry3.log 2>&1 < /dev/null &'
rsync -a aifoundry3:nekko/build/claims-v3/aifoundry3/pcie2/ build/pcie2-raw/aifoundry3/pcie2/
python3 tools/claims-v3/pcie2/reduce.py --data build/pcie2-raw --out build/pcie2-raw/pcie2.json --md build/pcie2-raw/results.md
```

`--preflight 1` on aifoundry3 is where the freeze meets the lab build: the probe's source hashes must equal the
locked sources, and its kernels' `.text` the freeze's (built here with aifoundry2's toolchain; AGENT.md section 6 says
the three give identical code). The validation's summary says which theories survived on each card (`reduce.py`'s
theory table; a T34 theory is "invalid" on a card whose R34 controls did not all pass). The raw data and the
reduction then go to `docs/reports/data/<date>-pcie2/` with a README (AGENT.md section 7).

## What a pass writes (`build/claims-v3/<card>/pcie2/p<pass>/`)

`plan.json` (the ten processes in their order), `<id>.out` and `.err` per process (lines `PCIE {json}`),
`launches.jsonl` (id, exit, times, arguments), `tel-{pre,mid,post}.json` and `tel.jsonl` (the samples and their
summaries), `marks.jsonl`, `manifest.txt` (`et-lab-manifest`), `code.sha256`, `binaries.json` (`--binhash`),
`pass.json`, `check.json` (`reduce.py --check-pass`), `block.json` (lib's format; queue.sh reads `"status":"ok"`).
Under `V3_DRY=1` the same, in `build/claims-v3-dry/`, from the stub; the knobs are in `block.sh`'s header.
