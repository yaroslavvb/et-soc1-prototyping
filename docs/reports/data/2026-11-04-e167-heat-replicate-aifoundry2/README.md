# E167: the heat replicate on aifoundry2 under its own governor - G1Q's plateau from the bits reads 1.35 °C high (RK3-b FAIL, not resolved by the readout), its trajectory 0.93 °C rms; the chain given the watts runs 5.4% of G1Q's 16.8 °C rise low (RK3-c FAIL; G2Q 0.14%); G2Q's trip plateau (−0.39 °C) and trip clock from the bits (−3.6 MHz) PASS

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**items 9, 8 and 6**. It answers **rank 3 of Q139's final critic** ("heat over minutes from the bits, a second session per card"), its
aifoundry2 half (E166 is the aifoundry3 half), as Q140's and Q141's critics left it (`card_half[4]`).*

*Wed 4 Nov 2026 (week 45), the card half of Q141, aifoundry2 card 0 under its own governor (65 W / 65 °C read before and after, nothing
set). Registered before any E167 data: [`E167.md`](../../../../tools/claims-v3/e167/E167.md) and its JSON `7ba987b3` (09:16:50 PST),
the scorer `f830b9e2` (09:31:08), the kit `4f4e7620` (09:59:53), amendment X2, `score_e167_x2.py`, the latch check and the bounded
collector `48994187` (11:24:19; [`E167.md.dated-note-2.md`](../../../../tools/claims-v3/e167/E167.md.dated-note-2.md)). It descends from
Q140(e)'s frozen predictions (`11174d20`, `c9aaf179`, `a4fe976d`, `ac06c9be`) and M9's aifoundry2 part (`5b98bd5c`, `245caffe`,
`5c98c0c5`). It ran after E165 on the same card, from the checkout at `5e1bb309` (E165's README, D1). The day's one `#community-lab`
post (message 1567662592850399304) named aifoundry2 from 14:11:27 PST.*

## The answer

| rule (X2, the registered verdicts) | hold | measured | predicted (the primary: M9's in-work level at the hold's own duty) | line | verdict |
|---|---|---|---|---|---|
| **RK3-b** | G1Q, `int8.b_line_zero_ff`, 93 × 8 s, in the 800 MHz regime | plateau **64.79 °C** (a 16.79 °C rise over its 48.0 °C REST) | 63.44 °C: **+1.35 °C**; trajectory **0.93 °C rms** | within 1.0 °C, trajectory at most 1.0 °C rms | **FAIL**, not resolved by the readout (at the REST + 0.5 °C it reads +0.65 °C and passes; at − 0.5 °C, +2.05 °C) |
| **RK3-c** (aifoundry2) | every rise of 10 °C or more, given the watts (arm A) | G1Q: arm A +0.91 °C = **5.4% of the rise**; G2Q: +0.02 °C = **0.14%** | | at most 1.5% of the rise, every hold | **FAIL** (G1Q outside, resolved; G2Q inside) |
| carried | G1Q's regime (the 800 MHz band) and its clock | 794.7 MHz in the window (97% of samples at 790 MHz or more) | the 800 MHz regime | | **PASS**, clock **PASS** |
| carried | G2Q, `fp32.real_smol_softmax_v_causal`, 91 processes, the trip regime | plateau **65.51 °C**; clock **663.9 MHz** (89% of samples below 790 MHz) | the trip rule's 65.9 °C: **−0.39 °C**; the trip clock from the bits 667.5 MHz: **−3.6 MHz** | ±0.60 °C; the clock ±35 MHz | **PASS**, clock **PASS** |

Source: [`scored.json`](scored.json) › `verdicts` (X2; `score_e167.py`'s own, kept beside as `verdicts_score_e167`, are the same), by
[`score_e167_x2.py`](../../../../tools/claims-v3/e167/score_e167_x2.py) behind `frozen-e167-x2.sha256` (15 OK). Both holds were complete
in X2's sense (`scored.json` › `x2.holds`: every planned process ran, no safety mark, the windows' lines all there), so no hold is gated
or excluded. **Rank 3 on the replicates** needs E166's RK3-a and RK3-c and E167's RK3-b and RK3-c all to hold (E167.md); E166 read RK3-a
and RK3-c FAIL (`179549ce`) and E167 reads RK3-b and RK3-c FAIL, so **rank 3 is not answered: the replicates fail it on both cards.**

## What this does to predicting power and heat

The terms tested, blind, on the governed card: Q140(e)'s duty convention and M9's in-work level (T2 through its relation, one die law)
where the bits set the die (G1Q), the chain's gain given the watts (both large rises), and the sustained trip clock from the bits (G2Q).

| | G1Q plateau from the bits | G1Q trajectory | G2Q trip clock from the bits |
|---|---|---|---|
| **before**: E161, out of sample as registered | −0.90 °C | 1.04 °C rms | +12.6 MHz |
| before, post hoc on Q140(e)'s convention (in sample for the duty) | +0.64 °C | 0.50 °C rms | −4.0 MHz |
| **after**: E167, blind (the primary) | **+1.35 °C** | **0.93 °C rms** | **−3.6 MHz** |
| beside it: M8 at the hold's duty / M8 continuous | +0.46 / −0.06 °C | 0.47 / 0.68 °C rms | +7.6 / +14.0 MHz |
| beside it: E2, M9's level with E165's anchor delta (reported) | +1.38 °C | 0.95 °C rms | −3.1 MHz |

(`scored.json` › `holds.*.primary_M9a_at_own_d`, `M8_at_own_d`, `M8_continuous`, `reported_M9a_E165_delta_at_own_d`; the "before" rows are
E167.md's.) So the trip clock from the bits replicates (−3.6 against −4.0 MHz post hoc), and the governed trip plateau is again set by the
trip rule (−0.39 °C). Where the bits set the die, the primary's in-work level runs low: G1Q's plateau 1.35 °C high, while M8's older
level is within 0.46 °C; and the chain given the measured watts is 0.91 °C low on G1Q (5.4% of its rise; E166 read 1.8-3.2% on
aifoundry3). On aifoundry2 the heat path's gain, not only the power term, is what the large G1Q rise misses. The day's anchor delta from
E165 (E2) moves G1Q by 0.03 °C and G2Q's clock by 0.5 MHz: the zeros level is not what is off.

## The session, step by step

| step | PST | card-minutes | what happened |
|---|---|---|---|
| latch check | 15:12 | — | `latch_check_e167.py --history` on the box's 5 s history: **GO**, the hottest-sensor field 70 °C, under E167's 72 °C line |
| config | 15:12:31 | — | `run_e167.sh config start`: TDP 65 W, threshold 65 °C, power state 3, 600 MHz at 519 mV |
| queue | 15:12:42 | — | `run_e167.sh go 15:12 15:45 16:55 17:10` (smoke not before, smoke latest, no start after, cutoff); `build/e167/runs/GO` touched 15:12:45; the queue's go at 15:13:29 (`via GO`, the code checked equal to `origin/main`) |
| SMOKE | 15:13:29-15:14:12 | 0.72 | rc 0; the smoke check sound (its C log 20 of 20 bit-exact) |
| STOPTEST-DIE | 15:14:12-15:14:15 | 0.03 | the die stop at 30 °C fired on the first live sample (`safety:die 70 C >= 30 C`, the hottest-sensor latch) |
| STOPTEST-BOARD | 15:14:15-15:14:18 | 0.05 | the board stop at 30 W fired 65 ms after the third line over it (`safety:board 31.1 W > 30 W on 3 samples`) |
| rest | 15:14:18-15:29:18 | — | E98's 15 minutes with no launch |
| G1Q | 15:29:18-15:44:29 | 15.18 | the REST read 48.0 °C (G1's gate: at most 49 °C) at once; the hold's 93 processes all ran |
| END | 15:44:29-15:46:31 | 2.03 | G1Q's cool-down |
| rest | 15:46:31-16:01:31 | — | 15 minutes with no launch |
| G2Q | 16:01:31-16:16:35 | 15.07 | REST 48.3 °C; 91 processes, in the trip regime |
| END2 | 16:16:35-16:18:37 | 2.03 | queue end "done" |

**35.12 card-minutes of the 40 cap** (E161: 35.07), 66 minutes of wall time. Every step's check of C is bit-exact: SMOKE 20 of 20,
STOPTEST-BOARD 3 of 3, G1Q 1,742 of 1,742, G2Q 1,612 of 1,612 launches (`ccheck-*.json`). Peaks: board 65.88 W (G2Q), the shires' mean
66 °C, the hottest-sensor field 70 °C (its latch) throughout. The 82 W admission is E161's static desk check (M8's 95% peaks 53.33 W and
68.15 W), as the kit's dated note says; the live stops are stricter (72 °C; over 80 W on three samples) and were tested above.

## Departures and notes (dated, Wed 4 Nov 2026)

- **The four gates** were set at the launch, never defaulted: 15:12 / 15:45 / 16:55 / 17:10. The cutoff and the last start are earlier
  than the round's 19:00 / 18:15 so that E168 (a 66-minute slot) and E169 (45) could still run after E167 inside the window. Nothing was
  cut: every step started and ended well inside them.
- **The tree**: the box's checkout was fast-forwarded to `5e1bb309` before E165 (E165's README, D1). `run_e167.sh check` then read
  `frozen-e167.sha256: every file as registered` and `frozen-e167-x2.sha256` 15 OK on the box, and the queue's go compared its files with
  `origin/main` and found them equal.
- **Collection** was by the runbook's v2 step (`tools/claims-v3/q141k-runbook/v2/s22_collect.sh e167`: the three boxes probed first, then
  `collect_e167_bounded.sh`, then the check of C per step, the hash list and the scorer). It reads the three boxes' own 5 s history over
  the session, numbers only (`history/`); E111's login scrub replaced nothing.
- No other departure. G2Q's checkpoints carry no skill (Q140(e)'s C9) and are not read as a result.

## Device commands sent

Exactly the registered set ([`E167.md` § Device commands](../../../../tools/claims-v3/e167/E167.md#device-commands);
[`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e167/logs/dmcmd-audit.txt): GO, 35 send sites): `ettelem sample` and
`ettelem config` reads (the two PMIC voltage-register reads among them, the owner's allowed reads), the trace copy, and the residency
read that is never sent (`*/e167-not-sent.jsonl`). No statistics reset, no firmware-revisions query, no governor, TDP, threshold or clock
set. The latch check reads a file.

## Files

| file | what |
|---|---|
| [`scored.json`](scored.json) | the registered scoring (`score_e167_x2.py`, with E165's anchors for the reported E2 arm: `E2_delta`) |
| `ccheck-*.json` | the check of C per step |
| `SMOKE/` … `END2/` | each step's session (runs, launches and the C log gzipped, the sampler lines in `tel/` gzipped, `sp/` traces) |
| `queue.jsonl`, `queue.out`, `status.json`, `schedule.json`, `GO` | the queue's own records, the day's gates and the go marker |
| `history/` | the three boxes' 5 s history over the session (numbers only) |
| `idle_logins.jsonl`, `phone.jsonl` | the idle-login rule's counts and the camera phone's health once a minute |

SPDX-License-Identifier: Apache-2.0
