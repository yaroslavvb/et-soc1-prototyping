# V3-E100: the idle reset against launch gaps, and one long launch with no gap (Q132)

*Pre-registered Sun 1 Nov 2026 (week 44), about 00:55 PDT, on the Intel, before any launch of this experiment. This commit freezes the design, the host change ([`host-gap.patch`](host-gap.patch)), the predictions ([`predictions.json`](predictions.json), from [`make_predictions_e100.py`](make_predictions_e100.py)), the protocol ([`protocol.json`](protocol.json)), the runner ([`run_e100.py`](run_e100.py)), the scorer ([`reduce_e100.py`](reduce_e100.py)) and the decision rules below. Any change after it goes in Amendments at the end, dated, before the data it touches. Data: `docs/reports/data/2026-11-01-e100-idle-reset/`.*

**The ask** (the owner, Sat 31 Oct 2026, about 23:30 PDT): *"Continue closing issues which are still open in https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers ... and run proper experiments on aifoundry"*. This is item 10 of that page's section 11: the governor's one-second idle reset in about 2% of processes.

**The question.** A desk reading of committed data ([`2026-11-01-q132-governor-desk`](../../../docs/reports/data/2026-11-01-q132-governor-desk/README.md) §b, post hoc) finds that the reset is the Master Minion's one-second heartbeat reading "no kernel in use" in the gap between two kernels. If so, the rate of falls is set by how much of the time no kernel is in use, and one long kernel has none. E100 controls the gap and predicts the rate.

**The chain under test** (public source, `aifoundry-org/et-platform` at `836a4ab`):

1. `device-minion-runtime/src/MasterMinion/src/services/sp_iface.c:76-100`, `sp_iface_mm_heartbeat_cb`: the heartbeat sends `event.state = KW_Get_Kernel_State()`, a snapshot.
2. `.../workers/kw.c:1915-1930`: busy only if a slot reads `KERNEL_STATE_IN_USE`; `:938` sets it after the launch's multicast, `:1653` frees the slot at completion.
3. `device-bootloaders/src/ServiceProcessorBL2/rtos_task/command_dispatcher.c:476`: the SP passes the state to `Thermal_Pwr_Mgmt_Update_MM_State`.
4. `.../services/thermal_pwr_mgmt.c:3110-3124`: on a busy-to-idle edge, POWER_IDLE at once; `:2177-2180`, `:1980-1985`: the boot point, 600 MHz.
5. `:879-880`, `:910-919`: the power branch climbs back only while the state is not idle.

## Card, slot and etiquette

- **aifoundry2, card 0, about 30 card-minutes.** A fall needs a live governor above 600 MHz: aifoundry3 (TDP 0) and aifoundry1 card 1 stay at 600 MHz, and aifoundry1 card 0 is out of this run.
- **Slot, epoch seconds: 1793521800 to 1793524200** (01:30 PDT to 01:10 PST; the clock goes back inside it). [`go_e100.sh`](go_e100.sh) reads it from the night's slot file, launches nothing before the start, checks E98's status and `et-who`, and waits with bounded polls for the card. [`run_e100.py`](run_e100.py) starts no run that could not finish, read and release 60 s before the end, and no process in the last 60 s.
- **The night's claim is E98's lane's:** `#community-lab` message `1566355908076765257` (for 8 h, until ~07:40 PST). E98's pre-registration `c8e84226` names E100 among the users under it. E100 makes no post and no release.
- **Nothing is set on the card:** no governor, TDP, threshold, clock, voltage or reset. `ettelem config` is read after every run, as `run_hpl.py` does, and the session ends unless it reads 65 W and 65 C. The sampler's statistics reset runs only in arm R (allowed by the owner's ruling of 31 October 2026; zeros at about 35 W never meet the power loop, the reason other runs sample without it).
- **The load:** int8 zeros, 1024 minions, 800 MHz, 35-37 W, die about 58 C in E80. Stops as E80: 85 C; 97 W on three samples. Runner: `run_hpl.py`'s own card lock, other-user checks and `timeout 10` on every device process.
- **The shared tree is not touched on the box.** The patched host is built from a copy of the source into `build/e100/`, the kernel ELF there is a byte copy of `build/sparsity_t2/kernel/sparsity.elf` (sha256 `990807f4...`, the file E80 ran), and this directory's files run from `build/e100/code/`.

## The host change

[`host-gap.patch`](host-gap.patch) to `workloads/sparsity/host/main.cpp`, applied to a copy, not committed to that file:

- `--fixed-iters N`: every launch after the calibration one runs N iterations. Without it a process rescales to 0.5 s at its calibration clock: 0.36 s at 800 MHz if it calibrated at 600 MHz, 0.50 s if at 800 MHz.
- `--gap-ms G`: after every launch of the `--seconds` loop, sleep a random time, uniform in 0 to 2G. Random because fixed gaps let the clock's own timing lock kernels to the heartbeat: the frozen model read 42% per heartbeat for a fixed 100 ms gap at 850,000 iterations and 17% at 930,000. A rate that hangs on the kernel's length would test the model, not the chain.

Built on the box from `main.cpp` at sha256 `0f53a7d5...`, the source's newest version, which is newer than `build/sparsity_t2`'s binary by the log-level registration of `27dce7f0`. The new binary's sha256 is `4625fe5c...` (recorded again in each session's `session.json`).

## Arms

Every arm: `--test fma --type int8 --values file:tools/claims-v3/kinds/tiles/int8/zeros.bin --shires 0xffffffff --per-shire 32`. Kernels of `--fixed-iters 850000`, 270.3 M cycles, 338 ms at 800 MHz. That length keeps every arm's kernel-plus-gap period away from 1000 ms over a small whole number (checked for each gap at 800 and 600 MHz). Sampler `ettelem sample --every-ms 100`. Ring after every run. Gate: die at most 62 C, at most 120 s.

A seeded random pause of 0-1 s before every process of a run but its first (`pause_seed` 100, each one a mark), so no process keeps one phase against the heartbeat.

| arm | launches | mean added gap | processes per run x runs per round | predicted falls in 144 heartbeats | band in 144 |
|---|---|---:|---|---:|---|
| A0 | `--seconds 7.5 --budget 9 --fixed-iters 850000` | 0 | 3 x 4 | 0.9 | 0-4 |
| A5 | the same, `--gap-ms 5` | 5 ms | 3 x 4 | 3.6 | 0-7 |
| A20 | the same, `--gap-ms 20` | 20 ms | 3 x 4 | 8.4 | 3-14 |
| A100 | the same, `--gap-ms 100` | 100 ms | 2 x 6 | 29.0 | 20-41 |
| N | `--seconds 0 --iters 10000000 --budget 7.5`: ONE kernel of 3.18 G cycles, 4.0 s at 800 MHz, 5.3 s if it stayed at 600 (the host's limit is 6 s) | none inside | 5 x 5 | 0 | 0 |
| R | A20 plus the sampler's `--reset-ms 1000` | 20 ms | 3 x 4 | 8.4 | 3-14 |

Two rounds in opposite order: A0, A5, A20, A100, N, R, then R, N, A100, A20, A5, A0. About 27 minutes, with a smoke first (a short process of each flag and one full-length long kernel; [`smoke_ok.py`](smoke_ok.py) must pass, or the session is not started). If the slot ends early the session stops where it stands, and the rules score what ran.

## Frozen predictions

[`make_predictions_e100.py`](make_predictions_e100.py) simulates the chain and nothing else, by events: a heartbeat every 1000.01 ms reads the slot; a busy-to-idle edge drops the clock to 600 MHz; while busy, each SP pass (every 200 ms) climbs a point; the kernels, gaps and windows as above. w is the idle window between kernels with no added gap: 2.0 ms, the zone's width in the committed boundaries; 1.3 ms, the host's mean gap, a floor; 2.5 ms, a generous top. The output is [`predictions.txt`](predictions.txt), and the numbers in the table are `falls_in_144` and `band_in_144` of `predictions.json`.

## Decision rules

Scored by [`reduce_e100.py`](reduce_e100.py), written before any pass is read. A FALL is a sampler reading of 600 MHz straight after a reading above 600 MHz, in a work process, more than 1.5 s after it started and more than 0.3 s before it ended. HEARTBEATS exposed are that window's length over 1000.01 ms. A process with any reading at 65 C or 65 W is left out and named; none is expected. The kernel counters are a second channel, reported beside. Bands are recomputed at the heartbeats really exposed: from the lower Poisson 95% limit of the rate at w = 1.3 ms to the upper limit at w = 2.5 ms.

- **D1, the rate follows the gap (primary).** PASS if, over the two rounds pooled, A100, A20 and A0 are each inside their bands.
- **D2, one long launch has no fall inside (primary).** PASS if N shows 0 falls inside a kernel after its climb, over at least 100 heartbeats inside kernels (fewer: NOT SCORED). Falls in N's process gaps are counted apart. Any fall inside a kernel refutes the chain.
- **D3, the gap decides each heartbeat (secondary, the sharpest).** A lattice (period within 0.006 ms of 1000.010 ms, phase free) is fitted on one round and scored on the other's A20 and A100, each way, pooled. For each lattice point with the clock above 600 MHz just before it: in a gap or in a kernel (1 ms either side of a kernel's edge is left out), against a 600 MHz reading in the next 250 ms. PASS at sensitivity ≥ 90% and specificity ≥ 95%. The committed data read 91 of 93 and 411 of 412 on process gaps.
- **D4, a fall lasts one heartbeat (secondary).** First 600 reading to first higher reading: median 1.0-1.25 s (committed: 1.10). In A100 a second heartbeat can land in a gap, so 3-35% of its falls should last 1.9 s or more (model: 13.9%).
- **D5, the statistics reset (secondary, if R ran).** R's falls inside A20's band at R's heartbeats: a once-a-second reset does not cause falls.

**What a failure means.** D1 failing with A100 near A0 says gaps do not matter: the chain is wrong on this build, and the cards do not run the public `kw.c` logic. D2 failing says something else also sets the idle state. Either is reported as it falls.

**What the first spec said, corrected before any data:** the spec of about 00:35 PDT had fixed gaps, 0.37 s kernels and "10-35% of A100's falls 2 s or more", with bands from f(1-f). The frozen model showed those fixed gaps lock to the heartbeat, so gaps became random, kernels 338 ms, and the bands and D4's numbers are those above.

## Checks before the launch

- [`selftest_e100.py`](selftest_e100.py), on two synthetic sessions laid out as `run_hpl.py` writes them: CHAIN reads D1-D4 PASS; RANDOM (falls at random times, whatever the gap) reads D1, D2 and D3 FAIL.
- Dry run: `run_e100.py --dry --only SMOKE` through `run_hpl.py`'s own dry path, exit 0, no device touched.

## Reduce

```bash
python3 tools/claims-v3/e100/reduce_e100.py <data dir>/s1 --out <data dir>/results.json > <data dir>/reduce.txt
```

## Amendments

*(none yet)*
