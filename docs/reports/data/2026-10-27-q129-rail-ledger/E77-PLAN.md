# E77 — the regulators' conversion loss, at two rail voltages (PLAN ONLY, NOT RUN)

Written Tue 27 Oct 2026 (week 44) as part of Q129's rail ledger. **Nothing here was run.** E77 is the number
reserved for it; this file is the plan a later session would pre-register, freeze and then execute.

## The one term the existing data cannot separate

The rail ledger (`README.md`) measures the board-to-rail step rail by rail and leaves **0.26 pJ of a 5.783 pJ
multiply-add (4.5%) unattributed**, inside an off-rail remainder of 1.19 pJ. The published attribution puts most
of that remainder — 0.86 pJ — on "the regulators' delivery loss plus whatever unmetered logic works in step with
the rail", as one coefficient per rail (0.188 × minion W on aifoundry2). **Nothing in the repository splits that
coefficient into the two things it names**, and two cards' data say it cannot be split from load alone:

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
different minion-rail voltages. On these cards the governor sets both clock and voltage together: **600 MHz at
517–522 mV, 800 MHz at 617–619 mV** (E60, E64), a 19% voltage step and therefore a **42% step in I² at matched
watts**. A 42% change in the conduction term is far above the measurement's noise — the off-rail remainder of a
20 W rail load reads to about 0.27 W rms over configuration means.

The workload, not the governor, closes the match: **at 800 MHz, fewer harts** deliver the same rail watts that
**1,024 harts at 600 MHz** deliver, because rail watts are very nearly linear in harts above the ~5.8 W offset
(E62-CAL: 5.80 ± 0.30 W + 55.8 ± 1.0 mW per hart). So the design is a **matched-rail-power pair** at the two
clocks, with the hart count as the knob.

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

**The ladder.** The `hp`/`hl` heater at per-shire hart counts, every launch 4 s, the statistic the median of the
10 Hz board samples and the **raw** rail readings over [t1−1.5, t1] (6 s of a 4 s run is not available, so the
settling correction is needed: measure it in the same block by running one rung for 12 s and comparing).

| arm | clock | harts | expected minion-rail W |
|---|---|---|---|
| A | 600 MHz, ~519 mV | 1,024 | ~22 (E38's fp32_randn at 600 MHz reads 22.2-22.4 W over idle) |
| A | 600 MHz | 768, 512, 256 | ~17, ~11, ~6 |
| B | 800 MHz, ~618 mV | 768, 576, 384, 192 | ~22, ~17, ~11, ~6 — matched to arm A |

Four matched rail-power rungs × two arms × 3 passes × 4 s = **96 launches, 6.4 card-minutes of launch time**;
with the strict start's approach (1–10 s below 65 °C since the October cooling, E60's amendment A2) and the
governor set/restore/read-back, **under 20 card-minutes** and about 35 minutes of wall clock.

**The pattern is held fixed across both arms** (`fp32 randn`, the Horace pattern) so that off-rail logic activity
per hart is the same; only the hart count changes, and 192 harts is already the quiet operating point at
800 MHz (E62: every 12-shire swap held 800 MHz at ~43 W board), so the governor should not intervene in arm B.
Each rung records `mhz.minion` every sample and any rung with a clock that moves is dropped, not corrected.

## The pre-registered reading

For each arm, per rung: `offrail = board − (minion + SRAM + NoC)`, all as deltas over that rung's own pre-launch
idle, with the S2 settling screen of this ledger (the idle bracket's minion rail steady within 0.15 W between
[t0−5, t0−3] and [t0−2, t0−0.3]) and the S3 dropout rule on every board window. Then one fit over both arms:

    offrail = a_m · minion + a_s · SRAM + a_n · NoC + R_eff · (minion / V_minion)^2

* **PASS (the term exists):** `R_eff` differs from 0 with 99% confidence over passes, and the fit's rms is at
  least 30% below the rms of the same fit without it. Report `R_eff` in mΩ and the conduction loss it implies at
  a 21 W minion rail — which is the pJ this moves out of "unattributed" in the ledger.
* **FAIL (it does not):** `R_eff`'s 99% interval contains 0. Then the off-rail remainder is reported as logic in
  step with the rails, with the conduction loss bounded above by the interval's edge, and the ledger's
  unattributed 0.26 pJ stays unattributed. **A FAIL is a result and is reported as one.**
* **Frozen before the first launch:** the predicted matched rail watts per rung (from E62-CAL's offset-plus-harts
  law), and the prediction that arm A's off-rail watts exceed arm B's at matched rail watts by
  (618/519)² − 1 = **42%** of whatever the conduction part is.

A departure that must be named if it happens: if arm B's governor intervenes at 768 harts, drop to 576 as the top
rung and say so; the match then tops out near 16 W.

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
