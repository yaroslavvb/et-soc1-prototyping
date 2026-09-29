# NV: the mesh (NoC) rail voltage step

This experiment sets the mesh rail to 485, 540 and 600 mV and measures E42's per-hop wire costs at each voltage. It
tests whether the mesh's data cost per bit·hop follows V² (Q63's explanation), V or nothing. The files that define it:

- [`DESIGN.md`](DESIGN.md): the theories, predictions, rules, sample size and safety rules, and §10, what the two
  reviews of 28 September changed.
- [`predictions.json`](predictions.json): the predictions and decision rules, fixed by `PREDICTIONS.sha256` before
  any card write.
- [`PREREG.md`](PREREG.md): the validation's frozen form, a skeleton until the freeze.

Nothing here has run on a card yet (2026-09-28).

**The ground rules:**

- **Only 485, 540 and 600 mV can ever be sent, and only on BL2 0.19.0 or later.** On BL2 0.18.0 every NoC set would
  also be written to the card's flash as its boot voltage.
- **Only on a host with one card.** The stock `dev_mngt_service` opens every card's management node.
- Development runs only on aifoundry3.
- Validation runs only on aifoundry2, and only after all of these: DV2's validation there has ended, the owner has
  released the card (`build/claims-v3/aifoundry2/nv/CARD-RELEASED`), and NV is frozen.
- NV never touches aifoundry1 (either card).

## Files

| File | What |
|---|---|
| `block.sh` | One pass per block: `block.sh <pass> [--smoke\|--probe]`. Passes 1–99 are development (aifoundry3); passes 101–199 are validation (aifoundry2, frozen). Always run detached (below). |
| `run-queue.sh` | NV's own queue over a schedule; it opens no device (DESIGN.md §4) |
| `nvlib.py` | Helpers for `block.sh` (files only): the per-card settings, the pass's plan and spares, parsing `dev_mngt_service` output, the check of each sampler window, the pass-count rule |
| `nv.json` | Levels, the whitelist, voltage orders, configurations, cards, timing, limits, the heater, burst-drop thresholds (development may change timing, limits, heater and drops) |
| `predictions.json` | The bands, the E42 references, the controls' rules, the temperature coefficient and the pass-count rule (fixed before any card write) |
| `reduce.py` | The items, controls and verdicts (`--card <card>`); `--self-test` (synthetic passes); `--monte-carlo` (the rules' error rates) |
| `selftest.sh` | 40 dry scenarios, the reducer's self-test and a short Monte Carlo (no device access, about 6.5 min) |
| `stubs/` | Stand-ins for `dev_mngt_service`, `ettelem`, `enercat_host`, the heater and `et-who` in dry runs. They are named `stub-*` so their process names never match a device tool's. |
| `freeze.sh` | `--predictions` writes `PREDICTIONS.sha256`; `--binaries <file>` writes `PREREG.sha256` and `LOCK.sha256` (it refuses while `PREREG.md` has a TBD or `prereg.json` is incomplete or off the rule); `--check` checks all three |
| `PREREG.md`, `prereg.json` | The validation's pre-registration (skeleton) and the values development fixes |
| `schedule-dev-aifoundry3.txt`, `schedule-val-aifoundry2.txt` | The `run-queue.sh` schedules |

**Data** goes under `build/claims-v3/<card>/`:

- `nv/p<N>/`: the passes;
- `nv-smoke/p<N>/`, `nv-probe/p<N>/`: never read by `reduce.py`;
- `nv/NV-STATE.json`: the state file;
- `nv/STOP`: NV's own stop file;
- `nv/CARD-RELEASED` (aifoundry2 only): written by a person when the owner releases the card;
- `nv/current-aborts.jsonl`, `nv/hot-aborts.jsonl`: the aborts that count towards NV's STOP;
- `nv/queue-state.jsonl`: `run-queue.sh`'s record.

A pass directory holds:

- `block.json`, `run.log`, `code.sha256`, `manifest.txt`;
- `order.json`, `plan.tsv`;
- `steps.jsonl`: every set, read-back, verification and restore;
- `dms.jsonl` and `dms/`: every `dev_mngt_service` call and its output;
- `vmin-start/`, `vmin-after-set/`, `vmin-end/`: the VMIN table at each read;
- `windows.jsonl`: every sampler window, with its check;
- `telemetry.jsonl.gz`, `runs.jsonl`, `marks.jsonl` (fills and heater launches), `heat.jsonl` (aifoundry2);
- the rejected windows' `*-rejected.jsonl`.

## 0. Dry runs (no device, any host)

```bash
bash tools/claims-v3/nv/selftest.sh                          # everything, about 6.5 min; or name scenarios: ... smoke kill9
V3_DRY=1 bash tools/claims-v3/nv/block.sh 1 --smoke          # one dry block as aifoundry3; NV_DRY_CARD=aifoundry2 for the other card
python3 tools/claims-v3/nv/reduce.py --self-test
python3 tools/claims-v3/nv/reduce.py --monte-carlo --reps 1000
```

A dry run works like this:

- It uses the stubs, never a real binary, and never lists the host's processes.
- It writes under `build/claims-v3-dry/`, with its own STOP and ALERT files, so it never stops a real queue.
- It prints every device call it would make.
- Its time runs 10× faster (`NV_STUB_SCALE`), so its telemetry cannot be analysed. The reducer is tested on synthetic
  data instead.
- Faults can be injected with `NV_STUB_FAIL`; `stubs/stub-dms`, `stub-ettelem` and `stub-enercat` list them.

A real run refuses any `NV_STUB_*`, `NV_DRY_*` or `NV_RUNQ_*` variable.

## 1. Before the first card write

1. **Fix the predictions** (in the git checkout, before any card run):

   ```bash
   bash tools/claims-v3/nv/freeze.sh --predictions
   ```

   Commit `predictions.json` and `PREDICTIONS.sha256`, and record the SHA-256 in `docs/findings/03-experiments.md`.
   Every real block refuses until this file checks.
2. **Tell the lab admin** what the first write can do. If the regulator's write or read-back fails, the firmware loops
   until its watchdog resets the card, and a reset on aifoundry3 clears et-board-clock-guard's TDP 0 and 600 MHz pin
   (DESIGN.md §2, §9).
3. **Read-only probes on aifoundry3**, in `~/nekko`, with the card idle. Stop if any current temperature reads 90 °C or
   more.

   ```bash
   et-who --check || exit 1
   ls /dev/et*_mgmt                                              # exactly one: NV runs only on a single-card host
   L=/run/lock/etsoc-shire0.lock; D=/opt/et/bin/dev_mngt_service
   flock -n $L timeout -k 3 10 $D -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000   # release 1.3.1, BL2 0.20.0 (>= 0.19.0)
   for c in GET_MODULE_UPTIME GET_MODULE_VOLTAGE GET_ASIC_VOLTAGE GET_ASIC_FREQUENCIES GET_MODULE_CURRENT_TEMPERATURE; do
     flock -n $L timeout -k 3 10 $D -m DM_CMD_$c -n 0 -u 5000; done    # uptime reads; NOC 485 mV, ~482-486 on die, NOC 400 Mhz
   cd "$(mktemp -d)" && flock -n $L timeout -k 3 10 $D -m DM_CMD_GET_VMIN_LUT -n 0 -u 5000 && sha256sum dev0_vmin_lut.bin && python3 -c "import struct;b=open('dev0_vmin_lut.bin','rb').read();[print(i,[(f,v) for f,v in struct.iter_unpack('<HB',b[18*i:18*i+18])]) for i in range(11)]"
                                           # row 0's third pair is the NoC's boot entry (mV = 250 + 5*code): expect 485
   cd ~/nekko && flock -n $L timeout -k 3 10 env LD_LIBRARY_PATH=/opt/et/lib build/ettelem/ettelem sample --seconds 5 --every-ms 500 > build/nv-probe-idle.jsonl
                                           # the idle baseline: reg_mv.noc 485, die_mv.noc ~484, mhz.noc 400, sp.noc_w ~2.5 W
   flock -n $L timeout -k 3 10 env LD_LIBRARY_PATH=/opt/et/lib build/ettelem/ettelem sptrace build/nv-probe-sp0.bin
   strings -n 6 build/nv-probe-sp0.bin | grep -i 'overrid\|unable to validate'
   ```

   The temperature call's "High" values are latched watermarks, not readings (DESIGN.md §4). The SP trace holds the
   boot line `Overriding NOC -> … (0x2F)` only shortly after a boot: it is an 8 KB buffer that wraps. If the line is
   there, it shows that the regulator's read-back returns the bare code, as the set's check assumes.

**Only a write can settle these:**

- whether the regulator reads back codes 0x3A (540 mV) and 0x46 (600 mV) exactly. If not, the firmware loops until
  its watchdog resets the card (DESIGN.md §2);
- whether the on-die check passes at those voltages.

The development probe below is that write. It tries 540 before 600.

## 2. Development (aifoundry3)

Run everything from `~/nekko` on aifoundry3, after `et-who --check`. First sync this directory from the git checkout,
including `PREDICTIONS.sha256`. Never edit or `scp` over a script that a queue is running.

**Every block runs detached**, so that an ssh drop cannot signal it (DESIGN.md §7). Watch it with `tail -f`:

```bash
setsid nohup bash tools/claims-v3/nv/block.sh 1 --probe > build/claims-v3/nv-probe-p1.log 2>&1 < /dev/null &
tail -f build/claims-v3/nv-probe-p1.log                 # the first write: 540, 600, restore; about 1 min
cat build/claims-v3/aifoundry3/nv-probe/p1/block.json   # status ok, restored true, vmin_same true, bl2 0.20.0
flock -n /run/lock/etsoc-shire0.lock timeout -k 3 10 env LD_LIBRARY_PATH=/opt/et/lib build/ettelem/ettelem sptrace build/nv-probe-sp.bin
strings -n 6 build/nv-probe-sp.bin | grep -i 'unable to validate'    # the firmware's PVT/PMIC retries, if any
setsid nohup bash tools/claims-v3/nv/block.sh 1 --smoke > build/claims-v3/nv-smoke-p1.log 2>&1 < /dev/null &
                                                        # 485 and 600 mV, two configurations each; about 2 min
setsid nohup bash tools/claims-v3/nv/run-queue.sh tools/claims-v3/nv/schedule-dev-aifoundry3.txt \
    > build/claims-v3/nv-queue-aifoundry3.log 2>&1 < /dev/null &                 # passes 1-6, about 45 min
python3 tools/claims-v3/nv/reduce.py --card aifoundry3 --out build/nv-dev.json   # the development result
```

After the smoke, check its `windows.jsonl`: `t_first_ms − t_launch_ms` (the sampler's start) should stay under about
1 s; the window design allows 2 s.

If something needs changing (timing, limits, the heater, the burst drops), change it in nv.json only, rerun
development passes (7, 8 ...), and record the reason in PREREG.md §3. `predictions.json` never changes after it is
fixed.

## 3. Freeze

Do this only after DV2's validation on aifoundry2 has ended and the owner has released the card.

1. Fill every TBD in `PREREG.md` from the development result. In `prereg.json` put:
   - `nD`, `sdD` and `nDev`: the development n_D, its per-pass SD and the number of valid passes;
   - `tol`;
   - `val_passes`: the rule's N, given by `python3 tools/claims-v3/nv/nvlib.py nrule <sdD>`.
2. Take the validation host's binary hashes. At the root of the tree on aifoundry2 run:

   ```bash
   sha256sum build/ettelem/ettelem build/enercat_v2/host/enercat_host /opt/et/bin/dev_mngt_service build/sparsity_t2/host/sparsity_host
   ```

   Save the output to a file.
3. Freeze and commit:

   ```bash
   bash tools/claims-v3/nv/freeze.sh --binaries <that file>
   ```

   Commit `PREREG.md`, `prereg.json`, `PREREG.sha256` and `LOCK.sha256`, and record the PREREG hash in
   `docs/findings/03-experiments.md`.
4. On aifoundry2, in the tree that will run the validation, run `bash tools/claims-v3/nv/freeze.sh --check`. It must
   check.

## 4. Validation (aifoundry2)

```bash
echo "released for NV by <who>, <date>, after DV2's validation ended (owner's OK)" > build/claims-v3/aifoundry2/nv/CARD-RELEASED
# the read-only probes of §1, with aifoundry2's lock (etsoc-shire0) and expectations (1.3.1, BL2 0.20.0)
setsid nohup bash tools/claims-v3/nv/block.sh 101 --probe > build/claims-v3/nv-probe-p101.log 2>&1 < /dev/null &
                                                        # the steps only; records no power; applies the windows' on-die rule
setsid nohup bash tools/claims-v3/nv/run-queue.sh tools/claims-v3/nv/schedule-val-aifoundry2.txt \
    > build/claims-v3/nv-queue-aifoundry2.log 2>&1 < /dev/null &
python3 tools/claims-v3/nv/reduce.py --card aifoundry2 --dev-ref tools/claims-v3/nv/prereg.json --out nv-validation.json
```

Collect the data into `docs/reports/data/<date>-nv-<host>/` with a README (the framework's convention). The summary
says which theories survived.

## 5. Stopping, and what to do after an alert

**Stopping:**

- **Stop NV on a card, before its next block:** `touch build/claims-v3/<card>/nv/STOP`.
- **Stop every queue on the host:** `touch build/claims-v3/STOP`.
- A running block also checks both files between configurations. It then restores the rail and ends.
- **Stop a running block now:** `kill -TERM <its bash pid>`. The trap restores 485 mV and verifies it.
- Never use `kill -9`. The guardian would still restore, but a `kill -9` of the whole process group leaves the rail
  stepped until the next reset or boot, and `NV-STATE.json` dirty.

**After an alert.** The alerts are `ALERT-NV-RESTORE`, `-SET`, `-STATE`, `-FLASH` and `-RESET`, written in
`build/claims-v3/` and the NV directory; the host's STOP is set.

1. Every NV block refuses until a person has looked.
2. Read the pass's `steps.jsonl`, `dms/` and `run.log`.
3. Check the rail by hand (`GET_MODULE_VOLTAGE`, as in §1).
4. If it is not 485 mV, set 485 by hand with `DM_CMD_SET_MODULE_VOLTAGE -v NOC,485`, under the card lock and
   `timeout -k 3 10`, and read it back twice. A card that does not answer is the lab admin's.
5. **After `ALERT-NV-RESET`:** tell the lab admin. On aifoundry3 et-board-clock-guard must be re-run (TDP 0 and the
   600 MHz pin) before anyone measures there.
6. **After `ALERT-NV-FLASH`:** stop all NV work on the card and tell the lab admin. The VMIN table (the flash) changed,
   so read it (`GET_VMIN_LUT`, §1) and compare it with `vmin-start/`.
7. Then remove the ALERT files, the STOP file and a dirty `NV-STATE.json`. Record what happened in
   `docs/findings/14-card-behaviour.md`.
