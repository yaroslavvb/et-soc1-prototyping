# E213, dated note 3 (arm B's data directory): the pooled rules HP1-HP5, made by the frozen scorer on both arms' committed data in one input file - MM1-v3 BETTER than MM1-v2 on all five (wall cycles 86/13/16, counter's mean 82/25/8, seconds 85/13/17, J over idle given the seconds 70/13/41, with the seconds forecast 67/15/42), with verify-e213bd's desk count beside

*Wed 18 Nov 2026 (week 47), PST; written at about 16:56 PST by Q219's lane `scores-e213b`, after both arms' data commits (arm A `c69a12aa`, 07:23:29 PST, aifoundry3 card 0; arm B `b0c727c5`, 15:49:38 PST, aifoundry1 card 1), arm A's scores (`01283623`, 08:48:06 PST: its dated note 2), arm B's data verifier (`verify-e213bd`, HOLDS WITH FIXES), arm B's dated note 1 (`3e1d1d43`) and arm B's dated note 2 (this directory's `README.md.dated-note-2.md`, listed with arm B's scorer outputs in `SHA256SUMS-note2`, sha256 `33582170aba3df7f6919bf1d249564bbcdb17982374f1f9321fa91d23362bf5b`). It adds new files only, in arm B's data directory: no committed file, datum, forecast, rule, band, label or scorer is changed. Labels: **registered** (E213.md section 7's pooled rules and its scorer), **measured** (both directories' committed records), **blind** (both arms' forecasts, frozen before either arm's first card command: arm A's in MM1-v3's land `b1493082`, arm B's by the registration `291c8201`), **REPORTED** (never a verdict), **post hoc**, **desk** (under `/usr/bin/python3` 3.12.3).*

**The words.** E213's frozen scorer (`score_e213.py`, registered sha256 `a4eece29...`), run with step 13's form of arguments on one file holding both arms' committed data, unchanged, and both arms' committed labels, printed: **HP1 MM1-v3 BETTER** (MM1-v3 / MM1-v2 / ties 86/13/16, p 2.29e-14), **HP2 MM1-v3 BETTER** (82/25/8, p 2.91e-08), **HP3 MM1-v3 BETTER** (85/13/17, p 3.98e-14), **HP4 MM1-v3 BETTER** (70/13/41, p 1.33e-10), **HP5 MM1-v3 BETTER** (67/15/42, p 5.26e-09). In the same output each arm's verdicts are exactly the ones its own step 13 printed (arm A: R0, S6, T1-T3 and E1-E3 PASS, E4 FAIL 78/87, H1-H5 MM1-v3 BETTER; arm B: R0, S6, T1-T3 and E1-E4 PASS, H1, H3-H5 MM1-v3 BETTER, H2 NOT DECIDED): pooling changes no arm's verdict. With R0 and S6 PASS in both arms, no pooled verdict carries a label.

**MM1-v3 against MM1-v2 over both arms, rms of the relative error** (desk arithmetic, REPORTED, blind): the wall cycles 4.27% against 8.90% (115 cases), the counter's mean 5.68% against 9.10%, seconds 4.31% against 8.96%; J over idle given the seconds 15.36% (103 points at 3 W and above) against 16.36% (102), and 3.91% against 7.34% without the seven gemmLnc points (post hoc); J with the card at rest given the seconds 5.86% against 6.16%, with the seconds forecast 6.76% against 9.85%; W over idle at arm A's 22 watts points 0.294 W against 0.362 W given the seconds.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `pool_e213.py` | 7,772 | `f63c21d9e360cea0d70694a7020a67c6bc9bdb4848290810e408bb9b328f434a` | builds the pooled input: each arm's committed data and labels, checked against its directory's `SHA256SUMS` and the pins in the script, copied unchanged into one file each, read back (Python's own modules only); `check` re-builds and compares |
| `pool-e213.txt` | 1,400 | `ea67b971e7a53434eef6f795b54ce3cc3fcdfc3fd09d67b63a5e5336dd3fe787` | its printout when it built the two files below |
| `pooled-data-e213-AB.json` | 268,421 | `600270764674b13d403d68fa4d4695f38427c3b8ec1bb69ee2e6d03a03efa0f3` | the scorer's input: `{"arms": {"A": <arm A's committed ARM>, "B": <arm B's committed ARM>}, "experiment", "reducer"}` and `pooled_from` naming the inputs (the scorer reads only `arms`) |
| `pooled-labels-e213-AB.json` | 130 | `f758f1e5050a8bf38d60baa67228b5e531ca573302d7c372303728b20724d3b0` | both arms' committed step-6n labels (none labelled) |
| `scores-e213-pooled.json` | 258,448 | `3b0c1bae797542c9a1f16ec4f117f97cfeb29a0b72311f59bbe08b1829daecad` | the frozen scorer's output on that input: both arms' verdicts, counts, cells and readings, and the pooled HP1-HP5 |
| `scores-e213-pooled.txt` | 2,058 | `6bb86ef3ff14b474a1940587551250af2a4b40fe0e115192d7e7e01411b83e73` | its printed lines |
| `README.md.dated-note-3.md` | (this note) | listed in `SHA256SUMS-note3` | this dated note |
| `SHA256SUMS-note3` | 8 lines | (not listed in itself) | the seven files above and `SHA256SUMS-note2` |

## 2. How the pooled verdicts were made (desk checks of code)

- **The input.** The scorer reads one data file, and step 13 gave each arm's own file to it, so each arm's output printed HP1-HP5 NO DATA (the kit's step text: "the pooled HP1-HP5 NO DATA unless one data file holds both arms: the scores lane scores the pooled rules once both arms are committed"). `pool_e213.py` read `docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json` (sha256 `d53caacb...`); `docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/labels-e213.json` (sha256 `f664a2ce...`); `docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/data-e213.json` (sha256 `93fe3e7e...`); `docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/labels-e213.json` (sha256 `d801cae7...`), each equal to its pin and to its directory's `SHA256SUMS` line, and each one blob at its data commit and at HEAD. It copied each arm's `ARM` object unchanged into `pooled-data-e213-AB.json` and each arm's labels into `pooled-labels-e213-AB.json`, in the scorer's own dump form, and read both back: each arm equals its input arm, value for value. Its `check` mode, run after, rebuilt both files byte for byte.
- **The run.** In a tree taken from the commits' objects (the scorer, its nine pinned inputs, both arms' `data-e213.json`, `labels-e213.json` and `SHA256SUMS`, each one blob at its data commit and at HEAD; no bytecode cache), with `pool_e213.py` beside arm B's data: `/usr/bin/python3 -I -B tools/claims-v3/e213/score_e213.py docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/pooled-data-e213-AB.json --labels docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/pooled-labels-e213-AB.json --out scores-e213-pooled.json`, its printed lines captured as `scores-e213-pooled.txt` (rc 0). A second run under an audit hook wrote the same two files byte for byte, and opened 12 files of the tree (the scorer, its nine pinned inputs and the two pooled input files), 33 standard-library files and nothing else but its own outputs.
- **The arms in the output.** Its arm A equals arm A's committed `scores-e213-A.json` (`01283623`) and its arm B equals this directory's `scores-e213-B.json` (dated note 2), value for value: every verdict, count, cell, measured point, head-to-head count, bootstrap and REPORTED reading. The scorer scores each arm alone (`score()`), so the two one-arm runs and this one agree by construction, and they do.
- **The pooled rules.** HP1-HP5 are the scorer's `decide()` over arm A's d values and arm B's together (`allh`), each case or point with its own arm's tie: 0.005 in ln for cycles and for seconds in both arms; for joules 0.01 (arm A) and 0.015 (arm B); 0.05 W at arm A's 22 watts points. Called here as `score()` calls it, `decide()` over the 115 and 124 d values gives the JSON's counts and p; the counts are arm A's plus arm B's own head-to-head counts; the bootstrap intervals (seeded `E213|bootstrap|pooled|<rule>`) equal the JSON's.
- **verify-e213bd's desk count beside.** The verifier pooled both arms with its own code before this lane ran (its `pooled-e213.json`: arm A by its own reader, which it found equal to `01283623` in every verdict, count and head-to-head): HP1 86/13/16, HP2 82/25/8, HP3 85/13/17, HP4 70/13/41, HP5 67/15/42, all MM1-v3 BETTER, with the same p values: equal to the frozen scorer's in every count.

## 3. The rules: their registered words, the verdicts, verify-e213bd beside

The scorer's printed lines (`scores-e213-pooled.txt`, verbatim):

```
E213 scorer (score_e213.py), the registered verdicts:
ARM A: R0 PASS; S6 PASS; T1 PASS 81/84; T2 PASS 82/84; T3 PASS 81/84; E1 PASS 82/87; E2 PASS 82/87; E3 PASS 81/87; E4 FAIL 78/87
  H1 MM1-v3 BETTER (v3 65 / v2 6 / ties 13; p 1.3321308760808536e-13); REPORTED bootstrap MM1-v3 BETTER [0.03143757864188094, 0.04940573454148727]
  H2 MM1-v3 BETTER (v3 62 / v2 15 / ties 7; p 6.083249930070788e-08); REPORTED bootstrap MM1-v3 BETTER [0.020689999233477266, 0.04104450826532456]
  H3 MM1-v3 BETTER (v3 65 / v2 6 / ties 13; p 1.3321308760808536e-13); REPORTED bootstrap MM1-v3 BETTER [0.031172052990476016, 0.04896998061010384]
  H4 MM1-v3 BETTER (v3 50 / v2 9 / ties 28; p 5.264832102225281e-08); REPORTED bootstrap MM1-v3 BETTER [0.010385878829239192, 0.027159088207662253]
  H5 MM1-v3 BETTER (v3 45 / v2 11 / ties 31; p 5.37831811014966e-06); REPORTED bootstrap MM1-v3 BETTER [0.011506328620352026, 0.029922849268087835]
ARM B: R0 PASS; S6 PASS; T1 PASS 31/31; T2 PASS 31/31; T3 PASS 31/31; E1 PASS 36/38; E2 PASS 36/38; E3 PASS 36/38; E4 PASS 36/38
  H1 MM1-v3 BETTER (v3 21 / v2 7 / ties 3; p 0.012540951371192932); REPORTED bootstrap MM1-v3 BETTER [0.01189045941704969, 0.03500549371741206]
  H2 NOT DECIDED (v3 20 / v2 10 / ties 1; p 0.09873714670538902); REPORTED bootstrap MM1-v3 BETTER [0.002858401163783083, 0.029698505296708345]
  H3 MM1-v3 BETTER (v3 20 / v2 7 / ties 4; p 0.0191572904586792); REPORTED bootstrap MM1-v3 BETTER [0.011904402025974517, 0.03455362435482624]
  H4 MM1-v3 BETTER (v3 20 / v2 4 / ties 13; p 0.001543879508972168); REPORTED bootstrap MM1-v3 BETTER [0.013974032138539238, 0.039567420752530336]
  H5 MM1-v3 BETTER (v3 22 / v2 4 / ties 11; p 0.0005335211753845215); REPORTED bootstrap MM1-v3 BETTER [0.015283043926518173, 0.04023316284254403]
POOLED: HP1 MM1-v3 BETTER (86/13/16, p 2.288987396986294e-14); HP2 MM1-v3 BETTER (82/25/8, p 2.908096741300926e-08); HP3 MM1-v3 BETTER (85/13/17, p 3.9846743192350404e-14); HP4 MM1-v3 BETTER (70/13/41, p 1.3333193226298718e-10); HP5 MM1-v3 BETTER (67/15/42, p 5.257316976900643e-09)
```

**The registered words** (E213.md 7): "H1-H5 pooled over both arms, each case or point once with its own arm's tie; NO DATA unless both arms scored", registered over "117 / 117 / 117 / 126 / 126" cases and points; each decided as H1-H5 are: "Decided by the exact two-sided sign test at alpha 0.05 on the untied cases: MM1-v3 BETTER if p < 0.05 and it is closer in more cases than not; MM1-v2 BETTER if p < 0.05 the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none." Both arms scored (arm A 84 cases and 87 points; arm B 31 cases and 37 points priced by both models), so the pooled rules are read over 115 cases and 124 points: arm B's k38 and k39 have no run ("a point or case with no run is NO DATA, never a failure").

| rule | the registered words (E213.md 7) | registered over | scored over (A + B) | MM1-v3 closer | MM1-v2 closer | ties | p (exact, two-sided) | the scorer | arm A (its note 2) | arm B (note 2) | verify-e213bd's desk count |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **HP1** | H1 pooled: cycles an op, the wall, per case | 117 | 115 (84 + 31) | 86 | 13 | 16 | 2.29e-14 | **MM1-v3 BETTER** | MM1-v3 BETTER 65/6/13 | MM1-v3 BETTER 21/7/3 | MM1-v3 BETTER 86/13/16 (p 2.29e-14) |
| **HP2** | H2 pooled: cycles an op, the counter's mean, per case | 117 | 115 (84 + 31) | 82 | 25 | 8 | 2.91e-08 | **MM1-v3 BETTER** | MM1-v3 BETTER 62/15/7 | NOT DECIDED 20/10/1 | MM1-v3 BETTER 82/25/8 (p 2.91e-08) |
| **HP3** | H3 pooled: seconds a GEMM, per case | 117 | 115 (84 + 31) | 85 | 13 | 17 | 3.98e-14 | **MM1-v3 BETTER** | MM1-v3 BETTER 65/6/13 | MM1-v3 BETTER 20/7/4 | MM1-v3 BETTER 85/13/17 (p 3.98e-14) |
| **HP4** | H4 pooled: J over idle given the measured seconds, per point both price | 126 | 124 (87 + 37) | 70 | 13 | 41 | 1.33e-10 | **MM1-v3 BETTER** | MM1-v3 BETTER 50/9/28 | MM1-v3 BETTER 20/4/13 | MM1-v3 BETTER 70/13/41 (p 1.33e-10) |
| **HP5** | H5 pooled: J over idle with the seconds forecast, per point both price | 126 | 124 (87 + 37) | 67 | 15 | 42 | 5.26e-09 | **MM1-v3 BETTER** | MM1-v3 BETTER 45/11/31 | MM1-v3 BETTER 22/4/11 | MM1-v3 BETTER 67/15/42 (p 5.26e-09) |

## 4. REPORTED beside the verdicts (never verdicts)

**The bootstrap 95% interval of the mean d, pooled** (the scorer's; B = 10,000; over the cases, or the points at 3 W and above for HP4 and HP5): HP1 [+0.0285, +0.0432] (mean d +0.0356, n 115, MM1-v3 BETTER); HP2 [+0.0185, +0.0353] (mean d +0.0269, n 115, MM1-v3 BETTER); HP3 [+0.0282, +0.0432] (mean d +0.0356, n 115, MM1-v3 BETTER); HP4 [+0.0144, +0.0287] (mean d +0.0214, n 102, MM1-v3 BETTER); HP5 [+0.0155, +0.0304] (mean d +0.0228, n 102, MM1-v3 BETTER).

**MM1-v3 and MM1-v2 over both arms, rms and bias** (this lane's arithmetic on both directories' measured points, through the committed scorer outputs' `measured` blocks, and the frozen CSV columns of both arms, read with Python's csv module; each arm's half equal to its verifier's figures: arm A's to verify-e213d's, arm B's to verify-e213bd's; relative error unless marked):

| quantity | MM1-v3 both arms (bias; n) | MM1-v2 both arms (bias; n) | MM1-v3 arm A | MM1-v2 arm A | MM1-v3 arm B | MM1-v2 arm B |
|---|---|---|---|---|---|---|
| wall cycles an op, per case | 4.27% (+1.19%; n 115) | 8.90% (+4.23%; n 115) | 4.61% (n 84) | 9.79% (n 84) | 3.19% (n 31) | 5.84% (n 31) |
| counter's mean, per case | 5.68% (+1.17%; n 115) | 9.10% (+4.16%; n 115) | 6.20% (n 84) | 10.03% (n 84) | 3.91% (n 31) | 5.88% (n 31) |
| seconds a GEMM, per case | 4.31% (+1.29%; n 115) | 8.96% (+4.33%; n 115) | 4.66% (n 84) | 9.86% (n 84) | 3.17% (n 31) | 5.87% (n 31) |
| J over idle given the seconds (3 W and above) | 15.36% (+1.77%; n 103) | 16.36% (+4.24%; n 102) | 14.11% (n 65) | 14.73% (n 65) | 17.29% (n 38) | 18.88% (n 37) |
| J over idle with the seconds forecast (3 W and above) | 15.35% (+2.00%; n 103) | 16.29% (+4.87%; n 102) | 14.14% (n 65) | 14.86% (n 65) | 17.24% (n 38) | 18.54% (n 37) |
| W over idle given the seconds (watts points) | 0.294 W (+0.205 W; n 22) | 0.362 W (+0.292 W; n 22) | 0.294 W (n 22) | 0.362 W (n 22) | - | - |
| J with the card at rest given the seconds | 5.86% (+0.97%; n 125) | 6.16% (+1.75%; n 124) | 5.29% (n 87) | 5.48% (n 87) | 7.00% (n 38) | 7.51% (n 37) |
| J with the card at rest with the seconds forecast | 6.76% (+2.22%; n 125) | 9.85% (+5.71%; n 124) | 6.60% (n 87) | 10.58% (n 87) | 7.10% (n 38) | 7.87% (n 37) |
| post hoc: J over idle given the seconds without the gemmLnc points | 3.91% (-1.99%; n 96) | 7.34% (+0.69%; n 95) | 3.92% (n 60) | 7.15% (n 60) | 3.87% (n 36) | 7.65% (n 35) |
| post hoc: J over idle with the seconds forecast without the gemmLnc points | 3.72% (-1.76%; n 96) | 7.55% (+1.40%; n 95) | 3.79% (n 60) | 7.55% (n 60) | 3.61% (n 36) | 7.54% (n 35) |

The gemmLnc points are arm A's a075, a079, a082, a086, a087 and arm B's k37, k40; arm B has no watts point. MM1-v2 prices no sparse50 (arm B's k34), so its energy counts run one under MM1-v3's.

## 5. Dated clauses (Wed 18 Nov 2026)

1. **The pooled rules carry the day's comparison, as registered.** E213.md 7, before the data: "on arm B alone it is weak, 0.24-0.50"; "pooled over both arms it is 0.91-0.98"; E213.md 8: "Arm B's own head-to-head is weak (its power above); the pooled rules carry the comparison, and they need both arms." Both arms ran and scored (arm B short of k38 and k39), and the five pooled rules read MM1-v3 BETTER, HP2 among them, where arm B's own H2 did not decide (arm B's note 2, clause 4).
2. **Correlated errors** (E213.md 7 and 8): "With errors correlated within a family or across a day both tests' false-winner rates rise" above the simulated ones. Pooling two days on two cards adds cases but not independence within a family; the bootstrap intervals and each arm's family check (each arm's note 2) are REPORTED beside, never verdicts.
3. **Pooling changes no arm's verdict.** Arm A's E4 FAIL (78 of 87, one point short) and its other verdicts, and arm B's verdicts (H2 NOT DECIDED among them), stand as each arm's step 13 printed them; the pooled file's arms equal both one-arm outputs value for value (section 2).
4. **The two cards' gemmLnc energy.** Seven of the pooled energy points are gemmLnc (five in arm A, two in arm B); their measured J over idle runs 1.15-1.80 times MM1-v3's J given the measured seconds (arm A 1.15-1.68, arm B 1.66-1.80), on both cards, while their cycles hold. They stay in every pooled rule as registered (post hoc rms without them in section 4); MM1-v3.1's declaration (`7375bc9c`) names the item.
5. **No other arm, no other test.** The pooled rules are the only rules over both arms (E213.md 7); no band and no other verdict is pooled, and nothing here re-scores either arm.

## 6. NOT RUN

- verify-e213bd's code: its desk counts were read and compared, not re-run.
- Independent code for the pooled bootstrap intervals (they are the frozen scorer's, re-run).
- Any read of aifoundry1's or aifoundry3's disks.

## What this note changes

Nothing measured, forecast, registered or scored per arm. It adds the pooled verdicts the registration names and the eight new files of section 1 (with this note and `SHA256SUMS-note3`, which lists the other seven and `SHA256SUMS-note2`). Every committed file stands as committed.

SPDX-License-Identifier: Apache-2.0
