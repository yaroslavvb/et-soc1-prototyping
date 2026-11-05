# Dated note on Q140(q)'s README, its C3 (Wed 4 Nov 2026, week 45, Q141(r))

*Written beside [`README.md`](README.md) and not inside it, after Q140's final critic (Q140(f)), whose fault 3 it records. The
README stays as committed. Post hoc wording only: no rule, number, prediction or verdict changes. It concerns item 1 of the kinds
page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) (where a large GEMM falls)
and rank 6 of Q139's final critic (a block-stride term). What it does to predicting power and heat: nothing; it says what E169 can
test about time per op.*

**What the README says.** In its E169 section, after the post hoc step reading: "So the L3's 8 MB index remains a candidate cause
of the collapses' extra time … This reading came after the registered test failed; E169 tests it." And under C3: "the layout's 8 MB
index is a candidate cause that E169 will test." The records carried the same: "E169's six frozen shapes test" the index.

**The fault.** Testing the index needs a rule for E169's step that says, before any data, what step each model predicts and what
reading supports or refutes it. Q140 froze E169's six shapes and their predictions (`predictions-e169.json`) but registered no such
rule, so at Q140 "E169 tests it" was not yet true.

**Now.** The step rule is registered, before any E169 data or claim: **A2 (E169)**,
[`tools/claims-v3/e169/REGISTRATION-A2.md`](../../../../tools/claims-v3/e169/REGISTRATION-A2.md) (`217c94a2`, 09:22:23 PST, Q141(s)),
with its dated note 2 (`5c9a62f1`, 10:44:17). It reads the step T800(P)/T800(N) at P1/N1 and P3/N3 against SM's +37.06% and +30.97%
and ISO's and STRICT's 0.0%, in zones of ±3 points, with a 95% t interval floored at σ0 0.336%, in seven verdicts; a negative step
reads UNRESOLVED, and B7 is kept as registered. So the wording to quote is: **E169 reads the 8 MB index's step by a registered step
rule** (A2 (E169)). The pointer beside [`REGISTRATION.md`](REGISTRATION.md) lists every amendment to Q140(q)'s registration, A2
(E168) included.
