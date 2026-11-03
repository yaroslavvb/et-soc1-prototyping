# E148: two A rows put back 0.16 ± 0.10 W of int8's no-issue excess - the A path is excluded as its per-row carrier; with equal per-op work in the two formats, TenC's read-address walk is the registered reading that holds (W1 WALK, per cycle excluded by 0.001 W); one row removes 0.75 ± 0.08 W (Q138, aifoundry1 card 1, 600 MHz, ten passes)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 11, "int8
zeros' extra 0.61 W"**, the complaint this answers: with nothing issued, int8's TensorFMA loop costs 2.11 W over idle against fp32's 0.38 W on
aifoundry3 (E109) and 1.57 ± 0.21 W more than fp32's on this card (E124's Y1), and the item's open part is "where the 1.7 W goes among what int8
alone runs every cycle ... and the premise of E129's split". It builds on [Q136(c)](../2026-11-02-q136c-tima-bench/README.md) (the TIMA bench's
counts: TenC's reads, the TIMA controls, TenTMP's staging, the scratchpad's 64-bit A reads), [E129](../2026-11-02-e129-int8-noissue/README.md)
(this card: one A row removes 0.70 ± 0.42 W, V1 INCONCLUSIVE) and [E124](../2026-11-01-e124-int8-zeros-replicate/README.md) (this card's
frame and per-read ceilings).*

*Mon 2 Nov 2026 (week 45), Q138, lane a1c1-e148-int8-excess. Pre-registered in [`tools/claims-v3/e148/README.md`](../../../../tools/claims-v3/e148/README.md)
with [`predictions-e148.json`](../../../../tools/claims-v3/e148/predictions-e148.json), committed as **`19eb22a4`** at 22:10:00 PST and pushed by
`commit_lab.sh` before the claim (22:11:45 PST) and before any device opened (22:11:58). **aifoundry1 card 1** (`V3_DEVICE=1`, its own lock), release
1.4.0 (BL1 and BL2 0.22.0), after [E142](../2026-11-02-e142-blind5-card1/README.md) released it at 21:35:48. `ettelem config` was read 26 times under
card 1's lock with `timeout 10`, through E128's allow-list (the session's start, 22:11:58, and end, 22:45:56, and both ends of the stop-path test, the
smoke and every pass): **TDP 65 W, threshold 65 °C, 600 MHz, 499 mV in every read** (power state `low_power` 6 times, `managed_power` 20). **Nothing
was set and no WRITE was sent** (§ Device commands sent; `since_reset_ms` −1 in all 19,056 samples). **Card session 22:11:58–22:45:56 PST, 34.0
card-minutes of the 40 allowed**: the stop-path test 14802, the smoke 14801 and **ten passes, 14810–14819 (172–206 s each), all kept**. The card was
claimed at 22:11:45 by rewriting the day's one card post in `#community-lab` (message `1566837317765963987`) and released at 22:46:37 by rewriting it
again (§ How it ran).*

**In plain words.** With nothing issued, an int8 matmul loop on this chip still draws about 1.6 W more than the same loop in fp32. This morning one
row of A took 0.7 W of that away, which left open what the removed part follows: the accumulator memory's changing read address (the "walk"), or the
way int8 stages A. Two rows of A separate them, because the walk turns on while the A staging falls. **Two rows put back 0.16 W, so the A staging
is excluded as the carrier, and the walk is what holds if the two formats spend the same energy per operation** (measured only to ±63 pJ, which
could carry the 0.16 W instead). Counted the registered way (reads at a new address) the walk over-predicts that by about
two times at this session's own scale; counted in address bits that change, a reading chosen after the data, it predicts 0.17 W. More than half of
the excess, 0.88 W, stays at one row: work int8 does every cycle that no shape here separates.

## Results

**All ten passes kept on the registered primary** (E78's `reduce_e78.py` unchanged through `reduce_e148.py`: leakage frozen at 0.2414 W/°C, card 1's
launch-gap dips removed, 1–10 samples a pass, E78's run and pass gates, card 1's 65/65 config gate): 140 runs, none failing a gate, a median of one
heat a launch (at most two). The relaxed reduction keeps the same ten. ([`scored.json`](scored.json) › `n_passes`, `which_reduction_scores` =
"primary"; [`e148.json`](e148.json) › `passes_set_aside` = [])

1. **Two A rows put back D21 = N2 − N1 = +0.159 ± 0.096 W** (95% +0.063 to +0.256; ten passes, paired inside each). **W1 reads WALK**: the walk's
   frozen range (+0.118 to +0.474 W) overlaps it, the A path's (−0.681 to −0.170 W) and per cycle's (+0.026 to +0.062 W) do not. **The per-cycle
   exclusion is by 0.001 W** (D21's lower bound 0.0629 against the range's top 0.0619); under the leakage-`auto` arm (0.141 W/°C, fitted on the
   session's 91 runs) D21 is +0.141 ± 0.090 W and W1 reads INCONCLUSIVE (C and W consistent). **W2 RISES** in every arm: two rows cost int8 more than
   one, so **int8's A staging (TenTMP and the scratchpad's 64-bit A reads), which falls at two rows, is excluded as the per-row carrier**.
   **Reading D21 as the walk assumes equal per-op work in the two formats**, E129's premise: both op rates fall by about a third from one row to two,
   so a per-op difference Δe enters D21 as about −3.4 × 10⁹ × Δe, and E129 measured Δe only to −4 ± 63 pJ (`one_row.e_op_diff_at_r1_rate_w`,
   −0.04 ± 0.62 W at the one-row rate), which allows +0.02 ± 0.21 W of D21. The A path's exclusion holds at that allowance (D21 would still lie
   above −0.17 W); the walk's share of D21 is then about +0.14 ± 0.23 W (the two half-widths in quadrature), not resolved from zero.
   (`scored.json` › `rules.W1`, `rules.W2`; `scored-auto.json` › `rules.W1`; E129 `scored.json` › `one_row`)
2. **N2, a shape no model was fitted on, against what each frozen reading predicted for it.** Measured, N2 = S(`m0r2.int8.zeros`) −
   S(`m0r2.fp32.zeros`) = **1.043 ± 0.087 W**. Predicted (this session's N1 plus each reading's frozen D21): the walk 1.180 W (error −0.137 W), per
   cycle 0.927 W (+0.115 W), the A path 0.458 W (+0.585 W); the bench at its own constants in the card's order 0.082–0.162 W (+0.88 to +0.96 W).
   (`scored.json` › `reported.N2_out_of_sample`)
3. **E129 replicates, now resolved** (T1 PASS ×2, Y1 PASS). With nothing issued, int8's sixteen-row loop costs **N = 1.631 ± 0.049 W** more than
   fp32's (E129 1.566, E124 1.567); with one A row **N1 = 0.884 ± 0.077 W** (E129 0.865 ± 0.357); so **one A row removes N − N1 = 0.747 ± 0.084 W**
   (E129 0.701 ± 0.421). V1 on this session alone is INCONCLUSIVE (N1's 0.807–0.960 W straddles N/2 = 0.815 W); **V1p, pooled with E129's three
   passes (13), reads PER-CYCLE**: N1 − N/2 = +0.071 ± 0.068 W, its lower bound +0.004 W, so more than half of the excess stays at one A row. Under
   leakage `auto` both read PER-CYCLE. (`scored.json` › `rules.T1`, `rules.Y1`, `rules.V1`, `rules.V1p`)
4. **The silicon keeps the RTL's schedule at two rows** (R6 PASS ×6). Every arm's cycles per op equal the frozen prediction, the bench's plus E109's
   7.75: **`m0r2` 96.0 (fp32) and 94.0 (int8)**, a schedule no card had run, the bench's 88.25 and 86.25 + 7.75 to the cycle; `m0` 544.001 / 318.001;
   `m0r1` 62.0 / 62.0. The smoke read the same. (`scored.json` › `rules.R6`; [`logs/session.log`](logs/session.log), the smoke lines)
5. **The registered two-term solve** (reported, no verdict) puts N − N1 and D21 on the two counts at once: **p_w = 75.5 ± 16.8 fJ a TenC read at
   a new address and p_t = 3.43 ± 1.68 pJ a 64-bit A read**. That p_t is 5.6 times the most any scratchpad read can cost on this card at fp32's own
   no-issue level (0.61 ± 0.13 pJ, E124 `extras.json` › `reported.read_ceiling_fp32_pj`), so the two-term reading needs int8's A staging to cost far
   more than a read. (`scored.json` › `reported.two_term`)
6. **Post hoc, deciding nothing** ([`posthoc/posthoc.txt`](posthoc/posthoc.txt)): at this session's own N − N1, the walk counted as the registration
   counted it, reads at a new address (× 0.4225), predicts D21 = 0.316 W and is excluded (D21 minus it −0.156 ± 0.077 W). Counted in **TenC
   read-address bits that change** (the bench's `raddr_tog`: 7,680 an op at sixteen rows, 1.875 bits a change, and 512 at two rows, one bit a change;
   × 0.2254 a second), a count chosen after the data were seen, it predicts **0.168 W, consistent (−0.009 ± 0.085 W)**, with no A-path term. Its
   one-term price is **50.5 ± 5.7 fJ an address-bit toggle** (or 94.8 ± 10.6 fJ a read at a new address; E129's post hoc was 89). A per-cycle share
   on its own (× 0.0506 of N1) is excluded (+0.115 ± 0.098 W). Three rows would test the toggle count with a gap of 0.16 of the walk's sixteen-row
   share (0.542 against 0.385), but at three rows the formats' op rates differ by 16%.

**What it changes.** Item 11 narrows on both of its open parts. **The per-row part:** one A row removes 0.75 ± 0.08 W, and a second row puts back a
fifth of that while int8's A staging falls below one row's, so the staging is excluded as its carrier (W2, every arm) and TenC's read-address walk
is the registered reading that holds (W1 WALK on the primary; the per-cycle reading's exclusion rests on 0.001 W and fails under the leakage arm).
**The premise of E129's split** (equal per-op work in the two formats) is not tested further, and the walk's reading of D21 needs it too: a per-op
difference between the formats at E129's ±63 pJ could carry D21 instead. A run that measures each format's per-op work at one and two rows (a K = 8
partner for each, as E109's `m0k8`) would remove it. **The per-cycle part:** pooled over 13 passes, more than half of N
stays at one row (V1p PER-CYCLE, lower bound +0.004 W): about 0.88 W of int8's 1.63 W is work it does every cycle whatever the walk, and nothing
here separates TenC's reads as such, the TIMA controls and the core.

## What it does to predicting power and heat

**The term measured:** int8's no-issue floor, the part of an int8 matmul's power that no data and no issued micro-op sets, 1.63 W over fp32's on this
card at sixteen rows. Before E148 no model term carried it and its shape-dependence was unknown (E129's split INCONCLUSIVE). After E148 it has a
two-part form: **N(shape) ≈ N1 + (a price) × (TenC's read-address activity a second)**, with N1 ≈ 0.88 W the per-cycle part at the one-row rate and
the walk part 0.75 W at sixteen rows.

**Out-of-sample error on N2** (two rows, a shape nothing was fitted on; measured 1.043 ± 0.087 W):

| predictor, frozen before the run | predicted N2 | error |
|---|---:|---:|
| the bench at its own constants, card order (Q136(c)'s pricing) | 0.08–0.16 W | **+0.88 to +0.96 W** |
| per cycle only (N1 scaled by the TIMA controls) | 0.927 W | +0.115 W |
| the walk, in reads at a new address, at E129's N − N1 (registered W) | 1.180 W | −0.137 W |
| the A path (registered T) | 0.458 W | +0.585 W |
| *post hoc:* the walk in address-bit toggles at this session's N − N1 | *1.052 W* | *−0.009 W* |

So the registered readings predict a new shape's floor to about 0.12–0.14 W (of 1.04 W), against the bench's 0.9 W, and the post hoc toggle count to
0.01 W, in sample for its choice of count. Every row but the bench's assumes equal per-op work in the two formats (result 1). **Heat** follows power through card 1's die rise per board watt (M7's H2, 0.1151 °C/W): a 0.16 W difference
is 0.02 °C, below what the 4.5 s readout resolves, so E148 scores power only.

## The arms (primary reduction)

D is over the format's zeros (interpolated between the pass's three zeros anchors) and S over the idle bracket, ± 95% over 10 passes (t 2.262).
"Cycles" is the median over the kept runs. Source: `e148.json` › `items`, `per_pass`; [`readme-numbers.txt`](readme-numbers.txt).

| item | cycles | ops/s (10⁹) | D, W | S, W |
|---|---|---|---|---|
| `fp32.zeros` | 546.001 | 1.1209 | 0 | +1.629 ± 0.026 |
| `int8.zeros` | 318.001 | 1.9248 | 0 | +2.236 ± 0.023 |
| `anchor_pi` | 546.001 | 1.1208 | +8.138 ± 0.024 | +9.846 ± 0.071 |
| `m0.fp32.zeros` | 544.001 | 1.1251 | −1.529 ± 0.058 | +0.132 ± 0.044 |
| `m0.int8.zeros` | 318.001 | 1.9247 | −0.441 ± 0.053 | +1.762 ± 0.048 |
| `m0r1.fp32.zeros` | 62.0 | 9.8640 | −0.386 ± 0.058 | +1.287 ± 0.052 |
| `m0r1.int8.zeros` | 62.0 | 9.8646 | −0.046 ± 0.032 | +2.171 ± 0.073 |
| **`m0r2.fp32.zeros`** | **96.0** | 6.3751 | −0.789 ± 0.062 | **+0.908 ± 0.054** |
| **`m0r2.int8.zeros`** | **94.0** | 6.5108 | −0.319 ± 0.043 | **+1.951 ± 0.059** |

Idle 33.02 W. Going from one row to two lowers both formats' level, fp32's by 0.379 ± 0.063 W and int8's by only 0.220 ± 0.090 W: B's traffic falls
with the op rate in both, and int8 alone adds the walk back. (`scored.json` › `stats.r2_over_r1_fp32`, `stats.r2_over_r1_int8`)

## The registered rules against the data

`scored.json` is `score_e148.py`'s output with `predictions-e148.json` on the primary, chosen by the set-aside rule over the relaxed reduction. The
arms: dips kept, leakage `auto`, and the relaxed reduction.

| rule | registered line | **E148 (primary, 10 passes)** | dips kept | leakage `auto` (0.141 W/°C) | relaxed |
|---|---|---|---|---|---|
| **W1** (primary) | D21's 95% interval against the frozen ranges W, T, C | **WALK** (+0.159 ± 0.096; W consistent, T and C excluded) | WALK | **INCONCLUSIVE** (C, W; +0.141 ± 0.090) | WALK |
| W2 | D21's lower bound > 0 | **RISES** (+0.063) | RISES | RISES | RISES |
| R6 | \|measured − predicted\| ≤ 2 cycles | **PASS ×6** (every difference ≤ 0.001) | PASS ×6 | PASS ×6 | PASS ×6 |
| Y1 | N's lower bound ≥ 0.84 W | **PASS** (+1.631 ± 0.049) | PASS | PASS | PASS |
| V1 | N1 against N/2 | **INCONCLUSIVE** (0.884 ± 0.077 against 0.815) | INCONCLUSIVE | PER-CYCLE | INCONCLUSIVE |
| V1p | N1 − N/2, pooled with E129's 3 passes | **PER-CYCLE** (+0.071 ± 0.068, 13 passes) | PER-CYCLE | PER-CYCLE | PER-CYCLE |
| T1 | N, N1 within 0.5 W of E129's | **PASS ×2** (1.631 vs 1.566; 0.884 vs 0.865) | PASS ×2 | PASS ×2 | PASS ×2 |

**One verdict moves with an arm: W1** (and V1). The dips-kept arm reproduces every N, N1, N2 and D21 exactly; leakage `auto` lowers D21 by 0.018 W
and brings the per-cycle range back inside its interval. The registered primary carries the verdict, and the margin is stated where it is used.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | committed and pushed before the claim and the first launch | `19eb22a4` committed 22:10:00 PST and pushed by `commit_lab.sh` before the claim (22:11:45); first device process 22:11:58 (the opening config read) |
| desk | the bench run and its identity check; the predictions; the self-test; the preflight; `bash -n`; the reducer's mechanical run. On the box: `check_e148.py`, the preflight, `bash -n`, a stub queue, `V3_DRY` of the stop test, smoke and pass 14810 | [`selftest.txt`](../../../../tools/claims-v3/e148/selftest.txt) PASS (A–C); [`dmcmd-audit.txt`](../../../../tools/claims-v3/e148/dmcmd-audit.txt) GO; the box's checks 22:08:02–22:09:25 PST ([`logs/desk/`](logs/desk/)) |
| stop test | before the smoke: the die, board and watcher stops each exit 6 on a live sample, no launch | 22:11:59–22:12:05: die stop on a sample read 0.102 s after it was taken, board 0.084 s, watcher 0.031 s; rc 6 three times ([`aifoundry1-c1/e148-stoptest/p14802/`](aifoundry1-c1/e148-stoptest/p14802/)) |
| smoke | seven items, 2 s runs; E109's gate | 22:12:14–22:12:57; every item 6 launch records, all `ok`, `tensor_errors` 0: SMOKE-GATE PASS; `m0r2` at 96.0 and 94.0 cycles |
| passes | 14810–14819 as the budget allows; about 600 s each expected | **all ten**, 172–206 s each (rc 0); the queue's rule ran out of passes, not budget (22:45:56, T0 + 2,038 s, limit T0 + 2,250 s) |
| kept | the primary carries if ≥ 3; else the relaxed one | **10 of 10** by E78's gates; the relaxed reduction keeps the same 10 |
| runs | 14 a pass | 140 of 140 ran and all are kept; a median of 1 heat a launch, at most 2 |
| stops | `build/e148/STOP`; board ≥ 66 W or a minion-shire reading ≥ 72 °C on a live sample (before every launch, every 0.1 s while waiting, and by the in-run watcher); run_e78's `--max-c 72`; another user's device process or this card's lock | none fired. In all 19,056 samples: board at most **59.79 W** (stop 66), the hottest-shire field 65 °C throughout (its latch; stop 72), the shires' mean 51–61 °C, the PMIC's reading at most 61 °C, 600 MHz, `since_reset_ms` −1 ([`telemetry-max.json`](telemetry-max.json)) |
| budget | at most 40 card-minutes, first config read to last; no session after 23:00 PST; passes end by 23:45 PST | **34.0** (22:11:58–22:45:56); claim to release 34.9 min (22:11:45–22:46:37) |
| config | read at both ends, never set | TDP 65 W, 65 °C, 600 MHz, 499 mV in all 26 reads |

## Departures (dated)

- **Mon 2 Nov 2026, the passes ran three times faster than registered, so all ten fit.** The registration projected 600 s a pass from E129's cool
  morning (536–663 s, a median of 5–8 heats a launch). This session's die stayed warm, a median of one heat a launch, and the passes took 172–206 s.
  The queue's budget rule, unchanged, started every pass it had (14810–14819) and ended at T0 + 2,038 s, inside its T0 + 2,250 s limit. Recorded,
  not amended: no rule depended on the number of passes beyond the registered minimum of three.
- **The day's post's plan read lagged at the release.** `delete_msg.mjs --plan` gave the post's text without a clause that a later lane had added
  (aifoundry3's), so `edit_replace.mjs` with `EXPECT_TEXT` refused (exit 7), as its rule says; the release text was rebuilt from what the edit box
  held, dropping only this card's clause, and saved (§ How it ran).

## How it ran

22:08:02–22:09:25 PST, before the commit, on the box with no device opened: Python 3.12.3; `check_e148.py` HARNESS OK (25 files: E129's 20 reused
files and the 5 binaries, every one byte-identical to E129's freeze); the preflight GO; every script parsed; the queue's budget rule on a 1 s stub;
`V3_DRY` of the stop test, the smoke and pass 14810 ([`logs/desk/`](logs/desk/)). `et-who`: no process held a device node or card lock. 22:10:00 the
registration committed (`19eb22a4`); `commit_lab.sh` pushed it before the claim. 22:11:45 the claim: the day's one card post, which read
`<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, was rewritten to
`<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry1 card 1 for 1 h, until ~23:11 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
(`edit_replace.mjs` with `EXPECT_TEXT`, dry run, save, read back, under the discord lock). 22:11:58 `session_e148.sh` started detached on the box
(`setsid nohup`, T0 = the launch): the 23:00 gate; `check_e148.py` (HARNESS OK); the preflight (GO); `et-who` (no holder); the opening config read;
the stop-path test 14802; the smoke 14801 and its gate; `queue_e148.sh`; the closing config read at 22:45:56; `et-who` (no holder). The other lab user's
idle logins were present throughout; no other user's process, device node or card lock was seen (E78's departure D1 for `aifoundry1-c*`).

Each pass ran E78's two burn-in runs of π, then 14 registered runs: π first and last, each format's zeros once in each of three segments, and E148's six
arms dealt round-robin with seed `E148|aifoundry1-c1|<pass>`. Each run launched at a 58 °C die reading after a 59 °C preheat, with 2 s quiet and 4 s
FMA runs on all 1,024 minions. The waits on the box were four bounded `ssh … 'bash -s'` calls that read the session's log lines only; nothing was
copied off the box until the session had ended.

22:46:37 the release: the post then held three clauses (aifoundry2's, this card's and aifoundry3's, added meanwhile; the plan's cached source lagged,
so `EXPECT_TEXT` refused with exit 7 and the text was rebuilt from the edit box). It was rewritten to the two still held,
`<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry3 for 1 h, until ~23:40 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`,
every word of theirs kept, and the rendered post read the same at the save. 22:46:4x the data were collected to the Intel
([`collect_e148.sh`](../../../../tools/claims-v3/e148/collect_e148.sh), and the box's desk checks into [`logs/desk/`](logs/desk/)), then reduced and scored
with [`pipeline_e148.sh`](../../../../tools/claims-v3/e148/pipeline_e148.sh) (six seconds). `reduce_e148.py` checks the 20 reused files' sha256 against
the freeze before it reads anything.

## Device commands sent

Every command the run sent to card 1, classified at registration from the source of its running build: release 1.4.0, BL1 and BL2 0.22.0,
et-platform **`836a4ab`** (the version-matched revision of Q136(w)'s table, E129's dated note C1 and E142's audit of the same command set).
Q136(w)'s checker on every file the session runs read **GO: 32 send sites, 0 disallowed, no WRITE allowed**, at the desk
([`dmcmd-audit.txt`](../../../../tools/claims-v3/e148/dmcmd-audit.txt)) and on the box before the first device opened
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt), 22:11:58 PST). **The run sent no WRITE** (`since_reset_ms` −1 in every sample).

| # | sent by | command (id) | class (BL2 0.22.0, `836a4ab`, under `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| 1 | `ettelem config` (session start and end, each block's start and end) | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | READ: `thermal_power_monitor.c:339` → `thermal_pwr_mgmt.c:613`, a copy from SP RAM |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | READ: `:438` → `:665`, SP RAM |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23) | READ: `:48` → `:551`, SP RAM |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | READ: `performance.c:41` → `io_pll.c:907-960`, PLL register reads |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32) | READ: `thermal_pwr_mgmt.c:1142`, PVT reads and two `pmic_get_voltage` I2C register reads (allowed by the owner's rule of 2 November 2026) |
| 6 | `ettelem sample` (the 10 Hz sampler; `lib.sh`'s 1 s die reads) | `DM_CMD_GET_MODULE_POWER` (33) | READ: `:984`, SP RAM |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60) | READ: `performance.c:404` → `thermal_pwr_mgmt.c:2780`, SP RAM, no reset |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | READ: `:732`, PVT sensor reads |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31) | READ: `:1010`, nine `pmic_get_voltage` register reads (allowed) |
| — | `lib.sh:154`'s forwarded arguments (a possible `--reset-ms` = `DM_CMD_SET_STATS_RUN_CONTROL`, 62) | WRITE, conditional: **never sent** (the reviewed exception: `block_e148.sh:104` passes the file and the duration only, and `ettelem_guard.sh` refuses `--reset-ms`) | |
| — | `lib.sh`'s `drain_mgmt` (`dev_mngt_service`) | **never sent**: replaced by a refusal in `block_e148.sh` | |
| — | `sparsity_host` (E109's `build/e109`; E78's heater `build/sparsity`) | the Master Minion's device-ops: DMA writes and reads of device DRAM, kernel launches, an abort on a 6 s overrun: the workload, not a device-management command | |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads; they open no device node | |

Not sent: the statistics reset, the SP log level (67), `sptrace`, `dev_mngt_service`, the firmware-revisions query (14), a residency read, any
governor, TDP, threshold, clock or voltage set, any reset.

## What this cannot say

- **RTL, not silicon, and a later revision.** The walk and the A path are counted in core-et's later revision (Erbium), not the ET-SoC-1's own RTL;
  the silicon matching the bench's cycles (R6) shows the schedule carries over, not the energy of each event.
- **The per-cycle candidates stay together.** No shape separates TenC's reads as such, the TIMA controls and the core: all three run every int8
  cycle at the same rate in every arm here (and TenC's reads cancel in the card's order if fp32 reads TenC too, Q136(c) result 3).
- **W1's per-cycle exclusion is 0.001 W wide** and does not survive the leakage-`auto` arm; W2 (the A path's exclusion) survives every arm.
- **Equal per-op work in the two formats is assumed, not measured here.** No arm of E148 measures each format's per-op work; E129's estimate
  (Δe = −4 ± 63 pJ an op) allows ±0.21 W of D21, so the walk's share of D21 is not resolved from zero without the premise (result 1).
- **The readings are single-carrier readings.** Each puts all of E129's N − N1 on one event. The reported two-term solve fits both counts with two
  equations and no residual; the post hoc toggle count fits one count, chosen after the data. Neither is a test.
- **Two rows are not exactly equal-rate.** int8 runs 94 cycles an op and fp32 96, so int8 does 2.1% more ops a second. At Q136(c)'s fp32-level
  bounds that buys int8 at most about 0.02 W of TenB writes and 0.01 W of scratchpad bits (`predictions-e148.json` › `bench_per_s_card_order`), and
  at E129's per-op price (about 80 pJ an op) about 0.01 W: below D21's interval.

## Files

`e148.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the primary reduction); `scored.json`, `results.md`, `score.log` (`score_e148.py`; the set-aside rule
chose the primary); `e148-relaxed.json`, `scored-relaxed.json`, `results-relaxed.md` and logs (always run, not needed); `e148-dipskept.json`,
`e148-auto.json` with their `scored-*`, `results-*`, `runs-*`, `reduce-*` (the two arms); `readme-numbers.txt` (every number above, printed by
[`numbers_e148.py`](../../../../tools/claims-v3/e148/numbers_e148.py), written after the run); `telemetry-max.json`
([`telemetry_max_e148.py`](../../../../tools/claims-v3/e148/telemetry_max_e148.py), E142's, after the run); `posthoc/` (post hoc, deciding nothing:
`posthoc_e148.py` and its `posthoc.txt`/`posthoc.json`, and `bench_ladder_e148.py` with `bench-ladder.json`, the bench's walk counts at 1–16 rows);
`aifoundry1-c1/e148/p1481[0-9]/` (every pass's raw data: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_start.json`,
`config_end.json`, `manifest.txt`, `binaries.sha256`, `code.sha256`, `gen.sha256`, `configs.json`, `plan.json`, `run.log`, `block.json`);
`aifoundry1-c1/e148-smoke/p14801/`; `aifoundry1-c1/e148-stoptest/p14802/` (with `STOP.die`, `STOP.board`, `STOP.watch`, `stoptest.rc`); `logs/` (the
session, its two config reads with their times, the queue, the preflight, `binaries.sha256`, `T0`; `logs/desk/`, the box's checks before the claim).
The registration and code are in [`tools/claims-v3/e148/`](../../../../tools/claims-v3/e148/README.md).

Rerun from the repo root: `bash tools/claims-v3/e148/pipeline_e148.sh <out dir> docs/reports/data/2026-11-02-e148-int8-excess/aifoundry1-c1/e148/p1481[0-9]`
(needs `uv` for numpy). Post hoc: `python3 docs/reports/data/2026-11-02-e148-int8-excess/posthoc/posthoc_e148.py`.

## Blog sentences, each with its baseline, its card and its source

*Any line about the RTL is about its later revision (Erbium, core-et), not the ET-SoC-1's own.*

- An int8 matmul loop with nothing to multiply still draws 1.63 W more than the same loop in fp32 on this chip, and giving it a single row of A takes
  0.75 ± 0.08 W of that away, measured over ten independent passes. [aifoundry1 card 1, 600 MHz; `scored.json` › `stats.N`, `stats.N_minus_N1`]
- Adding a second row puts 0.16 W back, while the way int8 stages A falls below one row's: so the staging is not what costs, and if the two formats
  spend the same energy per operation, the accumulator memory's changing read address is the reading that holds. [aifoundry1 card 1; `scored.json` ›
  `rules.W1`, `rules.W2`; the premise, E129 `scored.json` › `one_row`]
- The open RTL predicted the two-row loop's timing to the cycle on silicon it had never been run on: 96 cycles an op in fp32 and 94 in int8.
  [aifoundry1 card 1; `scored.json` › `rules.R6`]
- Frozen before the run, the readings predicted the two-row excess to within 0.12–0.14 W of 1.04 W; the simulation's own fitted constants missed it
  by 0.9 W. [aifoundry1 card 1; `scored.json` › `reported.N2_out_of_sample`]
- Counting the accumulator address's changing bits rather than its changes, a count chosen after the data, prices the walk at about 50 fJ a bit and
  predicts the second row's 0.16 W to 0.01 W; a run at another row count would test it. [aifoundry1 card 1; `posthoc/posthoc.txt`]
- More than half of the excess, about 0.88 W, stays at one row: work int8 does every clock cycle whatever the address does. [aifoundry1 card 1,
  E129 and E148 pooled, 13 passes; `scored.json` › `rules.V1p`]
