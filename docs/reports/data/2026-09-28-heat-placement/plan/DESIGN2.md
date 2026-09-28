# Heat placement and the thermal governor: experiment design, revision 2

Written 2026-09-27. It revises `DESIGN.md` by applying `CRITIQUE.md` and the owner's decisions of 27 September (O1–O3 and
the card roles, quoted in §0). No card was touched in writing it. The only computations were on committed data and
source, and every one is marked **[computed here]** with its script. Every prediction, band and rule below is fixed
**now, before any data**. The development rounds may change only what §5.5 lists.

## Citation key

| Tag | Meaning |
|---|---|
| `W/` | `/home/yaroslavvb/claude/et-soc1-heat`, branch `heat-placement` at `0cfc742` (the merge after `pages-v3b` `305fe0d`; every path `DESIGN.md` cites as `R/` is the same file here) |
| `V3/` | `W/docs/reports/data/2026-09-25-claims-v3/` |
| `TPM:N` | `heatplace/tpm-may2024.c`, line N: byte-identical to the 1.3.1 cards' closest source, `cafe03fc3^:…/services/thermal_pwr_mgmt.c` (`DESIGN.md` citation key) |
| `FW18` | `git show da192816a:…` (BL2 0.18.0, closest to aifoundry1 card 1), copies in `heatplace/src/da192816a/` |
| `D:N`, `C §x` | `DESIGN.md` line N; `CRITIQUE.md` section x |
| `firmware.md`, `observability.md`, `feasibility.md` | the research notes in this directory |
| `dfo:N` | line N of `derive_feasibility.out` |
| `ic:N` | line N of `idle_curves.out`, written by `idle_curves.py` here from the V3-IDLE raw telemetry [computed here] |
| `design2_sets.py` / `.json` | written here: it reads `MARTY` and `EMPTY` from `W/workloads/nocbench/analyze.py:50-60`, derives every mask below, and asserts every identity [computed here] |
| **[inference]** | reasoning, not a measurement or source text |

---

## 0. The design on one page

**Owner decisions applied (27 Sep 2026).**
- **O1 yes.** A run may chain back-to-back launches for up to about 150 s. Each process is ≤ 10 s under `timeout 10`.
  The card lock stays held, and the other-user check runs between launches. The device is released between launches.
  This makes Tier L the primary run length.
- **O2 yes.** A block may set the service processor's (SP's) log level to WARNING, the boot default. This design sets
  it **only on cards where the R0 probe shows that the trace test can work** (§3.2).
- **O3.** aifoundry2's part runs **today**, from whatever temperature it rests at. If the rest is too warm, the result
  is "not observable", stated as such (§3.5).
- **Cards.** Development runs on **aifoundry3** only; §0.1 says why it stays the choice. Validation runs on
  **aifoundry1 card 1** (the placement items) and **aifoundry2** (the clock items, today). No iteration happens after
  validation starts.
- **Card 0.** aifoundry1 card 0 is never used. While card 1 runs, card 0 stays idle, and a guard stops card 1's work
  if card 0 reads above 90 °C (§7).
- **Temperature.** No run may take the die above 90 °C. The script's own caps sit well below that (§7).

**Q1: does DVFS respond to the average or to one sensor?**
- **From source, the answer is the average.** The trigger compares the integer mean of 34 truncated sensors against
  `> 65` (TPM:656-679; `firmware.md` §2, §5).
- **The on-card tests are registered only where they can work.**
  - The **R0 probe** comes first on each card: one short launch with no sampler, then `sptrace` (§3.2). It shows
    whether the card's power-management task is alive, stuck, latched in `THERMAL_DOWN`, or off.
  - The source predicts that aifoundry3 is latched (`C §1.1`, checked here against TPM:2238-2246, 1788-1791, 2404-2458),
    that card 1's DVFS is off (`C §1.2`), and that aifoundry2 is inside its thermal loop whenever it rests at 66 °C or
    above.
  - **TRIG-B**, the trace test, is registered only on cards the probe classifies as ALIVE (§3.3).
  - **TRIG-A**, the clock test, runs on aifoundry2 today if its die rests at 65 °C or below (§3.4, §3.5).
- **Honest expectation [inference].** Today may leave Q1 with no on-card test at all. In that case the report says so,
  and the answer rests on source plus one fact: the host reads the same function the governor reads.

**Q2: does the same work placed at the edges run longer before the trigger?**
- **Primary item: PLACE-t.** It is `L = ln min(t66_PER16, C) − ln min(t66_INT16, C)` in Tier L. Here `t66` is the time
  from the kernel start until the governor's own input, `temp_c.minshire[0]`, first reads 66. `C` is the 150 s chain
  cap.
- **Refinements:**
  - where on the edge: the memory strip, the bare die edge, or the centre;
  - the same contrast at half power;
  - an airflow-gradient test with two sensor-field-balanced antisymmetric pairs;
  - a superposition test built on a correct minion-level identity, `INT16@16 ∪ PER16@16 = UNI32@16`;
  - the hot-spot counterfactual (CONC);
  - the map check (MAP);
  - equal-power and equal-work checks.

**The statistics.**
- Every sign test has three outcomes (holds, fails, None; §2.3).
- Censored pairs enter as `ln min(t66, C)` (§2.2).
- Before registration, a power step projects each item's validation interval. Items that cannot reach their band become
  **"reported, not tested"** (§2.4).
- The V3 outcome words and the pre-registration hash are kept (§6.3):
  - `PREREG-A2.md` freezes aifoundry2's source-derived items before today's session;
  - `PREREG.md` freezes card 1's items after development;
  - `block.sh` refuses a validation block whose hash differs.

**Card time.** About 3.7–7.1 h on aifoundry3, 1.8–5.4 h on card 1 and ≤ 0.5 h on aifoundry2 today. The range depends
on which block types the power step keeps. The caps are 8 h, 5.5 h and 0.5 h (§8). Budget 3–8 times that in wall-clock time (`W/docs/findings/14-card-behaviour.md:131-132`).

### 0.1 Why development stays on aifoundry3

`t66` is a host reading, so it works on any card whose die idles below 65 °C. That is true whatever state the
governor is in.

| | aifoundry3 | aifoundry1 card 1 | aifoundry2 |
|---|---|---|---|
| Idle vs the 65 °C trip | 54–57 °C, below (dfo:14-16) | 56–57 °C, below (dfo:18-20) | 67–77 °C after 900 s of cooling, above (dfo:10-12) |
| Time resolution of `t66` | heats slowly: all-shire 60 → 66 °C in 20–30 s (ic:2,5,8), so a Tier L `t66` spans many SP passes | heats 1.6–1.7× faster to the same rise (§5.1), so `t66` is shorter | proxy impossible above 65 °C |
| Neighbour hazard | none | card 0 overheats | none |
| Clean record | 407/407 heater processes rc 0 (dfo:17) | 151/151 (dfo:21) | — |
| Governor | predicted latched; it does not matter for `t66` | predicted off | clock can move, but only from a cool die |

aifoundry3 remains the best development card. The critique's finding changes only where TRIG-B can run, not where
development runs.

---

## 1. What changed from DESIGN.md

Every fix in `C §5` was applied, applied in modified form, or rejected. Rejections, with reasons, are collected in
§11. The table lists the substantive changes.

| # | Change | From | Where |
|---|---|---|---|
| 1 | The R0 probe runs per card before any trace test. TRIG-B is registered per card, only if the probe shows ALIVE | `C §1.4`, fix 1 | §3.2–3.3 |
| 2 | Three-outcome `SIGN`: fails on the opposite sign **or** on a CI wholly inside ±band. A two-sided `NONZERO` type is added for the gradient pairs | `C §2.1`, fix 2 | §2.3 |
| 3 | Power step P1 after R1 and binding power step P3 after R3. An item is registered only if its projected half-width ≤ 0.7 × band | `C §2.2`, fix 3 | §2.4 |
| 4 | Censored runs enter as `ln min(t66, C)`, with no dropping. A sign-count test is reported. Censoring target ≤ 5% | `C §2.3`, fix 4 | §2.2 |
| 5 | Superposition uses the exact minion-level identity `INT16@16 ∪ PER16@16 = UNI32@16`. CHK16E/O and H5 are dropped. SPREAD-t is reported only | `C §3.3`, `§3.10`, fix 5 | §4.6 |
| 6 | Burn-in chain at every block start. Williams (carryover-balanced) orders. A pre-registered edge-cooling covariate | `C §3.1`, fix 6 | §4.4 |
| 7 | Trace events: re-arm condition, coverage by ring overlap, printed value against the host mean, exit events, a fitted SP tick rate | `C §1.3`, fix 7 | §3.3 |
| 8 | `t0` from the heater's own `t_start_ms`. TRIG-A classifies down-steps by step size | `C §3.4`, `§3.6`, fix 8 | §2.1, §3.4 |
| 9 | Gradient pairs, **re-chosen** to be balanced in the sensor field (W8b/E8b, N8b/S8b). Airflow void rule from free per-run covariates | `C §3.5`, fix 9, modified | §4.2, §4.4 |
| 10 | Start edges are **not** alternated (rejected, §11 R1). Tier L is primary instead, and the truncation bias is stated | `C §3.2`, fix 10 | §4.4 |
| 11 | CONC = ½[Δhot(INT16) + Δhot(PER16)] − Δhot(UNI32). MAP uses 2 repeats and the I/O sensor's peak-hold. H10's claim is narrowed | `C §3.9`, fix 11 | §4.1 |
| 12 | Card 1: S_L set by a pre-set calibration on a non-registered workload. Card-0 guard at 90 °C (owner). aifoundry2 gate on the reading only, with a warm-up run | `C §3.8`, `§4`, fix 12 | §6.1, §3.5, §7 |
| 13 | H12 at 128 minions, exploratory. H5 not testable. H11 "not tested" when no `SIGN` item is registered | `C §3.6`, `§3.10`, `§2.4`, fix 13 | §3.5, §4.1 |
| 14 | G0, the steady-state and heating-rate check from V3-IDLE, done before R2 at zero card time. First numbers are already in §5.1 | `C §3.7`, fix 14 | §5.1 |
| 15 | Equal work (ops per minion) added beside equal power. The power-normalised and ops-normalised `L` are reported for every pair | `C §3.3`, `§2.4` | §4.5 |
| 16 | κ fit gate: at least 90% of samples where the predicted floor equals the reading. The network is simulated from the block start | `C §2.4` | §2.1 |
| 17 | aifoundry2 moves from "cool mornings over 7 days" to **today**, with its own pre-registration (PREREG-A2) and an explicit NOT OBSERVABLE outcome | owner O3 | §3.5 |

**Three corrections to the inputs, found while verifying.**
- **The `--per-shire` flag belongs to the heater, not to enercat.**
  - It is the heater's flag: `sparsity_host`, `participants()`, `W/workloads/sparsity/host/main.cpp:275-287`, which
    runs hart 0 of minions 0…N−1; the kernel returns at once when `(minion & 31) >= per_shire`
    (`kernel/sparsity.c:557`).
  - `enercat_host` has no `--per-shire`. Its `--minions 0x0000ffff` (`enercat/host/main.cpp:511`,
    `kernel/enercat.c:143`) selects the same minions 0–15.
  - So the identity holds under both hosts' semantics. The design uses the heater, `lib.sh:36-44`.
- **Not every "symmetric" group has a centred centroid** (`C §3.5`). INT16, MEM8 and CEN8 have their centroid exactly
  at the grid centre (2.5, 3.5). PER16 does not: its centroid is (2.81, 3.19). EDGE8's is (3.13, 2.88). Both are
  shifted south-west, because r0 holds only 3 compute tiles against r5's 5 (`design2_sets.py` output). So a linear
  gradient leaks into `L(PER16/INT16)` with weight 0.31 per row and per column. §4.2 uses this.
- **Card 1 heats 1.6–1.7× faster than aifoundry3 to the same rise, not "4–6×"** (D:379, `C §3.8`). Those figures
  compared different starting temperatures; the per-card budget in §6.1 and §8 uses the corrected figure (§5.1).

---

## 2. Shared definitions (fixed now)

### 2.1 Unit and per-run observables

**Unit.** One **block** holds one run of each placement in its set, in a pre-set carryover-balanced order (§4.4).
Contrasts are paired within a block. A card's value is the mean of the block contrasts, with a two-sided 99% Student t
interval, df = blocks − 1 (t = 9.925, 5.841, 4.604, 4.032, 3.707, 3.499, 3.355, 3.250, 3.169, 3.106 for df 2–11).
Samples and launches inside a run are never the unit (`V3/README.md:15-20`).

**Sampler.** One 10 Hz `ettelem sample --every-ms 100 --reset-ms 1000` per run. It starts before the run's preheat and
stops at the run's end, with SIGTERM only (`W/tools/claims-v3/lib.sh:146-176`). The 10 s cap is for device processes
(launches). The sampler holds only the management node, as in every V3 block (`lib.sh:147-162`; `idle/block.sh:21-25`).

| Name | Definition |
|---|---|
| `t0` | `t_start_ms` of the run's first kernel launch (launch −1, the calibration launch), from the heater's own `SPARSITY` line. It uses the same host epoch clock as the sampler's `t_ms` (`W/workloads/sparsity/host/main.cpp:619-620`; `W/tools/ettelem/ettelem.cpp:138`). Check: `board_w` ≥ `W_idle` + 1.5 W within 0.6 s of `t0` (+3 W for ≥ 512 minions). A run failing the check is flagged, not voided |
| `W_idle` | Median `board_w` over the 2 s before `t0` |
| **`t66`** | First sample with `temp_c.minshire[0]` ≥ 66, minus `t0`. Censored at `C`: **C = 7.0 s** in Tier S, where the launch is `--seconds 7`; **C = 150 s** in Tier L, the chain cap; **C = 7.0 s** for aifoundry2's `t_down` |
| `τ_c` | The run's **edge-cooling time**: from the first reading of S+1 on the way down to the first reading of S (the launch edge). A pre-treatment covariate that measures heat removal at launch (`C §3.1`) |
| `sw_W` | Median(`board_w` − `W_idle`) from `t0` + 1 s to min(`t0` + `t66`, the launch end) |
| `ops_rate` | Σ `iters` / Σ `wall_s` over the run's measured launches (per minion, since each minion runs `iters` per launch), from the heater's `SPARSITY` lines |
| `κ` | Coupling gain, fitted as in D:84. The Foster network is fitted to the block's CAL chain (§4.4) with measured `board_w` as input, and simulated **from the block's first sample** (`C §2.4`). **Gate:** the predicted whole-degree floor equals the reading in ≥ 90% of samples of the fit window, otherwise κ = None. The critique's rms gate admits a 0.28 °C systematic misfit |
| `Δhot` | As D:85: the mean over the last 3 reset windows of (`minshire[2]` − `minshire[0]`) before min(`t66`, the launch end), minus the same over the 3 windows before `t0`. A window with a failed reset is dropped |
| `ι_io` | The mean of `ioshire[2]`, the I/O sensor's own windowed peak-hold, over the last 3 windows of the launch, minus the same over the 3 windows before `t0` (`C §3.9`). D:86's `ι` is reported beside it |
| clock | `mhz.minion` in every sample. It must read 600 MHz on aifoundry3 and card 1 (dfo:3,5), or the run is void |

### 2.2 Contrasts, with censoring kept

- **Times.** `L(A/B) = ln min(t66_A, C) − ln min(t66_B, C)`. No pair is dropped for censoring. This is a
  restricted-time contrast: conservative toward 0, with no selection (`C §2.3`).
  - Reported beside it: a sign-count over blocks, with censored runs ranked longest and two censored runs tied, and an
    exact binomial p.
  - Tier parameters are set so that ≤ 5% of runs in a registered pair are censored (§5.3).
- **Adjusted contrast.** `L_adj = L − β(ln τ_c,A − ln τ_c,B)`. The coefficient β is the pooled within-block regression
  slope of `ln min(t66, C)` on `ln τ_c` in development. It is frozen in PREREG. P3 (§2.4) chooses the primary: `L`, or
  `L_adj` if its projected half-width is smaller. The other is reported.
- **Normalised contrasts, reported for every pair** (`C §2.4`, `§3.3`):
  - power-normalised: `L_P = L + ln(sw_W_A / sw_W_B)`;
  - ops-normalised: `L_ops = L + ln(ops_rate_A / ops_rate_B)`, the ops completed before the trip.
- **κ, Δhot, ι_io:** the difference A − B.

### 2.3 Prediction types and item results (three outcomes)

The band is δ = ln 1.10 = 0.0953 for time contrasts (**[choice made here, not from data]**, kept from D:95). The κ band
is ±0.05 for PLACE-κ and LIN; §4.1 gives the others.

| Type | holds | fails | None |
|---|---|---|---|
| `SIGN+` / `SIGN−` | 99% CI excludes 0 on the predicted side | CI excludes 0 on the **other** side, **or** lies wholly inside ±band (the effect is shown negligible) | otherwise |
| `NONZERO` (gradient pairs only; the direction depends on each chassis's airflow) | CI excludes 0 | CI lies wholly inside ±band | otherwise |
| `EQUIV` | CI lies inside ±band | CI lies wholly outside ±band (lower bound > band or upper bound < −band) | otherwise (straddles an edge) |

Fewer than 3 kept blocks gives None.

### 2.4 From development to a registered item: the power steps (fixed now)

**Projection.** h(n) = t(0.995, n−1) × s / √n.
- **P1**, after R1: `s = √2 × s_run`. `s_run` is the residual SD of `ln min(t66, C)` (or of κ, Δhot, ι_io) after a
  block + placement fit over all R1 runs with identical parameters. This is "R1's scatter", with more df than R1's
  three block contrasts.
- **P3**, after R3: `s` is the SD of the block contrasts pooled over R1–R3 blocks with identical parameters (at least
  6), or `√2 × s_run` if that is larger.
- **For card 1,** `s_card1 = s × max(1, CV_card1 / CV_a3)`. CV is the run-level SD of `ln t66` of the CAL chains at the
  frozen start edge on each card (§6.1).

**Registration rule (P3), per Q2 item, on aifoundry3's pooled development data:**
1. The development 99% CI excludes 0 → candidate `SIGN` on that side. For the gradient pairs, `NONZERO`.
2. Otherwise, if the CI lies inside ±band → candidate `EQUIV`.
3. Otherwise → **reported, not tested** (`C §2.4`: the "EQUIV by default" fallback of D:409 is removed).
4. **Power:** a candidate is registered only if h(n_val) ≤ 0.7 × band (`EQUIV`) or ≤ 0.7 × |development estimate|
   (`SIGN`, `NONZERO`). Otherwise it is **reported, not tested**.
   - Why 0.7 rather than 1.0, which is the literal "above its band": at h = band an `EQUIV` item holds only if the
     estimate is exactly 0.
   - At 0.7 and df 4–7, a true null holds `EQUIV` with probability 0.87–0.95, and a true effect at the development
     estimate holds `SIGN` with probability 0.93–0.98, before any winner's-curse shrinkage **[computed here from the
     t quantiles]**.
5. **n_val** per block type is the smallest n in [5, n_max] meeting step 4 for the type's primary item. n_max comes from
   the card-1 cap in §8. If no n ≤ n_max meets it, n_val = 5 and the item is reported, not tested.
6. POWER and WORK (§4.5) are always registered, as `EQUIV`, on every pair of a registered item.
7. **TRIG-A and TRIG-B take their prediction from source ("H1 holds"), not from development.** They are registered by
   the probe rule (§3.2).

**What P1 decides** (before R2): D-S, D-L16 and D-L8 (§5.3), and whether a block type goes on. A block type is dropped
if none of its items can reach step 4 at the n_max of §8. Its items are then reported, not tested, if they have any data.

### 2.5 Outcome words, multiplicity

- **Outcome words** are V3's, over the validation cards registered for the item (`card_verdicts`,
  `W/tools/claims-v3/idle/reduce.py:454-463`):
  - PASS: holds on every registered card;
  - FAIL: fails on every one;
  - CARD-DIFFERENT: holds on some and fails on others;
  - INSUFFICIENT: None on any registered card, including "not observable" today on aifoundry2.
- Items never registered are **reported, not tested**. aifoundry3's values are REPORTED (`idle/reduce.py:30-36`).
  INSUFFICIENT and "not tested" never count as "survived".
- **Multiplicity** (`C §2.4`):
  - Card 1 carries at most 15 registered items at 99%: the 13 registrable items of §4.1, plus TRIG-A and TRIG-B if
    card 1 is ALIVE.
  - Under a global null, each `SIGN` item holds falsely with probability 0.005 (one tail of a 99% interval). The
    expected number of false "holds" is therefore ≤ 0.07.
  - The report states the family size. No Bonferroni correction is applied (the V3 practice at 99%).

---

## 3. Q1: the average or one sensor

### 3.1 Source (unchanged from D:28-33)

The only temperature the thermal test reads is `pvt_get_minion_avg_temperature()` (TPM:656). That is
`floor(Σ floor(T_i)/34)` over the 34 minion-shire sensors (`firmware.md` §2). The test is `> 65`, and it logs the value
it compared (TPM:668-679). No per-sensor or maximum path changes the clock (`firmware.md` §5). The host's
`temp_c.minshire[0]` is the same function (`firmware.md:107-115`).

**Hypotheses.** H1 (mean) against H1′ (the hottest sensor), as D:108-109.

### 3.2 The R0 probe, per card (one launch, no sampler, no state change)

**Procedure.** Run on each card before any other card work there. On aifoundry1, `V3_DEVICE=1` and the card-0 guard
are on (§7).
1. `et-who`, `who`, `ps`, the lock free and no CI job (`lib.sh:62-97`). Then one 1 s die reading (`die_c`,
   `lib.sh:103-104`), which gives `R`.
2. `ettelem sptrace p0.bin`. This is the **level inference**:
   - `MS nn Voltage` lines → DEBUG;
   - `Host_Iface`/`pc_vq` lines → INFO (`C §4`);
   - neither → WARNING or lower.
3. One 2 s heater launch under `hold10` with **no sampler open**: `UNI32@4` (128 minions), `--seconds 2`. Any kernel
   makes the master minion busy, which is all the power branch needs. The light load keeps the rise below 1 °C even at
   800 MHz, so a cool aifoundry2 cannot cross 65 °C during its probe [inference: ic:2's +3 °C in 2.2 s at ≈ 27 W,
   scaled to ≈ 3–6 W].
4. `ettelem sptrace p1.bin` immediately, with no query in between. Then `ettelem config` (read-only).

**Classification** (at INFO, which V3 left on every card: `W/tools/claims-v3/tel/block.sh:316, 408`). Lines are counted
only from entries newer than `p0.bin`'s newest entry.

| Class | Lines in `p1` | Meaning |
|---|---|---|
| **ALIVE** | `Power throttle up/down` (CRITICAL, TPM:866, 880) **and** `Power Throttle event received` (INFO, TPM:2421) after it | the power task runs and returns, so the thermal trigger is re-armed after each episode |
| **STUCK** | power lines, but no `event received` line after the first | the power task spins in `power_throttling(POWER_DOWN)` (TPM:2238-2246 cannot exit at TDP 0 on the bottom point; TPM:1788-1791 returns without acting). The thermal trigger is live until its first firing, then latches (TPM:669, 2366-2374) |
| **SILENT** | no governor line | LATCHED (after a STUCK card first crossed 65 °C), or DVFS off (`active_power_management` = 0, TPM:670, 844), or, on a die at ≥ 66 °C, **LOOP**: inside the live thermal loop, which blocks both branches (TPM:669, 845; `firmware.md:189-194`). The trace cannot tell these apart; §3.2's predictions use each card's history |

**If a card is found at WARNING or lower,** it has rebooted since V3. The `received` line is then invisible.
- Governor lines present → STUCK if TDP = 0 per `config` (aifoundry3); otherwise treated as ALIVE-candidate. Its first
  thermal event in the session must be followed by a `Thermal idle state event`, or it is reclassified STUCK.
- No lines → SILENT.
- No level change is made for the probe.

**Predictions, fixed now:**
- **aifoundry3: SILENT (latched).** It was reset on 25 September (`14-card-behaviour.md:213-215`) and then heated to
  90 °C in V3 (dfo:14-16). If it has rebooted since: STUCK.
- **Card 1: SILENT (off).** Its clock read 600 MHz in 359,657 samples, including 11,446 at < 65 °C and 45–63 W, and
  up to 88 °C with no thermal step (dfo:5; `C §1.2`).
- **aifoundry2: LOOP (SILENT)** if R ≥ 66, and ALIVE if R ≤ 65 (E10's clock steps: `16-dvfs-and-leakage.md:67-91`).

**Consequences, applied mechanically:**

| Probe result | TRIG-B on this card | Log level |
|---|---|---|
| ALIVE | registered (§3.3); aifoundry2 in PREREG-A2, card 1 in PREREG | set WARNING (O2) for the card's blocks, restore the level found at the end (§3.3) |
| STUCK on aifoundry3 | **TRIG-B1 one-shot**, reported (§3.3, last bullet) | WARNING only for the one-shot run, then restore |
| STUCK on card 1 | not registered; the one-shot would fall in development-like runs on a validation card, so it is reported only | unchanged |
| SILENT | not registered; the report says why (latched, off or loop) | unchanged |

Card time: about 20 s per card.

### 3.3 TRIG-B, the trace test (registered only on ALIVE cards)

The trace test runs at WARNING. Its unit is the **thermal event**, a `Thermal throttle down event, current temperature: T`
line (TPM:673) or a `Thermal idle state event, current temperature T` line (TPM:2371).

**Coverage and timing** (`C §1.3`):
- **Coverage.** A dump counts only if the newest entry of the previous dump reappears in it. The ring overlapped, so
  nothing was lost. This test does not depend on either hypothesis.
- **Timing.** The SP u64 timestamp rate and offset are fitted once per session by least squares. The fit uses every
  `Power throttle up/down` line, which follows a kernel's `t_start_ms` within one SP pass, and every `Power idle state
  event`, which follows the process end within one pass. A fit residual above 0.3 s voids the session's TRIG-B.

**Per event E**, with `m(E)` the host mean readings in [E − 0.5 s, E + 0.5 s] and `h(E)` the windowed high over the same
span:
- **Discriminating** if max `h(E)` ≥ max `m(E)` + 2. The two rules then print different values.
- **H1-consistent:**
  - a down event with printed T ≥ 66 and T within ±1 of some `m(E)`; or
  - an idle event with printed T ≤ 65, T within ±1 of some `m(E)`, and max `m(E)` ≥ 65.
- **H1′-consistent:** printed T ≥ max `m(E)` + 2 (the governor printed the hot sensor, not the mean).

**First-event test,** per re-armed run.
- A run is **re-armed** if `h` ≤ 65 in the 3 samples before `t0`. Under both rules the governor is then below
  `THERMAL_DOWN`, which answers the critique's re-arm point.
- H1 predicts the run's first down event within [t_m − 0.3, t_m + 0.6] s, where t_m is the host mean's first ≥ 66.
- H1′ predicts it within [t_hi − 0.3, t_hi + 0.6] s, where t_hi is the high's first ≥ 66.
- A re-armed run in which `h` ≥ 67 for ≥ 1 s while the mean read ≤ 64, with no down event in that span, is an
  H1-consistent control observation. This is D:117's B-neg, with the re-arm condition built in.

**Rule.**
- **Holds** if there are ≥ 5 discriminating events, ≥ 90% of them H1-consistent, ≤ 1 H1′-consistent, and no
  first-event test fits H1′.
- **Fails** if ≥ 50% of the discriminating events are H1′-consistent, or ≥ 2 first-event tests fit H1′.
- **None** otherwise, and on a SILENT card.

**Log-level handling** (`C §4`):
- `ettelem-hp loglevel warning` is used at the start of a TRIG-B session, after the level inference. At the end, the
  level found is restored from an EXIT trap.
- On an intrusion abort (exit 3), the card is left at once and not touched. It stays at WARNING, the boot default
  (`FW:services/log.c:60`). The next session restores or sets the level.

**TRIG-B1 one-shot** (aifoundry3, only if STUCK). The first crossing of 65 °C since boot is the only thermal event the
card will ever log. It is spent deliberately, as R1's first run, before any preheat can cross 65 °C:
- set WARNING, dump the idle ring;
- run an `INT16@32` chain from rest until the mean reads 66, plus 2 launches, with the 10 Hz sampler (`--reset-ms 1000`);
- dump, restore the level.

The printed T and the host mean and high at the event are reported: H1 predicts host mean 66; H1′ predicts host mean
≈ 62–64 with the high at 66. It is one observation on the development card, so it is reported, never registered.

### 3.4 TRIG-A, the clock test (aifoundry2)

This test replaces D:124-132 with the critique's step-size classification (`C §3.6`). For each run with
`--reset-ms 1000`:
- **`t_up`:** the first sample at 800 MHz.
- **`t_hi`:** the first sample at 800 MHz whose windowed high reads ≥ 66 (the H1′ trip).
- **`t_m`:** the first sample whose mean reads ≥ 66.
- **`t_down`:** the first **one-point** down-step, 800 → 700 MHz.
  - A thermal reduce steps one VMIN-LUT point (TPM:1899-1914).
  - A single 800 → 600 change is an idle or boot reset (`go_to_idle_state`, TPM:1975-1979). It is excluded, whatever
    kernel boundaries are nearby.
  - The power branch cannot act: board power stays < 65 W at 128 minions (§3.5).

**Separating runs:**
- (a) `t_m − t_hi` ≥ 1.5 s; or
- (b) a **rise under a hot max**: the windowed high already reads ≥ 67 at `t_up`, and the clock holds 800 MHz for
  ≥ 0.5 s (≥ 3 SP passes of 133–162 ms). Under H1′ the governor would have been in `THERMAL_DOWN` and could not have
  stepped up.

**Fits:**
- H1: (a) `t_down` ∈ [t_m − 0.3, t_m + 1.2] s, or (b) as defined;
- H1′: (a) `t_down` ∈ [t_hi − 0.3, t_hi + 1.2] s.

The slack is kept from D:130.

**Rule.**
- **Holds** if there are ≥ 5 separating runs over ≥ 2 blocks, ≥ 80% fit H1 and ≤ 1 fits H1′.
- **Fails** if ≥ 50% fit H1′.
- **None** otherwise, including "not observable".

The ≥ 3 cool periods of D:132 are removed, because O3 allows one day only. The report states this limit: one day,
one room.

If card 1's probe is ALIVE **and** its smoke run shows the clock leaving 600 MHz below 65 °C, TRIG-A is also registered
on card 1. The 0.18.0 steps are 50 MHz, so a one-step reduce is 600 → 550 (FW18h:56-58).

### 3.5 aifoundry2 today (O3): the same-day clock-step attempt

**Pre-registration.**
- `PREREG-A2.md` and `prereg-a2.json` are written and hashed **before the session**. They hold:
  - TRIG-A;
  - TRIG-B, conditional on the probe rule of §3.2;
  - H12, as "reported";
  - the parameters below;
  - the sha256 of every file in `hp/a2/`, which holds frozen copies of every module it imports (`sptrace_events.py`,
    `hplib.py`), so later development edits cannot reach it.
- `hp/a2/block.sh` refuses `HP_ROUND=a2` if any hash differs.
- These items take their predictions from source. aifoundry3 cannot develop them, because its clock is pinned and its
  trace latched. So freezing them before development is not premature.
- Nothing in `hp/a2/` changes after the session starts.

**Session** (one, today, card lock held; `V3_DRY=1` of the whole session first):
1. **Gate** (`C §4`): `et-who`, `who`, the process scan, no `Runner.Worker`, no queue. There is no "≥ 6 h with no
   launch" condition.
2. **R0 probe** (§3.2) → gives `R` and the probe class.
3. **Smoke:** the sampler, one 2 s `UNI32@4` launch, `sptrace`, `reduce_a2.py --check-pass`. About 30 s, and a
   negligible heat.
4. **Branch on the rest reading `R`**, fixed now:

| `R` | Class | What runs | Outcome |
|---|---|---|---|
| ≤ 62 | COOL | up to 2 A2 blocks at start edge S_A2 = 63 (64 → 63 falling, as E10: `feasibility.md:104`) | TRIG-A and TRIG-B (if ALIVE) tested |
| 63 | COOL− | the same, at S_A2 = 64 (the 65 → 64 edge, reached quickly; 64 → 63 would approach the rest asymptotically) | tested; `t_down` is shorter |
| 64–65 | MARGINAL | 1 A2 block at S_A2 = 65 (66 → 65 edge). Only separating runs of type (b) and exit events are likely | tested; None is likely |
| ≥ 66 | WARM | one documentation run: a 7 s `UNI32@4` launch with the sampler. Expected: 600 MHz throughout, mean ≥ 66. Then stop | **TRIG-A, TRIG-B, H12: NOT OBSERVABLE** → INSUFFICIENT, with the reason "rest R °C ≥ 66: the governor sits in its thermal loop at the 600 MHz bottom point (TPM:2316-2360; `firmware.md:189-194`), so no clock step can be provoked" |

   If the first reading is WARM, **up to 3 more 1 s readings are allowed today**, each ≥ 2 h apart, each after the
   gate, the last before 22:00 local time. The session runs at the first reading ≤ 65. Nothing carries over to another
   day (O3).
5. **An A2 block:**
   - one **warm-up run** (`UNI32@4`), discarded (`C §4`: the first run of a period starts from rest, the others from a
     falling die);
   - then 8 measured runs in a seeded shuffle: `INT16@8` ×2, `PER16@8` ×2, `UNI32@4` ×2 (the H12 set, 128 minions
     each), and `B4C@32` ×2 (`0x00606000`, the centre 2 × 2, 128 minions concentrated, for large `t_m − t_hi`).
   - Each run:
     - waits for the S_A2 edge (cap 300 s, else void);
     - runs the sampler from ≥ 5 s before to 10 s after the launch, so it catches the exit event;
     - makes one 7 s launch under `hold10`;
     - then, if TRIG-B is registered, `sptrace`.
   - A second block runs only if the first block's last run reached its edge within 300 s.
6. **End:** restore the log level (if set), `block_end`.

**Why 128 minions** (`C §3.6`).
- 800 MHz costs about 1.9× the dynamic power of 600 MHz (`feasibility.md:217`).
- 128 random-data minions add about 6 W of switching over the 800 MHz idle. Board power stays near 42 W, well under
  the 65 W TDP [inference, from D:193-195 and `C §3.6`].
- E10 puts the first down-step at 1.3–1.5 s for ones (≈ 56 W) and 5.6–6.1 s for zeros (≈ 39 W) (dfo:22-28). So
  `t_down` is expected at 4–5 s, inside the 7 s launch.

**H12 (DVFS-PLACE), exploratory.** `ln(min(t_down_PER16@8, 7) / min(t_down_INT16@8, 7))` per block is reported with its
range. With at most 2 blocks it is not a test.

---

## 4. Q2: placement

### 4.1 Hypotheses and items

| Id | Hypothesis | Item (statistic, block type) | Prediction on card 1 |
|---|---|---|---|
| H2 | the edges trip later (owner) | **PLACE-t** `L(PER16@32/INT16@32)`, L16, primary; **PLACE-κ** κ_PER − κ_INT, L16; **PLACE8-t** `L(PER16@16/INT16@16)`, L8; **PLACE-tS** `L(PER16/INT16)`, S (secondary, D-S) | by §2.4 from aifoundry3: `SIGN+` supports H2, `SIGN−` supports H3, `EQUIV` supports H4 |
| H3 | the centre trips later | same items | same |
| H4 | the null: total power only | same items, band δ (times) or ±0.05 (κ) | same |
| H6 | linearity | **LIN**: r = κ_UNI32@16 − (P_I κ_INT16@16 + P_P κ_PER16@16)/(P_I + P_P), measured powers P, all three runs in one L8 block (§4.6) | `EQUIV` ±0.05 if registered |
| H7 | concentration lifts the hot spot | **CONC** = ½[Δhot(INT16@32) + Δhot(PER16@32)] − Δhot(UNI32@16), Tier S. The sensor with the largest offset enters every term once (`C §3.9`). The L16 replication and the INT/PER split are reported | `SIGN+`, band 0.5 °C |
| H8 | the memory-strip side couples less | **MEM** `L(MEM8/CEN8)`, L8 | by §2.4 |
| H9 | the bare N/S edge couples less | **EDGE** `L(EDGE8/CEN8)`, L8 | by §2.4 |
| H3′ | airflow gradient across the heatsink (`C §3.5`) | **GRAD-EW** `L(E8b/W8b)`, **GRAD-NS** `L(N8b/S8b)`, G8 | `NONZERO` or `EQUIV` by §2.4 (the direction depends on each chassis) |
| H10 | the map's I/O corner is where the latency map puts it | **MAP** ι_io(B4NE) − ι_io(B4SW), 2 repeats of each per Tier S block | `SIGN+`, band 0.5 °C |
| H11 | transfer | every registered `SIGN` item holds on card 1 | "not tested" if no `SIGN` item is registered (`C §2.4`) |
| H13 | equal power | **POWER** `sw_W_A − sw_W_B` on every registered pair | `EQUIV` ±0.5 W |
| — | equal work | **WORK** `ln(ops_rate_A/ops_rate_B)` on every registered pair | `EQUIV` ±0.01 |
| — | spreading | **SPREAD** `L(UNI32@16/INT16@32)`: reported only. Under linearity it equals ½·PLACE plus the intra-tile term, which LIN isolates (§4.6) | — |
| H12 | the clock consequence | DVFS-PLACE, aifoundry2 today (§3.5) | reported |

- **H5 is dropped as not testable.** Its leakage-convexity term is about 0.04 W (`observability.md:211-214`; `C §3.10`).
- **H10 is narrowed** (`C §3.9`). It tests where the I/O sensor sits relative to the grid, the NE corner of the drawing.
  The memory-strip sides come from memprobe's `ms_pos` (`observability.md:259-261`), and H10 neither confirms nor voids
  them.
- **M1 against M2** (better cooling against unsensed silicon) stays out of reach for host observables (D:579-584).

**Expectations before data [inference].**
- PLACE-t lies within ±10%, so H4 holds and H2 at most a few percent (M2).
- CONC holds with a difference of 1–2 °C.
- MAP holds.
- LIN and GRAD end reported, not tested, for power reasons.
- H1 is untested on-card unless aifoundry2 is cool today.

### 4.2 Placements, verified against the layout

`design2_sets.py` reads `MARTY` and `EMPTY` from `W/workloads/nocbench/analyze.py:50-60`. It maps them into the die
frame of `observability.md:262-284` (die row r = map x, column c = map y + 1). It asserts:
- every mask below;
- DESIGN's masks and the critique's masks, all bit-for-bit;
- the set identities;
- the minion-level identities;
- the mirror images;
- that D:154's identity is false.

Output: `design2_sets.json` [computed here].

```
      c1(W,MS0-3)  c2     c3     c4      c5       c6(E,MS4-7)
 r0:   S0          S8     S3     M/S     IO/PCIe  IO/PCIe      <- N die edge (I/O, PCIe)
 r1:   S24         S16    S4     S12     S20      S28
 r2:   S9          S1     S13    S21     S29      S5
 r3:   S25         S17    S14    S22     S30      S6
 r4:   S2          S10    S18    S26     S15      S7
 r5:   S11         S19    S27    M/S     S23      S31          <- S die edge
```

| Name | `--shires` | Per shire | Minions | Where (die frame) | Beside I/O-PCIe | Beside M/S | Centroid (r, c) | Block |
|---|---|---|---|---|---|---|---|---|
| INT16 | `0x6477f412` | 32 or 16 | 512 or 256 | interior r1–r4 × c2–c5 | 1 | 2 | (2.50, 3.50) | L16, S; L8 at @16 |
| PER16 | `0x9b880bed` | 32 or 16 | 512 or 256 | perimeter ring, corners S0, S11, S31 | 1 | 3 | (2.81, 3.19) | L16, S; L8 at @16 |
| UNI32 | `0xffffffff` | 16 (4 on aifoundry2) | 512 (128) | everywhere, minions 0–15 | 2 | 5 | (2.66, 3.34) | L16, S, L8; A2 |
| MEM8 | `0x130002e4` | 32 | 256 | beside the memory strips, c1/c6 × r1–r4 | 1 | 0 | (2.50, 3.50) | L8 |
| EDGE8 | `0x88880909` | 32 | 256 | the bare N/S edges, r0/r5 | 0 | 3 | (3.13, 2.88) | L8 |
| CEN8 | `0x04647010` | 32 | 256 | centre band, c3–c4 × r1–r4 | 0 | 2 | (2.50, 3.50) | L8 |
| **W8b** | `0x02026606` | 32 | 256 | r2–r3 × c1–c3 plus r4 × c1–c2 | 0 | 0 | (2.88, 1.88) | G8 |
| **E8b** | `0x606080e0` | 32 | 256 | the mirror of W8b (c → 7 − c) | 0 | 0 | (2.88, 5.13) | G8 |
| **N8b** | `0x01213212` | 32 | 256 | r1–r2 × c1–c4 | 0 | 1 | (1.50, 2.50) | G8 |
| **S8b** | `0x06464404` | 32 | 256 | the mirror of N8b (r → 5 − r) | 0 | 1 | (3.50, 2.50) | G8 |
| B4NE | `0x30100020` | 32 | 128 | beside I/O-PCIe | 2 | 0 | (1.5, 5.5) | S (MAP) |
| B4SW | `0x00080c04` | 32 | 128 | the far corner | 0 | 0 | (4.5, 1.5) | S (MAP) |
| B4C | `0x00606000` | 32 | 128 | the centre 2 × 2 | 0 | 0 | (2.5, 3.5) | A2 (TRIG-A) |
| ALL24 (CAL, preheat) | `0xffffffff` | 24 | 768 | everywhere; not a registered placement | — | — | — | every block |

**Identities.** Each was asserted by `design2_sets.py`:
- INT16 ∪ PER16 = all 32 shires, disjoint;
- MEM8 ∪ EDGE8 = PER16;
- CEN8 ⊂ INT16;
- at the minion level, `INT16@16 ∪ PER16@16 = UNI32@16`, disjoint;
- `INT16@32 ∪ PER16@32 = ALL@32`;
- `INT16@32 ≠ UNI32@16` as minion sets (D:154's identity is false).

**Why W8b/E8b and N8b/S8b and not W12/E12/N12/S12** (`C §3.5`, rejected in form: §11 R3).
- The critique's masks are correct: `0x03076616`, `0x747090e0`, `0x31313232` and `0x4646c4c4` were each reproduced
  here.
- But E12 and N12 each hold **both** tiles beside the unsensed I/O-PCIe cells (S20, S28). The I/O sensor is excluded
  from the mean, and PCIe has no sensor (`firmware.md:104-105`).
- So M2 alone predicts that E12 and N12 trip later, with no gradient at all. E12 also holds both tiles beside the master
  and spare cells, and W12 holds none.
- The balanced pairs are exact mirror images. Neither side touches I/O-PCIe, the master/spare adjacency is equal, and
  the memory-strip count is equal (3 and 3; 2 and 2).
- W8b/E8b is the largest such E–W pair in rows r1–r4. N8b/S8b is the largest N–S pair, 10 + 10 with r2/r3 × c5–c6
  added, cut to 8 + 8 to stay in the 256-minion class [computed here]. Their centroid separations are 3.25 columns
  and 2 rows.

**Gradient leakage (reported, not registered).**
- A linear gradient per row g_r and per column g_c leaks into `L(PER16/INT16)` as ≈ 0.31 g_r − 0.31 g_c. It leaks into
  `L(EDGE8/CEN8)` as ≈ 0.63 g_r − 0.63 g_c.
- The gradients are estimated as g_c ≈ GRAD-EW / 3.25 and g_r ≈ −GRAD-NS / 2.
- The gradient-corrected PLACE-t is reported beside PLACE-t. The correction is labelled approximate: G8 runs at
  256 minions, L16 at 512.

**Other features.**
- The die orientation is inferred (a transpose). A mirror would swap the labels W↔E or N↔S but no class
  (`observability.md:269-270`).
- The heater is no NoC confound: unselected shires and minions return at once (`W/workloads/sparsity/kernel/sparsity.c:553-562`),
  and TensorFMA on scratchpad data uses no mesh after setup (`observability.md:316-318`; `C §3.3`).

### 4.3 Block types

Every run is `hold10 $HEATER --test fma --type fp32 --pattern none --values randn --shires <mask> --per-shire <n> --seconds <s> --seed 1`
(`lib.sh:36-44, 122-123`). Power at 25.6 mW per minion (`16-dvfs-and-leakage.md:160-162`): 512 → 13.1 W, 256 → 6.6 W,
128 → 3.3 W, 768 → 19.7 W.

| Type | Start edge, cap | Runs after the burn-in (order) | Items | Priority |
|---|---|---|---|---|
| **L16** | S_L (60; R1 may move it to 59–62), chains of 2 s launches, stop 2 launches after the live mean first reads ≥ 66, cap 150 s | INT16@32, PER16@32, UNI32@16 (Williams order of 3, 6 sequences) | PLACE-t, PLACE-κ, SPREAD, CONC (L), POWER, WORK | 1 |
| **L8** | S_L8 (63; 61–64), same chain rule | MEM8, EDGE8, CEN8, INT16@16, PER16@16, UNI32@16 (Williams order of 6) | MEM, EDGE, PLACE8-t, LIN, POWER, WORK | 2 |
| **S** | S = 64 (65 → 64 edge), one `--seconds 7` launch, then 10 s of idle | INT16@32, PER16@32, UNI32@16, B4NE ×2, B4SW ×2 (seeded shuffle; B4 runs heat < 0.5 °C, so carryover is negligible) | CONC, MAP, PLACE-tS, PLACE-κ(S), POWER, WORK | 3 |
| **G8** | S_L8, same chain rule | W8b, E8b, N8b, S8b (Williams 4 × 4) | GRAD-EW, GRAD-NS | 4 |

**Dropped:** CHK16E and CHK16O. They served only D:154's false identity (`C §3.3`).

**Order.** Block k uses Williams sequence (k + seed) mod m, and the seed is logged. The predecessor placement and its
`sw_W × duration` are recorded for every run.

### 4.4 Start condition, burn-in, carryover, covariate, void rules

**Strict start from above** (`W/docs/findings/03-experiments.md:31-43`; start spread ±0.11 °C, `:45-46`):
1. If the mean is below the target, 2 s `ALL24` preheat bursts run until it reads ≥ the target, at most 30 bursts.
   - Targets: 68 for S, S_L + 2, and S_L8 + 2.
2. The card then idles with only the sampler open, until the mean first reads S on the way down (the S+1 → S edge).
3. Launch within one sample (100 ms) of the edge. The edge wait is capped at 600 s, or the run is void. `τ_c` is logged.

**Burn-in** (`C §3.1`; `14-card-behaviour.md:126`). Every block starts with a burn-in **CAL** run:
- For Tier L blocks: an `ALL24` chain run through the full protocol, from the block's own start edge to `t66` + 2
  launches.
- For S blocks: one 7 s `ALL24` launch from the 64 edge.
- The first block of a session gets 2 CAL runs.
- CAL runs are never in a contrast. Their `t66` is recorded:
  - for between-block drift, reported;
  - as the segments for the block's κ network fit;
  - for card 1's calibration (§6.1).

**Carryover** (`C §3.1`). Williams orders (§4.3) make each placement follow each other placement equally often over a
full cycle of sequences. The predecessor's energy is recorded.

**Covariate** (`C §3.1`). `τ_c` is pre-registered as the single adjustment covariate (§2.2).

**The whole-degree start is not dithered** (§11 R1).
- The fractional-part bias of `C §3.2` is real: about ±1–2 sensor-degrees out of the 35 a Tier S run adds, 3–6%.
- But a whole-degree change of the edge leaves every sensor's fractional part as it was, so alternating 63/64 would not
  dither it.
- **Mitigation:** Tier L is the primary tier, where the same bias is about 5× smaller relative to the +171
  sensor-degrees needed (`C §3.2`). The bias is also stated as one reason Tier S magnitudes do not transfer between
  cards.

**Void rules** (fixed now; the R-rounds may set the numeric limits within the ranges given):
- **Run void** if any of:
  - heater rc ≠ 0 (aifoundry3's old-binary crash signature is 1.08 s: `14-card-behaviour.md:304-318`);
  - a sample off the expected clock;
  - the edge not reached within 600 s;
  - a sampler gap > 1 s in the measured window;
  - a safety stop;
  - WORK outside ±5% of the block median. That is a broken launch, not a finding; WORK within ±1% is the registered
    check.
  - A void run is re-run once, at the end of its block. A second void drops the placement from that block.
- **Block void** (airflow and ambient; `C §3.5`, in modified form):
  - any run's `τ_c` outside [0.5, 2.0] × the block median (dev may set [0.33, 3]); or
  - the range of `W_idle` over the block's runs > 1.0 W (dev may set 0.5–2.0 W).

  This uses free per-run measures of heat removal at the edge instead of extra reference runs (§11 R4). A block is
  kept only if every registered pair in it is complete. Aborted blocks (exit 3) are re-queued whole, and their data
  are never used.

### 4.5 Equal power and equal work

- **POWER (H13):** `EQUIV` ±0.5 W on `sw_W_A − sw_W_B` for every registered pair.
  - Linearity at 25.6 mW per minion was measured only with all 32 shires active (`16-dvfs-and-leakage.md:160-162`).
  - The ±0.5 W band admits a bias of up to 0.037 in `L`, 39% of δ (`C §2.4`). So `L_P` is reported for every pair,
    not only when POWER fails.
- **WORK:** `EQUIV` ±0.01 on `ln(ops_rate_A / ops_rate_B)` for every registered pair. The heater prints `iters`,
  `wall_s`, `cycles_per_op` and `ghz` per launch (`main.cpp:619-620`; e.g.
  `V3/raw/aifoundry3/tel/p1/gov/runs.jsonl`: 546.0 cycles per op at 1,024 minions).
  - If WORK fails for a pair, the pair's time item is decided on `L_ops`, and the report says so.
- Both checks are registered on card 1 for every pair of a registered item (§2.4 step 6).

### 4.6 LIN: the corrected superposition identity

- Minion-level identity: `INT16@16 ∪ PER16@16 = UNI32@16`, a disjoint union of minions 0–15 of each shire (§1,
  `design2_sets.py`).
- **In a linear thermal system with placement-independent power per minion,** UNI32@16's response equals the sum of
  the two halves' responses.
- In gains: κ_UNI32@16 · P_UNI = κ_INT16@16 · P_I + κ_PER16@16 · P_P, with P_UNI = P_I + P_P checked by POWER.
- **LIN's residual** r (§4.1) is registered as `EQUIV` ±0.05 if the power step allows it.
  - All three runs sit in one L8 block, so one network fit serves them.
  - UNI32@16 from S_L8 reaches 66 in about 10–25 s [inference, ic:2 scaled by 13.1/27], and κ does not need the
    crossing.
- **What the old test mixed.** D:154 compared UNI32@16 with ½(INT16@32 + PER16@32). That difference is the
  **intra-tile term**: minions 0–15 against whole tiles, with the sensor's place in the tile unknown
  (`observability.md:454`). It is reported as κ_UNI32@16(L16) − ½(κ_INT16@32 + κ_PER16@32), not tested.
- SPREAD = ½·PLACE + the intra-tile term under linearity [inference], so SPREAD is reported with that decomposition.

---

## 5. Development on aifoundry3

### 5.1 G0: zero card time, before R1 and R2

From the V3-IDLE raw telemetry (`idle_curves.py` → ic:1-9) [computed here]:
- **The all-shire heater (≈ 27 W switching) on aifoundry3:**
  - 58 → 66 °C in 20.8–23.2 s (34.5 s from 56);
  - 60 → 66 °C in 20–30 s;
  - still rising at about 0.03 °C/s at 87–89 °C after 340–410 s;
  - so no steady state was reached.
- **Cooling after that heat:**
  - 68 → 64 °C in 45–52 s;
  - 62 → 60 °C in 36–47 s;
  - 64 → 60 °C in 65–82 s.
  - These are upper bounds, because the heatsink was hotter than after a single run.
- **Linear scaling of the heating curve [inference; it ignores leakage feedback, so it overstates small-power times]:**
  - 13.1 W from 60 °C: `t66` ≈ 50–60 s (a cold heatsink);
  - 6.6 W from 62 °C: ≈ 100 s;
  - 6.6 W from 63 °C: ≈ 60 s.
- **Card 1** (ic:10-12, 29-32) heats **1.6–1.7× faster** to the same rise, with 8–14% more early board power (57.9 W
  against 50.9–53.8 W, 3–8 s into the heat):
  - +10 °C in 22 s against 34–37 s;
  - +15 °C in 45 s against 76–81 s;
  - +20 °C in 78 s against 130–138 s (ic:29-32) [computed here].

  So D:379's and `C §3.8`'s "4–6× faster" compared different starting temperatures and overstates the difference.
  Card 1 also cools about 2× faster (68 → 64 °C in 23–25 s).

These set R1's starting guesses: S_L = 60 and S_L8 = 63. The deliverable before R2 is `C §3.7`'s full G0: a Foster fit
of the three aifoundry3 heat curves (`W/tools/ettelem/flip_thermal_model.py` step 1). It predicts `t66` for 13.1 W and
6.6 W from each allowed edge on a periodic-state heatsink, and flags any (power, edge) whose predicted `t66` exceeds
120 s or whose steady state lies within 2 °C of 66 °C.

### 5.2 Rounds

| Round | Content | Card min (est.) |
|---|---|---|
| **R0** | `V3_DRY=1` of every block type and of the probe. Probe (§3.2). `--smoke`: sampler, 2 preheat bursts, one 2 s `INT16@32` launch, `sptrace`, `reduce.py --check-pass` (`W/AGENT.md:234-242`) | 2 |
| **R1a** | Only if the probe says STUCK: TRIG-B1 one-shot (§3.3), before any other run crosses 65 °C | 0–5 |
| **R1b** scouting | UNI32@16 ×2 at S_L = 60; CEN8 ×2 and W8b ×1 at S_L8 = 63; `ALL24` CAL ×2 at S_L; Tier S UNI32@16 ×2 | ≈ 25 |
| **R1c** | 3 S blocks + 3 L16 blocks | ≈ 80 |
| **P1** | Power step 1 and D-S, D-L16, D-L8 (§5.3). No card time | 0 |
| **R2** | 3 L8 blocks + 3 G8 blocks, those P1 kept. A dropped type is replaced by 3 more L16 blocks | ≈ 36–117 |
| **R3** rehearsal | The frozen protocol, with the code that validation will run: 3 blocks of each kept type | ≈ 195 (all four types) |
| **P3** | Power step 3, the registration rule (§2.4), β, the primary (`L` or `L_adj`), n_val per type. PREREG written and hashed | 0 |
| **Total** | | ≈ 220–425 min (3.7–7.1 h), depending on the block types P1 keeps; cap 8 h |

Per-block estimates on aifoundry3 [inference from §5.1 and D:340-341]:

| Block | Burn-in | Per run | Block total |
|---|---|---|---|
| S | 1.5 min | 1.7 min | ≈ 14 min |
| L16 | 2.6 min | ≈ 3 min | ≈ 12 min |
| L8 | 2.6 min | ≈ 3.3 min | ≈ 23 min |
| G8 | 2.6 min | ≈ 3.3 min | ≈ 16 min |

Wall-clock is 3–8 times that, over ≥ 2 sessions via `queue.sh` (`W/AGENT.md:243-248`).

### 5.3 Decision rules between rounds (fixed now)

- **D-S** (after R1): Tier S `t66` (PLACE-tS) stays a candidate only if ≤ 5% of INT16 and PER16 Tier S runs are
  censored at 7 s. Otherwise PLACE-tS is reported only. Its κ, CONC and MAP are unaffected.
- **D-L16** (after R1b): S_L is set so that UNI32@16's median `t66` lies in 40–100 s and ≤ 5% of runs are censored.
  - Below 40 s, lower S_L by 1, not below 59.
  - Above 100 s, or if any run is censored, raise it by 1, not above 62.
- **D-L8** (after R1b and G0): S_L8 is set so that CEN8's median `t66` lies in 40–100 s with no censored scouting run,
  within 61–64.
  - If even S_L8 = 64 gives a censored scouting run, or G0 flags 6.6 W as within 2 °C of steady state, L8 and G8 are
    dropped. MEM, EDGE, PLACE8-t, LIN and GRAD then become reported, not tested, from whatever data exist.
- **D-type** (P1): as §2.4, last paragraph.
- **D-blocks** (P3): n_val per type by §2.4 step 5.

### 5.4 One-card development cannot tune the validation items' direction

- Every direction registered for card 1 comes mechanically from aifoundry3's pooled data by §2.4.
- The Q1 items come from source.
- Development data are never pooled into validation.
- R3 is pooled with R1/R2 blocks only when their parameters are identical.

### 5.5 What may change during development, and what may not

**May change:**
- S_L within 59–62, S_L8 within 61–64;
- preheat targets within ±2 °C;
- the chain cap within 100–150 s;
- the κ gate within 85–97%;
- the void-rule limits within the ranges of §4.4;
- dropping (never adding) placements or block types;
- n per type;
- β, estimated, and the primary (`L` or `L_adj`), by P3;
- code fixes that change no observable definition.

**May not change:**
- every observable of §2.1 and its definition;
- δ and all bands;
- the prediction types and their rules;
- the registration rule and the 0.7 factor;
- the unit and the statistic;
- the probe classification.

---

## 6. Validation (predictions frozen, no iteration)

### 6.1 aifoundry1 card 1 (the Q2 items; TRIG-A and TRIG-B only if ALIVE)

**Order:**
1. R0 on card 1 (probe, smoke) any time before PREREG.
2. **V0 calibration** after R3 and **before** PREREG is frozen.
3. PREREG freeze.
4. Validation blocks.

**Practicalities.** `V3_DEVICE=1`, `ET_DEVICES=1`, lock `etsoc-shire1` (`lib.sh:22-28, 181-186`; the lock at `:183-185`). Abort on a CI job
(`lib.sh:59-60`).
- **Card 0 must hold no process and no lock holder** at every between-launch check. `others_present` with `et-holders`
  covers this (`lib.sh:70-78`).
- The card-0 guard runs throughout (§7).
- Queue entries are ≤ 25 min, at least 15 min apart (D:384; `idle/block.sh:216`), on ≥ 2 sessions at least 4 h apart.

**V0, the card-1 calibration rule** (`C §3.8`; a non-registered workload, fixed now):
- For S_L: run `ALL24` CAL chains from edge E, starting at E = aifoundry3's frozen S_L, 3 chains per edge.
  - `T_cal` is aifoundry3's median CAL `t66` at its frozen S_L, from R3.
  - If card 1's median is < 0.5 × `T_cal`, lower E by 1 (not below 58).
  - If it is > 2 × `T_cal` or any chain is censored, raise E by 1 (not above 62).
  - At most 3 edges.
  - S_L8 is set the same way, with the L8 frozen offset (S_L8 − S_L from aifoundry3) kept.
- `CV_card1` for §2.4 comes from these chains.
- Card 1 heats 1.6–1.7× faster (§5.1), so its `t66` will be shorter than aifoundry3's at any allowed edge. Only the
  signs are compared across cards, never the magnitudes.

**Blocks:** the kept types, n_val each (§2.4), queued in priority order L16 > L8 > S > G8, interleaved across sessions.

Per-block estimates on card 1 [inference, ic:10-12]:

| Block | Per run | Block total |
|---|---|---|
| L16 | ≈ 1.7 min | ≈ 7 min |
| L8 | ≈ 2.0 min | ≈ 14 min |
| S | ≈ 1.2 min | ≈ 10 min |
| G8 | ≈ 2.0 min | ≈ 10 min |

### 6.2 aifoundry2 (the Q1 items, today)

This is §3.5 in full. Its items are frozen in PREREG-A2 before the session. It is aifoundry2's only validation session.

### 6.3 Pre-registration files and the hash lock (as D:394-402)

**`PREREG.md` and `prereg.json`**, written after P3, hold:
- every item of §4.1 and §3.3–3.4 for card 1, with its placements, block type, prediction type, band and rule, chosen
  by §2.4, or marked "reported, not tested" with the reason (direction, or power with the projected h);
- the frozen parameters per card: S_L, S_L8, targets, the chain cap, κ gate, void limits, β, the primary contrast,
  n_val, seeds (block seed = 1000 × card index + pass), and the Williams sequence assignment;
- aifoundry3's values per item with 99% CIs, marked REPORTED;
- the probe classes of all three cards;
- the family size;
- the sha256 of `hp/block.sh`, `hp/hplib.py`, `hp/reduce.py`, `hp/sptrace_events.py`, `hp/placements.json` and
  `hp/ettelem-hp/ettelem.cpp`.

**The lock.**
- `params-val-aifoundry1-c1.json` carries PREREG.md's sha256.
- `block.sh` with `HP_ROUND=val` **refuses to start** if PREREG.md or any hashed file differs.
- PREREG-A2 works the same way for `HP_ROUND=a2`.
- The proposed home is `W/docs/reports/data/2026-09-2x-heatplace/`. Committing is the owner's call; the hashes work
  either way.

### 6.4 No iteration after validation starts

Once the first validation block on a card starts:
- code, parameters and the item list stay as hashed;
- no placement, band, edge or card is added, dropped or re-chosen;
- no validation run is repeated except under §4.4's void rules.

A reducer bug found later is fixed as a written amendment before re-running the reducer, and both outcomes are shown
(`W/AGENT.md:249-253`; `V3/AMENDMENTS.md`). aifoundry3's development rounds never touch `hp/a2/` or the A2 items.

### 6.5 From items to the owner's questions

**Q1:**
- "The governor compares the mean of the 34 shire sensors (source, cited)."
- Then, per card: the probe class, and TRIG-A and TRIG-B outcomes where registered.
- Otherwise: "no on-card test was possible on <card> because <latched / off / resting at R °C>".

**Q2:**
- "Edges against the interior, same 512 minions, same work: X% (99% CI) longer to the trip on card 1 (Y% on
  aifoundry3, development)."
- Then PLACE-κ in watts, PLACE8-t at half power, MEM and EDGE, and GRAD with the gradient-corrected PLACE.
- CONC as the counterfactual: "a one-sensor governor would fire Z s earlier for the concentrated placement".
- DVFS-PLACE (exploratory), MAP, and POWER and WORK as preconditions.

**Theories survived:**

| Theory | Survived if |
|---|---|
| H1 | TRIG-A and TRIG-B PASS wherever registered; "not tested on-card" if registered nowhere |
| H1′ | the same items FAIL |
| H2 / H3 / H4 | PLACE-t registered `SIGN+` / `SIGN−` / `EQUIV`, and it PASSes |
| H3′ (gradient) | GRAD-EW or GRAD-NS registered `NONZERO` PASSes |
| H6 | LIN PASSes |
| H7 | CONC |
| H8 / H9 | MEM / EDGE |
| H10 | MAP |
| H11 | every registered `SIGN` item PASSes; not tested if none is registered |
| H12 | reported only |

---

## 7. Safety stops (enforced in `block.sh`, from the live sampler)

**Owner's absolute rule.**
- The die never exceeds 90 °C. Any sample with the windowed high ≥ 90, or the mean ≥ 90, **aborts the block and ends
  the session**.
- The script's operating caps make this unreachable in practice. The protocol needs about 68–70 °C at most.

**Run caps.** Stop launching and end the run if, for 2 consecutive samples:
- the mean reads ≥ 80; or
- the windowed high reads ≥ 85; or
- `board_w` reads ≥ 73 W.

These are the E12 and V3-IDLE precedents (`03-experiments.md:249-252`; `idle/block.sh:13-15`). The firmware gives no
protection above its floor (dfo:4, dfo:29).

**Preheat.** It stops at its target, at 30 bursts, or at 80 °C.

**Card-0 guard** (aifoundry1; owner decision):
- **Reading.** Card 0 is read by a read-only guard sampler, `ET_DEVICES=0 ettelem sample --every-ms 1000`, with no
  `--reset-ms`. It starts at block begin and stops with SIGTERM at block end. It is the only access to card 0: no
  launch, no lock, no configuration change.
- **Gate.** A card-1 block starts only if card 0's mean reads ≤ 85 °C.
- **Stop.** Card 1's work stops at once if:
  - any guard sample reads a card-0 mean > 90 °C; or
  - the guard's output is stale for > 10 s.

  On a stop: end the run, launch nothing more, `block_end fail`, end the session. Card 0 is not touched.
- **Secondary proxy** (`C §3.8b`): stop if card 1's `W_idle` at the edge rises by more than 2 W from the session's first
  block.
- **Alternative.** If the owner prefers not to hold card 0's management node, the guard becomes a 1 s read before every
  run and every 30 s during edge waits. Chains stay ≤ 150 s, and on card 1 they are about 40 s.
- **Drains.** A drain of card 1's queue (`dev_mngt_service` opens every card: `lib.sh:128-146`) first stops the guard,
  then restarts it. A guard that cannot restart stops the block.

**Abort the block** (V3 exit codes, `idle/block.sh:134-143`):
- 3 consecutive heater exits ≠ 0 (exit 1);
- another user, a foreign device process, a CI job, a holder on card 0, or a rise in the `et_soc1` use count (exit 3;
  the card is left at once);
- the sampler stale for > 3 s (exit 1).

**What is never done.** No TDP, threshold, clock, reset, firmware or driver change (`W/AGENT.md` §5). The only SP state
change is the log level, where §3.2 allows it.

---

## 8. Card-time budget per phase

The estimates come from §5.1, §5.2 and §6.1 [inference]. Wall-clock is 3–8 times card time
(`14-card-behaviour.md:131-132`).

| Phase | Card | Content | Card time (est.) | Cap |
|---|---|---|---|---|
| A2, today | aifoundry2 | gate; probe (0.3 min); smoke (0.5 min); COOL or COOL−: ≤ 2 A2 blocks of warm-up + 8 runs (≈ 11 min each); MARGINAL: 1 block; WARM: 1 documentation run (0.3 min) plus ≤ 3 one-second re-checks | WARM ≈ 1 min; COOL ≈ 12–24 min | 30 min |
| R0 | aifoundry3 | dry runs (0); probe; smoke | ≈ 2 min | 5 min |
| R0 | card 1 | dry runs; guard start test; probe; smoke | ≈ 3 min | 5 min |
| G0 | none | Foster fit of V3-IDLE curves | 0 | — |
| R1 | aifoundry3 | R1a (0–5), R1b (25), R1c: 3 S + 3 L16 (80) | ≈ 105–110 min | 120 min |
| P1 | none | power step 1 | 0 | — |
| R2 | aifoundry3 | 3 L8 + 3 G8, or 3 more L16 | ≈ 36–117 min | 130 min |
| R3 | aifoundry3 | 3 blocks per kept type | ≈ 36–195 min | 210 min |
| P3 | none | registration, PREREG hash | 0 | — |
| V0 | card 1 | CAL chains for S_L and S_L8 (≤ 18 chains) | ≈ 20 min | 30 min |
| V | card 1 | L16 × n (7 min each), L8 × n (14), S × n (10), G8 × n (10); n = 5–12 by §2.4 | ≈ 85–300 min (L16 + S only: 85–144) | 300 min |
| **Totals** | | aifoundry3 ≈ 3.7–7.1 h; card 1 ≈ 1.8–5.4 h; aifoundry2 ≤ 0.5 h today | | 8 h / 5.5 h / 0.5 h |

**If a cap binds,** block types are dropped in reverse priority: G8 first, then S, then L8. L16 is never dropped. A
dropped type's items are reported, not tested.

---

## 9. Code to write (the V3 framework, `W/AGENT.md:221-253`; new directory `W/tools/claims-v3/hp/`)

| File | What |
|---|---|
| `hp/block.sh <pass> [--smoke]` | One block (`HP_ROUND=r1\|r2\|r3\|val`, `HP_TYPE=S\|L16\|L8\|G8\|CAL`). It sources `../lib.sh` and reuses `idle/block.sh`'s intrusion machinery (`:68-143`). It runs the between-launch checks of O1, burn-in CAL, Williams order, edge wait with `τ_c`, the chain rule, safety stops, the card-0 guard (with `V3_DEVICE=1`), and the log level only where §3.2 allows. In `val` it refuses on a hash mismatch |
| `hp/probe.sh` | §3.2 steps 1–4 and the classification into `probe.json`. It never changes state |
| `hp/a2/block.sh`, `hp/a2/reduce_a2.py`, `hp/a2/params-a2.json` | §3.5, frozen by PREREG-A2 |
| `hp/hplib.py` | params, Williams sequences, PREREG hash check, the live stop tests, post-run checks |
| `hp/placements.json` | written by `hp/placements.py`, a copy of `design2_sets.py` with its asserts |
| `hp/sptrace_events.py` | governor lines with timestamps (imports `ring_entries` from `W/tools/ettelem/parse_sptrace_voltage.py`), ring-overlap check, level inference, SP-tick fit. `--self-test`: 26 down and 27 idle lines in `W/docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin` |
| `hp/reduce.py` | observables (§2.1), contrasts (§2.2), the κ fit with `flip_thermal_model.py`'s `nnls` and `lowpass` unchanged, P1, P3, items, `card_verdicts`. `--check-pass`, `--dev`, `--prereg` |
| `hp/ettelem-hp/` | a **copy** of `W/tools/ettelem/ettelem.cpp`: `loglevel critical\|error\|warning\|info\|debug` → 0–4 (`ETP/et-trace/include/et-trace/encoder.h:208-214`; today anything but `debug` maps to INFO: `ettelem.cpp:201`). Built into `build/ettelem-hp/` on each host with `nice -j4`; `build/ettelem/` and the campaign's sources are left untouched (`W/AGENT.md` §7) |
| `hp/README.md` | rules and departures, written before any data (the `gs/README.md` pattern) |
| `schedule-hp-*.txt` | `queue.sh` schedules |

**Deployment.**
- Files are copied into the tree that `lib.sh` runs from on each host: `~/nekko` on aifoundry1 and aifoundry3, and on
  aifoundry2 the checkout its V3 queue used.
- Never over a running script, and never into a build directory another queue uses.
- Every script is run with `V3_DRY=1`, then `--smoke`, then for real.

---

## 10. Risks, and what the host cannot answer

1. **Q1 on-card may be empty.** The expected probes are SILENT, SILENT and LOOP. Whether aifoundry2 is cool today
   decides it. The report must then say "source only" plainly.
2. **Power.** The primary Tier L contrast may need 8–12 blocks to reach ±δ (`C §2.2`). The power step makes the
   registered list honest rather than long. The Q2 number (X%, 99% CI) is reported whatever is registered.
3. **Regime dependence** (`C §3.7`). Card 1 heats 1.6–1.7× faster and cools about 2× faster, so its Tier L sits in a
   different part of its network. Only signs transfer, and H11 rests on signs.
4. **Heatsink history and airflow.** Mitigated by burn-in CAL, Williams orders, `τ_c` and the void rules. Not
   eliminated.
5. **Sensor offsets and truncation.** Uncalibrated sensors (`firmware.md:87-93`) affect CONC (handled by its form)
   and Tier S `t66` (§4.4).
6. **The inferred die frame.** MAP checks it partly. GRAD labels are the drawing's.
7. **Card 0.** Its idle temperature is unknown. If it idles above 85 °C, the gate stops card 1's validation and the Q2
   items end INSUFFICIENT.
8. **Other users.** aifoundry3's demo service can launch without the lock (`14-card-behaviour.md:274-276`). CI runs on
   aifoundry1 and aifoundry2 (`lib.sh:59-60`). The `--reset-ms` resets change the shared min/max (`V3/PLAN3.md:856`).
9. **Host observables cannot answer** (D:577-595, unchanged):
   - where the heat is (M1 against M2);
   - long horizons beyond 150 s;
   - the PMIC trip;
   - other clocks and patterns.

---

## 11. Critique points rejected, or adopted only in modified form

| # | Critique point | Decision and reason |
|---|---|---|
| **R1** | `C §3.2` / fix 10: alternate the start edge by block (S ∈ {63, 64}; {59, 60}) to dither the whole-degree truncation | **Rejected.** The edge method pins the start to the same integer-mean crossing. A 1 °C shift of an unchanged profile leaves every sensor's fractional part unchanged, so it does not dither; only profile-shape changes would, weakly. In Tier S it also doubles the required rise (+1.03 → +2.03 °C), which makes a different tier. Mitigation: Tier L primary (bias about 5× smaller relative) and the bias stated (§4.4) |
| **R2** | `C §3.3` / fix 5: a UNI32 hi-half variant via `enercat_host --minions 0xffff0000`, averaged with the lo half, for SPREAD-t | **Rejected.** enercat runs a different instruction mix, not TensorFMA, so it is not the same work. A heater change (`--minion-base`) would touch host and kernel for an item that the corrected identity already decomposes: SPREAD = ½·PLACE + the intra-tile term (§4.6). SPREAD is reported, not registered |
| **R3** | `C §3.5` / fix 9: the antisymmetric pairs W12/E12 (`0x03076616`/`0x747090e0`) and N12/S12 (`0x31313232`/`0x4646c4c4`) | **Adopted in modified form.** The masks are correct (reproduced here). But E12 and N12 hold both tiles beside the unsensed I/O-PCIe cells, and E12 both M/S-adjacent tiles, so the sensor-coverage mechanism (M2) alone predicts nonzero contrasts. Replaced by the balanced mirror pairs W8b/E8b and N8b/S8b (§4.2) |
| **R4** | `C §3.5`: bracket every block with the same reference run (UNI32 first and last) and void on their difference | **Rejected as specified.** It adds 30–100% to an L16 block. Replaced by the burn-in CAL record (between-block drift) and a void rule on free per-run measures of heat removal at the edge (`τ_c`, `W_idle`) (§4.4) |
| **R5** | `C §2.2(iv)`: let the owner set δ to 20% | **Not adopted as a design change.** δ stays ln 1.10, fixed before data. The owner may still choose 20% before R1 starts, never after development data exist |
| **R6** | `C §3.9`: ≥ 3 B4 repeats per block for MAP | **Modified:** 2 repeats of each, plus the I/O sensor's own peak-hold statistic `ι_io`. MAP qualifies geometry labels rather than answering Q1 or Q2, and P1 decides whether it can be registered at all |
| **R7** | `C §2.4`: κ gate at ≥ 95% floor-match | **Modified:** 90%, adjustable in development within 85–97% (no data yet show what a correct model scores at a 224 ms pass with sampler phase jitter) |
| **R8** | `C §1.4`: ask for O2 only if the probe shows (a) | **Superseded** by the owner's O2. Kept in effect: the level is changed only on cards the probe classes ALIVE (or for the aifoundry3 one-shot) |
| **R9** | `C §3.8(a)`: a 1 s card-0 reading at the start and end of each card-1 session | **Superseded** by the owner's stricter guard (§7). `C §3.8(b)` is kept as a secondary proxy |
| **R10** | `C §4` O1 discussion (PLAN3 against V3-IDLE) | **Moot:** the owner decided O1 |
| **R11** | `C §3.5`'s statement that the symmetric groups cancel a linear gradient in every one of their contrasts | **Corrected, not a fix:** PER16's and EDGE8's centroids are offset (+0.31 and +0.63 rows south, −0.31 and −0.63 columns west), so a gradient leaks partly. This is used to report a gradient-corrected PLACE-t (§4.2) |
| **R12** | `C §3.8`: card 1 "heats about 4–6× faster" (from D:379, dfo:18 against dfo:14-16), used to argue for a card-1 calibration | **Figure corrected, fix kept:** to the same rise, card 1 heats 1.6–1.7× faster (§5.1). The calibration V0 is kept anyway, because the networks differ (§6.1) |

Every other fix of `C §5` (1–4, 6–8, 11–14) and every point in `C §1`–`§4` not listed here was adopted as §1's table
states.
