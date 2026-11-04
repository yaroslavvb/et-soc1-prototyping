# Q140(q) registration: G4 for the large GEMM's sustained path, and a block-stride term from the L3's set mapping

*Written Wed 4 Nov 2026 (week 45), Q140's desk half, on the Intel, before any fit, score or prediction of this lane was
computed. Desk only: no card, no device command, no ssh to a lab box, nothing from the private archive. It answers Q139's
final critic's **rank 5** ("The large GEMM's sustained path: G3 to G4") and **rank 6** ("A large GEMM's time per op on new
shapes"). On the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
that is **item 1** ("Where a large GEMM falls") and, through the power path, **item 6**. The owner's goal, 2 November 2026:
to predict the power requirement and heat generation of numeric computations as accurately as possible.*

*What was read before this was written: the critic's ranks 5 and 6; Q139(q)'s G3 (`2026-11-03-q139q-gemm-g3/`: README,
`g3_model.py`, `e159_g3.py`, `posthoc-g3-inputs.json`'s field list); E159's README and corrections; E158's README and model;
E146's and E136's desk and prediction code; Q140(l)'s README, `m9_a2.json` and `predict_m9_a2.py`; the public RTL's shire
cache defines (`external/core-et`, Apache-2.0), the open firmware's BL2 cache and NoC code and the runtime's allocator
(`external/et-platform`, Apache-2.0), and the public programmer's reference manual (`external/et-man`). No model of this lane
has been run on any row.*

## Part A: G4, a governed large GEMM's sustained clock, board and window die on aifoundry2

**A1. Base.** G3 as frozen in `91def7c4` (`g3_model.py`): P0's levels (E146's `levels0` on the desk's 32 MB split, E136's
`cells.*.P_w`, or the law's arm form for E119/E126), E119's burst-cap dither (66.15 ± 2.75 W), the governor's trip held at
the die (trip on G3's grid), Q138(t)'s frozen aifoundry2 chain, the gaps at OFF_SHARE 0.5, the 0.2 s grid, the 20 s anchor,
the window = in-kernel samples of the last 40 s. Nothing in the chain or the cap changes.

**A2. Candidate terms, in this order** (the brief's list):

- **T_Z, Q140(l)'s zeros level.** Every level gains β·δ_t, β = 0.648275 and δ_t the format's fallback offset from
  `m9_a2.json` (fp32 −1.533980, fp16 −1.506775, int8 −1.535169 W), referred to M9's T_ref 54.3818 °C. No constant is
  fitted. No committed GEMM session ran kinds zeros anchors, so every scored run uses the fallback. (Q140(l)'s T2 carried, so
  M8's level is not the alternative.)
- **T_D, one die law for P0 (the start-die term).** G3's effective in-run constant k_eff·(T − T_start) is replaced by one
  law from a stated reference: every level is P0(f) [+ β·δ_t] + k_D·(T(t) − T_ref), with T(t) the chain's die at the step
  (the run's start die at its first step) and **T_ref = 54.3818 °C** (M9's, the mean burst start behind the relation P0 is
  built on). k_D is chosen on the grid **{0.44, 0.47, 0.50} W/°C** (the in-run leakage the brief names: E159 H1 0.49-0.50,
  Q139(q) C1's unheld runs 0.50, Q138(t)'s idle 0.442). No second slope is used anywhere.
- **T_G, the governor's process-boundary and in-process steps.** When the raised level at 800 MHz, L800(T), is at least P_G,
  each process's kernel time begins with a dip: for d_G × (that process's planned kernel seconds) the clock is **618 MHz**
  (E159 C1's mean dip clock) and the board the raised level there; then G3's loop resumes. The process-boundary dips and the
  mid-process ones are folded into one boundary dip of the same total length (in a 40 s window the two are not separable).
  d_G on **{0, 0.03, 0.06, 0.09, 0.12}**, P_G on **{44, 48, 52, 56} W**. The trip loop still holds the die.
- **T_S, M8's span fraction for other kinds** (structural, not selected). For a kind k other than zeros and the format's
  random (fp32/fp16 randn, int8 full), every arm's energy is S(zeros) + φ_k·(S(top) − S(zeros)) with φ_k = D_M8(k) / D_M8(top),
  M8's frozen D at 600 MHz on aifoundry3's footing: for pool 6's tiles, `predictions-blind6-aifoundry3.json` (blind for M8);
  for a kind in M8's training rows (int8 full, int8 sparse50, fp32 sparse50, the format's randn: E78's aifoundry3 rows in
  `rows-m8.json`), M8's frozen prediction from that row's features and `m8.json` (in sample for M8, said so); for E136's real
  kind, the mean of M8's predictions over E101's real set where M8 has them, else E95's r_real as E136; E136's own law (E107's measured S for sparse50, E95's r_real for real) is the "before". In the
  committed sessions this touches E136's four sustained g4k runs (fp32 real, fp32 sparse50, int8 real, fp16 real), so its
  effect is reported there, not put to the forward rule.

**A3. Rows and folds.** The 56 sustained GEMM-pattern runs of `posthoc-g3-inputs.json` (E119, E126, E136, E146) plus
E159's nine holds rebuilt with E159's own scorer path (`e159_g3.score`'s start, anchor, kernel mask and window, unchanged):
**65 runs, five sessions**. Leave one session out; every constant (G3's k and trip when T_D is off, k_D and trip when it is
on, d_G and P_G) is chosen inside each fold on the other four sessions by G3's loss, Σ (clock/15)² + (W/2)² + (die/1)², per
run. Grids: G3's k {0, 0.1, 0.2, 0.3, 0.442} and trip {65.1, 65.3, 65.5, 65.7, 65.9} °C.

**A4. The forward rule.** Base A0 = G3 nested (its two constants chosen per fold). T_Z, then T_D, then T_G are each added
to the model kept so far; a term **carries** if the held-out loss falls in **at least 3 of the 5 sessions and pooled**, and
is kept if it carries. G4 = G3 + the kept terms + T_S, its constants then chosen on all five sessions and frozen.

**A5. What is scored** (per held-out session and pooled; rms and mean of measured − predicted; count inside 15 MHz / 2 W /
1 °C): the window clock, the window board, the window die. Arms reported beside every step: G3 as frozen (0.1, 65.5; blind
on E159 only), G3 nested, E136's law (as G3's scorer computes it), the chain on the measured trace (heat alone). Paired
bootstrap over runs (10,000 draws) of G3 nested − G4 nested rms. Reported checks, no selection: (i) E158's 42 zeros bursts'
first-second board against P0 + β·δ + k_D·(T_start − T_ref) (the die law out of sample on bursts that never entered P0);
(ii) E159's three zeros holds' window spread (Q140(l) C1); (iii) E136's four other-kind runs with T_S against E136's law.

**A6. The new design for E168** (aifoundry2, its own governor, nothing set; E136's rgm136 binary unchanged). Three shapes
nobody has run, chosen so that their line split is not a stride question (NB odd or a short panel stride, KB ≥ 2):

| shape | arm | M × N × K (fp32) | A / B / C, MB |
|---|---|---|---|
| S1 | `gemmL1x3x3` | 1,024 × 1,536 × 1,536 | 6 / 9 / 6 (21 with C) |
| S2 | `gemmL3x3x2` | 3,072 × 1,536 × 1,024 | 12 / 6 / 18 (36) |
| S3 | `gemmL3x5x3` | 3,072 × 2,560 × 1,536 | 18 / 15 / 30 (63) |

Nine holds, each 12 processes of `--seconds 8` (budget 9.5, tail 6), about 106 s, the last 40 s read:
- fp32 random on S1, S2 and S3, each from a **cold** start (the card at rest, about 46 °C) and then from a **warm** start
  (after that hold, idle until the die reads 55 °C): six holds;
- at S2, from warm starts: **int8 zeros**, **int8 W8A8 real** (`int8.real_smol_w8a8_down`, pool 6's priority-1 W8A8
  down-projection tile, the one of its five W8A8 tiles with the lowest M8 D; `tools/claims-v3/kinds/blind6/`), and **int8
  sparse50** (`tools/claims-v3/kinds/tiles/int8/sparse50.bin`): three holds.

G4's frozen predictions are written for every hold at both nominal starts ("cold": the chain at rest at 46.0 °C; "warm55": as
G3's gate57, to 55 °C), and the registered primary is G4's mechanical prediction from each hold's own measured start (the
E159 scorer's path). If E168 runs kinds zeros anchors first, a second arm recomputes T_Z with the session's own δ_t
(`predict_m9_a2.session_delta`); the fallback stays the primary.

**A7. Rules for E168 (the critic's rank 5).** Per hold, measured − predicted (G4): window clock within **15 MHz**, board within
**2 W**, window die within **1 °C**; each quantity passes on **at least 8 of the 9 holds**. Each other kind's increment over
zeros (int8 W8A8 real and int8 sparse50 at S2, minus int8 zeros at S2, window board) within **15% of its shape's span**, the
span being G4's frozen 800 MHz level difference int8 full − int8 zeros at S2 at the hold's window die. E136's law and G3 (as
frozen) are scored beside it on every hold.

**A8. The 82 W rule.** A design's predicted peak is G3's frozen rule, P0(800) + 8.51 W, with no level term applied (a term must
not loosen a stop validated without it); any hold above 82 W is duty-cycled (the processes shortened until it is not) or
dropped. Stops as E159: board above 85 W on 3 live samples in a row, or a die reading at or above 76 °C.

## Part B: a block-stride term from the L3's set mapping

**B1. The public mapping.** The ET-SoC-1's own register definitions in the open HAL (`et-platform` at `836a4ab`,
`etsoc-hal/include/hwinc/shire_esr.h`, `sc_l3_shire_swizzle_ctl`'s field resets: shire select bits 0-4, bank 5-6, sub-bank
7-8 above the 64 B line) put an L3 line at physical address PA in L3 shire PA[10:6], bank PA[12:11] and sub-bank PA[14:13];
its `sc_idx_cop_sm_physical_index.way` field is 2 bits (**4 ways**). The public RTL (`openhwfoundation/core-et` at `b38a1a3`,
a later revision than the ET-SoC-1's, `rtl/inc/shire_cache_defines.vh` and `rtl/shire/esr/esr_cache_bank.v`; its DV model
`evl_global_attrs.sv` agrees) gives the same split, the set from PA[15] up masked by the L3's set mask, and a tag-state RAM
with a 5-bit LRU field per set (a full order of 4 ways fits in 5 bits). **Assumed, not documented for the ET-SoC-1 itself:
true LRU within a set.** The open BL2 (`bl2_cache_control.c`) gives each of a
shire's 4 × 4 sub-banks the L3's share of 1,024 sets; at 32 MB that is 256 sets, a set mask of 0xFF, so the set is PA[22:15]
and the L3 index repeats every **8 MB**. The only write to the swizzle register anywhere in the open firmware is
`noc_configuration.c`'s NoC reconfiguration for 8 or fewer minion shires (it sets an aliasing bit only), and `NOC_Configure`
calls it with no table, so a 32-shire card keeps the reset default. At tile level (1 KB, 16 lines): a tile's 16 lines land in 16
shires at one bank, sub-bank and set, so a tile's set is its address bits [22:10], **8,192 tile sets of 4 ways**.

**B2. The buffers' relative offsets.** The host (`rgm136/host/main.cpp`) allocates `out` (C), then `a`, then `b` through the
runtime's `mallocDevice`, a first-fit allocator over 4 KB blocks (`esperanto-tools-libs/src/MemoryManager.cpp`). So A starts
C's size after C, and B A's size after A; the common base is irrelevant (set conflicts depend on address differences only).

**B3. The term, SM.** E146's tile-level L3 trace (`reuse_e146.l3_steps`: all 32 shires in lock step, two passes, C's stores
allocating) with the fully associative 32 MB LRU replaced by the 8,192-set, 4-way, true-LRU L3 of B1 at B2's offsets;
everything else as E146 (`split()`: E136's L2 model, two shires averaged, the second pass), priced by E146's frozen MAB prices
(`predictions-e146.json fitted.<t>.ab`) and E119's c1 base, T(f) = C/f + M through 600 and 800 MHz (E158's `model_e158`).
**No constant is fitted.** Registered sensitivity arms (reported, never selected): all three buffers 8 MB aligned (the
offsets E146's model used); and the A operand's lines priced as E158 did (from the L3) with only B's from SM.

**B4. The DRAM side.** The memory controller's address map is public (`etsoc-hal/src/memshire_ddr_init_functions.c`, the
uMCTL2 `ADDRMAP` writes), but the physical-address-to-memshire interleave that feeds it is not in any public source found, so
no DRAM channel or bank term is registered or tested here. Said so in the README.

**B5. What is scored on committed data** (SM is parameter-free, so this is out of sample for SM; MAB's prices are in sample on
E146's L2 and D8 for every arm alike): T800 relative error on E158's 22 fp32 rungs with a far share and its K4 rungs in fp16
and int8, E146's 24 ladder cells (another session) and F6, against STRICT (E146's MAB) and ISO (E158's frozen retention curve).
Registered readings: **(S1)** SM's rms on E146's 24 cells and on E158's 22 rungs against ISO's out-of-sample 10.6% / in-sample
4.6%; **(S2)** the four power-of-two-stride collapses (`K6n4`, `K4n8`, `D4`, `D8`): SM within 3% on each where ISO misses by
8.5-13%; **(S3)** SM's far-B share against E158's measured share per rung.

**B6. E169's six new shapes** (fp32 zeros bursts in E158's harness, T800 from launches at or above 790 MHz):

| | power-of-two panel stride | | not |
|---|---|---|---|
| P1 | `gemmL1x8x5` (NB 8: all five blocks of a panel share sets) | N1 | `gemmL1x7x5` |
| P2 | `gemmL2x8x3` (NB 8, two row blocks) | N2 | `gemmL2x6x3` |
| P3 | `gemmL1x4x8` (NB 4: blocks two apart share sets) | N3 | `gemmL1x5x8` |

**B7. Rules for E169 (the critic's rank 6).** SM's frozen T800 within **3%** on every one of the six shapes (fp32; fp16 and
int8 printed if run); and the stride term **resolved** on each power-of-two shape: |T_SM − T_ISO| / T_ISO ≥ 3% and the
measured T800 closer to SM than to ISO. ISO and STRICT are frozen beside it.

## Freeze, files and order

1. This registration, committed first.
2. The fit: `g4_model.py` (G3 imported unchanged; the terms added), `fit_g4.py` → `fit-g4.txt`, `loso-g4.json` (every step,
   fold, arm and score), `g4.json` (the frozen G4).
3. `predict_e168.py` → `predictions-e168.json` / `.txt` (design, nominal predictions, rules) and its scorer `score_e168.py`.
4. `stride_sm.py` → `stride-sm.json` / `.txt` (committed-data scores, S1-S3), `predictions-e169.json` / `.txt`.
5. README: results first, number by number registered or post hoc, departures dated.

## Device commands sent

None. This lane opens no device.
