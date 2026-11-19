# E215, the pooled rules over both arms, dated note 3 of arm B's data directory: the frozen scorer on one input built from both arms' committed data - registered HP1-HP3 NOT DECIDED (13/19/18), HP4 and HP5 TOO FEW; post hoc (apart) HP1-HP3 MM1-v3 BETTER; with verify-e215d's pooled readings beside

*Thu 19 Nov 2026 (week 47), PST; written at about 15:50 PST by Q224's lane `scores-e215`, after both arms' data commits (arm A `8355db15`, 13:00:32 PST, aifoundry3 card 0; arm B `4f648f24`, 14:14:38 PST, aifoundry1 card 1), after `verify-e215d` (HOLDS WITH FIXES; it computed the pooled rules two ways, by its own code and by the frozen scorer on both committed data files, and both agree), after `fix-e215d` (`2b0c8814`) and after dated note 2 of this directory (arm B's scorer output, committed just before this note). It adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed. Labels as in note 2: **registered**, **measured**, **blind** (every forecast frozen before its arm's first card command), **REPORTED**, **post hoc**, **desk**.*

**The words.** E215.md 7 registers HP1-HP5: "H1-H5 pooled over both arms per group, each case or point once with its own arm's tie; NO DATA unless both arms scored that group". "Decided by the exact two-sided sign test at alpha 0.05 on the untied cases: MM1-v3.1 BETTER if p < 0.05 and it is closer in more cases than not; MM1-v3 BETTER if p < 0.05 the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none." The frozen scorer reads one data file and scores HP1-HP5 only when it holds both arms; each arm's committed `data-e215.json` holds one arm, so each arm's step 13 printed them NO DATA. `pool_e215.py` (in this directory) copies each arm's committed ARM object unchanged into one file, `pooled-data-e215-AB.json`, and both arms' committed labels into `pooled-labels-e215-AB.json`; the frozen scorer, run on them with step 13's arguments, printed (`scores-e215-pooled.txt`, last two lines):

```
POOLED REGISTERED: HP1 NOT DECIDED (13/19/18, p 0.37708558747544885); HP2 NOT DECIDED (13/19/18, p 0.37708558747544885); HP3 NOT DECIDED (13/19/18, p 0.37708558747544885); HP4 TOO FEW (6/2/42, p None); HP5 TOO FEW (6/1/43, p None)
POOLED POSTHOC: HP1 MM1-v3 BETTER (3/17/8, p 0.0025768280029296875); HP2 MM1-v3 BETTER (2/18/8, p 0.0004024505615234375); HP3 MM1-v3 BETTER (3/17/8, p 0.0025768280029296875); HP4 TOO FEW (3/3/22, p None); HP5 TOO FEW (3/2/23, p None)
```

| group | rule | over | MM1-v3.1 closer | MM1-v3 closer | ties | p (exact, two-sided) | the scorer | verify-e215d (own code; and its run of the frozen scorer) | REPORTED: bootstrap 95% interval of the mean d |
|---|---|---|---|---|---|---|---|---|---|
| registered (families P, C, R) | **HP1** | 50 | 13 | 19 | 18 | 0.377 | **NOT DECIDED** | NOT DECIDED (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3 BETTER [-0.0077, -0.0011] |
| registered (families P, C, R) | **HP2** | 50 | 13 | 19 | 18 | 0.377 | **NOT DECIDED** | NOT DECIDED (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3 BETTER [-0.0077, -0.0011] |
| registered (families P, C, R) | **HP3** | 50 | 13 | 19 | 18 | 0.377 | **NOT DECIDED** | NOT DECIDED (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3 BETTER [-0.0077, -0.0011] |
| registered (families P, C, R) | **HP4** | 50 | 6 | 2 | 42 | - | **TOO FEW** | TOO FEW (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3.1 BETTER [+0.0004, +0.0044] |
| registered (families P, C, R) | **HP5** | 50 | 6 | 1 | 43 | - | **TOO FEW** | TOO FEW (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3.1 BETTER [+0.0003, +0.0042] |
| post hoc (families L, S; reported apart) | **HP1** | 28 | 3 | 17 | 8 | 0.00258 | **MM1-v3 BETTER** | MM1-v3 BETTER (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3 BETTER [-0.0145, -0.0060] |
| post hoc (families L, S; reported apart) | **HP2** | 28 | 2 | 18 | 8 | 4.02e-04 | **MM1-v3 BETTER** | MM1-v3 BETTER (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3 BETTER [-0.0151, -0.0070] |
| post hoc (families L, S; reported apart) | **HP3** | 28 | 3 | 17 | 8 | 0.00258 | **MM1-v3 BETTER** | MM1-v3 BETTER (the same counts and p; its frozen-scorer run byte-equal to this one) | MM1-v3 BETTER [-0.0146, -0.0060] |
| post hoc (families L, S; reported apart) | **HP4** | 28 | 3 | 3 | 22 | - | **TOO FEW** | TOO FEW (the same counts and p; its frozen-scorer run byte-equal to this one) | NOT DECIDED [-0.0010, +0.0043] |
| post hoc (families L, S; reported apart) | **HP5** | 28 | 3 | 2 | 23 | - | **TOO FEW** | TOO FEW (the same counts and p; its frozen-scorer run byte-equal to this one) | NOT DECIDED [-0.0018, +0.0039] |

The registered answer is the registered group's: "The registered answer is the registered group's (P, C, R); the post hoc group's (L, S) is reported apart." Stated before the data (E215.md 1 and 7): "the sign test's power is 2-8% wherever it can decide, and H4 and H5 are TOO FEW by construction"; "So E215's head-to-head is registered, will be scored and printed, and is expected to read NOT DECIDED or TOO FEW whichever model is better: MM1-v3.1 and MM1-v3 differ by less than either's error." The registered HP1-HP5 read exactly so; the post hoc HP1-HP3 decide for MM1-v3 (family L's subset masks, where MM1-v3.1's refit sits further from the card than MM1-v3; note 1 of arm A's directory and note 2 here give each case).

**MM1-v3.1 against MM1-v3 pooled, rms of the relative error** (measured / forecast - 1 over both arms' cases and points together; desk arithmetic on the scorer's measured values and the frozen forecasts; each arm's figures equal verify-e215d's; REPORTED; blind):

| registered (families P, C, R) | wall cycles (cases) | counter's mean | seconds | J over idle given t (points) | J over idle, t forecast | J at rest given t (points) | J at rest, t forecast | W at the watts points, given t |
|---|---|---|---|---|---|---|---|---|
| MM1-v3.1 | 7.01% (50) | 6.44% | 7.00% | 11.50% (50) | 11.49% | 4.55% (50) | 6.28% | - |
| MM1-v3 | 6.78% (50) | 6.06% | 6.77% | 11.57% (50) | 11.55% | 4.57% (50) | 6.23% | - |
| v3.1 with T7 | 7.27% (50) | 6.48% | 7.27% | 11.54% (50) | 11.55% | 4.55% (50) | 6.57% | - |
| MM1-v2 | 10.37% (50) | 9.40% | 10.38% | 11.69% (50) | 12.10% | 4.56% (50) | 8.92% | - |

Without the gemmLnc points (post hoc; J over idle given t (n), with t forecast, J at rest given t, with t forecast): MM1-v3.1 3.59% (45), 3.77%, 1.29%, 4.95%; MM1-v3 3.89% (45), 4.00%, 1.41%, 4.84%; v3.1 with T7 3.52% (45), 3.72%, 1.25%, 5.28%; MM1-v2 5.00% (45), 6.29%, 1.56%, 8.62%.

| post hoc (families L, S; reported apart) | wall cycles (cases) | counter's mean | seconds | J over idle given t (points) | J over idle, t forecast | J at rest given t (points) | J at rest, t forecast | W at the watts points, given t |
|---|---|---|---|---|---|---|---|---|
| MM1-v3.1 | 9.53% (28) | 10.92% | 9.47% | 6.83% (35) | 7.16% | 1.90% (40) | 7.12% | 0.36 W (5) |
| MM1-v3 | 8.65% (28) | 10.13% | 8.59% | 6.71% (23) | 7.23% | 1.66% (28) | 7.86% | 0.30 W (5) |
| v3.1 with T7 | 15.61% (28) | 14.20% | 15.62% | 7.32% (35) | 7.91% | 1.88% (40) | 11.96% | 0.29 W (5) |
| MM1-v2 | 6.98% (28) | 7.47% | 6.97% | 6.04% (23) | 6.77% | 1.42% (28) | 6.88% | 0.24 W (5) |

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `pool_e215.py` | 7,871 | `8f1424c32f7c5cc94b4f1ac11c81b2ff3690886ea569e76cded646b261591d4a` | builds the pooled input from both arms' committed data and labels (each input checked against its pin and its directory's `SHA256SUMS` first); `check` rebuilds it and compares |
| `pool-e215.txt` | 1,400 | `a7f7825dbb221dcd0b91e9b442668d5f47a63d6a1f42db9d6d481345f9479dda` | its printout when it built the two input files |
| `pooled-data-e215-AB.json` | 284,089 | `10f726d24c532a88f2338cba82087b2996ed1515f0319ea35b4460bc13df3cc3` | the pooled input: arm A's and arm B's committed ARM objects, unchanged, and where each came from |
| `pooled-labels-e215-AB.json` | 130 | `f758f1e5050a8bf38d60baa67228b5e531ca573302d7c372303728b20724d3b0` | both arms' committed step-6n labels (no point and no case labelled 'ran before') |
| `scores-e215-pooled.json` | 239,396 | `0e2be24f791098fdc186aaa3da40f936643bbfd3d0f2253dc4721ff18fbe3b0b` | the frozen scorer's output on the pooled input: both arms' verdicts (equal to each arm's own file but the card transfer reading) and HP1-HP5 of both groups |
| `scores-e215-pooled.txt` | 4,115 | `d08cd078337001b9bd180e0e881476108b7d8b6c00ed76b0346529167edea3e3` | its printed lines |
| `README.md.dated-note-3.md` | (this note) | listed in `SHA256SUMS-note3` | this dated note |
| `SHA256SUMS-note3` | 8 lines | (not listed in itself) | the seven files above and `SHA256SUMS-note2` |

With `SHA256SUMS`, `SHA256SUMS-note1`, `SHA256SUMS-note2` and `SHA256SUMS-note3`, every file of this directory is in a list except `SHA256SUMS-note3` itself.

## 2. How the pooled verdicts were made (desk checks of code)

- **The input.** `pool_e215.py build` read arm A's `data-e215.json` and `labels-e215.json` from `8355db15` and arm B's from `4f648f24` (each one blob at its data commit and at the lab's HEAD when this note was built), checked each against its pin and its directory's `SHA256SUMS` line, copied each arm's ARM object unchanged, and read the output back: each arm equals its input value for value. Its printout (`pool-e215.txt`):

```
input, arm A: docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/data-e215.json sha256 651e954328c700205df64c497698621315870ad47d9223a25424e3df842ce763 (= the pin and its directory's SHA256SUMS line)
input, arm A: docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/labels-e215.json sha256 f664a2ce771d754f9e57015a5ac063037cfa305e32c8ec57ed12a5c48f7dbac1 (= the pin and its directory's SHA256SUMS line)
  arm A: 62 points with 116 point runs; smoke runs 4; tie runs 3; labels {"ran_before_cases": [], "ran_before_points": []}
input, arm B: docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/data-e215.json sha256 b4c6bdb54b079565959a13df82e8ba13e32f988beee700540d25614eb44780c9 (= the pin and its directory's SHA256SUMS line)
input, arm B: docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/labels-e215.json sha256 d801cae792a59f2e20cb92724310d46436605421a856a9bd34b1cd1f9f161184 (= the pin and its directory's SHA256SUMS line)
  arm B: 32 points with 68 point runs; smoke runs 5; tie runs 3; labels {"ran_before_cases": [], "ran_before_points": []}
read back: each arm of the output equals its input arm (A and B); labels likewise
wrote pooled-data-e215-AB.json (284089 bytes, sha256 10f726d24c532a88f2338cba82087b2996ed1515f0319ea35b4460bc13df3cc3) and pooled-labels-e215-AB.json (130 bytes, sha256 f758f1e5050a8bf38d60baa67228b5e531ca573302d7c372303728b20724d3b0)
```

- **The scorer.** In a tree of the 17 committed files the pooled run needs (the scorer, its ten pins, both arms' data, labels and `SHA256SUMS`), each one blob at its data commit and at HEAD, with `pool_e215.py` staged beside them, the frozen scorer ran on the pooled files with step 13's form of arguments, plain and under an audit hook: both runs wrote the same bytes, and the audited run opened the 13 files it reads (its own file, its ten pins and the two pooled files), 33 standard-library files and nothing else but its own outputs. `pool_e215.py check` re-made both inputs byte for byte (POOL-CHECK OK).
- **Its arms against the one-arm outputs.** Each arm in `scores-e215-pooled.json` equals that arm's own committed output (`scores-e215-A.json` in arm A's directory, note 1; `scores-e215-B.json` here, note 2) in every key but one: `readings_REPORTED` > `card_transfer`, which the scorer fills only when both arms are in one file (section 3).
- **HP1-HP5.** They are the scorer's own `decide()` over arm A's and arm B's d lists together (each case or point with its own arm's tie), as `score()` builds them: re-made in process by this lane with the scorer's functions, equal to the file. verify-e215d computed them with code that imports nothing of the kit's, and ran the frozen scorer on one input built from both committed data files: its output is byte-equal to `scores-e215-pooled.json` (the scorer reads only the arms, and the labels are the same).

## 3. REPORTED beside the pooled verdicts (never verdicts)

E215.md 7 registers the REPORTED pairs beside every head-to-head ("and the same sign test, cases and ties for MM1-v3.1 against MM1-v2 and for 'v3.1 with T7' against MM1-v3.1 (the walk's layout term at never-run layouts; at family L's points the two time forms differ by up to 28% in the wall cycles)."). The scorer computes them per arm only; pooled, they are desk arithmetic here: the scorer's own decide() over both arms' lists of its pair loop (copied line for line), equal to verify-e215d's pooled readings in every count.

**v3.1 with T7 against MM1-v3.1** (T7 / MM1-v3.1 / ties):

| group | rule | over | T7 closer | MM1-v3.1 closer | ties | p | reading |
|---|---|---|---|---|---|---|---|
| registered (families P, C, R) | HP1 | 50 | 19 | 25 | 6 | 0.451 | NOT DECIDED |
| registered (families P, C, R) | HP2 | 50 | 19 | 24 | 7 | 0.542 | NOT DECIDED |
| registered (families P, C, R) | HP3 | 50 | 19 | 25 | 6 | 0.451 | NOT DECIDED |
| registered (families P, C, R) | HP4 | 50 | 1 | 1 | 48 | - | TOO FEW |
| registered (families P, C, R) | HP5 | 50 | 3 | 1 | 46 | - | TOO FEW |
| post hoc (families L, S; reported apart) | HP1 | 28 | 17 | 8 | 3 | 0.108 | NOT DECIDED |
| post hoc (families L, S; reported apart) | HP2 | 28 | 19 | 6 | 3 | 0.0146 | v3.1 with T7 CLOSER |
| post hoc (families L, S; reported apart) | HP3 | 28 | 17 | 9 | 2 | 0.169 | NOT DECIDED |
| post hoc (families L, S; reported apart) | HP4 | 40 | 4 | 6 | 30 | 0.754 | NOT DECIDED |
| post hoc (families L, S; reported apart) | HP5 | 40 | 3 | 12 | 25 | 0.0352 | MM1-v3.1 CLOSER |

**MM1-v3.1 against MM1-v2** (MM1-v3.1 / MM1-v2 / ties):

| group | rule | over | MM1-v3.1 closer | MM1-v2 closer | ties | p | reading |
|---|---|---|---|---|---|---|---|
| registered (families P, C, R) | HP1 | 50 | 30 | 19 | 1 | 0.152 | NOT DECIDED |
| registered (families P, C, R) | HP2 | 50 | 30 | 19 | 1 | 0.152 | NOT DECIDED |
| registered (families P, C, R) | HP3 | 50 | 30 | 19 | 1 | 0.152 | NOT DECIDED |
| registered (families P, C, R) | HP4 | 50 | 19 | 19 | 12 | 1 | NOT DECIDED |
| registered (families P, C, R) | HP5 | 50 | 22 | 18 | 10 | 0.636 | NOT DECIDED |
| post hoc (families L, S; reported apart) | HP1 | 28 | 8 | 20 | 0 | 0.0357 | MM1-v2 CLOSER |
| post hoc (families L, S; reported apart) | HP2 | 28 | 6 | 22 | 0 | 0.00372 | MM1-v2 CLOSER |
| post hoc (families L, S; reported apart) | HP3 | 28 | 8 | 20 | 0 | 0.0357 | MM1-v2 CLOSER |
| post hoc (families L, S; reported apart) | HP4 | 28 | 4 | 11 | 13 | 0.118 | NOT DECIDED |
| post hoc (families L, S; reported apart) | HP5 | 28 | 5 | 9 | 14 | 0.424 | NOT DECIDED |

**(d) The card transfer** (E215.md 7's reading (d): the configurations both arms run, arm B over arm A measured, beside MM1-v3.1's card ratio; the scorer's `readings_REPORTED` > `card_transfer` in the pooled output, arm B's list; verify-e215d's finding 5):

| arm B point / arm A point | configuration | wall cycles, card 1 over aifoundry3 | W over idle, card 1 over aifoundry3 | MM1-v3.1's W ratio |
|---|---|---|---|---|
| b009 / a021 | `gemmLn1x15x3` fp32 random (rgm211 gemmLn) | 0.9971 | 1.0157 | 1.0276 |
| b010 / a022 | `gemmLn1x12x4` fp32 random (rgm211 gemmLn) | 0.9968 | 1.0162 | 1.0278 |
| b011 / a023 | `gemmLn1x10x5` fp32 random (rgm211 gemmLn) | 0.9971 | 1.0173 | 1.0279 |
| b015 / a033 | `gemmL2x15x2` fp32 random (rgm136 gemmL) | 0.9980 | 1.0164 | 1.0278 |
| b016 / a034 | `gemmL3x15x2` fp32 random (rgm136 gemmL) | 0.9979 | 1.0146 | 1.0278 |
| b017 / a035 | `gemmL10x15x2` fp32 random (rgm136 gemmL) | 0.9977 | 1.0152 | 1.0278 |
| b021 / a043 | `gemmL2x1x7` fp32 random (rgm136 gemmL) | 0.9994 | 1.0151 | 1.0301 |
| b022 / a044 | `gemmL2x1x7` int8 random (rgm136 gemmL) | 0.9915 | 1.0788 | 1.0543 |
| b023 / a045 | `gemmL1x1x41` fp32 random (rgm136 gemmL) | 0.9989 | 1.0237 | 1.0332 |

On the 8 shared fp32 configurations card 1's W over idle reads 1.015-1.024 times aifoundry3's, against MM1-v3.1's 1.028-1.033; the int8 one (gemmL2x1x7) 1.079 against 1.054; the wall cycles on card 1 are 0.992-0.999 times aifoundry3's. REPORTED, never a verdict.

## 4. Dated clauses (Thu 19 Nov 2026)

1. **The pooled registered head-to-head reads as E215.md said it would** (verify-e215d's pooled readings): MM1-v3.1's time form is MM1-v3's refitted, so the two models' time forecasts sit 0-2.3% apart against held-out errors near 5%, and their energy forms closer still; pooled, HP1-HP3 are NOT DECIDED (13/19/18, p 0.377) and HP4 and HP5 TOO FEW (6/2/42 and 6/1/43). The verdicts stand as registered.
2. **The post hoc HP1-HP3 decide for MM1-v3** (3/17/8, p 0.00258; 2/18/8, p 4.02e-04; 3/17/8, p 0.00258): post hoc readings of family L's subset masks, reported apart by D1, never E215's answer.
3. **The card transfer** (verify-e215d's finding 5, for this lane to report): at the eight shared fp32 configurations card 1 draws less power over idle relative to aifoundry3 than MM1-v3.1's card ratio says, at the int8 one more (section 3). REPORTED, never a verdict.
4. **The model session's sealed forecast** (registered in `18398ed2`) is not read or scored here.

## 5. NOT RUN

- Independent code for the pooled bootstrap intervals (the frozen scorer's own figures, reproduced by its re-runs).
- A pooled reading of the frozen terms posted before the data (the gemmLnc and layout terms): not this note's.
- Any read of a box's disk.

## What this note changes

Nothing committed. It adds the pooled input, its script and printout, the frozen scorer's output on it, this note and its hash list. The registered HP1-HP5 above are E215's pooled registered verdicts; the post hoc ones stay reported apart.
