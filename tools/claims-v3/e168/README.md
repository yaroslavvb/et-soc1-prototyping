# E168: G4's blind test, a governed large GEMM's sustained clock, board and die on aifoundry2 (Q141(o), the run kit)

*Wed 4 Nov 2026 (week 45), written on the Intel about 09:20-09:50 PST by Q141(o), desk only: no card claimed, no device command sent,
no ssh to a lab box. This README is E168's registration of the run, as `E159.md` was E159's. It is committed before any E168 data exists
and before the claim. The card session waits for the owner's go and fresh approvals; it does not run in Q141.*

*It answers:*
- *Q140's final critic, `card_half[5]` (E168: ready with gaps; missing: the run kit ported from E159's, a card-lane README,
  `dmcmd_audit` GO, a dated amendment adding a cold int8 zeros hold, the box checks) and `desk_next` 5 and 7;*
- *Q139's final critic, rank 5 (the large GEMM's sustained path, G3 to G4);*
- *the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 1 ("Where a
  large GEMM falls") and item 6 (the power model).*

*The owner's mandate is his words of 2 November 2026, "settle any unanswered questions regarding horace's power model", with his goal
"to be able to predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible".*

## It descends from these frozen commits

| what | where | commit |
|---|---|---|
| Q140(q)'s registration: G4's terms, rules A7 and the 82 W rule A8, E168's design A6 | [`REGISTRATION.md`](../../../docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION.md), `registration.json` | **`49575094`** (02:26:25 PST) |
| G4 frozen, E168's predictions and scorer: `g4.json` `fe5bb0a6…`, `predictions-e168.json` `430f4afa…`, `score_e168.py`, `frozen-sha256-e168.json` (9 files) | the same directory | **`e39d06da`** (02:49:40 PST) |
| amendment A1 (C1-C13; item 5: a cold int8 hold needs its own dated amendment) and the scorer's 18-file sidecar `frozen-sha256-e168-scorer.txt` | [`REGISTRATION-A1.md`](../../../docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION-A1.md) | **`1bfaa4e4`** (04:03:20 PST) |
| **amendment A2**: the cold int8 zeros hold at S2, the gates' bounds A6 left open, how the added hold is scored | [`REGISTRATION-A2-cold-int8-zeros.md`](REGISTRATION-A2-cold-int8-zeros.md), [`predictions-e168-a2.json`](predictions-e168-a2.json) `2afb290f…` | **`226249e1`** (09:18:35 PST, pushed 09:18:38) |
| the parent run, E159: its kit, registration, dated note and corrections | [`../e159/`](../e159/README.md) (`E159.md`, `queue_e159.py.dated-note.md`); data [`2026-11-03-e159-gemm-sustained/`](../../../docs/reports/data/2026-11-03-e159-gemm-sustained/README.md) | `d8badb73`, `55a43b69` |

- **Nothing of E168 is predicted here.** Every predicted number is Q140(q)'s, and the tenth hold's is copied from it (A2).
- **No frozen file changes.** The hash lists pass:
  - `score_e168.py check`: CHECK OK (9 files);
  - `shasum -a 256 -c frozen-sha256-e168-scorer.txt`: 18 OK;
  - see [`logs/score-e168-frozen-selftest.txt`](logs/score-e168-frozen-selftest.txt).
- **A dated note on A2's header.** A2 says *"about 09:25 PST"*. It was committed at 09:18:35 PST and pushed at 09:18:38, before this
  kit and before any claim.

## What runs

**aifoundry2 card 0 under its own governor.**
- 65 W / 65 °C, read by `ettelem config` at the queue's start and end and after every run.
- **Nothing is set on the card:** no TDP, threshold, clock or voltage; no `--reset-ms` and no statistics reset; no firmware-revisions
  query; no residency read; no governor move.

**E136's binary, unchanged.** It is rgm136's `SP_GEMM_LARGE`, built on aifoundry2 at 15:37 PST on 2 Nov 2026; E146, E158 and E159
ran the same three programs. Every shape is an argument, `gemmL<MB>x<NB>x<KB>`. E146's preflight refuses the session unless the three
device programs have E136's registered sha256: `76475508…`, `aace138c…`, `77a46171…`.

**The protocol** is [`protocol.json`](protocol.json), written by [`make_protocol_e168.py`](make_protocol_e168.py) from the frozen file
and A2, and printed in [`protocol.txt`](protocol.txt).

| block | runs | gate | admission estimate |
|---|---|---|---|
| SMOKE | 30 s of the idle card; then 2 s each of S1, S2, S3 fp32 zeros and S2 int8 zeros, each with rgm136's check of C, the cycles per op 50-250% of E146's law (T0 at 800 MHz × 800: 1,247.3, 1,188.5, 1,681.3, 1,289.3) | — | 45.6-46.9 W |
| stoptest-board | one 6 s burst of S2 fp32 zeros (P0(800) about 38 W over a 22 W rest) with `board_cap_w` 30 W on 3 samples | — | 46.6 W |
| stoptest-die | `abs_stop_c` 30 °C, the die about 45-47 °C at rest: the trip before any launch | — | — |
| **R** | the session's rest reading: 30 s idle, no launch (the chain's start, the first hold's 20 s anchor) | — | 30 W |
| **H**, the registered subset | S1, S2, S3 fp32 random, each **cold** then **warm55** (`gemmL1x3x3`, `gemmL3x3x2`, `gemmL3x5x3`; `randn`) | cold: die mean ≤ 46 °C, at most 360 s; warm55: ≤ 55 °C, at most 300 s (A2 §2) | 75.68, 76.63, 68.23 W |
| **I** | S2 int8 zeros, W8A8 real (`int8.real_smol_w8a8_down`, pool 6's tile cycled by the generator `tiles`), sparse50, all **warm55** | warm55 | 45.64, 52.48, 52.57 W |
| **A**, amendment A2 | S2 int8 zeros from **cold**, the tenth and last | cold | 45.64 W |

- **Every hold** is 12 processes of `--seconds 8` (budget 9.5, tail 6 s), about 106 s. The window is the in-kernel samples of the last
  40 s.
- **The stops**, under the keys run_hpl.py's watcher reads: one die reading (the minion shires' mean or the hottest-sensor field) at or
  above **76 °C**, or the board above **85 W on three live samples in a row**, ends the session (exit 4).
  - Each stop is tested on live samples by the stop-path tests before the session. The queue halts unless both fire as registered.
  - The hottest-sensor field reads the service processor's running maximum, about 69-70 °C in every earlier session on this card, so
    76 °C keeps about 6 °C over it.
- **The 82 W rule** (A8 and the brief): every hold's frozen predicted peak, P0(800) + 8.51 W, is at most 82 W. The highest is S2 fp32
  random's 76.63 W, so every hold runs as designed.
- **The run-time admission** is E105's rule, unchanged: a hold runs only if its estimate (its frozen peak) is at most
  `limit_p800_w` 82 W. After any run whose board reading reached `peak_lock_w` 82 W, no hold with an estimate at or above that run's
  goes on.

**What E168 adds to Q140(q)'s design.** None of it changes a hold's values, shape, order or rule.
- **E159's additions, ported:** the smoke, the stop-path tests, the rest reading R, the admission estimates, and the reduction's
  cut-hold filter and per-session scoring.
- **A2's tenth hold and the gates' bounds.**
- **One addition to the runner, which the frozen design needs in order to run at all** (below).
- **Two check-of-C clauses:**
  - the smoke halts unless every launch carries rgm136's check of C, ok and exact or approx;
  - a hold is cut if a process lacks that record.

  Every E159 work launch, 108 of 108, carried one.

### The runner's one addition: pool 6's W8A8 tile

Q140(q)'s frozen hold 8, `S2-int8-real_smol_w8a8_down-warm55`, names the tile file
`tools/claims-v3/kinds/blind6/tiles/int8/int8.real_smol_w8a8_down.bin`.

**Without the addition, the session would not run.** E159's chain checks every file a GEMM value names against E101's registry
(`run_e101s.verify_tiles`: E101's items and its real set). Pool 6's tiles are not in it, so the session is refused at load, `--dry`
included: *"… is not a registered tile"* ([`selftest.txt`](selftest.txt) §3). That would end the whole session with no hold run.

**What [`run_e168.py`](run_e168.py) does.** It checks such a value as E160's runner checks pool 6's `file:` values:
- pool 6's `blind6.json` and `MANIFEST` must hash as committed in Q139(x)'s `d98d2e34` (E160's pins, `e160_common.FROZEN`);
- the file must be a tile of the manifest of the run's own type;
- it must be 2,048 B, with the manifest's sha256 of the whole (`24fe46ef…`), of A and of B.

Any mismatch refuses the session before the card lock. Every other value goes through E101's check unchanged. The self-test shows the
tile accepted, and a flipped bit, a wrong type and a changed MANIFEST refused.

## The rules, which can fail (Q140(q)'s A7, applied by its frozen scorer unchanged)

- **The primary.** Per hold, G4 runs mechanically from the session's own measured state (the chain open loop on the measured board up
  to the hold, anchored on the measured die over the 20 s before it) on the hold's own kernel windows; T_Z takes the fallback δ.
- **The verdicts.** Measured − G4 must be within **15 MHz** (the window clock), **2 W** (the board) and **1 °C** (the window die).
  Each quantity **PASSES** on at least **8 of the 9** holds; with fewer than 9 scored, it passes only if all are inside.
- **The increment rule.** For W8A8 real and sparse50 at S2: the window board minus int8 zeros' at S2, measured against G4's (7.58 and
  7.68 W), must be within **±1.328 W** (15% of the 8.86 W span).
- **Beside G4:** G3 as frozen, E136's law (its die law from the hold's measured start), and the chain on the measured trace (heat given
  the watts, die only). Every arm's rms and mean are given, and whether G4's rms is below G3's and below E136's law's.
- **Which holds are scored.** A hold cut by a stop or not run is not scored. The verdicts are given over every scored hold (the
  primary) and over the registered subset, the six fp32 random holds.
- **The day's zeros offset.** With `--anchors` (E165's zeros-anchor reads, if E165 ran first that day), the scorer's
  `G4_own_anchors` arm is reported, labelled as E165's session. The fallback stays the primary.
- **A2's tenth hold is reported, not counted** (A2 §3). It is scored by the same code from its measured start, with
  `predictions-e168-a2.json`. The test of G4's start dependence: ΔW = cold − warm int8 zeros window board, against G4's mechanical
  difference (nominal +1.334 W), G3's (+0.641 W) and E136's law (0). Its reading: SUPPORTED, NO START DEPENDENCE or OPPOSITE SIGN at
  half of G4's difference. E159's three zeros holds spread 0.057 W where G4 spreads them 0.442 W.
- **R0, the checks of C.** Every kernel record in every launch must be ok (E159's count). The work launches without a check record
  are listed. A failure labels every verdict.

**The reduction** is [`reduce_e168.py`](reduce_e168.py), run on the Intel.
1. **The freeze.** `score_e168.check`, the 18-file sidecar and A2's sha256; else exit 2.
2. **The cut rule** (E159's, plus the check-of-C clause).
3. **Each session scored on its own** by the frozen `score_e168.score`, on a temporary copy with the cut holds and A2's hold left out,
   the launch records gzipped as the scorer reads them. The rows are pooled, and the verdicts recomputed with the scorer's own
   arithmetic. With one session, they must equal the scorer's own verdicts.
4. **A2's reported test.** The warm row must be identical in both calls.
5. **R0.**
6. **The safety record:** peaks, trips, holds not admitted, peak locks, the stop tests, the TDP and threshold reads, every hold's gate
   (reached, waited, its reading) and card time.

## Self-test, dry pass, audit

- **[`selftest.txt`](selftest.txt): 59 checks, ALL PASS** (`/usr/bin/python3 -B selftest_e168.py`).
  - The protocol against the frozen design and A2.
  - The runner's stop limits, and its pool-6 tile check.
  - The queue's stop-path check and smoke check on made-up records.
  - The reduction on E159's committed session, five holds relabelled as E168's cells:
    - the A7 rows equal the frozen scorer's own;
    - A2's warm row is the same in both calls;
    - a missing process cuts a hold, and so does a missing check of C;
    - a `--dry` session is exempt from that clause, and says so;
    - A2's reading on made-up rows.

    These rows are E159's holds under E168's labels and levels: a check of the code, not a score.
  - **The frozen scorer's own self-test, re-run unchanged**, prints exactly the committed `selftest-score-e168.txt`: worst |diff| 0.0004,
    PASS ([`logs/score-e168-frozen-selftest.txt`](logs/score-e168-frozen-selftest.txt)).
  - **The parent's registered verdicts.** E159's own reduction, unchanged, on E159's committed data reproduces its committed
    `results.json`, verdicts and rows. G3: clock FAIL (8 of 9), board FAIL (5 of 9), die FAIL (6 of 9).
- **The dry pass, on the Intel, about 09:28-09:31 PST.** [`logs/dry-queue.txt`](logs/dry-queue.txt) and
  [`dry-reduce.txt`](dry-reduce.txt).
  - What ran: the whole queue through `run_e168.py` on the toy card, with no device and no ssh. Then the smoke, both stop tests (each
    fired on live toy samples: the board trip 4 ms after the third line over 30 W; the die trip 51 ms after the first line), and the
    session's eleven runs.
  - What it showed: the reduction scored all ten holds, the consistency checks were true, and R0 passed.
  - The dry protocol cuts every gate's wait to 6 s, because the toy card rests near 51 °C.
  - These are a toy card's numbers: a check of the code, not a measurement.
- **[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): GO.** 19 send sites, every one READ, 0 disallowed, no `--allow`. The checked files
  are E159's chain with E168's runner and queue, the two modules E168's runner adds, and every file of this directory. The one reviewed
  exception is E136's, E146's, E158's and E159's (below).

## Device commands sent

*The brief's rule, kept since Q136: only read-only PMIC voltage reads and the statistics reset may be sent, and no governor move. Every
command the run sends is classified before the first launch.*

The chain is E159's: the same three binaries and E146's harness. E168's runner imports E146's preflight and runs E119's run_e119.py
unchanged; its queue is E159's with its names changed. They send nothing of their own beyond the queue's `ettelem config` snapshots.

The commands were classified from et-platform `836a4ab`'s source, the revision Q133's gov-prep matched to aifoundry2's BL2 0.22.0,
and checked with Q136(w)'s checker: 19 send sites, every one READ, GO. These are the same 19 sites as E159's.
- **READ** = no write anywhere but the service processor's own RAM copy of what it just read, and the host-SP queue's transport.
- **WRITE** = any register, flash, configuration, counter or PMIC write.

**E168 sends no WRITE.**

| program (when) | command | firmware handler at `836a4ab` | class |
|---|---|---|---|
| `ettelem sample --seconds N --every-ms 100` (gate to tail of every run, the stop tests included; no `--reset-ms`) | `DM_CMD_GET_MODULE_POWER`, `DM_CMD_GET_SP_STATS` | RAM copies (`thermal_pwr_mgmt.c:984-988`, `:2780`) | READ |
| | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | PVT sample registers read; refreshes the governor's RAM copy of what it read (`:732-773`) | READ |
| | `DM_CMD_GET_ASIC_VOLTAGE`, `DM_CMD_GET_MODULE_VOLTAGE` | PVT samples and PMIC voltage-register reads (`pmic_controller.c:1473-1500`, `get_pmic_reg`) | READ (the owner's allowed read-only PMIC voltage reads, 2 Nov 2026) |
| | `DM_CMD_GET_ASIC_FREQUENCIES` | PLL registers read (`perf_mgmt.c:276`, `io_pll.c:932`) | READ |
| `ettelem config` (the queue's two snapshots, each session's start and end, after every run) | `…GET_MODULE_STATIC_TDP_LEVEL`, `…TEMPERATURE_THRESHOLDS`, `…POWER_STATE`, `…GET_ASIC_VOLTAGE`, `…GET_ASIC_FREQUENCIES` | RAM copies (`thermal_pwr_mgmt.c:613-616`, `665-668`, `551-555`); the voltage and PLL reads as above | READ |
| `ettelem sptrace` (after every run) | none to the SP: the driver copies the trace region by MMIO read | — | READ |
| `ettelem residency 1 2 3` (run_e119's rewrite of run_hpl.py:622, after every run) | none: this build accepts raw states 2-6 only and returns 2 before it opens the device (`ettelem-dv2/ettelem.cpp:280-294`) | — | NOT SENT (the checker's reviewed exception; E159's 21 attempts all rc 2) |
| `dev_mngt_service -m DM_CMD_GET_MODULE_POWER` (run_hpl's drain, only if a sampler fails twice) | `DM_CMD_GET_MODULE_POWER` | as above | READ |
| `sparsity_host` (rgm136) | no management command: it opens the ops node only (`host/main.cpp`); the workload's path to the Master Minion (kernel load, DMA of the tiles and C, launches) | — | not device management |
| `et-lab-manifest`, `et-who`, `sensors -j`, `uptime`, `who`, `ps`, `flock` | none: sysfs, `/proc`, `fuser`, the host's hwmon | — | — |

## Card-minutes, the cap, the order on the box

| | planned | every cold gate at its 360 s (a rest floor above 46 °C) |
|---|---|---|
| the session: R, the nine holds, A2's hold, the gates (run_hpl's `plan_s`, 25 s a run, plus the planned waits: about 4 min per cold start after a hold, 0.5 min for the first, 10 s per warm gate) | 38.0 min | 49.5 min |
| the nine alone (R and nine holds) | 31.6 | 41.1 |
| with the smoke (3.0 min) and the stop tests (about 0.8) | **about 42 card-minutes** | **about 53** |
| the nine with the smoke and stop tests, without A2 | about 35 | about 45 (Q140(q)'s design: about 45, cap 55) |

- **A2's hold adds about 7-8 card-minutes.** The critic estimated about 8.
- **Planned rests.** The rests are planned from Q138(t)'s frozen chain ([`logs/rest-chain.txt`](logs/rest-chain.txt)): within 1 °C of
  the rest about 207 s after a warm fp32 hold, and about 178 s after the sparse50 hold. They agree with E161's measured rest on this
  card.
- **The cap.** The session's own cap is **58 card-minutes**, the smoke and the stop tests apart (`run_e119.py` starts a run only if its
  planned time fits). The slot is **66 minutes**, and the queue ends the session 3 min before the slot's end, so there are **at most 63
  card-minutes in all**: Q140(q)'s cap of 55 plus A2's 8. The tenth hold is last, so the cap can only cut it, never one of the nine.
- **The claim.** In the day's one post (section 15's protocol), rewritten at the claim and the release:
  `using aifoundry2 for 1.5 h, until ~HH:MM PST`.
- **The order on aifoundry2.** E165 first (about 36-38 card-minutes; its zeros anchors give E168's reported arm the day's offset), then
  E167 (35.1), then **E168**, then E169. E168's first cold gate waits out E167's last hold, bounded at 360 s. That is about 75-80 min
  after aifoundry2's first claim, plus handoffs.

## The box steps that wait for the approvals (after his go)

1. **The approvals and the day's post.** Rewrite the day's one post to hold E168's clause, under the discord lock with `EXPECT_TEXT`
   (section 15).
2. **The tree.** On aifoundry2, run `git pull --ff-only` in `~/claude/et-soc1-prototyping`; HEAD must contain this kit's commit.
   - The runner needs `tools/claims-v3/e168/`, `e160/e160_common.py`, `kinds/blind6/` (`blind6.json`, `MANIFEST`,
     `tiles/int8/int8.real_smol_w8a8_down.bin`), `kinds/tiles/{fp32,int8}/` and E159's chain (`e146`, `e119`, `kspeed`, `hpl`,
     `e111`).
   - `git status --porcelain -- tools/claims-v3` must be empty.
3. **The binaries' sha256 (the preflight).** `sha256sum build/e136/host/sparsity_host build/e136/kernel/sparsity.elf
   build/ettelem-hpl/ettelem` must give E136's `76475508…`, `aace138c…` and `77a46171…`. The runner refuses otherwise.
4. **The protocol and the tiles, with no device.** `python3 tools/claims-v3/e168/run_e168.py --protocol
   tools/claims-v3/e168/protocol.json --out build/e168/list --list` loads the protocol and runs the tile checks, the W8A8 tile against
   `blind6.json`, then exits without opening the card.
5. **The firmware and who is there.**
   - `et-lab-manifest` and the firmware build: BL2 0.22.0, the build the classification is from (`836a4ab`). A different build is
     NO-GO until it is reclassified.
   - `et-who`: no holder.
   - `who` and `uptime`: an idle login does not block (the owner's ruling of 1 November 2026), an active one does.
6. **A dry pass on the box,** about 3 min with no device. Its runs and slot go under `build/e168/dry/`, never `build/e168/runs/`.
   First write a dry slot line to `build/e168/dry/slot.txt`, in step 7's form, starting a few seconds ahead and ending 66 min later.
   Then:
   ```bash
   python3 tools/claims-v3/e168/queue_e168.py --dry --slots build/e168/dry/slot.txt --runs build/e168/dry/runs \
     --protocol tools/claims-v3/e168/protocol-dry.json \
     --stoptest-board tools/claims-v3/e168/protocol-stoptest-board-dry.json \
     --stoptest-die tools/claims-v3/e168/protocol-stoptest-die-dry.json
   ```
7. **The slot and the launch.** Write `SLOT E168: start <epoch s> (<HH:MM PST>) end <epoch s + 3960> (<HH:MM PST>) ` (a trailing
   space) to `~/claude/work/q141-a2-e168-slot.txt`. Then start the queue detached, inside a script file run by `ssh aifoundry2 'bash -s'
   < file`:
   ```bash
   setsid nohup python3 tools/claims-v3/e168/queue_e168.py --slots ~/claude/work/q141-a2-e168-slot.txt --runs build/e168/runs > build/e168/queue.out 2>&1 < /dev/null &
   ```
   The queue runs the smoke (the check of C on all four launches is the box's GEMM host-reference check for R0), then both stop-path
   tests, then the session.
   - It halts with no session if either stop test fails.
   - Wait on it with bounded remote calls (`timeout 540` inside a script), never a long local sleep.
8. **Collect and reduce.**
   - Copy `build/e168/runs/` to `docs/reports/data/<date>-e168-gemm-g4/aifoundry2/`, with `launches.jsonl` and `tel/*.jsonl` gzipped as
     E159's committed sessions.
   - Scrub any login name from an end reason (E64's other-user stop holds one).
   - On the Intel run
     `/usr/bin/python3 -B tools/claims-v3/e168/reduce_e168.py <that>/aifoundry2 --out <that>/results.json [--anchors <E165's reads>] > <that>/reduce.txt`.
   - The anchors' layout is `predict_m9_a2.session_delta`'s: `{type: [{burst_mhz, burst_w, die_start}]}`.
9. **The release.** Rewrite the day's post at the release (section 15).

## What this does to predicting power and heat

- **The term tested** is a governed large GEMM's sustained path on aifoundry2, G4:
  - G3's chain and trip rule;
  - Q140(l)'s zeros level, T_Z;
  - the governor's dip at each process, T_G;
  - M8's span fraction for int8 real and sparse50, T_S.
- **E168 makes G4 blind for the first time.**
  - **Before:** held out over five sessions, G4 read the board to about 1.33-1.47 W, the window die to 0.58-0.63 °C and the clock to
    10.3-11.1 MHz. G3, blind on E159, read 8.7 MHz, 1.94 W and 0.99 °C, every per-hold rule failing.
  - **After:** E168's nine holds give the blind out-of-sample error per quantity, rms and mean, for G4, G3 as frozen and E136's law, and
    the chain given the watts.
- **A2's hold** tests G4's start-referenced leakage law against a law in the absolute die and against none, on one shape and format.
- **No frozen prediction changes.**

## Files

| file | what |
|---|---|
| [`REGISTRATION-A2-cold-int8-zeros.md`](REGISTRATION-A2-cold-int8-zeros.md), [`make_amendment_a2.py`](make_amendment_a2.py) → [`predictions-e168-a2.json`](predictions-e168-a2.json), [`amendment-a2.txt`](amendment-a2.txt) | amendment A2 (`226249e1`): the tenth hold, the gates' bounds, the reported test; numbers copied, none computed |
| [`rest_chain_e168.py`](rest_chain_e168.py) → [`logs/rest-chain.txt`](logs/rest-chain.txt) | the rests from Q138(t)'s frozen chain, a planning aid (self-check against the frozen nominal predictions PASS) |
| [`make_protocol_e168.py`](make_protocol_e168.py) → `protocol.json`, `protocol-dry.json`, `protocol-stoptest-{board,die}[-dry].json`, [`protocol.txt`](protocol.txt) | the protocols, from the frozen design and A2 |
| [`run_e168.py`](run_e168.py) | the runner: E159's, plus the pool-6 tile check |
| [`queue_e168.py`](queue_e168.py) | the queue: E159's with its names changed, the docstring's stop-test burst corrected, the smoke's check of C |
| [`reduce_e168.py`](reduce_e168.py) | the registered reduction (the frozen scorer, A7, A2 reported, R0, safety) |
| [`selftest_e168.py`](selftest_e168.py) → [`selftest.txt`](selftest.txt) | 59 checks, ALL PASS |
| [`logs/dry-queue.txt`](logs/dry-queue.txt), [`dry-reduce.txt`](dry-reduce.txt) | the toy-card dry pass of the whole queue and its reduction |
| [`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt) | Q136(w)'s checker on the run chain: GO, 19 READ sites |
| [`logs/score-e168-frozen-selftest.txt`](logs/score-e168-frozen-selftest.txt) | the frozen scorer's check (9 OK), the sidecar (18 OK) and its self-test re-run (byte-identical) |
