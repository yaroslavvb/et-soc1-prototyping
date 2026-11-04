# E166: the heat replicate on aifoundry3 card 0 - the second session's four plateaus from the bits read 0.45 °C rms on M8 (E154: 0.37), RK3-a FAIL (2 of 4), RK3-c FAIL (the large rises 1.8-3.2% low given the watts), G_A SLOW STAGE SEEN by 0.008 °C while SL reads SLOPE NOT SEEN; every frozen band PASS

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 9** (heat over minutes), **item 8** (the heat path between sessions) and **item 6** (the power model). It answers **rank 3 of Q139's
final critic**, "Heat over minutes from the bits, a second session per card", its aifoundry3 half (E167 is aifoundry2's), as Q140's final critic
left it (`card_half[3]`). Wed 4 Nov 2026 (week 45), the card half of Q141, on the owner's go of that day (about 13:55 PST). The mandate: his words
of 2 November 2026 ("settle any unanswered questions regarding horace's power model"), with his goal "to be able to predict the power requirement
and heat generation of various kinds of numeric computations as accurately as possible".*

- **Card:** aifoundry3 card 0, **600 MHz in all 44,488 samples** (the smoke's 622, the pass's 43,866). `ettelem config` through E128's guard at
  the session's start (14:20:51 PST) and end (15:35:05): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV both times. **Nothing was set.**
- **Card session** 14:20:51-15:35:05 PST, **74.2 card-minutes**, inside the registered 76: the smoke with its five stop tests (block 16601,
  14:20:52-14:21:55), then **the full design** in one measured pass, 16620 (14:21:55-15:35:05). No subset, no exclusion, no departure after data.
- **G0, the start gate, passed:** R0's room (the 34-sensor mean over its last 120 s) read **51.924 °C** (firmware 51.0 °C) at 14:27:00, at or
  under 53.0 °C. So K_S ran the warm-room period, 3.20 s every 4.97 s (E154's room rule), and K_OL its full 25 minutes (its frozen in-launch
  peak at this room 65.90 °C, under the 67.5 °C line).
- **Every dispatch's C is bit-exact:** 6,692 of 6,692 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`): the smoke's 48 and
  the pass's 6,644 (fp32 4,130, int8 2,562; no ROUNDING, UNMODELLED or FAIL; no broken record), in the pass's 493 process launches.
- **Every device-management command sent was a read**, as registered and audited (§ Device commands sent). **No statistics reset was sent.**
- **No stop fired in the measured pass.** The highest live readings were 44.2 W board (K_S) and 66 °C `minshire[0]`, against the hold's 65 W /
  72 °C, the gate's 70 °C and the session's 74 °C. The five stop tests in the smoke all fired as designed on live samples.

## Results

**In plain words.** Four kinds from blind pool 6, held for 10 minutes once before on this card (E154, Tue 3 Nov), were held again a day later,
with the watts predicted from each tile's bits (M8) and a frozen heat model (Q138(t)'s chain) turning them into a die temperature over 10
minutes; one of them was held for 25 minutes. Every plateau landed inside its frozen 95% band. But the critic's stricter per-hold rule was met by 2 of the 4 replicate readings,
and given the measured watts the heat model still reads the large rises low, by less than in E154.

| reading (tile) | kernel duty | measured rise (°C) | from the bits, M8: predicted / error / checkpoints' rms (°C) | M7 / M6 error | given the watts (arm A): error, share of rise | band | RK3-a |
|---|---|---|---|---|---|---|---|
| K_S (`fp32.real_smol_softmax_v_causal`) | 0.6962 | 12.726 | 12.973 / **−0.248** / 0.343 | −0.186 / −0.117 | +0.233, 1.83% | PASS | not inside (rms over 0.278) |
| K_Q (`int8.real_qwen_w8a8_v`) | 0.9621 | 6.663 | 6.676 / **−0.014** / 0.103 | −0.030 / −0.065 | +0.200, 3.00% | PASS | **inside** |
| K_L (`int8.b_line_zero_ff`) | 0.9618 | 4.409 | 3.539 / **+0.869** / 0.600 | +0.505 / +0.047 | +0.403, 9.15% | PASS | not inside (over 0.574) |
| K_O's window (`fp32.a_onebit_b5_third`, 0-600 s) | 0.9609 | 11.268 | 11.231 / **+0.037** / 0.174 | +0.208 / +0.411 | +0.242, 2.15% | PASS | **inside** |
| K_OL's long window (the same hold, its last 300 s of 1,500) | 0.9609 | 12.363 | 11.992 / +0.371 / 0.281 | +0.553 / +0.769 | +0.400, 3.23% | PASS | (not one of RK3-a's four) |

The error is measured minus predicted, over each hold's anchor (the rest die just before it). Source: [`scored.json`](scored.json) ›
`readings`, `rules`; the scorer [`score_e166.py`](../../../../tools/claims-v3/e166/score_e166.py) as registered (`f830b9e2`), run on pass 16620.

**The session figure** (the four replicate readings, all complete; `scored.json` › `rules.session_figure`), the plateau error rms:

| from the bits, M8 (the primary) | M7 | M6 | E153's measured switching watts for these tiles | given this session's watts (arm A) |
|---|---|---|---|---|
| **0.452 °C** | 0.289 °C | 0.217 °C | 0.176 °C | 0.281 °C |

**The registered verdicts** (E166.md § What is scored, and Q140(e)'s R4 and R6, unchanged; `scored.json` › `verdicts`):

| rule | reading | verdict |
|---|---|---|
| **RK3-a**: at least 3 of the 4 replicate readings with \|arm E's plateau error\| and its checkpoints' rms both within the hold's scale (K_S 0.278, K_Q 0.369, K_L 0.574, K_O 0.277 °C) | I = 2 (K_Q, K_O's window), F = 2 (K_S on its checkpoints' rms 0.343; K_L on both, 0.869 and 0.600), X = 0 | **FAIL** |
| **RK3-c** (aifoundry3): every reading with a measured rise of 10 °C or more has \|arm A's error\| / rise ≤ 0.015 | K_S 1.83%, K_O's window 2.15%, K_OL's long window 3.23%: all three outside | **FAIL** |
| **G_A** (R6): arm A's error over K_OL's long window minus over K_O's window; SLOW STAGE SEEN ≥ +0.15 °C | 0.400 − 0.242 = **+0.158 °C** | **SLOW STAGE SEEN** |
| **SL**: arm A's 300-600 s error slope in K_OL; SEEN ≥ 0.430, NOT SEEN ≤ 0.147 °C per 10 min (5.0% false positives on the registered pool, 8.1-10.3% on window-matched pools, dated note 2) | **−0.295 °C per 10 min** | **SLOPE NOT SEEN** |
| the frozen 95% bands (Q140(e)), per reading | every plateau inside | **PASS** on all five |
| G0 (the room at R0's end at or under 53.0 °C) | 51.924 °C | passed |
| X1 (the incomplete-window rule) | every window complete | no exclusion |

**Rank 3 is not answered on the replicates.** E166.md: "Rank 3 is answered on the replicates if RK3-a, RK3-c (this session and E167's) and
E167's RK3-b all hold". RK3-a and RK3-c fail here, so whatever E167 reads on aifoundry2, the aifoundry3 half does not hold.

**What the two misses are.**
- **RK3-a fails on the power path, mostly.** K_L, int8's whole-line kind (B lines flipping between all-zero and all-one bytes), rose 0.87 °C
  more than M8's watts predicted; given the measured watts its error is +0.40 °C. M6 reads it within 0.05 °C. This is int8's whole-line
  class, where M8 and M9 part by up to 0.85 W (E163.md's likeliest misses, class L). K_S's plateau is within its scale (−0.248 against
  0.278); its checkpoints' rms (0.343) is not, the early checkpoints running 0.37-0.46 °C low.
- **RK3-c fails on the heat path, and the deficit repeats smaller.** Given the watts, the chain reads all three large rises low by 1.8-3.2%
  (E154: 3.1-4.6%, on the same card a day earlier), and the two small int8 rises by 0.20 and 0.40 °C. So E154's gain deficit repeats in sign,
  about a third smaller.

**The slow stage: the two registered readings split.** G_A reads SLOW STAGE SEEN by 0.008 °C over its line. SL, the slope decision added beside
it with a stated false-positive rate, reads SLOPE NOT SEEN, and the long hold's arm-A error does not keep growing: +0.256 °C at 600 s, +0.451 at
750, +0.542 at 900, then +0.388, +0.418 and +0.320 at 1,050, 1,200 and 1,350 s, a slope of −0.01 °C per 10 min from 600 s to the end
(`scored.json` › `rules.K_OL_reported`, reported). The registered confound stands: a room that warms during K_OL reads as a slow stage, and there
is no inlet thermometer. Both readings are reported as registered; neither is a steady-state result.

**Peaks** (`scored.json` › `peaks`): K_S 65.78 °C (34-sensor mean) and 44.2 W; K_Q 63.11 °C and 36.54 W; K_L 59.94 °C and 32.65 W; K_OL 66.89 °C
and 40.72 W. Every one is under the 67.5 °C design line and far under the stops.

## What this does to predicting power and heat

- **The term tested:** the whole path from a tile's bits to its die over minutes (M8's watts, Q138(t)'s frozen chain, E97's idle law, Q140(e)'s
  duty convention), in a second session on the card; the chain's gain given the watts on large rises (RK3-c); and whether heat keeps growing
  past 10 minutes (G_A, SL).
- **Before** (E154, aifoundry3, Tue 3 Nov): from the bits, 0.370 °C rms over four 10-minute plateaus, 1 of 4 inside the critic's per-hold rule;
  given the watts, the three large rises read 3.1-4.6% low.
- **After** (E166, the same card, Wed 4 Nov, blind): from the bits, **0.452 °C rms** with M8 (0.289 with M7, 0.217 with M6) over four replicate
  plateaus, **2 of 4** inside the per-hold rule, every plateau inside its 95% band; given the watts, 0.281 °C rms and the large rises **1.8-3.2%
  low**. The heat model's gain deficit is real and repeatable on this card; the bits-to-watts error of M8 on int8's whole-line class is the
  largest single miss.
- **Nothing frozen changes.** No prediction, band or rule is refitted here.

## Registered before any data, and what the box ran

- **Frozen first:** Q140(e)'s heat-replicate predictions and rules: registration `11174d20` (02:23:53 PST), frozen `c9aaf179` (02:46:04),
  corrections `a4fe976d` (03:43:53) and `ac06c9be` (03:44:40), in
  [`../2026-11-04-q140e-heat-replicates/`](../2026-11-04-q140e-heat-replicates/). Nothing was fitted here.
- **Registered** (Q141(h)), every commit before any E166 data, claim or launch:
  [`E166.md`](../../../../tools/claims-v3/e166/E166.md) with `e166-registration.json` and SL's rule, `2b450e66` (09:16:36 PST); the scorer
  `score_e166.py` and its self-test, `f830b9e2` (09:31:08); the run kit and `frozen-e166.sha256` (30 files), `c75bc460` (09:41:09); dated note 2,
  E154's registered verdicts re-derived and `frozen-e166-fix.sha256`, `ae39563c` (11:24:33). Q141(f), the readiness critic, re-ran the parent
  self-test byte for byte before the go.
- **The tree on the box:** the Intel's lab clone at `5e1bb309` (= origin/main), the synced paths unchanged since `c31e7ae3`. One bounded rsync of
  E163's step-4 paths and `tools/claims-v3/e166/` to aifoundry3's `~/aifoundry` at 14:18:34 PST (Q141(k)'s `s07_a3_sync.sh`, the go checklist's
  step 7, which answers the Q141 critic's F4). On the box at 14:18:47-49: `sha256sum -c frozen-e166.sha256` **30 OK** (the three box binaries
  included) and `preflight_e166.sh` **GO, 38 send sites, 0 disallowed**. The session re-checked both at its start (14:20:51).
- **Card reads before the session** (14:18:55): `et-lab-manifest` kept on the box; `ettelem config` through E128's guard: TDP 0 W, threshold
  65 °C, max_power, 600 MHz, 523 mV; et-who: no process held an ET-SoC-1 device node or card lock.
- **The V3_DRY session on the box** (14:19:05-14:19:12, no `E166_DESK`, so every file was checked): every file as registered, the audit GO, the
  dry smoke's four stop tests passing and its in-launch board test failing on the toy card, so the dry gate read NO-GO and no measured pass ran,
  as E154's dry pass did on the box (expected; README box step 4). Its lines are the first 71 of `logs/session.log`; its files are in the box's
  `build/claims-v3-dry/`, not here.
- **Look first** at 14:18:26 and again at 14:20:50 (et-who, who, uptime): no holder of a device node or lock; other accounts' idle logins only,
  which do not block (the owner's ruling of 1 November 2026, as E60's D1). Booted 26 Oct 15:18:24 PST, the same boot as the claim's read.

## Registered against what happened

| registered | what happened |
|---|---|
| the full design if T0 + 76 min is at or before the end gate; no subset | T0 14:20:51 PST, end gate 19:00 PST: the full design; 74.2 card-minutes |
| G0: R0's room at or under 53.0 °C, else exit 7 and no hold | 51.924 °C: passed |
| E154's room rule sets K_S's period | 51.924 °C in (51.5, 53.0]: the warm-room period, 4.97 s; K_S ran 121 launches in 600 s, kernel duty 0.6962 |
| natural chain holds K_Q, K_L, K_OL | 81, 82 and 209 launches; kernel duty 0.9609-0.9621 |
| K_OL's room rule | its frozen peak 65.90 °C at 51.924 °C ≤ 67.5 °C: 25 minutes, run in full (1,499.4 s) |
| stops: gate 70 °C, hold 72 °C / 65 W, pass 74 °C, on live samples | none fired in the pass: highest board 44.2 W, highest `minshire[0]` 66 °C, highest 34-sensor mean 66.89 °C (K_OL) |
| the five stop tests in the smoke | all passed (`logs/smoke-gate.json`): no launch at a 1 °C gate; the hold's die and board lines ended a hold with no launch; a board line at 28.14 W ended the launch in flight; the session line (1 °C) ended the block with exit 6 on a live sample (die 52.0 °C, board 24.15 W) |
| the smoke gate | GO at 14:21:55: block ok, every stop test, every hold tile launched, 48 launch and 48 C records, a sound C log, the 34 raw codes in all 622 telemetry lines, 600 MHz, both config reads |
| the C check, a validity label | 6,692 of 6,692 dispatches PASS: every hold "C verified" |
| no hold dropped, no departure after the data | none |

## Device commands sent

As registered ([`tools/claims-v3/e166/dmcmd-audit.md`](../../../../tools/claims-v3/e166/dmcmd-audit.md)); the preflight read GO on the box at the
session's start (`logs/dmcmd-preflight.txt`: 38 send sites, 0 disallowed, the one reviewed exception lib.sh:154, never called). The harness is
E154's, so the table is E154's:

| command | sent by | class |
|---|---|---|
| `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25), `…_TEMPERATURE_THRESHOLDS` (21), `…_POWER_STATE` (23) | `ettelem config` through E128's guard: the session's start and end, each block's start and end | READ (RAM copies) |
| `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`, `pvt_sample.py` (10 Hz), lib.sh's `die_c` | READ (PLL register reads) |
| `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`, `pvt_sample.py`, `die_c` | READ (PMIC voltage-register reads; allowed by the owner's rule of 2 November 2026) |
| `DM_CMD_GET_MODULE_POWER` (33), `DM_CMD_GET_SP_STATS` (60), `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `pvt_sample.py`, `die_c` | READ |
| `DM_CMD_GET_MODULE_VOLTAGE` (31) | lib.sh's `die_c` at each block's start and end | READ (PMIC voltage-register reads; allowed) |
| `DM_CMD_GET_ASIC_PVT_SAMPLES` (74), group 0 only | `pvt_sample.py` at 10 Hz | READ, from the held patch source (E144's classification) |
| the C-logging host (`sparsity_ccheck.sh` → `build/ccheck/b/host/sparsity_host`, E78's kernel) | every launch | no device-management command (ops node: code load, DMA, launches) |
| **not sent** | — | the statistics reset (`--reset-ms`), command 74's group 6, the firmware-revisions query, any residency read, any set, any reset |

Every class is read from et-platform `836a4ab`'s public handlers; aifoundry3 runs a non-public BL2 0.22.0 thermal build (since 7 Oct 2026), so
E154's caveat (its C8) binds all ten commands here too.

## The day's post

Wed 4 Nov's one `#community-lab` post, message `1567662592850399304`, posted at 14:11:27 PST by the card half's claim with three clauses, the
first `using aifoundry3 for 3 h, until ~17:11 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, which covers E166 and
E163 in one reservation (E163's README dated note). E166 needed no edit of it: it ended inside the clause's estimate. The release, after E163,
is recorded in E163's data README.

## What this cannot say

- **One session per card, four replicate readings.** An rms from n = 4 has a wide interval (0.452 °C gives about 0.27-1.30 °C at 95%, χ² with
  4 degrees of freedom). The plateau moved 0.3-0.8 °C within E97's one session on this card with nothing changed; the room's only proxy is the
  rest die, and there is no inlet thermometer.
- **The 10-minute holds are not a steady state**, and G_A's SLOW STAGE SEEN is 0.008 °C over a line that a warming room also crosses; SL, with
  its 5-10% false-positive rate, reads the other way.
- **The bands do not separate the models** (Q139(e)'s D4): all five plateaus are inside on M8's bands while M8 has the largest rms of the four.

## How to reproduce

```bash
# the C check (Q139(k)) on the two C logs, then the registered scorer (Python 3.9, numpy 1.26.4)
D=docs/reports/data/2026-11-04-e166-heat-replicate-aifoundry3
gunzip -k $D/ccheck/c-log-p16601.jsonl.gz $D/ccheck/c-log-p16620.jsonl.gz
python3 tools/claims-v3/ccheck/ccheck.py check $D/ccheck/c-log-p16601.jsonl $D/ccheck/c-log-p16620.jsonl --out ccheck-all.json --jobs 2
python3 tools/claims-v3/e166/score_e166.py $D/aifoundry3/e166/p16620 --json scored.json
python3 tools/claims-v3/e166/score_e166.py --self-test
```

## Files

| file | what |
|---|---|
| `scored.json` | the registered scorer's output: every arm per reading, the rules, the verdicts, the session figure, the peaks |
| `aifoundry3/e166/p16620/` | the measured pass: `telemetry.jsonl.gz` (the 10 Hz sampler with the 34 raw codes), `marks.jsonl` (rests, holds, 493 launches, `rest_die`, `room`, `start_gate`), `runs.jsonl` (one record per dispatch, 6,644), `run.log`, `configs.json`, the config reads, `block.json`, `gen.sha256`, `binaries.sha256`, `code.sha256`, `manifest.txt` |
| `aifoundry3/e166-smoke/p16601/` | the smoke and the five stop tests, in the same layout (with the stop tests' `STOP` and `HOLDSTOP` files) |
| `ccheck/` | the two C logs (`c-log-p16601.jsonl.gz`, `c-log-p16620.jsonl.gz`; moved here from the pass directories, byte-identical) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `logs/` | the box's `build/e166/`: the session log (the V3_DRY session's lines first, then the session's), `session.out`, the session's config reads with their times, the device-command preflight, the smoke gate. Its et-who readings name no other account (E164's scrub in `--check` mode: 0 left) |

SPDX-License-Identifier: Apache-2.0
