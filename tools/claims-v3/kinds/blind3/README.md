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
