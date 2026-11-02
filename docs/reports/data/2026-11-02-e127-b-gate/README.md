# E127: the float B-lane gate held steady against switching it every cycle, at equal operand activity (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): item 6, "A power model across kinds", whose main open case is the float B-lane gate (the list as it reads at `fbb682f9393b`).*

*Mon 2 Nov 2026 (week 45), Q136, critic 3 of Q134's final critic. Pre-registered in `166fb897` (committed 07:59:39 PST, on origin/main
by 07:59:54), before the claim and the first launch: [`tools/claims-v3/e127/README.md`](../../../../tools/claims-v3/e127/README.md), frozen
numbers in `predictions-e127.json` (sha256 `da46530e…`), the scorer `score_e127.py`, self-test 34 of 34. **Every M5 and M4 prediction scored
is frozen there**: the ten new tiles' from the bench's counts (`counts-e127.json`), the three E115 tiles' copied from Q133(b)'s
`predictions-blind3.json` and reproduced to 0.0 W. aifoundry3 card 0 at 600 MHz in every sample, 521.7 mV mean; `ettelem config` read at the
session's start (08:01:16) and end (08:29:38) under the card lock with `timeout 10`: TDP 0 W, threshold 65 °C, 600 MHz, 523 mV, never set.
**Every device-management command sent was a read** (nine kinds, two of them PMIC voltage-register reads, which the owner's rule of 2 November
2026 allows; § Device commands sent); no governor move, no reset, no `--reset-ms`, no firmware-revisions query. The day's one card post in
#community-lab (message 1566837317765963987) was rewritten at 08:01:02 to add this card's clause and at 08:30:37 to drop it, every other
clause kept; card session 08:01:16–08:29:38, **28.4 of the 35 card-minutes allowed**
([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)). **No amendments.***

*Corrected after verification, Mon 2 Nov 2026, at the desk, with no card touched and nothing re-run on a card (§ [Corrections after
verification](#corrections-after-verification-mon-2-nov-2026), C1–C6). The reductions now name their raw root inside the repository
(re-reduced by the registered collector, every number byte-identical); lane position is stated as small but not zero, with its likely share
of the per-flip price (post hoc); fp16's ratio is stated beside its watts; the per-flip price and the all-off fraction carry their post hoc
label; the device-command list names the firmware build whose source it could not read; the registered "PMIC reading" stop is named for what
it reads; and a usage probe run before the claim is disclosed. No registered prediction, rule, number or verdict changed.*

**In plain words.** E115 found that the chip's power model, M5, prices the float lanes' zero gate wrong: switching every lane's gate on and
off each cycle costs 1.2 W more than the model says, against holding half the lanes off. Was that the gate itself, or the numbers moving
through the lanes? E127 held the numbers still — every product exactly zero, the operand bus moving the same 4,096 bits an op in every tile —
and moved only the gate. **The whole miss stays: +1.15 W with the data still against +1.17 W with random data, a ratio of 0.98 [0.90, 1.06];
in fp16 the quiet miss is the same in watts (+1.13 W), 0.87 [0.76, 0.99] of fp16's larger random-data miss.** About seven tenths of it goes
with each lane's own gate flipping, post hoc about 0.18 pJ a flip more than the simulation prices; the other three tenths with micro-ops whose
eight lanes are all off at once, where the card takes (post hoc) about two thirds of the clocking saving the simulation gives them. A lane held
off for 32 cycles at a time prices like a steadily held one, apart from that all-off part. ~~Which lanes are held off does not matter.~~
*[Note, Mon 2 Nov 2026, after verification (C2): it matters a little. Lanes 0–3 live cost +0.135 [+0.035, +0.235] W more than lanes 4–7 live
(Q5), an interval that excludes zero; R6's PASS says only that it is under the registered 0.30 W, and R6 is arm-sensitive. And `q_blk` −
`q_steady` (Q4) reads −0.47 W against M5's −0.83, an excess of +0.36 W: in 32-cycle stretches only the flips' part goes, and the all-off part
stays.]*
My frozen expectation for the split was wrong: I expected the all-off micro-ops to carry it.

## Results

**Five passes of five kept (12710–12714), 164 of 164 runs, none failing a run gate, on the registered primary (dips removed by E82 A2's
definition, 54 samples; leakage `auto`, 0.1913 W/°C over 77 runs). Every verdict is the same on the anchor footing.** The dips-kept arm sets
two passes aside (12712: `int8.full` spans 1.066 W; 12713: `anchor_pi` drifts +0.645 W), as on E115, so every verdict scored there is marked
arm-sensitive to it. [`scored.json`](scored.json) › `primary`, [`results.md`](results.md).

**1. Registered against what happened** (W; e(C) is a contrast's excess over M5's frozen point, with the contrast's 95% interval, t(4)):

| rule | what | line | result | verdict | arms that move it | what I expected, frozen |
|---|---|---|---|---|---|---|
| **E127-R1** | the replicate: B1 = `g_blanes_alt` − `g_blanes_steady` (fp32) above M5's frozen interval | above +1.34 W | **+1.956 ± 0.064 W** (E115 +2.003, −0.047); per pass +1.93, +1.92, +1.91, +2.02, +2.01 | **PASS** | dips kept (INCONCLUSIVE) | PASS |
| **E127-R2** | **the primary: with the data held still** (fp32), e(Q1), Q1 = `q_alt` − `q_steady` | ≥ ½ e(B1) = +0.587 W | **e(Q1) +1.154 [+1.050, +1.257] W**; e(B1) +1.173; ratio **0.98 [0.90, 1.06]** | **GATE** | dips kept (NOT SCORED) | GATE |
| **E127-R3** | the same in fp16, e(F2), F2 = `q_alt` − `q_steady` | ≥ ½ e(F1) = +0.646 W | **e(F2) +1.129 [+1.040, +1.219] W**; e(F1) +1.292; ratio 0.87 [0.76, 0.99] | **GATE** | none | GATE |
| **E127-R4** | each lane flipping, or all off together? (random) e(B3), B3 = `g_blanes_chk` − `g_blanes_steady` | ≥ +0.587 PER-LANE, ≤ ALL-OFF | **e(B3) +0.879 [+0.741, +1.018] W**; ratio 0.75 [0.62, 0.88] | **PER-LANE** | dips kept (NOT SCORED) | **ALL-OFF: wrong** |
| **E127-R4q** | the same with the data still, e(Q2), Q2 = `q_chk` − `q_steady` | ½ e(Q1) = +0.577 W | **e(Q2) +0.810 [+0.716, +0.904] W**; ratio 0.70 [0.66, 0.74] | **PER-LANE** | dips kept (NOT SCORED) | **ALL-OFF: wrong** |
| **E127-R5** | the time scale (data still), e(Q4), Q4 = `q_blk` − `q_steady` | ≤ +0.577 SHORT, ≥ LONG | **e(Q4) +0.358 [+0.285, +0.431] W**; ratio 0.31 [0.23, 0.39] | **SHORT** | dips kept (NOT SCORED), leakage 0.3803 (INCONCLUSIVE) | **LONG: wrong** |
| **E127-R6** | lane position (data still), Q5 = `q_steady_hi` − `q_steady` | \|Q5\| + h ≤ 0.30 W | **+0.135 ± 0.100 W** | **PASS** | dips kept, leakage 0.3803 and 0 (INCONCLUSIVE) | PASS |
| **E127-S1** | the session tie against E115 on this card | ±0.50 W, int8 ±0.25 | `fp32.randn` 24.77 (E115 24.63), `fp16.randn` 22.20 (22.06), `anchor_pi` 8.49 (8.35), `int8.full` 7.08 (7.10) | **PASS** | leakage 0 (FAIL: the anchors' level moves with the slope) | PASS |

Against what I expected: R1, R2, R3, R6 and S1 came in as frozen; **R4, R4q and R5 did not**. I expected the miss to go with the micro-ops whose
eight lanes are all off (ALL-OFF, and LONG for `q_blk`), because the bench puts its whole 0.86 W clocked-bit difference between E115's pair
there. The card says most of the miss is each lane's own flipping. (The registration's first draft, before the bench's counts, expected
PER-LANE and SHORT; the registration says so.)

**2. The contrasts** (D(plus) − D(minus) inside each pass, mean over five; M5's interval is the frozen one):

| contrast | measured, W | per pass | **M5 [95%]** | excess over M5 [95%] | M5 reads it |
|---|---:|---|---:|---:|---|
| `B1` `fp32.g_blanes_alt` − `fp32.g_blanes_steady` | +1.956 ± 0.064 | +1.93, +1.92, +1.91, +2.02, +2.01 | +0.78 [+0.23, +1.34] | **+1.173** [+1.110, +1.237] | ABOVE |
| `B2` `fp32.g_blanes_chk` − `fp32.g_blanes_alt` | +0.639 ± 0.156 | +0.54, +0.79, +0.67, +0.48, +0.70 | +0.93 [+0.37, +1.50] | −0.294 [−0.449, −0.138] | INSIDE |
| `B3` `fp32.g_blanes_chk` − `fp32.g_blanes_steady` | +2.595 ± 0.139 | +2.47, +2.71, +2.59, +2.50, +2.71 | +1.72 [+1.16, +2.27] | **+0.879** [+0.741, +1.018] | ABOVE |
| `Q1` `fp32.q_alt` − `fp32.q_steady` | +0.687 ± 0.104 | +0.63, +0.57, +0.76, +0.77, +0.70 | −0.47 [−1.00, +0.06] | **+1.154** [+1.050, +1.257] | ABOVE |
| `Q2` `fp32.q_chk` − `fp32.q_steady` | +1.275 ± 0.094 | +1.17, +1.22, +1.32, +1.36, +1.31 | +0.46 [−0.06, +0.99] | **+0.810** [+0.716, +0.904] | ABOVE |
| `Q3` `fp32.q_alt` − `fp32.q_chk` | −0.588 ± 0.051 | −0.54, −0.65, −0.56, −0.59, −0.61 | −0.93 [−1.46, −0.40] | +0.344 [+0.292, +0.395] | INSIDE |
| `Q4` `fp32.q_blk` − `fp32.q_steady` | −0.472 ± 0.073 | −0.47, −0.47, −0.48, −0.55, −0.39 | −0.83 [−1.36, −0.30] | +0.358 [+0.285, +0.431] | INSIDE |
| `Q5` `fp32.q_steady_hi` − `fp32.q_steady` | +0.135 ± 0.100 | +0.09, +0.03, +0.21, +0.12, +0.22 | −0.00 [−0.53, +0.52] | +0.140 [+0.040, +0.240] | INSIDE |
| `F1` `fp16.g_blanes_alt` − `fp16.g_blanes_steady` | +1.783 ± 0.145 | +1.73, +1.99, +1.69, +1.73, +1.77 | +0.49 [−0.01, +0.99] | **+1.292** [+1.147, +1.438] | ABOVE |
| `F2` `fp16.q_alt` − `fp16.q_steady` | +0.705 ± 0.089 | +0.61, +0.73, +0.80, +0.73, +0.66 | −0.42 [−0.90, +0.05] | **+1.129** [+1.040, +1.219] | ABOVE |
| `F3` `fp16.q_chk` − `fp16.q_steady` | +1.338 ± 0.136 | +1.24, +1.30, +1.42, +1.24, +1.48 | +0.51 [+0.03, +0.98] | **+0.830** [+0.694, +0.966] | ABOVE |

The sign tells it. With the data still, the bench says switching every lane every cycle is **cheaper** than holding half of them off (Q1,
−0.47 W, because micro-ops with all eight lanes off clock 0.86 W fewer register bits); the card says it costs **+0.69 W more**. The checkerboard,
with every lane flipping and four live in every micro-op, costs +1.28 W over the steady tile where the bench says +0.46 (Q2).

**3. Every tile** (D over the type's zeros, W, 95% over five passes; ⚠ outside M5's frozen interval):

| tile | family | B bus bits/op | gate flips/op | D [95%] | **M5 [95%]** | D − M5 | M4 | D − M4 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `fp32.q_steady` | quiet | 4,096 | 0 | 4.72 ± 0.04 | **4.98** [4.60, 5.35] | −0.26 | 5.03 | −0.31 |
| `fp32.q_steady_hi` | quiet | 4,096 | 0 | 4.85 ± 0.09 | **4.97** [4.60, 5.35] | −0.12 | 5.02 | −0.17 |
| `fp32.q_blk` | quiet | 4,096 | 128 | 4.25 ± 0.08 | **4.15** [3.77, 4.52] | +0.10 | 4.19 | +0.06 |
| `fp32.q_chk` ⚠ | quiet | 4,096 | 4,096 | 5.99 ± 0.12 | **5.44** [5.07, 5.82] | +0.55 | 5.46 | +0.53 |
| `fp32.q_alt` ⚠ | quiet | 4,096 | 4,096 | 5.40 ± 0.11 | **4.51** [4.14, 4.88] | +0.90 | 4.53 | +0.88 |
| `fp16.q_steady` | quiet | 4,096 | 0 | 4.76 ± 0.07 | **4.97** [4.64, 5.31] | −0.21 | 5.03 | −0.26 |
| `fp16.q_chk` ⚠ | quiet | 4,096 | 4,096 | 6.10 ± 0.09 | **5.48** [5.15, 5.82] | +0.62 | 5.50 | +0.60 |
| `fp16.q_alt` ⚠ | quiet | 4,096 | 4,096 | 5.47 ± 0.11 | **4.55** [4.22, 4.89] | +0.92 | 4.56 | +0.90 |
| `fp32.g_blanes_steady` ⚠ | bridge | 28,066 | 0 | 12.58 ± 0.02 | **13.22** [12.83, 13.60] | −0.63 | 13.21 | −0.63 |
| `fp32.g_blanes_chk` | random | 73,024 | 4,096 | 15.18 ± 0.13 | **14.93** [14.53, 15.33] | +0.24 | 14.87 | +0.30 |
| `fp32.g_blanes_alt` ⚠ | bridge | 73,024 | 4,096 | 14.54 ± 0.07 | **14.00** [13.60, 14.40] | +0.54 | 13.94 | +0.60 |
| `fp16.g_blanes_steady` ⚠ | random | 29,446 | 0 | 11.50 ± 0.15 | **11.95** [11.60, 12.30] | −0.46 | 12.03 | −0.53 |
| `fp16.g_blanes_alt` ⚠ | bridge | 70,112 | 4,096 | 13.28 ± 0.09 | **12.44** [12.08, 12.80] | +0.84 | 12.46 | +0.82 |

E115's three tiles repeat within 0.15 W of E115 on this card (`g_blanes_steady` 12.58 against 12.47, `g_blanes_alt` 14.54 against 14.47, fp16
`g_blanes_alt` 13.28 against 13.13), with this session's float anchors 0.14 W higher too (S1). 5 of 13 tiles are inside M5's intervals, and 5 of 13
inside M4's; every quiet tile whose lanes never flip, and `q_blk`, are among the five. Every tile ran at 546.001 cycles an op: no gate pattern
changes the time an op takes.

**4. Post hoc, labelled, never a verdict: the miss in two parts, each the same with the data still and with random data**
([`posthoc_e127.py`](posthoc_e127.py), [`posthoc_e127.txt`](posthoc_e127.txt)). By construction Q1 = Q2 + Q3 and B1 = B3 − B2, so their excesses
add exactly; what is informative is that each part reads alike at both data regimes:

| part | data still (fp32) | random data (fp32) | fp16, data still |
|---|---:|---:|---:|
| **each lane's gate flipping**, four live lanes in every micro-op, against the steady tile | e(Q2) **+0.810** [+0.716, +0.904] W | e(B3) **+0.879** [+0.741, +1.018] W | e(F3) +0.830 [+0.694, +0.966] W |
| **micro-ops with all eight lanes off**, at equal flipping | e(Q3) **+0.344** [+0.292, +0.395] W | −e(B2) **+0.294** [+0.138, +0.449] W | — |
| the whole miss | e(Q1) +1.154 | e(B1) +1.173 | e(F2) +1.129 |

- **Per flip.** Over the 4,096 gate flips an op at 1.121 × 10⁹ ops a second, the per-lane part is **176 fJ [156, 197] a lane-gate flip** beyond
  M5's price with the data still, 191 [161, 222] fJ with random data, and 181 [151, 210] fJ in fp16. For scale, M5 prices a core net's toggle at
  1.6 fJ and an operand-bus net's at 7.6 fJ; at this card's 521.7 mV, 176 fJ is what charging about 1.3 pF costs, a lane-wide net rather than a
  gate's own wire. One dose was run, so linearity in flips is not shown; `q_blk`'s 128 flips an op would add 0.025 W at that price, and its excess
  (+0.358 W) is the all-off part's (+0.344 W) to within 0.015 ± 0.09 W.
- **Lane position's share** (added Mon 2 Nov 2026, after verification, C2; [`corrections_e127.py`](corrections_e127.py),
  [`corrections_e127.txt`](corrections_e127.txt) § 3). Q2 compares `q_chk`, whose live lane-cycles fall half on lanes 0–3 (from the tiles'
  bytes), with `q_steady`, whose fall on lanes 4–7 only. If lane position adds per live lane-cycle (assumed; no tile pair here tests it), half of
  e(Q5) (+0.070 W) sits in e(Q2) as lane position, not flipping. Netted out, the per-lane part is +0.740 [+0.665, +0.816] W and the price
  **161 fJ [145, 178] a lane-gate flip** beyond M5's, against the 176 [156, 197] above. Q1, Q4, B1 and B3 carry the same half (B1 and B3 only if
  lane position is the same at random data, where no `q_steady_hi` twin ran; fp16's F2 and F3 carry fp16's own, unmeasured) and Q3 none, so the
  per-lane share of the quiet miss would be 0.68
  (0.73 random) instead of 0.70 (0.75), R2's ratio stays 0.98, and `q_blk` sits −0.055 [−0.160, +0.049] W from the all-off part.
- **The all-off part.** With the data still, the card reads `q_alt` 0.588 W below `q_chk` where the bench says 0.932 W (Q3), so it takes 0.63 of
  the clocking saving the bench gives micro-ops whose eight lanes are all off; with random data, 0.68 (B2). `q_blk`, whose off stretches are
  all-off micro-ops 32 cycles long, misses by the same amount. E115's A-side gates, which also turn whole micro-ops off, read inside its
  intervals, so this part is the B-lane gate's (an A-gated `q_alt` was not run).
- **Where the per-tile miss sits moves with the data; the contrast does not.** With the data still, the tiles whose lanes are held steady read
  inside M5's intervals (`q_steady` −0.26, `q_steady_hi` −0.12, fp16 −0.21 W) and the flipping ones above (+0.55 to +0.92 W). With random data,
  the steady tiles read below (−0.63, fp16 −0.46 W) and the flipping ones above by less (+0.24 to +0.84 W). So the first suspect, a steady lane
  being cheaper than priced, is not what the quiet tiles show: at quiet data the steady tiles are priced right and the switching costs more.

## What it changes

**For item 6 of section 11 ("A power model across kinds"), the float B-lane gate, its main open case.** E115's miss **replicates** on its own two
tiles in a new session (+1.96 W against +2.00, M5 +0.78 [+0.23, +1.34]), and it is **the gate's own, not the data's**: with every product zero
and the operand bus moving the same bits, switching every lane every cycle against holding half off reads +1.15 W above M5, 0.98 [0.90, 1.06]
of the random-data miss, and in fp16 the same in watts (+1.13 W; 0.87 [0.76, 0.99] of fp16's random-data miss). It is mostly **each lane's own
gate flipping** (0.70–0.75 of it; post hoc, about 0.18 pJ a flip more than the bench prices), and partly **micro-ops whose eight lanes are all
off**, which save (post hoc) about two thirds of the clocking the bench gives them. A lane off for 32 cycles at a time prices like a steady one
but for that all-off part; ~~lane position does not matter (0.14 ± 0.10 W)~~. *[Note, Mon 2 Nov 2026, after verification (C2): lane position
matters a little, +0.135 [+0.035, +0.235] W, an interval that excludes zero; R6's PASS bounds it under the registered 0.30 W only, and R6 is
arm-sensitive. If it adds per live lane-cycle, half of it sits in the per-lane part, and the price is about 0.16 pJ a flip (161 fJ [145, 178],
post hoc, § 4).]* What the
model needs is a term for the B-lane gate's flips (a fitted price per flip; Q133(b)'s forms had the flip count, `gtr`, and it did not help out of
kind on those rows, where flips came with moving data; E127's tiles separate the two), and a smaller saving for all-off micro-ops than the
bench's clocked bits give. **Still open in this case:** what physically spends the flips' price (post hoc 0.16–0.18 pJ; a lane's clock-gate enable and its clock branch
restarting, the gate's enable logic, the valid pipeline or the write-back mask; E127 cannot tell them apart); whether the price is linear in
flips (one dose); the A-side gate at equal activity; int8's gate (E115 read it inside); and a refit of M5 with the term, scored on tiles it
never saw.

**For the blog material:** switching a lane's zero gate costs energy of its own, whatever numbers pass through. On the ET-SoC-1 at 600 MHz,
with every product exactly zero and the operand wires moving the same bits, flipping every lane's gate on and off each cycle costs about 0.7 W
more than holding half the lanes off, where a power model priced from the chip's simulated RTL says it should cost 0.5 W less. Post hoc, the part
that goes with each lane's own gate is about 0.18 pJ more than the model prices for every time one lane's gate turns on or off (about 0.16 pJ if a
small lane-position effect is netted out), the energy of charging roughly a picofarad, which a model priced from the RTL's toggles does not see.
With the numbers held still, it is 0.98 [0.90, 1.06] of E115's 1.2 W miss in fp32 (in fp16, 0.87 [0.76, 0.99] of fp16's). So in a sparse matmul, how often the zeros' pattern changes from one cycle to the next sets part of the power,
not only how many zeros there are: zeros that hold a lane off steadily are cheaper than the same number scattered so that the lanes flicker.

## Device commands sent

As registered ([`tools/claims-v3/e127/README.md`](../../../../tools/claims-v3/e127/README.md) § Device commands sent, classified from the firmware
source at et-platform `836a4ab`, BL2 0.22.0, the build aifoundry3 reports): **nine management commands, every one a read**. `ettelem config`
(`GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`)
at the smoke's start and end, at both ends of each of the five passes and once at the session end: 13 reads of the five. `ettelem sample`
at 10 Hz through each block (`GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`,
`GET_ASIC_FREQUENCIES`; 15,684 samples in the five passes' telemetry, and two 1 s `die_c` samples at each block's two ends). The PMIC reads are
`GET_ASIC_VOLTAGE`'s two voltage registers and `GET_MODULE_VOLTAGE`'s nine, which the owner's rule of 2 November 2026 allows. **Not sent:** the
statistics reset (no E127 call passes `--reset-ms`; Q136(w)'s checker flags `lib.sh:154`'s forwarded arguments as a conditional reset, and E127's
only `start_sampler` call, `block_e127.sh:105`, forwards none: [`logs/dmcmd_audit_e127.txt`](logs/dmcmd_audit_e127.txt)), the firmware-revisions
query, any residency read, any set. The lib.sh drain (`dev_mngt_service -m DM_CMD_GET_MODULE_POWER`, a read) is not logged when it runs, so whether it
ran is not recorded; it can send only that one read, and no sampler failed to start (no "sampler failed" line in any block log). The host program opened the ops node only. Binaries: the registered `sparsity_host` `20e760c2…` and `ettelem` `16037641…`
([`logs/binaries.sha256`](logs/binaries.sha256)).

*Note added Mon 2 Nov 2026, after verification (C4): this list is the public BL2 0.22.0's, read at et-platform `836a4ab`; "the build
aifoundry3 reports" is a version, not a source. aifoundry3 runs the thermal firmware build flashed on 7 October 2026, which answers command 74
(`DM_CMD_GET_ASIC_PVT_SAMPLES`), absent from `836a4ab`, and whose source is not held
([`docs/findings/14-card-behaviour.md`](../../../findings/14-card-behaviour.md), "A finer reading exists on aifoundry3's firmware build";
E89). So "every command a read" on the running build rests on the public source plus the nine GETs' unchanged behaviour: they are the stock
telemetry this card has answered since 7 October, and E127's replies were normal (`since_reset_ms` −1 in all 16,155 samples, no reset). The
residual is the lab's, not E127's alone (the registration's "*a* 0.22.0", recorded by E69 and Q133; the thermal build, by E89 and E97);
nothing in E127 suggests a write.*

## How it ran

| | |
|---|---|
| desk | Mon 2 Nov 06:46–07:59 PST: the tiles (`make_e127.py`), the bench's counts on the Intel (Q133(b)'s binary and maps; the first run was cut by this session's own 30-minute limit on a background job while the Intel's load guard had it paused, and was rerun whole, 07:38:29–07:56:57), the freeze, the self-test, and a rehearsal of the box's `setup` with stand-in predictions (no device access; the stand-in files were replaced before the commit) |
| registration | `166fb897`, committed 07:59:39 PST; `run_e127.sh setup` on aifoundry3 07:59:55–08:00:12, no device access: every reused, code and tile hash identical, both binaries the registered ones, a `V3_DRY` pass of 35 launches (13 on E127 tiles), the queue's stub test ([`logs/box-setup.txt`](logs/box-setup.txt)) |
| before the claim | #community-lab read at 08:00 (the day's post held one clause, aifoundry2's); `et-who` 08:00:25: no process holds an ET-SoC-1 device node or card lock (other lab users' idle logins only, which E78's D1 rule lets pass) |
| smoke 12701 | 08:01:16–08:02:06: eight 2 s runs, cycles per op 546.0 on every item (the denormal tiles included), every record ok, 0.5995 GHz, launch coverage ≥ 0.9976; config TDP 0 / 65 °C / 600 MHz / 523 mV at both ends ([`logs/smoke.txt`](logs/smoke.txt)) |
| passes | 12710 08:02:16–08:08:20 (364 s); 12711 –08:13:48 (313 s); 12712 –08:18:56 (293 s; E78's launch rule skipped one `int8.zeros` run, "launch reading not reached", so that pass's int8 zero line rests on two runs); 12713 –08:24:21 (310 s); 12714 08:24:36–08:29:38: the budget rule let all five start ([`logs/e127-queue.log`](logs/e127-queue.log)) |
| stops | never near: the highest board reading in the five passes 53.84 W (stop 65 W) and die 62 °C (stop 70 °C) |
| end | the session-end read 08:29:38, TDP 0 / 65 °C / 600 MHz / 523 mV; `et-who` clean; the post rewritten at 08:30:37 to drop this clause |
| reduction | `collect_e127.sh` on the Intel at nice 10, from a copy of the raw passes: E78's `reduce_e78.py` unchanged (sha256 checked), dips removed (54 samples), leakage `auto` 0.1913 W/°C; E78-R5's checks: idle consistency median \|S − S0 − D\| 0.081 W (≤ 0.15), carry-over 0.0019 ± 0.0007 W/W (≤ 0.01), rail lag re-fit median 1.0 s, 600 MHz in every sample, 521.7 mV mean. Re-run after verification (Mon 2 Nov, 09:11 PST) over the committed passes with the repo-relative raw root: every output byte-identical but the raw-root paths (C1) |

## Departures

- **None from the registered procedure.** The primary, its arms and every rule ran as written.
- **Disclosed, not departures:** while pass 12714 ran, the collector was run as a pipeline check on pass 12710 alone and on 12710–12713;
  nothing registered was or could be changed by then, and the reported reading is the five-pass one. The registration's expectations were
  rewritten after the bench's counts and before the commit (its README says so).
- **Disclosed after verification (Mon 2 Nov 2026, C6), not a departure:** at about 07:04 PST, before the registration and the claim, a desk
  probe ran the box's `build/ettelem/ettelem` with no arguments to read its usage line, outside the card lock and without `timeout 10`. By its
  source (the box's `tools/ettelem/ettelem.cpp`, identical to `de262730`), `main()` returns on `argc < 2` before it constructs `Dm`, which is
  what loads libDM and opens the management node, so no command reached the card. A device binary should still not run outside a claim on
  that reasoning alone: pre-claim probes keep to reads that execute nothing on a device path (`strings -a` on the binary gives the same usage
  text).

## What this cannot say

One card, the card M5's constants are on, and one clock. "The gate's own" means everything that changes with the gate pattern at equal operand
bits — clock gating, the gate's enable logic, the valid pipeline, the write-back mask — and E127 cannot tell those apart. The per-flip price rests
on one dose (4,096 flips an op) and assumes linearity (and, since the verification, on how lane position is counted: C2). The quiet tiles rest on the denormal flush (the manual, the RTL and E93's power reading; no
result was read back). M5 is priced on the public RTL's later revision and on merged nets, not wires, so the post hoc "176 fJ" is a price beyond M5's, not a
measured wire. The A-side gate at equal activity and int8 were not run.

## Files

- [`results.md`](results.md), [`scored.json`](scored.json): the registered reading, every rule and contrast, with the anchor footing and every arm.
- `e127.json`, `runs.csv`, `reduce.txt`: the primary reduction (dips removed); `e127-dipskept.json`, `e127-leak{0.1994,0.3803,0}.json`,
  `e127-gatesoff.json` and their csv/txt/log files: the arms.
- [`posthoc_e127.py`](posthoc_e127.py), [`posthoc_e127.txt`](posthoc_e127.txt): § 4's numbers, from `scored.json`, standard library only.
- [`corrections_e127.py`](corrections_e127.py), [`corrections_e127.txt`](corrections_e127.txt) (added after verification): the numbers of
  § Corrections after verification, post hoc, from `scored.json` and the tiles' bytes, standard library only.
- `aifoundry3/kinds/p12710`–`p12714`, `kinds-smoke-p12701`: every pass's raw data (runs, marks, telemetry, dumped tiles, config reads, manifest);
  `logs/`: the queue log, the dry run, the setup and smoke transcripts, the session reads, the binaries' sha256, Q136(w)'s checker output, the times
  and the post's texts.
- `code.sha256`: every file the run and the reduction used.
- Registration, tiles, counts and code: [`tools/claims-v3/e127/`](../../../../tools/claims-v3/e127/README.md). The model: Q133(b),
  [`../2026-11-01-q133b-power-model/`](../2026-11-01-q133b-power-model/README.md); the miss it answers: E115, [`../2026-11-01-e115-blind-pool/`](../2026-11-01-e115-blind-pool/README.md) § 6.

To reproduce from the committed raw passes (a python with numpy), from the repository root:
`PY=python3 bash tools/claims-v3/e127/collect_e127.sh 'p127[1-9][0-9]' docs/reports/data/2026-11-02-e127-b-gate/aifoundry3`. It writes
`build/e127-out/2026-11-02-e127-b-gate/`, whose `e127*.json`, `runs*.csv`, `reduce*`, `scored.json`, `results.md`, `score.log` and
`code.sha256` are byte-identical to these (the reductions name that repo-relative raw root in `dirs` and the `dir` column; C1). From a copy
of the box's tree instead, `<raw dir>` holds `kinds/p12710`–`p12714`, `kinds-smoke/p12701` and `logs/`. Then
`python3 docs/reports/data/2026-11-02-e127-b-gate/posthoc_e127.py` and `corrections_e127.py`.

## Corrections after verification (Mon 2 Nov 2026)

An independent verifier (Q136's) checked E127 the same morning, after the data commit (`9b6311c7`). Its verdict: holds with fixes, two major
faults (one in public text, one in how two results were stated) and six minor ones. It re-reduced the committed raw passes with the registered
reducer (`e127.json`'s 400 per-pass values to a difference of 0), re-scored them (`scored.json` and `results.md` exact), re-derived every rule's
verdict and interval by hand, rebuilt the tiles' figures from their bytes, and found the registration's timing, the frozen rules, the
write-command list, the stops, the card's state and the posting protocol sound; no write command was sent. Each fault is corrected here, at the
desk: no card was touched, and no registered prediction, rule, number or verdict changed (R1 PASS, R2 GATE, R3 GATE, R4 PER-LANE, R4q PER-LANE,
R5 SHORT, R6 PASS, S1 PASS). `scored.json`, `results.md`, `reduce*`, `score.log`, `code.sha256`, `posthoc_e127.*`, `logs/` and the raw passes
are byte-identical to `9b6311c7`.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Desk paths in public files.** The six reductions (`e127*.json`, `dirs`, five lines each) and their six `runs*.csv` (`dir` column, 164 rows each) named the raw root as the lane's scratch folder on the desk machine, an absolute home path: 1,014 lines. The lane's public-text scan had a pattern for it but was not run on the reducer's outputs | The registered collector (code unchanged since `166fb897`) was re-run over the committed raw passes from the repository root with the raw root `docs/reports/data/2026-11-02-e127-b-gate/aifoundry3`. The 12 files now read `docs/reports/data/2026-11-02-e127-b-gate/aifoundry3/kinds/p127<nn>`, and each equals its first version with only that prefix replaced; every other output of the collector is byte-identical to `9b6311c7`. A scan of every text file in this directory and in `tools/claims-v3/e127/` (CSV, JSON, logs and the gzipped telemetry included) then finds no desk path, tailnet link, archive name, credential, foundry identifier or other user's login. Git history keeps the old text |
| C2 | **Lane position and the 32-cycle stretches, overstated.** "Which lanes are held off does not matter" (In plain words) and "lane position does not matter (0.14 ± 0.10 W)" (What it changes): Q5 = +0.135 [+0.035, +0.235] W excludes zero; R6's PASS bounds it under 0.30 W only, and R6 reads INCONCLUSIVE at three arms. The lane's blog text also said a lane held off 32 cycles at a time "prices like a steady one" without this page's qualifier: Q4 = `q_blk` − `q_steady` reads −0.47 W against M5's −0.83, an excess of +0.36 W, which is the all-off part (e(Q4) − e(Q3) = +0.015 [−0.083, +0.112] W) | Both sentences struck through and kept, each with a dated note beside it. § 4 gains a post hoc line on lane position's share: if it adds per live lane-cycle, half of e(Q5) sits in Q2 (and in Q1, Q4, B1 and B3; none in Q3), and the per-flip price is then 161 fJ [145, 178] rather than 176 [156, 197] ([`corrections_e127.txt`](corrections_e127.txt) §§ 1–3) |
| C3 | **fp16, and the post hoc labels.** "And the same in fp16" (In plain words, What it changes): fp16's ratio is 0.87 [0.76, 0.99], an interval that excludes 1; what is the same is the quiet miss in watts (e(Q1) − e(F2) = +0.024 [−0.079, +0.128] W). The 0.18 pJ a flip and the "two thirds" of the all-off saving appeared outside § 4 without their post hoc label, and the 0.18 pJ is the price beyond M5's (M5 already prices +0.465 W of Q2's +1.275 W, with no per-flip term), not a flip's whole cost | fp16's ratio is stated beside its watts; "post hoc" and "more than the model prices" stand wherever those numbers appear outside § 4, which already said "beyond M5" ([`corrections_e127.txt`](corrections_e127.txt) §§ 4–5) |
| C4 | **The firmware build the command list could not read.** § Device commands sent called `836a4ab` "the build aifoundry3 reports"; aifoundry3 runs the thermal build flashed on 7 October, which answers command 74 (absent from `836a4ab`) and whose source is not held | A dated note under § Device commands sent, here and in the registration: classified from the public 0.22.0; on the running build the nine GETs' class rests on that source and on their unchanged behaviour |
| C5 | **The registered "PMIC reading ≥ 80 °C" stop is not a PMIC reading.** `run_e78.py` compares `temp_c.pmic` with `--max-c` + 10, and at `836a4ab` `get_module_current_temperature` fills that field (`pmic_sys`) from `pvt_get_minion_avg_temperature`, the minion shires' PVT average: it equals `minshire[0]` in 16,149 of E127's 16,155 samples (±1 °C in the other 6) | A dated note in the registration's § Stops: E127's two temperature stops were both die readings (70 and 80 °C), it read no PMIC temperature, and its margin to a PMIC over-temperature rested on board power (at most 53.84 W) and die temperature (at most 62 °C). Later lanes should not count the field as a PMIC guard |
| C6 | **A device binary run before the claim.** At about 07:04 PST a desk probe ran `ettelem` with no arguments on aifoundry3, outside the card lock and without `timeout 10`; by its source it returns before it loads libDM, so no command was sent | Listed under § Departures as disclosed, with the practice it breaks: probes before a claim execute nothing on a device path (`strings -a`) |

Three more of the verifier's faults were in the lane's report to the integration lanes, not on this page (its blog points 2, 3 and 5, the
kinds-table cells it lacked, and its summary of the arms, where this page's "arms that move it" column was right); they were corrected there.
