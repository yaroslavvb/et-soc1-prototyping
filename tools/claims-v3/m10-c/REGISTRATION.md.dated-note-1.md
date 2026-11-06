# REGISTRATION.md, dated note 1: the true times, E178's dated note A3, and two readings the code makes plain (Q148(c), before the first fit run)

*Written Fri 6 Nov 2026 (week 45), about 05:31-05:34 PST, on the Intel, desk only. [`REGISTRATION.md`](REGISTRATION.md) (lab `c71fbc7f`,
05:27:58 PST) stays as committed. This note is committed with `termc.py` and its self-test, before the code's first fit run: no level,
forecast or tie residual exists yet. Nothing here changes the term's form, rows, estimator, interval, entry rule, seeds or the arm's
scoring.*

1. **The header's times were written ahead of time.** The registration says "written about 05:40-06:10 PST" and that the inventory
   was read "about 05:33-05:37 PST" and the map's section 3 "about 05:38 PST". The true times: the inventory's rows were read about
   05:20-05:22 PST and the map's section 3 about 05:22 PST; the file was written about 05:22-05:27:40 PST and committed at 05:27:58 PST
   (`c71fbc7f`). The lane's structure-only check (registration § 0) ran at 05:19:48 PST, through the round's local slot.
2. **E178's dated note A3** (`77768027`, 05:17:12 PST, Q146(g)) was committed ten minutes before this registration and was not read
   for it. It adds a REPORTED minion-rail arm and a reader beside E178's scorer, and changes no file of the kit: `score_e178.py` and
   the `scored.json` fields registration § 5 reads (`primary.reported.kinds.<k>`: `D_w`, `n`, `P_w`, `c_kept`) are unchanged. This
   term's arm reads the board's D only. A3's hash list, `SHA256SUMS-e178-a3`, joins the post-commit check of registration § 9 step 4.
3. **The session scale in § 3.1 is M10's own rule, computed exactly.** `m10.json` › `session_scales_training` holds each session's
   float scale to five decimals. The code computes s for each of M10's sessions by `predict_m10.session_scale` over
   `fit_m10.assemble_anchors` (as `predict_m10.py selftest` does), and checks that each value rounds to the stored one; with that s,
   `d600` reproduces E78's and E82's `fp32.pi` in-sample predictions to 1.8e-15 W (self-test [2]). E171 and E172 use their scored
   `s_float`, as registered.
4. **Registration § 8's single-bit reading leaves out E147's rows.** E147's 15 rows among the 26 single-bit rows on eight base words
   are steps over each item's own constant-lane zero (D of 0.38-4.4 W), not D over the zeros anchor, so a level cancels in them. The
   post hoc reading covers the other 11 (E102's 10, E127's `q_chk`) and the 23 on one base word. They are not fit rows either way.
5. **The self-test** (`selftest-termc.txt`, registration § 9 step 2) passes all seven checks: the classing reproduces
   posthoc-structure.json's five classes row for row; `d600` reproduces the `fp32.pi` rows and E178's 54 frozen float P values (27
   kinds, two cards) exactly; the 27 tiles hash as `kinds-e178.json` and pass as one-word zeros; pi.bin is 512 words of 0x40490FDB,
   the host's 3.14159274f; the arm's scorer reads a synthetic P + L session BETTER and a synthetic P session WORSE (with a stand-in
   level of 0.07 W, never the fit's), and one kept pass NOT SCORED; the t quantile matches its tables. It prints no residual.

SPDX-License-Identifier: Apache-2.0
