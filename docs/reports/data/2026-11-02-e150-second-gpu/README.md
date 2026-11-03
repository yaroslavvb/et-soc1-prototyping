# E150: E149's frozen toggle model on a second GPU die, two A10Gs under their cap

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6, "a power model across kinds"**, asked on a second GPU, and **item 2, "a GPU measured the same way"**, which
[E149](../2026-11-02-e149-gpu-model-check/README.md) narrowed on one GPU model (the A100).*

*Mon 2 Nov 2026 (week 45), Q138. The owner's words that evening: "all cards are available, feel free to settle any
unanswered questions regarding horace's power model using mordast, runs on aifoundry and modal for sanity checks on GPUs
(don't exceed $20 on modal)", with Q137's goal, "to be able to predict the power requirement and heat generation of
various kinds of numeric computations as accurately as possible". Pre-registered in `0ddbad8d`
([`tools/gpu/e150/E150.md`](../../../../tools/gpu/e150/E150.md): the smoke and its rule for the GPU type and sizes, the
two phases, one scale per board, the rules, a selftest), pushed at 22:00:11 PST before any GPU call; amendments A1–A5
(`de658109`, `aa706ef6`, `37efe72d`, `436fcd34`, `fbd1df58`, and a note on A5 in `bc14113b`), each before the data it
touches; the freeze, `bacc1a94`, from phase L alone, pushed at 22:46:21 before phase H was reduced and while board B4
was still measuring it *(corrected after verification, C4: by then three of phase H's four board-passes had been
measured, and two of them, each board's first, were on the Intel unreduced; the freeze is a mechanical function of phase
L, and re-derived from logs cut at phase L's end its power predictions are identical, see "How it ran")*. Modal
workspace `yaroslavvb`, app `e150-second-gpu`.*

*Corrected after verification (a dated note, Mon 2 Nov 2026, about 23:55 PST; desk only: no GPU, no Modal app started, nothing re-run, no
device command). An independent verifier re-derived every registered number and verdict from the committed logs, found
the spend inside every limit and every window under the cap, and found eight faults (one major, seven minor). None
changes a measured number, a rule, a prediction or a verdict. Each is corrected in place, marked "corrected after
verification, C<n>", and listed in [§ Corrections after verification](#corrections-after-verification) at the end; the
numbers they quote are printed by [`corrections-numbers.py`](corrections-numbers.py) →
[`corrections-numbers.txt`](corrections-numbers.txt). The main one, C1: the heat error is not "mostly the heat model's
own, not the power path". The checkerboard's power over-read is 43% of the blind arm's squared error, and the blind
arm's near-zero bias is two errors cancelling; outside the checkerboard the heat model's own error dominates (0.94 °C
blind against 0.85 °C from measured power). The registration ([`tools/gpu/e150/E150.md`](../../../../tools/gpu/e150/E150.md),
`0ddbad8d` with A1–A5) is frozen and unchanged, apart from a dated note appended under its amendments (C5).*

## Results

**The L4 could not be tested: at every size from 512³ to 2048³ it runs these GEMMs at its 72 W cap**, with the
power-cap bit set in every sample of every random window, so its power reads the cap and the data moves its clock
instead (random bf16 at 2048³ ran 25% slower than zeros). By the registered rule E150 ran on the **A10G**, Ampere GA102:
the A100's generation on a different die. So E150 asks "across two dies of one generation", not "across generations".

**On two A10G boards under their 300 W cap (1710 MHz with no reason bit in every sample of every window), the A100's
structure repeats exactly**: all 11 of E149's structure verdicts come out the same (C1 HOLDS, 11 of 11). Power follows
bit changes, not ones (all four Hamming ladders); blocks of zeros save more than scattered ones; a random sign costs and
a fixed one is free; sorting saves; and neighbours along K are again not the pairing (R4b FAILS, as on the A100). The
A10G draws about half the A100's watts for the same kinds (random bf16 75.4 W over zeros against 154.7 W).

**E149's frozen model in the ET-SoC-1 form (G1), with nothing refitted but one scale per board (1.463 and 1.407 after
the measured rate conversion), predicts E149's 17 held-out kinds on the A10G to 11.2 W rms, 14.9% of the A10G's 75.4 W
span, biased −3.5 W.** One of the 17, the 75% sparse, re-seeds a phase-L rung (11.6 W rms over the other 16; *added
after verification, C7*, see Phase H). E149's own blind test of the same model on new A100 boards read 16% (24.7 W of 154.7). So F1–F4
and F6 **hold**: rms under 20% of the span, bias under 10%, 15 of 17 inside the scaled band, 3.1 times better than
density alone (G0, 34.9 W), and the two boards' scales within 4%. F5 **fails**: G1's form refitted natively on the
A10G's own ladders predicts better, 8.3 W against 11.2 (the bar was 1.25×). The best of E149's seven frozen forms is
again G4 (a K-lag of 16 plus the row direction): **5.2 W rms, 6.9% of the span** (12.8 W, 8.2%, on the A100). The
checkerboard is again G1's worst kind (−37.7 W; 6.7 W rms without it).

**The kinds' watts carry from one die to the other better than any model does.** The A100's own measured watts for each
held-out kind, times one ratio per format and board (the A10G's random kind over the A100's, read on phase L), predict
the A10G's held-out kinds to **3.0 W rms (4% of the span)**, the checkerboard to −0.09 W (T0, registered in A5 after
the freeze and before phase H was read; no verdict). So most of G1's 11.2 W is the model's own error (the checkerboard,
which its lag-1 pairing over-reads, above all), not the change of die.

**Heat: the A10G's die rises 0.142–0.146 °C per board W at steady state** (each board's fit; 0.144 pooled), with poles
at ≤ 0.2 s (the grid's edge) and 32 s; its leakage share of y is small (λr₁ = 0.034 pooled, against the A100's 0.131;
by board 0.008 on A and 0.059 on B4, whose leakage slopes differ sevenfold, so it is weakly determined *(corrected after
verification, C6)*), so E149's double count barely matters here. A held-out kind's 30 s rise is predicted to **1.21 °C
rms** blind (H1 FAILS; the corrected arm 1.19 °C, Hc FAILS) and **0.87 °C** from its measured power (H2 FAILS), against
rises of −4.4 to 10.9 °C; 16 of 17 fall inside the band (H3 HOLDS) and the two boards agree (H4 HOLDS, ratio 0.97). The
fit under-reads the 30 s rises (bias +0.65 °C from measured power), and NVML reports the die in whole degrees. The blind
arm's near-zero bias (+0.03 °C) is two errors cancelling: the registered path's power runs high (G1's −3.5 W bias,
about 0.38 °C, and the double count, 0.20 °C) and adds 0.62 °C to the predicted rises on average, while the heat model's
under-read takes 0.65 °C off them. The checkerboard's power over-read alone is 43% of the blind arm's squared error;
without the checkerboard the blind arm reads 0.94 °C and the measured-power arm 0.85 °C *(added after verification,
C1)*.

| what is predicted, E149's held-out kinds | before E150 | after E150 | source |
|---|---|---|---|
| **power of a new kind on a second GPU die (A10G, under its cap)** | no A10G model; E149's model in A100 watts 64.8 W rms (86% of the span); density alone, scaled, 34.9 W | E149's frozen G1 × one scale per board: **11.2 W** rms (14.9%), bias −3.5 W, 15 of 17 inside bands of ±6.5–69 W; frozen G4 × its scale **5.2 W** (6.9%); G1 refitted on the A10G 8.3 W; the A100's measured watts × one ratio per format (T0) **3.0 W** (4.0%) | `score-e150.json` `models`, `arms`, `rules` |
| **the second die's price per operand-bit flip** | — | **1.41–1.46 ×** the A100's at one multiply-add in G1's form (bf16 1.37–1.42, fp16 1.40–1.46, int8 at 512³ 1.97–2.07 with a scale per format): a ratio of predictor coefficients *(C6)* | `predictions-e150.json` `scales.G1` |
| **heat of a new kind**, die rise over a 30 s hold | no A10G model | **1.21 °C** rms blind (corrected for the double count 1.19 °C); **0.87 °C** from measured power. Without the checkerboard, whose power over-read is 43% of the blind arm's squared error, 0.94 and 0.85 °C; the blind bias, +0.03 °C, is two errors cancelling *(added after verification, C1)* | `score-e150.json` `heat`; `corrections-numbers.txt` C1 |
| die rise per board W, steady | — | **0.142 / 0.146 °C/W** (boards A / B4, their fits); 0.125–0.151 °C/W over a 60 s step, model-free; τ ≤ 0.2 s and 32 s; leakage 0.15 (A) and 1.14 (B4) W/°C, so λr₁ 0.008–0.059 by board (0.034 pooled) *(C6)* | `predictions-e150.json` `heat`; `posthoc.txt` §1 |

Every number in this section comes from `score-e150.json` (the blind scores and rules), `predictions-e150.json` (the
freeze: scales, predictions, bands, the heat model, phase L's rules), `reduce-L.json` / `reduce-H.json` (the measured
watts) and `choice-s.json` (the smoke), except those marked post hoc, from `posthoc.txt`. `summary.md` holds the tables
(`tools/gpu/e150/summarize_e150.py`).

## The smoke: why an A10G, and what an L4 does instead

The declared smoke ran random and zeros of each format at 512³–2048³ on one L4 and one A10G (`choice-s.json`, from
`analyze_e150.py choose`; one 5 s window each, not scored).

**The L4 runs every one of these GEMMs at its 72 W cap.** Every random window, at every size, read the board's enforced
72 W with the SW power-cap bit set in every sample, and from 1024³ up the zeros windows did too; only zeros at 512³ held
the 2040 MHz maximum (60–62 W). So no format has a size under the cap, and in this harness the L4 cannot test a power
model under its cap: its power reads the cap, and the data moves its clock instead. At 2048³ random bf16 ran at 1155 MHz
and 57.5 TFLOPS against zeros' 1530 MHz and 76.4 TFLOPS (25% slower), and random int8 at 111 TOPS against zeros' 145
(23% slower): E135's regime on the A100 and Horace He's effect, on the generation after the A100's (one window each).

| L4 (72 W), 2048³ | random: W, SM MHz, TFLOPS | zeros: W, SM MHz, TFLOPS |
|---|---|---|
| bf16 | 71.7, 1155, 57.5 | 72.2, 1530, 76.4 |
| fp16 | 72.2, 1080, 55.2 | 72.4, 1575, 79.2 |
| int8 (TOPS) | 72.1, 1545, 111.2 | 71.8, 2025, 145.2 |

**The A10G (300 W enforced, 1710 MHz maximum) held 1710 MHz with no reason bit in every bf16 and fp16 window at every
size**, drawing 174–239 W for random and 120–145 W for zeros, at the same speed for both (within 1 TFLOPS). int8 is
denser: its random window at 1024³ was valid but drew 273.6 W, over the rule's 270 W margin, and at 1536³ and 2048³ it
reached the cap (1560–1641 MHz, the power-cap bit). So the rule chose **bf16 at 2048³** (random 209.7 W, zeros
133.7 W), **fp16 at 2048³** (239.4 and 145.4 W) and **int8 at 512³** (138.7 and 103.5 W), where int8 runs launch-bound
at 29 TOPS (84 at 1024³): its watts are that kernel's at that duty.

## The boards: Modal's "A10G" is sometimes an A10

Modal served three of the six containers asked for as `A10G` as an **NVIDIA A10** (150 W enforced, NVIDIA's PCIe part),
under the same label. Board B of the measured run was one: its call was cancelled at 22:13:24, after its static reads,
build and 30 s idle and before any window (A3). The replacements B2 and B3 were A10s too, and the harness's guard
refused them in seconds (A3, A4). **B4 was an A10G and ran board B's plan.** The measured boards are **A**
(`b5f6c97556c4`) and **B4** (`22531ee7b547`, hashed UUIDs), both "NVIDIA A10G", 300 W enforced, 1710 MHz, building the
same operand bytes (sha256 on every kind). The A10's build matched them on only 21 of 90 kinds, the constants and the kinds
drawn from small random tensors (the square waves' phases, the low-rank factors; `posthoc.txt` §3), because torch's
generator spreads a seed over a grid sized to the GPU once a tensor is large. The cancelled and refused
folders are kept in `logs/e150-20261102-r1-not-used/`.

## Phase L: the A10G follows the same structure as the A100

Every window of both boards was valid, in both phases and every hold (V0: 72 of 72 phase-L kinds on each board). The
hottest cell drew 246.0 W (fp16 post-GELU × weights), 54 W under the cap. The speed did not depend on the data: bf16 ran
52.9–53.0 TFLOPS over 49 kinds (0.3% spread), fp16 56.3–56.5 (0.4%), int8 29.5–30.1 TOPS (2.0%). Random bf16 drew
75.4 W over zeros at 2048³ (S₂; the board drew 211.7 W), against the A100's 154.7 W. **All 11 of E149's structure
verdicts repeat (C1 HOLDS, 11 of 11 against a bar of 9)** (`predictions-e150.json` `rules_L`, beside E149's
`model-e149.json` `rules_stage1`):

| rule (phase L; n = 4 a kind, 2 boards × 2 passes) | A10G | A100 (E149) |
|---|---|---|
| R1a: no resolved rise along the scattered zero ladder (bf16, int8) | HOLDS, HOLDS | HOLDS, HOLDS |
| R1b: blocks of zeros save more than scattered, at 50% / 75% | HOLDS: +6.98 ± 0.85, +7.03 ± 0.99 W | HOLDS: +7.9 ± 3.9, +16.1 ± 3.4 W |
| R2: bit changes, not ones (middle rung over base / all-flipped over base) | HOLDS ×4: bf16 mantissa +36.6 / +3.6 W; exponent +22.9 / −4.7; fp16 mantissa +58.3 / +7.0; int8 +31.4 / +4.1 | HOLDS ×4: +81.4 / +7.0; +51.9 / −4.0; +81.7 / +6.8; +73.3 / +5.8 |
| R3a: a random sign costs | HOLDS: +17.95 ± 0.42 W | HOLDS: +43.1 ± 1.9 W |
| R3b: a fixed negative sign is free (within 10% of R3a) | HOLDS: +1.23 ± 0.40 W (limit 1.80) | HOLDS: +0.8 ± 1.9 W |
| R4a: sorted along K saves against the same values shuffled | HOLDS: +26.6 ± 1.0 W | HOLDS: +53.0 ± 4.7 W |
| R4b: neighbours along K are the pairing (period 2 costs more than 128) | **FAILS**: −3.93 ± 0.91 W | **FAILS**: −13.4 ± 4.1 W |
| B1: the two boards agree (slope; rms difference ≤ 5% of S₂) | HOLDS: 0.960; 2.11 W against 3.77 | HOLDS: 0.918; 7.33 against 7.74 |

The square waves along K read 37.5, 39.2, 43.5 and 41.5 W at blocks of 1, 4, 16 and 64 (the A100: 72.2, 82.7, 90.6,
85.6): the same shape at about half the watts. The A10G's replicates scatter less (SEs of 0.2–1.6 W, against the
A100's 2–5 W). Post hoc (`posthoc.txt` §4): the median bf16 kind drew 0.480 of its A100 watts (the middle half
0.467–0.497), fp16 0.751 (0.748–0.838), int8 0.400 (0.358–0.421). The exceptions are where the two dies differ: the
one-sided mantissa rungs (k = 3 on A only 0.33, on B only 0.79: the A-against-B split is not the A100's), the
constants (0.57–0.61) and, in int8, the base 1 (0.18).

## One scale per board

E149's coefficients are watts at the A100's multiply-add rate; the rate conversion divides by it. The A10G ran 0.337 of
the A100's rate in bf16 (52.9 against 157.1 TFLOPS), 0.519 in fp16 (56.4 against 108.7, at 2048³ against 1024³) and
0.198–0.205 in int8 (29.4–30.3 against 148.2 TOPS, at 512³ against 1024³). **G1's scale, least squares over phase L's
69 kinds of all formats: 1.463 on board A and 1.407 on B4** (ratio 1.040, F6 HOLDS): in G1's form, the A10G pays about
1.4 times the A100's energy per operand-bit flip at one multiply-add (a ratio of the two dies' predictor coefficients,
not a measured energy *(added after verification, C6)*). The one-scale fit reads phase L to 12.0 W rms in
bf16 (16% of S₂), 6.1 W in fp16 and 6.5 W in int8. With a scale per format, bf16 takes 1.37–1.42, fp16 1.40–1.46 and
int8 1.97–2.07: one number per board under-reads int8's launch-bound kernel by about 30%. Every other frozen form takes
its own scale the same way (G0 1.38–1.45, S1 1.38–1.44, G1s 1.41–1.46, G2 1.44–1.50, G3 and G4 1.42–1.48).

E149's coefficients are upper bounds on switching energy by y's leakage share (E149's C2), and that share differs
between the dies: λr₁ = 0.131 on the A100 and 0.034 on the A10G. Post hoc, the ratio of switching energies per flip
would be about 1.4 × (1 − 0.034) / (1 − 0.131) ≈ 1.6. The A10G's λr₁ is weakly determined (0.008 on board A and 0.059 on
B4, from leakage slopes 7.4 times apart), but the ratio survives it: 1.52–1.60 with 1.4, and 1.67 (A) and 1.52 (B4) with
each board's own scale and share *(added after verification, C6)*.

## Phase H, blind: E149's 17 held-out kinds

| model or arm (17 kinds, 2 boards × 2 passes) | rms W | bias W | worst W | rms / S₂ | on the A100 (E149) |
|---|---|---|---|---|---|
| **G1**, the ET-SoC-1 form, frozen, one scale a board (the registered primary) | **11.2** | −3.5 | 37.7 (checker) | **0.149** | 24.7 W, 0.159 |
| G1s, K-lag 32 | 10.9 | −0.9 | 34.2 | 0.144 | 24.0 |
| G2, G1 + the result path | 8.4 | +0.6 | 19.6 | 0.112 | 17.7 |
| G3, G1 + rows | 10.8 | −3.6 | 39.3 | 0.143 | 23.4 |
| **G4**, K-lag 16 + rows (picked after E149's scoring) | **5.2** | −1.9 | 11.8 | **0.069** | 12.8 W, 0.082 |
| S1, static bits | 20.2 | +15.4 | 42.3 | 0.268 | 33.8 |
| G0, density alone | 34.9 | +22.8 | 59.7 | 0.463 | 63.7 |
| G1 with a scale per format | 10.4 | −3.7 | — | 0.137 | — |
| G1 with one scale, no rate conversion | 16.1 | −4.8 | — | 0.213 | — |
| G1 in A100 watts, unscaled | 64.8 | −53.7 | — | 0.859 | — |
| G1's form refitted natively on phase L (F5's comparison) | 8.3 | −2.8 | — | 0.110 | — |
| **T0**, the A100's measured watts × one ratio per format (A5) | **3.0** | +1.5 | 8.0 (fp16 rand) | **0.040** | — |

Per kind (W; error = measured − predicted, the mean over the two boards):

| kind | measured y | G1 | G1 error | G4 error | T0 error | band ± |
|---|---|---|---|---|---|---|
| bf16 checker | 66.1 | 103.8 | **−37.7** | −6.7 | −0.1 | 22.8 |
| bf16 post-GELU × weights | 73.2 | 77.4 | −4.2 | −3.8 | +1.9 | 22.8 |
| bf16 low rank | 74.8 | 77.1 | −2.3 | −2.7 | +1.3 | 22.8 |
| bf16 one bit | 15.6 | 9.0 | +6.6 | +7.6 | +0.6 | 22.8 |
| bf16 pi | 11.7 | 17.1 | −5.4 | −1.6 | +3.4 | 22.8 |
| bf16 power law | 81.0 | 91.7 | −10.7 | −11.8 | +2.3 | 22.8 |
| bf16 uniform | 59.3 | 52.1 | +7.1 | +2.3 | +1.8 | 22.8 |
| bf16 uniform sorted along K | 42.2 | 32.5 | +9.8 | −4.5 | +0.1 | 22.8 |
| bf16 75% sparse | 43.6 | 45.7 | −2.1 | −2.2 | +0.1 | 22.8 |
| bf16 `sparse_neg` | 52.6 | 52.9 | −0.3 | −4.7 | +1.4 | 22.8 |
| bf16 ternary | 38.7 | 49.4 | −10.7 | −4.6 | +1.1 | 22.8 |
| bf16 twos | 6.4 | 17.1 | −10.6 | −6.9 | +1.5 | 22.8 |
| fp16 post-GELU × weights | 95.0 | 101.9 | −6.9 | −2.5 | +6.9 | 68.9 |
| fp16 uniform | 81.7 | 85.2 | −3.6 | −0.5 | +8.0 | 68.9 |
| int8 quantized post-GELU × weights | 33.2 | 26.2 | **+7.0** | +7.2 | −1.8 | 6.5 |
| int8 ternary | 26.8 | 22.1 | +4.6 | +4.2 | −1.6 | 6.5 |
| int8 twos | 0.4 | 1.0 | −0.5 | −1.2 | −1.3 | 6.5 |

**The checkerboard is the model's error, not the die's.** On the A10G it costs 66.1 W over zeros (the board drew
203.3 W), 0.487 times the A100's 135.9 W, exactly random bf16's ratio, so T0 lands on it (−0.1 W). G1's lag-1 pairing
over-reads it on both dies (by 79 W on the A100, 38 W here). Without it G1 reads 6.7 W rms and G4 5.1 W. The two kinds
outside G1's band are the checkerboard and int8's quantized activations × weights (+7.0 W against a band of ±6.5 W;
int8's one-scale under-read). The operand bytes are E150's own, built on the A10G from E149's seeds; their features give
G1's A100-watt predictions within 0.10 W rms of E149's (`posthoc.txt` §2), so the kinds are the same, if not the bytes.

**One of the 17 is not a new kind** *(added after verification, C7)*. The bf16 75% sparse (Horace He's kind) is built
as phase L's 75% scattered-zeros rung `zs75` is: randn with each element zeroed where a uniform draw falls under 0.75,
from other seeds ([`tools/gpu/e149/e149_app.py`](../../../../tools/gpu/e149/e149_app.py) lines 76–79, 314–317 and
354–361). So it is a re-seeded twin of a fitting kind (y 43.6 against 44.3 W), a split inherited from E149. Over the
other 16 kinds G1 reads 11.6 W rms (bias −3.6 W), G4 5.4 W and T0 3.1 W.

## Heat

The two-pole model refitted on phase L's session (both boards pooled; `predictions-e150.json` `heat`): **0.144 °C per
board W at steady state** (r₁ 0.052 at τ₁ ≤ 0.2 s, the grid's edge; r₂ 0.092 at τ₂ 31.8 s), 75% of it within 30 s
(0.108 °C/W), fit rms 0.86 °C. Each board alone: **0.142 (A) and 0.146 °C/W (B4)** (H4 HOLDS, ratio 0.974), and each
board's fit predicts the other's 30 s rises to 0.85 and 1.04 °C rms. Leakage at the held reference: 0.15 W/°C on A and
1.14 W/°C on B4 (mean 0.65; the A100's 1.8–2.6), so λr₁ = 0.034 (0.008 and 0.059 by board, so weakly determined
*(added after verification, C6)*). Without a model (post hoc, `posthoc.txt` §1): the 60 s
step from the reference hold to the zeros hold reads 0.151 (A) and 0.125 °C/W (B4); the 30 s holds read a median
0.092 and 0.087 °C per W of their own step, where the fitted model, driven by the same watts, reads 0.068 and 0.077. So
the fit under-reads a 30 s rise by about 10–25%.

| 30 s hold rise, 17 held-out kinds (°C) | rms | bias | rule |
|---|---|---|---|
| the registered path (E149's: scaled G1 + λ × the simulated rise) | 1.21 | +0.03 | H1 FAILS (≤ 0.8) |
| the corrected arm (G1's y × (1 − λr₁)) | 1.19 | +0.23 | Hc FAILS (≤ 0.8) |
| from the measured power | 0.87 | +0.65 | H2 FAILS (≤ 0.6) |
| inside the registered path's band | 16 of 17 | | H3 HOLDS (≥ 13) |

The measured rises run from −4.4 °C (int8 twos, whose 512³ kernel draws less than the bf16 zeros before it) to
10.9 °C (fp16 post-GELU × weights). The checkerboard's registered-path rise is off by 3.3 °C (10.3 predicted against
7.0), G1's power error carried into heat (from measured power it is off by 1.2 °C the other way; its miss alone is 43%
of the blind arm's squared error *(added after verification, C1)*); random uniform's by 2.0 °C the other way. The double count E149's path makes
is worth 0.02 °C rms here, because the A10G's y carries little leakage. NVML reports the die in whole °C, so a single
30 s rise (the mean of ten samples minus ten) is quantized: E150's rises come in steps of 0.05–0.1 °C and a one-board
reading can be off by up to half a degree when the die sits on one value.

## What this does to predicting power and heat

**Section 11 item 6 ("a power model across kinds"): the frozen form carries to a second GPU die with one scale per
board.** **Tested:** E149's toggle model in the ET-SoC-1 form (operand bit changes by field and side, the zero gate, the
sign term), frozen on the A100, with nothing refitted but one number per board fitted on the A10G's own core ladders.
Out of sample, on E149's 17 held-out kinds: **before**, no A10G model (E149's model in A100 watts 64.8 W rms, 86% of the
A10G's span; density alone, scaled, 34.9 W, 46%); **after**, **11.2 W rms (14.9%)** for G1, about the share E149's blind
test found on new A100 boards (16%), and **5.2 W (6.9%)** for G4, E149's best form (8.2% on the A100); over the 16 kinds
that are new (one of the 17 re-seeds a phase-L rung), 11.6 and 5.4 W *(added after verification, C7)*. **Measured:** the
A10G's price per operand-bit flip at one multiply-add, **about 1.4 times the A100's** in G1's form (1.41–1.46 by board;
1.97–2.07 for int8's launch-bound 512³ kernel with a scale of its own), a ratio of the two dies' predictor coefficients,
not a measured energy, and its leakage share of y (λr₁ 0.034 pooled against 0.131; 0.008–0.059 by board, weakly
determined) *(corrected after verification, C6)*. **Tested again, and confirmed on a second die:** the structure (C1, 11 of 11 verdicts as on the A100, R4b's
failure of the lag-1 pairing included). **What limits prediction now is the model's form, not the die:** the A100's
own measured watts per kind, carried by one ratio per format, predict the A10G to 3.0 W rms (4%), where the best frozen
model reads 5.2 W and the refitted G1 8.3 W (F5 fails: refitting G1 on the new die beats freezing it). On this pair of dies,
a few anchor kinds measured on the new board, times the measured GPU's watts per kind, predict better than any frozen
model (one pair of one generation: whether it holds across generations is open).

**Heat, measured for the first time on an A10G:** die rise **0.142–0.146 °C per board W** (fits; 0.125–0.151 by
model-free 60 s steps), poles ≤ 0.2 s and 32 s. A new kind's 30 s rise: **before**, no A10G model; **after**, 1.21 °C
rms blind from the bits (1.19 °C with E149's double count corrected) and 0.87 °C from measured power. **Corrected arm:**
the double count E149.md N2 named is real but small on this die (0.02 °C rms), because λr₁ is a quarter of the A100's
at the pooled value (0.06–0.45 of it by board, C6). **Where the heat error sits now:** outside the checkerboard, it is
mostly the heat model's own (0.94 °C rms blind against 0.85 °C from measured power, over the other 16 kinds; the fit
under-reads 30 s rises by 10–25%), plus NVML's whole degrees. The checkerboard's 3.3 °C miss is G1's power over-read,
43% of the blind arm's squared error, and the blind arm's near-zero bias (+0.03 °C) is two errors cancelling (the power
path adds 0.62 °C to the predicted rises, the heat model's under-read takes 0.65 °C off). Over all 17 kinds, putting
measured power in place of predicted power moves the predicted rises by 1.48 °C rms, more than the heat model's own
0.87 °C, and the two errors partly cancel (correlation −0.57). So the next gain in predicting heat here comes as much
from the power model's form (the checkerboard first) as from the two-pole heat model *(corrected after verification,
C1: this said "The heat error is now mostly the heat model's own (it under-reads 30 s rises by 10–25%) and NVML's
whole-degree readings, not the power path.")*

**Section 11 item 2 ("a GPU measured the same way"): narrowed again, not answered.** A second GPU type, the A10G, is
measured under its cap by kind (power, die temperature, speed), and a third, the L4, shows the cap regime instead: at
72 W every GEMM size here reads the cap, and random data slows it by about a quarter. Untouched: a later generation
under its cap, a lower cap, his board and an H100, other shapes.

## Registered against what happened

| rule | registered | E150 |
|---|---|---|
| V0 | ≥ 90% of phase-L kinds valid on each board | HOLDS (100%, both boards; phase H and every hold valid too) |
| C1 | ≥ 9 of 11 structure verdicts repeat E149's | **HOLDS, 11 of 11** |
| F1 | G1's rms ≤ 0.20 × S₂ (15.08 W) | **HOLDS**, 11.22 W |
| F2 | G1's \|bias\| ≤ 0.10 × S₂ (7.54 W) | **HOLDS**, −3.51 W |
| F3 | ≥ 13 of 17 inside the scaled band | **HOLDS**, 15 (outside: the checkerboard, int8 quantized post-GELU × weights) |
| F4 | G1's rms ≤ 0.7 × G0's | **HOLDS**, 11.22 against 34.87 W *(corrected after verification, C8: this said 34.88)* |
| F5 | G1 frozen ≤ 1.25 × G1 refitted natively | **FAILS**, 11.22 against 8.33 W (bar 10.41) |
| F6 | the two boards' scales within 0.9–1.1 | **HOLDS**, 1.040 |
| H1 | the registered heat path's rms ≤ 0.8 °C | **FAILS**, 1.21 °C |
| Hc | the corrected arm's rms ≤ 0.8 °C | **FAILS**, 1.19 °C |
| H2 | from measured power, rms ≤ 0.6 °C | **FAILS**, 0.87 °C |
| H3 | ≥ 13 of 17 rises inside the band | **HOLDS**, 16 |
| H4 | the two boards' die rise per W within 0.8–1.25 | **HOLDS**, 0.974 |

So 9 of the 13 registered rules hold (V0, C1, F1–F4, F6, H3, H4) and 4 fail (F5, H1, Hc, H2); B1, reported with the structure rules, holds.

## Post hoc (no verdicts)

From [`posthoc_e150.py`](../../../../tools/gpu/e150/posthoc_e150.py) into [`posthoc.txt`](posthoc.txt) and
`posthoc.json`: §1 model-free die rise per W (above); §2 E150's bytes against E149's (G1's A100-watt predictions within
0.10 W rms over the 17 kinds); §3 the A10's bytes (21 of 90 kinds the same: the constants, the square waves, low rank); §4 every phase-L kind's
A10G watts over its A100 watts (the medians above). Also above: G1 and G4 without the checkerboard (6.7 and 5.1 W rms,
from `score-e150.json` `per_kind`), and the switching-energy ratio of about 1.6 (from the two λr₁).

## How it ran

| when (PST, Mon 2 Nov 2026) | what | commit |
|---|---|---|
| 22:00:11 | registration committed, pushed at 22:00:13 before any GPU call (the smoke's app was created at 22:00:25) *(C5: this said "pushed" at 22:00:11)* | `0ddbad8d` |
| 22:00:3x–22:11 | the declared smoke: the A10G at once, the L4 queued for about 6 minutes, then run | — |
| 22:06:44 | A1: the choice (the A10G; bf16 and fp16 at 2048³, int8 at 512³). The L4's function had started 15 s before, at 22:06:28.7, which A1 did not see *(corrected after verification, C5: this said "while the L4 was still queued")* | `de658109` |
| 22:11:53 | A2: the L4 ran after all and qualifies with no format; the choice stands on the rule (A2's "started seconds after" A1 has the sign wrong: a dated note under the amendments, C5) | `aa706ef6` |
| 22:12 | the measured run launched: board A an A10G, board B an A10 | — |
| 22:13:24 | board B's call cancelled before any window | — |
| 22:14:11 | A3: the guard; B2 launched and refused (an A10) | `37efe72d` |
| 22:15:13 | A4: replacements one after another until 22:25; B3 refused (an A10); B4 an A10G, from 22:16 | `436fcd34` |
| 22:45:54–57 | the freeze's fetch of both boards from the Volume: steps 000–007 each, so phase L and each board's first phase-H pass (A 22:38:09–22:42:09, B4 22:41:45–22:45:45), raw and unreduced *(added after verification, C4)* | — |
| 22:46:09 | board A ends its second phase-H pass (from 22:42:09; not in the fetch) *(C4)* | — |
| 22:46:21 | the freeze from phase L alone (`reduce-L.json`, `predictions-e150.json`), before phase H was reduced, with B4 still measuring it (its second pass, 22:45:46–22:49:46) | `bacc1a94` |
| 22:47:21 | A5: comparison T0, before any phase-H window was reduced (a note on A5 at 22:47:4x, `bc14113b`) | `fbd1df58` |
| 22:59, 23:02 | boards A and B4 end, every step run, nothing skipped (2,783 and 2,781 s) | — |
| 23:03 | phase H reduced and scored; this README | this commit |

The freeze re-derived from the final logs is the committed one: `reduce-L.json` identical, `predictions-e150.json`
equal to 2 × 10⁻¹⁴ relative (BLAS's summation order).

*Added after verification, C4.* "Before phase H was reduced" holds, but it is half the story: by the push, three of phase
H's four board-passes had been measured (A's two, B4's first), and two of them, each board's first, were on the Intel,
raw and unreduced, from the freeze's own fetch (every fetched file byte-identical to the committed log of its name). A5's
T0, committed at 22:47:16, was written with those two passes on disk; its arithmetic reads no A10G phase-H number (E149's
measured A100 watts times phase L's anchor ratio, `analyze_e150.py` `do_score`). The freeze reads phase L only: re-derived
from a copy of the logs cut at the end of pass 2, every power prediction, scale and band is identical (to 2.3 × 10⁻¹⁴),
and the heat model's poles, gains and steady rise move by at most 0.2% (r₁ +0.17%, R_ss −0.01%, the 30 s rise per W
+0.02%). Its session-start terms, which no hold prediction uses, move by up to 1.3%, and the fit's sum of squares by 1.9%
on 37 fewer samples. These differences are there because the registered code ends the heat series at the last
phase-L row's start plus 10 s (`analyze_e150.py` `do_freeze`), 0.83 s (A) and 1.13 s (B4) into pass 3's first window, a
bf16 randn reference (a phase-L kind, no held-out one), where E150.md says "to the last phase-L cell".
(`corrections-numbers.txt` C4.)

## Departures, dated

- **A1–A5** (in [`E150.md`](../../../../tools/gpu/e150/E150.md), each pushed before the data it touches): the L4's late
  start; the choice; board B served as an A10 and cancelled; the guard and the replacements (B4 is the measured board
  B); the comparison T0.
- **Header times.** The headers of A1, A3, A4 and A5 say 22:08, 22:15, 22:17 and 22:50 PST; they were committed at
  22:06:44, 22:14:11, 22:15:13 and 22:47:21. Each was written a few minutes ahead of its push; the git times are the
  record, and every amendment still precedes the data it touches. A1's "8 minutes" was about 6 (A2 says so).
- **A2's "seconds after"** *(added after verification, C5)*. A2 says the L4's container "started seconds after" A1's
  push. It started before: the L4's function began at 22:06:28.7 (its `DONE`'s `t_fn`; its `STARTED` 22:06:27.2, its
  first NVML sample 22:06:28.8), 15 s before A1 was committed and 17 s before A1 was pushed (22:06:46), so A1's "did not
  start" no longer held when it was committed. No rule or choice depends on it: A2 applied the rule to both types'
  windows, and the A10G is chosen by the rule itself. A dated note under the amendments in `E150.md` says so; A2's text
  is unchanged.
- **The heat series' end** *(added after verification, C4)*. E150.md fits the heat model "to the last phase-L cell"; the
  registered code ends it at the last phase-L row's start plus 10 s, 0.8–1.1 s into phase H's first window, a bf16 randn
  reference. Cut at phase L's end, the heat model's parameters move by at most 0.2% (above, "How it ran").
- **The note on A5** gives fp16's ratio as 0.73–0.75 and int8's as about 0.42–0.44: those are the random-like kinds;
  across phase L the middle halves are 0.748–0.838 (fp16) and 0.358–0.421 (int8) (`posthoc.txt` §4).
- **The registration's budget** ($2.34 projected, $2.67 ceiling) assumed two boards; with the cancelled board and three
  refusals the metered total is in "Cost".

## What this cannot say

- **Not "across generations".** The L4 (Ada) runs these GEMMs at its 72 W cap, so its power reads the cap. E150 tests
  the frozen form on a second Ampere die (GA102 against the A100's GA100), not on a later generation. A later part with
  headroom under its cap would answer that.
- One board pair of one type, in rented slots, for 46 minutes each; one size per format, chosen by the cap, so int8 ran
  a launch-bound 512³ kernel where the A100 ran 1024³, and fp16 ran 2048³ where the A100 ran 1024³; one library (cuBLAS
  through torch 2.5.1); square K-contiguous operands. The scale is fitted per board on phase L, so a board the fit never
  saw needs its own phase L, or at least its anchors.
- The models are predictors in the ET-SoC-1 model's form, not either GPU's circuit: nothing here reads which operands
  meet on a wire. The per-flip ratios are between coefficients at the measured multiply-add rate, each an upper bound on
  switching energy by its die's leakage share.
- No lower power limit was tried: nothing is set on the GPU.

## Cost

**Metered $2.29** (`billing.json`: `modal billing report --for today --show-resources --json`, read 23:08 PST, app
`e150-second-gpu` only): the smoke $0.21 (A10G $0.12, L4 $0.06, CPU and memory $0.03); board A with the cancelled
board B $1.03; board B4 $1.00; the two refused replacements $0.04 (B3) and under $0.01 (B2) *(corrected after
verification, C2: the two boards' figures were swapped. `apps-e150.json`, `modal app list` read at 23:42 PST, ties each
billed app to its units: `ap-Wblo59…`, created 22:12:07, holds A and B, `ap-KG1Eul…`, created 22:15:45, holds B4)*.
Function-seconds from the Volume's `STARTED`/`DONE` (`ledger.json`): 6,179 s, of which the ledger prices 6,108,
$2.11 at the registered rates (the refusals record no elapsed time) *(corrected after verification, C3: this read
"6,179 s, $2.11")*. `ledger_e150.py` reads no GPU type from the A10 board B's name ("NVIDIA A10"; it matches "L4" and
"A10G" only), so B's 71 s are counted but not priced. Modal billed every A10 under its A10G resource; at that unit
rate all 6,179 s come to $2.14.
Projected at registration $2.34 (A3's revision: about $2.30), E150's stop $2.50, its cap $3. Q138's Modal round:
E149's $4.48 + E150's $2.29 = $6.77, under the round's $14 stop; with E135's $3.62, $10.39 of the owner's $20 for GPU
checks. No container is left running; the Volume `e150-second-gpu` (about 2 MB, every log committed here) remains.

## Files

- `choice-s.json`: the smoke's windows on both GPU types and the rule's choice; `logs/e150-20261102-smoke/` its logs.
- `logs/e150-20261102-r1/A`, `.../B4`: the measured run (steps, NVML samples every 100 ms, features, plan, `STARTED`,
  `DONE`); `logs/e150-20261102-r1-not-used/` the cancelled A10 board B and the refused B2, B3.
- `reduce-L.json` / `.txt` (phase L), `predictions-e150.json` / `.txt` (the freeze), `reduce-H.json` / `.txt` (phase
  H; zeros only in the text), `score-e150.json` / `.txt` (the blind scores, every rule, the heat holds),
  `summary.md` (`summarize_e150.py`), `posthoc.txt` / `posthoc.json` (`posthoc_e150.py`), `ledger.json`
  (`ledger_e150.py`), `billing.json` (the metered report, app `e150-second-gpu` only).
- Added after verification: `apps-e150.json` (`modal app list --json`, read 23:42 PST: the six `e150-second-gpu` apps,
  created and stopped), [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt)
  (every number the corrections quote, from committed files; run with `--trunc <scratch dir>`, it re-derives the freeze
  from logs cut at phase L's end, outside the repo).
- Code: [`tools/gpu/e150/`](../../../../tools/gpu/e150/) (`E150.md`, `e150_app.py`, `analyze_e150.py`,
  `selftest_e150.py` and `selftest.txt`, `summarize_e150.py`, `posthoc_e150.py`, `ledger_e150.py`); E149's
  `analyze_e149.py` and `model-e149.json` are imported unchanged.

## Corrections after verification

Mon 2 Nov 2026, about 23:55 PST, desk only. An independent verifier (`modal billing report`, `app list`, `container list` and the committed
logs; no GPU, no app started) re-derived E150's registered numbers and verdicts and found these eight faults. None
changes a measured number, a rule, a prediction or a verdict; `predictions-e150.json`, `score-e150.json`, the
reductions, the logs, `ledger.json` and `billing.json` are unchanged, and so is the registration (`E150.md` gains only
a dated note under its amendments). The numbers below are printed by `corrections-numbers.py` into
`corrections-numbers.txt`.

- **C1 (major), where the heat error sits.** "What this does" said the heat error "is now mostly the heat model's own …
  not the power path". The blind arm's error is the heat model's (from measured power) plus the power path's share (the
  predicted rise from measured power minus the blind one): over the 17 kinds 0.87 °C and 1.48 °C rms, partly cancelling
  (correlation −0.57) to 1.21 °C. The checkerboard's −3.29 °C blind miss (10.29 predicted against 7.00; from measured
  power +1.21) is 43% of the blind arm's sum of squares; without it the blind arm reads 0.94 °C and the measured-power arm
  0.85 °C, so outside the checkerboard the heat model's own error dominates. The blind bias, +0.03 °C, is the heat model's
  +0.65 °C and the power path's −0.62 °C (G1's −3.5 W bias about −0.38 °C, the double count −0.20 °C). Corrected in
  Results, the summary table, Heat and "What this does".
- **C2, the cost by board** was swapped: board A with the cancelled B $1.03 (`ap-Wblo59…`), B4 $1.00 (`ap-KG1Eul…`),
  tied by `apps-e150.json`'s creation times to the units' `STARTED` (22:12:11 for A and B, 22:15:49 for B4). The total,
  $2.2857, was right.
- **C3, the ledger's estimate** priced 6,108 of the 6,179 function-seconds: B's 71 s (an A10) carry no GPU type. All
  6,179 s at the A10G unit rate are $2.14.
- **C4, the freeze's timing** was half disclosed (header, "How it ran", Departures): three of phase H's four
  board-passes had been measured before the push, and two were on the Intel unreduced; re-derived from logs cut at phase
  L's end, the power predictions are identical and the heat model's parameters within 0.2%, the registered code's heat
  series ending 0.8–1.1 s into phase H's first (reference) window.
- **C5, A2's timing** had the sign wrong: the L4's function started 15 s before A1's commit, not after its push (a dated
  note in `E150.md`; "How it ran" corrected). The registration was committed at 22:00:11 and pushed at 22:00:13 (this
  README said pushed at 22:00:11); the first GPU call came after both.
- **C6, the scale and the leakage share** were stated with more certainty than they have: the scale is a ratio of
  predictor coefficients in G1's form, not a measured energy; λr₁ is 0.034 pooled but 0.008 (A) and 0.059 (B4) by board,
  from leakage slopes of 0.154 and 1.142 W/°C. The post hoc switching-energy ratio survives (1.52–1.67 by board).
- **C7, one held-out kind is a twin.** bf16 75% sparse re-seeds phase L's `zs75` (the same construction, other seeds;
  y 43.6 against 44.3 W), inherited from E149's split: 16 of the 17 are new kinds. Over those 16, G1 reads 11.56 W rms,
  G4 5.36 W, T0 3.07 W.
- **C8, two number slips.** G0's rms is 34.87 W (34.8746), not 34.88 (F4's row). The boards drew 104.4–246.0 W by cell
  (108.0–242.3 W by kind mean); "108–246 W", in this lane's result text, mixed the two.
