# E77 — the regulators' conversion loss, at two rail voltages (PLAN ONLY, NOT RUN)

Written Tue 27 Oct 2026 (week 44) as part of Q129's rail ledger; the design corrected the same day after
verification found the arms were not actually matched (see "Corrected" at the foot). **Nothing here was run.**
E77 is the number reserved for it; this file is the plan a later session would pre-register, freeze and execute.

## The one term the existing data cannot separate

The rail ledger (`README.md`) measures the board-to-rail step rail by rail. On its central footing the step is
**1.01 pJ of a 5.783 pJ multiply-add**, and the published attribution puts **0.88 pJ** of it on "the regulators'
delivery loss plus whatever unmetered logic works in step with the rail", as one coefficient per rail
(0.188 × minion W on aifoundry2). The 0.14 pJ left over is that fit's **residual**, consistent with zero and
largely explained by the measurement window's own heating — so the quantity E77 goes after is not a leftover
energy but **the 0.88 pJ itself, which is two different things added together**. Nothing in the repository
splits that coefficient, and two cards' data say it cannot be split from load alone:

* adding a square term in the rails' watts to the catalogue's 375 non-DRAM configuration means is not resolvable
  (aifoundry2 −0.00055 ± 0.00035 per W², aifoundry3 +0.00059 ± 0.00032 — **opposite signs on the same firmware**,
  rms better by 0.001 W), and a regulator's conduction loss is exactly what a square term would be;
* the management struct `DM_CMD_GET_SP_STATS` carries each regulator's **output** power and voltage and the
  board's **input** power, and no per-regulator input-side power at all, so the conversion loss is never read
  directly. The PMIC measures both sides over PMBus (`docs/findings/19-observability-and-the-unmetered.md`, "The
  meter chain": 84 numbers), but reaching them means PMIC commands, which this workflow forbids outright.

## The lever: the same rail watts at two rail voltages

A switching regulator's loss at its output power P splits into a conduction part and the rest:

    loss(P, V) = R_eff (P / V)^2 + (loss that does not depend on the current)

Off-rail logic that works in step with the rail does **not** carry the 1/V² — it is logic, its power scales with
its own supply and activity. So the two terms separate if the **same minion-rail watts** can be delivered at two
different minion-rail voltages. On these cards the governor sets both clock and voltage together, and this
ledger's own E38 runs read **516 mV at 600 MHz** on aifoundry2 against **617–619 mV at 800 MHz** in E64's
stretches: a 19.8% voltage step, so at matched watts the current is 19.8% lower in arm B and

    arm A's conduction loss exceeds arm B's by (618/516)^2 - 1 = 43.4%

A 43% change in the conduction term is far above the measurement's noise — the off-rail remainder of a 20 W rail
load reads to about 0.27 W rms over configuration means. **The rail voltage is read per rung and per sample**
(`sp.minion_mv`), not assumed: it drifts 516–522 mV at the floor, and the fit uses the measured value.

## Matching the arms: the hart count, on a measured 600 MHz rail law

The workload, not the governor, closes the match: **at 800 MHz, fewer harts** deliver the same rail watts that
more harts at 600 MHz deliver. The law this ledger measures, on the card E77 runs on, at the clock arm A runs
at, on the rail that is being matched (`rail-ledger.json`, `hart_law_600mhz`):

| | measured | from |
|---|---|---|
| **aifoundry2, minion rail, 600 MHz** | **−0.446 W + 22.31 mW per hart** | 1,024 / 512 / 256 harts (fp32_randn, randn_16, randn_8), launch window |
| aifoundry3, minion rail, 600 MHz | −0.234 W + 21.91 mW per hart | the same three rungs on the other card |
| aifoundry2, board, 600 MHz | −1.332 W + 30.03 mW per hart | the same rungs |

Three things about it matter for the design. **The offset is within half a watt of zero**, on both cards and on
both the rail and the board — which is E65's reading (−0.51 ± 0.03 W + 27.1 mW/hart at the board, idle-bracketed,
64–1,024 harts) and **not** E62-CAL's 5.80 ± 0.30 W. E65 refuted that offset explicitly ("the slope lands and
the offset does not", `docs/findings/05-claims.md` line 915): it belonged to E62's baseline, one pre-session idle
at a 49 °C die. The first version of this plan cited E62-CAL's **5.80 W + 55.8 mW/hart**, which is **board**
watts at **800 MHz** — the wrong quantity, the wrong clock, and a refuted offset — while its own rung table was
linear through zero. The table was right and the text was wrong; both now rest on the measured law above.

**The transfer to 800 MHz is a prediction, and E62-CAL is the check on it.** Scaling the measured 600 MHz law by
f·V² = (800/600) × (618/516)² = **1.913 per hart** predicts **57.4 mW/hart at the board at 800 MHz**; E62-CAL
measured **55.8 ± 1.0** on this card. The transfer lands at the board, which is what licenses the same transfer
on the minion rail: **42.7 mW/hart at 800 MHz**, and therefore **arm B needs 0.523 × arm A's harts** for the
same rail watts — not the 0.75 the first version used, which was the clock ratio alone and left the arms
mismatched by about 1.4×.

## Design (20 card-minutes, aifoundry2 card 0)

**Why aifoundry2:** it is the only card whose governor can be moved at all (aifoundry3 is latched at boot-time
TDP 0, aifoundry1's card 1 never reaches 800 MHz), and its idle leakage slope is the one that is measured
(E66, 0.294 W/°C over 51–58 °C).

**The two clocks, without ever setting a frequency.** `DM_CMD_SET_FREQUENCY` is forbidden. The 600 MHz arm is
reached the way aifoundry3 reaches it: the static TDP level at 0, which latches the clock at the floor under
load. The 800 MHz arm is the card's own free behaviour below 65 °C. Both are governor moves, so the whole of
the field manual applies — see "Gates" below. **If the TDP-0 latch cannot be established as not writing flash in
the exact running build, E77 does not run.** There is a fallback that needs no governor move at all: the 600 MHz
arm can instead be taken from a **hot** launch, where the governor itself drops the card to the 600 MHz floor
under random data (E64's SUS-02 held 600 MHz for 57 s) — slower to set up, and the die is 5–8 °C hotter, which
is a covariate, not a confound, because the leakage slope is measured.

**The ladder.** The `hp`/`hl` heater at per-shire hart counts (32 harts to a shire, so every rung is a multiple
of 32), every launch 4 s, the statistic the median of the 10 Hz board samples and the **raw** rail readings over
[t1−1.5, t1]. Six seconds of a 4 s run is not available, so the settling correction is measured in the same
block by running one rung for 12 s and comparing.

| rung | arm A: 600 MHz, ~516 mV | predicted minion W | arm B: 800 MHz, ~618 mV | predicted minion W | mismatch |
|---|---|---|---|---|---|
| 1 | **1,024** harts (32/shire) | 22.40 | **544** harts (17/shire) | 22.36 | **−0.2%** |
| 2 | **768** (24/shire) | 16.69 | **416** (13/shire) | 16.90 | **+1.3%** |
| 3 | **544** (17/shire) | 11.69 | **288** (9/shire) | 11.44 | **−2.2%** |
| 4 | **288** (9/shire) | 5.98 | **160** (5/shire) | 5.98 | **−0.1%** |

Every pair is matched to within 2.2% on predicted minion-rail watts, against the 1.4× mismatch the first version
would have run. **544 and 288 harts appear in both arms**, which gives the ladder a free internal check: the
same hart count at the two clocks must show the rail-watt ratio 1.91 that the f·V² transfer predicts, and if it
does not, the matching itself is wrong and that is reported before anything else.

Four matched rail-power rungs × two arms × 3 passes × 4 s = **96 launches, 6.4 card-minutes of launch time**;
with the strict start's approach (1–10 s below 65 °C since the October cooling, E60's amendment A2) and the
governor set/restore/read-back, **under 20 card-minutes** and about 35 minutes of wall clock.

**The pattern is held fixed across both arms** (`fp32 randn`, the Horace pattern) so that off-rail logic activity
per hart is the same; only the hart count changes, and 160 harts is already inside the quiet operating region at
800 MHz (E62: every 12-shire swap held 800 MHz at ~43 W board), so the governor should not intervene in arm B.
Each rung records `mhz.minion` every sample and any rung with a clock that moves is dropped, not corrected.

## The pre-registered reading

For each arm, per rung: `offrail = board − (minion + SRAM + NoC)`, all as deltas over that rung's own pre-launch
idle, with the S2 settling screen of this ledger (the idle bracket's minion rail steady within 0.15 W between
[t0−5, t0−3] and [t0−2, t0−0.3]) and the S3 dropout rule on every board window. **On the ledger's central
footing**: the registered leakage correction `leak × (t_window − t_launch)` is taken off the board and
distributed over the rows by the drift slopes measured in that same block, and the uncorrected footing is
published beside it, exactly as the ledger now does. Then one fit over both arms:

    offrail = a_m · minion + a_s · SRAM + a_n · NoC + R_eff · (minion / V_minion)^2

The fit does **not** require exactly matched rungs — it requires the two voltage arms to **cover the same range
of minion watts**, which the ladder above does by construction. The matching carries the descriptive check, not
the fit.

* **PASS (the term exists):** `R_eff` differs from 0 with 99% confidence over passes, and the fit's rms is at
  least 30% below the rms of the same fit without it. Report `R_eff` in mΩ and the conduction loss it implies at
  a 21 W minion rail — which is the pJ this moves out of the published 0.88 pJ "delivery loss + in-step logic"
  row and into a named regulator loss.
* **FAIL (it does not):** `R_eff`'s 99% interval contains 0. Then the whole 0.88 pJ is reported as off-rail
  logic in step with the rails, with the conduction loss bounded above by the interval's edge.
  **A FAIL is a result and is reported as one.**
* **Frozen before the first launch:** the predicted matched rail watts per rung from the measured 600 MHz law
  above (22.40 / 16.69 / 11.69 / 5.98 W in arm A; 22.36 / 16.90 / 11.44 / 5.98 in arm B); the rail-watt ratio
  1.91 at 544 and at 288 harts across the arms; and the prediction that **arm A's off-rail watts exceed arm B's
  at matched rail watts by 43.4% of whatever the conduction part is**, computed from the per-rung **measured**
  voltages rather than the nominal ones.
* **The matching is scored, not assumed.** If a pair's measured minion watts differ by more than **5%**, that
  pair is reported as mismatched, the descriptive 43.4% check is reported against the achieved mismatch, and the
  fit carries the verdict. If more than one pair misses 5%, the f·V² transfer is reported as refuted on this
  card and the ladder is re-cut from the measured arm B law before any verdict is read.

A departure that must be named if it happens: if arm B's governor intervenes at 544 harts, drop to 416 as the
top rung and say so; the match then tops out near 17 W.

## Gates (binding, from the field manual)

Any governor move in E77 follows the ET-SoC-1 firmware rebuild / OTA field manual (kept with the operator's own
notes, not in this repository): its `AGENTS.md` in full, then `docs/hosts-and-recovery.md`, `docs/runbook.md` and
`templates/change-record.md`. A change record with PASS / FAIL / **UNKNOWN** per gate (UNKNOWN is not PASS) is
filled from that template and committed with the data.
In short, and none of it optional:

1. **G0 identity, read fresh:** host, PCI BDF, `/dev/etN`, card identity, firmware/BL2/PMIC versions, module hash.
2. **Exclusive window:** the `#community-lab` claim, the card lock (`flock -n /run/lock/etsoc-shire<N>.lock`),
   `et-who` empty, and **no telemetry client holding the single-open management node** — the dashboard collector
   on aifoundry2 is paused or avoided deliberately, never killed.
3. **Rule 8, no incidental board-data change:** before any set, read the firmware source of the **exact running
   build** and show that `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` writes no flash or configuration data in it
   (`05-claims.md` records a BL2 build where a NoC voltage set did). If that cannot be established: **NO-GO**.
4. **Original values read and recorded first** (`ettelem config`: TDP, `sw_temperature_c`, power state), restored
   after the last run, read back, and the governor shown to step normally afterwards.
5. **Bounds:** TDP ≤ 75 W; abort if the die reads ≥ 72 °C or board power ≥ 85 W. Lowering the TDP to 0 is the
   safe direction, which is the whole of what E77 needs.
6. **Never:** a card reset, a frequency set, PCIe retrain, a driver reload, OTA, flashing, or a PMIC command.
   If a restore fails or the card stops answering: stop, keep the claim, write it up, alert.

Pre-registration (this file plus the frozen predictions) is committed and pushed **before the first launch**.

## Corrected, 27 Oct 2026

Two faults in the first version of this plan, both found by verification before any card time was spent:

1. **The arms were not matched.** Arm B was arm A × 0.75 throughout (the clock ratio alone), which ignores the
   V² half of its own lever. The true per-hart rail-watt ratio is f·V² = **1.91**, so arm B needs **0.523 ×**
   arm A's harts; as written, arm B's top rung would have delivered ~31 W against arm A's ~22 W and the frozen
   42% prediction would have been scored on unmatched rungs. The ladder is rebuilt above, matched to ≤ 2.2%.
2. **The matching law was the wrong law.** E62-CAL's 5.80 W + 55.8 mW/hart is **board** watts at **800 MHz**,
   and E65 refuted its offset. Replaced by this ledger's measured 600 MHz **minion-rail** law on aifoundry2,
   with E62-CAL kept only as an independent check on the f·V² transfer, which it passes (57.4 predicted against
   55.8 ± 1.0 measured).

Also updated: the 42% conduction prediction becomes **43.4%** on the measured 516/618 mV rather than nominal
519/618; the "0.26 pJ unattributed" framing is replaced by the corrected ledger's 0.88 pJ fit coefficient, which
is the quantity E77 actually splits; and the matching is now scored against a pre-registered 5% tolerance
instead of being assumed.
