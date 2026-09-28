# DV2: the DVFS-heat experiments (development tooling)

The owner asked (27 Sep 2026): **does voltage-frequency scaling act on the average temperature or on one hot shire,**
and **can the same computation run longer before throttling in some chip locations?** The design is `DESIGN.md`
revision 2 and `PREREG-DEV.md` (27 Sep, about 23:40-23:55 PDT, in the session scratchpad `dvfs2/`). These tools
implement the development part: tonight's run list (PREREG-DEV §4) on aifoundry2 and the read-only Z2 on aifoundry3.
The owner's method applies: theories and predictions first, all iteration on the development card, then a frozen test.
Nothing here is the replication (PREREG-DV2 is written at the freeze, after development).

**Theories** (DESIGN §3): TH1 the governor compares the integer mean of the 34 shire sensors (`> thr`), not the
hottest; TH2 the cards run the 0.20.0 governor (0.40 s blocking loop, one-call climb, exit to 600 MHz); TH3 no
hysteresis; TH4 heartbeat latency; TH5 placement delays the first throttle through the mean, diluted by the clock's
uniform adder; TH6 work (reported); TH7 recovery is thermal; TH8 the card states.

## Files

| File | What |
|---|---|
| `block.sh <pass>` | one pass on aifoundry2 (below); `queue.sh` runs it as `dv2 <pass>` |
| `dv2lib.sh` | shell helpers: a copy of `hp/hplib.sh`'s sampler, watcher, caps, edge, launch record, O2 log-level handling and probe, without the card-0 guard; plus the one-shot reset, the stop 2 s after the first 700 MHz sample, the C1m target stop, the gate before every run (et-who included), the post-run clock check (ABORT-LATCH), the dump scan, the night stop and the alerts |
| `dv2lib.py` | parameters, the branch table, the plans (C1m rows, the T-block cycle), the live watcher, `postcheck`, `resets`, `dumpcheck`, `z1sum`, the start rules (`natok`, `c1mok`), DEV-1's move rule, the level state (copied from hp), `envcheck`, and the V3_DRY simulator of the 0.20.0 governor; `selftest` |
| `dv2obs.py` | the per-run observables (A2's TRIG-A definitions: t_up, t_m, t_spm, t_hi, t_hi2, t_down, separating runs, the H-mean/H-max fits, G1-H, P_x, C1m's t_c) |
| `reduce_dv2.py` | `--dev` (dv2-dev.json: Z1, C1m's L600, G1-T counts, G4's L and L_pred/band/n_val by PREREG-DEV §1.4, the host bands, ADD's P_U, the DEV-n log, readiness); `--self-test` (planted effects) |
| `z2.sh` | Z2 on aifoundry3: standalone (no `../lib.sh`, no hp code), read-only, about 1 min |
| `hostlog.sh` | `sensors -j` every 60 s (Z1's host log; no card access) |
| `ettelem-dv2/` | `ettelem.cpp` = `hp/ettelem-hp/ettelem.cpp` + `residency <2-6>...` (DM 29, raw firmware states), `uptime` (DM 30), `threshold get`, and `sample --reset-once-file F`; `threshold set` is **not built** (refused before the node is opened) |
| `sptrace_events.py`, `placements.json` | copies of hp's (placements: + INT16@12, PER16@12, UNI32@20, ADD1) |
| `night.json` | tonight's clock windows (Z1 slots from 00:40, the smoke at 02:30, C1m start 02:30-03:00 and end by 04:05, NAT start 02:30-07:00, end 08:00) |
| `selftest/dry_all.sh` | the V3_DRY scenarios (every branch, the latch, an intrusion, the refusals, a queue run) |
| `../schedule-dv2-aifoundry2.txt` | tonight's queue |

## Passes (aifoundry2)

| Pass | What | Card time |
|---|---|---|
| 1001-1044 | **Z1**, one read-only cycle at its slot (00:40 + 10 min × k): gate; `flock -n` (skipped if held); `sptrace` (scanned for the error lines); `residency 2 3 4 5 6` + `uptime`; `config` (threshold must read 65, else ALERT-THRESHOLD and the night stops); a 1 s `sample --reset-ms 1000`. `z1.json`: reading, COOL (≤ 64), the governor lines | ≈ 5 s |
| 4001 | **the smoke** (row 4): R0; `sptrace`; Z2; `config`; one 2 s UNI32@4 launch inside the sampler with the one-shot reset; `sptrace`; the parser; the post-run clock check; the global-state table | ≈ 1 min |
| 5001 | **C1m** (row 5): LOOP only (R0 ≥ 66), a passed smoke, no Z1 reading ≤ 64 in the last 60 min, start 02:30-03:00, end by 04:05. 12 runs in DESIGN §5.4's rows; each: preheat (2 s UNI32@16 bursts, ≤ 30) to E+2 if below, the falling E+1 → E edge (E = R0 + 2; cap 300 s; the one-shot reset at E+1), up to 3 × 7 s launches until the mean reads E+4 (the watcher's stop file), a 10 s tail, the dump, the 600 MHz check (void if any sample off 600), the post-run check. Stops at 65 min, at a reading ≤ 64, or on two consecutive edge time-outs | ≤ 65 min |
| 6001-6032 | **NAT candidates** (row 6): exit at once unless `NAT-AUTOSTART` exists, the newest Z1 (≤ 15 min old) read ≤ 64, no NAT session ran tonight, and it is 02:30-07:00. Then: R0 → NAT-4/3/2/1 (else skipped), the probe (ALIVE required; otherwise ALERT-PROBE-SILENT, no heat), the smoke, WARNING (O2), ADD, T-blocks (DESIGN §5.5 cycle; NAT-1 its own rows), 2 RST runs, ADD, the level restored and checked, Z2, the global-state table | ≤ 60 min |
| 7xxx | **D1: refused** (the owner has not said yes; no threshold set path exists in this build) | 0 |

**A T-run** (T, ADD, RST): the gate; the 10 Hz sampler (`--reset-once-file`, or `--reset-ms 1000` for RST) and the
watcher; lifts (7 s UNI32@4, ≤ 4) while the mean reads < S+1; the falling S+1 → S edge (cap 300 s) with the one-shot
reset at S+1; the launch waits until the sampler reports the reset (≤ 1.5 s, else no launch); one launch
(`launch_s`, 7 s; DEV-2) with the heater's stop file written 2.0 s (DEV-3) after the first 800 → 700 step; a 10 s
tail; the sampler stopped (SIGTERM), then `sptrace`, the dump scan, the post-run clock check, the reset check, the
observables. A block starts only if its worst case (4 × 378 s) plus the closing ADD fits in the 60 min cap and before
08:00; rest 5 min between blocks (DEV-10: 10 min after a block with ≥ 2 edge time-outs); two consecutive edge time-outs
end the session. S = max(K − KS, the branch's S) with (N, KS) from DEV-1 (NAT-4/3); NAT-2 and NAT-1 keep their S.

## Safety (the owner's rules, enforced here)

- **Before any card work and before every run:** `who` (lib `others_present`), the process scan (`foreign_procs`),
  `et-who` (a holder of any other user), the `et_soc1` use count, and no other framework queue or block (hp, a2, V3)
  besides our own queue. Anything foreign ends the session at once with exit 3 (the card is left; a pending log level is
  restored by the next pass). Between launches and every 10 s of an edge wait, the same gate.
- **The card lock** (`/run/lock/etsoc-shire0.lock`) is held by lib's `block_begin` for a whole session; Z1 takes it
  with `flock -n` and skips its cycle if it is held. Samplers and the watcher start with the lock fds closed.
- **≤ 10 s per device process** (`hold10` = `timeout 10`, stdin closed); T-run chains ≤ 4 × 7 + 8 s, C1m ≤ 3 × 7 s,
  all within 150 s with telemetry running.
- **90 °C:** the watcher stops the heater (its stop file) and the session at a mean or high ≥ 90, writes ALERT-ABS90,
  the night stop and `build/claims-v3/STOP` (queue.sh stops); runs end after 2 samples at mean ≥ 80, high ≥ 85 or
  board ≥ 73 W.
- **No reset, no global-state change** except O2's SP log level (WARNING only after an ALIVE probe, the level found
  kept in `sp-level.json`, restored and checked at the end, a pending set restored by the next pass). The threshold,
  TDP, APM, clocks and voltages are never set; `ettelem-dv2` has no set path besides `loglevel` and the statistics
  reset (the same control-2 request every `--reset-ms` sampler of V3 and HP sent).
- **ABORT-LATCH** (R6): after every heating run the clock must read 600 MHz within 3 s of the kernel end and be at 600
  at the tail's end; otherwise stop all heat, restore the level, write `ALERT-LATCH.json`, `NIGHT-STOP` and the queue's
  STOP. Every dump is scanned (against the previous dump) for `failed to set operating point` / `failed to get soc
  power`: ALERT-FAILLINE, the night stops.
- **The night stops** (no DV2 pass touches the card again until the file is removed by a person) on ALERT-LATCH,
  ALERT-FAILLINE, ALERT-THRESHOLD, ALERT-ABS90. ALERT-PROBE-SILENT alerts only (no NAT that night).
- **Never aifoundry1:** `block.sh` runs on aifoundry2 only; `z2.sh` on aifoundry3 only (aifoundry1 refused;
  `ET_DEVICES`/`V3_DEVICE` refused); the simulator refuses aifoundry1-c0.
- **Dry-only variables** (`DV2_DRY_LATCH`, `DV2_DRY_LATCH_SILENT`, `DV2_DRY_THR`, `HP_DRY_REST`, `DV2_NIGHT_FILE`, `DV2_ANY_TIME`,
  `V3_FORCE`, `DV2_ETTELEM`, `DV2_HEATER`) are refused without `V3_DRY=1`. `DV2_NO_WARNING=1` is the owner's "no" to
  O2 (keeps INFO; the SP-line items are then not registered).

## Build, test, start

Builds (host only; never while a session runs; this worktree's own copies):

```bash
cd ~/claude/et-soc1-dvfs2
cmake -S tools/claims-v3/dv2/ettelem-dv2 -B build/ettelem-dv2 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/ettelem-dv2 -j4
cmake -S workloads/sparsity -B build/sparsity_t2 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/sparsity_t2 -j4
```

Tests (no device):

```bash
python3 tools/claims-v3/dv2/dv2lib.py selftest
python3 tools/claims-v3/dv2/reduce_dv2.py --self-test
bash tools/claims-v3/dv2/selftest/dry_all.sh          # every scenario, about 10 min; build/dv2-dry-tests/summary.txt
```

Start (the orchestrator, after checking `et-who`, `who` and that nothing else of ours runs on aifoundry2):

```bash
# aifoundry3, once, after its R3 queue ended (about 1 min of card time; read-only):
ssh aifoundry3 'cd ~/nekko && setsid nohup bash tools/claims-v3/dv2/z2.sh > build/claims-v3/z2-dv2.log 2>&1 < /dev/null &'
# aifoundry2 (this worktree): the host log and the queue
cd ~/claude/et-soc1-dvfs2 && mkdir -p build/claims-v3/aifoundry2/dv2
setsid nohup bash tools/claims-v3/dv2/hostlog.sh 08:15 > /dev/null 2>&1 < /dev/null &
touch build/claims-v3/aifoundry2/dv2/NAT-AUTOSTART        # PREREG-DEV row 3 done (the dry tests passed)
setsid nohup tools/claims-v3/queue.sh tools/claims-v3/schedule-dv2-aifoundry2.txt > build/claims-v3/queue-dv2-aifoundry2.log 2>&1 < /dev/null &
```

Watch: `build/claims-v3/aifoundry2/dv2/ALERT-*.json` (relay to the owner), `NIGHT-STOP`, `p1*/z1.json`,
`p4001/block.json`, `p5001/session.json`, `p60*/session.json`, `dev-log.jsonl`, `nat-candidates.jsonl`. Stop the queue:
`touch build/claims-v3/STOP` (it stops at the next pass boundary; a running session finishes its run and exits at its
next gate only if the STOP is also a night stop: `touch build/claims-v3/aifoundry2/dv2/NIGHT-STOP`). After the night:
`python3 tools/claims-v3/dv2/reduce_dv2.py --dev --data build/claims-v3/aifoundry2/dv2` (not on aifoundry2 while a
session runs).

## Departures from DESIGN/PREREG-DEV (fixed here before any DV2 card data; each is to be logged as a DEVIATION)

1. **Location.** The code and data live in the `et-soc1-dvfs2` worktree (branch `dvfs2`, from main), as the
   orchestrator directed, not in `et-soc1-heat` (PREREG-DEV §4's "W"). Data root:
   `et-soc1-dvfs2/build/claims-v3/aifoundry2/dv2/`. Its binaries are this worktree's own builds of the same sources
   (`build/sparsity_t2`: the heater kernel's sha256 equals the heat worktree's; `build/ettelem-dv2`).
2. **No D1, no T3.** No threshold set path exists (`ettelem-dv2 threshold set` refuses before opening the node; pass
   7xxx refuses). If the owner says yes, T3 (`thr.sh`: pending.json, watchdog, restore) must be written and dry-tested
   first (DESIGN §4.4), and the set path added then.
3. **No DM 36 marker.** It is optional (DESIGN §6 G3 "SP clock → host"); it is a SET-class request that reads the
   PMIC inside the SP, so it is left out. The SP→host fit uses OP lines only.
4. **The post-run clock check allows a transient re-climb** (≤ 2.0 s, back at 600 by the tail's end). The SP learns
   that a kernel ended only at the next heartbeat (about 1.05 s), so a thermal loop that exits just after the kernel
   end sees a stale busy flag and climbs (PUP) until PIDLE; the dry simulator of DESIGN §2.1's governor produced this
   and the literal rule ("stay at 600 for the rest of the tail") called it a latch. A latch holds the clock off 600: off
   600 at the tail's end, or off 600 for > 2 s, or no 600 within 3 s, is ABORT-LATCH.
5. **DEV-1 counts all 4 T-runs of a block** ("3 of 4 after block 1, 6 of 8 after block 2"; a block has one INT and one
   PER run, so the numbers fit only the 4 runs; K − S applies to all of them). S = max(K − KS, the branch's S): at
   NAT-3 the branch's floor R0 + 2 = 63 holds whatever the candidate.
6. **C1m's preheat.** DESIGN §5.4 gives no lift for C1m; a run whose mean reads below E+2 is preheated with 2 s
   UNI32@16 bursts (≤ 30) so that the falling edge can arm; normally the previous run's heat provides it. Not HP's
   ALL24: 768 minions draw about 76 W at 800 MHz, over the 73 W cap, if the card has left its loop (the dry test
   c1m-exit hit CAP_W that way); UNI32@16 is the C1m load's own power (about 64 W even at 800 MHz).
7. **C1m needs a passed smoke** (a 40xx block with status ok) that night; the NAT session runs its own smoke first.
8. **Lifts that cannot reach S+1** (4 lifts done) count as an edge time-out at once, with no 300 s wait.
9. **The one-shot reset**: the watcher touches the reset file at the first S+1 reading at or after the edge wait
   began (or at the edge if the mean passed S+1 before the wait); the launch waits until the sampler reports it
   (`resets: 1`, ≤ 1.5 s real time) and is skipped otherwise. `since_reset_ms` shows it; `resets` checks "exactly one
   reset before t0".
10. **Dumps are scanned against the previous dump** of the card (`last-dump.bin`); the night's first dump, with no
    previous one, is scanned whole (conservative).
11. **ALERT-PROBE-SILENT does not stop the night** (not in PREREG-DEV's list); no NAT session runs after it.
12. **T1 (`sptrace2.py`) is not built.** The copied `sptrace_events.py` walks the ring (8-byte entries) and the new
    lines (`new OP`, the two error strings) are matched by text; the binary POWER_STATUS records are not decoded. The
    SP-timed bands (DEV-4) and the SP-line items therefore wait for T1, verified on a real clock-change ring
    (readiness item).
13. **Z2 on aifoundry1-c1 is not built** (not tonight; it needs the owner's slot and the device-1 guard).
14. **Z1 is a queue pass per 10 min slot** (the queue's own gate, lock and bookkeeping), with `hostlog.sh` as a
    separate host process. Z1's predictions (b)-(d) need the kernel intervals and are left to the reducer's next pass.
15. **The smoke's t0 for the reset check** is the heater process start (it has no edge).
16. **"2.0 s after the first host sample at 700 MHz"** is read as 2.0 s after the first one-point 800 → 700 step (the
    trip). A 600 → 800 climb shows one 700 sample in 35 of 85 committed climbs (DESIGN §2.2 RA); the literal rule would
    stop those launches 2 s after the climb, before any trip. dv2obs's t_down uses the same step.
17. **C1m's clock window**: start 02:30-03:00 and end by 04:05 (night.json), besides the 65 min cap, so that a late
    queue cannot push C1m into the NAT window (PREREG-DEV row 5 says "about 02:35-03:40").
18. **A config read that fails** (threshold unreadable) fails that Z1 cycle or aborts the session, without the
    THRESHOLD alert; only a numeric reading other than 65 raises ALERT-THRESHOLD and stops the night.
20. **C1m ends when the card leaves its thermal loop**: a run start at a mean ≤ 65 or a clock off 600 MHz, a preheat
    burst that would start off 600 MHz, or a run with any sample off 600 MHz (that run is void) ends C1m, so heat off
    600 MHz is limited to one run's launch, under the caps; so does any safety stop in a C1m run. (PREREG-DEV row 5 stops
    only at a reading ≤ 64.)
21. **The gate runs before `block_begin`** too (its first act after the lock is a 1 s die reading), and every Z1 cycle
    restores a log level a killed or aborted session left pending, so the card is not left at WARNING after the night.
19. **Another framework process** means a shell running `tools/claims-v3/{queue.sh, */block.sh, hp/probe.sh,
    hp/run_*.sh, dv2/z2.sh}` without `V3_DRY` in its environment, other than our own queue and our children.

## Known limits

- The dry simulator's numbers mean nothing about the card; it checks the logic (branches, stops, the reset, the
  post-run check, the level handling, the queue).
- The ring at INFO holds under 1 s under a sampler: the dump after a run cannot be relied on for the governor's error
  lines; the post-run clock check is the primary latch detector.
- `reduce_dv2.py --dev` computes development estimates only; `prereg_dv2.py` (the freeze) is not written yet.
