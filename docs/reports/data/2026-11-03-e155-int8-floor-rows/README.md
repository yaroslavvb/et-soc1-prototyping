# E155: from one A row to three, int8's no-issue floor rises 0.31 ± 0.10 W; per cycle is excluded (F1a WALK) and, as registered, the rise's interval overlaps the toggle count's frozen band (its point 0.016 W below it) and misses the new-address count's by 0.018 W (F1b TOGGLES), but on bands that also take the shared per-op term out of E148's sixteen-row base the new-address count is not excluded (post hoc); the toggle count predicted the rise to −0.06 ± 0.10 W and the three-row floor to −0.01 ± 0.08 W; the per-op difference between the formats is 8 ± 27 pJ, not bounded below 30 pJ (F3 INCONCLUSIVE) (Q139, aifoundry1 card 1, 600 MHz, nine passes)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 11, int8's
no-issue floor** ("int8 zeros' extra 0.61 W"), and **rank 10 of Q138's final critic**, the complaint this answers: "int8's no-issue floor by shape: which
count the per-row part follows (address-bit toggles against new-address reads), the per-op premise, and what stays at one row", with its next test "a
registered three-row arm with K = 8 partners in both formats (avoid four rows, errata type D), both counts' predictions frozen. Rule: the rise from one
row to three within the frozen count's band, and the per-op difference between the formats bounded below 30 pJ." It builds on
[E148](../2026-11-02-e148-int8-excess/README.md) (this card, the night before: two rows put back 0.16 ± 0.10 W; at that session's own scale the walk
counted in new-address reads over-predicted it twofold and the walk counted in address-bit toggles fitted, a count chosen after the data),
[E129](../2026-11-02-e129-int8-noissue/README.md) and [E109](../2026-11-01-e109-int8-zeros/README.md) (the K = 8 construction of per-op work) and
[Q136(c)](../2026-11-02-q136c-tima-bench/README.md) (the TIMA bench).*

*Tue 3 Nov 2026 (week 45), Q139, lane a1c1-e155-int8-floor. Pre-registered in [`tools/claims-v3/e155/README.md`](../../../../tools/claims-v3/e155/README.md)
with [`predictions-e155.json`](../../../../tools/claims-v3/e155/predictions-e155.json), committed as **`82b5af8d`** and pushed by `commit_lab.sh` at
04:28:26 PST, before the claim (04:30:0x) and before any device opened (04:30:48). **aifoundry1 card 1** (`V3_DEVICE=1`, its own lock), release 1.4.0
(BL1 and BL2 0.22.0), the first session on the card that day (it had idled since E148 ended at 22:45:56). `ettelem config` was read 24 times under
card 1's lock with `timeout 10`, through E128's allow-list (the session's start, 04:30:48, and end, 05:07:01, and both ends of the stop-path test, the
smoke and every pass): **TDP 65 W, threshold 65 °C, 600 MHz, 499 mV in every read** (power state `low_power` 6 times, `managed_power` 18). **Nothing
was set and no WRITE was sent** (§ Device commands sent; `since_reset_ms` −1 in all 20,534 samples). **Card session 04:30:48–05:07:01 PST, 36.2
card-minutes of the 40 allowed**: the stop-path test 15502, the smoke 15501 and **nine passes, 15510–15518 (215–239 s each), all kept**. The card was
claimed at 04:30 by rewriting the day's one card post in `#community-lab` (message `1567153765390487573`) and released at 05:07 by rewriting it again
(§ How it ran).*

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 05:40–05:56 PST, pushed as `93637c7f` at 05:56; desk only: no card opened, no device command, nothing re-run, no
Modal). An independent verifier re-ran the pipeline on the nine committed passes (every scored file byte-identical), re-derived the frozen bands by
hand, recomputed every statistic with its own scorer and traced every command sent to a read at `836a4ab`. It found six faults in how the result
was read, two major and four minor; none changes a measured number, a rule, a frozen prediction or a registered verdict. Each is corrected in
place, marked "corrected after verification, C<n>" or "added after verification, C<n>", and listed with the title's old wording in
[§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The numbers they quote are printed by
[`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt) (new; it reads committed files only). The
main ones: **C1**, the frozen bands Wn, Wt and T scale *all* of E148's sixteen-row N − N1, which under the premise the registration adds at three
rows (equal per-op energy in the two formats) already holds 0.087 ± 0.014 W of shared per-op work; on bands that take it out (post hoc) the
new-address count's band (0.38–0.50 W) reaches D31's interval and F1b would read INCONCLUSIVE in every arm, while F1a WALK and the toggle count's
small errors stand; **C2**, D31's interval overlaps the toggle count's band but its point lies 0.016 W below it, so "inside the band" was wrong.
The registration ([`tools/claims-v3/e155/`](../../../../tools/claims-v3/e155/README.md), `82b5af8d`), `scored*.json`, `results*.md`, the
reductions, `posthoc/` and the raw passes are unchanged.*

**In plain words.** With nothing to multiply, an int8 matmul loop on this chip still draws more than the same loop in fp32, and how much depends on
the shape of the operation: 0.93 W more at one row of A, 1.24 W at three rows, 1.63 W at sixteen (E148). Last night's two-row run left open what the
part that grows with rows follows: how often the accumulator memory's read address changes, or how many of its address bits flip. At three rows the
two counts predict different rises, and both predictions were frozen before the run. **The rise was 0.31 ± 0.10 W. That range overlaps the band
the bit-flip count predicted (0.33–0.42 W; the rise's own value sits 0.016 W below it) and stops 0.018 W short of the address-change count's
(0.43–0.55 W), and the bit-flip count predicted the rise to within 0.06 W (± 0.10) and, with last night's one-row level, the three-row floor to
within 0.01 W (± 0.08).** But both bands were built by scaling all of last night's sixteen-row excess, part of which the same prediction books as
per-operation work; on bands that take that part out, the address-change count's band reaches the measured range too, so on that footing the run
does not exclude it (post hoc), while the bit-flip count still predicts best. That reading rests on the two formats spending the same energy on each
operation's fixed work. At three rows they do not run equally many operations a second, so it was measured: about 90 pJ an operation in each, the
same to within −19 to +35 pJ, not the ±30 pJ the test asked for, and a difference at those limits could move the rise by −0.15 to +0.08 W. A check
that trades this assumption for another, int8 run at one row's exact schedule with the walk switched on and B's halved writes priced at fp32's
(0.18 W of its 0.22 W), is consistent with the bit-flip count and does not exclude the address-change count (post hoc) *(corrected after
verification, C1–C4: this said "The rise was 0.31 W: inside the band the bit-flip count predicted (0.33–0.42 W) and below the address-change count's
(0.43–0.55 W), and the bit-flip count, with last night's one-row level, predicted the three-row floor to 0.012 W", and "A check that needs no such
assumption, int8 run at one row's exact schedule with the walk switched on, agrees (post hoc)")*.

## Results

**All nine passes kept on the registered primary** (E78's `reduce_e78.py` unchanged through `reduce_e155.py`: leakage frozen at 0.2414 W/°C, card 1's
launch-gap dips removed, E78's run and pass gates, card 1's 65/65 config gate): 126 runs, none failing a gate, a median of two heats a launch. The
relaxed reduction keeps the same nine. ([`scored.json`](scored.json) › `n_passes`, `which_reduction_scores` = "primary"; [`e155.json`](e155.json) ›
`passes_set_aside` = [])

1. **Three A rows put back D31 = N3 − N1 = +0.311 ± 0.102 W** (95% +0.208 to +0.413; nine passes, paired inside each). **F1a reads WALK and F1b
   TOGGLES**: D31's interval overlaps the frozen band of the walk counted in address-bit toggles (Wt, +0.327 to +0.419) and of the A path (T, +0.222 to
   +0.288), and excludes the walk counted in new-address reads (Wn, +0.430 to +0.549) and per cycle (C, +0.123 to +0.162). **Wn's exclusion is by
   0.018 W** (D31's upper end 0.4128 against 0.4304); in the dips-kept arm by 0.003 W, in the leakage-`auto` arm by 0.023 W; C's by 0.047 W
   *(corrected after verification, C2: this said 0.017, 0.002 and 0.046 W, truncated; 0.0176, 0.0028 and 0.0469 W)*. D31's point (0.311 W) lies
   0.016 W below Wt's band: the rule is overlap, and it is the interval that overlaps *(added after verification, C2)*. Every arm reads the same
   verdicts. (`scored.json` › `rules.F1`; [`corrections-numbers.txt`](corrections-numbers.txt) C2) **F1b's exclusion of Wn rests on how the bands
   were built** *(added after verification, C1)*: Wn, Wt and T scale *all* of E148's sixteen-row N − N1 (0.747 W) by the bench's count ratios and
   then add the shared per-op term at three rows (0.085 W), but under that term's own premise (equal per-op energy in the two formats) E148's
   sixteen-row N already holds E_op × 0.7996 × 10⁹ = **0.087 ± 0.014 W** of shared per-op work (int8 318 cycles an op there, fp32 544; at one row
   both run 62, so N1 holds none), which the readings count as walk. Taken out with the same E_op (post hoc), the points fall by 0.047 (Wn), 0.033
   (Wt) and 0.020 W (T) and the bands read **Wn +0.382 to +0.504, Wt +0.292 to +0.387, T +0.201 to +0.269** (C unchanged; paired per E148 pass Wn
   +0.398 to +0.488): D31's interval reaches Wn's band, so **on that footing F1b would read INCONCLUSIVE, in every arm**, and F1a WALK stands (C is
   built on N1, which has no rate gap). The registered margin (0.018 W) is smaller than the construction's own shift of Wn's point (0.047 W).
   F1b TOGGLES remains the registered verdict. ([`corrections-numbers.txt`](corrections-numbers.txt) C1)
2. **The frozen predictions against the three-row shape, which no model had seen** (`posthoc/posthoc.txt` section 4 prints these from `scored.json`):

   | predictor, frozen before the run | D31 predicted | D31 error | N3 from E148's N1 (0.884 W) | **N3 error** | on the premise's footing (post hoc): D31 / N3 error |
   |---|---:|---:|---:|---:|---:|
   | null: a third row changes nothing | 0 | +0.311 W | 0.884 | +0.361 W | same |
   | null plus the shared per-op term | +0.085 | +0.226 | 0.969 | +0.276 | same |
   | per cycle (C) | +0.142 | +0.168 | 1.026 | +0.218 | same |
   | the A path (T; excluded as the sole carrier by E148's W2) | +0.255 | +0.056 | 1.138 | +0.106 | +0.076 / +0.126 |
   | **the walk in address-bit toggles (Wt)** | **+0.373** | **−0.062** | **1.256** | **−0.012** | **−0.029 / +0.021** |
   | E148's two-term solve (75.5 fJ a new-address read, 3.43 pJ a 64-bit A read) | +0.442 | −0.131 | 1.326 | −0.081 | not recomputed |
   | the walk in new-address reads (Wn; E148's registered count) | +0.490 | −0.179 | 1.373 | −0.129 | −0.132 / −0.082 |

   Measured: N3 = **1.244 ± 0.083 W**, D31 = +0.311 ± 0.102 W; each error carries the measurement's interval, so the toggle count's errors are
   **−0.06 ± 0.10 W on D31 and −0.01 ± 0.08 W on N3**. D31's is the per-row term's own test: N3's is smaller because this session's N1 sits
   0.050 W above E148's, which offsets it *(added after verification, C4)*. The last column puts each count's frozen reading on the premise's own
   footing (result 1; C1): the toggle count predicts best on both footings, and the new-address count errs by 0.13–0.18 W on D31 *(column added
   after verification, C1)*. (`scored.json` › `reported.N3_out_of_sample`; [`corrections-numbers.txt`](corrections-numbers.txt) C1, C4)
3. **The per-op premise, measured at three rows for the first time** (F3 INCONCLUSIVE). E109's construction with the K = 8 partners gives **e = 90.2 ±
   15.0 pJ an op in fp32 and 86.4 ± 15.6 pJ in int8** (E129 at sixteen rows: 81 ± 43 and 77 ± 92), a raw difference **Δe₃ = −3.9 ± 26.6 pJ**. With the
   frozen allowance for int8's count changes between the partner and the arm (−12.0 ± 4.5 pJ) it is **Δe₃c = +8.2 pJ, interval −18.8 to +35.1 pJ**:
   inside ±35 but not inside ±30 pJ, so the premise is not bounded at the registered line. Entering D31 as −4.30 × 10⁹ × Δe (int8's op-rate change
   from one row to three), that interval allows **−0.151 to +0.081 W** of D31: at its upper end the new-address count's band would be reached, at its
   centre (−0.035 W) the reading moves toward the toggle count's point. (`scored.json` › `rules.F3`; § What this cannot say)
4. **The silicon keeps the RTL's schedule at three rows and at K = 8 there** (R6 PASS ×6). Every arm's cycles per op equal the frozen prediction, the
   bench's plus E109's 7.75 (one constant, fitted earlier on silicon on the ordinary op and the same in both formats; *added after verification,
   C5*): **`m0r3` 128.0 (fp32) and 110.0 (int8)**, **`m0r3k8` 72.0 and 62.0**, `m0r1` 62.0 and 62.0, schedules no card had run but
   one row's. The smoke read the same. (`scored.json` › `rules.R6`; [`logs/session.log`](logs/session.log), the smoke lines)
5. **What stays at one row replicates** (T1 PASS): **N1 = 0.934 ± 0.077 W** against E148's 0.884 ± 0.077 and E129's 0.865 ± 0.357 on this card.
   (`scored.json` › `rules.T1`, `stats.N1`)
6. **Post hoc, deciding nothing** ([`posthoc/posthoc.txt`](posthoc/posthoc.txt)). (a) int8's K = 8 arm runs one row's exact schedule (62 cycles, the
   same TIMA control bits, TenTMP staging and TenC read count an op) with the walk on, so **Q31k = S(`m0r3k8.int8`) − S(`m0r1.int8`)** needs no
   premise about the two formats' per-op work, but it needs another: B's TenB writes a second are halved in it, and adding them back prices int8's
   writes at fp32's *(corrected after verification, C3: this said it "needs no per-op premise")*. Raw it is +0.036 ± 0.065 W, and **+0.220 ± 0.118 W
   (0.103 to 0.338) once B's halved traffic is added back** at this session's fp32 price, 0.146 ± 0.077 pJ a TenB write (fp32's three arms solved
   per pass for e and that price), so 0.184 W of its 0.220 W (84%) is the add-back. The frozen walk parts are Wt +0.255 [0.227, 0.284] and Wn
   +0.359 [0.319, 0.399]: the toggle count's residual is −0.035 W, the new-address count's −0.139 W, and Q31k's interval overlaps both, so it is
   consistent with the toggle count and does not exclude the new-address count; on the premise's footing (result 1) the walk parts are 0.226 and
   0.317 W, residuals −0.006 and −0.097 W *(added after verification, C3)*. (b) Priced on D31 less this session's shared term (0.100 ± 0.008 W), the
   rise is **36.9 ± 17.0 fJ an address-bit toggle** or **49.3 ± 22.7 fJ a new-address read**. E148's sixteen-row prices, 50.5 and 94.8 fJ, keep its
   own shared term (0.087 W) in; on a matched footing they are **44.7 ± 5.8 and 83.8 ± 10.9 fJ** (that term removed at E148's E_op) or 43.6 ± 5.7
   and 81.8 ± 10.6 fJ (at this session's, 127.9 pJ). The toggle prices agree on every footing; the new-address prices miss by 0.9 fJ only when E148
   is put at its E_op and E155 at the session's, and overlap when one E_op serves both *(corrected after verification, C1: this said "against
   E148's sixteen-row 50.5 (consistent) or … against 94.8 (excluded)")*. ([`corrections-numbers.txt`](corrections-numbers.txt) C1, C3) (c) D31 /
   D21 = 1.95 against the counts' 1.71 (toggles) and 1.28 (new-address), before the shared terms.

**What it changes.** Item 11 narrows again. **Per cycle is excluded as the per-row carrier** (F1a WALK, registered, on either band construction).
**The walk counted in address-bit toggles predicts the per-row part best** on two shapes now: E148's two rows (post hoc, −0.009 W) and E155's
three rows (registered: D31 to −0.06 ± 0.10 W, N3 to −0.01 ± 0.08 W; −0.03 W on D31 on the premise's own footing). **The new-address count is
excluded at three rows only on the registered band construction** (F1b TOGGLES, by 0.018 W, under the per-op premise): on bands that take the
shared per-op term out of E148's sixteen-row base it is not (post hoc), and Q31k, which trades the per-op premise for another, does not exclude it
either *(corrected after verification, C1–C3: this said "The per-row part follows the walk counted in address-bit toggles on two shapes now: …
(registered: F1b TOGGLES, the new-address count excluded by 0.017 W, under the per-op premise; post hoc by Q31k without it)")*. The A path's band
also holds D31 at three rows, but E148's W2 excluded it as the sole carrier at two rows, and no single count other than the toggle count fits both
shapes: at two rows the new-address count stays excluded on the premise's footing too (E148's post hoc residual −0.134 ± 0.079 W, the toggle
count's −0.004 ± 0.085 W; [`corrections-numbers.txt`](corrections-numbers.txt) C1) *(added after verification, C1)*. **The premise** is measured
at three rows (−19 to +35 pJ), 2.4 times tighter than E129's ±63 pJ, but not inside the ±30 pJ the critic asked for. **What stays at one row** (0.93 W) is replicated a third time; what it is (per-cycle work or one row's A
staging) no arm here separates.

## What it does to predicting power and heat

*(Rewritten after verification, C1 and C4; the first version's words are quoted in
[§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026), C1 and C4.)*

**The term measured and tested:** int8's no-issue floor as a function of shape, N(R) ≈ N1 + p × count(R) + E_op × (the formats' op-rate
difference), the count being TenC read-address bits that change a second (toggles) or TenC reads at a new address. Before E155 the per-row count
was open (E148: the registered new-address count failed at its own scale, the toggle count fitted post hoc). **Out of sample, on a shape no model
was fitted on (three A rows, every prediction frozen first), against the measured rise D31 = +0.311 ± 0.102 W and floor N3 = 1.244 ± 0.083 W:**

| predictor | D31 error, as registered | D31 error, on the premise's footing (post hoc) | N3 error from E148's N1, as registered / on the footing |
|---|---:|---:|---:|
| null: a third row changes nothing | +0.311 W | +0.311 | +0.361 / +0.361 |
| null plus the shared per-op term | +0.226 | +0.226 | +0.276 / +0.276 |
| per cycle (C) | +0.168 | +0.168 | +0.218 / +0.218 |
| the A path (T; excluded as the sole carrier by E148's W2) | +0.056 | +0.076 | +0.106 / +0.126 |
| the walk in new-address reads (Wn; E148's registered count) | −0.179 | −0.132 | −0.129 / −0.082 |
| E148's two-term solve | −0.131 | not recomputed | −0.081 / — |
| **the walk in address-bit toggles (Wt)** | **−0.062** | **−0.029** | **−0.012 / +0.021** |

Each error carries the measurement's interval (± 0.102 W on D31, ± 0.083 W on N3; [`corrections-numbers.txt`](corrections-numbers.txt) C1, C4).
**So the per-row term's error falls from 0.31 W (the null) to 0.03–0.06 W with the toggle count, on both footings, inside the measurement's ± 0.10 W;
the new-address count errs by 0.13–0.18 W, but its exclusion holds only on the registered band construction.** For a model, the toggle's price is
44.7 ± 5.8 fJ at sixteen rows on the premise's footing (E148; 50.5 as committed, with E148's shared term counted as walk) and 36.9 ± 17.0 fJ at
three (post hoc, this session's shared term out): consistent, so one price times the bench's toggle count carries the floor to other int8 shapes
on this card. The shared per-op term (fp32's 108.7 pJ an op frozen, 127.9 ± 10.7 measured here) is 0.085–0.100 W at three rows and 0.087 W inside
E148's sixteen-row N, so a model applies it at every shape, the sixteen-row base included. The per-op difference between the formats is not yet
bounded below 30 pJ (−19 to +35 pJ), which leaves −0.15 to +0.08 W in D31. **Heat** follows power through card 1's die rise per board watt (M7's
H2, 0.1151 °C/W): the 0.03–0.06 W error is at most 0.007 °C and the whole rise 0.04 °C, below the 4.5 s readout, so no heat term changes.

## The arms (primary reduction)

D is over the format's zeros (interpolated between the pass's three zeros anchors) and S over the idle bracket, ± 95% over 9 passes (t 2.306).
"Cycles" is the median over the kept runs. Source: `e155.json` › `items`, `per_pass`; [`readme-numbers.txt`](readme-numbers.txt).

| item | cycles | ops/s (10⁹) | D, W | S, W |
|---|---|---|---|---|
| `fp32.zeros` | 546.001 | 1.1208 | 0 | +1.598 ± 0.028 |
| `int8.zeros` | 318.001 | 1.9249 | 0 | +2.200 ± 0.033 |
| `anchor_pi` | 546.001 | 1.1208 | +8.215 ± 0.029 | +9.794 ± 0.026 |
| `m0r1.fp32.zeros` | 62.0 | 9.8656 | −0.404 ± 0.051 | +1.220 ± 0.049 |
| `m0r1.int8.zeros` | 62.0 | 9.8660 | −0.052 ± 0.028 | +2.153 ± 0.058 |
| **`m0r3.fp32.zeros`** | **128.0** | 4.7811 | −1.044 ± 0.041 | **+0.569 ± 0.046** |
| **`m0r3.int8.zeros`** | **110.0** | 5.5644 | −0.372 ± 0.056 | **+1.814 ± 0.058** |
| **`m0r3k8.fp32.zeros`** | **72.0** | 8.4966 | −0.709 ± 0.055 | +0.886 ± 0.052 |
| **`m0r3k8.int8.zeros`** | **62.0** | 9.8652 | −0.000 ± 0.045 | +2.189 ± 0.069 |

Idle 33.03 W. From one row to three both formats' levels fall with the op rate and B's traffic, fp32's by 0.651 ± 0.054 W and int8's by only 0.340 ±
0.078 W; int8 alone adds the walk back. Halving K at three rows raises both again (fp32 +0.316 ± 0.081, int8 +0.376 ± 0.099 W). (`scored.json` ›
`stats.r3_over_r1_*`, `stats.r3k8_over_r3_*`)

## The registered rules against the data

`scored.json` is `score_e155.py`'s output with `predictions-e155.json` on the primary, chosen by the set-aside rule over the relaxed reduction.

| rule | registered line | **E155 (primary, 9 passes)** | dips kept (8 passes) | leakage `auto` (fitted) | relaxed |
|---|---|---|---|---|---|
| **F1** (primary) | D31's 95% interval against the frozen bands Wn, Wt, T, C | **F1a WALK; F1b TOGGLES** (+0.311 ± 0.102; Wt and T consistent, Wn and C excluded) | WALK; TOGGLES (+0.309 ± 0.119) | WALK; TOGGLES (+0.311 ± 0.096) | WALK; TOGGLES |
| **F3** | Δe₃c's interval (H = √(h² + 4.5²)) inside ±30 pJ | **INCONCLUSIVE** (+8.2; −18.8 to +35.1) | INCONCLUSIVE (+5.7; −24.8 to +36.2) | INCONCLUSIVE (+6.3; −20.0 to +32.7) | INCONCLUSIVE |
| R6 | \|measured − predicted\| ≤ 2 cycles | **PASS ×6** (every difference 0) | PASS ×6 | PASS ×6 | PASS ×6 |
| T1 | N1 within 0.5 W of E148's 0.884 | **PASS** (0.934) | PASS | PASS | PASS |

**No verdict moves with an arm.** The dips-kept reduction sets aside pass 15518 (π drifts +0.694 W against its 0.60 W gate with the meter's dips
kept); the primary and the relaxed keep all nine.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | committed and pushed before the claim and the first launch | `82b5af8d` pushed 04:28:26 PST; claim 04:30; first device process 04:30:48 (the opening config read) |
| desk | the bench and its identity checks; the predictions; the self-test; the preflight; `bash -n`; the reducer's mechanical run. On the box: `check_e155.py`, the preflight, `bash -n`, a stub queue, `V3_DRY` of the stop test, smoke and pass 15510 | [`selftest.txt`](../../../../tools/claims-v3/e155/selftest.txt) PASS (A–C); [`dmcmd-audit.txt`](../../../../tools/claims-v3/e155/dmcmd-audit.txt) GO; the box's checks 04:26:06–04:27:29 PST ([`logs/desk/`](logs/desk/)) |
| stop test | before the smoke: the die, board, watcher and stale-line stops each exit 6 on a live sample, no launch | 04:30:49–04:31:03: die stop on a sample read 0.044 s after it was taken, board 0.044 s, watcher 0.079 s, stale 0.077 s; rc 6 four times ([`aifoundry1-c1/e155-stoptest/p15502/`](aifoundry1-c1/e155-stoptest/p15502/)) |
| smoke | eight items, 2 s runs; E109's gate | 04:31:04–04:31:51; every item 6 launch records, all `ok`: SMOKE-GATE PASS; `m0r3` 128.0 / 110.0 and `m0r3k8` 72.0 / 62.0 cycles |
| passes | 15510–15519 as the budget allows | **nine**, 215–239 s each (rc 0); the budget rule stopped before 15519 (05:07:01, T0 + 2,174 s; it would have ended at T0 + 2,413 s against T0 + 2,250 s) |
| kept | the primary carries if ≥ 3; else the relaxed one | **9 of 9** by E78's gates; the relaxed reduction keeps the same 9 |
| runs | 14 a pass | 126 of 126 ran and all are kept; a median of 2 heats a launch (31–39 heater launches a pass) |
| stops | `build/e155/STOP`; board ≥ 66 W, a minion-shire reading ≥ 72 °C or a line ≥ 1.5 s old on a live sample (before every launch, every 0.1 s while waiting, and by the in-run watcher); run_e78's `--max-c 72`; another user's device process or this card's lock | none fired. In all 20,534 samples: board at most **59.48 W** (stop 66), the hottest-shire field 65 °C throughout (its latch; stop 72), the shires' mean 49–61 °C, 600 MHz, `since_reset_ms` −1 ([`telemetry-max.json`](telemetry-max.json)); no line was read 1.5 s stale |
| budget | at most 40 card-minutes, first config read to last; no session after 10:30 PST; passes end by 11:20 PST | **36.2** (04:30:48–05:07:01); claim to release about 37 min (04:30–05:07) |
| config | read at both ends, never set | TDP 65 W, 65 °C, 600 MHz, 499 mV in all 24 reads |

## Departures (dated)

- **Tue 3 Nov 2026, the passes ran 2.5 times faster than the queue's first estimate.** The registration projected 600 s a pass from E129's cool
  morning (522–650 s). This card's die started at 49 °C and settled at 53–61 °C with a median of two heats a launch, and the passes took 215–239 s;
  the queue's budget rule, unchanged, started nine. Recorded, not amended: no rule depended on the number of passes beyond the minimum of three.
- **The day's post's plan read lagged at the release**, as in E148: `delete_msg.mjs --plan` still showed the aifoundry3 lane's clause after that lane
  had dropped it, so `edit_replace.mjs` with `EXPECT_TEXT` refused (exit 7) as its rule says; the release text was rebuilt from what the edit box held
  (this card's clause alone), ` — released` appended, and saved (§ How it ran).

## How it ran

04:26:06–04:27:29 PST, before the commit, on the box with no device opened: Python 3.12.3; `check_e155.py` HARNESS OK (25 files: E148's 20 reused files
and the 5 binaries); the preflight GO; every script parsed; the queue's budget rule on a 1 s stub; `V3_DRY` of the stop test, the smoke and pass 15510
([`logs/desk/`](logs/desk/)). `et-who`: no process held a device node or card lock. 04:28:26 the registration was pushed (`82b5af8d`). 04:30 the claim,
under the discord lock, after a fresh `et-who`: the day's one card post, which the aifoundry3 lane had posted at 04:29 as
`<ai> **Claude says:** using aifoundry3 for 1 h, until ~05:29 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, was rewritten to
`<ai> **Claude says:** using aifoundry3 for 1 h, until ~05:29 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry1 card 1 for 1 h, until ~05:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
(`edit_replace.mjs` with `EXPECT_TEXT`, dry run, save, read back). 04:30:47 `session_e155.sh` started detached on the box (`setsid nohup`, T0 = the
launch): the 10:30 gate; `check_e155.py` (HARNESS OK); the preflight (GO); `et-who` (no holder); the opening config read; the stop-path test 15502;
the smoke 15501 and its gate; `queue_e155.sh`; the closing config read at 05:07:01; `et-who` (no holder). The other lab user's idle logins were
present throughout; no other user's process, device node or card lock was seen (E78's departure D1 for `aifoundry1-c*`).

Each pass ran E78's two burn-in runs of π, then 14 registered runs: π first and last, each format's zeros once in each of three segments, and E155's six
arms dealt round-robin with seed `E155|aifoundry1-c1|<pass>`. Each run launched at a 58 °C die reading after a 59 °C preheat, with 2 s quiet and 4 s
FMA runs on all 1,024 minions. The waits were bounded `ssh … 'bash -s'` calls that read the session's and the queue's log lines only; nothing was
copied off the box until the session had ended.

05:07 the release: the post then read (in its edit box) `<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~05:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`,
the aifoundry3 clause already dropped by its lane; this card was the last held, so it was rewritten to
`<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~05:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`
and read back. The data were then collected to the Intel ([`collect_e155.sh`](../../../../tools/claims-v3/e155/collect_e155.sh), the box's desk checks
into [`logs/desk/`](logs/desk/)), reduced and scored with [`pipeline_e155.sh`](../../../../tools/claims-v3/e155/pipeline_e155.sh).

## Device commands sent

Every command the run sent to card 1, classified at registration from the source of its running build: release 1.4.0, BL1 and BL2 0.22.0,
et-platform **`836a4ab`** (the version-matched revision of Q136(w)'s table and of E148's audit of the same command set). Q136(w)'s checker on every file
the session runs read **GO: 32 send sites, 0 disallowed, no WRITE allowed**, at the desk
([`dmcmd-audit.txt`](../../../../tools/claims-v3/e155/dmcmd-audit.txt)) and on the box before the first device opened
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt), 04:30:48 PST). **The run sent no WRITE** (`since_reset_ms` −1 in every sample).

| # | sent by | command (id) | class (BL2 0.22.0, `836a4ab`, under `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| 1 | `ettelem config` (session start and end, each block's start and end) | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | READ: `thermal_power_monitor.c:339` → `thermal_pwr_mgmt.c:613`, a copy from SP RAM |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | READ: `:438` → `:665`, SP RAM |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23) | READ: `:48` → `:551`, SP RAM |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | READ: `performance.c:41` → `perf_mgmt.c:276` (`get_module_asic_frequencies`, which also refreshes the SP's cached copy of the clocks in its RAM) → `io_pll.c:932`/`:907`, PLL register reads, and the strap pins (`reset.c:121`) *(corrected after verification, C6: this cited `performance.c:41` → `io_pll.c:907-960`, leaving out the `perf_mgmt.c` hop)* |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32) | READ: `thermal_pwr_mgmt.c:1142`, PVT reads and two `pmic_get_voltage` I2C register reads (allowed by the owner's rule of 2 November 2026) |
| 6 | `ettelem sample` (the 10 Hz sampler, and `lib.sh`'s 1 s die reads, which send rows 4–9) | `DM_CMD_GET_MODULE_POWER` (33) | READ: `:984`, SP RAM |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60) | READ: `performance.c:404` → `thermal_pwr_mgmt.c:2780`, SP RAM, no reset |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | READ: `:732`, PVT sensor reads |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31) | READ: `:1010`, nine `pmic_get_voltage` register reads (allowed) |
| — | `lib.sh:154`'s forwarded arguments (a possible `--reset-ms` = `DM_CMD_SET_STATS_RUN_CONTROL`, 62) | WRITE, conditional: **never sent** (the reviewed exception: `block_e155.sh:103` passes the file and the duration only, and `ettelem_guard.sh` refuses `--reset-ms`) | |
| — | `lib.sh`'s `drain_mgmt` (`dev_mngt_service`) | **never sent**: replaced by a refusal in `block_e155.sh` | |
| — | `sparsity_host` (E109's `build/e109`; E78's heater `build/sparsity`) | the Master Minion's device-ops: DMA writes and reads of device DRAM, kernel launches, an abort on a 6 s overrun: the workload, not a device-management command | |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads; they open no device node | |

Not sent: the statistics reset, the SP log level (67), `sptrace`, `dev_mngt_service`, the firmware-revisions query (14), a residency read, any
governor, TDP, threshold, clock or voltage set, any reset.

*Added after verification, C6.* `lib.sh`'s die reads (`die_c`, at each block's start and end) are `ettelem sample --seconds 1 --every-ms 500`, so
each sends all six sample commands, rows 4–9, not row 6 alone as the row said; every one is a READ. Row 4's chain gains the `perf_mgmt.c:276` hop,
whose refresh of the SP's cached clocks is already in Q136(w)'s table ([`dmcmd_table.json`](../../../../tools/claims-v3/dmcmd_table.json) ›
`GET_ASIC_FREQUENCIES`, `side_effects`). The registration's own table
([`tools/claims-v3/e155/README.md`](../../../../tools/claims-v3/e155/README.md) § Device commands sent, frozen at `82b5af8d`) carries the same two
imprecisions; it stays unchanged and this note corrects it. No class changes.

## What this cannot say

- **F1b's exclusion of the new-address count depends on how the bands were built** *(added after verification, C1)*. The frozen readings scale all
  of E148's sixteen-row N − N1, which under the premise the registration itself applies at three rows holds 0.087 ± 0.014 W of shared per-op work.
  On bands that take it out (post hoc) Wn's band is 0.382–0.504 W and D31's interval reaches it: F1b would read INCONCLUSIVE in every arm. F1a
  WALK and the toggle count's small errors (D31 −0.06 W registered, −0.03 W on that footing) hold on both constructions.
- **F1b rests on the per-op premise, which F3 does not bound at ±30 pJ.** Every reading of D31 assumes equal per-op work in the two formats. F3's
  interval (−18.8 to +35.1 pJ, after the frozen allowance) lets a per-op difference move D31 by −0.151 to +0.081 W, enough at its upper end to
  reach the new-address count's band (on the premise's footing the allowance moves by under 0.5 pJ and F3 stays INCONCLUSIVE, −19.3 to +34.7 pJ).
  The check by Q31k is post hoc and trades this premise for another: 0.184 W of its 0.220 W is B's halved traffic added back at fp32's price from
  its three arms (0.146 ± 0.077 pJ a TenB write, itself an effective number that absorbs fp32's TenA, scratchpad and register changes between the
  arms), which assumes int8's TenB writes cost what fp32's do; its interval (0.103–0.338 W) reaches the new-address count's frozen walk part
  (0.319–0.399 W), so it separates nothing *(corrected after verification, C3: this called Q31k "the premise-free check")*.
- **Wn's exclusion is narrow**: 0.018 W on the primary, 0.003 W with the meter's dips kept, and none on the premise's own footing *(corrected after
  verification, C1, C2: this said 0.017 and 0.002 W)*.
- **The A path is not excluded at three rows**: its band holds D31. Its exclusion as the sole per-row carrier is E148's (W2, two rows), and at three
  rows it rises with the walk, so this shape cannot separate them; the two-term mixture of E148 over-predicts D31 by 0.13 W.
- **RTL, not silicon, and a later revision.** The counts come from core-et's later revision (Erbium), not the ET-SoC-1's own RTL; R6 shows the
  schedule carries over, not the energy of each event.
- **One card, one morning.** The toggle count now fits two shapes in two sessions on aifoundry1 card 1; no other card has run these arms.
- **The per-cycle candidates stay together.** What stays at one row (0.93 W) may be per-cycle work or one row's A staging; no arm here separates
  them, or TenC's reads as such, the TIMA controls and the core.

## Files

`e155.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the primary reduction); `scored.json`, `results.md`, `score.log` (`score_e155.py`; the set-aside rule
chose the primary); `e155-relaxed.json`, `scored-relaxed.json`, `results-relaxed.md` and logs (always run, not needed); `e155-dipskept.json`,
`e155-auto.json` with their `scored-*`, `results-*`, `runs-*`, `reduce-*` (the two arms); `readme-numbers.txt` (every number above, printed by
[`numbers_e155.py`](../../../../tools/claims-v3/e155/numbers_e155.py), written while the passes ran); `telemetry-max.json`
([`telemetry_max_e155.py`](../../../../tools/claims-v3/e155/telemetry_max_e155.py), E148's); `posthoc/` (post hoc, deciding nothing: `posthoc_e155.py`,
written while the passes ran, and its `posthoc.txt`/`posthoc.json`); [`corrections-numbers.py`](corrections-numbers.py) with its
`corrections-numbers.txt` and `corrections-numbers.json` (post hoc, deciding nothing: every number the corrections after verification quote, from
committed files only; *added after verification*); `aifoundry1-c1/e155/p1551[0-8]/` (every pass's raw data: `runs.jsonl`,
`marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_start.json`, `config_end.json`, `manifest.txt`, `binaries.sha256`, `code.sha256`, `gen.sha256`,
`configs.json`, `plan.json`, `run.log`, `block.json`); `aifoundry1-c1/e155-smoke/p15501/`; `aifoundry1-c1/e155-stoptest/p15502/` (with `STOP.die`,
`STOP.board`, `STOP.watch`, `STOP.stale`, `stoptest.rc`); `logs/` (the session, its two config reads with their times, the queue, the preflight,
`binaries.sha256`, `T0`; `logs/desk/`, the box's checks before the claim). The registration and code are in
[`tools/claims-v3/e155/`](../../../../tools/claims-v3/e155/README.md).

Rerun from the repo root: `bash tools/claims-v3/e155/pipeline_e155.sh <out dir> docs/reports/data/2026-11-03-e155-int8-floor-rows/aifoundry1-c1/e155/p1551[0-8]`
(needs `uv` for numpy). Post hoc: `python3 docs/reports/data/2026-11-03-e155-int8-floor-rows/posthoc/posthoc_e155.py`; the corrections' numbers:
`python3 docs/reports/data/2026-11-03-e155-int8-floor-rows/corrections-numbers.py` (standard library only).

## Blog sentences, each with its baseline, its card and its source

*Any line about the RTL is about its later revision (Erbium, core-et), not the ET-SoC-1's own.*

- With nothing to multiply, an int8 matmul loop on this chip still draws more than the same loop in fp32, and the excess depends on the shape: 0.93 W
  with one row of A, 1.24 W with three, 1.63 W with sixteen. [aifoundry1 card 1, 600 MHz, nine passes; `scored.json` › `stats.N1`, `stats.N3`; E148
  `scored.json` › `stats.N`]
- The part that grows with rows is predicted best by how many bits of the accumulator memory's read address flip: frozen before the run, the
  bit-flip count predicted the rise from one row to three to within 0.06 W (± 0.10 W), where counting address changes missed by 0.18 W and
  assuming no change by 0.31 W. Whether counting address changes is ruled out depends on how its prediction is built, so this run favours the
  bit-flip count without excluding the other. [aifoundry1 card 1; `scored.json` › `rules.F1`, `reported.N3_out_of_sample`;
  `corrections-numbers.txt` C1] *(corrected after verification, C1, C4: this said the part "follows how many bits … flip, not how often that
  address changes", and "predicted the three-row excess to within 0.012 W from the one-row level measured the night before, where counting
  address changes missed by 0.13 W and assuming no change by 0.36 W")*
- That reading assumes the two formats spend the same energy on each operation's fixed work. Measured at three rows it is about 90 pJ an operation in
  each, equal to within −19 to +35 pJ, not yet inside the ±30 pJ the test asked for. [aifoundry1 card 1; `scored.json` › `rules.F3`,
  `stats.e3_fp32_pJ`, `stats.e3_int8_pJ`]
- The open RTL's schedule, plus one constant fitted earlier on silicon (7.75 cycles, E109), predicted two new schedules to the cycle: 128 and 110
  cycles an op in fp32 and int8 at three rows, 72 and 62 with half the K. [aifoundry1 card 1; `scored.json` › `rules.R6`; `corrections-numbers.txt`
  C5] *(corrected after verification, C5: this said "The open RTL predicted two new schedules on silicon to the cycle")*
- Run with half the K at three rows, int8 keeps one row's exact schedule but its accumulator walks. Pricing int8's halved B writes at fp32's (most
  of the 0.22 W it then costs), that is consistent with the bit-flip count's 0.26 W and does not rule out the address-change count's 0.32–0.40 W
  (post hoc). [aifoundry1 card 1; `posthoc/posthoc.txt` section 2; `corrections-numbers.txt` C3] *(corrected after verification, C3: this said "that
  alone costs about 0.22 W once the halved B traffic is added back, near the bit-flip count's 0.26 W")*

## Corrections after verification (Tue 3 Nov 2026)

An independent verifier (lane `verify-a1c1-e155-int8-floor`, about 05:20–05:50 PST) re-ran `pipeline_e155.sh` on the nine committed passes in a
`git archive` copy of `eb0d142b` (every scored file, reduction and table byte-identical), re-ran `posthoc_e155.py` (identical), re-derived the four
frozen bands by hand, recomputed every statistic with its own scorer, traced all nine commands sent to their handlers at et-platform `836a4ab`,
scanned all 20,534 samples (`since_reset_ms` −1 in each), and checked the registration's order, the stops, the card's release and the day's post.
Its verdict: the run holds, with fixes to how it is read. The corrections below (desk only, about 05:40–05:56 PST, pushed as `93637c7f`; no card opened, no device command,
nothing re-run, no Modal) change no measured number, rule, frozen prediction or registered verdict. Their numbers are printed by
[`corrections-numbers.py`](corrections-numbers.py) into [`corrections-numbers.txt`](corrections-numbers.txt), written independently of the
verifier's scorer; they reproduce its numbers, two of its roundings sharpened (the toggle count's D31 error on the premise's footing is −0.0288 W,
written −0.029, not −0.028; the mixed new-address price miss is 0.87 fJ, written 0.9, not 0.8), and they find one more truncated margin (the
dips-kept arm's Wn margin, 0.0028 W, written 0.002 before, now 0.003). The title said: "from one A row to three,
int8's no-issue floor rises 0.31 ± 0.10 W, inside the frozen band of the walk counted in address-bit toggles and outside the new-address count's (by
0.017 W) and per cycle's (F1a WALK, F1b TOGGLES); the toggle count predicted the three-row floor to 0.012 W" (C1, C2, C4).

- **C1 (major): F1b's exclusion of the new-address count depends on how the bands were built.** `make_predictions_e155.py` › `reading()` builds Wn,
  Wt and T as the bench's count ratio (0.5418, 0.3853, 0.2271) times *all* of E148's sixteen-row N − N1 (0.747 W), plus the shared per-op term at
  three rows, E_op × 0.782 × 10⁹ = 0.085 W. That term rests on the premise of equal per-op energy in the two formats; by the same premise E148's
  sixteen-row N already holds E_op × 0.7996 × 10⁹ = 0.087 ± 0.014 W (int8 318 cycles an op there, fp32 544), which the readings count as walk. With
  it taken out of each E148 pass at that pass's E_op (post hoc) the points fall by 0.047, 0.033 and 0.020 W and the bands, by the registration's own
  interval rule, are Wn 0.382–0.504 (registered 0.430–0.549), Wt 0.292–0.387 (0.327–0.419) and T 0.201–0.269 W (0.222–0.288); paired per E148
  pass, Wn 0.398–0.488. D31's interval (0.208–0.413) reaches Wn's band, so on that footing F1b would read INCONCLUSIVE, in every arm. Unaffected:
  F1a WALK (C is built on N1, which has no rate gap; excluded by 0.047 W) and the toggle count's small errors (D31 −0.062 registered / −0.029 on the
  footing; N3 −0.012 / +0.021 W), against the new-address count's −0.179 / −0.132 and −0.129 / −0.082 W. At two rows (E148's post hoc check) the
  new-address count stays excluded on that footing too (residual −0.134 ± 0.079 W; the toggle count −0.004 ± 0.085 W). F3's frozen allowance,
  priced from the same N − N1, moves by under 0.5 pJ on that footing and F3 stays INCONCLUSIVE (−19.3 to +34.7 pJ). The one-term prices had the
  same mismatch: E155's take the session's shared term out, E148's 50.5 and 94.8 fJ keep it in; matched, E148's are 44.7 ± 5.8 fJ a toggle and
  83.8 ± 10.9 fJ a new-address read (at its own E_op) or 43.6 and 81.8 fJ (at this session's), so the toggle prices agree on every footing and the
  new-address prices (E155 49.3 ± 22.7 fJ) miss by 0.9 fJ only in the mixed comparison and overlap when one E_op serves both. § What it does to
  predicting power and heat said "So the rise's error falls from 0.31 W (the null) or 0.18 W (the registered count) to 0.06 W, inside the
  measurement's ±0.10 W. Its price, 50.5 fJ an address-bit toggle at sixteen rows (E148) and 36.9 ± 17.0 fJ at three (post hoc), lets a model carry
  the floor to any int8 shape from the bench's toggle count"; it is rewritten with both footings. Result 1 gains the footing; result 2's table gains
  its column; result 6(b), What it changes, What this cannot say and blog sentence 2 are corrected. F1b TOGGLES stays the registered verdict.
- **C2 (major): "inside the band" was wrong, and three margins were truncated.** The title, the plain words and the lane's headline said the rise is
  *inside* the toggle count's frozen band. D31's point, 0.311 W, lies 0.016 W *below* that band (0.327–0.419 W); the registered rule is interval
  overlap, and D31's 95% interval (0.208–0.413) overlaps it and stops 0.018 W short of the new-address count's (0.430–0.549). The margins were
  written 0.017 (Wn), 0.046 (C) and 0.002 W (Wn, dips kept): they are 0.0176, 0.0469 and 0.0028 W, so 0.018, 0.047 and 0.003. The title, the plain
  words, result 1 and What this cannot say are corrected.
- **C3 (minor): Q31k was called premise-free and said to agree.** It needs no premise about the two formats' per-op work, but 0.184 W of its
  0.220 W is B's halved traffic added back at fp32's three-arm price (0.146 pJ a TenB write), which assumes int8's TenB writes cost what fp32's do;
  its interval, 0.103–0.338 W, reaches the new-address count's frozen walk part (0.319–0.399 W), so it is consistent with the toggle count and
  separates nothing. The plain words said "A check that needs no such assumption … agrees (post hoc)"; result 6(a), What it changes, What this
  cannot say ("The premise-free check (Q31k)") and blog sentence 5 said the same. All are corrected.
- **C4 (minor): "N3 to 0.012 W" without its interval.** The title, the plain words and blog sentence 2 quoted the toggle count's N3 error with no
  interval. It is −0.012 ± 0.083 W; the per-row term's own test is the rise, −0.062 ± 0.102 W, and N3's error is smaller because this session's N1
  sits 0.050 W above E148's. They now quote both with their intervals, and § What it does to predicting power and heat leads with the rise.
- **C5 (minor): blog sentence 4 credited the open RTL alone.** It said "The open RTL predicted two new schedules on silicon to the cycle". The
  frozen cycles are the bench's plus E109's one constant, 7.75 cycles, fitted earlier on silicon on the ordinary op (120.25 → 128, 102.25 → 110,
  64.25 → 72, 54.25 → 62). Result 4 and the sentence now say so.
- **C6 (minor): citation precision in Device commands sent** (no class changes; every command is a READ). Row 4 skipped the `perf_mgmt.c:276` hop
  (`get_module_asic_frequencies`, which refreshes the SP's cached clocks; Q136(w)'s `dmcmd_table.json` has it). Row 6 listed only
  `GET_MODULE_POWER` for `lib.sh`'s 1 s die reads, which are `ettelem sample --seconds 1` and send rows 4–9. The registration's own table carries
  both and stays frozen; the note under the table corrects it. The lane's result said "all 24 config reads identical"; TDP, threshold, clock and
  voltage were identical in all 24, and the power state read `low_power` 6 times and `managed_power` 18, as this README's header already said.

The integration lanes' suggested wording for item 11 changes with C1 and C2: "E155 (registered, card 1, nine passes): from one A row to three the
floor rises 0.31 ± 0.10 W; per cycle is excluded (F1a WALK) and the walk counted in address-bit toggles predicts the rise to −0.06 ± 0.10 W (N3 to
−0.01 ± 0.08 W) out of sample, against −0.18 W for the new-address count and +0.31 W for no change; F1b reads TOGGLES as registered, but on bands
that also take the shared per-op term out of E148's sixteen-row base the new-address count is not excluded (post hoc); the per-op premise is
measured at three rows, −19 to +35 pJ (F3 INCONCLUSIVE at ± 30); what stays at one row (0.93 W) is unseparated."
