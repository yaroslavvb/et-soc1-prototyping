# E224's point rule (written and hashed before any forecast it uses was computed)

*Written Fri 20 Nov 2026 (week 47), from about 15:20 PST, round Q237's lane `reg-e224`, at the desk on aifoundry2: no card, no device command,
no simulator run, nothing posted. This file, `desk/point_rule_e224.py` (the code that applies it), `desk/models_e224.py` (the forecasters it
calls) and `desk/neverrun_e224.py` (the scan's reader) are hashed into `desk/point-rule-e224.sha256` with the clock's time before the code is
run for real. The scan it reads (`desk/scan-e224-reg.json`, made 15:23:35-15:23:53 PST by `desk/neverrun_e224.py` over the lab at GitHub main
`d5df9568` and the round's lane folders) holds no forecast. No E224 datum exists. E220 AND E222 BLINDNESS: this lane read the round log only as
its copy cut before any E220 or E222 datum; the scan never opens a folder or file whose name holds `e220` or `e222`; no E220 or E222 datum,
score or result line was opened.*

**Disclosed before the rule** (what this lane looked at between the scan and the hash; no threshold below was set from a model output):
(1) `desk/xcheck_cands_e224.py` (15:32:07-15:32:34 PST) re-made each MM1-v3.3 candidate's FROZEN E220 forecasts (E220's 306 rows on these
two cards, published in the candidates' land) through these callers with E217's switch-count inputs merged: bit for bit, 306 of 306 rows each;
the four models within 4.84e-12 relative of E220's own frozen forecasts; the pairs by `compose_sub` equal the single acting term everywhere.
No forecast at an E224 point was computed. (2) A scan-only look (`OUT/reg-e224/logs/x01_scanlook.txt`, no model called): how many full-chip
gemmL shapes of the grid below never ran by session records on each card, per footprint region: L2 (KB <= 2, d < x1) 48 shapes, 16 never run on
card 1, 25 on aifoundry2, 10 on both; L3 (KB >= 3, d < 0.85 x1) 21 shapes, 2 / 2 / 1; the x1 band 48, 14 / 18 / 7; mid 289, 173 / 222 / 153;
the x2 band 248, 176 / 215 / 173; beyond 11,648, nearly all never run; and 492 gemmLnc grid shapes with both tokens never run on both cards.
That look moved family D's L3 region to a fallback (below). (3) The rule's control flow was run twice with a MOCK forecaster (deterministic
stand-in numbers from each configuration's sha256, no model called) into `OUT/reg-e224/work/mock-rule/`, to find crashes before the hash:
the first run filled no P shape and 22 / 19 D slots (the L3-resident and P regions as first written were nearly empty), and the regions below
were widened before this hash; the second run filled every slot. Nothing the mock wrote is registered.

## 0. Common to every family

- **The cards.** Arm A: **aifoundry1 card 1** at its 600 MHz (read, never set), board stop **72 W x3**, die stop 80 C (E220's arm A). Arm B:
  **aifoundry2 card 0** under its own governor, priced at **799.0 MHz** (E220's route c; 700 and 600 MHz columns frozen beside), board stop
  **70 W x3**, die stop 70 C (E220's arm B). Every model is called with the card name as E220's callers name it.
- **The kernel.** rgm136, E136's binary unchanged (kernel ELF sha256 `aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0`): its
  gemmL loop (cooperative loads) and its gemmLnc branch (rgm211's host with rgm136's ELF). Data: random (E101's grammar; fp32 and fp16
  `randn.bin`, int8 `full.bin`), zeros and ones (the lab's tile files), and family P's operand patterns (E212's and E217's tile files). Seed 1.
- **The grid.** `gemmL<MB>x<NB>x<KB>` with MB 1-16, NB 1-16, KB 1-48 (M = 1,024 MB, N = 512 NB, K = KB x 512 / 1,024 / 2,048 in fp32 / fp16
  / int8); the full-chip footprint d = 2 MB KB + NB KB + 2 MB NB (MB; MM1-v3's `footprint`, E220's and E222's); MM1-v3.2's L3 edges x1 = 37.33 MB
  and x2 = 101.44 MB (its frozen constants).
- **Never ran (the scan, in E220's form as its dated note 1 amends it).** `desk/neverrun_e224.py`'s `Never` class, by **session records only**:
  a token counts as RUN on a card only when MM1-v3.2's measured points hold it there, or a committed data folder naming the card or a session's
  own file in a lane folder naming the card (never a dry pass) names it (for aifoundry1 card 1 also a folder naming aifoundry1 but no card: the
  conservative side); desk copies in folders naming no card never count. The **token reading** (the shape token, loop and shape, never ran on
  the card in any format, data kind or mask). Families L and P read it **on both cards**; family D on its own arm's card; a gemmLnc point of
  family L reads both its tokens (the gemmLnc point and its cooperative twin `gemmL<..>`) on both cards. The literal reading is REPORTED beside.
- **The avoid list (the brief: none among E220's, E221's or E222's registered or scheduled points).** Every shape (MB, NB, KB) any token or
  E208-style arm name (`<MB>x<NB>x<KB>-<format>`) in these files names, in any loop: E220's `points-e220.json` (`2451ca9d...`), `plan-e220.json`
  (`6d633187...`), `OUT/reg-e220/POINTS-e220.csv` (`64a7c99a...`) and `OUT/reg-e220/POINTS.txt` (`058984a0...`); E221's registered schedules
  `tools/claims-v3/e221/proposal/src/sched/*.json` (nine sessions, the three not yet committed among them) and `arms.json`; E222's
  `OUT/reg-e222/POINTS.txt` (`fe996c15...`), `OUT/reg-e222/POINTS-e222.csv` (`8b709d4b...`) and its frozen `points-e222.json` (`55d41a4b...`,
  its plan's ties and smoke inside). No E224 point takes an avoided shape, in any loop, format, data kind or mask.
- **Every point passes, in this order:** (1) its shape is not avoided; (2) its shape is not already in E224 on that arm; (3) it never ran (the
  reading above); (4) MM1-v3.2 prices its energy on each arm it is drawn for (not NOT FORECAST); (5) **MM1-v3.2's seconds a GEMM at 600 MHz is at
  most 0.40 s** (E218's R0 lesson: the plain `timeout 10` must never cut off a GEMM's check of C; MM1-v3.2's time has no per-card term, so 600 MHz
  is both arms' slowest column); (6) **the drop line (the brief's rule):** PP32, the planning peak by MM1-v3.2 on the arm (its W over idle at its
  own seconds at the arm's registered clock, x (1 + 2 eps_G) at a gemmLnc point, eps_G = 8.43%, plus MM1-v3.2's rest law for the card at its T0
  forecast, plus 2 W; E220's form), **must be under the arm's board stop less 3 W: 69.0 W on arm A, 67.0 W on arm B**.
- **The draw order:** family L (L3S, posimb, AF4), then family P, then family D per arm. A shape drawn by L or P is used on both arms.
- **A fixed pseudo-random order** where a family draws without a model score: candidates sorted by the sha256 of `E224|<family>|<slot>|<token>|
  <format>|<kind>|<mask>` (no forecast, no measurement), the first that passes taken.
- **Ties in a ranking** are broken by the sorted string `token|format|mask` (or the kind name).

## 1. Family L: the three candidates' leads, never run on either card (the same points on both arms)

**L-L3S (6): the L3 edges for 'MM1-v3.2 + L3S'** (E222's L3b form). Every point `gemmL<MB>x<NB>x<KB>` fp32 random at the full chip; Delta =
ln(T_L3S / T_v32), the op time of 'MM1-v3.2 + L3S' over MM1-v3.2's at 600 MHz on aifoundry1 card 1, each from its frozen code.
- **L3S-1** (quota 3): NB 1 or 2, 0.8 x1 <= d <= 1.3 x1, ranked by |Delta| descending; distinct footprints; at least 1 on each side of x1 (a
  candidate is passed over when taking it would leave too few slots for the other side). Its unfilled quota passes to L3S-2.
- **L3S-2** (quota 3): NB 3-16, 32 < d <= 48 MB (the set-overflow band just past the L3's 32 MiB), ranked by |Delta| descending; distinct
  footprints, distinct NB.
- Ids e01-e06 in draw order.

**L-posimb (3 pairs, 6 points): equal-count layout pairs for 'MM1-v3.2 + posimb'** (E222's Y3 form). Per source (E216's y01 `gemmL1x8x8`,
y02 `gemmL1x8x12`, y03 `gemmL1x4x16`: E216 measured the layout effect there; E220's Y2 and E222's Y3 took their nearest shapes, now avoided):
the gemmL token, fp32, random, nearest the source by |log2(MB/MB0)| + |log2(NB/NB0)| + |log2(KB/KB0)| over MB 1-4, NB 2-16, KB 2-32, that is
not avoided, not used and never ran on either card; at that shape, among the 2-shire product masks (one row group by two column groups or two
row groups by one; shire s at row s >> 2, column s & 3) not used by an earlier pair, **the pair 'MM1-v3.2 + posimb' separates most**,
|ln(T_a / T_b) by posimb - ln(T_a / T_b) by MM1-v3.2| largest (at 600 MHz on card 1), the first of its 40 best pairs whose both masks pass
checks (4)-(6) on both arms; `a` is the mask posimb puts slower. Ids y1a, y1b, y2a, ... Fewer than 2 complete pairs: the family is short.

**L-AF4 (3 points and their 3 twins): gemmLnc at small predicted excess for 'MM1-v3.2 + AF4'** (E222's G3 form). Grid `gemmLnc<MB>x<NB>x<KB>`,
MB 1-8, NB in {1, 2, 3, 5, 6}, KB in {1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48}, the full chip, random; fp32 in every
regime, int8 only in the L2 regime. Regimes from MM1-v3.2's line map Q = (Q0 + Q1) / 2 at 600 MHz on card 1: beyond = 14 (1 - qA[L2]) +
12 (1 - qB[L2]); **L2** beyond < 2.6; **NB56** NB in {5, 6} and beyond >= 2.6. Score s = AF4's term W at MM1-v3.2's op time over its W over idle
(AF4's predicted excess share), **ascending**. Walk L2 then NB56; keep a candidate when both tokens never ran on both cards and are not avoided or
used, its (NB, KB) is new to L-AF4, and both it and its twin pass checks (4)-(6) on both arms; quotas **L2 1, NB56 2** (L2's unfilled quota passes
to NB56). Twins: rgm136's gemmL at the same shape, format and data, the full chip (every gemmLnc term exactly 0 there). Ids g01-g03, twins
g01t-g03t.

## 2. Family P: operand patterns whose switch counts the RTL bench made, each with its zeros and random twins (the same on both arms)

Four shapes (slots p1 fp32, p2 fp32, p3 fp16, p4 int8), each **full-chip gemmL with KB >= 2 and d < 0.85 x2** (E212's fp32 counts are per GEMM
state, S2 at KB >= 2; fp16 and int8 counts are at the harness launch points), drawn in the fixed sha256 order (`E224|P|<slot>|<token>|<format>`):
the first shape whose random point passes checks (1)-(6) on both arms and at which:
- **two operand patterns are drawn**: of the slot's format, from **E212's counted plan tiles** (fp32 bf16trunc, den16, den21, den4, den8,
  fld_mant, fld_sign, fp16grid, lanes2, pow2; fp16 den16_10, den16_4, fld16_exp, fld16_mant, fld16_sign; int8 i8_den1, i8_den3, i8_den6,
  i8_pm1: in MM1-v3.2's own tables, `tools/matmul/mm1/v3.1/counts/`) and from **E217's counted tiles** (fp32 rt16, rt32, rt32b, rt64, sg_kk,
  sgm1, th_top; fp16 h_rt32, h_rt64, h_sg, h_th_in; int8 i8_t06, i8_t1, i8_t2, i8_t3, i8_t46, i8_t5: counts-e217, frozen by decl-e217's
  `COUNTS-FROZEN.txt` before any E217 measurement, merged in memory as decl-e217 merged them; E217's four zero-row tiles gt125, gt25, gt875 and
  h_gt25, whose float gate decl-e217 declared, are never drawn), not drawn by an earlier P slot: **the E212 kind and the E217 kind with the
  largest |ln(W_counts / W_null)|**, W_counts = MM1-v3.2's W over idle with the kind's counts at its own op time, W_null = the mean of MM1-v3.2's
  W over idle at zeros, ones and random at the same configuration (E214's and E217's null N), each at 3 W or more (on card 1 at 600 MHz); if
  the format has no such E217 kind left, the next E212 kind; ties by the kind's name;
- **all four points** (random `r`, zeros `z`, the E212 pattern `a`, the E217 pattern `b`) are priced by MM1-v3.2 on both arms and pass the drop
  line on both arms.
At each P point the compositions that act (any of the three terms) are REPORTED beside (`no_term_acts_REPORTED`), never a condition. Ids
p1r, p1z, p1a, p1b, ... p4b. **Time** (kind-blind in every model) is scored at the random twin only (p<n>r); energy at all four.

## 3. Family D: the domain, per arm (30 slots)

Per arm, each slot takes the first candidate (shape and, for a subset slot, a mask) in the slot's fixed sha256 order (`E224|D|<slot>|<token>|
<format>|<kind>|<mask>`) over its region (then its fallback region, in that order) that passes checks (1)-(6) on that arm (never ran on that
arm's card). The same order on both arms, so the arms share a slot's point wherever it passes on both. The regions (d the full-chip footprint):
**L2** KB <= 2 and d < x1 (MM1's shire-cache regime); **L3** KB >= 3 and d < 0.85 x1 (L3-resident; its fallback: mid); **x1-below** 0.85 x1 <= d <
x1, **x1-above** x1 < d <= 1.15 x1; **mid** KB >= 2 and 1.15 x1 < d < 0.85 x2 (between the edges); **x2-below** 0.85 x2 <= d < x2, **x2-above**
x2 < d <= 1.15 x2; **beyond** d > 1.15 x2 (DRAM-streamed; the seconds cap bounds it); **subset** KB >= 2 and d < 0.85 x2 at a subset product mask
of the slot's shire count; **G-mid / G-L3 / G-L2** the same regions for rgm136's gemmLnc branch.

| region | slots (format, kind) | share |
|---|---|---|
| L2 | d01 fp32 random, d02 fp16 random, d03 int8 random, d04 fp32 ones, d05 int8 zeros | 5 / 30 |
| L3 (fallback mid) | d06 fp32 random, d07 fp16 random | 2 / 30 |
| x1 band | d08 fp32 random below, d09 fp32 random above, d10 fp16 random below, d11 int8 random above | 4 / 30 |
| mid | d12 fp32 random, d13 fp16 random, d14 int8 random, d15 fp32 zeros, d16 fp16 ones, d17 fp32 random | 6 / 30 |
| x2 band | d18 fp32 random below, d19 fp32 random above, d20 fp16 random above, d21 int8 random below | 4 / 30 |
| beyond | d22 fp32 random, d23 fp16 random, d24 int8 ones | 3 / 30 |
| subset masks | d25 1 shire fp32, d26 4 shires fp16, d27 8 shires fp32, d28 16 shires int8 (random) | 4 / 30 |
| gemmLnc | d29 fp32 random (G-mid, fallback G-L3), d30 int8 random (G-L2) | 2 / 30 |

Formats over the 30: fp32 14, fp16 8, int8 8; kinds: random 25, zeros 2, ones 3 (and P's patterns, zeros and random apart). A slot with no
passing candidate is empty and said (a gap).

## 4. The order and the card time, per arm

s01 (the opening smoke, E220's on that card: arm A `gemmL2x2x2` fp32 random; arm B E216's opening smoke, E208's three smoke arms
`1x1x4-fp16-ones`, `1x1x4-fp32-zeros`, `1x1x4-int8-rnd`); t01 (the tie, `gemmL2x4x4` fp32 random at the full chip: E206's and E218's; it ran
on all three cards: a bridge, never in a rule); **pass 1**: every point not of rgm136's gemmLnc branch once, in `random.Random("E224|<arm>|pass1")`'s
shuffle of their sorted ids; t01; **pass 2**: every family L, family P and D-subset point not of the gemmLnc branch again, in pass 1's order
reversed; t01; **the G block, last**: s03 (the G block's smoke, E220's on that card: arm A `gemmLnc2x1x37` fp32, arm B `gemmLnc6x5x10` fp32),
every gemmLnc point once by PP32 ascending, then L-AF4's gemmLnc points again in reverse. **Card time planned:** the runs (ties and point runs)
at E220's pace on each card (arm A 24.13 s a run, from E215 arm B on card 1; arm B 23.96 s, from E216 on aifoundry2 card 0). **The target 50
card-minutes; the rule 65** (no run starts after it); **the cap 75** (the session ends at the cap after the run in progress). **THE THINNING
RULE** (stated before any forecast): while the plan is over 50 card-minutes, pass 2's runs leave one at a time - family P's first, then
D-subset's, then family L's, the last in pass 2 first; no point leaves pass 1 by this rule. The registered subset if cut: the opening smoke, tie 1,
pass 1 and tie 2.

## 5. What the rule writes

`desk/candidates-e224.json` (every candidate walked, with its verdict), `desk/avoid-e224.json` (each avoided shape and the files naming it),
`points-e224.json` (the points per arm as `points_e215.describe` gives them - the GEMM computed, ops and MACs, the tiles, the host arguments -
with the families, the sources, PP32, the order and the plan) and `points-e224.csv` (one row a point and arm), `desk/l3s-extra-e224.json` and
`desk/posimb-features-e224.json` (the L3S set-model records and posimb features the candidates' frozen code made). The forecasts of every point
by every model and composition are made after this rule has run, by `forecast_e224.py` through `desk/models_e224.py` unchanged.
