# E137: in fp16, a random sign's rest on zero products goes with the accumulators differing (1.00 ± 0.06) and almost none of it with the sums changing (−0.00 ± 0.06), on tiles matched in alternations, six kept passes; M4's fp16 sign term holds out of sample at 0.13 W rms (aifoundry1 card 1, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 5, "Where a random sign's ~5 W goes"**, as [E128](../2026-11-02-e128-fp16-signs/README.md) left it: "fp16's rest ... the part that goes with the sums changing ... not established", E128-R8 and R9 INCONCLUSIVE at two passes. Q137 (the owner's words, Mon 2 Nov 2026 ~15:20 PST: "The overall goal is to be able to predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible").*

*Mon 2 Nov 2026 (week 45), lane `a1c1-q137`. Pre-registered in `a3e9d32d` (committed 15:36:38 PST and pushed by commit_lab before the next command at 15:36:49, before the claim at 15:37:58 and the first device access at 15:38:09): [`tools/claims-v3/e137/E137.md`](../../../../tools/claims-v3/e137/E137.md), frozen numbers in [`predictions-e137.json`](../../../../tools/claims-v3/e137/predictions-e137.json), the set-aside rule written there first. No amendment. Collected and scored on the Intel at 16:13 PST by the registered `collect_e137.sh`, unchanged.*

## Results

**In plain words.** Seven passes ran, every block `ok`, 196 runs; E78's gates set one pass aside (13710: `int8.zeros` departs +0.279 W from its straight line, against 0.25 W), so the primary reading S1 keeps **six passes** (13711–13716) and carries every verdict (four were needed; S2 and S3 were not reached). Every interval below is t(0.975, 5) = 2.571 over those six. **(1) fp16's rest is located on the matched tiles too (R1 MOST, R2 ALMOST NONE).** On zero products with B's random signs, holding the 256 accumulators at the walking tile's op-end sums (`b_B_zm` over `z_s`) carries **1.001 ± 0.055** of B's rest, and walking at those sums with the same alternations (`b_B_wm` over `b_B_zm`) carries **−0.001 ± 0.055**, inside ±0.10. With R3 (E108's design ported) MOST again at **1.026 ± 0.053**, E128's frozen sentence for fp16 — "fp16's rest is located as fp32's is: most of B's rest goes with the accumulators differing", which asked R7 and R8 both MOST — is now met, and with R9's ALMOST NONE the fp16 half of the sums-changing sentence too. **(2) The sign term of M4 predicts these contrasts out of sample (R7 PASS):** its seven frozen fp16 sign contrasts lie inside their 95% half-widths, rms error **0.125 W**, against 0.211 W on E128's two passes of the same contrasts (post hoc). **(3) The session matches its predecessors:** the step 4.80 ± 0.17 W (R5 PASS against E108's 4.98), M4 on the eight items 0.13 W rms (R6 PASS), the session tie (S1 PASS), every item 0.1–2.1% above E128's watts on the same card (median 1.0105).

| rule | quantity, per pass | verdict | measured (6 passes) | M4 | E128 (2 passes) |
|---|---|---|---:|---:|---:|
| **E137-R1** (E128-R8 again) | matched: (`b_B_zm` − `z_s`) / (`b_B_wm` − `z_s`) | **MOST** | 1.001 ± 0.055 | 1.042 | 0.926 ± 0.307 |
| **E137-R2** (E128-R9 again) | matched: (`b_B_wm` − `b_B_zm`) / (`b_B_wm` − `z_s`) | **ALMOST NONE** (dips kept and leak 0: INCONCLUSIVE) | −0.001 ± 0.055 | −0.042 | 0.074 ± 0.307 |
| **E137-R3** (E128-R7 again) | E108's design: (`b_B_z` − `z_s`) / (`b_B_w` − `z_s`) | **MOST** | 1.026 ± 0.053 | 1.045 | 1.006 ± 0.119 |
| **E137-R4** | R1's share less R3's | **INCONCLUSIVE** (ALIKE at leak 0.3803) | −0.026 ± 0.103 | −0.004 | −0.080 ± 0.188 |
| **E137-R5** | the step, `signs` − `ones` | **PASS** (E108 4.981 ± 1 W) | 4.802 ± 0.173 W | 4.854 | 4.697 (one pass) |
| **E137-R6** | M4 on the eight items | **PASS** (≤ 0.60 W) | rms 0.130 W, bias +0.089 W | | |
| **E137-R7** | M4's seven fp16 sign contrasts | **PASS** (all inside, rms ≤ 0.30 W) | rms 0.125 W, 0 of 7 outside | | |
| **E137-R8** | against E128, per share | **INCONCLUSIVE** (no share FAILs) | d +0.075, −0.075, +0.020; h 0.312, 0.312, 0.130 | | |
| **E137-S1** | session tie against E82 | **PASS** (FAIL at leak 0.545 and 0) | `fp32.randn` 23.97, `fp16.randn` 21.57, `anchor_pi` 8.17, `int8.full` 6.94 W | | |

(`scored.json` › `primary.rules`, `primary.quantities`; `results.md`.) R8 cannot pass while E128's half of each interval is t(0.975, 1)-wide: every share's d lies inside E128's own interval, and none FAILs.

**The watts behind the shares** (W over fp16's zeros, board; rail post hoc, [`posthoc_e137.txt`](posthoc_e137.txt) A):

| contrast | board | minion rail | M4 |
|---|---:|---:|---:|
| `z_s` → `b_B_zm`: the accumulators differing (matched) | 3.321 ± 0.130 | 2.817 ± 0.261 | 3.398 |
| `b_B_zm` → `b_B_wm`: the sums changing, same alternations | 0.002 ± 0.193 | −0.022 ± 0.182 | −0.136 |
| `z_s` → `b_B_wm`: B's rest on zero products (matched) | 3.323 ± 0.166 | 2.794 ± 0.238 | 3.262 |
| `z_s` → `b_B_z`: the accumulators differing (E108's design) | 3.692 ± 0.119 | | 3.532 |
| `z_s` → `b_B_w`: B's rest (E108's design) | 3.600 ± 0.131 | | 3.379 |
| the step, `ones` → `signs` | 4.802 ± 0.173 | | 4.854 |

On the rail, which the board meter's dips do not touch, the two matched shares read 1.009 ± 0.064 and −0.009 ± 0.064 (post hoc, no rule). Pooled with E128's two passes (a reported arm, eight passes): 0.982 ± 0.048 and 0.018 ± 0.048, the same bands.

**The arms** (`results.md`, Arms): R1 and R3 read MOST at every arm; R2 reads ALMOST NONE at five of seven and INCONCLUSIVE at two, each with five passes — dips kept (−0.067 ± 0.376: card 1's meter dips widen every interval, and its span gate set 13714 aside too) and no leakage correction (+0.020 ± 0.086, its upper end 0.106 past 0.10); no arm reads SOME or NEGATIVE. S1 fails at the leakage arms 0.545 and 0 (arm-sensitive); E128's S1 failed at 0.3803, 0.545 and 0.

## What it changes for predicting the power of signed data in fp16

**The sign term.** M4 prices a tile from the bench's toggle counts (its core, bus and rest terms, beside the clocked floor), with coefficients fitted on E78 alone and frozen before E95; the counts follow the lane bits a random sign makes differ, and it has **no term for the running sum changing** as such. Item 5 left open whether such a term was missing. On tiles whose alternation sequences are identical micro-op for micro-op, the sums changing cost **0.002 ± 0.193 W** of a 3.32 W rest (share −0.001 ± 0.055), so the answer in fp16, as in fp32 on the rail, is **no term is missing**: the sign cost on zero products is the accumulator-bit term, about **32.7 ± 1.3 fJ per differing lane C-read and result bit** on the matched held tile, 44.6 ± 1.4 fJ on E108's design (post hoc, [`posthoc_e137.txt`](posthoc_e137.txt) B, E128's formula; E128 read 30.1 and 42.0 fJ). **Out of sample:** M4's frozen predictions for the seven fp16 sign contrasts miss by **0.125 W rms** (mean +0.073 W, every one inside its 95% band; R7), where E128's two passes of the same contrasts missed by 0.211 W rms with intervals up to ±1.08 W (post hoc, C). The per-item error, 0.130 W rms with M4 0.09 W low on average (R6), is the size of the card-to-session drift (E137's items read 1.0% above E128's on the same card). So for predicting the power of signed fp16 data at 600 MHz: use M4's lane-bit terms as frozen; add nothing for the sums changing; expect ±0.13 W on a sign contrast of 3–5 W. What stays open: R4 (whether E108's design and the matched one give the same share, −0.026 ± 0.103) is not resolved; this is designed tiles on one card at one clock; heat is not measured here (the die is held at 58–59 °C by the launch rule).

**For the blog's kinds table:** fp16 × random signs on zero products, B's rest: **3.32 ± 0.17 W** at 600 MHz on card 1 (matched tiles), **1.00 ± 0.06** of it with the accumulators holding different values and **−0.00 ± 0.06** with the sums changing; the fp16 sign step 4.80 ± 0.17 W.

## What ran

All through E137's session script on aifoundry1 card 1 (`V3_DEVICE=1`, `etsoc-shire1.lock`), 600 MHz in all 19,335 samples. **15:38:08 PST** `check_e137.py` HARNESS OK (19 files), the device-command preflight GO; **15:38:09** the session-start config read (65 W / 65 °C / 600 MHz / 499 mV, `low_power`); the smoke 13701 (six 2 s runs, 546.001 cycles an op, 0.5992–0.5995 GHz, the gate PASS, 15:38:49); passes **13710–13716**, 263–280 s each, 28 recorded runs each (196, none skipped by the launch rule, none failed a run gate); the queue ended at T0 + 2,026 s (16:11:54) with all seven passes done; **16:11:54** the session-end config read (65 W / 65 °C / 600 MHz / 499 mV, `managed_power`). Every block's two config reads read 65 / 65; nothing was set. Device access 15:38:09–16:11:54, **33.75 card-minutes** of the 60 registered. et-who showed no holder on either card at the launch and at the end. The day's one post in `#community-lab` (message 1566837317765963987) gained this card's clause `using aifoundry1 card 1 for 1.5 h, until ~17:07 PST` at 15:37:58 (beside aifoundry3's; the first try was refused with exit 7 because another lane had just rewritten the post, and was rebuilt from its text) and lost it at 16:12:37 (aifoundry3's and aifoundry2's clauses kept): 34.7 minutes claim to release. Collected at 16:12–16:13 PST (`rsync` at nice 19 on the box, 2.9 MB) after the session ended.

## Registered against what happened

| | registered | what happened |
|---|---|---|
| passes | 13710–13716, at most seven; the budget rule decides; four kept needed | seven ran; S1 kept six (13710 set aside by an int8 anchor gate); every rule scored |
| runs | 28 a pass | 28 in every pass, 196 |
| set-aside | S1, then S2, then S3 if fewer than four | S1 kept six; S2 and S3 not reached. The relaxed reading (`e137-relaxed.json`) keeps all seven and is reported only |
| stops | board ≥ 68 W, any shire ≥ 72 °C | never near: board at most 60.68 W (7.32 W under the stop, 14.32 W under the PMIC's 75 W alarm), the shires' mean at most 62 °C, no shire above 65 °C (the PVT's running high, carried from before the session) ([`desk/telemetry-max-e137.txt`](desk/telemetry-max-e137.txt)) |
| budget | at most 60 card-minutes | 33.75 |
| expectations | R1 MOST; R2 ALMOST NONE or INCONCLUSIVE; R3 MOST; R4 ALIKE or INCONCLUSIVE; R5–R7 PASS (R7 or INCONCLUSIVE); R8 PASS or INCONCLUSIVE; S1 PASS | as expected in every rule |

## Device commands sent

The nine READs of E128's README § Device commands sent, classified at et-platform `836a4ab` (BL2 0.22.0, the build card 1 reports): `ettelem config` (commands 25, 21, 23, 53, 32) at the session's start and end and at both ends of each of the eight blocks, 18 reads; `ettelem sample --seconds --every-ms` (33, 60, 27, 31, 32, 53) for 19,335 samples plus `lib.sh`'s `die_c` reads. Commands 32 and 31 read PMIC voltage registers (2 and 9 I2C reads), allowed by the owner's rule of 2 November 2026. Every call went through E128's `ettelem_guard.sh` (byte-identical, checked by `check_e137.py`); the drain to the vendor tool was refused by the block; **no WRITE was sent**: no statistics reset, no log-level set, no firmware-revisions query, no residency read, no set. Q136(w)'s checker over every file the session ran read GO, 32 send sites, all READ, on the Intel before the freeze ([`desk/dmcmd-preflight-e137.txt`](desk/dmcmd-preflight-e137.txt)) and on the box before the first device access (`logs/dmcmd-preflight.txt`, `logs/session.log`). The workload host opened only the ops node (DMA to device DRAM, kernel launches).

## Files

- Reduction and scores (the registered `collect_e137.sh`, unchanged): `e137.json` (primary), `e137-relaxed.json` (the set-aside reading), the arms `e137-{dipskept,gatesoff,auto,leak0.1994,leak0.3803,leak0.545,leak0}.json`, each with `runs-*.csv`, `reduce-*.txt` and `.log`; `scored.json`, `results.md`, `score.log`, `code.sha256`.
- Raw: `aifoundry1-c1/e137/p13710`–`p13716` and `e137-smoke-p13701`; `logs/` (the session's log, its queue log, both session config reads, the box's preflight and binaries' hashes).
- Post hoc, no rule depends on them: [`posthoc_e137.txt`](posthoc_e137.txt) from `tools/claims-v3/e137/posthoc_e137.py` (the rail, the lane bits, the sign term before and after, E128 beside); [`desk/telemetry-max-e137.txt`](desk/telemetry-max-e137.txt) from `tools/claims-v3/e137/telemetry_max_e137.py`.
- Desk, before the run: `desk/selftest-e137.txt` (14 of 14), `desk/desk-reduce-check-e137.txt`, `desk/dmcmd-preflight-e137.txt` and `.md`, `desk/box-setup-e137.txt`.

## Corrections after re-derivation (Mon 2 Nov 2026)

At the desk after the results commit (`df05d9f3`), every headline number was re-derived without E137's reducer or scorer, from `runs.csv` (the primary's run rows), `predictions-e137.json`, the telemetry and the session's config reads ([`desk/rederive-e137.py`](desk/rederive-e137.py), [`desk/rederive-e137.txt`](desk/rederive-e137.txt)). Every number agrees to the digits quoted: 13710's `int8.zeros` departure +0.279 W (the only zeros line past 0.25 W; 13715's +0.207 W is under it); the shares 1.0008 ± 0.0553, −0.0008 ± 0.0553, 1.0265 ± 0.0529 and their difference −0.0257 ± 0.1032; the step 4.8023 ± 0.1732 W; R7's seven errors (rms 0.1251 W, mean +0.0731 W, all inside), R6's rms 0.1298 W and bias +0.0893 W; the session tie's four cells; 19,335 samples, all at 600 MHz, board at most 60.68 W, the shires' mean at most 62 °C; 33.75 card-minutes; 32.7 fJ per differing lane bit; the median ratio to E128's items 1.0105. Every block's two config reads, and the smoke's, read 65 W / 65 °C / 600 MHz. Three faults in this README's wording, corrected here, no number or verdict changed:

| | what was wrong | what changed |
|---|---|---|
| C1 | The arms paragraph said S1 fails at leak 0.545 and 0 "as at E128"; E128's S1 failed at 0.3803 too (E128 `results.md`, E128-S1) | It now says so |
| C2 | The sign-term paragraph said M4 prices a sign by "C-read and result bits ... store bits"; M4's terms are the bench's core, bus and rest toggle counts beside the clocked floor (E128.md, M4's table), which those lane bits drive but are not named as | Reworded to M4's own terms |
| C3 | The header gave the registration's push as 15:36:40 PST; the commit is 15:36:38 and commit_lab's push ended before the next command at 15:36:49 (no push time is recorded) | It gives those times |
