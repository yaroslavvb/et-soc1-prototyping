# E223: MM1's domain, case by case

From the declaration's section 0 (DECLARED-blind-e223.md): EVERY E223 case is IN MM1's domain: all 299 arms and the anchor are rgm136's cooperative gemmL<MB>x<NB>x<KB> loop (no gemmLnc, no block, stream or TenB arm; arms.json and every schedule checked) at the lab's kinds (zeros, ones, random; fp32, fp16, int8) on the three cards MM1-v3.2 has per-card constants for; NO case is OUT OF DOMAIN, so none is left unforecast. probe p01: every one of the 695 cases has a form (finite wall and mean cycles, op time; energy FORECAST) in MM1-v3.2 695, MM1-v3.1 695, MM1-v3 695, MM1-v2 695 at the nominal footing (work/step1/domain-probe.json, status only); the models' code: mm1_v32.py, mm1_v31.py, mm1_v3.py and MM1-v2 take any gemmL<MB>x<NB>x<KB> token and shire mask on rgm136 (the masked map); the terms' scopes by their own code (posimb_rows / posimb_mask.in_scope: mask not 0xffffffff, kernel rgm136, arm gemmL; L3S's domain_key: the full mask; AF4: gemmLnc tokens only). Every case is in `domain-e223.csv` (class, held-out sets, token, mask, ops a minion a pass, runs, the terms' scopes, and what its class measures).

| arm class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | MM1-v3.3 | posimb, posimb-mask scope | L3S domain |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ANCHOR | the anchor (4x8x8 int8 random, whole chip): first, between blocks and last in each session | 3 | 70 | 0 / 3 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 0 | 3 |
| PLACE | the core-group placements (family 'place'): 11 gemmL shapes (MB 1-4, NB 1-16, KB 1-24; fp32, fp16, int8) placed on shire groups at subset masks of 1 to 28 shires (PL with its subfamilies PL1, P34, G10, G14, FLOOR, ND1/ND2/ND34, D1/D2/D4, CNT/CNT3, TYPE; KW, G111/K111, I8, MIX/COL/ROW, FEED); the proposal's placement law, its held-out placements in the HO sets | 421 | 457 | 421 / 0 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 421 | 0 |
| EDGE | the held-walk edge (EDG, EDG2, EDGR, HO-EDGE): 20 gemmL shapes at MB 2-16, NB 6-10, KB 1-2 (fp32, int8), whole chip | 59 | 59 | 0 / 59 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 0 | 59 |
| L3 | the L3 region (L3R, L3R2, HO-L3, e220-4; the proposal's words): 13 narrow-N gemmL shapes at MB 2-8, NB 1-2, KB 1-6, whole chip | 39 | 39 | 0 / 39 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 0 | 39 |
| WIDE | the wide-B wait (WID, WID2, HO-WIDE): 18 wide-N deep-K gemmL shapes at MB 1-6, NB 9-24, KB 16-32 (fp32), whole chip | 51 | 51 | 0 / 51 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 0 | 51 |
| GATE | the masked energy cases outside PLACE (GATE, GAT, HO-GATE, medium-2, TW, HO-TW): fp32 zeros of 1x12x8 and 2x6x10 at the whole chip and at gate masks of 5, 8 and 16 shires | 30 | 33 | 24 / 6 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 24 | 6 |
| KIND | the kinds (KND, KND2, N3, N4, HO-KIND, CW, v37-18): five gemmL shapes (1x12x8, 1x1x1, 2x1x16, 2x2x3, 2x6x10) at zeros, ones and random, at the whole chip and at 26 shires | 57 | 59 | 39 / 18 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 39 | 18 |
| CELL111 | the 1x1x1 cells outside PLACE (G111, G11, v37-6, HO-111): gemmL 1x1x1 fp32 zeros at single shires | 17 | 17 | 17 / 0 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 17 | 0 |
| SHAPE | the shape probes (SHAPE, SH2, syn): gemmL 1x10x10 and 2x8x8 fp32 zeros at the whole chip and at single shires | 18 | 18 | 12 / 6 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc) | 12 | 6 |

**The held-out sets** (the proposal's 15 HO-<x> families; an arm may sit in two):

| set | cases | runs | classes | subset / full |
|---|---|---|---|---|
| HO-111 | 14 | 14 | {"CELL111": 14} | 14 / 0 |
| HO-Ccard | 3 | 3 | {"PLACE": 3} | 3 / 0 |
| HO-EDGE | 40 | 40 | {"EDGE": 40} | 0 / 40 |
| HO-G | 70 | 70 | {"PLACE": 70} | 70 / 0 |
| HO-GATE | 36 | 36 | {"PLACE": 24, "GATE": 12} | 36 / 0 |
| HO-KIND | 51 | 51 | {"EDGE": 6, "WIDE": 6, "KIND": 39} | 39 / 12 |
| HO-L3 | 21 | 21 | {"L3": 21} | 0 / 21 |
| HO-N | 24 | 24 | {"PLACE": 24} | 24 / 0 |
| HO-P1 | 121 | 145 | {"PLACE": 121} | 121 / 0 |
| HO-P1card | 2 | 2 | {"PLACE": 2} | 2 / 0 |
| HO-P2 | 18 | 18 | {"PLACE": 18} | 18 / 0 |
| HO-P34 | 21 | 21 | {"PLACE": 21} | 21 / 0 |
| HO-S | 48 | 48 | {"PLACE": 36, "SHAPE": 12} | 48 / 0 |
| HO-TW | 12 | 12 | {"GATE": 12} | 12 / 0 |
| HO-WIDE | 41 | 41 | {"WIDE": 41} | 0 / 41 |

- MASKE221: blind-e221's MASK class by its own definition (decl-e221's precedence ANCHOR, L2I8 (family L2I8), CELL1 (families CLK, PLS), then MASK = family PL): E223's arms.json carries no L2I8, CLK or PLS code, so MASKE221 = every non-anchor arm of family PL: 353 cases, 389 runs, all at subset masks (E223's PL arms have no whole-chip member; a whole-chip twin of a PL case is the case of the same card, token, format and kind at 0xffffffff wherever E223 runs one).
- GATESET: the masked energy cases: every arm of family GATE (93 cases), in whichever class (most are PLACE).
- NOT APPLICABLE in effect: AF4 (the gemmLnc energy term) acts at no E223 case (no gemmLnc arm): MM1-v3.3 = 'MM1-v3.2 + AF4' equals MM1-v3.2 on every case (checked to 1e-12 by its frozen per-row form), and so do 'MM1-v3.2 + posimb + AF4' = 'MM1-v3.2 + posimb', 'MM1-v3.2 + AF4 + L3S' = 'MM1-v3.2 + L3S', 'MM1-v3.2 + all three' = 'MM1-v3.2 + posimb + L3S' and 'MM1-v3.2 + AF4 + posimb-mask' = 'MM1-v3.2 + posimb-mask'; each is forecast and printed all the same (by its construction), and the MM1-v3.3 vs MM1-v3.2 sign test reads NO DATA (no untied case) by construction, declared here before any datum.
- Domain limits, REPORTED apart: IN the domain but beyond the fits, REPORTED apart (they enter the rules like every case): the core-group placements at shire masks no fit holds (most of E223's 50 masks), the 26-shire mask, MB up to 16, NB up to 24 and KB up to 32; aifoundry2 card 0 and aifoundry1 card 0 under their governors (the clock read from each run's start-of-run records; the nominal footing at 800 MHz); configuration twins (section c) split.
- OUT OF DOMAIN: none.
