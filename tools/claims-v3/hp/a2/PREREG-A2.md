# PREREG-A2: aifoundry2's same-day clock-step session (heat placement, DESIGN2 §3.4-3.5)

Written 2026-09-27 16:09 PDT, before the session, by `tools/claims-v3/hp/prereg.py --a2`. The session may run only on
**2026-09-27** (owner decision O3, 27 Sep 2026: aifoundry2's part is tried today from whatever temperature it rests
at; nothing carries over to another day). `a2/block.sh` refuses to run if any file below differs from its hash, or
this file from `PREREG-A2.sha256`.

These items take their predictions from the firmware source, not from development: the governor compares the integer
mean of the 34 truncated minion-shire sensors against `> 65` (TPM:656-679; `firmware.md` §2, §5). aifoundry3 cannot
develop them (its clock is pinned at 600 MHz and its trace is predicted latched), so freezing them before development
is not premature.

## The session

1. Gate: `et-who`, `who`, the process scan (no other user, no foreign device process, no `Runner.Worker`, no queue of
   ours), the card lock held from here to the end.
2. R0 probe (DESIGN2 §3.2): one 1 s die reading gives the rest reading **R**; `sptrace` p0; one 2 s `UNI32@4` launch
   (128 minions) with no sampler; `sptrace` p1 at once; `ettelem config`. Class: ALIVE (power lines and an "event
   received" line after them), STUCK (power lines only), SILENT (no governor line; at R >= 66 the governor sits in
   its thermal loop). Prediction: **SILENT (LOOP) if R >= 66, ALIVE if R <= 65**.
3. Smoke: the sampler, one 2 s `UNI32@4` launch, `sptrace`, `reduce_a2.py --check-pass`.
4. Branch on R:

| R | Class | What runs | Outcome |
|---|---|---|---|
| <= 62 | COOL | up to 2 A2 blocks from S_A2 = 63 (the 64 -> 63 falling edge) | TRIG-A, TRIG-B (if ALIVE) tested |
| 63 | COOL- | the same from S_A2 = 64 | tested; t_down shorter |
| 64-65 | MARGINAL | 1 A2 block from S_A2 = 65 | tested; None likely |
| >= 66 | WARM | one documentation run: a 7 s `UNI32@4` launch with the sampler (expected 600 MHz throughout, mean >= 66); then stop | **TRIG-A, TRIG-B, H12: NOT OBSERVABLE** -> INSUFFICIENT, reason "rest R C >= 66: the governor sits in its thermal loop at the 600 MHz bottom point (TPM:2316-2360; firmware.md:189-194), so no clock step can be provoked" |

   After a WARM first reading, up to 3 more 1 s readings are allowed today (`a2/block.sh 2..4`), each
   after the gate, each >= 2 h after the previous, the last before 22:00 local time. The
   session (probe, smoke, branch) runs at the first reading <= 65.
5. An A2 block: one warm-up run from rest (a 7 s `UNI32@4` launch, discarded); then the 8 runs
   (INT16@8, INT16@8, PER16@8, PER16@8, UNI32@4, UNI32@4, B4C@32, B4C@32) in a seeded shuffle (seed 200000 + block). Each run, inside its own 10 Hz `--reset-ms 1000`
   sampler: if the mean reads below S_A2 + 1, light lifts (7 s `UNI32@4` launches, at most 6, discarded) until
   it does (DESIGN2's single warm-up run, applied per run: a 128-minion run's heat is transient, so after its 10 s tail
   a cool die has already fallen below the edge and could give the next run no falling edge); the falling
   S_A2+1 -> S_A2 edge (cap 300 s, else void); one 7 s launch under `hold10`; 10 s more of sampling (the exit
   event); then, if TRIG-B is registered, `sptrace`. A second block runs only if the first block's last run reached its
   edge within 300 s. The session stops launching at 30 min of card time.
6. End: the log level restored (if set), `block_end`.

Safety (every run): the watcher stops the heater and the session at a mean or high >= 90 C; a run ends after 2
samples at mean >= 80, high >= 85 or board >= 73 W; the block aborts if the watcher dies or its state goes stale. No
TDP, threshold, clock, reset, firmware or driver change; the only SP state change is the log level (WARNING, the boot
default), and only when the probe is ALIVE (owner O2) and the level found at the session start is known (INFO or
DEBUG; it is kept in `build/claims-v3/aifoundry2/hp/sp-level.json`). An unknown level (a failed or empty dump) sets
nothing and TRIG-B is not tested; a level found at WARNING or lower is left as found. WARNING is recorded as pending
before the set command, restored at the end and checked with a dump; a set left pending (an abort) is restored before
the next attempt's probe.

The session card-time cap (30 min) holds for whole runs: a run starts only if its worst case (the lifts, the
300 s edge cap, the launch and its tail) fits in the time left. An aborted attempt (exit 1, or exit 3: someone else
on the card) writes `a2.json` with branch ABORTED; its data are never used, and a re-check (2-4) may follow (an ABORTED
attempt is no reading for the 2 h gap). The bypass variables `HP_A2_ANY_DAY`, `HP_A2_NO_GAP`, `HP_A2_IN_QUEUE` and
`HP_PARAMS_DIR` are refused unless `V3_DRY=1`; the caps are hplib.py's fixed defaults (no params file is read).

Outcome precedence (README departure 18, fixed before any data): a CI wholly inside +-band fails a SIGN or NONZERO
item even when it also excludes 0.

## Items

**TRIG-A (the clock test), prediction from source: H1 holds.** Per measured run (not a warm-up, the edge reached,
not void: heater rc, safety stop, sampler gap > 1 s), from the samples after t0 (the heater's own `t_start_ms`):
`t_up` the first sample at 800 MHz; `t_hi` the first sample at 800 MHz whose windowed high reads >= 66; `t_m` the
first sample whose mean reads >= 66; `t_down` the first **one-point** down-step 800 -> 700 MHz (a single 800 -> 600
change is an idle or boot reset and is excluded).
- Separating: (a) `t_m - t_hi` >= 1.5 s; or (b) a rise under a hot max: the high already reads >= 67 at `t_up`
  and the clock holds 800 MHz for >= 0.5 s.
- Fits H1: (a) `t_down` in [`t_m` - 0.3, `t_m` + 1.2] s, or (b). Fits H1': (a) `t_down` in [`t_hi` - 0.3, `t_hi` + 1.2] s.
- **Holds** if >= 5 separating runs over >= 2 blocks, >= 80% fit H1 and <= 1 fits H1'.
  **Fails** if >= 50% fit H1'. **None** otherwise, including not observable.
- The limit is stated: one day, one room.

**TRIG-B (the trace test), registered only if the probe is ALIVE (or ALIVE_CANDIDATE).** At WARNING. A dump counts
only if the newest entry of the previous dump reappears in it. The SP tick rate and offset are fitted by least
squares from the power lines against the heater's kernel starts and process ends; a residual above
300 ms voids the session's TRIG-B. Per thermal event E, with m(E) the host means and h(E) the highs within
+-0.5 s: discriminating if max h >= max m + 2; H1-consistent: a down event printing T >= 66 within +-1 of
some m, or an idle event printing T <= 65 within +-1 of some m with max m >= 65; H1'-consistent: T >= max m + 2.
First-event test per re-armed run (the high <= 65 in the 3 samples before t0): H1 puts the first down event in
[t_m - 0.3, t_m + 0.6] s, H1' in [t_hi - 0.3, t_hi + 0.6] s; a test counts for H1' only if it fits
H1' and not H1. **Holds** if >= 5 discriminating events, >= 90% H1-consistent, <= 1 H1'-consistent and no
first-event test for H1'; **fails** if >= 50% of the discriminating events are H1'-consistent or >= 2 first-event
tests fit H1'; **None** otherwise and on a SILENT card. An ALIVE_CANDIDATE whose first thermal down event has no idle
event after it is reclassified STUCK (None).

**H12 (DVFS-PLACE), exploratory, reported:** per block ln(min(t_down PER16@8, 7.0) / min(t_down INT16@8, 7.0)), each
placement the mean of its runs' ln min(t_down, 7.0), with its range. With at most 2 blocks it is not a test.

**Outcome words:** V3's (`card_verdicts`) over the one registered card, aifoundry2: PASS, FAIL, INSUFFICIENT (None,
including NOT OBSERVABLE). "Not registered" when the probe is not ALIVE.

## Parameters

```json
{
 "_what": "aifoundry2's same-day clock-step session (DESIGN2 \u00a73.5, owner decision O3 of 27 Sep 2026). Frozen by PREREG-A2.",
 "date": "2026-09-27",
 "card": "aifoundry2",
 "branches": {
  "COOL": {
   "rest_max": 62,
   "S_A2": 63,
   "blocks": 2
  },
  "COOL-": {
   "rest_max": 63,
   "S_A2": 64,
   "blocks": 2
  },
  "MARGINAL": {
   "rest_max": 65,
   "S_A2": 65,
   "blocks": 1
  },
  "WARM": {
   "rest_max": null,
   "S_A2": null,
   "blocks": 0
  }
 },
 "runs": [
  "INT16@8",
  "INT16@8",
  "PER16@8",
  "PER16@8",
  "UNI32@4",
  "UNI32@4",
  "B4C@32",
  "B4C@32"
 ],
 "warmup_run": "UNI32@4",
 "warmup_max": 6,
 "launch_s": 7,
 "idle_after_s": 10,
 "pre_launch_min_s": 5,
 "edge_cap_s": 300,
 "session_cap_s": 1800,
 "smoke_run": "UNI32@4",
 "smoke_launch_s": 2,
 "recheck_max": 3,
 "recheck_gap_s": 7200,
 "recheck_last_local_hour": 22,
 "seed_base": 200000,
 "trigA": {
  "sep_tm_minus_thi_s": 1.5,
  "rise_under_hot_high_c": 67,
  "rise_hold_s": 0.5,
  "fit_lo_s": -0.3,
  "fit_hi_s": 1.2,
  "holds_min_sep_runs": 5,
  "holds_min_blocks": 2,
  "holds_frac_h1": 0.8,
  "holds_max_h1p": 1,
  "fails_frac_h1p": 0.5
 },
 "trigB": {
  "window_s": 0.5,
  "disc_c": 2,
  "tol_c": 1,
  "first_event_lo_s": -0.3,
  "first_event_hi_s": 0.6,
  "holds_min_disc": 5,
  "holds_frac_h1": 0.9,
  "holds_max_h1p": 1,
  "fails_frac_h1p": 0.5,
  "fails_first_event_h1p": 2,
  "tick_resid_max_ms": 300
 },
 "C_down_s": 7.0
}
```

## Files and binaries (sha256)

| File | sha256 |
|---|---|
| `tools/claims-v3/hp/a2/block.sh` | `8e27fac2cd346db3459d47ef1193ce4a86a64d52eb071e8946c791000558b9f4` |
| `tools/claims-v3/hp/a2/hplib.py` | `3250f45e1e1e1cdcddfa5f074a741edbfb8729ef66f04ae89e1428158de52d38` |
| `tools/claims-v3/hp/a2/hplib.sh` | `f51577f090f6206a848afb9fa69b7694ad832a60d97d7ac05d20f14b612aacb4` |
| `tools/claims-v3/hp/a2/params-a2.json` | `b70b51ea58b3416b1cfa78221835f2083c169e858198c6c47bc7b18e0aa81f0d` |
| `tools/claims-v3/hp/a2/placements.json` | `3d0380c8860a0eff2a48ae2182abe018556a3503d31f996248aeb974dd632215` |
| `tools/claims-v3/hp/a2/reduce_a2.py` | `e9f16a93e8581c8a79c64212de97bd68b1c5f671f35f3c9a41708f200c0f4e33` |
| `tools/claims-v3/hp/a2/sptrace_events.py` | `19a66b4c73d516c4f65f573a4ccb0bee9bafe5357dd63b953f621fb325916662` |
| `tools/claims-v3/lib.sh` | `033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa` |

| Binary (role) | Path | sha256 |
|---|---|---|
| ettelem | `build/ettelem/ettelem` | `16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2` |
| ettelem_hp | `build/ettelem-hp/ettelem` | `ae5b63c53589cf371f9ef47a4e2294f61daf10f4027bdf2bc7f9a30196cb201d` |
| heater | `build/sparsity_t2/host/sparsity_host` | `bba697cbae72d359ca82d4dac7c119371fd02812202946ea2a3c08b6d274b8c4` |
| heater_kernel | `build/sparsity_t2/host/../kernel/sparsity.elf` | `990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24` |

This freeze replaces an unused earlier one (PREREG-A2.md sha256 `071ab6d4e2c58d39a2efff91d6d453c956c9f7a2fec32c4fb6b580ff6ce73c9d`); no a2 data existed.

## The lock (machine-readable; a2/block.sh checks every entry)

<!-- lock-begin -->
```json
{
 "binaries": {
  "ettelem": {
   "path": "build/ettelem/ettelem",
   "sha256": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2"
  },
  "ettelem_hp": {
   "path": "build/ettelem-hp/ettelem",
   "sha256": "ae5b63c53589cf371f9ef47a4e2294f61daf10f4027bdf2bc7f9a30196cb201d"
  },
  "heater": {
   "path": "build/sparsity_t2/host/sparsity_host",
   "sha256": "bba697cbae72d359ca82d4dac7c119371fd02812202946ea2a3c08b6d274b8c4"
  },
  "heater_kernel": {
   "path": "build/sparsity_t2/host/../kernel/sparsity.elf",
   "sha256": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24"
  }
 },
 "card": "aifoundry2",
 "files": {
  "tools/claims-v3/hp/a2/block.sh": "8e27fac2cd346db3459d47ef1193ce4a86a64d52eb071e8946c791000558b9f4",
  "tools/claims-v3/hp/a2/hplib.py": "3250f45e1e1e1cdcddfa5f074a741edbfb8729ef66f04ae89e1428158de52d38",
  "tools/claims-v3/hp/a2/hplib.sh": "f51577f090f6206a848afb9fa69b7694ad832a60d97d7ac05d20f14b612aacb4",
  "tools/claims-v3/hp/a2/params-a2.json": "b70b51ea58b3416b1cfa78221835f2083c169e858198c6c47bc7b18e0aa81f0d",
  "tools/claims-v3/hp/a2/placements.json": "3d0380c8860a0eff2a48ae2182abe018556a3503d31f996248aeb974dd632215",
  "tools/claims-v3/hp/a2/reduce_a2.py": "e9f16a93e8581c8a79c64212de97bd68b1c5f671f35f3c9a41708f200c0f4e33",
  "tools/claims-v3/hp/a2/sptrace_events.py": "19a66b4c73d516c4f65f573a4ccb0bee9bafe5357dd63b953f621fb325916662",
  "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa"
 }
}
```
<!-- lock-end -->
