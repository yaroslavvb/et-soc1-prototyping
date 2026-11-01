# E99 — which mechanism carries the DRAM pattern effect (Q132)

*Status Sun 1 Nov 2026, about 01:05 PDT: the desk result below is committed with the registration
(`tools/claims-v3/dm/README.md`). No E99 card session has run yet. The card's results will go above this section.*

## Step 1, at the desk: POST HOC, labelled

*`tools/claims-v3/dm/posthoc_desk.py`, output `posthoc-desk.txt`, `posthoc-desk.json`. This is not registered and not scored. It was
written after E75's and E81's data were seen, and it fits those data. Its only role is to freeze predictions for images it was not
fitted on.*

**What was computed.** A line-level encoder (`tools/claims-v3/dm/dm_enc.py`: two byte lanes, 32 beats, the read DBI rule, the 16-way channel
interleave) applied to every committed E75 and E81 DRAM image: pins driven high after inversion, pin toggles between beats after and
before inversion, bits changed between lines, and bits changed between two reads of one channel. Then least-squares fits of 18 measured
points, watts over each experiment's own zeros anchor: E81's ten data items and E75's seven rungs and its random anchor.

**What came out.**

| model | rms over the 18 points | of E81's 1.636 W (`dp_bern − dp_c2`) | of the arrangement, 0.996 W | of the period, 0.640 W | floor over zeros |
|---|---:|---:|---:|---:|---:|
| counting bits: ones + changed bits + floor | 0.516 W | **0** (the same counts by design) | 0 | 0 | +1.07 W |
| **the simplest DBI model**: high pins + encoded pin toggles + floor | 0.266 W | **0.972 W, 59 %** | 1.048 W | −0.076 W | +1.72 W |
| no DBI: ones + raw pin toggles + floor | 0.231 W | 0.920 W, 56 % | 0.904 W | 0.015 W | +0.90 W |
| ones + high pins + floor | 0.198 W\* | 1.013 W, 62 %\* | 0.823 W\* | 0.190 W\* | +1.00 W\* |
| ones + high pins + a channel's line changes + floor | 0.140 W | 1.394 W, 85 % | 0.755 W | 0.639 W | +1.09 W |
| ones + raw toggles + a channel's line changes + floor | 0.164 W | 1.332 W, 81 % | 0.695 W | 0.636 W | +0.99 W |

*\* That row also carries encoded toggles, `bits+dbi` in `posthoc-desk.txt`, with a price of −15 pJ per high pin and +14 pJ per encoded toggle: collinear
counts, not prices.*

Four readings, each from `posthoc-desk.txt`:

1. **The high-pin count alone gets the arrangement and none of the period.** The simplest DBI model gives 59 % of the 1.636 W: the whole 0.996 W arrangement
   and −0.076 W of the 0.640 W period.
2. **Adding a channel's line changes gets the period** (0.639 of 0.640 W at 2.2 pJ per bit changed between two reads of one channel), so 85 % of the 1.636 W.
   The count was built on the reading that each channel carries every 16th line, and E81's own finding is in the fit, so this agreement is no test.
3. **These data cannot tell high pins from toggles.** Across the 18 points the high-pin count, the encoded toggles and the raw toggles correlate at 0.99–1.00, and a model with
   no DBI at all fits about as well. The simplest DBI model's own toggle price is negative (−2.37 pJ) for that reason.
4. **Of the 63 % that counting bits missed** (E75's two prices give 36.6 % of the 3.25 W chord), the largest part is a floor. In the ones + high pins + channel model, random floats'
   3.31 W over zeros divide as floor 1.09 W (33 %), ones 0.88 W (27 %), high pins 0.84 W (25 %) and channel changes 0.50 W (15 %). So the floor, the high pins and the channel changes are
   what counting bits missed. Nothing yet says what the floor is, or that it is more than the shape of the response near zero: E75's w128 image already costs 1.405 W over zeros for
   128 ones and 16 high pins. `dm_w1`, one bit in every line, tests it.

**Why a registered test.** Images built to hold these counts apart, the same ones with different high pins, the same high pins with different ones, and the same high pins and toggles with different periods, make
the candidates disagree by up to 1.7 W (`tools/claims-v3/dm/README.md` §3).
