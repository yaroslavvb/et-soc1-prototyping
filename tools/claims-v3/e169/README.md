# E169 (Q141(s)): the stride shapes on aifoundry2 under its own governor, with the step rule

E169 runs Q140(q)'s six frozen stride shapes, P1-P3 at power-of-two panel strides and N1-N3 not, as fp32 zeros bursts in E158's harness.
Every shape is an argument of E136's binary. The question is whether the L3's public set map, with its 8 MB index (SM), sets the time a
large GEMM pays at a power-of-two panel stride. SM is tested against ISO (E158's retention curve) and STRICT (strict LRU at 32 MB),
which have no set index.

- **The registration** is Q140(q)'s ([`REGISTRATION.md`](../../../docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION.md) B6-B7,
  `49575094`) with **amendment A2** here, [`REGISTRATION-A2.md`](REGISTRATION-A2.md) (`217c94a2`). A2 adds the step rule, keeps B7 as
  registered, and gives the design.
- **The frozen predictions** are `predictions-e169.json` (`e39d06da`, corrections `1bfaa4e4`; predicted peaks at most 46.9 W). No frozen
  file changes.
- **It answers** Q140's final critic: `card_half[6]`, `desk_next` 4 and 7, and its new fault 3. That is Q139's critic's rank 6 and the
  kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 1.
- **The run's data** goes in `docs/reports/data/<the run's date>-e169-stride-shapes/`.

## The test, in one table

| pair (P over N) | SM's step | ISO's | STRICT's | in the verdict |
|---|---|---|---|---|
| P1/N1, `gemmL1x8x5` / `gemmL1x7x5` | +37.06% | 0.00% | 0.00% | yes |
| P3/N3, `gemmL1x4x8` / `gemmL1x5x8` | +30.97% | 0.00% | 0.00% | yes |
| P2/N2, `gemmL2x8x3` / `gemmL2x6x3` | +7.94% | +5.76% | −1.03% | reported (SM and ISO are 2.2 points apart) |

The step is T800(P) / T800(N) − 1, measured per pass and pooled in logs. Its 95% interval comes from the passes, never narrower than E158's
pass-to-pass repeatability allows (σ0 0.336%, so ±0.42 points over 5 passes). Each model's zone is its step ± 3.0 points.

The verdict on the 8 MB index, from P1/N1 and P3/N3 (A2 S4):

- **INDEX STEP AS SM**: both pairs show a step, and it is SM's size;
- **NO STEP**: neither pair shows one;
- **A STRIDE STEP SM DOES NOT SIZE**: both show a step, and at least one lies outside SM's zone;
- **A STRIDE STEP, ITS SIZE UNRESOLVED**, **MIXED**, **UNRESOLVED** or **NO VERDICT** otherwise.

For comparison, on E158's committed collapses the card stepped +14.9% to +33.3%, and on its plateau neighbours −0.55% to +1.29%
([`steps-e169.txt`](steps-e169.txt)). Also scored or reported:

- B7 as registered (SM's level within 3% on every shape; expected to fail);
- each model's level error;
- the ties to E158 (`K4n7`, `K4n8`, `K6n5`, `K6n4`: T800 within 2%, the committed steps within 2 points);
- R0's check of C;
- fp16 and int8, printed if run;
- a reported zeros-burst power reading on the six new shapes.

## What runs (A2 D1-D12)

| | |
|---|---|
| card | aifoundry2 card 0, its own governor (65 W / 65 °C read before and after); nothing set |
| harness, binary | E158's: E146's preflight (E136's three sha256), E119's `run_e119.py` unchanged; E136's `rgm136`, shapes as `gemmL<MB>x<NB>x<KB>` |
| a burst | one 6 s process (budget 7.5 s), tail 4 s, from a die at or below 55 °C (waiting at most 300 s); T800 from launches at or above 790 MHz |
| order | SMOKE (30 s rest, four 2 s checked launches), the two stop-path tests, then A (pass 1, with the ties), B (pass 2, with the ties), C, D and E (passes 3-5), F (fp16 and int8, printed if run) |
| bursts | **50**; the registered subset is A-C, 26 bursts |
| stops | board above **60 W** on 3 live samples, a die reading at or above **76 °C**, admission **82 W** (highest estimate 47.02 W), peak lock 60 W |
| card time | about **11-12 card-minutes**, plus up to 5 if the first cool gate waits; the session's cap is **20**, at most **25** in all; the claim reads "for 0.5 h" |

The order as the harness will plan it, `run_hpl.load_protocol` with `order_seed` 169 ([`selftest-kit.txt`](selftest-kit.txt) §3):

- **A:** N1 P1 N2 P2 N3 P3 K4n7 K4n8 K6n5 K6n4
- **B:** P3 P1 P2 K4n8 N1 K4n7 K6n4 N2 K6n5 N3
- **C:** P3 N2 N1 P1 N3 P2
- **D:** N2 P3 N3 N1 P2 P1
- **E:** N3 N2 P2 P3 N1 P1
- **F:** N1 P1 N2 P2 N3 P3 in fp16, then the same in int8

A to E are fp32.

The pools' device addresses are not logged. E136's binary prints none, and it keeps the runtime's verbose log levels disabled, so the
runtime's "Malloc at address" line cannot print (A2 D9). E169 runs with Q140(q)'s B2 offsets as an assumption.

## Checked at the desk (Wed 4 Nov 2026, on the Intel; no card, no device, no lab box)

- **The amendment's numbers.** [`steps-e169.txt`](steps-e169.txt): the frozen steps equal Q140(f)'s desk check to four decimals, and
  E158's repeatability and Q140(q) C3's six committed steps are reproduced.
- **The scorer's self-test, E158 → E169.** [`selftest.txt`](selftest.txt), ALL PASS:
  - `reduce_e169` reproduces E158's `results.json` exactly, and E158's own `score()` on that reduction reproduces its registered verdicts
    (R0 PASS; R1 INCONSISTENT; R2 NO SINGLE CURVE; R3 PASS ×3 at +0.41 / +0.26 / −0.76%; R4 NOT BETTER; R5 10 of 14);
  - the step machinery agrees with `steps_e169.py` on E158's four committed collapses;
  - 22 made-up truths read as built (42 checks in all). *Dated note, Wed 4 Nov 2026: commit `18aaca80`'s message says "23 made-up
    truths"; the file it committed holds 22, as here.*
- **The kit's self-test.** [`selftest-kit.txt`](selftest-kit.txt), ALL PASS: the runner's bounds, the protocol against A2, the planned
  order, and the queue's stop-path check on made-up records.
- **The dry pass.** [`logs/dry-queue.txt`](logs/dry-queue.txt) and [`logs/dry-score.txt`](logs/dry-score.txt): the whole queue on
  `run_hpl.py`'s toy card, then the scorer on its session. It opened no device and ran no ssh.
  - The queue exited 0. The smoke check passed.
  - Both stop-path tests fired on the toy card's live samples. The board stop fired 34 ms after the third line over 30 W, and the launch
    ended 228 ms later; the die stop fired 56 ms after the first line, before any launch.
  - All 50 runs ran (4.2 toy card-minutes), none refused.
  - The scorer read the session (exit 0), with every verdict labelled DRY. The toy card has one time per op and writes no check of C,
    so R0 reads FAIL there, as in E158's dry run.
- **The device-command audit.** [`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): GO, 19 send sites, every one READ, 0 disallowed, no
  allow-list, with E158's one reviewed exception (`run_hpl.py:622`). Without it, NO-GO on that one line.
- **The hash list.** [`frozen-sha256-e169.txt`](frozen-sha256-e169.txt) holds 54 files, and `shasum -a 256 -c` reads all OK. They are
  the frozen predictions and the code that froze them, the amendment, the scorer and its whole score path, the kit, the run chain's
  sources, and the audit with its table. [`trace-scorer-e169.txt`](trace-scorer-e169.txt) traces the score path on the dry session: the
  list covers all 20 files it loads.
- **The other lanes' frozen lists still pass:** `blind7/SHA256SUMS` 91 OK, `frozen-sha256-e168.json` 9 (`score_e168.py check`),
  `frozen-sha256-e168-scorer.txt` 18 OK, and predict_q140e's 26 input hashes.

## The box steps that wait for the owner's go and fresh lab access

E169 runs on aifoundry2 **last**, after E165, E167 and E168 (the critic's plan). Its bursts are cool zeros bursts.

1. **The day's one post.** Rewrite it to add `using aifoundry2 for 0.5 h, until ~HH:MM PST`, the other cards' clauses kept, and drop the
   clause at the release.
2. **The tree.** `git pull --ff-only` in aifoundry2's lab checkout, then, in `tools/claims-v3/e169`:
   - `shasum -a 256 -c frozen-sha256-e169.txt` (all OK);
   - `python3 -B score_e169.py check` (CHECK OK, 5 files);
   - `python3 -B selftest_kit_e169.py` (ALL PASS).
3. **Preflight.**
   - `et-who`, `who` and `uptime`: no device node or card lock held, and no other user active (an idle login does not block);
   - `et-lab-manifest` for the firmware (BL2 0.22.0, the build the command table classifies);
   - the three binaries under `build/e136/` and `build/ettelem-hpl/` with E136's sha256 (the runner refuses otherwise, before the lock).
4. **A dry pass on the box.** The queue with `--dry` and the dry protocols, as on the Intel. It opens no device.
5. **The slot file and the queue.** Write `~/claude/work/q141-a2-e169-slot.txt` with the line
   `SLOT E169: start <epoch s> (…) end <epoch s> (…) `, about 45 minutes. The queue gives up if the card is not free by 25 minutes
   before the slot's end, and its session ends 3 minutes before it. Then start the queue detached on the box:
   `setsid nohup python3 tools/claims-v3/e169/queue_e169.py --slots ~/claude/work/q141-a2-e169-slot.txt --runs build/e169/runs > build/e169/queue.out 2>&1 < /dev/null &`.
   The smoke and both stop-path tests run inside it, and either failing halts the queue with no session.
6. **The die stop at the start.** If the hottest-sensor field (the service processor's carried running maximum: 69-70 °C through E146,
   E158 and E159) reads 76 °C or more after E168, the smoke's die stop fires before any work launch and the queue halts. Nothing else
   happens. A retry then needs a dated amendment.
7. **Collect and score.** Copy `build/e169/runs` to `docs/reports/data/<date>-e169-stride-shapes/aifoundry2/`, then run
   `python3 -B tools/claims-v3/e169/score_e169.py <that dir>/s1 --out results.json > score.txt` and write the README, registered and
   post hoc kept apart.

## Device commands sent

*Q136's rule ("take more care for writing commands"), kept through Q141: only read-only PMIC voltage reads and the statistics reset may be
sent, and no governor move. Every command the run sends is classified from et-platform `836a4ab`'s source, the revision matched to
aifoundry2's BL2 0.22.0. The chain is E158's: the same three binaries, E146's preflight, E119's runner, and E158's queue with E169's names.
Checked by Q136(w)'s `dmcmd_audit.py` over `tools/claims-v3/e169/` and the chain: **19 send sites, every one READ, GO**, with E158's one
reviewed exception ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)). Without that exception it reads NO-GO on exactly that line.
**E169 sends no WRITE.***

| program (when) | command | firmware handler at `836a4ab` | class |
|---|---|---|---|
| `ettelem sample --every-ms 100` (`run_hpl.py:545`, gate to tail of every run, the stop tests included; no `--reset-ms`) | `DM_CMD_GET_MODULE_POWER`, `DM_CMD_GET_SP_STATS` | RAM copies (`thermal_pwr_mgmt.c:984-988`, `:2780`) | READ |
| | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | PVT sample registers read; refreshes the governor's RAM copy (`:732-773`) | READ |
| | `DM_CMD_GET_ASIC_VOLTAGE`, `DM_CMD_GET_MODULE_VOLTAGE` | PVT samples and PMIC voltage-register reads (`pmic_controller.c:1473-1500`) | READ (the owner's allowed read-only PMIC voltage reads, 2 Nov 2026) |
| | `DM_CMD_GET_ASIC_FREQUENCIES` | PLL registers read (`perf_mgmt.c:276`, `io_pll.c:932`) | READ |
| `ettelem config` (`queue_e169.py:173`, the queue's two snapshots; `run_hpl.py:626`, after every run and at each session's ends) | `…GET_MODULE_STATIC_TDP_LEVEL`, `…TEMPERATURE_THRESHOLDS`, `…POWER_STATE`, `…GET_ASIC_VOLTAGE`, `…GET_ASIC_FREQUENCIES` | RAM copies (`thermal_pwr_mgmt.c:613-616`, `665-668`, `551-555`); the voltage and PLL reads as above | READ |
| `ettelem sptrace` (`run_hpl.py:618`, after every run) | `TRACE_EXTRACT`: the driver copies the trace region by MMIO read | — | READ |
| `ettelem residency 1 2 3` (`run_hpl.py:622` as `run_e119.py` rewrites it) | none: this build accepts raw states 2-6 only and returns 2 before it opens the device | — | NOT SENT (the reviewed exception) |
| `dev_mngt_service -m DM_CMD_GET_MODULE_POWER` (`run_hpl.py:597`, the drain, only if a sampler fails twice) | `DM_CMD_GET_MODULE_POWER` | as above | READ |
| `sparsity_host` (rgm136) | no management command: it opens the ops node only (kernel load, DMA of the tiles and C, launches) | — | not device management |
| `et-lab-manifest`, `et-who`, `sensors -j`, `uptime`, `who`, `ps`, `flock` | none: sysfs, `/proc`, `fuser`, the host's hwmon | — | — |

## What E169 does to predicting power and heat

- **Time per op sets a GEMM's energy per op** (E = P·T) and, on the governed card, its clock and power. On a new shape that time stands
  at ISO's 6-11% rms, with single misses of 8-13% at power-of-two panel strides (E158 R4, Q140(q) C6). SM, as a level, fails at 13-14%.
- **What E169 makes scorable, blind:** whether a block-stride step belongs in the next time model. The step rule reads the step at two
  power-of-two strides against SM's frozen +37.06% and +30.97% and ISO's and STRICT's 0.0%:
  - INDEX STEP AS SM: SM's step on ISO's level becomes the candidate term, to be registered and tested on further shapes;
  - NO STEP: the stride term is dropped, and ISO's level stands with the committed collapses unexplained;
  - A STRIDE STEP SM DOES NOT SIZE: a stride term stays, with its size unknown (fitting it afterwards would not be blind).
- **The ties** re-measure two committed steps in the same session. **The reported power reading** puts E136's P0 and Q140(l)'s zeros level
  on six shapes that have never run.
- **Heat:** nothing directly. These are zeros bursts at about 36-38 W board.
- **No frozen prediction changes.** `predictions-e169.json`, G4, M9 and pool 7 are untouched. A2 adds a rule over the frozen numbers.

## What it cannot say

- **One card, one governor build, one session.** The interval is within the session; E158 against E146 gives the between-session repeat
  (−0.31% to +0.29%).
- **The L3 or the DRAM.** A power-of-two step does not separate the L3's set index from a DRAM-side channel or bank mapping at the same
  strides. No public source gives the address-to-memshire interleave, and the pools' addresses are not logged.
- **One shape family.** Only MB 1 and 2 shapes run. E158's `F6` (`K6n4`'s layout with three row blocks) kept 0.33 of its far lines, so
  the stride effect depends on more than NB.

## Files

| file | what |
|---|---|
| [`REGISTRATION-A2.md`](REGISTRATION-A2.md), [`step-rule-e169.json`](step-rule-e169.json), [`steps_e169.py`](steps_e169.py) → [`steps-e169.txt`](steps-e169.txt) | amendment A2 (`217c94a2`): the step rule, B7 as registered, the design, and every number behind them |
| [`score_e169.py`](score_e169.py), [`reduce_e169.py`](reduce_e169.py), [`selftest_e169.py`](selftest_e169.py) → [`selftest.txt`](selftest.txt) | the scorer, E158's reduction ported, and its self-test (`18aaca80`) |
| [`make_kit_e169.py`](make_kit_e169.py) → [`kit-e169.json`](kit-e169.json), [`kit-e169.txt`](kit-e169.txt) | the admission estimates, the smoke's cycles, the relation and the clock rule, from frozen inputs (`18aaca80`) |
| [`make_protocol_e169.py`](make_protocol_e169.py) → `protocol.json`, `protocol-dry.json`, `protocol-stoptest-{board,die}[-dry].json`, [`protocol.txt`](protocol.txt) | the protocols |
| [`run_e169.py`](run_e169.py), [`queue_e169.py`](queue_e169.py) | E158's runner and queue with E169's names (the die bound added, the cap default 20) |
| [`selftest_kit_e169.py`](selftest_kit_e169.py) → [`selftest-kit.txt`](selftest-kit.txt) | the kit's self-test |
| [`frozen-sha256-e169.txt`](frozen-sha256-e169.txt), [`trace_scorer_e169.py`](trace_scorer_e169.py) → [`trace-scorer-e169.txt`](trace-scorer-e169.txt) | the hash list and the score path's trace |
| [`logs/`](logs/) | the device-command audit, the dry pass's queue and score |
