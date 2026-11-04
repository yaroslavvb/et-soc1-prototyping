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

## The answer

**Three session terms carry, and together they take aifoundry2's held-out burst errors down by a third to a half.**
Each of the four burst sessions was held out in turn and predicted by a fit on the other three: 134 cells, every one with
its D measured on aifoundry3 on Q139(u)'s footing. Pooled over the four sessions:

- **Governed clock: 6.25 → 5.00 MHz rms.** The before is M7 as frozen, which is in sample on E80 and E83; M8 as frozen
  reads 6.60, and M8's form with its cap refitted per fold 7.33.
- **Governed board: 1.62 → 0.89 W rms**, and the bias falls from +1.23 to −0.05 W.
- **Pinned board: 1.52 → 0.75 W rms**, and the bias falls from −1.22 to −0.15 W.

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
  governed clock's session means from −4.52 and +3.43 MHz (M7 as frozen) to −2.62 and +1.91 MHz. **This is most of the
  "session offset whose sign flipped"** that the critic found.
- **The zeros level:** the session's own zeros anchors, referred to a common die start (54.38 °C), sit **1.35-1.74 W
  under the relation's 800 MHz zeros level in every session and format** (M8's level, to within 0.01 W). Raw, they spread 1.11-2.71 W: most of that spread was
  the die. A tile's levels move by **0.648 W per W** of its format's anchor offset (0.62-0.69). With no anchor read, the
  frozen fallback is −1.51 to −1.54 W per format.
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

**The checks the critic named** (reported; no anchors ran in either, so they take the fallback):

- **E161's first hold:** inside G1Q's kernel launches, M8's 800 MHz board is **0.91 W high**. M9's int8 level is 0.995 W
  lower, which leaves **0.08 W low**.
- **E159's zeros GEMMs:** G3 reads them 2.43-2.49 W high. M9's fp32 level shift (−0.99 W) would leave **1.43-1.49 W**:
  the rest is the GEMM's own level, P0. The measured GEMM zeros draw 0.32-0.37 W under M8's kinds zeros level, and about
  0.66 W over M9's.

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
- **End to end, blind D:**
  - E160 governed clock 6.72 (M8) / 5.14 (M7) → 3.68 MHz; governed board 1.39 / 1.11 → 0.66 W; pinned board 1.70 →
    0.80 W.
  - E143 6.64 → 5.12 MHz; 1.60 → 0.86 W; 1.18 → 0.87 W.

**Heat.** A 6 s burst's die rise follows the board through M8's frozen burst law (0.140 °C per W). Post hoc, on the
held-out boards ([`posthoc.txt`](posthoc.txt) P4), it reads **E143 0.548 → 0.467 °C** and **E160 0.562 → 0.438 °C rms**.
For heat over minutes, the critic counted M8's in-work level, 0.91 W high on E161's G1Q, as the larger part of that
hold's −0.90 °C plateau error. M9's level leaves it 0.08 W low. Through E161's committed decomposition (0.85 °C of fixed
point for its 0.91 W), that is about +0.0 °C under continuous work and about +0.5 °C at the kernel duty. That reading is
post hoc and linear; Q140(e) composes it properly. For the large GEMM, Q140(q)'s G4 takes M9's zeros level: G3's zeros
miss becomes about −1.45 W.

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
  - pinned: **15.35 MHz / 1.26 W**. The pinned clock band is wide because of the idle-status bursts, which no model
    predicts.
  - M8's frozen bands were 16.95 MHz / 3.50 W pooled.
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
- **For the later lanes:**
  - Q140(m)'s `predict_blind7.py` imports `predict_m9_a2.burst` for aifoundry2.
  - Q140(e) and Q140(q) take the level from `m9_a2.json`: β·δ(t) + k_T·(T − T_ref), and Δcap·Φ((L800 − W)/σ) at the cap.
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
| 7 | the rule: carries on a quantity if lower in ≥ 3 of 4 and pooled; kept if it carries on one and harms no other by more than 0.15 MHz / 0.03 W | T1, T2, T3 kept clearly; **T4 kept by 0.002 W**, its effect nil |
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
- **D2:** the T4 chain's label string read "without nothing" and was reworded. m9_a2.json's numbers are byte-identical
  (the diff shows the label only).
- **D3: the bands' group.** The registration says "per predicted group". The code uses the final model's own held-out
  predicted clock (below 795 MHz), which is the group the prediction code sees when it is used.
- **D4: the registration's header gives its window as "about 00:10-00:55 PST".** It was written from about 00:15 and
  committed at 00:43:45; the end time was an estimate made before the commit.
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
  relation calls pinned, ran at 721-788 MHz with the board far under the cap (35.8-50.2 W). That is the pattern of the
  mid-burst idle-status events in E143's and E160's corrections, here in all four sessions
  ([`rows-m9a2.json`](rows-m9a2.json)).
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

**Rerun** (from the top of the lab repo, with a numpy python, about 10 s each):

- `python3 -B docs/reports/data/2026-11-04-q140l-a2-session-terms/fit_m9_a2.py > docs/reports/data/2026-11-04-q140l-a2-session-terms/fit-output.txt`
- `python3 -B docs/reports/data/2026-11-04-q140l-a2-session-terms/selftest_predict_m9_a2.py > docs/reports/data/2026-11-04-q140l-a2-session-terms/selftest-predict-m9a2.txt`
- `python3 -B docs/reports/data/2026-11-04-q140l-a2-session-terms/posthoc_q140l.py > docs/reports/data/2026-11-04-q140l-a2-session-terms/posthoc.txt`

The fit imports, unchanged, `tools/claims-v3/e119/make_predictions_e119.py` (E83's dither) and Q139(s)'s
`fit_clock_voltage.py` (`sf`, `Chain.fit_B`). Its vectorized dither is checked against the imported one first (worst
4.6e-13 MHz).
