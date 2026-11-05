# Dated note A1 beside POOL8-REGISTRATION.md (Wed 4 Nov 2026, written about 23:26-23:30 PST; Q142(p)) - one tile is the same bytes in the same format, anchors are never re-runs, int8's three launch points, the scale's rate fallback, an added end-to-end self-test, and the dateline

*POOL8-REGISTRATION.md, `pool8-registration.json` and the two hash lists (`3e97f583`, 23:11:53 PST) stay as committed. This note is
committed before the predictor's commit and before any pool-8 output: no pool-8 prediction, scale or score exists. It changes no
model, price, band, rule, threshold or verdict. Each item says how a sentence of the registration is read where the predictor's code
had to decide something the sentence left open.*

## A1-1. A tile is the same tile only in the same format

**What § 2, § 3 and § 7 say:** committed points are reused for "a pool-8 tile whose bytes equal a pool-6, pool-7 or calibration
tile's (sha256 of the whole file)"; "a pool-8 tile whose bytes equal an anchor of M10's list is that anchor"; "a re-run is a tile
whose bytes equal a pool-6 or pool-7 tile's".

**Read as: equal bytes and the same type** (fp32, fp16 or int8). The bench and the card read the same bytes differently in each
format (`sparsity_host --type`), so the counts, D and the kind differ. Pool 7's three zeros anchors share one file's bytes. The
predictor's first development run of its `plan` mode on pool 7 stopped with "fp16.anchor7_zeros n0=91575: counted twice with
different counts": it had merged fp32's points into fp16's. The predictor keys every one of these rules by (sha256, type), and its
self-test T9 checks that pool 7's fp16 zeros anchor keeps its own points.

## A1-2. Anchors are never in the re-run set

§ 7 builds N1 without anchors and re-runs, and scores the re-runs apart (P8-LG, P8-RR). **A manifest anchor is never a re-run** in
those sets, even when its bytes and type equal an earlier tile's (a zeros anchor always does). It keeps its anchor role (§ 3), and a
random anchor equal to an anchor of M10's list is that anchor, as § 3 says. The re-runs the design asks for are pool 6's and 7's float
tiles under their own labels, which are not anchors.

## A1-3. int8's three launch points

§ 2 says "int8 tiles keep the bench's three standard points". RECOUNT-RULE.md's standard points are the float ones (546 cycles an
op). int8 runs 318 cycles an op, so its three launch points sit elsewhere: **int8's row is the bench's own three-point row, as
`run_kinds.py` writes it and `predict_blind7.py` reads it.** Nothing else changes.

## A1-4. The scale's rate when an anchor's item holds none

§ 3's statistic divides by each anchor's measured rate. Where a session's reduction gives an anchor no rate, **the predictor uses the
nominal rate for that anchor, as `fit_m10.assemble_anchors` did for every row M10 was fitted on**, and lists the anchor under
`anchors_at_nominal_rate` in the scale's output. E163's and E164's reductions give every anchor a rate.

## A1-5. An added end-to-end self-test (T9) and the predictor's own list

Beyond § 1's T1-T8, the predictor's self-test adds **T9**: a pool of pool 7's eight single-high-bit tiles and two int8 tiles, run
through `predict` for aifoundry3, card 1 and card 0, then `scale` and `primary` on E163's and E164's committed reductions, which must
give M10's in-sample predictions (`rows-m10.json`) within 1e-9 W and M10's committed session scales within their 5-decimal rounding,
and `burst` on E170's committed reads, which must give E170's committed primary for M9 field by field, with M10's rise at 0.2415 °C
per board W. It is a check, not a registered rule. T8's "predictor's own list" is the `SHA256SUMS` beside the predictor: the
predictor, its README, this registration's files and the nine pool-7 anchor tiles the self-tests read.

## A1-6. The registration's dateline

It says "written about 22:50-23:12 PST". It was last written at 23:10:31 and committed at 23:11:53 (`3e97f583`): the stated end ran
past the commit, the class of fault the M10 lane's A2-3 and A4 corrected. No other time in it changes.
