# E161 data: heat over minutes predicted end to end from the bits, under aifoundry2's own governor - Q139(e)'s frozen holds scored (Q139, Tue 3 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**items 9** (a steady state for heat), **8** (the heat path between sessions) and **6** (the power model). It bears on **rank 4 of Q138's
final critic**, "Heat over minutes predicted end to end from the computation's description ... The bits-to-M7-power-to-chain path for a new
kind has never been scored", and is its aifoundry2 half (E154 is the aifoundry3 half).*

*Pre-registered in [`tools/claims-v3/e161/E161.md`](../../../../tools/claims-v3/e161/E161.md), committed as **`ddbd15b1`** and pushed at
about 16:22 PST, before the claim and before any device access. The frozen predictions are Q139(e)'s,
[`../2026-11-03-q139e-heat-end-to-end/`](../2026-11-03-q139e-heat-end-to-end/README.md): `455c46c1` with amendment A1 `e224a3f8`, both
on origin/main before this registration. [`reduce_e161.py`](../../../../tools/claims-v3/e161/reduce_e161.py) checked 13 frozen inputs'
sha256 before scoring and imported `predict_q139e.py` and `score_e144.py` unchanged. Nothing was refitted or tuned.*

*(Dated note, Tue 3 Nov 2026, after verification, C5.) The registration was written between about 15:55 and 16:22 PST, not to 16:30. It
was committed at 16:22:46 PST and pushed at 16:22:49, before the claim (16:24:03–16:24:16) and the first device access (16:24:30).
`E161.md`'s header and the heading of its departures say "about 15:55-16:30 PST", which runs past its own commit. The frozen file is left
as it was.*

*The session, on aifoundry2 card 0 only, under its own governor (nothing set):*
- *Claimed at 16:24:16 PST by rewriting the day's one `#community-lab` post (message `1567332504330051616`, created 16:19 by another lane):
  the clause `using aifoundry2 for 1.5 h, until ~17:54 PST` joined the two clauses then held. Released at about 17:30 PST (the edit saved
  between 17:30:11 and 17:30:29): by then it was the only clause left, so ` — released` was appended, every word kept.*
- *The detached queue started at 16:23:47 and waited. The go came over ssh at 16:24:34 (`GO`); the box's runner, queue and seven protocols
  equalled origin/main's byte for byte.*
- *Card runs 16:25:00–17:30:05 PST: **35.07 card-minutes of 40**, about 65 minutes of wall time with E98's two 15-minute rests.*
- *`ettelem config` read **65 W / 65 °C** (low_power, 600 MHz, 519 mV) at the session-start read (16:24:30), at every step's start and end
  (14 reads) and at the session-end read (17:30:05). **Every command sent was a READ**; the residency read was answered unsent 22 times.*
- *No other user was logged in to aifoundry2 at any of the 236 idle-login checks (counts only), and `et-who` showed the card free before the
  go and after the end.*

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 18:10–18:27 PST; desk only: no card, no device command, no ssh, nothing
re-run). An independent verifier re-derived every registered number and verdict from the committed data and the frozen code, re-ran the
device-command audit and the check of C, and re-hashed the box's raw files read-only. All of it stands, the reduction and the post hoc
readings byte for byte. It found one major and four minor faults in what this README and the lane's result draw from them. None changes a
measured, frozen or registered number, rule, prediction or verdict. Each is corrected by a dated note beside the text it concerns, the text
itself left as it was, and set out in full in [§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the
end. Every number is printed by [`corrections_e161.py`](corrections_e161.py) → [`corrections.txt`](corrections.txt), labelled post hoc.*

- ***C1 (major):** the post hoc work share (P1, P2) counted the scoring window's last 6 s, after the work had ended, and each process's
  start-up as idle. The hold's own kernel duty, from `launches.jsonl` alone, is 0.970. At it the duty takes G1Q's error from −0.90 to
  −0.39 °C and G2Q's clock error from +12.6 to +5.6 MHz. Across definitions of the share the corrected figures run from −0.88 to +0.12 °C
  and from +12.3 to −2.2 MHz. So the duty is about half of G1Q's error, not most of it, and M8's level inside the work is the larger part.*
- ***C2:** "from the bits alone" means from the bits and the idle card's die and board just before each hold, a ±0.5 °C anchor.*
- ***C3:** this is the first blind score of rank 4's aifoundry2 half, not its answer.*
- ***C4:** G1Q was scored between the holds; nothing about G2Q changed.*
- ***C5:** the registration was written by 16:22 PST.*

## Results first

**All six registered readings PASS.** Heat over minutes predicted from the tile's bits alone, through M8's power, Q138(t)'s frozen chain and
the governor's trip rule, reads a 13-minute governed hold's plateau to **−0.90 °C** where the bits set the die (G1Q, band ±3.15 °C) and
**−0.40 °C** where the governor holds it (G2Q, band ±0.60 °C). The sustained clock from the bits reads **+12.6 MHz** (band ±35 MHz). Every
launch's C is bit-exact: **3,354 of 3,354** launches, the smoke's included ([`results.json`](results.json) `verdicts`, `c_check`;
[`reduce.txt`](reduce.txt)).

*(Dated note, Tue 3 Nov 2026, after verification, C2.) "From the tile's bits alone" goes too far, here and in the registration's own words
([`E161.md`](../../../../tools/claims-v3/e161/E161.md), [`tools/claims-v3/e161/README.md`](../../../../tools/claims-v3/e161/README.md)).
Every prediction is anchored on the idle card's measured die and board just before the hold: each REST's last 120 s, 47.0 °C and
22.12 / 22.19 W ([`results.json`](results.json) `T_rest_C`, `P_ref_W`). The die reads whole degrees, so the anchor is known to ±0.5 °C. Over
it G1Q's plateau error moves from −0.19 to −1.61 °C and G2Q's clock error from +4.1 to +21.1 MHz, every reading still PASS (the table under
"Over the rest die's whole-degree reading" below). Read "from the bits" on this page as: from the tile's bits and the idle card's die and
board just before the hold (a ±0.5 °C anchor). [§ Corrections, C2](#corrections-after-verification-tue-3-nov-2026).*

| hold (rest die, board) | arm | measured | predicted | error | registered band | verdict | beside |
|---|---|---|---|---|---|---|---|
| **G1Q** `int8.b_line_zero_ff`, 93 × 8 s (47.0 °C, 22.12 W) | **E, from the bits**: plateau (last 300 s) | **62.88 °C** | 63.78 °C (800 MHz fixed point) | **−0.90 °C** | ±3.149 (FAIL ±6.297) | **PASS** | M7 through the same path −1.45 |
| | E: trajectory, 7 checkpoints 60–750 s | rms **1.04 °C** (worst −1.71 at 180 s) | `a2_closed` from the REST | — | ≤ 3.149 | (in the PASS above) | M7 1.51 |
| | E: clock (share ≥ 790 MHz, last 300 s) | **0.952** (mean 790.9 MHz) | 800 MHz, never trips | — | PASS ≥ 0.90 | **PASS** | — |
| | **A, given the watts**: Q138(t)'s chain on the measured board | rms **0.48 °C**; plateau **+0.37** | — | — | rms ≤ 1.20, \|plateau\| ≤ 1.30 | **PASS** | M6's step response 1.72 / +0.37 |
| **G2Q** `fp32.real_smol_softmax_v_causal`, 91 × 8 s (47.0 °C, 22.19 W) | **E, from the bits**: the trip rule | **65.50 °C**, regime **trip** (81% of the last 300 s under 790 MHz) | 65.9 °C, trip (the 800 MHz fixed point would be 80.6 °C) | **−0.40 °C** | ±0.60 and the regime (FAIL ±1.20) | **PASS** | M7 −0.40 |
| | E: the clock from the bits (mean, last 300 s) | **680.1 MHz** | **667.5 MHz** (`a2_trip_clock` at this REST) | **+12.6 MHz** | ±35 (FAIL ±70) | **PASS** | M7 668.4: +11.6 |
| | A, given the watts | rms **0.48 °C**; plateau **−0.22** | — | — | as G1Q | **PASS** | M6 2.30 / −0.26 |

**The session figure** (the out-of-sample error of heat over minutes from the bits on this card): the rms of the two holds' plateau errors
is **0.69 °C**; G1Q's alone, where the bits set the die, is −0.90 °C; G2Q's clock error, the first sustained governed clock predicted from
the bits on a new kind, is +12.6 MHz (`session`). On G1Q the error from the bits is also inside the critic's tighter scale for this card,
1.0–1.3 °C (Q139(e)'s `critic_scale_C` 1.305; a post hoc reading, not a rule).

*(Dated note, Wed 4 Nov 2026, Q140(c), post hoc, after Q139's final critic.)* The 0.69 °C averages a plateau the bits set (G1Q) with one the trip rule set (G2Q: 65.50 against the rule's 65.9 °C). Quote G1Q, −0.90 °C, as this card's heat over minutes from the bits, assuming continuous work (−0.39 °C at the harness's kernel duty, C1: the figure like for like with E154's, whose chain ran on its realized dispatch records), and G2Q as the trip regime found and its clock, +12.6 MHz, its plateau 0.40 °C under the trip rule: a test of that rule, not of the bits. [`../2026-11-04-q140c-critic-checks/`](../2026-11-04-q140c-critic-checks/README.md).

1. **The heat path given the watts holds on a fourth session, blind.** Q138(t)'s chain (R 0.663 °C per board W, fitted on E111 and E133)
   follows the die through both holds to 0.48 °C rms given the measured board (E144b, the third session: 0.76 / 0.37 °C). M6's frozen
   step response misses by 1.72 and 2.30 °C.
2. **From the bits, the power path adds −1.27 °C on G1Q and −0.17 °C on G2Q** (E − A on the plateau). On G1Q, M8's composition put the hold's
   board at 47.40 W over its last 300 s; the card drew 45.24 W. *Post hoc* ([`posthoc.txt`](posthoc.txt) P1): inside the work processes it
   drew 45.90 W (46.26 W at ≥ 790 MHz), and 6.0% of the samples fall between processes, where the card idles. The composition assumes
   continuous work. With the switching part scaled by the measured work share, 0.940, the same frozen fixed point reads 62.76 °C, **+0.12 °C**
   from the measured plateau. So most of G1Q's −0.90 °C is the harness's duty, not M8's level or the chain.

   *(Dated note, Tue 3 Nov 2026, after verification, C1.)* The post hoc reading in this item is misdescribed. Of the scoring window's 2,998
   samples, **2.0% come after the hold's last process ended**: the HOLD file runs 5.9 s past it, idle at 27.3 W, so this is the registered
   window's end, not a duty. Another 0.3% fall in the gaps between processes, which last about 10 ms each, with the board still at 41.6 W.
   And **3.4% fall in a process's first 0.3 s, when the card is starting up and already drawing 36–39 W** (the first kernel launch starts
   0.146–0.203 s in). P1's 0.940 counted all of them as idle, and its 45.90 W is the trimmed windows' figure (45.62 W in the process
   windows, 45.78 W in the kernel launches). From the harness's own records alone (`launches.jsonl.gz`), the hold's **kernel duty**, the time
   in kernel launches over the hold's span, is **0.970**. At it the frozen fixed point reads 63.27 °C, **−0.39 °C** from the measured plateau,
   not +0.12. Across the definitions of the share the error runs from −0.88 to +0.12 °C. **M8's level is the larger part:** inside the
   kernel launches at ≥ 790 MHz the card drew 0.91 W less than M8's 800 MHz board at the same die. In round figures, the power path's
   −1.27 °C is about −0.85 °C of M8's level and −0.5 °C of the harness's duty, and the chain's own +0.37 °C given the watts offsets part of
   it. So the last sentence above does not hold. [§ Corrections, C1](#corrections-after-verification-tue-3-nov-2026).
3. **The trip was predicted from the rest die and held; the clock came out 12.6 MHz higher than the bits said.** The die settled at 65.50 °C
   (whole-degree readings 65 and 66), the regime the rule names. At this session's 47.0 °C rest the frozen relation gives 667.5 MHz (681.6 at
   the nominal 46.0 °C). The card held 680.1 MHz: 600 MHz in 38.7% of the last 300 s, 700 in 42.5%, 800 in 18.8% (P2). *Post hoc*, the same
   work share explains it: to hold the die at 65.9 °C with 6.1% of the time idle, the board inside the work must sit higher, and the frozen
   relation then reads **682.3 MHz** (−2.1 MHz). Amendment A1 C2's reading beside the verdict, the trip clock with R set to G1Q's measured
   0.6875 °C per board W, gives 656.0 MHz (+24.1 MHz). Here the heat path's R moves the prediction the wrong way, and the frozen 0.663 does
   better.

   *(Dated note, Tue 3 Nov 2026, after verification, C1.)* P2's −2.1 MHz rounds to **−2.2 MHz** (682.27 against the unrounded 680.09 MHz
   measured). "The same work share explains it" does not hold: that share counts the window's last 6 s and each process's start-up as idle.
   At the hold's kernel duty, 0.970, the trip clock reads 674.5 MHz, **+5.6 MHz** from the measured. Across definitions the error runs from
   +12.3 to −2.2 MHz. M8's level is in the loop here too: inside the kernel launches, M8's board at the clocks the card ran is 1.61 W above
   the measured. With that level alone the error would be −5.6 MHz, with the level and the duty −12.6 MHz, and with the level and the
   measured held die (65.50 °C for the rule's 65.9) −0.8 MHz. One hold does not resolve which terms close the clock.
   [§ Corrections, C1](#corrections-after-verification-tue-3-nov-2026).
4. **The governor's timing is not M8's cap.** M8 predicted G2Q's first step down at 48 s, from its 65.2 W cap; the highest board sample in the
   first 60 s was 64.9 W, so the cap never bound. The clock held 800 MHz in 580 of the first 600 samples; the exceptions were the start of
   the second process (8.5–9.6 s: 600 MHz, the board down to 38 W, the die 53–54 °C), the kind of process-boundary step E144b's G1 also
   showed. The
   die first read 65 °C at about 56 s and the trip regime followed (P3). The reducer's descriptive "first step down" (8.8 s on G2Q, 76 s on
   G1Q) reads such process boundaries, not the governor's trip (as E144b's D5).
5. **C is right on every launch.** Q139(k)'s check reads all 1,751 G1Q launches, all 1,579 G2Q launches and the smoke's 24 bit-exact
   (`ccheck-*.json`). G1Q's int8 tile carries operands up to \|128\|, a range the host's own read-backs of 25 Sep (\[−3, 3\]) never covered;
   the fp32 real tile's C is exact too. So the computation that heated the card is the one the bits describe.
6. **Safety.** No stop fired in either hold. G1Q peaked at 46.77 W and a 63 °C die mean, G2Q at 65.77 W and 66 °C. No sample passed 80 W. The
   hottest sensor's field read its carried 70 °C throughout, 2 °C under the 72 °C stop. Both holds ran as designed: M8's 95% peaks were 53.3 and
   68.2 W, under section 22's 82 W, so neither was duty-cycled or dropped. The stop path was tested on live samples before either hold: the
   die stop tripped 62 ms after the first live line at or above 30 °C, before any launch; the board stop tripped 65 ms after the third live
   line over 30 W, inside the launch, which ended 223 ms later ([`queue.jsonl`](queue.jsonl) `stoptest_detail`).

**Over the rest die's whole-degree reading** (post hoc, as E144b's C2). Both RESTs read 47 °C in all 1,199 samples of their last 120 s, so
every anchor is known to ±0.5 °C ([`results.json`](results.json) `posthoc_rest_quantization`):

| reading | as registered (47.00 °C) | over a rest die of 46.50–47.50 °C | holds over the range? |
|---|---|---|---|
| G1Q E: plateau error; checkpoints' rms | −0.90; 1.04 °C: PASS | −0.19 to −1.61; 0.48 to 1.70 | yes |
| G2Q E: plateau − 65.9 | −0.40 °C: PASS | −0.40 (the trip does not move with the anchor) | yes |
| G2Q E: clock error | +12.6 MHz: PASS | +4.1 to +21.1 | yes |

## What this does to predicting power and heat

**The term tested:** the whole path from a computation's description to its die over minutes on a governed card (the bits, M8's board at
800 MHz, Q138(t)'s closed chain, the governor's trip rule and cap), and, at the trip, the sustained clock from the bits. It was measured
blind, on a session none of them was fitted on.

| what is predicted | before (out of sample) | after: E161, blind |
|---|---|---|
| **The die over a 13-minute governed hold, from the bits** (arm E) | never scored; Q139(e)'s expected 95% size 3.15 °C below the trip, ±0.60 °C at it | **plateau −0.90 °C (G1Q) and −0.40 °C (G2Q), rms of the two 0.69 °C**; G1Q's trajectory 1.04 °C rms |
| **The same, given the measured board** (arm A) | 0.37–0.76 °C rms (E144b) | **0.48 / 0.48 °C rms**; plateaus +0.37 / −0.22 °C |
| **The sustained governed clock of a new kind, from the bits** | never scored (bursts only: M8 7.2 MHz rms in sample; E143's blind 6.6 MHz) | **+12.6 MHz** (one hold; M7 +11.6) |
| **The power path's share of the heat error** (E − A) | unknown | −1.27 °C (G1Q), −0.17 °C (G2Q) |

*(Dated note, Wed 4 Nov 2026, Q140(c).)* The first row's "rms of the two 0.69 °C" mixes the bits' plateau with the trip rule's; see the dated note under the session figure above.

So heat over minutes from the bits on aifoundry2 can now be quoted at **about 1 °C** at a plateau set by the bits and **about 0.4 °C** at the
trip, from one session with the rest die's reading as the anchor, and the sustained clock at **about 13 MHz**. Both are well inside Q139(e)'s
bands and, on G1Q, inside the critic's tighter 1.0–1.3 °C. **The next term**, found post hoc and so not yet a prediction: **the hold's work
share** (0.94 of the samples in work, with a duty set by the harness's process starts). Scaling the switching power by it moves G1Q's plateau
error from −0.90 to +0.12 °C and G2Q's clock error from +12.6 to −2.1 MHz. It should be frozen and tested blind on another session before it
is quoted. M8's own level at 800 MHz, about 0.8 W high on this tile inside the work, is the smaller part. The heat path's R, raised to the
session's measured 0.6875 (A1 C2), makes the clock worse (+24.1 MHz), so this session gives no support for moving it.

*(Dated note, Tue 3 Nov 2026, after verification, C1 and C3.)* Two readings in this paragraph go further than the data.
- ***"Can now be quoted."*** This is the first blind score of rank 4's aifoundry2 half: one session, two holds, with the rest die as a
  ±0.5 °C anchor (C2). G1Q's registered band, 3.15 °C, is 2.4–3.1 times the critic's decisive 1.0–1.3 °C, so its PASS cannot separate M8
  from M7 (−0.90 against −1.45 °C). G1Q's plateau error (−0.90 °C) and trajectory rms (1.04 °C) fall inside the critic's 1.3 °C only as a
  post hoc reading. Rank 4 is not closed until E154's aifoundry3 half and a replicate session have been scored.
- ***The next term.*** Its size depends on how the work share is defined (C1). The 0.94 counted the window's tail and the processes'
  start-up as idle. At the hold's kernel duty, 0.970 from `launches.jsonl` alone, the term takes G1Q's error from −0.90 to −0.39 °C and
  G2Q's clock error from +12.6 to +5.6 MHz. Before it is tested blind on another session, freeze it with that definition and that value,
  and end the scoring window at the hold's last process (or model the tail). M8's level inside the work, 0.91 W high on G1Q at
  ≥ 790 MHz and 1.61 W on G2Q's launches, is the larger part on G1Q, not "the smaller part", so the duty term alone will not close the
  error. [§ Corrections, C1, C3](#corrections-after-verification-tue-3-nov-2026).

## The session, step by step

| step | ran (PST) | card-min | result |
|---|---|---|---|
| SMOKE | 16:25:00–16:25:43 | 0.72 | exit 0, three launches rc 0, config 65 W / 65 °C; the C log sound: 21 C records for 21 SPARSITY lines, 3 host records naming the pinned host and E80's kernel; the DMA rule: median gap 3.0 ms, δ 2.0 ms, projected 8.75 s ≤ 9.2 s: passed |
| STOPTEST-DIE | 16:25:43–16:25:45 | 0.03 | exit 4 `safety:die 70 C >= 30 C` (the hottest sensor's carried 70 °C), 62 ms after the first live line, no launch: passed |
| STOPTEST-BOARD | 16:25:45–16:25:48 | 0.05 | exit 4 `safety:board 30.6 W > 30 W on 3 samples`, 65 ms after the third live line over 30 W, inside the launch, which ended 223 ms later: passed |
| rest | 16:25:48–16:40:48 | — | E98's rule, 15 min |
| **G1Q** | 16:40:48–16:56:00 | 15.20 | REST 120 s (47 °C, 22.12 W), then 93 of 93 processes of `int8.b_line_zero_ff` 16:42:51–16:55:54 (the 57 °C gate passed at 47 °C; 8.42 s start to start), 1,751 launches |
| END | 16:56:00–16:58:02 | 2.03 | G1Q's cool-down |
| rest | 16:58:02–17:13:02 | — | 15 min |
| **G2Q** | 17:13:02–17:28:02 | 15.00 | REST 120 s (47 °C, 22.19 W), then 91 of 91 processes of `fp32.real_smol_softmax_v_causal` 17:15:05–17:27:56 (8.47 s start to start; the hold 12.9 min), 1,579 launches |
| END2 | 17:28:03–17:30:05 | 2.03 | G2Q's cool-down |

## Device commands sent

As registered ([`E161.md` § Device commands sent](../../../../tools/claims-v3/e161/E161.md#device-commands-sent); the audit,
[`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e161/logs/dmcmd-audit.txt): GO, 35 send sites, every one READ). In the session: the
sampler `ettelem sample --every-ms 100` without `--reset-ms` (`DM_CMD_GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`,
`GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`: READs, the PMIC voltage reads the owner allowed on 2 November 2026);
`ettelem config` (`GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`,
`GET_ASIC_VOLTAGE`: READs) at the session's two ends, at every step's ends and after every run; `ettelem sptrace` (MMIO read of the trace
region, no SP command). The residency read was **not sent** (22 answers unsent, `*/e161-not-sent.jsonl`). The C-logging host sends no
device-management command (the ops node only; its two extra transfers a launch are runtime DMA). **No write of any kind was sent**: no
statistics reset, no governor, TDP, threshold or clock set, no firmware-revisions query, no raw state-4 residency read, no reset.

## Departures (dated)

- **D1–D6, registered before any data** ([`E161.md`](../../../../tools/claims-v3/e161/E161.md#departures-from-q139es-plan-dated-before-any-data-tue-3-nov-2026-1555-1630-pst)):
  the C-logging host; the holds as process counts; the stop-path tests and the go gate; G1Q's FAIL line read on the plateau or the
  trajectory; the anchor and windows defined; E98's rest rule kept before both holds. D6's fallback was not needed: both rests ran in full.
- **D7 (Tue 3 Nov 2026, about 17:35 PST, after the data): the C log's δ was 2.0 ms a launch**, not E160's 1.5 ms. The DMA rule held (8.75 s of
  9.2 s). G2Q's processes ran 8.47 s start to start, not the planned 8.58 s, so its 91 processes made a 12.9-minute hold, not 13.0. Both
  scoring windows (the last 300 s, checkpoints to 750 s) sit inside it.
- **D8 (after the data): the reducer's "first step down" reads a process boundary**, as E144b's D5 found. [`posthoc_e161.py`](posthoc_e161.py)
  P3 reads the governor from the kernel launches instead. No verdict uses either.
- *(Dated note, Tue 3 Nov 2026, after verification, C4.)* **An interim look, not disclosed above.** Between the holds the lane ran the
  registered reducer on G1Q at 16:56:45 PST, which gave its three verdicts PASS and the plateau error −0.898 °C. It checked G1Q's C at
  16:57:34 PST. Both came before G2Q's step started at 17:13:02 PST ([`queue.jsonl`](queue.jsonl)). Nothing about G2Q changed: its
  predictions and rules were frozen in `455c46c1`, `e224a3f8` and `ddbd15b1`, the detached queue ran it as registered, and `queue.jsonl`
  records no skip or stop.

## What this cannot say

- One session, one card, one evening, two holds. The plateau moves 0.3–1 °C between sessions with nothing changed (item 8). Both rests read
  47 °C, a whole-degree reading, and the rest die is the room's only proxy: there is no inlet thermometer.
- In the trip regime G2Q tests the governor's hold and the clock it settles at, not the chain's plateau.
- G1Q's band (3.15 °C) is wide. Its PASS cannot separate M8 from M7 (−0.90 against −1.45 °C); the errors themselves, E − A and the session
  rms are the informative figures (Q139(e)'s D4).
- The work-share term is post hoc, read from this session's own samples. It is a candidate, not a tested prediction.
- *(Dated note, Tue 3 Nov 2026, after verification, C1.)* Its size depends on its definition: −0.88 to +0.12 °C on G1Q, +12.3 to
  −2.2 MHz on G2Q. Two small effects sit inside the registered readings. The window [t1 − 300, t1) ends 5.9–6.0 s after the hold's last
  process, which lowers the measured plateau by 0.055 / 0.061 °C and G2Q's clock by 1.4 MHz. And the frozen trajectory's last-300 s mean sits
  0.067 °C under G1Q's fixed point, the hold's finite length. Both are small next to the registered bands.
- 13-minute holds read about 98% of the closed loop's plateau on this card; a stage slower than about 10 minutes is not resolved.

## How to reproduce

```bash
/usr/bin/python3 tools/claims-v3/e161/reduce_e161.py docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2 \
    --json docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/results.json > docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/reduce.txt
/usr/bin/python3 docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/posthoc_e161.py > docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/posthoc.txt
# the check of C, on each step's C log gunzipped to a scratch file (ccheck.py reads plain JSON lines):
python3 tools/claims-v3/ccheck/ccheck.py check <scratch>/G1Q/c-log.jsonl --out docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/ccheck-G1Q.json --jobs 6
```

numpy 1.26.4, Python 3.9 at the desk. The reducer reads the `ccheck-*.json` summaries if they exist; its scores do not depend on them.

## Files

| file | what |
|---|---|
| `SMOKE/`, `STOPTEST-DIE/`, `STOPTEST-BOARD/`, `G1Q/`, `END/`, `G2Q/`, `END2/` | each step's session: `tel/*.jsonl.gz` (the 10 Hz sampler), `launches.jsonl.gz`, `c-log.jsonl.gz` (the C log), `runs.jsonl`, `marks.jsonl`, `queries.jsonl`, `session.json`, `e161.json` (the runner's hashes), snapshots and config reads, `e161-not-sent.jsonl` |
| `queue.jsonl`, `queue.out`, `status.json`, `schedule.json`, `GO` | the detached queue's record |
| `idle_logins.jsonl`, `phone.jsonl`, `history/` | the idle-login decisions (counts only), the camera phone's health, the three boxes' 5 s history over the session (numbers only) |
| `config-session-start.txt`, `config-session-end.txt` | `ettelem config` at the session's two ends |
| `ccheck-SMOKE.json`, `ccheck-STOPTEST-BOARD.json`, `ccheck-G1Q.json`, `ccheck-G2Q.json` | Q139(k)'s check of C, every launch |
| `results.json`, `reduce.txt` | the registered reduction (`reduce_e161.py`) |
| `posthoc_e161.py`, `posthoc.txt` | post hoc readings P1–P3 (no verdict uses them) |
| `corrections_e161.py`, `corrections.txt` | the corrections after verification, C0–C3 (post hoc; no verdict uses them) |

## Corrections after verification (Tue 3 Nov 2026)

*Written Tue 3 Nov 2026, about 18:10–18:27 PST, by the fix pass, after the data, the post hoc readings and the verifier's report. Desk
only: no card, no device command, no ssh to any box, nothing re-run. No measured, frozen or registered number, rule, prediction or verdict
changed; the registration (`tools/claims-v3/e161/`, `ddbd15b1`) is untouched. Every number here is printed by
[`corrections_e161.py`](corrections_e161.py) → [`corrections.txt`](corrections.txt). The script imports `posthoc_e161.py`'s helpers and the
frozen code unchanged, after `reduce_e161.py`'s sha256 check. It first reproduces P1's and P2's shares, fixed point and trip clock (C0), so
each alternative below differs from them only in the definition of the share.*

### C1 (major): the post hoc work share

**What the text said.** P1 and P2 read "6.0% of the samples fall between processes, where the card idles". They scaled the switching part
by a work share of 0.940 / 0.939, which gave G1Q **+0.12 °C** and G2Q's clock **−2.1 MHz**. From that they concluded that "most of G1Q's
−0.90 °C is the harness's duty, not M8's level or the chain".

**Where the samples fall.** The scoring window is [t1 − 300, t1], 2,998 samples per hold (`corrections.txt` C1
`where_the_window_samples_fall`):

| samples | G1Q share | G1Q board, clock | G2Q share | G2Q board, clock |
|---|---|---|---|---|
| after the hold's last process (the HOLD file runs 5.94 / 5.96 s past it) | 2.00% | 27.3 W, 627 MHz | 2.00% | 27.3 W, 613 MHz |
| in the gaps between processes (about 10 ms each) | 0.33% | 41.6 W, 800 MHz | 0.07% | 52.4 W, 600 MHz |
| in a process's first 0.3 s (the first launch starts 0.146–0.203 s in) | 3.37% | 37.7 W, 780 MHz | 3.40% | 37.5 W, 723 MHz |
| … of which before its first kernel launch | 1.70% | 36.4 W, 784 MHz | 1.67% | 36.2 W, 702 MHz |
| in a process's last 0.05 s | 0.33% | 45.2 W, 800 MHz | 0.63% | 46.8 W, 658 MHz |
| in kernel launches | 95.36% | 45.78 W, 794 MHz | 95.53% | 50.91 W, 681 MHz |
| in the post hoc's trimmed windows (P1, P2) | 93.96% | 45.90 W, 795 MHz | 93.90% | 51.14 W, 680 MHz |

So the 6.0% that P1 counted as idle is three different things:
- the registered window's last 6 s, after the work had ended (2.0%);
- each process's start-up, when the card already draws 36–39 W, and its last 0.05 s (3.7–4.0%);
- the ~10 ms gaps between processes (0.07–0.33%).

The verifier's reading, 2.33% / 2.07% "between processes, at an idle-level board", is the first and last of these together: 2.00 points of
it are the window's tail.

**The share by definition, and what each gives.** These use P1's and P2's formulas and the frozen code (`corrections.txt` C1
`work_share_by_definition`, `G1Q_plateau_at_each_share`, `G2Q_clock_at_each_share`):

| definition of the work share | G1Q share | G1Q plateau error | G2Q share | G2Q clock error |
|---|---|---|---|---|
| continuous work (as registered) | 1 | −0.90 °C | 1 | +12.6 MHz |
| `launches.jsonl` alone: process time over the hold's span | 0.999 | −0.88 °C | 0.999 | +12.3 MHz |
| **`launches.jsonl` alone: kernel-launch time over the hold's span (the hold's kernel duty)** | **0.970** | **−0.39 °C** | **0.970** | **+5.6 MHz** |
| window samples in process windows (the verifier's "process windows") | 0.977 | −0.51 °C | 0.979 | +7.8 MHz |
| window samples in kernel launches (the verifier's "kernel launches") | 0.954 | −0.12 °C | 0.955 | +2.0 MHz |
| window samples in the post hoc's trimmed windows (P1, P2) | 0.940 | +0.12 °C | 0.939 | −2.2 MHz |

- **The tail.** The three window-sample shares count the window's last 6 s as idle work time. The two from `launches.jsonl` count only
  the hold.
- **The rounding.** P2's clock, unrounded, is 682.27 MHz against a measured 680.09 MHz: −2.18 MHz, which rounds to **−2.2**, not −2.1
  (C0).
- **The window's end** (post hoc). Ended at the hold's last process instead, the window gives a measured plateau 0.055 °C higher on G1Q
  (0.061 °C on G2Q) and a G2Q clock 1.36 MHz higher. At the kernel duty G1Q would then read −0.33 °C and G2Q +7.0 MHz
  (`window_tail_effect`, the `…_window_ended_at_last_process…` keys).
- **The finite hold.** The 13-minute hold's frozen trajectory has a last-300 s mean 0.067 °C under G1Q's fixed point (`finite_hold`).

**What the rest of G1Q's error is** (post hoc; `decomposition_posthoc`). Inside the kernel launches at ≥ 790 MHz the card drew **0.91 W
less** than M8's 800 MHz board at the same die, sample by sample (47.03 against 46.16 W at the plateau's mean die):

| G1Q fixed point with | share | M8's level | plateau error |
|---|---|---|---|
| nothing changed (as registered) | 1 | as frozen | −0.90 °C |
| the kernel duty alone | 0.970 | as frozen | −0.39 °C |
| M8's level alone, set to the kernel launches' | 1 | −0.91 W | −0.04 °C |
| both | 0.970 | −0.91 W | +0.44 °C |

With both changes the error comes to +0.44 °C, near arm A's +0.37 °C given the measured watts. So the power path's −1.27 °C (E − A) is
about **−0.85 °C from M8's level** and about **−0.5 °C from the harness's kernel duty** (each read alone; together they move the error by
1.34 °C). The chain's own +0.37 °C offsets part of it. So M8's level is the larger part, not "the smaller part", and at the kernel duty the
duty is about half of G1Q's −0.90 °C, not most of it.

**At the trip (G2Q) the terms do not separate.** Inside the kernel launches, M8's board at the clocks the card ran is **1.61 W** above the
measured. With that level alone the clock error would be −5.6 MHz, and with the level and the kernel duty −12.6 MHz. With the level and the
measured held die (65.50 °C in place of the rule's 65.9) it would be −0.8 MHz, and −7.7 MHz adding the duty. One hold does not say which
terms close the clock.

**What to freeze before a blind test.**
- The share, as the hold's kernel duty from `launches.jsonl` alone: the time in kernel launches over the span from the first process's
  start to the last's end, 0.970 on this harness. Never take it from the telemetry.
- A scoring window that ends at the hold's last process, or a model of the tail.
- M8's level, as a separate term. In [E160's session](../2026-11-03-e160-blind6-aifoundry2/README.md) the three zeros anchors read
  1.49–1.85 W under M8, the same direction.

The duty term alone will not close G1Q's error.

### C2 (minor): "from the bits alone"

The lane's headline, this README's "Results first" and the registration's own words (`E161.md`, `tools/claims-v3/e161/README.md`) say the
die was predicted "from the tile's bits alone". Every prediction is anchored on the idle card's measured die and board just before the
hold: the mean of each REST file's last 120 s, 47.0 °C and 22.12 / 22.19 W from 1,199 samples each (`corrections.txt` C2). The die reads
whole degrees, so the anchor is known to ±0.5 °C. Over that range G1Q's plateau error moves from −0.19 to −1.61 °C, and G2Q's clock error
from +4.1 to +21.1 MHz. G2Q's plateau error does not move, because the trip does not move with the anchor, and every reading stays PASS
(`results.json` `posthoc_rest_quantization`). The accurate wording is: **from the tile's bits and the idle card's die and board just before
the hold (a ±0.5 °C anchor)**.

### C3 (minor): rank 4 is not answered

The lane's result said "Rank 4 is answered on aifoundry2". What E161 gives is **the first blind score of rank 4's aifoundry2 half**: one
session, two holds.
- G1Q's registered band, 3.149 °C, is 3.15 times the critic's 1.0 °C and 2.41 times its 1.305 °C (`corrections.txt` C3, from Q139(e)'s
  frozen `predictions-q139e.json`). So the PASS cannot separate M8 from M7 (−0.90 against −1.45 °C).
- At the critic's own scale, G1Q's plateau error (−0.90 °C) and trajectory rms (1.04 °C) fall inside 1.305 °C, but only as a post hoc
  reading.
- The critic asked for 3–4 kinds held across the two cards; this half held two. Rank 4 is not closed until E154's aifoundry3 half and a
  replicate session have been scored.

### C4 (minor): an interim look

Between the holds the lane ran the registered reducer on G1Q (16:56:45 PST; its three verdicts PASS, plateau error −0.898 °C) and Q139(k)'s
check of C on G1Q's launches (16:57:34 PST). Both times come from the lane's own working files, which are not committed. Both came before
G2Q's step started at 17:13:02 PST (`queue.jsonl`). Nothing about G2Q changed:
- its predictions and rules were frozen in `455c46c1`, `e224a3f8` and `ddbd15b1`;
- the detached queue ran it as registered;
- `queue.jsonl` records no skip or stop.

The README did not say that G1Q was scored between the holds. It does now, in the departures.

### C5 (minor): the registration's writing window

`E161.md` says it was written "about 15:55-16:30 PST", and it dates its departures the same way. It was committed at 16:22:46 PST
(`git show -s ddbd15b1`) and pushed at 16:22:49, so it was written between about 15:55 and 16:22 PST. The frozen file is not edited.

### How to reproduce

```bash
/usr/bin/python3 docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/corrections_e161.py \
    > docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/corrections.txt
```
