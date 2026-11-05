# Dated amendment A2 beside REGISTRATION.md (Wed 4 Nov 2026, written about 21:15-21:40 PST; Q142(m)) - section 7 binds, and how each of its clauses is read

*REGISTRATION.md (`e9367b66`, 19:33:42 PST) and amendment A1 (`3bcb3fcd`, 19:43:44) stay as committed. So do `fit_m10.py`,
`m10.json` and every other file of `6829c9ba` (20:24:58). This amendment answers the lane's verifier, an adversarial read of
the lane's four commits (about 20:30-21:00 PST). It found that § 7 ("what would show a term is not wanted, beyond failing its
rule") was never evaluated, and that one of its clauses is met for term (d). This file is committed before:*
- *any output of the code that evaluates § 7 (`section7_m10.py`, committed later with its outputs);*
- *pool 8 (no pool 8 and no `blind8` exists at this commit: git log);*
- *any prediction made with M10.*

**What was known when this was written (disclosed).** The verifier's readings were known:
- **(d) is met.** § 7's second (d) clause is met by E144. E144's one large rise, `H_H` (R 15.00 °C), reads +0.015 °C under
  Q138(t)'s chain and −0.547 °C with its fold's leave-one-session-out γ (`docs/reports/data/2026-11-04-q142m-m10/tables-m10.md`
  § (d)).
- **Nothing else is.** Its readings of (a), (b), (c2) and (e) trigger nothing else.

So the reading rules below were written knowing the outcome. Each follows § 7's words as literally as a number allows. § A2-2
says where a word needed a number.

## A2-1. How § 7 binds

REGISTRATION.md registered § 7 with § 6 but did not state what follows when a clause is met. Read here:
- **The rule.** A term that enters by § 6 and meets any clause of its § 7 entry is not wanted. It stays out of M10's primary
  form.
- **Its numbers.** They are kept and reported, and the term is carried as a **reported arm** wherever a primary prediction is
  made, pool 8 first.
- **One way only.** § 7 never brings in a term that failed § 6.
- **Where the result goes.** `m10.json` is never edited. M10's primary entries after § 7 go in a new file, `m10-s7.json`,
  beside `m10.json` in `docs/reports/data/2026-11-04-q142m-m10/`, written by the code that evaluates § 7. It supersedes
  `m10.json`'s `entered` and `heat_chain_gain` as M10's primary, and nothing else. The prices, scales, card term, bands, the
  4.5 s law, card 0's k and κ0 stay as `m10.json` holds them.

**For (d), if § A2-2's reading confirms the verifier's:**
- M10's primary for heat over minutes is **Q138(t)'s chain unscaled** (γ = 0, factor 1).
- `m10.json`'s γ = 0.03199 (factor 1.032) is a reported arm.
- Pool 8's registration names the chain unscaled as its heat-over-minutes primary, with the 1.032 arm beside it.
- A per-card-kind gain, or a session or day level, needs a registration of its own.

## A2-2. Each clause as a reading (the numbers § 7 left out)

Every reading uses M10's committed held-out outputs (`heldout-m10.json`, `rows-m10.json`; § 5's folds). It comes after a re-run
of `fit_m10.py`, unchanged, has shown that they reproduce.

| term | § 7's words | read as | met if |
|---|---|---|---|
| (a) | the sessions' scales agree within their own noise (the spread of s over a card's sessions no larger than the spread the anchors' measurement errors give) | per card, the sample sd of s(σ, φ) over the card's sessions that ran an anchor of φ (all rows; the frozen variant's rule, B+a's beside), against the sd each s would have from its anchors' own errors alone: each anchor's measured D drawn as D + se × N(0, 1), with its se from the session's footing reduction and the model's D̂ held; 2,000 draws, seed 142; pooled over the card's sessions as √(mean of their variances) | on either card, the observed sd is no larger |
| (a) | pool 7's held-out bias does not move toward 0 on both cards | the bias (measured − predicted) of B and of B+a on pool 7's rows, per card, over all 52 kinds and over the priority-1 kinds | \|bias\| does not fall on a card, in either set |
| (a) | a family's scale over-corrects (its bias changes sign on a card and grows in size) | the family's bias, B → B+a, per card: on every row, on pool 7's 52 kinds and on its priority-1 kinds (per-format cells reported) | its sign changes and its size grows, in any of those |
| (b) | the S rows' held-out errors move the wrong way on either card | the S rows' held-out rms per card, B → B+b (B+a → B+a+b reported) | it rises on either card |
| (b) | for most S tiles the three-point count's error (3pt − N) lies within ±e(N) | each of the 13 S tiles' \|3pt − N\| against its e(N) | more than half of the tiles |
| (c1) | the session heat scales agree within the window rise's resolution; or the gain is not resolved | the first as (a)'s, with dT_win and its se from each experiment's own reduction (the heat rows' source), per card; the second by § 6's paired bootstrap, pooled and per card | either part, on either card |
| (c2) | the fitted card-0 coefficients' leave-one-tile-out spread includes 0.14004 | the 39 leave-one-tile-out k | 0.14004 lies in [min, max] |
| (d) | γ's sign differs between the card kinds | the per-card-kind γ on all fitted holds (aifoundry3, aifoundry2), with each fold's range reported | their signs differ |
| (d) | a held-out session's large rises read worse with γ | per session, the rms of its large-rise holds' plateau errors (R ≥ 10 °C, the fitted set) without γ and with its own leave-one-session-out γ, for the variant that entered | it rises in any session |
| (e) | the leave-one-tile-out κ values straddle κ0 within their spread; or the board error is not resolved | each family's leave-one-tile-out κ; § 6's paired-bootstrap interval | κ0 lies in either family's [min, max], or the interval includes 0 |

(c1) and (e) did not enter by § 6, so their readings are reported and change nothing. The re-run also lists every data file
the chain opens, with its sha256.

## A2-3. Corrections to the text (no term, row, rule or threshold changes)

1. **The datelines.**
   - REGISTRATION.md's "about 19:30-20:05 PST": it was written about 19:15-19:33 PST (last written 19:33:32) and committed
     at 19:33:42. That is before the first bench count (19:35:51, the one-point check on the mini) and the first fitter process
     (19:43:56; the first held-out output 19:44:23). 20:05 was the lane's planned end.
   - A1's "about 19:50 PST": it was last written at 19:43:38 and committed at 19:43:44, also before the first fitter process.
   - Precedence holds by git in both. This is the class of fault E163's and E164's D1 datings had.
2. **§ 3a, "in E78, E82 and E94".** `fp32.randn`, `fp16.randn` and `int8.full` are rows of `rows-m9.json` in E78 and E82
   only, not in E94. Nothing changes: in its own fold an anchor of the held-out kind is never read, in any session.
3. **A1-1, "There is no key `M9_frozen_form_loko` and no per-row list of those errors".** nested-m9.json holds that key 197
   times:
   - 109 as aggregates (`families.<family>.same_folds.<cell>`);
   - 88 per row for pool 6's rows (`families.<family>.pool6_rows`: 54 float, 34 int8, rounded to 1e-4 W).

   What it lacks is a per-row list over all 855 rows, so A1-1's two stricter checks stand. The original check is re-run on
   pool 6's 88 rows.
4. **The input list.** The refit's 174-file `SHA256SUMS` does not name every file the frozen chain opens. Two data files are
   missing (`docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json`, `tools/claims-v3/e145/predictions-e145.json`), and
   so are the pools' tile files. The re-run lists every data file it opens with its sha256 now, and the next model's
   registration names them all.
5. **§ 10, compute, for this amendment's runs.** The re-run and the readings go to a lab host if one answers. The lab hosts'
   sign-in checks were pending from 21:13 PST, and the only other remote host has no numpy. If no lab host answers, they run
   on the Intel as local checks of under a minute each on at most two threads, which the round's compute rule allows. The
   readings' note (A3) says which.

## A2-4. What stays

These stay as committed:
- M10 as frozen in `m10.json`;
- every held-out figure, every § 6 entry decision, and every number in the README and the tables;
- M9 and every earlier frozen file.

These hash lists must still pass: the registration's 174, M10's 68, `blind7/SHA256SUMS` (91), `frozen-sha256-e168.json` (9),
`frozen-sha256-e168-scorer.txt` (18) and `predict_q140e.py`'s 26 inputs.
