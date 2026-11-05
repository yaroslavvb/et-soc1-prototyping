# Blind pool 8 (Q142(d))

Made by `make_blind8.py build` (the committed generator; DESIGN.md beside it is the design) from seed `0x1da1fde559d92805`, the first 16 hex digits of sha256 of lab commit `c996d1357609c10009c80e59dd8e85bcc652343f`. 64 tiles of 2,048 bytes (A then B, make_kinds' layout) for `sparsity_host --test fma --type <fmt> --values file:<tile>`.

Files: `MANIFEST` (pool 7's fields: sha256, file, label, format, case, priority, role, flag), `tiles/<fmt>/`, `RERUNS` (every tile whose bytes are an earlier pool's, under that pool's label), `provenance-blind8.json` (every tile's rule, seed stream, parameters, statistics and twin check), `real/` (the real cuts as float32 arrays and their provenance), `SHA256SUMS`.

Roles: `anchor` (the random anchors a and b, and the floor), `check` (the check anchor: a third draw of the anchors' rule, held out to check the scale the two give), `kind` (new tiles), `rerun` (scored apart). Priorities: anchors p2 as in pool 7; in each other group a seeded quarter is p2.

## What each class aims at

- **0**: Anchors. Two random anchors per format (pool 7's rules: standard normal floats, uniform -128..127 int8) for the session's own scale, a third draw of the same rule held out as the check anchor (role `check`), and the all-zero tile kept under pool 7's own label as the floor.
- **S**: Single high B bits: A one constant word, B alternating every cycle between a base word (columns 0-7) and the same word with one bit flipped (columns 8-15), so each lane's B operand toggles that one bit and nothing else moves. New bit positions (mantissa high, middle and low, and one exponent-or-sign bit per format) and new base words, drawn by the seed.
- **U**: Kinds aimed at no named class: whole-tile value distributions (heavy tails, log-normal magnitudes, mixtures, grids, per-row scales, sparsity, correlation along the stream, bimodal values), the families and their parameters drawn by the seed from a fixed menu.
- **L**: int8 whole lines: A random over the full range, B built from two or three distinct 64-byte lines that change as a whole at k-group boundaries, in new patterns (k-bit flips per byte, a change every second boundary, a three-line cycle, half the words of a line changing).
- **H**: int8 held B: A random over the full range, every B line identical, at held values and lines no earlier pool held.
- **R**: Real tiles: operands cut from two public W8A8 checkpoints no earlier pool used, run on a public-domain text: int8 per-token-quantised activations (blocks holding the activation outliers) against the checkpoints' own int8 weights, and float attention, query-key and dequantised-weight operands.
- **rerun**: Re-runs: pool 6 and pool 7 float tiles, byte for byte, under their own labels and classes, chosen from their bytes and the seed to span the range of the operand-toggle count; scored apart from the new tiles.

## Quotas

| Class | What | Count | Quota |
|---|---|---|---|
| 0 | Anchors (random a, b per format; the check anchor per format) | 9 | two random anchors per format plus a check anchor per format |
| S | Single high B bits (fp32 and fp16) | 10 | at least 8 single high B bits at new bit positions and base words (fp32 and fp16) |
| U | Kinds aimed at no named class | 13 | at least 12 kinds from the generator aimed at no named class |
| L+H | int8 whole lines and held B | 7 | at least 6 int8 whole-line or held-B tiles |
| R | Real tiles (2 models; 4 int8 W8A8) | 10 | at least 8 real tiles from two or more public models used in no earlier pool, int8 W8A8 outlier activations among them |
| rerun | Re-runs of pool 6/7 float tiles, under their own labels | 12 | about 12 re-runs of pool 6/7 float tiles under their own labels (scored apart), chosen by a rule from their bytes and the seed so that they span the range of the data term |
| floor | The zero floor, pool 7's label, per format | 3 | (kept as in every earlier pool) |
| all | | 64 | |

## Tiles by format and class

| Format | Class | Tiles |
|---|---|---|
| fp32 | 0 | 4 |
| fp32 | R | 3 |
| fp32 | S | 6 |
| fp32 | U | 5 |
| fp32 | rerun | 8 |
| fp16 | 0 | 4 |
| fp16 | R | 3 |
| fp16 | S | 4 |
| fp16 | U | 4 |
| fp16 | rerun | 4 |
| int8 | 0 | 4 |
| int8 | H | 3 |
| int8 | L | 4 |
| int8 | R | 4 |
| int8 | U | 4 |

## Checking it

`python3 -I make_blind8.py check --out <this directory>` re-reads every tile, re-derives its label's byte part and its class structure from the bytes, re-checks make_kinds.encode, NaN/Inf, the byte twins against blind3-blind7, MANIFEST and SHA256SUMS. Re-running `build` from the same downloads reproduces every byte.
