# Q140(l): aifoundry2's level and session terms. The die at a burst's start, the zeros level and the cap's plateau carry leave one session out; s(f) at n = 2 from the reads changes nothing

*Wed 4 Nov 2026 (week 45), Q140's desk half, on the Intel. Desk only: no card, no device command, no ssh to a lab box,
nothing from the private archive. **Registered first:** the candidate terms, the folds, the fitting stages, what is
scored and the rule ([`REGISTRATION.md`](REGISTRATION.md), [`registration.json`](registration.json)) were committed in
`245caffe` at **00:43:45 PST**, before any fit, score or prediction of this lane was computed. The registered fit ran
00:49-00:56 PST ([§ Registered against what happened](#registered-against-what-happened), D1). It answers Q139's final
critic's **rank 2** ("aifoundry2's level and session terms ... desk-testable now leave one session out on
E80/E83/E143/E160") and **rank 8** ("fit s(f) jointly with the session term ... leave one session out"). On the kinds
page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) that is item 6 (a
power model across kinds). Through the level it also feeds items 8 and 9 (heat over minutes) and item 1 (the large GEMM).
The owner's goal, 2 November 2026: to predict the power requirement and heat generation of numeric computations as
accurately as possible.*

*Corrected after verification, Wed 4 Nov 2026, from 01:37 PST to this commit, after the registered result (`5b98bd5c`). The
verifier found nine minor faults. Each corrected passage is marked "corrected after verification, C<n>", and the old
wording is in [§ Corrections after verification](#corrections-after-verification). No frozen file, fitted number,
registered score, rule or verdict changed: `m9_a2.json` and `predict_m9_a2.py` are as committed. One correction is a
new post hoc reading that weakens a quoted figure (C4). With the selection itself nested inside each fold, the held-out
errors read 5.12 MHz / 0.93 W / 0.92 W against the registered 5.00 / 0.89 / 0.75, and 6.90 MHz on the clock under a
stricter inner rule.*

## The answer

**Three session terms carry, and together they take aifoundry2's held-out burst errors down by a third to a half.**
Each of the four burst sessions was held out in turn and predicted by a fit on the other three: 134 cells, every one with
its D measured on aifoundry3 on Q139(u)'s footing. Pooled over the four sessions:

- **Governed clock: 6.25 → 5.00 MHz rms.** The before is M7 as frozen, which is in sample on E80 and E83; M8 as frozen
  reads 6.60, and M8's form with its cap refitted per fold 7.33.
- **Governed board: 1.62 → 0.89 W rms**, and the bias falls from +1.23 to −0.05 W.
- **Pinned board: 1.52 → 0.75 W rms**, and the bias falls from −1.22 to −0.15 W.

*Corrected after verification, C4: the terms were chosen on these same folds, so these figures carry the selection's
optimism. E165's blind session is the clean test of the error.* Post hoc ([`corrections.txt`](corrections.txt) C4), the
registered forward rule was run inside each fold, on its three training sessions only (each inner fold fitted on two).
The rule has no exact three-session form, so it was run two ways:

- **at 2 of 3 inner sessions:** T1-T4 are kept in three folds. E143's fold drops T2. Without E143, T2 lowers both boards
  in all three inner sessions, but it raises the inner clock's pooled rms 6.44 → 7.14 MHz (lower in none of the three)
  before the die start is in (D5's order). Pooled, the nested errors read **5.12 MHz / 0.93 W / 0.92 W**, against the
  registered 5.00 / 0.89 / 0.75.
- **at 3 of 3:** T3 also drops in E83's and E143's folds, and the nested errors read **6.90 MHz / 0.89 W / 0.88 W**.

So both boards' gains survive the nested selection (governed 1.62 → 0.89-0.93 W, pinned 1.52 → 0.88-0.92 W). The clock's
gain over M7 as frozen (6.25 MHz) survives only the looser form. Against A0, the selection's fair base (7.33 MHz), the
clock gains under both. The inner fits rest on two sessions each, so these nested figures lean pessimistic, and the
registered ones optimistic.

The registered rule (a term carries on a quantity if its held-out rms falls in at least 3 of the 4 sessions and pooled)
kept the terms in the registered order:

| step | against | governed clock: sessions lower, pooled rms (MHz) | governed board (W) | pinned board (W) | verdict |
|---|---|---|---|---|---|
| **T1** cap level (the capped tiles' plateau over the cap) | A0 | 0/4, 7.331 → 7.331 | 4/4, 1.568 → 0.977 **carries** | 2/4, 1.515 → 1.520 | **kept** |
| **T2** same-session zeros-anchor level | T1 | 3/4, 7.331 → 6.646 **carries** | 4/4, 0.977 → 0.912 **carries** | 4/4, 1.520 → 0.918 **carries** | **kept** |
| **T3** die-start term | T1+T2 | 4/4, 6.646 → 4.994 **carries** | 2/4, 0.912 → 0.888 | 3/4, 0.918 → 0.747 **carries** | **kept** |
| **T4** s(f) at n = 2 from the reads, jointly | T1+T2+T3 | 2/4, 4.994 → 4.998 | 0/4, 0.888 → 0.890 | 3/4, 0.747 → 0.745 **carries** | **kept**, by 0.002 W |

([`fit-output.txt`](fit-output.txt); [`loso.json`](loso.json) `forward_steps`.) **T4 is kept by the rule's letter, and
its effect is nil.** Its pinned board falls by 0.002 W in 3 of 4 sessions, while its clock and governed board rise by 0.004
MHz and 0.002 W, inside the registered tolerance. The voltage reads' s(f) at n = 2 (1 / 1.4025 / 1.8999) and M8's frozen
one (1 / 1.4082 / 1.9052) predict the same to that size. **The exponent n = 2.28 was never used, and no exponent was
fitted.**

**What each term is, as fitted on all four sessions** ([`m9_a2.json`](m9_a2.json) `params`; the fold-to-fold ranges are
from the four leave-one-out fits):

- **The die at a burst's start: +0.395 W per °C** (0.386-0.417 over the folds) at every operating point. Under the cap
  that is **−2.4 MHz per °C**. E143's bursts started at 55.5 °C on average and E160's at 53.7 °C. The terms take the
  governed clock's session means from −4.52 and +3.43 MHz (M7 as frozen) to −2.62 and +1.91 MHz. *Corrected after
  verification, C2:* **that removes about half of the "session offset whose sign flipped"** that the critic found, and the
  sign still flips. Held out, 42% of E143's offset and 44% of E160's are removed, and 43% of their split (7.95 → 4.54
  MHz). T3's own step halves the split (9.00 → 4.52 MHz). The frozen code's −2.3 MHz per °C on the governed cells, times
  the two sessions' 1.81 °C gap, is 4.2 MHz, 53% of M7's split ([`corrections.txt`](corrections.txt) C2).
- **The zeros level:** the session's own zeros anchors, referred to a common die start (54.38 °C), sit **1.35-1.74 W
  under the relation's 800 MHz zeros level in every measured session and format** (*corrected after verification, C8:*
  11 of the 12; E80 ran no fp32 anchor, and its fp32 offset, −1.48 W, is filled from its other two). That level is M8's
  to within 0.01 W. Raw, they spread 1.11-2.71 W: most of that spread was the die. A tile's levels move by **0.648 W
  per W** of its format's anchor offset (0.62-0.69). With no anchor read, the frozen fallback is −1.51 to −1.54 W per
  format.
- **The cap's plateau:** the governor holds a capped burst's board **2.52 W over the effective cap** (2.29-2.75). The
  cap that fits the clocks falls to **64.60 W** (M8 65.20, M7 65.58) once the zeros level is lowered. So the model puts a
  fully capped burst's board near 67.1 W; the capped tiles of E143 and E160 measured 66.7-66.9 W.

**Per held-out session** (measured − predicted, rms (mean); [`fit-output.txt`](fit-output.txt)):

| | E80 | E83 | E143 | E160 | pooled |
|---|---:|---:|---:|---:|---:|
| cells: governed / pinned | 6 / 10 | 11 / 24 | 21 / 15 | 18 / 29 | 56 / 78 |
| **governed clock, MHz**: M7 as frozen | 4.80 (+4.49) | 8.53 (−0.94) | 6.20 (−4.52) | 4.97 (+3.43) | 6.25 (−0.30) |
| M8 as frozen | 7.07 (+6.85) | 8.63 (+1.41) | 4.93 (−2.40) | 6.71 (+5.60) | 6.60 (+1.92) |
| **M9's aifoundry2 part, held out** | **4.92 (+3.11)** | **6.93 (−1.05)** | **4.78 (−2.62)** | **3.71 (+1.91)** | **5.00 (−0.24)** |
| **governed board, W**: M7 as frozen | 1.49 (+1.06) | 2.18 (+1.87) | 1.67 (+1.29) | 1.15 (+0.82) | 1.62 (+1.23) |
| M8 as frozen | 1.79 (+1.43) | 2.54 (+2.27) | 1.97 (+1.63) | 1.44 (+1.16) | 1.93 (+1.58) |
| **M9's aifoundry2 part, held out** | **1.01 (−0.31)** | **1.21 (+0.46)** | **0.83 (+0.05)** | **0.66 (−0.39)** | **0.89 (−0.05)** |
| **pinned board, W**: M7 as frozen | 2.08 (−1.62) | 1.55 (−1.24) | 0.91 (−0.58) | 1.50 (−1.38) | 1.52 (−1.22) |
| M8 as frozen | 2.07 (−1.61) | 1.55 (−1.24) | 0.91 (−0.57) | 1.50 (−1.38) | 1.51 (−1.21) |
| **M9's aifoundry2 part, held out** | **1.46 (−0.54)** | **0.66 (−0.33)** | **0.55 (−0.02)** | **0.49 (+0.05)** | **0.75 (−0.15)** |

Against M7 as frozen, paired over cells inside each session (2,000 draws), M9's part is resolved better as follows:

- **pinned board:** in all four sessions;
- **governed board:** in E83, E143 and E160;
- **governed clock:** in E83, E143 and E160. In E80 it reads +0.11 MHz [−2.04, +1.46]: E80 has 6 governed cells, and
  M7's cap was fitted on it.

These intervals hold no session term ([`loso.json`](loso.json) `final_vs_references_bootstrap`).

**End to end, with the D the models actually predicted blind** (E143 with M7's frozen D, E160 with M8's, the
non-anchor registered tiles): **E160** governed clock 6.72 MHz (M8; M7 5.14) → **3.68**, governed board 1.39 W (M7 1.11)
→ **0.66**, pinned board 1.70 → **0.80 W**; **E143** 6.64 MHz → **5.12**, 1.60 → **0.86 W**, 1.18 → **0.87 W**. These are
the figures the critic quoted, now with the session terms ([`loso.json`](loso.json) `end_to_end_blind_D`).

**The critic's rank-2 targets** for the next blind session (governed clock rms ≤ 4 MHz with |mean| ≤ 2 MHz; governed
and pinned board |mean| ≤ 0.5 W; pinned rms ≤ 1.0 W) are met here, held out, on **E160 entirely** and on the board
everywhere but E80's pinned tiles (1.46 W, mean −0.54). **The governed clock is still the open part:** 4.8-6.9 MHz rms
on E80, E83 and E143, with session means of +3.1 and −2.6 MHz on E80 and E143 ([`loso.json`](loso.json)
`rank2_targets_on_final_loso`).

**The checks the critic named** (reported; no anchors ran in either, so they take the fallback). *Corrected after
verification, C1: the figures depend on the die law M9's level is composed with, and the two compositions differ by
0.3-1.0 W* ([`corrections.txt`](corrections.txt) C1; post hoc, linear):

- **E161's first hold:** inside G1Q's kernel launches, M8's 800 MHz board is **0.91 W high**.
  - **(a) The zeros-level shift alone,** with the hold's own die law kept (Q139(e)'s 0.442 W/°C from its 56.0 °C
    reference die): M9's int8 level is 0.99 W lower, which leaves **0.08 W low**. This was the figure quoted here.
  - **(b) M9 whole:** its die-start term (0.395 W/°C from its 54.38 °C T_ref) in place of Q139(e)'s law, carried to
    the 62.9 °C plateau, leaves **0.24 W high**.
  - The assumptions differ. Q139(e)'s 56.0 °C is the die on E144b's hold line that matched one E80 burst launched at
    55 °C or less, and (a) assumes that match holds for M9's level. M9's k_T was fitted on burst starts of 45-56 °C, so
    (b) extrapolates it 6.9 °C above the highest. No rule here chooses between them.
- **E159's zeros GEMMs:** G3 reads them 2.43-2.49 W high.
  - **(a) The shift alone:** M9's fp32 level shift (−0.99 W) would leave **1.43-1.49 W** high. G3's P0 has no start-die
    term; its 0.1 W/°C effective constant runs from each run's own start die. The rest is the GEMM's own level, P0. The
    measured GEMM zeros draw 0.32-0.37 W under M8's kinds zeros level, and about 0.66 W over M9's.
  - **(b) With M9's k_T as a start-die term on P0** (the role G4's own start-die term has in Q140's brief), the three
    holds read **−2.49 / −0.95 / −0.49 W** (measured − predicted) from their starts of 57, 53 and 52 °C. Their measured
    window boards spread only 0.06 W (35.98-36.04 W), where such a term spreads the prediction by 2.0 W.

## What this does to predicting power and heat

**Terms tested:** aifoundry2's governed relation P(f) = B(f) + c·s(f), plus four candidates (cap level, same-session
zeros level, die start, s(f) at n = 2 from the reads). Three carry. The fourth is nil. **Out-of-sample error before →
after:**

- **Leave one session out, pooled, on measured D** (before = M7 as frozen, in sample on E80/E83; M8 as frozen in
  brackets):
  - governed clock 6.25 (6.60) → **5.00 MHz rms**;
  - governed board 1.62 (1.93) → **0.89 W**;
  - pinned board 1.52 (1.51) → **0.75 W**;
  - the governed clock's per-session means move from −4.52…+4.49 to **−2.62…+3.11 MHz**.
  - *corrected after verification, C4:* the terms were chosen on these same folds. With the selection nested inside each
    fold (post hoc), the pooled errors read 5.12 MHz / 0.93 W / 0.92 W (inner rule at 2 of 3) or 6.90 / 0.89 / 0.88 (at
    3 of 3). E165's blind session is the clean test.
- **End to end, blind D:**
  - E160 governed clock 6.72 (M8) / 5.14 (M7) → 3.68 MHz; governed board 1.39 / 1.11 → 0.66 W; pinned board 1.70 →
    0.80 W.
  - E143 6.64 → 5.12 MHz; 1.60 → 0.86 W; 1.18 → 0.87 W.

**Heat.** A 6 s burst's die rise follows the board through M8's frozen burst law (0.140 °C per W). Post hoc, on the
held-out boards ([`posthoc.txt`](posthoc.txt) P4), it reads **E143 0.548 → 0.467 °C** and **E160 0.562 → 0.438 °C rms**.
For heat over minutes, the critic counted M8's in-work level, 0.91 W high on E161's G1Q, as the larger part of that
hold's −0.90 °C plateau error. *Corrected after verification, C1:* M9's level leaves it **0.08 W low with the zeros-level
shift alone** (Q139(e)'s die law kept), or **0.24 W high with M9's own die-start term** in that law's place (above).
Through E161's committed fixed points (linear, post hoc: 0.94 °C per W of level at continuous work, 0.91 at the kernel
duty), G1Q's plateau error goes:

- under continuous work, from −0.90 °C (M8) to +0.03 °C (shift alone) or −0.27 °C (M9 whole);
- at the kernel duty, from −0.39 °C to +0.51 °C or +0.22 °C.

Q140(e) composes it properly, with exactly one die law registered (see *For the later lanes*). For the large GEMM, G3's
zeros miss of about −2.45 W becomes −1.45 W with the shift alone, or −2.49 / −0.95 / −0.49 W with M9's k_T as P0's
start-die term.

*Corrected after verification, C3:* **rank 8's desk rule is not met.** The rule asks that the governed clock beat s(f) at
n = 2 by a resolved margin in every held-out session. The joint fit is lower in all four, and the gain is resolved in three
(E83, E143, E160), not in E80 (P5).

**What the corrections after verification do to prediction** (dated Wed 4 Nov 2026; [`corrections.txt`](corrections.txt)):

- No frozen number changes. The registered held-out errors stand as registered: 5.00 MHz / 0.89 W / 0.75 W pooled.
- The selection's optimism is now measured (C4). Nested, the errors are 5.12 MHz / 0.93 W / 0.92 W, or 6.90 MHz on the
  clock under a 3-of-3 inner rule. The bands' rule on the nested errors gives a pinned-board band of 1.48-1.75 W against
  the frozen 1.26 W, so the frozen pinned-board band may be narrow for a new session.
- The handoff for heat over minutes and the GEMM is corrected (C1). E161 G1Q's in-work level after M9 is −0.08 W or
  +0.24 W, against M8's +0.91 W, depending on the one die law Q140(e) registers. Its plateau error at the kernel duty is
  then +0.51 or +0.22 °C, against M8's −0.39 °C. E159's zeros miss is −1.45 W, or −0.49 to −2.49 W.

**What it does not do:** the governed clock is still 5 MHz rms held out. The session means still spread ±3 MHz after
the die start. Everything rests on four sessions of one card under one governor.

## M9's aifoundry2 part, frozen

- [`m9_a2.json`](m9_a2.json) (sha256 `cc6fbccc…`). It holds:
  - the relation: the reads' s(f) at n = 2, B refitted on E64's rows, and c_zeros = 1.442 / 1.396 / 2.127 W;
  - g = 0.98487, from xfer 1.01536;
  - the cap W = 64.60 W, Δcap = 2.525 W, β = 0.648, k_T = 0.395 W/°C, T_ref = 54.38 °C;
  - each session's die-referred anchor offsets, and the fallback;
  - the bands;
  - M8's burst heat law, unchanged;
  - M8's peak rule, unchanged.
- **Bands** (95th percentile of |held-out error| by the model's own predicted group):
  - governed: **9.65 MHz / 1.85 W**;
  - pinned: **15.35 MHz / 1.26 W**. The pinned clock band is wide because of the seven slow bursts (C9 in *What it
    cannot say*), which no model predicts.
  - M8's frozen bands were 16.95 MHz / 3.50 W pooled.
  - *Corrected after verification, C4 (information only; the frozen bands stay):* the same rule applied to the nested
    errors gives governed 9.77-11.97 MHz / 1.84-2.06 W and pinned 15.20-15.35 MHz / **1.48-1.75 W**
    ([`corrections.txt`](corrections.txt) C4).
- **The 82 W admission value stays M8's** (P800(c) + 1.94 W, and + 2.95 W at D's band top), with no level shift. As
  registered, a level term must not loosen a stop validated without it.
- [`predict_m9_a2.py`](predict_m9_a2.py), the frozen prediction code. Its call is
  `burst(D, t, anchors=None, die_starts=None, D_band_hw=0.0)`:
  - **Inputs:** D at 600 MHz on aifoundry3's footing and the format t, with the session's own zeros-anchor reads (per
    format, each anchor burst's `burst_w`, `burst_mhz`, `die_start`) and each burst's die start.
  - **It returns** the same keys as `predict_blind6.py`'s aifoundry2 record (clock, board, burst D, die rise, their bands,
    `P800_w`, M8's peak and its 82 W flag).
  - **It also returns** the sensitivities: per W of anchor offset, −3.9 MHz on a capped tile and +0.65 W on a pinned
    one; per °C of die start, −2.4 MHz and +0.40 W.
  - **For a blind protocol,** predictions can be frozen at the fallback and T_ref, then recomputed mechanically from the
    anchors and die starts once they are read. Nothing in it refits.
  - [`selftest_predict_m9_a2.py`](selftest_predict_m9_a2.py) → [`selftest-predict-m9a2.txt`](selftest-predict-m9a2.txt):
    it reproduces the fit's in-sample predictions of all 134 cells to 3e-13 MHz and 6e-14 W, uses the fallback with no
    anchors, fills E80's missing fp32 anchor from the other two, and leaves E160's 752 MHz fp16 anchor burst out. PASS.
    *Corrected after verification, C7:* that last check only counted the data's bursts. It now recomputes the anchor's
    offset from `m9_a2.json` over the two bursts at 795 MHz or more (−1.6676 W, against −2.3300 W with the 752 MHz burst
    counted), and compares it with the code's offset and with the fit's `session_deltas_w` for all three formats. A
    scratch mutation test, a predictor that counts the 752 MHz burst, now fails that check; the old check passed it.
- **For the later lanes:**
  - Q140(m)'s `predict_blind7.py` imports `predict_m9_a2.burst` for aifoundry2.
  - Q140(e) and Q140(q) take the level from `m9_a2.json`. *Corrected after verification, C1:* each registers **exactly
    one die law, with its reference temperature**, and never two slopes over the same span:
    - either **M9 whole:** β·δ(t) + k_T·(T − T_ref), with k_T = 0.395 W/°C from T_ref = 54.38 °C, a burst-start law
      (E161 G1Q +0.24 W; E159 −2.49 / −0.95 / −0.49 W);
    - or **the zeros-level shift alone**, β·δ(t) at T_ref, with the run's own law: Q139(e)'s 0.442 W/°C from its
      56.0 °C reference die, or G4's start-die term (0.44-0.50 W/°C) with its reference stated (E161 −0.08 W; E159
      −1.43 to −1.49 W on G3's P0).
    - The cap adds Δcap·Φ((L800 − W)/σ) either way. Moving the level between 54.38 and 56.0 °C is 0.64 W at k_T and
      0.72 W at 0.442 W/°C, as large as the effect, so the reference must be stated.
  - **E165** should still run its zeros anchors first. Post hoc, though (P2 below), with the die start known, the
    session's own anchors beat the frozen fallback by only 0.22 MHz on the governed clock and by nothing on the board.

## Registered against what happened

Number by number, what was registered in `245caffe` and what is post hoc:

| # | registered | what happened |
|---|---|---|
| 1 | four candidate terms, their forms, order T1-T4; never n = 2.28 or a fitted exponent | as registered; no other term or form tried |
| 2 | data: four sessions, cells, runs, zeros anchors as inputs; 134 scored cells (16 / 35 / 36 / 47) | as registered: 134, none without a measured D |
| 3 | D = measured aifoundry3 D on Q139(u)'s footing (E78, E141, E153 rows) | as registered |
| 4 | groups fixed by M8 as frozen (< 795 MHz governed) | 56 governed, 78 pinned |
| 5 | stages S1a (k_T, within-session slope, pinned runs ≥ 795 MHz), S1b (β through the origin), S2 (W on M8's grid), S3 (Δcap through the origin) | as registered |
| 6 | scored per held-out session and pooled: governed clock, governed board, pinned board (rms, mean) | as registered (the tables above) |
| 7 | the rule: carries on a quantity if lower in ≥ 3 of 4 and pooled; kept if it carries on one and harms no other by more than 0.15 MHz / 0.03 W | T1, T2, T3 kept clearly; **T4 kept by 0.002 W**, its effect nil. *C4 (post hoc):* nested inside each fold, E143's fold drops T2, and at 3 of 3 E83's and E143's folds also drop T3 |
| 8 | freeze: m9_a2.json, per-group bands, M8's heat law and peak rule unchanged, fallback δ, prediction code with the anchors as input, self-test | as registered (D3 on the bands' group) |
| 9 | reported: M7/M8 as frozen, each term alone, bootstrap vs M7/M8, rank-2 targets, reproduction checks, end to end with blind D, E159/E161 checks, per-fold parameters | all reported; both reproduction checks OK (E143: 6.635 / 1.601 / 1.007 / 1.185 against 6.629 / 1.601 / 1.007 / 1.184; E160: 6.722 / 1.391 / 3.891 / 1.725 against 6.72 / 1.39 / 3.89 / 1.73) |
| — | **post hoc** ([`posthoc_q140l.py`](posthoc_q140l.py) → [`posthoc.txt`](posthoc.txt), written after the registered result was read; nothing frozen depends on it) | P1-P5 below; the E161 plateau reading above |

**Departures and notes** (dated Wed 4 Nov 2026):

- **D1 (00:49-00:53 PST): T1-T3's numbers were seen before T4's were computed.**
  - The first complete run was killed (signal 9, 17 GB resident) inside T4's voltage table, after it had printed the
    T1-T3 steps. Q139(s)'s `voltage_table` also fits each point's droop with an n×n weight matrix (`np.diag`), about 20 GB
    for aifoundry2's 600 MHz point, and T4 needs none of it.
  - The fit now computes the same PVT busy means directly. It checks them against Q139(s)'s committed
    `clock-voltage.json` (all reads, and without E143) before use; the worst difference is 0.0.
  - The whole run was repeated from the start, and T1-T3's printed numbers were identical.
  - The rerun changed nothing in the procedure.
  - Before that, one attempt stopped on a syntax error under the system python 3.9, with nothing computed.
  - *Corrected after verification, C6:* between those two, a run started at 00:49:15 PST was killed by the system (signal
    9, exit 137) after 45 s, with nothing printed. The fit then only collected its lines; the echo to stderr was added
    before the next run, at 00:50:36, the one that printed T1-T3. No number was seen from it.
- **D2:** the T4 chain's label string read "without nothing" and was reworded. m9_a2.json's numbers are byte-identical
  (the diff shows the label only).
- **D3: the bands' group.** The registration says "per predicted group". The code uses the final model's own held-out
  predicted clock (below 795 MHz), which is the group the prediction code sees when it is used.
- **D4: the registration's header gives its window as "about 00:10-00:55 PST".** *Corrected after verification, C5:*
  the lane read the committed files from 00:24 PST, wrote REGISTRATION.md at 00:42-00:43 and committed it at 00:43:45
  (`245caffe`). "00:10" was wrong, and so was "from about 00:15"; the end time was an estimate made before the commit.
  The dated amendment is [`REGISTRATION-A1.md`](REGISTRATION-A1.md), and the registration keeps its text.
- **D5: the order mattered for T2's test.** The registered order put T2 before T3, so T2 was first judged without the
  die start. Post hoc (P1), T2 carries on all three quantities when added last as well.

## Post hoc readings (not registered)

- **P1. Dropping T2 once the die start is in.** T1+T3 reads 5.23 MHz / 0.96 W / 1.35 W pooled. The frozen model reads
  5.00 / 0.89 / 0.75, lower on every quantity in 4 of 4 sessions. So the zeros level is needed whatever the order.
- **P2. The session's own anchors against a frozen offset.** Replacing each held-out session's anchors with the fold's
  fallback (the three training sessions' mean, die-referred) gives 5.22 MHz / 0.89 W / 0.75 W. The own anchors are better
  by 0.22 MHz on the governed clock (4 of 4 sessions) and 0.00 W on the board. **Once the die start is in, almost all of
  T2's value is the level itself, about −1.0 W at 800 MHz, not the session's read.**
- **P3. By format** (held out):
  - fp32: governed clock 5.43 MHz (+0.84), governed board 1.08 W, pinned board 1.09 W;
  - fp16: 4.53 MHz (−1.33), 0.65 W, 0.68 W;
  - int8: never governed; pinned board 0.56 W.
  - The sessions' mean die starts: E80 53.88, E83 54.41, E143 55.46, E160 53.65 °C.
- **P4. Heat:** the burst rise through M8's law, as quoted above. **P5. The critic's rank-8 reading:** against s(f) at
  n = 2 with no session term (A0, or T4 alone), the frozen model's governed clock is lower in all four held-out sessions.
  The gain is resolved in E83, E143 and E160 (−1.6, −3.2 and −2.5 MHz), and not in E80 (−0.35 [−2.53, +0.99]). So the
  critic's rule, "by a resolved margin in every held-out session", is met in 3 of 4. **The missing piece was a session
  term (the die), not a clock-voltage form**, as the critic said.

## What it cannot say

- **Four sessions, one card, one governor build (BL2 0.22.0), 31 Oct to 3 Nov.** The terms are tested out of sample
  across sessions, not across cards or firmware. E80 and E83 ran the same day.
- **The die start is the firmware's whole-degree reading**, and there is no inlet thermometer. So k_T cannot be split
  into the die's own leakage and the room.
- **Δcap is the gap between the board meter's plateau and the relation's effective cap**, not a governor constant.
  Whether the governor regulates another sensor, or the relation is low at high power, is not separated.
- **The pinned cells' slow bursts are not predicted by any term.** Seven of the 351 scored bursts, all in cells the
  relation calls pinned, ran at 721-788 MHz with the board far under the cap (35.8-50.2 W)
  ([`rows-m9a2.json`](rows-m9a2.json)). *Corrected after verification, C9* ([`corrections.txt`](corrections.txt) C9):
  - four, at 751-758 MHz (E80 once, E83 twice, E160 once), match E160's mid-burst idle status (its M1: about 45 MHz
    lost);
  - one, E80's `fp32.nn_like`, ran at 721.6 MHz;
  - E143's two, at 784.0 and 787.8 MHz, are shallow dips, not that pattern.

  They set the pinned clock band (15.35 MHz).
- **Nothing here touches the 600 MHz model.** D is Q140(m)'s; end to end, its error adds.

## Device commands sent

None. This lane opened no device node, took no card lock and sent nothing. Every number comes from committed files.

## Files

| file | what |
|---|---|
| [`REGISTRATION.md`](REGISTRATION.md), [`registration.json`](registration.json) | the registration, committed first (`245caffe`, 00:43:45 PST) |
| [`fit_m9_a2.py`](fit_m9_a2.py) → [`fit-output.txt`](fit-output.txt), [`loso.json`](loso.json), [`rows-m9a2.json`](rows-m9a2.json), [`m9_a2.json`](m9_a2.json) | the registered fit: every arm, fold and score; per-cell rows; the freeze |
| [`predict_m9_a2.py`](predict_m9_a2.py), [`selftest_predict_m9_a2.py`](selftest_predict_m9_a2.py) → [`selftest-predict-m9a2.txt`](selftest-predict-m9a2.txt) | the frozen prediction code and its self-test |
| [`posthoc_q140l.py`](posthoc_q140l.py) → [`posthoc.txt`](posthoc.txt) | post hoc readings P1-P5 |
| [`corrections_q140l.py`](corrections_q140l.py) → [`corrections.txt`](corrections.txt), [`corrections.json`](corrections.json) | corrections after verification, post hoc: C0 (the import path reproduces `loso.json`), C1 (the two die-law compositions), C2 (the offset shares), C4 (the nested selection), C8, C9 |
| [`REGISTRATION-A1.md`](REGISTRATION-A1.md) | the registration's dated amendment A1, written after every fit and score (C5, C7, C1) |

**Rerun** (from the top of the lab repo, with a numpy python, about 10 s each):

- `python3 -B docs/reports/data/2026-11-04-q140l-a2-session-terms/fit_m9_a2.py > docs/reports/data/2026-11-04-q140l-a2-session-terms/fit-output.txt`
- `python3 -B docs/reports/data/2026-11-04-q140l-a2-session-terms/selftest_predict_m9_a2.py > docs/reports/data/2026-11-04-q140l-a2-session-terms/selftest-predict-m9a2.txt`
- `python3 -B docs/reports/data/2026-11-04-q140l-a2-session-terms/posthoc_q140l.py > docs/reports/data/2026-11-04-q140l-a2-session-terms/posthoc.txt`
- `python3 -B docs/reports/data/2026-11-04-q140l-a2-session-terms/corrections_q140l.py > docs/reports/data/2026-11-04-q140l-a2-session-terms/corrections.txt` (about 20 s; it also writes `corrections.json`)

The fit imports, unchanged, `tools/claims-v3/e119/make_predictions_e119.py` (E83's dither) and Q139(s)'s
`fit_clock_voltage.py` (`sf`, `Chain.fit_B`). Its vectorized dither is checked against the imported one first (worst
4.6e-13 MHz).

## Corrections after verification

*Wed 4 Nov 2026, from 01:37 PST to this commit, by the fix pass, after the registered result (`5b98bd5c`) and its verifier's
report. Desk only: no card, no device command, no ssh, Discord, Modal or archive access, and pool 7 never read. Nothing
frozen changed. `m9_a2.json` (sha256 `cc6fbccc…`), `predict_m9_a2.py`, `fit_m9_a2.py`, `loso.json`, `rows-m9a2.json`,
`fit-output.txt` and `posthoc.txt` are byte-identical to `5b98bd5c`, so Q140(m)'s `predict_blind7.py`, which loads this
part, is unaffected. The verifier re-derived every registered number to 1e-12. It found nine minor faults in what this
README and the lane's result say about them, and each was re-checked against the committed files before it was
corrected. The registration keeps its text; [`REGISTRATION-A1.md`](REGISTRATION-A1.md) is its dated amendment, written
after every fit and score.*

*Every new number is printed by [`corrections_q140l.py`](corrections_q140l.py) → [`corrections.txt`](corrections.txt)
([`corrections.json`](corrections.json)). It imports the registered fit's functions, never its `main()`, and first
reproduces `loso.json`'s frozen configuration exactly (C0: worst difference 0.0).*

### C1: the handoff's die law

**What the text said.** The checks: "M9's int8 level is 0.995 W lower, which leaves **0.08 W low**" and "M9's fp32 level
shift (−0.99 W) would leave **1.43-1.49 W**". *Heat*: "M9's level leaves it 0.08 W low ... about +0.0 °C under continuous
work and about +0.5 °C at the kernel duty ... G3's zeros miss becomes about −1.45 W". *For the later lanes*: "Q140(e)
and Q140(q) take the level from `m9_a2.json`: β·δ(t) + k_T·(T − T_ref), and Δcap·Φ((L800 − W)/σ) at the cap."

**The fault.** The formula includes M9's die-start term. The figures apply the zeros-level shift alone, each with the
check's own die law kept. Applying k_T on top of Q139(e)'s in-run law would count the die twice.

**Now.** Both compositions are given with their assumptions, and each later lane registers one die law with its
reference temperature: E161 G1Q −0.08 W (shift alone) or +0.24 W (M9 whole); E159 −1.43 to −1.49 W, or −2.49 / −0.95 /
−0.49 W. The verifier's E161 heat figures (+0.04 / −0.27 °C at continuous work, +0.55 / +0.24 °C at the kernel duty)
used one gain, 0.937 °C per W, for both shares, and left the relation's +0.004 W out of (a). E161's own fixed points give
0.909 °C per W at the kernel duty, so the readings here are +0.03 / −0.27 °C and +0.51 / +0.22 °C. G3 is not without a
die term: it has an effective in-run constant, 0.1 W/°C from each run's own start die. What it lacks is a start-die term
on P0's level.

### C2: "most" of the session offset

**What the text said.** "This is most of the "session offset whose sign flipped" that the critic found." **Now:** about
half, held out (42% of E143's offset and 44% of E160's; the split 7.95 → 4.54 MHz, 43%), and the sign still flips.

### C3: rank 8

The lane's handoff said "rank 8 is answered". The critic's desk rule asks for a resolved margin in every held-out session,
and P5 resolves three of four (E80 −0.35 MHz [−2.53, +0.99] against A0). The rule is not met. This README said "met in 3
of 4" in P5, and now says so in *What this does to predicting power and heat* too.

### C4: selection and score on the same folds

**What the text said.** The pooled figures were called held out, with no caveat. **Now:** the caveat, and the selection
measured. Nested inside each fold (corrections C4), the forward rule gives:

| inner rule | selected, by held-out session (E80, E83, E143, E160) | pooled G (MHz) | Bg (W) | Bp (W) |
|---|---|---:|---:|---:|
| registered (selection on the same folds) | T1+T2+T3+T4 in all four | 5.00 | 0.89 | 0.75 |
| nested, 2 of 3 inner sessions | T1-T4, T1-T4, **T1+T3**, T1-T4 | 5.12 | 0.93 | 0.92 |
| nested, 3 of 3 | T1-T4, **T1+T2**, **T1**, **T1+T2+T3** | 6.90 | 0.89 | 0.88 |

The verifier expected the effect to be small. Measured, it is 0.005-0.04 W on the governed board, 0.12-1.90 MHz on the
clock and 0.14-0.17 W on the pinned board. The bands' rule on the nested errors widens the pinned board's band from 1.26
to 1.48-1.75 W. That is information only: the frozen bands, and every registered verdict, stay. Re-freezing on a post hoc
nested reading would be a refit after the scores were seen, which the registration forbids. E165 tests the frozen part
blind.

### C5: the registration's window (D4)

**What the text said.** "It was written from about 00:15 and committed at 00:43:45". **Now:** read from 00:24 PST,
written 00:42-00:43, committed 00:43:45; [`REGISTRATION-A1.md`](REGISTRATION-A1.md) item 1.

### C6: D1's attempts

D1 left out the run started at 00:49:15 PST, killed at 45 s with nothing printed. It is now listed.

### C7: the self-test's 752 MHz check

**What the text said.** The self-test printed "E160's fp16 anchor: 2 of 3 bursts at 795 MHz or more count: OK", a count of
the data's bursts. **Now:** it recomputes the offset and compares it with the code's (|diff| 0.0) and with the fit's for
all three formats. A predictor that counts the 752 MHz burst fails it (a scratch-only mutation test). Only
`selftest_predict_m9_a2.py` and its output changed.

### C8: "every session and format"

**What the text said.** "in every session and format". **Now:** "in every measured session and format (11 of the 12;
E80's fp32 is filled from its other two)". The 1.35-1.74 W range is set by measured offsets alone.

### C9: the seven slow bursts

**What the text said.** "That is the pattern of the mid-burst idle-status events in E143's and E160's corrections, here in
all four sessions". **Now:** four at 751-758 MHz match E160's idle status, one ran at 721.6 MHz, and E143's two (784.0
and 787.8 MHz) are shallow dips. The verifier's "five at about 750-760 MHz" is four, plus the one at 721.6 MHz.

### Corrected in the lane's result only

These were not in this README; the corrected result carries the new wording.

- The headline's "every session's anchors" (C8).
- Blog point 1's mechanism. It now reads "the board draws 0.40 W more per degree at the start (the die's leakage and the
  room are not separated)".
- Blog point 2's "most" (C2), and point 3's "every session and format" (C8).
- Blog point 5's figures. They are now given with D measured at 600 MHz, and end to end with the 600 MHz model's blind D
  as 3.7-5.1 MHz and 0.66-0.87 W.
- The open issue on the slow bursts (C9).
- `for_integration`'s level formula (C1) and "rank 8 is answered" (C3).
