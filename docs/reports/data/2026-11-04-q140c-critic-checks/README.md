# Q140(c): Q139's final critic's four desk checks, re-derived, and the corrections they support (post hoc, desk only)

*Wed 4 Nov 2026 (week 45), from about 00:25 PST, on the Intel. Desk only: no card, no device command, no ssh to a lab host, no
Modal, no archive access. **Everything here is post hoc**: every number it reads was committed before this lane began (lab
`1f434cc4`), and none of its arms was registered. Q139's final critic ran these four checks in its own scratch, unverified; this
lane wrote its own code from the committed files, printed its numbers, and only then read the critic's scripts and outputs to
compare (§ Against the critic). It answers the critic's open ranks **2 and 8** (check 1: aifoundry2's session term, and the
clock-and-voltage term), **rank 1** (check 2: what M9's named terms can buy), **rank 4** (check 3: a card nobody has measured) and
the 4.5 s heat figure the records quote (check 4), all under the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6** (a power model across
kinds), with check 4's interval on E154 under **items 9 and 8** (heat over minutes). Then it corrects the critic's faults 0–9 in
the lab records, on the kinds page and on the hubs; fault 10 (the archive's host named in public lab files) is the owner's call
and is left untouched, and fault 11 (pushed commit messages) cannot change.*

## Results first

**1. Q139(s)'s board exponent n = 2.28 fails out of sample on E160: it doubles the governed clock's error.** n = 2.28 was
committed in `c944ff99` at 05:25:25 PST on Tue 3 Nov, before E160 was registered (`2e016917`, 06:40:07) and ran (06:41:50–07:12:39),
and `c944ff99` is an ancestor of E160's registration. Through Q139(s)'s committed chain, imported unchanged
([`check1_exponent_e160.py`](check1_exponent_e160.py) → [`check1-exponent-e160.txt`](check1-exponent-e160.txt)): pool 6's frozen M7
D per tile, B, the cells' c, the cap W* and c_zeros refitted on E64/E80/E83 at each arm's s(f), scored on E160's registered groups
(governed = M8's frozen clock below 795 MHz, 17 tiles; pinned 31), measured − predicted. Arm A0 reproduces E160's own M7 columns to
0.048 MHz and 0.005 W on all 48 tiles.

| arm | s(800) | E160 governed clock, rms (mean) [95% over tiles] | governed board W | pinned clock | pinned board W | E143 governed clock (the session the exponent was read against) |
|---|---:|---|---|---|---|---|
| A0 M7 as frozen | 1.9052 | **4.89** (+2.82) [3.14, 6.32] | 1.105 (+0.81) | 3.88 | 1.718 | 6.64 (−4.97) |
| A2 V² from the reads, chain refitted | 1.8999 | 4.96 (+2.93) | 1.112 | 3.88 | 1.722 | 6.57 (−4.87) |
| **A5 n = 2.28** | 1.9965 | **10.50** (+9.47) [8.10, 12.65] | 1.121 | 3.91 | 1.872 | 4.82 (+1.46) |
| A5c n = 2.28, re-referred at E66's slope | 1.9965 | 10.45 (+9.42) | 1.109 | 3.90 | 1.792 | 4.83 (+1.44) |
| A4c the ramp slopes at E66's slope | 1.9946 | 10.73 (+9.72) | 1.087 | 3.90 | 1.856 | 4.93 (+1.90) |
| A3 n = 2.43 | 2.0503 | 13.99 (+13.14) | 1.144 | 3.94 | 2.000 | 6.93 (+5.01) |
| M8 as frozen (E160's own columns) | — | 6.72 (+5.17) | 1.391 | 3.89 | 1.726 | — |

- **The exponent moves an offset, not a shape.** It lowers every governed tile's predicted clock by 3.1–7.6 MHz (6.5 on average) in
  E160 and by 3.4–7.2 MHz (6.3) in E143. E143's governed tiles needed that shift (mean −4.87 MHz at n = 2); E160's need the opposite
  (+2.93). In every arm the two sessions' mean errors sit **7.8–8.1 MHz apart**, while each session's spread about its own mean is
  4.0–4.8 MHz and grows a little with n (E160: 4.00 at n = 2, 4.54 at 2.28). Over both sessions' 36 governed tiles the exponent is
  worse: **5.87 MHz at n = 2, 8.02 at n = 2.28**, 10.85 at 2.43. A paired bootstrap over E160's 17 governed tiles (one session) puts
  rms(A5) − rms(A2) at [+4.73, +6.31] MHz.
- **So the governed clock's missing piece is a session term, not a clock-voltage form.** With each session's offset known exactly,
  the governed clock would read at about its within-session spread, 4.0–4.4 MHz at n = 2: the edge of the critic's rank-2 line
  (4 MHz). The board is not moved by the exponent (1.09–1.14 W against 1.105), and its +0.81 W governed bias (M8's +1.14 W) is a
  level, rank 2's cap term.

**2. Pool 6 without the six tiles that carry the named misses reads 0.17–0.19 W rms in every model, and most of that drop is the
selection itself.** From E153's and E157's committed `power_rows` (the 30 priority-1 new kinds, anchors out; errors recomputed from
`measured` and `pred`, equal to the committed `error` to 0 W) ([`check2_pool6_named_misses.py`](check2_pool6_named_misses.py) →
[`check2-pool6-named-misses.txt`](check2-pool6-named-misses.txt)):

| card, model | 30 tiles [95% over tiles] | without the six | each model's own six worst removed | six random removed (mean of 20,000) | the six removed and a perfect offset on exponent-heavy fp32 |
|---|---|---|---|---|---|
| aifoundry3 M8 | 0.286 [0.199, 0.373] | **0.190** [0.140, 0.235] | 0.171 | 0.285 | 0.173 |
| aifoundry3 M7 | 0.252 [0.170, 0.338] | **0.174** | 0.150 | 0.251 | 0.162 |
| aifoundry3 M6 | 0.243 [0.176, 0.312] | **0.193** | 0.155 | 0.242 | 0.174 |
| card 1 M8 | 0.323 [0.197, 0.451] | **0.184** [0.126, 0.233] | 0.171 | 0.321 | 0.164 |
| card 1 M7 | 0.314 [0.182, 0.450] | **0.174** | 0.153 | 0.311 | 0.174 |
| card 1 M6 | 0.283 [0.169, 0.411] | **0.177** | 0.152 | 0.280 | 0.176 |

- The six are `fp32.b_onebit_b20_third` (a high single B bit on a 1/3 base word: −0.81 / −0.80 / −0.70 W on aifoundry3, −1.09 /
  −1.21 / −1.12 W on card 1, M8 / M7 / M6), `int8.a_zeros_b_lineflip` and `int8.b_line_zero_ff` (M8's near-whole-byte discount:
  +0.62 and +0.36 W in M8, +0.23 and +0.04 W in M7, −0.23 and −0.35 W in M6 on aifoundry3, so these two are M8's misses, not every
  model's), and `int8.bheld_bit1`, `bheld_bit4`, `bheld_bit7` (B held: −0.24 to −0.57 W, every model low).
- They overlap each model's own six worst in only 3–5 of 6, and removing each model's own six worst gives 0.150–0.171 W: any post
  hoc removal of the 20% worst tiles buys about this much. So 0.17–0.19 W is what fixing exactly those six tiles would leave, not a
  bound: a named term may mend unnamed tiles (`fp32.negzero_a_b_complement` +0.38 / +0.43 W and the real softmax tile −0.38 / −0.34 W
  in M8 sit outside the six) or hurt others, as M8's discount did.
- **The fourth named miss, exponent-heavy fp32, buys little more.** Its five priority-1 tiles read +0.17 / +0.18 W over M8 on the two
  cards, +0.14 / +0.18 W over M7 / M6 on aifoundry3 and +0.00 / +0.04 W over M7 / M6 on card 1; a perfect class offset on top of the six
  removed reads 0.162–0.176 W.
- **The classes extend to priority 2.** Over all 44 non-anchor new kinds the six removed leave 0.21–0.31 W, because
  `int8.b_line_55_aa` (whole-line, +1.31 / +1.36 W in M8) and `fp16.b_onebit_b6_third` (a single B bit on a 1/3 base word, −0.46 to
  −0.55 W) are in the same classes; without those two as well, 0.18–0.21 W.
- Readout noise on D within one session (rms over tiles of sd over passes / √n): aifoundry3 0.035 / 0.035 / 0.052 W, card 1
  0.102 / 0.049 / 0.088 W (fp32 / fp16 / int8). The 0.17–0.19 W left is model error, not readout; on card 1 it also meets the
  0.1–0.2 W day-to-day floor (E157 K1).
- Per format, the registered 30 (M8; bootstrap over tiles, post hoc): aifoundry3 fp32 0.330 [0.19, 0.47] W, fp16 0.125 [0.07, 0.17],
  int8 0.296 [0.17, 0.40]; card 1 0.386 [0.17, 0.59], 0.098 [0.06, 0.13], 0.327 [0.19, 0.46]. As shares of the format's mean kind
  (13.8 / 17.9 / 4.9 W on aifoundry3, 13.2 / 17.3 / 4.8 W on card 1): **2.4% / 0.7% / 6.0% and 2.9% / 0.6% / 6.9%** (M7 and M6: fp32
  2.3–3.0%, int8 4.1–6.0%). A bootstrap end moves about 0.01 W with its seed at 6–12 tiles.

**3. Card 1's float scale from the two random anchors per format lands within 0.15% of pool 6's median; int8's within its own
noise.** Each card's committed primary on Q139(u)'s footing, E78's tile and pool 6's per format, D(card 1) / D(aifoundry3)
([`check3_anchor_card_scale.py`](check3_anchor_card_scale.py) → [`check3-anchor-card-scale.txt`](check3-anchor-card-scale.txt)):

| format | E78's anchor | pool 6's anchor | the anchors' median (rank 4's proposed rule) | pool 6's median (E157's X1 / X2) | anchors against the pool |
|---|---|---|---|---|---|
| floats (fp32, fp16) | 0.9624 ± 0.0014, 0.9634 ± 0.0025 | 0.9606, 0.9611 | **0.9618** (mean 0.9619 ± 0.0010) | 0.9632 [0.9613, 0.9659] over 25 tiles | **−0.15%** (mean −0.13%) |
| int8 | 0.9597 ± 0.0204 | 0.9563 | **0.9580** (± 0.0144) | 0.9681 [0.9534, 0.9783] over 16 tiles | **−1.04%** |

- The ± are each card's sd over its passes over √n, combined on the ratio (E78's tiles; pool 6's anchors carry pass means only, so
  theirs is taken as the same relative error, an assumption). **Card 1's int8 anchor read 7.08, 6.80 and 6.58 W over its three
  passes (3.6% sd)**, so the int8 scale from two anchors carries about ±1.5% of its own: the −1.0% is inside it, and a 2% line for
  int8 is about 1.3 of its standard errors.
- Carried by M8's 0.9616, a measured kind errs **0.72% rms per float tile** (25 tiles at D ≥ 5 W on both cards; worst
  `fp32.b_onebit_b20_third` −2.5%) and **1.97% per int8 tile** (16 at D ≥ 1 W; worst `int8.a_word_zero_one` −4.6%); about the
  anchors' own scale, 0.72% and 2.07%. Both tile sets and every ratio equal E157's registered `scored-e153.json` X1 / X2 to 2e-16.
- On this one card pair and session pair, rank 4's proposed rule (within 1% of the pool's median for floats, 2% for int8) is met
  by both formats.

**4. Over a 4.5 s run the rise from the bits beats a constant on the floats; on int8 it does so only through its two lowest-power
tiles on aifoundry3, and inside the readout floor on card 1.** From E153's and E157's committed `heat_rows` (the 30 priority-1 new
kinds) ([`check4_heat_constant.py`](check4_heat_constant.py) → [`check4-heat-constant.txt`](check4-heat-constant.txt)), °C rms:

| card | format (tiles) | M8 / M7 / M6 | a constant per format (its rises' sd) | the constant left one out | readout floor (rms of sd / √n) |
|---|---|---|---|---|---|
| aifoundry3 | fp32 (12) | **0.098** / 0.100 / 0.106 | 0.596 | 0.650 | 0.112 |
| | fp16 (6) | **0.106** / 0.103 / 0.096 | 0.277 | 0.333 | 0.110 |
| | int8 (12) | **0.128** / 0.126 / 0.122 | 0.209 | 0.228 | 0.090 |
| card 1 | fp32 (12) | **0.180** / 0.173 / 0.178 | 0.678 | 0.739 | 0.171 |
| | fp16 (6) | **0.183** / 0.182 / 0.178 | 0.332 | 0.399 | 0.133 |
| | int8 (12) | **0.123** / 0.127 / 0.132 | 0.283 | 0.308 | 0.198 |

- **aifoundry3's int8:** 10 of its 12 rises read exactly 1.00 °C. On those ten M8 errs 0.130 °C (M7 0.124, M6 0.114) against the
  constant 1.00's 0; its whole gain is the two lowest-power tiles, `int8.a_zeros_b_lineflip` (0.28 W, 0.25 °C: M8 −0.01, a constant
  −0.67) and `int8.a_word_zero_one` (2.74 W, 0.81 °C: +0.17 against −0.11).
- **Card 1's int8:** only 5 of 12 read exactly 1.00 °C; without the same two tiles M8 reads the other ten to 0.105 °C against a
  constant's 0.148, a gain inside the 0.198 °C readout floor: not resolved, rather than absent.
- **E154's heat over minutes, for the record's interval:** its four plateau errors (+0.024, −0.418, +0.492, +0.360 °C) give 0.370 °C
  rms, and a 95% interval on the sigma of **0.22–1.06 °C** (chi-square at 4 degrees of freedom, zero-mean errors assumed).

## Against the critic

Every number the critic quoted reproduces: check 1's arms to the second decimal (A0 4.89 / +2.82 / 1.105, A2 4.96 / 1.112, A5 10.50
/ +9.47 / 1.121, A5c 10.45, A3 13.99, pinned clock 3.88–3.94 MHz, pinned board 1.72 → 1.87 W at 2.28), check 2's 24-tile figures and
readout noise to the third, check 3's ratios to the fourth (0.9624 / 0.9606 / 0.9634 / 0.9611; 0.9597 / 0.9563; 0.72% and 1.97%),
check 4's constants and M8 rms to the third, and E154's interval. Compared only after the numbers above were printed: the critic's
`e160_exponent.py` / `.json`, `pool6_floor.py` / `.json` and `pool6_checks.py` / `.json` (its scratch, never committed). Where this
lane reads them differently:

- **Check 2's 0.17–0.19 W is not "the most M9's named terms can buy".** Each model's own six worst tiles removed give 0.150–0.171 W,
  so the figure is mostly what dropping a fifth of the tiles post hoc gives, and a term could mend tiles outside the six. Quote it as
  "with the six tiles that carry the named misses taken out, every model reads the other 24 at 0.17–0.19 W (post hoc)". Two of the
  six, the near-whole-byte pair, are M8's misses only: M7 reads them to +0.23 / +0.04 W on aifoundry3.
- **Check 4's int8 statement holds on aifoundry3 only.** On card 1 int8 edges a constant on the ten tiles left (0.105 against
  0.148 °C) inside a 0.20 °C readout floor. "A skill on the floats; int8's rises are whole-degree readings" stands for both cards.
- **Check 3's int8 "about −1%" is −1.0% ± 1.5%:** card 1's int8 anchor spread 3.6% over its passes. The float figure the critic gave
  as −0.14% is −0.13% for the anchors' mean unrounded and −0.15% for their median, the form rank 4's rule proposes.
- **Check 1 agrees, with one addition:** the two sessions' governed means sit 7.8–8.1 MHz apart in every arm while the spread inside
  each session does not move with n, so no clock-voltage form can remove the gap; the exponent buys E143 its offset and charges E160
  the same amount.

## What it does to predicting power and heat

- **The clock-and-voltage term, tested out of sample (check 1).** Term: the board exponent n in s(f) = (V_f/V_600)^n f/600 for
  aifoundry2's governed bursts. Before (M7 as frozen) on E160's governed clock: 4.89 MHz rms; after, n = 2.28: **10.50 MHz** (mean
  +9.47); s(f) at n = 2 from the reads: 4.96. Pooled over E143 and E160, 36 governed tiles: 5.87 MHz at n = 2 against 8.02 at 2.28.
  The exponent does not carry: quote s(f) from the reads at n = 2, keep the exponent out of M9, and carry a session term instead
  (rank 2; Q140(l) is told not to use 2.28). The board moves by at most about 0.15 W (the pinned board, 1.72 → 1.87 W at 2.28), the pinned clock by at most 0.06 MHz,
  and the die's rise by about 0.01 °C (0.660 → 0.655 °C over the 48 tiles).
- **Power of a new kind, what the named terms can buy (check 2).** Before: 0.24–0.32 W rms over pool 6's 30 kinds per card and model.
  With the six named-miss tiles removed: 0.17–0.19 W; with a perfect exponent-class offset too, 0.16–0.18 W; with each model's own
  worst six removed instead, 0.15–0.17 W. So about a third of the error sits in the named classes' tiles, and M9's gain should be
  scored on unaimed kinds as well (rank 1's rule).
- **A card nobody has measured (check 3).** No cheap read lands within 1% held out (E153: the closest −1.7%); two random anchors per
  format, paired on both 600 MHz cards, give card 1's float scale to −0.15% of pool 6's median and int8's to −1.0% ± 1.5%. A measured
  kind carried by the card term errs 0.72% per float tile and 1.97% per int8 tile. On one card pair and one session pair.
- **Heat over 4.5 s (check 4).** M7's heat law, carried in M8, against a per-format constant: aifoundry3 0.098 / 0.106 / 0.128 °C
  against 0.596 / 0.277 / 0.209, card 1 0.180 / 0.183 / 0.123 against 0.678 / 0.332 / 0.283. The skill is the floats'; int8's rises
  are whole-degree readings. E154's 0.370 °C over minutes carries a 95% interval of 0.22–1.06 °C on its sigma.
- No frozen number, band, prediction, rule or verdict changes. What changes is how the records and pages quote these errors.

## The corrections this supports (made by this lane)

The critic listed one moderate fault, nine minor and two carried (`result.json` `faults_found` 0–11; its `result.md` numbers them
1–12). Faults 0–9 are corrected below, each as a dated correction in the lab records (dated notes beside the text, the text left as
it was, or a cell that carries a dated clause), on the kinds page (exact replacements in section 11 and the page's top tile, with a
dated line in the How-well section and in Sources) and in the hubs that quoted the same text (a new Fix entry at the top of each
changed hub's week 45; no Log entry edited). Fault 10, the archive's host named in seven public lab files, is the owner's call and
stays on the private notes' list, untouched. Fault 11, pushed commit messages, cannot change.

0. **(Moderate) The exponent's gain.** The kinds page's clock-and-voltage row, item 6 and the closed-list bullet; 05-claims' rows
   "The clock/voltage term" and "The board's exponent (corrected)", 02's Q139 row and 03's Q139(s) entry; Q139(s)'s README (a dated
   note): on E160, run after it, n = 2.28 reads the governed clock 10.5 MHz against M7's 4.9, so its E143 gain was that session's
   offset (check 1).
1. **"From the bits" is not like for like.** aifoundry3's arm runs the chain on the session's realized dispatch records; E161's
   assumed continuous work, and at the kernel duty (0.970) G1Q reads −0.39 °C beside its registered −0.90. The page's top tile, its
   two heat tiles, the heat chart's head, item 9, the section's opening and "So:"; 05's "So:" and 02's Q139 row; the Horace Hub's
   "Where it stands now", its Q139 paragraph and Levels stop 3; the projects tracker's Horace row.
2. **aifoundry2's burst figures and their offsets.** "So:" and the burst row: where the governor acts (17 of 48 tiles), the clock's
   error mostly a session offset whose sign changed (E143 −5.0, E160 +5.2 MHz), the board's a +1.1 W bias both sessions share; all
   48 read 5.1 MHz and 1.6 W; the brackets are over tiles inside one session.
3. **The share of a kind's watts.** "So:" (page) and 05's "So:": 2.4–2.9% of an fp32 kind's watts, under 1% of fp16's, 6–7% of
   int8's (M8), not "about 1–2% of a float kind's" and "4–10% of an int8 kind's".
4. **The intervals.** Pool 6's per-format and 30-tile bootstrap intervals beside its table and its tile; E154's 0.22–1.06 °C beside
   every quote of its 0.37 °C (the page's tiles, the heat-over-minutes row, item 9, "So:"; 05's "So:").
5. **"0.69 °C rms over the two".** 05's governed heat row and E161's README (a dated note): G1Q, −0.90 °C, is the heat-from-the-bits
   figure; G2Q is the trip regime and its clock, its plateau 0.40 °C under the trip rule.
6. **A card nobody has measured.** The page's row, item 6 and the pool-6 paragraph; 05's row: card 1's +0.78% / −0.74% test the
   zeros-level form on new kinds of a card already in the model; rank 5's own test is E153's held-out aifoundry3, where no read lands
   within 1%; an unmeasured card carries about 2–5%; post hoc, paired anchors give card 1's float scale to 0.15% (check 3).
7. **The check of C's D half.** The page's closed-list bullet: the D half passes on aifoundry3 and fails on card 1, which repeats D
   only to 0.1–0.2 W between days (E157 K1: 3 of 6 within 0.05 W).
8. **"One reduction footing ... applied to every row and test".** The page's closed-list bullet and the Horace Hub's quote of it:
   applied to M8's training rows and its blind tests (E152 registered its own session fit, E155 E142's frozen slope, and E156
   carried the footing as an arm).
9. **The 4.5 s heat figure without its caveat.** 02's Q139 row, the findings README's Q139 paragraph and 05's item-6 row (dated
   notes): a skill on the floats; int8's rises are whole-degree readings (check 4).

## Files

- `check1_exponent_e160.py` → `check1-exponent-e160.json`, `check1-exponent-e160.txt` (numpy; imports Q139(s)'s
  `fit_clock_voltage.py` and `corrections-numbers.py` unchanged, bytecode off).
- `check2_pool6_named_misses.py` → `check2-pool6-named-misses.json`, `.txt` (standard library).
- `check3_anchor_card_scale.py` → `check3-anchor-card-scale.json`, `.txt` (standard library).
- `check4_heat_constant.py` → `check4-heat-constant.json`, `.txt` (standard library).
- Rerun from the repository root, each in a few seconds: `python3 -I -B docs/reports/data/2026-11-04-q140c-critic-checks/<script>.py
  . --out docs/reports/data/2026-11-04-q140c-critic-checks/<name>.json > docs/reports/data/2026-11-04-q140c-critic-checks/<name>.txt`
  (check 1 needs a python with numpy). The bootstraps use fixed seeds.

## Device commands sent

None. This lane opened no device node, took no card lock and ran nothing on a lab host. It read committed files only.
