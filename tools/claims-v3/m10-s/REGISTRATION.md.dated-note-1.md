# Term S's registration, dated note 1: the departures of the run, written after the fit (Fri 6 Nov 2026, about 02:50-03:05 PST)

*A dated note beside [`REGISTRATION.md`](REGISTRATION.md) (committed `dfc005bf` at about 02:31 PST, before any fit output). It
changes no rule, form, threshold, seed or entry condition of the registration. It records where the run departed from it, each
written after the numbers it touches (so each is disclosed, none is a registered change).*

1. **The order of § 9, for the code.** `term_s.py` was committed (`23e23210`) with its self-test before any fit, as § 9 says. Its first
   fit run then stopped on a coding error before writing any output: E173's `score.tiles_scored` is a count, not a list. The fit
   therefore runs as **`term_s_v2.py`, a new file** (`term_s.py` stays as committed): it reads the scored class-S tiles from E173's
   `score.pinned` and `score.governed` lists and from E174's measured tiles less its `left_out`, and stops unless they reproduce the
   committed class-S means (E173 +1.062 W, E174 +0.7126 W; both reproduce). Three more changes in v2 came after its first full output
   (`term-s-reg.json` had been read): the post hoc reading of pool 8 on the law (§ 7, read from `law_m10.py`'s `p8-law.json`); the base's
   heat coefficient read from `m10.json` when a law base file holds none; and E102's source keys written as `primary.prices["<key>"]`
   (the bare form reads like an e-mail address to a text scan). None touches the steps, the F-reg fit, the forms or the entry rule:
   every figure of the first output is unchanged in the committed `term-s-reg.json`, re-run with v2. v2's self-test
   (`selftest-term-s-v2.txt`) is term_s.py's and passes.
2. **`law_m10.py` (§ 6) was run before it was committed**, against § 9's order. Its first two runs stopped on coding errors before any
   output it writes: E157's and E164's wrappers take no `--drop-dips` (they remove A2's dips by default) and record build paths, so the
   committed pass copies are found by name in their data directories; and the float scale's anchor list must be M10's own float anchors
   followed by pool 8's scale anchors (`predict_pool8.scale`'s list; the first version read pool 8's alone and missed E172's committed
   s by 0.0008). The run that stopped there had already printed E171's law reading (P8-M1 −0.0517 W); the fix left it unchanged, as
   E171's anchors give the same median either way. Every check then passed: the route reproduces all 30 committed reductions at Q139(u)'s
   frozen slopes (largest |ΔD| 0 W); the refit reproduces `m10.json`'s and `m9.json`'s prices (largest relative difference 4.5e-12); the
   scoring code reproduces E171's and E172's committed P8-M1, M1f, M1i and A1 figures to 1e-9 W and their float scales exactly. The
   outputs committed are those of the committed code.
3. **The law sets passes aside.** FL3 keeps every other part of each registered reduction, so E78's pass gate (a zeros anchor more than
   0.25 W off its straight line) moves with k: at the law, nine sessions keep fewer or other passes (E86 5→3, E90 3→2, E95 5→4, E121
   4→3, E122 4→3, E137 the same count with 13710 for 13714, E141 4→1, E153 4→3, E163 3→1). One row loses its D (E141's
   `fp16.exp_only`) and is dropped from both models' fits, as § 6 registers. Recorded, not changed.
4. **E3 on the law** reads M10's registered held-out errors on pool 6's and 7's S rows (`rows-m10.json`), with the law-fitted term: a
   leave-one-kind-out refit of M10 on the law was not run. The entry is decided on F-reg (§ 4), so this changes no decision.
5. **E147's footing factor.** § 3.2's rule puts E147's steps at 0.98077 of their list values on F-reg, against the 0.97561 of M10's rows
   (M8's k_list = 0): a 0.5% difference, reported, never refitted, as § 3.2 says.
6. **The 800 MHz carry (§ 5)** is read from the frozen files' own ratios (burst D over the 600 MHz D: 1.871-1.874 on aifoundry2's eight
   class-S tiles; times κ0 0.9463, 1.771-1.773 on card 0's). The frozen part was not called with D + 1 W; linearity at each tile's
   inputs is an assumption, stated.

SPDX-License-Identifier: Apache-2.0
