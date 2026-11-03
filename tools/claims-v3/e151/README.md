# E151: int8's B side on aifoundry3 card 0 again - E145's design with its rail filter written and registered first, the minion rail as the registered primary (Q139)

*Pre-registered Tue 3 Nov 2026 (week 45), on the Intel, before the claim of aifoundry3 and before any E151 run, in Q139 (the owner's
words of Mon 2 Nov 2026, about 18:40 PST: "feel free to settle any unanswered questions regarding horace's power model", with Q137's
goal, "to be able to predict the power requirement and heat generation of various kinds of numeric computations as accurately as
possible"). **It answers item 12 of the kinds page's section 11**, "int8 at gate level"
([horace-kinds-of-numbers § 11, item 12](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), and
**rank 11 of Q138's final critic**: "the registered verdict on B's recoder (E145 again with a spike filter registered first, or on
aifoundry3) ... E145's design on aifoundry3, its rail filter written first. Rule: R1's interval clears the 30.68 fJ line." It builds on
[E130](../../../docs/reports/data/2026-11-02-e130-int8-netlists/README.md), [E138](../../../docs/reports/data/2026-11-02-e138-int8-b-rail/README.md)
(R1 INCONCLUSIVE, 0.2 fJ short of the line) and [E145](../../../docs/reports/data/2026-11-02-e145-int8-b-card1/README.md) (R1
INCONCLUSIVE on card 1 because its rail glitched; post hoc, with the glitches removed, +36.1 [+31.8, +40.5], which would have cleared
it). Card: **aifoundry3 card 0 only**, 600 MHz, TDP 0 W / threshold 65 °C as read, never set. **E151 sends no write command of any
kind** (§ Device commands sent). Any change after this commit goes in Amendments, dated, before the data it touches.*

## What it does to predicting power and heat

The power model prices an int8 multiply by the bits that flip in its operands (fJ per flipped bit, per operand). On aifoundry3 E130
found A's bits priced alike and E138 found B's priced by position (odd bits about 1.9× the even ones); E145 found card 0's per-position
B list predicts a second card's to 20% rms as registered (7% without card 1's rail glitches) against 39% (35%) for one price. **The
terms E151 measures and tests:** (1) the structural one, whether B is Booth-recoded (R1), which decides whether the per-position B
term is a property of the multiplier's design (so it can be carried to any kernel and card) or an accident of these tiles; (2) the
per-position B price itself, out of sample twice, both registered here and computed by `score_e151.py` (never a verdict): card 0's
earlier sessions' frozen prices (E130's and E138's, `predictions-e151.json` › `card0_prices_rail_fJ`) predicting today's prices on the
same card (the day-to-day error), and card 1's prices under E151's filter (`card1_prices_rail_fJ_filtered`, frozen here from E145's
data) predicting card 0's (the card-to-card error, now in the other direction). Before = one price per B bit (the shape of M5's and
M6's int8 forms; E145's 35-39% across cards), after = per position. It matters for kinds whose flips sit on a few B bit positions
(small integers, sign patterns, few-level quantised weights), not for uniform random int8, where every bit flips alike. **Heat**: E151
measures no heat term; the die is recorded per block (the shires' mean, `minshire[0]`), and heat follows power through the die rise
per board watt (0.87 °C/W on this card, Q138(t)), so E151 changes the heat prediction only through this power term.

## The rail filter (written and registered before anything else)

**Why.** Card 1's minion rail now and then reports the service processor's running maximum (`sp.minion_w[2]`, 34.50 W) as its current
reading (`sp.minion_w[0]`) for one or two samples. In E145 four such samples fell inside three B runs' rail windows and widened R1's
interval six-fold (E145 README § 3). The critic asks for the filter to be written down first, by a rule that never looks at B's
contrast, and tested on E145's data before the run.

**The rule** ([`railfilter_e151.py`](railfilter_e151.py), sha256 in `predictions-e151.json` › `rail_filter`). In each block's
telemetry, read as the sampler wrote it (one line a sample, in order), sample *i* is a **rail glitch** when

- **F1**: its rail reading `sp.minion_w[0]` is more than **4.0 W above both samples two steps away** (*i* − 2 and *i* + 2): E82
  amendment A2's board-dip rule mirrored onto the rail, E145's post-hoc definition unchanged; or
- **F2**: its rail reading **equals the running maximum the same sample reports** (`sp.minion_w[0] == sp.minion_w[2]`), the value
  card 1's glitch reports. F2 catches a glitch at a high load where the jump is under 4 W (card 1's fp32 sessions show such samples);
  on this card the field has read a constant 38.375 W in every sample since 1 Nov, and int8 trains draw 6.7-13.5 W on the rail (E138),
  so F2 cannot touch a real reading here.

A glitch sample is removed whole (its board reading too) before the reduction reads the telemetry, exactly as E82 A2's board dips
are, and E151's **registered primary removes both**, dips and glitches, each marked on the raw sequence and their union removed (E145's
post-hoc arm did the same with F1 alone). **The rule reads only the telemetry samples, one block at a time: never an item, a run, a
step, a price, B's odd − even or any other result.**

**Tested on E145's data before E151's first launch** ([`selftest-e151.txt`](selftest-e151.txt), [`e145_under_filter.py`](e145_under_filter.py)):

| test | result |
|---|---|
| E145's 16 blocks, 26,469 samples | the filter marks **15** (F1 15, F2 15, union 15): E145's post-hoc 15, all at the running maximum |
| E145's reducer (`reduce_e145.py`, unchanged) with its dip filter extended by E151's rule | reproduces E145's post-hoc reduction **byte for byte** (`posthoc/runs-posthoc.csv`, `e145-posthoc.json`); committed as [`e145-filtered/`](e145-filtered/) |
| scored with E145's scorer, unchanged | B odd − even **+36.12 [+31.75, +40.49]** board-equivalent fJ (n 13): R1 would read **RECODED** on card 1 under this filter |
| E138's 9 and E130's 11 aifoundry3 blocks | **0** marked (15,741 and 16,091 samples) |
| every committed aifoundry3 card-0 session since 1 Nov (25 sessions, 161 telemetry files) | **0 of 628,575 samples** marked; the running-maximum field 38.375 W in every sample (`predictions-e151.json` › `rail_filter.aifoundry3_census`) |
| synthetic lines | a lone glitch (F1 and F2), a pair (both), a load step (none), a high-load glitch under 4 W (F2 only), an aifoundry3-like stream (none) |

## The meter: aifoundry3 reports the minion rail cleanly

**Checked first, on committed data:** the rail is **live** on this card (E138: 2,255 distinct values in 16,082 samples, 5-95% range
7.46-11.46 W, the longest run of one value 5 samples; E141 9,340 distinct, 8.30-27.80 W; E144 6,998, 6.76-28.45 W; E147 5,380,
12.98-19.42 W; none held one value more than 7 samples) and **clean** (the census above: no glitch by either rule in 628,575 samples).
E78's lag fit on this card is 0.95 s. **Checked again live, in the smoke gate:** the rail must be live (at least 20 distinct values, a
5-95% range of at least 1.0 W, no 30 identical samples in a row: E145's test) **and clean** (the filter marks at most 1% of the smoke's
samples; card 1's rate was 0.06%). If either fails, no block runs: the board's `p_raw` as primary would need about 60 B blocks (E138's
board arm scattered 20.2 fJ a block), beyond the 35 card-minutes. So **the registered primary is E145's, with the filter**: the minion
rail's `rail_raw` (E78's mean over [t0+2 s, t0+4 s)) over each item's own zero interpolated in time, ÷ designed flips × rate, **÷ c_rb
= 0.81** (E78's frozen rail-per-board constant) = board-equivalent fJ.

## How many blocks fit, and the control

**The brief's "about 13 B blocks" does not fit in its 35 card-minutes on this card.** E138's B blocks took 177-178 s here (start to
start 182-183 s with the gap), E130's A blocks 133-134 s, and the stop-path test and smoke take about 55 s (E141). From the
session-start config read, 35 minutes (2,100 s, 45 s reserved for the closing read) hold **ten B blocks and one A block** (about 2,030
s), or eight B and three A, never thirteen B. E151 registers the first: **R1 is the registered primary and the critic's decisive test,
and B blocks are what narrow its interval** (ten B blocks: ±5.10 at E138's scatter; eight B: ±5.96).

**The control on this card is E130's.** On card 1, E145 ran three A blocks because the A side of a new card's meter was unknown. On
aifoundry3 the A side was measured and registered by E130 the day before (four A blocks: A odd − even −1.7 [−6.6, +3.2] fJ, FLAT; A's
sign step +67.8 [+58.8, +76.8], RISES), and E138, on this card, ran B only and read its R4 from E130's A verdicts. E151 does the same:
**E151-R4 is E138-R4's rule on E151-R1, with this card's A side as E130 registered it.** One A block runs after the ten B blocks if the
budget allows, as **an in-session check reported beside E130's** (its A odd − even and sign step, one block each, with E130's per-block
spread); one block is below E145's minimum of three, so E151-R2, R3, C1, R4s and N read NOT SCORED unless three A blocks are kept.

**Precision, before the data** (`predictions-e151.json` › `precision`; half-width = t(0.975, n − 1) × sd / c_rb / √n, board-equivalent
fJ; RECODED needs a mean of at least 30.68 + half-width):

| kept B blocks | 8 | 9 | **10** | 11 | 12 |
|---|---:|---:|---:|---:|---:|
| half-width at E138's block sd (5.77 rail fJ) | 5.96 | 5.48 | **5.10** | 4.79 | 4.53 |
| RECODED needs a mean of at least | 36.64 | 36.16 | **35.78** | 35.47 | 35.21 |
| half-width at E130's block sd (2.77 rail fJ) | 2.86 | 2.63 | **2.45** | 2.30 | 2.18 |
| RECODED needs a mean of at least | 33.55 | 33.32 | **33.13** | 32.98 | 32.86 |

**The chance of RECODED at ten blocks** (simulated, `precision.simulated_chances`: normal block values, the session's own sd and exact
t, as scored): at E138's scatter **0.17** if today's mean is E130's +33.15, **0.37** at card 0's two-session pool +34.8, **0.56** at
E138's +35.95, 0.58 at E145's filtered +36.12; at E130's scatter 0.53, 0.92, 0.99 and 0.99. FLAT is near impossible (at most 0.002).
So the outcome turns on today's block scatter as much as on the mean, and **R1 RECODED is less likely than not at card 0's pooled
mean** (§ What I expect).

## What runs

| | E145 (aifoundry1 card 1, `18e5a7d2`) | E151 (aifoundry3 card 0) | why |
|---|---|---|---|
| tiles | Q136(a)'s 26 int8 tiles, in place | **the same 26, byte for byte** (`tools/claims-v3/kinds/e130/`; `e130-items.json` copied unchanged, sha256 checked) | no new prediction is needed |
| B blocks | 14510-14522 (13 ran), E138's B design (34 runs: 4 settling `hb1`, `hb1` between every pair of the 14 hb1 items, the two sign triples) | **15110-15119 first**, the same design, each order seeded `Random("E151\|aifoundry3\|<pass>")` | R1's precision |
| A blocks | 14530-14532, E130's A design (25 runs) | **15130 after the ten B blocks, if the budget allows**, the same design; 15131, 15132 only if time remains | the control on this card is E130's (§ How many blocks fit) |
| sequence | 14510 14530 14511 ... (A second, sixth and tenth) | **15110 15111 15112 15113 15114 15115 15116 15117 15118 15119 15130 15120 15131 15132**; the budget rule decides how many run | B first |
| a run | E78's `sparsity_host --test fma --type int8 --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, trains (`--preheat 0 --target 200 --quiet-s 0.2 --burnin 0`) | the same | E130's protocol |
| primary | the rail, board-equivalent at 0.81, the board's dips removed | **the same, with E151's rail glitches removed too** | § The rail filter |
| reduction and gates | E78's `reduce_e78.py` unchanged via `reduce_e145.py --drop-dips` (card 1's configuration substitution); E78's run and pass gates; E130's train gate (a zero's interior read > 0.25 W off its neighbours' line, on the board's `p_raw`) | `reduce_e78.py` unchanged via **`reduce_e151.py --drop-dips --rail-filter`**; E78's own configuration gate (it accepts aifoundry3's 0 W / 65 °C: no substitution); the same gates | |
| scorer | `score_e145.py` (imports `score_e138.py`, `score_e130.py`) | **`score_e151.py`, which imports `score_e145.py` and so `score_e138.py` and `score_e130.py` unchanged** (sha256 in `predictions-e151.json` › `harness`); E145's exact t | one scorer for all four sessions |
| arms (reported) | board `p_raw`, board `p80`, rail dips kept, rail gates off | board `p_raw`, board `p80`, **rail with the filter off** (E145's primary form), rail with the dips kept, rail gates off | a verdict that moves at an arm is marked arm-sensitive |
| smoke | 14501: E138's eight 2 s runs, after the stop-path test 14502 | **15101**, the same eight, after the stop-path test **15102** (die, board and the in-run watcher) | cycles per op 318, tile dumps, the clock, the rail live and clean |
| budget | 3,000 s from the session-start config read | **2,100 s (35 card-minutes) from the session-start config read, 45 s reserved**; first estimates B 185 s, A 140 s, then the longest block of its kind | the brief's at most 35 card-minutes |
| time gates | — | **no session starts after 10:30 PST** (`session_e151.sh` refuses); the queue's deadline 11:25 PST, so every run ends by 11:30 | the round's gates |
| stops | board ≥ 60 W, any minion-shire reading ≥ 72 °C | **board ≥ 45 W, `minshire[0]` ≥ 68 °C, both on live samples, read by the main path and by an in-run watcher**; `run_e78`'s own cap 70 °C | § Stops |
| raw | `~/nekko/build/claims-v3/aifoundry1-c1/kinds/p145*` | `~/aifoundry/build/claims-v3/aifoundry3/e151/p151*`, `e151-smoke/`, `e151-stoptest/`, `build/e151/`; results `docs/reports/data/2026-11-03-e151-int8-b-aifoundry3/` | |

**No warm-up block**, as E138 and E145: every kept block counts. The session-level files are E141's aifoundry3 harness of last night
(the session script, the guard with the in-run watcher, the queue anchored on T0), ported with E145's two block kinds, each change marked
in the file.

## Stops

**Every stop reads live samples.** `run_e78.py` reads the newest line of the block's running sampler file, `telemetry.jsonl.raw` (which
`lib.sh`'s `start_sampler` writes one line a sample while `ettelem sample` runs), before every launch and every 0.1 s while it waits;
`run_e151.py` wraps that read (E145's guard as E141 ported it), and **a daemon thread reads the same file every 0.1 s for the whole
pass, runs included** (E141's in-run watcher: a 4 s run's own peak is otherwise unseen, and the host program checks the STOP file
before every launch of its loop). A line with **`board_w` ≥ 45 W** or **`temp_c.minshire[0]` ≥ 68 °C** writes the pass's STOP file and
ends the pass with EXIT_HOT; the queue then stops. **The die stop reads `minshire[0]`, the current shire reading** (the field
`run_e78`'s own `--max-c` reads): on aifoundry3 `minshire[2]` is a latch that reads 87 °C in every sample (E138, E140), so E145's field,
the largest entry, would stop every pass at once. The message records the line's `t_ms` and its age when read. Margin: E138's trains
on this card read at most 29.54 W on the board (its smoke 31.67 W) and 55 °C, against 45 W and 68 °C, and the PMIC's thresholds far
above. **The stop path is tested on the card before any launch** (pass 15102): the sampler starts, then `run_e151.py` runs three times,
with the die stop at 1.0 °C, the board stop at 1.0 W, and the watcher alone with the board stop at 1.0 W; each must end on a live
reading with EXIT_HOT and a STOP line naming its stop and a sample read at most 2.0 s after it was taken, from `telemetry.jsonl.raw`,
with no launch made. If any fails, nothing else runs. Also: the STOP files (`build/e151/STOP`, `build/claims-v3/STOP`,
`build/kinds-STOP`); another user's device process, a device node or this card's lock held by anyone else (D1: an idle login does not
block on aifoundry3); `timeout 10` on every device process.

## Device commands sent

*The owner's rules of Mon 2 Nov 2026: every device-management command the run's harness, sampler, host program and helpers send,
classified READ or WRITE from the firmware source of the running build; only read-only PMIC voltage reads and the statistics reset are
allowed, and **E151 does not send the reset**.* The sending code is E141's and E145's (`lib.sh` unchanged, the same `ettelem` binary
E138, E140, E141 and E147 ran on this card, through E128's guard `tools/claims-v3/e128/ettelem_guard.sh`, which admits `ettelem config`
with no argument and `ettelem sample --seconds <n> --every-ms <n>` only and refuses anything else before the device opens), classified
from et-platform `836a4ab` (BL2 0.22.0; Q136(w)'s table `tools/claims-v3/dmcmd_table.json`):

| sent by | command (id) | what the service processor does | class |
|---|---|---|---|
| `ettelem config` (session start and end; both ends of every block, the stop test and the smoke) | GET_MODULE_STATIC_TDP_LEVEL (25) | `thermal_pwr_mgmt.c:613-617`, a RAM copy | READ |
| | GET_MODULE_TEMPERATURE_THRESHOLDS (21) | `thermal_pwr_mgmt.c:665-669`, RAM | READ |
| | GET_MODULE_POWER_STATE (23) | `thermal_pwr_mgmt.c:551-555`, RAM | READ |
| | GET_ASIC_FREQUENCIES (53) | `perf_mgmt.c:276` → `io_pll.c:907-960`, PLL register reads | READ |
| | GET_ASIC_VOLTAGE (32) | `thermal_pwr_mgmt.c:1142-1222`, PVT reads and **two PMIC voltage-register reads** (`pmic_controller.c:1473-1500`; allowed) | READ |
| `ettelem sample --seconds --every-ms 100` (each block's sampler, 10 Hz), and `lib.sh`'s `die_c` (`ettelem sample --seconds 1 --every-ms 500` at both ends of each block, E145's C5) | GET_MODULE_POWER (33) | `thermal_pwr_mgmt.c:984-988`, the RAM copy the SP keeps | READ |
| | GET_SP_STATS (60) | `thermal_pwr_mgmt.c:2780-2784`, RAM | READ |
| | GET_MODULE_CURRENT_TEMPERATURE (27) | `thermal_pwr_mgmt.c:732-773`, PVT register reads | READ |
| | GET_MODULE_VOLTAGE (31) | `thermal_pwr_mgmt.c:1010-1140`, **nine PMIC voltage-register reads** (allowed) | READ |
| | GET_ASIC_VOLTAGE (32), GET_ASIC_FREQUENCIES (53) | as above | READ |
| `lib.sh:154` `start_sampler` forwarding `--reset-ms` (SET_STATS_RUN_CONTROL, the statistics reset) | — | **never sent**: `block_e151.sh`'s only call passes the file and the duration; the guard refuses `--reset-ms` | WRITE (allowed, not used) |
| `lib.sh` `drain_mgmt` (`dev_mngt_service` GET_MODULE_POWER) | — | **never sent**: replaced by a refusal in `block_e151.sh` | READ |
| `sparsity_host` (the ops node: DMA, kernel launches; also the heater, unused in trains), `et-who`, `et-holders`, `et-lab-manifest` | — | no device-management command (host state: `/proc`, lock files, sysfs) | — |

**All nine sent commands are READs.** Never sent: SET_STATS_RUN_CONTROL (no `--reset-ms` anywhere), any SET_*, the firmware-revisions
query, any residency read, any governor, TDP, threshold or clock set, any reset. **The checker** `tools/claims-v3/dmcmd_audit.py`
(unchanged), on every file the session runs (`preflight_e151.sh`: the E151 card files, `lib.sh`, the guard, E78's runner and common
module, the workload's host source): **NO-GO** without an exception, at the one conditional site E130's A1 reviewed (`lib.sh:154`), and
with the reviewed exception **GO, 32 send sites, 0 disallowed** ([`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt),
[`dmcmd-audit.txt`](dmcmd-audit.txt)); the desk files send nothing (GO, 0 sites, [`dmcmd-audit-desk.txt`](dmcmd-audit-desk.txt)). The
session runs the same preflight on the box before any device opens and stops on anything but GO. **Residual (E130's A1, E141's):**
aifoundry3 runs a non-public thermal firmware build first flashed on 7 Oct 2026, so these classes rest on `836a4ab`'s handlers and on
these reads' unchanged behaviour on this card; if the session's config reads or the smoke's telemetry come back in another form
(TDP 0 W / 65 °C / 600 MHz, `since_reset_ms` −1), the smoke gate fails and no block runs. **Verdict before the first launch: GO.**

## The frozen numbers

From E145's registration (`predictions-e145.json`, sha256 in `predictions-e151.json` › `source`; E138's, E130's and Q136(a)'s numbers),
nothing refitted:

| | value | from |
|---|---|---|
| T_B | **30.68** board fJ | E130, the midpoint between the groups' nearest predictions |
| T_A, T_S | **27.58**, **18.07** board fJ | E130 |
| c_rb | **0.81** | E78's frozen rail-per-board constant |
| Booth on B's band, B odd − even | **[54.79, 66.18]** board fJ | the hull of `booth`'s and `booth_tree`'s frozen bands |
| no recoder on B, B odd − even | **[0.49, 1.23]** board fJ | the hull of `booth_swap`'s and `plain`'s |
| Booth on B, B odd / even | **[4.164, 4.394]** | the same hulls of the ratio |
| no recoder on B, B odd / even | **[1.047, 1.095]** | |
| card 0's earlier per-bit rail prices, B bits 0-6 | 20.1, 56.7, 32.7, 64.4, 45.2, 61.6, 47.5 rail fJ (mean 46.9) | E130's 6 and E138's 9 B blocks (E145's frozen list, recomputed and checked equal) |
| card 0's earlier per-bit rail prices, A bits 0-6 | 68.2, 61.1, 59.7, 67.0, 67.7, 66.1, 63.4 rail fJ | E130's 4 A blocks |
| card 1's per-bit rail prices under E151's filter, B bits 0-6 | 16.7, 55.9, 30.0, 59.9, 41.1, 59.6, 44.8 rail fJ | E145's 13 B blocks, `e145-filtered/` |
| card 1's per-bit rail prices under E151's filter, A bits 0-6 | 70.7, 62.1, 59.8, 65.1, 66.3, 64.3, 62.1 rail fJ | E145's 3 A blocks |

## Decision rules

On the primary over kept blocks; a statistic is E130's per-block combination, its 95% interval t(n − 1) × sd / √n over blocks (exact t,
E145's); a ratio is Fieller's, paired. **Fewer than 3 kept blocks of a kind: that kind's rules NOT SCORED.**

| rule | what | verdicts |
|---|---|---|
| **E151-R1** (the registered primary; the critic's decisive test) | is B recoded? B's odd (1, 3, 5) − even (0, 2, 4), board-equivalent fJ, against T_B | **RECODED** if the low end ≥ 30.68 (the interval clears the line); **FLAT** if the high end ≤ 30.68; else **INCONCLUSIVE** |
| **E151-R1n** | the same interval against the two groups' bands | IN BOOTH ON B's BAND / IN NO RECODER's BAND / NEITHER (BETWEEN, ABOVE, BELOW) / INCONCLUSIVE if both |
| **E151-R1q** | B's odd / even on the rail (no unit, no c_rb) against the ratio bands | as R1n; NOT SCORED if unbounded |
| **E151-R4** | which multiplier on card 0: E138-R4's rule on E151-R1, with E130's registered A verdicts on this card (R2 FLAT, R3 RISES) | **BOOTH ON B** if R1 RECODED; **NO BOOTH** if FLAT; else INCONCLUSIVE between BOOTH ON B / NO BOOTH |
| E151-R2, E151-R3, E151-C1 | the in-session A control: A's odd − even against T_A; A's sign step against T_S; does today's A side read as E130's? | as E145-R2, R3, C1 (C1: REPRODUCES E130 / DIFFERS from E130); NOT SCORED under 3 kept A blocks |
| E151-R4s | E145-R4's form: E130-R4's rule on this session's own R1, R2, R3 | NOT SCORED under 3 kept A blocks |
| E151-R5, E151-R6 | the shared predictions (A's and B's sign, word 2 / word 1, in the shared band) | HOLDS / FAILS (ABOVE, BELOW) / NOT SCORED |
| E151-N | each netlist's frozen prediction on E130's three separators | SURVIVES / EXCLUDED by … / NOT SCORED (the A separators need 3 A blocks) |

**Reported, never a verdict:** every rule at every arm (a verdict that moves at an arm is marked arm-sensitive; the filter-off arm
shows what the filter moved); the samples each rule removed, per block; the pools (card 0's three sessions E130 + E138 + E151; E151 +
E138; two cards, E151 + E145 under the filter; all four); this card's rail/board scale from A's and B's bits 0-6, and R1 read at the
A-based scale; the c_rb at which R1's reading would change; every item's rail, board-equivalent and board fJ; the two out-of-sample
price tests (§ What it does to predicting power and heat); the telemetry's extremes per block; the A block's values beside E130's.

## What I expect, frozen so it can be wrong

**R1 INCONCLUSIVE** (RECODED's simulated chance about 0.37 at card 0's pooled mean and E138's scatter; above even only if today's
scatter is E130's), R1n and R1q **NEITHER (BETWEEN)**, R4 **INCONCLUSIVE between BOOTH ON B / NO BOOTH**, R2, R3, C1, R4s, R5 and N **NOT
SCORED** (one A block), R6 **FAILS (BELOW)** (card 0's rail: E138's b2_7 / b1_7 = 0.69). The filter **removes no sample** (the census).
Ten B blocks and one A block run (nine B and one A if the blocks run slow). Out of sample: per position < parity < flat on B in both
tests; per position about 3-5 rail fJ (7-10% of today's mean), flat about 13-15 (29-35%); on A flat and per position alike.

**The statement the page gets, decided now.** R1 RECODED: "on aifoundry3, with the rail filter registered first, B's odd − even clears
the line: the multiplier's B side is recoded (BOOTH ON B, with E130's A verdicts), in a way neither frozen netlist reproduces: its odd
bits cost what Booth on B predicts, its even bits about twice". R1 INCONCLUSIVE: "three sessions on card 0 and one on card 1, the line
not cleared by a registered test; the structural question stays open, the prediction is answered by per-position prices". R1 FLAT: "card
0 reads B's alternation below the line". Each with its c_rb dependence (the flip points and the A-based scale). **No tile, threshold,
band, filter or rule changes after this commit; only blocks that ran are scored.**

## What the rules cannot say

One clock, E130's base words, the card E130 and E138 used (a third session on it, a new day). The conversion to board fJ is E78's
constant, measured on this card; the in-session scale is reported, not used. The rail's lag (about 0.95 s here) carries into the next
read; the trains' paired zeros take most of it out. The filter cannot see a glitch that is neither 4 W above its neighbours nor at the
running maximum; on this card no glitch of any kind has been seen. The netlists are Q133(a)'s, at zero delay; why the even bits cost
about 2.2× Booth on B's count is the critic's other half of rank 11 (the archive's glitch-aware count, private, Q139(v)), not this run.

## Protocol (for this lane)

1. **Desk, before this commit:** `e145_under_filter.py` (the filter on E145's data), `make_predictions_e151.py` (the freeze),
   `selftest_e151.py` → `selftest-e151.txt` (22 checks: the filter, E145's reduction under it, the scorer on E138's, E130's and E145's
   data, the stop guard, the smoke gate's stop test, the harness check, the orders), the checker as above. All PASS.
2. **On the box, no device opened** (files rsynced to `aifoundry3:aifoundry/` at the same paths; done before this commit and again after
   it): the harness check (`check_e151.py`, 48 files), the tiles (`e151_common.py --verify`), the preflight (GO), dry runs of a B block (34
   launches, all int8 on E130's tiles), an A block (25) and the smoke (8), a dry session (it stops before any block when the stop test
   cannot fire), the queue's budget rule on stub blocks.
3. **Claim:** Tue 3 Nov's one post in `#community-lab` (created by the first lane to reserve, every later change a rewrite with
   `EXPECT_TEXT` under the discord lock) gets the clause `using aifoundry3 for 1 h, until ~HH:MM PST` beside the clauses held then;
   `et-who` free on card 0 before it.
4. **Session:** `E151_T0=$(date +%s) setsid nohup bash tools/claims-v3/e151/session_e151.sh` on the box: the check, the preflight, the
   start config read, the stop-path test, the smoke and its gate, the queue, the end config read.
5. **Collect** on the Intel: the raw blocks copied into the data directory, then `collect_e151.sh` on that copy; the README results
   first; the clause dropped or released.

## Files

`README.md` (this), `railfilter_e151.py` (the registered filter), `make_predictions_e151.py` → `predictions-e151.json` (the freeze, with
every file's sha256), `e130-items.json` (E130's, unchanged), `e151_common.py`, `run_e151.py`, `block_e151.sh`, `queue_e151.sh`,
`session_e151.sh`, `preflight_e151.sh`, `check_e151.py`, `smoke_gate_e151.py` (the card files), `reduce_e151.py`, `score_e151.py`,
`collect_e151.sh`, `telemetry_max_e151.py`, `e145_under_filter.py` → `e145-filtered/` (E145's data under the filter),
`selftest_e151.py` → `selftest-e151.txt` (the desk files), `dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`, `dmcmd-audit-desk.txt`.

## Amendments

*(none)*
