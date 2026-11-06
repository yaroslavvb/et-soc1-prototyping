# E178's data README, dated note 2 (Fri 6 Nov 2026; after the data commit and its fix): E178's three reported arms read on its committed data - Q148(c)'s constant-lane term reads NOT RESOLVED by its own rule and does not enter M10 (fp32's kinds +0.083 W above P against the term's +0.035 W, fp16's +0.029 W against +0.070 W); october-forecast-model's figure lies inside the board and minion-rail intervals of all five rule contrasts (int8 5s − 4s +0.039 W at the die against +0.053 W [+0.022, +0.085] at the board), its int8 ranking reads rho +0.357 against P's +0.643, and its float levels 0.972-0.993 of D; the rail arm as committed. Reported, never a verdict

*Written on the Intel at about 14:10-14:45 PST on Fri 6 Nov 2026, desk only, by the card day's arms lane (Q149), after the data
commit `f7820e70` (12:42:52 PST) and the data fix's [dated note 1](README.md.dated-note-1.md) (`f68f0380`, 13:57:23). [`README.md`](README.md),
[`SHA256SUMS`](SHA256SUMS), dated note 1 with its list, and every file of step 22's collection and score stay as committed. The note
answers the README's "Not read here" (lines 129-133): E178's two other reported arms, read after the data commit by their own registered
readings, and, in § 3, the minion-rail arm as the card lane wrote it. **None of the three is a verdict of E178: no E178 rule, threshold or
verdict reads any of them, and no E178 number, rule, verdict or gate reading changes.** Every forecast read here was committed before the
session's opening config read (11:33:24 PST, A2-4's first datum): Q148(c)'s term, registered `c71fbc7f` (05:27:58), coded `413d252b`,
fitted with its E178 forecasts frozen `6b5ad913` (05:39:33) and fixed by its dated note 2 `d62d0c8f` (06:37:59); october-forecast-model's
two freezes (00:00:55 and 01:39:53 PST), carried by E178's dated note M1 `97a5e16b` (10:01:16); and the rail arm, A3 `77768027` (05:17:12)
with A4's reader v2 `d48135dd` (06:40:23). The figures come from [`arms_note2_e178.py`](arms_note2_e178.py) and the two registered
scorers of Q148(c); [`arms-note2-e178.txt`](arms-note2-e178.txt) and [`arms-note2-e178.json`](arms-note2-e178.json) hold every reading
("output" below). [`SHA256SUMS-note2`](SHA256SUMS-note2) pins this note and its five files. For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, as the README.*

**Labels.** All three arms are **reported**, never a verdict. Their forecasts are **frozen** and their readings **blind**: Q148(c)'s for 23
of its 27 float kinds (its 4 bridge kinds, ones and −1 in each format, re-measure fit kinds and are blind by session only; its dated
note 2), october-forecast-model's for 34 of E178's 40 kinds (ones and −1 in each format are a check, not a test; M1-3), the rail arm's for
all 52 contrasts. Q148(c)'s rule words (BETTER, NOT RESOLVED, enters) are its own registration's and decide only whether the term enters
M10 for the next blind pool. Readings marked **beside** are not registered readings: arithmetic on the frozen figures and the committed
data, deciding nothing.

## 1. Q148(c)'s constant-lane term: NOT RESOLVED by its own rule, so it does not enter M10

What is read ([`REGISTRATION.md`](../../../../tools/claims-v3/m10-c/REGISTRATION.md) § 5-6): for each fp32 and fp16 kind E178's scorer
keeps (all 27), x = D − P, with P at the session's s and measured rate (`scored.json` › `primary` › `reported` › `kinds`), and
x′ = x − (P / P_frozen) × L, with L the frozen level on aifoundry3 (fp32 +0.0354 W, fp16 +0.0703 W). The two registered scorers ran as
their files say: `termc.py score` wrote [`arm-m10c-termc-e178.json`](arm-m10c-termc-e178.json) and `termc_note2.py score` (the rule passed
through, the split beside it) wrote [`arm-m10c-note2-e178.json`](arm-m10c-note2-e178.json). The script re-runs both in memory and finds
each file byte for byte; the bridge kinds are dated note 2's frozen four, checked again by bytes.

| reading (REGISTRATION.md § 6) | all 27 float kinds: the registered rule | the 23 new kinds: dated note 2's split, reported |
|---|---|---|
| rms(x) → rms(x′) | 0.0754 → 0.0610 W | 0.0693 → 0.0609 W |
| d = rms(x′) − rms(x), 95% (bootstrap over kinds) | −0.0143 [−0.0275, +0.0015] | −0.0084 [−0.0229, +0.0094] |
| C1 (BETTER needs d ≤ −0.010 W with the upper end below 0) | **NOT RESOLVED** | NOT RESOLVED |
| C2: d in fp32 / fp16 | −0.0309 / **+0.0082** W: does not hold | −0.0304 / +0.0257 W: does not hold |
| the term enters M10 for the next blind pool | **no** | (agrees with the rule) |
| m, fp32: mean x, 95% over kinds | +0.0832 [+0.0615, +0.1050] W, 14 kinds | +0.0807 [+0.0561, +0.1053], 12 |
| m, fp16 | +0.0286 [−0.0002, +0.0574] W, 13 kinds | +0.0169 [−0.0070, +0.0408], 11 |
| against L on aifoundry3 (95%, jackknife over runs) | fp32 +0.0354 [−0.0533, +0.1241]; fp16 +0.0703 [+0.0241, +0.1164] | the same |

- **By format** (output (1)): adding the level lowers fp32's rms miss from 0.0908 to 0.0599 W and raises fp16's from 0.0540 to 0.0622 W.
  fp32's kinds read further above P than the level (+0.083 against +0.035 W); fp16's read less (+0.029 against +0.070 W, the level above
  m's interval).
- **What would show the term is not wanted** (§ 6: C1 WORSE, or m's interval holding 0 and excluding L's interval in both formats): not
  met. C1 is not WORSE, fp32's m excludes 0, and fp16's holds 0 but overlaps L's interval. So M10 stays as frozen for constant-lane tiles,
  and M10-C is a reported arm in the next blind pool, as § 6 says.
- **The frozen arms beside** (§ 4, never in the rule): d for the per-card arm −0.0167 W and for arm R −0.0201 W. aifoundry3's own level
  (the per-card arm) is fp32 +0.110 W [+0.098, +0.122] and fp16 +0.081 W [+0.014, +0.148]: fp32's measured +0.083 W lies between the
  pooled level and aifoundry3's own, and fp16's lies below both.
- **The 4 bridge kinds apart:** fp32 ones +0.1251 and −1 +0.0716 W (mean +0.098), fp16 ones +0.0438 and −1 +0.1420 W (mean +0.093).
  Post hoc, their means are about the size of the term's own aifoundry3 rows of these kinds (+0.095 to +0.112 W,
  [`tools/claims-v3/m10-c/README.md`](../../../../tools/claims-v3/m10-c/README.md)); the 23 new kinds read lower, fp16's most (+0.017 W).
- **Beside, each kind against the forecast's frozen 95% predictive interval** (P + L ± 1.96 σ_C; σ_C 0.094 W fp32, 0.055 W fp16): D lies
  inside the interval as frozen (s = 1, E171's zeros rate) for 26 of the 27 kinds, fp16 −1 above it (8.418 W against 8.187-8.403); at the
  session's P (x′ within ± 1.96 σ_C), 26 of 27, fp16 (A 5, B 4) just below (x′ −0.110 against −0.108 W). Every kind's x and x′ is in
  output (1).

## 2. october-forecast-model, by dated note M1 (M1-4): inside both intervals on every rule contrast; a weaker int8 ranking than P's; float levels 1-3% under D

What is read ([`E178.md.dated-note-M1.md`](../../../../tools/claims-v3/e178/E178.md.dated-note-M1.md), M1-4): the scored figure per kind is
table 1's "power above zeros at 600 MHz, a3" for the 27 float kinds and int8 v2's "power above zeros at 600 MHz, die, a3" for the 13 int8
kinds ([`m1-october-forecast-model.json`](../../../../tools/claims-v3/e178/m1-october-forecast-model.json) › `scored` › `kinds`). A
contrast a − b reads the figure of a less that of b and is set against the board interval and the minion-rail interval that A4's reader
gives for it ([`rail-arm-e178.json`](rail-arm-e178.json)): inside, above or below. **Nothing is scaled:** the int8 figures are at the die,
and each reading names its column. E178's frozen P sits beside for comparison; read here against the board interval, it agrees with the
scorer's own reading of its scored dP on all 51 contrasts the scorer reads.

**The five rule contrasts** (output (2)):

| contrast | E178's rule | october-forecast-model, W | board D, W (95%) | the model | minion rail, W (95%) | the model | E178's frozen P, board |
|---|---|---|---|---|---|---|---|
| int8 5s − 4s | E178-H-int8 | **+0.0392** (die) | +0.0532 [+0.0217, +0.0848] | **inside** | +0.0261 [−0.0281, +0.0804] | inside | +0.1862, above |
| fp32 5s − 4s | E178-H-fp32 | +0.0128 | +0.0523 [−0.0459, +0.1505] | inside | +0.0422 [−0.0887, +0.1731] | inside | +0.0099, inside |
| fp16 5s − 4s | E178-H-fp16 | +0.0114 | +0.0558 [−0.0038, +0.1154] | inside | +0.0292 [−0.0251, +0.0835] | inside | +0.0167, inside |
| fp32 ones − 1.5 × 2^−64 | E178-U | +0.0421 | +0.0452 [−0.0314, +0.1217] | inside | +0.0328 [−0.1174, +0.1829] | inside | +0.0749, inside |
| int8 85 − (−1) | E178-S-int8 | **+0.0696** (die) | +0.0582 [−0.0770, +0.1935] | **inside** | +0.0688 [−0.0436, +0.1812] | inside | +0.3549, above |

His int8 pair at the model's own board equivalent, "about +0.047 W" (its int8 v2 per-pair line, as written), lies inside the couple-form
board interval above and inside the pass-form one, +0.0724 W [+0.0117, +0.1331].

**4s against 5s, the other forms:**

| pair | the model, W | board D, W (95%) | the model | minion rail, W (95%) | the model | E178's frozen P, board |
|---|---|---|---|---|---|---|
| int8 5s − 4s, pass form | +0.0392 (die) | +0.0724 [+0.0117, +0.1331] | inside | +0.0278 [−0.0221, +0.0776] | inside | +0.1862, above |
| fp32 5s − 4s, pass form | +0.0128 | +0.0533 [−0.0434, +0.1501] | inside | +0.0558 [−0.0429, +0.1545] | inside | +0.0099, inside |
| fp16 5s − 4s, pass form | +0.0114 | +0.0545 [−0.0063, +0.1153] | inside | +0.0345 [−0.0162, +0.0852] | inside | +0.0167, inside |
| int8 (A 4, B 5) − 4s | +0.0296 (die) | +0.0937 [+0.0282, +0.1591] | inside | +0.0474 [−0.0706, +0.1653] | inside | +0.1248, inside |
| int8 (A 4, B 5) − (A 5, B 4) | +0.0018 (die) | +0.0028 [−0.1231, +0.1286] | inside | +0.0232 [−0.0671, +0.1135] | inside | +0.0157, inside |
| fp32 (A 4, B 5) − (A 5, B 4), 3 passes | −0.0032 | +0.0595 [−0.2502, +0.3692] | inside | +0.0967 [+0.0075, +0.1859] | **below** | +0.0000, inside (rail: below) |
| fp32 (A 4, B 5) − 4s, 3 passes | +0.0078 | +0.0364 [−0.3523, +0.4251] | inside | +0.0612 [+0.0470, +0.0753] | **below** | +0.0165, inside (rail: below) |
| fp16 (A 4, B 5) − (A 5, B 4), 3 passes | −0.0033 | +0.0930 [−0.0543, +0.2403] | inside | +0.1116 [−0.2366, +0.4597] | inside | +0.0000, inside |
| fp16 (A 4, B 5) − 4s | +0.0082 | +0.0443 [−0.0791, +0.1678] | inside | +0.0579 [−0.2297, +0.3455] | inside | +0.0180, inside |

**The ranking** (M1-4: Spearman's rho with average ranks, `power_e178.spearman` imported unchanged, of the figure against measured D over
the kinds E178's scorer keeps):

| format | kinds | october-forecast-model against D | E178's scored P against D, beside |
|---|---|---|---|
| fp32 | 14 | +0.073 | −0.046 |
| fp16 | 13 | +0.162 | +0.280 |
| int8 | 13 | **+0.357** | **+0.643** (E178-R-int8, PASS at its line 0.56) |

M1-4 registers no line for the arm; E178-R-int8's line at n = 13 is given for scale only. The model puts int8 −1 lowest of the 13 kinds
(1.4994 W at the die) where the card reads it third highest (1.7594 W at the board).

**The model's extremes** (its highest figure less its lowest, per format, M1's own list):

| extreme | the model, W | board D, W (95%) | the model | minion rail, W (95%) | the model |
|---|---|---|---|---|---|
| fp32 5 − 1.5 × 2^−64 | +0.0552 | +0.0419 [−0.0989, +0.1828] | inside | +0.0396 [−0.0694, +0.1485] | inside |
| fp16 (A 5, B 4) − 0.5 | +0.0126 | −0.0354 [−0.2728, +0.2019] | inside | −0.0418 [−0.4756, +0.3921] | inside |
| int8 85 − (−1), E178-S-int8's own pair | +0.0696 (die) | +0.0582 [−0.0770, +0.1935] | inside | +0.0688 [−0.0436, +0.1812] | inside |

The first two are not among the reader's 52 contrasts, so they are read here by the reader's own pass-form statistic (`rail_e178.views`
with `score_e178.pair_xs` and `interval`, imported unchanged), after that route reproduced all 48 of the reader's pass-form contrasts on the
board and the rail to 5.6e-17 W. E178's own six extremes (by P) are among the 52: the model is inside every one of them on the board,
where P lies above two (int8 85 − ones and fp32 (A 5, B 4) − 1.5 × 2^−64); on the rail it is inside all but the fp32 cross
(A 4, B 5) − (A 5, B 4), where it lies below, as P does.

**The equal pairs.**
- **E178's 21 equal-flip pairs** (A3-1's list): the model's differences are at most 0.0027 W in size. They lie inside the board interval
  in 18 and above it in the three that read below 0 (fp16 2 − (−1) −0.1749 W, fp16 4 − (−1) −0.1458 W, int8 4 − 8 −0.0669 W; the model
  +0.0001, +0.0002 and +0.0014 W), and inside the rail interval in all 21: the same 18 and 3 as E178's P.
- **The 6 equal-popcount pairs:** inside the board interval in all 6; on the rail inside 5 and above 1, int8 5 − 3 (−0.0632 W [−0.1174,
  −0.0090], the model +0.0118 W).
- **The model's own ties** (M1-4: reported only): fp32 2 and 8 (8.1810 W), fp32 1 and −1 (8.1789 W), fp16 1.5 and 5 (8.1947 W). The card
  reads fp32 2 − 8 +0.0272 W [−0.0057, +0.0602], fp32 −1 − 1 −0.0543 W [−0.1166, +0.0081] and fp16 1.5 − 5 +0.0382 W [−0.0689,
  +0.1454] (read here, not among the 52): each spans 0, on the board and on the rail.
- **Beside, E178-E's equal groups:** the model's spreads are 0.0021 W (fp32 0.5, 1, −1, 2, 4, 8), 0.0018 W (fp16, the same numbers) and
  0.0026 W (int8 1, 2, 4, 8), against the measured 0.1048, 0.1749 and 0.0669 W and the rule's lines 0.1958, 0.1811 and 0.2460 W (E178's
  scored P: 0.0033, 0.0043 and 0.0003 W).

**Over the reader's 52 contrasts (48 distinct readings):**

| | october-forecast-model | E178's frozen P, beside |
|---|---|---|
| board interval: inside / above / below | 45 / 3 / 0 | 38 / 10 / 0 |
| minion-rail interval: inside / above / below | 45 / 1 / 2 | 39 / 7 / 2 |
| the 6 board intervals that do not span 0 | inside 3, above 3 | inside 1, above 5 |
| the 3 rail intervals that do not span 0 | above 1, below 2 | above 1, below 2 |

Most board intervals span 0 (42 of the 48), so most "inside" readings say only that the model forecasts a small difference where the card
resolves none. Where the board resolves one (6), the model is inside his int8 pair in both forms and int8 (A 4, B 5) − 4s, and above the
three equal-flip pairs that read below 0; E178's P is inside only int8 (A 4, B 5) − 4s.

**The levels** (beside: M1-4 names the scored figure per kind and registers no level statistic, so this is arithmetic on it; each kind's
figure against its measured D and Drail, unscaled, the intervals t over the kept passes and, for the means, over kinds):

| format | the model's column | kinds | D − the model's figure, W (95% over kinds) | the figure / D | the figure / Drail | the figure against each kind's D interval |
|---|---|---|---|---|---|---|
| fp32 | table 1, a3 | 14 | +0.184 [+0.165, +0.203] | 0.973-0.985 | 1.157-1.190 | inside 1, below 13 |
| fp16 | table 1, a3 | 13 | +0.124 [+0.095, +0.154] | 0.972-0.993 | 1.160-1.183 | inside 2, below 11 |
| int8 | int8 v2, a3, at the die | 13 | +0.157 [+0.121, +0.192] | 0.852-0.950 | 0.971-1.072 | inside 2, below 11 (Drail's: inside 7, above 6) |

- **The model's own level band, as written** ("on the committed ones kinds the model reads 0.97-0.98x the measured D on aifoundry3"): E178's
  check kinds read 0.973 (ones) and 0.979 (−1) in fp32, 0.984 and 0.972 in fp16; the 23 blind float kinds read 0.973-0.993.
- **int8:** the board D is 1.05-1.17 times the model's die figure (mean 1.10), against int8 v2's "the board adds roughly a quarter on these
  cards"; the die figure is 0.97-1.07 times the minion rail's Drail. Table 1's int8 ones (superseded by int8 v2, reported only) reads 0.943
  of D, against its stated 0.99x.
- **Beside, int8 v2's own band** (the held-operand term, from 0 up to the lab's measured ones-against-(−1) residual, at the die): the board
  D lies above it for all 13 int8 kinds; the minion rail's Drail lies inside it for 127, 85 and −1, post hoc the three kinds with the most
  set operand bits, and below it for the other 10.

## 3. The minion-rail arm, as the card lane committed it (A3, read by A4's reader v2)

Quoted from [`rail-arm-e178.json`](rail-arm-e178.json) and [`rail-arm-e178.md`](rail-arm-e178.md), and recounted here (output (3)): read at
the desk by A4-5's three lines at 12:32:03 PST, exit 0; 52 contrasts (48 distinct readings), the four kept passes, 299 kept runs, none
without a Drail, none flagged; the board column reproduces `scored.json`. Its forecasts are the frozen board forecast times E171's median
Drail/D (fp32 0.8096, fp16 0.8080, int8 0.8379) on the rail, and times one less it off the rail.

| contrast | board D, W | minion rail Drail, W | rail forecast (P) | off the rail, D − Drail, W | off-rail forecast (P) |
|---|---|---|---|---|---|
| E178-H-int8, int8 5s − 4s | +0.0532 [+0.0217, +0.0848] | **+0.0261 [−0.0281, +0.0804]**, spans 0 | +0.1560, **above** | +0.0271 [−0.0189, +0.0731], spans 0 | +0.0302, inside |
| the same, pass form | +0.0724 [+0.0117, +0.1331] | +0.0278 [−0.0221, +0.0776], spans 0 | +0.1560, above | +0.0446 [−0.0528, +0.1421], spans 0 | +0.0302, inside |
| E178-H-fp32 | +0.0523 [−0.0459, +0.1505] | +0.0422 [−0.0887, +0.1731] | +0.0080, inside | +0.0101 [−0.1610, +0.1812] | +0.0019, inside |
| E178-H-fp16 | +0.0558 [−0.0038, +0.1154] | +0.0292 [−0.0251, +0.0835] | +0.0135, inside | +0.0266 [−0.0646, +0.1177] | +0.0032, inside |
| E178-U | +0.0452 [−0.0314, +0.1217] | +0.0328 [−0.1174, +0.1829] | +0.0606, inside | +0.0124 [−0.1461, +0.1709] | +0.0143, inside |
| E178-S-int8, 85 − (−1) | +0.0582 [−0.0770, +0.1935] | +0.0688 [−0.0436, +0.1812] | +0.2974, above | −0.0106 [−0.1177, +0.0965] | +0.0575, inside |
| 127 − (−1) | +0.0271 [−0.0828, +0.1371] | +0.0177 [−0.0856, +0.1210] | +0.2029, above | +0.0095 [−0.1296, +0.1485] | +0.0393, inside |
| 85 − 127 (A2-2) | +0.0311 [−0.1188, +0.1810] | +0.0512 [−0.0243, +0.1266] | +0.0944, inside | −0.0201 [−0.1015, +0.0614] | +0.0183, inside |
| the bridge, int8 −1 − ones | +0.1227 [−0.2126, +0.4579] | +0.0630 [−0.1142, +0.2401] | +0.0921, inside | +0.0597 [−0.1166, +0.2360] | +0.0178, inside |
| int8's largest, 85 − ones | +0.1809 [−0.0297, +0.3915] | +0.1318 [−0.0001, +0.2637] | +0.3894, above | +0.0491 [−0.0355, +0.1338] | +0.0754, inside |

- **Over all 52, as the README gives them:** the rail's P forecast inside its interval in 42, above it in 7 and below it in 3; the rail
  intervals read above 0 in 3 (the fp32 crosses), below 0 in 1 (int8 5 − 3, −0.0632 W [−0.1174, −0.0090]) and span 0 in 48.
- **Beside, off the rail** (the README did not count them): the off-rail P forecast inside 49, above 1 (fp16 5 − 7) and below 2 (int8 2 − 4,
  read twice); the off-rail intervals read above 0 in 2 (int8 2 − 4, twice) and below 0 in 1 (fp16 5 − 7). The board intervals read above
  0 in 3 and below 0 in 3.
- **For his pair the board resolved what the rail did not:** +0.053 W [+0.022, +0.085] at the board, +0.026 W [−0.028, +0.080] on the
  minion rail with its frozen +0.156 W above, and +0.027 W [−0.019, +0.073] off it with +0.030 W inside. A3-3 claimed nothing for the
  rail's resolution.

## What the three arms say about predicting power (reported, deciding nothing)

1. **His one-number int8 pair is forecast best small.** M10's P (+0.186 W, E178-H-int8's SIZE FAIL HIGH) lies above the measured +0.053 W
   [+0.022, +0.085]; october-forecast-model's +0.039 W at the die (+0.047 W by its own board equivalent) lies inside it and inside the
   rail's [−0.028, +0.080]. The same holds for int8 85 − (−1) (+0.070 W against +0.058 W [−0.077, +0.194]; P +0.355 W above) and
   127 − (−1). Where the board resolves a difference, the model's figures are inside 3 of 6 and P's 1.
2. **But the int8 order is P's.** Spearman rho +0.357 for october-forecast-model against +0.643 for P (E178-R-int8 PASS). Neither forecast
   has both here: P orders the 13 int8 kinds, and october-forecast-model sizes their differences.
3. **The floats' constant-lane level is not one level per format as registered.** fp32's kinds read +0.083 W [+0.062, +0.105] above M10's
   P, fp16's +0.029 W [−0.000, +0.057]. Q148(c)'s rule reads NOT RESOLVED, with C2 failing in fp16, so M10 stays as frozen for these tiles.
   aifoundry3's own fp32 level (+0.110 W, the per-card arm) lies nearer fp32's reading than the pooled +0.035 W does.
4. **The levels:** october-forecast-model's float figures sit at 0.972-0.993 of the board D blind, as its own level band says; its int8
   die figures at 0.852-0.950 of the board D and 0.971-1.072 of the minion rail.
5. **The rail did not resolve his pair here.** Of the 48 distinct contrasts the board resolved 6 (his int8 pair in both forms among them)
   and the rail 3 (the fp32 crosses and int8 5 − 3), none of them the same.
6. **Heat:** nothing read or scored.

## Lines for the records

1. **Q148(c) on E178** (a reported arm; blind for 23 of its 27 float kinds): its registered rule reads NOT RESOLVED (C1 d −0.014 W
   [−0.028, +0.001] over 27 kinds; C2 fails in fp16, +0.008 W), so the term does not enter M10 for the next blind pool; the split on the 23
   new kinds reads the same (d −0.008 W [−0.023, +0.009]). The measured levels above P: fp32 +0.083 W [+0.062, +0.105], fp16 +0.029 W
   [−0.000, +0.057], against L +0.035 and +0.070 W.
2. **october-forecast-model on E178** (a reported arm by M1-4; blind for 34 kinds, a check for 6): inside the board and minion-rail
   intervals of all five rule contrasts; int8 5s − 4s +0.039 W at the die (its own board equivalent +0.047 W) against +0.053 W [+0.022,
   +0.085] at the board; Spearman rho fp32 +0.07, fp16 +0.16, int8 +0.36 (E178's P +0.64 in int8); float levels 0.972-0.993 of D, int8 die
   figures 0.852-0.950 of D. Never "it passed", and never any of E178's verdict words.
3. **The minion-rail arm:** as the README quotes it, recounted here unchanged; beside, off the rail, the P forecast inside 49, above 1 and
   below 2.
4. The model is named october-forecast-model only.

## Departures and disclosures

- **Two contrasts M1-4 names have no interval from A4's reader:** the model's fp32 and fp16 extremes. They are read by the reader's own
  pass-form statistic, after the check above; so is fp16 1.5 − 5, one of the model's ties.
- **The levels** (§ 2) and every row marked beside are arithmetic on the frozen figures, not registered readings; so is the per-kind
  predictive-interval reading of § 1.
- **E178's frozen P beside the model** is the frozen board figure (and the rail arm's frozen rail figure), not the scored dP; on the board
  its reading agrees with the scorer's on all 51 contrasts the scorer reads.
- **Compute:** Python through the round's local slot, one job at a time, at nice 10, one core: the hash lists and both Q148(c) scorers with
  their note-2 self-test (14:10:40-14:10:46 PST, identical to its committed log), and the arms script's development runs
  (14:17:58-14:22:59), then the in-place runs and checks before the commit. An independent check, standard library only and importing
  nothing from the lab, re-derived every rho, the level means and ratios, each of the 52 contrasts' model figure and readings, Q148(c)'s
  C1 and C2 d and m, and the rail arm's counts: 0 differences.

## What does not change

Every reading, verdict, gate, stop and figure of the README and of dated note 1 stands. With this note's seven files in the directory:
`SHA256SUMS` reads 345 of 345 OK, `SHA256SUMS-note1` 4 of 4 and `SHA256SUMS-note2` 6 of 6; E178's hash lists (registration 76, A1 27,
kit 72, A2 17, kit note 1 47, A3 34, A4 44, M1 13) and Q148(c)'s (25 and 18) read OK. The scorer reads none of these files, so no scored
figure can move.

## Files and re-run

| file | what |
|---|---|
| `README.md.dated-note-2.md` | this note |
| [`arms_note2_e178.py`](arms_note2_e178.py) | the arms reader: checks every input against its committed hash list, re-runs both Q148(c) scorers in memory, reads october-forecast-model by M1-4 and quotes the rail arm |
| [`arms-note2-e178.json`](arms-note2-e178.json), [`arms-note2-e178.txt`](arms-note2-e178.txt) | its output: every kind, contrast, count and level |
| [`arm-m10c-termc-e178.json`](arm-m10c-termc-e178.json) | `termc.py score`'s output on this `scored.json`, as written |
| [`arm-m10c-note2-e178.json`](arm-m10c-note2-e178.json) | `termc_note2.py score`'s output on this `scored.json`, as written |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | the five files above and this note |

From the top of the tree, under the Intel's `/usr/bin/python3` (3.9, numpy 1.26), one core, a few seconds:
- `python3 -B tools/claims-v3/m10-c/termc.py score --scored docs/reports/data/2026-11-06-e178-one-number-aifoundry3/scored.json --fit tools/claims-v3/m10-c/termc-fit.json --out <dir>/arm-m10c-termc-e178.json`;
- `python3 -B tools/claims-v3/m10-c/termc_note2.py score --scored docs/reports/data/2026-11-06-e178-one-number-aifoundry3/scored.json --out <dir>/arm-m10c-note2-e178.json`;
- `python3 -B docs/reports/data/2026-11-06-e178-one-number-aifoundry3/arms_note2_e178.py --out <dir> --scorers <dir>` (writes the two
  outputs, byte for byte these);
- in this directory, `shasum -a 256 -c SHA256SUMS-note2`.

SPDX-License-Identifier: Apache-2.0
