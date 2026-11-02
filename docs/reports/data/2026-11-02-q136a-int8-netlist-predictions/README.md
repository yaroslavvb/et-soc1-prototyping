# Q136(a): a single-bit set that separates Q133(a)'s int8 netlists, each netlist's prediction frozen before E130

*The complaint this answers: on the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 12, "int8 at gate level", which [Q133(a)](../2026-11-01-q133a-int8-gate-level/README.md) narrowed and left open: "which multiplier: the single bits favour radix-4 Booth on B, and E78's kind-level watts favour Booth on A; neither is registered". Q134's final critic, its item 8, asked for this: "freeze each netlist's prediction for a new single-bit set chosen to separate them (odd/even on both lists, the sign bit at two base words). Register it and run it on aifoundry3."*

*Mon 2 Nov 2026 (week 45), Q136, desk work, 06:47 to about 08:00 PST (the bench runs 06:54–06:56 and 07:14–07:33). **No card was opened and no device command was sent**; every watt below is a prediction or a committed experiment's (E78, E79, E102), named where it is used. The tiles are written by the kinds machinery, [`tools/claims-v3/kinds/make_e130.py`](../../../../tools/claims-v3/kinds/make_e130.py), into [`tools/claims-v3/kinds/e130/`](../../../../tools/claims-v3/kinds/e130/) (`e130.json`, `sha256.txt`, `tiles/int8/`). The counts are Q133(a)'s bench, rebuilt unchanged ([`rtl-sim/tima_gate`](../../../../rtl-sim/tima_gate/README.md), zero delay), and every number is in [`predictions.json`](predictions.json), written by [`predict.py`](predict.py) from the committed counts in [`runs/`](runs/); [`tables.md`](tables.md) is generated from it. E130, the card run that scores these predictions on aifoundry3, is another lane's; nothing here registers its rules.*

## Results

**1. The set: 26 int8 tiles in E79's two layouts, on fresh base words.** On the B side A is held at 1 and B's chosen bit flips on the line-group parity (E79's `kg` layout, E102's B list: 1,024 flips an op); on the A side B is held at 1 and A's chosen bit alternates down the rows (E79's A list: 8,192 flips an op). Each item has its own zero, the same base held constant, so an item minus its zero differs in the chosen bit alone. The bases are new: drawn from `random.Random(20261102)`, each byte of popcount 4 (so no flip zeroes a byte and no operand word is gated), none of them E79's (`e130.json` `bases`).

| tiles | what | base word | held operand |
|---|---|---|---|
| `hb1`, `b1_0` … `b1_7` | B's every bit, odd and even, and the sign | B1: 53 ac a3 c6 5c aa 3a a6 (each byte b6 + b5 = 1) | A = 1 |
| `hb2`, `b2_7` | B's sign bit at a second base word | B2: e8 e4 f0 72 6c 71 e1 63 (b6 = b5 = 1) | A = 1 |
| `hb1d`, `b1d_7` | B's sign bit, B1, with the held operand dense | B1 | A = 0x55 |
| `ha1`, `a1_0` … `a1_7` | A's every bit | A1: 0xc6 (b6 + b5 = 1) | B = 1 |
| `ha2`, `a2_7` | A's sign bit at a second base word | A2: 0xf0 (b6 = b5 = 1) | B = 1 |
| `ha1d`, `a1d_7` | A's sign bit, A1, with the held operand dense | A1 | B = 0x55 |

**Why these.** Both operands are signed on the card and in the bench (the kernel's `fma_word` leaves `u_a` and `u_b` clear), so the unit multiplies 9-bit sign-extended values. A radix-4 Booth recoder reads overlapping three-bit windows of ONE operand, so an odd bit of the recoded operand enters two digits and an even bit one. Yosys recodes the second operand of `x * y`, which is B as the RTL is written (Q133(a) METHOD §1). So `booth` and `booth_tree` should alternate on B and not on A, `booth_swap` on A and not on B, and `plain` on neither: odd and even positions on both lists tell the three groups apart. The two sign-bit base words differ in bits 6 and 5, which set the recoded operand's top digit, d3 = −2·b7 + b6 + b5: a sign flip moves it between +1 and −1 at word 1 and between +2 and 0 at word 2. The dense held operand (0x55, four nonzero radix-4 digits) multiplies the partial-product rows that carry the flipped operand's sign, but only in netlists that do not recode it (result 4).

**2. Each netlist's prediction, frozen: fJ per flipped bit at its own k** (whole VPU, `nets_map`, the mean of the bench's three launch points; `predictions.json` `arms.<netlist>.items.<tile>.fJ_map`). The price is k × merged nets toggled per flipped bit, item minus its zero. A flip moves no clocked bit: Δ clocked register bits is 0.0 on every item at every point (`d_ff_clocked_per_op`). k is each netlist's own int8-alone fit of Q133(a) (M2 on E78's board watts, aifoundry3, 600 MHz): `booth_tree` 1.006 ± 0.045, `booth` 1.018 ± 0.046, `booth_swap` 0.856 ± 0.019, `plain` 0.832 ± 0.045 fJ per net toggle (jackknife s.e.; `inputs.k_fJ_per_net_toggle`). The step in watts is fJ × flips per op × E78's int8 rate, 1.9255 × 10⁹ ops/s (`dW_map`; `tables.md` has every tile in watts).

| tile | bit | `booth_tree` | `booth` | `booth_swap` | `plain` | step, W (`booth_tree`; range over the four) |
|---|---:|---:|---:|---:|---:|---|
| `b1_0` | 0 | 9.7 | 10.0 | 8.6 | 9.7 | 0.019 (0.017–0.020) |
| `b1_1` | 1 | **90.3** | **90.8** | 7.7 | 8.4 | 0.178 (0.015–0.179) |
| `b1_2` | 2 | 19.7 | 20.4 | 9.3 | 11.3 | 0.039 (0.018–0.040) |
| `b1_3` | 3 | **79.3** | **80.0** | 12.9 | 13.4 | 0.156 (0.025–0.158) |
| `b1_4` | 4 | 24.0 | 24.5 | 15.0 | 12.2 | 0.047 (0.024–0.048) |
| `b1_5` | 5 | **64.8** | **64.8** | 13.9 | 13.9 | 0.128 (0.027–0.128) |
| `b1_6` | 6 | 19.6 | 20.5 | 14.2 | 12.3 | 0.039 (0.024–0.040) |
| `b1_7` | 7 (sign) | 127.2 | 129.7 | 119.3 | 135.3 | 0.251 (0.235–0.267) |
| `b2_7` | 7, word 2 | 130.4 | 132.6 | 120.9 | 137.3 | 0.257 (0.238–0.271) |
| `b1d_7` | 7, A = 0x55 | 119.5 | 121.7 | 127.7 | 117.7 | 0.236 (0.232–0.252) |
| `a1_0` | 0 | 46.6 | 47.7 | 38.1 | 41.8 | 0.735 (0.601–0.753) |
| `a1_1` | 1 | 47.5 | 47.6 | **201.5** | 45.0 | 0.749 (0.710–3.179) |
| `a1_2` | 2 | 50.6 | 51.4 | 72.9 | 44.8 | 0.797 (0.707–1.151) |
| `a1_3` | 3 | 56.2 | 55.4 | **115.0** | 49.4 | 0.887 (0.779–1.815) |
| `a1_4` | 4 | 62.9 | 64.0 | 59.0 | 47.2 | 0.993 (0.745–1.009) |
| `a1_5` | 5 | 57.8 | 57.2 | **111.6** | 53.1 | 0.912 (0.837–1.760) |
| `a1_6` | 6 | 61.1 | 61.5 | 70.1 | 53.2 | 0.963 (0.839–1.106) |
| `a1_7` | 7 (sign) | 294.1 | 288.8 | 227.8 | 247.5 | 4.639 (3.593–4.639) |
| `a2_7` | 7, word 2 | 294.1 | 290.8 | 229.8 | 250.2 | 4.640 (3.624–4.640) |
| `a1d_7` | 7, B = 0x55 | 326.0 | 323.2 | 219.6 | 300.9 | 5.142 (3.464–5.142) |

The largest predicted step is 5.1 W (`a1d_7`), the smallest 0.015 W (`b1_1` in `booth_swap`). `nets_hier` is frozen beside it (`fJ_hier`, `dW_hier`; `tables.md`). On the B list the two merges agree within 2.2 fJ a flip; on the A list `nets_hier` reads about half (`booth_tree`'s A list 24–33 fJ a magnitude bit and 153 at the sign, against 47–63 and 294), as Q133(a) found on E79's tiles (its Departures).

**3. What separates them: odd against even on both lists, and the A sign bit's held operand.** In fJ (the three-point means; `predictions.json` `arms.<netlist>.stats`), with the gap between netlists in units of the 95% half-width the card would give that statistic at E79's own 4-pass precision on aifoundry3 (E79 `scored.json`: median item half-width 6.0 board-fJ on the A list, 17.9 on the B list; a difference of two three-bit means carries √(2/3) of it, a difference of two items √2; `separation`):

| statistic | `booth_tree` | `booth` | `booth_swap` | `plain` | card half-width | separates, by (half-widths) |
|---|---:|---:|---:|---:|---:|---|
| B: odd bits (1, 3, 5) − even (0, 2, 4), `nets_map` | **+60.3** | **+60.3** | +0.5 | +0.8 | 14.6 | Booth on B from the rest, 4.1 |
| same, `nets_hier` | +60.7 | +60.6 | +0.8 | +1.1 | 14.6 | 4.1 |
| A: odd − even, `nets_map` | +0.5 | −1.0 | **+86.0** | +4.5 | 4.9 | Booth on A from the rest, 16.6–17.7 |
| same, `nets_hier` | +1.1 | +0.8 | **+50.6** | +2.9 | 4.9 | 9.7–10.2 |
| A sign: B = 0x55 − B = 1, `nets_map` | +31.9 | +34.3 | **−8.2** | +53.4 | 8.5 | Booth on A from the rest, 4.7–7.2 |
| same, `nets_hier` | +49.4 | +47.6 | **+4.2** | +34.1 | 8.5 | 3.5–5.3 |
| B list mean, bits 0–6, `nets_map` | 43.9 | 44.4 | 11.7 | 11.6 | 6.7 | Booth on B from the rest, 4.8 (a level: it carries k) |
| B sign: A = 0x55 − A = 1 | −7.7 | −8.0 | +8.4 | −17.5 | 25.2 | nothing (at most 1.0) |
| sign, word 2 ÷ word 1, B and A | 1.02–1.03, 1.00–1.01 | 1.02, 1.01 | 1.01, 1.01 | 1.02, 1.01 | — | nothing: the same in all four |

So the set tells **three groups** apart. Booth on B (`booth`, `booth_tree`) alternates on B (odd bits 4.2–4.4× the even in either merge, against 1.05–1.09× in the others) and not on A. Booth on A (`booth_swap`) alternates on A (2.5× in `nets_map`, 2.6× in `nets_hier`, against 0.98–1.13×) and not on B. Its A sign bit moves −4% to +3% with a dense held B, where every other netlist's rises 11–22% (24–32% in `nets_hier`). `plain` does neither. Each separation holds in both merges. **`booth` and `booth_tree` are not separated**: no statistic puts them more than 0.3 card half-widths apart, so at zero delay the sums' structure does not show in a single bit. Between Booth on B and `plain` the A sign's held-operand step changes order with the merge (`nets_map` puts `plain` higher, `nets_hier` lower), so only B's odd − even, 4.1 half-widths, separates those two robustly.

**4. The sign bit at two base words is a prediction all four netlists share, not a separator.** At word 2 every netlist prices the sign bit within 3% of word 1, on both lists and in both merges. With the held operand at 1, the held operand has one nonzero digit (one nonzero partial-product row), and in every netlist a sign flip costs the same whatever bits 6 and 5 are. A reading, not shown: the recoder's negate signal follows the window's top bit, so the digit's value does not matter. If the card's sign-bit price differs between the two words, every netlist is wrong about the sign in the same way. That is the open "the sign bit is priced about twice the card's" of item 12. On the levels, `nets_map` puts A's sign at 228–294 fJ, about 1.5–1.9× E79's 152 board-fJ at its own base word; `nets_hier` puts it at 133–153 fJ.

**5. The bench is Q133(a)'s, number for number.** The four netlists' benches were rebuilt from the same sources (core-et `b38a1a31`, `rtl-sim/tima_gate` and `rtl-sim/fma_toggle_v2` unchanged since Q133(a), the same `*_staged.v` netlists and cell models by sha256), the same Makefile and flags (`-fno-dfg`), Verilator 5.052 and Q133(a)'s own maps, on a second desk machine (Departures D1). The control put Q133(a)'s committed single-bit tiles (`e102_hq`, `e102_bk_5`, `e79_a8q`, `e79_a8_7`) through all four: **400 of 400 numbers equal** to Q133(a)'s committed `counts_bits.json` (unit and VPU `nets_hier`, `nets_map`, `nets_hier2`, net counts, stages, the check, cycles, clocked bits; [`runs/control.json`](runs/control.json)). Q133(a)'s own binary for `booth_tree`, run on the usual desk machine before its thermal guard paused it, also gave the same four tiles exactly (16 of 16). Every one of the 26 × 4 × 3 tile-points has 0 of 256 accumulator words wrong. The rest of the VPU (VPU − unit) adds the same per flip in every netlist (−0.7 to +2.1 nets), so the netlists differ by their units alone.

**6. What the card already said at E79's base words** (post hoc; context only, nothing registered): E79's `kg` B list on aifoundry3 put odd − even at +40 board-fJ (61.6, 72.3, 85.6 against 27.1, 31.2, 40.5) and its A list at −0.9 fJ (E79 `scored.json` `prices.int8_b_kg`, `int8_a`), the Booth-on-B pattern at a smaller amplitude than the netlists'. E78's kind-level watts fit `booth_swap` best (Q133(a) result 6). E130 tests the question on base words neither line of evidence has seen, against predictions frozen first.

## For E130's registration (suggestions, not rules)

- **The tiles**: `tools/claims-v3/kinds/e130/tiles/int8/<name>.bin`, 2,048 bytes each (`sparsity_host --test fma --type int8 --values file:<tile>`), sha256s in `e130/sha256.txt` and `e130.json`; `python3 tools/claims-v3/kinds/make_e130.py --check` rebuilds and compares them. Each item's zero is named in `e130.json` (`zero`), with its designed flips per op (`designed_flips_per_op`: 1,024 B, 8,192 A).
- **Expected steps** for launch gates and budgets: 0.015–0.27 W on the B list, 0.6–5.1 W on the A list (table above). The three A sign items are 3.5–5.1 W in every netlist, and `a1_1` reaches 3.2 W in `booth_swap`.
- **The statistics that separate in both merges**: B's odd − even (Booth on B from the rest: about +60 against +1 fJ, a midpoint near +30); A's odd − even (Booth on A from the rest: +51 to +86 against −1 to +5, a midpoint near +25); A's sign step with the dense held B (Booth on A −8 to +4 against +32 to +53). The word-2 sign ratio is a shared prediction (1.00–1.03). Shapes (ratios and differences inside a list) do not carry k; levels do, and on the A list a level depends on the merge by about 2×.
- **The noise**: at E79's 4-pass precision the B list's contrast is 4.1 half-widths, so the B side wants more passes than the A side; E102's rail read B singles at a median half-width of 15 rail-fJ on aifoundry1 card 1.

## What was asked and what was done

Asked (Q136's brief, lane Q136(a), from Q134's critic item 8): choose a single-bit set that separates Q133(a)'s four int8 netlists, with odd and even positions on both the A and the B list and the sign bit at two base words; freeze each netlist's predicted switching for every tile (zero-delay counts in the fixed bench, priced at each netlist's own fitted k), with the tiles written by the kinds machinery, sha256s and a README; commit before E130's claim. Done: all of that, with a second sign-bit contrast (the held operand), both merges and three launch points.

**Departures, each decided before any card ran any of these tiles.**
- **D1 (07:08 PST): the bench ran on a second desk machine.** The usual desk machine's thermal guard went to its hot tier at 06:56 PST, because the machine's 1-minute load reached 173 and 160 on 16 CPUs. In that tier it pauses agent work: from then on, every new bench process was stopped within a minute, for up to 30 minutes at a time, and the tier does not lift until the load is quiet. Q133(a)'s own binary had finished its control first (result 5). The guard was left alone. On the second machine (Apple silicon, idle) the same sources, flags and Verilator version built the four benches (07:10–07:13); the control's 400 equal numbers are why its counts are quoted as the fixed bench's. Builds and runs used `nice -n 10` and at most 6 jobs, as on the usual machine.
- **D2 (07:25 PST): the set's second version.** The first had a third sign-bit pair at a word with b6 = b5 = 0 (`hb3`, `b3_7`, `ha3`, `a3_7`). At the desk, no netlist's sign-bit price moved with the word, within 1.3% ([`runs/screening_v1_class3.json`](runs/screening_v1_class3.json); `predictions.json` `arms.<netlist>.screening_v1_class3`; the retired tiles' sha256s in [`e130_v1_class3.sha256`](e130_v1_class3.sha256)). So that pair was replaced by the dense-held pair (result 1). The word-3 bases are still drawn, so the other 22 tiles are byte for byte the first version's. The choice was made on the bench's predictions; no card had run either version.
- **D3: `nets_map` is primary, with `nets_hier` frozen beside it.** This is Q133(a)'s convention for single bits and the merge Q132(b) sets beside watts. Only `booth_tree` has `train_maps.py`'s maps; the other three have Q133(a)'s one-stream maps, as its single bits did. A map never drops a net; it only merges names it learned to repeat, so a one-stream map can only merge less. The separations in result 3 hold in both merges.
- **D4: the primary is the mean of the bench's three launch points** (157,232, 471,698 and 786,163 ops into a 0.5 s launch; `run_kinds.py`: "a time average over the launch is the average over the three"). Q133(a) ran single bits at the middle point only; that point's values are kept (`fJ_map_middle_point`) and each point's (`fJ_map_by_point`, `tables.md`). Each point is within 5% of the three-point mean on the B list's magnitude bits and within 2% on every sign bit; A's magnitude bits move up to 16% with the accumulator state.
- **D5: k is post hoc.** Each netlist's k was fitted on E78's 15 int8 kinds after their data. It scales a netlist's levels (2.3–5.4% s.e.), not its shapes.

## Device commands sent

**None.** This is a desk lane: no card was opened, no device node touched, no device-management command sent, so section 17's list is empty here. The tiles are operand files and carry no command; E130's runner lists and classifies its own.

## What this cannot say

- **The netlists are Q133(a)'s**: an open 7 nm library, from the public RTL's later revision (Erbium); the ET-SoC-1's own multiplier is not public. A set that separates these four tests them, not every possible multiplier.
- **Zero delay: no glitches.** A Booth array is the kind of logic that glitches (Q129 found about 1.5× in the float tree); a timing-annotated count could reorder the levels, and less likely the shapes.
- **k is a fitting constant**, per merged net toggle at 600 MHz on one card, fitted after E78's data. Levels carry it and the merge; shapes do not.
- **The card's precision is borrowed** from E79's four passes at another base word. E130 measures its own.
- **`booth` against `booth_tree` stays open**: this set cannot tell them apart.

## Section 11, item 12, and what a reader can be told

- **Item 12's first open point ("which multiplier") now has frozen predictions**, which E130 will score on aifoundry3. The glitch count, the sign bit's price and int8's clock term stay open. The sign bit gets a shared prediction (result 4); the other two are not addressed here.
- For the blog, each from a committed file: "Before the card ran it, each of four gate-level versions of the int8 multiplier predicted a different pattern for the same 26 single-bit flips. A multiplier that Booth-recodes B makes B's odd bits cost about four times its even bits, one that recodes A does that to A instead, and one with no recoder does neither (`predictions.json` `separation`)." And: "None of the four predicts that the sign bit's cost depends on the value's next two bits (`stats.*.B_sign_w2_over_w1`, `A_sign_w2_over_w1`)."

## Files

| file | what |
|---|---|
| `README.md`, `tables.md` | this, and the generated tables (both merges, watts, launch points, inputs) |
| `predictions.json`, `predict.py` | **the frozen predictions**: per netlist, per tile, fJ per flipped bit and W of step in both merges, by launch point, the separating statistics, the gaps, the inputs (k with its s.e., rate, tile sha256s) |
| `runs/<netlist>/counts.json` | `run_kinds.py`'s output for the 26 tiles at the three launch points (one call per tile, merged) |
| `runs/control.json` | the control against Q133(a)'s committed counts, number by number |
| `runs/screening_v1_class3.json`, `e130_v1_class3.sha256` | the retired first-version pair's counts and tile hashes (D2) |
| `versions.txt`, `sha256.txt` | tools, sources and hosts; hashes of every file here and of the tiles |
| `../../../../tools/claims-v3/kinds/make_e130.py`, `e130/` | the tile generator, `e130.json` (bases, zeros, flips, sha256s), `sha256.txt`, `tiles/int8/*.bin` |

```
python3 tools/claims-v3/kinds/make_e130.py --check          # the 26 tiles, byte for byte
# the bench: rtl-sim/tima_gate/README.md (make gate per netlist, Q133(a)'s netlists and maps); one run_kinds.py call per tile:
#   run_kinds.py --bin obj_<arm>/Vtb ... --only __none__ --extra-tiles int8:e130_<tile>:<tile.bin> --points launch
uv run --script predict.py                                   # in this directory: predictions.json, tables.md
```
