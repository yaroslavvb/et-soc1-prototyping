# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 18:30 PST: the S class's share as registered, when D1 was written, K7W's widths, and the day's post (E164's fix pass)

*This note sits beside [`README.md`](README.md), not inside it: the README stays as committed in `5eecc457` (17:28:54 PST). It records
what the verifier of the aifoundry1 scoring found in this README (Wed 4 Nov 2026, about 17:40–18:14 PST). Its verdict was "holds with
fixes". The data, the stops, the device commands, the order, the frozen lists, the window, the post and the privacy all hold, and every
collector output re-makes byte for byte from the committed passes (35 of 35, and the C check). Its items are wording only. This is desk
work: no verdict, number, band, prediction, rule or frozen file changes, no device command is involved, and nothing in this note was
registered. It answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, and the Q139 critic's ranks 1, 4, 7
and 9.*

## 1. The 27-point counts: R3 is the share of the squared error, not of the rms

The README's § Results, "Q141(t)'s 27-point arm across both cards", ends: *"So the 27-point counts remove 53-66% of the S class's power rms
(the scorer's counting share, 1 − r27 / r3), and R5 still reads a base-word price."*

**What is registered.** R3, the counting share, is "1 − Σ r27² / Σ r3² over S7: the share of the primary's squared S-class error the
27-point counts remove" ([`REGISTRATION.md`](../2026-11-04-q141t-s7-recount/REGISTRATION.md) § 3, the R3 row). `score_s7arm.py` computes it
as 1 − s27 / s3, where each s is a sum of squares (lines 207–210). On the same tiles that is 1 − (rms27 / rms3)². The rms itself falls by
1 − rms27 / rms3:

| set (the 7 priority-1 S tiles) | rms r3 → r27, W | the rms falls by | R3, the share of the squared error |
|---|---|---|---|
| card 1 (E164) | 0.543 → 0.318 | **41%** | 0.66 |
| aifoundry3 (E163) | 0.577 → 0.396 | **31%** | 0.53 |
| pooled (both cards) | 0.560 → 0.359 | **36%** | 0.59 |

Source: [`score-s7arm-a1.json`](score-s7arm-a1.json) › `cards.aifoundry1c1.R2_R4`, `cards.aifoundry3.R2_R4` and `pooled` (`rms3_w`,
`rms27_w`, `R3_counting_share`).

**The sentence, as it should read:** *"So the 27-point counts cut the S class's power rms by 41% on card 1, 31% on aifoundry3 and 36%
pooled. R3, the share of its squared error they remove, is 0.66 / 0.53 / 0.59 (reported, no verdict on M9). R5 still reads a base-word
price."* The rest of that paragraph stands as written. So does § What it says to change, item (3): "27 points take the S class from 0.54 to
0.32 W rms here".

## 2. D1 was written after the collection

The README's § Registered against what happened, row "departures", says: *"**D1, the collection route** (dated here, Wed 4 Nov 2026,
before the registered reduction ran)"*.

**What happened.**
- **The route was set before the run.** The scoring lane's own driver script (not in the repo) was last written at 17:04:23 PST. It ran the
  registered collector `collect_e164_a1.sh` over the card lane's digest-checked copy `build/e164-raw` (every per-directory digest equal
  to the box's, read 15:18 PST). It set `E164_S_RECOUNT` and passed E163's committed `e163.json` and `scored.json`.
- **The collection** ran 17:04:25–17:14:34 PST. The registered primary reduction wrote `e164.json` at 17:04:28, and `scored.json` and
  `results.md` were written at 17:14:33.
- **D1's text came later.** The lane's README draft of 17:09:55 holds no D1. The README was last written at 17:26:49 and committed at
  17:28:54.

So D1 is a departure recorded after the reduction ran, not one dated before it.

**As it should read:** *"**D1, the collection route** (written after the collection, Wed 4 Nov 2026, about 17:10–17:27 PST; the route, the
registered collector over the card lane's byte-equal copy, was set in the scoring lane's script before the run began at 17:04:25)"*. The
rest of D1 stands. D1 changes no data choice: the registered collector ran unchanged over a copy byte-equal to what the box wrote. The
verifier checked this again. The four passes, the smoke, the stop-path test and the logs each equal the pull byte for byte.

## 3. K7W's measured widths: wider than planned on the floats only

The README's § Results, "Rank 7's repeat", says: *"**K7W PASS: every tile inside its Welch half-width, 0.19-0.31 W on the floats and
0.22-0.33 W on int8**, wider than A1-1's planned ±0.09-0.16 / ±0.25-0.29 W, so this session bounds card 1's day-to-day change only to those
widths."*

Tile by tile, from [`results.md`](results.md) § K7 and the table in amendment A1-1
([`E164.md.dated-note.md`](../../../../tools/claims-v3/e164/E164.md.dated-note.md) § A1-1):

| K7 tile | A1-1's planned half-width (at E157's spreads), W | measured Welch half-width, W |
|---|---|---|
| `fp32.real_qwen_softmax_v` | 0.088–0.152 | 0.311 |
| `fp32.real_smol_softmax_v_causal` | 0.148–0.162 | 0.186 |
| `fp16.real_qwen_qk` | 0.089–0.132 | 0.274 |
| `fp16.e5m2grid_wide` | 0.100–0.135 | 0.231 |
| `int8.powerlaw_df4_pc` | 0.288 | 0.264 |
| `int8.bheld_bit1` | 0.253 | 0.233 |
| `int8.bheld_bit4` | 0.245 | 0.221 |
| `int8.real_qwen_w8a8_gate` | 0.271 | 0.330 |

All four float tiles came out wider than planned: 0.19–0.31 W against 0.09–0.16 W. The int8 widths bracket the plan: 0.22–0.33 W against
0.25–0.29 W, with three tiles narrower and one wider.

**As it should read:** *"... 0.19-0.31 W on the floats and 0.22-0.33 W on int8: wider than A1-1's planned ±0.09-0.16 W on the floats,
while int8's bracket the planned ±0.25-0.29 W. So this session bounds card 1's day-to-day change only to those widths."* In A1-1's
registered form, with the measured widths: "on card 1, the four float tiles repeated E157 within 0.19–0.31 W and the four int8 tiles within
0.22–0.33 W (K7W PASS, 95%), after the per-session anchor scale; K7D FAIL, 2 of 8 within 0.05 W". The README's next sentences stand:
K7D's reading, rank 7's second new card-1 session, and the 0.1–0.2 W int8 floor this session cannot resolve.

## 4. The day's post, after this README's account

The README's § Card and post ends with aifoundry2's clause still held. At 17:18:22 PST, before this README was committed, aifoundry2's lane
appended " — released" to message `1567662592850399304`. Its clause was the last one held, and every word was kept. It worked under the
Discord lock with `EXPECT_TEXT` and read the post back. The post's day, in full:
- 14:11:27: claimed with three clauses.
- 16:38:11: aifoundry3's clause dropped.
- 16:50:09–15: aifoundry1's clause dropped, by E170's lane.
- 17:18:22: " — released" appended, by aifoundry2's lane.

E164's lane made no edit, because aifoundry1's clause covered E170 as well.

## 5. How this note was checked

- R3's definition: `REGISTRATION.md` § 3 and `score_s7arm.py` lines 207–210. The figures come from `score-s7arm-a1.json`. Exactly, the
  rms falls by 1 − 0.3178 / 0.5430 = 41.5% on card 1, 1 − 0.3960 / 0.5766 = 31.3% on aifoundry3 and 1 − 0.3590 / 0.5600 = 35.9% pooled.
  R3 is 0.658, 0.528 and 0.589.
- D1's times: the collector's output files in `build/e164-out` (`e164.json` 17:04:28; `scored.json` and `results.md` 17:14:33), the
  lane's collection log (17:04:25–17:14:34), its README draft (17:09:55, no D1), the README file (17:26:49) and the commit (17:28:54).
- K7W: `results.md` § K7 against A1-1's table.
- No file in this directory was edited or re-made. The scrub's `--check` reads 0 left on `logs/` and on the whole directory.

SPDX-License-Identifier: Apache-2.0
