# Q133(b): blind pool 3 — 25 tiles on the power model's open cases, written before the model was read

Sun 1 Nov 2026 (week 44), Q133(b), desk only. **Answers item 6 of the kinds page's section 11** ("the power
model's open cases": [horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)).
The pool is for **E115**, the card run that scores it.

**Pool frozen 10:52 PST, before its designer had read the fitted model (M4) or any prediction of it.** This
commit carries the pool alone. The model's extension, its freeze and the frozen predictions for these 25 tiles
come in a later commit, so the order is in git's history (§ Order).

## What is in it

25 operand tile pairs, each 2,048 bytes in the host's `--values file:` layout (raw A then raw B, 1,024 bytes
each; `workloads/sparsity/host/main.cpp` `makeTiles`/`fillValues`), packed with `make_kinds.encode` and
described with `make_kinds.tile_stats` (the stream, gate and bus rules of `../README.md` § 1). 14 fp32, 5 fp16,
6 int8. **20 are priority 1 and 5 priority 2**: if E115's window cannot hold all 25, it runs the 20 and says so.
That choice is made here, before any data.

| tile | open case | what it is | gated | bus bits/op | prio | sha256 (first 12) |
|---|---|---|---|---|---|---|
| `fp32.s_pair0` | signs-moving-sums | signs alternate: the sum returns to exactly 0 every two k | 0.0% | 85,780 | 1 | `37d230cac80a` |
| `fp32.s_bridge` | signs-moving-sums | signs alternate: the sum climbs 8 k and walks back down | 0.0% | 82,376 | 1 | `62156c4018d0` |
| `fp32.s_drift12` | signs-moving-sums | signs alternate with a 2^-12 residual: the sum drifts slowly | 0.0% | 83,694 | 1 | `452f35dd1b82` |
| `fp16.s_wpair0` | signs-moving-sums | fp16: the two-term sums cancel in pairs of k-groups | 0.0% | 83,140 | 1 | `1e86d8129e3b` |
| `fp16.s_inword0` | signs-moving-sums | fp16: every two-term update is a1*b1 - a1*b1 = 0 | 0.0% | 83,828 | 1 | `09493b42d121` |
| `fp32.x_logu_s50` | exponents-spread-gate | exponents spread over 2^-30..2^30, half the words zero | 75.0% | 75,270 | 1 | `02937d67584b` |
| `fp32.x_logu_bsteady` | exponents-spread-gate | exponents spread, lanes 0-3 gated steadily | 50.0% | 66,328 | 2 | `079f74971669` |
| `fp16.x_logu_s50` | exponents-spread-gate | fp16: exponents over the whole normal range, half the words zero | 74.1% | 71,838 | 1 | `044fd1f90927` |
| `fp32.g_blanes_steady` | gated-kinds | B gate, 50% of lane-cycles, steady (lanes 0-3 never live) | 50.0% | 55,474 | 1 | `c59a4f777faf` |
| `fp32.g_blanes_alt` | gated-kinds | B gate, 50% of lane-cycles, every lane on and off each cycle | 50.0% | 101,088 | 1 | `02c1a1ace2ac` |
| `fp32.g_arows_alt` | gated-kinds | A gate, 50% of micro-ops, alternating every two cycles | 50.0% | 92,004 | 1 | `e5f8097584c7` |
| `fp16.g_blanes_alt` | gated-kinds | fp16: B gate, every lane on and off each cycle | 50.0% | 97,936 | 2 | `9d8320975130` |
| `int8.g_bpairs_steady` | gated-kinds | int8: B column pairs gated steadily, 50% | 50.0% | 67,258 | 1 | `1a069d7c9563` |
| `int8.g_awords_alt` | gated-kinds | int8: A gate on every other micro-op | 50.0% | 70,824 | 1 | `407d256051d1` |
| `fp32.a_lo8_b_randn` | a-side-busy-partner | A busy in its low 8 mantissa bits only, B random | 0.0% | 65,120 | 1 | `452f1b9e2f08` |
| `fp32.a_lo8_b_pi` | a-side-busy-partner | the same A, B constant pi (a quiet partner) | 0.0% | 8,256 | 1 | `5a8b283feca5` |
| `fp32.a_colconst_b_randn` | a-side-busy-partner | A random in value but constant down each column | 0.0% | 58,114 | 2 | `d6e283259e0d` |
| `fp16.a_mant_b_randn` | a-side-busy-partner | fp16: A busy in its 10 mantissa bits only, B random | 0.0% | 75,998 | 1 | `12ffa4d94a00` |
| `int8.a_low2_b_full` | a-side-busy-partner | int8: A busy in its two low bits only, B random | 0.0% | 19,968 | 1 | `147b37e873c2` |
| `int8.a_colconst_b_full` | a-side-busy-partner | int8: A random in value, constant down each word-column | 0.0% | 8,452 | 2 | `dae83c0579d8` |
| `fp32.m_bpair_eq` | memory-path | B column l+8 = column l: lanes never alternate, lines still random | 0.0% | 30,064 | 1 | `11d727af1022` |
| `fp32.m_blines_eq` | memory-path | all 16 B lines identical: lanes alternate, lines never change | 0.0% | 87,024 | 1 | `6524826da60e` |
| `fp32.z_single` | zero-level | all +0.0 but one A and one B word, which meet once an op | 99.98% | 432 | 1 | `b3f596273d43` |
| `int8.z_diag` | zero-level | int8: one live A word per word-column (15 of 16 micro-ops gated) | 93.8% | 11,856 | 1 | `38db5671e708` |
| `int8.st_f32bytes` | another-stream | int8 run on the raw bytes of a fresh fp32 randn tile | 0.0% | 61,230 | 2 | `fed4d00e9c7b` |

`gated` and `bus bits/op` are `make_kinds.tile_stats`' design-time figures (an accumulate op; int8's bus figure
rests on the reconstructed TIMA stream, `../README.md` § 1.2). The full rule of each tile, its seed, its three
sha256s (whole, A half, B half) and more descriptors are in [`blind3.json`](blind3.json): zero words per side,
the A and B bits that change line to line and half-line to half-line (what a line-wide or half-line-wide memory
path would carry, apart from the compute stream), and for fp32/fp16 the moving sum per C element in units of the
rms product (`s_pair0`, `s_wpair0`, `s_inword0`: the one-op sum is exactly 0 in all 256 elements; `s_bridge`: 215
of 256 in exact arithmetic; `s_drift12`: 0.0006 of a product; random tiles: 2-5).

**How the open cases map to tiles.** The case list is the brief's (Q133 § item 6, after Q132(b), E95, E103):

- *fp32 where signs alternate on moving sums*: three fp32 tiles whose per-op sum is exactly 0, ~0 by rounding, or
  2^-12 of a product (so C stays near one product all launch, or drifts up slowly), and two fp16 tiles that do the
  same across k-groups and inside the two-term update.
- *exponents spread under a gate*: products spread over 2^120 (fp32) or fp16's whole range, with half the words
  zero at random, or one fixed half of the lanes gated.
- *gated kinds*: the same 50% gated fraction three ways in fp32 (B gate steady, B gate switching every cycle, A gate
  switching every two cycles), once in fp16, and twice in int8 (B column pairs steady under both pairings, A every
  other micro-op).
- *the A side with a busy partner*: an A side busy in a few bits only, or busy in value but held down each column,
  against a random B, in all three formats, and one exact quiet-partner twin (`a_lo8_b_pi` has `a_lo8_b_randn`'s A
  half byte for byte).
- *the zero level*: one live lane-cycle an op in fp32, one live A word per column in int8.
- *the memory path's own term*: two fp32 tiles that move B's line-to-line bits and its in-lane alternation apart
  (`m_bpair_eq`: no alternation, random lines; `m_blines_eq`: full alternation, no line changes).
- *another stream*: the raw bytes of a fresh fp32 random tile run as int8 (the same 32-bit words through the other
  unit's stream). *Another clock or voltage* is not a tile and is not done: Q133 sets no clock (CONTEXT § 11).
- *a new card without a scale* is E115's choice of card plus frozen anchor-relative predictions (the later commit);
  *a physical reading of the constants* is desk work in the model's README (the later commit).

## Novelty

No pool tile equals any of the 10,593 `.bin` files in the tree outside `blind3/` (sha256 of the whole file, and
of each 1,024-byte half against both halves of every 2,048-byte file). The only shared half is `a_lo8_b_pi`'s B
half — every element pi — which is the pi tie's A and B half, by design. Nothing here has been measured.

## The independence protocol, and how far it holds

The brief asked for an **independent designer spawned with the Agent tool**, given only the tile format, the kinds
machinery and the open cases. This session had no Agent tool, so the brief's fallback was used: **the same agent
wrote and hashed the pool before reading the model's internals, and recorded the order.**

Read before the pool was written: the workflow brief (its § 11 and the case list above, including "R8 0.947 ±
0.037" and "R9 inconclusive"); the host's tile code; `../README.md` §§ 0-2; `../make_kinds.py`; the constants of
`../e78_common.py` and the item format of `../e103_common.py`; `../e103/e103.json`'s keys, smoke list and one
entry's rule text; and the **file names** of the tiles of E90, E92-E94, E102-E104 and E106.

Not read before the freeze: the model's README and code (`docs/reports/data/2026-11-01-q132-rtl-bench/`,
`rtl-sim/fma_toggle_v2/`), `../E103.md`, `../e103/selection.json`, `../e103/pool-predictions.json`, any
`predictions-*.json`, any data README of E88-E106, and the kinds page.

**The limit, stated plainly.** The lab's commit subjects, read with `git log` before the freeze, name the model's
headline form: a toggle count from the RTL bench priced per net toggle and per clocked bit, the operand bus priced
apart from the core, four constants plus a card scale; and they say that E103's worst miss was a near-cancelling
sum. So the designer knew the model's family, not its per-tile behaviour: no bench count, no prediction, no list
of which tiles it gets right. The open case "a pool written by someone else" is only half met by this pool; a
designer from another session would meet it fully.

## Files

| file | sha256 |
|---|---|
| [`make_blind3.py`](make_blind3.py) — the generator (numpy; `--check` rebuilds and compares) | `e17a2c32310698f5571def8ddc68d0547b4e90e6a977cb57ccce280a7af34956` |
| [`blind3.json`](blind3.json) — the pool in `e103.json`'s shape (`tiles`, `smoke`), plus `open_case` and `priority` | `60dfbf12a10fc3f464eb1225261954b466a6209d746fa91d1c9218b146786f88` |
| [`SHA256SUMS`](SHA256SUMS) — one line per tile | `d100a9c7bd4d3fa5d4516377b8962da79cc54ad13a78bac4fa2efc67a654d1db` |
| `tiles/<type>/<kind>.bin` — the 25 tiles | per tile in `SHA256SUMS` |

Reproduce: `python3 tools/claims-v3/kinds/blind3/make_blind3.py --check` (a python with numpy; prints
`"problems": []`).

## Order (PST, Sun 1 Nov 2026)

1. 10:40 brief read; 10:42 `git log` subjects; 10:44 no Agent tool, so the fallback.
2. 10:45-10:49 the machinery listed above.
3. 10:51 pool generated and hashed (`blind3.json` `60dfbf12…`); 10:52 novelty checked; this README written.
4. This commit: the pool alone, before any of the model's files were opened.
   *(Dated note, Sun 1 Nov 2026, after verification: `64b4124e` reworded this item in place to "10:53:35 the pool alone
   committed and pushed (`a9167033`), before any of the model's files were opened". The original wording is restored above;
   "this commit" is `a9167033`, pushed 10:53:35 PST.)*
5. 12:01:48 M5 fitted and frozen; 12:04 these predictions frozen from it and from M4; committed before E115's claim.
6. After verification: the amendment at the end of this file and the contrasts' intervals (`contrasts-blind3.json`),
   committed before E115's claim, with no pool file, count or prediction changed.

## The frozen predictions (added 12:04 PST, after the pool's commit `a9167033` and before any card ran a tile)

[`predictions-blind3.json`](predictions-blind3.json) (sha256 `5f28091a2878d5167aa4402286a1419cca2b78ebe4fbc0b3f34bda35a31f925a`) and its table [`predictions-blind3.md`](predictions-blind3.md), written by
[`predict_blind3.py`](../../../../docs/reports/data/2026-11-01-q133b-power-model/predict_blind3.py) from the bench's counts of these 25 tiles
([`counts-blind3.json`](counts-blind3.json), sha256 `428d0a3815ae66e7be84312e21a8763f276f2a1e8483dd5b17b27e823595684b`; every tile's accumulators match software at all three launch points
except `fp16.s_wpair0`, where 5 of 256 words differ at each point: fp16's window-model residue on near-cancelling sums, which `run_kinds.py` names; its count stands with that flag). Two models, both frozen before E115: **M5** ([`m5.json`](../../../../docs/reports/data/2026-11-01-q133b-power-model/m5.json), sha256
`c19f2c7bc098b5a8969694b6563784d57bf88e7336fe97ac2afe769b0c63e2da`), the form chosen by nested leave-one-kind-out over thirteen experiments, and **M4** as frozen for E103 (`b995463e`;
its constants checked by refitting it on E78 alone, max relative difference float 3.1e-15, int8 3.8e-16). D is W over the type's own zeros at
600 MHz, on three footings: `a3` (aifoundry3 card 0, no scale), `c1` (aifoundry1 card 1, times its scale) and `new` (a card with
no scale: the a3 figure, its interval widened by one card's step), and as a ratio to the same model's prediction for the type's
random anchor, so a session on any card can scale them by its own anchor.

| tile | open case | prio | **M5, a3 [95%]** | M5, c1 [95%] | M5, new card [95%] | M4, a3 [95%] | M4, c1 | M5 ÷ anchor |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `fp32.s_bridge` | signs-moving-sums | 1 | **25.32** [24.93, 25.72] | 24.59 [24.11, 25.08] | 25.32 [23.81, 26.84] | 25.27 [24.89, 25.65] | 24.57 | 1.0336 |
| `fp32.s_drift12` | signs-moving-sums | 1 | **24.70** [24.30, 25.11] | 23.99 [23.50, 24.48] | 24.70 [23.22, 26.19] | 24.71 [24.30, 25.12] | 24.02 | 1.0083 |
| `fp32.s_pair0` | signs-moving-sums | 1 | **24.64** [24.25, 25.03] | 23.93 [23.45, 24.41] | 24.64 [23.17, 26.12] | 24.62 [24.24, 25.01] | 23.94 | 1.0058 |
| `fp16.s_inword0` | signs-moving-sums | 1 | **16.68** [16.34, 17.02] | 16.20 [15.80, 16.60] | 16.68 [15.66, 17.71] | 16.88 [16.51, 17.25] | 16.41 | 0.7577 |
| `fp16.s_wpair0` | signs-moving-sums | 1 | **21.44** [21.08, 21.81] | 20.82 [20.40, 21.25] | 21.44 [20.15, 22.74] | 21.56 [21.19, 21.93] | 20.96 | 0.9740 |
| `fp32.x_logu_bsteady` | exponents-spread-gate | 2 | **13.88** [13.49, 14.26] | 13.48 [13.01, 13.95] | 13.88 [12.99, 14.77] | 13.82 [13.46, 14.17] | 13.43 | 0.5664 |
| `fp32.x_logu_s50` | exponents-spread-gate | 1 | **8.27** [7.88, 8.66] | 8.03 [7.55, 8.51] | 8.27 [7.65, 8.89] | 8.20 [7.84, 8.55] | 7.97 | 0.3375 |
| `fp16.x_logu_s50` | exponents-spread-gate | 1 | **7.71** [7.35, 8.07] | 7.49 [7.07, 7.90] | 7.71 [7.14, 8.28] | 7.69 [7.33, 8.04] | 7.47 | 0.3502 |
| `fp32.g_arows_alt` | gated-kinds | 1 | **13.29** [12.90, 13.69] | 12.91 [12.43, 13.39] | 13.29 [12.43, 14.16] | 13.24 [12.87, 13.60] | 12.87 | 0.5426 |
| `fp32.g_blanes_alt` | gated-kinds | 1 | **14.00** [13.60, 14.40] | 13.59 [13.11, 14.08] | 14.00 [13.10, 14.90] | 13.94 [13.57, 14.30] | 13.55 | 0.5713 |
| `fp32.g_blanes_steady` | gated-kinds | 1 | **13.22** [12.83, 13.60] | 12.83 [12.36, 13.31] | 13.22 [12.36, 14.07] | 13.21 [12.84, 13.58] | 12.84 | 0.5394 |
| `fp16.g_blanes_alt` | gated-kinds | 2 | **12.44** [12.08, 12.80] | 12.08 [11.67, 12.50] | 12.44 [11.64, 13.25] | 12.46 [12.10, 12.82] | 12.11 | 0.5652 |
| `int8.g_awords_alt` | gated-kinds | 1 | **4.71** [4.24, 5.17] | 4.58 [3.99, 5.18] | 4.71 [4.17, 5.24] | 4.69 [4.13, 5.25] | 4.56 | 0.6737 |
| `int8.g_bpairs_steady` | gated-kinds | 1 | **3.76** [3.30, 4.21] | 3.66 [3.07, 4.24] | 3.76 [3.26, 4.26] | 3.71 [3.18, 4.24] | 3.61 | 0.5380 |
| `fp32.a_colconst_b_randn` | a-side-busy-partner | 2 | **23.17** [22.72, 23.61] | 22.50 [21.98, 23.02] | 23.17 [21.76, 24.57] | 23.15 [22.71, 23.58] | 22.51 | 0.9455 |
| `fp32.a_lo8_b_pi` | a-side-busy-partner | 1 | **10.68** [10.29, 11.07] | 10.37 [9.90, 10.85] | 10.68 [9.95, 11.41] | 10.82 [10.43, 11.20] | 10.52 | 0.4360 |
| `fp32.a_lo8_b_randn` | a-side-busy-partner | 1 | **22.23** [21.80, 22.65] | 21.58 [21.08, 22.09] | 22.23 [20.88, 23.58] | 22.18 [21.77, 22.58] | 21.56 | 0.9072 |
| `fp16.a_mant_b_randn` | a-side-busy-partner | 1 | **21.78** [21.43, 22.14] | 21.15 [20.74, 21.57] | 21.78 [20.47, 23.10] | 21.97 [21.61, 22.34] | 21.36 | 0.9894 |
| `int8.a_colconst_b_full` | a-side-busy-partner | 2 | **3.17** [2.50, 3.84] | 3.08 [2.33, 3.83] | 3.17 [2.48, 3.86] | 3.30 [2.40, 4.19] | 3.20 | 0.4535 |
| `int8.a_low2_b_full` | a-side-busy-partner | 1 | **4.82** [4.29, 5.36] | 4.70 [4.05, 5.34] | 4.82 [4.23, 5.42] | 4.87 [4.19, 5.55] | 4.73 | 0.6909 |
| `fp32.m_blines_eq` | memory-path | 1 | **24.80** [24.40, 25.20] | 24.08 [23.59, 24.57] | 24.80 [23.31, 26.29] | 24.79 [24.39, 25.19] | 24.10 | 1.0122 |
| `fp32.m_bpair_eq` | memory-path | 1 | **16.42** [16.03, 16.80] | 15.94 [15.47, 16.42] | 16.42 [15.40, 17.44] | 16.48 [16.11, 16.85] | 16.02 | 0.6701 |
| `fp32.z_single` | zero-level | 1 | **0.01** [-0.36, 0.39] | 0.01 [-0.45, 0.47] | 0.01 [-0.36, 0.39] | 0.01 [-0.34, 0.36] | 0.01 | 0.0006 |
| `int8.z_diag` | zero-level | 1 | **1.85** [1.39, 2.31] | 1.80 [1.21, 2.39] | 1.85 [1.38, 2.32] | 1.88 [1.32, 2.44] | 1.83 | 0.2649 |
| `int8.st_f32bytes` | another-stream | 2 | **6.69** [6.22, 7.16] | 6.51 [5.92, 7.11] | 6.69 [6.10, 7.28] | 6.63 [6.08, 7.18] | 6.44 | 0.9582 |

**Contrasts inside the pool** (W, a3, M5 then M4), each a pair built to answer one open case:

| contrast | what it isolates | M5 | M4 |
|---|---|---:|---:|
| `g_blanes_alt` − `g_blanes_steady` (fp32) | gate switching every cycle against a steady gate, same gated fraction | +0.78 | +0.73 |
| `a_lo8_b_randn` − `a_lo8_b_pi` (fp32) | the same A side with a busy and a quiet partner | +11.55 | +11.36 |
| `m_blines_eq` − `m_bpair_eq` (fp32) | B alternating in-lane with no line changes, against lines changing with no in-lane alternation | +8.38 | +8.31 |
| `s_drift12` − `s_pair0` (fp32) | a sum that drifts up against one that returns to 0 | +0.06 | +0.08 |
| `s_bridge` − `s_pair0` (fp32) | a sum that climbs and walks back against one that returns every step | +0.68 | +0.65 |
| `x_logu_s50` − `x_logu_bsteady` (fp32) | exponents spread: a random 50% word gate against a steady lane gate | -5.61 | -5.62 |
| `s_wpair0` − `s_inword0` (fp16) | fp16: cancelling across k-groups against inside the two-term update | +4.76 | +4.68 |

**For E115's registration** (its own decision; these are suggestions written before any data): the primary score is rms(D − M5)
over the priority-1 float tiles, beside M4's on the same tiles and the paired difference of their squared errors; then the
95% coverage, per format; then each open case's mean D − M5 and the contrasts above, measured against predicted. If E115 runs
on a card with no scale of its own, the `new` footing and the anchor ratios are the frozen predictions for it.

M5 and M4 differ by at most 0.20 W on any tile here (`fp16.s_inword0` 0.20, `fp16.a_mant_b_randn` 0.19 W; the rest 0.13 W or less), well inside either interval: this pool was built blind to the model, so it tests the open cases themselves, and it can hardly tell M5 from M4. The model, its leave-one-kind-out scores and every file behind these numbers are in [`docs/reports/data/2026-11-01-q133b-power-model/`](../../../../docs/reports/data/2026-11-01-q133b-power-model/README.md).

## Amendment after verification (Sun 1 Nov 2026, before E115's claim)

*Appended after an independent verifier's read. Nothing above changed but § Order's item 4, restored to its original wording with a dated note (C6 of the model's [corrections](../../../../docs/reports/data/2026-11-01-q133b-power-model/README.md#corrections-after-verification-sun-1-nov-2026)), and item 6, appended. No pool file, count or prediction changed.*

**How M5 was chosen.** "The form chosen by nested leave-one-kind-out over thirteen experiments", above, needs one qualification: the candidate forms were widened after the first fit's results had been read. M5's own form, the adder priced per float format, was added then, and E91's anchor rows were dropped (the model's README, C1 and § Order). Run as first written, the procedure scores 0.214 W, worse than M4's form refitted (0.211 W). The 0.011 W gain of M5's procedure over M4's form refitted is not resolved by a paired bootstrap over kinds (95% CI −0.028 to +0.007 W, C2), and on E102 M5 is no better than M4. None of this touches the pool, committed before any of it (`a9167033`), or the predictions, frozen before any card ran a tile: they stay blind predictions, and E115 decides whether the per-format term helps.

**The contrasts' 95% intervals**, frozen here before E115's claim: [`contrasts-blind3.json`](contrasts-blind3.json) (sha256 `399128b9ff83f1a357e6c20cdfd359f11eeb2a7d1d6415516e63cbae4a628578`) and [`contrasts-blind3.md`](contrasts-blind3.md), written by [`contrasts_blind3.py`](../../../../docs/reports/data/2026-11-01-q133b-power-model/contrasts_blind3.py) (sha256 `7f82fbbafb8daa2aff64aabb137c9a1ba8d9e48e496d1a3cc3f05fec928b8269`) from `predictions-blind3.json` (`5f28091a…`), which it reads and does not change. Each point is the difference of the two tiles' frozen predictions. Each interval is the two tiles' frozen 95% half-widths in quadrature; on a new card, it is a3's interval widened by one card's step on the contrast, the rule the tiles' own `new` footing uses. On pairs of training kinds in one experiment, type and card this stand-in is about right, not conservative: 95.5% of 1,680 float differences fall inside it (the model's `corrections-check.txt` C5). W over the type's own zeros at 600 MHz:

| contrast | **M5, a3 [95%]** | M5, c1 [95%] | M5, new card [95%] | M4, a3 [95%] |
|---|---:|---:|---:|---:|
| `g_blanes_alt` − `g_blanes_steady` (fp32) | **+0.78** [+0.23, +1.34] | +0.76 [+0.09, +1.43] | +0.78 [+0.23, +1.34] | +0.73 [+0.21, +1.24] |
| `a_lo8_b_randn` − `a_lo8_b_pi` (fp32) | **+11.55** [+10.97, +12.12] | +11.21 [+10.52, +11.90] | +11.55 [+10.67, +12.42] | +11.36 [+10.80, +11.92] |
| `m_blines_eq` − `m_bpair_eq` (fp32) | **+8.38** [+7.82, +8.94] | +8.14 [+7.46, +8.82] | +8.38 [+7.64, +9.12] | +8.31 [+7.76, +8.86] |
| `s_drift12` − `s_pair0` (fp32) | **+0.06** [−0.50, +0.63] | +0.06 [−0.63, +0.75] | +0.06 [−0.50, +0.63] | +0.08 [−0.48, +0.65] |
| `s_bridge` − `s_pair0` (fp32) | **+0.68** [+0.12, +1.24] | +0.66 [−0.02, +1.34] | +0.68 [+0.12, +1.24] | +0.65 [+0.11, +1.19] |
| `x_logu_s50` − `x_logu_bsteady` (fp32) | **−5.61** [−6.16, −5.06] | −5.45 [−6.12, −4.78] | −5.61 [−6.25, −4.97] | −5.62 [−6.12, −5.12] |
| `s_wpair0` − `s_inword0` (fp16) | **+4.76** [+4.26, +5.26] | +4.62 [+4.04, +5.21] | +4.76 [+4.19, +5.33] | +4.68 [+4.15, +5.20] |

**Reading the memory-path pair.** The bench has no memory path, so its +8.38 W for `m_blines_eq` − `m_bpair_eq` is all compute and the operand bus: 2.99 W multiplier, 2.05 W adder, 2.61 W other nets, 0.74 W bus (`contrasts-blind3.json` › `M5_terms_w_a3`). Only `m_bpair_eq`'s B lines change (3,552 bits an op against 0), while `m_blines_eq`'s B half-lines change about twice as often (3,680 against 1,776; `blind3.json` › `stats`). A card reading below the interval would fit a cost for B lines that change, a reading above it a cost for half-lines that change, and either could instead be compute the bench misprices.

**For E115's registration**, in place of "the contrasts above, measured against predicted": each contrast against its interval here, on the footing of the card that runs it.
