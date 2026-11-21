# E224 arm A data, dated note 1 (post hoc): why R0 reads FAIL - the host's fixed check of C at K 25,600 against an fp32 accumulation that drops low bits, read at the desk, no wrong GEMM shown (NOT TESTED on a card); and why `sha256sum -c session/MANIFEST.sha256` fails on 215 of 562 lines (the scrub)

*Sat 21 Nov 2026 (week 47), PST; written from about 02:05 PST by round Q237's lane `fix-e224d` at the desk on aifoundry2 (no card, no simulator, no device opened), under `/usr/bin/python3` 3.12.3 with numpy 1.26.4, each numerical step single-threaded inside the round's CPU slots. It answers two findings of the day's data verifier `verify-e224d` (HOLDS WITH FIXES, 02:01 PST: both arms re-derive exactly from their raw records, every registered verdict reproduces, and the fixes it asks for are two dated notes). It comes after this directory's data commit `96528ad2` (committed 00:49:45 PST, pushed 00:49:50 PST) and arm B's `087f9baa` (committed 00:55:55 PST), and before the scorer's outputs are committed (a later lane; its notes are numbered after this one here, and after note 18 in arm B's directory). This note adds new files only: no committed file, datum, forecast, rule, band, label, verdict or scorer is changed, and nothing is dropped, re-chosen or re-scored.* **Labels:** **measured** (the committed records), **desk** (this lane's reading of code and its emulation), **post hoc** (all of it: read after the data), **REPORTED** (a reading, never a verdict), **NOT TESTED** on a card.

## 1. The files this note adds

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `posthoc-r0-check-e224.py` | the desk check of section 2: this lane's own code (numpy, single-threaded), reading only the two tile files and the 13 check records it names, all committed |
| `posthoc-r0-check-e224.txt` | its printed lines |
| `posthoc-r0-check-e224.json` | its output: the measured counts, the tiles, every model's counts and errors, the reading |
| `posthoc-manifest-scrub-e224a.txt` | the 215 manifest lines of section 3: kind, path under `session/`, the box's sha256, the committed sha256 |
| `SHA256SUMS-note1` | the five files above, then `README.md` and `SHA256SUMS` as the data commit holds them |

## 2. R0: why the check of C read 'wrong' at p3a and p3b

R0, as registered ([`E224.md`](../../../../tools/claims-v3/e224/E224.md)): "every check of C exact or approx; the smoke good ... a FAIL labels every other verdict of its arm and the pooled ones". It reads FAIL on both arms, from four checks on each:

| point (`gemmL1x1x25` fp16: K 25,600, 800 k-tiles of 32) | this arm (aifoundry1 card 1) | arm B (aifoundry2 card 0) | each check (measured) |
|---|---|---|---|
| p3a, E212's tile `fld16_mant` | runs 035, 076 | runs 040, 073 | words 16,384, within 0, exact 0: 'wrong', the process rc 1 |
| p3b, E217's tile `h_th_in` | runs 008, 092 | runs 014, 085 | words 16,384, within 12,160, exact 0: 'wrong', the process rc 1 |
| p3r, the host's random pool (gen `randn`; a twin) | runs 026, 081 | runs 035, 075 | within 16,384, exact 0: 'approx' |
| p3z, zeros (a twin) | runs 017, 087 | runs 041, 072 | exact 16,384: 'exact' |

The same two tile files (sha256 `a7d401d3e2f880f3...` and `c5da4e977eb04257...`, the bytes E224's kit pins on both arms) read 'approx' at `gemmL1x1x1` (K 1,024, 32 k-tiles) in E212's and E217's committed sessions: within 16,384 of 16,384 and exact 0 in each of E212 a1c1-S2 run 068 and a1c1-S3 run 060 (`fld16_mant`), and E217 a1c1-S3 run 079, a1c1-S4 run 060 and a1c0-S3 run 084 (`h_th_in`).

**The check** (rgm136 `host/main.cpp`, sha256 `f9b2279f838ad304...`, the host source both arms built (E224's kit pins it: arm A's harness and arm B's box source list); a desk reading of the code): the host reads C back after a short last launch and compares 64 sampled C tiles (lines 995-1013), each word against a reference summed in double over all KB x 32 k-tiles of its row and column (`Ref`, lines 823-839): 'exact' when C equals it, 'within' when |C - want| <= 1e-4 x the sum of the absolute products (`compareC`, lines 843-856). The check reads 'wrong' when any word is outside and 'approx' when all are within and not all exact, and a 'wrong' check makes the process exit 1 (lines 1050-1059).

**The tiles.** With one tile file every A tile and every B tile of the pools is that file's tile (lines 786-792), so each C tile is 800 k-tiles of one 16 x 16 partial product and the 64 sampled C tiles are equal: a count over 16,384 words is 64 times a count over the 256 words of one tile (12,160 = 190 x 64; 0 = 0 x 64). `fld16_mant` holds 1,024 halves, all positive and all with exponent field 15 (values in [1, 2)), none zero, subnormal, infinite or NaN: every product is positive, so the tolerance is 1e-4 of each word's own value. `h_th_in` holds 512 negative halves (exponent fields 6-16, none zero, subnormal, infinite or NaN): its k-tile's partial product has 129 of 256 words negative, and its words sum to a median 0.17 of their absolute products.

**Why the depth matters.** An fp32 accumulator that drops the bits below its running sum's last place at each addition (rounding toward zero, or truncating the smaller operand at alignment) loses part of a unit in that last place every time, always in the same direction, so for same-sign terms its loss grows in proportion to K: of the order of K x 2^-25 of the sum, which is **7.6e-4 at K 25,600** (above the 1e-4 tolerance) and **3.05e-5 at K 1,024** (inside it); this lane's emulation gives 5.3e-4 and 2.1e-5 (the median word) for per-product rounding toward zero. Rounding to nearest errs both ways, and its errors largely cancel (2.5e-5 at K 25,600).

**The emulation** (`posthoc-r0-check-e224.py`; desk, post hoc; 25 s single-threaded): the two tiles decoded as the host decodes them, the host's reference made as the host makes it, and 28 candidate fp32 accumulations of the card. **`fused-g<g>`**: the 32 products of a k-tile in groups of g consecutive k, each group summed exactly and added to the accumulator with one rounding (g 1, 2, 4, 8, 16, 32). **`align-g<g>-guard<G>`**: an adder that truncates the smaller operand at alignment, keeping G guard bits below the larger operand's last place with no sticky bit, then rounds (g 1, 2; G 0-3). Each rounds to nearest even (RNE) or toward zero (RZ). Products of two halves are exact; every sum is formed exactly in 80-bit precision (the script asserts it) and rounded once. These are models of the arithmetic, not the card's documented datapath. Words within / exact of the 256 words of one C tile:

| model | p3a, 800 k-tiles | p3a, 32 k-tiles | p3b, 800 k-tiles | p3b, 32 k-tiles | median abs(C - want) / abs at 800 k-tiles, p3a and p3b |
|---|---|---|---|---|---|
| fused-g1-RNE | 255 / 0 | 256 / 2 | 256 / 0 | 256 / 0 | 2.5e-5, 2.9e-6 |
| fused-g2-RNE | 256 / 0 | 256 / 1 | 256 / 0 | 256 / 0 | 1.7e-5, 2.3e-6 |
| fused-g4-RNE | 256 / 0 | 256 / 2 | 256 / 0 | 256 / 0 | 1.3e-5, 1.4e-6 |
| fused-g8-RNE | 256 / 0 | 256 / 3 | 256 / 0 | 256 / 0 | 8.6e-6, 8.7e-7 |
| fused-g16-RNE | 256 / 0 | 256 / 4 | 256 / 0 | 256 / 1 | 6.5e-6, 6.9e-7 |
| fused-g32-RNE | 256 / 0 | 256 / 6 | 256 / 0 | 256 / 1 | 5.9e-6, 6.2e-7 |
| fused-g1-RZ | 0 / 0 | 256 / 0 | 144 / 0 | 256 / 0 | 5.3e-4, 8.8e-5 |
| fused-g2-RZ | 0 / 0 | 256 / 0 | 209 / 0 | 256 / 0 | 2.7e-4, 4.4e-5 |
| fused-g4-RZ | 19 / 0 | 256 / 0 | 255 / 0 | 256 / 0 | 1.3e-4, 2.1e-5 |
| fused-g8-RZ | 250 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 6.7e-5, 1.1e-5 |
| fused-g16-RZ | 256 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 3.5e-5, 4.8e-6 |
| fused-g32-RZ | 256 / 0 | 256 / 1 | 256 / 0 | 256 / 0 | 1.7e-5, 2.1e-6 |
| align-g1-guard0-RNE | 0 / 0 | 256 / 0 | 253 / 0 | 256 / 1 | 5.3e-4, 8.4e-6 |
| align-g1-guard1-RNE | 0 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 2.6e-4, 5.6e-6 |
| align-g1-guard2-RNE | 67 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 1.3e-4, 4.3e-6 |
| align-g1-guard3-RNE | 200 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 6.9e-5, 3.1e-6 |
| align-g1-guard0-RZ | 0 / 0 | 256 / 0 | 253 / 0 | 256 / 0 | 5.3e-4, 8.4e-6 |
| align-g1-guard1-RZ | 0 / 0 | 256 / 0 | 208 / 0 | 256 / 0 | 5.3e-4, 4.7e-5 |
| align-g1-guard2-RZ | 0 / 0 | 256 / 0 | 174 / 0 | 256 / 0 | 5.3e-4, 6.9e-5 |
| align-g1-guard3-RZ | 0 / 0 | 256 / 0 | 157 / 0 | 256 / 0 | 5.3e-4, 7.9e-5 |
| align-g2-guard0-RNE | 0 / 0 | 256 / 0 | 256 / 0 | 256 / 1 | 2.7e-4, 6.2e-6 |
| align-g2-guard1-RNE | 52 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 1.3e-4, 4.3e-6 |
| align-g2-guard2-RNE | 211 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 6.5e-5, 2.8e-6 |
| align-g2-guard3-RNE | 255 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 3.4e-5, 2.2e-6 |
| align-g2-guard0-RZ | 0 / 0 | 256 / 0 | 256 / 0 | 256 / 0 | 2.7e-4, 6.2e-6 |
| align-g2-guard1-RZ | 0 / 0 | 256 / 0 | 251 / 0 | 256 / 0 | 2.7e-4, 2.2e-5 |
| align-g2-guard2-RZ | 0 / 0 | 256 / 0 | 238 / 0 | 256 / 0 | 2.7e-4, 3.3e-5 |
| align-g2-guard3-RZ | 0 / 0 | 256 / 0 | 225 / 0 | 256 / 0 | 2.7e-4, 3.9e-5 |
| **measured** (both cards at 800 k-tiles; E212's and E217's sessions at 32) | **0 / 0** | **256 / 0** | **190 / 0** | **256 / 0** | - |

What it shows (post hoc, REPORTED):
- **Round to nearest with no bit dropped does not give the card's counts:** the six fused RNE models put p3a at 255-256 of 256 words within at 800 k-tiles, where the card had 0, and leave 1-6 exact words a tile at 32 k-tiles (64-384 of 16,384), where the card left none.
- **The 13 models that give p3a's counts at both depths all drop low bits:** they round toward zero after each product or each pair of products (fused-g1-RZ, fused-g2-RZ), or truncate at alignment (align-g1 with RZ at any guard or RNE with 0-1 guard bits; align-g2 with RZ at any guard or RNE with none). Dropping bits less often does not: rounding toward zero once per 4, 8, 16 or 32 products puts p3a at 19, 250, 256 and 256 within, and truncation at alignment with more guard bits and rounding to nearest (2-3 guard bits per product, 1-3 per pair) at 52-255.
- **p3b does not pin the datapath:** 11 of those 13 also give p3b's counts at 32 k-tiles, and at 800 k-tiles they put p3b at 144 to 256 of 256 within. The card's 190 lies inside that range, but no model gives it.
- **The size of the loss:** per-product rounding toward zero loses a median 5.3e-4 and at most 7.2e-4 of each p3a word at 800 k-tiles (all 256 words outside the tolerance), and 2.1e-5 to 2.8e-5 at 32 k-tiles (all inside); per-product rounding to nearest, a median 2.5e-5 at 800 k-tiles.

**The reading** (post hoc, REPORTED; NOT TESTED on a card): the same counts on both cards are those of an fp32 accumulation that drops the bits below its running sum's last place per product or per pair of products, checked against the host's fixed tolerance of 1e-4 at a K 25 times that of E212's and E217's runs of these tiles. So R0's FAIL is read as the host's fixed tolerance failing at this depth for an all-positive repeated tile, not as a GEMM computed wrong. The records keep the check's counts only, not C's words, so neither the card's exact datapath nor C's values are established here, and nothing of this was tested on a card. One correction to the verifier's wording: its finding says every truncating model it tried gives p3a 0 of 256 at 800 k-tiles; by this lane's re-run that holds for the models that drop bits per product or per pair, not for those that round toward zero once per 4 or more products (19-256).

**What stands:** R0 reads FAIL on both arms by its registered words and labels every other verdict of each arm and the pooled ones; no point is dropped or re-chosen and nothing is re-scored. A later kit could scale the check's tolerance with K (for same-sign data, about K x 2^-25 of the sum), check pattern tiles only at small K, or print the sampled C words so that a desk can tell the datapath (REPORTED: a suggestion, not a change to E224).

**To reproduce** (from the top folder of the repository; Python 3 with numpy and an 80-bit long double, as on x86-64 Linux): `python3 docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry1-c1/posthoc-r0-check-e224.py --json <file>` prints the lines of `posthoc-r0-check-e224.txt` and writes the JSON of `posthoc-r0-check-e224.json` byte for byte (run so in a copy of the repository's files at main `c661275c` before this commit).

## 3. The session manifest and the scrub (verify-e224d's finding 2)

`session/MANIFEST.sha256` is the box's own list of the session directory's 562 files, as the box wrote it. In `session/`, `sha256sum -c MANIFEST.sha256` reads **347 OK and 215 FAILED, by design**: the 215 are the files the collection's scrub changed (the kit's [`collect_e224a.py`](../../../../tools/claims-v3/e224/collect_e224a.py), step 2: every form of the box's home path written as `~` and the box login as `<login>`, so that no committed file names either):
- 105 `runs/*/run.json`: each run's command line names the host, the kernel and the stop file under the box's home (the home masked in all 105);
- 108 `reads/etwho-*.out`: et-who's holder lines name the login (masked in all 108) and, in 107 of them, a command under the box's home (masked); the 108 `reads/etwho-*.err` beside them are the box's bytes;
- 2 `smoke/*/smoke.json` (s01 and s03): the home masked in both.

Every other file under `session/` is the box's bytes (347 lines OK). The README's "copied back exact and scrubbed" means this. Arm B's README note 13 states its one masked line in the same way, and E220 arm A's directory has the same form (229 of its 597 manifest lines, the same three kinds).

Checked at the desk (post hoc): the card lane's own copy of the box's session directory (kept at the desk, not committed, since it holds the box's home path and login) equals the box's bytes at all 562 manifest lines, and its manifest equals the committed one; this lane's own scrub of each of the 215 files gives the committed file byte for byte (215 of 215); the other 347 committed files equal the copy; no committed file of this directory holds the box's home path or the login; no et-who read holds another login's holder line; `SHA256SUMS` (the committed bytes) passes 577 of 577. `posthoc-manifest-scrub-e224a.txt` lists the 215 lines (kind, path, the box's sha256 as the manifest gives it, the committed sha256), so a reader can match each FAILED line to the list.

SPDX-License-Identifier: Apache-2.0
