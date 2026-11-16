# Ledger v2 to ledger v3, term by term

Ledger v3 (Q193, Mon 16 Nov 2026) is ledger v2 with seven rules, each switchable on its own (`ledger_v3.predict(..., rules=...)`).
With all seven off it is v2, number for number: `readings_ledger_v3.py` checks it against E189's, E191's and E194's frozen v2
forecasts and their frozen scorers (`docs/reports/data/2026-11-16-ledger-v3/roundtrip-v3.txt`). The exact constants, each with
its committed source, label and band, are in `frozen-v3.json` (its sha256 in `frozen-v3.json.sha256` is the freeze line).

v3 was written after the blind days' data (E189 on aifoundry3, E191 on aifoundry1 card 1) and after E194's (aifoundry2 under its
governor). Two of its constants are fitted on E189 and E191 (c_br, R_dram) and rule 7's form was chosen after E194: every reading
of those days is POST HOC. The blind scores stand.

## The terms

| # | term | v2 (frozen: `frozen-v2.json` 59ff9117..., `workloads/ledger/ledger_estimate.py` e3670e78...) | v3 | rests on | label |
|---|---|---|---|---|---|
| r1 | seconds of scalar code | hart-cycles = the sum over instructions of 1 / the catalogue row's issue rate (both harts) | T_hart = a (N - B - n_o) + c_br B + the n_o others at their own rows a participant; a = 2.0 for the a-set (the fitted programs' one-cycle mnemonics: each one's own row, less delta, within half a hart-cycle of a) and for untaken branches; every other mnemonic (mul and csrr in the blind day's programs; div, float arithmetic, any class a later program brings) at its own row's 1/rate less delta; t = T_hart / f | a: the catalogue's one-cycle rows (1/rate 2.66-2.70; the widest a-set row, andi's, 2.82) less their measuring loop (delta = 1/rate(add) - 2.0 = 0.683); mul's row 21.32 and csrr's 5.94 hart-cycles after delta; c_br: E189's and E191's slowest-minion cycles of SHA-256 and both sorts, fitted with mul and csrr at their own rows (13.579; each card alone 13.579; one program left out 13.320-13.992; a priori from the catalogue's beq_taken row 16.578) | a and the a-set: a priori; c_br: FITTED, POST HOC |
| r2 | seconds of memory code | a copy at the midpoint of [the stores at 27 GB/s, + the loads at 76 GB/s] | t = max(issue, L2 line time, DRAM traffic time): L2 line time = a minion's two harts' (read fills x 22.36 + write fills x 26.02) minion-cycles at 600 MHz (no minion clock in them, assumed); DRAM traffic = 3 B a byte copied through the L1 (read, allocate, write back) / R_dram | the line cycles: E48 (26 Sep); R_dram: the blind days' copies (49.69 GB/s aifoundry3, 49.70 card 1; 49.70 for a card without its own fit) | line cycles: a priori; R_dram: FITTED, POST HOC; the max(): POST HOC (carried by the sorts, whose line time is hidden) |
| r3 | bytes by level | bytes past the L1 at the L2 tensor-load row, 2.83 pJ a byte (aifoundry3's literal on every card): SHA-256 the message line once a compression, the sort every key read and written once a level | lines past the L1 from an L1 model of the documented 512 B a hart (`tools/counter/l1_model.py`): F fills x e_r + WB dirty evictions x (e_w - e_r), the card's own E48 prices (e_r = flw 4 KiB less 512 B, e_w = fsw 4 KiB less 512 B); the level by the working set: the L1 if the model leaves no steady-state fill, the L2 up to the L2 a shire (512 KiB; 384 KiB the largest validated), DRAM past the L2 a shire and the L3 in all (32 MiB), anything else outside v3 | the L1 geometry (facts-l1.json); E48's line prices (aifoundry3 301.4 / 691.6 pJ, card 1 351.2 / 829.5, aifoundry2 313.4 / 723.1) | a priori |
| r4 | the DRAM copy | loads at the tensor-load DRAM row, stores at the write-back path, literal prices on every card, no awake time | bytes x (the card's own tload/dram + st_stream/dram rows) + P_stall x max(0, t - bytes / the store stream's rate) + the loop's instructions as v2; at another clock the rows unscaled, their bands' high ends x (V/V600)^2 (as rule 3's), P_stall x (f/600 MHz) x (V/V600)^2 | the catalogue's DRAM rows per card (26 Sep); P_stall = E23's 1.19 W (v2's own awake price), band down to E193's stall price 0.292 W (1,024 minions) | a priori; the awake analog: POST HOC |
| r5 | the forecast starting die | 55 C (band 52-60), the card at rest over the seconds alone | 50 C (band 48-60), the card at rest over the seconds + 1.5 ms a launch | the blind days' measured T0 (49-51 C, 50-52 C) and t_w - t_k (1.3-1.8 ms) | POST HOC (input conditions) |
| r6 | card inputs | aifoundry3's literals carried to every card (E191's registered rule) | rules 2-4 read the card's own column (E48, catalogue DRAM rows, R_dram); a v2 term with no per-card value keeps its literal | E191's copies (-0.6 / -0.7 J from the carried literals) | rule |
| r7 | a governed card above its idle clock | none (v2 has no base of its own above the idle point) | J = (1 - s) (J(f) + (B(f) - B(f_idle)) t) + s J(f_idle), s the share of the burst's work done at f_idle during the governor's climb (compute-bound: climb x f_idle / f / (K t); byte-bound: climb / (K t)); zero on a pinned card | B: E136's relation on aifoundry2 (25.456 / 28.243 / 33.610 W at 600 / 700 / 800 MHz); the climb: E190 arm A's median 0.852 s (0.014-1.325 s) | the numbers a priori; the FORM POST HOC (after E194) |

## Unchanged

Every instruction price (the catalogue's rows, random column, the card's own mean; branches by outcome), the card at rest (each
card's footing law) and the run's own leakage rise (k_rise), the tensor, scratchpad, L2-stream and mesh terms, sparse parity's
whole load, the clock scaling of prices (x (V/V600)^2 on instruction and awake terms; byte paths and line prices unscaled, their
bands x (V/V600)^2), and the multiply-add: no refit.

## Fixed before the land (Q193 verify-ledger3's findings; re-frozen before any E201 datum)

The adversarial verify of the first freeze (`frozen-v3.json` sha256 bd6e71ca..., Mon 16 Nov 2026 03:40 PST, never landed) held
with one minor finding and six nits. All seven are answered here, and v3 was re-frozen (`frozen-v3.json` > `supersedes`).

| # | finding | the change |
|---|---|---|
| 1 | rule 1's a-set held every mnemonic of the five programs, so mul (catalogue 1/rate 22.00 hart-cycles) and csrr (6.63) issued at a = 2.0, against the design's rule for a class outside the one-cycle rows | the a-set is now the programs' one-cycle mnemonics (their own row, less delta, within 0.5 hart-cycles of a; the widest inside is andi at +0.14), computed in the freeze from the catalogue; mul and csrr issue at their own rows (21.32 and 5.94 after delta), and c_br is refitted with them there: 13.5785731 to 13.5785617 (-8.4e-7 relative). No printed reading moved: in `readings-v3.json` the largest change in an error is 1.0e-6. A loop that is 5% mul now reads +48% slower than at a, as the design intends |
| 2 | no self-test pinned a v3 number, so a model re-frozen with a wrong price passed | `selftest_ledger_v3.py` pins 30 POST HOC readings (E189 and E191 in sample: seconds and S1; E194: seconds and S1 with rule 7) at 1e-4 against the verify lane's independent re-derivation from the design's equations (no shared code); v3 matches within 1.3e-6 |
| 3 | `verdicts()` scored S2 by the 15% test alone; E189's registered S2 also needs the mean t_k inside the band | S2 is now E189's test in full (`ok_s2()`, as `score_e189.py` ok_S2); the 15% test alone is kept as S2-15, a reading only. Every reading is unchanged (every mean t_k is inside its band) |
| 4 | the model's docstring did not use the prescribed citation; the README's "cannot fix" item 8 kept most of a checkpoint phrase | the citation is "the owner's private checkpoint of Wed 11 Nov 2026"; item 8 is reworded |
| 5 | the freeze did not pin what a new configuration's counts and lines come from, nor E191's third session and E194, which it reads | `parents_sha256` adds the kernel's disassembly (`ledger.dis.gz`), `workloads/ledger/ledger_desk.py` and E191 s3's and E194's `SHA256SUMS`; the self-test re-hashes every file of every pinned `SHA256SUMS` (5 lists, 1,164 files) |
| 6 | the readings and self-test scripts wrote into the committed data directory by default | `--out` is required by both; the README's reproduce line names it and compares the output with the committed files |
| 7 | at another clock, the DRAM copy's byte-row bands were not widened by (V/V600)^2, as the text says byte-path bands are | rule 4's two byte rows take x (V/V600)^2 on their bands' high ends, as rule 3's do (1.0 at 600 MHz, so no 600 MHz number moves) |

`tools/counter/test_l1_model.py` also gained E201's other shapes (the 256- and 64-key sorts, a 128 KiB copy part), at the verify
lane's independent LRU values.

## What changed in the code

| file | what |
|---|---|
| `ledger_v3.py` | the model: `predict()` for a plain program (its counts by mnemonic, lines past the L1, working set, a copy's bytes), `given()` (the given-seconds forecast of scores 1 and 1T), `predict_v2load()` (sparse parity and any v2 load: v2's prices, rules 5 and 7 on top), `program()`, the level rule, rule 7; it imports `ledger_v2.py` and `ledger_estimate.py` after checking their sha256 |
| `freeze_ledger_v3.py` | writes `frozen-v3.json` and its freeze line from committed sources; `--check` recomputes it byte for byte |
| `measured_ledger_v3.py` | the blind days' committed passes (E189, E191's second and third sessions, E194) |
| `programs_ledger_v3.py` | the plain programs from the counts v2 priced (`ledger_estimate.estimate()`, watched, not changed) and lines from the L1 model; `programs_from_estimate()` for a new configuration |
| `readings_ledger_v3.py` | the round trip to v2 and the post hoc readings |
| `selftest_ledger_v3.py` | the self-tests |
| `../counter/l1_model.py`, `../counter/ledger_interp.py`, `../counter/test_l1_model.py` | the L1 model, the sort interpreter (it reproduces the counter's per-sort counts at 512 keys exactly) and their desk test |

SPDX-License-Identifier: Apache-2.0
