# Q148(c): M10's constant-lane term - a level per float format for tiles whose lanes each hold a constant word (one word in every lane, or eight lane words), fitted leave one run out on committed rows only, with its uncertainty, the rule by which it enters M10 for a later blind pool, and frozen forecasts for E178's 27 float one-number kinds as a REPORTED arm (registration, written before any fit output and before any E178 datum)

*Fri 6 Nov 2026 (week 45), written about 05:40-06:10 PST on the Intel, desk only (no card, no lab box, no device command, no bench
sweep, no Discord, no Modal), by the lane termc-m10 of Q148, beside Q148(r)'s records round. It answers critic-q145b's `next` rank 5
and its answer for the owner: post hoc, M10 misses by about +0.07 W on tiles whose lanes each hold a constant word, flipping bit or
not, and the old single-bit lists measured each bit only as a step above such a tile, so they cannot see that level. It serves the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6** (a power
model across kinds). The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of
numeric computations as accurately as possible; and of 5 November: "I want to build up on previous things as much as possible before
building new stuff." No new E or Q number: this is Q148's companion term.*

**Written and committed before any output it governs exists:** no level fitted, no forecast computed, and no M10 prediction or
residual computed on any tie row (§ 3.1 (b)). Everything below is fixed now. A departure is a dated amendment file beside this one,
written before the numbers it touches. **No E178 datum exists:** `git log --all` shows no commit under `docs/reports/data/` naming
E178, and E178's first datum is its session's opening config read on the card (E178 dated note A2, A2-4). **E178's registration,
amendments, kit, scorer, rules, forecasts, plan, stops and card-minutes are unchanged by this file:** the term is a REPORTED arm
for E178, scored after E178's data, and never one of E178's rules. Nothing here is written under `tools/claims-v3/e178/`.

**What it is, in one paragraph.** M10 prices the toggles the open-RTL bench counts. Post hoc, on M10's own committed held-out errors,
the float tiles whose lanes each hold one constant word (A one word everywhere, B one word everywhere: `ones`, `neg_ones`, `pi`,
`nz_both`, `dn1_both` and the like) read **+0.069 W above M10** (34 rows; aifoundry3 +0.106, card 1 +0.043; Q145(b)'s
`posthoc-structure.txt`), and the single-B-bit tiles on one base word read +0.098 W (23 rows). The single-bit price lists cannot see
such a level: each list item was measured as a step over its own zero, a tile of the same constant-lane structure, so a level common
to both cancels in the step. **The term is that level:** one value per float format and lane-word class, in J per op, added inside
M10's scaled sum for every float tile that passes the byte test of § 2 as a zero (no flipping bit). E178's 27 float one-number kinds
are all such tiles (one word in every lane), and none of them has been measured, so E178 is the term's first blind test.

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 05:33-05:37 PST: public rows
   H06, H07, H08, H15, H19, H20, H21, H24, H27, L23, P12 and P15 (opaque pointers), and the map's section 3 (the rule for lanes), read
   about 05:38 PST. Q145(b)'s study (round B, after the inventory was written) was read from the lab repo itself.
2. **Used.**
   - **The reading this term tests**, Q145(b)'s class-S study and its fix: the byte test `t_s` of
     `tools/claims-v3/m10-s/term_s.py` (`23e23210`), imported unchanged; `docs/reports/data/2026-11-06-q145b-m10-s/posthoc-structure.json`
     and `.txt` (`6f9ae408`, by `tools/claims-v3/m10-s/posthoc_structure.py`) and that README's section 5; the fix `aab4a5f9` (term S
     stays out; the README's dated note 1). *Check against the same quantity at the same operating point:* before any new output,
     this lane's classing of M10's 959 rows reproduces posthoc-structure.json's five classes, their row counts and biases (zero, one
     word: 34 rows, +0.069 W; zero, eight words: 3, +0.078; single bit, one base word: 23, +0.098; single bit, eight base words: 26,
     -0.036; other: 651), else it stops.
   - **M10 as frozen** (registration `e9367b66`; `6829c9ba` `docs/reports/data/2026-11-04-q142m-m10/`): `m10.json` (the float family
     `G8+c_end+xstage`, B+a+b: `coef_J`, card 1's term 0.9616, `session_scales_training`, `interval_pool_by_format_card`),
     `predict_m10.py` (`d600`), `rows-m10.json` (each row's committed held-out error `err_w["B+a+b"]`, leave one kind out, and
     `M10_insample_pred_w`), and `fit_m10.py`'s `assemble` and `footing_items` (each row's tile path, measured rate and features;
     each session's footing reduction), unchanged. *Check:* `predict_m10.d600` on fp32.pi's committed features reproduces
     `rows-m10.json`'s in-sample prediction of E78's and E82's `fp32.pi` rows to 1e-9 W, before any tie residual.
   - **The tie** (H07, H08, H19, H24): the built-in fp32 pi every kinds session runs first and last in each pass (`anchor_pi`, kind
     `pi_builtin`, E78's protocol, `tools/claims-v3/kinds/e78_common.py` line 30, `cfd94285`): the host's `--values pi` writes
     3.14159274f, word 0x40490FDB, into every element of A and B (`workloads/sparsity/host/main.cpp` line 463, `27dce7f0`), the bytes
     of `tools/claims-v3/kinds/tiles/fp32/pi.bin` (`654ee2ce`), whose every word is 0x40490FDB; E78's reducer checks the tie's
     dumped tile against fp32.pi's sha256 (`reduce_e78.py` line 423, `tie_dump`). Its D, se and measured rate per session from the
     committed reductions on M10's footing: Q139(u)'s `docs/reports/data/2026-11-03-q139u-footing/reduced/<exp>-footing.json`
     (`f47669d1`, H15) for E78-E142; E153 `8e18eb67`, E157 `fb2e5c6e`, E163 `4293d151`, E164 `5eecc457` (their footing
     reductions, `fit_m10.FOOTING`); pool 8's E171 `e171.json` (`91f8ae40`, `--leak 0.20563713796102187 --no-refit --drop-dips`,
     M10's aifoundry3 slope) and E172 `e172.json` (`b3255af1`, `--leak 0.3134106532552718 --no-refit`, M10's card 1 slope), with each
     session's float scale `s_float` from its `scored.json` › `primary.scale` (1.00615 and 1.00798; M10's term a by the frozen
     predictor's rule). The tie is not one of M10's 959 rows; it is the one constant-lane fp32 kind measured in every session.
   - **The committed constant-lane rows among M10's** (H07, H08, H19): E78's and E82's `ones`, `neg_ones` and `pi`; E88's `ones` and
     `c_cancel`; E90's, E92's, E106's, E108's, E122's, E128's and E137's `ones`; E93's and E121's `nz_both` and `dn1_both`; E102's
     `aq` (one word) and `hq`, `hq_e64` (eight lane words); fp32 and fp16 as each ran them.
   - **E178's registration** (H27; `48171930` `tools/claims-v3/e178/`): `forecast-e178.json` (`kinds.<k>.P_w` for aifoundry3 and card
     1 at s = 1 and E171's measured zeros rates, `rate`), `kinds-e178.json` (each tile's sha256) and `tiles/`; section 6's noise
     figures (identical bytes in one session read 0.066 W rms; a 0.041 W session term per kind) for § 7's design arithmetic; dated
     note A1 (`f421c67a`) A1-3, the int8 reading named in Not used; dated note A2 (`c212a345`) A2-4, the first datum. The kit
     (`a4aafc6f`, note 1 `763307e7`): `score_e178.py`'s `scored_forecasts` and `reported` fix the fields § 5 reads (`primary.reported.kinds.<k>`:
     `D_w`, `n`, `P_w` at the session's s and measured rate, `c_kept`). Nothing of E178 is changed or re-run here except its own
     `--check` scripts after the commits (§ 9).
   - **Ditzel's "Esperanto Retrospective"** (P15; Cool Chips Hot Takes, 25 Aug 2026, slide 12, as E178 section 4 and Q145(b)'s
     registration cite it): the silicon's register file is full custom and not in the open RTL (P12: core-et, Erbium branch, `b38a1a3`,
     the RTL the bench simulates). The public reason a constant-lane level can be invisible to the bench (§ 1).
3. **Not used.**
   - **int8** (A1-3's post hoc reading: M10 reads the committed int8 one-number kinds 0.13-0.22 W high, 5 rows): T_S is a float byte
     test; M10's int8 family is another form (`J8+bsat+bpp_r4`, no session scale, no S class); E178's int8 kinds carry E178's own
     int8 rules, which read differences, not a level. Not applicable to this term; noted.
   - **The single-B-bit T_S tiles as fit rows** (the lists' items and pool 6's and 7's case S): their miss also holds the bit's own
     step, which this term does not model (critic-q145b's rank 5 names it the class-S term's other part). Reported post hoc only (§ 8).
     Owed to the class-S registration that combines the level with the bit's step and A's word.
   - **Term S** (`tools/claims-v3/m10-s/`): it stays out by its own rule (`aab4a5f9`). Not stacked here.
   - **M10 on the law** (`m10-law.json`, `6f9ae408`): not frozen for a pool (no band, held-out errors or interval pools; critic-q145b
     fault 3). The term is fitted on M10's registered footing (F-reg) only; a law arm is owed with that freeze.
   - **The recount of the 99 steps' tiles at 27-243 points on the mini:** owed (section 54 of the round's brief), not done here. The
     constant-lane rows keep M10's three-point counts, as E178's P does: their accumulator walks differently at each launch point, and
     the launch-average error that leaves is what E178's F names (F − P from −0.054 to +0.03 W a kind, E178 section 4); σ_C (§ 4)
     carries it. M10's term b recounts case-S tiles only.
   - **E178's F** (the accumulator's launch mean): the term is added to P, E178's primary forecast, only.
   - **E147** (its rows are steps over each item's own zero, and no footing reduction carries its tie) and **E134, E65, E67, E70,
     E79** (price lists outside M10's rows; their zeros are T_S zeros whose D over the zeros anchor no committed M10 row carries).
   - **Pool 8's T_S zeros** (`fp32.anchor7_zeros`, `fp16.anchor7_zeros`): the zero word, D's own reference (§ 2).
   - **800 MHz** (E173-E175): the term is fitted at 600 MHz only and is not carried to the cap here.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code, or a public talk. No NDA-tier check is used, so
   there is no sha256 line, and no NDA-tier piece, name, verdict, ratio, direction or figure is cited.
5. **Readiness:** this block is the registration's own.

## 0. What was read before this was written (disclosed)

- `posthoc-structure.txt` and `.json` (every T_S row with its M10 held-out error; the card split +0.106 / +0.043 W), Q145(b)'s README
  and dated note 1, critic-q145b's answer and `next` list, and this lane's own exploration printing the same rows' classes and errors
  (the same numbers, from `rows-m10.json`).
- A1-3's int8 reading. E178's frozen P for its 27 float kinds (`forecast-e178.json`).
- **Structure only, no residual:** which sessions' footing reductions carry the tie with a D, an n and a rate (30 of M10's 31
  sessions, all but E147, and E171 and E172); that fp32.pi's two committed rows share one set of features and pi.bin's sha256; that
  pool 8's only T_S zeros are its zeros anchors; that E178's 27 float tiles pass T_S as one-word zeros. **No tie D was compared with
  M10, and no level was computed, before this commit.**

## 1. Why a level, and why the lists cannot see it

A one-number float tile feeds the same operand bits every cycle; what the bench counts there is the accumulator's walk and the
return-to-zero buses (E178 section 3), and M10 prices those toggles. A part of the energy that rises with the constant words the
lanes hold, rather than with toggles, is invisible to a toggle count: for example a read whose energy depends on the bits held, the
account E178's dated note A2 (A2-2) sets beside the flips for int8, or anything the silicon's full-custom register file spends that
the open RTL's model does not (§ Builds on, P15). That is a reason to expect a level; it is not a measurement of one. A price list's
item and its zero are both constant-lane tiles, so any such level cancels in the list's step. The term is empirical: which path
carries it is not resolved here.

## 2. The structure the term applies to (a byte test), and what a kind is

- **T_S** (`term_s.t_s`, imported unchanged): a float tile (fp32 or fp16, 2,048 bytes, A then B in make_kinds' layout) whose A holds
  one word everywhere, whose B column j holds one word u_j in all 16 lines and column j + 8 holds u_j XOR m, with m the same for every
  lane. **The term's tiles are T_S's zeros (m = 0)**, every lane holding constant words, in two classes:
  - **one word:** u_0 = ... = u_7, so B is one word everywhere (E178's float kinds, `ones`, `pi`, the tie);
  - **eight words:** otherwise (E102's `hq`, `hq_e64`, the lists' construction).
- **Excluded:** the tile whose A word and B word are both 0 (the zeros anchor, D's reference). A tile with one of the two words 0
  would be a row; none is committed.
- **A kind is a tile's bytes** (the sha256 of its 2,048 bytes): the tie and `fp32.pi` are one kind; `ones` under its several paths is
  one kind if the bytes agree. The code groups by sha256, never by label.
- E178's 27 float tiles (14 fp32, 13 fp16) each pass as one-word zeros, checked by bytes and against `kinds-e178.json`'s sha256 (§ 9).

## 3. The rows and the response

### 3.1 The rows (committed, 600 MHz, M10's registered footing)

- **(a) M10's own rows:** every one of `rows-m10.json`'s 959 rows whose tile is fp32 or fp16 and passes § 2 as a zero (expected from
  the post hoc reading: one word fp32 18, fp16 16; eight words fp32 2, fp16 1). **Response:** e = `err_w["B+a+b"]`, M10's committed
  held-out error (measured − predicted, W; leave one kind out), at the row's session scale, card term and measured rate.
- **(b) The tie:** `anchor_pi` in every session of `rows-m10.json` whose footing reduction (`fit_m10.footing_items`) gives it a D (30
  sessions: E78-E142, E153, E157, E163, E164; not E147), and in E171 and E172. **Response:** e = D − `predict_m10.d600`(f_pi, fp32,
  rate, card, m10, s), with f_pi fp32.pi's committed features (`fit_m10.assemble`, E78's row), rate the tie's measured rate
  (`items.anchor_pi.rate.mean`), s the session's frozen float scale (`m10.json` › `session_scales_training`; E171 and E172:
  `scored.json` › `primary.scale.s_float`), and card 1's term 0.9616. M10 as frozen is in sample for the kind pi (two of its 737 float
  rows); the gap between its in-sample and held-out errors on those two rows is reported beside (the tie's own held-out error would
  differ from its frozen one by about that gap).
- **A run** is one session (experiment and card). **A row's J per op:** ρ = e / (s × c × rate), with s, c and rate as above (for (a),
  the session's frozen scale and the row's measured rate from `fit_m10.assemble`; inside a leave-one-kind-out fold M10 re-read each
  session's scale, which this conversion does not repeat: a fold scale δ away from the frozen one moves ρ by δ × ρ, under 0.001 W at
  δ = 0.01, stated as a limit).

### 3.2 What the code prints about the rows before fitting

The rows per class, format, card and run; the kinds (sha256, labels, runs, rows); the reproduction check of § Builds on 2 (else stop);
the pi in-sample against held-out gap.

## 4. The form, the fit, the held-out errors and the uncertainty

- **The term.** For a float tile of format φ that passes § 2 as a zero of class w (one, eight): **M10-C's D = M10's D + s × c × rate ×
  λ_φ,w**, with s, c and rate as M10 applies them (so the level is carried by the session scale, the card term and the measured rate
  exactly as M10's own prices are). Every other tile: M10 unchanged.
- **The estimator (primary, "K"):** λ_φ,w = **the mean over the class's kinds of each kind's mean ρ** over its rows in the fit, rows (a)
  and (b), both cards pooled. Each kind weighs the same: the tie, one kind measured in 32 sessions, counts once, as a new E178 kind will.
- **Fallback:** a fit with no row of (φ, eight) uses λ_φ,eight = λ_φ,one.
- **Leave one run out:** for each run R that holds a class row, λ is fitted on the other runs' rows (kinds left with no row drop out of
  that fold), and R's rows are predicted: **e' = e − s × c × rate × λ_(−R)**, the term's held-out errors. There is no inner choice.
- **The frozen term:** λ fitted on every row. **Its uncertainty:**
  - (i) **the jackknife over runs:** se_J = √((n − 1)/n × Σ_R (λ_(−R) − mean)²), n the runs holding the format's one-word rows; **the
    95% interval λ ± t(0.975, n − 1) × se_J**, the term's registered interval;
  - (ii) beside, a cluster bootstrap over runs (resample runs with replacement; 2,000 draws, `random.Random(1481)`), percentile 95%;
  - (iii) **σ_C,φ**, the kind-weighted rms of the held-out errors e' over the format's one-word rows (√ of the mean over kinds of
    each kind's mean e'²): one new kind's scatter around M10-C in one session;
  - (iv) the eight-word level has one run (E102): it is reported in sample, is never held out except through the fallback, and
    enters nothing until a second run's eight-word rows exist.
- **Reported arms (frozen beside, never in the entry rule):** **"K-card"**, the same estimator on each card's rows alone (aifoundry3's
  level for aifoundry3, card 1's for card 1), with its own jackknife; **"R"**, the post hoc reading's construction: rows (a) only,
  each row weighing the same (its in-sample value must equal posthoc-structure's +0.069 W over 34 rows when both formats are pooled,
  a check), by format.

## 5. The frozen forecasts for E178's 27 float one-number kinds: a REPORTED arm

- **For each float kind k of format φ and each card** (aifoundry3, card 1; E178 runs on aifoundry3, with card 1 its fallback): **P_k +
  L_φ,card**, P_k E178's registered `P_w[card]` (s = 1, E171's measured zeros rate), **L_φ,card = c × rate_φ × λ_φ,one** (rate_φ
  `forecast-e178.json` › `rate`, c 1 or 0.9616), with the level's 95% interval (§ 4 (i)) and **the kind's 95% predictive interval
  P_k + L ± 1.96 × σ_C,φ**. The two arms' forecasts beside, labelled.
- **Scoring, after E178's data, read from E178's own scorer output** (`scored.json` › `primary.reported.kinds`): for every fp32 and
  fp16 kind with `c_kept` true, a `D_w` and `n` ≥ 2 kept passes, **x_k = D_w − P_w** (E178's `D_minus_P_w`: P at the session's s and
  measured rate) and **x'_k = x_k − f_k × L_φ,card**, f_k = P_w / P_k (the factor E178's scorer applied to P: the session's s times the
  measured over the registered rate). Fewer than 2 kept passes in the session (E178's rule): the arm is NOT SCORED.
- **What it is:** a reported arm for E178, scored after E178's data by `termc.py score` (§ 9), committed before any datum. **It is
  never one of E178's rules:** no E178 verdict, statistic, threshold, plan, stop or card-minute depends on it, and E178's kit runs
  without it.

## 6. The rule by which the term enters M10 for a later blind pool (stated now, read on E178)

- **C1 (both formats pooled):** d = rms(x') − rms(x) over the scored float kinds; its 95% interval by a bootstrap over kinds (2,000
  draws, `random.Random(1782)`, both forms on each draw). **BETTER** if d ≤ −0.010 W and the interval's upper end is below 0; **WORSE** if
  its lower end is above 0; else NOT RESOLVED.
- **C2:** d < 0 on the fp32 kinds and on the fp16 kinds separately.
- **Reported beside, never a verdict:** m_φ, the mean of x over the format's kinds with its t-interval over kinds (the measured
  constant-lane level against M10 at the session's own s), set against L_φ's interval; the arms' d; each kind's x and x'.
- **The term enters** if C1 reads BETTER and C2 holds: the next blind pool's frozen predictor (its own registration, committed before
  its designer draws a tile) computes **M10-C** (this file's frozen λ, unchanged) for every float tile passing § 2 as a zero, with M10
  beside it as an arm, and scores P-C: rms(D − M10-C) against rms(D − M10) on those tiles per 600 MHz card, paired, in P8-M1's form,
  BETTER / WORSE / NOT RESOLVED. **Otherwise** M10 stays as frozen for these tiles and M10-C is a reported arm in that pool.
  A refit of λ on E178's rows by this file's rule is allowed only by a dated amendment committed before that pool's first tile.
- **What would show the term is not wanted:** C1 WORSE; or m_φ's interval holding 0 and excluding L_φ's interval in both formats.
- **Its reach:** E178 is one session on one card. A pass reads that card; the other 600 MHz card is first tested in the next pool. The
  eight-word level, the per-card arm and int8 are not read by the rule.

## 7. The rule's power (design arithmetic, written before any datum)

x_k = L_true,φ + ε_k + c: ε_k ~ N(0, σ_C,φ) per kind, c ~ N(0, σ_com) common to the session's float kinds (a session-wide miss
the session scale leaves), σ_com ∈ {0, 0.02, 0.04} W; L_true ∈ {L, L/2, 0} at aifoundry3's L; 14 fp32 and 13 fp16 kinds; 2,000 draws
a case (`numpy.random.default_rng(1783)`), each with C1's bootstrap at 1,000 draws; reported: the chance C1 reads BETTER with C2, and
WORSE. A figure of design, never a forecast or a verdict.

## 8. What is reported, and how each figure is labelled

- **Held out (leave one run out) on the rows it is fitted on, labelled post hoc** (the reading came from these rows): the rms and bias
  of e and of e' by format, card and class, kind-weighted and row-weighted; per kind; per run.
- **Post hoc, not fit rows:** the single-B-bit T_S rows of M10 (one base word, 23; eight base words, 26) with the level of their class
  and format from the fold without their run added (does the level explain part of class S, "flipping bit or not"?); pool 8's single-bit
  T_S tiles on E171 and E172 (`scored.json` › `primary.rows`, `D_w` − `M10_primary_w`) with the frozen one-word level added at each
  tile's measured rate (`e171.json` / `e172.json` items), against class S's +0.195 / +0.138 W.
- **Frozen, for E178:** § 5's forecasts and § 7's power. **Blind:** nothing here; E178's float kinds are the first blind test.

## 9. The code and the order

1. This file, alone, first.
2. `tools/claims-v3/m10-c/termc.py` (the rows, the checks, the fit, the held-out errors, the uncertainty, the forecasts, the power,
   the post hoc readings, and `score` for § 5-6) with its self-test, committed before its first fit run. The self-test: the classing
   reproduces posthoc-structure.json (§ Builds on 2); `d600` reproduces E78's and E82's `fp32.pi` in-sample predictions to 1e-9 W;
   `d600` on each E178 float kind's `m10_features` at `rate` and s = 1 reproduces its `P_w` for both cards to 1e-9 W; the 27 tiles hash
   as `kinds-e178.json` says and pass § 2 as one-word zeros; pi.bin's 512 words are 0x40490FDB; `score` on two synthetic E178
   sessions (truth P + L: BETTER; truth P: WORSE) reads as it should. No residual is printed by the self-test.
3. `termc.py fit` → the outputs, with a README and a hash list, in `tools/claims-v3/m10-c/`, one commit, before any E178 datum
   (checked by `git log --all` first).
4. After the commits: E178's own `--check` scripts and hash lists re-run, unchanged, to show nothing of E178 moved.

Compute: Python on the Intel through the round's local slot (one job at a time, nice 10, one core); no bench, no card, no lab box. New
files only.

## 10. What this cannot say

- **The reading is post hoc** and these rows produced it: every held-out figure here is held out by run on rows already read, so the
  first blind test is E178's float kinds, and only for the one-word level on one card.
- **Few kinds:** about six fp32 and five fp16 constant-lane kinds; the tie is one kind (pi) in 32 sessions. A level that varies by word
  (pi's against ones') is not resolved by them; σ_C carries it.
- **A level against a price:** a level common to every one-word tile cannot be told here from a missed share of a price these tiles all
  carry (most of a float one-number kind's 8.2 W is M10's live-lane and clock terms, the same for every nonzero kind, E178 section 11).
- **The session scale:** M10 reads each session's float scale from its random anchors; a level here could also be that scale not
  carrying from random tiles to constant-lane ones. Not separated.
- **Mechanism:** § 1 is a public-source reason; which path spends it is not resolved.
- **Footing and clock:** M10's registered footing only, 600 MHz only; no int8.

SPDX-License-Identifier: Apache-2.0
