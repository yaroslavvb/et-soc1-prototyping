# E125: E113's A-side ladder replicates on a second card — all seven verdicts and every number at the kinds matrix's card scale; a few low A bits cost nearly what B pays (Q134, aifoundry1 card 1, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 15, "Smaller, and carried"**, its A-side part (the complaint this answers: Q133 answered the A side's form for the quiet
partner on one card, with "another card" left open), and **item 6**'s clause on the A-side ladders. It replicates
[E113](../2026-11-01-e113-a-side-saturation/README.md) (aifoundry3 card 0). Corrected after verification the same evening, at
the desk, with no number or verdict changed: see [Corrections after verification](#corrections-after-verification-sun-1-nov-2026).*

*Sun 1 Nov 2026 (week 44), Q134, lane a1c1-e125-a-side. Pre-registered in
[`tools/claims-v3/e125/E125.md`](../../../../tools/claims-v3/e125/E125.md) with
[`predictions-e125.json`](../../../../tools/claims-v3/e125/predictions-e125.json), the scorer and its self-test,
**committed as `105f4601` at 20:12:35 PST and pushed by 20:12:38**, before the claim (the day's post rewritten 20:13:59–20:14:04
PST) and before the first launch (the smoke's, 20:14:23). The session ran **20:14:18 → 20:42:32 PST on aifoundry1 card 1** (`V3_DEVICE=1`, its own lock):
the smoke, pass 12500, then passes 12501–12508, **28.2 card-minutes** of the 35 allowed. 600 MHz, 499.0 mV. `ettelem config`, read
under card 1's lock with `timeout 10` at the session's start and end, read TDP 65 W, threshold 65 °C, 600 MHz, 499 mV both times
(power state `low_power` at the start, `managed_power` at the end, as E124 saw on this card). **Nothing on the card was set.***

## Results

**E113's answer replicates on a second card (Z: REPLICATES).** `score_e113.py`, unchanged, reads every one of E113's seven verdicts
again on card 1, over the seven passes the gates keep. ([`scored.json`](scored.json) › `rules`, `e125.Z`; [`report.md`](report.md))

1. **The layout matters on A** (P1 PASS). At the same number of flipping A bits, spread bits cost more than low bits at every k from
   2 to 16; at k = 8 **+2.740 ± 0.029 W** (94 SE). The contrast has E113's shape, its dip at k = 4 included: +0.184, +1.765, +1.137,
   +1.996, +2.740, +2.476, +0.633 W at k = 2, 3, 4, 6, 8, 12, 16 (E113 in the same frame: +2.837 at k = 8). (`scored.json` › `D1_A`)
2. **A curve in A's own summed single-bit prices is rejected again** (P2 REJECTED): **0.682 W rms** at a refitted W of 5.66 W,
   against 0.40 W to accept and 0.60 W to reject (E113: 0.708 W). The top rung, out of every fit, `alq_h23` = 7.307 ± 0.029 W, sits
   1.64 W (58 SE) above that W (E113: 54 SE). (`scored.json` › `rules.P2`, `D2_A.out_of_sample_alq_h23`)
3. **The mirror describes the A side better** (P3 PASS, P4 "which bits"). With c frozen at E70's 0.643, the mirror reads the seven
   spread rungs to **0.238 W rms** (registered ≤ 0.50; the frozen S_A curve reads 0.172 W there, so P3 alone does not separate the
   two laws, as in E113). Refitted on both layouts, **c = 0.6617 ± 0.0020** per pass reads the 15 rungs to **0.273 W**, against
   0.682 W for a curve in S_A and 0.865 W for the best any "how many" law can do. That c is fitted against E70's B rungs, measured
   on aifoundry3, so it carries the 3% card scale: at card 1's own scale it reads 0.68 (× 1.030), as E113's did on aifoundry3
   ([C1](#corrections-after-verification-sun-1-nov-2026)). (`scored.json` › `rules.P3`, `rules.P4`, `D2_A`)
4. **The A word's weight** (P5 PASS): per designed bit, A over B, **ρ(8) = 1.278 ± 0.019 (low) and 1.387 ± 0.010 (spread)**, both in
   the band, their difference **+0.109 ± 0.024** inside P5's 0.30. That difference is 4.5 SE from zero, so the two layouts do not
   share one ρ(8). This is a reading beside P5, not a registered rule; the desk finding predicted it
   ([C3](#corrections-after-verification-sun-1-nov-2026)). E113's passes, reduced the same way, read +0.124 ± 0.019 (§ Desk
   finding). (`scored.json` › `rho8`)
5. **E70 and the random pair** (P6 PASS, P7 PASS). E70's seven A rungs (aifoundry3) come back within −0.253 to +0.136 W (bands 0.6 W,
   1.0 W at the top), and `ls_h8` − `lq_h8` reads 3.698 ± 0.055 W against E70's 3.860. `nrd_a` / `nrd_b` reads **0.663 ± 0.002**
   (E113: 0.664). (`scored.json` › `replicate`, `nrd`)

**The numbers carry over at the kinds matrix's card scale (X: 21 of 21 PASS; the A rungs 16 of 16).** Each card-1 number was
predicted at E113's value (its passes in the same frame) divided by E82's fp32 card scale, s = 1.030 (a ratio at E113's value), and
tested with both sessions' 95% half-widths against a tolerance w (0.6 W a rung, 1.0 W at the top; 0.30 for ρ; 0.05 for the random
pair and c). The largest misses are `als_h16` −0.126 W, `alq_h8` +0.090 W and `alq_h23` −0.080 W. Fitted on its own, this ladder's
card scale is **1.031** (rms 0.058 W over 16 rungs), E82's 1.030 again. Against E113's registered numbers (dips kept) the same rules
read 19 PASS and 2 INCONCLUSIVE: `als_h6` and low-layout ρ(8), the two numbers the dips moved most. (`scored.json` › `e125.x_rules`,
`e125.x_A_rungs`, `e125.ladder_scale`, `e125.x_rules_registered`)

**A few low A bits cost nearly what the same bits cost on B (N1: SMALL-K EXCESS).** Inside one session, with the B rungs run in the
same passes, the A/B ratio of the same low mask is **0.960 ± 0.039 at k = 2, 0.930 ± 0.021 at k = 4 and 0.639 ± 0.009 at k = 8**.
N1 = (r2 + r4)/2 − r8 = **+0.306 ± 0.023** (95% [0.250, 0.362]; every pass +0.21 to +0.37), against the registered 0.20. So E113's
odd ratios near 1.0 at k = 2 and 4 were not only an artifact of comparing two sessions: the excess holds within one session, at about
three quarters of the size E113 read across sessions (0.415). Per designed bit that is ρ = 1.92, 1.86 and 1.28 at k = 2, 4, 8 (post
hoc, [`posthoc.json`](posthoc.json) › `rho_k`). (`scored.json` › `e125.N1`)

| rule | asked | card 1 | verdict |
|---|---|---|---|
| **Z** | E113's seven verdicts read again by `score_e113.py` | P1 PASS, P2 REJECTED, P3 PASS, P4 which bits (mirror better), P5 PASS, P6 PASS, P7 PASS | **REPLICATES** |
| **X-A** | the 16 A rungs at E113 / 1.030, w 0.6 W (1.0 W at k = 23); PASS if none FAILs and ≥ 8 PASS | 16 PASS | **PASS** |
| **X**, the other five | D1_A(8), ρ(8) low and spread, `nrd_a`/`nrd_b`, c | 2.740 W, 1.278, 1.387, 0.663, 0.662 | **PASS ×5** |
| **N1** | (r2 + r4)/2 − r8 ≥ 0.20 at ≥ 3 SE | +0.306 ± 0.023 | **SMALL-K EXCESS** |

Every rule is scored as registered over passes 12502–12508. **Every arm keeps every verdict** (Z REPLICATES, X-A PASS, N1 SMALL-K
EXCESS): E113's own reduction (dips kept, slope fitted), dips kept at 0.2414 W/°C, dips removed with the slope fitted (0.219 W/°C on
this session) or fixed at 0.2, 0.3 or 0.4 W/°C, and all eight passes. Across them N1 reads 0.284–0.337, c 0.647–0.666 and D1_A(8)
2.62–2.77 W. (`report.md` § Arms; `scored.json` › `arms`)

## The two ladders on card 1

ΔW over the A-side zero `aq_h0` (A constant, B = 1.0), paired per pass, mean ± SE over seven passes, with the frozen prediction
(E113 in the same frame / 1.030) and E113's registered value (`scored.json` › `items`; `predictions-e125.json` › `x_rules`).

| k | low `alq` (W) | predicted | E113 registered | spread `als` (W) | predicted | E113 registered | flipping bits, spread |
|---|---|---|---|---|---|---|---|
| 1 | 0.300 ± 0.038 | 0.339 | 0.314 ± 0.058 | — | — | — | — |
| 2 | 0.965 ± 0.028 | 0.917 | 0.951 ± 0.025 | 1.149 ± 0.048 | 1.133 | 1.177 ± 0.028 | 0, 12 |
| 3 | 0.911 ± 0.021 | 0.917 | 0.950 ± 0.026 | 2.675 ± 0.015 | 2.628 | 2.641 ± 0.095 | 0, 8, 15 |
| 4 | 1.601 ± 0.026 | 1.539 | 1.594 ± 0.026 | 2.738 ± 0.029 | 2.739 | 2.827 ± 0.029 | 0, 6, 12, 17 |
| 6 | 2.031 ± 0.011 | 1.981 | 2.045 ± 0.023 | 4.027 ± 0.032 | 4.054 | 3.941 ± 0.169 | 0, 4, 8, 12, 15, 19 |
| 8 | 2.048 ± 0.019 | 1.958 | 2.026 ± 0.028 | 4.788 ± 0.025 | 4.712 | 4.844 ± 0.056 | 0, 3, 6, 9, 12, 14, 17, 20 |
| 12 | 3.422 ± 0.026 | 3.406 | 3.504 ± 0.043 | 5.898 ± 0.034 | 5.878 | 6.061 ± 0.062 | 12 of 0–21 |
| 16 | 5.556 ± 0.011 | 5.542 | 5.743 ± 0.071 | 6.190 ± 0.021 | 6.316 | 6.504 ± 0.049 | 16 of 0–22 |
| 23 | 7.307 ± 0.029 | 7.387 | 7.598 ± 0.032 | = `alq_h23` | | | 0–22 |

The B rungs, run in the same passes, over `lq_h0`: `lq_h2` 1.011 ± 0.037, `lq_h4` 1.725 ± 0.037, `lq_h8` 3.206 ± 0.028, `ls_h8`
6.904 ± 0.040 W. The random pair: `nrd_a` 6.952 ± 0.038 W over `aq_h0`, `nrd_b` 10.485 ± 0.041 W over `lq_h0`. Per designed A bit
the low rungs cost 112–210 fJ and the spread rungs 169–388 fJ (E70's within-experiment currency, which must not be carried into the
gate-level ledger; `items.*.fJ_per_designed_bit`).

**Post hoc** ([`posthoc_e125.py`](posthoc_e125.py) → [`posthoc.json`](posthoc.json), no verdict):

- **The mirror over-predicts the top rung on both cards.** The refitted mirror predicts `alq_h23` 0.729 W too high on card 1 (E113:
  0.635 W registered, 0.662 W in the same frame) and the frozen one 0.506 W (E113: 0.215 W); the refitted S_A curve 1.659 W too low
  (`top_rung`). So the mirror is the better one-parameter law on two cards, not an exact one.
- **Part of E113's odd small-k ratios sat in E70's B rungs.** Card 1's own `lq_h2` and `lq_h4`, times s, read 1.041 and 1.776 W,
  against E70's 0.928 ± 0.042 and 1.505 ± 0.201 W on aifoundry3 (2.0 and 1.3 SE; `lq_h8`: 3.302 against 3.248, 1.4 SE)
  (`b_small_k`). That is a cross-card reading: E70's B rungs at k = 2 and 4 may have read low, which would explain why E113's
  cross-session ratios (1.02 and 1.05) ran above card 1's within-session 0.96 and 0.93.

## A desk finding before the freeze: E113's own passes carry board-meter dips

*Found and committed with the registration (`105f4601`), before any card-1 data:
[`tools/claims-v3/e125/e113-nodips/`](../../../../tools/claims-v3/e125/e113-nodips/). Post hoc for E113, whose registration is
frozen; for E125 it set the frame the X rules compare in. The records lane may add a dated note to E113's README.*

Card 1's board meter reads some launch gaps as ~4 W dips, and E82's amendment A2 removes them
(`board_w[i] < min(board_w[i−2], board_w[i+2]) − 4.0 W`). The same test finds **37 dips in E113's seven committed passes on
aifoundry3, 13 inside a run's power window** (4 in pass 1137), against 45 and 10 in this session's eight passes on card 1
(`posthoc.json` › `dips`). With them removed and nothing else changed (`hl/reduce_hl.py` at E113's own `--leak auto`, 0.162 W/°C;
`score_e113.py` unchanged):

- **all seven of E113's passes are kept.** Pass 1137's constant-operand spread, 0.858 W in E113 (its D-a set-aside), reads
  0.204 W. The set-aside was a board-meter dip, as E124 found for E109's pass 10912;
- **every one of E113's seven verdicts stands**;
- **`lq_h8` reads 3.281 ± 0.027 W** (E113: 3.037 ± 0.189, with two passes at 2.74 and 2.23 W and four at 3.26–3.41; E70:
  3.248 ± 0.028). So **ρ(8) reads 1.230 ± 0.019 in the low layout against 1.354 ± 0.011 in the spread layout** (E113: 1.366 ± 0.106
  and 1.350 ± 0.012, "the same in both layouts"). P5 still passes its 0.30 band, but the layouts differ by 0.124 ± 0.019. Card 1 now
  reads the same split, 0.109 ± 0.024 (result 4).

## What it changes

- **Item 15, the A side's form (E113): "another card" is answered.** E113's seven verdicts read again on aifoundry1 card 1 (Z
  REPLICATES, registered), and its numbers carry over at the card scale the kinds matrix measured (21 of 21 X rules; this ladder's
  own scale 1.031 against E82's 1.030). In A's own single-bit sum the saturating form is rejected on two cards (0.71 and 0.68 W rms).
  Which positions flip sets A's cost on two cards (D1_A(8) +2.84 and +2.74 W). An A mask costs about two thirds of the same mask on B
  on both cards: the mirror's c reads 0.68 on aifoundry3, and on card 1 0.662 against E70's aifoundry3 B rungs, which is 0.68 at
  card 1's own scale (× 1.030); within card 1's own passes, A/B of the same mask at k = 8 is 0.64 (low) and 0.69 (spread) (C1).
  Still open: the busy partner, other A base words, fp16 and int8, the gated lane.
- **Item 6's A-side clause (the power model): the constant fraction fails at small low masks.** Within one session an A mask of 2 or
  4 low bits costs 0.93–0.96 of the same mask on B, where 8 low bits cost 0.64 (N1, registered). E113's spread masks and its 8 or more
  low bits sit at 0.56–0.76. A power-model term that prices an A mask at about two thirds of the same mask on B (E113's suggestion)
  needs a small-k exception, and on two cards the refitted mirror still over-predicts the top rung by 0.6–0.7 W.
- **E113's "ρ(8) is the same in both layouts" does not hold in the dip-free frame:** 1.23 low and 1.35 spread on aifoundry3 (post
  hoc), 1.28 and 1.39 on card 1 (a reading beside P5, not a registered rule; C3). Both pairs are inside P5's band. The per-slot
  footing for E78's C2 (an ungated fp32 lane) stands: an A bit costs 1.2–1.4 B bits at k = 8 on two cards, not the ~8× a per-word
  count would need.
- **For the blog:** flip the same bit positions on the broadcast operand A instead of B, and a second card pays the same fraction as
  the first, about two thirds, for spread masks and for 8 or more low bits. For a mask of 2–4 low bits it pays nearly the full B price.
  On the second card the 16 A rungs fit one card scale of 3% (1.031, the kinds matrix's 1.030; rms 0.06 W), and all 21 numbers
  tested at that scale pass (C2).

## What ran

One item list, 26 runs a pass after two unrecorded `anchor_pi` burn-in runs: E113's 23 items plus `lq_h2` and `lq_h4`. The operand
set `build/hl-gen6-e113` was written on the box by E113's own `make_e113.py --check`. All 177 files of E113's pass 1131 list are
byte-identical in it (`logs/setup.log`, 20:11:49 PST: "identical lists: yes"). The harness on the box matched the registration byte
for byte, 18 of 18 files ([`logs/code.sha256`](logs/code.sha256), written at the launch and compared on the Intel at 20:16). E67's and E70's protocol ran through `hl/block.sh`
unchanged with `V3_DEVICE=1`: launch at a 58 °C reading after 59 °C, 4 s runs on 1,024 minions, the rest shuffled with the pass
number. Card 1 stayed at or above 59 °C between runs, so no run needed the heater (0 heats in all 208 runs); each waited 0.1–3.3 s to
cool to 58 °C (`runs.jsonl` › `heats`, `wait_s`).

- **The smoke**, pass 12500 (`anchor_pi`, `als_h8`, `alq_h8`, no preheat, 20:14:18–20:14:51), passed E113's smoke gate unchanged:
  block ok, every launch ok on 1,024 minions at 546 cycles per op.
- **Eight passes, 12501–12508**, 189–195 s each, 20:14:51–20:42:17 (`logs/queue.out`). The eighth ended 4 min before the
  registered deadline (20:46:18). **208 of 208 runs passed every per-run gate**: 600 MHz in every window sample, 498–499 mV, launch on
  protocol at 58.0 °C, 546.001 cycles per op in every run. The op rate held at 1.1201–1.1218 G minion-ops/s over the card. Host
  load1 ran 0.43–1.11 (`logs/load.jsonl`).
- **One pass set aside, by E67's drift gate as registered:** in pass 12501, the first, `anchor_pi` drifted +0.328 W from first to
  last, against 0.3 W. The registered reduction is over **seven passes (12502–12508)**. The all-passes arm, with 12501 in, keeps every
  verdict (N1 0.284, D1_A(8) 2.710 W).
- **Card 1's frame:** 45 board-meter dips in 15,202 samples, 10 inside a power window, were removed (`dips/dips.json`). The leakage
  slope was fixed at 0.2414 W/°C (E82's); this session's own within-run fit reads 0.219 W/°C over 123 runs (the `leakauto` arm).

**Departures:**
- **D1, ssh blocked during the session (the Tailscale check).** From 20:24:42 to 20:38:09 PST no ssh reached aifoundry1. It was
  logged to the workflow's Tailscale list at 20:24:58 and probed every 3 min, each probe killed at 15 s. The session, detached on the
  box, ran on untouched. A bounded remote wait (20:16–20:24) ended when the remote host closed the connection. No data were lost.
- **D2, the release came before the push.** The clause was dropped from the day's post at 20:43:13 PST, 41 s after the session ended
  and before this README was pushed. The registration said "after it [the session]"; the lane's brief put the push first. Releasing
  first freed card 1's line in the post sooner, as E124 did.
- **No departure from the registration otherwise.** The first claim attempt (~20:13:3x) stopped with `edit_replace.mjs` exit 7: another
  lane had rewritten the day's post after this lane read it at 20:13:07. The text was rebuilt from the live post and saved, as the
  one-post rule says.

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier read the registration, the data and this page the same evening. It re-ran `score_e125.py` on the
committed `runs.csv` and its six arm CSVs (`report.md` and `report-e113-format.md` byte-identical), re-derived every registered
number from `runs.csv` with its own code, regenerated `predictions-e125.json` and the desk finding from committed sources, re-ran
the self-test, and checked the harness hashes, the order of events, the posting protocol and the card etiquette. Every registered
number and verdict holds (verdict: holds with fixes). Its five faults, all minor, are in wording, and all five hold against
committed files ([`corrections-check.py`](corrections-check.py), [`corrections-check.txt`](corrections-check.txt), standard
library). The corrections were made at the desk: no card was touched, and nothing was set or re-run. No frozen sentence, data
file, number or verdict changes, and `E125.md` is untouched.

| | what was wrong | what changed |
|---|---|---|
| C1 | **The mirror's c on card 1 was set beside E113's as if it were card 1's own A/B fraction** ("on two cards (c 0.68 and 0.66)", in "What it changes"). Card 1's c, 0.6617 ± 0.0020, is fitted against E70's B rungs, measured on aifoundry3, so it carries the 3% card scale: X-c predicted it at E113's 0.6809 / 1.030 = 0.661. The gap between 0.66 and 0.68 is that scale, not a difference between the cards | Result 3 and "What it changes" say: c = 0.662 against E70's aifoundry3 B rungs, 0.68 at card 1's own scale (× 1.030), as E113's 0.68 on aifoundry3. Within card 1's own passes, A/B of the same mask at k = 8 is 0.64 in the low layout (0.639 ± 0.009, N1's r8) and 0.69 in the spread layout (0.694 ± 0.005, paired per pass as N1 pairs the low ones). "About two thirds" stays |
| C2 | **Blog wording went past the data.** "The card itself scales every number by the same 3%" overstates one fitted scale. The ladder's 1.0314 is a least-squares fit with rms 0.058 W, and E113's rungs over card 1's run 0.979–1.166 (0.985–1.051 above 1.5 W). In the lane's result, "an A bit costs 1.28 (low) to 1.39 (spread) times a B bit" holds at k = 8 only: at k = 2 and 4 the low layout reads 1.92 and 1.86 per designed bit (post hoc, `posthoc.json` › `rho_k`) | "For the blog" says the 16 A rungs fit one card scale of 3% (1.031, the kinds matrix's 1.030; rms 0.06 W), and all 21 numbers tested at that scale pass. The result's blog line names k = 8 |
| C3 | **Result 4 gave "the two layouts do not share one ρ(8)" (+0.109 ± 0.024, 4.5 SE) as a result, without saying that no rule registers it.** P5 bounds only \|spread − low\| ≤ 0.30, and no Z, X or N1 rule tests the difference against zero | Result 4 and "What it changes" call it a reading beside P5, not a registered rule, which the desk finding predicted (+0.124 ± 0.019 on E113's dip-free passes, committed with the registration in `105f4601`) |
| C4 | In the lane's result only, not a committed file: its numbers list gave fJ per designed A bit (112–210 low, 169–388 spread) without this page's caveat | The result's entries carry the caveat: E70's within-experiment currency, not to be carried into the gate-level ledger |
| C5 | A doubled word in the header: "committed and **committed as `105f4601` …**" | "the scorer and its self-test, **committed as `105f4601` at 20:12:35 PST and pushed by 20:12:38**" |

## Files

| file | what |
|---|---|
| `report.md`, `scored.json` | **the registered result**: `score_e125.py` (P1–P7 by `score_e113.py` unchanged, Z, the X rules, N1) over the seven kept passes; the arms in `report.md` § Arms and `scored.json` › `arms` |
| `report-e113-format.md` | `score_e113.py`'s own report for card 1's runs |
| `hl.json`, `runs.csv`, `reduce.txt` | the primary reduction: `hl/reduce_hl.py` unchanged over the dip-free copies, `--leak 0.2414` (`runs.csv` is the scorers' input) |
| `hl-*.json`, `runs-*.csv`, `reduce-*.txt` | the arms: `e113frame` (dips kept, slope fitted), `dipskept` (0.2414), `leakauto`, `leak0.2/0.3/0.4` (dips removed) |
| `dips/dips.json` | card 1's dips per pass, where they fall (E82 A2's test) |
| `posthoc_e125.py`, `posthoc.json` | the numbers labelled post hoc |
| `corrections-check.py`, `corrections-check.txt` | added with the corrections after verification: post hoc, deciding nothing, standard library (the same output on Python 3.9 and 3.13, from any directory); prints, from committed files, every number the corrections quote |
| `predictions-e113.json`, `predictions-e125.json`, `manifest.json` | the frozen predictions as run; the operand set's items and designed flip counts |
| `aifoundry1-c1/e125/p12501…p12508` | per pass: `block.json`, `configs.json`, `gen.sha256`, `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz`, `tiles/` |
| `aifoundry1-c1/smoke-p12500` | the smoke pass |
| `logs/` | `setup.log` (files only: the operand set, its byte check, the dry run), `session.log`, `session.out`, `queue.out`, `smoke.log`, `load.jsonl`, both `config-session-*.json` with their times, `anchor-t0.txt`, `code.sha256` (the harness as launched) |

Nothing on the card was changed: no governor, TDP, threshold or clock write, no reset, no `--reset-ms`, no PMIC command (no PMIC
write, no firmware-revisions query). As in every lab run with the stock sampler, the two `ettelem config` reads sent
`GET_ASIC_VOLTAGE`, and each sampler reading sent `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE`. All 15,202 readings saved in the
passes' `telemetry.jsonl.gz` carry `die_mv` and `reg_mv`. These read PMIC voltage registers, with no write (the owner's open
question, Q133's records). No statistics reset was sent (`since_reset_ms` −1 in every saved reading). `et-who` showed no holder at
setup (20:11:49 PST, `logs/setup.log`), at the session's start (20:14:18, `logs/session.log`) and at its end (20:42:32). Other lab
users' logins on the host did not block (E60's departure D1, as `hl/block.sh` implements it for aifoundry1), and none of their names
is recorded here.
