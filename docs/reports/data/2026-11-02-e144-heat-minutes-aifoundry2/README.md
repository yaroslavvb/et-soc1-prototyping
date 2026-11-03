# E144b data: heat over minutes on aifoundry2 under its own governor, Q138(t)'s frozen holds scored blind (Q138, Mon 2 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 9**, "A steady state for heat", and **item 8**, "The heat path drifts between sessions". This is E144's aifoundry2 arm. E144's
aifoundry3 arm is a separate lane.*

*Pre-registered in [`tools/claims-v3/e144b/E144b.md`](../../../../tools/claims-v3/e144b/E144b.md), committed as **`71645e59`** at
21:58:22 PST and pushed before the claim and before any device access. The frozen inputs are Q138(t)'s files at amendment A1's commit
**`c2f9920d`** ([`../2026-11-02-q138t-heat-model/`](../2026-11-02-q138t-heat-model/README.md)), which was on origin/main before the claim.
[`reduce_e144b.py`](../../../../tools/claims-v3/e144b/reduce_e144b.py) checked their sha256 before scoring. Nothing was refitted or tuned.*

*The session, on aifoundry2 card 0 only:*
- *Claimed at 22:00:25 PST by rewriting the day's one `#community-lab` post (message `1566837317765963987`).*
- *The detached queue had started at 21:58:33 and waited for the go. The go came over ssh at 22:00:53 (`GO`). At that moment the box's
  copies of the runner, the queue and the seven protocols matched origin/main byte for byte.*
- *Card runs 22:00:53–23:10:07 PST: **39.22 card-minutes of 40**.*
- *`ettelem config` read 65 W / 65 °C (low_power, 600 MHz, 519 mV) at every read, from the session-start read (22:00:53) to the
  session-end read (23:10:07). Nothing was set, and **every command sent was a READ**. The residency read was answered unsent 22 times
  and never sent.*
- *Released at 23:10:53 PST: this card's clause was dropped from the post and the aifoundry3 clause kept word for word.*
- *The lab's Tailscale approval lapsed from about 22:04 to 22:08 PST. The queue ran on, detached, and the protocol of section 9 was
  followed (one line in the orchestrator's `tailscale-needed.txt`, probes every 3 minutes). The first probe answered at 22:08:28.*

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 00:15 PST; desk only: no card opened, no device command, nothing
re-run). An independent verifier reproduced `reduce.txt` and `results.json` byte for byte from the committed data, re-derived every score
with its own code, and confirmed that every command sent was a read. It found five faults (one major, four minor). None changes a measured
number, a registered rule, a prediction or a verdict. Each is corrected in place, marked "corrected after verification, C<n>", and listed
in [§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The numbers they quote are printed by
[`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt), using Q138(t)'s frozen code as
committed. The main one, C1: the per-kind heat coefficient this README named as the next term is withdrawn. The two holds differ in clock,
voltage, watts and governor state as well as in format, and E111 read the same two kinds equal over the same window. The whole-degree
rest readings alone allow tonight's gap to be anywhere from −0.007 to +0.080 °C per board W. The registration
([`tools/claims-v3/e144b/E144b.md`](../../../../tools/claims-v3/e144b/E144b.md), `71645e59`) is frozen. A dated note under it adds
`et-lab-manifest` to its no-device row (C5).*

## Results first

**Six of the scorer's seven registered readings PASS blind, and so does this registration's clock rule (E144b-K1).** The seventh is G1's
frozen t63 rule. It has no FAIL band, and amendment A1.8 had said, before the run, that it would read NOT PASS even if the model is right.
It read NOT PASS. A1.8's closed-loop reference beside it reads PASS ([`results.json`](results.json) `score`, `K1`;
[`reduce.txt`](reduce.txt)).

| hold | rest die | arm | measured | frozen prediction | error | band | verdict | M6 as frozen, beside |
|---|---|---|---|---|---|---|---|---|
| **G1**: int8 −1s, 800 MHz, 15.0 min | 46.00 °C | (a) the chain on the measured board | rms **0.762 °C**; plateau error **+0.724** | — | — | PASS: rms ≤ 1.20, \|plateau\| ≤ 1.30 | **PASS** | rms 1.593; plateau +0.626 |
| | | (b) the planned power | plateau rise **12.923 °C** | 11.833 °C | **+1.090** | PASS within ±1.30 | **PASS** | 11.933: +0.990 |
| | | (c) rise per board W, last 300 s | **0.711** | [0.62, 0.74] | — | PASS inside | **PASS** | — |
| | | (c) t63 | 79.1 s | 49.6 s open loop (A1.8: 76.0 s closed) | ×1.59 (A1.8: ×1.04) | PASS within ×0.75–1.33 | NOT PASS, as A1.8 expected (A1.8: **PASS**) | — |
| | | **E144b-K1**: share at ≥ 790 MHz, last 300 s | **0.962** (mean 792.7 MHz) | "800 MHz, the governor never trips" | — | PASS ≥ 0.90 | **PASS** | — |
| **G2**: fp32 random, governed, 15.2 min | 46.00 °C | (a) the chain on the measured board | rms **0.369 °C**; plateau error **+0.123** | — | — | as G1 | **PASS** | rms 2.198; plateau −0.053 |
| | | (b) the trip rule: max(rest + 21.49, 65.9) | plateau **67.288 °C**, regime **floor** (600 MHz in 1.000 of the last 300 s) | **67.493 °C, floor** (the rest die is 1.6 °C above the 44.41 °C edge) | **−0.205** | PASS within ±0.60 and the regime as predicted | **PASS** | floor only: 67.884, −0.596 |

**Over the rest die's whole-degree reading** *(table added after verification, C2)*. Both RESTs read 46 °C in every sample of their last
120 s (1,199 of 1,199), so the anchor every arm uses is known only to ±0.5 °C. The verdicts above are the registered ones: A1.3 defines
the rest die as that reading. Read post hoc, here is what each reading does when the frozen scorer is run with the anchor moved across
45.50–46.50 °C ([`corrections-numbers.txt`](corrections-numbers.txt) C2):

| reading | as registered (rest die 46.00 °C) | over a rest die of 45.50–46.50 °C | holds over the whole range? |
|---|---|---|---|
| G1 (a): rms; plateau error | 0.762; +0.724 °C: PASS | 0.370–1.235; +0.224 to +1.224 | no: INCONCLUSIVE below 45.54 °C (rms over 1.20) |
| G1 (b): plateau rise − 11.833 | +1.090 °C: PASS | +0.590 to +1.590 | no: INCONCLUSIVE below 45.79 °C |
| G1 (c): rise per board W | 0.711: PASS | 0.684–0.739 | yes |
| G1 (c): t63 against the open loop's 49.6 s | ×1.595: NOT PASS | ×1.301–1.615 | no: PASS below about 45.55 °C |
| G1 (c): t63 against A1.8's closed 76.0 s | ×1.041: PASS | ×0.849–1.054 | yes |
| E144b-K1 | 0.962: PASS | (no anchor) | yes |
| G2 (a): rms; plateau error | 0.369; +0.123 °C: PASS | 0.369–0.633; −0.377 to +0.623 | yes |
| G2 (b): plateau − max(rest + 21.49, 65.9) | −0.205 °C, floor as predicted: PASS | −0.705 to +0.295; the floor predicted throughout | no: INCONCLUSIVE above 46.40 °C |

So three of the six scorer readings that PASS, and K1, hold over the whole range: G1's rise per board W, A1.8's t63 and G2 (a). G1 (a),
G1 (b) and G2 (b) do not, and none of the eight reads FAIL anywhere in the range. This counts the rest reading's quantization only. The
plateaus are whole-degree readings too. In G1's last 300 s, 2,843 of 2,998 samples read 59 °C (the others are the dips between
processes), so its level is close to a single reading; G2's split 1,873 at 67 °C and 1,061 at 68 °C. Their quantization is not counted
here, and it could widen these ranges.

1. **The heat path holds on a third session, blind.** Q138(t)'s chain (R 0.663 °C per board W, five stages, t63 50 s) was fitted on
   E111 (1 Nov) and E133 (2 Nov, morning). Given tonight's measured board trace and the rest die's reading, it follows the die through
   both 15-minute holds to **0.76 °C rms (int8 −1s) and 0.37 °C rms (fp32 random)**: 0.37–1.24 and 0.37–0.63 °C over that reading's
   ±0.5 °C *(the reading and the ranges added after verification, C2 and C4)*. M6's frozen four-pole step response, scaled by 0.675 °C per
   board W, misses by 1.59 and 2.20 °C.
2. **The governor's regime was predicted from the rest die alone, and the prediction held. Q138(t)'s frozen description of the clock did
   not.** Tonight's free card idled at 46 °C, two degrees above E133's morning. The trip rule therefore put G2 in the floor regime, where
   the die settles at rest + 21.49 °C, and it did: the clock read 600 MHz in every sample of the last 300 s, and the plateau came out at
   67.29 °C, 0.21 °C under the rule. The regime was predicted correctly over the whole anchor range, since 46 ± 0.5 °C is 1.1–2.1 °C above
   the 44.41 °C edge. But the frozen statement of how the clock gets there, "800 MHz until the die reads 66, then the floor", did not hold
   *(corrected after verification, C3: this said "the clock steps to 600 MHz once the die reads 66 and stays there … That is what
   happened")*. The following times count from the start of the first `sparsity_host` process:
   - the clock reached 800 MHz at 1.1 s;
   - **the power limit stepped it down at 2.3 s**, to 700 MHz. The SP's running average then read 65.5 W, over the 65 W TDP, and the die
     52 °C, under its 65 °C threshold;
   - from then on the clock moved between 600, 700 and 800 MHz, and up to 128.6 s it read 800 MHz in only 14.6% of the samples;
   - the die first read 66 at 58.3 s;
   - the clock kept leaving the floor for another 70 s. Its last sample above 610 MHz came at 128.6 s (700 MHz), and from there it read
     600 MHz to the end;
   - the board peaked at 87.98 W at 61.6 s, at 700 MHz, 3.3 s after the die's first 66.

   Altogether the clock spent 19.6 s at 800 MHz ([`corrections-numbers.txt`](corrections-numbers.txt) C3).
   [`posthoc.txt`](posthoc.txt) § G2 times the same samples from the hold file's first sampler line, which came 1.28 s before the process
   started *(time base added after verification, C3)*. Its 2.4 s is the first 800 MHz sample. Its 3.8 s is the first sample at or under
   610 MHz, 2.5 s here and 0.2 s after the 700 MHz step. Its 59.5, 129.9 and 62.9 s are the die's first 66, the last sample above
   610 MHz and the board's peak.
3. **What is left is a level. These holds cannot say whether it depends on the kind** *(corrected after verification, C1: this said
   "What is left is a level, and it depends on the kind. int8 −1s heats the die about 7% more per board watt than the chain's 0.663: 0.711
   tonight, against 0.675 for fp32 random in the same session")*.
   - G1's plateau sits 0.72 °C over the chain given its own board watts, and 1.09 °C over the planned-power arm.
   - Of that 1.09 °C, about 0.2 °C comes from the board: it rose 18.17 W against the planned 17.84 W ([`posthoc.txt`](posthoc.txt) § G1).
     *(C1: "because the rest was warmer" is withdrawn; nothing here tests it.)*
   - At every checkpoint G1's rise ran 0.54–1.05 °C over the frozen curve (60 s, 2, 5 and 10 min: +0.68, +1.05, +0.54, +0.86 °C). With the
     rest die as read, that is inside (b)'s ±1.30 band at each one.

   Tonight int8 −1s reads 0.711 °C per board W against fp32 random's 0.675. That gap is not shown to be a format effect:
   - (i) the two holds differ in more than format: in clock and voltage (800 against 600 MHz), in board watts (18 against 32 W over
     idle) and in governor state;
   - (ii) the two whole-degree rest readings alone allow the gap to lie anywhere from −0.007 to +0.080 °C per W (−0.002 to +0.084 over
     600–900 s);
   - (iii) E111, the model's own training session, read the same two kinds equal, in the same floor regime: 0.7096 against 0.7016 °C per
     W over each hold's last 300 s, both near their plateaus at the end of 27-minute holds. Over 600–900 s it read 0.6854 against 0.6839,
     but there its fp32 hold had started warm, after E98's probe series and an int8 probe. Every int8 hold, and tonight's G2, started from
     rest.

   What does repeat is narrower, and each level below carries its own rest reading's ±0.5 °C
   ([`corrections-numbers.txt`](corrections-numbers.txt) C1):
   - int8 −1s at 800 MHz sits above the chain's single coefficient in all three sessions: by +0.73, +0.71 and +0.72 °C over each hold's
     last 300 s (E111 and E133 in sample), and by +0.34, +0.51 and +0.73 °C over the same 600–900 s window;
   - fp32 random's error moves from −0.24 °C (E133, at the governor's trip) to +0.99 °C (E111) over the last 300 s, and from −0.34 to
     +0.67 °C over 600–900 s.
4. **Item 8, between sessions: no move is resolved** *(corrected after verification, C2: this said "So tonight reads 3–4% higher, about
   0.4 °C at this power. That is the size of the session-to-session move item 8 names, and no model term carries it")*.
   - By the scorer's metric over the last 300 s, the int8 hold reads 0.7096 (E111, 1 Nov), 0.7134 (E133, 2 Nov morning) and **0.7111**
     tonight. The rest die read 46, 44 and 46 °C *(C2: this said the idle die "moved from 44 to 46 °C")*.
   - Those windows differ: tonight's last 300 s run 600–903 s, while E111's and E133's come at the end of 27-minute holds. Like for like,
     over 600–900 s, the three read 0.685, 0.689 and 0.707 °C per W (Q138(t) A1 `C8`; corrections C1). Tonight is about 3% higher, 0.3–0.4 °C
     at this power.
   - But one whole-degree rest reading alone moves a reading by ±0.028 °C per W (about ±4%). So the difference sits inside the readings'
     quantization, and no drift between these sessions is resolved.
   - The rest die is the room's only proxy, and the inlet stays unread.
5. **Safety.** No stop fired in either hold. G1 peaked at 41.27 W with the die at 60 °C. G2 peaked at **87.98 W**, with 79 samples over
   85 W and none over 90 W; its die reached 68 °C and the hottest sensor's running maximum 70 °C. The stops were 72 °C and 93 W on 3
   samples. G2 is the same hold as E111's (88.04 W) and E133's (88.65 W), and like them it raised no alarm. The stop path was tested on
   live samples in the smoke, before either hold. The die stop tripped 62 ms after the first live line at or above 30 °C, before any
   launch. The board stop tripped 62 ms after the third live line over 30 W, inside the launch, and the launch ended 186 ms later
   ([`queue.jsonl`](queue.jsonl) `stoptest_detail`).

## What this does to predicting power and heat

**The term tested:** the time-resolved heat path on a governed card, which is Q138(t)'s chain from board watts to the die, together with
the governor's trip rule that decides where the die settles. It was tested blind, on a session neither was fitted on.

| what is predicted | before: the desk's out-of-sample error (Q138(t), `cv-q138t.json`, A1 `A1_7_before_after`) | after: E144b, blind, a third session |
|---|---|---|
| **The die through a governed hold, given its board trace** (arm a) | the chain, fitted on one day and scored on the other: 0.44–1.16 °C rms, mean 0.79; M6's F(t) × 0.675 used as a chain: 0.47–1.28, mean 1.01; one pole of 89 s: 0.91–1.21, mean 0.99. Those six holds are four of 26.6–27.2 minutes and two warm probes of 5.7 minutes. The same session-out chains on the four long holds cut to E144b's 15-minute lengths (post hoc): **0.42–1.07 °C, mean 0.75** (int8 −1s from rest 0.42 and 0.90; fp32 random 0.63 and 1.07, those two begun warm, after E98's probe series) *(hold lengths and the cut added after verification, C2)* | **the chain: 0.76 °C (int8 −1s), 0.37 °C (fp32 random)**; plateau +0.72 / +0.12 °C. Over the rest reading's ±0.5 °C: 0.37–1.24 and 0.37–0.63 °C (C2). M6 as frozen: 1.59 / 2.20 °C |
| **The plateau from the planned power only** (arm b) | G1: no blind reading (in sample, E133's W1B reads +0.47 °C by the same rule); G2's rule back-checked on E111 (+0.71, floor) and E133 (−0.08, trip), in sample | **G1 +1.09 °C** (M6 +0.99); **G2 −0.21 °C**, the floor regime predicted and found (M6, which has no governor term, −0.60). Over the rest reading's ±0.5 °C: +0.59 to +1.59 and −0.70 to +0.30 °C (C2) |
| **Where the governor holds fp32 random** (G2's regime) | the rule max(rest + 21.49, 65.9): the regime edge at a rest die of 44.41 °C | correct from a 46 °C rest: the floor, with 600 MHz in 1.000 of the last 300 s. It is the floor over the whole anchor range |

So the die's trajectory over a quarter hour on this card can now be quoted at **about 0.4–0.8 °C rms given the board's watts and the rest
die's reading** (0.4–1.2 °C over that reading's ±0.5 °C). Its plateau can be quoted at **about 1 °C from the planned power** (within
1.6 °C over the same range). At one hold length the blind scores (0.76 and 0.37 °C) are no worse than the desk's session-out scores
(0.42–1.07 °C, mean 0.75), so the desk's error bar for the heat path held on a third session. What is left is a level, not a shape.

*Corrected after verification, C1.* This paragraph named the next term as "a per-kind heat coefficient (int8 −1s 0.711, fp32 random
0.675 °C per board W, against the chain's single 0.663), which would take most of G1's +0.7–1.1 °C". That is withdrawn. Here format is
confounded with clock, voltage, watts and governor state; E111 read the two kinds equal; and tonight's gap is inside the rest readings'
quantization (result 3). What the level needs, in order:

1. **A die reading finer than a whole degree, at rest and in the plateau.** Every level in question here, 0.1–1 °C, is the size of one
   reading's ±0.5 °C. Until the reading is finer, a kind effect, the drift between sessions and the chain's single coefficient cannot be
   told apart. Two candidates exist: E98's watt-derived rest die, which Q138(t) did not use, and the raw sensor codes that E97's harness
   reads on aifoundry3 (not yet read on aifoundry2).
2. **A matched test of format**: int8 and fp32 held at the same board watts and one clock, so that format is the only difference. It must
   resolve about 0.04 °C per board W, which is tonight's unresolved gap and about 0.7 °C at 18 W.
3. **An inlet thermometer**, for the moves between sessions (item 8). The lab does not record the inlet.

## The session, step by step

| step | ran (PST) | card-min | result |
|---|---|---|---|
| SMOKE | 22:00:53–22:01:36 | 0.72 | exit 0, three launches rc 0, config 65 W / 65 °C: smoke check passed |
| STOPTEST-DIE | 22:01:36–22:01:38 | 0.03 | exit 4 `safety:die 69 C >= 30 C` (the hottest sensor's carried 69 °C; the die mean 46), 62 ms after the first live line, no launch: passed |
| STOPTEST-BOARD | 22:01:38–22:01:42 | 0.07 | exit 4 `safety:board 36.5 W > 30 W on 3 samples`, 62 ms after the third live line over 30 W, inside the launch, which ended 186 ms later: passed |
| rest | 22:01:42–22:16:42 | — | E98's rule, 15 min |
| **G1** | 22:16:42–22:33:47 | 17.09 | REST 120 s (46 °C, 21.94 W), then 107 of 107 processes of int8 −1s from 22:18:45 (the 57 °C gate passed at 46 °C) |
| END | 22:33:47–22:35:49 | 2.03 | G1's cool-down: 55 → 48 °C |
| rest | 22:35:49–22:50:50 | — | 15 min |
| **G2** | 22:50:50–23:08:05 | 17.25 | REST 120 s (46 °C, 21.91 W), then 106 of 106 processes of fp32 randn from 22:52:52 |
| END2 | 23:08:05–23:10:07 | 2.03 | G2's cool-down: 62 → 49 °C |

No other user was logged in to aifoundry2 at any check ([`idle_logins.jsonl`](idle_logins.jsonl), counts only), and `et-who` showed the
card free before the go and after the end.

## Departures (dated)

- **D1–D4, registered before any data** ([`E144b.md`](../../../../tools/claims-v3/e144b/E144b.md#departures-from-q138ts-plan-dated-before-any-data)):
  END and END2 ran right after their holds; the stop-path tests and the go gate were added; the holds were set as process counts; and
  E144b-K1 was added.
- **D5 (Mon 2 Nov 2026, 23:15 PST, after the data): the reducer's descriptive "first step down" says nothing.** It reads the first busy
  sample at or under 610 MHz. On G1 that was a sample at a process boundary (24.7 s, die 51 °C). On G2 it was the launch's own first
  sample. Neither marks a step by the governor. [`posthoc.txt`](posthoc.txt) reads G2's clock properly, post hoc: the first sample at
  800 MHz, the first step down after it, the die's first 66, and the last sample above the floor. No verdict uses any of it.
  *(Time bases added after verification, C3. `posthoc.txt` times these from the hold file's first sampler line, 1.28 s before the first
  `sparsity_host` process started. `results.json`'s `first_step_down` counts from the first sample over 30 W, 0.53 s (G1) and 0.32 s (G2)
  after the process started. Its G1 sample, 25.2 s after that start, falls 0.04 s into the fourth process, before that process's first
  kernel launch, so it is a process boundary. [`corrections-numbers.txt`](corrections-numbers.txt) C3 times G2's clock from the process's
  start.)*
- **D6: the Tailscale lapse**, 22:04–22:08 PST, during the rest before G1. The queue needs no ssh, so it had no effect.
- **D7: the go came over ssh** (`GO`, 22:00:53). The fallback marker `tools/claims-v3/e144b/CLAIMED` was never needed and never committed.

## Device commands sent

Every one was a READ, and no WRITE of any kind was sent, not even the statistics reset. The registration has the full table
([`E144b.md` § Device commands sent](../../../../tools/claims-v3/e144b/E144b.md#device-commands-sent)), and the audit
([`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e144b/logs/dmcmd-audit.txt)) read GO: 35 send sites, with E133's two reviewed
exceptions. The counts below come from the records ([`posthoc.txt`](posthoc.txt) § 5).

| command | sent by, when | count | class (et-platform `836a4ab`, BL2 0.22.0) |
|---|---|---|---|
| `ettelem sample` (no `--reset-ms`): `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_FREQUENCIES` | the sampler, every 100 ms through every run | 23,447 sampler lines | READ (RAM copies; PVT and PLL registers read) |
| `ettelem sample`: `GET_ASIC_VOLTAGE` (2 PMIC voltage-register reads), `GET_MODULE_VOLTAGE` (9) | the sampler, every sample | as above | READ (the owner's allowed read-only PMIC voltage reads, 2 Nov 2026) |
| `ettelem config`: `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` (2 PMIC voltage-register reads) | `run_hpl.py:626`, in each of its 22 query sets (at each session's start, after every run and at its end; the two stop tests, which ended at their stop, have the start set only); the queue at each step's start and end (14); the session-end read (1) | **37** | READ (RAM copies; PLL registers and the allowed PMIC voltage reads) *(row rebuilt after verification, C5: it had three cells, and no count)* |
| `ettelem sptrace` | `run_hpl.py:618`, in each of its 22 query sets | 22 | READ (an MMIO copy of the SP trace region; no SP command) |
| `ettelem residency 2 3 4 5 6` (`run_hpl.py:622`) | — | 22 answered unsent | **NOT SENT** (`e144b-not-sent.jsonl` in each step) |
| `dev_mngt_service -m DM_CMD_GET_MODULE_POWER` | `run_hpl.py`'s drain, only if a sampler fails | 0 | READ |
| `sparsity_host` (E80's binary, sha256 `7adadf4f…`, checked by the runner) | every launch | 3 (smoke) + 1 (board stop test) + 107 + 106 processes | not device management (the ops node only) |
| `et-lab-manifest` (`run_hpl.py:824`), `et-who`, `sensors -j`, `uptime`, `who`, `ps`, `flock`, `git fetch` / `git show`, the camera phone's `/health` | `et-lab-manifest` at each `run_hpl` session's start, one `manifest.txt` per step; the others around each step | 7 `et-lab-manifest` | no device command: no `/dev/et*` node opened. `et-lab-manifest` reads sysfs and files only ([`tools/lab/et-lab-manifest`](../../../../tools/lab/et-lab-manifest), sha256 `6fbb4e10…`). The box's installed copy is the same, checked read-only by the verifier at 23:41 PST *(row added after verification, C5)* |
| any WRITE | — | **0** | **NONE SENT** |

## Files

| file | what |
|---|---|
| `README.md` | this |
| `results.json`, `reduce.txt` | `reduce_e144b.py`'s output: the frozen inputs' hashes, `score_e144.py a2 G1 G2` as committed at `c2f9920d`, E144b-K1, and the clock and safety readings |
| `posthoc_e144b.py`, `posthoc.txt` | post hoc readings, no verdict: G1's checkpoints, the board against the planned trace, G2's clock timeline, the idles, and the command counts |
| `corrections-numbers.py`, `corrections-numbers.txt`, `corrections-numbers.json` | *(added after verification)* every number the corrections C1–C5 quote, printed from committed files with Q138(t)'s frozen code imported as committed: rise per board W by kind and session (C1), the scores over the rest reading's ±0.5 °C and the before at one hold length (C2), G2's clock with its time bases (C3), the command counts (C5). No verdict |
| `SMOKE/`, `STOPTEST-DIE/`, `STOPTEST-BOARD/`, `G1/`, `END/`, `G2/`, `END2/` | each step's session: `tel/*.jsonl.gz` (the 10 Hz sampler), `launches.jsonl.gz`, `runs.jsonl`, `marks.jsonl`, `queries.jsonl`, `end.json`, `e144b.json` (hashes), `e144b-not-sent.jsonl`, the queue's `snapshot-*`, `config-*` and `sensors-*`, `sp/` (the SP trace ring) |
| `queue.jsonl`, `queue.out`, `schedule.json`, `status.json`, `GO`, `idle_logins.jsonl`, `phone.jsonl` | the queue's records, the go, the idle-login decisions (counts only) and the camera phone's health (descriptive) |
| `config-session-end.txt` | the session-end `ettelem config` (23:10:07 PST) |
| `history/` | the three boxes' own 5 s history over the session, numbers only |

## How to reproduce

```bash
/usr/bin/python3 tools/claims-v3/e144b/reduce_e144b.py docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2 > docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/reduce.txt
/usr/bin/python3 docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/posthoc_e144b.py > docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/posthoc.txt
/usr/bin/python3 docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/corrections-numbers.py > docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/corrections-numbers.txt
```

These need numpy 1.26.4 (the desk's system Python 3.9). The scorer is Q138(t)'s `score_e144.py`, unchanged. The third line was added after
verification and takes about 40 s; it also writes `corrections-numbers.json`.

## Corrections after verification (Tue 3 Nov 2026)

An independent verifier checked E144b on the night of 2 Nov 2026:
- It reproduced `reduce.txt` and `results.json` byte for byte from git-archived trees, and re-derived every score with its own code.
- It matched the 12 committed telemetry files to the box's raw files.
- It re-ran the command audit (GO, 35 send sites, every one a READ), and confirmed from the SP's statistics and trace rings that no reset
  and no write reached the card.

It found five faults, all in how the result was read. They are corrected above, in place, with dated markers. Nothing here changes a
measured number, a registered rule, a frozen prediction or a verdict. The registration's text (`tools/claims-v3/e144b/`, `71645e59`;
a dated note is appended under `E144b.md`, C5), `results.json`, `reduce.txt`, `posthoc.txt` and the raw data are unchanged. The numbers below are in
[`corrections-numbers.txt`](corrections-numbers.txt). That file is post hoc, desk only, and uses Q138(t)'s frozen code as committed at
`c2f9920d` after checking its seven sha256.

- **C1 (major): no per-kind heat coefficient is supported.** Result 3 and the prediction section put tonight's 0.711 against 0.675 °C per
  board W down to the number format, and named a per-kind coefficient as the next term. The data commit's subject (`30ae5368`) said
  "int8 heats 7% more per board W than the chain's 0.663". That reading is right (×1.073), but reading it as a property of int8 is
  withdrawn, for three reasons:
  - The two holds differ in clock and voltage (800 against 600 MHz), in watts over idle (18.2 against 31.6 W) and in governor state, as
    well as in format.
  - The two whole-degree rest readings alone (±0.5 °C each, so ±0.028 and ±0.016 °C per W) allow the gap to be −0.007 to +0.080 °C per W
    over the last 300 s, and −0.002 to +0.084 over 600–900 s.
  - E111 read the two kinds equal, in the same floor regime. The gap was +0.0079 ± 0.0432 °C per W over each hold's last 300 s, both
    near their plateaus. Over 600–900 s it was +0.0015 ± 0.0435, but there its fp32 hold had started warm, after the probe series. E133's
    fp32 hold sat at the governor's trip, not at the floor.

  What repeats is narrower: **int8 −1s at 800 MHz sits above the chain's single 0.663 in all three sessions** (+0.73, +0.71, +0.72 °C
  over each hold's last 300 s; +0.34, +0.51, +0.73 °C over 600–900 s; E111 and E133 in sample). fp32 random's error moves from −0.24 to
  +0.99 °C (−0.34 to +0.67 over 600–900 s). Corrected in result 3 and in the section on prediction. The next steps there are now a die
  reading finer than a whole degree and a matched-watts, single-clock test of format.
- **C2 (minor): the scored errors had no intervals.**
  - The table after "Results first" now gives each reading over a rest die of 45.50–46.50 °C, from the frozen scorer with the anchor
    moved, and says which PASSes hold over the whole range: G1's rise per board W, A1.8's t63, G2 (a) and K1. G1 (a), G1 (b) and G2 (b)
    do not; G1's frozen t63 NOT PASS turns PASS below about 45.55 °C; nothing reads FAIL.
  - Result 4's "+3–4% tonight, the size of the move item 8 names" sits inside one reading's ±0.028 °C per W (about ±4%), so no drift is
    resolved. Like for like over 600–900 s it is +3%.
  - The before in the prediction table mixed four holds of 26.6–27.2 minutes with two 5.7-minute probes. Cut post hoc to E144b's
    lengths, the four long holds read 0.42–1.07 °C rms session-out (mean 0.75), against 0.567–1.058 (mean 0.78) whole. The two int8
    holds there started from rest, like G1. The two fp32 holds began warm, after E98's probe series, unlike G2.
  - Result 4's "the idle die moved from 44 to 46 °C" is corrected to 46, 44 and 46 °C.
- **C3 (minor): G2's clock was described wrongly, and the time bases were not stated.** Result 2 said the clock steps to 600 MHz once the
  die reads 66, "That is what happened".
  - In fact the power limit stepped it down 2.3 s after the first process started. The SP's running average read 65.5 W against the
    65 W TDP, with the die at 52 °C.
  - The clock then moved between 600, 700 and 800 MHz (800 MHz in 14.6% of the samples up to 128.6 s), and kept leaving the floor for
    70 s after the die's first 66. The 87.98 W peak came at 700 MHz.
  - "First step down 3.8 s (board 61.3 W)" quoted the first sample at or under 610 MHz, timed from the hold file's first sampler line,
    1.28 s before the process started. It is the board after the step, not the average that triggered it.
  - The verifier's report says that `results.json`'s times also count from the sampler's start. They do not: `first_step_down` counts
    from the first sample over 30 W, 0.53 s (G1) and 0.32 s (G2) after the process started, and D5 already says what it reads.

  Every post-hoc time now names its base.
- **C4 (minor): M6 is a four-pole step response.** The lane's blog point called it "a one-number step response", the reading Q138(t)'s C1
  withdrew. M6 froze F(t) with τ 1.005, 15.98, 138.2 and 1500 s, times 0.675 °C per board W on aifoundry2. Result 1 now names it so. "Given
  the board's watts" now adds "and the rest die's reading", the anchor every arm uses.
- **C5 (minor): the command table.** The `ettelem config` row had three cells in four columns and no count. It is rebuilt: **37 reads**,
  made of the 22 `run_hpl` query sets, the queue's 14 and the session-end read. The `sptrace` row now says 22. `et-lab-manifest`
  (`run_hpl.py:824`, 7 calls, one per step) was named in neither table's no-device row. It now has a row here, and a dated note under the
  frozen registration's table. It reads sysfs and files only and opens no `/dev/et*` node, so the classification is unchanged.
