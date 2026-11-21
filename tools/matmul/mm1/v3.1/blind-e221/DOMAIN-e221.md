# E221: MM1's domain, case by case

From the declaration's section 0 (DECLARED-blind-e221.md): EVERY E221 case is IN MM1's domain: all 345 arms and the anchor are rgm136's cooperative gemmL<MB>x<NB>x<KB> loop (no gemmLnc, no block, stream or TenB arm); NO case is OUT OF DOMAIN, so none is left unforecast. probe p01: every one of the 733 cases has a form (finite wall and mean cycles, op time; energy FORECAST) in MM1-v3.2 733, MM1-v3.1 733, MM1-v3 733, MM1-v2 733 at the nominal footing (work/step1/domain-probe.json, status only). Every case is in `domain-e221.csv` (class, token, mask, ops a minion a pass, runs, the candidates' scope, and what its class measures).

| arm class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | posimb scope | L3S domain |
|---|---|---|---|---|---|---|---|---|---|---|
| MASK | the core-group masks (family PL: placement of one shape on shire groups, PLA/PLB/PLC/PLD/PLE/PLH/PLK/PLK3/PLL/PLM/PLN/PLX), each with its whole-chip twin | 392 | 402 | 360 / 32 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 360 | 32 |
| CELL1 | the 1x1x1 cells at new masks (families CLK and PLS): gemmL 1x1x1 at shire masks never run before, fp32 and fp16 | 79 | 79 | 76 / 3 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 76 | 3 |
| KB1 | KB = 1: gemmL MBxNBx1 at the whole chip (fp32 random and zeros, fp16 ones and zeros) | 72 | 72 | 0 / 72 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 0 | 72 |
| L2I8 | the int8 L2 point: gemmL 1x1xK int8 (K blocks 1-13) at the whole chip and at masks, with two fp32 zeros pairs | 54 | 54 | 25 / 29 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 25 | 29 |
| MQ3 | the MB = 3 ladders: gemmL 3xNBxKB, the whole chip | 47 | 47 | 0 / 47 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 0 | 47 |
| DK | deep K: gemmL at KB 16-32, the whole chip | 30 | 30 | 0 / 30 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 0 | 30 |
| HLD | the held walks: small gemmL shapes (2x3x3, 2x6x2, 2x7x2, 3x3x2, 3x5x2), the whole chip | 23 | 23 | 0 / 23 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 0 | 23 |
| BW | the BW shapes: gemmL 2x12x4, 5x12x2, 6x5x3 at every kind, the whole chip | 18 | 18 | 0 / 18 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 0 | 18 |
| NB1 | NB = 1: gemmL 2x1x7, 9x1x1, 9x1x2, the whole chip | 15 | 15 | 0 / 15 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 0 | 15 |
| ANCHOR | the anchor (4x8x8 int8 random, whole chip): first, between blocks and last in each session | 3 | 71 | 0 / 3 | yes (probe p01) | yes (probe p01) | yes (probe p01) | yes (probe p01) | 0 | 3 |

- MM1-v0 and MM1-v1 (not declared here, not probed): each has a gemmL form (MM1-v0 maps subsets at the full chip's footprint; MM1-v1 has the masked map).
- NOT APPLICABLE: 'v3.1 + gemmLnc term' (#1.29, F3) and 'MM1-v3.2 + gemmLnc term AF4' (lnc-form): each is 0 off gemmLnc and E221 runs no gemmLnc arm, so each equals its base on every case: declared NOT APPLICABLE, not scored.
- Domain limits, REPORTED apart: IN the domain but beyond the fits, REPORTED apart (they enter the rules like every case): the 1x1x1 cells and core-group masks at shire masks no fit holds (most of E221's 65 masks); aifoundry2 card 0 and aifoundry1 card 0 under their governors (the clock read from each run's start-of-run records; the nominal footing at 800 MHz); configuration twins (section c) split.
- OUT OF DOMAIN: none.
