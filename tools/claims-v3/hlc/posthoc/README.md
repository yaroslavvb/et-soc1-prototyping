# E63 post hoc: a second transfer point, and the card's own rails

*Written Mon 26 Oct 2026 (week 44) under request Q126, three days after E63 ran. **Nothing here is
pre-registered and nothing here carries a verdict.** E63's five decision rules were frozen on Fri 23 Oct
2026 before the first launch ([`../README.md`](../README.md)) and are untouched: no number in
`s*/analysis/lockin.json` changes, and no rule is re-scored. This directory reads out two quantities the
registered fit already computed and threw away, and one it never looked at.*

## What it answers

**1. The camera, card-free: a second point on the board's transfer function.** The registered lock-in carries
`sin 3phi` and `-cos 3phi` as shared nuisance columns, so the square drive's third harmonic cannot leak into
the fundamental, and then discards their coefficients (`lockin_hlc.analyse_block` keeps `z`, not `coef`).
The drive switches on a fixed 20 s grid, so that harmonic sits at **0.15 Hz**. Reading the camera's and the
board's third harmonics out of the same fit gives a second transfer point, H(3f) = Z3(camera) / Z3(board),
on exactly the data the 0.05 Hz point comes from, with the drive's own shape dividing out (a square wave's
third harmonic is a third of its fundamental, in phase with it). No card is opened and no new frame is taken:
this is why it is "card-free".

**2. The rails.** The 10 Hz sampler logs the card's own minion, SRAM and NoC rail watts (`sp.minion_w`,
`sp.sram_w`, `sp.noc_w`, each `[avg, min, max]`) in every run, beside the board-input watts the experiment
used. Each rail goes through the power's own lap model and through the same steady-window median the board
step is measured with, so each rail's share of the board step is measurable.

## The scripts

| File | What it does |
|---|---|
| `h3_rails_hlc.py` | one session: the camera's and every electrical series' third harmonic, the two transfer points, and the rails' steps and shares. Needs the session's RED (its frames), so it runs on aifoundry2. numpy only |
| `pool_h3.py` | both sessions' JSON: pools the four top-rung blocks by inverse variance — the ratio H(3f)/H(f) first, in which the camera's drifting gain divides out — and reports the single pole that would give that ratio. Standard library only |

Both scripts were run twice. The **second pass, the same day and after review**, changed how the pooling is
done and nothing about the data: `h3_rails_hlc.py` now writes H(3f) as a complex number and its jackknife
cloud, and gives the ratio |H(3f)|/|H(f)| **one** leave-one-lap-out jackknife with each lap dropped from both
harmonics; `pool_h3.py` pools the **complex** transfer, not the magnitude. Every per-block number below is
unchanged by it; the pooled ones moved by a few percent, and are marked. Why both changes were needed is
under [What came out](#what-came-out-both-sessions-fri-23-oct-2026s-data).

```bash
# on aifoundry2, from build/e63/code (the frozen copy), with this directory as posthoc/
python3 posthoc/h3_rails_hlc.py <RED>  --protocol protocol.json    \
    --template prereg/e62_bloom_dt.npy --scene-ref prereg/e62_scene.npy --out s1/posthoc/h3-rails.json
python3 posthoc/h3_rails_hlc.py <RED2> --protocol protocol-A1.json \
    --template prereg/e62_bloom_dt.npy --scene-ref prereg/e62_scene.npy --out s2/posthoc/h3-rails.json
# anywhere
python3 posthoc/pool_h3.py s1/posthoc/h3-rails.json s2/posthoc/h3-rails.json --out posthoc/h3-rails-pooled.json
```

Errors are jackknifed over laps (leave one lap out, refit the whole design), as the registered fundamental's
are, not taken from the design matrix: the camera's noise is not white, and a design SE would be optimistic.

## What came out (both sessions, Fri 23 Oct 2026's data)

**The third harmonic is at the noise floor in every single block**, and only the pooled number says anything.
Per top-rung block the camera reads 8.3 ± 10.2 to 19.5 ± 13.0 mK at 0.15 Hz — 0.8, 1.0, 1.2 and 1.5 SE, none
of them 2 SE from zero — on a board third harmonic of 0.53–0.89 W, which is itself 6.1–14.3 SE. (The *middle*
rungs are not all under 2 SE: session 1's reads 21.3 ± 9.8 mK, 2.2 SE. They are left out of the pool because
their board third harmonic is a quarter of a top rung's on the same camera floor, not because they are
quieter.) Pooled over the four top-rung blocks:

| | 0.05 Hz | 0.15 Hz |
|---|---|---|
| transfer, mK per W (vector mean) | **52.7 ± 2.0** at 95° | **18.4 ± 5.4** at 151° |
| — the same as a mean of magnitudes | 54.1 ± 1.8 | 19.0 ± 5.2 |
| the ratio H(3f)/H(f) | — | **0.343 ± 0.104** |
| — the first pass's quadrature SE | — | 0.352 ± 0.100 |
| lag | 87–109° (4.8–6.0 s) | 113–179° (2.1–3.3 s) |

**Pool the complex transfer, not the magnitude.** Each block's H(3f) is a complex number whose jackknife cloud
is most of its own length, and the magnitude of such a quantity averages above the magnitude of its mean
(E|Z| > |E Z|), so an inverse-variance mean of four magnitudes sits above the coherent transfer they share.
The first pass published that mean, 19.0 ± 5.2; the vector mean is 18.4 ± 5.4, 3.2% lower. At 0.05 Hz, where the
four blocks' camera fundamentals have SNR 21.4, 19.6, 9.1 and 4.8 and the transfer is 4–20 SE from zero, the two
routes agree to 2.6% — the bias is there too but small, which is the check that the machinery is not inventing
the gap at 3f. The SE quoted is along the pooled vector's own direction, taken from each block's cloud
projected onto it, so it is comparable with a magnitude's.

**And give the ratio one jackknife, not two SEs in quadrature.** H(3f) and H(f) are two coefficients of the
same fit on the same frames and share the camera's gain, which is the ratio's whole reason for existing, so
the first pass's quadrature treated as independent two errors that are not. Dropping each lap from both
harmonics at once gives 0.343 ± 0.104, against the quadrature's 0.352 ± 0.100 — the correction is smaller than
the error it corrects, which is worth knowing but does not change the reading.

So the board's answer at 0.15 Hz is about a third of its answer at 0.05 Hz: it is rolling off between the two,
**6.3 SE from flat** (a ratio of 1; the first pass said "3.3 SE from flat", which was the ratio's distance
from *zero*, 3.3 SE — a different and much weaker statement). A single pole with **tau ≈ 12 s** reproduces the
ratio, and that is the first measured number for the time constant E63's result was read against (E62's bloom
suggested 15–20 s, and the registered write-up already noted that 59 mK/W at 0.05 Hz was too fast for that).
Two things keep it from being a fitted time constant. A one-pole ratio falls from 1 only to **1/3** as the
pole grows, and 0.343 ± 0.104 sits on that floor: the 1 σ band runs from 3.2 s **upward with no end**, since
every longer pole fits as well. And a single pole cannot lag more than 90°, while the measured lag at f is
87–109° (99° on average). One pole is a scale, not a model: the extra phase is what a spreading, diffusive
board gives.

**The flips' watts land on the minion rail, and almost nowhere else.** In all four rung blocks of both sessions,
of the board's step between the two arms:

| | minion rail | SRAM rail | NoC rail | the three summed |
|---|---|---|---|---|
| top rung (4 blocks) | 84.3, 84.4, 86.1, 86.1% | 0.39–0.46% | 0.45–0.62% | 85.3–87.1% |
| middle rung (2) | 85.2, 86.0% | 0.61, 0.92% | 0.32, 1.39% | 86.2, 88.3% |

The missing 12–15% is the board's conversion loss and the rails the sampler does not break out; it is not a
third compute rail. The null's shares are meaningless and are reported only for completeness: its board step
is −0.03 to −0.04 W, so every ratio is a ratio of noise. The same rails' *fundamentals* at 0.05 Hz read
68–86% of the board's for the rungs, noisier than the steps (the rails are sampled at 10 Hz and have no
median to steady them), so the steps are the number to quote.

## The one thing that is not reproducible byte for byte

Session 1's reduced cube was never on aifoundry2: it was made on the Intel from a byte-identical copy of the
capture while session 2 was still running (03-experiments.md, E63), and was not kept. It was rebuilt on
aifoundry2 on 26 October with the same `reduce_hm.py` on the same raw capture. The rebuild reads the same
48,005 packets, 25.001 fps and 3,841 bins, but finds **244 shutter events against the committed
`s1/red/ffc.json`'s 243** — one borderline step landing on the other side of the 40 mK detection threshold on
a different machine's numpy, which is the only difference the two runs can have. One extra cut
changes nothing a reader would notice — re-running `summary_hlc.py` on it reproduces session 1's top rung's
plain bridged lock-in as 192.507 mK against the published 192.507, and moves only the null's, 13.4 → 14.2 mK
against an SE of 47 — but session 1's numbers here come from a reduction that differs from the registered one
by that one event. Session 2's RED is the original and reproduces to the last digit.
