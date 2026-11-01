# E87 data: the speed of real GPT-2 tensors under aifoundry2's own governor (Q130, Sat 31 Oct 2026)

Q130(n)'s nine real tiles, cut from GPT-2 small (layer 0's MLP up-projection, layer 6's MLP down-projection and layer
6's attention QKᵀ, each in fp32, fp16 and int8; [`tools/claims-v3/kinds/real/`](../../../../tools/claims-v3/kinds/real/README.md)),
on aifoundry2 card 0 under the card's own governor. E80's anchors ran again in the same session: fp32 randn, fp16
randn, int8 full, and fp32, fp16 and int8 zeros. Each tile got a **burst on a cool die**, run twice, and a **sustained
run** of about 76 s (fp32 randn and fp16 randn twice). **Nothing was set on the card**: the TDP and the threshold read
65 W and 65 °C at all 47 per-run reads of `ettelem config`, the smoke's three, the session's start and end, and once
more under the card lock at 20:25:35 PDT, before the release ([`final-config.txt`](final-config.txt)). The sampler ran
without `--reset-ms`.

The pre-registration is [`tools/claims-v3/kspeed/e87/`](../../../../tools/claims-v3/kspeed/e87/README.md)
(`7f84f454`, pushed 19:47:42 PDT). Its frozen predictions are
[`predictions.json`](../../../../tools/claims-v3/kspeed/e87/predictions.json), sha256 `025f4e15…`: Q130(n)'s frozen
points (`predictions-real.json`, sha256 `bab33bee…`) and Amendment 1's scoring intervals (`amendment-1.json`,
`f32e8a90…`). The card was claimed in `#community-lab` at 19:48:48 and released by editing the same post at 20:25. **No
amendment and no departure from the registered design.** While the session ran, the lane read only its progress lines
(run names, return codes, config reads); the reduction first ran on the complete session, after the release. An
independent verifier re-derived every registered number and reproduced every derived file byte for byte; the text it
found wrong is corrected in place, listed at the end (Corrections after verification), and no number or verdict
changed.

| session | PDT | what |
|---|---|---|
| `smoke/` | 19:49:01–19:49:22 | three 2 s launches of real tiles (fp32 `l6_attn_qk`, fp16 `l0_mlp_up`, int8 `l6_mlp_down`): 546.0 / 546.0 / 318.0 cycles per op, config 65 W / 65 °C; not analysed |
| `s1/` | 19:49:49–20:25:19 | the registered session, 47 runs, exit 0, **35.5 card-minutes** (35.8 with the smoke, of the 40 allowed): `BURST` 30 runs (19:49:51–19:57:00), `SUS` 17 runs (19:57:06–20:25:13) |

## Results first

### 1. All nine registered rules pass

**Q130(n)'s frozen speeds hold for real data.** E83's power-to-clock relation, fed Q130(n)'s predicted power for tiles
no card had run, hit the nine burst clocks to **10.7 MHz rms** (7.4 with the governor's one idle reset set aside) and
the nine sustained clocks to **6.1 MHz rms**, and called all nine sustained limits. **Those clock rules do not test the
power predictor, though.** The real tiles' clocks sit within a few MHz of random data's, and a baseline with no model,
which gives each real tile E80's cell for its format's random reference, scores as well: 9.75 MHz burst and 5.14 MHz
sustained ([`corrections-check.txt`](corrections-check.txt) C1). What the clock rules show is that E83's relation
carries over to real data in a new session (S1, on the measured power) and that real fp32 and fp16 data run at about
random data's speed. The predictor's test is like with like. Measured in one session, real fp32 tiles switch
0.985–0.995 of random fp32's power above zeros, real fp16 0.962–0.990 of random fp16's, and real int8 0.797–0.904 of
uniform random int8's. S4's int8 bar (0.835, below 0.9) is the one rule that "real = random" fails; in fp32 and fp16
all six tiles fall below 1, Q130(n)'s sign; S3's amended intervals hold 1.000 for 8 of the 9 tiles, so S3 alone cannot
separate the predictor from "real = random". Each verdict is scored exactly as registered
([`results.json`](results.json) `rules`, [`reduce.txt`](reduce.txt)).

| rule | verdict | what the data say |
|---|---|---|
| **E87-R1** burst rms ≤ 25 MHz against Q130(n)'s frozen points | **PASS** | **10.7 MHz** over the nine; 7.4 on A1's reset-free cells; 9.1 over the six fp32 and fp16 tiles. Every fp32 and fp16 tile ran 1.9–13.4 MHz below its point; int8 `l0_mlp_up`'s −23.0 is one pass the idle reset hit (§4). The no-model baseline scores 9.75, 6.03 and 7.39 (C1) |
| **E87-R2** sustained limit right for ≥ 7 of 9 | **PASS** | **9 of 9**: the six fp32 and fp16 tiles `thermal` (share at 800 MHz 0.000–0.018), the three int8 tiles `none` (0.967–1.000) |
| **E87-R3** sustained rms ≤ 25 MHz | **PASS** | **6.1 MHz**; 7.0 over the six fp32 and fp16 tiles; the no-model baseline scores 5.14 and 5.67 (C1). The largest miss is fp16 `l6_mlp_down`, 602.8 against 617.6 (−14.8): its measured c is 0.56 W above Q130(n)'s, worth 4 MHz (the relation on its measured c gives 613.5), and the session's two fp16 randn runs differ by 10.7 MHz |
| **E87-R4** ≥ 7 of 9 inside Amendment 1's burst intervals and ≥ 7 of 9 inside its sustained intervals | **PASS** | burst **8 of 9** (int8 `l0_mlp_up`'s 777.0 lies outside the single point 800; 9 of 9 reset-free), sustained **9 of 9**. Inside the frozen D-propagated ranges: 8 of 9 and 6 of 9 |
| **E87-R5** anchors within 25 MHz of their tie cells | **PASS** | all twelve rows; the largest is int8 full sustained, 774.7 against E80's 793.4 (−18.7; E83 786.5), in a session whose heat path ran 0.5 °C warmer than E80's (§5) |
| **E87-S1** the relation on measured c, burst and sustained rms ≤ 15 MHz | **PASS** | burst **10.1** (6.6 reset-free), sustained **5.2 MHz** |
| **E87-S2** real within ±15 MHz of same-session randn's burst, fp32 and fp16 | **PASS** | fp32 **−2.7 MHz** (703.3 against 706.0), fp16 **+7.8 MHz** (729.0 against 721.2), 1.3 σ, with all six real passes above both randn passes (registered expectation +1 and +5; C2); sustained +3.7 and +1.7 (labelled) |
| **E87-S3** like-with-like ratio inside its S3 interval for ≥ 7 of 9 | **PASS** | **9 of 9** (9 of 9 inside the frozen intervals too). The measured c lies inside Q130(n)'s converted c interval for 9 of 9 (frozen and amended). "Real = random" (1.000) lies inside 8 of the 9 amended intervals and 6 of the 9 frozen ones, so this rule does not separate the two (C1) |
| **E87-S4** format means below 1 (fp32), 1 (fp16), 0.9 (int8) | **PASS** | fp32 **0.992**, fp16 **0.980**, int8 **0.835**. int8's bar is the one "real = random" fails; across the three tiles, t against 1.000 is 2.48 (fp32), 2.25 (fp16) and 4.77 (int8) on 2 df (C4) |

### 2. The speeds: what real numbers get on this card

All on aifoundry2 card 0, its own governor, 1,024 minions repeating one 16×16 TensorFMA on the tile pair. A burst cell
is two 6 s runs from a die ≤ 55 °C (the clock from 1.5 s to the end); a sustained cell is the last 40 s of nine 8 s
processes from ≤ 57 °C, one run per tile (two for the randn anchors). One sustained run's 1 σ is ±15.6 MHz when it is
thermal-held above 615 MHz and ±5.6 MHz at or near a clamp, board W ±0.82, die ±0.81 °C (E83's
[corrections-check](../2026-10-31-e83-kinds-speed-rest/corrections-check.txt) C3). The full table, with the anchors,
p800 and board pJ per operation, is [`tables.md`](tables.md); the blog's cells are [`cells.json`](cells.json).

| tile | burst MHz (passes) | burst rate | sustained MHz | sustained rate | board W | die °C | limit (burst / sustained) | c W |
|---|---|---|---|---|---|---|---|---|
| fp32 `l0_mlp_up` | 708.8 (709.8 / 707.8) | 10.59 TFLOPS | 608.2 | 9.32 TFLOPS | 54.8 | 66.0 | power / thermal | 25.47 |
| fp32 `l6_mlp_down` | 699.0 (700.0 / 698.0) | 10.52 TFLOPS | 600.5 | 9.21 TFLOPS | 53.8 | 66.3 | power / thermal | 25.46 |
| fp32 `l6_attn_qk` | 702.0 (705.9 / 698.0) | 10.54 TFLOPS | 602.8 | 9.25 TFLOPS | 53.9 | 66.1 | power / thermal | 25.22 |
| fp32 randn (anchor) | 706.0 (706.0 / 705.9) | 10.66 TFLOPS | 600.1 (600.3 / 600.0) | 9.21 TFLOPS | 53.8 | 66.4 | power / thermal | 25.59 |
| fp16 `l0_mlp_up` | 727.0 (728.0 / 726.0) | 21.86 TFLOPS | 619.9 | 18.92 TFLOPS | 53.2 | 65.8 | power / thermal | 22.90 |
| fp16 `l6_mlp_down` | 725.5 (726.0 / 725.0) | 21.91 TFLOPS | 602.8 | 18.51 TFLOPS | 51.5 | 66.0 | power / thermal | 22.92 |
| fp16 `l6_attn_qk` | 734.4 (736.7 / 732.0) | 22.14 TFLOPS | 612.3 | 18.74 TFLOPS | 51.6 | 65.9 | power / thermal | 22.34 |
| fp16 randn (anchor) | 721.2 (720.4 / 722.0) | 21.82 TFLOPS | 610.0 (604.6 / 615.3) | 18.69 TFLOPS | 52.4 | 66.0 | power / thermal | 23.15 |
| int8 `l0_mlp_up` | 777.0 (800.0 / 754.0) | 81.61 TOPS | 794.4 | 83.70 TOPS | 51.6 | 64.5 | none / none | 8.24 |
| int8 `l6_mlp_down` | 800.0 (800.0 / 800.0) | 84.31 TOPS | 793.6 | 83.63 TOPS | 50.2 | 64.3 | none / none | 7.56 |
| int8 `l6_attn_qk` | 800.0 (800.0 / 800.0) | 84.31 TOPS | 800.0 | 84.33 TOPS | 50.7 | 64.5 | none / none | 7.53 |
| int8 full (anchor) | 800.0 (800.0 / 800.0) | 84.31 TOPS | 774.7 | 80.85 TOPS | 51.4 | 65.1 | none / thermal | 8.88 |

c is the switching term of E64's method: whole-board switching at 600 MHz and 0.517 V, referred to a 58 °C die, over
E64's fitted baseline B_f, not over idle; never quote it as the power a tile draws ([`results.json`](results.json)
`cells.*.c_w`; E83 C2). What a tile draws while it runs is the board W column (sustained) and p800 (the first second
at 800 MHz, [`tables.md`](tables.md)): 82.2–83.1 W for the real fp32 tiles, 76.8–77.9 W for fp16 and 46.8–47.6 W for
int8, against 81.9, 78.4 and 49.5 W for randn, randn and int8 full. The raw p800 also follows the start temperature:
fp32 randn's first pass started at 50 °C (80.4 W) and the real fp32 tiles' at 52–56 °C, which is why real fp32's raw
p800 reads above randn's. At equal starts (round 2: every fp32 tile, randn and zeros from 56 °C) the real tiles' p800
above zeros is 0.995 / 0.990 / 0.982 of randn's, the same direction as c
([`corrections-check.txt`](corrections-check.txt) C7).

### 3. Real against random, like with like

The sharpest comparison is the switching term above zeros as a share of the same-session reference's,
(c_tile − c_zeros) / (c_ref − c_zeros), every c from this session's bursts ([`results.json`](results.json)
`posthoc.like_with_like_ratios`, `rules.E87-S3`). It cancels the card's scale and the session's drift; a tile's two
rounds differ by 0.0000–0.0040 in fp32 and fp16 and by 0.011–0.039 in int8 (half-spreads 0.0000–0.0020 and
0.006–0.020; [`checks.txt`](checks.txt) K1, labelled; [`corrections-check.txt`](corrections-check.txt) C5).

| tile | measured share of the reference | Q130(n) predicted | rounds 1 / 2 |
|---|---|---|---|
| fp32 `l0_mlp_up` / randn | **0.995** | 0.989 | 0.9954 / 0.9953 |
| fp32 `l6_mlp_down` / randn | **0.995** | 0.986 | 0.9958 / 0.9936 |
| fp32 `l6_attn_qk` / randn | **0.985** | 0.989 | 0.9860 / 0.9840 |
| fp16 `l0_mlp_up` / randn | **0.988** | 0.980 | 0.9904 / 0.9864 |
| fp16 `l6_mlp_down` / randn | **0.990** | 0.964 | 0.9895 / 0.9895 |
| fp16 `l6_attn_qk` / randn | **0.962** | 0.972 | 0.9622 / 0.9626 |
| int8 `l0_mlp_up` / full | **0.904** | 0.835 | 0.9243 / 0.8852 |
| int8 `l6_mlp_down` / full | **0.803** | 0.735 | 0.8087 / 0.7976 |
| int8 `l6_attn_qk` / full | **0.797** | 0.815 | 0.7911 / 0.8032 |

- **fp32 and fp16: in each of the three GPT-2 tiles measured, real data cost about what random data cost, a little
  less.** Every real fp32 and fp16 tile switches less than random data of its format, by 0.5–1.5% (fp32) and 1.0–3.8%
  (fp16); the format means are 0.992 and 0.980. Three tiles from one model are a small sample: across them the means
  sit t = 2.48 (fp32) and 2.25 (fp16) below 1.000 on 2 df (one-sided p 0.07 and 0.08), although each tile's two rounds
  agree closely and round 2 alone, every burst from 55–56 °C, keeps all six signs ([`checks.txt`](checks.txt) K1;
  [`corrections-check.txt`](corrections-check.txt) C4). The tiles differ from each other more than the rounds do: the
  attention tile is the cheapest in both formats. Q130(n) got the direction and the size (predicted 0.986–0.989 and
  0.964–0.980) but not the order of the three tiles.
- **In clock terms, fp32 shows nothing and fp16 perhaps 1%.** Real minus randn in the burst is −2.7 MHz in fp32 and
  +7.8 MHz (1.1%) in fp16, the direction the fp16 tiles' lower switching predicts (+5 MHz registered); all six real
  fp16 passes ran above both randn passes. A three-tile mean minus one cell carries ±6.1 MHz (1 σ; a two-pass cell's
  random part is 5.3 MHz, E83 C6), so +7.8 is 1.3 σ: inside S2's ±15 MHz bar, and not established. Sustained, the
  differences are +3.7 and +1.7 MHz ([`results.json`](results.json) `rules.E87-S2`;
  [`corrections-check.txt`](corrections-check.txt) C2).
- **int8: real tensors are small integers, and cost clearly less than uniform random bytes.** 0.80–0.90 of int8 full,
  mean 0.835 (Q130(n): 0.735–0.835, mean 0.795; its calibration range 0.735–0.869). Two of the three read 0.07 above
  their points (`l0_mlp_up`, `l6_mlp_down`), all inside Amendment 1's intervals.

### 4. int8: real and random data both sit at the edge of the 65 °C trip

In the same session the three real int8 tiles sustained **793.6–800 MHz** with the limit `none` (die 64.3–64.5 °C,
board 50.2–51.6 W), and int8 full was thermal-held at **774.7 MHz** (65.1 °C, 51.4 W). **That shows no difference
between real and random int8.** int8 full itself held 793.4 MHz with the limit `none` in both of E80's runs (796.7 and
790.0; 0.967 and 0.928 of the last 40 s at 800 MHz) and was thermal-held at 786.5 in E83's one run (0.865 at 800), so
single sustained runs land on either side of the trip whatever the data. Which side a run lands on follows the heat
path's scatter: `l0_mlp_up` drew more sustained board power than int8 full (51.60 against 51.41 W) yet ran 0.73 °C
below E87's die line, while int8 full sat on it (−0.04 °C), and the line's rms is 0.42 °C
([`checks.txt`](checks.txt) K4; [`corrections-check.txt`](corrections-check.txt) C3). The real tiles' mean is 21 MHz
above int8 full here, 1.3 σ for single runs on and near the knee (±16 MHz); settling a sustained difference needs
several runs per kind in one session. In the burst every int8 tile runs at 800 MHz (84.3 TOPS) except one pass of
`l0_mlp_up`, which the governor's idle reset dropped to 754.0 (800.0 with the reset samples set aside, A1's view;
[`checks.txt`](checks.txt) K3). The reset fired in 4 of 183 work processes (2.2%, E80's rate): that burst pass, two
dips in int8 zeros' sustained run and one in int8 full's (774.2 without it).

### 5. The heat path and the anchors

- **The anchors tie** (R5): fp32 randn 706.0 / 600.1 MHz against E80's 711.9 / 604.3 and E83's 714.7 / 612.0; fp16
  randn 721.2 / 610.0 against 730.6 / 609.5 and 724.8 / 609.0; the zeros at 800 in the burst and 788.5–800 sustained.
- **The switching term is stable across three sessions on this card**: fp32 randn's c 25.55 / 25.59 / 25.585 W in E80,
  E83 and E87, fp16 randn's 23.07 / 23.05 / 23.15 and int8 full's 8.99 / 8.98 / 8.88 (the zeros' c spreads 1.55–2.49 W
  and moves 0.3–0.5 W between rounds; [`checks.txt`](checks.txt) K2).
- **The heat path was 0.5 °C warmer than E80's** (E87's die line 41.69 + 0.456 °C/W over its 17 sustained runs, rms
  0.42 °C; +0.515 °C at E80's slope, where E83 read −0.149: [`results.json`](results.json) `posthoc.die_line_e87`). In
  the governor's terms the card shed 48.47 W of 58 °C-referred power at the trip instead of 49.75 (arm a-adj E87,
  labelled). That moves the fp32 and fp16 sustained cells little (they sit near the 600 MHz floor). It makes a
  trip likelier for every int8 run but does not decide which run trips: the scatter about the line (rms 0.42 °C) is as
  large as the shift, and int8 full tripped in E83 too, on a heat path 0.15 °C cooler than E80's (§4). The a-adj arms
  do not improve R3: 6.25 MHz (a-adj E87) and 6.08 (a-adj E83) against 6.11.
- **The bursts ran a little slower than predicted**: −1.9 to −13.4 MHz for the six fp32 and fp16 tiles, and the randn
  anchors −5.9 and −9.4 MHz below E80's cells. The relation on each tile's measured c gives nearly the same clocks as on
  Q130(n)'s c (S1), so the shortfall is in the session's effective cap, not in the predicted power. The second round
  launched 2.3 °C warmer on average over the 15 kinds (1.4 °C on the eight power-limited kinds), and those eight ran
  2.3 MHz slower in it (sd 2.9; E83's order effect was 7.9 MHz), a small part of it
  ([`corrections-check.txt`](corrections-check.txt) C6).

## What was registered, and what happened

Everything ran as registered: 47 runs, no cap reached (35.5 of 38 card-minutes), no safety stop (peaks: die 67 °C,
board 88.5 W; stops 85 °C and 97 W on three samples), every launch rc 0, all 47 samplers started on attempt 1 and
stopped by the runner's SIGTERM with rc 0, no error mark. The plan said about 34 card-minutes; the cool gates held the
card for 79 s before bursts and 271 s before sustained runs in all. No amendment was written and no rule, threshold,
population or prediction was changed after `7f84f454`. Two files were added after the pre-registration and decide
nothing: [`tables_e87.py`](../../../../tools/claims-v3/kspeed/e87/tables_e87.py), the formatting script, written while
the session ran and before any result was read, and [`checks.py`](checks.py) (labelled checks K1–K4), written after.
After verification, [`corrections-check.py`](corrections-check.py) and [`final-config.txt`](final-config.txt) were
added (Corrections after verification); they decide nothing either.

## What it fills, and what it changes

- **The blog's kinds table gains nine real-data rows** with measured burst and sustained clocks, TFLOPS / TOPS, board W,
  die °C, limits and the switching term ([`cells.json`](cells.json), 174 cells; `interval` holds only an
  uncertainty: the two passes, the two runs, or one run's σ from E83 C3).
- **For the blog's argument**: in each of the three GPT-2 tiles measured, a real network's tensors in fp32 and fp16 give
  the chip nothing to skip (no zero word) and switch 0.5–3.8% less than random numbers (three tiles of one model: t 2.48
  and 2.25 on 2 df). That buys nothing measurable in fp32 (−2.7 MHz) and perhaps 1% of burst clock in fp16 (+7.8 MHz,
  1.3 σ, the predicted direction; not established); sustained, both sit at random data's clock. In int8 they are small
  integers and switch 0.80–0.90 of uniform random bytes. They burst at 800 MHz, as random int8 does, apart from one pass
  the idle reset hit; sustained, real and random int8 both sit at the edge of the 65 °C trip, and single runs land on
  either side of it whatever the data, so no sustained difference is shown. The measured share confirms Q130(n)'s
  direction in all three formats.
- **For the hub's Levels and Status**: the power → clock link holds out of sample on real data: E83's relation on each
  tile's measured power gives the clocks to 10.1 MHz rms in the burst and 5.2 sustained (S1), and the clocks frozen
  before the run held (R1–R4). Those clock rules do not test the kind → power link, because the real tiles' clocks sit
  within a few MHz of random data's: a no-model baseline (each real tile = E80's random cell for its format) scores
  9.75 and 5.14 MHz against the frozen points' 10.68 and 6.11. The kind → power link's test is like with like: S4's
  int8 bar (0.835 < 0.9), which "real = random" fails, and the fp32 and fp16 sign (all six tiles below 1). Per tile
  the predictor misses the order within fp32 and fp16 (it put `l6_mlp_down` cheapest; measured, the attention tile is)
  and reads int8 `l0_mlp_up` and `l6_mlp_down` 0.07 low, although its ratio errors are smaller than "real = random"'s
  in all three formats, clearly only in int8 (rms 0.057 against 0.172; fp32 0.007 against 0.010, fp16 0.017 against
  0.024; post hoc, [`corrections-check.txt`](corrections-check.txt) C1). Open: the tiles' order within a format (the
  predictor's terms are not mechanisms), whether fp32's and fp16's 1–2% holds beyond three tiles of one model, and any
  int8 real-vs-random sustained difference, which needs several runs per kind in one session.

## Card state

aifoundry2 card 0 free at 20:25:35 PDT (`et-who`: no process holds a device node or card lock), after the final
read-only `ettelem config` under the card lock (low_power, 600 MHz, 519 mV, TDP 65 W, threshold 65 °C;
[`final-config.txt`](final-config.txt); the session's own end query at 20:25:19.7 in `s1/queries.jsonl` reads the
same). `who` was empty
at the smoke and at the session's start, and the runner's other-user check passed before every launch process. The box's lab checkout was fast-forwarded `8b441fd9` → `7f84f454` (its
untracked `.claude/` left as found), and every file the session ran was checked by sha256 against the Intel's before
the claim; the run directories `build/e87/runs/{smoke,s1}` remain on the box.

## Files

| file | what |
|---|---|
| `s1/`, `smoke/` | the raw sessions as the runner wrote them (telemetry and launches gzipped): `session.json`, `kspeed.json`, `e87.json`, `runs.jsonl`, `queries.jsonl`, `marks.jsonl`, `tel/`, `sp/`, `logs/`, `manifest.txt`, `run.out` |
| `results.json`, `reduce.txt` | the registered reduction's output (`reduce_e87.py s1 --out results.json`) |
| `tables.md`, `cells.json` | the tables and the blog's cells (`tables_e87.py results.json --cells cells.json`; formatting only) |
| `checks.py`, `checks.txt` | post-hoc checks K1–K4, labelled |
| `final-config.txt` | the read-only `ettelem config` under the card lock at 20:25:35 that closed the card time, as printed (committed after verification, C9) |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind Corrections after verification: every number it quotes, from the committed files (standard library only) |

Reproduce from the top of the repository:

```bash
python3 tools/claims-v3/kspeed/e87/reduce_e87.py docs/reports/data/2026-10-31-e87-real-tensors-speed/s1 --out /tmp/results.json > /tmp/reduce.txt
python3 tools/claims-v3/kspeed/e87/tables_e87.py docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json --cells /tmp/cells.json > /tmp/tables.md
python3 docs/reports/data/2026-10-31-e87-real-tensors-speed/checks.py
python3 docs/reports/data/2026-10-31-e87-real-tensors-speed/corrections-check.py
```

## Corrections after verification (Sat 31 Oct 2026)

An independent verifier checked E87 after the data commit (`bc96f37d`). It re-derived every registered number,
recomputed the 30 bursts and 17 sustained clocks from the raw 10 Hz telemetry with its own code (all within 0.7 MHz),
and reproduced `predictions.json`, `results.json`, `reduce.txt`, `tables.md`, `cells.json` and `checks.txt` byte for
byte. It found the measurement, its timing and its safety sound, and three major and seven minor faults in how the
numbers were stated. Each is corrected above, desk only: no card was touched, nothing was re-run, and no registered
prediction, rule, number or verdict changed. All nine rules still pass. Every number below is printed by
[`corrections-check.py`](corrections-check.py) into [`corrections-check.txt`](corrections-check.txt), under the section
named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Major: the clock rules were read as a test of the power predictor.** What it changes said "the chain kind → power → clock now holds out of sample on real data (R1, R3, S1), with the power predicted from the numbers alone (S3, S4)". The frozen clocks sit within a few MHz of the random-number cells: a baseline with no model (each real tile gets E80's cell for its format's random reference) scores burst 9.75 MHz over the nine and 7.39 over the six fp32 and fp16 tiles (frozen points 10.68 and 9.10), and sustained 5.14 and 5.67 (6.11 and 7.02). S3's amended intervals hold 1.000 for 8 of the 9 tiles (the frozen ones for 6 of 9), so "real = random" passes S3 too. S1 tests E83's relation, not the predictor | §1, the R1, R3, S3 and S4 rows, and What it changes. R1–R4 and S1 show that E83's relation carries over to real data and that real fp32 and fp16 data run at about random data's speed. The predictor's test is S4's int8 bar, the fp32 and fp16 sign, and the per-tile ratios: its errors there are smaller than "real = random"'s in all three formats, clearly only in int8 (rms 0.057 against 0.172; post hoc). The baseline sits beside R1 and R3 |
| C2 | **Major: fp16's burst difference was called noise.** §3 said "in clock terms the difference is lost in the noise", and the blog text handed on said "+7.8 MHz … inside the noise of the comparison (about ±6 MHz)" and "buys no measurable speed". +7.8 is 1.3 σ on ±6.1 MHz, all six real fp16 passes ran above both randn passes, and the registered expectation was +5 | §3 and What it changes: fp32's −2.7 MHz shows nothing; fp16's +7.8 MHz (1.1%) is in the predicted direction, inside S2's bar and not established. The ±6.1 MHz stays, as the difference's 1 σ |
| C3 | **Major: §4's title said real int8 "stays below the thermal trip, random data does not"**, and the blog text handed on said real int8 held 793.6–800 "where random int8 throttled to 774.7". int8 full held 793.4 MHz with no limit in both of E80's runs and tripped in E83 (786.5) and here (774.7); `l0_mlp_up` drew more board power than int8 full yet ran 0.73 °C below the die line while int8 full sat on it (rms 0.42 °C) | §4 is retitled: single runs land either side of the trip whatever the data, so no real-against-random sustained difference is shown. §5 no longer calls the warmer heat path "the likely reason int8 full sustained lower": it makes a trip likelier for every int8 run but does not pick the run |
| C4 | **fp32's and fp16's lower switching was stated as a property of real tensors.** It rests on three tiles of one model: t = 2.48 and 2.25 on 2 df against 1.000 (one-sided p 0.07 and 0.08) | §3 and What it changes say "in each of the three GPT-2 tiles measured" and give the t; round 2 alone keeps every sign. S4's PASS stands as registered |
| C5 | **"The two rounds reproduce each tile's ratio to 0.0001–0.0020 (fp32, fp16) and 0.006–0.020 (int8)"**: those were half-spreads | §3 gives the round-to-round differences, 0.0000–0.0040 and 0.011–0.039, with the half-spreads beside them |
| C6 | **"The second round launched 2.3 °C warmer and ran 2.3 MHz slower on the eight power-limited kinds"** mixed two populations: +2.33 °C is the mean over all 15 kinds, +1.38 °C over the eight | §5 names both |
| C7 | **Real fp32's raw p800 (82.2–83.1 W) read above randn's (81.9 W)**, next to §3's "real fp32 switches less", with no explanation. randn's first pass started at 50 °C, the real tiles' at 52–56 °C | §2: at equal starts (round 2, all from 56 °C) the shares above zeros are 0.995 / 0.990 / 0.982, the same direction as c |
| C8 | **The blog text handed on gave "800 MHz, 84.3 TOPS" for every int8 burst**, which is A1's reset-free view | That text now names the one pass the idle reset hit (754 MHz); §4 already did |
| C9 | **The 20:25:35 config read was cited but not committed**; it was in the lane's scratch | Committed as [`final-config.txt`](final-config.txt) (no logins in it), and Card state also cites the committed end query (20:25:19.7, `s1/queries.jsonl`, the same values) |
| C10 | **Process: the lane's local probe script put its ssh in the background (`&`) behind a kill loop**, which the workflow's rules forbid. It ran the final config read and did not hang | Nothing in the repository to change; recorded here. Its output is `final-config.txt` (C9) |

One proposed fix was not taken as written: C2 asked to drop the "±6 MHz" clause. The figure is right, as the 1 σ of a
three-tile mean minus one cell (5.3 × √(1/3 + 1) = 6.1 MHz), so it stays; what is dropped is the claim that +7.8 MHz
lies inside it.
