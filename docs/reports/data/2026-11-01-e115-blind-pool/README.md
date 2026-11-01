# E115: blind pool 3 on the card — the power model M5 against 25 tiles written before it was read (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): item 6, "A power model across kinds" (the list as it read at `1fe8377a18af`).*

*Sun 1 Nov 2026 (week 44), Q133. Pre-registered in `3b0264dd`, pushed 15:02:49 PST, before the claim and the first launch:
[`tools/claims-v3/e115/README.md`](../../../../tools/claims-v3/e115/README.md), frozen numbers in `predictions-e115.json` (sha256 `0e40c3d6…`),
the scorer `score_e115.py`, self-test 25 of 25. **Every prediction scored is Q133(b)'s**, checked by sha256 before every run, reduction
and score: the pool ([`blind3.json`](../../../../tools/claims-v3/kinds/blind3/README.md), `a9167033`), M5 and the pool's predictions from M5
and M4 (`64b4124e`), the contrasts' 95% intervals (`0fae735f`). aifoundry3 card 0 at 600 MHz in every sample, 521.6 mV mean; `ettelem config`
read at the session's start (15:04:5x) and end (15:29:44) under the card lock with `timeout 10`: TDP 0 W, threshold 65 °C, 600 MHz, 523 mV,
never set. No governor move, no reset, no `--reset-ms`, no PMIC command. Claim 1566588818621206619 in #community-lab, posted 15:04:40 PST,
released by editing it at 15:30:16 PST (held 25.6 min); card session 15:04:52–15:29:44, **24.9 of the 30 card-minutes allowed**
([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)). **No amendments.***

**In plain words.** Q133(b)'s model M5 predicts what a matmul tile costs from a simulation of the chip's RTL and six fitted constants;
scored on the kinds it was fitted on, leaving each kind out in turn, it reads 0.20 W rms. Here it predicted 25 tiles built on the
cases it was known to be weak on, written before anyone read its numbers, on the card its constants come from. **Over the 16 main float
tiles it reads 0.29 W rms, 0.003 W above the 0.288 W its own score allows for 16 tiles: the registered rule fails, by a hair.** int8 reads
0.34 W and passes. 18 of the 25 tiles land inside their 95% intervals (72%), and 4 of the 7 built-in contrasts. The misses are not where I
expected: the sums that cancel came in inside, and the gate is what the model gets wrong. **A lane gate held steady costs 0.74–0.76 W less
than the model says, in two tiles, and a gate that switches every lane each cycle 0.48–0.69 W more**, so switching the gate costs +2.00 W
where the model says +0.78 W [0.23, 1.34]. The memory-path pair lands on the model to 0.005 W. M5 does not measurably beat M4.

## Results

**The registered primary scores nothing; the registered fallback does, and every verdict below is that fallback, labelled.** E78's
random-range gate (1.0 W) set two of the three passes aside: pass 11510 because `fp16.randn` spans 1.210 W, pass 11511 because `fp32.randn`
spans 2.217 W ([`reduce.txt`](reduce.txt), `e115.json` › `passes_set_aside`). Both spans are the board meter's dips: E82 amendment A2's
definition finds 14, 8 and 12 dip samples in the three passes (`e115-nodips.json` › `reducer.dip_samples_removed`), and with them removed
every pass is kept and the anchors repeat to 0.02 W (`fp32.randn` 24.629, 24.618, 24.636 W). So the primary keeps one pass and every rule
reads NOT SCORED there ([`scored.json`](scored.json)), and the registration names what is reported then: **"the dips-removed arm is then the
reading reported, labelled as that arm"** ([`results-nodips.md`](results-nodips.md), [`scored-nodips.json`](scored-nodips.json); with every arm beside,
[`results-nodips-arms.md`](results-nodips-arms.md), [`scored-nodips-arms.json`](scored-nodips-arms.json)). 134 of 135 planned runs ran and all 134 are
kept there; E78's launch rule skipped one, `fp16.zeros` in pass 11510 (#8, "launch reading not reached"), so that pass's fp16 zero line rests
on two runs.

**1. Registered against what happened** (the dips-removed arm, a3 footing; W):

| rule | what | threshold | result | verdict | anchor footing | the other arms | what I expected, frozen |
|---|---|---|---:|---|---|---|---|
| **E115-R1** | **the float family:** rms(D − M5), the 16 priority-1 float tiles | PASS ≤ 0.288 W, the nested-LOO interval for 16 tiles [0.135, 0.288] | **0.2905 W** (bootstrap over tiles 0.171–0.402), bias −0.02 W; M4 0.321 W | **FAIL**, by 0.003 W | PASS, 0.283 W | FAIL at leakage 0.1994 (0.315), 0.3803 (0.398) and 0 (0.660), and gates off (0.295) | PASS near 0.27 W |
| **E115-R2** | **the int8 family:** rms(D − M5), the 6 int8 tiles | PASS ≤ 0.432 W [0.124, 0.432] | **0.343 W** (0.132–0.544), bias +0.20 W (the model high); M4 0.394 W | **PASS** | PASS, 0.383 W | PASS in every arm | PASS |
| **E115-R3** | **coverage:** D inside M5's frozen 95% interval, all 25 | PASS ≥ 80%, FAIL < 60% | **18 of 25, 72%**: fp32 10 of 14, fp16 3 of 5, int8 5 of 6 (M4: 18 of 25) | **INCONCLUSIVE** | INCONCLUSIVE | FAIL at leakage 0 (56%) | PASS, about 21 of 25 |
| **E115-R4** | **the seven contrasts** inside their frozen intervals | PASS ≥ 6 of 7, FAIL ≤ 4 | **4 of 7**; ABOVE: the gate's switching, the exponents' gate, fp16's cancelling | **FAIL** | FAIL | INCONCLUSIVE at leakage 0 | PASS or INCONCLUSIVE |
| **E115-R5** | **M5 against M4:** rms(D − M4) − rms(D − M5), 16 floats | M5 BETTER if the 95% interval is above 0 | **+0.030 W [−0.005, +0.074]** (0.321 against 0.291 W; 4.4% of draws at or below 0) | **UNRESOLVED** | M5 BETTER, +0.024 W [+0.005, +0.049] | UNRESOLVED in every arm | UNRESOLVED |
| **E115-S1** | the session tie against E78 | ±0.50 W, int8 ±0.25 W | `fp32.randn` 24.63 (E78 24.72), `fp16.randn` 22.06 (22.16), `anchor_pi` 8.35 (8.36), `int8.full` 7.10 (7.06) | **PASS** | PASS | FAIL at leakage 0.3803 and 0 (the anchors' level moves with the slope) | PASS |

The leakage arms above are run on the dips-removed reduction, after the data and labelled: the registration defined them on the primary,
which keeps one pass (§ Departures). **R1's FAIL is the registered verdict and it is marginal.** It holds at every leakage slope and with the
pass gates opened. It does not hold on the anchor footing (0.283 W, inside) or without the one flagged tile (`fp16.s_wpair0`, whose bench count
carries fp16's window-model residue: 0.280 W against that set's 0.292 W). Neither of those is the verdict. On this card's own rows the nested
interval would be tighter ([0.125, 0.236] W, reported beside), so a reader who prefers that reference sees a clearer fail, and against the
283-row interval [0.180, 0.222] W the pool's 0.29 W sits above too.

Against what I expected: R1 failed where I expected a pass at 0.27 W; R4 failed where I expected PASS or INCONCLUSIVE; R3 came in lower (18,
not 21). And the misses are not where I said: the fp32 sign tiles came in inside their intervals and the gate is what broke.

**2. Every tile** (the dips-removed arm; D is 95% over three passes, t(2) = 4.30; ⚠ D outside M5's frozen interval; † the flagged count):

| tile | open case | prio | D, W [95%] | **M5 [95%]** | D − M5 | M4 | D − M4 | F0r |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `fp16.a_mant_b_randn` | a-side-busy-partner | 1 | 21.65 ± 0.06 | **21.78** [21.43, 22.14] | **−0.13** | 21.98 | −0.32 | 21.92 |
| `fp32.a_colconst_b_randn` ⚠ | a-side-busy-partner | 2 | 22.69 ± 0.05 | **23.17** [22.72, 23.61] | **−0.48** | 23.15 | −0.46 | 23.07 |
| `fp32.a_lo8_b_pi` | a-side-busy-partner | 1 | 10.59 ± 0.12 | **10.68** [10.29, 11.07] | **−0.10** | 10.82 | −0.23 | 10.72 |
| `fp32.a_lo8_b_randn` | a-side-busy-partner | 1 | 22.29 ± 0.44 | **22.23** [21.80, 22.65] | **+0.06** | 22.18 | +0.12 | 22.10 |
| `int8.a_colconst_b_full` ⚠ | a-side-busy-partner | 2 | 2.42 ± 0.10 | **3.17** [2.50, 3.84] | **−0.75** | 3.30 | −0.87 | 3.17 |
| `int8.a_low2_b_full` | a-side-busy-partner | 1 | 4.70 ± 0.26 | **4.82** [4.29, 5.36] | **−0.13** | 4.87 | −0.17 | 4.82 |
| `int8.st_f32bytes` | another-stream | 2 | 6.86 ± 0.11 | **6.69** [6.22, 7.16] | **+0.16** | 6.63 | +0.23 | 6.69 |
| `fp16.x_logu_s50` | exponents-spread-gate | 1 | 7.63 ± 0.09 | **7.71** [7.35, 8.07] | **−0.08** | 7.69 | −0.06 | 7.72 |
| `fp32.x_logu_bsteady` ⚠ | exponents-spread-gate | 2 | 13.12 ± 0.07 | **13.88** [13.49, 14.26] | **−0.76** | 13.82 | −0.70 | 13.78 |
| `fp32.x_logu_s50` | exponents-spread-gate | 1 | 8.11 ± 0.11 | **8.27** [7.88, 8.66] | **−0.16** | 8.20 | −0.09 | 8.22 |
| `fp16.g_blanes_alt` ⚠ | gated-kinds | 2 | 13.13 ± 0.19 | **12.44** [12.08, 12.80] | **+0.69** | 12.46 | +0.68 | 12.48 |
| `fp32.g_arows_alt` | gated-kinds | 1 | 13.48 ± 0.12 | **13.29** [12.90, 13.69] | **+0.19** | 13.24 | +0.25 | 13.22 |
| `fp32.g_blanes_alt` ⚠ | gated-kinds | 1 | 14.47 ± 0.14 | **14.00** [13.60, 14.40] | **+0.48** | 13.94 | +0.54 | 13.94 |
| `fp32.g_blanes_steady` ⚠ | gated-kinds | 1 | 12.47 ± 0.12 | **13.22** [12.83, 13.60] | **−0.74** | 13.21 | −0.74 | 13.16 |
| `int8.g_awords_alt` | gated-kinds | 1 | 4.45 ± 0.32 | **4.71** [4.24, 5.17] | **−0.26** | 4.69 | −0.24 | 4.71 |
| `int8.g_bpairs_steady` | gated-kinds | 1 | 3.55 ± 0.26 | **3.76** [3.30, 4.21] | **−0.20** | 3.71 | −0.16 | 3.76 |
| `fp32.m_blines_eq` | memory-path | 1 | 24.77 ± 0.06 | **24.80** [24.40, 25.20] | **−0.03** | 24.79 | −0.02 | 24.70 |
| `fp32.m_bpair_eq` | memory-path | 1 | 16.39 ± 0.08 | **16.42** [16.03, 16.80] | **−0.03** | 16.48 | −0.10 | 16.38 |
| `fp16.s_inword0` | signs-moving-sums | 1 | 16.49 ± 0.07 | **16.68** [16.34, 17.02] | **−0.19** | 16.88 | −0.39 | 16.80 |
| `fp16.s_wpair0` † ⚠ | signs-moving-sums | 1 | 21.86 ± 0.15 | **21.44** [21.08, 21.81] | **+0.41** | 21.56 | +0.30 | 21.51 |
| `fp32.s_bridge` | signs-moving-sums | 1 | 25.67 ± 0.11 | **25.32** [24.93, 25.72] | **+0.35** | 25.27 | +0.40 | 25.19 |
| `fp32.s_drift12` | signs-moving-sums | 1 | 24.78 ± 0.24 | **24.70** [24.30, 25.11] | **+0.07** | 24.71 | +0.07 | 24.61 |
| `fp32.s_pair0` | signs-moving-sums | 1 | 25.00 ± 0.14 | **24.64** [24.25, 25.03] | **+0.36** | 24.62 | +0.38 | 24.54 |
| `fp32.z_single` | zero-level | 1 | −0.06 ± 0.05 | **0.01** [−0.36, 0.39] | **−0.08** | 0.01 | −0.08 | 0.01 |
| `int8.z_diag` | zero-level | 1 | 1.81 ± 0.22 | **1.85** [1.39, 2.31] | **−0.04** | 1.88 | −0.07 | 1.85 |

**3. The contrasts** (D(plus) − D(minus) inside each pass, averaged; the interval is the measurement's, t(2); M5's is the frozen one):

| contrast | measured, W | **M5 [95%]** | verdict | M4 | per pass |
|---|---:|---:|---|---:|---|
| `fp32.g_blanes_alt` − `fp32.g_blanes_steady` | +2.00 ± 0.09 | **+0.78** [+0.23, +1.34] | **ABOVE** | +0.73 (outside its interval) | +1.96, +2.02, +2.02 |
| `fp32.a_lo8_b_randn` − `fp32.a_lo8_b_pi` | +11.71 ± 0.48 | **+11.55** [+10.97, +12.12] | **INSIDE** | +11.36 | +11.75, +11.87, +11.49 |
| `fp32.m_blines_eq` − `fp32.m_bpair_eq` | +8.39 ± 0.12 | **+8.38** [+7.82, +8.94] | **INSIDE** | +8.31 | +8.36, +8.44, +8.35 |
| `fp32.s_drift12` − `fp32.s_pair0` | −0.22 ± 0.29 | **+0.06** [−0.50, +0.63] | **INSIDE** | +0.08 | −0.35, −0.19, −0.13 |
| `fp32.s_bridge` − `fp32.s_pair0` | +0.67 ± 0.20 | **+0.68** [+0.12, +1.24] | **INSIDE** | +0.65 | +0.70, +0.59, +0.74 |
| `fp32.x_logu_s50` − `fp32.x_logu_bsteady` | −5.01 ± 0.08 | **−5.61** [−6.16, −5.06] | **ABOVE** | −5.62 (outside its interval) | −5.05, −4.99, −5.00 |
| `fp16.s_wpair0` † − `fp16.s_inword0` | +5.37 ± 0.21 | **+4.76** [+4.26, +5.26] | **ABOVE** | +4.68 (outside its interval) | +5.42, +5.27, +5.41 |

**The memory-path pair reads INSIDE, and closely: +8.387 W against +8.382 W predicted**, each tile within 0.03 W of M5, the measurement's own
95% ±0.12 W. As registered, that says no memory-path term between B lines that change and B half-lines that change, beyond the bench's compute
and bus, at the interval's resolution (±0.56 W); it does not say there is none. The three that miss all read ABOVE, and two of them are the same
thing seen twice (§ 4).

**4. By open case** (`scored-nodips.json` › `primary.reported.by_open_case`; mean D − M5 with its 95% interval over the case's tiles):

| open case | n | mean D − M5, W | rms M5 | rms M4 | inside |
|---|---:|---:|---:|---:|---|
| fp32/fp16 signs on moving sums | 5 | +0.20 ± 0.32 | 0.304 | 0.333 | 4 of 5 |
| exponents spread under a gate | 3 | −0.34 ± 0.92 | 0.452 | 0.410 | 2 of 3 |
| gated kinds | 6 | +0.03 ± 0.55 | 0.483 | 0.489 | 3 of 6 |
| the A side with a busy partner | 6 | −0.25 ± 0.31 | 0.372 | 0.443 | 4 of 6 |
| the memory path's own term | 2 | −0.03 ± 0.03 | 0.029 | 0.068 | 2 of 2 |
| the zero level | 2 | −0.06 ± 0.23 | 0.062 | 0.074 | 2 of 2 |
| another stream (int8 on fp32 words) | 1 | +0.16 | 0.163 | 0.226 | 1 of 1 |

- **Signs on moving sums, fp32: inside.** `s_pair0` +0.36, `s_bridge` +0.35, `s_drift12` +0.07 W, all inside their intervals, and both fp32
  sign contrasts inside (`s_bridge` − `s_pair0` +0.67 against +0.68). The direction is E103's (`c_near_rand` +0.89, `s_bhalf_alt` +0.45 under M4: the
  model low where sums return to zero), at about half the size. **fp16:** `s_wpair0` (flagged) +0.41 W, outside; `s_inword0` −0.19, inside.
- **Exponents spread under a gate:** with a random word gate, inside in both formats (`fp32.x_logu_s50` −0.16, `fp16.x_logu_s50` −0.08 W). With
  lanes 0–3 gated steadily, `fp32.x_logu_bsteady` reads **0.76 W below** M5. The exponents are not what misses; the steady gate is (next).
- **Gated kinds:** the same 50% gated fraction three ways in fp32. The A gate alternating every two cycles is inside (+0.19). **The B gate held
  steady on lanes 0–3 reads 0.74 W below M5; the B gate switching every lane each cycle reads 0.48 W above, and 0.69 W above in fp16.** int8's two
  gated tiles are inside (−0.26, −0.20).
- **The A side with a busy partner:** the exact twin (`a_lo8_b_randn` against `a_lo8_b_pi`, the same A half byte for byte) is inside, +11.71
  against +11.55 W, so swapping a random partner for pi costs what the model says. **An A side held constant down each column reads low in both
  formats**: `fp32.a_colconst_b_randn` −0.48 and `int8.a_colconst_b_full` −0.75 W, both outside (both priority 2).
- **The zero level:** inside. One live lane-cycle an op (`fp32.z_single`) costs −0.06 ± 0.05 W over zeros, nothing measurable; `int8.z_diag` 1.81
  against 1.85 W.
- **int8 as a whole:** the model reads high, bias +0.20 W, five of six tiles below it.

**5. M5, M4 and F0r** (`scored-nodips.json` › `primary.reported`; rms with the bias, predicted minus measured, W). F0r is M4's float form refitted
on Q133(b)'s 283 rows with no per-format term, computed at registration (E115's comparator, reported, never a verdict):

| set | n | **M5** | M4 | F0r |
|---|---:|---:|---:|---:|
| floats, priority 1 | 16 | **0.291** (−0.02) | 0.321 (−0.00) | 0.324 (−0.05) |
| fp32, priority 1 | 12 | **0.305** (−0.03) | 0.329 (−0.04) | 0.340 (−0.10) |
| fp16, priority 1 | 4 | **0.241** (−0.00) | 0.295 (+0.12) | 0.271 (+0.08) |
| floats, all | 19 | **0.373** (+0.01) | 0.384 (+0.02) | 0.377 (−0.02) |
| int8 | 6 | **0.343** (+0.20) | 0.394 (+0.21) | (= M5) |
| every tile | 25 | **0.366** (+0.06) | 0.387 (+0.07) | 0.369 (+0.03) |

Paired bootstraps over the 16 priority-1 float tiles: **the per-format term alone** (F0r − M5) +0.034 W [−0.003, +0.078], 3.9% of draws at or below 0;
**the refit alone** (M4 − F0r) −0.004 W [−0.035, +0.024]; int8, M4 − M5 +0.050 W [−0.014, +0.092]. So on the blind pool the refit of M4's form buys
nothing, and the per-format term's gain, about 0.03 W, is not resolved at 95%. That is the same shape as Q133(b)'s nested comparison (−0.011 W,
95% −0.028 to +0.007), now on blind tiles.

**6. Post hoc, labelled, never a verdict: one pattern behind three misses.** Both tiles with lanes 0–3 held off for the whole launch read low by
the same amount, `fp32.g_blanes_steady` −0.74 and `fp32.x_logu_bsteady` −0.76 W, while the tiles whose B gate switches every lane every cycle read
high, +0.48 (fp32) and +0.69 W (fp16). That one pattern accounts for two of R4's three misses (the gate's switching, +2.00 against +0.78 W; the
exponents' contrast, whose minus tile is the steady one) and for four of R3's seven. In the bench's own terms the steady tile clocks more register
bits than the switching one (`clk` 4.78 against 3.93 W, `predictions-e115.json` › `tiles.*.M5.terms_w_a3`), and the card reads the opposite order
of cost, 1.22 W beyond the prediction. The first suspect is clock gating under a steady lane gate, which the silicon may do more of than the
public RTL's bench counts; it is not tested here. The second pattern, A held constant down each column reading low (−0.48 fp32, −0.75 W int8),
is two priority-2 tiles in two formats.

## What it changes

**For item 6 of section 11 ("A power model across kinds").** M4 read two blind sets (E103, E95); M5, Q133(b)'s refit, now reads a third, blind
pool 3, on the card its constants are on. **It reads 0.29 W rms over 16 float tiles built on the open cases, 0.003 W above the 0.288 W its own
nested score implies for 16 tiles (R1 FAIL, marginal, on the registered dips-removed reading); int8 0.34 W (PASS); 18 of 25 inside the frozen
intervals (INCONCLUSIVE); 4 of 7 contrasts inside (FAIL).** E115 could not tell M5 from M4 (+0.030 W, 95% −0.005 to +0.074), and the per-format
term's gain over M4's form refitted is +0.034 W, 95% −0.003 to +0.078: "E115 decides" becomes "E115 could not tell them apart", as registered.
The open cases, one by one:

- **Narrowed:** fp32 sums returning to zero (three tiles inside, +0.07 to +0.36 W, and both contrasts inside); exponents spread under a random
  word gate (inside in fp32 and fp16); the A side with a busy and a quiet partner (the exact twin inside); the zero level (both tiles inside);
  the memory path's own term between changing B lines and changing half-lines (+8.39 against +8.38 W: no term at ±0.56 W); another stream
  (`int8.st_f32bytes` inside).
- **Newly located as the model's miss: gated kinds.** A steady lane gate costs 0.74–0.76 W less than the model says (two fp32 tiles), and a gate
  switching every lane each cycle 0.48–0.69 W more (fp32, fp16); switching the gate reads +2.00 W against +0.78 [+0.23, +1.34]. Q133(b) had
  read gated kinds as narrowed ("the bench's counts already carry what gating does"); on these tiles they do not.
- **Still open:** A held constant down columns (−0.48 fp32, −0.75 W int8, priority 2); fp16 cancelling across k-groups (`s_wpair0` +0.41 W, its
  count flagged); int8's +0.20 W bias; the A side on the single-bit ladders; any other clock, voltage or stream, E101's GEMM included; **a new
  card without a scale (not tested: this is the a3 card)**; a pool written by someone else (still half met); any physical reading of the
  constants.

**For the blog material:** a simulation-priced model of the chip's TensorFMA predicts 25 tiles nobody fitted, built on its known weak spots, to
0.29 W rms over the 16 main float tiles (readings of 0–26 W; about 1.2% of a 25 W random fp32 tile) and 0.34 W over 6 int8 tiles (about 5% of int8's 7 W random), on one card.
Where it misses is the clock gate: lanes held off steadily are cheaper, and lanes switched on and off every cycle dearer, than the simulation
prices them, by up to 0.76 W.

## How it ran

| | |
|---|---|
| registration | `3b0264dd`, pushed 15:02:49 PST; `run_e115.sh setup` on aifoundry3 15:03:10–15:03:27, no device access: every reused and frozen hash identical, the 25 tiles verified (each file and each half), a `V3_DRY` pass of 47 launches (25 on pool tiles), the queue's stub test ([`logs/box-setup.txt`](logs/box-setup.txt)) |
| before the claim | `#community-lab` read at 15:04 (no open aifoundry3 claim; E110's released 14:27); `et-who` 15:04:31: no process holds a device node or card lock (other lab users' idle logins only, which E78's D1 rule lets pass) |
| smoke 11501 | 15:04:53–15:05:41: eight 2 s runs, cycles per op 546.0 / 546.0 / 318.0, every record ok, 0.5995 GHz, launch coverage ≥ 0.996; config reads TDP 0 / 65 °C / 600 MHz / 523 mV at both ends ([`logs/smoke.txt`](logs/smoke.txt)) |
| passes | 11510 15:05:48–15:13:56 (488 s); 11511 15:14:11–15:21:46 (455 s); 11512 15:22:01–15:29:44 (463 s): the budget rule let all three start ([`logs/e115-queue.log`](logs/e115-queue.log)) |
| end | the session-end read 15:29:44, TDP 0 / 65 °C / 600 MHz / 523 mV; `et-who` clean; the claim edited to "— released" at 15:30:16 |
| reduction | `collect_e115.sh` on the Intel at nice 10, from a copy of the raw passes: E78's `reduce_e78.py` unchanged (sha256 checked), `auto` leakage 0.2300 W/°C on the primary, 0.2306 on the dips-removed arm (97 runs each) |
| E78-R5's checks (dips removed) | idle consistency median \|S − S0 − D\| 0.050 W (≤ 0.15); carry-over 0.0011 ± 0.0005 W/W (≤ 0.01); rail lag re-fit median 0.95 s; duty 0.9956–0.9967 (E78-R5's band is [0.990, 1.000]); 600 MHz in every sample, 521.6 mV mean |

## Departures

- **None from the registered procedure.** The fallback reading is the registration's own rule, used as written.
- **After the data, labelled:** the leakage arms (0.1994, 0.3803, 0) were also run on the dips-removed reduction (`e115-nodips-leak*.json`,
  `scored-nodips-arms.json`), because the registration defined them on the primary, which keeps one pass and scores nothing there. They move no
  verdict of R1, R2 or R5; R3 reads FAIL and R4 INCONCLUSIVE at leakage 0, and S1 fails at 0.3803 and 0 (the anchors' absolute level moves with
  the slope). The registered gates-off arm keeps the dips and moves no verdict.

## Files

- [`results-nodips.md`](results-nodips.md), [`scored-nodips.json`](scored-nodips.json): **the reading reported** (the dips-removed arm, scored alone, with its anchor footing);
  [`results-nodips-arms.md`](results-nodips-arms.md), [`scored-nodips-arms.json`](scored-nodips-arms.json): the same with the post-hoc leakage arms and the gates-off arm beside.
- [`results.md`](results.md), [`scored.json`](scored.json): the registered primary (one pass kept: NOT SCORED), with the registered arms.
- `e115.json`, `runs.csv`, `reduce.txt`: the primary reduction; `e115-nodips.json` (+ `runs-nodips.csv`, `reduce-nodips.txt`): the dips-removed arm;
  `e115-leak{0.1994,0.3803,0}.json`, `e115-gatesoff.json`, `e115-nodips-leak*.json` and their csv/txt/log files: the arms.
- `aifoundry3/kinds/p11510`–`p11512`, `kinds-smoke-p11501`: every pass's raw data (runs, marks, telemetry, dumped tiles, config reads, manifest);
  `logs/`: the queue log, the dry run, the session reads, the binaries' sha256, the setup and smoke transcripts, the times.
- `code.sha256`: every file the run and the reduction used.
- Registration and code: [`tools/claims-v3/e115/`](../../../../tools/claims-v3/e115/README.md). The model and the pool: Q133(b),
  [`../2026-11-01-q133b-power-model/`](../2026-11-01-q133b-power-model/README.md), [`tools/claims-v3/kinds/blind3/`](../../../../tools/claims-v3/kinds/blind3/README.md).

To reproduce from the raw passes (a python with numpy): `PY=python3 bash tools/claims-v3/e115/collect_e115.sh 'p115[1-9][0-9]' <raw root>` with
`<raw root>` holding `kinds/p11510`–`p11512`, `kinds-smoke/p11501` and `logs/` (as copied here under `aifoundry3/`), then the three
`reduce_e115.py --drop-dips --leak <k> --no-refit` runs and `score_e115.py` with those arms, as § Departures says.
