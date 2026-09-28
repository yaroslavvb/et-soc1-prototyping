# OH (E53): the effect of overheating on the ET-SoC-1

The owner asked (28 Sep 2026) for outside research on throttling and overheating, validated on the ET-SoC-1, on a page
called "The effect of overheating". These tools run the card part: **OH-1** (how far the hottest of the 34 shire
sensors leads their mean under the most concentrated load), **OH-2** (exact-checked kernels from rest to a mean of
82-84 C, the DRAM refresh period at the hot end, the cooling tail) and **OH-3** (the idle law, from the idle stretches
of both). The design, predictions and decision rules are frozen in `prereg/PREREG.md`; the plan they come from is the
session's `PLAN.md` (§2). hp/ and dv2v/ are locked and untouched: `ohlib.sh` and `ohlib.py` are pruned copies of
`../hp/hplib.sh` and `../hp/hplib.py`.

| File | What |
|---|---|
| `block.sh <pass>` | one block on the local card: 1xx OH-1, 201 OH-2, 9xx the smoke; `--binhash` prints the binaries with sha256 |
| `ohlib.sh` | the shell helpers: the between-launch checks, the chain rule, the card-0 guard, the run's sampler and watcher, heating to a target, one heater or checked process |
| `ohlib.py` | the watcher (caps), `kcheck` (every kernel's host-side comparison), the plan, the PREREG lock check, the V3_DRY simulator, `selftest` |
| `reduce.py` | `--check-pass`, `--oh1`, `--oh2`, `--oh3`, `--all`, `--self-test` |
| `params-oh.json` | every cap, band, condition, mask and the Williams square |
| `battery.txt` | OH-2's nine checked kernels |
| `prereg.py`, `prereg/` | the freeze: `PREREG.md` (with its lock block), `prereg.json`, `PREREG.sha256` |
| `run_queue.sh` | the only way to start a queue of an OH schedule (refuses card 0, aifoundry2, `V3_FORCE`, a missing `OH_PREREG_SHA256`) |
| `deploy.sh <host> [--check]` | copies this directory to `~/nekko` on aifoundry1 or aifoundry3 and checks every digest, plus lib.sh, queue.sh and gen_ops.py |
| `schedule-aifoundry3.txt`, `schedule-aifoundry1-c1.txt` | 201 then the OH-1 blocks (the smoke runs by hand first) |

## The rules, and where the code enforces them

- **Never aifoundry1 card 0**: `block.sh`, `ohlib.sh`, `ohlib.py` (`check_card`) and `run_queue.sh` refuse it. While
  card 1 runs, a read-only guard sampler on card 0 (1 Hz, no lock, no launch; E52's) must read <= 85 C at block start and
  stops everything above 90 C or 10 s stale; card 0 must hold no process and no lock holder at every between-launch
  check. Nothing on aifoundry2.
- **Nobody else**: lib's `others_present` and `ours_running`, the process scan and the et_soc1 use count at block start
  and between every two launches (`oh_between`: exit 3, the queue retries later). The card lock is held for the block.
- **<= 10 s per device process** (`hold10`), **chains <= 150 s** then >= 15 s with no launch (`oh_admit`, `oh_gap`),
  the sampler running throughout (SIGTERM only).
- **88 C on any sensor**: the watcher (10 Hz) stops the heater through its `--stop-file` and the block when the mean or
  the hottest sensor reads >= 88 C, or the board >= 82 W twice, and writes `build/claims-v3/STOP`. Soft caps: a sensor
  >= 86 C, the mean >= 85 C or the board >= 78 W (twice) stop heater launches until 1 C / 2 W below.
- **No global state change**: no TDP, threshold, clock, voltage, firmware, trace or SP log-level command. The one write
  is the sampler's SP statistics reset (`--reset-ms 1000`, as E52); every block records the standing statistics first,
  read-only (`stats-before.jsonl.gz`).
- `V3_DRY=1` runs any block with no device access against a small thermal model on a 40x clock
  (`OH_DRY_FAIL=<kernel>:<C>` plants a hot failure, `OH_DRY_VOID=<kernel>` a host crash, `OH_DRY_DHOT=<C>` a larger
  gap); data go to `build/claims-v3-dry/`.

## How to run (from the tree's root: `~/nekko` on the lab hosts)

```bash
python3 tools/claims-v3/oh/ohlib.py selftest && python3 tools/claims-v3/oh/reduce.py --self-test
bash tools/claims-v3/oh/deploy.sh aifoundry3            # from a checkout; also aifoundry1
V3_DRY=1 bash tools/claims-v3/oh/block.sh 901           # then 201, 101 (aifoundry1: V3_DEVICE=1); then et-who
bash tools/claims-v3/oh/block.sh --binhash > bins-a3.json   # on each host (V3_DEVICE=1 on aifoundry1)
python3 tools/claims-v3/oh/prereg.py --bins-a3 bins-a3.json --bins-c1 bins-c1.json   # prints PREREG.md's sha256
bash tools/claims-v3/oh/deploy.sh aifoundry3            # again, with prereg/
setsid nohup bash tools/claims-v3/oh/block.sh 901 > build/claims-v3/oh-smoke.log 2>&1 < /dev/null &
OH_PREREG_SHA256=<sha> setsid nohup tools/claims-v3/oh/run_queue.sh tools/claims-v3/oh/schedule-aifoundry3.txt \
    > build/claims-v3/queue-oh-aifoundry3.log 2>&1 < /dev/null &
python3 tools/claims-v3/oh/reduce.py --all --data <collected raw/> --out reductions/
```

## The freeze and its amendment

- **10:11 PDT, 28 Sep**: `prereg.py` froze PREREG.md, SHA-256 `8d620b64dc60239a104c59e3d9bd8c42cf1b4adb9e482460499dedc836f36661`
  (kept as `prereg/PREREG-before-amendment-1.md`), after the dry runs on both hosts and before the smokes (901).
- **10:33 PDT**: the first two OH-2 blocks were stopped by hand in their B2 band: `oh_heat_to` held the die at its
  target until the time cap instead of returning (the watcher stopped each heater launch at the target, and the loop
  re-read the mean a degree lower). Nothing measured was biased; the blocks were finalised by hand with `block.json`
  status `aborted` and set aside as `p201.aborted-a1`.
- **10:39 PDT**: amendment 1 (`prereg.py --amend`, which refuses any change to the registered items): the watcher's
  sticky `tgt_hit` and its use in `oh_heat_to`; `reduce.py --all` keeps aborted blocks out of the verdicts and reports
  their checked launches in `oh2-aborted.json`. PREREG.md SHA-256
  `067a32b41014fdc65d0880008d090d022075b812c63e360d8dc831c4222ad22e`. OH-2 re-ran from B0 under it.

## What a block writes (`build/claims-v3/<card>/oh/p<pass>/`)

`block.json` (lib), `marks.jsonl` (every step: heat, cond_begin/end, chain_gap, void, kernel_bad, abort),
`launches.jsonl` (every device process: kind, name, host times, rc, chain, status), `tel-<run>.jsonl.gz` (10 Hz with
`--reset-ms 1000`), `k.tar.gz` (every process's output), `mp/` (the refresh programs' labels and results),
`stats-before.jsonl.gz`, `guard.jsonl.gz` (card 1), `binaries.json`, `code.sha256`, `prereg-lock.json`, `plan.txt`,
`check.json` (`reduce.py --check-pass`), `manifest.txt` (et-lab-manifest).
