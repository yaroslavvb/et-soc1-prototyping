# PREREG-DEV: DV2 development on aifoundry2 (what development fixes, how it decides, tonight's runs)

Written 27 Sep 2026, about 23:55 PDT, before any DV2 card work, alongside `DESIGN.md` revision 2 (`D`).

**What this file does.** It fixes in advance what development may decide, and by which rule. The development card's
data then choose among stated candidates by stated rules, not by judgement after the fact.

**What it is not.** It is not the replication pre-registration. `PREREG-DV2.md` is written at the freeze (§6). No
development run counts toward replication.

---

## 0. Rules

- **The method** (the owner's). All iteration happens on the development card, aifoundry2, the only free governor. The
  test is then frozen and not iterated.
  - For governor items the test is a **replication on aifoundry2** in later sessions, if the owner accepts it (D §4.3a).
  - Heat-only placement across cards is HP's claim, not DV2's.
- **Logging.** Every decision below is taken by its rule and logged in
  `W/build/claims-v3/aifoundry2/dv2/dev-log.jsonl` with the data it used.
  - Anything this file does not list stays as `DESIGN.md` says.
  - Changing anything else is a **DEVIATION**: logged with a reason, and named on the pages.
- **Card rules** (the owner's; enforced by lib.sh, hplib and the dv2 scripts):
  - `et-who`, `who` and the process scan before the session, before every run and between launches;
  - the card lock held throughout;
  - every device process ≤ 10 s; chains ≤ 150 s with telemetry running;
  - stop at 90 °C;
  - no reset; no global-state change except those in D §4.2, each restored and verified;
  - never aifoundry1 card 0; nothing on aifoundry1 tonight;
  - tools are stopped with a plain kill;
  - code-only agents test with `V3_DRY=1`.
- **The threshold.** It is not changed tonight unless the owner answers D §4.3 with a yes. An agent message is not that
  yes.

---

## 1. Fixed now (development does not change these)

### 1.1 Definitions

- **Branches.** The table in D §4.1: NAT-4 (R0 ≤ 60, S 62), NAT-3 (61, S 63), NAT-2 (62, S 64), NAT-1 (63-64, S 65),
  D1 (62-68, owner's yes: thr* = R0 + 5 ≤ 73, K = R0 + 6, S = R0 + 2), LOOP (≥ 66), WARM.
  - The R0 probe must say ALIVE before any NAT branch runs.
- **Run kinds** (D §5.1-5.4): T (one launch, one statistics reset at S + 1, the stop file 2.0 s after the first 700
  sample, a 10 s tail), ADD, P (D1 only), C1m.
- **Order.** The T-block cycle of D §5.5 and C1m's four rows (D §5.4).
- **Per-run observables** (A2's TRIG-A, reused): t_up, t_m, t_spm, t_hi, t_hi2, t_down (one-point 800 → 700 only),
  with the high and the SP max taken since the run's one reset.
  - A run is separating if (a) t_m − t_hi ≥ 1.5 s, or (b) the high reads ≥ K + 1 at t_up and the clock holds 800 for
    ≥ 0.5 s.
  - It fits H-mean if t_down ∈ [t_m − 0.3, t_m + 0.6] s; it fits H-max if t_down ∈ [t_hi − 0.3, t_hi + 0.6] s.
- **Void rules.**
  - The heater's rc ≠ 0.
  - A safety stop.
  - A sampler gap > 1 s.
  - `since_reset_ms` showing anything but exactly one reset before t0.
  - In C1m, any sample off 600 MHz.
  - An edge not reached within 300 s.
- **Caps** (D §4.4): 90 °C stop; a run ends after 2 samples at mean ≥ 80, high ≥ 85 or board ≥ 73 W.

### 1.2 Source orderings (from TPM; frozen predictions)

| Item | Prediction |
|---|---|
| Z1 (a)-(d) | every EXIT prints X ≤ thr, every ENTER prints X = thr + 1; an EXIT on an idle card is followed by a PIDLE ≤ 0.3 s (SP); no `new OP` with no kernel of ours; THERMAL_DOWN changes only across an EXIT |
| Z2 aifoundry3 | residencies POWER_UP, POWER_DOWN, THERMAL_DOWN and SAFE are all 0 |
| Z2 aifoundry2 | POWER_UP > 0 if the SP booted before 21 Sep 06:46; THERMAL_DOWN unchanged between cycles with no EXIT |
| Z3 (D1) | set at R0 ≥ 66 → an EXIT within 2 s, then a PIDLE; restore at a rest ≥ 66 → an ENTER within 2 s on an idle card |
| G1-X | every ENTER prints X = K |
| G2-E | every EXIT while a kernel runs → a PUP or an ENTER within one pass; never neither |
| G2-X | an EXIT at 700 → OP 700→600, never 700→800 |
| G2-N | no down-step at a host mean ≤ K − 2 |
| G6-B | no PIDLE between the kernel end and the EXIT; a PIDLE ≤ 0.3 s (SP) after the EXIT |
| G7 (c) | after a PDN, no OP above 600 until an ENTER or the kernel end |

### 1.3 Host bands frozen from the retrospective (D §2.2; 275 changes, 21-23 Sep; `retro/`)

| Item | Band | Retrospective value |
|---|---|---|
| G2-C climbs | 700 in ≤ 1 host sample in ≥ 95% of climbs; no 700 sample in ≥ 25% | 85/85; 50/85 |
| G2-D descents | the 700 dwell of 800→700→600 ∈ [0.3, 0.7] s in ≥ 90% | 69/70 at 0.4-0.5 s |
| G2-U up-steps while hunting | the preceding reading ≤ thr + 1 in 100%; ≤ thr in ≥ 80%; never ≥ thr + 2 | 102/102; 91/102; 0 |
| G3-L launch → first 800 | median ∈ [0.4, 1.0] s; all ≤ 2.2 s | E10: median 0.73, 0.14-2.01 (n = 31) |
| G3-I kernel end → 600 with no episode | ∈ [0, 1.6] s | E10: median 1.02, ≤ 1.39 (n = 15) |

### 1.4 Formulas (applied to development inputs at the freeze; no tuning)

- **G4 point.** L_pred = ln((κ_U·P_U + P_x) / (κ_U·P_U + κ_P·P_x)), where:
  - κ_P = e^−L600(PER/INT) and κ_U = e^−L600(UNI/INT), from C1m's block means;
  - P_U is the mean of the development ADD runs;
  - P_x is the mean switching W at 800 MHz of the development INT and PER runs (board W over [t_up + 0.3,
    t_up + 2.3] minus ADD's 800 MHz board W).
- **G4 band.** L_pred ± b, with b = min(0.15, (L600 − L_pred)/2, L_pred/2). If b < 0.05, G4 becomes a sign test
  (D §6).
- **G4 rule.** PASS if the 99% CI lies wholly inside the band. FAIL if it lies wholly outside, on either side.
  INSUFFICIENT otherwise. The verdict is given on L and on L_P.
- **n_val.** The smallest n in [8, 16] with t(0.995, n−1)·SD_dev/√n ≤ b. SD_dev is the SD of per-block L over the
  development blocks run under the final DEV-1 candidate.
- **The prediction never moves to development's own L.** If development's L lies outside the band, D reports "TH5 not
  supported in development", and the replication still tests L_pred.
- **G1-T.** PASS if ≥ 6 separating runs over ≥ 3 blocks, ≥ 80% fit H-mean and ≤ 1 fits H-max. FAIL if ≥ 50% fit
  H-max.
- **G1-X.** PASS if ≥ 5 separating ENTERs, all print K, and the host high is ≥ K + 1 within ±0.5 s in ≥ 90%. FAIL on
  any ENTER printing ≥ K + 1 while the host mean reads ≤ K − 1.
- **G6-M.** a2_heat_sim.py's `run` and `leak`, with the run's measured start reading, load W and duration, give the
  model's t_rec. PASS if ≥ 70% of runs lie within ×2 of the measured EXIT time.

---

## 2. What development decides (each with its candidates, data and rule)

| # | Decision | Candidates (in order) | Data | Rule |
|---|---|---|---|---|
| DEV-1 | G4's minions and start offset (N, K − S) | (128, 4) → (192, 4) → (192, 3) | INT and PER T-runs of development blocks 1-2 of the first session with G4 (NAT-4, NAT-3 or D1) | A run **qualifies** if its trip falls in [t_up + 1.5 s, kernel end − 0.5 s]. Keep the candidate if ≥ 3 of 4 INT/PER runs qualify after block 1, and ≥ 6 of 8 after block 2. Otherwise move once: to the next candidate if the failures are censored (no trip). If the failures are early trips (< 1.5 s), stay at (128, 4) and flag it. At most two moves; the choice is final after block 3. Blocks under an abandoned candidate are reported but not used for SD_dev |
| DEV-2 | launch length | 7 s → 8 s | the wall time of every development heater process (`launches.jsonl`) | 8 s only if every 7 s process took ≤ 8.0 s wall (so an 8 s process stays ≤ 9.0 s under `timeout 10`). Decided after the smoke and block 1 |
| DEV-3 | stop-file delay after the first 700 sample | 2.0 s → 3.0 s | tripped development T-runs | 3.0 s if < 80% show a 600 MHz sample before the stop; otherwise 2.0 s |
| DEV-4 | SP-time bands: P_loop, the loop body, EXIT → OP, the spacing of the two climb OPs, ENTER → first OP, the PUP → PIDLE heartbeat period | — | development rings (T1-parsed) | the median ± 3 MAD, intersected with the source bounds (P_loop ∈ [0.395, 0.50] s SP; heartbeat ∈ [1.00, 1.10] s). ≥ 10 events each, or that sub-item is not registered |
| DEV-5 | registering the SP-line items (G1-X, G2-E/X/N, G3-Q/H, G6-B) | yes / no | development dumps | yes only if WARNING was set (O2 not refused by the owner) **and** ≥ 80% of development T-run dumps hold both the climb OP and the ENTER, with dump overlap shown |
| DEV-6 | G4 inputs κ_P, κ_U, P_U, P_x | — | C1m (4 blocks), ADD (≥ 2 runs), development INT/PER runs | the formulas of §1.4. If C1m has < 3 complete blocks, aifoundry3's dev-r3 values (L600 0.48 and 0.34) are used and G4 is labelled "couplings from aifoundry3" |
| DEV-7 | n_val | 8-16 | SD_dev (≥ 4 blocks under the final DEV-1 candidate) | §1.4 |
| DEV-8 | G1-H hold margin | thr + 2 → thr + 3 | the high − mean over the 3 samples before t0, over all development T-runs | thr + 3 if the 95th percentile ≥ 3 °C. Reported only |
| DEV-9 | G7 go/no-go and the bands for (a) and (b) | go / drop | development P-runs (D1 only) | drop G7 if any P-run reads ≥ 73 W or < 66 W at 800 MHz. Otherwise the bands are the median ± 3 MAD, with ≥ 3 events, else not registered |
| DEV-10 | between-block rest | 5 → 10 min | edge time-outs | 10 min from the next block on if any block has ≥ 2 edge time-outs |
| DEV-11 | the replication branch | D1, NAT-4 or NAT-3 | where the ≥ 4 development blocks ran | the branch that produced them. Bands are thr-relative, so NAT and D1 share items. A branch not developed is not registered |
| DEV-12 | the periodic-reset check (critique C4) | — | 2 UNI32@4 T-runs with `--reset-ms 1000` | reported: "periodic resets change the climb" if either shows 700 held ≥ 2 samples or a climb ending at 700. It does not affect G1 or G4 |

**Reported, not decided.**
- G1's development counts and G1-H's maximum.
- Development L and L_P against L_pred.
- C1m's L600 values against aifoundry3's 0.48 [0.41, 0.55].
- Absolute t800 (the median and its range).
- G6's t_rec.
- The covariates (edge slope, time since heating, W_idle, ambient).

All are labelled "development" wherever they appear.

**Readiness for the freeze** (all required):
- ≥ 4 T-blocks under the final DEV-1 candidate at one branch;
- C1m with ≥ 3 complete blocks (or the DEV-6 fallback, labelled);
- ≥ 2 ADD runs;
- T1 verified on a real clock-change ring;
- T6 reproducing D §2.2 from the retrospective files.

Until all hold, governor items stay in development, and further development sessions follow this file unchanged.

---

## 3. Development output

`reduce_dv2.py --dev` writes `W/build/claims-v3/aifoundry2/dv2/dv2-dev.json`, containing:
- each item as OBSERVABLE or NOT OBSERVABLE;
- the development estimates;
- DEV-1 to DEV-12 with the data each used;
- the global-state tables of every session;
- every DEVIATION.

`prereg_dv2.py` reads only this file and D to write PREREG-DV2 (§6).

---

## 4. Tonight's run list (27-28 Sep, PDT)

**Data root:** `W/build/claims-v3/aifoundry2/dv2/`, and for aifoundry3 `~/nekko/build/claims-v3/aifoundry3/dv2/`.

**Code:** `W/tools/claims-v3/dv2/`, which is `/home/yaroslavvb/claude/et-soc1-heat`, branch heat-placement, on
aifoundry2.

**Start rule.** Every card step starts detached (`setsid nohup … < /dev/null &`), and only after its tools passed their
`V3_DRY=1` tests (D §9).

| # | Window | Card | Condition | Runs | Card time |
|---|---|---|---|---|---|
| 0 | now to about 00:30 | none | — | Build T2 (`build/ettelem-dv2/`) and T5; their V3_DRY tests | 0 |
| 1 | about 00:30, once | **aifoundry3** | R3 finished; `et-who`/`who` clear; `flock -n` on its card lock | **Z2-a3**, in order, each under `timeout 10`: `ettelem-dv2 uptime`; `ettelem-dv2 residency` (states 2, 3, 4, 5, 6); `ettelem config`; `ettelem sptrace`. No launch, no sampler, no set. Only `tools/claims-v3/dv2/` is copied to `~/nekko` and `ettelem-dv2` built there; `hp/` and `lib.sh` there are untouched | about 1 min |
| 2 | about 00:40 to 08:00, every 10 min | **aifoundry2** | each cycle: gate, `flock -n` (skip if held) | **Z1**: `sptrace` → `residency` + `uptime` → `config` (threshold check) → a 1 s `sample --reset-ms 1000`. Host `sensors -j` every 60 s. About 44 cycles. The NAT auto-start flag stays off until run 3 is done | ≤ 5 s per cycle (about 4 min in total) |
| 3 | 00:30-02:30 | none | — | T4 (the session script): V3_DRY at HP_DRY_REST 60, 61, 62, 64, 66, 70; the latch simulation (must end in ABORT-LATCH); the per-run gate with a fake foreign user. Then the NAT auto-start flag goes on. T3 as well, but only if the owner has answered D §4.3 with yes | 0 |
| 4 | about 02:30-02:35 | aifoundry2 | the gate; lock | **Smoke**: R0 (1 s); `sptrace`; Z2; `config`; one 2 s UNI32@4 launch inside the sampler with the one-shot reset; `sptrace`; the parser on the result; the global-state table | about 1 min |
| 5 | about 02:35-03:40 | aifoundry2 | **LOOP** (R0 ≥ 66), and no Z1 reading ≤ 64 in the previous 60 min; else skip to 6 | **C1m development, 12 runs**: block 1 INT16@32, PER16@32, UNI32@16; block 2 UNI, PER, INT; block 3 PER, INT, UNI; block 4 UNI, INT, PER. Each run: the falling E + 1 → E edge (E = R0 + 2, cap 300 s), the one-shot reset at E + 1, up to 3 × 7 s launches until the mean reads E + 4 (censored at the third launch's end), a 10 s tail, `sptrace`, the 600 MHz check. Stop at 65 min of card time, or at a reading ≤ 64 (then 6 may start) | ≤ 65 min |
| 6 | about 03:40 to 07:00 (start by 07:00, end by 08:00); at most one session | aifoundry2 | the auto-start flag on; a Z1 reading ≤ 64; not during 5; gate; R0 ≤ 64; the **probe says ALIVE** (if SILENT: log it, alert, no heat) | **NAT development session**: smoke → WARNING (O2, unless the owner said no) → ADD → T-blocks in the D §5.5 cycle from block 1 (NAT-4/3: the DEV-1 candidates; NAT-2: the same cycle, G4 reported only; NAT-1: blocks of B4C@32, UNI32@4, B4C@32, UNI32@4) → 2 RST runs (DEV-12) if ≥ 10 min remain → ADD → restore the level, verify, Z2, the global-state table. Whole blocks only (a block starts only if its worst case fits). The session ends at 60 min of card time, at 08:00, on two consecutive edge time-outs, on ABORT-LATCH, or on a foreign user | ≤ 60 min |
| 7 | only after the owner's yes; start after T3's dry tests; end by 08:00 | aifoundry2 | 62 ≤ R0 ≤ 68; gate; lock; `pending.json` absent | **D1 development session**: Z3 set (`ettelem-dv2 threshold set R0+5`, watchdog first; no EXIT at R0 ≥ 66 → LATCHED: restore and stop) → probe → smoke → WARNING → ADD → T-blocks (D §5.5; DEV-1 from block 1) → 2 RST runs → ADD → at most 2 P-runs (UNI32@20) if ≥ 25 min remain, with 10 min rests → restore the level → Z3 restore and its ENTER check → verify `temp_threshold_c` = 65 → delete `pending.json` → Z2 → the global-state table. The session cap is 90 min of card time. It replaces 6 if both are possible | ≤ 90 min |
| 8 | all night | **aifoundry1-c1** | — | nothing (HP V0 22:30-23:45, HP validation 00:00-02:00 and 06:00-08:00). Z2-c1 only after 08:00, with the owner's slot and the device-1 guard | 0 |

**Budget.**
- With no cool window and no D1 (the expected case), the total is about 70 min: Z2-a3, Z1, the smoke and C1m.
- With a cool window, up to 60 min more (NAT).
- With the owner's yes, D1 replaces NAT, at up to 90 min.

**The night stops** (no further DV2 card work until the owner replies) on:
- ABORT-LATCH;
- ALERT-THRESHOLD;
- any `failed to set operating point` or `failed to get soc power` line in a dump;
- a 90 °C stop;
- a Z1 threshold reading ≠ 65 with no live D1 session.

---

## 5. After tonight

- `reduce_dv2.py --dev` runs after the last card step (not on aifoundry2 while any session runs).
- If §2's readiness holds, `prereg_dv2.py` writes PREREG-DV2. Otherwise further development sessions follow this file
  unchanged, with more NAT windows or D1.
- Page changes that need no experiment (D §13, including the "lift at 65" correction and RA/RB) go to the page pass
  now. They do not wait for DV2.

---

## 6. What the freeze (PREREG-DV2) contains, and what cannot change after it

**Contents:**
- items G1-T, G1-X (if DEV-5), G2-C/D/U, G2-E/X/N (if DEV-5), G3-L/I, G3-Q/H (if DEV-4/5), G4, G6-M, G6-B (if DEV-5),
  G7 (if DEV-9), Z1, Z2 and Z3 (D1);
- the §1 definitions;
- the DEV-1 to DEV-12 outcomes;
- L_pred, b and n_val;
- the replication branch;
- the session sheet;
- the file and binary hashes (`dv2/*`, `../lib.sh`, `ettelem-dv2/ettelem.cpp`, `build/ettelem/ettelem`,
  `build/ettelem-dv2/ettelem`, the heater and its kernel).

**Rules:**
- `session.sh` refuses a replication pass (9xxx) whose files differ.
- Replication runs over up to 3 pre-booked sessions until n_val blocks are complete. A block with fewer than its 4
  runs is dropped.
- No development run counts.
- Nothing changes between replication sessions.
- The summary reports, per theory TH1-TH8: survived (all its registered items PASS), fell (any FAIL), or untested,
  with the limits stated: one card, one chassis, the branch that ran, and D1's threshold if used.

---

## 7. To relay to the owner (verbatim text in D §4.3)

- **D1** (the threshold raise, with its risks). The default is no.
- **(a)** Replication on aifoundry2 in place of validation on another card, for governor items.
- **(b)** The WARNING level in native sessions under the O2 rule. The default is yes (O2); a no keeps INFO and drops
  the SP-line items.
- **(c)** The Z2 read on aifoundry1-c1 after 08:00.
