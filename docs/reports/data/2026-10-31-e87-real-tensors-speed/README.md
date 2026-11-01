# E87 data: the speed of real GPT-2 tensors under aifoundry2's own governor (Q130, Sat 31 Oct 2026)

Q130(n)'s nine real tiles, cut from GPT-2 small (layer 0's MLP up-projection, layer 6's MLP down-projection and layer
6's attention QKᵀ, each in fp32, fp16 and int8; [`tools/claims-v3/kinds/real/`](../../../../tools/claims-v3/kinds/real/README.md)),
on aifoundry2 card 0 under the card's own governor. E80's anchors ran again in the same session: fp32 randn, fp16
randn, int8 full, and fp32, fp16 and int8 zeros. Each tile got a **burst on a cool die**, run twice, and a **sustained
run** of about 76 s (fp32 randn and fp16 randn twice). **Nothing was set on the card**: the TDP and the threshold read
65 W and 65 °C at all 47 per-run reads of `ettelem config`, the smoke's three, the session's start and end, and once
more under the card lock at 20:25:35 PDT, before the release. The sampler ran without `--reset-ms`.

The pre-registration is [`tools/claims-v3/kspeed/e87/`](../../../../tools/claims-v3/kspeed/e87/README.md)
(`7f84f454`, pushed 19:47:42 PDT). Its frozen predictions are
[`predictions.json`](../../../../tools/claims-v3/kspeed/e87/predictions.json), sha256 `025f4e15…`: Q130(n)'s frozen
points (`predictions-real.json`, sha256 `bab33bee…`) and Amendment 1's scoring intervals (`amendment-1.json`,
`f32e8a90…`). The card was claimed in `#community-lab` at 19:48:48 and released by editing the same post at 20:25. **No
amendment and no departure from the registered design.** While the session ran, the lane read only its progress lines
(run names, return codes, config reads); the reduction first ran on the complete session, after the release.

| session | PDT | what |
|---|---|---|
| `smoke/` | 19:49:01–19:49:22 | three 2 s launches of real tiles (fp32 `l6_attn_qk`, fp16 `l0_mlp_up`, int8 `l6_mlp_down`): 546.0 / 546.0 / 318.0 cycles per op, config 65 W / 65 °C; not analysed |
| `s1/` | 19:49:49–20:25:19 | the registered session, 47 runs, exit 0, **35.5 card-minutes** (35.8 with the smoke, of the 40 allowed): `BURST` 30 runs (19:49:51–19:57:00), `SUS` 17 runs (19:57:06–20:25:13) |

## Results first

### 1. All nine registered rules pass

**Q130(n)'s frozen speeds hold for real data.** E83's power-to-clock relation, fed Q130(n)'s predicted power for tiles
no card had run, hit the nine burst clocks to **10.7 MHz rms** (7.4 with the governor's one idle reset set aside) and
the nine sustained clocks to **6.1 MHz rms**, and called all nine sustained limits. The like-with-like power
predictions hold too, in direction and inside their intervals: measured in one session, real fp32 tiles switch
0.985–0.995 of random fp32's power above zeros, real fp16 0.962–0.990 of random fp16's, and real int8 0.797–0.904 of
uniform random int8's. Each verdict is scored exactly as registered ([`results.json`](results.json) `rules`,
[`reduce.txt`](reduce.txt)).

| rule | verdict | what the data say |
|---|---|---|
| **E87-R1** burst rms ≤ 25 MHz against Q130(n)'s frozen points | **PASS** | **10.7 MHz** over the nine; 7.4 on A1's reset-free cells; 9.1 over the six fp32 and fp16 tiles. Every fp32 and fp16 tile ran 1.9–13.4 MHz below its point; int8 `l0_mlp_up`'s −23.0 is one pass the idle reset hit (§4) |
| **E87-R2** sustained limit right for ≥ 7 of 9 | **PASS** | **9 of 9**: the six fp32 and fp16 tiles `thermal` (share at 800 MHz 0.000–0.018), the three int8 tiles `none` (0.967–1.000) |
| **E87-R3** sustained rms ≤ 25 MHz | **PASS** | **6.1 MHz**; 7.0 over the six fp32 and fp16 tiles. The largest miss is fp16 `l6_mlp_down`, 602.8 against 617.6 (−14.8): its measured c is 0.56 W above Q130(n)'s, worth 4 MHz (the relation on its measured c gives 613.5), and the session's two fp16 randn runs differ by 10.7 MHz |
| **E87-R4** ≥ 7 of 9 inside Amendment 1's burst intervals and ≥ 7 of 9 inside its sustained intervals | **PASS** | burst **8 of 9** (int8 `l0_mlp_up`'s 777.0 lies outside the single point 800; 9 of 9 reset-free), sustained **9 of 9**. Inside the frozen D-propagated ranges: 8 of 9 and 6 of 9 |
| **E87-R5** anchors within 25 MHz of their tie cells | **PASS** | all twelve rows; the largest is int8 full sustained, 774.7 against E80's 793.4 (−18.7; E83 786.5), in a session whose heat path ran 0.5 °C warmer than E80's (§5) |
| **E87-S1** the relation on measured c, burst and sustained rms ≤ 15 MHz | **PASS** | burst **10.1** (6.6 reset-free), sustained **5.2 MHz** |
| **E87-S2** real within ±15 MHz of same-session randn's burst, fp32 and fp16 | **PASS** | fp32 **−2.7 MHz** (703.3 against 706.0), fp16 **+7.8 MHz** (729.0 against 721.2); sustained +3.7 and +1.7 (labelled) |
| **E87-S3** like-with-like ratio inside its S3 interval for ≥ 7 of 9 | **PASS** | **9 of 9** (9 of 9 inside the frozen intervals too). The measured c lies inside Q130(n)'s converted c interval for 9 of 9 (frozen and amended) |
| **E87-S4** format means below 1 (fp32), 1 (fp16), 0.9 (int8) | **PASS** | fp32 **0.992**, fp16 **0.980**, int8 **0.835** |

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
int8, against 81.9, 78.4 and 49.5 W for randn, randn and int8 full.

### 3. Real against random, like with like

The sharpest comparison is the switching term above zeros as a share of the same-session reference's,
(c_tile − c_zeros) / (c_ref − c_zeros), every c from this session's bursts ([`results.json`](results.json)
`posthoc.like_with_like_ratios`, `rules.E87-S3`). It cancels the card's scale and the session's drift; the two rounds
reproduce each tile's ratio to 0.0001–0.0020 in fp32 and fp16 and 0.006–0.020 in int8 ([`checks.txt`](checks.txt) K1,
labelled).

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

- **fp32 and fp16: real tensors cost about what random data cost, a little less.** Every real fp32 and fp16 tile
  switches less than random data of its format, by 0.5–1.5% (fp32) and 1.0–3.8% (fp16); the format means are 0.992
  and 0.980. The tiles differ from each other more than the rounds do: the attention tile is the cheapest in both
  formats. Q130(n) got the direction and the size (predicted 0.986–0.989 and 0.964–0.980) but not the order of the
  three tiles. In clock terms the difference is lost in the noise: real minus randn is −2.7 MHz (fp32) and +7.8 MHz
  (fp16) in the burst (a cell's random part is about 5.3 MHz, so a difference carries about ±6 MHz, 1 σ) and +3.7 and
  +1.7 MHz sustained ([`results.json`](results.json) `rules.E87-S2`).
- **int8: real tensors are small integers, and cost clearly less than uniform random bytes.** 0.80–0.90 of int8 full,
  mean 0.835 (Q130(n): 0.735–0.835, mean 0.795; its calibration range 0.735–0.869). Two of the three read 0.07 above
  their points (`l0_mlp_up`, `l6_mlp_down`), all inside Amendment 1's intervals.

### 4. int8: real data stays below the thermal trip, random data does not

In the same session, the three real int8 tiles sustained **793.6–800 MHz** with the limit `none` (die 64.3–64.5 °C,
board 50.2–51.6 W), while int8 full was thermal-held at **774.7 MHz** (65.1 °C, 51.4 W). That is +21 MHz for the real
tiles' mean, against about ±16 MHz (1 σ) for single runs on and near the knee, so it is suggestive, not settled; int8
full itself sustained 793.4 in E80 and 786.5 in E83 ([`checks.txt`](checks.txt) K4). In the burst every int8 tile runs
at 800 MHz (84.3 TOPS) except one pass of `l0_mlp_up`, which the governor's idle reset dropped to 754.0 (800.0 with
the reset samples set aside, A1's view; [`checks.txt`](checks.txt) K3). The reset fired in 4 of 183 work processes
(2.2%, E80's rate): that burst pass, two dips in int8 zeros' sustained run and one in int8 full's (774.2 without it).

### 5. The heat path and the anchors

- **The anchors tie** (R5): fp32 randn 706.0 / 600.1 MHz against E80's 711.9 / 604.3 and E83's 714.7 / 612.0; fp16
  randn 721.2 / 610.0 against 730.6 / 609.5 and 724.8 / 609.0; the zeros at 800 in the burst and 788.5–800 sustained.
- **The switching term is stable across three sessions on this card**: fp32 randn's c 25.55 / 25.59 / 25.585 W in E80,
  E83 and E87, fp16 randn's 23.07 / 23.05 / 23.15 and int8 full's 8.99 / 8.98 / 8.88 (the zeros' c spreads 1.55–2.49 W
  and moves 0.3–0.5 W between rounds; [`checks.txt`](checks.txt) K2).
- **The heat path was 0.5 °C warmer than E80's** (E87's die line 41.69 + 0.456 °C/W over its 17 sustained runs, rms
  0.42 °C; +0.515 °C at E80's slope, where E83 read −0.149: [`results.json`](results.json) `posthoc.die_line_e87`). In
  the governor's terms the card shed 48.47 W of 58 °C-referred power at the trip instead of 49.75 (arm a-adj E87,
  labelled). That moves the fp32 and fp16 sustained cells little (they sit near the 600 MHz floor), and it is the
  likely reason int8 full sustained lower than in E80 and E83. The a-adj arms do not improve R3: 6.25 MHz (a-adj E87)
  and 6.08 (a-adj E83) against 6.11.
- **The bursts ran a little slower than predicted**: −1.9 to −13.4 MHz for the six fp32 and fp16 tiles, and the randn
  anchors −5.9 and −9.4 MHz below E80's cells. The relation on each tile's measured c gives nearly the same clocks as on
  Q130(n)'s c (S1), so the shortfall is in the session's effective cap, not in the predicted power. The second round
  launched 2.3 °C warmer and ran 2.3 MHz slower on the eight power-limited kinds (sd 2.9; E83's order effect was
  7.9 MHz), a small part of it.

## What was registered, and what happened

Everything ran as registered: 47 runs, no cap reached (35.5 of 38 card-minutes), no safety stop (peaks: die 67 °C,
board 88.5 W; stops 85 °C and 97 W on three samples), every launch rc 0, all 47 samplers started on attempt 1 and
stopped by the runner's SIGTERM with rc 0, no error mark. The plan said about 34 card-minutes; the cool gates held the
card for 79 s before bursts and 271 s before sustained runs in all. No amendment was written and no rule, threshold,
population or prediction was changed after `7f84f454`. Two files were added after the pre-registration and decide
nothing: [`tables_e87.py`](../../../../tools/claims-v3/kspeed/e87/tables_e87.py), the formatting script, written while
the session ran and before any result was read, and [`checks.py`](checks.py) (labelled checks K1–K4), written after.

## What it fills, and what it changes

- **The blog's kinds table gains nine real-data rows** with measured burst and sustained clocks, TFLOPS / TOPS, board W,
  die °C, limits and the switching term ([`cells.json`](cells.json), 174 cells; `interval` holds only an
  uncertainty: the two passes, the two runs, or one run's σ from E83 C3).
- **For the blog's argument**: a real network's tensors in fp32 and fp16 give the chip nothing to skip (no zero word)
  and switch 0.5–3.8% less than random numbers, which buys no speed you can measure; in int8 they are small integers and
  switch 0.80–0.90 of random bytes; in this session that kept the card at 793.6–800 MHz sustained while random int8
  throttled to 774.7 (single runs: suggestive, not settled). The measured share confirms Q130(n)'s direction in all
  three formats.
- **For the hub's Levels and Status**: the chain kind → power → clock now holds out of sample on real data (R1, R3, S1),
  with the power predicted from the numbers alone (S3, S4). The open parts are the order of the tiles within a format
  (the predictor's terms are not mechanisms) and int8's real-vs-full sustained difference, which needs replicate runs.

## Card state

aifoundry2 card 0 free at 20:25:35 PDT (`et-who`: no process holds a device node or card lock), after the final
read-only `ettelem config` under the card lock (low_power, 600 MHz, 519 mV, TDP 65 W, threshold 65 °C). `who` was empty
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

Reproduce from the top of the repository:

```bash
python3 tools/claims-v3/kspeed/e87/reduce_e87.py docs/reports/data/2026-10-31-e87-real-tensors-speed/s1 --out /tmp/results.json > /tmp/reduce.txt
python3 tools/claims-v3/kspeed/e87/tables_e87.py docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json --cells /tmp/cells.json > /tmp/tables.md
python3 docs/reports/data/2026-10-31-e87-real-tensors-speed/checks.py
```
