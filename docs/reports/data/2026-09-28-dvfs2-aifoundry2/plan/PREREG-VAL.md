# PREREG-VAL: the frozen DV2 validation (DVFS and heat on ET-SoC-1)

Frozen 28 Sep 2026, about 03:15 PDT, after development ended (last development pass 02:54 PDT). The SHA-256 of this
file is in `PREREG-VAL.sha256`. The code, numbers and schedules it registers are locked by
`/home/yaroslavvb/claude/et-soc1-dvfs2/tools/claims-v3/dv2v/LOCK.sha256`, whose own SHA-256 is
`6ca61de1ed62678842a24bd94be17ca71f18fb52f09866aa7546f11721e34dea`. Every validation pass checks the lock and refuses
to run if any listed file differs (§8).

- What development showed, with the numbers and every change it made: `DEV-RESULTS.md`.
- The design it tests: `DESIGN.md` rev 2 and `PREREG-DEV.md` (this directory).

**The owner's method.** Theories and predictions come first. All iteration happened on the development card,
aifoundry2, on the night of 27-28 Sep. What follows is frozen and is not iterated. The summary will say which
theories survived.

**The owner's questions.**
- (Q1) Does voltage-frequency scaling act on the average temperature or on one hot die?
- (Q2) Can the same computation run longer before throttling in some chip locations?

---

## 1. Cards: what can validate what

| Card | Governor | Role |
|---|---|---|
| aifoundry2 (fw 1.3.1) | free: TDP 65 W, threshold 65 | **replication** of every governor item, in a later session. It is the only card whose governor steps the clock |
| aifoundry3 (fw 1.3.1) | stuck in its power loop (TDP 0 from a lab service) | **cross-card test of TH8, already run.** At 00:33 on 28 Sep, before any development card data, the frozen PREREG-DEV §1.2 prediction "POWER_UP = POWER_DOWN = THERMAL_DOWN = POWER_SAFE = 0" was tested and **MET**, after HP's R3 had heated it past 66 °C. No further aifoundry3 run is registered |
| aifoundry1-c1 (fw 1.2.0) | never above 600 MHz | nothing registered. Z2-c1 needs the owner's slot and a device-1 guard, which is not built |
| aifoundry1 card 0 | — | never |

- **Governor items are replicated on aifoundry2, not validated on another card.** This is the design's honest
  classification (DESIGN §11). It needs the owner's acceptance (DESIGN §4.3 question a). **Until the owner accepts, no
  validation pass is started.**
- **Precondition: the Master Minion.** The development night ended with aifoundry2's Master Minion hung
  (`ALERT-MM-HANG`; DEV-RESULTS §2). The service processor is fine.
  - The idle items (VZ) do not use the Master Minion.
  - The NAT items (VN) do: they need the lab admin to restore it first.

---

## 2. Theories and their registered items

| Theory | Statement | Registered items |
|---|---|---|
| **TH1-busy** (Q1) | At 800 MHz the first down-step follows the integer mean of the 34 shire sensors (`> 65`), not the hottest shire | G1-T, G1-H |
| **TH1-idle** (Q1) | On an idle card the thermal state follows the mean, not the hottest shire | I1 |
| **TH2** | The cards run the 0.20.0 governor. Its thermal loop re-reads every 0.4053 s; the climb is one call; there is no busy test | I4, I5, G2-C, G2-D |
| **TH3** | No hysteresis: ENTER at thr + 1 = 66, EXIT at thr = 65 | I2, G2-U |
| **TH4** | Launch-to-800 and end-to-600 latencies come from the Master Minion heartbeat | G3-L, G3-I |
| **Q2** | At 800 MHz, perimeter placement (PER16@12) runs longer before the first throttle than interior placement (INT16@12) at equal minions | G4-S |
| **TH5** | The placement effect is the heat-only effect diluted by the clock's uniform adder: L_pred = 0.28 ± 0.10 | G4: **not registered** (readiness failed, §5); reported |
| **TH7** | An exit from the thermal state on an idle card is followed at once by the idle reset (PIDLE) | I3 |
| **TH8** | The THERMAL_DOWN residency counter adds whole episodes (ENTER → EXIT) when they end | I6 (aifoundry3's part is already MET, §1) |

- **Verdict per theory.** A theory **survived** if every registered item under it passes. It **fell** if any
  fails. Otherwise it is **untested**.
- **Outcome words.** PASS, FAIL, INSUFFICIENT. The idle-only schedule leaves every NAT item INSUFFICIENT
  (not run).

---

## 3. The idle items (read-only VZ cycles; no heat)

**The VZ cycle** is the development Z1 cycle, unchanged:
1. the gate: `who`, the process scan, `et-who`, the et_soc1 use count, and no other framework queue;
2. `flock -n` on the card lock (the cycle is skipped if it is held);
3. `sptrace` (a BAR read of the SP's 4 KB trace ring);
4. residency states 2-6 and uptime;
5. `config` (the threshold must read 65);
6. one 1 s, 10 Hz `ettelem sample` with one statistics reset at its start. `temp_c.minshire` = [mean, low, high] of
   the 34 minion-shire sensors; the mean is the same integer mean the governor compares.

About 1.5 s of card access. No heat, no set.

**Common definitions** (`dv2v/reduce_val.py`, locked).
- **Lines.** The governor lines of every dump are merged by kind and SP timestamp.
- **SP → host time.**
  - Normally through the DM request lines of the previous cycle's sample that survive in the next dump: MsgID 33 is
    the first request of each sample, matched to its `t_ms`. A fit counts only if its spread is ≤ 5 ms.
  - If the ring holds no DM lines (the SP at WARNING, e.g. after a reset), a coarse fit from the uptime minutes is
    used. All margins below then widen by its half-width U (about 30 s).
- **Busy intervals are excluded from every item.** An interval is busy if it holds:
  - a `power_up`, `power_down` or `new OP` line (a kernel of anybody); or
  - one of our heating passes (its block.json window, ± 30 s ± U).
- **A clean cycle** meets all four:
  - its state is known: the last thermal line before the sample is an ENTER (IN) or an EXIT (OUT), and no heating
    pass of ours came after that line;
  - no thermal line lies within 30 s + U before or after the sample;
  - the next THERMAL_DOWN counter change is explained to within 5 ms (no hidden episode);
  - it is not busy.

| Item | Prediction (from the source and development) | PASS | FAIL |
|---|---|---|---|
| **I1** (TH1-idle) | Separating: a clean OUT cycle whose hottest shire reads ≥ 66 in every sample (under H-max the governor would be IN within one 0.13 s pass). H-mean never gives a clean IN cycle with the mean ≤ 64 | ≥ 5 separating cycles over ≥ 3 OUT stretches, and no clean IN cycle with the mean ≤ 64 | ≥ 2 clean IN cycles with the mean ≤ 64, making up ≥ 50% of the discriminating cycles |
| **I2** (TH3) | Every ENTER prints 66 and every EXIT prints ≤ 65 | ≥ 10 idle ENTERs and ≥ 10 idle EXITs, all as predicted | any other printed value |
| **I3** (TH7) | Every idle EXIT is followed, as the next governor line, by a PIDLE, within 0.30 s. Development: 0.003-0.131 s, 19 of 19 | ≥ 10 idle EXITs, all followed by a PIDLE, ≥ 90% within 0.30 s | any other next governor line, or > 10% later than 0.30 s |
| **I4** (TH2) | Every idle ENTER → EXIT interval < 60 s lies within 0.015 s of k × 0.4053 s (k ≥ 0 an integer). Development: 16 of 16 within 1.4 ms | ≥ 5 intervals with k ≥ 1, all on the grid | > 10% off the grid |
| **I5** (TH2) | ENTERs on an idle card: the previous governor line is a PIDLE or an EXIT, with no busy line within 30 s. Development: 18 | ≥ 3 such ENTERs | none, although ≥ 3 cycle pairs show the mean rising from ≤ 64 to ≥ 66 |
| **I6** (TH8) | Between two clean reads the counter change equals the summed durations of the episodes that ended between them, less 1.33 ms per episode, within 5 ms. Development: −0.19, −0.05, −0.06 ms | ≥ 3 idle intervals with ≥ 1 completed episode, all within 5 ms | any interval off by > 50 ms, or > 10% off by > 5 ms |

Reported with I1: the count of "strong" separating cycles, where the high is ≥ 67.

---

## 4. The NAT items (the frozen NAT-4 replication session; VN)

**When it starts.** A VN candidate (after every 5th VZ cycle) starts the session only if the newest VZ reading
(≤ 15 min old) is ≤ 60 °C, and only as NAT-4 (a start reading ≤ 60).
- At most 3 sessions.
- It stops starting sessions once 16 complete G4 blocks exist.

**The session** is `dv2/block.sh` with `DV2_VAL=1` (data in `dv2v/p6051-p6099`). It is the development NAT session
with every development decision fixed:
- **Before the blocks:** the R0 probe (must be ALIVE), the smoke, and an ADD run.
- **Each T-block:** the 4 T-runs from the falling 63 → 62 edge (S 62, K 66), with the one-shot statistics reset at
  63.
  - Each run is one 8 s launch. The stop comes 2.0 s after the first 800 → 700 step; the tail is 10 s.
  - The runs follow DESIGN §5.5's cycle: B4C@32, INT16@12, PER16@12, UNI32@4 (the final DEV-1 candidate (192, 4)).
- **After the blocks:** the closing ADD run.
- **Fixed:** no development decision is recomputed (DEV-1, DEV-2, DEV-3), no RST run, no log-level change. DEV-10's
  rest rule applies as frozen.
- **Kept:** the caps, the post-run clock check, ABORT-LATCH, the 60 min cap and the worst-case block fit.
- **Per-run observables** are `dv2obs.py`'s (PREREG-DEV §1.1).
- **A valid run:** heater rc 0, not void, the edge reached, no safety stop, and exactly one reset before t0.

| Item | Rule (PREREG-DEV §1.1, §1.3-1.4 unless stated) | PASS | FAIL |
|---|---|---|---|
| **G1-T** (TH1-busy) | Separating: t_m − t_hi ≥ 1.5 s, or the high ≥ 67 at t_up with 800 held ≥ 0.5 s. Fits H-mean: t_down ∈ [t_m − 0.3, t_m + 0.6] s. Fits H-max: t_down ∈ [t_hi − 0.3, t_hi + 0.6] s | ≥ 6 separating runs over ≥ 3 blocks, ≥ 80% fitting H-mean, ≤ 1 fitting H-max | ≥ 50% of the separating runs fit H-max |
| **G1-H** (TH1-busy; registered here from the design's "reported") | A hold: a sample at 800 MHz with the high ≥ 67 (thr + 2), followed by ≥ 1.0 s at 800 MHz, the high having risen ≥ 2 °C since t0. H-max allows none | ≥ 3 holds over ≥ 2 blocks | ≥ 6 runs reach a high ≥ 67 at 800 MHz and none holds |
| **G4-S** (Q2; new) | Per block, L = ln(t800(PER16@12) / t800(INT16@12)) at S 62, with t800 = t_down − t_up. A censored run counts as kernel end − t_up; a block with both runs censored is dropped | ≥ 6 blocks, and the 99% CI of the mean L lies wholly above 0 | the CI lies wholly within ±0.05 |
| **G2-C** (TH2) | climbs 600 → 800 | ≥ 20 climbs; ≥ 95% show 700 MHz in ≤ 1 sample, and ≥ 25% show none | otherwise, with ≥ 20 climbs |
| **G2-D** (TH2) | descents 800 → 700 → 600 | ≥ 20; the 700 MHz dwell in [0.3, 0.7] s in ≥ 90% | otherwise, with ≥ 20 |
| **G2-U** (TH3) | up-steps | ≥ 20; the preceding reading ≤ 66 in 100%, ≤ 65 in ≥ 80%, never ≥ 67 | otherwise, with ≥ 20 |
| **G3-L** (TH4) | launch → first 800 MHz (valid T and ADD runs) | ≥ 10; median in [0.4, 1.0] s, all ≤ 2.2 s | otherwise, with ≥ 10 |
| **G3-I** (TH4) | kernel end → 600 MHz for runs that end at 800 MHz with no trip | ≥ 10; all in [0, 1.6] s | otherwise, with ≥ 10 |

**G4 (TH5), reported only.** L_pred = 0.280 and b = 0.100 (`prereg-val.json`).
- Inputs: aifoundry3's couplings, κ_P = e^−0.48 and κ_U = e^−0.34, because C1m did not run. P_U = 7.37 W and
  P_x = 9.37 W from p6038.
- The reducer prints whether the 99% CI lies inside [0.18, 0.38]. That is not a registered verdict.

---

## 5. Why some items are registered and G4's band is not (a named deviation from PREREG-DEV §2's readiness rule)

**Readiness failed on one count:** 2 T-blocks, not 4, ran under the final DEV-1 candidate. The continuation session
that was to add 4 ended with the Master Minion hang.
- The count matters for G4's n_val (SD_dev). **G4's band test stays in development.** The replication still
  collects its blocks, and the band result is reported.
- G1-T, G2-C/D/U and G3-L/I have rules frozen in PREREG-DEV §1 before any data. G1-H and G4-S are one-sided tests
  that need no variance estimate. Their run parameters were fixed by DEV-1/2/3.
- T6 (the reducer reproduces the retrospective) held.
- T1 matters only for the SP-line items, which are not registered (DEV-5 = no).
- **The idle items I1-I6 are new.** They came from development:
  - they need no heat and no global change;
  - their rules and constants were fixed before any validation data;
  - their reducer ran on the development data (DEV-RESULTS §3).

---

## 6. Schedules and the exact start (NOT started)

**Before starting (all four):**
1. The owner accepts the replication on aifoundry2 (question a).
2. The owner picks a schedule:
   - **full:** VZ + VN, with heat, which needs the Master Minion restored;
   - **idle-only:** VZ, zero heat.
3. For the full schedule, the lab admin has restored aifoundry2's Master Minion.
4. `who` and `et-who` show nobody else, and no other queue of ours runs on aifoundry2.

**When.** At or after **12:00 PDT on 28 Sep 2026**, the later of `val.json`'s not_before and 4 h after the last
development pass (02:54).
- A VZ pass that is started early waits, holding nothing, if the earliest start is ≤ 8 h away. Otherwise it skips.
- The window is 20 h from the first VZ cycle: 399 cycles, 180 s apart, the last at about 08:00 the next day if
  started at 12:00.

**Commands (on aifoundry2):**

```bash
cd ~/claude/et-soc1-dvfs2
who; et-who                                          # nobody else on the card
sha256sum -c tools/claims-v3/dv2v/LOCK.sha256        # every line OK (the passes check it too)
rm -f build/claims-v3/STOP                           # left by the development night's stop (ALERT-MM-HANG)
# full (idle watch + the NAT-4 replication when the card rests <= 60 C):
setsid nohup tools/claims-v3/queue.sh tools/claims-v3/schedule-dv2val-aifoundry2.txt \
  > build/claims-v3/queue-dv2val-aifoundry2.log 2>&1 < /dev/null &
# or zero heat (idle watch only):
# setsid nohup tools/claims-v3/queue.sh tools/claims-v3/schedule-dv2val-idle-aifoundry2.txt \
#   > build/claims-v3/queue-dv2val-aifoundry2.log 2>&1 < /dev/null &
```

**Watch** `build/claims-v3/queue-dv2val-aifoundry2.log` and `build/claims-v3/aifoundry2/dv2v/ALERT-*.json`.

**Stop:** `touch build/claims-v3/STOP`. To end a running VN session at its next gate, also
`touch build/claims-v3/aifoundry2/dv2v/NIGHT-STOP`.

**The reduction.** Run it after the queue ends, not on aifoundry2 while a session runs:

```bash
cd ~/claude/et-soc1-dvfs2
python3 tools/claims-v3/dv2v/reduce_val.py --data build/claims-v3/aifoundry2/dv2v \
  --out build/claims-v3/aifoundry2/dv2v/verdicts-dv2val.json
```

It prints every item's verdict with its counts and the per-theory summary (§2), and it writes the JSON above.
`reduce_val.py --self-test` checks the rules on planted outcomes.

---

## 7. Risks and limits (stated before any validation data)

- **The Master Minion hang could recur in VN sessions.**
  - The single occurrence came at a heater launch 0.6 s after the previous one; 45 other launches did not hang.
  - A recurrence would again need the admin. The session aborts after 3 heater failures and does not retry.
  - The idle-only schedule carries no such risk.
- **VN needs a cool card** (a start reading ≤ 60 °C). On the development night the rest swung between 59 and 72 °C.
  In daytime a cool window may never come; the NAT items are then INSUFFICIENT.
- **I1 needs the rest to sit at a mean ≤ 65 with the hottest shire ≥ 66**, so an idle spread ≥ 1-2 °C at 64-65.
  Development saw 1 such cycle in 21. A 20 h watch at 180 s gives about 400 cycles.
- **After a reset the SP may log at WARNING.** The coarse time fit then applies (±30 s), and fewer cycles qualify
  as clean.
- **One card, one chassis, one room.** The NAT items run under NAT-4 at the native threshold of 65 °C, never with a
  raised threshold (D1 was never approved).
- **H-max as tested is "the hottest of the 34 shire sensors" (the PVT high).** Sensors outside the minion shires are
  not covered.

---

## 8. The lock (`tools/claims-v3/dv2v/LOCK.sha256`; every VZ and VN pass runs `sha256sum -c` on it)

```
3682c74d0ebf33800e0f9f5ff166bdc0610065738a4092f21e0d6322b8f03a4a  tools/claims-v3/dv2v/block.sh
c7edc72eb84b6945878b1d895f26cde47f3f887130b76c59fc5f61091794cd19  tools/claims-v3/dv2v/val.json
7472859f2c794d4e479239549318eb5f8e82fbe74507a76d0d5665728b13a770  tools/claims-v3/dv2v/vn_check.py
b9dc18e34a97221ef72db77687c773dc22a12b5e98989711aac647ec8e3580ca  tools/claims-v3/dv2v/reduce_val.py
5ea3638abca0a92139b67c3c7072c186de40c2d8d8518fc2a238122daaa4bbcf  tools/claims-v3/dv2v/prereg-val.json
159e0779099ad3d474fe26c5d8192a38c82e5d3ba9636b4f673968b8075a3495  tools/claims-v3/dv2/block.sh
b4bb3353c35d68bfd7055287806a04a0060f89b22493b84092f7e02d2ac2bdf8  tools/claims-v3/dv2/dv2lib.sh
910ec333cd6ee0340e5a21a819e58812152a498dfd837814dc5e7519e75850e7  tools/claims-v3/dv2/dv2lib.py
d749a0d1106dd0f3608d99c0404c1c9ae3fa8d284119192fa172a3bcaa901c4b  tools/claims-v3/dv2/dv2obs.py
8cbb7df0d6e32494945ad5a8d761b9b02c4b6ad3efa1d087b0c7091a71178834  tools/claims-v3/dv2/sptrace_events.py
8421fe1cdb45a99db7b979b1ba0add3a60418eac6546b8dbe9bfec2d7dd8c2ea  tools/claims-v3/dv2/placements.json
f2de28b4d255a9f96880df22b183998b031c2b07bc6dfd16493d9d2dd482b379  tools/claims-v3/dv2/reduce_dv2.py
033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa  tools/claims-v3/lib.sh
4b63600429614c2379ce6e63e0cfc4fe518e8069bfa3a01b594b663facd924e9  tools/claims-v3/queue.sh
77c44d33fe9dace7fbef4b83a971907a49e9be7292a00ae10f27e622e0d75204  tools/claims-v3/schedule-dv2val-aifoundry2.txt
e2a5cef245ec1b941985ff6250f14388fa4f925b2ba7365fec342ca38811deaa  tools/claims-v3/schedule-dv2val-idle-aifoundry2.txt
77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5  build/ettelem-dv2/ettelem
bc961635f175f52228d3035faafe0a13be34c0aa44a475dd23980ef0a4eb4b5f  build/sparsity_t2/host/sparsity_host
990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24  build/sparsity_t2/kernel/sparsity.elf
```

All paths are relative to `/home/yaroslavvb/claude/et-soc1-dvfs2` (branch `dvfs2`, uncommitted). Nothing listed
may change between the freeze and the end of validation. A change makes every pass refuse (exit 2).
