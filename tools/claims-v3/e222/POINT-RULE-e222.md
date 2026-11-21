# E222's point rule (written and hashed before any forecast it uses was computed)

*Written Fri 20 Nov 2026 (week 47), from about 13:40 PST, round Q236's lane `reg-e222`, at the desk on aifoundry2: no card, no device command, no
simulator run, nothing posted. This file, `desk/point_rule_e222.py` (the code that applies it), `desk/models_e222.py` (the forecasters it calls)
and `desk/neverrun_e222.py` (the scan's reader) are hashed into `desk/point-rule-e222.sha256` with the clock's time before the code is run. The
scan it reads (`desk/scan-e222-reg.json`, made 13:33:14-13:33:31 PST by `desk/neverrun_e222.py` over the lab at GitHub main `2f0ab9cd`) holds no
forecast. No E222 datum exists, and no E220 datum was opened by this lane (E220 BLINDNESS: the scan never opens a folder whose name holds `e220`).*

**Disclosed before the rule:** after the scan and before this rule, the lane (1) read the scan alone (no model called) and listed: E220's 32
lead-family configurations' verdicts on aifoundry3 card 0 (all 32 never ran there, by session records and literally); how many 0x values the
session records on the card name (1,099) and MM1-v3.2's 38 measured masks there; how many product masks of 2, 4 and 8 shires no session record on
the card names (2 shires: 36 of 48 one-row masks, 100 of 112 one-column masks); the counts of never-run NB-1 gemmL tokens by footprint band; and
how many gemmLnc tokens of a small grid never ran with their twins (801 of 896) (`OUT/reg-e222/logs/x01_scanlook.txt`, `x02_masklook.txt`);
(2) ran `desk/xcheck_cands_e222.py`, which re-made each candidate's FROZEN E220 forecasts (E220's 306 rows on aifoundry1 card 1 and aifoundry2
card 0, published in the candidates' land) through this registration's callers: equal bit for bit, 306 of 306 rows each; no forecast at
aifoundry3 card 0 was computed; (3) ran the rule's control flow once with a mock forecaster (deterministic stand-in numbers from each token's
hash, no model called) into a temporary folder, to find crashes before the hash. No threshold below was set from a model output.

## 0. Common to every family

- **The card.** aifoundry3 card 0 at its pinned 600 MHz (read, never set), its board stop **70 W x3** and die stop 70 C (E218's). Every score
  below is called with the card name `aifoundry3 card 0` at f = 600.0 MHz.
- **The kernel.** rgm136, E136's binary unchanged (kernel ELF sha256 `aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0`): its
  gemmL loop and its gemmLnc branch (rgm211's host with rgm136's ELF). Data random (E101's grammar; fp32 `randn.bin`, int8 `full.bin`), seed 1.
- **Never ran (the scan, in E220's form as its dated note 1 amends it).** `desk/neverrun_e222.py`'s `Never` class on aifoundry3 card 0, by
  **session records only**: a point counts as RUN on the card only when MM1-v3.2's measured points hold it there, or a committed data folder naming
  the card or a session's own file in a lane folder naming the card (never a dry pass) names it; desk copies in folders naming no card never count.
  The **token reading** (the shape token never ran on the card) for families T, L3b, G3 and G3t; for Y3 the token reading **and** each mask never
  ran on the card at any shape (no session record on the card names the mask, and no MM1-v3.2 measured point on the card has it: any 0x value a
  file names counts, the conservative side). A shape that ran on the card in any format, data kind or mask is not new. **Family R is exempt by
  its name** (E218's own points, re-run). The literal reading is REPORTED beside every verdict, never deciding.
- **The drop line (the brief's rule).** PP32, the planning peak by MM1-v3.2: its W over idle at its own seconds at 600 MHz, x (1 + 2 eps_G) at a
  gemmLnc point (eps_G = MM1-v3.2's held-out gemmLnc W error, 8.43%), plus MM1-v3.2's rest law for the card at its T0 forecast (24.74 W at
  54.4 C), plus 2 W. **No point qualifies whose PP32 is at or above the 70 W stop less 3 W: 67.0 W.** PP_all (the largest over every model and
  candidate, the same rest and margin) is REPORTED beside.
- **One shape, one slot.** No two points share a shape (MB, NB, KB), except a T pair's or Y3 pair's two masks, a G2 or G3 point and its twin,
  and R's pair and twin. The new families take no shape of R, T or each other.
- **Ties in a ranking** are broken by the sorted string `token|format|mask`.
- **The draw order:** R, T, then L3b (L3b-1, L3b-3, L3b-2), Y3 (q01 to q05), G3 (L2, then NB56).

## 1. Family R: four of E218's own points, re-run as same-card repeats (REPORTED only)

E218's registered points (`tools/claims-v3/e218/points-e218.csv`, sha256 `9971b831...`): **its first Y pair by id (y01a, y01b) and its first G
point by id with its cooperative twin (g01, g01t)**, each kept when it passes the drop line. Ids `ry01a`, `ry01b`, `rg01`, `rg01t`. They give the
day-to-day repeat of a layout pair's difference and of a gemmLnc excess on this card; no rule scores them as blind, and they are exempt from
the never-run rule by family name.

## 2. Family T: E220's lead-family points as aifoundry3 twins of the two E220 cards

E220's families L3 (l01-l08), Y2 (p01a-p05b) and G2 with G2t (n01-n07, n01t-n07t), read from `OUT/reg-e220/POINTS-e220.csv` (sha256
`64a7c99a...`, named in `OUT/reg-e220/POINTS.txt` `058984a0...`; the two E220 arms share these 32 configurations), **never its family X**
(E218's own points). Each is kept when it never ran on aifoundry3 card 0 (the token reading) and passes the drop line; **a Y2 pair keeps both
masks or neither, and a G2 point and its twin are kept or dropped together**. Ids `w` + E220's (`wl01`, `wp01a`, `wn01`, `wn01t`, ...), the
subfamilies T-L3, T-Y2, T-G2, T-G2t. Every T point is a twin of an E220 point on aifoundry1 card 1 and on aifoundry2 card 0: the cross-card
rule's twins. The ones that drop are listed with the reason.

## 3. Family L3b: L3S's family around the L3 edges (MM1-v3.2's walk)

The working set is MM1-v3's footprint at the full chip, d = 2 MB KB + NB KB + 2 MB NB (MB); the edges are MM1-v3.2's own constants x1 (about
37.3 MB) and x2 (about 101.4 MB). Every L3b point is `gemmL<MB>x<NB>x<KB>` fp32 random at the full chip; Delta = ln(T_L3S / T_v32) is the op time
of 'MM1-v3.2 + L3S' over MM1-v3.2's at 600 MHz on the card, each from its frozen code (`desk/models_e222.py`).

- **L3b-1, the first edge and the retention miss's family** (quota 5): NB = 1 (gemmL2x1x7's shape family, at other sizes), MB 1-16, KB 1-48,
  30 <= d <= 48 MB; ranked by |Delta| descending (where L3S and MM1-v3.2 differ most); distinct footprints; at least 2 on each side of x1 (a
  candidate is passed over when taking it would leave too few slots for the other side).
- **L3b-3, the set-overflow band** (quota 3): NB 2-16, MB 1-16, KB 1-48, 32 < d <= 48 MB (just past the L3's 32 MiB, where the 4-way set model
  departs from LRU); ranked by |Delta| descending; distinct footprints, distinct NB.
- **L3b-2, the second edge** (quota 2): MB 2-8, NB 2-8, KB 2-16, |d - x2| <= 15 MB; ranked by |d - x2| ascending (E220's L3-2 form); distinct
  footprints, distinct NB, at least 1 on each side of x2.
- Ids b01-b10 in draw order. Fewer than 8 in all: the family is short (a gap).

## 4. Family Y3: equal-count layout pairs for posimb

- **The masks:** every 2-shire mask that is a product of row groups (shire s >> 2) and column groups (s & 3) - one row group by two column groups,
  or two row groups by one column group (E216's 0x3 and 0x10001 kinds) - **that never ran on aifoundry3 card 0** (the mask reading above).
- **The shape**, per source (E216's y01 `gemmL1x8x8`, y02 `gemmL1x8x12`, y03 `gemmL1x4x16`, y07 `gemmL1x4x24`, y08 `gemmL1x8x24`: E220's Y2
  sources, whose nearest shapes family T now holds): the gemmL token, fp32, random, nearest the source by |log2(MB/MB0)| + |log2(NB/NB0)| +
  |log2(KB/KB0)| over MB 1-4, NB 2-16, KB 2-32, that never ran on the card (token reading) and takes no shape already in E222.
- **The pair at that shape: the two eligible masks (not used by an earlier Y3 pair) at which 'MM1-v3.2 + posimb' separates the pair most**,
  |ln(T_a / T_b) by posimb - ln(T_a / T_b) by MM1-v3.2| largest (posimb's frozen code at that shape and mask; MM1-v3.2 prices equal-count masks
  alike), ties by the sorted string; the first mask (`a`) is the one posimb puts slower. Both masks' PP32 must pass the drop line, else the
  next nearest shape is tried.
- Ids `q0Na` and `q0Nb`. Fewer than 4 complete pairs: the family is short.

## 5. Family G3 (rgm136's gemmLnc at small predicted excess for AF4) and its twins G3t

- **Grid** (E220's G2 grid): `gemmLnc<MB>x<NB>x<KB>`, MB 1-8, NB in {1, 2, 3, 5, 6}, KB in {1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32,
  40, 48}, the full chip, random; fp32 in every regime, int8 only in the L2 regime.
- **Regimes** (E220's, from MM1-v3.2's line map Q = (Q0 + Q1) / 2 at 600 MHz): beyond = 14 (1 - qA[L2]) + 12 (1 - qB[L2]); **L2**: beyond < 2.6
  (L2-resident); **NB56**: NB in {5, 6} and beyond >= 2.6. Other candidates are not drawn.
- **Score:** s = 'MM1-v3.2 + AF4''s term W at MM1-v3.2's op time / its W over idle (AF4's predicted excess share), **ascending** (the smallest
  predicted excess for AF4 first: E216 found MM1-v3.2's F3 over-predicts where the real excess is small, and AF4 claims to fix it).
- **Draw.** Walk L2, then NB56; keep a candidate when both tokens (the gemmLnc point and its cooperative twin `gemmL<MB>x<NB>x<KB>`) never ran on
  the card, its shape is new to E222, its (NB, KB) is new to G3, and both PP32s pass the drop line; quotas **L2 3, NB56 4**; the L2 regime's
  unfilled quota passes to NB56. Fewer than 6 G3 points: the family is short (a gap).
- **G3t**: each G3 point's cooperative twin (rgm136's gemmL loop, the same shape, format and data, the full chip), where every gemmLnc term is
  exactly 0. Ids k01-k07 in draw order, twins k01t-k07t.

## 6. The order and the card time

s01 (the smoke `gemmL2x2x2` fp32, the session gate, E218's); t01 (E218's tie, `gemmL2x4x4` fp32 random, the full chip: a bridge); **pass 1**:
every point not of rgm136's gemmLnc branch once (R's three, T-L3, T-Y2, T-G2t, L3b, Y3, G3t) in `random.Random("E222|A|pass1")`'s shuffle of
their sorted ids; t01; **pass 2**: the L3b, Y3, T-L3, T-Y2 and R-Y points again, in pass 1's order reversed; t01; **the G block, last**: s03 (the
smoke `gemmLnc2x2x2` fp32, E218's: the G block's own gate and stop path), every gemmLnc point (rg01, T-G2, G3) once by PP32 ascending, then the
G3 points again in reverse. **Card time planned:** the runs (ties and point runs) at E218's committed pace on this card (data `b445b0f5`: the
smoke s01, the stop-path test, 107 runs and s03 in 45.2 card-minutes, 25.35 s a run with every overhead). **The target 55 card-minutes; the
rule 70** (no run starts after it), **the cap 80** (the session ends at the cap after the run in progress). **THE THINNING RULE** (the brief's,
stated here before any forecast): while the plan is over 55 card-minutes, family T's pass-2 runs leave one at a time (T-Y2's first, then T-L3's,
the last in pass 2 first); T's points themselves are never thinned by this rule (if the plan were still over, it would be said, not thinned).
The registered subset if cut: the opening smoke, tie 1, pass 1 and tie 2.

## 7. What the rule writes

`desk/candidates-e222.json` (every candidate's features, scores and verdicts), `points-e222.json` (the points as `points_e215.describe` gives
them - the GEMM computed, ops and MACs, the tiles, the host arguments - with the families, the sources, PP32 and PP_all, the order and the plan)
and `points-e222.csv` (one row a point), `desk/l3s-extra-e222.json` (the L3S set-model records it made with L3S's frozen `a_shares`, for shapes
the landed cache lacks) and `desk/posimb-features-e222.json` (the posimb features it made with posimb's frozen `private_shared` and `mesh_lat`).
The forecasts of every point by every model and candidate (MM1-v3.2 the registered baseline; the three candidates; MM1-v3.1, MM1-v3 and MM1-v2
beside; 'MM1-v3.2 + all three' by construction) are made after this rule has run, by `forecast_e222.py` through `desk/models_e222.py` unchanged.
