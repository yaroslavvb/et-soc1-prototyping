# V3-HP: heat placement and the thermal governor

The owner asked two questions: **Q1**, does the governor's thermal trigger respond to the average of the die sensors
or to one sensor; **Q2**, does the same work placed at the edges of the die run longer before the trigger than the same
work in the interior. The experiment design is `DESIGN2.md` (27 Sep 2026, written in the session scratchpad
`heatplace/`, a revision of `DESIGN.md` after `CRITIQUE.md`); these tools implement it. The rules below were fixed here
before any data. Suggested experiment number: the next free E-number when the runs are recorded in
`docs/findings/03-experiments.md`.

## The owner's decisions (27 September 2026)

- **O1.** A run may chain back-to-back launches for up to about 150 s. Every process is <= 10 s under `timeout 10`;
  the card lock stays held and the other-user check runs between launches; the device is released between launches.
  Tier L (chains) is the primary run length.
- **O2.** A block may set the service processor's (SP's) log level to WARNING, the boot default, on the lab cards. It
  is set only on a card whose R0 probe is ALIVE (and for aifoundry3's one-shot), and the level found is restored.
- **O3.** aifoundry2's part is tried **today**, from whatever temperature it rests at; if the clock step cannot be
  observed, the result says so ("NOT OBSERVABLE").
- **Cards.** Development on **aifoundry3**; validation on **aifoundry1 card 1** (the placement items) and
  **aifoundry2** (the clock items, today). No iteration after validation starts. **aifoundry1 card 0 is never used**:
  while card 1 runs, card 0 stays idle and a guard stops card 1's work if card 0 reads above 90 C.
- **90 C.** No run may take the die to 90 C.

## Files

| File | What |
|---|---|
| `block.sh <pass> [--smoke]` | one block on the local card (R0 probe and smoke, development rounds, V0, validation) |
| `probe.sh <pass>` | the R0 probe (DESIGN2 §3.2); `block.sh` execs it for T = 8 |
| `hplib.sh` | the shell helpers: O1's between-launch checks, the per-run sampler and watcher, preheat, the falling edge, the chain, the log level, the card-0 guard, the probe, the V3_DRY simulator hooks |
| `hplib.py` | parameters and their allowed ranges, which block kinds may run on which card (`ALLOWED`; card 0 refused), block plans, Williams orders, the statistics (t quantiles, three-outcome rules, V3 words, sign test), run observables, the live watcher (safety stops, edge, first 66), run and block checks (from the block's own `plan.json`), the locks (`vallock`, `a2lock`, `binhash`), the SP log level's per-card state (`level-*`), V0's edge rule (`v0edge`, `v0final`), the override check (`envcheck`: V3_FORCE included), the dry-run simulator |
| `run_queue.sh <schedule>` | the only way to start a queue of an hp schedule: refuses (before `../queue.sh` runs) aifoundry1 with `V3_DEVICE` other than 1, aifoundry3 with `V3_DEVICE` set, any other host, `V3_FORCE` without `V3_DRY`, a line that is not `hp`/`sleep`/`end`, and validation lines without `HP_PREREG_SHA256`; then execs `queue.sh` |
| `run_a2.sh <attempt>` | the only way to start aifoundry2's session: refuses `V3_FORCE` and relocated binaries without `V3_DRY`, an attempt that already ran, and (a cool-down) any attempt within 30 min of an ABORTED attempt that launched; then execs `a2/block.sh` |
| `deploy.sh <host> [--check] [--with-prereg]` | copies the hp code to `~/nekko` on aifoundry1 or aifoundry3 and checks every digest there (frozen files compared, never copied); refuses while a queue or block runs there |
| `placements.py`, `placements.json` | the placements, derived from `workloads/nocbench/analyze.py`'s MARTY map with every identity asserted (the design's `design2_sets.py` plus the run definitions); `placements.py --check` re-derives and compares |
| `sptrace_events.py` | the SP ring parser (8-byte entries, stale entries past the write offset), the level inference (`level-since`: from the entries new between two dumps only), the probe classes, ring-overlap coverage, the SP tick fit, TRIG-B; `--self-test` on the committed 22 Sep aifoundry3 ring |
| `reduce.py` | `--check-pass`, `--dev`, `--p1`, `--p3`, `--val` (the reducer; works on partial data) |
| `prereg.py` | `--a2` (freezes `a2/` and writes PREREG-A2; refuses once a2 data exist), `--val` (PREREG after V0 and P3; refuses once PREREG or validation data exist), `--check` |
| `params/` | per round and card: `params-r1/r2/r3-aifoundry3.json`, `params-v0-aifoundry1-c1.json`; `params-val-aifoundry1-c1.json` is written by `prereg.py --val` |
| `ettelem-hp/` | a copy of `tools/ettelem/ettelem.cpp` whose only change is `loglevel`: `warning` sets WARNING (2), not INFO; built into `build/ettelem-hp/` only |
| `a2/` | aifoundry2's same-day session: `block.sh`, `reduce_a2.py`, `params-a2.json`, frozen copies of `hplib.sh`, `hplib.py`, `sptrace_events.py`, `placements.json`, and `PREREG-A2.md` + `prereg-a2.json` + `PREREG-A2.sha256` |
| `selftest/` | `synth_blocks.py` (synthetic blocks with planted effects, in block.sh's format) and `run_selftest.py` (development -> P1 -> V0 -> P3 -> PREREG -> validation -> verdicts, with the checks of the 27 Sep code review: the lock and its refusals, V0's edges, P3's power at n_val, the CV ratio, D-S, D-L8, block completeness, POWER/WORK, the n_val cap; and departure 35: P1 and P3 unchanged by edited params files, refusals of unrecorded or mixed edges; departure 36: V0 and PREREG without S_L8 once L8 and G8 are dropped; departure 37: the Tier S POWER waiver) |
| `../schedule-hp-aifoundry3.txt`, `../schedule-hp-aifoundry3-r1c.txt`, `../schedule-hp-aifoundry1-c1.txt` | queue schedules |

## Pass numbers

`queue.sh` needs a number, so a pass encodes its round and block type: **pass = R x 1000 + T x 100 + k** (k = 1..99).

| R | round | | T | block type |
|---|---|---|---|---|
| 0 | R0 | | 1 | S (Tier S: one 7 s launch from the 65 -> 64 edge) |
| 1-3 | R1-R3 (development, aifoundry3) | | 2 | L16 (Tier L: INT16@32, PER16@32, UNI32@16) |
| 5 | V0 (card 1's calibration) | | 3 | L8 (MEM8, EDGE8, CEN8, INT16@16, PER16@16, UNI32@16) |
| 9 | validation | | 4 | G8 (W8b, E8b, N8b, S8b) |
| | | | 5 | CAL (V0's ALL24 chains; k >= 11 for the S_L8 edges) |
| | | | 6 | SCOUT (R1b: k = 1 the L16 part, 2 the L8 part, 3 the Tier S part) |
| | | | 7 | B1 (aifoundry3's one-shot) |
| | | | 8 | PROBE (R0) |
| | | | 9 | SMOKE (R0) |

For example `801` is the R0 probe, `901` the R0 smoke, `1701` R1a's one-shot, `1201` R1's first L16 block, `9201` the
first validation L16 block. The data go to `build/claims-v3/<card>/hp/p<pass>/`.

## Where each block may run (refused otherwise, exit 2, before anything touches a card)

| Card | Allowed | Everything else |
|---|---|---|
| aifoundry3 | R0 (801 probe, 901 smoke), R1a one-shot (1701), R1b scouting (1601-1603), R1-R3 S/L16/L8/G8 (and `--smoke` under an R0-R3 pass) | refused (no V0, no validation) |
| aifoundry1 card 1 (`V3_DEVICE=1`) | R0 (801, 901), V0 (5501-5503, 5511-5513), validation S/L16/L8/G8 (9xxx) | refused (no development, no scouting, no one-shot) |
| aifoundry1 card 0 (`V3_DEVICE=0`) | nothing: `hplib.sh`, `block.sh`, `probe.sh`, `a2/block.sh`, `hplib.py` (plan, params, the simulator) all refuse it, and `run_queue.sh` refuses any `V3_DEVICE` but 1 before `queue.sh` could read card 0 | only the read-only card-0 guard of a card-1 block reads it |
| aifoundry2 | only `a2/block.sh` (its frozen same-day session) | `hp/block.sh` and `hp/probe.sh` refuse (heating would spoil the a2 rest reading) |

`HP_PARAMS_DIR`, `HP_PREREG_DIR` and a2's bypasses (`HP_A2_ANY_DAY`, `HP_A2_NO_GAP`, `HP_A2_IN_QUEUE`) are honoured
only under `V3_DRY=1` (dry tests); on a card they are refused, and in a dry run they are recorded in `marks.jsonl`.
**`V3_FORCE`** (lib.sh's `block_begin` then re-runs a finished block into its own directory: `runs.jsonl` truncated,
telemetry overwritten) is refused without `V3_DRY` for every validation block, every block on aifoundry1 card 1 (R0, V0,
validation), every queue started by `run_queue.sh` and every a2 attempt started by `run_a2.sh`; on aifoundry3's
development blocks it is allowed and recorded. `V3_FORCE`, `HP_BIN_ROOT`, `HP_HEATER`, `HP_ETTELEM` and `HP_ETTELEM_HP`
are recorded whenever set (`marks.jsonl` `block_begin` "overrides", and a validation block's `prereg-lock.json`);
`reduce.py --val` refuses a validation block that ran with `V3_FORCE`. Every refusal of `hp_envcheck`, `run_queue.sh`
and `run_a2.sh` is appended to `build/claims-v3/hp-refused.jsonl` (dry: `build/claims-v3-dry/`).

## How to run

Everything runs from the tree's root: `~/nekko` on aifoundry1 and aifoundry3, this worktree on aifoundry2. Dry first,
then the smoke, then for real (AGENT.md §7):

```bash
V3_DRY=1 bash tools/claims-v3/hp/block.sh 801                 # no device access (below); then check et-who
bash tools/claims-v3/hp/block.sh 801                          # the R0 probe: about 20 s of card time
bash tools/claims-v3/hp/block.sh 901                          # the smoke
setsid nohup tools/claims-v3/hp/run_queue.sh tools/claims-v3/schedule-hp-aifoundry3.txt \
    > build/claims-v3/queue-hp-aifoundry3.log 2>&1 < /dev/null &
```

**Queues start through `run_queue.sh`, never `queue.sh` directly.** `queue.sh` reads the die temperature of the card
`V3_DEVICE` names before every block (and waits up to 30 min while it reads above 80 C), before `block.sh` can refuse:
with `V3_DEVICE=0` that is card-0 access outside the guard. `queue.sh` is frozen in the PREREG lock (and runs from its
deployed copy on aifoundry3), so the refusal is in the wrapper: `run_queue.sh` refuses aifoundry1 unless
`V3_DEVICE=1`, then execs `queue.sh`. On aifoundry1 set `V3_DEVICE=1` for everything (lib.sh refuses a missing
`V3_DEVICE` there); card 0 is never addressed except by the read-only guard sampler. `run_queue.sh` is in the PREREG
lock.

**Deploying the hp code** to aifoundry1 or aifoundry3 (only while no queue or block of the framework runs there;
the script checks and refuses otherwise): `bash tools/claims-v3/hp/deploy.sh aifoundry3` copies the code files and
prints every digest (code, the frozen `lib.sh`/`queue.sh`/`a2/`/`flip_thermal_model.py`, params, prereg, schedules);
`--check` only compares; `--with-prereg` also copies `prereg/` and `params-val-aifoundry1-c1.json` (after
`prereg.py --val`). Params files and schedules with other lines on the host are reported, never overwritten.

**The development sequence (aifoundry3), then V0, then PREREG.** R0 (801, 901) -> R1a (1701: the one-shot, a no-op
unless the probe said STUCK) -> R1b (1601-1603) -> `reduce.py --data build/claims-v3/aifoundry3 --card aifoundry3 --p1`
for D-L16/D-L8 (they move the edge the scouting blocks ran at; departure 35) -> edit `params-r1-aifoundry3.json`
(S_L 59-62, S_L8 61-64) -> R1c (`schedule-hp-aifoundry3-r1c.txt`) -> P1 (`--p1`) -> `params-r2-aifoundry3.json` -> R2 -> R3 -> `params-v0-aifoundry1-c1.json` (aifoundry3's frozen S_L,
L8_offset = S_L8 - S_L and T_cal from R3's CAL chains) -> **V0 on card 1**: 5501-5503 (the S_L edges; a block ends at
once, "skipped", when the rule has settled), then 5511-5513 (the S_L8 edges start from card 1's settled S_L + the
offset, so they wait for 5501-5503) -> on aifoundry1:
```bash
python3 tools/claims-v3/hp/hplib.py v0final --data build/claims-v3/aifoundry1-c1 --card aifoundry1-c1 --write v0.json
V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/hp/block.sh --binhash > bin-c1.json     # card 1's binaries (no device access)
```
-> P3 on aifoundry3's data with card 1's V0 blocks (for CV_card1; P3 refuses without them):
`reduce.py --data build/claims-v3/aifoundry3 --card aifoundry3 --p3 --cal-card1 <copy of aifoundry1's build/claims-v3/aifoundry1-c1> --out reg.json`
-> `prereg.py --val --registration reg.json --v0 v0.json --bin-c1 bin-c1.json --probe-a3 .../aifoundry3/hp/p801/probe.json
--probe-c1 .../aifoundry1-c1/hp/p801/probe.json` (it prints PREREG.md's sha256: record it) -> copy `prereg/` and
`params/params-val-aifoundry1-c1.json` to aifoundry1 -> validation blocks (append their lines to
`schedule-hp-aifoundry1-c1.txt`) -> `reduce.py --data build/claims-v3/aifoundry1-c1 --card aifoundry1-c1 --val --prereg
tools/claims-v3/hp/prereg/prereg.json --out verdicts.json`.

**The lock.** `prereg/PREREG.md` is the root: its sha256 is in `prereg/PREREG.sha256`, and its lock block holds the
sha256 of `prereg.json` (items, predictions, bands, beta, primary, n_val), `params-val-aifoundry1-c1.json`, `block.sh`,
`hplib.sh`, `hplib.py`, `probe.sh`, `reduce.py`, `sptrace_events.py`, `placements.json`, `ettelem-hp/ettelem.cpp`,
`run_queue.sh`, `../lib.sh`, `../queue.sh`, `tools/ettelem/flip_thermal_model.py`, `tools/ettelem/ettelem.cpp`, and card
1's heater, its kernel, the sampler and ettelem-hp. PREREG.md and PREREG.sha256 certify only each other (editing both
would pass until the first validation block records the hash), so **the sha256 `prereg.py --val` prints is recorded
outside the tree** (commit PREREG.md and note the value in `docs/findings/03-experiments.md`) and every validation
block needs it: `HP_PREREG_SHA256=<sha> V3_DEVICE=1 setsid nohup tools/claims-v3/hp/run_queue.sh
tools/claims-v3/schedule-hp-aifoundry1-c1.txt ...` (`run_queue.sh` refuses validation lines without it, and
`vallock` refuses a block without it or with another value; a card-1 queue started earlier without it fails every
validation line it meets, so start a new one). `block.sh` (every 9xxx pass) runs `hplib.py vallock`: PREREG.md against
PREREG.sha256 and HP_PREREG_SHA256, every hash, params-val field by field against prereg.json's frozen values, the
binaries this block would run, and no earlier validation block under another PREREG; it writes `prereg-lock.json`
(with the recorded hash and the overrides set) into the block. `prereg.py --val` also lists card 1's validation
directories and deployed PREREG on aifoundry1 over ssh (`ls` and `sha256sum` only; or `--card1-listing FILE` with the
output of `prereg.CARD1_LIST_CMD` run there) and refuses if any validation directory exists there, if aifoundry1
already holds a PREREG (unless `--replace-unused`), or if the listing cannot be had. `reduce.py --val`
checks PREREG.md, the prereg.json it is given, the locked files (a reducer fix after the freeze only with
`--amendment`, recorded), and every validation block's `prereg-lock.json`, `binaries.json` and `code.sha256`.
`prereg.py --val` and `--a2` never re-freeze once data exist; an unused freeze is replaced only with
`--replace-unused`, and the new file records the hash it replaces.

**aifoundry2 today (O3).** `prereg.py --a2` was run before the session (it copies the modules into `a2/` and hashes
every file there, `../lib.sh` and the binaries `a2/block.sh` resolves on this host; `a2/block.sh` refuses on any
difference, or on another day). Attempt 1 ran at 16:51 on 27 Sep: rest 67 C, WARM, probe SILENT; `a2/` is frozen for
good. Every further attempt starts through `run_a2.sh`, which adds the checks the frozen code lacks (V3_FORCE, relocated
binaries, a re-run attempt, the 30 min cool-down after an ABORTED attempt that launched; departures 31-32):

```bash
cd ~/claude/et-soc1-heat
V3_DRY=1 HP_DRY_REST=61 bash tools/claims-v3/hp/run_a2.sh 1     # dry: the simulator at a 61 C rest (COOL)
bash tools/claims-v3/hp/run_a2.sh 1                             # the session: gate, probe, smoke, branch on R
bash tools/claims-v3/hp/run_a2.sh 2                             # only after a WARM reading: >= 2 h later, < 22:00
python3 tools/claims-v3/hp/a2/reduce_a2.py --data build/claims-v3/aifoundry2/hp/a2 --out verdicts-a2.json
```

**Binaries.** On aifoundry1 and aifoundry3 the blocks use `~/nekko`'s `build/ettelem/ettelem` (the V3 sampler) and
`build/sparsity/host/sparsity_host` (the heater), and `build/ettelem-hp/ettelem` for the log level only. On aifoundry2
lib.sh names `build/ettelem/ettelem` and `build/sparsity_t2/host/sparsity_host` relative to the tree, so this
worktree has its own builds of the same sources (27 Sep, `nice -j4`; the heater includes the 25 Sep log-level-race fix,
which the campaign's 21 Sep `sparsity_t2` predates):

```bash
cmake -S tools/ettelem -B build/ettelem -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/ettelem -j4
cmake -S workloads/sparsity -B build/sparsity_t2 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/sparsity_t2 -j4
cmake -S tools/claims-v3/hp/ettelem-hp -B build/ettelem-hp -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/ettelem-hp -j4
```

`HP_BIN_ROOT=<dir>` points every binary at another tree's build directory instead, e.g.
`HP_BIN_ROOT=$HOME/claude/et-soc1-prototyping/build` for the campaign's own aifoundry2 binaries (it then also expects
`<dir>/ettelem-hp/ettelem`); `HP_HEATER`, `HP_ETTELEM` and `HP_ETTELEM_HP` override one binary each. Every block
records the sha256 of the binaries it ran (`binaries.json`, `binaries.sha256`); validation and the a2 session refuse
any binary whose sha256 differs from the lock, wherever it comes from. Never build into a directory a running queue uses.

**V3_DRY=1** touches no device: lib.sh's stubs, plus an accelerated simulation (`hplib.py dry-*`: a two-stage thermal
model per card, the aifoundry2 governor stepping 800 -> 700 -> 600 MHz above 65 C, fake SP rings filtered by the
simulated log level and probe class). Time runs `HP_DRY_SPEED` (40) times faster on a virtual clock kept in
`build/claims-v3-dry/hp-sim/vt0`, so a block takes seconds to a minute and its data (in `build/claims-v3-dry/`) go
through the reducer. `HP_DRY_PROBE=ALIVE|STUCK|SILENT` picks the probe class, `HP_DRY_REST=<C>` the rest reading,
`HP_DRY_REST_C0=<C>` card 0's temperature (the guard's `dry-guard` readings: card 0 itself is not simulated). Test
hooks: `$HP_DRY_DIR/intrude` (an intrusion: the exit-3 paths), `HP_DRY_SPTRACE_FAIL=<regex>` (a dump fails),
`HP_DRY_LOGLEVEL_RC=[level:]rc` (the SP applies the level but the call fails), `HP_DRY_PIDLE_BUMP=<W>` (idle power),
`HP_DRY_CARD0_TEST=1` with `HP_DRY_CARD0_LOCK`, `HP_DRY_HOLDERS` (the card-0 idle check), `HP_DRY_LOCK_DIR` (the card
lock file). The simulator's numbers mean nothing about the cards.

## What a block does

See the headers of `block.sh`, `a2/block.sh` and `probe.sh`. In short: nobody else on the card (lib `others_present`,
`ours_running`, the et_soc1 use count; exit 3 otherwise); the R0 probe must exist; `block_begin` takes the card lock
for the whole block; on card 1 the card-0 guard starts (card 0 must read <= 85 C); WARNING only if the probe was ALIVE;
burn-in CAL run(s) (two for a session's first block) then the placements in a Williams order (S: a seeded shuffle);
each run inside its own 10 Hz `--reset-ms 1000` sampler and a live watcher: ALL24 preheat bursts to the target, the
mean's falling S+1 -> S edge (cap 600 s), then the chain or the single launch; after the run, an SP dump on a TRIG-B
card; void runs re-run once at the end (`hplib.py blockcheck`, with the round and params of the block's own
`plan.json`; if it cannot run, the block fails with `blockcheck_failed` in marks, never a silent "ok").

**Safety** (the watcher, every sample): mean or high >= 90 C -> the heater's stop file, the block aborts and the
session stops (`build/claims-v3/STOP`); two samples in a row at mean >= 80, high >= 85 or board >= 73 W -> the run
ends (void); card 0 > 90 C or its guard output 10 s stale (seen by the watcher or by the between-launch check), a guard
that does not restart, or card 1's W_idle at the edge 2 W above this session's first measured run (the secondary
proxy, checked at the edge and also when the edge wait times out, so a rise that lifts card 1's rest above its edge
is caught) -> the block aborts and the session stops. The shell checks the watcher at every step: if it is gone or its state
is older than 3 s (real time), the block aborts. The heater's `--stop-file` ends a launch within its current 0.5 s
inner launch.

**Card 0 idle** (card-1 blocks and the probe, at block start and between launches; DESIGN2 §6.1): no process of ours
with `ET_DEVICES` naming card 0, no holder of `/dev/et0_*` or `etsoc-shire0.lock` in `et-holders` (any user, ours
included, except our guard), no flock on `etsoc-shire0.lock` (`/proc/locks`, read, never taken) -> exit 3. An orphaned
guard of ours (a card-0 `ettelem sample --every-ms 1000` whose parent is no hp block) is stopped with SIGTERM first.

**The SP log level** (O2; DESIGN2 §3.2-3.3). WARNING is set only on a card whose probe is ALIVE (or ALIVE_CANDIDATE;
in validation also registered), or for aifoundry3's STUCK one-shot, and only when the level found in the idle dump is
known: INFO or DEBUG. The level first found is kept per card in `build/claims-v3/<card>/hp/sp-level.json` and is the only
restore target. The state is marked pending and `LEVEL_SET` is set before the set command (a set that times out is
restored too); at the block's end the original is restored and a dump must read it again (then pending is cleared;
`level_check` in marks, and the block note). An unknown level (failed or empty dump) sets nothing and the block runs
without TRIG-B; a level found at WARNING or lower is left as found. After an exit 3 the card is left at once; the next
block, probe or a2 attempt on the card restores the pending level first. **The level is always inferred from the
entries new between two dumps taken back to back** (`sptrace_events.py level-since`; the probe: new between p0 and
p1), never from the whole ring: the 4 KB ring keeps about 50 entries, so INFO-era Host_Iface lines survive a switch to
WARNING, and the whole ring read INFO on a card at WARNING (a restore that failed passed its check, most surely after
the one-shot, whose chain is kept inside the ring on purpose; and a WARNING card with a governor line read STUCK
instead of ALIVE_CANDIDATE). At INFO or DEBUG each dump request is itself logged, so an INFO card always shows a host
line in the delta of two back-to-back dumps; none means WARNING or lower. A delta reading INFO while the ring holds
DEBUG voltage lines is UNKNOWN at a block's start (nothing is set).

## Departures from DESIGN2 (and completions where it left a detail open)

1. **Seeds**: block seed = 100000 x card index + pass (DESIGN2 §6.3 says 1000 x; the four-digit passes would collide).
   Williams sequence = (k - 1 + card index) mod the number of sequences, so consecutive blocks walk the sequences.
2. **R1b** is three blocks (1601 L16 part, 1602 L8 part, 1603 Tier S part); 1602 and 1603 start with a burn-in CAL run.
3. **V0**: three ALL24 chains per edge, no extra burn-in (the design's budget of <= 18 chains); `v0edge` applies §6.1's
   rule from the finished V0 blocks.
4. **kappa's network fit** uses every uniform-power or idle sample of the block (the CAL run(s), the ALL24 preheats,
   the cool-downs and edge waits: everything but each measured run's launch and the 30 s after it), not the CAL chain
   alone. On the synthetic self-test a network fitted to the CAL chain alone (about a minute) could not identify the
   slow stages that carry heat into runs minutes later: a planted kappa of 1.0 came back 0.41-1.02, and 2,000 in L8.
   The gate is unchanged (floor match >= kappa_gate in the run's window).
5. **B1 one-shot**: 7 s launches (so the WARNING ring, about 50 CRITICAL lines, keeps the whole chain), ONE chain of
   <= 150 s (O1; the second chain of the first version was about 300 s of near-continuous load, which no owner decision
   covers). If it does not reach 66 C, the one-shot is reported as "no crossing" (`b1_no_crossing` in marks).
6. **A2 warm-up**: the block's first run from rest is the discarded warm-up; each measured run then lifts the die with
   light 7 s UNI32@4 launches (at most 6, discarded, in its own sampler) until the mean reads >= S_A2 + 1, and waits for
   the falling edge. A 128-minion run's heat is transient: in the dry simulation, a separate warm-up run followed by
   its 10 s tail left the die below the edge, and no run got an edge. PREREG-A2 states this.
7. **TRIG-B first-event test**: a run counts for H1' only if its first down event fits H1' and not H1 (the windows
   overlap when t_m - t_hi is small).
8. **SP tick fit anchors**: every heater process of the block or session (preheats, lifts, probe and smoke included):
   its first kernel start (launch -1's `t_start_ms`) and its last kernel end (the master minion goes idle there; the
   idle event follows within one pass). The 300 ms void rule applies to every SP power line inside the anchors' span:
   with the card lock held, each must belong to one of our processes.
9. **The SP ring** is walked with 8-byte entries (the 1.3.1 cards' lines are 56 and 64 bytes long); DESIGN2 §9 said to
   import `parse_sptrace_voltage.ring_entries`, which needs 16-byte multiples and walks none of these rings (as
   `tel/reduce.py:1171-1172` already notes). The self-test finds the design's 26 down and 27 idle lines (52 with
   timestamps, one whose timestamp the newest entry's tail overwrote).
10. **Failed reset windows** (Delta-hot, iota_io): ettelem does not log whether a stats reset succeeded; a window
    lasting > 1.5 x reset_ms or holding < 3 samples is dropped.
11. **tau_c offline** uses the watcher's rule exactly: after the last reading >= S+2 before t0, the first S+1, then
    the first reading <= S (a flickering integer mean does not move it).
12. **P1**: an item is "reachable" if h(n_max) <= 0.7 x max(band, |development estimate|); **L16 is never dropped**
    (§8), its items are then reported, not tested. n_max = 12 (§8's n = 5-12).
13. **Fixed predictions** (CONC and MAP SIGN+, LIN EQUIV, §4.1) are registered only if development supports that
    prediction (and the power rule holds); otherwise reported, not tested, with the reason.
14. **The chain cap**: no launch starts if it could end after 150 s (elapsed + launch + 1 s > cap).
15. **A session's first block** (two CAL runs): no heating block (S, L16, L8, G8, SCOUT, CAL; not the probe, the
    smoke or the one-shot) ended ok on this card within the last 30 min.
16. **Preheat bursts** write to `heater-<run>-pre.out`, so t0 (the first kernel start of `heater-<run>.out`) is the
    measured launch's.
17. **G0** (the Foster fit of the V3-IDLE heat curves before R2) is not implemented; `--p1` says so in D-L8.
18. **Outcome precedence** (DESIGN2 §2.3 left it open; fixed here before any data, pending the owner's review): a 99% CI
    lying wholly inside +-band FAILS a SIGN or NONZERO item even when it also excludes 0 (the effect is shown
    negligible), e.g. [0.017, 0.033] against band 0.095 fails SIGN+. P3's candidate typing follows it: a development CI
    inside the band is an EQUIV candidate even if it excludes 0. `hplib.py selftest` has the case; PREREG states it.
19. **TRIG-A on card 1** (DESIGN2 §3.4, last paragraph) is waived: this implementation has no card-1 clock-step
    protocol (its validation runs void any sample off 600 MHz). PREREG says so and the verdicts list it as
    "not tested (waived in PREREG)".
20. **params-val no longer carries PREREG.md's sha256** (DESIGN2 §6.3 says it does): PREREG.md now hashes params-val
    (and prereg.json), which would be circular. PREREG.md is the root; its sha256 is in PREREG.sha256 and printed by
    `prereg.py --val`.
21. **V0**: validation's own edge ranges, S_L 58-62 and S_L8 60-64 (development keeps 59-62 and 61-64); the S_L8 series
    starts from card 1's settled S_L + the frozen L8 offset; an edge whose three chains are all void settles at the
    previous edge (none: V0 cannot settle, and `prereg.py --val` refuses). `prereg.py --val` requires `v0.json`.
22. **P3**: n_val per type (§2.4 step 5): L16 by its primary item PLACE-t (the only primary DESIGN2 names, §0 and
    §4.1), or 5 when PLACE-t cannot reach step 4. S, L8 and G8 have no primary item in DESIGN2: their n_val is the
    smallest n in [5, n_max] at which ANY candidate of the type meets step 4 (the smallest projected n), or 5 when none
    does (fixed 27 Sep before P3, after the re-verification found that the stand-in primaries CONC, PLACE8-t and GRAD-EW
    capped every other item of the type at 5 whenever the stand-in was no candidate: on the synthetic P3, GRAD-NS
    reaching step 4 at n = 12 dropped G8). Every candidate of the type is then re-checked at that n_val and registered
    only if h(n_val) <= 0.7 x band or |estimate| (else "reported, not tested", with the power); the card-1 cap (§8)
    then drops types in reverse priority as before. CV (§2.4): aifoundry3's tier-L CAL chains of its R3 L16
    blocks at the frozen S_L, and card 1's V0 chains at the settled S_L edge; P3 refuses without card 1's V0 data unless
    `--allow-no-card1`, which is stated in the output. D-S (P1) is applied in P3 (PLACE-tS). D-L8 takes CEN8's median.
23. **POWER and WORK** (EQUIV) on every pair of every registered item: CONC's (INT16@32, UNI32@16) and
    (PER16@32, UNI32@16), MAP's (B4NE, B4SW), LIN's (PER16@16, INT16@16) and the identity UNI32@16 = INT16@16 + PER16@16
    (power UNI - (INT + PER), work ln(ops_UNI / mean(ops_INT, ops_PER))).
24. **Validation block count**: per type the first n_val usable blocks in pass order are used (void or incomplete
    blocks are replaced by later ones); later blocks are listed as extra and never used; fewer than n_val usable blocks
    gives INSUFFICIENT (no verdict from a partial set).
25. **Block completeness** (§4.4): a block enters the items only if every registered pair in it is complete; in
    development every registrable item counts as registered, in validation the registered items (and their pairs).
26. **The card-0 guard's lifetime** is 2700 s, restarted between runs after 1500 s (a SIGKILLed block's orphan ends by
    itself); background processes start with the card-lock fds closed; a block refuses to start without the card lock
    file.
27. **a2**: an aborted attempt (exit 1 or 3) writes `a2.json` with branch ABORTED (its data never used; no reading for
    the 2 h gap), so a re-check can follow; a run starts only if its worst case fits in the session cap; the limits are
    hplib.py's fixed defaults (no params file); the bypass variables work only under V3_DRY.
28. **C_L is the chain cap** (§2.1 defines C as the chain cap): a params file that sets `chain_cap_s` alone carries
    `C_L` with it, and one where they differ is refused (a run with no crossing heated for 100 s was entered as ln 150).
29. **blockcheck** reads the round from `plan.json`'s `info` and uses the params recorded in `plan.json` (as the reducer
    does); a blockcheck that cannot run fails the block (27 Sep: it read a top-level `round` that does not exist, so
    every block was r1: on card 1 it raised and no void run was ever re-run, and R2/R3 blocks were checked with R1's
    params; the block still ended "ok").
30. **The heater's kernel** is passed with `--kernel` (the path the locks hash as `heater_kernel`): the heater
    otherwise loads its compiled-in absolute `KERNEL_ELF`, which a relocated heater (`HP_HEATER`, `HP_BIN_ROOT`) does
    not share with the hashed path.
31. **The a2 wrapper** (`run_a2.sh`): `a2/` is frozen with data, so V3_FORCE, relocated binaries and a re-run attempt
    are refused in front of it, and every refusal is recorded.
32. **The a2 cool-down**: after an ABORTED attempt that launched anything, the next attempt waits until 30 min
    (DESIGN2 §4.4's session gap) after that attempt's end, so R is not read on a die warm from our own aborted runs
    (PREREG-A2 allows a re-check at once; this only delays it). If `a2/block.sh` is run directly the limit stands: a
    re-check right after an abort can read R 1 C high and shift the branch.
33. **H11** is FAIL as soon as one registered SIGN item FAILs, INSUFFICIENT if none fails and one is INSUFFICIENT, else
    PASS (it read INSUFFICIENT for [FAIL, INSUFFICIENT]).
34. **The card-0 guard's grace**: a guard file with no line yet is stale 30 s after the watcher starts, as its comment
    always said (it was stale at once; latent, since `hp_guard_start` waits for a first line).
35. **P1 and P3 read every run parameter from each block's own files** (`plan.json`'s params, the runs' recorded
    `edge`), never from the current params files, which are edited between rounds. 27 Sep: after `params-r1` was
    edited to S_L 61 / S_L8 64 for R1c, `--p1` on the R1b blocks (run at S_L 60 / S_L8 63) moved D-L16 and D-L8 from
    the edited values: it said "S_L 62" and "censored at S_L8 = 64: L8 and G8 dropped" (correct: S_L 61, S_L8 64,
    L8 and G8 kept). Now D-L16 and D-L8 move the edge the scouting runs recorded (`ran_at`); P3's CV_a3 uses the S_L
    its R3 L16 blocks ran at, and V0's settled edge is re-derived with the params the V0 blocks recorded. A block
    whose `plan.json` has no params, or whose runs' edges disagree with them or with each other, is refused. An item
    (or a D-rule) whose blocks ran at different edges or run parameters is refused, not pooled (DESIGN2 pools only
    "identical parameters", §2.4, §5.4). beta is the one exception: it is a within-block slope pooled over
    development (§2.2), so it pools across edges, and `beta_edges` lists them. Each P1/P3 item lists its blocks'
    `edges`. The current params file still supplies the analysis settings (n_min, n_max, reg_factor, and the fixed
    bands), and the output notes where it differs from the edges the blocks ran at. `--dev` and `--val` still fall
    back to the current params for a block without them (a validation block always has them).
36. **S_L8 only while L8 or G8 is kept** (27 Sep 2026, coordinator decision (c), before any validation data; D-L8 on
    R2's 2301 was expected to drop L8 and G8): `hplib.py v0final` requires card 1's settled S_L8 only if params-v0's
    `types` keeps L8 or G8 (V0's S_L8 passes 5511-5513 are then skipped), and `prereg.py --val` requires it only if the
    registration's `types_kept` does; otherwise the frozen S_L8 is aifoundry3's R3 value, unused (no L8 or G8
    validation block is planned), and PREREG.md says so. Before, PREREG could not be written after a drop: V0's S_L8
    series needs `T_cal_s.L8` from R3 L8 CAL chains that would not exist. Changes no observable. With L8 and G8
    dropped, `params-v0-aifoundry1-c1.json` must carry `"types": ["S", "L16"]` (v0final otherwise waits for S_L8).
    `run_selftest.py` checks both ways (refused while G8 is kept, frozen when dropped, the lock, the skipped blocks).
37. **Tier S POWER waived for INT16@32 pairs** (27 Sep 2026, coordinator decision (b), before any validation data):
    sw_W is the median over t0 + 1 s .. t0 + t66 (DESIGN2 §5.5, not changed), and INT16@32 crosses 66 C in < 1 s from
    S_S 64 (R1c: 0.86-0.97 s), so its window is empty and POWER cannot be computed for PLACE-tS, PLACE-kappa-S or
    CONC's INT16@32-UNI32@16 pair (registered, it would be INSUFFICIENT by construction, card 1 heating faster). POWER
    is waived for those pairs (`reduce.py` `POWER_WAIVED`): P3 lists them (`power_waived_pairs`), PREREG.md states the
    waiver, and `--val` reports them as "waived: no window in Tier S; see Tier L", with the same pair's value in card
    1's L16 blocks (`tier_L_ci99`, reported). Equal power for the INT/PER/UNI placements rests on the Tier L check
    (R1c L16 sw_W: INT16@32 13.96, PER16@32 13.87, UNI32@16 13.83 W; every pair within +-0.5 W). WORK is not waived,
    and the other Tier S pairs (CONC's PER16@32-UNI32@16, MAP's B4NE-B4SW) keep POWER EQUIV. The reason held on
    aifoundry3 only (all six development blocks: 0.86-0.999 s). On card 1 INT16@32 crossed in 1.14-1.41 s (validation,
    28 Sep), so its window was not empty and `--val` computed PLACE-tS's Tier S value, -0.27 [-0.42, -0.13] W; the
    waiver stands as frozen and the value is reported, not an outcome (`val.json`'s note still gives the development
    reason, "< 1 s").
38. **The kappa gate stays 0.90** (27 Sep 2026, coordinator decision (a), before any validation data): the design's
    value, although development may set 0.85-0.97 (§5.5) and at 0.90 only 1 of R1c's 9 L16 runs and no Tier S
    INT16@32 run gets a kappa (floor match 0.80-0.89). If no development data pass it, PLACE-kappa and PLACE-kappa-S are
    reported, not tested (P3: fewer than 3 development blocks); PREREG.md states the gate.
39. **Validation sessions start with an S block** (28 Sep 2026, coordinator decision after validation session 1's
    safety stop at 00:13 PDT, in effect when session 1b started at 00:27:06; this entry was first dated 00:40, after
    that start; no locked file changed, PREREG a1bdc4e42c88 stands). The card-1 W_idle guard (§7's
    secondary card-0 proxy, `hp_widle_check`: W_idle at the edge, the median board_w over the last 2 s, may not rise
    more than 2 W above the session's baseline) takes its baseline from the session's FIRST MEASURED RUN, whatever its
    tier. The tiers start at different edges, and card 1's idle power grows with the die temperature: W_idle at the edge
    was 34.4 W at 60 C (S_L; V0 p5502 and p9201), 34.9 W at 61 C (V0 p5501) and 36.7 W at 64 C (S_S; p9101's CAL). So an
    S block after an L16 block in the same session trips the guard by construction: session 1 (23:45 27 Sep) ran p9201
    (L16, ok, baseline 34.41 W), then p9101 (S) aborted at its first measured run with W_idle 36.71 W, a rise of 2.30 W >
    2.0 W, wrote the STOP file and stopped the queue (00:13). Card 0 read 63 C at both guard starts, its board power
    17.8-18.2 W and falling: no card-0 heat. From here every validation session starts with an S block (the higher-idle
    tier sets the baseline), so an L16 block later in the session reads about 2.3 W below it and the guard keeps its
    purpose (a rise from card 0's heat, or a drift) without false trips. p9201 stays session 1's valid L16 block; the
    aborted p9101 (status fail, never used by `reduce.py`) is kept as `p9101.guard-stop-27sep`, and the STOP file (ours,
    from this guard) was removed. Session 1b (`schedule-hp-aifoundry1-c1-val1b.txt`: 9101, 9202, 9102, 9203) re-runs
    pass 9101 from the start; session 2 (`schedule-hp-aifoundry1-c1-val2.txt`: 9103, 9204, 9104, 9205, 9105) was
    already S-first and starts >= 4 h after session 1b ends. The re-run of 9101 began at 00:27:08, 13.8 min after the
    stopped copy ended (00:13:22; both `block.json`): under the 15 min between queue entries that DESIGN2 §6.1
    ("Practicalities") asks and every schedule otherwise keeps (`sleep 900`). The stopped copy had run only its burn-in
    CAL run. This spacing note was recorded on 28 Sep after the validation, from its review.
40. **Block void reads tau_c over the measured runs only** (recorded 28 Sep 2026 after the validation, from its
    review; the reading itself is the locked `reduce.py`'s, frozen at 22:50 on 27 Sep before any validation data, and
    `reduce.py --dev` with the same code reproduces the development record byte for byte). DESIGN2 §4.4 voids a block
    if "any run's tau_c" lies outside [0.5, 2.0] x the block median; `block_void` takes the tau_c of the block's kept
    measured runs (`kept_runs`), not its burn-in CAL runs. The first CAL run of a Tier L block is reached by preheat
    bursts, not after a chain that took the mean past 66 C, and its mean falls through the last degree in 1.0-2.2 s
    against 5.8-15.0 s for the measured runs (both cards). Read literally, the rule would void every Tier L block on
    both cards (9 on aifoundry3, 5 on card 1) and no Tier S block. `heat.json` `tauc_roles` has the ranges and counts.

## Known limits

- **a2's frozen copies** (`a2/hplib.sh`, `a2/hplib.py`, `a2/sptrace_events.py`) keep the 27 Sep code: the level is
  inferred from the whole ring (so a2's end-of-session "SP level restored to INFO (checked)" cannot tell a failed
  restore while INFO-era lines remain in the ring), the heater gets no `--kernel`, and V3_FORCE and the cool-down are
  checked only by `run_a2.sh`. A2 data exist, so PREREG-A2 cannot be re-frozen. After an a2 session that set WARNING,
  check the restore offline: `python3 tools/claims-v3/hp/sptrace_events.py level-since <the last run's sp-N.bin>
  sp-level-check.bin` in the attempt directory (INFO: restored; WARNING_OR_LOWER: the restore did not take, or the SP
  logged the check dump's request only after copying the ring; a restore then needs the owner's approval, e.g.
  `ettelem-hp loglevel info` under the card lock).
- **The level inference assumes** that at INFO or DEBUG the SP logs every host DM request (a dump included). If a card
  did not, an INFO card would read WARNING_OR_LOWER from the delta: nothing is then set (TRIG-B at the current level),
  and a restore check fails and stays pending (restored again by the next block), which is safe but noisy.

- **Tier L on an ALIVE card**: each 2 s launch writes about two CRITICAL lines; a 4 KB ring holds about 50, so a chain
  of more than about 25 launches loses the dump's ring overlap, and the coverage rule drops that dump. Tier S, A2 and
  B1 runs are short enough.
- The κ gate (90% floor match) failed often on the synthetic data (noise 0.12 C before truncation); development may
  set it within 85-97%, but it stays 0.90 (departure 38).
- L8 at 6.6 W: on a card whose idle asymptote is far below 66 C, 256 minions from 63 C may never reach 66 C within
  150 s (the synthetic card showed it); D-L8 raises S_L8, and drops L8 and G8 if even 64 censors (then departure 36).
