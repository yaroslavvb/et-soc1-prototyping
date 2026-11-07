# Dated note 1 beside REGISTRATION.md (Sat 7 Nov 2026, Q153(m10acc), the fix pass) - four corrections to this file's words, with their figures in the data README's dated note 1; no number, rule or verdict changes

*Sat 7 Nov 2026 (week 45), written about 12:50-13:00 PST on the Intel, desk only, by Q153's fix pass for the lane m10acc, after an
independent verifier held the lane with fixes (two minor faults and three nits). This file (`b5586759`), its dated amendment A1
(`ceb643ca`) and every committed output stay as committed. Neither M10-ACC nor M10-ACC-L enters M10. The corrections, their figures
and their Builds on block are in
[`../../../docs/reports/data/2026-11-07-q153-m10acc/README.md.dated-note-1.md`](../../../docs/reports/data/2026-11-07-q153-m10acc/README.md.dated-note-1.md)
(sections N1-N5), computed by [`note1_m10acc.py`](note1_m10acc.py) beside this file. Read this file with them.*

- **§ 5 and § 6, the forecast's words and the rule's power.** P9-ACC's form, P8-M1's paired form, has no resolution floor. F-P9
  therefore reads BETTER for floats on card 1 and WORSE for class S on both cards, not NOT RESOLVED (N1). This file stated no power;
  it is stated now (N2):
  - R1-R3 let a float accumulator price in with chance 0.26 at the jackknife interval's upper end (+3.55 fJ), and about 0.6 at +5.7 fJ.
  - R3 makes the floats' rule blind to a Booth price.
  - A later term's registration states its power before any data.
- **§ 9, the launch size.** The frozen term's sensitivity, which § 9 says is stated, is now stated: τ_acc reads +0.1242 / +0.1236 /
  +0.1235 fJ at E67's smallest, median and largest launch (N4).
- **§ 9, the nesting.** Rows (a)'s responses are M10's leave-one-kind-out errors, and M10 is not refitted inside this term's folds.
  So run R's measurements reach τ_(−R)'s training responses through M10's fits. Any leak favours the term, which does not enter anyway
  (N3).
- **Builds on 2 (term S's bullet) and § 1, a citation.** "Term S's dated note 2 § 2" is term S's data note,
  `docs/reports/data/2026-11-06-q145b-m10-s/README.md.dated-note-1.md` § 2 (N5).

SPDX-License-Identifier: Apache-2.0
