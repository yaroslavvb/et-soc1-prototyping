# Dated amendment A1 beside REGISTRATION.md (Wed 4 Nov 2026, about 19:50 PST; Q142(m))

*REGISTRATION.md (`e9367b66`, 19:33:42 PST) stays as committed. This amendment is written and committed before any fit output
exists: `fit_m10.py` has not run on any row, and no self-test, held-out error or candidate term has been computed. It changes no
term, row, entry rule or threshold.*

## A1-1. The self-test's reference (§ 4, last item)

**What § 4 says:** B's machinery on M9's 855 rows must reproduce "`nested-m9.json`'s leave-one-kind-out errors of M9's frozen form
(`M9_frozen_form_loko`) within 1e-6 W on every row".

**What the file holds.** `nested-m9.json` keeps the frozen form's leave-one-kind-out errors only as aggregates
(`families.<family>.plain_loko_by_form.<form>`: the rms over all rows, per format and per card). There is no key
`M9_frozen_form_loko` and no per-row list of those errors (`rows-m9.json`'s `M9_nested_err_w` is the nested procedure's error, not
the frozen form's).

**So the self-test is, instead, two checks, both stricter than the one written:**
1. per row, M10's fitter against the committed fitter itself, `fit_m7.Fam(rows, {form}, "C0_M5_E78E82_family").loko(form)`, run in
   the same process on M9's 855 rows with M9's frozen terms: every row within **1e-9 W**;
2. M10's fitter's rms over each family's rows against `nested-m9.json` › `families.<family>.plain_loko_by_form.<M9's form>.rms_all_w`:
   within **1e-9 W**.

Either failing stops the refit.

## A1-2. M9 as frozen, the rate

M9 as frozen (§ 4, § 8) is computed at **each row's measured rate**, as every training row is and as M9's README departure D1 scored
pool 6. On pool 7's rows this differs slightly from E163's and E164's registered blind figures, which `predict_blind7.py` computed at
each format's nominal rate. Those registered figures are quoted beside, from each run's `scored.json`, unchanged.

## A1-3. The feature chain's checks (§ 3a, § 3b)

Before any fit, the chain `predict_blind7.py` runs is checked on committed counts: on pool 6's three random anchors it must give
Q139(x)'s frozen features (`predictions-blind6-aifoundry3.json`), on pool 7's eight S tiles the frozen features of
`predictions-blind7-aifoundry3.json`, and on each S row's three-point counts that row's committed features; each within 1e-9, else
the refit stops. Each row's D is also compared with its session's footing reduction (the anchors' source), and the largest
difference is reported.
