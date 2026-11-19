# E216's point rule (written and hashed before any forecast it uses was computed)

*Written Thu 19 Nov 2026 (week 47), from about 10:22 PST, Q227's lane `reg-e216`, at the desk on aifoundry2: no card, no device command, no
simulator run. This file and `desk/point_rule_e216.py` (the code that applies it) and `desk/models_e216.py` (the seven forecasters it calls) are
hashed into `desk/point-rule-e216.sha256` with the clock's time before the code is run; the scan it reads (`desk/scan-e216.json`, E213's scanner
at its pin, `desk/neverrun_e216.py`) holds no forecast. No E215 datum is read: the scan leaves every lane folder whose name holds `e215` out of
its view, and the only E215 file read is E215's registered point list (`tools/claims-v3/e215/points-e215.csv`, committed `4cb2c2ad`).*

**Disclosed before the rule:** one exploratory probe (`OUT/reg-e216/scripts/probe1.py`, 10:15 PST) called MM1-v3.1 at 18 configurations on this
card (rgm136 gemmL and gemmLnc, mostly fp32 random, 600 and 799 MHz) to read the scale of W over idle at 799 MHz before the planning line was
set. It chose no point and set no threshold below: the line (64.0 W) is the committed record's (every E212 session on this card was planned at
or under 64.0 W, two of them exactly so; the governor's TDP is 65 W, E209's start-config gate), the regimes are the gemmLnc term's own (its
README), the counts are Q227's brief's.

## 0. Common to every family

- **Card and clock.** aifoundry2 card 0 under its own governor, read never set. **The forecast clock is 799.0 MHz** (E208's win-view median on this
  card, E209's registered forecast clock); every score below is MM1 called at `f = 799.0` with `card = 'aifoundry2 card 0'`.
- **The kernel.** rgm136, E136's binary unchanged (kernel ELF sha256 `aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0`):
  its gemmL loop (cooperative loads) and its gemmLnc branch (non-cooperative loads).
- **Never ran (the token rule).** A point qualifies only if its token (E213's: `gemmL<MB>x<NB>x<KB>` or `gemmLnc<..>`, matched whole) never ran
  on aifoundry2 card 0: no hit COUNTED for that card in `desk/scan-e216.json` (a folder naming aifoundry2 or a2c0, or naming no card) and no
  MM1-v3 or MM1-v3.1 measured point of the token on that card (`neverrun_e216.ran_on_a2` returns nothing). A shape that ran on this card in any
  format, data kind or mask is not new (shape level, the strictest reading). A G point needs its Gt twin's token never run too.
- **One shape, one family slot.** No two E216 points share a shape (MB, NB, KB), except a G point and its Gt twin and the two masks of a Y
  pair, which share it by construction.
- **The planning line.** A point's planning peak PP = the largest W over idle at its own seconds at 799.0 MHz over the six scored forecasters
  (MM1-v3.1, MM1-v3, MM1-v2, 'v3.1 + gemmLnc term', 'v3.1 + contention', 'v3.1 + both terms'), plus the card's rest law at its T0 forecast
  (MM1-v3.1's `rest_law['aifoundry2 card 0']` at 51 C: 23.19 W), plus 2 W. **No point qualifies whose PP is above 64.0 W.** (Above it the
  governor would hold the clock under 800 MHz and the run's energy would read CAPPED.) Every candidate's energy must be forecast by all six.
- **Ties in a ranking** are broken by the sorted string `token|format|mask`.
- **The draw order** is G (with Gt), then Y, then F (a), then F (b): "new to E216" means not among the shapes already drawn.
- **The GEMM computed** by a token at a format: M = 1,024 MB, N = 512 NB, K = KB x the format's K block (fp32 512, fp16 1,024, int8 2,048;
  E209's `points_e209.py`); ops a minion a GEMM = 64 MB NB KB.
- **Ids:** G g01-g10 in its draw order, Gt g01t-g10t (each its G point's twin), Y y01a/y01b ... y08b (the pair's lower mask first; y01-y06 the
  largest-delta pairs in rank order, y07-y08 the controls), F f01-f06 the twins in rank order, f07-f10 the new points (fp16, fp16, int8, fp32).

## 1. Family G (rgm136's gemmLnc branch) and its twins, family Gt

- **Grid.** `gemmLnc<MB>x<NB>x<KB>`, MB 1-8, NB in {1, 2, 3, 5, 6}, KB in {1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48}
  (720 shapes), the full chip (0xffffffff), data random; fp32 in every regime, int8 too in the L2 regime (the term's fit holds int8 only there).
- **Regimes** (the gemmLnc term's own, from MM1-v3.1's line map Q = (Q0 + Q1) / 2 at 799.0 MHz, read as the term's maker reads it):
  beyond = 14 (1 - qA_L2) + 12 (1 - qB_L2), the duplicate reads of beyond-L2 lines a minion-op (the maker's `beyond`); **L2** (L2-resident):
  beyond < 2.6 (under a tenth of the 26 duplicates leave the L2); **NB3**: NB <= 3 and beyond >= 2.6; **NB56**: NB in {5, 6} and beyond >= 2.6.
  A candidate in no regime (NB 1-3 or 5-6 only by the grid) is not drawn.
- **Score.** g = ln(W over idle of 'v3.1 + gemmLnc term' / W over idle of MM1-v3.1), each at its own seconds at 799.0 MHz: where the two differ
  most in W over idle. Descending.
- **Draw.** Walk each regime's ranking; keep a candidate when it passes section 0 (both tokens never ran; the G point's PP, which carries the
  term, and its twin's PP at or under 64.0 W; its shape new to E216), until the regime holds its quota: **NB3 4, NB56 3, L2 3** (10). A regime with
  too few passes its unfilled quota to the next in the order NB3, NB56, L2, then back to NB3. **Fewer than 8 in all: the family is short (a gap).**
- **The 3 W rule.** A G point whose PP with the term comes within 3 W of the board stop (70 W) is dropped; under the 64.0 W line none can be: the
  candidates the line removes above each drawn point are counted and listed.
- **Gt.** Each G point's cooperative twin: the same shape, format and data as `gemmL<MB>x<NB>x<KB>` on rgm136's gemmL loop, the full chip. The
  gemmLnc term is exactly zero there (its `dup` and `first` are 0 on every cooperative loop): shown point by point.
- **Order.** The G block is LAST in the session, ordered by its PP with the term ascending; the Gt points run in pass 1 with the rest.

## 2. Family Y (subset masks in pairs)

- **Grid.** `gemmL<MB>x<NB>x<KB>`, MB in {1, 2, 4}, NB in {2, 4, 8}, KB in {4, 8, 12, 16, 24} (45 shapes), fp32, random; masks in four
  shire counts: n = 2: 0x3, 0x11, 0x101, 0x10001; n = 4: 0xf, 0x33, 0x1111, 0x1010101; n = 8: 0xff, 0xf0f, 0x5555, 0x11111111; n = 16: 0xffff,
  0xff00ff, 0x55555555, 0x33333333. A pair is two masks of one shire count at one shape (six pairs per shape and count).
- **Score.** delta = |ln(T(mask A) / T(mask B))| of 'v3.1 + contention' (T = T_v3.1 (1 + a Phi_fresh), a = -0.08316593007433395, Phi_fresh by
  the masked walk through `features_layout.py` and `eval_layout.phi_of` as frozen) at 799.0 MHz. A pair where MM1-v3.1 itself differs
  (|ln(T_v3.1(A) / T_v3.1(B))| > 0.0005) is not drawn: the family tests pairs MM1-v3.1's n/32 cannot tell apart.
- **Draw.** Only shapes whose token never ran on the card are walked. **Six pairs with the largest delta** (descending), then **two control pairs
  with the smallest delta** (ascending), each passing section 0, at most one pair a shape: 16 points. Fewer than 6 + 2: the family is short.

## 3. Family F (the full chip, rgm136's gemmL loop: both terms exactly zero)

- **(a) Card-transfer twins, up to 6.** From E215's REGISTERED point list (`tools/claims-v3/e215/points-e215.csv` at `4cb2c2ad`; no E215 datum):
  arm A's points of the registered group (families P, C, R), loop `rgm136 gemmL`, mask 0xffffffff. Score |ln(cycles_v3.1 / cycles_v3)| (the
  wall, at 799.0 MHz on this card), descending, ties by E215 id; keep each that passes section 0, up to 6. Labelled `card-transfer twin (E215 a0nn)`
  and reported apart.
- **(b) New, 4.** `gemmL<MB>x<NB>x<KB>`, MB 1-8, NB 1-16, KB in {1, 2, 3, 4, 6, 8, 12, 16} (1,024 shapes), the full chip, random, in fp16, int8 and
  fp32. The same score; quotas **fp16 2, int8 1, fp32 1**, each passing section 0 (its shape new to E216, the twins included).

## 4. What the rule writes

`desk/candidates-e216.json` (every candidate's scores, regime, PP and verdicts, in rank order), `points-e216.json` and `points-e216.csv` (the
46 points: id, family, regime or pair, token, loop, format, data, mask, shires, the GEMM computed, ops a minion a GEMM, the order block), and the
selection's printed table. The forecasts are then frozen by `forecast_e216.py` (the same forecasters, at 799.0, 700 and 600 MHz).
