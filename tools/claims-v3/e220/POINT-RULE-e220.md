# E220's point rule (written and hashed before any forecast it uses was computed)

*Written Fri 20 Nov 2026 (week 47), from about 05:15 PST, Q233's lane `reg-e220`, at the desk on aifoundry2: no card, no device command, no
simulator run, nothing posted. This file, `desk/point_rule_e220.py` (the code that applies it) and `desk/models_e220.py` (the four forecasters it
calls) are hashed into `desk/point-rule-e220.sha256` with the clock's time before the code is run. The scan it reads (`desk/scan-e220-reg.json`, made
05:13:11-05:13:23 PST by `desk/neverrun_e220.py`, E218's scanner form run literally) holds no forecast. No E220 datum exists (no card lane
`card-e220*`, no data folder naming E220).*

**Disclosed before the rule:** after the scan and before this rule, the lane read the scan's verdicts for E218's 52 points and E216's eight Y
pairs on both cards, and listed which gemmL tokens of footprint 30-45 MB at NB = 1, which tokens of footprint 86-116 MB and which gemmLnc tokens
with their twins never ran on either card (reads of the scan alone: no model was called, no forecast computed). It found every E218 point never
ran on either card, every E216 Y configuration read as run on both (copies of E219's and E217's registration scans in lane folders naming no card
name nearly every token the lab knows, and the literal reading counts those for every card), and no L2-resident gemmLnc token never run. The
rule below is written knowing that; no threshold was set from a model output.

## 0. Common to both arms

- **The arms.** **A**: aifoundry1 card 1 at 600 MHz as found (`ET_DEVICES=1`), its board stop 72 W x3 (E215 arm B's). **B**: aifoundry2 card 0
  under its own governor, read never set, the forecast clock **799.0 MHz** (E216's registered route c; 700 and 600 MHz columns beside), its board
  stop 70 W x3 (E216's). Every score below is MM1-v3.2 called with the arm's card name (`aifoundry1 card 1`, `aifoundry2 card 0`) at the arm's clock.
- **The kernel.** rgm136, E136's binary unchanged (kernel ELF sha256 `aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0`): its gemmL
  loop (cooperative loads) and its gemmLnc branch (non-cooperative loads, on rgm211's host with rgm136's ELF). Data random (E101's grammar; fp32 and
  fp16 `randn.bin`, int8 `full.bin`), seed 1.
- **Never ran (the scan, literally, E218's form).** `desk/scan-e220-reg.json` read through `desk/neverrun_e220.py`'s `Never` class: the **token
  reading** (the shape token never ran on the arm's card: no hit counted for that card by E213's folder classes - a folder naming the card, for
  card 1 also a folder naming aifoundry1 without a card, and a folder naming no card - and no MM1-v3.2 measured point of the token there) for the
  new families and for E218's G, Gt and F points; the **config reading** (the shape and mask never ran on the card) for E218's Y points, E218's own
  reading for them. A shape that ran on the card in any format, data kind or mask is not new to the new families (the strictest reading). A G2
  point needs its G2t twin's token never run too.
- **The drop line (the brief's rule).** PP32, the planning peak by MM1-v3.2: its W over idle at its own seconds at the arm's clock, x (1 + 2 eps_G)
  at a gemmLnc point (eps_G = MM1-v3.2's held-out gemmLnc W error, 8.43%, its `decisions_v32.json`), plus MM1-v3.2's rest law for the card at its T0
  forecast, plus 2 W. **No point qualifies whose PP32 is at or above the board stop less 3 W: 69.0 W on arm A, 67.0 W on arm B.** PP_all (the largest
  over the four models, the same rest and margin) is REPORTED beside. Every candidate's energy must be priced by MM1-v3.2.
- **One shape, one slot, per arm.** No two points of an arm share a shape (MB, NB, KB), except E218's G and Gt twins and Y pairs (family X keeps
  them), a G2 point and its twin, and a Y2 pair's two masks. The new families take no shape of family X and none of each other.
- **Ties in a ranking** are broken by the sorted string `token|format|mask`.
- **The draw order per arm:** X, then L3 (L3-1, then L3-2), then Y2 (p01 to p05), then G2 (L2, then NB56).

## 1. Family X: E218's 52 points as cross-card twins

E218's registered points (`tools/claims-v3/e218/points-e218.csv`, sha256 `9971b831...`, its 52 rows of families G, Gt, Y and F; the tie t01 and
the smoke rows are not points), each **kept on an arm when it never ran on that arm's card** by its E218 family's reading (G, Gt, F: token; Y:
config) and passes the drop line. Ids: E218's with an `x` in front (`xg01`, `xg01t`, `xy01b`, `xf04`, ...), the subfamilies XG, XGt, XY, XF. Every X
point is a configuration MM1-v3.2 forecast blind on aifoundry3 card 0 (E218, data `b445b0f5`, scores `0f046200`) and now forecasts on another card:
the cross-card rule's twins. The ones that drop are listed with the reason.

## 2. Family L3: the two L3 edges of MM1-v3.2's retention

- **The edges** are MM1-v3.2's own constants (`out/mm1_v32_params.json` > `time` > `theta`): x1 (the first edge, about 37.3 MB) and x2 (the second,
  where the B stream's surviving share pB ends). The working set is the footprint d = 2 MB KB + NB KB + 2 MB NB MB (MM1-v3's `mm1_core_v3.footprint`
  at the full chip: A 2 MB, B 1 MB, C 2 MB a block). Grid: `gemmL<MB>x<NB>x<KB>`, MB 1-16, NB 1-16, KB 1-48, fp32, random, the full chip.
- **L3-1, the first edge and the retention miss's neighbours** (5 points): NB = 1 (gemmL2x1x7's shape family), 30 <= d <= 45 MB; ranked by |d - 39|
  (gemmL2x1x7's own footprint, 39 MB: the miss E215 and E216 measured 12.7-14.9% slow on two cards) ascending; distinct footprints; at least 2 on each
  side of x1 (a candidate is passed over when taking it would leave too few slots for the other side).
- **L3-2, the second edge** (3 points): MB, NB, KB >= 2, |d - x2| <= 15 MB; ranked by |d - x2| ascending; distinct footprints, distinct NB, at least
  1 on each side of x2.
- Ids l01-l08 (L3-1 by its score, then L3-2 by its score). Fewer than 6 in all: the family is short (a gap).

## 3. Family Y2: E216's layout pairs' masks on new shapes

- **The pairs** (equal shire count, 2 shires each): E216's y01, y02 and y03 (masks 0x3 against 0x10001: measured on aifoundry2 card 0 +0.072,
  +0.068 and +0.040 in ln(wall a / wall b), the contention term's sign backwards) and E216's two control pairs y07, y08 (0x101 against 0x10001,
  measured +0.036 and +0.042 where every frozen layout candidate priced none). Five pairs, ids p01-p05: p01-p03 from y01-y03, p04-p05 from y07-y08.
- **The shape.** Each pair takes the gemmL token, fp32, random, nearest its E216 source shape (y01 `gemmL1x8x8`, y02 `gemmL1x8x12`, y03
  `gemmL1x4x16`, y07 `gemmL1x4x24`, y08 `gemmL1x8x24`) by |log2(MB/MB0)| + |log2(NB/NB0)| + |log2(KB/KB0)| over MB 1-4, NB 2-16, KB 2-32, that never
  ran on the arm's card (token reading), takes no shape already in the arm, and whose two masks' PP32 pass the drop line. The source configuration
  itself qualifies only if its token never ran on the card.
- Ids `p0Na` (the first mask: 0x3 or 0x101) and `p0Nb` (0x10001). Fewer than 4 complete pairs: the family is short.

## 4. Family G2 (rgm136's gemmLnc at small predicted excess) and its twins G2t

- **Grid.** `gemmLnc<MB>x<NB>x<KB>`, MB 1-8, NB in {1, 2, 3, 5, 6}, KB in {1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48}, the full
  chip, random; fp32 in every regime, int8 only in the L2 regime (E216's grid).
- **Regimes** (E218's and E216's, from MM1-v3.2's line map Q = (Q0 + Q1) / 2 at the arm's clock, as the gemmLnc term's maker reads it): beyond =
  14 (1 - qA[L2]) + 12 (1 - qB[L2]); **L2**: beyond < 2.6 (L2-resident); **NB56**: NB in {5, 6} and beyond >= 2.6. Other candidates are not drawn.
- **Score.** s = MM1-v3.2's F3 term W at its own op time / MM1-v3.2's W over idle (the term's predicted share: the predicted excess), **ascending**
  (the smallest predicted excess first: E216 found the term over-predicts where the real excess is small).
- **Draw.** Walk L2, then NB56; keep a candidate when both tokens (the gemmLnc point and its cooperative twin `gemmL<MB>x<NB>x<KB>`) never ran on the
  arm's card, its shape is new to the arm, its (NB, KB) is new to G2 (no two G2 points share NB and KB), and both PP32s pass the drop line; quotas
  **L2 3, NB56 4**; the L2 regime's unfilled quota passes to NB56. Fewer than 6 G2 points: the family is short (a gap).
- **G2t**: each G2 point's cooperative twin (rgm136's gemmL loop, the same shape, format and data, the full chip), where MM1-v3.2's F3 is exactly 0.
  Ids n01-n07 in draw order, twins n01t-n07t.

## 5. The order and the card time (per arm)

s01 (the smoke `gemmL2x2x2` fp32, the session gate); t01 (E218's tie, `gemmL2x4x4` fp32 random, the full chip: a bridge); **pass 1**: every point
not of rgm136's gemmLnc branch once (XGt, XY, XF, L3, Y2, G2t) in `random.Random("E220|<arm>|pass1")`'s shuffle of their sorted ids; t01; **pass 2**:
the L3 and Y2 points again, in pass 1's order reversed; t01; **the G block, last**: s03 (the smoke `gemmLnc2x2x2` fp32: the G block's own gate and
stop path), every gemmLnc point (XG and G2) once by PP32 ascending, then the G2 points again in reverse. Card time planned: the runs (ties and point
runs) at the arm's committed pace (arm A: E215 arm B, 71 runs, 5 smoke processes and the stop-path test in 28.55 card-minutes; arm B: E216, 69 runs
with its opening rest, smoke and stop-path test in 27.55 card-minutes); **the rule 60 card-minutes, the cap 70** (no run starts after the rule; the
session ends at the cap after the run in progress). The registered subset if cut: the opening smoke, tie 1, pass 1 and tie 2.

## 6. What the rule writes

`desk/candidates-e220.json` (every candidate's features, scores and verdicts), `points-e220.json` (both arms' points as `points_e215.describe` gives
them - the GEMM computed, ops and MACs, the tiles, the host arguments - with the families, the sources, PP32 and PP_all, and each arm's order and
plan) and `points-e220.csv` (one row a point and arm). The forecasts of every point by the four models (MM1-v3.2 registered; MM1-v3.1, MM1-v3, MM1-v2
beside) are made after this rule has run, by `forecast_e220.py` through `desk/models_e220.py` unchanged.
